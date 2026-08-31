# PROVENANCE — what existed before the competition, and what was built during it

> **Ground rule 02:** *"Make it clear what existed before the competition and what you added."*

This file exists so a judge does not have to infer it from timestamps. Every claim below is checkable against file modification times, git history, and the public URLs given.

**Kickoff: 2026-08-28 15:00 UTC. Deadline: 2026-08-31 18:00 UTC.**

---

## 1. Built entirely during the competition

**Everything in `src/`, `tests/`, `data/`, `docs/`, and every project artifact.** No line of this project's source existed before 2026-08-30 03:00 UTC. The git history is the record; the first commit is the beginning of the project.

This includes:
- the corpus harvest, the AMDPAR attributor, the eval-set constructor
- the deterministic scorer and the pre-registration
- `cfr_resolve`, `SKILL.md`, the ordered-state ledger
- every arm, every measurement, every evidence pack
- the codification worksheet, the README, the reproduction guide

---

## 2. Research scaffolding — 8 entries before kickoff, 35 after, and no project code in any of it

**2026-08-27, approximately 21:45 UTC — seventeen hours before kickoff.**

- `scraper/recon.cjs`, `sections.cjs`, `sections2.cjs`, `mapimg.cjs`, `slice.cjs` — Playwright recon scripts written to read the **public** HackerEarth challenge page, with their npm tooling (`package.json`, `package-lock.json`, `node_modules/`). That is **8 of `scraper/`'s 43 entries**. **The other 35 were written AFTER kickoff** — 2026-08-29, 03:13–06:21 UTC, **12.2 to 15.4 hours** past the 15:00 UTC line — and they are `portfolio.cjs`, `work.cjs`, `li.cjs`, `hn.cjs`, `he.mjs`, `rd.mjs`, `rd2.mjs` and 28 page dumps, of which **31** read the **operator's own** portfolio, LinkedIn and blog into `context/me/` or public commentary on the challenge into `rd_*.txt`, and **4** — `he.mjs` with `he_page.txt` and `he_links.json`, plus one `rd_*.txt` — re-read the same **public** HackerEarth challenge page the pre-kickoff five did. **Corrected at CH-12**, because dating all 43 to before kickoff is exactly the kind of claim ground rule 02 exists to make checkable. None of the 35 is problem work, none is reused, and `scraper/` is git-ignored in its entirety — so the substance of this section is unchanged and only its dating was wrong.
- `context/00-MASTER-CONTEXT.md` — an extraction of that public page, including content that was only present inside images (the rubric weights, the timeline, the registration deadline).

**Why this is not problem-specific work.** Two different defences, for two different sets, and they are separated here because the first does not cover the second. **For the 8 pre-kickoff entries:** the problem did not exist yet — the brief was released at kickoff, so nothing produced before 15:00 UTC on 2026-08-28 could have addressed the actual task. **For the 35 post-kickoff entries:** the date is no defence at all, and none is claimed. They gather the operator's own dossier and public commentary, they contain no problem work, and nothing they produced is used by the submitted system. **Neither set is part of it:** `scraper/` is excluded from the repository in its entirety by `.gitignore`, and `git ls-files scraper` is empty.

**Ground rule 01 expressly permits this:** *"You are welcome to build with tools and components you already know."* The tooling used was Playwright, cheerio and sharp — public libraries, used under their own licences.

---

## 3. Produced after kickoff, before coding — the decision record

**2026-08-29 to 2026-08-30.** All of this is the contestant's own work, produced with coding agents, and is shipped because it is evidence of method rather than reused code:

| Artifact | What it is |
|---|---|
| `context/03-IDEA-REVIEW-VERDICT.md` | 13 agents attacking the first candidate — 5 hostile critiques, 2 alternative passes, 6 rubric scorings, counted from `context/03b-review-raw.json`. It died. |
| `context/04-STRATEGY-BRIEF.md` | Research on the judging organisation and the competitive field. |
| `context/05-FINAL-DECISION.md` | A five-way design tournament. |
| `context/06-DIVERGENT-RESEARCH.md` | 143 candidate projects generated from 18 angles. **All 143 died.** |
| `context/07-KILL-TEST.md` | The surviving candidate destroyed by a 30-line script scoring 100%. |
| `context/08-FINAL-CALL.md` | The chosen project, after five audits and five rival architectures. |
| `context/09-COMPLIANCE-AUDIT.md` | An independent audit of this project's own build plan. |

