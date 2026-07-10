# -*- coding: utf-8 -*-
"""
altair-brain — aggiunge un aggiornamento a un report AION 'vivo'.

Il database e un JSON (reports/data/<report>.updates.json); questo tool vi appende una
voce {ts, testo} a un nodo o al verdetto, poi ri-sincronizza il blocco inline
#updates-db nel prototipo HTML (il JSON e la fonte di verita, l'HTML e uno specchio).
Deterministico, nessuna API.

Esempi:
  python tools/report_update.py --node nuclear --text "IAEA: nuova ispezione negata."
  python tools/report_update.py --verdict --text "Rivalutazione: ..." --set-current "Nuovo responso HTML..."
"""
import argparse, json, os, re, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("--report", default="altair-brain-iran-2026")
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--node", help="id del nodo (es. nuclear, economy, ...)")
g.add_argument("--verdict", action="store_true", help="aggiorna il verdetto/responso")
ap.add_argument("--text", required=True, help="testo dell'aggiornamento")
ap.add_argument("--ts", default=None, help="timestamp ISO (default: adesso)")
ap.add_argument("--set-current", default=None, help="(solo --verdict) nuova considerazione corrente (HTML)")
a = ap.parse_args()

db_path = os.path.join(ROOT, "reports", "data", f"{a.report}.updates.json")
proto = os.path.join(ROOT, "reports", f"{a.report}-prototype.html")
if not os.path.exists(db_path):
    sys.exit(f"database inesistente: {db_path}")

with open(db_path, encoding="utf-8") as f:
    db = json.load(f)

ts = a.ts or datetime.datetime.now().replace(microsecond=0).isoformat()
entry = {"ts": ts, "testo": a.text}

if a.verdict:
    db.setdefault("verdetto", {}).setdefault("storia", []).append(entry)
    if a.set_current:
        db["verdetto"]["corrente"] = a.set_current
    target = "verdetto"
else:
    nodi = db.setdefault("nodi", {})
    if a.node not in nodi:
        sys.exit(f"nodo '{a.node}' inesistente. Nodi: {', '.join(nodi.keys())}")
    nodi[a.node].append(entry)
    target = f"nodo {a.node}"

db["aggiornato_il"] = ts

with open(db_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
    f.write("\n")

# ri-sincronizza il blocco inline nel prototipo HTML (JSON = fonte di verita)
if os.path.exists(proto):
    h = open(proto, encoding="utf-8").read()
    new_json = json.dumps(db, ensure_ascii=False, indent=2)
    pat = re.compile(r'(<script type="application/json" id="updates-db">).*?(</script>)', re.S)
    if pat.search(h):
        h = pat.sub(lambda m: m.group(1) + new_json + m.group(2), h, count=1)
        open(proto, "w", encoding="utf-8").write(h)
        synced = "prototipo HTML ri-sincronizzato"
    else:
        synced = "ATTENZIONE: blocco #updates-db non trovato nel prototipo"
else:
    synced = "prototipo HTML non presente (solo DB aggiornato)"

print(f"Aggiornamento aggiunto a {target} ({ts}).")
print(" ", synced)
