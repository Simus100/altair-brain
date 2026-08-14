# -*- coding: utf-8 -*-
"""
Guardie sull'OFFICINA: il repo non e' un brain, e' il posto dove i brain si fanno.

    tools/ tests/ server/   il MOTORE, sorgente unica
    core/                   il PRODOTTO, generato dal motore
    brains/                 le ISTANZE, piu il registro

TRE CONFUSIONI DA IMPEDIRE, tutte silenziose:

1. IL PRODOTTO DENTRO IL SAPERE. graphify indicizza tutto il repo: da quando core/
   esiste, 1191 nodi su 3084 — il 39% del grafo — erano copie del motore esportato.
   Gonfiavano le metriche, sporcavano le tre viste, entravano nell'indice di ricerca
   e falsavano l'equilibrio tra aree. E quel rumore CRESCE con ogni brain creato.

2. IL MOTORE INCOLLATO A UN BRAIN. Se i tool costruiscono i percorsi da dove vivono
   loro, un motore puo' servire un brain solo — ed era la ragione per cui il brain di
   una persona restava mescolato all'infrastruttura.

3. UN'ISTANZA CHE NON SA STARE IN PIEDI. Un brain creato da core/ deve funzionare da
   solo: se dipende da qualcosa che sta nell'officina, non e' un'istanza, e' un pezzo.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GRAFO = ROOT / "graphify-out" / "graph.json"


# ---------------------------------------------- 1. il prodotto non e' conoscenza
@pytest.mark.skipif(not GRAFO.exists(), reason="graph.json assente")
def test_gli_artefatti_non_stanno_nel_grafo():
    """core/ e brains/ sono artefatti e istanze: nel grafo del brain non ci vanno."""
    from tools.graph_prune import ESCLUSE
    g = json.loads(GRAFO.read_text(encoding="utf-8"))
    dentro = sorted({(n.get("source_file") or "").replace("\\", "/").split("/")[0]
                     for n in g["nodes"]
                     if (n.get("source_file") or "").replace("\\", "/").startswith(ESCLUSE)})
    assert not dentro, (
        f"artefatti nel grafo del brain: {dentro} — manca la potatura "
        "(python tools/graph_prune.py, subito dopo 'graphify update')")


def test_la_potatura_gira_prima_di_chi_legge_il_grafo():
    """L'ordine conta: se la potatura arrivasse dopo le viste o l'indice, quelli
    avrebbero gia' letto il grafo sporco e nessuno se ne accorgerebbe."""
    testo = (ROOT / "tools" / "rebuild_all.py").read_text(encoding="utf-8")
    # Solo la lista STEPS: la docstring in testa elenca i passi in prosa e falserebbe
    # il confronto di posizione (verificato: il test falliva su quella, non sui passi).
    passi = testo[testo.index("STEPS = ["):testo.index("failed = False")]
    i_prune = passi.find("graph_prune.py")
    assert i_prune > 0, "la potatura non e nella pipeline"
    for dopo in ("build_atlas_view.py", "build_search_index.py", "graph_metrics.py",
                 "build_area_graphs.py"):
        assert passi.find(dopo) > i_prune, \
            f"{dopo} legge il grafo PRIMA della potatura: leggerebbe gli artefatti"


# ---------------------------------------------- 2. il motore non e' legato a un brain
def test_il_motore_risolve_il_brain_invece_di_presumerlo():
    """I percorsi del contenuto passano da tools/brain.py: e' il punto unico che
    permette a un motore di servire piu' brain."""
    from tools.brain import brain_root, BRAIN
    assert os.path.isdir(BRAIN)
    # default sicuro: senza indicazioni, il brain e' il repo stesso — cosi' un'istanza
    # autosufficiente (core/ dopo l'onboarding) si comporta esattamente come prima
    assert brain_root(str(ROOT)) == str(ROOT) or os.path.isdir(brain_root(str(ROOT)))


