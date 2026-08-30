# CONTEXT.md — THIS FILE IS LAW

**Project:** The Instruction That Won't Execute
**Version:** v1.1 · 2026-08-31 · amended at SPEC-FIX-2 under the `QUESTIONS.md` Q11 ruling; see §13
**Author:** ARCHITECT only. No build session edits this file.
**Precedence:** the official hackathon PDF (`context/01-PROBLEM-PDF.md`) outranks this file. This file outranks `plan.md`, the code, the tests, and anyone's memory. Any conflict between code and this file is a defect in the code.

**Provenance:** assembled from `context/08-FINAL-CALL.md` §5 (deltas, authoritative) applied over `context/07-KILL-TEST.md` §7 (base spec). Both survived adversarial review by 13 and 15 independent agents respectively.

---

## 1. Goal, non-goals, precision-critical domain

### Goal
Build an agent that reads a US federal final rule's **amendatory instructions** together with the CFR text **as it stood on the publication date**, and predicts whether the Office of the Federal Register will be able to **execute** each instruction — emitting the editorial note NARA would have to publish if it cannot.

### Non-goals — state these in the README
- Not a legal-advice tool. Output is an input to a drafter's judgement, never a filing.
- Not a classification-accuracy benchmark. We do not measure whether the *substance* of a rule is right.
- Not a general CFR question-answering system.

### Precision-critical domain
**Paragraph designations and quoted anchor text.** `(b)(4)(i)(A)` and the exact characters of a quoted string are the objects the whole result rests on.
- No normalisation may silently alter either.
- Matching is attempted at three **declared** levels — `exact` / `whitespace-collapsed` / `alphanumeric-only` — and the level achieved is **reported in the output**, never applied invisibly.
- No lossy encoding, no unicode folding, no smart-quote substitution anywhere in the pipeline.

---

## 2. The user, the bottleneck, the value

**User.** A regulations drafter or Office of the Federal Register liaison clearing a final rule for publication.
**Decision.** Per section: *will this amendatory instruction codify?*
**Clock.** The rule's statutory or court-ordered effective date.
**Exposure.** If the instruction is defective, OFR cannot incorporate it, the CFR text never changes, and NARA publishes a permanent, citable editorial note recording that the agency's rule did not take effect as written. The remedy is a correcting document — another Federal Register cycle.

**The bottleneck.** An amendatory instruction is an **anchor plus an operation**. It executes if and only if the anchor is present in the CFR exactly as quoted, and the target designation resolves at the right level of a nested hierarchy. The drafter writes against the text she believes is codified; OFR executes against the text that actually is. **The instruction carries no evidence of its own executability.**

**The generalisation — lead the README with this.** The underlying shape is *a batch of edits, each individually valid, that fail when applied to the real target.* Database migrations, refactors, config rollouts, infrastructure-as-code. The Federal Register is not the point; it is the one domain where this problem has **public, government-authored ground truth**.

---

## 3. The headline claim

> An amendatory instruction carries no evidence of its own executability. Three systems that each know part of the answer — a model, a ~150-line script, and the tool's raw signal, each near chance alone — **compose** into one that reconstructs NARA's own editorial note.

> ⚠️ **Provenance of the pilot figures 0.545 / 0.5855 / 0.52.** These come from `context/07-KILL-TEST.md` §7.3 and **trace to no committed artifact on this machine.** They are pre-competition pilot numbers at n=11 and **must not appear in the README, the Description or the video** until CH-08 re-derives them on the real pool with an evidence path. Until then this file carries them as *provenance-unverified*, and the headline is stated qualitatively as above. **A number without an evidence path violates hard rule 14.**

