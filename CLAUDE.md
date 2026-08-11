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

Il sistema produce TRE viste affiancate del grafo. Servono a domande diverse: se
ne stai usando una per la domanda sbagliata, stai perdendo tempo.

**La porta è `graphify-out/index.html`** (generata da `tools/build_views_index.py`):
apre le tre viste dicendo a quale domanda risponde ciascuna, prima del click.

- **Vista estesa** — `graphify-out/graph.html`, generata da `graphify update .` (tutti
  i nodi). Serve a *vedere tutto*; non serve a trovare niente.
- **Vista compatta strutturale** — `graphify-out/graph-compact.html`, generata da
  `python tools/altair_compact_view.py` (estende graphify, non lo modifica). Mostra
  altair-brain come **processo a 5 fasi**: (1) Sorgenti `raw/` → (2) Modello `wiki/` →
  (3) Motore `engine/` → (4) Skill `/aion` → (5) Feedback `LESSONS`, con anello di
  ritorno. Collassa il rumore (es. i 64 esagrammi in un nodo). Deterministica, no API.
  Serve a *spiegare* il sistema.
- **Atlante 3D esplorabile** — `graphify-out/graph-atlas.html`, generato da
  `python tools/build_atlas_view.py`. Serve a **navigare**: è la vista da aprire per
  orientarsi in un'area che non conosci. Mostra i ~214 nodi-FILE (non i 1603 titoli
  interni) in uno spazio dove **la posizione significa**:
  *altezza* = strato del processo (fonti → sapere → motore → uso, gli stessi passi
  della vista compatta), *spicchio* = macroarea (tutte della stessa ampiezza: le aree
  vuote si vedono), *raggio* = centralità (gli hub vicino all'asse). Tasto `L` = lente
  sul vicinato a 2 passi, doppio click = vola sul nodo. Canvas 2D scritto a mano:
  nessuna libreria, funziona offline da `file://`, deterministico.
  Le invarianti del layout sono verificate in `tests/test_atlas.py`.

Workflow dopo ogni modifica: **`python tools/rebuild_all.py`** (un comando: wiki dal
modello, validazioni, DB oracle, grafo, ponti, provenienza, sottografi, viste, indice
di ricerca, lezioni, metriche, salute). Poi commit.
Regole: la wiki e GENERATA da `engine/aion.model.json` (mai editarla a mano); il DB
oracle e GENERATO da `raw/aion/aion-oracle.md`; l'indice di ricerca e GENERATO dal corpus.

## Due motori di ricerca (usa quello giusto)

- **Struttura** → `graphify query "..."` : nodi e relazioni. Prima scelta per orientarsi.
- **Contenuto** → `python tools/search.py "..."` : BM25 sul testo, **inclusi i .txt che
  graphify non indicizza** (le note di `raw/data-science/` sono visibili solo qui).
  Endpoint `/v1/search`, tool MCP `brain_search`. Semantico opzionale: vedi
  `tools/build_dense_index.py`.

## Memoria operativa

Chiudi ogni lavoro significativo registrando la lezione:
`python tools/lesson_log.py --skill <nome> --domanda "..." --esito utile|vicolo-cieco|corretto|aperto --nota "..."`.
Confluisce in `engine/LESSONS.md` (passo 0 del reasoner). E il meccanismo che rende il
brain capace di migliorare: saltarlo lo lascia fermo.

## Provenienza (non negoziabile sui report)

Ogni affermazione con numeri o date porta la sua fonte. `engine/provenance.json` cuce
la catena fonte->conoscenza nel grafo; `tools/check_provenance.py` verifica i report.
Front-matter delle note: `date/area/source/tags/reviewed` (+ `valid_until`/`superseded_by`
per i fatti che invecchiano: si invalidano, **non si cancellano**). Vedi `raw/README.md`.

La CI (`.github/workflows/validate.yml`) ripete questi controlli su ogni push: i
consumatori (VPS, dispositivi) ricevono solo un brain valido.

## Scrittura (quando il brain produce prosa)

Report, pagine curate, note lunghe: la prosa del brain segue la dottrina dell'area
`creativita` (distillata da BookForge). **L'ordine non si inverte**: in stesura vale
solo `wiki/creativita/carta-della-prosa.md` (imperativi positivi); l'elenco dei tic
(`wiki/creativita/anti-ai.md`) si apre **in revisione**, mai durante il draft.

Regola sovrana: *se una frase va riletta per essere capita, va riscritta piu semplice* —
batte ogni altra regola. Verifica misurabile: `python tools/style_check.py <file>`
oppure `--report <nome>`, che distingue la classe OGGETTIVA (anglicismi, ripetizioni:
si correggono sempre) da quella INDIZIARIA (soglie e tic: solo segnalazione, l'orecchio
batte i numeri).

Skill del brain: `/aion` (ragionamento col modello di pensiero), `/triage` (smista
l'inbox nelle macroaree), `/oracle` (I Ching eseguibile via tools/oracle_cast.py),
`/scrivi` (scrittura e revisione con verifica stilometrica).
