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
already applied. Restated, not re-chosen.

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
    runs = []
    for path in sorted(directory.glob(f"{arm}-rep*.json")):
        if path.name.startswith(f"{arm}-rep") and "artifacts" not in path.name:
            runs.append(json.loads(path.read_text(encoding="utf-8")))
    if not runs:
        return {}, [], 0
    return majority([r["predictions"] for r in runs]), runs, len(runs)


def load_artifacts(arm: str) -> dict[str, dict]:
    """The LAST rep's emitted notes, for the trace-level analysis."""
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
        w(f"  {'arm':16s} {'tool?':>6s} {'calls':>8s} {'calls/item':>11s} {'items w/ 0 calls':>17s}")
        for a in order:
            arts = load_artifacts(a)
            if not arts:
                continue
            calls = sum(x.get("tool_calls_made", 0) for x in arts.values())
            zero = sum(1 for x in arts.values() if not x.get("tool_calls_made"))
            has_tool = "yes" if a in ("A1", "A1-iter1") else "no"
            w(f"  {a:16s} {has_tool:>6s} {calls:>8d} {calls / max(1, len(arts)):>11.2f}"
              f" {zero:>13d}/{len(arts)}")
        w("")
        w("  AVAILABILITY IS NOT USE. An arm holding the tool and not calling it is")
        w("  measured here rather than assumed away; it is the difference between")
        w("  shipping a capability and the agent exercising one.")
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
