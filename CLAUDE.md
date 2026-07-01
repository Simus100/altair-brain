## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Viste del grafo (processo standard)

Il sistema produce DUE viste affiancate del grafo:
- **Vista estesa** — `graphify-out/graph.html`, generata da `graphify update .` (tutti i nodi).
- **Vista compatta strutturale** — `graphify-out/graph-compact.html`, generata da
  `python tools/altair_compact_view.py` (estende graphify, non lo modifica). Mostra
  altair-brain come **processo a 5 fasi**: (1) Sorgenti `raw/` → (2) Modello `wiki/` →
  (3) Motore `engine/` → (4) Skill `/aion` → (5) Feedback `LESSONS`, con anello di
  ritorno. Collassa il rumore (es. i 64 esagrammi in un nodo). Deterministica, no API.

Workflow dopo ogni modifica (in ordine):
1. se hai toccato `engine/aion.model.json`: `python tools/gen_wiki_from_model.py` (la wiki
   e GENERATA dal modello — mai editarla a mano)
2. `python tools/validate_model.py` (deve dare 0 errori)
3. `graphify update .`
4. `python tools/altair_compact_view.py`

La CI (`.github/workflows/validate.yml`) ripete questi controlli su ogni push: i
consumatori (VPS, dispositivi) ricevono solo un brain valido.
