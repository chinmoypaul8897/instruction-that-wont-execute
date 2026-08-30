# CH-02 goldens — hand-computed, committed BEFORE the attributor exists

Hard rule 4: *"Hand-compute expected outputs **before** writing the code. A test whose
expected value came from the code it tests proves nothing."*

Every value in the three tables below was read off the raw govinfo Federal Register
XML by eye, from `sed` / `grep` / `awk` output only — no parser, no project code.
`src/attribute_amdpars.py` did not exist when this file was committed; the commit that
adds it is a **later** commit, so the ordering is provable from `git log` rather than
asserted here. `docs/evidence/ch01-pool/goldens.md` did the same at CH-01.

The three documents were chosen to span the decision surface, as `prompts/CH-02.md` §2
directs:

| | FR document | shape it pins |
|---|---|---|
| **G1** | FR Doc **2020-11897**, `FR-2020-07-16.xml`, 85 FR 43124–43141 | **most instructions name their own section** — 24 of 28 — and they name it in the *word* form `Section 90.209`, not `§ 90.209` |
| **G2** | FR Doc **2021-02268**, `FR-2021-02-04.xml`, 86 FR 8113–8131 | **most instructions are lettered sub-instructions** — 17 of 29 — the shape `CONTEXT.md` §8's worked example is drawn from, § 1468.23 included |
| **G3** | FR Doc **2016-23968**, `FR-2016-10-04.xml`, 81 FR 68312–68317 | **redesignations**, two of them, plus nested roman sub-sub-instructions |

All three are in the CH-01 pool: G1 is cited by the defect notes at 85 FR 43138/43139
(47 CFR §§ 90.209, 90.210, 90.213), G2 by 86 FR 8130 (7 CFR § 1468.3), G3 by
81 FR 68317 (32 CFR § 236.2).

Raw inputs, pinned by hash:

```
80dcb94f3f22b3295ba992c0363d13ef5d88f3e22ef135a5a3625f3ec530f92b  FR-2020-07-16.xml
14c9889d5e243fc835e824fc9cb973a910baf2e3f1d98e4b785542286b5e3191  FR-2021-02-04.xml
6f36a7649c5ba30ebfe0c9297f9339845fd7351343940afc94d68b8baf5a7d05  FR-2016-10-04.xml
```

---

## 0. The format, and where the AMDPARs live

The FR bulk daily issue is a `FEDREG` document. `<AMDPAR>` elements sit at

```
FEDREG / RULES    / RULE    / SUPLINF / REGTEXT / AMDPAR   <- amendments (ours)
FEDREG / PRORULES / PRORULE / SUPLINF / ...     / AMDPAR   <- proposals (excluded)
```

**A "document" for the purposes of `CONTEXT.md` §8's completeness denominator is one
`<RULE>` element**, identified by the FR Doc number in its `<FRDOC>` child. AMDPARs
inside `<PRORULE>` are *proposed* amendments that never executed and are excluded
before the denominator is formed. `<REGTEXT>` carries `TITLE` and `PART` attributes.

A citation resolves to a document by page. Two independent routes, and this file
pre-registers that they must agree:

1. **`<CNTNTS>` route.** The front-matter contents pairs `<PGS>43124-43141</PGS>` with
   `<FRDOCBP>2020-11897</FRDOCBP>`. This is the published page range.
2. **`<PRTPAGE>` carry-forward route.** `<PRTPAGE P="n"/>` marks the point at which
   page *n* begins. A rule's pages are every numeric `PRTPAGE` inside it, plus the page
   in effect when the `<RULE>` element opened. Non-numeric values (the roman-numbered
   front matter, `P="vii"`) are dropped.

Verified by hand on `FR-2016-06-10.xml`, the first four rules of the issue:

| FR Doc | `<CNTNTS>` `<PGS>` | carry-forward `PRTPAGE` set | agree? |
|---|---|---|---|
| 2016-13545 | 37485–37488 | 37485, 37486, 37487, 37488 | yes |
| 2016-12324 | 37488–37492 | 37488 (carried in), 37489, 37490, 37491, 37492 | yes |
| 2016-13250 | 37492–37494 | 37492 (carried in), 37493, 37494 | yes |
| 2016-13372 | 37494–37496 | 37494 (carried in), 37495, 37496 | yes |

The second rule carries no `PRTPAGE` of its own before its `<SUBJECT>`; it begins on
the page the previous rule ended on. A resolver that took only the first `PRTPAGE`
*inside* a rule would place 2016-12324 at 37489 and miss a citation to 37488.

## 1. Declared normalisation level — hard rule 7

AMDPAR text is extracted at level **`whitespace-collapsed`**: every descendant text
node of `<AMDPAR>` is concatenated in document order, then all runs of whitespace
collapse to a single space and the result is stripped. The level achieved is carried
in every record, never applied silently.

