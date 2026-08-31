# Video script — 5 minutes maximum

**Target 4:10. Hard cap 5:00 — check the final file is under 5:00, not 5:0x.**

**Record to this script. Do not narrate live** — live narration runs long and rambles, and the brief names seven specific beats.

**Upload unlisted to YouTube by 14:00 UTC.** Processing can take hours. A finished video still processing at 17:55 is a missing deliverable.

---

## Setup

- Screen recording + your voice. Windows: **Win + G** (Xbox Game Bar) or OBS.
- Have open and ready to switch between: `README.md`, a terminal, `docs/evidence/ch06-a1/EXEMPLAR-composition.md`, `CHANGELOG.md`.
- Do a 20-second test first — **check the audio actually recorded.** Silent video is the single most common failure here.
- Retakes are fine. Nobody records this in one pass.

---

## BEAT 1 — The problem · 45 s
### Show: a real amendatory instruction on screen

> "US federal agencies publish rules that amend the Code of Federal Regulations. The instructions look like this — *in section 433.2, remove this exact text and add this in its place.*
>
> If the quoted text isn't there — a comma out of place, the paragraph already renumbered by an earlier instruction — the Office of the Federal Register **can't execute it**. The rule doesn't codify. The National Archives publishes a note saying so, and it stays in the CFR permanently.
>
> The person who has this problem is a regulations drafter clearing a rule before publication. She's working against a statutory deadline, and **the instruction carries no evidence of its own executability.** She writes against the text she believes is codified; OFR executes against the text that actually is.
>
> This is not really about the Federal Register. It's a batch of edits, each individually valid, that fail against the real target — migrations, refactors, config rollouts. The Federal Register is just the one place where that problem has **public, government-authored ground truth.**"

## BEAT 2 — The simple baseline · 30 s
### Show: `agents/B0.md`

> "The baseline is one prompt. Give a model the amendatory instruction and ask whether it will execute. Nothing else — no CFR text, no tools.
>
> On 82 items it scores **47.6 percent.** That's a coin flip, and it should be: the instruction alone genuinely does not contain the answer."

## BEAT 3 — One realistic execution, start to finish · 90 s
### Show: the terminal, then `EXEMPLAR-composition.md`

> "Here's the full system on one case.
>
> It reads the amendatory instructions, and for each one it calls a deterministic resolver against the CFR text **as it stood on the publication date** — is this quoted string actually present, does this paragraph designation actually resolve.
>
> Then it emits **the editorial note the National Archives would have to publish.** Not a yes-or-no — the failing designation, the failure class in NARA's own vocabulary, and the full resolution trace. The verdict is derived in code from that trace, so the system can't be right for the wrong reason.
>
> On this case — 40 CFR 75.6 — something I didn't expect happened. The model **overrode its own resolver.** The tool reported the target as absent; the model read the surrounding text, saw the tool couldn't see nested designations, said so in the published note, and ruled *target already exists* — correctly.
>
> And when it can't resolve — 16 of 82 items — it routes to a human queue. Those trigger conditions are computed in code from the trace. The model is never asked whether it's confident."

## BEAT 4 — The comparison · 45 s
### Show: the results table in `README.md`

> "Two results, and the second is a null.
>
> **Giving the agent the CFR text moves it from 47.6 to 65.9 percent. Plus 18.3 points, p equals 0.006.** That's real, and an independent reviewer reproduced every figure from scratch to zero error.
>
> **Adding our two capabilities on top gets 71.9 percent. Plus 6.1 points — p equals 0.42. That is not significant.**
>
> Our pre-registered success criterion required a gap of 8 points, p under 0.05, n of at least 84, and 80 percent absolute. **We met none of the four.** The corpus yields 82 items, two short. We did not move the number — it's published unmet."

## BEAT 5 — The changelog · 40 s
### Show: `CHANGELOG.md`

> "Every iteration was predicted before it ran, and the predictions are timestamped in git.
>
> Iteration one — the resolver tool. **Predicted plus 8 points. Measured minus 9.8.** Wrong direction. Marked removed.
>
> Iteration two — the written execution procedure. Predicted 0.81, measured 0.72.
>
> A third capability, a memory ledger, was declared **not built in advance** and ships as a counted removal with the measurement that justified it."

## BEAT 6 — The change that contributed most · 20 s
### Show: the composition table

> "The tool alone made it **worse** — minus 9.8. The procedure alone made it **worse** — minus 1.2. Together: **plus 6.1.** Seventeen points above what adding them predicts.
>
> Neither capability helps on its own. It composes because **the written procedure repairs a defect in the tool** — the resolver can't see nested designations, in 60 of 128 cases, and every misfire is one-way. We found that because it cost us a point, and we left it unfixed and documented."

## BEAT 7 — One experiment removed · 20 s

> "We predicted that giving the agent the *current* CFR text instead of the point-in-time text would raise accuracy, because the current text leaks the answer. **It fell 6.1 points.** The prediction was wrong and it's published as wrong.
>
> The lesson we'd carry forward: a grounding corpus is a precision instrument, not a recall one. **If you hand an agent the document, measure which class got better — the average will lie to you.**"

---

## Delivery

- **Slow down.** Reading a script aloud always comes out faster than it reads.
- **Say the null results in the same tone as the good ones.** They're findings, not confessions.
- One pause after "That is not significant." Let it land.
- If you fluff a line, stop and redo that beat. Don't fix it in narration.

## After recording

1. Check duration is **under 5:00**.
2. Upload to YouTube, **Unlisted**.
3. **Open the link in a browser you are not signed into** and confirm it plays with audio.
4. Put the URL in `README.md`, `SUBMISSION.md`, and the HackerEarth form.
