# Lezioni apprese — memoria operativa del brain

> GENERATO da `tools/lessons_digest.py` — non editare a mano.
> Fonti: `engine/lessons.jsonl` (skill) + `graphify-out/memory/` (sessioni graphify).
> Passo 0 del reasoner: leggi questo file PRIMA di rispondere; verifica sempre
> prima di fidarti, e riapri i vicoli ciechi se il brain e cambiato da allora.

## Sintesi

- lezioni registrate: **24** · sessioni graphify: **1**
- esiti: 16 utili · 1 vicoli ciechi · 7 correzioni · 0 aperte
- skill piu attive: manuale (9), triage (5), aion (3), atlante-3d (3), oracle (2)
- temi ricorrenti: metodo (5), verifica (4), visualizzazione (3), guardie (3), report (2), oracolo (2), grafo (2), graphify (2)

## Ancoraggi consolidati

_Nodi utili in almeno 2 occasioni: punti di partenza affidabili._

- `test_golden.py` — 2× utile
- `apply_provenance.py` — 2× utile
- `graph_metrics.py` — 2× utile
- `aion-superia` — 2× utile
- `tools/build_atlas_view.py` — 2× utile

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
- `tools/build_views_index.py` — 1× utile

## Vicoli ciechi

_Non hanno portato a nulla in passato. Se il brain e cambiato, vale riprovare._

- `aion-cinematica` — 1× senza esito

## Lezioni recenti

- **2026-08-12** _((triage, utile))_ — Al quinto caso non si tappa il tool: si chiude la classe. 30 tool su 34 erano esposti allo stesso UnicodeEncodeError. Ma rendere OBBLIGATORIO l'import della protezione ha rotto report_update in un mini-repo senza console.py: una protezione facoltativa che impedisce l'avvio e' peggio del guasto che previene, quindi l'import va reso non fatale. Trovata anche un'incoerenza a monte: freshness_report consigliava add_frontmatter --apply su 57 file, ma il tool ne toccava zero (55 in strato generato, 2 fuori copertura). Un rapporto che consiglia un comando inutile insegna a ignorare i rapporti. E TARG
  - contesto: chiudere la classe di guasto della console e verificare tutto il sistema
- **2026-08-12** _((oracle, utile))_ — Tuono che erompe dalla terra: l'energia e' reale e viene dal basso, ma la linea 6 avverte di non farsi travolgere e la trasformazione porta a 23, dove 'non e' propizio andare in alcun luogo'. La condotta indicata e' disciplinare la scarica emotiva con l'esperienza (linea 4), non cavalcarla.
  - contesto: Che condotta tenere davanti a una confluenza di eventi che non controllo: eclissi, terremoti, caldo estremo, eruzioni
