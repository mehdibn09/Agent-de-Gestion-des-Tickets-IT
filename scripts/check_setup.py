"""Diagnostic sans réseau et sans affichage des secrets."""
import importlib.util
import sys

from ticket_agent.config import Settings


def main() -> int:
    errors = []
    if sys.version_info[:2] not in [(3, 11), (3, 12)]:
        errors.append("Python 3.11 ou 3.12 requis")
    for module in ["fastapi", "sklearn", "streamlit", "httpx"]:
        if importlib.util.find_spec(module) is None:
            errors.append(f"Module absent : {module}")
    config = Settings.from_env()
    if not config.model_path.exists():
        errors.append("Modèle absent : ticket train")
    if len(config.client_key) < 16 or len(config.admin_key) < 16 or config.client_key == config.admin_key:
        errors.append("Clés API absentes, trop courtes ou identiques : ticket config")
    for error in errors:
        print(error)
    print(f"Diagnostic : {len(errors)} erreur(s)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
