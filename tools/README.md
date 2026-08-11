# tools/ — feature di supporto ad altair-brain

Strumenti versionati che **estendono** graphify senza modificarne il binario installato
(questa è "l'attenzione del caso": il tool esterno resta intatto e aggiornabile).

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

Proprietà: **deterministico, nessuna API a pagamento**, idempotente.

## build_atlas_view.py — atlante 3D esplorabile

La terza vista. Le altre due falliscono l'esplorazione da lati opposti: l'estesa è un
gomitolo dove la posizione non significa nulla, la compatta è un diagramma che si
legge ma non si percorre.

L'atlante usa **l'architettura del brain come sistema di coordinate**: altezza =
strato del processo, spicchio = macroarea, raggio = centralità. Mostra i nodi-FILE e
apre le sezioni interne su richiesta. Canvas 2D scritto a mano — nessuna libreria,
nessuna CDN, si apre offline da `file://`.

```bash
python tools/build_atlas_view.py
```

Comandi: trascina per ruotare, rotella per lo zoom, click per aprire un nodo, doppio
click per volarci, `L` lente sul vicinato a 2 passi, `R` rotazione, `/` cerca.

Le promesse del layout non sono affidate all'occhio: `tests/test_atlas.py` verifica
che ogni nodo stia nel suo strato e nel suo spicchio, che il raggio segua la
centralità, che la provenienza resti verticale, e che la pagina non contenga
dipendenze esterne.

## build_views_index.py — la porta

Chi apre `graphify-out/` trova tre file `.html` e nessun indizio su quale serva.
`graphify-out/index.html` è la porta: apre le tre viste dicendo a quale domanda
risponde ciascuna, **prima** del click. Link relativi: funziona anche da `file://`.

```bash
python tools/build_views_index.py
```

Deterministica — i numeri vengono dal grafo, non dall'orologio né dal peso dei file
(che dipende dalla versione di graphify installata). La CI ne verifica la coerenza.

## Le tre viste

Punto d'ingresso: **`graphify-out/index.html`**.

| Vista | File | Generata da | Serve a |
|-------|------|-------------|---------|
| Estesa | `graphify-out/graph.html` | `graphify update .` | vedere tutto |
| Compatta | `graphify-out/graph-compact.html` | `python tools/altair_compact_view.py` | spiegare il sistema come processo |
| Atlante 3D | `graphify-out/graph-atlas.html` | `python tools/build_atlas_view.py` | navigare e orientarsi |

Workflow standard dopo una modifica: **`python tools/rebuild_all.py`**, che le rigenera
tutte e tre nell'ordine giusto.
