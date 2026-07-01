# ROADMAP — guida alle prossime implementazioni

> **Per chi legge (umano o agente AI):** questo documento è l'handoff ufficiale del
> progetto. Contiene tutto ciò che serve per implementare le prossime feature SENZA
> avere il contesto delle sessioni precedenti. Leggi prima `README.md` (cos'è il
> sistema) e la sezione "Regole vincolanti" qui sotto. Aggiorna questo file man mano
> che le implementazioni vengono completate (sposta le voci in "Completato").

---

## Contesto in 10 righe

altair-brain è un second brain personale: conoscenza a macroaree (`areas.json`) su un
knowledge graph (graphify), con modelli di pensiero eseguibili (AION è il primo).
Il **repo è il prodotto**: viene consumato da più canali — assistente AI locale (clone),
VPS con API FastAPI (`server/`, auto-allineata ogni 3 giorni con fetch+reset), e in
futuro altri dispositivi/assistenti. La CI (`.github/workflows/validate.yml`) garantisce
che `main` sia sempre valido, perché i consumatori fanno pull alla cieca.
Stato attuale: infrastruttura solida; area `aion` popolata (raw + wiki generata +
motore `engine/` + skill `/aion` + feedback loop); le altre 4 macroaree sono vuote.

## Regole vincolanti (violarle rompe il sistema)

1. **Nessuna API a pagamento per funzionare.** Tutto deterministico: dati + istruzioni.
   LLM locali (Ollama) o embeddings locali (sentence-transformers) sono ammessi.
2. **`wiki/aion/` è GENERATA** da `engine/aion.model.json` via
   `tools/gen_wiki_from_model.py`. MAI editarla a mano: modifica il modello e rigenera.
   La CI fallisce se wiki e modello divergono.
3. **Workflow dopo ogni modifica** (stesso ordine della CI):
   `python tools/gen_wiki_from_model.py` (se hai toccato il modello) →
   `python tools/validate_model.py` (0 errori) → `graphify update .` →
   `python tools/altair_compact_view.py` → commit+push.
4. **Quirk dei wikilink graphify**: `[[link]]` risolve SOLO nella stessa cartella;
   link a pagine inesistenti vengono scartati in silenzio; tra due pagine resta un solo
   arco (non orientato). Regola pratica: scrivi tutte le pagine, poi rebuild pulito
   (`rm -rf graphify-out/cache graphify-out/graph.json graphify-out/manifest.json && graphify update .`).
5. **Fine-riga LF** su `.sh` `.py` `.service` `.timer` `.json` (`.gitattributes` li
   forza; la CI li verifica). Un CRLF in uno script bash rompe la VPS.
6. **La VPS è un consumatore read-only**: layout a 3 cartelle (`~/altair-brain` repo,
   `~/altair-api` runtime, `~/altair-data` dati scrivibili FUORI dal repo).
   L'auto-update fa `git fetch + reset --hard origin/main`: qualsiasi file scritto
   dentro il repo sulla VPS VIENE CANCELLATO. I dati scrivibili vanno in `~/altair-data`.
7. **Modulo Velario INERTE**: è descritto nel corpus AION (aggiramento di filtri) ma
   NON va implementato né attivato su superfici esposte. Scelta di governance.
8. **graphify** = pacchetto PyPI `graphifyy` (CLI `graphify`), installato con
   `pipx install graphifyy`. Su questa macchina è già installato.
9. **Autenticazione API**: header `Authorization: Bearer <ALTAIR_API_TOKEN>` (o
   `X-API-Key`). Il token vive in `~/altair-api/.env` sulla VPS (mai in git).
10. **Commit**: messaggi in italiano, descrittivi. Push su `main` solo con CI locale
    passata (punto 3). La CI remota è l'ultima rete di sicurezza, non la prima.

---

## PRIORITÀ 0 — Repo privato (azione umana, 2 minuti) ⚠️

**Stato: DA FARE — richiede l'utente, non l'agente.**
Il repo `Simus100/altair-brain` è PUBBLICO (verificato 2026-07-01): chiunque può
leggerlo. Conterrà dati personali → va reso privato: GitHub → Settings → General →
Danger Zone → Change visibility → Private.
Effetti: la deploy key della VPS continua a funzionare; la CI resta gratuita
(2000 min/mese); GitHub Pages non è più disponibile (le viste le serve già l'API
con `/views/extended` e `/views/compact`).

---

## ✅ IMPLEMENTAZIONE 1 — Cattura da ovunque — COMPLETATA (vedi Completato)

