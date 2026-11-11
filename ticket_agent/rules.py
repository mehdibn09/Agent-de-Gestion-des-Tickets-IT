"""Règles métier ; la priorité ne dépend ni du sentiment ni du score ML."""
CATEGORIES = ("acces", "logiciel", "materiel", "reseau")
IMPACTS = ("individuel", "equipe", "organisation")
URGENCES = ("faible", "normale", "critique")
EQUIPES = {"acces": "Gestion des accès", "logiciel": "Applications",
           "materiel": "Support poste", "reseau": "Réseaux"}
MATRICE = {
    "individuel": {"faible": "P4", "normale": "P4", "critique": "P3"},
    "equipe": {"faible": "P4", "normale": "P3", "critique": "P2"},
    "organisation": {"faible": "P3", "normale": "P2", "critique": "P1"},
}
MESSAGES = {
    "acces": "Précisez le service concerné et le message d’erreur. Ne transmettez jamais votre mot de passe ni un code de connexion.",
    "logiciel": "Indiquez le nom et la version du logiciel, le message d’erreur et les étapes pour reproduire le problème.",
    "materiel": "Indiquez le type de matériel et les symptômes visibles. N’ouvrez pas le matériel et interrompez son utilisation s’il présente un danger.",
    "reseau": "Précisez si le problème concerne le Wi-Fi, le réseau filaire ou le VPN, et si d’autres postes sont affectés.",
}


def priorite(impact: str, urgence: str) -> str:
    if impact not in IMPACTS or urgence not in URGENCES:
        raise ValueError("Impact ou urgence inconnu")
    return MATRICE[impact][urgence]


def reponse_initiale(categorie: str | None) -> str:
    return MESSAGES.get(categorie or "", "Votre demande nécessite une qualification par le support. Précisez le problème et le service concerné, sans communiquer de secret.")
