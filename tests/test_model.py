from pathlib import Path

import joblib
import pytest

from ticket_agent.agent import Agent
from ticket_agent.corpus import lire
from ticket_agent.evaluation import evaluer
from ticket_agent.model import Classifier

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("texte,attendu", [
    ("Le mot de passe du compte est expiré.", "acces"),
    ("Le câble du clavier est cassé et les touches sont détachées.", "materiel"),
    ("Le réseau wifi ne permet plus aucune connexion Internet.", "reseau"),
    ("Le logiciel de comptabilité plante au lancement.", "logiciel")])
def test_categories_sur_exemples(classifier, texte, attendu):
    assert classifier.predire(texte)["categorie_proposee"] == attendu


def test_abstention_hors_vocabulaire(classifier):
    r = classifier.predire("xqzv wlkptr grombu zzzz qqqq")
    assert r["a_verifier"] and r["categorie"] is None and r["motif"] == "hors_vocabulaire"


def test_abstention_seuil(model_path):
    r = Classifier(model_path, 1).predire("La connexion wifi est très lente")
    assert r["a_verifier"] and r["motif"] == "confiance_insuffisante"


@pytest.mark.parametrize("texte", ["", "   ", "x" * 2201, None])
def test_texte_invalide(classifier, texte):
    with pytest.raises(ValueError):
        classifier.predire(texte)


def test_explication_reconstruit_logit(classifier):
    e = classifier.expliquer("Le réseau wifi ne donne plus de connexion Internet")
    assert e["base"] + e["somme_contributions"] == pytest.approx(e["logit"], abs=1e-10)
    assert e["termes"]


def test_evaluation_independante(classifier):
    result = evaluer(classifier, lire(ROOT / "data/test.csv"))
    assert result["n_test"] == 40
    assert sum(map(sum, result["matrice_confusion"])) == 40
    assert result["couverture"] == (40 - result["abstentions"]) / 40
    with pytest.raises(ValueError):
        evaluer(classifier, [])


def test_aucun_cas_accepte(model_path):
    r = evaluer(Classifier(model_path, 1), lire(ROOT / "data/test.csv"))
    assert r["accuracy_acceptee"] is None and r["couverture"] == 0


def test_modele_absent_incompatible(tmp_path):
    path = tmp_path / "modele.joblib"
    with pytest.raises(FileNotFoundError):
        Classifier(path)
    joblib.dump({"autre": True}, path)
    with pytest.raises(ValueError):
        Classifier(path)
    with pytest.raises(ValueError):
        Classifier(path, 1.1)


def test_orchestration_p1_et_incertitude(classifier):
    r = Agent(classifier).analyser("Incident général", "Le réseau wifi est inaccessible.", "organisation", "critique")
    assert r["priorite"] == "P1" and "criticite_P1" in r["motifs_escalade"]
    assert r["validation_humaine_requise"]
    unknown = Agent(classifier).analyser("Inconnu", "xqzv grombu zzzz qqqq", "individuel", "faible")
    assert unknown["equipe"] == "Support N1" and unknown["escalade"]
    with pytest.raises(ValueError):
        Agent(classifier).analyser("", "Description", "equipe", "normale")
