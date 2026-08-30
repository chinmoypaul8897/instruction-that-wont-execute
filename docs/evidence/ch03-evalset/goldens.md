# CH-03 — golden fixtures, hand-computed BEFORE the code

Hard rule 4: *"Hand-compute expected outputs **before** writing the code. A test whose
expected value came from the code it tests proves nothing."*

Every expected value below was worked out by hand, or read off the raw XML with a
generic `xml.etree` tag count — **never** from `src/cfr_pit.py`, `src/attribute_v11.py`
or `src/eval_set.py`, none of which existed when this file was committed. Each golden
is pinned by a test in `tests/test_ch03.py`.

The ERRATA convention from CH-02's goldens carries over: **a wrong number is corrected
in a new entry, never edited out of the old one.**

---

## G-A · Edition-year selection — hand-computed

The point-in-time text is *"the edition preceding its rule's publication date"*
(`prompts/NIGHT-RUN.md` 1b). Operationalised in the pre-registration as **the latest
annual edition whose statutory revision date is STRICTLY BEFORE the publication
date.** Strictly-before matters: an edition revised *on* the publication date could
already carry the amendment under test.

CFR statutory revision dates — titles **1–16** Jan 1 · **17–27** Apr 1 · **28–41**
Jul 1 · **42–50** Oct 1.

| # | title | revision date | publication date | working | **expected edition** |
|---|---|---|---|---|---|
| A1 | 40 | Jul 1 | 2005-05-18 | 2004-07-01 < 2005-05-18; 2005-07-01 > it | **2004** |
| A2 | 5 | Jan 1 | 2022-05-25 | 2022-01-01 < 2022-05-25 | **2022** |
| A3 | 47 | Oct 1 | 2026-06-10 | 2025-10-01 < 2026-06-10; 2026-10-01 > it | **2025** |
| A4 | 26 | Apr 1 | 2020-01-05 | 2019-04-01 < 2020-01-05; 2020-04-01 > it | **2019** |
| A5 | 12 | Jan 1 | 2019-12-31 | 2019-01-01 < 2019-12-31; 2020-01-01 > it | **2019** |
| A6 | 5 | Jan 1 | **2022-01-01** | 2022-01-01 is **not strictly before** itself | **2021** |
| A7 | 49 | Oct 1 | 2016-09-30 | 2015-10-01 < it; 2016-10-01 > it | **2015** |

A6 is the boundary case the word *strictly* exists for.

## G-B · Leakage-strip counts on real govinfo bytes — the known-positive

Source: `CFR-2024-title40-vol5.xml`, 5,524,321 B — the same file `CONTEXT.md` §8 took
its containment measurement on. Counted with a generic `xml.etree` walk over the raw
file, **not** with the stripper under test.

**B1 — whole-volume element totals.** These reproduce `CONTEXT.md` §8's own figures,
which is the check that the reader of §8 and the reader of this file are looking at
the same bytes.

| element | total in volume | of which inside a `<SECTION>` | §8 says |
|---|---:|---:|---|
| `EDNOTE` | **28** | **26** | "of 28 `<EDNOTE>` elements, 26 sit inside a `<SECTION>` block" ✅ |
| `EFFDNOTP` | **2** | **2** | "both `<EFFDNOTP>` elements do" ✅ |
| `CITA` | **255** | **252** | "252 of 255 `<CITA>` elements do" ✅ |
| `EAR` | **5** | **1** | §8 names `<EAR>` but publishes no count. **5 / 1 is new here.** |
| `SECTION` | **313** | — | |

**B2 — the two per-section known-positives.** A stripper that returns zero for these
is looking for the wrong name, and G-B is the assertion that stops that zero being
believed.

| section | `EDNOTE` | `EFFDNOTP` | `CITA` | `EAR` | expected strips |
|---|---:|---:|---:|---:|---:|
| `§ 52.2320` (outer) | 0 | 1 | 1 | 1 | **3** |
| `§ 52.2520` (outer) | 1 | 1 | 1 | 0 | **3** |

**B3 — a synthetic known-positive, so the assertion does not depend on one file.**
A fragment carrying exactly `EDNOTE`×2, `EFFDNOTP`×1, `CITA`×3, `EAR`×1 must report
exactly those four counts and a total of **7**. Fixture in `tests/test_ch03.py`.

