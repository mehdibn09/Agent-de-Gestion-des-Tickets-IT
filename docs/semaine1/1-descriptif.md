## Livrable 1 — Descriptif du projet mis à jour

**Rédacteur responsable : Mehdi Benjelloun** · Relecteur : Oussama Kamil · Relecture à formaliser dans la PR.

### 1.1 Contexte et problème

Un service support reçoit des demandes en texte libre. Le technicien doit les lire, déterminer leur catégorie et leur priorité, choisir l’équipe puis assurer leur suivi. TicketAssist vise à structurer ce premier traitement et à en conserver la traçabilité. Le scénario est pédagogique ; aucun déploiement réel à l’EMSI ou dans une entreprise n’est revendiqué.

### 1.2 Objectif

**Automatiser le tri et l’orientation des demandes IT : lire les tickets, proposer leur catégorie, priorité et équipe, préparer une réponse initiale, puis assurer création et escalade avec contrôle humain.**

### 1.3 Utilisateurs et scénario principal

Le **demandeur**, avec une clé client, crée et consulte les demandes. L’**opérateur**, avec une clé admin, confirme la catégorie et pilote les statuts. Le démonstrateur utilise des rôles partagés, sans isolation par demandeur.

1. Saisir un titre, une description, l’impact et l’urgence dans Streamlit.
2. Consulter la catégorie, le score, la priorité, l’équipe et la réponse initiale proposés.
3. Enregistrer le ticket au statut `A_VALIDER`.
4. L’opérateur confirme ou corrige explicitement la catégorie, puis démarre le traitement.
5. Renseigner un compte rendu pour résoudre ; rouvrir si nécessaire, en conservant l’historique.

### 1.4 Fonctionnalités du MVP — binôme

| ID | Fonctionnalité | Résultat utilisateur et critère observable | Priorité |
| --- | --- | --- | --- |
| F1 | Qualification et orientation | Catégorie parmi quatre classes, score, priorité selon une matrice à neuf combinaisons et équipe proposée | Indispensable |
| F2 | Assistance à la validation | Réponse initiale contrôlée, abstention signalée, escalade P1 et confirmation réservée à l’admin | Indispensable |
| F3 | Gestion du cycle de vie | Identifiant, liste paginée, filtre, détail, compte rendu et historique ; conflit détecté si version dépassée | Indispensable |

Les catégories sont `acces`, `logiciel`, `materiel`, `reseau`. Le seuil initial d’abstention est **0,45** ; un texte entièrement hors vocabulaire est également refusé. La priorité dépend exclusivement de l’impact et de l’urgence : individuel → P4/P4/P3 ; équipe → P4/P3/P2 ; organisation → P3/P2/P1, pour les urgences faible/normale/critique. P1 est la priorité maximale. Cette matrice pédagogique doit être approuvée pour tout usage métier.

### 1.5 Services et composants techniques

| Composant | Rôle | Technologie retenue | Justification |
| --- | --- | --- | --- |
| Modèle ML | F1 : classer les descriptions | TF-IDF + régression logistique scikit-learn | Modèle léger, explicable et exécutable hors ligne |
| Mémoire métier | F3 : tickets et événements | SQLite, transactions et requêtes paramétrées | Persistance simple ; contrôle de version pour les écritures concurrentes |
| Outils de l’agent | F1–F3 : qualifier, prioriser, proposer et enregistrer | Modules Python de `ticket_agent/` | Logique indépendante de HTTP, fonctions directement testables |
| API et contrats | F1–F3 : exposer les services | FastAPI, Pydantic, routes `/v1/tickets` | Validation des entrées, documentation OpenAPI, erreurs explicites |
| Interface | F1–F3 : saisie, revue et suivi | Streamlit, client HTTP | Parcours simple ; aucun accès direct au modèle ou à SQLite |
| Contrôle d’accès | F2/F3 : séparer client et admin | En-tête `X-API-Key` | Toutes les routes métier sont protégées ; la santé reste publique |
| Exécution et qualité | Ensemble du MVP | Paquet installable, Docker, GitHub Actions, pytest/Ruff/mypy | Environnement reconstructible et contrôles automatisés ; Docker/CI distante à confirmer |

Un **orchestrateur unique** coordonne ces modules. Le projet ne revendique ni plusieurs agents autonomes ni une génération par LLM. Le choix de classification et de règles répond à la fiche de l’encadrant ; aucun RAG n’est imposé par celle-ci.

### 1.6 Hors périmètre

Résolution technique autonome, commandes exécutées sur des postes, réinitialisation de mots de passe, connecteurs GLPI/ServiceNow, comptes individuels, SLA contractuels, RAG et déploiement de production multi-organisations. La résolution est déclarée par l’opérateur ; elle n’est pas vérifiée automatiquement sur les équipements.

### 1.7 Alignement sur la fiche officielle du projet n° 10

L’encadrant définit le projet **« Agent de gestion des tickets IT »**, catégorie **Support et ITSM**, niveau **Intermédiaire**, avec l’objectif **« Automatiser le tri et l’orientation des demandes »**. La mention « Sujet professionnel recommandé : Non » est conservée comme attribut du catalogue ; elle ne change pas les exigences de qualité du livrable.

| Fonctionnalité du catalogue | Couverture dans TicketAssist | Regroupement MVP |
| --- | --- | --- |
| Lit les tickets | Reçoit le titre, la description, l’impact et l’urgence via formulaire/API | F1 |
| Les classe automatiquement | Modèle ML à quatre catégories ; score et abstention si nécessaire | F1 |
| Identifie leur priorité | Matrice déterministe impact × urgence ; priorité indépendante du sentiment | F1 |
| Les assigne à la bonne équipe | Propose une équipe puis enregistre l’équipe confirmée lors de la validation admin | F1/F2 |
| Génère une réponse initiale | Gabarit contrôlé demandant les précisions utiles ; affichage à l’opérateur, sans envoi d’e-mail | F2 |
| Crée un ticket si nécessaire | Action explicite de création via API, identifiant SQLite et statut A_VALIDER | F3 |
| Escalade les cas complexes | Signale les faibles confiances, le hors-vocabulaire et P1 ; orientation Support N1 en cas d’abstention | F2/F3 |

**Adaptations de périmètre.** L’outil de tickets du MVP est interne : API et SQLite. Aucun connecteur externe GLPI/ServiceNow n’est fourni. Le titre et la description sont lus automatiquement ; l’impact et l’urgence sont déclarés par le demandeur, pas extraits automatiquement du texte. L’escalade correspond à un signal et à une revue humaine, sans transfert automatique vers une plateforme tierce. Ces choix rendent le périmètre démontrable en quatre semaines ; leur acceptation doit être confirmée avec l’encadrant. La classification, les champs structurés et l’intégration à l’outil local couvrent les points techniques retenus, sans revendiquer une intégration ITSM externe déjà réalisée.

**Contrôle de préparation :** besoin, trois fonctions, composants et exclusions définis. **Validation attendue :** approbation du périmètre et de la matrice par le relecteur puis l’enseignant.
