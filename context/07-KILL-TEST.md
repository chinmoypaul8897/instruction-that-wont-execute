# Kill Test — Results

> **Run:** 2026-08-29, solo session. **Method:** the corpus was harvested live from CBP CROSS, the
> evaluation set was built to the specification in `context/05-FINAL-DECISION.md` verbatim, and every
> attack below was **executed**, not argued. Scripts, logs and raw JSON are under `killtest/`.
>
> **Evidence key:** **VERIFIED** = I ran it or fetched it, and the number/URL is given · **INFERRED** =
> reasoning from verified facts · **UNKNOWN** = I looked and failed, and I say what I tried.

---

## 1. VERDICT ON CROSSCHECK

**CROSSCheck is dead. A 30-line script with no model in it scores 100.0% (36/36) on the exact
evaluation set the design specifies — and 100.0% again on a 120-line extension.**

It dies twice over, and the second death is the worse one.

**It dies as a benchmark.** The design's own primary attack — retrieve the ruling from the product
description, follow the revocation edge, compare the entry date to the effective date, emit the
corresponding code — is thirty lines of Python over the frozen snapshot. It scored **36/36 on the
36-line queue, 120/120 on the 120-line extension, and 24/24 on the superseded bucket that is supposed
to be the hard part.** It stayed at 100% when I moved the entry dates to within **one day** of the
effective date, when I replaced the merchandise description with **five keywords**, and when I varied
the effective-date rule from +0 to +180 days. This is the same attack, in the same corpus, that killed
`CROSS-Examined` in the divergent search. It is not close, and it is not fixable by tuning the queue.

**It dies as a problem.** The pitch rests on a factual claim: that a revoked CBP ruling sits in CROSS
with *"no marker distinguishing the two"*, and that CBP's API *"frequently fails to back-link"*, so the
staleness is invisible. Both halves are false at the population level.

- **94.7%** of the 514 superseded rulings in the harvested pool carry a **non-empty `revokedBy` /
  `modifiedBy` back-pointer** in CBP's own API (VERIFIED: 487/514, re-confirmed live on a random
  sample of 25). The 05-FINAL-DECISION figure of "four of five empty" came from the five *newest*
  pairs — the one slice where the index has not caught up. By revoking-ruling year the completeness is
  **100% for 2015–2020, 87.7% for 2024, 12.5% for 2025, 0% for 2026.** It is an indexing lag of about
  a year, not a structural defect.
- **CBP's own CROSS web application already displays the marker.** I pulled the Angular bundle
  (`https://rulings.cbp.gov/main.aca576e47806df3d.js`, 2,018,231 bytes) and it contains the rendered
  strings `S(1,"Revoked")`, `S(1,"Revoked by Operation of Law")`, `S(3,"Revoked by: ")`,
  `S(2,"Revokes: ")` and `S(3,"Modifies: ")`, bound to `ruling.revokedBy` and `ruling.modifiedBy`
  (VERIFIED, grep output in `killtest/data/ui_evidence.txt`). The broker in the persona opens the
  ruling and sees a **Revoked** badge and a link to the ruling that revoked it. *"Nothing checks"* is
  the load-bearing sentence of the pitch, and it is not true.

And the hot take does not survive contact with its own measurement either. *"The document that
describes your product best is the one that is no longer the law"* is true as far as it goes — the
revoked ruling wins BM25 top-1 in **91.7%** of superseded lines. But its stated consequence, that a
relevance-ranked retriever is *structurally blind* to currency, is false: the revoking ruling is in the
**top-5 for 100.0% of superseded lines**, because CBP's revoking ruling quotes the prior ruling's
merchandise description verbatim (**80.0%** of 300 sampled pairs share ≥5% of their 8-gram shingles).
The revocation is not hidden from the retriever. It is one hop down the same result list.

Three further internal contradictions, each measured:

1. **The named hard case is excluded by the design's own filter.** H322641 → H336949 is a *split*
   (8419.89.95 → 8419.40.00 + 8419.89.95). Construction step 3 keeps only pairs where *"each side
   resolves to exactly one substantive HTSUS code."* **0 of 514 clean pairs are splits.** The hard
   case has n = 0 in the benchmark that is built to showcase it. (There are 103 real splits in the
   911-pair pre-filter pool — 11.3% — so the class exists; the filter deletes it.)
2. **The pre-registered escape hatch is empty.** The H6 headroom gate says that if B0 ≥ 70% the design
   re-cuts onto *"multi-hop chains and modifications"*. Across the entire 2,851-edge supersession graph
   there are **56 two-hop chains, of which 9 have a terminal ruling dated 2015 or later**, collapsing to
   ~7 distinct terminal rulings (VERIFIED). That is below the ≥10-case floor. The fallback the plan
   depends on does not have a pool.
3. **The label is a field in the shipped corpus.** The gold code is the string in the `tariffs`
   metadata field of the controlling ruling; the input trivially retrieves that ruling; the script
   reads the same field. That is the label-leakage law in its purest form. Even reading the code out of
   the ruling *text* instead (`TARIFF NO.:` header regex) the script still scores 97.2% overall and
   **100.0% on the superseded bucket**.

Nothing here is a tuning problem. Every one of these is a property of the corpus.

---

## 2. The attack table

Every attack in §3 of the kill-test brief was **run**. The evaluation set was built to
`05-FINAL-DECISION.md`'s construction recipe verbatim: 12 superseded items (newest revoking-ruling date
first, single substantive code per side after stripping Chapter 99 overlays, codes differing, revoking
ruling dated ≥ 2015-01-01), each producing two dated queue lines, plus 12 chapter-matched stable
controls — **36 lines, primary bucket n = 24.** An extended set of 40 items / 120 lines was built the
same way. The frozen corpus is 4,200 CROSS ruling texts plus 18,983 metadata records, harvested live on
2026-08-29 and held offline; BM25 is a 30-line sparse implementation over that snapshot.

### 2.1 The attack table

| # | Attack | ALL 36 | SUPERSEDED 24 | pre-date 12 | post-date 12 | STABLE 12 |
|---|---|---|---|---|---|---|
| **A1** | graph-lookup (metadata codes, +60d rule) | **100.0%** | 100.0% | 100.0% | 100.0% | 100.0% |
| A1b | graph-lookup (regex TARIFF NO codes) | **97.2%** | 100.0% | 100.0% | 100.0% | 91.7% |
| A1-text | prose-only graph (+60d rule) | **80.6%** | 87.5% | 100.0% | 75.0% | 66.7% |
| A2a | majority-class constant (oracle-tuned) | **5.6%** | 4.2% | 8.3% | 0.0% | 8.3% |
| A2b | always-OLDEST-code (walk back edges) | **66.7%** | 50.0% | 100.0% | 0.0% | 100.0% |
| A2c | always-NEWEST-code (walk fwd edges) | **66.7%** | 50.0% | 0.0% | 100.0% | 100.0% |
| A2d | most-frequent-code-in-chapter | **2.8%** | 4.2% | 8.3% | 0.0% | 0.0% |
| A3 | BM25 top-1 ruling -> its own code | **66.7%** | 50.0% | 91.7% | 8.3% | 100.0% |
| A4 | follow edge -> regex TARIFF NO (no dates) | **63.9%** | 50.0% | 0.0% | 100.0% | 91.7% |

**A1 is the kill.** Thirty lines, no model: BM25 top-1 over the frozen corpus → follow the revocation
edge → compare the entry date to `revoking_ruling_date + 60 days` → emit the corresponding code.
**36/36.** I audited every line individually for a leakage bug and there is none: the script's only
inputs are the description string, the entry date, and the frozen corpus.

A note on why the constants look so weak. A2a (5.6%) and A2d (2.8%) score near zero because the label
space is ~2,900 ten-digit codes, not because the task is hard — that is the benchmark working as
designed, and it is the one thing in the design that holds up. A2b/A2c/A3/A4 all sit at exactly **50.0%
on the superseded bucket**, which is the design's central claim and it is correct: a date-blind policy
wins exactly one of the two dated lines. The problem is not that the degenerate policies win. It is
that the non-degenerate script wins outright.

### 2.2 A1 under stress

If a 100% is real it should survive being attacked. It does.

