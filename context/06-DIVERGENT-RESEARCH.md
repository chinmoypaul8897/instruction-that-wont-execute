# Divergent Idea Search — Results

> **Compiled:** 2026-08-29, ~10:00–17:00 UTC · **Method:** 18 isolated angle agents → hostile per-angle kill → real data verification → resurrection attempts → completeness critics.
> **Evidence key:** **VERIFIED** = I or a named agent fetched it (URL + what was seen) · **INFERRED** = reasoning · **UNKNOWN** = looked, failed.
> **Independence:** `context/03-IDEA-REVIEW-VERDICT.md`, `03b-review-raw.json`, `05-FINAL-DECISION.md` and `05b-tournament-raw.json` were **never opened** — by me or by any of the 57 agents. Every agent was given an explicit prohibition and none reported a breach.

---

## 1. How this was run

**Scale.** 57 agents, ~1,845 tool calls, ~4.9M subagent tokens, across four stages.

| Stage | What ran | Agents | Result |
|---|---|---|---|
| 1 — Diverge | 18 angle agents (A–R), fully isolated, each told to research real corpora rather than brainstorm | 18 | **143 raw candidates**, 0 agent failures |
| 2 — Fast kill | One hostile killer per angle, applying the 12 hard filters and running the trivial-solution test | 18 | **141 killed (98.6%)**, 1 survivor, 1 skipped |
| 3 — Verify | Per-survivor data verification, prior art, live census | 1 | died on a session limit; I did the verification myself instead |
| 4 — Adjudicate / Resurrect / Critique | Final adjudication, 12 resurrection attempts, 3 completeness critics | 9 | last survivor **killed**, skipped candidate **killed**, **2 resurrected only after redesign** |

**Kill counts.** 143 generated → 141 killed in the hostile round → the 1 remaining survivor (`CROSS-Examined`) killed by me → the 1 skipped candidate (`Citation Rot`) killed on adjudication. **As generated, all 143 died.** Two were then resurrected in redesigned form (§2).

**Cause of death, all 141 stage-2 kills:**

| Filter | Count | Share |
|---|---|---|
| **4 — trivial solution** | **94** | 67% |
| 2 — data not public/freezable | 18 | 13% |
| 1 — LLM in the scoring path | 9 | 6% |
| 5 — no headroom | 7 | 5% |
| 3 — <10 cases in 6h | 5 | 4% |
| 10 — needs the contestant's own expert judgement | 3 | 2% |
| 12, 6, 7, other | 5 | 4% |

**What I verified personally** (not delegated):
- The CBP CROSS API, end to end — 577 revocation hits, structured `revokes`/`revokedBy`, full ruling text; and five gold labels checked against the HQ holding text.
- **Six blind one-prompt baseline runs** on 11 real customs cases, plus **three** on facts-only input, plus **three** on 12 balanced RFC errata cases — 12 blind runs total, all scored by my own scorer.
- **The 20-line script that killed the last survivor** (11/11 = 100.0%), and its no-ID variant (45.5%).
- **The errata lookup attack** (12/12 = 100.0%, twice — with and without the record ID).
- A 61-URL reachability sweep (49 reachable), with real record counts pulled from 13 of them.
- The ATLAS prior-art paper, via the arXiv API.
- The GitHub competitor census.

**Stage 3b census — the field, live, at 2026-08-29 ~10:00 UTC (VERIFIED, my own `gh` queries):**
- **75** micro1-specific public repos created since 2026-08-27 — **up from the strategy brief's 64** at 06:57 UTC the same morning.
- **38 of the 75 (51%) have no description at all.** Lane occupancy is therefore systematically under-observed, and *"zero competitors in this lane"* is much weaker evidence than the brief's phrasing implies. I flag this because several §2.1 property-5 claims rest on it.
- Concept probes still returning **zero** repos since kickoff: abstention, CVE/CVSS, customs/HS classification, airworthiness directives, port state control, retractions, welding, electrical code, glossary consistency, crosswalk mapping, Federal Register, superseded guidance.

---

## 2. The survivors — ranked

**Nothing survived as generated.** Two candidates were resurrected only after a structural redesign, and both survive on the *same* narrow escape: the corpus is frozen offline **without** the answer documents. Both are ranked below with their residuals stated in full, because both residuals are serious.

### Rank 1 — Erratum Gate (redesigned) · angle D, Negative-space/adversarial

**What it is.** An agent triages the IETF's real RFC errata backlog. For each submitted claim that an RFC contains a technical error, it must rule **Verified** or **Rejected**, reading the actual RFC text to decide. Scored on a penalised-guessing Net Trust Score.

**Intended user.** The IETF Area Director or RFC Production Center editor working the errata queue before a biweekly IESG telechat. **VERIFIED: 728 errata sit unadjudicated** in "Reported" status right now.

**Ground truth.** The named IETF verifier for each erratum — an Area Director or stream approver acting under the IESG errata process. Every record carries `verifier_name` and a date. **The contestant authors nothing.**

**Corpus.** `https://www.rfc-editor.org/errata.json` — **VERIFIED: HTTP 200, 11,640,398 bytes, 8,021 records.** Verified 3,722 / Held-for-Document-Update 2,414 / Rejected 1,157 / Reported 728. One file; the cleanest offline freeze of anything in this search.

**Primary metric.** Net Trust Score on a balanced Verified/Rejected set; scorer is string equality against `errata_status_code`. No model anywhere in the scoring path.

**The redesign that saved it** — three changes, each structural rather than a patch:
1. **Delete the `notes` field entirely.** It is adjudicator-written, i.e. part of the label. The original kill was a regex on `/verifier'?s?\s*(notes?|comment)/i` scoring **96.66%**. Deleting a named field is not a scrub — there is no marker variant to miss.
2. **Pair within each (doc-id, verifier_name) cell**, so every RFC and every Area Director contributes equal Verified and Rejected counts. This makes the doc-id lookup and the verifier-name lookup — the shortcut that scored 49.8% and killed angle H's version — **exactly 50.0% by construction**.
3. **Ship `errata.json` with statuses stripped**; the scorer holds the labels.

