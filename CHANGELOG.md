# CHANGELOG.md — the Improvement Changelog

**This is deliverable 1.** It is written **per iteration, as it happens**, and is
never reconstructed at the end. A changelog assembled after the results are known is
a narrative; one written before each build is evidence.

The rubric's largest row asks **"which design choices helped the agent solve the
problem?"** The only defensible answer is one written *before* the choice was made —
so each row below is backed by an iteration card committed **before** its build, with
its prediction already fixed (`PROCESS.md` §5).

**A capability that does not move its number is REMOVED and its card stays.** A card
that predicted +8 pp and measured +1 pp is better evidence of method than one that
quietly succeeded.

---

## The four-column table (PDF §4)

| STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING |
|---|---|---|---|
| Baseline | **B0** (one prompt, instruction only) vs **B0-agent** (same model + point-in-time CFR text). The project's headline claim is that an amendatory instruction carries no evidence of its own executability; B0 is that sentence turned into an experiment. | **B0 0.4756 · B0-agent 0.6585 · gap +18.3 pp · McNemar exact p = 0.0059 (b=21 c=6, 27 discordant) · n = 82, 41 pairs, 3 reps, `claude-haiku-4-5-20251001` @ t=0.** B-script **0.6098**, within-pair permutation **p = 0.2355**. `docs/evidence/checkpoint/` | **GREEN.** Phase 2 proceeds. B0 landed on its predicted 0.50; B0-agent came in **9 pp below** its predicted 0.75. **An earlier run of this row read AMBER and is WITHDRAWN** — it was computed on an eval set that the CH-03 adversarial review then failed, and which a label-blind script beat at 0.8158. The withdrawn figures are kept at `docs/evidence/checkpoint/withdrawn/`. The corrected eval set is **harder**, not easier: the same attack now scores 0.5610. |
| Iteration 1 | **CH-05 `cfr_resolve`** — deterministic designation-state and quoted-anchor resolution, designation FIRST. **Observed failure it targets:** B0-agent's missed-defect rate is **0.4737** — it reads the text and still misses nearly half the defects, because reading is not checking. | **A1-iter1 = 0.5610 (46/82), which is −9.8 pp BELOW B0-agent's 0.6585.** McNemar p = 0.1516 (b=8, c=16). Missed-defect 0.4878 → **0.3902**; false-defect 0.1951 → **0.4878**, through the 0.25 guard. 367 tool calls, 4.48/item — it was used, not ignored. `docs/evidence/ch06-a1/iter1/`, `iter2/iter1_error_profile.txt` | **REMOVED as a standalone capability — the prediction MISSED by 17.8 pp and missed in the wrong direction.** Predicted +8 pp; measured −9.8 pp. The missed-defect half of the `cb65539` prediction moved the right way and still did not clear 0.25. **Learning: a deterministic tool that is systematically wrong in one direction is worse than no tool, because the agent trusts it.** `cfr_resolve` cannot see a nested designation (Q21): 60/128 designations, 33/82 items, every misfire absent-when-present. On items it touches, −18.2 pp; on items it does not, −4.1 pp. **The tool is NOT fixed** — frozen at `cb65539`, outside scope, and found because it cost a point. |
| Iteration 2 | **CH-06 `SKILL.md` + the note-emission contract** — the ordered OFR execution procedure, plus `CONTEXT.md` §5's output contract in which **`verdict` is DERIVED from `resolution_trace`**. **Observed failure it targets:** left open at commit time on purpose — it is measured from Iteration 1's errors, not guessed. The measured **prior**: on defective sections with ≥ 3 instructions B0-agent misses **11/16 = 0.6875**, against **9/25 = 0.3600** on shorter ones — `CONTEXT.md` §9's hard case as a number. | **A1 = 0.7195 (59/82), 3 reps — +6.1 pp over B0-agent, +15.9 pp over Iteration 1.** McNemar vs B0-agent exact p = **0.4244** (b=15, c=10). 95% CI clustered by FR document [0.6190, 0.8158]. **False-defect 0.4878 → 0.2195, back through the guard; missed-defect 0.3902 → 0.3415, the best of any arm.** `docs/evidence/ch06-a1/a1-result.txt` | **KEPT.** Prediction v2 (0.69) **beaten by 3.0 pp**; prediction v1 (0.81) **missed by 9.1 pp** — both scored, neither moved. **The finding is composition, not the skill:** tool alone **0.5610 (−9.8 pp)**, skill alone **0.6463 (−1.2 pp)**, both **0.7195 (+6.1 pp)** — **superadditive by +17.1 pp** against an additive prediction of 0.5488. **Neither capability helps on its own and together they do.** But the gap is **not significant at n = 82** and the pre-registered criterion is **NOT MET on any of its four clauses.** |
| Iteration 3 | **CH-07 ordered-state ledger — NOT BUILT**, pre-declared as counted removal #3 by ruling R-01 before any code existed. | **Class size recomputed in-repo and the published justification DOES NOT REPRODUCE**: four readings of `CONTEXT.md` §6's prose give 3.3% / 11.1% / 19.6% / 30.1%, and the published **42.0% sits above the ceiling of the loosest reading**; no denominator reconciles either (2,527 / 2,154, neither is 1,984). `QUESTIONS.md` **Q23**. | **REMOVED, and the removal is unaffected** — R-01 cut it to measure two capabilities properly rather than three in a hurry, which never rested on the class size. **The removed capability is visible in the shipped artifact rather than absent from it:** human-checkpoint condition **C3** fires when a designation is touched twice and names R-01 in its own escalation text, so A1 refuses to model execution order instead of pretending to. **16 of 82 items route.** |
| Final | **The full arm matrix, both ablations, and the compute-matched control.** The question a reader asks first is *"did the agent just get more compute?"* — so **B0′** was built to answer it: B0-agent at A1's token budget spent on best-of-3 self-consistency. | **B0 0.4756 · B0-agent 0.6585 · B0′ 0.6585 · A1-iter1 0.5610 · A1-minus-tool 0.6463 · A1 0.7195.** n = 82, 41 pairs, 37 FR documents, `claude-haiku-4-5-20251001` @ t=0 for every arm except B0′ (Q22). Full per-arm token and USD table, per-class recall, clustered bootstrap, and `docs/evidence/error-taxonomy.csv` (25 rows). Spend **USD 10.24 of the 18.00 ceiling**. | **B0′ = B0-agent EXACTLY — +0.0 pp, McNemar p = 1.0000, and b = c = 0, meaning it gave the IDENTICAL answer on all 82 items** although 26 of them had samples that disagreed. Extra compute spent on self-consistency converges to the greedy answer and buys nothing; the gain is the capabilities, not the budget. **A1 is the only agent arm that passes the false-defect guard (0.2195 ≤ 0.25)** and has the lowest missed-defect rate measured (0.3415), though that guard is still failed by every arm. **A1's per-class recall moves +14.6 pp on the defective class for −2.4 pp on the clean class** — `CONTEXT.md` §11's hot take confirmed on this corpus: the average would have hidden which class moved. |

