# Dossier de lancement — Semaine 1
## TicketAssist — Agent intelligent de qualification et de suivi des tickets IT

| Identification | Information |
| --- | --- |
| Formation | Projet du cours « Développement et déploiement d’applications intelligentes » |
| Équipe | **Mehdi Benjelloun** · **Oussama Kamil** |
| Dépôt de référence | Projet TicketAssist, évolution métier de Sentiment-app |
| Version du dossier | 1.1 — mise à jour du 11 novembre 2026 |
| Référence du catalogue | Projet n° 10 — Agent de gestion des tickets IT |
| Catégorie / niveau | Support et ITSM / Intermédiaire |
| Sujet professionnel recommandé | Non — mention du catalogue de l’encadrant |
| Horizon de réalisation | Quatre semaines ; calendrier proposé du 16 novembre au 13 décembre 2026 |

**Synthèse.** TicketAssist transforme une description d’incident en proposition de catégorie, priorité, équipe et réponse initiale. Un opérateur confirme la qualification avant traitement ; SQLite conserve le ticket et ses événements. Le démonstrateur est implémenté et testé localement. Ce dossier organise sa remise et sa validation ; il ne reconstitue pas un historique de contributions individuelles.

**Point d’attention pour la validation du sujet.** Le corpus joint est simulé. L’exigence du cours portant sur un échantillon réel reste à satisfaire par un export autorisé et anonymisé, ou par une dérogation explicite de l’enseignant. La licence finale, les relectures, la CI du dépôt distant et le visa enseignant ne sont pas déclarés acquis.

### Gouvernance et répartition du binôme

| Livrable | Rédacteur responsable désigné | Relecteur désigné | Fichier de remise |
| --- | --- | --- | --- |
| 1. Descriptif | Mehdi Benjelloun | Oussama Kamil | `docs/semaine1/1-descriptif.md` |
| 2. Dataset | Oussama Kamil | Mehdi Benjelloun | `docs/semaine1/2-dataset.md` + `data/sample/` |
| 3. Maquette globale | Mehdi Benjelloun | Oussama Kamil | `docs/semaine1/3-maquette.md` + `docs/semaine1/img/` |
| 4. Pipeline | Oussama Kamil, consolidation | Mehdi Benjelloun | `docs/semaine1/4-pipeline.md` |

Les responsables doivent relire et s’approprier les documents préparés avec assistance IA. Chaque membre saisit personnellement ses tâches. Les contributions effectives se prouvent par les commits, pull requests et relectures, pas par la seule présence de son nom.

**Circuit de remise.** Déposer la répartition dans `docs/semaine1/README.md` ; travailler sur quatre branches `semaine1/descriptif`, `semaine1/dataset`, `semaine1/maquette`, `semaine1/pipeline` ; ouvrir une PR par livrable ; obtenir la relecture de l’autre membre ; fusionner les versions approuvées ; créer les issues du planning ; poser le tag `semaine1-remis` sur le commit retenu puis informer l’enseignant. Ces actions restent à confirmer dans GitHub.

## Accès aux livrables

- [Descriptif](1-descriptif.md)
- [Dataset](2-dataset.md)
- [Maquette](3-maquette.md)
- [Pipeline](4-pipeline.md)

## Remise, preuves et décision de l’enseignant

### Checklist de remise — à compléter à partir des preuves

- [x] Quatre livrables Markdown et répartition préparés dans cette mise à jour.
- [x] Échantillon simulé de 100 tickets et trois maquettes SVG fournis.
- [x] Résultats locaux de référence disponibles : 93 tests réussis ; couverture mesurée 97,33 % ; cycle API et roue hors dépôt vérifiés.
- [ ] Annotations, périmètre et matrice relus et approuvés par le binôme.
- [ ] Données réelles autorisées/anonymisées obtenues, ou dérogation reçue ; licence définie.
- [ ] Quatre PR relues et fusionnées ; images et Mermaid affichés sur GitHub.
- [ ] Issues créées et contributions personnelles traçables.
- [ ] Recettes Windows/Docker et CI distante exécutées.
- [ ] Tag `semaine1-remis` posé ; enseignant informé.

Les cases cochées ci-dessus décrivent les artefacts préparés ou les vérifications locales observées. Elles ne valent pas approbation du relecteur ni décision de l’enseignant.

### Grille de décision — état présenté à l’enseignant

| Critère | Type | État factuel à examiner |
| --- | --- | --- |
| Données accessibles et échantillon réel | Bloquant | Simulé accessible ; exigence de données réelles non satisfaite |
| MVP réalisable en quatre semaines | Bloquant | Démonstrateur implémenté ; consolidation et validations externes planifiées |
| Répartition et relecteur distinct | Bloquant | Affectations définies ; contributions et approbations à prouver |
| Droits et données personnelles | Bloquant | Aucune donnée personnelle réelle ; droits/licence définitifs à formaliser |
| Architecture cohérente | À améliorer | Schéma et séparation des couches documentés et testés localement |
| Écrans couvrant le MVP | À améliorer | Trois maquettes, interface et tests d’interaction fournis ; rendu GitHub à vérifier |
| Tâches courtes et charge équilibrée | À améliorer | 16 tâches, 15 jours par membre ; issues à confirmer |
| Repli et test définis | À améliorer | CSV simulés locaux, 40 cas de classification et 12 hors domaine ; annotations à relire |

**Décision réservée à l’enseignant :** ☐ Validé · ☐ À reprendre · ☐ Refusé. Date et visa : non reçus.

Ce dossier constitue la référence de cadrage pour P1, documente les données et indicateurs pour P3, et organise le suivi pour P7. Les preuves individuelles restent les contributions et relectures effectuées dans le dépôt.
