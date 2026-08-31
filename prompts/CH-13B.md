# CH-13B — enhance the deck, record the real product, assemble the video

You are a **BUILD session**. **TIME BOX 2 h.** This is a **one-shot** chunk: the operator will not run it twice. Take the time. **The video is a pass/fail deliverable** — no video, no scoring, regardless of how good the work is.

**No arm is re-run. No result changes. No model calls.** API spend must read **USD 11.6323** at the end.

---

## 🔴 WHAT YOU ARE PRODUCING

**A finished, captioned, silent MP4 under 5:00** that a judge can watch with the sound off and understand completely. **It needs nothing from the operator** — no voice, no recording, no timing.

Three kinds of material, cut together:

1. **Enhanced slides** — the existing 13 plus three new visual slides
2. **A real screencast** of the codification worksheet, recorded with Playwright — the actual page, scrolling, showing real failing designations and the human-review queue
3. **Timed caption bands** carrying the script, burned into each frame

**The screencast is not optional.** The brief demands *"walk through one realistic execution from start to finish"*, and a recording of the real artifact is the strongest possible reading of that.

---

## READ FIRST

1. `CLAUDE.md` — hard rules **14, 15, 16**
2. `docs/slides/index.html` — the existing deck. **Its design system is law**: 5 colours, Georgia + Consolas, hairlines, no icons/gradients/cards/shadows/rounded corners.
3. `docs/slides/script.md` — the caption source, per slide, with timings
4. `docs/worksheet/index.html` — the page you will record
5. `tests/test_slides.py` — 22 tests that must still pass

---

## TOOLS — both already installed, verified

- **Playwright** (`c:\Users\chinm\micro1 engineering challenge\scraper\node_modules`, chromium at `~/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe`). Use it to render slide frames **and** to record the screencast.
- **ffmpeg 8.1.1** on PATH.

---

## PART 1 · THREE NEW SLIDES — the visuals the deck is missing

**Insert, keeping the existing design system exactly.** No new colours, no icons, no imported fonts.

### 1a. The system diagram — insert after slide 4 (becomes slide 5)

A judge has no mental model of the pipeline. Give them one, **set in type and hairlines, not clipart.**

```
        amendatory instruction ─┐
                                ├─→  cfr_resolve  ─→  resolution trace  ─→  editorial note
   point-in-time CFR text ──────┘    deterministic       one row per            verdict is
                                                         instruction            DERIVED from it
                                                              │
                                                              └─→  human review queue
                                                                   16 of 82 items
```

Build it with **CSS grid and 1px hairline borders** — real boxes made of rules, connectors made of thin divs. **Not ASCII art in a `<pre>`, and not an SVG of arrows.** Labels in the uppercase label style; the three nouns in serif; anything machine-shaped in mono.

**One line beneath, serif:** the verdict is derived in code from the trace, so the agent cannot be right for the wrong reason.

### 1b. The composition as a bar chart — replace slide 11's table

Three horizontal bars from a shared zero line:

```
tool alone      ████████████▌            −9.8    (oxblood, extends LEFT)
skill alone     ██▌                      −1.2    (oxblood, extends LEFT)
together                      ███████▌   +6.1    (ink, extends RIGHT)
```

Pure CSS — a zero rule, bars as divs with widths proportional to magnitude. **Oxblood for the two negatives, ink for the positive.** Value labels in mono at the bar ends. Axis marks at −10, 0, +10.

Keep the four-step reveal as **four separate frames** in the video (see Part 3).

Keep the existing caveat line: single-capability arms are one rep, A1's rep spread is 4.9 pp.

### 1c. The worksheet — a new slide near the end (after slide 12)

**A real screenshot** of `docs/worksheet/index.html`, taken by Playwright at 1920×1080, embedded as a **base64 `data:` URI** so the deck stays self-contained and offline.

Headline: a sentence, not a label — *"What the drafter actually gets."*
Beneath, mono: the human-review queue count, 16 of 82.

**Re-run `tests/test_slides.py` after every change.** The colour-set-equality and no-external-reference assertions must still pass. Update the tests for the new slide count rather than weakening them.

---

## PART 2 · THE SCREENCAST — record the real product

`docs/video/record_worksheet.js`, using Playwright with `recordVideo`.

**Storyboard — roughly 35 seconds, deliberately slow:**

1. Open `docs/worksheet/index.html`, viewport 1920×1080. **Hold 2 s.**
2. **Smooth-scroll** to a section with a failing designation. Scroll in small steps with ~40 ms between them — a real scroll, not a jump. **Hold 3 s** on it.
3. Scroll to a row where `cfr_resolve` reported `found: false` and the trace shows why. **Hold 4 s.**
4. Scroll to the **human-review queue** section. **Hold 4 s.**
5. Scroll to the **provenance footer** — commit, arm, model. **Hold 3 s.**

**No cursor. No clicking. No highlight boxes drawn over it.** The page is the evidence; let it be read.

If the worksheet is short enough that scrolling looks trivial, **say so and hold longer on each section instead of inventing movement.**

Convert the recording to a clean MP4 segment at 1920×1080, 30 fps.

---

## PART 3 · FRAMES AND CAPTIONS

The video is a sequence of **(PNG, duration)** pairs. Build them, don't hand-time them.

### The caption band

Render captions **into the slide HTML** before screenshotting — do not burn text with ffmpeg. A band across the bottom:

