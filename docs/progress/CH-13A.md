# CH-13A — the slide deck and the per-slide read-aloud script

**Session type:** BUILD, parallel with CH-12. **No model calls. No arm re-run. No result
changed.** Measured API spend at the end of this session is **USD 11.632274** over 2,107
ledger rows — the same figure it was at the start, recomputed from
`docs/evidence/runs/cost_ledger.csv`.

**Scope fence honoured.** Four paths created, nothing else touched:
`docs/slides/index.html` · `docs/slides/script.md` · `tests/test_slides.py` ·
`docs/progress/CH-13A.md`. `README.md`, `STATUS.md`, `PROGRESS.md`, `SUBMISSION.md` and
`AI-USE.md` are CH-12's and were read but never written. No `git add -A`.

---

## What was built

**`docs/slides/index.html`** — thirteen slides, one self-contained file, 23.5 KB, no
network reference of any kind. Fixed 1920×1080 canvas scaled to the viewport so a
recording is predictable. Arrow keys and space advance, `F` toggles fullscreen, nothing
else is bound. Slide 11 reveals three lines and a conclusion, one per press, by toggling
`visibility` — instant, no fade, no easing, and the layout is reserved so nothing shifts.

**`docs/slides/script.md`** — the word-for-word read, per slide, with a target duration, a
cumulative timestamp and the arrow presses marked.

**`tests/test_slides.py`** — 22 tests. Three of them are the ones the chunk asked for
(`http://`, `https://`, `src="//"`); the rest close the same hole from the other side and
then do something the brief did not ask for and hard rule 14 does: **every number the
deck prints is recomputed from its committed artifact and asserted against the slide it
is printed on**, and every quotation is read out of the artifact it was copied from and
compared character-for-character.

---

## Where every number on a slide came from

| slide | figure | artifact |
|---|---|---|
| 2 | the instruction, verbatim | `data/amdpars/amdpars.jsonl`, frdoc `2016-03298`, ordinal 180 |
| 2 | the point-in-time sentence | `data/evalset/items.jsonl`, item `2016-03298\|1150.35`, `section_text` |
| 3 | the editorial note, verbatim | `data/ednotes/defect_notes.jsonl`, ordinal 164, node `49:8.1.1.2.66.4.7.5` |
| 4 | the prompt, verbatim with one marked elision | `agents/B0.md` § System prompt |
| 4 | 47.6% · n = 82 · 39/82 | `docs/evidence/checkpoint/checkpoint-result.json` → `b0.accuracy` 0.47560975609756095 |
| 5 | four instructions + section-text excerpt | `data/evalset/items.jsonl`, item `05-8447\|75.6`; 11,488 chars is `len(section_text)` |
| 5 | user prompt 12,238 characters | `docs/trajectories/arms/A1-rep1.jsonl`, run `A1__05-8447_75.6__rep1`, step 1 `user_prompt_chars` |
| 6 | the call and the returned JSON | same trajectory, steps 6 and 7, `record: action` / `record: tool_response` |
| 7 | the four-row trace, `verdict`, `failing_designation`, `failure_class` | `docs/evidence/ch06-a1/A1-rep1-artifacts.jsonl`, item `05-8447\|75.6` |
| 7 | 16 of 82 routed | counted in the test: rows with `needs_human_review == true` in that file |
| 8 | both `why` strings, verbatim | same file, `resolution_trace[2].model_ruling.why` and `[3]` |
| 9 | 0.4756 / 0.6585 / 0.7195 / 0.6585, all `n/82` | `docs/evidence/ch06-a1/a1-result.json` → `results.*.accuracy`, `.success` |
| 9 | +18.3 pp · p = 0.0059 | `docs/evidence/checkpoint/checkpoint-result.json` → `as_run.gap_pp` 18.292682926829272, `as_run.mcnemar.p_value` 0.005924612283706665 |
| 9 | +6.1 pp · p = 0.4244 | `a1-result.json` → `comparisons.A1.gap_pp` 6.097560975609751, `.mcnemar.p_value` 0.42435622215270996 |
| 9 | +0.0 pp · p = 1.0000 | `a1-result.json` → `comparisons.B0prime` |
| 9 | the four-clause criterion | `GOOD.md` §4, quoting `CONTEXT.md` §7 |
| 10 | predicted +8 pp → 0.74; v1 0.81; v2 0.69 | `CHANGELOG.md`, iteration cards committed at `e12466c` |
| 10 | measured 0.5610 · −9.8 pp | `a1-result.json` → `results.A1-iter1.accuracy`, `comparisons.A1-iter1.gap_pp` −9.756097560975608 |
| 10 | 764 seconds | **recomputed, not relayed** — `git log -1 --format=%ct e12466c` = 2026-08-31T02:11:37Z; first `timestamp_utc` in `docs/trajectories/arms/A1-iter1-rep1.jsonl` = 02:24:21.091Z; **gap 764.091 s** |
| 11 | −9.8 · −1.2 · +6.1 | `a1-result.json` → `comparisons.{A1-iter1, A1-minus-tool, A1}.gap_pp` |
| 11 | rep-to-rep spread 4.9 pp | `docs/evidence/ch06-a1/a1-result.txt`, "REP-TO-REP STABILITY", A1 per-rep `0.7195 / 0.6707 / 0.7195` |
| 12 | the pre-registered prediction, verbatim | `docs/evidence/ch09-removed/leakage-result.txt`, quoting `CONTEXT.md` §10 |
| 12 | 0.6585 → 0.5976 · −6.1 pp · p = 0.4421 · b=11 c=16 | `docs/evidence/ch09-removed/leakage-result.json` |
| 13 | the hot take | `CONTEXT.md` §11 |

