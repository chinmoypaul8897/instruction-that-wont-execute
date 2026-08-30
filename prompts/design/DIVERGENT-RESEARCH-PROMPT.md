# DIVERGENT IDEA SEARCH — micro1 Agentic Workflows Hackathon

You are running a **wide divergent search** for hackathon project ideas. Read this whole file, then execute it.

---

## 0. Operating philosophy — read this first, it governs everything

> **"Every ball we throw is not supposed to be hit. Some are to test."**

**Most candidates you generate SHOULD die. That is success, not failure.** Kill fast, kill cheaply, and hand up only what survives.

**Breadth of ANGLE matters more than volume of ideas.** Every competitor has the same AI and the same internet. The edge is *how many genuinely different landscapes you think from*. Fifty ideas from one angle is worthless. Five ideas from eighteen unrelated angles is the whole point.

Three failure modes, all fatal:
- **Converging early.** If your candidate list starts rhyming, you have stopped searching. Force yourself back out.
- **Being polite to your own ideas.** An idea that survives because nobody attacked it is worse than no idea.
- **Manufacturing a challenger.** If nothing genuinely clears the bar in §2.1, say so. A null result is a real result.

**No token or time budget constraints. Go deep. Use many agents. Run workflows.** Depth and breadth both.

---

## 1. Required reading — do this before generating anything

Read these files in full. They are in this repository:

| File | What it gives you |
|---|---|
| `context/01-PROBLEM-PDF.md` | The official brief and the 100-point rubric. **Authoritative.** |
| `context/04-STRATEGY-BRIEF.md` | Verified research on micro1 (the judges) and the competitive field. Which lanes are crowded, which are empty, what micro1 values, which datasets are real, which claims are landmines. |
| `context/02-ABOUT-ME.md` | The contestant's background, skills and gaps. |
| `context/00-MASTER-CONTEXT.md` | Logistics, prizes, deadlines. |

Do **not** read `context/05-FINAL-DECISION.md` or `context/03-IDEA-REVIEW-VERDICT.md`. They contain a prior conclusion and reading them will anchor you. This search must be independent. If you accidentally open one, say so in your report.

---

## 2. The situation

- **micro1 Agentic Workflows Hackathon.** Deadline **31 Aug 2026, 18:00 UTC**.
- Solo entrant. **~26 hours of build time**, plus ~12 hours packaging (video, reproduction guide, agent trajectories).
- Claude Code subscription — agent runs are effectively flat-cost.
- ~7,300 registrants; realistically **400–600 submissions, 80–150 surviving the completeness gate**.
- **Goal is FIRST PRIZE ($5,000).** Not placing. Not participating.
- The judges are micro1's engineering team. micro1 is an **AI data lab that evaluates AI agents commercially** — you are being judged on an agent-evaluation exercise by people who do agent evaluation for a living.

### 2.1 The bar you must clear

A strong incumbent already exists. You are not told what it is — that would anchor you. You **are** told its properties, because a challenger that lacks them is not a challenger:

1. **Zero authored ground truth.** Every label was written by a qualified external body, published, and dated. The contestant selects cases and authors none of them.
2. **The scorer is a dependency-free script with no model in it** — string and date comparison only.
3. **Cheating is structurally foreclosed, not patched.** Memorisation, majority-class, and every degenerate shortcut lose *by construction* because the case design makes the shortcut wrong on one half of the set.
4. **Public-domain data, no licence ambiguity, freezes offline cleanly.**
5. **Zero visible competitors in the lane.**
6. **A simple baseline fails for a reason you can state in advance** — the blindness is structural, not accidental.

**Any candidate you advance must plausibly match or beat all six.** Report honestly how each survivor compares. If none match, say that plainly — it is the most useful thing you could tell us.

---

## 3. Hard filters — a candidate that fails ANY of these is dead

Apply these **before** you invest effort in specifying a candidate. Kill cheaply.

