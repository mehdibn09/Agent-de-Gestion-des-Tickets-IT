# Compte rendu de livraison — 11 novembre 2026

## Objectif et démarche

Transformer le sujet de gestion des tickets en une application exécutable en reprenant la séparation des couches et les contrôles du projet RAG de référence. Le code TicketAssist et les jeux simulés sont nouveaux ; aucun résultat du projet de référence n’est réattribué au binôme.

## Réalisations du périmètre

Classification, abstention, priorité par matrice, affectation, réponse initiale, revue administrative, transitions, historique SQLite et concurrence optimiste. API protégée sur toutes les routes métier. Interface uniquement cliente de HTTP. Commandes d’installation, de configuration, d’entraînement, d’analyse et d’évaluation. Construction de roue et de distribution source.

## Difficultés traitées

- Les scores de confiance ne suffisent pas à décider d’une priorité : une matrice métier séparée est utilisée.
- Une prédiction erronée au-dessus du seuil reste possible : aucune création n’est automatiquement validée.
- Deux opérateurs peuvent travailler sur la même fiche : le second envoi d’une ancienne version est refusé.
- Une résolution ne doit pas perdre la précédente : les notes de clôture sont conservées dans les événements.
- Le jeu de démonstration ne doit pas être présenté comme réel : les fichiers et rapports l’indiquent.
- Une roue ne contient pas le modèle ou les données : l’essai hors dépôt utilise des chemins externes.

## Vérification

Consulter `docs/validation-locale.txt` pour les commandes et résultats réellement observés. La CI, Windows, Docker et la validation métier distante ne sont pas déclarés exécutés lorsqu’ils ne l’ont pas été.

## Contributions

Répartition de référence : Mehdi Benjelloun, cadrage/API/interface/documentation ; Oussama Kamil, données/modèle/règles/persistance/évaluation. Les auteurs doivent relire, exécuter et s’approprier leur travail. Les commits, issues, approbations et visas individuels ne sont pas fabriqués par la génération de cette livraison.

## Suite

Obtenir les données réelles autorisées, faire relire les annotations et la matrice, vérifier les environnements Windows et Docker, exécuter la CI sur le dépôt propre, puis préparer la démonstration et une release v1.0.0.
