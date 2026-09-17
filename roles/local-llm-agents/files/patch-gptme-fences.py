#!/usr/bin/env python3
"""Accept ```bash and ```python fences in gptme.

gptme registers only 'shell' for the shell tool and 'ipython'/'py' for python.
Local models overwhelmingly emit ```bash and ```python, which then silently do
NOT execute -- and the model proceeds to hallucinate the output. Widening the
accepted fences removes a whole class of fabrication.

Re-run after `pipx upgrade gptme`.
"""
import sys
from pathlib import Path

VENV = Path.home() / ".local/share/pipx/venvs/gptme/lib/python3.13/site-packages/gptme/tools"
EDITS = [
    (VENV / "shell.py", 'block_types=["shell"]', 'block_types=["shell", "bash", "sh"]'),
    (VENV / "python.py", 'block_types=["ipython", "py"]', 'block_types=["ipython", "py", "python"]'),
]

changed = False
for path, old, new in EDITS:
    if not path.exists():
        sys.exit(f"not found: {path}")
    src = path.read_text()
    if new in src:
        print(f"  already patched: {path.name}")
        continue
    if old not in src:
        # try a looser match
        import re
        m = re.search(r'block_types\s*=\s*\[[^\]]*\]', src)
        sys.exit(f"  could not patch {path.name}; found: {m.group(0) if m else 'nothing'}")
    path.write_text(src.replace(old, new, 1))
    print(f"  patched: {path.name}  {old} -> {new}")
    changed = True

if changed:
    print("done")
