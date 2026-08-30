# SPEC-FIX-2 — the architect's ruling on Q11, plus the unblocked housekeeping

You are a **BUILD session**. You edit the spec, under a ruling the architect has already made and specified exactly. **You decide nothing.** Anything not specified below is a STOP.

**Context:** SPEC-FIX-1 was asked to judge a metric correction and **refused it**, correctly, on a sabotage control it built itself. The architect has accepted that refusal in full. This chunk applies the ruling that follows from it.

**Read `docs/evidence/spec-fix-1/verdict.md` first.** It is the reasoning this ruling rests on, and it was right where the architect was wrong.

---

## 🔴 THE SHAPE OF THIS RULING

The architect proposed a metric change that would have turned a failure into a pass. It was refused. **This ruling therefore does the opposite in three places on purpose:**

- it **keeps the gate failed** and publishes the failure
- it **adopts a correction that costs 8 points**, which the original proposal omitted
- it **adopts only the fix that is justified independently of its effect on the number**

If any instruction below reads as making a failing number pass, **stop and say so.** You have the same authority SPEC-FIX-1 had.

---

## READ FIRST

1. `CLAUDE.md` — every hard rule, **5 and 15–17 especially**
2. `docs/evidence/spec-fix-1/verdict.md` — the refusal and its evidence
3. `QUESTIONS.md` — **Q9, Q10, Q11, Q12, Q13**
4. `CONTEXT.md` §8
5. `PROGRESS.md` (latest)

---

## THE RULING — record it verbatim into `QUESTIONS.md` under Q11

```
Q11 - RULED by ARCHITECT, 2026-08-30.

The refusal is ACCEPTED IN FULL. The proposed metric was not adopted and will
not be re-proposed. SPEC-FIX-1's sabotage control is decisive: an attributor
that places 6,395 of 6,663 attributed elements on a DIFFERENT section scores
the identical 0.7613, so attributed/total cannot distinguish a correct
attributor from a 96%-wrong one. The architect's claim that it "answers the
question the gate exists to answer" was factually false, and was disproved by
running code rather than argued down.

Three further findings are accepted without qualification:
  (a) the proposed pass required BOTH post-hoc edits - 2a alone 0.7613, 2c
      alone 0.6643, together 0.9865. That is the shape of a rescue.
  (b) golden G1, chosen by CH-02 BECAUSE it demonstrates mis-attribution,
      passes the proposed gate at 0.9286.
  (c) the proposal adopted the +22.5pt correction and omitted the -8.0pt one
      that CH-02 had already called an improvement. Selecting the fix that
      helps and omitting the fix that hurts is the defect this project exists
      to detect, and the architect committed it.

On "would this have been raised at 0.92" - no. The diagnosis pre-existed the
number (goldens.md P6, committed 25 minutes before the attributor). The metric
change did not. Nothing was learned between the spec and the correction except
the number.

WHAT SURVIVES: only 46 of 2,913 unparsed elements (1.6%) are our defect. Parse
shape is a property of Federal Register drafting, not of our attributor, and
does not belong in an attributor's gate. That half of the diagnosis stands and
is recorded - but it does NOT license a metric change now, because no metric
that discriminates was available at a passing threshold. The gate stays as it
is and stays FAILED.

CONSEQUENCE: CH-02 remains in the "< 0.80 - documented failure" branch. The
failure is published in the README, not absorbed. CH-03 proceeds on the
per-document restriction that was pre-registered BEFORE any of this - see
plan.md CH-02's fallback - which is a rescue by nobody's definition because it
was written before the number existed.
```

---

## THE FOUR CHANGES

### 1. `CONTEXT.md` §8 — record the failure, do not fix it

Add a block stating, in substance:

> **The attributor gate FAILED and the failure is published.** Global completeness measured **0.5080** under this file's own detector and **0.6643** under an extended one; the gate required 0.90. Attribution alone measured 0.7613 / 0.9865, but **that figure was tested and rejected as a gate**: a control attributor placing 6,395 of 6,663 elements on a *different* section scores identically, so the measure is blind to the silent-wrong failure mode. It does catch the silent-drop mode that broke a predecessor pilot (a lead-ins-only attributor scores 0.2503). Evidence: `docs/evidence/spec-fix-1/`.
>
> **The definition was NOT rewritten after it failed.** A correction was proposed by the architect, judged by an independent session, and refused. The refusal is `docs/evidence/spec-fix-1/verdict.md`.
>
> **Known and deliberately unfixed** (Q10, counted, recovery < 0.31 pp): the `46 CFR 356.3` citation form, and table-driven amendments whose sections live inside a `GPOTABLE`. Found *after* the measurement; the pre-registered tokenisation rules forbid revising a rule once the number is in view.

**Do not add a new metric. Do not change the threshold. Do not alter the definition.**

### 2. `CONTEXT.md` §8 step 3 — fix the section-citation detector (Q9)

Amend the algorithm so a section is recognised in **either** the sign form (`§ 1.907`) or the word form (`Section 1.907 is amended by`).

