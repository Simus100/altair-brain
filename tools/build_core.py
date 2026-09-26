# -*- coding: utf-8 -*-
"""
altair-brain — genera core/: lo SCHELETRO cedibile, senza l'esperienza acquisita.

COSA SEPARA. Questo repo contiene due cose che finora vivevano mescolate:
  - il MOTORE   — grafo, provenienza, freschezza, ricerca, tre viste, anello di
                  apprendimento, API, guardie. Vale per qualsiasi conoscenza.
  - l'ACQUISITO — le note, le pagine curate, le lezioni, i report. Vale solo per
                  chi le ha scritte, ed e' il brain di una persona.
core/ e' il primo senza il secondo: si puo' consegnare a qualcun altro, che ci
mettera' la propria conoscenza.

PERCHE' GENERATO E NON COPIATO. Una copia dentro lo stesso repo diverge entro poche
settimane, e nessuno se ne accorge finche' non serve davvero. E' la stessa ragione per
cui wiki/aion e le tre viste sono generate: fonte unica, artefatto derivato, guardia
in CI che li confronta. Modificare core/ a mano fa fallire il test — si modifica la
sorgente, e core/ segue.

REGOLA DI COSTRUZIONE: qui si SELEZIONA e si SANIFICA, non si riscrive la logica.
Se un tool ha bisogno di essere reso generico, si cambia il tool nel repo vivo (dove
i test lo coprono) e core/ eredita. Una logica che esiste solo nell'export sarebbe
codice senza guardie.

DUE COSE DIVERSE, E VANNO TENUTE DISTINTE.
  - un TRAINING (core/training/) e' un imprinting iniziale: un modello di pensiero
    completo — fonti grezze, modello tipizzato, protocollo di ragionamento — che il
    brain ADOTTA COME PROPRIO MODO DI RAGIONARE. Se ne sceglie al massimo uno, in
    fase di onboarding, e si puo' anche non sceglierne nessuno.
  - un PLUGIN (core/plugins/) aggiunge una CAPACITA' senza toccare il pensiero: uno
    strumento in piu'. Se ne possono attivare quanti se ne vuole.
AION e' un training, non un plugin: non aggiunge un tool, decide come si ragiona.

Uso:  python tools/build_core.py        -> core/
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN, manifesto, versione_motore   # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente

    def versione_motore():
        with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as f:
            return f.read().strip()


# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

CORE = os.path.join(ROOT, "core")

# --- Cosa e' PLUGIN e cosa e' MOTORE ---------------------------------------
# I tool del plugin AION implementano UN modello di pensiero: l'oracolo I Ching, la
# generazione della wiki dal modello tipizzato, la validazione di quel modello.
# Senza il plugin il motore funziona lo stesso — semplicemente non ragiona con AION.
TOOL_TRAINING_AION = {
    "oracle_cast.py", "build_iching_db.py", "apply_iching_relations.py",
    "gen_wiki_from_model.py", "validate_model.py",
}
# Legati a contenuto di questo brain, non generalizzabili come sono.
TOOL_ESCLUSI = {
    "apply_procedural_iran.py",   # un singolo report, non un metodo
    "build_dense_index.py",       # livello semantico opzionale, ~2GB di dipendenze
    "build_core.py",              # genera lo scheletro: appartiene alla sorgente, non al prodotto
    # Strumenti dell'OFFICINA: servono a chi gestisce piu' brain accanto al motore.
    # Nello scheletro, che e' un brain solo, non avrebbero nulla su cui lavorare.
    "brain_new.py", "brain_export.py", "build_code_graph.py",
}
# SECONDO PLUGIN: la verifica stilometrica. Non e' motore perche' importa un engine
# di analisi che vive nel materiale grezzo (raw/<area>/bookforge/stylometry.py): senza
# quello il tool e' inerte. Meglio dichiararlo plugin che spacciarlo per infrastruttura.
TOOL_PLUGIN_SCRITTURA = {"style_check.py"}
TEST_PLUGIN_SCRITTURA = {"test_style_check.py"}
# Test che verificano l'acquisito (il corpus di una persona), non il motore.
TEST_ESCLUSI = {
    "test_corpus_divulgazione.py",   # verifica il corpus di una persona
    "test_golden.py",                # domande sul contenuto acquisito
    # Verifica che l'export sia sanificato: e' una garanzia di CHI CONSEGNA, non un
    # test del prodotto. Elencando i termini da cercare conterrebbe per forza i nomi
    # che deve tenere fuori, e si segnalerebbe da solo — la stessa autorilevazione
    # gia' vista nel checker privacy.
    "test_core.py",
}

TRAINING_AION_FILE = [
    ("engine/aion.model.json", "training/aion/engine/aion.model.json"),
    ("engine/aion-reasoner.md", "training/aion/engine/aion-reasoner.md"),
    ("engine/schema/aion.model.schema.json", "training/aion/engine/schema/aion.model.schema.json"),
    ("engine/iching.db.json", "training/aion/engine/iching.db.json"),
    ("raw/aion", "training/aion/raw/aion"),
    (".claude/skills/aion", "training/aion/skills/aion"),
    (".claude/skills/oracle", "training/aion/skills/oracle"),
]
SKILL_MOTORE = ["triage"]


def _scrivi(rel, testo):
    p = os.path.join(CORE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)


def _copia(src_rel, dst_rel, base=None, obbligatorio=False):
    src = os.path.join(base or ROOT, src_rel)
    dst = os.path.join(CORE, dst_rel)
    if not os.path.exists(src):
        # Saltare in silenzio un file mancante e' come il pacchetto AION ha perso
        # modello, reasoner, DB dell'oracolo e le 7 fonti: dalla migrazione del brain
        # in brains/aion li cercava nella radice, non li trovava, e produceva lo
        # stesso uno scheletro "valido" il cui training non installava nulla.
        if obbligatorio:
            raise SystemExit(f"build_core: manca {os.path.relpath(src, ROOT)} — lo "
                             f"scheletro sarebbe incompleto, quindi non lo genero")
        return 0
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(dst=dst, src=src)
        return sum(len(f) for _, _, f in os.walk(dst))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return 1


def brain_col_training(nome):
    """Il brain da cui si prende un training: quello che lo dichiara adottato nel
    manifesto. Non il brain attivo: se l'attivo fosse un brain senza training, il
    pacchetto uscirebbe vuoto."""
    reg = os.path.join(ROOT, "brains", "brains.json")
    if os.path.exists(reg):
        with open(reg, encoding="utf-8") as f:
            for b in json.load(f).get("brains", []):
                p = os.path.join(ROOT, b["percorso"])
                if manifesto(p).get("training") == nome:
                    return p
    return BRAIN


def aree_vuote():
    """Il registro delle aree diventa un ESEMPIO: una sola area di partenza.
    Le regole per area (SLA, coesione, strato generato) restano documentate, cosi'
    chi arriva vede subito che sono configurazione e non codice."""
    return {
        "schema_version": 1,
        "descrizione": "Registro delle macroaree: unica fonte per scaffolding, instradamento "
                       "delle domande, freschezza e coesione. Aggiungere un'area = una voce "
                       "qui + la cartella raw/<id>/. Schema: schema/areas.schema.json.",
        "convenzione": {
            "id": "kebab-case ascii, nessuno spazio; coincide con raw/<id>/",
            "status": "active | draft | archived",
            "sla_giorni": "giorni prima che una nota vada ri-verificata; null = non scade",
            "coesa": "true = l'area deve restare un solo componente connesso nel grafo",
            "generata_da": "se presente, wiki/<id>/ e GENERATA da questo file",
            "keywords": "parole che instradano una domanda a quest'area (sottostringa)",
            "colore": "colore dello spicchio nell'atlante 3D (facoltativo)",
        },
        "areas": [{
            "id": "esempio",
            "label": "Esempio",
            "description": "Sostituisci questa voce con la tua prima macroarea.",
            "status": "draft",
            "sla_giorni": 180,
            "keywords": ["esempio", "prova"],
        }],
    }


def costruisci():
    if os.path.exists(CORE):
        shutil.rmtree(CORE)
    conta = {"motore": 0, "training": 0, "plugin": 0, "guardie": 0}

    # 1. MOTORE: i tool, meno plugin ed esclusi
    for f in sorted(os.listdir(os.path.join(ROOT, "tools"))):
        if not f.endswith(".py") or f in TOOL_ESCLUSI:
            continue
        if f in TOOL_TRAINING_AION or f in TOOL_PLUGIN_SCRITTURA:
            continue
        conta["motore"] += _copia(f"tools/{f}", f"tools/{f}")
    _copia("tools/README.md", "tools/README.md")

    # 2. GUARDIE: i test del motore
    for f in sorted(os.listdir(os.path.join(ROOT, "tests"))):
        if f.endswith(".py") and f not in TEST_ESCLUSI and f not in TEST_PLUGIN_SCRITTURA:
            conta["guardie"] += _copia(f"tests/{f}", f"tests/{f}")

    # 3. API e CI
    for f in ("app.py", "brain_core.py", "mcp_server.py", "README.md"):
        _copia(f"server/{f}", f"server/{f}")
    _copia(".github/workflows/validate.yml", ".github/workflows/validate.yml")

    # 4. TRAINING AION: un imprinting, non uno strumento. Il contenuto (modello,
    # reasoner, fonti) si prende dal brain che l'ha ADOTTATO; skill e strumenti dal
    # motore. Ogni file e' obbligatorio: un training a meta' non e' un training.
    fonte = brain_col_training("aion")
    for src, dst in TRAINING_AION_FILE:
        base = ROOT if src.startswith(".claude/") else fonte
        conta["training"] += _copia(src, dst, base=base, obbligatorio=True)
    for f in sorted(TOOL_TRAINING_AION):
        conta["training"] += _copia(f"tools/{f}", f"training/aion/tools/{f}",
                                    obbligatorio=True)
    # La catena di provenienza del training: da quali fonti deriva la sua wiki. Senza,
    # un brain che adottava AION riceveva la wiki ma nessuno dichiarava da dove venisse
    # (l'atlante non aveva archi di provenienza: lo ha mostrato un'installazione vergine).
    with open(os.path.join(fonte, "engine", "provenance.json"), encoding="utf-8") as fh:
        prov = json.load(fh)
    parte = {"ancoraggi_area": [x for x in prov.get("ancoraggi_area", [])
                                if x.get("indice", "").startswith("wiki/aion/")],
             "mappe_dirette": [x for x in prov.get("mappe_dirette", [])
                               if x.get("wiki", "").startswith("wiki/aion/")]}
    if not parte["ancoraggi_area"]:
        raise SystemExit("build_core: il training aion non ha una catena di provenienza")
    _scrivi("training/aion/provenance.json",
            json.dumps(parte, ensure_ascii=False, indent=2) + "\n")
    _scrivi("training/README.md", TRAINING_README)

    # 5a. PLUGIN SCRITTURA: verifica stilometrica, inerte senza il suo engine
    for f in sorted(TOOL_PLUGIN_SCRITTURA):
        conta["plugin"] += _copia(f"tools/{f}", f"plugins/scrittura/tools/{f}")
    for f in sorted(TEST_PLUGIN_SCRITTURA):
        conta["plugin"] += _copia(f"tests/{f}", f"plugins/scrittura/tests/{f}")
    conta["plugin"] += _copia(".claude/skills/scrivi", "plugins/scrittura/skills/scrivi")
    _scrivi("plugins/scrittura/README.md", PLUGIN_SCRITTURA)

    # 5b. SKILL del motore
    for s in SKILL_MOTORE:
        _copia(f".claude/skills/{s}", f".claude/skills/{s}")

    # 6. CONFIGURAZIONE VUOTA — nessuna area di nessuno
    _scrivi("areas.json", json.dumps(aree_vuote(), ensure_ascii=False, indent=2) + "\n")
    _scrivi("engine/bridges.json", json.dumps(
        {"schema_version": 1,
         "descrizione": "Ponti intercampo CURATI tra macroaree. I wikilink non "
                        "attraversano le cartelle: i ponti si dichiarano qui.",
         "bridges": []}, ensure_ascii=False, indent=2) + "\n")
    _scrivi("engine/provenance.json", json.dumps(
        {"schema_version": 1,
         "descrizione": "Cuce la catena FONTE -> CONOSCENZA nel grafo.",
         "convenzione": {"ancoraggi_area": "indice di area <- note grezze che lo fondano",
                         "mappe_dirette": "pagina curata <- fonti da cui distilla"},
         "ancoraggi_area": [], "mappe_dirette": []}, ensure_ascii=False, indent=2) + "\n")
    _scrivi("engine/lessons.jsonl", "")
    _scrivi("engine/LESSONS.md",
            "# Lezioni apprese\n\nNessuna ancora. Il primo `python tools/lesson_log.py` "
            "la scrive.\n")

    # 7. CARTELLE VUOTE con le loro regole
    _scrivi("raw/README.md", RAW_README)
    _scrivi("raw/_inbox/README.md", INBOX_README)
    _scrivi("raw/_inbox/archive/.gitkeep", "")
    _scrivi("wiki/.gitkeep", "")
    _scrivi("reports/.gitkeep", "")
    _scrivi("metrics/.gitkeep", "")

    # 7b. VERSIONE DEL MOTORE, SCHEMI DEI CONTRATTI e MANIFESTO
    _copia("VERSION", "VERSION", obbligatorio=True)
    _copia("schema", "schema", obbligatorio=True)
    _scrivi("brain.json", json.dumps(
        {"schema_version": 1, "nome": "brain", "motore": versione_motore(),
         "training": None, "creato": None}, ensure_ascii=False, indent=2) + "\n")
    _scrivi(".gitignore", GITIGNORE)

    # 8. DOTTRINA e ONBOARDING
    _scrivi("README.md", README)
    _scrivi("CLAUDE.md", CLAUDE)
    _scrivi("onboarding.py", ONBOARDING)
    return conta


PLUGIN_SCRITTURA = """# plugin: scrittura

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
"""

TRAINING_README = """# training — imprinting iniziale del brain

