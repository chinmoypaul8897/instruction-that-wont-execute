## 0. Reading note before the list

Five auditors read `prompts/CH-00.md` at different revisions. The file at **09:18 IST (03:48 UTC)** now contains **Q1 ANSWERED** (paid Anthropic API, `claude-sonnet-5`, same model every arm, budget USD 20–30) and **Q2 ANSWERED** — the HackerEarth submission form, read from inside it: **four fields (Title / Description / Video URL / Source Code), Video is a URL not an upload, Source Code is an uploaded ZIP capped at 50 MB, and "Save as Draft" exists.** That retires two of the loudest findings and creates three new ones. Everything below is reconciled against the file as it stands, and against the working tree as it stands (446 MB, no `.git`, three Claude Code session JSONLs totalling 20.5 MB on disk).

**The single sentence that matters:** the Q2 rulings are binding spec written into a *prompt seed*. `plan.md` and `PROCESS.md` contain no trace of them. No chunk builds the 50 MB zip, no chunk saves the draft, no chunk uploads the video early, no chunk writes the Description field. The knowledge exists; the execution is unowned.

---

## 1. DISQUALIFYING — fix before anything else

### D1 · The first commit publishes a 446 MB tree containing the organiser's copyrighted material, third-party IP you cannot assign, and your own private information

> **"Keep credentials and private information outside the submission."** — 01-PROBLEM-PDF.md §7 ground rule 08
> **"Use every tool and component according to its license and service terms."** — §7 ground rule 03
> **"Submissions are governed by the Hackathon Participation Agreement (accepted at registration), under which micro1 owns submissions and may use them for AI model training and evaluation."** — 00-MASTER-CONTEXT.md §11

**Why the plan misses it.** `prompts/CH-00.md` §1 says `git init` in this folder with a six-pattern denylist: `.env`, `__pycache__/`, `*.pyc`, `.venv/`, `node_modules/`, `scraper/node_modules/`. Verified on disk, that commits:

| Path | Size | Problem |
|---|---|---|
| `d.pdf` | 132 K | micro1's own problem PDF, republished |
| `context/media/challenge-video.mp4` + `images/` + `slices/` + `screenshots/` + `raw/` | ~30 M | micro1 brand film + 9 HackerEarth assets + scraped page DOM |
| `context/01-PROBLEM-PDF.md` | 30 K | verbatim ten-page extraction of the unreleased brief |
| `context/02-ABOUT-ME.md` | 18 K | personal dossier; contains `[redacted - operator contact detail, ground rule 08]` (confirmed, 1 hit) |
| `context/me/raw/resume.pdf`, `linkedin.txt`, `portfolio.html`, `github/*.json` | — | private info under rule 08 |
| `context/me/readmes/acumen.md` | — | reads verbatim: *"All rights reserved… not licensed for reuse or redistribution. The trading strategy it implements is used with the owner's permission."* Third-party IP being assigned to micro1. |
| `killtest/` 179 M · `replay/` 96 M · `probe/` 22 M · `scraper/` 57 M · `aec/` · `bip/` | 354 M | three dead projects; includes `killtest/redesign_r1/pool_union.json` at 78.9 MB |

Only the credentials half of rule 08 is defended (CLAUDE.md rule 12). The only sweep in the plan is CH-14's secret scan, which looks for keys and would find none of this. **And with Q2's 50 MB ZIP cap now known, this is no longer only a licence problem — a 446 MB tree cannot produce a compliant submission archive at all.**

**Fix.** Rewrite `prompts/CH-00.md` §1 so the `.gitignore` is authored and committed **before** any `git add`, as an allowlist-shaped denylist:

```
.env
__pycache__/
*.pyc
.venv/
node_modules/
d.pdf
hz.html
wl.html
cfr2024t40v5.xml
fr20240103.xml
aec/
bip/
killtest/
probe/
replay/
scraper/
context/media/
context/images/
context/slices/
context/screenshots/
context/raw/
context/me/
context/02-ABOUT-ME.md
context/01-PROBLEM-PDF.md
BUILD-PHASE-1-PROMPT.md
DIVERGENT-RESEARCH-PROMPT.md
KILL-TEST-PROMPT.md
```

Then add a CH-00 done-when: *"print `git ls-files` in full and assert the count is under 60; assert no tracked file exceeds 25 MB."* Write the ship/no-ship ledger into `PROCESS.md` §3 so it is a rule, not a prompt detail. Amend `CLAUDE.md`'s Precedence line to read `context/01-PROBLEM-PDF.md` **(local, not redistributed)** — as written, the precedence chain requires that file to ship.

Keep `context/00-MASTER-CONTEXT.md` and the four `context/0Nb-*-raw.json` agent outputs (they are your own work and they carry deliverable-4 value). `killtest/` evidence arrives via the CH-01b migration, not by sweeping the directory in.

**Chunk:** `prompts/CH-00.md` §1 + `PROCESS.md` §3. **Hours: 0.5.** After the first commit this needs a history rewrite.

---

### D2 · Ground rule 02 has zero implementation, and the first commit will assert the opposite of the truth

> **"Make it clear what existed before the competition and what you added."** — §7 ground rule 02
> **"Clear statement of what pre-existed vs. what was built for the competition"** — §12 checklist, Deliverable 1

**Why the plan misses it.** No `PROVENANCE.md` in `PROCESS.md` §3's Files table, none in CH-00's skeleton list, no provenance slot in CH-11's README order, and the string does not appear in `plan.md`, `PROCESS.md`, `CLAUDE.md` or `CONTEXT.md`. The facts: `context/` and `scraper/` are dated **2026-08-27 ~21:45 UTC**, seventeen hours before the **2026-08-28 15:00 UTC** kickoff; no project source exists. A single undifferentiated initial commit dated 2026-08-30 asserts, falsely, that all of it was produced during the competition — while the file mtimes inside it say otherwise. The validation screen runs integrity and plagiarism checks.

**Fix.** Architect writes `PROVENANCE.md` now, three dated blocks:

- **Before kickoff** — 2026-08-27 ~21:45 UTC: public HackerEarth page scraped, `scraper/` recon scripts written. No problem-specific work was possible; the brief did not exist yet. Ground rule 01 expressly permits the reused Playwright tooling — name it.
- **Kickoff → CH-00** — 2026-08-28 15:00 → 2026-08-30 03:20 UTC: brief read, four candidate projects researched, three killed, `CONTEXT.md` v1.0 written. Artifacts `context/03`–`08` plus the four raw agent JSONs.
- **After CH-00** — every line of project source, the corpus, the eval set, the agent.

Then split the import: **commit A** = `.gitattributes`; **commit B** = `PROVENANCE.md`; **commit C** = pre-existing research, message `import: pre-existing research created before kickoff — see PROVENANCE.md`; **commit D onward** = competition work. Capture `ls -la --time-style=full-iso` over `context/` and `scraper/` into `docs/evidence/provenance/` so the mtimes back the claim. Link from the README's first screen.

**Chunk:** architect, before CH-00; commit-splitting instruction into `prompts/CH-00.md`. **Hours: 0.75.**

---

### D3 · Nothing submits, nothing builds the archive, and the Q2 rulings are stranded in a prompt seed

> **"A valid submission must be timely, complete, original, policy compliant, and reproducible, and include the required repository, archive, tests, README, agent-use evidence, and demo video."** — 00-MASTER-CONTEXT.md §12 FAQ
> **"Submissions close. Late or incomplete entries are not accepted."** — §7 timeline row 5

**Why the plan misses it.** `plan.md` ends at CH-14 with *"Repo made public at submission"* — a trailing clause with no owner. Five auditors out of five raised this independently. Q2 already tells you the archive is the **Source Code ZIP, max 50 MB**, that the video is a **URL**, and that **"Save as Draft"** exists — and none of that appears in `plan.md` or `PROCESS.md`. Phase 3 holds five chunks in twelve hours with no submit buffer.

**Fix.** Add **CH-15 · SUBMIT** with a wall-clock trigger, not a dependency, and a two-stage policy the rules explicitly permit (*"Revisions are allowed until the deadline; only the latest complete submission is evaluated"* — Eligibility 3):

