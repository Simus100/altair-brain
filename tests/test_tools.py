# -*- coding: utf-8 -*-
"""
Golden test sui tool critici del brain (finora coperti solo indirettamente dalla CI).

- oracle_cast: attribuzione decisionale (matematica Re Wen), lancio seedato, ricerca tag.
- report_update: round-trip su una copia temporanea del layout repo (il JSON e la
  fonte di verita, il prototipo HTML deve restare sincronizzato).

Tutto deterministico, nessuna rete, nessuna API.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.oracle_cast import attribute_reading, cast_reading, search_by_tags  # noqa: E402


# ---------------- attribuzione decisionale (metodo canonico dei report) ----------------

def test_attribuzione_6_linea4_da_59():
    """6 (Il Conflitto) + 4a linea mobile -> 59 (La Dissoluzione). Caso Iran."""
    r = attribute_reading(6, [4])
    assert r["esagramma_primario"]["id"] == 6
    assert r["esagramma_secondario"]["id"] == 59
    assert r["consiglio_linee"][0]["linea"] == 4
    assert "conciliazione" in r["consiglio_linee"][0]["testo"].lower()


def test_attribuzione_43_quattro_mobili_da_16():
    """43 + mobili [1,2,3,5] -> 16, con un consiglio per ogni linea mobile."""
    r = attribute_reading(43, [1, 2, 3, 5])
    assert r["esagramma_secondario"]["id"] == 16
    assert [c["linea"] for c in r["consiglio_linee"]] == [1, 2, 3, 5]


def test_attribuzione_senza_mobili_e_range():
    r = attribute_reading(1, [])
    assert r["esagramma_secondario"] is None
    try:
        attribute_reading(1, [7])
        assert False, "linea 7 fuori range accettata"
    except ValueError:
        pass


def test_cast_seedato_riproducibile():
    """Stesso seed -> stessa lettura (verificabilita)."""
    a, b = cast_reading(seed=1023), cast_reading(seed=1023)
    assert a["lanci"] == b["lanci"]
    assert a["esagramma_primario"]["id"] == b["esagramma_primario"]["id"]


def test_ricerca_tag_suggerisce_43():
    """La selezione decisionale trova il 43 per l'argomento 'decisione/svolta'."""
    out = search_by_tags("tensione critica decisione svolta superamento")
    assert out and out[0]["id"] == 43


# ---------------- report_update: round-trip DB -> prototipo ----------------

def _mini_repo(tmp_path: Path) -> Path:
    """Copia minima del layout repo: tools/report_update.py + report finto."""
    (tmp_path / "tools").mkdir()
    shutil.copy(ROOT / "tools" / "report_update.py", tmp_path / "tools")
    data = tmp_path / "reports" / "data"
    data.mkdir(parents=True)
    db = {"report": "caso-test", "titolo": "Test", "aggiornato_il": "2026-01-01T00:00:00",
          "verdetto": {"corrente": "iniziale", "storia": []},
          "nodi": {"alpha": []}}
    (data / "caso-test.updates.json").write_text(
        json.dumps(db, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "reports" / "caso-test-prototype.html").write_text(
        '<html><script type="application/json" id="updates-db">{}</script></html>',
        encoding="utf-8")
    return tmp_path


def _run_update(repo: Path, *args: str):
    p = subprocess.run([sys.executable, str(repo / "tools" / "report_update.py"),
                        "--report", "caso-test", *args],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr or p.stdout


def test_report_update_nodo_e_sync_prototipo(tmp_path):
    repo = _mini_repo(tmp_path)
    _run_update(repo, "--node", "alpha", "--text", "prova update",
                "--fonte", "TestWire", "--confidenza", "alta",
                "--ts", "2026-02-02T12:00:00")
    db = json.loads((repo / "reports" / "data" / "caso-test.updates.json")
                    .read_text(encoding="utf-8"))
    voce = db["nodi"]["alpha"][0]
    assert (voce["testo"], voce["fonte"], voce["confidenza"]) == \
           ("prova update", "TestWire", "alta")
    assert db["aggiornato_il"] == "2026-02-02T12:00:00"
    # il prototipo deve contenere il DB aggiornato (specchio sincronizzato)
    html = (repo / "reports" / "caso-test-prototype.html").read_text(encoding="utf-8")
    assert "prova update" in html and "TestWire" in html


def test_report_update_verdict_set_current(tmp_path):
    repo = _mini_repo(tmp_path)
    _run_update(repo, "--verdict", "--text", "svolta", "--set-current", "NUOVO RESPONSO")
    db = json.loads((repo / "reports" / "data" / "caso-test.updates.json")
                    .read_text(encoding="utf-8"))
    assert db["verdetto"]["corrente"] == "NUOVO RESPONSO"
    assert db["verdetto"]["storia"][-1]["testo"] == "svolta"


def test_report_update_nodo_inesistente_fallisce(tmp_path):
    repo = _mini_repo(tmp_path)
    p = subprocess.run([sys.executable, str(repo / "tools" / "report_update.py"),
                        "--report", "caso-test", "--node", "ghost", "--text", "x"],
                       capture_output=True, text=True)
    assert p.returncode != 0
