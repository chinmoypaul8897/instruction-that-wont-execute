# -*- coding: utf-8 -*-
"""Q42 - what does NIGHT-RUN-FINAL.jsonl actually contain?

`QUESTIONS.md` Q42 and `docs/trajectories/INDEX.md` say the file holds *both* CH-03
reviewers, *their launch prompts verbatim and their FAIL verdicts verbatim*. That is the
claim this chunk was told to index and disclose. Hard rule 15 says check it first.

For each of the two night-run exports this prints, per reviewer:

  * whether the launch prompt is present, and its length
  * the status its completion notification reports
  * whether a verbatim `VERDICT: FAIL` from that agent is in the file

Run:  python docs/evidence/ch14b/nightrun_contents.py
"""
import io
import json
import os
import re
import subprocess
import sys

FILES = [
    os.path.join("docs", "trajectories", "build", "NIGHT-RUN-CHECKPOINT.jsonl"),
    os.path.join("docs", "trajectories", "build", "NIGHT-RUN-FINAL.jsonl"),
]

# Both reviewers, by the description the launching Task call gave them.
REVIEWERS = ["Adversarial review of CH-03", "Re-review fixed CH-03"]


def head_sha():
    """Name the commit these counts were measured at - a parallel session can move
    docs/trajectories/ mid-chunk, and one did during CH-14b."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                      stderr=subprocess.STDOUT)
        return out.decode("utf-8", "replace").strip()
    except Exception:
        return "unknown"


def scan(path):
    raw = io.open(path, encoding="utf-8").read()
    recs = []
    for line in io.open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                recs.append(json.loads(line))
            except ValueError:
                pass

    launches = {}
    for r in recs:
        msg = r.get("message")
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_use" \
                        and b.get("name") in ("Task", "Agent"):
                    inp = b.get("input", {})
                    launches[inp.get("description")] = {
                        "prompt_chars": len(str(inp.get("prompt", ""))),
                        "tool_use_id": b.get("id"),
                    }

    # Completion notifications carry the agent id, a <status> and, when the agent
    # finished inside the session, a <result> block holding its report verbatim.
    notes = {}
    for m in re.finditer(r"<task-notification>(.*?)</task-notification>", raw, re.S):
        body = m.group(1)
        tid = re.search(r"<task-id>(.*?)</task-id>", body)
        st = re.search(r"<status>(.*?)</status>", body)
        summ = re.search(r"<summary>(.*?)</summary>", body, re.S)
        res = re.search(r"<result>(.*)", body, re.S)
        if not tid:
            continue
        key = tid.group(1)
        rec = notes.setdefault(key, {"statuses": set(), "summaries": set(),
                                     "verdict_fail": False, "result_seen": False})
        if st:
            rec["statuses"].add(st.group(1))
        if summ:
            rec["summaries"].add(" ".join(summ.group(1).split())[:120])
        if res:
            rec["result_seen"] = True
            if "VERDICT: **FAIL**" in res.group(1) or "VERDICT: FAIL" in res.group(1):
                rec["verdict_fail"] = True

    return {
        "path": path,
        "records": len(recs),
        "bytes": os.path.getsize(path),
        "launches": launches,
        "notes": notes,
        "verdict_fail_literal": raw.count("VERDICT: **FAIL**") + raw.count("VERDICT: FAIL"),
        "replacement_chars": raw.count("�"),
        "raw": raw,
    }


def main():
    scans = [scan(p) for p in FILES]
    print("measured at commit %s" % head_sha())

    for s in scans:
        print("=" * 78)
        print(os.path.basename(s["path"]))
        print("  %d records, %d bytes" % (s["records"], s["bytes"]))
        print("  launch prompts captured : %d" % len(s["launches"]))
        for name in REVIEWERS:
            L = s["launches"].get(name)
            if L is None:
                print("  - %-28s LAUNCH PROMPT ABSENT" % name)
            else:
                print("  - %-28s launch prompt %5d chars" % (name, L["prompt_chars"]))
        print("  completion notifications: %d agent id(s)" % len(s["notes"]))
        for aid, n in sorted(s["notes"].items()):
            print("    %s  status=%s  result_block=%s  verbatim_FAIL=%s"
                  % (aid, "/".join(sorted(n["statuses"])) or "-",
                     n["result_seen"], n["verdict_fail"]))
            for sm in sorted(n["summaries"]):
                print("        summary: %s" % sm)
        print("  literal 'VERDICT: FAIL' occurrences in file : %d"
              % s["verdict_fail_literal"])
        print("  U+FFFD replacement characters in file       : %d"
              % s["replacement_chars"])
        print()

    final = scans[-1]
    n_launch = len(final["launches"])
    n_fail = sum(1 for n in final["notes"].values() if n["verdict_fail"])

    print("=" * 78)
    print("FINDING - against what Q42 and INDEX.md currently claim")
    print("=" * 78)
    print("claim: NIGHT-RUN-FINAL.jsonl holds BOTH reviewers' launch prompts")
    print("       -> launch prompts present: %d of 2   %s"
          % (n_launch, "HOLDS" if n_launch == 2 else "DOES NOT HOLD"))
    print("claim: ...and BOTH their FAIL verdicts verbatim")
    print("       -> verbatim FAIL verdicts present: %d of 2   %s"
          % (n_fail, "HOLDS" if n_fail == 2 else "DOES NOT HOLD"))
    if n_fail < 2:
        print()
        print("       The first reviewer's own notification says why: its status is")
        print("       'stopped', with 'No completion record was found'. It ran across a")
        print("       session restart, so the session never received its report. The")
        print("       report itself is not lost - it is docs/reviews/REVIEW_CH-03.md -")
        print("       but it is NOT in this trajectory, and the file must not be indexed")
        print("       as though it were.")

    # Hard rule 14: zero-occurrence branches print as zeros, and the two counts must
    # be consistent with each other.
    assert n_fail <= n_launch
    return 0


if __name__ == "__main__":
    sys.exit(main())
