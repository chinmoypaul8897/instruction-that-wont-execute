## THE DECISION

**Build the tariff-classification project — but pivot it off "consistency" and onto **supersession**: an agent that resolves which CBP ruling was *good law on the date the entry was filed*, scored against CBP's own published revocations. Ship it as CROSSCheck.**

I verified the foundation live against the CROSS API at 2026-08-29 while making this call, and it is stronger than any red team assumed. Three reasons it wins.

**1. Both labels are CBP-authored, dated, and public domain — so the primary metric has zero authored ground truth and no LLM anywhere in the scoring path.** A revocation pair is: prior ruling assigns code A on date T1; a later HQ ruling explicitly revokes it and assigns code B on date T2. Both sides are written by CBP. I resolved the five newest such pairs end to end and every one produced a genuine code change on the same merchandise:

```
N347107 2025-04-16 1504.20.6040  -> H347637 2025-05-19  1516.10.00   (33 days later)
N336132 2023-11-22 6402.91.5020  -> H338307 2025-08-28  6402.19.90
N284950 2017-05-03 1905.90.1041  -> H293899 2025-03-24  1905.90.9090
H322641 2023-11-09 8419.89.95    -> H336949 2025-07-25  8419.40.00 + 8419.89.95
K82923  2004-03-02 6201.93.3000  -> H334134 2025-12-16  6210.20.50
```

A single 300-row keyword slice (`term=revocation&collection=HQ`) returned **263 Classification rulings that revoke or modify a named prior ruling and carry tariff codes**. The `revokes` / `modifies` / `revokedBy` / `modifiedBy` / `operationallyRevoked` fields are all real, structured, and in the API response. The scorer is a string comparison against a code CBP wrote. This is the only one of the five candidates where the contestant selects cases and authors nothing at all.

**2. The bottleneck is not asserted — it is a measurable defect in CBP's own metadata, and I measured it.** Of those five superseded rulings, **four carry an empty `revokedBy` back-pointer**, and `operationallyRevoked` is `False` on all five. A broker reading N347107 in CROSS today gets no signal whatsoever that CBP revoked it 33 days later. The only way to know is to invert the entire citation graph — which is exactly what the agent's tool does, and exactly what no retrieval stack has a slot to ask. The 15-point Problem row stops being a persona essay and becomes a number: *k of N superseded rulings in the frozen snapshot are silently stale in CBP's own index.*

**3. The eval is contamination-resistant by construction, which is rare and which the likeliest technical judge will notice immediately.** Each superseded item appears twice in the queue with different entry dates — one before the revocation's effective date (correct answer: the old code) and one after (correct answer: the new code). A model that memorised the famous original ruling fails the second line. A model that memorised the revocation fails the first. A degenerate "always use the newest ruling" policy wins one bucket and loses the other. Only date-aware authority resolution wins both. Every attack that killed the other four candidates — the one-line constant, the majority-class amplifier, the tautological invariant, the gaming lane between primary and guard — is structurally foreclosed rather than patched.

---

## WHY THE OTHERS LOST

**Bindline as originally specified.** Kill shot 2 was terminal and unfixable: because BIND pairs are defined as "CBP assigned the identical code," the consistency metric decomposes into `P(both correct) + P(both wrong identically)`, and the memory-attributable half is *consistent wrongness* — the precise behaviour the README's own 19 U.S.C. 1484 argument calls a compounding violation. The primary metric rewarded the thing the pitch condemned. The pivot inverts this: propagating the retracted code is now scored as failure, and the legal argument and the metric finally point the same way.

**Deferred (CVE severity).** Killed by facts outside the repo, all one search away. CVSS-BERT (arXiv 2111.08510, 2021) reports 55.3% exact-vector match with per-metric saliency spans — the same architecture, five years old. VLAI (CC-BY-4.0, on HuggingFace, ~400MB, runs offline on CPU) reports 81.58% band accuracy against this design's 48.5% CNA baseline, and sits unused in a PDF-sanctioned baseline slot. And a two-constant rule with no LLM at all clears the entire pre-registered bar (26.3% APY vs an 18.0% target). A judge who spends ninety seconds outside the README finds a 2021 paper with double the headline number and a free model that beats the baseline. Unrecoverable in 26 hours.

