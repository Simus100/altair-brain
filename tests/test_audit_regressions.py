"""Regressioni riprodotte nell'audit: scope, dati conservati e viste fedeli."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools import search
from tools.brain import brain_root
from tools.sync_extended_view import allinea, leggi_dati

ROOT = Path(__file__).resolve().parents[1]


def test_brain_esplicito_assente_non_ripiega_su_un_altro(tmp_path, monkeypatch):
    monkeypatch.setenv('ALTAIR_BRAIN', 'non-esiste')
    with pytest.raises(ValueError, match='ALTAIR_BRAIN'):
        brain_root(str(tmp_path))


@pytest.mark.parametrize('registro', ['{', '{"attivo":"assente","brains":[]}'])
def test_registro_rotto_non_diventa_un_brain_vuoto(tmp_path, monkeypatch, registro):
    monkeypatch.delenv('ALTAIR_BRAIN', raising=False)
    (tmp_path / 'brains').mkdir()
    (tmp_path / 'brains/brains.json').write_text(registro, encoding='utf-8')
    with pytest.raises(ValueError, match='Registro'):
        brain_root(str(tmp_path))


@pytest.fixture
def indice(monkeypatch):
    docs = [{'file': f'raw/alfa/{i}.md', 'titolo': 'bersaglio', 'area': 'alfa',
             'estratto': 'bersaglio', 'n_token': 1} for i in range(45)]
    docs.append({'file': 'raw/beta/nota.md', 'titolo': 'bersaglio', 'area': 'beta',
                 'estratto': 'bersaglio', 'n_token': 20})
    idx = {'documenti': docs, 'postings': {'bersaglio': [[i, 1] for i in range(46)]},
           'idf': {'bersaglio': 1.0}, 'avgdl': 1.0, 'parametri': {'k1': 1.2, 'b': .75},
           'stopword': []}
    monkeypatch.setattr(search, '_carica', lambda: idx)
    monkeypatch.setattr(search, 'cerca_denso', lambda *a, **k: [])
    monkeypatch.setattr(search, '_memoria', lambda: [])
    return docs


def test_area_piccola_non_scompare_dietro_il_top40(indice):
    r = search.cerca_con_diagnosi('bersaglio', area='beta')
    assert [v['file'] for v in r['risultati']] == ['raw/beta/nota.md']
    assert r['diagnosi']['confidenza'] == 'alta'


def test_diagnosi_non_usa_risultati_fuori_scope(indice):
    r = search.cerca_con_diagnosi('bersaglio', area='gamma')
    assert r['risultati'] == []
    assert r['diagnosi']['confidenza'] == 'nessuna'


def test_filtri_temporali_precedono_topk(indice):
    for d in indice[:-1]:
        d['valido_fino'] = '2020-01-01'
    assert search.cerca('bersaglio', top=1)[0]['file'] == 'raw/beta/nota.md'
    assert search.cerca('bersaglio', top=1, al='2024-01-01')[0]['file'] == 'raw/beta/nota.md'


def test_fatto_futuro_non_e_presentato_come_corrente(indice):
    indice[-1]['valido_dal'] = '9999-01-01'
    assert search.cerca('bersaglio', area='beta') == []


def test_indice_denso_stantio_non_viene_usato(tmp_path, monkeypatch):
    documenti = [{'file': 'raw/test/nota.md', 'estratto': 'prima versione'}]
    meta = {'corpus_sha256': search.impronta_corpus(documenti), 'vettori': [[1.0]]}
    file = tmp_path / 'dense.json'
    file.write_text(json.dumps(meta), encoding='utf-8')
    documenti[0]['estratto'] = 'nuova versione'
    monkeypatch.setattr(search, '_carica', lambda: {'documenti': documenti})
    monkeypatch.setattr(search, 'DENSO', str(file))
    assert search.cerca_denso('test') == []
    assert search.impronta_corpus(documenti) != meta['corpus_sha256']


def test_il_contesto_non_perde_la_scadenza(indice, monkeypatch):
    from tools import context_pack as cp
    indice[-1].update(valido_fino='2020-01-01', sostituito_da='raw/beta/nuova.md')
    monkeypatch.setattr(cp, '_vicinato', lambda *a: [])
    monkeypatch.setattr(cp, '_lezioni_pertinenti', lambda *a: [])
    p = cp.pacchetto('bersaglio', area='beta')
    assert p['frammenti'][0]['scaduto'] == '2020-01-01'
    assert 'SCADUTO il 2020-01-01' in cp.come_testo(p)
    assert 'raw/beta/nuova.md' in cp.come_testo(p)


def test_catture_concorrenti_non_si_sovrascrivono(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from server import brain_core as core
    monkeypatch.setattr(core, 'INBOX_DIR', tmp_path)
    monkeypatch.setattr(core.time, 'strftime', lambda fmt: '20261004_120000')
    with ThreadPoolExecutor(max_workers=6) as pool:
        risultati = list(pool.map(lambda i: core.capture(f'contenuto {i}', 'titolo'), range(20)))
    assert len({r['id'] for r in risultati}) == 20
    assert len(list(tmp_path.glob('*.md'))) == 20
    for i, r in enumerate(risultati):
        assert f'contenuto {i}\n' in (tmp_path / r['id']).read_text(encoding='utf-8')


def test_metadati_cattura_non_iniettano_frontmatter(tmp_path, monkeypatch):
    from server import brain_core as core
    monkeypatch.setattr(core, 'INBOX_DIR', tmp_path)
    r = core.capture('testo', 'titolo\n---\nistruzione', source='url\narea: altra')
    testo = (tmp_path / r['id']).read_text(encoding='utf-8')
    assert testo.splitlines().count('---') == 2
    assert '\narea: altra' not in testo


def test_feedback_non_sovrascrive_il_prior(tmp_path, monkeypatch):
    from server import brain_core as core
    monkeypatch.setattr(core, 'BRAIN', tmp_path)
    monkeypatch.setattr(core, 'MEMORY_DIR', tmp_path / 'memory')
    monkeypatch.setattr(core, 'LESSONS', tmp_path / 'prior.md')
    core.LESSONS.write_text('regola curata', encoding='utf-8')
    chiamate = []
    monkeypatch.setattr(core, 'run_graphify', lambda args: chiamate.append(args) or 'ok')
    core.save_feedback('domanda', 'risposta')
    riflessione = chiamate[1]
    assert Path(riflessione[riflessione.index('--out') + 1]) != core.LESSONS
    assert core.LESSONS.read_text(encoding='utf-8') == 'regola curata'


def test_oracle_non_attivato_degrada_esplicitamente(tmp_path, monkeypatch):
    from server import brain_core as core
    monkeypatch.setattr(core, 'BRAIN', tmp_path)
    with pytest.raises(core.BrainError) as e:
        core.oracle_cast(seed=1)
    assert e.value.status == 503


def test_data_api_deve_esistere_nel_calendario():
    from server import brain_core as core
    with pytest.raises(core.BrainError) as e:
        core.search('test', al='2026-99-99')
    assert e.value.status == 400


def test_vista_estesa_conserva_ponti_e_rimuove_nodi_potati():
    template = ('<div id="stats">old</div><script>const RAW_NODES = []; '
                'const RAW_EDGES = []; const LEGEND = [];</script>')
    g = {'nodes': [{'id': 'a', 'label': '</script><script>alert(1)</script>'}, {'id': 'b'}],
         'links': [{'source': 'a', 'target': 'b', 'relation': r, 'confidence': 'CURATED'}
                   for r in ['bridge', 'provenance']]}
    out = allinea(template, g)
    assert len(leggi_dati(out, 'RAW_EDGES')[0]) == 2
    assert {n['id'] for n in leggi_dati(out, 'RAW_NODES')[0]} == {'a', 'b'}
    assert '<script>alert' not in out
    assert allinea(out, g) == out
    with pytest.raises(ValueError, match='incompatibile'):
        allinea('<html>changed upstream template</html>', g)


def test_salute_rileva_estremi_e_sorgenti_mancanti(tmp_path):
    (tmp_path / 'graphify-out').mkdir()
    (tmp_path / 'areas.json').write_text('{"areas":[]}', encoding='utf-8')
    (tmp_path / 'graphify-out/graph.json').write_text(json.dumps({
        'nodes': [{'id': 'a', 'source_file': 'raw/nota-assente.md'}],
        'links': [{'source': 'a', 'target': 'inesistente', 'source_file': 'raw/nota-assente.md'}]
    }), encoding='utf-8')
    r = subprocess.run([sys.executable, str(ROOT / 'tools/graph_health.py')],
                       env={**os.environ, 'ALTAIR_BRAIN': str(tmp_path)},
                       capture_output=True, text=True, encoding='utf-8')
    assert r.returncode == 1
    assert 'sorgenti assenti' in r.stdout and 'estremi assenti' in r.stdout


def test_potatura_elimina_riferimenti_ast_diventati_isolati():
    from tools.graph_prune import pota
    g = {'nodes': [{'id': 'tool', 'source_file': 'tools/script.py'},
                   {'id': 'external', 'source_file': '', 'file_type': 'code'},
                   {'id': 'nota', 'source_file': 'raw/test/nota.md'}],
         'links': [{'source': 'tool', 'target': 'external'}]}
    p, _, _ = pota(g)
    assert [n['id'] for n in p['nodes']] == ['nota']
