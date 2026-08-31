# REPRODUCE.md — from a clean machine to the published numbers

Two tiers. **Tier 1 costs nothing, needs no key and runs with the network off.** It is
the one a judge should take. Tier 2 re-runs the model arms live and costs money.

**Tier 1 below was run from a clean environment before it was written down** — a fresh
clone, a fresh virtual environment, the network proved unreachable. **Tier 2 was not**,
and could not be: CH-11 was forbidden model calls, so every Tier-2 figure is copied from
the ledger of the runs that already happened rather than from a fresh one. Where a figure
appears, its committed artifact is named.

---

## Before either tier

| | |
|---|---|
| **Python** | **3.12.2** (CPython). Built and rehearsed on it; `docs/evidence/ch14-clean-clone/rehearsal.txt`. |
| **OS** | built on Windows 11. The code is pure Python with no platform calls; the suite and the replay were run on Windows. Nothing is asserted about macOS or Linux because nothing was measured there. |
| **Dependencies** | `pytest==9.1.1`, and nothing else. `requirements.txt` says why. |
| **Disk** | the tracked tree measured **61,696,512 B = 61.70 MB** (`docs/evidence/ch14-size/inventory.md`); the uploaded zip measured **10,613,737 B = 10.61 MB** (`docs/evidence/ch14-clean-clone/rehearsal.txt` — `inventory.md` records 10.18 MB from an earlier commit). Tier 2 adds the raw XML under `data/raw/`; see the last section for what that is and how big. |
| **Network** | Tier 1: none. Tier 2: `api.anthropic.com`, and `www.govinfo.gov` if you rebuild `data/raw/`. |

```
git clone https://github.com/chinmoypaul8897/instruction-that-wont-execute
cd instruction-that-wont-execute
python -m venv .venv
.venv/Scripts/activate            # Windows;  source .venv/bin/activate  elsewhere
python -m pip install -r requirements.txt
```

---

# Tier 1 — offline replay · **USD 0.00 · no API key · network off**

This does not re-run a single model call. It verifies the frozen corpus against its
SHA-256 manifest, then **rescores the committed run artifacts** and regenerates the
result files from them. If the scorer is honest and the artifacts are what they claim
to be, the regenerated files come back byte-identical to the committed ones.

```
python refetch.py --verify-only
python docs/evidence/checkpoint/analyse_checkpoint.py
python docs/evidence/ch06-a1/analyse_a1.py
python -m pytest -q
```

## What you should see — the exact strings

**1. `python refetch.py --verify-only`** — no network at all. It prints one `OK` line
per frozen file and a count for each of the five freezes — `4/4`, `6/6`, `2/2`, `3/3`,
`3/3`, eighteen files in total — and ends:

```
REFETCH OK - every frozen artefact reproduces from govinfo.
```

**2. `analyse_checkpoint.py`** — the baseline comparison, `docs/evidence/checkpoint/`.

```
gap       +18.3 pp
McNemar   p = 0.0059
BRANCH: GREEN
```

That is **B0 0.4756 → B0-agent 0.6585**, n = 82, exact two-sided McNemar, b = 21,
c = 6.

**3. `analyse_a1.py`** — the agent against every baseline, `docs/evidence/ch06-a1/`.

```
A1  vs  B0-agent 0.6585
    accuracy 0.7195   gap +6.1 pp
    McNemar exact two-sided p = 0.4244   (b=15 c=10 discordant=25)
TOTAL                                                11.6323
```

**`p = 0.4244` is not significant.** The script does not print the word — it prints the
four-clause verdict against `GOOD.md` §4's frozen success criterion, and all four read
`NOT MET`, including `McNemar p < 0.05            p = 0.4244`.

**4. `python -m pytest -q`**

```
316 passed, 26 skipped
```

The 26 skips are the tests that need `data/raw/` — **1.44 GB** of source XML that is
git-ignored. They skip rather than fail, and `refetch.py` brings them back. **From the
extracted submission zip the count is `314 passed, 28 skipped`** — two more, both in
`tests/test_size_guard.py`, which inspects the live repository and carries its own
reason string: *"not a git work tree (an extracted submission zip is a plain
directory)"*. Both counts are recorded in
`docs/evidence/ch14-clean-clone/rehearsal.txt`.

