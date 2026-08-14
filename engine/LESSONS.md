# Lezioni apprese — memoria operativa del brain

> GENERATO da `tools/lessons_digest.py` — non editare a mano.
> Fonti: `engine/lessons.jsonl` (skill) + `graphify-out/memory/` (sessioni graphify).
> Passo 0 del reasoner: leggi questo file PRIMA di rispondere; verifica sempre
> prima di fidarti, e riapri i vicoli ciechi se il brain e cambiato da allora.

## Sintesi

- lezioni registrate: **31** · sessioni graphify: **1**
- esiti: 23 utili · 1 vicoli ciechi · 7 correzioni · 0 aperte
- skill piu attive: manuale (14), triage (7), aion (3), atlante-3d (3), oracle (2)
- temi ricorrenti: verifica (5), metodo (5), architettura (4), grafo (3), visualizzazione (3), guardie (3), separazione (3), report (2)

## Ancoraggi consolidati

_Nodi utili in almeno 2 occasioni: punti di partenza affidabili._

- `test_golden.py` — 2× utile
- `apply_provenance.py` — 2× utile
- `graph_metrics.py` — 2× utile
- `aion-superia` — 2× utile
- `tools/build_atlas_view.py` — 2× utile
- `tools/build_views_index.py` — 2× utile
- `tools/console.py` — 2× utile
- `tests/test_console.py` — 2× utile
- `tools/graph_health.py` — 2× utile

## Tentativi (da confermare)

_Visti una volta sola: verifica prima di farci affidamento._

- `6` — 1× utile
- `59` — 1× utile
- `build_search_index.py` — 1× utile
- `ROADMAP.md` — 1× utile
- `build_dense_index.py` — 1× utile
- `aion-ethos` — 1× utile
- `workflow-analisi-dati` — 1× utile
- `apply_iching_relations.py` — 1× utile
- `areas.json` — 1× utile
- `provenance.json` — 1× utile
- `bridges.json` — 1× utile
- `router.json` — 1× utile
- `style_check.py` — 1× utile
- `carta-della-prosa` — 1× utile
- `anti-ai` — 1× utile
- `tests/test_atlas.py` — 1× utile
- `graphify-out/graph-atlas.html` — 1× utile
- `server/brain_core.py` — 1× utile
- `tools/rebuild_all.py` — 1× utile
- `graphify-out/index.html` — 1× utile

## Vicoli ciechi

_Non hanno portato a nulla in passato. Se il brain e cambiato, vale riprovare._

- `aion-cinematica` — 1× senza esito

## Regole operative

_Ognuna porta il proprio appiglio esterno: un test, un errore, una misura, una correzione. Se non lo porta, non e qui._

- **Quando** verifichi un'architettura multi-istanza con copie temporanee → **creane una VERA e lasciala: le copie usa-e-getta nascondono i difetti che nascono dalla convivenza**
  - appiglio: `guardia: creando brains/cucina sono emersi 3 difetti che 6 prove isolate non avevano mostrato — baseline git tra brain, nome dell'istanza, selettore`
- **Quando** un repo ospita insieme motore, prodotto generato e istanze → **togli gli artefatti dal grafo subito dopo l'indicizzazione: il rumore cresce con ogni istanza creata**
  - appiglio: `misura: core/ pesava 1191 nodi su 3084, il 39% del grafo, prima della potatura`
- **Quando** separi un motore riusabile da un brain personale → **genera l'export invece di copiarlo, e mettici una guardia che cerca contenuto personale: la copia diverge e la fuga non si vede a occhio**
  - appiglio: `guardia: il test dell'export ha trovato 8 fughe (bookforge, iran, styledna, universalis) in tool e test che sembravano generici`
- **Quando** progetti una memoria che si autoalimenta dagli output del modello → **pretendi un appiglio esterno per ogni regola e metti un tetto al prior: senza, degenera per autofagia o per context rot**
  - appiglio: `misura: il passo 0 leggeva un file di 495 byte fermo dal 1 luglio mentre il digest vero era 8.6 KB in engine/`
- **Quando** aggiungi file a un'area con invariante di coesione (raw/aion) → **collegali con wikilink alle note esistenti PRIMA di rigenerare, o l'area si spezza**
  - appiglio: `guardia: graph_health ha fermato rebuild_all con 'raw/aion/: 3 componenti connessi (atteso 1) su 539 nodi'`
- **Quando** introduci un import comune in molti tool (es. tools/console) → **rendilo NON fatale con try/except ImportError: una protezione facoltativa non deve impedire l'avvio**
  - appiglio: `test: test_report_update_verdict_set_current e test_report_update_nodo_e_sync_prototipo sono passati da rosso a verde`
- **Quando** entra materiale che porta posizioni personali (articoli, opinioni) → **tienilo fuori da raw/aion: AION deve valere a prescindere da chi lo usa**
  - appiglio: `utente: 'non devono influire su aion... non di aion che e imparziale'`

## Osservazioni recenti

_Senza appiglio esterno: contesto, non regole. Da verificare prima di farci affidamento._

