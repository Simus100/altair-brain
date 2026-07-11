# -*- coding: utf-8 -*-
"""
altair-brain — costruisce il prototipo 'living report' (report che si aggiorna).

Legge il report originale (reports/<nome>.html) e il database degli aggiornamenti
(reports/data/<nome>.updates.json) e produce reports/<nome>-prototype.html con:
- nei NODI: 'Cronologia Aggiornamenti' IN CIMA alla console (sopra l'analisi);
- 'Responso in aggiornamento' SOPRA le Conclusioni Strategiche;
- Conclusioni Strategiche PILOTATE DAL DATABASE (testo corrente + data + evoluzione).

Il JSON e la fonte di verita; l'HTML e generato. Deterministico, nessuna API.
Uso:  python tools/report_build.py [--report altair-brain-iran-2026]
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("--report", default="altair-brain-iran-2026")
a = ap.parse_args()

SRC = os.path.join(ROOT, "reports", f"{a.report}.html")
DB = os.path.join(ROOT, "reports", "data", f"{a.report}.updates.json")
OUT = os.path.join(ROOT, "reports", f"{a.report}-prototype.html")

for p in (SRC, DB):
    if not os.path.exists(p):
        sys.exit(f"file mancante: {p}")

html = open(SRC, encoding="utf-8").read()
db_json = open(DB, encoding="utf-8").read().strip()
json.loads(db_json)  # valida

CSS = """
    /* --- LIVING REPORT: timeline aggiornamenti + conclusioni vive --- */
    .update-log { margin: 14px 0; padding: 12px 14px; border: 1px solid var(--border-color); border-radius: 10px; background: rgba(6, 182, 212, 0.04); }
    .ul-title { font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #a5b4fc; margin-bottom: 12px; }
    .ul-item { position: relative; padding-left: 18px; margin-bottom: 14px; }
    .ul-item::before { content: ''; position: absolute; left: 0; top: 5px; width: 8px; height: 8px; border-radius: 50%; background: var(--color-secondary); box-shadow: 0 0 8px var(--color-secondary); }
    .ul-item::after { content: ''; position: absolute; left: 3.5px; top: 14px; bottom: -14px; width: 1px; background: var(--border-color); }
    .ul-item:last-child::after { display: none; }
    .ul-item:last-child { margin-bottom: 2px; }
    .ul-time { font-size: .68rem; font-weight: 700; color: var(--color-secondary); font-variant-numeric: tabular-nums; margin-bottom: 3px; }
    .ul-text { font-size: .82rem; color: var(--text-muted); line-height: 1.5; }
    .ul-empty { font-size: .8rem; color: var(--text-muted); font-style: italic; }
    .verdict-live { margin: 0 0 22px 0; padding: 18px; border: 1px solid rgba(251,191,36,.4); border-radius: 12px; background: rgba(251, 191, 36, 0.05); }
    .vl-badge { display:inline-block; font-size:.62rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:#fde68a; background:rgba(251,191,36,.12); border:1px solid rgba(251,191,36,.35); padding:3px 9px; border-radius:3px; margin-bottom:10px; }
    .vl-current { font-size: .92rem; color: var(--text-main); line-height: 1.65; }
    .concl-badge { display:inline-block; font-size:.62rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:#99f6e4; background:rgba(6,182,212,.10); border:1px solid rgba(6,182,212,.35); padding:3px 9px; border-radius:3px; margin-bottom:12px; }
"""

FEATURE = """
  <script type="application/json" id="updates-db">__DB__</script>
  <script>
  (function () {
    var DB = {};
    try { DB = JSON.parse(document.getElementById('updates-db').textContent); } catch (e) { console.warn('updates-db non valido', e); }
    function fmt(ts) {
      var d = new Date(ts); if (isNaN(d)) return ts;
      var p = function (n) { return String(n).padStart(2, '0'); };
      return p(d.getDate()) + '/' + p(d.getMonth() + 1) + '/' + d.getFullYear() + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
    }
    function timeline(items) {
      if (!items || !items.length) return '<div class="ul-empty">Nessun aggiornamento registrato.</div>';
      return items.slice().reverse().map(function (u) {
        return '<div class="ul-item"><div class="ul-time">' + fmt(u.ts) + '</div><div class="ul-text">' + u.testo + '</div></div>';
      }).join('');
    }

    /* --- NODI: cronologia IN CIMA alla console (sopra l'analisi) --- */
    window.renderNodeHistory = function (id) {
      var card = document.getElementById('details-card');
      var body = document.getElementById('node-body-text');
      if (!card || !body) return;
      var el = document.getElementById('oracle-history');
      if (!el) { el = document.createElement('div'); el.id = 'oracle-history'; el.className = 'update-log'; }
      body.parentNode.insertBefore(el, body);   // sopra il testo di analisi
      var items = (DB.nodi && DB.nodi[id]) || [];
      el.style.display = 'block';
      el.innerHTML = '<div class="ul-title">\\uD83D\\uDD52 Cronologia Aggiornamenti</div>' + timeline(items);
    };
    if (typeof window.selectNode === 'function') {
      var _orig = window.selectNode;
      window.selectNode = function (id) { _orig(id); try { renderNodeHistory(id); } catch (e) {} };
    }

    /* --- CONCLUSIONI: responso SOPRA + testo pilotato dal database --- */
    function renderLiving() {
      var host = document.getElementById('box-conclusions'); if (!host) return;
      var conclText = host.querySelector('.conclusions-text');

      /* 1. Responso in aggiornamento, SOPRA le conclusioni */
      var v = DB.verdetto || {};
      var vbox = document.getElementById('verdict-live');
      if (!vbox) {
        vbox = document.createElement('div'); vbox.id = 'verdict-live'; vbox.className = 'verdict-live';
        if (conclText) host.insertBefore(vbox, conclText); else host.appendChild(vbox);
      }
      vbox.innerHTML = '<div class="vl-badge">\\u26A1 Responso in aggiornamento \\u00B7 ' + fmt((v.storia && v.storia.length ? v.storia[v.storia.length-1].ts : DB.aggiornato_il)) + '</div>' +
        '<div class="vl-current">' + (v.corrente || '') + '</div>' +
        '<div class="ul-title" style="margin-top:16px;">\\uD83D\\uDD52 Evoluzione del Responso</div>' + timeline(v.storia);

      /* 2. Conclusioni Strategiche pilotate dal database */
      var c = DB.conclusioni;
      if (c && conclText) {
        conclText.innerHTML =
          '<div class="concl-badge">\\uD83D\\uDD01 Conclusioni aggiornate il ' + fmt(c.aggiornato_il || DB.aggiornato_il) + '</div>' +
          '<div>' + (c.corrente || '') + '</div>' +
          '<div class="update-log" style="margin-top:18px;"><div class="ul-title">\\uD83D\\uDD52 Evoluzione delle Conclusioni</div>' + timeline(c.storia) + '</div>';
      }
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', renderLiving);
    else renderLiving();
  })();
  </script>
"""

feature = FEATURE.replace("__DB__", db_json)

if "</style>" not in html or "</body>" not in html:
    sys.exit("HTML sorgente senza </style> o </body>: impossibile iniettare.")
html = html.replace("</style>", CSS + "\n  </style>", 1)
html = html.replace("</body>", feature + "\n</body>", 1)

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)
print(f"living report generato: {os.path.relpath(OUT, ROOT)} ({len(html)} byte)")
