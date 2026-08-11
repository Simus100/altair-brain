---
date: 2026-08-11
area: data-science
source: raw/data-science/PROJECT WORK/Analisi dati magazzino finale/
tags: [magazzino, inventory, pandas, feature-engineering, looker-studio]
reviewed: 2026-08-11
---
# Progetto: Analisi dati di magazzino

Analisi di un catalogo di 990 prodotti alimentari a scaffale, dal CSV grezzo alla
dashboard. E il progetto piu completo in **Python**: due notebook [[jupyter]] separano
la pulizia dall'analisi, e chiudono su una dashboard Looker Studio.

**Cosa contiene il dato**: 16 colonne — anagrafica prodotto e fornitore, quantita a
scaffale, livello e quantita di riordino, prezzo unitario, tre date (ricezione, ultimo
ordine, scadenza), posizione, volume di vendita, indice di rotazione, stato.
Copre circa un anno, da febbraio 2024 a febbraio 2025.

## Il metodo, in due passaggi separati

La separazione e la scelta strutturale: **un notebook che pulisce, uno che analizza**.
Il primo esporta `Dataset_pulito.csv` e finisce li; il secondo riparte da quel file e
non tocca mai il grezzo. Cosi la pulizia si rilegge senza scorrere l'analisi, e
rieseguire l'analisi non rischia di ripulire due volte.

1. **Pulizia** ([[controlli-qualita-dati]], [[data-cleaning]]) — nome di colonna
   sbagliato all'origine (`Catagory`), un unico valore mancante imputato per confronto
   con prodotti omonimi, prezzi da testo con simbolo di valuta a numero, tre colonne
   data da `MM/DD/YYYY` a `datetime`, spazi di bordo, controlli su duplicati e valori
   impossibili. Le ricette sono in [[python-pandas]].
2. **Analisi e colonne derivate** ([[analisi-esplorativa]],
   [[feature-engineering]]) — 13 colonne nuove che trasformano numeri grezzi in
   indicatori gestionali. Il sistema completo e in [[indicatori-magazzino]].

## Cosa e emerso

Numeri ricalcolati da `dataset_finale.csv`, non ripresi dalla prosa dei notebook.

- **465 prodotti su 990 (47%) sono da riordinare o sulla soglia** — 455 sotto il
  livello di riordino, 10 esattamente sul punto. Non e un picco: e quasi meta catalogo.
- **Costo stimato del riordino necessario: 132.851,49**, su un valore di stock a
  scaffale di 332.654,71. Riportare il magazzino sopra soglia costerebbe circa il 40%
  di quanto ci sta gia dentro.
- **Il fabbisogno si concentra**: i primi tre fornitori per costo di riordino
  (Feedbug 2.844,50 · Browsecat 2.780,25 · Viva 2.492,00) sono la leva piu corta se si
  vuole negoziare invece che ordinare a pioggia.
- **325 prodotti (32,8%) sono in `Backordered`**, cioe in arretrato. Il dato dice che
  succede, non di chi sia la colpa: mancano tempi di consegna e date d'ordine.
- **La domanda non guida le scorte.** Incrociando classe di domanda e stato delle
  scorte, la quota da riordinare e praticamente identica nei tre gruppi: 44,9% tra i
  prodotti a domanda alta, 48,7% tra quelli a domanda bassa. Se il riordino seguisse
  la domanda, i due numeri divergerebbero. **E il risultato piu utile del progetto**,
  e si vede solo perche qualcuno ha incrociato due variabili invece di guardarle una
  per volta.
- **96 prodotti (9,7%) sono a rischio alto di obsolescenza** — domanda bassa *e*
  rotazione bassa insieme — e immobilizzano 32.597,33, cioe il 9,8% del capitale.
  Quasi esattamente la loro quota: il rischio non e concentrato sui prodotti di valore.

## Cosa il dato NON poteva dire

La parte piu istruttiva del progetto e dove si e **fermato**. Tre limiti dichiarati
invece che aggirati — il metodo generale e in [[limiti-dichiarati]]:

- **Nessun identificativo di lotto**: `Product_ID` identifica il prodotto, non la
  singola fornitura. Non si puo verificare che ricezione e scadenza appartengano allo
  stesso lotto, e infatti 496 righe su 990 hanno la scadenza *prima* della ricezione.
  Nessuna analisi di durata commerciale e stata calcolata. Le date restano un
  indicatore di qualita del dato, non una misura.
- **`Unit_Price` ambiguo**: il dataset non dice se sia costo d'acquisto o prezzo di
  vendita. Valore di stock e costo di riordino restano quindi **stime dichiarate**.
- **990 posizioni di magazzino distinte su 990 righe**: un indirizzo diverso per ogni
  prodotto, dove ci si aspetterebbe corsie e scaffali ripetuti. Segnalato come
  probabile artificio del dataset invece di costruirci sopra un'analisi spaziale.

Stesso genere di scelta sui fornitori: 990 `Supplier_ID` distinti ma solo 350
`Supplier_Name`, cioe un identificativo per riga. L'aggregazione usa il nome — l'unico
campo che raggruppa davvero — e lo dichiara.

## Uscite

- `dataset_finale.csv` — 990 righe, 29 colonne, pronto per essere messo in pagina.
- Dashboard Looker Studio (link e PDF esportato nella cartella grezza),
  vedi [[struttura-report-analisi]] e [[data-storytelling]].

Collegati:
- [[progetti]]
- [[indicatori-magazzino]]
- [[limiti-dichiarati]]
- [[python-pandas]]
- [[jupyter]]
- [[controlli-qualita-dati]]
- [[data-cleaning]]
- [[analisi-esplorativa]]
- [[feature-engineering]]
- [[quartili-outlier]]
- [[struttura-report-analisi]]
- [[data-storytelling]]
- [[workflow-analisi-dati]]
- [[dataset]]
