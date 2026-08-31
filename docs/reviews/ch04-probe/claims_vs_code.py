"""REVIEW CH-04 - check 6, every load-bearing CLAIM in the code and in `GOOD.md`,
tested against what the code actually does.

Five claims are put on trial. Each section states the claim verbatim, then measures.

Run: python docs/reviews/ch04-probe/claims_vs_code.py
Out: docs/reviews/ch04-probe/claims-vs-code.txt
"""
from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import bscript  # noqa: E402
import score as score_mod  # noqa: E402

FAIL, EXEC = "WILL_FAIL", "WILL_EXECUTE"
OUT = []


def p(*a):
    OUT.append(" ".join(str(x) for x in a))


def lenient(raw):
    """The M06 mutation the suite did not catch: prose containing the word counts."""
    if raw is None:
        return None
    t = str(raw).strip().strip('"').strip("'").upper()
    if FAIL in t:
        return FAIL
    if EXEC in t:
        return EXEC
    return None


def main():
    items = sorted((json.loads(l) for l in
                    (REPO / "data/evalset/items.jsonl")
                    .read_text(encoding="utf-8").splitlines() if l.strip()),
                   key=lambda i: i["item_id"])
    gold = {i["item_id"]: i["label"] for i in items}
    ckpt = REPO / "docs/evidence/checkpoint"

    p("REVIEW CH-04 - check 6: claims vs code")
    p("=" * 78)

    # ------------------------------------------------------------------ CLAIM 1
    p("")
    p("CLAIM 1  src/score.py normalise_verdict: \"Deliberately strict ... Anything")
    p("         else - prose, a refusal, an empty string, a JSON blob without the")
    p("         field - returns None and is scored as a FAILURE.\"")
    p("")
    p("  The strictness is REAL, but mutation M06 (substring match instead of exact)")
    p("  survives the whole 313-test suite. Measured cost on the REAL B0 reps:")
    p("")
    total_flipped = 0
    for arm, files in (("B0", ["B0-rep1.json", "B0-rep2.json", "B0-rep3.json"]),
                       ("B0-agent", ["B0-agent-rep1.json", "B0-agent-rep2.json",
                                     "B0-agent-rep3.json"])):
        for f in files:
            preds = json.loads((ckpt / f).read_text(encoding="utf-8"))["predictions"]
            strict = {k: score_mod.normalise_verdict(v) for k, v in preds.items()}
            loose = {k: lenient(v) for k, v in preds.items()}
            flipped = [k for k in preds if strict[k] is None and loose[k] is not None]
            total_flipped += len(flipped)
            sa = sum(1 for k, g in gold.items() if strict.get(k) == g) / len(gold)
            la = sum(1 for k, g in gold.items() if loose.get(k) == g) / len(gold)
            p("    %-24s strict acc %.4f   lenient acc %.4f   "
              "non-answers rescued %d" % (f, sa, la, len(flipped)))
    p("")
    p("  non-answers a lenient parser would have converted, across all 6 reps: %d"
      % total_flipped)
    p("")
    p("  Zero on TONIGHT's data - the B0 prose non-answers happen not to contain")
    p("  either literal. The exposure is CH-06's A1, whose output contract is a JSON")
    p("  blob that DOES contain the verdict string:")
    blob = '{"verdict": "WILL_FAIL", "failing_designation": "(b)(4)"}'
    p("    raw     %s" % blob)
    p("    strict  -> %r   (a non-answer: the scorer wants the bare verdict)"
      % score_mod.normalise_verdict(blob))
    p("    lenient -> %r   (M06 would silently start accepting it)" % lenient(blob))
    p("  VERDICT: score.py is correct here; the SUITE does not defend it.")

    # ------------------------------------------------------------------ CLAIM 2
    p("")
    p("=" * 78)
    p("CLAIM 2  GOOD.md section 5, pre-registered and frozen:")
    p("           \"The observed labelling is one of the draws, so p can never be 0.\"")
    p("         src/bscript.py module docstring, point 2:")
    p("           \"The observed statistic is included in its own null. A permutation")
    p("            test that excludes it can return p = 0, which is not a probability")
    p("            any finite permutation test can produce.\"")
    p("")
    p("  TRUE in EXHAUSTIVE mode - itertools.product contains the all-keep draw.")
    p("  In SAMPLED mode the draws are independent coin flips, so the all-keep draw")
    p("  appears with probability 2^-k per draw. The shipped run uses k = 41 pairs")
    p("  and 2000 SAMPLED draws: 2^-41 = %.3e per draw. The claim does not hold"
      % (2.0 ** -41))
    p("  there, and `p_value = at_least / len(draws)` carries no +1 correction.")
    p("")
    p("  DIRECT CHECK on the SHIPPED configuration - is the observed labelling")
    p("  (the all-keep draw) actually among the 2000 draws at seed 20260831?")
    rng41 = random.Random(bscript.PERMUTATION_SEED)
    draws41, mode41 = bscript._within_pair_draws(
        [("p%02d" % i, "n%02d" % i) for i in range(41)], rng41,
        bscript.N_PERMUTATIONS)
    p("    k = 41 pairs, n_permutations = %d -> mode %r, %d draws"
      % (bscript.N_PERMUTATIONS, mode41, len(draws41)))
    p("    all-keep draw present : %s" % ((False,) * 41 in draws41))
    p("    all-swap draw present : %s" % ((True,) * 41 in draws41))
    p("    -> the observed labelling is NOT one of the draws.")
    p("")
    p("  Constructed counterexample where p ACTUALLY comes out 0.0 -")
    p("  20 pairs, positives all 1.0, negatives all 0.0, so ONLY the all-keep and")
    p("  all-swap draws (2 of 2^20) can reach the observed 1.0, and 200 sampled")
    p("  draws contain neither:")
    rows = []
    pairs = []
    for i in range(20):
        pos, neg = "p%02d" % i, "n%02d" % i
        rows.append({"item_id": pos, "label": FAIL, "group": "d%02d" % i,
                     "features": {"f": 1.0}})
        rows.append({"item_id": neg, "label": EXEC, "group": "d%02d" % i,
                     "features": {"f": 0.0}})
        pairs.append((pos, neg))
    r = bscript.permutation_null(rows, pairs, n_permutations=200)
    p("    mode                     %s" % r["mode"])
    p("    n_draws                  %d" % r["n_draws"])
    p("    observed best CV acc     %.4f" % r["observed_best_cv_accuracy"])
    p("    draws >= observed        %d" % r["draws_at_or_above_observed"])
    p("    p_value                  %r" % r["p_value"])
    p("    p_value == 0.0           %s   <<< a finite permutation test just"
      % (r["p_value"] == 0.0))
    p("                                      produced p = 0, which GOOD.md section 5")
    p("                                      and bscript.py both say cannot happen")
    p("    conventional (1+k)/(1+n) %r"
      % ((1 + r["draws_at_or_above_observed"]) / (1 + r["n_draws"])))
    p("")
    p("  The SHIPPED run was not bitten - 471/2000 draws >= observed, p = 0.2355 -")
    p("  because the B-script is near chance. The claim is still false as written,")
    p("  and it is frozen in GOOD.md where hard rule 5 forbids editing it.")
    p("")
    p("  tests/test_score.py::test_SD_p_value_can_never_be_zero uses 2 pairs and")
    p("  n_permutations=64, which takes the EXHAUSTIVE branch. The mode the project")
    p("  actually runs in is not covered by that test:")
    small = bscript.permutation_null(
        [{"item_id": "a", "label": FAIL, "group": "d1", "features": {"f": 9.0}},
         {"item_id": "c", "label": EXEC, "group": "d1", "features": {"f": 1.0}},
         {"item_id": "b", "label": FAIL, "group": "d2", "features": {"f": 8.0}},
         {"item_id": "d", "label": EXEC, "group": "d2", "features": {"f": 2.0}}],
        [("a", "c"), ("b", "d")], n_permutations=64)
    p("    the test's own call -> mode %r, p %.4f" % (small["mode"], small["p_value"]))

    # ------------------------------------------------------------------ CLAIM 3
    p("")
    p("=" * 78)
    p("CLAIM 3  src/score.py bootstrap_ci_clustered docstring:")
    p("           \"`CONTEXT.md` section 7 / `plan.md` CH-08: clustered by FR")
    p("            document.\"")
    p("")
    ctx = (REPO / "CONTEXT.md").read_text(encoding="utf-8")
    s7 = ctx.split("## 7. Metrics")[1].split("## 8.")[0]
    p("  grep of CONTEXT.md section 7 for 'bootstrap': %d hits"
      % s7.lower().count("bootstrap"))
    p("  grep of CONTEXT.md section 7 for 'cluster'  : %d hits"
      % s7.lower().count("cluster"))
    p("  grep of CONTEXT.md (whole file) for 'bootstrap': %d hits"
      % ctx.lower().count("bootstrap"))
    p("  grep of GOOD.md for 'bootstrap': %d hits"
      % (REPO / "GOOD.md").read_text(encoding="utf-8").lower().count("bootstrap"))
    p("  plan.md CH-08 does require it: %s"
      % ("paired bootstrap **clustered by FR document**"
         in (REPO / "plan.md").read_text(encoding="utf-8")))
    p("  -> section 7 does NOT mention a bootstrap. The citation is wrong.")
    p("     plan.md CH-08 asks for a PAIRED bootstrap of the DIFFERENCE;")
    p("     bootstrap_ci_clustered returns a one-arm accuracy CI, which is not that.")
    p("")
    p("  Mutation M12 (resample items, not clusters) survived the suite. Measured")
    p("  cost, my own reimplementation, 2000 reps, seed 424242, on B0-agent:")
    b0a = json.loads((ckpt / "B0-agent-rep1.json").read_text(encoding="utf-8"))
    preds = b0a["predictions"]
    hit = {i["item_id"]: score_mod.normalise_verdict(preds.get(i["item_id"]))
           == i["label"] for i in items}
    by_doc = {}
    for i in items:
        by_doc.setdefault(i["frdoc"], []).append(i["item_id"])
    keys = sorted(by_doc)
    ids = [i["item_id"] for i in items]
    for label, draw in (("clustered by frdoc", "cluster"), ("by ITEM", "item")):
        rng = random.Random(424242)
        accs = []
        for _ in range(2000):
            if draw == "cluster":
                flat = [x for _ in keys
                        for x in by_doc[keys[rng.randrange(len(keys))]]]
            else:
                flat = [ids[rng.randrange(len(ids))] for _ in ids]
            accs.append(sum(hit[x] for x in flat) / len(flat))
        accs.sort()
        lo, hi = accs[50], accs[1949]
        p("    %-20s CI [%.4f, %.4f]  width %.4f  sd %.4f"
          % (label, lo, hi, hi - lo, statistics.pstdev(accs)))
    p("  -> the item bootstrap is NARROWER. Using it would overstate precision,")
    p("     and nothing in tests/ would notice.")

    # ------------------------------------------------------------------ CLAIM 4
    p("")
    p("=" * 78)
    p("CLAIM 4  src/score.py detectable_effect(n_pairs, alpha=0.05, power=0.80)")
    p("         returns a field named `target_power`.")
    p("")
    for pw in (0.50, 0.80, 0.99, 0.0):
        d = score_mod.detectable_effect(41, power=pw)
        p("    power=%.2f -> min_discordant %s  gap %.4f pp  target_power reported %.2f"
          % (pw, d["min_discordant_all_one_way"], d["min_detectable_gap_pp"],
             d["target_power"]))
    p("  -> `power` changes NOTHING. It is echoed into the output as `target_power`")
    p("     beside a number that is not a power calculation. The docstring's closing")
    p("     note says so; the emitted field does not, and checkpoint-result.json")
    p("     carries \"target_power\": 0.8 next to \"min_detectable_gap_pp\": 7.317.")
    p("")
    p("  Also: min_discordant_all_one_way does not depend on n at all -")
    for n_pairs in (5, 41, 1000):
        d = score_mod.detectable_effect(n_pairs)
        p("    n_pairs=%-5d min_discordant %s  gap %.4f pp"
          % (n_pairs, d["min_discordant_all_one_way"], d["min_detectable_gap_pp"]))
    p("     only the implied gap moves, because it is 100 * 6 / (2 * n_pairs).")

    # ------------------------------------------------------------------ CLAIM 5
    p("")
    p("=" * 78)
    p("CLAIM 5  src/score.py n_needed_for_power - the NAME says power, the")
    p("         docstring says \"not a power calculation from an assumed effect\".")
    p("")
    r = score_mod.n_needed_for_power(21, 6, 82)
    p("    n_needed_for_power(b=21, c=6, n_items=82) -> n_needed %s (pairs %s)"
      % (r["n_needed"], r["pairs_needed"]))
    p("    the observed data ALREADY clears alpha (p = 0.0059), so the search stops")
    p("    at d_try = d and returns the n it was given. It answers 'how big is the")
    p("    n I already have', which is not what plan.md's AMBER branch asks for.")
    p("    plan.md AMBER: \"the n this design would need for power\".")
    p("")
    p("    a genuinely under-powered shape, b=6 c=3 at n=82:")
    r2 = score_mod.n_needed_for_power(6, 3, 82)
    p("      -> discordant_needed %s  n_needed %s  pairs_needed %s"
      % (r2["discordant_needed"], r2["n_needed"], r2["pairs_needed"]))
    p("    no `power` argument exists and no target power is used anywhere in it.")
    p("    Mutation M15 (flip the significance comparison) survived the suite: the")
    p("    function has NO test at all.")

    p("")
    p("=" * 78)
    dest = Path(__file__).resolve().parent / "claims-vs-code.txt"
    text = "\n".join(OUT) + "\n"
    dest.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
