# PROCESS.md — how this project is built

**Project:** *The Instruction That Won't Execute* — micro1 Agentic Workflows Hackathon
**Deadline:** 2026-08-31 18:00 UTC · **Adopted:** 2026-08-30 03:10 UTC (T−38.8 h)
**Spec:** `context/08-FINAL-CALL.md` §5 (deltas) over `context/07-KILL-TEST.md` §7 (base)

---

## 0. The design principle

Most hackathon processes are overhead that produces a submission at the end. **This one is designed so that running it *is* writing the submission.**

Four of the six scored rows are earned by how the work is done, not what is built:

| What the process produces | Rubric row |
|---|---|
| independent review reports — nothing self-graded | Agent Solution & Engineering — **30** |
| per-iteration cards linking a change to its evidence | Measured Improvement — **15** |
| frozen corpus, manifest, deterministic scorer, replay tier | Reproducibility — **15** |
| the recorded failure that taught us something | Hot Take — **5** |

So: **no artifact is written twice.** The session journal *is* the changelog source. The review reports *are* the agent-engineering evidence. The trajectory logs *are* deliverable 4. If something has to be reconstructed at the end, the process was wrong.

**Second principle: total honesty.** Every agent, every tool, every failure, every null result is disclosed. Commits carry `Co-Authored-By: Claude`. A red checkpoint ships as red. We are not hiding that AI built this — the hackathon *requires* agent use, and how well we directed it is the thing being scored.

---

## 1. Roles

| Role | Who | Does | Never |
|---|---|---|---|
| **ARCHITECT** | this session, continuous | owns the spec; writes every chunk prompt; verifies reports by recomputing load-bearing numbers; rules on ambiguities; decides sequence and gates | writes project code or commits |
| **OPERATOR** | Chinmoy | carries one prompt at a time into a fresh session; pastes the report back; runs long jobs; makes final calls | lets a session decide what the spec left open |
| **BUILD** | fresh session per chunk | executes exactly one chunk card | assumes · self-certifies · exceeds scope |
| **REVIEW** | a *different* fresh session | adversarially verifies one gated chunk | fixes what it reviews (may add kept probes) |

**Why the architect is this session:** it holds nine research files, three kill tests, the rubric and the full reasoning chain. Re-bootstrapping costs hours we don't have. From now on it is read-only on project source — it writes prompts and analysis, never code.

**One prompt at a time.** Two prompts in one message is how steps get skipped.

---

## 2. The loop

```
ARCHITECT writes the chunk card + build prompt
   → OPERATOR pastes into a FRESH session
      → session reads its card, builds, self-checks against "done when"
      → commits "(unreviewed)", pushes, emits ONE plain-text report block
   → OPERATOR pastes report back
   → ARCHITECT recomputes the load-bearing numbers itself

   if gated:  ARCHITECT writes the review prompt
      → OPERATOR pastes into a DIFFERENT fresh session
         → adversarial review, REVIEW_n.md, PASS → tag · FAIL → findings
      → ARCHITECT reads verdict; on FAIL issues a fix prompt

   → next chunk
```

**Chunks are self-contained.** One session, one sitting, one reviewable unit. A chunk that grows mid-flight is split (CH-05 → 05A/05B) and the split is recorded as a ruling.

**Every session prompt names its read-order explicitly** so a fresh session boots to full context deterministically.

**Every report is ONE plain-text block** so the operator copies it in one motion.

---

## 3. Files

Created at CH-00. **Chat history is not a record. If it matters it lives in a file in the repo.**

