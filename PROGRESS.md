# PROGRESS.md — session journal

**Newest entry on top.** This file is the source of the Improvement Changelog.
Chat history is not a record; if it matters it lives here.

Fixed template per entry: **scope · files · tests · decisions · questions · gate ·
status-ledger · state-for-next-session.**

When sessions run in parallel (Phase 3 only), a build session writes
`docs/progress/<CHUNK-ID>.md` instead and the architect folds it in here.

---

## CH-00 · 2026-08-30 · BUILD · Claude Code, `claude-opus-5` · ungated

### Scope
Repository initialisation, the canonical file set, the run logger with cost and
time accounting, the build-session trajectory exporter, and the pre-commit guard.
No harvest code, no AMDPAR parsing, no scorer, no eval logic, no thresholds in
`GOOD.md` — all explicitly fenced out and none written.

### Files
Created: `.gitignore` · `.gitattributes` · `STATUS.md` · `PROGRESS.md` ·
`QUESTIONS.md` · `CHANGELOG.md` · `AI-USE.md` · `GOOD.md` · `src/runlog.py` ·
`tests/test_runlog.py` · `tools/export_session.py` · `.githooks/pre-commit` ·
`docs/evidence/ch00-goldens.md` · `docs/evidence/ch00_guard_probe.py` +
`ch00-guard-probe.txt` · `docs/evidence/ch00_session_cost.py` +
`ch00-session-cost.txt` · `docs/evidence/runs/README.md` and the CH-00 demo run ·
`docs/trajectories/build/CH-00.jsonl` · directory scaffolding for
`docs/progress/`, `agents/`, `prompts/design/`, `docs/process/superseded/`.

Moved, not deleted: `DIVERGENT-RESEARCH-PROMPT.md` and `KILL-TEST-PROMPT.md` →
`prompts/design/` (they are the agent instructions that produced `context/06` and
`context/07`, both of which ship — deliverable 4 asks a trajectory be followable
*from the agent instructions* to the result, and shipping the outputs while
deleting the instructions fails exactly that half). `BUILD-PHASE-1-PROMPT.md` →
`docs/process/superseded/` (contradicts `plan.md`; out of the root so no build
session reads it as current, still in the repo because `PROVENANCE.md` cites it).

Edited under explicit operator ruling: `context/09-COMPLIANCE-AUDIT.md` and
`context/09b-audit-raw.json`, one PII substitution each. Nothing else under
`context/` was touched.

### Tests
`python -m pytest tests/ -q` → **22 passed, 0 failed, 0 skipped.**

The suite was committed **red** in `59dee06` (`ModuleNotFoundError: No module
named 'runlog'`) and turned green by `3b6d22b`. Both states are in the history, so
hard rule 4's ordering is provable from git rather than asserted in prose.

Goldens hand-computed in `docs/evidence/ch00-goldens.md`, then cross-checked by a
**third independent route** — exact `fractions.Fraction` arithmetic, no Decimal, no
project code. Hand doc, Fractions and implementation agree to 6 dp on all four
money goldens.

`docs/evidence/ch00-guard-probe.txt` → **16/16.** Every case feeds a guard
something it must refuse and asserts the refusal: operator phone, operator email,
Anthropic key, AWS key id, a 26 MB blob, and a missing pattern source (fail
closed). Plus a clean-file case so a guard that always fails cannot pass, and a
negative control proving ordinary prose survives untouched.

The hook's first live act was to refuse a commit of the probe's own source: it
found an AKIA-shaped token there and was right to. The literal is now assembled
from two halves at runtime so the probe still tests the identical string. Adding
an allowlist would have been weakening a guard to get it green (hard rule 5).

### Decisions
**Class B — implementation choices inside spec, recorded for review:**

1. **Money is `Decimal` end to end**, quantised to 6 dp ROUND_HALF_UP. Binary float
   for currency is a defect. The ledger carries the exact 6-dp string; the JSONL
   carries both a float and `imputed_usd_exact`.
2. **`delivery` field** — `standard` / `batch` (50%, per Q1) / `subscription`. Q1
   mandates the Batches API, so the halving has to live in the logger or every
   later cost number is 2x wrong. `subscription` imputes at full list and flags
   `cost_is_imputed` — "impute and say so".
3. **`est_usd` per run**, default USD 0.05, for the ceiling check. The spec says
   refuse *before* a run that would cross USD 18, and at `__enter__` no token count
   exists yet, so the projection needs an estimate. 0.05 is ~7x Q1's measured
   ~$0.0072/call — deliberately conservative, overridable per run.
4. **Aborted runs record `imputed_usd: null` and an EMPTY ledger cell**, never 0.
   "Unknown" and "free" are different claims and must not share an encoding.
   `cumulative_usd()` excludes them and `unknown_cost_runs()` counts them, so an
   unknown can never silently pass as free.
5. **A finished run reporting 0 input AND 0 output tokens raises `ZeroCostRun`.**
   A completed model call always consumes input tokens; zero means the caller never
   wired usage through, and a silent $0 would corrupt every cost-per-task figure.
