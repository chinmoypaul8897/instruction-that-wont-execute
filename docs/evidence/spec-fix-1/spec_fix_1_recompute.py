#!/usr/bin/env python3
"""SPEC-FIX-1 section 3 - re-report CH-02's numbers under the PROPOSED split metric.

The attributor is NOT re-run (SPEC-FIX-1 section 3 forbids it). Everything here is
recomputed from the frozen `data/amdpars/completeness.json` and `amdpars.jsonl`.

IMPORTANT - read with `verdict.md`. The verdict is GOALPOST-MOVING, so the proposed
definition was NOT adopted and `CONTEXT.md` is unchanged. These figures are computed
under the proposed definition in order to JUDGE it, not because it is in force. The
gate CH-02 actually took, and which still stands, is `CONTEXT.md` section 8's own
`spec_literal` detector.

Reads only. `data/` is sealed (hard rule 11). No clock, no network, no randomness.

Usage:  python docs/evidence/spec-fix-1/spec_fix_1_recompute.py
"""
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")

ROOT = Path(__file__).resolve().parents[3]
AMDPARS = ROOT / "data" / "amdpars" / "amdpars.jsonl"
COMPLETENESS = ROOT / "data" / "amdpars" / "completeness.json"
GATE = 0.90


def branch(v):
    """prompts/CH-02.md section 4's pre-registered branch table."""
    if v >= 0.90:
        return "BRANCH >= 0.90 : Proceed. Report the figure."
    if v >= 0.80:
        return "BRANCH [0.80,0.90) : Proceed AND compute the restricted pool."
    return "BRANCH < 0.80 : documented failure. Do not tune it to pass."


def main():
    agg = json.loads(COMPLETENESS.read_text(encoding="utf-8"))
    recs = [json.loads(l) for l in AMDPARS.open(encoding="utf-8")]
    n = len(recs)
    per = agg["per_document"]

    print("=" * 78)
    print("SPEC-FIX-1 section 3 - CH-02's numbers under the PROPOSED split metric")
    print("The attributor was NOT re-run. Recomputed from the frozen freeze.")
    print("=" * 78)
    print()

    print("-- GLOBAL ---------------------------------------------------------------")
    print("   %-13s %-26s %8s   %s" % ("detector", "metric", "value", "vs 0.90 gate"))
    for det in ("spec_literal", "extended"):
        g = agg["global"][det]
        rows = [
            ("attribution_completeness  (proposed GATE)", g["attributed"] / n),
            ("parse_completeness        (reported)", g["parsed"] / n),
            ("completeness  (CONTEXT.md section 8, in force)", g["complete"] / n),
        ]
        for label, v in rows:
            print("   %-13s %-46s %.4f   %s"
                  % (det, label, v, "PASS" if v >= GATE else "**FAIL**"))
        print()

    print("-- WHICH PRE-REGISTERED CH-02 BRANCH DOES EACH FIGURE LAND IN? ----------")
    print("   prompts/CH-02.md section 4's table is pre-registered and is NOT changed")
    print("   by this chunk. Applying it to each candidate figure:")
    print()
    for det in ("spec_literal", "extended"):
        g = agg["global"][det]
        print("   detector = %s" % det)
        for label, v in (("completeness (in force)", g["complete"] / n),
                         ("attribution_completeness (proposed)", g["attributed"] / n)):
            print("     %-38s %.4f  ->  %s" % (label, v, branch(v)))
        print()

    print("-- THE ANSWER SECTION 3 ASKS FOR, STATED PLAINLY ------------------------")
    lit = agg["global"]["spec_literal"]["attributed"] / n
    ext = agg["global"]["extended"]["attributed"] / n
    print("   Under CONTEXT.md section 8's OWN detector - the one CH-02 took its gate")
    print("   on, and the one still in force because section 2c was NOT applied -")
    print()
    print("       attribution_completeness = %.4f      **STILL MISSES THE 0.90 GATE**"
          % lit)
    print()
    print("   That is a SECOND FAILURE and it is reported as one. The split metric")
    print("   does not rescue CH-02 on its own; it clears 0.90 (%.4f) only if the" % ext)
    print("   Q9 regex correction is applied at the same time. Both figures ship.")
    print()

    print("-- PER DOCUMENT - attribution_completeness against the 0.90 gate --------")
    for det in ("spec_literal", "extended"):
        vals = []
        for doc, d in per.items():
            g = d[det]
            vals.append((g["attributed"] / g["total"], g["total"], doc))
        vals.sort()
        ge = sum(1 for v, _, _ in vals if v >= GATE)
        print()
        print("   detector = %s" % det)
        print("     documents        : %d" % len(vals))
        print("     >= 0.90          : %d  (%.4f of documents)" % (ge, ge / len(vals)))
        print("     <  0.90          : %d" % (len(vals) - ge))
        print("     == 0.00          : %d" % sum(1 for v, _, _ in vals if v == 0.0))
        print("     unweighted mean  : %.4f" % (sum(v for v, _, _ in vals) / len(vals)))
        print("     min / max        : %.4f / %.4f" % (vals[0][0], vals[-1][0]))
        print("     A per-document FLOOR at 0.90 (90% of documents must clear 0.90)")
        print("     evaluates to %d/%d = %.4f -> %s"
              % (ge, len(vals), ge / len(vals),
                 "PASS" if ge / len(vals) >= GATE else "**FAIL**"))
        print()
        print("     every document BELOW the gate, worst first:")
        print("       %-14s %8s %7s  %s" % ("frdoc", "attr", "elems", "attribution"))
        below = [x for x in vals if x[0] < GATE]
        if not below:
            print("       (zero documents below the gate)")
        for v, tot, doc in below:
            g = per[doc][det]
            print("       %-14s %8d %7d  %.4f" % (doc, g["attributed"], tot, v))
    print()

    print("-- THE FIVE LARGEST DOCUMENTS (50.1% of all elements) -------------------")
    big = sorted(((d["extended"]["total"], doc) for doc, d in per.items()),
                 reverse=True)[:5]
    print("       %-14s %7s %7s  %-9s %-9s" % ("frdoc", "elems", "share",
                                               "attr_ext", "parse"))
    for tot, doc in big:
        g = per[doc]["extended"]
        print("       %-14s %7d %6.1f%%  %.4f    %.4f"
              % (doc, tot, 100 * tot / n, g["attributed"] / tot, g["parsed"] / tot))
    print()
    print("   One document is 24.9% of every element measured. The global figure is")
    print("   therefore dominated by a handful of rules, which is why the")
    print("   per-document view above is reported beside it and not instead of it.")
    print()
    print("=" * 78)
    print("END. Nothing in data/ was written (hard rule 11). The attributor was not run.")
    print("=" * 78)


if __name__ == "__main__":
    main()
