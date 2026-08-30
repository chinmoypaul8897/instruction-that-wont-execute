"""Round 1's mutation harness was WRONG, and this is the corrected one.

`docs/reviews/ch03-probe/mutate.py` decided "caught" from `returncode != 0` **with no
green baseline**. Two consequences, both real:

  * a mutation applied to a suite that was ALREADY failing reads as "caught";
  * a mutation that is a **no-op on the fixture** reads as "caught" if anything else
    is red.

Round 2 showed M7 - "flip the negative-selection rule from the first to the last
sorted candidate" - **cannot** be caught: golden G-D's free candidate list is `["B"]`,
so `free[0]` and `free[-1]` are the same element. The "9/9 caught" table that
`REVIEW_CH-03.md`, `goldens.md` G-D2, `STATUS.md` and `PROGRESS.md` all repeated is
false, and this script is what a correct harness looks like.

**The rule it enforces: a mutation counts as CAUGHT only if the suite result CHANGES
from an established baseline.** Not "is red" - *changes*.

    python docs/reviews/ch03-probe2/mutate3.py
    # committed output: mutate3.txt

Every mutation is applied to a working copy, the suite is run, and the file is
restored and asserted byte-identical before the next one.
"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

TARGET = REPO / "src/eval_set.py"
CFR_PIT = REPO / "src/cfr_pit.py"

# (id, file, find, replace, what it breaks)
MUTATIONS = [
    ("N1", TARGET,
     "        negative = min(side, key=lambda s: (abs_rank(section_sort_key(s), key), s))",
     "        negative = free[0]",
     "revert the F1 fix to the EXACT defect that failed the gate"),
    ("N2", TARGET,
     "            side = higher if balance >= 0 else lower",
     "            side = lower",
     "always take the LOWER side - the F1 bias, re-created"),
    ("N3", TARGET,
     "            side = higher if balance >= 0 else lower",
     "            side = higher",
     "always take the HIGHER side - the F1 bias, mirrored"),
    ("N4", TARGET,
     "        balance += 1 if section_sort_key(negative) < key else -1",
     "        balance += 0",
     "disable the balance counter entirely"),
    ("N5", CFR_PIT,
     "        # F2: no declared range means a single-volume title, which covers the WHOLE",
     "        return False, False\n        # F2: no declared range means a single-volume title, which covers the WHOLE",
     "revert the F2 fix - a volume with no <PARTS> header is skipped again"),
    ("N6", TARGET,
     "                      and abs(c - own) <= tolerance)",
     "                      and abs(c - own) <= tolerance + 1)",
     "relax EXACT instruction-count matching to +/-1"),
]


def run_suite() -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header",
                        "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=str(REPO))
    summary = "?"
    for line in reversed(r.stdout.splitlines()):
        if " passed" in line or " failed" in line or " error" in line:
            summary = line.strip()
            break
    return r.returncode, summary


def main() -> int:
    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 88)
    p("MUTATION TEST, DONE CORRECTLY - a mutation is CAUGHT only if the RESULT CHANGES")
    p("=" * 88)
    p("")
    p("  Round 1's harness read `returncode != 0` as 'caught' and never established a")
    p("  baseline, so a no-op mutation on an already-red suite counted as caught. That")
    p("  is how 'M7 caught' entered four committed documents while being impossible.")
    p("")

    base_rc, base_sum = run_suite()
    p(f"  BASELINE   rc={base_rc}   {base_sum}")
    p("")
    p(f"  {'id':<5}{'target':<18}{'result':<34}{'verdict':<10}  what it breaks")

    results = []
    for mid, path, find, repl, what in MUTATIONS:
        original = path.read_text(encoding="utf-8")
        if find not in original:
            p(f"  {mid:<5}{path.name:<18}{'TARGET NOT FOUND':<34}{'SKIPPED':<10}  {what}")
            results.append((mid, "SKIPPED", what))
            continue
        path.write_text(original.replace(find, repl, 1), encoding="utf-8", newline="\n")
        try:
            rc, summary = run_suite()
        finally:
            path.write_text(original, encoding="utf-8", newline="\n")
            if path.read_text(encoding="utf-8") != original:
                raise SystemExit(f"{mid}: FAILED TO RESTORE {path}")
        caught = (rc, summary) != (base_rc, base_sum)
        verdict = "CAUGHT" if caught else "**MISSED**"
        p(f"  {mid:<5}{path.name:<18}{summary[:32]:<34}{verdict:<10}  {what}")
        results.append((mid, verdict, what))

    missed = [r for r in results if r[1] == "**MISSED**"]
    p("")
    p("=" * 88)
    p(f"  {len(results) - len(missed)} caught, {len(missed)} MISSED of {len(results)}")
    p("=" * 88)
    for mid, _, what in missed:
        p(f"  MISSED  {mid}  {what}")
    if not missed:
        p("  (no mutation went uncaught)")
    p("")
    p("  A MISSED row is a hole in the suite, not a pass. Round 2's SEVERE finding 1")
    p("  was exactly this: five of six mutations of the fixed selection rule were")
    p("  uncaught, because the kept test asserted on the FROZEN FILE and a source")
    p("  mutation does not touch a frozen file.")
    text = w.getvalue()
    io.open(OUT / "mutate3.txt", "w", encoding="utf-8", newline="\n").write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
