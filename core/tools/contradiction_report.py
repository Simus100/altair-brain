# -*- coding: utf-8 -*-
"""
altair-brain — candidati a contraddizione fra note diverse (rapporto, non guardia).

PERCHE' ESISTE. Il lint del brain era tutto strutturale: coesione del grafo, link
rotti, nodi orfani, freschezza, provenienza. Nessuno guardava se due note dicono cose
diverse sulla stessa cosa. Il pattern LLM Wiki mette il controllo delle
contraddizioni fra le operazioni di manutenzione di base; qui mancava.

COME, SENZA LLM. Deterministico e volutamente prudente: si cercano AFFERMAZIONI
NUMERICHE con un'unita' ("... e' al 4,50 per cento", "... dura 3 anni", "... costa
120 euro"), si riduce il soggetto alle sue ultime parole piene, e si segnalano i
soggetti che in note DIVERSE hanno valori diversi con la stessa unita'. Non si
segnala nulla che il brain abbia gia' risolto: la nota scaduta (valid_until) o
collegata all'altra da superseded_by e' una storia, non una contraddizione.

E' un RAPPORTO, non una guardia: un'euristica lessicale sbaglia per costruzione, e
una guardia che sbaglia insegna a ignorarla. Serve a chi cura il brain per sapere
dove guardare. Esce sempre 0.

Uso:  python tools/contradiction_report.py            (i primi 20 candidati)
      python tools/contradiction_report.py --json
"""
import argparse, datetime, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN
except ImportError:
    BRAIN = ROOT
from tools import frontmatter as fm  # noqa: E402

UNITA = {
    "%": "%", "per cento": "%", "percento": "%",
    "euro": "euro", "€": "euro", "dollari": "dollari", "$": "dollari",
    "anni": "anni", "anno": "anni", "mesi": "mesi", "mese": "mesi",
    "giorni": "giorni", "giorno": "giorni", "ore": "ore",
    "punti": "punti", "punti base": "punti base",
    "milioni": "milioni", "miliardi": "miliardi",
    "km": "km", "kg": "kg", "°c": "°C", "gradi": "gradi",
}
VUOTE = set("il lo la i gli le un uno una di a da in con su per tra fra e o che del dello "
            "della dei degli delle al allo alla ai agli alle dal dallo dalla dai dagli "
            "dalle nel nello nella nei negli nelle sul sullo sulla sui sugli sulle "
            "circa oltre quasi solo ancora gia' sempre".split())
# Come il corpus scrive davvero i numeri (campionato: 98 righe con numero e unita'):
# "pari al 27,20%", "Debito/PIL italiano: 116,5%", "stimati al 75%", "rappresentano il
# 50,52%", "e' sceso al 2,00 per cento". Il primo modello voleva un verbo subito prima
# del numero ed estraeva UN fatto da tutto il brain: un rapporto sempre vuoto non e' un
# rapporto pulito, e' un rapporto cieco.
LEGAME = (r"(?:e'|è|era|sono|erano|resta|rimane|vale|valgono|costa|costano|dura|durano|"
          r"pesa|arriva|sale|scende|pari|stimat[oaie]|rappresent[a-z]+|raggiung[a-z]+|"
          r"supera|superano|conta|contano|:|=)")
FATTO = re.compile(
    r"(?P<soggetto>(?:[A-Za-zÀ-ÿ'/]+\s+){0,5}[A-Za-zÀ-ÿ'/]+)\s*,?\s*" + LEGAME +
    r"\s*(?:(?:a|al|allo|alla|il|lo|la|i|gli|le|di|del|circa|oltre|quasi|sceso|salito|fermo)\s+)*"
    r"(?P<valore>\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?)\s*"
    r"(?P<unita>per cento|percento|punti base|%|€|\$|euro|dollari|anni|mesi|giorni|ore|"
    r"punti|milioni|miliardi|km|kg|°c|gradi)(?![A-Za-zÀ-ÿ])",
    re.IGNORECASE)
ANNO = re.compile(r"\b(19\d{2}|20\d{2})\b")
# Righe che non sono affermazioni: codice, stile, tabelle, attributi SVG.
NON_PROSA = re.compile(r"[{};<>|]|\bpx\b|stop-color|offset=|gradient", re.IGNORECASE)


