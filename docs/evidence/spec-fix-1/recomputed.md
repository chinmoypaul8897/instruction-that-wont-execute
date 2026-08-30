# SPEC-FIX-1 §3 — CH-02's numbers re-reported under the proposed split metric

**Read this with [`verdict.md`](verdict.md).** The verdict is **GOALPOST-MOVING**, so the
proposed definition was **not adopted** and `CONTEXT.md` is unchanged. These figures are
computed *under* the proposed definition in order to **judge** it — not because it is in
force. The definition in force remains `CONTEXT.md` §8's combined one, taken on §8's own
`spec_literal` detector.

**The attributor was not re-run** (§3 forbids it). Everything below is recomputed from the
frozen `data/amdpars/completeness.json` and `data/amdpars/amdpars.jsonl` by
`spec_fix_1_recompute.py`, whose stdout ships beside it as `recomputed.txt`.

---

## The headline §3 asks for, stated plainly

> ### Under `CONTEXT.md` §8's own detector — the one CH-02 gated on, and the one still in force because §2c was not applied — `attribution_completeness` is **0.7613**. It **STILL MISSES the 0.90 gate.**
>
> §3 says: *"If `attribution_completeness` still misses 0.90, say so plainly — the correction
> is not permitted to be a rescue, and a second failure is a real finding."* **It does, and
> this is that finding.**

The 0.9865 the prompt's fact table quotes is not the figure under `CONTEXT.md` §8 as it
stands. It is the figure under the `extended` detector — the one **§2c would create**. The
split metric does not rescue CH-02 on its own. It clears 0.90 **only** when the metric
change and the regex change are applied together.

---

## Global — every figure, both detectors, nothing quoted alone