Empty by design at CH-00. CH-00 builds no capability and moves no metric; it builds
the instrument that every later row is measured with. Writing a row for it would be
the exact padding this table exists to expose.

---

## Iteration cards

Each card is committed to this file **before** the build it describes, in this shape:

```
## Iteration N — <capability>
Observed failure : <the specific failure in the previous arm, with its number>
Hypothesis       : <why this capability should fix it>
Prediction       : <the number it should move, and by how much>   <- BEFORE the run
Evidence path    : docs/evidence/iter-N/
```

and completed after it:

```
Result           : <measured>
Decision         : kept / revised / REMOVED
Learning         : <what it taught us about the problem>
```

*(No cards yet. The first is written at the CHECKPOINT, for the Baseline row.)*

---

## Removed experiments — three, all counted

The brief requires removed experiments and most entrants will have none. Ours are
declared here as they are decided, not harvested at the end:

1. **Current-CFR-text leakage probe** — CH-09.
2. **Intra-rule collision detector** — CH-09; class size measured five ways at ~1.3%.
3. **Ordered-state ledger** — CH-07, **declared removed in advance** by ruling R-01,
   before any code existed. Its justification (order-sensitivity fires on 38–42% of
   items, two independent counts, not label-correlated) is published as the reason it
   was *worth* building, alongside the reason it was not built.

---

## Iteration cards — CH-06, committed BEFORE the capabilities are built