**Descendant text, not direct text.** This is not a detail. Many AMDPARs open with an
`<E T="03">` italic run, so their *direct* text is the empty string:

```xml
<AMDPAR>e. Amend <E T="03">Section II.A.1 of Chapter 2</E> by removing the bullet ...
```

An extractor reading `element.text` alone returns `"e. Amend "` and loses the
instruction. Observed in `FR-2019-02-05.xml` (84 FR 1606, 12 CFR § 702.304), where
several of the 156 AMDPARs begin with an element rather than a character. This is the
`<AMDPAR>`-shaped instance of `QUESTIONS.md` **Q8**, and §8 of this file records the
known-positive assertion that guards it.

## 2. The parse rules, fixed here before any code — hard rule 4

`CONTEXT.md` §8 gives the algorithm and the field meanings but not the tokenisation.
These seven rules are the tokenisation, pre-registered so that the tables in §3–§5 are
predictions rather than transcriptions.

**P1 — quoted spans are lifted out first.** A *quoted span* is text between `“` and the
next `”` (or between a pair of straight `"`). An unclosed `“` closes at end of text and
the element is counted in `unclosed_quote`. The **anchor** is the first quoted span;
all spans are kept in `anchors`. Section, operation and designation are then searched
in the **de-quoted** text, so that a cross-reference being *inserted* — `add the cross
reference “paragraph (a)(5)”` — can never be mistaken for the paragraph being amended.

**P2 — the section citation.** `CONTEXT.md` §8 specifies `§\s*[\d.]+[a-z]?`. Applied
literally that regex truncates every title-26 section number: `§ 1.367(a)-8` becomes
`1.367`, and truncation in exactly this position is what `CONTEXT.md` §8 records as
having produced 0.46 completeness once already. The pre-registered pattern is
therefore the base `\d+[A-Za-z]?\.\d+[A-Za-z0-9]*`, followed by a
`(\([A-Za-z0-9]+\))*-\d+[A-Za-z0-9]*` suffix **only when the `-N` tail is present**.

The `-N` condition is what keeps `§ 90.213(a)` — section 90.213, paragraph (a) — from
being read as a section named `90.213(a)`, while still reading `§ 1.401(a)(31)-1` whole.
Hand-checked against every section shape in the CH-01 pool:

| citation | base | absorbs | section |
|---|---|---|---|
| `§ 1468.3` | `1468.3` | — | `1468.3` |
| `§ 90.213(a)` | `90.213` | no `-N` tail, so no | `90.213` (+ designation `(a)`) |
| `§ 1.367(a)-8` | `1.367` | `(a)-8` | `1.367(a)-8` |
| `§ 1.1400Z2(b)-1` | `1.1400Z2` | `(b)-1` | `1.1400Z2(b)-1` |
| `§ 1.401(a)(31)-1` | `1.401` | `(a)(31)-1` | `1.401(a)(31)-1` |
| `§ 1.199A-0` | `1.199A` | `-0` | `1.199A-0` |
| `§ 1.1502-47` | `1.1502` | `-47` | `1.1502-47` |
| `§ 210.8-01` | `210.8` | `-01` | `210.8-01` |
| `§ 6.302-1` | `6.302` | `-1` | `6.302-1` |

**P3 — two section detectors, both reported, neither substituted for the other.**

- **`spec_literal`** — the citation of P2 must be introduced by `§`. This is
  `CONTEXT.md` §8's own rule and it is the one the gate branch is taken on.
- **`extended`** — `§`, **or** the word form `Section 90.209` / `Sections 90.209 and
  90.210`.

They are not a strict/loose pair. On G1 the spec-literal detector does not merely miss
sections, it **mis-attributes**: 24 of 28 elements name their section in the word form,
so `current_section` stays pinned at `1.9005` — set by the one element that used `§` —
and 20 elements are carried forward onto a section they have nothing to do with. Both
figures are computed, both ship, and the divergence is raised for the architect in
`QUESTIONS.md` **Q9**. Nothing is silently substituted (hard rule 3).

When more than one section is named, `current_section` becomes the **first**, and all
are kept in `sections_named` — the same rule CH-01 fixed for `fr_citation`.

**P4 — the operation.** One of `revise · add · remove · redesignate · amend`, matched
on word stems in the de-quoted text. `amend` is a **fallback, not a first match**: FR
drafting convention subordinates the real verb to it — *"Amend § 236.1 by revising the
last two sentences"* is a revision, not an amendment. So:

> operation = the first of `{revise, add, remove, redesignate}` to appear, scanning
> left to right; if none appears and `amend` does, operation = `amend`; otherwise
> operation is **null** and the element cannot be complete.

