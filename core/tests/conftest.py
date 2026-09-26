# -*- coding: utf-8 -*-
"""
Presupposti dei test: cosa deve esistere perche' una guardia abbia un oggetto.

IL DIFETTO CHE CHIUDE. Il motore e' unico, i brain no. Un brain appena consegnato
non ha un registro (e' solo, non c'e' nulla da elencare), non ha adottato un training
(niente modello, niente oracolo, niente reasoner), non ha plugin e non ha contenuto.
Le guardie che presuppongono una di queste cose non hanno un oggetto da verificare:
li' non sono rosse perche' il sistema e' rotto, sono rosse perche' non c'e' niente da
guardare.

E' la stessa regola gia' in vigore nella pipeline — un passo il cui tool non c'e'
viene SALTATO, non fa fallire tutto — applicata al banco di prova. Senza di essa lo
scheletro ceduto arrivava con 25 test rossi il primo giorno: la prima cosa che
chiunque lancia dopo una consegna, e l'unica impressione che conta.

REGOLA: un test che presuppone qualcosa lo DICHIARA qui. Non si toglie dallo
scheletro — resta, e si accende da solo il giorno in cui il presupposto compare.
"""
import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from tools.brain import BRAIN as _b
    BRAIN = pathlib.Path(_b)
except ImportError:
    BRAIN = ROOT


def _ha_registro():
    """Piu' brain nello stesso repo: il selettore, i percorsi relativi, l'officina."""
    return (ROOT / "brains" / "brains.json").exists()


def _ha_training():
    """Un training adottato: modello tipato, oracolo, reasoner, wiki generata."""
    return (BRAIN / "engine" / "aion.model.json").exists()


def _ha_contenuto():
    """Conoscenza vera: aree attive E pagine curate. Senza pagine non esistono gli
    archi fonte->sapere su cui si misurano atlante, provenienza e recupero: il brain
    'cucina' (due aree, quattro note, zero pagine) lo ha mostrato appena esportato."""
    try:
        aree = json.load(open(BRAIN / "areas.json", encoding="utf-8"))["areas"]
    except (OSError, ValueError, KeyError):
        return False
    pagine = [p for p in (BRAIN / "wiki").rglob("*.md")
              if p.name not in ("README.md", "index.md")] if (BRAIN / "wiki").is_dir() else []
    return len([a for a in aree if a.get("status") == "active"]) >= 2 and bool(pagine)


def _ha_esperienza():
    """Abbastanza registrazioni da mettere alla prova la memoria (almeno 20)."""
    p = BRAIN / "engine" / "lessons.jsonl"
    if not p.exists():
        return False
    return sum(1 for r in p.read_text(encoding="utf-8").splitlines() if r.strip()) >= 20


def _ha_plugin_scrittura():
    return (BRAIN / "plugins" / "scrittura").is_dir() or (ROOT / "tools" / "style_check.py").exists()


def _ha_corpus_data_science():
    """Le note di data-science del brain di riferimento: i test di recupero su
    'quartili / outlier / IQR' cercano proprio quelle."""
    d = BRAIN / "raw" / "data-science"
    return d.is_dir() and any(p.name != "README.md" for p in d.rglob("*.md"))


def _ha_report_verificati():
    return (BRAIN / "raw" / "divulgazione" / "metodo-report-verificati.md").exists()


PRESUPPOSTI = {
    "registro": (_ha_registro, "nessun registro dei brain: istanza sola"),
    "training": (_ha_training, "nessun training adottato: niente modello ne' oracolo"),
    "contenuto": (_ha_contenuto, "brain senza conoscenza: niente da misurare"),
    "corpus_data_science": (_ha_corpus_data_science,
                            "nessuna nota di data-science: le domande su quartili e outlier non hanno oggetto"),
    "report_verificati": (_ha_report_verificati, "nessun report verificato da cui estrarre il metodo"),
    "esperienza": (_ha_esperienza, "meno di 20 registrazioni: memoria non ancora messa alla prova"),
    "scrittura": (_ha_plugin_scrittura, "plugin scrittura non installato"),
}

# Chi presuppone cosa. Chiave: nome del file di test, oppure 'file::test' per i
# singoli. La granularita' fine serve dove un file mescola guardie universali e
# guardie che dipendono da un training — test_api ne e' l'esempio: l'autenticazione
# vale in ogni brain, il modello tipato no.
RICHIEDE = {
    "test_officina.py": "registro",
    "test_motore_unico.py": "registro",
    "test_esperienza.py::test_il_reasoner_legge_il_prior_che_viene_davvero_generato": "training",
    "test_esperienza.py::test_il_registro_cresce_ma_il_prior_no": "esperienza",
    "test_tools.py::test_hook_eseguibili_non_versionati": "registro",
    "test_frontmatter_coerenza.py::test_lo_strato_generato_e_riconosciuto": "training",
    "test_frontmatter_coerenza.py::test_gli_strati_generati_restano_intatti": "training",
    "test_atlas.py::test_i_nodi_connessi_stanno_piu_vicino_allasse": "contenuto",
    "test_atlas.py::test_la_provenienza_sale_di_uno_strato": "contenuto",
    "test_api.py::test_health_pubblico_e_ricco": "training",
    "test_api.py::test_auth_richiesta_e_constant_time_ok": "training",
    "test_api.py::test_alias_non_versionati": "training",
    "test_api.py::test_query_degrada_o_funziona": "contenuto",
    "test_api.py::test_oracle_deterministico_con_seed": "training",
    "test_api.py::test_oracle_hexagram_lookup_re_wen": "training",
    "test_api.py::test_rate_limiter_uses_client_host": "training",
    "test_api.py::test_search_trova_nel_contenuto": "corpus_data_science",
    # Questi interrogano il CONTENUTO del brain di riferimento. Il comportamento del
    # motore che verificano (ricerca, confidenza, diagnosi) e' coperto ovunque, su un
    # brain sintetico, da test_valutazione.py.
    "test_tools.py::test_ricerca_trova_il_contenuto_giusto": "corpus_data_science",
    "test_tools.py::test_ricerca_copre_le_note_grezze_di_metodo": "corpus_data_science",
    "test_tools.py::test_confidenza_alta_su_conoscenza_presente": "corpus_data_science",
    "test_tools.py::test_diagnosi_dichiara_cosa_misura": "corpus_data_science",
    "test_tools.py::test_memoria_annota_ancoraggi_consolidati": "esperienza",
    "test_tools.py::test_report_harvest_estrae_fonti_e_metodo": "report_verificati",
    "test_tools.py::test_report_harvest_nota_presente_e_dichiarata": "report_verificati",
    "test_tools.py::test_harvest_non_sovrascrive_il_lavoro_umano": "report_verificati",
    "test_api.py::test_search_filtro_area": "corpus_data_science",
    "test_api.py::test_le_tre_viste_sono_servite_e_protette": "contenuto",
    "test_api.py::test_health_dichiara_le_tre_viste": "contenuto",
    "test_api.py::test_health_segnala_una_vista_rimasta_indietro": "contenuto",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        file = pathlib.Path(str(item.fspath)).name
        chiave = RICHIEDE.get(f"{file}::{item.originalname or item.name}") or RICHIEDE.get(file)
        if not chiave:
            continue
        presente, motivo = PRESUPPOSTI[chiave]
        if not presente():
            item.add_marker(pytest.mark.skip(reason=f"presupposto '{chiave}' assente — {motivo}"))
