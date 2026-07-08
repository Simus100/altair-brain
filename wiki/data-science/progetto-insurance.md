# Progetto: Insurance Analysis

Analisi di dati assicurativi (charges) in [[excel]]/[[python-pandas]].

**Metodologia**:
- *Statistiche di base*: MIN/MAX/MEDIA/MEDIANA/DEV.ST.C -> media (13.270$) > mediana (9.382$) segnala distribuzione asimmetrica con code ad alto costo.
- *Qualita* ([[controlli-qualita-dati]]): outlier IQR = 139 valori TENUTI come segmento ad alto rischio; nessun mancante (1.338 record); controllo interi; 1 sola riga duplicata; frequenze categoriche (sesso ~50/50, fumatori 20,48%, regioni ~uniformi).
- *Feature* ([[feature-engineering]]): bmi_category, fascia_eta, charges_level (percentili 1/3 e 2/3), risk_score 0-3 (fumatore+obeso+eta>=50), high_cost_outlier.
- *Analisi* ([[analisi-relazionale]] via Pivot): outlier per fumatore (quasi meta dei fumatori ad alto costo vs <1% non fumatori), charges per age_group (cresce con l'eta), per region (southeast piu caro), per bmi_category.

Dati su disco (fuori dal repo): vedi [[dataset]].

Collegati:
- [[progetti]]
- [[workflow-analisi-dati]]
- [[controlli-qualita-dati]]
- [[feature-engineering]]
- [[quartili-outlier]]
- [[analisi-relazionale]]
- [[framework-domande-analitiche]]
- [[excel]]
- [[python-pandas]]
- [[dataset]]