Stems: `revis(e|es|ed|ing|ion)` · `add(|s|ed|ing)` · `remov(e|es|ed|ing|al)` ·
`redesignat(e|es|ed|ing|ion)` · `amend(|s|ed|ing|ment|ments|atory)`.

**P5 — the designation.** The first run of one or more consecutive
`\([A-Za-z0-9]{1,4}\)` groups in the de-quoted text, with the span matched as a section
by P2 excluded. The four-character content limit is what stops prose parentheses:
`“forms of agreements ( e.g., contracts, grants, ...)”` in G3 does not match, and nor
does `pursuant to 16 U.S.C. 3835(f)` reach the front of G2 element 29, where
`in paragraph (c)(2)` appears earlier.

**P6 — completeness, read as `CONTEXT.md` §8 writes it.**

> completeness = (AMDPAR elements attributed to a section **and** parsed into at least
> one complete `(operation, anchor OR designation)` triple) ÷ (total AMDPAR elements in
> the document)

"At least one" is read as: the element has an operation **and** at least one anchor or
at least one designation. Three consequences are visible in the tables below and none
of them is a bug to be tuned away:

- an **authority citation** — *"The authority citation for part 90 continues to read as
  follows"* — has no operation and no designation, and counts as incomplete;
- a **lead-in** — *"Amend § 236.2 by:"* — names the section and carries the specifics
  in its lettered children, so it is attributed but incomplete;
- a **whole-section operation** — *"Section 90.601 is revised to read as follows"* —
  has an operation but no paragraph path and no quoted anchor, and is incomplete.

Because these three shapes are structural, the completeness ceiling is set by the
corpus, not by the parser. That is a measurement, and §6 below states what this file
predicts it to be **before** the measurement is run.

**P7 — `current_section` resets at each `<RULE>` boundary and nowhere else.**
`CONTEXT.md` §8 says "iterate in document order" and specifies no other reset, so none
is added. Carrying a section across a `<REGTEXT>` `PART` change is therefore possible
and, where it happens, wrong; the count of elements whose attributed section's part
differs from the enclosing `REGTEXT/@PART` ships as the diagnostic `part_mismatch`
rather than being silently repaired.

---

## 3. G1 · FR Doc 2020-11897 — 28 AMDPARs, section named in the word form

`awk` slice: `FR-2020-07-16.xml` lines 1619–3165. 47 CFR parts 1, 2, 20, 27, 90.

Attribution below is under the **`extended`** detector. The `spec_literal` result is
given after the table because the two disagree on most elements, which is the whole
reason this document was chosen.

| # | instruction (truncated) | names | section | operation | anchor | desig. | complete |
|---:|---|---|---|---|---|---|:--:|
| 1 | 1. The authority citation for part 1 continues… | — | *(null)* | — | — | — | **unattributable** |
| 2 | 2. Section 1.907 is amended by revising the definition of “covered geographic licenses”… | 1.907 | 1.907 | revise | covered geographic licenses | — | yes |
| 3 | 3. In § 1.9005 add paragraph (nn)… | 1.9005 | 1.9005 | add | — | (nn) | yes |
| 4 | 4. The authority citation for part 2 continues… | — | 1.9005 | — | — | — | no |
| 5 | 5. Section 2.106 is amended by revising pages 31 and 32… | 2.106 | 2.106 | revise | — | — | no |
| 6 | 2.106 Table of Frequency Allocations. | — | 2.106 | — | — | — | no |
| 7 | 6. The authority citation for part 20 continues… | — | 2.106 | — | — | — | no |
| 8 | 7. Section 20.12 is amended by revising paragraph (a)(1)… | 20.12 | 20.12 | revise | — | (a)(1) | yes |
| 9 | 8. The authority citation for part 27 continues… | — | 20.12 | — | — | — | no |
| 10 | 9. Section 27.1 is amended by adding paragraph (b)(16)… | 27.1 | 27.1 | add | — | (b)(16) | yes |
| 11 | 10. Section 27.5 is amended by adding paragraph (n)… | 27.5 | 27.5 | add | — | (n) | yes |
| 12 | 11. Section 27.12 is amended by revising paragraph (a)… | 27.12 | 27.12 | revise | — | (a) | yes |
| 13 | 12. Section 27.13 is amended by adding paragraph (n)… | 27.13 | 27.13 | add | — | (n) | yes |
| 14 | 13. Add subpart P to read as follows: | — | 27.13 | add | — | — | no |
| 15 | 14. The authority citation for part 90 continues… | — | 27.13 | — | — | — | no |
| 16 | 15. Section 90.7 is amended by adding definitions for “900 MHz broadband,”… | 90.7 | 90.7 | add | 900 MHz broadband, | — | yes |
| 17 | 16. Section 90.35 is amended by revising paragraph (c)(71)… | 90.35 | 90.35 | revise | — | (c)(71) | yes |
| 18 | 17. Section 90.205 is amended by revising paragraph (k)… | 90.205 | 90.205 | revise | — | (k) | yes |
| 19 | 18. Section 90.209 is amended by revising the heading to the table in paragraph (b)(5)… “896-901/935-940” | 90.209 | 90.209 | revise | 896-901/935-940 | (b)(5) | yes |
| 20 | 19. Section 90.210 is amended by revising the heading to the table, relocating it… “896-901/935-940” | 90.210 | 90.210 | revise | 896-901/935-940 | — | yes |
| 21 | 20. Section 90.213 is amended by revising the heading to the table in paragraph (a)… “896-901” | 90.213 | 90.213 | revise | 896-901 | (a) | yes |
| 22 | 21. Section 90.601 is revised to read as follows: | 90.601 | 90.601 | revise | — | — | no |
| 23 | 22. Section 90.603 is amended by revising the introductory text… | 90.603 | 90.603 | revise | — | — | no |
| 24 | 23. Section 90.613 is amended by revising the introductory text… | 90.613 | 90.613 | revise | — | — | no |
| 25 | 24. Add § 90.616 to read as follows: | 90.616 | 90.616 | add | — | — | no |
| 26 | 25. Section 90.617 is amended by revising the introductory text of paragraphs (c) and (f)… | 90.617 | 90.617 | revise | — | (c) | yes |
| 27 | 26. Section 90.619 is amended by revising paragraphs (b)(1) introductory text… | 90.619 | 90.619 | revise | — | (b)(1) | yes |
| 28 | 27. Section 90.672 is revised to read as follows: | 90.672 | 90.672 | revise | — | — | no |