| Stress applied to A1 | ALL | SUPERSEDED |
|---|---|---|
| extended set, 40 items / 120 lines | **100.0%** | 100.0% |
| entry dates ±90d from the effective date | **100.0%** | 100.0% |
| entry dates ±30d | **100.0%** | 100.0% |
| entry dates ±7d | **100.0%** | 100.0% |
| entry dates ±1d | **100.0%** | 100.0% |
| query = top-30 TF-IDF keywords only | **100.0%** | 100.0% |
| query = top-15 TF-IDF keywords only | **97.2%** | 100.0% |
| query = top-8 TF-IDF keywords only | **97.2%** | 100.0% |
| query = top-5 TF-IDF keywords only | **97.2%** | 100.0% |
| query = first 25 words of the description | **100.0%** | 100.0% |
| effective-date rule = rev_date + 0 days | **100.0%** | 100.0% |
| effective-date rule = rev_date + 30 days | **100.0%** | 100.0% |
| effective-date rule = rev_date + 90 days | **100.0%** | 100.0% |
| effective-date rule = rev_date + 180 days | **100.0%** | 100.0% |

Two things follow. First, the **date rule does not matter**: entry dates at ±1 day from the effective
date and offsets from 0 to 180 days all leave A1 at 100%, because the revocation pairs are years apart,
not days. Second, **retrieval difficulty does not matter**: five TF-IDF keywords still give A1 100% on
the superseded bucket. The only thing A1 needs is the edge, and the edge is shipped.

### 2.3 The model arms

Both run blind, one prompt, no tools beyond a single file read; the protocol was self-reported honoured
by all batches except one B0 batch, which I report separately.

| Arm | What it got | ALL 36 | SUPERSEDED 24 | pre | post | STABLE 12 |
|---|---|---|---|---|---|---|
| **A5** | description + entry date only, no corpus | **16.7%** | 8.3% | 16.7% | 0.0% | 33.3% |
| **B0** | + the BM25 top-5 frozen-corpus documents | **94.4–97.2%** | 91.7–95.8% | 91.7% | 91.7–100% | 100% |
| **A1** | the 30-line script | **100.0%** | 100.0% | 100.0% | 100.0% | 100.0% |

A5's exact-match figure understates it: at 6-digit granularity A5 scores **58.3%**, and its failures are
mostly statistical-suffix mismatches (`8709.19.0030` against a gold of `8709.19.00`). That is worth
recording as a separate design flaw — **gold codes are 8 digits in 16 lines and 10 digits in 20**, so
exact string equality penalises answers that are correct to the published subheading. The primary
metric as specified is not length-normalised.

**B0 is the second, independent kill.** The design pre-registers *"B0 lands near 50% by the structure of
its own blindness"* and sets success at *"A1 ≥ B0 + 25 percentage points."* Measured B0 is **94.4–97.2%**
(the 2-line spread is one batch-alignment slip by the agent, not a reasoning failure). The prediction is
wrong by roughly 45 points, the H6 headroom gate fires its *"B0 ≥ 70%"* branch immediately — and §1
shows the pre-registered fallback (multi-hop chains) has **9 instances in the entire graph**, of which
~7 are distinct. **There is at most one line of headroom for three capabilities to fix.**

### 2.4 A6 — the leakage probe

| Measurement | Value |
|---|---|
| BM25 top-1 == the source ruling the description was copied from | 94.4% |
| BM25 top-5 contains the source ruling | 100.0% |
| [superseded] BM25 top-5 contains the **revoking** ruling | 100.0% |
| [superseded] BM25 top-5 contains **both** sides of the pair | 100.0% |
| [superseded] the revoking ruling **outranks** the revoked one (the hot take) | 8.3% |
| revoking ruling shares ≥5% of the prior's 8-gram shingles (n=300 pairs) | 80.0% |

The design says retrieval is made easy on purpose so it is not the variable under test. That is a
defensible choice. What it did not account for is that CBP's revoking ruling **reproduces the prior
ruling's merchandise description verbatim**, so making retrieval easy for the prior ruling makes it
equally easy for the successor. Both sides of every pair are in the top 5, every time.

This also corrects the hot take. *"The document that describes your product best is the one that is no
longer the law"* — true, the revoked ruling wins top-1 **91.7%** of the time. But the stated
consequence, that a relevance-ranked retriever is *structurally blind* to currency, is false. The
revoking ruling is in the top 5 in **100%** of superseded lines. Relevance ranking demotes the
revocation by four places; it does not hide it.

### 2.5 Pool and premise

| Measurement | Value |
|---|---|
| clean revocation pairs available (2015+, single code both sides, codes differ) | **514** |
| pairs before the single-code filter | 911 |
| revocations that **split** merchandise across ≥2 codes | 103 (11.3% of all pairs) |
| splits surviving the design's own single-code filter | **0** |
| superseded rulings carrying a **non-empty** `revokedBy`/`modifiedBy` back-pointer | **94.7%** |
| `operationallyRevoked == True` | 0.0% |
| prose regex recovers the correct revocation edge, all 514 pairs | 52.5% |
| revoking rulings stating a Customs Bulletin publication date in prose | 55.5% |
| revoking rulings saying the revocation is 'effective immediately' | 0.5% |

*(The 103 "splits" figure is corrected downward to **13 genuine same-goods splits** in §5, redesign R2 — the rest
are aggregation artifacts of the `tariffs` field in multi-ruling revocations.)*

---

## 3. The structural question

> **Can the corpus be frozen offline such that the AGENT can determine the controlling authority, but a
> DETERMINISTIC SCRIPT cannot?**

**No. There is no freeze boundary on this corpus that admits the agent and excludes the script. This is
measured across four progressively hostile freezes, not argued.**

The revocation information must be in the shipped corpus or nobody can answer. I shipped it four ways,
each stripping more than the last, and ran the cheapest model-free attack that each freeze admits.
Codes are extracted from the ruling *text* in all four rows so the numbers are comparable.

| Freeze | What the judge's clone contains | Cheapest model-free attack | n=36 | n=120 |
|---|---|---|---|---|
| **F1** | everything CBP publishes (structured `revokes`/`revokedBy` + subject + text) | structured-edge lookup, 16 lines | 94.4% | 95.8% |
| **F2** | structured revocation fields stripped; `subject` kept | regex on the `subject` string | 86.1% | 90.8% |
| **F3** | structured fields **and** `subject` stripped; raw ruling text kept | regex on the ruling's own RE: line | 88.9% | 93.3% |
| **F4** | + **every ruling-number token deleted from every document** | 8-gram quotation overlap + date | 94.4% | 94.2% |

The ladder does not decay. It bottoms out at **F3 (88.9%)** and then goes back **up** at F4, which is the
finding. Here is why.

