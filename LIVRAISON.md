# Livraison TicketAssist 1.0.0

## Fichiers du dépôt

Cette archive contient un projet autonome. Le dossier avec `pyproject.toml`, `README.md`, `ticket_agent`, `api`, `ui`, `tests`, `data`, `docs`, `scripts` et `.github` forme la racine du dépôt. Ne pas mélanger ses tests avec ceux de l’ancienne application Sentiment-app ; lire MIGRATION.md.

Le ZIP exclut `.venv`, `.env`, le modèle binaire, la base SQLite, les caches et les distributions. Le modèle est reconstruit avec `ticket train`. Les métriques JSON/CSV sont incluses pour rendre l’évaluation vérifiable.

## Démarrage Windows

Installer Python 3.11 ou 3.12, extraire le projet puis ouvrir CMD à sa racine.

```cmd
scripts\setup.bat
scripts\lancer_web.bat
```

Le setup installe les dépendances depuis Internet ; une connexion est nécessaire à cette étape. L’entraînement et l’utilisation n’exigent ensuite aucun téléchargement de données ni appel à un LLM. Les clés sont générées localement dans `.env` et jamais intégrées au code.

## Vérification manuelle

Créer un ticket « Connexion Wi-Fi » décrivant une panne réseau. Constater A_VALIDER. Copier l’identifiant dans l’onglet de suivi. Avec la clé admin dans la barre latérale, confirmer la catégorie reseau, démarrer le ticket puis résoudre avec un compte rendu. Recharger l’API : le ticket et les événements doivent rester dans SQLite.

## Dépannage

| Symptôme | Action |
| --- | --- |
| Python 3.11 absent | Installer 3.11/3.12 ou utiliser la variante disponible |
| `pyproject.toml` introuvable | Se placer dans le dossier extrait contenant ce fichier |
| `ticket` introuvable | Activer .venv ; utiliser `python -m ticket_agent` à la place |
| Modèle indisponible / 503 | Lancer `ticket train`, vérifier TICKET_MODEL puis redémarrer API |
| Clé absente / 401 | Renseigner la clé client générée localement ; ne pas utiliser l’exemple vide |
| Configuration clés / 503 | Clés distinctes, 16 caractères minimum ; variables d’environnement prioritaires |
| Rôle insuffisant / 403 | Les validations et transitions demandent la clé admin |
| Conflit / 409 | Rouvrir le ticket pour récupérer sa version courante |
| `.env` existe déjà | Le conserver et renseigner les deux variables TICKET_API_KEY_* sans copier une vraie clé sur GitHub |
| Port déjà utilisé | Arrêter l’ancien service ou `ticket serve --port 8001`, puis modifier l’URL de l’API dans l’interface |
| Message API indisponible au premier affichage | Attendre son chargement puis actualiser l’interface |
| Résultats après nouvel entraînement inchangés | Redémarrer l’API : le modèle est chargé une fois par processus |

## Sauvegarde

Conserver le fichier SQLite `var/tickets.sqlite3` et son historique hors Git. Pour une copie cohérente pendant l’exécution, utiliser l’API backup de SQLite ou arrêter le service avant de copier le fichier. Ne pas sauvegarder uniquement un fichier partiel pendant une écriture.

## Limites de validation

Les tests locaux et le contrôle des distributions sont documentés dans docs/validation-locale.txt. Windows, Docker et la CI distante ne sont pas déclarés exécutés depuis cet environnement. « Projet complet » désigne le périmètre pédagogique documenté, pas une garantie d’absence de défaut dans tous les environnements.
