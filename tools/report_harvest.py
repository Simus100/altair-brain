# -*- coding: utf-8 -*-
"""
altair-brain — riporta nel brain la conoscenza durevole dei report (F7).

IL PROBLEMA MISURATO: i report erano un SILO — zero archi tra reports/ e gli strati
di conoscenza. Ogni report prodotto porta lavoro reale (fonti verificate,
metodo di attribuzione, convenzioni editoriali) che non tornava mai indietro: sola
scrittura. Un second brain che produce e non riassorbe spreca il proprio lavoro.

COSA RACCOGLIE (non i fatti, che invecchiano: il METODO e l'ESPERIENZA, che restano):
- PROFILO DELLE FONTI: quali fonti si sono davvero usate e quanto. E' la cosa piu
  utile per il report successivo: dice su chi si e costruito, non cosa si e detto.
- CONVENZIONI EDITORIALI in uso: distribuzione delle confidenze, uso della provenienza.
- METODO ORACOLARE: quale attribuzione e stata scelta e verso cosa muta.
- ESTENSIONE TEMPORALE: da quando a quando il caso e stato seguito.

Scrive in raw/divulgazione/ perche e conoscenza di METODO comunicativo — la stessa
logica per cui data-science conserva il metodo e non i dataset.

Uso:  python tools/report_harvest.py            (anteprima)
      python tools/report_harvest.py --apply    (scrive la nota)
"""
import argparse, collections, datetime, glob, hashlib, json, os, re, sys

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

DEST = os.path.join(BRAIN, "raw", "divulgazione", "metodo-report-verificati.md")


def _voci(db):
    v = list(db.get("verdetto", {}).get("storia", []))
    v += list(db.get("conclusioni", {}).get("storia", []))
    for n in (db.get("nodi") or {}).values():
        v += n
    return v


def raccogli():
    fonti = collections.Counter()
    confidenze = collections.Counter()
    autori = collections.Counter()
    con_fonte = totali = 0
    casi = []

    for p in sorted(glob.glob(os.path.join(BRAIN, "reports", "data", "*.updates.json"))):
        with open(p, encoding="utf-8") as f:
            db = json.load(f)
        voci = _voci(db)
        if not voci:
            continue
        date = sorted(v.get("ts", "")[:10] for v in voci if v.get("ts"))
        cast = db.get("verdetto", {}).get("cast") or {}
        casi.append({
            "titolo": db.get("titolo", db.get("report", "?")),
            "voci": len(voci),
            "dal": date[0] if date else "?",
            "al": date[-1] if date else "?",
            "cast": (f"{cast['primario']['id']} {cast['primario']['nome']} -> "
                     f"{cast['secondario']['id']} {cast['secondario']['nome']}"
                     if cast.get("primario") and cast.get("secondario") else None),
            "metodo": cast.get("metodo"),
        })
        for v in voci:
            totali += 1
            if v.get("fonte"):
                con_fonte += 1
                for f_ in v["fonte"].split("·"):
                    f_ = f_.strip()
                    if f_:
                        fonti[f_] += 1
            if v.get("confidenza"):
                confidenze[v["confidenza"]] += 1
            if v.get("autore"):
                autori[v["autore"]] += 1

    return {"fonti": fonti, "confidenze": confidenze, "autori": autori,
            "con_fonte": con_fonte, "totali": totali, "casi": casi}


