---
date: 2026-06-30
area: generale
source: 
tags: []
reviewed: 2026-08-06
---
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

## Front-matter standard (convenzione del brain)

```yaml
---
date: 2026-07-01           # quando la nota entra nel brain
area: data-science         # macroarea (coincide con la cartella)
source: libro/url/riflessione propria
tags: [parola-chiave, altra]
reviewed: 2026-07-19       # ultima verifica umana -> guida il freshness SLA
---
```

Campi **opzionali** per i fatti che invecchiano (bi-temporalita, modello Zep):

```yaml
confidence: alta | media | bassa
valid_from: 2026-06-17     # da quando il fatto e vero nel mondo
valid_until: 2026-07-08    # quando ha smesso di esserlo
superseded_by: raw/area/nota-che-lo-rimpiazza.md
```

**Regola d'oro della bi-temporalita:** un fatto che smette di essere vero **non si
cancella**, si marca con `valid_until` e si indica cosa lo sostituisce. La storia
resta consultabile, la verita corrente e sempre identificabile. Vale anche per
l'inbox (si archivia, non si elimina) e per i report living (le timeline).

**Strumenti:**
- `python tools/add_frontmatter.py --apply` aggiunge i campi mancanti (idempotente,
  non sovrascrive nulla, e si rifiuta di toccare gli strati GENERATI come `wiki/aion/`);
- `python tools/freshness_report.py` elenca cosa e scaduto e cosa va ri-verificato.

**Freschezza (SLA di default):** attualita 30 giorni · metodo 365 giorni · principi
nessuna scadenza · resto 180 giorni. Le note catturate via `/capture` hanno gia il
front-matter. La cartella `_inbox/` e la cassetta di cattura: smistala con `/triage`.

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
