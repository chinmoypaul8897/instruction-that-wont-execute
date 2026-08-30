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

---

## ERRATUM — appended 2026-08-30, after the parser was written

Recorded here rather than by editing the tables above. Hard rule 5 forbids moving a
golden after seeing a result, and that includes moving one quietly to agree with the
code it was written to test. **Nothing in G1–G4 above has been altered.** This section
records where the implementation and the pre-registered expectation diverged, what was
done, and why the load-bearing values are unaffected.

### E1 — `section_raw` on G2: `""` pre-registered, `None` produced

**G2 above pre-registers `section_raw` as the empty string**, reading the field as
"the container's `N` attribute" — the appendix's `N` is genuinely `N=""`, which is the
observation the golden was pinned for.

`src/harvest_ednotes.py` implements `section_raw` with the narrower meaning **"the `N`
of the enclosing `SECTION` container"**. Golden G2 has no `SECTION` ancestor at all, so
the field is `None`, not `""`.

| | G2 as pre-registered | As implemented |
|---|---|---|
| `section` | `null` | `null` — **agree** |
| `section_level` | `false` | `false` — **agree** |
| `container_type` | `APPENDIX` | `APPENDIX` — **agree** |
| `section_raw` | `""` | `None` — **diverge** |

**The two load-bearing values agree.** `section` and `section_level` decide whether a
note enters the pool, and both readings answer "no section here" identically. The
divergence is confined to how *absence* is spelled.

**Resolution — carry both, delete neither.** A field `container_n` was added: the `N`
of the nearest structural container whatever its type. For G2 that is `""`, exactly as
pre-registered. `section_raw` keeps its narrower meaning and stays `None`. The test
`test_golden_g2_defect_note_in_appendix_is_not_section_level` now asserts **both**
values, so neither reading can drift unnoticed:

```python
assert r["section_raw"] is None      # no enclosing SECTION container at all
assert r["container_n"] == ""        # the appendix's own N, as G2 recorded it
```

Collapsing the two into one field would lose the distinction between *no section* and
*a section with no number*, and the second of those is a shape this corpus can produce.

### E2 — a second reading of "section-level", found while checking the reference

Not a golden divergence; recorded here because it is the same class of thing and the
goldens are where a reader looks for definitions.

`prompts/CH-01.md` step 5 defines section-level as *"not appendix/part"* — a question
about the note's **container**, which is what G1 (`true`) and G2 (`false`) pin. On the
nine reference titles that reading gives **36**, against `CONTEXT.md` §8's **38**.

`CONTEXT.md` §8's own table resolves it: its rows *Section-level 38/44* and *Localise
below section level 6/44* sum to 44, so its 38 counts notes that **localise to a named
section** wherever they physically sit. Under that reading the re-derived figure is
**38 — the reference exactly**. The two notes in the gap are title 40 part 63 (in an
`APPENDIX`) and title 49 part 383 (at `PART` level), each naming its section in prose.

A field `names_section` now carries the second reading. **The pool gate is computed on
the container reading — the smaller of the two.** Working shown in
`exclusion-ladder.md`.

### E3 — `<DIV1 N=...>` is the volume index, not the title number

Found by a check that was expected to print `0` and printed `2428`. The title of a
record is stated three independent ways — the container's `NODE` prefix, the enclosing
`TYPE="TITLE"` div, and the filename — and all three disagreed on **every** record.

The cause was one attribute. `<DIV1 N="1" NODE="11:1" TYPE="TITLE">` is *volume 1 of
title 11*: the `N` is the printed volume index, and the title number is the `NODE`
prefix. Reading `N` labelled every title in the corpus `"1"`.

Fixed to read `NODE`; the three sources now agree on all 2,428 records, and
`test_div1_N_is_the_volume_index_and_is_not_the_title_number` pins it. No count in
this chunk was affected — `title` already preferred the `NODE` prefix — but a
disagreement counter that reads `2428` and is reported as a data finding rather than
debugged is precisely the failure hard rule 15 exists to prevent.
