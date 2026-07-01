# -*- coding: utf-8 -*-
"""
altair-brain — AION_Oracle eseguibile: lancio I Ching deterministico (seedabile).

Logica fedele a raw/aion/aion-oracle.md (Sezione 1):
- 6 valori in {6,7,8,9} dal basso verso l'alto (linea 1 = bit sinistro)
- 6 = yin mobile (bit 0, muta in yang), 7 = yang stabile (1),
  8 = yin stabile (0), 9 = yang mobile (bit 1, muta in yin)
- ID esagramma via tabella lookup Re Wen (MAI binario+1)
- Regole linee mobili: 1 -> quella; 2 -> la yin (se stesso tipo: la piu bassa,
  convenzione documentata); 3 -> la mediana; 4 -> la piu alta fissa; 5 -> la fissa
  rimanente (estensione coerente della regola 4, non nel testo originale);
  6 -> ignora il primo esagramma, consulta il secondo.

Uso come modulo:  from tools.oracle_cast import cast_reading, get_hexagram
Uso da CLI:       python tools/oracle_cast.py [--seed N] [--question "..."]
"""
import json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "engine", "iching.db.json")
_db = None


def _load():
    global _db
    if _db is None:
        with open(DB_PATH, encoding="utf-8") as f:
            _db = json.load(f)
        _db["_by_id"] = {e["id"]: e for e in _db["esagrammi"]}
    return _db


def get_hexagram(hid: int) -> dict:
    db = _load()
    e = db["_by_id"].get(int(hid))
    if not e:
        raise KeyError(f"esagramma {hid} inesistente (range 1-64)")
    return e


def _to_binary(lanci):
    # linea 1 = bit piu a sinistra; 6,8 -> 0 (yin); 7,9 -> 1 (yang)
    return "".join("1" if v in (7, 9) else "0" for v in lanci)


def _mutate(lanci):
    # 6 -> 7 (yin mobile diventa yang), 9 -> 8 (yang mobile diventa yin)
    return [7 if v == 6 else 8 if v == 9 else v for v in lanci]


def _focus_line(lanci, mobili):
    """Applica le regole di selezione della linea da interpretare. Ritorna (posizione, regola)."""
    n = len(mobili)
    if n == 0:
        return None, "nessuna linea mobile: si interpreta il Giudizio del primo esagramma"
    if n == 1:
        return mobili[0], "1 linea mobile: si interpreta quella"
    if n == 2:
        yin = [p for p in mobili if lanci[p - 1] == 6]
        if len(yin) == 1:
            return yin[0], "2 linee mobili (yin+yang): si sceglie la Yin"
        return min(mobili), "2 linee mobili dello stesso tipo: si sceglie la piu bassa (convenzione)"
    if n == 3:
        return sorted(mobili)[1], "3 linee mobili: si sceglie la mediana"
    if n == 4:
        fisse = [p for p in range(1, 7) if p not in mobili]
        return max(fisse), "4 linee mobili: si sceglie la piu alta fissa"
    if n == 5:
        fisse = [p for p in range(1, 7) if p not in mobili]
        return fisse[0], "5 linee mobili: si sceglie la fissa rimanente (estensione della regola 4)"
    return None, "6 linee mobili: si ignora il primo esagramma e si consulta il secondo"


def _public(e):
    return {k: v for k, v in e.items() if not k.startswith("_")}


def cast_reading(question: str = None, seed: int = None) -> dict:
    db = _load()
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    lanci = [rng.choice((6, 7, 8, 9)) for _ in range(6)]
    mobili = [i + 1 for i, v in enumerate(lanci) if v in (6, 9)]

    b1 = _to_binary(lanci)
    id1 = db["lookup_binario"][b1]
    primo = _public(get_hexagram(id1))

    secondo = None
    if mobili:
        b2 = _to_binary(_mutate(lanci))
        secondo = _public(get_hexagram(db["lookup_binario"][b2]))

    pos, regola = _focus_line(lanci, mobili)
    linea_focus = None
    if pos is not None:
        linea_focus = {"posizione": pos, **primo["linee"][pos - 1]}

    return {
        "question": question,
        "seed": seed,
        "lanci": lanci,
        "binario": b1,
        "esagramma_primario": primo,
        "linee_mobili": mobili,
        "linea_focus": linea_focus,
        "regola_applicata": regola,
        "esagramma_secondario": secondo,
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Lancio I Ching (AION_Oracle)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--question", default=None)
    ap.add_argument("--hexagram", type=int, default=None, help="mostra solo la scheda di un esagramma")
    a = ap.parse_args()
    out = get_hexagram(a.hexagram) if a.hexagram else cast_reading(a.question, a.seed)
    json.dump({k: v for k, v in out.items() if not k.startswith("_")} if a.hexagram else out,
              sys.stdout, ensure_ascii=False, indent=2)
    print()
