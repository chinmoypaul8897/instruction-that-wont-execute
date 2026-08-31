# CH-13B — the deck enhanced, the product recorded, the video assembled

**Build session. No arm re-run, no model call. API spend unchanged at USD 11.632274 over
2,107 ledger rows** (`docs/evidence/runs/cost_ledger.csv`, re-summed at the end of this
chunk).

`STATUS.md` and `PROGRESS.md` are architect-merged, and both are outside this chunk's
scope fence, so this file is the entry. `QUESTIONS.md` is also outside the fence, and the
card directs ambiguities here instead — §7 below is what would otherwise have gone there.

---

## 1 · What shipped

`dist/instruction-that-wont-execute.mp4` — **4:30.87**, 1920×1080, 30 fps, H.264
yuv420p, silent AAC 44.1 kHz stereo, 37.25 MB, `+faststart`. `dist/` is git-ignored; the
video is uploaded, and the four scripts that reproduce it are committed.

Three sources cut together:

| | |
|---|---|
| **40 still frames** | one per caption segment, rendered from `docs/slides/index.html` with the caption laid out *in the page* |
| **39.08 s screencast** | `docs/worksheet/index.html` in a real browser, scrolling, captioned with ffmpeg `drawtext` in the same band |
| **end card** | `docs/video/endcard.html`, 4 s |

The deck went from 13 slides to 15. `tests/test_slides.py` went from 22 tests to 35, and
every original assertion is still there — see §4, which is the one place this chunk came
near hard rule 5 and had to argue its way through.

---

## 2 · The two defects this chunk found in its own build

Both produced a video that played, at the right resolution, for a plausible length.
Neither would have been caught by anything green.

### 2a · Still frames ran 4.2 % long

The obvious way to hold a PNG for 6.4 s is a concat list with `duration 6.4`. It does not
do that — the image demuxer carries a frame duration of its own — so **69.0 s of plan
encoded as 74.7 s**, and every caption sat on screen longer than the number
`build_video.py` printed beside it. A report that disagrees with its own artifact.

Fixed by encoding one segment per still with `-frames:v round(d*30)`, which cannot drift,
and asserting the resulting frame count equals the planned one.

### 2b · Screencast captions sat over the wrong sections

They were timed off the recorder's wall clock. Chromium drops capture frames under load,
so **41.9 s at the keyboard came out 40.6 s on the tape** and the error compounded along
the recording. The extracted frame is what caught it: a caption reading *"the trace row
where the resolver returned found equals false"* — which names **49 CFR 1150.35** — was
drawn over **47 CFR 80.905**. The build reported nothing wrong.

A second attempt failed more quietly. Detecting the still stretches by frame-differencing
looked principled, but at 64×36 greyscale **a blank white page and a light document are
nearly the same picture**, so the lead-in merged into the first hold and the trim point
was 1.8 s out with nothing looking broken.

Fixed by making the recording carry its own clock: `record_worksheet.js` stamps a 120×80
grey patch, one level per beat, at `y = 1000–1080`; `build_video.py` reads it back per
frame. The patch is never seen — it sits inside the strip the caption band paints over,
and `assert_mark_is_covered()` checks that rather than assuming it.

### The probe flips — `docs/evidence/ch13b/timing_probe.py`, output in `timing-probe.txt`

```
A. STILL FRAME DURATION      three stills of 4.0s, 6.4s, 6.8s -> 516 frames at 30 fps
   OLD  concat list with a `duration` per image :   720 frames ( 24.00s)   DRIFTS +204 frames = +6.80s
   NEW  one segment per still, -frames:v N     :   516 frames ( 17.20s)   MATCHES          FLIPS: yes

B. SCREENCAST CAPTION ALIGNMENT     drift    OLD              NEW
                                      0%     5 of 5 correct   5 of 5 correct
                                      1%     5 of 5 correct   5 of 5 correct
                                      2%     3 of 5 correct   5 of 5 correct   <-- old breaks
                                      3%     2 of 5 correct   5 of 5 correct
                                      5%     1 of 5 correct   5 of 5 correct
                                     12%     1 of 5 correct   5 of 5 correct   FLIPS: yes
```