**Two projects were killed before a line was written**, and both kills are in the record with the measurements that caused them. That is the point of shipping these.

---

## 4. Method that pre-existed — disclosed, because it is load-bearing

`PROCESS.md` — the build process used here — derives from a method the contestant developed and **published before this competition**, on projects unrelated to it:

- `github.com/chinmoypaul8897/acumen` (public since July 2026) — 28 adversarial review reports
- `github.com/chinmoypaul8897/nistula-assistance-` (public, last pushed **2026-08-18**, ten days before kickoff) — documents the multi-agent review gate and reports **17 blocker-class defects found while the test suite was green**

**The method is prior art and is not claimed as new here.** What is new is its application to this problem, and the process file itself was rewritten for this project's constraints.

The `nistula-assistance-` result is cited in this project's README — [`README.md` §f, "the premise underneath the whole project is prior art"](README.md) — as the *motivating hypothesis* for why a green test suite is insufficient evidence, never as a result of this project. No code, data, or artifact from either repository is reused here.

**Correction, 2026-08-31 (CH-12). The sentence above was FALSE from the day it was written until the commit that carries this note.** It asserts something about the contents of another file, and that file did not contain it: `README.md` held **zero** occurrences of `nistula`, of `17 blocker` and of `github.com`. The cause is ordinary and worth naming — **this section was written before `README.md` existed.** `git log --diff-filter=A` puts this file's first commit at `3ac8207`, **2026-08-30 18:03:46 +0530**, and the sentence is in that first version (`git show 3ac8207:PROVENANCE.md | grep -ci nistula` → 2); `README.md` was created at `67a5206`, **2026-08-31 11:36:59 +0530**, **17 h 33 min later**. The sentence described what the author intended the README to say, and nobody ran the grep. **One `grep -c` falsifies it**, and a disclosure claim under ground rule 02 is exactly the kind of claim a judge is entitled to check.

Two lawful repairs existed: make the README cite it, or correct this file to say it does not. **The first was taken** — the citation is real, it is in the README's hot-take section beside the other prior-art credit, and it states in terms that the 17-defect number is *not* re-derived here and carries no weight here. Re-verified after the edit: `grep -ci nistula README.md` = **1**, `grep -ci '17 blocker' README.md` = **1**, `grep -ci github.com README.md` = **1**. `acumen` remains **0** and is not claimed above. Evidence: [`docs/evidence/ch12/`](docs/evidence/ch12/).

*This is the **fourth** correction in this file — §2's dating error, shipped in the very same commit as this note, is the third — and the pattern in all four is the same: a sentence about the work, written once, never re-checked against the thing it describes. **The miscount is itself the fourth instance.** It survived only because the evidence script counts with a line-anchored `grep '^\*\*Correction'`, which structurally cannot see §2's inline `**Corrected at CH-12**`; a reader counting by reading counts four. Caught by this chunk's own adversarial audit, and corrected rather than re-defined.*

---

## 4b. Verification of the brief extraction — 2026-08-30

`context/01-PROBLEM-PDF.md` is our transcription of micro1's problem PDF, and every requirement in this project was validated against it rather than against the original. That made it a single point of failure, so it was checked.

**Checked against the original document, 2026-08-30:**

| Item | Result |
|---|---|
| Rubric weights — 15 / 30 / 20 / 15 / 15 / 5 = 100 | ✅ exact match |
| Anti-slop clause, End-to-End Quality | ✅ verbatim |
| All ten ground rules, opening clauses | ✅ match |
| Four deliverable headings | ✅ match |
| Passages marked *(decoded)* — our analysis, not micro1's words | 4, all in analysis sections (capability menu, deliverable→rubric mapping, what the examples share). **None is a requirement, and no downstream document quotes one as authoritative.** |

