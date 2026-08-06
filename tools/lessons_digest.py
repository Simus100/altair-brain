# -*- coding: utf-8 -*-
"""
altair-brain — consolida le lezioni in engine/LESSONS.md (P1: feedback loop).

Fonde DUE sorgenti, senza toccare nessuna delle due:
  A) engine/lessons.jsonl        — registro append-only scritto dalle skill (lesson_log.py)
  B) graphify-out/memory/*.md    — sessioni salvate da `graphify save-result`

Produce engine/LESSONS.md: il passo 0 del reasoner ("consulta le lezioni") legge
questo file. Deterministico, nessuna API: l'aggregazione e conteggio + ordinamento.

EMERGENZA (nel senso Zettelkasten): un nodo citato piu volte con esito "utile" diventa
un ancoraggio affidabile; un nodo ricorrente nei vicoli ciechi e un segnale di allarme.
La distinzione consolidato/tentativo evita di dare per certo cio che si e visto una volta.

Uso:  python tools/lessons_digest.py   (parte di rebuild_all.py)
"""
import collections, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "engine", "lessons.jsonl")
MEM_DIR = os.path.join(ROOT, "graphify-out", "memory")
OUT = os.path.join(ROOT, "engine", "LESSONS.md")

SOGLIA_CONSOLIDATA = 2      # citazioni utili oltre le quali una lezione e affidabile
RECENTI = 12                # quante lezioni mostrare per esteso


def carica_jsonl(path):
    voci = []
    if not os.path.exists(path):
        return voci
    with open(path, encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga:
                continue
            try:
                voci.append(json.loads(riga))
            except json.JSONDecodeError:
                continue        # una riga corrotta non deve far cadere il digest
    return voci


def sessioni_graphify(d):
    """Le sessioni salvate da graphify: si contano, non si reinterpretano."""
    if not os.path.isdir(d):
        return []
    return [f for f in sorted(os.listdir(d)) if f.endswith(".md")]


voci = carica_jsonl(LOG)
sessioni = sessioni_graphify(MEM_DIR)

# --- aggregazione: nodi per esito, tag, skill ---
utili = collections.Counter()
ciechi = collections.Counter()
tag = collections.Counter()
skill = collections.Counter()
for v in voci:
    skill[v.get("skill", "?")] += 1
    for t in v.get("tag", []):
        tag[t] += 1
    dest = utili if v.get("esito") == "utile" else (ciechi if v.get("esito") == "vicolo-cieco" else None)
    if dest is not None:
        for n in v.get("nodi", []):
            dest[n] += 1

consolidati = [(n, c) for n, c in utili.most_common() if c >= SOGLIA_CONSOLIDATA]
tentativi = [(n, c) for n, c in utili.most_common() if c < SOGLIA_CONSOLIDATA]

righe = [
    "# Lezioni apprese — memoria operativa del brain",
    "",
    "> GENERATO da `tools/lessons_digest.py` — non editare a mano.",
    "> Fonti: `engine/lessons.jsonl` (skill) + `graphify-out/memory/` (sessioni graphify).",
    "> Passo 0 del reasoner: leggi questo file PRIMA di rispondere; verifica sempre",
    "> prima di fidarti, e riapri i vicoli ciechi se il brain e cambiato da allora.",
    "",
    "## Sintesi",
    "",
    f"- lezioni registrate: **{len(voci)}** · sessioni graphify: **{len(sessioni)}**",
    f"- esiti: {sum(1 for v in voci if v.get('esito') == 'utile')} utili · "
    f"{sum(1 for v in voci if v.get('esito') == 'vicolo-cieco')} vicoli ciechi · "
    f"{sum(1 for v in voci if v.get('esito') == 'corretto')} correzioni · "
    f"{sum(1 for v in voci if v.get('esito') == 'aperto')} aperte",
    f"- skill piu attive: {', '.join(f'{k} ({c})' for k, c in skill.most_common(5)) or '—'}",
    f"- temi ricorrenti: {', '.join(f'{k} ({c})' for k, c in tag.most_common(8)) or '—'}",
    "",
]

if consolidati:
    righe += ["## Ancoraggi consolidati", "",
              f"_Nodi utili in almeno {SOGLIA_CONSOLIDATA} occasioni: punti di partenza affidabili._", ""]
    righe += [f"- `{n}` — {c}× utile" for n, c in consolidati] + [""]

if tentativi:
    righe += ["## Tentativi (da confermare)", "",
              "_Visti una volta sola: verifica prima di farci affidamento._", ""]
    righe += [f"- `{n}` — {c}× utile" for n, c in tentativi[:20]] + [""]

if ciechi:
    righe += ["## Vicoli ciechi", "",
              "_Non hanno portato a nulla in passato. Se il brain e cambiato, vale riprovare._", ""]
    righe += [f"- `{n}` — {c}× senza esito" for n, c in ciechi.most_common(15)] + [""]

note = [v for v in voci if v.get("nota")]
if note:
    righe += ["## Lezioni recenti", ""]
    for v in sorted(note, key=lambda x: x.get("ts", ""), reverse=True)[:RECENTI]:
        giorno = (v.get("ts") or "")[:10]
        righe.append(f"- **{giorno}** _(({v.get('skill', '?')}, {v.get('esito', '?')}))_ — {v['nota']}")
        if v.get("domanda"):
            righe.append(f"  - contesto: {v['domanda']}")
    righe.append("")

if not voci and not sessioni:
    righe += ["## Nessuna lezione ancora", "",
              "Registrane una: `python tools/lesson_log.py --skill manuale --domanda \"...\" "
              "--nota \"...\"`", ""]

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(righe))

print(f"LESSONS consolidate: {len(voci)} lezioni + {len(sessioni)} sessioni "
      f"-> engine/LESSONS.md ({len(consolidati)} ancoraggi, {len(ciechi)} vicoli ciechi)")
