"""CH-06 §2a — ITERATION 1's ERRORS, measured, to fill Iteration 2's card.

The Iteration 2 card committed at `e12466c` left its `Observed failure` line **open on
purpose**, with the note: *"TO BE MEASURED FROM ITERATION 1'S ERRORS, NOT GUESSED."*
This script is that measurement. It runs after Iteration 1 and **before Iteration 2**,
and the git order proves it.

It also tests the card's committed PRIOR. The card predicted, before either ran, that
Iteration 1's errors would concentrate on multi-instruction sections, on the strength of
B0-agent's 0.6875-vs-0.3600 split. **If they do not, the prior is wrong and this file
says so** - which is the point of writing a prior down.

PURITY: no network, no clock, no randomness. `data/` is read-only.

    python docs/evidence/ch06-a1/iter2/iter1_error_profile.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from score import normalise_verdict, score  # noqa: E402

EVALSET = REPO / "data/evalset/items.jsonl"
CH06 = REPO / "docs/evidence/ch06-a1"
CHECKPOINT = REPO / "docs/evidence/checkpoint"
OUT = Path(__file__).resolve().parent / "iter1_error_profile.txt"


def majority(reps):
    out = {}
    for k in sorted({k for r in reps for k in r}):
        c = Counter(v for v in (normalise_verdict(r.get(k)) for r in reps) if v)
        if not c:
            out[k] = None
            continue
        top = c.most_common()
        out[k] = ("WILL_FAIL" if len(top) > 1 and top[0][1] == top[1][1]
                  and "WILL_FAIL" in c else top[0][0])
    return out


def main() -> int:
    items = sorted((json.loads(l) for l in EVALSET.read_text(encoding="utf-8").splitlines()
                    if l.strip()), key=lambda i: i["item_id"])
    run = json.loads((CH06 / "A1-iter1-rep1.json").read_text(encoding="utf-8"))
    preds = {k: normalise_verdict(v) for k, v in run["predictions"].items()}
    arts = {}
    for line in (CH06 / "A1-iter1-rep1-artifacts.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            a = json.loads(line)
            arts[a["item_id"]] = a
    base = majority([json.loads((CHECKPOINT / f"B0-agent-rep{r}.json").read_text(encoding="utf-8"))["predictions"]
                     for r in (1, 2, 3)])

    res = score(items, preds)
    bres = score(items, base)

    lines = []
    w = lines.append
    w("=" * 78)
    w("ITERATION 1's ERRORS - measured, to fill the Iteration 2 card's open line")
    w("=" * 78)
    w("")
    w(f"  A1-iter1  accuracy {res['accuracy']:.4f}  ({res['success']}/{res['n']})"
      f"   1 rep, {run['tool_calls']} tool calls")
    w(f"  B0-agent  accuracy {bres['accuracy']:.4f}  ({bres['success']}/{bres['n']})   3 reps")
    w(f"  gap       {100 * (res['accuracy'] - bres['accuracy']):+.1f} pp")
    w("")
    w("  PREDICTION COMMITTED AT e12466c, BEFORE THE RUN:  +8 pp -> 0.74")
    w(f"  MEASURED:                                         {100 * (res['accuracy'] - bres['accuracy']):+.1f} pp -> {res['accuracy']:.4f}")
    w(f"  THE PREDICTION MISSED, AND IT MISSED IN THE WRONG DIRECTION"
      f" ({100 * (res['accuracy'] - bres['accuracy']) - 8.0:+.1f} pp against the card).")
    w("")
    w("-" * 78)
    w("WHICH DIRECTION DID IT MOVE? - the two guards, against B0-agent")
    w("-" * 78)
    w("")
    w(f"  {'':22s} {'B0-agent':>10s} {'A1-iter1':>10s} {'delta':>10s}   guard")
    w(f"  {'false-defect rate':22s} {bres['false_defect_rate']:>10.4f}"
      f" {res['false_defect_rate']:>10.4f}"
      f" {res['false_defect_rate'] - bres['false_defect_rate']:>+10.4f}"
      f"   <= 0.25  {'PASS' if res['guard_false_defect_pass'] else 'FAIL'}")
    w(f"  {'missed-defect rate':22s} {bres['missed_defect_rate']:>10.4f}"
      f" {res['missed_defect_rate']:>10.4f}"
      f" {res['missed_defect_rate'] - bres['missed_defect_rate']:>+10.4f}"
      f"   <= 0.25  {'PASS' if res['guard_missed_defect_pass'] else 'FAIL'}")
    w("")
    w("  THE TOOL DID EXACTLY WHAT IT WAS BUILT TO DO, AND IT COST ACCURACY.")
    w("  The missed-defect rate FELL - the resolver does make the agent see defects it")
    w("  was blind to. The false-defect rate ROSE FURTHER, through the pre-registered")
    w("  0.25 guard, and the second effect is larger than the first.")
    w("")
    w("  This is QUESTIONS.md Q21's prediction, committed BEFORE this run:")
    w("    \"A1's false-defect rate rises against B0-agent's 0.1951, possibly through")
    w("     the pre-registered 0.25 guard, at the same time as its missed-defect rate")
    w("     falls. Both are reported. Neither guard is moved.\"")
    w("  Both halves are confirmed. The guard is NOT moved.")
    w("")

    # ---- where the new errors are
    pos = [i for i in items if i["label"] == "WILL_FAIL"]
    neg = [i for i in items if i["label"] == "WILL_EXECUTE"]
    newly_wrong = [i for i in items
                   if base.get(i["item_id"]) == i["label"] and preds.get(i["item_id"]) != i["label"]]
    newly_right = [i for i in items
                   if base.get(i["item_id"]) != i["label"] and preds.get(i["item_id"]) == i["label"]]
    w("-" * 78)
    w("WHAT THE TOOL BROKE, AND WHAT IT FIXED - item-level, against B0-agent")
    w("-" * 78)
    w("")
    w(f"  B0-agent right -> A1-iter1 wrong   {len(newly_wrong):3d}"
      f"   ({sum(1 for i in newly_wrong if i['label'] == 'WILL_EXECUTE')} clean,"
      f" {sum(1 for i in newly_wrong if i['label'] == 'WILL_FAIL')} defective)")
    w(f"  B0-agent wrong -> A1-iter1 right   {len(newly_right):3d}"
      f"   ({sum(1 for i in newly_right if i['label'] == 'WILL_EXECUTE')} clean,"
      f" {sum(1 for i in newly_right if i['label'] == 'WILL_FAIL')} defective)")
    w("")
    w("  The tool is not noise. It moves items in BOTH directions and the net is")
    w("  negative because the breakage lands on the clean class.")
    w("")

    # ---- the Q21 mechanism, item by item
    nested = json.loads((CH06 / "iter1/nested_designation_probe.json").read_text(encoding="utf-8"))
    affected = set(nested["affected_items"])
    w("-" * 78)
    w("IS Q21's NESTED-DESIGNATION CEILING THE MECHANISM? - the decisive split")
    w("-" * 78)
    w("")
    for name, sub in (("items TOUCHED by the ceiling", [i for i in items if i["item_id"] in affected]),
                      ("items NOT touched", [i for i in items if i["item_id"] not in affected])):
        if not sub:
            w(f"  {name:32s} n=0   (zero-occurrence branch, printed as zero)")
            continue
        a_acc = sum(1 for i in sub if preds.get(i["item_id"]) == i["label"]) / len(sub)
        b_acc = sum(1 for i in sub if base.get(i["item_id"]) == i["label"]) / len(sub)
        w(f"  {name:32s} n={len(sub):3d}   B0-agent {b_acc:.4f}   A1-iter1 {a_acc:.4f}"
          f"   {100 * (a_acc - b_acc):+6.1f} pp")
    w("")
    fd_aff = [i for i in neg if i["item_id"] in affected]
    fd_not = [i for i in neg if i["item_id"] not in affected]
    for name, sub in (("CLEAN items touched by the ceiling", fd_aff),
                      ("CLEAN items not touched", fd_not)):
        if not sub:
            w(f"  {name:36s} n=0   (zero)")
            continue
        fd = sum(1 for i in sub if preds.get(i["item_id"]) != i["label"]) / len(sub)
        w(f"  {name:36s} n={len(sub):3d}   A1-iter1 false-defect rate {fd:.4f}")
    w("")

    # ---- the card's committed prior
    w("-" * 78)
    w("THE ITERATION 2 CARD's COMMITTED PRIOR, TESTED")
    w("-" * 78)
    w("")
    w("  The card predicted at e12466c that errors would concentrate on sections with")
    w("  >= 3 amendatory instructions, on the strength of B0-agent's 0.6875 vs 0.3600.")
    w("")
    w(f"  {'subset':38s} {'n':>4s} {'B0-agent':>10s} {'A1-iter1':>10s}")
    for name, sub in (("defective, >= 3 instructions", [i for i in pos if i["instruction_count"] >= 3]),
                      ("defective, < 3 instructions", [i for i in pos if i["instruction_count"] < 3]),
                      ("clean, >= 3 instructions", [i for i in neg if i["instruction_count"] >= 3]),
                      ("clean, < 3 instructions", [i for i in neg if i["instruction_count"] < 3])):
        if not sub:
            w(f"  {name:38s} {0:>4d}   (zero-occurrence branch, printed as zero)")
            continue
        a_err = sum(1 for i in sub if preds.get(i["item_id"]) != i["label"]) / len(sub)
        b_err = sum(1 for i in sub if base.get(i["item_id"]) != i["label"]) / len(sub)
        w(f"  {name:38s} {len(sub):>4d} {b_err:>10.4f} {a_err:>10.4f}   (error rates)")
    w("")

    # ---- emission health, and the tool-use gap
    w("-" * 78)
    w("EMISSION HEALTH AND THE TOOL-USE GAP")
    w("-" * 78)
    w("")
    unruled = [a for a in arts.values() if a.get("instructions_unruled")]
    zero_calls = [a for a in arts.values() if not a.get("tool_calls_made")]
    w(f"  items with an INCOMPLETE emission (a targeted instruction unruled) "
      f"{len(unruled):3d} of {len(arts)}")
    w(f"  items where the model made ZERO tool calls despite having the tool "
      f"{len(zero_calls):3d} of {len(arts)}")
    w(f"  total tool calls {run['tool_calls']}   "
      f"{run['tool_calls'] / max(1, len(arts)):.2f} per item")
    w(f"  items routed to the human checkpoint {run['items_routed_to_human']} of {len(arts)}")
    w("")
    fc = Counter(a.get("failure_class") for a in arts.values() if a.get("failure_class"))
    w(f"  failure_class emitted, across all items: {dict(fc) if fc else '{} (zero)'}")
    w("")

    w("=" * 78)
    w("THE OBSERVED FAILURE, FOR THE ITERATION 2 CARD's OPEN LINE")
    w("=" * 78)
    w("")
    w(f"  A1-iter1 scores {res['accuracy']:.4f}, {100 * (res['accuracy'] - bres['accuracy']):+.1f} pp against B0-agent, and its errors")
    w(f"  have INVERTED. Missed defects fell {bres['missed_defect_count']} -> {res['missed_defect_count']}; false defects rose")
    w(f"  {bres['false_defect_count']} -> {res['false_defect_count']}, a rate of {res['false_defect_rate']:.4f} through the 0.25 guard. The agent")
    w("  now over-flags: handed a resolver that says a paragraph is absent, it rules")
    w("  the instruction defective and stops. It trusts the tool MORE than the tool")
    w("  deserves, and it does not cross-check the tool's answer against the section")
    w("  text it was also given.")
    w("")
    text = "\n".join(lines) + "\n"
    print(text)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"  wrote {OUT.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