**Probe B is reported honestly and it is not a clean flip on the tape that shipped.** On
this recording the two clocks agree to 0.03 s (−0.08 %), so at 0 % drift *both* methods
are right and the defect does not reproduce. Claiming a flip here would be claiming
something that did not happen. So the probe measures the property instead: the wall-clock
method is correct **only while capture drift stays under 2 %**, and the observed drift on
the recording that actually failed was ≈ 3 %. The tape-reading method has no tolerance to
find, because it never consults the wall clock.

A bug that appears only under load is exactly the kind a green build hides. That is why
the fix is to stop depending on the wall clock, not to widen a tolerance.

---

## 3 · The three new slides

**Slide 5 · the pipeline.** CSS grid, six boxes of 1px hairline rules, connectors made of
1px divs, arrowheads set in type. No SVG, no `<pre>`, no clipart — `tests/test_slides.py`
asserts all three. `16 of 82` on the queue box is recomputed from
`A1-rep1-artifacts.jsonl` by the test, not typed.

**Slide 12 · the composition as bars.** One zero rule, oxblood negatives extending left,
ink positive extending right, axis marks at −10 / 0 / +10. **1 pp = 52 px, and the test
asserts each bar's pixel width equals `round(|gap_pp| × 52)` from `a1-result.json`** — so
a bar that drifts from the number printed at its end goes red rather than needing an eye.
The four-step reveal is kept as four frames. The one-rep / 4.9 pp caveat line is kept.

**Slide 14 · the worksheet.** A real 1920×1080 Playwright screenshot of
`docs/worksheet/index.html`, inlined as a `data:` URI. The test decodes the base64, reads
the PNG's IHDR and asserts the dimensions, so a slide claiming a 1920×1080 capture cannot
ship a placeholder.

Folios renumbered `02/15` … `14/15`; the deck's `<title>` says fifteen. Palette still
exactly the five colours. Zero external references, verified below.

**Two things I fixed after looking at the rendered frames rather than at the code.** The
zero rule was drawn straight through the `0` axis label, and the queue box's count was
being uppercased by the label style into `16 OF 82 ITEMS · REFUSED, NOT GUESSED` with
`GUESSED` orphaned on its own line. Both are only visible in a picture.

---

## 4 · The one test rule that had to be argued — hard rule 5

`test_no_external_stylesheet_or_script` carried a **blanket ban on `<img>`**. Slide 14 is
a `<img src="data:image/png;base64,…">`, so the ban had to go. That is a loosened literal
assertion, and it is the kind of move hard rule 5 exists to stop, so here is the argument
in full rather than a one-line note.

The property the ban protected is **offline self-containment**, not the absence of a tag.
It is replaced by a strictly stronger pair:

1. `<iframe|video|audio|object|embed>` remain banned outright.
2. **Every `src` and `href` in the file must begin with `data:` or `#`** —
   `test_every_src_and_href_is_inline`. The old rule never checked this, and would have
   passed a relative `src="shot.png"`, which breaks the deck the moment it is opened
   anywhere but that directory.
3. `test_worksheet_screenshot_is_a_real_1920x1080_png` decodes the payload and reads its
   header.

`http://`, `https://`, `src="//"`, `<link>`, `@import` and `url(` remain banned, all
untouched. **Measured on the shipped deck: 0 / 0 / 0 / 0 / 0 / 0, one `src`, and it is the
`data:` URI.** No other assertion in the file was relaxed; the renumbered slide tests
assert the same content against its new index.

---

## 5 · Measured

Every figure below is read back from the artifact, not from the plan.
`docs/evidence/ch13b/build-video.txt` is the generating script's committed output.

