# -*- coding: utf-8 -*-
"""
Guardie sulla coerenza tra CHI SEGNALA e CHI RIPARA.

IL DIFETTO CHE HANNO CHIUSO. freshness_report elencava 57 file "senza front-matter"
e consigliava `add_frontmatter.py --apply`. Ma quel comando ne toccava zero:
55 erano in uno strato GENERATO che il tool si rifiuta (giustamente) di modificare,
e i 2 restanti stavano fuori dalla sua copertura.

Un rapporto che consiglia un comando destinato a non fare nulla e' peggio di un
rapporto muto: insegna a ignorare i rapporti. Questi test tengono allineate le due
liste per sempre — quello che viene segnalato dev'essere esattamente quello che
qualcuno puo' riparare.
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import frontmatter as fm  # noqa: E402


def _senza_frontmatter():
    """Tutti i .md di conoscenza privi di front-matter, per percorso POSIX."""
    fuori = []
    for base in ("raw", "wiki", "reports"):
        for f in (ROOT / base).rglob("*.md"):
            meta, _ = fm.leggi(f)
            if not meta:
                fuori.append(f.relative_to(ROOT).as_posix())
    return sorted(fuori)


def test_lo_strato_generato_e_riconosciuto():
    """La regola vive in un posto solo: se qualcuno la duplica, divergera'."""
    assert fm.e_generato("wiki/aion/aion-oracle.md")
    assert fm.e_generato(r"wiki\aion\index.md"), "deve reggere anche i percorsi Windows"
    assert not fm.e_generato("wiki/divulgazione/index.md")
    assert not fm.e_generato("raw/aion/aion-oracle.md"), "la FONTE non e' generata"


def test_add_frontmatter_non_duplica_la_regola():
    """Se add_frontmatter ridefinisse la propria lista, le due divergerebbero
    silenziosamente: e' esattamente come e' nato il difetto dei sette parser."""
    testo = (ROOT / "tools" / "add_frontmatter.py").read_text(encoding="utf-8")
    assert "from tools.frontmatter import STRATI_GENERATI" in testo, \
        "add_frontmatter deve importare la regola, non riscriverla"


def test_nessun_file_riparabile_resta_senza_front_matter():
    """Lo stato desiderato: tutto cio' che PUO' avere provenienza, ce l'ha."""
    riparabili = [f for f in _senza_frontmatter() if not fm.e_generato(f)]
    assert not riparabili, (
        "file senza front-matter e non esenti: " + ", ".join(riparabili) +
        "\nrimedio:  python tools/add_frontmatter.py --apply")


def test_il_rapporto_non_consiglia_un_comando_inutile():
    """Il cuore della faccenda, verificato eseguendo davvero i due strumenti:
    se la freschezza segnala file mancanti, l'arricchimento deve trovarne almeno
    altrettanti da scrivere. Zero contro N e' la contraddizione da impedire."""
    amb = dict(os.environ)
    amb["PYTHONIOENCODING"] = "utf-8"

    rapporto = subprocess.run([sys.executable, "tools/freshness_report.py"],
                              cwd=str(ROOT), capture_output=True, env=amb)
    assert rapporto.returncode == 0, rapporto.stderr.decode("utf-8", "replace")
    testo_rapporto = rapporto.stdout.decode("utf-8", "replace")

    anteprima = subprocess.run([sys.executable, "tools/add_frontmatter.py"],
                               cwd=str(ROOT), capture_output=True, env=amb)
    assert anteprima.returncode == 0, anteprima.stderr.decode("utf-8", "replace")
    testo_anteprima = anteprima.stdout.decode("utf-8", "replace")

    segnala = "Senza front-matter:" in testo_rapporto
    ripara = " 0 file da arricchire" not in testo_anteprima
    assert segnala == ripara, (
        "freschezza e arricchimento in disaccordo.\n"
        f"  la freschezza segnala mancanze: {segnala}\n"
        f"  l'arricchimento ne troverebbe:  {ripara}\n"
        "--- freschezza ---\n" + testo_rapporto[-500:] +
        "\n--- arricchimento ---\n" + testo_anteprima[-400:])


def test_gli_strati_generati_restano_intatti():
    """La protezione non deve mai cedere: scrivere li' farebbe divergere la pagina
    dal modello che la genera, e la fonte unica smetterebbe di essere unica."""
    amb = dict(os.environ)
    amb["PYTHONIOENCODING"] = "utf-8"
    esito = subprocess.run([sys.executable, "tools/add_frontmatter.py"],
                           cwd=str(ROOT), capture_output=True, env=amb)
    assert "[protetti]" in esito.stdout.decode("utf-8", "replace"), \
        "add_frontmatter non dichiara piu' di proteggere gli strati generati"


def test_la_copertura_segue_le_aree_esistenti():
    """TARGET era un elenco a mano ('raw/', 'wiki/data-science/'): ogni macroarea
    nuova restava scoperta in silenzio. Deve valere per sottrazione."""
    testo = (ROOT / "tools" / "add_frontmatter.py").read_text(encoding="utf-8")
    riga = next(r for r in testo.splitlines() if r.startswith("TARGET"))
    assert "wiki/data-science/" not in riga, \
        "la copertura elenca ancora una singola area: le nuove resterebbero fuori"
    assert '"wiki/"' in riga and '"raw/"' in riga