> **These two cards are committed before `agents/A1-SKILL.md` and `src/a1.py` exist and
> before a single A1 call is made.** That ordering is the whole mechanism: a prediction
> written after the run is a description. The commit SHA of *this* card and the first
> timestamp in `docs/evidence/runs/cost_ledger.csv` for arm `A1-*` are the two facts a
> reviewer should check against each other, and they are checkable by `git log` alone.

### The observed failure both cards target — measured, not guessed

Script: `docs/evidence/ch06-a1/iter1/b0agent_error_profile.py`
Output: `docs/evidence/ch06-a1/iter1/b0agent_error_profile.txt`
Run over the committed checkpoint reps and the frozen eval set, **before either card was
written**:

| Measurement | Value |
|---|---|
| B0-agent accuracy | **0.6585** (54/82) |
| B0-agent **missed-defect rate** | **0.4878** (20/41) — pre-registered guard ≤ 0.25, **FAILED** |
| B0-agent false-defect rate | 0.1951 (8/41) — guard ≤ 0.25, passed |
| Share of all errors that are **missed defects** | **71.4%** (20 of 28) |
| Recall on `WILL_FAIL` (defective) | **0.5122** |
| Recall on `WILL_EXECUTE` (clean) | **0.8049** |
| Missed defects carrying a designation or a quoted anchor a resolver can check | **19 of 20** |
| Missed defects carrying **neither** — out of reach of the tool | **1 of 20** |
| Miss-rate on defective items with **≥ 3 instructions** | **0.6875** (11/16) |
| Miss-rate on defective items with **< 3 instructions** | 0.3600 (9/25) |

**Read the last two rows together.** They are `CONTEXT.md` §9's hard case — *the defect
that is not the first instruction* — showing up as a measured number rather than an
anecdote. B0-agent is nearly twice as likely to miss a defect when the section carries
three or more instructions. And read rows 5–6 together: giving the model the CFR text
moved the **average** +18.3 pp and left the **decision boundary** where it was. The arm
did not become accurate; it became *agreeable*. That is `CONTEXT.md` §11's hot take
landing on this project's own baseline.

---

