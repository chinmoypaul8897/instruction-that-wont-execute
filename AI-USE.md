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
| **Coding** | fresh Claude Code BUILD and REVIEW sessions that write this repository | 1 so far | `docs/trajectories/build/<CHUNK-ID>.jsonl` |
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

### CH-00 · 2026-08-30 · Claude Code · `claude-opus-5` · BUILD

- **Scope:** repository initialisation, canonical files, `src/runlog.py`,
  `tools/export_session.py`, `.githooks/pre-commit`.
- **Trajectory:** `docs/trajectories/build/CH-00.jsonl`
- **Measured usage** (from the session transcript's own `usage` records, 113
  assistant turns — not estimated):

  | | tokens |
  |---|---|
  | output | 250,950 |
  | input, uncached | 226 |
  | input, cache write | 601,321 |
  | input, cache read | 13,954,622 |
  | **total input** | **14,556,169** |

- **Imputed cost — the build subscription is flat-cost to the operator, so this is
  an imputation and is labelled as one (never `$0`):**

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **79.05** |
  | Cache-adjusted — cache write at 1.25x, cache read at 0.10x input list | **~17.01** |

  Both are reported because the second depends on cache-tier multipliers that were
  **not** re-verified against the published table in this session, and an unverified
  multiplier is a claim, not a measurement (hard rule 15). The upper bound needs no
  assumption. Working: `docs/evidence/ch00-session-cost.txt`.

- **Note:** this session's spend is *not* charged against the USD 18 ceiling in
  `src/runlog.py`. That ceiling governs the **paid API** used by the evaluation arms
  (`QUESTIONS.md` Q1). Build-session cost is a flat subscription and is reported here
  for disclosure, not budgeting. Conflating the two would misstate both.
