"""Q8's trap, caught in the act: the spec names <EFFDNOTP>; the corpus also uses
<EFFDNOT>, and <EFFDNOTP> occurs ZERO times in the volume where <EFFDNOT> occurs four.

The strip counter printed `EFFDNOTP: 0` for CFR-2015-title7-vol13. **The zero was true
for that tag and false for the corpus.** This script measures how far that goes, over
every annual-edition volume CH-03 actually downloaded.

Two questions, because the answer decides whether "exclude the affected items and
report it" is safe or whether it is merely comfortable:

  1. How many note-like containers exist that CONTEXT.md section 8 does not name?
  2. Does EVERY such container carry one of plan.md's four literals? If it does, the
     leakage test's rule (c) is a complete backstop for the ones the element list
     misses. If it does not, there is residual exposure and it must be stated.

    python docs/evidence/ch03-evalset/alt_element_census.py
    # committed output: alt-element-census.txt
"""
from __future__ import annotations

import io
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from cfr_pit import LEAKAGE_ELEMENTS, LEAKAGE_LITERALS, eligible_sections  # noqa: E402

RAW = REPO / "data/raw/cfr"
OUT = Path(__file__).resolve().parent

# Every container that could plausibly carry an editorial or effective-date note or a
# source credit. The list is deliberately WIDER than CONTEXT.md section 8's four, and
# the point of the census is to find out which of the extras actually occur.
CANDIDATES = [
    "EDNOTE", "EFFDNOTP", "CITA", "EAR",           # the four section 8 names
    "EFFDNOT", "EFFDNOTE", "NOTE", "NOTES", "NOTE1",
    "REVTXT", "APPRO", "SECAUTH", "SOURCE", "CREDIT", "AMDNOTE",
]


