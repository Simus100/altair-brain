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

import pathlib as _pl
try:
    from tools.brain import BRAIN as _b
    BRAIN = _pl.Path(_b) if isinstance(ROOT, _pl.Path) else _b
except ImportError:
    BRAIN = ROOT

GOLDEN = ROOT / "tests" / "golden_queries.json"
GRAPH = BRAIN / "graphify-out" / "graph.json"


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


# ---------------- F2: il RECUPERO, non solo la struttura ----------------
# I test sopra verificano che i file esistano e siano connessi nel grafo. Non
# verificano che la RICERCA li trovi: si potrebbe rompere del tutto il ranking BM25
# e restare verdi. Questo e il "context recall @N" della letteratura RAG (RAGAS),
# in versione deterministica: nessun modello, solo la posizione nei risultati.

RECALL_AT = 8          # entro quanti risultati deve comparire cio che serve
RECALL_MINIMO = 0.70   # frazione di domande che deve trovare almeno un file atteso


def _casi_recupero():
    """Solo le domande a cui la ricerca LESSICALE puo' rispondere. Quelle marcate
    'recupero_lessicale: false' restano nel golden set per il test di STRUTTURA, ma
    non sono un metro per BM25: e' documentato il perche' caso per caso, cosi la
    marcatura non puo' diventare un modo per nascondere regressioni vere."""
    d = json.loads(GOLDEN.read_text(encoding="utf-8"))
    return [q for q in d["queries"] if q.get("recupero_lessicale", True)]


@pytest.mark.parametrize("caso", _casi_recupero(),
                         ids=[q["domanda"][:45] for q in _casi_recupero()])
def test_golden_query_il_recupero_trova_qualcosa_di_pertinente(caso):
    """Per ogni domanda reale, la ricerca deve portare in superficie almeno uno dei
    file attesi entro i primi N. Se fallisce, il ranking e regredito."""
    from tools.search import cerca
    trovati = {_norm(r["file"]) for r in cerca(caso["domanda"], top=RECALL_AT)}
    attesi = {_norm(f) for f in caso["attesi"]}
    assert trovati & attesi, (
        f"recupero fallito: {caso['domanda']}\n"
        f"  attesi (uno basta): {sorted(attesi)}\n"
        f"  trovati nei primi {RECALL_AT}: {sorted(trovati)}")


def test_recall_complessivo_sopra_soglia():
    """Metrica aggregata: se scende sotto soglia, la qualita del recupero e calata
    nel suo insieme, anche se i singoli casi passano per un pelo."""
    from tools.search import cerca
    casi = _casi_recupero()
    successi, falliti = 0, []
    for caso in casi:
        trovati = {_norm(r["file"]) for r in cerca(caso["domanda"], top=RECALL_AT)}
        if trovati & {_norm(f) for f in caso["attesi"]}:
            successi += 1
        else:
            falliti.append(caso["domanda"][:50])
    recall = successi / len(casi)
    assert recall >= RECALL_MINIMO, (
        f"context recall @{RECALL_AT} = {recall:.0%} (minimo {RECALL_MINIMO:.0%})\n"
        f"  domande senza risposta: {falliti}")


def test_esclusioni_dal_recupero_sono_motivate_e_limitate():
    """Una domanda puo' essere esclusa dal metro lessicale SOLO con una motivazione
    scritta. Ma una motivazione si scrive per qualsiasi cosa: serve anche un TETTO,
    altrimenti il presidio resta sociale e non tecnico — bastava escludere tutto per
    avere il golden set sempre verde."""
    d = json.loads(GOLDEN.read_text(encoding="utf-8"))
    escluse = [q for q in d["queries"] if not q.get("recupero_lessicale", True)]
    for q in escluse:
        assert q.get("perche_non_lessicale"), f"esclusione non motivata: {q['domanda']}"
    tetto = max(1, len(d["queries"]) // 5)          # al piu' il 20%
    assert len(escluse) <= tetto, (
        f"{len(escluse)} domande escluse su {len(d['queries'])} (tetto {tetto}): "
        f"il golden set sta smettendo di misurare invece di segnalare un problema")


def test_banco_semantico_e_ancora_un_banco():
    """Le domande del banco semantico devono FALLIRE col solo lessicale: e' la loro
    ragione d'essere. Se una iniziasse a passare, non misura piu' nulla e va
    promossa a caso normale (oppure il semantico e' stato attivato: allora vanno
    tutte spostate nel golden set principale)."""
    from tools.search import cerca
    d = json.loads(GOLDEN.read_text(encoding="utf-8"))
    banco = d.get("banco_semantico", {}).get("queries", [])
    assert len(banco) >= 3, "banco semantico troppo piccolo per decidere"
    passano = []
    for q in banco:
        trovati = {_norm(r["file"]) for r in cerca(q["domanda"], top=RECALL_AT)}
        if trovati & {_norm(f) for f in q["attesi"]}:
            passano.append(q["domanda"][:45])
    assert len(passano) <= len(banco) // 2, (
        "il banco semantico non discrimina piu': queste passano gia' col lessicale "
        f"e vanno promosse nel golden set principale -> {passano}")


def test_confidenza_alta_sulle_domande_golden():
    """Le domande golden interrogano conoscenza che il brain POSSIEDE: se il
    valutatore di confidenza (F1) le giudica scarse, e tarato male."""
    from tools.search import cerca_con_diagnosi
    casi = _casi_recupero()
    scarse = [c["domanda"][:45] for c in casi
              if cerca_con_diagnosi(c["domanda"], top=5)["diagnosi"]["confidenza"]
              in ("bassa", "nessuna")]
    assert len(scarse) <= len(casi) * 0.3, (
        f"F1 troppo pessimista su conoscenza presente: {scarse}")
