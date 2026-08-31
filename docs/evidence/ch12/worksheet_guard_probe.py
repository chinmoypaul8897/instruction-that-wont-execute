#!/usr/bin/env python3
"""CH-12 - prove the worksheet's self-containment guard actually catches things.

Hard rule 6: a fix ships a probe that flips. A guard that has never failed is not
evidence that it works; it is evidence that nothing has tested it. So this script
takes the SHIPPED page, injects one external reference at a time into an in-memory
copy, and asserts the guard rejects each. It never writes to `docs/worksheet/`.

Each injection is a real way a self-contained page silently stops being one:

  1. a CDN <script> - the obvious one
  2. a Google Fonts <link> - the one that slips through review
  3. a protocol-relative <img src="//..."> - no scheme, still a fetch
  4. `@import` inside the inline <style> - a stylesheet fetch with no tag
  5. `url(...)` in a CSS background - a fetch with no tag AND no attribute
  6. an <a href="https://..."> around a corpus URL - the page's own text,
     made live. This is the one the naive "assert 'http://' not in html" guard
     could never distinguish from what the page legitimately does today.

Run:  python docs/evidence/ch12/worksheet_guard_probe.py
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.test_worksheet import (  # noqa: E402
    test_no_external_resource_reference,
    test_scheme_strings_are_corpus_text_only,
    test_scheme_strings_that_do_occur_are_inert,
)

PAGE = ROOT / "docs" / "worksheet" / "index.html"

GUARDS = (
    ("no_external_resource_reference", test_no_external_resource_reference),
    ("scheme_strings_are_corpus_text_only", test_scheme_strings_are_corpus_text_only),
    ("scheme_strings_that_do_occur_are_inert", test_scheme_strings_that_do_occur_are_inert),
)

INJECTIONS = (
    ("cdn script tag",
     "</head>",
     '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head>'),
    ("google fonts stylesheet",
     "</head>",
     '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter"></head>'),
    ("protocol-relative image",
     "</body>",
     '<img src="//example.invalid/logo.png"></body>'),
    ("css @import",
     "<style>",
     '<style>@import "https://fonts.googleapis.com/css2?family=Inter";'),
    ("css url() background",
     "  body{",
     '  body{background-image:url("https://example.invalid/paper.png");'),
    ("corpus url made into a live link",
     "http://www.archives.gov",
     '<a href="http://www.archives.gov">http://www.archives.gov</a>'),
)


def run(name: str, text: str) -> list[str]:
    """Return the names of the guards that REJECTED this text."""
    rejected = []
    for guard_name, guard in GUARDS:
        try:
            guard(text)
        except AssertionError:
            rejected.append(guard_name)
    return rejected


def main() -> int:
    clean = PAGE.read_text(encoding="utf-8")

    print("WORKSHEET SELF-CONTAINMENT GUARD - PROBE")
    print("=" * 72)
    print(f"page   : {PAGE.relative_to(ROOT).as_posix()}  ({len(clean.encode()):,} B)")
    print(f"guards : {', '.join(n for n, _ in GUARDS)}")
    print()

    print("BASELINE - the shipped page, unmodified")
    rejected = run("baseline", clean)
    print(f"  guards that rejected it : {rejected or 'none'}")
    baseline_ok = not rejected
    print(f"  {'PASS' if baseline_ok else 'FAIL'} - the shipped page must pass every guard")
    print()

    print("INJECTIONS - each must be rejected by at least one guard")
    print("-" * 72)
    results = []
    for label, needle, replacement in INJECTIONS:
        if needle not in clean:
            print(f"  {label:38s} SKIP - anchor {needle!r} not in the page")
            results.append((label, False, ["anchor missing"]))
            continue
        dirty = clean.replace(needle, replacement, 1)
        assert dirty != clean, f"injection {label} did not change the page"
        rejected = run(label, dirty)
        ok = bool(rejected)
        results.append((label, ok, rejected))
        print(f"  {label:38s} {'CAUGHT' if ok else 'MISSED':6s}  by {rejected or '-'}")

    print("-" * 72)
    caught = sum(1 for _, ok, _ in results if ok)
    missed = len(results) - caught
    print(f"injections caught : {caught}")
    print(f"injections MISSED : {missed}")
    assert caught + missed == len(INJECTIONS), "success + failure != n"
    print(f"success + failure == n : {caught} + {missed} == {len(INJECTIONS)}  OK")
    print()

    verdict = baseline_ok and missed == 0
    print(f"VERDICT: {'PASS' if verdict else 'FAIL'}"
          f" - the guard flips: it passes the real page and rejects every injection")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
