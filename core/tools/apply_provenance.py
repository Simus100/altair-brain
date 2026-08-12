# -*- coding: utf-8 -*-
"""
altair-brain — cuce la catena FONTE -> CONOSCENZA nel grafo (P8).

PROBLEMA RISOLTO: raw/ e wiki/ erano due isole separate (misurato: 0 archi tra i due
strati). L'architettura a 3 strati esisteva nella documentazione ma NON nel grafo:
da una pagina curata non si poteva risalire alla fonte che l'ha generata, ne viceversa.
Il golden set (tests/test_golden.py) lo ha reso evidente fallendo sulla domanda
"da dove nasce il database degli esagrammi?".

COSA FA: legge engine/provenance.json e aggiunge archi tipizzati:
  - 'generated_from'  pagina curata -> artefatto che la genera (es. aion.model.json)
  - 'derived_from'    artefatto/pagina -> nota grezza da cui distilla
Da eseguire DOPO graphify update (che rigenera graph.json) e dopo apply_bridges.

Deterministico e idempotente. I file dichiarati ma non presenti nel grafo vengono
SEGNALATI senza far fallire la pipeline: graphify indicizza solo .md, quindi le note
.txt/.docx non sono nodi (limite noto, documentato in ROADMAP).

Uso:  python tools/apply_provenance.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
REG = os.path.join(ROOT, "engine", "provenance.json")

if not os.path.exists(REG):
    print("nessun engine/provenance.json: nessuna provenienza da applicare")
    sys.exit(0)

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
with open(REG, encoding="utf-8") as f:
    reg = json.load(f)

# nodo-FILE: quello la cui label e il nome del file (non gli heading figli)
filenode = {}
for n in g["nodes"]:
    sf = (n.get("source_file") or "").replace("\\", "/")
    if sf and n.get("label", "") == os.path.basename(sf):
        filenode[sf] = n["id"]

esistenti = {(e.get("source"), e.get("target")) for e in g["links"]}
aggiunti, assenti = 0, []


def collega(src_file, dst_file, relazione, nota=""):
    """Aggiunge un arco tra due FILE se entrambi sono nodi del grafo."""
    global aggiunti
    a, b = filenode.get(src_file), filenode.get(dst_file)
    for f, nid in ((src_file, a), (dst_file, b)):
        if nid is None and f not in assenti:
            assenti.append(f)
    if a is None or b is None or (a, b) in esistenti or (b, a) in esistenti:
        return
    g["links"].append({
        "source": a, "target": b, "relation": relazione,
        "nota": nota, "confidence": "CURATED", "confidence_score": 1.0,
        "weight": 1.0, "source_file": "engine/provenance.json",
    })
    esistenti.add((a, b))
    aggiunti += 1


# 1) ancoraggi d'area: l'indice curato -> i documenti grezzi da cui l'area nasce.
#    Basta questo per unire in un solo componente due strati altrimenti separati.
for anc in reg.get("ancoraggi_area", []):
    for fonte in anc.get("fonti", []):
        collega(anc["indice"], fonte, "derived_from", anc.get("nota", ""))

# 2) mappe dirette: singola pagina -> nota grezza (precisione fine)
for m in reg.get("mappe_dirette", []):
    for fonte in m.get("fonti", []):
        collega(m["wiki"], fonte, "derived_from", m.get("nota", ""))

with open(GRAPH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(g, f, ensure_ascii=False)
    f.write("\n")

print(f"Provenienza applicata: {aggiunti} archi nuovi.")
if assenti:
    non_md = [f for f in assenti if not f.endswith(".md")]
    print(f"  [info] {len(assenti)} file dichiarati non sono nodi del grafo "
          f"({len(non_md)} non-.md: graphify indicizza solo .md).")
    for f in assenti[:5]:
        print(f"    - {f}")