```
## Iteration 1 - Tool (cfr_resolve)

Observed failure : B0-agent cannot check whether a quoted anchor or a paragraph
                   designation is actually PRESENT in the point-in-time text. It is
                   shown the text and asked to rule; it has no way to verify, so it
                   defers. Measured: B0-agent 0.6585, and its errors concentrate in
                   MISSED DEFECTS - 20 of 41 defective sections called executable,
                   71.4% of all its errors, a missed-defect rate of 0.4878 against a
                   pre-registered guard of 0.25, with recall 0.5122 on the defective
                   class against 0.8049 on the clean class. 19 of those 20 misses
                   carry a designation or an anchor a deterministic resolver can
                   check; 1 carries neither and is out of the tool's reach.

Hypothesis       : giving it a deterministic resolver removes the guess. The failures
                   are not reasoning failures, they are LOOKUP failures - and a lookup
                   is exactly what a pure function does better than a model.

Prediction       : +8 pp over B0-agent, i.e. A1-iter1 = 0.74   <- COMMITTED BEFORE THE RUN
                   Secondary, and the one that would falsify the hypothesis if it does
                   not move: missed-defect rate 0.4878 -> below 0.35.
                   Mechanism I am betting on: roughly half the 19 reachable misses get
                   caught, minus a few new false defects from over-trusting the tool.

Evidence path    : docs/evidence/ch06-a1/iter1/

## Iteration 2 - Skill (SKILL.md)

Observed failure : FILLED FROM MEASUREMENT, 2026-08-31, after Iteration 1 ran and
                   before Iteration 2 ran. Evidence:
                   docs/evidence/ch06-a1/iter2/iter1_error_profile.txt

                   A1-iter1 = 0.5610, -9.8 pp against B0-agent, and ITS ERRORS HAVE
                   INVERTED. Missed defects 20 -> 16. False defects 8 -> 20, a rate of
                   0.4878 straight through the pre-registered 0.25 guard. The agent
                   OVER-FLAGS: handed a resolver that says a paragraph is absent, it
                   rules the instruction defective and stops. It trusts the tool more
                   than the tool deserves and never cross-checks the tool's answer
                   against the section text it was also given.

                   The mechanism is isolated, not inferred. Splitting the corpus by
                   whether Q21's nested-designation ceiling touches the item:
                     touched     n=33  B0-agent 0.6364 -> A1-iter1 0.4545  -18.2 pp
                     not touched n=49  B0-agent 0.6735 -> A1-iter1 0.6327   -4.1 pp
                   and on CLEAN items the ceiling touches, A1-iter1's false-defect rate
                   is 0.8462 against 0.3214 where it does not. The damage is 4.4x
                   larger where the tool is wrong. Errors also moved 16 items from
                   right to wrong and 8 from wrong to right - the tool is not noise,
                   it is a biased signal.

                   THE CARD'S COMMITTED PRIOR IS FALSIFIED, and is reported as such.
                   e12466c predicted the errors would concentrate on sections with >= 3
                   instructions. They do not - they concentrate BY CLASS. Error rates:
                     defective >=3 instr  0.6875 -> 0.5625   (IMPROVED)
                     defective  <3 instr  0.3600 -> 0.2800   (IMPROVED)
                     clean     >=3 instr  0.2500 -> 0.6250   (much worse)
                     clean      <3 instr  0.1600 -> 0.4000   (much worse)
                   Instruction count was the wrong axis. The prior was written down so
                   that it could be wrong, and it was.

                   The PRIOR that motivated building the skill at all, measured on
                   B0-agent and committed here: on defective sections with >= 3
                   amendatory instructions B0-agent misses 11 of 16 (0.6875); on
                   defective sections with < 3 it misses 9 of 25 (0.3600). CONTEXT.md
                   section 6 F2 predicts the mechanism - "given the tool, the agent
                   checks the first anchor and rules from it" - and section 9 names it
                   the hard case. If Iteration 1's errors do NOT concentrate on
                   multi-instruction items, this prior is wrong and the card says so.

Hypothesis       : an explicit ordered procedure - parse EVERY AMDPAR into
                   (operation, anchor, designation), resolve EVERY one against the
                   as-of text, and only then rule - stops the premature ruling. The
                   tool makes each check possible; the skill makes the agent perform
                   all of them.

Prediction, v1   : +7 pp over Iteration 1, i.e. A1 = 0.81      <- COMMITTED AT e12466c
                   Secondary: missed-defect rate below 0.25, clearing the guard.

                   THE TWO HALVES OF THIS SENTENCE NOW DISAGREE, because Iteration 1
                   landed at 0.5610 rather than the 0.74 the card assumed. Both
                   readings are evaluated and neither is moved:
                     absolute reading   A1 >= 0.81
                     relative reading   A1 >= 0.5610 + 0.07 = 0.6310

Prediction, v2   : A1 = 0.69, i.e. +13 pp over Iteration 1  <- COMMITTED BEFORE THE
                   REVISED ARM RAN, and made WITH MORE INFORMATION than v1 had. That
                   is stated rather than hidden: v2 is a second prediction by an author
                   who has now seen Iteration 1's errors, and it is weaker evidence of
                   method than v1 precisely for that reason. v1 is NOT deleted and NOT
                   moved. Both are scored.

                   The arithmetic behind 0.69, so it can be checked rather than
                   trusted: 20 false defects, of which ~11 sit on the 13 clean items
                   the ceiling touches (rate 0.8462). If Step 2.5 recovers most of
                   those 11 and costs a couple of defect catches, that is roughly
                   +13 pp on 82 items. 0.69 is +3.2 pp over B0-agent, which STILL
                   FAILS GOOD.md's +8 pp clause. Predicting a number that fails the
                   pre-registered criterion is the honest thing to do when that is
                   what the evidence supports.
                   Secondary: false-defect rate back under 0.25; missed-defect rate
                   not worse than Iteration 1's 0.3902.

Evidence path    : docs/evidence/ch06-a1/iter2/
```

### What Iteration 2 actually CHANGED, and why that is iteration and not tuning

`agents/A1-SKILL.md` goes to **version 2**. The change is a new **Step 2.5 —
cross-check a `designation_exists: false` against the text you were given**, plus a
fifth entry at the head of the prohibitions list. It tells the agent, in the open, that
its own tool has a measured blind spot and how to check around it: look for the
designation's last component under its parent, and use `siblings`, which frequently
hands back the very paragraph the tool just denied.

**Why this is legitimate iteration:**

- it is driven by an **error mode** measured on Iteration 1 — over-trust of a
  systematically biased signal — and **never by a per-item label**. No item id, gold
  label, or per-item outcome appears anywhere in the skill;
