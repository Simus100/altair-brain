# AGENTS.md — regole di altair-brain per gli agenti

- `raw/` e materiale grezzo, diviso per macroarea (`raw/<area>/`, registro in `areas.json`).
- `wiki/` e GENERATA: `wiki/aion/` deriva da `engine/aion.model.json` via
  `tools/gen_wiki_from_model.py`. Non editarla a mano: modifica il modello e rigenera.
- Ogni pagina wiki collega i concetti con `[[wikilink]]` (risolvono solo nella stessa cartella).
- Non inventare contenuti: se `raw/` non basta, segnala cosa manca.
- Nessuna API a pagamento e richiesta per il funzionamento del brain.
- Dopo ogni modifica: **`python tools/rebuild_all.py`** (un comando: validazione, grafo,
  e le TRE viste — estesa, compatta, atlante 3D). Poi commit.
- Per ragionare col modello di pensiero AION usa la skill `/aion`
  (protocollo: `engine/aion-reasoner.md`; modulo Velario INERTE, non aggirarlo).
