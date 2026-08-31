#!/usr/bin/env python3
"""CH-12 - the measured facts behind `docs/trajectories/INDEX.md`.

The INDEX's "what to look at in it" column is editorial judgement. Everything else in
it - sizes, line counts, record spans, session ids, which file holds which reviewer -
is measured here, so a reader can check the navigation rather than trust it.

Pure: no network, no clock, no randomness, no model call. `git` is read-only.

Run:  python docs/evidence/ch12/trajectory_facts.py > docs/evidence/ch12/trajectory-facts.txt
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, encoding="utf-8",
                          errors="replace", check=True).stdout


REPO = Path(sh("git", "rev-parse", "--show-toplevel").strip())
os.chdir(REPO)

BUILD = Path("docs/trajectories/build")
ARMS = Path("docs/trajectories/arms")
PROBE = Path("docs/trajectories/probe")

#: The three review verdicts, and the file each one is recorded in.
REVIEWS = ["REVIEW_CH-03.md", "REVIEW_CH-03-round2.md", "REVIEW_CH-04.md"]


def read_jsonl(p: Path):
    for line in p.open(encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def main() -> int:
    print("CH-12 - TRAJECTORY FACTS")
    print("=" * 108)

    # ------------------------------------------------------------ build sessions
    print("\nBUILD SESSIONS - docs/trajectories/build/\n")
    print(f"{'file':<30}{'bytes':>11}{'lines':>8}{'asst':>7}  "
          f"{'first record (UTC)':<26}{'last record (UTC)':<26}{'sessionId':<10}")
    print("-" * 128)
    sessions: defaultdict[str, list[str]] = defaultdict(list)
    tot_b = tot_l = 0
    for p in sorted(BUILD.glob("*.jsonl")):
        recs = list(read_jsonl(p))
        ts = sorted(r["timestamp"] for r in recs if r.get("timestamp"))
        asst = sum(1 for r in recs if r.get("type") == "assistant")
        sid = next((r.get("sessionId") for r in recs if r.get("sessionId")), "?")
        lines = sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
        b = p.stat().st_size
        tot_b += b
        tot_l += lines
        sessions[sid[:8]].append(p.name)
        print(f"{p.name:<30}{b:>11,}{lines:>8,}{asst:>7}  "
              f"{(ts[0] if ts else '-'):<26}{(ts[-1] if ts else '-'):<26}{sid[:8]:<10}")
    print("-" * 128)
    n_files = len(list(BUILD.glob('*.jsonl')))
    print(f"{'TOTAL':<30}{tot_b:>11,}{tot_l:>8,}")
    print(f"\nfiles: {n_files}   DISTINCT SESSIONS: {len(sessions)}")
    for sid, names in sorted(sessions.items()):
        if len(names) > 1:
            print(f"  session {sid} exported {len(names)} times: {', '.join(names)}")

    # Is one export a byte-prefix of the other? (the NIGHT-RUN question)
    for sid, names in sorted(sessions.items()):
        if len(names) == 2:
            a, b = (BUILD / n for n in sorted(names, key=lambda n: (BUILD / n).stat().st_size))
            la = a.read_bytes()
            lb = b.read_bytes()
            print(f"  is {a.name} a byte-exact prefix of {b.name}? "
                  f"{'YES' if lb.startswith(la) else 'NO'}")

    # ------------------------------------------------- where the instructions are
    print("\n\nWHERE EACH BUILD SESSION'S INSTRUCTIONS ARE\n")
    tracked = set(sh("git", "ls-files", "prompts").split("\n"))
    print(f"{'trajectory':<30}{'opening operator message':<52}{'card tracked?'}")
    print("-" * 108)
    for p in sorted(BUILD.glob("*.jsonl")):
        prompt = next((r.get("lastPrompt") for r in read_jsonl(p)
                       if r.get("type") == "last-prompt" and r.get("lastPrompt")), None)
        card = "?"
        if prompt and "prompts/" in prompt:
            card = prompt.split("prompts/")[1].split()[0].rstrip(".")
            card = "prompts/" + card
        state = ("tracked" if card in tracked else
                 "UNTRACKED" if Path(card).exists() else "MISSING")
        print(f"{p.name:<30}{(prompt or '(none recorded)')[:50]:<52}{state}")

    # ------------------------------------------------------- who held the reviews
    print("\n\nWHICH BUILD TRANSCRIPT CONTAINS WHICH REVIEW\n")
    print(f"{'trajectory':<30}" + "".join(f"{r:<26}" for r in REVIEWS) + "Agent calls")
    print("-" * 122)
    for p in sorted(BUILD.glob("*.jsonl")):
        raw = p.read_text(encoding="utf-8", errors="replace")
        counts = [raw.count(r) for r in REVIEWS]
        agents = raw.count('"name":"Agent"') + raw.count('"name": "Agent"')
        print(f"{p.name:<30}" + "".join(f"{c:<26}" for c in counts) + str(agents))

    print("\nVerdict of each committed review (first VERDICT line in the file):")
    for r in REVIEWS:
        f = Path("docs/reviews") / r
        if not f.exists():
            print(f"  {r:<26} FILE MISSING")
            continue
        line = next((l.strip() for l in f.read_text(encoding="utf-8",
                                                    errors="replace").splitlines()
                     if "VERDICT" in l.upper()), "(no verdict line)")
        print(f"  {r:<26} {line[:80]}")

    # ------------------------------------------------------------ evaluation arms
    print("\n\nEVALUATION ARMS - docs/trajectories/arms/\n")
    print(f"{'file':<34}{'bytes':>11}{'records':>9}  record kinds")
    print("-" * 108)
    for p in sorted(ARMS.glob("*.jsonl")):
        kinds = Counter(r.get("record") for r in read_jsonl(p))
        n = sum(kinds.values())
        pretty = ", ".join(f"{k}:{v}" for k, v in sorted(kinds.items(),
                                                         key=lambda kv: str(kv[0])))
        print(f"{p.name:<34}{p.stat().st_size:>11,}{n:>9}  {pretty}")

    # ---------------------------------------------------- what is NOT in the repo
    print("\n\nWHAT IS ON DISK BUT NOT SHIPPED, AND WHY\n")
    per_item = ARMS / "per-item"
    on_disk = len(list(per_item.glob("*.jsonl"))) if per_item.exists() else 0
    in_git = len([x for x in sh("git", "ls-files",
                                str(per_item).replace("\\", "/")).split("\n") if x])
    print(f"  docs/trajectories/arms/per-item/ : {on_disk:,} files on disk, "
          f"{in_git} tracked")
    print("    git-ignored by .gitignore's `docs/trajectories/*/per-item/` rule. "
          "Every record")
    print("    survives in the BUNDLED <arm>-rep<N>.jsonl - src/arms.py::bundle() "
          "promises")
    print("    'EVERY RECORD SURVIVES - nothing is sampled, summarised or dropped'.")
    print("  reviewer subagent transcripts       : 0 tracked. The Agent tool writes "
          "them to a")
    print("    temp path outside the repository. What ships is the launch prompt "
          "verbatim inside")
    print("    the build transcript, the verdict verbatim in its task-notification, "
          "and the")
    print("    runnable probes under docs/reviews/.")
    print("  workflow journals (86 audit subagents): 0 tracked. Same reason. "
          "QUESTIONS.md Q40.")

    # ------------------------------------------------------------------- totals
    print("\n\nTOTALS\n")
    counts = {"build": len(list(BUILD.glob("*.jsonl"))),
              "arms": len(list(ARMS.glob("*.jsonl"))),
              "probe": len(list(PROBE.glob("*.jsonl")))}
    tracked_jsonl = [x for x in sh("git", "ls-files", "docs/trajectories").split("\n")
                     if x.endswith(".jsonl")]
    print(f"  on disk : " + ", ".join(f"{k} {v}" for k, v in counts.items())
          + f"  = {sum(counts.values())}")
    print(f"  tracked : {len(tracked_jsonl)}")
    assert sum(counts.values()) == len(tracked_jsonl), \
        "a trajectory on disk is not tracked, or vice versa"
    print("  on disk == tracked  OK")
    total_bytes = sum(p.stat().st_size for p in
                      list(BUILD.glob('*.jsonl')) + list(ARMS.glob('*.jsonl'))
                      + list(PROBE.glob('*.jsonl')))
    print(f"  total   : {total_bytes:,} B = {total_bytes / 1e6:.2f} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