**G1 hand-computed totals — `extended`:** attributed 27, unattributable 1,
complete **15**, incomplete 13. **completeness = 15 / 28 = 0.5357**.

**G1 hand-computed totals — `spec_literal`:** only elements 3 and 25 introduce their
section with `§`. `current_section` is null for elements 1–2 (**2 unattributable**),
`1.9005` for elements 4–24, and `90.616` for elements 26–28. Elements 8, 10, 11, 12,
13, 16, 17, 18, 19, 20, 21, 26 and 27 still parse into a complete triple, and every one
of those 13 is now attributed to a section it does not amend. Element 2, complete under
`extended`, becomes unattributable. **completeness = 13 / 28 = 0.4643, and every
completed element under it is a wrong attribution.**

*Element 6, `<AMDPAR>2.106 Table of Frequency Allocations.</AMDPAR>`, is an upstream
mis-tag: a section heading marked up as an amendatory instruction. It is attributable,
carries no operation, and is counted incomplete. It is kept in the denominator — the
denominator is "total AMDPAR elements", and a parser that drops the elements it cannot
read is the parser this project exists to catch.*

## 4. G2 · FR Doc 2021-02268 — 29 AMDPARs, mostly lettered sub-instructions

`awk` slice: `FR-2021-02-04.xml` lines 816–2076. 7 CFR part 1468. Both detectors agree
on every element: every lead-in uses `§`.

