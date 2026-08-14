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
try:
    from tools.brain import BRAIN            # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente


# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

sys.path.insert(0, ROOT)

from tools import build_atlas_view as atlante          # noqa: E402  (riuso, non duplico)

USCITA = os.path.join(BRAIN, "graphify-out", "index.html")


def brain_corrente():
    """Quale brain stiamo guardando. Senza questo, la porta mostrava tre viste
    senza dire DI CHE COSA: con un brain solo si intuisce, con due e' una trappola.

    ATTENZIONE al caso che sembrava innocuo: dentro un'istanza autosufficiente BRAIN
    e ROOT COINCIDONO, quindi confrontarli faceva chiamare ogni brain 'brain di
    riferimento' — aprivi l'atlante di 'cucina' e diceva di essere il brain
    principale. Il riferimento si riconosce dal fatto di essere un'OFFICINA: ha
    core/ e brains/ accanto. Tutto il resto si chiama col proprio nome."""
    base = os.path.abspath(BRAIN)
    # Il REGISTRO ha la precedenza: il brain addestrato dell'autore vive nella radice
    # dell'officina, ma non e' un default anonimo — e' una voce con un nome, come le
    # altre. Chiamarlo "brain di riferimento" nascondeva proprio quel fatto.
    reg = os.path.join(ROOT, "brains", "brains.json")
    if os.path.exists(reg):
        try:
            with open(reg, encoding="utf-8") as f:
                for b in json.load(f).get("brains", []):
                    if os.path.abspath(os.path.join(ROOT, b["percorso"])) == base:
                        return b["nome"]
        except (OSError, ValueError, KeyError):
            pass
    return os.path.basename(base)


def altri_brain():
    """Gli altri brain del repo, con la porta di ciascuno. Vuoto in un'istanza
    autosufficiente: li' non c'e' un registro, e non ci sono altri brain da vedere."""
    reg = os.path.join(ROOT, "brains", "brains.json")
    if not os.path.exists(reg) or os.path.abspath(BRAIN) != os.path.abspath(ROOT):
        return []
    try:
        with open(reg, encoding="utf-8") as f:
            elenco = json.load(f).get("brains", [])
    except (OSError, ValueError):
        return []
    fuori = []
    for b in elenco:
        base = os.path.abspath(os.path.join(ROOT, b["percorso"]))
        # Il brain su cui sei gia' non e' un "altro": il brain addestrato dell'autore
        # e' una voce del registro come le altre (percorso '.'), non un default
        # implicito — ma elencarlo qui lo farebbe puntare a se stesso.
        if base == os.path.abspath(BRAIN):
            continue
        porta = os.path.join(base, "graphify-out", "index.html")
        # link RELATIVO: la porta deve funzionare aperta da file://
        rel = os.path.relpath(porta, os.path.join(BRAIN, "graphify-out"))
        fuori.append({"nome": b["nome"], "href": rel.replace("\\", "/"),
                      "pronto": os.path.exists(porta)})
    return sorted(fuori, key=lambda x: x["nome"])


def numeri():
    """Cosa contiene ciascuna vista, contato sul grafo vero."""
    with open(atlante.GRAFO, encoding="utf-8") as f:
        g = json.load(f)
    dati = atlante.costruisci()

    compatta = "—"
    percorso = os.path.join(BRAIN, "graphify-out", "graph-compact.json")
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
        "brain": brain_corrente(),
        "altri_brain": altri_brain(),
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

    altri = n.get("altri_brain") or []
    if altri:
        voci = "".join(
            f'<a class="brain{"" if b["pronto"] else " spento"}" '
            f'href="{b["href"]}">{b["nome"]}</a>' if b["pronto"] else
            f'<span class="brain spento" title="grafo non ancora generato">{b["nome"]}</span>'
            for b in altri)
        selettore = ('\n  <nav class="brains">'
                     '<span class="etichetta">altri brain</span>' + voci + "</nav>")
    else:
        selettore = ""

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
.quale{{color:#64748b !important;font-size:12px;margin-top:4px !important}}
.quale b{{color:#22d3ee;font-weight:600}}
.brains{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;
  padding:12px 16px;border-radius:12px;background:rgba(14,14,17,.9);
  border:1px solid rgba(148,163,184,.22)}}
.brains .etichetta{{font-size:10px;letter-spacing:.13em;text-transform:uppercase;
  color:#64748b;font-weight:700;margin-right:4px}}
.brain{{font-size:12px;padding:4px 11px;border-radius:999px;text-decoration:none;
  color:#cbd5e1;border:1px solid rgba(148,163,184,.28)}}
.brain:hover{{border-color:#22d3ee;color:#22d3ee}}
.brain:focus-visible{{outline:2px solid #22d3ee;outline-offset:2px}}
.brain.spento{{color:#475569;border-style:dashed;cursor:default}}
@media(prefers-reduced-motion:reduce){{.vista{{transition:none}}}}
</style></head><body>
<div class="foglio">
  <header>
    <h1>Le tre viste del grafo</h1>
    <p class="quale">stai guardando: <b>{n['brain']}</b></p>
    <p>Sono tre risposte a <b>tre domande diverse</b>. Aprire quella sbagliata per la
       domanda che hai è il modo più comune di perderci tempo — qui sta scritto
       prima del click.</p>
  </header>{selettore}
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
                if not os.path.exists(os.path.join(BRAIN, "graphify-out", v["file"]))]
    print(f"Porta delle viste -> graphify-out/index.html (grafo {n['commit']})")
    if mancanti:
        print(f"  ATTENZIONE: viste non ancora generate: {', '.join(mancanti)}")


if __name__ == "__main__":
    main()
