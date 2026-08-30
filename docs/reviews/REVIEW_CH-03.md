# REVIEW — CH-03 · point-in-time text + eval set

## VERDICT: **FAIL**

---

## Provenance of this document — read this first

**The independent reviewer was stopped by a session crash before it wrote its own
verdict file.** What survived on disk is its runnable evidence — seven probe scripts
in `docs/reviews/ch03-probe/` and two kept tests in
`tests/test_review_ch03_findings.py`, both RED.

**This file was assembled by the BUILD session from those artifacts.** That is a
weaker provenance than `CLAUDE.md` hard rule 2 asks for, and it is stated here rather
than glossed:

- The reviewer ran with **zero shared context** and its findings are its own.
- **Every finding below was independently re-derived by the build session** with code
  written separately from the reviewer's, before being acted on (hard rule 15: a
  finding from another agent is a claim, not a fact). The re-derivations are in the
  commit that adds this file.
- **The build session did not soften, drop or re-rank anything.** The verdict is FAIL
  and the build session's own work is what failed.
- **A fresh reviewer with zero shared context re-reviews the fix.** This document is
  not a gate pass and does not pretend to be one.

---

## Findings, severity-ranked

### 🔴 SEVERE · F1 — the eval set is beatable by a six-line script that reads neither the instructions, nor the CFR text, nor a model

`src/eval_set.py:138` — `negative = free[0]`.

The negative is chosen as the **sorted-first** count-matched sibling, while the
positive is a *given* section. Negatives therefore sit systematically earlier in
section order than their positives.

**Measured, two ways, independently:**

| measurement | reviewer | build session's own re-derivation |
|---|---|---|
| label-blind sort-order script accuracy | 0.7763 (59/76) | **0.8158 (62/76)** |
| pairs whose negative sorts BEFORE its positive | 27/33 | **32/38 — RETRACTED, see below** |
| exact two-sided binomial | p = 0.000324 | **p = 0.000024 — RETRACTED** |

> **The build session's `32/38, p = 0.000024` is WITHDRAWN.** It came from an
> uncommitted inline snippet that RECONSTRUCTED the pairing from the frozen items
> file instead of running the rule — a hard rule 14 violation, no generating script.
> Measured properly by `docs/evidence/ch03-evalset/ordering_bias.py`, the pre-fix rule
> gives **36/50, exact p = 0.0026**, and the shipped rule **25/50, p = 1.0000**. The
> direction and the conclusion are unchanged; the number was wrong.

*(The two differ because the reviewer recovered pairs from `(frdoc, count)` groups and
the build session recovered them per-positive; both find the same defect.)*

**Why this is SEVERE and not MAJOR.** It beats:

- **B0-agent, 0.6447**, by 17 pp — with no model and no corpus;
- **`GOOD.md`'s A1 absolute bar of 0.80**;
- `CONTEXT.md` §7's own stated trivial-attack surface, *"best of 26 features 0.5934
  inside its own null at p = 0.185"*.

`CONTEXT.md` §8 on exact count matching: *"Non-negotiable — unmatched, a hardcoded
threshold on instruction count beats the agent, and that is precisely how an earlier
candidate died."* **The count is matched. The SELECTION is not.** The project built a
guard against the exact failure that then arrived through the neighbouring door.

**The pre-registration's own justification is falsified.**
`docs/evidence/ch03-evalset/pre-registration.md` §3 says the rule is *"deterministic,
declared, and independent of any label."* It is independent of the label and
**correlated with it through the selection asymmetry**, which is the property that
matters. The reason given was wrong, and it was wrong before any number existed.

**Consequence: the ★ CHECKPOINT numbers at `7595562` were computed on a defective eval
set and are withdrawn pending a re-run.**

### 🟠 MAJOR · F2 — a volume that declares no `<PARTS>` header excludes every section in it, silently

`src/cfr_pit.py` — `parse_parts_header("")` returns `part_lo=None`; `volume_covers`
then returns `(False, False)` for every part; `candidate_volumes` returns `[]`.

**The declared G-G2 fallback cannot fire, because it is itself gated on
`covers_part`.** Single-volume CFR titles carry no `<PARTS>` element at all —
`CFR-2016-title13-vol1.xml`, 4,157,015 bytes, has none.

**Verified consequence:** FR Doc `2016-16399`'s pair — positive `13 CFR 125.6`,
negative `13 CFR 121.1001` — is present exactly once each in the 2016 edition, strips
cleanly and passes the leakage test, and was nonetheless excluded on the
`section-not-in-as-of-edition` rung with reason `no-volume-covers-this-part`.

**The frozen n is understated: 39 pairs / 78 items, not 38 / 76.**

`goldens.md` G-G2 wrote the epitaph before the defect happened: *"a wrong answer that
presents as a smaller n rather than as an error — that is the shape of every failure
this project is built to catch."*

### 🟡 MINOR · F3 — the reviewer's from-spec reimplementation disagrees with the shipped attributor on 545 of 8,752 elements (6.23%)

Reimplementing `CONTEXT.md` §8 **literally**, importing nothing from the project, the
reviewer measured completeness **0.5362** against the committed **0.5340**, with 545
elements attributed differently.

