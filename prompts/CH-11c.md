# CH-11c — five factual corrections in shipping files

You are a **BUILD session**. **TIME BOX 45 min.**

**No arm is re-run. No result changes. No model calls.** API spend must read **USD 11.6323** when you finish, unchanged.

These are corrections to **statements about the work**, not to the work. Every one is a claim a judge could check and find false.

---

## READ FIRST

1. `CLAUDE.md` — hard rules **14, 15, 16** especially
2. `QUESTIONS.md` — **Q31, Q32, Q33, Q34, Q35**
3. `PROVENANCE.md`, `README.md`, `GOOD.md`

---

## 1 · Q35 — `PROVENANCE.md` names the wrong model. **Architect's error.**

`PROVENANCE.md` line ~92 reads:

```
| Anthropic API (`claude-sonnet-5`) | commercial, per terms | every evaluation arm |
```

**That is false.** Verified: **19** artifact files under `docs/evidence/` name `claude-haiku-4-5-20251001`; 4 name `claude-sonnet-5` and those are the **withdrawn** sensitivity subset only.

The architect wrote `PROVENANCE.md` before the model decision changed to Haiku on cost grounds and never returned to it.

**Replace that row with:**

```
| Anthropic API — `claude-haiku-4-5-20251001` | commercial, per terms | every evaluation arm |
| Anthropic API — `claude-sonnet-5` | commercial, per terms | the model-sensitivity subset only, which was WITHDRAWN as a harness defect — see QUESTIONS.md |
```

**Then add a line beneath the table**, in substance:

> An earlier version of this file named `claude-sonnet-5` as the model of every arm. That was wrong — it was written before the model was changed to Haiku on cost grounds, and it was caught at CH-11 by a session checking the claim against the artifacts rather than against the file. Corrected here rather than quietly.

**Verify:** `grep -c "sonnet" PROVENANCE.md` and confirm every remaining occurrence is about the withdrawn subset.

---

## 2 · Q32 — a ruling misattributes what `GOOD.md` says. **Architect's error.**

`QUESTIONS.md` Q19 and `docs/evidence/ch06-a1/a1-result.txt` state that **`GOOD.md` pre-registered the RESTRICTED eval set as primary.** Q32 reports that `GOOD.md` §11 says the opposite.

**Read `GOOD.md` §11 yourself and establish what it actually says.** Then:

- If `GOOD.md` does **not** pre-register the restricted set as primary, the Q19 ruling rests on a false premise about its own pre-registration. **Append a dated correction to Q19** — do not edit the original ruling text — saying what `GOOD.md` actually says, that the architect misdescribed it, and that **the substantive decision (unrestricted set is primary, restricted yields one pair and measures nothing) is unaffected**, because that rests on the pair count, not on the attribution.
- Correct the same misattribution wherever else it appears, including `README.md` if it repeats it.
- If `GOOD.md` *does* say what Q19 claims, record that Q32 was mistaken, with the quote that settles it.

**Quote `GOOD.md` verbatim in the correction so a reader can check without opening it.**

---

## 3 · Q34 — `B0′` is described as compute-matched and is not

Measured: **1,377,402 tokens vs A1's 4,006,662** — roughly a third, not matched.

CH-11 already renamed it a *repeated-sampling control* in the README. **Sweep every other shipping file** — `CONTEXT.md` is protected, so if the phrase appears there, **record it in `QUESTIONS.md` for the architect and do not edit it.** Everywhere you may edit, the arm is a **repeated-sampling control at 3× best-of sampling**, and the token counts are published beside it.

**Say plainly that a genuine compute-matched control was not run.** That is the honest statement and it is stronger than a mislabelled one: it means *"the agent did not simply get more compute"* is supported by the sampling control, not by a token match.

---

## 4 · Q33 — the changelog's "26" does not reproduce

`CHANGELOG.md` says **26** items had samples that disagreed; the votes file gives **22** three separate ways. CH-11 published 22 in the README and raised the question.

**`CHANGELOG.md` is a deliverable and it currently disagrees with the README.** Correct it to **22**, and add a one-line note that an earlier figure of 26 did not reproduce against `<the votes artifact path>` and was corrected at CH-11. Cite the path.

---

## 5 · Q31 — the secret-sweep scope figures disagree

`STATUS.md` and `AI-USE.md` say **450 blobs / 81 commits**; `scan.txt` says **462 / 84**.

**`scan.txt` is the generating artifact and it wins** (hard rule 14). Correct the two summaries to match it, and cite the path. If the difference is because the summaries were written before the last three commits, **say so in one line** rather than silently aligning the numbers.

---

## 6 · Then re-verify the whole shipping surface

Run one sweep over every tracked shipping file — `README.md`, `REPRODUCE.md`, `PROVENANCE.md`, `SAFETY.md`, `THIRD-PARTY.md`, `SUBMISSION.md`, `CHANGELOG.md`, `STATUS.md`, `AI-USE.md`, `QUESTIONS.md`:

- **Every model name** mentioned — does it match the artifacts?
- **Every numeric claim** — does it cite a path, and does that path contain that number?
- **Any remaining "compute-matched"**, or claim that a gate passed when it did not.

**Report what you swept, what you found, and what you could not check.** If a number cannot be traced, say so — do not delete it silently and do not invent a citation.

---

## SCOPE FENCE

**Change ONLY:** `PROVENANCE.md`, `README.md`, `CHANGELOG.md`, `STATUS.md`, `AI-USE.md`, `QUESTIONS.md`, `SUBMISSION.md`, `docs/evidence/ch11c-sweep/`.

**Protected read-only:** `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, **`GOOD.md`** (read it, quote it, never edit it), `src/`, `tests/`, `data/`, `agents/`, `prompts/`, `context/`, every prior `docs/evidence/` directory.

**Corrections are APPENDED where a file is a dated record** (`QUESTIONS.md` rulings, `PROVENANCE.md` — add the correction note, but the wrong table row *is* replaced since it is a factual table, not a dated statement). **Where a file states a live figure** (`README.md`, `CHANGELOG.md`, `STATUS.md`) the figure is corrected in place **and** the correction noted.

---

## GIT

Atomic commits, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
`python tools/export_session.py CH-11c` before you finish.

---

## FINAL OUTPUT

ONE plain-text block:

```
CHUNK CH-11c REPORT
Q35 model name  : PROVENANCE corrected? remaining "sonnet" mentions all about the
                  withdrawn subset? y/n
Q32 GOOD.md s11 : what does it ACTUALLY say - quote it. Was the architect wrong? y/n
                  correction appended, original ruling text untouched? y/n
Q34 B0-prime    : all editable files say repeated-sampling control? token counts
                  published? does any protected file still say compute-matched?
Q33 changelog   : 26 -> 22, note added, path cited? y/n
Q31 sweep scope : summaries now match scan.txt? y/n
SWEEP           : files checked · model names wrong · numbers without a path ·
                  numbers whose path disagrees · anything untraceable
API SPEND       : USD 11.6323 unchanged? (must be yes)
FILES · STATUS LINE · PUSHED SHA · QUESTIONS
TOKENS + COST   : in / out / wall-clock
```

---

## HARD SAFETY RIDER

- No destructive commands, no force-push, no history rewrite. **No model calls.**
- Never print, echo or commit the API key.
- **`GOOD.md` is frozen** — reading and quoting it is required; editing it is a Class A violation.
- **Never delete a number to make a discrepancy go away.** Correct it and say what it was, or report that you could not trace it.
- Ambiguity not covered here → `QUESTIONS.md`, conservative option, continue.