def main() -> int:
    vols = sorted(RAW.glob("*.xml"))
    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 78)
    p("ALTERNATE NOTE-ELEMENT CENSUS - QUESTIONS.md Q8's trap, measured")
    p("=" * 78)
    p("")
    p(f"  volumes scanned: {len(vols)}")
    p("")

    totals = Counter()
    vols_with = Counter()
    literal_carried = Counter()
    literal_missing = Counter()
    examples: dict[str, tuple] = {}

    for path in vols:
        try:
            root = ET.parse(str(path)).getroot()
        except Exception as exc:                       # pragma: no cover
            p(f"  UNPARSEABLE {path.name}: {exc!r}")
            continue
        seen = Counter(e.tag for e in root.iter())
        for tag in CANDIDATES:
            if seen.get(tag):
                totals[tag] += seen[tag]
                vols_with[tag] += 1
        for tag in CANDIDATES:
            for el in root.iter(tag):
                flat = " ".join("".join(el.itertext()).split())
                if any(lit in flat for lit in LEAKAGE_LITERALS):
                    literal_carried[tag] += 1
                else:
                    literal_missing[tag] += 1
                    examples.setdefault(tag + "|missing", (path.name, flat[:160]))
                examples.setdefault(tag, (path.name, flat[:160]))

    p(f"  {'element':<12}{'occurrences':>13}{'volumes':>10}{'named by CONTEXT 8':>21}")
    for tag in CANDIDATES:
        named = "YES" if tag in LEAKAGE_ELEMENTS else "no"
        p(f"  {tag:<12}{totals.get(tag, 0):>13}{vols_with.get(tag, 0):>10}{named:>21}")
    p("")
    p("  Zero-occurrence rows are printed above, not omitted (hard rule 14).")
    p("")

    p("=" * 78)
    p("IS plan.md's LITERAL TEST (rule c) A COMPLETE BACKSTOP FOR THE UNNAMED ONES?")
    p("=" * 78)
    p("")
    p(f"  {'element':<12}{'carries a literal':>19}{'carries NONE':>15}{'backstop':>12}")
    unnamed_gap = 0
    for tag in CANDIDATES:
        if not totals.get(tag):
            continue
        c, m = literal_carried.get(tag, 0), literal_missing.get(tag, 0)
        if tag in LEAKAGE_ELEMENTS:
            verdict = "n/a (named)"
        elif m == 0:
            verdict = "COMPLETE"
        else:
            verdict = "INCOMPLETE"
            unnamed_gap += m
        p(f"  {tag:<12}{c:>19}{m:>15}{verdict:>12}")
    p("")
    p(f"  UNNAMED elements carrying NO literal, i.e. residual exposure: {unnamed_gap}")
    p("")

    if "EFFDNOT" in examples:
        name, text = examples["EFFDNOT"]
        p("  A sample <EFFDNOT>, the element CONTEXT.md section 8 does not name:")
        p(f"    from {name}")
        p(f"    {text!r}")
        p("")

    p("=" * 78)
    p("RESIDUAL EXPOSURE ON THE FROZEN CORPUS ITSELF - the number that decides")
    p("=" * 78)
    p("")
    p("  The whole-volume census above is an upper bound over material we never")
    p("  freeze. What matters is what SURVIVES stripping inside the 76 frozen items.")
    p("")
    import json as _json
    from cfr_pit import find_section, strip_leakage, section_text
    items_path = REPO / "data/evalset/items.jsonl"
    if not items_path.exists():
        p("  data/evalset/items.jsonl absent - build the eval set first.")
    else:
        items = [_json.loads(l) for l in
                 items_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        surviving = Counter()
        items_with = Counter()
        fr_cit_in_unnamed = 0
        roots: dict = {}
        for it in items:
            vp = RAW / it["volume"]
            if vp not in roots:
                roots[vp] = ET.parse(str(vp)).getroot()
            sec, _n = find_section(roots[vp], it["section"])
            if sec is None:
                continue
            stripped, _c = strip_leakage(sec)
            hit_any = set()
            for tag in CANDIDATES:
                if tag in LEAKAGE_ELEMENTS:
                    continue
                k = sum(1 for _ in stripped.iter(tag))
                if k:
                    surviving[tag] += k
                    hit_any.add(tag)
            for tag in hit_any:
                items_with[tag] += 1
            flat = " ".join(section_text(stripped).split())
            import re as _re
            if _re.search(r"\d{1,3}\s+FR\s+\d{1,6}", flat):
                fr_cit_in_unnamed += 1
        p(f"  frozen items inspected: {len(items)}")
        p("")
        p(f"  {'element':<12}{'surviving':>12}{'items affected':>17}")
        for tag in CANDIDATES:
            if tag in LEAKAGE_ELEMENTS:
                continue
            p(f"  {tag:<12}{surviving.get(tag, 0):>12}{items_with.get(tag, 0):>17}")
        p("")
        p(f"  frozen items whose STRIPPED text still contains ANY 'NN FR NNNN'")
        p(f"  citation (not necessarily their own - rule (b) already excludes that):")
        p(f"    {fr_cit_in_unnamed} of {len(items)}")
        p("")
        p("  This figure is REPORTED, not remedied. CONTEXT.md section 8's honest")
        p("  bounding already says prior notes on the same section are")
        p("  label-correlated; this is that statement turned into a count.")
        p("")

    p("=" * 78)
    p("WHAT WAS DONE ABOUT IT")
    p("=" * 78)
    p("")
    p("  NOTHING was added to the stripper. CONTEXT.md section 8 names four elements")
    p("  and adding a fifth is a Class A spec change, which belongs to the architect")
    p("  and not to the session that found it (QUESTIONS.md Q17).")
    p("")
    p("  The affected items were EXCLUDED on the named ladder rung")
    p("  `leakage-test-failed-after-strip`. That makes the eval set SMALLER, which is")
    p("  the conservative direction; extending the stripper would have made it larger")
    p("  after the number was in view, which is the direction this project refuses.")
    p("")
    p("  The defence that caught it was pre-registered: plan.md's leakage test checks")
    p("  LITERALS as well as element names, so it fires on content the element list")
    p("  misses. That is the reason the test has three rules and not one.")
    io.open(OUT / "alt-element-census.txt", "w", encoding="utf-8",
            newline="\n").write(w.getvalue())
    print(w.getvalue(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
