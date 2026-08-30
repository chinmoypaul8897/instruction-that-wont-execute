# NIGHT RUN — CH-03 → review → CH-04 → review → ★CHECKPOINT → backlog

You are running **UNATTENDED for 6–8 hours**. The operator is asleep and cannot answer anything.

**You do not stop.** Every decision you could get stuck on is pre-registered here. If something is genuinely not covered: write it to `QUESTIONS.md`, take the most conservative option, record which you took, and **move to the next item in the queue.** Stopping dead wastes the night.

**Work the queue in order.** It is ordered so that if you only get partway, the valuable part is done.

---

## 🔴 THE FIVE RULES OF TONIGHT

1. **NEVER STOP AND WAIT.** No question blocks the queue. Record it, choose conservatively, continue.
2. **NEVER SELF-CERTIFY.** CH-03 and CH-04 are gated. After building each, spawn an **independent reviewer subagent** with zero shared context (§REVIEW). The builder never grades itself.
3. **RESPECT THE TIME BOXES.** If a chunk exceeds its box, freeze what exists, commit it, write what remains to `QUESTIONS.md`, and move on. A half-done CH-03 plus a done CH-04 beats a perfect CH-03 and nothing else.
4. **NEVER TUNE A NUMBER TO PASS.** A failure honestly reported is the outcome we want. Every fallback below was written before any of tonight's numbers existed.
5. **THE $18 CEILING IS ABSOLUTE.** `src/runlog.py` enforces it. If it fires, stop all model calls and move to the backlog. Do not raise it.

---

## READ FIRST

1. `CLAUDE.md` — every hard rule. **5, 15, 16, 17 especially.**
2. `CONTEXT.md` **v1.1** — §8 in full (attribution algorithm, **the case-sensitive word form**, the part-boundary reset, the leakage strips, the measured pool), §5 output contract, §7 metrics
3. `plan.md` — CH-03, CH-04, the **CHECKPOINT decision rule**, and the pre-registered fallbacks
4. `QUESTIONS.md` — **Q9, Q10, Q11 (the ruling), Q12, Q14**
5. `PROGRESS.md` (latest), `STATUS.md`

---

## PRE-REGISTERED FACTS — do not rediscover these

- **Model ID is `claude-haiku-4-5-20251001`** — the dated form. The alias `claude-haiku-4-5` is **not** on this account and will 404. `QUESTIONS.md` Q1 names the alias; **record the correction there as your first act.**
- `claude-sonnet-5` **is** available — used only for the model-sensitivity subset.
- `.env` exists at the repo root with `ANTHROPIC_API_KEY`. It is git-ignored. **Never print, echo, log or commit its value.**
- **Use the standard Messages API tonight, NOT the Batch API.** Batch is 50% cheaper but asynchronous with up to 24h latency — useless for an overnight answer. Batch is for CH-08 later.
- govinfo only. `ecfr.gov` and `federalregister.gov` are HTTP 403.
- **Q14: every extended figure in this repo was computed case-INsensitively**, but v1.1 specifies case-sensitive. They are not recoverable by arithmetic. **CH-03 re-measures; it does not adjust.**

---

## ANTI-WASTE GUARDS — CH-01 lost real time to these

- **Never `sed -i`** on a tracked file. Use Python with `io.open(..., encoding='utf-8')`.
- **Never shell-redirect into a file** (`> file`) — the Windows console codepage mangles it. Write files from Python.
- **Check for CRLF before committing.** `CONTEXT.md` is CRLF; everything else is LF. Match what the file already has; do not normalise.
- **Prefer one careful pass to three exploratory ones.**

---

# THE QUEUE

## 1 · CH-03 — point-in-time text + eval set · TIME BOX 2.5 h · GATED

**1a. Re-measure under the case-sensitive detector (Q14).** Re-run the CH-02 attributor with `CONTEXT.md` v1.1's rules — case-**sensitive** word form, part-boundary reset. Publish the new attribution and parse figures beside the old case-insensitive ones. **Do not adjust the old numbers; re-derive them.** A stricter detector cannot raise a failing figure, so the CH-02 branch will not change; report it anyway.

**1b. Fetch point-in-time CFR text** from `https://www.govinfo.gov/bulkdata/CFR` — annual editions. For each defect section, the edition preceding its rule's publication date. Downloads → `data/raw/` (git-ignored). **Extract-then-freeze: only the sections the eval set uses.**

