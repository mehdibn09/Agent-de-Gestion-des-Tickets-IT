# Cadrage — Agent de gestion des tickets IT

## Besoin et utilisateurs

Assister un demandeur et un opérateur de support pour qualifier, prioriser, orienter et suivre une demande. Le scénario est pédagogique, sans déploiement métier observé. Le MVP comprend F1 qualification, F2 validation humaine avec réponse initiale, F3 persistance et suivi.

## Choix de l’approche

| Critère | Décision |
| --- | --- |
| Données étiquetées | Quatre catégories ; corpus simulé pour le prototype, corpus réel à obtenir |
| Vérifiabilité | Priorité déterministe, historique horodaté, revue obligatoire de la catégorie |
| Coût par requête | TF-IDF et régression logistique exécutés localement, pas d’appel payant |
| Conséquence d’une erreur | Mauvaise orientation : l’humain valide avant prise en charge |

Approche retenue : **ML supervisé pour la classification + règles métier pour priorité, équipe et réponse**. Un RAG n’apporterait pas une solution au manque d’étiquettes ; un LLM autonome n’est pas requis pour les trois fonctionnalités.

## Périmètre livré

Quatre catégories, matrice à neuf combinaisons, abstention et escalade P1, tickets A_VALIDER, validation admin, transitions suivies et reprise après redémarrage. Les modifications concurrentes exigent de recharger la version courante.

## Critères fonctionnels

- Toute création reçoit un identifiant et une trace de création.
- Tout ticket reste A_VALIDER jusqu’à une catégorie explicitement confirmée par un admin.
- Les neuf priorités correspondent à la matrice et ne dépendent pas du score.
- Une clé client n’effectue aucune modification administrative.
- Une clôture sans compte rendu est refusée ; une version périmée produit un conflit.

## Hors périmètre

Réparation automatique, scripts sur postes, réinitialisation de mots de passe, GLPI/ServiceNow, comptes individuels, SLA et production multi-organisations. Les messages sont des gabarits de qualification, pas des solutions garanties.
