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
import os
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


def _ignorati(candidati):
    """I percorsi che git ignora per costruzione (cache, output rigenerabili).

    DIFETTO REALE della prima versione di questa guardia: controllava il DISCO. Sulla
    macchina dell'autore graphify-out/cache esiste, quindi ROADMAP.md passava; in CI,
    su un clone pulito, no — e la CI e' fallita per un controllo che in locale era
    verde. Citare un artefatto ignorato e' legittimo ('cancella la cache'): lo si
    riconosce chiedendolo a git, che risponde anche per cartelle che non esistono."""
    import subprocess
    righe = []
    for p in candidati:
        for base in ("", os.path.relpath(BRAIN, ROOT).replace("\\", "/")):
            q = f"{base}/{p}" if base not in ("", ".") else p
            righe += [q, q + "/"]
    try:
        esito = subprocess.run(["git", "check-ignore", "--stdin", "-v"], cwd=str(ROOT),
                               input="\n".join(righe).encode("utf-8"),
                               capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    # Si accetta solo una risposta che nomina un pattern VERO. Per un percorso che
    # finisce con '/' e non esiste, git puo' rispondere "ignorato" citando una riga
    # VUOTA di .gitignore (pattern vuoto): verificato, e senza questo filtro la guardia
    # dichiarava ignorato qualunque file inventato, e non vedeva piu' nulla.
    ignorati = set()
    for r in esito.stdout.decode("utf-8").splitlines():
        meta, _, percorso = r.partition("\t")
        if meta.split(":", 2)[-1].strip():
            ignorati.add(percorso.strip().rstrip("/"))
    return {p for p in candidati
            if any(q.rstrip("/").endswith(p) for q in ignorati)}


def _rotti(testo):
    assenti = set()
    for m in PERCORSO.finditer(testo):
        p = m.group(1).rstrip("/.")
        if any(c in p for c in "<*{…"):
            continue
        if not ((ROOT / p).exists() or (BRAIN / p).exists()):
            assenti.add(p)
    return sorted(assenti - _ignorati(assenti)) if assenti else []


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


def test_nessun_presupposto_dichiarato_a_vuoto():
    """Il registro dei presupposti (conftest.py) deve nominare solo test che esistono.

    DIFETTO REALE: questa guardia viveva DENTRO conftest.py, dove pytest non raccoglie
    test. Non e' mai stata eseguita: una guardia verde perche' nessuno la guardava."""
    import conftest
    esistenti = {p.name for p in (ROOT / "tests").glob("test_*.py")}
    for chiave in conftest.RICHIEDE:
        assert chiave.split("::")[0] in esistenti, f"RICHIEDE nomina {chiave}, che non esiste"
    for chiave in set(conftest.RICHIEDE.values()):
        assert chiave in conftest.PRESUPPOSTI, f"presupposto sconosciuto: {chiave}"


def test_le_skill_degli_altri_agenti_sono_una_copia_generata():
    """.agents/skills/ (standard Agent Skills: Codex, Gemini CLI...) deve essere
    identica a .claude/skills/, la fonte. Due copie tenute a mano divergono: e' come le
    copie del motore dentro i brain erano arrivate a 17 tool diversi su 31."""
    if not (ROOT / ".agents" / "skills").is_dir():
        import pytest
        pytest.skip("nessuna copia per altri agenti in questa installazione")
    from tools.sync_agent_skills import differenze
    d = differenze()
    assert not d, f"skill divergenti: {d} — rigenera con python tools/sync_agent_skills.py"
