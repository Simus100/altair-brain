# Controlli di qualita dei dati (data quality)

Batteria di controlli applicata PRIMA di ogni analisi (da Insurance, Social Media, Hotel). Si documenta in fogli dedicati (data_cleaning, data_logic) e si chiude con una validazione.

- **Duplicati**: CONTA.VALORI vs CONTA.VALORI.UNICI; righe intere con CONTA.PIU.SE multi-colonna, poi CONTA.SE(check>1).
- **Valori mancanti**: CONTA.VUOTE; numerici RIGHE - CONTA.NUMERI; categorici/spazi con MATR.SOMMA.PRODOTTO((ANNULLA.SPAZI(col&"")="")*1).
- **Outlier**: metodo IQR ([[quartili-outlier]]); decidere se rimuoverli o TENERLI come segmento significativo (es. assicurati ad alto costo).
- **Coerenza**: MIN/MAX plausibili, controllo interi (RESTO(col;1)<>0), frequenza dei categorici (UNICI + CONTA.SE + percentuale).
- **Correzioni**: valori importati male (es. da dividere per 10), decimali testo ([[normalizzazione-decimali]]).

Collegati:
- [[metodi]]
- [[data-cleaning]]
- [[quartili-outlier]]
- [[normalizzazione-decimali]]
- [[excel]]