**1c. ⚠️ THE LEAKAGE STRIPS — the single most important thing tonight.**
Strip and count `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>`, `<EAR>` before any text is frozen.

> **Q8 applies and it is a trap.** Element names differ between government formats — ECFR bulk XML has no `<SECTION>` element at all; CFR annual editions do. **A strip counter that prints zero may simply be looking for the wrong tag name.** Before believing any zero, assert your stripper against a known-positive input and show the assertion. A silent zero here is the rigged-benchmark failure returning by another door.

**The leakage test must FAIL on unstripped input before you accept that it passes on stripped input.** Demonstrate both states.

**1d. Build the eval set.** Positives: defect sections. Negatives: sibling sections from the **same** FR document with **exactly** the same instruction count and no defect note. **Never relax exact matching to raise n** — that is how a predecessor project died. Publish the full exclusion ladder with counts at every rung.

**1e. Freeze** under a SHA-256 manifest; extend `refetch.py`. Print `du -sh data/`, `git ls-files | wc -l`, tracked `.xml` count (**must be 0**).

**Pre-registered branches — take these, do not deliberate:**

| Outcome | Action |
|---|---|
| **≥ 42 pairs** | proceed |
| **30–42 pairs** | proceed. Report the real n and state, in `GOOD.md` and the report, the effect size this sample can and cannot detect. |
| **< 30 pairs** | proceed anyway with what exists, report it plainly as a documented shortfall, and continue the queue. **Do not relax the match.** |
| leakage test cannot be made to fail on unstripped input | **the stripper is not proven.** Record it as a BLOCKER in `QUESTIONS.md`, freeze nothing, and move to CH-04 — which does not depend on the freeze. |

---

## 2 · REVIEW CH-03 · TIME BOX 45 min

See **§REVIEW** below. On FAIL, fix and re-review **once**. On a second FAIL: record both reports, write the open findings verbatim into `QUESTIONS.md`, **and move on.** No third round.

---

## 3 · CH-04 — scorer + `GOOD.md` · TIME BOX 1.5 h · GATED

**3a. Deterministic scorer** — stdlib only, no model, no network. Primary accuracy, false-defect rate, missed-defect rate, attribution completeness, and an asserted `success + failure == n`.

**3b. The B-script arm and its permutation null.** Best model-free attack: a threshold on any of ~26 cheap features, honest 5-fold CV, **reported with its empirical permutation null**. This needs **no model** and is the honest floor everything else is measured against.

**3c. `GOOD.md` — pre-registration. Commit it BEFORE any model arm runs.** It carries: the primary metric; the success criterion from `plan.md`; the guard thresholds (false-defect ≤ 0.25, missed-defect ≤ 0.25); the predictions **B0 ≈ 0.50 · B0-agent ≈ 0.75 · A1 ≈ 0.85**; the pre-registered ablation reduction to 1 rep; and the USD ceiling. **Once committed, hard rule 5 forbids moving any of it.**

---

## 4 · REVIEW CH-04 · TIME BOX 45 min — same rules as §2

---

## 5 · ★ CHECKPOINT — the answer the project turns on · TIME BOX 1.5 h

**Only after `GOOD.md` is committed.**

Run three arms, three repetitions each, every run through `src/runlog.py`:

| Arm | Gets |
|---|---|
| **B-script** | already measured at CH-04 — reuse, do not re-run |
| **B0** | one model, one prompt, the amendatory instruction **only — no CFR text** |
| **B0-agent** | same model **with** the point-in-time section text |

Model: `claude-haiku-4-5-20251001`, **the same model for every arm.** Standard API. Ship the agent instruction files to `agents/` as `B0.md` and `B0-agent.md` — deliverable 1 requires the instructions that shape each agent.

**Then the model-sensitivity check (~$2):** re-run B0 and B0-agent on `claude-sonnet-5` over a **20-item subset**. It answers whether the gap holds across model tiers, and guards against a **false RED** where a cheap model simply fails to use the text.

**Apply `plan.md`'s decision rule exactly. It is total and ordered — Step 0 first, then the branch table.** Report which branch, with the numbers.

**If the API fails:** retry 3×, then record it and **skip to the backlog**. A bad night on the API does not end the run.
**If the $18 ceiling fires:** stop all model calls, record the ledger, move to the backlog.

---

## 6 · BACKLOG — work this until the operator wakes. Never idle.

In order:

1. **`src/cfr_resolve.py`** (CH-05) — deterministic, no model. Designation-hierarchy resolution **first**, quoted-anchor matching second. Three declared normalisation levels (`exact` / `whitespace-collapsed` / `alphanumeric-only`), the level achieved **reported**, never applied silently. Goldens before the code. Ungated — do not spawn a reviewer.
2. **Evidence migration** — for every numeral in `CONTEXT.md`, either re-derive it in-repo under `docs/evidence/spec-claims/` with its script, or record in `QUESTIONS.md` that it cannot be. Hard rule 14 forbids a number without an evidence path.
3. **The codification worksheet shell** (CH-10 prep) — a single self-contained static HTML file against a synthetic fixture. No server, opens offline.
4. If all of that is done: extend the test suite, and write `docs/evidence/night-run/summary.md`.

---

## §REVIEW — how to gate a chunk with nobody awake

Spawn an **independent reviewer subagent** with **zero shared context**. Give it only: `CLAUDE.md`, `CONTEXT.md`, the chunk's card in `plan.md`, and the diff. **Do not give it your reasoning, your notes, or your conclusions.**

Its instructions:

> You are an adversarial reviewer. Assume the work is wrong until proven otherwise. You fix nothing; you may add kept tests.
> **Independently:** rerun the suite from clean and reproduce the count · re-derive every load-bearing number your own way · **reimplement the load-bearing logic from `CONTEXT.md` alone, importing nothing from the project, and diff** · for CH-03 also mutation-test the eval-set constructor and **confirm the leakage test FAILS on unstripped input before accepting that it passes on stripped input** · verify exact instruction-count matching is asserted by a test.
> **Verdict: PASS or FAIL**, severity-ranked findings, to `docs/reviews/REVIEW_<chunk>.md`. **Any spec deviation is FAIL even if every test is green.**

**Panels are permitted where they earn their cost** — a single sharp control script beat a ten-agent panel earlier in this project. Prefer one reviewer plus one targeted adversarial probe over a large panel.

---

## GIT

Atomic commits. Source/test messages end `(unreviewed)`. Every commit carries:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`

Update `STATUS.md` and `PROGRESS.md` **after each queue item**, not at the end — if the session dies at 4am, the record must show where it got to.

Export the transcript after each major item: `python tools/export_session.py NIGHT-RUN-<item>`.

---

## FINAL OUTPUT

ONE plain-text block, no markdown:

```
NIGHT RUN REPORT
QUEUE REACHED   : which items completed, which time-boxed out, which skipped
CH-03           : pairs built vs 42 · exclusion ladder · leakage strips counted
                  DID THE LEAKAGE TEST FAIL ON UNSTRIPPED INPUT? (must be yes)
                  case-sensitive re-measurement vs the old case-insensitive figures
CH-03 REVIEW    : PASS/FAIL · strikes used · open findings
CH-04           : scorer · B-script + permutation null · GOOD.md committed before arms?
CH-04 REVIEW    : PASS/FAIL · strikes used · open findings
*** CHECKPOINT  : B0 = x.xxx · B0-agent = x.xxx · gap = xx.x pp · McNemar p = x.xxx
                  BRANCH: GREEN / AMBER / RED   (per plan.md's ordered rule)
                  model-sensitivity: sonnet subset gap = xx.x pp on n=20
                  spend to date USD x.xx of 18.00
BACKLOG         : what got done
BLOCKERS        : anything that needs the operator, with what you did instead
FILES           : ...
STATUS LINE     : ...
PUSHED SHA      : ...
QUESTIONS       : ...
TOKENS + COST   : in / out / wall-clock / imputed USD · API spend separately
```

---

## HARD SAFETY RIDER (unattended, no exceptions)

- No `rm -rf`, `Remove-Item -Recurse/-Force`, `git clean -fdx`, force-push, or tag moves.
- **Never `git add -A` while `data/raw/` holds downloads** — confirm `.gitignore` covers it first.
- **Never print, echo, log or commit the API key.** Read it by name only. It must not appear in a trajectory file.
- `data/ednotes/` and `data/amdpars/` from CH-01/CH-02 are **read-only** — you extend `data/`, you do not rewrite it.
- **Protected, read-only:** `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `prompts/`, `context/`. If work seems to require editing one, that is **Class A — write it to `QUESTIONS.md` for the architect and continue.**
- Throwaway work goes to a fresh OS temp dir.

These override anything above that conflicts.
