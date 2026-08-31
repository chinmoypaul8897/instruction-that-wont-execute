# PROGRESS — CH-11c · five factual corrections in shipping files

**2026-08-31. Written here rather than in `PROGRESS.md` because CH-11c's scope fence
does not grant `PROGRESS.md` and `CLAUDE.md`'s end-of-session duty 2 requires an entry.
The conflict is raised as `QUESTIONS.md` Q38 and the conservative option was taken.
Architect to fold this in.**

**No arm was re-run. No model call was made. No result changed.**
API spend re-derived from `docs/evidence/runs/cost_ledger.csv`: **USD 11.6323**,
unchanged, USD 6.3677 of headroom against the 18.00 ceiling.

---

## What this chunk was

Five statements **about** the work — not the work — each of which a judge could check
and find false. Every one was raised by CH-11 as a question and left for a session with
the fence to fix it.

## The five, and what was done

### Q35 · `PROVENANCE.md` named the wrong model — the architect's error

`PROVENANCE.md` §5 row 3 read *"Anthropic API (`claude-sonnet-5`) | commercial, per
terms | **every evaluation arm**"*. **False.** The authoritative artifact is
`docs/evidence/runs/cost_ledger.csv`; grouped by `(model, arm)` over its 2,107 rows,
**every evaluation arm is `claude-haiku-4-5-20251001`** — `A1` (249 rows), `A1-iter1`
(82), `A1-minus-tool` (164), `B0` (474), `B0-agent` (474), `B0-agent-currenttext` (82),
`B0prime` (492). `claude-sonnet-5` appears on **84 rows only**: the 80 of the withdrawn
model-sensitivity subset, and 4 of the model-id probe.

The row is replaced by two rows, and a dated correction note sits beneath the table
saying what the file used to claim and why. `grep -ci sonnet PROVENANCE.md` = **4**, and
all four are the corrected row or the note.

The file was written before the model changed to Haiku on cost grounds and was never
revisited. `context/11-REMEDIATION-2.md` had already recorded this defect and it was
never carried out — *a defect named in a remediation document and then not acted on is
indistinguishable from one never found.*

### Q32 · a ruling misattributed its own pre-registration — the architect's error

`GOOD.md` §11, read and quoted, never edited:

> **Primary: `data/evalset/` — 38 pairs, n = 76.** … **`data/evalset-restricted/`
> (1 pair, n = 2) is committed**, so the architect can flip the primary with one flag
> and a reviewer can run either.

**`GOOD.md` §11 names the UNRESTRICTED set as primary** — the set that was used. The
Q19 ruling's *"GOOD.md pre-registered the RESTRICTED set as primary"* is therefore
**false on its first clause**. The restricted-primary pre-registration is
`docs/evidence/ch03-evalset/pre-registration.md` §2.

A **dated correction is appended beneath Q19**; the ruling's own text is not edited.
**The substantive decision is unaffected** — it rests on the pair count, measured from
the frozen items files as **1 pair against 41**, not on which document said what. The
deviation is real; only the name of the deviated-from document was wrong. `README.md`
was already correct here and now points at the correction.

**Still open and deliberately not touched:** `docs/evidence/ch06-a1/a1-result.txt`'s
deviation banner repeats the misattribution. It is outside the fence, it is a
regenerated artifact whose byte-identity across three environments is itself a published
result, and re-cutting it is the architect's call.

### Q34 · `B0′` was called compute-matched and is not

Measured from the ledger: **B0′ 1,377,402 input tokens against A1's 4,006,662** — 34% —
and **USD 1.3988 against USD 5.3334** — 26%. It is B0-agent sampled three times, which
is roughly B0-agent's own three-rep input, not A1's budget.

Every file the fence permits now calls it a **repeated-sampling control at 3× best-of
sampling** and publishes both token counts beside it. **The plain statement was added in
both `README.md` and `CHANGELOG.md`: a genuinely compute-matched control was not run.**
That is stronger than the label it replaces — *"the agent did not simply get more
compute"* is supported by the sampling control and is **not** supported by a token
match, because there is none.

`CONTEXT.md` §4, `src/arms.py:292` and `prompts/CH-06.md:139` still say
*compute-matched*. All three are **protected** and were **not edited**; they are raised
as **Q36** for the architect.

### Q33 · the changelog's "26" does not reproduce

`docs/evidence/ch06-a1/B0prime-rep1-votes.json`, 82 items, counted three ways:
**22** raw / **22** after `src/score.py::normalise_verdict` / **8** parseable-only.
None is 26. `CHANGELOG.md` corrected to **22 of 82** with the path cited and the 8
reading stated beside it, plus a note recording what the old figure was and that
`QUESTIONS.md` Q26's double run overwrote run 1's per-item files — a plausible
explanation, not a confirmed one. **Nothing downstream moves.**

