# -*- coding: utf-8 -*-
"""CH-14b - Q40 and Q42: correct what the three index files say about the audit class.

Q42 asked this chunk to disclose `NIGHT-RUN-FINAL.jsonl` in `docs/trajectories/INDEX.md`
and `AI-USE.md`, naming what it contains: "both CH-03 reviewers, their launch prompts
and their FAIL verdicts verbatim."

Checking it first (hard rule 15) showed the second half does not hold, and that
`INDEX.md` already contradicts itself two lines apart - a header sentence claiming both
verdicts, above a row recording that the first reviewer crashed before producing one.
Measured in `docs/evidence/ch14b/nightrun-contents.txt`: 2 of 2 launch prompts, 1 of 2
verdicts.

Q40 asked whether the agent class is wrong or the trajectory is missing. Measured in
`docs/evidence/ch14b/audit-class-census.txt`: the class is right, the trajectory is
missing, and the class is not evidence-free - which is what the current wording implies.

Same discipline as apply_ch14b_fixes.py: every target's occurrence count is asserted,
old-gone and new-present are both checked, and a single mismatch writes nothing.

Run:  python docs/evidence/ch14b/apply_q40_q42.py
"""
import io
import sys

EDITS = []


def edit(path, old, new, n=1):
    EDITS.append((path, old, new, n))


A = "AI-USE.md"
I = "docs/trajectories/INDEX.md"
S = "docs/trajectories/SELECTION-RULE.md"

CENSUS = "`docs/evidence/ch14b/audit-class-census.txt`"

# ------------------------------------------------------------------ AI-USE.md
edit(A,
     "| **Coding** | fresh Claude Code BUILD sessions that write this repository | "
     "**11 sessions / 12 files** — CH-00, CH-01, CH-02, SPEC-FIX-1, SPEC-FIX-2, "
     "NIGHT-RUN (exported twice), CH-06/CH-08/CH-09, CH-14a, CH-11, CH-11c, CH-12 |",
     "| **Coding** | fresh Claude Code BUILD sessions that write this repository | "
     "**13 sessions / 14 files at `0410843`** — CH-00, CH-01, CH-02, SPEC-FIX-1, "
     "SPEC-FIX-2, NIGHT-RUN (exported twice), CH-06/CH-08/CH-09, CH-14a, CH-11, CH-11c, "
     "CH-12, CH-13A, CH-13B — and **14 sessions / 15 files** once CH-14b exports its own |")

edit(A,
     "| `docs/reviews/`, `docs/evidence/ch11c-sweep/`, `docs/evidence/spec-fix-1/` | "
     "**NO — `QUESTIONS.md` Q40** |",
     "| `docs/reviews/`, `docs/evidence/ch11c-sweep/`, `docs/evidence/spec-fix-1/`, and "
     "**endpoints inside the build transcripts** | **NO, and now measured — "
     "`QUESTIONS.md` Q40.** **0** sidechain records in 12,168 records across 14 "
     "transcripts: no audit agent's own turns are captured anywhere. What ships is the "
     "endpoints — 3 launch prompts, 7 workflow scripts, 2 verdicts and 6 fleet results, "
     "all verbatim. " + CENSUS + " |")

edit(A,
     "**38 trajectory files at `7223552`**, measured by "
     "`docs/evidence/ch12/trajectory_facts.py`;",
     "**39 trajectory files at `0410843`** — 14 build · 15 arms · 10 probe — measured by "
     "`docs/evidence/ch12/trajectory_facts.py`;")

edit(A,
     """**This class has no trajectory file, and that is a gap in deliverable 4 rather than an
omission from this index.** `tools/export_session.py` captures a *session*; a subagent is
not a session, and the `Agent` tool writes each transcript to a temp path outside the
repository. What ships for every fleet is **the launch prompt verbatim inside the parent
build transcript, the final result verbatim in its task-notification, and the runnable
evidence under `docs/reviews/` or `docs/evidence/`** — and for the 21-agent sweep, a
finding-by-finding transcription generated from the journal rather than written by hand.
It is raised as `QUESTIONS.md` **Q40** with the fix costed.""",
     """**This class has no trajectory file, and that is a gap in deliverable 4 rather than an
omission from this index.** `tools/export_session.py` captures a *session*; a subagent is
not a session, and the `Agent` tool writes each transcript to a temp path outside the
repository.

**What ships instead was measured at CH-14b rather than described, because the earlier
description of it was too generous.** Over all 14 build transcripts, 12,168 records
(""" + CENSUS + """):

| | count |
|---|---:|
| **sidechain records — an audit agent's own turns** | **0** |
| single-agent launch prompts, verbatim (3 distinct agents; the night run's two are exported twice) | 5 |
| workflow scripts, verbatim — a fleet's instructions, carrying each subagent's prompt template | 7 |
| completion notifications delivering a result verbatim | 8 |
| of those, a single agent's review VERDICT | 2 |
| of those, a fleet's aggregated structured output | 6 |

**The zero is the finding.** Not one audit agent's intermediate turns exist in this
repository, so no reader can watch one work; what a reader can do is read exactly what
each was asked and exactly what it returned. **Two corrections to the older wording:**
the phrase *"the launch prompt verbatim"* was right for the three single agents and
wrong for the fleets, whose instructions ship as a `Workflow` **script** instead; and
*"the final result verbatim"* holds for 8 of the launches but **not** for the first CH-03
reviewer, which crashed mid-run — see `docs/trajectories/INDEX.md` §3. For the 21-agent
sweep, `ch11c-agent-sweep.md` is a finding-by-finding transcription generated from the
journal rather than written by hand. Raised as `QUESTIONS.md` **Q40**, with the fix
costed and the gap now sized.""")

