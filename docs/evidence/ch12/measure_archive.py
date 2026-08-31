#!/usr/bin/env python3
"""CH-12 - measure the uploaded artifact, and every figure the packet gives for it.

CH-12's own adversarial self-audit found the packet publishing FIVE different answers
to "how big is the zip" - 10.18, 10.24, 10.66, 11.74 and 11.77 MB - none of which was
the archive at the time of writing, and one of which was chosen (its own `checked` note
said so) because it preserved an adjacent "4.9x". That is the inverse of hard rule 5.

This script is the single measurement those figures are now pinned to. It measures at
NAMED COMMITS rather than at HEAD, because HEAD moves and a dated figure that says
which commit it belongs to cannot go stale - it can only become historical.

Pure: no network, no clock, no randomness, no model call. It writes only to a temp
directory outside the repository.

Run:  python docs/evidence/ch12/measure_archive.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

CAP = 50_000_000        # the HackerEarth submission form's cap, QUESTIONS.md Q2 C1
HOOK_LIMIT = 45_000_000  # what .githooks/pre-commit refuses to exceed

#: (commit, what it is). Historical figures the packet quotes are re-derived here so a
#: reader can see they were right when written rather than take that on trust.
COMMITS = [
    ("bc99ef4", "CH-14a, the commit inventory.md measured (10.18 MB)"),
    ("e01fdfd", "CH-11's last, the commit SUBMISSION.md measured (10.66 MB)"),
    ("57829c1", "CH-11c's last - CH-12's starting point"),
    ("9f8c26d", "CH-12's first commit"),
    ("b39cd0c", "CH-12's last code/doc commit"),
    ("HEAD", "whatever HEAD is when this is run - NOT a citable figure"),
]


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, encoding="utf-8",
                          errors="replace", check=True).stdout


def main() -> int:
    repo = Path(sh("git", "rev-parse", "--show-toplevel").strip())
    os.chdir(repo)

    print("CH-12 - THE UPLOADED ARCHIVE, MEASURED AT NAMED COMMITS")
    print("=" * 96)
    print(f"cap: {CAP:,} B = {CAP / 1e6:.0f} MB  ·  "
          f"pre-commit hook refuses above {HOOK_LIMIT:,} B\n")
    print(f"{'commit':<10}{'bytes':>14}{'MB':>9}{'entries':>9}{'x under cap':>13}  what it is")
    print("-" * 118)

    rows = []
    with tempfile.TemporaryDirectory() as td:
        for ref, what in COMMITS:
            try:
                sha = sh("git", "rev-parse", "--short", ref).strip()
            except subprocess.CalledProcessError:
                print(f"{ref:<10}{'(not in this history)':>45}  {what}")
                continue
            z = Path(td) / f"{sha}.zip"
            subprocess.run(["git", "archive", "--format=zip", "-o", str(z), ref],
                           check=True, capture_output=True)
            n = z.stat().st_size
            with zipfile.ZipFile(z) as zf:
                entries = len(zf.infolist())
            rows.append((sha, n, entries, what))
            print(f"{sha:<10}{n:>14,}{n / 1e6:>9.2f}{entries:>9}"
                  f"{CAP / n:>12.2f}x  {what}")

    print("-" * 118)
    print()
    print("EVERY FIGURE THE PACKET QUOTES, AND WHETHER IT RECONCILES")
    print("-" * 96)
    by_sha = {r[0]: r for r in rows}
    QUOTED = [
        ("10.18 MB", "bc99ef4", "docs/evidence/ch14-size/inventory.md, STATUS.md, AI-USE.md"),
        ("10.66 MB", "e01fdfd", "SUBMISSION.md (superseded at CH-12)"),
        ("12.51 MB", "b39cd0c", "SUBMISSION.md, STATUS.md, AI-USE.md after CH-12"),
    ]
    ok = bad = 0
    for quoted, sha, where in QUOTED:
        row = by_sha.get(sha)
        if not row:
            print(f"  {quoted:<10} at {sha}  COULD NOT CHECK          {where}")
            continue
        actual = f"{row[1] / 1e6:.2f} MB"
        match = actual == quoted
        ok += match
        bad += not match
        print(f"  {quoted:<10} at {sha}  measured {actual:<10} "
              f"{'MATCH' if match else 'MISMATCH':<9} {where}")
    print(f"\n  reconciled : {ok}")
    print(f"  mismatched : {bad}")
    assert ok + bad == len(QUOTED), "success + failure != n"
    print(f"  success + failure == n : {ok} + {bad} == {len(QUOTED)}  OK")

    print()
    print("NOT MEASURED HERE, and stated rather than implied: **10.24 MB**, which two")
    print("shipping files carried until CH-12 and which no commit in this history")
    print("produces. It was not a measurement of anything; it was corrected, not traced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
