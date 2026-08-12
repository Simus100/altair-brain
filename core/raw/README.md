---
date: 2026-01-01
area: generale
source:
tags: []
reviewed: 2026-01-01
---
# raw/ — materiale grezzo per macroarea

Ogni sottocartella e una macroarea dichiarata in `../areas.json`. Il grafo estrae
nodi e relazioni da questi file.

## Front-matter standard

```yaml
---
date: 2026-01-01           # quando la nota entra nel brain
area: <id-area>            # coincide con la cartella
source: libro/url/riflessione propria
tags: [parola-chiave]
reviewed: 2026-01-01       # ultima verifica umana -> guida lo SLA di freschezza
---
```

Campi opzionali per i fatti che invecchiano: `confidence`, `valid_from`,
`valid_until`, `superseded_by`.

**Regola d'oro:** un fatto che smette di essere vero **non si cancella**, si marca
con `valid_until` e si indica cosa lo sostituisce.

## Regole

- `raw/` e grezzo: fonti e documenti come sono. Le pagine ragionate e collegate con
  `[[wikilink]]` vanno in `wiki/`.
- Naming in `kebab-case` ascii, senza spazi. Formato preferito `.md`.
- **Non inventare:** se una fonte manca, segnalalo nel file invece di riempirlo.
