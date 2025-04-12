from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import setup_rag_pipeline
from embedding import setup_vector_store
from utils import load_documents
import os
import requests
import time
from requests.exceptions import ConnectionError, Timeout, RequestException
from logger import logger
from constants import (
    DEFAULT_DATA_PATH, DEFAULT_DB_PATH, ENV_TOKENIZERS_PARALLELISM,
    ENV_TOKENIZERS_PARALLELISM_VALUE, MSG_LOADING_DOCUMENTS,
    MSG_LOADED_DOCUMENTS, MSG_SETUP_VECTOR_STORE, MSG_INIT_RAG,
    ERROR_FILE_NOT_FOUND, DEFAULT_LM_STUDIO_URL
)

# Initialize Flask app
app = Flask(__name__)
# Enable CORS with more specific configuration
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# Load environment variables
os.environ[ENV_TOKENIZERS_PARALLELISM] = ENV_TOKENIZERS_PARALLELISM_VALUE

data_path = os.getenv("DATA_PATH", DEFAULT_DATA_PATH)
db_path = os.getenv("DB_PATH", DEFAULT_DB_PATH)

# Ensure data file exists
if not os.path.exists(data_path):
    logger.error(ERROR_FILE_NOT_FOUND.format(data_path))
    raise FileNotFoundError(ERROR_FILE_NOT_FOUND.format(data_path))

# Load documents and set up vector store
logger.info(MSG_LOADING_DOCUMENTS)
documents = load_documents(data_path)
logger.info(MSG_LOADED_DOCUMENTS.format(len(documents)))

logger.info(MSG_SETUP_VECTOR_STORE)
vector_store = setup_vector_store(documents, db_path, force_rebuild=False)

# Set up RAG pipeline
logger.info(MSG_INIT_RAG)
rag_chain = setup_rag_pipeline(vector_store)


@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to handle chatbot queries."""
    data = request.get_json()
    user_query = data.get("query", "")

    if not user_query:
        logger.warning("Received empty query")
        return jsonify({"error": "Query is required"}), 400

    # Check if LLM service is available
    llm_url = os.getenv("LM_STUDIO_URL", DEFAULT_LM_STUDIO_URL)
    # Add debug logs for Docker detection and URL configuration
    logger.info(f"IS_DOCKER env: {os.getenv('IS_DOCKER', 'not set')}")
    logger.info(
        f"Using LLM URL: {llm_url} (DEFAULT is {DEFAULT_LM_STUDIO_URL})")

    llm_available = check_llm_availability(llm_url)

    if not llm_available:
        error_msg = f"LLM service is not available at {llm_url}. Please make sure LM Studio is running."
        logger.error(error_msg)
        return jsonify({
            "error": "LLM service unavailable",
            "message": error_msg
        }), 503  # Service Unavailable

    # Process query with retry
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(
                f"Processing query: {user_query} (attempt {attempt+1}/{max_retries})")
            result = rag_chain.invoke({"query": user_query})
            response = {
                "answer": result.get("result", "No answer generated"),
                "sources": [doc.metadata for doc in result.get("source_documents", [])]
            }
            return jsonify(response)

        except ConnectionError as e:
            logger.error(
                f"Connection error (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                return jsonify({
                    "error": "Failed to connect to LLM service after multiple attempts",
                    "message": f"The server could not connect to the LLM service at {llm_url}. Please ensure LM Studio is running and accessible."
                }), 503

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing query: {error_msg}")
            return jsonify({
                "error": f"Error processing your query: {error_msg}",
                "message": "The server encountered an error while processing your request. This might be due to the complexity of your query or the size of the document corpus."
            }), 500


def check_llm_availability(url):
    """Check if the LLM service is available by making a simple request."""
    try:
        # Try a simple request to the models endpoint (standard for OpenAI-compatible APIs)
        response = requests.get(f"{url}/models", timeout=3)
        if response.status_code == 200:
            logger.info(f"LLM service available at {url}")
            return True

        # If models endpoint doesn't work, try a direct test with a simple completion
        headers = {
            "Content-Type": "application/json",
        }
        test_data = {
            # This should be ignored by most OpenAI compatible APIs if model doesn't match
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        }

        response = requests.post(
            f"{url}/chat/completions", headers=headers, json=test_data, timeout=5)
        # Accept any non-server error (even 401 or 404 means the server is responding)
        if response.status_code < 500:
            logger.info(f"LLM service responding at {url}")
            return True

        logger.warning(
            f"LLM service returned status code {response.status_code} at {url}")
        return False

    except (ConnectionError, Timeout) as e:
        logger.warning(f"Connection error when checking LLM service: {str(e)}")
        return False
    except RequestException as e:
        logger.warning(f"Request error when checking LLM service: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"Unexpected error when checking LLM service: {str(e)}")
        return False


@app.route('/sources', methods=['GET'])
def sources():
    """Endpoint to retrieve sources for the last chatbot response."""
    logger.info("Sources endpoint called (not yet implemented)")
    return jsonify({"message": "This endpoint is not yet implemented."})


@app.route('/load_documents', methods=['POST'])
def load_new_documents():
    """Endpoint to load a new .jsonl file from an uploaded file."""
    try:
        if 'file' not in request.files:
            logger.warning("No file part in the request")
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.endswith('.jsonl'):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({"error": "Only .jsonl files are supported"}), 400

        # Save the uploaded file temporarily for processing
        temp_file_path = os.path.join('/tmp', file.filename)
        file.save(temp_file_path)
        logger.info(f"File saved temporarily at {temp_file_path}")

        # Also save the file to the data folder
        data_folder = os.path.dirname(data_path)
        permanent_file_path = os.path.join(data_folder, file.filename)

        try:
            # Ensure the data folder exists
            os.makedirs(data_folder, exist_ok=True)
            # Copy the file from temp to data folder
            with open(temp_file_path, 'rb') as src_file:
                with open(permanent_file_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
            logger.info(f"File saved permanently at {permanent_file_path}")
        except Exception as e:
            logger.error(f"Failed to save file to data folder: {str(e)}")
            # Continue with processing even if permanent save fails

        # Load documents from the temporary file
        new_documents = load_documents(temp_file_path)
        logger.info(f"Loaded {len(new_documents)} new documents")

        # Set up new vector store
        logger.info("Setting up new vector store...")
        global vector_store
        vector_store = setup_vector_store(
            new_documents, db_path, force_rebuild=True)

        # Reinitialize RAG pipeline
        logger.info("Reinitializing RAG pipeline...")
        global rag_chain
        rag_chain = setup_rag_pipeline(vector_store)

        # Remove temporary file
        os.remove(temp_file_path)
        logger.info(f"Temporary file {temp_file_path} removed")

        return jsonify({
            "message": f"File '{file.filename}' successfully processed with {len(new_documents)} documents loaded.",
            "saved_path": permanent_file_path
        }), 200

    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info(f"Starting API server on port 5005")
    app.run(host='0.0.0.0', port=5005, debug=True)
