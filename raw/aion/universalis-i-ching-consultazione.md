---
date: 2026-08-11
area: aion
source: https://www.universalis.it/filosofia/i-ching
tags: [i-ching, oracolo, esagrammi, linee-mobili, sincronicita]
reviewed: 2026-08-11
---
# I Ching: 1. Consultazione

Articolo proprio, pubblicato il **20 giugno 2022** su universalis.it (~2.200 parole,
registro divulgativo-tecnico). Prima puntata, insieme a
`universalis-i-ching-trigrammi.md`.

**Perche' sta qui.** Il brain ha gia' l'oracolo eseguibile (`aion-oracle.md`,
`engine/iching.db.json`, `tools/oracle_cast.py`). Questa nota e' la fonte *esterna e
divulgativa* dello stesso sistema: dove il materiale interno definisce il meccanismo,
qui c'e' il modo in cui l'autore lo spiega a chi non lo conosce.

**Tesi.** «L'I Ching deve essere consultato formulando domande che riguardano la
propria posizione individuale riguardo una situazione o una circostanza.»

**Il punto che conta piu' di tutti:** l'oracolo «non rivela magicamente il futuro, ma
permette di individuare la giusta condotta». E' la stessa premessa su cui poggia
l'attribuzione decisionale implementata in `tools/oracle_cast.py`: le linee mobili si
leggono come vettori di cambiamento, non come previsione.

- Sessantaquattro esagrammi, linee spezzate o chiuse che esprimono **yin** e **yang**.
- Riferimento storico: Re Wu, dinastia Zhou (~1046 a.C.).
- **Carl Gustav Jung** vi trovo' elementi chiave per la teoria della **sincronicita'**.
- Due metodi di consultazione: **tre monete** (moderno) e **steli di millefoglie**
  (tradizionale).
- L'esagramma si costruisce **dal basso verso l'alto**, sei linee.
- **Linee mobili (6 e 9)**: producono due esagrammi, uno iniziale e uno derivato.
- Metodo delle tre monete: yang = 3, yin = 2, sei lanci.
- Esempi portati: esagramma 14 «Il grande raccolto» e 47 «L'esaurimento».

**Chiude** su un dettaglio combinatorio che vale la pena tenere: 6 e 9 nascono da
**una sola** combinazione degli addendi, mentre 7 e 8 (linee fisse) da tre. Le linee
mobili sono percio' strutturalmente piu' rare — il che spiega perche' un responso con
molte linee mobili sia un evento raro e non un caso qualsiasi.

Collegati:
- [[aion-oracle]] — la fonte eseguibile dello stesso sistema, da cui e' generato
  `engine/iching.db.json`
- [[universalis-i-ching-trigrammi]] — la seconda puntata
- [[aion-framework]]
