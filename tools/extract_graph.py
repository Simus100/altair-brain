"""Extract one brain in isolation, including brains intentionally ignored by Git."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.brain import BRAIN


def main():
    if not shutil.which('graphify'):
        raise SystemExit('Install graphifyy==0.9.2 before rebuilding.')
    brain = Path(BRAIN)
    output = brain / 'graphify-out'
    with tempfile.TemporaryDirectory(prefix='altair-extract-') as work:
        work = Path(work)
        # An ignored local brain must still be extractable. Never scan sibling
        # brains, the workshop, or large data binaries when making its graph.
        for part in ('raw', 'wiki', 'engine', 'reports'):
            source = brain / part
            if not source.exists():
                continue
            for f in source.rglob('*'):
                if f.is_file() and f.suffix.lower() in ('.md', '.txt', '.json', '.py', '.sql'):
                    dest = work / f.relative_to(brain)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
        target = work / 'graphify-out'
        target.mkdir()
        for name in ('graph.json', 'manifest.json', '.graphify_labels.json'):
            if (output / name).exists():
                shutil.copy2(output / name, target / name)
        result = subprocess.run(['graphify', 'update', '.'], cwd=work)
        if result.returncode:
            return result.returncode
        output.mkdir(exist_ok=True)
        for f in target.iterdir():
            if f.is_file() and f.name != '.graphify_root':
                shutil.copy2(f, output / f.name)
    return 0


if __name__ == '__main__':
    try:
        from tools.console import usa_utf8
        usa_utf8()
    except ImportError:
        pass
    sys.exit(main())