Un **training** e un modo di ragionare gia formato che il brain puo adottare in fase
di onboarding: fonti grezze, modello tipizzato, protocollo di ragionamento. Non e uno
strumento in piu — decide *come* si pensa, non *cosa* si puo fare.

Regole:

- se ne adotta **al massimo uno**, e si puo non adottarne nessuno;
- si sceglie all'onboarding, ma si puo adottare anche dopo;
- una volta adottato diventa parte del brain: le sue fonti finiscono in `raw/`, il
  suo protocollo in `engine/`, le sue skill fra le altre.

## Disponibile

**aion** — modello di pensiero a livelli con quattro modalita di ragionamento, un
gate etico sempre attivo e un oracolo I Ching eseguibile usato per le decisioni.
Aggiunge la macroarea `aion`.

## Farne uno tuo

Serve una cartella con la stessa forma: `raw/<id>/` con le fonti, `engine/` con il
modello e il protocollo, `skills/` con le skill che lo invocano. L'onboarding lo
propone se lo trova qui.

## Senza training

Il motore funziona lo stesso. Il modo di ragionare lo costruisci strada facendo, e
l'anello delle lezioni lo registra man mano — con la differenza che parte da zero
invece che da un imprinting.
"""

GITIGNORE = """# Dati pesanti delle aree: restano sul disco, NON in git (limiti di dimensione,
# e un repo pubblicato e' permanente). I pattern iniziano con **/ perche' un pattern
# con una barra nel mezzo e' ancorato alla radice e smette di valere se il brain
# viene spostato: e' esattamente cosi' che dei dataset sono finiti in un repo pubblico.
**/raw/**/*.xlsx
**/raw/**/*.pbix
**/raw/**/*.csv
**/raw/**/*.zip
**/raw/**/*.png
**/raw/**/*.pdf
**/raw/**/*.bkp
**/raw/**/backup/
**/graphify-out/cache/
**/graphify-out/search/
.env
*.key
**/secrets.*
# Hook eseguibili degli agenti: attivi in locale, mai versionati. In un repo
# pubblicato sarebbero codice shell eseguito sulla macchina di chi lo clona.
.claude/settings.local.json
.claude/settings.json
__pycache__/
*.pyc
.pytest_cache/
"""

INBOX_README = """---
area: _inbox
source: documentazione della cartella
tags: []
---
# _inbox — cassetta di cattura

