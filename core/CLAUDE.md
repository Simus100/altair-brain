## Come lavorare in questo repo

**Percorsi.** `raw/`, `wiki/`, `engine/` e `areas.json` sono relativi al brain attivo:
`python tools/brain.py` ne stampa la cartella. In questa installazione il brain e' la
cartella stessa (stampa `.`); in un'officina con piu' brain e' `brains/<nome>`.

- La conoscenza sta in due strati: `raw/` (fonti grezze) e `wiki/` (pagine curate e
  collegate con `[[wikilink]]`). I wikilink si risolvono **solo dentro la stessa
  cartella**: i concetti condivisi tra aree si dichiarano in `engine/bridges.json`.
- Le macroaree si dichiarano in `areas.json`, un registro solo: parole chiave per
  instradare le domande, SLA, coesione, strati generati, colore. Nessuna area va
  scritta dentro il codice. Gli schemi dei contratti sono in `schema/`.
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

Senza `--ancora` resta un'osservazione: la sintesi di una sessione, che entra nel prior
come contesto ma mai fra le regole. E' la difesa contro l'autofagia: un brain che
impara dalla prosa che il modello ha scritto amplifica i propri errori a ogni giro.
