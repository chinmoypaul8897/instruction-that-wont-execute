# AI-USE.md — every model, tool and agent used on this project

**This is part of deliverable 4.** Hard rule 13: *"Nothing about how this was built is
concealed — the hackathon requires agent use and scores how well it was directed."*

This project is machine-written throughout, under a written constitution
(`CLAUDE.md`), a spec that outranks the code (`CONTEXT.md`), and adversarial review
gates by sessions with zero shared context. That is the claim; the trajectories below
are what makes it checkable rather than asserted.

---

## Agent classes — three, all evidenced

| Class | What it is | Count | Trajectories live at |
|---|---|---|---|
| **Research / ideation** | ~90 agents across four design workflows that proposed, attacked and killed candidate projects | ~90 | `context/*-raw.json` (committed) |
| **Coding** | fresh Claude Code BUILD and REVIEW sessions that write this repository | 2 so far | `docs/trajectories/build/<CHUNK-ID>.jsonl` |
| **Solution** | the evaluation arms — the thing being measured | 0 so far | `docs/trajectories/<run_id>.jsonl` + `docs/evidence/runs/cost_ledger.csv` |

The coding row is the one that is easy to lose and easy to fake. Those transcripts
live outside the repository in `~/.claude/projects/`, where Claude Code rotates and
prunes them, and they contain deliverable 4's own checklist verbatim — agent
instructions, every tool call, every tool response, retries, and human
interruptions. `tools/export_session.py` captures them; `CLAUDE.md`'s end-of-session
duty 6 makes a chunk **not done** until its transcript is exported.

---

## Models

| Model | Exact id | Where used | Price basis |
|---|---|---|---|
| Claude Opus 5 (1M context) | `claude-opus-5` | every Claude Code build/review session, incl. this one | $5.00 / $25.00 per MTok |
| Claude Haiku 4.5 | `claude-haiku-4-5` | **planned** — every evaluation arm, via Message Batches (`QUESTIONS.md` Q1) | $1.00 / $5.00 per MTok, batch at 50% |
| Claude Sonnet 5 | `claude-sonnet-5` | **planned** — model-sensitivity check at the CHECKPOINT only, 20-item subset | $2.00 / $10.00 per MTok |

Prices are Anthropic published list, re-read from the published table on 2026-08-30
rather than recalled, and recorded in every run as `price_basis` +
`price_basis_url`. Source: <https://docs.claude.com/en/docs/about-claude/pricing>.

**Fairness constraint:** every evaluation arm gets the *same* model. What the model
choice limits is generalisability, not the internal comparison — and the
model-sensitivity check turns that limit into a number instead of a caveat.

---

## Tools available to the coding sessions

Claude Code's own harness: file read/write/edit, glob, grep, shell, web fetch, task
subagents. No custom MCP server. No autonomous scheduling. The session runs under
`CLAUDE.md`, a per-chunk prompt committed verbatim in `prompts/`, and a hard safety
rider that makes `context/` and the root specs read-only to build sessions.

Tools the *solution* agents get are a different and much smaller set, defined per arm
in `agents/` — that separation is the point of the experiment and is not blurred here.

---

## Human direction

The operator (Chinmoy Paul) is the architect: writes the spec and the chunk prompts,
rules on every question raised to `QUESTIONS.md`, and merges `STATUS.md` /
`PROGRESS.md`. Sessions do not certify their own work (hard rule 2). Human decision
points are recorded as they happen — `QUESTIONS.md` Q5 and Q7 in this chunk were both
put to the operator mid-session and answered before work continued.

Human time per chunk is tracked for the rubric's *human time per task* row; the
blind human-time study (8 items by hand, stopwatched, before seeing gold) is CH-09.

---

## Session log

Newest first. Every build session appends one row here **and** exports its transcript.

### CH-01 · 2026-08-30 · Claude Code · `claude-opus-5` · BUILD

