"""Configuration explicite, compatible dépôt et roue installée."""
import os
from dataclasses import dataclass
from pathlib import Path


def valeurs_env(path: Path) -> dict[str, str]:
    """Sous-ensemble .env : NOM=valeur, guillemets simples/doubles, sans interpolation."""
    if not path.is_file():
        return {}
    valeurs = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            valeurs[key.strip()] = value
    return valeurs


@dataclass(frozen=True)
class Settings:
    model_path: Path
    db_path: Path
    client_key: str = ""
    admin_key: str = ""
    threshold: float = 0.45

    def __post_init__(self) -> None:
        if not 0.25 <= self.threshold <= 1.0:
            raise ValueError("TICKET_THRESHOLD doit être compris entre 0.25 et 1")
        if self.db_path == self.model_path:
            raise ValueError("La base et le modèle doivent avoir des chemins différents")

    @classmethod
    def from_env(cls) -> "Settings":
        local = valeurs_env(Path.cwd() / ".env")

        def get(name: str, default: str) -> str:
            return os.environ.get(name, local.get(name, default))

        return cls(
            model_path=Path(get("TICKET_MODEL", "models/tickets.joblib")).expanduser().resolve(),
            db_path=Path(get("TICKET_DB", "var/tickets.sqlite3")).expanduser().resolve(),
            client_key=get("TICKET_API_KEY_CLIENT", ""),
            admin_key=get("TICKET_API_KEY_ADMIN", ""),
            threshold=float(get("TICKET_THRESHOLD", "0.45")),
        )
