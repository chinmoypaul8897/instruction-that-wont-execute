# Remediation 2

**Pass:** second remediation · cold read · 2026-08-30
**Scope fence honoured:** this file is the only file created. Nothing was edited, no repo was initialised, no chunk was started.
**Method:** every claim below was checked against the files as they stand now. Claims are labelled **VERIFIED** (I read it or ran it — the number, path or output is given), **INFERRED**, or **UNKNOWN**. 206 read-only audit agents ran across eight independent lenses; every finding they filed was re-checked by an adversarial refuter and a materiality judge, and everything that reaches this document was then re-verified by me against the bytes. Two agent claims were wrong and are recorded as such in §6.

> **A note on a moving target.** `CLAUDE.md` was edited *during* this pass — mtime `2026-08-30 13:03:50 +0530`, after I had already read it. It gained three hard rules (15, 16, 17). This report audits the **13:03 version**. Anything written against the 14-rule version is stale. See §2.1.

---

## 1. Verification summary

### 1.1 Job A — the outstanding findings

| Tier | Items | CONFIRMED | ALREADY-FIXED | PARTIALLY-FIXED | FALSE-ALARM | NOT-WORTH-FIXING |
|---|---|---|---|---|---|---|
| **MAJOR** — §3, M-12…M-35 | 24 | **20** | 2 | 2 | 0 | 0 |
| **MINOR / POLISH** — §4, m-1…m-21 + p-1, p-2 | 23 | **19** | 2 | 2 | 0 | 0 |
| **§7 "What nobody audited"** — O-1…O-25 | 25 | **20** | 4 | 1 | 0 | 0 |
| **§9 "What I could not verify"** | 12 | 6 still open | — | — | **1 killed** | — |
| **Job A total** | **84** | **65** | **8** | **5** | **1** | **0** |

### 1.2 Job B — the cold read

**30 findings that map to no audit item.** Eight would stop a fresh build session outright; four make a review gate unable to do its job; eleven are cross-file contradictions the author introduced while fixing contradictions; seven are false or unsupported statements inside files that ship.

### 1.3 The number the operator asked for

**Every measured number in `CONTEXT.md` still resolves to no evidence path.** `grep -c "docs/evidence" CONTEXT.md` = **0**; `ls -d docs/evidence` = *No such file or directory*. **32 lines** of `CONTEXT.md` carry a ratio, percentage, pp-delta or p-value. Per-number recommendations in §5.

The good news the first pass missed: **three of those groups recompute exactly, today, from artifacts on this machine.** See §5.1. That converts the worst of M-16 from a research task into an hour of copying.

---

## 2. JOB B — the cold read

*The section that matters. Ordered by consequence.*

### 2.1 HALT · `CLAUDE.md` now carries 17 hard rules; two other files still say 14, and one of them is the first line CH-00 reads

**VERIFIED.** `grep -cE '^[0-9]+\. \*\*' CLAUDE.md` = **18 numbered rule lines**, numbered 1–17. Rules 15 (`VERIFY BEFORE YOU RELAY`), 16 (`VERIFY YOUR OWN EDIT LANDED`) and 17 (`THE CLOCK IS NOT A DESIGN INPUT`) are new.

- `prompts/CH-00.md:9` — *"1. `CLAUDE.md` — the session constitution. **All 14 hard rules apply to you.**"*
- `PROCESS.md` §4 carries **14** rules (`sed -n '/^## 4. Hard rules/,/^---/p' PROCESS.md | grep -cE '^[0-9]+\. \*\*'` = 14) under the heading at `PROCESS.md:104` — *"Verbatim into `CLAUDE.md`."*

A CH-00 session is told there are fourteen. It counts seventeen. Under hard rule 1 that is a contradiction between the prompt and the constitution on the first line of the first chunk, and it stops. Worse: rules 15–17 are precisely the rules written to prevent the failures this pass exists to catch, and the prompt tells the session they do not exist.

**FIX — `prompts/CH-00.md:9`, REPLACE:**
```
1. `CLAUDE.md` — the session constitution. **All 17 hard rules apply to you. Rules 15-17 are new and
   are the ones this project has already been burned by; read their italicised worked examples, not
   just the headings.**
```
**AND `PROCESS.md:104`, REPLACE:**
```
Rules 1-14 are copied verbatim into `CLAUDE.md`. `CLAUDE.md` additionally carries rules 15-17
(VERIFY BEFORE YOU RELAY / VERIFY YOUR OWN EDIT LANDED / THE CLOCK IS NOT A DESIGN INPUT), added
2026-08-30 after the architect broke each of them. `CLAUDE.md` is the operative list; this section is
the rationale. Where they differ, `CLAUDE.md` governs.
```
**Hours: 0.1**

### 2.2 HALT · `CLAUDE.md:42` claims a disclosure that does not exist

**VERIFIED.** `CLAUDE.md:42` — *"The rules exist because the failure is not hypothetical — it is in this repository's history, and **it is disclosed in `PROVENANCE.md` rather than hidden**."*

`grep -ni "descartes\|150-250\|verify before\|relay" PROVENANCE.md` → **no match.** `PROVENANCE.md`'s mtime is `11:41`, ninety minutes *before* `CLAUDE.md` gained the sentence. **There is no such disclosure.**

This is the sharpest self-inflicted wound in the repository. The paragraph introducing a rule against relaying unverified claims *is itself an unverified claim*, in the constitution, pointing at a shipping file, on a submission whose pitch is integrity. A judge who follows the pointer — and `PROVENANCE.md:5` explicitly invites the check — finds nothing.

**FIX — `PROVENANCE.md`, INSERT a new §4c after §4b:**
```
## 4c. Three failures of method by the architect, and the rules they produced - 2026-08-30

`CLAUDE.md` hard rules 15-17 were not written in advance. They were written after the architect broke
each of them on this project, and they are recorded here because a process document that records only
its successes is not evidence of a process.

| Failure | What happened | Rule it produced |
|---|---|---|
| Relayed an agent's claim as fact | Called `d.pdf` "micro1's problem PDF". It is a Descartes Systems customs brochure (`pi_customs_info_reference.indd`, 2015). The mislabel propagated into `context/09-COMPLIANCE-AUDIT.md` and into the `.gitignore` comment. | 15 - VERIFY BEFORE YOU RELAY |
| Relayed an unchecked budget | Quoted USD 150-250 for the evaluation. The measured figure at published list prices is ~USD 9 batched - roughly 3x too high, acted on without arithmetic. | 15 |
| Declared edits applied without checking | A batch of programmatic edits silently failed to match; nothing errored; two shipping files ended up disagreeing about the plan. Six contradictions were introduced while fixing contradictions, and only a sweep found them. | 16 - VERIFY YOUR OWN EDIT LANDED |

Each was an agent's or an earlier document's claim, accepted because checking felt slower than
believing. Every one traces to hurrying, which is rule 17. This project's thesis is that a green test
suite is not evidence of correctness. These are the same failure, one level up.
```
**Hours: 0.2**

### 2.3 HALT · `prompts/CH-00.md` never issues the second commit — and both of its safety checks are therefore vacuous

The most consequential single defect in the spec, because it fails **silently and in the flattering direction** — the exact pattern `CONTEXT.md` §8 already identifies as gate-class.

**VERIFIED — there is no `git add` and no `git commit` anywhere in the file.** `grep -n "git add\|git commit" prompts/CH-00.md` returns one hit, `:26`, and it is a *prohibition*: *"Before `git init`, before any `git add`."* The numbered sequence runs 1 (write `.gitignore`) → 2 (`git init`) → 3 (first commit: `.gitattributes` + `.gitignore`) → 4 (verify) → 4b (moves) → 5 (redact) → 6 (create remote) → 7 (push). **"The second commit" is named as a landmark twice and never issued.** The tracked set at `:104` ("What SHOULD be tracked") is phrased as a description, never as a command.

Three consequences, all VERIFIED by reading the sequence:

**(a) The 25 MB / 60-file assertion cannot fail.** `prompts/CH-00.md:79` — *"**VERIFY BEFORE THE SECOND COMMIT.** Run `git status --porcelain` and `git ls-files`. **Assert: fewer than 60 tracked files, and no tracked file over 25 MB.**"* At that instant `git ls-files` lists exactly **two** files, both a few hundred bytes. The assertion that exists to protect a **447 MB** working tree (`du -sh .` = **447M** — the prompt says 446 MB, accurate to rounding) passes trivially and proves nothing.

**(b) The PII sweep passes falsely.** `prompts/CH-00.md:94-96` pipes `git ls-files -z` into grep. Against a two-file index it scans nothing, prints nothing, and `:99` instructs — *"Paste the empty final result into your report."* **The empty result is the pass criterion, and emptiness is guaranteed regardless of what the tree contains.** The operator receives documentary proof of a redaction that never ran.

There is a second, independent bug in the same three lines: `:96` ends `# must print nothing`, but `grep -c` prints `path:0` for every non-matching file. The stated criterion is unachievable even against a correctly populated index.

**(c) There are four PII carriers, not two.** `prompts/CH-00.md:99` names *"`context/09-COMPLIANCE-AUDIT.md` and `context/09b-audit-raw.json`"*. **VERIFIED** by pattern-matching without printing values: the operator's contact detail is also in **`context/04b-intel-raw.json`** and **`context/05b-tournament-raw.json`**, both matched by the `context/*-raw.json` clause of the tracked set. The prompt is right that the list must not be hard-coded; the problem is that the sweep it substitutes does not run.

**(d) A second-order trap.** `context/10-REMEDIATION.md` carries the number too. It escapes today only because M-31's glob bug excludes it. **Fixing M-31 without fixing this sweep makes the leak worse.** That is exactly the un-checked fix interaction the first pass flagged at its §9 item 12.

**FIX — `prompts/CH-00.md`, REPLACE steps 4 and 5 (lines 79 and 91-99):**
```
4. **STAGE THE SHIP-SET, THEN VERIFY, THEN COMMIT — in that order.** The checks below are worthless
   against an empty index, so stage first.

   git add .gitattributes .gitignore
   git add CONTEXT.md plan.md CLAUDE.md PROCESS.md PROVENANCE.md
   git add prompts/ context/00-MASTER-CONTEXT.md
   git add context/[0-9][0-9]-*.md context/*-raw.json
   git rm --cached -r --ignore-unmatch context/01-PROBLEM-PDF.md context/02-ABOUT-ME.md

4a. **NOW ASSERT, against the staged index.** Run these and paste their output into the report:

   git diff --cached --name-only | wc -l                     # assert < 60
   git diff --cached --name-only -z | xargs -0 -I{} du -b {} | sort -rn | head -5   # assert max < 5 MB

   The 5 MB threshold replaces the earlier 25 MB one: nothing this project legitimately tracks is
   larger, and 25 MB would not have caught the 19.6 MB micro1 brand film (m-19).

5. **REDACT — against the staged index, before the commit.** Ask the operator for the two strings
   (personal phone, personal email); hold them in shell variables only, never in a file.

   git diff --cached --name-only -z | xargs -0 grep -l -e "$PHONE" -e "$EMAIL"
   # for each hit: replace the value with [redacted - operator contact detail, ground rule 08], re-stage
   git diff --cached --name-only -z | xargs -0 grep -c -e "$PHONE" -e "$EMAIL" | grep -v ':0$'
   # PASS CRITERION: the second command exits 1 and prints nothing.

   Note the criterion carefully. `grep -c` prints `path:0` for every non-matching file, so "must print
   nothing" is unachievable without the `| grep -v ':0$'` filter. Paste the command AND its exit
   status. Known carriers at time of writing are FOUR, not two: context/09-COMPLIANCE-AUDIT.md,
   context/09b-audit-raw.json, context/04b-intel-raw.json, context/05b-tournament-raw.json. Do not
   trust that list either - it is the sweep that decides.

5b. **SECOND COMMIT.** `git commit` the staged, verified, redacted set.
```
**Hours: 0.4**

### 2.4 HALT · Step 4b's three `git mv` calls abort — the files are not tracked yet

**VERIFIED.** `prompts/CH-00.md:83-86`:
```
mkdir -p prompts/design docs/process/superseded
git mv DIVERGENT-RESEARCH-PROMPT.md prompts/design/
git mv KILL-TEST-PROMPT.md          prompts/design/
git mv BUILD-PHASE-1-PROMPT.md      docs/process/superseded/
```
At step 4b the index holds two files (§2.3). `git mv` requires its source to be tracked; on an untracked path it aborts with `fatal: not under version control, source=…, destination=…` and moves nothing. All three fail in a row, and the session halts **before** reaching §3, which `:260` calls *"the real work of this chunk"*. The stated purpose — shipping the design-phase agent instructions deliverable 4 requires — is silently not achieved.

**VERIFIED** the three files are present and untracked at the repo root — `DIVERGENT-RESEARCH-PROMPT.md` (16,735 B), `KILL-TEST-PROMPT.md` (9,193 B), `BUILD-PHASE-1-PROMPT.md` (10,389 B) — and `prompts/` holds only `CH-00.md`, `REMEDIATION.md`, `REMEDIATION-2.md`. **`prompts/design/` does not exist.** *(The already-applied list records "design prompts moved to `prompts/design/`". The instruction was written; the move has not happened and cannot happen as written.)*

