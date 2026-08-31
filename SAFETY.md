# SAFETY.md — what this system does, what it refuses to do, and who decides

Ground rules 04 and 05 of the brief ask for human approval before an action happens,
and for a qualified human reviewer inside any system that could significantly affect
someone. This file answers both concretely. Where it states a number, the number comes
from a committed artifact and the path is given.

---

## 1. The system takes no consequential action

There is no action to approve, because the system performs none.

A run reads two things — a Federal Register final rule's amendatory instructions, and
the CFR text as it stood on the publication date — and writes one JSON record per
`(rule, section)` item. That record is the shape in `CONTEXT.md` §5: a verdict, a
failing designation, a failure class, and the full per-instruction resolution trace it
was derived from. The record is written to disk. That is the end of it.

It does not file anything. It does not submit to the Office of the Federal Register,
touch a docket, e-mail an agency, or write to any system outside this repository. Neither
the scorer nor the resolver reaches the network or reads the clock (`CLAUDE.md` hard rule
8). The only components that reach the network at all are `src/apiclient.py`, which posts
to the Anthropic Messages API, and `refetch.py`, which downloads public XML from govinfo.

**Two qualifications, because hard rule 8 also says "no randomness" and one of them is
not literally true.** For the resolver, purity is asserted by a test:
`tests/test_cfr_resolve.py::test_RF_the_resolver_fetches_nothing` reads
`src/cfr_resolve.py`'s own source and fails if it contains `urllib`, `requests`, `socket`,
`http.client`, `datetime.now`, `time.time` or `random.`. **There is no equivalent
source-level purity test for `src/score.py`**, and the scorer does use randomness —
`src/score.py:193` `import random`, `:201` `rng = random.Random(seed)`, inside the
clustered bootstrap. The seed is a declared parameter echoed into the result, so the
interval is byte-reproducible under hard rule 9, but `score.py`'s own docstring still says
"no randomness" and that is **open finding F11 in `docs/reviews/REVIEW_CH-04.md`**, not a
settled question.

**The output is an input to a drafter's judgement.** `CONTEXT.md` §1 lists that as a
non-goal in the specification itself: *"Not a legal-advice tool. Output is an input to
a drafter's judgement, never a filing."*

`docs/worksheet/worksheet.html` renders one item's trace for a human to read. It ships
today as a shell against a synthetic fixture — CH-10, the chunk that fills it from
real runs, is `todo` in `STATUS.md`, and that is stated here rather than implied away.

## 2. The intended reviewer is named

**A qualified regulations drafter, or an Office of the Federal Register liaison,
clearing a final rule for publication.** `CONTEXT.md` §2 names that person as the user
and this file names them as the decider. They already own the decision the system
comments on: *will this amendatory instruction codify?* Nothing here moves that
decision anywhere else.

The exposure is real, which is why the reviewer matters. If an instruction is
defective, OFR cannot incorporate it, the CFR text never changes, and NARA publishes a
permanent, citable editorial note recording that the agency's rule did not take effect
as written. The remedy is a correcting document and another Federal Register cycle. A
wrong prediction from this system, acted on without a drafter, would either send
someone chasing a defect that is not there or let a real one through.

## 3. The human checkpoint fires on 16 of 82 items, and code decides when

Evidence: `docs/evidence/ch06-a1/a1-result.txt` — *"items routed to the HUMAN
CHECKPOINT: 16 of 82"*. Every routed item carries a `human_checkpoint` record in its
trajectory under `docs/trajectories/arms/`.

**The trigger conditions are computed in code from the resolution trace. The model is
never asked whether it wants help.** `src/a1.py::human_checkpoint_reasons` — an agent
that decided for itself when to escalate would escalate whenever it felt unsure, which
is a confidence report and not a checkpoint. The three conditions:

- **C1** — a quoted anchor is absent at every declared normalisation level while the
  target designation exists. The two halves of the instruction disagree about whether
  it can execute.
- **C2** — both halves were asked and came back opposite: `found` and
  `designation_exists` contradict each other.
