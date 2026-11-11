## Livrable 2 — Dataset et protocole d’évaluation

**Rédacteur responsable : Oussama Kamil** · Relecteur : Mehdi Benjelloun · Annotations et droits à relire avant remise.

### 2.1 Description du corpus disponible

| Rubrique | Réponse |
| --- | --- |
| Nom et source | TicketAssist Démonstration ; fichiers locaux `data/train.csv`, `validation.csv`, `test.csv`, `hors_domaine.csv` |
| Producteur | Données simulées préparées pour ce projet avec assistance IA ; aucun export d’un organisme tiers |
| Volume | 160 tickets d’entraînement, 32 de validation, 40 de test et 12 demandes hors domaine |
| Échantillon de remise | `data/sample/tickets_exemple.csv` : 100 lignes, 25 par catégorie, 17,047 octets UTF-8 |
| Structure | CSV : `id`, `titre`, `description`, `categorie`, `famille`, `source` ; le modèle utilise uniquement la description |
| Langue et période | Français ; aucune période d’observation réelle ; corpus préparé pour la livraison de novembre 2026 |
| Droits | Pas de contenu tiers repris ; licence de diffusion à arrêter par le binôme. Tout futur export réel exige une autorisation préalable |
| Données personnelles | Aucune identité, coordonnée, adresse interne ou secret réel dans les CSV joints |
| Emplacement complet | Dossier `data/` du projet ; aucune source distante requise pour le prototype |

### 2.2 Qualité constatée

Les fichiers sont lisibles, les champs requis sont renseignés et les classes sont équilibrées. Les descriptions normalisées et les familles sont distinctes entre entraînement, validation et test. Les variantes d’une même famille restent à l’entraînement. L’échantillon de 100 lignes est un **sous-ensemble de train**, pas une donnée supplémentaire à concaténer ni un test indépendant.

La redondance des motifs et le vocabulaire commun à des données rédigées selon les mêmes conventions peuvent rendre le score optimiste. Aucun contrôle de doublons exacts ne suffit à éliminer toutes les paraphrases. Les annotations sont proposées ; leur validation humaine n’est pas encore attestée.

### 2.3 Couverture fonctionnelle

| Fonction | Données utilisées | Justification et limite |
| --- | --- | --- |
| F1 | Descriptions/catégories et matrice impact × urgence | Entraîne le prototype et teste les règles ; les fréquences ne représentent pas un service réel |
| F2 | Validation, test, hors domaine et gabarits de réponse | Mesure le compromis réponse/abstention et illustre la revue humaine ; pas de garantie de détection de tous les cas hors domaine |
| F3 | Scénarios de création, transition et concurrence | Teste SQLite et l’historique ; aucun historique d’incidents métier réel n’est disponible |

### 2.4 Source cible et alternative de repli

**Source cible :** obtenir auprès d’un support volontaire un export autorisé, anonymisé avant publication et annoté dans les quatre catégories. Ni l’accord ni l’accès à cet export ne sont acquis. Retirer les identités, coordonnées, secrets et informations internes ; conserver la preuve des droits d’usage.

**Repli disponible :** CSV simulés joints, accessibles localement sans lien externe. Ils permettent la démonstration complète, mais font perdre la représentativité métier et **ne remplissent pas l’exigence d’un échantillon réel**. Ce point requiert des données autorisées ou une dérogation explicite avant validation académique finale.

### 2.5 Jeu de test, indicateurs et résultats observés

Le test comporte **40 tickets**, dix par catégorie, séparés du train et de la validation ; les réponses attendues sont les catégories rédigées dans les CSV avec assistance IA. Oussama et Mehdi doivent les relire contradictoirement. Les **12 demandes hors domaine** mesurent les abstentions. Les **93 tests logiciels**, distincts de ces observations statistiques, couvrent notamment règles, API, droits, transitions, concurrence et interface.

| Indicateur | Résultat local | Interprétation |
| --- | --- | --- |
| F1 macro brut | 0.975 | Qualité sur 40 cas simulés ; cible pédagogique proposée ≥ 0,80 |
| Exactitude brute | 97.5% | Une catégorie erronée sur le test |
| Couverture au seuil 0,45 | 97.5% | 39 réponses acceptées, une abstention |
| Exactitude acceptée | 97.4% | Une erreur subsiste au-dessus du seuil |
| Refus hors domaine | 8/12 | Quatre demandes hors domaine ne sont pas refusées |

Preuves : `models/metrics.json`, `models/diagnostic.json`, `models/courbe_seuil.csv`, `docs/validation-locale.txt`. La courbe de seuil utilise la validation, pas le test. Une description de moniteur avec des lignes verticales est classée logiciel au lieu de matériel : cet échec est conservé dans le diagnostic, sans réécriture du test pour le masquer.

**Contrôle de préparation :** corpus simulé, échantillon et protocole disponibles. **Validation attendue :** relecture des annotations, droits/licence et échantillon réel ou dérogation.
