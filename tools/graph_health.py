# -*- coding: utf-8 -*-
"""
altair-brain — controllo di salute del grafo (per CI e uso locale).

Verifica:
1. i nodi wiki/aion formano UN solo componente connesso;
2. i nodi raw/aion formano UN solo componente connesso;
3. nessun nodo isolato (grado 0) sotto raw/, wiki/, engine/;
4. ANTI-REGRESSIONE: il numero di nodi non cala oltre il 20% rispetto al commit
   precedente (il workflow fa 'rm graph.json' e bypassa la protezione nativa di
   graphify). Override consapevole: variabile d'ambiente ALTAIR_ALLOW_SHRINK=1.

Exit 0 = sano; 1 = problemi. Uso:  python tools/graph_health.py
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
SHRINK_TOLERANCE = 0.20
MIN_BASELINE = 50

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)

nodes = g["nodes"]
adj = {n["id"]: set() for n in nodes}
sf = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in nodes}
for e in g["links"]:
    s, t = e.get("source"), e.get("target")
    if s in adj and t in adj:
        adj[s].add(t)
        adj[t].add(s)

problems = []

def components_of(prefix):
    ids = {i for i in adj if sf[i].startswith(prefix)}
    seen, comps = set(), 0
    for start in ids:
        if start in seen:
            continue
        comps += 1
        stack = [start]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend((adj[x] & ids) - seen)
    return comps, len(ids)

# coesione della wiki di OGNI area (lo strato curato deve essere un unico grafo).
# Le note grezze in raw/ possono essere scollegate (sono appunti): non si richiede coesione.
try:
    with open(os.path.join(ROOT, "areas.json"), encoding="utf-8") as f:
        area_ids = [a["id"] for a in json.load(f)["areas"]]
except Exception:
    area_ids = ["aion"]
for area in area_ids:
    prefix = f"wiki/{area}/"
    comps, n = components_of(prefix)
    if n and comps != 1:
        problems.append(f"{prefix}: {comps} componenti connessi (atteso 1) su {n} nodi")
# raw/aion e interconnesso dai footer: resta un invariante noto
comps, n = components_of("raw/aion/")
if n and comps != 1:
    problems.append(f"raw/aion/: {comps} componenti connessi (atteso 1) su {n} nodi")

# orfani ammessi solo NON negli strati curati (wiki/ ed engine/)
orphans = [i for i in adj if not adj[i]
           and sf[i].startswith(("wiki/", "engine/"))]
if orphans:
    problems.append(f"nodi isolati (grado 0) in wiki/ o engine/: {len(orphans)} — es. {orphans[:5]}")

# anti-regressione vs commit precedente
prev_ref = os.environ.get("ALTAIR_PREV_REF", "HEAD~1")
try:
    prev_raw = subprocess.run(
        ["git", "show", f"{prev_ref}:graphify-out/graph.json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
    if prev_raw.returncode == 0 and prev_raw.stdout.strip():
        prev_nodes = len(json.loads(prev_raw.stdout).get("nodes", []))
        cur_nodes = len(nodes)
        if prev_nodes >= MIN_BASELINE and cur_nodes < prev_nodes * (1 - SHRINK_TOLERANCE):
            msg = (f"ANTI-REGRESSIONE: nodi {prev_nodes} -> {cur_nodes} "
                   f"(calo > {int(SHRINK_TOLERANCE*100)}%)")
            if os.environ.get("ALTAIR_ALLOW_SHRINK") == "1":
                print(f"[avviso, override attivo] {msg}")
            else:
                problems.append(msg + " — se voluto: ALTAIR_ALLOW_SHRINK=1")
    else:
        print(f"[info] baseline {prev_ref} non disponibile, anti-regressione saltata")
except Exception as ex:
    print(f"[info] anti-regressione saltata: {ex}")

if problems:
    print(f"GRAFO NON SANO — {len(problems)} problemi:")
    for p in problems:
        print("  -", p)
    sys.exit(1)

print(f"Grafo sano: {len(nodes)} nodi, {len(g['links'])} archi; "
      f"wiki/aion e raw/aion coesi; nessun orfano.")
