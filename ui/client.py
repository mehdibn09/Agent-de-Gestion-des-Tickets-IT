"""Client HTTP unique, sans lecture du modèle ni de la base."""
from typing import Any
from urllib.parse import urlparse

import httpx


class ApiError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class Client:
    def __init__(self, url: str, key: str, transport: httpx.BaseTransport | None = None):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("URL HTTP(S) de l’API invalide")
        self.url, self.key, self.transport = url.rstrip("/"), key, transport

    def request(self, method: str, route: str, payload: dict[str, Any] | None = None,
                params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            with httpx.Client(base_url=self.url, timeout=15, transport=self.transport, trust_env=False) as session:
                response = session.request(method, route, json=payload, params=params,
                                           headers={"X-API-Key": self.key} if self.key else {})
        except httpx.TransportError:
            raise ApiError("API injoignable ou délai dépassé. Vérifier ticket serve.") from None
        try:
            body = response.json()
        except ValueError:
            raise ApiError("Réponse de l’API illisible", response.status_code) from None
        if response.status_code >= 400:
            raise ApiError(body.get("message", "Erreur API") if isinstance(body, dict) else "Erreur API", response.status_code)
        if not isinstance(body, dict):
            raise ApiError("Réponse JSON objet attendue", response.status_code)
        return body

    def health(self):
        return self.request("GET", "/health")

    def analyze(self, payload: dict[str, Any]):
        return self.request("POST", "/v1/tickets/analyze", payload)

    def create(self, payload: dict[str, Any]):
        return self.request("POST", "/v1/tickets", payload)

    def tickets(self, statut: str | None = None, offset: int = 0):
        params: dict[str, Any] = {"limit": 20, "offset": offset}
        if statut:
            params["statut"] = statut
        return self.request("GET", "/v1/tickets", params=params)

    def get(self, identifiant: str):
        return self.request("GET", f"/v1/tickets/{identifiant}")

    def update(self, identifiant: str, payload: dict[str, Any]):
        return self.request("PATCH", f"/v1/tickets/{identifiant}", payload)
