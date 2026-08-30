# REVIEW — CH-03 · point-in-time text + eval set · **ROUND 2** (re-review of the fix at `76e2e4b`)

## VERDICT: **FAIL**

---

## The one-paragraph answer

**The two findings the fix was written against are genuinely fixed, and I could not
break the eval set.** F1 is dead: my own attack, written from scratch and importing
nothing from `src/`, tops out at **0.6585** across 38 label-blind features × 3 attack
shapes, and that number sits at **p = 0.4671** inside its own within-block permutation
null (null mean 0.6482, p95 0.7073). Every *structural* feature — section sort order,
part number, position in the document, the selection rule itself — is at or below
0.5610. F2's recovered pair is real on real bytes. The strip counts, the exclusion
ladder, exact instruction-count matching and byte-for-byte determinism all reproduce
independently.

**CH-03 nevertheless fails its gate**, on four grounds that are independent of the
eval set's soundness. `plan.md` calls this gate **"FULL (domain + code) + mutation
tests"**, and: (1) the fixed rule survives a **literal revert to the defect that
failed the gate** with the suite 275-green — five of six mutations of it are uncaught;
(2) the mutation evidence the round-1 gate rests on is **false** — I re-ran M7 at
`028c06a` and it was **not** caught; (3) two published numbers do not reproduce as
stated — `32/38, p = 0.000024` and `5 of 82 items would have leaked unstripped`;
(4) an unruled **Class A** deviation from the pre-registration's own §2 is open, and
the re-run ★ CHECKPOINT's GREEN now rests on it. None of these require rebuilding the
frozen corpus.

---

## Findings, severity-ranked

### 🔴 SEVERE · R2-F1 — the F1 fix is protected by no test. Reverting it to `free[0]` leaves the suite 275-green

`src/eval_set.py:177-189` · evidence `docs/reviews/ch03-probe2/mutate2.txt`

The kept round-1 test
`tests/test_review_ch03_findings.py:57` asserts on **`data/evalset/items.jsonl`** — a
data file that a source mutation does not touch. `build_pairs`'s only unit goldens
(G-D, `tests/test_eval_set.py:37-77`) use synthetic section names `A/B/C/D`, whose
`section_sort_key` values all **tie**, so they exercise only the degenerate
`side = lower or higher or free` branch and never the balance logic at all.

Six mutations applied to the fixed code, suite re-run, tree restored and verified:

| # | mutation | suite | rebuilt pairing (negatives sorting before) |
|---|---|---|---|
| MA | `negative = min(side, …)` → **`free[0]`** — *a literal revert to the gate defect* | **NOT CAUGHT** (275 passed) | 36/50, p = 0.0026 |
| MB | `side = higher if balance >= 0 else lower` → **always `higher`** | **NOT CAUGHT** (275 passed) | 11/50, p = 0.000090 |
| MC | → **always `lower`** | **NOT CAUGHT** (275 passed) | 38/50, p = 0.000306 |
| MD | revert the `<PARTS>` fix (`return True, True` → `False, False`) | **CAUGHT** | 25/50, p = 1.0 |
| ME | nearest-candidate tie-break → **farthest** | **NOT CAUGHT** (275 passed) | 25/50, p = 1.0 |
| MF | the balance counter is **never updated** | **NOT CAUGHT** (275 passed) | 11/50, p = 0.000090 |

Only MD is caught, and only because the round-1 reviewer's F2 test calls
`volume_covers` **directly**. The rule that the whole re-review exists for is
unguarded in exactly the way round 1 diagnosed — *"a test that pins a rule is not a
test that the rule is correct"* — except it is now worse: **no test pins the rule at
all.**

`docs/evidence/ch03-evalset/goldens.md` G-D2 says the balance property is *"now
asserted on the frozen corpus forever"* with the row *"negatives sorting before their
positive | not significantly ≠ half at α = 0.05"*. **No test in the repository
computes a binomial on that quantity.** `grep -rn "binom" tests/` returns only
`test_score.py`'s tail function.

**Closed by** the kept test I added, `tests/test_review_ch03_round2_findings.py::R1`,
which rebuilds the pairing from the real corpus and asserts p ≥ 0.05. It is **GREEN
on `76e2e4b` and RED under MA** — both states shown above.