**FIX — `prompts/CH-00.md`, REPLACE the block at :82-87:**
```
mkdir -p prompts/design docs/process/superseded
mv DIVERGENT-RESEARCH-PROMPT.md prompts/design/
mv KILL-TEST-PROMPT.md          prompts/design/
mv BUILD-PHASE-1-PROMPT.md      docs/process/superseded/
git add prompts/design docs/process/superseded
```
*(`git mv` is only correct once the files are tracked. They are not; this chunk is the commit that first tracks them.)* **Hours: 0.1**

### 2.5 HALT · The scope fence still forbids three things the TASK orders

D-1's contradiction 5 was fixed by widening the fence. The widened fence recreated the same defect on three new paths. **VERIFIED** by diffing `:310` against every path the TASK requires:

| Path | Required by | In the fence? |
|---|---|---|
| `.githooks/pre-commit` | `:294` — *"Also install a pre-commit hook."* | **NO** |
| `docs/evidence/runs/cost_ledger.csv` | `:278` — *"Also emit `docs/evidence/runs/cost_ledger.csv`"* | **NO** |
| `docs/process/superseded/` | `:83` — `mkdir -p … docs/process/superseded` | **NO** |
| `docs/trajectories/<run_id>.jsonl` | `:264` — the logger's own output | only `docs/trajectories/build/` is named |

`CLAUDE.md` §"Never" — *"Exceed your scope fence. Tempted elsewhere → STOP."* The rider at `:365` — *"If anything seems to require touching … files outside this chunk's scope: **STOP and report**"* — and it declares itself overriding. Three clean halts.

**FIX — `prompts/CH-00.md:310`, REPLACE:**
```
**Change ONLY:** repo setup (`.gitignore`, `.gitattributes`, `.githooks/`), the canonical skeletons
listed above, `src/runlog.py`, `tests/test_runlog.py`, `tools/export_session.py`,
`tools/render_trajectory.py`, and the directories `docs/trajectories/` (including `build/`),
`docs/evidence/runs/`, `docs/process/superseded/`, `agents/` and `prompts/design/`.
```
**Hours: 0.1**

### 2.6 HALT · The CHECKPOINT decision rule is neither exhaustive nor mutually exclusive

The single go/no-go of the project. **VERIFIED**, `plan.md:64-66`:

- **GREEN** — `B0-agent − B0 ≥ 15 pp, McNemar p < 0.05`
- **AMBER** — `gap present, p ≥ 0.05`
- **RED** — `gap < 8 pp, or B0 ≥ 0.70`

**A hole.** gap = 10 pp, p = 0.01, B0 = 0.55 → not GREEN (gap < 15), not AMBER (p < 0.05), not RED (gap ≥ 8 and B0 < 0.70). **No branch matches.** This is not exotic: it is a *significant but modest* gap, the single most likely way for a real experiment to land between a bold prediction and a null.

**An overlap.** B0 = 0.72, B0-agent = 0.90, p = 0.01 → GREEN by bullet 1 **and** RED by *"or B0 ≥ 0.70"*. **Two branches match and they prescribe opposite actions.**

Under hard rule 1 the session must STOP — at the decision point, with the clock running, holding results it cannot classify.

**FIX — `plan.md`, REPLACE the three decision bullets with a total rule:**
```
**Decision rule — evaluated in this order; the first match wins; the branches are exhaustive.**

0. **LEAK CHECK, first and separately.** If **B0 >= 0.70**, the instruction text is leaking
   executability regardless of the gap. Strip the *quoted anchor text* (keep operation and
   designation) and re-run the gate **once**, then re-enter at step 1 with the new numbers. If B0 is
   still >= 0.70, go to RED. *This is a precondition, not a branch - it previously collided with GREEN.*
1. **GREEN** - gap >= 15 pp AND McNemar p < 0.05 -> Phase 2 proceeds as specified.
2. **AMBER** - gap >= 8 pp and NOT GREEN (either p >= 0.05, or the gap is in [8, 15) at any p)
   -> **Phase 2 PROCEEDS.** The checkpoint enters `CHANGELOG.md` as the Baseline row with exact n,
   gap and p. `GOOD.md` is unchanged. The agent is built to move the gap, not to rescue the p-value.
   If A1 is still p >= 0.05, the README leads with effect size, its confidence interval, and the n
   this design would need for power.
3. **RED** - gap < 8 pp, or step 0 failed twice.

The bands are [0,8) RED, [8,15) AMBER, [15,inf) GREEN-if-significant-else-AMBER. Every
(gap, p, B0) triple lands in exactly one branch.
```
**Hours: 0.3**

### 2.7 HALT · `CONTEXT.md` §1 and §8 specify two different point-in-time texts — the system's core input contract

**VERIFIED**, in the file declared LAW, 172 lines apart:

- `CONTEXT.md:15` (§1, the Goal) — *"reads a US federal final rule's amendatory instructions together with the CFR text **as it stood on the publication date**"*
- `CONTEXT.md:187` (§8) — *"The as-of edition is chosen at **(effective year − 1)**"*

Publication date and *(effective year − 1)* are different selections, and for any rule published in one year with an effective date in the next they resolve to different editions. CH-03 builds the frozen corpus from this. CH-05's `cfr_resolve(…, as_of_date, …)` takes it as a parameter (`:97`). A CH-03 session cannot tell which to implement, and a reviewer reimplementing from `CONTEXT.md` alone builds a different corpus than the build did. Under hard rule 1, STOP.

