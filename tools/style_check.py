# -*- coding: utf-8 -*-
"""
altair-brain — verifica stilometrica dei testi che il brain produce.

COSA FA: mette la perizia stilometrica di BookForge al servizio di TUTTO il brain,
non solo dei libri. Il brain scrive gia parecchio — report editoriali, pagine wiki,
note di metodo — e finora nessuno controllava se quella prosa suonasse artificiale.
BookForge ha risolto il problema per i romanzi: qui lo si estende a ogni testo.

FONTE UNICA, NIENTE COPIE. Il motore e lo script canonico dell'area creativita
(raw/creativita/bookforge/stylometry.py): questo modulo lo IMPORTA, non lo duplica.
Se BookForge aggiorna la sua analisi, il brain la eredita senza allineamenti manuali —
la stessa regola per cui esiste tools/frontmatter.py invece di sette parser gemelli.

DUE CLASSI DI SEGNALE (da references/scrittura.md §Step 5, dottrina BookForge):
- OGGETTIVA, si corregge sempre: anglicismi e calchi dall'inglese, ripetizioni
  verbatim di bigrammi/trigrammi.
- INDIZIARIA, solo segnalazione: ASL, flag anglo-tradotto, tic da LLM. Dice DOVE
  guardare; se intervenire lo decide la rilettura. L'orecchio batte i numeri.

Uso:
  python tools/style_check.py reports/altair-brain-iran-2026.html
  python tools/style_check.py wiki/creativita/styledna.md --json
  python tools/style_check.py --report altair-brain-iran-2026   (estrae la prosa dal DB)
"""
import argparse, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTORE = os.path.join(ROOT, "raw", "creativita", "bookforge", "stylometry.py")


def carica_motore():
    """Importa lo script canonico di BookForge come modulo (una sola implementazione)."""
    if not os.path.exists(MOTORE):
        return None
    spec = importlib.util.spec_from_file_location("bookforge_stylometry", MOTORE)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


def testo_da_file(path):
    """Estrae la PROSA da md/txt/html: i tag e il front-matter non sono scrittura."""
    with open(path, encoding="utf-8") as f:
        grezzo = f.read()
    if path.endswith((".html", ".htm")):
        grezzo = re.sub(r"<script.*?</script>|<style.*?</style>", " ", grezzo, flags=re.S | re.I)
        grezzo = re.sub(r"<[^>]+>", " ", grezzo)
        grezzo = re.sub(r"&[a-z]+;|&#\d+;", " ", grezzo)
    if path.endswith(".md"):
        sys.path.insert(0, ROOT)
        from tools.frontmatter import dividi
        _, grezzo = dividi(grezzo)
        grezzo = re.sub(r"```.*?```", " ", grezzo, flags=re.S)      # blocchi di codice
        # Anche il codice IN RIGA e' identificatore, non prosa: un percorso di file
        # ripetuto in un elenco veniva contato come ripetizione stilistica.
        grezzo = re.sub(r"`[^`\n]+`", " ", grezzo)
        # Le parole tra virgolette caporali sono di QUALCUN ALTRO. Chiedere di
        # correggere un anglicismo dentro una citazione significa chiedere di
        # falsificare la fonte.
        grezzo = re.sub(r"«[^»]*»", " ", grezzo)
        grezzo = re.sub(r"^\s*[|#>\-*].*$", " ", grezzo, flags=re.M)  # tabelle, titoli, liste
        # Il BERSAGLIO di un wikilink e un identificatore, non una parola scelta da
        # chi scrive: tenerlo faceva contare 'feature-engineering' come anglicismo e
        # chiedeva di correggere il NOME di una pagina. Una classe "correggi sempre"
        # che segnala nomi di file smette di essere obbedibile.
        grezzo = re.sub(r"\[\[[^\]]+\]\]", " ", grezzo)
    return re.sub(r"[ \t]+", " ", grezzo).strip()


def testo_da_report(nome):
    """La prosa editoriale di un report living sta nel database, non nell'HTML."""
    p = os.path.join(ROOT, "reports", "data", f"{nome}.updates.json")
    if not os.path.exists(p):
        sys.exit(f"report inesistente: {p}")
    with open(p, encoding="utf-8") as f:
        db = json.load(f)
    pezzi = []
    for chiave in ("verdetto", "conclusioni"):
        sez = db.get(chiave) or {}
        if sez.get("corrente"):
            pezzi.append(sez["corrente"])
        pezzi += [v.get("testo", "") for v in sez.get("storia", [])]
    for voci in (db.get("nodi") or {}).values():
        pezzi += [v.get("testo", "") for v in voci]
    testo = " ".join(pezzi)
    return re.sub(r"<[^>]+>", " ", testo)


