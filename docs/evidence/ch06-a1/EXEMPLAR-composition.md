# The exemplar — what "the capabilities **compose**" looks like in one artifact

**Item `05-8447|75.6` · 40 CFR 75.6 · FR document 05-8447, published 2005-05-18 · gold
label `WILL_FAIL`.**
Source: `docs/evidence/ch06-a1/A1-rep1-artifacts.jsonl`, arm `A1`, rep 1. Not
cherry-picked for the verdict — it is `CONTEXT.md` §9's own hard case #2, *"adding an
entry that already exists — the pure designation-state check"*, and it is the first
routed item in the file.

---

## The three arms on the same instruction, side by side

| | What it saw | What it ruled |
|---|---|---|
| **B0** | the instruction only | wrong — it has no way to check anything |
| **A1-iter1** *(tool, no procedure)* | `designation_exists: false` | `target-does-not-exist` on instruction 3, and instruction 4 waved through |
| **A1** *(tool + procedure)* | the same `false`, **plus `siblings`** | **instruction 3 executes; instruction 4 fails as `target-already-exists`** |

## What A1 actually emitted, verbatim

Instruction 3 — `Redesignate paragraphs (a)(38) through (a)(41) as (a)(39) through (a)(42);`

```
RESOLVER : designation_exists = false     found = false
MODEL    : executes = true    failure_class = null
why      : "cfr_resolve reported designation_exists=false, but (38) is declared
            under (a) in the section text; the tool cannot see nested designations.
            The siblings list confirms (38), (39), (40), (41) all exist."
```

Instruction 4 — `Add new paragraphs (a)(38), (a)(43), and (a)(44); and`

```
RESOLVER : designation_exists = false     found = false
MODEL    : executes = false   failure_class = "target-already-exists"
why      : "Instruction attempts to add (a)(38), but (38) is already declared under
            (a) in the section text. The siblings list confirms (38) exists. Cannot
            add a paragraph that already exists."
```

Derived by the harness, not by the model:

```
verdict              WILL_FAIL          <- gold: WILL_FAIL
failing_designation  (a)(38)
failure_class        target-already-exists
needs_human_review   true
review_reason        C3 designation (a)(38) is touched by instructions [3, 4] -
                     instruction 3 changes what instruction 4 will find, and the
                     ordered-state ledger is NOT BUILT (ruling R-01, counted removal #3)
```

---

## Why this single item carries four of the project's claims at once

**1. The capabilities compose — this is `CONTEXT.md` §3's central claim, visible.**
The tool alone gets this wrong: `A1-iter1` believed `designation_exists: false` and ruled
`target-does-not-exist` on the wrong instruction. The procedure alone could not have known
what is in the section at all. **Together they are right**, and the mechanism is legible:
the tool supplied `siblings`, the procedure told the agent to read it.

**2. The agent overrode its own deterministic tool, correctly, and said so in the note.**
`cfr_resolve` is wrong here — this is `QUESTIONS.md` **Q21**, the nested-designation
ceiling, which misfires on 60 of 128 designations and always in the same direction. Step
2.5 of `agents/A1-SKILL.md` exists because Iteration 1 measured that failure. The emitted
`why` **names the tool's limitation in the published note**: *"the tool cannot see nested
designations."* An agent that documents the defect in its own instrument, in the artifact
a human will read, is doing the job this project says agents should do.

**3. It is right for the RIGHT REASON, and the artifact proves it.**
A verdict alone would be one bit — and `WILL_FAIL` was reachable here by guessing, since
a coin lands on it half the time. The trace shows the agent named **which** instruction
fails (4, not 3), **why** (`(a)(38)` already exists), and **which NARA class** applies.
`CONTEXT.md` §5: *"every capability becomes directly readable in the artifact rather than
inferable from an average."* This is what that sentence buys.

**4. The removed capability is visible as an escalation rather than absent.**
`(a)(38)` is touched twice — redesignated by instruction 3, added by instruction 4 — so
what instruction 4 finds depends on whether instruction 3 executed first. **Modelling that
is capability 3, the ordered-state ledger, NOT BUILT under ruling R-01.** A1 does not
pretend to model execution order. It routes the item to a human, **names the ruling that
removed the capability in its own escalation text**, and ships both readings with the full
paragraph trace — `CONTEXT.md` §9's *"unresolved cases route to a named human checkpoint
with both readings and the paragraph trace"*, satisfied concretely rather than in prose.

---

## What this exemplar is NOT

**It is not the result.** A1 scores **0.7195** on rep 1 and the pre-registered success
criterion is **not met** on any of its four clauses. One item that goes right does not
move that, and it is shown here to explain the mechanism, never to stand in for the
aggregate. The 82-item numbers, the guards, the ablations and the misses are in
`a1-result.txt` and `docs/evidence/error-taxonomy.csv`, and the errors are listed there in
the same detail as this success.

**It is also not proof the override generalises.** The same instruction to distrust
`designation_exists` could make the agent override the tool when the tool is *right*. That
is a live risk of Step 2.5, it is exactly what the false-defect and missed-defect guards
are for, and both are reported per arm.