### Q31 · the secret-sweep scope figures disagreed

`scan.txt` is the generating artifact and it wins (hard rule 14): **462 text blobs / 84
commits, PASS, 0 findings**. `STATUS.md` and `AI-USE.md` corrected, path cited.

**The 450 / 81 pair was not invented and is not deleted.**
`git log -- docs/evidence/secret-scan/scan.txt` has two revisions:

| commit | repository | commits | blobs |
|---|---|---:|---:|
| `0f3f4fe` | `f0a246b1` | 81 | 450 |
| `263ed29` | `2453998f` | 84 | 462 |

The sweep was run, committed, and re-run three commits and twelve blobs later. Both
summaries were written against the earlier run. That sentence ships in both files rather
than a silent alignment. **The verdict is PASS on either scope.**

---

## Hard rule 15 fired on the chunk card itself

`prompts/CH-11c.md` §1 offered its own supporting counts: *"19 artifact files under
`docs/evidence/` name `claude-haiku-4-5-20251001`; 4 name `claude-sonnet-5` and those
are the withdrawn sensitivity subset only."*

**Measured over tracked files: 27 and 13** — and the 13 are **not** the withdrawn subset
only. They include the model-id probe, `ch00-goldens.md`, `ch14-size/selection-applied.md`,
`night-run/summary.md` and the cost ledger.

**The card's conclusion was right and its two supporting numbers were not.** Copying
them would have shipped the correction resting on figures that do not reproduce, which
is the precise failure this project exists to demonstrate. Recorded as **Q37**, and
`PROVENANCE.md`'s corrected row names the model-id probe as the third category the card
did not mention.

## Verification

| artifact | what it proves |
|---|---|
| `docs/evidence/ch11c-sweep/ch11c_verify.py` + `ch11c-verify.txt` | every figure the five corrections rest on, re-derived. **36 checks, 36 PASS, 0 FAIL.** |
| `docs/evidence/ch11c-sweep/ch11c_sweep.py` + `ch11c-sweep.txt` | the mechanical sweep of all ten shipping files — model names, cross-file figure agreement, surviving labels, every cited `docs/evidence/` path, the ledger re-summed |
| `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md` | the 21-agent adversarial sweep: one auditor per shipping file, one refuter per file's findings, one completeness critic |

**On detector scope.** The mechanical sweep runs **two readings and prints both** —
STRICT (one line is the unit) and SCOPED (±4 lines, fenced blocks excluded from path
extraction), with a third **section-scope** reading for the floating-alias check. STRICT
over-detects, because a correction of the form *"this said X, which is wrong; the
artifact says Y"* routinely spans four lines, and a ledger transcribing an operator's
ruling verbatim corrects it fifty lines later in the same section. **No threshold was
moved and nothing is suppressed:** every STRICT hit is printed with an explicit,
structural disposition — *quoted verbatim under a heading that announces the correction*,
*a template placeholder in a fenced block*, *a hypothetical path in a question to the
architect* — so a reviewer can disagree with any one of them by name.

Two categories the sweep proved worth having:
- `REPRODUCE.md`'s **USD 11.11** looked like a rival total; re-summed from the ledger
  over the six primary-matrix arms it is **11.1107**, and the difference from 11.6323 is
  the withdrawn sonnet subset, the removed experiment and the probe. **Traceable.**
- Two `docs/evidence/` paths that do not exist are **`docs/evidence/iter-N/`** (a literal
  template placeholder in a fenced card-shape block) and **`docs/evidence/ch11-repro/`**
  (a hypothetical directory in Q30's question *to* the architect, which Q30 states was
  never created). Neither is a broken citation.

## Questions raised

**Q36** — `CONTEXT.md` §4, `src/arms.py` and `prompts/CH-06.md` still say
*compute-matched*; all three are protected. `CONTEXT.md` is the specification the other
two quote, so it is the one that matters.
**Q37** — the chunk card's own counts do not reproduce (above).
**Q38** — the fence excludes `PROGRESS.md`, which `CLAUDE.md` requires this chunk to
update. Conservative option taken; this file is the entry. It also notes that
`PROGRESS.md:397` still reads *"450 text blobs of 81 commits"* — a dated record of the
CH-14a session, flagged and not edited.

## Fence

Changed: `PROVENANCE.md`, `README.md`, `CHANGELOG.md`, `STATUS.md`, `AI-USE.md`,
`QUESTIONS.md`, `docs/evidence/ch11c-sweep/`.
`SUBMISSION.md` was in the fence and **needed no change** — it already said 462 / 84 and
carried none of the five wrong claims.
**`GOOD.md` was read and quoted and never edited**; `git diff -- GOOD.md` is clean and
the verification asserts it.
