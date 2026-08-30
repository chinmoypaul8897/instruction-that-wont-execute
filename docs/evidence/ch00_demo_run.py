"""CH-00 done-when: a dummy agent run emitting a readable trajectory AND a cost row.

Run: python docs/evidence/ch00_demo_run.py

Writes into docs/evidence/runs/ch00-demo/ -- a SANDBOX. The production ledger at
docs/evidence/runs/cost_ledger.csv is deliberately left absent until the first
real run, because seeding it with demo rows would corrupt the cumulative total
the USD 18 spend ceiling is computed from.

The clock and the UTC stamp are injected, so this artifact is byte-reproducible
(hard rule 9). Re-running it must produce an identical trajectory; the script
asserts that against the committed copy if one exists.

No model is called. The token counts are stand-ins for a real API response's
usage figures, and the money is computed from them exactly as it will be in
anger.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from runlog import RunLogger, compute_usd  # noqa: E402

DEMO_DIR = REPO / "docs" / "evidence" / "runs" / "ch00-demo"
TRAJ_DIR = DEMO_DIR / "trajectories"
LEDGER = DEMO_DIR / "cost_ledger.csv"

# Stand-ins for a real response's usage block.
INPUT_TOKENS = 18_432
OUTPUT_TOKENS = 1_207
MODEL = "claude-haiku-4-5"
DELIVERY = "batch"          # QUESTIONS.md Q1 mandates the Message Batches API

# Hand-computed, the same way docs/evidence/ch00-goldens.md does it:
#   18_432 / 1e6 * 1.00 = 0.018432
#    1_207 / 1e6 * 5.00 = 0.006035
#                  sum  = 0.024467
#   batch  x 0.5        = 0.0122335  -> 6 dp ROUND_HALF_UP -> 0.012234
EXPECTED_USD = Decimal("0.012234")

AGENT_INSTRUCTIONS = (
    "You are the B0-agent arm. Given a Federal Register amendatory instruction and "
    "the CFR section text as it stood on the publication date, predict whether the "
    "Office of the Federal Register can EXECUTE the instruction. Emit the editorial "
    "note NARA would publish if it cannot. Report the normalisation level at which "
    "any quoted anchor was matched: exact / whitespace-collapsed / alphanumeric-only."
)


class FrozenClock:
    def __init__(self, *ticks):
        self.ticks = list(ticks)
        self.last = ticks[-1]

    def __call__(self):
        if self.ticks:
            self.last = self.ticks.pop(0)
        return self.last


def frozen_utc():
    return datetime(2026, 8, 30, 12, 0, 0, tzinfo=timezone.utc)


def main() -> int:
    for stale in (TRAJ_DIR / "CH-00-demo.jsonl", LEDGER):
        if stale.exists():
            stale.unlink()          # rebuild from scratch so the assert is real
    TRAJ_DIR.mkdir(parents=True, exist_ok=True)

    with RunLogger(
        arm="B0-agent",
        item_id="40-433.2",
        model=MODEL,
        delivery=DELIVERY,
        agent_instructions=AGENT_INSTRUCTIONS,
        run_id="CH-00-demo",
        traj_dir=TRAJ_DIR,
        ledger_path=LEDGER,
        _clock=FrozenClock(1000.0, 1004.219),
        _utc=frozen_utc,
    ) as log:
        log.action("tool_call", name="cfr_resolve",
                   input={"section": "40 CFR 433.2", "designation": "(b)(4)(i)(A)",
                          "anchor": "pretreatment standards for existing sources"})
        log.tool_response(name="cfr_resolve",
                          output={"level_attempted": "exact", "found": False,
                                  "designations_present": ["(a)", "(b)(1)", "(b)(2)"]})
        log.feedback("no (b)(4) exists at the as-of date; the instruction assumes a "
                     "paragraph the section does not have, so the next step tests "
                     "whether the anchor matches anywhere under a looser level")
        log.retry(reason="exact anchor match failed at (b)(4)(i)(A)", attempt=2)
        log.action("tool_call", name="cfr_resolve",
                   input={"section": "40 CFR 433.2", "level": "whitespace-collapsed"})
        log.tool_response(name="cfr_resolve", output=None,
                          error="anchor absent at every declared level")
        log.human_checkpoint(
            reason="two sibling sections carry a near-identical anchor; "
                   "an automated pick here would be a guess",
            resolution="operator confirmed 433.2, not 433.11")
        log.action("message", name="assistant",
                   input={"verdict": "WILL_FAIL",
                          "note": "This amendment could not be incorporated due to "
                                  "inaccurate amendatory instruction."})
        usd = log.finish(verdict="WILL_FAIL",
                         input_tokens=INPUT_TOKENS, output_tokens=OUTPUT_TOKENS)

    print("CH-00 DEMO RUN - dummy agent run, no model called")
    print("=" * 74)
    print(f"trajectory : {log.trajectory_path.relative_to(REPO)}")
    print(f"ledger     : {LEDGER.relative_to(REPO)}")
    print()

    lines = Path(log.trajectory_path).read_text(encoding="utf-8").splitlines()
    print(f"TRAJECTORY - {len(lines)} records, one JSON object per line")
    print("-" * 74)
    for line in lines:
        rec = json.loads(line)
        tag = rec["record"]
        step = rec.get("step")
        head = f"  {('step %d' % step) if step else '      ':<8} {tag:<16}"
        if tag == "run_start":
            print(head + f"{rec['arm']} / {rec['item_id']} / {rec['model']} / {rec['delivery']}")
            print(f"  {'':<8} {'':<16}agent_instructions: {len(rec['agent_instructions'])} chars")
        elif tag == "run_end":
            print(head + f"verdict={rec['verdict']}  in={rec['input_tokens']:,} "
                         f"out={rec['output_tokens']:,}  {rec['wall_clock_s']}s  "
                         f"USD {rec['imputed_usd_exact']}")
        elif tag == "feedback":
            print(head + rec["what_changed_the_next_step"][:44] + "...")
        else:
            print(head + str(rec.get("name") or rec.get("reason") or "")[:44])
    print()

    print("COST LEDGER ROW")
    print("-" * 74)
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        print("  " + line)
    print()

    recomputed = compute_usd(MODEL, INPUT_TOKENS, OUTPUT_TOKENS, DELIVERY)
    print("CHECKS")
    print("-" * 74)
    checks = [
        ("every line parses as JSON", all(json.loads(l) for l in lines)),
        ("run_start first, run_end last",
         json.loads(lines[0])["record"] == "run_start"
         and json.loads(lines[-1])["record"] == "run_end"),
        ("hand-computed USD matches", recomputed == EXPECTED_USD == usd),
        ("cost row carries input tokens", str(INPUT_TOKENS) in LEDGER.read_text(encoding="utf-8")),
        ("cost row carries output tokens", str(OUTPUT_TOKENS) in LEDGER.read_text(encoding="utf-8")),
        ("cost row carries wall-clock", "4.219" in LEDGER.read_text(encoding="utf-8")),
        ("cost row carries imputed USD", "0.012234" in LEDGER.read_text(encoding="utf-8")),
        ("imputed USD > 0 (never $0)", usd > 0),
        ("production ledger untouched",
         not (REPO / "docs" / "evidence" / "runs" / "cost_ledger.csv").exists()),
    ]
    for name, ok in checks:
        print(f"  {'PASS' if ok else '*** FAIL ***':<14}{name}")
    n_ok = sum(1 for _, ok in checks if ok)
    print(f"\n  {n_ok}/{len(checks)} checks passed   "
          f"(success + failure == n: {n_ok + (len(checks) - n_ok) == len(checks)})")
    print(f"\n  hand-computed  USD {EXPECTED_USD}")
    print(f"  logger emitted USD {usd}")
    return 0 if n_ok == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
