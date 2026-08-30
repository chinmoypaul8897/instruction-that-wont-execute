"""CH-03 RE-REVIEW round 2 - does the F1 FIX introduce a NEW exploitable pattern?

The replacement rule balances a running counter. A balanced counter is not the same
thing as an unbiased selection: a counter that is driven to zero by ALTERNATING
produces a perfectly predictable sequence. This probe asks three questions.

  1. What is the realised sequence of `negative sorts before positive` in build order,
     and is it alternating?
  2. Can an attacker who can only ORDER the pairs (not label them) exploit that
     sequence - i.e. does an alternating guess beat chance?
  3. Does the choice correlate with document size, block size, or the position of the
     document in processing order?

This file imports `build_pairs` from src ONLY to recover the ground-truth pairing and
the build order. Every attack below is scored on labels the attacker does not have,
and every attacker-side feature is recomputed from items.jsonl alone.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from eval_set import build_pairs, instruction_counts, load_jsonl   # noqa: E402
from cfr_pit import section_sort_key                               # noqa: E402


def binom_two_sided(k, n, p=0.5):
    """Exact two-sided binomial p-value, stdlib only."""
    probs = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = probs[k]
    return sum(x for x in probs if x <= obs * (1 + 1e-12))


def main():
    records = load_jsonl(REPO / "data/attribution-v11/amdpars_v11.jsonl")
    citations = json.loads((REPO / "data/amdpars/citations.json").read_text("utf-8"))
    counts = instruction_counts(records, "v11")
    all_defects = sorted({(c["frdoc"], c["section"]) for c in citations.values()
                          if c.get("status") == "resolved"})
    pairs, unmatched = build_pairs(counts, all_defects, tolerance=0)
    print("build_pairs on the unrestricted pool: %d pairs, %d unmatched, total %d"
          % (len(pairs), len(unmatched), len(all_defects)))

    frozen = [json.loads(l) for l in
              (REPO / "data/evalset/items.jsonl").read_text("utf-8").splitlines() if l.strip()]
    frozen_ids = {(i["frdoc"], i["section"]) for i in frozen}
    kept = [p for p in pairs
            if (p["frdoc"], p["positive"]) in frozen_ids
            and (p["frdoc"], p["negative"]) in frozen_ids]
    print("of those, %d pairs survive to the freeze (expected 41)\n" % len(kept))

    # ---- 1. the realised sequence, in BUILD order -------------------------------
    seq = [1 if p["negative_sorts_before_positive"] else 0 for p in pairs]
    forced = [p["side_forced"] for p in pairs]
    print("BUILD ORDER over all %d matched pairs (1 = negative sorts BEFORE):" % len(seq))
    print("  " + "".join(str(x) for x in seq))
    print("  forced (one-sided, structural):")
    print("  " + "".join("F" if f else "." for f in forced))
    b = sum(seq)
    print("  before %d / after %d   exact two-sided binomial p = %.4f"
          % (b, len(seq) - b, binom_two_sided(b, len(seq))))

    seqk = [1 if p["negative_sorts_before_positive"] else 0 for p in kept]
    fk = [p["side_forced"] for p in kept]
    bk = sum(seqk)
    print("\nFROZEN 41 PAIRS (1 = negative sorts BEFORE):")
    print("  " + "".join(str(x) for x in seqk))
    print("  " + "".join("F" if f else "." for f in fk))
    print("  before %d / after %d   exact two-sided binomial p = %.4f"
          % (bk, len(seqk) - bk, binom_two_sided(bk, len(seqk))))
    free_only = [s for s, f in zip(seqk, fk) if not f]
    bf = sum(free_only)
    print("  FREE (both sides available) subset: %d pairs, before %d, p = %.4f"
          % (len(free_only), bf, binom_two_sided(bf, len(free_only)) if free_only else 1.0))
    forced_only = [s for s, f in zip(seqk, fk) if f]
    bfo = sum(forced_only)
    print("  FORCED subset: %d pairs, before %d, p = %.4f"
          % (len(forced_only), bfo,
             binom_two_sided(bfo, len(forced_only)) if forced_only else 1.0))

    # ---- 2. is the FREE subsequence alternating, and is that exploitable? --------
    runs = 0
    for a, c in zip(free_only, free_only[1:]):
        runs += (a != c)
    print("\n  alternations inside the FREE subsequence: %d of %d adjacent gaps"
          % (runs, max(0, len(free_only) - 1)))

    # An attacker cannot see `side_forced`, and cannot see which member is the
    # positive. The strongest reconstruction available from items.jsonl alone is to
    # order the pairs the way the builder does - by (frdoc, then section) - and then
    # guess the alternating pattern. Both phases are tried; the better is reported.
    blocks = defaultdict(list)
    for i in frozen:
        blocks[(i["frdoc"], i["instruction_count"])].append(i)
    recovered = []
    for k in sorted(blocks):
        grp = sorted(blocks[k], key=lambda i: section_sort_key(i["section"]))
        for j in range(0, len(grp), 2):
            if j + 1 < len(grp):
                recovered.append((grp[j], grp[j + 1]))
    print("  attacker-recovered adjacent pairs: %d (true pairs 41)" % len(recovered))
    best = 0.0
    for phase in (0, 1):
        right = 0
        for idx, (lo, hi) in enumerate(recovered):
            # guess: on even index the LOWER-sorting member is the negative
            neg = lo if (idx + phase) % 2 == 0 else hi
            pos = hi if neg is lo else lo
            right += (neg["label"] == "WILL_EXECUTE") + (pos["label"] == "WILL_FAIL")
        best = max(best, right / len(frozen))
    print("  ALTERNATING-PHASE ATTACK best accuracy: %.4f" % best)

    # ---- 3. correlation of the choice with document / block properties ----------
    per_item = {(i["frdoc"], i["section"]): i for i in frozen}
    print("\n  choice vs document and block properties (frozen pairs):")
    for name, fn in (
        ("doc amdpar count", lambda p: per_item[(p["frdoc"], p["positive"])]["document_amdpar_count"]),
        ("doc completeness", lambda p: per_item[(p["frdoc"], p["positive"])]["document_completeness_v11"]),
        ("free candidates", lambda p: p["free_candidates"]),
        ("count-matched cands", lambda p: p["count_matched_candidates"]),
        ("instruction count", lambda p: p["instruction_count"]),
    ):
        xs = [fn(p) for p in kept]
        ys = [1.0 if p["negative_sorts_before_positive"] else 0.0 for p in kept]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
        r = num / den if den else 0.0
        print("    pearson r(%-20s, negative-sorts-before) = %+.4f" % (name, r))

    # ---- 4. does the OLD rule still beat the set?  the counterfactual ------------
    old_pairs = []
    used = {}
    defect_by_doc = defaultdict(set)
    for f, s in all_defects:
        defect_by_doc[f].add(s)
    for frdoc, section in sorted(all_defects):
        doc = counts.get(frdoc, {})
        own = doc.get(section)
        if own is None:
            continue
        taken = used.setdefault(frdoc, set())
        free = sorted(s for s, c in doc.items()
                      if s != section and s not in defect_by_doc[frdoc]
                      and s not in taken and c == own)
        if not free:
            continue
        neg = free[0]
        taken.add(neg)
        old_pairs.append((frdoc, section, neg))
    ob = sum(1 for f, p, n in old_pairs if section_sort_key(n) < section_sort_key(p))
    print("\n  COUNTERFACTUAL - the OLD `free[0]` rule on the same pool: "
          "%d/%d negatives sort before, p = %.6f"
          % (ob, len(old_pairs), binom_two_sided(ob, len(old_pairs))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
