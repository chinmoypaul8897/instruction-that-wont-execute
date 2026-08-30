# SPEC-FIX-1 — the verdict on the completeness-definition correction

**Session:** SPEC-FIX-1 · 2026-08-31 · Claude Code, `claude-opus-5` · BUILD (spec-edit scope)
**Question put:** is the correction specified in `prompts/SPEC-FIX-1.md` §2 a **legitimate
spec correction** or **goalpost-moving** under `CLAUDE.md` hard rule 5?
**Authorisation:** the prompt states, in its own words, *"you are authorised to refuse it …
A session that refuses this correction has done its job correctly."*

---

## VERDICT

> ## GOALPOST-MOVING — as proposed.
>
> **The diagnosis is right. The prescription is not, and it is disprovable rather than
> merely arguable.**
>
> §2a's own justifying sentence — *"`attribution_completeness` … **This is the gate
> metric.** It answers the question the gate exists to answer"* — is **false**.
> The question §2a says the gate exists to answer is *"did carry-forward put each
> instruction on the **right** section?"*. `attributed ÷ total` is **provably invariant to
> that**: an attributor that pins every element to its document's *first*-named section —
> disagreeing with the shipped attributor about **8,417 of 8,634 attributed elements
> (97.5%)** — scores **the identical 0.9865**, to six decimal places. The metric being
> promoted to gate cannot see the failure mode it is being promoted to catch.
>
> **No spec edit was made.** `CONTEXT.md` is unchanged; §2a, §2b, §2c and §2d were not
> applied. §2 is conditioned *"if and only if the verdict is LEGITIMATE"*, and it is not.

**This refusal is narrow, and it is not a rejection of the whole correction.** The
*split* — removing parse shape from an attributor's gate — is correct, and I verified it
independently. What fails is the choice of `attributed ÷ total` as the replacement gate,
made after the failure was known, when strictly harder metrics were available at zero cost
from booleans already frozen in the record. §5 below gives the path back; three of the four
steps are one line each.

---

## Method, and what is mine

`CLAUDE.md` hard rule 15 forbids relaying another agent's claim as fact. Two things were
run here, and they are kept apart on purpose:

1. **My own scripts**, committed beside this file, generating committed output:
   - `spec_fix_1_classes.py` → `classes.txt` — partitions all 2,913 unparsed elements into
     mutually exclusive buckets and asserts `sum(buckets) == n`.
   - `spec_fix_1_sabotage.py` → `sabotage.txt` — the discriminating-power test, the
     edit-coupling table, the strictly-harder ladder, and golden G1.
2. **An adversarial panel of ten subagents** (three independent recounts, five judges with
   distinct lenses including a prosecutor instructed to default to GOALPOST-MOVING, two
   harder-metric designers). Disclosed in `AI-USE.md` per hard rule 13. Panel tally:
   **4 LEGITIMATE / 1 GOALPOST-MOVING.**

**I did not adopt the panel's majority, and I did not adopt any panel number.** The
sabotage control was raised by the dissenting prosecutor; I rebuilt it from scratch, and
its first assertion is that my replay of `CONTEXT.md` §8 reproduces the frozen attributor
with **0 mismatches of 8,752** — so the control differs from the shipped attributor in
exactly one line and the comparison is valid. Every figure quoted below is from my own
scripts. Where the panel's counts differ from mine, both are shown.

---

## Q1 — are the three classes real and material? *Counted, not taken on trust.*

**Real: yes. Material: yes. A complete account of the loss: no — and the prompt does not
say they are, but its reader would assume it.**

My partition of all 2,913 unparsed elements (`classes.txt` §2, `sum(buckets)` asserted):

