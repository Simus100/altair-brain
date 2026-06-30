# -*- coding: utf-8 -*-
"""
altair-brain — generatore della VISTA COMPATTA STRUTTURALE.

Estende graphify (NON lo modifica): legge graphify-out/graph.json e produce una vista
compatta che mostra altair-brain come PROCESSO a 5 fasi (sorgenti -> modello -> motore
-> skill -> feedback), collassando il rumore (es. i 64 esagrammi I Ching in un nodo).

Output (accanto a graph.html, che resta intatto):
  - graphify-out/graph-compact.json
  - graphify-out/graph-compact.html   (interattivo, D3, colorato per fase)

Deterministico, nessuna API. Uso:  python tools/altair_compact_view.py
"""
import json, os, html, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
OUT_JSON = os.path.join(ROOT, "graphify-out", "graph-compact.json")
OUT_HTML = os.path.join(ROOT, "graphify-out", "graph-compact.html")

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)

id2sf = {n["id"]: n.get("source_file", "") for n in g["nodes"]}

def collapse(nid):
    """Mappa un nodo originale al suo nodo compatto."""
    sf = id2sf.get(nid, "")
    if sf == "raw/aion/aion-oracle.md":
        return "grp:iching"
    if sf.startswith("raw/aion/") and sf.endswith(".md") and "README" not in sf:
        stem = sf.split("/")[-1][:-3]
        return "doc:" + stem
    if sf.startswith("wiki/aion/insegnamento-"):
        return "grp:insegnamenti"
    if sf.startswith("wiki/aion/"):
        return "wiki:" + sf.split("/")[-1][:-3]
    if sf.startswith("engine/"):
        return "eng:" + sf.split("/")[-1]
    return None  # fuori scope per la vista compatta

# nodi compatti reali (derivati dal grafo)
real = {}
for n in g["nodes"]:
    c = collapse(n["id"])
    if c:
        real.setdefault(c, 0)
        real[c] += 1

# etichette leggibili
def label_for(cid):
    if cid == "grp:iching": return "I Ching DB (64 esagrammi)"
    if cid == "grp:insegnamenti": return "26 Insegnamenti"
    if cid.startswith("doc:"): return cid[4:]
    if cid.startswith("wiki:"): return cid[5:]
    if cid.startswith("eng:"): return cid[4:]
    return cid

def layer_for(cid):
    if cid.startswith("doc:") or cid == "grp:iching": return "raw"
    if cid.startswith("wiki:") or cid == "grp:insegnamenti": return "wiki"
    if cid.startswith("eng:"): return "engine"
    return "altro"

# edge compatti dal grafo (collassati e dedup)
edge_set = set()
for e in g["links"]:
    a, b = collapse(e["source"]), collapse(e["target"])
    if a and b and a != b:
        edge_set.add(tuple(sorted((a, b))))

# ---- backbone di PROCESSO (5 fasi) ----
phases = [
    ("fase:1", "(1) Sorgenti — raw/", "processo"),
    ("fase:2", "(2) Modello — wiki/", "processo"),
    ("fase:3", "(3) Motore — engine/", "processo"),
    ("fase:4", "(4) Skill /aion", "processo"),
    ("fase:5", "(5) Feedback — LESSONS", "processo"),
]
nodes = []
seen = set()
def add_node(nid, label, layer, kind="dato"):
    if nid in seen: return
    seen.add(nid)
    nodes.append({"id": nid, "label": label, "layer": layer, "kind": kind,
                  "size": (16 if layer == "processo" else 7)})

for pid, plab, lay in phases:
    add_node(pid, plab, lay, kind="fase")
for cid in real:
    add_node(cid, label_for(cid), layer_for(cid))
# nodi di processo non presenti nel grafo
add_node("skill:aion", "/aion (SKILL.md)", "engine")

edges = []
def add_edge(a, b, kind="rel"):
    edges.append({"source": a, "target": b, "kind": kind})

# catena delle fasi + anello di feedback
for i in range(len(phases) - 1):
    add_edge(phases[i][0], phases[i+1][0], kind="flow")
add_edge("fase:5", "fase:2", kind="loop")  # il feedback rientra nel modello/ragionamento

# aggancio dei cluster reali alle fasi
for cid in real:
    lay = layer_for(cid)
    if lay == "raw": add_edge("fase:1", cid, kind="has")
    elif lay == "wiki": add_edge("fase:2", cid, kind="has")
    elif lay == "engine": add_edge("fase:3", cid, kind="has")
add_edge("fase:4", "skill:aion", kind="has")
add_edge("fase:3", "skill:aion", kind="rel")

# relazioni interne del modello (collassate)
for a, b in edge_set:
    add_edge(a, b, kind="rel")

compact = {"nodes": nodes, "links": edges,
           "meta": {"generato_da": "tools/altair_compact_view.py",
                    "fonte": "graphify-out/graph.json",
                    "descrizione": "Vista compatta strutturale di altair-brain come processo a 5 fasi."}}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(compact, f, ensure_ascii=False, indent=2)

# ---- HTML interattivo (D3 v7, self-contained tranne la lib da CDN) ----
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
  text{fill:#cfd3da;font-size:11px;pointer-events:none}
  .fase text{fill:#fff;font-size:13px;font-weight:600}
</style></head><body>
<div id="h"><b>altair-brain</b> &nbsp;<span>vista compatta &mdash; il sistema come processo a 5 fasi</span></div>
<div id="leg">
  <div><span class="sw" style="background:#6ea8fe"></span>processo (fasi)</div>
  <div><span class="sw" style="background:#7ed0a8"></span>raw &mdash; sorgenti</div>
  <div><span class="sw" style="background:#c39bf0"></span>wiki &mdash; modello</div>
  <div><span class="sw" style="background:#f0a35e"></span>engine &mdash; motore</div>
</div>
<svg></svg>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const G = __DATA__;
const color = {processo:"#6ea8fe", raw:"#7ed0a8", wiki:"#c39bf0", engine:"#f0a35e", altro:"#888"};
const svg = d3.select("svg"), W = innerWidth, H = innerHeight;
const g = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.2,4]).on("zoom", e => g.attr("transform", e.transform)));
const sim = d3.forceSimulation(G.nodes)
  .force("link", d3.forceLink(G.links).id(d=>d.id).distance(l=>l.kind==="flow"?120:70).strength(0.5))
  .force("charge", d3.forceManyBody().strength(-260))
  .force("center", d3.forceCenter(W/2, H/2))
  .force("collide", d3.forceCollide(22));
const link = g.append("g").selectAll("line").data(G.links).join("line")
  .attr("class", d=>"lnk "+d.kind);
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
HTML = HTML.replace("__DATA__", DATA)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(HTML)

print("Vista compatta generata:")
print("  nodi compatti:", len(nodes), " edge:", len(edges))
print("  ->", os.path.relpath(OUT_JSON, ROOT))
print("  ->", os.path.relpath(OUT_HTML, ROOT))