**F1 → F2 → F3: the edge is written in prose, repeatedly, in CBP's own house style.** Every revoking HQ
ruling is titled `Revocation of NY N336132; Tariff Classification of Men's Footwear from Vietnam`. That
string is in the `subject` metadata field, in the `RE:` line of the ruling text, and again in the first
paragraph (*"This is in response to your request … for reconsideration of New York Ruling Letter (NY)
N336132"*). Stripping the structured fields moves the attack from a dict lookup to a one-line regex and
costs about six points. A first-pass regex I wrote in a single attempt recovers the correct edge for
**52.5% of all 514 pairs**; on the 12-item evaluation pool it recovers **75%**. Anyone tuning that regex
for an hour gets most of the rest, because it is boilerplate.

**F4 is the decisive one.** I deleted *every* ruling-number token from *every* document in the corpus,
plus the `subject` field, plus all structured revocation fields. Nothing in the judge's clone names the
edge at all. A **22-line** script still scores **94.4% (n=36) and 94.2% (n=120)**, including **92.5% on the
superseded bucket**. The mechanism is CBP's own drafting convention: the revoking ruling reproduces the
prior ruling's merchandise description verbatim under `FACTS:`. So the script retrieves the top-6
documents for the query, keeps the one that (a) contains a revocation word and (b) shares the most
8-gram shingles with the query, treats it as the successor, compares dates, and emits its
`TARIFF NO.`. **80.0%** of 300 sampled pairs share ≥5% of their shingles.

That is the trap, and it is closed on both sides:

- **You cannot hide the edge from the script without hiding it from the agent.** The only signals that
  identify the successor are the ruling number, the revocation vocabulary, and the quoted description.
  The agent has exactly the same three and nothing more. There is no fourth signal that requires
  judgement — no ambiguity to resolve, no conflicting authorities to weigh, no facts to apply law to.
- **You cannot make the residual difficulty real, because there is no residual difficulty.** Once the
  successor is identified the remaining work is `if entry_date >= rev_date + 60: new else old`. It is a
  date comparison against a constant offset. I varied that offset from 0 to 180 days and moved the entry
  dates to ±1 day of the boundary; A1 stayed at **100.0%** throughout, because the pairs are years
  apart, not days. Only **0.5%** of revoking rulings invoke the "effective immediately" carve-out under
  19 U.S.C. §1625(c)(1), so even the one place a legal rule could bite is empty.

**Is the residual difficulty real judgement or lookup? Lookup.** The design nominates the *split* case
— a revocation that assigns merchandise to two codes, so the prior ruling remains controlling in part —
as the one place real judgement lives. There are **103** such splits in the 911-pair pool (11.3%),
so the class is not an anecdote in the corpus. But **0** survive the design's own step-3 filter, which
keeps only pairs resolving to exactly one code per side. The benchmark as specified contains **zero**
instances of the only case it claims requires a human. You cannot have both the clean single-code label
and the hard case; the design asks for both in consecutive paragraphs.

**One honest note against my own kill.** The scoring path also has an authored component the design does
not acknowledge: the "controlling authority as of date D" is defined by the contestant's reading of
19 C.F.R. §177.12 (`effective = ruling_date + 60 days`), and CBP publishes the actual effective date
only in prose, in **55.5%** of revoking rulings, as a Customs Bulletin volume-and-date citation that
still needs the 60-day rule applied to it. So the claim *"zero authored ground truth"* is not quite
right either — the codes are CBP's, but the **date rule that selects between them is the contestant's**.
This does not save the candidate; it just means property 1 was overstated as well.

---

## 4. Prior art

**ATLAS is not the collision. Four papers published between April and August 2026 are.**

### 4.1 ATLAS — verdict: DISTINCT AXIS, but it owns the corpus

**arXiv 2509.18400** (2025-09-22), *"ATLAS: Benchmarking and Adapting LLMs for Global Trade via
Harmonized Tariff Code Classification"*, Pritish Yuvraj and Siva Devarakonda. I pulled the arXiv API
record myself: 40% fully-correct at 10 digits, 57.5% at 6 digits for the fine-tuned LLaMA-3.3-70B;
GPT-5-Thinking 25.0% / 55.5%; Gemini-2.5-Pro-Thinking 13.5% / 31.0%. There is also an extended
peer-reviewed version at **https://ceur-ws.org/Vol-4162/paper7.pdf** (11 pages, CEUR-WS Vol-4162).

A term search over the full text of *both* versions returns **zero** hits for `revoke`, `revocation`,
`supersede`, `effective date`, `currency`, `stale`, `1625`, `177.12`, `expire`, `amend`, `withdraw`,
`overrule`, `temporal`, and `entry date` (VERIFIED). The word `date` appears three times, and the only
substantive occurrence is `Date: {date}` inside the GPT-4o-mini extraction prompt — the ruling date is
fed to the transformation model and **discarded before the training pair is formed**.

The released record schema confirms it: every row of the 18,254-row train split and the 200-row test
split has exactly one top-level key, `messages`, holding a two-turn chat pair. **No date, no ruling ID,
no status, no edge.** For any CROSSCheck pair — the same product at two entry dates straddling a
revocation — ATLAS's input for both members is byte-identical. ATLAS does not ignore the date; it
cannot represent it.

The sharpest evidence is inside ATLAS's own data. Eight rows carry the byte-identical prompt
*"What is the HTS US Code for offset printing posters?"* — six labelled `4911.91.2020`, two labelled
`4911.91.4020`. Those are the post- and pre-revocation answers for the same goods, and one reasoning
trace says so out loud: *"the protestant was entitled to classification under 4911.91.4020 during a
60-day delayed effective date."* **583 distinct prompts in the train split carry mutually conflicting
labels.** ATLAS's format collapses a revocation pair into contradictory labels on identical inputs.

Two operational notes. The dataset is **Apache-2.0** with an attribution requirement to Flexify.AI Inc.
And both official Flexify.AI HuggingFace repos — the dataset and the model — **return HTTP 401 as of
2026-08-29** (a control fetch of `squad` returned 200 in the same session, and the org page shows
"datasets 0 None public yet"). ATLAS's release claim is currently not honoured at its own URLs; the
schema findings above come from a public mirror whose split sizes match the paper exactly. There is
also a commercial product on the same corpus, **TariffPro** (`https://tariffpro.flexify.ai/`), which I
fetched: its page contains **zero** occurrences of *revoke*, *supersede*, *stale*, *effective date* or
*citator*.

So: ATLAS owns the corpus and the classification axis, and is structurally blind to the currency axis.
On this narrow question the design's framing was correct.

### 4.2 The real collisions — and they are recent

Four papers, all VERIFIED by fetching and grepping the full text rather than reading abstracts:

| Work | What it already establishes | Why it hurts |
|---|---|---|
| **"When Do LLMs Apply the Wrong Law?"** arXiv **2608.14610** (2026-07-08) | Names the capability **"temporal applicable-law determination"**; shows LLMs apply the most recently enacted law *"regardless of when the legally relevant facts occurred"*; studies *"post-cutoff staleness, where models apply superseded rules after legislative amendments, and recency bias"* | CROSSCheck's headline finding — models default to today's authority — **is this paper's abstract.** Published seven weeks ago. |
| **Controlling Authority Retrieval (CAR)**, arXiv **2604.14488** (2026-04-15) | Formalises retrieving the *"currently active authority frontier"* rather than the top-similarity document; proves it is a distinct objective from relevance; ships four supersession benchmarks including SCOTUS overruling and FDA superseding-label pairs | This is CROSSCheck's **hot take, as a theorem, with benchmarks.** *"Newer authorities can revoke older established ones even when semantically distant."* |
| **FiscalQA Pro**, arXiv **2608.09393** (2026-08-10) | Date-conditioned retrieval of the version controlling at a past date over a 32,436-version corpus; names *"temporal misgrounding"*; reports static RAG at 0% | This is CROSSCheck's **task shape**, on French tax law, three weeks old. |
| **LexKairos**, arXiv **2608.09106** (2026-08-10) | Nine sub-tasks of "legal temporal capability" over Chinese statutes and cases | Establishes the benchmark category. |

Plus the citator family, which is older and well populated: *Large Legal Fictions* (arXiv 2401.01301,
also *J. Legal Analysis* 16(1):64) has an explicit **"Overruling year"** task motivated in CROSSCheck's
exact words; *Validate Your Authority* (arXiv 2605.17691) does multi-label precedent-treatment
classification; *Do LLMs Truly Understand When a Precedent Is Overruled?* (arXiv 2510.20941, JURIX
2025); LegalBench's `overruling` task; SAT-Graph RAG (arXiv 2505.00039) for deterministic
point-in-time legal retrieval.

**Honest collision assessment: ADJACENT_OVERLAP.** CROSSCheck occupies a novel *cell*, not a novel
*axis*. The genuine gap is narrow and real — every as-of-date benchmark that exists runs on **versioned
statutory** corpora where supersession is already machine-readable version metadata, whereas an agency
adjudicative ruling revoked by a separately-published notice carrying its own effective date has no
benchmark literature (arXiv API sweeps for `"ruling revocation"` and `"good law" AND "citator"` return
**zero** entries, VERIFIED). But a judge who runs one search finds 2608.14610 and says the discovery
was already made. That is survivable on its own; it is not survivable on top of A1 = 100%.

### 4.3 The premise, falsified in its literal form

I asked an agent to try to break *"there is no Shepard's for customs rulings"*, and it broke:

- **data.gov's own CROSS description** advertises the citator function: *"CROSS has the added
  functionality of CROSS referencing rulings from the initial search result set with their modified,
  revoked or referenced counterparts."*
- **The CROSS web UI ships the badge.** (My own measurement — see §1.)
- **An existing public artifact already does it.** `github.com/HumbleIgnite/cbp-customs-rulings`, an
  Apify actor last updated 2026-06-06, derives an explicit `active`/`revoked`/`modified` status from
  `revokedBy`, and its README markets the exact use case: *"Rulings marked revoked have been superseded
  — check the revokedBy array to find the replacement ruling."*
- **The corpus artifact already exists too.** Zenodo record **21877141**, *"Durability of United States
  Tariff Classification Rulings, 1989 to 2026"* (CC-BY-4.0, deposited **2026-08-10**), enumerates all
  **221,442** CROSS rulings and builds the full withdrawal graph.

What survives is only the operative form: the linkage is incomplete on the newest rulings, and there
are genuine false negatives in the old ones. I verified one: HQ **951027** (1992) has the subject line
*"HRL 085384 revoked."* and an **empty `revokes` array**, while **085384** shows an empty `revokedBy`.
That case is invisible in the structured graph in both directions — and §5.4 shows why that does not
help.

### 4.4 Competitor census, re-run live

**81** public repos created since 2026-08-27 referencing micro1 / the challenge (VERIFIED via the
authenticated `gh` API, two layers: repo search on name/description/topics, then code search on file
contents — layer 2 found 16 repos layer 1 missed). Lane probes across the 71 repos with readable
READMEs: **zero** hits for customs, CBP, CROSS ruling, tariff, HTSUS, HS code, harmonized, trade
compliance, citator, "good law", errata, IETF, RFC ⟨n⟩, Federal Register, amendatory, airworthiness or
retraction. `HTSUS`, `citator`, `"good law"`, `"Federal Register"`, `"amendatory instruction"`,
`"CVE severity"` and `airworthiness` each return **global** total_count = 0 across all of GitHub for
the window.

**The honest qualifier, which matters:** **37 of 81 (45.7%) have an empty description**, 10 have no
README, and **6 are fully opaque** (no description *and* no README). The defensible statement is
*"no lane competitor among the 71 repos whose content was readable on 2026-08-29"* — not *"no lane
competitor exists."* The nearest things found were `Bernaljp/nightstop` (the only entry built on a live
US regulatory corpus, eCFR) and `chanse-syres/evidence-maintainer` (competes on reasoning pattern, not
lane).

