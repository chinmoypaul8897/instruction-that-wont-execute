# Caption script — `docs/slides/index.html`

**This file is the source the video is built from.** `docs/video/build_video.py` parses
the `## The lines` section below, splits each block into caption segments, computes each
segment's duration from its own word count, and renders one 1920×1080 frame per segment
with the caption burned into the page. Nothing here is timed by hand.

**The video is silent and captioned.** CH-13A wrote this file as a read-aloud script for
a human narrator at 140 wpm. CH-13B changed the delivery: a judge watches with the sound
off, every word is on the screen, and the operator does not have to record anything. The
words are almost all CH-13A's — the change is who says them.

---

## How a duration is arrived at

Each segment is at most **22 words**, and

```
duration = max(3.0, words / 2.8)      # ~168 wpm reading speed, rounded to 0.1 s
```

**Nothing is ever under 3.0 seconds.** A caption that flashes is worse than no caption,
so a six-word line still holds for three seconds even though nobody needs three seconds
to read it. That floor is why the total is not simply `words / 2.8`.

Three frames carry no caption at all, and all three are deliberate:

- **Slide 1**, the title card. Four seconds, the title, nothing else.
- **Slide 15**, the hot take. The slide *is* one sentence set in 64px serif. A caption
  band underneath repeating it in 30px would be the padding the brief warns about, so
  the slide holds for `words-on-the-slide / 2.8` instead and the reader reads the slide.

The **end card** — repo, name — is `docs/video/endcard.html`, four seconds, no caption.

The measured total is printed by `build_video.py` and reported in
`docs/progress/CH-13B.md`. **The hard cap is 5:00.** If a rebuild ever goes over, cut
caption segments from slide 10 and slide 11 first: they carry the most words and the
least that is irreplaceable. **Never speed the video up.**

---

## The lines

Each `>` block below is one caption *block*. The builder splits a block that runs over
22 words at a sentence boundary, and only inside a sentence if a single sentence is
itself over 22 words. One segment, one frame.

### Slide 1 · Title

*No caption. Four seconds.*

### Slide 2 · The defective instruction

> US agencies change the Code of Federal Regulations by publishing instructions like this one. Remove this exact sentence.

> The Office of the Federal Register has to find that sentence in the text. Look at the quoted words.

> The rule says notion of exemption. The Code says notice. One word, and there is nothing to remove.

### Slide 3 · The editorial note

> So the amendment could not go in. The National Archives publishes this note instead.

> It is permanent, it is citable, and the text it targeted never changed.

### Slide 4 · The baseline

> The simple baseline is one prompt. Give a model the instruction, ask whether it will execute. No Code text, no tools.

> On eighty-two items it scores forty-seven point six percent. That is a coin flip, and it should be.

> The instruction alone does not contain the answer.

### Slide 5 · The pipeline

> Here is the whole system. Two inputs: the amendatory instruction, and the CFR text as it stood the day before.

> For every instruction a deterministic resolver answers two questions, and each answer is written to a trace.

> The verdict is computed from that trace in code. Anything contradictory is refused rather than guessed.

### Screencast · the shipped worksheet

**Five captions, one per storyboard beat.** These are not stills, so they are drawn onto
the recording with ffmpeg `drawtext` in the same band, at the same size, in the same
place.

The builder does **not** take the beat boundaries from the recorder's sidecar, and an
earlier version of this paragraph said it did. It reads them off the tape:
`record_worksheet.js` stamps a grey patch, one level per beat, into the strip the band
later paints over, and `build_video.py` decodes that patch per frame. The sidecar's
wall-clock offsets survive only for comparison, and both appear in
`docs/evidence/ch13b/build-video.txt`. The reason is `docs/progress/CH-13B.md` §2b — a
caption timed off the wall clock was drawn over the wrong CFR section, and the build
reported nothing wrong.

Caption *k* is held for the whole of beat *k*: the scroll toward the section and then
the hold on it. Each is subject to the same `max(3.0, words / 2.8)` rule as the stills,
and `build_video.py` enforces it — the first draft of caption 1 ran 20 words in 3.4
seconds, which is 353 wpm, and the build now refuses that rather than reporting it as
`OK`.