edit(A,
     """| **total** | **103** | | **6,400,255** measured on three fleets | | | |""",
     """| **total** | **103** | | **6,400,255** measured on three fleets | | | |

**This table is not complete, and the shortfall is named rather than left to be found.**
The census counts **7** workflow launches and **6** delivered fleet results across the
transcripts at `0410843`; six fleets are costed above. Missing are **CH-12's second,
self-auditing fleet of 36** (`STATUS.md`'s CH-12 row: 31 findings raised, 11 refuted, 18
survived, all 31 acted on) and **CH-13B's**, which ran in parallel with this chunk and
whose evidence is outside its fence. Their agent counts are published in `STATUS.md`;
their token cost is **not** measured here and no figure is invented for it. Counting
CH-12's second fleet the class is **139**, which is the number `STATUS.md` uses.
""")

edit(A,
     """operator asleep. Transcript: `docs/trajectories/build/NIGHT-RUN-CHECKPOINT.jsonl`
(1,348 lines, 3.1 MB; the exporter's redaction sweep found **zero** credentials).""",
     """operator asleep. **Exported twice, and both exports ship** —
`docs/trajectories/build/NIGHT-RUN-CHECKPOINT.jsonl` (1,348 lines, 3,123,874 B), a
mid-session snapshot committed to satisfy `CLAUDE.md` duty 6 before the run continued,
and `docs/trajectories/build/NIGHT-RUN-FINAL.jsonl` (1,659 lines, 3,696,750 B), **which
is the complete record and the one to read.** The exporter's redaction sweep found
**zero** credentials in either.

**`NIGHT-RUN-FINAL.jsonl` is the most valuable process evidence in this repository and
until CH-12 it was named nowhere** (`QUESTIONS.md` **Q42**). It holds **both** CH-03
adversarial gate reviewers: their launch prompts verbatim, 5,444 and 5,040 characters,
each opening *"Assume the work is WRONG until proven otherwise"*, and **one of their two
verdicts verbatim** — the round-2 reviewer's `## VERDICT: **FAIL**` arrived inside its
completion notification and is in the file in full. The first reviewer's is **not**: its
own notification reads `<status>stopped</status>`, it crashed before delivering a report,
and `docs/reviews/REVIEW_CH-03.md` says so in its own header. *Q42 and this file both
said "their FAIL verdicts verbatim", plural. Measured at CH-14b: 2 of 2 prompts, **1** of
2 verdicts — `docs/evidence/ch14b/nightrun-contents.txt`.*""")

# ------------------------------------------------------------------ INDEX.md
edit(I,
     """It contains **both** CH-03 adversarial reviewers, launched as background subagents with
zero shared context, their **launch prompts verbatim** and their **verdicts verbatim**:""",
     """It contains **both** CH-03 adversarial reviewers, launched as background subagents with
zero shared context, and **both launch prompts verbatim** — 5,444 and 5,040 characters.
**One of the two verdicts is in the file verbatim, not both**, and the row below says
which. *Corrected at CH-14b: this sentence read "their verdicts verbatim", which
contradicted the very next row of its own table. Measured 2 of 2 prompts and 1 of 2
verdicts, `docs/evidence/ch14b/nightrun-contents.txt`.*""")