6. **Injectable clock and UTC stamp** (`_clock`, `_utc`) so the suite asserts an
   exact `wall_clock_s` rather than `> 0`. Hard rule 8's purity constraint binds the
   scorer and resolver, not the logger, whose job is to measure the clock.
7. **PII patterns are never stored in the repository.** The exporter and the hook
   read literals from, in order, `$MICRO1_PII_PATTERNS` → `~/.config/micro1/
   pii_patterns.txt` → the git-ignored `context/02-ABOUT-ME.md`, sharing one source
   order so they cannot disagree. A file that lists the value in order to remove it
   is a new copy of the leak. **No `.gitignore` line was added**, because the
   prompt fixed that file's contents exactly.
8. **The hook fails closed** when no pattern source exists. A sweep that cannot find
   its patterns and passes anyway is the precise failure this project exists to
   expose. `--no-verify` remains as a visible, logged escape.
9. **CSV written with `lineterminator="\n"`** and JSONL with `newline="\n"`, so
   artifacts are byte-identical across platforms under `* -text` (hard rule 9).

**Class C — cosmetic:** default branch `main`; commit messages carry reasoning
because they are read by reviewers who have zero shared context.

**Scope-fence note, declared rather than quietly taken.** The fence names
`docs/evidence/runs/`. Rule 14 requires every data claim to ship its generating
script and committed output, and `PROCESS.md` §3 makes `docs/evidence/` canonical, so
five evidence artifacts were written to `docs/evidence/` itself rather than to the
`runs/` subdirectory, where they would be miscategorised as run records. Flagged
here for the architect; trivially movable if ruled otherwise.

**Not done, deliberately:** no test file for `tools/export_session.py`. The fence
names `tests/test_runlog.py` and no other test path. Its behaviour is instead proved
by `docs/evidence/ch00_guard_probe.py`, which lives inside `docs/evidence/`. If the
architect wants it in the suite, that is a one-line move at the next chunk.

### Questions
Raised and recorded: **Q4** (the prompt contradicts itself about whether the design
prompts are staged at step 4b — closed by convergence, both readings give a
byte-identical result), **Q5** (the safety rider makes `context/` read-only while
step 5 requires editing two files in it — **put to the operator, ruled: redact in
place**), **Q6** (§1b says strip `.env` values, the rider says never read `.env` —
resolved in code: the exporter strips credential *shapes* and `KEY=value` forms and
never opens `.env`), **Q7** (commit author identity becomes public at CH-15 —
**put to the operator, ruled: keep it**).

**Finding worth the architect's attention, in Q5.** The audit's claim that there are
**four** PII carriers is **wrong**. A maximally permissive sweep — literal,
digits-only projection, JSON-escape-stripped, case-insensitive — finds **two**:
`context/09-COMPLIANCE-AUDIT.md` and `context/09b-audit-raw.json`.
`context/04b-intel-raw.json` and `context/05b-tournament-raw.json` are clean;
`context/10-REMEDIATION.md` had already self-redacted to `<OPERATOR-PHONE>`, as that
file itself records. The personal email has **zero** carriers. The sweep is not
vacuous: the same pattern returns 1 against the git-ignored source file and 0
against the tracked set after redaction — positive control and pass criterion both
reported. The prompt's own instruction *"do not hard-code the list, find them with
the sweep"* is what caught the over-claim; the hard-coded list would have sent a
session hunting three already-clean files.

### Gate
**None.** CH-00 is ungated by `plan.md` and `PROCESS.md` §6. No self-certification
beyond the done-when criteria is claimed: the suite is green, the guard probe is
16/16, and the goldens were computed before the code — but nobody has independently
reviewed this chunk, and this entry does not pretend otherwise.

### Status ledger
`STATUS.md`: CH-00 → **built**. Every other chunk seeded **todo**, except CH-07,
which is **not built** by ruling R-01 as pre-declared counted removal #3.

Repository `chinmoypaul8897/instruction-that-wont-execute`, **private**; anonymous
`curl` returns **404**, verified. Tree 430.2 MB / 7,460 files; **53 tracked**,
largest tracked blob 1.05 MB (the exported CH-00 transcript).

### State for next session (CH-01)
- `git config core.hooksPath .githooks` is set **on this machine only**. A fresh
  clone must re-run it; the hook is not self-installing.
- `data/` does not exist yet. CH-01 creates it. `data/raw/` and `*.xml` are already
  git-ignored, and the hook rejects any blob over 25 MB — **extract, then freeze.**
- `www.ecfr.gov` and `www.federalregister.gov` are **403 from this machine**.
  `www.govinfo.gov` is the sole harvest channel. Do not attempt a workaround.
- The run logger is ready and is the only sanctioned way to invoke an agent
  (hard rule 10). CH-01 needs no model, so it needs no runs.
- `GOOD.md` is deliberately empty and must stay empty until CH-04.
