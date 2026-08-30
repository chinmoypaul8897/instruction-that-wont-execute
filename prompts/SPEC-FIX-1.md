# SPEC-FIX-1 — correct the completeness definition, the section regex, and commit the dirty tree

You are a **BUILD session** with an unusual scope: **you edit the spec.** `CONTEXT.md` is normally architect-owned and read-only to build sessions. For this chunk only, the architect has decided the changes and specified them exactly; you execute them. **You decide nothing** — anything not specified below is a STOP.

---

## 🔴 THE THING THAT MATTERS MOST — read this before anything else

**You are being asked to change a measurement definition AFTER seeing that it failed.** That is the exact shape of the thing this project exists to catch, and `CLAUDE.md` hard rule 5 forbids it:

> **NEVER WEAKEN A TEST OR A THRESHOLD.** No loosening an assertion to get green. No moving a `GOOD.md` number after seeing a result.

**So your FIRST task is to decide whether this correction is legitimate — and you are authorised to refuse it.**

Do that in §1 below, in writing, before you touch a file. If you conclude it is goalpost-moving, **write that conclusion, make no edit, and report.** The architect will accept that verdict. A session that refuses this correction has done its job correctly.

---

## READ FIRST

1. `CLAUDE.md` — every hard rule, **5 and 15–17 especially**
2. `CONTEXT.md` §8 — the AMDPAR attribution algorithm and the completeness definition
3. `QUESTIONS.md` — **Q9 and Q10**, raised by CH-02
4. `docs/evidence/ch02-attributor/completeness.md` and `data/amdpars/completeness.json`
5. `docs/evidence/ch02-attributor/goldens.md` §2 — the pre-registered tokenisation rules P1–P7
6. `PROGRESS.md` (latest)

---

## 1. FIRST TASK — judge the correction. Write the verdict before editing anything.

**The measured facts, verify them yourself from `data/amdpars/completeness.json`:**

| | |
|---|---|
| attribution rate | **0.9865** — 8,634 of 8,752 elements attributed to a section |
| unattributable | **118** |
| parse rate | **0.6672** |
| completeness (the gate metric) | **0.6643** — gate required 0.90 |
| elements with operation `none` | **1,074** |

**The architect's claim:** the completeness definition in `CONTEXT.md` §8 measures the wrong thing. It was written to answer *"did carry-forward put each instruction on the right section?"* — the failure mode that broke a predecessor pilot at 0.46 — but as written it also requires every element to parse into an `(operation, anchor OR designation)` triple. Three classes of legitimate amendatory instruction cannot:

- **authority citations**, which carry no operation at all
- **lead-ins** (`"Amend § 236.2 by:"`) whose specifics live in their lettered children
- **whole-section revisions** (`"Section 90.601 is revised to read as follows"`), which have no paragraph path and no quoted anchor

**Judge it. Answer each in writing:**

1. Are those three classes real and material? **Count them in the data** — do not take the architect's word.
2. Does the current definition conflate *attribution* (the failure mode the gate exists to catch) with *parse shape* (a property of the instruction, not of the attributor)?
3. **Would this correction have been made if the number had come in at 0.92?** Answer honestly. If no, say so — that is the strongest argument against it.
4. Is there a version of this correction that is *strictly harder* to pass rather than easier?
5. **VERDICT: LEGITIMATE SPEC CORRECTION or GOALPOST-MOVING.**

Write this to `docs/evidence/spec-fix-1/verdict.md` and commit it **before** any spec edit. If the verdict is GOALPOST-MOVING, stop there and report.

---

## 2. If and only if the verdict is LEGITIMATE — apply these four changes

### 2a. Split the metric in two. Do not replace one number with another.

In `CONTEXT.md` §8, replace the single completeness definition with **two named metrics, both reported always**:

- **`attribution_completeness`** = (elements attributed to a section) ÷ (total elements). **This is the gate metric.** It answers the question the gate exists to answer. **Threshold: ≥ 0.90.**
- **`parse_completeness`** = (elements parsed into a complete `(operation, anchor OR designation)` triple) ÷ (total elements). **Reported, never gated.** It is a property of Federal Register drafting, not of our attributor.

**Both numbers ship in every report. The original definition's figure is preserved and labelled**, so a reader can see the metric that failed and the metric that replaced it, side by side.

### 2b. Record the correction against hard rule 5, in the open

