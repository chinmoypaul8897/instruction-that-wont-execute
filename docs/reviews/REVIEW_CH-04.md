# VERDICT: FAIL

**Chunk:** CH-04 — the scorer and the pre-registration. Gate: FULL (domain + code) + mutation.
**Reviewer:** independent adversarial session, zero shared context with the build session.
**Reviewed at:** `git HEAD = 487873db605362d8bd37dc4322a3761614270daf`, 2026-08-31.
**Read:** `CLAUDE.md`, `CONTEXT.md` §7, `plan.md` CH-04, `GOOD.md`, `src/score.py`, `src/bscript.py`,
`tests/test_score.py`, `docs/evidence/ch04-scorer/`, `docs/evidence/checkpoint/`, and git history.
**Not read, deliberately:** `PROGRESS.md`'s CH-04 entry, `STATUS.md`'s CH-04 row before forming a
view, and every prior file under `docs/reviews/`.

---

## Why FAIL, in one paragraph

**The arithmetic is right and I proved it.** A from-scratch reimplementation of `CONTEXT.md` §7,
importing nothing from the project and building even its binomial coefficients by hand, reproduces
**every** shipped checkpoint number to a delta of exactly `0.000e+00` — accuracy, both guard rates,
the gap, McNemar's `b`, `c` and `p`. Every golden in `goldens.md` reproduces by hand. The
pre-registration provably predates every model arm by 478 seconds on two independent clocks. A
non-answer is a failure by construction across sixteen refusal shapes, and no arm can buy accuracy
by declining.

**The claims around the arithmetic are not right.** `GOOD.md` — frozen under hard rule 5 — carries a
pre-registered statistical guarantee that is false in the mode the project actually runs
(**F1**), and an `n` that is wrong by six items with no errata (**F4**). A metric the CH-04 card puts
in the scorer's scope, and which `CONTEXT.md` §7 says *blocks any headline number*, is not in
`src/score.py` at all (**F2**). The rep-aggregation rule that produced the GREEN checkpoint is
declared "pre-registered" in a script written after the reps existed and is written down in no
binding document (**F3**). A function cites a section of the spec that does not mention it, is not
what `plan.md` asks for, and has no test (**F5**). And the project's own headline invariant,
`success + failure == n`, can be deleted outright without turning the suite red (**F6**).

This project's thesis is that a green suite is not evidence of correctness. Six of sixteen findings
are exactly that shape. Under the stated rule — *any deviation from the spec is a FAIL even if every
test is green* — this is a FAIL.

**None of the findings changes tonight's GREEN checkpoint verdict**, and I measured that rather than
assuming it. The remediation is errata and tests, not new numbers.

---

## Findings

| # | Severity | Finding |
|---|---|---|
| F1 | **MATERIAL** | `GOOD.md` §5 pre-registers "the observed labelling is one of the draws, so p can never be 0". At the shipped configuration (41 pairs, 2000 **sampled** draws, seed 20260831) the all-keep draw is verifiably **absent**; `p = at_least/n_draws` has no `+1` correction and `p = 0.0` is producible. Demonstrated. |
| F2 | **MATERIAL** | `src/score.py` implements **no attributor-completeness metric and no ≥ 0.90 guard**, though `plan.md` CH-04 puts it in the scorer's scope and §7 calls it the guard that *blocks any headline number*. `score()` returns two guard booleans and nothing about completeness. |
| F3 | **MATERIAL** | The 3-rep aggregation rule (**majority, ties → the FAILURE side**) is fixed in **no** binding document. It first appears in `analyse_checkpoint.py`, committed 3 min after the first arm call, whose docstring calls it "the pre-registered aggregation". It is not. Measured: no alternative changes the branch. |
| F4 | **MATERIAL** | `GOOD.md` §4 and §11 state **n = 76 / 38 pairs** and a **7.9 pp** floor. The shipped corpus is **n = 82 / 41 pairs**, floor **7.3 pp**. Rule 5 forbids editing; the project's own errata convention (append, never edit) was not applied, so the frozen pre-registration ships factually wrong. |
| F5 | **MATERIAL** | `bootstrap_ci_clustered` cites "`CONTEXT.md` §7 / `plan.md` CH-08". §7 contains **0** occurrences of "bootstrap" or "cluster"; so does all of `CONTEXT.md`. `plan.md` CH-08 asks for a **paired** bootstrap of the difference; this returns a one-arm CI. It has **no test**, and mutation M12 (resample items, not clusters) survives — the item bootstrap is measurably narrower. |
| F6 | **MATERIAL** | Mutation M07 — **deleting the `success + failure == n` check entirely** — leaves all 313 tests green. The check exists and does fire (proved in check 4), but no test in `tests/` reaches it. It is `CLAUDE.md` hard rule 14's named invariant and `GOOD.md` §1's "asserted in code". |
| F7 | **MATERIAL** | Mutation M06 — making `normalise_verdict` a **substring** match so prose containing the verdict counts — leaves all 313 tests green. Zero cost on tonight's B0 data, but CH-06's A1 emits a JSON blob containing the verdict string: strict → `None`, lenient → `WILL_FAIL`. |
| F8 | minor | §7 defines false-defect as "**called WILL_FAIL** on an executable section". `score()` charges every non-`WILL_EXECUTE`, non-answers included. On B0 that is 0.1220 vs the strict 0.0976, and 0.9268 vs 0.8780. Stricter and defensible, documented in the docstring — but stated in neither §7 nor `GOOD.md`. |
| F9 | minor | `permutation_null` restores the true labels by **assuming** `pair[0]` is the positive; `free_permutation_null`, in the same file, snapshots. Pass a valid `(negative, positive)` pair and the caller's labels are silently inverted. Not live (`reconstruct_pairs` always emits positive-first); no test would catch a reversal. |
| F10 | minor | `detectable_effect(..., power=0.80)` never uses `power`, yet emits it as `target_power` into `checkpoint-result.json` beside `min_detectable_gap_pp`. `n_needed_for_power` is named for a calculation its own docstring disclaims, has **no test**, and mutation M15 (flipping its significance comparison) survives. |
| F11 | minor | `src/score.py`'s module docstring asserts "**no randomness**. The permutation null lives in `bscript.py`" — while line 193 of the same file does `import random` for the bootstrap. `goldens.md` S-G's RNG declaration covers only the permutation null. |
| F12 | minor | The CH-04 card's "**also report** the count of items whose unstripped text would have contained the answer" appears nowhere under `docs/evidence/ch04-scorer/`, and where it does appear it disagrees with itself: `evalset-build.txt` says **5 / 82**, `README.md` and `data/evalset/leakage.json` say **3**. |
| F13 | minor | `src/score.py`, `src/bscript.py` and `tests/test_score.py` — the CH-04 deliverables — were first committed inside `067a9d9`, a commit titled *"CH-03: 38 pairs frozen…"*. `CLAUDE.md` requires atomic commits; `plan.md` fences chunk scope. |
| F14 | minor | Mutation M13 (`paired_accuracy_vectors` drops its sort) survives. Equivalent under the current caller, so low risk — but it is the third untested public function in `score.py`. |
| F15 | minor | `score()` silently ignores predictions for `item_id`s **not** in the eval set — no surplus-key count, no error — while `cv_predictions` does check the opposite direction. |
| F16 | informational | `features()` returns **30** features, not "~26". Honestly disclosed in `bscript-run.txt`. Recorded so no later reader thinks it was hidden. |

