# CLAUDE.md — session constitution

**Read this first, every session, before anything else.**

## Read order
1. `CLAUDE.md` (this file)
2. `plan.md` → your chunk card, and `PROCESS.md` §6–§7 for the gate policy and the clock
3. `CONTEXT.md` → the sections your card cites. **THIS FILE IS LAW.**
4. `STATUS.md`
5. `PROGRESS.md` (latest entry)
6. `QUESTIONS.md`
7. `docs/reviews/` (prior, if any)

If the card, the spec and the logs disagree → **STOP** and write to `QUESTIONS.md`.

## Precedence
`context/01-PROBLEM-PDF.md` (the hackathon rules — **local, not redistributed; see `QUESTIONS.md` Q3**) → `CONTEXT.md` → `PROCESS.md` → `plan.md` → code → tests → memory.

## The hard rules

1. **STOP RULE.** Spec ambiguous, incomplete or contradictory → stop that item, write it to `QUESTIONS.md` with the options you see, continue unblocked work. **Never assume.** Stopping on a real ambiguity is success, not failure.
2. **NO SELF-GRADING.** You never certify your own work. Gated chunks are reviewed by a different session with zero shared context.
3. **NO SILENT DEVIATION.** Class A (changes meaning or results) → STOP, ask the architect. Class B (implementation choice within spec) → do it, record it in `PROGRESS.md` with rationale. Class C (cosmetic) → one line.
4. **GOLDEN FIXTURES DEFINE DONE.** Hand-compute expected outputs **before** writing the code. A test whose expected value came from the code it tests proves nothing.
5. **NEVER WEAKEN A TEST OR A THRESHOLD.** No loosening an assertion to get green. **No moving a `GOOD.md` number after seeing a result.** A red result ships as red.
6. **EVERY FIX SHIPS A PROBE THAT FLIPS.** Fails on the old code, passes on the new — show both. The probe is kept forever.
7. **EXACTNESS.** Paragraph designations and quoted anchor text are precision-critical. Three declared normalisation levels — `exact` / `whitespace-collapsed` / `alphanumeric-only`. The level achieved is **reported**, never applied silently.
8. **PURITY.** Scorer and resolver take data in and return results. No network, no clock, no randomness inside them.
9. **DETERMINISM.** Same inputs → byte-identical outputs, provable by hash.
10. **EVERY AGENT RUN IS LOGGED.** No exceptions, from the first run. Trajectory + input tokens + output tokens + wall-clock + imputed USD. Retrofitting is impossible and it is a submission gate item.
11. **`data/` IS SEALED** after CH-03. Read-only. No write, move, rename or delete without an explicit named sanction in your prompt; any sanctioned mutation runs on a copy.
12. **SECRETS NEVER IN THE REPO.** `.env` only, git-ignored, never printed or echoed. To confirm a key exists, read only its name.
13. **TOTAL DISCLOSURE.** Every model, tool and agent goes in `AI-USE.md`. Every commit carries `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`. Nothing about how this was built is concealed — the hackathon requires agent use and scores how well it was directed.
14. **EVIDENCE OR IT DIDN'T HAPPEN.** Any claim from data ships its generating script **and** its committed output under `docs/evidence/`. Zero-occurrence branches print as zeros. `success + failure == n` is asserted.

15. **VERIFY BEFORE YOU RELAY.** A finding from another agent, another document, or an earlier session is a **claim**, not a fact. Check it against the files and the data before acting on it or repeating it. *Recorded because the architect broke this three times in one day: it called a file "micro1's problem PDF" (it is a Descartes brochure), relayed a budget of USD 150-250 (the measured figure is ~USD 9), and declared thirteen outstanding items "cosmetic" without reading them. Each was an agent's claim, accepted because checking felt slower.*

16. **VERIFY YOUR OWN EDIT LANDED.** After any programmatic edit, assert the new text is present **and** the old text is gone. *A batch of edits silently failed here — the replace targets did not match, nothing errored, and two shipping files ended up disagreeing about the plan. Six contradictions were introduced while fixing contradictions, and only a sweep found them.*

17. **THE CLOCK IS NOT A DESIGN INPUT.** The operator owns the schedule. Never trade correctness for speed, never propose a cut justified by time, and never declare work finished because you are tired of it. *Every one of the failures in rules 15 and 16 traces to hurrying.* If you catch yourself reasoning "this is probably fine, and checking is slow" — that is the signal to check.

> These three rules are this project's own thesis turned on its author. We are building a system to prove that **a green test suite is not evidence of correctness**. The architect twice declared work correct without checking it. The rules exist because the failure is not hypothetical — it is in this repository's history, and it is disclosed in `PROVENANCE.md` rather than hidden.

## Operational constraint — binding
`www.ecfr.gov` and `www.federalregister.gov` return **HTTP 403** from this machine (verified 2026-08-30 02:17 UTC). **Do not build on them. Do not try to work around it.** `www.govinfo.gov` returns 200, needs no key, and is the sole harvest channel.

## End-of-session duties
1. Commit any new rulings to `QUESTIONS.md` / `CONTEXT.md` **first**, before anything else.
2. Update `STATUS.md` (one line for your chunk) and `PROGRESS.md` (newest entry on top).
3. Atomic commits. Message ends `(unreviewed)` for any source or test change. Every commit carries the `Co-Authored-By` trailer.
4. Push. Report the SHA.
5. Emit your report as **ONE plain-text code block** — no markdown — so the operator copies it in one motion.
6. **Run `python tools/export_session.py <CHUNK-ID>` and commit the exported trajectory.** This is a deliverable-4 gate item: the session transcript is the only trace of the coding agents, it lives outside the repo, and Claude Code prunes session directories. **A chunk whose transcript was not exported is not done.**

## Report template
```
CHUNK <id> REPORT
WHAT CHANGED   : ...
VERIFICATION   : goldens hand-computed? y/n · suite pass/fail/skip counts
PROBE FLIP     : fails-on-old / passes-on-new — both shown, or n/a
FILES          : ...
STATUS LINE    : ...
PROGRESS LINE  : ...
PUSHED SHA     : ...
QUESTIONS      : raised to QUESTIONS.md, or none
TOKENS + COST  : in / out / wall-clock / imputed USD
```

## Parallel sessions
When more than one build session runs at once (Phase 3 only, by architect instruction):
- **Commit ONLY the paths your chunk card declares.** Never `git add -A`, never `git add .`.
- `STATUS.md` and `PROGRESS.md` are **architect-merged**. Write your entry to `docs/progress/<CHUNK-ID>.md` instead; the architect folds it in.
- `git pull --rebase` before every push. If a conflict touches a file outside your declared paths, **STOP and report** — do not resolve it.

## Never
- Self-certify. A fresh review follows.
- Exceed your scope fence. Tempted elsewhere → STOP.
- Skip the logger.
- Report a number without its evidence path.
