# Read-aloud script — `docs/slides/index.html`

**Target 4:09. Hard cap 5:00.** Thirteen slides, thirteen lines, read word for word.

Open `index.html`, press `F` for fullscreen, and start recording. **Arrow key or space
advances.** Slide 11 is the only slide with reveals inside it — four presses — and they
are marked below.

---

## How the duration was arrived at, and what it is not

**No human has read this aloud with a timer yet.** The figures below are computed, not
performed: **557 spoken words** at 140 words per minute, plus 9 seconds of deliberate
silence budgeted at the three places marked `[PAUSE]`. That gives **4:07**; the clock
table below sums the per-slide figures after rounding each to a whole second and comes
to **4:09**. Both are stated rather than one of them quietly picked.

140 wpm is the rate `docs/video-script.md` asks for — *"slow down; reading a script aloud
always comes out faster than it reads."* The word count is reproducible from this file:
count the words in every `>` line under `## The lines`.

The margin is what matters, so here is the envelope rather than a single number:

| delivery rate | duration |
|---|---|
| 120 wpm — very slow | **4:47** |
| 130 wpm | **4:26** |
| **140 wpm — the target** | **4:07** |
| 150 wpm | **3:51** |

**Every rate in that range lands under 5:00.** The operator still times the real read
before recording, and if it comes back over 4:30, cut from slide 9 and slide 10 first —
they carry the most words and the least that is irreplaceable.

---

## The clock

| # | slide | duration | cumulative | beat (PDF §8 deliverable 03) |
|---|---|---|---|---|
| 1 | Title | 0:09 | **0:09** | — |
| 2 | The defective instruction | 0:24 | **0:33** | the problem |
| 3 | The NARA note | 0:11 | **0:44** | the problem |
| 4 | The baseline B0 | 0:20 | **1:04** | the simple baseline |
| 5 | What the agent receives | 0:13 | **1:17** | one realistic execution |
| 6 | The tool call | 0:15 | **1:32** | one realistic execution |
| 7 | The emitted note | 0:21 | **1:53** | one realistic execution |
| 8 | The override | 0:20 | **2:13** | one realistic execution |
| 9 | The comparison | 0:34 | **2:47** | the final comparison |
| 10 | Predictions vs measurements | 0:26 | **3:13** | the changelog |
| 11 | The composition | 0:28 | **3:41** | the change that contributed most |
| 12 | The removed experiment | 0:15 | **3:56** | one experiment removed |
| 13 | The hot take | 0:13 | **4:09** | — |

---

## The lines

### Slide 1 · Title · 0:09 · cumulative 0:09

> This is The Instruction That Won't Execute. It reads a Federal Register amendment and
> decides whether it will actually codify.

`→ ARROW`

### Slide 2 · The defective instruction · 0:24 · cumulative 0:33

> US agencies change the Code of Federal Regulations by publishing instructions like this
> one. Remove this exact sentence. The Office of the Federal Register has to find that
> sentence in the text. Look at the quoted words. The rule says notion of exemption. The
> Code says notice. One word, and there is nothing to remove.

`→ ARROW`

### Slide 3 · The NARA note · 0:11 · cumulative 0:44

> So the amendment could not go in. The National Archives publishes this note instead.
> It is permanent, it is citable, and the text it targeted never changed.

`→ ARROW`

### Slide 4 · The baseline · 0:20 · cumulative 1:04

> The simple baseline is one prompt. Give a model the instruction. Ask whether it will
> execute. No Code text, no tools. On eighty-two items it scores forty-seven point six
> percent. That is a coin flip, and it should be. The instruction alone does not contain
> the answer.

`→ ARROW`

### Slide 5 · What the agent receives · 0:13 · cumulative 1:17

> Here is the whole system on one case. Forty CFR seventy-five point six. The agent gets
> four instructions, and the section text as it stood before the rule was published.

`→ ARROW`

### Slide 6 · The tool call · 0:15 · cumulative 1:32

> For each instruction it calls a deterministic resolver. Is this paragraph declared. Is
> this quoted string present. Here is the real call and the real answer. The resolver
> says paragraph a thirty-eight does not exist.

`→ ARROW`

### Slide 7 · The emitted note · 0:21 · cumulative 1:53