---

## 5. Redesigns attempted

Three, per §6's cap. **All three die**, and two die on measurements sharper than the ones that killed
the original.

### R1 — Prospective revocation risk (temporal holdout) · VERDICT: DIES

The one shape the 143-idea search never generated: freeze CROSS at date T, strip every edge pointing at
a document dated ≥ T, and ask which live rulings CBP will revoke next. The answer document genuinely
does not exist inside the freeze — the escape is real.

It dies on the other side. On the honest population — every ruling live at T — the base rate is
**0.207%**, and **always-NO scores 0.99793** (T = 2021-01-01, 161,468 live rulings, 334 positives).
Force a 1:1 matched balanced design and every leak-free method lands between **0.47 and 0.62**: best
tuned-on-test structured feature 0.612, best regex 0.623, BM25 top-1 0.497, and TF-IDF + LogReg drops
from 0.741 to **0.579** once folds are grouped by revoking ruling instead of by pair (the 0.741 was
product-cluster memorisation). The agent has nothing to read that the classifier cannot: **89.4% of all
live rulings already conflict with precedent and only 0.26% of them get revoked.** What decides it is
whether an importer chose to file a reconsideration request — aleatoric, outside the document. Fails
property 6 from the other side, exactly as the CISA KEV probe did in the divergent search.

### R2 — Partial-authority / split router · VERDICT: DIES

Predict whether the controlling authority after revocation resolves to one code or splits across
several, and route the splits to a human.

Two freezes, both fatal. **With the revoking ruling inside the freeze**, the label *is* a field: counting
the entries in its `tariffs` metadata reproduces the label at **1.0000**, and a 40-character regex on
the `TARIFF NO.:` header scores **0.9871 / F1 0.9604**. **With the revoking ruling withheld**, nothing
predicts it: the best honest grouped-CV score is **0.8232**, *below* the **0.8344** constant.

And the crux, which also corrects a number of my own: **of the 103 alleged splits, only 13 are genuine
same-goods splits (12.6%).** 85 of 103 (82.5%) are aggregation artifacts — the ≥2 codes belong to
*different* prior rulings covered by the same revocation notice, and this prior's goods get exactly one
code. Those 13 come from **6 distinct revoking rulings, 8 of them from one ruling (H303761)**. The
"hard case" is not 11.3% of the pool. It is thirteen rows from six documents. §4 of the kill-test
prompt asked whether that is a benchmark or an anecdote; it is an anecdote.

*(Group-leakage note worth keeping: random 5-fold CV reported F1 0.6118 for TF-IDF+LogReg on this task;
GroupKFold by revoking ruling reported **0.0833**. Anyone evaluating without grouping would have
reported a working 0.89-accuracy model that is memorising 36 revocation notices.)*

### R3 — Downstream contamination · VERDICT: DIES

Given one revoked ruling and the revoking ruling's reasoning, predict which *other* live rulings the
same reasoning invalidates. Ground truth = the rest of CBP's own `revokes[]` array, held out. Pool: 209
revoking rulings (2015+) that supersede ≥2 priors — size is not the problem.

The revoking ruling's `subject` field is literally a list of its victims. A regex over it plus
`relatedRulings[]` scores **F1 0.864 / exact-set 0.632** (0.884 F1 on the harder |gold| ≥ 3 subset), and
raw `relatedRulings[]` alone has **recall 0.998** — it contains every held-out answer in **208 of 209**
cases. The agent's summary is the right epitaph: *"R3 asks the agent to recover a list from a document
whose title is that list. That is extraction wearing a reasoning costume. The moment you delete the
list to make it reasoning, you delete the only evidence the list exists."*

### 5.4 The last rescue, and why it fails by construction

One escape remained. The design's construction step 1 selects rulings with a **non-empty structured
`revokes`/`modifies` array** — which selects precisely the subset where CBP's citation graph is
complete, i.e. precisely the subset a graph-lookup script solves. So build the benchmark from the
complement: the "dark" pairs, named only in prose, absent from the structured graph in both directions
(like 951027 → 085384).

I built it. **1,043 dark edges** exist in my index. After resolution and the same mechanical purity
filters: **24 clean pairs, of which exactly 1 is dated 2015 or later.** And the fatal point is logical
rather than numeric: **the pool is defined by the regex that discovers it, so edge recall for that same
regex is 100% by construction.** Any pool you can find with a script is a pool that script has already
solved. There is no third option.

*(Caveat, stated: my metadata index covers 18,983 of CROSS's ~221,442 rulings, so 1,004 of the 1,043
dark edges could not be resolved to both endpoints. A full harvest would enlarge the pool. It would not
touch the construction argument, which is what kills it.)*

---

## 6. Head-to-head

Four options, because the kill test's §6 produced a fourth: a **three-class variant of Erratum Gate**
that I built and piloted in this session. It is listed separately because the two-class version as
specified in `06-DIVERGENT-RESEARCH.md` fails a property that the three-class version does not.

### 6.1 The licence question for Erratum Gate — RESOLVED

**VERDICT: CONDITIONAL — YES, `errata.json` may be redistributed inside a micro1-owned submission.**
The IP assignment to a commercial sponsor is **not** a blocker. Controlling documents fetched and read
in full: TLP 5.0 (`https://trustee.ietf.org/documents/trust-legal-provisions/tlp-5/`), RFC 5378, RFC
5377, RFC 3978, RFC 2026 §10, the IETF Trust FAQ, and the Copyright Policy & TLP FAQ.

Four conditions, all cheap to satisfy:

1. **Verbatim only.** TLP 5.0 §3.d.i grants **no** licence to modify IETF Documents "or portions
   thereof" outside the IETF Standards Process. *Selecting or filtering records is fine* (that is
   compilation) — so stripping `errata_status_code` and `notes` is permitted — but the `orig_text` and
   `correct_text` strings must ship unedited. **This is compatible with the redesign**, which needs
   field removal, not text rewriting.
2. **Per-excerpt attribution.** TLP §3.c.iii(x) requires each portion be "clearly attributed to IETF and
   identifies the RFC … from which it is taken." Keep `doc-id` on every record.
3. **The one-fifth legend rule fires.** For at least six RFCs the errata corpus reproduces more than a
   fifth of the document (RFC 4717 48.9%, RFC 9656 39.9%, RFC 3382 33.1%, RFC 4763 27.1%, RFC 4566
   22.5%), which triggers TLP §3.c.iii(y): all IETF legends and indications of authorship must travel
   with the excerpt. Discharged by a `NOTICE` file plus `doc-id`; belt-and-braces is to ship those six
   RFCs whole (whole-RFC reproduction is unconditionally permitted).
