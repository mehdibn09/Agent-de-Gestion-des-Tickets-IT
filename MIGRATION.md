# Dépôt GitHub propre pour TicketAssist

Cette livraison est le projet complet de gestion des tickets. Ce n’est pas un correctif à ajouter à côté des fichiers de l’ancienne application de sentiment.

## Méthode simple : nouveau dépôt

1. Extraire `TicketAssist_Complet.zip` et ouvrir son dossier `TicketAssist`.
2. Créer un dépôt GitHub vide, par exemple `TicketAssist`.
3. Envoyer le **contenu** du dossier TicketAssist à la racine, en conservant `.github`, `.streamlit` et les autres chemins.
4. Vérifier dans Actions que les jobs se terminent. Ne pas pousser le ZIP, .env, .venv, le fichier .joblib ou SQLite.

## Conserver le dépôt Sentiment-app

Conserver d’abord l’historique Git et la release v0.6.0. Effectuer la migration dans une branche dédiée `ticketassist-v1`, en remplaçant l’ancien arbre applicatif par le contenu complet de cette livraison. Ne pas conserver les anciens `sentiment_app/`, anciens scripts `src/` et anciens tests : ils correspondent à une autre application et peuvent rendre les contrôles incohérents. Les dossiers `api/`, `ui/`, `tests/`, `src/`, `scripts/`, la configuration Python et le workflow doivent correspondre entièrement à cette version.

Relire le diff, exécuter la validation puis ouvrir une pull request. Ne pas déplacer le tag v0.6.0 ; après validation, utiliser v1.0.0 pour TicketAssist. Aucun dépôt distant n’a été modifié automatiquement par cette préparation.

## Différences assumées

- Commande `ticket` et paquet `ticket_agent`, au lieu de `sentiment`/`sentiment_app`.
- Quatre catégories IT au lieu de sentiment positif/négatif.
- Toutes les routes métier sont privées, sans ancienne route publique de prédiction.
- SQLite et validation admin obligatoires ; aucune résolution technique autonome.
