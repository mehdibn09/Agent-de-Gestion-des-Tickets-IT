"""Orchestrateur métier indépendant de HTTP et de l'interface."""
from typing import Any

from ticket_agent.model import Classifier
from ticket_agent.rules import EQUIPES, priorite, reponse_initiale


class Agent:
    def __init__(self, classifier: Classifier):
        self.classifier = classifier

    def analyser(self, titre: str, description: str, impact: str, urgence: str) -> dict[str, Any]:
        if not titre.strip() or not description.strip():
            raise ValueError("Titre et description requis")
        # L'entraînement porte sur les descriptions ; le titre reste un champ de suivi.
        prediction = self.classifier.predire(description)
        niveau = priorite(impact, urgence)
        category = prediction["categorie"]
        motifs = []
        if prediction["a_verifier"]:
            motifs.append(prediction["motif"])
        if niveau == "P1":
            motifs.append("criticite_P1")
        return {**prediction, "priorite": niveau,
                "equipe": EQUIPES.get(category, "Support N1"),
                "reponse_initiale": reponse_initiale(category),
                "escalade": bool(motifs), "motifs_escalade": motifs,
                "validation_humaine_requise": True}
