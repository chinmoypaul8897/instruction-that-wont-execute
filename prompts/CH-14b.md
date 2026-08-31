# CH-14b — the submission Description, housekeeping, and the last in-fence findings

You are a **BUILD session**. **TIME BOX 1 h.** **Runs in parallel with CH-13B.**

**CH-13B holds:** `docs/slides/`, `tests/test_slides.py`, `docs/video/`, `docs/evidence/ch13b/`, `dist/`, `.gitignore`. **Do not touch any of those.** Commit only your declared paths; **never `git add -A`**; `git pull --rebase` before pushing.

**No arm is re-run. No result changes. No model calls.** API spend must read **USD 11.6323** at the end.

---

## 🔴 PART 1 IS THE PRIORITY — the Description does not exist

The HackerEarth form has four required fields. Three are handled. **The Description is not drafted anywhere**, and it is **the first thing a judge reads** — the 20 seconds that decide whether the rest is read carefully.

Write it to **`docs/submission-description.md`**, ready to paste. The operator does a voice pass on it afterwards, so **write it to be improved by a human, not to be admired.**

### What it must do, in this order

1. **One sentence: what this is.** Not "an agentic workflow that leverages" — what it *does*, for whom.
2. **The honest headline, immediately.** The result is a null: A1 beats the strongest baseline by **+6.1 pp** at **p = 0.4244** on **n = 82**, and the pre-registered criterion is **met on none of its four clauses**. Say it plainly, near the top, in the same tone as everything else.
3. **The result that is significant:** giving the agent the point-in-time CFR text moves **+18.3 pp, p = 0.0059** — independently reproduced from scratch to zero error by a reviewer.
4. **The finding worth reading:** tool alone **−9.8**, procedure alone **−1.2**, together **+6.1** — **+17.1 pp above additive.** Neither capability helps alone; the procedure repairs a defect in the tool. *That* is the answer to "which design choices helped".
5. **How to verify it in 90 seconds:** the offline Tier-1 replay, one command, no API key, reproduces every headline number byte-identically. **Rehearsed from the extracted zip.**
6. **The GitHub URL** — there is no repo field on the form, so it lives here.
7. **One line on method**, because it is the thing that separates this: chunked builds, each gated by an independent adversarial review with zero shared context. **Say plainly that six gated chunks did not pass, that this is disclosed in the README's LIMITATIONS section, and that one review found a six-line script with no model beating the agent by 17 points — a rigged benchmark caught before it shipped.**

### Constraints

- **Under 400 words.** Shorter is better. A judge reads the first 60.
- **No markdown headings** — many form fields render them as literal `#`. Short paragraphs, plain text, at most one short list.
- **Every number that appears must be true and traceable.** Verify each in its artifact before writing it. No number appears here that is not already in the README.
- **Character limit is UNKNOWN** — the operator has not reported one. Also produce a **≤ 1,200 character** cut-down at the bottom of the same file, so there is a fallback if the field is small.
- **Also draft the Title** — under 80 characters, a name not a summary. Offer three options and mark your recommendation.

### 🔴 Voice — this is where slop shows most

Banned: *delve · leverage · robust · comprehensive · seamless · cutting-edge · it's worth noting · furthermore · in today's landscape · we are excited to*. No em-dash-heavy rhythm. **No sentence that could describe any other project.**

Read it back and ask: **does this sound like a person who did the work, or like a summary of it?** If the second, rewrite.

---

## PART 2 · Housekeeping · 15 min

**Track the six untracked files.** They are agent instructions and deliverable-1 evidence:

```
docs/video-script.md
prompts/CH-11.md  prompts/CH-11c.md  prompts/CH-12.md
prompts/CH-13A.md  prompts/CH-13B.md
```

*(`prompts/CH-14b.md` — this card — too, once it exists on disk.)*

**Then close two open questions:**

- **Q42** — `docs/trajectories/build/NIGHT-RUN-FINAL.jsonl` ships and is disclosed nowhere. Add it to `docs/trajectories/INDEX.md` and `AI-USE.md`, naming what it contains: **both CH-03 reviewers, their launch prompts and their FAIL verdicts verbatim.** That is the most valuable process evidence in the repository and it is currently unlabelled.
- **Q40** — `SELECTION-RULE.md` clause T1 names an agent class with **zero** trajectories. Either the class is wrong or the trajectory is missing. **Establish which by reading the artifacts**, then correct the rule or record why the class has none. Do not delete the clause silently.

---

## PART 3 · The last in-fence sweep findings · 20 min

CH-12's Q39 update left **16 in-fence findings** needing a rewrite. Work down by severity, in `AI-USE.md`, `QUESTIONS.md`, `STATUS.md`, `PROGRESS.md`, `README.md`, `SUBMISSION.md`.

Named as the worst:
- **`AI-USE.md`'s SPEC-FIX-2 and CH-02 usage tables disagree with their artifacts on every row.**
- `CHANGELOG.md`'s `0.4737` — **`CHANGELOG.md` is out of your fence. Record it for the architect, do not edit it.**

**Method, not optional:** re-verify each finding against the **current** file before acting. CH-12 re-checked 75 and **14 did not reproduce.** Fix what is real, report what is not, and **never delete a number to make a discrepancy go away** — correct it and say what it was, or report it as untraceable.

**Complete `SUBMISSION.md`** — every row satisfied except the video URL, which stays `TBD` until the operator uploads.

---

## SCOPE FENCE

**Change ONLY:** `docs/submission-description.md` (new), `SUBMISSION.md`, `README.md`, `AI-USE.md`, `QUESTIONS.md`, `STATUS.md`, `PROGRESS.md`, `docs/trajectories/INDEX.md`, `docs/trajectories/SELECTION-RULE.md`, `docs/evidence/ch14b/` (new), and `git add` the untracked files listed in Part 2.

**Do NOT touch:** anything CH-13B holds (see the header) · `CHANGELOG.md` · `CONTEXT.md` · `plan.md` · `PROCESS.md` · `CLAUDE.md` · `GOOD.md` · `PROVENANCE.md` · `src/` · `data/` · `agents/` · `tests/`.

---

## GIT

Atomic commits, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
`git pull --rebase` before pushing. `python tools/export_session.py CH-14b` before you finish.

---

## FINAL OUTPUT

ONE plain-text block:

```
CHUNK CH-14b REPORT
*** DESCRIPTION : docs/submission-description.md - word count · character count
                  cut-down version present and under 1,200 chars? y/n
                  three Title options + your recommendation
                  every number verified in its artifact? list number -> path
                  self-check: does it sound like a person who did the work? y/n
HOUSEKEEPING    : six files tracked? y/n · Q42 closed (NIGHT-RUN indexed)? ·
                  Q40 resolved - which way, and on what evidence?
SWEEP           : re-verified how many · did not reproduce · fixed · left with reasons
                  out of fence (list)
SUBMISSION.md   : which of the six rows are satisfied · which are TBD
PARALLEL        : files committed (declared only?) · rebase clean? · did you touch
                  anything CH-13B holds? (must be no)
API SPEND       : USD 11.6323 unchanged? (must be yes)
FILES · PUSHED SHA · QUESTIONS
TOKENS + COST   : in / out / wall-clock
```

---

## HARD SAFETY RIDER

- No destructive commands, no force-push. **No model calls.**
- Never print, echo or commit the API key. **Do not commit `dist/`.**
- **Never write a number you have not verified in its artifact.**
- **Never `git add -A`** — CH-13B is running and `dist/` must not slip in.
- Ambiguity not covered here → `QUESTIONS.md`, conservative option, **continue**.
