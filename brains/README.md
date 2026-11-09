# Brain locali, prodotto pubblico

`starter/` è il modello vergine pubblicato: nessuna nota acquisita, nessuna lezione,
nessun training adottato. `brains.default.json` lo seleziona su un clone nuovo.

Il registro `brains.json` e tutti gli altri brain sono **locali e ignorati da Git**.
Se presente, il registro locale prevale sul default pubblico. I brain già esistenti
restano nelle loro cartelle e continuano a essere utilizzabili.

```powershell
python tools/brain_new.py --nome ricerca --aree fonti,metodi
$env:ALTAIR_BRAIN = 'brains/ricerca'
python tools/rebuild_all.py
```

La creazione del primo brain imposta il registro locale. In un'installazione con
più brain, modificare `attivo` in `brains.json` oppure usare `ALTAIR_BRAIN`.
Per adottare il modulo opzionale AION aggiungere `--training aion` alla creazione.

La rimozione dei brain dalla distribuzione corrente non cancella i vecchi commit,
i branch precedenti, i fork o le copie già scaricate. Non usare il repository
pubblico come deposito di informazioni riservate.
