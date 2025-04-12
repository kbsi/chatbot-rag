# Utilisation du système de journalisation (Logger)

Ce projet utilise un système de journalisation centralisé pour assurer une cohérence dans les logs et faciliter le débogage.

## Comment utiliser le logger

### Import de base

```python
from logger import logger

# Exemples d'utilisation
logger.debug("Message de débogage détaillé")
logger.info("Information générale")
logger.warning("Avertissement")
logger.error("Erreur importante")
logger.critical("Erreur critique")
```

### Logger personnalisé par module

Si vous avez besoin d'un logger spécifique pour un module particulier:

```python
from logger import get_logger

# Créer un logger avec un nom spécifique
module_logger = get_logger("nom_du_module")
module_logger.info("Message spécifique à ce module")
```

## Configuration

Les logs sont stockés dans le répertoire `logs/` à la racine du projet, avec un fichier par session nommé selon le format `chatbot_rag_YYYYMMDD_HHMMSS.log`.

Tous les messages sont également affichés dans la console.