**Markscheme (SPF).** The killer objection is unanswered and unanswerable: a researcher transcribes Tables 6, 7 and 8 once — thirteen columns, at most twenty values — into a config file and never needs the agent again. The build plan literally budgets H2–H5 to do exactly that, by hand, permanently. Problem & User Value scored 10/15 for a reason. Compounded by a transcription error already sitting in the design document (eleven comma-separated entries expanded to fourteen surveys) on the single most-cited gold artifact, in a project whose thesis is silent transcription error.

**Second Analyst (ASRS).** The "invariant discovered in the data" is printed on page 16 of NASA's public coding form — Primary Problem is a single-select from the Contributing Factors checklist plus one extra option. The 100.00% is a tautology of a form, presented as an empirical finding, and it justifies one of only three capabilities. Then BM25 precedent retrieval, the capability meant to carry the result, biases the context +11.1pp toward the majority class and retrieves the true label 0-13% of the time on the exact long tail the guard metric protects. Agent Solution & Engineering scored 16/30 — the first tie-break, and the lowest of the five.

**Warrant (defect review).** `crowding: very_high`, and it is worse than that. Anthropic ships the verification step and the judges use Claude Code. A direct competitor has already published Repro-Bot with "the attempts rejected" and "what is NOT established" in its README — that is the recall-cost thesis, shipped, before he starts. You cannot un-crowd a lane in 26 hours.

---

## THE PROJECT — full specification

### Name and tagline

**CROSSCheck** — *CBP publishes when it revokes a ruling. Nothing checks. This does, and it dates the answer to the entry.*

### Intended user, with a decision and a clock

A **Licensed Customs Broker** working the classification desk at a mid-size brokerage. Her decision, per line: which 10-digit HTSUS code goes on CBP Form 7501, and whether any entry already filed needs a Post Summary Correction. Her clock: entry summary is due within 10 working days of release, and the classification desk is the throughput constraint on the whole file. Her exposure: filing under a ruling CBP has revoked is a reasonable-care failure under 19 U.S.C. 1484 — it surfaces months later as a Form 28, a Form 29, or 1592 penalty exposure, and the penalty scales with the number of affected lines, so one stale ruling contaminates every entry that relied on it.

She is not fictional-with-a-name-and-a-time-of-day. Write her as a role with a documented statutory duty, and cite the statute rather than inventing a calendar.

### The bottleneck

CBP revokes and modifies its own classification rulings continuously, and the revoked ruling stays in CROSS, fully searchable, indefinitely. It is usually the *better-matching* document, because it describes the merchandise in detail while the revoking HQ ruling is written in legal-procedural language. There is no Shepard's, no KeyCite, no citator for customs rulings. Worse, CBP's own API frequently fails to back-link: **four of the five superseded rulings I checked carry an empty `revokedBy` field and `operationallyRevoked: False`**, so the staleness is invisible from the document itself. Currency is a graph property; retrieval only ever sees documents.

### Why it matters

The broker's search returns the right merchandise and the wrong law, with no marker distinguishing the two. Nothing in a standard RAG pipeline has a place to ask "is this still good law on the date I am filing?"

### Baseline

**B0 — PDF baseline type 2: one general-purpose agent with basic tools.** Full-text search over the frozen CROSS snapshot plus the relevant HTSUS chapter notes, the entire 36-line queue in one context window, one pass. Deliberately the strongest honest baseline: it *can* find the revoking ruling if it searches for it, it has the same corpus, the same model, the same tools.

**B-script — PDF baseline type 3: a simple script.** Zero-model. BM25 over the merchandise description against the frozen corpus; emit the top-1 ruling's code. Thirty minutes of work, and it forecloses the single attack that destroyed the CVE candidate ("a one-liner beats your pre-registered bar"). It also doubles as evidence for the hot take, because it is precisely the policy the hot take says fails.

### Compute-matched control arm

**B0′** — B0 at A1's exact token budget, spent on best-of-3 self-consistency with majority vote at 10 digits and a published tie-break rule. Same tools, same corpus, same context, more compute. This rules out "the agent just thought longer." Publish the token counts for all four arms side by side so the match is auditable.

### The advanced solution and its three capabilities

Three. Not four. Each one earns its place from a failure measured in the arm before it, and each has a changelog row.

**Capability 1 — Tools: `authority_check(ruling_id, as_of_date)`.** A deterministic lookup over a reverse index built by inverting every `revokes` / `modifies` edge across the frozen corpus, because CBP does not publish the back-pointers. Returns `{status, superseded_by, superseding_code, effective_date, chain_depth}`. *Fixes F1: B0 cites revoked rulings and never learns they are dead, because the document does not say so and the API's back-pointer is empty.*