**Measured attack surface after redesign** (420 cases, 210/210, across 149 cells — all numbers from the resurrection agent's own scripts):

| Attack | Score |
|---|---|
| Constant / majority class | 0.5000 |
| doc-id lookup, in-sample **oracle** | 0.5000 |
| verifier-name lookup, in-sample **oracle** | 0.5000 |
| (doc, verifier) lookup, **oracle** | 0.5000 |
| Best length threshold, **tuned on the test set** | 0.5905 |
| TF-IDF + LogReg, 5-fold CV | 0.4690 |
| CountVec + MultinomialNB, 5-fold | 0.4381 |
| "correct_text appears in the successor RFC → Verified" (231 successor RFCs downloaded) | 0.5250 |
| **One off-the-shelf model, one prompt, no tools** | **0.5833** |
| **Same model reading the frozen RFC corpus** | **0.7857** |

**Against the six properties:** 1 ✅ labels 100% IETF-authored and dated · 2 ✅ string equality, no model · 3 ⚠️ shortcuts are 50% *by construction*, which is the right kind of foreclosure, but see residual 1 · 4 ❌ **licence UNKNOWN** · 5 ✅ 0 of 75 repos, though 51% have no description · 6 ✅ the baseline fails because it cannot check the spec, and reading the RFC is what fixes it.

**Strongest argument for it.** The shortcut table above is the best in this entire search: four separate lookups pinned at exactly 0.5000 by construction, and two trained classifiers *below* chance — the pairing removed the confounds rather than hiding them. The 0.583 → 0.786 jump is caused by the agent actually reading the specification, and the three flips were diagnosable: RFC 2328 Table 6 (the proposed change contradicts surrounding prose), RFC 5905 §8 (the formula as printed is correct), RFC 7230 §3.2.6 (curly quotes are a PDF artefact).

**Strongest argument against it.** **The gap is not statistically real yet.** 0.786 vs 0.583 is Fisher two-sided **p = 0.29**, and the one-prompt baseline is not distinguishable from chance (binomial p = 0.54). *Nothing here is pre-registerable until it is re-run at n = 60–100.* A direction was measured, not a gap. Second, the escape is **(c) and only (c)**: `orig_text` is a verbatim RFC quotation, so anyone with a network connection scores **100%** — I verified this myself, 12/12, twice. The benchmark is honest only because the shipped corpus withholds the labels, and an eval-lab judge will say that out loud. Third, the licence is **UNKNOWN**: `rfc-editor.org/copyright/` is **404** and the IETF Trust Legal Provisions defers to TLP 5.0 / RFC 5378 with no SPDX identifier. Fourth, 35 of 420 cases (8.3%) have degenerate `correct_text` ("[see Notes]", "???") that becomes unanswerable once `notes` is deleted.

**What would have to be true for it to win first prize.** The n=60–100 re-run would have to hold the gap at p < 0.05; the licence question would have to resolve cleanly on reading TLP 5.0; and the "you banned the lookup to save the benchmark" objection would have to be answered *in the README, pre-emptively and in the judge's own vocabulary* — the answer being that an Area Director's job is to read the spec, not to look up their own future ruling.

### Rank 2 — The Instruction That Won't Execute (redesigned) · angle M, Constructed ground truth

**What it is.** An agent reads a US federal final rule's amendatory instructions plus the CFR text as it stood on the publication date, and predicts whether the Office of the Federal Register will be able to **execute** that instruction — or will have to publish an editorial note saying it could not.

**Intended user.** A regulations drafter or OFR liaison clearing a final rule under a statutory or court-ordered deadline. A defective instruction means the rule does not codify.

**Ground truth.** The Office of the Federal Register — the statutory codifier. The editorial note is NARA's, dated, and names a section and an FR citation.

**The redesign.** Freeze ships the FR rule XML plus the eCFR section text at publication date **with every `<EDNOTE>` stripped**, and ships **no** post-effective-date snapshot. The unit of prediction moves from *instruction* to *(rule, section)* pair, because NARA's note names a section and a citation, never an instruction index — so no derivation rule has to be authored. Negatives are sibling sections amended by the same rule, matched on instruction count.

**Why the freeze is legitimate here** (this is the sharper argument of the two): the withheld artefacts — the editorial note, and the codified text after the effective date — **do not exist at prediction time in the real world either.** The drafter decides before OFR codifies. Withholding them restores the real information set rather than banning the agent's contribution.

**Measured, on a 53-case count-matched set (27 defective / 26 executable):**

| Attack | Score |
|---|---|
| Constant / majority class | 0.5000 |
| **Best hardcoded single feature** (`n_instructions >= 5`) | **0.5876** |
| Best deterministic retrieval script (~150 lines, anchor extraction + CFR paragraph hierarchy) | 0.5855 |
| The attack that scored **1.000** in the original kill | **0.5855** |

Harvest was fully mechanical: eCFR search `total_count` 640 → 169 unique sections → only **50** still carry a live EDNOTE → 39 resolve to an FR document. A 2-line mechanical cross-check rejected **6 of 39 (15.4%)** wrong-document resolutions, all confirmed wrong by inspection. **The contestant authors zero labels.**

**Against the six properties:** 1 ✅ NARA-authored, dated · 2 ✅ deterministic · 3 ⚠️ see the residual below — this is the weak one · 4 ✅ **US federal, edict of government, zero licence ambiguity** · 5 ✅ zero competitors · 6 ✅ the blindness is structural resolution of anchors against deeply nested text.

**Strongest argument for it.** It is the only surviving candidate with a **clean licence** and a genuinely novel user. It converts the original 1.000 attack down to 0.5855 — a real, measured foreclosure. And the failure mode is legible on video: an instruction that says "remove 'X'" where X is not there.

**Strongest argument against it — and it is close to fatal.** **The best hardcoded constant (0.5876) still beats the best retrieval script (0.5855).** A section receiving many instructions is genuinely likelier to carry a defect (defective mean 4.93 instructions vs executable 3.85). The resurrection matched nearest-available, not exactly. **Unless the contestant matches exactly on instruction count and pre-registers that matching as published code, a hardcoded constant beats the agent and this dies the same death as the CNA-severity candidate.** Second, the pool is 27 defective cases — it clears the ≥10 floor with no slack. Third, headroom above ~0.59 is **asserted, not demonstrated**: nobody has shown an agent clears the script.

**What would have to be true for it to win first prize.** Exact instruction-count matching, pre-registered as code, before anything is run. Then an agent would have to demonstrably clear 0.59 — and if it lands at 0.65, the improvement is thin and noisy on n=53.

---

## 3. The kill list

141 candidates from the hostile round, grouped by angle, one line each with the filter it failed and why. Plus the two adjudicated later.

**Killed at adjudication (stage 4):**

- **CROSS-Examined** *(A, the last survivor)* — **F4 + F7.** A 20-line script with no model scored **11/11 = 100.0%**: search the ruling number, read `revokedBy`, fetch the revoking ruling, regex `TARIFF NO:`. An independent agent reproduced this from scratch on its own fresh sample. Separately and fatally, **ATLAS (arXiv 2509.18400, 2025-09-22)** is already *"the first benchmark for HTS code classification, derived from CROSS"*, reporting 57.5% at 6-digit.
- **Citation Rot** *(L)* — **F4.** Two constants — `AMENDED_SINCE if guidance_date < 2016-12-19 else CURRENT` — scored **66/67 = 98.5%** across three real FDA guidance documents, because federal rulemaking arrives in waves. Also: the candidate's own scorer *is* the trivial solution, line for line. And its declared hard case does not exist in nature — a 1,966-section census across four CFR titles found **1** instance at ~0.05%, whose "new" heading was the literal string `xxx`. OFR's `[Reserved]` convention forecloses it by design.

---

### The 141 killed in the hostile round

### Angle A — Data-first  (7 killed)

- **Second Opinion on Severity** — *F4* — Two hardcoded constants beat it: 'take the CNA vector and force C:H/I:H/A:H' is one line of Python scoring 47.1%, and the disagreement is one CNA's house style (cna@vuldb.com, 188 of 255 pairs) rather than a reasoning gap. There i…
- **The Replay Centre Disagrees** — *F4* — Textbook label leakage: the L2M `comments` field is written by the reviewer AFTER reaching the verdict, so a 20-line naive Bayes over it hits 84.2% and the task is extraction, not judgement. Strip the comment and it collapses to a…
- **Conference Room** — *F12* — The MSHA Violations dataset ships no narrative or condition-description field at all, so there is literally nothing for a language agent to reason over - it is a seven-feature tabular classification with a 73.4% majority class. Th…
- **Where the Raters Split** — *F4* — I downloaded DICES-990 (50.4MB, 72,103 rater rows, 990 items) and a 20-line naive Bayes over the raw conversation text - no model, no API, no agent - scores 69-73% balanced accuracy on held-out data, against the candidate's claime…
- **Exempt Until Proven Otherwise** — *F2* — I re-probed ico.org.uk myself: the 364KB decision-notices page contains zero 'IC-' case references, zero PDF links, zero per-notice hrefs and no API/JSON/search endpoint of any kind - one occurrence of 'Upheld' and it is filter vo…
- **Allowed on Appeal** — *F2* — The only OGL-licensed structured route is a SPARQL endpoint whose portal 403s, the CKAN package lists no CSV or JSON resource, and the reasoning inputs are per-case PDFs behind a search UI - so zero structured records exist to bui…
- **Ex Parte** — *F2* — The free PTAB API returns the Open Data Portal SPA HTML shell rather than JSON and appears retired behind a keyed portal, so zero decision records exist; even granted access, each case needs a rejection plus a full claim set plus …

### Angle B — Statute-and-regulation-first  (8 killed)

- **RAD Gate** — *F4* — The lookup attack the generating agent explicitly flagged as UNTESTED is the one that kills it: a committee-memory table beats his best-tested constant by 2.5x on his own metric without ever opening the filing. Compounding it, hal…
- **Level Set** — *F4* — His 12.8% 'rescue' number is wrong by ~2.2x because he keyed the lookup on the wrong field; DOL publishes every input and every determination for ~1M cases per quarter, so the correct engineering answer is a lookup over DOL's own …
- **Revoked** — *F4* — The CROSS search index hands you the answer: every ruling record carries revokedBy/modifiedBy pointers and a tariffs string in the same JSON, so a link-follow beats any classifier. Retrieval, not judgement.
- **154(b)** — *F2* — The data is simply not reachable without credentials, so no eval set exists and no trivial attack can even be run. A judge cannot re-derive it from a bare clone.
- **Annex VI** — *F4* — The only reachable input source contains the answer, explicitly sourced to ECHA and the CLP Regulation, in the same record you would hand the agent. Strip it and the residue is a fifteen-line cut-off table lookup.
- **801** — *F4* — One hardcoded constant scores 90.9% on the only half that has labels, and the half that is actually hard has no per-trial regulator label at all — the contestant would have to author ACT determinations himself in a regulated domai…
- **SNC** — *F5* — EPA publishes the algorithm and the inputs arrive as typed numeric rows, so a correct sixty-line implementation of the Technical Review Criteria is the reference solution, not a baseline — there is nothing left for an agent to do.…
- **1904** — *F4* — The employer's question and OSHA's answer sit in the same document, so building the eval set means the contestant chooses where to cut — that is authoring ground truth by another name — and the corpus cannot even be enumerated ove…

### Angle C — Time-and-versioning-first  (8 killed)

- **Entry-Date Tariff** — *F4* — The candidate's own scorer defines truth as `new if entry_date >= bulletin_date + 60 days else old`, so a script implementing that identical formula scores 100% by construction — two hardcoded constants (CBP's structured `tariffs`…
- **Tolerance In Force** — *F4* — I wrote a 14-line script that reproduces the candidate's entire hard case and its whole 60-second demo, and the one claimed moat — resolving "bell pepper" to "Vegetable, fruiting, group 8-10" — is 40 CFR 180.41 Table 1, an officia…
- **Supersession Clock** — *F4* — One regex plus the Federal Register's structured `effective_on` field extracts the whole supersession graph, so "which AD is in force on date D" is a ~30-line script; the only rescue (compliance due dates from paragraph (h) clock-…
- **Existing Stocks Window** — *F4* — EPA's cancellation orders state the actor-by-actor answer in templated boilerplate sentences where the actor is the grammatical subject and the deadline is in the same clause, so a regex — never mind one off-the-shelf prompt — rea…
- **Exclusion At Date Of Service** — *F4* — A ~30-line join of UPDATED.csv against the monthly reinstatement CSVs is the complete solution and the generating agent said so itself; the only part a script cannot do — fuzzy provider entity resolution — has no external label au…
- **Retraction Currency** — *F4* — An inner join on OriginalPaperDOI plus one date comparison is not a baseline, it is the ceiling, and the generating agent killed this itself after downloading the 66 MB file; its own text admits "the blindness I would need to stat…
- **Recall Status Rewind** — *F4* — All four dates the answer depends on are structured fields inside the single JSON object the agent fetches, so a five-line date comparison is the complete solution, and a constant beats most of the metric anyway. The generating ag…
- **Vanished Guidance** — *F1* — There is no external label author: Wayback capture dates say when a crawler visited, not when the text changed, so the contestant himself must decide which version governed on each date — authored ground truth wearing a costume, a…

### Angle D — Negative-space / adversarial  (8 killed)

- **Erratum Gate** — *F4* — The adjudicator's own rationale is appended into the `notes` field the agent is given as input — 758 of 779 Rejected technical errata carry a `--VERIFIER NOTES--` / `Verifier's Note:` block, so the IETF's verdict leaks into the pr…
- **No Record At That Station** — *F4* — ghcnd-inventory.txt IS NOAA's published crosswalk of station x element x years, so "is this answerable" is a grep, not a judgement, and the candidate admits the naive design dies to a three-character regex at 93.8%. Its USC-only r…
- **Still Binding** — *F4* — CBP publishes revokedBy / modifiedBy / operationallyRevoked as structured booleans in the same search response that returns the tariffs, so the whole benchmark is a 20-line script: search, take top hit, read tariffs, and if revoke…
- **Cause Undetermined** — *F12* — One reading-comprehension call with no tools, no feedback and no course-correction on a rubric that weights agent engineering at 30 points, and the reason for the NTSB's abstention ("wreckage not recovered", "no witnesses", "destr…
- **The Number BLS Won't Print** — *F4* — BLS publishes the establishment count that drives its own suppression rule in the same row as the suppression flag, so one integer comparison against one constant reproduces the label. Dead on arrival by its own measurement.
- **Withdrawn Support** — *F6* — Retraction Watch IS the published retraction crosswalk, so the differentiating step is a three-line DOI set-membership test, and everything around it is the crowded generic-deep-research-agent-with-citations lane (25-40 competitor…
- **Does This AD Apply** — *F10* — The CANNOT_DETERMINE class — deciding that an AD's applicability paragraph conditions on something the FAA registry does not record — is a reading of compressed airworthiness prose that a non-A&P contestant would be making himself…
- **Not Established** — *F4* — The ground-truth phrase is a literal string in the document handed to the agent, so `'have not been established' in pediatric_use` is a one-line regex at essentially 100%, and the majority class alone is 65.2%. It also puts a non-…

### Angle E — Physical and field operations  (7 killed)

- **Revoked by Customs** — *F5* — I rebuilt the corpus live (3,422 HQ rulings, 1,683 with tariff+prior, 132 fully resolved pairs) and then ran the sanctioned baseline #1 myself: one direct prompt, product description only, code redacted, no tools, no HTS tree, no …
- **Cause Code 389** — *F10* — The ground truth is the regulated railroad's own filing, and the candidate's own pitch says that filing is systematically wrong — so the metric pays the agent to reproduce a scheduling clerk's habitual miscoding, and separating a …
- **Class I or Class II** — *F4* — A ~25-line Naive Bayes on reason_for_recall scores 73.7% on an honest event-level split against a 44.3% majority floor — the generator pre-registered a trivial ceiling of 58.1% and was wrong by 15 points. The corridor it claimed a…
- **Will Customs Come Back** — *F4* — I confirmed the time-leak the generator suspected: 1,290 of the 2,606 revoked/modified prior rulings carry pre-1997 all-numeric ruling numbers, so a regex on the ruling-number format alone separates half the positive class, and it…
- **Defining Event** — *F4* — Nobody — not the generator, not me — has ever seen a single labelled record, so every number in this candidate would be invention; and its structural twin (FRA cause codes) floors at 22–26% with a 25-line script on a dataset that …
- **Significant and Substantial** — *F4* — I fetched the MSHA field-definition file myself and confirmed there is no condition-or-practice narrative column, so the only non-leaking input is the cited 30 CFR part/section and a lookup of P(S&S | section) is the entire availa…
- **Which Standard Was Cited** — *F2* — I re-verified the DOL bulk catalogue independently: every OSHA table and snapshot date 301-redirects to the data.dol.gov homepage and serves an 11,015-byte Drupal page, so there is no corpus and no eval set.

### Angle F — Non-English / non-Western institutions  (8 killed)

- **Column Two** — *F5* — Its pre-registered thesis — a blind one-prompt model scores 0% and lands on the Commission's published rejected code — is falsified: I replicated the test and scored 50% at 8-digit exact match with zero tools and zero traps hit. E…
- **Heading Contested** — *F1* — Measured leakage: in T-313/25 the operative part names exactly one heading, 9021, which is also printed in the judgment's own title keyword line at character 219 and appears 50 times in the text — a regex that echoes the heading o…
- **In Force On** — *F4* — A constant 'no measure in force' clears 90% on any un-curated draw, and the only defence is the contestant hand-balancing the case set 50/50 — which is him authoring the case distribution, exactly what an eval lab would flag. The …
- **Set Aside** — *F4* — 'Predict whatever the AAR said' is a 20-line baseline that exploits the AAAR's uphold rate, a number nobody has measured and which is almost certainly 70%+, so the agent would likely lose to it outright. There is no consolidated r…
- **For: Read:** — *F5* — The corpus splits into a half a 20-line numeral-diff across the 24 language versions already wins (numerals are language-invariant) and a half no method can touch (one well-formed Hungarian name replaced by another), leaving no ba…
- **Risk Type** — *F4* — A one-word constant returning 'chemical' scores about 49% on the primary metric per the Commission's own published risk-type distribution, and the second half of the metric falls to a forty-row category-to-standard lookup table. O…
- **Content: Dry** — *F4* — Two constants keyed off one other column in the same CSV as the label score 58.3% exact match against a 31.3% majority class, and the label author also wrote the input text, so a regex over the wellbore history for 'dry'/'oil'/'ga…
- **Alias Graph** — *F1* — The EU publishes the alias groupings, so the only way to make this a prediction task is for the contestant to hand-write the probe names — he becomes the label author in all but name. And cross-script fuzzy name matching is a solv…

### Angle G — Micro-expertise  (8 killed)

- **Tail Number AD Board** — *F4* — The FAA publishes applicability *text*, never a per-tail determination, so every label is manufactured by the contestant's own join script — which means that script IS a 100%-scoring solution, and deciding an AD applies to a speci…
- **Squawk to JASC** — *F4* — A 25-line pure-stdlib Naive Bayes over the narrative and part fields scores 83.5% exact on the candidate's own pre-registered protocol — there is no headroom left for an agent, and no lookup of the JASC PDF is even needed.
- **Superseded Stack** — *F4* — A bare regex over paragraph (b) reconstructs the entire supersedure graph, so there is no residual reasoning to measure.
- **Hangar Clock** — *F1* — The contestant writes the synthetic logbooks AND the reference implementation that produces the answer key, so he is exam setter and answer key at once, and resolving ambiguous 'whichever occurs first / unless already done' langua…
- **Sustained or Dismissed** — *F4* — The dataset leaks its own verdict: certification_status carries the literal string 'N/A - DISMISSED', so a one-field lookup scores 85.2% on the exact 50/50 balanced set the candidate pre-registered. The agent never opened the othe…
- **Charge Sheet** — *F4* — The canned label text is the opening of the narrative, so this is extraction, not judgement, and a crude token-overlap script already beats the majority class by 3x.
- **Detainable** — *F2* — The only corpus carrying detention labels forbids storage and transmission outright, and the one public-domain alternative has no detention flag and no bulk export, so there is no case set to build.
- **Modified on Review** — *F4* — There is no narrative column in the public bulk file, so the input reduces to seven inspector-assigned structured fields and S&S is very largely a deterministic function of two of them (LIKELIHOOD, INJ_ILLNESS) — a tabular rule, w…

### Angle H — Failure archaeology  (8 killed)

- **Errata Court** — *F4* — A two-column lookup table keyed on the Area Director's name alone — reading not one word of the erratum or any RFC — scores 49.8% on the balanced 3-class set, beating every content-based shortcut and leaving only ~10 points to the…
- **Same Defect, Different Verdict** — *F5* — The discriminating evidence FDA actually used (firm complaint counts, distribution volume, internal toxicology) is not public, so there is no evidence the agent clears the 50% bag-of-words floor the generating agent already measur…
- **Root Cause, Not Symptom** — *F4* — CNAs write the description using the CWE's own published name and then assign that CWE, so this is extraction dressed as judgement; the 50/50 shortcut-right/shortcut-wrong rescue requires the contestant to hand-select cases agains…
- **Exploit Weather** — *F4* — The matched-pair design holds vendor and CVSS constant but does not hold constant the vendor's own machine-readable 'Exploitation Detected' flag, which is published on release day and is exactly the signal CISA later ratifies — a …
- **Why It Broke** — *F4* — A 20-line Naive Bayes gets 78.5% against a 25.0% majority class because the recall narrative states the root cause in the firm's own words, and the labels are firm-authored rather than regulator-authored, so even the ground-truth …
- **Retraction or Correction** — *F4* — A per-reason-token vote scores 82.9% because the Retraction Watch reason codes and the outcome are effectively the same variable, and the inputs are authored by Retraction Watch rather than by the publisher, so input and label sha…
- **Which Standard Did They Break** — *F2* — The data cannot be fetched at all, with the network ON, let alone frozen offline for a judge, and the untested bag-of-words shortcut almost certainly wins anyway because the narrative and the citation are written by the same compl…
- **Claims That Did Not Survive** — *F2* — Every USPTO and PatentsView endpoint returns a JS shell or fails outright, the claim-number gold list would have to be transcribed out of PDFs by the contestant (authored ground truth by the back door), and it lands in the crowded…

### Angle I — Economic  (8 killed)

- **Origin of Record** — *F4* — Its entire cheat-proofing claim is false: the 15/15 stratification forecloses exactly one heuristic and leaves two others untouched, so a three-line script beats the design's own by-construction floor by 18 points. Secondary: deci…
- **Duty at Risk** — *F7* — This is a re-run of a published 2025 benchmark built from the identical corpus, submitted to the one audience that would recognise it on sight. Its only claimed differentiator — the money metric — is beaten by a constant, by his m…
- **Broker's Refusal** — *F4* — A zero-parameter constant — refuse every line — wins at every point of his own pre-registered fee sweep, not just below a threshold, and the only lever that could change that is a fee number he invented himself. The underlying cla…
- **Scope Watch** — *F3* — The load-bearing corpus was never retrieved by him or by me, and the reachable substitute cannot produce ten balanced cases with product descriptions. Where a Federal Register title does carry the verdict, a title regex is the who…
- **Penalty Reconstruction (MSHA)** — *F4* — The dataset publishes the penalty alongside every structured input to the deterministic formula that produces it and contains no narrative whatsoever, so a table join is the answer and there is nothing for an agent to investigate.
- **False Positive Burn-Down (OFAC)** — *F1* — OFAC authors the positives but nobody authors the negatives, so every hard case would be a pair the contestant invented — the exact thing the bar's first property forbids. The half that is externally labelled is the half classical…
- **Advance Ruling India** — *F2* — The corpus is unobtainable programmatically, the orders are scanned per-state PDFs with no API, and the licence is UNKNOWN — so a judge cannot run this from a bare clone with the network off. Dead on access before any design quest…
- **Two Customs Houses** — *F1* — The divergence stratum the entire eval rests on is defined by the contestant deciding that a CBP-ruled article and an EU BTI article are 'the same product' — an unlabelled adjudication no authority performs for him. And there is n…

### Angle J — Deterministic-verifier-first  (8 killed)

- **Landed Duty Exposure** — *F4* — On its own money metric a single hardcoded constant does nearly all the work, and the only document carrying the merchandise description states the answer in plain text. Solving the entire hard classification problem is worth ~11%…
- **Patent Term Adjustment Reconstruction** — *F2* — He never obtained one byte and neither did I; and by his own admission a 300-line rules engine beats the agent, so the solver equals the verifier.
- **Certified Count Reproduction** — *F4* — An off-the-shelf tabulator with pre-shipped AEC configs already reproduces these certified counts exactly, so the honest baseline is `git clone` and it wins.
- **Service-Preserving Feed Repair** — *F1* — He concedes no external body authors the correct repair, so the standard for a good fix is his own — and a 40-line stub-synthesiser scores near-max on the metric as written.
- **Amendment Application to Consolidated Text** — *F2* — I independently reproduced his data failure — legislation.gov.uk returns HTTP 202 with zero bytes — and he has no measurement in either direction on headroom for a task models are natively good at.
- **Reported Emissions Recomputation** — *F4* — EPA publishes the operands in the same table as the answer, so a ~200-line implementation of the Part 98 equations is both the solver and the scorer.
- **Public Domain Determination** — *PUBLISHED-LOOKUP* — The task reduces to a fuzzy join against a published, machine-readable renewal registry — which is a lookup table by definition — and the CRMS label column is 403 to any script.
- **Check-Digit Anchored Identifier Repair** — *F4* — A brute-force enumerate-and-checksum script recovers essentially every single-character corruption, so verification and generation are both easy and the agent adds nothing.

### Angle K — Consistency-across-a-series  (8 killed)

- **Consolidator** — *F4* — The Federal Register final rule prints the resulting text verbatim in the same XML the agent is given ("The additions and revision read as follows:"), and "in alphabetical order" is satisfied by sorted(); the task is parse-and-spl…
- **Compiled Statute** — *F4* — The candidate's own claim that "a perfect regex baseline caps out around 34% of INSTRUCTIONS" is wrong by a factor of ~2.6 — I measured 87.9%, because it filed "positional insert" (30.2%) under the hard bucket when it is the leaki…
- **Entity List Reconstructor** — *F4* — Two independent fatal wounds: the BIS rule prints the complete new entry tuple verbatim (country, name, aliases, address, licence requirement, licence review policy) so the content half is the same parse-and-splice script that bea…
- **Authority Control** — *F2* — I checked the hole the generating agent flagged and it is real: LoC MARC records here carry no $0 authority URI at all, and bulk download 403s — so the mention-to-authority mapping would be authored by the contestant, which is the…
- **Tag Continuity** — *F4* — I measured it on the real filing series and it is worse than the generating agent estimated: 'reuse whatever this filer used last quarter' scores 95.59%, so all headroom lives in three switch quarters across a decade that the cont…
- **RFC Lineage** — *F4* — Dead on the generating agent's own measurements: a constant 'obsoletes and updates nothing' is right for 7,426 of 9,834 documents (75.5%) and a plain body regex recovers a true relation in 52% of the positives, leaving no defensib…
- **Glossary Lock** — *F4* — An exact translation-memory splice is not a shortcut on half A, it is the definition of the correct answer, so a 20-line script sits at ceiling on the dominant half; and the substring scorer breaks on German compounding and Russia…
- **Serial Name Forms** — *F4* — A chapter-1 name table force-replaced through the rest of the book solves the consistency half outright, and any off-the-shelf model already renders Raskolnikov consistently because the name is in its training data; the fidelity h…

### Angle L — Multi-authority contradiction  (7 killed)

- **Residue Gate** — *F4* — Its central defensive claim — "a regex cannot bind value to tissue without positional reasoning" — is factually false, and I disproved it by writing the script: EUR-Lex serves a perfectly regular 7-column table where the MRL cell …
- **Superseded Mandate** — *F4* — The generating agent beat its own candidate with two curl calls and a regex and said so plainly, and never measured the IN_FORCE base rate that decides whether a constant also wins. The only escape route — moving the metric onto r…
- **Three Regulators One Monitor** — *F4* — A ten-line pandas script with zero domain knowledge reproduces EPA's own published statistic for 97.0% of 1,191 sites, leaving about three points of headroom on the flagship metric, and the EU and WHO forms are arithmetically simp…
- **Second Opinion** — *F4* — Textbook label leakage: NVD's own JSON record carries the NVD Primary and the CNA Secondary CVSS vectors as adjacent fields in the same document the agent is handed, so 'reconciling four authorities' is reading two neighbouring ke…
- **Four Lists One Person** — *F4* — The candidate splits into a half a one-line regex join solves (982 of 1,016 UN references match OFSI on the shared UN key) and a half with no external join key at all, and the second half would require the contestant to author the…
- **Tolerance Gap** — *F2* — Two of the three authorities were verified NOT to serve data to a script — the EU Pesticides Database API returns a 'Server temporarily unavailable' page on every endpoint, the Codex detail grid is JavaScript-loaded, and the EUR-L…
- **Five Verdicts One CAS** — *F4* — CAS number is a perfect exact join key requiring zero nomenclature resolution, so the whole task is a five-way dictionary join in about thirty lines — the exact opposite of the alignment difficulty the angle depends on. Compounded…

### Angle M — Constructed ground truth  (8 killed)

- **The Instruction That Won't Execute** — *F4* — I beat its pre-registered metric twice, at 1.000 balanced accuracy, on its own flagship 10-instruction set: once by grepping the answer key out of the live eCFR (NARA prints the editorial note verbatim inside the very section the …
- **Correction Pending** — *F4* — The Federal Register API itself machine-links every rule to its own corrections, so the label is a field on the input document, not a judgement; and the negative class label is 'nobody has noticed yet', which is not an authority s…
- **Before The Corrigendum** — *F4* — The corrigendum's CELEX id is a deterministic string function of the base act's CELEX id, and I fetched it: it quotes the exact wrong text, article and page. A ten-line script gets perfect precision and recall at any flag budget.
- **Codify It Yourself** — *F4* — The answer key is the identical public API endpoint with one date string changed — GET the eCFR snapshot after the effective date and return it verbatim for a guaranteed 100% exact match. This is the 'two hardcoded constants' fail…
- **One Error, Somewhere In This Spec** — *F4* — A per-RFC errata URL keyed on the input RFC number returns the erratum's orig_text verbatim, so a three-line fetch scores 100% on the primary metric; the 'exactly one error' oracle is also artificial and the no-error half is label…
- **Feed Surgeon** — *F2* — The BART developer terms 403'd so hard filter 2 is simply unmet, and by the author's own enumeration every corruption class except one falls to a sub-20-line script (range check, tz-from-coords, fuzzy id match) while another class…
- **Seeded Rot** — *F4* — Every injection class is beaten by 8-40 lines of pandas, the error taxonomy the labels depend on does not exist in free testable form, and the ground truth is entirely the contestant's own injection log with no external authority …
- **The Code Drifted From The Law** — *F10* — Deciding whether code faithfully implements a statute is a legal judgement the contestant is not qualified to make, and the 'labels' are volunteer contributors' metadata known to go stale, so the ground truth is wrong precisely in…

### Angle N — Aggregation and rollup  (7 killed)

- **Effectivity** — *F4* — A ~40-line script with no registry, no agent and no model scores 49.1% on its own primary metric, because the abstain half of the label is literally a regex over the applicability paragraph the agent is handed, and the count half …
- **Non-Contiguous** — *F4* — The generating agent measured its own death: a 25-line range expander over the real PyPI release list gets 81.3% exact set match on 572 Django affected-entries, leaving no headroom worth 26 hours. Feeding prose advisories instead …
- **Extra-Regio** — *F4* — One line of Python scores 100%, and so does the deliberately wrong one line — when a statistical authority publishes both the parts and the total it has already reconciled them, so there is nothing for an agent to do. The demo is …
- **Balancing Authority** — *F1* — EIA adjusts 0.00–0.02% of rows, so 'echo the input' scores ~99.98%, and the supposed ground truth fails its own accounting identity on 35% of adjusted rows. No authority ever states which balancing authority was right, so the exte…
- **Primary Equivalent** — *F2* — FAO has never published a traceable methodology from supply-utilisation accounts to the food balance sheet, so the scorer measures the contestant's ability to guess undocumented FAO conventions rather than agent reasoning, and the…
- **Cover Page** — *F4* — An eight-line `if abs(sum(rows)/total - 1000) < tol: divide by 1000` solves every uniformly mis-scaled filing and there is zero evidence that mixed-scale-within-one-table filings are common; the corpus was never observed and the U…
- **Cross-Cut** — *F4* — The total the agent must produce sits at the bottom of the same dense multi-column budget table it reads, and redacting a PDF table is far harder than redacting a named prose section, so the benchmark measures PDF table extraction…

### Angle O — Cross-system mapping  (9 killed)

- **Second Opinion at the Border** — *F4* — The agent attacked the wrong corpus — it measured shortcuts on 150 recent NY rulings, but the candidate's actual case set is HQ reconsiderations, where the harness must hand the agent the prior ruling, and a ~20-line script that s…
- **Nomenclature Drift** — *F4* — The validity half is `code.replace('.','') in FROZEN_SET` — one line, 100% accurate, no agent — and the which-child half has, by the generating agent's own measurement, 1 labelled case per 150 rulings, so it cannot reach 10 cases.…
- **The Overlay** — *F4* — Majority class wins outright and the genuinely cross-system half is a published join table (Ch.99 subchapter notes keyed by HTS8 x country), so a script is not a shortcut but the correct engineering answer. Filtering to overlay-on…
- **Two Shelves, One Book** — *F4* — A 20-line in-sample LCC-to-DDC majority lookup already scores 91.1% on the headline metric, and the DDC schedules the agent would need are OCLC copyright so the reference material cannot ship in a self-contained clone.
- **What It Is vs Who Makes It** — *F4* — GSA publishes the PSC-to-NAICS crosswalk and a 20-line majority lookup takes 84.4% of the task; the 15-point residue is contracting-officer noise with no external adjudicator, so there is nothing correctly-labelled left to compete…
- **Same Bug, Different Registry** — *F4* — The ground truth IS a free bulk-downloadable lookup table — OSV publishes the complete CVE-to-purl mapping for every advisory, so a Python `dict` scores 100% and any judge can download the answer key. Freeze dates do not save it b…
- **One Smokestack, Two Federal IDs** — *F4* — 89.2% of the task is a one-line pandas exact-ID merge and a further 174 rows fall to three string normalisations EPA documents in the file itself, leaving 73 agentic cases whose answers are published in the same CSV the agent is s…
- **Designated Twice** — *F1* — The third-party key the whole design rests on does not exist: zero UN listing references across 29 MB of OFAC SDN XML and only 86 non-empty on the EU side, so the only remaining pairing source is OpenSanctions (CC-BY-NC, forbidden…
- **The Name It Goes By Now** — *F4* — A two-line GBIF API echo scores 93.3% on the natural distribution, and the only escape — restricting to the divergent subset — requires the contestant to adjudicate contested taxonomic questions he has no standing to arbitrate.

### Angle P — Deliberate anti-crowding  (8 killed)

- **Standing Precedent** — *F4* — The entire claimed novelty — "the broker cannot tell a live precedent from a dead one at search time" — is factually false: CBP's own search API returns `revokedBy`, `revokes`, `modifiedBy` and `operationallyRevoked` as machine-re…
- **Rights Statement** — *F2* — The author could not find any reuse statement for the Hathifiles and hathitrust.org/hathifiles 403s (I re-confirmed: HTTP 403), so "judge runs it from a bare clone with the network off" is unestablished for the only file that carr…
- **Cutoff Authority** — *F4* — NARA publishes the mapping itself: I found "GRS Crosswalk" at https://www.archives.gov/files/records-mgmt/grs/grs-crosswalk.xlsx linked off the GRS index page — an official old-item-to-current-item spreadsheet, which is the publis…
- **Accepted Name** — *F4* — The gold label and the shortcut are the same file: the WFO Darwin Core backbone carries `acceptedNameUsageID` keyed on `scientificName`, so "return the accepted taxon id" is a one-column join against the answer key. On top of that…
- **Deprecated Heading** — *F4* — The Library of Congress publishes the old-heading-to-new-heading mapping as weekly approved lists, so the task is a dictionary join and a 20-line script is the complete correct solution, not a baseline. The author already reached …
- **Compliance Requirement** — *F4* — The finding narrative names its own compliance requirement in its heading ("2023-003 Controls Over Reporting" → gold letter L = Reporting), so this is extraction, not judgement, and a keyword map wins. Independently, the data sour…
- **Condition or Practice** — *F3* — MSHA's bulk Violations dataset has no "condition or practice" narrative field at all, so there is no text for an agent to reason over; what remains is tabular prediction that a gradient-boosted tree does better than any agent, and…
- **Health Hazard Class** — *F4* — The reason_for_recall field is a one-line hazard statement, so the hazard class is written into the input and a six-line regex takes most of it; the trajectory is one shallow classification call. The author is right and I reproduc…

### Angle Q — Contestant-asset  (8 killed)

- **Ex-Date Contract Master** — *F4* — The NSE FAOP circular the agent is meant to fetch publishes the answer as labelled fields — `Type of corporate action`, `Adjustment factor*`, `Adjusted revised market lot*` — so the whole task collapses to regex-the-table, divide,…
- **Circular to Executable** — *F3* — Its own author could not confirm the reference-price series NSE keys lot sizes off is public, so the benchmark may be unanswerable rather than hard, and rule-changing circulars that produce a bulk published file are too rare to re…
- **Backtest Discontinuity Audit** — *F4* — The ground truth is defined as the union of NSE's published FAOP circulars and symbolchange.csv — documents the agent is explicitly allowed to fetch — so enumerating the circular directory for the window reproduces the answer key …
- **Allotment Basis Rebuild** — *F3* — Its author never obtained a single Basis-of-Allotment document (registrar HTTP 000, BSE 301), so the ground truth is unverified and speculative, and the scorer requires hand-transcribing registrar PDFs — authored ground truth, whi…
- **RTI Appeal Outcome** — *F3* — cic.gov.in exposes no bulk decision index and the PDFs carry no structured outcome field, so Chinmoy would have to read each decision and write the clause and disposal himself — authored ground truth by a non-lawyer, dead on two f…
- **Rig Downtime Coding** — *F2* — No public IADC-coded daily drilling report corpus exists — IADC sells the forms, and NSTA/Sodir/NLOG publish well results not daily NPT-coded operations — so the labels would have to be authored by a non-credentialed drilling engi…
- **Ministry Routing** — *F4* — The label is literally the first clause of the input ('Will the Minister of RAILWAYS be pleased to state'), and once stripped the task degrades to topical bag-of-words classification a TF-IDF baseline plausibly wins, decided in a …
- **Ban Period Replay** — *F4* — A one-line persistence constant — 'emit yesterday's list' — nearly solves it, the metric saturates near 100% which reads as rigged, and the trajectory is a single arithmetic pass with nothing to watch.

### Angle R — Wildcard  (8 killed)

- **Clockwork** — *F4* — I cloned eggert/tz and read the Asia/Tehran block: the maintainers wrote the Gregorian conversion INTO the quotation the agent is handed — "1357/8/19 AP=1978-11-10" and "At the hour 24 of Friday 19th of Aban (=1978-11-10)" — so th…
- **Errata Court** — *F5* — I ran the exact baseline the candidate admitted it never tested — one off-the-shelf model, one prompt, no tools, no RFC retrieval, sanitised erratum text only — on a blind 10/10 balanced sample and scored 0.90 balanced accuracy ag…
- **Protest Room** — *F2* — I pulled the PDF and read page 2: "ISBN: 978-1-938915-57-4 / © 2025 United States Sailing Association, Inc. / All rights reserved." — an ISBN-registered copyrighted book, and the rulebook it depends on is World Sailing copyright t…
- **Rule 9.16** — *F4* — I computed the number the candidate said it could not compute: predicting ER=0 for every pitcher-game in games containing an error play scores 0.5798 exact-integer accuracy across the full 2023 season, so a single constant takes t…
- **Rating Officer** — *F5* — FIDE B.02 is a published closed-form calculation and the body that publishes the answers also publishes the formula, so a 20-line script or one prompt plus the handbook solves it — the candidate's own author concedes this and coul…
- **Homonym** — *F4* — I re-ran the GBIF probes myself and confirmed the authority's own /species/match endpoint returns EXACT with the correct kingdom at confidence 97-99 on the cross-kingdom homonyms designed to break it, so the entire benchmark is on…
- **Cited-Retracted** — *F4* — A constant "nothing is retracted" scores ~100% on natural data (0 retracted citations in 1,310 real references), and on any enriched set a six-line dictionary lookup against the 63,021 retracted DOIs catches 67.3% of references fo…
- **Heading Maintenance** — *F4* — LC publishes cancelled headings and their replacements as linked data with explicit replacement edges, so a thirty-line graph walk over the frozen dump resolves the chains with no model at all — the PUBLISHED-LOOKUP-TABLE law, dec…

---

## 4. What the angles revealed

**All 18 angles self-reported RICH after generation. All 18 reported BARREN after measurement.** That inversion is the finding.

**The landscapes that were genuinely rich in *data* and barren in *problems*:**
- **US federal publishing** (angles B, C, K, M, N, P) — eCFR, Federal Register, CBP, FAA, FDA. Superb corpora: keyless, dated, public domain, freezing cleanly. And almost uniformly fatal, because *the same agency that publishes the input publishes the crosswalk to the answer.* Angle C's own epitaph: "when a US agency publishes dated snapshots it also publishes the crosswalk."
- **Customs** (A, C, E, F, I, J, O, P — 8 of 18 angles converged here independently, without seeing each other). The convergence was a real signal of a real bottleneck, and it died twice: to a 100% script, and to a benchmark published in September 2025.
- **Adjudication corpora** (D, H, R — RFC errata, three independent arrivals). The one seam where a qualified body rules on someone *else's* claim, so the text argues for the wrong answer. This produced the single surviving candidate.

**The barren landscapes, and why:**
- **Micro-expertise (G)** — killed structurally: the rulebooks that matter (ASME BPVC, AWS D1.1, NFPA 70, ASME A17.1) are **private consensus standards**. You cannot vendor them. The trades are unreachable, not unexplored.
- **Aggregation/rollup (N)** — the only angle honest enough to self-report barren at generation time. Eurostat NUTS-2 GDP sums to the national total exactly once you include the extra-regio code; a one-line `sum()` is the correct answer.
- **Cross-system mapping (O)** — self-executing law: *a published crosswalk is a lookup table and the lookup table wins.* Measured four times (PSC→NAICS 84.4%, LCC→DDC 91.1%, CAMD→EIA 89.2%, Ch.99 overlays F1 0.986).
- **Contestant-asset (Q)** — NSE is poisoned at the root: the exchange publishes the adjustment factor, mechanism class and revised lot as **labelled fields in a free circular**. Every framing over that data is extraction.

**The three general laws the search produced** — these are worth more than any candidate:

1. **The retrieval law.** *If the answer document is shipped inside the artifact the judge runs, and the input keys it, a retrieval script beats the agent.* (Stated correctly — see §6, my first draft of it was wrong.)
2. **The label-leakage law.** Where an authority explains its own decision in the same document it hands you, the task is extraction and a regex or naive Bayes wins. Killed most of angle H, plus the L2M candidate (84.2% naive Bayes on the reviewer's own comment), DICES (71.4% naive Bayes), and the original Erratum Gate (96.66% regex).
3. **The closed-form anti-signal (angle J's own discovery).** *If a task can be checked in 20 lines of model-free code, it can usually be solved in 200.* Deterministic verifiability and headroom are in tension, which inverts the appeal of angle J entirely.

**Where the field is not looking, and why it may not matter.** The empty lanes are real — I re-probed them and they are still empty at 75 repos. But three of them are empty *because they are hard in ways that kill projects*, not because nobody thought of them: physical operations has no label-bearing public data that isn't WAF-blocked; micro-expertise has private rulebooks; non-English institutions publish prose the contestant cannot verify. **Emptiness is evidence of difficulty at least as often as it is evidence of opportunity** — that is the most useful strategic correction this search produced.

---

---

## 5. Verified data assets

Everything in this section I fetched myself in this session. Status codes are what `curl` actually returned; record counts are parsed from the real payload. This is a reusable asset — several of these corpora are excellent even though the candidates built on them died.

### 5.1 Assets I pulled real record counts from — VERIFIED

| Asset | URL | Status | What I actually saw |
|---|---|---|---|
| CBP CROSS rulings (search) | `https://rulings.cbp.gov/api/search?term=%22is%20hereby%20revoked%22&collection=ALL` | 200 | `totalHits: 577`; objects carry `revokes`, `revokedBy`, `modifies`, `modifiedBy`, `tariffs`, `rulingDate`, `collection` |
| CBP CROSS rulings (single) | `https://rulings.cbp.gov/api/ruling/H237685` | 200 | 8,423 chars of full ruling text; `TARIFF NO: 6405.90.90` |
| IETF RFC errata | `https://www.rfc-editor.org/errata.json` | 200 | **11,640,398 bytes, 8,021 records**; Verified 3,722 / HFDU 2,414 / Rejected 1,157 / Reported 728 |
| openFDA drug enforcement | `https://api.fda.gov/drug/enforcement.json` | 200 | **17,899 records**, last_updated 2026-08-19 |
| openFDA device recalls | `https://api.fda.gov/device/recall.json` | 200 | **59,049 records**, last_updated 2026-08-27 |
| CISA KEV catalog | `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | 200 | **1,685 entries**, dateReleased 2026-08-27 |
| Crossref retractions | `https://api.crossref.org/works?filter=update-type:retraction` | 200 | **75,092 total-results** |
| ClinicalTrials.gov v2 | `https://clinicaltrials.gov/api/v2/studies` | 200 | **600,762 studies** |
| W3C ACT rules testcases | `https://act-rules.github.io/testcases.json` | 200 | **1,134 testcases**, carries its own `license` key |
| NVD CVE API | `https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2024-3094` | 200 | Both a `Primary` (nvd@nist.gov) and `Secondary` (CNA) CVSS vector on one record — the dual-assessor structure is real |
| CISA vulnrichment | `https://api.github.com/repos/cisagov/vulnrichment` | 200 | licence **CC0-1.0**, confirmed from the repo LICENSE blob |
| Chicago food inspections | `https://data.cityofchicago.org/api/views/4ijn-s7e5.json` | 200 | `licenseId: SEE_TERMS_OF_USE` — **confirmed not an SPDX open licence** |
| Fed SPF microdata | `https://www.philadelphiafed.org/.../SPFmicrodata.xlsx` | 200 | real XLSX payload (`application/vnd.openxmlformats-...sheet`) |

### 5.2 Reachable, licence or shape not separately confirmed by me — VERIFIED reachable only

NHTSA recalls API · EPA ECHO enforcement · OSHA/DOL enforcement catalogue · FAA Airworthiness Directives (DRS) · NASA ASRS search · Aviation Safety Network · US HTS tariff (USITC reststop, 12,635,520 bytes for the full nomenclature) · EU TARIC consultation · UN Comtrade HS reference · SEC EDGAR full-text search (`efts.sec.gov`) · SEC EDGAR submissions API · FRED · EUR-Lex · EU RASFF portal · EMA medicine data · EFSA OpenFoodTox (Zenodo) · SEBI · RBI statistics · **NSE corporate announcements API (200 from this machine)** · India eGazette · CBIC GST · NFPA codes · USDA NASS QuickStats · UN Treaty Collection · Federal Register API · govinfo bulkdata · CourtListener API v4 (no key needed) · Caselaw Access Project · SYNERGY dataset repo · ICLR review dataset repo · Zenodo CUAD record 4595826 · USPTO bulk office actions · PubMed E-utilities · WHO ICTRP · CMS ICD-10 · Retraction Watch via Crossref Labs.

### 5.3 NOT reachable — killed candidates outright

| Asset | Status | Consequence |
|---|---|---|
| CFPB complaints CSV | **403** | blocked to fetchers |
| USDA FSIS recalls API | **403** | blocked |
| ECHA C&L inventory | **403** | blocked; also has a 9,999-row UI export cap |
| USCG PSC detentions | **403** | blocked |
| WHO ICD-11 API | **401** | needs credentials |
| CPSC saferproducts recalls | **404** | endpoint retired |
| FDA Warning Letters page | **404** | moved |
| Paris MoU / Tokyo MoU detentions | **404** | killed the whole port-state-control lane |
| NTSB CAROL | **405** | POST-only query API |
| data.gov.in catalog | **404** | sample key dead |
| GLEIF LEI API | no output | bracket-quoting issue, not retried |

### 5.4 Licence findings that matter — these are gate items

- **CISA vulnrichment: CC0-1.0.** Clean. VERIFIED from the LICENSE blob.
- **`CVEProject/cvelistV5`: NO SPDX licence at all** on GitHub (`license: None`). Both `nvd.nist.gov/developers/terms-of-use` and `cve.org/Legal/TermsOfUse` are **JS-walled and return no text to any fetcher** — I tried curl with a browser UA and WebFetch, and got 12 chars and a "please enable JavaScript" stub respectively. **The CVE lane therefore carries real, unresolved licence ambiguity** and fails incumbent property 4 until someone opens it in a real browser.
- **IETF errata: UNKNOWN.** `rfc-editor.org/copyright/` is **404**; the IETF Trust Legal Provisions page defers to TLP 5.0 / RFC 5378 / RFC 5377 and states no SPDX identifier. Status codes are uncopyrightable facts, but `orig_text`/`correct_text` quote RFC content.
- **Chicago food inspections: `SEE_TERMS_OF_USE`.** Confirmed from the portal's own metadata — City of Chicago Terms of Use, not an open licence.
- **US Sailing racing rules: "© 2025 United States Sailing Association, Inc. All rights reserved"**, ISBN 978-1-938915-57-4 — a killer reviewer read it off page 2 of the PDF. Not vendorable.
- **CBP / USITC: US federal agency work → public domain under 17 U.S.C. §105 (INFERRED — neither site publishes an SPDX tag).**

### 5.5 Prior art found, with URLs — VERIFIED

- **ATLAS**, arXiv **2509.18400** (2025-09-22): *"the first benchmark for HTS code classification, derived from the U.S. Customs Rulings Online Search System (CROSS)."* Fine-tuned LLaMA-3.3-70B reaches **57.5% at 6-digit**; frontier models sit ~15–27.5 points lower. **This is a direct collision with the entire customs family** — eight of our candidates were built on CROSS.

---

## 6. Honest assessment

**Did anything clear the §2.1 bar? No. Not as generated, and not cleanly even after redesign.**

143 candidates from 18 deliberately unrelated angles all died. Two came back only after being structurally redesigned, and both survive on the narrowest of the three escapes — freezing the corpus without the answers. Neither matches all six properties:

| Property | Erratum Gate (redesigned) | Instruction That Won't Execute (redesigned) |
|---|---|---|
| 1 — zero authored ground truth | ✅ | ✅ |
| 2 — dependency-free scorer, no model | ✅ | ✅ |
| 3 — cheating foreclosed by construction | ⚠️ foreclosed *within the freeze*; 100% online | ❌ **a hardcoded constant (0.5876) still beats the best script (0.5855)** |
| 4 — public domain, no licence ambiguity | ❌ **UNKNOWN** | ✅ |
| 5 — zero visible competitors | ✅ (weakened: 51% of repos have no description) | ✅ |
| 6 — simple baseline fails structurally | ✅ but **p = 0.29** | ⚠️ asserted, not demonstrated |

**Three corrections to my own work, from the critics I ran to attack it.** I report these because suppressing them would make the null result look stronger than it is.

1. **My headline law was overstated.** I wrote *"a published label is a retrievable label."* That is **false as written** — publication is a fact about the world; retrievability is a fact about the freeze boundary. The defensible form: **"A published label is retrievable whenever the answer document is shipped inside the artifact the judge runs — and the authority almost always forces you to ship it, because the same machine-readable channel that supplies your inputs supplies its own determinations."** micro1's engineers are precisely the readers who would construct the counterexample to my first version.
2. **The kill *verdicts* were sound; roughly one kill *reason* in three was not.** An auditor overturned three stated grounds by measurement — the Federal Audit Clearinghouse is **not** account-gated (67 MB and 254 MB CSVs, keyless, HTTP 200), and ICO decision notices **are** obtainable (26,367 via POST). Both candidates still died, but on *the auditor's* numbers (70.18% naive Bayes; 82.32% section lookup), not the killer's. Of 141 kills, **31 (22%) carry no filter-4 component at all** and **13 (9.2%) were killed with the trivial attack explicitly never run.** So the retrieval law is the cause of death for at most ~110 of 141, and about a fifth of the corpus died of sourcing friction, which says nothing about problem shape.
3. **My own kill of the last survivor is weaker than I first stated.** My 100% script calls the live CROSS API — and hard filter 2 requires the judge to run **network off**. Under a strict offline freeze that shipped only the HTSUS text and a held-out key, my attack does not execute. **`CROSS-Examined` therefore dies robustly on filter 7 (ATLAS already published the benchmark) and only conditionally on filter 4.** I am stating this against my own headline finding because it is true.

**The structural tension is the real result.** Property 1 demands labels externally authored **and published**. Filter 4 demands no lookup beats the metric. The same institutional machinery that makes a label trustworthy is the machinery that makes it retrievable. Every candidate in this family must break one of: the answer document being present in the freeze, the input keying it, or the answer being a surface string. **Only one of 143 specs ever attempted a held-out-authority corpus design** — and it was the sole survivor of the hostile round.

**And the shape nobody generated.** A grep across all 857,887 bytes of angle specifications found **zero** hits for "prospective", "forecast", "held out until", "embargo", "ex ante". Every one of the 143 candidates is **retrospective** — both input and label already published at build time, which is exactly the precondition the retrieval law needs. The one shape that escapes absolutely was never generated. A critic then built the cheapest instance of it (CISA KEV membership from the NVD record) and it died anyway: a one-line vendor hot-list rule scored **95.0%**, and what remained after neutralising it was *aleatoric* attacker choice — not a structural blindness, so it fails property 6 from the other side.

**Is this confirming that the obvious lanes are the good lanes? No — something sharper.** Three fresh corpora, chosen adversarially *after* the sweep by a critic hunting for over-kill, died to the same law: FDA 510(k) product codes to a **12/12 = 100.0%** regex on FDA's own clearance letter; California DMHC independent medical review to an **80.7%** naive Bayes on leaked reviewer findings; CISA KEV to that **95.0%** one-liner. Three institutions no angle had opened, three deaths, same mechanism. **141/143 is not over-killing — it is the law being general.**

**My verdict, plainly.** I did not find a challenger that beats a well-executed obvious idea. What I found is that the §2.1 bar is harder than it looks, because two of its own properties pull against each other, and that the honest way to clear it is to make the freeze boundary — not the publication status — do the work. If the incumbent clears all six, **INFERRED**, it almost certainly does so by holding the determining authority outside the shipped corpus while shipping the rule system the practitioner actually reasons from. That is analysis from the six properties and the measured law, not archaeology — I never opened the decision files.

**If forced to choose from what survived**, I would take **Erratum Gate (redesigned)** — the shortcut table is the most convincing artefact this search produced, four independent lookups pinned at exactly 0.5000 by construction — and I would spend the first two build hours re-running it at n = 60–100. If the gap does not hold at p < 0.05, it should be abandoned, and that decision should be made before any other code is written.
