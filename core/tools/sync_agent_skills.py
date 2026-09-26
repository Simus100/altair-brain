# -*- coding: utf-8 -*-
"""
altair-brain — le skill per gli altri agenti, generate da quelle di Claude.

PERCHE' ESISTE. Lo standard Agent Skills (agentskills.io) fa leggere le stesse
SKILL.md a Claude Code, Codex, Gemini CLI e agli altri: questo repo e' scritto da piu'
agenti, e qualcuno ha installato una copia delle skill in .agents/skills/. Era identica
a .claude/skills/ — oggi. Due copie tenute a mano divergono: e' esattamente come le
copie del motore dentro ogni brain erano arrivate a 17 tool diversi su 31.

Quindi una fonte sola, .claude/skills/, e .agents/skills/ GENERATA da questa, con una
guardia (tests/test_percorsi_agenti.py) che fallisce se le due differiscono.

Uso:  python tools/sync_agent_skills.py        (lo chiama rebuild_all)
"""
import filecmp, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(ROOT, ".claude", "skills")
COPIA = os.path.join(ROOT, ".agents", "skills")


def differenze():
    """Le skill che mancano o differiscono nella copia (nomi relativi)."""
    if not os.path.isdir(FONTE):
        return []
    fuori = []
    for radice, _, files in os.walk(FONTE):
        for f in files:
            a = os.path.join(radice, f)
            rel = os.path.relpath(a, FONTE).replace("\\", "/")
            b = os.path.join(COPIA, rel)
            if not os.path.exists(b) or not filecmp.cmp(a, b, shallow=False):
                fuori.append(rel)
    if os.path.isdir(COPIA):
        for radice, _, files in os.walk(COPIA):
            for f in files:
                rel = os.path.relpath(os.path.join(radice, f), COPIA).replace("\\", "/")
                if not os.path.exists(os.path.join(FONTE, rel)):
                    fuori.append(rel + " (solo nella copia)")
    return sorted(fuori)


def main():
    try:
        sys.path.insert(0, ROOT)
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass          # tool eseguito fuori dal repo: si perde la protezione, non il tool
    if not os.path.isdir(FONTE):
        print("skill per gli agenti: nessuna skill in .claude/skills, niente da copiare")
        return 0
    if os.path.isdir(COPIA):
        shutil.rmtree(COPIA)
    shutil.copytree(FONTE, COPIA)
    n = sum(len(f) for _, _, f in os.walk(COPIA))
    print(f"skill per gli agenti: {n} file in .agents/skills (copia di .claude/skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
