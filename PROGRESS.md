# PROGRESS.md — session journal

**Newest entry on top.** This file is the source of the Improvement Changelog.
Chat history is not a record; if it matters it lives here.

Fixed template per entry: **scope · files · tests · decisions · questions · gate ·
status-ledger · state-for-next-session.**

When sessions run in parallel (Phase 3 only), a build session writes
`docs/progress/<CHUNK-ID>.md` instead and the architect folds it in here.

---

## SPEC-FIX-2 · 2026-08-31 · BUILD (spec-edit scope) · Claude Code, `claude-opus-5` · GATE: none · **APPLIED**

### Scope
Apply the architect's ruling on `QUESTIONS.md` Q11 — which **accepted SPEC-FIX-1's refusal
in full** — to `CONTEXT.md`, and clear Q13's housekeeping. *"You decide nothing."* The
prompt gave the ruling verbatim and fenced everything else as a STOP.

**`CONTEXT.md` is now v1.1. No number moved. Nothing was re-run.** The attributor was not
executed, `data/`, `src/` and `tests/` were never opened, and every figure written into the
spec was already committed before this session started.

### The shape of the ruling, which is the point of the chunk

The architect proposed a metric change that would have turned a failure into a pass.
SPEC-FIX-1 refused it on a sabotage control it built itself. **This chunk does the opposite
in three places on purpose:**

| | change | effect on the number |
|---|---|---|
| 1 | §8 **records the failed gate** and publishes it — 0.5080 / 0.6643 against 0.90 | none; it documents a failure |
| 2 | the detector takes the **word form**, **case-sensitively** (Q9, Q12(c)) | would **raise** attribution if re-measured |
| 3 | `current_section` **resets at a `<REGTEXT>` part boundary** (Q10, Q12(a)) | **costs 8.0 points** |

**Change 3 is the load-bearing one.** SPEC-FIX-1's third finding was that the original
proposal took the +22.5-point fix and never mentioned the −8.0-point one CH-02 had already
called *"a one-line change and would be an improvement"*. Adopting only the half that helps
would have repeated the defect in the act of correcting it.

### DID ANY CHANGE MAKE A FAILING NUMBER PASS? **NO** — and it is asserted, not claimed

1. The **gate definition is byte-identical** to v1.0 and appears exactly once; the
   threshold is untouched; the refused metric does not appear in `CONTEXT.md` at all —
   the verifier asserts the string `attribution_completeness` is **absent from the file**.
2. **The gated figure cannot reach the branch boundary even if every change helped.** The
   word-form fix can at most move it from 0.5080 toward 0.6643. **0.6643 < 0.80**, so CH-02
   stays in its pre-registered *"< 0.80 — documented failure"* branch and is nowhere near
   0.90. The part reset moves it **down**; case-sensitivity can only **remove** detections.
3. Nothing was measured, so no figure in the repository could have moved.

### Decisions

- **Class A — none taken.** Every substantive change was specified by the ruling. Where
  the ruling was silent, the answer was a STOP, not a judgement call.
- **Class B — the part-boundary reset was written into step 2 rather than a new step**, so
  the algorithm keeps its five-step numbering and existing references to "§8 step 3" stay
  valid. The reset is a property of `current_section`'s lifecycle, which is what step 2
  declares.
- **Class B — the 8-point cost is stated with its measurement basis.** v1.1 says the
  0.9865 → 0.9066 endpoints were both measured under the case-**in**sensitive detector, so
  the cost under the rule v1.1 actually specifies is itself unmeasured. Without that clause
  §8 would print a precise number for a detector it no longer describes.
- **Class C — `#### ` heading level** for the failure block, one level under §8's `###`.

### What was deliberately NOT done

`§8`'s *"only ~42% of AMDPARs name a section"* is now stale in a **third** way — Q9 already
recorded that it matches neither 25.0% (sign-only) nor 37.4% (case-insensitive extended),
and under v1.1 it matches an unmeasured figure. **It was left alone.** Editing a fourth
number was not specified, and the scope fence says anything not specified is a STOP. Raised
as **Q14** instead. Q10's two spellings stay recorded and unfixed. No metric was added, no
threshold moved, no definition altered.

### Questions

- **Q11 — RULED.** Recorded **verbatim**, committed **first** at `5adab30` before any spec
  edit, and the transcription is asserted byte-identical to its source in
  `prompts/SPEC-FIX-2.md` (now tracked, so the check is reproducible by anyone).
- **Q13 — CLOSED.** All three housekeeping items done; SPEC-FIX-1's original text left
  exactly as written.
- **Q14 — RAISED.** v1.1 specifies a case-sensitive detector, but **every `extended` figure
  in the repository was computed case-INsensitively** — 0.6643, 0.9865, 0.9066, 57/70,
  2,459, 1,086, and the 699 / 573 / 126 decomposition. They are **not reconstructible by
  arithmetic**, so CH-03 must re-measure rather than adjust. Plus the stale "~42%".

### The verifier failed on its first run, and the check was what was wrong

`docs/evidence/spec-fix-2/spec_fix_2_verify.py` asserts, re-runnably, that each change
landed and each replaced line is gone (hard rule 16), that nothing else in `CONTEXT.md`
changed, and that no read-only or protected path was touched. **Its first run reported
FAIL** on *"v1.0 bare `current_section` step 2 — absent"*. The edit was correct; the check
was not — v1.0's step 2 is a strict **prefix** of its v1.1 replacement, so a substring test
can never be satisfied by any correct edit. It was made line-exact, and **the reason is a
comment in the script and a section in `applied.md` rather than a silent deletion**,
because a check quietly adjusted until it turns green is exactly what this project exists
to warn about. **38 checks, all pass, exit 0.**

The script also fixes for itself the CRLF-on-a-`* -text`-repo defect CH-02 and SPEC-FIX-1
both recorded and neither owned — one line reconfiguring stdout to LF.

### A file-hygiene observation, recorded not fixed

**`CONTEXT.md` is the only canonical markdown file in the repository stored with CRLF
line endings** — 331 CRLF, no LF-only lines — while `QUESTIONS.md`, `STATUS.md`,
`PROGRESS.md` and `AI-USE.md` are all LF. `.gitattributes` is `* -text`, so git stores
what it is given and the mixture is invisible to it. This session **matched the existing
CRLF** rather than normalising, because normalising would have produced a 331-line diff on
a file that is LAW in a chunk authorised to change three things. It is written down here so
the next session that edits `CONTEXT.md` does not introduce a mixed-ending file by
accident.

### Economy — the instruction was followed and it worked

