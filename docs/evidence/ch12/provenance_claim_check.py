#!/usr/bin/env python3
"""CH-12 - re-run the greps that falsified `PROVENANCE.md` §4, and the ones that
now support its correction.

§4 asserted: *"The `nistula-assistance-` result is cited in this project's README as
the motivating hypothesis for why a green test suite is insufficient evidence."*

**One grep falsified it.** This script is that grep, kept, so the claim is checkable
by anyone at any commit rather than taken on the correction's word. It also prints
what the sentence CANNOT be checked against, which matters as much: the external
repository is not reachable from here and its contents are not verified by this
project.

Hard rule 14 - the zero branches print as zeros, and `success + failure == n` is
asserted.

Run:  python docs/evidence/ch12/provenance_claim_check.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
README = ROOT / "README.md"
PROVENANCE = ROOT / "PROVENANCE.md"

#: (label, pattern, what a non-zero count would mean for the claim)
TERMS = [
    ("nistula", r"nistula",
     "the repository the claim names is cited"),
    ("acumen", r"acumen",
     "the OTHER prior-art repository is cited - NOT required by the claim"),
    ("17 blocker", r"17 blocker",
     "the defect count the claim calls the motivating hypothesis is cited"),
    ("github.com", r"github\.com",
     "some GitHub repository is cited at all"),
    ("chinmoypaul", r"chinmoypaul",
     "the operator's own namespace is cited"),
    ("green test suite", r"green test suite",
     "the hypothesis is stated in the README's own words"),
]

#: Terms whose presence the §4 sentence actually REQUIRES.
REQUIRED = {"nistula", "17 blocker", "github.com"}


def count(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, re.IGNORECASE))


def git(*args: str) -> str:
    """Run git and decode as UTF-8.

    `text=True` would decode with the console codepage, which on this machine is
    cp1252 and dies on the first curly quote in the README. The whole point of this
    script is a byte-accurate count, so the encoding is pinned rather than inherited.
    """
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                          encoding="utf-8", errors="replace").stdout


def main() -> int:
    print("CH-12 - PROVENANCE.md SECTION 4, THE DISCLOSURE CLAIM, CHECKED")
    print("=" * 84)
    print("Claim: the `nistula-assistance-` result is cited in this project's README")
    print("       as the motivating hypothesis for why a green test suite is")
    print("       insufficient evidence.\n")

    head_readme = git("show", "HEAD:README.md")
    now_readme = README.read_text(encoding="utf-8")

    print(f"{'term':<20}{'at HEAD':>9}{'working tree':>14}   required?   meaning")
    print("-" * 110)
    supported = unsupported = 0
    for label, pattern, meaning in TERMS:
        at_head = count(head_readme, pattern) if head_readme else -1
        now = count(now_readme, pattern)
        req = "REQUIRED" if label in REQUIRED else "-"
        print(f"{label:<20}{at_head:>9}{now:>14}   {req:<11}  {meaning}")
        if label in REQUIRED:
            if now >= 1:
                supported += 1
            else:
                unsupported += 1

    print("-" * 110)
    print(f"required terms present : {supported}")
    print(f"required terms ABSENT  : {unsupported}")
    assert supported + unsupported == len(REQUIRED), "success + failure != n"
    print(f"success + failure == n : {supported} + {unsupported} == {len(REQUIRED)}  OK")
    print()

    verdict = "TRUE" if unsupported == 0 else "FALSE"
    print(f"VERDICT on the working tree : the §4 sentence is {verdict}")
    if head_readme:
        head_ok = all(count(head_readme, p) >= 1
                      for lbl, p, _ in TERMS if lbl in REQUIRED)
        print(f"VERDICT at HEAD             : the §4 sentence is "
              f"{'TRUE' if head_ok else 'FALSE'}")
        print("   (these differ until the fixing commit lands; that is the point of "
              "printing both)")
    print()

    # --- where the citation actually sits ------------------------------------
    print("WHERE THE CITATION SITS IN THE README")
    print("-" * 84)
    hits = [(i, line.strip()) for i, line in enumerate(now_readme.splitlines(), 1)
            if re.search(r"nistula|17 blocker", line, re.IGNORECASE)]
    if hits:
        for i, line in hits:
            print(f"  README.md:{i}: {line[:100]}")
    else:
        print("  none - the README does not cite it")
    print()

    # --- the ordering that explains the defect --------------------------------
    print("WHY IT WAS WRONG - the file asserted this before the file it asserts about "
          "existed")
    print("-" * 84)
    for path in ("PROVENANCE.md", "README.md"):
        out = git("log", "--diff-filter=A", "--date=iso",
                  "--format=%h  %ad  %s", "--", path).strip().splitlines()
        print(f"  {path:<16} created: {out[-1] if out else '(not in history)'}")
    first = git("show", "3ac8207:PROVENANCE.md")
    print(f"  the sentence is in PROVENANCE.md's FIRST commit: "
          f"{count(first, 'nistula')} occurrence(s) of 'nistula' at 3ac8207")
    print()

    # --- what this project does NOT check -------------------------------------
    print("WHAT THIS SCRIPT DOES NOT AND CANNOT CHECK")
    print("-" * 84)
    print("  The external repository itself. No network call is made here, by policy,")
    print("  and nothing in this repository re-derives the 17-defect count. It is")
    print("  PRIOR ART, cited; it is not a result of this project and no claim in")
    print("  this submission rests on it. A reader who wants that number verified")
    print("  must go to the cited repository - which is exactly what a citation is")
    print("  for, and exactly why the README says the number carries no weight here.")
    print()

    # --- and the sibling claim in PROVENANCE ----------------------------------
    prov = PROVENANCE.read_text(encoding="utf-8")
    print(f"PROVENANCE.md mentions 'nistula' {count(prov, 'nistula')}x and "
          f"'acumen' {count(prov, 'acumen')}x")
    print(f"PROVENANCE.md carries {count(prov, chr(10) + r'\*\*Correction|' + chr(10) + r'\*\*A second correction')} "
          f"dated corrections (grep '^\\*\\*Correction' + '^\\*\\*A second correction')")

    return 0 if unsupported == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