**Capability 2 — Skills: `SKILL.md`, the classification procedure.** Fixed order of operations: identify merchandise → search CROSS → **call `authority_check` on every ruling you intend to rely on, before citing it** → apply the effective-date rule against the line's entry date → emit code plus the authority it rests on. *Fixes F2: given the tool in the previous iteration, the agent calls it late, selectively, or not at all. Tool availability is not tool use — measure the gap and report it; it is one of the most useful findings in the whole build.*

**Capability 3 — Memory: the classification decision register.** Carries `(commodity profile → code, controlling ruling, effective date)` forward across the ordered queue, and when a later line reveals that an authority changed, it re-opens the earlier lines that relied on it and files each into the correction queue with a disposition — *no action, entry predates effective date* or *flag for Post Summary Correction*. *Fixes F3: arms without it switch codes going forward and never revisit what they already emitted, silently leaving the importer with an inconsistent set of filed entries. This is the real broker workflow and it is what makes memory load-bearing rather than a cache.*

If the H15–H18 measurement shows the register contributes nothing, it becomes the removed experiment and the submission ships with two capabilities. Two purposeful capabilities beat three where one is decorative — the PDF says so outright.

### Primary metric, and exactly why it is not LLM-judged

**Controlling-Authority Agreement (CAA-SUPERSEDED):** the fraction of the 24 dated queue lines on superseded merchandise where the emitted 10-digit code equals the code assigned by the ruling that was controlling **as of that line's entry date**.

Not LLM-judged because there is no judgement in the scoring path at all. Both candidate codes are strings CBP published. The controlling authority as of a date is resolved by comparing two dates. The scorer is a dependency-free stdlib script with no model, no network and no hand-picked keys, and it is the same script for all four arms. The one legal rule it encodes — revocation under 19 CFR 177.12 takes effect 60 days after publication in the Customs Bulletin, so pre-effective-date entries were correct as filed — is stated in the README as an explicit interpretation with the citation, per the brief's "write your interpretation into the README" cover.

Two named negative criteria, reported per arm alongside the primary number, in micro1's own Realm Financial style:

- **Stale-authority error** — emitted the retracted code on a post-effective-date line.
- **Anachronistic-authority error** — emitted the new code on a pre-effective-date line.

These are symmetric and they close every degenerate lane: "always use the newest ruling" maximises one and maximises the other.

### Guard metric, pre-registered

**CAA-STABLE on the 12 control lines: A1 must not lose more than 1 line relative to B0.** Plus **False Supersession Rate: A1 must assert at most 1 supersession across 36 lines that CBP's frozen citation graph does not contain.** Both are checked mechanically against the same frozen data. Pre-registered success on the primary: **A1 ≥ B0 + 25 percentage points on CAA-SUPERSEDED, with line-level McNemar p < 0.05.** Predicted outcome, written down before the run: B0 lands near 50% by the structure of its own blindness (it gets the pre-date lines right and the post-date lines wrong); A1 lands near 80%. **Do not chase 100%.** A partial gain with the failing class named is the shape the brief endorses; a clean sweep reads as a rigged baseline.

### The evaluation corpus

**Source:** U.S. Customs Rulings Online Search System (CROSS). Search API `https://rulings.cbp.gov/api/search` — verified HTTP 200 today, returning `rulingNumber`, `rulingDate`, `categories`, `collection`, `tariffs`, `revokes`, `modifies`, `revokedBy`, `modifiedBy`, `operationallyRevoked`. Ruling full text at `https://rulings.cbp.gov/ruling/<number>`. HTSUS chapter notes from `hts.usitc.gov`.

**Licence:** works of the United States Government, public domain under 17 U.S.C. §105; CBP's own copyright notice states its material is in the public domain; `robots.txt` returns 404. No account, no click-through, no SPDX ambiguity. This clears ground rules 03 and 07 cleanly, which is more than three of the four rejected candidates could say.

**Construction — fully mechanical, published with exclusion counts at every step:**

1. Pull Classification-category rulings with a non-empty `revokes` or `modifies` array. (One 300-row slice already yields 263 candidates; paginate until the pool is exhausted.)
2. Resolve each named prior ruling through the API.
3. Keep pairs where: the revoking ruling's date is ≥ 2015-01-01; **each side resolves to exactly one substantive HTSUS code after stripping Chapter 99 overlays** (`9903.*`, `9817.*`, `9801.*`) — this exclusion alone removes the entire "you author labels" attack from the original design; and the two codes differ at 10 digits.
4. Sort by revoking-ruling date descending. Take the first 12. Publish the full candidate list and every exclusion count so there is no lever to bias the set.
5. For each of the 12, generate **two queue lines** — one with an entry date before the revocation's effective date, one after.
6. Add 12 **STABLE** control lines: for each superseded item, the nearest-dated Classification ruling in the same HTS chapter with no revocation edge and exactly one substantive code. Chapter-matching prevents the buckets from being distinguishable by subject matter.

