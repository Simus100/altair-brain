# server/ — API HTTP e server MCP

Espone un brain ad altri dispositivi e ad assistenti AI. Graphify gira in locale e il
ragionamento resta al client che interroga (Claude, ChatGPT, qualsiasi client HTTP o
MCP): nessuna API a pagamento.

## File

| File | Ruolo |
|---|---|
| `app.py` | API FastAPI, endpoint sotto `/v1` |
| `brain_core.py` | logica condivisa da API e server MCP |
| `mcp_server.py` | server MCP via stdio, per assistenti locali |
| `requirements.txt` | dipendenze con versioni bloccate (fastapi, uvicorn, mcp) |
| `bootstrap.sh` | installa il runtime sulla VPS: cartelle, virtualenv, dipendenze |
| `update_brain.sh` | allinea il repo al remoto e rigenera grafo e viste |
| `backup_data.sh` | backup giornaliero a rotazione dei dati scrivibili |
| `systemd/` | unit per API, aggiornamento periodico, backup e notifiche di guasto |
| `Caddyfile` | reverse proxy con HTTPS automatico |
| `.env.example` | elenco delle variabili di configurazione |
| `client_example.py` | client di prova, solo libreria standard |
| `altair.http` | richieste di esempio per VS Code REST Client o JetBrains |

## Graphify