- the prediction for the revised arm is **committed in this file before the revised arm
  runs**, which is the whole mechanism these cards exist for;
- the change is **disclosed in the shipped instruction file itself**, which now carries
  its own version note and the numbers that caused it.

**Why the tool was not fixed instead**, which is the obvious engineering answer:
`src/cfr_resolve.py` is outside this chunk's scope fence, CH-05 is gated and unreviewed,
and — decisively — the defect was found *because it cost A1 a point*. See `QUESTIONS.md`
Q21. Compensating in the procedure, with the compensation written down where a judge can
read it, is honest; silently repairing the capability that the measurement just
embarrassed is not.

### Two things these predictions are deliberately NOT

**They do not sum to `GOOD.md`'s pre-registered A1 ≈ 0.85.** 0.6585 + 8 + 7 = **0.81**,
four points short. That gap is left standing rather than closed by adjusting either
number. `GOOD.md` is frozen and is not touched; these cards are a second, finer-grained
prediction made later and with more information (the error profile above did not exist
when `GOOD.md` was written), and where the two disagree **both are reported**.

**They are not a floor.** A card that predicts +8 pp and measures +1 pp is better
evidence of method than one that quietly succeeded — `CHANGELOG.md`'s own opening rule.
If either capability fails to move its number it is marked **REMOVED** and its card
stays exactly as written above.

### The ablation identity, declared now rather than discovered later

`A1 minus skill` **is** `A1-iter1`: both are *B0-agent + `cfr_resolve`, no procedure*.
They are the same configuration under two names, so the arm is **run once** and reported
in both rows with the identity stated. Running it twice would produce two numbers that
differ only by sampling and inviting a reader to treat them as independent evidence.
`A1 minus tool` is genuinely distinct — the procedure without the resolver.

---

## The three removed experiments — cards, CH-09

Written as the removals were decided, not harvested at the end. **Each one ships its
measured class size**, because a removal with a counted class is a decision and a removal
with an asserted class is a preference.

