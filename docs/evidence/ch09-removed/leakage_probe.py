"""CH-09 — **REMOVED EXPERIMENT 1: the current-CFR-text leakage probe.**

`CONTEXT.md` §10, verbatim, pre-registered before it ran:

    "Current CFR text instead of point-in-time text. Pre-registered prediction,
     committed before it runs: accuracy collapses toward a trivial oracle, because
     after a failed amendment the current text still lacks the change and after a
     successful one it contains it - the current text LEAKS THE LABEL. If the number
     goes up, that is PROOF OF LEAKAGE, NOT CAPABILITY, and must be reported as such."

    stage 1:  python docs/evidence/ch09-removed/leakage_probe.py extract
    stage 2:  python docs/evidence/ch09-removed/leakage_probe.py run       # costs money
    stage 3:  python docs/evidence/ch09-removed/leakage_probe.py analyse

WHY THIS IS A REMOVED EXPERIMENT AND NOT A RESULT
--------------------------------------------------
This arm is **not** a better version of `B0-agent`. It is the same arm given evidence it
must not have. It is run, published, and **excluded from every headline**, because an
experiment that is removed *with its number* is worth more than one that is quietly not
attempted. **A rise here is the finding.**

FAIRNESS - THE PROBE IS ONLY HONEST IF THE TEXT IS PREPARED IDENTICALLY
-----------------------------------------------------------------------
The current text goes through **exactly** the pipeline the frozen point-in-time text
went through in `src/eval_set.py`: find-the-section → `strip_leakage` → `section_text`, with
`strip_leakage` and `section_text` reused UNMODIFIED from `src/cfr_pit.py`.

That matters more than it looks. `strip_leakage` removes `EDNOTE`, `EFFDNOTP`, `CITA`
and `EAR` — including **the very editorial note that defines this item's gold label**.
Without it the probe would measure *"we handed the agent the answer key"*, which is
trivially true and completely uninteresting. With it, any rise is attributable to the
**amendment state of the text itself**: after a failed amendment the current text still
lacks the change; after a successful one it contains it.

**So this probe measures structural leakage, not a note left lying around.** The strip
counts are published per item so the claim is checkable.

PURITY: no network. The eCFR snapshot in `data/raw/ecfr/` is a frozen local corpus and
`data/` is read-only (hard rule 11). Stage 2 is the only stage that calls the API and
every call goes through `RunLogger` (hard rule 10).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from apiclient import ApiError, call_messages, load_api_key  # noqa: E402
from arms import ARMS, MAX_TOKENS, user_prompt                # noqa: E402
from cfr_pit import (  # noqa: E402
    REPRINT_ANCESTORS, _parent_map, section_text, strip_leakage,
)
from runlog import RunLogger, SpendCeilingExceeded             # noqa: E402
from score import mcnemar, normalise_verdict, score            # noqa: E402

HERE = Path(__file__).resolve().parent
EVALSET = REPO / "data/evalset/items.jsonl"
ECFR = REPO / "data/raw/ecfr"
CHECKPOINT = REPO / "docs/evidence/checkpoint"
TRAJ = REPO / "docs/trajectories/arms/per-item"
LEDGER = REPO / "docs/evidence/runs/cost_ledger.csv"
CURRENT = HERE / "current-text.jsonl"
RUN = HERE / "B0-agent-currenttext-rep1.json"
HAIKU = "claude-haiku-4-5-20251001"

_roots: dict[str, ET.Element] = {}


# --------------------------------------------------------------------------
# THE eCFR ADAPTER - written HERE, not in `src/cfr_pit.py`
# --------------------------------------------------------------------------
# The two corpora do not share a schema, and this is the whole reason the probe
# needed writing rather than configuring:
#
#   annual edition   <SECTION><SECTNO>§ 75.31</SECTNO><SUBJECT>...</SUBJECT>...
#   eCFR snapshot    <DIV8 N="§ 75.31" TYPE="SECTION"><HEAD>§ 75.31 ...</HEAD>...
#
# `cfr_pit.find_section` reads `<SECTNO>`, which the eCFR files simply do not have -
# which is why the first extraction run returned 0 of 82 and why that count is
# reported here rather than quietly fixed. `section_text` and `strip_leakage` ARE
# schema-generic and are reused UNMODIFIED, so both corpora go through byte-identical
# text preparation. `src/cfr_pit.py` is not touched: it is CH-03's, it is frozen, and
# an adapter for a removed experiment has no business inside a shipped module.
_SECT_TOKEN = re.compile(r"\d+[A-Za-z]?\.[0-9A-Za-z][0-9A-Za-z.\-]*")


def ecfr_find_section(root: ET.Element, section: str) -> tuple[ET.Element | None, int]:
    """The eCFR equivalent of `cfr_pit.find_section`. Same contract, same reprint rule.

    Returns the FIRST eligible match and the total count, so an ambiguity is reported
    rather than silently resolved.
    """
    parents = _parent_map(root)
    hits = []
    for d in root.iter("DIV8"):
        if d.get("TYPE") != "SECTION":
            continue
        m = _SECT_TOKEN.search(d.get("N") or "")
        if not m or m.group(0).rstrip(".") != section:
            continue
        node, reprint = d, False
        while node in parents:
            node = parents[node]
            if node.tag in REPRINT_ANCESTORS:
                reprint = True
                break
        if not reprint:
            hits.append(d)
    return (hits[0] if hits else None), len(hits)


def load_items():
    return sorted((json.loads(l) for l in EVALSET.read_text(encoding="utf-8").splitlines()
                   if l.strip()), key=lambda i: i["item_id"])


def root_for(title: str) -> ET.Element | None:
    if title not in _roots:
        path = ECFR / f"ECFR-title{title}.xml"
        if not path.exists():
            return None
        _roots[title] = ET.parse(path).getroot()
    return _roots[title]


def extract() -> int:
    """Stage 1 — pull each item's CURRENT section text. No network, no API, free."""
    items = load_items()
    rows, missing = [], []
    for it in items:
        root = root_for(it["cfr_title"])
        if root is None:
            missing.append((it["item_id"], "no eCFR file for the title"))
            continue
        sec, n = ecfr_find_section(root, it["section"])
        if sec is None:
            # A section absent from the CURRENT CFR is itself informative: it was
            # removed at some point after the rule. Recorded, not silently dropped.
            missing.append((it["item_id"], f"section not in the current CFR (n={n})"))
            continue
        stripped, counts = strip_leakage(sec)
        rows.append({
            "item_id": it["item_id"], "label": it["label"],
            "cfr_title": it["cfr_title"], "section": it["section"],
            "current_text": section_text(stripped),
            "strip_counts": counts,
            "chars_current": len(section_text(stripped)),
            "chars_point_in_time": len(it["section_text"]),
            "duplicate_sectno_matches": n,
        })
    CURRENT.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
                       encoding="utf-8", newline="\n")
    print(f"  extracted {len(rows)} of {len(items)} items -> "
          f"{CURRENT.relative_to(REPO).as_posix()}")
    print(f"  MISSING {len(missing)}:")
    for m in missing[:20]:
        print(f"    {m[0]:26s} {m[1]}")
    if rows:
        dc = sum(r["chars_current"] for r in rows)
        dp = sum(r["chars_point_in_time"] for r in rows)
        print(f"  chars: current {dc:,}  point-in-time {dp:,}  ratio {dc / dp:.2f}x")
        sc = Counter()
        for r in rows:
            for k, v in r["strip_counts"].items():
                sc[k] += v
        print(f"  leakage elements stripped from the CURRENT text: {dict(sc)}")
        print("  (the gold-label-defining EDNOTE is stripped here exactly as it is from")
        print("   the point-in-time text, so any rise is STRUCTURAL leakage, not a note)")
    (HERE / "extract-report.json").write_text(
        json.dumps({"extracted": len(rows), "n_items": len(items),
                    "missing": [{"item_id": a, "reason": b} for a, b in missing]},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


def run() -> int:
    """Stage 2 — B0-agent's prompt, with the CURRENT text swapped in. Costs money."""
    if not CURRENT.exists():
        print("  run `extract` first")
        return 2
    items = {i["item_id"]: i for i in load_items()}
    rows = [json.loads(l) for l in CURRENT.read_text(encoding="utf-8").splitlines() if l.strip()]
    spec = ARMS["B0-agent"]
    key = load_api_key()
    preds, errors = {}, []
    usage = {"in": 0, "out": 0}
    for r in rows:
        it = dict(items[r["item_id"]])
        it["section_text"] = r["current_text"]          # THE ONLY CHANGE
        it["as_of_edition"] = "CURRENT eCFR snapshot"
        it["as_of_revision_date"] = "current"
        prompt = user_prompt(it, spec["gets_text"])
        run_id = ("B0agentCURRENT__"
                  + r["item_id"].replace("|", "_").replace("/", "_") + "__rep1")
        try:
            with RunLogger(arm="B0-agent-currenttext", item_id=r["item_id"],
                           model=HAIKU, agent_instructions=spec["system"],
                           delivery="standard", est_usd="0.02", run_id=run_id,
                           traj_dir=TRAJ, ledger_path=LEDGER) as log:
                log.action("message", "messages.create",
                           input={"model": HAIKU, "temperature": 0.0,
                                  "max_tokens": MAX_TOKENS,
                                  "REMOVED_EXPERIMENT": "current CFR text, not "
                                                        "point-in-time - CONTEXT.md §10",
                                  "user_prompt_chars": len(prompt),
                                  "user_prompt": prompt})
                try:
                    text, u, _ = call_messages(key, model=HAIKU, user=prompt,
                                               system=spec["system"],
                                               max_tokens=MAX_TOKENS, temperature=0.0)
                except ApiError as exc:
                    log.tool_response("messages.create", error=str(exc))
                    errors.append({"item_id": r["item_id"], "error": str(exc)[:200]})
                    continue
                log.tool_response("messages.create", output={"text": text})
                preds[r["item_id"]] = text.strip()
                usage["in"] += u["input_tokens"]
                usage["out"] += u["output_tokens"]
                log.finish(verdict=text.strip()[:32], input_tokens=u["input_tokens"],
                           output_tokens=u["output_tokens"])
        except SpendCeilingExceeded:
            raise
    RUN.write_text(json.dumps({"arm": "B0-agent-currenttext", "model": HAIKU, "rep": 1,
                               "predictions": preds, "errors": errors, "usage": usage,
                               "n_items": len(rows), "n_predicted": len(preds)},
                              indent=2, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"  predicted {len(preds)}/{len(rows)}  in={usage['in']:,} out={usage['out']:,}"
          f"  errors={len(errors)}")
    return 0


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


def analyse() -> int:
    """Stage 3 — the comparison, on the SUBSET both arms answered. Free."""
    rows = [json.loads(l) for l in CURRENT.read_text(encoding="utf-8").splitlines() if l.strip()]
    run_obj = json.loads(RUN.read_text(encoding="utf-8"))
    cur = run_obj["predictions"]
    base = majority([json.loads((CHECKPOINT / f"B0-agent-rep{r}.json").read_text(encoding="utf-8"))["predictions"]
                     for r in (1, 2, 3)])
    all_items = {i["item_id"]: i for i in load_items()}
    # THE SAME ITEMS FOR BOTH ARMS. Comparing an 82-item arm with a 76-item arm and
    # calling the difference an effect is exactly the error this project exists to name.
    subset = sorted((all_items[r["item_id"]] for r in rows), key=lambda i: i["item_id"])

    res_cur = score(subset, cur)
    res_pit = score(subset, base)
    va = [normalise_verdict(cur.get(i["item_id"])) == i["label"] for i in subset]
    vb = [normalise_verdict(base.get(i["item_id"])) == i["label"] for i in subset]
    mc = mcnemar(va, vb)
    gap = 100 * (res_cur["accuracy"] - res_pit["accuracy"])

    L = []
    w = L.append
    w("=" * 78)
    w("REMOVED EXPERIMENT 1 - CURRENT CFR TEXT INSTEAD OF POINT-IN-TIME")
    w("=" * 78)
    w("")
    w("  PRE-REGISTERED PREDICTION - CONTEXT.md section 10, written before the corpus")
    w("  was built and quoted here verbatim:")
    w("")
    w("    \"accuracy collapses toward a trivial oracle, because after a failed")
    w("     amendment the current text still lacks the change and after a successful")
    w("     one it contains it - the current text LEAKS THE LABEL. If the number goes")
    w("     up, that is PROOF OF LEAKAGE, NOT CAPABILITY, and must be reported as")
    w("     such.\"")
    w("")
    w(f"  items compared            {len(subset)} of 82   (the SAME items for both arms)")
    w(f"  items with no current section  {82 - len(subset)}   see extract-report.json")
    w("")
    w("  Both arms get text prepared by the IDENTICAL pipeline:")
    w("  find_section -> strip_leakage -> section_text. The EDNOTE that DEFINES the")
    w("  gold label is stripped from the current text too, so a rise here cannot be")
    w("  'we showed it the answer key' - it is structural leakage in the text itself.")
    w("")
    w("-" * 78)
    w(f"  point-in-time (B0-agent)   {res_pit['accuracy']:.4f}"
      f"   ({res_pit['success']}/{res_pit['n']})")
    w(f"  CURRENT text               {res_cur['accuracy']:.4f}"
      f"   ({res_cur['success']}/{res_cur['n']})")
    w(f"  difference                 {gap:+.1f} pp")
    w(f"  McNemar exact two-sided    p = {mc['p_value']:.4f}"
      f"   (b={mc['b_only_a_correct']} c={mc['c_only_b_correct']}"
      f" discordant={mc['n_discordant']})")
    w("-" * 78)
    w("")
    w(f"  false-defect  {res_pit['false_defect_rate']:.4f} -> {res_cur['false_defect_rate']:.4f}")
    w(f"  missed-defect {res_pit['missed_defect_rate']:.4f} -> {res_cur['missed_defect_rate']:.4f}")
    w("")
    if gap > 0:
        w("  *** THE NUMBER WENT UP. BY THE PRE-REGISTERED RULE THIS IS PROOF OF")
        w("      LEAKAGE, NOT CAPABILITY, AND IT IS REPORTED AS SUCH. ***")
        w("")
        w("  This arm is EXCLUDED from every headline and every results table except")
        w("  the removed-experiments row. It is not a better agent. It is the same")
        w("  agent holding evidence it must not have, and the rise is the measurement")
        w("  of how much that evidence is worth - which is precisely why the corpus")
        w("  was built point-in-time at CH-03 at considerable cost.")
    elif gap < 0:
        w("  The number went DOWN. The pre-registered prediction anticipated a rise;")
        w("  it did not happen, and the prediction is recorded as MISSED rather than")
        w("  reinterpreted. A drop is still consistent with the current text being")
        w("  the wrong evidence - it is simply not the leakage direction.")
    else:
        w("  No change. Reported as the zero it is (hard rule 14).")
    w("")
    w("  EITHER WAY THE POINT-IN-TIME CORPUS IS VINDICATED AS A DESIGN CHOICE: this")
    w("  is the experiment that shows what it would have cost to skip it.")
    w("")
    text = "\n".join(L) + "\n"
    print(text)
    (HERE / "leakage-result.txt").write_text(text, encoding="utf-8", newline="\n")
    (HERE / "leakage-result.json").write_text(
        json.dumps({"n_compared": len(subset), "accuracy_point_in_time": res_pit["accuracy"],
                    "accuracy_current_text": res_cur["accuracy"], "gap_pp": gap,
                    "mcnemar": mc,
                    "false_defect": [res_pit["false_defect_rate"], res_cur["false_defect_rate"]],
                    "missed_defect": [res_pit["missed_defect_rate"], res_cur["missed_defect_rate"]]},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stage", choices=["extract", "run", "analyse"])
    a = ap.parse_args(argv)
    return {"extract": extract, "run": run, "analyse": analyse}[a.stage]()


if __name__ == "__main__":
    sys.exit(main())