## G-C · The v1.1 attributor — a six-element hand trace

Six `<AMDPAR>` texts in document order, with the `<REGTEXT>` `PART` each sits in. The
sequence is built to separate the two v1.1 changes from each other and from v1.0.

| # | part | AMDPAR text |
|---|---|---|
| 1 | 52 | `1. The authority citation for part 52 continues to read as follows:` |
| 2 | 52 | `2. Section 52.2320 is amended by revising paragraph (c).` |
| 3 | 52 | `a. Revise paragraph (c)(1);` |
| 4 | **75** | `3. Appendix A to part 75 is amended by revising the title of section 1.1.` |
| 5 | 75 | `4. Amend § 75.6 by removing paragraph (b).` |
| 6 | 75 | `b. Remove paragraph (c).` |

Element 4 is `CONTEXT.md` §8's own worked example of the case-insensitivity defect
(Q12(c)), and it also sits across the part boundary — so it is the single element the
two v1.1 changes both act on.

**Parse — detector-independent** (operation AND at least one of anchor/designation):

| # | operation | designation | `parsed` | why |
|---|---|---|---|---|
| 1 | none | none | **false** | no revise/add/remove/redesignate, and no *amend* either |
| 2 | revise | `(c)` | **true** | |
| 3 | revise | `(c)(1)` | **true** | |
| 4 | revise | none | **false** | *"the title of section 1.1"* carries no parenthesised designation |
| 5 | remove | `(b)` | **true** | *removing* beats the *Amend* fallback |
| 6 | remove | `(c)` | **true** | |

**Attribution — hand-traced per detector:**

| # | `spec_literal` | `extended_ci` | `extended_cs` | **`v11`** |
|---|---|---|---|---|
| 1 | — | — | — | — |
| 2 | — (no sign) | 52.2320 | 52.2320 | **52.2320** |
| 3 | — (carries null) | 52.2320 | 52.2320 | **52.2320** |
| 4 | — | **1.1** (lowercase matched) | — (carries 52.2320) → **52.2320** | **—** (part 52→75 resets, and lowercase is not matched) |
| 5 | 75.6 | 75.6 | 75.6 | **75.6** |
| 6 | 75.6 | 75.6 | 75.6 | **75.6** |

**Expected totals, hand-computed:**

| detector | attributed | attribution rate | complete (attributed ∧ parsed) | completeness | unattributable |
|---|---:|---:|---:|---:|---:|
| `spec_literal` | 2 | 2/6 = **0.3333** | 2 | 2/6 = **0.3333** | 4 |
| `extended_ci` | 5 | 5/6 = **0.8333** | 4 | 4/6 = **0.6667** | 1 |
| `extended_cs` | 5 | 5/6 = **0.8333** | 4 | 4/6 = **0.6667** | 1 |
| **`v11`** | **4** | 4/6 = **0.6667** | **4** | 4/6 = **0.6667** | **2** |

Three things this golden pins, each of which is a claim made elsewhere in the repo:

1. **`extended_ci` and `extended_cs` differ in WHERE element 4 lands, not in how many
   elements are attributed** — case-insensitivity does not merely over-detect, it puts
   element 4 on section `1.1` (a part-75 appendix's internal numbering read as a CFR
   section) instead of carrying 52.2320. Both score 5/6; only one of them is right,
   and neither is right about element 4. This is SPEC-FIX-1's sabotage finding in
   miniature: **attribution rate cannot see the difference.**
2. **`completeness` and `attribution_rate` are different numbers** — 0.6667 vs 0.8333
   under `extended_ci` — which is why `CONTEXT.md` §8 keeps the first as the gate.
3. **`v11` scores LOWER on attribution than `extended_ci`** (0.6667 vs 0.8333) and
   **identically on completeness** (0.6667). The v1.1 rules cost attribution and buy
   correctness; the gate metric does not reward them. That is expected and it is
   pre-registered here so it cannot be reported later as a surprise.

## G-D · Count-matched pairing — hand-computed

Instruction counts per `(document, section)`; `D` and `A` carry defect notes.

```
doc D1 :  A=3 (defect)   B=3   C=2   D=3 (defect)
doc D2 :  E=5 (defect)   F=4
```

