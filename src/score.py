"""CH-04 · 3a — the deterministic scorer. Stdlib only. No model. No network.

`CONTEXT.md` §7's primary metric, verbatim:

    Fraction of exact-instruction-count-matched (rule, section) items where the
    emitted `verdict` equals whether NARA published a live editorial note for that
    section.

**Do not change this metric.** §7: *"It is pre-registered, piloted, and the only metric
in the packet whose trivial-attack surface has been measured. Every rival that changed
its primary died to the first script someone wrote."*

Guards, also §7, also pre-registered: false-defect rate ≤ 0.25, missed-defect rate
≤ 0.25. And `success + failure == n` is **asserted**, not assumed.

WHAT COUNTS AS A FAILURE
------------------------
An unparseable verdict, an absent verdict, or an arm that errored counts as a
**failure**, never as a skip. Dropping it would let an arm raise its accuracy by
declining to answer, and `success + failure == n` is exactly the assertion that stops
that. Every item in the eval set appears in the denominator of every arm.

PURITY - hard rule 8. Everything here is data-in/results-out: no network, no clock,
no randomness. The permutation null lives in `bscript.py`, uses a declared seed, and
says so.
DETERMINISM - hard rule 9. Same inputs -> byte-identical outputs.

Goldens: `docs/evidence/ch04-scorer/goldens.md` S-A, S-B, committed before this file.
"""
from __future__ import annotations

from math import comb

WILL_FAIL = "WILL_FAIL"
WILL_EXECUTE = "WILL_EXECUTE"
VERDICTS = (WILL_FAIL, WILL_EXECUTE)

# CONTEXT.md section 7, pre-registered. Never moved after a result (hard rule 5).
GUARD_FALSE_DEFECT_MAX = 0.25
GUARD_MISSED_DEFECT_MAX = 0.25


