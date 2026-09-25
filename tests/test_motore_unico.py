# -*- coding: utf-8 -*-
"""
Guardie sul MOTORE UNICO: il codice esiste una volta sola, i brain sono conoscenza.

IL DIFETTO CHE HANNO CHIUSO. Ogni brain nasceva con una copia di tools/, tests/ e
server/, e nessuno la aggiornava. Il giorno dell'audit, in brains/aion 17 tool su 31
e tutti gli 8 test erano gia' diversi da core/. Copiato fuori dal repo, il brain
'cucina' ricostruiva il suo grafo con 670 nodi duplicati che l'officina aveva gia'
eliminato: le correzioni non arrivavano mai alle copie, e nulla lo diceva.

Ora: il motore ha una VERSION, ogni brain un manifesto con la versione con cui e'
stato verificato, e per portare un brain fuori dal repo lo si ESPORTA (motore della
versione corrente + conoscenza), invece di copiarne la cartella.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# brain_new e brain_export sono strumenti dell'OFFICINA: nello scheletro ceduto non
# ci sono, e questi test li' non hanno oggetto (lo dice anche conftest.py).
brain_new = pytest.importorskip("tools.brain_new", reason="non e' un'officina")
from tools import brain_upgrade  # noqa: E402
from tools.brain import versione_motore  # noqa: E402

MOTORE = ("tools", "tests", "server", "plugins", "training", "onboarding.py")


def _registro():
    return json.loads((ROOT / "brains" / "brains.json").read_text(encoding="utf-8"))["brains"]


def test_nessun_brain_porta_una_copia_del_motore():
    copie = {b["nome"]: [p for p in MOTORE if (ROOT / b["percorso"] / p).exists()]
             for b in _registro()}
    copie = {k: v for k, v in copie.items() if v}
    assert not copie, (f"brain con una copia del motore dentro: {copie} — una copia che "
                       "nessuno aggiorna invecchia in silenzio. Il motore sta nella radice.")


def test_ogni_brain_dichiara_con_quale_motore_e_verificato():
    for b in _registro():
        codice, msg = brain_upgrade.stato(str(ROOT / b["percorso"]))
        assert codice in ("ok", "aggiornabile"), f"{b['nome']}: {msg}"


def test_il_registro_non_duplica_il_manifesto():
    """Una sola fonte per ciascun fatto: il registro dice DOVE, il manifesto COSA."""
    for b in _registro():
        assert set(b) <= {"nome", "percorso", "nota"}, (
            f"il registro ripete dati del manifesto per {b['nome']}: {sorted(set(b))}")


@pytest.mark.parametrize("brain,motore,atteso", [
    ("1.0.0", "1.0.0", "ok"),
    ("1.0.0", "1.3.2", "aggiornabile"),
    ("1.0.0", "2.0.0", "incompatibile"),   # formato dei file cambiato
    ("1.4.0", "1.3.0", "incompatibile"),   # brain verificato da un motore piu' nuovo
    (None, "1.0.0", "senza"),
])
def test_la_compatibilita_segue_il_versionamento_semantico(tmp_path, monkeypatch,
                                                          brain, motore, atteso):
    if brain:
        (tmp_path / "brain.json").write_text(json.dumps({"motore": brain}), encoding="utf-8")
    monkeypatch.setattr(brain_upgrade, "versione_motore", lambda: motore)
    assert brain_upgrade.stato(str(tmp_path))[0] == atteso


@pytest.fixture
def officina_temporanea(tmp_path, monkeypatch):
    """brain_new scrive nel registro: nei test lo si fa scrivere altrove."""
    brains = tmp_path / "brains"
    monkeypatch.setattr(brain_new, "BRAINS", str(brains))
    monkeypatch.setattr(brain_new, "REGISTRO", str(brains / "brains.json"))
    if not (ROOT / "core").is_dir():
        pytest.skip("core/ assente")
    return brains


def test_un_brain_nuovo_e_solo_conoscenza(officina_temporanea):
    dest = pathlib.Path(brain_new.crea("prova", aree="alfa,beta"))
    for parte in ("raw", "wiki", "engine", "areas.json", "brain.json"):
        assert (dest / parte).exists(), f"manca {parte}"
    assert not [p for p in MOTORE if (dest / p).exists()], "il brain nuovo porta il motore"
    man = json.loads((dest / "brain.json").read_text(encoding="utf-8"))
    assert man["motore"] == versione_motore() and man["training"] is None
    aree = [a["id"] for a in json.loads((dest / "areas.json").read_text(encoding="utf-8"))["areas"]]
    assert aree == ["alfa", "beta"]
    assert (dest / "raw" / "alfa").is_dir() and (dest / "wiki" / "beta").is_dir()
    assert (dest / "engine" / "lessons.jsonl").read_text(encoding="utf-8") == ""
    reg = json.loads((officina_temporanea / "brains.json").read_text(encoding="utf-8"))
    assert reg["brains"] == [{"nome": "prova", "percorso": "brains/prova"}]


def test_il_training_si_adotta_alla_nascita(officina_temporanea):
    if not (ROOT / "core" / "training" / "aion").is_dir():
        pytest.skip("pacchetto del training assente")
    dest = pathlib.Path(brain_new.crea("studio", aree="note", training="aion"))
    assert (dest / "engine" / "aion.model.json").exists(), "il modello non e' stato adottato"
    assert (dest / "raw" / "aion" / "aion-oracle.md").exists(), "le fonti non sono state adottate"
    assert json.loads((dest / "brain.json").read_text(encoding="utf-8"))["training"] == "aion"
    aree = [a["id"] for a in json.loads((dest / "areas.json").read_text(encoding="utf-8"))["areas"]]
    assert aree == ["note", "aion"]
    assert not (dest / "tools").exists(), "gli strumenti del training restano nel motore"


def test_l_export_porta_conoscenza_e_motore(tmp_path):
    from tools import brain_export
    sorgente = ROOT / "brains" / "cucina"
    if not sorgente.is_dir():
        pytest.skip("brain di prova assente")
    dest = tmp_path / "fuori"
    brain_export.esporta(str(sorgente), str(dest))
    assert (dest / "tools" / "rebuild_all.py").exists(), "manca il motore"
    assert (dest / "VERSION").read_text(encoding="utf-8").strip() == versione_motore()
    man = json.loads((dest / "brain.json").read_text(encoding="utf-8"))
    assert man["nome"] == "cucina" and man["motore"] == versione_motore()
    assert (dest / "raw" / "ricette").is_dir(), "manca la conoscenza del brain"
    assert not (dest / "brains").exists(), "un export e' un brain solo, non un'officina"
    assert "**/raw/**/*.csv" in (dest / ".gitignore").read_text(encoding="utf-8")
    # dentro l'export il brain e' la cartella stessa
    esito = subprocess.run([sys.executable, "tools/brain.py"], cwd=str(dest),
                           capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8",
                                                     "ALTAIR_BRAIN": ""})
    assert esito.stdout.decode("utf-8").strip() == ".", esito.stderr.decode("utf-8", "replace")


def test_un_brain_rimasto_indietro_non_si_esporta(tmp_path):
    from tools import brain_export
    brain = tmp_path / "vecchio"
    (brain / "engine").mkdir(parents=True)
    (brain / "brain.json").write_text(json.dumps({"motore": "0.9.0"}), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        brain_export.esporta(str(brain), str(tmp_path / "fuori"))
    assert "export rifiutato" in str(e.value)
    assert not (tmp_path / "fuori").exists()