1. **No LLM-as-judge in the primary scoring path.** micro1's CEO calls it circular: *"developing a model to judge domain performance essentially means you've already solved the underlying task."* The primary metric must be deterministic, or grounded in **pre-existing human labels the contestant did not author**.
2. **Public or synthetic data, licence checkable, freezable offline.** A judge must run it from a bare clone with the network off. No accounts, no credentialing, no click-through, no DUA.
3. **≥10 evaluation cases assemblable in under 6 hours**, plus ≥1 genuinely hard case.
4. **THE TRIVIAL-SOLUTION TEST — apply this ruthlessly, it is the most common killer.** Before accepting any candidate, actively try to beat its metric with: a constant, a majority-class predictor, a 20-line script, a lookup table, a regex, or a single off-the-shelf model. *A previous strong-looking candidate died because two hardcoded constants beat its entire pre-registered target.* **If you did not genuinely try to break it this way, you have not tested it.**
5. **Headroom must exist.** A plausible simple baseline must fail in a way you can articulate *before* running anything. If a single good prompt plausibly solves it, it is dead.
6. **Not in the crowded lanes.** See §3 of the strategy brief. Code review / PR gates, résumé screening, incident triage, repo scoring, agent-about-agents meta-tooling, contract review, generic research agents, support triage — all heavily occupied. A candidate in these needs an extraordinary reason.
7. **No collision with shipped prior art.** See the Landmines section of the strategy brief. Do not let the contestant claim novelty on something Anthropic, OpenAI or DeepMind already ships. **Search for prior art before advancing a candidate, not after.**
8. **Buildable in 26 hours by one person**, with at most 3 agent capabilities.
9. **Avoid saturating metrics.** 0% → 100% reads as a rigged baseline. A partial honest gain with the failing class named is stronger.
10. **Survivable domain risk.** The contestant is not a credentialed professional in any specialist field. A candidate is acceptable only if the *ground truth comes from the domain's own authority* — so his lack of expertise cannot produce wrong labels. If winning requires him to make expert judgement calls himself, it is dead.
11. **Demonstrable in 60 seconds of video.** End-to-End Quality is 20 points and a ≤5-minute video is a required deliverable. If the failure the project fixes cannot be *shown* — vividly, on screen, fast — the candidate is weak. Ask concretely: what does the judge SEE?
12. **Rich agent trajectories.** Representative trajectories for every agent are a required deliverable and a gate item. A candidate where the agent does one shallow call produces a thin, unimpressive trajectory. Prefer problems where the agent visibly investigates, uses tools, gets feedback, and changes course.

---

## 4. THE ANGLES — generate from each one independently

This is the core of the task. **Treat each angle as a separate mind that has never heard of the others.** Do not let one angle's output contaminate another's. Spawn separate agents per angle.

For each angle, produce **4–8 raw candidates**. Expect most to die at §3.

**A. Data-first.** Start from datasets, not problems. Hunt for public corpora where *two or more qualified humans labelled the same item and disagreed*. The disagreement IS the ground truth. What exists that nobody has built on?

**B. Statute-and-regulation-first.** Where does law, regulation or a standard create an answer that is objectively checkable — a formula, a deadline, a threshold, a mandatory procedure — and where do professionals still get it wrong?

**C. Time-and-versioning-first.** Where does the correct answer *change over time*, so that a correct-yesterday answer is wrong-today? Superseded rules, deprecated APIs, revised guidance, recalled products, amended standards, withdrawn approvals, expired certifications. What breaks when a system doesn't know the date?

**D. Negative-space / adversarial.** Invert it: what would be *embarrassing* for an AI to get wrong? Where is confident fluency most dangerous? Where does saying "I don't know" have real value — and could abstention itself be the primary metric? (Verified: **0 of 64** visible competitors use abstention as a metric.)

**E. Physical and field operations.** Non-digital work: manufacturing QA, logistics, agriculture, construction inspection, maintenance, energy, transport, food safety. Verified: **0 of 64** competitors are anywhere near physical operations.

**F. Non-English / non-Western institutions.** Regulators, courts, standards bodies and professional systems outside the Anglosphere that publish openly. Where does an entire institutional corpus sit unexploited?

**G. Micro-expertise.** Skilled trades and narrow crafts with real codified standards — welding, electrical code, HVAC, marine survey, aviation maintenance, pharmacy compounding, veterinary. Deep rules, real consequences, no AI attention.

**H. Failure archaeology.** Start from *published lists of real mistakes*: recall notices, incident reports, correction notices, retraction databases, audit findings, enforcement actions, safety bulletins, post-mortems. Someone already did the labelling work — find it.

**I. Economic.** Where does an error cost a specific, measurable amount of money, and where is that cost publicly documented? Money makes the "why it matters" row write itself.

**J. Deterministic-verifier-first.** Invert the design: start from *what can be checked in 20 lines of code with no model* — closed-form formulas, checksums, schema validity, arithmetic identities, graph reachability, date arithmetic, unit consistency, balance equations. Then find the professional judgement task that verifier could score.