1. **DRAFT-1 at 2026-08-31 12:00 UTC (T−6h).** Save a complete-but-imperfect draft: all four fields filled, placeholder video if needed. From here the project is insured.
2. **SUBMIT at 16:00 UTC (T−2h).** `git archive --format=zip HEAD -o dist/submission-<sha>.zip`; assert **< 50 MB**; extract to a fresh temp dir and run the **Tier-1 replay from the extraction**, not from the clone; record the zip's SHA-256 in the README.
3. Flip repo public → open the URL in a private window with no GitHub session → `git clone` the HTTPS URL with no credentials → confirm the video plays logged out.
4. Paste the four fields. Screenshot the confirmation, commit it.
5. **17:00 UTC is the last permitted touch. Nothing after 17:30.**
6. **Revision discipline, one line in the card:** every submission event ships a complete four-field package. Never replace a complete submission with a partial revision — "only the latest **complete** submission is evaluated" admits a reading where a partial revision destroys a complete one.

Also fold Q2's C1/C2/C3 into the chunks that must honour them: C1 (extract-then-freeze, never whole title XMLs) into **CH-03**'s scope; C2 (curated representative trajectory set in the zip, complete set in the repo, **selection rule written down**) into **CH-12**; C3 (unlisted YouTube uploaded early) into the video split at D6.

**Chunk:** new CH-15; scope lines into CH-03 and CH-12. **Hours: 0.25 to write the card now + 1.0 to execute.**

---

### D4 · Deliverable 4 covers the eval arms and omits the agents that actually build the project — and the evidence is volatile

> **"Include representative trajectories for every agent you used. Make each trajectory easy to follow from the agent instructions to the final result. Show what the agent did and how its tools responded. Capture the feedback that shaped its next step as well as any retries or human checkpoints."** — §8 deliverable 04
> **"Coding-agent use is required. You must disclose the tools you used and submit the required trajectories for evaluation."** — 00-MASTER-CONTEXT.md §2

**Why the plan misses it.** `src/runlog.py` instruments programmatic model calls — B0, B0-agent, B0′, A1. The ~15 fresh Claude Code BUILD/REVIEW sessions that `PROCESS.md` is built around pass through it zero times, and `PROCESS.md` §3 states the opposing policy outright: *"Chat history is not a record."* The submission will disclose in `AI-USE.md` that a coding agent wrote every line while shipping no trace of that agent, on an event whose validation screen names **trace-integrity** as a gate check. Verified on disk right now:

```
C:\Users\chinm\.claude\projects\c--Users-chinm-micro1-engineering-challenge\
  9acf056f-….jsonl   15,651,473 bytes   (this session, still being written)
  3b661cd3-….jsonl    2,697,409 bytes
  6ab8522b-….jsonl    2,166,960 bytes
```

That is deliverable 4's verbatim checklist already on disk. Nothing copies it. Session directories are not permanent.

Second half of the same gap: `CONTEXT.md` line 8 boasts the spec *"survived adversarial review by 13 and 15 independent agents respectively."* Their raw outputs exist (`context/03b`, `04b`, `05b`, `08b-raw.json`, ~900 KB total) and no chunk ships them, so the file declared LAW carries an unevidenced claim about 28 agents.

**Fix.** Three moves, the first before CH-00 runs:

1. **CLAUDE.md, sixth end-of-session duty:** *"Copy your own session JSONL from `~/.claude/projects/<slug>/<uuid>.jsonl` to `docs/trajectories/build/<CH-id>-<role>-<uuid>.jsonl`, strip absolute home paths, grep for `sk-ant`/`AIza`/`Bearer `, commit."* CH-00 creates the directory. Every session from the first captures itself.
2. **CH-12** selects representatives with a **written mechanical rule** (C2 makes this mandatory anyway): one BUILD session, one REVIEW that returned FAIL, one eval run of each arm — a FAIL review is the best human-checkpoint evidence in the project. Add `docs/trajectories/README.md` as an index stating the selection rule, so curation reads as method rather than cherry-picking.
3. **`docs/trajectories/pre-build/`** holds the four design-swarm JSONs with a one-page index (swarm, date, model, what it was asked, what it changed in the spec), labelled *design-phase agents, pre-dating CH-00* — which also discharges half of D2 for free. If they cannot be packaged, delete the "13 and 15 independent agents" clause from `CONTEXT.md` rather than shipping an unevidenced boast.

**Chunk:** CLAUDE.md + `prompts/CH-00.md` now; CH-12 for selection. **Hours: 0.25 now, 0.75 at CH-12.**

---

### D5 · Phase 1 is budgeted at ~5 h and its own review mechanics make it a 16–20 h phase, with no strike limit, no AMBER action, and no numeric fallbacks

> **"HARD CUTOFF: at T−12h (2026-08-31 06:00 UTC), Phase 3 begins regardless of Phase 2 state."** — PROCESS.md §7
> **"Review mechanics (gated chunks): … reimplement the load-bearing logic from `CONTEXT.md` alone, importing nothing from the project, and diff · mutation-test critical operators"** — PROCESS.md §6

**Why the plan misses it.** A from-scratch reimplementation plus a mutation campaign is 1.5–3 h of session time. Phase 1 mandates three of them (CH-02, CH-03, CH-04) on top of a network harvest, three hand-verified golden rules, an annual-edition download, an exact-count-matched eval set and a permutation null. Five hours is off by a factor of three. Compounding it, four exits are undefined:

- **No strike limit.** `PROCESS.md` §2 says only *"on FAIL issues a fix prompt."* The loop has no exit. Two FAILs on CH-02 and Phase 2 is gone.
- **AMBER has no action.** `plan.md` defines what to *print* on AMBER; both `PROCESS.md` §7 and `plan.md` say Phase 2 runs *"only if GREEN"*. AMBER is the single most likely outcome of an underpowered paired test at n=84, and it is the one branch with no behaviour.
- **RED ships "as dead" with no spec for what a dead project ships**, while every Phase 3 card assumes A1 exists.
- **CH-02's `≥ 0.90` and CH-03's `≥ 42 pairs` have no pre-registered fallback**, and hard rule 5 correctly forbids moving them after seeing a result. At 0.87 the operator's only moves are burn hours or move the threshold — and moving it is the one act that would falsify the integrity story, visibly, in git history.

**Fix — all four, written before any number exists (this is what makes it pre-registration rather than rationalisation):**

- **Re-estimate.** Write 16–20 h into `PROCESS.md` §7. Then tier the review: **MANDATORY core** = rerun suite from clean and reproduce the count + reimplement-from-spec + diff + rebuild each probe on the pre-change commit (45–70 min). **IF-TIME** = mutation testing, secret sweep (CH-14 duplicates the latter). Architect picks the tier per chunk and records it as a ruling.
- **Two-strike rule** into `PROCESS.md` §6: *"A gated chunk gets at most two fix→re-review rounds. On a second FAIL the architect either accepts the chunk with its open findings copied verbatim into the README's LIMITATIONS section and the review report shipped as-is, or invokes the chunk's pre-registered fallback. The decision and its timestamp go in QUESTIONS.md."*
- **AMBER branch:** *"Phase 2 PROCEEDS. The checkpoint result enters `CHANGELOG.md` as the Baseline row with exact n, gap and p. `GOOD.md` is unchanged. The agent is built to move the gap, not to rescue the p-value. If A1 is still p ≥ 0.05, the README leads with effect size, CI, and the n required for power."*
- **RED branch:** *"CH-05/06/07 are cut. The corpus, attributor, scorer, permutation null and the three baseline arms become the contribution. CH-08 becomes 'why the gap did not open, measured'. CH-10 renders B0-agent traces. Deliverable 4 is satisfied by baseline-arm trajectories."*
- **Numeric fallbacks:** CH-02 — *"if global completeness lands in [0.80, 0.90), restrict the eval set to FR documents with per-document completeness ≥ 0.90, publish the restriction as a named rung of the exclusion ladder with its count, report both figures. Below 0.80 the attributor is a documented failure and the headline is withdrawn."* CH-03 — *"if pairs land in [30, 42), report the real n and state in `GOOD.md` and the README the effect size the sample can and cannot detect. **Do not relax the exact instruction-count match to inflate n** — that is precisely how a predecessor died."*
- **MVS drop list** into `PROCESS.md` §7, in drop order (last dropped last): 1 public repo + < 50 MB zip + submitted form · 2 README with user/bottleneck/value/changelog/failure-mode/hot-take · 3 Tier-1 offline repro reaching ONE headline number · 4 video ≤ 5 min · 5 trajectories + `AI-USE.md` · 6 everything else. Anything below the line ships with a stated LIMITATION, never silently absent. **T−6h ritual: read the list aloud and mark each item done/not-done before touching more code.**
- **One protected 4.5 h sleep block**, placed against the govinfo bulk downloads and the checkpoint sweep, with the next two chunk prompts pre-written so you wake to a queue. Hard alarms at **06:00 UTC** (cutoff) and **12:00 UTC** (draft) and **16:00 UTC** (submit).

