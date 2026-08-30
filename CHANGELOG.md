# CHANGELOG.md — the Improvement Changelog

**This is deliverable 1.** It is written **per iteration, as it happens**, and is
never reconstructed at the end. A changelog assembled after the results are known is
a narrative; one written before each build is evidence.

The rubric's largest row asks **"which design choices helped the agent solve the
problem?"** The only defensible answer is one written *before* the choice was made —
so each row below is backed by an iteration card committed **before** its build, with
its prediction already fixed (`PROCESS.md` §5).

**A capability that does not move its number is REMOVED and its card stays.** A card
that predicted +8 pp and measured +1 pp is better evidence of method than one that
quietly succeeded.

---

## The four-column table (PDF §4)

| STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING |
|---|---|---|---|
| Baseline | *(pending — CHECKPOINT)* | | |
| Iteration 1 | *(pending — CH-05 `cfr_resolve`)* | | |
| Iteration 2 | *(pending — CH-06 `SKILL.md` + note-emission contract)* | | |
| Iteration 3 | *(pending — CH-07 ordered-state ledger, **pre-declared as not built**)* | | |
| Final | *(pending — CH-08)* | | |

Empty by design at CH-00. CH-00 builds no capability and moves no metric; it builds
the instrument that every later row is measured with. Writing a row for it would be
the exact padding this table exists to expose.

---

## Iteration cards

Each card is committed to this file **before** the build it describes, in this shape:

```
## Iteration N — <capability>
Observed failure : <the specific failure in the previous arm, with its number>
Hypothesis       : <why this capability should fix it>
Prediction       : <the number it should move, and by how much>   <- BEFORE the run
Evidence path    : docs/evidence/iter-N/
```

and completed after it:

```
Result           : <measured>
Decision         : kept / revised / REMOVED
Learning         : <what it taught us about the problem>
```

*(No cards yet. The first is written at the CHECKPOINT, for the Baseline row.)*

---

## Removed experiments — three, all counted

The brief requires removed experiments and most entrants will have none. Ours are
declared here as they are decided, not harvested at the end:

1. **Current-CFR-text leakage probe** — CH-09.
2. **Intra-rule collision detector** — CH-09; class size measured five ways at ~1.3%.
3. **Ordered-state ledger** — CH-07, **declared removed in advance** by ruling R-01,
   before any code existed. Its justification (order-sensitivity fires on 38–42% of
   items, two independent counts, not label-correlated) is published as the reason it
   was *worth* building, alongside the reason it was not built.
