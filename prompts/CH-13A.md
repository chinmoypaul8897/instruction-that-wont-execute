# CH-13A — build the slide deck and the per-slide script

You are a **BUILD session**. **TIME BOX 3 h.** Take the time. This deck carries the video, which is a pass/fail deliverable.

**No arm is re-run. No result changes. No model calls.** API spend must read **USD 11.6323** at the end.

**Runs in parallel with CH-12.** You write **only** to `docs/slides/` and `docs/progress/CH-13A.md`. **Do not touch `README.md`, `STATUS.md`, `PROGRESS.md`, `SUBMISSION.md` or `AI-USE.md`** — another session holds them. **Read numbers from the frozen artifacts, never from `README.md`.**

---

## 🔴 THE ONE TEST THIS MUST PASS

When you finish, open it and ask: **"does this look like a pitch deck?"**

**If yes, you have failed.** Start the styling again.

It must look like **a legal exhibit or an audit report** — a document, not a presentation. The subject is government paperwork and forensic precision. The deck should feel like something submitted into evidence.

---

## READ FIRST

1. `CLAUDE.md` — hard rules **14 and 15**. Every number on a slide is copied from a committed artifact, and you verify it there.
2. `docs/video-script.md` — the seven beats and their timings. **The deck serves that script.**
3. `context/01-PROBLEM-PDF.md` §8 deliverable 03 — the verbatim requirement
4. `CHANGELOG.md` — predictions and measured results

---

## THE BINDING REQUIREMENT

> *"Submit a video of up to 5 minutes. Begin with **the problem and simple baseline**, then walk through **one realistic execution from start to finish**. Show **the final comparison** and briefly explain **the changelog**. Highlight **the change that contributed most** as well as **one experiment you removed**."*

Nothing in the brief mentions camera, screen recording or format. **Slides are compliant.**

**But "walk through one realistic execution from start to finish" binds slides 5–8.** Those four must show **real committed artifacts** — actual JSON, actual terminal output, actual government text. **A diagram of a pipeline does not satisfy it.** If you find yourself drawing boxes and arrows for those slides, you have substituted a picture for the evidence.

---

## FORMAT

- **One self-contained HTML file:** `docs/slides/index.html`
- **Opens offline by double-click.** No CDN, no external font, no external image, no framework. Everything inline: CSS, JS, and any image as a `data:` URI.
- **Fixed 1920×1080 canvas**, scaled to fit the viewport, so recording is predictable.
- **Arrow keys / space** advance. `F` toggles fullscreen. Nothing else.
- **A test** — `tests/test_slides.py` — that fails if the HTML contains `http://`, `https://` or `src="//`.

---

## THE DESIGN SYSTEM — use these exact values

### Colour

```
--paper      #FBFAF7   warm off-white, document stock. NOT #FFFFFF.
--ink        #1A1A18   near-black, slightly warm
--ink-muted  #6B6862   secondary text, captions
--rule       #D8D4CC   hairlines only, 1px
--accent     #9B2226   OXBLOOD
```

**The accent has exactly one meaning: this did not work.** Failed predictions, missed criteria, the wrong-direction result. **Nothing else may be red — not headings, not emphasis, not decoration.**

**The significant result gets NO colour.** It is set in plain ink. The deck's logic is *we mark what failed; what worked is simply stated.* Do not add green. Do not add blue. **Five colours total, and one of them is a hairline.**

### Type

```
--serif  Georgia, 'Times New Roman', serif        headlines and prose
--mono   Consolas, 'SF Mono', 'Courier New', monospace   EVERY machine-produced value
```

**System fonts only** — the deck must open offline. **No sans-serif anywhere except tiny uppercase labels.**

**Rule: if a value came from a computer, it is monospace.** Numbers, JSON, file paths, terminal output, p-values, section designations. If a human wrote it, it is serif.

Sizes at 1920×1080:

