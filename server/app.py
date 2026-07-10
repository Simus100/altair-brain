# -*- coding: utf-8 -*-
"""
altair-brain — API FastAPI v1.

Espone il second brain e graphify ad altri dispositivi/AI in modo sicuro ed
efficiente. Nessuna API a pagamento: il ragionamento LLM resta al client.

Sicurezza: token Bearer con confronto constant-time; rate limiting per IP;
subprocess senza shell; validazione input (aree, id inbox, seed); Velario inerte.
Endpoint sotto /v1/ (alias non versionati mantenuti per compatibilita).

Config (env / .env): ALTAIR_API_TOKEN (obbligatoria), ALTAIR_REPO_DIR, GRAPHIFY_BIN,
ALTAIR_MEMORY_DIR, ALTAIR_LESSONS, ALTAIR_INBOX_DIR, ALTAIR_UPDATE_SCRIPT,
ALTAIR_RATE_LIMIT (req/min per IP, default 120).

Avvio:  uvicorn server.app:app --host 127.0.0.1 --port 8000
        (dalla cartella runtime:  uvicorn app:app ...)
"""
import os, secrets, subprocess, time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

try:  # eseguito come pacchetto (server.app) o da cartella runtime (app)
    from . import brain_core as core
except ImportError:
    import brain_core as core

TOKEN = os.environ.get("ALTAIR_API_TOKEN")
RATE_LIMIT = int(os.environ.get("ALTAIR_RATE_LIMIT", "120"))  # req/min per IP

app = FastAPI(title="altair-brain API", version="2.0",
              description="Second brain + graphify. Auth Bearer. Velario inerte.")


def _err(e: core.BrainError):
    return HTTPException(e.status, e.detail)


# ---------------- auth (constant-time) ----------------
def auth(authorization: str = Header(None), x_api_key: str = Header(None)):
    if not TOKEN:
        raise HTTPException(503, "ALTAIR_API_TOKEN non configurato sul server.")
    supplied = ""
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()
    elif x_api_key:
        supplied = x_api_key.strip()
    if not secrets.compare_digest(supplied, TOKEN):
        raise HTTPException(401, "Token mancante o non valido.")
    return True