### 🔴 SEVERE · R2-F2 — the round-1 mutation table is false, and it was relayed into three shipping documents unchecked

`docs/reviews/REVIEW_CH-03.md` ("MUTATIONS — 9 designed, **9 caught**") ·
`docs/evidence/ch03-evalset/goldens.md` G-D2 ·
`docs/reviews/ch03-probe/mutate.py:75-80`

`mutate.py` decides "caught" from `proc.returncode != 0` and **never establishes a
green baseline**. I checked out `028c06a` into an isolated worktree and measured:

- baseline, full suite: **3 failed**, 248 passed, 24 skipped;
- baseline with the two review-red tests removed: **1 failed**
  (`test_freeze_is_deterministic_byte_for_byte`), 248 passed, 24 skipped;
- **M7 applied** (`negative = free[0]` → `free[-1]`), full suite: **identical** —
  1 failed, 248 passed, 24 skipped;
- **M7 applied**, `test_eval_set.py` + `test_cfr_pit.py` only: **48 passed, 8
  skipped** — byte-identical to the un-mutated baseline of the same two files.

**M7 was not caught.** It cannot have been: G-D's `free` list for positive `A` is
`["B"]`, so `free[0]` and `free[-1]` are the same element. Every "CAUGHT" in that
table is unproven, and the harness cannot distinguish a caught mutation from a
pre-existing red.

This matters beyond bookkeeping. G-D2's argument — *"M7 … **is caught**, so the suite
pinned the declared rule exactly. No test asserted the rule was UNBIASED"* — is the
build session's account of **why** F1 got through, and it is wrong in the direction
that flatters: the suite did not pin the rule either. `CLAUDE.md` hard rule 15 was
applied to F1 and F2 (both re-derived) and **not** to the mutation table.

### 🟠 MAJOR · R2-F3 — `5 of 82 items would have leaked unstripped` counts a numerator of 86 against a denominator of 82. The real figure is **3**

`src/eval_set.py:441-452` (the increment at **:450**) · `:543` ·
`data/evalset/leakage.json` · `docs/evidence/ch03-evalset/README.md` · `STATUS.md:21`

`would_have_leaked` is incremented for every member of every pair that **reached** the
leakage stage, and only afterwards does `if bad: continue` drop the two pairs that
fail the post-strip test. So the numerator ranges over **43 pairs = 86 items**, while
`items_total` and the README both say **82**.

Re-derived on the real govinfo bytes with a from-spec reimplementation
(`docs/reviews/ch03-probe2/rederive.py`, output `.txt`):

| population | items whose UNSTRIPPED text leaks |
|---|---|
| the 82 **frozen** items | **3** — `2020-11897\|90.210`, `2025-00723\|742.4`, `2025-00723\|742.6` (all positives; all strip to 0 violations) |
| the 4 items of the 2 pairs dropped on `leakage-test-failed-after-strip` | **2** — `2015-01571\|1942.5`, `2020-07837\|3.111` (these leak **before and after** stripping, which is why the pairs were dropped) |
| total considered | 5 |

`plan.md`'s CH-04 card calls this "a publishable result about the corpus", so it has
to be a rate over a stated population. The guarding test,
`tests/test_eval_set.py:235`, asserts only `0 <= n <= d["items_total"]` — it cannot
see a population mismatch. **RED test added:**
`tests/test_review_ch03_round2_findings.py::R2`.

### 🟠 MAJOR · R2-F4 — `32/38, p = 0.000024` does not reproduce, and ships with no generating script

Published in `docs/evidence/ch03-evalset/README.md`, `pre-registration.md` ERRATA
E-1, `goldens.md` G-D2, `REVIEW_CH-03.md`, `STATUS.md` and the `76e2e4b` commit
message.

I replayed the pre-fix rule (`negative = free[0]`) over the pool and restricted it to
the 38 pairs actually frozen at `028c06a`:

| method | negatives sorting before | exact two-sided p |
|---|---|---|
| exact replay, project's own `section_sort_key` | **29 / 38** | 0.001658 |
| exact replay, plain string order | **31 / 38** | 0.000116 |
| pairs reconstructed from the freeze by `(frdoc, count)`, either comparator | 29 or 31 / 38 | 0.00166 / 0.000116 |
| round-1 probe `attack_pair_order.py`, run by me on the old freeze | **27 / 33** | 0.000324 ✔ reproduces the reviewer's figure exactly |
| **committed** | **32 / 38** | **0.0000243** |

`p = 0.0000243` is exactly `binom(32, 38)`, so 32 is a real computed value — but I
cannot find the method that produces it, and **no script in the repository produces
it**. `CLAUDE.md` hard rule 14: *"Any claim from data ships its generating script
**and** its committed output under `docs/evidence/`."* The `0.8158` half of the same
table **does** reproduce (I get 62/76 exactly). The defect F1 describes is real under
every reading; the specific number is not.

### 🟠 MAJOR · R2-F5 — the +3 pairs are attributed entirely to F2. Only **one** of them is F2's

`pre-registration.md` ERRATA E-2 ("**Effect on n:** 38 pairs -> 41 pairs, n 76 -> 82")
and the `76e2e4b` commit message both place the whole gain under the F2 heading. The
old and new `section-not-in-as-of-edition` ladder details show otherwise:

| pair | why it was excluded at `028c06a` | recovered by |
|---|---|---|
| `2016-16399` · 13 CFR 125.6 | `positive: no-volume-covers-this-part` | **F2** ✔ |
| `2021-04453` · 21 CFR 556.360 | `negative: 516.812 section-not-in-as-of-edition` | **F1** — the balanced rule picked `556.300` instead |
| `2026-08556` · 34 CFR 682.405 | `negative: 674.39 section-not-in-as-of-edition` | **F1** — the balanced rule picked `685.303` instead |

The round-1 reviewer predicted F2 alone would give **39 pairs / 78 items** and was
right. Two consequences beyond the mis-attribution:

- **n is coupled to the negative-selection rule.** When the chosen negative fails to
  resolve in the as-of edition, `cmd_build` drops the whole pair rather than trying
  the next candidate (`src/eval_set.py:428-440`). A different-but-equally-valid
  selection rule yields a different n. This is not new at `76e2e4b`, but it is now
  load-bearing for a number that changed.
- All three recovered pairs verify as real: sections present exactly once as an
  eligible `<SECTION>` in the stated edition, correct title/part/year, strip cleanly,
  0 post-strip violations. Confirmed on the real bytes.

### 🟠 MAJOR · R2-F6 — an open, unruled Class A deviation from the pre-registration selects the eval set with the larger n

`docs/evidence/ch03-evalset/pre-registration.md` §2 vs `src/eval_set.py:70-72`
(`DEFAULT_FLOOR = 0.0`) · `QUESTIONS.md` Q16

The pre-registration, committed **before** any count existed, says: *"the
**restricted** set is the primary eval set. That is the architect's ruling and it is
fixed here, before the count is known, **precisely so that it cannot later be chosen
for its effect on n**."* The shipped primary is `data/evalset/` at `--floor 0.0`
(41 pairs); the restricted build is `data/evalset-restricted/` (**1 pair, n = 2**,
verified).

Q16 records the contradiction honestly, names the uncomfortable fact, offers two
number-independent arguments, builds both sets — and then **ends by asking the
architect for the ruling it has already acted on**: *"What is wanted from the
architect: a ruling on whether (i) or (ii) is the eval set."* Hard rule 3: Class A →
**STOP, ask the architect**. The queue continued instead, CH-04 scored on it, and the
re-run ★ CHECKPOINT at `9786f6c` (GREEN, +18.3 pp, p = 0.0059) rests on it. This
pre-dates the fix and round 1 did not flag it; it is unresolved at the gate, so it is
a gate finding.

*(Q16 also states "Reading (ii) is the frozen primary: **50 pairs, n = 100**". The
frozen primary is 41 pairs / n = 82; 50 is the pairing yield before the
text-resolution rungs.)*

### 🟡 MINOR · R2-F7 — `strip_counts.EDNOTE` is a perfect one-sided label indicator inside `items.jsonl`

