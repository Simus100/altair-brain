# -*- coding: utf-8 -*-
"""
altair-brain — partiziona graphify-out/graph.json in SOTTOGRAFI PER AREA.

Perche: scala (traversal su grafi piccoli) e sicurezza per costruzione (lo scope
per-area = quale file puoi leggere, non un filtro sui risultati).

Output (deterministico, ordinato):
  graphify-out/areas/<area>/graph.json   — stesso formato node-link di graphify,
                                           quindi `graphify query --graph <path>` funziona
  graphify-out/areas/bridges.json        — archi CROSS-area (i ponti intercampo)

Mappatura: raw/<area>/ e wiki/<area>/ -> area; engine/, server/, tools/, .claude/,
.agents/, file di radice -> "core"; raw/_inbox -> escluso. Le aree vengono da areas.json.

Uso:  python tools/build_area_graphs.py
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
AREAS = os.path.join(ROOT, "areas.json")
OUTDIR = os.path.join(ROOT, "graphify-out", "areas")

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
with open(AREAS, encoding="utf-8") as f:
    area_ids = [a["id"] for a in json.load(f)["areas"]]


def area_of(source_file: str):
    sf = (source_file or "").replace("\\", "/")
    if sf.startswith("raw/_inbox"):
        return None
    for a in area_ids:
        if sf.startswith(f"raw/{a}/") or sf.startswith(f"wiki/{a}/"):
            return a
    if sf.startswith("graphify-out/"):
        return None
    return "core"  # engine/, server/, tools/, .claude/, .agents/, radice


node_area = {}
for n in g["nodes"]:
    node_area[n["id"]] = area_of(n.get("source_file", ""))

buckets = {a: {"nodes": [], "links": []} for a in area_ids + ["core"]}
bridges = []

for n in sorted(g["nodes"], key=lambda x: x["id"]):
    a = node_area[n["id"]]
    if a:
        buckets[a]["nodes"].append(n)

for e in sorted(g["links"], key=lambda x: (str(x.get("source")), str(x.get("target")), str(x.get("relation")))):
    sa, ta = node_area.get(e.get("source")), node_area.get(e.get("target"))
    if sa is None or ta is None:
        continue
    if sa == ta:
        buckets[sa]["links"].append(e)
    else:
        bridges.append({"source": e.get("source"), "target": e.get("target"),
                        "relation": e.get("relation"), "area_source": sa, "area_target": ta})

meta_keys = {k: g[k] for k in ("directed", "multigraph", "graph") if k in g}
if os.path.isdir(OUTDIR):
    shutil.rmtree(OUTDIR)
os.makedirs(OUTDIR)

report = []
for a in area_ids + ["core"]:
    sub = dict(meta_keys)
    sub["area"] = a
    sub["built_at_commit"] = g.get("built_at_commit")
    sub["nodes"] = buckets[a]["nodes"]
    sub["links"] = buckets[a]["links"]
    os.makedirs(os.path.join(OUTDIR, a), exist_ok=True)
    with open(os.path.join(OUTDIR, a, "graph.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(sub, f, ensure_ascii=False, indent=1)
        f.write("\n")
    report.append(f"{a}: {len(sub['nodes'])} nodi / {len(sub['links'])} archi")

with open(os.path.join(OUTDIR, "bridges.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"descrizione": "archi cross-area (ponti intercampo)",
               "bridges": bridges}, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("Sottografi per area generati:")
for r in report:
    print("  ", r)
print(f"   ponti cross-area: {len(bridges)}")
