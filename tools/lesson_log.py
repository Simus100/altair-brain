# -*- coding: utf-8 -*-
"""
altair-brain — registro append-only delle lezioni apprese (P1: feedback loop).

PROBLEMA RISOLTO: il loop di apprendimento esisteva (graphify save-result/reflect) ma
richiedeva un'azione manuale che nessuno ricordava: in 20 giorni era stata salvata una
sola sessione. Qui la registrazione diventa un gesto unico, atomico e a costo zero,
richiamabile a fine di ogni skill.

MODELLO (ispirato ad A-MEM, arXiv 2502.12110): ogni lezione e una nota atomica con
attributi strutturati — contesto (domanda), collegamenti (nodi del grafo), esito, tag.
L'aggregazione emergente la fa tools/lessons_digest.py.

Il file e JSONL append-only: nessuna riscrittura, nessuna perdita, diff git leggibili.

Uso:
  python tools/lesson_log.py --skill aion --domanda "..." --esito utile \
      --nodi AION_SUPERIA,AION_ETHOS --nota "il gate ETHOS ha bloccato X" --tag governance
"""
import argparse, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Console Windows (cp1252): vedi tools/console.py. Attivo SOLO da riga di comando,
# per non toccare i flussi di chi importa questo modulo (test compresi).
if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

LOG = os.path.join(ROOT, "engine", "lessons.jsonl")

ESITI = ("utile", "vicolo-cieco", "corretto", "aperto")


def _lista(val: str) -> list:
    """CSV -> lista pulita. Rifiuta valori che iniziano con '-' (argument injection:
    stessa classe di problema gia corretta in server/brain_core.py)."""
    out = []
    for x in (val or "").split(","):
        x = x.strip()
        if not x:
            continue
        if x.startswith("-"):
            sys.exit(f"valore non ammesso (inizia con '-'): {x!r}")
        out.append(x[:120])
    return out


ap = argparse.ArgumentParser(description="Registra una lezione appresa nel brain")
ap.add_argument("--skill", required=True, help="aion | triage | oracle | report | manuale | <altro>")
ap.add_argument("--domanda", required=True, help="il contesto: cosa si stava cercando di fare")
ap.add_argument("--esito", default="utile", choices=ESITI)
ap.add_argument("--nodi", default="", help="CSV dei nodi/pagine del grafo che sono serviti")
ap.add_argument("--nota", default="", help="la lezione in una frase (cosa ricordare la prossima volta)")
ap.add_argument("--tag", default="", help="CSV di parole chiave")
ap.add_argument("--ts", default=None, help="timestamp ISO (default: adesso)")
a = ap.parse_args()

if not re.match(r"^[a-z0-9][a-z0-9_-]{0,30}$", a.skill):
    sys.exit("--skill deve essere kebab/snake case ascii")

voce = {
    "ts": a.ts or datetime.datetime.now().replace(microsecond=0).isoformat(),
    "skill": a.skill,
    "domanda": a.domanda.strip()[:400],
    "esito": a.esito,
    "nodi": _lista(a.nodi),
    "tag": _lista(a.tag),
}
if a.nota.strip():
    voce["nota"] = a.nota.strip()[:600]

os.makedirs(os.path.dirname(LOG), exist_ok=True)
with open(LOG, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(voce, ensure_ascii=False) + "\n")

print(f"lezione registrata ({voce['esito']}) — {len(voce['nodi'])} nodi, skill '{voce['skill']}'")
print("  consolida con: python tools/lessons_digest.py")
