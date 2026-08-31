# The Instruction That Won't Execute

**An agent that reads a Federal Register amendatory instruction the way the Office of
the Federal Register does — and writes the editorial note NARA will have to publish if
the rule ships as drafted.**

The headline result is a null. A1 beats the strongest baseline by **+6.1 pp**, at
**p = 0.4244**, on **n = 82**. That is **not significant**, and the pre-registered success
criterion is **not met on any of its four clauses**. The criterion was written before
any model ran and it was not moved. What the project did find is smaller, stranger and
more useful. **Measured one at a time, neither capability helps. Measured together they
land +17.1 pp above the sum of their separate deltas.** The single-capability arms are one
rep each and A1's own rep-to-rep spread is 4.9 pp, so read "neither helps alone" as *not
distinguishable from no effect*, not as a measured harm.

Reproduce all of it offline, in under half a minute, for nothing: **[REPRODUCE.md](REPRODUCE.md)**.

---

## a. The user, the bottleneck, and why anyone should care

A regulations drafter, or an Office of the Federal Register liaison, clearing a final
rule for publication. The decision is per section and it is binary: **will this
amendatory instruction codify?** The clock is the rule's statutory or court-ordered
effective date.

If the instruction is defective, OFR cannot incorporate it. The CFR text never changes.
NARA publishes a permanent, citable editorial note recording that the agency's rule did
not take effect as written. The remedy is a correcting document: another Federal Register
cycle, months later, for a paragraph letter.

An amendatory instruction is **an anchor plus an operation**. *In paragraph (b)(4),
remove "shall" and add "must".* It executes if and only if the quoted anchor is present
in the codified text exactly as quoted, and the target designation resolves at the right
level of a nested hierarchy. The drafter writes against the text she believes is
codified. OFR executes against the text that actually is.

**An amendatory instruction carries no evidence of its own executability.** You cannot
tell by reading it. You can only tell by resolving it against the text.

**What this is not**, from the specification's own non-goals (`CONTEXT.md` §1). Not a
legal-advice tool: the output is an input to a drafter's judgement, never a filing. **Not
a classification-accuracy benchmark** — nothing here measures whether the *substance* of a
rule is right, only whether its instructions will execute. And not a general CFR
question-answering system.

### The generalisation, which is the reason this is not a niche

The shape underneath is **a batch of edits, each individually valid, that fail when
applied to the real target.** Database migrations written against a schema that has
moved. Refactors against a file someone else has already touched. Config rollouts and
infrastructure-as-code against drifted state. Every one of them is a set of anchored
operations validated in isolation and executed against reality.

The Federal Register is not the point. It is the one domain where this problem has
**public, government-authored ground truth**. NARA writes down every instruction that
failed to execute, and says why.

## b. What was built

**Two capabilities. A third was declared removed in advance, before any code existed.**

**1. `cfr_resolve` — a deterministic resolver** (`src/cfr_resolve.py`). Given a title,
part, section, as-of date, quoted anchor and paragraph designation, it returns
`{found, level, designation_exists, siblings, char_offset}`. **Designation-hierarchy
resolution first, quoted-anchor matching second.** That order is forced by measurement,
not taste: 41 of 82 labelled items have no extractable quoted anchor on any instruction (118 of 208 instructions carry none; `data/evalset/items.jsonl`), and NARA's
dominant note mechanisms are designation-*state* facts. Matching is attempted at three
**declared** levels, `exact`, `whitespace-collapsed` and `alphanumeric-only`, and **the
level achieved is returned in the output, never applied invisibly.** `alphanumeric-only`
does not fold case, because `(A)` and `(a)` are different paragraphs.

**2. `SKILL.md` — the OFR execution procedure** (`agents/A1-SKILL.md`). Parse every
AMDPAR into `(operation, anchor, designation)`, in order. Resolve every one against the
as-of text. Only then rule.

**3. The ordered-state ledger — NOT BUILT.** Counted removal #3, declared by ruling R-01
before a line of it existed, so that two capabilities could be measured properly instead
of three in a hurry. **The removed capability is visible in the shipped artifact rather
than absent from it:** human-checkpoint condition **C3** fires when one designation is
touched by two instructions, and names R-01 in its own escalation text. The agent refuses
to model execution order rather than pretending to.

### The output contract is the load-bearing decision

The agent does not emit a bit. It emits **the editorial note NARA would publish**: the
failing designation, the failure class from NARA's own five-way vocabulary, and the full
per-instruction resolution trace.

**`verdict` is derived in code from that trace, not asked of the model**
(`src/a1.py::derive_output`). The model is never asked for a section verdict and cannot
emit one; it rules one instruction at a time, and the harness computes the section
verdict by *a section fails if any instruction fails*. **So a correct `WILL_FAIL` requires
naming which instruction fails and why.** The verdict cannot be produced without the
reasoning that would justify it. It does not make the reasoning right, and §e below counts
the two items where it was not.

**16 of 82 items route to a human checkpoint**, and the three trigger conditions are
computed in code from the trace, never asked of the model. An agent that decides for
itself when to escalate escalates whenever it is unsure, which is a confidence report
and not a checkpoint. `docs/evidence/ch06-a1/a1-result.txt`; details in
[SAFETY.md](SAFETY.md).

