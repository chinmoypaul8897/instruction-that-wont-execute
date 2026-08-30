# CH-01 goldens — hand-computed, committed BEFORE the parser exists

Hard rule 4: *"Hand-compute expected outputs **before** writing the code. A test whose
expected value came from the code it tests proves nothing."*

Every value below was read off the raw govinfo XML by eye, using `sed` / `grep` / `awk`
only — no parser, no project code. `src/harvest_ednotes.py` did not exist when this
file was committed; the commit that adds it is a **later** commit, so the ordering is
provable from git history rather than asserted here.

The four records were chosen to span the decision surface this chunk turns on:
a defect note inside a section (the usable case), a defect note inside an appendix
(the case the section-level rung excludes), an `<EDNOTE>` that is not a defect note at
all (the negative control — a filter that keeps this one is broken), and a defect note
carrying two FR citations (the case that decides what `fr_citation` means).

---

## The format, and one correction to the spec's element name

`CONTEXT.md` §8 and `prompts/CH-01.md` §2 both say an `<EDNOTE>` may sit "inside a
`<SECTION>` block". **There is no `<SECTION>` element in the ECFR bulk XML.** That name
belongs to the *CFR annual-edition* DTD, which is a different govinfo product — and the
one `CONTEXT.md`'s leakage measurement was in fact taken on (`CFR-2024-title40-vol5`).
CH-03 reads annual editions and will meet `<SECTION>` there; CH-01 reads ECFR bulk and
does not.

The ECFR bulk XML is a `DLPSTEXTCLASS` document whose structural containers are
numbered `DIV` elements carrying a `TYPE` attribute. Measured inventory, title 7:

| Container | `TYPE` | count in title 7 |
|---|---|---|
| `DIV1` | `TITLE` | 15 |
| `DIV3` | `CHAPTER` | 40 |
| `DIV4` | `SUBCHAP` | 45 |
| `DIV5` | `PART` | 548 |
| `DIV6` | `SUBPART` | 1,253 |
| `DIV7` | `SUBJGRP` | 1,324 |
| `DIV8` | **`SECTION`** | 17,205 |
| `DIV9` | `APPENDIX` | 144 |

**`<DIV8 TYPE="SECTION">` is the ECFR bulk spelling of `<SECTION>`.** The semantic test
the spec asks for — *section-level, not appendix/part* — is unchanged. Recorded as a
**Class B** deviation (implementation choice inside spec) in `PROGRESS.md`, and raised
as a documentation note in `QUESTIONS.md` so CH-03 does not inherit the wrong element
name for the format it actually reads.

## Declared normalisation level — hard rule 7

Note text is extracted at level **`whitespace-collapsed`**: every descendant text node
of `<EDNOTE>` is concatenated in document order, then all runs of whitespace (including
the newlines govinfo inserts inside elements) collapse to a single space and the result
is stripped. The level achieved is **carried in every record**, never applied silently.

Two text fields, because a single one is ambiguous. `</HED>` is immediately followed by
`<PSPACE>` with no separating character, so a naive whole-element concatenation yields
`Editorial Note:At 83 FR ...` — a missing space no reader would predict:

- **`hed`** — the text of the `<HED>` child alone.
- **`text`** — every descendant text node **except** those inside `<HED>`. This is the
  note itself, and it is what the `"could not be incorporated"` filter reads.

## FR citation

Pattern `\b(\d+)\s+FR\s+(\d+)\b`, all matches kept in document order. `fr_citation` is
the **first** match — the rule the note is about. A note may cite a second rule for
context (golden G4 is that shape), so the count of notes with more than one citation is
reported rather than hidden.

---

## G1 — defect note, section-level *(the usable case)*

**Source:** `data/raw/ecfr/ECFR-title7.xml`, `<EDNOTE>` opening at line **12514**.
Enclosing `<DIV8 N="§ 2.22" NODE="7:1.1.1.1.5.3.29.9" TYPE="SECTION">` opens at line
12089 and closes at 12516, immediately after the note. Enclosing
`<DIV5 N="2" NODE="7:1.1.1.1.5" TYPE="PART">` opens at line 9778.

| field | hand-computed expected value |
|---|---|
| `title` | `7` |
| `part` | `2` |
| `section` | `2.22` |
| `section_raw` | `§ 2.22` |
| `node` | `7:1.1.1.1.5.3.29.9` |
| `container_type` | `SECTION` |
| `section_level` | `true` |
| `hed` | `Editorial Note:` |
| `is_defect` | `true` |
| `fr_citation` | `83 FR 61311` |
| `fr_citations` | `["83 FR 61311"]` |
| `normalisation` | `whitespace-collapsed` |

`text`, verbatim at the declared level:

> At 83 FR 61311, Nov. 29, 2018, § 2.22 was amended by adding (a)(1)(xvi), however paragraph (a)(xvi) was not provided in the text, this amendment could not be incorporated due to inaccurate amendatory instruction.

---

## G2 — defect note, **appendix**-level *(the case the section-level rung excludes)*