The prompt forbade a subagent panel, citing SPEC-FIX-1's own finding that its ten-agent
panel took **55%** of that chunk's budget, voted **4–1 for the wrong answer**, and that
*"a cheaper panel would have bought it too."* **No subagent was run in this chunk.**

**Result: 10.58 M input tokens — the cheapest session in the project by a wide margin**
(previous minimum SPEC-FIX-1's coding session at 19.15 M; CH-01 was 41.09 M).
**It still missed the prompt's stated target of under 5 M, by 2.1×, and that is a miss.**
Attributable causes, largest first: the `CLAUDE.md` read-order duty itself — this chunk's
required reading is `CLAUDE.md`, a 20 KB verdict, five long `QUESTIONS.md` entries,
`CONTEXT.md`, `STATUS.md` and `PROGRESS.md` — re-read as cached context across 99
assistant turns, which is 10.33 M of the 10.58 M; and three self-inflicted retries (two
shell here-documents that mangled escaping, and the verifier's first-run failure). The
first is structural for any session under this constitution and a 5 M target may not be
reachable while the read order stands; the retries were mine.

### Gate
None. This chunk edits a specification under a ruling; it certifies nothing and re-runs
nothing. **CH-02 remains at `built`, in the `< 0.80` documented-failure branch**, and
CH-03 proceeds on the per-document restriction pre-registered before any of this.

### Status ledger
`SPEC-FIX-2 · apply the Q11 ruling · built` — `CONTEXT.md` v1.1, gate stays FAILED and
published, 38 verifier checks pass.

### State for the next session
`CONTEXT.md` **v1.1** is law. **CH-03 must re-measure under the v1.1 detector** — word form
included, matched **case-sensitively**, with `current_section` reset at part boundaries —
and must **publish the new figures beside the old rather than in place of them** (the
`goldens.md` ERRATA convention). The gate outcome will not change: 0.6643 was already
below 0.80 and a stricter detector cannot raise it. Read **Q14** before quoting any
`extended` number.

---

## SPEC-FIX-1 · 2026-08-31 · BUILD (spec-edit scope) · Claude Code, `claude-opus-5` · GATE: none · **REFUSED**

### Scope
Judge whether `prompts/SPEC-FIX-1.md`'s correction to `CONTEXT.md` §8 — replacing the
failing combined completeness definition with a split `attribution_completeness` (gated)
and `parse_completeness` (reported) — is a legitimate spec correction or goalpost-moving
under hard rule 5, and apply it **only if legitimate**. The prompt authorised a refusal in
terms: *"A session that refuses this correction has done its job correctly."*

**Verdict: GOALPOST-MOVING. Nothing in `CONTEXT.md` was edited.** No §2a, no §2b, no §2c,
no v1.1 bump, no §13 change-log row, and §2d's housekeeping left untouched because §2 is
conditioned *"if and only if the verdict is LEGITIMATE."* The attributor was not re-run,
`data/` was read-only, `src/` and `tests/` were never opened.

### The verdict, and the one artefact that decides it

`docs/evidence/spec-fix-1/verdict.md`, committed at **`72b95e1` before anything else in
the chunk**, so the order is provable from git.

§2a asserts of the proposed gate metric: *"It answers the question the gate exists to
answer"* — *"did carry-forward put each instruction on the **right** section?"*
**That is a factual claim, and it is false.** `spec_fix_1_sabotage.py` builds a control
attributor identical to the shipped one except for one line — carry the **first**-named
section of a document forward instead of the **last** — and scores it:

| detector | real | sabotaged | Δ | placed differently |
|---|---:|---:|---:|---:|
| `extended` | **0.9865** | **0.9865** | **0.000000** | **8,417 / 8,634 = 97.5%** |
| `spec_literal` | 0.7613 | 0.7613 | 0.000000 | 6,395 / 6,663 = 96.0% |

The script asserts its replay of §8 reproduces the frozen record with **0 mismatches of
8,752** before drawing the comparison, so the control is a valid one. The result is
structural: an element is attributed iff some section was named at or before it — true of
both rules — so `attributed ÷ total` measures only *where the first citation appears*.

**Stated fairly, because it is the strongest point for §2a:** the metric is not vacuous in
general. It catches the silent-DROP mode that killed the predecessor pilot at 0.46 — a
lead-ins-only extractor scores 0.2503 / 0.3744 and fails hard. It is blind specifically to
the silent-WRONG mode CH-02 found in this corpus (Q9), which is the mode the correction was
written in response to.

### Three findings behind the verdict, each measured here

1. **The pass needs both post-hoc edits.** §2a alone **0.7613 FAIL**; §2c alone **0.6643
   FAIL**; together **0.9865 PASS**. CH-02 gated on `spec_literal`, and the prompt's fact
   table quotes only the `extended` figure without saying so.
2. **Strictly harder metrics were free from already-frozen booleans, and none was taken:**
   attributed AND part-consistent **0.9066** (still passes, margin 8.65 pts → 0.66);
   attributed AND part-consistent AND no rival conflict **0.8579 FAIL**; the per-document
   floor §8 *already mandates* **57/70 = 0.8143 FAIL**.
3. **Golden G1 passes the proposed gate.** The document CH-02 chose *because* it
   demonstrates mis-attribution — Q9 records 20 of its 28 elements pinned to a section they
   do not amend — scores **26/28 = 0.9286, PASS**.

Also weighed: Q9's fix is worth **+22.5 pts** and was adopted, while the part-boundary
reset is worth **−8.0 pts**, was called *"a one-line change and would be an improvement"* by
CH-02, and is not mentioned in the prompt at all.

### What survives the refusal — the diagnosis is right, and it is half the correction

Verified independently rather than taken from the prompt: **0 of 2,913** unparsed elements
carry both an operation and an anchor-or-designation, and only **46 (1.6%)** are recoverable
parser gaps (20 backtick-apostrophe anchors, 1 dotted paragraph path, 25 out-of-vocabulary
verbs such as *"Stay the section indefinitely"*). **Parse failure genuinely is Federal
Register drafting, not our attributor**, so removing it from an attributor's gate is real
specification work and should be re-issued. `QUESTIONS.md` Q11 carries the four-step path
back.

### Class counts — counted, not taken on trust

| class | n | share of the 2,913 unparsed |
|---|---:|---:|
| authority citations | **591** | 0.2029 |
| lead-ins, CFR section named | **548** | 0.1881 |
| whole-section operations | **436** | 0.1497 |
| **the architect's three as named** | **1,575** | **0.5407** |
| residue the architect did not name | 1,338 | 0.4593 |

Read as families (part-level lead-ins, continuation fragments and part-level operations are
the same drafting devices one level out) the account reaches **2,449 = 84.1%**. Four
independent counts — mine plus three panel recounts — land at 54.1 / 55.4 / 58.5 / 59.7%;
the spread is definitional, and every one agrees the residue is large and the residue is
not our bug.

### Decisions
- **Class A, escalated not taken:** the whole correction. Refused and returned to the
  architect with a specified path back (Q11).
- **Class B:** produced `recomputed.md` even under a refusal, because the report block asks
  for it unconditionally and the numbers are evidence *for* the verdict. It states on its
  first line that the definition was not adopted.
- **Class B:** ran an adversarial panel of ten subagents before deciding. Disclosed in
  `AI-USE.md` with per-agent tokens and USD. **It returned 4–1 the other way and was
  overruled**; only its sabotage control survived, and only after being rebuilt here.
- **Class C:** normalised the session-cost output to LF before staging — `ch00_session_cost.py`
  still emits CRLF into a `* -text` repository, the same defect CH-02 logged, and it is
  outside this chunk's fence to fix.

### Questions
- **Q11** — the refusal, the sabotage control, and the four changes that would make the
  correction legitimate. **An architect ruling is wanted.**
- **Q12** — two numbers already in `QUESTIONS.md` overstate the attributor's error: Q10's
  *"every one of those [699] is wrong"* is wrong for **126** of them (they name their own
  section; the `REGTEXT` part tag is what disagrees), and Q9's `detector_disagrees = 2,459`
  is **488** genuine rival-section conflicts plus 1,971 elements `spec_literal` never
  attributed. Plus a new finding: the shipped `extended` detector is **case-insensitive**
  and reads appendix-internal numbering (*"section 1.1"* of Appendix A) as a CFR section.
  Recorded in a new entry, never edited into the old ones.
- **Q13** — §2d's housekeeping is fenced behind the LEGITIMATE verdict, so the uncommitted
  `CONTEXT.md` edit and the untracked `prompts/CH-02.md` and `prompts/SPEC-FIX-1.md` were
  left alone. **One line from the architect unblocks all three.**

### Gate
None. This chunk is not gated — but it is the first in the project whose *whole output is a
refusal*, and the refusal was reached against a 4–1 advisory majority on the strength of a
control the session built and ran itself.

### Status ledger
`STATUS.md` — SPEC-FIX-1 row added above CH-03, state **refused**. CH-02's row is
unchanged: no spec edit was made, so nothing about its gate result moves. It remains
**built**, in the `< 0.80` documented-failure branch.

### State for the next session
`CONTEXT.md` §8 is **exactly as CH-02 found it** — the combined definition still stands and
CH-02 still fails it at 0.5080 / 0.6643. Nothing downstream has been unblocked. **CH-03
must not start until Q11 is ruled on**, because the ruling decides which detector builds the
eval set and therefore which sections the pairs are drawn from. The working tree is dirty in
exactly the way it was found (Q13). Every number quoted anywhere in this entry regenerates
from `docs/evidence/spec-fix-1/`'s four scripts.

---

## CH-02 · 2026-08-30 · BUILD · Claude Code, `claude-opus-5` · GATE: FULL (domain + code)

### Scope
Pull the Federal Register documents cited by CH-01's 85 section-level defect notes from
govinfo FR bulk; extract `<AMDPAR>` elements; attribute every lettered sub-instruction
to its section by carry-forward per `CONTEXT.md` §8; measure completeness globally and
per document against the pre-registered branches; and **measure the count-matched pair
yield**, which `prompts/CH-02.md` calls the project's largest unknown.

No CFR annual editions, no eval set, no pairs built, no scorer, no `GOOD.md` edit, no
change to `src/runlog.py` or `src/harvest_ednotes.py` — all fenced out, none written.
Verified rather than asserted: `git diff --name-only 8e9eb18..HEAD` over `CONTEXT.md`,
`plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `GOOD.md`, `src/runlog.py`,
`src/harvest_ednotes.py`, `tools/`, `.githooks/`, `context/` and `prompts/` returns
**0 files each**.

### The gate number — the attributor is a DOCUMENTED FAILURE, and it is reported

| | `spec_literal` (§8's own regex) | `extended` |
|---|---:|---:|
| **completeness** | **0.5080** (4,446 / 8,752) | **0.6643** (5,814 / 8,752) |
| attribution rate | 0.7613 | **0.9865** |
| parse rate | 0.6672 | 0.6672 |
| unattributable | 2,089 | 118 |

**Both figures are below 0.80, so `plan.md`'s pre-registered `< 0.80` branch fires: the
attributor is a documented failure. It was not tuned to pass.** The `[0.80, 0.90)`
restricted-pool branch was not taken because neither figure reaches 0.80 — and had it
been, the restriction would have left 2 of 70 documents, which would not have supported
an eval set. Evidence: `docs/evidence/ch02-attributor/completeness.md`, generated by
`ch02_attributor.py`, whose stdout ships as `ch02-attributor-run.txt`.

**Where the loss is, and why it is not the predecessor's failure.** Carry-forward
*works*: attribution is 0.9865, and only 118 of 8,752 elements are unattributable. The
loss is entirely in the **parse** half of §8's numerator, and it is structural — an
authority citation carries no operation; a lead-in (*"Amend § 236.2 by:"*) carries its
specifics in its lettered children; a whole-section revision (*"Section 90.601 is
revised to read as follows"*) has no paragraph path and no quoted anchor. All three are
complete, valid instructions that §8's definition scores as incomplete. The predecessor
pilot's 0.46 was an **attribution** failure; this is a **definition** ceiling. The
definition was not rewritten to raise the number.

**The global figure is dominated by five rules.** One document (`2015-01571`, Rural
Development) is **24.9%** of every AMDPAR measured and the top five are **50.1%**. The
per-document median — 0.610 spec-literal, 0.661 extended over 70 documents — is the more
representative statistic and is reported beside the global one rather than instead of it.

### ⭐ The pair yield — the measurement this chunk existed to produce

| | n |
|---|---:|
| defect sections (all 85 resolved) | **85** |
| with ≥ 1 **exact** count-matched sibling | **51** |
| without | 34 |
| … document amends only that section | 4 |
| … siblings exist, none with a matching instruction count | 20 |
| … no AMDPAR attributes to the section at all | 10 |

**YIELD = 0.6000 · PROJECTED PAIRS = 85 × 0.6000 = 51 · target 42 · CLEARS at 1.21×**
(n = 102 against the n ≥ 84 target).

Under **±1** instruction matching the yield is 0.6824 and the pairs 58. **That rule is
reported and NOT ADOPTED.** `CONTEXT.md` §8 makes exact matching non-negotiable —
unmatched, a hardcoded threshold on instruction count beats the agent, and that is how a
predecessor candidate died. The exact rule clears the target on its own, so there was
never a moment where relaxing it was even tempting; the looser figure is published only
so the architect can see the headroom without asking.
`docs/evidence/ch02-attributor/pair-yield.md` itemises all 34 non-pairing sections.

### The exclusion ladder — every rung prints, zeros included

| Rung | | Remaining |
|---|---:|---:|
| section-level defect notes with an FR citation (CH-01) | | **85** |
| minus no readable date | −0 | 85 |
| minus no issue file | −0 | 85 |
| minus volume mismatch | −0 | 85 |
| minus unresolved page | −0 | **85** |

**85 of 85 resolved, into 70 distinct FR documents** (78 distinct citations, because
several notes cite different pages of the same rule). `kept + removed == received` is
asserted before the file is written, and the tally checks **raise** rather than
`assert`, so `python -O` cannot switch them off.

### Goldens committed before the parser, provably
`docs/evidence/ch02-attributor/goldens.md` is commit **`98f1cff`**;
`src/attribute_amdpars.py` arrives later in this chunk. 97 AMDPAR elements across three
FR documents were read by eye from `sed`/`grep`/`awk` output only and hand-attributed
and hand-parsed into `(operation, anchor, designation)` before any code existed — G1
(2020-11897, 28 elements, section named in the *word* form), G2 (2021-02268, 29,
mostly lettered sub-instructions, `CONTEXT.md` §8's own worked example), G3 (2016-23968,
40, two redesignations and nested roman children).

The goldens also pre-registered, before any number existed, seven tokenisation rules
(P1–P7) and the **prediction** that global completeness would land in **[0.65, 0.80)**
and that the `< 0.80` branch would therefore fire. Measured `extended` = **0.6643** —
inside the predicted interval. All four §6 predictions held.

**Golden divergence, recorded not resolved away.** G1's `spec_literal` total was
hand-predicted as 13/28; measured 14/28. The hand enumeration omitted element 3, the one
element in that document naming its section with a `§` and therefore the one
`spec_literal` attributes *correctly*. **The golden was not edited**; ERRATUM E1 was
appended and the test asserts the measured 14 while naming the erratum — the same
discipline CH-01 applied to its G2.

### PROBE FLIP
`docs/evidence/ch02-attributor/ch02_probe_resolution.py` (+ `ch02-probe-resolution.txt`),
and two live tests. Both states shown, exit 2 on missing input:

- **Old rule** (`resolve_page`, contents route first — what the goldens pre-registered):
  79 FR 24198 resolves to FR Doc `2014-08743`, the *Federal Acquisition Circular 2005-73*
  cover document, which has **0 AMDPARs**; 90 FR 52865 resolves to a rule that does not
  amend the cited section; 85 FR 43138 and 87 FR 31688 resolve to **nothing at all**.
- **New rule** (`resolve_citation`): 838 AMDPARs, the right rule, and all four resolved
  to a document that actually amends the cited section.

Cause, measured not guessed: govinfo lists a *circular* in the front-matter contents as
one entry spanning the page range of every rule inside it; and an editorial note's date
is the date the rule was **filed**, not published, drifting a day in *either* direction.

### Files
Created: `src/attribute_amdpars.py` · `tests/test_attribute_amdpars.py` ·
`data/amdpars/` (`amdpars.jsonl` 8,752 records · `documents.json` · `completeness.json` ·
`pair_yield.json` · `citations.json` · `wanted_issues.json` · `manifest.json`) ·
`docs/evidence/ch02-attributor/` (`goldens.md` · `completeness.md` · `pair-yield.md` ·
`ch02_attributor.py` + `ch02-attributor-run.txt` · `ch02_probe_resolution.py` +
`ch02-probe-resolution.txt`).
Edited: `refetch.py` (CH-02 freeze + a bounded two-round fetch/extract for neighbour-day
issues), `QUESTIONS.md` (Q9, Q10), `STATUS.md`, `PROGRESS.md`, `AI-USE.md`.

### Tests
`python -m pytest tests/ -q` → **121 passed, 0 failed, 0 skipped** (61 from CH-00/CH-01,
60 new). Zero skips *because `data/raw/fr` is populated*; **on a clean clone the 19
tests gated on the 272 MB of raw issues stand down and the count is 102 passed /
19 skipped.** Both states are correct and both are reported.

**The Q8 known-positive assertion, applied to this chunk's counter.** A zero AMDPAR count
that means "wrong tag name" looks exactly like a zero that means "nothing there", so
`test_live_parser_amdpar_count_equals_a_plain_text_sweep` asserts, on four issues, that
**parser count + `<PRORULE>` count == a raw byte-level `grep -c '<AMDPAR>'`** — and that
the raw count is itself non-zero. Parser and dumb text sweep can only disagree if
elements are dropped or duplicated. Two documents in the corpus genuinely have 0 AMDPARs
(a Federal Acquisition Circular cover page and an IRS correction notice) and
`test_live_a_zero_amdpar_rule_is_a_real_zero_not_a_wrong_element_name` pins one of them
inside an issue carrying 892 AMDPARs, so the zero cannot be an element-name error.

**Determinism proved by hash (hard rule 9).** `test_freeze_is_deterministic_byte_for_byte`
re-runs the whole extract into a throwaway directory and compares all manifest SHA-256s.
`python refetch.py --verify-only` verifies **4/4** CH-01 and **6/6** CH-02 with the
network untouched.

**Exact instruction-count matching is asserted by a test**, as `plan.md`'s CH-03 card
requires: `test_pair_yield_matches_exactly_and_a_near_miss_does_not_count` shows a
3-vs-4 sibling is rejected at tolerance 0 and accepted at tolerance 1, and that the
looser rule inflates the yield.

**Document order is asserted to be the mechanism.** `CONTEXT.md` §8 says any reordering
breaks carry-forward; `test_document_order_is_the_mechanism_reordering_changes_the_answer`
demonstrates it rather than leaving the central claim unpinned.

### Decisions

**Class A — escalated, not acted on:**

1. **`QUESTIONS.md` Q9.** `CONTEXT.md` §8's detector misses the word form *"Section
   1.907 is amended by…"*, and under carry-forward that does not under-detect, it
   **mis-attributes**: on golden G1, 20 of 28 elements are pinned to a section they do
   not amend. **Both detectors were implemented, both are recorded in every frozen
   record, both are reported, and the gate branch was taken on the spec-literal one**
   because `prompts/CH-02.md` says *"implement that, not your own reading"* and it is
   the lower figure. Correcting §8 is an edit to a protected file and belongs to the
   architect.
2. **`QUESTIONS.md` Q10.** Two further citation spellings — `46 CFR 356.3` (9 elements,
   1 document, which is the only document with zero attributed sections) and
   table-driven amendments whose sections live in a `<GPOTABLE>` (26 elements,
   1 document) — were found **after** the measurement. **Neither detector was changed.**
   The goldens' §6 forbids revising a rule in §2 once §7 is measured, and the recovery
   would be under 0.31 percentage points; a pre-registration that survives contact with
   the number is worth more than that. Recorded with counts in goldens §9.

**Class B — implementation choices inside spec:**

3. **A citation resolves on three keys, not one.** Page alone cannot separate two
   documents that share a page, and the contents index is wrong twice in 85. The cited
   **section** is a third exact key; where it does not separate the candidates the
   per-`<RULE>` `<PRTPAGE>` route wins over the editorial index. Not a heuristic, and it
   moves no completeness figure into a kinder branch: 0.5080 / 0.6643 before and after.
   Shipped with the probe above.
4. **Neighbour-day resolution is exhaustive, never short-circuited.** Both ±1 days are
   always evaluated and a neighbour is accepted only on a section match; if both match,
   the citation is recorded `neighbour-ambiguous` and left unresolved rather than
   guessed. Stopping at the first hit would have made the answer depend on which files
   happened to be on disk, which breaks hard rule 9. Round-tripped to a fixed point:
   `wanted_issues.json` is empty and `refetch.py` reproduces it in two bounded rounds.
5. **`<PRORULE>` AMDPARs are excluded before the denominator is formed.** A *proposed*
   amendment never executed, so it is not an amendatory instruction. Counted separately
   and used as the reconciliation term in the Q8 known-positive test.
6. **The parse is detector-independent; only attribution differs.** `(operation, anchor,
   designation)` is computed once, blanking the `extended` section spans, which are a
   superset of the spec-literal ones. So the two completeness figures differ *only*
   where §8's own regex differs, and no second effect is smuggled in beside it.
7. **Quoted spans are lifted before section, operation and designation are read.**
   Otherwise `add the cross reference "paragraph (a)(5)"` donates a designation, and a
   verb inside quoted replacement text becomes the operation. Pinned by golden G2
   element 10 and by a unit test.
8. **`current_section` is not reset at a `<REGTEXT>` `PART` boundary**, because §8
   specifies no such reset (goldens P7). The measured consequence — **699 of 8,752**
   elements attributed across a part boundary, every one of them wrong — ships as the
   field `part_mismatch` so CH-03 can exclude them, rather than being silently repaired.
   Raised in Q10.
9. **The whole 8,752-element set is frozen, not only the 85 defect sections.** 6.8 MB
   buys an auditable denominator; a completeness ratio whose denominator cannot be
   re-counted is not a measurement. Same reasoning CH-01 recorded for freezing all 2,428
   EDNOTEs.
10. **`data/raw/fr/` holds whole daily issues; `data/amdpars/` holds only extracted
    instructions.** The raw 272 MB stays git-ignored; 6.8 MB is tracked, against the
    50 MB submission cap (`QUESTIONS.md` Q2).

**Class C — cosmetic:** the evidence scripts' stdout was first captured under the
Windows console codepage, producing a cp1252 em-dash and CRLF line endings in a
`* -text` repository — the same CRLF trap CH-01 recorded. Regenerated under
`PYTHONUTF8=1` and normalised to LF before the first commit that touched them, so
history carries no CRLF this time.

### Questions
**Q9** and **Q10** raised for the architect; neither blocked any work, and both ship
with the numbers under each reading rather than a recommendation dressed as a finding.
**Q8** (CH-01) was applied as instructed: the AMDPAR counter is asserted against a
known-positive input before any zero it prints is believed.

### Gate
**FULL (domain + code)** — `plan.md`. **Not self-certified** (hard rule 2). The reviewer
should note: `PROCESS.md` §6 requires the load-bearing logic to be reimplementable from
`CONTEXT.md` alone. §8 gives the algorithm and the completeness definition but *not* the
tokenisation, so a reviewer reimplementing from §8 alone will get a different number.
The tokenisation is pre-registered in `goldens.md` §2 (P1–P7), committed at `98f1cff`
before any code — that file, not this one, is what a reimplementation should be checked
against.

### State for the next session
`data/amdpars/` is frozen and verifies from its manifest. CH-03 inherits: 70 FR
documents with per-section instruction counts (`documents.json`), 51 defect sections
with at least one exact count-matched sibling, and the 34 that have none, itemised by
cause. **The pair target is met on exact matching alone — do not relax it.** The
`part_mismatch` and `detector_disagrees` fields are carried on every record so CH-03 can
exclude the 699 cross-part attributions and see where the two detectors diverge.
`data/` is **not** sealed until CH-03 passes its gate.

---

## CH-01 · 2026-08-30 · BUILD · Claude Code, `claude-opus-5` · ungated

### Scope
govinfo ECFR bulk XML harvest: download all title XML into the git-ignored
`data/raw/`, extract `<EDNOTE>` **structurally**, filter to codification-defect
notes carrying `"could not be incorporated"`, resolve each to its FR citation,
publish the exclusion ladder, and freeze the extracted records under a SHA-256
manifest with a `refetch.py` that reproduces them.

No AMDPAR parsing, no CFR annual editions, no eval set, no scorer, no `GOOD.md`
edit, no change to anything from CH-00 — all fenced out, none written. Verified
rather than asserted: `git diff --name-only f181be2^..HEAD` over `CONTEXT.md`,
`plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `GOOD.md`, `src/runlog.py`,
`tools/`, `.githooks/`, `context/` and `prompts/` returns **0 files each**.

### The pool — the number this chunk exists to produce

| Rung | | Remaining |
|---|---:|---:|
| CFR titles on govinfo ECFR bulk | | **49** |
| `<EDNOTE>` extracted structurally | | **2,428** |
| minus notes without `"could not be incorporated"` | −2,321 | **107** |
| minus notes not inside `<DIV8 TYPE="SECTION">` | −21 | **86** |
| minus notes with no resolvable FR citation | −1 | **85** |

**Pool gate: `plan.md` CH-03 pre-registers ≥ 60 section-level defect notes with a
resolvable FR citation. Measured 85. CLEARS at 1.42×.** The threshold was read, never
adjusted. Rate: **2.184 defect notes per title**.

`docs/evidence/ch01-pool/exclusion-ladder.md`, generated by `ch01_pool.py`, whose
stdout ships as `ch01-pool-run.txt`. Every rung asserts kept + removed == received.

### The nine-title reference reproduces exactly

`CONTEXT.md` §8's pre-existing measurement on titles 12, 20, 21, 24, 26, 40, 42, 45,
49, re-derived on today's govinfo bytes by an independently written parser:

| Measure | §8 | Measured | Δ |
|---|---:|---:|---:|
| Total `<EDNOTE>` | 903 | **903** | +0 |
| Codification-defect notes | 44 | **44** | +0 |
| Carrying an FR citation | 44 | **44** | +0 |
| Section-level, container reading | 38 | 36 | **−2** |
| Section-level, names-a-section reading | 38 | **38** | +0 |

Three of four integers identical. The fourth is a **definition difference, reconciled
exactly**: §8's own rows (*38 section-level* + *6 below section level* = 44) count
notes that **name** a section; `prompts/CH-01.md` step 5 counts notes that **sit** in
one (*"not appendix/part"*). Both readings are computed and both ship. **The gate uses
the container reading — the smaller of the two** (85 usable, not 87). The gap is two
identified notes: title 40 part 63 in an `APPENDIX`, title 49 part 383 at `PART` level.

### Three deviations — reported, not tuned

**D1 · The pool is below the projected range.** 107 defect notes against `CONTEXT.md`
§8's expected 150–250, and 86 section-level against 130–210. Cause measured, not
guessed: §8's range extrapolates per title from the nine reference titles, and those
are the **largest** — 408 MB of 824 MB, **50 % of the corpus by bytes but 18 % by
title count**, including title 40 (largest) and title 26 (second). 44 ÷ 9 × 50 = 244,
over by **2.28×**.

**D2 · The "~2.3× eCFR undercount" is not the API's error, it is the extrapolation's.**
§8 states the eCFR search API's figure of 92 undercounts by ~2.3×. Measured
govinfo : eCFR = **1.16×**. The 2.28× belongs to D1's arithmetic. **92 was far closer
to the truth than the range built to discredit it.** Hard rule 15 firing on this
project's own spec. Republished beside the old figure, never in place of it.

**D3 · The corpus is 824,289,052 B over 49 titles, not ~2.3 GB over 50.** Title 35 is
reserved and has no govinfo folder. The 2.3 GB is D1's extrapolation again
(407 MB ÷ 9 × 50). The measured nine-title figure of 407 MB in §8 is **correct** —
only the projection from it is not.

`CONTEXT.md` is protected read-only for a build session, so D1–D3 are recorded here
and in the ladder **for the architect**, not applied.

### One defect note carries no FR citation, and it is an upstream typo
Title 47 § 54.503: *"At 83 FR , May 1,2018, § 54.503 was amended…"* — the page number
is absent from the **published** note. No extractor can resolve that. Excluded at rung
4, counted, and quoted in full rather than silently dropped. FR resolution is
deterministic for the other 106; §8's 44/44 on the reference titles reproduces exactly.

### Files
Created: `src/harvest_ednotes.py` · `tests/test_harvest_ednotes.py` · `refetch.py` ·
`data/ednotes/` (`ednotes.jsonl` 2,428 records · `defect_notes.jsonl` 107 ·
`counts.json` · `counts_by_title.csv` · `manifest.json` · `source_index.json`) ·
`docs/evidence/ch01-pool/` (`goldens.md` · `exclusion-ladder.md` · `ch01_pool.py` +
`ch01-pool-run.txt` · `ch01_determinism.py` + `ch01-determinism.txt`).
Edited: `QUESTIONS.md` (Q8), `STATUS.md`, `PROGRESS.md`, `AI-USE.md`.

`du -sh data/` = **788 M**, of which `data/raw/` is **787 M** (git-ignored, never
tracked) and the frozen `data/ednotes/` is **1.7 M**. Tracked files **68**.
`git ls-files | grep -c '\.xml$'` = **0**.

### Tests
`python -m pytest tests/ -q` → **61 passed, 0 failed, 0 skipped** (22 from CH-00, 39
new). Zero skips *because `data/raw/` is populated*: the two `test_live_*` cases
re-derive the goldens from the real 41 MB title-7 XML and are marked `skipif` absent,
so on a clean clone the count is 59 passed / 2 skipped. Both states are correct and
both are reported.

**Goldens committed before the parser, provably.** `docs/evidence/ch01-pool/goldens.md`
is commit `dd1504d`; `src/harvest_ednotes.py` is commit `7d56f26`. Four records read
off the raw XML with `sed`/`grep`/`awk` only: G1 a defect note in a section, G2 a
defect note in an appendix with an empty `N=""`, G3 a non-defect note (negative
control — a filter that keeps it is broken), G4 a defect note with two FR citations.

**An independent route to the same integer.** `test_live_title7_structural_count_
matches_a_text_only_sweep` asserts the parser's defect count equals a plain `count()`
of the literal over the raw bytes, and its `<EDNOTE>` count equals a plain count of the
open tag. Parser and dumb text sweep can only disagree if notes are dropped or
duplicated.

**Determinism proved by hash (hard rule 9).** `ch01_determinism.py` re-parses all
824 MB into a throwaway directory: **6/6 artefacts byte-identical**, then the freeze
verifies **4/4** against its own manifest with the network untouched. It exits **2**,
not 0, when `data/raw/` is absent — a determinism proof that passes on missing input
proves nothing.

### PROBE FLIP
`test_div1_N_is_the_volume_index_and_is_not_the_title_number` fails on the code as
first written (`doc_title = el.get("N")` yields `"1"` for every title, so
`title_sources` reads `{'node': '11', 'div1_node': '1', 'filename': '11'}`) and passes
on the fix (`doc_title = _title_from_node(el.get("NODE"))` → all three read `"11"`).
Both states were observed: the counter printed **2428** disagreements before, **0**
after. Kept forever, per hard rule 6.

### Decisions

**Class B — implementation choices inside spec:**

1. **`<DIV8 TYPE="SECTION">` is the ECFR bulk spelling of `<SECTION>`.** The spec's
   element name belongs to the CFR annual-edition DTD. Semantics unchanged; see
   `QUESTIONS.md` **Q8**, which also flags the consequence forward to CH-03.
2. **`hed` and `text` are separate fields.** `</HED>` abuts `<PSPACE>` with no
   separator, so a whole-element concatenation silently yields `Editorial Note:At 83
   FR …`. The defect filter reads `text`.
3. **`fr_citation` is the FIRST match**, all matches kept in `fr_citations`. Golden G4
   is the note where the second citation is the stay it collided with; reading the last
   match would mis-attribute the defect at CH-02. **5 of 107** notes cite more than one.
4. **stdlib `xml.etree.ElementTree`, not `lxml`.** `refetch.py` and the suite must run
   in the CH-14a clean-clone rehearsal with no third-party dependency. Streamed with
   `iterparse` and pruned as it goes: **161 MB title 40 parses in 0.8 MB of heap**.
5. **`refetch.py` lives at the repo root**, not inside `data/ednotes/`. `CONTEXT.md`
   §8's Freeze paragraph scopes it to *everything under `data/`*, and CH-03 adds to the
   same file rather than shipping a second one.
6. **The whole `<EDNOTE>` set is frozen, not just the 107 defects.** 1.5 MB buys an
   auditable denominator; a ladder whose top rung cannot be re-counted is not a ladder.
7. **`names_section` carries the second reading of section-level but never replaces the
   first.** The gate uses the smaller. Recorded before anything depends on it.
8. **`tally()` raises rather than asserts.** `python -O` strips `assert`, and a
   load-bearing count that stops checking itself under an optimisation flag is exactly
   the silent green this project exists to expose.
9. **`manifest.json` carries the sha256 of every raw title XML**, so the pool number is
   pinned to specific upstream bytes. `source_index.json` (govinfo's announced sizes
   and last-modified stamps) is deliberately **outside** the hashed set: that stamp
   moves on re-publication even when nothing that matters changed, and a manifest that
   fails for that reason trains a reader to ignore it.

**Golden divergence, recorded not resolved away.** G2 pre-registered `section_raw` as
the empty string (the appendix's own `N=""`); the implementation returns `None` (no
enclosing `SECTION` at all). **The golden was not edited.** A field `container_n` now
carries the pre-registered reading, `section_raw` keeps the narrower one, and the test
asserts **both**. The two load-bearing fields — `section` and `section_level` — agreed
under either reading. Full account: the ERRATUM appended to `goldens.md`.

**Class C — cosmetic:** a Python `write_text` patch introduced CRLF into `QUESTIONS.md`
and three other files on a `* -text` repository, making commit `f181be2` rewrite all
250 lines of `QUESTIONS.md` for nothing. Normalised back to LF in this chunk's ledger
commit; `git diff --ignore-cr-at-eol` confirms the content is byte-identical to the
committed Q8 text. History is left as it stands — no rewrite, no force-push.

**`CHANGELOG.md` gets no row.** It is the Improvement Changelog: capability iterations
with a prediction fixed before the build. CH-01 builds no capability and moves no
metric; it measures the corpus. A row here would be the exact padding the table exists
to expose — the same reasoning CH-00 recorded.

### Questions
**Q8** raised and self-resolved in code (no operator decision needed), with its CH-03
consequence flagged. **D1–D3** are corrections to `CONTEXT.md` §8 that a build session
may not apply to a protected file; they are recorded here and in the ladder for the
architect. None blocked any work.

### Gate
**None** (`plan.md`: CH-01 GATE: none). Self-checked against the card's done-when: pool
count printed per title ✔ · exclusion ladder committed with counts at every step ✔ ·
results within range of the nine-title reference **or the deviation explained** —
explained, exactly, three of four measures reproducing to the integer ✔ ·
`du -sh data/` and tracked-file count printed ✔ · no XML tracked ✔.

### Status ledger
`CH-01 · govinfo EDNOTE harvest | none | built | 2,428 EDNOTEs -> 107 defect -> 86
section-level -> 85 with FR; pool gate >=60 CLEARS at 1.42x; 9-title reference
903/44/44 reproduces exactly; suite 61 green`

### State for the next session
`data/ednotes/defect_notes.jsonl` holds **107** records; **85** are section-level with
a resolvable FR citation and are what CH-02 attributes. The distinct FR documents
behind them are the CH-02 fetch list. `data/raw/ecfr/` holds all 49 title XMLs
(787 MB, git-ignored) — CH-02 needs the **FR** bulk collection, not these, and
`data/raw/` must stay untracked. `data/` is **not** sealed yet; sealing happens on
CH-03's PASS.

---

## CH-00 · 2026-08-30 · BUILD · Claude Code, `claude-opus-5` · ungated

### Scope
Repository initialisation, the canonical file set, the run logger with cost and
time accounting, the build-session trajectory exporter, and the pre-commit guard.
No harvest code, no AMDPAR parsing, no scorer, no eval logic, no thresholds in
`GOOD.md` — all explicitly fenced out and none written.

### Files
Created: `.gitignore` · `.gitattributes` · `STATUS.md` · `PROGRESS.md` ·
`QUESTIONS.md` · `CHANGELOG.md` · `AI-USE.md` · `GOOD.md` · `src/runlog.py` ·
`tests/test_runlog.py` · `tools/export_session.py` · `.githooks/pre-commit` ·
`docs/evidence/ch00-goldens.md` · `docs/evidence/ch00_guard_probe.py` +
`ch00-guard-probe.txt` · `docs/evidence/ch00_session_cost.py` +
`ch00-session-cost.txt` · `docs/evidence/runs/README.md` and the CH-00 demo run ·
`docs/trajectories/build/CH-00.jsonl` · directory scaffolding for
`docs/progress/`, `agents/`, `prompts/design/`, `docs/process/superseded/`.

Moved, not deleted: `DIVERGENT-RESEARCH-PROMPT.md` and `KILL-TEST-PROMPT.md` →
`prompts/design/` (they are the agent instructions that produced `context/06` and
`context/07`, both of which ship — deliverable 4 asks a trajectory be followable
*from the agent instructions* to the result, and shipping the outputs while
deleting the instructions fails exactly that half). `BUILD-PHASE-1-PROMPT.md` →
`docs/process/superseded/` (contradicts `plan.md`; out of the root so no build
session reads it as current, still in the repo because `PROVENANCE.md` cites it).

Edited under explicit operator ruling: `context/09-COMPLIANCE-AUDIT.md` and
`context/09b-audit-raw.json`, one PII substitution each. Nothing else under
`context/` was touched.

### Tests
`python -m pytest tests/ -q` → **22 passed, 0 failed, 0 skipped.**

The suite was committed **red** in `59dee06` (`ModuleNotFoundError: No module
named 'runlog'`) and turned green by `3b6d22b`. Both states are in the history, so
hard rule 4's ordering is provable from git rather than asserted in prose.

Goldens hand-computed in `docs/evidence/ch00-goldens.md`, then cross-checked by a
**third independent route** — exact `fractions.Fraction` arithmetic, no Decimal, no
project code. Hand doc, Fractions and implementation agree to 6 dp on all four
money goldens.

`docs/evidence/ch00-guard-probe.txt` → **16/16.** Every case feeds a guard
something it must refuse and asserts the refusal: operator phone, operator email,
Anthropic key, AWS key id, a 26 MB blob, and a missing pattern source (fail
closed). Plus a clean-file case so a guard that always fails cannot pass, and a
negative control proving ordinary prose survives untouched.

The hook's first live act was to refuse a commit of the probe's own source: it
found an AKIA-shaped token there and was right to. The literal is now assembled
from two halves at runtime so the probe still tests the identical string. Adding
an allowlist would have been weakening a guard to get it green (hard rule 5).

### Decisions
**Class B — implementation choices inside spec, recorded for review:**

1. **Money is `Decimal` end to end**, quantised to 6 dp ROUND_HALF_UP. Binary float
   for currency is a defect. The ledger carries the exact 6-dp string; the JSONL
   carries both a float and `imputed_usd_exact`.
2. **`delivery` field** — `standard` / `batch` (50%, per Q1) / `subscription`. Q1
   mandates the Batches API, so the halving has to live in the logger or every
   later cost number is 2x wrong. `subscription` imputes at full list and flags
   `cost_is_imputed` — "impute and say so".
3. **`est_usd` per run**, default USD 0.05, for the ceiling check. The spec says
   refuse *before* a run that would cross USD 18, and at `__enter__` no token count
   exists yet, so the projection needs an estimate. 0.05 is ~7x Q1's measured
   ~$0.0072/call — deliberately conservative, overridable per run.
4. **Aborted runs record `imputed_usd: null` and an EMPTY ledger cell**, never 0.
   "Unknown" and "free" are different claims and must not share an encoding.
   `cumulative_usd()` excludes them and `unknown_cost_runs()` counts them, so an
   unknown can never silently pass as free.
5. **A finished run reporting 0 input AND 0 output tokens raises `ZeroCostRun`.**
   A completed model call always consumes input tokens; zero means the caller never
   wired usage through, and a silent $0 would corrupt every cost-per-task figure.
6. **Injectable clock and UTC stamp** (`_clock`, `_utc`) so the suite asserts an
   exact `wall_clock_s` rather than `> 0`. Hard rule 8's purity constraint binds the
   scorer and resolver, not the logger, whose job is to measure the clock.
7. **PII patterns are never stored in the repository.** The exporter and the hook
   read literals from, in order, `$MICRO1_PII_PATTERNS` → `~/.config/micro1/
   pii_patterns.txt` → the git-ignored `context/02-ABOUT-ME.md`, sharing one source
   order so they cannot disagree. A file that lists the value in order to remove it
   is a new copy of the leak. **No `.gitignore` line was added**, because the
   prompt fixed that file's contents exactly.
8. **The hook fails closed** when no pattern source exists. A sweep that cannot find
   its patterns and passes anyway is the precise failure this project exists to
   expose. `--no-verify` remains as a visible, logged escape.
9. **CSV written with `lineterminator="\n"`** and JSONL with `newline="\n"`, so
   artifacts are byte-identical across platforms under `* -text` (hard rule 9).

**Class C — cosmetic:** default branch `main`; commit messages carry reasoning
because they are read by reviewers who have zero shared context.

**Scope-fence note, declared rather than quietly taken.** The fence names
`docs/evidence/runs/`. Rule 14 requires every data claim to ship its generating
script and committed output, and `PROCESS.md` §3 makes `docs/evidence/` canonical, so
five evidence artifacts were written to `docs/evidence/` itself rather than to the
`runs/` subdirectory, where they would be miscategorised as run records. Flagged
here for the architect; trivially movable if ruled otherwise.

**Not done, deliberately:** no test file for `tools/export_session.py`. The fence
names `tests/test_runlog.py` and no other test path. Its behaviour is instead proved
by `docs/evidence/ch00_guard_probe.py`, which lives inside `docs/evidence/`. If the
architect wants it in the suite, that is a one-line move at the next chunk.

### Questions
Raised and recorded: **Q4** (the prompt contradicts itself about whether the design
prompts are staged at step 4b — closed by convergence, both readings give a
byte-identical result), **Q5** (the safety rider makes `context/` read-only while
step 5 requires editing two files in it — **put to the operator, ruled: redact in
place**), **Q6** (§1b says strip `.env` values, the rider says never read `.env` —
resolved in code: the exporter strips credential *shapes* and `KEY=value` forms and
never opens `.env`), **Q7** (commit author identity becomes public at CH-15 —
**put to the operator, ruled: keep it**).

**Finding worth the architect's attention, in Q5.** The audit's claim that there are
**four** PII carriers is **wrong**. A maximally permissive sweep — literal,
digits-only projection, JSON-escape-stripped, case-insensitive — finds **two**:
`context/09-COMPLIANCE-AUDIT.md` and `context/09b-audit-raw.json`.
`context/04b-intel-raw.json` and `context/05b-tournament-raw.json` are clean;
`context/10-REMEDIATION.md` had already self-redacted to `<OPERATOR-PHONE>`, as that
file itself records. The personal email has **zero** carriers. The sweep is not
vacuous: the same pattern returns 1 against the git-ignored source file and 0
against the tracked set after redaction — positive control and pass criterion both
reported. The prompt's own instruction *"do not hard-code the list, find them with
the sweep"* is what caught the over-claim; the hard-coded list would have sent a
session hunting three already-clean files.

### Gate
**None.** CH-00 is ungated by `plan.md` and `PROCESS.md` §6. No self-certification
beyond the done-when criteria is claimed: the suite is green, the guard probe is
16/16, and the goldens were computed before the code — but nobody has independently
reviewed this chunk, and this entry does not pretend otherwise.

### Status ledger
`STATUS.md`: CH-00 → **built**. Every other chunk seeded **todo**, except CH-07,
which is **not built** by ruling R-01 as pre-declared counted removal #3.

Repository `chinmoypaul8897/instruction-that-wont-execute`, **private**; anonymous
`curl` returns **404**, verified. Tree 430.2 MB / 7,460 files; **53 tracked**,
largest tracked blob 1.05 MB (the exported CH-00 transcript).

### State for next session (CH-01)
- `git config core.hooksPath .githooks` is set **on this machine only**. A fresh
  clone must re-run it; the hook is not self-installing.
- `data/` does not exist yet. CH-01 creates it. `data/raw/` and `*.xml` are already
  git-ignored, and the hook rejects any blob over 25 MB — **extract, then freeze.**
- `www.ecfr.gov` and `www.federalregister.gov` are **403 from this machine**.
  `www.govinfo.gov` is the sole harvest channel. Do not attempt a workaround.
- The run logger is ready and is the only sanctioned way to invoke an agent
  (hard rule 10). CH-01 needs no model, so it needs no runs.
- `GOOD.md` is deliberately empty and must stay empty until CH-04.
