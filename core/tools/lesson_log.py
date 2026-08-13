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

sys.path.insert(0, ROOT)
try:
    from tools.brain import BRAIN            # dove vive il CONTENUTO
except ImportError:
    BRAIN = ROOT                             # istanza autosufficiente


LOG = os.path.join(BRAIN, "engine", "lessons.jsonl")

ESITI = ("utile", "vicolo-cieco", "corretto", "aperto")

# --- L'ANCORA: la difesa contro l'autofagia -------------------------------
# Un brain che impara dalla prosa che il modello ha scritto amplifica i propri
# errori a ogni giro: e' il modo in cui una memoria artificiale degenera. La
# difesa non e' filtrare meglio, e' RICHIEDERE UN APPIGLIO ESTERNO. Una lezione
# entra nel digest solo se nomina qualcosa che esiste fuori dal discorso del
# modello e che qualcun altro puo' andare a controllare.
ANCORE = {
    "test":    "un test passato da rosso a verde (nome del test)",
    "errore":  "un comando fallito, col messaggio o l'exit code",
    "misura":  "un numero misurato, con l'unita e come e stato ottenuto",
    "utente":  "una correzione esplicita dell'utente (cosa ha detto)",
    "guardia": "una guardia del brain che ha fermato qualcosa (quale)",
}
# Ancore verificate da qualcun altro per costruzione: valgono da sole, senza
# aspettare che il caso si ripeta.
ANCORE_FORTI = ("utente", "guardia")

# Tetti di lunghezza. Il formato a tre slot NON serve a scrivere di meno: serve a
# scrivere il pezzo che si rilegge. Alla rilettura la domanda e sempre e solo
# "questa vale adesso?", e a quella risponde SOLO 'quando'. Un paragrafo di prosa
# la seppellisce; tre campi corti la mettono in prima riga.
MAX_QUANDO, MAX_ALLORA, MAX_ANCORA = 160, 220, 200


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


def main():
    # Console Windows (cp1252): vedi tools/console.py.
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool

    ap = argparse.ArgumentParser(description="Registra una lezione appresa nel brain")
    ap.add_argument("--skill", required=True, help="aion | triage | oracle | report | manuale | <altro>")
    ap.add_argument("--domanda", required=True, help="il contesto: cosa si stava cercando di fare")
    ap.add_argument("--esito", default="utile", choices=ESITI)
    ap.add_argument("--nodi", default="", help="CSV dei nodi/pagine del grafo che sono serviti")
    ap.add_argument("--nota", default="", help="la lezione in una frase (cosa ricordare la prossima volta)")
    ap.add_argument("--tag", default="", help="CSV di parole chiave")
    ap.add_argument("--ts", default=None, help="timestamp ISO (default: adesso)")
    ap.add_argument("--quando", default="", help="il segnale che fa scattare la regola")
    ap.add_argument("--allora", default="", help="cosa fare quando quel segnale compare")
    ap.add_argument("--ancora", default="",
                    help="appiglio esterno: " + " | ".join(f"{k}:..." for k in ANCORE))
    ap.add_argument("--supera", default="",
                    help="ts della lezione che questa sostituisce (non la cancella)")
    a = ap.parse_args()

    if not re.match(r"^[a-z0-9][a-z0-9_-]{0,30}$", a.skill):
        sys.exit("--skill deve essere kebab/snake case ascii")

    tipo_ancora = ""
    if a.ancora.strip():
        tipo_ancora = a.ancora.split(":", 1)[0].strip().lower()
        if tipo_ancora not in ANCORE:
            sys.exit("--ancora deve iniziare con uno di questi tipi:\n  " +
                     "\n  ".join(f"{k}: {d}" for k, d in ANCORE.items()))
        if len(a.ancora.split(":", 1)[-1].strip()) < 8:
            sys.exit("--ancora troppo vaga: deve dire QUALE test, QUALE errore, QUALE misura")

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
    if a.quando.strip():
        voce["quando"] = a.quando.strip()[:MAX_QUANDO]
    if a.allora.strip():
        voce["allora"] = a.allora.strip()[:MAX_ALLORA]
    if a.ancora.strip():
        voce["ancora"] = a.ancora.strip()[:MAX_ANCORA]
        voce["ancora_tipo"] = tipo_ancora
    if a.supera.strip():
        voce["supera"] = a.supera.strip()[:40]

    # Il livello decide COSA finisce sotto gli occhi del modello prima di ogni risposta.
    # Senza appiglio esterno una registrazione resta osservazione: conservata, cercabile,
    # ma mai promossa a prior del ragionamento.
    voce["livello"] = "lezione" if voce.get("ancora") else "osservazione"

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(voce, ensure_ascii=False) + "\n")

    print(f"{voce['livello']} registrata ({voce['esito']}) — {len(voce['nodi'])} nodi, "
          f"skill '{voce['skill']}'")
    if voce["livello"] == "osservazione":
        print("  senza --ancora resta OSSERVAZIONE: conservata e cercabile, ma non entra")
        print("  in engine/LESSONS.md, che il reasoner legge prima di ogni risposta.")
        print("  Per promuoverla serve un appiglio esterno: " + ", ".join(ANCORE))
    elif voce["ancora_tipo"] in ANCORE_FORTI:
        print(f"  ancora '{voce['ancora_tipo']}': verificata da altri, consolida subito.")
    else:
        print(f"  ancora '{voce['ancora_tipo']}': consolida quando il caso si ripete.")
    print("  consolida con: python tools/lessons_digest.py")


if __name__ == "__main__":
    main()
