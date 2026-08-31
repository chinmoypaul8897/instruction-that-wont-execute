"""CH-06 §2e / CH-08 — A1 against B0-agent, and every ablation, in one report.

    python docs/evidence/ch06-a1/analyse_a1.py

Reads only committed artifacts. Writes `a1-result.txt`, `a1-result.json`, the per-arm
token/cost table, and `docs/evidence/error-taxonomy.csv`.

WHAT IT COMPUTES, AND UNDER WHOSE RULES
---------------------------------------
* the primary metric, `src/score.py`, unmodified - `CONTEXT.md` §7
* exact two-sided McNemar - `src/score.py::mcnemar`
* a **paired bootstrap CLUSTERED BY FR DOCUMENT** - `plan.md` CH-08. A positive and its
  count-matched negative come from the same rule and share its label structure, so an
  item-level resample overstates confidence. `probe_cluster_matters()` demonstrates the
  difference rather than asserting it.
* the guards, per arm, never blended
* `GOOD.md`'s frozen success criterion, evaluated clause by clause, **with the n = 82
  against n ≥ 84 shortfall stated in the same breath** (`QUESTIONS.md`, Q16 ruling)
* per-class recall, because `CONTEXT.md` §11 says the average will lie to you
* the **tool-availability-vs-tool-use gap** - `plan.md` CH-06

Aggregation across reps is MAJORITY, ties to the FAILURE side - the rule the checkpoint
already applied. Restated here, NOT re-chosen after seeing an A1 number.

    DISCLOSED, from the CH-04 adversarial review (finding F3, `docs/reviews/
    REVIEW_CH-04.md`): THIS RULE IS PRE-REGISTERED NOWHERE. It appears in no binding
    document - not `CONTEXT.md`, not `GOOD.md`, not `plan.md` - and debuts in
    `docs/evidence/checkpoint/analyse_checkpoint.py`, committed AFTER the first arm
    call, whose docstring wrongly calls it pre-registered. The reviewer measured the
    alternatives and every one of them still lands the checkpoint on GREEN, so nothing
    published turns on the choice. It is restated here for consistency with the
    baseline it is compared against, and the fact that it was never pre-registered is
    printed in this script's own output rather than left in a review file.

PURITY: no network, no clock. The bootstrap's RNG is seeded from `GOOD.md`'s declared
`20260831` and the seed is printed with the interval.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from score import (  # noqa: E402
    bootstrap_ci_clustered, detectable_effect, mcnemar, normalise_verdict, score,
)

HERE = Path(__file__).resolve().parent
CHECKPOINT = REPO / "docs/evidence/checkpoint"
EVALSET = REPO / "data/evalset/items.jsonl"
LEDGER = REPO / "docs/evidence/runs/cost_ledger.csv"
TAXONOMY = REPO / "docs/evidence/error-taxonomy.csv"

B0_AGENT = "B0-agent"
SEED = 20260831          # GOOD.md section 5 declares it; echoed with every interval


def load_items():
    return sorted((json.loads(l) for l in EVALSET.read_text(encoding="utf-8").splitlines()
                   if l.strip()), key=lambda i: i["item_id"])


def majority(reps: list[dict]) -> dict:
    out = {}
    for k in sorted({k for r in reps for k in r}):
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


def collect(arm: str, directory: Path) -> tuple[dict, list[dict], int]:
    """All reps of one arm -> (majority predictions, per-rep run dicts, n_reps)."""
    import re as _re
    # STRICT: `<arm>-rep<N>.json` and nothing else. The loose glob also matched the
    # sidecars this pipeline writes - `-rep1-artifacts.jsonl` and B0prime's
    # `-rep1-votes.json` - and a votes file has no `predictions` key, so it would have
    # crashed the collector or, worse, been counted as a rep.
    pat = _re.compile(rf"^{_re.escape(arm)}-rep\d+\.json$")
    runs = []
    for path in sorted(directory.glob(f"{arm}-rep*.json")):
        if pat.match(path.name):
            runs.append(json.loads(path.read_text(encoding="utf-8")))
    if not runs:
        return {}, [], 0
    return majority([r["predictions"] for r in runs]), runs, len(runs)


def load_artifacts(arm: str) -> dict[str, dict]:
    """The LAST rep's emitted notes, for the trace-level analysis.

    The scored `predicted` column always comes from the MAJORITY across reps; the trace
    detail can only come from ONE rep, and the last is chosen by a rule rather than by
    inspection. Where that rep's own verdict differs from the majority the taxonomy says
    so in `trace_rep_agrees_with_majority`, because a trace explaining a verdict the arm
    did not report would be a fabricated explanation.
    """
    paths = sorted(HERE.glob(f"{arm}-rep*-artifacts.jsonl"))
    if not paths:
        return {}
    out = {}
    for line in paths[-1].read_text(encoding="utf-8").splitlines():
        if line.strip():
            a = json.loads(line)
            out[a["item_id"]] = a
    return out


def probe_cluster_matters(items, preds) -> dict:
    """`plan.md` CH-08 asks for a probe that FAILS under item-level resampling.

    Same data, same seed, same reps - the only change is the resampling unit. If the
    item-level interval is not narrower, clustering bought nothing and the claim that
    it was necessary would be decoration.
    """
    clusters = {i["item_id"]: i["frdoc"] for i in items}
    singletons = {i["item_id"]: i["item_id"] for i in items}
    by_doc = bootstrap_ci_clustered(items, preds, clusters, seed=SEED)
    by_item = bootstrap_ci_clustered(items, preds, singletons, seed=SEED)
    w_doc = by_doc["ci_high"] - by_doc["ci_low"]
    w_item = by_item["ci_high"] - by_item["ci_low"]
    return {
        "clustered_by_frdoc": by_doc, "resampled_by_item": by_item,
        "width_clustered": w_doc, "width_item_level": w_item,
        "item_level_is_narrower": w_item < w_doc,
        "narrower_by_pp": 100.0 * (w_doc - w_item),
        "verdict": ("PROBE FLIPS: the item-level interval is narrower, so item-level "
                    "resampling would have overstated confidence and clustering by FR "
                    "document is doing real work"
                    if w_item < w_doc else
                    "PROBE DOES NOT FLIP: clustering did not widen the interval here; "
                    "the methodological argument stands but this data does not "
                    "demonstrate it, and that is reported rather than asserted"),
    }


def ledger_by_arm() -> dict[str, dict]:
    if not LEDGER.exists():
        return {}
    agg: dict[str, dict] = defaultdict(
        lambda: {"rows": 0, "in": 0, "out": 0, "usd": Decimal("0"), "wall": 0.0,
                 "unknown_cost": 0})
    with open(LEDGER, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            a = agg[row["arm"]]
            a["rows"] += 1
            a["in"] += int(row["input_tokens"] or 0)
            a["out"] += int(row["output_tokens"] or 0)
            a["wall"] += float(row["wall_clock_s"] or 0)
            if (row["imputed_usd"] or "").strip():
                a["usd"] += Decimal(row["imputed_usd"])
            else:
                a["unknown_cost"] += 1
    return dict(agg)


def rep_stability(runs: list[dict], items) -> dict:
    """How much does this arm move BETWEEN REPS at temperature 0?

    Committed as a live obligation in `QUESTIONS.md` Q24's retraction, and it turns out
    to matter far more than the retraction expected. A temperature-0 arm is widely
    assumed deterministic; the checkpoint's three `B0-agent` reps were in fact
    identical. **A tool-using arm is not**, because the agentic loop varies in how many
    calls it makes and in what order, and each variation changes the context the next
    turn is sampled from.

    This is reported because it bounds what the SINGLE-REP arms can carry. `A1-iter1`,
    `A1-minus-tool` and `B0prime` are 1 rep each by `GOOD.md` §8 / ruling R-01, so any
    ablation gap smaller than the rep-to-rep spread measured here is inside the noise
    and must not be read as an effect.
    """
    if len(runs) < 2:
        return {"n_reps": len(runs), "comparable": False}
    ids = [i["item_id"] for i in items]
    accs, pairs = [], []
    for r in runs:
        p_ = r["predictions"]
        accs.append(sum(1 for i in items
                        if normalise_verdict(p_.get(i["item_id"])) == i["label"]) / len(items))
    for a in range(len(runs)):
        for b in range(a + 1, len(runs)):
            pa, pb = runs[a]["predictions"], runs[b]["predictions"]
            diff = [k for k in ids
                    if normalise_verdict(pa.get(k)) != normalise_verdict(pb.get(k))]
            pairs.append({"rep_a": runs[a]["rep"], "rep_b": runs[b]["rep"],
                          "n_disagree": len(diff), "rate": len(diff) / len(ids)})
    return {"n_reps": len(runs), "comparable": True,
            "per_rep_accuracy": accs,
            "accuracy_spread_pp": 100.0 * (max(accs) - min(accs)),
            "pairwise": pairs,
            "max_disagreement_rate": max(p_["rate"] for p_ in pairs)}


def tool_use_profile(arts: dict) -> dict:
    """`plan.md` CH-06's TOOL-AVAILABILITY-VS-TOOL-USE GAP, in three separable layers.

    Availability is not use, and use is not agreement. An arm can hold the tool and
    never call it; call it and ignore what came back; or call it, disagree with it, and
    be right to. Only the third layer distinguishes `A1` from `A1-iter1`, because Step
    2.5 of the v2 skill exists precisely to make the agent OVERRIDE a resolver it has
    measured to be wrong (`QUESTIONS.md` Q21).

    OVERRIDE is counted only on instructions where the resolver actually asserted
    something - `designation_exists is True/False`, never `None`, which means nothing
    was asked and there is nothing to agree or disagree with.
    """
    n_items = len(arts)
    calls = sum(a.get("tool_calls_made", 0) for a in arts.values())
    zero = sum(1 for a in arts.values() if not a.get("tool_calls_made"))
    ruled = agree = override_to_fail = override_to_pass = 0
    override_items = set()
    for a in arts.values():
        for t in a.get("resolution_trace", []):
            mr = t.get("model_ruling") or {}
            if mr.get("executes") is None or t.get("designation_exists") is None:
                continue
            ruled += 1
            resolver_says_ok = bool(t["designation_exists"])
            model_says_ok = bool(mr["executes"])
            if resolver_says_ok == model_says_ok:
                agree += 1
            else:
                override_items.add(a["item_id"])
                if model_says_ok:
                    # resolver said the target is ABSENT; the model ruled it EXECUTES.
                    # This is the Step 2.5 cross-check firing - the shape that recovers
                    # Q21's false defects.
                    override_to_pass += 1
                else:
                    override_to_fail += 1
    return {"n_items": n_items, "tool_calls": calls,
            "calls_per_item": calls / max(1, n_items),
            "items_with_zero_calls": zero,
            "instructions_where_resolver_asserted": ruled,
            "model_agrees_with_resolver": agree,
            "model_overrides_resolver": ruled - agree,
            "override_rate": (ruled - agree) / max(1, ruled),
            "override_toward_EXECUTES": override_to_pass,
            "override_toward_FAILS": override_to_fail,
            "items_containing_an_override": len(override_items)}


def per_class_recall(items, preds) -> dict:
    out = {}
    for label in ("WILL_FAIL", "WILL_EXECUTE"):
        sub = [i for i in items if i["label"] == label]
        hit = sum(1 for i in sub if preds.get(i["item_id"]) == label)
        out[label] = {"n": len(sub), "correct": hit,
                      "recall": (hit / len(sub)) if sub else 0.0}
    return out


def main() -> int:
    items = load_items()
    by_id = {i["item_id"]: i for i in items}
    clusters = {i["item_id"]: i["frdoc"] for i in items}

    arms: dict[str, dict] = {}
    b0a_preds, b0a_runs, b0a_reps = collect(B0_AGENT, CHECKPOINT)
    b0_preds, _, _ = collect("B0", CHECKPOINT)
    if b0a_preds:
        arms[B0_AGENT] = {"preds": b0a_preds, "reps": b0a_reps, "runs": b0a_runs}
    if b0_preds:
        arms["B0"] = {"preds": b0_preds, "reps": 3, "runs": []}
    for arm in ("A1-iter1", "A1", "A1-minus-tool", "B0prime"):
        p, runs, reps = collect(arm, HERE)
        if p:
            arms[arm] = {"preds": p, "reps": reps, "runs": runs}

    results = {a: score(items, d["preds"]) for a, d in arms.items()}

    lines = []
    w = lines.append
    w("=" * 78)
    w("*** CH-06 / CH-08 - A1, THE ADVANCED SOLUTION, AGAINST EVERY BASELINE")
    w("=" * 78)
    w("")
    w("  DEVIATION FROM THE PRE-REGISTRATION, DISCLOSED HERE AND NOT ABSORBED:")
    w("  GOOD.md section 11 named data/evalset-restricted/ as the primary eval set.")
    w("  The primary used below is the UNRESTRICTED set - 41 pairs, n = 82 - by the")
    w("  architect's Q19 ruling of 2026-08-31. The restricted set yields ONE pair and")
    w("  measures nothing. Both sets are committed and either can be run.")
    w("")
    w(f"  eval set   {EVALSET.relative_to(REPO).as_posix()}   n = {len(items)}"
      f"   {sum(1 for i in items if i['label'] == 'WILL_FAIL')} positive"
      f" / {sum(1 for i in items if i['label'] == 'WILL_EXECUTE')} negative")
    w(f"  clusters   {len(set(clusters.values()))} FR documents")
    w("  model      claude-haiku-4-5-20251001 @ temperature 0, EVERY arm")
    w("  reps       aggregated MAJORITY, ties to the FAILURE side")
    w("             ^ NOT PRE-REGISTERED - CH-04 review finding F3. The rule is in no")
    w("               binding document and debuts in analyse_checkpoint.py, committed")
    w("               after the first arm call. Every alternative aggregation still")
    w("               lands the checkpoint on GREEN, so nothing turns on it; it is")
    w("               disclosed rather than defended.")
    w("")

    w("=" * 78)
    w("THE ARMS")
    w("=" * 78)
    w("")
    w(f"  {'arm':16s} {'reps':>4s} {'acc':>8s} {'succ/n':>9s} {'false-def':>10s}"
      f" {'missed-def':>11s} {'unparse':>8s}")
    order = [a for a in ("B0", "B0-agent", "B0prime", "A1-iter1", "A1-minus-tool", "A1")
             if a in results]
    for a in order:
        r = results[a]
        w(f"  {a:16s} {arms[a]['reps']:>4d} {r['accuracy']:>8.4f}"
          f" {r['success']:>4d}/{r['n']:<4d}"
          f" {r['false_defect_rate']:>10.4f} {r['missed_defect_rate']:>11.4f}"
          f" {r['unparseable_or_absent']:>8d}")
    w("")
    w("  guards, per arm, NEVER blended - CONTEXT.md section 7, thresholds not moved:")
    for a in order:
        r = results[a]
        w(f"    {a:16s} false-defect {r['false_defect_rate']:.4f} <= 0.25 "
          f"{'PASS' if r['guard_false_defect_pass'] else 'FAIL'}"
          f"   missed-defect {r['missed_defect_rate']:.4f} <= 0.25 "
          f"{'PASS' if r['guard_missed_defect_pass'] else 'FAIL'}")
    w("")
    w("  attributor completeness 0.5340 against >= 0.90 was ALREADY FAILED before any")
    w("  arm ran (GOOD.md section 3). The accuracy headline is withdrawn on that guard")
    w("  and nothing below restores it.")
    w("")

    w("=" * 78)
    w("PER-CLASS RECALL - CONTEXT.md section 11: the average will lie to you")
    w("=" * 78)
    w("")
    w(f"  {'arm':16s} {'WILL_FAIL':>12s} {'WILL_EXECUTE':>14s}   {'delta vs B0-agent':>22s}")
    base_rec = per_class_recall(items, arms[B0_AGENT]["preds"]) if B0_AGENT in arms else None
    for a in order:
        rc = per_class_recall(items, arms[a]["preds"])
        d = ""
        if base_rec and a != B0_AGENT:
            d = (f"{100 * (rc['WILL_FAIL']['recall'] - base_rec['WILL_FAIL']['recall']):+6.1f} pp"
                 f" / {100 * (rc['WILL_EXECUTE']['recall'] - base_rec['WILL_EXECUTE']['recall']):+6.1f} pp")
        w(f"  {a:16s} {rc['WILL_FAIL']['recall']:>12.4f} {rc['WILL_EXECUTE']['recall']:>14.4f}   {d:>22s}")
    w("")

    comparisons = {}
    if B0_AGENT in arms:
        w("=" * 78)
        w("THE COMPARISON - each arm against B0-agent, PAIRED")
        w("=" * 78)
        w("")
        base = [normalise_verdict(arms[B0_AGENT]["preds"].get(i["item_id"])) == i["label"]
                for i in items]
        for a in order:
            if a == B0_AGENT:
                continue
            vec = [normalise_verdict(arms[a]["preds"].get(i["item_id"])) == i["label"]
                   for i in items]
            mc = mcnemar(vec, base)
            gap = results[a]["accuracy"] - results[B0_AGENT]["accuracy"]
            ci = bootstrap_ci_clustered(items, arms[a]["preds"], clusters, seed=SEED)
            comparisons[a] = {"gap_pp": 100 * gap, "mcnemar": mc, "ci": ci,
                              "accuracy": results[a]["accuracy"]}
            w(f"  {a}  vs  B0-agent {results[B0_AGENT]['accuracy']:.4f}")
            w(f"    accuracy {results[a]['accuracy']:.4f}   gap {100 * gap:+.1f} pp")
            w(f"    McNemar exact two-sided p = {mc['p_value']:.4f}"
              f"   (b={mc['b_only_a_correct']} c={mc['c_only_b_correct']}"
              f" discordant={mc['n_discordant']})")
            w(f"    95% CI on accuracy, bootstrap CLUSTERED BY FR DOCUMENT, seed {SEED}:"
              f" [{ci['ci_low']:.4f}, {ci['ci_high']:.4f}]")
            w("")

    if "A1" in arms:
        w("=" * 78)
        w("THE CLUSTERING PROBE - plan.md CH-08 wants one that FAILS at item level")
        w("=" * 78)
        w("")
        pr = probe_cluster_matters(items, arms["A1"]["preds"])
        w(f"  clustered by FR document  width {pr['width_clustered']:.4f}"
          f"   [{pr['clustered_by_frdoc']['ci_low']:.4f}, {pr['clustered_by_frdoc']['ci_high']:.4f}]")
        w(f"  resampled by ITEM         width {pr['width_item_level']:.4f}"
          f"   [{pr['resampled_by_item']['ci_low']:.4f}, {pr['resampled_by_item']['ci_high']:.4f}]")
        w(f"  item-level narrower by    {pr['narrower_by_pp']:+.2f} pp of width")
        w("")
        for chunk in [pr["verdict"][i:i + 72] for i in range(0, len(pr["verdict"]), 72)]:
            w(f"  {chunk}")
        w("")

    if "A1" in arms:
        w("=" * 78)
        w("THE TOOL-AVAILABILITY-VS-TOOL-USE GAP - plan.md CH-06 requires it measured")
        w("=" * 78)
        w("")
        w("  LAYER 1 - AVAILABILITY vs USE. Did the arm call the tool it was given?")
        w("")
        w(f"  {'arm':16s} {'tool?':>6s} {'calls':>8s} {'calls/item':>11s} {'items w/ 0 calls':>17s}")
        profiles = {}
        for a in order:
            arts = load_artifacts(a)
            if not arts:
                continue
            pr = tool_use_profile(arts)
            profiles[a] = pr
            has_tool = "yes" if a in ("A1", "A1-iter1") else "no"
            w(f"  {a:16s} {has_tool:>6s} {pr['tool_calls']:>8d}"
              f" {pr['calls_per_item']:>11.2f}"
              f" {pr['items_with_zero_calls']:>13d}/{pr['n_items']}")
        w("")
        w("  LAYER 2 - USE vs AGREEMENT. When the resolver asserted something about a")
        w("  designation, did the model's ruling go along with it? Counted only where")
        w("  designation_exists is true or false - never null, which means nothing was")
        w("  asked and there is nothing to agree or disagree with.")
        w("")
        w(f"  {'arm':16s} {'asserted':>9s} {'agree':>7s} {'override':>9s} {'rate':>7s}"
          f" {'->EXECUTES':>11s} {'->FAILS':>8s}")
        for a, pr in profiles.items():
            w(f"  {a:16s} {pr['instructions_where_resolver_asserted']:>9d}"
              f" {pr['model_agrees_with_resolver']:>7d}"
              f" {pr['model_overrides_resolver']:>9d}"
              f" {pr['override_rate']:>6.1%}"
              f" {pr['override_toward_EXECUTES']:>11d}"
              f" {pr['override_toward_FAILS']:>8d}")
        w("")
        w("  LAYER 3 - WHAT THE OVERRIDES MEAN. `->EXECUTES` is the Step 2.5 cross-check")
        w("  firing: the resolver said the target is ABSENT and the model ruled the")
        w("  instruction executes anyway, having checked `siblings` against the section")
        w("  text. That is the shape that recovers Q21's manufactured false defects, and")
        w("  the difference between A1 and A1-iter1 on this row is the SKILL's whole")
        w("  contribution made visible.")
        w("")
        w("  AVAILABILITY IS NOT USE, AND USE IS NOT AGREEMENT. An arm can hold the tool")
        w("  and never call it; call it and ignore the answer; or call it, disagree, and")
        w("  be RIGHT to. Only the third layer separates a capability that was shipped")
        w("  from one the agent actually exercised.")
        w("")

    # ------------------------------------------------------- rep stability
    w("=" * 78)
    w("REP-TO-REP STABILITY AT TEMPERATURE 0 - and why it bounds the ablations")
    w("=" * 78)
    w("")
    stab = {}
    for a in order:
        if arms[a].get("runs") and len(arms[a]["runs"]) >= 2:
            st = rep_stability(arms[a]["runs"], items)
            stab[a] = st
            w(f"  {a:16s} {st['n_reps']} reps   per-rep accuracy "
              f"{[f'{x:.4f}' for x in st['per_rep_accuracy']]}")
            w(f"  {'':16s} spread {st['accuracy_spread_pp']:.1f} pp   "
              f"max pairwise disagreement {st['max_disagreement_rate']:.1%} of items")
            for pr in st["pairwise"]:
                w(f"  {'':16s}   rep{pr['rep_a']} vs rep{pr['rep_b']}: "
                  f"{pr['n_disagree']} of {len(items)} items differ")
    if not stab:
        w("  no arm in this run has >= 2 reps to compare (zero, printed as zero)")
    w("")
    w("  A TEMPERATURE-0 TOOL-USING ARM IS NOT DETERMINISTIC. The checkpoint's three")
    w("  B0-agent reps were identical (0.6585 x3) because that arm makes ONE call per")
    w("  item. A1 runs an agentic loop, and the loop varies in how many tool calls it")
    w("  makes and in what order - so each turn is sampled from a context the previous")
    w("  turn shaped. Determinism at temperature 0 is a property of a SINGLE call, not")
    w("  of a multi-turn agent, and this is the measurement of the difference.")
    w("")
    w("  WHAT THIS COSTS THE ABLATIONS, stated plainly. A1-iter1, A1-minus-tool and")
    w("  B0prime are ONE REP each (GOOD.md section 8; ruling R-01 item 2). Any gap")
    w("  between them smaller than the spread above is INSIDE THE RUN-TO-RUN NOISE and")
    w("  must not be read as an effect. The ablation ordering is reported with that")
    w("  caveat attached rather than presented as if the numbers were exact.")
    w("")
    w("  hard rule 9 - DETERMINISM - is not violated by this. It binds the SCORER and")
    w("  the RESOLVER, both of which are pure and byte-reproducible; a sampled model is")
    w("  not in its scope. What would violate the rule is claiming a model arm is")
    w("  reproducible when it is not, which is why this section exists.")
    w("")

    # ---------------------------------------------------------------- GOOD.md
    w("=" * 78)
    w("AGAINST GOOD.md's FROZEN SUCCESS CRITERION - nothing here moved a number")
    w("=" * 78)
    w("")
    w("  \"A1 >= B0-agent + 8 pp, McNemar p < 0.05, at n >= 84, and A1 >= 0.80 absolute.\"")
    w("")
    if "A1" in arms and B0_AGENT in arms:
        c = comparisons["A1"]
        acc = results["A1"]["accuracy"]
        cl = [
            ("A1 >= B0-agent + 8 pp", c["gap_pp"] >= 8.0,
             f"gap {c['gap_pp']:+.1f} pp"),
            ("McNemar p < 0.05", c["mcnemar"]["p_value"] < 0.05,
             f"p = {c['mcnemar']['p_value']:.4f}"),
            ("n >= 84", len(items) >= 84,
             f"n = {len(items)}  - TWO SHORT of the 84 the criterion names"),
            ("A1 >= 0.80 absolute", acc >= 0.80, f"A1 = {acc:.4f}"),
        ]
        for name, ok, detail in cl:
            w(f"    {'MET    ' if ok else 'NOT MET'}  {name:26s}  {detail}")
        w("")
        w("  THE CRITERION AS A WHOLE IS NOT MET, and the n clause alone was already")
        w("  unsatisfiable before any arm ran. GOOD.md section 4 recorded that in")
        w("  advance. Per the architect's Q16 ruling of 2026-08-31: 84 IS NOT MOVED,")
        w("  the result is reported at n = 82 against a criterion written for 84, and")
        w("  the two-item shortfall is stated wherever the criterion is quoted.")
        w("  Reported split: UNMET ON n, and the effect clauses evaluated on their own.")
        w("")
        de = detectable_effect(len(items) // 2)
        w(f"  what this n can detect: smallest all-one-way discordant count clearing")
        w(f"  alpha = 0.05 is {de['min_discordant_all_one_way']}, a floor of "
          f"{de['min_detectable_gap_pp']:.1f} pp. A mixed split needs more.")
        w("")
        w("  Q20's two readings of the cb65539 Iteration 1 card's \"gap above 20 pp\":")
        gap_vs_b0 = 100 * (acc - results["B0"]["accuracy"]) if "B0" in results else None
        if gap_vs_b0 is not None:
            w(f"    (a) A1 - B0        = {gap_vs_b0:+.1f} pp"
              f"   {'MET' if gap_vs_b0 > 20 else 'NOT MET'}")
        w(f"    (b) A1 - B0-agent  = {c['gap_pp']:+.1f} pp"
          f"   {'MET' if c['gap_pp'] > 20 else 'NOT MET'}   <- the BINDING reading")
        w("")

    # ---------------------------------------------------------------- money
    w("=" * 78)
    w("PER-ARM TOKENS AND COST - docs/evidence/runs/cost_ledger.csv")
    w("=" * 78)
    w("")
    led = ledger_by_arm()
    w(f"  {'arm':18s} {'calls':>6s} {'input tok':>12s} {'output tok':>11s}"
      f" {'USD':>9s} {'USD/item':>9s} {'wall s':>9s}")
    total_usd = Decimal("0")
    for a in sorted(led):
        d = led[a]
        total_usd += d["usd"]
        w(f"  {a:18s} {d['rows']:>6d} {d['in']:>12,d} {d['out']:>11,d}"
          f" {float(d['usd']):>9.4f} {float(d['usd']) / max(1, d['rows']):>9.5f}"
          f" {d['wall']:>9.1f}")
    w(f"  {'TOTAL':18s} {'':>6s} {'':>12s} {'':>11s} {float(total_usd):>9.4f}")
    w(f"  ceiling USD 18.00, enforced in src/runlog.py. Remaining: "
      f"{float(Decimal('18.00') - total_usd):.4f}")
    unknown = sum(d["unknown_cost"] for d in led.values())
    w(f"  ledger rows with an EMPTY cost cell: {unknown}"
      f"   (unknown is not the same claim as free)")
    w("")

    # ---------------------------------------------------------------- taxonomy
    if "A1" in arms:
        arts = load_artifacts("A1")
        rows = []
        for i in items:
            pred = arms["A1"]["preds"].get(i["item_id"])
            a = arts.get(i["item_id"], {})
            correct = pred == i["label"]
            trace = a.get("resolution_trace", [])
            failing_idx = next((t["instruction_index"] for t in trace
                                if (t.get("model_ruling") or {}).get("executes") is False),
                               None)
            # right verdict for the wrong reason: it ruled WILL_FAIL on an instruction
            # whose resolver facts do not support a failure.
            wrong_reason = ""
            if correct and i["label"] == "WILL_FAIL" and failing_idx:
                t = trace[failing_idx - 1]
                if t.get("designation_exists") is True and t.get("found") is not False:
                    wrong_reason = "right-verdict-possibly-wrong-reason"
            if not correct or wrong_reason:
                rows.append({
                    "item_id": i["item_id"], "frdoc": i["frdoc"],
                    "gold": i["label"], "predicted": pred if pred else "(none)",
                    "error_type": ("false-defect" if i["label"] == "WILL_EXECUTE" and not correct
                                   else "missed-defect" if not correct
                                   else wrong_reason),
                    "failure_class": a.get("failure_class") or "",
                    "failing_designation": a.get("failing_designation") or "",
                    "which_trace_step_went_wrong": (
                        f"instruction {failing_idx}" if failing_idx else
                        "no instruction ruled failing"),
                    "instruction_count": i["instruction_count"],
                    "tool_calls_made": a.get("tool_calls_made", 0),
                    "instructions_unruled": ";".join(str(x) for x in a.get("instructions_unruled", [])),
                    "needs_human_review": a.get("needs_human_review", ""),
                    # the trace is one rep's; the verdict is the majority's. When they
                    # disagree the trace does not explain the scored answer, and that is
                    # printed rather than glossed.
                    "trace_rep_verdict": a.get("verdict") or "(none)",
                    "trace_rep_agrees_with_majority": (a.get("verdict") == pred),
                })
        TAXONOMY.parent.mkdir(parents=True, exist_ok=True)
        with open(TAXONOMY, "w", encoding="utf-8", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else
                                ["item_id", "frdoc", "gold", "predicted", "error_type"])
            wr.writeheader()
            wr.writerows(rows)
        w("=" * 78)
        w("A1 ERROR TAXONOMY - docs/evidence/error-taxonomy.csv")
        w("=" * 78)
        w("")
        w(f"  {len(rows)} row(s) written")
        cnt = Counter(r["error_type"] for r in rows)
        for k, v in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
            w(f"    {k or '(none)':38s} {v:4d}")
        if not rows:
            w("    ZERO rows. Printed as zero rather than omitted (hard rule 14).")
        w("")
        fc = Counter(r["failure_class"] for r in rows if r["failure_class"])
        w(f"  failure_class on the error rows: {dict(fc) if fc else '{} (zero)'}")
        w("")
        routed = sum(1 for x in arts.values() if x.get("needs_human_review"))
        w(f"  items routed to the HUMAN CHECKPOINT: {routed} of {len(arts)}")
        w("")

    text = "\n".join(lines) + "\n"
    print(text)
    (HERE / "a1-result.txt").write_text(text, encoding="utf-8", newline="\n")
    (HERE / "a1-result.json").write_text(
        json.dumps({"results": {a: {k: v for k, v in r.items() if k != "per_item"}
                                for a, r in results.items()},
                    "comparisons": comparisons,
                    "per_class_recall": {a: per_class_recall(items, arms[a]["preds"])
                                         for a in arms},
                    "ledger": {a: {**{k: (float(v) if isinstance(v, Decimal) else v)
                                      for k, v in d.items()}} for a, d in led.items()},
                    "n": len(items), "seed": SEED},
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(f"  wrote a1-result.txt / .json and {TAXONOMY.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
