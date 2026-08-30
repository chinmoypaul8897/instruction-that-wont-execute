# BUILD PHASE 1 — Logger, Harvest, and the Go/No-Go Checkpoint

This is the **first build session**. Create the repo, instrument logging, harvest the corpus, and then answer one question with real numbers:

> **Does the measured gap survive at a real sample size?**

Stop at that answer. **Do not build the agent.** A later session does that.

---

## 0. Read first

| File | What it is |
|---|---|
| `context/08-FINAL-CALL.md` | **The decision and the final spec.** §5 "THE FINAL SPEC — only the deltas" is authoritative and overrides anything below it that conflicts. |
| `context/07-KILL-TEST.md` | §7 is the base spec the deltas apply to. §8 lists the honest gaps — read it. |
| `context/01-PROBLEM-PDF.md` | The official rubric and rules. |

**The project:** *The Instruction That Won't Execute.* US agencies publish final rules containing **amendatory instructions** — "in § 433.2, remove 'X' and add 'Y' in its place." If the anchor text or the paragraph designation isn't exactly where the instruction says, the Office of the Federal Register **cannot execute it**, the CFR never changes, and NARA publishes an editorial note recording the failure. The agent predicts this before publication — and writes the note NARA would have to publish.

---

## 1. HARD OPERATIONAL CONSTRAINT — read before writing any fetch code

**`www.ecfr.gov` and `www.federalregister.gov` return HTTP 403 from this machine.** Verified 2026-08-30 02:17 UTC. They worked 9 hours earlier; sustained automated traffic got us blocked. **Do not build the harvest on them. Do not spend time trying to get around it.**

**`www.govinfo.gov` returns HTTP 200, needs no key, and is the harvest channel.**

- `https://www.govinfo.gov/bulkdata/ECFR` — current eCFR title XML, contains `<EDNOTE>` elements (the labels)
- `https://www.govinfo.gov/bulkdata/CFR` — annual CFR editions back to 1996 (point-in-time text)
- `https://www.govinfo.gov/bulkdata/FR` — Federal Register issues (the amendatory instructions, in `<AMDPAR>` elements)

Confirm all three respond before doing anything else. If govinfo also blocks, **stop and report** — that is a project-level blocker and the session should end there.

---

## 2. Phase 1 — Repo and logger (~45 min). Do this before anything else.

