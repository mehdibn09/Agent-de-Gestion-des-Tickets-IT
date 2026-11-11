# Données TicketAssist

## Provenance

Tous les CSV fournis sont des **données simulées créées pour ce projet avec assistance IA**. Aucun historique réel, aucune identité ni donnée d’entreprise n’est utilisé. Ne pas les présenter comme un export de l’EMSI ou d’un service support. Les catégories et formulations demandent une revue humaine avant une évaluation académique finale.

| Jeu | Lignes | Usage |
| --- | --- | --- |
| train.csv | 160 | 20 familles par catégorie, deux formulations par famille |
| validation.csv | 32 | Huit cas par catégorie, réglage du seuil |
| test.csv | 40 | Dix cas par catégorie, mesure finale |
| hors_domaine.csv | 12 | Demandes simulées sans rapport avec le support IT |

Les colonnes requises pour l’apprentissage sont `id`, `titre`, `description`, `categorie`, `famille`. La colonne `source` documente la provenance. Les catégories possibles sont `acces`, `logiciel`, `materiel`, `reseau`. La classification porte sur la description ; impact et urgence sont fournis à l’API et traités par les règles, pas appris à partir du texte.

Les familles du jeu train sont exclusivement dans train. Aucune famille ni description normalisée n’est partagée entre train, validation et test. Cela élimine les doublons exacts, pas les ressemblances sémantiques entre exemples rédigés selon les mêmes conventions. Le test reste petit et optimiste pour une généralisation métier.

## Remplacer par des données autorisées

1. Obtenir un export autorisé, anonymisé avant toute publication ; conserver la preuve d’autorisation et la licence.
2. Retirer noms, contacts, identifiants, adresses internes et secrets. Vérifier les pièces jointes et champs libres.
3. Mapper les catégories vers les quatre classes, sans déduire artificiellement les étiquettes de prédictions du même modèle.
4. Séparer par incident, famille, demandeur ou période selon le risque de fuite. Conserver un test indépendant que l’on ne règle pas.
5. Exporter trois CSV avec les colonnes ci-dessus ; les passer à `ticket train --train chemin/train.csv --validation chemin/validation.csv` puis `ticket evaluate --test chemin/test.csv --output models/metrics.json`.
6. Redémarrer l’API après entraînement et réécrire la fiche modèle, la provenance et les résultats. Éviter de versionner un modèle contenant des textes de référence réels.

L’évaluation CLI refuse un test identique aux fichiers d’apprentissage et toute réutilisation de leurs textes normalisés ou familles. Elle ne détecte pas toutes les paraphrases ; la revue de séparation demeure nécessaire.

**Exigence du cours :** un échantillon réel n’est pas fourni ici. Ce point bloque une déclaration de conformité totale au dossier de lancement, sauf dérogation explicite de l’enseignant.
