import sys
from typing import Dict, List, Any
from logger import logger
from constants import (
    DEFAULT_LM_STUDIO_URL, DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE,
    UI_WELCOME_MESSAGE, UI_GOODBYE_MESSAGE, UI_SOURCES_HEADER, UI_SOURCES_FOOTER
)


class ChatbotCLI:
    """
    Interface en ligne de commande pour interagir avec le chatbot RAG.
    Gère les entrées utilisateur, les réponses et l'affichage des sources.
    """

    def __init__(self, rag_chain):
        """
        Initialise le chatbot CLI.

        Args:
            rag_chain: La chaîne RAG utilisée pour traiter les requêtes
        """
        self.rag_chain = rag_chain
        self.history = []  # Historique des conversations
        logger.info("ChatbotCLI initialized")

    def start(self):
        """Démarre l'interface interactive du chatbot en ligne de commande"""
        print(UI_WELCOME_MESSAGE)  # Garder print pour l'interface utilisateur
        logger.info("Starting interactive CLI session")

        while True:
            # Récupération de l'entrée utilisateur
            user_input = input("\nYou: ").strip()

            # Vérification des commandes de sortie
            if user_input.lower() in ["exit", "quit"]:
                # Garder print pour l'interface utilisateur
                print(UI_GOODBYE_MESSAGE)
                logger.info("User requested to exit the session")
                sys.exit(0)

            if not user_input:
                # Garder print pour l'interface utilisateur
                print("Please enter a question.")
                logger.debug("User entered empty query")
                continue

            # Traitement de la requête via RAG
            try:
                logger.info(f"Processing user query: {user_input}")
                result = self.rag_chain.invoke({"query": user_input})

                # Stockage de la réponse dans l'historique
                self.history.append({"query": user_input, "response": result})

                # Extraction et affichage de la réponse
                answer = result.get("result", "No answer generated")
                # Garder print pour l'interface utilisateur
                print("\nChatbot:", answer)
                logger.debug(f"Generated answer: {answer[:100]}..." if len(
                    answer) > 100 else answer)

                # Obtention des sources
                source_docs = result.get("source_documents", [])
                logger.debug(f"Retrieved {len(source_docs)} source documents")
                self._display_sources(source_docs)

            except Exception as e:
                error_msg = f"Error processing your question: {str(e)}"
                # Garder print pour l'interface utilisateur
                print(f"\n{error_msg}")
                logger.error(error_msg)
                # Garder print pour l'interface utilisateur
                print("Please try again with a different question.")

    def _display_sources(self, sources: List[Any]):
        """
        Affiche les sources utilisées pour générer la réponse.

        Args:
            sources: Liste des documents sources
        """
        if not sources:
            return

        print(UI_SOURCES_HEADER)  # Garder print pour l'interface utilisateur
        for i, doc in enumerate(sources, 1):
            # Récupération de l'ID depuis les métadonnées, 'N/A' par défaut
            source_id = doc.metadata.get('id', 'N/A')
            # Garder print pour l'interface utilisateur
            print(f"\nSource {i} (ID: {source_id}):")

            # Affichage d'un extrait du contenu
            content_preview = doc.page_content[:200]
            if len(doc.page_content) > 200:
                content_preview += "..."
            # Garder print pour l'interface utilisateur
            print(f"Content: {content_preview}")
        print(UI_SOURCES_FOOTER)  # Garder print pour l'interface utilisateur