| | |
|---|---|
| duration (`ffprobe`) | **270.87 s = 4:30.87**, cap 5:00 — **29.1 s of margin** |
| planned vs encoded | 270.88 s planned, 270.87 s encoded, **−0.01 s** |
| resolution · fps · pix_fmt | 1920×1080 · 30/1 · yuv420p · h264 |
| audio stream | **present** — aac, 44100 Hz, 2 ch |
| size | 37.25 MB |
| still frames | 40, totalling 231.8 s |
| shortest frame | **3.0 s** — equals the floor, never under it |
| longest caption | **22 words** on a still, 20 on the screencast — cap is 22 |
| shortest screencast caption | 3.4 s |
| caption band | 37 captions rendered, tallest **43.5 px** of the 124 px available — every one fits on one line |
| exemplar slide (9) | 6.4 + 5.7 + 4.6 = **16.7 s**, against the card's ≥ 12 s |
| screencast | 39.08 s, trimmed from 1.44 s in; page **14,791 px** tall, **13,711 px** scrolled |
| deck | 15 slides, **5 colours**, 182,811 bytes, **0 external references** |
| suite | `tests/test_slides.py` **35 passed**; whole suite **392 passed, 0 failed, 0 skipped** |
| API spend | **USD 11.632274**, 2,107 rows — unchanged |

**Is the worksheet long enough to scroll?** Yes, and not marginally. It is 14,791 px at
this viewport — 13.7 screens — and the recording travels 13,711 px of it. No holding was
substituted for movement.

**Three frames pulled back out of the encoded MP4** by `docs/video/extract_frames.py`,
committed to `docs/evidence/ch13b/`, and looked at. What I actually see is in §8.

---

## 6 · Deviations from the card — Class B, disclosed

None of these changes a result. Each is an implementation choice the card left open or a
conflict between two of its own clauses.

1. **The screencast does not delete any slide's captions.** The card says it "slots in
   after the system diagram, replacing whatever caption segments cover the execution
   beat." It is placed after slide 5 exactly as instructed. It replaces nothing, because
   the segments that cover the execution beat are slides 6–9 — the tool call, the emitted
   note and the override — and deleting them would gut the *"one realistic execution"*
   beat the brief requires **and** contradict the card's own instruction that the exemplar
   slide get at least 12 s. Conservative reading taken: the screencast is an additional
   beat carrying its own captions, which is what "since it is video not a still" is
   about. **If the architect meant the stronger reading, this is the one thing to re-cut.**

2. **The end card is `docs/video/endcard.html`, not a 16th slide.** Keeping it out of the
   deck leaves the folio run and the deck's own ending — the hot take — intact. Its five
   colours and two font stacks are copied from the deck verbatim and
   `test_endcard_uses_the_decks_palette` asserts it invented none.

3. **Screencast beat 1 holds 3.4 s, not the card's 2 s.** The card also says "Nothing
   under 3.0 s, ever — a caption that flashes is worse than no caption." That beat carries
   a caption, so the floor wins over the hold; `build_video.py` now fails the build rather
   than shipping a 2.0 s caption.

4. **The screencast is 39.08 s, not "roughly 35".** The card permits holding longer where
   the page is long, and it is: see §5. The hold times are 3.4 / 3.0 / 4.0 / 4.0 / 3.0 s
   as the storyboard asks; the extra seconds are all in the scrolls, at the 40 ms step the
   card specifies.

5. **Slide 15, the hot take, carries no caption.** The card says "No caption on slide 1 or
   the final card"; that is the title card and the end card. Slide 15 is a third
   uncaptioned frame, and the reason is the card's own fifth standard question: the slide
   *is* one sentence in 64 px serif, and a band underneath repeating it in 30 px is
   padding. It holds for `words-on-the-slide / 2.8` = 11.8 s instead.

