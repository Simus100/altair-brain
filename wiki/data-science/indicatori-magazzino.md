---
date: 2026-08-11
area: data-science
source: raw/data-science/PROJECT WORK/Analisi dati magazzino finale/
tags: [magazzino, inventory, kpi, feature-engineering]
reviewed: 2026-08-11
---
# Indicatori di magazzino (colonne derivate)

Un gestionale espone quantita, soglie e prezzi. Nessuna di queste colonne risponde da
sola a «cosa devo ordinare oggi». Le domande operative vivono nelle **combinazioni**:
sono le colonne che non esistono nel dato e vanno costruite.

Sistema completo estratto da [[progetto-magazzino]]. Ogni indicatore nasce da una
domanda, non dalla disponibilita di una colonna — la regola di [[feature-engineering]].

## Stato delle scorte

| Indicatore | Come si costruisce | A cosa risponde |
|---|---|---|
| `Supply_Status` | confronto quantita ↔ soglia, tre esiti: sotto, sulla soglia, sopra | quali prodotti richiedono attenzione |
| `Stock_Gap` | quantita − soglia | **quanto** sono sotto: ordina per urgenza |
| `Units_To_Reorder_Level` | (soglia − quantita) portato a zero se negativo | quante unita servono per rientrare |
| `Stock_Reorder_Ratio` | quantita ÷ soglia | urgenza **relativa**: confronta prodotti con soglie diverse |

I quattro non sono ridondanti, e vale la pena capire perche. `Stock_Gap` risponde in
unita, `Stock_Reorder_Ratio` in proporzione: un prodotto a −20 su soglia 100 e messo
molto meglio di uno a −20 su soglia 25, e solo il rapporto lo dice. Un cruscotto usa
il primo per la lista della spesa, il secondo per decidere a chi pensare per primo.

## Valore economico

| Indicatore | Come si costruisce | A cosa risponde |
|---|---|---|
| `Inventory_Value` | quantita × prezzo unitario | quanto capitale c'e fermo, per prodotto |
| `Estimated_Reorder_Cost` | quantita di riordino × prezzo unitario | quanto costerebbe l'ordine |
| `Reorder_Needed_Flag` | 1 se sotto o sulla soglia, altrimenti 0 | maschera per i totali |
| `Reorder_Cost_Required` | costo stimato × flag | **il costo dei soli riordini che servono davvero** |

L'ultimo e il piu importante e il meno ovvio. Sommare `Estimated_Reorder_Cost` su tutto
il catalogo dà il costo di riordinare *ogni cosa*, che nessuno vuole sapere.
Moltiplicare per un flag 0/1 prima di sommare e il modo piu corto per far rispondere
un totale alla domanda giusta.

**Attenzione dichiarata**: se il prezzo unitario e il prezzo di *vendita* e non il
costo d'acquisto, questi quattro indicatori sono stime, non importi. Va scritto accanto
al numero, non pensato e basta ([[limiti-dichiarati]]).

## Classificazioni per quantile

| Indicatore | Come si costruisce | A cosa risponde |
|---|---|---|
| `Demand_Class` | volume di vendita in tre fasce sui percentili 33 e 67 | quanto tira un prodotto |
| `Turnover_Class` | indice di rotazione in tre fasce su Q1 e Q3 | quanto e fermo a scaffale |

Le soglie **si leggono dai dati** ([[quartili-outlier]]), non si scelgono a mano. Il
vantaggio e che l'indicatore resta valido quando il catalogo cambia; il costo e che le
classi sono *relative*: «rotazione bassa» significa bassa rispetto a questo magazzino,
non in assoluto. Con Q1/Q3 la classe centrale raccoglie per costruzione circa meta dei
prodotti — e una proprieta della regola, non una scoperta sul magazzino, e chi legge
il grafico a torta va avvisato.

## Rischio, cioe due indicatori che si parlano

| Indicatore | Come si costruisce | A cosa risponde |
|---|---|---|
| `Obsolescence_Risk` | alto se domanda bassa **e** rotazione bassa; medio se una sola; basso altrimenti | cosa rischia di restare invenduto |

E la sola colonna costruita da altre due colonne derivate, ed e li che l'analisi smette
di descrivere e comincia a suggerire. Un prodotto che vende poco puo essere normale;
uno che vende poco *ed* e fermo a scaffale e un problema di capitale.

Scelta di metodo che vale la pena copiare: **il valore economico resta fuori dalla
formula del rischio**. Serve dopo, per quantificare quanto capitale sta in ciascuna
classe. Mescolarlo dentro avrebbe prodotto un punteggio che non si sa piu cosa misura —
se il rischio o l'importo.

## La regola generale

Un indicatore derivato va accompagnato da tre cose, sempre: **la formula**, **la
domanda a cui risponde** e **cosa lo invaliderebbe**. Le prime due lo rendono usabile,
la terza lo rende onesto.

Collegati:
- [[progetto-magazzino]]
- [[feature-engineering]]
- [[quartili-outlier]]
- [[limiti-dichiarati]]
- [[python-pandas]]
- [[framework-domande-analitiche]]
- [[struttura-report-analisi]]
- [[metodi]]
