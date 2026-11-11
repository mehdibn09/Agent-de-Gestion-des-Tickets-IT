"""Entraînement reproductible et classification avec abstention."""
import hashlib
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ticket_agent.corpus import empreinte, lire, normaliser, verifier_separation
from ticket_agent.rules import CATEGORIES


def entrainer(train: Path, validation: Path, destination: Path) -> dict[str, Any]:
    apprendre, valider = lire(train), lire(validation)
    verifier_separation(apprendre, valider)
    if set(r["categorie"] for r in apprendre) != set(CATEGORIES):
        raise ValueError("L’entraînement doit couvrir les quatre catégories")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, strip_accents="unicode")),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", C=4, random_state=42)),
    ])
    pipeline.fit([r["description"] for r in apprendre], [r["categorie"] for r in apprendre])
    metadata = {"format": 1, "source": "CSV utilisateur ; voir data/README.md pour la provenance",
                "n_train": len(apprendre), "n_validation": len(valider),
                "train_sha256": empreinte(train), "validation_sha256": empreinte(validation),
                "classes": list(CATEGORIES),
                "reference_familles": sorted({r["famille"] for r in apprendre + valider}),
                "reference_text_hashes": sorted({hashlib.sha256(normaliser(r["description"]).encode()).hexdigest() for r in apprendre + valider})}
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "metadata": metadata}, destination)
    return metadata


class Classifier:
    def __init__(self, path: Path, threshold: float = 0.45):
        if not 0.25 <= threshold <= 1:
            raise ValueError("Seuil invalide")
        if not path.is_file():
            raise FileNotFoundError("Modèle absent : lancer ticket train")
        # Ne charger que des artefacts de confiance : pickle/joblib peut exécuter du code.
        bundle = joblib.load(path)
        if not isinstance(bundle, dict) or bundle.get("metadata", {}).get("format") != 1:
            raise ValueError("Format de modèle incompatible")
        self.pipeline = bundle["pipeline"]
        self.metadata = bundle["metadata"]
        if set(self.pipeline.classes_) != set(CATEGORIES):
            raise ValueError("Classes du modèle incompatibles")
        self.threshold = threshold

    def predire(self, texte: str) -> dict[str, Any]:
        if not isinstance(texte, str) or not texte.strip() or len(texte) > 2200:
            raise ValueError("Texte non blanc de 1 à 2200 caractères attendu")
        vect = self.pipeline.named_steps["tfidf"].transform([texte])
        probabilities = self.pipeline.predict_proba([texte])[0]
        index = int(np.argmax(probabilities))
        score = float(probabilities[index])
        candidate = str(self.pipeline.classes_[index])
        refuse = vect.nnz == 0 or score < self.threshold
        return {"categorie": None if refuse else candidate,
                "categorie_proposee": candidate, "confiance": round(score, 6),
                "a_verifier": refuse,
                "motif": "hors_vocabulaire" if vect.nnz == 0 else ("confiance_insuffisante" if refuse else "classification")}

    def expliquer(self, texte: str, n: int = 8) -> dict[str, Any]:
        prediction = self.predire(texte)
        vect = self.pipeline.named_steps["tfidf"]
        clf = self.pipeline.named_steps["clf"]
        row = vect.transform([texte]).toarray()[0]
        index = list(clf.classes_).index(prediction["categorie_proposee"])
        contributions = row * clf.coef_[index]
        termes = vect.get_feature_names_out()
        ordre = sorted(np.flatnonzero(row), key=lambda i: abs(contributions[i]), reverse=True)
        return {"categorie": prediction["categorie_proposee"],
                "base": float(clf.intercept_[index]), "somme_contributions": float(contributions.sum()),
                "logit": float(clf.decision_function(vect.transform([texte]))[0, index]),
                "termes": [{"terme": str(termes[i]), "contribution": float(contributions[i])} for i in ordre[:n]],
                "limite": "Contributions linéaires au logit, sans preuve de causalité ni valeur SHAP."}
