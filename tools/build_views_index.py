# -*- coding: utf-8 -*-
"""
altair-brain — la PORTA di graphify-out/: una pagina che apre le tre viste.

PERCHE ESISTE. Chi apre la cartella trova tre file .html e nessun indizio su quale
serva. Le viste rispondono a domande diverse e usare quella sbagliata e' il modo
piu' comune di perderci tempo: la porta lo dice prima del click, non dopo.

Deterministica: i numeri vengono dal grafo, non dall'orologio ne' dal peso dei
file (che dipende dalla versione di graphify installata). Stesso grafo, stessa
pagina — cosi la CI puo' verificarne la coerenza come per le altre viste.

Uso:  python tools/build_views_index.py     -> graphify-out/index.html
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools import build_atlas_view as atlante          # noqa: E402  (riuso, non duplico)

USCITA = os.path.join(ROOT, "graphify-out", "index.html")


def numeri():
    """Cosa contiene ciascuna vista, contato sul grafo vero."""
    with open(atlante.GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    dati = atlante.costruisci()

    compatta = "—"
    percorso = os.path.join(ROOT, "graphify-out", "graph-compact.json")
    if os.path.exists(percorso):
        with open(percorso, encoding="utf-8") as f:
            c = json.load(f)
        compatta = f"{len(c.get('nodes', []))} nodi di processo"

    return {
        "commit": (g.get("built_at_commit") or "?")[:7],
        "estesa": f"{len(g.get('nodes', []))} nodi · {len(g.get('links', []))} relazioni",
        "compatta": compatta,
        "atlante": f"{len(dati['nodi'])} file · {len(dati['archi'])} relazioni",
        "aree": dati["conta"],
    }


VISTE = [
    {"file": "graph-atlas.html", "nome": "Atlante 3D", "chiave": "atlante",
     "colore": "#22d3ee", "serve": "navigare e orientarsi",
     "testo": "Uno spazio dove la posizione significa: l'altezza è lo strato del "
              "processo, lo spicchio è la macroarea, la distanza dall'asse è quanto "
              "un file è connesso. È la vista da aprire quando devi entrare in "
              "un'area che non conosci.",
     "come": "doppio click vola su un nodo · L isola il vicinato a 2 passi · "
             "[ ] scorrono i vicini · Backspace torna indietro"},
    {"file": "graph-compact.html", "nome": "Vista compatta", "chiave": "compatta",
     "colore": "#a855f7", "serve": "spiegare il sistema",
     "testo": "Il brain ridotto al suo processo a cinque fasi — sorgenti, modello, "
              "motore, skill, feedback — con l'anello di ritorno. Collassa il rumore: "
              "i 64 esagrammi diventano un nodo solo.",
     "come": "si legge in un minuto, non si esplora"},
    {"file": "graph.html", "nome": "Vista estesa", "chiave": "estesa",
     "colore": "#f59e0b", "serve": "vedere tutto",
     "testo": "Ogni nodo, nessuna riduzione: anche i titoli interni di ogni file. "
              "Serve quando cerchi qualcosa che le altre due hanno collassato. "
              "La posizione qui non significa niente: è l'equilibrio di una "
              "simulazione fisica.",
     "come": "pesante da caricare, lenta da percorrere"},
]


def html(n):
    schede = "\n".join(f"""
    <a class="vista" href="{v['file']}" style="--tinta:{v['colore']}">
      <div class="riga-alta">
        <span class="serve">{v['serve']}</span>
        <span class="conto">{n[v['chiave']]}</span>
      </div>
      <h2>{v['nome']}</h2>
      <p>{v['testo']}</p>
      <p class="come">{v['come']}</p>
      <span class="file">{v['file']}</span>
    </a>""" for v in VISTE)

    aree = " · ".join(f"<b>{a}</b> {q}" for a, q in
                      sorted(n["aree"].items(), key=lambda x: -x[1]))

    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Altair Brain — le tre viste del grafo</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#000;color:#e2e8f0;
  font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  padding:clamp(24px,6vw,72px);display:flex;justify-content:center}}
.foglio{{width:100%;max-width:920px;display:flex;flex-direction:column;gap:30px}}
header h1{{font-size:clamp(23px,3.4vw,31px);font-weight:700;letter-spacing:-.015em;text-wrap:balance}}
header p{{color:#94a3b8;margin-top:10px;max-width:62ch}}
header b{{color:#cbd5e1;font-weight:600}}
.viste{{display:flex;flex-direction:column;gap:14px}}
.vista{{display:block;text-decoration:none;color:inherit;padding:20px 22px;border-radius:14px;
  background:rgba(14,14,17,.9);border:1px solid rgba(148,163,184,.22);
  border-left:3px solid var(--tinta);transition:border-color .16s,transform .16s}}
.vista:hover{{border-color:var(--tinta);transform:translateX(3px)}}
.vista:focus-visible{{border-color:var(--tinta);outline:2px solid var(--tinta);outline-offset:3px}}
.riga-alta{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.serve{{font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--tinta);font-weight:700}}
.conto{{margin-left:auto;font-size:11px;color:#64748b;
  font-family:ui-monospace,SFMono-Regular,monospace;font-variant-numeric:tabular-nums}}
.vista h2{{font-size:19px;font-weight:700;margin:7px 0 8px}}
.vista p{{color:#94a3b8;font-size:13.5px;max-width:66ch}}
.come{{color:#64748b !important;font-size:12px !important;margin-top:9px !important}}
.file{{display:inline-block;margin-top:12px;font-size:11px;color:#475569;
  font-family:ui-monospace,SFMono-Regular,monospace}}
footer{{border-top:1px solid rgba(148,163,184,.14);padding-top:18px;color:#64748b;font-size:12px}}
footer code{{background:rgba(148,163,184,.12);border-radius:4px;padding:2px 7px;
  font-family:ui-monospace,SFMono-Regular,monospace;color:#cbd5e1}}
footer .aree{{margin-top:10px;line-height:1.9}}
footer b{{color:#94a3b8;font-weight:600}}
@media(prefers-reduced-motion:reduce){{.vista{{transition:none}}}}
</style></head><body>
<div class="foglio">
  <header>
    <h1>Le tre viste del grafo</h1>
    <p>Sono tre risposte a <b>tre domande diverse</b>. Aprire quella sbagliata per la
       domanda che hai è il modo più comune di perderci tempo — qui sta scritto
       prima del click.</p>
  </header>
  <div class="viste">{schede}
  </div>
  <footer>
    Generate da <code>python tools/rebuild_all.py</code> · grafo <code>{n['commit']}</code>
    <div class="aree">{aree}</div>
  </footer>
</div>
</body></html>
"""


def main():
    if not os.path.exists(atlante.GRAFO):
        sys.exit("graphify-out/graph.json assente: esegui prima 'graphify update .'")
    n = numeri()
    with open(USCITA, "w", encoding="utf-8", newline="\n") as f:
        f.write(html(n))
    mancanti = [v["file"] for v in VISTE
                if not os.path.exists(os.path.join(ROOT, "graphify-out", v["file"]))]
    print(f"Porta delle viste -> graphify-out/index.html (grafo {n['commit']})")
    if mancanti:
        print(f"  ATTENZIONE: viste non ancora generate: {', '.join(mancanti)}")


if __name__ == "__main__":
    main()
