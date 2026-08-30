# CH-04 — golden fixtures, hand-computed BEFORE the scorer

Hard rule 4. `src/score.py` and `src/bscript.py` do not exist at the SHA that commits
this file. Every expected value below was worked out with a pen; nothing was read back
off a run.

---

## S-A · Primary accuracy, false-defect rate, missed-defect rate

Eight items — four positives (gold `WILL_FAIL`), four negatives (gold `WILL_EXECUTE`):

| item | gold | predicted | outcome |
|---|---|---|---|
| p1 | WILL_FAIL | WILL_FAIL | ✅ |
| p2 | WILL_FAIL | WILL_FAIL | ✅ |
| p3 | WILL_FAIL | WILL_EXECUTE | ❌ missed defect |
| p4 | WILL_FAIL | WILL_EXECUTE | ❌ missed defect |
| n1 | WILL_EXECUTE | WILL_EXECUTE | ✅ |
| n2 | WILL_EXECUTE | WILL_EXECUTE | ✅ |
| n3 | WILL_EXECUTE | WILL_EXECUTE | ✅ |
| n4 | WILL_EXECUTE | WILL_FAIL | ❌ false defect |

- **accuracy** = 5 / 8 = **0.6250**
- **false-defect rate** = called WILL_FAIL on an executable = 1 / 4 = **0.2500**
- **missed-defect rate** = called WILL_EXECUTE on a defective = 2 / 4 = **0.5000**
- **success + failure = 5 + 3 = 8 = n** ✅ (`CONTEXT.md` §7 requires this asserted)

Both guard thresholds in `CONTEXT.md` §7 are ≤ 0.25, so this fixture **passes the
false-defect guard exactly at its boundary and FAILS the missed-defect guard** — which
is the point of choosing these numbers: a fixture where every guard passes cannot show
that the guards are wired up.

**An unparseable or absent verdict is a `failure`, never a silent skip.** A run that
emitted nothing counts against accuracy; dropping it would let a model raise its score
by refusing to answer.

## S-B · McNemar, exact two-sided binomial on the discordant pairs

Not the chi-square approximation: at these discordant counts the approximation is
wrong, and the whole checkpoint turns on this p-value.

| case | b (A✓ B✗) | c (A✗ B✓) | working | **expected p** |
|---|---:|---:|---|---|
| S-B1 | 8 | 2 | 2 × P(X ≤ 2 \| n=10, p=½) = 2 × (1+10+45)/1024 = 112/1024 | **0.109375** |
| S-B2 | 10 | 0 | 2 × P(X ≤ 0 \| n=10) = 2 × 1/1024 | **0.001953125** |
| S-B3 | 5 | 5 | 2 × P(X ≤ 5 \| n=10) = 2 × 638/1024 = 1.246… → capped | **1.0** |
| S-B4 | 0 | 0 | no discordant pairs; the arms are identical | **1.0** |

S-B4 is the degenerate case a naive implementation divides by zero on.

## S-C · The single-feature threshold classifier

Feature values — positives `[3, 4, 5]`, negatives `[1, 2, 3]`. The rule is
*predict WILL_FAIL if x ≥ t*, and the mirror *predict WILL_FAIL if x ≤ t* is tried too,
because a feature that is informative in reverse is still a trivial attack.

| t | positives caught | negatives correctly left | accuracy |
|---|---|---|---|
| 3 | 3,4,5 → 3 | 1,2 → 2 | 5/6 = 0.8333 |
| 4 | 4,5 → 2 | 1,2,3 → 3 | 5/6 = 0.8333 |
| 5 | 5 → 1 | 1,2,3 → 3 | 4/6 = 0.6667 |

**Best accuracy = 0.8333**, achieved at t = 3 and t = 4. **Declared tie-break: the
LOWEST threshold**, so the answer does not depend on iteration order.

## S-D · The permutation null, computed EXHAUSTIVELY

Four items, two positive; feature values `[2, 2, 1, 1]` for items `[a, b, c, d]`.
True labels: `a, b` positive. Observed best accuracy = **1.0** (perfect separation).

All C(4,2) = 6 possible label assignments, best accuracy under either direction:

| positives | feature values | best accuracy |
|---|---|---|
| a, b | 2,2 vs 1,1 | **1.0** |
| c, d | 1,1 vs 2,2 | **1.0** (the mirror rule separates it) |
| a, c | 2,1 vs 2,1 | 0.5 |
| a, d | 2,1 vs 2,1 | 0.5 |
| b, c | 2,1 vs 2,1 | 0.5 |
| b, d | 2,1 vs 2,1 | 0.5 |

**p = #{permutations ≥ observed} / #permutations = 2 / 6 = 0.3333.**

Two things this pins:

1. **The mirror rule must be counted in the null too.** Score only the `x ≥ t`
   direction and the `c, d` permutation scores 0.5, giving p = 1/6 = 0.1667 — a
   p-value that is too small because the null is weaker than the test.
2. **The observed statistic is included in its own null** (the permutation that
   reproduces the true labels is one of the six). A null that excludes it can return
   p = 0, which is not a probability any finite permutation test can produce.

## S-E · The null must respect the pairing

The eval set is **matched**: each positive has one negative from the same FR document
with the same instruction count. The exchangeable unit is therefore the **pair**, not
the item.

- **Primary null — within-pair permutation.** For each pair independently, either keep
  the labels or swap them. With *k* pairs there are 2^k assignments, every one of them
  balanced, and the null asks the right question: *can this feature tell a defect
  section from its own count-matched sibling?*
- **Diagnostic null — free permutation** of all labels. Reported beside, never instead.

Hand-computed check: with 3 pairs there are 2³ = **8** within-pair assignments, and the
free null has C(6,3) = **20**. The two are different tests and their p-values are not
interchangeable.

## S-F · Cross-validation folds must not split a document

Positive and negative come from the **same FR document**. A fold split that put one in
train and the other in test would leak. **Declared: 5-fold grouped by `frdoc`,
documents assigned to folds round-robin after sorting** — deterministic, no RNG.

Hand-computed: documents `d1..d7` sorted, 5 folds →
`d1→0, d2→1, d3→2, d4→3, d5→4, d6→0, d7→1`. Fold 0 = {d1, d6}, fold 1 = {d2, d7},
folds 2–4 one document each.

## S-G · Determinism, and the one place randomness is allowed

Hard rule 8 forbids randomness *inside* the scorer and resolver. The permutation null
needs it. **Declared resolution:** the accuracy, rate and McNemar functions are pure
and RNG-free; the permutation null uses `random.Random(20260831)`, the seed is a module
constant, it is printed in the output, and the whole run is byte-reproducible. Where
the number of permutations is smaller than the exhaustive count the test is run
**exhaustively instead**, and the output says which was used.

---

## ERRATA

The CH-02 convention: **a wrong entry is corrected in a new entry, never edited out of
the old one.** S-A..S-G above stand exactly as committed at `8dae806`.

### E-1 · S-D is the FREE null. The within-pair null over the same fixture is 2/4, not 2/6.

S-D is headed *"The permutation null"* without saying **which**, and its table
enumerates all C(4,2) = 6 free label assignments. That is the **free** null, and
`p = 2/6` is right for it.

The first test written against S-D applied it to `permutation_null`, which is the
**within-pair** null, and asserted `p = 1.0`. **The test failed.** The expectation was
wrong; the code was right. Hand-traced over the same fixture, 2 pairs give 2² = **4**
draws:

| draw | labels | best accuracy |
|---|---|---|
| keep, keep | a,b positive | **1.0** — separates |
| swap, swap | c,d positive | **1.0** — the mirror rule separates it |
| keep, swap | a,d positive | 0.5 — a 2 and a 1 in each class |
| swap, keep | b,c positive | 0.5 |

**p = 2/4 = 0.5.** Neither 1.0 (the wrong guess) nor 2/6 (the free null's answer).

S-E already said these are different tests whose p-values are not interchangeable;
E-1 is that sentence turned into two tests, both of which now run:
`test_SD_free_permutation_exhaustive_is_2_of_6` enumerates the six assignments **in
the test itself**, so the golden checks `cv_accuracy` against a hand count rather than
checking the null against itself; `test_SD_within_pair_null_over_two_pairs_is_2_of_4`
pins 0.5.

**Nothing in the implementation was changed to make either pass.**
