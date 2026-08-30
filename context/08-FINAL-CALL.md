# THE FINAL CALL

## 1. THE CALL

**STICK — build "The Instruction That Won't Execute" — but kill the sequence/ledger reframe as the centrepiece and change the *output shape* instead: the agent stops emitting a bit and starts emitting the editorial note NARA would have to publish.**

The evidence, in the order it settles the question:

- **All five auditors returned `no_needs_more` on the reframe.** As-specified scores: 21, 21, 21, 21, 20 (mean 20.8, sd 0.4 — near-perfect convergence). Reframed: 24, 19, 23, 22, 18 (mean 21.2, sd 2.6). The reframe buys **+0.4 points of mean and 6× the variance.** The two auditors who scored it *down* are the two who measured its pool before scoring it.
- **The collision class was measured five independent ways and it is empty-to-tiny:** 0/68 labelled items contain a redesignation instruction; 0/82 harvested blocks contain the string "redesignat"; 3/82 labelled items have any collision (2 positive); 26/1,984 corpus items (1.31%) are order-sensitive and 15 of those 26 are *correct drafting* (redesignate-then-add); ~25–30 collision-flavoured notes CFR-wide, mostly pre-2017. **And NARA never publishes a note naming an intra-rule conflict** — live probe: `"conflicting amendments"` total_count = 0. The label cannot confirm the mechanism the ledger detects.
- **OFR announces the dependency in prose.** 39% of redesignation AMDPARs contain "newly redesignated"; on the post-redesignation subset it is 78.9% (45/57). Both showcase hard cases proposed for the video contain the words "newly redesignated" *on screen*. A two-word regex abstains correctly on four-fifths of the class.
- This is **CROSSCheck's death, repeated one file later**: a named hard case with n≈0 in the benchmark built to showcase it, and the 103-splits→13-genuine audit is the same shape. §8.11 wrote the lesson down: *audit any mechanically-derived positive class before believing its size.* The reframe asks you to skip that step on the row that decides first place.
- **All five rivals died to measured attacks** (verdicts: worse, worse, worse, dead, dead; totals 61–72). Codify falls to a 95-line interpreter at 0.333 and to a purity-gate pincer with no agent-shaped band; Codify-or-Refuse hands a risk-free 0.500 to always-CANNOT_EXECUTE and collides head-on with Prior et al., NLLP@ACL 2025 (same task, same exact-match metric, same hard case, same conclusion); LEDGER's 24.6% moat is a section-attribution bug that fixes to 7.0% and lets a 25-line script reach the agent's own pre-registered target; REPLAY loses to a 25-line script at 0.491 and to `cfpb/regulations-parser`; STALE BASE loses 1.000 to a 20-line containment probe *after* its own CITA strip.
- **There is no destination.** Erratum Gate is measured dead (0.675 vs 0.675, p = 1.00, four configurations). A new idea at T−46h has a 2/143 prior on filter 4 and, decisively, **no cheap abort** — this project answers its own question at H6 for ~6 hours.

And one thing I measured this session that no auditor had, which is what makes STICK the *strong* call rather than the safe one: **NARA's editorial notes carry more than a bit, and the pool is 2–3× larger than the incumbent believes.**

---

## 2. The 30-point row — the honest number

**As specified in §7: 21/30.** Not 24, not 18. Five independent lenses returned 21, 21, 21, 21, 20. That is the tightest agreement anywhere in the packet and I am not going to second-guess it.

**Reframed as proposed: 21/30.** No change. The mean moves +0.4 and the dispersion triples.

### Where the five agreed — and this is the finding