edit(I,
     """**Why there is no JSONL.** `tools/export_session.py` captures a *session*; a subagent is
not a session. Its per-agent records live in the Claude Code workflow journal outside
this repository, and the `Agent` tool writes each transcript to a temp path that is
never exported. **What does ship, for every fleet: the launch prompt verbatim inside
the parent build transcript, the final result verbatim in the task-notification, and
the runnable evidence under `docs/reviews/` or `docs/evidence/`.** For the 21-agent
sweep, `ch11c-agent-sweep.md` is generated from the journal line by line, so no finding
is paraphrased, dropped or re-scored.""",
     """**Why there is no JSONL.** `tools/export_session.py` captures a *session*; a subagent is
not a session. Its per-agent records live in the Claude Code workflow journal outside
this repository, and the `Agent` tool writes each transcript to a temp path that is
never exported.

**What does ship was counted at CH-14b rather than characterised** — across all 14 build
transcripts, 12,168 records (""" + CENSUS + """): **0** sidechain records · 5 single-agent
launch prompts, 3 distinct · 7 workflow scripts, which are a fleet's instructions · 8
completion notifications carrying a result, of which 2 are a single agent's verdict and 6
a fleet's aggregated output. **The zero is the point:** no audit agent's intermediate
turns exist here at all. What a reader gets is both endpoints — what each agent was asked
and what it returned — for every launch but one. For the 21-agent sweep,
`ch11c-agent-sweep.md` is generated from the journal line by line, so no finding is
paraphrased, dropped or re-scored.""")

# ------------------------------------------------------------ SELECTION-RULE.md
edit(S,
     """| **adversarial audits** | **not JSONL.** These are subagent fleets spawned *inside* a coding session; their per-agent records live in the workflow journal, which is outside the repository, and what is committed is the **verbatim** transcription of each agent's finding | `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md`, `docs/reviews/`, `docs/evidence/spec-fix-1/` |""",
     """| **adversarial audits** | **not JSONL.** These are subagents and subagent fleets spawned *inside* a coding session; their per-agent records live in the workflow journal, which is outside the repository. What is committed is (a) their **instructions** verbatim inside the parent build transcript — 5 single-agent launch prompts and 7 workflow scripts — (b) their **results** verbatim in 8 completion notifications, and (c) the transcription of each agent's finding | `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md`, `docs/reviews/`, `docs/evidence/spec-fix-1/`, and `docs/trajectories/build/*.jsonl` |""")

edit(S,
     """**The gap is real and is not repaired by wording.** The adversarial-audit class is the
one class whose agents cannot be replayed from `docs/trajectories/`, and
`AI-USE.md` says where each fleet's evidence is instead. It is raised as
`QUESTIONS.md` **Q40**.""",
     """**The gap is real and is not repaired by wording — and CH-14b sized it rather than
restating it.** `QUESTIONS.md` **Q40** asked whether the class was named wrongly or the
trajectory was simply missing. Reading the artifacts answers it: **the class is right and
the trajectory is missing.** Across all 14 build transcripts, 12,168 records, there are
**0** sidechain records — not one audit agent's own turns are captured anywhere, so not
one can be replayed. What is captured is both **endpoints**, and those are not nothing:
12 sets of instructions and 8 delivered results, verbatim, listed in the row above.

**So T1 is not corrected, and it is not deleted.** The clause names a class that exists,
did the work the project leans on hardest, and has committed evidence at both ends of
every agent. It has no trajectory, which is what T1's own column already says. The
measurement is """ + CENSUS + """; the one thing a reader cannot do is watch an audit
agent work, and that stays true until the workflow journals are exported.""")


def main():
    by_file = {}
    for path, old, new, n in EDITS:
        by_file.setdefault(path, []).append((old, new, n))

    failures = []
    staged = {}
    for path, edits in by_file.items():
        txt = io.open(path, encoding="utf-8").read()
        original = txt
        for old, new, n in edits:
            found = txt.count(old)
            if found != n:
                failures.append("%s: expected %d occurrence(s) of %r, found %d"
                                % (path, n, old[:70], found))
                continue
            txt = txt.replace(old, new)
        for old, new, n in edits:
            if old in txt and old not in new:
                failures.append("%s: OLD TEXT SURVIVED: %r" % (path, old[:70]))
            if new not in txt:
                failures.append("%s: NEW TEXT ABSENT: %r" % (path, new[:70]))
        staged[path] = (original, txt, len(edits))

    if failures:
        print("NOTHING WAS WRITTEN. %d target(s) did not match:" % len(failures))
        for f in failures:
            print("  " + f)
        return 1

    for path, (original, txt, n) in staged.items():
        io.open(path, "w", encoding="utf-8", newline="\n").write(txt)
        print("%-34s %d edits applied, %d -> %d bytes" % (path, n, len(original), len(txt)))

    print()
    print("all %d edits applied; old text gone and new text present for every one"
          % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
