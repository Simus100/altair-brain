## Roadmap

Le implementazioni pianificate (con spec complete, regole vincolanti del progetto e
criteri di accettazione) sono in **`ROADMAP.md`**: leggilo PRIMA di iniziare qualsiasi
nuova feature, e aggiornalo quando completi una voce.

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

Workflow dopo ogni modifica: **`python tools/rebuild_all.py`** (un comando: wiki dal
modello, validazioni, DB oracle, grafo, sottografi per area, viste, salute). Poi commit.
Regole: la wiki e GENERATA da `engine/aion.model.json` (mai editarla a mano); il DB
oracle e GENERATO da `raw/aion/aion-oracle.md`.

La CI (`.github/workflows/validate.yml`) ripete questi controlli su ogni push: i
consumatori (VPS, dispositivi) ricevono solo un brain valido.

Skill del brain: `/aion` (ragionamento col modello di pensiero), `/triage` (smista
l'inbox nelle macroaree), `/oracle` (I Ching eseguibile via tools/oracle_cast.py).