| # | instruction (truncated) | names | section | operation | anchor | desig. | complete |
|---:|---|---|---|---|---|---|:--:|
| 1 | 1. The authority citation for part 1468 continues… | — | *(null)* | — | — | — | **unattributable** |
| 2 | 2. Amend § 1468.3 as follows: | 1468.3 | 1468.3 | amend | — | — | no |
| 3 | a. In the definition of “Beginning farmer or rancher”: | — | 1468.3 | — | Beginning farmer or rancher | — | no |
| 4 | i. In paragraph (1), remove the words “farm or ranch or”… | — | 1468.3 | remove | farm or ranch or | (1) | yes |
| 5 | ii. In paragraphs (2) and (3), remove the words “farm or ranch”… | — | 1468.3 | remove | farm or ranch | (2) | yes |
| 6 | b. In the definition of “Eligible land”, add the word “land”… | — | 1468.3 | add | Eligible land | — | yes |
| 7 | c. In the definition of “Farm or ranch succession plan”, remove… | — | 1468.3 | remove | Farm or ranch succession plan | — | yes |
| 8 | d. In the definition of “Future viability”, add the words… | — | 1468.3 | add | Future viability | — | yes |
| 9 | e. In the second sentence in the definition of “Maintenance”, add… | — | 1468.3 | add | Maintenance | — | yes |
| 10 | 3. Amend § 1468.6 in paragraph (a)(3)(iii) by removing the cross reference “paragraph (a)(4)”… | 1468.6 | 1468.6 | remove | paragraph (a)(4) | (a)(3)(iii) | yes |
| 11 | 4. Amend § 1468.20 in paragraph (b)(1)(ii) by adding the word “demonstrated”… | 1468.20 | 1468.20 | add | demonstrated | (b)(1)(ii) | yes |
| 12 | 5. Amend § 1468.22 as follows. | 1468.22 | 1468.22 | amend | — | — | no |
| 13 | a. Revise paragraph (b)(11); and | — | 1468.22 | revise | — | (b)(11) | yes |
| 14 | b. In paragraph (c)(2), add the word “annually”… | — | 1468.22 | add | annually | (c)(2) | yes |
| 15 | 6. Amend § 1468.23 as follows: | 1468.23 | 1468.23 | amend | — | — | no |
| 16 | a. In paragraph (b)(1), remove the words “Up to”… | — | 1468.23 | remove | Up to | (b)(1) | yes |
| 17 | b. In paragraph (b)(2), remove the words “Up to”… | — | 1468.23 | remove | Up to | (b)(2) | yes |
| 18 | 7. In § 1468.24 revise paragraphs (b)(2)(i), (iii), and (iv)… | 1468.24 | 1468.24 | revise | — | (b)(2)(i) | yes |
| 19 | 8. In § 1468.25 revise paragraphs (c) and (d)(4)… | 1468.25 | 1468.25 | revise | — | (c) | yes |
| 20 | 9. Amend § 1468.26 in paragraph (b)(1) by removing the words “up to”… | 1468.26 | 1468.26 | remove | up to | (b)(1) | yes |
| 21 | 10. Amend § 1468.27 as follows: | 1468.27 | 1468.27 | amend | — | — | no |
| 22 | a. In paragraph (c)(1), add the words “the purchase of the land”… | — | 1468.27 | add | the purchase of the land | (c)(1) | yes |
| 23 | b. In paragraphs (c)(3)(ii) and (c)(4), add the words “of the land”… | — | 1468.27 | add | of the land | (c)(3)(ii) | yes |
| 24 | b. Redesignate paragraphs (e)(4)(iii) and (iv) as paragraphs (e)(4)(iv) and (v); | — | 1468.27 | **redesignate** | — | (e)(4)(iii) | yes |
| 25 | c. Add a new paragraph (e)(4)(iii). | — | 1468.27 | add | — | (e)(4)(iii) | yes |
| 26 | 11. Amend § 1468.28 as follows: | 1468.28 | 1468.28 | amend | — | — | no |
| 27 | a. Revise paragraph (c); and | — | 1468.28 | revise | — | (c) | yes |
| 28 | b. In paragraph (f), add the words “in whole or in in part,”… | — | 1468.28 | add | in whole or in in part, | (f) | yes |
| 29 | 12. Amend § 1468.32 in paragraph (c)(2) by adding the words “or land under a CRP contract…” | 1468.32 | 1468.32 | add | or land under a CRP contract … and such land | (c)(2) | yes |

**G2 hand-computed totals:** attributed 28, unattributable 1, complete **22**,
incomplete 7. **completeness = 22 / 29 = 0.7586**.

*Elements 23 and 24 are both lettered `b.` — an upstream enumeration error inside
instruction 10. It changes nothing: carry-forward attributes on position, not on the
letter, which is precisely why `CONTEXT.md` §8 says order is the whole mechanism.*

*Element 29's anchor spans the phrase containing `16 U.S.C. 3835(f)`. Under P5 the
designation is taken from the de-quoted text, where `in paragraph (c)(2)` is the only
candidate — the statutory `(f)` sits inside the quoted span and never reaches the
designation search.*

## 5. G3 · FR Doc 2016-23968 — 40 AMDPARs, two redesignations

`awk` slice: `FR-2016-10-04.xml` lines 2458–2944. 32 CFR part 236. Both detectors agree
on every element.

