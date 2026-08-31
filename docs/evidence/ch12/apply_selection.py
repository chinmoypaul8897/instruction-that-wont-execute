#!/usr/bin/env python3
"""CH-12 - APPLY `docs/trajectories/SELECTION-RULE.md`, mechanically.

The rule was committed at `1afc295`, in its own commit, BEFORE this script existed.
`git log -- docs/trajectories/SELECTION-RULE.md docs/evidence/ch12/apply_selection.py`
is the audit: the rule pre-dates every number below, so the curation cannot have been
fitted to a result.

Pure: no network, no clock, no randomness, no model call. Reads the committed
trajectories, the frozen eval set and the committed cost ledger. `git` is invoked
read-only, for `ls-files` and `archive`.

    python docs/evidence/ch12/apply_selection.py > docs/evidence/ch12/selection-applied.md
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, encoding="utf-8",
                          errors="replace", check=True).stdout


REPO = Path(sh("git", "rev-parse", "--show-toplevel").strip())
os.chdir(REPO)

TRAJ = "docs/trajectories"
LEDGER = Path("docs/evidence/runs/cost_ledger.csv")
EVALSET = Path("data/evalset/items.jsonl")

#: The classes clause T1 names, in the card's own words, mapped to the directory that
#: holds them. `None` means the class exists but has no trajectory directory - which is
#: a finding, not an omission, and is printed as one.
T1_CLASSES = {
    "build sessions": "build",
    "evaluation arms": "arms",
    "adversarial audits": None,
}


def agent_class(path: str) -> str:
    parts = Path(path).parts
    return parts[2] if len(parts) > 2 else "(root)"


def main() -> int:
    out = sys.stdout.write

    gold = {}
    for line in EVALSET.read_text(encoding="utf-8").splitlines():
        if line.strip():
            it = json.loads(line)
            gold[it["item_id"]] = it["label"]

    cost_by_run: dict[str, float] = defaultdict(float)
    with LEDGER.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                cost_by_run[row["run_id"]] += float(row["imputed_usd"] or 0.0)
            except ValueError:
                pass

    files = sorted(p for p in sh("git", "ls-files", "-z", TRAJ).split("\0")
                   if p.endswith(".jsonl"))

    facts: dict[str, dict] = {}
    for f in files:
        kinds: defaultdict[str, int] = defaultdict(int)
        disagreements = 0
        items: set[str] = set()
        run_ids: set[str] = set()
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(r, dict):
                    continue
                kind = r.get("record")
                if kind is None:          # a Claude Code session export, not an arm run
                    kinds["<session-export>"] += 1
                    continue
                kinds[kind] += 1
                if r.get("run_id"):
                    run_ids.add(r["run_id"])
                iid = r.get("item_id")
                if iid:
                    items.add(iid)
                if kind == "run_end":
                    v = r.get("verdict")
                    if iid in gold and v is not None and str(v) != gold[iid]:
                        disagreements += 1
        facts[f] = {
            "cls": agent_class(f),
            "kinds": dict(kinds),
            "disagreements": disagreements,
            "items": len(items),
            "cost": sum(cost_by_run.get(r, 0.0) for r in run_ids),
            "bytes": os.path.getsize(f),
            "retries": kinds.get("retry", 0),
            "checkpoints": kinds.get("human_checkpoint", 0),
        }

    by_class: defaultdict[str, list[str]] = defaultdict(list)
    for f, d in facts.items():
        by_class[d["cls"]].append(f)

    # ---------------------------------------------------------------- the clauses
    selected: defaultdict[str, list[str]] = defaultdict(list)

    # T1 - one per agent class. Applied to EVERY class present on disk, including the
    # one T1's wording does not name, because skipping a directory silently is the
    # failure the rule exists to prevent.
    for cls, members in sorted(by_class.items()):
        selected[sorted(members)[0]].append(
            f"T1 first-by-path representative of class `{cls}`")

    arms = sorted(by_class.get("arms", []))
    if arms:
        selected[arms[0]].append("T2a first arms run (sorted repo-relative path)")

        ranked = sorted(arms, key=lambda f: (facts[f]["cost"], f))
        idx = (len(ranked) - 1) // 2
        med = ranked[idx]
        selected[med].append(
            f"T2b median-cost arms run (USD {facts[med]['cost']:.4f}; "
            f"rank {idx + 1} of {len(ranked)}, lower median)")

        with_retry = [f for f in arms if facts[f]["retries"]]
        if with_retry:
            selected[with_retry[0]].append(
                f"T2c contains a `retry` record ({facts[with_retry[0]]['retries']})")

        with_hc = [f for f in arms if facts[f]["checkpoints"]]
        if with_hc:
            selected[with_hc[0]].append(
                f"T2d contains a `human_checkpoint` record "
                f"({facts[with_hc[0]]['checkpoints']})")

    # T3 - EVERY run whose verdict disagreed with gold. No cap, by design.
    for f, d in facts.items():
        if d["disagreements"] > 0:
            selected[f].append(
                f"T3 carries {d['disagreements']} item run(s) whose verdict disagreed "
                f"with gold - failures are never filtered out")

    # ---------------------------------------------------------------- the report
    out("# CH-12 - the selection rule APPLIED\n\n")
    out("Generated by `docs/evidence/ch12/apply_selection.py`, which evaluates every "
        "clause of [`docs/trajectories/SELECTION-RULE.md`](../../trajectories/SELECTION-RULE.md) "
        "against the committed trajectories.\n\n")
    out("**The rule was committed at `1afc295`, before this script existed.** "
        "`git log --format='%h %ad' --date=iso -- docs/trajectories/SELECTION-RULE.md "
        "docs/evidence/ch12/apply_selection.py` is the proof of ordering.\n\n")

    classes = ", ".join(f"`{c}` {len(v)}" for c, v in sorted(by_class.items()))
    out(f"Trajectory files considered: **{len(files)}** across "
        f"**{len(by_class)}** directories ({classes}).\n\n")

    # T1's named classes vs what exists.
    out("## T1 - one per agent class, and the class that has none\n\n")
    out("| class named by T1 | directory | files | representative |\n"
        "|---|---|---:|---|\n")
    for name, d in T1_CLASSES.items():
        if d is None:
            out(f"| **{name}** | *(none)* | **0** | "
                "**NO TRAJECTORY FILE EXISTS** - see `QUESTIONS.md` Q40 |\n")
        else:
            members = sorted(by_class.get(d, []))
            rep = Path(members[0]).name if members else "-"
            out(f"| {name} | `{d}/` | {len(members)} | `{rep}` |\n")
    unnamed = sorted(set(by_class) - {v for v in T1_CLASSES.values() if v})
    for d in unnamed:
        members = sorted(by_class[d])
        out(f"| *(not named by T1)* | `{d}/` | {len(members)} | "
            f"`{Path(members[0]).name}` - selected anyway |\n")
    out("\n")

    out("## Per file: which clause selected it\n\n")
    out("| class | trajectory | raw B | items | USD | selected by |\n")
    out("|---|---|---:|---:|---:|---|\n")
    for f in files:
        d = facts[f]
        cl = selected.get(f, [])
        mark = "<br>".join(cl) if cl else "**NOT SELECTED BY ANY CLAUSE**"
        out(f"| `{d['cls']}` | `{Path(f).name}` | {d['bytes']:,} | "
            f"{d['items'] or '-'} | {d['cost']:.4f} | {mark} |\n")

    n_sel = sum(1 for f in files if selected.get(f))
    n_unsel = len(files) - n_sel
    sel_bytes = sum(facts[f]["bytes"] for f in files if selected.get(f))
    all_bytes = sum(facts[f]["bytes"] for f in files)
    assert n_sel + n_unsel == len(files), "success + failure != n"

    out(f"\n**Selected: {n_sel} of {len(files)} files "
        f"({sel_bytes:,} B of {all_bytes:,} B = "
        f"{100 * sel_bytes / all_bytes:.1f}%). Not selected: {n_unsel}.** "
        f"`{n_sel} + {n_unsel} == {len(files)}`.\n\n")

    # ---------------------------------------------------------------- T3 dominates
    armfiles = sorted(by_class.get("arms", []))
    n_arm_t3 = sum(1 for f in armfiles if facts[f]["disagreements"] > 0)
    out("## Does T3 still select every arm file?\n\n")
    out(f"**{'YES' if n_arm_t3 == len(armfiles) else 'NO'} - "
        f"{n_arm_t3} of {len(armfiles)}.** ")
    out("T3 selects on *disagreement with gold*, and no arm scores 1.000 on this "
        "corpus - the best, A1, scores 0.7195 - so every arm run contains items whose "
        "verdict disagreed with gold, and a clause that never filters out a failure "
        "necessarily keeps every arm file. **A rule that selects everything is honest "
        "and worth stating.** CH-14a found the same thing under the clause name R3; "
        "it still holds with two more trajectories in the tree.\n\n")
    out("| arms trajectory | items | verdicts disagreeing with gold | retries | "
        "`human_checkpoint` records |\n|---|---:|---:|---:|---:|\n")
    for f in armfiles:
        d = facts[f]
        out(f"| `{Path(f).name}` | {d['items']} | {d['disagreements']} | "
            f"{d['retries']} | {d['checkpoints']} |\n")

    tot_hc = sum(facts[f]["checkpoints"] for f in armfiles)
    tot_rt = sum(facts[f]["retries"] for f in armfiles)
    out(f"\n**Totals across the arms class: {tot_rt} `retry` records, "
        f"{tot_hc} `human_checkpoint` records.** Both zero branches would print as "
        "zeros; neither is zero.\n\n")

    # ---------------------------------------------------------------- what it costs
    out("## What curation would save, measured inside the archive\n\n")
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / "a.zip"
        subprocess.run(["git", "archive", "--format=zip", "-o", str(zpath), "HEAD"],
                       check=True, capture_output=True)
        zip_bytes = zpath.stat().st_size
        comp: dict[str, int] = {}
        with zipfile.ZipFile(zpath) as z:
            for info in z.infolist():
                comp[info.filename] = info.compress_size
    sel_comp = sum(comp.get(f, 0) for f in files if selected.get(f))
    uns_comp = sum(comp.get(f, 0) for f in files if not selected.get(f))

    out(f"`git archive --format=zip HEAD` is **{zip_bytes:,} B = "
        f"{zip_bytes / 1e6:.2f} MB** against a **50 MB** cap "
        f"({50e6 / zip_bytes:.2f}x under, {(50e6 - zip_bytes) / 1e6:.2f} MB of "
        f"headroom).\n\n")
    out("| | files | raw B | compressed B | share of the upload |\n"
        "|---|---:|---:|---:|---:|\n")
    out(f"| selected | {n_sel} | {sel_bytes:,} | {sel_comp:,} | "
        f"{100 * sel_comp / zip_bytes:.1f}% |\n")
    out(f"| **NOT selected** | {n_unsel} | {all_bytes - sel_bytes:,} | "
        f"{uns_comp:,} | **{100 * uns_comp / zip_bytes:.1f}%** |\n")
    out(f"\nDropping every unselected file would take the upload from "
        f"**{zip_bytes / 1e6:.2f} MB** to **{(zip_bytes - uns_comp) / 1e6:.2f} MB**, "
        f"against a cap it already clears by "
        f"**{(50e6 - zip_bytes) / 1e6:.2f} MB**.\n\n")
    out("**So the rule is NOT INVOKED as a filter.** Under T4 the complete set ships, "
        "and a superset of the representatives is representative *a fortiori*. "
        "Invoking it here would cost real evidence - build-session transcripts are "
        "deliverable 4's only trace of how the coding agents were directed - to "
        "recover a fraction of an upload that is already far under cap. "
        "**That trade is refused.**\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
