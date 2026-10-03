# Audit del sistema Altair Brain — 4 ottobre 2026

Il prodotto è un motore condiviso che serve conoscenze, fonti, relazioni ed esperienze
separate per brain. Graphify estrae e naviga la struttura; la ricerca BM25 recupera
testo; il client AI svolge il ragionamento. AION è un protocollo opzionale adottabile
all'onboarding, non un addestramento dei pesi del modello.

**Esito:** funzionano i percorsi verificati, ma i test preesistenti lasciavano passare
difetti reali di isolamento, conservazione delle note e coerenza delle viste.
Le correzioni sotto sono applicate e protette da regressioni. I miglioramenti della
seconda tabella restano proposte, non promesse di capacità già implementate.

## Verifiche eseguite

Base ispezionata: `a945df8`; working tree inizialmente pulito. Correzioni nel motore
**1.1.1**, con verifica di entrambi i manifesti attraverso `brain_upgrade.py`. Ambiente Windows,
Python 3.13.14 isolato in `test_env/`, Graphify 0.9.2. Verificati anche i pin server:
FastAPI 0.139.0, Uvicorn 0.49.0, MCP 1.28.1.

| Prova | Risultato |
|---|---|
| Suite iniziale | 240 passati, 1 saltato |
| Suite dopo le correzioni | 259 passati, 1 saltato |
| Pipeline completa Aion e Cucina | entrambe completate |
| Installazione autonoma senza training | onboarding e pipeline OK; 81 passati, 41 saltati |
| Installazione autonoma con AION | onboarding e pipeline OK; 149 passati, 31 saltati |
| API su entrambi, in processi separati | health, search, context, route e tre viste: HTTP 200 |
| Autenticazione / training | ricerca senza token: 401; oracle Aion: 200, Cucina: 503 |
| Isolamento su query campione | SUPERIA trovato in Aion, nessun risultato in Cucina |
| Browser | portale, ricerca e selezione nodo esteso, atlante e compatta caricati; nessun errore JS osservato |
| Dipendenze dell'ambiente | pip-audit: 68 pacchetti, nessuna vulnerabilità nota segnalata |

I test saltati nelle installazioni autonome dipendono principalmente da corpus,
plugin, training o registro multi-brain assenti. Alcuni skip sono ancora troppo ampi:
non equivalgono a funzionalità verificate. Rimane un avviso di deprecazione del
TestClient Starlette/httpx, senza fallimenti. Non verificati qui: server Linux reale,
reverse proxy/TLS, deployment Contabo, carico multiutente, scanner della storia Git,
avvio MCP attraverso un client esterno e CI remota di questo commit.

| Brain | Nodi | Archi | Frammenti ricercabili |
|---|---:|---:|---:|
| Aion | 1201 | 1561 | 1862 |
| Cucina | 14 | 10 | 10 |

Entrambi hanno sorgenti esistenti ed estremi degli archi validi. I nodi sono anche
titoli di sezione: il loro numero non misura intelligenza né verità. Per la query
campione `emulsione olio acqua`, 50 ricerche lessicali a cache calda hanno dato una
mediana locale di circa 1,12 ms su Aion e 0,11 ms su Cucina. È una misura limitata,
non un benchmark di scalabilità o di latenza HTTP.

## Difetti corretti

| Rischio | Evidenza prima della correzione | Intervento |
|---|---|---|
| Alto: usare il brain sbagliato | `ALTAIR_BRAIN=brains/non-esiste` selezionava Aion | selezione esplicita e registro errati interrompono l'operazione; controllo anche nel server |
| Alto: perdere note catturate | stesso titolo nello stesso secondo: un solo file, seconda nota sovrascriveva la prima | UUID e creazione esclusiva; test di 20 catture concorrenti; metadati quotati contro newline nel front-matter |
| Alto: perdere il prior curato | `save_feedback` faceva scrivere `graphify reflect` sopra `engine/LESSONS.md` | riflessioni in `graphify-out/reflections/LESSONS.md`; regole curate conservate |
| Medio: viste discordanti | estesa: 1203 nodi/1471 archi; grafo finale: 1201/1561 | sincronizzazione dopo potatura, ponti e provenienza; verifica di nodi e relazioni su tutti i brain registrati |
| Medio: perdere risultati per area | 45 match globali migliori nascondevano l'unico match dell'area richiesta | filtri prima del taglio dei candidati; diagnosi calcolata nello stesso ambito |
| Medio: usare fatti fuori validità | risultati correnti dietro il limite globale; informazioni sulla scadenza perse nel context pack | priorità ai candidati correnti, filtro temporale, esclusione dei fatti futuri, scadenza e sostituzione mantenute nel contesto |
| Medio: falso successo di rebuild | assenza di Graphify poteva essere saltata continuando con artefatti preesistenti | assenza del motore di estrazione interrompe la pipeline |
| Medio: associazioni semantiche sbagliate | vettori densi identificati per posizione senza identità del corpus | impronta SHA-256 ordinata del corpus; indice vecchio ignorato, BM25 resta disponibile |
| Medio: guardie incomplete | sorgenti cancellate ed estremi inesistenti non erano sempre denunciati | controlli dedicati; potatura dei riferimenti AST esterni rimasti isolati dopo la rimozione del codice |
| Basso: errori API | oracle senza DB poteva sollevare errore non gestito; date come 2026-99-99 accettate | 503 esplicito senza training; validazione della data di calendario |

