# GOOD.md — pre-registration

## THIS FILE IS EMPTY ON PURPOSE. IT IS FILLED AT CH-04.

**No threshold, no prediction and no success criterion may be written here before
CH-04**, and once written **none of them may be changed after a result is seen**
(hard rule 5: *"No moving a `GOOD.md` number after seeing a result."*).

**It must be committed and timestamped BEFORE any model arm runs.** A success
criterion written after the numbers exist is not a criterion, it is a description.
That commit is the artifact — its SHA and UTC timestamp are what make every later
claim in the README pre-registered rather than retrofitted.

CH-00 deliberately writes nothing here. The CH-00 scope fence names *"any thresholds
in `GOOD.md`"* under **Do NOT write**, and the run logger this chunk builds is the
instrument, not the criterion.

---

## What CH-04 must put here

| Item | Source |
|---|---|
| Primary metric — execution-prediction accuracy | `CONTEXT.md` §7 |
| Secondary metrics, reported beside and **never blended** | `CONTEXT.md` §7 |
| Pre-registered guards | `CONTEXT.md` §7 |
| Success thresholds | `CONTEXT.md` §7 "Success" |
| Checkpoint decision rule — STEP 0 leakage precondition, then the gap/p branches | `plan.md` CHECKPOINT |
| Ablation repetitions = **1** (final arms keep 3) | ruling R-01 item 2 |
| The effect size this n can and cannot detect | `plan.md` CH-03 fallback |

The checkpoint decision rule and the ablation-repetition count are already fixed by
`plan.md` and ruling R-01. They are **restated** here at CH-04 with their commit
timestamp; they are not re-decided.

---

## Standing constraints, already binding

- **Fairness.** Every arm runs the same model (`CONTEXT.md` §4, `QUESTIONS.md` Q1).
- **Spend.** USD 18.00 hard ceiling enforced in `src/runlog.py` against the operator's
  USD 20 limit; the logger refuses a run before it starts.
- **A red result ships as red.** The RED branch is fully specified in `plan.md` and
  has its own writing plan. Nothing here may be relaxed to avoid it.
