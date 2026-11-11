"""Mesures réelles, sans confondre prototype simulé et performance métier."""
from typing import Any

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from ticket_agent.corpus import normaliser
from ticket_agent.model import Classifier
from ticket_agent.rules import CATEGORIES


def evaluer(classifier: Classifier, rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Jeu de test vide")
    expected = [r["categorie"] for r in rows]
    results = [classifier.predire(r["description"]) for r in rows]
    predicted = [r["categorie_proposee"] for r in results]
    accepted = [i for i, r in enumerate(results) if not r["a_verifier"]]
    groupes = {}
    for groupe in ("court", "long"):
        indices = [i for i, row in enumerate(rows) if (len(normaliser(row["description"]).split()) <= 9) == (groupe == "court")]
        groupes[groupe] = {"n": len(indices), "accuracy": sum(expected[i] == predicted[i] for i in indices) / len(indices) if indices else None}
    return {"n_test": len(rows), "threshold": classifier.threshold,
            "accuracy_brute": float(accuracy_score(expected, predicted)),
            "f1_macro_brut": float(f1_score(expected, predicted, labels=list(CATEGORIES), average="macro", zero_division=0)),
            "couverture": len(accepted) / len(rows), "abstentions": len(rows) - len(accepted),
            "accuracy_acceptee": sum(expected[i] == predicted[i] for i in accepted) / len(accepted) if accepted else None,
            "classes": list(CATEGORIES), "matrice_confusion": confusion_matrix(expected, predicted, labels=list(CATEGORIES)).tolist(),
            "par_classe": classification_report(expected, predicted, labels=list(CATEGORIES), output_dict=True, zero_division=0),
            "par_longueur": groupes,
            "limite": "Corpus de démonstration simulé ; aucune performance sur tickets réels n’est établie."}
