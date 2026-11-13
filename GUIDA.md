# GUIDA — uso quotidiano del brain

> I percorsi come `engine/…`, `raw/…`, `wiki/…` stanno dentro il brain che stai usando
> (`python tools/brain.py` ti dice quale: su un clone nuovo è `brains/starter`). I comandi si danno
> dalla cartella principale del progetto.

> Questa guida spiega l'uso quotidiano. Per le specifiche tecniche c'è `ROADMAP.md`,
> per la panoramica `README.md`, per il deploy sulla VPS `server/README.md`.

---

## Cos'è, in un minuto

Un brain è una cartella di file Markdown.
- Le fonti grezze vanno in `raw/<area>/`, le pagine curate in `wiki/<area>/`.
- La pipeline ne ricava un grafo e un indice di ricerca, che un assistente AI può
  interrogare da terminale, via MCP o via HTTP.
- Se hai una VPS collegata, ogni push le arriva al prossimo aggiornamento automatico.
- Nessuna API a pagamento: grafo, ricerca e viste si costruiscono in locale.

---

## Le 6 cose che farai più spesso

### 1. Aggiungere conoscenza (dal PC)
Metti il file in `raw/_inbox/`, oppure direttamente in `raw/<area>/` se sai già
dove va. Poi apri l'agente (Claude Code) e digli:

> smista l'inbox    *(usa la skill `/triage`)*

oppure, se hai messo i file già a posto:

> rigenera il brain e pubblica

L'agente esegue `python tools/rebuild_all.py` (un comando fa tutto: wiki, validazioni,
grafo, sottografi, viste, salute) e poi commit+push.

### 2. Catturare un'idea dal telefono (o ovunque)
Con la VPS attiva, manda una richiesta all'API. Conviene salvarla una volta in un
Comando rapido di iOS o in un'automazione Android:

```
POST https://TUO-DOMINIO/v1/capture
Authorization: Bearer IL-TUO-TOKEN
{"text": "l'idea che mi è venuta", "title": "titolo breve"}
```

La nota finisce nell'inbox della VPS. Al prossimo "smista l'inbox" dal PC l'agente la
recupera, la assegna a un'area e la archivia.

### 3. Interrogare il brain

Ci sono due motori, e servono a domande diverse:

| Cerchi… | Usa | Perché |
|---|---|---|
| un **nome preciso** o come sono collegate le cose | `graphify query "..."` | naviga la **struttura**: nodi e relazioni |
| un **concetto**, con parole tue | `python tools/search.py "..."` | cerca nel **testo**, anche nelle note `.txt` che il grafo non vede |

- **Dall'agente:** chiedi ("cosa sa il brain su X?"). Con il training AION puoi
  usare `/aion <domanda>` per un ragionamento guidato dal suo protocollo.
- **Da terminale:**
  - struttura → `graphify query "domanda"` (`--graph graphify-out/areas/<area>/graph.json` per una sola area)
  - contenuto → `python tools/search.py "domanda" --area <area> --top 5`
- **Da altri dispositivi:** `GET /v1/query?q=...` (grafo, con router automatico) e
  `GET /v1/search?q=...` (contenuto). Entrambi col token.

> La ricerca funziona subito in modalità **lessicale** (BM25, nessuna dipendenza).
> Per la ricerca **semantica**, che trova anche con parole diverse:
> `pip install sentence-transformers`, poi `python tools/build_dense_index.py`.
> Da quel momento le due ricerche vengono fuse. Il pacchetto pesa circa 2 GB.

### 4. Consultare l'oracolo (solo con AION)
Dall'agente: `/oracle <domanda>`. Il lancio genera sei linee, ricava l'esagramma
dalla sequenza di Re Wen e calcola linee mobili ed esagramma di trasformazione; la
lettura segue il protocollo AION.
Da API: `POST /v1/oracle` con `{"question": "..."}`.

### 5. Far imparare il brain
Le skill registrano una lezione a fine esecuzione. Puoi farlo anche a mano:

```bash
python tools/lesson_log.py --skill manuale --domanda "cosa cercavo" --esito utile --nota "cosa ricordare"
```

