# -*- coding: utf-8 -*-
"""CH-14b - complete SUBMISSION.md and refresh the two counts README.md carries.

The card: "Complete SUBMISSION.md - every row satisfied except the video URL, which
stays TBD until the operator uploads."

Every figure below was measured at commit `0410843` by the command named beside it, in
this session, and none was copied from a prior chunk's cell:

  tracked files / commits   git ls-files | wc -l ; git rev-list --count HEAD
  archive                   git archive --format=zip HEAD, then os.path.getsize
  tests                     python -m pytest -q, on the build machine
  trajectories              os.listdir over docs/trajectories/{build,arms,probe}
  QUESTIONS entries         grep -c '^## Q' QUESTIONS.md
  secret sweep              docs/evidence/secret-scan/scan_history.py, re-run at HEAD

Same discipline as the other CH-14b appliers: occurrence counts asserted, old-gone and
new-present both checked, one mismatch writes nothing.

Run:  python docs/evidence/ch14b/apply_submission_readme.py
"""
import io
import sys

EDITS = []


def edit(path, old, new, n=1):
    EDITS.append((path, old, new, n))


S = "SUBMISSION.md"
R = "README.md"

# ---------------------------------------------------------------- the six-item table
edit(S,
     "| 1 | **Repository** | https://github.com/chinmoypaul8897/instruction-that-wont-execute | "
     "✅ **323 tracked files, 90 commits** at `e01fdfd` (CH-11) |",
     "| 1 | **Repository** | https://github.com/chinmoypaul8897/instruction-that-wont-execute | "
     "✅ **395 tracked files, 126 commits** at `0410843` (CH-14b). *Re-measured every "
     "chunk; it read 323 / 90 at CH-11's `e01fdfd`.* **Private until CH-15**, which owns "
     "flipping it public and proving 200 to an unauthenticated request |")

edit(S,
     "| 2 | **Archive** (the uploaded zip) | `git archive --format=zip HEAD` → **12.51 MB** "
     "against a 50 MB cap | ✅ re-measured at CH-12, `b39cd0c`: **12,513,651 B, 4.00× under "
     "cap** (`docs/evidence/ch12/archive-size.txt`). It read 10,662,339 B / 373 entries at "
     "CH-11's `e01fdfd`; the growth is this chunk's own 2.8 MB session transcript |",
     "| 2 | **Archive** (the uploaded zip) | `git archive --format=zip HEAD` → **22.40 MB** "
     "against a 50 MB cap | ✅ re-measured at CH-14b, `0410843`: **22,399,615 B across 451 "
     "entries, 2.23× under cap**. It read 12,513,651 B at CH-12's `b39cd0c` and 10,662,339 B "
     "at CH-11's `e01fdfd`. **The growth is real and is not trimmed**: each session commits "
     "its own multi-MB transcript, and CH-13B added the video assets. `.githooks/pre-commit` "
     "refuses any commit whose archive exceeds 45 MB and fails closed if it cannot measure |")

edit(S,
     "| 3 | **Tests** | [`tests/`](tests/) — 14 test modules, **353 passed / 26 skipped** in "
     "a clean clone at `7223552`; **351 / 28** from the extracted zip | ✅ green from the "
     "extracted zip |",
     "| 3 | **Tests** | [`tests/`](tests/) — **400 passed / 0 skipped** on the build machine "
     "at `0410843`, where `data/raw/` is present so nothing skips; **353 / 26** in a clean "
     "clone at `7223552`; **351 / 28** from the extracted zip | ✅ green from the extracted "
     "zip. *Three numbers because they are three environments, and the one a judge gets is "
     "the third* |")

edit(S,
     "| 5 | **Agent-use evidence** | [`AI-USE.md`](AI-USE.md) + "
     "[`docs/trajectories/`](docs/trajectories/) — 38 JSONL trajectories at `7223552` + "
     "[`agents/`](agents/) + [`prompts/`](prompts/) | ✅ |",
     "| 5 | **Agent-use evidence** | [`AI-USE.md`](AI-USE.md) + "
     "[`docs/trajectories/`](docs/trajectories/) — **39 JSONL trajectories at `0410843`** + "
     "[`agents/`](agents/) + [`prompts/`](prompts/), **now complete: the six untracked "
     "instruction files were committed at `b6d80a4`** (`QUESTIONS.md` Q41) | ✅ |")

edit(S,
     "| 6 | **Demo video** | **TBD** — unlisted YouTube URL, to be pasted into the "
     "submission form's Video URL field | ⏳ not yet recorded |",
     "| 6 | **Demo video** | **TBD** — unlisted YouTube URL, to be pasted into the "
     "submission form's Video URL field | ⏳ **the one row not satisfied.** CH-13B holds the "
     "recording; the URL lands here, in `README.md` and in the form. Everything else on this "
     "page is ✅ |")

