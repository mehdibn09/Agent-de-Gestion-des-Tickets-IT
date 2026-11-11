"""Commande installable ticket : préparation, analyse, API et interface."""
import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

from ticket_agent import __version__
from ticket_agent.config import Settings


def _config(args: argparse.Namespace) -> int:
    path = Path(".env")
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(f"TICKET_API_KEY_CLIENT={secrets.token_urlsafe(32)}\nTICKET_API_KEY_ADMIN={secrets.token_urlsafe(32)}\n")
        if os.name != "nt":
            path.chmod(0o600)
    except FileExistsError:
        print(".env existe déjà : conservé. Compléter ses deux clés manuellement.", file=sys.stderr)
        return 1
    print("Deux clés aléatoires créées dans .env ; utiliser la clé CLIENT dans l’interface.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ticket", description="TicketAssist : agent de gestion des tickets IT")
    parser.add_argument("--version", action="version", version=f"ticket-assist {__version__}")
    commands = parser.add_subparsers(dest="commande", required=True)
    commands.add_parser("config", help="crée .env avec des clés aléatoires, sans écraser")
    train = commands.add_parser("train", help="entraîne sur les CSV locaux")
    train.add_argument("--train", type=Path, default=Path("data/train.csv"))
    train.add_argument("--validation", type=Path, default=Path("data/validation.csv"))
    evaluate = commands.add_parser("evaluate", help="mesure le jeu de test gelé")
    evaluate.add_argument("--test", type=Path, default=Path("data/test.csv"))
    evaluate.add_argument("--output", type=Path, default=Path("models/metrics.json"))
    analyze = commands.add_parser("analyze", help="analyse locale, sans HTTP ni enregistrement")
    analyze.add_argument("texte")
    analyze.add_argument("--impact", default="individuel", choices=["individuel", "equipe", "organisation"])
    analyze.add_argument("--urgence", default="normale", choices=["faible", "normale", "critique"])
    explain = commands.add_parser("explain", help="contributions linéaires du modèle")
    explain.add_argument("texte")
    serve = commands.add_parser("serve", help="lance FastAPI")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    commands.add_parser("ui", help="lance Streamlit (API séparée)")
    args = parser.parse_args(argv)
    try:
        settings = Settings.from_env()
        if args.commande == "config":
            return _config(args)
        if args.commande == "serve":
            import uvicorn
            uvicorn.run("api.main:app", host=args.host, port=args.port)
            return 0
        if args.commande == "ui":
            import importlib.util
            if importlib.util.find_spec("streamlit") is None:
                print('Installer : pip install "ticket-assist[ui]"', file=sys.stderr)
                return 1
            page = Path(__file__).resolve().parents[1] / "ui" / "app.py"
            return subprocess.call([sys.executable, "-m", "streamlit", "run", str(page)])
        from ticket_agent.model import Classifier, entrainer
        if args.commande == "train":
            result = entrainer(args.train, args.validation, settings.model_path)
        elif args.commande == "evaluate":
            from ticket_agent.corpus import empreinte, lire, normaliser
            from ticket_agent.evaluation import evaluer
            rows = lire(args.test)
            clf = Classifier(settings.model_path, settings.threshold)
            if empreinte(args.test) in (clf.metadata["train_sha256"], clf.metadata["validation_sha256"]):
                raise ValueError("Le test doit être distinct de l’entraînement et de la validation")
            if (set(r["famille"] for r in rows) & set(clf.metadata.get("reference_familles", [])) or
                    set(hashlib.sha256(normaliser(r["description"]).encode()).hexdigest() for r in rows) & set(clf.metadata.get("reference_text_hashes", []))):
                raise ValueError("Fuite : le test partage des textes ou familles avec l’apprentissage/validation")
            result = evaluer(clf, rows) | {"test_sha256": empreinte(args.test), "model_metadata": {k: v for k, v in clf.metadata.items() if k not in {"reference_text_hashes", "reference_familles"}}}
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif args.commande == "explain":
            result = Classifier(settings.model_path, settings.threshold).expliquer(args.texte)
        else:
            from ticket_agent.agent import Agent
            result = Agent(Classifier(settings.model_path, settings.threshold)).analyser("Analyse CLI", args.texte, args.impact, args.urgence)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