> Then it writes the editorial note the Archives would have to publish. Not a yes or no.
> The failing designation, the failure class in NARA's own vocabulary, the full trace.
> The verdict is derived in code from that trace, so it cannot be right for the wrong
> reason.

`→ ARROW`

### Slide 8 · The override · 0:20 · cumulative 2:13

> On this case, something I did not expect happened. The resolver was wrong. It cannot
> see nested designations. The model read the section text, saw paragraph thirty-eight
> sitting there, and overrode its own tool. It named the tool's limitation in the
> published note. And it ruled correctly.

`→ ARROW`

### Slide 9 · The comparison · 0:34 · cumulative 2:47

> Two results. The second is a null. Giving the agent the Code text moves it from
> forty-seven point six to sixty-five point nine percent. Plus eighteen point three
> points, p equals zero point zero zero six. That is real. Adding our two capabilities
> gets seventy-one point nine. Plus six point one points, p equals zero point four two.
> That is not significant.

**`[PAUSE — 2 seconds. Let it land. Do not soften it.]`**

> Our pre-registered criterion had four clauses. We met none. It ships unmet.

`→ ARROW`

### Slide 10 · Predictions against measurements · 0:26 · cumulative 3:13

> Every iteration was predicted before it ran, and the predictions are timestamped in
> git. Iteration one was the resolver. Predicted plus eight points, measured minus nine
> point eight. Wrong direction. Removed. Iteration two was the written procedure.
> Predicted zero point eight one, measured zero point seven two. That prediction was
> committed seven hundred and sixty-four seconds before the arm ran.

`→ ARROW` — **this lands on slide 11 empty. The three lines are not there yet.**

### Slide 11 · The composition · 0:28 · cumulative 3:41

**Four arrow presses inside this slide. Press first, then say the line.**

`→ ARROW` *(reveals `tool alone · A1-iter1 · −9.8`)*

> The tool alone made it worse.

`→ ARROW` *(reveals `skill alone · A1-minus-tool · −1.2`)*

> The procedure alone made it worse.

`→ ARROW` *(reveals `together · A1 · +6.1`)*

> Together, plus six point one.

`→ ARROW` *(reveals the sentence beneath)* **`[PAUSE — 6 seconds across the four reveals]`**

> Neither capability helps on its own. It composes because the procedure repairs a defect
> in the tool. We found that defect because it cost us a point, and we left it unfixed
> and documented.

`→ ARROW` — **the fifth press leaves slide 11 for slide 12.**

### Slide 12 · The removed experiment · 0:15 · cumulative 3:56

> One experiment we removed. We predicted the current Code text would raise accuracy,
> because it leaks the answer. It fell six point one points. The prediction was wrong,
> and it is published as wrong.

`→ ARROW`

### Slide 13 · The hot take · 0:13 · cumulative 4:09

**`[PAUSE — 1 second before you start. The slide is one sentence; let it be read.]`**

> A grounding corpus is a precision instrument, not a recall instrument. If you hand an
> agent the document, measure which class got better. The average will lie to you.

*(End. Stop recording.)*

---

## Delivery

- **Say the null results in the same tone as the good ones.** Slides 9, 10, 11 and 12 all
  report something that did not work. They are findings, not confessions. No apology in
  the voice, no rising inflection at the end of "we met none".
- **Read the numbers slowly.** "Forty-seven point six" and "zero point zero zero six" are
  the two most easily fluffed lines in the deck.
- **Do not narrate live.** Live narration runs long and rambles, and the brief names
  seven specific beats. Every one of them is above, in order.
- **Retakes are fine.** If a line is fluffed, stop and redo that slide. Do not repair it
  in narration.
- **Do the twenty-second audio test first.** A silent video is the single most common
  failure here.

## What the deck does not say out loud, and where it is written instead

Two things the script deliberately does not spend words on, because they are on the
slide in front of the viewer and reading them aloud would cost twenty seconds each:

- **The artifact path in the footer of every slide.** Every figure on the deck is
  reproduced from the file named in the bottom-left corner. Nothing is asserted.
- **The caveat under slide 11.** The single-capability arms are one rep each, and A1's
  own rep-to-rep spread is 4.9 pp — so "neither helps alone" is *not distinguishable from
  no effect*, not measured harm. It is printed on the slide; if the read comes in short,
  say it aloud.
