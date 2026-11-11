from concurrent.futures import ThreadPoolExecutor

import pytest

from ticket_agent.storage import Conflit, Introuvable, Store, TransitionInvalide


def nouveau(tmp_path):
    store = Store(tmp_path / "nested/tickets.sqlite3")
    ticket = store.creer({"titre": "Test"}, {"categorie": "reseau"}, "client")
    return store, ticket


def test_cycle_persistant_et_historique(tmp_path):
    store, t = nouveau(tmp_path)
    t = store.modifier(t["id"], "valider", 0, "reseau")
    assert t["equipe_validee"] == "Réseaux"
    t = store.modifier(t["id"], "demarrer", 1)
    t = store.modifier(t["id"], "resoudre", 2, resolution="Configuration vérifiée par le technicien")
    assert t["statut"] == "RESOLU" and len(t["historique"]) == 4
    assert t["historique"][-1]["details"]["resolution"] == "Configuration vérifiée par le technicien"
    t = store.modifier(t["id"], "reouvrir", 3)
    assert t["statut"] == "EN_COURS" and t["version"] == 4
    autre = Store(store.path)
    assert autre.obtenir(t["id"])["version"] == 4
    assert autre.lister("EN_COURS")["total"] == 1
    assert autre.lister(offset=100)["items"] == []


def test_erreur_sans_ecriture_partielle(tmp_path):
    store, t = nouveau(tmp_path)
    for action, cat in [("resoudre", None), ("valider", None), ("valider", "autre")]:
        with pytest.raises(TransitionInvalide):
            store.modifier(t["id"], action, 0, cat)
    assert store.obtenir(t["id"])["version"] == 0
    assert len(store.obtenir(t["id"])["historique"]) == 1
    store.modifier(t["id"], "valider", 0, "materiel")
    with pytest.raises(Conflit):
        store.modifier(t["id"], "demarrer", 0)
    with pytest.raises(TransitionInvalide):
        store.modifier(t["id"], "demarrer", 1, categorie="acces")
    with pytest.raises(TransitionInvalide):
        store.modifier(t["id"], "demarrer", 1, resolution="pas une résolution")
    store.modifier(t["id"], "demarrer", 1)
    with pytest.raises(TransitionInvalide):
        store.modifier(t["id"], "resoudre", 2, resolution="   ")
    assert store.obtenir(t["id"])["statut"] == "EN_COURS"


def test_concurrence_un_seul_gagnant(tmp_path):
    store, t = nouveau(tmp_path)
    def operation():
        try:
            store.modifier(t["id"], "valider", 0, "reseau")
            return "OK"
        except Conflit:
            return "CONFLIT"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: operation(), range(2)))
    assert sorted(results) == ["CONFLIT", "OK"]
    assert len(store.obtenir(t["id"])["historique"]) == 2


def test_sql_et_parametres(tmp_path):
    store, t = nouveau(tmp_path)
    with pytest.raises(Introuvable):
        store.obtenir("' OR 1=1 --")
    with pytest.raises(Introuvable):
        store.modifier("absent", "valider", 0, "reseau")
    for args in [("AUTRE", 50, 0), (None, 0, 0), (None, 50, -1)]:
        with pytest.raises(ValueError):
            store.lister(*args)
    assert store.lister()["total"] == 1