> **Corrected at CH-12.** The sentence above read **824 MB** until 2026-08-31. Measured,
> `data/raw/` holds **1,443,366,993 B = 1.44 GB** across 234 files; **824 MB is the
> `ecfr/` titles alone** (824,298,523 B), and the whole tree is **1.75×** that. **The
> right figure was already in this file** — the per-subdirectory table further down,
> under *"`data/`, `data/raw/`, and rebuilding the corpus"*, has said 1.44 GB all along
> and explains the 824 MB in the next paragraph. So this document contradicted itself,
> and **the wrong half is the one that got quoted onward** into `SUBMISSION.md`. Neither
> figure was deleted; both are here with what each measures. Generating script and
> committed output: `docs/evidence/ch12/measure_corpus.py` →
> `docs/evidence/ch12/corpus-size.txt`.
>
> The same measurement clears a **third** number that looks like a fourth
> disagreement and is not. `CONTEXT.md` §8 says *"49 titles, 824,289,052 B"*, which is
> 9,471 B short of `data/raw/ecfr/`. Traced: `data/raw/ecfr/` holds **50** files — the
> 49 title XMLs, which come to **824,289,052 B and match `CONTEXT.md` to the byte**,
> plus `_govinfo_index.json` at exactly **9,471 B**. **Reconciled, not rounded.**

## The fifth command, if you want the model-free baseline too

```
python docs/evidence/ch04-scorer/run_bscript.py
```

```
held-out CV accuracy         0.6098
p-value                    0.2355
```

Committed outputs: `docs/evidence/ch04-scorer/bscript-run.txt` and `bscript-result.json`.

That is `CONTEXT.md` §4's type-3 baseline: the best threshold on any of the cheap
features, 5-fold cross-validation grouped by FR document, scored inside a within-pair
permutation null. §4 specifies *"~26 cheap features"*; the shipped `features()` returns
**30**, and `bscript-run.txt` prints the divergence in its own first lines rather than
leaving it to be noticed. **It is separated out because it takes about 2½ minutes** — the
whole procedure, feature selection included, is re-run on each of 2,000 permutation
draws, so the p-value prices in the search over all 30 features.

## Runtime and what has been verified

**Under half a minute for the four commands above.** Measured twice at CH-11, each time
in a fresh `git clone` and a fresh virtual environment built from `requirements.txt`
alone, with the network proved unreachable first by attempting `govinfo.gov` through a
closed port and requiring the attempt to fail:

| | run 1 | run 2 |
|---|---:|---:|
| `refetch.py --verify-only` | 0.60 s | 1.75 s |
| `analyse_checkpoint.py` | 0.39 s | 1.61 s |
| `analyse_a1.py` | 0.89 s | 1.34 s |
| `pytest -q` | 12.54 s | 21.15 s |
| **total** | **14.42 s** | **25.84 s** |

**Both numbers are published because a single one would be a claim about your machine
rather than a measurement of ours.** Same repository, same interpreter, same commit
family; the spread is load on the build machine. `run_bscript.py` adds about 2½ minutes
(143.13 s measured), and its two committed outputs come back byte-identical as well.
Both runs matched all seven headline strings and all four regenerated result files.

The working is in `PROGRESS.md`'s CH-11 entry. It is not under `docs/evidence/` because
CH-11's scope fence makes that directory read-only; `QUESTIONS.md` Q30 records that.

**This path was rehearsed from the extracted zip, not just from a clone.** CH-14a
unpacked `git archive --format=zip HEAD` into a plain directory — what a judge actually
opens — and replayed it offline on a fresh interpreter: **ALL PASS, 8 of 8**, manifests
18/18, every headline string matched literally, and all four regenerated result files
byte-identical to the committed ones.
`docs/evidence/ch14-clean-clone/rehearsal.txt`.

## If a number comes out different

Report it. The regenerated result files are compared by SHA-256 in the rehearsal for
exactly this reason, and a mismatch is a finding about this project, not a bug in your
setup. `refetch.py`'s mismatch report prints both sides rather than exiting on the
first difference.

