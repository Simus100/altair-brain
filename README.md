# altair-brain

Second brain personale, scalabile e portabile. La conoscenza e organizzata a
**macroaree** su un knowledge graph ([graphify](https://github.com/safishamsi/graphify))
e puo contenere **modelli di pensiero eseguibili**: AION e il primo. Il repo stesso e il
cervello — ogni canale di accesso (assistente AI locale, VPS/FastAPI, altri dispositivi)
lo consuma via git o via API.

## Principi

1. **Nessuna API a pagamento per funzionare** — tutto e deterministico: dati + istruzioni.
2. **Fonte unica di verita** — `engine/aion.model.json` genera la wiki; niente deriva.
3. **Consumatori in sola lettura** — chi fa `git pull` riceve un brain sempre valido
   (validazione in CI prima che arrivi su `main`).

## Struttura (il processo a 5 fasi)

| Fase | Cartella | Contenuto |
|------|----------|-----------|
| 1. Sorgenti | `raw/<area>/` | materiale grezzo per macroarea (registro: `areas.json`) |
| 2. Modello | `wiki/<area>/` | pagine collegate con `[[wikilink]]` — **generate**, non editare a mano |
| 3. Motore | `engine/` | modello tipizzato (`aion.model.json`) + protocollo (`aion-reasoner.md`) |
| 4. Skill | `.claude/skills/aion/` | `/aion`: il brain ragiona col modello di pensiero |
| 5. Feedback | `graphify-out/memory` → `reflections/LESSONS.md` | il brain impara dagli esiti |

Il grafo e le due viste sono in `graphify-out/` (`graph.html` estesa, `graph-compact.html`
compatta per processo). Tool di supporto in `tools/`, stack di esposizione in `server/`.

## Macroaree

`aion` (modello di pensiero — popolata) · `data-science` · `finanza` · `divulgazione` ·
`web-design`. Concetti con lo stesso nome esatto in aree diverse vengono fusi dal grafo:
sono i **ponti intercampo**.

## Come si consuma

- **Assistente AI locale** (Claude Code, Antigravity, OpenClaw…): clona il repo; le regole
  sono in `CLAUDE.md`/`AGENTS.md`; ragiona con la skill `/aion`.
- **Sistemi esterni**: leggi direttamente `engine/aion.model.json` (JSON tipizzato) e
  `engine/aion-reasoner.md` (protocollo a 9 passi).
- **Rete / altri dispositivi**: API FastAPI in `server/` (token + HTTPS), deploy su VPS con
  auto-allineamento ogni 3 giorni. Guida: `server/README.md`.

## Workflow di modifica (per chi scrive nel brain)

```bash
# 1. modifica raw/ o engine/aion.model.json (mai wiki/ a mano)
python tools/rebuild_all.py     # UN comando: wiki, validazioni, DB oracle, grafo,
                                # sottografi per area, viste, salute del grafo
# 2. commit + push: i consumatori si allineano da soli (la CI rivalida tutto)
```

## Guide

- **`GUIDA.md`** — uso quotidiano per umani (cattura, triage, query, oracolo, collegare AI)
- **`ROADMAP.md`** — handoff tecnico per agenti (regole vincolanti + spec implementazioni)
- **`server/README.md`** — API, deploy VPS, MCP, Custom GPT
