---
date: 2026-07-01
area: _inbox
source: 
tags: []
reviewed: 2026-08-12
---
# _inbox — cassetta di cattura

Cartella tecnica (NON e una macroarea): qui finiscono le note grezze in attesa di
smistamento.

- **Dal PC:** butta qui un file `.md` qualsiasi, senza pensarci.
- **Da telefono/altri dispositivi:** `POST /v1/capture` sull'API del brain
  (le note arrivano nell'inbox della VPS e vengono recuperate al triage).
- **Smistamento:** invoca la skill `/triage` — classifica ogni nota nella macroarea
  giusta, rigenera il grafo e archivia.

Le note processate finiscono in `archive/` (non si cancella mai nulla).
