# Lezioni apprese — memoria operativa del brain

> GENERATO da `tools/lessons_digest.py` — non editare a mano.
> Fonti: `engine/lessons.jsonl` (skill) + `graphify-out/memory/` (sessioni graphify).
> Passo 0 del reasoner: leggi questo file PRIMA di rispondere; verifica sempre
> prima di fidarti, e riapri i vicoli ciechi se il brain e cambiato da allora.

## Sintesi

- lezioni registrate: **11** · sessioni graphify: **1**
- esiti: 6 utili · 1 vicoli ciechi · 4 correzioni · 0 aperte
- skill piu attive: manuale (6), aion (3), report (1), oracle (1)
- temi ricorrenti: metodo (4), report (2), graphify (2), limite (2), corpus (2), living (1), editoriale (1), oracolo (1)

## Ancoraggi consolidati

_Nodi utili in almeno 2 occasioni: punti di partenza affidabili._

- `apply_provenance.py` — 2× utile
- `aion-superia` — 2× utile

## Tentativi (da confermare)

_Visti una volta sola: verifica prima di farci affidamento._

- `6` — 1× utile
- `59` — 1× utile
- `test_golden.py` — 1× utile
- `graph_metrics.py` — 1× utile
- `build_search_index.py` — 1× utile
- `ROADMAP.md` — 1× utile
- `build_dense_index.py` — 1× utile
- `aion-ethos` — 1× utile
- `workflow-analisi-dati` — 1× utile

## Vicoli ciechi

_Non hanno portato a nulla in passato. Se il brain e cambiato, vale riprovare._

- `aion-cinematica` — 1× senza esito

## Lezioni recenti

- **2026-08-08** _((aion, utile))_ — SUPERIA orchestra, ETHOS e sempre attivo come gate: partire da questi due orienta subito
  - contesto: chi decide l'ordine di attivazione degli agenti
- **2026-08-08** _((aion, utile))_ — il workflow in 7 fasi copre dall'import al report
  - contesto: come si struttura un'analisi dati end-to-end
- **2026-08-08** _((aion, vicolo-cieco))_ — descritto ma non eseguibile: non porta a nulla di operativo
  - contesto: quale componente usare per la generazione cinematografica
- **2026-08-07** _((manuale, utile))_ — una voce di roadmap invecchia male se descrive come 'da costruire' cio che e gia costruito: va riscritta con lo STATO reale (fatto/da attivare), il costo vero misurato e il criterio per capire se e servita davvero
  - contesto: dove registrare un miglioramento futuro gia progettato ma non attivato
- **2026-08-07** _((manuale, utile))_ — convertire .txt->.md con git mv ha portato raw/data-science da 4 a 55 nodi e la provenienza da 8 a 31 archi; ma attenzione: cambia anche la strategia di spezzettamento dell'indice (i .md si spezzano per titolo), quindi le note in prosa vanno spezzate a blocchi o collassano in un frammento unico
  - contesto: rendere navigabili nel grafo le note grezze in .txt
- **2026-08-06** _((manuale, utile))_ — il golden set ha trovato in 1 minuto un difetto strutturale invisibile da mesi (raw e wiki con 0 archi tra loro): una misura scritta prima delle feature vale piu di dieci feature
  - contesto: come accorgersi che due strati del brain sono scollegati
- **2026-08-06** _((manuale, corretto))_ — graphify indicizza SOLO .md: 430KB di note .txt in raw/data-science erano invisibili al brain (4 nodi su 1187). Verificare sempre COSA entra nel grafo, non dare per scontato che tutto il corpus ci sia
  - contesto: quale formato indicizza graphify
- **2026-08-06** _((manuale, corretto))_ — una riga che inizia con '#' dentro il front-matter viene letta come titolo markdown e diventa un nodo spurio: testare su UN file e misurare il delta del grafo prima di propagare a 50
  - contesto: aggiungere metadati alle note senza rompere il grafo
- **2026-08-06** _((oracle, utile))_ — l'attribuzione decisionale (--attribuisci) e piu difendibile del lancio casuale in un prodotto editoriale: il seme non spiega nulla al lettore, la motivazione si
  - contesto: quale esagramma per uno stato di conflitto senza vincitore possibile
- **2026-08-06** _((manuale, corretto))_ — grep sul sorgente non prova che il browser mostri il contenuto: servono server locale + lettura del DOM renderizzato (file:// e bloccato nel sandbox)
  - contesto: verificare che una modifica a un file HTML sia davvero visibile
- **2026-08-06** _((report, corretto))_ — aggiornare solo la timeline NON basta: il testo visibile (nodi + campo 'corrente') resta fermo. Servono entrambi, e --set-current per verdetto/conclusioni
  - contesto: aggiornare un report living senza rompere la struttura