1. `git init` a **private** repo in this folder. First file: `.gitattributes` containing `* -text` (a CRLF-mangled checksum manifest failing on the judge's machine is the worst possible first impression).
2. **Write the run logger before any project code.** Every agent invocation is wrapped in a harness that emits, per run, one JSONL trajectory:
   - the agent instructions given
   - each action taken and each tool response
   - the feedback that shaped the next step
   - retries and human checkpoints
   - input/output token counts, wall-clock, and **imputed cost at published API list prices** (the subscription is flat-cost — impute and say so; never report `$0`)
3. Prove it: a dummy run must produce a readable trajectory file and a cost row.

**Why first:** agent trajectories are a required deliverable and a qualification-gate item, and cost/time per task appear in only two repos on all of GitHub. Both are retrofit-hostile. Every run from here on gets captured, including this session's.

---

## 3. Phase 2 — The harvest (~2–3 h). This is the risk; it is also the whole project.

### 3a. Labels — structural `<EDNOTE>` extraction

Download the ECFR bulk title XMLs from govinfo and extract `<EDNOTE>` elements structurally. Filter to **codification-defect notes**: those containing `"could not be incorporated"`.

Reference measurements from nine titles (12, 20, 21, 24, 26, 40, 42, 45, 49) — use these to sanity-check your own numbers, not to substitute for them:

| Measure | Value |
|---|---|
| Total EDNOTEs | 903 |
| Codification-defect notes | 44 |
| Carry their own FR citation | **44/44** |
| Section-level (not appendix/part) | 38/44 |
| Localise the failure below section level | 6/44 (13.6%) |
| State an explicit failure mechanism | 10/44 (22.7%) |

**Expected full pool across 50 titles: 150–250 defect notes, ~130–210 section-level.** The eCFR search API previously reported 92 — it undercounts by ~2.3×.

Because every note carries its own FR citation, **FR-document resolution is deterministic** — no search step needed.

### 3b. Instructions — the AMDPAR attributor

From each note's FR citation, pull the FR document from govinfo and extract `<AMDPAR>` elements.

**The attributor is a carry-forward, not a hard problem.** Iterate AMDPARs in document order, maintain the last-named section, attach lettered sub-instructions to it. Three independent parties measured this at **0.99, 0.914 and 0.998 completeness.** A naive extractor that only reads lead-ins gets ~0.46 and silently poisons everything downstream.

**Hard gate: attributor completeness ≥ 0.90, measured and printed, before any headline number.** Completeness = fraction of items whose amendatory block parsed into at least one complete (operation, anchor-or-designation) triple.

### 3c. Point-in-time CFR text

The agent needs the section text **as it stood when the rule was published**. eCFR's versioner API is 403, so use **govinfo CFR annual editions** (`bulkdata/CFR`, back to 1996). The annual edition preceding the rule's publication date is the correct snapshot.

**Verify this actually works on 3 real cases by hand before scaling it.** If annual granularity turns out to be too coarse — the section was amended twice in the same year — record how often that happens and report it; it is an exclusion criterion, not a surprise.

### 3d. Build the eval set

- **Positives:** `(rule, section)` pairs carrying a live codification-defect note.
- **Negatives:** sibling sections amended by the same rule with no note, **matched exactly on instruction count.** Exact matching is non-negotiable — an unmatched set lets a hardcoded threshold on instruction count beat the agent, and that is precisely how an earlier candidate died.
- Publish the **full exclusion ladder** with counts at every step.
- Freeze everything under `data/` with a SHA-256 manifest and a `refetch.py`.

**Target: ≥ 42 pairs (n ≥ 84).** Report the real number.

---

## 4. Phase 3 — Pre-registration (~30 min). Before any agent runs.

Commit `GOOD.md`, timestamped, containing:
- the primary metric (execution-prediction accuracy, string equality against the NARA-authored fact)
- the success threshold: **agent ≥ baseline-with-text + 8 pp, McNemar p < 0.05, at n ≥ 84**
- guard metrics: false-defect ≤ 0.25, missed-defect ≤ 0.25, attributor completeness ≥ 0.90
- the predictions, written before the run: **B0 ≈ 0.50 · B0-agent ≈ 0.75 · A1 ≈ 0.85**

Commit this **before** running anything. It is the evidence that the goalposts did not move.

---

## 5. Phase 4 — THE CHECKPOINT (~1–1.5 h). The reason this session exists.

Build the deterministic scorer first (stdlib only, no model, no network): accuracy, false-defect rate, missed-defect rate, attributor completeness, and a reconciliation line asserting `success + failure == n`.

Then run **three arms**, three repetitions each, all logged:

| Arm | What it gets | Prediction |
|---|---|---|
| **B-script** | best model-free attack — threshold on any cheap feature, honest 5-fold CV, **reported with its permutation null** | ~0.59, p ≈ 0.185 |
| **B0** | one model, one prompt, the amendatory instruction only — **no CFR text** | ~0.50 (chance) |
| **B0-agent** | same model, **with** the point-in-time section text and search tools | ~0.75–0.82 |

### The decision rule — apply it honestly

- **B0-agent − B0 ≥ 15 pp with McNemar p < 0.05 at n ≥ 84** → **GREEN.** The corpus changes the answer. Build proceeds.
- **Gap present but p ≥ 0.05** → **AMBER.** Report the exact n, the gap, and the p-value. Say what n would be needed.
- **Gap < 8 pp, or B0 ≥ 0.70** → **RED.** If B0 ≥ 0.70 the instruction text is leaking executability: strip the *quoted anchor text* from the input (keep the operation and designation) and re-run the gate **once**. If it is still red, the project is dead and must be reported as dead.

**Do not tune to reach green.** A red result found now is worth more than a green one manufactured. The single most valuable thing this session can produce is an honest red.

---

## 6. Output → `context/09-CHECKPOINT.md`

```
# Build Phase 1 — Checkpoint Results

## 1. VERDICT: GREEN / AMBER / RED
The decision, then the numbers behind it.

## 2. The pool
Titles processed, EDNOTEs found, defect notes, section-level, FR docs resolved,
attributor completeness, pairs built, final n. Full exclusion ladder with counts.

## 3. The arms
Table: B-script (with its permutation null), B0, B0-agent — mean of 3 reps,
observed range, McNemar p, plus tokens / wall-clock / imputed cost per item.

## 4. What broke
Everything that did not work as the spec predicted, and what you did about it.
Especially: govinfo behaviour, annual-edition granularity, attributor edge cases.

## 5. Ready-to-build state
What exists in the repo, what the next session inherits, what it must do first.

## 6. Honest gaps
What you could not settle and how much it matters.
```

**Rules of evidence:** label every claim **VERIFIED** (you ran it — give the number), **INFERRED**, or **UNKNOWN**. Never present a guess as a fact. Report failures as prominently as successes.

---

## 7. Scope discipline

**Do NOT build:** the `cfr_resolve` tool, `SKILL.md`, the memory ledger, the worksheet UI, the README, or the video. Those belong to the next session.

**Do build:** repo, logger, harvest, eval set, pre-registration, scorer, three baseline arms, checkpoint report.

If you finish early, **do not start the agent.** Spend the time widening the pool and hardening the freeze instead — sample size is worth more than a head start.

---

## 8. Final step — the handoff

Print a text block, **under 350 words**, for the user to paste into the other session:

1. **VERDICT:** GREEN / AMBER / RED and the numbers that decided it
2. **Pool:** final n, attributor completeness, exclusion summary
3. **Arms table:** B-script / B0 / B0-agent with p-value
4. **What broke** and what it cost
5. **Cost and wall-clock** so far
6. Confirmation the full report is at `context/09-CHECKPOINT.md`

Then stop.
