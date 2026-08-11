---
date: 2026-08-11
area: web-design
source: https://www.universalis.it/informatica/filesaver-js
tags: [javascript, front-end, blob, download, api-browser]
reviewed: 2026-08-11
confidence: media
valid_from: 2021-01-06
---
# Filesaver.js

Articolo proprio, pubblicato il **6 gennaio 2021** su universalis.it (~1.200 parole,
registro tecnico-professionale, con codice JavaScript).

**Scopo, dalle parole dell'autore.** «Quante volte ci siamo imbattuti nella necessità
di salvare file dal lato client per le nostre webapp? Grazie alla libreria di "Eli
Gray" ciò diviene semplice e sicuro.»

**Cosa insegna davvero:** come si salva un file **senza passare dal server**. Il
problema e' vecchio quanto le webapp e la risposta e' un'API del browser che quasi
nessuno conosce.

- Implementazione dell'API **W3C FileSaver** tramite il metodo
  `saveAs(data, filename)`.
- Verifica del supporto del browser con `new Blob`; fallback tramite **Blob.js** se
  l'API non c'e'.
- `canvas.toBlob()` per convertire il contenuto di un canvas.
- Salvataggio di documenti XHTML con `XMLSerializer.serializeToString()`.
- Dati binari gestiti con `ArrayBuffer` e `DataView`, usando `setUint8`, `setUint16`,
  `setUint32`.
- Caso particolare del browser Microsoft: `navigator.msSaveOrOpenBlob`.

**Nota di freschezza:** e' del 2021 e il panorama e' cambiato. Il fallback
`navigator.msSaveOrOpenBlob` riguarda browser non piu' in circolazione, e oggi molti
casi si risolvono con `URL.createObjectURL` e l'attributo `download` senza libreria.
Il valore che resta e' la mappa dei concetti — Blob, ArrayBuffer, serializzazione —
non le righe da copiare.

**Licenza:** il sito pubblica sotto Creative Commons Attribuzione – Non commerciale
4.0 Internazionale.