| positive | own count | eligible siblings (non-defect) | exact matches | chosen negative | pair? |
|---|---:|---|---|---|---|
| `D1/A` | 3 | `B`=3, `C`=2 | `B` | **B** | **yes** |
| `D1/D` | 3 | `B`=3, `C`=2 | `B` | **B** | yes — *but `B` is already used* |
| `D2/E` | 5 | `F`=4 | none | — | **no** |

**Expected: 3 positives, 1 unmatched, and a negative-reuse collision.** A negative may
be paired with at most **one** positive — reusing `B` would put the same section in the
eval set twice and inflate n with a duplicate item. Declared resolution, fixed here
before the count: **positives are processed in sorted `(frdoc, section)` order and each
negative is consumed on first use**; `D1/D` therefore finds no free sibling and is
excluded on the `no-free-count-matched-sibling` rung. Expected pairs = **1**, expected
n = **2**.

## G-E · The nested-`<SECTION>` trap — real bytes

In `CFR-2024-title40-vol5.xml`, **313 `<SECTION>` elements, of which 2 are nested
inside an `<EFFDNOTP>/<REVTXT>`**:

| `SECTNO` | eligible outer copy | nested copy |
|---|---|---|
| `§ 52.2320` | 148,032 chars, has the `EFFDNOTP` | **24,455 chars — the pending amendment text verbatim** |
| `§ 52.2520` | 147,585 chars, has the `EDNOTE` and the `EFFDNOTP` | **3,501 chars — ditto** |

The nested copy is the rule under test, printed in full by the CFR's own
*"For the convenience of the user, the … text is set forth as follows"* convention.

**Expected:** a section lookup for `52.2320` returns **exactly one** eligible section —
the outer one — and the nested copy is never selected, never frozen, and cannot appear
in the output. A lookup that returned 2 candidates, or the wrong one, is a defect.

## G-F · The leakage test itself must be falsifiable

**Expected, and it is the single most important expectation in this chunk:** running
the leakage test over the **unstripped** § 52.2320 and § 52.2520 text **FAILS**, and
names which rule fired. Running it over the **stripped** text **PASSES**.

Hand-computed from the raw bytes, the unstripped text of these two sections contains:

- `"Effective Date Note:"` — present (both, via the `EFFDNOTP` `<HD>`)
- `"set forth as follows"` — present (both, the `EFFDNOTP` convention sentence)
- `"Editorial Note:"` — present in § 52.2520 (its `EDNOTE` `<HD>`), absent in § 52.2320
- an `EFFDNOTP` element — present in both

so at minimum **rule (a) and rule (c) both fire on both sections** before stripping.

**A leakage test that cannot be made to fail is not evidence of a clean corpus; it is
an untested assertion.** If it cannot be made to fail, the pre-registration's branch
applies: BLOCKER, freeze nothing, move on.

---

## G-G · Volume selection — hand-computed, added before `src/cfr_pit.py` was written

**Appended, not edited.** G-A..G-F stand as committed at `c685e80`. This entry is new
work, and it exists because reading the govinfo listings turned up a hazard that the
pre-registration did not anticipate: **CFR annual-edition volumes do not map one-to-one
onto parts.** Title 26's part 1 is split across roughly twenty volumes by *section*
range, and 10 of the 85 pool citations are title 26.

Real `<PARTS>` headers, read off govinfo:

| header string | expected `part_lo` | `part_hi` | expected section range |
|---|---:|---:|---|
| `Parts 53 to 59` | 53 | 59 | none |
| `Parts 1 to 49` | 1 | 49 | none |
| `Part 52` | 52 | 52 | none |
| `Part 80 to End` | 80 | **None** (= End, unbounded) | none |
| `Parts 500 to 599` | 500 | 599 | none |
| `Part 1 (§§ 1.908 to 1.1000)` | 1 | 1 | `1.908` … `1.1000` |
| `Part 63 (§§ 63.600—63.1199)` | 63 | 63 | `63.600` … `63.1199` |
| `Part 1 (§§ 1.1401 to 1.1550)` | 1 | 1 | `1.1401` … `1.1550` |

Note the em-dash separator and the U+2009 thin space after `§§`. A parser that splits
on ASCII `-` alone gets `63.600—63.1199` wrong, and a parser that splits on `-` at all
would break a real hyphenated section number such as `1.199A-0`. **Declared rule: take
every section-shaped token inside the parentheses and use the first and the last.**

