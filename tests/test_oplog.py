# -*- coding: utf-8 -*-
"""
Il registro delle operazioni (tools/oplog.py): cronaca di cosa e' stato fatto al brain.

Tre proprieta', ciascuna contro un difetto gia' visto in questo repo:
  - cresce solo quando succede qualcosa (una ricostruzione identica non aggiunge righe);
  - non entra nell'indice di ricerca, che altrimenti resterebbe un giro indietro;
  - non entra nel grafo: e' cronaca, non conoscenza.
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import oplog  # noqa: E402


def test_registra_e_non_ripete(tmp_path):
    assert oplog.registra("rebuild", "10 nodi, 5 frammenti", str(tmp_path))
    assert not oplog.registra("rebuild", "10 nodi, 5 frammenti", str(tmp_path)), \
        "una ricostruzione identica ha aggiunto una riga"
    assert oplog.registra("rebuild", "12 nodi, 6 frammenti", str(tmp_path))
    righe = oplog.voci(str(tmp_path))
    assert len(righe) == 2 and all(r.startswith("- [") and "] rebuild — " in r for r in righe)


def test_solo_tipi_dichiarati(tmp_path):
    with pytest.raises(ValueError):
        oplog.registra("qualcosa", "x", str(tmp_path))


def test_resta_fuori_da_indice_e_grafo():
    import re
    indice = (ROOT / "tools" / "build_search_index.py").read_text(encoding="utf-8")
    cartelle = re.search(r"CARTELLE\s*=\s*\(([^)]*)\)", indice).group(1)
    assert "log" not in cartelle, "il registro verrebbe indicizzato e resterebbe indietro"
    from tools import graph_prune
    assert "log.md" in graph_prune.ESCLUSE, "il registro finirebbe nel grafo come conoscenza"
