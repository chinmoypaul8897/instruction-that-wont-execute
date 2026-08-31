# The trajectory selection rule — published BEFORE it is applied

**Deliverable 4.** This file states which trajectories a reader is pointed at first,
and it is committed **before** the script that applies it runs. That ordering is the
whole point: a curation nobody can audit is indistinguishable from quietly dropping
the runs that looked bad.

> **Nothing is deleted, ever.** This is an **index**, not a filter. The complete
> trajectory set stays in the repository and ships in the submission zip. Curation
> here means *what a judge is shown first*, and the rule exists so that choice is
> checkable rather than tasteful.

---

## Why there is a rule at all

`QUESTIONS.md` **Q2**, consequence **C2**, is binding spec:

> *The PDF requires "**representative** trajectories for every agent you used", not
> all of them. Ship a curated representative set in the zip; ship the complete set in
> the git repo and link it from the Description. **Record the selection rule so the
> curation is auditable.**"*

And `CLAUDE.md` hard rule 5 — *never weaken a test or a threshold* — applies to this
rule too. **No clause below may be relaxed to make a set smaller or a story neater.**

## Provenance of the rule text — the ordering that makes it auditable

The clauses are **quoted from the CH-12 chunk card**, `prompts/CH-12.md` §2, issued by
the architect before this session read a byte of trajectory. This file is committed in
its own commit, and `docs/evidence/ch12/apply_selection.py` — which computes what the
rule selects — runs **after** that commit. `git log` on the two paths is the proof, and
a reader who does not trust it can check the order themselves.

A rule written after the measurement is a rationalisation. This one is not, and the
history says so.

---

## The rule

| id | clause |
|---|---|
| **T1** | one trajectory per **agent class** — build sessions, evaluation arms, adversarial audits |
| **T2a** | for the arms: the **first** run |
| **T2b** | for the arms: the **median-cost** run |
| **T2c** | for the arms: one containing a **`retry`** record |
| **T2d** | for the arms: one containing a **`human_checkpoint`** record |
| **T3** | **every run whose verdict disagreed with gold** — failures are never filtered |
| **T4** | the **complete** set stays in the repository; the curated set is what a reader is pointed at first |

### Tie-breaks, fixed here so no choice is made with a result in view

- **"First"** and **"one containing"** resolve by **sorted repo-relative path**,
  ascending. Not by timestamp, not by cost, not by accuracy, not by how the run reads.
- **Median-cost** is the element at index `(k−1)//2` of the arms trajectories sorted by
  `(imputed_usd, path)` — the **lower** median when `k` is even. Cost is summed from
  `docs/evidence/runs/cost_ledger.csv` over the `run_id`s a trajectory contains.
- The **unit of selection is the file**, not the item-level run. A file is selected if
  **any** clause selects **any** run inside it. Selecting a fraction of a bundle would
  contradict `src/arms.py::bundle()`, which promises *"EVERY RECORD SURVIVES — nothing
  is sampled, summarised or dropped."*
- A trajectory selected by several clauses is listed once, with **every** clause that
  reached it named. Overlap is reported, not collapsed.

### What T3 is for, and what it will probably do

T3 is the clause that stops this from being a highlight reel. It selects on
**disagreement with gold** — that is, on failure — and it has no cap. If it selects
everything, the rule is not broken; the rule is working, and the honest thing is to
say so rather than to add a limit that would keep the set small.

*(CH-14a ran the same clause under the name R3 and found it selected **all 15** arms
trajectories on its own, because no arm scores 1.000 on this corpus — the best, A1,
scores 0.7195, so every arm file contains items whose verdict disagreed with gold.
Whether that still holds is a measurement, and it is reported in
`docs/evidence/ch12/selection-applied.md`, not assumed here.)*

---

## One clause names a class whose trajectories are not JSONL — stated, not glossed

**T1 names three agent classes. `docs/trajectories/` has directories for two of them.**

| class in T1 | trajectory form | where |
|---|---|---|
| **build sessions** | one JSONL per Claude Code session, written by `tools/export_session.py` | `docs/trajectories/build/` |
| **evaluation arms** | one JSONL per arm run, written by `src/runlog.py` | `docs/trajectories/arms/` |
| **adversarial audits** | **not JSONL.** These are subagent fleets spawned *inside* a coding session; their per-agent records live in the workflow journal, which is outside the repository, and what is committed is the **verbatim** transcription of each agent's finding | `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md`, `docs/reviews/`, `docs/evidence/spec-fix-1/` |

There is also a fourth directory, `docs/trajectories/probe/`, which T1 does not name:
the model-id probe runs from `QUESTIONS.md` Q1. **It is not dropped.** T1 is applied to
**every class present in `docs/trajectories/`**, the probe class included, because a
rule that silently skipped a directory would be exactly the failure this file exists to
prevent.

**The gap is real and is not repaired by wording.** The adversarial-audit class is the
one class whose agents cannot be replayed from `docs/trajectories/`, and
`AI-USE.md` says where each fleet's evidence is instead. It is raised as
`QUESTIONS.md` **Q40**.

---

## When curation would actually bite

Never, on this tree — and that is a measurement, not a hope.
`docs/evidence/ch14-size/selection-rule.md` records the finding: `git archive
--format=zip HEAD` is far under the 50 MB cap, so the complete set ships and the rule
is **not invoked** as a filter. `.githooks/pre-commit` refuses any commit whose archive
exceeds 45 MB.

If that threshold is ever crossed, the clauses apply in order
T1 → T2a → T2b → T2c → T2d → T3, the applier is re-run, and the resulting curation
ships with its own audit. **Under T4 the complete set remains in git either way.**
If the selected set alone exceeded the cap, that is a red result and it ships red.
