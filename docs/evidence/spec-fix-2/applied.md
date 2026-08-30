# SPEC-FIX-2 — what the Q11 ruling changed, and what it deliberately did not

**Session:** SPEC-FIX-2 · 2026-08-31 · Claude Code, `claude-opus-5` · BUILD (spec-edit scope)
**Mandate:** apply a ruling already made. *"You decide nothing."*
**Predecessor:** SPEC-FIX-1 refused a metric correction. `docs/evidence/spec-fix-1/verdict.md`.

---

## The one-line summary

**The architect proposed a change that would have turned a failure into a pass. It was
refused. This chunk applied the ruling that followed — and the ruling keeps the gate
failed, adopts a fix that costs 8 points, and publishes the failure in the spec itself.**

`CONTEXT.md` went to **v1.1**. **No number moved. Nothing was re-run.**

---

## Answer to the question the prompt makes the headline

> **DID ANY CHANGE MAKE A FAILING NUMBER PASS?**
>
> ## NO.

Three independent reasons, all checkable by `spec_fix_2_verify.py` §4–§5:

1. **The gate definition is byte-identical to v1.0** and appears exactly once. The
   threshold is untouched. The refused metric `attributed ÷ total` **does not appear in
   `CONTEXT.md` at all** — the script asserts the string `attribution_completeness` is
   absent from the file.
2. **The gated figure cannot reach the branch boundary even if every v1.1 change helped.**
   CH-02 measured completeness at **0.5080** (sign-only) and **0.6643** (extended). The
   word-form correction can at most move the gated figure from the first toward the
   second. **0.6643 < 0.80**, so CH-02 stays in the *"< 0.80 — documented failure"*
   branch, and is nowhere near the 0.90 gate. The part-boundary reset moves the figure
   **down**. Case-sensitivity can only **remove** detections, never add them.
3. **Nothing was measured.** The attributor was not re-run; `data/`, `src/` and `tests/`
   were never opened. Every figure quoted in v1.1 was already committed before this
   session began.

---

## The three changes, and why each is the opposite of a rescue

| # | change | effect on the number | why it is in |
|---|---|---|---|
| **1** | §8 records that **the gate FAILED**, publishes 0.5080 / 0.6643 against 0.90, and names `attributed ÷ total` as **tested and rejected** | none — it *documents* a failure | the refusal itself is now part of the law, not a footnote in a rejected chunk |
| **2** | the section detector takes the **word form** beside the sign form, **case-sensitively** | would **raise** attribution if re-measured | justified with the number out of view: **ten documents / 1,910 elements attribute to nothing** without it |
| **3** | `current_section` **resets at a `<REGTEXT>` part boundary** | **costs 8.0 points** (0.9865 → 0.9066) | adopted *because* it hurts — the fix that helps and the fix that hurts are ruled on together |

**Change 3 is the load-bearing one.** SPEC-FIX-1's third finding was that the original
proposal adopted the +22.5-point fix and never mentioned the −8.0-point one CH-02 had
already called an improvement. Adopting only the second half of that pair would have
repeated the defect in the act of correcting it.

---

## What was written into `CONTEXT.md`, precisely

- **§8, after the completeness definition** — a four-paragraph block headed *"THE GATE
  FAILED, AND THE FAILURE IS PUBLISHED — it was not fixed"*: the two failing figures
  against the 0.90 gate; the sabotage control (6,395 of 6,663 elements placed on a
  different section, **identical 0.7613**) as the reason the attribution figure was
  rejected; the fair statement that the metric is *not* vacuous (it catches the
  silent-drop mode at 0.2503); the fact that the definition was **not** rewritten after
  it failed; and Q10's two spellings, counted at **< 0.31 pp** and left unfixed.
- **§8 algorithm step 2** — the part-boundary reset.
- **§8 algorithm step 3** — sign form and word form, with `Section` **case-sensitive**
  stated as specification rather than left to the implementer.
- **§8, four block-quoted rationales** — why the word form is in and why the reason is not
  the number; why case-sensitivity is specified (and that **every 0.9865 in the repository
  is the case-insensitive figure and therefore an over-count**); why the reset is adopted
  though it hurts; and Q12(a)'s correction that **126 of the 699** part mismatches are an
  unlogged `regtext_part` extraction defect, not attribution error, leaving **573**.
- **Header** — v1.0 → **v1.1**. **§13** — one change-log row naming the refusal.

Every number above was quoted from evidence committed before this session and re-checked
against it, not carried across from the prompt (hard rule 15). The prompt's claim of
*"1,910 elements"* was verified by summing the ten documents in
`docs/evidence/spec-fix-1/recomputed.md`: 838 + 649 + 136 + 100 + 52 + 50 + 44 + 27 + 9 +
5 = **1,910**. ✅

---

## What was deliberately NOT done

| | |
|---|---|
| re-run the attributor | **no** — forbidden by the prompt; re-measuring is CH-03's job |
| add a metric, move a threshold, alter the definition | **no** — all three explicitly forbidden, and asserted against in §4 of the verifier |
| fix Q10's two spellings | **no** — they stay recorded and unfixed |
| fix §8's stale *"~42% of AMDPARs name a section"* | **no** — not specified, so it is a STOP. **Raised as `QUESTIONS.md` Q14** |
| touch `data/`, `src/`, `tests/`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `GOOD.md` | **no** — asserted in §6 of the verifier |
| convene a subagent panel | **no** — the prompt forbade it, and it was right to. See the economy note in `PROGRESS.md` |

---

## The residue this chunk creates, recorded as Q14

v1.1 specifies a **case-sensitive** detector. **Every `extended` figure in the repository
was computed case-INsensitively** — 0.6643, 0.9865, 0.9066, 57/70, 2,459, 1,086, and the
699 / 573 / 126 decomposition. Those figures now describe a detector the specification no
longer names, and they are **not reconstructible by arithmetic** from what is known (683 of
684 lowercase-only elements are affected, most of them correctly). **CH-03 must re-measure
rather than adjust.** It does not change the gate outcome: a stricter detector cannot raise
a failing figure.

---

## One thing the verifier caught, recorded rather than smoothed away

Its first run **failed**, on `[v1.0 bare current_section step 2 - absent]`. The check was
wrong, not the edit: v1.0's step 2 is a strict **prefix** of its v1.1 replacement, so a
substring test can never be satisfied by any correct edit. It was rewritten to be
line-exact, and the reason is a comment in the script rather than a silent deletion —
because a check quietly adjusted until it turns green is precisely the failure this
project exists to demonstrate.

The script also fixes, for itself, the CRLF-on-a-`* -text`-repo defect CH-02 and
SPEC-FIX-1 both recorded and neither owned: it reconfigures stdout to LF in one line.

---

**Verification:** `spec_fix_2_verify.py` → `verify.txt`. **38 checks, all PASS, 0 FAIL, exit 0.**
Re-runnable from a clean clone; it opens no data and invokes no model.
