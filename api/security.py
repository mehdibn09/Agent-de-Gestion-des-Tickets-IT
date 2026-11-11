"""Authentification par clé, sans accès de secours public aux tickets."""
import secrets
from typing import Annotated

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from ticket_agent.config import Settings

HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def authentifier(request: Request, key: Annotated[str | None, Security(HEADER)] = None) -> str:
    if not key:
        raise HTTPException(401, "Clé API requise", headers={"WWW-Authenticate": "ApiKey"})
    settings: Settings = request.app.state.settings
    keys = {"client": settings.client_key, "admin": settings.admin_key}
    if any(len(v) < 16 for v in keys.values()) or settings.client_key == settings.admin_key:
        raise HTTPException(503, "Configurer deux clés API distinctes de 16 caractères minimum")
    result = None
    for role, expected in keys.items():
        if secrets.compare_digest(key.encode(), expected.encode()):
            result = role
    if result is None:
        raise HTTPException(401, "Clé API invalide", headers={"WWW-Authenticate": "ApiKey"})
    return result


def administrateur(role: Annotated[str, Security(authentifier)]) -> str:
    if role != "admin":
        raise HTTPException(403, "Rôle administrateur requis")
    return role
