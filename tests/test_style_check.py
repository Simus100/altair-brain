# -*- coding: utf-8 -*-
"""
Guardie sul verificatore stilometrico (tools/style_check.py).

Il tool ha una classe OGGETTIVA — anglicismi e ripetizioni — che per contratto
"si corregge sempre". Una classe del genere vale solo se non segnala cose che non
si possono correggere: il giorno in cui chiede di rinominare una pagina, chi la
legge impara a ignorarla, e da quel momento non protegge piu' nulla.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

sc = pytest.importorskip("tools.style_check")


def _scrivi(tmp_path, corpo):
    f = tmp_path / "prova.md"
    f.write_text("---\ndate: 2026-08-11\narea: test\n---\n" + corpo,
                 encoding="utf-8")
    return str(f)


def test_il_bersaglio_di_un_wikilink_non_e_prosa(tmp_path):
    """Un [[wikilink]] punta a un identificatore, non a una parola scelta da chi
    scrive. Contarlo faceva segnalare 'feature-engineering' come anglicismo e
    chiedeva di correggere il NOME di una pagina."""
    testo = sc.testo_da_file(_scrivi(
        tmp_path, "Le colonne nuove si preparano come spiega [[feature-engineering]].\n"))
    assert "feature" not in testo
    assert "colonne nuove si preparano" in testo


def test_il_front_matter_non_e_prosa(tmp_path):
    testo = sc.testo_da_file(_scrivi(tmp_path, "Frase unica di prova.\n"))
    assert "date" not in testo and "2026" not in testo
    assert "Frase unica di prova" in testo


def test_i_blocchi_di_codice_non_sono_prosa(tmp_path):
    """Il codice non si giudica con le misure della scrittura: senza questo, un
    notebook trascritto farebbe esplodere ogni soglia."""
    testo = sc.testo_da_file(_scrivi(
        tmp_path, "Ecco la ricetta.\n\n```python\ndf = pd.read_csv(file)\n```\n\nFine.\n"))
    assert "read_csv" not in testo
    assert "Ecco la ricetta" in testo and "Fine" in testo


def test_gli_anglicismi_veri_vengono_ancora_visti(tmp_path):
    """Il test che impedisce di 'sistemare' i falsi positivi accecando la guardia."""
    percorso = _scrivi(tmp_path, (
        "Abbiamo fatto un deep dive sul workflow del team, con un focus sul "
        "customer journey. Il framework e stato implementato in modo performante "
        "e scalabile, con una governance orientata al delivery del prodotto.\n"))
    d = sc.analizza(sc.testo_da_file(percorso), "it")
    if d == "USA_CLI" or d is None:
        d = sc.analizza_via_cli(sc.testo_da_file(percorso), "it")
    righe = " ".join(sc.riassumi(d))
    assert "OGGETTIVO" in righe, "la classe oggettiva non segnala piu' i calchi veri"
    for calco in ("team", "performante"):
        assert calco in righe, f"anglicismo non rilevato: {calco}"
