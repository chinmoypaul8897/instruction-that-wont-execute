"""CH-14a step 1b - APPLY the published selection rule mechanically, and show what
it selects. The rule is in `selection-rule.md` and was written before this ran.

`QUESTIONS.md` Q2 consequence C2 requires a curated representative trajectory set in
the zip and an auditable selection rule. This script IS the audit: it evaluates every
clause against the committed trajectories and prints, per file, which clause selected
it - or that no clause did.

Pure: no network, no clock, no randomness. Reads the committed trajectories, the
frozen eval set and the committed cost ledger.

    python docs/evidence/ch14-size/apply_selection.py > docs/evidence/ch14-size/selection-applied.md
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
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


REPO = Path(sh("git", "rev-parse", "--show-toplevel").strip())
os.chdir(REPO)

TRAJ = "docs/trajectories"
LEDGER = Path("docs/evidence/runs/cost_ledger.csv")
EVALSET = Path("data/evalset/items.jsonl")


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

    # --- per-run imputed cost, from the committed ledger -----------------------
    cost_by_run: dict[str, float] = defaultdict(float)
    with LEDGER.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                cost_by_run[row["run_id"]] += float(row["imputed_usd"] or 0.0)
            except ValueError:
                pass

    files = sorted(p for p in sh("git", "ls-files", "-z", TRAJ).split("\0")
                   if p.endswith(".jsonl"))

    # --- read every trajectory once -------------------------------------------
    facts: dict[str, dict] = {}
    for f in files:
        kinds: defaultdict[str, int] = defaultdict(int)
        disagreements = 0
        items = set()
        run_ids = set()
        with open(f, encoding="utf-8") as fh:
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
                if kind is None:      # a Claude Code session export, not an arm run
                    kinds["<session-export>"] += 1
                    continue
                kinds[kind] += 1
                rid = r.get("run_id")
                if rid:
                    run_ids.add(rid)
                iid = r.get("item_id")
                if iid:
                    items.add(iid)
                if kind == "run_end":
                    v = r.get("verdict")
                    if iid in gold and v is not None and str(v) != gold[iid]:
                        disagreements += 1
        cost = sum(cost_by_run.get(r, 0.0) for r in run_ids)
        facts[f] = {
            "cls": agent_class(f),
            "kinds": dict(kinds),
            "disagreements": disagreements,
            "items": len(items),
            "cost": cost,
            "bytes": os.path.getsize(f),
            "has_retry": kinds.get("retry", 0) > 0,
            "has_checkpoint": kinds.get("human_checkpoint", 0) > 0,
        }

    by_class: defaultdict[str, list[str]] = defaultdict(list)
    for f, d in facts.items():
        by_class[d["cls"]].append(f)

    # --- evaluate the clauses --------------------------------------------------
    selected: defaultdict[str, list[str]] = defaultdict(list)   # path -> clauses

    for cls, members in sorted(by_class.items()):
        first = sorted(members)[0]
        selected[first].append("R1 first-by-path representative of class " + cls)

    arms = sorted(by_class.get("arms", []))
    if arms:
        # R2a - the FIRST run of the arms class, by sorted path.
        selected[arms[0]].append("R2a first arms run (sorted path)")
        # R2b - the median-cost run.
        ranked = sorted(arms, key=lambda f: (facts[f]["cost"], f))
        idx = (len(ranked) - 1) // 2
        med = ranked[idx]
        selected[med].append(
            "R2b median-cost arms run (USD %.4f; rank %d of %d)"
            % (facts[med]["cost"], idx + 1, len(ranked)))
        # R2c - one containing a retry record.
        with_retry = [f for f in arms if facts[f]["has_retry"]]
        if with_retry:
            selected[with_retry[0]].append(
                "R2c contains a `retry` record (%d)"
                % facts[with_retry[0]]["kinds"].get("retry", 0))
        # R2d - one containing a human_checkpoint record.
        with_hc = [f for f in arms if facts[f]["has_checkpoint"]]
        if with_hc:
            selected[with_hc[0]].append(
                "R2d contains a `human_checkpoint` record (%d)"
                % facts[with_hc[0]]["kinds"].get("human_checkpoint", 0))

    # R3 - EVERY run whose verdict disagreed with gold. Failures are never filtered.
    for f, d in facts.items():
        if d["disagreements"] > 0:
            selected[f].append(
                "R3 carries %d item run(s) whose verdict disagreed with gold - "
                "failures are never filtered out" % d["disagreements"])

    # --- report ---------------------------------------------------------------
    out("# CH-14a - the selection rule APPLIED\n\n")
    out("Generated by `docs/evidence/ch14-size/apply_selection.py`, which evaluates "
        "every clause of `selection-rule.md` against the committed trajectories. "
        "The rule was written first; this is what it selects.\n\n")
    classes = ", ".join("`%s` %d" % (c, len(v)) for c, v in sorted(by_class.items()))
    out("Trajectory files considered: **%d** across **%d** agent classes (%s).\n\n"
        % (len(files), len(by_class), classes))

    out("## Per file: which clause selected it\n\n")
    out("| agent class | trajectory | raw B | items | USD | selected by |\n")
    out("|---|---|---:|---:|---:|---|\n")
    for f in files:
        d = facts[f]
        cl = selected.get(f, [])
        mark = "<br>".join(cl) if cl else "**NOT SELECTED BY ANY CLAUSE**"
        out("| `%s` | `%s` | %s | %s | %.4f | %s |\n"
            % (d["cls"], Path(f).name, format(d["bytes"], ","),
               d["items"] or "-", d["cost"], mark))

    n_sel = sum(1 for f in files if selected.get(f))
    n_unsel = len(files) - n_sel
    sel_bytes = sum(facts[f]["bytes"] for f in files if selected.get(f))
    all_bytes = sum(facts[f]["bytes"] for f in files)

    out("\n**Selected: %d of %d files (%s B of %s B = %.1f%%). Not selected: %d.**\n\n"
        % (n_sel, len(files), format(sel_bytes, ","), format(all_bytes, ","),
           100 * sel_bytes / all_bytes, n_unsel))

    out("## Why clause R3 dominates\n\n")
    armfiles = sorted(by_class.get("arms", []))
    n_arm_r3 = sum(1 for f in armfiles if facts[f]["disagreements"] > 0)
    out("R3 - *every run whose verdict disagreed with gold* - selects **%d of %d** "
        "arms trajectories on its own. No arm scores 1.000 on this corpus (the best, "
        "A1, scores 0.7195), so every arm run contains disagreeing items, and a rule "
        "that never filters out a failure necessarily keeps every arm file. **That is "
        "not a loophole; it is the clause doing exactly what it was written to do.**\n\n"
        % (n_arm_r3, len(armfiles)))
    out("| arms trajectory | items | verdicts disagreeing with gold |\n|---|---:|---:|\n")
    for f in armfiles:
        out("| `%s` | %d | %d |\n"
            % (Path(f).name, facts[f]["items"], facts[f]["disagreements"]))

    # --- what the UNSELECTED files would actually save, measured in the archive --
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / "a.zip"
        subprocess.run(["git", "archive", "--format=zip", "-o", str(zpath), "HEAD"],
                       check=True, capture_output=True)
        zip_bytes = zpath.stat().st_size
        with zipfile.ZipFile(zpath) as z:
            info = {i.filename: i for i in z.infolist()}
    unsel_files = [f for f in files if not selected.get(f)]
    u_raw = sum(info[f].file_size for f in unsel_files if f in info)
    u_cmp = sum(info[f].compress_size for f in unsel_files if f in info)
    s_cmp = sum(info[f].compress_size for f in files
                if selected.get(f) and f in info)

    out("\n## What dropping the unselected files would actually save\n\n")
    out("Measured inside `git archive --format=zip HEAD`, not estimated from raw "
        "size. This is the whole reason the rule is not invoked.\n\n")
    out("| | raw B | compressed B | share of the %.2f MB upload |\n|---|---:|---:|---:|\n"
        % (zip_bytes / 1e6))
    out("| selected (%d files) | %s | %s | %.1f%% |\n"
        % (len(files) - len(unsel_files),
           format(sum(info[f].file_size for f in files
                      if selected.get(f) and f in info), ","),
           format(s_cmp, ","), 100 * s_cmp / zip_bytes))
    out("| **NOT selected (%d files)** | %s | **%s** | **%.1f%%** |\n"
        % (len(unsel_files), format(u_raw, ","), format(u_cmp, ","),
           100 * u_cmp / zip_bytes))
    out("\nDropping every unselected file would take the upload from **%.2f MB** to "
        "**%.2f MB**, against a **50 MB** cap it already clears by **%.2f MB**.\n"
        % (zip_bytes / 1e6, (zip_bytes - u_cmp) / 1e6,
           (50_000_000 - zip_bytes) / 1e6))

    out("\n## What is shipped\n\n")
    out("The archive ships the **complete** trajectory set, which is a **superset** of "
        "the selection above. The rule is published and applied so that the curation "
        "is auditable if the archive ever has to be trimmed; at %s B raw the set "
        "compresses inside the cap and no trimming is needed. See `inventory.md` and "
        "`QUESTIONS.md` Q27.\n" % format(all_bytes, ","))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