Every one of those was opened and read in this session. `AI-USE.md`'s own note on the
`764` was checked against `git` and the trajectory rather than taken on trust, per hard
rule 15 — it reproduces to 764.091 s.

---

## Decisions taken without asking, and why

**Class B — slides 2–3 use a different item from slides 5–8.** The chunk card asks slide 2
for an instruction *"whose anchor genuinely did not resolve"* and slide 8 for the
`05-8447|75.6` exemplar. Those cannot be the same item: 75.6's only quoted anchor
**resolves** — `found: true, level: exact, char_offset: 1103`. So slides 2–3 use
`2016-03298|1150.35`, where the rule quotes *"the filing of the **notion** of exemption"*
and the Code says *"**notice**"*, and slides 5–8 follow `05-8447|75.6` start to finish.
Each slide carries its citation, and this mirrors `docs/video-script.md`, whose beat 1 and
beat 3 already show two different sections. The absence was verified at all three declared
normalisation levels (`exact`, `whitespace-collapsed`, `alphanumeric-only`) and that check
is a test, not a claim.

**Class B — every slide carries its artifact path in the footer.** Not asked for. It is
hard rule 14 made visible to a judge who is watching rather than reading, and it is the
single strongest signal that this is an exhibit and not a pitch deck.

**Class B — a `#N` / `#N.S` URL hash selects the opening slide.** Needed to screenshot one
slide at a time for the visual check, and useful to the operator for retakes. Read once at
load. **No key binding was added**: arrows, space and `F`, nothing else.

**Class B — mono size steps around the declared 22px.** `mono data 22px` is the base and is
used where it fits; artifact blocks that will not fit at 1920×1080 step down (17–20px) and
the two showpiece quotations step up (26–34px). Family, colour and line-height unchanged.

**Class C — `.headline.wide` raises the headline `max-width` from 24ch to 34ch**, used
twice: slide 8, so *"The agent overrode its own tool."* sets on one line, and slide 13, so
the hot take sets in five centred lines instead of nine. Size (64px), family, weight and
line-height are the declared values.

**Class C — the area outside the 1920×1080 canvas is `--ink`.** One of the five colours; it
gives the page a visible edge when the viewport is not 16:9.

**Class C — slide 3's serif line was reworded** from *"still reads the way it read in
2015"* to *"the text it targeted was not changed"*. Two reasons: `2015` is a
machine-produced value and the design system puts those in mono, and the note only
supports the claim for the portion that failed, not for the whole section.

---

## Verification

**Rendered and looked at.** Every slide was rendered to PNG at 1920×1080 with headless
Chrome and inspected. That is how the slide-8 hanging indent was found and fixed, and how
the self-check below was answered rather than asserted.

**Opens from the file alone.** `index.html` was copied by itself into an empty directory
and rendered there. Slides 1, 5, 9 and 13 came back **byte-identical** to the in-repo
renders (`sha256` compared), so the deck depends on nothing beside it.