| Convergent claim | Auditors | Strength |
|---|---|---|
| The reframe is not sufficient | **5/5** | unanimous |
| Keep the project; do not abandon | **5/5** | unanimous |
| **The cap is the one-bit output**, not the narrative | **5/5** | unanimous, five different phrasings |
| §7.3's own concession is the deduction: the +32 pp belongs to **B0-agent, a sanctioned baseline** | **5/5** | quoted by all five |
| The fix is to **change the output shape / unit of prediction** | **4/5** | (the fifth prescribes composition + repair instead) |
| The AMDPAR attributor is a **carry-forward bug, not a hard problem** | 3/3 who measured it | 0.99, 0.807/0.914, 0.998 |
| The pool is **~250–300, not 92** | 3/3 who measured it | 269, 284 (255 post-2017), 306 |
| **eCFR and federalregister.gov are 403 from this machine** | 3 measured + **my own probe today** | 4 confirmations |
| `anchor_resolve` **no-ops on most of the pool** | 2/2 who measured it | 26/33 and 35/42 items have no extractable quoted anchor |

Five lenses, one answer: **the row is capped because no design choice can be *seen* doing work.** A capability can only be inferred from a delta in an average, the average is a bit, and the bit moves on n = 84, where 6 pp with ~12 discordant pairs is McNemar p = 0.146. Three changelog rows reading "+6 pp, not significant" is what 21/30 looks like.

### Where they disagree, and who is right

Auditors 1 and 3 scored the reframe **up** (+3, +2) on its *narrative* — "each instruction individually valid, the rule collectively defective" is Appendix Example 3 transposed, and the memory/consistency lane is 1 of 64 occupied. Auditors 2, 4 and 5 scored it **down** (−2, −1, −2) after *counting its pool*.

**The ones who counted are right**, and auditor 1 effectively concedes it: its own deduction (b) is "the collision class size is unmeasured — §7.7 names it as the hard case and gives no n." That is the tell. A centrepiece with n ≤ 3 in the labelled pool, defeated by a 15-line detector on the general case, self-announced in prose 39–79% of the time, and **never labelled by the authority**, is not a thesis. Auditors 1 and 3 scored a sentence; auditors 2, 4 and 5 scored a dataset.

### What I measured this session, which changes the arithmetic

