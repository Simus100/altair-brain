# Lezioni apprese — memoria operativa del brain

> GENERATO da `tools/lessons_digest.py` — non editare a mano.
> Fonti: `engine/lessons.jsonl` (skill) + `graphify-out/memory/` (sessioni graphify).
> Passo 0 del reasoner: leggi questo file PRIMA di rispondere; verifica sempre
> prima di fidarti, e riapri i vicoli ciechi se il brain e cambiato da allora.

## Sintesi

- lezioni registrate: **15** · sessioni graphify: **1**
- esiti: 9 utili · 1 vicoli ciechi · 5 correzioni · 0 aperte
- skill piu attive: manuale (9), aion (3), report (1), oracle (1), scrivi (1)
- temi ricorrenti: metodo (5), report (2), verifica (2), graphify (2), limite (2), corpus (2), living (1), editoriale (1)

## Ancoraggi consolidati

_Nodi utili in almeno 2 occasioni: punti di partenza affidabili._

- `test_golden.py` — 2× utile
- `apply_provenance.py` — 2× utile
- `graph_metrics.py` — 2× utile
- `aion-superia` — 2× utile

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

## Vicoli ciechi

_Non hanno portato a nulla in passato. Se il brain e cambiato, vale riprovare._

- `aion-cinematica` — 1× senza esito

## Lezioni recenti

- **2026-08-10** _((manuale, utile))_ — misurare PRIMA e DOPO su dati reali, e poi provare a SABOTARE il meccanismo: le relazioni I Ching non hanno fuso le community come ipotizzato (il beneficio vero era un altro), e l'anti-clobber di report_harvest sembrava funzionare finche non ho provato a modificare il file in coda
  - contesto: come si verifica che un miglioramento serva davvero
- **2026-08-10** _((manuale, corretto))_ — i piu gravi sono quelli che rendono un componente CREDIBILE ma falso: cache mai invalidata che serviva indici vecchi mentre la confidenza diceva 'alta'; memoria che attribuiva esperienza per sottostringa (sql marchiava postgresql); nodo fantasma con grado 72 invisibile a 68 test
  - contesto: quali difetti sfuggono a test e CI
- **2026-08-10** _((manuale, utile))_ — sei passi: nome ASCII (l'API valida ^[a-z0-9-]+$ e rifiuterebbe gli accenti), areas.json, keyword nel router, wiki curata col METODO non copie, provenienza wiki->raw, ponti intercampo. I wikilink NON attraversano le cartelle: tra aree si usano i bridges
  - contesto: come si integra una nuova macroarea nel brain
- **2026-08-10** _((scrivi, utile))_ — l'ordine e vincolante: in stesura solo la Carta (imperativi positivi), l'elenco dei tic si apre SOLO in revisione — un regolamento attivo durante il draft produce scrittura difensiva. Poi perizia eseguibile e budget di 10 interventi: la revisione illimitata toglie i difetti e la vita insieme
  - contesto: come evitare che la prosa del brain suoni artificiale
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
