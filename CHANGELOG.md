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
| Baseline | **B0** (one prompt, instruction only) vs **B0-agent** (same model + point-in-time CFR text). The project's headline claim is that an amendatory instruction carries no evidence of its own executability; B0 is that sentence turned into an experiment. | **B0 0.4756 · B0-agent 0.6585 · gap +18.3 pp · McNemar exact p = 0.0059 (b=21 c=6, 27 discordant) · n = 82, 41 pairs, 3 reps, `claude-haiku-4-5-20251001` @ t=0.** B-script **0.6098**, within-pair permutation **p = 0.2355**. `docs/evidence/checkpoint/` | **GREEN.** Phase 2 proceeds. B0 landed on its predicted 0.50; B0-agent came in **9 pp below** its predicted 0.75. **An earlier run of this row read AMBER and is WITHDRAWN** — it was computed on an eval set that the CH-03 adversarial review then failed, and which a label-blind script beat at 0.8158. The withdrawn figures are kept at `docs/evidence/checkpoint/withdrawn/`. The corrected eval set is **harder**, not easier: the same attack now scores 0.5610. |
| Iteration 1 | **CH-05 `cfr_resolve`** — deterministic designation-state and quoted-anchor resolution, designation FIRST. **Observed failure it targets:** B0-agent's missed-defect rate is **0.4737** — it reads the text and still misses nearly half the defects, because reading is not checking. | *(card committed at `cb65539`, before the capability is wired into an arm; the measured result belongs to CH-08)* | **Prediction, fixed now: A1 moves the missed-defect rate below 0.25 and the gap above 20 pp.** If it does not, the card stays and says so. |
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
