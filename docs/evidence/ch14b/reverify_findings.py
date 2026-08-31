# -*- coding: utf-8 -*-
"""CH-14b - re-verify the standing in-fence sweep findings against the CURRENT files.

`QUESTIONS.md` Q39 UPDATE (CH-12) left 16 in-fence findings needing a rewrite rather
than a value swap. The chunk card names the worst: `AI-USE.md`'s SPEC-FIX-2 and CH-02
usage tables disagree with the artifacts they cite on every row.

Method, from the card and from hard rule 15: **re-verify each finding against the
current file before acting on it.** CH-12 re-checked 75 and 14 did not reproduce.

TWO READINGS ARE PRINTED, and neither is applied silently - the shape hard rule 7
requires and the one CH-11c's sweep used for the same reason:

  STRICT  the bare value anywhere in the file. Over-detects by construction, because
          this project corrects a number by printing the old one beside the new one
          under a heading that says so. After CH-14b's own fixes the STRICT count RISES,
          which is the disclosure working, not a regression.
  SCOPED  the value in its live position - the table row or the sentence that makes the
          claim. This is the reading that decides whether a finding still reproduces.

Run:  python docs/evidence/ch14b/reverify_findings.py
"""
import io
import json
import re
import subprocess
import sys

# Takes the file to check as an optional argument, so the same detector can be run
# against the PRE-FIX bytes out of git and the flip shown both ways (hard rule 6):
#   git show b6d80a4:AI-USE.md > old.md && python reverify_findings.py old.md
AI_USE = sys.argv[1] if len(sys.argv) > 1 else "AI-USE.md"


def head_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       stderr=subprocess.STDOUT).decode().strip()
    except Exception:
        return "unknown"


def artifact_numbers(path):
    """Pull the labelled figures out of a *-session-cost.txt artifact."""
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    pats = {
        "turns": r"assistant turns\s*:\s*([\d,]+)",
        "output": r"output tokens\s*:\s*([\d,]+)",
        "uncached": r"input, uncached\s*:\s*([\d,]+)",
        "cache_write": r"input, cache write\s*:\s*([\d,]+)",
        "cache_read": r"input, cache read\s*:\s*([\d,]+)",
        "total_input": r"TOTAL INPUT\s*:\s*([\d,]+)",
        "upper": r"upper bound, no cache discount\s+USD\s*([\d.]+)",
        "adjusted": r"cache-adjusted \(1\.25x / 0\.10x\)\s+USD\s*([\d.]+)",
    }
    got = {}
    for k, p in pats.items():
        m = re.search(p, txt)
        got[k] = m.group(1).replace(",", "") if m else None
    return got


def trajectory_span(path):
    """First and last assistant timestamp, and the assistant turn count."""
    stamps = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") == "assistant" and r.get("timestamp"):
            stamps.append(r["timestamp"])
    stamps.sort()
    if not stamps:
        return None, None, 0
    return stamps[0], stamps[-1], len(stamps)


def minutes_between(a, b):
    import datetime
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            t0 = datetime.datetime.strptime(a, fmt)
            t1 = datetime.datetime.strptime(b, fmt)
            return (t1 - t0).total_seconds() / 60.0
        except ValueError:
            continue
    raise ValueError("unparseable timestamps")


TXT = io.open(AI_USE, encoding="utf-8").read()
STATE = {"total": 0, "reproduced": 0, "strict_only": 0}


def check(label, bare, live, truth, note=""):
    """bare = the STRICT needle; live = the SCOPED needle (the claim in position)."""
    STATE["total"] += 1
    n_strict = TXT.count(bare) if bare else 0
    n_live = TXT.count(live) if live else 0
    reproduces = n_live > 0
    if reproduces:
        STATE["reproduced"] += 1
    elif n_strict:
        STATE["strict_only"] += 1
    print("  %-32s strict=%d scoped=%d  truth=%-14s %s%s"
          % (label, n_strict, n_live, str(truth),
             "REPRODUCES" if reproduces else
             ("does NOT reproduce (strict hits are quotations)" if n_strict
              else "does NOT reproduce"),
             ("   " + note) if note else ""))
    return reproduces


def fmt(v):
    if v is None:
        return "?"
    return "{:,}".format(int(v)) if "." not in v else v