- **2026-08-12** _((triage, utile))_ — Al quinto caso non si tappa il tool: si chiude la classe. 30 tool su 34 erano esposti allo stesso UnicodeEncodeError. Ma rendere OBBLIGATORIO l'import della protezione ha rotto report_update in un mini-repo senza console.py: una protezione facoltativa che impedisce l'avvio e' peggio del guasto che previene, quindi l'import va reso non fatale. Trovata anche un'incoerenza a monte: freshness_report consigliava add_frontmatter --apply su 57 file, ma il tool ne toccava zero (55 in strato generato, 2 fuori copertura). Un rapporto che consiglia un comando inutile insegna a ignorare i rapporti. E TARG
- **2026-08-12** _((oracle, utile))_ — Tuono che erompe dalla terra: l'energia e' reale e viene dal basso, ma la linea 6 avverte di non farsi travolgere e la trasformazione porta a 23, dove 'non e' propizio andare in alcun luogo'. La condotta indicata e' disciplinare la scarica emotiva con l'esperienza (linea 4), non cavalcarla.
- **2026-08-11** _((triage, corretto))_ — Avevo messo due articoli divulgativi in raw/aion con wikilink verso aion-oracle: quattro archi dal materiale d'opinione al modello impersonale. AION deve valere a prescindere da chi lo usa, quindi non puo' incorporare la voce di nessuno. Il corpus ora vive in due sole aree: divulgazione (dove la soggettivita' e' dichiarata) e finanza (dove il contenuto e' materia verificabile). Regola resa eseguibile con 8 test invece che affidata alla memoria. Tolta anche la ridondanza: modello-di-pensiero rielencava 5 mosse su 7 gia' scritte altrove, ora rimanda invece di ripetere.
- **2026-08-11** _((triage, corretto))_ — Avevo distillato il METODO (come si spiega, onesta argomentativa) credendo bastasse, ma alla prova 'come ragiona e come costruisce un argomento' il brain rispondeva con materiale AION: il modello era nel corpus e in nessuna pagina. Verificare con una domanda reale invece di fidarsi di aver scritto le pagine giuste. Resta un limite lessicale misurato: la domanda generica e' sommersa dai 649 nodi di aion, registrata nel banco semantico. Quarto tool colpito dal guasto cp1252: creato tools/console.py invece di ripetere la toppa.
- **2026-08-11** _((triage, utile))_ — Smistare per MATERIA invece che per categoria del sito ha riempito tre aree vuote: finanza 4->37 nodi, divulgazione 10->39, web-design 4->8. La guardia di coesione ha fermato la pipeline perche' le due note aggiunte in raw/aion non linkavano nulla: aggiungere file a un'area coesa senza collegarli la spezza in componenti, e nessuno se ne accorgerebbe guardando. Il verificatore stilometrico contava come prosa il codice in riga e il testo tra virgolette caporali: chiedeva di correggere un anglicismo DENTRO UNA CITAZIONE, cioe' di falsificare la fonte. Terzo caso della stessa classe di difetto dop
- **2026-08-11** _((triage, utile))_ — Ricalcolare i numeri dalla fonte invece di riprenderli dalla prosa: qui coincidevano, ma il controllo costa un minuto e rende citabile il risultato. Due difetti trovati usando le guardie del brain sul lavoro vero: style_check.py moriva su console cp1252 prima del verdetto (una freccia bastava) e contava il bersaglio dei wikilink come prosa, chiedendo di correggere il NOME di una pagina. Una classe 'correggi sempre' che segnala identificatori insegna a ignorarla. Nota strutturale: graphify indicizza solo .md, quindi una cartella di soli notebook/PDF non ha nodo e non puo reggere la provenienza:
- **2026-08-11** _((atlante-3d, utile))_ — Un artefatto puo essere presente e comunque introvabile: graphify-out conteneva tre .html senza alcun indizio su quale aprire. La porta (index.html) dice a quale domanda risponde ogni vista PRIMA del click. Deterministica: i numeri vengono dal grafo, non dal peso dei file (che dipende dalla versione di graphify).
- **2026-08-11** _((atlante-3d, utile))_ — Una vista non basta generarla: va DICHIARATA dove il brain si descrive (/v1/health, output di rebuild_all), altrimenti resta invisibile a chi non legge i doc. Health ora dice anche se una vista e rimasta indietro rispetto al grafo: una mappa vecchia non si annuncia da sola. Su fondo nero pieno un pannello nero perde il bordo e sparisce: le superfici vanno sollevate di un soffio sopra il fondo.
- **2026-08-10** _((atlante-3d, utile))_ — In 3D la posizione deve SIGNIFICARE, altrimenti e' un gomitolo con una dimensione in piu: qui altezza=strato del processo, spicchio=area, raggio=centralita. Due difetti trovati solo misurando il canvas renderizzato, invisibili leggendo il codice: la scala era una costante tarata a mano (il disegno riempiva il 17% della vista) e la tela restava 0x0 se la finestra aveva larghezza 0 al caricamento. Verificare una vista guardando il sorgente non basta: misurare il bounding box dei pixel dipinti su piu risoluzioni.
- **2026-08-10** _((manuale, utile))_ — misurare PRIMA e DOPO su dati reali, e poi provare a SABOTARE il meccanismo: le relazioni I Ching non hanno fuso le community come ipotizzato (il beneficio vero era un altro), e l'anti-clobber di report_harvest sembrava funzionare finche non ho provato a modificare il file in coda
- **2026-08-10** _((manuale, corretto))_ — i piu gravi sono quelli che rendono un componente CREDIBILE ma falso: cache mai invalidata che serviva indici vecchi mentre la confidenza diceva 'alta'; memoria che attribuiva esperienza per sottostringa (sql marchiava postgresql); nodo fantasma con grado 72 invisibile a 68 test
- **2026-08-10** _((manuale, utile))_ — sei passi: nome ASCII (l'API valida ^[a-z0-9-]+$ e rifiuterebbe gli accenti), areas.json, keyword nel router, wiki curata col METODO non copie, provenienza wiki->raw, ponti intercampo. I wikilink NON attraversano le cartelle: tra aree si usano i bridges
