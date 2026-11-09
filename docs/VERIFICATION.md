# Verification record

Distribution transition: 9 November 2026. Engine 1.2.0.

## Published product

- 0 acquired source notes in the starter.
- 0 acquired lessons; no training adopted by default.
- 3 graph views: extended, compact and immersive atlas.
- Optional AION package: 64 hexagrams, installed only when selected.
- Screenshot corpus: 3 areas, 18 synthetic source notes, 18 curated pages;
  144 section nodes and 219 relationships (including 18 provenance links).

Screenshots are browser captures of generated product pages, not mockups.
The corpus is created by `python docs/generate_demo.py`, entirely independently
of installed brains. PNGs in assets/ were captured at 1440 Ã— 960 with Edge/Playwright.

## Validation

Verified with a clean distribution snapshot on Windows / Python 3.13.14,
using Graphify 0.9.2 and the server dependencies installed in an isolated environment.

| Configuration | Passed | Skipped | Outcome |
|---|---:|---:|---|
| Virgin distribution, no training | 137 | 119 | rebuild and tests pass |
| New local brain, AION selected | 191 | 68 | adoption, rebuild and tests pass |

Both runs report one Starlette/httpx TestClient deprecation warning. This is not
an application runtime error. Run `python docs/verify_distribution.py` after staging
your changes to repeat this check against exactly the files intended for GitHub.
Results are recorded after verifying a clean distribution snapshot. Tests that require
uninstalled corpus, optional training or plugins are explicitly skipped; skipped tests
are not counted as capabilities verified. The corpus-specific tests from earlier
populated versions remain available for local use.

The earlier audit's 259 tests refer to the previous populated reference environment,
not to the default virgin installation or an accuracy benchmark. No large-corpus load
test, AI answer-quality benchmark, or production deployment is claimed here.

## Local content preservation

The transition removes acquired brains from the Git index using `git rm --cached`.
Their local files are preserved and compared against a pre-transition SHA-256 manifest.
The local registry continues to select the installed brain. Neither private brain names
nor their contents are needed to build core/ or run CI.

Removal from main does not erase previously published history or other historical refs.