| # | instruction (truncated) | names | section | operation | anchor | desig. | complete |
|---:|---|---|---|---|---|---|:--:|
| 1 | 1. The authority citation is revised to read as follows: | — | *(null)* | revise | — | — | **unattributable** |
| 2 | 2. Amend § 236.1 by revising the last two sentences in the section… | 236.1 | 236.1 | revise | — | — | no |
| 3 | 3. Amend § 236.2 by: | 236.2 | 236.2 | amend | — | — | no |
| 4 | a. Revising the definition of “Covered contractor information system”. | — | 236.2 | revise | Covered contractor information system | — | yes |
| 5 | b. Revising the definition of “Covered defense information”. | — | 236.2 | revise | Covered defense information | — | yes |
| 6 | c. Revising the definition of “Cyber incident”. | — | 236.2 | revise | Cyber incident | — | yes |
| 7 | d. Revising the definition of “DIB participant”. | — | 236.2 | revise | DIB participant | — | yes |
| 8 | e. Removing “DoD-DIB CS information sharing program” and adding… | — | 236.2 | remove | DoD-DIB CS information sharing program | — | yes |
| 9 | f. Removing “Contractor” and adding in its place “contractor”… | — | 236.2 | remove | Contractor | — | yes |
| 10 | 4. Amend § 236.3 by: | 236.3 | 236.3 | amend | — | — | no |
| 11 | a. In paragraph (b)(1), removing “DoD-DIB CS information sharing program”… | — | 236.3 | remove | DoD-DIB CS information sharing program | (b)(1) | yes |
| 12 | b. In paragraph (c), removing “DoD-DIB CS information sharing program”… | — | 236.3 | remove | DoD-DIB CS information sharing program | (c) | yes |
| 13 | 5. Amend § 236.4 by: | 236.4 | 236.4 | amend | — | — | no |
| 14 | a. In paragraph (a), removing “applicable agreements”… | — | 236.4 | remove | applicable agreements | (a) | yes |
| 15 | b. In paragraph (d), removing “, as appropriate”… | — | 236.4 | remove | , as appropriate | (d) | yes |
| 16 | c. In paragraph (e), removing “ http://iase.disa.mil/pki/eca/certificate.html”… | — | 236.4 | remove | (the URL, leading space included) | (e) | yes |
| 17 | d. In paragraph (m)(4), adding “non-attributional cyber threat information”… | — | 236.4 | add | non-attributional cyber threat information | (m)(4) | yes |
| 18 | e. Redesignating paragraphs (n) through (p) as paragraphs (o) through (q). | — | 236.4 | **redesignate** | — | (n) | yes |
| 19 | f. Redesignating paragraph (m)(6) as paragraph (n). | — | 236.4 | **redesignate** | — | (m)(6) | yes |
| 20 | 6. Amend § 236.5 by: | 236.5 | 236.5 | amend | — | — | no |
| 21 | a. Revising the section heading. | — | 236.5 | revise | — | — | no |
| 22 | b. In paragraph (a), removing “DoD-DIB CS information sharing program”… | — | 236.5 | remove | DoD-DIB CS information sharing program | (a) | yes |
| 23 | c. In paragraph (b), removing “DoD-DIB CS information sharing program”… | — | 236.5 | remove | DoD-DIB CS information sharing program | (b) | yes |
| 24 | d. Revising paragraph (d). | — | 236.5 | revise | — | (d) | yes |
| 25 | e. In paragraph (g), removing “DoD-DIB CS information sharing program”… | — | 236.5 | remove | DoD-DIB CS information sharing program | (g) | yes |
| 26 | 7. Amend § 236.6 by: | 236.6 | 236.6 | amend | — | — | no |
| 27 | a. Revising the section heading. | — | 236.6 | revise | — | — | no |
| 28 | b. In paragraph (a): | — | 236.6 | — | — | (a) | no |
| 29 | i. Removing “DoD-DIB CS information sharing program”… in the first sentence. | — | 236.6 | remove | DoD-DIB CS information sharing program | — | yes |
| 30 | ii. Removing “DoD-DIB CS information sharing program”… in the second sentence. | — | 236.6 | remove | DoD-DIB CS information sharing program | — | yes |
| 31 | c. In paragraph (c), removing… | — | 236.6 | remove | DoD-DIB CS information sharing program | (c) | yes |
| 32 | d. In paragraph (d), removing… | — | 236.6 | remove | DoD-DIB CS information sharing program | (d) | yes |
| 33 | e. In paragraph (e), removing… | — | 236.6 | remove | DoD-DIB CS information sharing program | (e) | yes |
| 34 | f. In paragraph (g), removing… | — | 236.6 | remove | DoD-DIB CS information sharing program | (g) | yes |
| 35 | 8. Amend § 236.7 by: | 236.7 | 236.7 | amend | — | — | no |
| 36 | a. Revising the section heading. | — | 236.7 | revise | — | — | no |
| 37 | b. In paragraph (a) introductory text, removing… | — | 236.7 | remove | DoD-DIB CS information sharing program | (a) | yes |
| 38 | c. In paragraph (a)(1), adding “to at least the Secret level” after “FCL.” | — | 236.7 | add | to at least the Secret level | (a)(1) | yes |
| 39 | d. In paragraph (a)(2), removing… | — | 236.7 | remove | DoD-DIB CS information sharing program | (a)(2) | yes |
| 40 | e. In paragraph (a)(3)(iii), removing… | — | 236.7 | remove | DoD-DIB CS information sharing program | (a)(3)(iii) | yes |

**G3 hand-computed totals:** attributed 39, unattributable 1, complete **28**,
incomplete 12. **completeness = 28 / 40 = 0.7000**.

*Element 28, `b. In paragraph (a):`, has a designation and no operation. It is the
mirror image of element 21, which has an operation and no designation. Both are
incomplete, and the definition in `CONTEXT.md` §8 requires exactly that: the operation
is mandatory, and one of anchor/designation must join it.*