**This is adopted because it is justified independently of its effect on any number:** under the sign-only detector **10 documents attribute NOTHING** — 1,910 elements, including two of the five largest rules in the corpus (`2014-08744` at 838 elements, `2021-22144` at 649), because FAR rules write *"Section 52.204-8 is amended"* without the sign. Mis-attribution, not under-detection: CH-02 measured 20 of 28 elements on golden G1 pinned to a section they do not amend.

**State the case-sensitivity explicitly (Q12):** the word form is matched **case-sensitively** — `Section`, not `section`. CH-02's shipped detector was case-insensitive and read appendix-internal numbering (`"section 1.1"` of Appendix A) as a CFR section in 683 of 684 lowercase-only elements, 44 of them carrying `part_mismatch`. Record that the 0.9865 figure was the case-**in**sensitive one and is therefore an over-count.

### 3. `CONTEXT.md` §8 — adopt the part-boundary reset. **This costs 8 points.**

Add to the algorithm: **`current_section` resets to null at a `REGTEXT` part boundary.** An instruction cannot inherit a section from a different CFR part.

**Adopted precisely because it makes the number worse.** CH-02 identified 699 cross-part attributions and called the reset *"a one-line change and would be an improvement"*; the architect's proposal never mentioned it. Symmetry is the point: **if the fix that helps is adopted, the fix that hurts is adopted.**

**Note the correction from Q12:** of those 699, **126 name their own section correctly** and the `REGTEXT` part tag is what disagrees — an unlogged extraction defect, not an attribution error. Record that, so the 699 is not quoted as if all of it were attributor error.

### 4. Housekeeping — Q13, unblocked and independent of all the above

- Commit `CONTEXT.md`'s **uncommitted CH-01 measured-pool edit** in its own commit, its message saying it is an architect edit from CH-01 that was never committed.
- `git add` **`prompts/CH-02.md`**, **`prompts/SPEC-FIX-1.md`** and **`prompts/SPEC-FIX-2.md`**. Every other chunk prompt is tracked, and prompts **are** deliverable 1's *"instructions that shape each agent."*
- Bump `CONTEXT.md` to **v1.1**, with a §13 change-log row covering changes 1–3 and naming the refusal.

---

## WHAT YOU DO NOT DO

- **Do not re-run the attributor.** No number changes in this chunk. Changes 2 and 3 alter the spec for CH-03 onward; re-measuring is CH-03's job.
- **Do not touch `data/`, `src/`, `tests/`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `GOOD.md`.**
- **Do not fix Q10's two spellings.** They stay recorded and unfixed.

---

## SCOPE FENCE — hard

**Change ONLY:** `CONTEXT.md`, `QUESTIONS.md`, `docs/evidence/spec-fix-2/`, `STATUS.md`, `PROGRESS.md`, `AI-USE.md`, and `git add` the three prompt files named in §4.

Anything else → **STOP**, write `QUESTIONS.md`.

---

## VERIFY

- After each `CONTEXT.md` edit, assert the new text is present **and** the old text is gone. A batch of edits silently failed earlier in this project because the replace targets did not match and nothing errored (`CLAUDE.md` rule 16).
- `git ls-files prompts/ | wc -l` must show all chunk prompts tracked.
- `git status --porcelain CONTEXT.md` must be empty at the end.

---

## GIT

Atomic commits, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`

Commit the Q11 ruling **first**, before the spec edits, so the order is provable from git.
End-of-session duty 6: `python tools/export_session.py SPEC-FIX-2`, commit the transcript.

---

## FINAL OUTPUT

ONE plain-text block, no markdown:

```
SPEC-FIX-2 REPORT
RULING RECORDED : Q11 verbatim? y/n
CHANGES         : 1 failure recorded · 2 regex + case-sensitivity · 3 part reset
                  · 4 housekeeping - each applied? verified how?
DID ANY CHANGE MAKE A FAILING NUMBER PASS? : must be NO - say so explicitly
HOUSEKEEPING    : CONTEXT.md committed clean? prompts tracked? v1.1 + changelog?
VERIFICATION    : new text present AND old text gone, per edit
                  git status --porcelain CONTEXT.md empty?
FILES           : ...
STATUS LINE     : ...
PROGRESS LINE   : ...
PUSHED SHA      : ...
QUESTIONS       : ...
TOKENS + COST   : in / out / wall-clock / imputed USD
```

---

## ECONOMY — read this, it is part of the chunk

**This is a text-editing chunk. It should be the cheapest of the project.**

**Do not convene a subagent panel.** SPEC-FIX-1 spent 55% of its budget on a ten-agent panel that argued 4–1 *against* the verdict it correctly reached; the entire result came from one dissenter's control script. Its own conclusion: *"a cheaper panel would have bought it too."*

Target: **under 5M input tokens.** If you find yourself spawning agents to decide something, the ruling above has already decided it — apply it or STOP.

---

## HARD SAFETY RIDER

- No destructive commands, no force-push, no tag moves.
- Never read, print, echo or commit `.env` or any credential.
- `data/`, `src/`, `tests/` are **read-only** in this chunk.
- If anything appears to require work outside this fence: **STOP and report.**
