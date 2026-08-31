"""Generate CH-06's `AI-USE.md` session row FROM THE LEDGER, not from memory.

Hard rule 13 requires every model, tool and agent disclosed. Hard rule 14 requires every
number to ship its generating script. This is that script: the call counts, token totals
and USD in the emitted row are read out of `docs/evidence/runs/cost_ledger.csv` at write
time, so a transcription error is not possible.

Hard rule 15 is the reason it exists at all. Earlier in this same session I published a
duration I had estimated from a feeling rather than read from this ledger's own
`wall_clock_s` column, and had to retract it seven minutes later (`QUESTIONS.md` Q24).
Numbers that can be computed are computed.

    python docs/evidence/ch06-a1/aiuse_entry.py           # print
    python docs/evidence/ch06-a1/aiuse_entry.py --write   # splice into AI-USE.md
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LEDGER = REPO / "docs/evidence/runs/cost_ledger.csv"
AIUSE = REPO / "AI-USE.md"
MARKER = "## Session log\n\nNewest first. Every build session appends one row here **and** exports its transcript.\n"

# The arms this session created. Everything else in the ledger predates it.
CH06_ARMS = ("A1", "A1-iter1", "A1-minus-tool", "B0prime", "B0-agent-currenttext")


def read_ledger():
    with open(LEDGER, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rows = read_ledger()
    by_arm = defaultdict(lambda: {"n": 0, "in": 0, "out": 0, "usd": Decimal("0"),
                                  "wall": 0.0, "unknown": 0, "model": set()})
    by_model = defaultdict(lambda: {"n": 0, "usd": Decimal("0")})
    for r in rows:
        a = by_arm[r["arm"]]
        a["n"] += 1
        a["in"] += int(r["input_tokens"] or 0)
        a["out"] += int(r["output_tokens"] or 0)
        a["wall"] += float(r["wall_clock_s"] or 0)
        a["model"].add(r["model"])
        if (r["imputed_usd"] or "").strip():
            a["usd"] += Decimal(r["imputed_usd"])
        else:
            a["unknown"] += 1
    ch06 = [a for a in CH06_ARMS if a in by_arm]
    for r in rows:
        if r["arm"] in CH06_ARMS:
            m = by_model[r["model"]]
            m["n"] += 1
            if (r["imputed_usd"] or "").strip():
                m["usd"] += Decimal(r["imputed_usd"])

    total_all = sum((by_arm[a]["usd"] for a in by_arm), Decimal("0"))
    total_ch06 = sum((by_arm[a]["usd"] for a in ch06), Decimal("0"))
    unknown_all = sum(by_arm[a]["unknown"] for a in by_arm)

    L = []
    w = L.append
    w("### CH-06 → CH-08 → CH-09 · 2026-08-31 · Claude Code · `claude-opus-5` · "
      "BUILD, UNATTENDED · **THE ADVANCED SOLUTION**")
    w("")
    w("One unattended session working a pre-registered queue. It produced the project's")
    w("first advanced solution, without which the entry is invalid under the hackathon's")
    w("own rule that *\"every valid entry must present both a baseline solution and an")
    w("advanced solution.\"*")
    w("")
    w("**Models called by THIS session, all logged through `src/runlog.py`:**")
    w("")
    w("| id | calls | USD | why |")
    w("|---|---:|---:|---|")
    why = {
        "claude-haiku-4-5-20251001": ("every A1 arm and both ablations, temperature 0 — "
                                      "the same model as every baseline (`CONTEXT.md` §4)"),
    }
    for m in sorted(by_model):
        w(f"| `{m}` | {by_model[m]['n']:,} | {float(by_model[m]['usd']):.4f} | "
          f"{why.get(m, 'see the per-arm table below')} |")
    w("")
    w("**Arms run by this session, per-arm, from the ledger:**")
    w("")
    w("| arm | calls | input tok | output tok | USD | wall s | unknown-cost rows |")
    w("|---|---:|---:|---:|---:|---:|---:|")
    for a in ch06:
        d = by_arm[a]
        w(f"| `{a}` | {d['n']:,} | {d['in']:,} | {d['out']:,} | {float(d['usd']):.4f} | "
          f"{d['wall']:.0f} | {d['unknown']} |")
    w(f"| **this session** | | | | **{float(total_ch06):.4f}** | | |")
    w("")
    w("**Subagents: one.** An independent adversarial **CH-04 gate reviewer**, "
      "`claude-opus-5`, spawned with zero shared context and given only `CLAUDE.md`, "
      "`CONTEXT.md` §7, `plan.md`'s CH-04 card and the diff — explicitly *not* this")
    w("project's own account of its work. It returned **FAIL with 16 findings**, "
      "reimplemented the scorer from the specification prose alone, and mutation-tested "
      "`src/score.py` sixteen times, restoring it byte-for-byte after each. Its verdict "
      "is `docs/reviews/REVIEW_CH-04.md`; its probes are kept at "
      "`docs/reviews/ch04-probe/`. **Nothing it found was taken on trust** — finding F3 "
      "was independently checked against the repository before this session acted on it.")
    w("")
    w("**Tools the agent was given, and whether it used them.** `cfr_resolve` was "
      "exposed as a real Anthropic tool-use schema rather than pre-computed into the "
      "prompt, specifically so that *use* could be counted rather than assumed. It was "
      "called and the calls are in the trajectories. The measured "
      "availability-vs-use-vs-agreement gap is in `docs/evidence/ch06-a1/a1-result.txt`.")
    w("")
    w("**Human direction: none during the run.** The queue was fixed in "
      "`prompts/CH-06.md`, which is committed. Every ambiguity that arose was written to "
      "`QUESTIONS.md` (Q20–Q24) and the conservative option taken, rather than "
      "self-authorised — including **Q21**, a material defect in a shipped capability "
      "that this session declined to fix because the defect was discovered *through the "
      "fact that it cost the headline number a point*.")
    w("")
    w("**One published number was retracted by this session, seven minutes after it was "
      "published.** `QUESTIONS.md` **Q24** asserted a run duration that had been "
      "estimated from a sense of how much work had happened rather than read from the "
      "ledger's own `wall_clock_s` column. It was wrong by a factor of eight and the "
      "scheduling contingency built on it was unnecessary. The entry is kept unedited "
      "with the retraction beside it.")
    w("")
    w(f"**Cost: USD {float(total_ch06):.4f} for this session; USD {float(total_all):.4f} "
      f"committed in total against the 18.00 ceiling**, {len(rows):,} logged runs, "
      f"{unknown_all} of unknown cost carrying an empty cell rather than a zero.")
    w("")

    entry = "\n".join(L)
    if not args.write:
        print(entry)
        return 0

    text = AIUSE.read_text(encoding="utf-8")
    if MARKER not in text:
        print("ERROR: the Session log marker was not found verbatim in AI-USE.md; "
              "refusing to guess where to splice.", file=sys.stderr)
        return 2
    if "### CH-06 → CH-08 → CH-09" in text:
        # REPLACE the existing row rather than refuse. The ledger moved after this row
        # was first written - two arms were accidentally run twice, QUESTIONS.md Q26 -
        # and a DISCLOSURE row carrying a stale cost figure is worse than no row at all.
        # The old block is cut at the next "### " heading so nothing else is disturbed.
        start = text.index("### CH-06 → CH-08 → CH-09")
        nxt = text.find(chr(10) + "### ", start + 1)
        text = text[:start] + text[(nxt + 1 if nxt != -1 else len(text)):]
    out = text.replace(MARKER, MARKER + "\n" + entry, 1)
    AIUSE.write_text(out, encoding="utf-8", newline="\n")
    # hard rule 16
    back = AIUSE.read_text(encoding="utf-8")
    if "### CH-06 → CH-08 → CH-09" not in back or MARKER not in back:
        print("ERROR: the edit did not land as expected", file=sys.stderr)
        return 4
    print(f"  spliced {len(entry):,} chars into AI-USE.md directly under the Session log "
          f"heading; marker intact, no duplicate row")
    return 0


if __name__ == "__main__":
    sys.exit(main())