```
## Removed experiment 1 - CURRENT CFR TEXT INSTEAD OF POINT-IN-TIME

Status           : RUN. Excluded from every headline by design, not by result.
Pre-registered   : CONTEXT.md section 10, written before the corpus was built:
prediction         "accuracy collapses toward a trivial oracle, because after a failed
                   amendment the current text still lacks the change and after a
                   successful one it contains it - the current text LEAKS THE LABEL.
                   IF THE NUMBER GOES UP, THAT IS PROOF OF LEAKAGE, NOT CAPABILITY,
                   AND MUST BE REPORTED AS SUCH."
Why run it       : it is the experiment that prices the point-in-time corpus. CH-03
                   spent most of a night building text as it stood on the publication
                   date. This is the measurement of what skipping that would have
                   bought - and of how badly it would have flattered the result.
Fairness         : both arms' text goes through the IDENTICAL pipeline -
                   find-the-section -> strip_leakage -> section_text, with
                   strip_leakage and section_text reused UNMODIFIED from
                   src/cfr_pit.py. 41 EDNOTEs and 81 CITAs are stripped from the
                   CURRENT text, INCLUDING the editorial notes that define the gold
                   labels. Without that the probe would only prove we handed the
                   agent the answer key. With it, any rise is STRUCTURAL leakage in
                   the amendment state of the text itself.
                   The eCFR uses a different schema - <DIV8 N="§ 75.31"> against the
                   annual editions' <SECTION><SECTNO> - so an adapter was written in
                   the probe, NOT in src/cfr_pit.py, which is CH-03's and frozen. The
                   first extraction returned 0 of 82 for exactly that reason and the
                   count is reported rather than quietly fixed.
Evidence path    : docs/evidence/ch09-removed/leakage_probe.py, leakage-result.txt
Result           : see leakage-result.txt - published whichever direction it went.

## Removed experiment 2 - THE INTRA-RULE COLLISION DETECTOR

Status           : NOT BUILT. Cut by ruling R-01 with its class size measured.
Class size       : RECOMPUTED IN-REPO, as CONTEXT.md section 10 pre-committed:
                     43 of 2,527 items = 1.70%
                   against the two prior figures, reproducing NEITHER:
                     pilot            26/1,984 = 1.31%   (+0.39 pp)
                     naive recount    61/1,984 = 3.07%   (-1.37 pp)
                   THE CLASS SIZE DOES NOT REPRODUCE ACROSS IMPLEMENTATIONS. A third
                   number is added to the range rather than the range being narrowed,
                   which is what section 10 asked for and is the honest outcome.
Consistency      : collision-only = 0 of 2,527, so collisions are a STRICT SUBSET of
                   state-carry exactly as section 6 implies. The check passes.
Why the number   : the removal rested on three things, none of them the class size -
does not decide    - 0 of 68 labelled items contain a redesignation instruction;
                     - NARA NEVER PUBLISHES a note naming an intra-rule conflict; a
                       live probe for "conflicting amendments" returned 0;
                     - 15 of the pilot's 26 collisions are CORRECT DRAFTING.
                   A detector for a class NARA does not write notes about cannot be
                   scored against NARA's notes at any class size.
Evidence path    : docs/evidence/ch09-removed/class_sizes.py, class_sizes.txt

## Removed experiment 3 - THE ORDERED-STATE LEDGER (capability 3)

Status           : NOT BUILT. Pre-declared as counted removal #3 at ruling R-01,
                   BEFORE any code existed - the card ships, the code does not.
Why it was worth : this is the actual OFR execution model. Instruction k+1 is executed
building           against the text instructions 1..k left behind, and nothing else in
                   the system models that. It is also the mechanism behind
                   CONTEXT.md section 9's sharpest hard case, 12 CFR 702.504 -> 702.304.
                   A1 does not model execution order, and rather than pretend to, it
                   ROUTES: condition C3 of the human checkpoint fires when a
                   designation is touched twice, naming R-01 in the escalation text.
                   THE REMOVED CAPABILITY IS VISIBLE IN THE SHIPPED ARTIFACT as an
                   escalation rather than absent from it.
Class size       : RECOMPUTED IN-REPO, four readings of section 6's prose definition,
                   because no single reading reproduces the published figure:
                     A same designation touched twice (literal)   83/2,527 =  3.3%
                     B later path is a prefix/descendant         280/2,527 = 11.1%
                     C >1 instruction naming any designation     495/2,527 = 19.6%
                     D >1 instruction at all (the CEILING)       760/2,527 = 30.1%
                     published figure                            833/1,984 = 42.0%
                   *** 42.0% IS ABOVE READING D, WHICH IS THE CEILING. *** No
                   denominator reconciles either: 2,527 items under v11, 2,154
                   spec-literal, neither is 1,984. QUESTIONS.md Q23. NOT concluded
                   that 42.0% is wrong - only that it is not reproducible from the
                   shipped artifacts and therefore cannot carry a claim.
Why the removal  : R-01 cut it to measure TWO capabilities properly rather than three
stands             in a hurry. That reasoning never rested on the class size - which
                   is precisely why discovering the number is unreliable costs the
                   decision nothing. A removal justified BY a number that then failed
                   to reproduce would have been a far worse position to be in.
Evidence path    : docs/evidence/ch09-removed/class_sizes.py
```

### The blind human-time study — reserved, not run

`plan.md` CH-09 asks for 8 items timed by hand before seeing gold. **The selection rule
is committed before the selection**, the same device `GOOD.md` §9 used for the
model-sensitivity subset:

> sorted by `item_id`; **at most one item per FR document**; label alternating
> `WILL_FAIL` / `WILL_EXECUTE`; first 8. No RNG.

Eight items hand-timed is a small enough sample that *which* eight decides the answer.
Chosen afterwards they would be the eight that made the point. **The 8 reserved:**
`05-8447|75.6` · `2011-27587|80.917` · `2015-01571|1942.8` · `2015-15249|87.305` ·
`2016-03298|1150.35` · `2016-08827|522.1315` · `2016-09949|1436.3` · `2016-13651|425.606`
— **4 defective, 4 clean, 8 distinct FR documents, balanced by construction.**

`docs/evidence/ch09-removed/human_time_study.py` emits a **blind** operator brief
(instructions + section text, no label, no note, no `role`) and a worksheet, and
`assert_blind()` scans the emitted bytes for `will_fail`, `will_execute`, `editorial
note` and `could not be incorporated` and **refuses to write the file** if any appears.
The answers live in a separate sealed JSON the operator opens only after timing.

**It is an order-of-magnitude reading on how long this takes a person, at n = 8, one
operator.** It will never carry a statistical claim and its n is printed wherever it is
quoted.
