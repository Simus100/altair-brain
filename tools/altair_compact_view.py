# -*- coding: utf-8 -*-
"""
altair-brain — generatore della VISTA COMPATTA STRUTTURALE (generica su tutte le aree).

Estende graphify (NON lo modifica): legge graphify-out/graph.json + areas.json e produce
una vista compatta che mostra altair-brain come PROCESSO a 5 fasi
(sorgenti -> modello -> motore -> skill -> feedback), con UN nodo per area in ciascuna
fase di conoscenza (dimensionato sul numero reale di nodi) e i ponti intercampo tra aree.

Output (accanto a graph.html, che resta intatto):
  - graphify-out/graph-compact.json
  - graphify-out/graph-compact.html   (interattivo, D3, colorato per area/fase)

Deterministico, nessuna API. Uso:  python tools/altair_compact_view.py
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
AREAS = os.path.join(ROOT, "areas.json")
BRIDGES = os.path.join(ROOT, "graphify-out", "areas", "bridges.json")
OUT_JSON = os.path.join(ROOT, "graphify-out", "graph-compact.json")
OUT_HTML = os.path.join(ROOT, "graphify-out", "graph-compact.html")

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
with open(AREAS, encoding="utf-8") as f:
    areas = [a["id"] for a in json.load(f)["areas"]]

# conteggio nodi reali per (strato, area)
raw_count = {a: 0 for a in areas}
wiki_count = {a: 0 for a in areas}
engine_files, skill_names = set(), set()
for n in g["nodes"]:
    sf = (n.get("source_file") or "").replace("\\", "/")
    for a in areas:
        if sf.startswith(f"raw/{a}/"):
            raw_count[a] += 1
        elif sf.startswith(f"wiki/{a}/"):
            wiki_count[a] += 1
    if sf.startswith("engine/") and sf.endswith((".json", ".md")):
        engine_files.add(sf.split("/")[-1])
    if sf.startswith(".claude/skills/"):
        parts = sf.split("/")
        if len(parts) > 2:
            skill_names.add(parts[2])

def sz(count):
    return 7 + min(18, round(math.sqrt(count) * 1.6)) if count else 7

nodes, edges, seen = [], [], set()

def add_node(nid, label, layer, size=8, kind="dato"):
    if nid in seen:
        return
    seen.add(nid)
    nodes.append({"id": nid, "label": label, "layer": layer, "kind": kind, "size": size})

def add_edge(a, b, kind="rel"):
    if a in seen and b in seen:
        edges.append({"source": a, "target": b, "kind": kind})

# ---- backbone di PROCESSO (5 fasi) ----
phases = [
    ("fase:1", "(1) Sorgenti — raw/"),
    ("fase:2", "(2) Modello — wiki/"),
    ("fase:3", "(3) Motore — engine/"),
    ("fase:4", "(4) Skill"),
    ("fase:5", "(5) Feedback — LESSONS"),
]
for pid, plab in phases:
    add_node(pid, plab, "processo", size=17, kind="fase")
for i in range(len(phases) - 1):
    add_edge(phases[i][0], phases[i + 1][0], kind="flow")
add_edge("fase:5", "fase:2", kind="loop")  # il feedback rientra nel modello

# ---- un nodo per area, in fase Sorgenti e in fase Modello ----
for a in areas:
    if raw_count[a]:
        add_node(f"raw:{a}", f"{a} (raw)", f"area:{a}", size=sz(raw_count[a]))
        add_edge("fase:1", f"raw:{a}", kind="has")
    if wiki_count[a]:
        add_node(f"wiki:{a}", f"{a}", f"area:{a}", size=sz(wiki_count[a]))
        add_edge("fase:2", f"wiki:{a}", kind="has")
    if raw_count[a] and wiki_count[a]:
        add_edge(f"raw:{a}", f"wiki:{a}", kind="derive")

# ---- motore, skill, feedback ----
for ef in sorted(engine_files):
    add_node(f"eng:{ef}", ef, "engine", size=8)
    add_edge("fase:3", f"eng:{ef}", kind="has")
for sk in sorted(skill_names):
    add_node(f"skill:{sk}", f"/{sk}", "skill", size=9)
    add_edge("fase:4", f"skill:{sk}", kind="has")
add_edge("fase:3", "fase:4", kind="rel")  # il motore alimenta le skill
add_node("data:lessons", "LESSONS / memory", "feedback", size=9)
add_edge("fase:5", "data:lessons", kind="has")

# ---- ponti intercampo (edge cross-area tra i modelli) ----
bridge_count = 0
if os.path.exists(BRIDGES):
    with open(BRIDGES, encoding="utf-8") as f:
        for br in json.load(f).get("bridges", []):
            sa, ta = br.get("area_source"), br.get("area_target")
            if sa != ta and f"wiki:{sa}" in seen and f"wiki:{ta}" in seen:
                add_edge(f"wiki:{sa}", f"wiki:{ta}", kind="bridge")
                bridge_count += 1

compact = {"nodes": nodes, "links": edges,
           "meta": {"generato_da": "tools/altair_compact_view.py",
                    "fonte": "graphify-out/graph.json + areas.json",
                    "aree": areas, "ponti_intercampo": bridge_count,
                    "descrizione": "Vista compatta: altair-brain come processo a 5 fasi, un nodo per area."}}
with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
    json.dump(compact, f, ensure_ascii=False, indent=2)
    f.write("\n")

# palette per area (ciclica) + colori di sistema
AREA_COLORS = ["#7ed0a8", "#c39bf0", "#f0a35e", "#e57ea8", "#8fd0e5", "#d9c66a"]
area_color = {f"area:{a}": AREA_COLORS[i % len(AREA_COLORS)] for i, a in enumerate(areas)}
legend_areas = "".join(
    f'<div><span class="sw" style="background:{area_color[f"area:{a}"]}"></span>{a}</div>'
    for a in areas if wiki_count[a] or raw_count[a])
color_js = json.dumps({**area_color, "processo": "#6ea8fe", "engine": "#f0a35e",
                       "skill": "#9ad06a", "feedback": "#e5b567", "altro": "#888"})

DATA = json.dumps(compact, ensure_ascii=False)
HTML = """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<title>altair-brain — vista compatta strutturale</title>
<style>
  html,body{margin:0;height:100%;background:#0f1115;color:#e6e6e6;font-family:system-ui,sans-serif}
  #h{position:fixed;top:12px;left:16px;z-index:10}
  #h b{font-size:16px} #h span{font-size:12px;color:#9aa0aa}
  #leg{position:fixed;top:12px;right:16px;z-index:10;font-size:12px;background:#171a21;
       border:1px solid #2a2f3a;border-radius:8px;padding:8px 10px}
  .sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}
  svg{width:100vw;height:100vh;display:block}
  .lnk{stroke:#3a4150;stroke-width:1} .lnk.flow{stroke:#6ea8fe;stroke-width:2.5}
  .lnk.loop{stroke:#f0a35e;stroke-width:2;stroke-dasharray:5 4} .lnk.has{stroke:#2a2f3a}
  .lnk.derive{stroke:#4a5568;stroke-dasharray:2 3} .lnk.bridge{stroke:#e5c07b;stroke-width:2.5}
  text{fill:#cfd3da;font-size:11px;pointer-events:none}
  .fase text{fill:#fff;font-size:13px;font-weight:600}
</style></head><body>
<div id="h"><b>altair-brain</b> &nbsp;<span>vista compatta &mdash; processo a 5 fasi, un nodo per area</span></div>
<div id="leg">
  <div><span class="sw" style="background:#6ea8fe"></span>processo (fasi)</div>
  __LEGEND_AREAS__
  <div><span class="sw" style="background:#f0a35e"></span>engine</div>
  <div><span class="sw" style="background:#9ad06a"></span>skill</div>
  <div><span class="sw" style="background:#e5c07b"></span>ponte intercampo</div>
</div>
<svg></svg>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const G = __DATA__;
const color = __COLORS__;
const svg = d3.select("svg"), W = innerWidth, H = innerHeight;
const g = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.2,4]).on("zoom", e => g.attr("transform", e.transform)));
const sim = d3.forceSimulation(G.nodes)
  .force("link", d3.forceLink(G.links).id(d=>d.id).distance(l=>l.kind==="flow"?130:l.kind==="bridge"?90:70).strength(0.5))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(W/2, H/2))
  .force("collide", d3.forceCollide(26));
const link = g.append("g").selectAll("line").data(G.links).join("line").attr("class", d=>"lnk "+d.kind);
const node = g.append("g").selectAll("g").data(G.nodes).join("g")
  .attr("class", d=>d.kind==="fase"?"fase":"")
  .call(d3.drag()
    .on("start",(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y;})
    .on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y;})
    .on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));
node.append("circle").attr("r", d=>d.size).attr("fill", d=>color[d.layer]||"#888")
  .attr("stroke","#0f1115").attr("stroke-width",1.5);
node.append("text").attr("x", d=>d.size+4).attr("y", 4).text(d=>d.label);
sim.on("tick", () => {
  link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  node.attr("transform", d=>`translate(${d.x},${d.y})`);
});
</script></body></html>
"""
HTML = (HTML.replace("__DATA__", DATA).replace("__COLORS__", color_js)
            .replace("__LEGEND_AREAS__", legend_areas))
with open(OUT_HTML, "w", encoding="utf-8", newline="\n") as f:
    f.write(HTML)

print("Vista compatta generata:")
print("  nodi:", len(nodes), " edge:", len(edges), " ponti intercampo:", bridge_count)
print("  aree:", ", ".join(f"{a}(raw {raw_count[a]}/wiki {wiki_count[a]})" for a in areas))