**36 lines total. Primary bucket n = 24.** Stretch to 16 items / 44 lines if the headroom gate says power is needed; the pool supports it.

**Queue-line text:** the merchandise description taken verbatim from CBP's own ruling, with all HTS-shaped strings and ruling numbers stripped (`check_leakage.py` asserts it). State the scoping decision loudly and without apology: **this benchmark does not measure classification skill, it measures authority resolution — retrieval is made easy on purpose so it is not the variable under test.** That single sentence converts the "you authored the difficulty" attack into a design choice, because the difficulty lives in a fact (the revocation) that appears nowhere in the description, and because leaked classification knowledge is the *wrong answer* on half the lines.

**Frozen offline:** `data/cross/` holds byte-verbatim API responses and ruling texts with a SHA-256 manifest and `refetch.py`. Ship `.gitattributes` containing `* -text` so the manifest verifies on a judge's clone — a CRLF-mangled manifest printing FAIL as the first line of the reproduction guide is the worst possible opening for a submission staked on integrity. Two clearly labelled tiers: **Tier 1** replays committed run artifacts and rescores, offline, deterministic, under 90 seconds; **Tier 2** re-runs the agents live, needs `ANTHROPIC_API_KEY`, with stated runtime and imputed cost. Never write "runs offline" without that split.

### The hard case

**H322641 → H336949.** A revocation that *splits*: the prior ruling put the merchandise entirely under 8419.89.95; the 2025 HQ ruling returns **two** codes, 8419.40.00 and 8419.89.95, so the old ruling is still controlling for part of the goods and not for the rest. Correct behaviour is not to pick one — it is to detect that the terminal authority does not resolve to a single code for this line and route it to the LCB with both candidates and the reasoning. This is the one named human checkpoint in the system, it satisfies ground rules 04 and 05 concretely rather than rhetorically, and it is the case most likely to break A1. Report what it revealed either way.

Second hard case if there is room: a two-hop chain (H271470 revokes three separate NY rulings; chains where the intermediate ruling is itself later superseded exist in the pool). The failure mode is stopping at the first hop.

### The planned removed experiment

**Precedent-first retrieval** — inject the top-k lexically similar prior rulings into context before classifying. Pre-registered prediction, committed before it runs: *it will make CAA-SUPERSEDED worse on post-effective-date lines*, because lexical similarity systematically ranks the revoked ruling above the ruling that revoked it. If it hurts, it is the perfect removed experiment and it is the same mechanism as the hot take. If it helps, report that the hot take does not hold on this corpus and say why. Both outcomes are publishable; only silence is not.

### The hot take

**"The document that describes your product best is the one that is no longer the law."**

Measured, deterministically, in about thirty minutes with no model in the loop: run BM25 over each merchandise description against the frozen corpus and count how often the revoked ruling outranks the ruling that revoked it. Pair it with the metadata finding — four of five superseded rulings carry no back-pointer in CBP's own API.

The transferable lesson, which is what the 5-point row actually asks for: **currency is a property of the citation graph, not of the document, so it can only be learned from something pointing *at* the document — and a relevance-ranked retriever is structurally blind to it. In any regulated corpus, build the supersession index before you build the retriever. Relevance is an anti-signal for currency.** That generalises without modification to case law, clinical guidelines, tax rulings, and standards.

One non-negotiable integrity item: **cite ATLAS (arXiv 2509.18400) on the first screen.** It is the first published HTS classification benchmark derived from CROSS, and its GPT-5-Thinking figure of 25% at 10 digits is a free external floor. Position CROSSCheck as measuring the axis a per-item accuracy benchmark structurally cannot see — whether the gold label is still good law. Not citing it is an unforced integrity error on a submission staked on integrity, and it is one search away.

---

## THE 26-HOUR BUILD PLAN

