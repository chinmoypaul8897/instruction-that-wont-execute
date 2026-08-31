# CH-14a — clear the submission blocker, then the clean-clone rehearsal

You are a **BUILD session**. **TIME BOX 1.5 h.** Packaging has started; measurement is over.

**No arm is re-run. No number changes. `GOOD.md` is frozen.** If anything below appears to move a published figure, **STOP and report.**

---

## 🔴 THE BLOCKER — this is why you exist

**The tracked tree is 59.4 MB. The HackerEarth upload cap is 50 MB.** As things stand **the submission cannot be uploaded**, which fails the completeness check before anyone reads a line of it.

Verified now:

```
tracked total : 59.4 MB   (cap 50)
  7.2 MB  data/attribution-v11/amdpars_v11.jsonl
  7.1 MB  data/amdpars/amdpars.jsonl
  3.5 MB  docs/trajectories/build/NIGHT-RUN-FINAL.jsonl
  3.0 MB  docs/trajectories/arms/B0prime-rep1.jsonl
  3.0 MB  docs/trajectories/build/NIGHT-RUN-CHECKPOINT.jsonl
  2.7 MB  docs/trajectories/arms/A1-rep1.jsonl
```

**Q25 also records that the guard built to prevent this never sums bytes.** Fix the guard as well as the symptom, or it recurs.

---

## READ FIRST

1. `CLAUDE.md` — every hard rule
2. `PROCESS.md` §3 — the ship/no-ship ledger
3. `QUESTIONS.md` — **Q25** (the blocker), **Q26** (the double-run), Q21, Q23
4. `prompts/CH-00.md` Q2 — the four submission-form constraints, **C1 and C2 especially**

---

## 1 · Clear the blocker · 45 min

**The repository stays complete. The ZIP is what must fit.** Q2's C2 already rules how:

> *The PDF requires "**representative** trajectories for every agent you used", not all of them. Ship a curated representative set in the zip; ship the complete set in the git repo and link it from the Description. Record the selection rule so the curation is auditable.*

**Do this — in this order:**

**1a. Measure honestly first.** Write `docs/evidence/ch14-size/inventory.md`: every tracked path over 256 KB with its size, and the total. This is the before-picture and it ships.

**1b. Apply the published selection rule.** `docs/evidence/ch14-size/selection-rule.md`, written **before** you drop anything:

- one trajectory per **agent class** — build, arms, probe
- for the arms: the **first** run, the **median-cost** run, one containing a **retry**, one containing a **`human_checkpoint`** record
- **every run whose verdict disagreed with gold** — failures are never filtered out
- everything else stays in git history and is linked from the submission Description

**1c. Reduce the zip, not the repo.** Prefer a `.gitattributes`-driven `export-ignore` or an explicit exclude list used by `git archive`, so the repository keeps everything and only the archive is trimmed. **If a file must actually leave git, say so explicitly and record why.**

**1d. Check the derived numbers.** `data/attribution-v11/amdpars_v11.jsonl` and `data/amdpars/amdpars.jsonl` are 14.3 MB together and are **derived** from `data/raw/` via `refetch.py`. If `refetch.py` reproduces either byte-identically, it belongs in the archive's exclude list, not in the upload. **Prove the reproduction before excluding — a manifest check, shown.**

**1e. Fix the guard.** The pre-commit hook checks per-file size and file count but **never sums bytes**. Add a total-tracked-bytes check that fails at **45 MB**, leaving headroom under the 50 MB cap. Ship a probe that **fails on the current tree and passes after the fix** — both states shown.

**Done when:** `git archive --format=zip HEAD` produces a file **under 45 MB**, and the number is printed.

---

## 2 · Fix `GOOD.md`'s stale n — **read this carefully before touching it**

`GOOD.md` records **n = 76 / 38 pairs**. The shipped eval set is **n = 82 / 41 pairs**.

**This is NOT a threshold change and must not become one.** The success *criterion* (n ≥ 84, gap ≥ 8 pp, p < 0.05, A1 ≥ 0.80) is **frozen and stays exactly as written** — it was already ruled NOT MET on all four clauses and that verdict stands.

