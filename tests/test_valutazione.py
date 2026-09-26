# -*- coding: utf-8 -*-
"""
Valutazione della memoria su tre capacita', oltre al richiamo.

PERCHE'. Il golden set misura se la ricerca TROVA la risposta. LongMemEval, il banco
piu' usato per la memoria a lungo termine degli agenti, ne misura cinque; tre
mancavano del tutto, e una di queste era rotta senza che nessuno lo sapesse:

  AGGIORNAMENTO  un fatto superato non deve tornare come vero.
                 ROTTO: le note dichiaravano valid_until e superseded_by, ma l'indice
                 non li leggeva e la ricerca restituiva il fatto vecchio come quello
                 nuovo. Ora il fatto scaduto scende in fondo, marcato, e dice cosa lo
                 sostituisce.
  TEMPO          cosa era vero a una certa data: search.py --al AAAA-MM-GG.
                 MANCAVA: non c'era modo di chiederlo.
  ASTENSIONE     su cio' che il brain non sa, la confidenza deve essere bassa.
                 FUNZIONAVA gia' (verificato su domande fuori dominio): ora e' protetta.

Si lavora su un brain SINTETICO costruito al momento: le proprieta' sono del motore,
non del contenuto di qualcuno, e cosi' valgono anche nello scheletro vuoto.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

VECCHIO = "raw/economia/tasso-2024.md"
NUOVO = "raw/economia/tasso-2025.md"


def _nota(testa, corpo):
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in testa.items()) + "---\n" + corpo


@pytest.fixture(scope="module")
def brain(tmp_path_factory):
    b = tmp_path_factory.mktemp("brain_valutazione")
    (b / "engine").mkdir()
    (b / "raw" / "economia").mkdir(parents=True)
    (b / "areas.json").write_text(json.dumps({"schema_version": 1, "areas": [
        {"id": "economia", "label": "Economia", "status": "active", "keywords": ["tasso"]}]}),
        encoding="utf-8")
    (b / "brain.json").write_text(json.dumps(
        {"schema_version": 1, "nome": "valutazione", "motore": "1.1.0"}), encoding="utf-8")
    (b / VECCHIO).write_text(_nota(
        {"date": "2024-03-01", "area": "economia", "valid_until": "2025-06-01",
         "superseded_by": NUOVO},
        "# Tasso di riferimento\n\nIl tasso di riferimento della banca centrale e' fermo "
        "al 4,50 per cento, livello deciso per contenere l'inflazione.\n"), encoding="utf-8")
    (b / NUOVO).write_text(_nota(
        {"date": "2025-06-02", "area": "economia", "valid_from": "2025-06-01"},
        "# Tasso di riferimento\n\nIl tasso di riferimento della banca centrale e' sceso "
        "al 2,00 per cento dopo il rallentamento dell'inflazione.\n"), encoding="utf-8")
    for i, testo in enumerate(("Il debito pubblico si misura in rapporto al prodotto interno.",
                               "La bilancia commerciale confronta esportazioni e importazioni.",
                               "La disoccupazione giovanile resta sopra la media europea.")):
        (b / "raw" / "economia" / f"nota-{i}.md").write_text(
            _nota({"date": "2025-01-01", "area": "economia"}, f"# Nota {i}\n\n{testo}\n"),
            encoding="utf-8")
    amb = {**os.environ, "ALTAIR_BRAIN": str(b), "PYTHONIOENCODING": "utf-8"}
    esito = subprocess.run([sys.executable, str(ROOT / "tools" / "build_search_index.py")],
                           capture_output=True, env=amb)
    assert esito.returncode == 0, esito.stderr.decode("utf-8", "replace")
    return b


def _cerca(brain, domanda, al=None):
    """La ricerca in un processo pulito: i tool risolvono il brain all'import."""
    codice = ("import json,sys;sys.path.insert(0,%r);from tools.search import cerca_con_diagnosi;"
              "print(json.dumps(cerca_con_diagnosi(%r,top=5,al=%r)))" % (str(ROOT), domanda, al))
    esito = subprocess.run([sys.executable, "-c", codice], capture_output=True,
                           env={**os.environ, "ALTAIR_BRAIN": str(brain), "PYTHONIOENCODING": "utf-8"})
    assert esito.returncode == 0, esito.stderr.decode("utf-8", "replace")
    return json.loads(esito.stdout.decode("utf-8").strip().splitlines()[-1])


def test_aggiornamento_il_fatto_superato_non_torna_come_vero(brain):
    r = _cerca(brain, "tasso di riferimento della banca centrale")["risultati"]
    file = [x["file"] for x in r]
    assert file[0] == NUOVO, f"il fatto corrente non e' il primo: {file}"
    vecchio = next((x for x in r if x["file"] == VECCHIO), None)
    assert vecchio is not None, "il fatto superato e' sparito: la storia non si cancella"
    assert vecchio.get("scaduto") == "2025-06-01", "il fatto superato non e' marcato"
    assert vecchio.get("sostituito_da") == NUOVO, "non dice cosa lo sostituisce"
    assert file.index(VECCHIO) > file.index(NUOVO)


def test_tempo_cio_che_era_vero_a_una_data(brain):
    allora = [x["file"] for x in _cerca(brain, "tasso di riferimento", al="2025-01-01")["risultati"]]
    assert VECCHIO in allora and NUOVO not in allora, (
        f"a gennaio 2025 valeva solo il fatto vecchio: {allora}")
    dopo = [x["file"] for x in _cerca(brain, "tasso di riferimento", al="2025-09-01")["risultati"]]
    assert NUOVO in dopo and VECCHIO not in dopo, f"a settembre 2025 solo il nuovo: {dopo}"


@pytest.mark.parametrize("domanda", ["orbita di Plutone e fascia di Kuiper",
                                     "ricetta della carbonara con guanciale",
                                     "chi ha vinto il campionato di calcio nel 1982"])
def test_astensione_su_cio_che_il_brain_non_sa(brain, domanda):
    conf = _cerca(brain, domanda)["diagnosi"]["confidenza"]
    assert conf in ("bassa", "nessuna"), f"sicuro di se' su cio' che non sa: {conf}"


def test_su_cio_che_sa_la_confidenza_non_crolla(brain):
    """Il rovescio dell'astensione: un brain che dubita di tutto e' inutile."""
    conf = _cerca(brain, "debito pubblico rapporto prodotto interno")["diagnosi"]["confidenza"]
    assert conf in ("alta", "media"), conf
