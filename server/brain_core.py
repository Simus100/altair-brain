# -*- coding: utf-8 -*-
"""
altair-brain — nucleo condiviso tra API FastAPI (app.py) e server MCP (mcp_server.py).

Tutta la logica di accesso al brain vive qui, una volta sola:
config, esecuzione sicura di graphify (argomenti a lista, MAI shell), lettura file,
router per-area, oracle, inbox (con anti path-traversal), feedback, health.
Nessuna API a pagamento.
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path(os.environ.get("ALTAIR_REPO_DIR", Path(__file__).resolve().parent.parent))
GRAPHIFY = os.environ.get("GRAPHIFY_BIN", "graphify")
TIMEOUT = int(os.environ.get("ALTAIR_CMD_TIMEOUT", "120"))
MEMORY_DIR = Path(os.environ.get("ALTAIR_MEMORY_DIR", REPO / "graphify-out" / "memory"))
LESSONS = Path(os.environ.get("ALTAIR_LESSONS", REPO / "graphify-out" / "reflections" / "LESSONS.md"))
INBOX_DIR = Path(os.environ.get("ALTAIR_INBOX_DIR", REPO / "raw" / "_inbox"))
UPDATE_SCRIPT = Path(os.environ.get("ALTAIR_UPDATE_SCRIPT", REPO / "server" / "update_brain.sh"))

sys.path.insert(0, str(REPO))  # per: from tools.oracle_cast import ...

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.md$")
_SAFE_AREA = re.compile(r"^[a-z0-9-]+$")
MAX_CAPTURE_BYTES = 100_000


class BrainError(Exception):
    def __init__(self, status: int, detail: str):
        self.status, self.detail = status, detail
        super().__init__(detail)


# ---------------- graphify ----------------
def graphify_available() -> bool:
    return shutil.which(GRAPHIFY) is not None or Path(GRAPHIFY).exists()


def run_graphify(args: list) -> str:
    if not graphify_available():
        raise BrainError(503, "graphify non disponibile sul server.")
    try:
        p = subprocess.run([GRAPHIFY, *[str(a) for a in args]], cwd=str(REPO),
                           capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise BrainError(504, "graphify: timeout.")
    if p.returncode != 0:
        raise BrainError(500, f"graphify errore: {p.stderr.strip()[:500]}")
    return p.stdout


# ---------------- file del brain (sola lettura) ----------------
def read_repo_text(rel: str) -> str:
    f = REPO / rel
    if not f.exists():
        raise BrainError(404, f"File non presente: {rel}")
    return f.read_text(encoding="utf-8")


def read_repo_json(rel: str) -> dict:
    return json.loads(read_repo_text(rel))


def lessons_text() -> str:
    for f in (LESSONS, REPO / "graphify-out" / "reflections" / "LESSONS.md"):
        if Path(f).exists():
            return Path(f).read_text(encoding="utf-8")
    return "# Nessuna lezione ancora.\n"


# ---------------- router per-area ----------------
def load_router() -> dict:
    try:
        return read_repo_json("engine/router.json")
    except BrainError:
        return {"aree": {}}


def valid_areas() -> list:
    base = REPO / "graphify-out" / "areas"
    if not base.is_dir():
        return []
    return sorted(d.name for d in base.iterdir() if (d / "graph.json").exists())


def area_graph_path(area: str) -> Path:
    if not _SAFE_AREA.match(area or ""):
        raise BrainError(400, "Nome area non valido.")
    p = REPO / "graphify-out" / "areas" / area / "graph.json"
    if not p.exists():
        raise BrainError(404, f"Area '{area}' inesistente. Aree: {', '.join(valid_areas())}")
    return p


def route_question(q: str) -> dict:
    """Routing deterministico: match keyword per area. Nessun match -> grafo completo."""
    ql = (q or "").lower()
    best, best_score, matches = None, 0, []
    for area, cfg in load_router().get("aree", {}).items():
        hits = [k for k in cfg.get("keywords", []) if k.lower() in ql]
        if len(hits) > best_score:
            best, best_score, matches = area, len(hits), hits
    if best and best not in valid_areas():
        best = None  # area dichiarata ma sottografo non ancora generato
    return {"area": best, "score": best_score, "matches": matches}


def graph_query(q: str, budget: int = 2000, area: str = None) -> tuple:
    """Ritorna (output, area_usata). area=None -> router; 'full' -> grafo completo."""
    used = "full"
    args = ["query", q, "--budget", str(int(budget))]
    if area and area != "full":
        args += ["--graph", str(area_graph_path(area))]
        used = area
    elif area is None:
        r = route_question(q)
        if r["area"]:
            args += ["--graph", str(area_graph_path(r["area"]))]
            used = r["area"]
    return run_graphify(args), used


# ---------------- oracle ----------------
def oracle_cast(question: str = None, seed=None) -> dict:
    if seed is not None:
        try:
            seed = int(seed)
        except (TypeError, ValueError):
            raise BrainError(400, "seed deve essere un intero.")
    try:
        from tools.oracle_cast import cast_reading
    except Exception as e:
        raise BrainError(503, f"oracle non disponibile: {e}")
    return cast_reading(question=question, seed=seed)


def oracle_hexagram(hid: int) -> dict:
    try:
        from tools.oracle_cast import get_hexagram
        return {k: v for k, v in get_hexagram(int(hid)).items()}
    except KeyError:
        raise BrainError(404, "Esagramma inesistente (range 1-64).")
    except (TypeError, ValueError):
        raise BrainError(400, "id esagramma non valido.")
    except Exception as e:
        raise BrainError(503, f"oracle non disponibile: {e}")


# ---------------- inbox (cattura da ovunque) ----------------
def _safe_inbox_file(item_id: str) -> Path:
    if not _SAFE_ID.match(item_id or "") or ".." in item_id:
        raise BrainError(400, "id non valido.")
    p = (INBOX_DIR / item_id).resolve()
    if p.parent != INBOX_DIR.resolve():
        raise BrainError(400, "id non valido.")
    return p


def _slug(s: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:maxlen] or "nota"


def capture(text: str, title: str = None, area_hint: str = None, source: str = None) -> dict:
    if not text or not text.strip():
        raise BrainError(400, "text vuoto.")
    if len(text.encode("utf-8")) > MAX_CAPTURE_BYTES:
        raise BrainError(413, f"nota troppo grande (max {MAX_CAPTURE_BYTES} byte).")
    if area_hint and not _SAFE_AREA.match(area_hint):
        raise BrainError(400, "area_hint non valida.")
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    name = f"{ts}_{_slug(title or text[:40])}.md"
    front = ["---", f"date: {time.strftime('%Y-%m-%dT%H:%M:%S')}"]
    if title:
        front.append(f"title: {title}")
    if area_hint:
        front.append(f"area_hint: {area_hint}")
    if source:
        front.append(f"source: {source}")
    front.append("---")
    (INBOX_DIR / name).write_text("\n".join(front) + "\n\n" + text.strip() + "\n",
                                  encoding="utf-8", newline="\n")
    return {"id": name}


def inbox_list() -> list:
    if not INBOX_DIR.is_dir():
        return []
    out = []
    for f in sorted(INBOX_DIR.glob("*.md")):
        if f.name.upper().startswith("README"):
            continue
        head = f.read_text(encoding="utf-8")[:500]
        title = re.search(r"^title:\s*(.+)$", head, re.M)
        hint = re.search(r"^area_hint:\s*(.+)$", head, re.M)
        out.append({"id": f.name, "title": title.group(1) if title else None,
                    "area_hint": hint.group(1) if hint else None})
    return out


def inbox_read(item_id: str) -> dict:
    p = _safe_inbox_file(item_id)
    if not p.exists():
        raise BrainError(404, "nota inesistente.")
    return {"id": item_id, "content": p.read_text(encoding="utf-8")}


def inbox_done(item_id: str) -> dict:
    p = _safe_inbox_file(item_id)
    if not p.exists():
        raise BrainError(404, "nota inesistente.")
    arch = INBOX_DIR / "archive"
    arch.mkdir(parents=True, exist_ok=True)
    p.rename(arch / p.name)
    return {"archived": item_id}


# ---------------- feedback (apprendimento) ----------------
def save_feedback(question: str, answer: str, outcome: str = "useful",
                  ftype: str = "query", nodes: list = None, correction: str = None) -> str:
    if outcome not in ("useful", "dead_end", "corrected"):
        raise BrainError(400, "outcome deve essere useful|dead_end|corrected.")
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    args = ["save-result", "--question", question, "--answer", answer,
            "--type", ftype, "--outcome", outcome, "--memory-dir", str(MEMORY_DIR)]
    if nodes:
        args += ["--nodes", *nodes]
    if correction:
        args += ["--correction", correction]
    out = run_graphify(args)
    LESSONS.parent.mkdir(parents=True, exist_ok=True)
    run_graphify(["reflect", "--memory-dir", str(MEMORY_DIR), "--out", str(LESSONS),
                  "--graph", str(REPO / "graphify-out" / "graph.json")])
    return out.strip()


# ---------------- health ----------------
_health_cache = {"mtime": None, "data": None}

def health_info() -> dict:
    gpath = REPO / "graphify-out" / "graph.json"
    mtime = gpath.stat().st_mtime if gpath.exists() else None
    if _health_cache["mtime"] == mtime and _health_cache["data"]:
        return _health_cache["data"]
    graph = {}
    if gpath.exists():
        try:
            g = json.loads(gpath.read_text(encoding="utf-8"))
            graph = {"nodes": len(g.get("nodes", [])), "edges": len(g.get("links", [])),
                     "built_at_commit": g.get("built_at_commit"),
                     "age_seconds": int(time.time() - mtime)}
        except Exception:
            graph = {"error": "graph.json illeggibile"}
    model = {}
    try:
        m = read_repo_json("engine/aion.model.json")
        model = {"schema_version": m.get("schema_version"), "versione": m.get("versione")}
    except BrainError:
        model = {"error": "modello mancante"}
    data = {"status": "ok", "service": "altair-brain", "api_version": "v1",
            "graphify": graphify_available(), "graph": graph, "model": model,
            "areas": valid_areas()}
    _health_cache.update(mtime=mtime, data=data)
    return data
