# `B0-agent` — agent instructions

**PDF baseline type 2: a general agent with basic tools.**

`CONTEXT.md` §4 gives this arm *"same model **with** point-in-time section text and
search tools; no skill, no memory"*. Predicted **≈ 0.75**, committed to `GOOD.md`
before the arm ran.

**`B0-agent` is a BASELINE, not the solution**, and the results table says so one row
above the agent. `CONTEXT.md` §3 is explicit that the retrieval gain belongs here and
must be reported as a baseline effect: *"This honesty is not optional: it is already
conceded in the spec's own §7.3 and a judge will find it."*

## The one difference from `B0`

**This arm is given the CFR section text as it stood before the rule was published.**
Everything else — model, temperature, prompt shape, output contract, scoring, item
order — is identical. That is what makes the gap attributable to the text rather than
to a prompt change.

The text is the **stripped** point-in-time section: `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>`
and `<EAR>` removed and counted before freezing, and the frozen text asserted to
contain none of `could not be incorporated`, `Editorial Note`, `Effective Date Note`,
`set forth as follows`, its own FR citation, or — measured — **any FR citation at
all**. Without those strips this arm would be reading the answer: **8 of the 76 items
would have contained it in their unstripped text.**

The edition is the latest annual edition revised **strictly before** the rule's
publication date. Strictly-before is the point: an edition revised *on* that date
could already carry the amendment under test.

## System prompt

```
You are an editor at the Office of the Federal Register (OFR).

Your job is to decide whether an amendatory instruction in a final rule can be
EXECUTED against the Code of Federal Regulations - that is, whether OFR will be able
to incorporate it into the CFR text.

An instruction fails to execute when, for example, the paragraph it targets does not
exist, the paragraph it adds already exists, quoted text it says to find is not
present in the section, set-out text is incomplete, or a citation or designation is
incorrect. When an instruction cannot be executed, OFR does not change the CFR and
NARA publishes a permanent editorial note recording that the amendment could not be
incorporated.

You will be shown the amendatory instructions for ONE CFR section from ONE final
rule, AND the text of that section as it stood immediately before the rule was
published. Check each instruction against the section text.

Answer with exactly one word, and nothing else:

WILL_FAIL      - at least one instruction cannot be executed as written
WILL_EXECUTE   - every instruction can be executed as written
```

## User prompt template

```
CFR title {cfr_title}, section {section}.
Federal Register document {frdoc}, published {publication_date}.

The text of {cfr_title} CFR {section} as of the {as_of_edition} annual edition
(revised {as_of_revision_date}), which is the last edition published before this
rule:

--- BEGIN SECTION TEXT ---
{section_text}
--- END SECTION TEXT ---

Amendatory instructions ({instruction_count}), in document order:

{numbered instruction texts, one per line}

Will these instructions execute against the section text above? Answer with exactly
one word: WILL_FAIL or WILL_EXECUTE.
```

## Configuration — fixed in `GOOD.md` before the arm ran

| | |
|---|---|
| Model | `claude-haiku-4-5-20251001` — the **same model as `B0`** (fairness, `CONTEXT.md` §4) |
| Temperature | `0` |
| `max_tokens` | 16 |
| Reps | 3 |
| Delivery | standard |
| Item order | sorted by `item_id`, identical to `B0` |
| **Section text** | **full, never truncated** |

**No truncation, and the reason is measured rather than assumed.** The 76 items total
847,851 characters ≈ 212 K tokens, so three full reps cost ≈ USD 0.65 against an
USD 18.00 ceiling. There was no budget reason to truncate, so nothing was truncated
and no item carries a truncation flag. Had a cap been needed it would have been
declared in `GOOD.md` with the count of items it touched — because a silent truncation
would make the arm's failures unattributable.

## What this arm is still NOT given

- **No `SKILL.md`** — no OFR execution procedure, no instruction to parse each AMDPAR
  into `(operation, anchor, designation)` and resolve them in order.
- **No `cfr_resolve` tool** — it cannot check an anchor or a designation
  deterministically; it must read.
- **No memory / ordered-state ledger** — it does not carry designation state across
  instructions. (That capability is `CONTEXT.md` §6's counted removal #3.)
- No examples, no retries on content, no chain-of-thought request.

Those three absences are exactly what `A1` adds, which is why this arm is the
comparison A1's improvement is measured against.

## Scoring

`src/score.py`, identical to `B0`. An unparseable or absent verdict is a **failure**,
never a skip.