| bucket | n | share of unparsed | named by the architect? |
|---|---:|---:|---|
| authority citations | **591** | 0.2029 | ✅ class A |
| lead-ins, CFR section named | **548** | 0.1881 | ✅ class B |
| whole-section operations | **436** | 0.1497 | ✅ class C |
| lead-ins at part / subpart / appendix level | 155 | 0.0532 | ❌ |
| lead-ins naming no target | 91 | 0.0312 | ❌ |
| continuation fragments (operation lives in the parent) | 598 | 0.2053 | ❌ |
| part / appendix-level operations | 29 | 0.0100 | ❌ |
| document opener | 1 | 0.0003 | ❌ |
| other, no CFR target named | 464 | 0.1593 | ❌ |
| **operation AND a target, yet unparsed** | **0** | 0.0000 | — |
| **TOTAL** | **2,913** | | |

- **The three as named: 1,575 = 54.1% of the parse loss.** The residue the architect did
  not name is **1,338 = 45.9%**.
- Read as families — a part-level lead-in is the same drafting device one level out — the
  account reaches **2,449 = 84.1%**.
- Four independent counts (mine plus three panel recounts) land at **54.1%, 55.4%, 58.5%,
  59.7%**. The spread is definitional — where a "lead-in" ends and a "whole-section
  operation" begins — and every count agrees the residue is large.

**The part of the architect's case that survives every check.** The residue is *not our
bug*:

- **0 of 2,913** unparsed elements carry both an operation and an anchor-or-designation —
  i.e. there is no element the shipped parser should have completed and did not
  (`classes.txt` §4a). An independent panel re-derivation of rules P1/P4/P5 from the raw
  text agrees at 0, with a 52/5,839 control in the other direction proving the test is not
  vacuous.
