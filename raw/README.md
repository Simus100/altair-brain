# raw/ — materiale grezzo per macroarea

Questa cartella contiene il materiale grezzo del second brain, **diviso per macroarea**. Ogni
sottocartella e una macroarea; il grafo (`graphify`) estrae nodi e relazioni da questi file e li
fonde in un unico grafo navigabile.

## Macroaree attive

L'elenco canonico vive in [`../areas.json`](../areas.json). Allo stato attuale:

| Cartella | Area | Ambito |
|----------|------|--------|
| `aion/` | AION | Modello di pensiero: framework, principi, struttura |
| `data-science/` | Data science | ML, statistica, analisi dati, MLOps |
| `finanza/` | Finanza | Mercati, fiscale, contabilita, investimenti |
| `divulgazione/` | Divulgazione | Comunicazione, scrittura, contenuti |
| `web-design/` | Web design | UI/UX, front-end, design system |

## Regole

- **`raw/` e grezzo.** Qui vanno fonti, note e documenti cosi come sono. Le pagine ragionate e
  collegate con `[[wikilink]]` vanno in `wiki/` (vedi [`../AGENTS.md`](../AGENTS.md)).
- **Naming:** file e cartelle in `kebab-case`, ascii, senza spazi. Formato preferito `.md`.
- **Ponti intercampo:** un concetto condiviso tra due aree, scritto con **lo stesso nome esatto**
  in entrambe, viene fuso dal grafo in un unico nodo che collega le aree. E il meccanismo dei
  ponti — sfruttalo usando nomi coerenti.
- **Non inventare:** se una fonte manca, segnalalo nel file invece di riempirlo.

## Aggiungere una nuova macroarea

1. Aggiungi una voce in [`../areas.json`](../areas.json) (`id`, `label`, `description`, `status`).
2. Crea la cartella `raw/<id>/` con un `README.md` che ne descrive l'ambito.
3. Inserisci il materiale e rigenera il grafo: `graphify update .`

Il sistema e pensato per crescere: le aree sono indipendenti, si aggiungono senza toccare le altre.