**The retrieval gain is reported as the baseline it is.** The **+27.3 pp** from giving the model the CFR text belongs to `B0-agent`, a PDF-sanctioned baseline. *(Pilot figure, pre-competition, n=11 — labelled as such everywhere it appears. The shipped number is CH-08's, measured on the real pool. An earlier draft of this file also quoted “+32 pp” for the same intervention; that figure is withdrawn.)* It appears in the results table one row above the agent, labelled as a baseline. This honesty is not optional: it is already conceded in the spec's own §7.3 and a judge will find it.

**Pitch sentence.**
> I built the agent that reads a Federal Register amendatory instruction the way the Office of the Federal Register does — and made it write the editorial note NARA will have to publish if the rule ships as drafted.

---

## 4. Arms

| Arm | PDF baseline type | Gets | Predicted |
|---|---|---|---|
| **B-script** | type 3 (simple script) | best model-free attack: threshold on any of ~26 cheap features, honest 5-fold CV, **reported with its permutation null** | ~0.59, p ≈ 0.185 |
| **B0** | type 1 (one direct prompt) | one model, one prompt, the amendatory instruction only — **no CFR text** | ~0.50 (chance) |
| **B0-agent** | type 2 (general agent, basic tools) | same model **with** point-in-time section text and search tools; no skill, no memory | **~0.75** |
| **B0′** | compute-matched control | B0-agent at A1's exact token budget, spent on best-of-3 self-consistency with a published tie-break | — |
| **A1** | the solution | B0-agent + the two built capabilities in §6 | ~0.85 |

**Fairness rules.** All arms get the same task, the same items, the same model, and the same frozen corpus. Any difference in resources is stated in the results table. Token counts for every arm are published side by side.

---

## 5. Output contract — the load-bearing design decision

Per `(rule, section)` item the agent emits:

```json
{
  "verdict": "WILL_FAIL | WILL_EXECUTE",
  "failing_designation": "(b)(4)(i)(A) | null",
  "failure_class": "target-does-not-exist | target-already-exists | quoted-text-not-present | incomplete-set-out-text | incorrect-citation-or-designation | null",
  "resolution_trace": [
    { "instruction_index": 1, "operation": "...", "anchor": "...", "designation": "...",
      "found": true, "level": "exact|whitespace|alphanumeric|none",
      "designation_exists": true, "siblings": ["..."], "char_offset": 1234 }
  ]
}
```

**`verdict` is a DERIVED field of `resolution_trace`, not the primary output.** This is the change that earns the 30-point row: every capability becomes directly readable in the artifact rather than inferable from an average.

`failure_class` values are **read off NARA's own note vocabulary**, not invented.

---

## 6. Capabilities — two built, one pre-declared as a counted removal

> **Ruling R-01 (2026-08-30):** capability 3, the ordered-state ledger, is **NOT BUILT**. It is declared in advance as **counted removal #3**, with its measured justification published alongside the reason it was cut. Two capabilities each traced to a numbered failure is a stronger answer to *"which design choices helped the agent solve the problem?"* than three where the third was rushed. See `plan.md` ruling R-01.

**1. Tool — `cfr_resolve(title, part, section, as_of_date, quoted_text, designation)`**
Deterministic. **Designation-hierarchy resolution FIRST, quoted-anchor matching second.**
Returns `{found, level, designation_exists, siblings, char_offset}`.
*Fixes F1: B0 cannot check the anchor at all.*
*Ordering is forced by measurement:* 26/33 and 35/42 labelled items have **no extractable quoted anchor**, and NARA's dominant note mechanisms (`did-not-exist`, `already-exists`) are designation-**state** facts. A pure quoted-string matcher no-ops on ~80% of the pool.

**2. Skill — `SKILL.md`, the OFR execution procedure**
Parse each AMDPAR into `(operation, anchor, designation)` triples, in order; resolve each against the as-of text; check intra-rule interactions; only then rule. Also specifies the **note-emission contract**: name the designation, name the class, cite the offset.
*Fixes F2: given the tool, the agent checks the first anchor and rules from it. Both clean-item errors in the pilot were premature rulings on a partial read.*

**3. Memory — the ordered-state ledger — NOT BUILT (ruling R-01), shipped as a counted removal**
Carry `designation → state after each executed instruction` across the rule, so instruction *k+1* is read against the state instructions *1..k* left.
*Fixes F3: this is the actual OFR execution model.*
*Justified by measurement, not by the collision story:* **state-carry sensitivity** — instruction *k+1* reads the state instructions *1..k* left — fires on **833/1,984 = 42.0%** of items (also 31/82 on the pilot pool; two independent counts, **not** label-correlated — 16 defective / 15 executable). *This is a different measurement from the redesignation-collision rate in §10; the two are not comparable and were conflated in an earlier draft.*

**Cap is two built.** *"Purposeful choices matter more than the number of components"* — the PDF, verbatim. A third built capability is a spec change requiring an architect ruling that supersedes R-01.

---

## 7. Metrics

### Primary — execution-prediction accuracy
Fraction of exact-instruction-count-matched `(rule, section)` items where the emitted `verdict` equals whether NARA published a live editorial note for that section.
**Scorer:** stdlib only, no model, no network, string equality against a NARA-authored fact.
**Do not change this metric.** It is pre-registered, piloted, and the only metric in the packet whose trivial-attack surface has been measured (`n_instructions` pinned at 0.5000; best of 26 features 0.5934 inside its own null at p = 0.185). Every rival that changed its primary died to the first script someone wrote.

### Secondary — reported beside, **never blended**
1. **Defect-localisation accuracy** on NARA's localised subset (~13.6% of notes). A constant scores **0.000**.
2. **Failure-class recall** against NARA's five-way vocabulary on the mechanism subset (~22.7%). A constant scores **0.000**.
3. **Instruction-level resolution-claim correctness** against a deterministic oracle — *is this string / designation present in the point-in-time text?* Computable, zero authored labels, ~1,000 records. **DIAGNOSTIC ONLY, never the primary** — a script scores 1.0 on it because it *is* the script. Its purpose is statistical power for the per-capability ablations.

### Guards — pre-registered numbers
| Guard | Threshold |
|---|---|
| False-defect rate (called WILL_FAIL on an executable section) | ≤ 0.25 |
| Missed-defect rate | ≤ 0.25 |
| **Attributor completeness** | **≥ 0.90 — blocks any headline number** |

### Success — committed to `GOOD.md` before A1 exists
**A1 ≥ B0-agent + 8 pp, McNemar p < 0.05, at n ≥ 84, and A1 ≥ 0.80 absolute.**
Predictions written before the run: B0 ≈ 0.50 · B0-agent ≈ 0.75 · A1 ≈ 0.85.
**Do not chase 1.00.** A saturating metric reads as a rigged baseline.

---

## 8. The corpus

### Operational constraint — binding
**`www.ecfr.gov` and `www.federalregister.gov` return HTTP 403 from this machine.** Verified 2026-08-30 02:17 UTC; they worked nine hours earlier. Sustained automated traffic got us blocked. **Do not build on them. Do not attempt to work around it.**

**`www.govinfo.gov` returns 200, needs no key, and is the sole harvest channel.**

| Source | URL | Provides |
|---|---|---|
| ECFR bulk XML | `https://www.govinfo.gov/bulkdata/ECFR` | `<EDNOTE>` elements — **the labels** |
| CFR annual editions | `https://www.govinfo.gov/bulkdata/CFR` | point-in-time section text (back to 1996) |
| FR bulk | `https://www.govinfo.gov/bulkdata/FR` | `<AMDPAR>` elements — **the instructions** |

### Labels
Extract `<EDNOTE>` structurally; filter to codification-defect notes containing `"could not be incorporated"`.
Reference measurements from 9 titles (12, 20, 21, 24, 26, 40, 42, 45, 49) — sanity-check against these, do not substitute them:

| Measure | Value |
|---|---|
| Total EDNOTEs | 903 |
| Codification-defect notes | 44 |
| Carry their own FR citation | **44/44** — FR resolution is deterministic, no search step |
| Section-level | 38/44 |
| Localise below section level | 6/44 (13.6%) |
| State an explicit mechanism | 10/44 (22.7%) |

### MEASURED at CH-01 — this supersedes the projection that was here

| | |
|---|---|
| Corpus | **49 titles, 824,289,052 B** (not ~2.3 GB / 50 — title 35 is reserved and has no govinfo folder) |
| `<EDNOTE>` extracted | **2,428** |
| Codification-defect notes | **107** (4.4% of EDNOTEs) |
| … section-level | **86** |
| … **with a resolvable FR citation** | **85 — the pool gate number. ≥ 60 required. CLEARS at 1.42×.** |
| Distinct FR documents | **78** — this bounds the count-matched pair yield |
| Spread | 25 titles |

**Three corrections to this file's own earlier text, each measured rather than argued:**

1. **The "150–250" projection was wrong — the real figure is 107.** The nine reference titles are the *largest*: 408 MB of 824 MB (50% of the corpus by bytes, 18% by title count). Extrapolating per-title from them overshot by **2.28×**.
2. **The claim that the eCFR search API's 92 "undercounts by ~2.3×" was false.** Measured govinfo:eCFR = **1.16×**. 92 was close to the truth; the range built to discredit it carried the error. Both figures are published; neither is quoted alone.
3. **"Section-level" has two readings and they differ by 2.** Notes that *name* a section = 38 on the reference set; notes that *sit inside* one = 36. **The gate uses the smaller.** Both ship.

*The 9-title reference reproduces exactly on today's bytes — 903 EDNOTEs, 44 defect, 44 carrying an FR citation — from a parser written without sight of those numbers.*

### AMDPAR attribution — the algorithm, specified here so a reviewer can reimplement it

`PROCESS.md` §6 requires a gated chunk's reviewer to **reimplement the load-bearing logic from this file alone, importing nothing from the project.** CH-02's logic was described only in `plan.md`'s card, which a reviewer is not told to reimplement from — so its FULL gate could not have caught a defect in it. That is the identical failure that let the leakage defect through. Specified here instead.

**The problem.** A Federal Register final rule contains `<AMDPAR>` elements — amendatory instructions. Only some name their section; the rest are lettered sub-instructions belonging to the last-named one:

```
6. Amend § 1468.23 as follows:          <- names the section
   a. Revise paragraph (b)(2);          <- belongs to 1468.23
   b. Remove paragraph (c).             <- belongs to 1468.23
7. Amend § 1468.25 by ...               <- names a new section
```

**Measured:** only ~42% of AMDPARs name a section. An extractor that reads lead-ins alone attributes 42% and silently drops the rest — which is exactly how a predecessor pilot reported 0.46 completeness and poisoned its own eval set.

**The algorithm — carry-forward:**
1. Iterate `<AMDPAR>` elements in **document order**. Order is the whole mechanism; any reordering breaks it.
2. Maintain `current_section`, initially null. **Reset `current_section` to null at every `<REGTEXT>` part boundary** — an instruction cannot inherit a section from a different CFR part. *(v1.1)*
3. If the element names a section in its own text, set `current_section` to it and attribute the element there. **A section is named in either of two forms and both count** *(v1.1)*:
   - the **sign form** — `§\s*[\d.]+[a-z]?`, as in *“§ 1.907 is amended”*;
   - the **word form** — `Section` or `Sections` followed by the number, as in *“Section 1.907 is amended by revising…”*. **The word form is matched CASE-SENSITIVELY: `Section`, never `section`.**
4. Otherwise attribute the element to `current_section`. If `current_section` is null, the element is **unattributable** — count it, never guess.
5. Parse each attributed element into `(operation, anchor, designation)` where `operation` is one of `revise · add · remove · redesignate · amend`, `anchor` is the quoted text if present, `designation` is the paragraph path such as `(b)(4)(i)(A)`.

> **Why the word form is in the detector — and the reason is not the number** *(v1.1; `QUESTIONS.md` Q9, ruled at Q11).* The sign-only detector of v1.0 does not merely under-detect, it **mis-attributes**: an element not recognised as naming a section inherits the previous one, so a miss produces a confident wrong answer rather than a gap. Measured over all 70 FR documents / 8,752 elements: under the sign-only reading **ten documents attribute NOTHING — 1,910 elements**, among them two of the five largest rules in the corpus (`2014-08744` at 838 elements, `2021-22144` at 649), because FAR-family rules write *“Section 52.204-8 is amended”* without the sign. On golden G1 (FR Doc 2020-11897) CH-02 measured **20 of 28 elements pinned to a section they do not amend**. **This correction is adopted because it is justified independently of its effect on any number** — a detector that leaves 1,910 elements attributed to nothing is wrong at any completeness figure. Evidence: `docs/evidence/spec-fix-1/recomputed.md`.

> **Case-sensitivity is part of the specification, not an implementation choice** *(v1.1; `QUESTIONS.md` Q12(c)).* CH-02's shipped detector was case-**in**sensitive, and it therefore read appendix-internal numbering as CFR sections: of 684 elements whose only word-form citation is lowercase, **683** were treated as naming a section and **44 of those carry `part_mismatch`** — *“Appendix A to part 75 is amended by revising the title of section 1.1”* pins `current_section` to `1.1` inside a part-75 `<REGTEXT>`. **Every 0.9865 figure in this repository is the case-INsensitive one and is therefore an over-count.** The case-sensitive figure is **not yet measured** — SPEC-FIX-2 changed the specification and deliberately re-ran nothing; measuring it belongs to CH-03. No number here has been restated to match this rule.

> **The part-boundary reset is adopted although it makes the number worse** *(v1.1; `QUESTIONS.md` Q10 and Q12(a), ruled at Q11).* It costs **8.0 points** — attribution 0.9865 → 0.9066, both endpoints measured under the case-**in**sensitive detector CH-02 shipped, so the cost under the case-sensitive rule specified above is itself unmeasured and is expected to differ. CH-02 identified **699 of 8,752** elements attributed to a section whose part differs from the part of the `<REGTEXT>` containing them, and called the reset *“a one-line change and would be an improvement”*; the correction proposed at SPEC-FIX-1 adopted the +22.5-point word-form fix and never mentioned this one. **It is in this file for precisely that reason: if the fix that helps is adopted, the fix that hurts is adopted in the same edit — or the ruling is made with the scoreboard visible.**

> **The 699 is not all attributor error and must not be quoted as though it were** *(Q12(a)).* **126** of those elements **name their own section correctly in their own text** — the `REGTEXT/@PART` tag is the thing that disagrees — so they are evidence of a separate and previously unlogged `regtext_part` extraction defect, not of mis-attribution. The figure for genuine carry-forward part mismatches is **573**. Both numbers ship; neither is quoted alone.

**Completeness — the definition the gate asserts on:**

> **completeness = (number of AMDPAR elements attributed to a section AND parsed into at least one complete `(operation, anchor OR designation)` triple) ÷ (total AMDPAR elements in the document)**

Reported **globally** and **per FR document**; the per-document figure is what CH-02's pre-registered fallback restricts on. An element attributed but unparsed counts as **incomplete**, not complete — attribution alone is not the bar.

#### THE GATE FAILED, AND THE FAILURE IS PUBLISHED — it was not fixed *(v1.1)*

**The attributor gate FAILED.** CH-02 measured global completeness at **0.5080** under this file's v1.0 sign-only detector and **0.6643** under an extended one. The gate required **0.90**. CH-02 therefore sits in its pre-registered *“< 0.80 — documented failure”* branch, and the failure is **published in the README, not absorbed**.

**Attribution alone measured 0.7613 / 0.9865 — and that figure was tested and REJECTED as a gate.** A control attributor identical to the shipped one but for a single line — it carries the *first*-named section of a document forward instead of the *last* — places **6,395 of 6,663** attributed elements on a **different** section and scores **the identical 0.7613**, to six decimal places. `attributed ÷ total` therefore cannot distinguish a correct attributor from a 96%-wrong one, and cannot be this gate. Stated fairly, it is **not** vacuous: it does catch the silent-**drop** mode that reported 0.46 and poisoned a predecessor pilot's eval set — a lead-ins-only extractor scores **0.2503**. It is blind to the silent-**wrong** mode, which is the mode this corpus actually exhibits. Evidence, control script included: `docs/evidence/spec-fix-1/`.

**The definition was NOT rewritten after it failed.** A correction to it was proposed by the architect, put to an independent session that was authorised to refuse, and **refused** — `docs/evidence/spec-fix-1/verdict.md`. The architect accepted the refusal in full; the ruling is `QUESTIONS.md` Q11. The threshold is unmoved, the definition above is unaltered, no replacement metric was introduced, and **no number in this repository was changed by that ruling or by the v1.1 edits it authorised.**

**Known, counted, and deliberately unfixed** (`QUESTIONS.md` Q10; total recovery **< 0.31 percentage points**): the `46 CFR 356.3` citation form, which names neither a sign nor the word *Section* (9 elements, and it is why one document in the corpus is unattributable in full); and table-driven amendments — *“For each section and paragraph indicated in the left column of the following table…”* — whose sections live inside a `<GPOTABLE>` and never appear in the AMDPAR text (26 elements). Both were found **after** the measurement, and the pre-registered tokenisation rules forbid revising a rule once the number is in view. They stay recorded and unfixed for that reason, not because they are cheap.

### Leakage strips — mandatory, counted, and published

**The label and the input come from the same XML tree.** Measured on a real govinfo annual-edition volume (`CFR-2024-title40-vol5`, 5,524,321 B): of 28 `<EDNOTE>` elements, **26 sit inside a `<SECTION>` block**; both `<EFFDNOTP>` elements do; 252 of 255 `<CITA>` elements do. `<EDNOTE>` is where the gold label lives.

`<EFFDNOTP>` prints amendments pending at compile time **verbatim**. One observed block names the FR citation, the section, every designation touched, and then says *"For the convenience of the user, the revised and added text is set forth as follows."*

**Therefore, before any section text is frozen or shown to any arm, strip and count:**

| Element | Why |
|---|---|
| `<EDNOTE>` | carries the editorial note that **is** the label |
| `<EFFDNOTP>` | prints the pending amendment — the rule under test — verbatim |
| `<CITA>` | source credit naming the amending rule |
| `<EAR>` | editorial amendment record |

Per-element strip counts go in the freeze manifest **and** in the README as a named design decision. The stripper is pure (hard rule 8) and lives in shipped code, so `refetch.py` reproduces the stripped corpus byte-for-byte and the manifest verifies from a clean clone.

**Honest bounding.** The as-of edition is chosen at (effective year − 1), so the note for the rule under test normally lands in the *next* edition — the leak is not guaranteed per item. It fires anyway in three non-hypothetical ways: off-by-one edition selection for any mid-year effective date; `<EFFDNOTP>`, which by design prints the pending rule; and prior `<EDNOTE>`s on the same section, which are label-correlated even when the specific note is absent. **Structural containment is measured; the per-item rate is UNKNOWN and measuring it is part of the fix.**

**Why this is gate-class: it fails silently and in the flattering direction.** Accuracy goes *up*. Every guard in §7 still passes. `GOOD.md`'s thresholds are cleared. And a FULL adversarial review of CH-03 could not have caught it, because this file — the only document the reviewer reimplements from — did not mention it. It was lost in transcription from `08-FINAL-CALL.md` §5.

*(The eCFR "Link to an amendment published at NN FR …" annotation needs no strip: it is an eCFR artifact and appears 0 times in the govinfo annual editions, which are our only source.)*

> ⚠️ **ELEMENT NAMES ARE FORMAT-DEPENDENT — raised at CH-01 (Q8), and it bites at CH-03.**
> The leakage containment above (26/28 `<EDNOTE>` inside `<SECTION>`) was measured on a **CFR annual-edition** file. **ECFR bulk XML has no `<SECTION>` element at all** — it uses `DIV8 TYPE="SECTION"` (title 7: 17,205 `DIV8`, 548 `DIV5 TYPE="PART"`, 144 `DIV9 TYPE="APPENDIX"`, **zero** `<SECTION>`). Both descriptions are correct for their own format; neither spec file said which format it meant.
> **Consequence, binding on CH-03:** a strip counter that reports **zero** may simply be looking for the wrong element name. **Every strip counter must be asserted against a known-positive input before any zero it prints is believed.** A silent zero here is the leakage defect returning by a different door.

### Eval set
- **Positives:** `(rule, section)` pairs carrying a live codification-defect note.
- **Negatives:** sibling sections amended by the same rule with no note, **matched EXACTLY on instruction count.** Non-negotiable — unmatched, a hardcoded threshold on instruction count beats the agent, and that is precisely how an earlier candidate died.
- Publish the **full exclusion ladder** with counts at every step.
- **Target ≥ 42 pairs (n ≥ 84).** Report the real number.

### Freeze
Everything under `data/` with a SHA-256 manifest and `refetch.py`. `.gitattributes` = `* -text` on line one. Sealed read-only after CH-03.

### Licence — clean, and the only candidate with no caveat
All three sources are OFR/GPO properties, **public domain under 17 U.S.C. §105**. eCFR does not contain standards incorporated by reference, so the ASTM/NFPA copyright problem does not touch the corpus.

---

## 9. The hard case

**The defect that is not the first instruction** — a section where instructions 1..k−1 all execute and instruction k fails, so a partial read rules correctly for the wrong reason. **Measured n = 16 defective items in the 82-item pilot pool.**

Three verified NARA-authored exemplars, ascending in sharpness:
1. **12 CFR 702.2** — revising a definition that *did not exist*. Target named, not quoted — only the widened tool form catches it.
2. **26 CFR 1.199A-0** — adding an entry that *already exists*. The pure designation-state check.
3. **12 CFR 702.504 → 702.304** — revising a citation, after redesignation, that did not exist in the section. The collision case, honestly counted, kept as the sharpest single instance and **named as rare**.

Unresolved cases route to a named human checkpoint with both readings and the paragraph trace. This satisfies ground rules 04 and 05 concretely.

---

## 10. Removed experiments — two, both planned

**1. Current CFR text instead of point-in-time text.**
Pre-registered prediction, committed before it runs: **accuracy collapses toward a trivial oracle**, because after a failed amendment the current text still lacks the change and after a successful one it contains it — the current text *leaks the label*. **If the number goes up, that is proof of leakage, not capability, and must be reported as such.**

**2. The intra-rule collision detector**, built on the ledger, **removed with its measured class size as the stated reason.** Measured five ways: 0/68 labelled items contain a redesignation instruction; 3/82 have any collision (2 positive); **redesignation-collision sensitivity** is **~1.3–3.1%** of corpus items (the pilot reported 26/1,984 = 1.31%; an independent naive recount returned 61/1,984 = 3.07%. **The figure does not reproduce and is therefore provisional — CH-09 recomputes it in-repo and publishes whichever number the shipped script yields, with the discrepancy stated.** Either value supports the removal decision; neither is quoted as settled), and 15 of those 26 are *correct drafting*; **NARA never publishes a note naming an intra-rule conflict** — live probe for `"conflicting amendments"` returned 0.
A removed capability with a **counted** hard-case class is worth more than a kept one with an uncounted class.

---

## 11. The hot take

> **A verification agent's grounding corpus is a precision instrument, not a recall instrument — and if you hand it the document, measure *which class* got better, because the average will lie to you.**

Measured across two corpora, not asserted:
- **IETF errata:** giving the agent the specification moved Rejected recall **+12.0 pp** and Verified recall **−4.0 pp** — net +4.0, statistically nothing (p = 0.64). In the three-class variant the same access moved the policy class **−16.7 pp** and made the arm *worse overall*.
- **Amendatory instructions:** giving the agent the CFR text moved accuracy **+27.3 pp**, because the baseline was at chance and the corpus supplies the only fact that decides the answer.

The difference is not the model and not corpus quality. It is whether the answer is **in** the document or merely **argued about** by it. Evidence tells you when a claim is false; it rarely tells you a claim is true, because the claim was written to look true.

**The transferable rule:** before building retrieval into an adjudication pipeline, measure the baseline's per-class recall. If the negative class is already strong, retrieval buys an average that flatters and a decision boundary that does not move.

Generalises without modification to fact-checking, code review, security triage, and RAG over any corpus of contested claims.

---

## 12. Prior art — cite, do not collide

- **Prior et al., NLLP@ACL 2025** — amendatory instruction execution as a task. Cite on the first screen. Our axis is *predicting failure before publication and localising it*, not executing the amendment.
- **`cfpb/regulations-parser`** — existing CFR amendment parser. Cite; we do not reimplement it as a contribution.
- **ATLAS, arXiv 2509.18400** — HTS classification from CROSS. Unrelated domain; listed because it killed a predecessor project and the lesson is recorded.

Not citing known prior art on a submission staked on integrity is an unforced error and is one search away for a judge.

---

## 13. Change log

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-08-30 03:20 UTC | Initial. Assembled from `08-FINAL-CALL.md` §5 over `07-KILL-TEST.md` §7. |
| v1.1 | 2026-08-31 | **§8, under the `QUESTIONS.md` Q11 ruling, which ACCEPTED IN FULL SPEC-FIX-1's refusal of the proposed metric.** (1) The failed gate is **recorded, not fixed** — 0.5080 / 0.6643 against 0.90, and `attributed ÷ total` named as tested and rejected because a 96%-wrong control attributor scores the identical 0.7613. The definition, the threshold and the metric are **unchanged**. (2) The section-citation detector now recognises the **word form** beside the sign form, matched **case-sensitively** (Q9, Q12(c)) — adopted because ten documents / 1,910 elements attribute to nothing without it, independently of any number. (3) `current_section` now **resets at a `<REGTEXT>` part boundary** (Q10, Q12(a)) — adopted **although it costs 8.0 points**, because the fix that helps and the fix that hurts are ruled on together. Nothing was re-run and no measurement moved. |