Cartella tecnica, non una macroarea: qui finiscono le note grezze in attesa di
smistamento. Butta qui un file `.md` qualsiasi, oppure usa `POST /v1/capture`
sull'API del brain. La skill `/triage` classifica ogni nota nella macroarea giusta,
rigenera il grafo e sposta la nota in `archive/`: non si cancella mai nulla.
"""

RAW_README = """---
area: generale
source: documentazione della cartella
tags: []
---
<!-- Niente 'date'/'reviewed' di proposito: questo file e documentazione della
     cartella, non conoscenza che invecchia. Con una data fissa, un brain appena
     creato segnalerebbe subito contenuto scaduto — un prodotto che si lamenta
     di se stesso al primo avvio. -->
# raw/ — materiale grezzo per macroarea

Ogni sottocartella e una macroarea dichiarata in `../areas.json`. Il grafo estrae
nodi e relazioni da questi file.

## Front-matter standard

```yaml
---
date: 2026-01-01           # quando la nota entra nel brain
area: <id-area>            # coincide con la cartella
source: libro/url/riflessione propria
tags: [parola-chiave]
reviewed: 2026-01-01       # ultima verifica umana -> guida lo SLA di freschezza
---
```

Campi opzionali per i fatti che invecchiano: `confidence`, `valid_from`,
`valid_until`, `superseded_by`.

