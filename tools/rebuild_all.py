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
  6b. vista atlante 3D       (tools/build_atlas_view.py)
  7. indice di ricerca BM25  (tools/build_search_index.py)
  8. lezioni consolidate     (tools/lessons_digest.py)
  9. metriche nel tempo      (tools/graph_metrics.py)
 10. salute del grafo        (tools/graph_health.py)

Uso:  python tools/rebuild_all.py        (poi: git add -A && commit && push)
Exit 0 = tutto ok; 1 = un passo e fallito (i successivi non vengono eseguiti).
"""
import os, shutil, subprocess, sys

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

PY = sys.executable

# Passi che hanno senso solo se il brain possiede un certo INGRESSO. Non basta
# guardare se il tool esiste: in un brain autosufficiente il tool di un training non
# adottato non c'e' e il passo si salta da solo, ma quando e' l'OFFICINA a ricostruire
# un altro brain i tool ci sono tutti — e la pipeline provava a generare la wiki di
# 'cucina' da un modello AION che quel brain non ha mai adottato, fallendo al primo
# passo. Il presupposto e' il file, non lo strumento.
INGRESSO = {
    "tools/gen_wiki_from_model.py": "engine/aion.model.json",
    "tools/validate_model.py":      "engine/aion.model.json",
    "tools/build_iching_db.py":     "raw/aion/aion-oracle.md",
    "tools/apply_bridges.py":       "engine/bridges.json",
    "tools/apply_provenance.py":    "engine/provenance.json",
}

STEPS = [
    # Prima di tutto: questo motore puo' ricostruire questo brain? Il manifesto
    # brain.json dice con quale versione e' stato verificato (tools/brain_upgrade.py).
    ("compatibilita' brain-motore", [PY, "tools/brain_upgrade.py", "--verifica"]),
    # I file che definiscono il brain, contro i loro schemi (schema/).
    ("contratti del brain", [PY, "tools/validate_contracts.py"]),
    ("wiki dal modello", [PY, "tools/gen_wiki_from_model.py"]),
    ("validazione modello", [PY, "tools/validate_model.py"]),
    ("DB oracle", [PY, "tools/build_iching_db.py"]),
    ("grafo (graphify update)", ["graphify", "update", "."]),
    ("potatura del grafo (artefatti fuori)", [PY, "tools/graph_prune.py"]),
    ("ponti intercampo", [PY, "tools/apply_bridges.py"]),
    ("provenienza fonte->conoscenza", [PY, "tools/apply_provenance.py"]),
    ("sottografi per area", [PY, "tools/build_area_graphs.py"]),
    ("vista compatta", [PY, "tools/altair_compact_view.py"]),
    ("vista atlante 3D", [PY, "tools/build_atlas_view.py"]),
    ("porta delle viste (index)", [PY, "tools/build_views_index.py"]),
    ("scheletro cedibile core/", [PY, "tools/build_core.py"]),
    # PRIMA la memoria, POI l'indice: l'indice legge engine/LESSONS.md. Nell'ordine
    # inverso indicizzava il prior del giro precedente, e ogni lezione nuova restava
    # invisibile alla ricerca fino al rebuild successivo. Lo ha scoperto la prima
    # esecuzione dei test su un brain appena esportato.
    ("lezioni consolidate", [PY, "tools/lessons_digest.py"]),
    ("indice di ricerca (BM25)", [PY, "tools/build_search_index.py"]),
    # Consolidamento offline: RIGENERA i digest per area (senza --solo-proposte, che
    # li salterebbe: incoerenza rilevata dalla guardia anti-digest-stantio in
    # graph_health). Volutamente SENZA check di coerenza in CI, a differenza degli
    # altri generati: contiene data di generazione e freschezza dei file, quindi
    # cambia col tempo per costruzione.
    ("consolidamento (digest per area)", [PY, "tools/consolidate.py"]),
    ("metriche del brain", [PY, "tools/graph_metrics.py"]),
    ("relazioni wiki (link non rotti)", [PY, "tools/check_wikilinks.py"]),
    # Rapporto, non guardia: esce sempre 0. Dice a chi cura il brain dove due note
    # danno valori diversi per la stessa cosa (tools/contradiction_report.py).
    ("contraddizioni fra note (rapporto)", [PY, "tools/contradiction_report.py"]),
    ("salute del grafo", [PY, "tools/graph_health.py"]),
    # Nell'officina: il grafo del CODICE, separato da quello della conoscenza.
    ("grafo del codice (officina)", [PY, "tools/build_code_graph.py"]),
    # Le skill per Codex e gli altri agenti: una copia GENERATA, non tenuta a mano.
    ("skill per gli altri agenti", [PY, "tools/sync_agent_skills.py"]),
]

failed = False
for name, cmd in STEPS:
    if cmd[0] == "graphify" and shutil.which("graphify") is None:
        print(f"~~ {name}: SALTATO (graphify non installato: pipx install graphifyy)")
        continue
    # Un passo il cui tool non c'e' viene SALTATO, non fa fallire la pipeline.
    # Serve perche' il motore e modulare: i passi di un training (wiki dal modello,
    # validazione, DB oracle) esistono solo se quel training e stato adottato.
    # Senza questa regola lo scheletro non partiva nemmeno una volta — e falliva al
    # primo passo, prima di dire qualsiasi cosa di utile.
    if len(cmd) > 1 and cmd[0] == PY and not os.path.exists(os.path.join(ROOT, cmd[1])):
        print(f"~~ {name}: SALTATO ({cmd[1]} non presente in questa installazione)")
        continue
    _ing = INGRESSO.get(cmd[1] if len(cmd) > 1 else "")
    if _ing and not os.path.exists(os.path.join(BRAIN, _ing)):
        print(f"~~ {name}: SALTATO (questo brain non ha {_ing})")
        continue
    print(f"== {name} ==")
    # I tool del motore vivono nell'officina (ROOT) e sanno da soli dove sta il
    # contenuto. graphify no: indicizza la cartella in cui lo lanci, quindi va
    # lanciato NEL BRAIN. Lanciandolo in ROOT nasceva un secondo graphify-out nella
    # radice, e il brain restava con il grafo di prima senza che nulla lo dicesse.
    r = subprocess.run(cmd, cwd=BRAIN if cmd[0] == "graphify" else ROOT)
    if r.returncode != 0:
        print(f"XX {name}: FALLITO (exit {r.returncode}) — pipeline interrotta.")
        failed = True
        break

# La cronaca: una riga nel registro delle operazioni, solo se qualcosa e' cambiato.
if not failed:
    try:
        import json as _json
        sys.path.insert(0, ROOT)
        from tools.oplog import registra
        def _conta(rel, chiave):
            with open(os.path.join(BRAIN, rel), encoding="utf-8") as _f:
                return len(_json.load(_f)[chiave])
        _regole = 0
        _log = os.path.join(BRAIN, "engine", "lessons.jsonl")
        if os.path.exists(_log):
            with open(_log, encoding="utf-8") as _f:
                _regole = sum(1 for r in _f if '"livello": "lezione"' in r)
        registra("rebuild", f"{_conta('graphify-out/graph.json', 'nodes')} nodi, "
                            f"{_conta('engine/search_index.json', 'documenti')} frammenti, "
                            f"{_regole} regole")
    except (OSError, ValueError, KeyError, ImportError):
        pass          # la cronaca non deve mai far fallire una pipeline riuscita

if failed:
    sys.exit(1)

# Le tre viste sono il volto del brain: dirle qui evita che qualcuno ne apra una
# sola per anni senza sapere che le altre due rispondono a domande diverse.
print("\n== TUTTO OK ==")
print("Apri  graphify-out/index.html  — la porta: dice a quale domanda risponde ogni vista.")
print("Le TRE viste del grafo:")
for rel, serve_a in (("graphify-out/graph.html",         "vedere tutto"),
                     ("graphify-out/graph-compact.html", "spiegare il sistema come processo"),
                     ("graphify-out/graph-atlas.html",   "navigare e orientarsi (3D esplorabile)")):
    peso = os.path.getsize(os.path.join(BRAIN, rel)) // 1024 if os.path.exists(os.path.join(BRAIN, rel)) else 0
    print(f"  {rel:<34} {peso:>5} KB  — {serve_a}")
print("\nOra:  git add -A && git commit -m \"...\" && git push")