```
hero number    180px / weight 400 / letter-spacing -0.03em
headline        64px / serif / line-height 1.15 / max-width 24ch
body            28px / serif / line-height 1.5 / max-width 60ch
mono data       22px / line-height 1.6
label           15px / uppercase / letter-spacing 0.14em / --ink-muted
slide number    14px / mono / --ink-muted / bottom-right
```

### Layout

- Margins **120px** left and right, **100px** top and bottom.
- **Left-aligned. Asymmetric. Never centre a slide's content**, except the single hot-take slide.
- One idea per slide. **If a slide needs two ideas, it is two slides.**
- Hairline rules to separate, never boxes. **No cards, no shadows, no rounded corners, no fills.**

### 🔴 BANNED — every one of these is an AI tell

gradients · icons of any kind, including emoji · rounded cards · drop shadows · centred body text · three-bullet parallel structure · slide titles like *"Overview"*, *"The Solution"*, *"Key Takeaways"*, *"Conclusion"* · progress bars · logos · stock imagery · more than one accent colour · any transition other than an instant cut · bullet lists where a sentence works

**Headlines are sentences or numbers, not labels.** *"The instruction quoted text that was not there"* — not *"The Problem"*.

---

## THE THIRTEEN SLIDES

Pull every quoted artifact from the paths given. **Verify each number in its source file and say in your report where you got it.**

**1 · Title.** Project name. One sentence beneath: what it does. Bottom-left, small: `Chinmoy Paul · IIT Guwahati`. Nothing else. No date, no logo.

**2 · A real defective instruction.** Verbatim from `data/amdpars/amdpars.jsonl` — pick one whose anchor genuinely did not resolve. Monospace, generous size. **The quoted text that was not there, marked in oxblood.** Label above: `FEDERAL REGISTER · AMENDATORY INSTRUCTION`.

**3 · What happened.** The actual NARA editorial note for that section, verbatim from `data/ednotes/defect_notes.jsonl`. Label: `WHAT THE CODE OF FEDERAL REGULATIONS SAYS TODAY`. One serif line beneath: the rule did not codify.

**4 · The baseline.** The real prompt from `agents/B0.md`, monospace, trimmed to what fits. Then the hero number **47.6%** with `n = 82` beneath in mono. One serif line: the instruction alone does not contain the answer.

**5 · The input.** The instruction plus an excerpt of the point-in-time CFR text the agent was given. Two columns, hairline between. Label: `WHAT THE AGENT RECEIVES`.

**6 · The tool call.** The real `cfr_resolve` invocation and the **real JSON it returned**, from `docs/trajectories/arms/A1-rep1.jsonl`. Monospace, syntax left plain. Label: `DETERMINISTIC RESOLUTION`.

**7 · The emitted note.** The real A1 output for that item — `verdict`, `failing_designation`, `failure_class`, and the `resolution_trace`. Label: `WHAT THE AGENT WRITES`. One serif line: the verdict is derived in code from the trace, so it cannot be right for the wrong reason.

**8 · The exemplar.** From `docs/evidence/ch06-a1/EXEMPLAR-composition.md` — the case where the model **overrode its own resolver**, named the tool's limitation in the published note, and ruled correctly. Quote the note verbatim. This is the most interesting slide in the deck; give it room.

**9 · The comparison.** A table, hairlines only. Rows: `B0` · `B0-agent` · `A1` · `B0′`. Columns: accuracy, gap, McNemar p. From `docs/evidence/checkpoint/checkpoint-result.json` and `docs/evidence/ch06-a1/a1-result.json`. **`p = 0.4244` and the word `not significant` in oxblood.** The +18.3 pp result in plain ink.

**10 · Predictions against measurements.** From `CHANGELOG.md`. `Iteration 1 · predicted +8 pp · measured −9.8 pp` — **the measured value in oxblood**. Then iteration 2. One mono line beneath: the prediction was committed to git **764 seconds** before the arm ran.