class ScoreError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips. A load-bearing count that
    stops checking itself under an optimisation flag is exactly the silent green this
    project exists to expose."""


def normalise_verdict(raw) -> str | None:
    """An arm's raw output -> a verdict, or None if it is not one.

    Deliberately strict. `WILL_FAIL` and `WILL_EXECUTE` are the only two values
    `CONTEXT.md` §5's output contract admits. Anything else - prose, a refusal, an
    empty string, a JSON blob without the field - returns None and is scored as a
    FAILURE by `score`, which is what keeps a non-answer from being free.
    """
    if raw is None:
        return None
    text = str(raw).strip().strip('"').strip("'").upper()
    if text in (WILL_FAIL, WILL_EXECUTE):
        return text
    return None


def score(items, predictions) -> dict:
    """`CONTEXT.md` §7's primary metric and its guards. Pure.

    `items`        [{"item_id", "label"}], label in {WILL_FAIL, WILL_EXECUTE}
    `predictions`  {item_id -> raw verdict or None}

    Every item is scored. An item with no prediction is a failure, not a skip.
    """
    n = len(items)
    if n == 0:
        raise ScoreError("cannot score an empty eval set")
    seen = set()
    correct = wrong = 0
    false_defect = missed_defect = 0
    n_pos = n_neg = 0
    unparseable = 0
    per_item = []
    for it in items:
        iid, gold = it["item_id"], it["label"]
        if gold not in VERDICTS:
            raise ScoreError(f"{iid}: gold label {gold!r} is not a verdict")
        if iid in seen:
            raise ScoreError(f"duplicate item_id {iid!r} in the eval set")
        seen.add(iid)
        if gold == WILL_FAIL:
            n_pos += 1
        else:
            n_neg += 1
        pred = normalise_verdict(predictions.get(iid))
        if pred is None:
            unparseable += 1
        ok = pred == gold
        if ok:
            correct += 1
        else:
            wrong += 1
            # A non-answer is charged to the class it FAILED to get right, so an arm
            # cannot dodge the false-defect guard by emitting nothing.
            if gold == WILL_EXECUTE:
                false_defect += 1
            else:
                missed_defect += 1
        per_item.append({"item_id": iid, "gold": gold, "predicted": pred,
                         "raw": predictions.get(iid), "correct": ok})

    if correct + wrong != n:
        raise ScoreError(f"success {correct} + failure {wrong} != n {n}")
    if n_pos + n_neg != n:
        raise ScoreError(f"positives {n_pos} + negatives {n_neg} != n {n}")

    fd = (false_defect / n_neg) if n_neg else 0.0
    md = (missed_defect / n_pos) if n_pos else 0.0
    return {
        "n": n,
        "n_positives": n_pos,
        "n_negatives": n_neg,
        "success": correct,
        "failure": wrong,
        "accuracy": correct / n,
        "false_defect_count": false_defect,
        "false_defect_rate": fd,
        "missed_defect_count": missed_defect,
        "missed_defect_rate": md,
        "unparseable_or_absent": unparseable,
        "guard_false_defect_pass": fd <= GUARD_FALSE_DEFECT_MAX,
        "guard_missed_defect_pass": md <= GUARD_MISSED_DEFECT_MAX,
        "guard_false_defect_max": GUARD_FALSE_DEFECT_MAX,
        "guard_missed_defect_max": GUARD_MISSED_DEFECT_MAX,
        "per_item": per_item,
    }


def binom_tail_le(k: int, n: int) -> float:
    """P(X <= k) for X ~ Binomial(n, 1/2). Exact, in integer arithmetic until the
    final division, so there is no floating-point drift in the tail."""
    if n == 0:
        return 1.0
    k = max(0, min(k, n))
    return sum(comb(n, i) for i in range(k + 1)) / (2 ** n)


def mcnemar(a_correct, b_correct) -> dict:
    """Exact two-sided McNemar over paired correctness vectors. Pure. Goldens S-B.

    The EXACT binomial, not the chi-square approximation: the checkpoint's branch
    turns on this p-value and the approximation is unreliable at small discordant
    counts, which is exactly the regime a 50-pair eval set lives in.

    `b` = A right and B wrong; `c` = A wrong and B right. Concordant pairs carry no
    information about a difference and are excluded, which is what makes it McNemar
    rather than a two-sample test.
    """
    a_correct, b_correct = list(a_correct), list(b_correct)
    if len(a_correct) != len(b_correct):
        raise ScoreError("McNemar needs two vectors of the same length")
    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)
    c = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)
    nd = b + c
    if nd == 0:
        # Every pair concordant. There is no evidence of a difference, and no
        # division either - the degenerate case a naive implementation crashes on.
        p = 1.0
    else:
        p = min(1.0, 2.0 * binom_tail_le(min(b, c), nd))
    return {"b_only_a_correct": b, "c_only_b_correct": c, "n_discordant": nd,
            "p_value": p, "test": "exact two-sided binomial (McNemar)"}


def paired_accuracy_vectors(items, predictions):
    """Correctness per item, in the eval set's own sorted order, so two arms' vectors
    are aligned by construction rather than by a lookup that could silently mis-pair."""
    out = []
    for it in sorted(items, key=lambda i: i["item_id"]):
        out.append(normalise_verdict(predictions.get(it["item_id"])) == it["label"])
    return out


def bootstrap_ci_clustered(items, predictions, clusters, reps: int = 2000,
                           seed: int = 20260831, alpha: float = 0.05) -> dict:
    """Percentile CI for accuracy, resampling CLUSTERS (FR documents), not items.

    `CONTEXT.md` §7 / `plan.md` CH-08: clustered by FR document. A positive and its
    count-matched negative come from the same document and are not independent, so an
    item-level bootstrap would report a CI that is too narrow.

    The seed is a parameter with a declared default and is echoed in the result, so
    the interval is byte-reproducible (hard rule 9).
    """
    import random

    by_cluster: dict[str, list] = {}
    for it in items:
        by_cluster.setdefault(clusters[it["item_id"]], []).append(it)
    keys = sorted(by_cluster)
    if not keys:
        raise ScoreError("no clusters to bootstrap")
    rng = random.Random(seed)
    accs = []
    for _ in range(reps):
        drawn = [by_cluster[keys[rng.randrange(len(keys))]] for _ in keys]
        flat = [it for group in drawn for it in group]
        correct = sum(1 for it in flat
                      if normalise_verdict(predictions.get(it["item_id"])) == it["label"])
        accs.append(correct / len(flat))
    accs.sort()
    lo = accs[int((alpha / 2) * reps)]
    hi = accs[min(reps - 1, int((1 - alpha / 2) * reps))]
    return {"reps": reps, "seed": seed, "alpha": alpha,
            "n_clusters": len(keys), "ci_low": lo, "ci_high": hi,
            "note": "percentile bootstrap over FR documents, not over items"}


def n_needed_for_power(b: int, c: int, n_items: int, alpha: float = 0.05) -> dict:
    """`plan.md`'s AMBER branch requires "the n this design would need for power".

    Holds the OBSERVED discordance shape fixed - the b:c ratio and the discordant
    RATE - and asks how large n would have to be before an exact two-sided McNemar
    cleared `alpha`. This is a projection from one measurement, not a power
    calculation from an assumed effect, and the difference is stated in the result
    rather than left for a reader to assume.
    """
    d = b + c
    if d == 0:
        return {"observed_b": b, "observed_c": c, "n_items": n_items,
                "discordant_rate": 0.0, "n_needed": None,
                "note": "no discordant pairs; nothing to project from"}
    rate = d / n_items
    frac_c = c / d
    for d_try in range(d, 20 * d + 1):
        c_try = round(d_try * frac_c)
        if min(1.0, 2.0 * binom_tail_le(min(c_try, d_try - c_try), d_try)) < alpha:
            return {
                "observed_b": b, "observed_c": c, "observed_discordant": d,
                "n_items": n_items, "discordant_rate": rate,
                "discordant_needed": d_try,
                "n_needed": int(round(d_try / rate)),
                "pairs_needed": int(round(d_try / rate / 2)),
                "alpha": alpha,
                "note": ("projection holding the OBSERVED b:c ratio and discordant "
                         "rate fixed. It is an extrapolation from one measurement, "
                         "not a power calculation from an assumed effect size."),
            }
    return {"observed_b": b, "observed_c": c, "n_items": n_items,
            "discordant_rate": rate, "n_needed": None,
            "note": "no n within 20x the observed discordance clears alpha"}


def detectable_effect(n_pairs: int, alpha: float = 0.05, power: float = 0.80) -> dict:
    """What gap this n can and cannot detect - `plan.md` CH-03's fallback requires this
    stated in `GOOD.md` and the README when pairs land in [30, 42).

    Exact and assumption-light: for McNemar the question is how many DISCORDANT pairs
    are needed before an exact binomial rejects at `alpha`. Reported as the smallest
    discordant count `nd` for which an all-one-way split is significant, and the
    implied gap in percentage points at this n.
    """
    n_items = 2 * n_pairs
    nd_min = None
    for nd in range(1, n_items + 1):
        if min(1.0, 2.0 * binom_tail_le(0, nd)) < alpha:
            nd_min = nd
            break
    return {
        "n_pairs": n_pairs,
        "n_items": n_items,
        "alpha": alpha,
        "target_power": power,
        "min_discordant_all_one_way": nd_min,
        "min_detectable_gap_pp": (100.0 * nd_min / n_items) if nd_min else None,
        "note": ("the smallest ALL-ONE-WAY discordant count that clears alpha; a "
                 "mixed split needs more. This is a floor on the detectable effect, "
                 "not a power calculation."),
    }
