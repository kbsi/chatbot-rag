"""
Module de journalisation centralisé pour le projet Chatbot-RAG.
Configure un système de journalisation uniforme qui écrit à la fois dans un fichier et sur la console.
"""
import logging
import os
from datetime import datetime
import sys


def setup_logger(name="chatbot_rag", log_level=logging.INFO):
    """
    Configure et retourne un logger avec gestion de fichiers et formatage avancé.

    Args:
        name (str): Nom du logger
        log_level (int): Niveau de journalisation (ex: logging.INFO)

    Returns:
        logging.Logger: Instance de logger configurée
    """
    # Vérifier si le logger existe déjà avec des handlers configurés
    existing_logger = logging.getLogger(name)
    if existing_logger.handlers:
        existing_logger.debug(
            "Logger already configured, reusing existing instance")
        return existing_logger

    # Créer le répertoire de logs s'il n'existe pas
    logs_dir = os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Générer un nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(logs_dir, f"{name}_{timestamp}.log")

    # Configurer le logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Supprimer les gestionnaires existants s'il y en a
    if logger.handlers:
        logger.handlers.clear()

    # Formateur pour les messages
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Gestionnaire pour les fichiers
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    # Gestionnaire pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # Journaliser la création du logger
    logger.info(f"Logger initialized. Logs will be saved to: {log_file_path}")

    return logger


def get_logger(name="chatbot_rag", log_level=None):
    """
    Récupère un logger existant ou en crée un nouveau si nécessaire.

    Args:
        name (str): Nom du logger à récupérer ou créer
        log_level (int, optional): Niveau de journalisation si un nouveau logger est créé

    Returns:
        logging.Logger: Instance du logger demandé
    """
    existing_logger = logging.getLogger(name)
    if existing_logger.handlers:
        return existing_logger
    else:
        return setup_logger(name, log_level or logging.INFO)


# Logger par défaut pour le projet
logger = setup_logger()

# Ajouter un commentaire d'utilisation pour clarifier l'import
"""
Exemple d'utilisation dans d'autres modules:

from src.logger import logger

# Utilisation directe
logger.info("Message d'information")
logger.error("Erreur critique")

# Pour un logger personnalisé
from src.logger import get_logger
custom_logger = get_logger("module_specifique")
custom_logger.debug("Message de débogage spécifique au module")
"""
