# -*- coding: utf-8 -*-
"""
altair-brain — UN comando per rigenerare e verificare tutto (newbie-friendly).

Esegue in ordine l'intera pipeline del brain:
  1. wiki dal modello        (tools/gen_wiki_from_model.py)
  2. validazione modello     (tools/validate_model.py)
  3. DB oracle dal grezzo    (tools/build_iching_db.py)
  4. grafo                   (graphify update .)
  5. sottografi per area     (tools/build_area_graphs.py)
  6. vista compatta          (tools/altair_compact_view.py)
  7. salute del grafo        (tools/graph_health.py)

Uso:  python tools/rebuild_all.py        (poi: git add -A && commit && push)
Exit 0 = tutto ok; 1 = un passo e fallito (i successivi non vengono eseguiti).
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

STEPS = [
    ("wiki dal modello", [PY, "tools/gen_wiki_from_model.py"]),
    ("validazione modello", [PY, "tools/validate_model.py"]),
    ("DB oracle", [PY, "tools/build_iching_db.py"]),
    ("grafo (graphify update)", ["graphify", "update", "."]),
    ("sottografi per area", [PY, "tools/build_area_graphs.py"]),
    ("vista compatta", [PY, "tools/altair_compact_view.py"]),
    ("salute del grafo", [PY, "tools/graph_health.py"]),
]

failed = False
for name, cmd in STEPS:
    if cmd[0] == "graphify" and shutil.which("graphify") is None:
        print(f"~~ {name}: SALTATO (graphify non installato: pipx install graphifyy)")
        continue
    print(f"== {name} ==")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print(f"XX {name}: FALLITO (exit {r.returncode}) — pipeline interrotta.")
        failed = True
        break

if failed:
    sys.exit(1)
print("\n== TUTTO OK == Ora:  git add -A && git commit -m \"...\" && git push")
