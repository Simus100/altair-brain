# -*- coding: utf-8 -*-
"""
altair-brain — API FastAPI.

Espone il second brain e le funzionalita di graphify ad altri dispositivi, in modo
sicuro e SENZA API a pagamento (graphify gira in locale come binario; il ragionamento
LLM resta a carico del client, es. OpenClaw/GPT).

Config via variabili d'ambiente:
  ALTAIR_API_TOKEN   (obbligatoria)  token Bearer per autenticare le richieste
  ALTAIR_REPO_DIR    (default: cartella padre di server/)  radice del repo
  GRAPHIFY_BIN       (default: "graphify")  percorso/eseguibile graphify

Avvio:  uvicorn server.app:app --host 127.0.0.1 --port 8000
"""
import os, subprocess, shutil
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import PlainTextResponse, JSONResponse, FileResponse
from pydantic import BaseModel

REPO = Path(os.environ.get("ALTAIR_REPO_DIR", Path(__file__).resolve().parent.parent))
GRAPHIFY = os.environ.get("GRAPHIFY_BIN", "graphify")
TOKEN = os.environ.get("ALTAIR_API_TOKEN")
TIMEOUT = int(os.environ.get("ALTAIR_CMD_TIMEOUT", "120"))
# Dati scrivibili TENUTI FUORI dal repo (così l'auto-update git non entra in conflitto):
MEMORY_DIR = os.environ.get("ALTAIR_MEMORY_DIR", str(REPO / "graphify-out" / "memory"))
LESSONS = os.environ.get("ALTAIR_LESSONS", str(REPO / "graphify-out" / "reflections" / "LESSONS.md"))
UPDATE_SCRIPT = os.environ.get("ALTAIR_UPDATE_SCRIPT", str(REPO / "server" / "update_brain.sh"))

app = FastAPI(title="altair-brain API", version="1.0",
              description="Second brain + graphify, esposto in modo sicuro. Velario inerte.")


def auth(authorization: str = Header(None), x_api_key: str = Header(None)):
    """Richiede Bearer token o X-API-Key. /health e esente."""
    if not TOKEN:
        raise HTTPException(503, "ALTAIR_API_TOKEN non configurato sul server.")
    supplied = None
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()
    elif x_api_key:
        supplied = x_api_key.strip()
    if supplied != TOKEN:
        raise HTTPException(401, "Token mancante o non valido.")
    return True


def graphify_available() -> bool:
    return shutil.which(GRAPHIFY) is not None or Path(GRAPHIFY).exists()


def run_graphify(args: list[str]) -> str:
    """Esegue graphify con argomenti come LISTA (niente shell -> niente injection)."""
    if not graphify_available():
        raise HTTPException(503, "graphify non disponibile sul server (build Linux mancante).")
    try:
        p = subprocess.run([GRAPHIFY, *args], cwd=str(REPO),
                           capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "graphify: timeout.")
    if p.returncode != 0:
        raise HTTPException(500, f"graphify errore: {p.stderr.strip()[:500]}")
    return p.stdout


def serve_file(relpath: str, media_type: str):
    f = REPO / relpath
    if not f.exists():
        raise HTTPException(404, f"File non presente: {relpath}")
    return FileResponse(str(f), media_type=media_type)


# ---------------- pubblico ----------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "altair-brain", "graphify": graphify_available()}


# ---------------- dati del brain (sola lettura) ----------------
@app.get("/model", dependencies=[Depends(auth)])
def model():
    return serve_file("engine/aion.model.json", "application/json")

@app.get("/reasoner", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def reasoner():
    return serve_file("engine/aion-reasoner.md", "text/markdown")

@app.get("/graph", dependencies=[Depends(auth)])
def graph():
    return serve_file("graphify-out/graph.json", "application/json")

@app.get("/graph/compact", dependencies=[Depends(auth)])
def graph_compact():
    return serve_file("graphify-out/graph-compact.json", "application/json")

@app.get("/lessons", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def lessons():
    f = Path(LESSONS)
    if not f.exists():
        f = REPO / "graphify-out/reflections/LESSONS.md"
    return f.read_text(encoding="utf-8") if f.exists() else "# Nessuna lezione ancora.\n"

@app.get("/views/extended", dependencies=[Depends(auth)])
def view_extended():
    return serve_file("graphify-out/graph.html", "text/html")

@app.get("/views/compact", dependencies=[Depends(auth)])
def view_compact():
    return serve_file("graphify-out/graph-compact.html", "text/html")


# ---------------- funzioni graphify (sola lettura, gratis) ----------------
@app.get("/query", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def query(q: str = Query(..., min_length=1), budget: int = 2000):
    return run_graphify(["query", q, "--budget", str(budget)])

@app.get("/path", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def path(a: str = Query(..., min_length=1), b: str = Query(..., min_length=1)):
    return run_graphify(["path", a, b])

@app.get("/explain", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def explain(x: str = Query(..., min_length=1)):
    return run_graphify(["explain", x])

@app.get("/affected", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def affected(x: str = Query(..., min_length=1), depth: int = 2):
    return run_graphify(["affected", x, "--depth", str(depth)])


# ---------------- feedback (apprendimento, gratis) ----------------
class Feedback(BaseModel):
    question: str
    answer: str
    outcome: str = "useful"      # useful | dead_end | corrected
    type: str = "query"
    nodes: list[str] = []
    correction: str | None = None

@app.post("/feedback", dependencies=[Depends(auth)])
def feedback(fb: Feedback):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    args = ["save-result", "--question", fb.question, "--answer", fb.answer,
            "--type", fb.type, "--outcome", fb.outcome, "--memory-dir", MEMORY_DIR]
    if fb.nodes:
        args += ["--nodes", *fb.nodes]
    if fb.correction:
        args += ["--correction", fb.correction]
    out = run_graphify(args)
    os.makedirs(os.path.dirname(LESSONS), exist_ok=True)
    run_graphify(["reflect", "--memory-dir", MEMORY_DIR, "--out", LESSONS,
                  "--graph", str(REPO / "graphify-out" / "graph.json")])
    return {"saved": True, "detail": out.strip()}


# ---------------- admin: aggiornamento manuale ----------------
@app.post("/admin/update", dependencies=[Depends(auth)])
def admin_update():
    script = Path(UPDATE_SCRIPT)
    if not script.exists():
        raise HTTPException(404, f"Script di update non trovato: {UPDATE_SCRIPT}")
    try:
        p = subprocess.run(["bash", str(script)], cwd=str(REPO),
                           capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "update: timeout.")
    return JSONResponse({"returncode": p.returncode,
                         "stdout": p.stdout[-2000:], "stderr": p.stderr[-1000:]})
