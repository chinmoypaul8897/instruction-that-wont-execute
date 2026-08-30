# CH-03 — point-in-time text and the eval set

Every number below has a generating script and a committed output in this directory
(hard rule 14). Zero-occurrence branches print as zeros.

**The pre-registration and the goldens were committed BEFORE the code** — `c685e80`
and `f2e8a37`, and `src/attribute_v11.py`, `src/cfr_pit.py` and `src/eval_set.py` do
not exist at either SHA.

---

## The headline

| | |
|---|---|
| **Pairs** | **38** · n = **76** |
| Target | ≥ 42 pairs (n ≥ 84) — **not reached** |
| Pre-registered branch | **[30, 42) → proceed; report the real n and state the effect size this sample can and cannot detect** |
| Instruction-count match | **exact, tolerance 0**, asserted by `tests/test_eval_set.py::test_EXACT_instruction_count_matching_is_asserted` |
| Leakage test FAILS on unstripped input? | **YES** — demonstrated on real govinfo bytes, both states committed |
| Determinism | every artefact rebuilds **byte-for-byte** (`ch03-determinism.txt`) |

**What n = 76 can detect.** `src/score.py::detectable_effect(38)` — the smallest
all-one-way discordant count clearing α = 0.05 on an exact McNemar is **6**, i.e. a
floor of **7.9 pp** at this n. A mixed discordant split needs more. This is a floor on
the detectable effect, not a power calculation, and it is stated because the
pre-registered branch requires it.

## 1a · The v1.1 re-measurement — `remeasure-v11.txt`

`QUESTIONS.md` Q14 said the case-sensitive figures did not exist and were not
recoverable by arithmetic. They exist now.

| config | word form | case | part reset | completeness | attribution | unattributable | part_mismatch |
|---|---|---|---|---:|---:|---:|---:|
| `spec_literal` | no | — | no | 0.5080 | 0.7613 | 2,089 | 671 |
| `extended_ci` | yes | insensitive | no | 0.6643 | 0.9865 | 118 | 699 |
| `extended_cs` | yes | **sensitive** | no | 0.5385 | 0.8010 | 1,742 | 622 |
| **`v11`** | yes | **sensitive** | **yes** | **0.5340** | **0.7428** | **2,251** | **115** |

**The pre-registered control passes.** `spec_literal` and `extended_ci` reproduce
CH-02's committed figures on every field, not merely to four decimals.

- Case-sensitivity alone costs **12.58 completeness points** and moves **1,669**
  attributions.
- The part reset costs a further **0.45 points** under case-sensitivity — **not** the
  8.0 measured case-insensitively. `CONTEXT.md` v1.1 said that cost "is itself
  unmeasured and is expected to differ". It differs by **17×**.
- `part_mismatch` falls **699 → 115**. That is the reset doing its job.
- **Q14(b):** §8's "~42% of AMDPARs name a section" measures **0.2503 / 0.3744 /
  0.2964** under the three readings. The architect now has a measured replacement.

**CH-02's gate outcome is unchanged and could not have changed.** 0.5340 < 0.80, so
CH-02 stays in its pre-registered documented-failure branch. A stricter detector
cannot raise a failing figure, which is why re-measuring was safe to do honestly.

## 1c · The leakage strips — `alt-element-census.txt`

**Over the 76 frozen items:** `EDNOTE` 5 · `EFFDNOTP` 1 · `CITA` 64 · `EAR` 0 —
**70 elements stripped**.

**`EAR` is 0 and the zero is warranted, not merely printed.** Q8: a strip counter that
prints zero may be looking for the wrong element name. The known-positive assertion
runs before every freeze and reports `EAR: 1` on a fixture that contains one, so the
counter demonstrably sees `EAR` when there is an `EAR` to see.

**The leakage test FAILS on unstripped input**, on real bytes, before it is accepted on
stripped input — `tests/test_cfr_pit.py::test_GF_the_leakage_test_FAILS_on_unstripped_real_bytes`:

| section | unstripped | stripped |
|---|---|---|
| `40 CFR 52.2320` | rule (b) own citation `89 FR 54360`; rule (c) `Effective Date Note`, `set forth as follows` | **0 violations** |
| `40 CFR 52.2520` | rule (b) `89 FR 50233`; rule (c) `Editorial Note`, `Effective Date Note`, `set forth as follows` | **0 violations** |

