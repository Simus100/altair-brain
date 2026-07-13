# -*- coding: utf-8 -*-
"""
altair-brain — scaffolding di un NUOVO report 3D living (nasce gia conforme).

Estrae il blueprint HTML dal template (reports/template_showcase_3d.md, Sez. 2),
sostituisce il titolo e crea:
  reports/<caso>.html                 fonte statica da personalizzare (nodi, contenuti)
  reports/data/<caso>.updates.json    database aggiornamenti (vuoto, con prima voce)

Poi: personalizza la fonte (Sez. 1 del template: nodes/nodeConnections/nodeIntelligence)
e genera il living report con  python tools/report_build.py --report <caso>

Uso:  python tools/report_new.py --caso mio-nuovo-caso --titolo "Titolo del Report"
"""
import argparse, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "reports", "template_showcase_3d.md")

ap = argparse.ArgumentParser()
ap.add_argument("--caso", required=True, help="slug kebab-case (es. altair-brain-energia-2026)")
ap.add_argument("--titolo", required=True, help="titolo del report")
a = ap.parse_args()

if not re.match(r"^[a-z0-9][a-z0-9-]*$", a.caso):
    sys.exit("--caso deve essere kebab-case (a-z, 0-9, trattini)")

src = os.path.join(ROOT, "reports", f"{a.caso}.html")
db = os.path.join(ROOT, "reports", "data", f"{a.caso}.updates.json")
for p in (src, db):
    if os.path.exists(p):
        sys.exit(f"esiste gia: {p} — scegli un altro --caso")

# 1. estrai il blueprint HTML dal template (il blocco ```html della Sez. 2)
md = open(TEMPLATE, encoding="utf-8").read()
m = re.search(r"```html\n(.*?)\n```", md, re.S)
if not m:
    sys.exit("blueprint ```html``` non trovato nel template")
html = m.group(1).replace("{{SHOWCASE_TITLE}}", a.titolo)

os.makedirs(os.path.dirname(db), exist_ok=True)
with open(src, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

# 2. database iniziale (prima voce datata adesso, mai date future)
now = datetime.datetime.now().replace(microsecond=0).isoformat()
with open(db, "w", encoding="utf-8", newline="\n") as f:
    json.dump({
        "report": a.caso,
        "titolo": a.titolo,
        "aggiornato_il": now,
        "verdetto": {
            "corrente": "Responso iniziale in elaborazione.",
            "storia": [{"ts": now, "testo": "Apertura del caso.", "autore": "redazione"}],
        },
        "nodi": {},   # riempi con gli id dei nodi della fonte: "<id>": []
    }, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Scaffold creato per '{a.caso}':")
print(f"  fonte:    reports/{a.caso}.html   (personalizza nodes/nodeIntelligence — Sez. 1 del template)")
print(f"  database: reports/data/{a.caso}.updates.json   (aggiungi gli id dei nodi in 'nodi')")
print(f"  poi:      python tools/report_build.py --report {a.caso}")
