---
date: 2026-08-11
area: data-science
source: raw/data-science/PROJECT WORK/Analisi dati magazzino finale/
tags: [metodo, qualita-dato, provenienza]
reviewed: 2026-08-11
---
# Limiti dichiarati (cosa il dato non puo dire)

I [[controlli-qualita-dati]] chiedono: *questo dato e pulito?* Questa pagina chiede
un'altra cosa: **fin dove arriva una conclusione che ci posso costruire sopra?**

Sono due domande diverse. Un dataset puo essere perfettamente pulito — zero nulli, zero
duplicati, tipi corretti — e comunque non poter rispondere alla domanda che gli si sta
facendo. La pulizia non e una licenza a concludere.

## Perche e un pezzo di metodo, non una premessa di cortesia

Un'analisi che non dichiara i propri limiti resta plausibile. Diventa consultabile,
viene citata, entra in una decisione — e nessuno sa piu quale parte reggeva davvero.
Il limite scritto accanto al numero e l'unica cosa che sopravvive al passaggio di mano.
E la stessa ragione per cui in questo brain ogni cifra porta la sua fonte: vedi
[[struttura-report-analisi]].

## I tre modi in cui un dato smette di poter rispondere

**1. Manca la chiave giusta.** Il dato c'e, ma non alla granularita della domanda.
In [[progetto-magazzino]] esistono data di ricezione e data di scadenza, ma manca
l'identificativo di lotto: l'ID identifica il prodotto, non la fornitura. Le due date
possono appartenere a consegne diverse — e infatti in meta delle righe la scadenza
precede la ricezione. Ogni calcolo di durata sarebbe stato aritmeticamente corretto e
privo di senso.
*Cosa si fa*: non si calcola. Le date restano un **indicatore di qualita**, e il
conteggio delle incoerenze si pubblica come risultato a se.

**2. Il campo e ambiguo.** La colonna esiste, il nome non basta a dire cosa contiene.
`Unit_Price` puo essere costo d'acquisto o prezzo di vendita: da questa scelta dipende
se «valore di magazzino» sia un costo o un ricavo potenziale.
*Cosa si fa*: si calcola comunque, e si scrive **stima** accanto al numero, dicendo da
cosa dipende. Un numero con la sua condizione vale piu di un numero omesso.

**3. Il dato non e plausibile.** Nessuna regola formale e violata, ma la realta non si
comporta cosi. Novecentonovanta posizioni di magazzino diverse per novecentonovanta
prodotti descrivono un magazzino dove niente sta accanto a niente.
*Cosa si fa*: si segnala e si rinuncia a quel filone. Costruire un'analisi spaziale su
posizioni inventate avrebbe prodotto grafici perfetti su un magazzino inesistente.

## Il caso a parte: il dato che manca per attribuire una causa

Diverso dai tre precedenti, e il piu facile da sbagliare. Sapere che il 32,8% dei
prodotti e in arretrato non dice **di chi** sia la responsabilita: servirebbero tempi
di consegna, date d'ordine, cause del ritardo. Il salto dal *cosa* al *perche* e il
punto in cui un'analisi corretta diventa un'accusa infondata.

*Cosa si fa*: si riporta il fenomeno, si nomina il dato mancante che impedisce
l'attribuzione. Chi legge sa cosa chiedere per andare avanti.

## Dove va scritto

Non in fondo, in una sezione «limitazioni» che nessuno apre. **Accanto al numero**, nel
punto in cui qualcuno potrebbe usarlo: la frase «questa e una stima perche il prezzo
potrebbe essere di vendita» deve stare sotto il grafico dei costi, non a pagina dodici.

Collegati:
- [[controlli-qualita-dati]]
- [[progetto-magazzino]]
- [[indicatori-magazzino]]
- [[struttura-report-analisi]]
- [[framework-domande-analitiche]]
- [[workflow-analisi-dati]]
- [[metodi]]