4. **No BSD-relicensing of the prose.** Trust FAQ: *"Can I choose to use or distribute non-Code portions
   of an IETF Document under the Modified BSD License? No."* The code and schema can be MIT and assigned
   to micro1; the corpus sits in a separately-noticed third-party data directory.

**Also resolved, for completeness.** *Federal Register / eCFR / govinfo:* **CLEAN** — 17 U.S.C. §105,
robots.txt disallows only search/auth paths, FR API needs no key, and eCFR states it "does not link to
or contain standards incorporated by reference," so the IBR problem does not touch the text. *CBP CROSS
/ USITC HTS:* **CONDITIONAL** — access is wide open (`rulings.cbp.gov/robots.txt` is a hard 404) and the
HTSUS itself is uncopyrightable (19 U.S.C. §3004(c)(1)(A) makes it "statutory provisions of law for all
purposes"; *Georgia v. Public.Resource.Org* forecloses any upstream claim; the HS Convention text
contains **zero** occurrences of "copyright"). The carve-out is that CROSS rulings quote the **WCO
Explanatory Notes** verbatim and pervasively — a commercially sold WCO publication that is *not* enacted
into US law, and which CBP's own boilerplate concedes is "neither legally binding nor dispositive." A
search for "Explanatory Notes" saturates the API's 10,000-hit cap, so this is most classification
rulings, not a fringe case.

### 6.2 The Instruction candidate — the decisive check, and it passes

> *"Confirm whether exact instruction-count matching neutralises the constant. If it does not, it dies."*

**It does, and the candidate is in much better shape than `06-DIVERGENT-RESEARCH.md` concluded.**

An independent re-harvest (92 live EDNOTE sections, up from the prior 50, resolved to Federal Register
documents and AMDPAR-parsed) produced **42 exact instruction-count-matched same-rule pairs, n = 84**,
stable across 40 independent matchings. On that set:

| Attack (n=84) | Score |
|---|---|
| constant / majority class | 0.5000 |
| **`n_instructions` — the matching variable** | **0.5000 by construction** |
| best model-free feature, honest 5-fold CV (`sec_tail_len`) | 0.5934 |
| **its own permutation null for the same 26-way search** | **mean 0.5621, p95 0.6184 → empirical p = 0.185** |
| max paragraph nesting depth | 0.5768 |
| CFR part / title / agency (categorical, honest CV) | 0.4083 / 0.2393 / 0.2168 |
| TF-IDF + LogReg / MultinomialNB, 5-fold CV | 0.4307 / 0.4085 |
| GradientBoosting / RandomForest on 26 features, 5-fold CV | 0.4010 / 0.3498 |

This is a *stronger* foreclosure than the prior work found, and for a reason the prior work missed: the
0.5876 "constant that beat the script" was **the maximum of a multi-feature search**, and when you run
the permutation null for that same search the observed maximum is **indistinguishable from chance**
(p = 0.185). Every trainable model-free classifier lands *below* 0.50. The honest floor is **0.50**.

**The number nobody had ever measured — an agent arm — I ran.** Rebuilding the items with the CFR
section text as it stood the day before publication (eCFR versioner point-in-time), one high-effort agent
per item, no network, no lookups:

| Arm (Instruction) | All 24 items | The 11 items with a complete instruction block |
|---|---|---|
| model-free floor | 0.500 (0.5934 sits inside its own null) | — |
| **B0: instruction only, no CFR text** | **0.500** (12/24) | **0.545** (6/11) |
| **agent: instruction + the point-in-time section text** | **0.708** (17/24) | **0.818** (9/11) |
| delta | **+20.8 pp** (Fisher p = 0.24, McNemar p = 0.18) | **+27.3 pp** (Fisher p = 0.36, McNemar p = 0.375) |

**State this plainly: at my pilot's sample size the gap is not statistically established.** n = 24 and
n = 11 cannot establish a 20-point difference, and I am not going to pretend otherwise. What the pilot
does establish is *direction and mechanism*: the baseline sits **exactly at chance** without the section
text, the agent is 21–27 points above it with the text, and its errors are diagnosable rather than random.
If that rate holds at the full 42-pair pool (n = 84) the gap lands at **Fisher p = 0.0002** — so the
question is powerable, and powering it is the first thing the build does.

Contrast this with Erratum Gate, where the same comparison is not *unproven* but **measured at zero**:
0.675 with no corpus, 0.675 with a high-effort agent and the whole RFC, Fisher p = 1.00.

Two honest deductions, both mine to own. **(a)** 13 of my 24 items had a truncated amendatory block —
my AMDPAR extractor captured the lead-in (`"6. Amend § 1468.23 as follows:"`) and dropped the lettered
sub-instructions. One agent caught this itself and wrote *"the item is truncated and should be
regenerated before this datapoint is scored"*, which is why the clean-11 column exists. **(b)** The
independent harvest hit the mirror-image problem: 25 of 86 confirmed EDNOTE sections were dropped because
no AMDPAR could be attributed to them — and those are disproportionately the *most spectacular* failures
(an instruction naming a section that does not exist), so the surviving pool is biased toward **subtler**
defects. That is conservative for a kill test and it makes the 0.818 more impressive, not less, but it
means **fixing the AMDPAR attributor is the single highest-value build task.**

### 6.2b Erratum Gate — re-measured, and property 6 fails

The shortcut table survives independent replication and is the best in the search. **The headroom does
not exist.**

