# User guide — working with a brain day to day

> Paths such as `engine/…`, `raw/…` and `wiki/…` are inside the brain you are using
> (`python tools/brain.py` prints which one: `brains/starter` on a fresh clone). Run
> every command from the repository root.

> This guide covers daily use. The overview is in `README.md`, technical specs in
> `ROADMAP.md`, VPS deployment in `server/README.md`. Command-line flags are in
> Italian (`--nome`, `--aree`, `--domanda`); they are shown here exactly as typed.

---

## What a brain is

A brain is a folder of Markdown files.
- Raw sources go in `raw/<area>/`, curated pages in `wiki/<area>/`.
- The pipeline builds a graph and a search index from them, which an AI assistant can
  query from the terminal, over MCP or over HTTP.
- If a VPS is connected, every push reaches it at the next automatic update.
- No paid API: graph, search and views are all built locally.

---

## Everyday tasks

### 1. Add knowledge from your computer
Put the file in `raw/_inbox/`, or straight into `raw/<area>/` if you already know where
it belongs. Then open the agent (Claude Code) and say:

> triage    *(or "smista l'inbox": runs the `/triage` skill)*

or, if the files are already in place:

> rebuild the brain and publish

The agent runs `python tools/rebuild_all.py`, which validates the brain and regenerates
graph, subgraphs, views and health checks in one pass, then commits and pushes.

### 2. Capture an idea from your phone
With the VPS running, send one request to the API. Save it once as an iOS Shortcut or
an Android automation:

```
POST https://YOUR-DOMAIN/v1/capture
Authorization: Bearer YOUR-TOKEN
{"text": "the idea I just had", "title": "short title"}
```

The note lands in the VPS inbox. The next time you sort the inbox from your computer,
the agent fetches it, assigns it to an area and archives it.

### 3. Query the brain

There are two engines, for two kinds of question:

| You are looking for… | Use | Why |
|---|---|---|
| an **exact name**, or how things connect | `graphify query "..."` | walks the **structure**: nodes and relationships |
| a **concept**, in your own words | `python tools/search.py "..."` | searches the **text**, including `.txt` notes the graph does not see |

- **From the agent:** ask ("what does the brain know about X?"). With the AION training
  you can use `/aion <question>` for reasoning guided by its protocol.
- **From the terminal:**
  - structure → `graphify query "question"` (`--graph graphify-out/areas/<area>/graph.json` for one area)
  - content → `python tools/search.py "question" --area <area> --top 5`
- **From other devices:** `GET /v1/query?q=...` (graph, with automatic area routing)
  and `GET /v1/search?q=...` (content). Both need the token.

> Search works out of the box in **lexical** mode (BM25, no dependencies). For
> **semantic** search, which also matches different wording:
> `pip install sentence-transformers`, then `python tools/build_dense_index.py`.
> From then on the two rankings are fused. The package is about 2 GB.

### 4. Consult the oracle (AION only)
From the agent: `/oracle <question>`. A cast produces six lines, looks up the hexagram
in the King Wen sequence and works out the moving lines and the transformed hexagram;
the reading follows the AION protocol.
From the API: `POST /v1/oracle` with `{"question": "..."}`.

### 5. Teach the brain
Skills log a lesson when they finish. You can also log one by hand:

```bash
python tools/lesson_log.py --skill manuale --domanda "what I was looking for" --esito utile --nota "what to remember"
```

Outcomes are `utile` (useful), `vicolo-cieco` (dead end), `corretto` (corrected) and
`aperto` (open). This records an observation. To make it a rule, add `--quando` (when),
`--allora` (then) and `--ancora` (anchor): an external check such as a test, an error,
a measurement or your own correction. Full instructions are in `CLAUDE.md`. Everything
is collected in `engine/LESSONS.md`, which the agent reads before answering.

### 6. Look at the graph and the brain's health
- `graphify-out/index.html` is the entry page: it lists the three views and says which
  question each one answers.
- `graphify-out/graph.html`: extended view, every node.
- `graphify-out/graph-compact.html`: compact view, the system as a five-stage process.
- `graphify-out/graph-atlas.html`: the 3D atlas, the one to open when you need to find
  your way. Height is the layer (sources → knowledge → engine → use), the slice is the
  area, distance from the axis is how connected a file is. Double-click to fly to a
  node, press `L` to isolate its two-step neighbourhood.
- Remotely: `GET /v1/views/compact` or `/v1/views/atlas` with the token.
- `metrics/graph_metrics.csv`: how the brain changes over time. If `grado_medio`
  (average degree) falls while the node count rises, you are adding unconnected notes.

---

## Maintenance (occasionally, not daily)

| Command | What it tells you | When |
|---|---|---|
| `python tools/freshness_report.py` | what has expired and what you have not reviewed for too long | monthly |
| `python tools/check_provenance.py` | claims with figures and no source | before publishing a report |
| `python tools/link_suggest.py` | missing links between related pages | after adding notes |
| `python tools/add_frontmatter.py` | notes without provenance (preview; `--apply` to write) | after an import |
| `python tools/check_privacy.py` | what you are about to make public (emails, secrets, concentration) | **before every significant push** |
| `python tools/resurface.py` | 3 notes to reread, isolated ones first | weekly |
| `python tools/consolidate.py` | per-area digest and what to prune | monthly |

