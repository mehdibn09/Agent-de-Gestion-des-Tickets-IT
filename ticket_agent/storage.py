"""Persistance SQLite, transitions explicites et concurrence optimiste."""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ticket_agent.rules import CATEGORIES, EQUIPES

STATUTS = ("A_VALIDER", "NOUVEAU", "EN_COURS", "RESOLU")


class Introuvable(Exception):
    pass


class Conflit(Exception):
    pass


class TransitionInvalide(Exception):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, statut TEXT NOT NULL,
                    version INTEGER NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT NOT NULL REFERENCES tickets(id),
                    at TEXT NOT NULL, action TEXT NOT NULL,
                    role TEXT NOT NULL, details TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_ticket ON events(ticket_id);
            """)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def maintenant() -> str:
        return datetime.now(timezone.utc).isoformat()

    def creer(self, entree: dict[str, Any], analyse: dict[str, Any], role: str) -> dict[str, Any]:
        identifiant, at = uuid.uuid4().hex, self.maintenant()
        payload = {**entree, "analyse": analyse, "categorie_validee": None,
                   "equipe_validee": None, "resolution": None}
        with self.connection() as db:
            db.execute("INSERT INTO tickets VALUES (?,?,?,?,?,?)",
                       (identifiant, at, at, "A_VALIDER", 0, json.dumps(payload, ensure_ascii=False)))
            db.execute("INSERT INTO events(ticket_id,at,action,role,details) VALUES(?,?,?,?,?)",
                       (identifiant, at, "creation", role, json.dumps({"statut": "A_VALIDER"})))
        return self.obtenir(identifiant)

    @staticmethod
    def serialiser(row: sqlite3.Row) -> dict[str, Any]:
        return {key: row[key] for key in ("id", "created_at", "updated_at", "statut", "version")} | json.loads(row["payload"])

    def obtenir(self, identifiant: str) -> dict[str, Any]:
        with self.connection() as db:
            row = db.execute("SELECT * FROM tickets WHERE id=?", (identifiant,)).fetchone()
            if row is None:
                raise Introuvable("Ticket introuvable")
            ticket = self.serialiser(row)
            ticket["historique"] = [dict(e) for e in db.execute(
                "SELECT at,action,role,details FROM events WHERE ticket_id=? ORDER BY event_id", (identifiant,))]
        for event in ticket["historique"]:
            event["details"] = json.loads(event["details"])
        return ticket

    def lister(self, statut: str | None = None, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        if statut is not None and statut not in STATUTS:
            raise ValueError("Statut inconnu")
        if not 1 <= limit <= 100 or offset < 0:
            raise ValueError("Pagination invalide")
        clause, params = (" WHERE statut=?", [statut]) if statut else ("", [])
        with self.connection() as db:
            total = db.execute("SELECT COUNT(*) FROM tickets" + clause, params).fetchone()[0]
            rows = db.execute("SELECT * FROM tickets" + clause + " ORDER BY created_at DESC, id LIMIT ? OFFSET ?",
                              [*params, limit, offset]).fetchall()
        return {"items": [self.serialiser(r) for r in rows], "total": total, "limit": limit, "offset": offset}

    def modifier(self, identifiant: str, action: str, version: int,
                 categorie: str | None = None, resolution: str | None = None) -> dict[str, Any]:
        with self.connection() as db:
            # Verrou d'écriture : lecture et mise à jour appartiennent à la même transaction.
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM tickets WHERE id=?", (identifiant,)).fetchone()
            if row is None:
                raise Introuvable("Ticket introuvable")
            if row["version"] != version:
                raise Conflit("Version dépassée : recharger le ticket")
            payload = json.loads(row["payload"])
            transitions = {("A_VALIDER", "valider"): "NOUVEAU", ("NOUVEAU", "demarrer"): "EN_COURS",
                           ("EN_COURS", "resoudre"): "RESOLU", ("RESOLU", "reouvrir"): "EN_COURS"}
            cible = transitions.get((row["statut"], action))
            if cible is None:
                raise TransitionInvalide("Transition interdite")
            if action == "valider":
                if categorie not in CATEGORIES:
                    raise TransitionInvalide("Catégorie explicite requise pour valider")
                payload["categorie_validee"] = categorie
                payload["equipe_validee"] = EQUIPES[categorie]
            elif categorie is not None:
                raise TransitionInvalide("La catégorie se définit pendant la validation")
            if action == "resoudre":
                if not resolution or not resolution.strip():
                    raise TransitionInvalide("Compte rendu de résolution requis")
                payload["resolution"] = resolution.strip()
            elif resolution is not None:
                raise TransitionInvalide("La résolution se renseigne à la clôture")
            at = self.maintenant()
            db.execute("UPDATE tickets SET statut=?,version=version+1,updated_at=?,payload=? WHERE id=? AND version=?",
                       (cible, at, json.dumps(payload, ensure_ascii=False), identifiant, version))
            details = {"de": row["statut"], "vers": cible, "categorie": categorie, "version": version + 1}
            if action == "resoudre":
                details["resolution"] = payload["resolution"]
            db.execute("INSERT INTO events(ticket_id,at,action,role,details) VALUES(?,?,?,?,?)",
                       (identifiant, at, action, "admin", json.dumps(details, ensure_ascii=False)))
        return self.obtenir(identifiant)
