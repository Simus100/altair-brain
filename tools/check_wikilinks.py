# -*- coding: utf-8 -*-
"""
altair-brain — verifica la CORRETTEZZA delle relazioni nella wiki.

I wikilink [[x]] risolvono solo verso una pagina x.md nella STESSA cartella; un link a
una pagina inesistente viene scartato in silenzio da graphify -> relazione intesa ma
ROTTA. Questo tool li trova. Verifica anche la reciprocita opzionale non e richiesta.

Exit 0 = nessun link rotto; 1 = trovati link penzolanti. Uso:
  python tools/check_wikilinks.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(ROOT, "wiki")
LINK = re.compile(r"\[\[([^\]|]+)")

dangling = []
total_links = 0
for dirpath, _, files in os.walk(WIKI):
    stems = {f[:-3] for f in files if f.endswith(".md")}
    for f in files:
        if not f.endswith(".md"):
            continue
        text = open(os.path.join(dirpath, f), encoding="utf-8").read()
        for m in LINK.finditer(text):
            target = m.group(1).strip()
            total_links += 1
            if target not in stems:
                rel = os.path.relpath(os.path.join(dirpath, f), ROOT).replace("\\", "/")
                dangling.append((rel, target))

if dangling:
    print(f"WIKILINK ROTTI — {len(dangling)} su {total_links} link totali:")
    for src, tgt in dangling:
        print(f"  - {src}  ->  [[{tgt}]]  (pagina inesistente nella stessa cartella)")
    sys.exit(1)

print(f"Relazioni wiki corrette: {total_links} wikilink, 0 penzolanti.")