- **2026-08-11** _((triage, corretto))_ — Avevo messo due articoli divulgativi in raw/aion con wikilink verso aion-oracle: quattro archi dal materiale d'opinione al modello impersonale. AION deve valere a prescindere da chi lo usa, quindi non puo' incorporare la voce di nessuno. Il corpus ora vive in due sole aree: divulgazione (dove la soggettivita' e' dichiarata) e finanza (dove il contenuto e' materia verificabile). Regola resa eseguibile con 8 test invece che affidata alla memoria. Tolta anche la ridondanza: modello-di-pensiero rielencava 5 mosse su 7 gia' scritte altrove, ora rimanda invece di ripetere.
  - contesto: gli articoli d'opinione non devono contaminare AION, che e' impersonale
- **2026-08-11** _((triage, corretto))_ — Avevo distillato il METODO (come si spiega, onesta argomentativa) credendo bastasse, ma alla prova 'come ragiona e come costruisce un argomento' il brain rispondeva con materiale AION: il modello era nel corpus e in nessuna pagina. Verificare con una domanda reale invece di fidarsi di aver scritto le pagine giuste. Resta un limite lessicale misurato: la domanda generica e' sommersa dai 649 nodi di aion, registrata nel banco semantico. Quarto tool colpito dal guasto cp1252: creato tools/console.py invece di ripetere la toppa.
  - contesto: il brain sa restituire il modello di pensiero dell'autore?
- **2026-08-11** _((triage, utile))_ — Smistare per MATERIA invece che per categoria del sito ha riempito tre aree vuote: finanza 4->37 nodi, divulgazione 10->39, web-design 4->8. La guardia di coesione ha fermato la pipeline perche' le due note aggiunte in raw/aion non linkavano nulla: aggiungere file a un'area coesa senza collegarli la spezza in componenti, e nessuno se ne accorgerebbe guardando. Il verificatore stilometrico contava come prosa il codice in riga e il testo tra virgolette caporali: chiedeva di correggere un anglicismo DENTRO UNA CITAZIONE, cioe' di falsificare la fonte. Terzo caso della stessa classe di difetto dop
  - contesto: ingerire 18 articoli pubblicati da un sito e smistarli per materia nel brain
- **2026-08-11** _((triage, utile))_ — Ricalcolare i numeri dalla fonte invece di riprenderli dalla prosa: qui coincidevano, ma il controllo costa un minuto e rende citabile il risultato. Due difetti trovati usando le guardie del brain sul lavoro vero: style_check.py moriva su console cp1252 prima del verdetto (una freccia bastava) e contava il bersaglio dei wikilink come prosa, chiedendo di correggere il NOME di una pagina. Una classe 'correggi sempre' che segnala identificatori insegna a ignorarla. Nota strutturale: graphify indicizza solo .md, quindi una cartella di soli notebook/PDF non ha nodo e non puo reggere la provenienza:
  - contesto: elaborare il project work di analisi magazzino e inserirlo nella knowledge
- **2026-08-11** _((atlante-3d, utile))_ — Un artefatto puo essere presente e comunque introvabile: graphify-out conteneva tre .html senza alcun indizio su quale aprire. La porta (index.html) dice a quale domanda risponde ogni vista PRIMA del click. Deterministica: i numeri vengono dal grafo, non dal peso dei file (che dipende dalla versione di graphify).
  - contesto: rendere trovabile la visualizzazione dentro la cartella del progetto
- **2026-08-11** _((atlante-3d, utile))_ — Una vista non basta generarla: va DICHIARATA dove il brain si descrive (/v1/health, output di rebuild_all), altrimenti resta invisibile a chi non legge i doc. Health ora dice anche se una vista e rimasta indietro rispetto al grafo: una mappa vecchia non si annuncia da sola. Su fondo nero pieno un pannello nero perde il bordo e sparisce: le superfici vanno sollevate di un soffio sopra il fondo.
  - contesto: atlante come terza vista dichiarata, fondo nero, navigazione
- **2026-08-10** _((atlante-3d, utile))_ — In 3D la posizione deve SIGNIFICARE, altrimenti e' un gomitolo con una dimensione in piu: qui altezza=strato del processo, spicchio=area, raggio=centralita. Due difetti trovati solo misurando il canvas renderizzato, invisibili leggendo il codice: la scala era una costante tarata a mano (il disegno riempiva il 17% della vista) e la tela restava 0x0 se la finestra aveva larghezza 0 al caricamento. Verificare una vista guardando il sorgente non basta: misurare il bounding box dei pixel dipinti su piu risoluzioni.
  - contesto: terza vista del grafo: rappresentazione 3D immersiva ed esplorabile
- **2026-08-10** _((manuale, utile))_ — misurare PRIMA e DOPO su dati reali, e poi provare a SABOTARE il meccanismo: le relazioni I Ching non hanno fuso le community come ipotizzato (il beneficio vero era un altro), e l'anti-clobber di report_harvest sembrava funzionare finche non ho provato a modificare il file in coda
  - contesto: come si verifica che un miglioramento serva davvero
- **2026-08-10** _((manuale, corretto))_ — i piu gravi sono quelli che rendono un componente CREDIBILE ma falso: cache mai invalidata che serviva indici vecchi mentre la confidenza diceva 'alta'; memoria che attribuiva esperienza per sottostringa (sql marchiava postgresql); nodo fantasma con grado 72 invisibile a 68 test
  - contesto: quali difetti sfuggono a test e CI
- **2026-08-10** _((manuale, utile))_ — sei passi: nome ASCII (l'API valida ^[a-z0-9-]+$ e rifiuterebbe gli accenti), areas.json, keyword nel router, wiki curata col METODO non copie, provenienza wiki->raw, ponti intercampo. I wikilink NON attraversano le cartelle: tra aree si usano i bridges
  - contesto: come si integra una nuova macroarea nel brain