None of these edits your notes: they propose, you decide. `link_suggest` never writes,
because a wrong link added automatically would go unnoticed.

## Capture a web source

```bash
graphify add https://example.com/article --author "Author" --contributor "me"
```

This downloads the page into `raw/`, records author and contributor, and updates the
graph. The source stays in the brain even if the original link stops working. Then add
provenance with `python tools/add_frontmatter.py --apply` and rebuild with `rebuild_all`.

> ⚠️ If the brain ends up in a public repository, whatever you download becomes public
> too. Use this command only for content you are allowed to redistribute, and check
> what came in before you push.

---

## Connect other AI clients

**Claude Desktop (or another MCP client)** — add to `claude_desktop_config.json`:
```json
{ "mcpServers": { "altair-brain": {
    "command": "python",
    "args": ["<PATH>/altair-brain/server/mcp_server.py"],
    "env": { "ALTAIR_REPO_DIR": "<PATH>/altair-brain" } } } }
```
Run `pip install mcp` once. The assistant then has `brain_query`, `brain_search`,
`brain_context`, `brain_feedback` and the other tools listed in `server/README.md`.

**Custom GPT (ChatGPT)** — in the GPT's Actions, import the schema from
`https://YOUR-DOMAIN/openapi.json` and set authentication to API Key / Bearer with your
token.

**Any other HTTP client** — call the `/v1/...` endpoints with the token (full list in
`server/README.md`).

---

## The VPS (the always-on brain)

- It pulls from GitHub every three days, or immediately with `POST /v1/admin/update`.
- If a service stops you get a push notification: install the [ntfy](https://ntfy.sh)
  app, pick a secret topic (e.g. `altair-x8k2f9q`), subscribe to it in the app and set
  `NTFY_TOPIC=altair-x8k2f9q` in `~/altair-api/.env`.
- Writable data (feedback, captures) is backed up automatically every day.
- Deployment is described step by step in `server/README.md`.

---

## When something goes wrong

| Symptom | What to do |
|---|---|
| CI on GitHub is red ❌ | The push has a problem: open the error under GitHub → Actions, or ask the agent to fix CI. The `backup` branch stays on the last validated commit. |
| `rebuild_all` fails | Read which step failed: it names what to regenerate. |
| The API returns 401 | Wrong or missing token in the Authorization header. |
| The API returns 429 | Too many requests per minute: wait a moment. |
| The API returns 503 on /query | graphify is not installed on that server: `pipx install graphifyy`. |
| The VPS looks out of date | `GET /v1/health` shows `built_at_commit` and the graph's age. Force it with `POST /v1/admin/update`. |

---

## Ground rules

1. **Generated pages are not edited by hand.** With AION, `wiki/aion/` is generated
   from `engine/aion.model.json`: change the model and rebuild.
2. **One command rebuilds everything:** `python tools/rebuild_all.py`.
3. **The token is a secret:** never commit it, never paste it in a public chat.
4. **The repository is public.** Installed brains and the local registry are excluded
   from Git, and `tools/check_distribution.py` checks this in CI. Credentials and
   personal data stay outside the repository (`~/altair-data`, local disks).
5. Before any new work, the agent reads `ROADMAP.md`.
6. **Hooks are not in Git.** They live in `.claude/settings.local.json`, which is
   ignored: in a public repository a versioned hook would run commands on the machine
   of anyone who clones it. The inert example is `.claude/settings.example.json`; to
   enable it on a new machine: `cp .claude/settings.example.json .claude/settings.local.json`.
7. **`.agents/` is versioned**: any change to it must carry the `[hooks-ok]` marker in
   the commit message, or CI rejects it.

---

## Disaster recovery

Everything generated can be rebuilt from a clone. If you lose the computer or the VPS,
or `main` is damaged:

1. **Repository**: clone `main` from GitHub, or the `backup` branch, which points to the
   last commit that passed CI (`git checkout backup`), or use an existing local or VPS
   clone. CI also creates a weekly tag, `ripristino-YYYY-wNN`.
2. **Tools**: Python 3.12+, `pipx install graphifyy`, `pip install -r
   server/requirements.txt` (pinned versions, so the rebuild is identical).
3. **Rebuild**: `python tools/rebuild_all.py` regenerates graph, subgraphs, views and
   index from the sources (`raw/`, `wiki/`, `engine/`).
4. **Data outside the repository** (`~/altair-data`: feedback, captures, VPS lessons):
   restore from the latest `~/backups/altair-data_*.tar.gz` (7 local copies) or from the
   off-site rclone copy if configured (`ALTAIR_RCLONE_REMOTE`).
5. **If graphify disappeared from PyPI**: the brain stays readable, since it is all text.
   Queries and the graph would be lost, no content. Upstream source:
   github.com/safishamsi/graphify.

**Restore test, roughly every three months:** unpack the latest `~/altair-data` archive
into a temporary folder and check that the files open; clone the repository into a new
folder and run `python tools/rebuild_all.py`. A backup you have never restored is a
backup you do not know works.
