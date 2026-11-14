# tools/ — il motore

Ogni comando si lancia dalla radice del repo e trova da solo il brain attivo
(`python tools/brain.py` lo stampa). I tool estendono graphify senza modificarlo: il
pacchetto installato resta intatto e aggiornabile.

## Indice

| Gruppo | Comandi |
|---|---|
| Pipeline | `rebuild_all.py` (tutto, in ordine), `extract_graph.py`, `graph_prune.py`, `apply_bridges.py`, `apply_provenance.py`, `build_area_graphs.py`, `sync_extended_view.py` |
| Brain | `brain.py` (quale brain è attivo), `brain_new.py`, `brain_upgrade.py`, `brain_export.py`, `onboarding.py`, `oplog.py` |
| Ricerca e contesto | `search.py`, `build_search_index.py`, `build_dense_index.py` (semantica, facoltativa), `context_pack.py` |
| Viste | `altair_compact_view.py`, `build_atlas_view.py`, `build_views_index.py` |
| Contratti e guardie | `validate_contracts.py`, `graph_health.py`, `check_wikilinks.py`, `check_provenance.py`, `check_privacy.py`, `check_distribution.py` |
| Qualità del corpus | `freshness_report.py`, `contradiction_report.py`, `link_suggest.py`, `add_frontmatter.py`, `resurface.py`, `consolidate.py`, `graph_metrics.py` |
| Lezioni | `lesson_log.py`, `lessons_digest.py` |
| Report | `report_new.py`, `report_build.py`, `report_update.py`, `report_harvest.py`, `style_check.py` |
| AION (solo con il training) | `gen_wiki_from_model.py`, `validate_model.py`, `build_iching_db.py`, `oracle_cast.py`, `apply_iching_relations.py` |
| Officina | `build_core.py` (genera `core/`), `build_code_graph.py`, `sync_agent_skills.py`, `console.py` |

Ogni file spiega nella propria intestazione cosa fa e perché. I report di qualità
propongono e basta: nessuno modifica le note da solo.

Lo scheletro `core/`, che è un brain solo, riceve una parte di questi tool. Restano
nell'officina quelli che gestiscono più brain (`brain_new.py`, `brain_export.py`,
`check_distribution.py`), `build_core.py`, `build_code_graph.py` e la ricerca
semantica. I tool AION vanno in `training/aion/tools/`, `style_check.py` nel plugin
`scrittura`, perché richiede un motore di stilometria che vive nel materiale grezzo.

Le sezioni che seguono descrivono le tre viste del grafo.

## altair_compact_view.py — vista compatta strutturale

Genera una vista **compatta** del grafo, affiancata a quella **estesa** prodotta da
graphify, che rappresenta altair-brain come **processo a 5 fasi**:

```
(1) Sorgenti raw/ → (2) Modello wiki/ → (3) Motore engine/ → (4) Skill /aion → (5) Feedback LESSONS
                                   ↑__________________________________________________|
```

Cosa fa:
- legge `graphify-out/graph.json` (sola lettura, non lo tocca);
- collassa il rumore (i 64 esagrammi I Ching in un nodo, gli insegnamenti in uno);
- aggancia ogni cluster reale alla sua fase di processo;
- scrive due file **nuovi**, lasciando intatti `graph.json` e `graph.html`:
  - `graphify-out/graph-compact.json`
  - `graphify-out/graph-compact.html` (interattivo, D3, colorato per fase)

Uso:

```bash
python tools/altair_compact_view.py
```

Deterministico e idempotente, senza API a pagamento.

## build_atlas_view.py — atlante 3D esplorabile

La vista estesa mostra tutto ma la posizione dei nodi non significa nulla; la compatta
si legge ma non si percorre. L'atlante serve a esplorare.

L'atlante usa **l'architettura del brain come sistema di coordinate**: altezza =
strato del processo, spicchio = macroarea, raggio = centralità. Mostra i nodi-FILE e
apre le sezioni interne su richiesta. Canvas 2D scritto a mano — nessuna libreria,
nessuna CDN, si apre offline da `file://`.

```bash
python tools/build_atlas_view.py
```

Comandi: trascina per ruotare, rotella per lo zoom, click per aprire un nodo, doppio
click per volarci, `L` lente sul vicinato a 2 passi, `R` rotazione, `/` cerca.

`tests/test_atlas.py` verifica
che ogni nodo stia nel suo strato e nel suo spicchio, che il raggio segua la
centralità, che la provenienza resti verticale, e che la pagina non contenga
dipendenze esterne.

## build_views_index.py — pagina d'ingresso

`graphify-out/index.html` è la pagina d'ingresso: elenca le tre viste e dice a quale
domanda risponde ciascuna. Link relativi: funziona anche da `file://`.

```bash
python tools/build_views_index.py
```

È deterministica: i numeri vengono dal grafo, non dall'orologio né dalla dimensione
dei file, che cambia con la versione di graphify. La CI ne verifica la coerenza.

## Le tre viste

Punto d'ingresso: **`graphify-out/index.html`**.

| Vista | File | Generata da | Serve a |
|-------|------|-------------|---------|
| Estesa | `graphify-out/graph.html` | `graphify update .` | vedere tutto |
| Compatta | `graphify-out/graph-compact.html` | `python tools/altair_compact_view.py` | spiegare il sistema come processo |
| Atlante 3D | `graphify-out/graph-atlas.html` | `python tools/build_atlas_view.py` | navigare e orientarsi |

Workflow standard dopo una modifica: **`python tools/rebuild_all.py`**, che le rigenera
tutte e tre nell'ordine giusto.
