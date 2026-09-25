# -*- coding: utf-8 -*-
"""
Guardia sui percorsi scritti PER GLI AGENTI: documenti di istruzione e skill.

IL DIFETTO CHE CHIUDE. Spostato il brain dell'autore dalla radice a brains/aion, le
istruzioni sono rimaste com'erano: 56 percorsi nei documenti per agenti non esistevano
piu', comprese tutte e quattro le skill. /aion, lanciata dalla radice, al passo 0
cercava engine/aion.model.json — che dalla radice non c'e'. Nessun test lo vedeva:
le guardie controllavano il codice, non cio' che il codice dice agli agenti di fare.

LA REGOLA (dichiarata in CLAUDE.md, AGENTS.md, GUIDA.md, README.md e in ogni skill):
i percorsi di contenuto sono relativi al BRAIN ATTIVO, quelli del motore alla radice.
Quindi un percorso citato e' valido se esiste in uno dei due posti.

Si saltano i segnaposto (<area>, <nome>, *, {…}): descrivono una forma, non un file.
Di ROADMAP.md si controlla solo la parte operativa: lo storico cita per forza file
che non esistono piu', ed e' giusto che resti com'era.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from tools.brain import BRAIN as _b
    BRAIN = pathlib.Path(_b)
except ImportError:
    BRAIN = ROOT

DOCUMENTI = ["CLAUDE.md", "AGENTS.md", "GUIDA.md", "README.md", "ROADMAP.md"]
CARTELLE = ("tools", "tests", "server", "core", "brains", "engine", "raw", "wiki",
            "reports", "graphify-out", "metrics", "schema")
PERCORSO = re.compile(
    r"(?<![\w/.<-])((?:" + "|".join(CARTELLE) + r")/[A-Za-z0-9_./\-]*[A-Za-z0-9_/])")


def _testi():
    for nome in DOCUMENTI:
        p = ROOT / nome
        if p.exists():
            t = p.read_text(encoding="utf-8")
            if nome == "ROADMAP.md" and "## Completato" in t:
                t = t[:t.index("## Completato")]
            yield nome, t
    for p in sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md")):
        yield p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")


def _rotti(testo):
    fuori = set()
    for m in PERCORSO.finditer(testo):
        p = m.group(1).rstrip("/.")
        if any(c in p for c in "<*{…"):
            continue
        if not ((ROOT / p).exists() or (BRAIN / p).exists()):
            fuori.add(p)
    return sorted(fuori)


def test_ogni_percorso_citato_agli_agenti_esiste():
    rotti = {nome: r for nome, t in _testi() if (r := _rotti(t))}
    assert not rotti, (
        "percorsi citati agli agenti che non esistono ne' nella radice ne' nel brain "
        f"attivo ({BRAIN.name}): {rotti}")


def test_la_regola_dei_percorsi_e_dichiarata():
    """Un percorso relativo al brain e' corretto solo se chi legge SA che lo e'."""
    senza = [nome for nome, t in _testi()
             if nome in ("CLAUDE.md", "AGENTS.md") or nome.endswith("SKILL.md")
             if "tools/brain.py" not in t]
    assert not senza, f"documenti che non dicono come trovare il brain attivo: {senza}"


def test_la_guardia_vede_un_percorso_rotto():
    """Senza questa prova la guardia potrebbe non vedere nulla e restare verde."""
    assert _rotti("leggi engine/file-che-non-esiste.json") == ["engine/file-che-non-esiste.json"]
    assert _rotti("smista in raw/<area>/ e poi tools/brain.py") == []