def main():
    print("CH-14b - re-verification of the standing in-fence sweep findings")
    print("measured at commit %s" % head_sha())
    print("=" * 96)

    a = artifact_numbers("docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt")
    b = artifact_numbers("docs/evidence/ch02-attributor/ch02-session-cost.txt")

    print()
    print("F1  AI-USE.md SPEC-FIX-2 usage table vs docs/evidence/spec-fix-2/"
          "spec-fix-2-session-cost.txt")
    for label, bare, live, key in [
        ("output", "126,862", "| output | 126,862 |", "output"),
        ("input, uncached", "198", "| input, uncached | 198 |", "uncached"),
        ("input, cache write", "250,800", "| input, cache write | 250,800 |", "cache_write"),
        ("input, cache read", "10,327,144", "| input, cache read | 10,327,144 |", "cache_read"),
        ("total input", "10,578,142", "| **total input** | **10,578,142** |", "total_input"),
        ("assistant turns", "99", "| assistant turns | 99 |", "turns"),
        ("upper bound USD", "56.062260", "discount | **56.062260** |", "upper"),
        ("cache-adjusted USD", "9.903612", "list | **9.903612** |", "adjusted"),
    ]:
        check(label, bare, live, fmt(a[key]))

    print()
    print("F2  AI-USE.md CH-02 usage table vs docs/evidence/ch02-attributor/"
          "ch02-session-cost.txt")
    for label, bare, live, key in [
        ("output", "514,051", "| output | 514,051 |", "output"),
        ("input, uncached", "478", "| input, uncached | 478 |", "uncached"),
        ("input, cache write", "626,057", "| input, cache write | 626,057 |", "cache_write"),
        ("input, cache read", "40,957,406", "| input, cache read | 40,957,406 |", "cache_read"),
        ("total input", "41,583,941", "| **total input** | **41,583,941** |", "total_input"),
        ("assistant turns", "239", "(239 assistant turns", "turns"),
        ("upper bound USD", "220.770980", "discount | **220.770980** |", "upper"),
        ("cache-adjusted USD", "37.245224", "list | **37.245224** |", "adjusted"),
    ]:
        check(label, bare, live, fmt(b[key]))

    print()
    print("F3  derived figures that inherit the two tables")
    sf1 = 19152452 + 23254519
    ch01 = 41093185
    check("SPEC-FIX-2 total in M", "10.58 M", "session's total is 10.58 M",
          "%.2f M" % (int(a["total_input"]) / 1e6))
    check("over the 5 M target", "2.1×", "**10.58 M — 2.1× over**",
          "%.2fx" % (int(a["total_input"]) / 5e6))
    check("reduction vs SPEC-FIX-1", "4.0×", "a 4.0× reduction",
          "%.1fx" % (sf1 / float(a["total_input"])), "SPEC-FIX-1 = 19,152,452+23,254,519")
    check("cache read share", "10.33 M", "**10.33 M of the 10.58 M is cache",
          "%.2f M" % (int(a["cache_read"]) / 1e6))
    check("turns in the narrative", "99 turns", "across 99 turns", "%s turns" % a["turns"])
    check("CH-02 in the comparison list", "41.58 M", "CH-02 41.58 M",
          "%.2f M" % (int(b["total_input"]) / 1e6))
    check("CH-02 input tokens", "41.6 M", "came out at **41.6 M**",
          "%.1f M" % (int(b["total_input"]) / 1e6))
    check("CH-02 vs CH-01", "1.2% higher", "i.e. **1.2% higher**",
          "%.1f%% higher" % ((int(b["total_input"]) / float(ch01) - 1) * 100),
          "CH-01 = 41,093,185")

    print()
    print("F4  AI-USE.md CH-02 wall-clock vs the shipped trajectory it cites")
    first, last, turns = trajectory_span("docs/trajectories/build/CH-02.jsonl")
    print("      shipped CH-02.jsonl : %d assistant turns, %s -> %s"
          % (turns, first, last))
    check("wall-clock span", "47.6 min", "= **47.6 min**, against",
          "%.1f min" % minutes_between(first, last))

    print()
    print("F5  findings already fixed by CH-11c / CH-12 - confirm they stay fixed")
    check("CH-02 trajectory line count", "644 lines", "(644 lines", "709 lines")
    check("CH-02 trajectory byte count", "1,574,519", "1,574,519 B;", "1,689,144")
    check("project spend to date", "1.935538", "Measured spend to date: USD 1.935538",
          "11.632274")
    live_headings = [l for l in TXT.splitlines()
                     if l.startswith("### NIGHT-RUN") and "FAILED then FIXED" in l]
    STATE["total"] += 1
    if live_headings:
        STATE["reproduced"] += 1
    else:
        STATE["strict_only"] += TXT.count("CH-03 FAILED then FIXED") > 0
    print("  %-32s strict=%d scoped=%d  truth=%-14s %s"
          % ("NIGHT-RUN heading verdict", TXT.count("CH-03 FAILED then FIXED"),
             len(live_headings), "FAIL x2 -> ESC",
             "REPRODUCES" if live_headings else
             "does NOT reproduce (strict hits are quotations)"))

    print()
    print("=" * 96)
    print("re-verified                       : %d" % STATE["total"])
    print("REPRODUCE (live defect)           : %d" % STATE["reproduced"])
    print("do NOT reproduce                  : %d" % (STATE["total"] - STATE["reproduced"]))
    print("  of those, STRICT still hits     : %d  <- the old value quoted inside the"
          % STATE["strict_only"])
    print("                                       dated note that corrects it. Kept on")
    print("                                       purpose: hard rule 5 forbids deleting")
    print("                                       a number to make a discrepancy vanish.")
    assert STATE["reproduced"] <= STATE["total"]
    return 0


if __name__ == "__main__":
    sys.exit(main())