**Chunk:** `PROCESS.md` §6 + §7, `plan.md` CHECKPOINT/CH-02/CH-03 cards. **Hours: 1.0.**

---

### D6 · The video cannot be uploaded early because CH-13 sits after the cutoff, and CH-14 — the rehearsal that could find a fatal defect — runs last

> **"Submit a video of up to [5 minutes]."** — §8 deliverable 03
> **"A project that cannot be run or verified may be disqualified before rubric scoring."** — 00-MASTER-CONTEXT.md §9

**Why the plan misses it.** CH-13's own card says *"Upload early; processing can take hours"* — and CH-13 is the fourth of five Phase-3 chunks, which by `plan.md`'s own rule cannot begin before 06:00 UTC. Earliest plausible upload is T−4h. Q2's C3 says the same thing the card says and neither is schedulable. Meanwhile CH-14 (clean-clone rehearsal) runs **last**, at ~T−2h, so a broken manifest surfaces with no time to fix it. There is also **no script** — CH-13 is a beat list, to be improvised at hour 68, which is exactly the finish the 20-point anti-slop clause is hunting.

**Fix.**
- **Split CH-13.** **CH-13A** (recordable during Phase 2, as soon as CH-04 lands): problem, simple baseline, one realistic execution, changelog structure, the removed experiment. Upload immediately as an unlisted YouTube placeholder — it proves the pipeline and starts the processing clock. **CH-13B** (Phase 3): record only the final-comparison segment, splice, re-upload.
- **Write both scripts at the CHECKPOINT**, as timed beat sheets: **GREEN** (problem 45 s / baseline 30 s / execution 90 s / comparison 45 s / changelog 40 s / biggest contributor 20 s / removed experiment 20 s) and **AMBER-RED** (same seven beats, where "the change that contributed most" becomes "the change that did not move the number, and what that tells you"). Pick one at the cutoff. Record to script; never narrate live.
- **Reorder Phase 3:** CH-14a rehearsal **first**, against whatever exists → CH-12 → CH-11 → CH-11b voice pass → CH-10 → CH-13B → CH-14b final rehearsal → CH-15.
- **Done-when on the video:** duration under 5:00 (not 5:0x); link opens and plays in a browser profile with no Google session; link recorded in README, the HackerEarth Video URL field, and the Description.

**Chunk:** `plan.md` Phase 3 reorder + CH-13 split. **Hours: 0.5 to replan; 1.0 for the scripts at CHECKPOINT.**

---

### D7 · Registration is nowhere recorded, and the organiser's support window closes in ~20 hours

> **"Entries are individual only. A participant may register once and submit one final entry."** — 00-MASTER-CONTEXT.md §8 Eligibility 3
> **"Final-day checkpoint | Sun, Aug 30 · 23:59 | Submission reminder, known issues and support escalation window"** — §7 timeline row 4

**Assessment, honestly downgraded.** Three auditors called this a total-loss unknown. Q2's field list — *"exactly four required fields… Save as Draft alongside Submit"* — can only have been read from inside the submission form, which is strong evidence registration completed. But it is not recorded anywhere, and the support window is the last moment a human at micro1 is on duty before deadline day.

**Fix.** Five minutes now: confirm the page shows Submit rather than Register, screenshot to `docs/evidence/access/registration.png`, record as **Q0 CLOSED** in QUESTIONS.md with its UTC timestamp. Set an alarm for **2026-08-30 23:45 UTC**: read the challenge page and any organiser mail; if anything is anomalous, email `yeison@micro1.ai` *then*, not Monday. Ask in the same message for notes from the Aug 27 pre-event briefing on submission format — it costs one sentence.

**Chunk:** operator action now, `QUESTIONS.md` Q0; alarm noted in `PROCESS.md` §7. **Hours: 0.25.**

---

## 2. MAJOR POINT LOSS

Ranked by points at risk.

### M1 · The CH-00 prompt contains a spec contradiction that will stop the first session · 0.25 h · do this in the same fifteen minutes as D1

`prompts/CH-00.md` instructs the build session to seed `CHANGELOG.md` with *"the four-column table from `PROCESS.md` §5."* **`PROCESS.md` §5 contains no table** — it contains a seven-field iteration card (Observed failure / Hypothesis / Prediction / Evidence path / Result / Decision / Learning). Under hard rule 1 the session must STOP, costing an architect round-trip at hour zero; under pressure it will invent one instead.

This is also a real scoring gap. The PDF mandates the structure verbatim:

> **"Add a clearly labeled Improvement Changelog using the structure above."** — §8 deliverable 01, referring to §4's **STAGE / WHAT YOU TRIED AND WHY / EVIDENCE / DECISION-LEARNING** table with a Baseline row, one row per iteration, and a Final row.

**Fix.** Write the exact four-column table into `PROCESS.md` §5 above the card. `CHANGELOG.md` is table-first — Baseline / Iteration 1 tool / Iteration 2 skill / Iteration 3 memory / **Removed 1** / **Removed 2** / **Control B0′** / Final — with each EVIDENCE cell a relative path into `docs/evidence/`, and the full iteration cards below as backing detail. The README **embeds the table**, not a link to it. *Risk: 15 pts (Measured Improvement) plus one hour of hour-zero schedule.*

### M2 · The anti-slop fix is not merely missing — `PROCESS.md` §0 forbids it · 1.5 h · 20 pts

> **"…with the finish of something a person would sign their name to rather than an obvious AI generated draft."** — §6 End to End Quality (20 pts)

Known item (a). **The planned fix is worse than inadequate: the process's founding principle vetoes it.** `PROCESS.md` §0 states *"no artifact is written twice… If something has to be reconstructed at the end, the process was wrong."* Under that rule a session proposing to rewrite the README in the human's voice is violating the process. Four of five auditors converged on this. Compounding: `CHANGELOG.md`, `README.md`, `AI-USE.md` and the video script are all authored after the T−12h cutoff by fresh machine sessions and signed off by a human awake 30+ hours; and Q2's **C4** — *"THE DESCRIPTION IS THE FIRST THING A JUDGE READS"* — is a field no chunk writes at all.

**Fix, three parts.**
1. Amend `PROCESS.md` §0: *"No **evidence** artifact is written twice. Three prose artifacts are exceptions and are rewritten by hand before shipping: the README's first screen, the CHANGELOG's Decision/Learning column, and the video script — plus the HackerEarth Description."*
2. **Pull the authoring forward.** Today, while CH-01 runs, the operator hand-writes README §§ intended user / bottleneck / why valuable and the video's opening beats, from `CONTEXT.md` §2 — which is already hand-shaped prose. CH-11 then fills numbers around human writing instead of generating prose around numbers.
3. **New CH-11b · VOICE PASS**, 45–60 min, operator only, no session, scheduled **before CH-13B** so the script inherits the voice. Mechanical checklist: read aloud; delete every sentence that could appear in any other submission; no em-dash-per-sentence cadence; no *delve / leverage / robust / seamless / comprehensive*; no "It's not X, it's Y"; no three-item lists where two or four is truer. Add two or three sentences only the person who did this work could write — the 0.46-completeness bug that poisoned the pilot, the hour ecfr.gov started 403ing, the experiment that got killed. Sign it.
4. **Separate the machine records rather than rewriting them:** move `PROCESS.md`, `plan.md`, `CLAUDE.md`, `STATUS.md`, `PROGRESS.md`, `QUESTIONS.md` into `docs/process/`; leave `README.md`, `REPRODUCE.md`, `CHANGELOG.md`, `AI-USE.md`, `GOOD.md`, `PROVENANCE.md`, `LICENSE` at root. One authored README line: *"`docs/process/` holds the working records — the spec, the chunk plan, the session journal, the rulings. They are agent-authored and unedited on purpose; they are the audit trail, not the pitch."* That converts a liability into a disclosure asset.

### M3 · CH-08 and the CHECKPOINT — the two chunks producing every quotable number — are ungated · 1.2 h · 30 + 15 pts

> **"Gate what a silent bug would invalidate."** — PROCESS.md §6, its own principle

CH-02/03/04 get FULL adversarial gates. CH-08 (ablation matrix, McNemar, paired bootstrap clustered by FR document) carries **GATE: none**, and the CHECKPOINT that decides GREEN/AMBER/RED carries **Gate: —**. A clustered bootstrap is easy to get subtly wrong — resampling items instead of documents, one- versus two-sided, CI direction — and this number goes into the README, the results table and the video simultaneously.

