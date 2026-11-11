from pathlib import Path

import pytest

from ticket_agent.cli import main
from ticket_agent.config import Settings, valeurs_env


def test_configuration_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / ".env"
    path.write_text("# commentaire\n\nignore\nTICKET_THRESHOLD='0.5'\nTICKET_MODEL=local.joblib\nTICKET_API_KEY_CLIENT=local-client\n")
    monkeypatch.setenv("TICKET_API_KEY_CLIENT", "env-client")
    settings = Settings.from_env()
    assert settings.threshold == 0.5 and settings.client_key == "env-client"
    assert settings.model_path == tmp_path / "local.joblib"
    assert valeurs_env(tmp_path / "absent") == {}
    with pytest.raises(ValueError):
        Settings(path, path)
    with pytest.raises(ValueError):
        Settings(path, tmp_path / "db", threshold=0)


def test_config_sans_ecrasement(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["config"]) == 0
    keys = valeurs_env(tmp_path / ".env")
    assert len(keys["TICKET_API_KEY_CLIENT"]) >= 32
    assert keys["TICKET_API_KEY_CLIENT"] != keys["TICKET_API_KEY_ADMIN"]
    original = (tmp_path / ".env").read_bytes()
    assert main(["config"]) == 1
    assert (tmp_path / ".env").read_bytes() == original


def test_cli_reel(model_path, tmp_path, monkeypatch, capsys):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("TICKET_MODEL", str(model_path))
    assert main(["analyze", "Le réseau wifi est inaccessible."]) == 0
    assert "priorite" in capsys.readouterr().out
    assert main(["explain", "Le mot de passe de mon compte est expiré."]) == 0
    assert main(["evaluate", "--test", str(root / "data/test.csv"), "--output", str(tmp_path / "metrics.json")]) == 0
    assert main(["evaluate", "--test", str(root / "data/train.csv")]) == 1
    monkeypatch.setenv("TICKET_MODEL", str(tmp_path / "absent.joblib"))
    assert main(["analyze", "Le wifi ne fonctionne plus."]) == 1


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "1.0.0" in capsys.readouterr().out