6. **`docs/slides/script.md` was rewritten from a read-aloud script into the caption
   source.** It is in fence and the card calls it "the caption source". `build_video.py`
   parses it, so the captions are derived from a committed file rather than typed into
   Python. CH-13A's three `[PAUSE]` directions and its delivery notes for a human narrator
   — *"say the null results in the same tone as the good ones"*, *"read the numbers
   slowly"* — are **removed**, because a silent video has no tone and no reading speed,
   and leaving them would describe something the file no longer produces. The file says so
   in its own last section.

7. **The recording carries a beat-marker patch that is not in the card.** See §2b. It is
   an addition to what gets recorded, so it is disclosed even though it is provably
   invisible.

8. **The bar chart replaced slide 11's rows, not "slide 11's table".** The card says
   table; slide 11 (now 12) held three flex rows of type, and slide 9 is the one with a
   `<table>`. The composition slide is plainly what was meant.

---

## 7 · Questions for the architect

The card routes ambiguity here rather than to `QUESTIONS.md`, which is out of fence.
**These are raised, not resolved.**

- **Q44.** Deviation 1 above. Was "replacing whatever caption segments cover the execution
  beat" meant literally? Taken conservatively; the video is re-cuttable from the committed
  scripts in one command if not.
- **Q45.** The fence excludes `prompts/`, so **`prompts/CH-13B.md` is left untracked** —
  the same situation CH-11 raised as Q30 and it is still open. The card that governs this
  chunk is therefore not in the repository a judge clones.
- **Q46.** The fence also excludes `AI-USE.md` (hard rule 13, total disclosure). This
  chunk ran **an adversarial audit fleet of Claude Code subagents** over its own output,
  and their existence and token cost cannot be recorded in `AI-USE.md` from inside this
  fence. Their trajectory is in this session's exported transcript. **The architect needs
  to fold this into `AI-USE.md`** — as CH-11's 52 agents and CH-12's 36 and 103 already
  are. Subagent tokens are Claude Code usage and are *not* in the USD 11.6323 arm ledger,
  which is unchanged.
- **Q47.** `docs/video-script.md` is untracked in the repo root's `docs/` and predates this
  chunk. It is not this chunk's file and was left alone, but it now sits beside a
  `docs/slides/script.md` that says something different about how the video is delivered.
  One of them should go.
- **Q48.** Determinism (hard rule 9). Everything this chunk controls is deterministic — the
  same `script.md`, deck and recording give the same frames, durations and concat plan. The
  **recording itself is not**: a browser capture varies run to run in length and in dropped
  frames, so `dist/instruction-that-wont-execute.mp4` is not byte-reproducible. This is
  stated rather than glossed. The *captions'* alignment is now independent of that
  variation, which was the point of §2b.

---

## 8 · The five standard questions, answered honestly

**1. Could someone with no context follow it with the sound off?** Yes for the argument;
the numbers are the risk. Every beat the brief names is on screen with a caption in plain
words, and the captions never carry a figure the slide behind them does not show. What a
cold viewer will *not* get in one pass is the difference between the arms — B0, B0-agent,
A1 and B0′ are four names on slide 10 and the captions explain three of them. B0′ is never
captioned.

**2. Does any caption move on before you can finish reading it?** No frame is under 3.0 s,
the build fails if one would be, and the rate is 2.8 words/second against a 22-word cap —
so the slowest frame is 7.9 s for 22 words. The two places to watch are the three
six-word bar-chart reveals, which sit at the 3.0 s floor: they are short lines under a
chart that is already legible, and they are the one place a viewer could feel hurried if
they were also trying to read the caveat line.

**3. Does it look like a document, or like a template?** A document. Five colours,
Georgia and Consolas, hairlines, a folio and an artifact path on every slide, no icon and
no rounded corner anywhere. The frames in `docs/evidence/ch13b/` are the evidence.

