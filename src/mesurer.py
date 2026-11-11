"""Évaluation hors domaine, diagnostic des erreurs et empreinte du modèle."""
import csv
import hashlib
import json
from pathlib import Path

from ticket_agent.config import Settings
from ticket_agent.corpus import lire
from ticket_agent.model import Classifier


def main() -> int:
    settings = Settings.from_env()
    clf = Classifier(settings.model_path, settings.threshold)
    with Path("data/hors_domaine.csv").open(encoding="utf-8", newline="") as f:
        ood = list(csv.DictReader(f))
    predits = [clf.predire(r["description"]) for r in ood]
    erreurs = []
    for row in lire(Path("data/test.csv")):
        result = clf.predire(row["description"])
        if result["categorie_proposee"] != row["categorie"] or result["a_verifier"]:
            erreurs.append({"id": row["id"], "description": row["description"], "attendu": row["categorie"], **result})
    result = {"ood_n": len(ood), "ood_refus": sum(r["a_verifier"] for r in predits),
              "ood_taux_refus": sum(r["a_verifier"] for r in predits) / len(ood),
              "ood_details": [{**row, **r} for row, r in zip(ood, predits, strict=True)],
              "erreurs_ou_abstentions_test": erreurs,
              "model_sha256": hashlib.sha256(settings.model_path.read_bytes()).hexdigest(),
              "limite": "12 demandes hors domaine simulées, pas une garantie d'évitement de tous les hors domaine"}
    path = Path("models/diagnostic.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
