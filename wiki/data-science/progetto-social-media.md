# Progetto: Analisi dati social media

Analisi dell'impatto dei social (uso quotidiano, sonno) in [[excel]], report su Looker Studio.

**Metodologia**:
- *Import*: da Testo/CSV in tabella.
- *Cleaning* ([[controlli-qualita-dati]]): filtro condizionale su Student_ID (duplicati), celle vuote, CONTA.VALORI vs CONTA.VALORI.UNICI, CONTA.VUOTE, coerenza MIN/MAX; corretta un'incoerenza dividendo per 10 le ore di uso/sonno; checkbox di validazione finale.
- *Feature* ([[feature-engineering]]): Livello_Utilizzo (fasce), Tempo_Libero = 24 - sonno - social, Rapp_Social_Sonno (rapporto).
- *EDA* ([[analisi-esplorativa]]): foglio analisi_exp con Pivot e grafici per correlazioni.
- *Report*: Looker Studio ([[struttura-report-analisi]]).

Dati su disco (fuori dal repo): vedi [[dataset]].

Collegati:
- [[progetti]]
- [[workflow-analisi-dati]]
- [[controlli-qualita-dati]]
- [[feature-engineering]]
- [[analisi-esplorativa]]
- [[struttura-report-analisi]]
- [[excel]]
- [[dataset]]
