# -*- coding: utf-8 -*-
"""
Guardia sulla codifica della console (tools/console.py).

STORIA. Lo stesso guasto si e' presentato CINQUE volte, ogni volta su un tool diverso:
style_check moriva su una freccia, search su un estratto accentato, oracle_cast sugli
hanzi degli esagrammi. La console di Windows parla cp1252; qualsiasi tool che stampi
contenuto del brain puo' incontrare un carattere fuori tabella e terminare con
UnicodeEncodeError PRIMA di dire quello che aveva trovato.

E' il modo peggiore di fallire: non un risultato sbagliato, ma nessun risultato, con
una traccia di stack al posto della risposta.

Rattoppare il tool colpito lasciava gli altri trenta esposti. Questo test chiude la
classe: ogni tool che stampa deve passare per usa_utf8(). Un tool nuovo che se ne
dimentica fallisce qui, non davanti a chi lo usa.
"""
import ast
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

# Moduli di sola libreria: non hanno una riga di comando, non stampano.
NON_ESEGUIBILI = {"__init__.py", "console.py", "frontmatter.py"}


def tool_che_stampano():
    """Ogni tool che puo' scrivere sullo standard output quando viene eseguito."""
    fuori = []
    for f in sorted(TOOLS.glob("*.py")):
        if f.name in NON_ESEGUIBILI:
            continue
        testo = f.read_text(encoding="utf-8")
        if "print(" in testo:
            fuori.append(f)
    return fuori


def test_ci_sono_tool_da_controllare():
    """Se questo scende a zero, il test si e' rotto in silenzio."""
    assert len(tool_che_stampano()) >= 25


def test_ogni_tool_che_stampa_usa_la_guardia():
    """L'invariante. Vale per i tool nuovi quanto per quelli vecchi."""
    scoperti = [f.name for f in tool_che_stampano()
                if "usa_utf8" not in f.read_text(encoding="utf-8")]
    assert not scoperti, (
        "tool che stampano senza guardia di codifica: " + ", ".join(scoperti) +
        "\naggiungi:  from tools.console import usa_utf8; usa_utf8()")


def test_la_guardia_non_tocca_chi_importa():
    """Deve attivarsi SOLO da riga di comando: se scattasse all'import,
    riconfigurerebbe lo stdout anche di pytest e di chiunque usi questi moduli."""
    problemi = []
    for f in tool_che_stampano():
        albero = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for nodo in ast.walk(albero):
            if not (isinstance(nodo, ast.Call) and getattr(nodo.func, "id", "") == "usa_utf8"):
                continue
            # la chiamata deve stare dentro un 'if __name__ == "__main__"'
            # oppure dentro una funzione (invocata solo dal main)
            dentro = False
            for cont in ast.walk(albero):
                if isinstance(cont, (ast.FunctionDef, ast.If)) and nodo in ast.walk(cont):
                    if isinstance(cont, ast.FunctionDef):
                        dentro = True
                    elif isinstance(cont.test, ast.Compare) and \
                            getattr(cont.test.left, "id", "") == "__name__":
                        dentro = True
            if not dentro:
                problemi.append(f.name)
    assert not problemi, f"usa_utf8() chiamato all'import in: {sorted(set(problemi))}"


def test_la_guardia_regge_un_carattere_fuori_tabella(tmp_path):
    """La prova vera: un sottoprocesso con stdout cp1252 che stampa un hanzi.
    Senza la guardia questo esce con exit 1 e UnicodeEncodeError."""
    script = tmp_path / "prova.py"
    script.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from tools.console import usa_utf8\n"
        "usa_utf8()\n"
        "print('\\u8c6b \\u2192 \\u00e8 \\u00ab citazione \\u00bb')\n",
        encoding="utf-8")
    amb = dict(os.environ)
    amb.pop("PYTHONIOENCODING", None)
    amb.pop("PYTHONUTF8", None)
    esito = subprocess.run([sys.executable, str(script)], capture_output=True, env=amb)
    assert esito.returncode == 0, esito.stderr.decode("utf-8", "replace")


@pytest.mark.parametrize("tool", ["search.py", "style_check.py", "oracle_cast.py"])
def test_i_tre_tool_gia_colpiti_non_muoiono_piu(tool):
    """Regressione sui casi reali: sono i tre che hanno fallito davanti all'utente."""
    argomenti = {
        "search.py": ["analisi dei dati", "--top", "2"],
        "style_check.py": ["brains/aion/wiki/divulgazione/index.md"],
        "oracle_cast.py": ["--hexagram", "16"],
    }[tool]
    amb = dict(os.environ)
    amb.pop("PYTHONIOENCODING", None)
    amb.pop("PYTHONUTF8", None)
    esito = subprocess.run([sys.executable, str(TOOLS / tool)] + argomenti,
                           cwd=str(ROOT), capture_output=True, env=amb)
    assert esito.returncode == 0, esito.stderr.decode("utf-8", "replace")[-600:]


def test_la_guardia_non_deve_mai_essere_fatale(tmp_path):
    """REGRESSIONE VERA, trovata dai test: rendere obbligatorio l'import di
    tools.console ha rotto report_update quando veniva copiato in un mini-repo
    senza quel modulo. Una protezione facoltativa che impedisce l'avvio e' peggio
    del guasto che previene: qui si verifica che l'assenza degradi, non uccida."""
    finto = tmp_path / "tools"
    finto.mkdir()
    # si copia UN tool senza console.py accanto: la situazione che ha rotto i test
    sorgente = TOOLS / "report_update.py"
    (finto / sorgente.name).write_text(sorgente.read_text(encoding="utf-8"),
                                       encoding="utf-8")
    esito = subprocess.run([sys.executable, str(finto / sorgente.name), "--help"],
                           capture_output=True)
    stderr = esito.stderr.decode("utf-8", "replace")
    assert "ModuleNotFoundError" not in stderr, \
        "il tool muore senza tools/console.py: l'import va reso non fatale"
    assert esito.returncode == 0, stderr[-400:]


def test_ogni_import_della_guardia_e_protetto():
    """L'invariante strutturale che corrisponde al test sopra."""
    scoperti = []
    for f in tool_che_stampano():
        testo = f.read_text(encoding="utf-8")
        if "from tools.console import usa_utf8" in testo and "except ImportError" not in testo:
            scoperti.append(f.name)
    assert not scoperti, f"import fatale di tools.console in: {scoperti}"
