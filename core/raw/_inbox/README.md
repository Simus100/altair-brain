---
area: _inbox
source: documentazione della cartella
tags: []
---
# _inbox — cassetta di cattura

Cartella tecnica, non una macroarea: qui finiscono le note grezze in attesa di
smistamento. Butta qui un file `.md` qualsiasi, oppure usa `POST /v1/capture`
sull'API del brain. La skill `/triage` classifica ogni nota nella macroarea giusta,
rigenera il grafo e sposta la nota in `archive/`: non si cancella mai nulla.
