# server/ — esposizione del second brain via FastAPI

Espone il brain e graphify ad altri dispositivi, in sicurezza, **senza API a pagamento**
(graphify gira in locale; il ragionamento LLM resta al client, es. OpenClaw/GPT).

## Componenti
- `app.py` — API FastAPI (auth a token, endpoint sotto).
- `requirements.txt` — dipendenze Python (fastapi, uvicorn).
- `update_brain.sh` — pull + `graphify update` + vista compatta (auto-update).
- `systemd/` — servizio API + timer "ogni 3 giorni".
- `Caddyfile` — reverse proxy con HTTPS automatico.
- `.env.example` — copia in `.env` e imposta `ALTAIR_API_TOKEN`.

## Dipendenza: graphify (pacchetto Python)
graphify e il pacchetto PyPI **`graphifyy`** (CLI `graphify`), da https://github.com/safishamsi/graphify.
Installazione su Linux (consigliata pipx o uv):

```bash
pipx install graphifyy         # oppure:  uv tool install graphifyy
graphify --version
```

Va sul PATH dell'utente (`~/.local/bin`). Poiche i servizi systemd non ereditano quel
PATH, imposta in `server/.env` la variabile `GRAPHIFY_BIN` col percorso assoluto
(es. `/home/altair/.local/bin/graphify`); `bootstrap.sh` lo fa da solo. L'API degrada
con eleganza: gli endpoint dati funzionano comunque, quelli graphify rispondono 503 se
il binario non e raggiungibile.

## Endpoint (v1 — alias non versionati mantenuti)
| Metodo | Path | Funzione |
|--------|------|----------|
| GET | `/v1/health` | stato ricco: grafo (nodi, commit, età), modello, aree (pubblico) |
| GET | `/v1/model` | `engine/aion.model.json` (contratto: `schema_version`) |
| GET | `/v1/reasoner` | protocollo di ragionamento AION |
| GET | `/v1/graph`, `?area=<id>`, `/v1/graph/compact` | grafo completo / per area / compatto |
| GET | `/v1/areas` | aree disponibili + tabella di routing |
| GET | `/v1/views/extended`, `/v1/views/compact` | le due viste HTML |
| GET | `/v1/lessons` | lezioni apprese |
| GET | `/v1/route?q=` | decisione del router (trasparenza) |
| GET | `/v1/query?q=&area=&budget=` | query (router automatico; header `X-Altair-Area`) |
| GET | `/v1/path`, `/v1/explain`, `/v1/affected` | funzioni graphify |
| POST | `/v1/oracle` `{question?, seed?}` | lancio I Ching (AION_Oracle eseguibile) |
| GET | `/v1/oracle/hexagram/{id}` | scheda esagramma (1-64) |
| POST | `/v1/capture` `{text, title?, area_hint?, source?}` | cattura nota → inbox |
| GET | `/v1/inbox`, `/v1/inbox/{id}` | note pendenti / contenuto |
| POST | `/v1/inbox/{id}/done` | archivia nota processata |
| POST | `/v1/feedback` | registra esito + reflect (apprendimento) |
| POST | `/v1/admin/update` | allineamento manuale al remoto |

Tutti (tranne `/health`) richiedono `Authorization: Bearer <ALTAIR_API_TOKEN>`
(o `X-API-Key`). Confronto token constant-time; rate limit per IP
(`ALTAIR_RATE_LIMIT`, default 120 req/min).

## Server MCP (assistenti AI locali)
`server/mcp_server.py` espone il brain come tool MCP nativi (`brain_query`,
`brain_model`, `brain_oracle`, `brain_feedback`, ...). Richiede `pip install mcp`.
Config Claude Desktop: vedi intestazione del file o `GUIDA.md`.

## Custom GPT (ChatGPT Actions)
Nelle Actions del GPT importa lo schema da `https://<dominio>/openapi.json` e imposta
autenticazione API Key → Bearer con il token. Il GPT ottiene tutti gli endpoint v1.

## Notifiche di guasto + backup
- `systemd/altair-notify@.service`: push gratuito via ntfy.sh quando una unit fallisce
  (imposta `NTFY_TOPIC` in `.env`, iscriviti dall'app ntfy sul telefono). Le unit
  API/update/backup hanno gia `OnFailure=`.
- `systemd/altair-backup.{service,timer}` + `backup_data.sh`: backup giornaliero
  rotante (7 copie) di `~/altair-data` — l'unico dato non protetto da GitHub.

## Deploy
Vedi i prompt passo-passo per OpenClaw (consegnati a parte). In sintesi:
1. utente dedicato + dipendenze (python3-venv, git, caddy, build Linux di graphify);
2. `git clone` del repo, venv, `pip install -r server/requirements.txt`;
3. `server/.env` con un token casuale robusto;
4. `systemd` per l'API e per il timer di aggiornamento (3 giorni);
5. Caddy per HTTPS + firewall (solo 80/443 pubblici; API su 127.0.0.1:8000);
6. verifica da un altro dispositivo con il token.

## Sicurezza (attenzioni del caso)
- Token obbligatorio; l'API non parte senza `ALTAIR_API_TOKEN`.
- Subprocess con argomenti come lista (no shell) → niente command injection.
- Uvicorn su `127.0.0.1`; l'esterno passa solo da Caddy (TLS).
- Modulo **Velario inerte** a livello di dati: non aggira filtri.
- Esegui come utente non-root; `server/.env` non e versionato.
