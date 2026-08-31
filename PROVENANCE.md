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

## 2. Produced before kickoff — research only, no project code

**2026-08-27, approximately 21:45 UTC — seventeen hours before kickoff.**

- `scraper/` — Playwright recon scripts written to read the **public** HackerEarth challenge page.
- `context/00-MASTER-CONTEXT.md` — an extraction of that public page, including content that was only present inside images (the rubric weights, the timeline, the registration deadline).

**Why this is not problem-specific work:** the problem did not exist yet. The brief was released at kickoff. Nothing produced before 15:00 UTC on 2026-08-28 could have addressed the actual task, and nothing in `scraper/` is part of the submitted system — it is excluded from the repository by `.gitignore`.

**Ground rule 01 expressly permits this:** *"You are welcome to build with tools and components you already know."* The tooling used was Playwright, cheerio and sharp — public libraries, used under their own licences.

---

## 3. Produced after kickoff, before coding — the decision record

**2026-08-29 to 2026-08-30.** All of this is the contestant's own work, produced with coding agents, and is shipped because it is evidence of method rather than reused code:

| Artifact | What it is |
|---|---|
| `context/03-IDEA-REVIEW-VERDICT.md` | 15 agents attacking the first candidate. It died. |
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

The `nistula-assistance-` result is cited in this project's README as the *motivating hypothesis* for why a green test suite is insufficient evidence — never as a result of this project. No code, data, or artifact from either repository is reused here.

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
| Anthropic API — `claude-haiku-4-5-20251001` | commercial, per terms | every evaluation arm, temperature 0 |
| Anthropic API — `claude-sonnet-5` | commercial, per terms | the model-sensitivity subset only, which was **WITHDRAWN** as a harness defect — `QUESTIONS.md` Q19. No claim in this submission rests on it. Also the four rows of the model-id probe. |
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

Prior art cited rather than reimplemented: **Prior et al., NLLP@ACL 2025** (amendatory instruction execution) and **`cfpb/regulations-parser`**. Neither is used as code; both are named in `CONTEXT.md` §12.

---

## 6. What is deliberately excluded from this repository

Not everything on the build machine is shipped, and the reasons matter:

- **micro1's own materials** — the problem PDF, the brand video, page assets. They are the organiser's copyright. Under the Participation Agreement micro1 owns submissions; republishing their own material back to them serves nobody.
- **The operator's personal data** — résumé, contact details, portfolio dumps. Ground rule 08.
- **Research scratch directories** from the ideation sessions (~300 MB of intermediate data). Superseded; the conclusions are in `context/`, the measurements that mattered are in `docs/evidence/`.
- **Third-party repository content** whose licences forbid redistribution.

`.gitignore` is the enforcement, and `git ls-files` is the proof.