**4. Does the execution beat show the real thing, or a picture of the real thing?** The
real thing. `frame-screencast.png` is a frame of a browser scrolling
`docs/worksheet/index.html`, holding on 49 CFR 1150.35's resolution trace: instruction 3,
`remove` the sentence quoting *"notion of exemption"*, resolved **no**, level **none**,
`fails`, and the page's own reason — *"the section text contains 'notice of exemption' but
the instruction quotes 'notion of exemption'"*. That is the same defect slide 2 opens on,
found again in the shipped artifact three minutes later. Slide 14 is a picture of it; the
screencast is it.

**5. Is there anywhere it feels padded?** Two honest answers.
   - **The worksheet appears twice** — the 39 s screencast at 1:09, and the still on slide
     14 at 4:02. That is deliberate as a callback and the still does a different job (the
     headline, the 16-of-82), but it is the one place a judge could reasonably say *we saw
     this already*. It cost 6.4 s of the 12.8 s that slide holds.
   - **The end card's 4 s** are the card's requirement, not an editorial choice.
   Nothing else exists to fill time: every frame is one caption segment and every segment
   is a sentence that says something.

---

## 9 · Frames extracted from the encoded MP4, and what is actually in them

Not what was intended — what I see. Offsets computed from `dist/plan.json`, listed in
`docs/evidence/ch13b/frames-extracted.txt`.

- **`frame-slide.png`** (t = 151.68 s, slide 9). Headline *"The agent overrode its own
  tool."* Instruction 3 and instruction 4 laid out in mono with `resolver` /
  `model` / `why` rows, the two `why` strings quoted in full, `executes = true` against
  `designation_exists = false`. Serif line beneath: *"The resolver was wrong, and the
  published note says so."* Footer `docs/evidence/ch06-a1/EXEMPLAR-composition.md`, folio
  `09 / 15`. Caption band across the bottom in Georgia on `--ink`.
- **`frame-barchart.png`** (t = 217.48 s, slide 12 reveal 2). Two oxblood bars — −9.8 and
  −1.2 — both ending exactly on the zero rule, their values in mono to the left of each
  bar. **The third row is blank**: the reveal has not reached it and the space is already
  reserved, so nothing jumps when it arrives. Axis −10 / 0 / +10 with the zero rule
  stopping level with the ticks. Caption *"The procedure alone made it worse."*
- **`frame-screencast.png`** (t = 89.32 s, inside beat 3's hold). Described in §8.4. The
  beat-marker patch is **not visible** — the caption band covers it, which is the
  assertion `assert_mark_is_covered()` makes and this frame confirms by eye.

---

## 10 · Files

**Changed:** `docs/slides/index.html`, `docs/slides/script.md`, `tests/test_slides.py`
**Added:** `docs/video/build_video.py`, `record_worksheet.js`, `render_frames.js`,
`shoot_worksheet.js`, `embed_worksheet_shot.py`, `extract_frames.py`, `endcard.html`;
`docs/evidence/ch13b/timing_probe.py`, `timing-probe.txt`, `build-video.txt`,
`timeline.json`, `frames-extracted.txt`, `frame-slide.png`, `frame-barchart.png`,
`frame-screencast.png`; this file.
**Not touched:** `README.md`, `STATUS.md`, `PROGRESS.md`, `SUBMISSION.md`, `AI-USE.md`,
`CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `GOOD.md`, `src/`, `data/`, `agents/`.
`.gitignore` needed no change — `dist/` was already ignored at line 42.

**To rebuild the whole video from a clean tree:**

```
node   docs/video/shoot_worksheet.js        # 1920x1080 screenshot of the worksheet
python docs/video/embed_worksheet_shot.py   # inline it into slide 14 as a data: URI
node   docs/video/record_worksheet.js       # the screencast + its measured sidecar
python docs/video/build_video.py            # frames, captions, ffmpeg, the report
python docs/video/extract_frames.py         # pull three frames back out as evidence
python docs/evidence/ch13b/timing_probe.py  # both probes, old method vs new
```