**11 · The composition — the only animated slide.** Three lines revealed one per arrow-press:

```
tool alone      −9.8
skill alone     −1.2
together        +6.1
```

The two negatives in oxblood, `+6.1` in plain ink. Then a fourth reveal, one serif line: *neither capability helps alone.* Instant reveals — **no fades, no slides, no easing.**

**12 · What we removed.** The leakage probe: predicted accuracy would rise, **measured a 6.1 pp fall** — the fall in oxblood. Label: `PRE-REGISTERED PREDICTION · WRONG`.

**13 · The hot take.** One sentence, serif, large, centred — **the only centred slide in the deck.** Nothing else on it.

> A verification agent's grounding corpus is a precision instrument, not a recall instrument — and if you hand it the document, measure *which class* got better, because the average will lie to you.

---

## THE SCRIPT — `docs/slides/script.md`

Alongside the deck, produce the read-aloud script.

- **Per slide:** the slide number, a target duration, a cumulative timestamp, and the **word-for-word** line to read.
- **Total must land at 4:10 or under**, against the 5:00 cap.
- Written to be **read aloud**: short sentences, no subordinate clauses, no words that trip the tongue.
- **The failures are stated flatly, in the same register as everything else.** Not apologetically.
- Mark where to press the arrow key on slide 11.

Base it on `docs/video-script.md`'s seven beats. Tighten the wording for speech.

---

## SELF-CHECK BEFORE YOU FINISH

Open the deck and answer these in your report:

1. Does it look like a pitch deck? **Must be no.**
2. Count the colours actually used. **Must be 5 or fewer.**
3. Is every machine-produced value in monospace?
4. Do slides 5–8 contain **real artifact text**, or a drawing of a pipeline?
5. Is there any icon, gradient, card, shadow or rounded corner? **Must be none.**
6. Is any slide title a label rather than a sentence or a number?
7. Does it open with the network off, from a fresh copy of the file alone?
8. Read the script aloud with a timer. **What was the real duration?**

---

## SCOPE FENCE

**Create/change ONLY:** `docs/slides/index.html`, `docs/slides/script.md`, `tests/test_slides.py`, `docs/progress/CH-13A.md`.

**Read-only, everything else.** In particular do not touch `README.md`, `STATUS.md`, `PROGRESS.md`, `SUBMISSION.md`, `AI-USE.md` — **CH-12 holds them**. Per `CLAUDE.md` §Parallel sessions, commit only your declared paths, never `git add -A`, and `git pull --rebase` before pushing.

---

## GIT

Atomic commits, every one carrying:
`Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
`python tools/export_session.py CH-13A` before you finish.

---

## FINAL OUTPUT

ONE plain-text block:

```
CHUNK CH-13A REPORT
DECK            : slides built · opens offline from the file alone? y/n
                  self-contained test passes? y/n
SELF-CHECK      : looks like a pitch deck? (must be NO) · colours used (<=5) ·
                  every machine value monospace? · icons/gradients/cards/shadows? (must be 0)
                  any slide title that is a label? (must be none)
REAL ARTIFACTS  : slides 5-8 - which file each quotation came from, per slide
NUMBERS         : each figure + the artifact path you verified it in
SCRIPT          : total duration read aloud with a timer = M:SS  (cap 5:00)
                  per-slide timestamps present? y/n
PARALLEL        : files committed (must be only the four declared) · rebase clean?
API SPEND       : USD 11.6323 unchanged? (must be yes)
FILES · PUSHED SHA · QUESTIONS
TOKENS + COST   : in / out / wall-clock
```

---

## HARD SAFETY RIDER

- No destructive commands, no force-push. **No model calls.**
- Never print, echo or commit the API key.
- **Never put a number on a slide you have not verified in its artifact.** If you cannot find it, leave the slide incomplete and say so.
- **Never `git add -A`** — CH-12 is running.
- Ambiguity not covered here → `docs/progress/CH-13A.md`, conservative option, continue.
