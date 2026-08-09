---
date: 2026-08-09
area: creativita
source: raw/creativita/bookforge/ (sistema BookForge v7.6.1)
tags: [bookforge, scrittura, indice, metodo]
reviewed: 2026-08-09
---
# Creatività — scrittura ed editoria

Macroarea orientata al **metodo di scrittura**, non ai testi prodotti: come si scrive
prosa che valga la pena leggere, e come si verifica che lo sia. La stessa logica per
cui `workflow-analisi-dati` (area data-science) conserva il metodo e non i dataset.

Il corpo del sapere e **BookForge**, un sistema per scrivere libri con l'AI: sei fasi
dal questionario strategico alla pubblicazione, con una parte notevole per il brain —
lo stile e trattato come **grandezza misurabile**, non come gusto.

## I quattro pilastri

- [[styledna]] — lo stile come vettore a 12 assi: preset per genere, tetti di salute,
  deroghe che si guadagnano con una prova, non si dichiarano.
- [[stilometria]] — la verifica **eseguibile**: `tools/style_check.py` misura la prosa
  e distingue cio che si corregge sempre da cio che si guarda soltanto.
- [[anti-ai]] — cosa fa suonare artificiale un testo, e i due fallimenti opposti
  (genericita e manierismo). Si apre in revisione, mai in stesura.
- [[carta-della-prosa]] — l'unica dottrina attiva mentre si scrive: imperativi positivi.

## Il processo

- [[fasi-editoriali]] — le sei fasi, dalla scheda strategica alla revisione.
- [[granularita-scrittura]] — le tre tacche di controllo: capitolo, scena, beat.
- [[psicologia-personaggio]] — coerenza dei personaggi su 9 assi (fiction).
- [[stato-narrativo]] — cosa va ricordato tra un capitolo e l'altro perche la storia tenga.

## Perche riguarda tutto il brain

Il brain **scrive**: report editoriali, pagine curate, note di metodo. Finora nessuno
verificava se quella prosa suonasse artificiale. Ora la perizia di BookForge si applica
a qualunque testo: `python tools/style_check.py <file>`. Ponte diretto con
`aion-fabulatorium` (narrazione simbolica) e `livello-orchestrazione-stile` di AION —
ponti intercampo dichiarati in `engine/bridges.json`, perché i collegamenti a doppia
parentesi risolvono solo dentro la stessa cartella.
