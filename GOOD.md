# GOOD.md — pre-registration

**Filled at CH-04, 2026-08-31, and committed BEFORE any model arm runs.** That commit
is the artifact: its SHA and UTC timestamp are what make every later claim in the
README pre-registered rather than retrofitted.

**Hard rule 5 now binds every number below: none of it may be changed after a result
is seen.** A success criterion written after the numbers exist is not a criterion, it
is a description.

At the moment of this commit the following have **not** been run: `B0`, `B0-agent`,
`B0′`, `A1`, any ablation, and the model-sensitivity subset. The **B-script** arm is
model-free and is run **after** this file is committed, from the procedure fixed in §5.

---

## 1. The primary metric — `CONTEXT.md` §7, unchanged

> Fraction of exact-instruction-count-matched `(rule, section)` items where the emitted
> `verdict` equals whether NARA published a live editorial note for that section.

Scorer: `src/score.py`. Stdlib only, no model, no network, no clock, no randomness.

**Do not change this metric.** §7: *"Every rival that changed its primary died to the
first script someone wrote."*

**An unparseable or absent verdict is a FAILURE, never a skip.** Every item in the eval
set is in the denominator of every arm, and `success + failure == n` is asserted in
code. An arm cannot raise its score by declining to answer.

## 2. Secondary metrics — reported beside, **never blended**

1. Defect-localisation accuracy on NARA's localised subset. A constant scores 0.000.
2. Failure-class recall against NARA's five-way vocabulary on the mechanism subset.
   A constant scores 0.000.
3. Instruction-level resolution-claim correctness against a deterministic oracle.
   **DIAGNOSTIC ONLY, never the primary** — a script scores 1.0 on it because it *is*
   the script.

## 3. Guards — `CONTEXT.md` §7, pre-registered, not moved

| Guard | Threshold |
|---|---|
| False-defect rate (called `WILL_FAIL` on an executable section) | **≤ 0.25** |
| Missed-defect rate (called `WILL_EXECUTE` on a defective section) | **≤ 0.25** |
| Attributor completeness | **≥ 0.90 — blocks any headline number** |

**The attributor guard is already FAILED and that is published, not absorbed.** CH-02
measured 0.5080 / 0.6643 and CH-03's re-measurement under `CONTEXT.md` v1.1 gives
**0.5340**, all against 0.90. CH-02 sits in its pre-registered *"< 0.80 — documented
failure"* branch. **The accuracy headline is therefore already withdrawn** before any
arm has run, and no result below can restore it.

## 4. The success criterion — and why it CANNOT be met on this corpus

`CONTEXT.md` §7, verbatim:

> **A1 ≥ B0-agent + 8 pp, McNemar p < 0.05, at n ≥ 84, and A1 ≥ 0.80 absolute.**

**The `n ≥ 84` clause is not satisfiable. CH-03 froze 38 pairs, n = 76.** This is
recorded here, before any arm runs, rather than discovered afterwards:

- **The criterion is NOT relaxed, and 84 is NOT moved to 76.** Hard rule 5.
- **A1 will therefore fail the pre-registered success criterion on the n clause alone,
  whatever it scores.** That is the honest consequence of a corpus that came in short,
  and it ships as such.
- The other three clauses are still evaluated and reported, because they are the ones
  that carry information about whether the capabilities worked.

**What n = 76 can and cannot detect** — `plan.md` CH-03's fallback requires this stated
here. From `src/score.py::detectable_effect(38)`: the smallest **all-one-way**
discordant count clearing α = 0.05 on an exact McNemar is **6**, i.e. a floor of
**7.9 pp**. A mixed discordant split needs more. **This is a floor on the detectable
effect, not a power calculation**, and this sample cannot detect a gap of a few points
at any p-value worth reporting.

## 5. The B-script arm and its null — fixed before it runs

- Features: the ~26 cheap, model-free features in `src/bscript.py::features`. **None
  reads the label or the editorial note**, and a test asserts it.
- Classifier: a single threshold, **both directions** (`>=` and `<=`), tie broken to
  the **lowest** threshold.
- Validation: **5-fold, grouped by FR document**, folds assigned round-robin over
  sorted documents, **no RNG**. Positive and negative come from the same document; a
  split that separated them would leak.
- **Primary null: within-pair permutation.** 2^38 draws is not enumerable, so
  **2,000 sampled draws at seed `20260831`**, declared here and printed with the
  result. The **whole procedure including feature selection** is re-run per draw, so
  the p-value prices in the search over 26 features. **The observed labelling is one
  of the draws, so p can never be 0.**
- **Diagnostic null: free permutation.** Reported beside, never instead.

## 6. The CHECKPOINT decision rule — restated from `plan.md`, not re-decided