| Hours | Work | Done when |
|---|---|---|
| **H0–1** | Private repo. `.gitattributes` with `* -text`. **Run logger first, before any other code**: every arm wrapped in a harness that writes one JSONL trajectory per run — agent instructions, each action, each tool response, the feedback that shaped the next step, retries, human checkpoints — plus input/output tokens, wall-clock and imputed cost per line. Nothing else gets written until this exists. | A dummy run produces a readable trajectory file and a cost row |
| **H1–3** | Paginate the CROSS API for all Classification rulings with non-empty `revokes`/`modifies`. Resolve priors. Apply the mechanical filter. Freeze to `data/cross/` with SHA-256 manifest and `refetch.py`. Build the **reverse index** by inverting the forward edges. | Candidate table + exclusion counts committed; `authority_check` returns correctly for all five verified pairs above |
| **H3–4** | Build the 36-line queue: 12 superseded items × 2 dated lines + 12 chapter-matched stable lines. Run `check_leakage.py`. | `queue.jsonl` + `gold.jsonl` committed, leakage check green |
| **H4–6** | Deterministic scorer (stdlib, no deps, no model): CAA per bucket, stale-authority and anachronistic-authority counts, false-supersession count, reconciliation line `success + failure == n`. Ship **B-script** (BM25 top-1, zero model). | Scorer scores B-script end to end |
| **H6** | **HEADROOM GATE.** Run B0 once over the full queue. | See branch rules below |
| **H6–7** | Freeze `GOOD.md`: primary metric, buckets, thresholds, the +25pp target, the guard numbers, the predicted B0 ≈ 50%, the removed-experiment prediction. Commit and timestamp **before A1 exists.** | Pre-registration committed |
| **H7–9** | B0 × 3 reps and B0′ × 3 reps. Record pass@3 and variance. | Baseline table populated, all trajectories captured |
| **H9–12** | **Iteration 1 — `authority_check` tool.** Run × 3. Diff against B0. Write the changelog row from the measured failure, not from intent. | Row 1 has evidence |
| **H12–15** | **Iteration 2 — `SKILL.md`.** Measure the tool-availability-vs-tool-use gap explicitly (how often the tool existed and was not called). Run × 3. | Row 2 has evidence |
| **H15–18** | **Iteration 3 — decision register + correction queue.** Run × 3. If it contributes nothing, promote it to the removed experiment and say so. | Row 3 has evidence, kept or removed |
| **H18–19** | **Removed experiment: precedent-first retrieval.** Run, measure, report. | Row 4 has evidence |
| **H19–20** | Ablations: A1 minus tool, A1 minus skill, A1 minus register. Final A1 × 3. Paired bootstrap CI clustered by item; line-level McNemar. | Full results matrix, failures included |
| **H20–21** | Hot-take measurement (BM25 rank of revoked vs revoking) and the back-pointer completeness rate over the whole frozen corpus. **Blind human-time study**: resolve 8 queue lines himself using only the public CROSS UI, stopwatched, *before* looking at gold, reported as a non-expert second-reader reference. | Two numbers, honestly labelled |
| **H21–23** | The artifact: a single self-contained static HTML **classification worksheet** — one row per line, the code, the ruling it rests on with status and effective date, superseded citations struck through with the superseding ruling linked, the correction queue for the LCB to sign, and the routed-to-human lines separated. No server, opens from the clone. This is what the video walks through. | Opens from a clean clone with the network off |
| **H23–25** | README (user → bottleneck → value → changelog → main failure mode → hot take), reproduction guide with exact commands for all four arms and both tiers, versions, runtime, cost. Package trajectories as a product with labelled human-intervention points, one per agent. | Deliverables 01, 02, 04 complete |
| **H25–26** | Clean-clone rehearsal on a second path, network off, manifest verify, Tier 1 replay. Fix whatever breaks. | Tier 1 green from a bare clone |

**HEADROOM GATE at H6 — the explicit branch.** Run B0 once and read CAA-SUPERSEDED.

- **B0 between 20% and 65%:** proceed as specified. This is the expected outcome.
- **B0 ≥ 70% (baseline too good):** the design is re-cut, not the data rigged. Swap the primary bucket from single-hop revocations to **multi-hop chains and modifications** — cases where the terminal authority requires following two edges, or where a ruling is modified in part and remains controlling for the rest. The candidate pool supports this (H271470 alone revokes three rulings). Budget 3 hours from the H15–H18 block, and drop capability 3 to two capabilities if needed. Do **not** respond by weakening B0's tools; that is the rigged-baseline pattern the brief says gets punished hardest.
- **B0 ≤ 10% (floor):** retrieval is broken, not the task. Fix the search tool and re-run the gate. Do not proceed to A1 with a broken corpus index.

