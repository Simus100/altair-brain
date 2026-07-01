# -*- coding: utf-8 -*-
"""
Client di test per l'API altair-brain. Usalo da qualunque dispositivo.

Uso:
  ALTAIR_URL=https://brain.tuodominio.it ALTAIR_TOKEN=xxxx python client_example.py
oppure:
  python client_example.py https://brain.tuodominio.it xxxx

Dipende solo dalla stdlib (urllib): nessun pacchetto extra.
"""
import os, sys, json, urllib.request, urllib.parse

BASE = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ALTAIR_URL", "http://127.0.0.1:8000")).rstrip("/")
TOKEN = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("ALTAIR_TOKEN", "")

def call(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode("utf-8", "replace")
            return r.status, txt
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)

def show(label, status, txt, limit=300):
    head = txt if len(txt) <= limit else txt[:limit] + " …"
    print(f"\n### {label}  ->  HTTP {status}\n{head}")

q = urllib.parse.quote
print(f"BASE = {BASE}   TOKEN = {'(impostato)' if TOKEN else '(mancante!)'}")
show("GET /health",            *call("GET", "/health"))
show("GET /model",             *call("GET", "/model"))
show("GET /graph/compact",     *call("GET", "/graph/compact"))
show("GET /query AION_SUPERIA", *call("GET", f"/query?q={q('quali componenti usa AION_STRATEGIC_ENGINE')}"))
show("GET /explain aion-superia", *call("GET", f"/explain?x={q('aion-superia')}"))
show("GET /path superia->analyst", *call("GET", f"/path?a={q('AION_SUPERIA')}&b={q('AION_Analyst')}"))
show("GET /lessons",           *call("GET", "/lessons"))
# esempio di feedback (commentato per non scrivere per sbaglio):
# show("POST /feedback", *call("POST", "/feedback", {
#     "question": "test dal client", "answer": "ok", "outcome": "useful", "nodes": ["AION_SUPERIA"]}))
print("\nTest completato.")