Downloaded nine govinfo ECFR bulk title XMLs (titles 12, 20, 21, 24, 26, 40, 42, 45, 49 — 407 MB, keyless, HTTP 200; files at `C:\Users\chinm\AppData\Local\Temp\claude\c--Users-chinm-micro1-engineering-challenge\9acf056f-c3bb-4803-968b-020f9249d7a0\scratchpad\fc\`) and extracted `<EDNOTE>` structurally rather than through the eCFR search API:

| Measurement | Value |
|---|---|
| Total EDNOTEs, 9 titles | 903 |
| **Codification-defect notes** | **44** (title 12: 7 · 21: 2 · 26: 10 · 40: 12 · 42: 5 · 45: 3 · 49: 5 · 20, 24: 0) |
| Contain the incumbent's exact query phrase `"could not be incorporated"` | **44/44** |
| Section-level (vs appendix/part-level) | 38/44 |
| **Name the FR citation** | **44/44** |
| **Name the failing target *below section level*** | **6/44 = 13.6%** |
| **State an explicit failure mechanism** | **10/44 = 22.7%** |
| Do both | 4/44 = 9.1% |
| Generic "due to inaccurate amendatory instruction", no mechanism | 32/44 = 72.7% |
| Mention redesignation | 3/44 = 6.8% |
| Operation named in note | revise 10 · add 5 · remove-and-add-in-place 4 · redesignate 3 |

**Two consequences.**

**(a) The pool.** Nine of fifty titles yield 44 notes carrying the incumbent's own exact query string, while that query returned **92 across all fifty**. Naive projection 244; my nine titles were chosen amendment-dense, so the honest band is **150–250 defect notes, ~130–210 of them section-level, against the 92 the API found.** A fourth independent route to the same conclusion three auditors reached (269 / 284 / 306). **The eCFR search API undercounts the pool by roughly 2.3×, and §8's belief that pre-2017 coverage was the binding constraint is wrong — the query was.**

**(b) The output shape, and this is the important one.** NARA's note is not always a bit. In 22.7% of cases the authority *states the mechanism* and in 13.6% it *localises the failure below section level*, in its own words, dated and citable:

> *§ 702.2 was amended by revising the definition of "Regulatory Capital"; **however, the definition did not exist.***
> *§ 1.199A-0 was amended by adding an entry for § 1.199A-2(b)(2)(iv), **however, this paragraph already exists.***
> *§ 149.510 was amended in part by revising paragraph (c); however, **the amendment to paragraph (c)** could not be incorporated **because it contained incomplete text.***
> *§ 702.504 (prior to redesignation as § 702.304) was amended in paragraph (b)(4) by revising the citation "§ 702.306(c)"; **however, that citation did not exist in the section.***

**Those are externally-authored, zero-contestant-labelled, sub-section, mechanism-typed ground truth.** Property 1 stays a tick. And a constant scores **exactly zero** on them, because a constant names no designation and no mechanism — the degenerate lane closes on the second component by the shape of the output space, with no count-matching required.

---

## 3. Is the sequence/ledger reframe enough?

**No.** It is the right *axis* and the wrong *object*: it changes what you say about the agent without changing what the agent emits, and the cap is in the emission. Four additions get the row to **25–26**; a fifth, gated, gets it to 27.

### A. The agent emits the note, not the bit — 3 h (mostly already budgeted)

Output becomes `{verdict, failing_designation, failure_class, resolution_trace}` and `WILL_FAIL` is a **derived field**. `failure_class` comes from NARA's own vocabulary, read off the notes rather than invented: `target-does-not-exist` · `target-already-exists` · `quoted-text-not-present` · `incomplete-set-out-text` · `incorrect-citation-or-designation`.

Three things happen at once, and each is directly worth points on this row:
- **Every capability becomes readable in the artifact.** A judge scrolls one worksheet row and *sees* `resolve()` return `{designation_exists: false, siblings: [(b)(1),(b)(2)], level: none}` and *sees* the verdict derived from it. The row's question is answered on the page instead of inferred from an average.
- **`n` multiplies.** The instruction-level trace turns ~250 section items into ~1,000+ scored resolution claims. The per-capability ablation moves from "never significant at 12 discordant pairs" to "sometimes significant."
- **The localisation and class sub-scores are things B0-agent structurally cannot produce.** B0-agent has no procedure for naming which designation failed and why. That is where the +8 pp residual has somewhere to *live* — right now it has nowhere.

This is not new work. §7.10 already builds the codification worksheet at H20–22 and calls it presentation. **Move it to H7 and make it the output.**

### B. Harvest the pool structurally, not through the search API — 1.5 h, and it is forced anyway

`www.ecfr.gov` and `www.federalregister.gov` return **HTTP 403 from this machine** (my probe, 2026-08-30; three auditors independently). `govinfo.gov` returns 200, needs no key, and its `robots.txt` sitemaps `/bulkdata`. Structural `<EDNOTE>` extraction over all 50 ECFR title XMLs is the label channel, and it is *better* than the API: 44/44 notes carry their own FR citation, so FR-document resolution is deterministic from the label with no search step at all. Pool goes from 92 to 150–250. **This single change is what powers everything downstream.**

### C. Carry-forward the AMDPAR attributor — 1 h

Iterate AMDPARs in document order, maintain the last-named section, attach lettered sub-instructions to it. Measured three ways by three independent parties: **0.99 (46/5,590 unattributable), 0.807/0.914, 0.998 (422/423 on a 423-instruction rule).** The project's own §8.2 "single highest-value build task" and its H4 stop-gate are cleared in an hour, and 3–4 planned hours are freed to pay for A.

### D. Lead with composition and foreclosure, not retrieval — 0 h, already measured

The 30-point row's headline stops being "we gave it the document" and becomes four numbers you already own:

| Arm | Score |
|---|---|
| model alone, no CFR text | **0.545** |
| best model-free script, 150 lines, honest CV | **0.5855** (best of 26 features 0.5934, inside its own null, p = 0.185) |
| the tool's own raw signal alone (designation absent → FAIL) | **0.52** |
| **composed** | **target ≥ 0.85** |

*"The model converts malformed amendatory prose into typed edit operations; the tool executes and verifies them against frozen text; each half alone is at chance and only the composition works."* That is a causal answer to "which design choices helped", it has no rhetoric in it, and it costs nothing. Beside it, the foreclosure sentence: *"Without the tool the agent asserted a quoted anchor was present when it was not, in X% of instructions; with the tool, 0% by construction."* — a T4 claim, and Chinmoy's own signature move (`the model structurally cannot state an unbacked price`).

### E. STRETCH, gated at H14 — `apply_instruction` executable verification — 4–6 h

`apply_instruction(section_tree, op, anchor, designation) → new_tree | Failure(reason)`. The agent's `WILL_EXECUTE` is accepted only if the simulated edit succeeds; its `WILL_FAIL` only if the edit throws *for the reason the agent named*. The harness executes rather than the agent asserting. No model in the scoring path — the opposite of the CEO's circularity objection. **Only build this if H8 is green and ahead of schedule.** Note the rival attacks: a deterministic executor is lethal *as a metric* (it becomes the baseline that beats you) and safe *as a tool* (both arms may use it). Keep it on the tool side of that line.

**Honest ceiling: A–D lands 25–26/30 and is buildable. A–E lands 27 and is not, at 24 hours, without cutting the video.**

---

## 4. The rivals

- **Codify (replay the amendment)** — *lost.* A 95-line interpreter scores 0.333 exact against a claimed 0.000 floor, and the purity gate is a pincer: tighten it and you keep exactly the items a compiler wins; loosen it and exact-match is unreachable for anything that sees only pre-text plus instructions. Also n = 9 is n ≈ 5 (byte-identical AMDPARs), and 5 of 9 "pre-texts" were `<EFFDNOTP>` note fragments misread as sections.
- **Codify or Refuse** — *lost.* Its central claim ("no constant scores above zero") is false on its own spec: nothing penalises `CANNOT_EXECUTE` on an executable item, so always-refuse collects **0.500** risk-free. 63.3% of amendment units have the answer printed verbatim in the input. And Prior et al., NLLP@ACL 2025 published the task, the exact-match metric, the multi-step hard case *and* the "drafts subject to human verification" conclusion.
- **The Part Ledger** — *lost.* Its own author rates it `probably_not` in 24 hours and recommends it only as Codify's stretch tier. Correct.
- **LEDGER (instruction-level localisation)** — *lost, and it is the closest thing to a win.* Its 24.6% false-defect moat is a section-attribution bug: fixed, it is 7.0%, and its own prescribed pool filter drives it to ~2.5%, at which point a 25-line script reaches macro-F1 0.53–0.81 against a pre-registered agent target of 0.70. Its "structural guarantee" fails at 78.9%. **But its instruction-level output shape is right, and I am taking that** — as a *diagnostic on the incumbent's already-foreclosed primary*, not as a new primary with a fresh unattacked surface.
- **STALE BASE** — *dead.* A 20-line containment probe scores 1.000 on the flagship class *after* the CITA strip, and 15/15 on localisation. Its scoring rule defends against constants while filter 4 is about scripts — the exact confusion that killed CROSSCheck at A1 = 100% while its constants sat at 5.6%.

**Nothing survived. Every rival traded a measured 0.500 floor for an unmeasured one, and every unmeasured floor collapsed the first time someone wrote the script.**

---

## 5. THE FINAL SPEC — only the deltas

Everything in §7 not named here is unchanged.

### Headline
**Was:** 0.500 → 0.818 — giving the agent the point-in-time CFR text.
**Now:** *An amendatory instruction carries no evidence of its own executability. Three systems that each know part of the answer — a model at 0.545, a 150-line script at 0.5855, the tool's raw signal at 0.52 — compose into one that reconstructs NARA's own editorial note.* The retrieval gain is reported **as the baseline it is** (§7.3's honesty survives contact with the README, in the same table, one row above).

### Output shape — the load-bearing change
Per `(rule, section)` the agent emits `{verdict, failing_designation, failure_class, resolution_trace[]}`. The **codification worksheet is the artifact**, not a presentation layer. Moves from H20–22 to H7.

### Primary metric — **unchanged**
Execution-prediction accuracy on the exact instruction-count-matched pair set, string equality against a NARA-authored fact. Do **not** change the primary at T−46h: it is pre-registered, piloted, and it is the only metric in this packet whose trivial-attack surface has been measured (`n_instructions` pinned at 0.5000; best of 26 features 0.5934, empirical p = 0.185). Every rival that changed its primary died to the first script someone wrote.

**Added beside it, never blended** (micro1's own LongExtractBench language):
1. **Defect localisation accuracy** on the NARA-localised subset (13.6% of notes → ~20–30 items at the projected pool). Constant scores **0.000**.
2. **Failure-class recall** against NARA's own five-way vocabulary on the mechanism subset (22.7% → ~35–55 items). Constant scores **0.000**. This is micro1's published "structured failure taxonomy," externally authored.
3. **Instruction-level resolution-claim correctness** against a deterministic oracle — *is this quoted string / this designation present in the point-in-time text?* is a computable fact, not a judgement, so it costs **zero authored labels** and yields ~1,000 records. **This is a diagnostic, never the primary** — a script scores 1.0 on it because it *is* the script. It is where the per-capability ablations get their statistical power.
4. Guard metrics unchanged (false-defect ≤ 0.25, missed-defect ≤ 0.25, attributor completeness ≥ 0.90).

### Capability order — same three slots, two re-justified
1. **Tool — `cfr_resolve` (widened).** Designation-hierarchy resolution **first**, quoted-anchor matching second. Forced by measurement: 26/33 and 35/42 labelled items have *no extractable quoted anchor*, and the note taxonomy names `did-not-exist` / `already-exists` — designation-*state* facts — as the dominant mechanisms. A pure quoted-string matcher no-ops on ~80% of the pool.
2. **Skill — `SKILL.md`.** Unchanged in substance; now also specifies the note-emission contract (name the designation, name the class, cite the offset).
3. **Memory — the ordered-state ledger. Kept, and re-justified.** *Not* to catch collisions (measured 1.3%) but so instruction k+1 is read against the state instructions 1..k left — which fires on **38–42% of items** (31/82 and 833/1,984, two independent counts, and *not* label-correlated: 16 defective / 15 executable).

### Removed experiments — now two, both honest
- §7.8 unchanged: current CFR text instead of point-in-time, with the pre-registered directional leakage prediction. Best thing in the plan.
- **New:** the **intra-rule collision detector**, built on top of the ledger, **removed with its measured class size as the stated reason.** A removed capability with a *counted* n=2 hard-case class is worth more on this row than a kept capability with an *uncounted* one — and it is the disciplined version of the reframe this session was asked to evaluate.

### Hard case — changed
**Was:** the intra-rule collision (measured n ≈ 2–3 in the labelled pool).
**Now:** **the defect that is not the first instruction** — a section where instructions 1..k−1 all execute and instruction k fails, so a partial read rules correctly for the wrong reason. Measured n = 16 defective items in the 82-item pilot pool. Three verified NARA-authored exemplars, from my own extraction today, in ascending sharpness:
- 12 CFR 702.2 — *revising a definition that did not exist* (target named, not quoted — the tool's widened form is what catches it)
- 26 CFR 1.199A-0 — *adding an entry that already exists* (the pure designation-state check)
- 12 CFR 702.504 → 702.304 — *revising a citation, after redesignation, that did not exist in the section* (the collision, honestly counted, kept as the sharpest single instance and named as rare)

### Pitch sentence
> **I built the agent that reads a Federal Register amendatory instruction the way the Office of the Federal Register does — and made it write the editorial note NARA will have to publish if the rule ships as drafted.**

### Leakage strips — publish all three as a named design decision
`<EFFDNOTP>` (prints the pending amendment verbatim: *"the revised and added text is set forth as follows"*), the eCFR `"Link to an amendment published at 88 FR …"` annotation (in 30% of point-in-time XML, and it names the very rule under test), and `<CITA>` / `<EAR>`. Strip, list in the freeze manifest, and say why in the README **before a judge asks**.

---

### Revised first 8 hours

| Hours | Work | Done when |
|---|---|---|
| **H0–0.75** | Repo, `.gitattributes` `* -text`, **run logger before any other code**. Simultaneously kick off, in background, the download of all 50 govinfo ECFR bulk title XMLs and the FR daily issues you will need. Nothing waits on the network again. | Dummy run emits a trajectory + a cost row; download running |
| **H0.75–2.0** | **HARVEST-A — labels.** Structural `<EDNOTE>` extraction over all 50 titles, union regex. Per note parse: section, FR citation, failing designation, mechanism class. **Do not touch ecfr.gov or federalregister.gov — both 403 (verified 4×).** | **GATE-1** |
| **H2.0–3.5** | **HARVEST-B — instructions.** FR daily XML from govinfo (the note's own citation gives page + date). AMDPAR extraction with **carry-forward attribution**. | **GATE-2** |
| **H3.5–4.5** | **HARVEST-C — before-text.** govinfo CFR annual edition at (effective year − 1). This removes the 2017 floor *and* the eCFR dependency in one move. Apply and log all three leakage strips. | Text present for ≥ 70% of pool; strip list committed |
| **H4.5–5.5** | Count-matched pairs, full exclusion ladder, SHA-256 freeze, `refetch.py`. | Balance asserted by a test; manifest verifies from a clean clone |
| **H5.5–6.5** | Scorer (stdlib): verdict accuracy, localisation, class recall, resolution-oracle, both guards, attributor completeness, `success + failure == n`, tokens/cost. **Re-run the full 26-feature sweep AND its permutation null on the new, larger pool** — the pool changed, so the foreclosure must be re-earned. | Null re-run; best feature reported with its p |
| **H6.5–7.0** | **GATE-3 — headroom.** B0 on the full pool, then one B0-agent pass. | **The number that decides the project** |
| **H7.0–8.0** | Freeze `GOOD.md`: primary + three co-reported metrics with thresholds, the +8 pp target, both guards, predicted B0 / B0-agent / A1, and **both** removed-experiment predictions. Commit and timestamp **before A1 exists**. Worksheet skeleton scaffolded. | Pre-registration committed |

### The gates, and the exact numbers

**GATE-1 (H2) — pool.** Section-level defect notes with a resolvable FR citation. **Decides on: ≥ 60.** My nine-title measurement projects 130–210; if the full scan returns < 60, fall back to n = 84 as originally specified, demote localisation and class recall to a case study, and proceed — the project still runs, it just runs at 23/30 instead of 26.

**GATE-2 (H4) — attributor.** Completeness **≥ 0.90**, unchanged from §7.10. Three independent measurements say carry-forward delivers 0.99. If it does not, **stop and fix before anything else** — a pool built on truncated blocks is not recoverable downstream and it is precisely what made the pilot report 0.708 instead of 0.818.

**GATE-3 (H6.5–7) — headroom. This is the go/no-go, and here is exactly what decides it:**

> **B0-agent − B0 ≥ +15 pp with McNemar p < 0.05 at n ≥ 200.**

- **Pass** → proceed. §8.1's own projection says the pilot rates at n = 84 give Fisher p = 0.0002; at n ≥ 200 this is comfortably powered and the "MATTERS MOST" open question is *closed*, in hour seven, in public.
- **B0 ≥ 0.70** → the instruction text is leaking executability. Do not weaken B0. Strip the quoted anchor (keep operation + designation), re-run the gate.
- **Fail (gap not significant at n ≥ 200)** → **abandon at H6 and ship the negative result.** *"The corpus does not change the answer at n = 213"* is publishable, it is what §8.1 pre-committed to, and it is a result the contestant has shipped twice before (Acumen proved the strategy loses money; DrillScribe's headline is that models don't transfer). It costs ~7 hours and leaves 16 to write it up properly.

---

## 6. What would still make this lose

**1. A1 − B0-agent measures ≈ 0.** *The* risk. The +32 pp headline belongs to a sanctioned baseline; no capability has ever been measured, and the Erratum Gate precedent is capability additions measuring **exactly zero, p = 1.00, across four configurations**.
→ *Mitigations, in order of force:* (a) the pool ×2.3 makes +8 pp detectable at all; (b) the localisation and class sub-metrics give the capabilities somewhere to appear that B0-agent **structurally cannot reach** — it has no procedure for naming the failing designation; (c) the instruction-level oracle gives ~1,000 records where a 6 pp delta is testable; (d) pre-commit in `GOOD.md` to shipping the null as the result. A submission whose changelog says *"iteration 3 measured +1 pp, p = 0.62, removed"* scores better on this rubric than one that hides it.

**2. Harvest overrun eats the build.** govinfo bulk is 1–2 GB and the primary APIs are 403.
→ Start the download at minute 5, in background, before writing a line of parser. Hard stop at H4.5 — ship whatever pool exists and state the coverage boundary. **Cut the pre-2017 fallback as a separate workstream**: annual editions are now the *primary* before-text source, not a fallback, so the work is done once.

**3. Leakage in the shipped text.** Three named vectors, two of which the kill test never mentions: `<EFFDNOTP>`, the eCFR pending-amendment link (30% of documents, names the rule under test), `<CITA>`.
→ Strip, publish the strip in the manifest, and note that §7.8's removed experiment is designed to detect exactly this class of error. Getting caught with an unstripped leak is a total loss on Reproducibility *and* on credibility; disclosing three strips you found yourself is worth points.

**4. The foreclosure does not survive the bigger pool.** The 0.5934 / p = 0.185 null was measured at n = 84. Change the pool, change the null.
→ Re-run the full 26-feature sweep **and** its permutation null at H5.5–6.5, **before any agent number exists**, and add the two features the reframe would have introduced (`has-redesignation-intersecting-another-AMDPAR`, `count-of-distinct-designations-touched`) so that attack is closed too. Pre-register: if the best feature clears its null at p < 0.05, re-tighten the matching or die there.

**5. The tool no-ops.** Quoted anchors exist in only ~17–21% of labelled items.
→ Already handled by the widening in §5, and the measured note taxonomy is the *evidence* for the widening — which itself is a changelog row ("Iteration 1 shipped as quoted-anchor matching; measured 19% coverage; widened to designation-hierarchy resolution").

**6. Presumed negatives.** A section with no note may still have failed silently.
→ Count-matched siblings come from the *same rule*, so the negative is a section the same document *did* codify. The noise is one-sided and structural; state it in one sentence and move on.

**7. Anti-slop (20 pts) and the missing deliverable (total loss).** ~62% of the visible field is engineers building for engineers, and a missing trajectory file is a zero.
→ The worksheet is the artifact and it must look authored. Reserve H22–24 as written, do not spend them. The video's best line is now verified and needs no editing: *"§ 702.2 was amended by revising the definition of 'Regulatory Capital'. Here is § 702.2. There is no such definition. OFR could not codify it."*

**8. Prior art on the incumbent.** The consolidation literature (Prior et al. 2025; `cfpb/regulations-parser`; Akoma Ntoso change management) is dense — but it is all about *applying* amendments. **Executability prediction is its complement and appears in none of it.** Say so explicitly in the README, with the citations, and the rivals' fatal flaw becomes the incumbent's differentiator.

---

## 7. What I would do with 40 build hours

I would build `apply_instruction` as a real designation-state machine and make verification *executable* rather than argumentative — the harness runs the agent's claimed edit and accepts `WILL_FAIL` only when the simulated edit throws for the reason the agent named — and I would add `repair@1`: for every predicted defect the agent emits a corrected instruction, and the harness re-runs the executor on it. That converts the deliverable from a verdict into the drafter's actual next action (a correcting document costs another Federal Register cycle), and it is the one shape that reaches 27–28 on this row, because the agent's success criterion becomes *a deterministic downstream process accepts its output*. I would also derive per-instruction labels by diffing the point-in-time section at (effective − 1) against (effective + grace) on sections amended by exactly one rule, which multiplies n again and drops chance from 0.50 to ~0.20; run a genuine 2×2 ablation with three runs per cell instead of a dependent chain; and take the human-time study to 20 items instead of 8. **What the clock is buying instead: a pool that is 2.3× bigger, a headline the baseline does not own, and a submission that is finished.** At T−46h, finished beats 28.