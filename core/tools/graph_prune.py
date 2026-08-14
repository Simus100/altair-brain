# -*- coding: utf-8 -*-
"""
altair-brain — toglie dal grafo cio' che NON e' conoscenza di questo brain.

IL PROBLEMA MISURATO. graphify indicizza tutto il repo. Da quando il repo e diventato
un'officina, dentro ci sono anche il PRODOTTO (core/) e le ISTANZE (brains/): 1191
nodi su 3084, il 39% del grafo, erano l'artefatto dell'export — copie dei tool, del
loro README, del training. Non conoscenza: rumore che gonfiava le metriche, sporcava
le tre viste, entrava nell'indice di ricerca e falsava l'equilibrio tra aree.

Peggio: quel rumore CRESCE con ogni brain creato. Un repo con cinque brain avrebbe
avuto piu' nodi di artefatti che di sapere.

COSA FA: rimuove i nodi che vivono nelle cartelle escluse e gli archi che li toccano.
Estende graphify senza modificarlo, come tools/altair_compact_view.py — graphify
resta aggiornabile.

Da eseguire SUBITO DOPO 'graphify update', prima di ogni tool che legge graph.json.

Uso:  python tools/graph_prune.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN            # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente

if __name__ == "__main__":
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

GRAFO = os.path.join(BRAIN, "graphify-out", "graph.json")

# Cartelle che NON sono conoscenza del brain:
#   core/      il prodotto generato — copia del motore, non sapere
#   brains/    le altre istanze — hanno il proprio grafo, non vanno nel nostro
#   training/  il training COME PACCHETTO. Quando un brain lo adotta, le fonti
#              entrano in raw/ e il modello in engine/: quella e' la copia viva.
#              La cartella training/ resta la copia CEDIBILE, identica byte per byte
#              (verificato: 7 file su 7). Lasciarla nel grafo faceva comparire la
#              stessa conoscenza due volte — 670 nodi doppi su 2436 — gonfiando la
#              centralita' di cio' che e' duplicato e squilibrando le aree. In un
#              brain che il training NON l'ha adottato e' pura zavorra: nel brain
#              'cucina' erano 670 nodi su 1252, sapere di nessuno.
ESCLUSE = ("core/", "brains/", "training/")


def _rel(nodo):
    return (nodo.get("source_file") or "").replace("\\", "/")


def pota(g):
    """Ritorna (grafo potato, nodi rimossi, archi rimossi). Deterministico."""
    da_togliere = {n["id"] for n in g["nodes"]
                   if _rel(n).startswith(ESCLUSE)}
    if not da_togliere:
        return g, 0, 0
    nodi_prima, archi_prima = len(g["nodes"]), len(g["links"])
    g["nodes"] = [n for n in g["nodes"] if n["id"] not in da_togliere]
    g["links"] = [e for e in g["links"]
                  if e.get("source") not in da_togliere
                  and e.get("target") not in da_togliere]
    return g, nodi_prima - len(g["nodes"]), archi_prima - len(g["links"])


def main():
    if not os.path.exists(GRAFO):
        sys.exit("graph.json assente: esegui prima 'graphify update .'")
    with open(GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    g, nodi, archi = pota(g)
    if nodi:
        with open(GRAFO, "w", encoding="utf-8", newline="\n") as f:
            json.dump(g, f, ensure_ascii=False, indent=2)
    print(f"Grafo potato: -{nodi} nodi, -{archi} archi da {', '.join(ESCLUSE)} "
          f"(artefatti, non conoscenza)")
    print(f"  restano {len(g['nodes'])} nodi, {len(g['links'])} archi")


if __name__ == "__main__":
    main()