**This is a known and documented deviation, not a new defect.** Every example is a
title-26 long-form section number — `1.367(a)-3T`, `1.367(b)-0` — where §8's printed
regex truncates to `1.367` and the shipped parser captures the full designation.
`QUESTIONS.md` Q9 records it in terms: *"section 8's regex truncates every title-26
section number (`§ 1.367(a)-8` → `1.367`), which CH-02 fixed under goldens rule P2 and
which is the same class of defect section 8 itself blames for a predecessor's 0.46."*

**Kept as MINOR rather than dismissed**, because it is a real divergence between the
spec as printed and the code as shipped, and the reviewer was right to surface it. It
is the architect's to close, not a build session's.

---

## MUTATIONS — 9 designed, **the "9 caught" claim is RETRACTED**

> **RETRACTION, added after round 2.** The table below is **false** and it is kept
> rather than deleted. `mutate.py` decided "caught" from `returncode != 0` **with no
> green baseline**, so a mutation applied to an already-red suite — or one that is a
> **no-op on the fixture** — reads as caught. **M7 cannot have been caught**: golden
> G-D's free candidate list is `["B"]`, so `free[0]` and `free[-1]` are the same
> element and the mutation changes nothing.
>
> The build session **repeated this claim in four documents without checking it**,
> which is precisely the failure `CLAUDE.md` hard rule 15 exists to prevent, and it
> did so on the evidence that was supposed to prove the gate worked.
>
> **Verified independently before retracting:** reverting the F1 fix to
> `negative = free[0]` produces a test result **identical** to the unmutated run.
>
> The corrected harness — which counts a mutation as caught only when the result
> **changes from an established baseline** — is
> `docs/reviews/ch03-probe2/mutate3.py`. Against a green baseline of 278 passed it
> reports **6 caught, 0 missed**, and that number can be trusted because the harness
> establishes the baseline it compares against.

`docs/reviews/ch03-probe/mutate.py`. Each mutation was applied to the working tree, the
suite run, and the tree restored.

| # | mutation | result |
|---|---|---|
| M1 | tolerance 0 → effectively 1 (exact matching relaxed) | **CAUGHT** |
| M2 | a defect section permitted as a NEGATIVE | **CAUGHT** |
| M3 | a negative may be REUSED across positives | **CAUGHT** |
| M4 | exclusion-ladder closure assertion dropped | **CAUGHT** |
| M5 | `build_pairs`' own `pairs + unmatched == defects` guard dropped | **CAUGHT** |
| M6 | the leakage gate no longer drops a leaking pair from the freeze | **CAUGHT** |
| M7 | negative-selection flipped to the LAST sorted candidate | **CAUGHT** |
| M8 | the `n_items == 2 * n_pairs` assertion dropped | **CAUGHT** |
| M9 | `instruction_counts` silently counts UNATTRIBUTED elements too | **CAUGHT** |

**M7 is worth dwelling on, and for a different reason than this review first gave.**
The original text here claimed the suite catches a flip from *first* to *last* sorted
candidate. **It does not, and cannot** — see the retraction above. The true statement
is stronger and worse: **no test pinned the rule at all**, and the kept test added by
this review asserted on the FROZEN FILE, which a source mutation does not touch. Round
2's SEVERE finding 1 is exactly that, and the gap is closed by
`tests/test_review_ch03_round2_findings.py::test_R1_...`, which runs `build_pairs`
against the real corpus so a change to the RULE is caught by the RULE's own test.

*A test that pins an artifact is not a test that pins the property.* That sentence is
the whole lesson of both review rounds.

---

## WHAT I REPRODUCED

| claim | committed | reproduced | ✓ |
|---|---|---|---|
| suite green | 232 | 232 passed | ✓ |
| pairs / n | 38 / 76 | 38 / 76 | ✓ (but **understated** — see F2) |
| exclusion ladder closes | 13+22+10+2+38 = 85 | 85 | ✓ |
| strip counts | EDNOTE 5 · EFFDNOTP 1 · CITA 64 · EAR 0 = 70 | identical | ✓ |
| items that would have leaked unstripped | 8 / 76 | 8 / 76 | ✓ |
| leakage test FAILS on unstripped input | asserted | reproduced on real bytes | ✓ |
| exact instruction-count matching | asserted by a test | holds in the frozen data | ✓ |
| `data/ednotes/`, `data/amdpars/` unmodified | claimed read-only | no commits touch them | ✓ |
| v1.1 global completeness | 0.5340 | **0.5362** from-spec | ✗ — F3 |

**Could not reproduce:** the from-spec completeness figure (F3), explained above.

---

## What must happen before CH-03 can pass

1. **Fix F1** with a negative-selection rule that is neutral in section-sort order, and
   **publish the residual attack accuracy** as the evidence that it worked.
2. **Fix F2** so a volume with no `<PARTS>` header is searched rather than skipped, and
   re-freeze at the corrected n.
3. **Re-run the ★ CHECKPOINT.** Its numbers were computed on the defective set.
4. **Keep both red tests forever.** They are the probe that flips (hard rule 6).
5. **Re-review from a fresh session with zero shared context.**