---

# Tier 2 — live re-run · **needs a key · costs money**

Only do this if you want to re-run the model arms. Tier 1 already proves the published
numbers follow from the committed artifacts; Tier 2 asks the separate question of
whether the artifacts reproduce.

## Setup

```
echo ANTHROPIC_API_KEY=sk-ant-... > .env       # git-ignored, never committed
```

`src/apiclient.py` reads `.env` and hands the value to its caller. It never prints it,
never logs it, and never writes it to a trajectory (hard rule 12). `src/runlog.py`
refuses to start a run that would take total spend past **USD 18.00**.

| | |
|---|---|
| **Model** | **`claude-haiku-4-5-20251001`** — dated, never the floating alias. |
| **Temperature** | **0** on every arm **except `B0prime`**, which runs at **1.0**. Self-consistency at temperature 0 is a no-op — three deterministic samples are the same sample — so the control could not exist at 0. `B0prime`@0 **is** B0-agent and is reported using the 0.6585 it already has. The deviation from `GOOD.md` §8 is declared in `src/arms.py::run_b0prime`'s own docstring and ruled in `QUESTIONS.md` **Q22**. It is the only arm in the primary matrix not at temperature 0. |
| **Delivery** | standard, not batch. Recorded per ledger row, so the doubled unit price is visible. |
| **Retries** | 3, on 429/5xx and transport errors only. A 400 or a 404 is a real answer and is not retried. |
| **Item order** | sorted by `item_id`, identical for every arm and every rep. |

All of that is fixed in `GOOD.md` §8, committed **before any arm ran**.

## The commands

`src/` is not an installed package, so put it on the path.

```
export PYTHONPATH=src           # Windows PowerShell:  $env:PYTHONPATH = "src"
```

**The baselines** — `agents/B0.md`, `agents/B0-agent.md`:

```
python -m arms run --arm B0 --arm B0-agent --reps 3
python -m arms b0prime --reps 1          # the repeated-sampling control, t = 1.0
```

**The solution and its ablations** — `agents/A1.md`, `agents/A1-SKILL.md`:

```
python -m a1 run --arm A1 --reps 3
python -m a1 run --arm A1-iter1 --reps 1        # tool, no procedure
python -m a1 run --arm A1-minus-tool --reps 1   # procedure, no tool
```

`--arm A1-minus-skill` is **refused on purpose**: it is the same configuration as
`A1-iter1`, that identity was declared in `CHANGELOG.md` before the runs, and billing
it twice would invite a reader to treat one arm as two pieces of evidence.

Smoke-test first if you like — `python -m a1 run --arm A1 --limit 3` runs the first
three items.

**The evaluation** — no model, no network, and the same scripts Tier 1 runs:

```
python docs/evidence/checkpoint/analyse_checkpoint.py
python docs/evidence/ch06-a1/analyse_a1.py
```

## Measured cost and runtime — not an estimate

From `docs/evidence/runs/cost_ledger.csv`, printed by `analyse_a1.py`:

| arm | calls | input tok | output tok | USD | wall s |
|---|---:|---:|---:|---:|---:|
| A1 (3 reps) | 249 | 4,006,662 | 265,354 | **5.3334** | 2516.1 |
| A1-iter1 | 82 | 944,767 | 67,840 | 1.2840 | 763.9 |
| A1-minus-tool | 164 | 1,158,758 | 51,746 | 1.4175 | 665.0 |
| B0 (3 reps) | 474 | 184,275 | 3,952 | 0.2040 | 876.4 |
| B0-agent (3 reps) | 474 | 1,453,863 | 3,816 | 1.4729 | 475.2 |
| B0prime | 492 | 1,377,402 | 4,288 | 1.3988 | 505.1 |
| B0-agent-currenttext *(removed experiment 1)* | 82 | 259,727 | 656 | 0.2630 | 81.5 |
| B0-agent-sonnet *(withdrawn)* | 40 | 100,784 | 584 | 0.2074 | 70.0 |
| B0-sonnet *(withdrawn)* | 40 | 22,936 | 500 | 0.0509 | 61.7 |
| probe-model-id | 10 | 102 | 28 | 0.0003 | 11.7 |
| **TOTAL API SPEND** | | | | **11.6323** | **6026.7** |

