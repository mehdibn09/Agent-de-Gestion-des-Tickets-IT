from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ui.client import ApiError, Client

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def page(api, auth, monkeypatch):
    monkeypatch.setenv("TICKET_UI_KEY", auth["X-API-Key"])
    def request(self, method, route, payload=None, params=None):
        response = api.request(method, route, json=payload, params=params, headers={"X-API-Key": self.key})
        body = response.json()
        if response.status_code >= 400:
            raise ApiError(body["message"], response.status_code)
        return body
    monkeypatch.setattr(Client, "request", request)
    return AppTest.from_file(str(ROOT / "ui/app.py"), default_timeout=30)


def champ(collection, label):
    return next(x for x in collection if x.label == label)


def test_page_vide_et_validation_locale(page):
    at = page.run()
    assert not at.exception
    assert any("API prête" in s.value for s in at.success)
    champ(at.button, "Analyser").click().run()
    assert any("au moins" in e.value for e in at.error)


def test_creation_depuis_interface(page, api, auth):
    at = page.run()
    champ(at.text_input, "Titre").set_value("Panne du réseau")
    champ(at.text_area, "Description").set_value("Le réseau wifi ne permet plus la connexion Internet.")
    champ(at.button, "Analyser").click().run()
    assert not at.exception and len(at.metric) == 3
    champ(at.button, "Créer pour validation humaine").click().run()
    assert not at.exception
    assert api.get("/v1/tickets", headers=auth).json()["total"] == 1
    assert any("Ticket créé" in s.value for s in at.success)


def test_revue_admin_depuis_interface(page, api, auth, admin, payload):
    ticket = api.post("/v1/tickets", headers=auth, json=payload).json()
    at = page.run()
    champ(at.text_input, "Clé API").set_value(admin["X-API-Key"])
    champ(at.text_input, "Identifiant du ticket à ouvrir").set_value(ticket["id"])
    champ(at.button, "Ouvrir le ticket").click().run()
    assert not at.exception
    champ(at.selectbox, "Catégorie confirmée pour la validation").set_value("reseau")
    champ(at.button, "Appliquer : valider").click().run()
    assert not at.exception
    result = api.get(f"/v1/tickets/{ticket['id']}", headers=auth).json()
    assert result["statut"] == "NOUVEAU"