| File | Purpose | Ships? |
|---|---|---|
| `CONTEXT.md` | **the spec — THIS FILE IS LAW.** Versioned, architect-authored only | yes |
| `plan.md` | chunk cards: scope, inputs, outputs, gate, done-when | yes |
| `CLAUDE.md` | session constitution — read order, the hard rules, end-of-session duties | yes |
| `STATUS.md` | one line per chunk: `todo / built / reviewed-PASS / reviewed-FAIL` | yes |
| `PROGRESS.md` | session journal, newest first — **source of the Improvement Changelog** | yes |
| `QUESTIONS.md` | every ambiguity and every ruling, verbatim | yes |
| `GOOD.md` | **pre-registration** — metric, thresholds, predictions, committed before results exist | yes |
| `CHANGELOG.md` | **the Improvement Changelog, written per iteration as it happens** | **deliverable 1** |
| `AI-USE.md` | every model, tool and agent used; what each did; where its trajectory is | **deliverable 4** |
| `docs/evidence/` | per claim: the generating script **and** its committed output | yes |
| `prompts/` | every chunk prompt, committed verbatim as issued — these **are** the agent instructions deliverable 1 requires | **yes** |
| `docs/progress/` | per-chunk session entries when sessions run in parallel; architect merges into `PROGRESS.md` | yes |
| `docs/reviews/` | one report per gated chunk | yes |
| `docs/trajectories/` | one JSONL per agent run | **deliverable 4** |
| `prompts/design/` | the design-phase agent instructions that produced `context/06` and `context/07` | yes |
| `agents/` | one file per evaluation arm: the exact instructions that shape it | **deliverable 1** |
| `src/` | the solution, the scorer, the resolver | yes |
| `tests/` | the suite — **named as a required item by the submission-validity FAQ** | yes |
| `README.md` | user → bottleneck → value → changelog → failure mode → hot take | **deliverable 1** |
| `REPRODUCE.md` | clean-environment guide, both tiers, exact commands | **deliverable 2** |
| `PROVENANCE.md` | what pre-existed vs what was built — ground rule 02 | yes |
| `SUBMISSION.md` | the six FAQ items with a path or URL each | yes |
| `LICENSE` · `THIRD-PARTY.md` · `SAFETY.md` | licence, dependency clearances, human-reviewer statement | yes |
| `data/` | frozen corpus + SHA-256 manifest + `refetch.py` | yes |

---

## 4. Hard rules

Verbatim into `CLAUDE.md`.

1. **STOP RULE.** Spec ambiguous, incomplete or contradictory → stop that item, write it to `QUESTIONS.md` with the options you see, continue unblocked work. **Never assume.** Stopping on a real ambiguity is success.
2. **NO SELF-GRADING.** The session that built a thing never certifies it. Gated chunks are reviewed by a session with zero shared context.
3. **NO SILENT DEVIATION.** Class A (changes meaning or results) → STOP, ask. Class B (implementation choice inside spec) → do it, record it, judged at review. Class C (cosmetic) → one line.
4. **GOLDEN FIXTURES DEFINE DONE.** Hand-compute expected outputs *before* writing the code. A test whose expected value came from the code it tests proves nothing.
5. **NEVER WEAKEN A TEST OR A THRESHOLD.** No loosening an assertion to get green. **No moving a `GOOD.md` number after seeing a result.** A red result ships as red.
6. **EVERY FIX SHIPS A PROBE THAT FLIPS.** Fails on the old code, passes on the new, both proven, probe kept forever.
7. **EXACTNESS WHERE IT COUNTS.** The precision-critical domain is **paragraph designations and quoted anchor text** — `(b)(4)(i)(A)` and the exact characters of a quoted string. Normalisation levels are *reported*, never silently applied.
8. **PURITY.** Scorer and resolver take data in and return results — no network, no clock, no randomness inside. This is what makes the judge's replay identical to ours.
9. **DETERMINISM.** Same inputs → byte-identical outputs, provable by hash. `.gitattributes` = `* -text` on line one. Frozen corpus under SHA-256 manifest.
10. **EVERY AGENT RUN IS LOGGED.** No exceptions, from the first run. Trajectory + tokens + wall-clock + imputed cost. Retrofitting is impossible and it is a gate item.
11. **DATA IS SEALED.** After CH-03, `data/` is read-only to sessions. No writes, moves, renames or deletes without an explicit named sanction; sanctioned mutation runs on a copy.
12. **SECRETS NEVER IN THE REPO.** `.env` only, git-ignored, never printed or echoed. History scanned before the repo goes public.
13. **TOTAL DISCLOSURE.** Every model, tool and agent is named in `AI-USE.md`. Commits carry `Co-Authored-By: Claude`. Nothing about how this was built is concealed.
14. **EVIDENCE OR IT DIDN'T HAPPEN.** Any claim from data ships its generating script and committed output under `docs/evidence/`. Zero-occurrence branches print as zeros. `success + failure == n` is asserted.