The extraction is faithful on every load-bearing element. Recorded here because a plan validated against a transcription is only as good as the transcription.

---

## 5. Third-party components — used, not authored

| Component | Licence | Role |
|---|---|---|
| CFR / Federal Register / eCFR data from govinfo.gov | **Public domain, 17 U.S.C. §105** | the corpus |
| Python standard library | PSF | the scorer, deliberately dependency-free |
| Anthropic API — `claude-haiku-4-5-20251001` | commercial, per terms | every evaluation arm. Temperature 0 on all of them **except `B0prime`, which ran at temperature 1.0** — best-of-3 self-consistency at 0 draws the same deterministic sample three times, so the control could not exist at 0 (`QUESTIONS.md` Q22). |
| Anthropic API — `claude-sonnet-5` | commercial, per terms | the model-sensitivity subset only, which was **WITHDRAWN** as a harness defect — the architect's ruling *"MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31"*, recorded in `QUESTIONS.md` under **ARCHITECT RULINGS — 2026-08-31** (not Q19, which is the CH-03 escalation). No claim in this submission rests on it. Also the four rows of the model-id probe. |
| Claude Code | commercial, per terms | wrote this project — see `AI-USE.md` |

**Correction, 2026-08-31 (CH-11c).** An earlier version of this file named
`claude-sonnet-5` as the model of *every evaluation arm*. **That was wrong.** It was
written before the model was changed to `claude-haiku-4-5-20251001` on cost grounds, and
it was never revisited. It was caught at CH-11 by a session that checked the claim against
the artifacts rather than against this file, raised as `QUESTIONS.md` **Q35**, and
corrected here rather than quietly. The generating artifact is
`docs/evidence/runs/cost_ledger.csv`: of its 2,107 rows, every evaluation-arm row — `A1`,
`A1-iter1`, `A1-minus-tool`, `B0`, `B0-agent`, `B0-agent-currenttext`, `B0prime` — carries
`claude-haiku-4-5-20251001`, and the only `claude-sonnet-5` rows are the 80 rows of the
withdrawn sensitivity subset (`B0-sonnet`, `B0-agent-sonnet`) plus 4 rows of
`probe-model-id`. Re-derivable at `docs/evidence/ch11c-sweep/`.

**A second correction, to the first one, same day.** The corrected row above first read *"every evaluation arm, temperature 0"*. **That qualifier was also false, and CH-11c wrote it.** `B0prime` ran at **temperature 1.0** — `docs/evidence/ch06-a1/B0prime-rep1.json` records `temperature: 1.0`, and `src/arms.py` defaults the arm to 1.0 because best-of-3 self-consistency at 0 is a no-op (`QUESTIONS.md` Q22) — and the withdrawn sonnet subset ran at the model default because sonnet rejects the parameter. It was caught within the hour by this chunk's own adversarial sweep (`docs/evidence/ch11c-sweep/ch11c-agent-sweep.md`, finding ranked 2 of 9) and is recorded rather than quietly amended. **A session correcting a false claim about the model introduced a new false claim about the temperature in the same sentence** — which is the thesis of this repository applied to its own corrections.

Prior art cited rather than reimplemented: **Prior et al., NLLP@ACL 2025** (amendatory instruction execution) and **`cfpb/regulations-parser`**. Neither is used as code; both are named in `CONTEXT.md` §12.

---

## 6. What is deliberately excluded from this repository

Not everything on the build machine is shipped, and the reasons matter:

- **micro1's own materials** — the problem PDF, the brand video, page assets. They are the organiser's copyright. Under the Participation Agreement micro1 owns submissions; republishing their own material back to them serves nobody.
- **The operator's personal data** — résumé, contact details, portfolio dumps. Ground rule 08.
- **Research scratch directories** from the ideation sessions (~300 MB of intermediate data). Superseded; the conclusions are in `context/`, the measurements that mattered are in `docs/evidence/`.
- **Third-party repository content** whose licences forbid redistribution.

`.gitignore` is the enforcement, and `git ls-files` is the proof.