- **Scope:** govinfo ECFR `<EDNOTE>` harvest — `src/harvest_ednotes.py`,
  `tests/test_harvest_ednotes.py`, `refetch.py`, the `data/ednotes/` freeze and
  `docs/evidence/ch01-pool/`.
- **Trajectory:** `docs/trajectories/build/CH-01.jsonl` (672 lines, 1,433,689 B;
  772 home-path substitutions, every other scrub category an explicit 0).
- **Wall-clock:** first turn 13:51:08 UTC → last 14:30:36 UTC = **39.5 min**.
- **Measured usage** (237 assistant turns, read from the transcript's own `usage`
  records — measured, not estimated). Snapshot taken at the final export; the commit
  that lands these numbers is necessarily not in them, so the true totals are
  marginally higher — the same structural caveat CH-00 recorded. Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id 577b7ed1-d9e2-49ed-aaf2-53f1454e71ce`;
  committed output: `docs/evidence/ch01-pool/ch01-session-cost.txt`.

  | | tokens |
  |---|---|
  | output | 348,831 |
  | input, uncached | 474 |
  | input, cache write | 546,507 |
  | input, cache read | 40,546,204 |
  | **total input** | **41,093,185** |

- **Imputed cost** — same two bases as CH-00, and for the same reason: the
  cache multipliers are assumed and were not re-verified this session, so the
  assumption-free upper bound is printed beside them, never instead.

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **214.186700** |
  | Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **32.411916** |

- **Against the economy instruction — a miss, stated plainly.** `prompts/CH-01.md`
  asked for *"a fraction of"* CH-00's ~26 M input tokens. This session used
  **41.1 M**, about **1.6×** CH-00 rather than a fraction, and 32.41 against 22.51
  cache-adjusted. Attributable causes, in order of size: a 824 MB download and two
  full-corpus re-parses (the extraction plus the determinism proof) that produced
  long tool outputs across many turns; a `sed -i` that converted every `\n` escape
  in the test file to a real newline and cost a restore-and-reapply cycle; and a
  CRLF-on-a-`* -text`-repo mistake that had to be found and normalised. The first
  was inherent to the task; the second and third were self-inflicted and are
  recorded as such in `PROGRESS.md`.

### CH-00 · 2026-08-30 · Claude Code · `claude-opus-5` · BUILD

- **Scope:** repository initialisation, canonical files, `src/runlog.py`,
  `tools/export_session.py`, `.githooks/pre-commit`.
- **Trajectory:** `docs/trajectories/build/CH-00.jsonl`
- **Measured usage** (from the session transcript's own `usage` records,
  144 assistant turns — measured, not estimated from character counts).
  **Snapshot taken at export time**; the session necessarily continues for the
  final commit and push, so the true totals are marginally higher. Regenerate with
  `python docs/evidence/ch00_session_cost.py`:

  | | tokens |
  |---|---|
  | output | 315,403 |
  | input, uncached | 288 |
  | input, cache write | 654,586 |
  | input, cache read | 21,069,904 |
  | **total input** | **21,724,778** |

- **Imputed cost — the build subscription is flat-cost to the operator, so this is
  an imputation and is labelled one (never `$0`):**

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **116.508965** |
  | Cache-adjusted — cache write at 1.25x, cache read at 0.10x input list | **22.512630** |

  Both are reported because the second depends on cache-tier multipliers that were
  **not** re-verified against the published table in this session, and an unverified
  multiplier is a claim, not a measurement (hard rule 15). The upper bound rests on
  no assumption at all. Working: `docs/evidence/ch00-session-cost.txt`.

- **Note:** this session's spend is *not* charged against the USD 18 ceiling in
  `src/runlog.py`. That ceiling governs the **paid API** used by the evaluation arms
  (`QUESTIONS.md` Q1). Build-session cost is a flat subscription and is reported here
  for disclosure, not budgeting. Conflating the two would misstate both.
