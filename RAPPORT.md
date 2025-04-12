# Rapport sur le développement du chatbot RAG

## Difficultés rencontrées

### Compréhension conceptuelle du RAG

- **Fonctionnement général** : La prise en main du concept RAG a représenté une courbe d'apprentissage importante. Bien que le principe soit simple en théorie - récupérer des informations pertinentes puis générer une réponse - la mise en œuvre pratique et l'orchestration des différents composants se sont révélées complexes.
- **Approche des embeddings** : Les embeddings constituent un concept abstrait dont la compréhension intuitive reste difficile. J'ai réussi à implémenter le code nécessaire avec l'aide de Copilot, mais la dimension mathématique sous-jacente reste un domaine que je souhaiterais approfondir à l'avenir.
- **Optimisation des paramètres** : Le réglage des paramètres comme le nombre de chunks à récupérer ou les seuils de similarité s'est fait principalement de manière empirique. C'est un processus qui demande beaucoup d'expérimentation et dont j'aimerais mieux comprendre les fondements.

### Défis techniques

- **Intégration de ChromaDB** : La mise en place d'une base de données vectorielle était une première pour moi. Les concepts de collections, d'index et de recherche par similarité ont nécessité un temps d'adaptation et plusieurs tentatives avant d'obtenir une configuration fonctionnelle.
- **Équilibre du contexte** : Trouver le juste équilibre entre la quantité d'informations à inclure dans le contexte et les limitations de tokens des modèles a été un exercice délicat. Trop peu d'informations donnait des réponses incomplètes, trop d'informations provoquait des erreurs ou diluait la pertinence.
- **Prétraitement des documents** : La préparation des données pour l'indexation s'est avérée plus nuancée que prévu. Le découpage des documents en segments cohérents tout en préservant le contexte nécessaire a demandé plusieurs itérations.

### Limitations des outils

- **Expérience avec Copilot** : L'utilisation de GitHub Copilot s'est révélée parfois frustrante :
  - Suggestions parfois déconnectées du contexte spécifique du RAG
  - Propositions redondantes ou mal adaptées à l'architecture existante
  - Difficulté à obtenir des suggestions pertinentes pour les aspects les plus spécialisés du RAG

## Améliorations possibles

### Architecture et performances

- Implémenter un système de mise en cache des requêtes fréquentes pour améliorer les temps de réponse
- Explorer des techniques de "hybrid search" combinant recherche vectorielle et BM25 pour améliorer la pertinence
- Mettre en place un système de feedback utilisateur pour affiner les résultats de recherche

### Expérience utilisateur

- Développer une interface plus intuitive permettant de visualiser les sources utilisées pour générer les réponses
- Ajouter un système d'explication du raisonnement du modèle pour renforcer la transparence
- Implémenter un mécanisme de conversation avec mémoire contextuelle plus sophistiqué

### Qualité des données

- Améliorer les techniques de chunking avec un découpage plus intelligent basé sur la sémantique
- Mettre en place un pipeline de mise à jour automatique de la base de connaissances
- Développer un système de qualification des sources pour pondérer leur fiabilité

### Évaluation et monitoring

- Créer un framework d'évaluation systématique de la qualité des réponses
- Implémenter des métriques de suivi de performance (latence, pertinence, satisfaction utilisateur)
- Mettre en place un système de détection de "hallucinations" du modèle

Cette expérience, malgré ses défis, a permis d'acquérir une compréhension approfondie des systèmes RAG et ouvre de nombreuses perspectives d'amélioration pour les futures itérations du projet.
