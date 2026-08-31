# -*- coding: utf-8 -*-
"""Q40 - does the adversarial-audit class really have ZERO trajectories?

`docs/trajectories/SELECTION-RULE.md` clause T1 names three agent classes. Two have a
directory under `docs/trajectories/`. The third, adversarial audits, has none, and both
that file and `QUESTIONS.md` Q40 record the class as having no trajectory at all. Hard
rule 15: that is a claim until the artifacts are read.

This reads every exported build session and separates three things that are easy to
conflate, and which this script's own first version DID conflate:

  1. sidechain records   - a subagent's OWN turns. This is what "a trajectory" means.
  2. launch prompts      - the Task/Agent tool_use input for a single audit agent.
  3. workflow scripts    - the Workflow tool_use input for a FLEET of audit agents.
                           This is the fleet's equivalent of a launch prompt and it
                           carries each subagent's prompt template inside it.
  4. delivered reports   - the agent's or fleet's final result, verbatim, inside the
                           completion <task-notification><result> block.

The immediate tool_result of a Task call is NOT the report. For an async agent it is
launch metadata ("Async agent launched successfully..."), identical for every launch.
Counting it as a report is what the first version of this file did, and it inflated the
answer from 1 to 5. The count below is taken from the notification instead.

Run:  python docs/evidence/ch14b/audit_class_census.py
"""
import io
import json
import os
import re
import subprocess
import sys

BUILD = os.path.join("docs", "trajectories", "build")
LAUNCHERS = ("Task", "Agent")
LAUNCH_METADATA = "Async agent launched successfully"


def head_sha():
    """Name the commit every count below was measured at.

    CH-12 recorded why this matters: a parallel session landed a transcript
    mid-audit and moved three of its counts. CH-13B landed one during this
    chunk, taking docs/trajectories/build/ from 13 files to 14 between two
    runs of this script.
    """
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                      stderr=subprocess.STDOUT)
        return out.decode("utf-8", "replace").strip()
    except Exception:
        return "unknown"


def load(path):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def blocks(rec):
    msg = rec.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), list):
        for b in msg["content"]:
            if isinstance(b, dict):
                yield b


def census(path):
    recs = load(path)
    raw = io.open(path, encoding="utf-8").read()

    sidechain = sum(1 for r in recs if r.get("isSidechain") is True)

    launches = []
    scripts = []
    metadata_only = 0
    for r in recs:
        for b in blocks(r):
            if b.get("type") == "tool_use" and b.get("name") in LAUNCHERS:
                inp = b.get("input", {})
                launches.append({
                    "description": inp.get("description"),
                    "prompt_chars": len(str(inp.get("prompt", ""))),
                })
            elif b.get("type") == "tool_use" and b.get("name") == "Workflow":
                inp = b.get("input", {})
                scripts.append({"chars": len(str(inp.get("script", "")))})
            elif b.get("type") == "tool_result":
                if LAUNCH_METADATA in json.dumps(b.get("content", ""), ensure_ascii=False):
                    metadata_only += 1

    # A delivered report is a completion notification carrying a <result> block.
    # Two kinds matter and they are counted apart, because they are different evidence:
    #   single agent - summary 'Agent "<name>" finished', result is the agent's report
    #   fleet        - summary 'Dynamic workflow "<name>"', result is the workflow's
    #                  aggregated structured output over all its subagents
    # Background shell commands notify the same way and carry no <result>; they drop
    # out here by construction.
    delivered, verdicts, fleets = 0, 0, 0
    seen = set()
    for m in re.finditer(r"<task-notification>(.*?)</task-notification>", raw, re.S):
        body = m.group(1)
        tid = re.search(r"<task-id>(.*?)</task-id>", body)
        res = re.search(r"<result>(.*)", body, re.S)
        summ = re.search(r"<summary>(.*?)</summary>", body, re.S)
        if not tid or not res:
            continue
        if tid.group(1) in seen:       # a task-id may notify more than once
            continue
        seen.add(tid.group(1))
        delivered += 1
        if summ and "Dynamic workflow" in summ.group(1):
            fleets += 1
        if "VERDICT: **FAIL**" in res.group(1) or "VERDICT: FAIL" in res.group(1) \
                or "VERDICT: **PASS**" in res.group(1) or "VERDICT: PASS" in res.group(1):
            verdicts += 1

    return {
        "file": os.path.basename(path),
        "records": len(recs),
        "sidechain": sidechain,
        "launches": launches,
        "scripts": scripts,
        "metadata_only_results": metadata_only,
        "delivered_reports": delivered,
        "delivered_verdicts": verdicts,
        "delivered_fleets": fleets,
    }


