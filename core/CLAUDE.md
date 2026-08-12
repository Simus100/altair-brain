## Come lavorare in questo repo

- La conoscenza sta in due strati: `raw/` (fonti grezze) e `wiki/` (pagine curate e
  collegate con `[[wikilink]]`). I wikilink si risolvono **solo dentro la stessa
  cartella**: i concetti condivisi tra aree si dichiarano in `engine/bridges.json`.
- Le macroaree si dichiarano in `areas.json` e in `engine/router.json`. Nessuna area
  va scritta dentro il codice: SLA, coesione e strati generati sono proprieta' delle
  aree, non dei tool.
- Dopo ogni modifica: **`python tools/rebuild_all.py`**, che rigenera grafo, viste,
  indice di ricerca, metriche e fa girare le guardie. Poi commit.

## Provenienza (non negoziabile)

Ogni affermazione con numeri o date porta la sua fonte. `engine/provenance.json`
cuce la catena fonte->conoscenza nel grafo.

## Memoria operativa

Chiudi ogni lavoro registrando cosa hai imparato:

```bash
python tools/lesson_log.py --skill <nome> --domanda "..." \
  --quando "il segnale che fa scattare la regola" \
  --allora "cosa fare" \
  --ancora "test:... | errore:... | misura:... | utente:... | guardia:..."
```

Senza `--ancora` resta osservazione e non entra nel prior del ragionamento. E' la
difesa contro l'autofagia: un brain che impara dalla prosa che il modello ha
scritto amplifica i propri errori a ogni giro.
