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

## Dipendenza esterna: graphify (build Linux)
graphify e un **binario standalone**, non un pacchetto pip. Sulla VPS serve la **build
Linux** dello stesso graphify, messa sul PATH (`graphify --version` deve funzionare).
L'API degrada con eleganza: gli endpoint dati funzionano comunque, quelli graphify
rispondono 503 finche il binario non c'e.

## Endpoint
| Metodo | Path | Funzione |
|--------|------|----------|
| GET | `/health` | stato (pubblico) |
| GET | `/model` | `engine/aion.model.json` |
| GET | `/reasoner` | protocollo di ragionamento |
| GET | `/graph`, `/graph/compact` | grafo esteso / compatto (JSON) |
| GET | `/views/extended`, `/views/compact` | le due viste HTML |
| GET | `/lessons` | lezioni apprese |
| GET | `/query?q=`, `/path?a=&b=`, `/explain?x=`, `/affected?x=` | funzioni graphify |
| POST | `/feedback` | registra esito + reflect (apprendimento) |
| POST | `/admin/update` | pull + rigenerazione manuale |

Tutti (tranne `/health`) richiedono header `Authorization: Bearer <ALTAIR_API_TOKEN>`
(oppure `X-API-Key: <token>`).

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
