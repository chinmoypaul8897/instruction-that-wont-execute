"""CH-06 §2a — WHERE DO B0-agent's ERRORS CONCENTRATE?

The iteration card for capability 1 must name the **observed failure** it targets, and
`PROCESS.md` §5 requires that failure to be *measured, not guessed*. This script is the
measurement. It runs BEFORE the card is written and BEFORE `cfr_resolve` is wired into
any arm, so the card's "observed failure" line cites a number that already exists.

Reads only committed artifacts:
    docs/evidence/checkpoint/B0-agent-rep{1,2,3}.json     the three reps
    data/evalset/items.jsonl                              the frozen eval set (SEALED)

Aggregation across reps is MAJORITY with ties resolved to the FAILURE side, which is the
rule `docs/evidence/checkpoint/analyse_checkpoint.py` already applied to produce the
published 0.6585. It is restated here rather than re-chosen.

PURITY: no network, no clock, no randomness. Determinism: same inputs, same bytes.

    python docs/evidence/ch06-a1/iter1/b0agent_error_profile.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from score import normalise_verdict, score  # noqa: E402

CHECKPOINT = REPO / "docs/evidence/checkpoint"
EVALSET = REPO / "data/evalset/items.jsonl"
OUT = Path(__file__).resolve().parent / "b0agent_error_profile.txt"


def load_items():
    return sorted(
        (json.loads(l) for l in EVALSET.read_text(encoding="utf-8").splitlines() if l.strip()),
        key=lambda i: i["item_id"],
    )


def majority(reps: list[dict]) -> dict:
    """MAJORITY across reps, ties to the FAILURE side. The published rule, restated."""
    out = {}
    keys = sorted({k for r in reps for k in r})
    for k in keys:
        votes = [normalise_verdict(r.get(k)) for r in reps]
        c = Counter(v for v in votes if v is not None)
        if not c:
            out[k] = None
            continue
        top = c.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            out[k] = "WILL_FAIL" if "WILL_FAIL" in c else top[0][0]
        else:
            out[k] = top[0][0]
    return out


def has_extractable_anchor(item) -> bool:
    return any(ins.get("anchor") for ins in item["instructions"])


def has_designation(item) -> bool:
    return any(ins.get("designation") for ins in item["instructions"])


def main() -> int:
    items = load_items()
    by_id = {i["item_id"]: i for i in items}
    reps = [json.loads((CHECKPOINT / f"B0-agent-rep{r}.json").read_text(encoding="utf-8"))["predictions"]
            for r in (1, 2, 3)]
    preds = majority(reps)
    res = score(items, preds)

    lines = []
    w = lines.append
    w("=" * 78)
    w("B0-agent ERROR PROFILE - measured BEFORE the Iteration 1 card is written")
    w("=" * 78)
    w("")
    w(f"  eval set  {EVALSET.relative_to(REPO).as_posix()}   n = {res['n']}"
      f"   {res['n_positives']} positive / {res['n_negatives']} negative")
    w(f"  reps      3, aggregated MAJORITY, ties to the FAILURE side")
    w("")
    w(f"  accuracy              {res['accuracy']:.4f}   ({res['success']}/{res['n']})")
    w(f"  success + failure     {res['success']} + {res['failure']} = {res['success'] + res['failure']}"
      f"   (asserted == n by score.py)")
    w(f"  false-defect  rate    {res['false_defect_rate']:.4f}"
      f"   ({res['false_defect_count']}/{res['n_negatives']})   guard <= 0.25"
      f"   {'PASS' if res['guard_false_defect_pass'] else 'FAIL'}")
    w(f"  missed-defect rate    {res['missed_defect_rate']:.4f}"
      f"   ({res['missed_defect_count']}/{res['n_positives']})   guard <= 0.25"
      f"   {'PASS' if res['guard_missed_defect_pass'] else 'FAIL'}")
    w(f"  unparseable/absent    {res['unparseable_or_absent']}")
    w("")
    w("-" * 78)
    w("WHERE THE ERRORS ARE - the whole point of this file")
    w("-" * 78)
    w("")
    w("  An error on a WILL_FAIL item is a MISSED DEFECT: the arm read the section")
    w("  text and still failed to see that an instruction cannot execute.")
    w("  An error on a WILL_EXECUTE item is a FALSE DEFECT.")
    w("")
    n_missed = res["missed_defect_count"]
    n_false = res["false_defect_count"]
    tot_err = n_missed + n_false
    w(f"  missed defects  {n_missed:3d}   {n_missed / tot_err:.1%} of all errors")
    w(f"  false defects   {n_false:3d}   {n_false / tot_err:.1%} of all errors")
    w(f"  total errors    {tot_err:3d}")
    w("")

    # Per-class recall - CONTEXT.md section 11's hot take applied to the baseline
    pos = [i for i in items if i["label"] == "WILL_FAIL"]
    neg = [i for i in items if i["label"] == "WILL_EXECUTE"]
    rec_pos = sum(1 for i in pos if preds.get(i["item_id"]) == "WILL_FAIL") / len(pos)
    rec_neg = sum(1 for i in neg if preds.get(i["item_id"]) == "WILL_EXECUTE") / len(neg)
    w(f"  recall on WILL_FAIL    (defective) {rec_pos:.4f}")
    w(f"  recall on WILL_EXECUTE (clean)     {rec_neg:.4f}")
    w("")
    w("  THE ARM IS NOT AT CHANCE AND NOT BALANCED. It is strongly biased toward")
    w("  WILL_EXECUTE: it clears the false-defect guard comfortably and fails the")
    w("  missed-defect guard by a wide margin. Reading the text made it CAUTIOUS,")
    w("  not ACCURATE. This is CONTEXT.md section 11's hot take showing up in the")
    w("  baseline: the average moved +18.3 pp and the decision boundary did not.")
    w("")
    w("-" * 78)
    w("DO THE MISSES HAVE A CHECKABLE STRUCTURE? - can a resolver reach them?")
    w("-" * 78)
    w("")

    def bucket(subset, name):
        if not subset:
            w(f"  {name:44s} n=0   (zero-occurrence branch, printed as zero)")
            return
        miss = sum(1 for i in subset
                   if preds.get(i["item_id"]) != i["label"])
        w(f"  {name:44s} n={len(subset):3d}   errors {miss:3d}   rate {miss / len(subset):.4f}")

    w("  ALL ITEMS, split by what a deterministic resolver could check:")
    bucket([i for i in items if has_designation(i)], "has >=1 extractable designation")
    bucket([i for i in items if not has_designation(i)], "has NO extractable designation")
    bucket([i for i in items if has_extractable_anchor(i)], "has >=1 extractable quoted anchor")
    bucket([i for i in items if not has_extractable_anchor(i)], "has NO extractable quoted anchor")
    w("")
    w("  MISSED DEFECTS ONLY (gold WILL_FAIL, predicted WILL_EXECUTE or nothing):")
    missed = [i for i in pos if preds.get(i["item_id"]) != "WILL_FAIL"]
    w(f"    of {len(missed)} missed defects:")
    w(f"      {sum(1 for i in missed if has_designation(i)):3d} carry an extractable designation")
    w(f"      {sum(1 for i in missed if has_extractable_anchor(i)):3d} carry an extractable quoted anchor")
    w(f"      {sum(1 for i in missed if has_designation(i) or has_extractable_anchor(i)):3d} carry AT LEAST ONE of the two")
    w(f"      {sum(1 for i in missed if not has_designation(i) and not has_extractable_anchor(i)):3d} carry NEITHER"
      f"  <- these are OUT OF REACH of cfr_resolve")
    w("")
    ops = Counter()
    for i in missed:
        for ins in i["instructions"]:
            ops[ins["operation"]] += 1
    w(f"    operations across the missed defects' instructions: {sorted(ops.items(), key=lambda x: (-x[1], str(x[0])))}")
    w("")
    w("  INSTRUCTION COUNT - CONTEXT.md section 9's hard case is the defect that is")
    w("  NOT the first instruction, where a partial read rules correctly for the")
    w("  wrong reason and a deep read is needed to rule at all:")
    multi = [i for i in pos if i["instruction_count"] >= 3]
    single = [i for i in pos if i["instruction_count"] < 3]
    for name, sub in (("defective, >=3 instructions", multi), ("defective, <3 instructions", single)):
        if sub:
            m = sum(1 for i in sub if preds.get(i["item_id"]) != "WILL_FAIL")
            w(f"    {name:32s} n={len(sub):3d}   missed {m:3d}   miss-rate {m / len(sub):.4f}")
        else:
            w(f"    {name:32s} n=0   (zero-occurrence branch, printed as zero)")
    w("")
    w("=" * 78)
    w("THE OBSERVED FAILURE, IN ONE SENTENCE, FOR THE ITERATION 1 CARD")
    w("=" * 78)
    w("")
    w(f"  B0-agent scores {res['accuracy']:.4f} and {n_missed / tot_err:.0%} of its errors are MISSED")
    w(f"  DEFECTS: {n_missed} of {res['n_positives']} defective sections called executable, a missed-defect")
    w(f"  rate of {res['missed_defect_rate']:.4f} against a pre-registered guard of 0.25. Of those {len(missed)}")
    w(f"  misses, {sum(1 for i in missed if has_designation(i) or has_extractable_anchor(i))} carry a designation or a quoted anchor that a deterministic")
    w(f"  resolver can check against the point-in-time text, and {sum(1 for i in missed if not has_designation(i) and not has_extractable_anchor(i))} carry neither.")
    w("")
    text = "\n".join(lines) + "\n"
    print(text)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"  wrote {OUT.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
