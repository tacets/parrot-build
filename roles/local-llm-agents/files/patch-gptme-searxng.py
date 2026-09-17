#!/usr/bin/env python3
"""Add a SearXNG backend to gptme's browser tool.

gptme ships google/duckduckgo/perplexity. Google is CAPTCHA-blocked, duckduckgo
only works on the lynx backend (unreachable once playwright is installed), and
perplexity needs a paid external key. Models instinctively call search(), get an
error, and then answer from memory instead -- which is how you get a confident
"nmap 7.94" when 7.95 is installed locally.

This makes search() hit the self-hosted SearXNG instead. Re-run after
`pipx upgrade gptme`, which overwrites the file.
"""
import re
import sys
from pathlib import Path

MARKER = "# --- searxng backend (local patch) ---"
DEFAULT_URL = "https://kracken.taila9e14f.ts.net:8443"

path = Path.home() / ".local/share/pipx/venvs/gptme/lib/python3.13/site-packages/gptme/tools/browser.py"
if not path.exists():
    sys.exit(f"not found: {path}")

src = path.read_text()
if MARKER in src:
    print("already patched")
    sys.exit(0)

impl = f'''

{MARKER}
def _searxng_url() -> str | None:
    import os

    return os.environ.get("SEARXNG_URL", "{DEFAULT_URL}") or None


def search_searxng(query: str) -> str:
    """Query a self-hosted SearXNG instance via its JSON API."""
    import requests

    base = (_searxng_url() or "").rstrip("/")
    resp = requests.get(
        base + "/search",
        params={{"q": query, "format": "json"}},
        timeout=60,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return SEARCH_ENGINE_ERROR_PREFIX + " searxng returned no results"
    out = []
    for item in results[:10]:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = (item.get("content") or "").strip()[:250]
        out.append(f"- {{title}}\\n  {{url}}" + (f"\\n  {{snippet}}" if snippet else ""))
    return "\\n".join(out)
# --- end searxng backend ---
'''

# 1. append the implementation
src = src.rstrip() + impl

# 2. make it the first-choice backend
old_avail = '''    engines: list[EngineType] = []

    if has_perplexity:'''
new_avail = '''    engines: list[EngineType] = []

    # Self-hosted SearXNG first: no CAPTCHA, no third party, no API key.
    if _searxng_url():
        engines.append("searxng")  # type: ignore[arg-type]

    if has_perplexity:'''
if old_avail not in src:
    sys.exit("could not patch _available_search_engines (upstream changed?)")
src = src.replace(old_avail, new_avail, 1)

# 3. dispatch it
old_disp = '''    if engine == "perplexity":
        if has_perplexity:'''
new_disp = '''    if engine == "searxng":
        return search_searxng(query)

    if engine == "perplexity":
        if has_perplexity:'''
if old_disp not in src:
    sys.exit("could not patch _search_with_engine (upstream changed?)")
src = src.replace(old_disp, new_disp, 1)

path.write_text(src)
print(f"patched {path}")
