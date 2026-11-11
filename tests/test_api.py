from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from api.main import create_app


def test_health_public(api):
    assert api.get("/").json()["application"] == "TicketAssist"
    assert api.get("/health").status_code == 200
    assert api.get("/v1/health").status_code == 200
    paths = api.get("/openapi.json").json()["paths"]
    assert "security" in paths["/v1/tickets"]["post"]
    assert api.post("/predict", json={"text": "Un texte"}).status_code == 404


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "mauvaise-cle"}])
@pytest.mark.parametrize("route,method", [("/v1/tickets", "get"), ("/v1/tickets", "post"), ("/v1/tickets/analyze", "post"), ("/v1/tickets/absent", "get")])
def test_toutes_routes_metier_authentifiees(api, headers, route, method, payload):
    response = api.request(method, route, headers=headers, json=payload if method == "post" else None)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "ApiKey"


def test_analyse_sans_persistance(api, auth, payload):
    r = api.post("/v1/tickets/analyze", headers=auth, json=payload)
    assert r.status_code == 200 and r.json()["priorite"] == "P4"
    assert api.get("/v1/tickets", headers=auth).json()["total"] == 0


def test_cycle_api_et_roles(api, auth, admin, payload):
    response = api.post("/v1/tickets", headers=auth, json=payload)
    assert response.status_code == 201
    t = response.json()
    assert t["statut"] == "A_VALIDER" and t["version"] == 0
    route = f"/v1/tickets/{t['id']}"
    assert api.patch(route, headers=auth, json={"action": "valider", "version": 0, "categorie": "reseau"}).status_code == 403
    assert api.patch(route, headers=admin, json={"action": "valider", "version": 0}).status_code == 422
    r = api.patch(route, headers=admin, json={"action": "valider", "version": 0, "categorie": "reseau"})
    assert r.json()["statut"] == "NOUVEAU"
    assert api.patch(route, headers=admin, json={"action": "demarrer", "version": 0}).status_code == 409
    assert api.patch(route, headers=admin, json={"action": "demarrer", "version": 1}).status_code == 200
    assert api.patch(route, headers=admin, json={"action": "resoudre", "version": 2, "resolution": "Réseau rétabli, contrôle effectué"}).json()["statut"] == "RESOLU"
    assert len(api.get(route, headers=auth).json()["historique"]) == 4
    assert api.get("/v1/tickets?statut=RESOLU", headers=auth).json()["total"] == 1


@pytest.mark.parametrize("champ,valeur", [("titre", ""), ("titre", "   "), ("titre", " a "), ("description", " a        "), ("titre", "x" * 161),
    ("description", ""), ("description", " " * 15), ("description", "x" * 2001),
    ("description", 42), ("impact", "autre"), ("urgence", "immédiate"), ("admin", True)])
def test_validation(api, auth, payload, champ, valeur):
    payload[champ] = valeur
    r = api.post("/v1/tickets", headers=auth, json=payload)
    assert r.status_code == 422 and set(r.json()) == {"code", "message"}
    assert api.get("/v1/tickets", headers=auth).json()["total"] == 0


def test_pagination_et_erreurs(api, auth, admin):
    assert api.get("/v1/tickets/absent", headers=auth).status_code == 404
    assert api.patch("/v1/tickets/absent", headers=admin, json={"action": "valider", "version": 0, "categorie": "acces"}).status_code == 404
    for query in ["limit=101", "limit=0", "offset=-1", "statut=AUTRE"]:
        assert api.get("/v1/tickets?" + query, headers=auth).status_code == 422
    assert api.post("/v1/tickets", headers={**auth, "Content-Type": "application/json"}, content="{").status_code == 422


def test_modele_absent(settings, tmp_path, auth, payload):
    with TestClient(create_app(replace(settings, model_path=tmp_path / "absent.joblib"))) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/v1/tickets/analyze", headers=auth, json=payload).status_code == 503
        assert client.get("/v1/tickets", headers=auth).status_code == 200


@pytest.mark.parametrize("client_key,admin_key", [("", ""), ("court", "admin-long-1234567890"), ("identique-1234567890", "identique-1234567890")])
def test_cles_mal_configurees(settings, client_key, admin_key, payload):
    with TestClient(create_app(replace(settings, client_key=client_key, admin_key=admin_key))) as client:
        r = client.post("/v1/tickets", headers={"X-API-Key": "test"}, json=payload)
        assert r.status_code == 503


def test_erreur_interne_masquee(api, auth, payload, monkeypatch):
    def fail(**kwargs):
        raise RuntimeError("NE_PAS_DIVULGUER")
    monkeypatch.setattr(api.app.state.agent, "analyser", fail)
    # Starlette renvoie 500 puis relance l'exception pour les clients de test.
    api.raise_server_exceptions = False
    with TestClient(api.app, raise_server_exceptions=False) as other:
        monkeypatch.setattr(other.app.state.agent, "analyser", fail)
        r = other.post("/v1/tickets/analyze", headers=auth, json=payload)
        assert r.status_code == 500 and "NE_PAS_DIVULGUER" not in r.text


def test_modele_corrompu(settings, tmp_path):
    path = tmp_path / "corrompu.joblib"
    path.write_bytes(b"incompatible")
    with TestClient(create_app(replace(settings, model_path=path))) as client:
        assert client.get("/health").status_code == 503
