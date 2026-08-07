--- FUNZIONI DI DATA_PROCESISNG EXCEL ---


1. STATISTICHE DI BASE

=MIN(tabella[colonna])

=MAX(tabella[colonna])

=MEDIA(tabella[colonna])

=MEDIANA(tabella[colonna])

=DEV.ST.C(tabella[colonna])




RISULTATO: l dataset presenta assicurati con età compresa tra 18 e 64 anni. Il costo medio annuo della polizza è pari a circa 13.270 dollari, ma la mediana è più bassa, circa 9.382 dollari. Questa differenza suggerisce la presenza di alcuni assicurati con costi molto elevati che alzano la media complessiva. Anche la deviazione standard dei costi, superiore a 12.000 dollari, conferma una forte variabilità nei valori di charges.




2. CALCOLO OUTLIER



PRIMO QUARTILE:

=QUARTILE.INC(tabella[colonna];1)


SECONDO QUARTILE:

=QUARTILE.INC(tabella[colonna];3)


IQR:

Q1-Q3


LIM.INF: 

Q1 − 1,5 × IQR


LIM.SUP:

Q3 + 1,5 × IQR


N.OUTLIER:

=CONTA.PIÙ.SE(tabella[colonna];"<"&<LIM.INF>)+CONTA.PIÙ.SE(tabella[colonna];">"&<LIM.SUP>)


RISULTATO: L’analisi tramite intervallo interquartile ha individuato 139 valori anomali nella variabile charges, corrispondenti a costi superiori a circa 34.489 dollari annui. Questi valori non sono stati eliminati, poiché rappresentano assicurati ad alto impatto economico e costituiscono un segmento rilevante per l’analisi del rischio.


3. CELLE VUOTE


CONTEGGIO RIGHE:

=RIGHE(tabella[colonna])


CONTEGGIO VALORI MANCANTI:

=RIGHE(tabella[colonna])-CONTA.NUMERI(tabella[colonna])   ---> Valori numerici

=MATR.SOMMA.PRODOTTO((ANNULLA.SPAZI(tabella[colonna]&"")="")*1) ---> Valori categorici


RISULTATO: Il dataset non presenta valori mancanti. Tutti i 1.338 record risultano compilati per ciascuno dei sette attributi. Non sono state rilevate nemmeno celle contenenti esclusivamente spazi.


4. FREQUENZA VALORI CATEGORICI:

=DATI.ORDINA(UNICI(tabella[colonna]))  ---> individuazione elementi degli attributi ed elenco

=CONTA.SE(tabella[colonna];"attributo") ---> Conteggio occorrenze 

(NUMERO OCCORRENZE/RIGHE TOTALI)*100 ---> Calcolo percentuale


RISULTATO: La distribuzione per sesso è sostanzialmente equilibrata. Gli uomini rappresentano il 50,52% del campione e le donne il 49,48%. Non emerge quindi uno sbilanciamento significativo nella composizione del dataset.

I non fumatori costituiscono la maggioranza del campione, con il 79,52% degli assicurati. I fumatori rappresentano invece il 20,48%. La diversa numerosità dei due gruppi dovrà essere considerata nelle successive analisi dei costi medi.

Le quattro regioni sono rappresentate in maniera abbastanza uniforme. La regione southeast presenta una presenza leggermente maggiore, pari al 27,20%, mentre le altre regioni si collocano intorno al 24%.


5. CONTROLLO DEGLI INTERI:

=MATR.SOMMA.PRODOTTO((RESTO(insurance[age];1)<>0)*1)

=MATR.SOMMA.PRODOTTO((RESTO(insurance[children];1)<>0)*1)

RISULTATO: Le variabili age e children risultano coerenti con il tipo di dato previsto: tutti i valori sono numeri interi e non sono stati rilevati valori decimali o testuali.


6. RIGHE DUPLICATE:

Nuova colonna dle dataset:

=CONTA.PIÙ.SE(
insurance[age];[@age];
insurance[sex];[@sex];
insurance[bmi];[@bmi];
insurance[children];[@children];
insurance[smoker];[@smoker];
insurance[region];[@region];
insurance[charges];[@charges]
)

Individuazione delle righe duplicate:

=CONTA.SE(insurance[duplicate_check];">1")

RISULTATO: È stata individuata una sola osservazione duplicata. Eliminando esclusivamente la copia eccedente, il dataset pulito sarà composto da 1.337 record unici.


--- CREAZIONE DI VARIABILI DERIVATE UTILI ---


1. INDICE DI PESO:


se il BMI è inferiore a 18,5 → Sottopeso;

altrimenti, se è inferiore a 25 → Normopeso;

altrimenti, se è inferiore a 30 → Sovrappeso;

in tutti gli altri casi → Obeso.

Nuova colonna:

=SE([@bmi]<18,5;"Sottopeso";SE([@bmi]<25;"Normopeso";SE([@bmi]<30;"Sovrappeso";"Obeso")))




2. FASCIA DI ETA':

18–29 → Giovane
30–49 →	Adulto
50–64 →	Senior

Nuova colonna:

=SE([@age]<=29;"Giovane";SE([@age]<=49;"Adulto";"Senior"))



3. CHARGES LEVEL:


=INC.PERCENTILE(insurance[charges];1/3)

=INC.PERCENTILE(insurance[charges];2/3)



Basso	charges ≤ 6.265,1298
Medio	charges > 6.265,1298 e ≤ 12.820,11503
Alto	charges > 12.820,11503



RISULTATO: La variabile charges_level è stata costruita utilizzando il primo e il terzo quartile della distribuzione dei costi. I valori fino al primo quartile sono stati classificati come Bassi, quelli compresi tra il primo e il terzo quartile come Medi e quelli superiori al terzo quartile come Alti.




Nuova colonna:

=SE([@charges]*1<='data processing'!$E$78*1;"Basso";SE([@charges]*1<='data processing'!$E$80*1;"Medio";"Alto"))


*E78, E80 sono rispettivamente il terzo più basso e quello più alto nel foglio "data processing" di Excel



4. RISK SCORE:

indice semplice da 0 a 3:

+1 se fumatore;
+1 se obeso;
+1 se ha almeno 50 anni.

Nuova colonna:

=SE([@smoker]="yes";1;0)+SE([@bmi]>=30;1;0)+SE([@age]>=50;1;0)


5. HIGH COST OUTLIER

Nuova colonna:

=SE([@charges]>'data processing'!$I$31;"Sì";"No")


* I31 è il limite superiore calcolato sui charges