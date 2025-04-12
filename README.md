# RAG Chatbot avec LM Studio

Ce projet implémente un chatbot basé sur la Génération Augmentée par Récupération (RAG) qui utilise LM Studio comme backend de modèle de langage. Le système récupère des informations pertinentes à partir d'un corpus de documents pour fournir des réponses précises et contextualisées.

## Fonctionnalités

- Chargement et traitement de documents à partir de fichiers JSONL
- Découpage de texte avec chevauchement pour une meilleure préservation du contexte
- Embeddings vectoriels utilisant sentence-transformers
- Stockage vectoriel efficace avec ChromaDB
- Implémentation RAG avec LangChain
- Interface CLI pour une interaction facile
- API REST avec Flask pour l'intégration dans des applications web
- Interface utilisateur web avec React et Tailwind CSS

## Configuration

### Prérequis

1. Python 3.9+
2. Pipenv
3. LM Studio installé et exécuté localement avec le serveur API activé
4. Node.js et npm (pour le frontend)

### Installation

1. Clonez ce dépôt
2. Installez les dépendances Python en utilisant Pipenv :
   ```
   pipenv install
   ```
3. Installez les dépendances du frontend :
   ```
   cd frontend
   npm install
   ```
4. Démarrez LM Studio et activez le serveur API local (généralement sur le port 1234)

### Utilisation

#### Mode CLI

1. Placez vos données de documents dans le fichier `data/train.jsonl`
2. Exécutez le chatbot :
   ```
   pipenv run python src/main.py
   ```

#### Mode API + Frontend

1. Démarrez le serveur API :
   ```
   pipenv run python src/api.py
   ```
2. Dans un autre terminal, démarrez le frontend :
   ```
   cd frontend
   npm start
   ```
3. Accédez à l'interface web à l'adresse http://localhost:3000

#### Options de ligne de commande (CLI)

- `--data_path` : Chemin vers les données d'entraînement (par défaut : data/train.jsonl)
- `--db_path` : Chemin pour stocker la base de données vectorielle (par défaut : chroma_db)
- `--rebuild_db` : Force la reconstruction de la base de données vectorielle

### Commandes CLI

Une fois le chatbot en cours d'exécution :

- Tapez vos questions pour obtenir des réponses
- Tapez `sources` pour voir les sources de la dernière réponse
- Tapez `exit` ou `quit` pour terminer la session

### Endpoints API

- `POST /chat` : Envoyer une requête et obtenir une réponse
- `GET /sources` : Récupérer les sources de la dernière réponse
- `POST /load_documents` : Charger un nouveau fichier JSONL

## Tests

Exécutez les tests pour vérifier la fonctionnalité du système :

```
pipenv run python -m pytest src/tests/
```

## Structure du projet

- `src/main.py` : Point d'entrée principal (CLI)
- `src/api.py` : Serveur API REST
- `src/embedding.py` : Gestion des embeddings et du stockage vectoriel
- `src/rag.py` : Implémentation du pipeline RAG
- `src/chatbot.py` : Interface CLI
- `src/utils.py` : Fonctions utilitaires
- `src/logger.py` : Configuration de la journalisation
- `src/constants.py` : Constantes du projet
- `frontend/` : Application web React/Tailwind
- `data/` : Corpus de documents
- `chroma_db/` : Stockage de la base de données vectorielle
- `logs/` : Fichiers journaux

## Personnalisation

Vous pouvez personnaliser le système en :

1. Ajustant la taille des fragments et le chevauchement dans `embedding.py`
2. Modifiant le modèle de prompt dans `rag.py`
3. Ajoutant de nouveaux formats de documents dans `utils.py`
4. Configurant l'interface web dans le dossier `frontend/`

## Variables d'environnement

- `LM_STUDIO_URL` : URL du serveur LM Studio (par défaut : http://localhost:1234/v1)
- `LM_STUDIO_MODEL` : Nom du modèle à utiliser
- `LM_TEMPERATURE` : Température pour la génération de texte
- `DATA_PATH` : Chemin vers les données d'entraînement
- `DB_PATH` : Chemin pour stocker la base de données vectorielle
