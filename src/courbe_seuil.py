"""Courbe d'abstention calculée sur validation uniquement, pas sur test."""
import csv
import json
from pathlib import Path

from ticket_agent.config import Settings
from ticket_agent.corpus import lire
from ticket_agent.evaluation import evaluer
from ticket_agent.model import Classifier


def main() -> int:
    config = Settings.from_env()
    rows = lire(Path("data/validation.csv"))
    results = []
    for seuil in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90]:
        r = evaluer(Classifier(config.model_path, seuil), rows)
        results.append({key: r[key] for key in ["threshold", "couverture", "accuracy_acceptee", "abstentions"]})
    path = Path("models/courbe_seuil.csv")
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
