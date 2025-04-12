import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from logger import logger
from constants import (
    DEFAULT_RETRIEVER_TOP_K, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP,
    ERROR_UNSUPPORTED_FILE_FORMAT, ERROR_FILE_NOT_FOUND,
    ERROR_MISSING_TEXT_FIELD, ERROR_MISSING_ID_FIELD,
    ERROR_INVALID_JSON, ERROR_PROCESSING_LINE,
    MSG_LOADING_DOCUMENTS, MSG_LOADED_DOCUMENTS,
    DEFAULT_LM_STUDIO_URL, DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE
)


def get_llm():
    """
    Initialise et configure le modèle de langage via LM Studio.

    Returns:
        ChatOpenAI: Instance du modèle de langage configurée
    """
    # Utilisation d'une clé API factice si LM Studio n'en a pas besoin
    api_key = os.getenv("LM_STUDIO_API_KEY", "NotNeeded")
    base_url = os.getenv("LM_STUDIO_URL", DEFAULT_LM_STUDIO_URL)
    model_name = os.getenv("LM_STUDIO_MODEL", DEFAULT_MODEL_NAME)
    temperature = float(os.getenv("LM_TEMPERATURE", str(DEFAULT_TEMPERATURE)))

    logger.info(
        f"Connecting to LLM at: {base_url} (model: {model_name}, temperature: {temperature})")

    return ChatOpenAI(
        openai_api_key=api_key,
        base_url=base_url,  # Point vers le serveur LM Studio local
        model=model_name,
        temperature=temperature
    )


def setup_rag_pipeline(vector_store, k=DEFAULT_RETRIEVER_TOP_K):
    """
    Configure le pipeline RAG avec le vector store fourni.

    Args:
        vector_store: La base de données vectorielle pour la récupération de contexte
        k: Nombre de documents à récupérer par requête (par défaut: 3)

    Returns:
        RetrievalQA: La chaîne RAG configurée
    """
    llm = get_llm()

    # Création d'un template de prompt efficace pour utiliser le contexte récupéré
    template = """
    You are a helpful AI assistant that provides accurate information based on the given context.
    If you don't know the answer, just say you don't know. Don't make up answers.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    # Création de la chaîne RAG
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(
            search_type="similarity",
            # Récupérer les k chunks les plus pertinents
            search_kwargs={"k": k}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain
