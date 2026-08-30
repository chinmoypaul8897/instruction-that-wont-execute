# plan.md — chunk cards

**Owner:** ARCHITECT. Changes to this file are recorded architect rulings.
**Read with:** `CONTEXT.md` (law), `PROCESS.md` (how), `STATUS.md` (where we are).

> ## ARCHITECT RULING R-01 — scope, 2026-08-30
> The remediated plan totalled ~57 h against ~31.5 h available (1.8× oversubscribed). The operator ruled: **Option B + two trims.** Recorded here because it is a judged decision and its reasoning ships.
>
> **1. CH-07, the ordered-state ledger, is NOT BUILT — and is declared now, in advance, as counted removal #3.**
> Not a casualty of the clock. The brief requires removed experiments and most entrants will have none; we ship **three**, each with a measured number: the current-CFR-text leakage probe, the intra-rule collision detector (class size measured five ways at ~1.3%), and the ledger. **Two capabilities each traced to a numbered failure is a stronger answer to "which design choices helped the agent solve the problem?" than three where the third was rushed.** The ledger's justification — order-sensitivity firing on 38–42% of items — is published as the reason it was *worth* building, alongside the reason it was not.
>
> **2. Ablation repetitions 3 → 1.** Final arms keep 3 reps. Pre-registered in `GOOD.md` **before any arm runs**, so it is a declared decision and not a corner cut. Widens CIs on the ablations only; also conserves most of the API budget.
>
> **3. CH-01 and CH-01b merge into one session.** Round-trip saving only.
>
> **4. The polished CLI is dropped**; `--offline` replay and the committed worksheet survive. Judges run the replay, not a CLI.
>
> **NOT cut, at any price:** any Phase 3 item, the three full review gates, the voice pass, the early video upload, the 12:00 UTC draft.

**Gates:** CH-02, CH-03 and CH-04 each get their own full adversarial review, in a fresh session with zero shared context. They form a serial chain — the attributor feeds the eval set feeds the scorer — so a defect caught late invalidates everything built on it. Reviewing them separately is the point.

**Strike limit:** a chunk that FAILS review twice is escalated to the architect rather than fixed a third time.

---

## Phase 1 — foundation and the go/no-go

### CH-00 · Repo, canonical files, run logger — GATE: none
**Scope:** git repo (private), `.gitattributes`, canonical files, the run logger and cost/time accounting.
**Inputs:** `PROCESS.md`, `CONTEXT.md`, `plan.md`.
**Outputs:** initialised repo; `CLAUDE.md`, `STATUS.md`, `PROGRESS.md`, `QUESTIONS.md`, `CHANGELOG.md`, `AI-USE.md` skeletons; `src/runlog.py`; `docs/trajectories/`.
**Done when:** a dummy agent run emits a readable JSONL trajectory **and** a cost row containing input tokens, output tokens, wall-clock, and imputed USD at published list prices. Suite green. Pushed.
**Scope fence:** no harvest code, no scorer, no eval logic.

### CH-01 · govinfo EDNOTE harvest — GATE: none
**Scope:** download ECFR bulk title XML from govinfo; extract `<EDNOTE>` structurally; filter to codification-defect notes containing `"could not be incorporated"`; resolve each to its FR citation.
**Done when:** pool count printed per title; exclusion ladder committed with counts at every step; results within range of the 9-title reference in `CONTEXT.md` §8 (44 defect notes / 903 EDNOTEs) or the deviation explained.
Downloads land in `data/raw/`, which is git-ignored and **never tracked**. **Extract-then-freeze:** what enters `data/` is only the `<SECTION>` and `<AMDPAR>` blocks the eval set uses — never a whole title XML or a whole FR issue. Measured: extraction is ~1.4 MB at n = 84; whole CFR volumes are ~231 MB and 50 ECFR title XMLs are **~2.3 GB against a 50 MB submission cap**. Print `du -sh data/` and the tracked file count at the end of the chunk.
**Scope fence:** labels only. No AMDPAR parsing, no CFR text.
**Note:** govinfo only. ecfr.gov and federalregister.gov are 403.

### CH-02 · AMDPAR carry-forward attributor — GATE: **FULL (domain + code)**
**Scope:** pull FR documents from govinfo by citation; extract `<AMDPAR>` elements; attribute every lettered sub-instruction to its section by carry-forward (iterate in document order, maintain last-named section).
**Done when:** **attributor completeness ≥ 0.90, measured and printed.** Golden fixtures: 3 rules hand-verified instruction-by-instruction before the code is written.
**Why gated:** a truncation bug here already produced 0.46 completeness once and poisoned an entire pilot. Highest-risk component in the project.

### CH-03 · Point-in-time text + eval set — GATE: **FULL (domain + code)** + mutation tests
**Scope:** CFR annual editions from govinfo for as-of text; build positives and count-matched negatives; freeze under SHA-256 manifest with `refetch.py`.
**Done when:** ≥ 42 pairs (n ≥ 84); **exact instruction-count matching asserted by a test**; full exclusion ladder published; manifest verifies from a clean clone; **the corpus is EXTRACTED then frozen** — only the `<SECTION>` and `<AMDPAR>` blocks the eval set actually uses, never whole title XMLs or whole FR issues; **and the leakage-strip test passes.**

**The leakage-strip test — this is the one that stops a rigged benchmark.** It FAILS if any frozen section text contains (a) an `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>` or `<EAR>` element, (b) the FR citation of its own rule under test, or (c) any of the literals `"could not be incorporated"`, `"Editorial Note"`, `"Effective Date Note"`, `"set forth as follows"`. Per-element strip counts are printed and committed to the manifest.
**Review instruction:** the reviewer independently re-derives the strip counts, and **confirms the leakage test FAILS on unstripped input before accepting that it passes on stripped input.**
**Why gated:** exact count matching is what stops a hardcoded constant beating the agent. Wrong here = rigged benchmark = dead submission.
**Seals `data/` read-only on PASS.**

### CH-04 · Scorer + GOOD.md — GATE: **FULL (domain + code)** + mutation tests
**Scope:** deterministic scorer (stdlib, no model, no network): primary accuracy, false-defect, missed-defect, attributor completeness, `success + failure == n`. B-script arm and **its permutation null**. `GOOD.md` pre-registration.
**Also report:** the count of items whose **unstripped** text would have contained the answer. That number is itself a publishable result about the corpus.
**Done when:** scorer reproduces the B-script number with its null; `GOOD.md` committed and timestamped **before any model arm runs**.
**Why gated:** the one thing that must never be self-graded.

### ★ CHECKPOINT · B-script / B0 / B0-agent × 3 reps
**Decision rule — evaluated in this order, first match wins. It is TOTAL: every (gap, p, B0) triple lands in exactly one branch.**

**STEP 0 — leakage precondition, checked BEFORE any branch.** If **B0 ≥ 0.70**, the instruction text is leaking executability. Strip the *quoted anchor text* (keep operation and designation), re-run the gate **once**, and evaluate the branches on the re-run numbers. This is a precondition, not an outcome — previously it sat inside RED, so `B0 = 0.72` with an 18 pp gap matched GREEN and RED simultaneously.

**STEP 1 — branch on the (possibly re-run) numbers:**

| Condition | Branch |
|---|---|
| gap **< 8 pp** | **RED** |
| gap **≥ 8 pp** and McNemar **p < 0.05** | **GREEN** |
| gap **≥ 8 pp** and McNemar **p ≥ 0.05** | **AMBER** |

*(The 15 pp figure in `CONTEXT.md` §7 is the **predicted** effect, not a threshold. A 10 pp gap at p = 0.01 is a real result and reads GREEN — under the previous wording it matched no branch at all.)*

- **GREEN** → Phase 2 proceeds.
- **AMBER** — gap present, p ≥ 0.05 → **Phase 2 PROCEEDS.** The checkpoint enters `CHANGELOG.md` as the Baseline row with exact n, gap and p. `GOOD.md` is unchanged. **The agent is built to move the gap, not to rescue the p-value.** If A1 is still p ≥ 0.05, the README leads with effect size, its confidence interval, and the n this design would need for power.
- **RED** — gap < 8 pp after Step 0 → **the accuracy claim is withdrawn and the null is published.** CH-08 becomes *"why the gap did not open, measured"*; the corpus, attributor, scorer and permutation null become the contribution; deliverable 4 is satisfied by baseline-arm trajectories. That leaves ~16 h to write it up properly.

> ### VALIDITY CONSTRAINT — why RED may not cut the agent entirely
> *"**Every valid entry must present both a baseline solution and an advanced solution.** The advanced solution should show a meaningful improvement in capability, reliability, efficiency, coverage or engineering quality, not a cosmetic variation."* — `00-MASTER-CONTEXT.md` §4, verbatim
>
> The word is **valid**, which ties it to the qualification gate rather than the rubric. Gating Phase 2 on GREEN alone would produce, on RED, an entry with **no advanced solution at all**.
>
> **Honest note on its authority:** this sentence is on the HackerEarth page and **not** in the brief — `grep -c "advanced solution" context/01-PROBLEM-PDF.md` = **0** — and the master context's own header limits its scope to dates, prizes, eligibility and FAQs. Whether it binds is genuinely unclear, which under hard rule 1 is a STOP-and-record, not an assumption. **Recorded as a ruling; we take the safe reading, because the safe reading is nearly free.**
>
> **On RED: ship the tool and the skill anyway.** Claim the improvement on one of the four other axes the rules accept, measured with the same discipline — instruction-level resolution-claim correctness (already the high-power diagnostic in `CONTEXT.md` §7), the checkpoint queue's catch rate, per-arm token cost, or pool coverage. **Report the accuracy null as the headline honestly, and the axis that did move beside it.**

**Pre-registered numeric fallbacks** — written now, before any number exists, which is what makes this pre-registration rather than rationalisation:
- **CH-02.** If global attributor completeness lands in **[0.80, 0.90)**, restrict the eval set to FR documents with per-document completeness ≥ 0.90, publish the restriction as a named rung of the exclusion ladder with its count, and report both figures. **Below 0.80** the attributor is a documented failure and the headline is withdrawn.
- **CH-03.** Pool gate: decides on **≥ 60** section-level defect notes with a resolvable FR citation. If the full scan returns < 60, fall back to n = 84, demote localisation and class recall to a case study, and proceed. If pairs land in **[30, 42)**, report the real n and state in `GOOD.md` and the README the effect size the sample can and cannot detect. **Do not relax the exact instruction-count match to inflate n** — that is precisely how a predecessor died.

**Model-sensitivity check — runs HERE, at the checkpoint, not at the end (~$2).** Re-run B0 and B0-agent on `claude-sonnet-5` over a 20-item subset while the full matrix runs on `claude-haiku-4-5`. Two purposes: it reports whether the gap holds **across model tiers** — an axis almost no entrant will have — and it guards against a **false RED**, where a cheap model simply fails to use the CFR text and we kill a sound project on weak inference. **If Haiku shows no gap and Sonnet does, that is a finding, not a failure**, and the RED branch is not taken.

**Do not tune to reach green.** An honest red found here is worth more than a green manufactured at hour 20.
**Requires model access** — first chunk that does. See `QUESTIONS.md` Q1.

---

## Phase 2 — the agent · on GREEN **or AMBER** · whatever remains until 06:00 UTC

Each capability chunk commits its **iteration card** to `CHANGELOG.md` (`PROCESS.md` §5) **before** the build, with its prediction.

### CH-05 · `cfr_resolve` tool — GATE: code-only
Designation-hierarchy resolution first, quoted-anchor matching second. Three declared normalisation levels, level reported never applied silently.
**Done when:** golden fixtures pass; Iteration 1 card completed with measured result.

