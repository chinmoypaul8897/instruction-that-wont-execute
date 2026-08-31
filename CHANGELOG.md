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
| Iteration 1 | **CH-05 `cfr_resolve`** — deterministic designation-state and quoted-anchor resolution, designation FIRST. **Observed failure it targets:** B0-agent's missed-defect rate is **0.4737** — it reads the text and still misses nearly half the defects, because reading is not checking. | *(card committed at `cb65539`, before the capability is wired into an arm; the measured result belongs to CH-08)* | **Prediction, fixed now: A1 moves the missed-defect rate below 0.25 and the gap above 20 pp.** If it does not, the card stays and says so. |
| Iteration 2 | **CH-06 `SKILL.md` + the note-emission contract** — the ordered OFR execution procedure, plus `CONTEXT.md` §5's output contract in which **`verdict` is DERIVED from `resolution_trace`**. **Observed failure it targets:** left open at commit time on purpose — it is measured from Iteration 1's errors, not guessed. The measured **prior**: on defective sections with ≥ 3 instructions B0-agent misses **11/16 = 0.6875**, against **9/25 = 0.3600** on shorter ones — `CONTEXT.md` §9's hard case as a number. | *(card committed at this SHA, before `agents/A1-SKILL.md` and `src/a1.py` exist and before any A1 call; measured result to follow)* `docs/evidence/ch06-a1/iter2/` | **Prediction, fixed now: +7 pp over Iteration 1 → A1 = 0.81, and missed-defect rate below the 0.25 guard.** If it does not move, the card stays and is marked REMOVED. |
| Iteration 3 | *(pending — CH-07 ordered-state ledger, **pre-declared as not built**)* | | |
| Final | *(pending — CH-08)* | | |

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

Observed failure : <TO BE MEASURED FROM ITERATION 1'S ERRORS, NOT GUESSED. This line is
                   deliberately left open at commit time and is filled from
                   docs/evidence/ch06-a1/iter2/iter1_error_profile.txt after Iteration 1
                   runs and before Iteration 2 runs. Writing it now would be guessing.>

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

Prediction       : +7 pp over Iteration 1, i.e. A1 = 0.81      <- COMMITTED BEFORE THE RUN
                   Secondary: missed-defect rate below 0.25, clearing the guard.

Evidence path    : docs/evidence/ch06-a1/iter2/
```

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