**Perché:** un second brain vive o muore sull'attrito di cattura. Oggi si scrive solo
dal PC con l'agente. Serve catturare un pensiero da telefono/altro dispositivo in
2 secondi, e smistarlo dopo.

**Architettura (attenzione al vincolo 6 — repo read-only sulla VPS):**
```
telefono/dispositivo --POST /capture--> VPS scrive in ~/altair-data/inbox/  (FUORI dal repo)
                                                    |
PC di sviluppo  --skill /triage--> GET /inbox (lista) --> smista in raw/<area>/
                                   --> commit+push --> POST /inbox/{id}/done (archivia)
```

**1a. Endpoint API** (in `server/app.py`, stessi pattern di auth esistenti):
- `POST /capture` — body `{"text": str, "title": str|null, "area_hint": str|null,
  "source": str|null}`. Scrive un file MD in `ALTAIR_INBOX_DIR` (nuova env var,
  default `<ALTAIR_MEMORY_DIR>/../inbox`), nome `YYYYMMDD_HHMMSS_<slug-titolo>.md`,
  con frontmatter (data ISO, source, area_hint). Ritorna `{"id": "<filename>"}`.
- `GET /inbox` — lista file pendenti: `[{"id", "created", "title", "area_hint"}]`.
- `GET /inbox/{id}` — contenuto completo del file (validare che `id` sia un filename
  semplice: niente `/` né `..` — path traversal).
- `POST /inbox/{id}/done` — sposta il file in `<inbox>/archive/` (non cancellare mai).
- Aggiorna `server/.env.example` (ALTAIR_INBOX_DIR) e `server/README.md` (tabella endpoint).

**1b. Inbox locale**: crea `raw/_inbox/README.md` che spiega: qui si possono buttare
note grezze anche a mano dal PC; `/triage` le smista. Aggiungi `_inbox` come area
"tecnica" NON in `areas.json` (non è una macroarea). Verifica che graphify non si
rompa con la cartella (al più la indicizza: innocuo).

**1c. Skill `/triage`** (`.claude/skills/triage/SKILL.md`):
1. Raccogli le note pendenti: locali in `raw/_inbox/*.md` (escluso README) e remote
   via `GET /inbox` (chiedi all'utente URL+token se non configurati; se l'API non è
   raggiungibile, procedi solo con le locali).
