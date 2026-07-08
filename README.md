# Altair Brain

**An operational second brain that AIs reason *with* — not just a knowledge graph they read.**

**Un second brain operativo con cui le AI ragionano — non solo un grafo di conoscenza che leggono.**

altair-brain turns a knowledge graph into a living, servable, self-maintaining brain:
organized knowledge across domains, **executable thinking models**, multi-channel access
for AI assistants, and automated quality gates that keep it correct as it grows.
**No paid API is required to run it** — the pipeline is deterministic; LLM reasoning stays
with the client.

> Built on top of [graphify](https://github.com/safishamsi/graphify) (the graph-extraction
> engine). This project is the *architecture around it* that makes the knowledge
> operational, servable, and durable.

---

## What makes it different from graphify

graphify maps a corpus into a navigable knowledge graph (query / path / explain, community
structure, cross-file relations). altair-brain uses that as its graph engine and builds a
whole system on top.

| | graphify | **altair-brain** |
|---|---|---|
| **Nature** | A knowledge-graph engine (a tool) | A second-brain **architecture** built on it |
| **Knowledge** | Extracts a graph from a corpus | Organizes it into **routed macro-areas** + curated **cross-area bridges** |
| **Reasoning** | Query/path/explain over the graph | **Executable thinking models**: typed model + reasoner protocol + invokable skill |
| **Access** | CLI / AI-assistant integration | **Multi-channel**: local AI, FastAPI (`/v1`), MCP server, Custom GPT |
| **Source of truth** | The extracted graph | A **typed model that generates** the wiki (CI fails if they diverge) |
| **Durability** | — | CI quality gates, self-updating deployment, feedback loop, backups |
| **Cost** | LLM for semantic naming | **Deterministic, no paid API** required to function |

**In one line:** *graphify maps knowledge into a graph; altair-brain turns that graph into
an operational brain that AIs think with — and keeps it correct over time.*

---

## Architecture — the system as a 5-phase process

```
(1) Sources        (2) Model          (3) Engine         (4) Skills        (5) Feedback
   raw/      ───▶     wiki/     ───▶    engine/    ───▶   /aion /oracle ──▶  LESSONS
 grezzo,           generated,        typed model +       reasoning &        learns from
 per area          interlinked       reasoner protocol   oracle, triage     outcomes
     ▲                                                                          │
     └──────────────────────────  feedback loop  ◀──────────────────────────────┘
```

- **Macro-areas** (`areas.json`) with a **deterministic router**: a query is scoped to the
  right area subgraph — *performance and security by construction* (scope = which file you
  may read, not a filter on results).
- **Curated cross-area bridges** (`engine/bridges.json`) connect domains explicitly, so
  distinct fields start to inform each other.

## Technical characteristics

- **No paid API to function** — deterministic pipeline (data + instructions). Executable
  domains (e.g. the I Ching oracle) are pure logic; LLM reasoning is the client's.
- **Single source of truth** — a typed model (`engine/aion.model.json`) *generates* the
  navigable wiki; CI blocks any divergence. No hand-maintained duplication.
- **Secured multi-channel serving** — constant-time token auth, per-IP rate limiting,
  per-area scope, input validation (path-traversal safe), a governance module kept inert.
- **Self-maintaining** — CI quality gates on every push (model consistency, JSON schema,
  graph cohesion, no broken relations, API tests); the deployment auto-aligns on a schedule;
  failure notifications and rotating backups.
- **Learns over time** — a feedback loop distills lessons the reasoner consults before
  answering.
- **Scalable** — adding a domain is a folder + one registry line; the guards generalize
  automatically to every area.

## How AIs interface with it

- **Local AI assistants** (Claude Code, Antigravity, …) — clone the repo; reason via the
  `/aion` skill and the graph.
- **Any MCP client** (Claude Desktop, …) — native tools through `server/mcp_server.py`.
- **Over the network** — FastAPI (`server/app.py`, `/v1` endpoints) with token + HTTPS;
  Custom GPT via the generated `/openapi.json`.
- **Directly** — read `engine/aion.model.json` (typed) and `engine/aion-reasoner.md`
  (the reasoning protocol). Everything is a stable, machine-readable contract.

## Inside the brain (domains)

- **AION** — an *executable* thinking model, not just a documented one: four logical levels,
  orchestrating agents, functional components, operating modes, cross-cutting teachings, and
  a runnable I Ching **oracle** (correct King-Wen mathematics, deterministic). The model is
  navigable, validated, and drives an invokable reasoning skill.
- **Data science** — an *analyst intelligence*: transferable methodologies (data-quality
  checks, feature engineering, an analytical-question framework, report structure) **extracted
  from real projects**. It knows the *how*, not just the *what* — so it can approach a new
  dataset the way an analyst would.

## Visualizzazione 3D (Showcases)

altair-brain dispone di un sistema di presentazione interattivo WebGL-free per esporre le analisi strategiche prodotte tramite un **Cervello Neurale 3D** navigabile integrato con l'Oracolo AION.
- **Template Schema:** [raw/template_showcase_3d.md](file:///C:/Users/mace/altair-brain/raw/template_showcase_3d.md) definisce le specifiche dati (JSON per nodi e relazioni) ed il blueprint HTML/CSS/JS nativo (con rendering proiettivo 3D in tempo reale) per generare console di controllo offline ad alte prestazioni per mobile e desktop.

## Repository layout

```
raw/<area>/       grezzo sources per macro-area (e template globali in raw/)
wiki/<area>/      interlinked model (generated for AION)  engine/         typed model + reasoner + router + bridges
tools/            deterministic pipeline (rebuild, guards, views)         server/  FastAPI + MCP + deploy
.github/          CI quality gates                        graphify-out/   graph + visual views
```

- **`GUIDA.md`** — everyday use (human, non-technical).
- **`ROADMAP.md`** — engineering handoff (binding rules + specs) for any future contributor/agent.
- **`server/README.md`** — API reference, MCP, and VPS deployment.
- **`raw/template_showcase_3d.md`** — Schema riutilizzabile per dashboard neurali 3D.

## Status

Two connected areas live (AION thinking-model, data-science analyst), multi-channel serving,
CI-guarded, self-updating deployment. Growing by design.

---

Built on [graphify](https://github.com/safishamsi/graphify) · MIT licensed.
