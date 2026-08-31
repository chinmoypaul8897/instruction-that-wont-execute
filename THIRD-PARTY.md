# THIRD-PARTY.md — everything here that someone else wrote

This project's own code is MIT (`LICENSE`). This file lists everything it stands on
and what each thing is licensed under. Where a licence is quoted below it was read
out of the installed package's own metadata in the CH-11 verification venv, not
recalled — hard rule 15.

---

## 1. Runtime dependencies — one, and it is only needed for the tests

| Package | Version | Licence | Read from |
|---|---|---|---|
| **pytest** | **9.1.1** | **MIT** | `pytest-9.1.1.dist-info/METADATA` → `License-Expression: MIT` |

That is the whole direct dependency set. It is derived from the imports, not from a
`pip freeze` — every top-level `import` across `src/`, `tests/`, `tools/`,
`refetch.py`, `docs/evidence/` and `docs/reviews/` was collected, and one name came
back that is neither the standard library nor a module of this project. See the
comment block in `requirements.txt` for the method.

**There is no HTTP library, no vendor SDK and no scientific stack.**
`src/apiclient.py` calls the Anthropic Messages API through `urllib`. `src/score.py`
computes an exact two-sided McNemar and a clustered bootstrap out of `math.comb`
and a function-local `random`, and imports nothing else. That is a specification requirement, not thrift:
`CONTEXT.md` §7 fixes the scorer as *"stdlib only, no model, no network"*, and hard
rule 8 makes purity a property the reviewer checks.

**Tier 1 — the offline replay — needs nothing from this table.** `refetch.py
--verify-only`, `analyse_checkpoint.py` and `analyse_a1.py` are stdlib. Only the
suite needs pytest.

### Transitive, resolved by pip for pytest 9.1.1

Recorded because a reader who wants a fully pinned environment should be able to pin
it, and because a future resolution difference should be visible rather than silent.
This project imports none of these.

| Package | Version | Licence | Read from |
|---|---|---|---|
| colorama | 0.4.6 | BSD 3-clause | its own `licenses/LICENSE.txt`, three clauses |
| iniconfig | 2.3.0 | MIT | `License-Expression: MIT` |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | `License-Expression` |
| pluggy | 1.6.0 | MIT | `License: MIT` |
| Pygments | 2.21.0 | BSD-2-Clause | `License-Expression` |

## 2. The interpreter

**CPython 3.12.2**, under the **PSF License Agreement**. The standard library is the
project's real dependency — `xml.etree`, `urllib`, `json`, `csv`, `decimal`,
`fractions`, `hashlib`, `re`, `statistics`.

## 3. The corpus — US Government work, public domain

| Source | URL | What it gives |
|---|---|---|
| eCFR bulk XML | `https://www.govinfo.gov/bulkdata/ECFR` | `<EDNOTE>` elements — **the gold labels** |
| CFR annual editions | `https://www.govinfo.gov/bulkdata/CFR` | point-in-time section text |
| Federal Register bulk | `https://www.govinfo.gov/bulkdata/FR` | `<AMDPAR>` elements — **the instructions** |

Everything under `data/` is derived from those three. They are works of the United
States Government, and under **17 U.S.C. §105** a work prepared by an officer or
employee of the US Government as part of that person's official duties carries no
copyright protection in the United States. **The corpus is in the public domain.** It
is redistributed here with a SHA-256 manifest per freeze and `refetch.py` to rebuild
it from source.

**govinfo is the sole harvest channel, and that is a measured constraint, not a
preference.** `www.ecfr.gov` and `www.federalregister.gov` return **HTTP 403** from
the build machine — verified 2026-08-30 02:17 UTC, recorded as binding in
`CLAUDE.md`, and not worked around. govinfo returns 200 and needs no key.

The raw XML is **not** in this repository. `data/raw/` is git-ignored and `refetch.py`
rebuilds it. Measured on the build machine at CH-11 and transcribed into `PROGRESS.md`:
**1,443,366,993 B across 234 files** — 824,298,523 B of eCFR titles, 349,679,334 B of CFR
annual-edition volumes and 269,389,136 B of Federal Register issues. The **824 MB** figure
quoted elsewhere in this project is `CONTEXT.md` §8's *"49 titles, 824,289,052 B"*, which
is the eCFR portion alone. See `REPRODUCE.md`.

## 4. The model

**`claude-haiku-4-5-20251001`** (Anthropic), used under Anthropic's commercial terms,
for every evaluation arm. Dated, never the floating alias: a reproducibility claim
pinned by a moving alias is not pinned (`GOOD.md` §8, `QUESTIONS.md` Q1). Temperature
0 on every arm in the primary comparison. Total measured API spend **USD 11.6323**
against a USD 18.00 ceiling enforced in `src/runlog.py` —
`docs/evidence/runs/cost_ledger.csv`.

`claude-sonnet-5` calls exist in the ledger. They belong to the **model-sensitivity
check, which is WITHDRAWN** as a harness defect: 13 of 20 `B0-agent-sonnet`
predictions came back empty. No sensitivity claim is made anywhere in this
submission. The architect's ruling is transcribed verbatim in `QUESTIONS.md` Q19.

## 5. The coding agents

**Claude Code** running **`claude-opus-5` (1M context)**, under Anthropic's
commercial terms, wrote this repository under human direction. Every session, what it
did, its token counts and its imputed cost are in **`AI-USE.md`**; the transcripts
are in **`docs/trajectories/build/`**; the prompt that opened each session is in **`prompts/`**,
committed verbatim as issued — with **one exception, named rather than glossed:
`prompts/CH-11.md`, the prompt for the session that wrote this file, is on disk and
untracked.** CH-11's own scope fence makes `prompts/` read-only, so the session that
received it could not commit it. One `git add` closes the gap; `QUESTIONS.md` Q30 records
it. Nothing about how this was built is
concealed — the brief requires agent use and scores how well it was directed.

## 6. Prior art — cited, not reimplemented

Neither of these is used as code. Both are named in `CONTEXT.md` §12, and they are
named because not citing known prior art on a submission staked on integrity is an
unforced error and is one search away for a judge.

- **Prior et al., NLLP@ACL 2025** — amendatory instruction execution as a task. Their
  axis is *executing* the amendment. Ours is *predicting the failure before
  publication and localising it*, against NARA's own published editorial notes as the
  label.
- **`cfpb/regulations-parser`** — an existing CFR amendment parser, and a good one.
  `src/attribute_amdpars.py` is not a competitor to it and does not claim to be; it
  implements the AMDPAR carry-forward rule written out in `CONTEXT.md` §8, and its
  completeness against that specification is **0.5080** spec-literal and **0.6643**
  extended — `docs/evidence/ch02-attributor/ch02-attributor-run.txt` — published as a
  **failed** gate rather than a feature.
- **ATLAS, arXiv 2509.18400** — HTS classification from CBP CROSS rulings. Unrelated
  domain. It is listed because it killed a predecessor project of ours, and the
  record of that kill is in `context/07-KILL-TEST.md`.

## 7. Excluded on purpose

`PROVENANCE.md` §6 has the full list and the reasons. In short: micro1's own problem
materials are their copyright and are not republished; the operator's personal data is
out under ground rule 08; and the pre-competition research scratch is superseded.
`.gitignore` is the enforcement and `git ls-files` is the proof.

**What this file audited:** six installed packages, the interpreter, the govinfo corpus,
the model, the coding agent, and three prior-art citations. It is not a scan of every byte
in the repository. If something here is redistributed against its licence, it is an error,
and naming it will get it removed.