---

## 5. The iteration card — the mechanism that earns the 30-point row

The rubric's biggest row asks: **"Which design choices helped the agent solve the problem?"** The only defensible answer is one written *before* the choice was made.

**Before building any capability chunk (CH-05 … CH-07), the architect commits an iteration card to `CHANGELOG.md`:**

**`CHANGELOG.md` uses the four-column table the brief mandates** (PDF §4) — one row per stage:

| STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING |
|---|---|---|---|
| Baseline | … | … | Established the starting point |
| Iteration 1 | … | … | kept / revised / **removed** |
| Final | Combined the changes that worked | … | Identified the main contribution |

Each row is backed by an iteration card, committed **before** the build:

```
## Iteration N — <capability>
Observed failure : <the specific failure in the previous arm, with its number>
Hypothesis       : <why this capability should fix it>
Prediction       : <the number it should move, and by how much>  ← committed BEFORE the run
Evidence path    : docs/evidence/iter-N/
```

After the run, the same card is completed:

```
Result           : <measured>
Decision         : kept / revised / REMOVED
Learning         : <what it taught us about the problem>
```

**A capability that does not move its number is removed and the card stays.** The PDF requires a removed experiment; this guarantees we have real ones rather than manufactured ones. A card that predicted +8 and measured +1 is *better evidence of method* than one that quietly succeeded.

---

## 6. Gate policy

Gating everything costs more hours than exist. Gating nothing forfeits the 30-point row. So: **gate what a silent bug would invalidate.**

| Chunk | Gate | Why |
|---|---|---|
| **CH-02** AMDPAR attributor | **FULL** | a truncation bug already produced 0.46 completeness once and poisoned an entire pilot |
| **CH-03** eval-set constructor | **FULL** | exact instruction-count matching is what stops a constant beating the agent; wrong here = rigged benchmark = dead |
| **CH-04** scorer + `GOOD.md` | **FULL** + mutation tests | the one thing that must never be self-graded |
| **CH-06** note emission | **CODE-ONLY** | the load-bearing capability |
| everything else | self-check against done-when | presentation and measurement |

**Tiered review.** **MANDATORY CORE** (45–70 min): rerun the suite from clean and reproduce the count · reimplement the load-bearing logic from `CONTEXT.md` alone and diff · rebuild each probe on the pre-change commit and confirm it fails there. **IF-TIME:** mutation testing, secret sweep. The architect picks the tier per chunk and records it as a ruling.

**NUMBERS-ONLY review** — a third, cheap tier (30–40 min, no reimplementation). A fresh session receives only the committed per-item verdict CSVs and `CONTEXT.md` §7, independently recomputes accuracy, the McNemar statistic, the bootstrap CI and the effect size, **confirms the bootstrap resamples documents not items** (with a probe that fails under item-level resampling), confirms each ablation arm differs from A1 in exactly one capability by diffing arm configs, then diffs against the reported figures. **Applies to the CHECKPOINT before its call is acted on, and to CH-08 before any number reaches the README.**

**Two-strike rule.** A gated chunk gets at most **two** fix→re-review rounds. On a second FAIL the architect either accepts the chunk with its open findings copied **verbatim** into the README's LIMITATIONS section and the review report shipped as-is, or invokes the chunk's pre-registered fallback. The decision and its UTC timestamp go in `QUESTIONS.md`. **There is no third round.**

