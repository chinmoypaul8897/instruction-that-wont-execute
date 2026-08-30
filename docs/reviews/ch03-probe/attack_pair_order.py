"""ADVERSARIAL REVIEW of CH-03 - the trivial script that beats the eval set.

The negative is chosen as "the FIRST in sorted order among free count-matched
siblings" (pre-registration section 3, src/eval_set.py:122-138). The positive is a
GIVEN section. Sorted-first selection therefore puts the negative BEFORE the positive
in section order far more often than chance, and the pairing is recoverable from
items.jsonl alone because both members share (frdoc, instruction_count).

This file implements the attack. No model, no CFR text, no network - 12 lines.
"""
import json
import math
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def binom_two_sided(k, n, p=0.5):
    def pmf(i):
        return math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    obs = pmf(k)
    return sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-12)


def attack(path, label=""):
    items = [json.loads(l) for l in
             Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    groups = defaultdict(list)
    for i in items:
        groups[(i["frdoc"], i["instruction_count"])].append(i)

    # ---- THE ATTACK, in full -----------------------------------------------------
    pred = {}
    for g in groups.values():
        if len(g) != 2:
            for i in g:
                pred[id(i)] = "WILL_FAIL"          # degenerate group, guess one way
            continue
        a, b = sorted(g, key=lambda i: i["section"])
        pred[id(a)] = "WILL_EXECUTE"               # sorts first -> the negative
        pred[id(b)] = "WILL_FAIL"
    # ------------------------------------------------------------------------------

    right = sum(1 for i in items if pred[id(i)] == i["label"])
    n = len(items)
    pairs = sum(1 for g in groups.values() if len(g) == 2)
    degenerate = len(groups) - pairs
    print(f"  {label}")
    print(f"    items                                   : {n}")
    print(f"    groups recovered from (frdoc, count)    : {len(groups)}"
          f"  ({pairs} clean pairs, {degenerate} not size-2)")
    print(f"    ACCURACY of the sort-order script       : {right}/{n} = {right / n:.4f}")
    kp = right // 2
    print(f"    pairs it orders correctly               : {kp}/{pairs}"
          f" = {kp / pairs:.4f}   two-sided binomial p = {binom_two_sided(kp, pairs):.5f}")
    return right / n


print("=" * 100)
print("THE SORT-ORDER SCRIPT - no model, no CFR text, no instruction text")
print("=" * 100)
a = attack(REPO / "data/evalset/items.jsonl", "data/evalset/items.jsonl (the PRIMARY eval set)")

print()
print("=" * 100)
print("WHY IT WORKS - the negative-selection rule is 'sorted order, first element'")
print("=" * 100)
items = [json.loads(l) for l in
         (REPO / "data/evalset/items.jsonl").read_text(encoding="utf-8").splitlines()
         if l.strip()]
g = defaultdict(list)
for i in items:
    g[(i["frdoc"], i["instruction_count"])].append(i)
neg_first = 0
for grp in g.values():
    if len(grp) != 2:
        continue
    p = [x for x in grp if x["label"] == "WILL_FAIL"][0]
    nn = [x for x in grp if x["label"] == "WILL_EXECUTE"][0]
    if nn["section"] < p["section"]:
        neg_first += 1
tot = sum(1 for grp in g.values() if len(grp) == 2)
print(f"  pairs whose NEGATIVE sorts before its POSITIVE : {neg_first}/{tot}"
      f" = {neg_first / tot:.4f}   (chance 0.50)")
print(f"  two-sided binomial p                           : "
      f"{binom_two_sided(neg_first, tot):.6f}")

print()
print("  For comparison, CONTEXT.md section 7's own measured trivial-attack surface:")
print("    'n_instructions pinned at 0.5000; best of 26 features 0.5934 inside its")
print("     own null at p = 0.185'")
print(f"  and GOOD.md's success bar: A1 >= 0.80 absolute, B0-agent ~0.75.")