Whatever the gate returns, it is written into the changelog as Iteration 0 with the number. A gate that fired and changed the design is better evidence of method than a gate that was never checked.

---

## WHAT COULD STILL GO WRONG

**1. B0 finds the revoking ruling more often than expected and the gap is small.** Most likely single failure. HQ revocation rulings recite the merchandise description, so BM25 may surface both documents. Mitigation: the H6 gate exists precisely for this, with the multi-hop re-cut pre-specified and budgeted. Secondary mitigation: even a modest CAA gain is accompanied by the stale-authority and anachronistic-authority breakdown, which tells a complete story about *where* the arms differ even when the headline gap is narrow.

**2. The corpus filter is more brutal than the sample suggests and yields fewer than 12 clean pairs.** The single-substantive-code requirement plus the code-must-differ requirement plus the 2015 date floor could compound. Mitigation: measure the yield at H2, not H4. If the pool is thin, relax the date floor to 2010 before relaxing the code-purity rule — date stability is worth less than label cleanliness. The 263-candidate slice I pulled came from one keyword; the true pool is larger.

**3. Trajectories are incomplete or unusable at submission.** This is the deliverable format he has never produced and it is a gate item, not a rubric item — a missing trajectory is a total loss. Mitigation: it is built in hour 1, before any project code, and every arm is wrapped from the first run. Include the corpus-derivation agent's trajectory too, with the derivation policy written alongside it.

**4. Model drift between his runs and the judge's.** The agent arms need a live model and judging happens days later. Mitigation: pin the exact model ID, publish 3 reps with the observed range rather than a point estimate, and make Tier 1 replay-from-committed-artifacts the path the reproduction guide leads with. The headline number must be reproducible from committed run artifacts even if a live re-run drifts.

**5. He over-builds.** Named as his primary personal risk in his own dossier — nine substantial projects, several at 40k+ lines and 2,000+ tests. Mitigation: three capabilities is a hard cap, 36 lines is a hard cap, and the H21 artifact is a single static HTML file with no framework. If the plan slips, the ablations at H19–20 are the first thing cut, not the trajectories or the reproduction rehearsal.

**6. A customs-law error in the effective-date interpretation.** He is not a broker. Mitigation: state the interpretation with its citation in the README as an interpretation, not as expertise; scope the claim to "the code CBP's controlling ruling assigns," which is what the scorer actually checks; and never claim the worksheet is filable. The worksheet is an input to a licensed broker's judgement and says so on its face.

**7. Adjacency to micro1's own Realm Tax benchmark.** Tariff nomenclature is a genuinely distinct discipline from tax, but a judge who owns Realm Tax may read this against in-house work. Mitigation: confess the adjacency in one sentence and move on. It is second-order.

---

## THE FIRST THREE THINGS TO DO

**1. Create the private repo and write the run logger — before anything else, including the corpus.** `.gitattributes` with `* -text` on line one. Then the harness that wraps every agent invocation and emits one JSONL trajectory (instructions, actions, tool responses, feedback, retries, checkpoints) plus input/output tokens, wall-clock and imputed cost per line. Both of the metrics that only two repositories on all of GitHub carry are retrofit-hostile, and the trajectory format is the one deliverable he has never produced. Thirty to forty-five minutes, and it must be the first commit.

**2. Paginate the CROSS API and measure the actual yield of the mechanical filter.** Start from what already works:

```
https://rulings.cbp.gov/api/search?term=revocation&collection=HQ&pageSize=100&page=N&sortBy=DATE
```

Keep rows where `categories == "Classification"` and `revokes` or `modifies` is non-empty and `tariffs` is non-empty. Resolve every named prior through the same endpoint. Then report four numbers before writing another line of code: total candidate pairs, pairs surviving single-substantive-code purity, pairs where the codes differ at 10 digits, and pairs dated 2015 or later. If that last number is comfortably above 12, the project is green. Sixty to ninety minutes.

**3. Build the reverse index and measure the back-pointer completeness rate over the full frozen corpus.** Invert every `revokes`/`modifies` edge, then count how many superseded rulings carry a populated `revokedBy` or `modifiedBy` of their own. My five-ruling sample said one in five. Whatever the real rate is over hundreds of rulings, it is the first hard number in the README, it is the justification for capability 1, and it is the sentence the whole pitch opens with. Thirty minutes, and it converts the problem statement from an argument into a measurement before hour three.