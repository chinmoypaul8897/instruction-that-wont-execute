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
