# INDEX — every agent trajectory, and what to look at in each

**Deliverable 4.** The brief asks that each trajectory be *"easy to follow from the
agent instructions to the final result"*. So every row below names **where the
instructions are**, **what the agent did**, **where the result landed**, and **what is
worth opening the file for**.

The curation rule is [`SELECTION-RULE.md`](SELECTION-RULE.md), committed at `1afc295`
**before** anything was selected. What it selects is
[`docs/evidence/ch12/selection-applied.md`](../evidence/ch12/selection-applied.md).
Every size, line count and record span below is measured by
[`docs/evidence/ch12/trajectory_facts.py`](../evidence/ch12/trajectory_facts.py) →
[`trajectory-facts.txt`](../evidence/ch12/trajectory-facts.txt).

**36 trajectory files. 43.62 MB. Nothing is curated away — this is an index, not a
filter.**

| class | files | what it is | instructions | result |
|---|---:|---|---|---|
| [build sessions](#build-sessions--11-files-10-sessions) | **11** | the Claude Code sessions that wrote this repository | `prompts/<CHUNK-ID>.md` | the commits of that window |
| [evaluation arms](#evaluation-arms--15-files) | **15** | the thing being measured | `agents/*.md` | `docs/evidence/ch06-a1/`, `docs/evidence/checkpoint/` |
| [probe](#probe--10-files) | **10** | the model-id probe from `QUESTIONS.md` Q1 | `prompts/NIGHT-RUN.md` | `docs/evidence/ch03-model-id/` |
| [adversarial audits](#adversarial-audits--86-subagents-and-no-jsonl) | **0** | 86 subagents that attacked this project's own conclusions | inside the build transcripts | `docs/reviews/`, `docs/evidence/ch11c-sweep/` |

---

## Start here — three files, and what makes each worth the click

**If a judge opens only three, open these.**

### 1. The run where the model overrode its own tool, and published the tool's limit

**[`arms/A1-rep1.jsonl`](arms/A1-rep1.jsonl)** — 2,809,706 B, 925 records.
Note: [`docs/evidence/ch06-a1/EXEMPLAR-composition.md`](../evidence/ch06-a1/EXEMPLAR-composition.md).

Item **`05-8447|75.31`**, instruction 4. `cfr_resolve` returned
`designation_exists: false` for `(b)(1)`. The model did not take the tool's word for
it. It read the `siblings` field, saw `(1)` and `(2)` declared under `(b)` in the
section text, and ruled the instruction **executes anyway** — writing the reason into
the shipped artifact:

> *"cfr_resolve reported designation_exists=false, but (1) and (2) are declared under
> (b) in the section text; **the tool cannot see nested designations**. Siblings field
> confirms both exist."*

That is the deterministic resolver's known blind spot (`QUESTIONS.md` **Q21**, 60 of
128 designations, every misfire one-way) being **caught at run time by the agent, in
writing, in the record a reader gets.** The tool was not fixed — it was outside the
chunk's fence, and the skill compensates in the open instead. This is the single
clearest artifact of what the two capabilities do together, and it is also rendered as
a row in [`docs/worksheet/index.html`](../worksheet/index.html).

### 2. A run carrying `human_checkpoint` records

**[`arms/A1-rep1.jsonl`](arms/A1-rep1.jsonl)** again — **16 `human_checkpoint`
records**, one per item the system refused to decide. Also
[`arms/A1-iter1-rep1.jsonl`](arms/A1-iter1-rep1.jsonl) (17) and
[`arms/A1-rep2.jsonl`](arms/A1-rep2.jsonl) (17).

The checkpoint is **computed in code from the resolution trace, never asked of the
model** — an agent that decides for itself when to escalate is reporting confidence,
not escalating. Three conditions: **C1** the anchor path and the designation path
disagree; **C2** both paths were asked and returned contradictory facts; **C3** one
designation is touched by two instructions, so the answer depends on execution order
and the ordered-state ledger that would resolve it is a **declared, counted removal**.
C3's escalation text names ruling R-01 in its own body: the system says *why* it will
not guess. The whole queue is a section of
[`docs/worksheet/index.html`](../worksheet/index.html).

### 3. A build session where a review FAILED the work

**[`build/NIGHT-RUN-FINAL.jsonl`](build/NIGHT-RUN-FINAL.jsonl)** — 3,696,750 B, 1,659
lines, 537 assistant records. **This is the most valuable file in the directory and it
is more valuable than any clean one.**

It contains **both** CH-03 adversarial reviewers, launched as background subagents with
zero shared context, their **launch prompts verbatim** and their **verdicts verbatim**:

| what | where in the file | verdict |
|---|---|---|
| first reviewer launched | `2026-08-30T21:29:55Z`, `Agent`, *"Adversarial review of CH-03"*, 5,444-char prompt opening *"Assume the work is WRONG until proven otherwise"* | **FAIL** — [`docs/reviews/REVIEW_CH-03.md`](../reviews/REVIEW_CH-03.md) |
| — and it **crashed** before writing its verdict | its own task-notification returns `<status>stopped</status>` | the verdict file says so in its header rather than glossing it |
| re-review of the fix | `2026-08-30T22:25:12Z`, `Agent`, *"Re-review fixed CH-03"* | **FAIL again** — [`REVIEW_CH-03-round2.md`](../reviews/REVIEW_CH-03-round2.md), strike 2, **escalated** |

The first review's finding is the most important defect this project has found in its
own work: **a label-blind script reading only `frdoc` and `section` scored 0.8158** on
the eval set — beating the agent baseline by 17 pp with no model, no CFR text and no
instructions. The eval set was rebuilt; the attack falls to 0.5610.

The second is sharper still, because it is about evidence rather than code: *"The fix
was real; my evidence about it was not."* CH-03 stands at **`reviewed-FAIL ×2 →
ESCALATED`** and is **not claimed to pass** anywhere.

The third FAIL, [`REVIEW_CH-04.md`](../reviews/REVIEW_CH-04.md), was launched from
**[`build/CH-06.jsonl`](build/CH-06.jsonl)** at `2026-08-31T02:07:39Z`. Its opening
line is worth the click on its own: *"The arithmetic is correct and I proved it
independently. The claims wrapped around it are not."*

**All three committed reviews are FAIL verdicts against this project's own work, and
they ship unedited.**

---

## Build sessions — 11 files, 10 sessions

`NIGHT-RUN` was exported **twice**: `NIGHT-RUN-CHECKPOINT.jsonl` is a **byte-exact
prefix** of `NIGHT-RUN-FINAL.jsonl` (asserted in `trajectory_facts.py`), a mid-session
snapshot committed to satisfy `CLAUDE.md` duty 6 before the session continued. Both
ship; neither is deleted. `QUESTIONS.md` **Q42**.

Every session's instructions are the operator's literal opening message, recorded in
the transcript itself: `Read prompts/<CHUNK-ID>.md and execute it fully.`

| trajectory | B | lines | window (UTC) | instructions | what it did → where the result is | what to look at |
|---|---:|---:|---|---|---|---|
| [`CH-00.jsonl`](build/CH-00.jsonl) | 1,105,661 | 418 | 08-30 09:06 → 12:54 | [`prompts/CH-00.md`](../../prompts/CH-00.md) | repo, the constitution, the run logger → `src/runlog.py`, `tools/export_session.py`, `docs/evidence/ch00-*` | **the session that built the exporter that captured every other file here.** One of only **two** transcripts carrying an `AskUserQuestion` — a human decision point put to the operator mid-session and recorded as it happened (`CH-14a.jsonl` is the other) |
| [`CH-01.jsonl`](build/CH-01.jsonl) | 1,433,689 | 672 | 08-30 13:51 → 14:30 | [`prompts/CH-01.md`](../../prompts/CH-01.md) | govinfo EDNOTE harvest → `src/harvest_ednotes.py`, `docs/evidence/ch01-pool/` | a check expected to print 0 printed **2,428**: `N="1"` is a volume number, not a title. **The golden was not edited to agree with the code** — an erratum was appended instead |
| [`CH-02.jsonl`](build/CH-02.jsonl) | 1,689,144 | 709 | 08-30 14:43 → 18:16 | [`prompts/CH-02.md`](../../prompts/CH-02.md) | AMDPAR carry-forward attributor → `src/attribute_amdpars.py`, `docs/evidence/ch02-attributor/` | the gate **FAILED** (0.5080 against 0.90) and the failure was reported rather than tuned; the pair yield cleared. Re-exported once, which is why `AI-USE.md` carried a stale line count until CH-12 |
| [`SPEC-FIX-1.jsonl`](build/SPEC-FIX-1.jsonl) | 1,336,857 | 454 | 08-30 18:18 → 19:04 | [`prompts/SPEC-FIX-1.md`](../../prompts/SPEC-FIX-1.md) | judge a spec change → `docs/evidence/spec-fix-1/verdict.md`. **Zero source, zero `CONTEXT.md` change** | **the session that refused its operator.** It ran a ten-agent panel, the panel went **4–1 against** the verdict it then reached, and it refused anyway: *"the split is right, the replacement gate is not"* |
| [`SPEC-FIX-2.jsonl`](build/SPEC-FIX-2.jsonl) | 786,125 | 341 | 08-30 19:53 → 20:10 | [`prompts/SPEC-FIX-2.md`](../../prompts/SPEC-FIX-2.md) | apply the ruling → `CONTEXT.md` v1.1, `docs/evidence/spec-fix-2/` | the refusal **accepted in full**: the gate stays FAILED and the failure is written into the specification itself. Shortest session in the set, and the only one that ran no subagent |
| [`NIGHT-RUN-CHECKPOINT.jsonl`](build/NIGHT-RUN-CHECKPOINT.jsonl) | 3,123,874 | 1,348 | 08-30 20:31 → 22:36 | [`prompts/NIGHT-RUN.md`](../../prompts/NIGHT-RUN.md) | mid-session snapshot of the run below | kept because duty 6 made it mandatory at that moment; a byte-exact prefix of FINAL |
| **[`NIGHT-RUN-FINAL.jsonl`](build/NIGHT-RUN-FINAL.jsonl)** | 3,696,750 | 1,659 | 08-30 20:31 → 23:13 | [`prompts/NIGHT-RUN.md`](../../prompts/NIGHT-RUN.md) | CH-03 → review → CH-04 → ★CHECKPOINT, unattended → `src/eval_set.py`, `src/score.py`, `src/cfr_resolve.py`, `docs/reviews/`, `docs/evidence/checkpoint/` | **§3 above.** Also: it corrected its own chunk card (*"the alias answers HTTP 200. The claim is false"*) and, after the second FAIL, retracted three of its own published numbers including a *"9 mutations designed, 9 caught"* that it had put in four documents without checking |
| [`CH-06.jsonl`](build/CH-06.jsonl) | 2,302,522 | 1,027 | 08-31 02:03 → 03:28 | [`prompts/CH-06.md`](../../prompts/CH-06.md) | the advanced solution → `agents/A1.md`, `agents/A1-SKILL.md`, `src/a1.py`, `docs/evidence/ch06-a1/` | holds the **CH-04 reviewer** (FAIL, 16 findings). And a **7-minute self-correction**: it raised a schedule question from a remembered duration, then retracted it from the ledger's own `wall_clock_s` — *"I never read a clock… and then reasoned confidently from that fabricated quantity to a ruling"* |
| [`CH-14a.jsonl`](build/CH-14a.jsonl) | 1,632,439 | 733 | 08-31 03:54 → 04:56 | [`prompts/CH-14a.md`](../../prompts/CH-14a.md) | packaging, clean-clone rehearsal → `docs/evidence/ch14-size/`, `ch14-clean-clone/`, `secret-scan/` | the 50 MB blocker **was never a blocker**. Found two tests that fail in the zip a judge opens, *"and one of them was mine"*. Contains a **human interrupt** marker at 04:20:15Z |
| [`CH-11.jsonl`](build/CH-11.jsonl) | 2,456,849 | 987 | 08-31 05:19 → 06:10 | `prompts/CH-11.md` — **untracked, Q41** | README and the five files under it → `README.md`, `REPRODUCE.md`, `SAFETY.md`, `LICENSE`, `THIRD-PARTY.md` | ran a **52-agent** audit over its own drafts whose sharpest finding was against itself: nine literal U+FFFD written into the README from a terminal artefact, **with a paragraph defending them**. Removed |
| [`CH-11c.jsonl`](build/CH-11c.jsonl) | 1,799,806 | 746 | 08-31 07:12 → 08:12 | `prompts/CH-11c.md` — **untracked, Q41** | five factual corrections → `docs/evidence/ch11c-sweep/` | **a correction that was itself false.** While fixing a wrong model name it wrote *"every evaluation arm, temperature 0"*; `B0prime` ran at 1.0. Its own 21-agent sweep caught it within the hour |

**Two cards are not in git** — `prompts/CH-11.md` and `prompts/CH-11c.md`, plus
`prompts/CH-12.md` for the chunk that wrote this index. `prompts/` is protected
read-only in all three of those chunks' fences, so no session can add them.
`QUESTIONS.md` **Q41**; it is a one-line operator action.

---

## Evaluation arms — 15 files

One JSONL per arm-rep, written by `src/runlog.py` and bundled by `src/arms.py`. The
instructions are in [`agents/`](../../agents/) and are **the thing being measured**, so
they are kept separate from the coding sessions' prompts on purpose.

| instructions | arm | what it gets |
|---|---|---|
| [`agents/B0.md`](../../agents/B0.md) | `B0` | the instruction text alone. No CFR text, no tool |
| [`agents/B0-agent.md`](../../agents/B0-agent.md) | `B0-agent`, `B0prime`, `B0-agent-currenttext` | the section text as well |
| [`agents/A1.md`](../../agents/A1.md) + [`agents/A1-SKILL.md`](../../agents/A1-SKILL.md) | `A1`, `A1-iter1`, `A1-minus-tool` | `cfr_resolve` and/or the OFR execution procedure |

| trajectory | B | records | retries | `human_checkpoint` | disagreed with gold | what to look at |
|---|---:|---:|---:|---:|---:|---|
| [`A1-rep1.jsonl`](arms/A1-rep1.jsonl) | 2,809,706 | 925 | **1** | **16** | 23 | **the exemplar run — §1 above.** Accuracy 0.7195 |
| [`A1-rep2.jsonl`](arms/A1-rep2.jsonl) | 2,803,610 | 918 | 0 | 17 | 27 | 0.6707. **The rep that shows A1 is not deterministic**: an agentic loop at temperature 0 samples each turn from a context the last turn shaped |
| [`A1-rep3.jsonl`](arms/A1-rep3.jsonl) | 2,804,905 | 925 | 0 | 16 | 23 | 0.7195 again — rep-to-rep spread 4.9 pp, published beside every single-rep claim |
| [`A1-iter1-rep1.jsonl`](arms/A1-iter1-rep1.jsonl) | 1,605,694 | 1,188 | 0 | 17 | **36** | **the tool alone, and it made the agent WORSE**: 0.5610, −9.8 pp. Its card predicted +8 pp. The most instructive failure in the packet, and the card was not edited |
| [`A1-minus-tool-rep1.jsonl`](arms/A1-minus-tool-rep1.jsonl) | 2,447,989 | 345 | **1** | 16 | 29 | the skill alone: 0.6463, −1.2 pp. Together with the row above: **neither capability helps alone; both together are +17.1 pp superadditive** |
| [`B0prime-rep1.jsonl`](arms/B0prime-rep1.jsonl) | 3,172,976 | 984 | 0 | 0 | **104** | 246 samples — best-of-3 self-consistency at **temperature 1.0**, the only primary-matrix arm off 0, because self-consistency at 0 is a no-op. Result: **+0.0 pp**, exactly B0-agent |
| [`B0-agent-currenttext-rep1.jsonl`](arms/B0-agent-currenttext-rep1.jsonl) | 1,187,233 | 328 | 0 | 0 | 33 | the removed leakage experiment: swap point-in-time text for current text and the average moves −6.1 pp while the **error composition inverts** |
| [`B0-agent-rep1/2/3.jsonl`](arms/) | 1,386,4xx | 432 each | 0 | 0 | 28 each | the strongest baseline, 0.6585. `rep2` is the **median-cost** run the rule selects |
| [`B0-rep1/2/3.jsonl`](arms/) | ~305,600 | 432–434 | 2 / 0 / 0 | 0 | 43 / 43 / 44 | the no-text baseline, 0.4756 — and **not at chance**: it called almost everything executable. `rep1` is the retry-bearing run |
| [`B0-sonnet-rep1.jsonl`](arms/B0-sonnet-rep1.jsonl) · [`B0-agent-sonnet-rep1.jsonl`](arms/B0-agent-sonnet-rep1.jsonl) | 86,985 · 245,063 | 120 · 121 | 0 · **1** | 0 | 11 · 17 | the model-sensitivity subset, **WITHDRAWN** as a harness defect. Shipped anyway, labelled, because a withdrawn arm that vanishes is indistinguishable from one that was never run |

**`docs/trajectories/arms/per-item/` holds 1,446 files and none is tracked** — the
`.gitignore` rule is deliberate and `src/arms.py::bundle()` promises *"EVERY RECORD
SURVIVES — nothing is sampled, summarised or dropped"* into the bundles above. The
bundler once wrote an **empty** bundle without erroring, losing 246 records; that is
disclosed in `QUESTIONS.md` and the verifier that now catches it is
`docs/evidence/ch06-a1/verify_bundles.py`.

---

## Probe — 10 files

`QUESTIONS.md` **Q1** pre-registered, as a fact not to be rediscovered, that the model
alias `claude-haiku-4-5` *"is not on this account and will 404"*. Hard rule 15 required
checking it. **It answers HTTP 200.** These ten one-call trajectories are that check —
two aliases × two dated ids × temperature set and unset — and the dated id is used
anyway, because an alias does not pin a reproducibility claim.

Instructions: [`prompts/NIGHT-RUN.md`](../../prompts/NIGHT-RUN.md). Result:
[`docs/evidence/ch03-model-id/`](../evidence/ch03-model-id/). Four of the ten are the
only `claude-sonnet-5` rows in the ledger that are **not** the withdrawn subset.

---

## Adversarial audits — 86 subagents, and no JSONL

**This class has no trajectory file, and that is a gap in deliverable 4 rather than an
omission from this index.** `QUESTIONS.md` **Q40**.

| fleet | agents | launched from | what survives in the repository |
|---|---:|---|---|
| SPEC-FIX-1 verdict panel | **10** | [`build/SPEC-FIX-1.jsonl`](build/SPEC-FIX-1.jsonl) | `docs/evidence/spec-fix-1/` — the verdict and per-agent cost |
| CH-03 gate reviewers | **2** | [`build/NIGHT-RUN-FINAL.jsonl`](build/NIGHT-RUN-FINAL.jsonl) | `docs/reviews/REVIEW_CH-03.md`, `REVIEW_CH-03-round2.md` + **15** runnable probe scripts (23 files, with their committed outputs) |
| CH-04 gate reviewer | **1** | [`build/CH-06.jsonl`](build/CH-06.jsonl) | `docs/reviews/REVIEW_CH-04.md` + `ch04-probe/` |
| CH-11 shipping audit | **52** | [`build/CH-11.jsonl`](build/CH-11.jsonl) | the nine figures it corrected before they shipped |
| CH-11c shipping sweep | **21** | [`build/CH-11c.jsonl`](build/CH-11c.jsonl) | `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md` — **all 75 findings verbatim from the workflow journal**, not summarised by hand |
| **total** | **86** | | |

**Why there is no JSONL.** `tools/export_session.py` captures a *session*; a subagent is
not a session. Its per-agent records live in the Claude Code workflow journal outside
this repository, and the `Agent` tool writes each transcript to a temp path that is
never exported. **What does ship, for every fleet: the launch prompt verbatim inside
the parent build transcript, the final result verbatim in the task-notification, and
the runnable evidence under `docs/reviews/` or `docs/evidence/`.** For the 21-agent
sweep, `ch11c-agent-sweep.md` is generated from the journal line by line, so no finding
is paraphrased, dropped or re-scored.

**Follow one end to end** to see what is and is not there: open
[`build/NIGHT-RUN-FINAL.jsonl`](build/NIGHT-RUN-FINAL.jsonl) at
`2026-08-30T21:29:55Z` for the launch prompt, then its task-notification at `21:58:38Z`
for what came back — including `<status>stopped</status>`, the crash that
[`REVIEW_CH-03.md`](../reviews/REVIEW_CH-03.md) discloses in its own header rather than
glossing.

---

## Research / ideation agents — before this repository

~90 agents across four design workflows that proposed, attacked and killed candidate
projects, **including two whole projects killed before a line of this one was written**.
They predate the git history and ship as [`context/*-raw.json`](../../context/) beside
the synthesised verdicts. `PROVENANCE.md` §3 dates them; `AI-USE.md` counts them.

---

## What a reader should not mistake this for

- **Nothing here is curated away.** [`SELECTION-RULE.md`](SELECTION-RULE.md) exists so
  that *if* the archive ever had to be trimmed the choice would be auditable. It is
  **not invoked**: the upload is far under cap and the complete set ships.
- **A trajectory is not a result.** The arms' verdicts are scored in
  `docs/evidence/ch06-a1/`; the build sessions' claims are gated by
  `docs/reviews/`, and **three of three gate reviews are FAIL**.
- **Two of the four agent classes cannot be fully replayed from this directory** —
  adversarial audits have no JSONL at all, and the arms' per-item files are ignored in
  favour of their bundles. Both are stated above rather than left to be discovered.