def componi(d):
    oggi = datetime.date.today().isoformat()
    copertura = (d["con_fonte"] / d["totali"] * 100) if d["totali"] else 0
    r = [
        "---",
        f"date: {oggi}",
        "area: divulgazione",
        "source: estratto dai report pubblicati (tools/report_harvest.py)",
        "tags: [metodo, report, fonti, verifica]",
        f"reviewed: {oggi}",
        "generato_hash: PLACEHOLDER",
        "---",
        "# Metodo dei report verificati",
        "",
        "Conoscenza di metodo estratta dai report gia pubblicati. NON contiene i fatti",
        "(invecchiano e vivono nei report): contiene come sono stati costruiti e su",
        "quali fonti ci si e appoggiati davvero — cio che serve al report successivo.",
        "",
        "## Fonti su cui il brain ha costruito",
        "",
        "Frequenza d'uso reale, non un elenco di buoni propositi: dice su chi si e",
        "poggiata l'analisi quando contava.",
        "",
        "| Fonte | Volte citata |",
        "|---|---|",
    ]
    for f, c in d["fonti"].most_common(15):
        r.append(f"| {f} | {c} |")
    r += [
        "",
        "## Convenzioni editoriali in uso",
        "",
        f"- **Copertura della provenienza**: {copertura:.0f}% delle affermazioni porta "
        f"una fonte ({d['con_fonte']} su {d['totali']}).",
    ]
    if d["confidenze"]:
        dist = ", ".join(f"{k} {v}" for k, v in d["confidenze"].most_common())
        r.append(f"- **Confidenza dichiarata per voce**: {dist}.")
    if d["autori"]:
        firme = ", ".join(f"{k} ({v})" for k, v in d["autori"].most_common(5))
        r.append(f"- **Firme**: {firme}.")
    r += [
        "- **Regola non negoziabile**: ogni affermazione con numeri o date porta la sua",
        "  fonte; la verifica e automatica (`tools/check_provenance.py --strict`).",
        "- **Fatti che invecchiano**: non si cancellano, si invalidano (`valid_until`,",
        "  `superseded_by`). La cronologia resta leggibile, la verita corrente e una.",
        "",
        "## Casi seguiti",
        "",
    ]
    for c in d["casi"]:
        r.append(f"- **{c['titolo']}** — {c['voci']} aggiornamenti, dal {c['dal']} al {c['al']}.")
        if c["cast"]:
            r.append(f"  - lettura oracolare per *{c['metodo']}*: {c['cast']}")
    r += [
        "",
        "## Metodo oracolare nei report",
        "",
        "L'esagramma NON si estrae a caso: si **attribuisce** allo stato del caso",
        "(candidati con `oracle_cast.py --cerca`), le linee mobili marcano i vettori in",
        "mutamento e il loro testo e il consiglio operativo. La mutazione produce la",
        "destinazione. Verificabile: `python tools/oracle_cast.py --attribuisci <id> --mobili <n>`.",
        "",
        "Collegati:",
        "- [[README]]",
        "",
        f"_Generato da `tools/report_harvest.py` il {oggi}. Rilanciarlo aggiorna i numeri;",
        "il testo di metodo si puo integrare a mano: e una nota grezza, non un file generato._",
    ]
    return "\n".join(r) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Riporta nel brain il metodo dei report")
    ap.add_argument("--apply", action="store_true", help="scrive la nota (default: anteprima)")
    ap.add_argument("--force", action="store_true",
                    help="sovrascrive anche se la nota e stata modificata a mano")
    a = ap.parse_args()

    d = raccogli()
    if not d["totali"]:
        print("Nessun report con aggiornamenti da cui raccogliere.")
        return

    testo = componi(d)
    print(f"Raccolto da {len(d['casi'])} report: {d['totali']} affermazioni, "
          f"{len(d['fonti'])} fonti distinte, "
          f"{d['con_fonte'] / d['totali'] * 100:.0f}% con provenienza.")
    if a.apply:
        # NON sovrascrivere il lavoro umano. La nota vive in raw/, che e lo strato
        # SORGENTE: e legittimo integrarla a mano. Rigenerarla alla cieca cancellerebbe
        # quelle integrazioni senza dirlo — la contraddizione peggiore in un sistema
        # che altrove distingue con cura cio che e generato da cio che e scritto.
        if os.path.exists(DEST) and not a.force:
            su_disco = open(DEST, encoding="utf-8").read()
            m = re.search(r"^generato_hash:\s*(\w+)", su_disco, re.M)
            atteso = hashlib.sha256(
                re.sub(r"^generato_hash:.*$", "generato_hash: ", su_disco, flags=re.M)
                .replace("generato_hash: ", "generato_hash: PLACEHOLDER")
                .replace("generato_hash: PLACEHOLDER", "").encode()).hexdigest()[:16]
            if m and m.group(1) != atteso:
                print(f"  NON SOVRASCRITTA: {os.path.relpath(DEST, BRAIN)} e stata")
                print("  modificata a mano dopo l'ultima generazione (impronta diversa).")
                print("  Integra i numeri nuovi a mano, oppure rilancia con --force.")
                return
        os.makedirs(os.path.dirname(DEST), exist_ok=True)
        with open(DEST, "w", encoding="utf-8", newline="\n") as f:
            f.write(testo)
        print(f"  scritta: {os.path.relpath(DEST, BRAIN)}")
        print("  ora rigenera il grafo:  python tools/rebuild_all.py")
    else:
        print(f"  destinazione: {os.path.relpath(DEST, BRAIN)}\n")
        print(testo[:1200] + ("\n[...]" if len(testo) > 1200 else ""))
        print("\nPer scrivere davvero:  python tools/report_harvest.py --apply")


if __name__ == "__main__":
    main()
