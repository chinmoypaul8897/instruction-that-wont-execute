# Verdict: kill the mechanism, keep the problem

*Synthesis of five hostile critiques, six independent rubric scorings, and one verified fact none of the critiques fully priced.*

---

## 0. The fact that changes the argument

Before the verdict, one thing I checked rather than assumed. The insider critic claimed the proposed "advanced solution" already exists in a public repo. It does. `github.com/chinmoypaul8897/nistula-assistance-` is **public**, last pushed **2026-08-18 — ten days before kickoff**. Its README says, verbatim:

> "Before each merge, a multi-agent review pass put independent Claude reviewers on the change set through distinct lenses (money, security, reliability, process), with every finding attacked by separate skeptics before it counted."

And two paragraphs later:

> "…this rigorous review process uncovered **17 blocker-class defects while the test suite remained green** — demonstrating that automated test passage doesn't guarantee correctness."

So the incumbent proposal's **advanced solution** and its **hot take** are both already published, publicly, under your own name, dated before the competition started. Not similar. The same sentence. This is not plagiarism — it is your own work — but ground rule 02 ("make it clear what existed before the competition and what you added") is checked at the **validation screen**, which runs *before* rubric scoring, and integrity failures there are disqualification, not point loss. A judge finds this in one search because the repo is under the same name you submit under.

Every rubric-scored element of the incumbent except the corpus is prior art.

---

## 1. VERDICT

**Survive with modifications — but the modifications delete the two things the proposal is built around.** Keep the problem, the user, the green-suite premise, and the corpus-admission instinct. Abandon the multi-lens/skeptic architecture as the *contribution* (demote it to disclosed prior art), abandon the hot take entirely, and rebuild the project around a mechanism you have not yet published: **findings admitted only by execution**.

Justification, in four numbers:

- **Six independent scorings, mean ~70** (67 / 78 / 68 / 74 / 68 / 66). Six of six said "good, will not win." That is not five people finding five different problems; it is convergence, which is the strongest signal available in this dossier.
- **Tie-break #1 is Agent Solution & Engineering (30 pts).** As proposed, that row scores 19–22 across scorers because persona fan-out plus a critic is the most-implemented multi-agent pattern in existence, and the PDF warns outright: *"Purposeful choices matter more than the number of components."* You cannot win the top tie-break with an architecture you shipped in July and published in August.
- **The hot take row (5 pts) asks for "an observed failure mode turned into a practical lesson for building more reliable agents."** "A green test suite is not evidence of correctness" is Dijkstra 1969, it is a lesson about test suites rather than agents, and — decisively — it is already the closing sentence of your own public README. It cannot be this weekend's insight.
- **The corpus as specified is a 15–20 hour research task inside a 28-hour budget**, producing points in one row. Four of five critics named it the single biggest risk independently.

What survives cross-examination: the problem is a near-verbatim operationalisation of the event's own framing sentence, the green-suite admission criterion is genuinely good eval design, and "every finding must state a concrete failure scenario" is one short step from the mechanism that fixes everything else.

---

## 2. Real criticisms vs. noise

### Convergence table (RJ = rubric-judge, CR = crowding, MI = micro1-insider, FE = feasibility, AL = asset-leverage, SC = independent scorer)

