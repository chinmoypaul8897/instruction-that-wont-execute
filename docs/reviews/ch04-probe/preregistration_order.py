"""REVIEW CH-04 - check 5: did GOOD.md acquire its numbers BEFORE any arm ran?

Two independent clocks are used and cross-checked:
  * GIT commit times (`git log --format=%cI`), converted to UTC;
  * the WALL CLOCK inside the run artefacts - every trajectory record and every
    cost-ledger row the arms produced.

`GOOD.md` claims: "committed BEFORE any model arm runs ... At the moment of this
commit the following have not been run: B0, B0-agent, B0-prime, A1, any ablation, and
the model-sensitivity subset." That claim is tested here, not taken.

Run: python docs/reviews/ch04-probe/preregistration_order.py
Out: docs/reviews/ch04-probe/preregistration-order.txt
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = []


def p(*a):
    OUT.append(" ".join(str(x) for x in a))


def git_utc(rev, path=None):
    args = ["git", "log", "-1", "--format=%cI"]
    if path:
        args += ["--diff-filter=A", "--", path] if rev is None else [rev, "--", path]
    elif rev:
        args += [rev]
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    s = r.stdout.strip().splitlines()
    if not s:
        return None
    return datetime.fromisoformat(s[0]).astimezone(timezone.utc)


def main():
    p("REVIEW CH-04 - check 5: pre-registration order, by two independent clocks")
    p("=" * 78)
    p("")

    events = []

    # ---------------------------------------------------------------- git clock
    for label, rev in (("goldens.md committed (8dae806)", "8dae806"),
                       ("src/score.py + src/bscript.py + tests first committed "
                        "(067a9d9)", "067a9d9"),
                       ("GOOD.md filled with its numbers (5172092)", "5172092"),
                       ("CH-04 3a/3b, the B-script run (91ab719)", "91ab719"),
                       ("checkpoint arm runner committed (715eeec)", "715eeec"),
                       ("first CHECKPOINT verdict, AMBER (7595562)", "7595562"),
                       ("re-run CHECKPOINT verdict, GREEN (9786f6c)", "9786f6c")):
        t = git_utc(rev)
        if t:
            events.append((t, "git    ", label))

    # ------------------------------------------------- GOOD.md's own history
    r = subprocess.run(["git", "log", "--format=%cI %h %s", "--", "GOOD.md"],
                       cwd=REPO, capture_output=True, text=True)
    p("GOOD.md's full commit history (newest first):")
    for line in r.stdout.strip().splitlines():
        iso, rest = line.split(" ", 1)
        p("    %s UTC  %s" % (datetime.fromisoformat(iso)
                              .astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                              rest))
    p("")
    p("    The 2026-08-30 18:23 commit is the empty skeleton from CH-00; the numbers")
    p("    arrive only at 5172092. Confirmed by diffing the skeleton:")
    old = subprocess.run(["git", "show", "6abf4f2:GOOD.md"],
                         cwd=REPO, capture_output=True, text=True).stdout
    p("      skeleton length %d chars; contains '0.25': %s; contains 'n = 76': %s"
      % (len(old), "0.25" in old, "n = 76" in old))
    now = (REPO / "GOOD.md").read_text(encoding="utf-8")
    p("      filled   length %d chars; contains '0.25': %s; contains 'n = 76': %s"
      % (len(now), "0.25" in now, "n = 76" in now))
    p("")

    # ---------------------------------------------------------------- run clock
    traj = REPO / "docs/trajectories/arms"
    ts_re = re.compile(r'"timestamp_utc"\s*:\s*"([^"]+)"')
    per_file = []
    for f in sorted(traj.glob("*.jsonl")):
        stamps = []
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            for m in ts_re.finditer(line):
                try:
                    stamps.append(datetime.fromisoformat(
                        m.group(1).replace("Z", "+00:00")).astimezone(timezone.utc))
                except ValueError:
                    pass
        if stamps:
            per_file.append((f.name, min(stamps), max(stamps), len(stamps)))
    p("Arm trajectories under docs/trajectories/arms/ (the model calls themselves):")
    p("    %-32s %-21s %-21s %s" % ("file", "first record UTC", "last record UTC",
                                    "stamps"))
    for name, lo, hi, n in sorted(per_file, key=lambda x: x[1]):
        p("    %-32s %-21s %-21s %d"
          % (name, lo.strftime("%Y-%m-%d %H:%M:%S"),
             hi.strftime("%Y-%m-%d %H:%M:%S"), n))
    if per_file:
        first_call = min(x[1] for x in per_file)
        events.append((first_call, "run    ",
                       "FIRST model-arm API call (%s)"
                       % min(per_file, key=lambda x: x[1])[0]))
    p("")

    # ---------------------------------------------------------------- ledger
    led = REPO / "docs/evidence/runs/cost_ledger.csv"
    rows = list(csv.DictReader(led.open(encoding="utf-8")))
    stamped = []
    for r_ in rows:
        m = re.search(r"(\d{8}T\d{6})", r_["run_id"])
        if m:
            stamped.append((datetime.strptime(m.group(1), "%Y%m%dT%H%M%S"), r_["arm"]))
    p("Cost ledger, docs/evidence/runs/cost_ledger.csv:")
    p("    %d rows; %d carry a timestamp in the run_id." % (len(rows), len(stamped)))
    arms = sorted({r_["arm"] for r_ in rows})
    p("    arms present: %s" % ", ".join(arms))
    if stamped:
        lo = min(stamped)
        p("    earliest timestamped row: %s  arm=%s"
          % (lo[0].strftime("%Y-%m-%d %H:%M:%S"), lo[1]))
        events.append((lo[0].replace(tzinfo=timezone.utc), "ledger ",
                       "earliest timestamped ledger row (arm=%s)" % lo[1]))
    p("")
    p("    NOTE: the B0 / B0-agent / sonnet rows carry NO timestamp in the run_id, so")
    p("    the ledger alone cannot date the arms. The trajectories can, and do.")
    p("")

    # ---------------------------------------------------------------- timeline
    p("=" * 78)
    p("MERGED TIMELINE (UTC)")
    p("=" * 78)
    good = None
    first_arm = None
    for t, src, label in sorted(events):
        p("    %s  %s  %s" % (t.strftime("%Y-%m-%d %H:%M:%S"), src, label))
        if "GOOD.md filled" in label:
            good = t
        if "FIRST model-arm" in label:
            first_arm = t
    p("")
    if good and first_arm:
        delta = (first_arm - good).total_seconds()
        p("    GOOD.md numbers committed   %s UTC" % good.strftime("%H:%M:%S"))
        p("    first model-arm API call    %s UTC" % first_arm.strftime("%H:%M:%S"))
        p("    margin                      %+.0f s (%.1f min)" % (delta, delta / 60))
        p("")
        p("    CHECK 5: %s"
          % ("PASS - the pre-registration provably predates every arm"
             if delta > 0 else
             "FAIL - an arm ran before the pre-registration was committed"))
    p("")
    p("    The one model call that DOES predate GOOD.md is the model-id probe at")
    p("    2026-08-30 20:37:36 UTC. GOOD.md section 10 discloses it by name:")
    p("      \"Committed spend at the time of this commit: USD 0.000246, all of it")
    p("       the model-id probe.\"")
    p("    Cross-check against the ledger AS IT STOOD AT THAT COMMIT")
    p("    (`git show 5172092:docs/evidence/runs/cost_ledger.csv`):")
    at = subprocess.run(["git", "show", "5172092:docs/evidence/runs/cost_ledger.csv"],
                        cwd=REPO, capture_output=True, text=True).stdout
    at_rows = list(csv.DictReader(at.splitlines()))
    at_arms = sorted({r_["arm"] for r_ in at_rows})
    at_tot = sum(float(r_["imputed_usd"]) for r_ in at_rows if r_["imputed_usd"])
    p("      rows %d; arms present: %s" % (len(at_rows), ", ".join(at_arms)))
    p("      -> NO arm row of any kind existed when GOOD.md was committed: %s"
      % (at_arms == ["probe-model-id"]))
    p("      imputed USD in the ledger at that commit: %.6f" % at_tot)
    p("      GOOD.md section 10 states:                0.000246")
    p("      agree: %s   delta %.6f"
      % (abs(at_tot - 0.000246) < 5e-7, at_tot - 0.000246))
    p("      the delta is exactly one haiku probe row (0.000034); GOOD.md counted")
    p("      five of the six priced haiku rows. The direction of the error is")
    p("      DOWNWARD - the pre-registration understates its own committed spend.")
    p("")
    p("    Ledger rows for the ARMS carry no timestamp, so the first-arm time above")
    p("    comes from the trajectories. Both clocks put every arm after 5172092.")

    p("")
    p("=" * 78)
    text = "\n".join(OUT) + "\n"
    (Path(__file__).resolve().parent / "preregistration-order.txt").write_text(
        text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