> That system produces this page. Nothing here is staged.

> Forty CFR seventy-five point six: the failing designation, and the class of failure.

> The trace row where the resolver returned found equals false, and the page saying why.

> The human-checkpoint queue. Sixteen of eighty-two, each with the reason it was flagged.

> And the provenance footer: both commits, the arm, the model, and a hash for every input.

### Slide 6 · What the agent receives

> Now the same case, step by step. Forty CFR seventy-five point six.

> The agent gets four instructions, and the section text as it stood before the rule was published.

### Slide 7 · The tool call

> For each instruction it calls the resolver. Is this paragraph declared? Is this quoted string present?

> Here is the real call and the real answer. The resolver says paragraph a thirty-eight does not exist.

### Slide 8 · The emitted note

> Then it writes the editorial note the Archives would have to publish. Not a yes or no.

> The failing designation, the failure class in the Archives' own vocabulary, and the full trace.

> The verdict is derived in code from that trace, so it cannot be right for the wrong reason.

### Slide 9 · The override

> In this case, something I did not expect happened. The resolver was wrong: it cannot see nested designations.

> The model read the section text, saw paragraph thirty-eight sitting there, and overrode its own tool.

> It named the tool's limitation in the published note. And it ruled correctly.

### Slide 10 · The comparison

> Two results, and the second is a null. Giving the agent the Code text moves accuracy from forty-seven point six

> to sixty-five point nine. Plus eighteen point three points, p equals zero point zero zero six. That is real.

> Adding our two capabilities gets seventy-one point nine five. Plus six point one points, p equals zero point four two.

> That is not significant. Our pre-registered criterion had four clauses. We met none. It ships unmet.

### Slide 11 · Predictions against measurements

> Every iteration was predicted before it ran, and the predictions are timestamped in git.

> Iteration one was the resolver. Predicted plus eight points, measured minus nine point eight. Wrong direction. Removed.

> Iteration two was the written procedure. Predicted zero point eight one, measured zero point seven two.

> That prediction was committed seven hundred and sixty-four seconds before the arm ran.

### Slide 12 · The composition

**Exactly four blocks, one per reveal.** The builder asserts it: block *k* is rendered
with bars 1 through *k* visible, so the chart is built in front of the viewer rather
than arriving finished.

> The tool alone: minus nine point eight points.

> The procedure alone: minus one point two points.

> Together, plus six point one points.

> One rep each against a 4.9 point spread, so read the negatives as no effect, not harm. Together, they compose.

### Slide 13 · The removed experiment

> One experiment we removed. We predicted the current Code text would raise accuracy, because it leaks the answer.

> It fell six point one points. The prediction was wrong, and it is published as wrong.

### Slide 14 · The shipped worksheet

> That page is the deliverable. Every item carries its trace, and the level each anchor actually resolved at.

> Sixteen of eighty-two are not decided by the tool. They go to a person, each with its reason.

### Slide 15 · The hot take

*No caption. The slide is the sentence.*

---

## What the deck does not caption, and where it is written instead

Two things the captions deliberately do not spend words on, because they are on the
slide in front of the viewer and captioning them would cost twenty seconds each:

- **The artifact path in the footer of every slide.** Every figure on the deck is
  reproduced from the file named in the bottom-left corner. Nothing is asserted.
- **The caveat under slide 12.** The single-capability arms are one rep each, and A1's
  own rep-to-rep spread is 4.9 pp — so "neither helps alone" is *not distinguishable
  from no effect*, not measured harm. It is printed on the slide.

## What was cut when the delivery changed

CH-13A's script carried three `[PAUSE]` directions and a block of delivery notes for a
human reader — *"say the null results in the same tone as the good ones"*, *"read the
numbers slowly"*. A silent video has no tone and no reading speed to control, so those
are gone rather than left in place to describe something the file no longer produces.
The pauses became what they always were in a captioned cut: a segment boundary, and a
minimum three seconds on every frame.
