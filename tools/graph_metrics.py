# -*- coding: utf-8 -*-
"""
altair-brain — serie storica della salute del brain (P6).

PERCHE: "connection over collection" (Zettelkasten) e una massima inutile se non la
si misura. Un brain puo crescere di note e IMPOVERIRSI di collegamenti: nodi che
nessuno cita, aree che si isolano, community che si sbriciolano. Senza una serie
storica non te ne accorgi finche non e troppo tardi per rimediare a mano.

Scrive UNA riga al giorno in metrics/graph_metrics.csv (la riga del giorno viene
sostituita se rilanciato): file piccolo, diffabile, leggibile fra dieci anni.

Metriche chiave da guardare nel tempo:
  grado_medio      sale = il brain si connette; scende = si sta disperdendo
  archi_raw_wiki   la catena fonte->conoscenza regge?
  isolati          note che nessuno raggiunge (conoscenza morta)
  con_frontmatter  quanta conoscenza ha provenienza tracciata

Uso:  python tools/graph_metrics.py   (parte di rebuild_all.py)
"""
import collections, csv, datetime, json, os, subprocess
import sys

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
OUT_DIR = os.path.join(BRAIN, "metrics")
OUT = os.path.join(OUT_DIR, "graph_metrics.csv")

CAMPI = ["data", "commit", "nodi", "archi", "grado_medio", "isolati", "community",
         "archi_raw_wiki", "nodi_raw", "nodi_wiki", "nodi_engine",
         "note_md", "con_frontmatter", "lezioni"]


def strato(p):
    p = (p or "").replace("\\", "/")
    for s in ("raw/", "wiki/", "engine/"):
        if p.startswith(s):
            return s.rstrip("/")
    return None


with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)

nodi, archi = g["nodes"], g["links"]
sf = {n["id"]: (n.get("source_file") or "").replace("\\", "/") for n in nodi}

adj = collections.defaultdict(set)
for e in archi:
    s, t = e.get("source"), e.get("target")
    if s and t:
        adj[s].add(t)
        adj[t].add(s)

per_strato = collections.Counter(strato(v) for v in sf.values())
raw_wiki = sum(1 for e in archi
               if {strato(sf.get(e.get("source"), "")), strato(sf.get(e.get("target"), ""))}
               == {"raw", "wiki"})

# quante note hanno provenienza tracciata (front-matter)
note_md = con_fm = 0
for base in ("raw", "wiki", "reports"):
    for root, _, files in os.walk(os.path.join(BRAIN, base)):
        for f in files:
            if not f.endswith(".md"):
                continue
            note_md += 1
            try:
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    if fh.read(4).lstrip().startswith("---"):
                        con_fm += 1
            except (OSError, UnicodeDecodeError):
                pass

lezioni = 0
log = os.path.join(BRAIN, "engine", "lessons.jsonl")
if os.path.exists(log):
    with open(log, encoding="utf-8") as f:
        lezioni = sum(1 for r in f if r.strip())

try:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True, timeout=10).stdout.strip() or "?"
except Exception:
    commit = "?"

riga = {
    "data": datetime.date.today().isoformat(),
    "commit": commit,
    "nodi": len(nodi),
    "archi": len(archi),
    "grado_medio": round(sum(len(v) for v in adj.values()) / max(len(nodi), 1), 2),
    "isolati": sum(1 for n in nodi if not adj.get(n["id"])),
    "community": len({n.get("community") for n in nodi if n.get("community") is not None}),
    "archi_raw_wiki": raw_wiki,
    "nodi_raw": per_strato.get("raw", 0),
    "nodi_wiki": per_strato.get("wiki", 0),
    "nodi_engine": per_strato.get("engine", 0),
    "note_md": note_md,
    "con_frontmatter": con_fm,
    "lezioni": lezioni,
}

os.makedirs(OUT_DIR, exist_ok=True)
storico = []
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8", newline="") as f:
        storico = [r for r in csv.DictReader(f) if r.get("data") != riga["data"]]

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPI, lineterminator="\n")
    w.writeheader()
    for r in storico:
        w.writerow({k: r.get(k, "") for k in CAMPI})
    w.writerow(riga)

prec = storico[-1] if storico else None
delta = ""
if prec:
    try:
        d = round(float(riga["grado_medio"]) - float(prec["grado_medio"]), 2)
        delta = f" (grado medio {'+' if d >= 0 else ''}{d} dal {prec['data']})"
    except (ValueError, KeyError):
        pass

print(f"Metriche registrate: {riga['nodi']} nodi, {riga['archi']} archi, "
      f"grado medio {riga['grado_medio']}, {riga['archi_raw_wiki']} archi raw<->wiki, "
      f"{riga['con_frontmatter']}/{riga['note_md']} note con provenienza{delta}")
print(f"  serie storica: metrics/graph_metrics.csv ({len(storico) + 1} rilevazioni)")
