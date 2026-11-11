import pytest
from hypothesis import given
from hypothesis import strategies as st

from ticket_agent.rules import CATEGORIES, EQUIPES, priorite, reponse_initiale


@pytest.mark.parametrize("impact,urgence,attendu", [
    ("individuel", "faible", "P4"), ("individuel", "normale", "P4"), ("individuel", "critique", "P3"),
    ("equipe", "faible", "P4"), ("equipe", "normale", "P3"), ("equipe", "critique", "P2"),
    ("organisation", "faible", "P3"), ("organisation", "normale", "P2"), ("organisation", "critique", "P1")])
def test_matrice_metier(impact, urgence, attendu):
    assert priorite(impact, urgence) == attendu


@pytest.mark.parametrize("impact,urgence", [("autre", "faible"), ("equipe", "urgent"), ("", "")])
def test_refus_valeurs_inconnues(impact, urgence):
    with pytest.raises(ValueError):
        priorite(impact, urgence)


@given(st.sampled_from(["individuel", "equipe", "organisation"]))
def test_urgence_croissante_ne_diminue_pas_priorite(impact):
    niveaux = [int(priorite(impact, u)[1]) for u in ["faible", "normale", "critique"]]
    assert niveaux == sorted(niveaux, reverse=True)


@pytest.mark.parametrize("categorie", [*CATEGORIES, None, "autre"])
def test_reponse_controlee(categorie):
    assert len(reponse_initiale(categorie)) > 40
    if categorie in CATEGORIES:
        assert categorie in EQUIPES