**Review mechanics (gated chunks):** fresh session, zero shared context · rerun the suite from clean and reproduce the count before adding anything · **reimplement the load-bearing logic from `CONTEXT.md` alone, importing nothing from the project, and diff** · mutation-test critical operators (CH-03/04) · findings numbered with severity · **PASS/FAIL — any spec deviation is FAIL even if tests are green.**

---

## 7. Chunk plan

### Phase 1 — foundation and the go/no-go · **~17 h** *(revised: the original ~5 h excluded its own three review gates — see the compliance audit)*
| Chunk | Scope | Gate | Done when |
|---|---|---|---|
| CH-00 | repo, `.gitattributes`, canonical files, **run logger + cost/time accounting** | — | dummy run emits a trajectory and a cost row |
| CH-01 | govinfo `<EDNOTE>` harvest → defect notes with FR citations | — | pool count + exclusion ladder committed |
| CH-02 | AMDPAR carry-forward attributor | **FULL** | completeness ≥ 0.90, measured and printed |
| CH-03 | point-in-time CFR text + eval set + **exact instruction-count matching** | **FULL** | ≥ 42 pairs; balance asserted by test; manifest verifies from clean clone |
| CH-04 | deterministic scorer + **`GOOD.md`** | **FULL** | scorer reproduces B-script number and its permutation null |
| **★** | **CHECKPOINT** — B-script / B0 / B0-agent × 3 | — | **GREEN / AMBER / RED** |

### Phase 2 — the agent · ~11.5 h · **on GREEN *or* AMBER** — whatever remains until 06:00 UTC
*(AMBER proceeds: the agent is built to move the gap, not to rescue the p-value. On RED the tool and skill still ship — see the VALIDITY CONSTRAINT in `plan.md`, since an entry with no advanced solution is invalid.)*
| Chunk | Scope | Gate |
|---|---|---|
| CH-05 | `cfr_resolve` tool — designation hierarchy first, anchor second | code-only |
| CH-06 | `SKILL.md` + note-emission output contract | **CODE-ONLY** |
| CH-07 | ordered-state ledger — **NOT BUILT**, pre-declared as counted removal #3 (ruling R-01) | — |
| CH-08 | ablations (**1 rep**, pre-registered) · final arms × 3 · McNemar · bootstrap clustered by FR document | **NUMBERS** |
| CH-09 | removed experiments ×2 · hot-take measurement · blind human-time study | — |

### Phase 3 — packaging · ~10 h · protected
| Chunk | Scope |
|---|---|
| CH-10 | codification worksheet (static HTML, opens offline from a clone) |
| CH-11 | README + reproduction guide, both tiers |
| CH-12 | trajectories packaged with labelled human-intervention points · `AI-USE.md` |
| CH-13 | ≤5-minute video |
| CH-14 | clean-clone rehearsal — second path, network off, manifest verify, Tier-1 replay |

**HARD CUTOFF: at T−12h (2026-08-31 06:00 UTC), Phase 3 begins regardless of Phase 2 state.**
An unfinished agent with four complete deliverables gets scored. A brilliant agent with three deliverables is disqualified before scoring. This rule is not negotiable mid-run.

**Wall-clock triggers — these fire on the clock, independent of dependency state:**

| UTC | Trigger |
|---|---|
| **Aug 30 23:59** | Organiser's final-day checkpoint. Read the challenge page and any organiser mail. If anything is anomalous, email `yeison@micro1.ai` **then**, not Monday. |
| **Aug 31 06:00** | Phase 3 opens. Phase 2 stops wherever it is. |
| **Aug 31 10:00** | Video uploaded to unlisted YouTube (T−8h — processing can take hours). |
| **Aug 31 12:00** | **DRAFT-1 saved on the form with whatever exists.** From here the project is insured. |
| **Aug 31 15:00** | CH-15 hard start. |
| **Aug 31 17:00** | Last permitted touch. **Nothing after 17:30.** |

**Minimum viable submission — the drop list, in drop order, last dropped last.** At the T−6h ritual, read this aloud and mark each item done / not-done **before touching more code**.