## c. Results

### What did not work — this part first

**The pre-registered success criterion was NOT met, on all four clauses.**
`GOOD.md` §4, committed before any arm ran: *A1 ≥ B0-agent + 8 pp, McNemar p < 0.05, at
n ≥ 84, and A1 ≥ 0.80 absolute.*

| clause | measured | |
|---|---|---|
| A1 ≥ B0-agent + 8 pp | gap **+6.1 pp** | **NOT MET** |
| McNemar p < 0.05 | **p = 0.4244** | **NOT MET** |
| n ≥ 84 | **n = 82** — two short of the 84 the criterion names | **NOT MET** |
| A1 ≥ 0.80 absolute | **A1 = 0.7195** | **NOT MET** |

`docs/evidence/ch06-a1/a1-result.json`. **The criterion was never moved.** The `n ≥ 84`
clause was already unsatisfiable when the pre-registration was written. `GOOD.md` §4
says so, in advance, at a corpus of 76. The architect's ruling was that 84 stands
and the two-item shortfall is stated wherever the criterion is quoted
(`QUESTIONS.md` **Q16**). `GOOD.md` carries a dated addendum correcting the stale corpus
figure with **zero original lines changed**.

**Iteration 1 predicted +8 pp and measured −9.8 pp.** Wrong direction. `cfr_resolve` on
its own scored **0.5610** against B0-agent's 0.6585. A deterministic tool made the agent
*worse*. The card is marked **REMOVED** and it stays exactly as written. It was committed
to git at `e12466c` **764 seconds before the first call of the arm it predicted**
(first record in `docs/trajectories/arms/A1-iter1-rep1.jsonl`, `2026-08-31T02:24:21.091Z`,
against the commit's `2026-08-31T02:11:37Z`).

**Iteration 2 predicted 0.81 and measured 0.7195**, missing by 9.1 pp. A second, later
prediction of 0.69 was beaten by 3.0 pp. Both are scored; neither was moved; and the
weaker evidential status of the later one is stated in `CHANGELOG.md` rather than
quietly enjoyed.

**The leakage probe's pre-registered prediction missed.** `CONTEXT.md` §10 predicted that
giving the agent *current* CFR text instead of point-in-time text would make accuracy
**rise**, because the current text leaks the label, and pre-committed that a rise would
be *"proof of leakage, not capability."* It fell: **0.6585 → 0.5976, −6.1 pp.** Recorded
as **MISSED**, not reinterpreted. `docs/evidence/ch09-removed/leakage-result.txt`.

**The model-sensitivity check is withdrawn.** A harness defect, not a finding: **13 of 20**
`B0-agent-sonnet` calls returned an empty text block and the scorer correctly charged each
as a failure. An arm that produced no output on 65% of its items measured the harness.
**No sensitivity claim is made anywhere in this submission.** Artifacts kept, labelled
withdrawn. `QUESTIONS.md` Q19.

### What did work

**The corpus claim, and it is significant.** Giving the model the point-in-time CFR text
moved accuracy from **0.4756 to 0.6585**: **+18.3 pp, exact two-sided McNemar
p = 0.0059**, b = 21, c = 6, n = 82.
`docs/evidence/checkpoint/checkpoint-result.json`. The CH-04 reviewer reimplemented
`CONTEXT.md` §7 from scratch, importing nothing and building its own binomial
coefficients, and reproduced every checkpoint number to a delta of **0.000e+00**
(`docs/reviews/REVIEW_CH-04.md`). This is a baseline result and is reported as one: it
belongs to `B0-agent`, which the brief calls a type-2 baseline, and it sits one row above
the agent in every table.

**A1 = 0.7195 against B0-agent's 0.6585 — +6.1 pp, p = 0.4244. Not significant.**
95% CI on A1's accuracy, bootstrap clustered by FR document, **[0.6190, 0.8158]** over 37
clusters. Written here in those words because that is what it is.

**The composition finding — this is the answer to "which design choices helped?"**

| arm | accuracy | vs B0-agent |
|---|---:|---:|
| B0-agent — the model with the CFR text | 0.6585 | — |
| **+ tool only** (Iteration 1) | **0.5610** | **−9.8 pp** |
| **+ skill only** (`A1-minus-tool`) | **0.6463** | **−1.2 pp** |
| **+ both** (A1) | **0.7195** | **+6.1 pp** |

Add the two separate deltas to the baseline and you predict
0.6585 − 0.0976 − 0.0122 = **0.5488**. Measured: **0.7195**. **Superadditive by +17.1 pp.**
The three accuracies and the two `gap_pp` values are in
`docs/evidence/ch06-a1/a1-result.json`; the subtraction is done here, in the open, because
no committed script publishes it.

**Neither capability is distinguishable from no effect on its own, and together they
clear both.** Say it carefully, because the ablations are one rep each and A1's rep-to-rep
spread is 4.9 pp: −1.2 pp for skill-alone is inside that, and −9.8 pp for tool-alone is
outside it. The mechanism, though, is not a mystery. The written procedure repairs a defect in the tool. `cfr_resolve` cannot see a
paragraph designation codified nested under its parent. The CFR writes `(b)` then bare
`(1)`, and the resolver looks for the literal string `(b)(1)`. It reports *absent* for
paragraphs that are present: **60 of 128 designations, touching 33 of 82 items, and every
single misfire runs in that one direction.** Zero in the other direction. That is the signature of a
systematic modelling error, not noise. `QUESTIONS.md` **Q21**,
`docs/evidence/ch06-a1/iter1/nested_designation_probe.txt`.

The tool alone therefore manufactures false defects: Iteration 1's false-defect rate went
**0.1951 → 0.4878**, straight through a pre-registered 0.25 guard. **The skill's Step 2.5
tells the agent, in the open, that its own tool has a measured blind spot and how to check
around it.** Read `siblings`, it says, which frequently hands back the very paragraph the
tool just denied. That is why the pair composes and neither half works.

**Was it just more compute?** The control built to answer that says no, with one caveat
about the control itself. **B0′** is B0-agent sampled three times per item with a
majority vote and a tie-break published before the run. It scored **0.6585 — identical to
B0-agent to four decimal places, +0.0 pp, McNemar p = 1.0000**, differing on 2 of 82 items
whose flips cancel exactly, while **22 of 82 items had samples that disagreed with each
other** (`docs/evidence/ch06-a1/B0prime-rep1-votes.json`; 8 if only parseable votes are
counted). So the sampling was doing something, and majority voting over it converged back
to the greedy answer.

**The caveat, because the control's own name overstates it.** `CONTEXT.md` §4 specifies
B0′ as *"B0-agent at A1's exact token budget"*. Measured, it spent **1,377,402 input
tokens against A1's 4,006,662** and USD 1.3988 against USD 5.3334
(`docs/evidence/ch06-a1/a1-result.json`) — roughly a third of A1's input, not a match.
It is a **repeated-sampling control at 3× best-of sampling**, not a token-matched one. It
rules out *"three tries instead of one"*; it does not rule out *"three times the tokens"*.
**A genuinely compute-matched control was not run at all** — building one means new paid
arms, and it is stated here rather than implied by a label. That statement is stronger
than the mislabel would have been: *"the agent did not simply get more compute"* is
supported by the sampling control, and it is **not** supported by a token match, because
there is none. `QUESTIONS.md` **Q34**. B0′ is **the only arm in the primary matrix not at temperature 0** — self-consistency
at 0 is a no-op, and the deviation is ruled in `QUESTIONS.md` Q22. *Corrected at CH-11c:
this read "the only arm in the packet", which is false — the two withdrawn sonnet arms
also ran off 0, because `claude-sonnet-5` rejects the parameter (HTTP 400, measured), so
they ran at the model default. `GOOD.md` §8 records that asymmetry as a reported
limitation. B0′ at temperature 1.0 is the only such arm among the six that carry a
published number.*

**And the trivial attack is dead.** The best model-free script, a threshold over 30 cheap
features with 5-fold CV grouped by FR document, scores **0.6098 at permutation
p = 0.2355**. An earlier project of ours died to exactly this kind of script scoring 100%,
so this baseline was built to win if it could. `docs/evidence/ch04-scorer/bscript-run.txt`.

### Every arm, one table

| arm | acc | succ/n | false-def | missed-def | unparseable |
|---|---:|---:|---:|---:|---:|
| B0 — instruction only | 0.4756 | 39/82 | 0.1220 ✅ | 0.9268 ❌ | 3 |
| B0-agent — + point-in-time CFR text | 0.6585 | 54/82 | 0.1951 ✅ | 0.4878 ❌ | 0 |
| B0′ — repeated-sampling control | 0.6585 | 54/82 | 0.2195 ✅ | 0.4634 ❌ | 0 |
| A1-iter1 — + tool | 0.5610 | 46/82 | 0.4878 ❌ | 0.3902 ❌ | 2 |
| A1-minus-tool — + skill | 0.6463 | 53/82 | 0.3415 ❌ | 0.3659 ❌ | 0 |
| **A1 — both** | **0.7195** | **59/82** | **0.2195 ✅** | **0.3415 ❌** | **0** |

Guards are pre-registered at ≤ 0.25 and were not moved. **A1 is the only one of the three
A1-family arms that passes the false-defect guard** — B0, B0-agent and B0′ pass it too, and
the two ablations do not. **Every arm fails the missed-defect guard.** An
unparseable or absent verdict is scored a **failure**, never a skip, and
`success + failure == n` is asserted in code — so no arm can raise its score by declining
to answer. `docs/evidence/ch06-a1/a1-result.txt`.

## d. The Improvement Changelog

Each row was committed **before** the build it describes, with its prediction already
fixed. A card that predicted +8 pp and measured −9.8 pp is better evidence of method than
one that quietly succeeded. The full cards, with their arithmetic, are in `CHANGELOG.md`.

| STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING |
|---|---|---|---|
| **Baseline** | **B0** (one prompt, instruction only) against **B0-agent** (same model + point-in-time CFR text). The project's claim is that an instruction carries no evidence of its own executability. B0 is that sentence turned into an experiment. | B0 **0.4756** · B0-agent **0.6585** · gap **+18.3 pp** · McNemar exact **p = 0.0059** (b=21 c=6) · n = 82, 41 pairs, 3 reps. B-script **0.6098**, permutation **p = 0.2355**, `docs/evidence/ch04-scorer/bscript-run.txt`. Arms: `docs/evidence/checkpoint/` | **GREEN.** Phase 2 proceeds. B0 landed on its predicted 0.50; B0-agent came in **9 pp below** its predicted 0.75. **An earlier run of this row read AMBER and is WITHDRAWN** — it was computed on an eval set the CH-03 review then failed, which a label-blind script beat at 0.8158. Figures kept at `checkpoint/withdrawn/`. The corrected set is **harder**: the same attack now scores 0.5610. |
| **Iteration 1** | **`cfr_resolve`** — deterministic designation-state and quoted-anchor resolution. **Targets a measured failure:** B0-agent reads the text and still misses nearly half the defects, because reading is not checking. | **0.5610 (46/82) — −9.8 pp BELOW B0-agent.** McNemar p = 0.1516. Missed-defect 0.4878 → **0.3902**; false-defect 0.1951 → **0.4878**, through the 0.25 guard. 367 tool calls, 4.48/item — it was used, not ignored. `docs/evidence/ch06-a1/a1-result.txt`; the error profile and the Q21 probe at `docs/evidence/ch06-a1/iter1/` and `iter2/` | **REMOVED as a standalone capability. Predicted +8 pp; measured −9.8 pp** — missed by 17.8 pp in the wrong direction. **Learning: a deterministic tool that is systematically wrong in one direction is worse than no tool, because the agent trusts it.** Cause isolated to Q21's nested-designation ceiling: on items it touches, −18.2 pp; elsewhere, −4.1 pp. **The tool was NOT fixed** — out of scope, CH-05 gated, and found *because* it cost a point. |
| **Iteration 2** | **`SKILL.md` + the note-emission contract** — the ordered OFR procedure, plus the output contract in which `verdict` is **derived** from `resolution_trace`. Targets Iteration 1's measured error inversion: the agent over-trusts the tool and never cross-checks it. | **A1 = 0.7195 (59/82), 3 reps — +6.1 pp over B0-agent, +15.9 pp over Iteration 1.** McNemar **p = 0.4244** (b=15 c=10). CI clustered by FR document [0.6190, 0.8158]. **False-defect 0.4878 → 0.2195, back through the guard; missed-defect 0.3902 → 0.3415, the best of any arm.** `docs/evidence/ch06-a1/a1-result.txt` | **KEPT.** Prediction v1 (0.81) **missed by 9.1 pp**; v2 (0.69) **beaten by 3.0 pp**; neither moved. **The finding is composition, not the skill:** tool alone −9.8, skill alone −1.2, both +6.1 — **superadditive by +17.1 pp.** But the gap is **not significant at n = 82** and the criterion is **not met on any clause.** |
| **Iteration 3** *(removed #3)* | **Ordered-state ledger — NOT BUILT.** Pre-declared as a counted removal by ruling R-01 before any code existed. | Class size recomputed in-repo and **the published justification DOES NOT REPRODUCE**: four readings of the spec's prose give 3.3% / 11.1% / 19.6% / 30.1%, and the published **42.0% sits above the ceiling of the loosest reading**. No denominator reconciles. `QUESTIONS.md` **Q23** | **REMOVED, and the removal is unaffected** — R-01 cut it to measure two capabilities properly rather than three in a hurry, which never rested on the class size. **A removal justified BY a number that then failed to reproduce would have been a far worse position.** The capability is visible as an escalation rather than absent: **human-checkpoint condition C3** fires when one designation is touched twice and **names R-01 in its own escalation text**. 16 of 82 items route to the checkpoint. |
| **Removed #1** | **Current CFR text instead of point-in-time text.** The experiment that prices the corpus: CH-03 spent a night building text as it stood on the publication date, and this measures what skipping it would have bought. | **0.6585 → 0.5976, −6.1 pp**, McNemar p = 0.4421, same 82 items, identical text pipeline including stripping the editorial notes that define the labels. False-defect 0.1951 → **0.5122**; missed-defect 0.4878 → **0.2927**. `docs/evidence/ch09-removed/leakage-result.txt` | **The pre-registered prediction MISSED and is recorded as missed.** It predicted a *rise* and pre-committed that a rise would be proof of leakage. The number fell. **The point-in-time corpus is vindicated either way** — and look at the class shift, not the average: the current text turned a missed-defect problem into a false-defect problem. |
| **Removed #2** | **Intra-rule collision detector.** Cut by R-01 with its class size measured rather than asserted. | **43 of 2,527 = 1.70%**, reproducing **neither** prior endpoint (pilot 1.31%, naive recount 3.07%). Consistency check passes: collision-only = 0, so collisions are a strict subset of state-carry. `docs/evidence/ch09-removed/class_sizes.txt` | **REMOVED, and not because of the class size.** 0 of 68 labelled items contain a redesignation instruction; **NARA never publishes a note naming an intra-rule conflict** — a live probe for *"conflicting amendments"* returned 0; and 15 of the pilot's 26 collisions are *correct drafting*. **A detector for a class NARA does not write notes about cannot be scored against NARA's notes at any class size.** |
| **Final** | **The full arm matrix, both ablations, and the control for extra compute.** The first question any reader asks is *"did the agent just get more compute?"*, so **B0′** was built to answer it. | B0 0.4756 · B0-agent 0.6585 · **B0′ 0.6585** · A1-iter1 0.5610 · A1-minus-tool 0.6463 · A1 0.7195. Per-arm tokens and USD, per-class recall, clustered bootstrap with a probe against item-level resampling, and `docs/evidence/error-taxonomy.csv`. Spend **USD 11.63** of an 18.00 ceiling. | **B0′ = B0-agent to four decimal places**, +0.0 pp, p = 1.0000, differing on 2 of 82 items whose flips cancel — while **22 of 82** had samples that disagreed with each other (`B0prime-rep1-votes.json`). **Majority voting over repeated samples converges to the greedy answer and buys nothing** — though B0′ spent 1.38 M input tokens against A1's 4.01 M, so it is a repeated-sampling control at 3× best-of sampling rather than the token-matched one `CONTEXT.md` §4 specifies, and **a genuinely compute-matched control was not run** (Q34). **A1's per-class recall moves +14.6 pp on the defective class for −2.4 pp on the clean class** — the hot take confirmed on this project's own baseline. |

## e. The main failure mode

**Missed defects. 14 of A1's 23 errors** — `docs/evidence/error-taxonomy.csv`, 25 rows:
14 missed-defect, 9 false-defect, 2 right-verdict-possibly-wrong-reason. A1's
missed-defect rate is **0.3415 against a pre-registered guard of 0.25**, and it is the
best of any arm measured.

**Twelve of the fourteen carry the same trace signature: `no instruction ruled failing`.**
The agent walked every instruction, ruled each one executable, and derived
`WILL_EXECUTE` — correctly, from its own premises. The other two are rep disagreement:
the trace on file names a failing instruction and rules `WILL_FAIL`, while the majority
across three reps does not, and the CSV's `trace_rep_agrees_with_majority` column reads
`False` on exactly those two rows.

### Worked example — `2016-09949|1436.3`, 7 CFR 1436.3

NARA's note, which is the gold label, quoted from `data/evalset/items.jsonl`:

> At 81 FR 25592, Apr. 29, 2016, § 1436.3 was amended; however, the amendment could not
> be incorporated due to inaccurate amendatory instruction.

Seven instructions, and the agent ruled all seven executable. The harness resolves every
instruction against the as-of text whatever the arm does, so the trace records what was
true beside what the model said: **the resolver located a quoted anchor for three of the
seven, and found nothing to check on the other four.** The agent made 3 `cfr_resolve`
calls of its own. **All four unchecked instructions are waved through, three of them on
one rationale and the fourth on a sibling of it.** `executes` and `why` are from the
emitted trace, `docs/evidence/ch06-a1/A1-rep1-artifacts.jsonl`; the instruction text is
from `data/evalset/items.jsonl`, which is where the trace does not carry it:

```
instructions 2, 5, 7   e.g. "a. Add in alphabetical order definitions for
                             “Aquaculture,” “ARS,” and “CCC;”"
                       executes = true
                       why      = "add directive with no specific target designation
                                   or anchor; asserts no verifiable target"

instruction 1          "4. Amend § 1436.3 as follows:"
                       executes = true
                       why      = "umbrella; asserts no target"
```

The target of instructions 2, 5 and 7 is a **definition name inside an alphabetical
list**, not a paragraph designation and not a quoted anchor. `cfr_resolve` addresses
designations and anchors. It has nothing to say here, so the agent has nothing to check,
**and when it has nothing to check it rules that the instruction executes.**

**That default is the failure mode.** It is not a reasoning error and it is not the tool
being wrong. It is the absence of coverage being scored as evidence of correctness, the same shape as a
green test suite over untested code, which is the thing this whole project was built to
argue about. NARA's note for this section names no designation either. It
just says the instruction was inaccurate.

### The two most honest rows in the file

Two items are marked **`right-verdict-possibly-wrong-reason`**. Both are scored **correct**
on the primary metric. Both got there on a rationale the agent's own tool contradicts: it
ruled `WILL_FAIL` on an instruction where the resolver had reported `designation_exists:
true` and had located the anchor.

| item | class the agent named | designation |
|---|---|---|
| `2015-01571|1942.8` | quoted-text-not-present, instruction 4 of 4 | (h) |
| `2020-11897|90.213` | target-already-exists, instruction 1 of 1 | (a) |

**An accuracy average cannot see this. The emitted note can.** That is the entire argument
for the output contract in `CONTEXT.md` §5, arriving as a live example rather than a
hypothetical, and it is why the taxonomy separates *right verdict, right reason* from
*right verdict, wrong reason* instead of counting both as a point. On a binary label a coin
gets the verdict half the time; only the trace shows whether the agent knew why.

## f. The hot take

> **A verification agent's grounding corpus is a precision instrument, not a recall
> instrument — and if you hand it the document, measure *which class* got better, because
> the average will lie to you.**

The average said giving the model the CFR text was worth **+18.3 pp**. Here is what it did
to the classes:

| arm | recall on `WILL_FAIL` (defective) | recall on `WILL_EXECUTE` (clean) |
|---|---:|---:|
| B0 — no text | 0.0732 | 0.8780 |
| B0-agent — with the text | **0.5122** | 0.8049 |
| **A1** | **0.6585** *(+14.6 pp)* | 0.7805 *(−2.4 pp)* |

`docs/evidence/ch06-a1/a1-result.txt`. B0 was not at chance. **It was a constant** — it
called almost everything executable, scored 0.8780 on the clean class and 0.0732 on the
defective one, and landed at 0.4756 overall because the eval set is balanced by
construction. Handing it the corpus moved the *average* 18 points and left the decision
boundary roughly where it was. The arm did not become accurate. It became **agreeable**.
Missed defects were still **71.4% of all its errors**.

The removed leakage experiment says the same thing from the other side. Swapping
point-in-time text for current text moved the average only **−6.1 pp**, which looks like
noise, while the false-defect rate went **0.1951 → 0.5122** and the missed-defect rate
went **0.4878 → 0.2927**. The average barely moved. The system became a different system.

And the composition finding is the sharpest version. **A capability's contribution is not
a property of the capability.** `cfr_resolve` scored −9.8 pp alone and is part of the only
arm that clears the false-defect guard. `SKILL.md` scored −1.2 pp alone. Ablating one
capability at a time and reading the deltas would have concluded that both were useless.
Both ablations ran, both are published, and both are wrong about the system they came from.

**The transferable rule.** Before you build retrieval into an adjudication pipeline,
measure the baseline's **per-class** recall. If the negative class is already strong,
retrieval buys you an average that flatters and a decision boundary that does not move.
And before you cut a component that ablates flat, check whether it is repairing something
else.

**How far that transfers is a hypothesis, not a result.** `CONTEXT.md` §11 claims it
*"generalises without modification to fact-checking, code review, security triage, and RAG
over any corpus of contested claims."* Nothing in `docs/evidence/` measures anything
outside 82 Federal Register items, so that sentence is a prediction this project has not
earned and it is quoted here as one. The hypothesis behind it came from an earlier
measurement on IETF errata, from work outside this repository; it is not re-derived here
and it carries no weight here. Everything above is measured on this corpus, with its script
and its output committed.

**And the premise underneath the whole project is prior art, cited rather than claimed.**
The thing this repository was built to test — *a green test suite is not evidence of
correctness* — did not originate here. The motivating observation is
`github.com/chinmoypaul8897/nistula-assistance-`, public and last pushed **2026-08-18,
ten days before kickoff**, which documents the multi-agent review gate this project's
`PROCESS.md` derives from and records **17 blocker-class defects found while the test
suite was green**. That is the hypothesis. **This project reuses none of its code, data
or artifacts, and does not re-derive that number** — nothing in `docs/evidence/` measures
it, it is not checkable from inside this repository, and no claim in this submission rests
on it. What is new here is the *test*: the same premise put to a different corpus under a
criterion written before any model ran — 82 Federal Register items, and a criterion this
project then **failed on all four clauses** and did not move. Full disclosure of what
pre-existed is [PROVENANCE.md](PROVENANCE.md) §4.

### What it changes about what we build next

Three things. **Report per-class recall beside every average**, as a default, in every
evaluation. It costs nothing and it is the difference between "retrieval helped" and
"retrieval made the model agreeable." **Test capabilities in combination, not one at a
time**, because a one-at-a-time ablation table would have deleted both of ours. And **when
a deterministic tool is wrong, check whether it is wrong in one direction** before deciding
it is noise: 60 misfires one way and 0 the other is a modelling error you can write a
procedure against, which is exactly what Step 2.5 is.

## g. LIMITATIONS

Not a footnote, and not a short one. Every item below is a reason to trust this
submission less, and each is here because we found it rather than because someone asked.

**n = 82 against a criterion written for 84.** Two items short. The criterion was **not
moved** and the shortfall is stated wherever it is quoted (`QUESTIONS.md` Q16). At this n,
the smallest all-one-way discordant count clearing α = 0.05 is 6, a floor of **7.3 pp** on
the detectable effect. A mixed split needs more. **This sample cannot detect a gap of a few
points at any p-value worth reporting**, and that was written down in `GOOD.md` §4 before
any arm ran.

**The primary eval set deviates from a pre-registration.** `docs/evidence/ch03-evalset/
pre-registration.md` §2 fixes the **restricted** set — FR documents at per-document
completeness ≥ 0.90 — as primary, *"precisely so that it cannot later be chosen for its
effect on n."* The restricted set yields **one pair** and measures nothing. The architect
ruled the unrestricted set (41 pairs, n = 82) primary and required the deviation disclosed
in every results table rather than absorbed (`QUESTIONS.md` **Q19**). **Both sets ship** and
either can be run with one flag. The uncomfortable part is stated in Q16: the option taken
is also the one with the larger n.

**A note on which document said what**, because two shipping files get this wrong and this
one should not. `docs/evidence/ch06-a1/a1-result.txt`'s deviation banner and Q19's ruling
text both attribute the restricted-primary pre-registration to **`GOOD.md` §11**. `GOOD.md`
§11 says the opposite — *"Primary: `data/evalset/` — 38 pairs, n = 76"*, the unrestricted
set. The deviation is real and it is from the CH-03 pre-registration; the attribution to
`GOOD.md` is a misquotation that has propagated. It was raised as `QUESTIONS.md` **Q32**
and **answered at CH-11c**: a dated correction is appended beneath the Q19 ruling, quoting
`GOOD.md` §11 in full, and **the ruling's own text is left unedited**. The substantive
decision is unaffected — it rests on the pair count, **1 against 41**, not on which
document pre-registered what. `a1-result.txt`'s banner is **still uncorrected** and is
left so deliberately: it is a regenerated artifact whose byte-identity across three
environments is itself a published result, and re-cutting it is the architect's call.

**Gate status, plainly.** `PROCESS.md` §6 gates a chunk on review by a session with zero
shared context. **Six chunks carry a gate. None of them passed it.**

| chunk | gate | state |
|---|---|---|
| CH-02 · AMDPAR attributor | FULL | **never reviewed.** `PROCESS.md` §6 gates it FULL because *"a truncation bug already produced 0.46 completeness once and poisoned an entire pilot"*, and §7's done-when is *"completeness ≥ 0.90, measured and printed"*. It measured **0.5080 / 0.6643**. Two spec-fix sessions argued over its metric; neither was the adversarial review the gate asks for. |
| CH-03 · point-in-time text + eval set | FULL + mutation | **reviewed-FAIL ×2 → ESCALATED.** Round 1 found a label-blind script scoring **0.8158** on the eval set — beating B0-agent by 17 pp with no model and no CFR text. Fixed; the attack now scores 0.5610. Round 2 confirmed the fix was real and failed it anyway, because **no test protected it**, round 1's mutation table was **false**, and two published numbers did not reproduce. Strike limit reached, no third round — and **one of the escalation's three open items was never ruled on.** See below. |
| CH-04 · scorer + `GOOD.md` | FULL + mutation | **reviewed-FAIL ×1.** 16 findings, **7 material**, not re-reviewed. The arithmetic was vindicated to 0.000e+00; the findings are provenance and coverage — including that **deleting `success + failure == n` outright leaves all 313 tests green.** |
| CH-05 · `cfr_resolve` | code-only | **not reviewed.** |
| CH-06 · `SKILL.md` + A1 | CODE-ONLY | **not reviewed.** |
| CH-08 · ablations and final arms | **NUMBERS** | **not reviewed — and this is the gate written for this document.** `PROCESS.md` §6 pre-registers a NUMBERS-ONLY review that *"applies to the CHECKPOINT before its call is acted on, and to CH-08 before any number reaches the README"*: an independent recomputation of accuracy, McNemar, the bootstrap CI and the effect size, a probe confirming the bootstrap resamples documents not items, and a config diff confirming each ablation differs from A1 in exactly one capability. `plan.md` and `STATUS.md` both record CH-08's gate as `none`, which contradicts `PROCESS.md`, and `PROCESS.md` outranks `plan.md`. **Every number in section c reached this README without it.** |

**One escalated question is still open, quoted rather than paraphrased.** `PROCESS.md`
§6's two-strike rule requires a twice-failed chunk's open findings copied **verbatim**
into this section. CH-03's escalation raised three; the architect ruled on two.
`QUESTIONS.md` Q19, item 2:

> **Whether the corrections above are legitimate**, or whether the strike rule should
> have frozen CH-03 exactly as it stood at the second FAIL.

and the ruling's own closing line:

> **Point 2 — whether CH-03's post-strike corrections were legitimate — is not addressed
> by these rulings and remains open.**

The corrections in question are retractions of three demonstrably false published
numbers. The build session's position — that retracting a false number is not "fixing a
chunk" — is its own, and it says so.

**The attributor gate failed and the failure is published, not fixed.** Completeness
measured **0.5080** spec-literal and **0.6643** extended at CH-02, and **0.5340** under
`CONTEXT.md` v1.1, against a pre-registered **≥ 0.90 that blocks any headline number**.
**The accuracy headline is therefore withdrawn, by us, on our own guard, and it was
withdrawn before any arm ran** (`GOOD.md` §3). A proposed metric change that would have
passed the gate was **refused**: under the proposed metric a control attributor that
mis-attributes **8,417 of 8,634 elements — 97.5% wrong — scores the identical 0.9865, to
six decimal places.** `docs/evidence/spec-fix-1/verdict.md`; ruling `QUESTIONS.md` Q11.

**`cfr_resolve` has a known one-way defect and it was left unfixed.** Q21, above: 60 of 128
designations, 33 of 82 items, every misfire in the same direction. It is outside CH-06's
scope fence, CH-05 is gated and unreviewed, and, decisively, **it was found because it
cost A1 a point.** A capability changed on that basis is tuned, however good the
engineering argument. The compensation lives in the published procedure where a judge can
read it, instead of in a quiet repair to the component the measurement just embarrassed.

**A published figure in the spec does not reproduce.** `CONTEXT.md` §6 justifies the
removed ledger with a state-carry rate of **833/1,984 = 42.0%**. Recomputed in-repo, four
readings give 3.3% / 11.1% / 19.6% / 30.1%, and **42.0% is above the ceiling of the loosest
reading**. No denominator reconciles. We do not conclude the figure is wrong. It may come from a corpus or a definition this
repository cannot see. We conclude only that **it is not reproducible from the shipped
artifacts and therefore cannot carry a claim**
(`QUESTIONS.md` Q23).

**About USD 1.43 of API spend was wasted on a double-run.** Two arms were run twice because
the operator reasoned about the job queue from memory instead of reading the command he had
typed. The ledger is append-only and both runs are kept, so the money is reported correctly;
what is damaged is `run_id` uniqueness, on 651 rows, and the duplicates are enumerable in one
pass. `A1-minus-tool`'s two runs are identical on all 82 items; `B0prime`'s differ on 2, and
the flips cancel. **No published number moves.** `QUESTIONS.md` Q26.

**Three reps of A1 are not identical, at temperature 0.** Per-rep accuracy 0.7195 / 0.6707 /
0.7195, up to 12 of 82 items differing between a pair of reps, while B0-agent's three reps
were identical on every item. A1 runs an agentic loop and each turn is sampled from a context
the previous turn shaped. **Determinism at temperature 0 is a property of a single call, not
of a multi-turn agent.** The ablations are one rep each, so **any gap between them smaller
than that spread is inside the run-to-run noise** and must not be read as an effect.

**The rep-aggregation rule is pre-registered nowhere.** Majority across reps, ties to the
failure side. It debuts in `analyse_checkpoint.py`, committed after the first arm call,
whose docstring wrongly called it pre-registered. The CH-04 reviewer caught it. Every alternative
aggregation still lands the checkpoint on GREEN, so nothing turns on it, and it is disclosed
in the analysis script's own output rather than defended.

**One instruction-count reading, one platform, one operator.** Exact instruction-count
matching is enforced at tolerance 0. The suite and the replay were run on Windows with
CPython 3.12.2; nothing is claimed about other platforms because nothing was measured there.

---

## Where everything is

| | |
|---|---|
| **Reproduce it** | [REPRODUCE.md](REPRODUCE.md) — Tier 1 offline in 14.42 s and 25.84 s on two runs for USD 0, Tier 2 live |
| **The pre-registration** | [GOOD.md](GOOD.md) — metric, thresholds, predictions, committed before any result existed |
| **The iteration cards** | [CHANGELOG.md](CHANGELOG.md) — each committed before its build |
| **The spec** | [CONTEXT.md](CONTEXT.md) — architect-authored, versioned, outranks the code |
| **Every ambiguity and every ruling** | [QUESTIONS.md](QUESTIONS.md) — **43** entries (`grep -c '^## Q'`), including our own retractions |
| **Chunk-by-chunk state** | [STATUS.md](STATUS.md) · [PROGRESS.md](PROGRESS.md) |
| **The worksheet the agent produces** | [`docs/worksheet/index.html`](docs/worksheet/index.html) — real committed A1 output, opens offline by double-clicking |
| **Every trajectory, and what to look at in it** | [`docs/trajectories/INDEX.md`](docs/trajectories/INDEX.md) — 36 files, with the curation rule published before it was applied |
| **Every model, tool and agent** | [AI-USE.md](AI-USE.md) · [`docs/trajectories/`](docs/trajectories/) · [`prompts/`](prompts/) · [`agents/`](agents/) |
| **What pre-existed vs what was built** | [PROVENANCE.md](PROVENANCE.md) |
| **Reviews** | [`docs/reviews/`](docs/reviews/) — three reports, three FAIL verdicts, one escalation, with runnable probes |
| **Evidence** | [`docs/evidence/`](docs/evidence/) — every claim's generating script and its committed output |
| **Safety, licence, dependencies** | [SAFETY.md](SAFETY.md) · [LICENSE](LICENSE) · [THIRD-PARTY.md](THIRD-PARTY.md) |
| **Submission checklist** | [SUBMISSION.md](SUBMISSION.md) |

**Prior art, cited and not reimplemented:** Prior et al., NLLP@ACL 2025 (amendatory
instruction execution as a task) and `cfpb/regulations-parser`. Details in
[THIRD-PARTY.md](THIRD-PARTY.md) §6.

**How this was built.** Claude Code driving `claude-opus-5`, under human direction, in
spec-first chunks with adversarial review gates. Every session transcript, every prompt, and
every token and dollar is published. All three of those review reports are FAIL verdicts against this project's own
work, and they ship unedited. `QUESTIONS.md` holds three errors this project made **about its
own work**, found by checking rather than by being told.

**Not a legal service.** This produces a worksheet a qualified regulations drafter acts on.
It never files anything and it takes no consequential action. [SAFETY.md](SAFETY.md).