**Fix — a third, cheap gate tier, not a full one.** Add **NUMBERS-ONLY review** (30–40 min, no reimplementation) to `PROCESS.md` §6: a fresh session receives only the committed per-item verdict CSVs and `CONTEXT.md` §7, independently recomputes accuracy, the McNemar statistic, the bootstrap CI and effect size, confirms the bootstrap resamples **documents not items** (with a probe that fails on item-level resampling), confirms each ablation arm differs from A1 in exactly one capability by diffing arm configs, then diffs against the reported figures. Apply to the CHECKPOINT **before the GREEN/AMBER/RED call is acted on** and to CH-08 before any number reaches the README.

### M4 · The API budget is short by roughly an order of magnitude · 0.25 h · gates all of Phase 2

Q1's ruling is good and correctly reasoned. Its number is not. The seed says *"~750 programmatic model calls (3 arms × 3 reps × ~84 items)"* and *"Budget USD 20-30."* That covers the CHECKPOINT only. CH-08 adds three ablation arms plus B0′ plus final arms × 3 reps: **7–8 arms × 3 reps × 84 items ≈ 1,800–2,000 additional multi-turn agentic runs**, each carrying point-in-time CFR section text. At Sonnet list prices with ~15–25 k input tokens per run that is **$120–400**, not $20–30. Discovered at hour 25, it kills CH-08.

**Fix.** Revise the estimate in Q1 to the full arm matrix. Put a stated USD ceiling in `GOOD.md` **with a pre-registered reduction** — *"if the ceiling is reached, ablation arms drop from 3 reps to 1; final arms keep 3"* — so the cut is a declared decision rather than a panic. Enable prompt caching on the shared corpus payload. Verify the model id in the logger's `PRICES` dict is one the funded account can actually call; a price basis naming an uncallable model silently corrupts every cost row.

### M5 · The instructions that shape each agent are not shipped as files · 1.0 h · 30 pts

> **"Share the full project and everything required to run it. Include the code as well as **the instructions that shape each agent**."** — §8 deliverable 01
> **"The instructions that shape each agent, included as files"** — §12 checklist

`CONTEXT.md` §4 defines five arms; no chunk commits any arm's prompt text to a file. They will live as string literals inside arm scripts, so the fairness claim (*"the same task, the same items, the same model"*) is unverifiable by reading, and a judge cannot diff B0-agent's instructions against A1's to see what the skill added. `prompts/` also has no row in `PROCESS.md` §3's Files table.

**Fix.** Create `agents/` with one file per arm — `B0.md`, `B0-agent.md`, `B0-prime.md`, `A1.md`, `A1-SKILL.md`, plus the `cfr_resolve` tool schema. Arm scripts **read these files** rather than embedding strings. `run_start.agent_instructions` records the file path **and its SHA-256** alongside the resolved text, so a judge can confirm the trajectory used the shipped instructions. Add `agents/` and `prompts/` (Ships: yes) to `PROCESS.md` §3. CH-00 creates the directory and loader; CHECKPOINT fills B0/B0-agent; CH-05–07 fill A1.

### M6 · Every number that justifies the design was computed outside the repo, and no chunk migrates it · 2.0 h · 30 + 5 pts

> **"Connect every claim about your results to the evidence you submit."** — §7 ground rule 09
> **"EVIDENCE OR IT DIDN'T HAPPEN."** — the project's own CLAUDE.md rule 14

Hard rule 14 binds build sessions. It does not bind the architect's own spec, and `CONTEXT.md` ships. Load-bearing and unevidenced: 0.545 / 0.5855 / 0.52 (§3); 26/33 and 35/42 with no extractable anchor, 31/82 and 833/1,984 order-sensitive (§6); n=16 hard cases (§9); 0/68, 3/82, 26/1,984 = 1.31% (§10); and the entire hot take — IETF errata +12.0 pp / −4.0 pp, p = 0.64, −16.7 pp on the policy class (§11). Their generating scripts sit in `killtest/` (confirmed: `errata_arms.py`, `errata_score.py`, `errata_build.py`, `errata/`), `probe/` and `replay/` — all correctly excluded from the repo by D1. §6's counts are the entire argument for why there are exactly three capabilities.

**Fix — new CH-01b (ungated, parallel with CH-01).**
- `docs/evidence/spec-claims/` — re-derive the four counts `CONTEXT.md` §6 depends on **from the frozen corpus, in-repo**, script committed, and update `CONTEXT.md` to the re-derived values with paths beside them.
- `docs/evidence/pilot/<claim-id>/` — for numbers that cannot be re-derived, copy the specific generating script + input hash + stdout, with a one-line README stating the date it ran, that it ran pre-repo, and which claim it supports. Anything neither re-derivable nor migratable gets **deleted from `CONTEXT.md`**, not shipped bare.
- `docs/evidence/hot-take/` — **Path B, not Path A.** `07-KILL-TEST.md` §6.1 already resolved IETF redistribution as CONDITIONAL on four conditions (verbatim-only text, per-record `doc-id` attribution under TLP §3.c.iii(x), a NOTICE file because six named RFCs exceed the one-fifth legend threshold, no BSD-relicensing). Do **not** vendor the corpus. Ship the aggregate numbers plus the generating script, with the corpus fetched by URL at replay time. Write that into CH-09's done-when so nobody vendors it by reflex.

**And a hard rule for the README (M6b, 0.5 h):** add to CH-11's done-when — *"every numeral in the README, CHANGELOG, GOOD.md and the video script resolves to a `docs/evidence/` path generated by this repo. Any retained pre-competition figure is prefixed `PILOT (pre-competition, n=NN)` and carries its own path."* Enforce with a script that extracts numerals and asserts each appears in a committed evidence file, committed as `docs/evidence/claims-audit.md` — it doubles as direct proof of ground-rule-09 compliance. Without this, `CONTEXT.md` §3's pilot figures (0.545 → +32 pp) will not match CH-08's numbers, and the discrepancy is visible without running anything.

### M7 · The human checkpoint is claimed everywhere and fires nowhere · 1.5 h · 30 pts + rules 04/05

> **"Capture the feedback that shaped its next step as well as any retries or human checkpoints."** — §8 deliverable 04
> **"Add human approval before the action happens." / "Make a qualified human reviewer part of any solution that could significantly affect someone."** — §7 ground rules 04, 05

`CONTEXT.md` §9 routes unresolved cases to *"a named human checkpoint"*; CH-10 has a queue; the logger has a `human_checkpoint` record type. But **"unresolved" is never defined**, the §5 output contract has no field for it, no chunk implements the routing, and ~750 automated runs mean every shipped trajectory contains zero such records. A build session reaching CH-06 and finding "unresolved" undefined **must STOP under hard rule 1** — burning architect time in the most expensive hours of the schedule.

**Fix.**
- **`CONTEXT.md` §5, two new fields:** `"needs_human_review": true|false`, `"review_reason": "..."`.
- **`CONTEXT.md` §9, a trigger rule not a word:** fires when (a) any instruction in the trace has `level: "none"` **and** `designation_exists: true`, or (b) the designation path and the anchor path disagree on the verdict, or (c) the ordered-state ledger reports a designation touched twice.
- **CH-06 done-when:** at least one eval item routes to the queue and its trajectory contains a `human_checkpoint` record.
- **CH-08:** run **two** hard-case items interactively — the agent emits the checkpoint with both readings and the paragraph trace, the human calls it, the run resumes, the resolution is recorded. **CH-12** designates those two as the checkpoint representatives and links them from the README's ground-rules section. One becomes the on-screen moment in the video's realistic-execution beat. Almost no entry will ship a trajectory where a human actually intervened.
- **Measure it while you are there** (this is the cheap half of the "verification capability" question — see §4): report the queue's **catch rate** (fraction of A1's wrong verdicts routed rather than shipped confident) and its **interruption cost** (correct verdicts also stopped). If it does not pay, it becomes removed experiment #3 with its number.

### M8 · Raw JSONL is not "easy to follow", and there is no stated selection rule · 1.0 h · 30 pts + trace gate

> **"Make each trajectory easy to follow from the agent instructions to the final result."** — §8 deliverable 04

CH-12's card says *"packaged with labelled human-intervention points"* and specifies no rendering. A judge who opens a 2 MB JSONL, scrolls and closes it has not seen the best evidence in the project. `PROCESS.md` §0's claim that *"the trajectory logs ARE deliverable 4"* is wrong — they are the raw material for it.

**Fix.** `tools/render_trajectory.py` → one markdown page per representative run: agent instructions (collapsed), a numbered step table (action / tool response, long outputs truncated with the full value linked into the JSONL), feedback and retries inline, the final emitted JSON, the gold label, and whether it matched. Build it at CH-00 alongside the logger for ~20 extra minutes. Pair with the C2 selection rule from D3.