# ------------------------------------------------------------------- item 2 narrative
edit(S,
     """The uploaded artifact is `git archive --format=zip HEAD`. **10,662,339 B = 10.66 MB
against a 50 MB cap** — 4.7× under, with 39.3 MB of headroom. Re-measured at CH-11's
last commit; CH-14a measured 10,613,737 B and `docs/evidence/ch14-size/inventory.md`
10,182,500 B, both at earlier commits.""",
     """The uploaded artifact is `git archive --format=zip HEAD`. **22,399,615 B = 22.40 MB
against a 50 MB cap** — 2.23× under, with 27.6 MB of headroom, measured at CH-14b's
`0410843`. Earlier commits measured 12,513,651 B (CH-12 `b39cd0c`), 10,662,339 B
(CH-11 `e01fdfd`), 10,613,737 B (CH-14a) and 10,182,500 B
(`docs/evidence/ch14-size/inventory.md`). **Five figures, five commits, and the archive
genuinely more than doubled** — session transcripts and the video assets, not drift in
the measurement. The current number is the one to quote and it names its commit.""")

# ---------------------------------------------------------------------- item 5 table
edit(S,
     "| **38 JSONL at `7223552`** — 13 build transcripts (12 sessions; NIGHT-RUN exported "
     "twice), 15 arm bundles carrying every one of the 2,097 logged runs, 10 probe runs. "
     "*The count rises as each session exports its own transcript, which is why it names a "
     "commit.* **Nothing sampled**; the arms are bundled, not one file per run |",
     "| **39 JSONL at `0410843`** — 14 build transcripts (13 sessions; NIGHT-RUN exported "
     "twice), 15 arm bundles carrying every one of the 2,097 logged runs, 10 probe runs. "
     "*The count rises as each session exports its own transcript, which is why it names a "
     "commit.* **Nothing sampled**; the arms are bundled, not one file per run. **No audit "
     "agent has a trajectory here at all** — 0 sidechain records in 12,168, measured at "
     "CH-14b, `QUESTIONS.md` Q40 |")

# ------------------------------------------------------------------------ secret sweep
edit(S,
     "**Secret sweep:** `docs/evidence/secret-scan/scan.txt` — **PASS, 0 findings** across all\n"
     "462 text blobs of all 84 commits plus the 39.4 MB of trajectories that existed at the "
     "scan commit `263ed29`. **At `7223552` the set is 38 files** (byte total in "
     "`docs/evidence/ch12/trajectory-facts.txt`, regenerated each commit) "
     "(`docs/evidence/ch12/trajectory-facts.txt`); the sweep has not been re-run over the "
     "difference, and `CH-14b` is the chunk that does it. `.env` is git-ignored,\nnever "
     "tracked, never committed on any ref.",
     "**Secret sweep: RE-RUN AT CH-14b over the full history, and it is the current one.**\n"
     "`docs/evidence/ch14b/secret-scan-ch14b.txt` — **VERDICT: PASS, 0 findings** across "
     "**649 text blobs of all 126 commits**, 43 trajectory files, 62,155,794 bytes, at "
     "`0410843`. 6 binary blobs were skipped and are counted, not silently dropped; 6 hits "
     "matched a declared exception, each listed with its reason. The earlier run "
     "(`docs/evidence/secret-scan/scan.txt`, 462 blobs / 84 commits at `263ed29`) **is kept, "
     "not replaced** — SUBMISSION.md said *\"CH-14b is the chunk that does it\"*, and this is "
     "it. `.env` is git-ignored, never tracked, never committed on any ref.\n\n"
     "The scan's own stated limitations travel with the verdict rather than behind it: "
     "**regex prefix matching, no entropy analysis**, binary blobs skipped, refs reachable "
     "from `--all` only. It is not gitleaks and its output says so in its header.")

# ---------------------------------------------------------------------- entry counts
edit(S,
     "`QUESTIONS.md` holds **43** entries (`grep -c '^## Q'`; this read 31 until CH-11c, when the",
     "`QUESTIONS.md` holds **46** entries (`grep -c '^## Q'`; this read 31 until CH-11c and 43 until CH-14b, when the")

edit(R,
     "| **Every ambiguity and every ruling** | [QUESTIONS.md](QUESTIONS.md) — **43** entries "
     "(`grep -c '^## Q'`), including our own retractions |",
     "| **Every ambiguity and every ruling** | [QUESTIONS.md](QUESTIONS.md) — **46** entries "
     "(`grep -c '^## Q'`), including our own retractions |")

edit(R,
     "| **Every trajectory, and what to look at in it** | "
     "[`docs/trajectories/INDEX.md`](docs/trajectories/INDEX.md) — 38 files at `7223552`, "
     "with the curation rule published before it was applied |",
     "| **Every trajectory, and what to look at in it** | "
     "[`docs/trajectories/INDEX.md`](docs/trajectories/INDEX.md) — 39 files at `0410843`, "
     "with the curation rule published before it was applied |")


def main():
    by_file = {}
    for path, old, new, n in EDITS:
        by_file.setdefault(path, []).append((old, new, n))

    failures, staged = [], {}
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
        print("%-16s %d edits applied, %d -> %d bytes" % (path, n, len(original), len(txt)))
    print()
    print("all %d edits applied; old text gone and new text present for every one" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
