from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from ticket_agent.config import Settings
from ticket_agent.model import Classifier, entrainer

ROOT = Path(__file__).resolve().parents[1]
CLIENT = "client-test-1234567890"
ADMIN = "admin-test-12345678901"


@pytest.fixture(scope="session")
def model_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("model") / "tickets.joblib"
    entrainer(ROOT / "data/train.csv", ROOT / "data/validation.csv", path)
    return path


@pytest.fixture
def classifier(model_path):
    return Classifier(model_path)


@pytest.fixture
def settings(model_path, tmp_path):
    return Settings(model_path, tmp_path / "tickets.sqlite3", CLIENT, ADMIN)


@pytest.fixture
def api(settings):
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def payload():
    return {"titre": "Connexion Wi-Fi", "description": "La connexion wifi est inaccessible depuis mon poste.",
            "impact": "individuel", "urgence": "normale"}


@pytest.fixture
def auth():
    return {"X-API-Key": CLIENT}


@pytest.fixture
def admin():
    return {"X-API-Key": ADMIN}
