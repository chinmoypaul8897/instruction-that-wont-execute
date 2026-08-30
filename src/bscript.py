"""CH-04 · 3b — the B-script arm: the best model-free attack, and its permutation null.

`CONTEXT.md` §4 calls this PDF baseline **type 3, a simple script**: *"best model-free
attack: threshold on any of ~26 cheap features, honest 5-fold CV, reported with its
permutation null."*

**This is the honest floor everything else is measured against**, and it is the arm
that killed a predecessor project — an unmatched eval set let a threshold on
`n_instructions` beat the agent. So it is built to WIN if it can. A baseline built to
lose is a rigged benchmark by another name.

THREE THINGS THAT MAKE THE NULL HONEST, all pre-registered in `goldens.md` S-C..S-G
before this file existed:

1. **The mirror rule is scored in the null as well as in the test.** A feature that
   separates in reverse is still a trivial attack. Score only `x >= t` and the null is
   weaker than the test, and the p-value comes out too small.
2. **The observed statistic is included in its own null.** A permutation test that
   excludes it can return p = 0, which is not a probability any finite permutation
   test can produce.
3. **The null respects the PAIRING.** Each positive has one count-matched negative
   from the same FR document, so the exchangeable unit is the pair. The primary null
   swaps labels **within a pair**; every draw stays balanced, and the question it asks
   is the right one: *can this feature tell a defect section from its own
   count-matched sibling?* A free permutation over all labels is reported beside it as
   a diagnostic, never instead of it.

**Folds are grouped by FR document** (S-F). Positive and negative come from the same
document; a split that separated them would leak the answer across the fold boundary.

DETERMINISM - hard rule 9. Fold assignment is round-robin over sorted documents and
uses no RNG at all. The permutation null uses `random.Random(PERMUTATION_SEED)`, the
seed is a module constant that is printed with the result, and where the exhaustive
count is smaller than the sample count the test runs **exhaustively** and says so.
"""
from __future__ import annotations

import itertools
import random
import re

PERMUTATION_SEED = 20260831            # declared; printed in every result
N_PERMUTATIONS = 2000
N_FOLDS = 5
EXHAUSTIVE_LIMIT = 4096                # run all 2^k draws when k is small enough

WILL_FAIL = "WILL_FAIL"


