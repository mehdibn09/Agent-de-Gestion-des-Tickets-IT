# Dossier de lancement — TicketAssist

Binôme : Mehdi Benjelloun et Oussama Kamil. Projet pédagogique : qualification et suivi des tickets IT. Mise à jour du 11 novembre 2026 ; application de démonstration implémentée, validations externes encore à produire.

## 1. Descriptif

Le support reçoit des descriptions non structurées. L’objectif est de proposer une catégorie, une priorité et une équipe, puis permettre la validation et le suivi humain. Le MVP comporte F1 qualification, F2 aide à la validation avec réponse initiale, F3 persistance et historique. ML TF-IDF/LogReg pour la catégorie ; règles métier pour le reste ; FastAPI, Streamlit, SQLite, paquet installable, CI et Docker.

Rédacteur responsable proposé : Mehdi Benjelloun ; relecteur : Oussama Kamil. Hors périmètre : résolution autonome, systèmes ITSM externes, comptes individuels, RAG et LLM. Le cadrage détaillé est dans docs/cadrage/agent-tickets.md.

## 2. Dataset

Rédacteur responsable proposé : Oussama Kamil ; relecteur : Mehdi Benjelloun. Corpus simulé fourni : 160/32/40 tickets pour entraînement/validation/test, quatre catégories équilibrées, et 12 demandes hors domaine. Format CSV UTF-8, colonnes id/titre/description/categorie/famille/source. Pas de données personnelles réelles. Le fichier data/README.md donne la provenance et le protocole de remplacement.

Les données s’ouvrent localement et permettent de reconstruire le modèle. Familles et descriptions sont séparées. La validation statistique reste limitée par l’origine simulée. L’exigence de données réelles du cours n’est pas satisfaite : obtenir un export autorisé/anonymisé ou une dérogation. Aucune licence de données d’un tiers n’est inventée. Le binôme doit définir sa licence de diffusion.

## 3. Maquette et architecture

Rédacteur responsable proposé : Mehdi Benjelloun ; relecteur : Oussama Kamil. Trois vues sont couvertes par l’interface réalisée : création/analyse, liste filtrée, détail et validation. Le schéma du README décrit le flux Streamlit → API → orchestrateur → modèle/règles → validation → SQLite. Les tests Streamlit exercent la création et la validation via une API en mémoire ; les captures sur les postes du binôme restent à produire.

Voir aussi [les trois maquettes](docs/maquettes.md), fournies comme vues de conception.

## 4. Pipeline pédagogique

Consolidateur proposé : Oussama Kamil ; relecteur : Mehdi Benjelloun. Les tâches ont des critères observables ; les contributions effectives doivent être tracées dans GitHub.

| Tâche | Responsable proposé | Durée prévue | Dépendance | Critère |
| --- | --- | --- | --- | --- |
| T1 Cadrage et règles | Mehdi | 2 j | — | Matrice et périmètre approuvés |
| T2 Données et droits | Oussama | 2 j | — | Autorisation et échantillon réel, ou blocage soumis |
| T3 Maquettes et parcours | Mehdi | 2 j | T1 | Trois vues compréhensibles |
| T4 Corpus et test | Oussama | 2 j | T2 | Séparation et annotations relues |
| T5 API et contrats | Mehdi | 2 j | T3/T4 | Routes et erreurs testées |
| T6 Modèle et règles | Oussama | 2 j | T4 | Modèle et évaluation reproductibles |
| T7 Interface et contrôle d’accès | Mehdi | 2 j | T5/T6 | Cycle démontré selon rôles |
| T8 Persistance et historique | Oussama | 2 j | T5 | Reprise et concurrence testées |
| T9 Recette et notice | Mehdi | 2 j | T7/T8 | Installation sur poste du binôme |
| T10 CI, Docker et métriques | Oussama | 2 j | T7/T8 | Jobs et conteneurs vérifiés |
| T11 Démonstration | Mehdi | 1 j | T9/T10 | Scénario prêt |
| T12 Gel et bilan | Oussama | 1 j | T9/T10 | Tag et rapport final |

Charge prévisionnelle : 11 jours par membre. Jalons : semaine 1 cadrage/données ; semaine 2 modèle/API ; semaine 3 MVP et exécution reproductible ; semaine 4 validation, bilan et soutenance. Les fonctions techniques du démonstrateur sont livrées ; les tâches de droits, relecture et validation des environnements ne sont pas déclarées accomplies.

## Remise et décision

- [x] Code et données simulées fournis.
- [x] Évaluation locale reproductible et tests écrits.
- [ ] Échantillon réel et droits approuvés, ou dérogation reçue.
- [ ] Relectures et contributions individuelles attestées.
- [ ] Pull requests approuvées, issues et CI du dépôt final contrôlées.
- [ ] Windows/Docker vérifiés par le binôme.
- [ ] Tag semaine1-remis posé et enseignant informé.

Décision et visa : réservés à l’enseignant, non reçus. L’application peut être exécutée ; cela ne vaut pas validation académique de tous les critères.