**16 findings: 7 material, 8 minor, 1 informational.**

---

## Check 1 — rerun the suite from clean, reproduce the count

**Command**

```
cd "c:/Users/chinm/micro1 engineering challenge" && python -m pytest tests/ -q
```

**Observed, first run of this review (≈ 07:44 local):**

```
278 passed in 26.15s
```

**Observed, every run after ≈ 07:48 local (including the final one):**

```
313 passed in 28.26s
```

**0 failed, 0 skipped, 0 xfail, 0 error in every run.**

The count moved **278 → 313 mid-review**, and the cause is not a defect in CH-04. A **concurrent CH-06
session** committed `tests/test_a1.py` (35 tests) at `aed8b17` / `6b61f6f`, 2026-08-31 07:47–07:50
local, while this review was running. `278 + 35 = 313`.

```
git log --format="%h %ci %s" -5
  487873d 2026-08-31 07:54:13 +0530 Q21 CLASS A: cfr_resolve cannot see a nested designation ...
  6b61f6f 2026-08-31 07:50:18 +0530 CH-06 section 2b/2c: A1 - the skill, the output contract ...
  aed8b17 2026-08-31 07:47:42 +0530 CH-06 goldens: hand-computed from CONTEXT.md section 5 ...

python -m pytest tests/ -q --collect-only | grep -oE "^tests/[a-z0-9_]+\.py" | sort | uniq -c
   35 tests/test_a1.py          <- did not exist at the first run
   ...
   38 tests/test_score.py
```

`tests/test_score.py` contributes **38** of the 313. `STATUS.md` says "suite 278 green"; that was
true when written and is now stale by the same 35. **Reported as an observation, not a finding** —
it is a live-repo artefact, not a CH-04 defect. Every mutation result below was re-established
against the stable 313 baseline.

**Evidence:** `docs/reviews/ch04-probe/mutation-report.txt` (baseline block).

---

## Check 2 — reimplement §7 independently and diff the numbers

**Script:** `docs/reviews/ch04-probe/reimplement_from_spec.py`
**Output:** `docs/reviews/ch04-probe/reimplement-from-spec.txt`
**Command:** `python docs/reviews/ch04-probe/reimplement_from_spec.py`

Written from the prose of `CONTEXT.md` §7 alone. It imports nothing from `src/`, copies no line from
`src/score.py`, and builds its binomial coefficients by a **Pascal recurrence** rather than
`math.comb`, summing the tail in exact `Fraction` arithmetic — so agreement cannot be an artefact of
a shared library call. It also computes the exact two-sided p **two ways** (sum-of-outcomes-at-most-
as-likely, and doubling the smaller tail) and asserts they agree, which independently validates the
doubling convention `src/score.py` uses.

### Result — 11 quantities, largest disagreement `0.000e+00`

```
    B0 accuracy                        mine 0.475609756098  theirs 0.475609756098  MATCH
    B0 false-defect (charged)          mine 0.121951219512  theirs 0.121951219512  MATCH
    B0 missed-defect (charged)         mine 0.926829268293  theirs 0.926829268293  MATCH
    B0 unparseable                     mine 3.000000000000  theirs 3.000000000000  MATCH
    B0-agent accuracy                  mine 0.658536585366  theirs 0.658536585366  MATCH
    B0-agent false-defect (charged)    mine 0.195121951220  theirs 0.195121951220  MATCH
    B0-agent missed-defect (charged)   mine 0.487804878049  theirs 0.487804878049  MATCH
    gap pp                             mine 18.292682926829  theirs 18.292682926829 MATCH
    McNemar b                          mine 21              theirs 21              MATCH
    McNemar c                          mine 6               theirs 6               MATCH
    McNemar p                          mine 0.005924612284  theirs 0.005924612284  MATCH

    largest absolute disagreement: 0.000e+00
    VERDICT: ALL NUMBERS REPRODUCE EXACTLY
    conventions agree exactly  True      (sum-of-<=-likely == doubled smaller tail)
```