**FIX — `CONTEXT.md:15`, REPLACE the clause:**
```
...together with the CFR text as it stood immediately before the rule took effect - operationally,
the govinfo annual edition for (effective year - 1), the selection rule stated in full in §8 - and
predicts...
```
*(Take §8's rule, not §1's phrasing: §8's is operational, is what the corpus is actually built from, and carries its own honest bounding paragraph on off-by-one editions.)* **Hours: 0.15**

### 2.8 HALT · The CH-02 FULL gate cannot be executed as specified

This is the mechanism that earns the 30-point row. `PROCESS.md:177` and `:269` require, for gated chunks: *"**reimplement the load-bearing logic from `CONTEXT.md` alone, importing nothing from the project, and diff**"*.

**VERIFIED — CH-02's load-bearing logic is not in `CONTEXT.md`.** `grep -nic "carry-forward\|carry forward\|attribut" CONTEXT.md` = **2**, and both are incidental: `CONTEXT.md:133`, a row in the guards table reading `| **Attributor completeness** | **≥ 0.90 — blocks any headline number** |`, and nothing else. `CONTEXT.md` never describes carry-forward attribution. The algorithm exists only at `plan.md:43` — *"iterate in document order, maintain last-named section"* — which is the one file the reviewer is forbidden to use.

**And "completeness" is never defined anywhere.** `grep -n "completeness" CONTEXT.md plan.md PROCESS.md` returns six lines; **not one gives a numerator or a denominator.** A threshold that *"blocks any headline number"* and carries a three-rung fallback ladder (`plan.md:78`) has no definition. A CH-02 build session cannot evaluate its own done-when and must STOP under hard rule 1 before writing a line.

This is the same shape as the leakage defect: `CONTEXT.md` did not mention it, so no reviewer could have caught it.

**FIX — `CONTEXT.md`, INSERT a new §8b before "### Eval set":**
```
### 8b. Attribution - the instruction-to-section map

An FR document is a sequence of `<AMDPAR>` elements in document order. Most do not name their
section: a numbered instruction names one ("2. The FAA amends § 39.13 by:") and the lettered
sub-instructions beneath it inherit it ("a. Removing Airworthiness Directive (AD) 2020-24-12...",
"b. Adding the following new AD:").

**Carry-forward attribution.** Iterate the `<AMDPAR>` elements in document order, maintaining the last
section explicitly named. An element that names a section sets the carry; an element that names none
is attributed to the current carry. The carry resets at each `<REGTEXT>` boundary. An element
appearing before any section has been named within its `<REGTEXT>` is UNATTRIBUTED.

**Attributor completeness** is the fraction of `<AMDPAR>` elements attributed to exactly one section:

    completeness = attributed_amdpars / total_amdpars_in_scope

both counts printed, and `attributed + unattributed == total` asserted. The denominator is every
`<AMDPAR>` in the FR documents the eval set draws on, not a sample.

**Why the threshold is >= 0.90, and why it is realistic rather than aspirational.** An extractor that
requires an explicit section reference attributes only 27 of 64 `<AMDPAR>` blocks (42%) on
FR 2024-01-03 - within noise of the 0.46 a truncation bug once produced, which poisoned an entire
pilot. The other 58% are inheriting sub-instructions. Carry-forward is the fix for exactly that class.

**Golden fixture, hand-computable before any code (hard rule 4).** FR 2024-01-03, part 39,
section 39.13: instruction 2 names the section; sub-instructions a and b inherit it. Expected 3/3
attributed to section 39.13; a naive explicit-reference extractor scores 1/3. That fixture
discriminates the exact bug the gate exists for.
```
**AND ADD to `plan.md`'s CH-02 card:** `Golden fixture #1 is CONTEXT.md §8b's § 39.13 case, hand-computed before the code is written.`
**Hours: 0.5** — *the 27/64 and 42-`<REGTEXT>` counts come from the first pass's O-10 measurement on `fr20240103.xml`; I did not re-derive them and label them **INFERRED** (§9 item 2).*

### 2.9 MAJOR · The NUMBERS-ONLY review tier is handed inputs that do not exist

**VERIFIED.** `PROCESS.md:173` — the tier *"receives only the committed per-item verdict CSVs and `CONTEXT.md` §7"*, and must *"independently recompute accuracy, the McNemar statistic, the bootstrap CI and the effect size, **confirms the bootstrap resamples documents not items**"*.

- `grep -nic "csv" CONTEXT.md` = **0.** No CSV schema is defined anywhere in the six files.
- `CONTEXT.md` §7 names McNemar exactly once, in the success line at `:136`. It never mentions the bootstrap, clustering by FR document, or effect size. Those live at `plan.md:104` — a file this tier is not given.
- No chunk produces the per-arm config files the tier must diff.

So the reviewer cannot confirm the one thing the tier exists to confirm. This gate is scheduled to run twice: at the CHECKPOINT before its call is acted on, and at CH-08 before any number reaches the README.

**FIX — `CONTEXT.md` §7, ADD after the Guards table:**
```
### Reporting contract - what every arm commits, and what a reviewer recomputes from

Each arm writes `docs/evidence/arms/<arm>-rep<N>.csv`, one row per item, header exactly:

    item_id,fr_document_id,arm,rep,gold,predicted,correct,input_tokens,output_tokens,wall_clock_s,imputed_usd,schema_valid

`item_id` is `<title>-<section>`. `fr_document_id` is the FR citation, and it is the **clustering
unit**: the paired bootstrap resamples FR documents with replacement, never items, because sections
amended by one rule are not independent. `gold` and `predicted` are `WILL_FAIL` / `WILL_EXECUTE`.
`schema_valid` is false when the run emitted no parseable verdict, and a false row scores as WRONG,
never as excluded - the policy is identical for every arm and is pre-registered in `GOOD.md` before
any arm runs. `sum(schema_valid) + sum(not schema_valid) == n` is asserted per arm.

Accuracy is `mean(correct)`. The primary comparison is McNemar's exact test on the paired
(A1, B0-agent) discordant cells. The CI is a paired bootstrap over 10,000 resamples of
`fr_document_id`. Effect size is the accuracy difference in percentage points. A NUMBERS-ONLY reviewer
holding these CSVs and this section can recompute all four without the project's code, and a probe
that resamples `item_id` instead of `fr_document_id` must fail.
```
**Hours: 0.4**

### 2.10 MAJOR · Ruling R-01 declares a merge that never happened — CH-01b's content is simply absent

**VERIFIED.** `plan.md:14` — *"**3. CH-01 and CH-01b merge into one session.** Round-trip saving only."* `grep -n "CH-01b" plan.md` returns **exactly that one line.** There is no CH-01b card, and CH-01's card (`plan.md:35-40`) gained none of CH-01b's content.

R-01 records the merge as a *saving*. It was a *deletion*. Everything CH-01b owned is now unowned:

| Lost with CH-01b | Which finding it closed |
|---|---|
| evidence migration into `docs/evidence/` | **M-16** — the numbers that justify the design |
| the count-matched-sibling yield | **M-17** — the assumption `n ≥ 84` rests on |
| the blind human-time baseline | **M-24**, and the type-4 baseline in **O-15** |
| the 8 reserved item ids, logged before gold is opened | the blindness of the whole study |

**And the consequence that cannot be recovered later.** `plan.md:108` still places the *"**blind human-time study** (8 items by hand, stopwatched, **before seeing gold**)"* in **CH-09**, in Phase 2. Gold is opened at CH-03/CH-04. **By CH-09 the word "blind" is false**, and once gold is open those eight verdicts can never honestly be collected again. `PROCESS.md:201` repeats the CH-09 placement.

**FIX — `plan.md`, INSERT a CH-01b card after CH-01, and DELETE R-01 clause 3:**
```
### CH-01b · Evidence migration + the blind human baseline — GATE: none — runs beside CH-01
**Scope:** make every number in `CONTEXT.md` either re-derived in-repo or migrated with its generator.
1. `docs/evidence/spec-claims/` — re-derive in-repo the counts §6 and §8 depend on; commit the script;
   update `CONTEXT.md` to the re-derived values with their paths beside them.
2. `docs/evidence/pilot/<claim-id>/` — for numbers that cannot be re-derived, copy the generating
   script + input hash + stdout, with a README stating when it ran, that it ran pre-repo, and which
   claim it supports. Label every retained figure `PILOT (pre-competition, n=NN)`.
3. `docs/evidence/hot-take/` — ship `killtest/errata/{arms,arm3,arm4,lookup_loo}.json` plus
   `errata_arms.py` / `errata_score.py`. Do NOT vendor the 11.6 MB IETF corpus; fetch it by URL at
   replay time.
4. `docs/evidence/pilot/ednote-pool/` — copy `probe/ednote_hits.json` with a README recording that it
   came from the eCFR search API before that host began returning 403; retained as the
   pre-registration record of the pool projection, NOT as a reproducible artifact.
5. **Anything neither re-derivable nor migratable is DELETED from `CONTEXT.md`, not shipped bare.**
   That decision is the architect's, recorded in `QUESTIONS.md`.
6. **The human baseline, while it can still be blind.** Reserve 8 `(rule, section)` ids from CH-01's
   defect pool, exclude them from the golden-fixture set, work them by hand with a stopwatch, and
   **record the VERDICT for each item alongside the time** in `docs/evidence/human-time/by-hand-log.md`,
   committed BEFORE gold for those items is opened — the commit timestamp is the proof. Those 8
   verdicts are scored by the same scorer as every arm and published as the **type-4 baseline** row
   ("the manual process people use today"), with n = 8 and "the timer is the author" stated beside the
   number, not in a footnote.
7. **Compute the count-matched-sibling yield on the pool and publish it**, before the eval set is
   built, while there is still time to act on a bad number.
**Done when:** every numeral in `CONTEXT.md` resolves to a `docs/evidence/` path or has been deleted;
the 8 reserved ids are logged with timestamps preceding CH-02's first commit.
```
**AND REPLACE `plan.md:108`'s clause** *"blind human-time study (8 items by hand, stopwatched, before seeing gold)"* **with** `second (worksheet-assisted) pass over CH-01b's same 8 items; publish both times and both accuracies`. **Same edit at `PROCESS.md:201`.**
**Hours: 0.4 for the card; the work itself is 1.5 h at CH-01b**

### 2.11 MAJOR · Removed experiments are "two" in three places and "three" in five

**VERIFIED.**

| Says **three** | Says **two** |
|---|---|
| `plan.md:10` — *"we ship **three**, each with a measured number"* | `CONTEXT.md:220` — *"## 10. Removed experiments — **two**, both planned"* |
| `CONTEXT.md:95` — *"declared in advance as **counted removal #3**"* | `plan.md:109` — CH-09 done-when: *"**both** removed experiments have numbers"* |
| `CONTEXT.md:107`, `plan.md:101`, `PROCESS.md:199` | `PROCESS.md:201` — *"removed experiments **×2**"* |

**CH-09 is the chunk that produces them, and its done-when says two.** A session that satisfies its card ships two — and R-01's entire justification for not building the ledger (*"three counted removals is a better changelog than three kept capabilities"*) evaporates unnoticed. The brief rewards removed experiments and most entrants will have none; this is a self-inflicted loss of the strongest thing in the plan.

**FIX — `CONTEXT.md:220`, REPLACE the heading:** `## 10. Removed experiments — three, all planned, all with a measured class size` — **and after removed experiment 2, INSERT:**
```
**3. The ordered-state ledger — pre-declared NOT BUILT (ruling R-01), with its measured justification
published beside the reason it was cut.** State-carry sensitivity — instruction *k+1* reads the state
instructions *1..k* left — fires on **833/1,984 = 42.0%** of corpus items, and on 31/82 of the pilot
pool: two independent counts, not label-correlated (16 defective / 15 executable). That is the
measurement that made it worth building. It was cut so that two capabilities could each be traced to a
numbered failure rather than three rushed. The iteration card ships; the code does not.
```
**AND REPLACE `plan.md:109`:** `**Done when:** all three removed experiments have numbers; hot take has its two-corpus measurement.` **AND `PROCESS.md:201`:** `removed experiments ×3`. **Hours: 0.2**

### 2.12 MAJOR · CH-08's gate is specified three ways, and CH-14's five steps belong to no chunk

**CH-08. VERIFIED:** `plan.md:103` — *"### CH-08 · Ablations and final arms — **GATE: none**"*. `PROCESS.md:200` — *"| CH-08 | … | **NUMBERS** |"*. `PROCESS.md:173` — *"Applies to the CHECKPOINT before its call is acted on, and to **CH-08 before any number reaches the README**."* CH-08 produces every quotable number in the submission. **FIX — `plan.md:103`:** `### CH-08 · Ablations and final arms — GATE: **NUMBERS-ONLY** (PROCESS.md §6)`.

**CH-14. VERIFIED:** the Phase-3 run order (`plan.md:119-127`) names **CH-14a** (*"early rehearsal — fresh venv from pinned `requirements.txt` (Python 3.12.2), network off, manifest verify, Tier-1 replay"*) and **CH-14b** (*"final rehearsal from the finished repo; secret scan over full history"*). The single CH-14 card (`plan.md:158-165`) has **five** numbered steps. Steps 3 (build the zip), 4 (extract and replay from the extraction) and 5 (write `SUBMISSION.md`) are allocated to **neither**. **The submission archive — the artifact CH-15 uploads — has no owner in the run order.**

Take M-32's reorder while splitting, because step 3 currently builds the zip *before* step 5 writes the index the zip is supposed to contain (`git archive HEAD` exports committed content only).

**FIX — `plan.md`, REPLACE the CH-14 card with two:**
```
### CH-14a · Early rehearsal — Phase 3, first — 06:00 UTC
1. Fresh venv from pinned `requirements.txt` (Python 3.12.2 — the build interpreter; state it),
   network off, manifest verify, Tier-1 replay, following `REPRODUCE.md` line by line.
2. Run it once more under WSL or `python:3.12-slim`. "A clean environment" is not "a second directory
   on the same machine".
**Done when:** Tier-1 replay is green in both environments, or the failure is reported with time to fix it.

### CH-14b · Secret scan, index, archive, and the replay that matters — Phase 3, eighth
1. **Secret scan with a named tool and a pass criterion.** `gitleaks detect --source . --log-opts="--all"`
   over the full history, plus an explicit regex sweep of `docs/trajectories/**/*.jsonl` for `sk-ant`,
   `AIza`, `Bearer `, the operator's phone and email, and the funded key's first eight characters.
   PASS = zero findings. Commit the tool version and the clean output to `docs/evidence/secret-scan/`.
   A scan with no recorded criterion is not a scan.
2. Write `SUBMISSION.md` at the repo root listing the six items the FAQ names — repository, archive,
   tests, README, agent-use evidence, demo video — each with its path or URL, plus the repository URL
   and the video URL. **Commit it.**
3. Build `submission-<short-sha>.zip` with `git archive --format=zip HEAD` from **that** commit.
   **Assert < 50 MB.**
4. **Extract the zip to a fresh temp directory and run the Tier-1 replay FROM THE EXTRACTION.** The zip
   is what a judge opens; it is the thing that must work.
5. Record the zip's SHA-256 in `SUBMISSION.md`'s footer and in the README, noting that the footer hash
   necessarily post-dates the archive.
**Done when:** the zip is under 50 MB and Tier-1 replay passes from the extracted copy, network off.
```
**Hours: 0.4**

### 2.13 MAJOR · `PROCESS.md` §7 was never resynced — Phase 3 is missing four entries and understates its own protected window

**VERIFIED.** `PROCESS.md:203-210` lists five chunks — CH-10, CH-11, CH-12, CH-13, CH-14 — under *"### Phase 3 — packaging · **~10 h** · protected"*. `plan.md`'s Phase 3 run order has **nine** entries: CH-14a, CH-13, CH-12, CH-11, **CH-11b**, CH-10, **DRAFT-1**, **CH-14b**, **CH-15**.

The already-applied list records "Phase 3 reordered", "CH-11b voice pass added", "CH-15 Submit added". **All three landed in `plan.md` only.** `PROCESS.md` still shows the old set, the old order, and no run order at all — while `CLAUDE.md`'s read order sends every session to *"`PROCESS.md` §6–§7 for the gate policy and the clock"*, so a Phase-3 session reads the stale table first.

The protected window is 06:00 → 18:00 UTC on Aug 31 = **12.0 h exactly**, and the reconciled Phase 3 the reorder came from totals **12.0 h**. `~10 h` understates it by two hours and leaves no room for the two chunks the table omits.

**FIX — `PROCESS.md` §7, REPLACE the Phase 3 block with a pointer rather than a duplicate**, because a second copy of a nine-row table is how this went stale in the first place:
```
### Phase 3 — packaging · **12.0 h — the full protected window, with no slack** · opens 06:00 UTC Aug 31

**`plan.md`'s Phase 3 run-order table is authoritative for the chunk list, the order and the wall-clock
gates.** It is not duplicated here. Nine entries: CH-14a · CH-13 · CH-12 · CH-11 · CH-11b · CH-10 ·
DRAFT-1 · CH-14b · CH-15. **Run order is NOT the chunk numbering** — the video runs second so that its
own T−8h deadline is reachable.
```
**Hours: 0.2**

### 2.14 MAJOR · `PROVENANCE.md` — the ground-rule-02 artifact — contradicts the plan in three places and overstates one check

`PROVENANCE.md` ships, and `PROVENANCE.md:5` invites verification: *"Every claim below is checkable against file modification times, git history, and the public URLs given."* Four problems, all **VERIFIED**:

**(a) It names the wrong model for every arm.** `PROVENANCE.md:92` — *"| Anthropic API (`claude-sonnet-5`) | commercial, per terms | **every evaluation arm** |"*. The binding ruling is `prompts/CH-00.md:174` — *"Model: **claude-haiku-4-5**, THE SAME MODEL FOR EVERY ARM (fairness — CONTEXT.md section 4)"*, at an operator ceiling of USD 20 with a USD 18 hard stop in code. `grep -n "haiku" PROVENANCE.md` = **no match**: the model that will run every arm is named nowhere in the disclosure file, and the model that will not is asserted as fact. A hard-rule-13 failure in the file whose entire job is disclosure.

**FIX — `PROVENANCE.md:92`, REPLACE the row with two:**
```
| Anthropic API - `claude-haiku-4-5` via the Message Batches API | commercial, per terms | every evaluation arm; the same model for all, which is what makes the comparison fair (`CONTEXT.md` §4) |
| Anthropic API - `claude-sonnet-5` | commercial, per terms | the model-sensitivity check only: B0 and B0-agent re-run over 20 items at the checkpoint, to report whether the gap holds across model tiers |
```

**(b) It lists a capability that ruling R-01 cancelled.** `PROVENANCE.md:18`, under *"## 1. Built entirely during the competition"* → *"- `cfr_resolve`, `SKILL.md`, **the ordered-state ledger**"*. R-01 states the ledger is **NOT BUILT** (`CONTEXT.md:95`, `:107`; `plan.md:9`, `:100`; `PROCESS.md:199`). A judge reading `PROVENANCE.md` is told the project built a thing it deliberately did not build — and it is the removal the changelog leans on. **FIX:** replace with `- \`cfr_resolve\` and \`SKILL.md\` (the ordered-state ledger was pre-declared NOT BUILT — ruling R-01 — and ships as counted removal #3 with its measured justification)`.

**(c) §4b's decoded-passage count is wrong, and its reassurance is unsafe.** `PROVENANCE.md:80` — *"| Passages marked *(decoded)* — our analysis, not micro1's words | **4**, all in analysis sections (capability menu, deliverable→rubric mapping, what the examples share). **None is a requirement**, and no downstream document quotes one as authoritative. |"*

**VERIFIED — there are six.** `grep -ni "decod" context/01-PROBLEM-PDF.md`: `:57` *(decoded)*, `:95` `> **Decoded:**`, `:147` ***(decoded checklist)***, `:229` *(decoded)*, `:280` *(decoded)*, `:315` *(decoded — my analysis, not micro1's words)*. The row names three, counts four, and the file has six.

The one that matters: **`:147` is headed "### Evaluation hard requirements *(decoded checklist)*"**. A decoded checklist titled *Evaluation hard requirements* is requirement-shaped by construction, and `:95`'s decoded note governs comparison fairness, which `CONTEXT.md` §4's fairness rules rest on. *"None is a requirement"* is not supportable as written.

**FIX — `PROVENANCE.md:80`, REPLACE the row:**
```
| Passages marked *(decoded)* — the extracting agent's analysis, not micro1's words | **6**: `:57` capability menu · `:95` a note on comparison fairness · `:147` "Evaluation hard requirements" · `:229` deliverable→rubric mapping · `:280` what the examples share · `:315` strategic read. **Two of the six are requirement-shaped** — `:147` by its title, `:95` because `CONTEXT.md` §4's fairness rules lean on it. Both were re-read against the original PDF; neither adds an obligation the verbatim text does not carry, and the verbatim text governs where they differ. |
```

**(d) §2 dates all of `scraper/` to before kickoff; most of it is after.** `PROVENANCE.md:26` — *"**2026-08-27, approximately 21:45 UTC — seventeen hours before kickoff.**"*, covering `scraper/`. **VERIFIED** with `TZ=UTC stat -c '%y %n' scraper/*`: **8 entries** fall at 2026-08-27 21:42–21:45 ✓, and **36 entries** fall at **2026-08-29 03:13–06:21 UTC** — twelve to fifteen hours *after* the 2026-08-28 15:00 kickoff (`portfolio.cjs`, `work.cjs`, `li.cjs`, `hn.cjs`, `he.mjs`, and 31 `rd_*` Reddit/YouTube/X intel dumps).

Nothing improper happened — post-kickoff competitive research is ordinary work, and `scraper/` is git-ignored either way. The defect is that the file makes a checkable claim, invites the check at `:5`, and the check fails.

**FIX — `PROVENANCE.md:26`, REPLACE the heading and add the second paragraph:**
```
**2026-08-27, approximately 21:45 UTC — seventeen hours before kickoff.**

- `scraper/recon.cjs`, `sections.cjs`, `sections2.cjs`, `mapimg.cjs`, `slice.cjs` and their
  `package.json` — Playwright recon scripts written to read the **public** HackerEarth challenge page.
- `context/00-MASTER-CONTEXT.md` — an extraction of that public page, including content present only
  inside images (the rubric weights, the timeline, the registration deadline).

**The rest of `scraper/` is dated 2026-08-29 03:13-06:21 UTC — after kickoff — and it is stated here
because file timestamps are the proof this document offers.** Those are competitive-intelligence
scrapes (Reddit, YouTube, X, LinkedIn, the HackerEarth page) and personal-portfolio scrapes run during
the competition. They are not part of the submitted system and are git-ignored. They are disclosed
because a reader taking the invitation at line 5 would otherwise find a discrepancy the file did not own.
```
**Hours: 0.4 for all four**

### 2.15 MINOR-plus · `CONTEXT.md` is still "v1.0 · Initial" after a day of amendment

**VERIFIED.** `CONTEXT.md:4` — *"**Version:** v1.0 · 2026-08-30 03:20 UTC"*. Real mtime **`2026-08-30 12:18:58 +0530` = 06:48 UTC**, and the file has been amended repeatedly since 03:20: the leakage-strip subsection (`:170-191`), ruling R-01 (`:95`, `:107`), the withdrawal of "+32 pp" (`:49`), the state-carry / redesignation split (`:110`, `:225`). `CONTEXT.md:256-260` — the change log — carries exactly **one** row: *"| v1.0 | 2026-08-30 03:20 UTC | Initial. |"*

`PROCESS.md:75` describes this file as *"**the spec — THIS FILE IS LAW.** Versioned, architect-authored only"*. It is not versioned. A reviewer cannot state which revision they reviewed against, and `CLAUDE.md`'s read order tells sessions to STOP when card, spec and logs disagree — with no way to tell a defect from a stale copy.

*Both verifiers rated my original MAJOR as OVERSTATED and I accept that: `CONTEXT.md` §13 is not in the read order, so nothing halts on it.*

**FIX — `CONTEXT.md:4` → `**Version:** v1.4 · <UTC at edit time>`, and REPLACE §13's table:**
```
| Version | Date (UTC) | Change |
|---|---|---|
| v1.0 | 2026-08-30 03:20 | Initial. Assembled from `08-FINAL-CALL.md` §5 over `07-KILL-TEST.md` §7. |
| v1.1 | 2026-08-30 05:40 | §8: leakage strips added (`<EDNOTE>`/`<EFFDNOTP>`/`<CITA>`/`<EAR>`), measured on `CFR-2024-title40-vol5`, with the honest bounding paragraph. Lost in transcription from `08-FINAL-CALL.md` §5; recovered by the compliance audit (D-2). |
| v1.2 | 2026-08-30 06:10 | §3: "+32 pp" withdrawn in favour of "+27.3 pp"; the pilot figures 0.545 / 0.5855 / 0.52 labelled provenance-unverified. §6/§10: "order-sensitive" split into its two distinct senses (state-carry 42.0%, redesignation-collision 1.31%). |
| v1.3 | 2026-08-30 06:48 | §6: ruling R-01 — capability 3, the ordered-state ledger, NOT BUILT, pre-declared as counted removal #3. |
| v1.4 | <this edit> | §1/§8 as-of selection reconciled · §8b attribution added · §7 reporting contract added · §5b entry point added · §9 human-checkpoint trigger rule added · §10 third removal added · §12 Prior et al. citation corrected. See `context/11-REMEDIATION-2.md`. |
```
**Hours: 0.2** — *the v1.1–v1.3 timestamps are reconstructed from content, not from a log; **INFERRED**, and the architect should replace them with the real ones if known.*

### 2.16 MAJOR · The API spend plan is USD 20; the code stops at USD 18 — and the item the ceiling cancels is the false-RED guard

**VERIFIED**, `prompts/CH-00.md`:
- `:182` — *"plan: ~$9 matrix + ~$5 rerun reserve + **~$3 model-sensitivity** + ~$3 slack"* → **sums to USD 20.00**
- `:184` — *"MODEL-SENSITIVITY CHECK (**~$2**, run AT THE CHECKPOINT…)"* — **two lines later, a different figure for the same item.** `plan.md:81` also says `~$2`.
- `:192` and `:280` — *"REFUSES to start a run that would cross **USD 18**"*, `SPEND_CEILING_USD = 18.00`.

The itemised plan exceeds the enforced ceiling. The logger raises *before starting a run*, so the overrun surfaces not as an overspend but as a refusal — and the item at the end of the queue is the **model-sensitivity check**, which `plan.md:81` describes as the guard against a **false RED**: *"where a cheap model simply fails to use the CFR text and we kill a sound project on weak inference."* **The ceiling can silently disable the guard against killing the project.**

Two further gaps. The `$18.14 / $9.07` derivation is computed at **Haiku** list prices — `11.8M × $1.00 + 1.26M × $5.00 = $18.10`, ✓ **VERIFIED** arithmetic, and `$18.14 / 2 = $9.07` ✓ — but the sensitivity check runs on **`claude-sonnet-5`**, whose price basis is never stated, while hard rule 10 requires `price_basis` on every run. And *"~2,520 calls"* has no derivation anywhere (**UNKNOWN**, §9).

**FIX — `prompts/CH-00.md`, REPLACE Q1's budget block (:179-184):**
```
Measured budget, at published list prices (Haiku 4.5 = $1.00/M in, $5.00/M out; Sonnet-class =
$3.00/M in, $15.00/M out - both recorded as `price_basis` on every run):
  full matrix ~2,520 calls = 11.8M in / 1.26M out  ->  standard $18.14, batched $9.07
  (2,520 = 5 model arms x 3 reps x ~84 items = 1,260, plus 2 ablation arms x 1 rep x ~84 = 168,
   plus A1's multi-turn calls at ~2 turns per item. RECOMPUTE at CH-04 and correct this line.)

  plan, against the USD 18.00 CEILING ENFORCED IN CODE - not against the operator's USD 20:
    ~$9.10  full matrix, batched
    ~$2.00  model-sensitivity check (Sonnet; 40 calls = 20 items x 2 arms)   <-- RESERVED, NOT LAST
    ~$4.00  rerun reserve
    ~$2.90  slack
    -------
    $18.00  = the coded ceiling exactly. Nothing is planned above it.

  THE SENSITIVITY CHECK IS RESERVED, NOT QUEUED. The logger reserves its ~$2.00 at start-up and
  refuses matrix runs that would eat the reservation. It is the guard against a FALSE RED, and a
  budget that can cancel the guard against killing the project is not a budget.
```
*(and delete the `~$3` at `:182`, keeping `~$2`, so the two figures agree)* **Hours: 0.25**

### 2.17 MAJOR · `PROCESS.md` §4 says its 14 rules go "Verbatim into `CLAUDE.md`". Twelve differ, and two lose content

**VERIFIED** by diffing the two lists rule by rule. Beyond §2.1's three extra rules, twelve of fourteen differ in wording. Two differ in substance — and in both cases `CLAUDE.md`, the file every session actually reads, is the poorer copy:

| Rule | `PROCESS.md` carries | In `CLAUDE.md` |
|---|---|---|
| **9 DETERMINISM** | *"`.gitattributes` = `* -text` on line one. Frozen corpus under SHA-256 manifest."* | both clauses **absent** |
| **12 SECRETS** | *"**History scanned before the repo goes public.**"* | **absent**; replaced by *"To confirm a key exists, read only its name."* |

A session reading `CLAUDE.md` alone never learns the history-scan duty — and `PROCESS.md:104`'s "Verbatim" is precisely why nobody would think to diff them. **FIX:** §2.1's replacement text, plus restore the two dropped clauses into `CLAUDE.md`'s rules 9 and 12. **Hours: 0.1**

### 2.18 MAJOR · The brief's "one challenging case" requirement has no owner

**VERIFIED**, `context/01-PROBLEM-PDF.md:131` — *"**Include one challenging case and explain what it revealed.**"* — and `:153`'s checklist — *"**≥1 deliberately hard case**, with an explanation of what it revealed"*. A hard, checkable requirement.

`grep -nic "hard case\|hard-case\|challenging case" plan.md PROCESS.md` = **0 and 0.** `CONTEXT.md` §9 names three exemplars; no chunk writes up what any of them revealed.

**FIX — ADD to CH-08's done-when:**
```
`docs/evidence/hard-case/` for 12 CFR 702.504 -> 702.304: every arm's full `resolution_trace` side by
side, which arms got it right, and what the failure taught - that a partial-read agent rules correctly
for the wrong reason. This is the brief's required challenging case; it is the case the video walks
through and the case the README explains.
```
**Hours: 0.5**

### 2.19 MAJOR · `PROCESS.md` §3 says all twenty files are "Created at CH-00"; CH-00 creates eight

**VERIFIED.** `PROCESS.md:71` — *"Created at CH-00."* — heads a twenty-row table. CH-00's TASK creates `STATUS.md`, `PROGRESS.md`, `QUESTIONS.md`, `CHANGELOG.md`, `AI-USE.md`, `GOOD.md`, `src/`, `tests/` and three directories. The rest — `README.md`, `REPRODUCE.md`, `SUBMISSION.md`, `LICENSE`, `THIRD-PARTY.md`, `SAFETY.md`, `data/`, `agents/`, `docs/evidence/`, `docs/progress/`, `docs/reviews/`, `prompts/design/` — belong to later chunks or to nobody. A literal CH-00 session either overreaches its fence or stops.

**Three rows have no owner in any chunk. VERIFIED:** `SAFETY.md` (`grep -c "SAFETY.md" plan.md` = **0**), `docs/progress/` and `docs/reviews/` (**0** in `plan.md`, though `CLAUDE.md:12` and `:72` both depend on them). **And `tools/` has no row at all**, though CH-00 builds `tools/export_session.py` and `CLAUDE.md` duty 6 depends on it.

**FIX — `PROCESS.md:71`, REPLACE:** `**Owned by the chunk named in the right-hand column.** Chat history is not a record. If it matters it lives in a file in the repo.` — add a `Created by` column (CH-00 for the eleven it creates · CH-11 for `README.md`/`REPRODUCE.md`/`THIRD-PARTY.md`/`LICENSE`/`SAFETY.md` · CH-14b for `SUBMISSION.md` · CH-03 for `data/` · CH-01b for `docs/evidence/`), and add a `tools/` row. **Hours: 0.3**

### 2.20 The rest of the cold read — one line each, all VERIFIED

| # | Finding | Fix |
|---|---|---|
| B-1 | `CONTEXT.md:25` declares the levels `exact` / `whitespace-collapsed` / `alphanumeric-only`; `:81`'s output contract emits `"exact\|whitespace\|alphanumeric\|none"`. Two of three names differ — in the field §1 says must never be silently altered. *(= M-33.)* | Adopt the §5 enum in §1 verbatim; it also carries the `none` case §1 omits. |
| B-2 | `CONTEXT.md:47` says the pilot figures *"come from `context/07-KILL-TEST.md` §7.3"*. **`0.5855` appears 0 times in that file** — it is at `08-FINAL-CALL.md:111`. The single `0.52` hit in `07-KILL-TEST.md` (`:924`) is *"the prior work's 0.5250"* — a third party's number. Only `0.545` is where the pointer says. | Cite `08-FINAL-CALL.md:110-111` for 0.5855; establish what 0.52 measured before it ships. |
| B-3 | `plan.md:132` — *"The anti-slop clause is worth **up to 5 of the 20** End-to-End points"*. No such sub-allocation exists in either source; the brief says only that 20 points partly ride on it. A number invented inside a fix applied this cycle. | Use the brief's own words: *"the anti-slop clause sits inside End-to-End Quality (20 pts) and is explicitly scored"*. |
| B-4 | `plan.md:155` requires CH-13's video URL in `README.md` and `SUBMISSION.md`; CH-13 runs **2nd** in Phase 3, README is 4th, `SUBMISSION.md` 8th. CH-13 cannot satisfy its own done-when. *(= m-20.)* | CH-13's done-when ends at "uploaded, plays signed-out, under 5:00"; routing the URL moves to CH-11 and CH-14b. |
| B-5 | `plan.md:136` requires CH-10's worksheet to render *"the collision trace"* and *"the human-checkpoint queue"*. The collision detector is removed experiment #2 and the ledger it was built on is NOT BUILT. | Drop "the collision trace"; keep the queue, sourced from M-22's trigger rule. |
| B-6 | `PROCESS.md` §6's gate table routes CH-05 to *"everything else \| self-check"*; `plan.md:92` and `PROCESS.md:197` both say `code-only`. §6 contradicts §7 of the same file. | Add a CH-05 `code-only` row to §6's table. |
| B-7 | `prompts/CH-00.md:104` lists `process/` in the tracked set. `ls -A process/` = **0 entries**; git cannot track an empty directory. | Delete `process/` from the clause; `docs/process/superseded/` is the real destination. |
| B-8 | `prompts/CH-00.md:322`'s DONE WHEN says *"`QUESTIONS.md` carries Q1"*. The prompt seeds **Q1, Q2 and Q3**, and `CLAUDE.md`'s precedence line depends on Q3 existing. | `QUESTIONS.md` carries Q1, Q2 and Q3. |
| B-9 | `CLAUDE.md` duty 6 — *"A chunk whose transcript was not exported is not done"* — is absent from CH-00's DONE WHEN. | Add `tools/export_session.py CH-00 has run and its output is committed`. |
| B-10 | `plan.md:170` states the form's four fields were *"verified from inside it, 2026-08-30"*. Nothing on disk records the check. | One screenshot into `docs/evidence/access/`, referenced from Q2. |
| B-11 | `CONTEXT.md:236` (§11) states *"+27.3 pp"* unlabelled, while `:49` (§3) rules it must carry *"pilot, pre-competition, n=11"* **everywhere it appears**. | Add the label at `:236`. |
| B-12 | `context/01-PROBLEM-PDF.md`'s stated source is `micro1 - First Hackathon97ce7c5.pdf`; `PROVENANCE.md` §4b records a check against it but names no method and no checker. | §4b gains one line: who checked, against which path, and how far. See §6 FA-1. |

---

## 3. CONFIRMED MAJORS from §3 (M-12 … M-35) — grouped by target file

All **VERIFIED** against the current files by the greps shown. Fix text is ready to paste. Items already covered in §2 are cross-referenced, not repeated.

### 3.1 → `prompts/CH-00.md`

**M-12 · `agents/` is named twice and populated by nothing. — 1.0 h**
**VERIFIED:** `grep -n "agents/"` across the six files returns exactly two hits — `PROCESS.md:90` (the files table: *"one file per evaluation arm: the exact instructions that shape it — **deliverable 1**"*) and `prompts/CH-00.md:310` (the scope fence). **No TASK step creates or fills it, and no later chunk mentions it.** Git cannot track an empty directory, so `agents/` would not exist in the repo at all. Deliverable 1 requires *"the instructions that shape each agent"* as shipped files.

**FIX — ADD a row to `prompts/CH-00.md` §2's skeleton table:**
```
| `agents/` | one file per arm — `B0.md`, `B0-agent.md`, `B0-prime.md`, `A1.md`, `A1-SKILL.md`, and the `cfr_resolve` tool schema — plus `agents/load.py`, a loader returning `(text, sha256)`. Create the directory, the loader, and a stub for each of the five arms now (a stub is a heading plus `TODO: filled at <chunk>`) so the directory is tracked. Arm scripts READ these files; they never embed prompt strings. `run_start.agent_instructions` records the file path AND its SHA-256 beside the resolved text, so a judge can confirm the trajectory used the shipped instructions. The CHECKPOINT fills `B0.md` and `B0-agent.md`; CH-05/CH-06 fill `A1.md` and `A1-SKILL.md`; CH-08 fills `B0-prime.md`. |
```

**M-13 · The secret scan names no tool and no pass criterion, and the logger creates the exposure it must cover. — 0.5 h**
**VERIFIED:** `grep -ci "gitleaks"` across all six files = **0**. `plan.md:160` is the entire specification: *"2. Secret scan over the **full history**, not just the working tree."* No tool, no criterion, no artifact. Meanwhile `prompts/CH-00.md:268` has the logger write `agent_instructions` and raw `tool_response.output` into committed files — so the logger *creates* the exposure the scan must catch.
**FIX — ADD to `prompts/CH-00.md` §3:** `**The logger WHITELISTS the fields it writes** rather than dumping raw tool output: for each record type only the fields in the table above are serialised, and any other key is dropped with a counted warning. A logger that commits whatever a tool returned will eventually commit a key.` **AND** CH-14b step 1, whose text is in §2.12.

**M-15 · The architect's state lives in chat, which `PROCESS.md` itself forbids. — 0.4 h**
**VERIFIED:** `grep -c "ARCHITECT.md"` across all six files = **0**. `PROCESS.md:71` — *"Chat history is not a record. If it matters it lives in a file in the repo."* `PROCESS.md:37` — the architect must be this session because *"Re-bootstrapping costs hours we don't have."* Both cannot be true. **This pass proved the risk concretely: `CLAUDE.md` changed under a running audit and nothing in the repo recorded that it had.**
**FIX — ADD a row to `prompts/CH-00.md` §2's skeleton table:**
```
| `ARCHITECT.md` | the architect's state, outside chat. After every chunk, a dated 12-line block: current chunk and verdict · next chunk · every number verified so far with its evidence path · open rulings · which spec files changed since the last block and at what UTC time · the read-order a replacement architect needs. The next two chunk prompts stay pre-written in `prompts/` at all times, so the operator wakes to a queue rather than to a decision. |
```

**M-31 · The tracked-set glob silently drops the entire verification record. — 0.1 h**
**VERIFIED:** `prompts/CH-00.md:104` enumerates `context/0[3-9]*.md`. `ls context/0[3-9]*.md` matches **exactly seven files** and **does not match `context/10-REMEDIATION.md`** (135 KB), nor this file, nor any future `context/1N-*.md`. The whole audit-and-remediation record would never ship.
**FIX — REPLACE that clause with:** `` `context/00-MASTER-CONTEXT.md`, `context/[0-9][0-9]-*.md` **except** `context/01-PROBLEM-PDF.md` and `context/02-ABOUT-ME.md`, and the `context/*-raw.json` agent outputs ``
**⚠ ORDERING — this fix is unsafe on its own.** `context/10-REMEDIATION.md` carries the operator's phone number (**VERIFIED** by pattern count; value never printed). Widening the glob adds a fifth PII carrier to the ship-set. **Apply §2.3's staged-and-verified sweep first, or this fix leaks.** This is exactly the fix-interaction class the first pass listed as unchecked at its §9 item 12.

**M-35 / O-25 · The `d.pdf` mislabel is still live, in a file that ships. — 0.2 h**
**VERIFIED, independently and from scratch:** `strings d.pdf` returns `/Title(pi_customs_info_reference.indd)`, `/Creator(Adobe InDesign CS6 (Windows))`, `/CreationDate(D:20150204122954-05'00')`, `Descartes Gray_CMYK`, `Descartes_Logo_CMYK.eps`. **`d.pdf` is a Descartes Systems Group customs-information brochure from 2015**, an artifact of the killed CROSSCheck project.

Two carriers, both unfixed:
- `context/09-COMPLIANCE-AUDIT.md:21` — ``| `d.pdf` | 132 K | micro1's own problem PDF, republished |`` — **false, and this file ships** (it matches the tracked-set glob).
- `prompts/CH-00.md:37-39` — `d.pdf` still filed under `# third-party material we must not redistribute (micro1's own assets)`.

The exclusion is right; the stated reason is wrong.
**FIX (a) — `prompts/CH-00.md`, move `d.pdf` under its own comment:** `# third-party marketing material from the abandoned CROSSCheck research (Descartes Customs Info Reference brochure, 2015) - not ours to redistribute`
**FIX (b) — `context/09-COMPLIANCE-AUDIT.md:21`, replace the cell:** ``| `d.pdf` | 132 K | Descartes Customs Info Reference brochure (2015), left over from the killed CROSSCheck project — NOT micro1's brief. Corrected 2026-08-30; the original entry was wrong and propagated into the `.gitignore` comment. |``
*(The other half of M-35 — nine `killtest/*.py` scripts sending `User-Agent: Mozilla/5.0` — I did not re-verify; **INFERRED** from the first pass. The forward-looking half is unwritten and belongs in O-6's §8 rewrite.)*

### 3.2 → `CONTEXT.md`

**M-22 · The human checkpoint is claimed everywhere and fires nowhere. — 1.0 h**
**VERIFIED:** `grep -ci "needs_human_review"` across all six files = **0**. `CONTEXT.md:216` — *"Unresolved cases route to a named human checkpoint… This satisfies ground rules 04 and 05 concretely."* **"Unresolved" is never defined**, so a CH-06 session must STOP under hard rule 1, and ground rules 04/05 rest on a mechanism that does not exist.

**FIX — ADD two fields to `CONTEXT.md` §5's output contract**, at the top level: `"needs_human_review": true|false,` and `"review_reason": "..."`. **AND REPLACE `CONTEXT.md:216`:**
```
Unresolved cases route to a named human checkpoint with both readings and the paragraph trace.
**"Unresolved" is a trigger rule, not a word.** `needs_human_review` is true when any of:
 (a) an instruction in the trace has `level: "none"` AND `designation_exists: true` - the anchor is
     missing but the target exists, which is the shape of both a real defect and a quoting slip;
 (b) the designation path and the anchor path disagree on the verdict;
 (c) two instructions in the same rule touch the same designation.
`review_reason` names which of (a)/(b)/(c) fired. CH-06's done-when: at least one eval item routes to
the queue and its trajectory contains a `human_checkpoint` record. CH-08 runs two hard-case items
interactively - the agent emits the checkpoint with both readings, the human calls it, the run
resumes, the resolution is recorded. **Measure the queue while you are there:** its catch rate (the
fraction of A1's wrong verdicts routed rather than shipped confident) and its interruption cost
(correct verdicts also stopped). If it does not pay, it becomes a fourth counted removal with its number.
```
*(Trigger (c) is written to survive R-01: it needs only the trace, not the cancelled ledger.)*

**M-25 · The solution has no entry point and is never run on an input a user would bring. — 1.5 h**
**VERIFIED:** `grep -nic "entry point\|python -m\|--offline\|CLI"` — `CONTEXT.md` **0**; `plan.md` **1**, and that hit is `plan.md:16`, R-01 clause 4: *"The polished CLI is dropped; `--offline` replay and the committed worksheet survive."* R-01 dropped the *polished* CLI; it did not create the plain one, and nothing else does. Deliverable 2 requires *"the exact commands for the solution, the baseline and the evaluation"*.

**FIX — ADD to `CONTEXT.md` as a new §5b:**
```
### 5b. The input contract and the entry point

`python -m src.check --rule <FR-citation> --title <N> --part <N> [--as-of YYYY-MM-DD]`

Emits the §5 JSON to stdout and writes the CH-10 worksheet beside it. `--offline <item-id>` replays a
frozen item, needs no network and no key, and is the Tier-1 path a judge runs. The baseline and the
evaluation are the same module: `python -m src.check --arm B0-agent --eval` and
`python -m src.eval --arms all`. Three commands, published verbatim in `REPRODUCE.md`.
```
**AND ADD to CH-10's done-when:** `run the pipeline once on a rule that is NOT in the eval set, commit the resulting worksheet under docs/demo/, and make it the artifact the video walks through.`

**M-33** — §2.20 B-1. **0.15 h** · **M-16 / M-17 / M-24 / O-15** — all four are CH-01b, deleted by R-01; see **§2.10**. **1.5 h at CH-01b** · **M-9 / m-18 / O-9** — number and citation corrections; see §5 and §4.1.

### 3.3 → `plan.md`

**M-19 · Neither video script exists, and both branches need one. — 0.5 h**
CH-13's card gives seven beats and no timings, and nothing schedules the writing.
**FIX — ADD to the CHECKPOINT's done-when:** `Write **both** timed beat sheets now, before the call is known. GREEN: problem 45 s · simple baseline 30 s · one realistic execution end to end 90 s · final comparison 45 s · changelog 40 s · the change that contributed most 20 s · one experiment removed 20 s = 4:50. AMBER-RED: the same seven beats, where "the change that contributed most" becomes "the change that did not move the number, and what that tells you". Pick one at the cutoff. Record to script; never narrate live.`

**M-20 · `B0′` appears in no chunk. — 0.5 h**
**VERIFIED:** `grep -n "B0′\|B0'"` → `CONTEXT.md:63` **1 hit**; `plan.md` **0**; `PROCESS.md` **0**. `CONTEXT.md` §4 defines it as the compute-matched control — the arm that answers *"your agent just got more compute"*.
**FIX — ADD to CH-08's scope:** `Name **B0′** explicitly in the arm list and run it: B0-agent at A1's exact token budget, spent on best-of-3 self-consistency with a published tie-break. Publish the per-arm token table — input tokens, output tokens, tool calls, imputed USD, all per item — from the cost ledger. Dropping B0′ silently invites "your agent got 5× the compute"; if the clock forces it out, drop it by recorded ruling in QUESTIONS.md, never by omission.`

**M-21 · The README's "main failure mode" has a slot and no producer. — 0.75 h**
**VERIFIED:** `plan.md:139` puts *"main failure mode"* in the README's required order; nothing computes one.
**FIX — ADD to CH-08's done-when:** `emit docs/evidence/error-taxonomy.csv — every A1 error with (item_id, gold, predicted, failure_class, which resolution_trace step went wrong). CH-09 names the largest class with its count and a worked example. That becomes the README's "main failure mode" section.`

**M-23 · The hot take's evidence and its "what I'd build next". — 0.5 h**
The artifacts are 181 B, not a corpus — migration is CH-01b item 3 (§2.10).
**FIX — ADD to CH-09's done-when:** `two authored first-person sentences answering "how would it change what you build next?", written by the operator during CH-11b's voice pass, not generated.`

**M-26 · The clean-clone rehearsal is same-machine, same-OS. — 0.6 h · PARTIALLY FIXED.** `plan.md:119` now names `requirements.txt` and Python 3.12.2 ✓. The second-environment half is absent, and **no chunk creates `requirements.txt`** — `grep -c "requirements.txt"` across all six files = **1**, that same row. Both are in §2.12's CH-14a text; add `requirements.txt` to CH-00's skeleton table as a pinned file that every chunk adding a dependency updates.

**M-27 · Raw JSONL is not "easy to follow". — 1.5 h**
**VERIFIED:** `grep -ci "render_trajectory"` = **0**. Deliverable 4 asks that each trajectory be *"easy to follow from the agent instructions to the final result"*. A judge will not read JSONL.
**FIX — ADD to `prompts/CH-00.md` §1b and the scope fence:** `tools/render_trajectory.py` → one markdown page per trajectory: agent instructions at the top, then a step table (action → tool response → the feedback that shaped the next step), retries and human checkpoints called out, final result at the bottom. **Built at CH-00, run at CH-12.**

**M-28 · Ground rule 05's strongest answer is sitting unused. — 0.5 h**
**VERIFIED:** `grep -c "SAFETY.md" plan.md` = **0**; the row exists at `PROCESS.md:97` with no owner.
**FIX — ADD `SAFETY.md` to CH-11's outputs**, ~250 words, linked from the README's first screen, making four points the design already supports and never states: (1) the system performs no action — hard rule 8 makes scorer and resolver pure, and the output is a worksheet, never a filing; (2) **every gold label in the eval set was authored by Office of the Federal Register editors, so the ground truth *is* a qualified human reviewer's judgement** — the sharpest rule-05 answer available; (3) the checkpoint queue routes ambiguous items to a named drafter before use, per M-22's trigger rule; (4) plainly: *"I am not a regulations drafter. This tool is validated against OFR-authored ground truth, not against my own legal judgement, and a qualified drafter reviews every output before it informs a filing."*

**M-29 / M-30 · PARTIALLY FIXED.** `THIRD-PARTY.md` and `LICENSE` are now CH-11 outputs (`plan.md:122`) ✓, and `CH-11b · VOICE PASS` exists (`plan.md:131-133`) ✓. **Outstanding:** (a) `PROCESS.md` §0's *"no artifact is written twice"* still forbids the rewrite CH-11b performs — **FIX, `PROCESS.md:22`:** `**No EVIDENCE artifact is written twice.** Four prose artifacts are explicit exceptions and are rewritten by hand before shipping: the README's first screen, the CHANGELOG's Decision/Learning column, the video script, and the HackerEarth Description.` (b) M-30(c)'s root-clutter move is unapplied — five machine-authored `.md` files sit at root today and CH-00…CH-15 add nine to twelve more. (c) `plan.md:132`'s invented "5 of the 20" — §2.20 B-3. (d) `CONTEXT.md` §8's constraint note is unrewritten — O-6 in §4.1.

**M-32** — §2.12. **0.2 h** · **M-34** — closed at source by §2.3's staged sweep, *provided it runs before the second commit*. No wording change needed: the sentence is right as an intention and wrong only as a statement of present fact. **0 h**

**M-14 · ALREADY-FIXED — and the first pass's own fix text is now unsafe.** Q1's budget was superseded by the haiku / Batch / USD 20 ruling. **Its proposed replacement — *"Budget USD 150-250"* and model id `claude-sonnet-5` — would violate two standing constraints and must not be applied.** The residual defects are in §2.16.
**M-18 · ALREADY-FIXED.** The NUMBERS-ONLY tier exists at `PROCESS.md:173`. Its residue is the CH-08 gate contradiction (§2.12) and its unavailable inputs (§2.9).

---

## 4. CONFIRMED MINORS — one line, one fix

| # | Finding (**VERIFIED** unless noted) | Fix | h |
|---|---|---|---|
| m-1 | "Versions pinned" will read as `requirements.txt` only | `REPRODUCE.md` states the interpreter (Python 3.12.2), the OS, **`claude-haiku-4-5`**, and approximate runtime and cost per tier. **The source finding said `claude-sonnet-5`; that is stale and would violate the model ruling.** | 0.25 |
| m-2 | The brief says "the baseline", singular; there are four non-solution arms | `REPRODUCE.md` names **B0-agent** as the headline baseline for the three-row table, with the other three beneath as supporting arms | 0.5 |
| m-3 | CH-11's README order omits four things `CONTEXT.md` mandates | add: §1 non-goals ("state these in the README"), §2 the generalisation ("lead the README with this"), §12 prior art ("cite on the first screen"), and a `PROVENANCE.md` link | 0.4 |
| m-5 | The worksheet carries no disclaimer on its own face. **PARTIAL** — named in the Phase-3 run-order row, absent from CH-10's card | header band into the card: *"Draft review aid — predicted OFR execution outcomes, not a determination. Not legal advice and not a filing. Every row is a prediction to be checked against the section text beside it; rows flagged for review are the ones the system could not resolve, not the only ones worth reading."* Footer: run id, model, corpus manifest hash, as-of date, queue count. **The band disclaims the tool's authority; it must not tell the drafter to seek sign-off from herself** — `CONTEXT.md:32` names her as the intended user | 0.25 |
| m-6 | FR XML carries `FOR FURTHER INFORMATION CONTACT` blocks naming agency staff | `data/README.md` (**create it**): published under 17 U.S.C. §105; contains agency contact details as published; no data inferred, enriched, joined or republished outside its original document context; no individual is a subject of analysis | 0.25 |
| m-7 | Registration is not recorded in the repo | record `Q0 CLOSED` in `QUESTIONS.md` with its timestamp and citation | 0.1 |
| m-8 | The revision rule is ambiguous once a draft exists | one line in CH-15: *every submission event ships a complete four-field package; never replace a complete submission with a partial revision — "only the latest **complete** submission is evaluated" admits a reading where a partial revision destroys a complete one* | 0.1 |
| m-9 | "Verification" is named in the 30-point row and is not a capability here | **do not add a fourth capability** — the cap is itself a scoring asset. Name the checkpoint queue as a *verification surface* in the README and measure its catch rate and interruption cost (M-22) | 0.5 |
| m-10 | The two artifacts a judge meets first are ungated with no usability read | one session, not the author, opens the worksheet cold and reports what it could not understand in five minutes | 0.5 |
| m-11 | 14–17 machine-authored markdown files at repo root | M-30(c): move `PROCESS.md`, `plan.md`, `CLAUDE.md`, `STATUS.md`, `PROGRESS.md`, `QUESTIONS.md` into `docs/process/`; one authored README line turns the liability into an asset | 0.4 |
| m-12 | Nobody produces the brief's own three-row results table | README, immediately after the headline claim: Primary outcome / Human time per task / Cost per task × Simple baseline / Agent solution / Change; full arm matrix beneath; one video frame | 0.25 |
| m-13 | The hard case is named and nobody writes what it revealed | = §2.18 | 0.5 |
| m-14 | No statement of which capabilities were deliberately not used | README table, four rows: orchestration (rejected — single-document read, no sub-goals), RAG over current CFR text (rejected **and measured** — removed experiment #1, leaks the label), verification (m-9), plus anything an ablation removed. Restraint only scores when it is visible | 0.5 |
| m-17 | "13 and 15 independent agents" does not reconcile, and the largest swarm ships no trace | recount from the dumps and state each count with its file path; say **which four swarms** ship traces and why, rather than implying full coverage. `context/06`'s 57 agents / ~1,845 tool calls have **no `06b-*.json`** — **INFERRED** from the first pass, not re-verified | 0.3 |
| m-18 | `CONTEXT.md:168` — *"The eCFR search API previously reported 92 — it undercounts by ~2.3×"* | at CH-01 publish the govinfo structural count beside it and record the query behind 92, **or delete the sentence**. The 403 means it can never be reproduced | 0.2 |
| m-19 | The 25 MB guard sits above the largest piece of host copyright it nominally guards | lower to **5 MB** with deliberate exceptions listed — folded into §2.3's step 4a | 0.1 |
| m-20 | CH-13's done-when is circular | = §2.20 B-4 | 0.1 |
| m-21 | **PARTIALLY FIXED** — the repo URL now has an anonymous check at CH-15 (`plan.md:184`) but is routed into no surface | one clause in CH-14b step 2, already in §2.12's text | 0.05 |
| p-1 | The user is asserted, never evidenced | quote NARA's Document Drafting Handbook verbatim on the first screen, quote one real NARA note, and give the **rate** — O-7 computes ~44 defect notes/year, with its five caveats shipped beside it | 0.4 |
| p-2 | `cfpb/regulations-parser` is archived and deprecated, unmentioned | say so in the citation: *"(DEPRECATED, archived 2018-09-17)"*. **INFERRED** — GitHub state not re-checked this pass | 0.1 |

### 4.1 §7 items still open — terse

**O-5** `grep -c "tests/" plan.md` = **0**; "tests" is a named submission-validity item owned by no card — add `tests/` to CH-00's outputs and to every gated chunk's done-when *(0.1 h)* · **O-6** commit `docs/evidence/corpus-access/govinfo-robots.txt` and rewrite `CONTEXT.md` §8's constraint note factually: both hosts 403 to this environment, neither is used, govinfo bulk is the sole channel, the two blocked hosts were **abandoned rather than circumvented**, `refetch.py` sends a descriptive User-Agent with a contact address and honours 429/503, **and Tier 1 needs no network at all, so a judge is never exposed to it** *(0.5 h)* · **O-7** the ~44/year defect rate into the README's first screen with its five caveats — including that 2025's 19 is unexplained and 2017's 93 is double its neighbours, so **no trend line** *(0.3 h)* · **O-8** one dated paragraph in `PROVENANCE.md` recording the four originality queries and their outcomes *(0.2 h)* · **O-9** correct the Prior et al. citation — **VERIFIED still wrong at `CONTEXT.md:248` and propagated to `PROVENANCE.md:95`**. The paper is *"Risks and Limits of Automatic Consolidation of Statutes"* (Prior, Hof, Wais, Grabmair) — German statute **consolidation**, not amendatory-instruction execution. `CONTEXT.md:252`'s own words: *"Not citing known prior art on a submission staked on integrity is an unforced error and is one search away for a judge."* It was one search away *(0.2 h)* · **O-10** the § 39.13 fixture into CH-02, text in §2.8 *(0 h)* · **O-11** the architect records the model and orchestration for each of the four design swarms into `AI-USE.md`'s pre-build seed, **before that memory is gone** *(0.3 h)* · **O-12** one line in `PROVENANCE.md` §6 distinguishing quotation-for-analysis from republication *(0.1 h)* · **O-14** the reliability table as CH-08's second done-when, with the no-verdict policy pre-registered in `GOOD.md` and applied identically to every arm — **VERIFIED `grep -ihc "reliab"` across the six files = 1, and that hit is inside a quoted requirement** *(0.5 h)* · **O-15** the type-4 verdicts — CH-01b item 6, and **unrecoverable once gold is opened** *(0 h extra)* · **O-16** one line into each of CH-05/06/07's done-when: report the primary metric on the frozen eval set at that point, same scorer, so the changelog's EVIDENCE column is comparable row to row *(0.2 h)* · **O-17** CH-13 watches the recording end to end for credentials, home paths, contact details, other tabs, notifications and git-ignored trees — *"the one deliverable no secret scanner can read"* *(0.2 h)* · **O-18** a ~200-word `HOW-TO-JUDGE.md` — **VERIFIED `grep -ci` = 0**; the brief invites it in a highlighted box, and it is the one place a hard-on-yourself framing is rewarded *(0.5 h)* · **O-19** `GOOD.md` gains a "good for the drafter" block above the statistical one — the two guards, not the accuracy figure, are what make the tool usable *(0.2 h)* · **O-20** tag the submitted state and stop pushing to `main` until 2026-09-07; judging runs Sep 2–4 against a live repo — **VERIFIED `grep -ci "git tag\|do not push"` = 0** *(0.2 h)* · **O-21** the exporter becomes a **redacting** exporter with a per-rule fired count and an output-size assertion; a raw export re-imports ~13 MB of page assets the `.gitignore` exists to exclude *(0.5 h)* · **O-22** ten minutes: confirm the registration profile carries accurate identity/location/contact and that only one registration exists; record as Q0 *(0.2 h)* · **O-23** use the three award criteria's own vocabulary when writing the README opening and the Description — no new work *(0 h)* · **O-24** ADD to `CLAUDE.md`'s Precedence line, at the very top: `an official organiser clarification (recorded in QUESTIONS.md with its source and UTC timestamp) → …` — **VERIFIED `grep -ci "clarification"` = 0** *(0.1 h)*

---

## 5. Untraceable numbers in `CONTEXT.md`

**The headline. VERIFIED:** `grep -c "docs/evidence" CONTEXT.md` = **0**. `ls -d docs/evidence` = *No such file or directory*. **32 lines** carry a measured ratio, percentage, pp-delta or p-value. **Not one resolves to an evidence path.** Hard rule 14 and `PROCESS.md` §9 (*"No number is quoted without its evidence path"*) are both violated across the whole file.

That is the honest headline. The useful finding is that the file is in far better shape than "32 bare numbers" implies, and I recomputed three groups myself.

### 5.1 Recomputed this pass — real, and cheap to make shippable

| `CONTEXT.md` | Claim | My independent recomputation | Verdict |
|---|---|---|---|
| `:172` | `CFR-2024-title40-vol5`, **5,524,321 B** | `wc -c cfr2024t40v5.xml` = **5524321** | ✅ **exact** |
| `:172` | **28** `<EDNOTE>`, **26** inside a `<SECTION>` | 28 / 26 | ✅ **exact** |
| `:172` | both `<EFFDNOTP>` inside a `<SECTION>` | 2 / 2 | ✅ **exact** |
| `:172` | **252 of 255** `<CITA>` inside a `<SECTION>` | 255 / 252 | ✅ **exact** |
| `:191` | the eCFR "Link to an amendment…" annotation appears **0 times** in the govinfo annual editions | 0 in `cfr2024t40v5.xml`, 0 in `fr20240103.xml` | ✅ **exact** |
| `:110` | **833/1,984 = 42.0%** state-carry sensitivity | `probe/items.json` holds **1,984** items; **833** carry more than one instruction = **41.986%** | ✅ **exact** |

**Recommendation: RE-DERIVE — it is nearly free.** Six of the most load-bearing numbers in the spec — the entire leakage-strip justification and the ledger's measured justification — reproduce exactly from two files already on this machine. The work is: put the `cfr2024t40v5.xml` counts behind a 20-line script under `docs/evidence/spec-claims/`, put `probe/items.json` (or the derived count plus its script) under `docs/evidence/pilot/state-carry/`, and commit both with their stdout. **This contradicts the first pass's characterisation of §6 as untraceable**, and it turns the worst of M-16 into an hour of copying.

⚠ **Blocker, VERIFIED:** all three source artifacts are excluded by CH-00's `.gitignore` — `*.xml` catches `cfr2024t40v5.xml`, and `probe/` sits in the research-scratch block. **Migration must be an explicit copy into `docs/evidence/`, never a reliance on the file being present.** That is CH-01b item 1.

### 5.2 Does not reproduce — and it justifies removing a capability

| `CONTEXT.md:225` | *"redesignation-collision sensitivity is **26/1,984 = 1.31%** of corpus items"* |
|---|---|
| My recount | items containing a `redesignat*` instruction in `probe/items.json`: **61 = 3.08%** |

**VERIFIED** that the naive recount gives 61, not 26. That does **not** prove 26 wrong — the original almost certainly applied a narrower filter (a redesignation that actually *collides* with a later instruction, rather than any redesignation at all), which is **INFERRED**, not established. What *is* established: **the filter is unrecorded and the number cannot be reproduced from the artifact**, and it is used to justify removing a capability. **Recommendation: RE-DERIVE with the filter stated inside the sentence, or delete the "26/1,984 = 1.31%" figure and keep the four other measurements §10 already lists.**

### 5.3 Documented in a shipping file, but with no `docs/evidence/` path

| Numbers | Where they actually derive | Recommendation |
|---|---|---|
| `:121` **0.5000** / **0.5934** / **p = 0.185** — the three numbers that make the primary metric unchangeable | **VERIFIED** at `07-KILL-TEST.md:517-518` and `:535`, with the full derivation: best model-free feature `sec_tail_len` at 0.5934; its own 26-way permutation null, mean 0.5621, p95 0.6184 → empirical p = 0.185; model-free floor 0.500 | **KEEP AND LABEL**, citing `07-KILL-TEST.md` §7.2 inline; **re-derive at CH-04**, which builds the B-script arm and its permutation null anyway. These are not bare assertions and the first pass understated them |
| `:235` **+12.0 pp / −4.0 pp / p = 0.64 / −16.7 pp** — the hot take | the headline `fisher_p = 0.6368` and net +4.0 were confirmed against `killtest/errata/arms.json` (181 B) by the first pass — **INFERRED**, I did not re-run it. The per-class split appears only as prose at `killtest/draft_67.md:220` | **RE-DERIVE at CH-09** rather than re-quote; the artifacts are 181 B and ship under `docs/evidence/hot-take/` |
| `:47` **0.545 / 0.5855 / 0.52** | already labelled *provenance-unverified* in the file ✓ — **but the pointer is wrong.** `0.5855` has **0 hits** in `07-KILL-TEST.md` (it is at `08-FINAL-CALL.md:111`), and the one `0.52` in `07-KILL-TEST.md` (`:924`) reads *"the prior work's 0.5250"* — a third party's number, not this project's tool signal | **KEEP AND LABEL with the correct pointer**, and establish what 0.52 measured before it ships. The self-labelling here is exemplary; only the citation is wrong |

### 5.4 Untraceable, no local artifact — recommendation per group

| `CONTEXT.md` | Numbers | Recommendation |
|---|---|---|
| `:101` | **26/33** and **35/42** labelled items with no extractable quoted anchor; *"~80% of the pool"* | **RE-DERIVE at CH-01b.** This is the entire argument for the tool's ordering. The nearest artifact (`probe/anchor_rows.json`, n = 30, 16/30 = 53%) is a third pool ~27 points off the gloss — **INFERRED** from the first pass. Until re-derived, **delete the "~80%" gloss**; keep the ordering decision and justify it from NARA's note vocabulary, which is independently checkable |
| `:157-166` | **903** EDNOTEs · **44** defect notes · **44/44** · **38/44** · **6/44 (13.6%)** · **10/44 (22.7%)** | **RE-DERIVE at CH-01** — this is literally CH-01's job, and its done-when already says *"results within range of the 9-title reference … or the deviation explained"*. Label the current values `PILOT (pre-repo, 9 titles)` until CH-01 lands |
| `:168` | **150–250** · **~130–210** · **92** · **~2.3×** | **DELETE the "92 … ~2.3×" clause** (m-18): the 403 makes it permanently unreproducible and the query behind 92 is recorded nowhere. **KEEP AND LABEL** the projection as a pre-registration |
| `:110`, `:209` | **31/82** · **16 defective / 15 executable** · **n = 16 in the 82-item pilot pool** | **KEEP AND LABEL** `PILOT (pre-competition, n=82)`. Internally consistent — 16 + 15 = 31 ✓ **VERIFIED** by arithmetic — but no artifact |
| `:225` | **0/68** · **3/82 (2 positive)** · **15 of 26** · *"live probe for 'conflicting amendments' returned 0"* | **KEEP AND LABEL**, and note that *"labelled items"* carries **four different denominators in this file — 33, 42, 68 and 82** — none of them defined. Define the term once in §8 or the numbers are not comparable to each other |
| `:126` | *"~1,000 records"* | **KEEP AND LABEL** as an estimate; CH-03 replaces it with the real count |
| `:8` | *"survived adversarial review by **13 and 15** independent agents"* | **RE-DERIVE by recounting the dumps** (m-17); `PROVENANCE.md:43` separately attributes 15 to `context/03`, whose own dump counts 13 |
| `:60-64`, `:136-137` | **~0.59 / ~0.50 / ~0.75 / ~0.85**, guards **≤ 0.25 / ≥ 0.90**, **+8 pp / p < 0.05 / n ≥ 84 / ≥ 0.80** | **KEEP.** These are predictions and pre-registered thresholds, not claims from data, so rule 14 does not bite. `:137` already labels them *"Predictions written before the run"* ✓ |

**The count, for the operator: 32 lines carrying a measured figure; 0 evidence paths. Six of those figures recompute exactly today; three more carry a full derivation in a shipping file; one does not reproduce and should not ship as it stands.**

---

## 6. FALSE ALARMS and NOT-WORTH-FIXING — with the evidence that killed each

I am not padding this list, and one entry is a finding of mine that I killed.

**FA-1 · "There is no micro1 PDF on this machine, so `PROVENANCE.md` §4b's verification is unsupportable." — KILLED. This was my own finding, and it was wrong.**

I ran `find . -iname "*.pdf"` from the **repo root**, got two hits — `d.pdf` and `context/me/raw/resume.pdf` — and concluded the brief's source was absent. **The brief is outside the repo.** `ls -la "/c/Users/chinm/Downloads/micro1 - First Hackathon97ce7c5.pdf"` returns a real file: **648,125 B, dated 2026-08-29 08:28** — exactly the filename `context/01-PROBLEM-PDF.md` names as its source. **VERIFIED.**

This also **kills the first pass's own §9 item 11 and the second half of O-25**, both of which assert *"VERIFIED: its stated source … is not on this machine."* That check was repo-root-only too, and it is false. The consequence is material and good: **`PROVENANCE.md` §4b's recorded verification is supportable**, the operator did hold the original, and the document at the top of the precedence chain is checkable after all.

What §4b still lacks is the *method*. It records outcomes and not who checked, against what, or how far — and by its own table the check covered rubric weights, the anti-slop clause, ground-rule **opening clauses** and deliverable **headings**, not the deliverables' sub-clauses.
**Remaining fix, 0.1 h — `PROVENANCE.md` §4b, ADD one line:** `Checked by the operator on 2026-08-30 against the original at \`~/Downloads/micro1 - First Hackathon97ce7c5.pdf\` (648,125 B, 2026-08-29). The check covered the rubric table, the anti-slop clause, the ten ground rules' opening clauses and the four deliverable headings; the deliverables' sub-clauses were not read line by line.`

*This is the third time on this project that a claim of the form "X does not exist" was produced by a search narrower than the claim. Rule 15 now covers exactly that, which is the argument for rule 15.*

**FA-2 · "`PROVENANCE.md`'s enforcement mechanism does not exist — there is no `.gitignore`, no git history, no `git ls-files`." — KILLED on its premise.**
All four quotes reproduce verbatim (`:5`, `:13`, `:31`, `:108`) and `ls -d .git .gitignore` does return *No such file or directory*. But `PROVENANCE.md` describes the repository as it will exist after CH-00, and `prompts/CH-00.md:26` creates it as its first act. A document describing a post-CH-00 state is not defective for describing it before CH-00 runs. **The real residue is M-34's ordering point** — the redaction must precede the first commit or the file ships a falsehood into history — and that is closed by §2.3.

**FA-3 · "`CLAUDE.md` end-of-session duty 1 orders build sessions to edit `CONTEXT.md`, which `CONTEXT.md:5` forbids." — KILLED.**
`CLAUDE.md:48` reads *"**Commit** any new rulings to `QUESTIONS.md` / `CONTEXT.md` **first**, before anything else."* "Commit" is a git verb here, not an authoring verb: it is item 1 of a numbered list whose siblings are *"Atomic commits"*, *"Push"* and *"Report the SHA"*. The architect authors; the session commits. No conflict.

**NWF-1 · `PROCESS.md:61` cites a `CH-05 → 05A/05B` split as an accomplished fact; no such split exists.** It is an illustrative example of the splitting rule, not a claim about the plan. Cosmetic.

**NWF-2 · `CONTEXT.md:174` quotes the `<EFFDNOTP>` leak string with terminal punctuation differing from the source XML.** The quoted sentence is materially accurate and the strip is structural, not string-matched. Not worth an edit to a file that needs eleven substantive ones.

**NWF-3 · m-21, the repository URL.** D-3 already put the URL and an unauthenticated `curl` check into CH-15 (`plan.md:184`). Routing it into `SUBMISSION.md` is one clause inside a fix already being made (§2.12); it does not need its own finding.

---

## 7. Adequacy of the ~24 already-applied fixes

| # | Applied fix | Verdict |
|---|---|---|
| 1 | Leakage strips into `CONTEXT.md` §8; the CH-03 leakage test; the reviewer instruction to confirm it fails on unstripped input | **SUFFICIENT.** `CONTEXT.md:170-191` ✓; `plan.md:51` covers all four elements plus the rule's own FR citation plus the three literals ✓; `plan.md:52` carries the fails-on-unstripped instruction ✓. **One gap:** the measurement paragraph counts `<EDNOTE>`, `<EFFDNOTP>` and `<CITA>` but gives **no count for `<EAR>`**, which it strips. I measured it: **5 total, 1 inside a `<SECTION>`.** Add it, so all four stripped elements carry a number — hard rule 14's zero-branch principle |
| 2 | `.gitignore` rewritten (`*.xml`, `data/raw/`, `dist/`, `*.zip`, `*.mp4`, `*.stackdump`); design prompts to `prompts/design/` | **PARTIAL.** The ignore block is correct and complete ✓. **The move cannot execute** (§2.4) and `prompts/design/` does not exist. The `d.pdf` comment still labels a Descartes brochure as micro1's asset (§3.1) |
| 3 | PII redaction sweep as CH-00 step 5; pre-commit hook for size and PII | **BROKEN — the most important half-fix.** The sweep runs against a two-file index and passes vacuously; its stated pass criterion is unachievable in principle; two of four carriers are unnamed. §2.3 |
| 4 | AMBER proceeds; RED path specified; VALIDITY CONSTRAINT recorded; CH-02/CH-03 numeric fallbacks pre-registered | **PARTIAL.** All four present, and the VALIDITY CONSTRAINT is **exemplary** — I verified its quote verbatim at `00-MASTER-CONTEXT.md:130`, confirmed it sits inside §4 *(verbatim)*, and confirmed `grep -c "advanced solution" context/01-PROBLEM-PDF.md` = **0**, exactly as `plan.md:73` claims. The honest note on its own authority is the right call. **But the decision rule it hangs on is not total** (§2.6), and CH-03's fallback ladder covers ≥ 42 and [30, 42) and is silent below 30 |
| 5 | Ruling R-01 — CH-07 NOT BUILT as counted removal #3; ablations 1 rep; CH-01/CH-01b merged; polished CLI dropped | **PARTIAL, and clause 3 is a deletion mis-recorded as a saving** (§2.10). Clause 1 is undercut by the two-vs-three split (§2.11). Clause 4 dropped the polished CLI and left no plain one (M-25). Clause 2 and the reps reduction are sound ✓ |
| 6 | Wall-clock triggers, MVS drop list, two-strike rule, NUMBERS-ONLY tier, protected sleep block in `PROCESS.md` | **SUFFICIENT as written** ✓ — `:215-224`, `:226-233`, `:175`, `:173`, `:237`. **But the NUMBERS-ONLY tier cannot run on the inputs it is given** (§2.9), and CH-08's gate contradicts it (§2.12) |
| 7 | Phase 3 reordered, video 2nd and clearing 10:00 UTC; CH-11b; CH-15 with an unauthenticated repo check | **PARTIAL.** All three landed in `plan.md` ✓, and CH-15 is strong — the anonymous `curl` check and the *"`gh` gives a false pass"* reasoning are exactly right. **`PROCESS.md` §7 was never resynced** and still shows the old five-chunk Phase 3 at ~10 h (§2.13). CH-14's five steps are unallocated, so the zip has no owner (§2.12) |
| 8 | `PROVENANCE.md` written, including a recorded verification that the brief transcription matches the original | **PARTIAL.** The file is a genuine asset and §4b was the right instinct. **Four defects:** wrong model; a cancelled capability listed as built; a decoded-passage count of 4 against an actual 6, with one headed "Evaluation hard requirements"; and `scraper/` dated wholly pre-kickoff when 36 of 44 entries postdate it (§2.14). The §4b check itself is **supportable** (§6 FA-1) — it simply does not record its method |
| 9 | Parallel-session file-ownership rules in `CLAUDE.md` | **SUFFICIENT** ✓ `CLAUDE.md:69-73`. Minor: it routes entries to `docs/progress/`, which no chunk creates (§2.19) |
| 10 | Budget ruling revised — `claude-haiku-4-5` every arm via the Batch API, ceiling USD 20, hard stop USD 18 in the logger, Sonnet sensitivity check at the checkpoint | **PARTIAL, materially.** The ruling is a real improvement and the reasoning about a weaker model producing a flatteringly larger gap is the right instinct, honestly stated. **But** the itemised plan sums to USD 20 against a USD 18 coded stop; the sensitivity check is priced at both ~$3 and ~$2 five lines apart; its Sonnet price basis is unstated; and it sits last in a queue the ceiling can cancel — while being the guard against a false RED (§2.16). **And `PROVENANCE.md` still tells a judge the arms run on Sonnet** |

**Summary: 3 sufficient, 6 partial, 1 broken.**

The pattern is worth naming, because it is one pattern and not ten: **every fix landed in the file it was written against, and no fix was propagated to the second file carrying the same fact.** `plan.md` got Phase 3; `PROCESS.md` did not. `CLAUDE.md` got three new rules; `prompts/CH-00.md` and `PROCESS.md` did not. `prompts/CH-00.md` got the haiku ruling; `PROVENANCE.md` did not. That is hard rule 16's failure mode exactly, and it is why §2 is as long as it is.

---

## 8. Is the spec executable?

**No. A fresh session handed `prompts/CH-00.md` right now stops six times before it reaches the run logger — the thing the prompt itself calls "the real work of this chunk".**

Walking it literally, in order:

| Where | What happens |
|---|---|
| **`prompts/CH-00.md:9`** — the first line of the read order | *"All **14** hard rules apply to you."* The session opens `CLAUDE.md` and counts **17**. Prompt and constitution disagree → **STOP** (hard rule 1). §2.1 |
| `:79` — step 4 | The tree-safety assertion runs against a two-file index and cannot fail. Not a stop — **worse**: a false pass on a 447 MB tree. §2.3 |
| **`:84`** — step 4b | `git mv DIVERGENT-RESEARCH-PROMPT.md prompts/design/` → `fatal: not under version control`. Three times → **STOP**. §2.4 |
| **`:96`** — step 5 | The PII sweep scans a two-file index, and its stated criterion (`grep -c` "must print nothing") is unachievable in principle. Either a false green or a **STOP** on an impossible criterion. §2.3 |
| **after `:99`** | *"The second commit"* has now been referenced twice and never issued. The ship-set is never staged → **STOP**. §2.3 |
| **`:278` and `:294` vs `:310`** | The TASK orders `docs/evidence/runs/cost_ledger.csv` and `.githooks/pre-commit`; the scope fence forbids both, and the safety rider declares itself overriding → **STOP**, twice. §2.5 |

**The first stop is at the prompt's ninth line, before any work begins.** The most dangerous item is not a stop at all: the PII sweep produces documentary evidence of a redaction that never ran, and `:99` instructs the session to paste that empty output into its report as proof.

**Two gates downstream cannot do their jobs even if CH-00 succeeds.** CH-02's FULL review requires reimplementing carry-forward attribution from `CONTEXT.md` alone; `CONTEXT.md` never describes it and never defines the completeness ratio its ≥ 0.90 threshold gates on (§2.8). The NUMBERS-ONLY tier is handed CSVs with no schema and a §7 that never mentions the bootstrap it must confirm (§2.9). Both are the leakage-defect shape: the reviewer cannot catch what `CONTEXT.md` does not say.

**And the project's single go/no-go cannot classify an ordinary result** (§2.6).

**Cost to make it executable: 2.0 h of architect edits.** §2.1–§2.5 are 0.9 h and clear every CH-00 halt. §2.6–§2.9 are 1.35 h and are what make the checkpoint and the two gates real. Everything else in this document can travel with the chunk it belongs to.

### Remaining hours, honestly

The standing constraint is that the clock is not a design input and hours are stated, not used to justify cuts. So, stated:

| | Hours |
|---|---|
| **Architect pre-flight** — §2 (2.0 h to unblock) plus §3's majors and §4's minors, applied as grouped per-file edits | **7.5** |
| Phase 1 as specified, with CH-01b restored, including three review gates | **17.0** |
| Phase 2 as specified (CH-07 not built) | **11.5** |
| Phase 3 as specified — nine entries | **12.0** |
| **Total** | **≈ 48 h** |
| Available: now (2026-08-30 ~13:00 UTC) → 2026-08-31 18:00 UTC, less one 4.5 h protected sleep block | **≈ 24.5 h** |
| **Shortfall** | **≈ 23.5 h — about 2.0× oversubscribed** |

**This is worse than the documents currently say, and the discrepancy is itself a finding.** `PROCESS.md` §7's phase headings total **17 + 11.5 + 10 = 38.5 h**. `plan.md`'s R-01 states *"~57 h against ~31.5 h available"* and records trims worth 5.0 h, which leaves ~52 h — not 38.5 h. Three mutually inconsistent time accountings across two files, and none of them matches the wall clock now. R-01 records the trims and never states the residual shortfall.

**I propose no cuts.** The mechanism for this already exists and is good: the **T−12h hard cutoff** at `PROCESS.md:212` and the **minimum-viable-submission drop list** at `:226-233`. Phase 2 gets whatever remains when Phase 3 opens; the drop list decides what ships from wherever the work has reached; anything below the line ships with a stated LIMITATION rather than silently absent. That is the design working as intended. The one thing that makes it work is that the drop list exists *before* the hour it is needed — and it does.

---

## 9. What I could not verify

Honest, with how much each matters.

1. **`git mv`'s exact failure on an untracked path.** I did **not** run it — the scope fence forbids `git init`. I read the error table out of the installed `git.exe` (`bad source` / `not under version control` / `destination already exists` …) and its companion format string `%s, source=%s, destination=%s`. That `git mv` requires a tracked source is documented behaviour. **VERIFIED** that the three files are untracked at step 4b and that no `git add` precedes it; **INFERRED** that the command aborts. **Matters: high, but the conclusion does not turn on it** — even if `git mv` succeeded, §2.3's missing second commit stands alone.

2. **The CH-02 attributor counts inside §2.8's fix text** — 27 of 64 `<AMDPAR>` naming a section, 42 `<REGTEXT>` blocks, the § 39.13 fixture. Taken from the first pass's O-10 on `fr20240103.xml`; I did not re-derive them. **INFERRED. Matters: medium** — the fixture is hand-computable at CH-02 and the reviewer will check it. If the counts are off, the motivating paragraph needs a number changed, not a redesign.

3. **The `26/1,984 = 1.31%` filter.** My recount gives 61 under a naive `redesignat*` match. Whether 26 comes from a narrower, correct filter or from a different pool is **UNKNOWN**. **Matters: medium** — it justifies a removal; §5.2 says state the filter or drop the figure.

4. **The count-matched-sibling yield.** Still **UNKNOWN**, still the largest unquantified risk in the project, and still the assumption `n ≥ 84` rests on. The first pass tried and discarded its own attempt for stated reasons. Nothing has changed. **Matters: high.** CH-01b item 7.

5. **The per-item rate at which the leakage strips fire.** **UNKNOWN.** I confirmed structural containment exactly (26/28 `<EDNOTE>` inside `<SECTION>`, 2/2 `<EFFDNOTP>`, 252/255 `<CITA>`) and confirmed `"could not be incorporated"` appears **0 times** in that volume — so **no positive label has been observed leaking**. That is exactly why the fix is a test and a count rather than an argument. **Matters: high.**

6. **`CONTEXT.md` §6's `26/33` and `35/42`.** **UNKNOWN**, unchanged from the first pass. The entire argument for the tool's ordering. **Matters: high.**

7. **The `me` / `mw` / `ma` inversion** flagged at the first pass's §9 item 6 — alphanumeric-only matching finding *fewer* anchors than exact. I did not open that file. **UNKNOWN. Matters: medium** — CH-05 must resolve it before building `cfr_resolve`, and `CONTEXT.md` §1 makes normalisation levels precision-critical.

8. **The hot take's per-class figures** (+12.0 / −4.0 / −16.7 pp). **UNVERIFIED** this pass. **Matters: medium** — CH-09 should recompute rather than re-quote.

9. **Whether the funded Anthropic account can call `claude-haiku-4-5` and `claude-sonnet-5`.** No `.env` exists; I checked by name only and never read a value. **UNKNOWN. Matters: high, and it gates the CHECKPOINT.** A `PRICES` dict keyed on a model the account cannot call silently corrupts every cost row.

10. **Registration state, and the HackerEarth form's character limits.** **UNKNOWN.** Both are minutes of operator work (O-22, and a look at the form during DRAFT-1). **Matters: low now, catastrophic if registration is wrong.**

11. **Everything about the external world.** `github.com/chinmoypaul8897/{acumen,nistula-assistance-}` (`PROVENANCE.md` §4), the archived state of `cfpb/regulations-parser` (p-2), the ACL Anthology volume behind O-9, and govinfo's current HTTP status. All **INFERRED from the first pass or UNKNOWN**; I made no network requests. **Matters: low individually**, except O-9, where the citation sits on the README's first screen and the first pass's evidence is specific enough to act on.

12. **Mutual applicability of the fixes in this document.** I checked the pairs that touch the same lines and flagged the one dangerous interaction explicitly — **M-31's glob widening must follow §2.3's sweep, or it leaks PII.** I did **not** systematically diff every proposal against every other. **PARTIALLY UNKNOWN. Matters: medium.** Apply per-file, in the order §2 gives, and re-read each file once after its group rather than after each edit — which is hard rule 16.

13. **Whether `CLAUDE.md` changed again while I was writing this.** It changed once mid-audit (mtime `13:03:50`). Everything here is written against that version. **Matters: low in itself, but it is the concrete case for `ARCHITECT.md` (M-15)** — the spec moved under a running audit, and nothing in the repository recorded that it had.

---

*End of the second remediation pass. Nothing in this document has been applied; one file was created and no other file was touched. The architect applies it — that separation is the point.*