`docs/reviews/ch03-probe2/leak_hunt2.txt`

| `strip_counts.EDNOTE` | WILL_FAIL | WILL_EXECUTE |
|---|---:|---:|
| non-zero | **3** | **0** |
| zero | 38 | 41 |

The per-item strip counters are the fingerprint of the very elements that carry the
label, frozen into the same record as the input. `CONTEXT.md` §8 requires per-element
strip counts *"in the freeze manifest and in the README"*; putting them per item is a
choice, and it re-opens a (weak, but 100%-precision) channel. **Latent, not active:**
`src/arms.py:104-141` builds its prompt from `cfr_title, section, frdoc,
publication_date, section_text, instruction_count, instructions` only, and
`src/bscript.py:59-110` does not read `strip_counts`. No test guards it. Same shape,
weaker: `chars_unstripped − chars_stripped` means 130.8 (positives) vs 101.9
(negatives).

### 🟡 MINOR · R2-F8 — `cfr_part` is wrong for 3 frozen items

`2016-08827|522.1193` carries `cfr_part: "524"`; `2026-03157|1037.205` and
`|1037.615` carry `"1036"`. This is `CONTEXT.md` §8's known `regtext_part` extraction
defect landing in the freeze. **Pre-existing** — identical at `028c06a` — and nothing
currently consumes the field, but `resolve_text` selects candidate volumes with it, so
a wrong part is a silent n-suppressor for any multi-volume title where the wrong
part's volume does not also contain the section.

### 🟡 MINOR · R2-F9 — `src/eval_set.py`'s own docstring still declares the rule the file replaced

`src/eval_set.py:23-25`: *"The negative chosen for a positive is the **FIRST** in
sorted order among free count-matched siblings — declared in the pre-registration, so
it is **independent of any label**."* The body at :177-189 implements the balanced
rule, and ERRATA E-1 records that "independent of any label" was tested and found
**false**. Two shipping statements of the same rule disagree inside one file — hard
rule 16's failure mode. **RED test added:**
`tests/test_review_ch03_round2_findings.py::R3`.

### 🟡 MINOR · R2-F10 — assorted

- `src/cfr_pit.py:200` — the new `declares_range` key is **dead**: computed, never
  read anywhere in the repository. The F2 fix keys off `part_lo is None` instead, so
  a `<PARTS>` header that merely fails to parse (or sits past the 8,000-byte head
  slice `volume_index` reads, `src/cfr_pit.py:496`) is now indistinguishable from a
  genuine single-volume title. **Measured and currently harmless:** 1 of 421 indexed
  volumes has no parsed range and it is the real single-volume title 13; 0 of 82
  frozen items resolve to a wrong title, part or year; 0 items resolve to more than
  one eligible `<SECTION>`.
- `tests/test_eval_set.py:141` — docstring says *"Measured at 0 of 76"*; n is 82.
- The **true pairing is not persisted** anywhere in `data/`. `items.jsonl` has no
  `pair_id` and the `kept` ladder rung carries no detail, so downstream
  (`docs/evidence/ch04-scorer/run_bscript.py:54-68`) reconstructs pairs by
  `(frdoc, instruction_count)` + sorted zip, which does **not** recover the builder's
  pairing for the 3 multi-pair documents. Harmless for a within-pair permutation null
  (exchangeability is preserved), but "exact instruction-count matching" is only
  assertable as a per-document multiset equality.

---

## IS THE F1 FIX REAL?

**Yes. My judgement is that the fix is real, not cosmetic, and that the eval set is
now sound as an artefact.**

I wrote `docs/reviews/ch03-probe2/attack_labelblind.py` from scratch, importing
nothing from `src/`, reading `label` / `role` / `note_text` / `note_node` /
`section_text` **only to score**. The eval set's own matched design hands the attacker
its blocks for free: `(frdoc, instruction_count)` recovers 38 blocks, every one of
them exactly half positive — verified, and that verification is the attack's licence.
38 features × {block-halving within count blocks, block-halving within FR documents,
best global threshold}.

**Best label-blind accuracy reached: 0.6585 (54/82).**

