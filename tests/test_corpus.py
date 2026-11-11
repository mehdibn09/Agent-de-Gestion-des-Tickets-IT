from pathlib import Path

import pytest

from ticket_agent.corpus import empreinte, lire, normaliser, verifier_separation

ROOT = Path(__file__).resolve().parents[1]


def test_jeux_et_familles_distincts():
    jeux = [lire(ROOT / f"data/{split}.csv") for split in ["train", "validation", "test"]]
    assert list(map(len, jeux)) == [160, 32, 40]
    verifier_separation(*jeux)
    with pytest.raises(ValueError):
        verifier_separation(jeux[0], jeux[0])
    assert len(empreinte(ROOT / "data/train.csv")) == 64


@pytest.mark.parametrize("corps", ["colonne\nvaleur\n", "id,titre,description,categorie,famille\n",
    "id,titre,description,categorie,famille\n1,Test,Description,autre,f1\n",
    "id,titre,description,categorie,famille\n1,Test,,acces,f1\n",
    "id,titre,description,categorie,famille\n1,T,Description,acces,f1\n1,T,Autre,acces,f2\n",
    "id,titre,description,categorie,famille\n1,T,Identique,acces,f1\n2,T,identique,acces,f2\n"])
def test_csv_invalide(tmp_path, corps):
    path = tmp_path / "invalide.csv"
    path.write_text(corps)
    with pytest.raises(ValueError):
        lire(path)


def test_normalisation():
    assert normaliser("  Bonjour  LE\nMONDE ") == "bonjour le monde"
