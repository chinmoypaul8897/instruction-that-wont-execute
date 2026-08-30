"""Probe for the DIV1-volume-vs-title fix. Hard rule 6: fails on old, passes on new.

    "EVERY FIX SHIPS A PROBE THAT FLIPS. Fails on the old code, passes on the new -
     show both. The probe is kept forever."

THE BUG. `<DIV1 N="1" NODE="11:1" TYPE="TITLE">` is *volume 1 of title 11*. The `N`
attribute is the printed volume index; the CFR title number is the `NODE` prefix.
`src/harvest_ednotes.py` as first written read `N`, which labelled every title in the
corpus `"1"`.

HOW IT SURFACED. Each record states its title three independent ways - the container's
`NODE` prefix, the enclosing `TYPE="TITLE"` div, and the filename - and the extractor
counts how many records have those three disagree. The counter is expected to print
**0**. It printed **2428**: every record in the corpus.

WHY THIS MATTERS MORE THAN THE BUG DOES. No count in CH-01 was wrong, because `title`
already preferred the `NODE` prefix. What was at stake was the *reading* of the
number: `2428` disagreements is exactly the shape of a spectacular data finding, and a
session in a hurry writes it up as one. Hard rule 15 says a finding is a claim until
it is checked, and hard rule 17 says the clock is not a design input. This probe is
what checking looked like.

The permanent regression test is
`tests/test_harvest_ednotes.py::test_div1_N_is_the_volume_index_and_is_not_the_title_number`.
This script exists to show the FLIP - the assertion evaluated against both the
pre-fix and post-fix module, side by side, in one output.

    python docs/evidence/ch01-pool/ch01_probe_div1.py

Output committed as `ch01-probe-div1.txt`. Needs a git worktree (it reads the old
module out of history with `git show`); prints a SKIP and exits 2 if it cannot.
"""
from __future__ import annotations

import io
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

#: The commit that introduced src/harvest_ednotes.py, before the fix.
OLD_COMMIT = "7d56f26"
#: The commit that fixed it.
NEW_COMMIT = "9cde11c"

#: A title-11 fragment carrying the exact attribute shape that triggers the bug:
#: N="1" on the TYPE="TITLE" div, NODE="11:1" beside it.
FIXTURE = (
    '<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
    '<DIV1 N="1" NODE="11:1" TYPE="TITLE">'
    '<DIV5 N="104" NODE="11:1.0.1.1.12" TYPE="PART">'
    "<EDNOTE><PSPACE>could not be incorporated at 90 FR 9</PSPACE></EDNOTE>"
    "</DIV5></DIV1></DLPSTEXTCLASS>"
).encode("utf-8")


def title_sources(module_dir: str) -> dict:
    sys.path.insert(0, module_dir)
    sys.modules.pop("harvest_ednotes", None)
    try:
        import harvest_ednotes as h
        rec = list(h.iter_ednotes(io.BytesIO(FIXTURE), "ECFR-title11.xml", "11"))[0]
        return dict(rec["title_sources"])
    finally:
        sys.path.pop(0)
        sys.modules.pop("harvest_ednotes", None)


def report(label: str, src: dict) -> bool:
    distinct = {v for v in src.values() if v}
    agree = len(distinct) == 1
    print(f"  {label}")
    print(f"    title_sources    {src}")
    print(f"    distinct values  {sorted(distinct)}")
    print(f"    all three agree  {agree}")
    print(f"    ASSERTION        {'PASSES' if agree else 'FAILS'}")
    return agree


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="ch01-probe-"))
    old_dir = tmp / "old"
    old_dir.mkdir()
    try:
        blob = subprocess.run(
            ["git", "show", f"{OLD_COMMIT}:src/harvest_ednotes.py"],
            cwd=REPO, capture_output=True)
        if blob.returncode != 0:
            print("SKIP - cannot read the pre-fix module out of git history.")
            print(f"       `git show {OLD_COMMIT}:src/harvest_ednotes.py` failed.")
            print("       Exiting 2 rather than 0: a probe that cannot run must not")
            print("       report the same thing as a probe that passed.")
            return 2
        (old_dir / "harvest_ednotes.py").write_bytes(blob.stdout)

        print("PROBE - test_div1_N_is_the_volume_index_and_is_not_the_title_number")
        print("=" * 78)
        print("assertion: a record's three independent statements of its CFR title -")
        print("           the container NODE prefix, the enclosing TYPE=\"TITLE\" div,")
        print("           and the filename - must all read \"11\" for a title-11 note.")
        print()
        print(f"OLD CODE  {OLD_COMMIT}  (doc_title = el.get(\"N\"))")
        old_ok = report("", title_sources(str(old_dir)))
        print()
        print(f"NEW CODE  {NEW_COMMIT}  (doc_title = _title_from_node(el.get(\"NODE\")))")
        new_ok = report("", title_sources(str(REPO / "src")))
        print()
        print("=" * 78)
        flipped = (not old_ok) and new_ok
        print(f"FLIP: fails on old = {not old_ok}   passes on new = {new_ok}   "
              f"-> {'PROBE FLIPS' if flipped else 'PROBE DOES NOT FLIP'}")
        print()
        print("Corpus-wide effect, measured on all 49 titles:")
        print("  title-source disagreements BEFORE the fix   2428  (every record)")
        print("  title-source disagreements AFTER the fix       0")
        print("  see data/ednotes/counts.json -> total.title_source_disagreements")
        return 0 if flipped else 1
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