| feature | best | what it is |
|---|---:|---|
| `instr_n_anchor` | 0.6585 | how many instructions carry a quoted anchor |
| `instr_chars_mean`, `instr_chars_total` | 0.6585 | length of the instruction text |
| `chars_stripped`, `chars_unstripped` | 0.6585 | length of the section text |
| `chars_delta` | 0.6341 | bytes removed by the stripper |
| **`section_lex`** | **0.5366** | the round-1 attack's own feature |
| **`section_num`** | **0.5244** | numeric section sort order |
| `part_num`, `ord_min/mean/max`, `vol_*`, `strip_*`, `doc_*` | ≤ 0.5976 | — |

Against its own **within-block permutation null over the same 38-feature bank**
(500 draws, seed 20260831): null mean **0.6482**, p95 **0.7073**, max 0.8049,
**p(best-of-bank ≥ observed) = 0.4671**. The best number I can reach is ordinary
noise for a bank that size, and it lives entirely in *corpus substance* (text length,
anchor counts) — the territory the sanctioned B-script arm already occupies at 0.6098
with its own p = 0.2355.

I then attacked the **selection rule directly**
(`docs/reviews/ch03-probe2/attack_selection_rule.py`): given the two members and the
document's full section list from `data/attribution-v11/`, ask which member is "the
nearest free count-matched sibling of the other" — the exact asymmetry the new rule
creates. **0.5122.** Doc-structure features (`rank_in_doc`, `n_siblings_lower/higher`,
`min_dist_to_any_sibling`, `sections_in_doc`) top out at 0.5610.

**Did the fix introduce a new bias?** (`docs/reviews/ch03-probe2/new_bias_probe.py`)

- Realised sequence over the 41 frozen pairs: **21 before / 20 after, exact two-sided
  p = 1.0000** — reproduces the committed figure exactly.
- Split by branch: the 26 pairs where **both sides existed** are 13/13 (p = 1.0); the
  15 **structurally forced** pairs are 8/7 (p = 1.0). The balance mechanism is not
  hiding a forced-side imbalance.
- **Alternation:** the free subsequence alternates on 13 of 25 adjacent gaps — not the
  perfect alternation the `balance >= 0` rule could have produced. An attacker who
  orders the recovered pairs and guesses the alternating phase scores **0.5122**.
- **Correlation with document properties:** Pearson r with `negative-sorts-before` is
  +0.198 (doc AMDPAR count), +0.098 (free candidates), +0.096 (count-matched
  candidates), +0.013 (doc completeness), +0.018 (instruction count). Nothing
  approaching significance at n = 41.
- **Counterfactual:** the old `free[0]` rule on the same pool gives 36/50,
  p = 0.002602. The direction and the defect are confirmed.

**Leakage.** The three-rule test fails on unstripped real bytes and passes on
stripped, demonstrated by me on 5 items (3 frozen, 2 excluded). Hunting wider than
`plan.md` requires: **0** frozen items contain any FR-citation shape
(`NN FR NNNN`, `NN F.R. NNNN`, `Fed. Reg.`, `[NN FR`); the longest word-run shared
between a positive's `note_text` and its `section_text` is 8 words of statutory
boilerplate; no leakage element survives in any frozen `<SECTION>` tree. The one
residual channel is R2-F7, and it is outside `section_text`.

---

## WHAT I REPRODUCED

