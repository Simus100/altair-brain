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
    .update-log { margin: 14px 0; padding: 14px 16px; border: 1px solid var(--border-color); border-left: 2px solid var(--color-secondary); border-radius: 10px; background: linear-gradient(135deg, rgba(6,182,212,.06), rgba(6,182,212,.015) 55%); }
    .ul-title { display: flex; align-items: center; gap: 8px; font-size: .7rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #a5b4fc; margin-bottom: 14px; }
    .ul-count { font-size: .62rem; font-weight: 800; color: var(--color-secondary); background: rgba(6,182,212,.12); border: 1px solid rgba(6,182,212,.3); border-radius: 999px; padding: 1px 8px; }
    .ul-item { position: relative; padding-left: 20px; margin-bottom: 16px; }
    .ul-item::before { content: ''; position: absolute; left: 0; top: 5px; width: 8px; height: 8px; border-radius: 50%; background: var(--color-secondary); box-shadow: 0 0 8px var(--color-secondary); }
    .ul-item::after { content: ''; position: absolute; left: 3.5px; top: 15px; bottom: -16px; width: 1px; background: linear-gradient(to bottom, var(--border-glow), var(--border-color)); }
    .ul-item:last-child::after { display: none; }
    .ul-item:last-child { margin-bottom: 2px; }
    .ul-item.latest::before { background: var(--color-gold); box-shadow: 0 0 10px var(--color-gold); animation: ul-pulse 2.2s ease-in-out infinite; }
    @keyframes ul-pulse { 0%,100% { box-shadow: 0 0 6px var(--color-gold); } 50% { box-shadow: 0 0 14px var(--color-gold), 0 0 22px rgba(251,191,36,.35); } }
    .ul-time { display: inline-flex; align-items: center; gap: 7px; font-size: .67rem; font-weight: 700; color: var(--color-secondary); font-variant-numeric: tabular-nums; letter-spacing: .04em; margin-bottom: 4px; }
    .ul-new { font-size: .56rem; font-weight: 900; letter-spacing: .12em; color: #0b0e18; background: var(--color-gold); border-radius: 999px; padding: 1.5px 7px; }
    .ul-item.latest .ul-time { color: var(--color-gold); }
    .ul-text { font-size: .83rem; color: var(--text-muted); line-height: 1.55; }
    .ul-item.latest .ul-text { color: var(--text-main); }
    .ul-empty { font-size: .8rem; color: var(--text-muted); font-style: italic; }
    .verdict-live { position: relative; margin: 0 0 24px 0; padding: 20px; border: 1px solid rgba(251,191,36,.4); border-radius: 12px; background: linear-gradient(160deg, rgba(251,191,36,.08), rgba(251,191,36,.02) 60%); overflow: hidden; }
    .verdict-live::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, var(--color-gold), transparent); opacity: .7; }
    .vl-badge { display:inline-flex; align-items:center; gap:7px; font-size:.62rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#fde68a; background:rgba(251,191,36,.12); border:1px solid rgba(251,191,36,.35); padding:4px 11px; border-radius:999px; margin-bottom:12px; }
    .vl-dot { width:7px; height:7px; border-radius:50%; background: var(--color-gold); animation: ul-pulse 2.2s ease-in-out infinite; }
    .vl-current { font-size: .93rem; color: var(--text-main); line-height: 1.7; }
    .concl-badge { display:inline-flex; align-items:center; gap:7px; font-size:.62rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#99f6e4; background:rgba(6,182,212,.10); border:1px solid rgba(6,182,212,.35); padding:4px 11px; border-radius:999px; margin-bottom:12px; }
    .live-pill { display:inline-flex; align-items:center; gap:7px; vertical-align:middle; margin-left:14px; font-size:.6rem; font-weight:900; letter-spacing:.16em; text-transform:uppercase; color:#fda4af; background:rgba(244,63,94,.12); border:1px solid rgba(244,63,94,.45); border-radius:999px; padding:4px 12px; }
    .live-dot { width:7px; height:7px; border-radius:50%; background: var(--color-rose); animation: live-pulse 1.6s ease-in-out infinite; }
    @keyframes live-pulse { 0%,100% { box-shadow: 0 0 4px var(--color-rose); opacity: 1; } 50% { box-shadow: 0 0 12px var(--color-rose), 0 0 20px rgba(244,63,94,.4); opacity: .6; } }
    .live-date { display:inline-block; vertical-align:middle; margin-left:10px; font-size:.62rem; font-weight:700; letter-spacing:.05em; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    /* metadati editoriali per voce di timeline: fonte, autore, confidenza */
    .ul-meta { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-top:5px; font-size:.62rem; color:#64748b; }
    .ul-meta .m { display:inline-flex; align-items:center; gap:4px; }
    .ul-conf { font-weight:800; letter-spacing:.06em; text-transform:uppercase; border-radius:999px; padding:1px 8px; font-size:.56rem; }
    .ul-conf.alta   { color:#86efac; background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.35); }
    .ul-conf.media  { color:#fde68a; background:rgba(251,191,36,.10); border:1px solid rgba(251,191,36,.3); }
    .ul-conf.bassa  { color:#fda4af; background:rgba(244,63,94,.10); border:1px solid rgba(244,63,94,.3); }
    /* cast oracolare verificabile nel box del responso */
    .vl-cast { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-top:14px; padding:10px 14px; border:1px dashed rgba(251,191,36,.35); border-radius:8px; font-size:.74rem; color:var(--text-muted); }
    .vl-cast .hex { font-size:1.2rem; color:var(--color-gold); line-height:1; }
    .vl-cast strong { color:var(--text-main); font-weight:700; }
    .vl-motiv { margin-top:10px; font-size:.78rem; color:var(--text-muted); font-style:italic; line-height:1.55; }
    .vl-lines { margin-top:12px; }
    .vl-line { font-size:.8rem; color:var(--text-main); line-height:1.5; padding:6px 10px; margin-bottom:6px; border-left:2px solid var(--color-gold); background:rgba(251,191,36,.05); border-radius:0 6px 6px 0; }
    .vl-line-n { font-weight:800; color:var(--color-gold); font-size:.68rem; letter-spacing:.05em; }
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
    function meta(u) {
      /* riga dei metadati editoriali: fonte citata, firma, confidenza */
      var parts = [];
      if (u.fonte) parts.push('<span class="m">\\uD83D\\uDCCE ' + u.fonte + '</span>');
      if (u.autore) parts.push('<span class="m">\\u270D\\uFE0E ' + u.autore + '</span>');
      if (u.confidenza) parts.push('<span class="ul-conf ' + u.confidenza + '">conf. ' + u.confidenza + '</span>');
      return parts.length ? '<div class="ul-meta">' + parts.join('') + '</div>' : '';
    }
    function timeline(items) {
      if (!items || !items.length) return '<div class="ul-empty">Nessun aggiornamento registrato.</div>';
      return items.slice().reverse().map(function (u, i) {
        var latest = i === 0;
        return '<div class="ul-item' + (latest ? ' latest' : '') + '">' +
               '<div class="ul-time">' + fmt(u.ts) + (latest ? ' <span class="ul-new">ULTIMO</span>' : '') + '</div>' +
               '<div class="ul-text">' + u.testo + '</div>' + meta(u) + '</div>';
      }).join('');
    }
    function title(label, items) {
      var n = (items || []).length;
      return '<div class="ul-title">\\uD83D\\uDD52 ' + label + (n ? ' <span class="ul-count">' + n + '</span>' : '') + '</div>';
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
      el.innerHTML = title('Cronologia Aggiornamenti', items) + timeline(items);
    };
    if (typeof window.selectNode === 'function') {
      var _orig = window.selectNode;
      window.selectNode = function (id) { _orig(id); try { renderNodeHistory(id); } catch (e) {} };
    }

    /* --- TITOLO: badge LIVE + ultima data di aggiornamento (dal database) --- */
    function latestTs() {
      var all = [];
      if (DB.verdetto && DB.verdetto.storia) all = all.concat(DB.verdetto.storia);
      if (DB.conclusioni && DB.conclusioni.storia) all = all.concat(DB.conclusioni.storia);
      if (DB.nodi) Object.keys(DB.nodi).forEach(function (k) { all = all.concat(DB.nodi[k]); });
      var ts = DB.aggiornato_il || '';
      all.forEach(function (u) { if (u.ts > ts) ts = u.ts; });
      return ts;
    }
    function renderLiveTitle() {
      var h1 = document.querySelector('header h1'); if (!h1) return;
      if (document.getElementById('live-pill')) return;
      var pill = document.createElement('span');
      pill.id = 'live-pill'; pill.className = 'live-pill';
      pill.innerHTML = '<span class="live-dot"></span>LIVE';
      h1.appendChild(pill);
      var dt = document.createElement('span');
      dt.className = 'live-date';
      dt.textContent = 'agg. ' + fmt(latestTs());
      h1.appendChild(dt);
    }

    /* --- FRESCHEZZA 3D: beacon lampeggiante sui nodi con update recenti ---
       Un nodo e "fresco" se il suo ultimo aggiornamento cade entro FRESH_DAYS
       dall'ultimo aggiornamento globale del report (freschezza relativa: regge
       anche per scenari con date proprie). Patcha le label HUD dell'array
       globale `nodes` del template 3D; il render loop le ridisegna a ogni frame,
       quindi il toggle periodico del simbolo produce il lampeggio. */
    function markFreshNodes() {
      try {
        if (typeof nodes === 'undefined' || !DB.nodi) return;
        var FRESH_DAYS = 7;
        var last = new Date(latestTs()).getTime();
        var fresh = {};                             /* id -> numero update recenti */
        Object.keys(DB.nodi).forEach(function (id) {
          var n = DB.nodi[id].filter(function (u) {
            return last - new Date(u.ts).getTime() <= FRESH_DAYS * 86400000;
          }).length;
          if (n > 0) fresh[id] = n;
        });
        var base = {};                              /* label originali, per il toggle */
        nodes.forEach(function (n) { base[n.id] = n.label; });
        var on = true;
        function paint() {
          nodes.forEach(function (n) {
            if (fresh[n.id]) n.label = base[n.id] + (on ? ' \\u25C9' : ' \\u25CB') + fresh[n.id];
          });
          on = !on;
        }
        paint();
        setInterval(paint, 900);
      } catch (e) { /* il template 3D non espone `nodes`: nessun beacon, nessun danno */ }
    }

    /* --- CONCLUSIONI: responso SOPRA + testo pilotato dal database --- */
    function renderLiving() {
      renderLiveTitle();
      markFreshNodes();
      var host = document.getElementById('box-conclusions'); if (!host) return;
      var conclText = host.querySelector('.conclusions-text');

      /* 1. Responso in aggiornamento — ordine canonico: SOTTO le conclusioni,
         in coda al box (le Conclusioni aggiornate aprono, il Responso chiude) */
      var v = DB.verdetto || {};
      var vbox = document.getElementById('verdict-live');
      if (!vbox) {
        vbox = document.createElement('div'); vbox.id = 'verdict-live'; vbox.className = 'verdict-live';
        vbox.style.marginTop = '22px';
        host.appendChild(vbox);
      }
      /* ATTRIBUZIONE ORACOLARE: l'esagramma non e estratto a caso, e ATTRIBUITO
         decisionalmente all'argomento; le linee mobili marcano i vettori in
         mutamento e il loro testo e il consiglio del cambiamento. */
      var castHtml = '';
      if (v.cast) {
        var c2 = v.cast;
        var mob = (c2.linee_mobili || []).join('\\u00AA, ') + (c2.linee_mobili && c2.linee_mobili.length ? '\\u00AA' : '');
        castHtml = '<div class="vl-cast">' +
          '<span class="hex">' + (c2.primario.simbolo || '') + '</span>' +
          '<span><strong>' + c2.primario.id + ' ' + c2.primario.nome + '</strong> \\u2192 </span>' +
          '<span class="hex">' + (c2.secondario ? c2.secondario.simbolo : '') + '</span>' +
          '<span><strong>' + (c2.secondario ? c2.secondario.id + ' ' + c2.secondario.nome : '') + '</strong></span>' +
          (mob ? '<span>\\u00B7 linee mobili: ' + mob + '</span>' : '') +
          '<span>\\u00B7 attribuzione decisionale AION_Oracle</span></div>';
        if (c2.motivazione) {
          castHtml += '<div class="vl-motiv">' + c2.motivazione + '</div>';
        }
        if (c2.consiglio_linee && c2.consiglio_linee.length) {
          /* il cuore del metodo: le linee mobili come consiglio operativo */
          castHtml += '<div class="vl-lines"><div class="ul-title" style="margin-bottom:8px;">\\u268D Il consiglio delle linee mobili</div>' +
            c2.consiglio_linee.map(function (l) {
              return '<div class="vl-line"><span class="vl-line-n">' + l.linea + '\\u00AA' +
                     (l.vettore ? ' \\u00B7 ' + l.vettore : '') + '</span> ' + l.testo + '</div>';
            }).join('') + '</div>';
        }
      }
      vbox.innerHTML = '<div class="vl-badge"><span class="vl-dot"></span>\\u4DEA Responso in aggiornamento \\u00B7 ' + fmt((v.storia && v.storia.length ? v.storia[v.storia.length-1].ts : DB.aggiornato_il)) + '</div>' +
        '<div class="vl-current">' + (v.corrente || '') + '</div>' + castHtml +
        '<div style="margin-top:18px;">' + title('Evoluzione del Responso', v.storia) + timeline(v.storia) + '</div>';

      /* 2. Conclusioni Strategiche pilotate dal database */
      var c = DB.conclusioni;
      if (c && conclText) {
        conclText.innerHTML =
          '<div class="concl-badge">\\uD83D\\uDD01 Conclusioni aggiornate il ' + fmt(c.aggiornato_il || DB.aggiornato_il) + '</div>' +
          '<div>' + (c.corrente || '') + '</div>' +
          '<div class="update-log" style="margin-top:18px;">' + title('Evoluzione delle Conclusioni', c.storia) + timeline(c.storia) + '</div>';
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
# titolo del living report: via il prefisso, resta il nome del caso
html = html.replace("Cervello Geopolitico 3D: ", "", 1)
html = html.replace("</style>", CSS + "\n  </style>", 1)
html = html.replace("</body>", feature + "\n</body>", 1)

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)
print(f"living report generato: {os.path.relpath(OUT, ROOT)} ({len(html)} byte)")