*Element 1 is the only AMDPAR in G3 that carries an operation yet is still not counted:
`current_section` is null when it is read, so it is **unattributable**, and §8's
numerator requires attribution before parsing is even considered.*

---

## 6. What this file predicts, before the measurement runs

Recorded here so that §7's measured numbers can be checked against a prediction made
without sight of them, and so that a reviewer can see whether the outcome was reasoned
to or rationalised from.

1. **Attribution will be near-total; completeness will not.** Under carry-forward the
   only unattributable elements are those preceding the first named section in a
   document — one per document in all three goldens. Expect **global attribution above
   0.95**. The loss is in the *parse* half of §8's numerator, not the attribution half,
   and that is a different failure from the predecessor pilot's 0.46.
2. **Global completeness will land near 0.70, and below 0.90.** The three goldens give
   0.536, 0.759 and 0.700 on 97 hand-read elements. G1 was chosen as a hard case and
   should sit below the corpus; G2 and G3 are ordinary. **The prediction is
   [0.65, 0.80).**
3. **Therefore the `< 0.80` pre-registered branch is expected to fire**, and under
   `prompts/CH-02.md` §4 that makes the attributor *a documented failure that is
   reported, not tuned*. Writing the expectation down before the run is what stops the
   parse rules in §2 from being quietly relaxed once the number appears. **No rule in
   §2 may be changed after §7 is measured.** If one is found to be wrong, the change
   ships as a probe that flips (hard rule 6) with both numbers published.
4. **`spec_literal` will sit below `extended`**, and the gap will be concentrated in
   FCC- and SEC-style documents that write `Section 90.209`. On G1 the gap is 0.464 vs
   0.536, with every completed element under `spec_literal` mis-attributed.

## 7. The known-positive assertion for the extractor — `QUESTIONS.md` Q8

Q8's binding instruction is that *"a strip counter that reports zero may simply be
looking for the wrong element name … every counter must be asserted against a
known-positive input before any zero it prints is believed."* The AMDPAR extractor is
the same class of counter, so the same guard applies, and it is pre-registered here
rather than invented after a zero appears:

- **the element name is `AMDPAR` in the FR bulk DTD** — 64 in `fr20240103.xml`, 28 / 29
  / 40 in the three goldens above, all counted by `grep -c '<AMDPAR>'` with no parser;
- **the parser's per-document AMDPAR count must equal a plain text `grep` count of the
  open tag over the same byte range**, and the suite asserts it — parser and dumb text
  sweep can only disagree if elements are dropped or duplicated;
- **`extract_text` must return the full instruction for an AMDPAR whose first child is
  an element**, not the empty string — asserted on the `<E T="03">` case quoted in §1;
- **a zero AMDPAR count for a document is only accepted when the `grep` count is also
  zero**, which is the honest case of a rule that amends nothing (a delegation of
  authority, a technical correction to a preamble).

## 8. Measured

Generated by `ch02_attributor.py`; full output in `ch02-attributor-run.txt`, tables in
`completeness.md` and `pair-yield.md`. **Nothing in §§0–7 above was edited after these
numbers appeared.** Where a hand value turned out to be wrong it is corrected in the
ERRATA below, never in place.

### The three goldens reproduce

| | hand-computed, §§3–5 | measured | Δ |
|---|---:|---:|---:|
| G1 `extended` | 15 / 28 = 0.5357 | **15 / 28 = 0.5357** | +0 |
| G1 `spec_literal` | 13 / 28 = 0.4643 | **14 / 28 = 0.5000** | **+1 — ERRATUM E1** |
| G2 | 22 / 29 = 0.7586 | **22 / 29 = 0.7586** | +0 |
| G3 | 28 / 40 = 0.7000 | **28 / 40 = 0.7000** | +0 |

Every element of every hand table — section, operation, anchor, designation, complete —
reproduces. The one divergence is in a *prose* sub-claim about the secondary detector,
not in a table, and it is written up as E1.

### The corpus

| | `spec_literal` | `extended` |
|---|---:|---:|
| completeness | **0.5080** (4446 / 8752) | **0.6643** (5814 / 8752) |
| attribution rate | 0.7613 | **0.9865** |
| parse rate | 0.6672 | 0.6672 |
| unattributable | 2089 | 118 |

85 of 85 citations resolved, into 70 distinct FR documents. **Both figures land in the
`< 0.80` branch: the attributor is a documented failure, reported and not tuned.**

### The predictions in §6, scored

| # | predicted | measured | held? |
|---|---|---|:--:|
| 1 | attribution above 0.95; the loss is in the parse half, not the attribution half | `extended` attribution **0.9865**, parse **0.6672** | yes |
| 2 | global completeness in **[0.65, 0.80)** | `extended` **0.6643** | yes |
| 3 | the `< 0.80` branch fires | it fired, on both detectors | yes |
| 4 | `spec_literal` sits below `extended` | 0.5080 vs 0.6643 | yes |