**Source:** `data/raw/ecfr/ECFR-title7.xml`, `<EDNOTE>` opening at line **390151**.
Enclosing `<DIV9 N="" NODE="7:12.1.2.7.10.2.1.8.15" TYPE="APPENDIX">` opens at line
390111. Enclosing `<DIV5 N="1900" NODE="7:12.1.2.7.10" TYPE="PART">` opens at line
389709.

The appendix's `N` attribute is the **empty string** — its identity lives in its
`<HEAD>`, not its `N`. A parser that assumes `N` is populated breaks here, which is why
this record is pinned rather than described.

| field | hand-computed expected value |
|---|---|
| `title` | `7` |
| `part` | `1900` |
| `section` | `null` |
| `section_raw` | `` *(the empty string — the `N` attribute is empty)* |
| `node` | `7:12.1.2.7.10.2.1.8.15` |
| `container_type` | `APPENDIX` |
| `section_level` | `false` |
| `hed` | `Editorial Note:` |
| `is_defect` | `true` |
| `fr_citation` | `58 FR 52646` |
| `fr_citations` | `["58 FR 52646"]` |
| `normalisation` | `whitespace-collapsed` |

`text`, verbatim at the declared level:

> At 58 FR 52646, Oct. 12, 1993, the Farmers Home Administration attempted to amend exhibit C of subpart B of part 1900 by removing in the second paragraph the words “(month) ________,”; however, because “(month) ________” does not exist in the second paragraph, this amendment could not be incorporated.

---

## G3 — **not** a defect note *(negative control)*

**Source:** `data/raw/ecfr/ECFR-title11.xml`, `<EDNOTE>` opening at line **4504**.
Enclosing `<DIV8 N="§ 104.3" NODE="11:1.0.1.1.12.0.1.3" TYPE="SECTION">` opens at line
4160.

This is the boilerplate "List of CFR Sections Affected" pointer. It carries **no**
`"could not be incorporated"` and **no** FR citation. It is here because a filter that
admits it, or a citation extractor that invents a citation for it, is broken — and a
golden set of positives only cannot show that.

It also exercises the inline `<E T="04">Federal Register</E>` element: the extractor
must yield `For Federal Register citations`, one space either side of the italicised
words, not `ForFederal Registercitations`.

| field | hand-computed expected value |
|---|---|
| `title` | `11` |
| `part` | `104` |
| `section` | `104.3` |
| `section_raw` | `§ 104.3` |
| `node` | `11:1.0.1.1.12.0.1.3` |
| `container_type` | `SECTION` |
| `section_level` | `true` |
| `hed` | `Editorial Note:` |
| `is_defect` | **`false`** |
| `fr_citation` | `null` |
| `fr_citations` | `[]` |
| `normalisation` | `whitespace-collapsed` |

`text`, verbatim at the declared level:

> For Federal Register citations affecting § 104.3, see the List of CFR Sections Affected, which appears in the Finding Aids section of the printed volume and at www.govinfo.gov.

---

## G4 — defect note carrying **two** FR citations *(the first-match rule)*

**Source:** `data/raw/ecfr/ECFR-title7.xml`, `<EDNOTE>` body at line **231604**.
Enclosing `<DIV8 N="§ 981.467" NODE="7:8.1.1.1.23.3.334.9" TYPE="SECTION">` opens at
line 231582.

Pinned because it is the case that decides whether `fr_citation` means "the rule the
note is about" or "any FR number in the note". The amending rule is the **first**
citation; the second is the indefinite stay it collided with. Reading the last match,
or the only match, would attribute this defect to the wrong rule at CH-02.

| field | hand-computed expected value |
|---|---|
| `title` | `7` |
| `part` | `981` |
| `section` | `981.467` |
| `section_raw` | `§ 981.467` |
| `node` | `7:8.1.1.1.23.3.334.9` |
| `container_type` | `SECTION` |
| `section_level` | `true` |
| `is_defect` | `true` |
| `fr_citation` | `88 FR 82235` |
| `fr_citations` | `["88 FR 82235", "88 FR 67627"]` |

`text`, verbatim at the declared level:

> At 88 FR 82235, Nov. 24, 2023, § 981.467 was amended; however, the amendments could not be incorporated because the section was stayed indefinitely at 88 FR 67627, Oct. 2, 2023.

---

## Provenance of the raw files these goldens were read from

`data/raw/` is git-ignored and never tracked (`.gitignore:35`, proved with
`git check-ignore -v` before the first byte was downloaded). Both files are reproducible
from govinfo by `refetch.py`. Their announced sizes and last-modified stamps, as read
from `https://www.govinfo.gov/bulkdata/json/ECFR/title-N` on 2026-08-30:

| file | bytes | govinfo last-modified |
|---|---|---|
| `ECFR-title7.xml` | 41,335,479 | 28-Aug-2026 21:27 |
| `ECFR-title11.xml` | 1,673,499 | 09-Jun-2026 20:48 |