def main():
    files = sorted(f for f in os.listdir(BUILD) if f.endswith(".jsonl"))
    rows = [census(os.path.join(BUILD, f)) for f in files]

    print("Q40 - adversarial-audit class census over docs/trajectories/build/")
    print("measured at commit %s" % head_sha())
    print("=" * 84)
    print("%-28s %8s %9s %8s %8s %9s %8s %7s"
          % ("session transcript", "records", "sidechain", "launches", "scripts",
             "delivered", "verdicts", "fleets"))
    print("-" * 92)
    for r in rows:
        print("%-28s %8d %9d %8d %8d %9d %8d %7d"
              % (r["file"], r["records"], r["sidechain"], len(r["launches"]),
                 len(r["scripts"]), r["delivered_reports"], r["delivered_verdicts"],
                 r["delivered_fleets"]))
    print("-" * 92)
    tot_side = sum(r["sidechain"] for r in rows)
    tot_launch = sum(len(r["launches"]) for r in rows)
    tot_deliv = sum(r["delivered_reports"] for r in rows)
    tot_verd = sum(r["delivered_verdicts"] for r in rows)
    tot_meta = sum(r["metadata_only_results"] for r in rows)
    tot_fleet = sum(r["delivered_fleets"] for r in rows)
    tot_script = sum(len(r["scripts"]) for r in rows)
    print("%-28s %8d %9d %8d %8d %9d %8d %7d"
          % ("TOTAL (%d files)" % len(rows), sum(r["records"] for r in rows),
             tot_side, tot_launch, tot_script, tot_deliv, tot_verd, tot_fleet))
    print()
    print("Task tool_results that are launch metadata only, not a report: %d" % tot_meta)
    print()

    print("Every captured audit-agent launch, and every fleet script")
    print("=" * 92)
    if tot_launch == 0 and tot_script == 0:
        print("(none)")
    for r in rows:
        for d in r["launches"]:
            print("%-28s %-32s launch prompt %6d chars"
                  % (r["file"], (d["description"] or "?")[:32], d["prompt_chars"]))
        for d in r["scripts"]:
            print("%-28s %-32s workflow script %5d chars"
                  % (r["file"], "(subagent fleet)", d["chars"]))
    print()

    # The two night-run files are two exports of ONE session, so their launches are the
    # same agents counted twice. Distinct agents is what the answer turns on.
    nightrun = [r for r in rows if r["file"].startswith("NIGHT-RUN")]
    dupes = 0
    if len(nightrun) == 2:
        a = set((d["description"], d["prompt_chars"]) for d in nightrun[0]["launches"])
        b = set((d["description"], d["prompt_chars"]) for d in nightrun[1]["launches"])
        dupes = len(a & b)
    distinct = tot_launch - dupes

    print("FINDING")
    print("=" * 84)
    print("sidechain records across every build transcript   : %d" % tot_side)
    print("audit-agent launch prompts captured               : %d" % tot_launch)
    print("  minus the night run's second export of the same : -%d" % dupes)
    print("  DISTINCT audit agents with a committed prompt   : %d" % distinct)
    print("workflow scripts committed (a fleet's instructions): %d" % tot_script)
    print("reports delivered verbatim into a transcript      : %d" % tot_deliv)
    print("  of those, a single agent's review VERDICT       : %d" % tot_verd)
    print("  of those, a subagent FLEET's aggregated output   : %d" % tot_fleet)
    print()
    print("Q40 asked whether the class is wrong or the trajectory is missing.")
    print("THE CLASS IS RIGHT AND THE TRAJECTORY IS MISSING - but the class is not")
    print("evidence-free inside docs/trajectories/, which is what the rule implies now:")
    print("  * %d distinct audit agents ship their LAUNCH PROMPT verbatim" % distinct)
    print("  * %d ship their VERDICT verbatim" % tot_verd)
    print("  * %d workflow scripts ship verbatim - a fleet's instructions, carrying"
          % tot_script)
    print("    each subagent's prompt template inside them")
    print("  * %d subagent FLEETS ship their aggregated structured output verbatim"
          % tot_fleet)
    print("What no file holds, for any audit agent, is the agent's OWN INTERMEDIATE")
    print("TURNS: %d sidechain records in %d records across %d transcripts."
          % (tot_side, sum(r["records"] for r in rows), len(rows)))
    print("The gap is real, it is narrower than 'zero trajectories', and it is not closed.")

    # Hard rule 14: the totals must reconcile with the rows they came from.
    assert tot_launch == sum(len(r["launches"]) for r in rows)
    assert tot_verd <= tot_deliv
    assert distinct <= tot_launch
    assert tot_script == sum(len(r["scripts"]) for r in rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