Add to `CONTEXT.md` §8, verbatim in substance:

> **This definition was corrected after it failed.** The original gate metric conflated attribution with parse shape and scored 0.6643 against a 0.90 threshold. Attribution — the failure mode the gate exists to catch, and the one that broke a predecessor pilot at 0.46 — measured **0.9865**. Both figures are published. The correction is disclosed here rather than absorbed, because changing a measurement after seeing it fail is precisely the behaviour this project was built to detect, and an undisclosed correction would be indistinguishable from the defect. The session that judged this correction legitimate is `docs/evidence/spec-fix-1/verdict.md`; it was authorised to refuse and did not.

### 2c. Fix the section-citation regex — Q9

`CONTEXT.md` §8's detector matches only the sign form (`§ 1.907`). It misses the word form (`Section 1.907 is amended by`). **Under carry-forward this MIS-ATTRIBUTES rather than under-detects** — CH-02 measured 20 of 28 elements on golden G1 pinned to a section they do not amend.

Amend the algorithm's step 3 so a section is recognised in **either** form. State in the file that this is a correction to a defect that caused mis-attribution, with the G1 count as evidence.

**Q10's two further spellings (`46 CFR 356.3`, and table-driven amendments inside `GPOTABLE`) are NOT fixed here.** CH-02 found them after measuring and correctly left them alone; recovery is under 0.31 percentage points. **Record them in `CONTEXT.md` as known, counted, and deliberately unfixed**, with the reason.

### 2d. Housekeeping

- `CONTEXT.md` carries an **uncommitted** working-tree modification (the CH-01 measured-pool correction). Commit it as part of this chunk, in its own commit, with a message saying it is an architect edit from CH-01 that was never committed.
- **`prompts/CH-02.md` is untracked.** Commit it — every other chunk prompt is tracked, and the prompts *are* deliverable 1's "instructions that shape each agent."
- Bump `CONTEXT.md` to **v1.1** and add a row to its §13 change log covering all of the above.

---

## 3. Then re-report the CH-02 numbers under the corrected definition

Do **not** re-run the attributor. Recompute from the frozen `data/amdpars/completeness.json`:

- `attribution_completeness` global and per document, against the 0.90 gate
- `parse_completeness` beside it
- **Which pre-registered CH-02 branch the corrected metric lands in**

Write to `docs/evidence/spec-fix-1/recomputed.md`. **If `attribution_completeness` still misses 0.90, say so plainly** — the correction is not permitted to be a rescue, and a second failure is a real finding.

---

## SCOPE FENCE — hard

**Change ONLY:** `CONTEXT.md`, `QUESTIONS.md`, `docs/evidence/spec-fix-1/`, `STATUS.md`, `PROGRESS.md`, `AI-USE.md`, and `git add` the two files named in §2d.

**Do NOT:** re-run the attributor · modify `src/` or `tests/` · touch `data/` · edit `plan.md`, `PROCESS.md`, `CLAUDE.md` or `PROVENANCE.md` · touch `GOOD.md`.

Anything not specified above → **STOP** and write `QUESTIONS.md`.

---

## GIT

Atomic commits, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`

Commit the verdict **before** the spec edits, so the order is provable from git.
End-of-session duty 6: `python tools/export_session.py SPEC-FIX-1`, commit the transcript.

---

## FINAL OUTPUT

ONE plain-text block, no markdown:

```
SPEC-FIX-1 REPORT
VERDICT         : LEGITIMATE / GOALPOST-MOVING  + the four answers behind it
                  (including: would this have been raised at 0.92?)
COUNTS          : authority citations / lead-ins / whole-section revisions,
                  counted from the data, not taken from the architect
CHANGES         : what was edited, or NONE if refused
RECOMPUTED      : attribution_completeness vs the 0.90 gate · parse_completeness
                  which CH-02 branch it now lands in
STILL FAILING?  : yes/no - and if yes, say it plainly
FILES           : ...
STATUS LINE     : ...
PROGRESS LINE   : ...
PUSHED SHA      : ...
QUESTIONS       : ...
TOKENS + COST   : in / out / wall-clock / imputed USD
```

---

## HARD SAFETY RIDER

- No destructive commands, no force-push, no tag moves.
- Never read, print, echo or commit `.env` or any credential.
- `data/` is **read-only** in this chunk — you recompute from it, you do not write to it.
- If anything appears to require work outside this fence: **STOP and report.**
