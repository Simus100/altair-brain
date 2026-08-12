# -*- coding: utf-8 -*-
"""
Guardie su core/: lo scheletro cedibile.

COSA PROTEGGONO. core/ e' il motore senza l'esperienza acquisita — la parte che si
puo' consegnare a qualcun altro. Due cose lo rovinerebbero, entrambe in silenzio:

1. UNA FUGA. Se una nota, una lezione o il nome di un progetto personale finisce
   nell'export, non e' piu' uno scheletro: e' il brain di qualcuno con dei buchi.
   Il danno non si vede aprendo la cartella, si vede quando e' gia' stata consegnata.

2. LA DERIVA. core/ e' GENERATO. Una copia che qualcuno modifica a mano diverge dalla
   sorgente entro poche settimane e nessuno se ne accorge, esattamente come il passo 0
   del reasoner e' rimasto sei settimane a leggere un file morto.
"""
import json
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.skipif(not CORE.exists(),
                                reason="core/ assente: esegui tools/build_core.py")

# Nomi che appartengono al brain di una persona, non al motore.
PERSONALI = re.compile(
    r"\b(universalis|macelloni|bookforge|magazzino|olist|iran|davos|austerit|"
    r"enneagramm|styledna|geko|simone)\b", re.I)


def file_del_motore():
    """Tutto core/ tranne i plugin: quelli contengono materiale dichiarato."""
    return [f for f in CORE.rglob("*")
            if f.is_file() and "plugins" not in f.parts]


def test_il_motore_non_contiene_contenuto_personale():
    """La guardia principale: lo scheletro dev'essere di chiunque."""
    fughe = {}
    for f in file_del_motore():
        try:
            testo = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        trovati = sorted(set(m.lower() for m in PERSONALI.findall(testo)))
        if trovati:
            fughe[f.relative_to(CORE).as_posix()] = trovati
    assert not fughe, "contenuto personale nello scheletro: " + json.dumps(
        fughe, ensure_ascii=False)


def test_nessuna_conoscenza_acquisita():
    """Niente note, niente pagine curate, niente report: solo le cartelle vuote."""
    for cartella, ammessi in (("wiki", 1), ("raw", 1), ("reports", 1)):
        n = sum(1 for f in (CORE / cartella).rglob("*") if f.is_file())
        assert n <= ammessi, f"core/{cartella}/ contiene {n} file: dovrebbe essere vuota"


def test_nessuna_lezione_di_nessuno():
    """Il registro dell'esperienza parte a zero: e' l'esperienza di chi lo usera'."""
    assert (CORE / "engine" / "lessons.jsonl").read_text(encoding="utf-8").strip() == ""


def test_nessuna_area_di_nessuno():
    """Le aree sono configurazione: l'export ne porta una di esempio, non le vere."""
    aree = json.loads((CORE / "areas.json").read_text(encoding="utf-8"))["areas"]
    ids = [a["id"] for a in aree]
    assert ids == ["esempio"], f"aree reali finite nello scheletro: {ids}"
    router = json.loads((CORE / "engine" / "router.json").read_text(encoding="utf-8"))
    assert list(router["aree"]) == ["esempio"]


def test_il_motore_c_e_tutto():
    """Uno scheletro senza il motore non serve a niente: si controlla che i pezzi
    portanti ci siano davvero, non solo che manchi il resto."""
    attesi = ["tools/rebuild_all.py", "tools/build_search_index.py", "tools/search.py",
              "tools/graph_health.py", "tools/lesson_log.py", "tools/lessons_digest.py",
              "tools/build_atlas_view.py", "tools/frontmatter.py", "tools/console.py",
              "server/app.py", "onboarding.py", "README.md", "CLAUDE.md",
              ".github/workflows/validate.yml"]
    mancanti = [p for p in attesi if not (CORE / p).exists()]
    assert not mancanti, f"pezzi del motore assenti dallo scheletro: {mancanti}"


def test_aion_e_un_plugin_non_il_motore():
    """La scelta dichiarata: si parte senza modello di pensiero, o si adotta questo."""
    assert (CORE / "plugins" / "aion").is_dir(), "il plugin AION non e stato esportato"
    assert not (CORE / "tools" / "oracle_cast.py").exists(), \
        "l'oracolo sta nel motore: dovrebbe essere nel plugin"
    assert not (CORE / "engine" / "aion.model.json").exists(), \
        "il modello di pensiero sta nel motore: dovrebbe essere nel plugin"


def test_lo_scheletro_e_deterministico():
    """Generato due volte deve dare lo stesso risultato, altrimenti ogni rebuild
    sporca il diff e la CI non distingue un cambiamento vero dal rumore."""
    def impronta():
        # __pycache__ e' un artefatto di compilazione, non parte dell'export: senza
        # escluderlo il test diventa rosso solo perche' un altro test ha compilato.
        return sorted((f.relative_to(CORE).as_posix(), f.stat().st_size)
                      for f in CORE.rglob("*")
                      if f.is_file() and "__pycache__" not in f.parts)
    prima = impronta()
    subprocess.run([sys.executable, "tools/build_core.py"], cwd=str(ROOT),
                   check=True, capture_output=True)
    assert impronta() == prima, "core/ cambia tra due generazioni consecutive"


def test_l_onboarding_e_eseguibile():
    """La prima cosa che tocca chi riceve lo scheletro non puo' essere rotta."""
    esito = subprocess.run([sys.executable, "-c",
                            "import ast,pathlib;ast.parse(pathlib.Path('core/onboarding.py')"
                            ".read_text(encoding='utf-8'))"],
                           cwd=str(ROOT), capture_output=True)
    assert esito.returncode == 0, esito.stderr.decode("utf-8", "replace")


def test_i_tool_esportati_compilano():
    """Un export che non compila e' peggio di nessun export."""
    esito = subprocess.run([sys.executable, "-m", "compileall", "-q", str(CORE / "tools")],
                           capture_output=True)
    assert esito.returncode == 0, esito.stdout.decode("utf-8", "replace")[-800:]