Gli esiti sono `utile`, `vicolo-cieco`, `corretto`, `aperto`. Così si registra
un'osservazione. Perché diventi una regola servono anche `--quando`, `--allora` e
`--ancora`, cioè un riscontro esterno (un test, un errore, una misura, una tua
correzione): le istruzioni complete sono in `CLAUDE.md`. Tutto confluisce in
`engine/LESSONS.md`, che l'agente rilegge prima di rispondere.

### 6. Vedere il grafo e la salute del brain
- `graphify-out/index.html` è la pagina d'ingresso: elenca le tre viste e dice a
  quale domanda risponde ciascuna.
- `graphify-out/graph.html`: vista estesa, tutti i nodi.
- `graphify-out/graph-compact.html`: vista compatta, il sistema come processo a 5 fasi.
- `graphify-out/graph-atlas.html`: atlante 3D, quello da aprire per orientarsi: altezza = strato (fonti → sapere → motore → uso), spicchio = macroarea,
  distanza dall'asse = quanto un file è connesso. Doppio click per volare su un nodo,
  `L` per isolare il suo vicinato a 2 passi.
- Da remoto: `GET /v1/views/compact` o `/v1/views/atlas` con il token.
- `metrics/graph_metrics.csv`: l'andamento del brain nel tempo. Se il `grado_medio`
  scende mentre i nodi crescono, stai accumulando note scollegate.

---

## Manutenzione (ogni tanto, non tutti i giorni)

| Comando | Cosa ti dice | Quando |
|---|---|---|
| `python tools/freshness_report.py` | cosa è scaduto e cosa non verifichi da troppo | ogni mese |
| `python tools/check_provenance.py` | affermazioni con numeri e senza fonte | prima di pubblicare un report |
| `python tools/link_suggest.py` | collegamenti mancanti tra pagine affini | dopo aver aggiunto note |
| `python tools/add_frontmatter.py` | note senza provenienza (anteprima; `--apply` per scrivere) | dopo un import |
| `python tools/check_privacy.py` | cosa stai rendendo pubblico (email, segreti, concentrazione) | **prima di ogni push importante** |
| `python tools/resurface.py` | 3 note da rilegge­re, priorita alle isolate | una volta a settimana |
| `python tools/consolidate.py` | digest per area + cosa potare | una volta al mese |

Nessuno di questi modifica le note: propongono, e decidi tu. `link_suggest` non scrive
mai, perché un collegamento sbagliato inserito in automatico passerebbe inosservato.

## Catturare una fonte dal web

```bash
graphify add https://esempio.it/articolo --author "Autore" --contributor "io"
```

Scarica la pagina in `raw/`, ne registra autore e contributore e aggiorna il grafo.
La fonte resta nel brain anche se il link originale smette di funzionare. Poi aggiungi la provenienza con
`python tools/add_frontmatter.py --apply` e rigenera con `rebuild_all`.

> ⚠️ Se il brain finisce in un repo pubblico, anche ciò che scarichi diventa pubblico.
> Usa questo comando solo per contenuti che puoi ridistribuire, e controlla cosa è
> entrato prima del push.

---

## Collegare altre AI al brain

**Claude Desktop (o altri client MCP)** — aggiungi al file di config
(`claude_desktop_config.json`):
```json
{ "mcpServers": { "altair-brain": {
    "command": "python",
    "args": ["<PERCORSO>/altair-brain/server/mcp_server.py"],
    "env": { "ALTAIR_REPO_DIR": "<PERCORSO>/altair-brain" } } } }
```
Serve una volta `pip install mcp`. L'assistente avrà i tool `brain_query`,
`brain_search`, `brain_context`, `brain_feedback` e gli altri elencati in
`server/README.md`.

**Custom GPT (ChatGPT)** — nelle Actions del GPT: importa lo schema da
`https://TUO-DOMINIO/openapi.json`, autenticazione "API Key / Bearer" con il tuo token.

**Qualsiasi altro client HTTP** — usa gli endpoint `/v1/...` con il token
(elenco completo in `server/README.md`).

---

## La VPS (il brain sempre acceso)

