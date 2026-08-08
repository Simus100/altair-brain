# -*- coding: utf-8 -*-
"""
altair-brain — server MCP (stdio): il brain come tool nativi per qualsiasi
assistente AI compatibile MCP (Claude Desktop, ecc.). Gira in locale dove il repo
e clonato: nessuna rete, nessun token, nessuna API a pagamento.

Requisiti:  pip install mcp
Config Claude Desktop (claude_desktop_config.json):
{ "mcpServers": { "altair-brain": {
    "command": "python",
    "args": ["<PERCORSO>/altair-brain/server/mcp_server.py"],
    "env": {"ALTAIR_REPO_DIR": "<PERCORSO>/altair-brain"} } } }
"""
import json

from mcp.server.fastmcp import FastMCP

try:
    from . import brain_core as core
except ImportError:
    import brain_core as core

mcp = FastMCP("altair-brain")


def _safe(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except core.BrainError as e:
        return f"[errore {e.status}] {e.detail}"


@mcp.tool()
def brain_query(q: str, area: str = "", budget: int = 2000) -> str:
    """Interroga il knowledge graph del brain (BFS scopato). area: vuota = router
    automatico; 'full' = grafo completo; oppure un id area (es. 'aion', 'core')."""
    def run():
        out, used = core.graph_query(q, budget=budget, area=(area or None))
        return f"[area: {used}]\n{out}"
    return _safe(run)


@mcp.tool()
def brain_search(q: str, top: int = 8, area: str = "") -> str:
    """Cerca nel CONTENUTO delle note (BM25 + semantico se attivo). Complementare a
    brain_query, che naviga la struttura: questa legge il testo, inclusi i .txt che
    il grafo non indicizza. Usala quando cerchi un concetto, non un nome preciso."""
    def run():
        r = core.search(q, top=top, area=(area or None))
        d = r.get("diagnosi", {})
        if not r["risultati"]:
            return f"Nessun risultato per {q!r}. {d.get('motivo', '')}"
        righe = [f"{len(r['risultati'])} risultati per {q!r}",
                 f"CONFIDENZA {d.get('confidenza', '?').upper()}: {d.get('motivo', '')}"]
        if d.get("confidenza") in ("bassa", "nessuna"):
            righe.append("(attenzione: il brain potrebbe non contenere questa "
                         "conoscenza — non dedurne una risposta certa)")
        for i, x in enumerate(r["risultati"], 1):
            riga = f"{i}. [{x['area']}] {x['titolo']} — {x['file']}"
            if x.get("memoria"):
                riga += f"\n   memoria: {x['memoria']['nota']}"
            righe.append(f"{riga}\n   {x['estratto']}")
        return "\n".join(righe)
    return _safe(run)


@mcp.tool()
def brain_explain(x: str) -> str:
    """Spiega un nodo del grafo e i suoi collegamenti (graphify explain)."""
    return _safe(core.run_graphify, ["explain", x])


@mcp.tool()
def brain_path(a: str, b: str) -> str:
    """Percorso piu breve tra due nodi del grafo (graphify path)."""
    return _safe(core.run_graphify, ["path", a, b])


@mcp.tool()
def brain_model() -> str:
    """Il modello di pensiero AION tipizzato (engine/aion.model.json)."""
    return _safe(core.read_repo_text, "engine/aion.model.json")


@mcp.tool()
def brain_reasoner() -> str:
    """Il protocollo di ragionamento AION a 9 passi (engine/aion-reasoner.md)."""
    return _safe(core.read_repo_text, "engine/aion-reasoner.md")


@mcp.tool()
def brain_lessons() -> str:
    """Le lezioni apprese dal brain (LESSONS.md, feedback loop)."""
    return core.lessons_text()


@mcp.tool()
def brain_oracle(question: str = "", seed: int = -1) -> str:
    """Lancio I Ching (AION_Oracle eseguibile). seed >= 0 per un lancio riproducibile."""
    def run():
        r = core.oracle_cast(question or None, seed if seed >= 0 else None)
        return json.dumps(r, ensure_ascii=False, indent=2)
    return _safe(run)


@mcp.tool()
def brain_feedback(question: str, answer: str, outcome: str = "useful") -> str:
    """Registra l'esito di una risposta (useful|dead_end|corrected): il brain impara."""
    return _safe(core.save_feedback, question, answer, outcome)


if __name__ == "__main__":
    mcp.run()
