# plugin: scrittura

Verifica stilometrica della prosa che il brain produce: anglicismi e calchi
(si correggono sempre), ripetizioni verbatim, lunghezza media, tic da modello.

**Serve un engine.** `style_check.py` non implementa l'analisi: la IMPORTA da uno
script di stilometria che deve stare nel materiale grezzo, in
`raw/<tua-area>/bookforge/stylometry.py`. Senza quel file il tool e inerte e lo
dichiara, invece di fingere un verdetto.

E un plugin e non motore proprio per questo: un componente che dipende da contenuto
non e infrastruttura, e chiamarlo tale sarebbe una promessa che non puo mantenere.

Per attivarlo: copia `tools/` e `skills/` nelle cartelle corrispondenti, e metti il
tuo engine di stilometria al percorso atteso.