**G-G2 — section ordering must be NUMERIC, not lexicographic.** Hand-computed:

| comparison | lexicographic says | **correct answer** |
|---|---|---|
| `1.908` vs `1.1000` | `1.908` > `1.1000` ❌ | `1.908` **<** `1.1000` |
| `60.41a` vs `60.41b` | a < b ✅ | `60.41a` < `60.41b` |
| `1.199A-0` vs `1.199B-1` | ✅ | `1.199A-0` < `1.199B-1` |
| `1.61` vs `1.169` | `1.61` > `1.169` ❌ | `1.61` **<** `1.169` |

A lexicographic comparator would send every title-26 lookup to the wrong volume, and
it would do so *silently* — the section would simply not be found and the item would
drop off the exclusion ladder as "not in the as-of edition". **That is the shape of
every failure this project is built to catch: a wrong answer that presents as a
smaller n rather than as an error.** Hence a declared fallback: if the section is not
found in the volume the range chose, **every other volume covering that part is
searched before the item is excluded**, and the route that found it is recorded.

**G-G3 — a volume's own `<REVISED>` stamp is not always its edition year.**
`CFR-2019-title26-vol21.xml` says *"Revised as of April 1, **2010**"*. GPO carries a
volume forward unchanged when nothing in it was amended. **The edition is the year
folder on govinfo, never the `<REVISED>` line**, and the `<REVISED>` line is recorded
per item so the discrepancy is visible rather than assumed away.

### G-D2 · The negative-selection rule must be NEUTRAL IN SORT ORDER — added at the review

G-D fixed *which* negative is consumed and *that* a negative is consumed once. It did
not fix the property that mattered, and the CH-03 adversarial review found the gap:
**a rule can satisfy every assertion in G-D and still leak the label through section
order.**

Mutation **M7** — flipping the rule from the sorted-FIRST to the sorted-LAST candidate
— **is caught** by the suite. So the suite pinned the declared rule exactly. **No test
asserted the rule was unbiased**, and that is why a green suite shipped an eval set a
six-line script beat at 0.8158.

**A test that pins a rule is not a test that the rule is correct.**

**Expected, and now asserted on the frozen corpus forever:**

| property | expected |
|---|---|
| label-blind sort-order script accuracy | **≤ 0.60** |
| negatives sorting before their positive | not significantly ≠ half at α = 0.05 |

Measured before the fix: **0.8158**, and **32 of 38** (exact two-sided p = 0.000024).
Measured after: **0.5610**, and **21 of 41** (exact two-sided p = 1.0000).

The kept tests are `tests/test_review_ch03_findings.py`. They were RED when written
and are GREEN now, and both states are in the history — hard rule 6's probe that
flips, on the most important defect this project has found in its own work.

### G-D2 ERRATA - the mutation claim inside G-D2 was itself false

G-D2 above says *"Mutation M7 ... **is caught** by the suite. So the suite pinned the
declared rule exactly."* **That is wrong**, and it is corrected here rather than edited
out.

M7 **cannot** be caught: G-D's free candidate list for positive `A` is `["B"]`, a
single element, so `free[0]` and `free[-1]` are the same section and the mutation
changes nothing. Round 1's harness read `returncode != 0` as "caught" without ever
establishing a green baseline, and the build session repeated the result in four
documents without checking it - `CLAUDE.md` hard rule 15, broken on the very evidence
meant to show the gate working.

**The true statement is worse than the false one.** No test pinned the rule at all:
the kept round-1 test asserts on the FROZEN `items.jsonl`, and a source mutation does
not touch a frozen file. Five of six mutations of the fixed rule went uncaught.

**Closed by** `tests/test_review_ch03_round2_findings.py::test_R1_...`, which runs
`build_pairs` over the real corpus so the RULE has a test of its own, and by
`docs/reviews/ch03-probe2/mutate3.py`, a harness that counts a mutation as caught only
when the result **changes from an established baseline**. Against a green baseline of
278 passed: **6 caught, 0 missed**.

G-D2's numeric expectations are also corrected: the pre-fix ordering bias is
**36/50 at exact p = 0.0026** and the shipped rule is **25/50 at p = 1.0000**, both
measured by running the rules rather than reconstructing them from the freeze
(`docs/evidence/ch03-evalset/ordering_bias.py`). The withdrawn figures were
32/38 and p = 0.000024.