- **Recoverable parser gaps: 46 elements = 1.58% of unparsed, 0.53% of the corpus** — 20
  backtick-apostrophe quoted spans P1 does not take, 1 dotted paragraph path P5 cannot
  spell, 25 out-of-vocabulary verbs (*"Lift the suspension of October 27, 2011"*, *"Stay
  the section indefinitely"*). The panel's independent estimate was ~83 (2.8%); same order,
  same conclusion.

**So parse failure genuinely is a property of Federal Register drafting, not of our
attributor, and gating an attributor on it is a real specification error.** That finding is
what makes §5's path back available.

---

## Q2 — does the definition conflate attribution with parse shape?

**Yes. Unambiguously, and the conflation is a genuine defect.**

`CONTEXT.md` §8 requires an element be *attributed* **and** *parsed into a triple*. The two
halves measure different things and only one is the attributor's:

| half | measures | whose property |
|---|---|---|
| attributed to a section | did carry-forward reach this element | **ours** |
| parsed into `(operation, anchor OR designation)` | did the drafter write a paragraph path or quote the text | **the Federal Register's** |

With 0 recoverable triples in the unparsed set, the parse half is a **corpus ceiling**. A
perfect attributor scores ~0.667 on §8's definition. **A gate no correct implementation can
ever pass is a defective gate**, and correcting it is legitimate work.

**This is not hindsight.** `docs/evidence/ch02-attributor/goldens.md` §2 rule P6 —
committed at **`98f1cff`, 2026-08-30 20:33:24**, twenty-five minutes *before* the attributor
existed (`409f14b`, 20:58:25) and before any corpus number was known — names all three
classes verbatim and states: *"Because these three shapes are structural, the completeness
ceiling is set by the corpus, not by the parser."* §6 then predicted, in writing, *"attribution
above 0.95"*, *"global completeness in [0.65, 0.80)"*, and *"the loss is in the parse half of
§8's numerator, not the attribution half."* All four predictions held. **The diagnosis
predates the number. Only the prescription does not.**

---

## Q3 — would this correction have been made if the number had come in at 0.92?

### **No.** And per the prompt's own instruction, I record that as the strongest argument against it.

The honest answer requires splitting the question, because the two halves answer differently:

| | at 0.92? | evidence |
|---|---|---|
| would the **conflation** have been *noticed*? | **Yes — it already had been** | goldens P6/§6 at `98f1cff`, before any number |
| would the **gate metric** have been *changed*? | **No** | see below |

Three documentary facts, each checkable:

1. **`prompts/CH-02.md`'s pre-registered branch table has three rows. The `≥ 0.90` row
   reads, in full: "Proceed. Report the figure."** No row instructs anyone to re-examine
   whether the definition measures the right thing. At 0.92 that row fires and `CONTEXT.md`
   §8 is never reopened.
2. **`CONTEXT.md` §8 authored the coupling deliberately and defended it in the same
   paragraph:** *"An element attributed but unparsed counts as **incomplete**, not complete —
   attribution alone is not the bar."* This was not an oversight to be discovered.
3. **CH-02 knew the whole argument and declined to make it.** Its `PROGRESS.md` entry states
   the diagnosis in the architect's exact terms and then says: *"The definition was not
   rewritten to raise the number."* CH-02 had every fact SPEC-FIX-1 has. What changed
   between CH-02 and SPEC-FIX-1 is not evidence. It is only that the number was now known
   to be failing.

**Nothing was learned between the specification and the correction except the number.** That
is the definition of the thing hard rule 5 exists to stop.

---

## Q4 — is there a version that is strictly harder rather than easier?

**Yes — at least four, every one computable from booleans CH-02 already froze, requiring no
re-run and no new labelling. None was adopted.** That is what turns "an incomplete
justification" into "selection in the flattering direction."

**The ladder** (`sabotage.txt` §4; denominator 8,752 and threshold 0.90 unchanged throughout,
so every rung is *strictly* harder than the one above):

| | metric | value | vs 0.90 |
|---|---|---:|---|
| **L0** | attributed — **§2a as proposed** | **0.9865** | PASS by 8.65 pts |
| **L1** | attributed **AND** part-consistent | **0.9066** | PASS by 0.66 pts |
| **L2** | attributed AND no *carried* part mismatch | 0.9210 | PASS by 2.10 pts |
| **L3** | attributed AND no rival-section conflict | 0.9308 | PASS by 3.08 pts |
| **L4** | attributed AND part-consistent AND no rival conflict | **0.8579** | **FAIL** |
| **F** | per-document floor: docs at ≥ 0.90 | **57/70 = 0.8143** | **FAIL** |

L1 costs one boolean already present in every record (`part_mismatch_extended`), still
passes, and cuts the margin from 8.65 points to 0.66. **A correction genuinely aimed at
attribution correctness had a passing, strictly-harder option available for free and took
the most forgiving metric on the table instead.**

**The per-document floor is not an invention.** `CONTEXT.md` §8 already requires the metric
be *"reported globally **and** per FR document,"* and says *"the per-document figure is what
CH-02's pre-registered fallback restricts on."* §2a gates on the global figure — the single
most forgiving aggregation available — and is silent about the per-document restriction the
spec already mandates. That matters downstream: CH-03 draws eval pairs *per document*, so a
document whose attribution is wrong poisons every pair from it, and a global 0.9865 hides it.

---

## Q5 — the verdict, and the three findings that decide it

### Finding 1 — the proposed gate metric cannot see the failure mode it names

`sabotage.txt` §1. A control attributor identical to the shipped one except that it carries
the **first**-named section forward instead of the **last**:

| detector | real | sabotaged | Δ metric | elements placed differently |
|---|---:|---:|---:|---:|
| `extended` | **0.9865** | **0.9865** | **0.000000** | **8,417 / 8,634 = 97.5%** |
| `spec_literal` | 0.7613 | 0.7613 | 0.000000 | 6,395 / 6,663 = 96.0% |

This is structural, not coincidental: **an element is attributed iff some section was named
at or before it — true of both rules.** `attributed ÷ total` measures only *where the first
citation appears*. It is mathematically incapable of distinguishing correct carry-forward
from arbitrary carry-forward.

Stated fairly, and this is the strongest point *for* §2a: the metric is **not** vacuous in
general. It does catch the *silent-drop* mode that killed the predecessor pilot at 0.46 — a
lead-ins-only extractor scores **0.2503 / 0.3744** and fails hard. But CH-02's own discovery
in *this* corpus (Q9) was the *silent-wrong* mode, and §2a is blind to exactly that. The
correction was written immediately after the silent-wrong mode was found, and selected the
one metric that cannot see it.

### Finding 2 — the pass exists only when two post-hoc spec edits are bundled

`sabotage.txt` §3. The prompt presents §2a and §2c as independent corrections and quotes
0.9865 as *the* attribution rate. It is not — it is the figure under the detector that §2c
creates:

| edits applied | attribution_completeness | |
|---|---:|---|
| neither — `CONTEXT.md` §8 as written | 0.5080 | FAIL |
| **§2a only** — split the metric, keep §8's sign-only regex | **0.7613** | **FAIL** |
| **§2c only** — fix the regex, keep the combined definition | **0.6643** | **FAIL** |
| **§2a + §2c** — as SPEC-FIX-1 proposes | **0.9865** | **PASS** |

**CH-02 took its gate on `spec_literal`, which is `CONTEXT.md` §8's own detector. Under it,
`attribution_completeness` is 0.7613 and FAILS.** The prompt's fact table quotes only the
`extended` figure and does not mention this. Neither edit alone converts the failure into a
pass; only their conjunction does.

### Finding 3 — the defect fixes were adopted asymmetrically, with the scores in view

Three attributor defects were on the table, **all raised by CH-02 in `QUESTIONS.md` before
SPEC-FIX-1 was written**:

| defect | effect on the gate figure | SPEC-FIX-1's treatment |
|---|---|---|
| Q9 — word-form section regex | **+22.5 pts** (0.7613 → 0.9865) | **adopted** (§2c) |
| Q10 — two further spellings | +0.31 pts at most | declined, **with reasons given** |
| Q10's third diagnostic — reset `current_section` at a `REGTEXT` PART boundary | **−8.0 pts** (0.9865 → 0.9066) | **absent — neither adopted nor declined** |

CH-02 wrote of the third: *"Resetting at a part boundary is a one-line change and **would be
an improvement**, but it is a change to a pre-registered rule after the measurement, so it is
the architect's call."* The architect's call was made for the two that were named and not for
the one that lowers the number. The fix worth +22.5 points is in; the fix CH-02 itself
endorsed, worth −8.0 points, is not mentioned. `CONTEXT.md` §8 has a phrase for this
signature, written about the leakage defect: ***"it fails silently and in the flattering
direction."***

### The corroborating case: golden G1 passes the new gate

`sabotage.txt` §6. FR Doc 2020-11897 is the document CH-02 chose *precisely because* it
demonstrates the silent-wrong mode. `QUESTIONS.md` Q9 records **20 of its 28 elements pinned
to a section they do not amend**; I measure 24 of 28 placed differently by the two detectors.

| metric on G1 | value | |
|---|---:|---|
| old completeness, `spec_literal` | 14/28 = 0.5000 | FAIL |
| **proposed `attribution_completeness`, `spec_literal`** | **26/28 = 0.9286** | **PASS** |
| **proposed `attribution_completeness`, `extended`** | **27/28 = 0.9643** | **PASS** |

**The proposed gate passes, comfortably, the one document in the corpus that was selected to
exhibit the failure the gate is said to exist for.**

---

## The strongest argument against my own verdict

Recorded because a verdict that cannot state its own weakness is not a verdict.

1. **The premise is true and I proved it myself.** Only 46 of 2,913 unparsed elements
   (1.6%) are recoverable parser gaps. Gating an attributor on Federal Register drafting is
   a real specification error, and **refusing leaves in place a gate that no correct
   attributor can ever pass.** A permanently unpassable gate teaches nothing, and that is
   its own kind of failure.
2. **Every behavioural marker of good faith is present, and a goalpost-mover shows none of
   them.** The 0.90 threshold is *not* moved. The failing 0.6643 is preserved and published
   beside the new figure. A disclosure paragraph naming hard rule 5 is written *into* the
   spec rather than the change being absorbed. The judging session was explicitly authorised
   to refuse and told that refusing is success. The prompt itself demands the Q3
   counterfactual. **This is a process trying to catch itself, and it did.**
3. **My sharpest weapon may be aimed slightly off-target.** The sabotage control attacks the
   *sufficiency of `attributed ÷ total` as a gate*. It does not attack *the split*. Both can
   be true, and if so the proportionate response is "harden the replacement metric," not
   "refuse the correction." Four of five panel judges took that view.

**I hold the verdict anyway, on the narrowest ground available:** §2a is not a proposal to be
weighed on balance, it is a **factual claim** — *"it answers the question the gate exists to
answer"* — and that claim is disproven by a control differing from the shipped attributor in
one line. A gated chunk cannot be certified on a false premise, and a strictly-harder metric
that still passes (L1 = 0.9066) was available for one boolean. When the easier option is
chosen after the failure is known and the harder one is free, hard rule 5 governs.

---

## §5 — what would make this legitimate. Four steps; the architect may re-issue.

**Nothing here requires re-running the attributor.** Every figure is already frozen.

1. **Keep the split.** `parse_completeness` does not belong in an attributor's gate — 1.6%
   of the parse loss is ours. §2a's *diagnosis* survives this refusal intact.
2. **Do not gate on `attributed ÷ total`.** Gate on a **correctness-constrained** attribution
   metric. The minimum honest version is **L1 — attributed AND part-consistent = 0.9066**,
   which costs one already-frozen boolean and still passes. If the architect wants the gate
   to bind, **L4 = 0.8579**, which fails, is the defensible harder reading. Publish
   whichever is chosen **beside the whole ladder**, so a reader sees which harder metrics
   were available and declined at the moment the definition changed.
3. **Restore the per-document floor** that `CONTEXT.md` §8 already requires and CH-02's
   branch table already restricts on. Publish **57/70 = 0.8143**, and say plainly that it
   fails.
4. **Decide the part-boundary reset in the same edit as the Q9 regex fix.** The fix that
   raises the number and the fix that lowers it must be ruled on together, or the ruling is
   made with the scoreboard visible.

**And publish the sabotage control itself.** A metric that returns 0.9865 for an attributor
that is 97.5% wrong is the sharpest single artefact this project has produced in support of
its own thesis — that a green number is not evidence of correctness. It belongs in the
submission, not in a rejected chunk's evidence folder.

---

## What was and was not done

| | |
|---|---|
| **`CONTEXT.md`** | **UNCHANGED.** §2a, §2b, §2c not applied. Not bumped to v1.1. No §13 row. |
| **§2d housekeeping** | **NOT DONE.** §2d sits under *"if and only if the verdict is LEGITIMATE"*, so the uncommitted `CONTEXT.md` working-tree edit and the untracked `prompts/CH-02.md` were left alone. The scope fence says anything not specified is a STOP; this needs its own one-line authorisation. Raised as **Q13**. |
| **`data/`** | **NOT TOUCHED.** Read-only throughout (hard rule 11); both scripts assert it. |
| **`src/`, `tests/`** | Not touched. The attributor was **not** re-run. |
| **Written** | this verdict, two evidence scripts and their committed output, `recomputed.md`, `QUESTIONS.md` Q11–Q13, `STATUS.md`, `PROGRESS.md`, `AI-USE.md`. |

**A note on what this session was.** It was given a spec edit already decided, told *"you
decide nothing,"* and told it could refuse. It refused, on a control it built and ran
itself, against a majority of its own advisory panel. Whether that was right is for the
architect; that it happened is on the record, in this order, provable from git.
