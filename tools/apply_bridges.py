# -*- coding: utf-8 -*-
"""
altair-brain — inietta i PONTI INTERCAMPO curati (engine/bridges.json) nel grafo.

I wikilink non attraversano le cartelle e graphify non fonde nodi tra aree: i ponti
tra macroaree vanno dichiarati a mano e aggiunti come archi 'bridge' nel grafo DOPO
`graphify update` (che rigenera graph.json da zero). Da eseguire in pipeline dopo
graphify update e PRIMA di build_area_graphs (che li rilevera come cross-area).

Deterministico, idempotente. Exit 1 se un ponte punta a una pagina inesistente.
Uso:  python tools/apply_bridges.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
REG = os.path.join(ROOT, "engine", "bridges.json")

if not os.path.exists(REG):
    print("nessun engine/bridges.json: nessun ponte da applicare")
    sys.exit(0)

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
with open(REG, encoding="utf-8") as f:
    bridges = json.load(f).get("bridges", [])

# nodo-FILE per ogni pagina: quello il cui label e il nome-file (non gli heading figli)
filenode = {}
for n in g["nodes"]:
    sf = (n.get("source_file") or "").replace("\\", "/")
    if sf.endswith(".md") and n.get("label", "") == os.path.basename(sf):
        filenode[sf] = n["id"]

existing = {(e.get("source"), e.get("target")) for e in g["links"]}
errors, added = [], 0

for b in bridges:
    sa = f"wiki/{b['from']['area']}/{b['from']['page']}.md"
    sb = f"wiki/{b['to']['area']}/{b['to']['page']}.md"
    ia, ib = filenode.get(sa), filenode.get(sb)
    if not ia:
        errors.append(f"pagina ponte inesistente: {sa}")
    if not ib:
        errors.append(f"pagina ponte inesistente: {sb}")
    if not ia or not ib:
        continue
    if (ia, ib) in existing or (ib, ia) in existing:
        continue
    g["links"].append({
        "source": ia, "target": ib, "relation": "bridge",
        "concetto": b.get("concetto", ""), "confidence": "CURATED",
        "confidence_score": 1.0, "weight": 1.0,
    })
    existing.add((ia, ib))
    added += 1

if errors:
    print(f"PONTI NON VALIDI — {len(errors)} errori:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

with open(GRAPH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(g, f, ensure_ascii=False)
    f.write("\n")

print(f"Ponti intercampo applicati: {added} nuovi ({len(bridges)} dichiarati).")
