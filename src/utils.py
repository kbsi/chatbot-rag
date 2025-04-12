import json
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from logger import logger


def load_documents(file_path: str) -> List[Document]:
    """
    Charge les documents depuis un fichier JSON Lines.

    Args:
        file_path: Chemin vers le fichier contenant les documents

    Returns:
        List[Document]: Liste des documents chargés
    """
    documents = []
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix == '.jsonl':
        # Chargement depuis un fichier JSONL
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip() and not line.strip().startswith('//'):  # Ignorer les commentaires
                    try:
                        data = json.loads(line)
                        # Adaptation en fonction de la structure de vos données
                        content = data.get(
                            'text', '') or data.get('content', '')
                        # Extraire les métadonnées, mais s'assurer qu'elles sont de types primitifs
                        metadata = {}
                        for k, v in data.items():
                            if k not in ['text', 'content']:
                                if isinstance(v, (str, int, float, bool)):
                                    metadata[k] = v
                                elif isinstance(v, dict):
                                    # Aplatir les dictionnaires imbriqués
                                    for sub_k, sub_v in v.items():
                                        if isinstance(sub_v, (str, int, float, bool)):
                                            metadata[f"{k}_{sub_k}"] = sub_v

                        doc = Document(page_content=content, metadata=metadata)
                        documents.append(doc)

                    except json.JSONDecodeError:
                        logger.warning(
                            f"Skipping invalid JSON line in {file_path}")
    else:
        # Support pour d'autres formats pourrait être ajouté ici
        logger.error(f"Unsupported file format: {file_path.suffix}")
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    logger.info(f"Loaded {len(documents)} documents from {file_path}")
    # Vérifier que les documents ont bien les attributs nécessaires
    if documents and hasattr(documents[0], 'page_content') and hasattr(documents[0], 'metadata'):
        logger.info(f"Document type: {type(documents[0])}")
        logger.info(
            f"First document preview: {documents[0].page_content[:50]}...")
    else:
        logger.warning("Documents may not have expected structure")

    return documents
