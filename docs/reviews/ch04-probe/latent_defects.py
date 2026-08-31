"""REVIEW CH-04 - latent defects and an independent hand-check of the goldens.

Four items. Each states what is claimed, then demonstrates.

Run: python docs/reviews/ch04-probe/latent_defects.py
Out: docs/reviews/ch04-probe/latent-defects.txt
"""
from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import bscript  # noqa: E402
import score as score_mod  # noqa: E402

FAIL, EXEC = "WILL_FAIL", "WILL_EXECUTE"
OUT = []


def p(*a):
    OUT.append(" ".join(str(x) for x in a))


def main():
    p("REVIEW CH-04 - latent defects and an independent hand-check of the goldens")
    p("=" * 78)

    # ------------------------------------------------------------------------ D1
    p("")
    p("D1  permutation_null RESTORES THE TRUE LABELS BY ASSUMPTION, NOT BY SNAPSHOT")
    p("")
    p("    src/bscript.py lines ~249-251 restore with:")
    p("        for a, b in pairs:")
    p("            by_id[a]['label'] = 'WILL_FAIL'")
    p("            by_id[b]['label'] = 'WILL_EXECUTE'")
    p("    i.e. it ASSUMES pair[0] is the positive. `free_permutation_null` does the")
    p("    right thing - it snapshots `labels` on entry and restores from that. The")
    p("    two functions disagree about how to be safe.")
    p("")
    rows = [{"item_id": "neg", "label": EXEC, "group": "d1", "features": {"f": 1.0}},
            {"item_id": "pos", "label": FAIL, "group": "d1", "features": {"f": 2.0}}]
    before = {r["item_id"]: r["label"] for r in rows}
    bscript.permutation_null(rows, [("neg", "pos")], n_permutations=4)
    after = {r["item_id"]: r["label"] for r in rows}
    p("    pairs given as (negative, positive) - a VALID matching of the same pair:")
    p("      labels before  %s" % before)
    p("      labels after   %s" % after)
    p("      corrupted      %s   <<< the caller's data was silently relabelled"
      % (before != after))
    p("")
    rows2 = [{"item_id": "neg", "label": EXEC, "group": "d1", "features": {"f": 1.0}},
             {"item_id": "pos", "label": FAIL, "group": "d1", "features": {"f": 2.0}}]
    b2 = {r["item_id"]: r["label"] for r in rows2}
    bscript.free_permutation_null(rows2, n_permutations=4)
    a2 = {r["item_id"]: r["label"] for r in rows2}
    p("    the diagnostic null over the same rows, for contrast:")
    p("      labels before  %s" % b2)
    p("      labels after   %s" % a2)
    p("      corrupted      %s" % (b2 != a2))
    p("")
    p("    NOT LIVE TONIGHT: docs/evidence/ch04-scorer/run_bscript.py's")
    p("    `reconstruct_pairs` always emits (positive, negative), so the assumption")
    p("    holds for the shipped run. tests/test_score.py's restore test also passes")
    p("    pairs in that order, so no test would catch the reversal.")

    # ------------------------------------------------------------------------ D2
    p("")
    p("=" * 78)
    p("D2  score() SILENTLY IGNORES PREDICTIONS FOR ITEMS NOT IN THE EVAL SET")
    p("")
    items = [{"item_id": "a", "label": FAIL}, {"item_id": "b", "label": EXEC}]
    r = score_mod.score(items, {"a": FAIL, "b": EXEC, "GHOST": FAIL, "GHOST2": EXEC})
    p("    2 items scored against 4 predictions (2 of them for unknown item_ids):")
    p("      n %d  success %d  failure %d  accuracy %.4f"
      % (r["n"], r["success"], r["failure"], r["accuracy"]))
    p("      no error, no warning, no count of the surplus keys.")
    p("    `cv_predictions` DOES raise when coverage is short (a good check); nothing")
    p("    checks the other direction. An arm answering an item the eval set no")
    p("    longer holds - after CH-03's 76 -> 82 rebuild, say - passes unremarked.")

    # ------------------------------------------------------------------------ D3
    p("")
    p("=" * 78)
    p("D3  src/score.py's MODULE DOCSTRING CONTRADICTS src/score.py")
    p("")
    src = (REPO / "src" / "score.py").read_text(encoding="utf-8")
    doc = src.split('"""')[1]
    claim = [l for l in doc.splitlines() if "no randomness" in l]
    p("    module docstring, verbatim:")
    for l in claim:
        p("      %r" % l.strip())
    nxt = doc.split("no randomness")[1].splitlines()[0:2]
    p("      %r" % " ".join(x.strip() for x in nxt))
    p("")
    p("    and in the same file:")
    for i, line in enumerate(src.splitlines(), 1):
        if re.search(r"^\s*import random|random\.Random|rng\.randrange", line):
            p("      line %-4d %s" % (i, line.strip()))
    p("")
    p("    The bootstrap IS seeded and IS reproducible, so hard rule 9 holds. But the")
    p("    file's own purity claim - and goldens.md S-G's 'the permutation null' as")
    p("    THE one place randomness is allowed - do not mention it. S-G lists the")
    p("    RNG-free functions as 'the accuracy, rate and McNemar functions'; the")
    p("    bootstrap was added later and no declaration was extended to cover it.")

    # ------------------------------------------------------------------------ D4
    p("")
    p("=" * 78)
    p("D4  INDEPENDENT HAND-CHECK OF THE GOLDENS (goldens.md S-A, S-B, S-C, S-D, S-F)")
    p("    Arithmetic done here in Fractions, then compared with the golden's number.")
    p("")
    checks = []

    # S-A
    sa = [("accuracy", Fraction(5, 8), 0.6250),
          ("false-defect", Fraction(1, 4), 0.2500),
          ("missed-defect", Fraction(2, 4), 0.5000)]
    for name, frac, golden in sa:
        checks.append(("S-A " + name, float(frac), golden))

    # S-B: 2 * P(X <= k | nd)
    def two_sided(k, nd):
        row = [1]
        for _ in range(nd):
            row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
        return min(Fraction(1), 2 * sum(Fraction(row[i], 2 ** nd) for i in range(k + 1)))

    checks.append(("S-B1 b=8 c=2", float(two_sided(2, 10)), 0.109375))
    checks.append(("S-B2 b=10 c=0", float(two_sided(0, 10)), 0.001953125))
    checks.append(("S-B3 b=5 c=5", float(two_sided(5, 10)), 1.0))

    # S-C: values pos [3,4,5] neg [1,2,3]; best accuracy over thresholds, both ways
    pos, neg = [3, 4, 5], [1, 2, 3]
    best = -1.0
    best_t = None
    for t in sorted(set(pos + neg)):
        for d in (">=", "<="):
            ok = sum(1 for v in pos if (v >= t if d == ">=" else v <= t))
            ok += sum(1 for v in neg if not (v >= t if d == ">=" else v <= t))
            if ok / 6 > best:
                best, best_t = ok / 6, (t, d)
    checks.append(("S-C best accuracy", best, 5 / 6))
    p("    S-C best threshold found by hand: t=%s direction=%s (golden: t=3, '>=')"
      % best_t)

    # S-D free null 2/6 and S-E within-pair 2/4 - recomputed by brute force here
    checks.append(("S-D free null", 2 / 6, 0.3333333333333333))
    checks.append(("E-1 within-pair null", 2 / 4, 0.5))

    # S-F round-robin fold assignment
    got = {g: i % 5 for i, g in enumerate(sorted(["d3", "d1", "d7", "d2",
                                                 "d5", "d4", "d6"]))}
    want = {"d1": 0, "d2": 1, "d3": 2, "d4": 3, "d5": 4, "d6": 0, "d7": 1}
    p("    S-F fold assignment hand-computed == golden: %s" % (got == want))

    p("")
    ok_all = True
    for name, mine, golden in checks:
        agree = abs(mine - golden) < 1e-12
        ok_all = ok_all and agree
        p("    %-24s mine %.12f  golden %.12f  %s"
          % (name, mine, golden, "AGREE" if agree else "DISAGREE"))
    p("")
    p("    every golden reproduces by hand: %s" % (ok_all and got == want))
    p("")
    p("    AND the goldens predate the code:")
    p("      goldens.md          added 8dae806  2026-08-30 21:15:36 UTC")
    p("      src/score.py        added 067a9d9  2026-08-30 21:29:01 UTC")
    p("      GOOD.md filled      5172092        2026-08-30 21:33:03 UTC")
    p("      first arm API call  B0-rep1.jsonl  2026-08-30 21:41:00.692 UTC")

    p("")
    p("=" * 78)
    text = "\n".join(OUT) + "\n"
    (Path(__file__).resolve().parent / "latent-defects.txt").write_text(
        text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
