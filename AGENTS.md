# AGENTS.md — regole di altair-brain per gli agenti

- `raw/` e materiale grezzo, diviso per macroarea (`raw/<area>/`, registro in `areas.json`).
- `wiki/` e GENERATA: `wiki/aion/` deriva da `engine/aion.model.json` via
  `tools/gen_wiki_from_model.py`. Non editarla a mano: modifica il modello e rigenera.
- Ogni pagina wiki collega i concetti con `[[wikilink]]` (risolvono solo nella stessa cartella).
- Non inventare contenuti: se `raw/` non basta, segnala cosa manca.
- Nessuna API a pagamento e richiesta per il funzionamento del brain.
- Dopo ogni modifica: `python tools/validate_model.py` (0 errori), `graphify update .`,
  `python tools/altair_compact_view.py`. Poi commit.
- Per ragionare col modello di pensiero AION usa la skill `/aion`
  (protocollo: `engine/aion-reasoner.md`; modulo Velario INERTE, non aggirarlo).
