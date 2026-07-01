# GUIDA — come usare il tuo second brain (per umani, zero tecnicismi)

> Questa guida spiega l'uso quotidiano. Per le specifiche tecniche c'è `ROADMAP.md`,
> per la panoramica `README.md`, per il deploy sulla VPS `server/README.md`.

---

## Cos'è, in un minuto

Hai un "cervello" fatto di file, dentro questa cartella (che è anche su GitHub).
- Metti **conoscenza grezza** in `raw/<area>/` (es. `raw/finanza/`).
- Un grafo collega tutto e le AI possono **interrogarlo, ragionarci e impararci sopra**.
- Ogni modifica che pubblichi (push) arriva **da sola** alla VPS e a tutti i dispositivi.
- Non serve pagare nessuna API: funziona tutto in locale.

---

## Le 6 cose che farai più spesso

### 1. Aggiungere conoscenza (dal PC)
Butta il file/nota in `raw/_inbox/` (senza pensarci), oppure direttamente in
`raw/<area>/` se sai già dove va. Poi apri l'agente (Claude Code) e digli:

> smista l'inbox    *(usa la skill `/triage`)*

oppure, se hai messo i file già a posto:

> rigenera il brain e pubblica

L'agente esegue `python tools/rebuild_all.py` (un comando fa tutto: wiki, validazioni,
grafo, sottografi, viste, salute) e poi commit+push.

### 2. Catturare un'idea dal telefono (o ovunque)
Con la VPS attiva, manda una richiesta all'API (una tantum: creati una Shortcut
iOS/Android che fa questo):

```
POST https://TUO-DOMINIO/v1/capture
Authorization: Bearer IL-TUO-TOKEN
{"text": "l'idea che mi è venuta", "title": "titolo breve"}
```

La nota finisce nell'inbox della VPS. Al prossimo "smista l'inbox" dal PC, l'agente la
recupera, la classifica nell'area giusta e la archivia.

### 3. Interrogare il brain
- **Dall'agente:** chiedi e basta ("cosa sa il brain su X?") — usa il grafo da solo.
  Per un ragionamento profondo in stile AION: `/aion <domanda>`.
- **Da terminale:** `graphify query "domanda"` (aggiungi `--graph graphify-out/areas/aion/graph.json` per una sola area).
- **Da altri dispositivi:** `GET /v1/query?q=...` con il token (il **router** sceglie
  da solo l'area giusta; l'area usata è nell'header `X-Altair-Area`).

### 4. Consultare l'oracolo (I Ching)
Dall'agente: `/oracle <la tua domanda strategica>` — lancio reale (matematica corretta
di Re Wen), linee mobili, esagramma di trasformazione, lettura in stile AION.
Da API: `POST /v1/oracle` con `{"question": "..."}`.

### 5. Far imparare il brain
Quando una risposta è stata utile (o sbagliata), dillo all'agente:
> registra questo esito come utile / vicolo cieco / corretto

Si accumula in `LESSONS.md` e il protocollo AION lo consulta a ogni ragionamento (passo 0).

### 6. Vedere il grafo
- `graphify-out/graph.html` = vista estesa (tutti i nodi)
- `graphify-out/graph-compact.html` = vista compatta (il sistema come processo a 5 fasi)
- Da remoto: `GET /v1/views/compact` con il token.

---

## Collegare altre AI al brain

**Claude Desktop (o altri client MCP)** — aggiungi al file di config
(`claude_desktop_config.json`):
```json
{ "mcpServers": { "altair-brain": {
    "command": "python",
    "args": ["C:/Users/mace/altair-brain/server/mcp_server.py"],
    "env": { "ALTAIR_REPO_DIR": "C:/Users/mace/altair-brain" } } } }
```
Serve una volta: `pip install mcp`. Da quel momento quell'AI ha i tool
`brain_query`, `brain_model`, `brain_oracle`, `brain_feedback`, ecc.

**Custom GPT (ChatGPT)** — nelle Actions del GPT: importa lo schema da
`https://TUO-DOMINIO/openapi.json`, autenticazione "API Key / Bearer" con il tuo token.

**OpenClaw / qualsiasi AI sulla VPS o via HTTP** — usa gli endpoint `/v1/...`
(il prompt di collegamento è in `server/README.md`).

---

## La VPS (il brain sempre acceso)

- Si **auto-aggiorna ogni 3 giorni** dal GitHub (o subito: `POST /v1/admin/update`).
- Se qualcosa si rompe ti arriva una **notifica push sul telefono**: installa l'app
  [ntfy](https://ntfy.sh), scegli un topic segreto (es. `altair-x8k2f9q`), iscriviti
  nell'app e scrivilo in `~/altair-api/.env` come `NTFY_TOPIC=altair-x8k2f9q`.
- I dati "vivi" (feedback, catture) sono al sicuro: backup automatico giornaliero.
- Il deploy completo si fa con i prompt pronti in `server/README.md` (li dai a OpenClaw).

---

## Se qualcosa va storto

| Sintomo | Cosa fare |
|---|---|
| La CI su GitHub è rossa ❌ | Il push aveva un problema: apri l'errore su GitHub → Actions, oppure chiedi all'agente "sistemare la CI". I consumatori NON ricevono brain rotti, quindi niente panico. |
| `rebuild_all` fallisce | Leggi quale passo è fallito: dice esattamente cosa rigenerare. |
| L'API risponde 401 | Token sbagliato o mancante nell'header Authorization. |
| L'API risponde 429 | Troppe richieste al minuto: aspetta un attimo. |
| L'API risponde 503 su /query | graphify non è installato su quel server: `pipx install graphifyy`. |
| La VPS sembra "vecchia" | `GET /v1/health` mostra `built_at_commit` e l'età del grafo. Forza: `POST /v1/admin/update`. |

---

## Le regole d'oro (non dimenticarle)

1. **Mai modificare `wiki/` a mano** — si genera da `engine/aion.model.json`.
2. **Un solo comando per rigenerare tutto:** `python tools/rebuild_all.py`.
3. **Il token è un segreto**: mai committarlo, mai condividerlo in chat pubbliche.
4. **Il repo deve restare PRIVATO** su GitHub.
5. Per qualsiasi lavoro nuovo, l'agente deve leggere prima `ROADMAP.md`.