| Criticism | Who raised it | Load-bearing? |
|---|---|---|
| Prose "failure scenario" must become an **executable probe** (fails on buggy rev, passes on fix, harness runs both) | RJ, CR, MI, AL, SC — **5 of 6**, and all five named it the *single highest-leverage change* | **Yes. The most convergent finding in the dossier.** |
| Corpus of live historical repos will eat the build; freeze/buy it instead | RJ, CR, MI, FE, AL, SC — **6 of 6**; named "biggest risk" by RJ, MI, FE, AL | **Yes.** FE measured it: `click` at 2022 and 2024 fails collection under modern pytest; `attrs` fails on a missing dep; each repo needs its own (python, pytest-pin, deps) triple |
| The FP guard has no threshold, no denominator, and **no clean control cases** — so "flag everything" is indistinguishable from a perfect reviewer | RJ, CR, MI, FE, AL, SC — **6 of 6** | **Yes. This is the metric, and it does not currently exist.** |
| Hot take is a truism and aimed at the wrong row | RJ, CR, MI, AL, SC — 5 of 6 (FE dissents) | **Yes**, and now doubly so: it is your own published pre-competition sentence |
| No **compute-matched control arm**; 4–5 calls vs 1 violates §3's "explain any meaningful difference in the resources available to each one" | RJ, MI, SC — 3 of 6, from the three most rubric-literate lenses | **Yes.** A judge at an eval lab asks this in the first 60 seconds |
| n=10–12, single run, no variance = statistically empty | RJ (95% CI on 8/12 ≈ [0.39, 0.94]), MI (McNemar p≈0.25 on 3 discordant pairs), FE, SC (±15pp) | **Yes**, but the fix is honesty + stratification, not a bigger n (see §3) |
| "Anyone merging AI-written code" is a category, not a user | RJ, CR, MI, AL, SC — 5 of 6 | **Yes**, cheap to fix, worth 2–3 pts on a 15-pt row |
| Crowding: "agentic code review" is the modal submission | 6 of 6; CR quantified it at 60–120 diff-review entries, 15–40 multi-lens-plus-critic | **Yes, but it costs attention, not points** — note CR scored it *highest* (78) while calling it most crowded |
| The 17-defect anecdote is a rule-09 liability | RJ, CR, MI, FE, SC — 5 of 6 (AL dissents, wants it shipped as data) | **Yes** — and now it has dated public provenance, which changes the fix (see §3) |
| Prior art is public and undisclosed | MI alone | **Yes — verified above. Single-lens, but factual and it hits the pre-scoring gate.** |

### Noise, or actively wrong

- **AL: "build the corpus from your own repositories."** Refuse this. It inverts ground rule 07 (public/synthetic preferred), creates a rule 08 exposure (production Razorpay/PMS/guest code), makes every case unverifiable by a judge, and is precisely the self-graded exam your own method rejects. AL's other four recommendations are the best in the dossier; this one is the single worst.
- **MI: "20–30 cases × 2–3 arms × 5 seeds."** Not budget-checked. FE measured the advanced arm at roughly 8 min per case; that prescription is 60+ hours of wall clock. The critics collectively prescribe a 45-hour plan for a 28-hour window. Someone has to cut, and it is me.
- **CR: "concede Most Useful Real-World Workflow, aim at Best Engineering Workflow."** Sensible hedging, irrelevant to a stated goal of first prize. The selective awards are not the $5,000.
- **CR: adjacent pivot to spreadsheet/financial-model defects.** CR itself says don't, at T-62h, with no assets there. Agreed.
- **FE's defence of the hot take.** Minority of one, and now falsified by the public README.
- **MI: Cohen's kappa on a hand-labelled adjudication sample.** Becomes near-unnecessary once the probe adjudicates. Keep it as a 30-finding residual audit, not a workstream.

---

## 3. RECOMMENDED DIRECTION

# **Pin** — a review gate that is not allowed to tell you about a bug

*A finding is not a finding until it is pinned: a test that goes red on the bad revision and green on the fix. Everything that cannot be pinned is deleted before a human sees it.*

This is the modified incumbent. Eight things changed; the seven that matter are listed at the end of this section.

**Intended user.** The solo maintainer or two-person team merging agent-authored PRs into a system that moves money or makes promises, with no second engineer and roughly twenty minutes of attention per PR. The green CI badge is the only gate that exists. Name him in the README and price the miss: one unnoticed pricing defect reaching production costs more than the whole review budget for a quarter.