- Full width, height ~150px, background `--ink`, text `--paper`
- **Georgia, 30px, line-height 1.45**, max-width 90ch, left-aligned with the slide's 120px margin
- Sits **below** the slide content — shrink the content area, do not overlap it
- **No caption on slide 1 or the final card**

### Segmenting

Split each slide's script into caption segments of **at most 22 words**. One frame per segment.

**Duration per frame:**

```
duration = max(3.0, words / 2.8)      # ~168 wpm reading speed
```

Round to 0.1 s. **Nothing under 3.0 s**, ever — a caption that flashes is worse than no caption.

### Special handling

- **The bar chart: four frames.** Bar 1 alone → bars 1–2 → all three → all three plus the conclusion line. Each with its own caption segment.
- **The exemplar slide** (the model overriding its own tool): give it **at least 12 s** across its segments. It is the most interesting thing in the deck.
- **The screencast** slots in after the system diagram, replacing whatever caption segments cover the execution beat. **Overlay its captions with ffmpeg `drawtext`** in the same band style, since it is video not a still.
- **Title card 4 s**, no caption. **End card 4 s**: repo URL, `Chinmoy Paul · IIT Guwahati`, nothing else.

---

## PART 4 · ASSEMBLE

`docs/video/build_video.py` — one script, re-runnable, deterministic.

1. Render every frame to `dist/frames/NNN.png` at exactly 1920×1080 via Playwright.
2. Write an ffmpeg **concat list** with per-frame durations.
3. Splice the screencast segment in at its position.
4. **Add a silent AAC audio track** — `-f lavfi -i anullsrc=r=44100:cl=stereo -shortest`. Some players and platforms mishandle a video with no audio stream at all.
5. Encode: `libx264`, `-pix_fmt yuv420p`, `-r 30`, CRF 18, `-movflags +faststart`.
6. Output **`dist/instruction-that-wont-execute.mp4`**.

`dist/` is git-ignored — the MP4 is uploaded, not committed. **The scripts are committed** so the video is reproducible.

---

## PART 5 · VERIFY — measure, do not assert

Report every one of these as a measured value:

- **`ffprobe` duration. MUST be under 5:00.** If it is over, cut caption segments from slides 9 and 10 first, as `script.md` already directs. **Never speed up the video.**
- Resolution exactly 1920×1080; frame rate 30; audio stream present.
- **Total frames, and the shortest frame duration** — must be ≥ 3.0 s.
- **Every caption's word count** — none over 22.
- File size in MB.
- `tests/test_slides.py` still passes, with the count updated not weakened.
- **The deck still opens offline** with zero external references, including the new base64 screenshot.
- **Extract three frames** — one slide, one bar-chart step, one screencast — save them to `docs/evidence/ch13b/` and **look at them**. Report what you actually see, not what you intended.

---

## 🔴 THE STANDARD

Open the finished video and watch it. Then answer honestly:

1. **Could someone with no context follow it with the sound off?**
2. **Does any caption move on before you can finish reading it?**
3. **Does it look like a document, or like a template?** It must look like a document.
4. **Does the execution beat show the real thing, or a picture of the real thing?**
5. **Is there anywhere it feels padded?** If a frame exists to fill time, cut it.

**If any answer is wrong, fix it before you finish.** The operator gets one run at this.

---

## SCOPE FENCE

**Create/change ONLY:** `docs/slides/index.html`, `docs/slides/script.md`, `tests/test_slides.py`, `docs/video/` (new), `docs/evidence/ch13b/` (new), `dist/` (ignored), `docs/progress/CH-13B.md`, `.gitignore` (only if `dist/` needs adding).

**Read-only:** everything else. In particular **do not touch** `README.md`, `STATUS.md`, `PROGRESS.md`, `SUBMISSION.md`, `AI-USE.md`, `src/`, `data/`, `agents/`, `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`.

Commit only declared paths. **Never `git add -A`** — `dist/` must not slip in.

---

## GIT

Atomic commits, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
`python tools/export_session.py CH-13B` before you finish.

---

## FINAL OUTPUT

ONE plain-text block:

```
CHUNK CH-13B REPORT
*** VIDEO       : dist/instruction-that-wont-execute.mp4
                  ffprobe duration = M:SS   (cap 5:00)   resolution   fps   audio stream
                  size MB · total frames · shortest frame duration (must be >= 3.0 s)
                  longest caption in words (must be <= 22)
NEW SLIDES      : system diagram · bar chart · worksheet screenshot - each y/n
                  slide count now · test_slides.py passing? colours still 5?
                  deck still opens offline with 0 external refs? y/n
SCREENCAST      : recorded? seconds · what it shows, section by section
                  is the worksheet long enough to scroll, or did you hold instead?
THE STANDARD    : answer all five questions from the card, honestly
FRAMES INSPECTED: the three you extracted - what you ACTUALLY see in each
API SPEND       : USD 11.6323 unchanged? (must be yes)
FILES · PUSHED SHA · QUESTIONS
TOKENS + COST   : in / out / wall-clock
```

---

## HARD SAFETY RIDER

- No destructive commands, no force-push. **No model calls.**
- Never print, echo or commit the API key.
- **Do not commit `dist/`.**
- **Never weaken a test to accommodate a new slide** — update the expected count, keep every assertion.
- **Never put a number on a slide you have not verified in its artifact.**
- Ambiguity not covered here → `docs/progress/CH-13B.md`, conservative option, continue. **Do not stop and wait.**
