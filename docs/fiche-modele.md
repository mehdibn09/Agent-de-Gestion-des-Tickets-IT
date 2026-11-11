# Fiche modèle — TicketAssist

## Identité du modèle

TicketAssist 1.0.0. Pipeline TF-IDF et régression logistique multiclasse, exécuté localement, sans LLM ni service externe. Modèle reconstruit dans `models/tickets.joblib` ; chemin alternatif `TICKET_MODEL`.

## Usage prévu

Assister la qualification de tickets informatiques en français en proposant réseau, matériel, logiciel ou accès. La classification prépare une proposition ; un opérateur confirme explicitement la catégorie avant traitement.

## Usages exclus

Réparation autonome, décisions sur les personnes, production critique, diagnostic de sécurité garanti, tickets multilingues non évalués et déploiement multi-organisations sans contrôle d’accès individuel.

## Données d’entraînement

160 descriptions simulées, 40 par classe ; 32 descriptions de validation séparées par familles. Corpus généré pour cette livraison avec assistance IA. Pas de tickets d’une entreprise ou de l’EMSI. Les familles et descriptions sont contrôlées, les paraphrases sémantiques ne peuvent pas être toutes détectées.

## Performances mesurées

Sur 40 cas de test simulés : F1 macro 0.975, exactitude brute 0.975, couverture 0.975, exactitude acceptée 0.974. Au seuil 0,45, 8/12 demandes hors domaine sont refusées. Ces résultats restreints ne valident pas la généralisation métier.

## Limites connues

Un incident peut concerner plusieurs catégories, alors que le modèle est mono-étiquette. Les négations, implicites et mots inconnus peuvent induire une erreur. Le score n’est pas calibré comme probabilité de justesse. Une erreur matériel vers logiciel subsiste sur le test, malgré une confiance supérieure au seuil.

## Biais mesurés

Rapport descriptif par longueur dans `models/metrics.json`. Données synthétiques équilibrées, vocabulaire partagé par la conception : pas de représentation des fréquences d’un service réel. Aucune mesure d’équité sociale, aucune déduction causale à partir de la longueur.

## Explicabilité

`ticket explain` affiche la contribution TF-IDF × coefficient des termes présents au logit de la classe proposée, avec interception et somme complète. Le total reconstruit le score linéaire ; ce ne sont pas des valeurs SHAP ni une preuve de causalité. Un terme peut influencer plusieurs classes.

## Conditions d’usage

Validation humaine requise pour tous les tickets, en particulier les abstentions et P1. Impact et urgence sont déclarés ; leur matrice métier doit être approuvée localement. Ne transmettre aucun mot de passe. Les deux rôles partagés ne remplacent pas un système de comptes individuels. Modèles joblib de confiance seulement ; clés et base hors Git.

## Maintenance

Réentraîner sur des CSV autorisés et séparés, recalculer les métriques, refaire les tests et redémarrer l’API. Adapter la documentation et la version en cas de changement de contrat. Conserver la preuve des droits du corpus et les versions des dépendances. Les décisions de validation restent sous la responsabilité de l’opérateur.
