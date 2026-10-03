# -*- coding: utf-8 -*-
"""Allinea i dati della vista graphify al grafo DOPO potatura e ponti.

Conserva interfaccia e layout di graphify 0.9.2. Il formato delle tre costanti
JavaScript e' verificato: se upstream lo cambia, interrompiamo la pipeline invece
di pubblicare una vista vecchia. Nessuna chiamata a modelli o riclassificazione.
"""
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.brain import BRAIN  # noqa: E402


def leggi_dati(testo, nome):
    marker = re.search(r"const " + nome + r"\s*=\s*", testo)
    if not marker:
        raise ValueError(f"Vista graphify incompatibile: manca {nome}")
    dati, fine = json.JSONDecoder().raw_decode(testo[marker.end():])
    return dati, marker.end(), marker.end() + fine


def allinea(testo, grafo):
    vecchi = {n['id']: n for n in leggi_dati(testo, 'RAW_NODES')[0]}
    legenda = {n['cid']: n for n in leggi_dati(testo, 'LEGEND')[0]}
    ids = {n['id'] for n in grafo['nodes']}
    grado = Counter()
    archi = []
    for e in grafo['links']:
        a, b = e['source'], e['target']
        if a not in ids or b not in ids:
            raise ValueError('Grafo con estremi mancanti: impossibile generare la vista')
        grado.update((a, b))
        relazione, conf = e.get('relation', ''), e.get('confidence', '')
        archi.append({'from': a, 'to': b, 'label': relazione,
                      'title': html.escape(f"{relazione} [{conf}]"),
                      'confidence': conf, 'dashes': conf == 'INFERRED',
                      'width': 2, 'color': {'opacity': 0.7}})
    nodi, comunita = [], Counter()
    for n in grafo['nodes']:
        voce = dict(vecchi.get(n['id'], {}))
        cid = n.get('community', 0)
        colore = legenda.get(cid, {}).get('color', '#4E79A7')
        label = n.get('label') or n['id']
        voce.update(id=n['id'], label=label, title=html.escape(label),
                    community=cid, source_file=n.get('source_file', ''),
                    file_type=n.get('file_type', ''), degree=grado[n['id']],
                    size=min(35, 12 + grado[n['id']] * 0.1))
        voce.setdefault('color', {'background': colore, 'border': colore})
        voce.setdefault('font', {'size': 0, 'color': '#ffffff'})
        voce.setdefault('community_name', legenda.get(cid, {}).get('label', f'Community {cid}'))
        nodi.append(voce)
        comunita[cid] += 1
    gruppi = [dict(legenda.get(cid, {'cid': cid, 'color': '#4E79A7',
                                    'label': f'Community {cid}'}), count=n)
              for cid, n in sorted(comunita.items())]
    for nome, dati in [('RAW_NODES', nodi), ('RAW_EDGES', archi), ('LEGEND', gruppi)]:
        _, inizio, fine = leggi_dati(testo, nome)
        # Una label e' dato, mai markup eseguibile (anche se contiene </script>).
        encoded = json.dumps(dati, ensure_ascii=True).replace('<', '\\u003c')
        testo = testo[:inizio] + encoded + testo[fine:]
    testo, n = re.subn(r'(<div id="stats">).*?(</div>)',
                      lambda m: m[1] + f'{len(nodi)} nodes &middot; {len(archi)} edges '
                      f'&middot; {len(gruppi)} communities' + m[2], testo, count=1)
    if n != 1:
        raise ValueError('Vista graphify incompatibile: statistiche assenti')
    return testo


def main():
    base = Path(BRAIN) / 'graphify-out'
    file = base / 'graph.html'
    grafo = json.loads((base / 'graph.json').read_text(encoding='utf-8'))
    testo = allinea(file.read_text(encoding='utf-8'), grafo)
    file.write_text(testo, encoding='utf-8', newline='\n')
    print(f"Vista estesa allineata: {len(grafo['nodes'])} nodi, {len(grafo['links'])} archi")


if __name__ == '__main__':
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    main()
