#!/usr/bin/env python3
"""CH-12 - apply the standing CH-11c sweep findings whose fix is a one-line factual
correction inside this chunk's fence, and prove each one landed.

WHY THIS IS A SCRIPT AND NOT A SEQUENCE OF HAND EDITS. `CLAUDE.md` hard rule 16 was
written because a batch of hand edits silently failed here once: the replace targets
did not match, nothing errored, and two shipping files ended up disagreeing. So every
replacement below is checked three ways and the run fails loudly if any check fails:

  1. the OLD string occurs EXACTLY ONCE in the file before the edit
     (or zero times AND the NEW string is already present - the idempotent case)
  2. after the edit the OLD string occurs ZERO times
  3. after the edit the NEW string occurs EXACTLY ONCE

Line endings are preserved byte-for-byte: the files are read and written as BYTES,
never through text mode. `QUESTIONS.md`, `AI-USE.md`, `README.md`, `REPRODUCE.md`,
`STATUS.md` and `SUBMISSION.md` are 100% CRLF; `PROVENANCE.md` is 100% LF. A single
replacement written with the wrong newline would silently fail to match, which is
exactly failure mode 1 above.

EVERY `new` VALUE BELOW WAS MEASURED IN THIS SESSION, not copied from a report. The
finding that prompted it is named in `why`; the command that established the new value
is in `checked`.

NOTE, added at CH-12 after this chunk's own adversarial audit caught it: FOUR of the
entries below were superseded by CH-12's own LATER commits - the AI-USE agent-class
table was rewritten wholesale, and the trajectory count moved 36 -> 37 when this
chunk's transcript was exported. Their NEW values are therefore the values that
SHIPPED, not the intermediate ones this script first wrote. Without that repair the
script printed `4 FAIL, NOTHING WAS WRITTEN` and exited 1, and the shipped claim
"26/26 verified on disk" described a state that had existed for four commits and was
gone. **A verification script that stops reproducing is not evidence.** Its re-run
output is committed at `docs/evidence/ch12/sweep-fixes-rerun.txt`.

Run:  python docs/evidence/ch12/apply_sweep_fixes.py
Idempotent: running it twice is a no-op and reports every fix as ALREADY-APPLIED.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]

# Each entry: (file, sweep-line, severity, old, new, why, checked)
FIXES: list[tuple[str, str, str, str, str, str, str]] = [

    # ---------------------------------------------------------------- AI-USE.md
    ("AI-USE.md", "line 18", "material",
     "**6** — CH-00, CH-01, CH-02, SPEC-FIX-1, SPEC-FIX-2, NIGHT-RUN",
     "**11 sessions / 12 files** — CH-00,",
     "the Coding class said 6 sessions; the file's own session log carries 10",
     "grep -c '^### ' AI-USE.md -> 10; ls docs/trajectories/build/*.jsonl -> 11 files "
     "(NIGHT-RUN was exported twice: NIGHT-RUN-CHECKPOINT and NIGHT-RUN-FINAL)"),

    ("AI-USE.md", "line 19", "material",
     "| **12** | `docs/reviews/` for the verdicts",
     "| **103** | `docs/reviews/`, `docs/evidence/ch11c-sweep/`, "
     "`docs/evidence/spec-fix-1/` |",
     "the Adversarial-audit class total was stale by 74 against the file's own "
     "disclosures",
     "workflow journals counted on disk: wf_5260a72c-01a 10 results (SPEC-FIX-1), "
     "wf_44b0dd6c-5e5 52 (CH-11), wf_74534735-795 21 (CH-11c); plus NIGHT-RUN's two "
     "CH-03 gate reviewers and CH-06's one CH-04 gate reviewer = 10+52+21+2+1 = 86"),

    ("AI-USE.md", "line 20", "material",
     "**1028** logged runs across B0, B0-agent and the sonnet subset",
     "**2,097** logged runs across every evaluation arm "
     "(2,107 ledger rows less the 10 model-id probe calls)",
     "the Solution class is defined as 'the evaluation arms' but counted only four of "
     "them, omitting every A1 arm and B0prime",
     "Counter over cost_ledger.csv arm column: 2,107 rows total, probe-model-id 10, "
     "evaluation-arm rows 2,097"),

    ("AI-USE.md", "line 36", "material",
     "every evaluation arm. 951 logged calls",
     "every evaluation arm. 2,020 logged calls",
     "951 is the NIGHT-RUN session subtotal (B0 474 + B0-agent 474 + probe 3) reused "
     "as a project-level total",
     "Counter over cost_ledger.csv model column: claude-haiku-4-5-20251001 -> 2,020"),

    ("AI-USE.md", "line 78", "cosmetic",
     "Q5 and Q7 in this chunk were both",
     "Q5 and Q7 in CH-00 were both",
     "'this chunk' has no referent in a project-level section",
     "QUESTIONS.md Q5 and Q7 both read 'Raised: CH-00, 2026-08-30.'"),

    ("AI-USE.md", "line 255", "material",
     "the zip is 10.24 MB.",
     "the zip is 10.18 MB at `bc99ef4` "
     "(`docs/evidence/ch14-size/inventory.md`; 11.74 MB at CH-12).",
     "10.24 MB appears in no artifact; the committed measurements are 10.18 and 10.61",
     "inventory.md: 'git archive --format=zip HEAD : 10,182,500 B = 10.18 MB'; "
     "re-measured at CH-12: git archive HEAD = 11,736,711 B = 11.74 MB"),

    ("AI-USE.md", "line 505", "material",
     "(644 lines, 1,574,519 B;",
     "(709 lines, 1,689,144 B;",
     "the CH-02 session was deliberately re-exported and this line was never refreshed",
     "wc -lc docs/trajectories/build/CH-02.jsonl -> 709 1689144; "
     "git show 215052e:<same> -> 644 1574519"),

    ("AI-USE.md", "line 598", "cosmetic",
     "about **1.6×** CH-00 rather than a fraction",
     "about **1.89×** CH-00's measured 21.72 M rather than a fraction",
     "1.6x is the ratio to the prompt's ~26 M estimate, not to CH-00's measured total",
     "ch00-session-cost.txt TOTAL INPUT 21,724,778; ch01-session-cost.txt 41,093,185; "
     "41093185/21724778 = 1.8915"),

    # ------------------------------------------------------------ PROVENANCE.md
    ("PROVENANCE.md", "line 26", "material",
     "- `scraper/` — Playwright recon scripts written to read the **public** "
     "HackerEarth challenge page.",
     "- `scraper/recon.cjs`, `sections.cjs`, `sections2.cjs`, `mapimg.cjs`, "
     "`slice.cjs` — Playwright recon scripts written to read the **public** "
     "HackerEarth challenge page, with their npm tooling (`package.json`, "
     "`package-lock.json`, `node_modules/`). That is **8 of `scraper/`'s 43 "
     "entries**. **The other 35 were written AFTER kickoff** — 2026-08-29, "
     "03:13–06:21 UTC, twelve to fifteen hours past the 15:00 UTC line — "
     "and they are `portfolio.cjs`, `work.cjs`, `li.cjs`, `hn.cjs`, `he.mjs`, "
     "`rd.mjs`, `rd2.mjs` and 28 page dumps, which read the **operator's own** "
     "portfolio, LinkedIn and blog into `context/me/` and public commentary on the "
     "challenge into `rd_*.txt`. **Corrected at CH-12**, because dating all 43 to "
     "before kickoff is exactly the kind of claim ground rule 02 exists to make "
     "checkable. None of the 35 is problem work, none is reused, and `scraper/` is "
     "git-ignored in its entirety — so the substance of this section is "
     "unchanged and only its dating was wrong.",
     "PROVENANCE section 2 dated all of scraper/ to 2026-08-27 ~21:45 UTC; 35 of its "
     "43 entries were written after kickoff and read the operator dossier, not the "
     "challenge page",
     "mtime census of scraper/ against the 2026-08-28T15:00Z kickoff: 8 pre "
     "(recon/sections/sections2/mapimg/slice.cjs + package.json + package-lock.json + "
     "node_modules), 35 post, all 2026-08-29T03:13:12Z-06:21:37Z; grep of OUT= shows "
     "the five pre-kickoff scripts target hackerearth.com -> context/, the post-kickoff "
     "ones target the operator's sites -> context/me/"),

    ("PROVENANCE.md", "line 43", "material",
     "| `context/03-IDEA-REVIEW-VERDICT.md` | 15 agents attacking the first candidate. "
     "It died. |",
     "| `context/03-IDEA-REVIEW-VERDICT.md` | 13 agents attacking the first candidate "
     "— 5 hostile critiques, 2 alternative passes, 6 rubric scorings, counted "
     "from `context/03b-review-raw.json`. It died. |",
     "the file was credited with 15 agents; its own committed dump accounts for 13",
     "json over context/03b-review-raw.json: critiques 5, alternatives 2, scores 6 = 13"),

    ("PROVENANCE.md", "line 93", "cosmetic",
     "which was **WITHDRAWN** as a harness defect — `QUESTIONS.md` Q19.",
     "which was **WITHDRAWN** as a harness defect — the architect's ruling "
     "*\"MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31\"*, recorded in "
     "`QUESTIONS.md` under **ARCHITECT RULINGS — 2026-08-31** (not Q19, which is "
     "the CH-03 escalation).",
     "Q19 is the CH-03 escalation ruling and never mentions sonnet; the withdrawal is "
     "an unnumbered architect ruling elsewhere in the file",
     "grep -n '^## Q19' QUESTIONS.md -> 983 'CH-03 FAILED review TWICE'; "
     "grep -n 'MODEL-SENSITIVITY CHECK' QUESTIONS.md -> 1110, under the "
     "'ARCHITECT RULINGS' heading at 1086"),

    # --------------------------------------------------------------- README.md
    ("README.md", "line 67", "material",
     "most labelled items have no extractable quoted anchor at all",
     "41 of 82 labelled items have no extractable quoted anchor on any instruction "
     "(118 of 208 instructions carry none; `data/evalset/items.jsonl`)",
     "the claim carried no evidence path and glossed a pilot-pool figure; on the "
     "shipped set it is exactly 50.0%, which is not 'most'",
     "over data/evalset/items.jsonl: 41 of 82 items have no instruction with a "
     "non-empty anchor; 118 of 208 instructions carry none"),

    ("README.md", "line 505", "material",
     "Tier 1 offline in 15 s for USD 0",
     "Tier 1 offline in 14.42 s and 25.84 s on two runs for USD 0",
     "the index published one runtime where the artifact it cites publishes two and "
     "says in bold that publishing one would be a claim rather than a measurement",
     "REPRODUCE.md's timing table: | **total** | **14.42 s** | **25.84 s** |"),

    # ------------------------------------------------------------- REPRODUCE.md
    ("REPRODUCE.md", "line 176", "material",
     "It is the only arm in the packet not at temperature 0.",
     "It is the only arm in the primary matrix not at temperature 0.",
     "false as written: the two withdrawn sonnet arms also ran off 0, because "
     "claude-sonnet-5 rejects the parameter (HTTP 400, measured)",
     "input.temperature across docs/trajectories/arms/*.jsonl: every haiku arm 0.0 "
     "except B0prime 1.0; B0-sonnet-rep1 and B0-agent-sonnet-rep1 carry None. "
     "'primary matrix' is the phrase the project already ruled and shipped at "
     "README.md and QUESTIONS.md"),

    # ---------------------------------------------------------------- STATUS.md
    ("STATUS.md", "line 23", "cosmetic",
     "sonnet-5 **−30.0 pp** — a flag, not a finding",
     "sonnet-5 **−30.0 pp** — a subset since **WITHDRAWN** as a harness "
     "defect (`QUESTIONS.md`, ARCHITECT RULINGS 2026-08-31), and even before that a "
     "flag, not a finding",
     "the ruling requires the withdrawn label at every citation of these figures",
     "checkpoint-result.txt reproduces both figures; QUESTIONS.md's sensitivity row "
     "says 'The -sonnet rows are WITHDRAWN. No sensitivity claim appears.'"),

    ("STATUS.md", "line 30", "material",
     "a digit transposition, and the only occurrence of that value anywhere in the "
     "repository",
     "not a transposition — 0.4421 is A1 rep 1's own single-rep McNemar, "
     "superseded by the 3-rep aggregate — and not the only occurrence either: "
     "`docs/evidence/ch09-removed/leakage-result.txt` still publishes p = 0.4421 as "
     "the live McNemar of removed experiment #1",
     "both halves of the parenthetical were false",
     "leakage-result.txt line 27: 'McNemar exact two-sided p = 0.4421 "
     "(b=11 c=16 discordant=27)' - a live published statistic, and 0.4421 also appears "
     "at README.md and PROGRESS.md"),

    ("STATUS.md", "line 32", "material",
     "nearly twice as often (45 vs 24)",
     "nearly twice as often (46 vs 24)",
     "the generating artifact says 46, not 45",
     "docs/evidence/ch06-a1/a1-result.txt LAYER 2 table: "
     "'A1 128 75 53 41.4% 46 7' and 'A1-iter1 124 89 35 28.2% 24 11'"),

    ("STATUS.md", "line 39", "material",
     "the zip is 10.24 MB, 4.9× under cap",
     "the zip is 10.18 MB at `bc99ef4`, 4.9× under cap",
     "10.24 MB appears in no artifact; 10.18 MB is the figure in inventory.md and in "
     "the Q27 this same line cites, and it is the one that makes the adjacent 4.9x true",
     "docs/evidence/ch14-size/inventory.md: 10,182,500 B = 10.18 MB; "
     "50e6/10182500 = 4.91"),

    # ------------------------------------------------------------ SUBMISSION.md
    ("SUBMISSION.md", "line 21", "cosmetic",
     "34 JSONL trajectories",
     "37 JSONL trajectories",
     "stale by two: CH-11.jsonl and CH-11c.jsonl were exported after this was written",
     "git ls-files docs/trajectories | grep -c '\\.jsonl$' -> 36 "
     "(arms 15, build 11, probe 10)"),

    ("SUBMISSION.md", "line 63", "cosmetic",
     "34 files, complete, nothing sampled",
     "37 files, complete, nothing sampled",
     "the same stale count, repeated in the agent-use table",
     "git ls-files docs/trajectories | grep -c '\\.jsonl$' -> 36"),

    ("SUBMISSION.md", "line 33", "cosmetic",
     "The repository is 63.62 MB uncompressed.",
     "The tracked tree at `e01fdfd` is 63.62 MB uncompressed.",
     "63.62 MB is the tracked-tree total at one commit, not 'the repository', and the "
     "line cited no path; every other figure in the paragraph is measured at e01fdfd",
     "git ls-tree -r -l e01fdfd -> 323 entries, 63,615,283 B = 63.62 MB"),

    # ------------------------------------------------------------- QUESTIONS.md
    ("QUESTIONS.md", "line 807", "cosmetic",
     "Three excluded documents have attribution **1.0000** - perfect - and fail purely on",
     "Four excluded documents have attribution **1.0000** - perfect - and fail purely on",
     "the artifact Q16 cites says four, and names a fourth document",
     "docs/evidence/ch03-evalset/floor-decomposition.txt: "
     "'attribution == 1.0000 and yet excluded : 4', listing 2024-31513 as well"),

    ("QUESTIONS.md", "line 808", "cosmetic",
     "parse rate (`2011-12279` 0.4167, `2020-17549` 0.6111, `2024-30575` 0.2500).",
     "parse rate (`2024-31513` 0.0000, `2011-12279` 0.4167, `2020-17549` 0.6111, "
     "`2024-30575` 0.2500).",
     "the fourth document was missing from the enumeration",
     "floor-decomposition.txt: '2024-31513 completeness 0.0000 attribution 1.0000 "
     "parse 0.0000 elements 3'"),

    ("QUESTIONS.md", "line 1249", "cosmetic",
     "Reading (b) is demanding, and is 0.85 higher than the",
     "Reading (b) is demanding, and is 0.0485 higher than the",
     "a difference of 0.85 between two accuracies both below 0.86 is impossible; "
     "the gap is 0.0485",
     "the same entry's own table: A1 > 0.6585 + 0.20 = 0.8585; 0.8585 - 0.81 = 0.0485"),

    ("QUESTIONS.md", "line 1744", "cosmetic",
     "| **Wasted spend** | **~USD 1.43** of the 18.00 ceiling |",
     "| **Wasted spend** | **~USD 1.41** of the 18.00 ceiling |",
     "1.43 does not reproduce from the ledger by any route",
     "cost_ledger.csv, scoped as Q26 scopes it (A1-minus-tool + B0prime, the two arms "
     "run twice): second-occurrence sum 1.4081; half of both arms' totals "
     "(1.4175 + 1.3988)/2 = 1.4082"),

    ("QUESTIONS.md", "line 1796", "cosmetic",
     "3. The **~USD 1.43** is spent and is not recoverable; remaining headroom against the",
     "3. The **~USD 1.41** is spent and is not recoverable; remaining headroom against the",
     "the same figure, repeated in the same entry - fixing one alone would make the "
     "entry contradict itself",
     "same computation as the row above"),
]


#: Corrections that a LATER CH-12 commit superseded with a further, also-correct edit.
#: (file, sweep-line) -> a substring that must be present for the correction to be in
#: force in its superseding form. Without this the script reports FAIL on text that is
#: not wrong but *more* right, which would be a verification script lying in the strict
#: direction. Each entry names what replaced it and why.
SUPERSEDED = {
    ("AI-USE.md", "line 255"):
        ("the zip is 10.18 MB at `bc99ef4`",
         "the self-audit showed the appended '11.74 MB at CH-12' was the archive at "
         "CH-12's STARTING point, not at CH-12; re-measured to 12.51 MB at b39cd0c"),
    ("PROVENANCE.md", "line 26"):
        ("**8 of `scraper/`'s 43 entries**",
         "the self-audit found 4 of the 35 post-kickoff entries re-read the public "
         "challenge page rather than the operator dossier; the bullet now says so, and "
         "the span was widened from 'twelve to fifteen' to the measured 12.2-15.4 h"),
    ("STATUS.md", "line 39"):
        ("the zip *was* 10.18 MB at `bc99ef4`",
         "the self-audit objected that a past figure was stated in the present tense; "
         "the cell now dates it and adds the re-measured 12.51 MB"),
    ("SUBMISSION.md", "line 63"):
        ("12 build transcripts (11 sessions; NIGHT-RUN exported twice)",
         "the count went 34 -> 36 -> 37 as this chunk exported its own transcript, and "
         "the self-audit then killed the row's 'one JSONL per agent run' predicate, "
         "which this chunk's own evidence refutes"),
}

def main() -> int:
    print("CH-12 - APPLYING THE IN-FENCE ONE-LINE SWEEP FIXES")
    print("=" * 90)
    print(f"{len(FIXES)} replacements across "
          f"{len({f[0] for f in FIXES})} files\n")

    applied = already = superseded = 0
    failures: list[str] = []
    contents: dict[str, bytes] = {}

    for path, sweep_line, severity, old, new, why, checked in FIXES:
        p = ROOT / path
        if path not in contents:
            contents[path] = p.read_bytes()
        blob = contents[path]

        # Encode with the file's own newline convention. Both OLD and NEW here are
        # single-line, so the only risk is a stray \n, which we forbid outright.
        assert "\n" not in old and "\n" not in new, f"{path}: multi-line replacement"
        old_b, new_b = old.encode("utf-8"), new.encode("utf-8")

        n_old, n_new = blob.count(old_b), blob.count(new_b)

        if n_old == 0 and n_new >= 1:
            already += 1
            print(f"  ALREADY  {path:<15} {sweep_line:<11} {severity:<9} "
                  f"(new text present {n_new}x)")
            continue

        sup = SUPERSEDED.get((path, sweep_line))
        if n_old == 0 and sup and sup[0].encode("utf-8") in blob:
            superseded += 1
            print(f"  SUPERSEDED {path:<13} {sweep_line:<11} {severity:<9} {sup[1][:58]}")
            continue

        if n_old != 1:
            failures.append(f"{path} {sweep_line}: OLD occurs {n_old} times, expected 1"
                            f"  OLD={old[:70]!r}")
            print(f"  FAIL     {path:<15} {sweep_line:<11} OLD occurs {n_old} times")
            continue

        blob = blob.replace(old_b, new_b, 1)

        # hard rule 16: assert the new text is present AND the old text is gone
        if blob.count(old_b) != 0:
            failures.append(f"{path} {sweep_line}: OLD survived the replacement")
            continue
        if blob.count(new_b) != 1:
            failures.append(f"{path} {sweep_line}: NEW occurs "
                            f"{blob.count(new_b)} times after the replacement")
            continue

        contents[path] = blob
        applied += 1
        print(f"  APPLIED  {path:<15} {sweep_line:<11} {severity:<9} {why[:60]}")

    if failures:
        print("\nFAILURES - NOTHING WAS WRITTEN:")
        for f in failures:
            print("  " + f)
        return 1

    for path, blob in contents.items():
        (ROOT / path).write_bytes(blob)

    print("-" * 90)
    print(f"applied         : {applied}")
    print(f"already applied : {already}")
    print(f"superseded      : {superseded}  (a later CH-12 commit corrected it further)")
    assert applied + already + superseded == len(FIXES), "success + failure != n"
    print(f"applied + already + superseded == n : {applied} + {already} + "
          f"{superseded} == {len(FIXES)}  OK")

    # Post-write re-verification, reading the files back off disk.
    print("\nRE-VERIFICATION, reading the files back from disk")
    bad = 0
    for path, sweep_line, _sev, old, new, _why, _chk in FIXES:
        blob = (ROOT / path).read_bytes()
        sup = SUPERSEDED.get((path, sweep_line))
        ok = blob.count(old.encode()) == 0 and (
            blob.count(new.encode()) == 1
            or (sup is not None and sup[0].encode("utf-8") in blob))
        if not ok:
            bad += 1
            print(f"  MISMATCH {path} {sweep_line}: "
                  f"old={blob.count(old.encode())} new={blob.count(new.encode())}")
    print(f"  {len(FIXES) - bad} of {len(FIXES)} in force on disk; {bad} mismatched")

    # Line endings must be unchanged.
    print("\nLINE ENDINGS - unchanged by construction (bytes in, bytes out)")
    for path in sorted(contents):
        blob = (ROOT / path).read_bytes()
        crlf = blob.count(b"\r\n")
        lf = blob.count(b"\n") - crlf
        print(f"  {path:<16} CRLF {crlf:<6} bare-LF {lf}")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
