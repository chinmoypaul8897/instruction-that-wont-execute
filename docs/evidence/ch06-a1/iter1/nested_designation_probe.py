"""CH-06 — MEASURING A CEILING IN `cfr_resolve`, WITHOUT TOUCHING IT.

Found during the 3-item A1 smoke test, before the paid runs: on item `05-8447|75.31`
A1 ruled `WILL_FAIL` because `cfr_resolve` reported `designation_exists: false` for
`(b)(1)`. The gold label is `WILL_EXECUTE`. **The paragraph is there.**

WHAT THE CFR ACTUALLY WRITES
----------------------------
`declared_designations()` on that section returns

    [('(a)', 41), ('(b)', 858), ('(1)', 1251), ('(2)', 1653), ('(c)', 2477), ...]

The children of `(b)` are declared as **bare `(1)`, `(2)`** — the codified text does not
repeat the parent. `cfr_resolve.designation_state()` builds the canonical string
`(b)(1)` and looks for it among the declared designations, so it finds nothing and
returns `designation_exists: false` for a paragraph that a human drafter would locate in
seconds.

**This is a real ceiling on capability 1 and it produces FALSE DEFECTS**, which is the
error direction that matters least for the missed-defect guard and most for a drafter
who would be sent chasing a defect that is not there.

THIS SCRIPT DOES NOT FIX IT. IT COUNTS IT.
------------------------------------------
`src/cfr_resolve.py` is **outside CH-06's scope fence**, and CH-05 is a `built`,
unreviewed, gated chunk. Changing it here would be all three of:

  * a scope-fence violation;
  * a **Class A** change under hard rule 3 — it changes results — made without the
    architect's ruling;
  * and, decisively, **a change to a capability made after seeing that it cost the
    headline number a point.** That is the exact move hard rules 5 and 17 exist to stop.
    The defect was found *because* it hurt A1. Fixing it on that basis would be tuning,
    however good the engineering argument.

So the tool ships as committed at `cb65539`, A1 runs against it, and the ceiling is
**measured and published** as a limitation of the shipped capability. `QUESTIONS.md` Q21
raises it to the architect as Class A.

The nested-aware reading below exists ONLY to size the gap. It is never imported by
`src/`, never used to score an arm, and no arm's number depends on it.

PURITY: no network, no clock, no randomness. `data/` is read-only here.

    python docs/evidence/ch06-a1/iter1/nested_designation_probe.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from cfr_resolve import (  # noqa: E402
    ResolveError, declared_designations, designation_state, parse_designation,
)

EVALSET = REPO / "data/evalset/items.jsonl"
OUT = Path(__file__).resolve().parent / "nested_designation_probe.txt"


def nested_aware_exists(text: str, designation: str) -> bool | None:
    """MEASUREMENT ONLY. A second, independent reading of "does this paragraph exist".

    The CFR declares a nested paragraph as a bare child under its parent - `(b)` then
    `(1)` - rather than repeating the parent. So `(b)(4)(i)(A)` exists if, walking the
    declaration list in document order, each component appears at its level AFTER its
    parent and BEFORE the parent's next sibling.

    Deliberately simple and deliberately NOT installed in the shipped tool: it is one
    reading of a hierarchy the flattened text only implies, and adopting a reading is
    the architect's call, not a probe's.
    """
    path = parse_designation(designation)
    if not path:
        return None
    declared = declared_designations(text)
    # The literal spelling still counts - some sections do write `(b)(1)` in full.
    canonical = "".join(f"({p})" for p in path)
    if any(d == canonical for d, _ in declared):
        return True
    # Otherwise walk: find each component, in order, after the previous one.
    lo = -1
    for comp in path:
        target = f"({comp})"
        nxt = next((o for d, o in declared if d == target and o > lo), None)
        if nxt is None:
            return False
        lo = nxt
    return True


def main() -> int:
    items = sorted(
        (json.loads(l) for l in EVALSET.read_text(encoding="utf-8").splitlines() if l.strip()),
        key=lambda i: i["item_id"])

    depth_hist = Counter()
    n_ins = n_desig = 0
    shipped_false_nested_true = []      # the disagreement that produces false defects
    shipped_true_nested_false = []      # the opposite direction, if any
    agree = 0
    refused = 0
    affected_items = set()

    for it in items:
        text = it["section_text"]
        for idx, ins in enumerate(it["instructions"], start=1):
            n_ins += 1
            d = ins.get("designation")
            if not d:
                continue
            n_desig += 1
            try:
                path = parse_designation(d)
            except ResolveError:
                refused += 1
                continue
            depth_hist[len(path)] += 1
            shipped = designation_state(text, d)["designation_exists"]
            nested = nested_aware_exists(text, d)
            row = {"item_id": it["item_id"], "label": it["label"],
                   "instruction_index": idx, "designation": d, "depth": len(path),
                   "operation": ins.get("operation"),
                   "shipped_designation_exists": shipped,
                   "nested_aware_exists": nested}
            if shipped is False and nested is True:
                shipped_false_nested_true.append(row)
                affected_items.add(it["item_id"])
            elif shipped is True and nested is False:
                shipped_true_nested_false.append(row)
                affected_items.add(it["item_id"])
            else:
                agree += 1

    lines = []
    w = lines.append
    w("=" * 78)
    w("cfr_resolve's NESTED-DESIGNATION CEILING - counted, not fixed")
    w("=" * 78)
    w("")
    w(f"  eval set   {EVALSET.relative_to(REPO).as_posix()}   {len(items)} items")
    w(f"  instructions                       {n_ins}")
    w(f"  ... carrying a designation         {n_desig}")
    w(f"  ... the resolver REFUSED to parse  {refused}   (not a guess; a refusal)")
    w("")
    w("  designation DEPTH - depth 1 is unaffected by construction, because a depth-1")
    w("  path has no parent to be written separately from:")
    for depth in sorted(depth_hist):
        marker = "" if depth == 1 else "   <- can hit the ceiling"
        w(f"    depth {depth}   {depth_hist[depth]:4d} instruction(s){marker}")
    deep = sum(v for k, v in depth_hist.items() if k >= 2)
    w(f"    depth >= 2 TOTAL   {deep}   ({deep / n_desig:.1%} of designations)")
    w("")
    w("-" * 78)
    w("THE DISAGREEMENT")
    w("-" * 78)
    w("")
    w(f"  the two readings AGREE on                          {agree} designations")
    w(f"  shipped says NOT PRESENT, nested-aware says PRESENT {len(shipped_false_nested_true)}"
      f"   <- FALSE DEFECTS")
    w(f"  shipped says PRESENT, nested-aware says NOT PRESENT {len(shipped_true_nested_false)}")
    w(f"  eval ITEMS touched by any disagreement              {len(affected_items)}"
      f" of {len(items)}   ({len(affected_items) / len(items):.1%})")
    w("")
    if not shipped_false_nested_true:
        w("  ZERO. The branch is printed as zero rather than omitted (hard rule 14).")
    else:
        by_label = Counter(r["label"] for r in shipped_false_nested_true)
        w(f"  those {len(shipped_false_nested_true)} disagreements by GOLD LABEL of their item: {dict(by_label)}")
        w("")
        w("  A disagreement on a WILL_EXECUTE item pushes A1 toward a FALSE DEFECT.")
        w("  A disagreement on a WILL_FAIL item may still land on the right verdict")
        w("  for the WRONG REASON, which the resolution_trace makes visible and an")
        w("  accuracy average would hide - CONTEXT.md section 5's whole argument.")
        w("")
        w("  first 12, in item order:")
        for r in sorted(shipped_false_nested_true,
                        key=lambda r: (r["item_id"], r["instruction_index"]))[:12]:
            w(f"    {r['item_id']:24s} #{r['instruction_index']:<2d} "
              f"{str(r['operation']):12s} {r['designation']:16s} depth {r['depth']}"
              f"   gold {r['label']}")
    w("")
    w("-" * 78)
    w("WHAT IS AND IS NOT BEING CLAIMED")
    w("-" * 78)
    w("")
    w("  IS:      the shipped cfr_resolve under-detects nested paragraph designations,")
    w("           on the count above, and that ceiling is inside A1's measured number.")
    w("  IS NOT:  that the nested-aware reading is correct. It is ONE reading of a")
    w("           hierarchy that flattened text only implies. Adopting a reading is a")
    w("           Class A change and it is the architect's - QUESTIONS.md Q21.")
    w("")
    w("  cfr_resolve is NOT modified by CH-06. It is outside the scope fence, CH-05 is")
    w("  gated and unreviewed, and - decisively - this defect was found BECAUSE it cost")
    w("  A1 a point. Changing a capability on that basis is tuning, whatever the")
    w("  engineering argument for it. The tool ships as committed at cb65539.")
    w("")
    text = "\n".join(lines) + "\n"
    print(text)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    (OUT.with_suffix(".json")).write_text(
        json.dumps({"shipped_false_nested_true": shipped_false_nested_true,
                    "shipped_true_nested_false": shipped_true_nested_false,
                    "depth_histogram": {str(k): v for k, v in sorted(depth_hist.items())},
                    "n_instructions": n_ins, "n_with_designation": n_desig,
                    "n_refused": refused, "n_agree": agree,
                    "affected_items": sorted(affected_items)},
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(f"  wrote {OUT.relative_to(REPO).as_posix()} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