### CH-06 · `SKILL.md` + note-emission contract — GATE: **CODE-ONLY**
The OFR execution procedure; the output contract in `CONTEXT.md` §5. Measure the **tool-availability-vs-tool-use gap** explicitly.
**Done when:** agent emits the full `resolution_trace`; Iteration 2 card completed.

### CH-07 · Ordered-state ledger — **NOT BUILT (ruling R-01)**
Pre-declared as **counted removal #3**. Its iteration card is written in `CHANGELOG.md` with the prediction, the measured justification (order-sensitivity fires on 38–42% of items, two independent counts, not label-correlated), and the ruling that it was cut in favour of measuring the two built capabilities properly. **The card ships; the code does not.**

### CH-08 · Ablations and final arms — GATE: none
A1 minus each capability (**1 rep, pre-registered in `GOOD.md`**); final arms × 3; McNemar; paired bootstrap **clustered by FR document**.
**Done when:** full results matrix committed, failures included, `docs/evidence/` populated.

### CH-09 · Removed experiments + hot take — GATE: none
Current-CFR-text leakage probe; collision-detector removal with measured class size; per-class recall deltas; **blind human-time study** (8 items by hand, stopwatched, before seeing gold).
**Done when:** both removed experiments have numbers; hot take has its two-corpus measurement.

---

## Phase 3 — packaging · protected · opens 2026-08-31 06:00 UTC regardless of Phase 2 state

**Run order is NOT the chunk numbering.** Under the old order the video's own T−8h deadline was unreachable by ~2 hours. Reordered:

| # | Chunk | Wall-clock | Why here |
|---|---|---|---|
| 1 | **CH-14a** · early rehearsal — fresh venv from pinned `requirements.txt` (Python 3.12.2), network off, manifest verify, Tier-1 replay | | a fatal defect must surface with time to fix it, not at T−2h |
| 2 | **CH-13** · video — record, splice, upload, verify signed-out | **must complete by 10:00 UTC (T−8h)** | YouTube processing can take hours |
| 3 | **CH-12** · trajectories + `AI-USE.md` | | |
| 4 | **CH-11** · README + `REPRODUCE.md` + `THIRD-PARTY.md` + `LICENSE` | | |
| 5 | **CH-11b** · **VOICE PASS** — operator only, no session | | see below |
| 6 | **CH-10** · worksheet + disclaimer band + provenance footer | | |
| 7 | **DRAFT-1** · **12:00 UTC — wall-clock, not dependency.** All four fields saved as a draft | | from here the project is insured |
| 8 | **CH-14b** · final rehearsal from the finished repo; secret scan over full history | | |
| 9 | **CH-15** · **SUBMIT · 15:00 UTC.** 17:00 last touch. **Nothing after 17:30.** | | |

**Parallelisable (architect will assign):** CH-10, CH-11 and CH-12 write to disjoint paths and may run as three concurrent sessions under `CLAUDE.md` §"Parallel sessions". CH-13, CH-14a/b and CH-15 are serial.

### CH-11b · VOICE PASS — operator only, no session
**The anti-slop clause is worth up to 5 of the 20 End-to-End points**, and everything we produce is machine-written. The operator reads the README, the Description and the video script aloud and rewrites anything that does not sound like him. Nothing is generated in this chunk; only cut and rewritten.
**Done when:** the README's opening three paragraphs and the entire Description have been hand-edited, and no paragraph survives that the operator would not say out loud.

### CH-10 · Codification worksheet
Single self-contained static HTML. One row per instruction: anchor, resolution level, designation state, the section text with the anchor highlighted or its absence marked, the collision trace, the human-checkpoint queue. **Opens from a clean clone with the network off.**

### CH-11 · README + reproduction guide
README order: intended user → bottleneck → why valuable → **Improvement Changelog** → main failure mode → hot take. Reproduction guide, both tiers: **Tier 1** replays committed artifacts offline in < 90 s at $0; **Tier 2** re-runs live with a key, runtime and cost stated. Versions pinned.

