---
date: 2026-08-11
area: data-science
source: https://www.universalis.it/informatica/a-dijkstra
tags: [algoritmi, pathfinding, euristiche, grafi, javascript]
reviewed: 2026-08-11
---
# A* | Dijkstra

Articolo proprio, pubblicato il **20 novembre 2020** su universalis.it (~2.800 parole,
registro tecnico-didattico, con codice JavaScript).

**Perche' sta in data-science e non in informatica generica:** e' ricerca su grafo, la
stessa famiglia di algoritmi che il brain usa per navigare se stesso (`graphify` fa
BFS sul grafo della conoscenza). Il vocabolario di questa nota — nodo, costo,
euristica, lista aperta — e' quello con cui si ragiona sul grafo del brain.

**Tesi/scopo.** «L'algoritmo di ricerca A* é stato sviluppato dallo "Stanford Research
institute" ed ampiamente utilizzato nel pathfinding. Esso rappresenta un'estensione
dell'algoritmo di "Edsger Dijkstra".»

**La frase che chiarisce tutto in una riga:** Dijkstra e' lo stesso algoritmo di A*
**sprovvisto di euristica**. Detto cosi', la differenza tra i due smette di essere una
nozione da memorizzare.

- **Fase 1**: la griglia come array bidimensionale.
- **Fase 2**: `startPos` e `endPos`; gestione di **lista aperta** e **lista chiusa**;
  scansione dei nodi adiacenti.
- **Fase 3**: `F_Score = G_Score + H_Score`, dove G e' il costo gia' pagato dal punto
  di partenza e H la **stima euristica** verso la destinazione. E' la sola formula che
  serve capire.
- **Euristiche** implementate: Manhattan (spostamenti orizzontali e verticali),
  euclidea (movimento diagonale), octile, Chebyshev.
- Costi di movimento usati: 1 in rettilineo, 1,414 in diagonale (oppure 10 e 14 in
  forma intera, per evitare i decimali).
- Esempio portato fino in fondo: `startPos = (0,0)`, `endPos = (10,1)`,
  G_Score = √101 ≈ 10,4.
- Formula euclidea scritta per esteso: d(p,q) = √Σ(qᵢ − pᵢ)².

**Codice**: JavaScript, con le quattro euristiche come funzioni brevi — Manhattan,
euclidea, octile, Chebyshev.

**Licenza:** il sito pubblica sotto Creative Commons Attribuzione – Non commerciale
4.0 Internazionale.