**And the test made the stripper falsifiable.** Point the stripper at ECFR element
names and the known-positive assertion RAISES —
`test_GB3_the_assertion_would_FAIL_if_the_stripper_looked_for_the_wrong_name`.

### The publishable corpus result plan.md CH-04 asks for

> **8 of 76 items (10.5%) would have contained the answer in their UNSTRIPPED text.**

`CONTEXT.md` §8 said "the per-item rate is UNKNOWN and measuring it is part of the
fix." This is that number.

### Q8's trap fired for real — `QUESTIONS.md` Q17

`CONTEXT.md` §8 names `<EFFDNOTP>`. The corpus **also** uses `<EFFDNOT>`, and in
`CFR-2015-title7-vol13.xml` `<EFFDNOTP>` occurs **0** times while `<EFFDNOT>` occurs
**4**, carrying the FR citation, the designations, *"set forth as follows"* and a
`<REVTXT>` reprint of the pending amendment. Census over 68 volumes: **379 `<EFFDNOT>`
in 26 volumes**.

**The pre-registered three-rule test caught it and a one-rule test would not have.**
All 379 carry one of the literals, so rule (c) is a complete backstop; rule (a) is
blind to it. Two pairs were excluded on `leakage-test-failed-after-strip`. **The
stripper was NOT extended** — that is a Class A spec change, and the post-hoc edit
would have raised n from 76 to 80, which is the direction this project refuses.

**Residual exposure, measured on the frozen corpus:** `EFFDNOT` 0 · `REVTXT` 0 ·
`SOURCE` 0 · `NOTE` 14 in 6 items · `APPRO` 1 · `SECAUTH` 1. And **0 of 76 frozen items
contain any `NN FR NNNN` citation at all** — stronger than rule (b) requires.

## 1d · The exclusion ladder — every rung with its positive/negative split

| rung | items | positives | negatives |
|---|---:|---:|---:|
| pool citations resolved (the top) | 85 | 85 | — |
| document completeness below floor | 0 | 0 | 0 |
| positive has no attributed instructions | 13 | 13 | 0 |
| no count-matched sibling | 22 | 22 | 0 |
| no **free** count-matched sibling | 0 | 0 | 0 |
| no title for section | 0 | 0 | 0 |
| as-of edition unavailable | 0 | 0 | 0 |
| section not in the as-of edition | 20 | 10 | 10 |
| **leakage test failed after strip** | 4 | 2 | 2 |
| **kept** | **76** | **38** | **38** |

`13 + 22 + 10 + 2 + 38 = 85`. The ladder closes, and the closure is **asserted** in
code, not eyeballed.

**Diagnostics — computed, published, never used as the eval set:** pairs at
tolerance ±1 = **56**; pairs under the 0.90 reference floor = **1**.

**Of the 13 positives with no attributed instructions, 6 are in documents that
attribute nothing at all under v11** — `QUESTIONS.md` Q15, the case-sensitivity
finding.

## 1e · The freeze

`data/evalset/` — `items.jsonl` (976,820 B), `exclusion_ladder.json`, `leakage.json`,
`manifest.json`. `data/evalset-restricted/` is the same build with the ≥ 0.90 floor
applied (`QUESTIONS.md` Q16 reading (i)): **1 pair, n = 2**, committed so the architect
can flip the eval set with one flag.

`refetch.py` rebuilds and verifies all four freezes; `--verify-only` needs no network.

## Scripts and their committed outputs

| script | output | what it shows |
|---|---|---|
| `src/attribute_v11.py remeasure` | `remeasure-v11.txt` | the four detector configurations and the CH-02 control |
| `ch03_diagnostics.py` | `case-sensitivity-cost.txt`, `floor-decomposition.txt` | the evidence under Q15 and Q16 |
| `alt_element_census.py` | `alt-element-census.txt` | Q8's trap, measured; Q17 |
| `ch03_determinism.py` | `ch03-determinism.txt` | byte-identical rebuild |
| `src/eval_set.py build` | `evalset-build.txt` | the ladder and the strips |