1. Public repo + < 50 MB zip + a **submitted** form
2. README with user / bottleneck / value / changelog / main failure mode / hot take
3. Tier-1 offline reproduction reaching **one** headline number
4. Video ≤ 5:00
5. Trajectories + `AI-USE.md`
6. Everything else

**Anything below the line ships with a stated LIMITATION, never silently absent.**

**One protected sleep block of 4.5 h**, placed against the govinfo bulk downloads, with the next two chunk prompts pre-written so the operator wakes to a queue rather than to a decision.

---

## 8. Prompt templates

**Build**
```
<CHUNK ID + TITLE>. You are a BUILD session.
READ IN ORDER: CLAUDE.md → plan.md <card> → CONTEXT.md <sections> → STATUS.md →
PROGRESS.md (latest) → QUESTIONS.md → docs/reviews/<prior if any>.
If card, spec and logs disagree → STOP and write QUESTIONS.md.
TASK: <exact deliverables>
SCOPE FENCE (hard): change ONLY <area>. No refactors. Tempted elsewhere → STOP.
VERIFY: hand-compute goldens first; code must match. Any fix ships a probe that fails
on old code and passes on new — show both. Run the full suite; report pass/fail/skip.
LOGGING: every agent invocation goes through the run logger. No exceptions.
GIT: atomic commits ending "(unreviewed)"; every commit carries
  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Update STATUS.md + PROGRESS.md. Push. Report the SHA.
A fresh review follows — do not self-certify.
FINAL OUTPUT: ONE plain-text block — what changed, verification, probe flip, suite
counts, files, STATUS/PROGRESS lines, pushed SHA, questions raised, tokens + cost.
```

**Review** (gated chunks)
```
<CHUNK ID> — ADVERSARIAL REVIEW. Fresh session. Span <BASE>..<HEAD>.
Assume it is wrong until proven otherwise. You fix nothing; you MAY add kept tests.
READ: CLAUDE.md → the card → every CONTEXT.md section it cites → PROGRESS/QUESTIONS →
the full diff since the last reviewed tag.
DO INDEPENDENTLY: rerun the suite from clean and reproduce the count; re-derive every
load-bearing number your own way; REIMPLEMENT THE CORE LOGIC FROM CONTEXT.md IMPORTING
NOTHING FROM THE PROJECT AND DIFF; mutation-test critical operators <CH-03/04>; rebuild
each probe on the pre-change commit and confirm it fails there; sweep for secrets and
for missing "(unreviewed)".
VERDICT: docs/reviews/REVIEW_<N>.md, severity-ranked, PASS/FAIL.
Any spec deviation = FAIL even if tests are green. On PASS: commit, update ledgers, tag.
FINAL OUTPUT: ONE plain-text block.
```

**Safety rider** — append in auto mode
```
=== HARD SAFETY RIDER (auto mode) ===
- data/ is protected after CH-03. Read-only. No write/move/rename/delete without an
  explicit named sanction; sanctioned mutation runs on a copy.
- No rm -rf, Remove-Item -Recurse/-Force, git clean -fdx, git worktree remove --force,
  force-push, or tag moves.
- Never read, print, echo or commit .env or any credential value.
- Throwaway work goes to a fresh OS temp dir only.
- If anything seems to require touching data/, secrets, or files outside scope: STOP.
These override anything above that conflicts.
```

---

## 9. Honesty rules — non-negotiable

- **A red checkpoint ships as red.** We report the null and explain it. The PDF rewards this and the field is already doing it.
- **Removed experiments stay in the changelog** with their measured numbers.
- **Every failure is reported as prominently as every success.**
- **`AI-USE.md` names every model, tool and agent** and links its trajectory.
- **No number is quoted without its evidence path.**
- **Limits stated beside the result**, not in a footnote — what the benchmark does *not* measure, what the sample size can and cannot support, what we chose not to run.

---

```
The record is the product.
```