**Bottleneck.** A test suite reports *coverage of behaviours someone thought to write down*. The defects that survive an agent-authored PR are the ones nobody thought to write down — and the reviewer has no way to separate a real concern from a fluent one. LLM reviewers make this worse, not better: they are excellent at writing convincing paragraphs about bugs that do not exist. So the maintainer either merges on the badge or reads twenty findings to find the one that matters.

**Baseline (PDF type 2, one general-purpose agent with basic tools).** One agent, one prompt: *"review this diff; output BLOCK or PASS with file:line."* It gets **file read and a shell** — the same tools the gate has. Do not cripple it. The difference must come from design, not from withheld capability, or §3's fairness clause bites you and the whole result is attributable to tool access.

**Control arm (this is the one the incumbent lacked).** The same single prompt sampled *k* times at the gate's exact call count, findings unioned. This is the "is your architecture just sampling in a costume" test. §3 requires it: *"Explain any meaningful difference in the resources available to each one."*

**Advanced solution (Pin).** Three components, each earning a changelog row, each added in response to a measured baseline miss:
1. **Tool — cross-file resolver.** For every changed symbol, pull its callers and callees into context. This is the mechanism that wins the cross-file cases; persona prompts do not resolve callers.
2. **Skills — 3 lenses**, derived *after* running the baseline and categorising its misses, not chosen up front. Cap at 3. Every lens is +45 min of trajectory packaging.
3. **Verification — the probe gate, enforced in code.** Every surviving finding must emit a test that (a) FAILS on the dirty revision, (b) PASSES on the reference-fixed revision, (c) PASSES on the pre-defect original. The harness runs all three in a container. **Anything that does not flip is discarded before a human sees it.** Output is BLOCK/PASS plus, for each block, a red pytest — not a review essay.

**Primary metric — verified block rate.** On the dirty half of the corpus: fraction of cases where the system emits BLOCK, names a line range intersecting the planted defect, **and** ships a probe the harness confirms flips all three ways. Machine-computed. No LLM judge anywhere in the scoring path.

**Guard metric — false block rate on clean twins**, pre-registered at **≤ 1 in 12**, committed with a timestamp before the first results commit. Flag-everything now loses *by construction*, not by threshold: on a clean twin there is no defect, so no probe can flip.

Report alongside, per §5's table: **human minutes to a merge/no-merge decision** (stopwatched on 3 cases per arm, blind to labels, timed in hour 1 before you have seen the corpus) and **cost per case** (measured tokens converted at published list prices, with the flat subscription disclosed as an imputation — never "$0").

**Report stratified, not blended.** "We tie on local defects; on cross-file the baseline gets 1/8 and Pin gets 6/8" is a defensible claim about a design choice. One blended number with a ±15pp CI is not. Run k=3 seeds and publish the observed range. Almost nobody in this field will report run-to-run variance of an LLM system; for a review gate it is the single most important honest number there is.

**Where the ≥10 cases come from, concretely.** 12 defect cases + 12 clean twins, all **vendored into the repo** as `cases/<id>/{before/, after/, patch.diff, probe_ref.py, ci_log.txt, LICENSE, meta.yaml}`. No judge ever clones a repo, installs a toolchain, or touches the network.
- **3 real-mined cases.** Source: 2–3 tiny pure-Python MIT/BSD repos with zero deps and sub-10-second suites. FE verified `boltons` end to end in four minutes: 432 tests green at the fix commit's parent in 5.6s, and applying only the fix commit's test file yields 1 failed / 432 passed. The bug was live while the suite was green — demonstrable, not rhetorical. FE also found 35 / 52 / 32 fix-with-test candidates across three such repos with a five-line `awk` filter, so sourcing is a rounding error. Hermeticity: delete the fix's test from the shipped case, strip test hunks from the diff, synthesise a plausible commit message, no git log past the parent, no issue refs. Say this procedure out loud in the README or a judge assumes leakage.
- **9 hand-authored cases**, 8 of them cross-file, injected into the same vendored snapshots, each admitted only if **the vendored suite still passes with the defect present**. Do not script them: FE ran 36 mechanical operator mutations across six modules in 82 seconds and **zero survived the suite**. That result is not a setback, it is a free removed-experiment row.
- **Clean twins are free** — the same diff without the defect. They are the FP denominator the incumbent did not have.
- Report **real-mined vs authored catch rates separately.** If Pin scores 90% on authored and 40% on real, that is the most interesting finding in the project and burying it is the integrity failure.

