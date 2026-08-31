# -*- coding: utf-8 -*-
"""CH-14b - apply the re-verified in-fence corrections, asserting every one landed.

Only findings that `reverify_findings.py` shows still REPRODUCING against the current
files are touched. Hard rule 16: for every edit this asserts the old text is gone AND
the new text is present, and refuses to write anything if a single target does not
match. CH-12 shipped a fix script that stopped reproducing while two files still
claimed "26/26 verified"; this one fails loudly instead.

Hard rule 5, restated for this chunk: no number is DELETED to make a discrepancy go
away. Each corrected table carries a dated note naming what it used to say.

Run:  python docs/evidence/ch14b/apply_ch14b_fixes.py
"""
import io
import sys

# (file, old, new, expected occurrences)
EDITS = []


def edit(path, old, new, n=1):
    EDITS.append((path, old, new, n))


A = "AI-USE.md"

# ---------------------------------------------------------------- SPEC-FIX-2 table
edit(A, "| output | 126,862 |", "| output | 132,805 |")
edit(A, "| input, uncached | 198 |", "| input, uncached | 204 |")
edit(A, "| input, cache write | 250,800 |", "| input, cache write | 252,525 |")
edit(A, "| input, cache read | 10,327,144 |", "| input, cache read | 10,797,901 |")
edit(A, "| **total input** | **10,578,142** |", "| **total input** | **11,050,630** |")
edit(A, "| assistant turns | 99 |", "| assistant turns | 102 |")
edit(A, "| Upper bound — all input at full list, no cache discount | **56.062260** |",
        "| Upper bound — all input at full list, no cache discount | **58.573275** |")
edit(A, "| Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **9.903612** |",
        "| Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **10.298377** |")

# The note that keeps the old figures on the record rather than deleting them.
edit(A,
     """  | **total input** | **11,050,630** |
  | assistant turns | 102 |
""",
     """  | **total input** | **11,050,630** |
  | assistant turns | 102 |

  *Corrected at CH-14b, and the old row is named rather than deleted.* Every row above
  and both cost bases below previously read a **pre-close snapshot** — output 126,862 ·
  uncached 198 · cache write 250,800 · cache read 10,327,144 · total 10,578,142 · 99
  turns · USD 56.062260 / 9.903612 — which the committed artifact this entry cites has
  never carried. `git log -- docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt`
  returns exactly one commit, `28a59e3`, holding the figures now shown. The gap is
  3 turns and 472,488 input tokens: the closing commits the caveat above warns about.
  **The defect was not the snapshot; it was quoting pre-close figures beside a
  post-close artifact and calling that artifact the source.** No result moves — this is
  the coding agent's own usage and is not charged against the USD 18 arms ceiling.
  Re-verification: `docs/evidence/ch14b/reverify-before.txt`.
""")

# ------------------------------------------------------- SPEC-FIX-2 derived figures
edit(A,
     """**This session's total is 10.58 M
  input tokens against SPEC-FIX-1's 42.41 M combined — a 4.0× reduction on a chunk of
  comparable stakes.**""",
     """**This session's total is 11.05 M
  input tokens against SPEC-FIX-1's 42.41 M combined — a 3.8× reduction on a chunk of
  comparable stakes.**""")
edit(A, "**10.58 M — 2.1× over**", "**11.05 M — 2.21× over**")
edit(A, "CH-02 41.58 M", "CH-02 42.21 M")
edit(A,
     """**10.33 M of the 10.58 M is cache
  read**""",
     """**10.80 M of the 11.05 M is cache
  read**""")
edit(A, "across 99 turns", "across 102 turns")

# ---------------------------------------------------------------- CH-02 usage table
edit(A, "| output | 514,051 |", "| output | 515,671 |")
edit(A, "| input, uncached | 478 |", "| input, uncached | 482 |")
edit(A, "| input, cache write | 626,057 |", "| input, cache write | 627,283 |")
edit(A, "| input, cache read | 40,957,406 |", "| input, cache read | 41,584,976 |")
edit(A, "| **total input** | **41,583,941** |", "| **total input** | **42,212,741** |")
edit(A, "| Upper bound — all input at full list, no cache discount | **220.770980** |",
        "| Upper bound — all input at full list, no cache discount | **223.955480** |")
edit(A, "| Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **37.245224** |",
        "| Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **37.607192** |")
edit(A, "- **Measured usage** (239 assistant turns", "- **Measured usage** (241 assistant turns")

edit(A,
     """  | **total input** | **42,212,741** |
""",
     """  | **total input** | **42,212,741** |

  *Corrected at CH-14b.* These rows previously read output 514,051 · uncached 478 ·
  cache write 626,057 · cache read 40,957,406 · total 41,583,941 · 239 turns · USD
  220.770980 / 37.245224 — no row of which appears in the artifact named above, and
  `git log` on that artifact returns one commit, `215052e`. **241 turns is the snapshot
  the artifact holds, and the session did not stop there:** `CH-02.jsonl` was
  deliberately re-exported at `940c0b9` to cover the later commits and now carries
  **268** assistant turns. Both numbers are true of different moments; only one of them
  is what this table's source measured.
""")

# --------------------------------------------------------------- CH-02 wall-clock
edit(A,
     """- **Wall-clock:** first turn 14:43:18 UTC → last 15:30:55 UTC = **47.6 min**, against
  the ~3 h unattended window `prompts/CH-02.md` allowed.""",
     """- **Wall-clock:** measured on the shipped trajectory, first assistant turn
  `2026-08-30T14:43:21.021Z` → last `2026-08-30T18:16:43.050Z` = **213.4 min**, against
  the ~3 h unattended window `prompts/CH-02.md` allowed. **That is over the window, not
  under it.** *Corrected at CH-14b: this read "14:43:18 → 15:30:55 = 47.6 min", which is
  the span of the **first** export (`215052e`, measured 14:43:21.021Z → 15:30:45.240Z =
  47.4 min, 241 turns). The session was re-exported at `940c0b9` and the sentence was
  not. The claim as it stood said the chunk beat its window roughly fourfold; measured
  against the record it cites, it ran past it. The number was corrected in the direction
  that costs the chunk.*""")

# --------------------------------------------------------------- CH-02 comparison
edit(A,
     """but input tokens came out at **41.6 M** against
  CH-01's 41.1 M, i.e. **1.2% higher**, not lower.""",
     """but input tokens came out at **42.2 M** against
  CH-01's 41.1 M, i.e. **2.7% higher**, not lower. *(Corrected at CH-14b from 41.6 M and
  1.2%, which were derived from the superseded table above; CH-01's 41,093,185 does
  match its own artifact.)*""")


def main():
    by_file = {}
    for path, old, new, n in EDITS:
        by_file.setdefault(path, []).append((old, new, n))

    failures = []
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
        if failures:
            continue
        # Hard rule 16, both halves.
        for old, new, n in edits:
            if old in txt and old not in new:
                failures.append("%s: OLD TEXT SURVIVED: %r" % (path, old[:70]))
            if new not in txt:
                failures.append("%s: NEW TEXT ABSENT: %r" % (path, new[:70]))
        if failures:
            continue
        io.open(path, "w", encoding="utf-8", newline="\n").write(txt)
        print("%-14s %d edits applied, %d -> %d bytes"
              % (path, len(edits), len(original), len(txt)))

    if failures:
        print()
        print("NOTHING WAS WRITTEN. %d target(s) did not match:" % len(failures))
        for f in failures:
            print("  " + f)
        return 1

    print()
    print("all %d edits applied; old text gone and new text present for every one"
          % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
