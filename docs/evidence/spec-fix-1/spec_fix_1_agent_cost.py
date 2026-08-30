#!/usr/bin/env python3
"""SPEC-FIX-1 - measure the ADVERSARIAL PANEL's token usage, per agent.

Hard rule 10: *every* agent run is logged - trajectory, input tokens, output tokens,
wall-clock, imputed USD, no exceptions from the first run. `docs/evidence/ch00_session_cost.py`
measures the main coding session's own transcript and cannot see subagents, which live in
their own transcript directory. This script measures those, on the same pricing basis and
with the same two-figure convention (assumption-free upper bound printed beside the
cache-adjusted figure), so the panel is not an unlogged agent run.

The panel is disclosed in `AI-USE.md` and its verdicts are summarised in
`docs/evidence/spec-fix-1/verdict.md`. No panel number was used in the verdict without
being rebuilt in-repo first (hard rule 15).

Usage:
  python docs/evidence/spec-fix-1/spec_fix_1_agent_cost.py --dir <workflow transcript dir>

The transcript directory is outside the repository and is not redistributed - the same
treatment `QUESTIONS.md` Q3 records for `context/01-PROBLEM-PDF.md`. Pass `--dir` to
reproduce; the committed output beside this file is what the run printed.
"""
import argparse
import glob
import io
import json
import os
import sys
from decimal import Decimal

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")

IN_PRICE = Decimal("5.00")          # USD per 1M input tokens   - same basis as CH-00
OUT_PRICE = Decimal("25.00")        # USD per 1M output tokens
CACHE_WRITE_MULT = Decimal("1.25")  # ASSUMED, not re-verified this session
CACHE_READ_MULT = Decimal("0.10")   # ASSUMED, not re-verified this session


def tally(path):
    tot = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0, "turns": 0}
    models = set()
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get("message") or {}
            usage = msg.get("usage") or rec.get("usage") or {}
            if not usage:
                continue
            if msg.get("model"):
                models.add(msg["model"])
            tot["turns"] += 1
            tot["input"] += usage.get("input_tokens", 0)
            tot["output"] += usage.get("output_tokens", 0)
            tot["cache_creation"] += usage.get("cache_creation_input_tokens", 0)
            tot["cache_read"] += usage.get("cache_read_input_tokens", 0)
    return tot, models


# The on-disk `agent-*.meta.json` carries only {"agentType","spawnDepth"} - no role
# label - so the id-to-role map is transcribed here from the workflow run's own progress
# report (run wf_5260a72c-01a). It is a label for reading, never an input to a number.
ROLES = {
    "a3f40b42c5de13421": "recount:regex",
    "ab76f8ca2e403bc3f": "recount:fields",
    "a1680dbe5c2efd2f2": "recount:sampling",
    "a686c376eb91b9dbd": "judge:prosecutor",
    "a20579560e69281c9": "judge:defender",
    "a392306c8ebb302b4": "judge:counterfactual",
    "a465b4c2992bc8eae": "judge:gate-integrity",
    "a76e68167419eef98": "judge:process",
    "a18020fd602cefea2": "harder:per-doc",
    "a2976400489c6f594": "harder:correctness",
}


def label_for(path):
    agent_id = os.path.basename(path)[len("agent-"):-len(".jsonl")]
    return ROLES.get(agent_id, agent_id)


def usd(tot):
    total_in = tot["input"] + tot["cache_creation"] + tot["cache_read"]
    upper = (Decimal(total_in) / 1_000_000 * IN_PRICE
             + Decimal(tot["output"]) / 1_000_000 * OUT_PRICE)
    adj = (Decimal(tot["input"]) / 1_000_000 * IN_PRICE
           + Decimal(tot["cache_creation"]) / 1_000_000 * IN_PRICE * CACHE_WRITE_MULT
           + Decimal(tot["cache_read"]) / 1_000_000 * IN_PRICE * CACHE_READ_MULT
           + Decimal(tot["output"]) / 1_000_000 * OUT_PRICE)
    return total_in, upper, adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True,
                    help="workflow transcript directory holding agent-*.jsonl")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "agent-*.jsonl")))
    print("=" * 78)
    print("SPEC-FIX-1 ADVERSARIAL PANEL COST - measured per agent (hard rule 10)")
    print("=" * 78)
    print("transcript dir : %s" % args.dir)
    print("agent runs     : %d" % len(files))
    if not files:
        print("ZERO agent transcripts found. Printed as a zero rather than omitted")
        print("(hard rule 14); a zero here means the directory is wrong, not that no")
        print("agent ran - the panel is disclosed in AI-USE.md either way.")
        return
    print()

    grand = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0, "turns": 0}
    allmodels = set()
    print("   %-22s %6s %10s %12s %14s" % ("agent", "turns", "output", "total input",
                                           "USD upper"))
    rows = []
    for f in files:
        tot, models = tally(f)
        allmodels |= models
        for k in grand:
            grand[k] += tot[k]
        total_in, upper, _ = usd(tot)
        rows.append((label_for(f), tot, total_in, upper))
    for label, tot, total_in, upper in sorted(rows, key=lambda r: -r[3]):
        print("   %-22s %6d %10s %12s %14s"
              % (label[:22], tot["turns"], "{:,}".format(tot["output"]),
                 "{:,}".format(total_in), "%.6f" % upper))
    print()

    total_in, upper, adj = usd(grand)
    print("   %-22s %6d %10s %12s %14s"
          % ("TOTAL", grand["turns"], "{:,}".format(grand["output"]),
             "{:,}".format(total_in), "%.6f" % upper))
    print()
    print("models         : %s" % (", ".join(sorted(allmodels)) or "(none recorded)"))
    print()
    print("output tokens         : %12s" % "{:,}".format(grand["output"]))
    print("input, uncached       : %12s" % "{:,}".format(grand["input"]))
    print("input, cache write    : %12s" % "{:,}".format(grand["cache_creation"]))
    print("input, cache read     : %12s" % "{:,}".format(grand["cache_read"]))
    print("TOTAL INPUT           : %12s" % "{:,}".format(total_in))
    print()
    print("IMPUTED COST (flat-cost subscription - imputed, never reported as $0)")
    print("  upper bound, no cache discount        USD %.6f" % upper)
    print("  cache-adjusted (1.25x / 0.10x)        USD %.6f" % adj)
    print()
    print("  The cache multipliers are ASSUMED and were not re-verified against the")
    print("  published table in this session. The upper bound rests on no assumption")
    print("  at all, which is why both are printed. Hard rule 15.")
    print()
    print("  This is the PANEL only. The main coding session is measured separately by")
    print("  docs/evidence/ch00_session_cost.py, which cannot see subagent transcripts;")
    print("  AI-USE.md carries both and their sum, so neither is quoted alone.")
    print()
    print("  Not charged against the USD 18 ceiling in src/runlog.py - that ceiling")
    print("  governs the paid API used by the evaluation arms (QUESTIONS.md Q1).")
    print("=" * 78)


if __name__ == "__main__":
    main()