def test_i_tool_non_costruiscono_percorsi_di_contenuto_da_ROOT():
    """La regressione da impedire: un tool nuovo che scrive os.path.join(ROOT, 'wiki')
    torna a legare il motore a un brain solo, e nessun test lo noterebbe."""
    import re
    pat = re.compile(r'(?:os\.path\.join\(\s*ROOT\s*,\s*|ROOT\s*/\s*)'
                     r'"(raw|wiki|reports|metrics|graphify-out)"')
    colpevoli = {}
    for f in sorted((ROOT / "tools").glob("*.py")):
        if f.name in ("brain.py", "build_core.py"):   # build_core lavora sull'officina
            continue
        n = pat.findall(f.read_text(encoding="utf-8"))
        if n:
            colpevoli[f.name] = sorted(set(n))
    assert not colpevoli, (
        "tool che presumono il brain invece di risolverlo: " + json.dumps(colpevoli) +
        "\nusa:  from tools.brain import BRAIN")


def test_il_brain_si_puo_spostare():
    """La prova funzionale: puntando ALTAIR_BRAIN altrove, i tool seguono."""
    import importlib
    from tools import brain as mod
    finto = ROOT / "core"          # una cartella che ha la forma di un brain
    os.environ["ALTAIR_BRAIN"] = "core"
    try:
        importlib.reload(mod)
        assert mod.BRAIN == str(finto.resolve()), \
            "ALTAIR_BRAIN non sposta il contenuto: il motore resta legato al repo"
    finally:
        os.environ.pop("ALTAIR_BRAIN", None)
        importlib.reload(mod)


# ---------------------------------------------- 3. le istanze stanno in piedi
def test_il_registro_dei_brain_esiste_ed_e_valido():
    reg = ROOT / "brains" / "brains.json"
    assert reg.exists(), "manca brains/brains.json: il repo non sa quali brain contiene"
    d = json.loads(reg.read_text(encoding="utf-8"))
    assert "brains" in d and isinstance(d["brains"], list)
    for b in d["brains"]:
        assert {"nome", "percorso"} <= set(b), f"voce incompleta nel registro: {b}"
        assert (ROOT / b["percorso"]).is_dir(), \
            f"il registro elenca {b['percorso']}, che non esiste"


def test_si_puo_creare_un_brain_e_sta_in_piedi(tmp_path):
    """La prova che conta: un brain nuovo nasce da core/, si configura e la sua
    pipeline gira — senza nulla dell'officina."""
    import shutil
    core = ROOT / "core"
    if not core.is_dir():
        pytest.skip("core/ assente")
    istanza = tmp_path / "istanza"
    shutil.copytree(core, istanza)

    amb = dict(os.environ)
    amb["PYTHONIOENCODING"] = "utf-8"
    amb.pop("ALTAIR_BRAIN", None)
    esito = subprocess.run([sys.executable, "onboarding.py"], cwd=str(istanza),
                           input="prova\nProva\ndescrizione\n\nn\n".encode("utf-8"),
                           capture_output=True, env=amb, timeout=180)
    assert esito.returncode == 0, esito.stderr.decode("utf-8", "replace")[-500:]

    aree = json.loads((istanza / "areas.json").read_text(encoding="utf-8"))["areas"]
    assert [a["id"] for a in aree] == ["prova"], "l'onboarding non ha scritto l'area"
    assert (istanza / "raw" / "prova").is_dir(), "manca la cartella dell'area in raw/"
    assert (istanza / "wiki" / "prova").is_dir()
    # l'inferenza vive in raw/ di OGNI brain, e parte vuota
    assert (istanza / "engine" / "lessons.jsonl").read_text(encoding="utf-8").strip() == ""


def test_la_porta_dice_quale_brain_stai_guardando():
    """Con un brain solo si intuisce; con due, una porta che non lo dice e' una
    trappola — apri tre viste senza sapere di CHE COSA."""
    porta = ROOT / "graphify-out" / "index.html"
    if not porta.exists():
        pytest.skip("porta non generata")
    assert "stai guardando" in porta.read_text(encoding="utf-8")


