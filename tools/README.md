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

## Le due viste

| Vista | File | Generata da | Scopo |
|-------|------|-------------|-------|
| Estesa | `graphify-out/graph.html` | `graphify update .` | tutti i nodi, esplorazione di dettaglio |
| Compatta | `graphify-out/graph-compact.html` | `python tools/altair_compact_view.py` | struttura del sistema come processo |

Workflow standard dopo una modifica: `graphify update .` poi `python tools/altair_compact_view.py`.
