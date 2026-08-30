"""Measure a Claude Code build session's token usage from its own transcript.

Run: python docs/evidence/ch00_session_cost.py [--session-id <uuid>]

Hard rule 14 - any claim from data ships its generating script AND its committed
output. This is the generating script for the usage table in AI-USE.md.

The numbers are read from the `usage` records the transcript already contains.
They are measured, not estimated from character counts.

The build subscription is flat-cost to the operator, so the dollar figure is an
IMPUTATION and is labelled one. Two bases are printed:

  upper bound    every input token at full list price, no cache discount.
                 Needs no assumption and cannot be an under-report.
  cache-adjusted cache writes at 1.25x and cache reads at 0.10x the input list
                 price. Closer to a real bill, but it rests on multipliers that
                 were NOT re-verified against the published table -- so it is
                 printed beside the upper bound, never instead of it.

Never emits $0.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from decimal import ROUND_HALF_UP, Decimal

USD = Decimal("0.000001")
SESSION_DIR = os.path.expanduser(
    "~/.claude/projects/c--Users-chinm-micro1-engineering-challenge")

# claude-opus-5 published list, USD per 1M tokens.
# https://docs.claude.com/en/docs/about-claude/pricing
IN_PRICE = Decimal("5.00")
OUT_PRICE = Decimal("25.00")
CACHE_WRITE_MULT = Decimal("1.25")   # ASSUMED - not re-verified this session
CACHE_READ_MULT = Decimal("0.10")    # ASSUMED - not re-verified this session


def measure(path):
    tot = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0}
    turns = 0
    models = set()
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message") or {}
        usage = msg.get("usage") or rec.get("usage") or {}
        if not usage:
            continue
        turns += 1
        if msg.get("model"):
            models.add(msg["model"])
        tot["input"] += usage.get("input_tokens", 0)
        tot["output"] += usage.get("output_tokens", 0)
        tot["cache_creation"] += usage.get("cache_creation_input_tokens", 0)
        tot["cache_read"] += usage.get("cache_read_input_tokens", 0)
    return turns, models, tot


def q(d):
    return d.quantize(USD, rounding=ROUND_HALF_UP)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-id")
    args = ap.parse_args()

    if args.session_id:
        path = os.path.join(SESSION_DIR, f"{args.session_id}.jsonl")
    else:
        files = sorted(glob.glob(os.path.join(SESSION_DIR, "*.jsonl")),
                       key=os.path.getmtime)
        if not files:
            raise SystemExit(f"no transcripts under {SESSION_DIR}")
        path = files[-1]

    turns, models, tot = measure(path)
    total_in = tot["input"] + tot["cache_creation"] + tot["cache_read"]

    print("CH-00 BUILD SESSION COST - measured from the session transcript")
    print("=" * 70)
    print(f"transcript          : {os.path.basename(path)}")
    print(f"assistant turns     : {turns}")
    print(f"models              : {', '.join(sorted(models)) or 'unknown'}")
    print()
    print(f"{'output tokens':<22}: {tot['output']:>12,}")
    print(f"{'input, uncached':<22}: {tot['input']:>12,}")
    print(f"{'input, cache write':<22}: {tot['cache_creation']:>12,}")
    print(f"{'input, cache read':<22}: {tot['cache_read']:>12,}")
    print(f"{'TOTAL INPUT':<22}: {total_in:>12,}")
    print()

    upper = (Decimal(total_in) / 1_000_000 * IN_PRICE
             + Decimal(tot["output"]) / 1_000_000 * OUT_PRICE)
    adjusted = (
        Decimal(tot["input"]) / 1_000_000 * IN_PRICE
        + Decimal(tot["cache_creation"]) / 1_000_000 * IN_PRICE * CACHE_WRITE_MULT
        + Decimal(tot["cache_read"]) / 1_000_000 * IN_PRICE * CACHE_READ_MULT
        + Decimal(tot["output"]) / 1_000_000 * OUT_PRICE)

    print("IMPUTED COST (flat-cost subscription - imputed, never reported as $0)")
    print(f"  upper bound, no cache discount        USD {q(upper)}")
    print(f"  cache-adjusted (1.25x / 0.10x)        USD {q(adjusted)}")
    print()
    print("  The cache multipliers are ASSUMED and were not re-verified against the")
    print("  published table in this session. The upper bound rests on no assumption")
    print("  at all, which is why both are printed. Hard rule 15.")
    print()
    print("  This session's spend is NOT charged against the USD 18 ceiling in")
    print("  src/runlog.py. That ceiling governs the paid API used by the evaluation")
    print("  arms (QUESTIONS.md Q1). Conflating the two would misstate both.")
    assert upper > 0 and adjusted > 0, "never emit $0"


if __name__ == "__main__":
    main()
