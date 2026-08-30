# CH-03 — pre-registration

**Committed BEFORE any CH-03 number exists.** Everything below is a decision about
*how* to measure, taken while the answer is still unknown. Hard rule 5 forbids moving
any of it afterwards. Where a decision could go either way, the reason is recorded
here so a reviewer can judge the choice on its merits rather than on its result.

Read with `docs/evidence/ch03-evalset/goldens.md`, which hand-computes the expected
outputs, also before the code.

---

## 1. Which detector the eval set is built on

**`CONTEXT.md` v1.1's detector, and only that one.** §13 says changes 2 and 3 —
the case-**sensitive** word form and the `<REGTEXT>` part-boundary reset — "alter the
spec **for CH-03 onward**". `CONTEXT.md` is law and outranks the code. So:

- a section is named by the **sign form** `§\s*[\d.]+[a-z]?` **or** the **word form**
  `Section` / `Sections` + number, the word form matched **case-sensitively**;
- `current_section` **resets to null** whenever the enclosing `<REGTEXT>`'s `PART`
  differs from the previous element's;
- an element with no `current_section` is **unattributable** — counted, never guessed.

**Four detector configurations are measured, not one.** Reporting only the v1.1
figure would leave the reader unable to tell which of the two v1.1 changes moved
what. Q14 asks for the case-sensitive figures **beside** the case-insensitive ones,
following `goldens.md`'s ERRATA convention (a wrong number is corrected in a new
entry, never edited out of the old one):

| id | word form | case | part reset | what it is |
|---|---|---|---|---|
| `spec_literal` | no | — | no | `CONTEXT.md` v1.0's own regex. CH-02 measured **0.5080**. |
| `extended_ci` | yes | insensitive | no | what CH-02 shipped. Measured **0.6643 / 0.9865**. |
| `extended_cs` | yes | **sensitive** | no | isolates the cost of case-sensitivity alone |
| `v11` | yes | **sensitive** | **yes** | **`CONTEXT.md` v1.1. The eval set is built on this.** |

`spec_literal` and `extended_ci` must **reproduce CH-02's committed figures exactly**.
If they do not, the re-measurement is wrong and nothing downstream of it is trusted.
That is the control, and it is declared before it runs.

**Q14(b).** §8's *"only ~42% of AMDPARs name a section"* is measured under all four
and the four figures published. Retiring the sentence is the architect's call, not
this session's.

## 2. The per-document completeness restriction

`QUESTIONS.md` Q11's ruling: *"CH-03 proceeds on the per-document restriction that
was pre-registered BEFORE any of this — see plan.md CH-02's fallback."*

**Applied as a named rung of the exclusion ladder: FR documents whose per-document
completeness under `v11` is < 0.90 are excluded, with their count.** The ladder
publishes n **with and without** that rung, and the **restricted** set is the primary
eval set. That is the architect's ruling and it is fixed here, before the count is
known, precisely so that it cannot later be chosen for its effect on n.

## 3. Positives, negatives, and the matching rule

- **Positive:** a `(rule, section)` pair carrying a live codification-defect note.
- **Negative:** a sibling section amended by the **same FR document**, with **exactly
  the same instruction count**, carrying **no** defect note.
- **Tolerance is 0. It will not be relaxed for any n.** `CONTEXT.md` §8: unmatched, a
  hardcoded threshold on instruction count beats the agent. A ±1 figure is computed
  as a **diagnostic only** and is never the eval set.
- Where several siblings match, the negative is chosen by **sorted order, first
  element** — deterministic, declared, and independent of any label.

## 4. The point-in-time edition

**Edition = the latest annual edition whose revision date is STRICTLY BEFORE the
rule's publication date.** CFR statutory revision dates: titles 1–16 Jan 1;
17–27 Apr 1; 28–41 Jul 1; 42–50 Oct 1. Hand-computed cases are golden **G-A**.

Strictly-before is the point: an edition revised *on* the publication date could
already contain the amendment under test.

**If the required edition is not on govinfo** (coverage starts 1996; the current
year's edition is published months in arrears) the item is **excluded as a named
rung**, never silently substituted with a neighbouring year.

## 5. The leakage strips — and what would make them a lie

Strip and count `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>`, `<EAR>` before any text is frozen.

**Q8's trap is pre-registered here as a specific hazard with a specific defence.**
Element names are format-dependent: ECFR bulk XML has no `<SECTION>` element at all.
CH-03 reads **CFR annual editions**, where those four names are correct — but a
counter that prints zero because it is looking for the wrong name is indistinguishable
from a corpus that is genuinely clean.

**Therefore, declared before the run:**

1. **Every strip counter is asserted against a known-positive input** whose expected
   counts are hand-computed in `goldens.md` (**G-B**, real govinfo bytes). A zero is
   believed only after the counter has been shown to produce a non-zero.
2. **The leakage test must FAIL on unstripped input before it is accepted on stripped
   input.** Both states are demonstrated and both are committed.
3. **A second trap, found while reading the bytes and recorded before the code:** the
   volume `CFR-2024-title40-vol5.xml` contains **313 `<SECTION>` elements, of which 2
   are nested inside an `<EFFDNOTP>/<REVTXT>`** — a verbatim copy of the *pending
   amendment*, 24,455 characters of it for § 52.2320. A section lookup that takes any
   `<SECTION>` with a matching `<SECTNO>` can therefore return the leak itself.
   **Only a `<SECTION>` with no `EDNOTE`/`EFFDNOTP`/`REVTXT` ancestor is eligible.**
   Golden **G-E**.

**The test fails** if frozen text contains (a) any of the four elements, (b) the FR
citation of its own rule under test, or (c) any of the literals
`"could not be incorporated"`, `"Editorial Note"`, `"Effective Date Note"`,
`"set forth as follows"`.

## 6. Pre-registered branches on n — taken, not deliberated

From `prompts/NIGHT-RUN.md`, restated so the branch cannot be re-read after the fact:

| pairs | action |
|---|---|
| ≥ 42 | proceed |
| 30–42 | proceed; report the real n and state, in `GOOD.md` and the report, the effect size this sample can and cannot detect |
| < 30 | proceed with what exists; report it plainly as a documented shortfall. **Do not relax the match.** |
| leakage test cannot be made to FAIL on unstripped input | **the stripper is not proven.** BLOCKER in `QUESTIONS.md`, freeze nothing, move to CH-04 |

## 7. What is deliberately NOT done

- **No number in `data/ednotes/` or `data/amdpars/` is rewritten.** They are read-only
  (CH-01/CH-02 froze them). CH-03 **extends** `data/` with new directories.
- **`CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, `prompts/`
  and `context/` are not edited.** Anything that seems to require it is Class A and
  goes to `QUESTIONS.md`.
- **The CH-02 gate outcome is not revisited.** A stricter detector cannot raise a
  failing figure; the re-measurement is reported, and CH-02 stays in its
  `< 0.80` documented-failure branch whatever `v11` returns.