**The test bites.** Eleven mutations were applied one at a time to a backed-up copy of the
deck; every one turned the suite red, and the deck was restored byte-identical
(`sha256 bc8f5514728d45887927081d1e46a5fee53abc557087bb6292748b1d71e6e103` before and
after). This is the negative control, not a probe flip — nothing was fixed here, so hard
rule 6 does not apply; the control is run anyway because a green test that cannot go red
is not evidence.

| mutation | result |
|---|---|
| slide 9 A1 accuracy `0.7195 → 0.7295` | RED |
| slide 9 gap `+18.3 → +18.4 pp` | RED |
| slide 9 p-value `0.4244 → 0.0244` | RED |
| slide 4 hero `47.6% → 57.6%` | RED |
| slide 7 routed count `16 → 18` | RED |
| slide 12 leakage fall flipped to a rise | RED |
| slide 5 quotation, one capital letter | RED |
| slide 8 `why` string reworded by one word | RED |
| accent colour changed | RED |
| a network image added | RED (2 tests) |
| a CSS transition added | RED |

**The first version of the test did not bite.** `0.7195 → 0.7295` on slide 9 passed,
because the assertion only required the string to appear *somewhere* in the deck and slide
10 still carried the right value. The test was rewritten to assert per slide, and the
mutation then went red. Recorded because a test that passes for the wrong reason is this
project's whole subject.

**Suites.** `tests/test_slides.py` 22 passed. Full repository suite **379 passed**, 0
failed, 0 skipped, 65.9 s.

---

## Self-check, answered after looking at the rendered slides

1. **Does it look like a pitch deck? — NO.** Warm paper stock, Georgia, hairlines, a folio
   bottom-right and an artifact path bottom-left on every page. No cards, no fills, no
   centring except slide 13.
2. **Colours used — 5, and no more.** `#FBFAF7 #1A1A18 #6B6862 #D8D4CC #9B2226`, asserted
   by `test_palette_is_exactly_five_colours` as set equality, so a sixth colour is red.
   Oxblood appears only on things that did not work: the absent quoted text, `p = 0.4244`
   and *not significant*, *met on none of the four clauses*, `−9.8`, `−1.2`,
   *v1 missed by 9.1 pp*, and the leakage `−6.1 pp`. The `+6.1` that worked is plain ink.
3. **Every machine-produced value in monospace — yes.** Audited programmatically: **zero**
   serif blocks in the deck contain a numeral.
4. **Slides 5–8 — real artifact text**, not a drawing of a pipeline. Slide 5 is the
   instructions and the point-in-time section text, slide 6 is the trajectory's own
   `action` and `tool_response` records, slide 7 is the emitted artifact, slide 8 is the
   two `why` strings verbatim. There is not a box or an arrow anywhere in the deck.
5. **Icon, gradient, card, shadow, rounded corner — none.** No `<img>`, no emoji, no
   `border-radius`, `box-shadow`, `gradient`, `transition` or `animation`; asserted.
6. **A slide title that is a label — none.** The labels are locators
   (`FEDERAL REGISTER · AMENDATORY INSTRUCTION`), and the two headlines are sentences.
   Nothing reads *Overview*, *The Solution* or *Key Takeaways*.
7. **Opens with the network off, from a fresh copy — yes**, shown byte-identical above.
8. **Read aloud with a timer — NOT DONE, and that is stated rather than papered over.**
   No audio was produced in this session, so no real duration exists. The published figure
   is computed: **557 spoken words**, and at 140 wpm plus 9 s of marked pauses that is
   **4:07**; the per-slide clock, rounded, sums to **4:09**. The envelope runs **4:47** at
   a slow 120 wpm down to **3:51** at 150. **Every rate in that band is under the 5:00
   cap.** The operator must still time the real read before recording — `script.md` says
   where to cut first if it comes back long.

---

## Open items for the architect

1. **The video-script wording is now in two places.** `docs/video-script.md` holds the
   seven beats in long form; `docs/slides/script.md` holds the tightened read. They agree
   on every number but not word for word, by design — one is a plan and one is a
   teleprompter. If only one should survive to submission, the tightened one is the one
   that gets recorded.
2. **Nothing links to the deck yet.** `README.md` and `SUBMISSION.md` belong to CH-12 this
   session and were not touched. Someone has to add `docs/slides/index.html` to them.
3. **The read is untimed.** See self-check 8. This is the one item in this chunk that a
   session cannot close.