**Regola d'oro:** un fatto che smette di essere vero **non si cancella**, si marca
con `valid_until` e si indica cosa lo sostituisce.

## Regole

- `raw/` e grezzo: fonti e documenti come sono. Le pagine ragionate e collegate con
  `[[wikilink]]` vanno in `wiki/`.
- Naming in `kebab-case` ascii, senza spazi. Formato preferito `.md`.
- **Non inventare:** se una fonte manca, segnalalo nel file invece di riempirlo.
"""

README = """# core — scheletro di second brain

Il motore, senza la conoscenza di nessuno. Ci metti la tua.

## Cosa c'e dentro

- **Grafo** della conoscenza con sottografi per area e tre viste (estesa, compatta,
  atlante 3D esplorabile che si apre offline).
- **Provenienza**: ogni pagina curata sa da quali fonti grezze deriva, e l'arco
  esiste nel grafo, non solo nella documentazione.
- **Freschezza e bi-temporalita**: SLA per area, fatti che scadono senza essere
  cancellati.
- **Ricerca** BM25 in Python puro, senza dipendenze, con misura di confidenza che
  dichiara cosa sta misurando.
- **Anello di apprendimento**: le lezioni entrano nel prior del ragionamento solo se
  portano un appiglio esterno verificabile, e il prior ha un tetto di dimensione.