**The hard case (case 12) — the self-inflicted regression.** Two rounds. Round 1 has defect A; Pin blocks it and a fix is applied. Round 2 feeds the *patched* code back through the gate, where the fix has introduced defect B. Does the gate catch the bug its own loop just caused? This is the code-domain isomorph of the PDF's Example 3 memory trap ("each sentence can be correct while the series as a whole no longer feels coherent"), it is the one hard case no other entrant will have, and it is the evidence base for the hot take. Every other multi-lens entry will claim "cross-file" as its hard case; this one is yours.

**Planned removed experiment (two, both already half-measured).**
1. **The skeptic layer.** Predicted null: once findings must execute, adversarial argument adds nothing measurable. Measure it, report the null, cut it. This is honest, cheap, and it pre-empts "critic agents are the LangGraph tutorial" by measuring the objection away instead of defending against it.
2. **Script-mutation seeding.** 36 mutations, 0 survivors, 82 seconds — so the automated seeding half was dropped and the interesting defects had to be written by hand.

**Hot take.** *"The repair round generates defects at roughly the rate the build round does. In my production record, 5 of 17 blockers were regressions introduced by the previous round's own fix. So a gate that runs once is not a gate, it's a speed bump — never seal a fix without re-running the full gate against the fix itself."* This is about building reliable agents (which the row asks for), it is an observed failure mode turned into a design rule, and — critically — **the number in your results table comes from case 12, not from the anecdote.** The 17-defect story becomes the hypothesis; the shipped eval is the evidence. That satisfies rule 09 cleanly, which the incumbent framing did not.

### Exactly what changed from the incumbent, and why

1. **The headline contribution moves from lenses to the probe.** *Why:* 5 of 6 critics named it independently, it is the one element in this design space a professional eval panel says it has not been shown, it converts adjudication from self-grading to machine-checking, and it kills the "just sampling" objection dead — a probe either flips or it does not.
2. **The metric becomes verified block rate on paired clean/dirty cases with a pre-registered false-block ceiling.** *Why:* 6 of 6 said the guard did not exist. §5 requires "good" to be defined before running.
3. **The corpus becomes vendored static fixtures; no judge builds anything.** *Why:* reproducibility is 15 pts, tie-break #2, *and* a gate item — "a project that cannot be run or verified may be disqualified before rubric scoring." Ship three tiers: `--replay` (scores committed transcripts at $0), `--smoke` (one live case, ~$0.30), full run.
4. **A matched-cost sampled control arm is added.** *Why:* §3, verbatim.
5. **The user narrows to a named role with a clock and a priced miss.** *Why:* the 15-pt row asks "who experiences the bottleneck."
6. **The hot take is replaced.** *Why:* the old one is Dijkstra, it is about tests not agents, and it is already in your public README.
7. **Prior art is disclosed in the README's first section and in the video**, with the repo link and the 2026-08-18 push date: *"I shipped this gate in July on a hunch and published the claim. This weekend I tried to falsify it."* *Why:* ground rule 02 at the integrity gate — and because that framing is a better story than "I built a reviewer." It converts your largest liability into the credibility spine.
8. **The name changes.** "Review Gate" gets filed with the other forty in the first three seconds. Lead with the mechanism.

**Realistic score: 84–88**, versus 66–70 as proposed. Strongest on the tie-break rows in tie-break order.

### 28-hour build order

