---
name: triage
description: Smista le note dell'inbox del second brain nelle macroaree giuste e rigenera il grafo. Usa quando l'utente dice "smista l'inbox", "triage", "processa le note catturate", o quando ci sono note in raw/_inbox da archiviare nelle aree.
---

# Skill: triage dell'inbox

Smista le note grezze catturate (dal telefono via API o a mano in `raw/_inbox/`) nelle
macroaree del brain, poi rigenera e pubblica.

## Procedura

1. **Raccogli le note pendenti:**
   - Locali: `raw/_inbox/*.md` (escludi README.md e la cartella archive/).
   - Remote (VPS): se l'utente ha configurato URL e token, `GET <url>/v1/inbox` con
     header `Authorization: Bearer <token>`, poi `GET /v1/inbox/{id}` per il contenuto.
     Se l'API non e raggiungibile, procedi solo con le locali e dillo.
2. **Per ogni nota:** leggi contenuto e frontmatter (`area_hint` se presente). Decidi la
   macroarea consultando `areas.json`. Se ambigua, chiedi all'utente. Normalizza il nome
   file in kebab-case descrittivo e scrivi in `raw/<area>/<nome>.md` (mantieni il
   frontmatter, e la convenzione: stesso concetto = stesso nome esatto tra aree per i
   ponti intercampo).
3. **Rigenera e verifica:** `python tools/rebuild_all.py` (fa tutto: wiki, validazioni,
   grafo, sottografi, viste, salute). Deve uscire senza errori.
4. **Pubblica:** commit con messaggio descrittivo + push.
5. **Archivia le note processate:** locali → spostale in `raw/_inbox/archive/`
   (creala se manca); remote → `POST /v1/inbox/{id}/done`.

## Vincoli
- Non inventare contenuti: smisti, non riscrivi (piccole correzioni di battitura ok).
- Se una nota non appartiene a nessuna area, chiedi se creare una nuova area
  (voce in areas.json + engine/router.json + cartelle) o lasciarla in inbox.