**K. Consistency-across-a-series.** Problems where each individual item is correct but the *set* is incoherent — a metric a single stateless prompt structurally cannot win. (Verified: **1 of 64** competitors. The field misread the brief's own example as an audio problem.)

**L. Multi-authority contradiction.** Not two humans disagreeing — two *official sources* disagreeing with each other. Where do two regulators, two standards, two official registries, or an authority and its own prior guidance conflict on the same question? Who currently reconciles that, and how badly?

**M. Constructed ground truth.** Where can truth be generated *by construction* rather than found — inject a known change, corruption, omission or inconsistency into real public material and measure detection? Careful: this risks the "you authored your own exam" attack, so it only survives if the injection is mechanical, published, and the case set is auditable.

**N. Aggregation and rollup.** Where every individual item is answered correctly but the *combination* is wrong — totals that must reconcile, portfolios that must balance, coverage that must be exhaustive, categories that must partition. Distinct from K: this is about composition, not sequence.

**O. Cross-system mapping.** The same real-world thing classified by two different codified systems that must agree or be reconciled — competing taxonomies, code sets, registries, identifiers, or schemas. Where is the mapping published, contested, or broken?

**P. Deliberate anti-crowding.** Ask directly: what would a software engineer *never* pick, that nonetheless fits this brief perfectly? Generate from the space developers are blind to.

**Q. Contestant-asset angle.** Given his actual background — quantitative trading and Indian market data, hospitality operations, e-commerce support, Indian civic and government process, oil and gas drilling, crypto payments, plus a documented adversarial-review engineering method — what could *only he* build credibly? Be honest: if a random strong engineer could produce it, it is not an asset play.

**R. Wildcard.** Ideas that fit the brief but belong to none of the above. Go somewhere genuinely strange. At least 5.

---

## 5. The funnel — execute in this order

**Stage 1 — Diverge.** Run all 18 angles independently, in parallel, isolated. Target **70–120 raw candidates**. Do not filter yet. Do not deduplicate yet.

**Stage 2 — Fast kill.** Apply §3 to every candidate. One or two sentences of reasoning each. **Expect to kill 70–85%.** Record what died and the single reason why — the kill list is a genuine deliverable, because it proves the ground was searched.

**Stage 3 — Verify the survivors' foundations.** For every survivor, **actually fetch the data**. Real HTTP status, real row counts, real licence text, real API response shape. **A candidate whose dataset was not personally verified does not advance.** Kill anything that turns out to be unreachable, credentialed, paywalled, licence-ambiguous, or thinner than claimed.

**Stage 3b — Census the live field.** Before specifying anything, re-run a competitor census against GitHub for repos created since 2026-08-27 mentioning this hackathon, and search for each survivor's core concept. The field has grown since the strategy brief was written. **Kill any survivor that someone has already published.** Report the current repo count so we know how stale the brief's numbers are.

**Stage 4 — Specify.** Take the **8–12** strongest survivors. For each: intended user (a named role with a decision and a clock), bottleneck, why it matters, baseline (a PDF-sanctioned type), compute-matched control arm, the advanced solution with at most 3 capabilities each tied to a failure it fixes, primary metric, why it is not LLM-judged, guard metric with a pre-registered number, eval corpus with exact URLs and licence, the hard case, the planned removed experiment, the hot take. Also state: **what the judge sees in the 60-second demo**, and **what the agent's trajectory looks like**.

**Stage 5 — Attack.** Each specified candidate gets an independent hostile reviewer whose job is to **kill it**, not improve it. The reviewer must personally run the trivial-solution test from §3.4 — try the constant, try the script, try the majority class, try the off-the-shelf model — and must search for prior art. Score against the 100-point rubric row by row. Anything that dies here, dies.

**Stage 6 — Rank and report.** Survivors ranked, each scored against the six properties in §2.1. Be honest about what is genuinely strong versus merely undamaged.

---

## 6. Output — write to `context/06-DIVERGENT-RESEARCH.md`

Write the file directly. Structure it exactly as:

```
# Divergent Idea Search — Results

## 1. How this was run
Angles covered, raw candidate count, kill counts per stage, what you verified yourself,
current competitor repo count from the Stage 3b census.

## 2. The survivors — ranked
For each: full specification, rubric score, crowding, execution risk, how it scores
against the six properties in §2.1, the strongest argument for it, the strongest
argument against it, and what would have to be true for it to win first prize.

## 3. The kill list
Every candidate that died, in one line each, with the reason. Grouped by angle.
This section proves the ground was searched — do not abbreviate it.

## 4. What the angles revealed
Which landscapes were rich, which were barren, and what that says about where the
field is NOT looking.

## 5. Verified data assets
Every dataset you personally confirmed reachable: URL, licence, size, HTTP status,
what it contains, and what it could support. Even for candidates that died —
this is a reusable asset.

## 6. Honest assessment
Did anything here genuinely clear the §2.1 bar, or is this confirming that the
obvious lanes are the good lanes? Say so plainly either way. A null result is a
real result and must be reported as one. Do not manufacture a challenger.
```

---

## 7. Rules of evidence

- Label every factual claim **VERIFIED** (you fetched it — give the URL and what you saw), **INFERRED** (your reasoning), or **UNKNOWN** (you looked, you failed).
- Never present a guess as a fact.
- "I could not find this" is a valuable, acceptable answer.
- Quote short exact snippets with URLs for anything load-bearing.

---

## 8. Final instruction

When you are done, print a **short summary in the chat** — under 300 words — covering: how many candidates were generated and killed, the top 3 survivors in one line each, how many cleared the §2.1 bar, and your honest verdict on whether the search found anything that beats a well-executed obvious idea.

Then stop. **Do not start building anything.**