def _soggetto(testo):
    parole = [p for p in re.findall(r"[a-zà-ÿ']+", testo.lower()) if p not in VUOTE]
    return " ".join(parole[-3:])


def _valore(v):
    """'1.338' -> 1338, '27,20' -> 27.2, '4.5' -> 4.5 (punto decimale all'inglese)."""
    if "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", v):
        return float(v.replace(".", ""))
    return float(v)


def fatti(brain=None):
    """[(soggetto, unita, valore, file, frase)] dalle note scritte a mano e valide oggi."""
    brain = brain or BRAIN
    oggi = datetime.date.today().isoformat()
    fuori, successori = [], {}
    for strato in ("raw", "wiki"):
        # anche i .txt: le note di data-science sono .txt, e graphify non le vede. Il
        # primo rapporto aveva lo stesso punto cieco che la ricerca aveva gia' chiuso.
        percorsi = sorted(glob.glob(os.path.join(brain, strato, "**", "*.md"), recursive=True) +
                          glob.glob(os.path.join(brain, strato, "**", "*.txt"), recursive=True))
        for p in percorsi:
            rel = os.path.relpath(p, brain).replace("\\", "/")
            if fm.e_generato(rel) or rel.startswith("raw/_inbox/"):
                continue
            meta, corpo = fm.leggi(p)
            meta = meta or {}
            if meta.get("superseded_by"):
                successori[rel] = meta["superseded_by"].strip()
            if (meta.get("valid_until") or "9999") < oggi:
                continue                      # scaduto: e' storia, non contraddizione
            for frase in re.split(r"(?<=[.;!?])\s+|\n", corpo):
                if NON_PROSA.search(frase):
                    continue
                anni = sorted(set(ANNO.findall(frase)))
                for m in FATTO.finditer(frase):
                    sogg = _soggetto(m.group("soggetto"))
                    if len(sogg.split()) < 2:
                        continue              # "costa 3 euro": di cosa? troppo vago
                    # Una frase datata parla di QUELL'anno: 116,5% nel 2011 e 131,8% nel
                    # 2017 sono una serie storica, non una contraddizione.
                    if anni:
                        sogg = f"{sogg} [{'/'.join(anni)}]"
                    try:
                        val = _valore(m.group("valore"))
                    except ValueError:
                        continue
                    fuori.append((sogg, UNITA.get(m.group("unita").lower(), m.group("unita")),
                                  val, rel, frase.strip()[:160]))
    return fuori, successori


def candidati(brain=None):
    elenco, successori = fatti(brain)
    per_chiave = {}
    for sogg, unita, val, rel, frase in elenco:
        per_chiave.setdefault((sogg, unita), []).append((val, rel, frase))
    fuori = []
    for (sogg, unita), voci in sorted(per_chiave.items()):
        per_file = {}
        for val, rel, frase in voci:
            per_file.setdefault(rel, (val, frase))
        if len(per_file) < 2 or len({v for v, _ in per_file.values()}) < 2:
            continue
        coppie = []
        file = sorted(per_file)
        for i, a in enumerate(file):
            for b in file[i + 1:]:
                if per_file[a][0] == per_file[b][0]:
                    continue
                if successori.get(a) == b or successori.get(b) == a:
                    continue                  # gia' risolta: una sostituisce l'altra
                coppie.append((a, b))
        if coppie:
            fuori.append({"soggetto": sogg, "unita": unita,
                          "valori": {f: {"valore": v, "frase": fr}
                                     for f, (v, fr) in sorted(per_file.items())},
                          "coppie": coppie})
    return fuori


def main():
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Candidati a contraddizione fra note")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max", type=int, default=20)
    a = ap.parse_args()
    c = candidati()
    if a.json:
        print(json.dumps(c, ensure_ascii=False, indent=2))
        return 0
    if not c:
        print("Contraddizioni: nessun candidato (stesso soggetto, stessa unita', valori "
              "diversi in note diverse e non collegate da superseded_by).")
        return 0
    print(f"Contraddizioni: {len(c)} candidati da verificare (euristica: rapporto, non verdetto)")
    for voce in c[:a.max]:
        print(f"\n  «{voce['soggetto']}» ({voce['unita']})")
        for f, d in voce["valori"].items():
            print(f"    {d['valore']:g} — {f}: {d['frase'][:100]}")
    print("\nSe uno dei due fatti e' superato: valid_until + superseded_by nella nota vecchia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