### The pair yield

51 of 85 defect sections have at least one **exact** count-matched sibling.
**YIELD = 0.6000 · PROJECTED PAIRS = 51 · target 42 · CLEARS at 1.21×.** Under ±1
matching the yield is 0.6824 and the pairs 58; that rule is reported and **not adopted**.

---

## ERRATA — recorded, not corrected in place

### E1 · G1's `spec_literal` total was hand-counted as 13; it is 14

§3 predicted `spec_literal` completeness of **13 / 28 = 0.4643** and asserted that
*"every completed element under it is a wrong attribution."* Measured: **14 / 28 =
0.5000**, and **13 of the 14 are wrong attributions, not 14 of 14.**

The cause is an enumeration slip in the prose, not an error in a parse rule. The
prose listed elements 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 26 and 27 and omitted
**element 3**, *"In § 1.9005 add paragraph (nn)"* — the one element in the document that
introduces its section with the sign, and therefore the one element `spec_literal`
attributes **correctly**. It is complete under both detectors.

The correction makes the sign-only detector look very slightly *better*, which is worth
saying plainly: the erratum does not flatter the fix. `spec_literal` still mis-attributes
20 of G1's 28 elements and still sits below `extended` on the corpus, 0.5080 to 0.6643.

`tests/test_attribute_amdpars.py::test_live_golden_G1_reproduces_and_pins_the_detector_divergence`
asserts the measured 14 and names this erratum.

### E2 · §0 pre-registered that the two page-resolution routes "must agree". They do not

§0 said the `<CNTNTS>` route and the `<PRTPAGE>` route *"must agree"*, and verified it
on four rules of one issue. On the full 85 they disagree **twice**, and both times the
route §0 listed **first** — the contents index — is the wrong one:

- **79 FR 24198** → contents gives FR Doc `2014-08743`, the *Federal Acquisition
  Circular 2005-73* cover document: **0 AMDPARs**. The rule that actually amends
  48 CFR § 6.302-1 is `2014-08744`, with **838**. govinfo lists a circular in the
  contents as one entry spanning the page range of every rule inside it.
- **90 FR 52865** → contents gives `2025-20827` (2 AMDPARs, pages 52858–52860); the
  rule amending 30 CFR § 887.11 is `2025-20831` (16 AMDPARs, pages 52862–52865).

Two further citations resolved to **nothing**: an editorial note's date is the date the
rule was **filed**, not published, and the two differ by a day in *either* direction —
85 FR 43138 is noted 2020-07-15 and published 2020-07-16; 87 FR 31688 is noted
2022-05-25 and published 2022-05-24.

**The fix, and why it is not tuning.** A citation carries three exact keys — volume,
page and **section**. `resolve_citation` gathers every candidate either route admits and
prefers the one whose AMDPARs actually attribute to the cited section; where that does
not separate them the per-`<RULE>` PRTPAGE route wins over the editorial index; and when
nothing in the noted issue matches, **both** neighbouring days are tried and a neighbour
is accepted only on a section match. Using a third exact key is not a heuristic, and the
change moves no completeness figure into a kinder branch — 0.5080 / 0.6643 before and
after, the same `< 0.80` branch either way.

Both states are kept forever in `ch02_probe_resolution.py` and
`ch02-probe-resolution.txt`, and in two live tests (hard rule 6).

## 9. Found after the measurement, and deliberately NOT fixed

§6 states: *"No rule in §2 may be changed after §7 is measured."* Two section-citation
spellings turned up in the corpus that §2's detectors do not read. **Neither detector was
changed.** They are recorded here, counted, and raised for the architect as
`QUESTIONS.md` Q10.

| finding | elements | documents | effect |
|---|---:|---:|---|
| a section cited as `46 CFR 356.3` — no `§`, no the word *Section* | 9 | 1 (`2026-11267`) | all **27** AMDPARs of that document are unattributable; it is the only document in the corpus with zero attributed sections |
| a table-driven amendment — *"For each section and paragraph indicated in the left column of the following table…"* — where the sections live in a `<GPOTABLE>` and not in the AMDPAR text at all | 26 | 1 (`2024-18445`) | 4 defect sections in that document have no AMDPAR attributed to them |

Adding a `NN CFR X.Y` detector would recover at most 27 of 8752 elements — **under 0.31
percentage points**, nowhere near the 0.80 branch boundary. It is declined anyway,
because the value of a pre-registration is exactly that it is not revised once the
number is in view, and 0.31 points is a cheap price for keeping that intact. The
architect can adopt it at CH-03 with both numbers already on the table.