class BScriptError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips."""


# ============================================================ the 26 cheap features

_WORD = re.compile(r"\w+")


def features(item) -> dict:
    """~26 cheap, model-free features of one eval item. Pure.

    Everything here is computable from the frozen record with no model and no network.
    Nothing reads the label, and nothing reads the editorial note - `note_text` is
    present on positives ONLY and is deliberately not touched. A feature that read it
    would score 1.0 and measure nothing.
    """
    instrs = item.get("instructions") or []
    texts = [(i.get("text") or "") for i in instrs]
    ops = [i.get("operation") for i in instrs]
    anchors = [i.get("anchor") for i in instrs if i.get("anchor")]
    desigs = [i.get("designation") for i in instrs if i.get("designation")]
    body = item.get("section_text") or ""
    joined = " ".join(texts)

    def op_count(name):
        return sum(1 for o in ops if o == name)

    return {
        "instruction_count": float(item.get("instruction_count") or 0),
        "instr_chars_total": float(sum(len(t) for t in texts)),
        "instr_chars_mean": float(sum(len(t) for t in texts) / len(texts)) if texts else 0.0,
        "instr_chars_max": float(max((len(t) for t in texts), default=0)),
        "instr_words_total": float(len(_WORD.findall(joined))),
        "distinct_operations": float(len({o for o in ops if o})),
        "op_revise": float(op_count("revise")),
        "op_add": float(op_count("add")),
        "op_remove": float(op_count("remove")),
        "op_redesignate": float(op_count("redesignate")),
        "op_amend": float(op_count("amend")),
        "op_none": float(sum(1 for o in ops if not o)),
        "anchor_count": float(len(anchors)),
        "anchor_chars_total": float(sum(len(a) for a in anchors)),
        "designation_count": float(len(desigs)),
        "designation_chars_total": float(sum(len(d) for d in desigs)),
        "designation_max_depth": float(max((d.count("(") for d in desigs), default=0)),
        "instr_without_anchor": float(sum(1 for i in instrs if not i.get("anchor"))),
        "instr_without_designation": float(
            sum(1 for i in instrs if not i.get("designation"))),
        "mentions_table": float(sum(1 for t in texts if "table" in t.lower())),
        "mentions_paragraph": float(sum(1 for t in texts if "paragraph" in t.lower())),
        "section_text_chars": float(len(body)),
        "section_text_lines": float(body.count("\n") + 1 if body else 0),
        "cfr_title": float(item.get("cfr_title") or 0),
        "section_numeric": float(_section_numeric(item.get("section") or "")),
        "as_of_edition": float(item.get("as_of_edition") or 0),
        "publication_year": float((item.get("publication_date") or "0000")[:4]),
        "document_amdpar_count": float(item.get("document_amdpar_count") or 0),
        "document_completeness_v11": float(item.get("document_completeness_v11") or 0.0),
        "share_of_document": (
            float(item.get("instruction_count") or 0)
            / float(item.get("document_amdpar_count") or 1)),
    }


def _section_numeric(section: str) -> float:
    m = re.match(r"(\d+)\.(\d+)", section)
    return float(m.group(2)) if m else 0.0


FEATURE_NAMES = None                    # filled on first use by `feature_names`


def feature_names(items) -> list[str]:
    if not items:
        raise BScriptError("no items")
    return sorted(features(items[0]))


# ============================================================ the threshold classifier

def best_threshold(values, labels) -> dict:
    """Best single threshold on one feature, BOTH directions. Pure. Goldens S-C.

    Declared tie-break: the LOWEST threshold, and `>=` before `<=`, so the answer
    never depends on iteration order.
    """
    if len(values) != len(labels):
        raise BScriptError("values and labels must be the same length")
    n = len(values)
    if n == 0:
        raise BScriptError("cannot fit a threshold on no items")
    best = {"accuracy": -1.0, "threshold": None, "direction": None}
    for t in sorted(set(values)):
        for direction in (">=", "<="):
            correct = 0
            for v, lab in zip(values, labels):
                pred_pos = (v >= t) if direction == ">=" else (v <= t)
                if pred_pos == (lab == WILL_FAIL):
                    correct += 1
            acc = correct / n
            if acc > best["accuracy"]:
                best = {"accuracy": acc, "threshold": t, "direction": direction}
    return best


def apply_threshold(values, rule) -> list[bool]:
    t, d = rule["threshold"], rule["direction"]
    return [(v >= t) if d == ">=" else (v <= t) for v in values]


# ============================================================ grouped CV

def fold_assignment(groups) -> dict:
    """FR document -> fold. Round-robin over SORTED documents, no RNG. Goldens S-F."""
    return {g: i % N_FOLDS for i, g in enumerate(sorted(set(groups)))}


def cv_accuracy(rows) -> dict:
    """Honest 5-fold grouped CV over every feature; returns the best.

    `rows` = [{"features": {...}, "label": ..., "group": frdoc}]

    A threshold is fitted on the TRAINING folds only and applied to the held-out fold.
    The feature is selected by held-out accuracy, and that selection is itself inside
    the permutation null below - which is what stops "best of 26" being free.
    """
    if not rows:
        raise BScriptError("no rows")
    names = sorted(rows[0]["features"])
    assign = fold_assignment([r["group"] for r in rows])
    per_feature = {}
    for name in names:
        correct = total = 0
        for fold in range(N_FOLDS):
            train = [r for r in rows if assign[r["group"]] != fold]
            test = [r for r in rows if assign[r["group"]] == fold]
            if not train or not test:
                continue
            rule = best_threshold([r["features"][name] for r in train],
                                  [r["label"] for r in train])
            preds = apply_threshold([r["features"][name] for r in test], rule)
            for p, r in zip(preds, test):
                correct += int(p == (r["label"] == WILL_FAIL))
                total += 1
        per_feature[name] = (correct / total) if total else 0.0
    # deterministic argmax: highest accuracy, then the alphabetically first name
    best_name = sorted(per_feature, key=lambda k: (-per_feature[k], k))[0]
    return {"per_feature": per_feature,
            "best_feature": best_name,
            "best_accuracy": per_feature[best_name],
            "n_features": len(names),
            "folds": N_FOLDS}


# ============================================================ the permutation null

def _within_pair_draws(pairs, rng, n_requested):
    """Label assignments that swap within pairs. Exhaustive when 2^k is small enough
    (and the result says which was used), sampled otherwise."""
    k = len(pairs)
    if k <= 12 and 2 ** k <= EXHAUSTIVE_LIMIT and 2 ** k <= n_requested:
        return list(itertools.product((False, True), repeat=k)), "exhaustive"
    return [tuple(rng.random() < 0.5 for _ in range(k)) for _ in range(n_requested)], \
        "sampled"


def permutation_null(rows, pairs, n_permutations: int = N_PERMUTATIONS,
                     seed: int = PERMUTATION_SEED) -> dict:
    """The empirical null for the WHOLE procedure - feature selection included.

    Each draw relabels the data and re-runs `cv_accuracy` end to end, so the p-value
    prices in the fact that 26 features were searched. Scoring only the observed
    feature would understate the null and overstate the result.

    `pairs` = [(positive item_id, negative item_id)], the matching the eval set was
    built on. The observed labelling IS one of the draws (S-D), so the p-value can
    never be 0.
    """
    observed = cv_accuracy(rows)["best_accuracy"]
    by_id = {r["item_id"]: r for r in rows}
    for a, b in pairs:
        if a not in by_id or b not in by_id:
            raise BScriptError(f"pair ({a}, {b}) is not fully present in rows")

    rng = random.Random(seed)
    draws, mode = _within_pair_draws(pairs, rng, n_permutations)
    at_least = 0
    null_accs = []
    for draw in draws:
        for swap, (a, b) in zip(draw, pairs):
            by_id[a]["label"] = "WILL_EXECUTE" if swap else "WILL_FAIL"
            by_id[b]["label"] = "WILL_FAIL" if swap else "WILL_EXECUTE"
        acc = cv_accuracy(rows)["best_accuracy"]
        null_accs.append(acc)
        if acc >= observed:
            at_least += 1
    # restore the true labels - a null that leaves the data permuted poisons whatever
    # runs next, and that is a silent corruption rather than an error
    for a, b in pairs:
        by_id[a]["label"] = "WILL_FAIL"
        by_id[b]["label"] = "WILL_EXECUTE"

    null_accs.sort()
    return {
        "observed_best_cv_accuracy": observed,
        "n_draws": len(draws),
        "mode": mode,
        "seed": seed,
        "draws_at_or_above_observed": at_least,
        "p_value": at_least / len(draws),
        "null_mean": sum(null_accs) / len(null_accs),
        "null_p50": null_accs[len(null_accs) // 2],
        "null_p95": null_accs[min(len(null_accs) - 1, int(0.95 * len(null_accs)))],
        "null_max": null_accs[-1],
        "note": ("within-pair permutation; the whole procedure including feature "
                 "selection is re-run per draw; the observed labelling is one of the "
                 "draws so p can never be 0"),
    }


def free_permutation_null(rows, n_permutations: int = N_PERMUTATIONS,
                          seed: int = PERMUTATION_SEED) -> dict:
    """The DIAGNOSTIC null: labels shuffled freely, ignoring the matching. Reported
    beside the within-pair null and never instead of it (S-E)."""
    observed = cv_accuracy(rows)["best_accuracy"]
    labels = [r["label"] for r in rows]
    rng = random.Random(seed)
    at_least = 0
    for _ in range(n_permutations):
        shuffled = labels[:]
        rng.shuffle(shuffled)
        for r, lab in zip(rows, shuffled):
            r["label"] = lab
        if cv_accuracy(rows)["best_accuracy"] >= observed:
            at_least += 1
    for r, lab in zip(rows, labels):
        r["label"] = lab
    return {"observed_best_cv_accuracy": observed,
            "n_draws": n_permutations, "seed": seed,
            "draws_at_or_above_observed": at_least,
            "p_value": at_least / n_permutations,
            "note": "FREE permutation - ignores the pairing. Diagnostic only."}


def cv_predictions(rows, feature: str) -> dict:
    """OUT-OF-FOLD predictions for one feature. Pure.

    The threshold is fitted on the training folds and applied to the held-out fold, so
    no item is ever predicted by a rule that saw it. This is what the scorer's guards
    and rates are computed on - an in-sample prediction would flatter every one of
    them.
    """
    assign = fold_assignment([r["group"] for r in rows])
    out = {}
    for fold in range(N_FOLDS):
        train = [r for r in rows if assign[r["group"]] != fold]
        test = [r for r in rows if assign[r["group"]] == fold]
        if not train or not test:
            continue
        rule = best_threshold([r["features"][feature] for r in train],
                              [r["label"] for r in train])
        preds = apply_threshold([r["features"][feature] for r in test], rule)
        for pred, r in zip(preds, test):
            out[r["item_id"]] = WILL_FAIL if pred else "WILL_EXECUTE"
    if len(out) != len(rows):
        raise BScriptError(
            f"out-of-fold predictions cover {len(out)} of {len(rows)} items; an item "
            "with no prediction would silently leave the denominator")
    return out


def build_rows(items) -> list[dict]:
    return [{"item_id": it["item_id"], "label": it["label"],
             "group": it["frdoc"], "features": features(it)} for it in items]
