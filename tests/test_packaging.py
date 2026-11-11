import ast
import tomllib
from pathlib import Path

from ticket_agent import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_metadata_et_frontieres():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert config["project"]["version"] == __version__
    assert config["project"]["scripts"]["ticket"] == "ticket_agent.cli:main"
    assert set(config["tool"]["setuptools"]["packages"]) == {"ticket_agent", "api", "ui"}
    for file in (ROOT / "ui").glob("*.py"):
        tree = ast.parse(file.read_text())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        assert not any(n.startswith(("joblib", "sqlite3", "ticket_agent.model", "ticket_agent.storage")) for n in imports)