**STEP 0 — leakage precondition, checked BEFORE any branch.** If **B0 ≥ 0.70**, the
instruction text is leaking executability. Strip the *quoted anchor text* (keep
operation and designation), re-run the gate **once**, and evaluate the branches on the
re-run numbers.

**STEP 1 — branch on the (possibly re-run) numbers. First match wins.**

| Condition | Branch |
|---|---|
| gap **< 8 pp** | **RED** |
| gap **≥ 8 pp** and McNemar **p < 0.05** | **GREEN** |
| gap **≥ 8 pp** and McNemar **p ≥ 0.05** | **AMBER** |

GREEN and AMBER both proceed to Phase 2. RED withdraws the accuracy claim and
publishes the null. **Do not tune to reach green.**

## 7. Predictions — written before the run

| Arm | Predicted |
|---|---|
| **B-script** | ~0.59, p ≈ 0.185 |
| **B0** | **≈ 0.50** (chance) |
| **B0-agent** | **≈ 0.75** |
| **A1** | **≈ 0.85** |

**Do not chase 1.00.** A saturating metric reads as a rigged baseline.

## 8. How the arms are run — fixed here so no choice is made with a number in view

- **Model: `claude-haiku-4-5-20251001`, the same model for every arm** (fairness,
  `CONTEXT.md` §4). Dated, not the floating alias. See `QUESTIONS.md` Q1's correction:
  the alias works, and it is still not used, because a reproducibility claim pinned by
  a floating alias is not pinned.
- **Temperature 0** on every haiku arm. **`claude-sonnet-5` rejects the parameter**
  (HTTP 400, measured), so the sensitivity subset runs at the model default. **That
  asymmetry is a reported limitation.** It does not touch the primary comparison,
  every arm of which is the same model at the same temperature.
- **Delivery: standard, not batch.** Q1 mandated batch for its 50% discount; batch is
  up to 24 h asynchronous and this answer is needed tonight. Every ledger row records
  `delivery=standard`, so the doubled unit price is visible rather than assumed away.
  Q1's batch ruling stands for CH-08.
- **Reps: 3** for the final arms. **Ablations: 1 rep**, per ruling R-01 item 2.
- **No truncation of the section text.** Measured before deciding: the 76 items total
  847,851 characters ≈ 212 K tokens, so three full reps of `B0-agent` cost ≈ USD 0.65.
  There is no budget reason to truncate, so nothing is truncated and no item carries a
  truncation flag. Had a cap been needed it would have been declared here with the
  count of items it touched.
- **Retries: 3, on 429/5xx and transport errors only.** A 400 or 404 is a real answer
  and is not retried. Every attempt is recorded in the trajectory.
- **Every call goes through `src/runlog.py`** — trajectory, input tokens, output
  tokens, wall-clock, imputed USD (hard rule 10). A call that dies before `finish()`
  gets a ledger row with an **empty** cost cell: unknown is not the same claim as free.
- **Item order: sorted by `item_id`**, identical for every arm and every rep.

## 9. The model-sensitivity subset — selection rule fixed before it runs

`claude-sonnet-5`, `B0` and `B0-agent`, **1 rep**, on the **first 10 pairs by sorted
`(frdoc, positive section)` = 20 items, 10 positive and 10 negative**. Label-balanced
by construction and chosen by a rule that cannot see a result.

Purpose, from `QUESTIONS.md` Q1: it reports whether the gap holds across model tiers,
and it guards against a **false RED** in which a cheap model simply fails to use the
CFR text. **If Haiku shows no gap and Sonnet does, that is a finding, not a failure.**

## 10. Spend

**USD 18.00 hard ceiling, enforced in `src/runlog.py`**, against the operator's USD 20
limit. The logger refuses a run before it starts. **It is not raised.** Committed spend
at the time of this commit: USD 0.000246, all of it the model-id probe.

## 11. Which eval set

**Primary: `data/evalset/` — 38 pairs, n = 76.** `QUESTIONS.md` Q16 records the
contradiction between `plan.md`'s scoping of the per-document completeness floor and
Q11's ruling, what each reading costs, and that the reading taken is also the one with
the larger n. **`data/evalset-restricted/` (1 pair, n = 2) is committed**, so the
architect can flip the primary with one flag and a reviewer can run either.

Both freezes verify from their SHA-256 manifests, and every CH-03 artefact rebuilds
byte-for-byte.

## 12. Standing constraints

- **Fairness.** Every arm runs the same model on the same items with the same frozen
  corpus. Any difference in resources is stated in the results table.
- **A red result ships as red.** The RED branch is fully specified in `plan.md` and has
  its own writing plan. Nothing here may be relaxed to avoid it.
- **No number in this file moves after a result is seen.**