### M9 · There is no way for the intended user to run this on their own rule · 2.0–2.5 h · 20 pts · **cut candidate**

> **"A strong solution completes a realistic and self contained execution and produces a final result the user can use."** — §6 End to End Quality
> **"…then walk through one realistic execution from start to finish."** — §8 deliverable 03

`CONTEXT.md` §2 names the user as *"a regulations drafter clearing a final rule for publication"* — someone holding a draft that is **not yet published and therefore in no corpus**. Every arm runs over the frozen labelled historical set. CH-10 renders a worksheet from evaluation outputs. There is no entry point from "here is the rule I am clearing" to "here is its worksheet". A benchmark harness with an HTML report is a research result, not a tool, and the video's central beat has no artifact behind it.

**Fix.** Declare the CLI in `CONTEXT.md` §5 **before CH-05 builds the tool**, then add to CH-10: `python -m src.clear --amdpar <file|FR-doc-number> --title N --part N --as-of YYYY-MM-DD` → `out/<doc>/worksheet.html`, using frozen CFR text when the as-of date is in the corpus. Run it once on a 2025/2026 final rule **not in the eval set and with no NARA note yet**, commit as `docs/demo/`, label it clearly as a demonstration so it never contaminates the results table, and make it the execution the video walks through. This is the honest use case — pre-publication, no ground truth.

**Flag:** this is the largest single new cost in the audit and the first thing to cut if Phase 1 overruns. See §6.

### M10 · Reproducibility: same-machine rehearsal, no pinned environment, no tolerance · 1.5 h · 15 pts (tie-break #2)

> **"Could they do it from a clean environment?"** — §6 Reproducibility
> **"Share the relevant versions along with the approximate runtime and cost."** — §8 deliverable 02

Three separate holes. (a) CH-14's "second path" is a second directory on the same Windows 11 machine with the same Python, same PATH, same cached wheels, same author — it cannot see a backslash path literal, a `python` vs `python3` shebang, or a case-sensitive filename mismatch, and the judge is almost certainly on Linux. (b) *"Versions pinned"* is a clause, not a file: no `requirements.txt`, no interpreter pin. (c) The load-bearing version is the **model snapshot id**, and nothing requires stating it, the sampling parameters, or a **tolerance** — a judge who reruns Tier 2 and gets 0.81 against a claimed 0.85 records a failed reproduction.

**Fix.** CH-11 produces `requirements.txt` with exact pins (or asserts stdlib-only), the exact Python version, and one copy-pasteable command **per arm**, each labelled with which of the PDF's four sanctioned baseline types it is (B-script = type 3, B0 = type 1, B0-agent = type 2), with an EXPECTED block under each carrying the accuracy that command prints and the SHA-256 of its output file; Tier-1 replay asserts those hashes and exits non-zero on mismatch. State the model snapshot id per arm, temperature/top-p, that model calls are non-deterministic, and publish the spread the three reps already give you for free (*"A1 across 3 reps: 0.84 / 0.86 / 0.85; expect ±2 pp"*). CH-14a runs the Tier-1 replay once inside **WSL or `python:3.12-slim`** from a fresh `git clone` of the public HTTPS URL, network off.

### M11 · Ground rule 03 is cleared for the corpus and nothing else, and the repo ships a self-reported service-terms breach · 1.0 h

> **"Use every tool and component according to its license and service terms."** — §7 ground rule 03

`CONTEXT.md` §8's govinfo/17 U.S.C. §105 analysis is genuinely thorough — and it is the only clearance in the project. Uncleared: the Python dependency set, anything CH-10 vendors into the offline HTML, and the model provider's terms. Worse, `CONTEXT.md` §8 and `CLAUDE.md` both ship the sentence *"Sustained automated traffic got us blocked"* — a voluntary confession of a service-terms incident against two .gov domains, with no remediation beside it, in the submission whose entire pitch is integrity.

**Fix.** (1) Rewrite the §8 constraint note factually and without the admission of fault — both hosts return 403 to this environment, neither is used, govinfo bulk data is the sole channel — then add the compliance half: govinfo's robots.txt checked and permits bulkdata; `refetch.py` sends a descriptive User-Agent with a contact address, sleeps N seconds between requests, backs off, honours 429/503; the two blocked hosts were **abandoned rather than circumvented** (quote CLAUDE.md's own rule as the mitigation); no authentication, paywall or click-through bypassed; **Tier 1 needs no network at all so a judge is never exposed to it.** Handled this way the incident becomes evidence of discipline. (2) Add `THIRD-PARTY.md` in CH-11: every dependency and data source with licence and link, including the model provider and the basis on which its outputs may be assigned. (3) Constrain CH-10: **no external fonts, CSS or JS — inline hand-written styles only.** (4) Add a `LICENSE` file; there is none.

### M12 · Rule 05's strongest available answer is sitting unused, and the builder's non-expertise is undisclosed · 0.7 h

> **"Make a qualified human reviewer part of any solution that could significantly affect someone."** — §7 ground rule 05

Nothing names a qualified reviewer. CH-09's blind study is a human doing the task for *timing*, not reviewing outputs. The pre-registered guards permit a false-defect rate of 0.25 and a missed-defect rate of 0.25 — one wrong call in four, in a domain where a wrong `WILL_EXECUTE` means a federal rule silently fails to codify. A judge reads that budget, looks for the reviewer, and finds one sentence.

**Fix — `SAFETY.md`, ~250 words, linked from the README's first screen**, making four points the design already supports and never states: (1) the system performs no action — CLAUDE.md rule 8 makes scorer and resolver pure, the output is a worksheet, never a filing; (2) **every gold label in the eval set was authored by Office of the Federal Register editors — the ground truth *is* a qualified human reviewer's judgement.** This is the sharpest rule-05 answer available and nobody is making it; (3) the checkpoint queue routes ambiguous items to a named drafter before use, with the trigger rule from M7; (4) plainly: *"I am not a regulations drafter. This tool is validated against OFR-authored ground truth, not against my own legal judgement, and a qualified drafter reviews every output before it informs a filing."*

### M13 · "Close with the main failure mode" has a README slot and no producer · 1.5 h · 20 + 5 pts

> **"Close with the main failure mode and your hot take."** — §8 deliverable 01

CH-08 emits a results matrix; CH-09 produces the removed experiments and the hot take. Nothing classifies A1's actual errors into a taxonomy, counts them, or names the dominant one. The §11 hot take is about retrieval per-class recall on an earlier IETF corpus — it is **not this system's failure mode**, and the PDF asks for both as separate closing items.

**Fix.** CH-08 done-when: emit `docs/evidence/error-taxonomy.csv` — every A1 error with `(item_id, gold, predicted, failure_class, which resolution_trace step went wrong)`. CH-09 names the largest class with its count and a worked example. That becomes the README's "main failure mode" section and two sentences of a video beat.

### M14 · Human time per task is measured for one arm of a two-arm row · 1.0 h · 15 pts

> **"| Human time per task | [value] | [value] | [change] |"** — §5, the suggested results table
> **"Report human time per task and cost per task"** — §10 item 10, listed as new material

CH-09 stopwatches 8 items by hand. Nothing measures the drafter's time reviewing the worksheet, which is not zero because the design routes cases to a checkpoint. The table ships with a blank cell or an unsupported "~0" — the tell of a comparison that was not thought through. **And the study cannot be blind where it is scheduled:** by CH-09 the operator has hand-verified three golden rules, built the eval set, written the scorer and seen every checkpoint result. Calling it *"before seeing gold"* at that point is not true, and it is checkable from git timestamps.

**Fix.** Move the by-hand pass to **CH-01b**, immediately after the harvest: reserve 8 `(rule, section)` ids from the defect-note pool, exclude them from the golden-fixture set, work them by hand with a stopwatch, commit the per-item log with UTC timestamps to `docs/evidence/human-time/` so the ordering is provable. Then in Phase 3, after CH-10 exists, run the **same 8 items** from the worksheet, clearing only the routed checkpoints. Publish both with the caveat verbatim beside the number, not in a footnote: the timer is the author, n=8, second pass benefits from familiarity, treat the delta as an upper bound. A caveated real number beats an uncaveated unbelievable one.

### M15 · Public access is never verified from outside your own session · 0.5 h · gate

> **"Give judges enough access to run the project and reproduce the main result."** — §7 ground rule 10

CH-00 creates the repo **private, no description, no topics**. CH-14 says *"Repo made public at submission."* Both `gh repo view` and any browser carrying your GitHub session succeed on a private repo, so the natural check gives a false pass while every judge gets a 404. Folded into D3's CH-15 checklist; screenshots go to `docs/evidence/access/`.