Graphify si installa dal pacchetto PyPI `graphifyy`, che fornisce il comando `graphify`
([sorgente](https://github.com/safishamsi/graphify)). Su Linux:

```bash
pipx install graphifyy         # oppure: uv tool install graphifyy
graphify --version
```

Il comando finisce in `~/.local/bin`, che i servizi systemd non hanno nel PATH. Per
questo il file `.env` del runtime contiene `GRAPHIFY_BIN` con il percorso assoluto;
`bootstrap.sh` lo imposta da solo. Se il binario non si trova, gli endpoint sui dati continuano a
funzionare e quelli che usano graphify rispondono 503.

## Endpoint

Tutti sotto `/v1`; i vecchi percorsi senza prefisso restano attivi come alias.

| Metodo | Percorso | Risposta |
|---|---|---|
| GET | `/v1/health` | stato: nodi del grafo, commit di build, età, aree. Senza token |
| GET | `/v1/areas` | aree e tabella di instradamento |
| GET | `/v1/route?q=` | in quale area il router manderebbe la domanda |
| GET | `/v1/query?q=&area=&budget=` | interrogazione del grafo; l'area scelta torna nell'header `X-Altair-Area` |
| GET | `/v1/search?q=&top=&area=&al=` | ricerca nel testo (BM25, più semantica se attivata); `al=AAAA-MM-GG` risponde con ciò che era vero in quella data |
| GET | `/v1/context?q=&budget=&area=&formato=` | contesto pronto per un LLM entro un budget di token; `formato=testo` restituisce markdown |
| GET | `/v1/path`, `/v1/explain`, `/v1/affected` | percorso fra due nodi, spiegazione di un concetto, nodi toccati da una modifica |
| GET | `/v1/graph`, `/v1/graph?area=`, `/v1/graph/compact` | grafo completo, di un'area, compatto |
| GET | `/v1/views/extended`, `/v1/views/compact`, `/v1/views/atlas` | le tre viste HTML |
| GET | `/v1/lessons` | lezioni consolidate |
| POST | `/v1/capture` `{text, title?, area_hint?, source?}` | salva una nota nell'inbox |
| GET | `/v1/inbox`, `/v1/inbox/{id}` | note in attesa, contenuto di una nota |
| POST | `/v1/inbox/{id}/done` | archivia una nota smistata |
| POST | `/v1/feedback` | registra l'esito di una risposta |
| POST | `/v1/admin/update` | forza l'allineamento al remoto |

Solo con il training AION:

| Metodo | Percorso | Risposta |
|---|---|---|
| GET | `/v1/model` | il modello AION (`engine/aion.model.json`, campo `schema_version`) |
| GET | `/v1/reasoner` | il protocollo di ragionamento |
| POST | `/v1/oracle` `{question?, seed?}` | lancio I Ching |
| GET | `/v1/oracle/hexagram/{id}` | scheda di un esagramma, da 1 a 64 |

Ogni endpoint tranne `/health` richiede `Authorization: Bearer <ALTAIR_API_TOKEN>`
oppure `X-API-Key`. Il token si confronta in tempo costante; il limite di richieste per
IP si imposta con `ALTAIR_RATE_LIMIT` (predefinito 120 al minuto).

## Server MCP

`mcp_server.py` espone gli stessi servizi come tool MCP: `brain_query`,
`brain_search`, `brain_context`, `brain_explain`, `brain_path`, `brain_lessons`,
`brain_feedback` e, con AION, `brain_model`, `brain_reasoner`, `brain_oracle`.
Gira dove il repo è clonato, senza rete e senza token. Serve `pip install mcp`.

Configurazione di Claude Desktop (`claude_desktop_config.json`):

```json
{ "mcpServers": { "altair-brain": {
    "command": "python",
    "args": ["<PERCORSO>/altair-brain/server/mcp_server.py"],
    "env": { "ALTAIR_REPO_DIR": "<PERCORSO>/altair-brain" } } } }
```

## ChatGPT (Custom GPT)

Nelle Actions del GPT importa lo schema da `https://<dominio>/openapi.json` e scegli
l'autenticazione API Key di tipo Bearer con il token.

## Deploy su VPS

1. Crea un utente dedicato, non root, e installa python3-venv, git, Caddy e graphify.
2. Clona il repo nella home di quell'utente e lancia `server/bootstrap.sh`. Crea
   `~/altair-api` (runtime: virtualenv, codice, configurazione) e `~/altair-data`
   (dati scrivibili fuori da Git: feedback, catture, lezioni). Si può rilanciare.
3. Al primo avvio lo script scrive `~/altair-api/.env` con un token casuale di 64
   caratteri esadecimali e lo stampa una volta: conservalo. Un `.env` esistente non
   viene toccato.
4. Installa come root le unit di `systemd/`: l'API, il timer di aggiornamento ogni tre giorni,
   il backup giornaliero.
5. Configura Caddy per l'HTTPS. Uvicorn ascolta solo su `127.0.0.1:8000`; il firewall
   lascia aperte solo le porte 80 e 443.
6. Prova da un altro dispositivo con `client_example.py` e il token.

Il repo sulla VPS si usa in sola lettura: l'aggiornamento fa fetch e reset, quindi
modifiche locali al repo vanno perse. I dati vivi stanno in `~/altair-data`.

## Guasti e backup

- `systemd/altair-notify@.service` manda una notifica push via [ntfy](https://ntfy.sh)
  quando una unit fallisce. Imposta `NTFY_TOPIC` in `.env` e iscriviti allo stesso topic
  dall'app. API, aggiornamento e backup hanno già `OnFailure=`.
- `systemd/altair-backup.{service,timer}` con `backup_data.sh` salvano ogni giorno
  `~/altair-data` e tengono le ultime 7 copie. È l'unico dato che GitHub non conserva.

## Sicurezza

- L'API non parte senza `ALTAIR_API_TOKEN`; `.env` non è versionato.
- I comandi esterni ricevono gli argomenti come lista, senza shell.
- Aree, id dell'inbox e seed vengono validati prima dell'uso.
- Il modulo Velario del protocollo AION è inerte: l'API non lo usa per aggirare filtri.

**Limite noto.** C'è un solo token, e vale per tutto il brain servito, operazioni
amministrative comprese (`/v1/admin/update`, `/v1/inbox/{id}/done`). Credenziali
separate per lettura e amministrazione sono fra le prossime priorità.
