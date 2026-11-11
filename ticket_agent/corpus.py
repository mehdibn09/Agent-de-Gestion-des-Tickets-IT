"""Lecture contrôlée des jeux CSV. Les jeux fournis sont simulés."""
import csv
import hashlib
import re
from pathlib import Path

from ticket_agent.rules import CATEGORIES


def normaliser(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def lire(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not {"id", "titre", "description", "categorie", "famille"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV : colonnes id,titre,description,categorie,famille requises")
        rows = list(reader)
    if not rows:
        raise ValueError("Corpus vide")
    ids: set[str] = set()
    texts: set[str] = set()
    for row in rows:
        if any(not isinstance(v, str) or not v.strip() for v in row.values()):
            raise ValueError("Valeur vide ou ligne CSV mal formée")
        if row["categorie"] not in CATEGORIES:
            raise ValueError("Catégorie inconnue")
        if row["id"] in ids or normaliser(row["description"]) in texts:
            raise ValueError("Doublon d’identifiant ou de description")
        ids.add(row["id"])
        texts.add(normaliser(row["description"]))
    return rows


def verifier_separation(*jeux: list[dict[str, str]]) -> None:
    vus: set[str] = set()
    familles: set[str] = set()
    for jeu in jeux:
        textes = {normaliser(r["description"]) for r in jeu}
        groupes = {r["famille"] for r in jeu}
        if vus & textes or familles & groupes:
            raise ValueError("Fuite entre jeux : texte ou famille de formulation partagés")
        vus |= textes
        familles |= groupes


def empreinte(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
