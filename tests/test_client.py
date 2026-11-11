import httpx
import pytest

from ui.client import ApiError, Client


def test_transport_et_contrats():
    calls = []
    def respond(request):
        calls.append(request)
        return httpx.Response(200, json={"status": "OK"})
    c = Client("http://test", "cle", httpx.MockTransport(respond))
    assert c.health() == {"status": "OK"}
    c.analyze({"titre": "test"})
    c.create({"titre": "test"})
    c.tickets("NOUVEAU", 20)
    c.get("abc")
    c.update("abc", {"action": "demarrer"})
    assert len(calls) == 6 and calls[1].headers["X-API-Key"] == "cle"
    assert calls[3].url.params["offset"] == "20"


@pytest.mark.parametrize("url", ["file:///tmp/a", "ftp://serveur", "http://user:pass@serveur", "invalide"])
def test_url_invalide(url):
    with pytest.raises(ValueError):
        Client(url, "")


@pytest.mark.parametrize("status,body", [(401, {"message": "Clé invalide"}), (500, {}), (200, ["pas un objet"])])
def test_erreurs_http_et_format(status, body):
    c = Client("http://test", "", httpx.MockTransport(lambda request: httpx.Response(status, json=body)))
    with pytest.raises(ApiError):
        c.health()


def test_json_illisible_et_transport():
    c = Client("http://test", "", httpx.MockTransport(lambda request: httpx.Response(200, text="html")))
    with pytest.raises(ApiError):
        c.health()
    def fail(request):
        raise httpx.ConnectError("secret interne")
    c = Client("http://test", "", httpx.MockTransport(fail))
    with pytest.raises(ApiError) as exc:
        c.health()
    assert "secret" not in str(exc.value)
