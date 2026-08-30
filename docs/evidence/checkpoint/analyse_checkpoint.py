"""★ CHECKPOINT — apply `plan.md`'s decision rule to the measured arms. EXACTLY.

The rule is TOTAL and ORDERED, and this script applies it in that order rather than
reading the numbers and choosing a branch:

    STEP 0  leakage precondition, checked BEFORE any branch.
            If B0 >= 0.70 the instruction text is leaking executability. Strip the
            QUOTED ANCHOR TEXT (keep operation and designation), re-run the gate ONCE,
            and evaluate the branches on the re-run numbers.

    STEP 1  first match wins:
            gap  < 8 pp                      -> RED
            gap >= 8 pp and McNemar p < 0.05 -> GREEN
            gap >= 8 pp and McNemar p >= 0.05-> AMBER

*(The 15 pp figure in `CONTEXT.md` §7 is the PREDICTED effect, not a threshold.)*

No model and no network: it reads the committed run files under
`docs/evidence/checkpoint/` and the frozen eval set.

MAJORITY VOTE ACROSS REPS is the pre-registered aggregation and it is stated here
because it is a choice: each arm's per-item verdict is the majority of its 3 reps,
with an exact tie - impossible at 3 reps unless a rep errored - resolved to the
FAILURE side, so a flaky arm cannot be rescued by a tie-break.

    python docs/evidence/checkpoint/analyse_checkpoint.py
    # committed outputs: checkpoint-result.txt, checkpoint-result.json
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from score import (  # noqa: E402
    bootstrap_ci_clustered,
    detectable_effect,
    mcnemar,
    n_needed_for_power,
    normalise_verdict,
    paired_accuracy_vectors,
    score,
)

HERE = Path(__file__).resolve().parent
EVALSET = REPO / "data/evalset/items.jsonl"

STEP0_B0_THRESHOLD = 0.70
GAP_THRESHOLD_PP = 8.0
ALPHA = 0.05


def load_items():
    items = [json.loads(l) for l in
             EVALSET.read_text(encoding="utf-8").splitlines() if l.strip()]
    return sorted(items, key=lambda i: i["item_id"])


def majority(preds_per_rep, item_ids):
    """Majority verdict per item across reps. Ties -> the FAILURE side.

    A tie is only reachable if a rep errored on that item. Resolving it to the wrong
    answer rather than by coin-flip means a flaky arm is charged for its flakiness.
    """
    out = {}
    for iid in item_ids:
        votes = [normalise_verdict(p.get(iid)) for p in preds_per_rep]
        votes = [v for v in votes if v is not None]
        if not votes:
            out[iid] = None
            continue
        c = Counter(votes).most_common()
        if len(c) > 1 and c[0][1] == c[1][1]:
            out[iid] = "__TIE__"          # never equals a gold label -> counts wrong
        else:
            out[iid] = c[0][0]
    return out


def load_arm(arm, tag="", stripped=False):
    pat = f"{arm}{tag}{'-stripped' if stripped else ''}-rep*.json"
    files = sorted(HERE.glob(pat))
    if not files:
        return None
    return [json.loads(f.read_text(encoding="utf-8")) for f in files]


def evaluate(items, reps):
    ids = [i["item_id"] for i in items]
    gold = [{"item_id": i["item_id"], "label": i["label"]} for i in items]
    maj = majority([r["predictions"] for r in reps], ids)
    sc = score(gold, maj)
    per_rep = [score(gold, r["predictions"])["accuracy"] for r in reps]
    clusters = {i["item_id"]: i["frdoc"] for i in items}
    ci = bootstrap_ci_clustered(gold, maj, clusters)
    return {"score": sc, "majority": maj, "per_rep_accuracy": per_rep, "ci": ci,
            "usage": {"in": sum(r["usage"]["in"] for r in reps),
                      "out": sum(r["usage"]["out"] for r in reps)},
            "errors": sum(len(r["errors"]) for r in reps)}


def gate(items, b0, b0a, label, w):
    def p(*a):
        print(*a, file=w)

    gold = [{"item_id": i["item_id"], "label": i["label"]} for i in items]
    a_vec = paired_accuracy_vectors(gold, b0a["majority"])
    b_vec = paired_accuracy_vectors(gold, b0["majority"])
    mc = mcnemar(a_vec, b_vec)
    gap_pp = 100.0 * (b0a["score"]["accuracy"] - b0["score"]["accuracy"])

    p("")
    p(f"  {label}")
    p(f"    B0        accuracy {b0['score']['accuracy']:.4f}"
      f"   per-rep {['%.4f' % x for x in b0['per_rep_accuracy']]}")
    p(f"    B0-agent  accuracy {b0a['score']['accuracy']:.4f}"
      f"   per-rep {['%.4f' % x for x in b0a['per_rep_accuracy']]}")
    p(f"    gap       {gap_pp:+.1f} pp")
    p(f"    McNemar   p = {mc['p_value']:.4f}   "
      f"(b={mc['b_only_a_correct']} c={mc['c_only_b_correct']} "
      f"discordant={mc['n_discordant']}, exact two-sided binomial)")
    return {"gap_pp": gap_pp, "mcnemar": mc,
            "b0_accuracy": b0["score"]["accuracy"],
            "b0_agent_accuracy": b0a["score"]["accuracy"]}


def branch(gap_pp, p_value):
    """`plan.md` STEP 1. First match wins. TOTAL: every (gap, p) lands in one branch."""
    if gap_pp < GAP_THRESHOLD_PP:
        return "RED", f"gap {gap_pp:.1f} pp < {GAP_THRESHOLD_PP} pp"
    if p_value < ALPHA:
        return "GREEN", f"gap {gap_pp:.1f} pp >= {GAP_THRESHOLD_PP} and p {p_value:.4f} < {ALPHA}"
    return "AMBER", f"gap {gap_pp:.1f} pp >= {GAP_THRESHOLD_PP} and p {p_value:.4f} >= {ALPHA}"


def main() -> int:
    items = load_items()
    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 78)
    p("*** CHECKPOINT - plan.md's decision rule, applied in its own order")
    p("=" * 78)
    p("")
    p(f"  eval set   data/evalset/items.jsonl   n = {len(items)}   "
      f"{sum(1 for i in items if i['label'] == 'WILL_FAIL')} positive / "
      f"{sum(1 for i in items if i['label'] == 'WILL_EXECUTE')} negative")
    p(f"  aggregation across reps: MAJORITY, ties resolved to the FAILURE side")
    p("")

    b0_reps, b0a_reps = load_arm("B0"), load_arm("B0-agent")
    if not b0_reps or not b0a_reps:
        p("  ARMS NOT PRESENT - run `python -m arms run` first.")
        print(w.getvalue(), end="")
        return 1

    b0, b0a = evaluate(items, b0_reps), evaluate(items, b0a_reps)

    p("=" * 78)
    p("STEP 0 - leakage precondition, checked BEFORE any branch")
    p("=" * 78)
    p("")
    p(f"  B0 accuracy = {b0['score']['accuracy']:.4f}   "
      f"threshold {STEP0_B0_THRESHOLD}")
    step0_fired = b0["score"]["accuracy"] >= STEP0_B0_THRESHOLD
    if step0_fired:
        p("  B0 >= 0.70: THE INSTRUCTION TEXT IS LEAKING EXECUTABILITY.")
        p("  The gate must be re-run ONCE with the quoted anchor text stripped, and")
        p("  the branches evaluated on the RE-RUN numbers.")
    else:
        p("  B0 < 0.70: the precondition does not fire. The branch table is")
        p("  evaluated on these numbers.")

    p("")
    p("=" * 78)
    p("THE ARMS")
    p("=" * 78)
    first = gate(items, b0, b0a, "as run", w)

    used = first
    rerun = None
    if step0_fired:
        b0_s, b0a_s = load_arm("B0", stripped=True), load_arm("B0-agent", stripped=True)
        if b0_s and b0a_s:
            b0s, b0as = evaluate(items, b0_s), evaluate(items, b0a_s)
            rerun = gate(items, b0s, b0as, "STEP 0 re-run, quoted anchors stripped", w)
            used = rerun
        else:
            p("")
            p("  STEP 0 FIRED BUT THE RE-RUN IS ABSENT. The branch is NOT taken on the")
            p("  as-run numbers - that would be exactly the error plan.md's STEP 0 was")
            p("  written to prevent. Run:")
            p("    python -m arms run --strip-anchors")
            print(w.getvalue(), end="")
            return 2

    verdict, why = branch(used["gap_pp"], used["mcnemar"]["p_value"])

    p("")
    p("=" * 78)
    p("STEP 1 - the branch table. First match wins.")
    p("=" * 78)
    p("")
    p(f"  BRANCH: {verdict}")
    p(f"  because {why}")
    p(f"  evaluated on the {'STEP 0 RE-RUN' if rerun else 'as-run'} numbers")
    p("")

    p("=" * 78)
    p("GUARDS - CONTEXT.md section 7, per arm, never blended")
    p("=" * 78)
    p("")
    for name, r in (("B0", b0), ("B0-agent", b0a)):
        s = r["score"]
        p(f"  {name:<10} success+failure {s['success']}+{s['failure']}={s['n']}"
          f"   false-defect {s['false_defect_rate']:.4f}"
          f" {'PASS' if s['guard_false_defect_pass'] else 'FAIL'}"
          f"   missed-defect {s['missed_defect_rate']:.4f}"
          f" {'PASS' if s['guard_missed_defect_pass'] else 'FAIL'}"
          f"   unparseable {s['unparseable_or_absent']}   errors {r['errors']}")
        p(f"             95% CI (clustered by FR doc) "
          f"[{r['ci']['ci_low']:.4f}, {r['ci']['ci_high']:.4f}]")
    p("")

    power = detectable_effect(len(items) // 2)
    p("=" * 78)
    p("WHAT THIS n CAN AND CANNOT DETECT - GOOD.md section 4")
    p("=" * 78)
    p("")
    p(f"  pairs {power['n_pairs']}, n {power['n_items']}")
    p(f"  smallest ALL-ONE-WAY discordant count clearing alpha: "
      f"{power['min_discordant_all_one_way']}  -> floor "
      f"{power['min_detectable_gap_pp']:.1f} pp")
    p(f"  GOOD.md section 4: the pre-registered success criterion requires n >= 84.")
    p(f"  n = {len(items)}. THE CRITERION IS NOT SATISFIABLE ON THIS CORPUS and 84")
    p(f"  was not moved to {len(items)}.")
    p("")
    need = n_needed_for_power(used["mcnemar"]["b_only_a_correct"],
                             used["mcnemar"]["c_only_b_correct"], len(items))
    if verdict == "AMBER":
        p("  plan.md's AMBER branch: \"the README leads with effect size, its")
        p("  confidence interval, and THE n THIS DESIGN WOULD NEED FOR POWER.\"")
        p("")
        p(f"    observed discordance      b={need['observed_b']} c={need['observed_c']}"
          f"  ({need['observed_discordant']} of {need['n_items']}, rate "
          f"{need['discordant_rate']:.3f})")
        p(f"    discordant pairs needed   {need['discordant_needed']}")
        p(f"    n NEEDED FOR POWER        {need['n_needed']}"
          f"   ({need['pairs_needed']} pairs)  vs the {len(items)} we have")
        p(f"    {need['note']}")
        p("")

    # sensitivity subset, if present
    sb0, sb0a = load_arm("B0", tag="-sonnet"), load_arm("B0-agent", tag="-sonnet")
    sens = None
    if sb0 and sb0a:
        sub_ids = set(sb0[0]["predictions"]) | {e["item_id"] for e in sb0[0]["errors"]}
        sub = [i for i in items if i["item_id"] in sub_ids]
        s0, s0a = evaluate(sub, sb0), evaluate(sub, sb0a)
        # The ONLY fair comparison is haiku on the SAME 20 items. Comparing a
        # 20-item sonnet gap against the FULL-CORPUS haiku gap would be comparing two
        # different item sets and calling the difference a model effect.
        h0, h0a = evaluate(sub, b0_reps), evaluate(sub, b0a_reps)
        sens = {"n": len(sub),
                "b0": s0["score"]["accuracy"], "b0_agent": s0a["score"]["accuracy"],
                "gap_pp": 100.0 * (s0a["score"]["accuracy"] - s0["score"]["accuracy"]),
                "haiku_same_items_b0": h0["score"]["accuracy"],
                "haiku_same_items_b0_agent": h0a["score"]["accuracy"],
                "haiku_same_items_gap_pp": 100.0 * (h0a["score"]["accuracy"]
                                                    - h0["score"]["accuracy"]),
                "haiku_full_corpus_gap_pp": first["gap_pp"]}
        p("=" * 78)
        p("MODEL-SENSITIVITY CHECK - claude-sonnet-5, 1 rep, the pre-registered subset")
        p("=" * 78)
        p("")
        p(f"  {'arm':<26}{'B0':>10}{'B0-agent':>12}{'gap':>10}")
        p(f"  {'claude-sonnet-5, n=20':<26}{sens['b0']:>10.4f}"
          f"{sens['b0_agent']:>12.4f}{sens['gap_pp']:>+9.1f} pp")
        p(f"  {'haiku, THE SAME 20 items':<26}{sens['haiku_same_items_b0']:>10.4f}"
          f"{sens['haiku_same_items_b0_agent']:>12.4f}"
          f"{sens['haiku_same_items_gap_pp']:>+9.1f} pp")
        p(f"  {f'haiku, full corpus n={len(items)}':<26}{b0['score']['accuracy']:>10.4f}"
          f"{b0a['score']['accuracy']:>12.4f}{first['gap_pp']:>+9.1f} pp")
        p("")
        p("  The haiku row on the SAME 20 items is the only fair comparison. A")
        p(f"  20-item sonnet gap set against an {len(items)}-item haiku gap would be")
        p("  two different item sets with the difference called a model effect.")
        p("")
        p("  QUESTIONS.md Q1 anticipated the OPPOSITE failure - that a cheap model")
        p("  would fail to use the text and we would kill a sound project on weak")
        p("  inference. What was measured is the reverse: the CHEAPER model gains")
        p("  from the text and the STRONGER one loses. The RED branch was not taken")
        p(f"  and this does not rescue or threaten the {verdict} branch either way,")
        p("  which is decided on the full-corpus haiku arms alone.")
        p("")
        p("  THREE REASONS NOT TO OVER-READ THIS, stated before anyone else says them:")
        p(f"   1. n = 20, ONE rep. The haiku arms are n = {len(items)} and three reps.")
        p("   2. A CONFOUND, not merely a limitation: sonnet-5 REJECTS `temperature`")
        p("      (HTTP 400, measured), so this subset ran at the model default while")
        p("      every haiku arm ran at 0. A sampling difference is a live")
        p("      alternative explanation for a reversal of this size and it has not")
        p("      been ruled out.")
        p(f"   3. One rep gives no variance estimate at all, so the "
          f"{sens['gap_pp']:+.1f} pp has no")
        p("      interval around it.")
        p("")
        p("  It is reported because it was pre-registered and run, not because it is")
        p("  a result this project wanted. CH-08 can settle it with reps at a")
        p("  matched sampling setting; tonight it is a flag, not a finding.")
        p("")

    text = w.getvalue()
    (HERE / "checkpoint-result.txt").write_text(text, encoding="utf-8", newline="\n")
    (HERE / "checkpoint-result.json").write_text(json.dumps({
        "branch": verdict, "because": why,
        "step0_fired": step0_fired,
        "evaluated_on": "step0-rerun" if rerun else "as-run",
        "as_run": {k: v for k, v in first.items() if k != "mcnemar"}
                  | {"mcnemar": first["mcnemar"]},
        "step0_rerun": ({k: v for k, v in rerun.items() if k != "mcnemar"}
                        | {"mcnemar": rerun["mcnemar"]}) if rerun else None,
        "b0": {k: v for k, v in b0["score"].items() if k != "per_item"},
        "b0_agent": {k: v for k, v in b0a["score"].items() if k != "per_item"},
        "b0_ci": b0["ci"], "b0_agent_ci": b0a["ci"],
        "b0_per_rep": b0["per_rep_accuracy"],
        "b0_agent_per_rep": b0a["per_rep_accuracy"],
        "usage": {"b0": b0["usage"], "b0_agent": b0a["usage"]},
        "detectable_effect": power,
        "n_needed_for_power": n_needed_for_power(
            used["mcnemar"]["b_only_a_correct"],
            used["mcnemar"]["c_only_b_correct"], len(items)),
        "sensitivity": sens,
        "n": len(items),
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