### CH-12 · Trajectories + AI-USE.md
**The selection rule — required, because "representative" is a choice and an unexplained choice looks like curation.** Publish it in `AI-USE.md` before selecting:
- **one per agent class** minimum — research/ideation, coding, solution arms;
- for the solution arms: the **first** run, the **median-cost** run, one run containing a **retry**, and one containing a **`human_checkpoint`** record;
- for coding agents: **every** chunk transcript (they are the process evidence);
- **plus every run whose verdict disagreed with gold** — failures are not filtered out.

The complete set ships in the repository; the curated set ships in the ≤50 MB zip; the Description links the full set. Print the counts of both.

`AI-USE.md` names every model, tool and agent, what each did, and where its trajectory is.

### CH-13 · Video ≤ 5 min
Beats: problem → simple baseline → one realistic execution end to end → final comparison → changelog → the change that contributed most → **one experiment removed**.
**Host: unlisted YouTube** (the form takes a URL, not an upload). **Fallback is a second hosted copy on a different provider — the MP4 is NOT committed.** A five-minute screen recording routinely exceeds 50 MB on its own; committing it puts it inside `git archive` and breaks the one cap that must not move.
**Done when:** the link plays **in a browser profile not signed into the operator's Google account**, with audio; duration is **under 5:00**, not 5:0x; the URL is recorded in `README.md`, `SUBMISSION.md` and the HackerEarth form.
**Upload by T−8h at the latest** — YouTube processing can take hours and a video still processing at 17:55 UTC is a missing deliverable.

### CH-14 · Clean-clone rehearsal + submission archive
1. Clone to a second path, network off, manifest verify, **Tier-1 replay green from the clone**.
2. Secret scan over the **full history**, not just the working tree.
3. Build `submission-<short-sha>.zip` with `git archive --format=zip HEAD` (respects `.gitignore`, excludes `.git`). **Assert < 50 MB** — the HackerEarth cap.
4. **Extract the zip to a fresh temp directory and run the Tier-1 replay FROM THE EXTRACTION**, not from the clone. The zip is what a judge opens; it is the thing that must work.
5. Write `SUBMISSION.md` at the repo root listing the six items the FAQ names — repository, archive, tests, README, agent-use evidence, demo video — each with its path or URL, so a validator ticks them without hunting.

**Done when:** the zip is under 50 MB and Tier-1 replay passes from the extracted copy on a machine with the network off.

### CH-15 · Submit — **hard start 2026-08-31 15:00 UTC (T−3h)**
The plan does not end at rehearsal. This chunk owns the transaction.

The HackerEarth form has exactly four required fields (verified from inside it, 2026-08-30):

| Field | Content |
|---|---|
| **Title** | short and descriptive |
| **Description** | **the first thing a judge reads.** The 20-second case: user → bottleneck → what was measured → the headline number with its honest baseline → the GitHub link (there is no repo field) |
| **Video URL** | the unlisted YouTube link from CH-13 |
| **Source Code** | upload `submission-<sha>.zip`, **≤ 50 MB** |

**Procedure:**
1. **Save a draft as soon as anything complete-but-imperfect exists** — earlier than T−3h if possible. *"Revisions are allowed until the deadline; only the latest complete submission is evaluated."* An early draft removes the single-point failure of one submission attempt at 17:55.
2. At T−3h, submit the real package.
3. Revise until T−1h. **Stop touching it at T−1h.**

**Flip the repository public — this has an owner now.** Ground rule 10: *"Give judges enough access to run the project and reproduce the main result."* A private repo returns 404 and `gh` or any logged-in browser gives a **false pass**. Verify anonymously: `curl -s -o /dev/null -w "%{http_code}" https://github.com/chinmoypaul8897/instruction-that-wont-execute` must return **200**, run with no credentials. Screenshot it into `docs/evidence/access/`.

**Done when:** the submission is in a submitted state (not draft); the video link plays from a signed-out browser; the uploaded zip has been re-downloaded and opened to confirm it is intact; **and the repo returns 200 to an unauthenticated request.**