2. Per ogni nota: leggi, decidi la macroarea guardando `areas.json` (se ambigua,
   chiedi all'utente), normalizza il nome in kebab-case, scrivi in `raw/<area>/`.
3. Esegui il workflow (regola 3), commit+push.
4. Archivia: locali → cancella da `_inbox`; remote → `POST /inbox/{id}/done`.

**Criteri di accettazione:**
- `curl -X POST .../capture` con token crea il file fuori dal repo; senza token → 401.
- `id` con `../` → 400/404 (test path traversal).
- `/triage` con 2 note di prova le smista, il grafo si aggiorna, CI verde.

---

## ✅ IMPLEMENTAZIONE 2 — Server MCP — COMPLETATA (vedi Completato)

**Perché:** MCP è lo standard per collegare assistenti AI a strumenti. Con un server
MCP, Claude Desktop / altri client usano il brain come tool nativi, senza HTTP a mano.

**Cosa costruire:** `server/mcp_server.py`, server MCP **stdio** con SDK ufficiale
Python (`pip install mcp` — gratuito). Gira sulla macchina dove il repo è clonato.
Tool da esporre (riusa la logica di `server/app.py` — estrai le funzioni condivise in
`server/brain_core.py` per non duplicare: subprocess graphify con argomenti a lista,
lettura file del repo):
- `brain_query(q, budget=2000)` → `graphify query`
- `brain_explain(x)` / `brain_path(a, b)` / `brain_affected(x)`
- `brain_model()` → contenuto `engine/aion.model.json`
- `brain_reasoner()` → `engine/aion-reasoner.md`
- `brain_lessons()` → LESSONS.md
- `brain_feedback(question, answer, outcome, nodes=[])` → save-result + reflect

**Config di esempio da documentare** (in `server/README.md`):
```json
{ "mcpServers": { "altair-brain": {
    "command": "python",
    "args": ["/percorso/altair-brain/server/mcp_server.py"],
    "env": { "ALTAIR_REPO_DIR": "/percorso/altair-brain" } } } }
```

**Bonus zero-sforzo da documentare:** FastAPI espone già `/openapi.json` → è lo schema
pronto per le Actions di un Custom GPT (URL + auth Bearer). Aggiungi 5 righe in
`server/README.md` su come collegarlo.

**Criteri di accettazione:**
- `python server/mcp_server.py` parte senza errori; da un client MCP i tool rispondono.
- Nessuna dipendenza a pagamento; `requirements.txt` aggiornato (voce `mcp`).
- `app.py` e `mcp_server.py` condividono `brain_core.py` (niente logica duplicata).

---

## ✅ IMPLEMENTAZIONE 3 — Oracle eseguibile — COMPLETATA (vedi Completato)

**Perché:** primo componente AION che passa da descritto a ESEGUIBILE. Tutto
deterministico, zero API.

**3a. Database:** `tools/build_iching_db.py` che parsa `raw/aion/aion-oracle.md`
(struttura regolare: `## N. <hanzi> <nome> (<pinyin>) <simbolo>` + sezioni `### Struttura`,
`### Relazioni`, `### Tag`, `### Giudizio`, `### Immagine`, `### Interpretazione Moderna`,
`### Linee Mobili`) e genera `engine/iching.db.json`:
```json
{ "lookup_binario": {"111111": 1, "000000": 2, ...},   // dalla Sezione 3.6 (Re Wen!)
  "trigrammi": [ {"simbolo":"☰","nome":"Cielo","binario":"111", ...} ],  // Sezione 3.5
  "esagrammi": [ { "id":1, "nome":"Il Creativo", "hanzi":"乾", "pinyin":"Qián",
      "simbolo":"䷀", "binario":"111111", "trigramma_sup":"☰", "trigramma_inf":"☰",
      "relazioni": {"opposto":2, "rovesciato":1, "nucleare":1},
      "tag": ["leadership","iniziativa",...], "giudizio":"...", "immagine":"...",
      "interpretazione":"...", "linee":["...","...","...","...","...","..."] } ] }
```
**ATTENZIONE:** l'ID NON è binario+1 — la sequenza di Re Wen richiede la tabella di
lookup (Sezione 3.6 del file). Il parser DEVE validare: 64 esagrammi, 64 voci lookup,
ogni relazione punta a un id 1-64, 6 linee per esagramma. Exit code ≠ 0 se qualcosa manca.

**3b. Endpoint API** (in `server/app.py`):
- `POST /oracle` — body `{"question": str|null, "seed": int|null}`. Lancia 6 valori
  casuali in {6,7,8,9} (seed opzionale per riproducibilità), calcola esagramma
  primario (lookup), linee mobili (6 e 9), esagramma secondario (mutazione 6→7, 9→8),
  applica le regole di selezione della linea (1 mobile→quella; 2→la yin; 3→mediana;
  4→la più alta fissa; 6→solo secondo esagramma — sono nella Sezione 1 del file
  oracle) e ritorna la lettura completa dal DB.
- `GET /oracle/hexagram/{id}` — scheda completa di un esagramma (1-64).

**3c. Skill `/oracle`** (opzionale): `.claude/skills/oracle/SKILL.md` che fa il lancio
in locale leggendo `engine/iching.db.json` (stessa logica, senza API).

**Criteri di accettazione:**
- `python tools/build_iching_db.py` genera il DB e valida 64/64; aggiungilo alla CI.
- `POST /oracle` con `seed` fisso dà sempre la stessa lettura (test deterministico).
- Esagramma 1 con binario `111111` → id 1; `000000` → id 2 (test lookup Re Wen).

---

## ✅ IMPLEMENTAZIONE 4 — Guardie di qualita — COMPLETATA (vedi Completato)

**4a. `tools/graph_health.py`:** legge `graphify-out/graph.json` (committato) e
fallisce (exit 1) se: i nodi di `wiki/aion` non formano 1 solo componente connesso;
i nodi di `raw/aion` non formano 1 solo componente; esistono nodi con grado 0 sotto
`raw/` `wiki/` `engine/`. Stampa un report sintetico. Aggiungi step alla CI.

**4b. Test API:** `tests/test_api.py` con `fastapi.testclient.TestClient`
(dipendenze test: `pytest`, `httpx`):
- `/health` → 200 anche senza token;
- `/model` senza token → 401; con token (env `ALTAIR_API_TOKEN=test` nel test) → 200;
- `/query` senza graphify disponibile → 503 (comportamento degradato corretto);
- path traversal su eventuale `/inbox/{id}` → respinto.
Aggiungi step CI: `pip install fastapi httpx pytest && pytest -q`.

---

## ✅ INFRASTRUTTURA 2.0 — COMPLETATA 2026-07-01 (vedi Completato; le spec restano come riferimento)

**I2.1 — Router + sottografi per area (priorità alta appena c'è una 2ª area).**
Un solo `graph.json` monolitico non scala (traversal lenti, viz inusabile a 10k+ nodi)
e lo scope di sicurezza per-area come "filtro sui risultati" è fragile. Architettura:
- genera `graphify-out/areas/<area>/graph.json` (sottografo per macroarea; un tool in
  `tools/` che partiziona per prefisso `source_file`, oppure run graphify per-cartella);
- `engine/router.json`: tabella di routing machine-readable
  `{area: {keywords[], descrizione, budget_default}}` — il router deterministico
  (match keyword; embeddings locali in futuro) decide quale/i grafo/i interrogare;
- API: `/query?area=` usa `--graph graphify-out/areas/<area>/graph.json`; senza `area`,
  il router decide. Scope di sicurezza = QUALE FILE puoi leggere (per costruzione),
  non un filtro. Regola ponti: nodo-ponte visibile solo se il chiamante vede entrambe le aree;
- vista globale on-demand: `graphify merge-graphs` (gia nel CLI).

**I2.2 — Guardia anti-regressione del grafo in CI.**
Il workflow fa `rm graph.json` prima del rebuild, quindi BYPASSA la protezione nativa
di graphify (fewer nodes → --force). Aggiungere a `tools/graph_health.py`: confronto
col graph.json del commit precedente (`git show HEAD~1:graphify-out/graph.json`);
se i nodi calano oltre il 20% senza flag esplicito → exit 1.

**I2.3 — Notifiche di guasto (VPS autonoma = VPS che sa chiedere aiuto).**
`OnFailure=altair-notify@%n.service` sulle unit; la unit di notifica manda un push via
ntfy.sh (gratuito, senza account): `curl -d "altair-brain: %i FALLITO" ntfy.sh/<topic-segreto>`.
Silenzio ≠ successo: senza questo, un update rotto passa inosservato per giorni.

**I2.4 — `/health` arricchito (staleness detection).**
Esporre: `built_at_commit` (gia dentro graph.json), conteggio nodi/edge, mtime del
grafo, versione modello. I client rilevano da soli un brain stantio.

**I2.5 — Backup `~/altair-data` (unico dato NON protetto da GitHub).**
Timer systemd giornaliero: tar con rotazione (7 copie) in `~/backups/`, o rclone verso
storage esterno. Feedback/lezioni/catture della VPS oggi hanno zero copie.

**I2.6 — Contratto del modello: `schema_version` + JSON Schema.**
Aggiungere `schema_version` a `engine/aion.model.json` e creare
`engine/schema/aion.model.schema.json`; la CI valida il modello contro lo schema
(`pip install jsonschema`). I sistemi esterni ottengono un contratto versionato:
il modello puo evolvere senza rompere i client.

**I2.7 — API versionata `/v1/` + rate limiting basilare.**
Prefissare gli endpoint con `/v1/` (mantenere alias non versionati per compatibilita
finche serve). Rate limiting: middleware semplice in-app o plugin Caddy. Costa zero
ora, evita breaking change quando i client saranno molti.

**I2.8 — Merge driver graphify per lavoro multi-macchina.**
Quando si scrivera da piu PC, i conflitti git su graph.json sono ingestibili a mano.
graphify ha gia la soluzione: `graphify hook install` (post-commit/post-checkout +
merge driver union). Cablarlo e documentarlo in README.

**I2.9 — Front-matter standard per le note raw.**
Convenzione YAML in testa a ogni nota (`date`, `source`, `tags`, `area`): prepara
provenienza e ricerca semantica prima che ci siano mille note da retrofittare.
Documentare in `raw/README.md` + template.

Ordine consigliato: I2.3 e I2.6 subito (costano poco, proteggono molto); I2.2 nella
prossima passata CI; I2.1 appena esiste la seconda macroarea popolata; il resto a seguire.

## DOPO che le macroaree saranno popolate (non prima)

- **Ricerca semantica locale**: `sentence-transformers` (gratuito) per un indice
  embeddings di `raw/` e `wiki/` → endpoint `/search?q=` che trova per significato.
  I ponti intercampo emergono anche senza nomi identici. Peso: modello ~100MB, ok VPS.
- **Scope per-area sui token**: più token, ognuno con lista di aree leggibili;
  il gate filtra i risultati per `source_file` prefix. Regola ponti: un nodo-ponte è
  visibile solo se il chiamante vede ENTRAMBE le aree che collega.
- **`/reason` con LLM locale** (Ollama sulla VPS): esegue il protocollo
  `engine/aion-reasoner.md` lato server. Solo modelli locali (vincolo 1).
- **Fisiologia AION in wiki**: estendere `engine/aion.model.json` con una sezione
  `processi` (pipeline 9 passi, SFO, FCC, Moduli 3-6) e fare in modo che
  `gen_wiki_from_model.py` generi anche quelle pagine (fonte unica, regola 2).
- **Sync lezioni VPS→repo**: le LESSONS della VPS vivono in `~/altair-data` e non
  tornano indietro. Possibile endpoint `GET /memory/export` + merge manuale periodico.

---

## Completato (storico, per orientamento)

- **Impl 1 — Cattura da ovunque** (2026-07-01): `POST /v1/capture`, `GET /v1/inbox`,
  `/v1/inbox/{id}`, `/v1/inbox/{id}/done` (anti path-traversal, limite 100KB);
  `raw/_inbox/` locale; skill `/triage`. Inbox VPS fuori dal repo (`ALTAIR_INBOX_DIR`).
- **Impl 2 — Server MCP** (2026-07-01): `server/mcp_server.py` (stdio, SDK `mcp`) con
  tool brain_query/explain/path/model/reasoner/lessons/oracle/feedback; logica condivisa
  in `server/brain_core.py` (zero duplicazione con app.py). Actions Custom GPT via
  `/openapi.json` documentate.
- **Impl 3 — Oracle eseguibile** (2026-07-01): `tools/build_iching_db.py` →
  `engine/iching.db.json` (64/64 validati, lookup Re Wen, cross-check binario↔id);
  `tools/oracle_cast.py` (cast deterministico seedabile, regole linee mobili);
  `POST /v1/oracle`, `GET /v1/oracle/hexagram/{id}`; skill `/oracle`. Coerenza in CI.
- **Impl 4 — Guardie qualita** (2026-07-01): `tools/graph_health.py` (coesione wiki/raw,
  orfani, anti-regressione vs HEAD~1 con override ALTAIR_ALLOW_SHRINK);
  `tests/test_api.py` (11 test: auth, degradazione, oracle, inbox, traversal); CI estesa.
- **I2.1 Router+sottografi** (2026-07-01): `engine/router.json`,
  `tools/build_area_graphs.py` → `graphify-out/areas/<area>/graph.json` + `bridges.json`;
  `/v1/query?area=` con routing automatico (header X-Altair-Area), `/v1/route`, `/v1/areas`.
- **I2.2** anti-regressione (in graph_health, CI con fetch-depth 2). **I2.3** notifiche
  ntfy (`altair-notify@.service`, OnFailure su api/update/backup). **I2.4** `/health`
  arricchito (nodi, built_at_commit, eta, modello, aree). **I2.5** backup
  (`backup_data.sh` + timer giornaliero, 7 copie). **I2.6** `schema_version` +
  `engine/schema/aion.model.schema.json` validato in CI. **I2.7** API `/v1/` (alias
  legacy) + rate limit per IP + auth constant-time. **I2.8** merge driver graphify:
  configurato ESPLICITAMENTE (niente `graphify hook install`: i suoi hook post-commit
  rilanciano rebuild in background e sporcano l'albero). Su ogni nuova macchina di
  scrittura eseguire una volta:
  `git config merge.graphify.name "graphify graph union merge"` e
  `git config merge.graphify.driver "graphify merge-driver %O %A %B"`
  (il binding e gia in .gitattributes: `graphify-out/graph.json merge=graphify`). **I2.9** front-matter standard documentato in `raw/README.md`.
- **`tools/rebuild_all.py`**: un comando per l'intera pipeline (usato da GUIDA e skill).
- **`GUIDA.md`**: manuale d'uso per umani (newbie-friendly).

### Storico precedente

- Strato 1-2-3 AION: `raw/aion` (6 doc interconnessi) → `wiki/aion` (55 pagine
  GENERATE) → `engine/` (modello tipizzato + reasoner 9 passi + skill `/aion`).
- I Ching v. ristrutturata (`raw/aion/aion-oracle.md`) con lookup Re Wen corretto.
- Feedback loop: `graphify save-result` → `reflect` → `LESSONS.md` (passo 0 del reasoner).
- Due viste: estesa (`graph.html`) + compatta strutturale (`graph-compact.html`,
  `tools/altair_compact_view.py`).
- Fonte unica di verità + validatore (`tools/validate_model.py`) + CI.
- Stack VPS: `server/` (FastAPI, bootstrap, systemd, Caddy, client di test),
  auto-update 3 giorni, layout 3 cartelle. Guida deploy: prompt in `server/README.md`.
