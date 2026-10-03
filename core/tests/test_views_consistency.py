"""Confronta i dati pubblicati dalla vista estesa con il grafo di ogni brain."""
from collections import Counter
import json
from pathlib import Path

import pytest

from tools.brain import BRAIN
from tools.sync_extended_view import leggi_dati

ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / 'brains/brains.json'
BRAINS = ([ROOT / b['percorso'] for b in json.loads(REGISTRO.read_text(encoding='utf-8'))['brains']]
          if REGISTRO.exists() else [Path(BRAIN)])


@pytest.mark.parametrize('brain', BRAINS, ids=lambda p: p.name)
def test_vista_estesa_corrisponde_al_grafo(brain):
    base = brain / 'graphify-out'
    if not (base / 'graph.json').exists():
        pytest.skip('brain non ancora indicizzato')
    g = json.loads((base / 'graph.json').read_text(encoding='utf-8'))
    h = (base / 'graph.html').read_text(encoding='utf-8')
    nodes = leggi_dati(h, 'RAW_NODES')[0]
    edges = leggi_dati(h, 'RAW_EDGES')[0]
    assert Counter(n['id'] for n in nodes) == Counter(n['id'] for n in g['nodes'])
    assert Counter((e['from'], e['to'], e['label']) for e in edges) == Counter(
        (e['source'], e['target'], e.get('relation', '')) for e in g['links'])