- **API** con token, rate limit e validazione dell'input.
- **Guardie**: la suite di test che impedisce alle regole di degradare in silenzio.

## Partenza

```bash
python onboarding.py
```

Chiede le tue macroaree e se attivare il plugin AION. Poi:

```bash
python tools/rebuild_all.py
```

## Training e plugin — due cose diverse

- **`training/`** — un imprinting iniziale: un modo di ragionare gia formato che il
  brain puo adottare. Se ne sceglie **al massimo uno**, o nessuno. Disponibile:
  **aion**, modello di pensiero a livelli con oracolo I Ching eseguibile.
- **`plugins/`** — capacita aggiuntive che non toccano il pensiero. Se ne attivano
  quante se ne vuole.

Senza training il motore funziona lo stesso: il modo di ragionare lo costruisci
strada facendo, e l'anello delle lezioni lo registra man mano.
"""

CLAUDE = """## Come lavorare in questo repo

**Percorsi.** `raw/`, `wiki/`, `engine/` e `areas.json` sono relativi al brain attivo:
`python tools/brain.py` ne stampa la cartella. In questa installazione il brain e' la
cartella stessa (stampa `.`); in un'officina con piu' brain e' `brains/<nome>`.

- La conoscenza sta in due strati: `raw/` (fonti grezze) e `wiki/` (pagine curate e
  collegate con `[[wikilink]]`). I wikilink si risolvono **solo dentro la stessa
  cartella**: i concetti condivisi tra aree si dichiarano in `engine/bridges.json`.