### M16 · The architect is a single point of failure whose state lives in chat · 0.5 h

`PROCESS.md` §3 declares *"Chat history is not a record"* while `PROCESS.md` §1 explains that the architect must be this session because *"re-bootstrapping costs hours we don't have."* Both cannot be true. A compaction or crash at hour 18 costs 2–4 hours that do not exist.

**Fix.** Add `ARCHITECT.md` to CH-00's skeleton list and one duty to `PROCESS.md` §2: after every chunk, append a dated 12-line state block — current chunk and verdict, next chunk, every number verified so far with its evidence path, open rulings, and the read-order a replacement architect needs. Keep the **next two chunk prompts pre-written** in `prompts/` at all times, so a dead architect costs zero chunks rather than two. (This also feeds the sleep block in D5.)

### M17 · The dependency chain is serial where it need not be · 1.0 h saved

`CONTEXT.md` §2 already contains finished, hand-shaped prose for user / bottleneck / value — 15 points of Problem & User Value that could be written today and instead gets written at hour 30. The worksheet's HTML shell can be built against a synthetic fixture at any time. `AI-USE.md` accrues continuously and is deferred to CH-12. The govinfo bulk downloads are I/O-bound and could stream from CH-00 onward. The operator is idle during every long build.

**Fix.** Start the govinfo fetches as a background job during CH-00. During CH-01/CH-02 build sessions the operator hand-drafts README §§ user/bottleneck/value and video beats 1–2 (this is also M2's fix). Build the worksheet HTML shell against a hand-written fixture during Phase 1. Append to `AI-USE.md` every session. **Run parallel-track prose work on a `docs` branch or a `git worktree`** and name the rule in `PROCESS.md` §2 — two uncoordinated sessions on one working tree is its own failure mode.

---

## 3. MINOR / POLISH

- **CH-11's README order is missing four things `CONTEXT.md` mandates:** §1 non-goals ("state these in the README"), §2 the generalisation ("lead the README with this"), §12 prior art ("cite on the first screen" — Prior et al. NLLP@ACL 2025, `cfpb/regulations-parser`, ATLAS), and the PROVENANCE link. Name them in the card or the build session will ship without them. **0.5 h.**
- **The PDF's own three-row results table** (Primary outcome / Human time per task / Cost per task × Simple baseline / Agent solution / Change) is produced by no chunk. Put it in the README immediately after the headline claim, with the full arm matrix beneath it, and on a single video frame. Free points. **0.25 h.**
- **B0′ appears exactly once in the whole project** — in `CONTEXT.md` §4 — and in no chunk card. Name it in CH-08's scope, plus the promised per-arm token table (input/output tokens, tool calls, imputed USD, per item) sourced from the cost ledger. Dropping it silently invites "your agent got 5× the compute"; if the clock forces it out, drop it by recorded ruling. **0.5 h.**
- **"Include one challenging case and explain what it revealed"** is unowned between CH-08 and CH-09. Add `docs/evidence/hard-case/` for 12 CFR 702.504→702.304: each arm's full `resolution_trace` side by side, which arms got it right, and what the failure taught — that partial-read agents rule correctly for the wrong reason. Make it the case the video walks through. **0.5 h.**
- **Rejected-capabilities table** in the README, four rows with reasons and where possible numbers: orchestration (rejected — single-document read, no sub-goals), context/RAG over current CFR text (rejected **and measured** — removed experiment #1, leaks the label), verification (see §4), plus anything an ablation removed. Restraint only scores when it is visible. **0.5 h.**
- **The hot take never answers the row's second half** — *"how would it change what you build next?"* Two authored first-person sentences at the end. **0.25 h.**
- **The worksheet carries no disclaimer on its own face.** Header band: *"Draft review aid — predicted OFR execution outcomes. Not legal advice and not a filing. Every row requires sign-off by a qualified regulations drafter."* Footer: run id, model, corpus manifest hash, as-of date, count of rows in the review queue. The README is two clicks away; the worksheet is what gets forwarded. **0.25 h.**
- **The secret scan names no tool and no pass criterion.** Add `gitleaks detect` over full history plus an explicit regex sweep of `docs/trajectories/*.jsonl` for `sk-ant`, `AIza`, `Bearer `, and the key's own first eight characters — the logger writes `agent_instructions` and raw `tool_response.output` into committed files, so it creates the risk the scan must cover. Make the logger whitelist the fields it writes rather than dumping raw output. Commit the tool version and clean output under `docs/evidence/`. **0.5 h.**
- **The user is asserted, never evidenced.** Cite OFR's own Document Drafting Handbook §2 on amendatory instructions (it names the role and is the procedure the agent implements), convert CH-01's defect pool into a **rate** (defect notes per year across harvested titles, each meaning a correcting document in a later FR issue), and quote one real NARA note verbatim on the first screen. The government's own words read as authored because they are. **0.75 h.**
- **Removed experiments and B0′ get no changelog rows.** `PROCESS.md` §5's card mechanism covers CH-05–07 only. Extend it to controls and removals; add three rows to the table. **0.5 h.**
- **Originality re-check was run against the dead idea.** `03-IDEA-REVIEW-VERDICT.md` found the previous candidate's hot take already published publicly under your own name. The project changed completely; nobody re-ran the check. Thirty minutes searching the exact hot-take sentence, "amendatory instruction" + agent, and your own GitHub/blog/LinkedIn. Whatever surfaces goes into `PROVENANCE.md` as a dated citation. **0.5 h.**
- **FR XML carries `FOR FURTHER INFORMATION CONTACT` blocks** naming agency staff with direct phone and email. Lawful (17 U.S.C. §105, published record) but unacknowledged. Two sentences in `data/README.md`: published under §105, contains agency contact details as published, no data inferred/enriched/joined or republished outside its original document context, no individual is a subject of analysis. **0.15 h.**
- **`BUILD-PHASE-1-PROMPT.md` at repo root is a superseded plan** that contradicts `plan.md` (one Phase-1 session vs five gated chunks). Gitignore it or move it to `docs/process/`. A build session reading root markdown will find it. **0.05 h.**

---

## 4. Duplicates and disagreements

**Convergence — treat these as confirmed, not opinions.**

| Finding | Auditors | Read |
|---|---|---|
| No chunk performs the submission | **5 / 5** | The strongest signal in the whole audit. D3. |
| No archive produced | **5 / 5** | Now sharpened by Q2: it is the ≤ 50 MB Source Code ZIP. |
| Anti-slop fix is blocked by `PROCESS.md` §0, not merely absent | **4 / 5** | Independent discovery of the same structural veto. M2. |
| `.gitignore` / first-commit contents | **3 / 5** (licence half by a 4th) | Every dimension independently verified on disk. D1. |
| Build-agent trajectories missing and volatile | **3 / 5** | JSONLs confirmed present and being written now. D4. |
| No `PROVENANCE.md` for ground rule 02 | **3 / 5** gave concrete fixes | Known item; all three fixes agree. D2. |
| Repo-public flip unverified from logged-out | **3 / 5** | M15. |
| Clean-environment rehearsal is same-machine | **3 / 5** | M10. |
| Hot-take evidence lives outside the repo | **3 / 5** | M6. |
| Registration unverified | **3 / 5** | Downgraded — see below. |
| Video upload timing / host / logged-out playback | **3 / 5** | D6. |
| CH-08 ungated | 2 / 5 | M3. |
| Claims/numeral audit before shipping | 2 / 5 | M6b. |
| Human checkpoint never fires | 2 / 5 | M7. |
| Agent-arm human time missing | 2 / 5 | M14. |
| 403 disclosure needs its compliance half | 2 / 5 | M11. |

**Disagreements, resolved.**

1. **Does `context/01-PROBLEM-PDF.md` ship?** Auditor 3 says yes ("your own notes"); Auditor 2 says no ("a full verbatim ten-page extraction"). **Auditor 2 is right.** The file's own header states *"every page in this PDF is a text page… All text below is verbatim."* That is a reproduction of micro1's unreleased brief, not a note. Auditor 2 also caught the consequence Auditor 3 missed: `CLAUDE.md`'s Precedence chain names it as a live repo file, so excluding it requires a one-line CLAUDE.md amendment. Ship `00-MASTER-CONTEXT.md` (genuinely your own synthesis) and keep `01-PROBLEM-PDF.md` local.

2. **Add Verification as a fourth capability?** Auditor 4 argues for it (2 h) on the grounds that it is named verbatim in the 30-point row's text and second in the PDF's leaked changelog order. Nobody else raises it. **Reject the capability; take the cheap half.** `CONTEXT.md` §6 caps at three with the PDF's own anti-kitchen-sink line as the reason, and that restraint is itself a scoring asset the plan should keep. But the human-checkpoint router is already being built for CH-10 and M7 already requires it to fire — so **name it as a verification surface in the README and measure its catch rate and interruption cost**. If it does not pay it becomes removed experiment #3 with its number, which is worth nearly as much. Do not add a fifth of anything.

3. **`git archive` as the archive fix.** Auditors 1, 2 and 4 all propose `git archive --format=zip HEAD`. All three are right about the mechanism and all three assumed a small repo. **It only works after D1 lands**, and it only stays under Q2's 50 MB cap if CH-03 honours C1 (extract-then-freeze the specific CFR sections and FR blocks, never whole title XMLs — nine titles measured 407 MB). Sequence the fixes: D1 → CH-03 scope line → CH-15 archive.

4. **When does the human-time study run?** Auditor 5 says move it before CH-02 to make "blind" true; Auditor 4 says run it on both arms. **Both are right and they compose**, but Auditor 5's placement needs one correction: CH-03 does not exist yet, so sample the 8 items from **CH-01's defect-note pool by id**, reserve them, exclude them from goldens. The second (worksheet) pass necessarily happens in Phase 3 after CH-10. M14 merges them.

5. **Where does the voice pass go?** Auditor 2 says T−4h, Auditor 3 says between the two submissions, Auditor 4 says before the video, Auditor 5 says inside CH-15. **Auditor 4 is right** — it must precede the video so the script inherits the voice, and burying it inside CH-15 puts prose editing in the same hour as an upload deadline. CH-11b, after CH-11, before CH-13B.

6. **Auditor 5's Phase-1 re-estimate versus everyone else's new chunks.** Nobody else priced the schedule, and Auditor 5 did not price the additions. Together they are in direct conflict: the audits collectively add ~10 h of work to a phase that is already ~11 h over budget. **Auditor 5's finding governs.** §6 resolves it by ruthless triage rather than by pretending both fit.

---

## 5. FALSE ALARMS

Honest corrections. These were raised and the plan — or the current file state — already covers them.

- **"The submission form is entirely unknown; the Details tab was never re-scraped."** *(Auditor 3, its central claim, 0.5 h fix.)* **Superseded.** `prompts/CH-00.md` now seeds **Q2 ANSWERED** with the form read from inside it: four fields, Video URL is a link, Source Code is an uploaded ZIP capped at 50 MB, "Save as Draft" exists. The auditor read an earlier revision. What survives is narrower and is captured in D3: those rulings live only in a prompt seed and no chunk executes them.
- **"Q1 model access is OPEN with no owner and no deadline."** *(Auditors 3 and 5.)* **Superseded.** Q1 is ANSWERED with a recorded, well-reasoned ruling — paid Anthropic API, `claude-sonnet-5`, **the same model for every arm** for fairness, with the explicit and correct reasoning that a stronger model produces a stronger baseline and therefore a smaller measured gap. What survives is only the budget figure (M4).
- **"Registration may never have completed."** *(Auditors 2, 3, 5 — all rated disqualifying.)* **Downgraded.** Q2's field list cannot be read from outside the form. Strong circumstantial evidence registration is live. Still worth the five-minute screenshot (D7), but not the emergency all three described.
- **"Nothing says to submit early."** *(Auditor 3.)* **Half-covered.** Q2's C5 states the policy verbatim: *"'Save as Draft' exists. A complete-but-imperfect draft is saved as soon as one exists, then updated."* The policy exists; the execution has no owner. That half is D3.
- **"Cost per task is not instrumented."** Not raised as a gap by anyone, and correctly so — CH-00's cost ledger with input tokens, output tokens, wall-clock, imputed USD at published list prices, a recorded price basis with source URL, and an explicit rule never to emit `$0` for flat-cost work, is genuinely ahead of the field. `PROCESS.md` correctly identifies it as retrofit-hostile.
- **"Ground rule 04's sandbox half is unimplemented."** *(Auditor 2 raised it, then conceded it.)* The sandbox half is satisfied **structurally**: CLAUDE.md rule 8 makes scorer and resolver pure — no network, no clock, no randomness — the output is a JSON document and a static HTML page, and nothing writes to any external system. The system cannot take a consequential action. Only the *routing* half is missing (M7), and only the *saying so* is missing (M12).
- **"No statement of which capabilities were deliberately not used."** *(Auditor 4.)* Partly covered already: `CONTEXT.md` §6 caps at three quoting the PDF verbatim and requiring an architect ruling for a fourth, and §10 documents two pre-planned removals with pre-registered predictions. What is missing is only that it reaches the README — listed in §3 as polish, not as a design gap.
- **"Deliverable 4's record schema is incomplete."** It is not. `run_start` (carrying `agent_instructions` verbatim) → `action` → `tool_response` → `feedback` (field literally named `what_changed_the_next_step`) → `retry` → `human_checkpoint` → `run_end` is a line-by-line match to the requirement. The gaps are coverage (D4), rendering (M8) and firing (M7) — not schema.
- **"Prior art is not handled."** `CONTEXT.md` §12 names all three, states the differentiating axis for each, and articulates why it matters. The gap is only that CH-11's card does not carry it into the README order.
- **Genuinely strong and not to be touched:** the two-tier repro design (Tier 1 replays offline in < 90 s at $0 with no API key — the correct read of a judge with limited time); `.gitattributes = * -text` as literally the first file in the first commit; `GOOD.md` pre-registered and timestamped before any model arm runs with hard rule 5 forbidding movement; exact instruction-count-matched negatives asserted by a test under a FULL gate; the B-script arm reported with its permutation null; the T−12h cutoff and its stated rationale; the iteration card committing a numeric prediction before each build; the corpus licence analysis including the incorporation-by-reference check; hard rule 14; and the honesty regime in §9. Roughly 60 points of method are already well defended. Everything in this audit is about not losing them at the gate.

---

## 6. THE REVISED CHUNK LIST

Now: **2026-08-30 ~04:00 UTC. 38.0 hours remain.** Solo. Assume 4.5 h sleep. Effective working time ≈ 33 h, of which Phase 3 is protected from **06:00 UTC Aug 31** (T−12h).

### Stage 0 — ARCHITECT PRE-FLIGHT · 2.5 h · **no session, do it now, before CH-00**

| # | Action | File | h |
|---|---|---|---|
| P1 | `.gitignore` allowlist + ship/no-ship ledger + `git ls-files` done-when + 25 MB file assertion | `prompts/CH-00.md` §1, `PROCESS.md` §3 | 0.5 |
| P2 | Write `PROVENANCE.md`; add commit-splitting instruction (A `.gitattributes` → B `PROVENANCE.md` → C pre-existing import → D+ build) | new file + `prompts/CH-00.md` | 0.75 |
| P3 | Write the **four-column changelog table** into `PROCESS.md` §5 (removes the CH-00 contradiction); extend the card mechanism to removals and controls | `PROCESS.md` §5 | 0.25 |
| P4 | AMBER branch · RED path · CH-02 and CH-03 numeric fallbacks · two-strike rule · tiered review (MANDATORY core / IF-TIME) · MVS drop list · T-schedule with alarms · sleep block | `PROCESS.md` §6–7, `plan.md` | 1.0 |
| P5 | Session-transcript end-of-session duty; `docs/trajectories/build/`; `ARCHITECT.md`; `agents/` + loader; `prompts/` row in Files table | `CLAUDE.md`, `prompts/CH-00.md` | 0.25 |
| P6 | `CONTEXT.md` edits: §5 `needs_human_review` + `review_reason`; §9 trigger rule; §8 403 rewrite + rate-limit/UA policy; §5 CLI signature; Q1 budget correction with pre-registered rep reduction | `CONTEXT.md`, `QUESTIONS.md` | 0.5 |
| P7 | Registration screenshot → Q0 CLOSED; set alarms 23:45 UTC / 06:00 / 12:00 / 16:00 | `QUESTIONS.md` | 0.25 |

*(P1–P7 overlap in editing passes; budget 2.5 h, not 3.5.)*

### Phase 1 — foundation and go/no-go · **re-estimated 15.5 h** (was "~5 h")

| Chunk | Change | Gate | h |
|---|---|---|---|
| **CH-00** | + `docs/trajectories/build/`, `agents/` + loader, `ARCHITECT.md`, `render_trajectory.py`, logger field-whitelisting, `gitleaks` + pre-commit hook, **corrected `.gitignore` and split commits**; start govinfo bulk fetch in background | — | 1.5 |
| **CH-01** | unchanged; **+ done-when: convert the defect pool to a rate** (notes/year across harvested titles) | — | 2.0 |
| **CH-01b** *(new)* | 8 reserved items worked **by hand, stopwatched, logged with UTC timestamps** → `docs/evidence/human-time/`; migrate spec-claim evidence → `docs/evidence/spec-claims/` + `pilot/`; hot-take Path B → `docs/evidence/hot-take/` | — | 1.5 |
| **CH-02** | unchanged scope; **fallback pre-registered**; tiered review | FULL-core | 2.0 + 1.25 |
| **CH-03** | + **C1: extract-then-freeze only the sections/blocks the eval set uses** — never whole title XMLs; + `data/README.md` with the §105 and contact-data paragraphs; fallback pre-registered | FULL-core | 2.5 + 1.25 |
| **CH-04** | unchanged; + USD ceiling and rep-reduction rule into `GOOD.md` | FULL-core | 1.5 + 1.25 |
| **★ CHECKPOINT** | + **NUMBERS-ONLY review before the call is acted on**; + write **both** video scripts (GREEN and AMBER-RED) | NUMBERS | 1.5 + 0.5 + 1.0 |

**Parallel, operator, during long jobs (M17):** hand-draft README §§ user/bottleneck/value and video beats 1–2 on a `docs` branch; build the worksheet HTML shell against a synthetic fixture; append to `AI-USE.md` each session. **CH-13A recordable and uploadable as soon as CH-04 lands.**

### Phase 2 — the agent · **GREEN or AMBER** · budget: whatever remains to 06:00 UTC

| Chunk | Change | Gate | h |
|---|---|---|---|
| **CH-05** | unchanged | code-only | 2.0 |
| **CH-06** | + done-when: **one eval item routes to the checkpoint queue and its trajectory contains a `human_checkpoint` record** | CODE-ONLY | 2.5 |
| **CH-07** | unchanged — **first capability cut if the clock demands** (see below) | code-only | 2.0 |
| **CH-08** | + **name B0′ explicitly in the arm list**; + per-arm token table from the cost ledger; + `docs/evidence/error-taxonomy.csv`; + `docs/evidence/hard-case/`; + two interactive human-checkpoint runs; + checkpoint catch-rate / interruption-cost | **NUMBERS** | 3.0 + 0.5 |
| **CH-09** | + second human-time pass deferred to Phase 3; + hot-take Path B done-when; + the two "what I'd build next" sentences | — | 1.5 |

### Phase 3 — packaging · protected · begins 06:00 UTC Aug 31 · **reordered**

| Order | Chunk | h |
|---|---|---|
| 1 | **CH-14a · early rehearsal** — fresh `venv` from pinned `requirements.txt`, network off, manifest verify, Tier-1 replay, **run once under WSL / `python:3.12-slim`**, following the written guide line by line | 1.25 |
| 2 | **CH-12 · trajectories** — build-session JSONLs + pre-build swarm JSONs + rendered markdown pages + `docs/trajectories/README.md` with the **written selection rule** + `AI-USE.md` | 1.5 |
| 3 | **CH-11 · README + repro guide** — full section list (generalisation → user → bottleneck → value → prior art → non-goals → results table (PDF's 3-row form) → changelog table → main failure mode → hot take → PROVENANCE → SAFETY → AI use → licence); per-arm commands with EXPECTED blocks and hashes; model snapshot ids and tolerance; `THIRD-PARTY.md`; `LICENSE`; `SAFETY.md`; **claims-audit script** | 2.5 |
| 4 | **CH-11b · VOICE PASS** *(new)* — operator only, no session, 45–60 min, four surfaces + the HackerEarth Description | 1.0 |
| 5 | **CH-10 · worksheet** — + disclaimer band and provenance footer; + no external fonts/CSS/JS; + second human-time pass (20 min); + one-session usability read | 2.0 |
| 6 | **CH-13B · video** — record to the chosen script, splice with 13A, re-upload, verify logged-out, under 5:00 | 1.5 |
| 7 | **CH-14b · final rehearsal** — repeat from the finished repo; `gitleaks` over full history; `docs/evidence/access/` screenshots | 0.75 |
| 8 | **DRAFT-1 · 12:00 UTC** — all four fields saved as draft | 0.5 |
| 9 | **CH-15 · SUBMIT · 16:00 UTC** — build zip, assert < 50 MB, extract-and-replay, flip public, verify logged-out ×3, submit, screenshot. **17:00 last touch. Nothing after 17:30.** | 1.0 |

### What does not fit, and what to cut

Pre-flight 2.5 + Phase 1 15.5 = **18 h**, ending ~22:00 UTC Aug 30. Sleep 4.5 h → 02:30 UTC Aug 31. Phase 3 opens at 06:00 UTC. **Phase 2 gets ~3.5 hours.** Phase 2 as revised needs 11.5.

That is the real finding, and the architect must choose now rather than at hour 20. In cut order:

1. **M9 (the user-facing CLI, 2.0–2.5 h) is cut first.** It is the largest new cost and the weakest per-hour return under time pressure. Substitute the cheap version: run the existing pipeline once on a rule not in the eval set, commit the worksheet as `docs/demo/`, and call it a demonstration. **Saves 2 h; keeps the video's beat.**
2. **CH-07 (memory / ordered-state ledger) is the first capability cut.** Ship two capabilities plus **three** removed experiments (leakage probe, collision detector, ordered-state-ledger-not-built-with-its-measured-class-size). The PDF demands removed experiments and most entries will have none; two kept capabilities each traced to a numbered failure plus three counted removals is a *better* changelog than three kept capabilities and a rushed CH-08. **Saves 2 h.** Record the cut as a dated architect ruling with its reason, never as an omission.
3. **Ablation reps drop from 3 to 1**, final arms keep 3. **Saves ~1 h and most of the API budget.**
4. **Merge CH-01 and CH-01b into one session.** **Saves 0.5 h of round-trip.**
5. **If still short: CH-02's gate drops from FULL-core to CODE-ONLY plus a three-fixture domain spot-check.** Do this only last — CH-02 is the component that already produced 0.46 once.

Do **not** cut: any Phase-3 item, the NUMBERS-ONLY gates, the voice pass, the early video upload, or the 12:00 UTC draft. Those are the difference between a scored submission and an unscored one.

---

## 7. The single most likely way this fails

Phase 1 is budgeted at five hours and, with three from-scratch reimplementation reviews on its critical path, is really fifteen-plus. CH-02 — the plan's own named highest-risk component, the one that already produced 0.46 completeness and poisoned a pilot — lands at 0.87 against a hard, correctly-immovable `≥ 0.90` with no pre-registered fallback, or it FAILs its adversarial review. The operator enters a fix→re-review loop that `PROCESS.md` §2 never bounds, each round costing two to three hours of architect-write, build-session, review-session round-trips. Somewhere in there he sleeps, unplanned, because no sleep was scheduled. He wakes past 06:00 UTC with no agent, no numbers, no packaging, and faces the one rule the process declared non-negotiable — and breaks it, because there is no minimum-viable-submission list telling him what to preserve. The video is then recorded unscripted at hour 68 and uploaded at 17:40 into a processing queue that "can take hours"; the repo is still private because the flip was a seven-word clause inside a chunk that never ran; the 50 MB zip was never built because no chunk owned it; and roughly sixty points of genuinely excellent method — pre-registration, exact count-matching, permutation nulls, offline replay, iteration cards with predictions committed before the run — are never read, because *"a project that cannot be run or verified may be disqualified before rubric scoring."*

**Mitigation, and every piece of it costs under an hour today.** Spend the next 2.5 hours on Stage 0 before a single build session starts: the `.gitignore` allowlist, `PROVENANCE.md`, the changelog table that removes the hour-zero contradiction, and — most importantly — the four exits the process is missing (two-strike rule, AMBER branch, RED path, numeric fallbacks for CH-02 and CH-03), plus the MVS drop list and a written T-schedule with four alarms. Then make the two cuts now rather than at hour 20: drop the user-facing CLI to a committed demo, and pre-declare CH-07 as the first capability to go. Record CH-13A and upload it as an unlisted placeholder the moment CH-04 lands, so the processing clock starts twenty hours early. Save the HackerEarth draft at 12:00 UTC on the 31st with whatever exists. From that moment the project is insured: the rules permit unlimited revision, only the latest complete submission is evaluated, and every remaining hour improves a submission that already exists rather than racing one that does not.