`hits + misses == n` held on both arms. **The scorer's arithmetic is correct.**

### The one place my reading of §7 and the code differ — **F8**

§7's table gives a parenthetical for one guard only:

> | False-defect rate (**called WILL_FAIL on an executable section**) | ≤ 0.25 |
> | Missed-defect rate | ≤ 0.25 |

A literal reading puts only `pred == WILL_FAIL ∧ gold == WILL_EXECUTE` in the numerator. `score()`
puts every `pred != WILL_EXECUTE` there, non-answers included, and says so in its docstring
("*charged to the class it FAILED to get right, so an arm cannot dodge the false-defect guard by
emitting nothing*"). Both readings, measured:

```
    B0         false-defect strict 0.0976 vs charged 0.1220
               missed-defect strict 0.8780 vs charged 0.9268
    B0-agent   identical under both (0 non-answers)
```

The code's reading is **stricter**, is the right instinct, and does not flip a guard tonight. But it
is a deviation from the only definition §7 gives, and it is stated in neither `CONTEXT.md` nor
`GOOD.md` — only in a docstring. Class A/B judgement belongs to the architect; **recorded, not
resolved.**

### The majority-aggregation question — **F3**

The checkpoint aggregates 3 reps by **majority, ties resolved to the FAILURE side**.

**Is it written down anywhere binding? No.**

```
grep -rn -i "majority|aggregat|best-of-3|self-consistency|tie-break" GOOD.md CONTEXT.md plan.md PROCESS.md
  CONTEXT.md:63: | B0' | ... best-of-3 self-consistency with a published tie-break | — |
```

That single hit is `CONTEXT.md` §4's description of **B0′**, a different arm that has not been run.
`GOOD.md` §8 fixes "**Reps: 3** for the final arms" and stops there — model, temperature, delivery,
retries, item order and truncation are all pinned, and *how three reps become one verdict* is not.

The rule is declared for the first time in `docs/evidence/checkpoint/analyse_checkpoint.py`, whose
module docstring says:

> "MAJORITY VOTE ACROSS REPS is the **pre-registered** aggregation and it is stated here because it
> is a choice…"

It is not pre-registered. That file was first committed at `715eeec`, **2026-08-30 21:44:34 UTC** —
after the first arm API call at **21:41:00 UTC**. The rule was therefore chosen with reps on disk.
Calling it pre-registered is a hard-rule-15 failure inside the one document whose purpose is to make
choices unfalsifiable-after-the-fact.

**How much was that freedom worth? I measured it rather than speculating:**

```
    majority, ties -> FAILURE    B0 0.4756  agent 0.6585  gap +18.3 pp  p 0.0059
    majority, ties -> EXECUTE    B0 0.4756  agent 0.6585  gap +18.3 pp  p 0.0059
    rep 1 alone                  B0 0.4756  agent 0.6585  gap +18.3 pp  p 0.0059
    rep 2 alone                  B0 0.4756  agent 0.6585  gap +18.3 pp  p 0.0059
    rep 3 alone                  B0 0.4634  agent 0.6585  gap +19.5 pp  p 0.0037
```

**Every alternative lands GREEN.** The unwritten rule bought nothing, and the tie-branch is in fact
unreachable on this data (no item had a 3-rep tie; `unparseable = 3` came from items where a
majority still existed). So this is a **process** finding, not a numbers finding — but the fix is not
optional: the rule must be written into a binding document before A1 runs, and
`analyse_checkpoint.py`'s "pre-registered" must be retracted.

---

## Check 3 — mutation-test the scorer

**Script:** `docs/reviews/ch04-probe/mutate_score.py`
**Output:** `docs/reviews/ch04-probe/mutation-report.txt`
**Command:** `python docs/reviews/ch04-probe/mutate_score.py`

Baseline established **first**, on the unmutated tree: `exit 0 · 313 passed`. Sixteen semantic
mutations, applied **one at a time**, each verified to have landed (new text present, old text gone —
hard rule 16), each followed by the whole suite, each restored from the captured original bytes with
a SHA-256 check inside a `finally`.

```
id    mutation                                                       suite  result
M01   mcnemar: swap b and c                                          RED    CAUGHT
M02   mcnemar: flip the tail comparison, min(b,c) -> max(b,c)        RED    CAUGHT
M03   mcnemar: make it ONE-SIDED (drop the factor of two)            RED    CAUGHT
M04   mcnemar: count CONCORDANT pairs into b as well                 RED    CAUGHT
M05   binom_tail_le: off-by-one, P(X < k) instead of P(X <= k)       RED    CAUGHT
M06   normalise_verdict: LENIENT - prose containing the word counts  GREEN  *** SURVIVED ***
M07   score: DROP the `success + failure == n` check                 GREEN  *** SURVIVED ***
M08   score: charge a wrong answer to the OPPOSITE class             RED    CAUGHT
M09   score: a NON-ANSWER is charged to NEITHER guard (silent skip)  RED    CAUGHT
M10   score: a NON-ANSWER is dropped from the denominator entirely   RED    CAUGHT
M11   guards: WEAKEN both pre-registered thresholds 0.25 -> 0.50     RED    CAUGHT
M12   bootstrap: resample ITEMS instead of CLUSTERS                  GREEN  *** SURVIVED ***
M13   paired_accuracy_vectors: drop the sort                         GREEN  *** SURVIVED ***
M14   detectable_effect: require a 1-sided split, not all-one-way    RED    CAUGHT
M15   n_needed_for_power: flip the significance comparison           GREEN  *** SURVIVED ***
M16   score: DROP the duplicate-item_id check                        RED    CAUGHT

applied 16 - CAUGHT 11 - SURVIVED 5 - skipped 0
```

### Restoration — mandatory, and verified

```
sha256 before 436e8967223bfd3c4b7b02aaac4b88d0f446cf703485b29b70548b81cce15374
sha256 after  436e8967223bfd3c4b7b02aaac4b88d0f446cf703485b29b70548b81cce15374
restored byte-for-byte: True
git diff --exit-code -- src/score.py  ->  exit 0 (clean)
```

Re-verified at the end of the whole review: `git diff --exit-code -- src/` → **exit 0**, and
`git diff --exit-code -- GOOD.md CONTEXT.md plan.md tests/` → **exit 0**. Nothing under `src/`,
`data/`, `GOOD.md`, `CONTEXT.md`, `plan.md` or `tests/` was modified by this review. The only files
this session created are under `docs/reviews/`.

### What the survivors mean

The eleven catches are real and the mcnemar/guard coverage is genuinely good — M11, weakening a
**pre-registered threshold** from 0.25 to 0.50, goes red immediately, which is exactly the tripwire
hard rule 5 needs. The five survivors are the finding.

**M06 — `normalise_verdict` becomes a substring match (F7).** Every parametrised non-verdict in
`test_unparseable_verdicts_are_none_and_score_as_failures` (`None`, `""`, `"maybe"`, `"{}"`,
`"WILL FAIL"`, `"unsure"`, `42`) still returns `None` under a substring rule, so the suite never
notices. Measured cost on real data:

```
    B0-rep1..3, B0-agent-rep1..3: strict acc == lenient acc on all six reps
    non-answers a lenient parser would have converted: 0
```

Zero tonight. The exposure is CH-06:

```
    raw     {"verdict": "WILL_FAIL", "failing_designation": "(b)(4)"}
    strict  -> None          (a non-answer)
    lenient -> 'WILL_FAIL'   (M06 would silently start accepting it)
```

A1's output contract (`CONTEXT.md` §5) is exactly that blob. The strictness is correct and
load-bearing, and nothing defends it.

**M07 — the `success + failure == n` check can be deleted (F6).** In normal operation `correct` and
`wrong` are incremented on exactly the branches that partition the loop, so the identity is a
tautology and no ordinary test can reach the raise. `test_SA_success_plus_failure_equals_n_is_ASSERTED`
asserts the *arithmetic identity on the returned dict*, which holds with or without the check — it
proves the numbers add up, not that the scorer would object if they did not. I did reach the raise
(check 4), so the check is real; but it is the invariant `CLAUDE.md` hard rule 14 names by hand, and
it is undefended.

**M12 — the bootstrap resamples items instead of clusters (F5).** `bootstrap_ci_clustered` has no
test at all. Measured cost, my own reimplementation, 2000 reps, seed 424242, B0-agent:

```
    clustered by frdoc   CI [0.5385, 0.7683]  width 0.2298  sd 0.0590
    by ITEM              CI [0.5488, 0.7561]  width 0.2073  sd 0.0510
```

The item bootstrap is **narrower** — it would overstate precision, which is the direction that
flatters a result, and nothing would notice.

**M13 (F14)** is equivalent under the current caller (both arms are handed the same already-sorted
list), so it is low risk. **M15 (F10)** is a genuine hole: `n_needed_for_power` has no test whatever.

---

## Check 4 — `success + failure == n`, and a non-answer scores as a FAILURE

**Script:** `docs/reviews/ch04-probe/hostile_nonanswer.py`
**Outputs:** `hostile-nonanswer.txt`, `hostile-nonanswer-O.txt`
**Commands:** `python docs/reviews/ch04-probe/hostile_nonanswer.py` and the same under `python -O`

Proved by construction with a hostile prediction dict, not by reading the code.
**CHECK 4 RESULT: PASS.**

**1 · Sixteen refusal shapes**, each fired at a defective item and at an executable item: empty
string, whitespace, explicit `None`, **absent key**, prose refusal, policy refusal, `{}`, JSON
without the field, `"probably WILL_FAIL"`, the verdict inside a sentence, a list, a dict, a bool, a
number, `"WILL FAIL"`, and a **real** prose non-answer lifted verbatim from
`docs/evidence/checkpoint/B0-rep1.json`. All 32 cases: `n` stayed 2, `success` stayed 1, `failure`
stayed 1, `unparseable_or_absent` was 1, and the item was charged to the correct class.

```
   shapes that behaved unexpectedly: 0
```

**2 · Refusing cannot pay.** 20 items; an honest arm answers everything and gets 12 right; a hostile
arm gives the *same* 12 answers and refuses the other 8:

```
   HONEST   n 20  success 12  failure 8  accuracy 0.6000  unparseable 0
   HOSTILE  n 20  success 12  failure 8  accuracy 0.6000  unparseable 8
   refusing changed the accuracy by +0.0000  ->  NO GAIN
```

**3 · The total refusenik** — an arm that answers nothing at all:

```
   n 20  success 0  failure 20  accuracy 0.0000  unparseable 20
   false-defect 10/10 = 1.0000  missed-defect 10/10 = 1.0000   both guards fail: True
```

**4 · Is the identity ASSERTED or merely computed?** A derived count that always agrees with itself
proves nothing, so I broke the invariant genuinely: `score()` takes `n = len(items)` and then tallies
by **iterating** `items`, so a sequence whose `__len__` and iteration disagree violates it for real.

```
   len()=3, yields 2  ->  ScoreError: success 2 + failure 0 != n 3
   len()=1, yields 2  ->  ScoreError: success 2 + failure 0 != n 1
```

It raises. And because it is `if …: raise ScoreError(...)` and not a bare `assert`, it survives the
optimisation flag — the identical output under `python -O` is committed at
`hostile-nonanswer-O.txt`. That design choice is right and the docstring's reasoning for it is right.

**The check works. The caveat is F6: no test in `tests/` reaches it**, so it could be deleted
silently (mutation M07). This probe is the missing test; it should be promoted into
`tests/test_score.py`.

---

## Check 5 — was `GOOD.md` committed BEFORE any arm ran?

**Script:** `docs/reviews/ch04-probe/preregistration_order.py`
**Output:** `docs/reviews/ch04-probe/preregistration-order.txt`
**CHECK 5 RESULT: PASS**, on three mutually independent pieces of evidence.

### Timeline, UTC

```
    2026-08-30 20:37:36  ledger   earliest timestamped ledger row (arm=probe-model-id)
    2026-08-30 21:15:36  git      goldens.md committed (8dae806)
    2026-08-30 21:29:01  git      src/score.py + src/bscript.py + tests first committed (067a9d9)
    2026-08-30 21:33:03  git      GOOD.md filled with its numbers (5172092)
    2026-08-30 21:38:50  git      CH-04 3a/3b, the B-script run (91ab719)
    2026-08-30 21:41:00  run      FIRST model-arm API call (B0-rep1.jsonl)
    2026-08-30 21:44:34  git      checkpoint arm runner committed (715eeec)
    2026-08-30 21:54:27  git      first CHECKPOINT verdict, AMBER (7595562)
    2026-08-30 22:35:14  git      re-run CHECKPOINT verdict, GREEN (9786f6c)

    margin  +478 s (8.0 min)
```

**Clock 1 — git.** `GOOD.md` has exactly two commits. The CH-00 skeleton (`6abf4f2`) is 2 036 chars
and contains neither `0.25` nor `n = 76`; the filled file (`5172092`) is 9 381 chars and contains
both. The numbers therefore arrive at `5172092`, 2026-08-30 21:33:03 UTC, and nowhere earlier.

**Clock 2 — the run artefacts.** Every `docs/trajectories/arms/*.jsonl` record carries
`timestamp_utc`. The earliest across all eight arm files is `B0-rep1.jsonl` at
**2026-08-30T21:41:00.692Z** — 478 s after the pre-registration commit.

**Clock 3 — the ledger as it stood at that commit**, which is independent of both:

```
git show 5172092:docs/evidence/runs/cost_ledger.csv
  rows 10; arms present: probe-model-id
  -> NO arm row of any kind existed when GOOD.md was committed: True
```

**Also checked, and it does not undermine the conclusion:** the arm rows in `cost_ledger.csv` carry
**no** timestamp in `run_id` (only the 10 `probe-model-id` rows do), so the ledger alone cannot date
the arms — the trajectories can, and do. And the one model call that *does* predate `GOOD.md` is the
model-id probe at 20:37:36 UTC, which `GOOD.md` §10 discloses by name.

### One number in `GOOD.md` §10 is wrong

```
      imputed USD in the ledger at commit 5172092: 0.000280
      GOOD.md section 10 states:                   0.000246
      delta 0.000034  = exactly one haiku probe row
```

`GOOD.md` counted five of the six priced haiku probe rows. The error is 3.4 hundredths of a cent and
the direction is **downward** — it understates its own committed spend — so it changes nothing
material. It is recorded because this is the document whose whole value is that its numbers check out,
and it is frozen, so it needs an errata rather than an edit.

### Order relative to the goldens (hard rule 4)

`goldens.md` claims "*`src/score.py` and `src/bscript.py` do not exist at the SHA that commits this
file*". Verified:

```
git ls-tree -r --name-only 8dae806 -- src/
  src/apiclient.py  src/attribute_amdpars.py  src/attribute_v11.py
  src/harvest_ednotes.py  src/runlog.py          <- no score.py, no bscript.py
```

And the errata convention was honoured — `git diff 8dae806 HEAD -- docs/evidence/ch04-scorer/goldens.md`
is a **pure append** of the `## ERRATA` / E-1 block; S-A…S-G are byte-identical to the original
commit, exactly as the errata claims. **This is done properly and I want it on the record.**

**F13:** those three CH-04 files were nonetheless first committed inside `067a9d9`, titled
*"CH-03: 38 pairs frozen, the leakage test proven falsifiable…"*. Ordering is fine; commit hygiene
and the chunk scope fence are not.

---

## Check 6 — spec deviation, line by line against `CONTEXT.md` §7

### What is correct

- **The primary metric is §7's, unchanged.** `score()` returns `correct / n` over every item, gold
  compared by string equality against the NARA-derived label. The docstring quotes §7 verbatim. No
  reweighting, no subsetting, no blending with a secondary. ✔
- **The guard thresholds are the pre-registered ones and have not moved.** `GUARD_FALSE_DEFECT_MAX
  = 0.25`, `GUARD_MISSED_DEFECT_MAX = 0.25` in `src/score.py`; `GOOD.md` §3's table reads
  0.25 / 0.25 / 0.90, matching §7's table exactly. Mutation M11 (0.25 → 0.50) turns the suite red. ✔
- **The success criterion is quoted verbatim and not relaxed.** `GOOD.md` §4 carries §7's
  "A1 ≥ B0-agent + 8 pp, McNemar p < 0.05, at n ≥ 84, and A1 ≥ 0.80 absolute" and states in terms
  that **84 was not moved**, that the criterion is unsatisfiable, and that A1 will fail it whatever
  it scores. That is the correct handling of hard rule 5 and it is worth more than a green. ✔
- **The predictions match §7.** B-script ~0.59 · B0 ≈ 0.50 · B0-agent ≈ 0.75 · A1 ≈ 0.85. ✔
- **Determinism (hard rule 9) verified.** Re-running both evidence generators reproduces
  byte-identical output:
  ```
  sha256 before/after  1730c73b…  docs/evidence/ch04-scorer/bscript-run.txt
  sha256 before/after  2cf7c817…  docs/evidence/ch04-scorer/bscript-result.json
  sha256 before/after  57e9ce45…  docs/evidence/checkpoint/checkpoint-result.txt
  sha256 before/after  e0f00058…  docs/evidence/checkpoint/checkpoint-result.json
  ```
- **The B-script null is honest in the way that matters most.** The best feature is selected on
  pooled held-out accuracy and then that same number is reported — the classic optimistic bias — and
  the design neutralises it correctly by re-running `cv_accuracy` end to end inside every
  permutation draw, so `p = 0.2355` prices the search over all features. Folds are grouped by FR
  document with no RNG; the mirror direction is scored in the null as well as the test; the free
  null is reported beside, never instead. This is better statistics than most entrants will ship.
- **`plan.md` CH-04's "done when: scorer reproduces the B-script number with its null"** is
  satisfied: 0.6098 on `instr_chars_mean`, within-pair p = 0.2355, free p = 0.5975. ✔

### F1 — a pre-registered statistical guarantee that is false

`GOOD.md` §5, frozen:

> "**The observed labelling is one of the draws, so p can never be 0.**"

`src/bscript.py`'s module docstring, point 2:

> "The observed statistic is included in its own null. A permutation test that excludes it can
> return p = 0, which is not a probability any finite permutation test can produce."

True in **exhaustive** mode — `itertools.product` contains the all-keep tuple. **False in sampled
mode**, which is the mode the project runs in. `_within_pair_draws` returns independent coin flips;
`p_value = at_least / len(draws)` applies no `+1` correction. Direct check on the shipped
configuration:

```
    k = 41 pairs, n_permutations = 2000 -> mode 'sampled', 2000 draws, seed 20260831
    all-keep draw present : False
    all-swap draw present : False
    -> the observed labelling is NOT one of the draws.
```

And `p = 0.0` is producible — 20 pairs, positives all 1.0, negatives all 0.0, so only the all-keep
and all-swap draws (2 of 2²⁰) can reach the observed 1.0:

```
    mode sampled  n_draws 200  observed 1.0000  draws >= observed 0
    p_value 0.0                <- a finite permutation test just produced p = 0
    conventional (1+k)/(1+n)   0.004975
```

`tests/test_score.py::test_SD_p_value_can_never_be_zero` pins the property with 2 pairs and
`n_permutations=64`, which takes the **exhaustive** branch (`mode 'exhaustive'`). The mode that ships
is untested.

**Not outcome-changing tonight** — the real run had 471/2000 draws at or above observed, p = 0.2355,
because the B-script is near chance. But `GOOD.md` is frozen under hard rule 5 and now asserts a
guarantee the code does not provide. The fix is an errata plus the `(1+k)/(1+n)` estimator, not an
edit.

### F2 — the guard that "blocks any headline number" is not in the scorer

`plan.md` CH-04, scope, verbatim:

> "deterministic scorer (stdlib, no model, no network): primary accuracy, false-defect,
> missed-defect, **attributor completeness**, `success + failure == n`."

`CONTEXT.md` §7:

> | **Attributor completeness** | **≥ 0.90 — blocks any headline number** |

```
grep -n -i "completeness" src/score.py    ->  no match
grep -rn "0\.90" src/*.py                 ->  only src/eval_set.py (CH-03's per-document filter)
```

`score()` returns `guard_false_defect_pass` and `guard_missed_defect_pass` and **nothing** for
completeness. No `GUARD_ATTRIBUTOR_COMPLETENESS_MIN` constant exists. No code path blocks a headline
number. The 0.90 that does exist lives in `src/eval_set.py` as `PER_DOCUMENT_COMPLETENESS_FLOOR`, a
CH-03 eval-set filter — a different quantity with a different job.

**Mitigation, stated fairly:** `GOOD.md` §3 handles the *consequence* impeccably in prose — it
records 0.5080 / 0.6643 / 0.5340 against 0.90, places CH-02 in its pre-registered "< 0.80 —
documented failure" branch, and withdraws the accuracy headline **before any arm ran**. That is the
honest move and it is the strongest thing in the document. But the card put the metric in the
scorer, and it is not there; the guard is enforced by a human reading a Markdown file.

### F4 — the frozen pre-registration's `n` is wrong by six items

`GOOD.md` §4: "**CH-03 froze 38 pairs, n = 76**" and "`src/score.py::detectable_effect(38)` … a floor
of **7.9 pp**". §11: "**Primary: `data/evalset/` — 38 pairs, n = 76.**"

```
wc -l data/evalset/items.jsonl        ->  82
Counter(labels)                       ->  {'WILL_EXECUTE': 41, 'WILL_FAIL': 41}
checkpoint-result.txt                 ->  n = 82   41 positive / 41 negative   floor 7.3 pp
```

`STATUS.md` records the cause — CH-03's second fix, "a volume with no `<PARTS>` header excluded its
whole title silently — took **38 pairs → 41, n 76 → 82**". So the corpus grew after `GOOD.md` was
frozen. Hard rule 5 rightly forbids editing the number. The project's **own** errata convention,
quoted in `goldens.md` and executed correctly there ("*a wrong entry is corrected in a new entry,
never edited out of the old one*"), was not applied to `GOOD.md`. As it ships, a judge reading the
pre-registration is told n = 76 and a 7.9 pp floor; the shipped corpus is n = 82 and 7.3 pp.

The **conclusion** is unaffected — `n ≥ 84` fails at 82 as it failed at 76 — which is why this is a
material documentation defect rather than a result defect.

### F5 — a false citation on an untested function that is not what `plan.md` asked for

`bootstrap_ci_clustered` docstring: "`CONTEXT.md` §7 / `plan.md` CH-08: clustered by FR document."

```
  occurrences of 'bootstrap' in CONTEXT.md section 7 : 0
  occurrences of 'cluster'   in CONTEXT.md section 7 : 0
  occurrences of 'bootstrap' in CONTEXT.md (whole)   : 0
  occurrences of 'bootstrap' in GOOD.md              : 0
  plan.md CH-08 requires "paired bootstrap clustered by FR document" : True
```

Three problems. **(a)** §7 does not mention a bootstrap; the citation is invented. **(b)** `plan.md`
CH-08 asks for a **paired** bootstrap of the *difference between arms*; this returns a one-arm
accuracy CI, which cannot answer the question CH-08 poses. **(c)** Its parameters (`reps=2000`,
`seed=20260831`, `alpha=0.05`) appear in **no** pre-registration, so they remain a free choice at
CH-08 time. Combined with M12 surviving and the item bootstrap being narrower, this is the least
defended number in the packet — and it is already printed in `checkpoint-result.txt` as
"95% CI (clustered by FR doc)".

### F10 — two functions whose names and outputs claim more than their arithmetic

```
    power=0.50 -> min_discordant 6  gap 7.3171 pp  target_power reported 0.50
    power=0.80 -> min_discordant 6  gap 7.3171 pp  target_power reported 0.80
    power=0.99 -> min_discordant 6  gap 7.3171 pp  target_power reported 0.99
    power=0.00 -> min_discordant 6  gap 7.3171 pp  target_power reported 0.00
```

`power` is **dead**. It is nonetheless echoed into `checkpoint-result.json` as
`"target_power": 0.8`, sitting beside `"min_detectable_gap_pp": 7.317`, where any reader will read
the pair as an 80 %-power MDE. It is not: it is the smallest all-one-way discordant count clearing
α, which does not depend on n at all —

```
    n_pairs=5     min_discordant 6  gap 60.0000 pp
    n_pairs=41    min_discordant 6  gap 7.3171 pp
    n_pairs=1000  min_discordant 6  gap  0.3000 pp
```

— only `100 × 6 / (2 · n_pairs)` moves. **In fairness, the docstring's closing note and `GOOD.md`
§4 both say plainly "this is a floor on the detectable effect, not a power calculation", which is
honest and correct.** The defect is that the *emitted field* does not, and the emitted field is what
travels into the README.

`n_needed_for_power` has the mirror problem: the name promises a power calculation its own docstring
disclaims, it takes no target power, it has **no test**, and mutation M15 survives. On the observed
shape it returns the n it was handed:

```
    n_needed_for_power(b=21, c=6, n_items=82) -> n_needed 82 (pairs 41)
```

— because the observed data already clears α, so the search terminates at `d_try = d`. `plan.md`'s
AMBER branch asks for "the n this design would need for power"; on a genuinely under-powered shape it
does answer sensibly (`b=6, c=3, n=82` → `n_needed 337`), but nothing tests either path.

### F9, F11, F12, F15 — see `docs/reviews/ch04-probe/latent-defects.txt`

**F9** — `permutation_null` restores by assumption, demonstrated live:

```
    pairs given as (negative, positive) - a VALID matching of the same pair:
      labels before  {'neg': 'WILL_EXECUTE', 'pos': 'WILL_FAIL'}
      labels after   {'neg': 'WILL_FAIL',    'pos': 'WILL_EXECUTE'}
      corrupted      True
```

`free_permutation_null`, in the same file, snapshots and restores correctly. The two functions
disagree about how to be safe; the *primary* null is the unsafe one. Not live tonight —
`reconstruct_pairs` always emits positive-first — and `test_SD_the_null_restores_the_true_labels`
passes pairs in that same order, so no test would catch a reversal.

**F11** — `src/score.py`'s module docstring says "no randomness. The permutation null lives in
`bscript.py`", and the same file contains `import random` (line 193), `random.Random(seed)` (201) and
`rng.randrange` (204). The bootstrap is seeded and reproducible so hard rule 9 holds, but
`goldens.md` S-G declares *the permutation null* as the single place randomness is permitted and
lists "the accuracy, rate and McNemar functions" as the RNG-free set. The bootstrap arrived later and
no declaration was extended to cover it.

**F12** — `plan.md` CH-04: "**Also report:** the count of items whose **unstripped** text would have
contained the answer. That number is itself a publishable result about the corpus." It is absent from
`docs/evidence/ch04-scorer/` entirely, and where it appears it contradicts itself:

```
docs/evidence/ch03-evalset/evalset-build.txt:44  items whose UNSTRIPPED text would have
                                                 contained the answer: 5 / 82
docs/evidence/ch03-evalset/README.md:93          3 of 82 items would have contained the answer
data/evalset/leakage.json                        "items_whose_UNSTRIPPED_text_would_have_leaked": 3
```

`git show 76e2e4b:data/evalset/leakage.json` gives **5**; the value was changed to **3** at
`a7ddf90`, and `evalset-build.txt` was never regenerated. The CH-04 card's own publishable number
therefore ships in two values. (The regeneration is CH-03's territory — already FAIL ×2 and escalated
— but the *reporting obligation* is CH-04's.)

**F15** — `score()` silently ignores predictions for `item_id`s not in the eval set:

```
    2 items scored against 4 predictions (2 for unknown item_ids):
      n 2  success 2  failure 0  accuracy 1.0000   -- no error, no warning, no surplus count
```

`cv_predictions` raises when coverage is *short*; nothing checks the other direction. After a corpus
rebuild like CH-03's 76 → 82, an arm answering stale item ids passes unremarked.

### F16 — feature count, recorded for completeness

`features()` returns **30** keys against `CONTEXT.md` §4's "~26". `bscript-run.txt` prints
"`features 30 (CONTEXT.md section 4 says ~26)`" and `test_features_are_all_numeric_and_there_are_at_least_26`
asserts `>= 26`. Disclosed, within the tilde, **not a defect** — noted so no later reader thinks it
was concealed.

---

## What must change before this passes

**Blocking:**

1. **F1** — errata in `GOOD.md` retracting "p can never be 0" for sampled mode; switch
   `permutation_null` (and `free_permutation_null`) to `(1 + at_least) / (1 + n_draws)`; add a test
   that exercises the **sampled** branch.
2. **F2** — implement attributor completeness and its ≥ 0.90 guard in `src/score.py`, returning a
   `guard_attributor_completeness_pass` alongside the other two, or obtain an architect ruling that
   moves it off the CH-04 card.
3. **F3** — write the rep-aggregation rule into a binding document **before A1 runs**, and retract
   "pre-registered" from `analyse_checkpoint.py`'s docstring. The measurement showing no alternative
   changes the branch should ship beside it.
4. **F4** — errata in `GOOD.md` recording n = 76 → 82, 38 → 41 pairs, 7.9 → 7.3 pp, by the same
   append-never-edit convention `goldens.md` already uses.
5. **F5** — correct the citation; either build the **paired** bootstrap `plan.md` CH-08 asks for or
   rename this to what it is; pre-register reps/seed/alpha; add a test that fails when the resample
   unit changes.
6. **F6, F7** — promote `docs/reviews/ch04-probe/hostile_nonanswer.py` into `tests/test_score.py`
   (it kills M07), and add a test that a JSON blob containing the verdict string scores as a
   non-answer (it kills M06).

**Non-blocking but should ship:** F8 (state the charging rule in a binding document), F9 (snapshot
the labels), F10 (drop the dead `power` parameter or make it real; test both functions), F11 (correct
the docstring / extend S-G), F12 (report the number under `ch04-scorer/`, once, correctly), F13
(atomic commits), F15 (count and report surplus prediction keys).

---

## Reviewer's own disclosures

- **Nothing was committed.** The build session commits.
- **Nothing under `src/`, `data/`, `tests/`, `GOOD.md`, `CONTEXT.md` or `plan.md` was modified.**
  `git diff --exit-code` returns 0 on all of them; `src/score.py` was restored byte-for-byte after
  every one of the sixteen mutations and its SHA-256 is unchanged.
- **No network calls. No API key was read, printed or committed.** `data/` was read only.
- **A concurrent CH-06 session was writing to this repository throughout** (`agents/A1-SKILL.md`,
  `src/arms.py`, `docs/evidence/ch06-a1/`, `docs/trajectories/arms/A1-*.jsonl`,
  `docs/evidence/runs/cost_ledger.csv`, and commits `e1a2804`…`487873d`). That is the cause of the
  278 → 313 suite drift in check 1. `src/a1.py` and `src/arms.py` do not import `score`, so the
  mutation windows could not corrupt a live arm run; `tests/test_a1.py` does, so a suite run started
  by that session inside a ~30 s mutation window would have seen a spurious red. Disclosed rather
  than assumed away.
- **Probe scripts and their committed outputs, kept forever, under `docs/reviews/ch04-probe/`:**
  `reimplement_from_spec.py` / `.txt` · `mutate_score.py` / `mutation-report.txt` ·
  `hostile_nonanswer.py` / `.txt` / `-O.txt` · `claims_vs_code.py` / `claims-vs-code.txt` ·
  `latent_defects.py` / `latent-defects.txt` · `preregistration_order.py` / `preregistration-order.txt`.
