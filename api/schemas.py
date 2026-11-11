"""Contrats HTTP versionnés."""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Categorie = Literal["acces", "logiciel", "materiel", "reseau"]
Statut = Literal["A_VALIDER", "NOUVEAU", "EN_COURS", "RESOLU"]


class TicketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titre: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=2000)
    impact: Literal["individuel", "equipe", "organisation"] = "individuel"
    urgence: Literal["faible", "normale", "critique"] = "normale"

    @field_validator("titre", "description", mode="before")
    @classmethod
    def non_blanc(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Texte vide")
        return value.strip()


class Analyse(BaseModel):
    categorie: Categorie | None
    categorie_proposee: Categorie
    confiance: float = Field(ge=0, le=1)
    a_verifier: bool
    motif: str
    priorite: Literal["P1", "P2", "P3", "P4"]
    equipe: str
    reponse_initiale: str
    escalade: bool
    motifs_escalade: list[str]
    validation_humaine_requise: bool


class TicketOut(TicketInput):
    id: str
    created_at: str
    updated_at: str
    statut: Statut
    version: int
    analyse: Analyse
    categorie_validee: Categorie | None
    equipe_validee: str | None
    resolution: str | None
    historique: list[dict[str, Any]] = Field(default_factory=list)


class ListeTickets(BaseModel):
    items: list[TicketOut]
    total: int
    limit: int
    offset: int


class Modification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["valider", "demarrer", "resoudre", "reouvrir"]
    version: int = Field(ge=0)
    categorie: Categorie | None = None
    resolution: str | None = Field(default=None, min_length=1, max_length=2000)


class Erreur(BaseModel):
    code: str
    message: str
