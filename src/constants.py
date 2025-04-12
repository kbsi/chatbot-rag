"""
Constantes utilisées dans l'application chatbot RAG.
"""
import os

# Chemins par défaut
DEFAULT_DATA_PATH = 'data/train.jsonl'
DEFAULT_DB_PATH = 'chroma_db'

# Variables d'environnement
ENV_TOKENIZERS_PARALLELISM = "TOKENIZERS_PARALLELISM"
ENV_TOKENIZERS_PARALLELISM_VALUE = "false"

# Paramètres pour le découpage de texte
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 0.2

# Configuration LLM
DEFAULT_LM_STUDIO_URL = f"http://localhost:1234/v1"
DEFAULT_MODEL_NAME = "mistral-7b-instruct-v0.3"
DEFAULT_TEMPERATURE = 0.3

# Configuration RAG
DEFAULT_RETRIEVER_TOP_K = 3

# Paramètres pour les embeddings
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Messages utilisateur
MSG_LOADING_DOCUMENTS = "Loading documents..."
MSG_LOADED_DOCUMENTS = "Loaded {} documents"
MSG_SETUP_VECTOR_STORE = "Setting up vector store..."
MSG_INIT_RAG = "Initializing RAG pipeline..."
MSG_RAG_INITIALIZED = "\n=== RAG Chatbot initialized successfully ==="
MSG_USING_DATA = "Using data from: {}"
MSG_VECTOR_STORE_LOCATION = "Vector store location: {}"

# Messages d'erreur
ERROR_UNSUPPORTED_FILE_FORMAT = "Unsupported file format: {}. Please use .jsonl files."
ERROR_FILE_NOT_FOUND = "Data file not found at {}"
ERROR_MISSING_TEXT_FIELD = "Warning: Skipping line {} in {} due to missing 'text' field."
ERROR_MISSING_ID_FIELD = "Warning: Skipping line {} in {} due to missing 'id' field."
ERROR_INVALID_JSON = "Warning: Skipping invalid JSON line {} in {}"
ERROR_PROCESSING_LINE = "Warning: Error processing line {} in {}: {}"

# Messages pour l'interface utilisateur
UI_WELCOME_MESSAGE = "\n=== Chatbot RAG ===\nType 'exit' or 'quit' to end the session"
UI_GOODBYE_MESSAGE = "Goodbye!"
UI_SOURCES_HEADER = "\n--- Sources ---"
UI_SOURCES_FOOTER = "\n--------------"
