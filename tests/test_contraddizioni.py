# -*- coding: utf-8 -*-
"""
Il rapporto sulle contraddizioni (tools/contradiction_report.py) vede cio' che deve, e
tace su cio' che il brain ha gia' risolto.

Sul corpus reale di aion non trova candidati: e' un esito plausibile (note diverse
raramente misurano la stessa cosa), ma un rapporto che non trova nulla potrebbe anche
essere cieco — la prima versione estraeva UN fatto da tutto il brain. Per questo si
verifica su casi piantati apposta, di cui si conosce la risposta.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import contradiction_report as cr  # noqa: E402


def _brain(tmp_path, note):
    b = tmp_path / "b"
    (b / "raw" / "economia").mkdir(parents=True)
    (b / "areas.json").write_text(json.dumps({"schema_version": 1, "areas": [
        {"id": "economia", "label": "Economia", "status": "active"}]}), encoding="utf-8")
    for nome, (testa, corpo) in note.items():
        fm = "".join(f"{k}: {v}\n" for k, v in {"date": "2025-01-01", "area": "economia",
                                                 **testa}.items())
        (b / "raw" / "economia" / nome).write_text(f"---\n{fm}---\n{corpo}\n", encoding="utf-8")
    return str(b)


def test_vede_due_note_che_danno_valori_diversi(tmp_path):
    b = _brain(tmp_path, {
        "a.md": ({}, "Il tasso di disoccupazione giovanile e' al 22 per cento."),
        "b.md": ({}, "Oggi il tasso di disoccupazione giovanile e' al 28%."),
    })
    c = cr.candidati(b)
    assert len(c) == 1, c
    assert c[0]["unita"] == "%" and {v["valore"] for v in c[0]["valori"].values()} == {22, 28}


def test_tace_se_la_nota_vecchia_e_superata(tmp_path):
    b = _brain(tmp_path, {
        "vecchia.md": ({"superseded_by": "raw/economia/nuova.md"},
                       "Il tasso di riferimento bancario e' al 4,50%."),
        "nuova.md": ({}, "Il tasso di riferimento bancario e' al 2,00%."),
    })
    assert cr.candidati(b) == [], "una sostituzione dichiarata non e' una contraddizione"


def test_tace_se_la_nota_vecchia_e_scaduta(tmp_path):
    b = _brain(tmp_path, {
        "vecchia.md": ({"valid_until": "2020-01-01"}, "Il tasso di riferimento bancario e' al 4,50%."),
        "nuova.md": ({}, "Il tasso di riferimento bancario e' al 2,00%."),
    })
    assert cr.candidati(b) == [], "un fatto scaduto e' storia, non contraddizione"


def test_tace_su_una_serie_storica(tmp_path):
    """116,5% nel 2011 e 131,8% nel 2017 sono due misure, non due versioni della stessa."""
    b = _brain(tmp_path, {
        "a.md": ({}, "Nel 2011 il debito pubblico italiano era pari al 116,5%."),
        "b.md": ({}, "Nel 2017 il debito pubblico italiano era pari al 131,8%."),
    })
    assert cr.candidati(b) == []


def test_non_confonde_codice_e_stile_con_affermazioni(tmp_path):
    b = _brain(tmp_path, {
        "a.md": ({}, "width: 100%; height: 380px;"),
        "b.md": ({}, "<stop offset=\"0%\" stop-color=\"var(--oro)\" />"),
    })
    assert cr.fatti(b)[0] == []
