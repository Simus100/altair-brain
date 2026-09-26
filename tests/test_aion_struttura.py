# -*- coding: utf-8 -*-
"""
La struttura del training AION: gli agenti stanno insieme, ETHOS e' il cancello.

Non basta che ogni nome del modello esista (quello lo controllava gia'
validate_model). Qui si prova che il validatore FERMA un modello che si scolla:
  - un agente che l'orchestratore SUPERIA non raggiunge piu';
  - un secondo cancello accanto a ETHOS (l'etica deve avere un punto solo);
  - un insegnamento consultato da una parte sola del legame.
Su una copia del modello, rotta di proposito: un validatore che non vede un guasto
costruito apposta non vedra' quelli veri.
"""
import copy
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.brain import BRAIN  # noqa: E402

MODELLO = pathlib.Path(BRAIN) / "engine" / "aion.model.json"
if not MODELLO.exists():
    pytest.skip("training AION non adottato in questo brain", allow_module_level=True)
if not (ROOT / "tools" / "validate_model.py").exists():
    pytest.skip("validatore del training assente", allow_module_level=True)


def _valida(tmp_path, modifica=None):
    b = tmp_path / "b"
    (b / "engine" / "schema").mkdir(parents=True)
    m = json.loads(MODELLO.read_text(encoding="utf-8"))
    if modifica:
        modifica(m)
    (b / "engine" / "aion.model.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    for rel in ("engine/aion-reasoner.md", "engine/schema/aion.model.schema.json"):
        shutil.copy2(pathlib.Path(BRAIN) / rel, b / rel)
    esito = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_model.py")],
                           capture_output=True, env={**os.environ, "ALTAIR_BRAIN": str(b),
                                                     "PYTHONIOENCODING": "utf-8"})
    return esito.returncode, esito.stdout.decode("utf-8", "replace")


def _agente(m, id_):
    return next(a for a in m["agenti"] if a["id"] == id_)


def test_il_modello_vero_sta_insieme(tmp_path):
    codice, out = _valida(tmp_path)
    assert codice == 0, out


def test_un_agente_scollegato_da_superia_viene_fermato(tmp_path):
    def rompi(m):
        sup = _agente(m, "aion-superia")
        sup["orchestra"] = [x for x in sup["orchestra"] if x != "aion-cognition-view"]
        for a in m["agenti"]:
            a["collabora"] = [x for x in a.get("collabora", []) if x != "aion-cognition-view"]
    codice, out = _valida(tmp_path, rompi)
    assert codice == 1 and "irraggiungibile" in out and "aion-cognition-view" in out, out


def test_un_secondo_cancello_accanto_a_ethos_viene_fermato(tmp_path):
    def rompi(m):
        _agente(m, "aion-synth")["gate"] = True
    codice, out = _valida(tmp_path, rompi)
    assert codice == 1 and "cancello" in out, out


def test_un_legame_a_senso_unico_viene_fermato(tmp_path):
    def rompi(m):
        t = m["insegnamenti"][0]
        t["consultato_da"] = [x for x in t["consultato_da"]][1:]   # toglie un agente
    codice, out = _valida(tmp_path, rompi)
    assert codice == 1 and "asimmetria" in out, out
