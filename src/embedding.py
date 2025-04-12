import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from logger import logger
from constants import (
    DEFAULT_EMBEDDING_MODEL, ENV_TOKENIZERS_PARALLELISM, ENV_TOKENIZERS_PARALLELISM_VALUE,
    DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_DB_PATH
)


def split_documents(documents, chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP):
    """
    Divise les documents en chunks avec un chevauchement spécifié.
    """
    from langchain_core.documents import Document

    # Vérifier les documents avant le traitement
    if not documents:
        logger.warning("Empty document list provided to split_documents")
        return []

    # Log avant la division
    logger.info(
        f"Splitting {len(documents)} documents, first document type: {type(documents[0])}")
    if documents and hasattr(documents[0], 'page_content'):
        logger.info(
            f"First document content sample: {documents[0].page_content[:50]}...")

    # Pour les petits documents, aucun besoin de split
    # Simplement les retourner comme ils sont
    if all(len(doc.page_content) < chunk_size for doc in documents if hasattr(doc, 'page_content')):
        logger.info("Documents are small enough, skipping splitting")
        return documents

    # Sinon, procéder au split
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    overlap_tokens = int(chunk_size * chunk_overlap)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap_tokens,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    # Splitter les documents
    try:
        chunks = splitter.split_documents(documents)
        logger.info(
            f"Created {len(chunks)} chunks from {len(documents)} documents")

        # Vérifier que les chunks sont des objets Document
        return chunks
    except Exception as e:
        logger.warning(f"Error splitting documents: {str(e)}")
        return documents


def setup_vector_store(documents, persist_directory=DEFAULT_DB_PATH, force_rebuild=False,
                       embedding_model_name=DEFAULT_EMBEDDING_MODEL):
    """
    Configure la base de données vectorielle avec les documents fournis.
    """
    # Importer Document depuis le bon module
    from langchain_core.documents import Document
    from copy import deepcopy

    # Initialisation du modèle d'embedding
    embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
    logger.info(f"Using embedding model: {embedding_model_name}")

    # Vérification si la base vectorielle existe déjà
    if os.path.exists(persist_directory) and not force_rebuild:
        logger.info(f"Loading existing vector store from {persist_directory}")
        return Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

    # Vérification initiale des documents
    if not documents:
        raise ValueError("No documents provided for vector store creation")

    # Log des types de documents reçus
    doc_types = [type(doc) for doc in documents[:3]] if len(
        documents) >= 3 else [type(doc) for doc in documents]
    logger.info(f"Document types before processing: {doc_types}")

    # Vérification et conversion des documents si nécessaire
    validated_docs = []
    for i, doc in enumerate(documents):
        if isinstance(doc, str):
            validated_docs.append(Document(page_content=doc, metadata={}))
        elif hasattr(doc, 'page_content'):
            validated_docs.append(doc)
        else:
            logger.warning(f"Invalid document at index {i}: {type(doc)}")

    if not validated_docs:
        raise ValueError(
            "No valid documents provided for vector store creation")

    # Division des documents en chunks
    logger.info("Splitting documents into chunks...")
    chunks = split_documents(validated_docs)

    if not chunks:
        logger.warning("No chunks created, using original documents")
        chunks = validated_docs

    # Étape de validation supplémentaire pour s'assurer que tous les chunks sont des objets Document
    logger.info("Validating chunks before metadata processing...")
    validated_chunks = []
    for i, chunk in enumerate(chunks):
        if isinstance(chunk, str):
            logger.info(f"Converting string chunk at index {i} to Document")
            validated_chunks.append(Document(page_content=chunk, metadata={}))
        elif hasattr(chunk, 'page_content'):
            validated_chunks.append(chunk)
        else:
            logger.warning(f"Invalid chunk at index {i}, type: {type(chunk)}")
            try:
                validated_chunks.append(
                    Document(page_content=str(chunk), metadata={}))
            except Exception as e:
                logger.warning(
                    f"Could not convert chunk to Document: {str(e)}")

    logger.info(
        f"Validated {len(validated_chunks)} chunks out of {len(chunks)} original chunks")
    chunks = validated_chunks

    def filter_complex_metadata_safely(metadata):
        """
        Version sécurisée de filter_complex_metadata qui gère proprement les chaînes et les None.
        """
        if metadata is None:
            return {}

        if isinstance(metadata, str):
            # Si metadata est une chaîne, retourner un dictionnaire avec cette chaîne
            return {"content": metadata}

        if not isinstance(metadata, dict):
            # Si ce n'est pas un dictionnaire, renvoyer un dictionnaire vide
            return {}

        # Pour les dictionnaires, nous devons nous assurer que toutes les valeurs sont des types simples
        # Ne pas utiliser filter_complex_metadata qui cause des problèmes
        filtered_metadata = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                filtered_metadata[k] = v
            elif isinstance(v, dict):
                # Pour les dictionnaires imbriqués, aplatir avec des préfixes
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (str, int, float, bool, type(None))):
                        filtered_metadata[f"{k}_{sub_k}"] = sub_v
            elif isinstance(v, (list, tuple)):
                # Pour les listes, convertir en chaîne JSON si possible
                try:
                    filtered_metadata[k] = json.dumps(v)
                except:
                    filtered_metadata[k] = str(v)
            else:
                # Pour tout autre type, convertir en chaîne
                filtered_metadata[k] = str(v)

        return filtered_metadata

    # Filtrage des métadonnées complexes
    filtered_documents = []
    for chunk in chunks:
        # Créer un nouveau Document quoi qu'il arrive
        if isinstance(chunk, str):
            # Cas simple: c'est une chaîne
            doc = Document(page_content=chunk, metadata={})
        elif hasattr(chunk, 'page_content'):
            # Cas normal: c'est un objet Document ou similaire
            try:
                # Extraire le contenu
                content = chunk.page_content

                # Récupérer et sécuriser les métadonnées
                if hasattr(chunk, 'metadata'):
                    # Ne pas utiliser deepcopy qui peut causer des problèmes
                    metadata = filter_complex_metadata_safely(chunk.metadata)
                else:
                    metadata = {}

                # Créer un nouveau Document propre
                doc = Document(page_content=content, metadata=metadata)
            except Exception as e:
                # En cas d'erreur, créer un Document avec le contenu disponible
                logger.warning(
                    f"Error processing document attributes: {str(e)}")
                if hasattr(chunk, 'page_content'):
                    doc = Document(
                        page_content=chunk.page_content, metadata={})
                else:
                    doc = Document(page_content=str(chunk), metadata={})
        else:
            # Cas exceptionnel: c'est un objet inconnu
            doc = Document(page_content=str(chunk), metadata={})

        # Ajouter le document à la liste filtrée
        filtered_documents.append(doc)

    # Vérifier qu'il reste des documents après filtrage
    if not filtered_documents:
        raise ValueError(
            "No valid documents after filtering metadata. Check document format.")

    # Créer et persister la base vectorielle
    logger.info(
        f"Creating new vector store with {len(filtered_documents)} documents in {persist_directory}...")
    vector_store = Chroma.from_documents(
        documents=filtered_documents,
        embedding=embedding_model,
        persist_directory=persist_directory
    )

    logger.info(
        f"Vector store created successfully with {len(filtered_documents)} embeddings")
    return vector_store