**The six arms in the primary matrix cost USD 11.11 and 5,802 seconds of measured
wall-clock — about 97 minutes.** Every row above is USD 11.6323 and 6,027 seconds,
against a USD 18.00 ceiling enforced in code. Elapsed time was less than the sum,
because some arms ran concurrently — which is how two of them came to be **run twice**,
wasting roughly **USD 1.43**. That duplication is disclosed in full at `QUESTIONS.md`
Q26, both runs' figures are published side by side, and no headline number moves
between them.

**You will not get byte-identical predictions, and that is measured rather than
excused.** At temperature 0 the three `B0-agent` reps were identical on all 82 items.
The three `A1` reps were not — per-rep accuracy 0.7195 / 0.6707 / 0.7195, up to 12 of
82 items differing between a pair of reps. A1 runs an agentic loop, so each turn is
sampled from a context the previous turn shaped, and determinism at temperature 0 is a
property of a single call rather than of a multi-turn agent. The full working is in
`docs/evidence/ch06-a1/a1-result.txt` under *rep-to-rep stability*.

---

# `data/`, `data/raw/`, and rebuilding the corpus

**`data/` ships extracted artifacts only, and it is sealed.** **Five** freezes, named in
`refetch.py`'s own `FREEZES` list — `CH-01` the EDNOTE harvest, `CH-02` the AMDPAR
attribution, `CH-03/1a` the v1.1 re-measurement, `CH-03` the eval set, and
`CH-03/restricted` the alternative eval set — each with a SHA-256 manifest.
`refetch.py --verify-only` checks all 18 files with no network.

**`data/raw/` is git-ignored and is not in the repository.** Measured on the build
machine at CH-11, transcribed into `PROGRESS.md`'s CH-11 entry:

| under `data/raw/` | files | bytes |
|---|---:|---:|
| `ecfr/` — 49 title XMLs plus the govinfo index | 50 | 824,298,523 |
| `cfr/` — annual-edition volumes the point-in-time text is cut from | 110 | 349,679,334 |
| `fr/` — the Federal Register issues the instructions come from | 74 | 269,389,136 |
| **total** | **234** | **1,443,366,993 = 1.44 GB** |

The **824 MB** figure quoted elsewhere in this project is the **eCFR titles alone** —
`CONTEXT.md` §8's *"49 titles, 824,289,052 B"* — not the whole raw tree. Either way it is
far past the 50 MB submission cap, so it is rebuilt rather than shipped.

```
python refetch.py                        # fetch + extract + verify   (needs network)
python refetch.py --title 7 --title 11   # just the two titles the goldens cite
python refetch.py --verify-only          # verify the freeze            (no network)
```

**One honest caveat about a full refetch.** The eCFR is a live document. Every title
XML carries a last-modified date that moves, and the manifest records what govinfo
served when this project measured it. **A hash mismatch after a refetch is a real event
to report, not a bug to paper over** — upstream changed. `manifest.json` carries the
govinfo last-modified stamps so a mismatch can be dated.

## Where the data comes from, and where it does not

| Source | Status |
|---|---|
| `https://www.govinfo.gov/bulkdata/{ECFR,CFR,FR}` | **200, no key needed. The sole harvest channel.** |
| `www.ecfr.gov` | **HTTP 403** from the build machine, verified 2026-08-30 02:17 UTC |
| `www.federalregister.gov` | **HTTP 403**, same measurement |

Sustained automated traffic got the build machine blocked on the latter two. They are
not used, and `CLAUDE.md` makes not working around them binding. Everything here comes
from govinfo, which is public domain — `THIRD-PARTY.md` §3.

---

# What Tier 1 does not prove

It proves the published numbers follow from the committed run artifacts, deterministically
and offline. It does not prove the model would produce those artifacts again — Tier 2 is
that question, and its answer for A1 is *not exactly*, quantified above. And it does not
make the result significant: **A1 − B0-agent is +6.1 pp at p = 0.4244 on n = 82, which
is not significant, and the pre-registered success criterion is not met on any of its
four clauses.** The README leads with that.
