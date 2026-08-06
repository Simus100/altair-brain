# -*- coding: utf-8 -*-
"""
altair-brain — valutazione del brain sul golden set (P9).

PERCHE: senza una misura, la qualita del retrieval degrada in silenzio. Aggiungi 500
note, rinomina una pagina, spezza un ponte — e te ne accorgi mesi dopo. Questo test
verifica che le domande reali di tests/golden_queries.json continuino ad avere risposta
nel grafo: i nodi attesi ESISTONO e sono CONNESSI tra loro entro max_hops.

Legge graphify-out/graph.json (committato): deterministico, nessuna dipendenza da
graphify installato, quindi gira anche in CI.
"""
import collections
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "tests" / "golden_queries.json"
GRAPH = ROOT / "graphify-out" / "graph.json"


def _norm(p: str) -> str:
    return (p or "").replace("\\", "/")


@pytest.fixture(scope="module")
def brain():
    """Grafo caricato una volta: indice file->nodi e adiacenza non orientata."""
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    per_file = collections.defaultdict(set)
    for n in g["nodes"]:
        per_file[_norm(n.get("source_file"))].add(n["id"])
    adj = collections.defaultdict(set)
    for e in g["links"]:
        s, t = e.get("source"), e.get("target")
        if s and t:
            adj[s].add(t)
            adj[t].add(s)
    return {"per_file": per_file, "adj": adj}


def _distanza(adj, sorgenti: set, destinazioni: set, max_hops: int):
    """BFS multi-sorgente: minima distanza tra due insiemi di nodi (None se irraggiungibili)."""
    if sorgenti & destinazioni:
        return 0
    visti = set(sorgenti)
    frontiera = set(sorgenti)
    for salto in range(1, max_hops + 1):
        prossima = set()
        for x in frontiera:
            prossima |= adj.get(x, set()) - visti
        if not prossima:
            return None
        if prossima & destinazioni:
            return salto
        visti |= prossima
        frontiera = prossima
    return None


def _casi():
    d = json.loads(GOLDEN.read_text(encoding="utf-8"))
    return [(q, d.get("max_hops", 4)) for q in d["queries"]]


@pytest.mark.parametrize("caso,max_hops", _casi(),
                         ids=[q["domanda"][:45] for q, _ in _casi()])
def test_golden_query_ha_risposta_nel_grafo(brain, caso, max_hops):
    per_file, adj = brain["per_file"], brain["adj"]

    # 1) i file attesi devono esistere nel grafo (rileva cancellazioni e rinomine)
    mancanti = [f for f in caso["attesi"] if not per_file.get(_norm(f))]
    assert not mancanti, (
        f"domanda senza risposta: {caso['domanda']}\n"
        f"file attesi assenti dal grafo: {mancanti}")

    # 2) devono essere connessi tra loro (rileva la frammentazione della conoscenza)
    attesi = [set(per_file[_norm(f)]) for f in caso["attesi"]]
    for i in range(len(attesi) - 1):
        d = _distanza(adj, attesi[i], attesi[i + 1], max_hops)
        assert d is not None, (
            f"conoscenza frammentata: {caso['domanda']}\n"
            f"'{caso['attesi'][i]}' e '{caso['attesi'][i+1]}' non sono connessi "
            f"entro {max_hops} salti — un collegamento si e rotto")


def test_golden_set_e_significativo():
    """Il golden set stesso non deve impoverirsi: presidio contro la sua erosione."""
    d = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert len(d["queries"]) >= 8, "golden set troppo piccolo per essere una misura"
    for q in d["queries"]:
        assert q.get("domanda") and len(q.get("attesi", [])) >= 2, \
            f"caso malformato: {q}"
