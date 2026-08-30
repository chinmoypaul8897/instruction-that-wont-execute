# CH-05 — `cfr_resolve` golden fixtures, hand-computed BEFORE the code

Hard rule 4. `src/cfr_resolve.py` does not exist at the SHA that commits this file.

The tool `CONTEXT.md` §6 specifies:

> `cfr_resolve(title, part, section, as_of_date, quoted_text, designation)`
> Deterministic. **Designation-hierarchy resolution FIRST, quoted-anchor matching
> second.** Returns `{found, level, designation_exists, siblings, char_offset}`.

And §1, the precision-critical clause:

> Matching is attempted at three **declared** levels — `exact` /
> `whitespace-collapsed` / `alphanumeric-only` — and the level achieved is **reported
> in the output**, never applied invisibly.

---

## The fixture

A deliberately tiny string, so every offset below is countable by hand:

```
(a) alpha. (b) beta  gamma.
```

| index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| char | `(` | `a` | `)` | ` ` | `a` | `l` | `p` | `h` | `a` | `.` | ` ` | `(` | `b` | `)` |

| index | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| char | ` ` | `b` | `e` | `t` | `a` | ` ` | ` ` | `g` | `a` | `m` | `m` | `a` | `.` |

Note the **two** spaces at 19 and 20. They are the whole point of the fixture.

## R-A · Designation parsing

| input | expected path |
|---|---|
| `(b)(4)(i)(A)` | `["b", "4", "i", "A"]` |
| `(a)` | `["a"]` |
| `(b)(1)` | `["b", "1"]` |
| `` (empty) `` | `[]` |
| `(b) (4)` — a space between groups | `["b", "4"]` — FR drafting spaces them and it means the same designation |

## R-B · Designation existence and siblings

Designations present in the fixture: `(a)` at offset **0**, `(b)` at offset **11**.

| query | `designation_exists` | `siblings` |
|---|---|---|
| `(a)` | **true** | `["(a)", "(b)"]` |
| `(b)` | **true** | `["(a)", "(b)"]` |
| `(c)` | **false** | `["(a)", "(b)"]` |
| `(b)(1)` | **false** | `["(a)", "(b)"]` — no depth-2 designations exist here |

**`siblings` is returned even when the designation does NOT exist**, and that is the
point of the field: `CONTEXT.md` §9's hard cases are *"revising a definition that did
not exist"* and *"adding an entry that already exists"*, and both are answered by
what is present around the target, not by the target alone. A tool that returned an
empty list on a miss would answer neither.

## R-C · The three declared normalisation levels

| # | `quoted_text` | expected `level` | expected `char_offset` | expected matched span in the ORIGINAL |
|---|---|---|---|---|
| C1 | `beta  gamma` (two spaces) | **`exact`** | **15** | `beta  gamma` |
| C2 | `beta gamma` (one space) | **`whitespace-collapsed`** | **15** | `beta  gamma` |
| C3 | `betagamma` | **`alphanumeric-only`** | **15** | `beta  gamma` |
| C4 | `Beta Gamma` | **`none`** | `null` | — |
| C5 | `alpha` | **`exact`** | **4** | `alpha` |
| C6 | `` (empty) `` | **`none`** | `null` | — |

**C4 is the one that stops the levels becoming a licence.** `alphanumeric-only` strips
punctuation and whitespace; it must **not** fold case. `CONTEXT.md` §1: *"No lossy
encoding, no unicode folding, no smart-quote substitution anywhere in the pipeline."*
A matcher that returned `alphanumeric-only` for C4 has silently made the anchor
case-insensitive, and paragraph designations like `(A)` versus `(a)` are a real
distinction in the CFR.

**The levels are tried in order and the FIRST that matches is reported.** A string that
matches exactly must never be reported as `whitespace-collapsed`.

## R-D · `char_offset` is in ORIGINAL coordinates, always

C2 and C3 match only after normalisation, and both still report **15** — an index into
the string the caller passed in, not into a normalised copy it never sees.

This is the clause that makes `hard rule 7` operational. A tool that reported an offset
into its own normalised buffer would be reporting a position in a document that does
not exist, and the codification worksheet (CH-10) highlights the anchor **in the real
text** using this number.

**Expected, asserted for every level:**
`original_text[char_offset : char_offset + len(matched_span)] == matched_span`.

## R-E · Designation-hierarchy resolution comes FIRST

`CONTEXT.md` §6 fixes the order, and gives the measurement that forces it: *"26/33 and
35/42 labelled items have no extractable quoted anchor, and NARA's dominant note
mechanisms (`did-not-exist`, `already-exists`) are designation-state facts. A pure
quoted-string matcher no-ops on ~80% of the pool."*

| call | expected |
|---|---|
| `designation="(c)"`, `quoted_text="alpha"` | `designation_exists` **false**, `found` **true**, `level` `exact`, `char_offset` **4** |
| `designation="(a)"`, `quoted_text="delta"` | `designation_exists` **true**, `found` **false**, `level` `none` |
| `designation="(c)"`, `quoted_text=None` | `designation_exists` **false**, `found` **false**, `level` `none` |
| `designation=None`, `quoted_text="alpha"` | `designation_exists` **null**, `found` **true**, `level` `exact` |

**`found` and `designation_exists` are INDEPENDENT fields and neither is derived from
the other.** Collapsing them into one boolean is how a partial read becomes a confident
wrong answer — `CONTEXT.md` §6 records that both clean-item errors in the pilot were
premature rulings on a partial read.

`designation_exists` is **`null`**, not `false`, when no designation was asked about.
False would assert that a designation is absent when none was queried.

## R-F · Purity and determinism

- **No network, no clock, no randomness** (hard rule 8). `as_of_date` selects which
  frozen text the caller passes in; the resolver never fetches anything.
- Same inputs → byte-identical output (hard rule 9).
- The resolver **never mutates** the text it is given.

## R-G · What the tool must refuse rather than guess

| input | expected |
|---|---|
| a `designation` that is not parenthesised, e.g. `b4iA` | raise — it is not a designation and guessing at one would invent a target |
| `title`/`part`/`section` that do not match the text supplied | the caller's problem; the resolver reports on the text it is given and **echoes the identifiers back** so a mismatch is visible in the trace |

Echoing the identifiers is not decoration: `resolution_trace` in `CONTEXT.md` §5 is the
artifact a judge reads, and a trace that does not say which section it resolved against
cannot be checked.