| claim | committed | my independent value | ✓ |
|---|---|---|---|
| suite from clean | 275 green | **275 passed, 0 failed, 0 skipped** | ✓ |
| pairs / n | 41 / 82 | 41 / 82 | ✓ |
| label-blind sort-order attack, post-fix | 0.5610 | **46/82 = 0.5610** | ✓ |
| the same attack on the pre-fix freeze | 0.8158 | **62/76 = 0.8158** | ✓ |
| negatives sorting before, post-fix | 21/41, p = 1.0000 | **21/41, p = 1.0000** | ✓ |
| negatives sorting before, **pre-fix** | **32/38, p = 0.000024** | 29/38 (p = 0.00166) or 31/38 (p = 0.000116) | ✗ **R2-F4** |
| round-1 reviewer's own figures | 0.7763, 27/33, p = 0.000324 | identical | ✓ |
| ladder top (resolved pool) | 85 | 85 | ✓ |
| `positive-has-no-attributed-instructions` | 13 | 13 | ✓ |
| `no-count-matched-sibling` | 22 | 22 | ✓ |
| `no-free-count-matched-sibling` | 0 | 0 | ✓ |
| `section-not-in-as-of-edition` | 7 pairs | 7 pairs (50 reach text resolution, 41 kept) | ✓ |
| `leakage-test-failed-after-strip` | 2 pairs | 2 pairs, both verified on real bytes | ✓ |
| ladder closes | 13+22+0+0+0+7+2+41 = 85 | 85 | ✓ |
| strip counts over the frozen corpus | EDNOTE 3 · EFFDNOTP 0 · CITA 65 · EAR 0 = 68 | **identical**, from a from-spec reimplementation | ✓ |
| every item's frozen `section_text` | — | **token-identical** to my own independent strip, 82/82 | ✓ |
| items whose UNSTRIPPED text would leak | **5 of 82** | **3 of 82** (5 of the 86 considered) | ✗ **R2-F3** |
| leakage test FAILS on unstripped input | asserted | reproduced on real govinfo bytes | ✓ |
| 0 frozen items contain any `NN FR NNNN` | 0 | 0 (and 0 for three other citation shapes) | ✓ |
| residual element census | NOTE 21 in 7 items · APPRO 2 · SECAUTH 4 | NOTE 21 · APPRO 2 · SECAUTH 4 | ✓ |
| exact instruction-count matching | tolerance 0, asserted by a test | holds in the frozen data; `len(instructions) == instruction_count` for all 82 | ✓ |
| v1.1 detector table (0.5080 / 0.6643 / 0.5385 / 0.5340) | README §1a | reproduces from `completeness_v11.json` on every field | ✓ |
| 6 of the 13 no-instruction positives are in zero-attribution documents | 6 | 6 | ✓ |
| diagnostics: tolerance ±1 = 56, 0.90 floor = 1 | — | 56, 1 | ✓ |
| restricted set | 1 pair, n = 2 | 1 pair, n = 2 | ✓ |
| detectable effect: 6 discordant, 7.3 pp floor | — | `binom(0,6)*2 = 0.03125 ≤ 0.05`; 6/82 = 7.32 pp | ✓ |
| determinism | byte-for-byte | **full rebuild to a scratch dir → all three SHA-256s identical** | ✓ |
| `refetch.py --verify-only` | green on all four freezes | 4/4, 6/6, 2/2, 3/3, 3/3 | ✓ |
| `evalset-build.txt`, `alt-element-census.txt`, `ch03-determinism.txt` | committed | re-run reproduces each exactly (census differs in line endings only) | ✓ |
| `data/ednotes/`, `data/amdpars/` untouched | read-only | `git log 067a9d9..HEAD -- data/ednotes data/amdpars` is **empty**; last touched at `d682997`/`5207d16` | ✓ |
| goldens predate the code | `c685e80`, `f2e8a37` | `goldens.md` + `pre-registration.md` added at `c685e80` 02:14; `src/cfr_pit.py` and `src/eval_set.py` **do not exist** at `c685e80` or `f2e8a37`, first appearing at `067a9d9` 02:59 | ✓ |
| round-1 mutations: 9 designed, 9 caught | 9/9 | **M7 re-run at `028c06a`: NOT caught** | ✗ **R2-F2** |
| the 3 recovered pairs are real | — | all 3 present exactly once as an eligible `<SECTION>`, right title/part/year, strip clean, 0 post-strip violations | ✓ |
| the +3 is F2's | ERRATA E-2 | **1 of 3 is F2's; 2 are F1's side effect** | ✗ **R2-F5** |

**Could not reproduce:** `32/38, p = 0.000024` (R2-F4) and `5 of 82` (R2-F3).
**Could not verify:** the round-1 mutation table beyond M7 — the harness has no green
baseline, so none of its nine verdicts is evidence either way.

---

## MUTATIONS