def test_il_selettore_compare_quando_ci_sono_altri_brain(tmp_path):
    """La funzione che costruisce l'elenco deve reggere sia il caso a un brain
    (nessun selettore, niente rumore) sia quello a piu' brain."""
    import importlib
    from tools import build_views_index as bvi
    importlib.reload(bvi)
    altri = bvi.altri_brain()
    reg = json.loads((ROOT / "brains" / "brains.json").read_text(encoding="utf-8"))
    # Tutti TRANNE quello su cui sei: il brain corrente e' nel registro come gli
    # altri (non e' un default anonimo), ma nel selettore punterebbe a se stesso.
    assert len(altri) == len(reg["brains"]) - 1, \
        "il selettore deve elencare tutti i brain del registro tranne quello corrente"
    nomi = {b["nome"] for b in altri}
    assert bvi.brain_corrente() not in nomi, "il selettore elenca il brain corrente"
    for b in altri:
        assert b["href"].startswith("../"), \
            "il link a un altro brain deve essere RELATIVO: la porta si apre da file://"
        assert "pronto" in b, "manca l'indicazione se il grafo di quel brain esiste"


def test_un_brain_vergine_non_si_lamenta_al_primo_avvio(tmp_path):
    """Un prodotto che al primo avvio segnala contenuto gia' scaduto insegna a
    ignorare i suoi stessi rapporti. Il README di raw/ non deve portare una data
    fissa: e' documentazione della cartella, non conoscenza che invecchia."""
    core = ROOT / "core"
    if not core.is_dir():
        pytest.skip("core/ assente")
    # Si guarda il SUO front-matter, non il testo: il README documenta la convenzione
    # con un esempio che contiene 'date:' e 'reviewed:' — cercarli nel corpo darebbe
    # un falso positivo sulla documentazione stessa.
    from tools.frontmatter import leggi
    meta, _ = leggi(core / "raw" / "README.md")
    assert meta is not None, "il README dello scheletro non ha front-matter"
    assert not ({"date", "reviewed"} & set(meta)), \
        (f"il README dello scheletro invecchia (campi {sorted(set(meta) & {'date','reviewed'})}): "
         "un brain appena creato risulterebbe gia' scaduto")


def test_ogni_istanza_si_chiama_col_proprio_nome():
    """DIFETTO REALE: dentro un'istanza BRAIN e ROOT coincidono, quindi il confronto
    faceva dichiarare 'brain di riferimento' a QUALSIASI brain — aprivi l'atlante di
    'cucina' e diceva di essere il principale. Il riferimento si riconosce dall'essere
    un'officina (ha core/ e brains/), non dal fatto che i percorsi coincidano."""
    import importlib
    from tools import build_views_index as bvi
    importlib.reload(bvi)
    reg = json.loads((ROOT / "brains" / "brains.json").read_text(encoding="utf-8"))["brains"]
    nomi = {b["nome"] for b in reg}
    # NESSUN brain e' un default anonimo: anche quello che vive nella radice ha una
    # voce nel registro e si chiama col suo nome.
    assert bvi.brain_corrente() in nomi, (
        f"il brain corrente si chiama '{bvi.brain_corrente()}', assente dal registro")
    for b in reg:
        porta = ROOT / b["percorso"] / "graphify-out" / "index.html"
        if not porta.exists():
            continue
        assert f"<b>{b['nome']}</b>" in porta.read_text(encoding="utf-8"), \
            f"la porta di {b['nome']} non dichiara il proprio nome"


def test_il_selettore_punta_a_file_che_esistono():
    """Un selettore che offre porte inesistenti e' peggio di nessun selettore."""
    from tools import build_views_index as bvi
    for b in bvi.altri_brain():
        if not b["pronto"]:
            continue
        dest = (ROOT / "graphify-out" / b["href"]).resolve()
        assert dest.exists(), f"il selettore punta a {b['href']}, che non esiste"


def test_un_brain_non_legge_la_storia_di_un_altro():
    """DIFETTO REALE: graph_health chiedeva a git 'HEAD~1:graphify-out/graph.json',
    ma i percorsi di git sono relativi al REPOSITORY. Da brains/<nome>/ tornava il
    grafo del brain di riferimento: un'istanza confrontava i propri nodi con quelli
    di un'altra e falliva l'anti-regressione per un calo mai avvenuto."""
    testo = (ROOT / "tools" / "graph_health.py").read_text(encoding="utf-8")
    assert "rev-parse" in testo and "--show-toplevel" in testo, \
        "il baseline non e calcolato rispetto alla radice del repository"
    assert 'f"{prev_ref}:graphify-out/graph.json"' not in testo, \
        "percorso git fisso: un'istanza leggerebbe la storia del brain di riferimento"
