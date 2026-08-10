# -*- coding: utf-8 -*-
"""
altair-brain — ATLANTE: la terza vista del grafo, esplorabile in 3D.

PERCHE UNA TERZA VISTA. Le due esistenti falliscono l'esplorazione per ragioni
opposte. La vista estesa (1603 nodi) e un gomitolo force-directed: la posizione
non significa nulla, e solo l'equilibrio di una simulazione fisica, e trovare
qualcosa e impossibile. La vista compatta (19 nodi) e un diagramma del processo:
si legge, non si esplora. In mezzo manca il livello che serve davvero — navigare
la conoscenza sapendo sempre dove ci si trova.

L'IDEA: usare l'architettura del brain come sistema di coordinate, invece di
lasciar decidere alla fisica.

  ALTEZZA (Y)  = lo strato del processo, dal basso in alto:
                 FONTI (raw/) -> SAPERE (wiki/) -> MOTORE (engine tools server)
                 -> USO (skill, report, dottrina).  Gli stessi 5 passi della
                 vista compatta, resi navigabili: le due viste concordano.
  ANGOLO       = la macroarea. Ogni area ha uno spicchio della STESSA ampiezza:
                 se un'area e vuota, lo spicchio vuoto si vede a colpo d'occhio.
  RAGGIO       = la centralita. I nodi piu connessi stanno vicino all'asse, le
                 foglie in periferia. Si vola verso il centro per trovare gli hub.
  ANGOLO FINE  = la community. Dentro uno spicchio i nodi della stessa community
                 sono angolarmente adiacenti: i grappoli si leggono.

Cosi la forma del brain si LEGGE senza spiegazioni: la provenienza raw->wiki
diventa un arco VERTICALE (l'architettura a strati resa visibile), i ponti
intercampo diventano archi ORIZZONTALI che scavalcano gli spicchi, e le aree
povere sono buchi nella ruota.

DETTAGLIO SU RICHIESTA. Si mostrano i ~214 nodi-FILE, non i 1603 titoli interni:
un file si apre e rivela le proprie sezioni e i vicini per tipo di relazione. La
"lente" (tasto L) spegne tutto tranne il vicinato a 2 passi del nodo scelto: e il
modo per essere insieme chiari e profondi senza tornare al gomitolo.

TECNICA: canvas 2D con proiezione prospettica scritta a mano. Nessuna libreria,
nessuna CDN, funziona da file:// e offline. Archi disegnati come curve di Bezier
campionate in 3D (gli archi dritti in prospettiva si confondono col fondo).
Deterministico: stesso grafo -> stesso atlante, byte per byte.

Uso:  python tools/build_atlas_view.py     -> graphify-out/graph-atlas.html
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAFO = os.path.join(ROOT, "graphify-out", "graph.json")
ROUTER = os.path.join(ROOT, "engine", "router.json")
OUT = os.path.join(ROOT, "graphify-out", "graph-atlas.html")

# --- Gli strati del processo, dal basso verso l'alto ------------------------
# Le quote sono equidistanti: la distanza verticale tra due nodi si legge come
# "quanti passi di lavorazione li separano".
STRATI = {
    "fonti":  {"y": -3.0, "label": "FONTI",  "sotto": "raw/ — materiale grezzo",        "colore": "#f59e0b"},
    "sapere": {"y": -1.0, "label": "SAPERE", "sotto": "wiki/ — conoscenza curata",      "colore": "#22d3ee"},
    "motore": {"y":  1.0, "label": "MOTORE", "sotto": "engine tools server tests",      "colore": "#a855f7"},
    "uso":    {"y":  3.0, "label": "USO",    "sotto": "skill, report, dottrina",        "colore": "#f472b6"},
}
CARTELLE_MOTORE = ("engine", "tools", "server", "tests", "graphify-out", "metrics")
CARTELLE_USO = (".claude", ".agents", "reports", ".github")

COLORI_AREA = {
    "aion":         "#a78bfa",
    "creativita":   "#f472b6",
    "data-science": "#22d3ee",
    "divulgazione": "#34d399",
    "finanza":      "#fbbf24",
    "web-design":   "#fb923c",
    "impianto":     "#7c8aa0",
}
AREA_ALTRO = "impianto"          # tutto cio che non e conoscenza di dominio

# Geometria della ruota. R_MIN evita che gli hub collassino sull'asse.
R_MIN, R_MAX = 1.05, 4.75


# --------------------------------------------------------------------------
# 1. Lettura del grafo e riduzione al livello-file
# --------------------------------------------------------------------------
def _rel(nodo):
    return (nodo.get("source_file") or "").replace("\\", "/")


def strato_di(rel):
    testa = rel.split("/")[0]
    if testa == "raw":
        return "fonti"
    if testa == "wiki":
        return "sapere"
    if testa in CARTELLE_MOTORE:
        return "motore"
    # cartelle di consumo e file di dottrina in radice (CLAUDE.md, ROADMAP.md...):
    # sono cio che un agente legge al momento di usare il brain.
    return "uso"


def aree_canoniche():
    """Ordine delle aree preso dal router: la vista non inventa una tassonomia sua."""
    try:
        with open(ROUTER, encoding="utf-8") as f:
            return list(json.load(f).get("aree", {}).keys())
    except (OSError, ValueError):
        return []


def area_di(rel, canoniche):
    parti = rel.split("/")
    if parti[0] in ("raw", "wiki") and len(parti) > 2 and parti[1] in canoniche:
        return parti[1]
    return AREA_ALTRO


def carica(canoniche):
    with open(GRAFO, encoding="utf-8") as f:
        g = json.load(f)

    # Un nodo e un FILE quando la sua etichetta e il nome del file stesso:
    # e la convenzione con cui graphify marca la radice di ogni sorgente.
    per_id, sezioni = {}, {}
    for n in g["nodes"]:
        rel = _rel(n)
        if not rel:
            continue
        etichetta = (n.get("label") or "").strip()
        if etichetta == os.path.basename(rel):
            per_id[n["id"]] = {
                "id": n["id"], "file": rel, "nome": os.path.basename(rel),
                "strato": strato_di(rel), "area": area_di(rel, canoniche),
                "tipo": n.get("file_type") or "document",
                "comunita": n.get("community", -1),
            }
        elif etichetta:
            sezioni.setdefault(rel, []).append(etichetta[:80])

    ids = set(per_id)
    archi, grado, visti = [], {i: 0 for i in ids}, set()
    for e in g["links"]:
        s, t = e.get("source"), e.get("target")
        if s not in ids or t not in ids or s == t:
            continue
        chiave = (min(s, t), max(s, t), e.get("relation"))
        if chiave in visti:
            continue
        visti.add(chiave)
        archi.append({"a": s, "b": t, "r": e.get("relation") or "?"})
        grado[s] += 1
        grado[t] += 1
    return per_id, archi, grado, sezioni


# --------------------------------------------------------------------------
# 2. Layout analitico — nessuna simulazione, nessun caso
# --------------------------------------------------------------------------
def disponi(per_id, grado, canoniche):
    """Assegna x,y,z. Deterministico: dipende solo dal grafo, mai dall'ordine di
    iterazione o da un seme casuale."""
    presenti = [a for a in canoniche if any(d["area"] == a for d in per_id.values())]
    aree = presenti + [AREA_ALTRO]        # l'impianto occupa l'ultimo spicchio
    settore = {a: i for i, a in enumerate(aree)}
    n_aree = len(aree)
    ampiezza = (2 * math.pi / n_aree) * 0.80      # 20% di corridoio tra spicchi

    gruppi = {}
    for d in per_id.values():
        gruppi.setdefault((d["area"], d["strato"]), []).append(d)

    for (area, strato), gruppo in gruppi.items():
        n = len(gruppo)
        base = (settore[area] / n_aree) * 2 * math.pi - ampiezza / 2

        # RAGGIO — rango di centralita. La radice distribuisce i nodi a densita
        # uniforme sull'anello: senza, si ammassano tutti al bordo esterno.
        per_grado = sorted(gruppo, key=lambda d: (-grado.get(d["id"], 0), d["file"]))
        for rango, d in enumerate(per_grado):
            q = (rango + 0.5) / n
            d["_r"] = R_MIN + (R_MAX - R_MIN) * math.sqrt(q)

        # ANGOLO — ordine per community: i grappoli diventano archi contigui.
        # Indipendente dal raggio, cosi le due letture non si sovrappongono.
        per_comunita = sorted(gruppo, key=lambda d: (d["comunita"], d["file"]))
        for k, d in enumerate(per_comunita):
            ang = base + ampiezza * ((k + 0.5) / n)
            d["x"] = round(math.cos(ang) * d["_r"], 4)
            d["z"] = round(math.sin(ang) * d["_r"], 4)
            # Rilievo dentro lo strato: la community diventa una micro-quota, cosi
            # il piano non e una lastra piatta e la profondita si percepisce.
            d["y"] = round(STRATI[strato]["y"] + ((d["comunita"] % 5) - 2) * 0.075, 4)
            d["grado"] = grado.get(d["id"], 0)
            d["colore"] = COLORI_AREA.get(area, COLORI_AREA[AREA_ALTRO])
            del d["_r"]
    return aree


# --------------------------------------------------------------------------
# 3. Serializzazione compatta (chiavi corte: il file va aperto in un browser)
# --------------------------------------------------------------------------
def costruisci():
    canoniche = aree_canoniche()
    per_id, archi, grado, sezioni = carica(canoniche)
    aree = disponi(per_id, grado, canoniche)

    nodi = sorted(per_id.values(), key=lambda d: d["file"])
    indice = {d["id"]: i for i, d in enumerate(nodi)}
    conta = {}
    for d in nodi:
        conta[d["area"]] = conta.get(d["area"], 0) + 1

    return {
        "nodi": [{"n": d["nome"], "f": d["file"], "a": d["area"], "s": d["strato"],
                  "x": d["x"], "y": d["y"], "z": d["z"], "g": d["grado"],
                  "c": d["colore"], "t": d["tipo"],
                  "sez": sorted(sezioni.get(d["file"], []))[:24]} for d in nodi],
        "archi": [{"a": indice[e["a"]], "b": indice[e["b"]], "r": e["r"]} for e in archi],
        "aree": aree, "conta": conta, "strati": STRATI, "colori": COLORI_AREA,
    }


def html(dati):
    compatto = json.dumps(dati, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return MODELLO.replace("__DATI__", compatto)


MODELLO = r"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Altair Brain — Atlante 3D</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(circle at 50% 42%,#0d1424 0%,#05070d 62%);color:#e2e8f0;
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;overflow:hidden}
canvas{display:block;cursor:grab;position:fixed;inset:0}canvas.presa{cursor:grabbing}
.pan{position:fixed;background:rgba(9,13,23,.9);border:1px solid rgba(148,163,184,.2);
  border-radius:13px;backdrop-filter:blur(14px);box-shadow:0 12px 40px rgba(0,0,0,.45)}
#capo{top:16px;left:16px;padding:14px 17px;max-width:318px}
#capo h1{font-size:15px;font-weight:700;letter-spacing:.01em}
#capo p{font-size:11.5px;color:#94a3b8;margin-top:7px;line-height:1.5}
#capo b{color:#cbd5e1}
#hud{margin-top:9px;padding-top:9px;border-top:1px solid rgba(148,163,184,.14);
  font-size:10.5px;color:#64748b;font-family:ui-monospace,SFMono-Regular,monospace}
#cmd{top:16px;right:16px;padding:13px 14px;width:230px;max-height:calc(100vh - 32px);overflow:auto}
#cmd::-webkit-scrollbar{width:5px}#cmd::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
#cmd h2{font-size:9.5px;letter-spacing:.12em;color:#64748b;text-transform:uppercase;margin:13px 0 7px}
#cmd h2:first-child{margin-top:0}
#cerca{width:100%;background:rgba(2,6,16,.8);border:1px solid rgba(148,163,184,.24);border-radius:8px;
  padding:8px 10px;color:#e2e8f0;font-size:12px;outline:none}
#cerca:focus{border-color:#38bdf8;box-shadow:0 0 0 3px rgba(56,189,248,.12)}
#esiti{font-size:10.5px;color:#64748b;margin-top:5px;min-height:13px}
.riga{display:flex;align-items:center;gap:8px;padding:3.5px 0;font-size:11.5px;cursor:pointer;user-select:none}
.riga:hover{color:#fff}.riga.spenta{opacity:.3}.riga .num{margin-left:auto;color:#475569;font-size:10px}
.bollo{width:9px;height:9px;border-radius:50%;flex:none}
.bollo.q{border-radius:2px}
.bott{display:inline-block;font-size:10.5px;padding:4px 9px;margin:2px 3px 0 0;border-radius:7px;cursor:pointer;
  border:1px solid rgba(148,163,184,.24);color:#cbd5e1;background:rgba(2,6,16,.5)}
.bott:hover{border-color:#38bdf8;color:#fff}.bott.on{border-color:#38bdf8;color:#38bdf8;background:rgba(56,189,248,.1)}
#det{left:16px;bottom:16px;width:378px;max-height:56vh;overflow:auto;padding:16px 18px;display:none}
#det.aperto{display:block}
#det::-webkit-scrollbar{width:5px}#det::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
#det .nome{font-size:15.5px;font-weight:700;word-break:break-word;padding-right:22px}
#det .via{font-size:10.5px;color:#64748b;margin-top:3px;font-family:ui-monospace,monospace;word-break:break-all}
.etich{display:flex;gap:6px;flex-wrap:wrap;margin:11px 0 2px}
.tag{font-size:10px;padding:2.5px 9px;border-radius:999px;border:1px solid rgba(148,163,184,.28);color:#cbd5e1}
#det h3{font-size:9.5px;letter-spacing:.1em;color:#64748b;text-transform:uppercase;margin:14px 0 6px}
#det ul{list-style:none;font-size:11.5px}
#det li{padding:3px 0;color:#cbd5e1;border-bottom:1px solid rgba(148,163,184,.07)}
#det li.link{cursor:pointer}#det li.link:hover{color:#38bdf8}
#det li .dove{color:#475569;font-size:10px}
.chiudi{position:absolute;top:12px;right:14px;cursor:pointer;color:#64748b;font-size:18px;line-height:1}
.chiudi:hover{color:#e2e8f0}
#suggerimento{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);font-size:10.5px;color:#475569;
  text-align:center;pointer-events:none;white-space:nowrap}
kbd{background:rgba(148,163,184,.14);border-radius:3px;padding:1.5px 5px;font-size:9.5px;color:#94a3b8}
#nube{position:fixed;pointer-events:none;background:rgba(2,6,16,.94);border:1px solid rgba(148,163,184,.3);
  border-radius:7px;padding:5px 9px;font-size:11px;display:none;white-space:nowrap;z-index:9}
#nube .sub{color:#64748b;font-size:10px}
@media(max-width:820px){#cmd,#capo{display:none}#det{width:calc(100vw - 32px)}}
</style></head><body>
<canvas id="tela"></canvas>

<div class="pan" id="capo">
  <h1>Atlante del Brain</h1>
  <p><b>Qui la posizione significa.</b> L'altezza è lo strato del processo, lo
     spicchio è la macroarea, la distanza dall'asse è quanto un nodo è connesso.
     Ogni area ha uno spicchio uguale: se è vuoto, si vede.</p>
  <div id="hud"></div>
</div>

<div class="pan" id="cmd">
  <h2>Cerca</h2>
  <input id="cerca" placeholder="nome file o area…" autocomplete="off" spellcheck="false">
  <div id="esiti"></div>
  <h2>Strati</h2><div id="fStrati"></div>
  <h2>Aree</h2><div id="fAree"></div>
  <h2>Relazioni</h2><div id="fRel"></div>
  <h2>Vista</h2>
  <div>
    <span class="bott" onclick="posa('obliqua')">obliqua</span>
    <span class="bott" onclick="posa('sezione')">sezione</span>
    <span class="bott" onclick="posa('alto')">dall'alto</span>
    <span class="bott" id="bLente" onclick="lente()">lente 2 passi</span>
    <span class="bott" id="bGira" onclick="gira()">rotazione</span>
  </div>
</div>

<div class="pan" id="det">
  <span class="chiudi" onclick="chiudi()">&times;</span>
  <div class="nome" id="dNome"></div>
  <div class="via" id="dVia"></div>
  <div class="etich" id="dTag"></div>
  <div id="dCorpo"></div>
</div>

<div id="nube"></div>
<div id="suggerimento"><kbd>trascina</kbd> ruota · <kbd>rotella</kbd> zoom ·
  <kbd>click</kbd> apri · <kbd>doppio click</kbd> vola al nodo ·
  <kbd>L</kbd> lente · <kbd>R</kbd> rotazione · <kbd>Esc</kbd> chiudi</div>

<script>
"use strict";
const D = __DATI__;
const R_MIN = __R_MIN__, R_MAX = __R_MAX__;   // stessa geometria del layout Python

/* Etichette leggibili per le relazioni che graphify estrae. Le prime tre sono
   quelle che raccontano l'architettura: si disegnano piu spesse. */
const REL = {
  derived_from:  {c:'#f59e0b', l:'provenienza (fonte → sapere)', forte:1},
  bridge:        {c:'#f472b6', l:'ponte intercampo',             forte:1},
  generated_from:{c:'#a855f7', l:'generato da',                  forte:1},
  references:    {c:'#64748b', l:'riferimento (wikilink)'},
  imports:       {c:'#94a3b8', l:'import di codice'},
  imports_from:  {c:'#94a3b8', l:'import di codice'},
  calls:         {c:'#475569', l:'chiamata'},
  contains:      {c:'#475569', l:'contiene'},
};
const info = r => REL[r] || {c:'#475569', l:r};

const tela = document.getElementById('tela'), ctx = tela.getContext('2d');
let W, H;
/* Camera orbitale: due angoli, una distanza, un bersaglio. Il bersaglio si muove
   quando si "vola" su un nodo — e cio che rende l'esplorazione immersiva invece
   che una rotazione attorno a un centro fisso. */
let angX = -0.40, angY = 0.55, dist = 14.0, scala = 900;
let mira = {x:0, y:0, z:0}, miraObiettivo = {x:0, y:0, z:0}, distObiettivo = 14.0;
let trascina = false, ux = 0, uy = 0, mosso = false;
let scelto = null, sfiorato = null, conLente = false, rotante = true;
let filtro = '', mouse = {x:-9e9, y:-9e9};

const strati = new Set(Object.keys(D.strati));
const aree = new Set(D.aree);
const relUsate = [...new Set(D.archi.map(a => a.r))].sort(
  (a,b) => (info(b).forte|0) - (info(a).forte|0) || a.localeCompare(b));
const relAttive = new Set(relUsate);

/* Adiacenza: serve alla lente, al pannello e all'evidenziazione. Costruita una
   volta sola — ricalcolarla a ogni frame costerebbe piu del disegno. */
const vicini = D.nodi.map(() => []);
D.archi.forEach((a, i) => { vicini[a.a].push({j:a.b, i}); vicini[a.b].push({j:a.a, i}); });

function intorno(i, passi) {
  const visto = new Set([i]); let bordo = [i];
  for (let p = 0; p < passi; p++) {
    const prossimo = [];
    bordo.forEach(k => vicini[k].forEach(v => {
      if (!visto.has(v.j)) { visto.add(v.j); prossimo.push(v.j); } }));
    bordo = prossimo;
  }
  return visto;
}

/* Il ridimensionamento e controllato dal ciclo di disegno, non dall'evento
   'resize': se la pagina viene aperta in un contenitore che ha larghezza 0 al
   caricamento (pannello nascosto, iframe montato dopo), l'evento non arriva mai
   e la tela resterebbe vuota per sempre. Il confronto costa due letture a frame. */
function ridimensiona() {
  W = innerWidth; H = innerHeight;
  tela.style.width = W + 'px'; tela.style.height = H + 'px';
  tela.width = Math.max(1, W * devicePixelRatio);
  tela.height = Math.max(1, H * devicePixelRatio);
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  // La scala segue la finestra: una costante fissa lascerebbe l'atlante grande
  // come un francobollo su uno schermo largo e tagliato su uno piccolo.
  // Su schermo stretto il vincolo e la larghezza, su schermo largo l'altezza:
  // si prende il piu severo dei due, altrimenti la ruota esce dai bordi in verticale.
  scala = Math.max(300, Math.min(W * 0.82, H * 0.95));
}
ridimensiona();

/* --- Proiezione prospettica, scritta a mano ------------------------------
   Traslazione sul bersaglio, rotazione attorno a Y (imbardata) poi attorno a X
   (beccheggio), infine divisione per la profondita. Niente matrici: con due soli
   angoli il conto esplicito e piu corto e piu veloce. */
function proietta(p) {
  const x0 = p.x - mira.x, y0 = p.y - mira.y, z0 = p.z - mira.z;
  const cy = Math.cos(angY), sy = Math.sin(angY);
  const x = x0*cy - z0*sy;  let z = x0*sy + z0*cy;
  const cx = Math.cos(angX), sx = Math.sin(angX);
  const y = y0*cx - z*sx;   z = y0*sx + z*cx;
  const d = z + dist;
  if (d <= 0.4) return null;                    // dietro la camera
  const s = scala / d;
  return {sx: W/2 + x*s, sy: H/2 - y*s, s, d};
}
/* Velo di profondita: cio che e lontano sbiadisce. E l'unico indizio di distanza
   che il cervello legge senza pensarci, e da solo trasforma un disegno piatto in
   uno spazio. */
const velo = d => Math.max(0.16, Math.min(1, 1.55 - (d - (dist - 5.5)) / 13));

const acceso  = n => strati.has(n.s) && aree.has(n.a);
const combacia = n => !filtro || n.n.toLowerCase().includes(filtro) || n.a.includes(filtro);

let insiemeLente = null;
const dentroLente = i => !conLente || scelto === null || insiemeLente.has(i);

/* --- Disegno ------------------------------------------------------------- */
const P = new Array(D.nodi.length);

function anelloStrato(st) {
  ctx.strokeStyle = st.colore + '1c'; ctx.lineWidth = 1;
  ctx.beginPath();
  for (let i = 0; i <= 64; i++) {
    const a = i / 64 * Math.PI * 2;
    const p = proietta({x: Math.cos(a)*(R_MAX+0.35), y: st.y, z: Math.sin(a)*(R_MAX+0.35)});
    if (!p) { ctx.stroke(); ctx.beginPath(); continue; }
    i ? ctx.lineTo(p.sx, p.sy) : ctx.moveTo(p.sx, p.sy);
  }
  ctx.stroke();
  const e = proietta({x: R_MAX + 0.75, y: st.y, z: 0});
  if (e) {
    // L'etichetta segue l'anello in 3D, ma non deve mai uscire dallo schermo:
    // quando arriverebbe oltre il bordo si ribalta e si allinea a destra.
    let tx = e.sx;
    if (tx > W - 150) { tx = Math.min(tx, W - 10); ctx.textAlign = 'right'; }
    else if (tx < 10) { tx = 10; ctx.textAlign = 'left'; }
    else ctx.textAlign = 'left';
    ctx.fillStyle = st.colore + 'cc'; ctx.font = '700 10.5px sans-serif';
    ctx.fillText(st.label, tx, e.sy);
    if (W >= 560) {                       // la riga di spiegazione solo se c'e posto
      ctx.fillStyle = '#475569'; ctx.font = '9.5px sans-serif';
      ctx.fillText(st.sotto, tx, e.sy + 12);
    }
  }
}

/* Le divisioni tra spicchi: sono cio che rende leggibile "questa area finisce
   qui". Senza, la ruota e un disco indistinto. */
function spicchi() {
  const n = D.aree.length;
  ctx.lineWidth = 1;
  for (let k = 0; k < n; k++) {
    const a = (k / n) * Math.PI*2 - Math.PI/n;
    const p1 = proietta({x: Math.cos(a)*R_MIN, y: -3.35, z: Math.sin(a)*R_MIN});
    const p2 = proietta({x: Math.cos(a)*(R_MAX+0.35), y: -3.35, z: Math.sin(a)*(R_MAX+0.35)});
    if (p1 && p2) { ctx.strokeStyle = 'rgba(148,163,184,.10)';
      ctx.beginPath(); ctx.moveTo(p1.sx,p1.sy); ctx.lineTo(p2.sx,p2.sy); ctx.stroke(); }
    const area = D.aree[k], q = D.conta[area] || 0;
    const centro = (k / n) * Math.PI*2;
    const e = proietta({x: Math.cos(centro)*(R_MAX+0.15), y: -3.5, z: Math.sin(centro)*(R_MAX+0.15)});
    if (e && aree.has(area)) {
      ctx.textAlign = 'center'; ctx.font = '600 10px sans-serif';
      ctx.fillStyle = (D.colori[area] || '#7c8aa0') + (q ? 'dd' : '55');
      ctx.fillText(area + '  ' + q, e.sx, e.sy);
    }
  }
}

/* L'anello di ritorno: le lezioni prodotte usando il brain rientrano tra le
   fonti. E un'annotazione di PROCESSO, non un arco del grafo — percio e
   tratteggiata e dichiarata, per non farla scambiare per un dato. */
function anelloFeedback() {
  ctx.save(); ctx.setLineDash([5, 6]);
  ctx.strokeStyle = 'rgba(52,211,153,.34)'; ctx.lineWidth = 1.4;
  ctx.beginPath();
  let primo = true, medio = null;
  for (let i = 0; i <= 30; i++) {
    const t = i/30, ang = -Math.PI*0.32;
    const r = (R_MAX + 0.9) + Math.sin(t*Math.PI) * 1.5;
    const p = proietta({x: Math.cos(ang)*r, y: 3.0 - 6.0*t, z: Math.sin(ang)*r});
    if (!p) continue;
    if (i === 15) medio = p;
    primo ? (ctx.moveTo(p.sx,p.sy), primo=false) : ctx.lineTo(p.sx,p.sy);
  }
  ctx.stroke(); ctx.restore();
  if (medio) { ctx.textAlign='center'; ctx.font='9.5px sans-serif';
    ctx.fillStyle='rgba(52,211,153,.6)'; ctx.fillText('le lezioni rientrano', medio.sx, medio.sy); }
}

/* Archi come curve: il punto di controllo e spinto FUORI dall'asse, cosi due
   nodi vicini non producono una corda che taglia il centro della ruota. In
   prospettiva le corde dritte si sovrappongono e diventano illeggibili. */
function arco(a, b) {
  const mx = (a.x+b.x)/2, my = (a.y+b.y)/2, mz = (a.z+b.z)/2;
  const l = Math.hypot(mx, mz) || 1;
  const gonfio = 0.20 * Math.hypot(a.x-b.x, a.y-b.y, a.z-b.z);
  const cxp = mx + (mx/l)*gonfio, czp = mz + (mz/l)*gonfio;
  const punti = [];
  for (let i = 0; i <= 10; i++) {
    const t = i/10, u = 1-t;
    const p = proietta({x: u*u*a.x + 2*u*t*cxp + t*t*b.x,
                        y: u*u*a.y + 2*u*t*my  + t*t*b.y,
                        z: u*u*a.z + 2*u*t*czp + t*t*b.z});
    if (p) punti.push(p);
  }
  return punti;
}

function disegna() {
  if (W !== innerWidth || H !== innerHeight) ridimensiona();
  // interpolazione morbida verso il bersaglio: il "volo" verso un nodo
  mira.x += (miraObiettivo.x - mira.x)*0.12;
  mira.y += (miraObiettivo.y - mira.y)*0.12;
  mira.z += (miraObiettivo.z - mira.z)*0.12;
  dist += (distObiettivo - dist)*0.10;
  if (rotante && !trascina) angY += 0.0013;

  ctx.clearRect(0, 0, W, H);
  for (let i = 0; i < D.nodi.length; i++) {
    const n = D.nodi[i];
    P[i] = acceso(n) ? proietta(n) : null;      // mai lasciare proiezioni stantie
  }

  spicchi();
  Object.entries(D.strati).forEach(([k, st]) => { if (strati.has(k)) anelloStrato(st); });
  // L'anello di ritorno gira piu largo di tutto il resto: su schermo stretto
  // uscirebbe dal bordo, e non vale la pena rimpicciolire l'atlante per lui.
  if (strati.size === 4 && W >= 700) anelloFeedback();

  // ARCHI (prima dei nodi: restano dietro)
  let archiVisti = 0;
  for (const e of D.archi) {
    const A = P[e.a], B = P[e.b];
    if (!A || !B || !relAttive.has(e.r)) continue;
    if (!dentroLente(e.a) || !dentroLente(e.b)) continue;
    const sel = scelto !== null && (e.a === scelto || e.b === scelto);
    const evi = sfiorato !== null && (e.a === sfiorato || e.b === sfiorato);
    if (filtro && !sel && !combacia(D.nodi[e.a]) && !combacia(D.nodi[e.b])) continue;
    const I = info(e.r), forte = !!I.forte;
    const op = velo((A.d + B.d)/2) * (sel||evi ? 1 : (forte ? 0.5 : 0.22));
    const punti = arco(D.nodi[e.a], D.nodi[e.b]);
    if (punti.length < 2) continue;
    ctx.globalAlpha = op; ctx.strokeStyle = I.c;
    ctx.lineWidth = sel ? 2.1 : (evi ? 1.7 : (forte ? 1.25 : 0.65));
    ctx.beginPath(); ctx.moveTo(punti[0].sx, punti[0].sy);
    for (let i = 1; i < punti.length; i++) ctx.lineTo(punti[i].sx, punti[i].sy);
    ctx.stroke(); archiVisti++;
  }
  ctx.globalAlpha = 1;

  // NODI, dal fondo verso la camera (algoritmo del pittore)
  const ordine = [];
  for (let i = 0; i < D.nodi.length; i++) if (P[i] && dentroLente(i)) ordine.push(i);
  ordine.sort((a, b) => P[b].d - P[a].d);

  // Scala di riferimento: quella del piano che la camera sta guardando. Tutte le
  // grandezze in pixel si esprimono come rapporto con questa, cosi restano uguali
  // su qualsiasi schermo e crescono solo per l'avvicinamento prospettico.
  const sRif = scala / dist;
  const etichette = [];
  for (const i of ordine) {
    const n = D.nodi[i], p = P[i];
    const sel = i === scelto, evi = i === sfiorato, ok = combacia(n);
    const r = Math.max(2.2, (2.9 + Math.sqrt(n.g)*1.35) * p.s/sRif);
    ctx.globalAlpha = velo(p.d) * (ok ? 1 : 0.12);
    if (sel || evi) {                                  // alone
      ctx.beginPath(); ctx.arc(p.sx, p.sy, r + (sel?9:6), 0, 7);
      ctx.fillStyle = n.c + (sel ? '3a' : '22'); ctx.fill();
    }
    ctx.beginPath();
    // quadrato = codice, cerchio = documento: si distingue senza leggere
    if (n.t === 'code') ctx.rect(p.sx-r, p.sy-r, r*2, r*2);
    else ctx.arc(p.sx, p.sy, r, 0, 7);
    ctx.fillStyle = n.c; ctx.fill();
    if (sel) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.7; ctx.stroke(); }
    ctx.globalAlpha = 1;
    // Etichette: solo dove non affollano. Gli hub le hanno sempre, gli altri solo
    // se cercati o toccati — altrimenti il testo copre il disegno.
    if (sel || evi || (filtro && ok) || n.g >= 7 || (conLente && scelto !== null))
      etichette.push({p, n, sel: sel||evi, ok});
  }
  etichette.forEach(({p, n, sel, ok}) => {
    ctx.globalAlpha = velo(p.d) * (ok ? 0.95 : 0.2);
    ctx.font = (sel ? '700 ' : '') + Math.max(9, Math.min(15, 11*p.s/sRif)) + 'px sans-serif';
    ctx.textAlign = 'center';
    const testo = n.n.replace(/\.(md|py|json|html|yml|txt)$/, '');
    if (sel) { ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(5,7,13,.85)'; ctx.strokeText(testo, p.sx, p.sy - 11); }
    ctx.fillStyle = sel ? '#fff' : '#cbd5e1';
    ctx.fillText(testo, p.sx, p.sy - 11);
  });
  ctx.globalAlpha = 1;

  document.getElementById('hud').textContent =
    ordine.length + ' file · ' + archiVisti + ' relazioni visibili' +
    (conLente && scelto !== null ? ' · lente attiva' : '');
}

function anima() { disegna(); requestAnimationFrame(anima); }

/* --- Puntamento ---------------------------------------------------------- */
function sotto(mx, my) {
  let vicino = null, dmin = 20;
  for (let i = 0; i < D.nodi.length; i++) {
    const p = P[i];
    if (!p || !dentroLente(i) || !combacia(D.nodi[i])) continue;
    const d = Math.hypot(p.sx - mx, p.sy - my);
    if (d < dmin) { dmin = d; vicino = i; }
  }
  return vicino;
}

const nube = document.getElementById('nube');
tela.addEventListener('mousedown', e => {
  trascina = true; mosso = false; ux = e.clientX; uy = e.clientY; tela.classList.add('presa');
});
addEventListener('mouseup', () => { trascina = false; tela.classList.remove('presa'); });
addEventListener('mousemove', e => {
  mouse = {x: e.clientX, y: e.clientY};
  if (trascina) {
    if (Math.abs(e.clientX-ux) + Math.abs(e.clientY-uy) > 3) { mosso = true; rotante = false; segnaGira(); }
    angY += (e.clientX - ux) * 0.0062;
    angX = Math.max(-1.5, Math.min(1.5, angX + (e.clientY - uy) * 0.0062));
    ux = e.clientX; uy = e.clientY;
    nube.style.display = 'none';
    return;
  }
  const i = sotto(e.clientX, e.clientY);
  sfiorato = i;
  if (i === null) { nube.style.display = 'none'; return; }
  const n = D.nodi[i];
  nube.innerHTML = '<b>' + esc(n.n) + '</b><br><span class="sub">' + esc(n.a) +
    ' · ' + D.strati[n.s].label.toLowerCase() + ' · ' + n.g + ' collegamenti</span>';
  nube.style.display = 'block';
  nube.style.left = Math.min(W - 210, e.clientX + 14) + 'px';
  nube.style.top = (e.clientY + 16) + 'px';
});
tela.addEventListener('wheel', e => {
  e.preventDefault();
  distObiettivo = Math.max(3.2, Math.min(30, distObiettivo * (e.deltaY > 0 ? 1.11 : 0.9)));
}, {passive: false});
tela.addEventListener('click', e => {
  if (mosso) return;
  const i = sotto(e.clientX, e.clientY);
  i === null ? chiudi() : apri(i);
});
tela.addEventListener('dblclick', e => {
  const i = sotto(e.clientX, e.clientY);
  if (i !== null) { apri(i); vola(i); }
});

/* Touch: un dito ruota, due dita zoomano. */
let td = null;
tela.addEventListener('touchstart', e => {
  rotante = false; segnaGira();
  if (e.touches.length === 1) { ux = e.touches[0].clientX; uy = e.touches[0].clientY; td = null; }
  else if (e.touches.length === 2) td = distanzaDita(e);
}, {passive: true});
tela.addEventListener('touchmove', e => {
  e.preventDefault();
  if (e.touches.length === 1 && td === null) {
    angY += (e.touches[0].clientX - ux) * 0.0062;
    angX = Math.max(-1.5, Math.min(1.5, angX + (e.touches[0].clientY - uy) * 0.0062));
    ux = e.touches[0].clientX; uy = e.touches[0].clientY;
  } else if (e.touches.length === 2) {
    const d = distanzaDita(e);
    if (td) distObiettivo = Math.max(3.2, Math.min(30, distObiettivo * (td/d)));
    td = d;
  }
}, {passive: false});
const distanzaDita = e => Math.hypot(
  e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);

addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') { if (e.key === 'Escape') e.target.blur(); return; }
  const k = e.key.toLowerCase();
  if (e.key === 'Escape') chiudi();
  else if (k === 'l') lente();
  else if (k === 'r') gira();
  else if (k === '/') { e.preventDefault(); document.getElementById('cerca').focus(); }
  else if (e.key === 'ArrowLeft')  angY -= 0.09;
  else if (e.key === 'ArrowRight') angY += 0.09;
  else if (e.key === 'ArrowUp')    angX = Math.max(-1.5, angX - 0.07);
  else if (e.key === 'ArrowDown')  angX = Math.min(1.5, angX + 0.07);
  else if (e.key === '+' || e.key === '=') distObiettivo = Math.max(3.2, distObiettivo*0.85);
  else if (e.key === '-') distObiettivo = Math.min(30, distObiettivo*1.18);
});

/* --- Pannello di dettaglio ------------------------------------------------ */
const esc = s => String(s).replace(/[<>&"]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]));

function apri(i) {
  scelto = i; insiemeLente = intorno(i, 2);
  const n = D.nodi[i], st = D.strati[n.s];
  document.getElementById('dNome').textContent = n.n;
  document.getElementById('dVia').textContent = n.f;
  document.getElementById('dTag').innerHTML =
    `<span class="tag" style="border-color:${n.c}66;color:${n.c}">${esc(n.a)}</span>` +
    `<span class="tag" style="border-color:${st.colore}66;color:${st.colore}">${esc(st.label)}</span>` +
    `<span class="tag">${n.g} collegamenti</span>` +
    `<span class="tag">${intorno(i,2).size - 1} nodi a 2 passi</span>`;

  const perRel = {};
  vicini[i].forEach(v => { const r = D.archi[v.i].r; (perRel[r] = perRel[r] || []).push(v.j); });

  let h = '';
  if (n.sez.length) h += '<h3>Dentro questo file · ' + n.sez.length + '</h3><ul>' +
    n.sez.map(s => '<li>' + esc(s) + '</li>').join('') + '</ul>';
  Object.keys(perRel).sort((a,b) => (info(b).forte|0)-(info(a).forte|0) || a.localeCompare(b))
    .forEach(r => {
      const lista = perRel[r], I = info(r);
      h += `<h3 style="color:${I.c}">${esc(I.l)} · ${lista.length}</h3><ul>` +
        lista.slice(0, 18).map(j =>
          `<li class="link" onclick="apri(${j});vola(${j})">${esc(D.nodi[j].n)}` +
          `<span class="dove"> — ${esc(D.nodi[j].a)} · ${esc(D.strati[D.nodi[j].s].label.toLowerCase())}</span></li>`
        ).join('') +
        (lista.length > 18 ? `<li class="dove">…e altri ${lista.length-18}</li>` : '') + '</ul>';
    });
  if (!h) h = '<h3>Nessun collegamento</h3><ul><li>Nodo isolato: nessun altro file lo raggiunge.</li></ul>';
  document.getElementById('dCorpo').innerHTML = h;
  document.getElementById('det').classList.add('aperto');
}
function vola(i) {
  const n = D.nodi[i];
  miraObiettivo = {x: n.x, y: n.y, z: n.z};
  distObiettivo = Math.min(distObiettivo, 7.5);
  rotante = false; segnaGira();
}
function chiudi() {
  scelto = null; insiemeLente = null;
  miraObiettivo = {x:0, y:0, z:0};
  document.getElementById('det').classList.remove('aperto');
}

/* --- Comandi -------------------------------------------------------------- */
function interruttore(dove, chiave, testo, colore, insieme, quadrato) {
  const d = document.createElement('div'); d.className = 'riga';
  d.innerHTML = `<span class="bollo${quadrato?' q':''}" style="background:${colore}"></span><span>${testo}</span>`;
  d.onclick = () => { insieme.has(chiave) ? insieme.delete(chiave) : insieme.add(chiave);
                      d.classList.toggle('spenta', !insieme.has(chiave)); };
  dove.appendChild(d); return d;
}
Object.entries(D.strati).forEach(([k, st]) =>
  interruttore(document.getElementById('fStrati'), k, st.label, st.colore, strati));
D.aree.forEach(a => {
  const q = D.conta[a] || 0;
  interruttore(document.getElementById('fAree'), a,
    `${a} <span class="num">${q}</span>`, D.colori[a] || '#7c8aa0', aree);
});
relUsate.forEach(r => interruttore(document.getElementById('fRel'), r,
  info(r).l, info(r).c, relAttive));

const campo = document.getElementById('cerca'), esiti = document.getElementById('esiti');
campo.addEventListener('input', e => {
  filtro = e.target.value.trim().toLowerCase();
  const trovati = D.nodi.filter(n => acceso(n) && combacia(n));
  esiti.textContent = !filtro ? '' :
    (trovati.length ? trovati.length + ' file — Invio per volarci' : 'nessun file');
});
campo.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const i = D.nodi.findIndex(n => acceso(n) && combacia(n) && filtro);
  if (i >= 0) { apri(i); vola(i); }
});

function posa(quale) {
  rotante = false; segnaGira();
  if (quale === 'obliqua') { angX = -0.40; angY = 0.55; distObiettivo = 14.0; }
  if (quale === 'sezione') { angX = 0.0;   angY = 0.55; distObiettivo = 15.0; }  // gli strati di taglio
  if (quale === 'alto')    { angX = -1.44; angY = 0.0;  distObiettivo = 16.0; }  // la ruota delle aree
  miraObiettivo = {x:0, y:0, z:0};
}
function lente() {
  conLente = !conLente;
  document.getElementById('bLente').classList.toggle('on', conLente);
}
function gira() { rotante = !rotante; segnaGira(); }
function segnaGira() { document.getElementById('bGira').classList.toggle('on', rotante); }
segnaGira();

anima();
</script></body></html>
"""


def main():
    if not os.path.exists(GRAFO):
        sys.exit("graphify-out/graph.json assente: esegui prima 'graphify update .'")
    dati = costruisci()
    testo = html(dati).replace("__R_MIN__", str(R_MIN)).replace("__R_MAX__", str(R_MAX))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)

    peso = os.path.getsize(OUT) / 1024
    per_strato = {}
    for n in dati["nodi"]:
        per_strato[n["s"]] = per_strato.get(n["s"], 0) + 1
    print(f"Atlante 3D: {len(dati['nodi'])} nodi-file, {len(dati['archi'])} relazioni "
          f"({peso:.0f} KB) -> graphify-out/graph-atlas.html")
    print(f"  strati: { {k: per_strato.get(k, 0) for k in STRATI} }")
    print(f"  aree:   {dict(sorted(dati['conta'].items(), key=lambda x: -x[1]))}")
    print("  layout: altezza=strato · spicchio=area · raggio=centralita (deterministico)")


if __name__ == "__main__":
    main()