**Shortcut table** (my rebuild at n = 670, paired within `(doc-id, verifier_name)` with `notes` deleted;
an independent rebuild reproduced the prior work's n = 420 / 149 cells exactly):

| Attack | n=670 (mine) | n=420 (independent) |
|---|---|---|
| constant / majority | 0.5000 | 0.5000 |
| doc-id lookup, in-sample **oracle** | **0.5000** | **0.5000** |
| verifier-name lookup, **oracle** | 0.5000 (by construction) | **0.5000** |
| (doc, verifier) lookup, **oracle** | 0.5000 (by construction) | **0.5000** |
| `orig_text` appears verbatim in the current RFC | **0.5000** (contingency 43/43, 7/7) | 0.4786–0.5476 |
| best honest cross-validated model-free | **0.5687** | **0.5929** (edit-similarity, invented) |
| best tuned-on-test upper bound | 0.5657 | 0.6071 |

Four independent lookups pinned at exactly 0.5000, and the strongest known deterministic attack — *is the
quoted text actually in the RFC?* — pinned at exactly 0.5000 with a perfectly symmetric contingency table.
Nothing model-free clears 0.60. **This is the best foreclosure produced by the entire 143-idea search, and
I want to say so plainly before saying what follows.**

**The arms, all measured blind on the same balanced n = 100 (50 Verified / 50 Rejected):**

| Arm | Accuracy | Verified recall | Rejected recall |
|---|---|---|---|
| best model-free script | 0.569–0.593 | — | — |
| **one model, one prompt, no RFC at all** | **0.700** | 0.700 | 0.700 |
| one model, one prompt + a 5,000-char RFC excerpt | 0.740 | 0.680 | 0.800 |
| agent with the full RFC, grep + read, 5 items per batch | 0.740 | 0.660 | 0.820 |
| **agent with the full RFC, one high-effort agent per erratum** | **0.675** | 0.600 | 0.750 |

On the identical 40-item subset: no-corpus **0.675**, high-effort agent **0.675**, **Fisher p = 1.0000**.
Spending 363 tool calls and a dedicated agent per item on the published specification bought **nothing**
over a single prompt that never saw it. Three configurations, one of them deliberately over-resourced,
and the corpus does not move the decision boundary.

The three-class rescue I built to save it failed the same way. Recasting the task as the IETF's actual
three statuses (Verified / Rejected / **Held for Document Update**) produced an *even better* shortcut
table — doc-id, verifier and (doc, verifier) oracles all pinned at exactly **0.3333**, best honest
model-free **0.4356** against a 0.3333 chance line, on a balanced n = 450 across 108 cells. And then:
**baseline 0.5444, agent with the full RFC 0.5000.** Giving the agent the specification made it *worse*,
driven by Held-for-Document-Update recall falling 0.533 → 0.367.

The pattern across both formulations is consistent and is the most interesting thing I measured: reading
the spec shifts the agent toward **Rejected** (+12.0 pp two-class, +3.3 pp three-class) at the cost of the
other classes (Verified −4.0 pp; HFDU −16.7 pp). That is profitable only when the negative class is half
the set. It is a real finding about verification agents — it is §7.9's hot take — but it is not a
benchmark whose corpus is load-bearing.

**Contamination is not the explanation.** A recall-framed probe, explicitly inviting the model to recall
the published adjudication, scored **0.7400** — identical to the RFC-reading arm — and the model
self-reported genuine recall on **1 of 100** items. The 0.70 baseline is reasoning from the erratum
record, not memorising it. The erratum record simply contains most of the signal: the reporter quotes the
RFC accurately in **97 of 100** cases, so the one check the corpus uniquely enables almost never fires.

### 6.3 The six properties

| # | Property | CROSSCheck | Erratum Gate | Instruction |
|---|---|---|---|---|
| 1 | Zero authored ground truth | ⚠️ codes are CBP's, but **the effective-date rule is the contestant's** | ✅ IETF adjudicators, named and dated | ✅ NARA/OFR, named and dated |
| 2 | Dependency-free scorer, no model | ✅ | ✅ string equality | ✅ string equality |
| 3 | Cheating foreclosed **by construction** | ❌ **A1 = 100.0%** | ✅ four lookups pinned at exactly 0.5000; honest ceiling 0.5929 | ✅ `n_instructions` pinned at 0.5000; best feature **inside its own null (p = 0.185)** |
| 4 | Public data, licence unambiguous, freezes offline | ⚠️ CONDITIONAL — WCO Explanatory Notes are quoted pervasively and are not enacted law | ⚠️ CONDITIONAL — redistributable under TLP 5.0 with a NOTICE, verbatim-only | ✅ **CLEAN** — 17 U.S.C. §105, no key, no robots restriction |
| 5 | No visible competitors | ✅ 0/71 readable repos | ✅ 0/71 | ✅ 0/71 (`"amendatory instruction"` global count = 0) |
| 6 | A simple baseline fails for a statable reason | ❌ **B0 = 94.4–97.2%** | ❌ **measured at zero: 0.675 no-corpus vs 0.675 agent, p = 1.00** | ⚠️→✅ **0.545 → 0.818 on complete items (+27 pp), direction clear, n too small to be significant** |

### 6.4 The three practical dimensions

| | CROSSCheck | Erratum Gate | Instruction |
|---|---|---|---|
| **Buildable in ~24 h solo** | ✅ (irrelevant) | ✅✅ one 11.6 MB JSON file + plain-text RFCs — the easiest build in the search | ⚠️ **the real cost**: eCFR search → FR document resolution → AMDPAR attribution → point-in-time CFR text. An agent did it end-to-end in ~45 min across 8 scripted steps, but the attributor needs rework and eCFR point-in-time starts at **2017** (pre-2017 sections need govinfo annual CFR editions) |
| **Demonstrable in 60 s of video** | ✅ | ✅ | ✅✅ *"This rule says: remove the words 'and safety' from paragraph (b)(3). Here is paragraph (b)(3). Those words are not there. OFR could not codify it."* Nothing in this search is more legible |
| **Rich agent trajectory** | ✅ | ✅✅ measured — 363 tool calls over 40 items, RFC-grounded citations | ✅ measured — grep the section for each anchor, verify verbatim, report the failing instruction. The `failing_instruction` field *is* the trajectory |

### 6.5 Ranking

**1. Instruction — the only candidate with a measured, statable, mechanism-backed baseline failure.**
**2. Erratum Gate — the best foreclosure in the search, attached to a task the agent cannot improve.**
**3. CROSSCheck — dead.**

---

## 7. RECOMMENDATION

# Build "The Instruction That Won't Execute."

**One line: it is the only one of the three where the corpus changes the answer — a baseline that sits at
chance without the CFR text reaches 0.818 with it — and where the best model-free attack, after exact
instruction-count matching, cannot be told apart from chance by its own permutation null.**

Erratum Gate has the prettier shortcut table and the easier build, and I spent real compute trying to
save it: two classes, three classes, one prompt, an excerpt, an agent at five items per batch, and a
high-effort agent at one item per batch with the whole RFC. **Every configuration landed between 0.675
and 0.740, and the best of them was indistinguishable from a single prompt with no corpus at all
(p = 1.00).** A benchmark whose corpus does not change the answer is not a benchmark about the corpus.
I am not recommending it, and I would not defend it under cross-examination.

---

### 7.1 The user, with a decision and a clock

A **regulations drafter or Office of the Federal Register liaison** clearing a final rule for
publication. Her decision, per section: *will this amendatory instruction codify?* Her clock is the rule's
statutory or court-ordered effective date. Her exposure is specific and public: if the instruction is
defective, OFR cannot incorporate it, the CFR text never changes, and NARA publishes an editorial note
saying so — a permanent, citable record that the agency's rule did not take effect as written. The fix is
a correcting document, which costs another Federal Register cycle.

**VERIFIED: 92 CFR sections currently carry a live editorial note** of the form *"§ 433.2 was amended;
however, a portion of the amendment could not be incorporated due to inaccurate amendatory instruction"*
(eCFR, 2026-08-29). Every one is a rule that did not do what its agency intended.

### 7.2 The bottleneck

An amendatory instruction is an **anchor plus an operation**: *"In § 433.2, in the definition of 'ASHRAE
Baseline Building 2004', remove the text 'ANSI/ASHRAE/IES Standard 90.1-2004…' and add in its place…"*.
It executes if and only if the anchor is present in the CFR **exactly as quoted**, down to punctuation,
and the target designation resolves at the right level of a nested `(a)(1)(i)(A)` hierarchy. The drafter
writes the instruction against the text she believes is codified; OFR executes it against the text that
actually is. **The instruction carries no evidence of its own executability** — which is exactly why the
no-corpus baseline lands *below chance* while the same model with the section text reaches 0.818.

### 7.3 Baseline, control arm, and the arms already measured

- **B-script (PDF baseline type 3):** best model-free attack on the exact-count-matched set — a threshold
  on any of 26 cheap features. **0.5934 honest 5-fold CV, empirical p = 0.185 against its own permutation
  null.** Report it *with* the null; reporting 0.5934 alone would overstate it.
- **B0 (PDF baseline type 1):** one model, one prompt, the amendatory instruction only, no section text.
  **Measured 0.500 (all 24) / 0.545 (clean 11) — i.e. chance.**
- **B0-agent (PDF baseline type 2):** the same model with the section text and search tools but no skill,
  no memory, no ablation. **Measured 0.708 (all 24) / 0.818 (clean 11).** *This is the bar A1 must clear,
  and it is honest to say so — do not present 0.818 as the advanced solution's achievement.*
- **B0′ (compute-matched control):** B0-agent at A1's token budget spent on best-of-3 self-consistency
  with a published tie-break. Publish token counts for all arms side by side.

### 7.4 The advanced solution — three capabilities, each from a measured failure

1. **Tool — `anchor_resolve(title, part, section, as_of_date, quoted_text, designation)`.** Deterministic:
   fetch the point-in-time CFR section, then report whether the quoted text is present at three
   normalisation levels (exact / whitespace-collapsed / alphanumeric-only) and whether the paragraph
   designation resolves in the section's hierarchy. Returns
   `{found, level, designation_exists, siblings, char_offset}`. *Fixes F1: B0 cannot check the anchor at
   all — that is the entire 44-point gap.*
2. **Skill — `SKILL.md`, the OFR execution procedure.** One instruction at a time, in order: parse the
   AMDPAR into (operation, anchor, designation) triples; resolve each against the as-of text; check for
   intra-rule collisions (two instructions touching the same designation, an `add` onto an existing
   designation, a redesignation cycle); only then rule. *Fixes F2: given the tool, the agent checks the
   first anchor and rules from it. In my pilot the two clean-item errors were both premature rulings on a
   partial read.*
3. **Memory — the rule-level instruction ledger.** A rule amends many sections; instructions interact.
   Carry `(designation → state after each executed instruction)` across the rule so that instruction 7 is
   evaluated against the text as instructions 1–6 left it, not against the original. *Fixes F3: this is
   the actual OFR execution model, and no single-section arm can represent it.* If it does not move the
   number, promote it to the removed experiment and ship two capabilities.

### 7.5 Primary metric and guard metric

**Primary — execution-prediction accuracy** on the exact instruction-count-matched pair set: the fraction
of `(rule, section)` items where the emitted `WILL_FAIL` / `WILL_EXECUTE` equals whether NARA published a
live editorial note for that section. Scorer: string equality against a NARA-authored fact, stdlib, no
model, no network. **Target pool: the full 42 pairs (n = 84), stretch to ~60 pairs once the attributor is
fixed.**

**Pre-registered success: A1 ≥ B0-agent + 8 pp with McNemar p < 0.05 at n ≥ 84**, and A1 ≥ 0.80 absolute.
*Predicted before the run: B0 ≈ 0.50, B0-agent ≈ 0.75, A1 ≈ 0.85.* Do not chase 1.00.

**Guard metrics, both with numbers:**
- **Symmetric error reporting.** *False-defect rate* (called WILL_FAIL on an executable section) and
  *missed-defect rate*, reported per arm. A1 must not exceed **0.25** on either. This closes the
  degenerate lane: always-WILL_FAIL scores 0.500 and maximises false-defects.
- **Attributor completeness.** Publish, per arm, the fraction of items whose amendatory block parsed into
  at least one complete (operation, anchor) triple. **This must be ≥ 0.90 before any headline number is
  reported** — my pilot ran at 11/24 = 0.46 and that is exactly why its confidence interval is wide.

### 7.6 The corpus

- **eCFR search API** — `https://www.ecfr.gov/api/search/v1/results?query="could not be incorporated"`
  and variants, for live editorial notes. **VERIFIED: 92 sections.**
- **eCFR versioner** — `https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{n}.xml?part=&section=`
  for point-in-time section text. **VERIFIED working; note it only covers 2017-01-01 onward** — this cost
  me half my pool and is the reason to add **govinfo bulk CFR annual editions**
  (`https://www.govinfo.gov/bulkdata/CFR`) for pre-2017 sections.
- **Federal Register API** — `https://www.federalregister.gov/api/v1/documents.json`, plus each
  document's `full_text_xml_url` for `<AMDPAR>` elements. **No API key needed.**

**Licence: CLEAN.** All three are OFR/GPO properties under 17 U.S.C. §105. `robots.txt` on all three
returns 200 and disallows only search and auth paths — never document bodies, never the API endpoints a
harvest uses. The Federal Register API publishes exactly one usage restriction and it concerns *logos and
seals*, not text. eCFR states it *"does not link to or contain standards incorporated by reference into
the CFR"*, so the ASTM/NFPA copyright problem does not touch the corpus. **This is the only one of the
three candidates with no licence caveat at all.**

### 7.7 The hard case

**The intra-rule collision**, not the missing anchor. A missing anchor is a single lookup; the tool finds
it and the agent reports it. The hard case is a rule whose instruction 12 removes a paragraph that
instruction 5 already redesignated, so **each instruction is individually valid and the rule is
collectively defective**. That cannot be checked one instruction at a time, which is precisely what
capability 3 exists for and what a single-section script cannot see. Route unresolved collisions to a
named human checkpoint with both readings and the paragraph trace.

### 7.8 The planned removed experiment

**Give the agent the *current* CFR text instead of the point-in-time text.** Pre-registered prediction,
committed before it runs: **accuracy collapses toward a trivial oracle**, because after a *failed*
amendment the current text still lacks the change and after a *successful* one it contains it — the
current text leaks the label. If the number goes *up*, that is proof of leakage, not of capability, and
it must be reported as such. This is a cheap, honest demonstration that the freeze boundary is doing real
work, and it is the single most likely mistake an outside reimplementation would make.

### 7.9 The hot take

> **A verification agent's grounding corpus is a precision instrument, not a recall instrument — and if
> you hand it the document, measure *which class* got better, because the average will lie to you.**

Measured across two corpora in this session, not asserted:

- On IETF errata, giving the agent the specification moved **Rejected recall +12.0 pp and Verified recall
  −4.0 pp**, for a net +4.0 pp that is statistically nothing (p = 0.64); in the three-class variant the
  same access moved the policy class **−16.7 pp** and made the arm *worse overall*.
- On amendatory instructions, giving the agent the CFR text moved accuracy **+27.3 pp**, because the
  baseline there was at chance and the corpus supplies the only fact that decides the answer.

The difference is not the model and not the corpus quality. It is whether the answer is **in** the
document or merely **argued about** by it. Evidence tells you when a claim is false; it rarely tells you a
claim is true, because the claim was written to look true. **Before building retrieval into an
adjudication pipeline, measure the baseline's per-class recall. If the negative class is already strong,
retrieval will buy you an average that flatters and a decision boundary that does not move.**

That generalises without modification to fact-checking, code review, security triage, and RAG over any
corpus of contested claims.

### 7.10 The 24-hour build plan

| Hours | Work | Done when |
|---|---|---|
| **H0–1** | Private repo. `.gitattributes` with `* -text` on line one. **Run logger before any other code**: every arm wrapped in a harness emitting one JSONL trajectory per item — instructions, actions, tool responses, retries, human checkpoints — plus tokens, wall-clock and imputed cost. | A dummy run produces a readable trajectory and a cost row |
| **H1–4** | **The harvest, and it is the risk.** eCFR search for live editorial notes → resolve each to its FR document → **AMDPAR attributor** (this is the part that must be rebuilt: attach every lettered sub-instruction to its section, not just the lead-in) → point-in-time section text, with **govinfo annual CFR editions as the pre-2017 fallback**. | Attributor completeness ≥ 0.90 measured and printed; pool size reported |
| **H4–5** | Build the exact instruction-count-matched pairs. Publish the full exclusion ladder and the count-matching code. Freeze with a SHA-256 manifest and `refetch.py`. | ≥ 40 pairs, balance asserted by a test, manifest verifies from a clean clone |
| **H5–6** | Deterministic scorer (stdlib): accuracy, false-defect and missed-defect rates, attributor-completeness, `success + failure == n`. Ship **B-script** *and its permutation null* — the null is part of the result. | Scorer reproduces 0.5934 with p = 0.185 |
| **H6** | **HEADROOM GATE.** Run B0 (instruction only) once on the full pool. | See branch rules below |
| **H6–7** | Freeze `GOOD.md`: metric, thresholds, the +8 pp target, both guard numbers, the predicted B0 ≈ 0.44 / B0-agent ≈ 0.75 / A1 ≈ 0.85, and the removed-experiment prediction. Commit and timestamp **before A1 exists**. | Pre-registration committed |
| **H7–9** | B0 × 3 and B0-agent × 3 and B0′ × 3. | Baseline table populated, trajectories captured |
| **H9–12** | **Iteration 1 — `anchor_resolve`.** × 3. Changelog row from the measured failure. | Row 1 has evidence |
| **H12–15** | **Iteration 2 — `SKILL.md`.** Measure the tool-availability-vs-tool-use gap explicitly. × 3. | Row 2 has evidence |
| **H15–17** | **Iteration 3 — the rule-level ledger.** × 3. Kept or promoted to removed experiment. | Row 3 has evidence |
| **H17–18** | **Removed experiment: current CFR text instead of point-in-time.** Run, measure against the pre-registered leakage prediction. | Row 4 has evidence |
| **H18–19** | Ablations; final A1 × 3; McNemar and a paired bootstrap clustered by rule (**cluster by FR document — sections from one rule share their label structure**). | Full matrix, failures included |
| **H19–20** | Hot-take measurement: per-class recall deltas from B0 → B0-agent → A1. **Blind human-time study**: resolve 8 items by hand, stopwatched, before looking at gold. | Two numbers, honestly labelled |
| **H20–22** | The artifact: one self-contained static HTML **codification worksheet** — one row per instruction, the anchor, whether it resolved, the matching level, the section text with the anchor highlighted or its absence marked, and the collision trace for multi-instruction rules. No server, opens from the clone. | Opens from a clean clone with the network off |
| **H22–23** | README (user → bottleneck → value → changelog → main failure mode → hot take); reproduction guide, both tiers (Tier 1 replays committed artifacts offline in < 90 s; Tier 2 re-runs live, needs a key, stated runtime and cost). Trajectories packaged with labelled human-intervention points. | Deliverables complete |
| **H23–24** | Clean-clone rehearsal on a second path, network off, manifest verify, Tier 1 replay. | Tier 1 green from a bare clone |

**HEADROOM GATE at H6.** Run B0 (instruction only, no section text) once on the full pool.

- **B0 ≤ 0.60:** proceed as specified. Expected — the pilot measured 0.500–0.545, i.e. chance.
- **B0 ≥ 0.70:** the instruction text is leaking executability. Do not weaken B0. Instead strip the
  instruction's *quoted* anchor text (keep the operation and the designation) and re-run the gate — that
  removes the only plausible leak and the task remains well-posed.
- **Attributor completeness < 0.90 at H4:** stop and fix it before anything else. A pool built on
  truncated instruction blocks produces the exact artifact that made my own pilot report 0.708 instead of
  0.818, and it is not recoverable downstream.

### 7.11 The first ninety minutes

1. Repo, `.gitattributes`, run logger. Nothing else until a dummy run emits a trajectory and a cost row.
   *(45 min.)*
2. `https://www.ecfr.gov/api/search/v1/results?query=%22could+not+be+incorporated%22&per_page=100` and
   its variants; print the total_count for each. Confirm you reach ~92 live editorial-note sections.
   *(20 min.)*
3. Take **one** rule end to end by hand — FR document, AMDPAR list, point-in-time section — and satisfy
   yourself that every lettered sub-instruction attaches to its section. That single hour of manual
   verification is what protects the headline number. *(25 min.)*

---

## 8. What I could not settle

Ordered by how much it would change the recommendation.

**1. The Instruction gap is not statistically established. — MATTERS MOST.**
My pilot is n = 24, of which only **11 had a complete amendatory-instruction block**. On those 11 the
baseline scores 0.545 and the agent 0.818, but Fisher p = 0.36 and McNemar p = 0.375. **A 27-point
difference cannot be established at n = 11 and I am not claiming it is.** What is established is the
*direction* (+21 to +27 pp across both cuts), the *mechanism* (the baseline has no access to the fact
that decides the answer), and that the question is **powerable**: the full exact-count-matched pool is 42
pairs (n = 84), where the same rates would give p = 0.0002. This is why the build's first four hours go to
the harvest and its H6 gate is a real branch and not a formality. If the gap does not survive n = 84, the
project should be abandoned at H6, and that decision should be made before any capability is written.

**2. My AMDPAR attributor is the weak link, and so is the independent one.**
13 of my 24 items carried only the lead-in (`"6. Amend § 1468.23 as follows:"`) because my extractor
dropped the lettered sub-instructions — an agent caught this itself and told me the item should be
regenerated before scoring. The independent harvest hit the mirror image: **25 of 86** confirmed EDNOTE
sections were dropped because no AMDPAR could be attributed to them, and those are disproportionately the
*most spectacular* defects (an instruction naming a section that does not exist). Both losses are
non-random and correlated with the label. The surviving pool is biased toward **subtler** defects, which
is conservative — but the true defective population is not represented, and **no headline number should be
published until attributor completeness is ≥ 0.90 and printed.**

**3. eCFR point-in-time coverage starts at 2017.**
That is why my usable pool fell from 42 pairs to 12: pre-2017 sections return HTTP 404 from the versioner
API. The fallback is govinfo's bulk CFR annual editions (back to 1996), which I did not implement. Until
it exists, roughly half the harvested pairs cannot be given the section text an agent needs, and the
benchmark is smaller than the harvest suggests.

**4. Erratum Gate's negative result is strong but not infinitely strong.**
Four configurations (one prompt no corpus 0.700; one prompt with a 5k excerpt 0.740; agent at five items
per batch 0.740; high-effort agent at one item per batch 0.675) all landed in the same band, and the best
was indistinguishable from the no-corpus arm (p = 1.00). That is much better evidence than the divergent
research's n = 42 pilot, but it is still a *baseline* agent — no purpose-built locate tool, no iterated
skill file, no memory. I am confident enough to not recommend it; I am not confident enough to say no
design could open a gap. If someone builds it anyway, the honest framing is that they are betting against
four measurements.

**5. Contamination on Erratum Gate — probed, not eliminated.**
A recall-framed probe scored 0.7400, identical to the RFC-reading arm, and the model self-reported genuine
recall on **1 of 100** items. Good evidence that the 0.70 baseline is reasoning, not memorisation; not
proof, since a model can use memorised knowledge without recognising it. The clean test — errata submitted
after the training cutoff — has no labels (123 of the 728 unadjudicated are from 2026), so it cannot be
run. The same concern applies in principle to the Instruction candidate and I did not probe it there.

**6. My model-arm protocol is honest but not airtight.**
"One model, one prompt, no tools" was a subagent instructed to make exactly one file read and then stop.
Across every arm in this session, **one** B0 batch on the CROSSCheck queue self-reported
`used_only_the_file: false`; I report its three lines separately (excluding it moves B0 from 97.2% to
97.0% on the remaining 33). There is no API key on this machine, so a genuinely tool-free API call was not
available. Every arm ran on the same frontier model, which is *stronger* than the "off-the-shelf model"
the divergent research used — that alone may explain why my Erratum Gate baseline is 0.70 against its
0.5833, a difference that sits inside its n = 42 confidence interval, so the two are not in conflict.

**7. The CROSS back-pointer number depends on the population, and two agents measured different ones.**
I report **93.9%** (988/1052) of rulings *named as the target of a `revokes`/`modifies` edge* carry a
back-pointer, verified live on a random 25 (23 non-empty, 25/25 cache agreement) and stable across every
year (100% for 2015–2020, 87.7% for 2024, 12.5% for 2025). Another agent reported **2.4%** over a keyword
sample of 500 rulings matching "revoked" — a population dominated by *revoking* rulings, which correctly
have an empty `revokedBy`. Both are right about their own denominators. The kill does not depend on this
(A1 scores 100% via the forward edge alone), but the *premise* critique does, so I state the population
explicitly. The genuine false negatives are real: HQ 951027 (1992) says *"HRL 085384 revoked."* in its
subject and has an empty `revokes` array, and 085384 has an empty `revokedBy` — invisible in both
directions.

**8. My CROSS index is partial.**
18,983 metadata records and 4,200 ruling texts against CROSS's ~221,442 rulings. That bounds the dark-pool
count (1,004 of 1,043 dark edges could not be resolved to both endpoints) and makes the 514-pair clean
pool a lower bound. Neither affects the kill: A1 was measured on a corpus containing every document it
needs, and the freeze-ladder argument is about construction, not coverage.

**9. Competitor census: 45.7% of the field is unreadable.**
37 of 81 repos have no description, 10 have no README, 6 have neither. The defensible claim is *"no lane
competitor among the 71 repos whose content was readable on 2026-08-29"*, not *"no lane competitor
exists."*

**10. Things I chose not to run, and why.**
- A human-expert adjudication sample, which would give the human ceiling on either candidate. It belongs
  in the build's H19–20 human-time study, not in a kill test.
- ATLAS's official HuggingFace artifacts, which return **HTTP 401**. Schema findings come from a public
  mirror whose split sizes (18,254/200/200) match the paper exactly and which is tagged
  `arxiv:2509.18400`. Confidence high, byte-identity unproven.
- A full 221,442-ruling CROSS harvest — hours of work that could not have changed any verdict.
- Erratum Gate's "correct_text appears in the *successor* RFC" attack as originally specified; it needs
  the Obsoleted-By/Updated-By graph. The adjacent proxy (present in the *current* RFC) scored 0.4786 on
  honest CV, i.e. chance, and the prior work's 0.5250 is consistent with that.

**11. Two numbers of my own that I corrected mid-run, and both times the correction mattered.**
- I first reported **103** revocation splits (11.3% of pairs) as evidence CROSSCheck's "hard case" class
  was real. A hand-audit of all 103 found **85 (82.5%) are aggregation artifacts** — the ≥2 codes belong
  to different prior rulings covered by the same revocation notice — leaving **13 genuine same-goods
  splits from 6 documents**. Audit any mechanically-derived positive class before believing its size.
- I read the Instruction agent arm at n = 11 partway through and saw 0.818 with a baseline of 0.375; the
  completed baseline came in at 0.545, halving the apparent gap. Early reads on small samples are worth
  exactly what they cost. Both corrections are in this document rather than behind it.
