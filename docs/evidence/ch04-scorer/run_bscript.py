"""CH-04 3b — run the B-script arm on the frozen eval set and publish its null.

This is `CONTEXT.md` §4's **type 3 PDF baseline**: the best model-free attack. It is
built to WIN if it can. A baseline built to lose is a rigged benchmark by another name,
and an unmatched eval set once let a threshold on `n_instructions` beat an agent
outright — which is the failure this whole corpus design exists to prevent.

No model. No network. Runs from `data/evalset/items.jsonl` alone.

    python docs/evidence/ch04-scorer/run_bscript.py
    # committed outputs: bscript-run.txt, bscript-result.json
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import bscript  # noqa: E402
from bscript import (  # noqa: E402
    N_PERMUTATIONS,
    PERMUTATION_SEED,
    build_rows,
    cv_accuracy,
    cv_predictions,
    free_permutation_null,
    permutation_null,
)
from score import (  # noqa: E402
    bootstrap_ci_clustered,
    detectable_effect,
    score,
)

OUT = Path(__file__).resolve().parent
EVALSET = REPO / "data/evalset/items.jsonl"


def reconstruct_pairs(items):
    """Rebuild the (positive, negative) matching from the frozen items.

    The eval set is matched on `(frdoc, instruction_count)`, so items are grouped by
    that key and the sorted positives are zipped with the sorted negatives. The
    within-pair null only needs a VALID matching of the exchangeable units, and this
    one is deterministic and reproduces from the freeze alone.

    Raises rather than guessing if a group is unbalanced - an unbalanced group would
    mean the exact-count matching had been broken upstream, and silently dropping the
    odd item would hide it.
    """
    groups: dict[tuple, dict[str, list]] = {}
    for it in items:
        key = (it["frdoc"], it["instruction_count"])
        groups.setdefault(key, {"WILL_FAIL": [], "WILL_EXECUTE": []})
        groups[key][it["label"]].append(it["item_id"])
    pairs = []
    for key in sorted(groups):
        pos = sorted(groups[key]["WILL_FAIL"])
        neg = sorted(groups[key]["WILL_EXECUTE"])
        if len(pos) != len(neg):
            raise SystemExit(
                f"UNBALANCED group {key}: {len(pos)} positives, {len(neg)} negatives. "
                "The exact instruction-count matching is broken upstream.")
        pairs.extend(zip(pos, neg))
    return pairs


def main() -> int:
    items = [json.loads(l) for l in
             EVALSET.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = build_rows(items)
    pairs = reconstruct_pairs(items)

    cv = cv_accuracy(rows)
    preds = cv_predictions(rows, cv["best_feature"])
    sc = score([{"item_id": i["item_id"], "label": i["label"]} for i in items], preds)
    clusters = {i["item_id"]: i["frdoc"] for i in items}
    ci = bootstrap_ci_clustered(
        [{"item_id": i["item_id"], "label": i["label"]} for i in items],
        preds, clusters)
    power = detectable_effect(len(pairs))

    within = permutation_null(rows, pairs, n_permutations=N_PERMUTATIONS)
    free = free_permutation_null(rows, n_permutations=N_PERMUTATIONS)

    ranked = sorted(cv["per_feature"].items(), key=lambda kv: (-kv[1], kv[0]))

    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 78)
    p("CH-04 3b - THE B-SCRIPT ARM (PDF baseline type 3) AND ITS PERMUTATION NULL")
    p("=" * 78)
    p("")
    p(f"  eval set        data/evalset/items.jsonl")
    p(f"  n               {sc['n']}   ({sc['n_positives']} positive / "
      f"{sc['n_negatives']} negative)")
    p(f"  pairs           {len(pairs)}")
    p(f"  features        {cv['n_features']}   (CONTEXT.md section 4 says ~26)")
    p(f"  validation      {cv['folds']}-fold, GROUPED BY FR DOCUMENT, no RNG")
    p("")
    p("=" * 78)
    p("RESULT")
    p("=" * 78)
    p("")
    p(f"  best feature                 {cv['best_feature']}")
    p(f"  held-out CV accuracy         {cv['best_accuracy']:.4f}")
    p(f"  95% CI (clustered by FR doc) [{ci['ci_low']:.4f}, {ci['ci_high']:.4f}]"
      f"   {ci['reps']} reps, seed {ci['seed']}")
    p("")
    p(f"  success + failure == n       {sc['success']} + {sc['failure']} = {sc['n']}"
      f"   ASSERTED")
    p(f"  false-defect rate            {sc['false_defect_rate']:.4f}"
      f"   (guard <= {sc['guard_false_defect_max']})   "
      f"{'PASS' if sc['guard_false_defect_pass'] else 'FAIL'}")
    p(f"  missed-defect rate           {sc['missed_defect_rate']:.4f}"
      f"   (guard <= {sc['guard_missed_defect_max']})   "
      f"{'PASS' if sc['guard_missed_defect_pass'] else 'FAIL'}")
    p(f"  unparseable or absent        {sc['unparseable_or_absent']}")
    p("")
    p("=" * 78)
    p("THE NULL - the whole procedure, feature selection included, re-run per draw")
    p("=" * 78)
    p("")
    p(f"  PRIMARY  within-pair permutation   (respects the count-matched design)")
    p(f"    draws                      {within['n_draws']}  ({within['mode']}, "
      f"seed {within['seed']})")
    p(f"    draws >= observed          {within['draws_at_or_above_observed']}")
    p(f"    p-value                    {within['p_value']:.4f}")
    p(f"    null mean / p50 / p95 / max"
      f"   {within['null_mean']:.4f} / {within['null_p50']:.4f} /"
      f" {within['null_p95']:.4f} / {within['null_max']:.4f}")
    p("")
    p(f"  DIAGNOSTIC  free permutation       (ignores the pairing - reported beside)")
    p(f"    draws                      {free['n_draws']}  (seed {free['seed']})")
    p(f"    p-value                    {free['p_value']:.4f}")
    p("")
    p("=" * 78)
    p("EVERY FEATURE, RANKED - so nobody has to take 'best of 26' on trust")
    p("=" * 78)
    p("")
    for name, acc in ranked:
        flag = "  <- selected" if name == cv["best_feature"] else ""
        p(f"    {acc:.4f}  {name}{flag}")
    p("")
    p("=" * 78)
    p("WHAT THIS n CAN AND CANNOT DETECT")
    p("=" * 78)
    p("")
    p(f"  pairs {power['n_pairs']}, n {power['n_items']}, alpha {power['alpha']}")
    p(f"  smallest ALL-ONE-WAY discordant count that clears alpha: "
      f"{power['min_discordant_all_one_way']}")
    p(f"  implied floor on the detectable gap: "
      f"{power['min_detectable_gap_pp']:.1f} pp")
    p(f"  {power['note']}")
    p("")
    p("  The instruction-count feature is pinned AT CHANCE BY CONSTRUCTION: the eval")
    p("  set matches positives to negatives on it exactly, so the two classes have")
    p("  identical distributions. That is the whole point of the matching, and")
    p("  tests/test_eval_set.py asserts it on the frozen data.")

    text = w.getvalue()
    io.open(OUT / "bscript-run.txt", "w", encoding="utf-8", newline="\n").write(text)
    io.open(OUT / "bscript-result.json", "w", encoding="utf-8", newline="\n").write(
        json.dumps({
            "arm": "B-script",
            "eval_set": "data/evalset/items.jsonl",
            "n": sc["n"], "pairs": len(pairs),
            "best_feature": cv["best_feature"],
            "cv_accuracy": cv["best_accuracy"],
            "per_feature_cv_accuracy": cv["per_feature"],
            "score": {k: v for k, v in sc.items() if k != "per_item"},
            "bootstrap_ci": ci,
            "permutation_null_within_pair": within,
            "permutation_null_free": free,
            "detectable_effect": power,
            "seed": PERMUTATION_SEED,
            "n_permutations": N_PERMUTATIONS,
        }, indent=2, sort_keys=True) + "\n")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