| detector | metric | value | vs 0.90 |
|---|---|---:|---|
| `spec_literal` (§8's own) | **`attribution_completeness`** (proposed gate) | **0.7613** | **FAIL** |
| `spec_literal` | `parse_completeness` (reported, never gated) | 0.6672 | — |
| `spec_literal` | `completeness` (§8 in force) | 0.5080 | **FAIL** |
| `extended` (needs §2c) | **`attribution_completeness`** (proposed gate) | **0.9865** | PASS |
| `extended` | `parse_completeness` (reported, never gated) | 0.6672 | — |
| `extended` | `completeness` (§8 in force) | 0.6643 | **FAIL** |

**The original definition's figure is preserved and labelled**, as §2a required, so the
metric that failed and the metric proposed to replace it are readable side by side.

---

## Which pre-registered CH-02 branch does each figure land in?

`prompts/CH-02.md` §4's branch table is pre-registered and **is not changed by this chunk**.
Applied to each candidate figure:

| detector | figure | value | branch |
|---|---|---:|---|
| `spec_literal` | `completeness` (in force) | 0.5080 | **`< 0.80` — documented failure. Do not tune it to pass.** |
| `spec_literal` | `attribution_completeness` (proposed) | 0.7613 | **`< 0.80` — documented failure. Do not tune it to pass.** |
| `extended` | `completeness` (in force) | 0.6643 | **`< 0.80` — documented failure.** |
| `extended` | `attribution_completeness` (proposed) | 0.9865 | `≥ 0.90` — *Proceed. Report the figure.* |

**Three of the four land in the documented-failure branch.** The single cell that reaches
"proceed" is the one requiring both post-hoc spec edits at once.

**CH-02's actual outcome is unchanged by this chunk.** It took the `< 0.80` branch, and it
remains there: no spec edit was made, so nothing about its gate result moves.

---

## Per document, against the 0.90 gate

`CONTEXT.md` §8 requires the metric be reported *"globally **and** per FR document,"* and
says the per-document figure is what CH-02's fallback restricts on.

| | `spec_literal` | `extended` |
|---|---:|---:|
| documents | 70 | 70 |
| **≥ 0.90** | **47 (0.6714)** | **57 (0.8143)** |
| < 0.90 | 23 | 13 |
| **= 0.0000** | **10** | **1** |
| unweighted mean | 0.7942 | 0.9426 |
| min / max | 0.0000 / 1.0000 | 0.0000 / 1.0000 |
| **per-document floor at 0.90** | **0.6714 — FAIL** | **0.8143 — FAIL** |

**Under both detectors the per-document floor fails.** A global 0.9865 that becomes 0.8143
when every document is weighted equally is a figure carried by a handful of very large rules.

### The ten `spec_literal` zero-attribution documents — a finding in their own right

Under `CONTEXT.md` §8's own detector, **ten documents have not one attributed element**, and
two of them are among the five largest in the corpus:

| frdoc | elements | share of corpus | `spec_literal` | `extended` |
|---|---:|---:|---:|---:|
| `2014-08744` | 838 | 9.6% | **0.0000** | 0.9988 |
| `2021-22144` | 649 | 7.4% | **0.0000** | 0.9985 |
| `2024-29226` | 136 | 1.6% | **0.0000** | 0.9926 |
| `2020-22974` | 100 | 1.1% | **0.0000** | 0.9900 |
| `2021-09097` | 52 | 0.6% | **0.0000** | 0.9808 |
| `2026-11140` | 50 | 0.6% | **0.0000** | 0.9800 |
| `2015-15249` | 44 | 0.5% | **0.0000** | 0.9773 |
| `2026-11267` | 27 | 0.3% | **0.0000** | **0.0000** |
| `2025-00723` | 9 | 0.1% | **0.0000** | 0.8889 |
| `2020-16986` | 5 | 0.1% | **0.0000** | 0.8000 |

These are Federal Acquisition Regulation and similar rules that write *"Section 52.204-8 is
amended…"* without the sign. **This is the clearest possible corroboration of Q9's substance
and it is why §2c is right on the merits**, independent of the metric dispute: 1,910 elements
in these ten documents are attributed to nothing at all under the detector the spec prints.

`2026-11267` is zero under **both** detectors — the Q10 `46 CFR 356.3` document, already
recorded, counted, and deliberately unfixed.

### Every `extended` document below the gate

| frdoc | attributed | elements | attribution |
|---|---:|---:|---:|
| `2026-11267` | 0 | 27 | 0.0000 |
| `2019-18241` | 4 | 5 | 0.8000 |
| `2020-16986` | 4 | 5 | 0.8000 |
| `2025-13289` | 4 | 5 | 0.8000 |
| `2019-07652` | 5 | 6 | 0.8333 |
| `2022-05512` | 5 | 6 | 0.8333 |
| `2024-18445` | 75 | 89 | 0.8427 |
| `2021-27643` | 6 | 7 | 0.8571 |
| `2025-17122` | 6 | 7 | 0.8571 |
| `2024-23195` | 7 | 8 | 0.8750 |
| `2017-00727` | 8 | 9 | 0.8889 |
| `2025-00723` | 8 | 9 | 0.8889 |
| `2024-14542` | 17 | 19 | 0.8947 |

Eleven of the thirteen have fewer than 20 elements, so a single miss costs them the gate;
`2024-18445` (the Q10 `GPOTABLE` document) and `2026-11267` are the two substantive failures.

---

## The concentration caveat, restated because it governs how the global figure reads

| frdoc | elements | share | `attribution_completeness` | `parse_completeness` |
|---|---:|---:|---:|---:|
| `2015-01571` | 2,177 | **24.9%** | 0.9995 | 0.7028 |
| `2014-08744` | 838 | 9.6% | 0.9988 | 0.6659 |
| `2021-22144` | 649 | 7.4% | 0.9985 | 0.6841 |
| `2024-17239` | 379 | 4.3% | 0.9974 | 0.4591 |
| `2024-07002` | 338 | 3.9% | 0.9970 | 0.7426 |

One document is a quarter of every element measured; the top five are **50.1%**. All five
score above 0.997 on the proposed metric. **The global `attribution_completeness` is, to a
first approximation, a statement about five rules.** That is the mechanism by which
0.9865 global coexists with 0.8143 per-document.

---

## Summary against §3's three asks

| ask | answer |
|---|---|
| `attribution_completeness` global vs the 0.90 gate | **0.7613 FAIL** under §8's own detector; 0.9865 PASS only under the detector §2c would create |
| `attribution_completeness` per document | **47/70 (`spec_literal`) · 57/70 (`extended`)** — a per-document floor at 0.90 **fails under both** |
| `parse_completeness` beside it | **0.6672**, identical under both detectors — it is a property of the corpus, not of the detector, which is the one point in the architect's case that every measurement confirms |
| which pre-registered CH-02 branch | **`< 0.80` — documented failure — under three of four readings**, and unchanged by this chunk, because no spec edit was made |
| **does it still miss 0.90?** | **YES, under the definition in force. Stated plainly, as §3 required.** |