What is wrong is a **descriptive** figure: `GOOD.md` describes the corpus as smaller than it is. Correct it by **appending a dated addendum**, never by editing the original text:

```
## ADDENDUM 2026-08-31 - descriptive correction, no criterion moved
GOOD.md was written when the eval set stood at 38 pairs / n=76. CH-03's review
found and fixed a selection defect and the shipped set is 41 pairs / n=82.
The SUCCESS CRITERION IS UNCHANGED - n>=84, gap>=8pp, p<0.05, A1>=0.80 - and it
was ruled NOT MET on all four clauses at CH-06. Both the original figure and the
shipped figure are shown so a reader can see the criterion was never adjusted to
the corpus. Ruling: QUESTIONS.md Q16.
```

**If you find yourself deleting or rewriting any original line of `GOOD.md`, stop.**

---

## 3 · Clean-clone rehearsal · 30 min

1. Clone to a **second path**. Fresh venv from a pinned `requirements.txt` (Python 3.12.2).
2. **Network off.** Verify the SHA-256 manifest.
3. **Tier-1 replay** — rescore the committed run artifacts offline, and confirm it reproduces the published headline numbers exactly: **checkpoint gap +18.3 pp / p = 0.0059**, **A1 0.7195 vs B0-agent 0.6585 / p = 0.4244**.
4. Then **extract the zip to a third path and run the Tier-1 replay FROM THE EXTRACTION.** The zip is what a judge opens; it is the thing that must work.
5. `gitleaks`-style secret sweep over the **full history**, plus an explicit sweep of `docs/trajectories/**` for `sk-ant`, `AIza`, `Bearer `, and the operator's phone number. **PASS = zero.** Commit the tool version and the clean output.

**If the replay from the extraction fails, that is the most important finding of the day — report it immediately and stop.**

---

## 4 · If time remains

Write `SUBMISSION.md` at the repo root listing the six items the FAQ names — repository, archive, tests, README, agent-use evidence, demo video — each with its path or URL, so a validator ticks them without hunting. Leave the video URL as `TBD`.

---

## SCOPE FENCE

**Change ONLY:** `.gitattributes`, `.githooks/pre-commit`, `GOOD.md` (**addendum only**), `SUBMISSION.md`, `docs/evidence/ch14-size/`, `docs/evidence/secret-scan/`, `tests/`, `STATUS.md`, `PROGRESS.md`, `AI-USE.md`, `QUESTIONS.md`.

**Protected read-only:** `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `agents/`, `src/`, `data/`, `prompts/`, `context/`, every `docs/evidence/` directory from a prior chunk.

**Do NOT** run any arm, re-score anything, or change a published number.

---

## GIT

Atomic commits, `(unreviewed)`, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`

`python tools/export_session.py CH-14a` before you finish.

---

## FINAL OUTPUT

ONE plain-text block:

```
CHUNK CH-14a REPORT
*** ZIP SIZE    : before xx.x MB -> after xx.x MB   (cap 50, target < 45)
                  what was excluded and under which clause of the selection rule
                  guard probe: fails-on-old / passes-on-new, both shown
GOOD.md         : addendum appended? ANY original line changed? (must be NO)
CLEAN CLONE     : manifest verified? Tier-1 replay reproduces +18.3/p=0.0059 and
                  0.7195/0.6585/p=0.4244 EXACTLY? y/n
FROM THE ZIP    : replay run from the EXTRACTION, not the clone? y/n
SECRET SWEEP    : tool, scope (full history?), findings (must be 0)
SUBMISSION.md   : written? six items listed?
FILES · STATUS LINE · PUSHED SHA · QUESTIONS
TOKENS + COST   : in / out / wall-clock · API spend unchanged at USD 11.63?
```

---

## HARD SAFETY RIDER

- No destructive commands, no force-push, no history rewrite. **If clearing the blocker seems to need a history rewrite, STOP and report** — that is an architect decision.
- Never print, echo or commit the API key.
- **No model calls.** API spend must be unchanged at the end.
- Ambiguity not covered here → `QUESTIONS.md`, conservative option, continue.
