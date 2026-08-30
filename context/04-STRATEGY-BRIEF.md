# STRATEGY BRIEF — micro1 Agentic Workflows Hackathon

**Compiled:** 2026-08-29 ~07:00 UTC (T+16h of a 75-hour window) · **Sources:** nine research reports + my own live verification of the competitive census and empty-lane probes, run at 06:57–06:58 UTC today.

**Evidence key:** `[V]` verified on a primary source (URL given) · `[I]` inference/reasoning · `[U]` looked for, could not find.

**One evidence-quality warning up front.** Several "verbatim" micro1 quotes in the underlying research came through WebFetch, which returns a summarising model's reading of the page, not raw HTML. One researcher flagged this explicitly. Anything you quote micro1 on *inside the submission itself* must be re-opened and confirmed character-for-character first. The quotes below are safe to reason from; they are not yet safe to publish.

---

## 1. Who is judging, in their own words

### What micro1 actually is

**`[V]` micro1 is not a recruiting company and has not been one since roughly 2024.** Their own homepage title and H1: *"Data lab to train frontier models & evaluate agents … We're building the infrastructure for advancing intelligence through expert human data, real-world training environments, and contextual evaluations"* — https://www.micro1.ai/

They sell three named products `[V]` (https://www.micro1.ai/):
- **Realm** — RL environments producing expert human data for agentic actions
- **Cortex** — *"The contextual evaluation platform for improving AI agent performance in production"*
- **Robotics** — real-world robotics data

Zara, the AI recruiter, is now the *supply engine* for the data business, not the product `[V]` (https://www.micro1.ai/realm: *"Zara, our AI recruiter agent, sources and vets domain experts at high velocity, forming the human foundation that generates net-new expert data"*).

Scale: `[V]` gross annual run rate went $100M → $500M in eight months to August 2026; net $150–200M after paying experts (https://techcrunch.com/2026/08/20/ai-data-startup-micro1-reaches-500m-gross-run-rate-amid-ai-training-boom/). `[V]` $35M Series A at a $500M valuation, September 2025, led by 01 Advisors (https://techcrunch.com/2025/09/12/micro1-a-competitor-to-scale-ai-raises-funds-at-500m-valuation/). **Do not cite $500M as a current valuation** — TechCrunch hints at a newer round and could not confirm it.

**The one-sentence version: you are being judged by an agent-evaluation company on an agent-evaluation exercise.**

### Their technical vocabulary — use it, sparingly and correctly

These are their words, in their own published material:

| Their term | Where it comes from |
|---|---|
| **contextual evaluation** | Cortex's product category `[V]` |
| **verifier**, **rollout**, **seeding data**, **tasks** | Ali Ansari's four components of an RL environment `[V]` — https://www.micro1.ai/forum/engineers-get-paid-1000-hour-to-do-this-not-coding |
| **reproducible environment · deterministic verification · golden reference solution** | the literal triad in their job specs `[V]` — https://jobs.micro1.ai/post/ca549605-be95-4fe1-b995-40794422b4a5 |
| **failure taxonomy** | their named cure for *"Prompt Whack-a-Mole"* `[V]` |
| **cost per task** | a live column in their production dashboard `[V]` — https://www.micro1.ai/realm: *"performance tracking that measures velocity, error rates, cost per task, and quality in real time"* |
| **completion vs. accuracy**, **pass@3**, **negative criteria**, **restraint** | their published benchmark methodology `[V]` |

### The seven statements that should shape the submission

1. **Evaluation is the hard problem, not intelligence.** `[V]` micro1 features the Forbes headline *"micro1 Shows Why AI's Hardest Problem Is Evaluation, Not Intelligence"* on their own newsroom (https://www.micro1.ai/newsroom).

2. **Pure LLM-as-judge is, in their marketing, "missing the basics."** `[V]` https://www.micro1.ai/cortex lists what teams lack, ending: *"Human expert review beyond automated evals and LLM-as-judge."*

3. **The CEO thinks LLM-as-judge is circular.** `[V]` Ali Ansari, via Forbes: he notes *"a 'chicken-and-egg problem': developing a model to judge domain performance essentially means you've already solved the underlying task."* This is the single most important design constraint in this brief.

4. **Grading is graded, not pass/fail — and you must name a production threshold.** `[V]` Ansari: *"It's not like typical software where you can kind of say like yes or no to whether it works. But more so, like how well does it work, and what are the thresholds we're looking for to go into production?"*

5. **Fluency is not evidence of reasoning.** `[V]` https://www.micro1.ai/benchmark/realm-legal: *"Polished writing can mask weak reasoning; the IRAC decomposition exposes it."* Their rubrics decompose a fuzzy quality judgement into named, weighted sub-skills (issue 4% · rule 33% · application 48% · conclusion 9%).

6. **Failures must be reported next to successes, never blended.** `[V]` https://github.com/micro1-research/longextract-bench: *"completion is a first-class result … a system that quietly fails the hardest documents and posts a high score on the easy ones cannot hide behind a single blended number."* Their grader is *"deterministic and dependency-free … no hand-picked keys, so there is no lever to bias the result."*

7. **Prompt tweaking is their named anti-pattern.** `[V]` https://www.micro1.ai/blog/the-ai-agents-scaling-bottleneck: *"Trying to break through this ceiling with ad-hoc prompt tweaks isn't just exhausting, it's structurally ineffective."* And: *"When a probabilistic system fails, 'it didn't work' is not a usable metric. Teams need to establish structured failure taxonomies."*

### What a submission needs to look like to impress *these* people

A generic hackathon panel rewards a slick demo. This panel rewards evaluation craft. Concretely, the things that will read as fluent to them and to almost nobody else:

- **The eval harness is the deliverable, not the scaffolding.** `[V]` Their careers page: *"the frontier will be defined not only by compute and algorithms, but by the quality of the data, environments, and evaluation systems that guide model development."*
- **Decompose the primary metric into 4–6 named sub-skills with published weights.** Report per-bucket scores so the changelog can say *where* each iteration helped.
- **Include negative criteria** — specific plausible-but-wrong things the agent must not say — and report the trigger rate. `[V]` Realm Financial does exactly this (*"does not report the wrong WACC of 8.5%"*) and found ~1 in 4 still tripped.
- **Report `N_completed` beside the headline number and print a reconciliation line** (`success + failure == n_cases`).
- **Run each case 3× and report pass@3 and variance.** `[V]` Their argument: *"not average performance across a benchmark, but the probability that any single run of the model produces a usable answer on a hard task."*
- **Make the grader deterministic and say so loudly.** If an LLM judge is unavoidable, use a 3-judge majority panel (their RedlineBench method) *and* publish its agreement rate against your own hand labels.
- **Put ONE human checkpoint at ONE named failure mode**, and justify it. `[V]` Their Chief Economist: human expertise belongs *"at the failure modes that genuinely require it, not spread thin across the entire system."* A blanket approval gate reads as compliance theatre.
- **Ship agent instructions as files** — `SKILL.md` + per-task `instruction.md` is literally their RedlineBench layout `[V]`, and the PDF requires "the instructions that shape each agent" as files anyway.
- **Add an "Independence & Fairness" block** with named roles — who wrote the rubric, who made the ground truth, what the baseline got, what the agent got. `[V]` They publish exactly this on LongExtractionBench.
- **Score restraint, not only correctness.** `[V]` https://www.micro1.ai/benchmark/realm-pathology-report: *"The benchmark rewards restraint as much as it rewards extraction … the failures are less about getting facts wrong and more about saying more than the report allows."*

**Who the judges actually are: `[U]`.** No panel is published anywhere. micro1's 461-URL sitemap contains zero hackathon pages; both GitHub orgs expose zero public members. The best available proxies are `[I]` Andrew Maas (VP of AI; Stanford PhD; author of the IMDB Large Movie Review benchmark) and Imran Nasim (VP Research). If Maas reads it, **eval-set construction is what gets scrutinised hardest** — document provenance of each case and why it was included, not just that there are ten.

---

## 2. What the research changes — ranked

### 1. `[V]` **INVALIDATED: "I publish honest negative results" is no longer a differentiator.** It is table stakes.

This was the assumed edge. It is gone. At T+15h a competitor's README already opened with *"**Result: nothing beat one prompt.** … Three of the six agentic additions … made it **measurably worse**"* and *"A late variance check invalidated four of this project's own findings"* (https://github.com/Jamesokooboh/blast-radius). Another leads with *"A **zero-skill constant predictor beats both systems** … The **external validation returned null**"* (https://github.com/adarshcod30/artifact-repro-triage).

Keep the removed experiment — the PDF mandates it. Do not build the pitch around it.

### 2. `[V]` **INVALIDATED: "deterministic verification wrapped around a model" is the single most crowded design pattern in the field.**

The tagline *"— and proves it"* appears verbatim across a dozen unrelated competitor repos. The whole field read the same PDF through the same model and converged on the same move. This is *his* signature move and it is now the field's median move.

**The method is still correct. It cannot be the pitch.** Differentiation has to come from the problem and the metric.

### 3. `[V]` **The tie-break order is the real objective function, and it is published.**

From the HackerEarth page, verbatim: **1. Agent Solution & Engineering → 2. Reproducibility → 3. Measured Improvement → 4. End to End Quality.** At the top of the distribution, scores cluster; this ordering picks 1st from 3rd. The marginal hour goes to design rationale and a bulletproof reproduction path — not to the idea or the UI.

### 4. `[V]` **The hackathon is an RL-environment-authoring audition.**

Both job postings linked from the prizes section are the same job. From the "Open Source Contributor" post (https://jobs.micro1.ai/post/dcb37b06-8e05-434d-ac22-372a4c04cefc): *"create reproducible rl environments that test a model's ability to solve these workflows along with a golden reference solution."* Their newest engineering posting (2026-08-24, four days before kickoff) adds: *"You will design reproducible environments, deterministic verification, and golden reference solutions."*

The four deliverables map 1:1 onto an RL-environment task submission. Package it that way and use those three as literal README headings.

### 5. `[V]` **Cost per task and human time per task are almost universally skipped — and they are micro1's own dashboard columns.**

Only **two** repositories on all of GitHub contain both phrases `"cost per task"` and `"human time per task"`, and both are micro1 hackathon entries. The PDF puts both in its suggested results table. Roughly two hours of instrumentation, near-free differentiation, and it is retrofit-hostile — do it from run one.

### 6. `[V]` **A saturating metric is a scoring liability, and several leaders have one.**

Visible competitor results include 0/11 → 11/11, 42% → 100%, 0% → 97%. Judges are explicitly instructed to check baseline fairness (*"Explain any meaningful difference in the resources available to each one"*). A perfect score on a self-authored case set reads as a baseline set up to fail. **58% → 79% with the failing case class named** is a harder result to build and a much harder one to dismiss.

### 7. `[V]` **The real field is ~100 serious competitors, not 7,300.**

Registrations are 7.3K and climbing (registration closes 23:59 UTC today). Comparable completion rates: GitLab 600+/7,000 = 8.6%; Microsoft 570/18,000 = 3.2%; DataHub 550/3,073 = 17.9%. `[I]` Expect 400–600 submissions and **80–150** that survive a completeness/integrity/trace/reproducibility gate. **Completeness beats brilliance at the margin.** A missing trajectory file is a total loss; a slightly weaker metric is a few points.

### 8. `[V]` **No organiser guidance exists and none is coming.**

The "Details" tab now links the same PDF you already have. The person answering questions publicly (u/AromaticFood83) states outright: *"no, no trabajo como Dev, no se que requerimientos tienen ellos."* The Aug 27 pre-event briefing left no public trace anywhere. **Stop waiting. Resolve every ambiguity by writing your interpretation into the README** — the PDF's own "define what good looks like before you run it" clause is your cover.

### 9. `[V]` **micro1 commercially buys agent traces.** $2–15/trace for this event, plus a standing role at $80–100/hr for curating *"session traces from local or agentic AI tools … documenting research methodologies, problem-solving approaches, and points of human intervention."*

The trajectory deliverable is the artifact closest to their commercial interest. Format it as a product with labelled human-intervention points, not a terminal dump. `[I]` It is also the deliverable most likely to be missing or unusable across the field, because nobody has produced this format before — including him.

### 10. `[V]` **INVALIDATED: framing anything around "micro1 the AI recruiter."** Two years out of date. And candidate evaluation specifically is Zara's job — 3,000+ interviews daily, with a published paper.

---

## 3. The field

**Base rates that anchor everything below `[V]`:** the DataHub Agent Hackathon (3,073 registrants, ended 10 Aug 2026) produced 550 submissions of which **40.2% shared one theme**. Two taglines scraped adjacently were functionally the same sentence. That is the empirical convergence rate for "500 people read one open-ended brief."

**My own live census `[V]`, run 2026-08-29 06:57 UTC:**
- 64 public repos mention micro1 and were created since Aug 27 (was ~61 at 06:24 UTC — roughly +3 per half hour)
- 43 repos contain "Agentic Workflows Hackathon" in the README
- 19 contain "Frontier Engineering Challenge"

Of the 64 visible entries, **roughly 40 (≈62%) name a developer, SRE, data engineer or ML engineer as the user.** Engineers are building agents for engineers.

**Caveat on everything in this section `[I]`:** these are public, GitHub-indexed repos at T+16h. Private repos and late starters are invisible. Early public pushers skew toward experienced builders; the long tail (résumé screeners, support chatbots) will surface late.

### Ranked duplication forecast, per ~500 real submissions

| # | Cluster | Est. count | Live evidence at T+16h |
|---|---|---|---|
| 1 | **Code review / PR gate / diff analysis** | 55–85 | blast-radius, patch_guard, diffradius, evidence-driven-engineering-agent |
| 2 | **Résumé / candidate screening** (Example 2 clones) | 40–65 | mostly still private; the XPRIZE gallery shows career/résumé at 5% of a general field |
| 3 | **Incident / log triage / root-cause** | 35–55 | incident-engineer, traceguard, cloud-sre-autoheal, FrontierChallenge26 — **two are near-identical twins built independently** |
| 4 | **Repo quality scoring / codebase valuation** (Example 1 clones) | 30–50 | repoguard, repoguard-ai, repowiki, codecat, artifact-repro-triage |
| 5 | **Agent-about-agents meta-tooling** | 30–45 | taskgate, confess, rewardgate, fairtask, benchmark-forge, Creative Court, artifact-repro-triage — **7 of 64 already** |
| 6 | **Contract / legal / policy review** | 25–40 | saksama, contractguard-ai |
| 7 | **Generic deep-research agent with citations** | 25–40 | ai-research-agent-hackathon |
| 8 | **Customer-support ticket triage** | 20–35 | hackathon-customer |
| 9 | **Migration / upgrade agents** (SDK, framework, language) | 15–30 | php-upgrade-agent, expo-upgrade-agent |
| 10 | **Test generation / bug repro / flaky tests** | 15–25 | flake-doctor, Repro-Bot |
| 11 | **Text-to-SQL with self-verification** | 15–25 | — |
| 12 | **Security scan / dependency / config audit** | 12–25 | rlsguard, org-drift-sentinel |
| 13 | **Invoice / ledger / settlement reconciliation** | 12–25 | qazisaad21/frontier-challenge-2026, settlement-reconciler, recount-micro1 |
| 14 | **Data-pipeline / schema-drift / contract-drift** | 10–20 | micro1-chaos-agent |
| 15 | **Medical / mental-health triage** | 8–18 | — |
| 16 | **Cross-item consistency / translation** (Example 3 clones) | **2–6** | exactly **1** of 64 |

### The near-empty categories

Verified by my own probe of repos created since kickoff `[V]`, plus inspection of all 64 competitor descriptions:

| Category | Occupancy | Probe result |
|---|---|---|
| **Vulnerability triage / CVE severity enrichment** | **0 of 64** | `cve cvss agent created:>2026-08-27` → **0** |
| **Rank correlation against an expert panel** (Example 1's *technique*) | **0** | `spearman rank correlation agent` → **0**; `"human panel" agent baseline hackathon` (code) → **0** |
| **Abstention / "knows what it doesn't know" as the primary metric** | **0** | `abstention agent created:>2026-08-27` → **0** |
| **Cross-item consistency over an ordered series** | **1 of 64** | `glossary consistency` → **0** |
| **Forecasting / calibration as the primary metric** | **1 of 64** | one entry: `Dnlofreitas/micro1-agentic-forecast` |
| **Non-English / multilingual professional judgement** | **2 of 64** | saksama (Indonesian labour contracts), apura (Brazilian gazettes) |
| **Regulated non-software expert domains** (clinical coding, insurance adjudication, tax treatment, manufacturing QA, customs classification) | **~0** | no entry in the 64 touches any of these |
| **Physical / field operations** (drilling, logistics, hospitality ops) | **0 of 64** | — |

Two structural observations:

`[I]` **Why Example 3 is empty despite being handed out for free.** It is the only appendix example that *appears* to need audio, ASR and multi-hour media. Entrants read "podcast translation" as an infrastructure problem and skip it. That reading is wrong — the *technique* (a metric only a memory-carrying system can pass) ports to any ordered text corpus. The perceived barrier is not real, which is exactly why the category stays empty.

`[I]` **The meta lane is a trap, not an opportunity.** "Build something that looks like micro1's own business" is the obvious flattery move and seven people made it. One of them (taskgate's author) claims to do this professionally — a domain-authenticity contest you would lose.

---

## 4. Open lanes

Ranked by **differentiation × feasibility in 28 build hours**. Every dataset below was verified reachable by a researcher who actually fetched it.

### Tier 1 — best ratio

**1. NVD CVE → CVSS severity enrichment with evidence-cited retrieval**

- **The bottleneck is government-announced and four months old.** `[V]` https://www.nist.gov/news-events/news/2026/04/nist-updates-nvd-operations-address-record-cve-growth — *"Starting on April 15, 2026, we will prioritize the following CVEs for enrichment … we will move all backlogged CVEs with an NVD publish date earlier than March 1, 2026, into the 'Not Scheduled' category."*
- **A two-to-three-expert panel already exists in public JSON.** `[V]` The NVD API returns both a `Primary` (NVD analyst) and `Secondary` (CNA) CVSS assessment for the same CVE: https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2024-3094
- **Measured disagreement, reproducible in one curl.** `[V]` Of 495 CVEs published 1–15 Jan 2025 carrying both vectors, **379 (76.6%) diverge**. Independently corroborated: `[V]` https://arxiv.org/html/2607.05670v1 — *"73% of public CNAs have at least one diverging assessment from the NVD."*
- **A third assessor, CC0.** `[V]` https://github.com/cisagov/vulnrichment (CISA ADP container, **CC0-1.0**).
- **Bulk corpus, git-cloneable.** `[V]` https://github.com/CVEProject/cvelistV5 — daily midnight baselines; licence is the CVE Program Terms of Use (**see landmines — the exact wording is `[U]`**).
- **A published, weak, citable external baseline.** `[V]` https://arxiv.org/html/2512.06781 — GPT-5 scoring CVSS from description alone gets 71.6% on Privileges Required, 68.0% on Availability Impact, and *barely* beats the majority-class baseline on Attack Complexity (84.66% vs 83.85%). The authors name the missing ingredient as **context** — which is precisely what an agent adds.
- **The score is a closed-form formula**, so a deterministic verifier can mechanically reject any vector whose stated score doesn't match. Verification becomes load-bearing, not decorative.
- **`[V]` Occupancy: 0 of 64 visible entries.**

**2. Cross-item consistency over an ordered professional corpus (any text domain)**

- Not a dataset — a *technique*, and the brief hands it out: `[V]` PDF Example 3, *"Include one case that depends on a recurring detail."*
- Needs only an ordered corpus of 10+ related documents where an earlier decision binds later ones — a glossary, an entity name, a unit convention, a prior ruling, a recurring policy.
- Gives you a metric a single prompt **provably cannot win**, the mandatory hard case for free, and the cleanest possible justification for "memory" without kitchen-sinking the other five capabilities.
- `[V]` Occupancy: 1 of 64.

### Tier 2 — strong, with one named caveat each

**3. Survey of Professional Forecasters microdata — forecaster disagreement / calibration**
`[V]` https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/historical-data/SPFmicrodata.xlsx (24.6 MB, HTTP 200 confirmed). Per-forecaster responses back to 1968; realised outcomes from FRED. Public domain (US Federal Reserve).
**Why it's good:** a genuine named expert panel *and* objective ground truth — a rare combination. The PDF explicitly blesses calibration as a primary metric (*"a forecasting team may focus on calibration"*). Occupancy: 1 of 64.
**Caveat:** you must construct the agent's task carefully or it collapses into a time-series regression, which is not an agentic problem.

**4. NASA Aviation Safety Reporting System — analyst coding of free-text narratives**
`[V]` https://asrs.arc.nasa.gov/search/database.html — CSV export, 10,000 records per download, US-government public domain. *"expert analysts create coded information from the original report."*
**Why it's good:** trained analysts assigning taxonomy codes (Anomaly, Human Factors, Primary Problem) to pilot narratives is a genuine judgement call, on genuinely open data, in a vertical nobody in the field is near. Vivid on video.
**Caveat:** one analyst label per report — you measure agreement with a single expert, not a panel.

**5. Chicago Food Inspections + the Stanford RegLab RCT**
`[V]` https://data.cityofchicago.org/api/views/4ijn-s7e5.json — 314,675 rows, live Socrata API, inspector free-text plus a Pass / Pass-w-Conditions / Fail verdict.
**The best problem statement in the entire research corpus:** `[V]` https://reglab.stanford.edu/publications/does-peer-review-work/ — *"observing identical conditions, inspectors disagreed 60% of the time"*, from an RCT over 28,000 inspections.
**Caveat — this is a licence item, not a nitpick:** the licence field reads `SEE_TERMS_OF_USE`. It is **City of Chicago Terms of Use, not an SPDX open licence.** Ground rule 03 is checked at the qualification gate. Say so explicitly.

**6. SEC EDGAR staff comment letters (UPLOAD / CORRESP)**
`[V]` https://efts.sec.gov — 1,563 UPLOAD letters in Q1 2025 alone; CORRESP gives the registrant's reply. US-government public domain.
**Why it's good:** "which disclosure will SEC staff question, and why" is a real, inconsistently-made judgement call with a public regulator record, and essentially nobody builds on it.
**Caveat:** ground truth is one-sided — you see the comments issued, never the filings staff silently passed. False-positive rate is not cleanly measurable. Disclosable, but it caps the rigour.

### Tier 3 — good data, worse fit

- **SYNERGY systematic-review screening** — `[V]` https://github.com/asreview/synergy-dataset, **CC0-1.0**, `pip install synergy-dataset`, 26 reviews / 169,288 records / 2,834 included, with eligibility criteria shipped alongside. Technically the *cleanest* option. `[I]` Demoted because the ASReview community has benchmarked this for years and "LLM screens abstracts" is a well-worn demo.
- **W3C ACT Rules test cases** — `[V]` https://act-rules.github.io/testcases.json, 1,134 cases across 91 rules, W3C licence, with a third marked `inapplicable` (where human auditors over-report). Excellent hard cases. But `curbcut` already occupies WCAG in this field, and the ground truth is deterministic, which weakens the "contested judgement" framing.
- **CUAD** — `[V]` https://arxiv.org/abs/2103.06268, **CC BY 4.0**, Zenodo record 4595826, 510 contracts / 13k attorney labels. Clean and licence-safe, but it is the single most reached-for legal NLP dataset and two contract entries are already public.
- **USPTO Office Action Research Dataset** — `[V]` https://data.uspto.gov/bulkdata/datasets/ptoffact, 4.4M office actions, public domain. Examiner variance is one of the best-documented inconsistent-expert phenomena in law and economics. Corpus is heavy; prosecution context is hard to reconstruct in 28 hours.
- **ICLR peer-review dataset** — `[V]` https://github.com/berenslab/iclr-dataset, **MIT**, 55,906 submissions, published reviewer agreement r = 0.40. Great data. `[I]` Risky: the judges live inside this system and "AI reviews AI papers" is well-worn.
- **CFPB Consumer Complaints** — `[V]` https://files.consumerfinance.gov/ccdb/complaints.csv.zip, explicitly free to reuse. No second expert per case, so the inconsistency framing must be built rather than found.

### Domains that look attractive and have no usable public data `[U]`

Searched for specifically and **not found**: hospitality/PMS guest-complaint severity; e-commerce support escalation with expert adjudications; GST Advance Ruling contradictions (real phenomenon, **no bulk download** — individual PDFs behind a per-order search); Central Information Commission RTI decisions (no bulk dataset); Medicare Part C/D claim denials (aggregate rates only); ECHA C&L divergent classifications (9,999-row UI export cap, no API); CPGRAMS (ministry-level aggregates only); GAO bid protests (no bulk download, and GAO states most dismissals are unpublished).

**Equinor Volve** `[V]` (https://www.equinor.com/energy/volve-data-sharing) is the only genuinely open oil & gas operational corpus, but the licence is bespoke (Equinor Open Data Licence, not SPDX) and re-entering the drilling domain repeats prior work rather than showing range.

**NSE India** `[V]` is reachable programmatically from his machine (corporate-announcements API and bhavcopy both returned HTTP 200 with a cookie jar). But NSE serves bot defences and a judge in another jurisdiction may get nothing. **If this route is taken, vendoring a frozen dated snapshot into the repo so the eval runs with the network off is not optional — it is the difference between 15 reproducibility points and 0.**

---

## 5. Landmines

### Solved problems that must not be presented as novel

All of these are shipped products or published papers. Claiming any of them costs more than it gains:

| Claim | Who already did it |
|---|---|
| AI code reviewer that verifies findings before posting | `[V]` Anthropic ships it. https://code.claude.com/docs/en/code-review: *"multiple agents analyze the diff … then a verification step checks candidates against actual code behavior to filter out false positives."* **The judges use Claude Code. They will know.** |
| Sandboxed exploitability validation | `[V]` OpenAI Aardvark ("Validation Sandbox", 92% on golden repos) |
| Multi-modal automated patch validation | `[V]` DeepMind CodeMender (differential testing, fuzzing, SMT solvers, LLM critique; 72 fixes upstreamed) |
| Code review that runs your app | `[V]` Ito (https://www.ito.ai/) — funded commercial product |
| Two-stage detect-then-filter review | `[V]` ByteDance BitsAI-CR (arXiv 2501.15134, 75% precision, 12,000 WAU) |
| Turning review comments into executable tests | `[V]` c-CRAB benchmark, March 2026 (arXiv 2603.23448) — 184 PR instances, 234 tests, 67 repos |
| Generating a reproduction test from an issue | `[V]` **Near-solved.** SWT-Bench leaders at 84–89% (https://swtbench.com/) |
| Second-LLM hallucination filtering of review comments | `[V]` HalluJudge at Atlassian, F1 0.85, $0.009/assessment |

`[I]` **The one seam that is still open in this lane:** executional proof exists for *security exploits* and *runtime/UI regressions*; argumentative self-critique covers everything else. Ordinary non-crashing **logic defects in a diff** sit in the gap. And **no source publishes precision-conditional-on-proof alongside the recall the gate costs.** That is narrow, real, and unclaimed.

### Contaminated benchmarks — do not evaluate on these

- **`[V]` SWE-bench / SWE-bench Verified.** arXiv 2410.06992: *"32.67% of the successful patches involve cheating … 31.08% of the passed patches are suspicious … from 12.47% to 3.97% … over 94% of the issues were created before LLM's knowledge cutoff."* Second, independent memorisation result — arXiv 2506.12286: 76% buggy-file-path identification *inside* the benchmark vs 53% outside.
- **`[V]` Even passing tests aren't proof.** arXiv 2503.15223: 7.8% of "correct" patches fail the developer test suite; 29.6% behave differently from ground truth; reported rates inflated by 6.2pp. **Pre-empt this: a passing test is evidence, not proof.**
- **`[V]` Agent benchmarks are broken generally.** arXiv 2507.02825: of ten audited benchmarks, seven violated task validity and seven violated outcome validity; τ-bench overestimates by 38%.

### Licence traps

- Chicago food inspections: **Terms of Use, not SPDX**. Say so.
- Equinor Volve: **bespoke licence**, not CC-BY.
- MIMIC-IV / n2c2: credentialing plus a DUA — **days of latency**, fatal at 28 hours.
- `[U]` **NVD's own terms page and the CVE Program Terms of Use page are Cloudflare/JS-blocked to fetchers.** The exact wording is unverified. If the CVE route is taken, **open it in a browser and read it before writing the licence section** — this is a gate item.
- `[V]` micro1 owns submissions per the Hackathon Participation Agreement and may use them for AI model training and evaluation. Not a trap, but decide knowingly.

### Known judge irritations, evidenced

1. **A pure LLM-judge metric.** Cortex calls it "missing the basics"; the CEO calls it chicken-and-egg.
2. **A changelog of prompt tweaks.** *"structurally ineffective"*, in their own words.
3. **"It didn't work" as a failure report.** They want a named taxonomy.
4. **Stacking capabilities.** `[V]` The PDF: *"Purposeful choices matter more than the number of components."* Corroborated by their own pathology finding: *"longer runs do not buy accuracy … The most over-produced traces — 10–20 tool calls, repeated planning loops — were frequently the lowest-scoring."*
5. **A self-serving metric.** The self-designed-rubric escape hatch is the biggest lever in the PDF and the most obvious trap. Their antidote, quotable: a grader with *"no hand-picked keys, so there is no lever to bias the result."*

### Domain traps

- **Candidate evaluation** (Example 2). `[V]` Zara does 3,000+ interviews daily, has a published paper and a randomised field study. Unwinnable in 28 hours.
- **micro1's own six benchmarked domains**: legal reasoning, pathology reports, financial reasoning, tax, contract redlining, long-document extraction. Building there invites silent comparison against work the judges know intimately.

### Own-goals that fail the *gate*, not the rubric

Private repo · video not publicly viewable · secrets anywhere in git history (ship a `.env.example`; scan history) · single-commit repo (a listed disqualifier elsewhere, and Rule 02 asks what pre-existed vs. what you added) · `node_modules` committed — **`[V]` one competitor has already done this** · missing trajectories for any agent · video uploaded at 17:50 UTC (`[V]` Devpost warns YouTube processing can take *"several hours or more"*).

### One operational security note

`[V]` I found 64 competitor repos in under ten minutes of API queries. Anyone doing the same research will find yours. There is no upside to a public, descriptively-named repo before Aug 31 18:00 UTC, and a real downside in handing a distinctive framing to a field that is already converging.

---

## 6. The five strongest directions

Ranked by (differentiation × feasibility in 28h × defensible personal standing). Deliberately unspecified — a separate process picks and scopes.

**1. CVE severity enrichment with evidence-cited retrieval and explicit abstention.**
A government-admitted bottleneck four months old, a two-to-three-expert panel already sitting in public JSON, 76.6% measured expert disagreement, a published weak baseline whose authors name *context* as the missing ingredient, and a closed-form scoring formula that makes deterministic verification load-bearing rather than decorative — with zero visible competitors.

**2. Cross-item consistency over an ordered professional corpus, in text rather than audio.**
The only appendix technique the entire field skipped (1 of 64 entries), because everyone misread "podcast" as an ASR problem — and it yields the one class of metric a single prompt structurally cannot win, which converts "memory" from a bolt-on into the thesis.

**3. Analyst-grade coding of free-text safety or inspection narratives in a regulated non-software vertical.**
Trained government experts demonstrably disagree on identical facts (60%, RCT-backed), the corpora are public-domain and already expert-labelled, and nobody in the visible field is within a mile of a regulated non-software domain — so the 15-point "who has this problem" row is uncontested.

**4. Professional-forecaster disagreement and calibration adjudication.**
The brief explicitly names calibration as a legitimate primary metric, the SPF microdata supplies a rare combination of a real named expert panel *and* objective realised outcomes, and only 1 of 64 visible entries touches forecasting at all — while sitting closest to his genuine quantitative standing.

**5. Evidence-gated defect review that publishes its own recall cost.**
The single seam left open in the most crowded category — executional proof exists for exploits and runtime regressions but not ordinary logic defects, and nobody publishes precision-conditional-on-proof beside what the gate silently discards — which is also the only direction where his existing guardrail work transfers with zero translation.

---

## 7. What we still do not know

| Gap | Status | Worth more time? |
|---|---|---|
| **Who the judges are** | `[U]` No panel published anywhere. 461-URL sitemap: zero hackathon pages. Both GitHub orgs: zero public members. Reddit/X/LinkedIn hard-blocked. | **No.** Genuinely unfindable. Write for a reader who has personally built benchmark datasets and assume the highest technical bar. |
| **What the Aug 27 pre-event briefing said** | `[U]` No recording, slides, notes or participant summary anywhere. Not on micro1's YouTube (all 65 videos enumerated), not on Reddit, not on dev.to. | **Marginal.** One email to yeison@micro1.ai costs two minutes; the PDF plus the post-kickoff Reddit update almost certainly cover it. Do not wait on a reply. |
| **How many judges, how long per submission** | `[U]` No micro1 statement. GitLab's 19 judges / 18 days for 600 entries is a proxy only. | **No.** Assume a first pass measured in minutes and build the README's first screen accordingly. |
| **Exact NVD / CVE Program licence wording** | `[U]` Both pages Cloudflare/JS-blocked to fetchers. | **Yes — 5 minutes, in a browser,** but only if the CVE route is taken. It is a qualification-gate item under ground rule 03. |
| **The private half of the competitive field** | `[U]` Unknowable. My census sees public, GitHub-indexed repos only. | **Yes, cheaply.** Re-run the two search queries once before locking the video script — two minutes, and it tells you whether anyone landed on your framing. |
| **What separates 1st from 5th in a rubric-scored hackathon** | `[U]` No published score distributions exist for *any* comparable event. Winner write-ups and judge quotes only. | **No.** The published tie-break order is a better guide than any external data would be. |
| **Whether Claude Code's verification step actually executes code** | `[U]` The docs say *"checks candidates against actual code behavior"* — they do not say whether that means running it. | **Only if direction 5 is chosen**, where it decides the novelty claim. Flag as unknown rather than assuming favourably. |
| **Forbes / Inc. profiles of Ali Ansari** | `[U]` HTTP 403 to every fetcher tried. Only search-snippet paraphrase obtained; the "truth vs. taste" framing is indicated, not verified. | **No.** micro1's own site covers the same ground with quotable primary text. |
| **Whether a 2026 funding round closed** | `[U]` TechCrunch says "may have recently raised"; Tracxn and Sacra still show the Sept 2025 round. | **No.** Just never cite a valuation. |
| **micro1 headcount** | `[U]` Vendor estimates range 101–250 to 8,516; they measure different populations (staff vs. contractor network). | **No.** Never cite a headcount. |
| **micro1's rubric for evaluating code or SWE agents** | `[U]` **None exists.** Searched directly. All six published micro1 benchmarks are professional-judgement work products. | Not a gap to close — it is a **signal**. `[I]` Appendix Example 1 was written aspirationally; micro1 has no in-house prior art on code evaluation, and a judgement-heavy professional task will resonate more than a code-quality tool. |
| **Whether his cost-per-task will be competitive** | `[U]` Unknown until instrumented. Reference points: a competitor reports $0.007/task and another $0.49 for an entire project; Anthropic's own PR review is $15–25. | **Yes, immediately.** If it lands in dollars rather than cents it will look bad in side-by-side judging, and it is retrofit-hostile. |

**One last honest note on the corpus.** Nine reports, high internal consistency, and the two most decision-relevant claims — that the field has converged on deterministic-verification-plus-honest-negative-result, and that Example 3's technique is untouched — I re-verified myself this morning and both held. The weakest link in the whole evidence base is that nobody could read a single spoken word from Ali Ansari, Andrew Maas or Imran Nasim: every YouTube transcript route returned 403, X is inaccessible, Nitter is dead, LinkedIn serves HTTP 999. Everything about how these people talk comes from written marketing and press paraphrase. Treat the cultural read as strong but second-hand.