| Hours | Work |
|---|---|
| 0–1 | Decisions (§5), case schema, **pre-registration commit** (metric, ≤1/12 threshold, stopping rule), timestamped before anything runs |
| 1–4 | 5 draft pairs + harness skeleton. **Trajectory logging and token accounting instrumented from run 1 — never retrofit these** |
| **4–6** | **HEADROOM GATE.** Run the baseline on 5 dirty + 5 clean. If it correctly blocks ≥4/5 *with flipping probes*, the case format is wrong: widen the review unit from a minimal reversed hunk to a realistic PR-sized diff and re-check. Half a morning; cheapest insurance in the plan |
| 6–12 | Corpus to 12 pairs, vendored, licensed, provenance-labelled |
| 12–16 | Probe generation + three-way sandboxed flip check + auto-discard |
| 16–19 | Cross-file resolver + 3 lenses |
| 19–21 | Three arms × 24 cases × k=3, checkpointed to disk, 5-wide parallel, baseline cached (it never changes after iteration 0) |
| 21–23 | Ablations: drop each lens, drop the skeptic, probe-off. **These are the changelog rows** |
| 23–25 | CLI (`git diff \| pin`), terse evidence-only output contract enforced in code, one unedited sample in the README labelled unedited |
| 25–28 | Buffer |

---

## 4. RUNNER-UP

**Intake** — screening candidate eval items against OpenAI's public 93-developer annotation panel. Scored 75, the highest of any alternative, low crowding, and the best ground truth available to anyone in this competition (1,699 samples × 3 paid professional annotators, third-party, downloadable). It executes the PDF's own Example 1 technique — *"have qualified reviewers rank ten approved codebases… does the agent come closer to the reviewers' order"* — more rigorously than the example does, with a five-row scoreboard from random floor to human ceiling to oracle.

**Why it lost.** Its thesis is "audit your ground truth," and it does not audit its own. All 500 SWE-bench Verified instances are a strict subset of the 539 non-filtered instances, and Verified-500 membership is a public list with 321k downloads on one mirror alone. Pure memorisation scores 0.867 precision on the headline decision metric — *beating* the 0.804 a real paid annotator achieves. The contamination is not fully removable, because the issue text itself is identifying; blinding the instance ID does not blind "this is a Django issue." And the power is fatal as scoped: bootstrapped 95% CI width on Spearman is 0.33 against a human ceiling of 0.376, so fixing it needs 400–500 held-out instances × 2 arms plus cloning django/sympy/scikit-learn at pinned commits — and the ready-made codebase-content dataset covers only the *clean* Verified 500, i.e. exactly the instances you do not need. Execution risk: high, in 28 hours, on Windows.

**The condition under which Intake is the better choice:** if you decide, in the next 60 minutes and not later, that (a) you are unwilling to ship a corpus where 9 of 12 defects were authored by you, and (b) you would rather carry a permanently-caveated headline number than a self-authored ruler, and (c) you will run the memorisation probe as changelog Iteration 0 and lead the README with it. **The pivot window closes at hour 8.** After that, if the headroom gate fails, re-cut Pin's corpus toward harder diffs — do not pivot into a high-execution-risk project with 20 hours left.

Everything else is out. **Precedent** is dead on arrival: Zheng et al. show a single GPT-4 prompt already reaches ~85% agreement against a ~81% human ceiling on that exact corpus, so the primary metric is a null before you start. **Verdict** has a metric hole in the sentence defending it (rejects count toward coverage, so reject-68 / merge-4 / hold-48 posts 100% precision at 60% coverage while merging 4 of ~60 mergeable patches). **Sharpen**'s held-out split leaks by line co-location, which deflates the exact number its hot take rests on. **Stopwatch** is the cleanest small project and the least crowded, but the improvement is manufactured twice — the baseline is denied a stopwatch then scored with one, and six of twelve cases are self-authored textbook wins — and wall-clock does not reproduce on a judge's machine, which is tie-break #2.

---

## 5. Three decisions to make before writing any code

