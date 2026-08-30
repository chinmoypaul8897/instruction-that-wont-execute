#!/usr/bin/env python3
"""SPEC-FIX-1 - the discriminating-power test for the PROPOSED gate metric.

`prompts/SPEC-FIX-1.md` section 2a proposes

    attribution_completeness = (elements attributed to a section) / (total elements)

as the new gate metric, and asserts of it: "This is the gate metric. It answers the
question the gate exists to answer" - namely *"did carry-forward put each instruction on
the RIGHT section?"*

That is a factual claim about a metric, so it is testable. This script tests it by
building a deliberately sabotaged attributor and scoring it on the same metric:

    SABOTAGE: pin every element to the FIRST section named anywhere in its document.
              Same unattributable rule - an element before the first named section is
              unattributable. Carry-forward is otherwise destroyed.

If the sabotaged attributor scores the same as the real one, the metric cannot
distinguish a correct attributor from a broken one, and the claim in section 2a is
false. Hard rule 14: the script ships with its output; hard rule 15: this is checked
here rather than taken from another agent's report.

Reads only. `data/` is sealed (hard rule 11). No clock, no network, no randomness.

Usage:  python docs/evidence/spec-fix-1/spec_fix_1_sabotage.py
"""
import io
import json
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")

ROOT = Path(__file__).resolve().parents[3]
AMDPARS = ROOT / "data" / "amdpars" / "amdpars.jsonl"
COMPLETENESS = ROOT / "data" / "amdpars" / "completeness.json"
GATE = 0.90


def by_document(recs):
    docs = defaultdict(list)
    for r in recs:
        docs[r["frdoc"]].append(r)
    for k in docs:
        docs[k].sort(key=lambda r: r["ordinal"])
    return OrderedDict(sorted(docs.items()))


def real_attribution(rows, det):
    """CONTEXT.md section 8 step 3/4, replayed: carry the LAST-named section forward."""
    out, cur = [], None
    for r in rows:
        named = r["sections_named_" + det]
        if named:
            cur = named[0]
        out.append(cur)
    return out


def sabotage_attribution(rows, det):
    """The control: carry the FIRST-named section of the document forward, forever."""
    out, first = [], None
    for r in rows:
        named = r["sections_named_" + det]
        if named and first is None:
            first = named[0]
        out.append(first)
    return out


