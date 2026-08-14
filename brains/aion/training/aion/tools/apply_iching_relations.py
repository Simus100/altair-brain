# -*- coding: utf-8 -*-
"""
altair-brain — inietta nel grafo le relazioni combinatorie dell'I Ching (SPERIMENTALE).

PERCHE ESISTE: le relazioni opposto/rovesciato/nucleare tra i 64 esagrammi sono
matematicamente coerenti (involuzioni verificate) e vivono in engine/iching.db.json,
ma sono INVISIBILI al grafo — graphify vede solo l'adiacenza testuale del documento
grezzo, non le relazioni combinatorie curate. Le coppie opposte (11/12, 1/2, 43/44...)
finiscono oggi in community diverse: la coerenza logica del sistema non e navigabile.

STATO: OPZIONALE, NON cablato in tools/rebuild_all.py. Va eseguito a mano quando lo
si vuole; non altera il comportamento di default del brain finche non lo si lancia
esplicitamente. Stessa filosofia di tools/build_dense_index.py (ricerca semantica):
un potenziamento che si attiva, non una dipendenza imposta.

FONTE UNICA: legge le relazioni da engine/iching.db.json (gia esistente), non ne crea
una copia — se il DB cambia rigenerando da raw/aion/aion-oracle.md, questo script si
allinea da solo alla prossima esecuzione.

REVERSIBILE: `git checkout -- graphify-out/graph.json` annulla tutto (e generato).
IDEMPOTENTE: rilanciarlo non duplica archi (opposto e rovesciato sono simmetrici:
si registra una sola volta per coppia; nucleare puo essere non simmetrico e si
verifica comunque l'esistenza dell'arco prima di aggiungerlo).

Uso:
  python tools/apply_iching_relations.py             (applica su graphify-out/graph.json)
  python tools/apply_iching_relations.py --dry-run   (mostra cosa farebbe, non scrive)
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN            # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente


# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

GRAPH = os.path.join(BRAIN, "graphify-out", "graph.json")
DB = os.path.join(BRAIN, "engine", "iching.db.json")

RELAZIONI = ("opposto", "rovesciato", "nucleare")


def trova_nodi_esagramma(g):
    """I 64 nodi-esagramma nel testo grezzo: label 'N. hanzi Nome (pinyin) simbolo'."""
    mappa = {}
    for n in g["nodes"]:
        m = re.match(r"^(\d+)\.\s", n.get("label", "") or "")
        sf = (n.get("source_file") or "").replace("\\", "/")
        if m and sf == "raw/aion/aion-oracle.md":
            mappa[int(m.group(1))] = n["id"]
    return mappa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="mostra senza scrivere")
    a = ap.parse_args()

    if not os.path.exists(DB):
        sys.exit("engine/iching.db.json assente: esegui prima tools/build_iching_db.py")
    if not os.path.exists(GRAPH):
        sys.exit("graphify-out/graph.json assente: esegui prima 'graphify update .'")

    with open(DB, encoding="utf-8") as f:
        db = json.load(f)
    with open(GRAPH, encoding="utf-8") as f:
        g = json.load(f)

    nodi = trova_nodi_esagramma(g)
    if len(nodi) != 64:
        print(f"[avviso] trovati {len(nodi)}/64 nodi-esagramma: la struttura del "
              f"documento potrebbe essere cambiata. Procedo comunque con quelli trovati.")

    # Chiave di deduplica: (coppia NON ORDINATA, tipo di relazione) — non la sola
    # coppia. DIFETTO REALE TROVATO E CORRETTO: con la coppia da sola, quando due
    # esagrammi sono legati da PIU relazioni contemporaneamente (capita 8 volte sui
    # 64 reali: 11/12, 17/18, 53/54 hanno opposto+rovesciato sullo stesso bersaglio,
    # 63/64 addirittura tutte e tre) la seconda relazione veniva scartata come
    # "gia presente" mentre era un fatto logico DIVERSO — informazione persa in
    # silenzio. Con la relazione nella chiave, ogni fatto distinto ottiene il suo
    # arco; resta idempotente perche la stessa relazione sulla stessa coppia (anche
    # vista dal verso opposto, es. opposto(1)=2 e opposto(2)=1) e riconosciuta come
    # lo stesso fatto e aggiunta una sola volta.
    esistenti = set()
    for e in g["links"]:
        esistenti.add((frozenset((e.get("source"), e.get("target"))), e.get("relation")))

    aggiunti, saltati_gia_presenti = 0, 0
    for esa in db["esagrammi"]:
        i = esa["id"]
        if i not in nodi:
            continue
        for rel in RELAZIONI:
            j = esa["relazioni"].get(rel)
            if not j or j not in nodi or j == i:
                continue
            a_id, b_id = nodi[i], nodi[j]
            chiave = (frozenset((a_id, b_id)), f"iching_{rel}")
            if chiave in esistenti:
                saltati_gia_presenti += 1
                continue
            g["links"].append({
                "source": a_id, "target": b_id, "relation": f"iching_{rel}",
                "confidence": "CURATED", "confidence_score": 1.0, "weight": 1.0,
                "source_file": "engine/iching.db.json",
            })
            esistenti.add(chiave)
            aggiunti += 1

    print(f"Relazioni I Ching: {aggiunti} archi da aggiungere "
          f"({saltati_gia_presenti} gia presenti — idempotente).")
    if a.dry_run:
        print("(--dry-run: nulla scritto)")
        return

    with open(GRAPH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False)
        f.write("\n")
    print(f"Scritto: {GRAPH} ({len(g['nodes'])} nodi, {len(g['links'])} archi)")
    print("Per vedere l'effetto sulle community: graphify cluster-only . --no-label")


if __name__ == "__main__":
    main()