# ---------------- rate limiting per IP ----------------
_buckets = defaultdict(deque)

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    path = request.url.path
    if not path.endswith("/health"):
        ip = request.client.host if request.client else "?"
        now = time.time()
        q = _buckets[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return JSONResponse({"detail": "Rate limit superato, riprova tra poco."}, 429)
        q.append(now)
        if len(_buckets) > 10000:  # pulizia difensiva
            for k in [k for k, v in _buckets.items() if not v]:
                _buckets.pop(k, None)
    return await call_next(request)


api = APIRouter()


# ---------------- pubblico ----------------
@api.get("/health")
def health():
    return core.health_info()


# ---------------- dati del brain (sola lettura) ----------------
def _file(rel, media):
    f = core.REPO / rel
    if not f.exists():
        raise HTTPException(404, f"File non presente: {rel}")
    return FileResponse(str(f), media_type=media)

@api.get("/model", dependencies=[Depends(auth)])
def model():
    return _file("engine/aion.model.json", "application/json")

@api.get("/reasoner", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def reasoner():
    return _file("engine/aion-reasoner.md", "text/markdown")

@api.get("/graph", dependencies=[Depends(auth)])
def graph(area: str = Query(None, pattern="^[a-z0-9-]+$")):
    if area:
        try:
            return FileResponse(str(core.area_graph_path(area)), media_type="application/json")
        except core.BrainError as e:
            raise _err(e)
    return _file("graphify-out/graph.json", "application/json")

@api.get("/graph/compact", dependencies=[Depends(auth)])
def graph_compact():
    return _file("graphify-out/graph-compact.json", "application/json")

@api.get("/areas", dependencies=[Depends(auth)])
def areas():
    return {"aree_disponibili": core.valid_areas(), "router": core.load_router()}

@api.get("/lessons", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def lessons():
    return core.lessons_text()

@api.get("/views/extended", dependencies=[Depends(auth)])
def view_extended():
    return _file("graphify-out/graph.html", "text/html")

@api.get("/views/compact", dependencies=[Depends(auth)])
def view_compact():
    return _file("graphify-out/graph-compact.html", "text/html")


# ---------------- graphify (router per-area) ----------------
@api.get("/route", dependencies=[Depends(auth)])
def route(q: str = Query(..., min_length=1)):
    return core.route_question(q)

@api.get("/query", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def query(response: Response, q: str = Query(..., min_length=1),
          budget: int = Query(2000, ge=100, le=20000),
          area: str = Query(None, pattern="^[a-z0-9-]+$|^full$")):
    try:
        out, used = core.graph_query(q, budget=budget, area=area)
    except core.BrainError as e:
        raise _err(e)
    response.headers["X-Altair-Area"] = used
    return out

@api.get("/path", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def path(a: str = Query(..., min_length=1), b: str = Query(..., min_length=1)):
    try:
        return core.run_graphify(["path", a, b])
    except core.BrainError as e:
        raise _err(e)

@api.get("/explain", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def explain(x: str = Query(..., min_length=1)):
    try:
        return core.run_graphify(["explain", x])
    except core.BrainError as e:
        raise _err(e)

@api.get("/affected", response_class=PlainTextResponse, dependencies=[Depends(auth)])
def affected(x: str = Query(..., min_length=1), depth: int = Query(2, ge=1, le=5)):
    try:
        return core.run_graphify(["affected", x, "--depth", str(depth)])
    except core.BrainError as e:
        raise _err(e)


# ---------------- oracle (AION_Oracle eseguibile) ----------------
class OracleReq(BaseModel):
    question: str | None = None
    seed: int | None = None

@api.post("/oracle", dependencies=[Depends(auth)])
def oracle(req: OracleReq):
    try:
        return core.oracle_cast(req.question, req.seed)
    except core.BrainError as e:
        raise _err(e)

@api.get("/oracle/hexagram/{hid}", dependencies=[Depends(auth)])
def oracle_hexagram(hid: int):
    try:
        return core.oracle_hexagram(hid)
    except core.BrainError as e:
        raise _err(e)


# ---------------- inbox (cattura da ovunque) ----------------
class CaptureReq(BaseModel):
    text: str = Field(..., min_length=1)
    title: str | None = None
    area_hint: str | None = None
    source: str | None = None

@api.post("/capture", dependencies=[Depends(auth)])
def capture(req: CaptureReq):
    try:
        return core.capture(req.text, req.title, req.area_hint, req.source)
    except core.BrainError as e:
        raise _err(e)

@api.get("/inbox", dependencies=[Depends(auth)])
def inbox_list():
    return core.inbox_list()

@api.get("/inbox/{item_id}", dependencies=[Depends(auth)])
def inbox_read(item_id: str):
    try:
        return core.inbox_read(item_id)
    except core.BrainError as e:
        raise _err(e)

@api.post("/inbox/{item_id}/done", dependencies=[Depends(auth)])
def inbox_done(item_id: str):
    try:
        return core.inbox_done(item_id)
    except core.BrainError as e:
        raise _err(e)


# ---------------- feedback (apprendimento) ----------------
class Feedback(BaseModel):
    question: str
    answer: str
    outcome: str = "useful"
    type: str = "query"
    nodes: list[str] = []
    correction: str | None = None

@api.post("/feedback", dependencies=[Depends(auth)])
def feedback(fb: Feedback):
    try:
        detail = core.save_feedback(fb.question, fb.answer, fb.outcome, fb.type,
                                    fb.nodes, fb.correction)
    except core.BrainError as e:
        raise _err(e)
    return {"saved": True, "detail": detail}


# ---------------- admin ----------------
@api.post("/admin/update", dependencies=[Depends(auth)])
def admin_update():
    script = core.UPDATE_SCRIPT
    if not script.exists():
        raise HTTPException(404, f"Script di update non trovato: {script}")
    try:
        p = subprocess.run(["bash", str(script)], cwd=str(core.REPO),
                           capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "update: timeout.")
    return {"returncode": p.returncode, "stdout": p.stdout[-2000:], "stderr": p.stderr[-1000:]}


# /v1/... e alias non versionati (compatibilita)
app.include_router(api, prefix="/v1")
app.include_router(api)