1. **Am I willing to open the README by naming my own prior art — linking the public `nistula-assistance-` repo, dated 2026-08-18, quoting its multi-lens sentence — and reducing my hackathon claim to the probe layer plus the falsification attempt?** (If no, you are building a project whose architecture and hot take are both publicly pre-dated, and the integrity check runs before scoring.)

2. **Am I willing to ship an eval corpus where 9 of 12 defects were written by me, and defend "you made your own ruler" — or do I want externally-labelled ground truth badly enough to accept SWE-bench contamination and a 400-instance power requirement instead?** (This is the Pin/Intake fork. It is not reversible after hour 8.)

3. **What exact number counts as a win, and will I publish the miss?** Write it down now, commit it timestamped, before you have seen a single result: *"Good = Pin blocks ≥9/12 defect cases with a flipping probe, at ≤1 false block in 12 clean twins, with the matched-cost control below both."* Then answer the harder half: if at hour 6 the one-prompt baseline matches Pin, **do you ship the null and make the changelog the product, or do you re-cut the corpus?** Decide the stopping rule before you have a reason to move it. You are the person who published that a trader's strategy loses ₹1.68 crore and that DrillScribe's models do not transfer — this is the one decision your record says you can actually make.

---

## 6. What makes this submission lose, ranked by likelihood

| # | Failure | Likelihood | What it costs |
|---|---|---|---|
| 1 | **Filed as the fortieth code-review agent in the first twenty seconds.** Judges have Sep 2–4 for 400–600 submissions. Crowding does not lower any row; it decides whether your rigour is read at all | ~70% unless the first sentence and the first 20 seconds of video lead with the probe mechanism, never with "multi-agent review" | The prize, not the score |
| 2 | **Not all four deliverables complete at 18:00 UTC Monday.** Completeness is a gate item; "late or incomplete entries are not accepted." The sleeper is Deliverable 4 — representative trajectories for *every* agent, including the corpus-authoring one, in a format your own dossier flags as one you have never produced | ~50% if trajectory capture is not instrumented in hour 1 | Disqualification before scoring |
| 3 | **Headroom collapse discovered at hour 20.** FE's worked case reduces to flipping `<` to `<=` in a 12-line helper — any competent single prompt finds that. The mining heuristic structurally selects for small, local, unit-testable defects, i.e. the exact class a naive baseline is best at | ~40% without the hour-6 gate; ~10% with it | Measured Improvement (15) craters and the 30-pt row loses its justification |
| 4 | **The judge's numbers do not match the README's.** LLM nondeterminism plus a Windows-authored harness plus no clean-environment test. "A project that cannot be run or verified may be disqualified before rubric scoring" | ~30%, dropping to <10% with replay mode, smoke mode, and a published k=3 range | Reproducibility (15) and tie-break #2, possibly the gate |
| 5 | **The anti-slop clause lands on an artifact that is literally generated prose.** If a sample review opens "Overall the code looks good, but here are some potential issues to consider," the 20-pt row loses 5 | ~30% without a terse evidence-only output contract enforced in code | 5 pts on a 20-pt row |
| 6 | **Ground rule 02 flag on the undisclosed prior art** at the integrity check | ~20% if disclosed in the first section; high if not | Disqualification |
| 7 | **Ground rule 09** — the 17-defect anecdote sitting near a results surface as if it were evidence | ~15% | Integrity flag, and it reads as "I have a great result I can't show you" |
| 8 | **Licence/provenance on vendored third-party code.** Rule 03, and micro1 takes ownership of submissions — so MIT/BSD/Apache only, LICENSE file per case, upstream commit URL recorded | ~10% | Gate risk, free to eliminate |

The one-line summary: **your idea's problem was never the problem. It was that you were planning to submit, as new work, an architecture and an insight you had already published — and to prove them with a corpus that would have eaten two thirds of the clock. Disclose the first, replace the second, freeze the third, and make the probe the whole point.**