- Si aggiorna da GitHub ogni 3 giorni, o subito con `POST /v1/admin/update`.
- Se un servizio si ferma ricevi una notifica push sul telefono: installa l'app
  [ntfy](https://ntfy.sh), scegli un topic segreto (es. `altair-x8k2f9q`), iscriviti
  nell'app e scrivilo in `~/altair-api/.env` come `NTFY_TOPIC=altair-x8k2f9q`.
- I dati scrivibili (feedback, catture) hanno un backup giornaliero automatico.
- Il deploy è descritto passo per passo in `server/README.md`.

---

## Se qualcosa va storto

| Sintomo | Cosa fare |
|---|---|
| La CI su GitHub è rossa ❌ | Il push ha un problema: apri l'errore in GitHub → Actions, o chiedi all'agente di sistemare la CI. Il branch `backup` resta sull'ultimo commit validato. |
| `rebuild_all` fallisce | Leggi quale passo è fallito: dice esattamente cosa rigenerare. |
| L'API risponde 401 | Token sbagliato o mancante nell'header Authorization. |
| L'API risponde 429 | Troppe richieste al minuto: aspetta un attimo. |
| L'API risponde 503 su /query | graphify non è installato su quel server: `pipx install graphifyy`. |
| La VPS sembra "vecchia" | `GET /v1/health` mostra `built_at_commit` e l'età del grafo. Forza: `POST /v1/admin/update`. |

---

## Le regole d'oro (non dimenticarle)

1. **Le pagine generate non si modificano a mano.** Con AION, `wiki/aion/` deriva da
   `engine/aion.model.json`: si cambia il modello e si rigenera.
2. **Un solo comando per rigenerare tutto:** `python tools/rebuild_all.py`.
3. **Il token è un segreto**: mai committarlo, mai condividerlo in chat pubbliche.
4. **Il repo è pubblico.** I brain installati e il registro locale sono esclusi da Git,
   e `tools/check_distribution.py` lo verifica in CI. Credenziali e dati personali
   restano comunque fuori dal repo (`~/altair-data`, dischi locali).
5. Per qualsiasi lavoro nuovo, l'agente deve leggere prima `ROADMAP.md`.
6. **Gli hook NON stanno in git.** Vivono in `.claude/settings.local.json` (ignorato):
   in un repo pubblico un hook versionato eseguirebbe comandi sulla macchina di
   chiunque lo cloni. L'esempio inerte e `.claude/settings.example.json`; per
   attivarlo su una nuova macchina: `cp .claude/settings.example.json .claude/settings.local.json`.
7. **`.agents/` resta versionato**: ogni modifica va dichiarata col marcatore
   `[hooks-ok]` nel commit, o la CI la respinge.

---

## Disaster recovery — ricostruire tutto da zero

Tutto ciò che è generato si ricostruisce da un clone. Se perdi il PC o la VPS, o se
main viene danneggiato:

1. **Repo**: clona `main` da GitHub, oppure il branch `backup`, che punta all'ultimo
   commit passato dalla CI (`git checkout backup`), oppure usa un clone locale o
   della VPS. La CI crea anche un tag settimanale `ripristino-AAAA-wNN`.
2. **Strumenti**: Python 3.12+, `pipx install graphifyy`, `pip install -r
   server/requirements.txt` (versioni pinnate = ricostruzione identica).
3. **Rigenerazione**: `python tools/rebuild_all.py` ricrea grafo, sottografi, viste e
   indice dalle fonti (`raw/`, `wiki/`, `engine/`).
4. **Dati fuori repo** (`~/altair-data`: feedback, catture, lezioni VPS): ripristina
   dall'ultimo `~/backups/altair-data_*.tar.gz` (7 copie locali) o dalla copia
   off-site rclone se configurata (`ALTAIR_RCLONE_REMOTE`).
5. **Se sparisse graphify da PyPI**: il brain resta leggibile (è tutto testo);
   query/grafo si perdono ma nessun contenuto. Sorgente upstream:
   github.com/safishamsi/graphify.

**Prova di ripristino, ogni tre mesi circa:** scompatta l'ultimo archivio di
`~/altair-data` in una cartella temporanea e controlla che i file si aprano; clona il
repo in una cartella nuova e lancia `python tools/rebuild_all.py`. Un backup che non
hai mai ripristinato non sai se funziona.
