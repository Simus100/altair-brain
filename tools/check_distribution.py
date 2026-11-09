"""Fail if acquired brains or a local registry enter the public Git tree."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', 'brains'], cwd=ROOT)
    paths = [p for p in tracked.decode('utf-8').split('\0') if p]
    allowed = ('brains/starter/', 'brains/brains.default.json', 'brains/README.md')
    forbidden = [p for p in paths if not p.startswith(allowed)]
    lessons = ROOT / 'brains/starter/engine/lessons.jsonl'
    notes = [p for p in (ROOT / 'brains/starter/raw').rglob('*')
             if p.is_file() and p.name not in ('README.md', '.gitkeep')]
    portal = ROOT / 'brains/starter/graphify-out/index.html'
    if portal.exists() and '../../' in portal.read_text(encoding='utf-8'):
        raise SystemExit('Public starter links to locally installed brains.')
    if forbidden or notes or (lessons.exists() and lessons.read_text(encoding='utf-8').strip()):
        raise SystemExit('Distribution contains acquired content or a local registry.')
    print(json.dumps({'tracked_brain_files': len(paths), 'acquired_notes': 0,
                      'acquired_lessons': 0, 'distribution': 'virgin'}))


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    main()
