import os
import argparse
from dotenv import load_dotenv
from utils import load_documents
from chatbot import ChatbotCLI
from rag import setup_rag_pipeline
from embedding import setup_vector_store
from logger import logger
from constants import (
    DEFAULT_DATA_PATH, DEFAULT_DB_PATH,
    MSG_LOADING_DOCUMENTS, MSG_LOADED_DOCUMENTS,
    MSG_SETUP_VECTOR_STORE, MSG_INIT_RAG, MSG_RAG_INITIALIZED,
    MSG_USING_DATA, MSG_VECTOR_STORE_LOCATION,
    ENV_TOKENIZERS_PARALLELISM, ENV_TOKENIZERS_PARALLELISM_VALUE
)

# Éviter des problèmes avec les tokenizers HuggingFace
os.environ[ENV_TOKENIZERS_PARALLELISM] = ENV_TOKENIZERS_PARALLELISM_VALUE


def main():
    """
    Point d'entrée principal de l'application chatbot RAG.
    Configure l'environnement, traite les arguments, initialise le système RAG et démarre l'interface CLI.
    """
    load_dotenv()  # Chargement des variables d'environnement

    # Analyse des arguments de ligne de commande
    parser = argparse.ArgumentParser(description='RAG Chatbot with LM Studio')
    parser.add_argument('--data_path', type=str, default=DEFAULT_DATA_PATH,
                        help='Path to the training data')
    parser.add_argument('--db_path', type=str, default=DEFAULT_DB_PATH,
                        help='Path to store the vector database')
    parser.add_argument('--rebuild_db', action='store_true',
                        help='Force rebuilding the vector database')
    args = parser.parse_args()

    # Vérification de l'existence du fichier de données
    if not os.path.exists(args.data_path):
        logger.error(f"Data file not found at {args.data_path}")
        raise FileNotFoundError(f"Data file not found at {args.data_path}")

    # Chargement et traitement des documents
    logger.info(MSG_LOADING_DOCUMENTS)
    documents = load_documents(args.data_path)
    logger.info(MSG_LOADED_DOCUMENTS.format(len(documents)))

    # Création ou chargement du vector store
    logger.info(MSG_SETUP_VECTOR_STORE)
    vector_store = setup_vector_store(
        documents, args.db_path, force_rebuild=args.rebuild_db)

    # Configuration du pipeline RAG
    logger.info(MSG_INIT_RAG)
    rag_chain = setup_rag_pipeline(vector_store)

    # Démarrage de l'interface CLI
    logger.info(MSG_RAG_INITIALIZED)
    logger.info(MSG_USING_DATA.format(args.data_path))
    logger.info(MSG_VECTOR_STORE_LOCATION.format(args.db_path))
    chatbot = ChatbotCLI(rag_chain)
    chatbot.start()


if __name__ == "__main__":
    main()