def analizza(testo, lang="it"):
    mod = carica_motore()
    if mod is None:
        return None
    # lo script espone la sua analisi come funzione o come main: si prova la via pulita
    for nome in ("analyze", "analizza", "run_analysis", "build_report"):
        fn = getattr(mod, nome, None)
        if callable(fn):
            try:
                return fn(testo, lang)
            except TypeError:
                try:
                    return fn(testo)
                except Exception:
                    pass
    return "USA_CLI"


def analizza_via_cli(testo, lang="it"):
    """Ripiego robusto: lo script come processo separato, sul suo contratto pubblico."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as f:
        f.write(testo)
        tmp = f.name
    try:
        p = subprocess.run([sys.executable, MOTORE, tmp, "--lang", lang, "--json"],
                           capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace")
        if p.returncode != 0:
            return {"errore": (p.stderr or "")[:300]}
        return json.loads(p.stdout)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def riassumi(d):
    """Il verdetto leggibile: prima cio che si corregge sempre, poi cio che si guarda."""
    if not d or "errore" in (d or {}):
        return ["analisi non disponibile: " + str((d or {}).get("errore", "motore assente"))]
    r = []
    m = d.get("metrics", {})
    r.append(f"{m.get('words', 0)} parole · {m.get('sentences', 0)} frasi · "
             f"lunghezza media {m.get('avg_sentence_length', 0)}")

    ir = d.get("italian_register", {})
    if ir.get("anglo_translated_flag"):
        r.append(f"[INDIZIARIO] registro: {ir.get('severity')} — prosa frantumata, "
                 f"sa di traduzione dall'inglese. Cura: ri-legare dove serve (piu virgole, "
                 f"subordinate), NON allungare per principio.")

    ang = d.get("anglicism_scan", {})
    trovati = []
    for v in (ang.values() if isinstance(ang, dict) else []):
        if not isinstance(v, list):
            continue
        for x in v:
            if isinstance(x, dict) and x.get("term"):
                sugg = x.get("suggerito") or x.get("suggested") or "?"
                trovati.append(f"{x['term']}→{sugg} ({x.get('conteggio', 1)}x)")
            elif x:
                trovati.append(str(x))
    if trovati:
        r.append(f"[OGGETTIVO] anglicismi/calchi: {', '.join(trovati[:6])}"
                 + (f" e altri {len(trovati) - 6}" if len(trovati) > 6 else ""))

    tic = d.get("tic_detection", {})
    rip = (tic.get("repeated_bigrams") or []) + (tic.get("repeated_trigrams") or [])
    if rip:
        leggibili = [f"«{t}» {n}x" if isinstance(t, str) else str(t)
                     for t, n in (x if isinstance(x, (list, tuple)) and len(x) == 2
                                  else (x, "?") for x in rip[:4])]
        r.append(f"[OGGETTIVO] ripetizioni verbatim: {', '.join(leggibili)}")

    llm = d.get("llm_tics", {})
    accesi = [k for k, v in llm.items()
              if isinstance(v, dict) and v.get("warn")]
    if accesi:
        r.append(f"[INDIZIARIO] tic da LLM sopra soglia: {', '.join(accesi)} "
                 f"— correggi solo quelli che alla rilettura suonano in posa")

    if len(r) == 1:
        r.append("Nessun segnale: prosa pulita secondo le spie disponibili.")
    return r


def main():
    sys.path.insert(0, ROOT)
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool      # vedi tools/console.py: quarto tool colpito dallo stesso guasto

    ap = argparse.ArgumentParser(description="Verifica stilometrica dei testi del brain")
    ap.add_argument("file", nargs="?", help="file da analizzare (md, txt, html)")
    ap.add_argument("--report", help="analizza la prosa editoriale di un report living")
    ap.add_argument("--lang", default="it")
    ap.add_argument("--json", action="store_true", help="output grezzo completo")
    a = ap.parse_args()

    if not os.path.exists(MOTORE):
        sys.exit("motore assente: manca raw/creativita/bookforge/stylometry.py")

    if a.report:
        testo, etichetta = testo_da_report(a.report), f"report {a.report}"
    elif a.file:
        if not os.path.exists(a.file):
            sys.exit(f"file inesistente: {a.file}")
        testo, etichetta = testo_da_file(a.file), a.file
    else:
        ap.error("serve un file oppure --report")

    if len(testo.split()) < 50:
        sys.exit(f"testo troppo breve ({len(testo.split())} parole): "
                 f"sotto le ~50 le misure non sono affidabili")

    d = analizza(testo, a.lang)
    if d == "USA_CLI" or d is None:
        d = analizza_via_cli(testo, a.lang)

    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return
    print(f"== VERIFICA STILOMETRICA — {etichetta} ==\n")
    for riga in riassumi(d):
        print(" ", riga)
    print("\n  Dottrina: wiki/creativita/anti-ai.md (cosa toglie vita alla prosa)")
    print("  Regola sovrana: se una frase va riletta per capirla, va riscritta piu semplice.")


if __name__ == "__main__":
    main()