- **C3** — one designation is touched by two instructions, so instruction *k* changes
  what instruction *k+1* will find. Modelling that is capability 3, the ordered-state
  ledger, **not built** under ruling R-01. **C3's escalation text names the ruling that
  removed the capability.** The agent refuses to model execution order rather than
  pretending to.

C1 carries a bug's worth of history that is worth stating. Without the clause requiring
that an anchor was actually *asked* for, C1 fired on every instruction naming a
paragraph that exists. **A checkpoint that fires on everything is not a checkpoint.**
Golden C0 catches it.

## 4. What the system gets wrong, stated where a user will see it

Both pre-registered guards are reported per arm and neither threshold was moved
(`docs/evidence/ch06-a1/a1-result.txt`):

| A1 | measured | guard | verdict |
|---|---|---|---|
| false-defect rate — `WILL_FAIL` called on a clean section | **0.2195** | ≤ 0.25 | **PASS** |
| missed-defect rate — `WILL_EXECUTE` called on a defective one | **0.3415** | ≤ 0.25 | **FAIL** |

**A1 misses about a third of real defects, and every arm measured fails that guard.** A
drafter who treats a `WILL_EXECUTE` from this system as clearance is relying on something
that has been measured wrong roughly once in three on defective sections. A1's 0.3415 is
the lowest missed-defect rate any arm reached, which makes it the best of six and still a
failed guard; the README says both of those in the same sentence and so does this file.

Two more, for the same reason:

- **`cfr_resolve` has a known one-way defect.** It cannot see a paragraph designation
  written nested under its parent, so it reports *absent* for paragraphs that are
  present — 60 of 128 designations in the eval set, touching 33 of 82 items, **and
  every misfire runs in that one direction** (`QUESTIONS.md` Q21,
  `docs/evidence/ch06-a1/iter1/nested_designation_probe.txt`). On a clean section that
  manufactures a false defect, which is the error direction with the highest cost to
  the user. **It was found because it cost the headline a point, and it was left
  unfixed** for the reasons in Q21. It is published, not repaired quietly.
- **The accuracy headline is withdrawn on our own pre-registered guard.** Attributor
  completeness measured 0.5080 / 0.6643 at CH-02 and 0.5340 under `CONTEXT.md` v1.1,
  against a blocking threshold of 0.90 (`GOOD.md` §3). That withdrawal was recorded
  before any model arm ran.

## 5. Data and secrets

**No personal data is processed.** The corpus is published federal regulatory text —
public domain, 17 U.S.C. §105. Nothing in it is about an identifiable private
individual, and the system builds no profile of anyone.

**The API key lives in `.env`, which is git-ignored and has never been tracked on any
ref** (`CLAUDE.md` hard rule 12). It is never printed, never logged, and never written
to a trajectory: `src/apiclient.py` returns it to its caller and reports nothing about
it but its name. The full-history sweep at CH-14a read **462 text blobs across 84
commits** and returned **PASS, 0 findings**, with every zero-occurrence rule printed as
a zero — `docs/evidence/secret-scan/scan.txt`, which also lists its own six
limitations, including the absence of entropy analysis.

**Spend is capped in code, not by intention.** `src/runlog.py` refuses to start a run
that would cross USD 18.00. Measured total: **USD 11.6323**
(`docs/evidence/runs/cost_ledger.csv`).

## 6. What would have to be true before this ran on live rules

Stated plainly, because the honest answer is *more than has been done*.

The missed-defect guard would have to be met rather than failed. The attributor
completeness gate would have to clear 0.90. `cfr_resolve`'s nested-designation defect
would have to be fixed — as a pre-registered experiment with its own prediction, not as
a quiet correction. The evaluation would need an *n* that clears the pre-registered 84;
at 82 the gap between A1 and the strongest baseline is **not significant**
(p = 0.4244). And CH-03 and CH-04 would have to pass the review gates they currently
fail.

None of that is hidden in a footnote here. It is in the README's LIMITATIONS section
and in `STATUS.md`, chunk by chunk.