Harness: `docs/reviews/ch03-probe2/mutate2.py`. Each patch is asserted to have landed
(new text present, old occurrence gone) before the suite runs; the tree is restored
and `git status src/` verified empty afterwards. Every mutation that touches
`build_pairs` also has its **rebuilt pairing** measured in a fresh interpreter,
because the suite's frozen-corpus tests cannot see a source mutation.

| # | mutation | suite | rebuilt bias |
|---|---|---|---|
| MA | negative-selection reverted to `free[0]` | **NOT CAUGHT** | 36/50, p = 0.0026 |
| MB | balance counter always picks `higher` | **NOT CAUGHT** | 11/50, p = 0.000090 |
| MC | balance counter always picks `lower` | **NOT CAUGHT** | 38/50, p = 0.000306 |
| MD | `<PARTS>` fix reverted | **CAUGHT** | — |
| ME | nearest tie-break → farthest | **NOT CAUGHT** | 25/50, p = 1.0 |
| MF | balance counter never updated | **NOT CAUGHT** | 11/50, p = 0.000090 |

**1 of 6 caught.** Restored: `git status --porcelain src/ tests/ data/` is empty.

Historical re-check, in an isolated `git worktree` at `028c06a`: **M7 was not
caught** — mutated and un-mutated runs of `test_eval_set.py` + `test_cfr_pit.py` are
both `48 passed, 8 skipped`, and the full-suite result is identical too.

---

## Kept tests added by this review

`tests/test_review_ch03_round2_findings.py` — do not weaken these.

| id | state | what it pins |
|---|---|---|
| **R1** | **GREEN** on `76e2e4b`, **RED** under MA (both shown) | the negative-selection rule is unbiased **when run**, not merely in the file it once produced — the mutation guard R2-F1 says is missing |
| **R2** | **RED** | the unstripped-leak count must be measured over the population it is published against (3, not 5) |
| **R3** | **RED** | `src/eval_set.py`'s docstring must not declare the rule the file replaced |

Suite with them: **276 passed, 2 failed**. A red result ships as red.

---

## What must happen before CH-03 can pass

1. **Close R2-F1.** Keep R1 (or an equivalent), and add a golden for `build_pairs`
   whose section names do **not** tie, so MA/MB/MC/ME/MF are caught by unit tests
   rather than by a data file.
2. **Correct R2-F3** — publish the leak count over the frozen 82 (**3**), or publish
   both populations explicitly. No rebuild of `data/` is needed; the artefact is
   right, the number beside it is not.
3. **Correct or withdraw `32/38, p = 0.000024`** (R2-F4) and ship the script that
   produces whatever replaces it, per hard rule 14. My replay gives 29/38.
4. **Correct the attribution of the +3 pairs** (R2-F5) in ERRATA E-2, the README and
   `STATUS.md`: F2 recovered **one** pair, F1's reselection recovered two.
5. **Withdraw "9/9 mutations caught"** from `REVIEW_CH-03.md`, `goldens.md` G-D2 and
   `STATUS.md`, and state that the round-1 harness had no green baseline (R2-F2).
6. **Get the architect's ruling on Q16** (R2-F6) before any further number is computed
   on `data/evalset/`.
7. Fix the docstring (R2-F9) and the small items in R2-F10.

**None of this requires rebuilding the frozen corpus, and none of it moves a
threshold.** The eval set survived every attack I could write. What failed is the
evidence around it.

---

## Provenance of this document

Written by a fresh session with zero shared context, from `CLAUDE.md`, `CONTEXT.md`
§7–§8, `plan.md`'s CH-03 card, `docs/reviews/REVIEW_CH-03.md` and the diff
`028c06a..76e2e4b`. `PROGRESS.md` and `STATUS.md` were not read until after the
findings were fixed. Nothing in the round-1 verdict or the fix commit message was
taken on trust; every number in it that I quote, I re-derived (hard rule 15), and the
two I could not re-derive are findings. All probes are in
`docs/reviews/ch03-probe2/` with their committed outputs. Nothing outside
`docs/reviews/` and `tests/` was modified; `git status --porcelain src/ data/` is
empty.

Repository state reviewed: `src/`, `tests/` and `data/` as at **`76e2e4b`**
(unchanged through `56cae9c`, which was pushed by another session while this review
ran and touches only docs, evidence and trajectories).