def main():
    recs = [json.loads(l) for l in AMDPARS.open(encoding="utf-8")]
    agg = json.loads(COMPLETENESS.read_text(encoding="utf-8"))
    n = len(recs)
    docs = by_document(recs)

    print("=" * 78)
    print("SPEC-FIX-1 - does the PROPOSED gate metric discriminate?")
    print("=" * 78)
    print("records : %d over %d FR documents" % (n, len(docs)))
    print()

    for det in ("spec_literal", "extended"):
        print("-- detector = %s %s" % (det, "-" * (56 - len(det))))
        real_all, sab_all, elems = [], [], []
        for _, rows in docs.items():
            real_all += real_attribution(rows, det)
            sab_all += sabotage_attribution(rows, det)
            elems += rows

        # 1. replay must reproduce the frozen record before anything is concluded
        frozen = [r["section_" + det] for r in elems]
        mismatch = sum(1 for a, b in zip(real_all, frozen) if a != b)
        print("   replay of CONTEXT.md section 8 vs the frozen record : "
              "%d mismatches of %d" % (mismatch, n))
        assert mismatch == 0, "replay does not reproduce the frozen attributor"
        print("   ASSERTED: the replay IS the shipped attributor, so the control below")
        print("   differs from it in exactly one respect - first-named vs last-named.")
        print()

        real_att = sum(1 for s in real_all if s is not None)
        sab_att = sum(1 for s in sab_all if s is not None)
        differ = sum(1 for a, b in zip(real_all, sab_all)
                     if a != b and a is not None)

        print("   REAL      attribution_completeness = %d/%d = %.4f  -> %s"
              % (real_att, n, real_att / n, "PASS" if real_att / n >= GATE else "FAIL"))
        print("   SABOTAGED attribution_completeness = %d/%d = %.4f  -> %s"
              % (sab_att, n, sab_att / n, "PASS" if sab_att / n >= GATE else "FAIL"))
        print("   difference in the metric            = %.6f"
              % abs(real_att / n - sab_att / n))
        print("   elements the sabotage puts on a DIFFERENT section = %d of %d "
              "attributed = %.4f" % (differ, real_att, differ / real_att))
        print()
        if real_att == sab_att:
            print("   >>> IDENTICAL. The metric cannot tell the two attributors apart,")
            print("       though they disagree about %d of %d attributed elements."
                  % (differ, real_att))
            print("       This is not a coincidence: an element is attributed iff at")
            print("       least one section was named at or before it, which is true of")
            print("       BOTH rules. attributed/total therefore measures only WHERE THE")
            print("       FIRST CITATION APPEARS - it is invariant to whether the")
            print("       carry-forward that follows is right or wrong.")
        else:
            print("   >>> the two differ; the metric has some discriminating power here.")
        print()

        # 2. the predecessor's failure mode - which the metric DOES catch
        leadin_att = sum(1 for r in elems if r["names_section_" + det])
        print("   CONTROL 2 - the predecessor pilot's failure mode (lead-ins only, no")
        print("   carry-forward at all): attribution_completeness = %d/%d = %.4f -> %s"
              % (leadin_att, n, leadin_att / n,
                 "PASS" if leadin_att / n >= GATE else "FAIL"))
        print("       So the metric DOES catch the silent-DROP failure that killed the")
        print("       predecessor at 0.46. It is blind only to the silent-WRONG failure")
        print("       that CH-02 actually found in this corpus (Q9).")
        print()

    # 3. the coupling: which edits are load-bearing for the pass
    print("-- WHICH OF SPEC-FIX-1's EDITS IS LOAD-BEARING FOR THE PASS? ------------")
    lit, ext = agg["global"]["spec_literal"], agg["global"]["extended"]
    table = [
        ("neither edit  (status quo: CONTEXT.md section 8 as written)",
         lit["complete"] / n),
        ("2a only       (split the metric, keep section 8's sign-only regex)",
         lit["attributed"] / n),
        ("2c only       (fix the regex, keep the combined definition)",
         ext["complete"] / n),
        ("2a + 2c       (both, as SPEC-FIX-1 proposes)",
         ext["attributed"] / n),
    ]
    for label, v in table:
        print("   %-62s %.4f  %s"
              % (label, v, "PASS" if v >= GATE else "FAIL"))
    print()
    print("   The pass exists only in the last row. Neither edit alone clears 0.90.")
    print()

    # 4. the strictly-harder ladder, all from already-frozen booleans
    print("-- THE STRICTLY-HARDER LADDER, FROM FROZEN FIELDS ONLY ------------------")
    att = [r for r in recs if r["attributed_extended"]]
    pm_all = sum(1 for r in recs if r["part_mismatch_extended"])
    pm_self = sum(1 for r in recs
                  if r["part_mismatch_extended"] and r["names_section_extended"])
    pm_carried = pm_all - pm_self
    both = [r for r in recs
            if r["attributed_extended"] and r["attributed_spec_literal"]]
    rival = sum(1 for r in both
                if r["section_extended"] != r["section_spec_literal"])
    disagree = sum(1 for r in recs if r["detector_disagrees"])

    print("   part_mismatch_extended                       : %d" % pm_all)
    print("     ... of which name their OWN section        : %d  (QUESTIONS.md Q10 says"
          % pm_self)
    print("         'every one of those is wrong' - for these %d the section is right"
          % pm_self)
    print("         and the REGTEXT part tag is the thing that disagrees)")
    print("     ... of which inherited by carry-forward    : %d" % pm_carried)
    print("   detector_disagrees (raw flag)                : %d" % disagree)
    print("     ... genuine rival-section conflicts        : %d  (both detectors named a"
          % rival)
    print("         section AND the two sections differ)")
    print("     ... spec_literal simply found nothing      : %d" % (disagree - rival))
    print()

    ladder = []
    ladder.append(("L0  attributed (SPEC-FIX-1 section 2a as proposed)",
                   len(att)))
    ladder.append(("L1  attributed AND part-consistent",
                   sum(1 for r in att if not r["part_mismatch_extended"])))
    ladder.append(("L2  attributed AND no CARRIED part mismatch",
                   sum(1 for r in att
                       if not (r["part_mismatch_extended"]
                               and not r["names_section_extended"]))))
    ladder.append(("L3  attributed AND no rival-section conflict",
                   sum(1 for r in att
                       if not (r["attributed_spec_literal"]
                               and r["section_extended"] != r["section_spec_literal"]))))
    ladder.append(("L4  attributed AND part-consistent AND no rival conflict",
                   sum(1 for r in att
                       if not r["part_mismatch_extended"]
                       and not (r["attributed_spec_literal"]
                                and r["section_extended"] != r["section_spec_literal"]))))
    for label, k in ladder:
        print("   %-56s %d/%d = %.4f  %s"
              % (label, k, n, k / n, "PASS" if k / n >= GATE else "FAIL"))
    print()

    # 5. per-document floor
    print("-- PER-DOCUMENT FLOOR (the aggregation CONTEXT.md section 8 already ------")
    print("   requires be reported, and CH-02's branch table restricts on) -----------")
    for det in ("extended", "spec_literal"):
        per = []
        for _, rows in docs.items():
            a = sum(1 for r in rows if r["attributed_" + det])
            per.append(a / len(rows))
        ge = sum(1 for v in per if v >= GATE)
        print("   %-13s docs with attribution_completeness >= 0.90 : %d/%d = %.4f  %s"
              % (det, ge, len(per), ge / len(per),
                 "PASS" if ge / len(per) >= GATE else "FAIL"))
        print("   %-13s unweighted per-document mean = %.4f   min = %.4f"
              % ("", sum(per) / len(per), min(per)))
    print()

    # 6. golden G1 - the document CH-02 chose to demonstrate the failure mode
    print("-- GOLDEN G1 (FR 2020-11897), the document chosen to DEMONSTRATE the -----")
    print("   silent-WRONG failure mode -----------------------------------------------")
    g1 = docs.get("2020-11897", [])
    if not g1:
        print("   G1 NOT PRESENT in the corpus (0 elements) - reported as zero.")
    else:
        for det in ("spec_literal", "extended"):
            a = sum(1 for r in g1 if r["attributed_" + det])
            c = sum(1 for r in g1 if r["complete_" + det])
            print("   %-13s attribution_completeness = %d/%d = %.4f -> %s   "
                  "(old completeness %d/%d = %.4f -> %s)"
                  % (det, a, len(g1), a / len(g1),
                     "PASS" if a / len(g1) >= GATE else "FAIL",
                     c, len(g1), c / len(g1),
                     "PASS" if c / len(g1) >= GATE else "FAIL"))
        dis = sum(1 for r in g1 if r["detector_disagrees"])
        print("   elements the two detectors put on different sections : %d of %d"
              % (dis, len(g1)))
        print("   QUESTIONS.md Q9 records 20 of these 28 as pinned to a section they do")
        print("   not amend under spec_literal. The proposed gate scores that document")
        print("   %.4f and PASSES it." % (sum(1 for r in g1
                                              if r["attributed_spec_literal"]) / len(g1)))
    print()
    print("=" * 78)
    print("END. Nothing in data/ was written (hard rule 11).")
    print("=" * 78)


if __name__ == "__main__":
    main()