La sincronizzazione della vista conserva l'interfaccia Graphify e le relazioni
multiple. Rifiuta un template upstream incompatibile invece di dichiararlo valido.
Gli indici densi creati prima dell'impronta devono essere rigenerati esplicitamente
con `tools/build_dense_index.py`; non è stato scaricato né attivato un modello
semantico durante questo audit. Il motore lessicale continua a funzionare senza di esso.

## Priorità ancora aperte

| Priorità | Limite verificato nel codice | Miglioramento e prova di accettazione |
|---|---|---|
| P1 | un unico token autorizza lettura, cattura, feedback e `/admin/update`; filtro area e router non sono ACL | separare credenziali/ruoli; test: token lettore riceve 403 su ogni scrittura e amministrazione |
| P1 | rebuild e aggiornamento scrivono molti file sul posto; l'updater usa `reset --hard origin/main` | release in directory temporanea, validazione e switch atomico, lock per brain, rifiuto di modifiche locali prima di aggiornare; fault injection durante ogni fase |
| P1 | parser/template Graphify e dipendenze transitive non hanno un contratto di versione completamente bloccato | lock verificato su Windows e Linux; matrice CI con Graphify installato, pipeline su due brain e installazioni autonome |
| P2 | health usa mtime e una cache legata al solo grafo; può dichiarare `ok` con artefatti mancanti | manifest con hash degli artefatti e stato degraded; test dopo sostituzione/cancellazione di ogni vista |
| P2 | il grafo viene generato prima del digest delle lezioni; un cambio strutturale del digest può essere visto solo al rebuild successivo | ordinare i produttori prima dei consumatori; test: una nuova lezione compare in tutti i derivati dopo un solo rebuild |
| P2 | memoria caricata tutta e poi tagliata; letture integrali JSON, ranking e grafi browser crescono col corpus | benchmark 10k/100k note, lettura JSONL limitata, indici persistenti e viste progressive solo quando i dati giustificano la migrazione |
| P2 | il pacchetto di contesto usa caratteri/4 e conserva almeno un frammento: non è un limite rigoroso per ogni tokenizer | dichiarare il budget stimato e misurare sul tokenizer del client quando disponibile; provare domande lunghe e testi multilingue |
| P2 | l'apprendimento usa feedback dichiarato, non prove indipendenti; alcune annotazioni ignorano supersessione e ambito | revisioni con provenienza e validità, esempi negativi, astensione; separare opinioni, regole operative e fatti |
| P3 | comunità calcolate prima dei ponti, colori non rappresentano causalità; testo del portale cita 64 esagrammi anche senza AION | documentare significato delle relazioni, descrizioni condizionali e ricalcolo controllato delle comunità con confronto prima/dopo |
| P3 | compatta ed estesa dipendono da librerie CDN; l'atlante è autonomo | asset locali versionati e prova offline di tutte le viste |

Non serve introdurre ora un database a grafo esterno solo per aumentare la complessità.
Prima vanno chiusi aggiornamento atomico, ruoli e riproducibilità: sono prerequisiti
per crescere senza compromettere i contenuti. Una suite verde su questo corpus non
certifica correttezza delle fonti, imparzialità del client AI o assenza di vulnerabilità.

## Ripetere le verifiche

Usare un ambiente Python isolato con dipendenze di test (`pytest`, `jsonschema`,
`httpx`) e quelle di `server/requirements.txt`. Graphify verificato: **0.9.2**.
Le pipeline rigenerano artefatti: prima controllare `git status` e revisionare il diff dopo.

```powershell
python -m pytest tests/ -q
python tools/rebuild_all.py
$env:ALTAIR_BRAIN = 'brains/cucina'
python tools/rebuild_all.py
Remove-Item Env:ALTAIR_BRAIN
python -m pytest tests/test_audit_regressions.py tests/test_views_consistency.py -q
python -m pip_audit
```

Per le installazioni pulite copiare `core/` in una cartella temporanea **fuori dalle
directory ignorate da Git**, avviare onboarding con `--aree note --training nessuno`
oppure `--training aion`, poi rebuild e test. Graphify rispetta anche le esclusioni
ereditate dalle cartelle superiori: una prova dentro `test_env/` non simula un export.

Consultata anche la [documentazione upstream di Graphify](https://github.com/Graphify-Labs/graphify):
conferma la distinzione fra estrazione strutturale locale e passaggi semantici tramite
modelli. Nessun aggiornamento automatico all'upstream corrente: l'integrazione locale
va provata sulla versione adottata, senza attribuirle caratteristiche di release diverse.