- Le macroaree si dichiarano in `areas.json`, un registro solo: parole chiave per
  instradare le domande, SLA, coesione, strati generati, colore. Nessuna area va
  scritta dentro il codice. Gli schemi dei contratti sono in `schema/`.
- Dopo ogni modifica: **`python tools/rebuild_all.py`**, che rigenera grafo, viste,
  indice di ricerca, metriche e fa girare le guardie. Poi commit.

## Provenienza (non negoziabile)

Ogni affermazione con numeri o date porta la sua fonte. `engine/provenance.json`
cuce la catena fonte->conoscenza nel grafo.

## Memoria operativa

Chiudi ogni lavoro registrando cosa hai imparato:

```bash
python tools/lesson_log.py --skill <nome> --domanda "..." \\
  --quando "il segnale che fa scattare la regola" \\
  --allora "cosa fare" \\
  --ancora "test:... | errore:... | misura:... | utente:... | guardia:..."
```

Senza `--ancora` resta un'osservazione: la sintesi di una sessione, che entra nel prior
come contesto ma mai fra le regole. E' la difesa contro l'autofagia: un brain che
impara dalla prosa che il modello ha scritto amplifica i propri errori a ogni giro.
"""

ONBOARDING = """# -*- coding: utf-8 -*-
\"\"\"Prima configurazione di questo brain: le tue macroaree e, se vuoi, un training.

La logica vive nel motore (tools/onboarding.py), una volta sola; questo file e' solo
la porta d'ingresso per chi apre lo scheletro.
  python onboarding.py                         interattivo
  python onboarding.py --aree "a,b" --training nessuno
\"\"\"
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.onboarding import main  # noqa: E402

if __name__ == "__main__":
    main()
"""


def main():
    conta = costruisci()
    n = sum(len(f) for _, _, f in os.walk(CORE))
    kb = sum(os.path.getsize(os.path.join(r, f))
             for r, _, fs in os.walk(CORE) for f in fs) / 1024
    print(f"core/ generato: {n} file, {kb:.0f} KB")
    print(f"  motore: {conta['motore']} tool · guardie: {conta['guardie']} test")
    print(f"  training aion: {conta['training']} file (opzionale) "
          f"· plugin: {conta['plugin']} file")
    print("  nessuna nota, nessuna pagina curata, nessuna lezione: solo lo scheletro.")
    print("  partenza per chi lo riceve:  python onboarding.py")


if __name__ == "__main__":
    main()
