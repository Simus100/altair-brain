---
date: 2026-08-11
area: data-science
source: project work personale — analisi dati di magazzino
tags: [magazzino, inventory, pandas, jupyter, looker-studio]
reviewed: 2026-08-11
---
# Project work — Analisi dati di magazzino

Materiale grezzo del project work sull'analisi di un magazzino alimentare: 990
prodotti, dal CSV originale alla dashboard. La conoscenza distillata sta in
`wiki/data-science/progetto-magazzino.md`, `indicatori-magazzino.md`,
`limiti-dichiarati.md` e `python-pandas.md`.

Questa nota esiste anche per una ragione tecnica: **graphify indicizza solo i `.md`**.
Senza un file di testo in questa cartella, notebook, CSV e PDF non sarebbero nodi del
grafo e la catena fonte → conoscenza non potrebbe essere cucita
(`engine/provenance.json`).

## Cosa c'e in `MACELLONI_SIMONE_Analisi Dati di magazzino/`

| File | Cosa contiene |
|---|---|
| `01_pulizia_dati_magazzino.ipynb` | pulizia e preparazione: tipi, mancanti, duplicati, valuta, date, controlli di coerenza, IQR sui prezzi. Esporta `Dataset_pulito.csv` |
| `02_analisi_esplorativa_feature_eng.ipynb` | analisi esplorativa e 13 colonne derivate: scorte, valore, riordino, domanda, rotazione, rischio. Esporta `dataset_finale.csv` |
| `Dataset.csv` | dato originale: 990 righe, 16 colonne |
| `dataset processati/Dataset_pulito.csv` | uscita del primo notebook |
| `dataset processati/dataset_finale.csv` | uscita del secondo: 990 righe, 29 colonne |
| `Documentazione.pdf` | relazione scritta del progetto |
| `dashboard_pdf.pdf` | esportazione della dashboard |
| `link dashboard interattiva looker studio.txt` | indirizzo della dashboard Looker Studio |

## Il dato in breve

Catalogo alimentare a scaffale, febbraio 2024 – febbraio 2025. Anagrafica prodotto e
fornitore, quantita disponibile, livello e quantita di riordino, prezzo unitario, tre
date (ricezione, ultimo ordine, scadenza), posizione di magazzino, volume di vendita,
indice di rotazione, stato (`Active` / `Backordered` / `Discontinued`).

## Avvertenze sulla fonte

Il dataset presenta segni di generazione artificiale — 990 posizioni di magazzino
distinte su 990 righe, un `Supplier_ID` diverso per ogni riga — e 496 righe in cui la
scadenza precede la ricezione. **Il metodo estratto resta valido; i numeri descrivono
questo dataset e non un magazzino reale.** I limiti sono trattati come materia di
metodo in `wiki/data-science/limiti-dichiarati.md`.

I due PDF non sono stati letti in fase di distillazione (font a codifica propria, non
estraibili senza una libreria dedicata): la conoscenza in wiki deriva dai due notebook
e dal ricalcolo diretto su `dataset_finale.csv`.
