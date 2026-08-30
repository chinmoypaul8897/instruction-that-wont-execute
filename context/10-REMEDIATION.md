# Remediation Plan

**Produced:** 2026-08-30, 04:26–06:00 UTC · **Deadline:** 2026-08-31 18:00 UTC (T−36.8 h at the start of this pass)
**Input:** the 94 findings in `context/09b-audit-raw.json`, the consolidated narrative in `context/09-COMPLIANCE-AUDIT.md`, and the artifacts as they stand.
**Method:** every finding was given to an independent verification agent with read-only tool access and instructed to check it by running commands, not by reasoning about it. 89 of 94 returned a verdict on the first pass; the remaining 5 were re-run. Every verdict was then attacked by a second agent pointed in the *riskier* direction — told to defend the finding when the verifier wanted to dismiss it, and to demolish it when the verifier wanted to keep it. In parallel, eight agents read the official brief and the master context end to end looking for requirements nobody had audited; two critics then went over their output, one hunting for what the eight had missed and one killing padded claims — it killed nine of thirty-seven, which is why §7 is shorter than it could have been. The orchestrator ran its own independent pass over the same artifacts throughout, and every item in §2 was verified by the orchestrator personally with the commands shown, not delegated.

**Rules of evidence used throughout.** Every claim below is marked **VERIFIED** (a command was run or a file was read — the path, line, count or output is given), **INFERRED** (reasoned from verified facts, which are named), or **UNKNOWN** (could not be checked — §9 lists all of these). No claim is presented as fact without one of these labels.

**Scope.** This document proposes; it changes nothing. No file outside this one was written, no repository was initialised, no commit was made.

---

## 1. Verification summary

### 1.1 Where the 94 findings landed

**Coverage: 94 of 94 verified. 89 of those adversarially challenged** (the five whose first agent died to a connection error were re-run and reached the document too late for a challenge — noted in §9).

| Outcome | Count | Share |
|---|---|---|
| **CONFIRMED** — the gap is real in the files as they stand | **64** | 68% |
| **DUPLICATE-OF** another finding | **20** | 21% |
| **ALREADY-FIXED** — an architect fix closed it outright | **8** | 9% |
| **FALSE-ALARM** — the finding is wrong on its facts | **2** | 2% |

**Proposed hours: 74.9. Hours that survived on these 64: 34.6.** Roughly half the proposed effort was duplicated or aimed at something already done. This pass then added about eleven hours of its own findings, so the honest remediation bill is **≈ 46 hours**, not 74.9 and not 18.

### 1.2 Severity, after verification

| Severity | As filed | Surviving on the 94 | Added by this pass |
|---|---|---|---|
| Disqualifying | 33 | **1** | **5** |
| Major | 44 | 31 | 8 |
| Minor | 15 | 21 | 5 |
| Polish | 2 | 11 | 2 |

**Thirty-two of the thirty-three "disqualifying" findings did not survive at that severity** — because CH-15, CH-14's archive steps, CH-13's video card and the `.gitignore` rewrite genuinely moved them. Most were downgraded rather than dismissed: the *gate* is closed, the *residue* is real. The one that survived intact is **L3-06, the repository public-flip**, which the consolidated audit believed it had folded into CH-15 and did not. This pass then found five further gate-class defects no auditor raised (§7).

### 1.3 Per-auditor reliability

Kill rate = the share of a lens's findings that ended already-fixed, duplicated, or false.

| Lens | Findings | Confirmed | Already-fixed | Duplicate | False alarm | **Kill rate** |
|---|---|---|---|---|---|---|
| **4 · rubric-scoring** | 20 | 15 | 0 | 4 | 1 | **25%** — *most reliable* |
| **5 · process-integrity** | 20 | 15 | 0 | 5 | 0 | **25%** |
| **2 · ground-rules** | 18 | 11 | 2 | 4 | 1 | **39%** |
| **3 · gate-and-logistics** | 18 | 11 | 3 | 4 | 0 | **39%** |
| **1 · deliverables** | 18 | 12 | 3 | 3 | 0 | **33%** |

The spread is narrower than the raw audit suggested. **Lens 3 looked far worse at the verification stage — 72% killed — and recovered to 39% once challenged**, because its findings had been dismissed as "already fixed" by fixes that turn out to be partial. Lens 4's high duplicate count is not sloppiness: it audited the rubric row by row, so it restates defects other lenses found from a scoring angle.

**Counter-check on quotation accuracy.** Every finding's `requirement_verbatim` was grepped against the source it cited. **87 of 88 checked out** — only `L5-06` misquoted. The auditors were accurate quoters; where they went wrong, they went wrong about the *state of the artifact*, not about the rule. That is worth knowing: it means the findings can be triaged by re-reading the files, which is what this pass did, rather than by re-reading the brief.

### 1.4 Two measurements I do not trust, disclosed

**(a) Fix-soundness.** Each verifier rated the auditor's proposed fix SOUND / PARTIALLY-SOUND / UNSOUND. The result was **84 PARTIALLY-SOUND, 2 SOUND, 2 UNSOUND out of 88**. A judgement that puts 95% of cases in one middle bucket is not discriminating. The *individual* corrections are substantive and several are used below, but **do not read "almost every proposed fix needed correction" as a result.** It is not one.

**(b) The challenge stage's amendment rate.** Of 89 challenges: **74 AMENDED, 11 OVERTURNED, 4 UPHELD**, changing **40 verdicts outright**. A skeptic that fully agrees 4% of the time is not a neutral instrument — it was asked to attack, and it attacked. So I trust the *direction* and the *specific evidence*, not the rate.

**The direction is worth trusting, and here is why.** The dominant movement was **ALREADY-FIXED → CONFIRMED**, thirteen times. The challengers were pointed at exactly that: defend a finding the verifier wants to dismiss. And their conclusion — that the architect's fixes are real but partial — is **independently corroborated**, because I ran my own pass over the eight fixes in §6 before any challenge result existed and reached the same verdict on all eight. Two instruments with different biases agreeing on a direction is evidence; the magnitude is not.

---

## 2. DISQUALIFYING — confirmed, grouped by chunk

Six items. One is the survivor from the 94; five were found by this pass. Ordered by the chunk they land in so they can be applied in one editing pass.

---

### D-1 · `prompts/CH-00.md` cannot execute as written — five internal contradictions stop the first session at hour zero
**Lands in:** `prompts/CH-00.md` (architect pre-flight) · **Raised by:** nobody; found by this pass, sharpening L3-07 / L4-03 · **Hours: 0.5**

> **"STOP RULE.** Spec ambiguous, incomplete or contradictory → stop that item, write it to `QUESTIONS.md` … **Never assume.**" — `CLAUDE.md`, hard rule 1

**VERIFIED, with line numbers:**

| # | Line | The instruction | What forbids or breaks it |
|---|---|---|---|
| 1 | `prompts/CH-00.md:95` | "Add to `CLAUDE.md` end-of-session duties, as the final step: …" | `:100` "`CONTEXT.md`, `plan.md`, `CLAUDE.md` and `PROCESS.md` already exist — **do not edit them.**" and `:274` rider "Protected: … every `.md` at the repo root that already exists … **Read-only.**" + "These override anything above that conflicts." |
| 2 | `prompts/CH-00.md:97` | "add a `prompts/` row to `PROCESS.md` §3's Files table" | same two lines |
| 3 | `prompts/CH-00.md:107` | seed `CHANGELOG.md` with "the four-column table from `PROCESS.md` §5" | `grep -ci "four-column" PROCESS.md` = **0**; `grep -ci "STAGE" PROCESS.md` = **0**. §5 holds a seven-field iteration card, not a table. |
| 4 | `prompts/CH-00.md:75` | "Record this in `QUESTIONS.md` as ruling **Q3** (text below)" | `grep -n "Q3" prompts/CH-00.md` returns **one hit — the forward reference itself**. Only `## Q1` (:113) and `## Q2` (:141) exist. There is no Q3 text. |
| 5 | `prompts/CH-00.md:223` | scope fence: "Change ONLY: repo setup, the canonical skeletons listed above, `src/runlog.py`, `tests/test_runlog.py`." | §1b requires building `tools/export_session.py` and creating `docs/trajectories/build/`. Neither is inside the fence. |

**Why this is disqualifying rather than annoying.** Contradiction 1 is the delivery mechanism for the *fix to the deliverable-4 gap*. If the session obeys the rider, the export duty never enters `CLAUDE.md`, and every session from CH-01 onward silently skips the transcript export — so the fix the architect believes is in place quietly does not run, and the evidence it was meant to capture is volatile. If instead the session obeys §1b and edits a protected file, it has broken the safety rider on the first chunk of a project whose pitch is process discipline.

**EXACT FIX — three edits, all architect-owned, all before CH-00 is issued.**

**(a) REPLACE** `prompts/CH-00.md` lines 95 and 97 with:

```
**The `CLAUDE.md` duty and the `PROCESS.md` Files-table row are ARCHITECT edits and are already applied.
Do not edit those files.** Your job in this section is to build `tools/export_session.py` and create
`docs/trajectories/build/`. Confirm the duty exists by reading `CLAUDE.md`'s end-of-session list; if it
does not, STOP and report rather than editing a protected file.
```

**(b) REPLACE** the scope fence at `prompts/CH-00.md:223` with:

```
**Change ONLY:** repo setup and `.gitignore`/`.gitattributes`, the canonical skeletons listed above,
`src/runlog.py`, `tests/test_runlog.py`, `tools/export_session.py`, and the directories
`docs/trajectories/build/`, `agents/` and `prompts/design/`.
```

**(c) INSERT** the missing Q3 block into `prompts/CH-00.md`, after the Q2 block at line 176. *(The inner `~~~` fence stands for the triple-backtick fence CH-00 uses around its verbatim QUESTIONS.md seeds — restore backticks when pasting.)*

```
**Also seed `QUESTIONS.md` with, verbatim:**
~~~
## Q3 - Precedence chain names a file that is deliberately not redistributed
Raised: CH-00, 2026-08-30. Status: RULED by ARCHITECT, 2026-08-30.

CLAUDE.md's Precedence line names context/01-PROBLEM-PDF.md as the top of the chain.
That file is a full verbatim extraction of micro1's ten-page brief. It is the
organiser's copyright, it is not ours to republish, and under the Participation
Agreement anything committed is assigned to micro1 - so republishing their own
brief back to them serves nobody and creates a licence question where none exists.

RULING: context/01-PROBLEM-PDF.md stays local and git-ignored. The precedence chain
still names it because it IS the top authority for this project; a judge reading
CLAUDE.md should understand that the brief outranks our spec, and the brief is in
their hands already. context/00-MASTER-CONTEXT.md, which is our own synthesis of a
public page, DOES ship.

Consequence for build sessions: do not treat the absence of that file as a defect,
and do not attempt to reconstruct it. If a decision appears to turn on brief text
you cannot read, STOP and ask the architect.
~~~
```

Then amend `CLAUDE.md`'s Precedence line to read `context/01-PROBLEM-PDF.md` **(local, not redistributed — see QUESTIONS.md Q3)**, and add item 6 to `CLAUDE.md`'s end-of-session duties:

```
6. Run `python tools/export_session.py <CHUNK-ID>` and commit the exported trajectory. This is a
   deliverable-4 gate item: the session transcript is the only trace of the coding agents, it lives
   outside the repo, and Claude Code prunes session directories. A chunk whose transcript was not
   exported is not done.
```

---

### D-2 · The point-in-time corpus can contain the answer — the leakage strips were lost in transcription
**Lands in:** `CONTEXT.md` §8 and `plan.md` CH-03/CH-04 (architect pre-flight) · **Raised by:** nobody · **Hours: 1.5**

> *"Wrong here = rigged benchmark = dead submission."* — `plan.md`, CH-03's own "why gated" line

**This is the most important item in this document.** `context/08-FINAL-CALL.md` §5 — the document `CONTEXT.md`'s own header names as its authoritative delta source — carries a section headed **"Leakage strips — publish all three as a named design decision"**. It did not survive into `CONTEXT.md`.

**VERIFIED:** `grep -ci "EFFDNOTP"` → `CONTEXT.md` **0** · `plan.md` **0** · `PROCESS.md` **0** · `prompts/CH-00.md` **0**. Same for `"leakage strip"` and `"Link to an amendment"`.

**VERIFIED structurally, against a real govinfo CFR annual-edition volume** (`cfr2024t40v5.xml`, 5,524,321 B), by walking every `<SECTION>…</SECTION>` block and testing containment:

```
SECTION blocks : 311
EDNOTE    inside SECTION : 26 / 28    (first: § 52.2020)
EFFDNOTP  inside SECTION :  2 /  2    (first: § 52.2320)
CITA      inside SECTION : 252 / 255
EAR       inside SECTION :   1 /   5
```

`CONTEXT.md` §8 sources **the labels** from `<EDNOTE>` and **the input** from CFR annual editions. Those are the same XML tree, and **the label element sits inside the input element.** A naive "extract the section text" — which is exactly what CH-03's card asks for and nothing forbids — carries the editorial note into the model's prompt.

**VERIFIED verbatim, one of the two `<EFFDNOTP>` blocks in that file:**

> "Effective Date Note: At **89 FR 54360**, July 1, 2024, **§ 52.2320** was amended in the table in paragraph (c) revising the entries "R307-110-32" and "R307-110-35" adding the center heading … effective July 31, 2024 **For the convenience of the user, the revised and added text is set forth as follows:** § 52.2…"

That single block carries the FR citation, the section, the operation, every designation touched, and the resulting text.

**Honest bounding of the risk, so this is not overstated.** The as-of edition is chosen at (effective year − 1), so the note for the rule under test would normally land in the *next* edition. The leak is therefore not guaranteed per item. It fires anyway in three ways that are not hypothetical: off-by-one edition selection for any mid-year effective date; `<EFFDNOTP>`, which by design prints amendments *pending at compile time* — i.e. the rule under test — verbatim; and prior `<EDNOTE>`s on the same section, which are label-correlated even when the specific note is absent. `"could not be incorporated"` appears **0** times in this particular volume, so I have **not** observed a positive label leaking. **The structural containment is what is measured; the per-item rate is UNKNOWN and is precisely what the fix must measure.**

**Why it is gate-class anyway: it fails silently and in the flattering direction.** Accuracy goes *up*. Every guard in `CONTEXT.md` §7 still passes. `GOOD.md`'s pre-registered thresholds are cleared. And the FULL adversarial gate on CH-03 cannot catch it, because `CONTEXT.md` — the only document the reviewer is told to reimplement from — never mentions it.

**EXACT FIX (a) — INSERT into `CONTEXT.md` §8, immediately before "### Eval set":**

```
### Leakage strips — mandatory, counted, and published

The label and the input come from the same XML tree. Measured on a real govinfo annual-edition volume
(`CFR-2024-title40-vol5`): of 28 `<EDNOTE>` elements, **26 sit inside a `<SECTION>` block**; both
`<EFFDNOTP>` elements do; 252 of 255 `<CITA>` elements do. `<EDNOTE>` is where the gold label lives.
`<EFFDNOTP>` prints amendments pending at compile time verbatim — one observed block names the FR
citation, the section, every designation touched, and then says "For the convenience of the user, the
revised and added text is set forth as follows".

Therefore, before any section text is frozen or shown to any arm, strip and count:

| Element | Why |
|---|---|
| `<EDNOTE>` | carries the editorial note that IS the label |
| `<EFFDNOTP>` | prints the pending amendment, i.e. the rule under test, verbatim |
| `<CITA>` | source credit naming the amending rule |
| `<EAR>` | editorial amendment record |

Per-element strip counts go in the freeze manifest and in the README as a named design decision.
The stripper is pure (hard rule 8) and lives in shipped code, so `refetch.py` reproduces the stripped
corpus byte-for-byte and the manifest verifies from a clean clone.

*(The eCFR "Link to an amendment published at NN FR …" annotation needs no strip here: it is an eCFR
artifact and appears 0 times in the govinfo annual editions, which are our only source. One of the
three strips named in 08-FINAL-CALL.md §5 is therefore moot under the govinfo-only constraint.)*
```

**EXACT FIX (b) — REPLACE `plan.md` CH-03's Done-when with:**

```
**Done when:** ≥ 42 pairs (n ≥ 84); **exact instruction-count matching asserted by a test**; full
exclusion ladder published; manifest verifies from a clean clone; **the corpus is EXTRACTED then
frozen — only the `<SECTION>` blocks and `<AMDPAR>` blocks the eval set actually uses, never whole
title XMLs or whole FR issues**; **and the leakage-strip test passes.**

**The leakage-strip test — this is the one that stops a rigged benchmark.** It FAILS if any frozen
section text contains (a) an `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>` or `<EAR>` element, (b) the FR
citation of its own rule under test, or (c) any of the literals "could not be incorporated",
"Editorial Note", "Effective Date Note", "set forth as follows". Per-element strip counts are printed
and committed to the manifest.
```

**EXACT FIX (c) — ADD to `plan.md` CH-04's scope:** `report the count of items whose UNSTRIPPED text would have contained the answer — that number is itself a publishable result about the corpus.`

**EXACT FIX (d) — ADD to the CH-03 review prompt:** `independently re-derive the strip counts, and confirm the leakage test FAILS on unstripped input before accepting that it passes on stripped input.`

---

### D-3 · Nobody owns making the repository public — judges get a 404
**Lands in:** `plan.md` CH-15 (architect pre-flight; executed at CH-15) · **Raised by:** L3-06 (+ L2-13, L5-12 partial) — **3 of 5 auditors** · **Hours: 0.2**

> **"Give judges enough access to run the project and reproduce the main result."** — `01-PROBLEM-PDF.md` §7 ground rule 10

**VERIFIED:** `grep -ci "public" plan.md` = **0**. The only mention anywhere in the plan is `prompts/CH-00.md:70` — *"It becomes public at submission"* — a subordinate clause inside a prompt seed for a chunk that finishes 30 hours before submission. It appears in no chunk card, no done-when, and no checklist. The consolidated audit believed it had folded this into CH-15's checklist; it had not.

**Why the natural check gives a false pass:** `gh repo view` and any browser carrying the operator's GitHub session both succeed on a private repo. Verified precondition: `gh` is installed at `/c/Program Files/GitHub CLI/gh` and authenticated as `chinmoypaul8897` with scopes `gist, read:org, repo, workflow` — `repo` is sufficient for the visibility change.

**EXACT FIX — INSERT into `plan.md` CH-15's Procedure as new steps 2–3, renumbering the rest:**

```
2. **Flip the repository public. This step has an owner and a proof, or the judges get a 404.**
   `gh repo edit chinmoypaul8897/instruction-that-wont-execute --visibility public --accept-visibility-change-consequences`
   Then verify from OUTSIDE your own session — `gh` and any browser carrying your GitHub cookie both
   succeed on a private repo and give a false pass:
     a. open the HTTPS URL in a private window with no GitHub session — expect the repo, not a 404;
     b. `git clone https://github.com/<owner>/<repo>.git` into a fresh temp dir with credentials
        unset — expect success with no prompt;
     c. screenshot both into `docs/evidence/access/`.
3. From that anonymous clone, confirm `SUBMISSION.md`'s six paths resolve and the video URL plays.
```

**AND REPLACE** CH-15's Done-when with:

```
**Done when:** the submission is in a submitted state (not draft); **the repository is public and was
cloned anonymously from a session with no GitHub credentials**; the video link plays from a signed-out
browser; and the uploaded zip has been re-downloaded and opened to confirm it is intact.
```

---

### D-4 · The `.gitignore` fix leaves the operator's phone number in two files that ship
**Lands in:** `prompts/CH-00.md` §1 (architect pre-flight) · **Raised by:** nobody — the auditors raised the file that *is* now excluded · **Hours: 0.25**

> **"Keep credentials and private information outside the submission."** — `01-PROBLEM-PDF.md` §7 ground rule 08

**VERIFIED:** grepping the tracked set for the operator's phone number returns **line 24 of `context/09-COMPLIANCE-AUDIT.md`** and **one hit in `context/09b-audit-raw.json`**. Both files are inside the 20-file tracked set, and `prompts/CH-00.md`'s "What SHOULD be tracked" names `context/0[3-9]*.md` and the `*-raw.json` agent outputs **explicitly**.

**This document made the same mistake and has been corrected.** An earlier draft of this section quoted the number literally, four times. It has been replaced with `<OPERATOR-PHONE>` throughout, and the fix below is written so it can be applied without ever typing the digits. That is not an aside: it is the shape of the defect. **The number spreads through the act of auditing for it.** Every document that reports the leak becomes a new copy of it, which is why the fix must be a grep-and-replace run over the tracked set immediately before the second commit, not a one-time edit to two named files.

The `.gitignore` correctly excludes `context/02-ABOUT-ME.md` and `context/me/`. The number survives anyway, because an auditor quoted it into the audit that ships. Ground rule 08 covers *private information*, not only credentials — and no ignore rule can reach a number that is inside a file you intend to keep.

**EXACT FIX — ADD to `prompts/CH-00.md` §1 as step 5, before the second commit.** Written so the architect never has to type the digits: the operator supplies them once, into a local scratch variable that is never committed.

```
5. **Redact before the second commit.** Ground rule 08 covers private information, not only
   credentials, and no ignore rule can reach a value that sits inside a file we intend to ship.
   Ask the operator for the two strings to scrub - the personal phone number and the personal
   email address - and hold them in shell variables only. Then, over the TRACKED set:

     git ls-files -z | xargs -0 grep -l -e "$PHONE" -e "$EMAIL"
     # for each hit: replace with [redacted - operator contact detail, ground rule 08]
     git ls-files -z | xargs -0 grep -c -e "$PHONE" -e "$EMAIL"   # must print nothing

   Paste the empty final result into your report. Known carriers at the time of writing:
   `context/09-COMPLIANCE-AUDIT.md` and `context/09b-audit-raw.json` for the phone number.
   **Do not hard-code the list.** Every document that reports the leak becomes a new copy of it -
   this remediation plan itself had to be scrubbed of four occurrences - so the check is a sweep
   over whatever is tracked at commit time, and it is repeated by the pre-commit hook in §3.
```

---

### D-5 · The `.gitignore` is name-specific, and CH-01's first act is a multi-gigabyte download
**Lands in:** `prompts/CH-00.md` §1 + `plan.md` CH-01/CH-03 (architect pre-flight) · **Raised by:** nobody; Q2's C1 exists but never reached a chunk card · **Hours: 0.5**

> **"Source Code — an UPLOADED FILE (zip). MAX 50 MB."** — `prompts/CH-00.md` Q2, ruled by the operator from inside the form

**VERIFIED:** the `.gitignore` names exactly two XML files — `cfr2024t40v5.xml` and `fr20240103.xml`. There is no `*.xml`, no `data/raw/`, no `dist/`, no `*.zip`, no `*.mp4`. **VERIFIED:** `plan.md:22` CH-01's scope is "download ECFR bulk title XML from govinfo", and `CONTEXT.md` §8 targets 50 titles. **VERIFIED:** the `<60 tracked files / no file over 25 MB` assertion exists **once**, at `prompts/CH-00.md:69`, runs at CH-00 *before the download exists*, and is never repeated — `grep -c "25 MB" plan.md` = 0. **VERIFIED:** the rule that would prevent it, Q2's C1 *"Extract-then-freeze, never download-then-freeze"*, lives only at `prompts/CH-00.md:157` — `grep -ci "extract-then-freeze" plan.md` = **0**.

**Quantified against the real corpus on disk:**

| Approach | Size | Against a 50 MB cap |
|---|---|---|
| Extract-then-freeze — only the `<SECTION>` and `<AMDPAR>` blocks used, n = 84 | **~1.4 MB** (median-based ~0.14 MB) | fine |
| Freeze whole FR issues, 42 rules × 2.06 MB | **~87 MB** | already over, alone |
| Freeze whole CFR volumes, 42 × 5.51 MB | **~231 MB** | 4.6× over |
| Download 50 ECFR title XMLs | **~2.3 GB** | 46× over |

*(measured: `cfr2024t40v5.xml` 311 `<SECTION>` blocks, mean 16,638 B, median 1,571 B, max 919,774 B; `fr20240103.xml` 64 `<AMDPAR>` blocks, mean 94 B. Nine-title figure of 407 MB is the audit's, at `prompts/CH-00.md:157`.)*

**EXACT FIX (a) — REPLACE the `.gitignore` block in `prompts/CH-00.md` §1 step 1 with:**

```
# secrets and env
.env
.env.*
.venv/
__pycache__/
*.pyc
node_modules/

# third-party material we must not redistribute (micro1's own assets)
d.pdf
context/01-PROBLEM-PDF.md
context/media/
context/images/
context/slices/
context/screenshots/
context/raw/

# operator personal data (ground rule 08)
context/02-ABOUT-ME.md
context/me/

# research scratch from prior sessions - large, superseded, not part of the build
aec/
bip/
killtest/
probe/
replay/
scraper/
hz.html
wl.html

# bulk corpus downloads - NEVER tracked. data/ holds only extracted, frozen artifacts.
*.xml
!data/**/*.xml
data/raw/
data/cache/
dist/
*.zip

# large media - the video is hosted, not committed (see CH-13)
*.mp4
*.mov
*.mkv

# Windows/Cygwin crash dumps - these land in the repo root unannounced
*.stackdump
```

Five changes, each load-bearing: `*.xml` + `data/raw/` + `data/cache/` catch CH-01's download; `*.mp4`/`*.mov`/`*.mkv` catch CH-13's committed fallback (§3, M-6); `dist/` + `*.zip` stop the submission archive being committed into itself; `*.stackdump` catches Cygwin crash dumps, which land in the repo root unannounced — **VERIFIED: one appeared during this pass** (`grep.exe.stackdump`, 1,729 B, and it is the only file besides this document that changed in the working tree while the pass ran); and the three superseded prompt files are **deliberately removed** from the ignore list — see M-5.

**EXACT FIX (b) — APPEND to `plan.md` CH-01's Done-when:**

```
Downloads land in `data/raw/`, which is git-ignored and never tracked. **Extract-then-freeze:** what
enters `data/` is only the `<SECTION>` and `<AMDPAR>` blocks the eval set uses — never a whole title
XML or a whole FR issue. Measured: extraction is ~1.4 MB at n = 84; whole CFR volumes are ~231 MB and
50 ECFR title XMLs are ~2.3 GB, against a 50 MB submission cap. Print `du -sh data/` and the tracked
file count at the end of the chunk.
```

**EXACT FIX (c) — ADD to `prompts/CH-00.md` §3**, so the assertion runs more than once:

```
Install a pre-commit hook, `.githooks/pre-commit`, and `git config core.hooksPath .githooks`. It
rejects the commit if any staged file exceeds 25 MB or if the tracked count exceeds 300. The CH-00
one-off assertion protects the tree as it stands today; the hook protects the tree every later chunk
creates, which is where the 50 MB cap actually gets broken.
```

---

### D-6 · Q2's C2 never reached CH-12 — the trajectory selection rule does not exist
**Lands in:** `plan.md` CH-12 (architect pre-flight) · **Raised by:** L1-10 partially · **Hours: 0.4**

> **"Include representative trajectories for every agent you used."** — `01-PROBLEM-PDF.md` §8 deliverable 04

**VERIFIED:** `plan.md` CH-12's entire card is two sentences. `grep -ci "selection rule" plan.md` = **0**; `grep -ci "curated" plan.md` = **0**. Q2's C2 — *"Ship a curated representative set in the zip; ship the complete set in the git repo and link it from the Description. Record the selection rule so the curation is auditable"* — exists only at `prompts/CH-00.md:160-166`. **VERIFIED:** the session transcripts total ~21.5 MB today and grow every session; ~750+ eval runs with full prompts would add far more. Against a 50 MB zip, unselected trajectories are not shippable, and *unrecorded* selection reads as cherry-picking on an event whose validation screen names **trace-integrity** as a gate check.

**EXACT FIX — REPLACE `plan.md`'s CH-12 card with:**

```
### CH-12 · Trajectories + AI-USE.md
**Scope:** package trajectories for all three agent classes, with a written selection rule.

**The selection rule, recorded in `docs/trajectories/README.md` and applied mechanically:**
- one BUILD session transcript per phase (CH-00, one Phase-1 chunk, one Phase-2 chunk);
- **every REVIEW session that returned FAIL** — a FAIL review is the best human-checkpoint evidence
  in the project, and excluding one would be the only selection choice that flatters us;
- one eval run per arm, chosen as the median-length run of that arm, tie broken by lowest item id;
- both interactive human-checkpoint runs from CH-08 in full.
Everything not selected still ships in the git repo; the zip carries the selected set. The
Description links the repo for the rest.

**Also:** `AI-USE.md` names every model, tool and agent across all three classes — research/ideation
(the four `context/*-raw.json` swarms and their prompt files in `prompts/design/`), coding (chunk
prompt + session JSONL + resulting commits), and solution (run-logger JSONL) — stating for each what
ships and why.

**Done when:** the selection rule is committed before the selection is made; every FAIL review is
present; `du -sh` of the shipped trajectory set is printed and is under 20 MB.
```

---

## 3. MAJOR — confirmed, grouped by chunk

Twenty-four survived from the 94; six were added by this pass. Grouped by target so the architect applies them file by file.

### Architect pre-flight — the spec files themselves

**M-1 · `PROCESS.md` §7 is stale and contradicts `plan.md`** · *added by this pass; sharpens L4-01, L2-03, L3-03, L3-04* · **0.5 h**
**VERIFIED:** `PROCESS.md` §7's Phase 3 table lists CH-10…CH-14 only. `grep -c "CH-15" PROCESS.md` = **0**. Its CH-14 row omits the archive, the zip and `SUBMISSION.md`; its Phase-1 budget still reads "~5 h"; its Phase-3 budget still reads "~10 h". Two shipping architect files now disagree on the chunk list, and `PROCESS.md` is the one carrying the budgets.
**FIX — REPLACE `PROCESS.md` §7's three phase tables with the reconciled plan in §8 below**, and replace the single HARD CUTOFF line with:
```
**HARD CUTOFF: at T−12h (2026-08-31 06:00 UTC), Phase 3 begins regardless of Phase 2 state.**
**Wall-clock triggers, independent of dependency state:**
  2026-08-30 23:59 UTC — organiser's final-day checkpoint. Read the challenge page and any organiser
                         mail. If anything is anomalous, email yeison@micro1.ai then, not Monday.
  2026-08-31 06:00 UTC — Phase 3 opens. Phase 2 stops wherever it is.
  2026-08-31 10:00 UTC — video uploaded to unlisted YouTube (T−8h; processing can take hours).
  2026-08-31 12:00 UTC — DRAFT-1 saved on the form with whatever exists. From here the project is insured.
  2026-08-31 15:00 UTC — CH-15 hard start.
  2026-08-31 17:00 UTC — last permitted touch. Nothing after 17:30.
```

**M-2 · `PROCESS.md` is in neither `CLAUDE.md`'s read order nor its precedence chain** · *added by this pass* · **0.1 h**
**VERIFIED:** `CLAUDE.md`'s read order is CLAUDE.md → plan.md → CONTEXT.md → STATUS.md → PROGRESS.md → QUESTIONS.md → docs/reviews/. Its precedence chain is 01-PROBLEM-PDF → CONTEXT.md → plan.md → code → tests → memory. `PROCESS.md` appears in neither, yet it defines the gate policy, the files table, the iteration card and the hard cutoff. Only `prompts/CH-00.md` tells a session to read it, and only §3/§4/§5.
**FIX — REPLACE `CLAUDE.md`'s "## Read order" list item 2 with:** `2. `plan.md` → your chunk card, and `PROCESS.md` §6–§7 for the gate policy and the clock` — and add `PROCESS.md` to the precedence line between `CONTEXT.md` and `plan.md`.

**M-3 · The ship/no-ship ledger omits the source, the tests and the README** · *added by this pass* · **0.3 h**
**VERIFIED:** `PROCESS.md` §3's Files table has no row for `src/`, `tests/`, `README.md`, `REPRODUCE.md`, `prompts/`, `PROVENANCE.md`, `agents/`, `SUBMISSION.md` or `LICENSE`. `grep -c "tests/"` → `plan.md` **0**, `PROCESS.md` **0**. The word `tests/` never appears in `plan.md` at all.
**Why it matters beyond tidiness:** *"A valid submission must be … complete … and include the required repository, archive, **tests**, README, agent-use evidence, and demo video."* — `00-MASTER-CONTEXT.md` §12 FAQ. Tests are a named completeness item at the qualification gate, and the ledger a build session is told to consult says nothing about them.
**FIX — INSERT these rows into `PROCESS.md` §3's Files table:**
```
| `prompts/` | every chunk prompt verbatim as issued — **the agent instructions deliverable 1 asks for** | yes |
| `prompts/design/` | the design-phase agent instructions that produced `context/06` and `context/07` | yes |
| `agents/` | one file per evaluation arm: the exact instructions that shape it | **deliverable 1** |
| `src/` | the solution, the scorer, the resolver | yes |
| `tests/` | the suite — **named as a required item by the submission-validity FAQ** | yes |
| `README.md` | user → bottleneck → value → changelog → failure mode → hot take | **deliverable 1** |
| `REPRODUCE.md` | clean-environment guide, both tiers, exact commands | **deliverable 2** |
| `PROVENANCE.md` | what pre-existed vs what was built — ground rule 02 | yes |
| `SUBMISSION.md` | the six FAQ items with a path or URL each | yes |
| `LICENSE` · `THIRD-PARTY.md` · `SAFETY.md` | licence, dependency clearances, human-reviewer statement | yes |
```

**M-4 · The mandated Improvement Changelog table does not exist** · L1-06 · **0.4 h**
**VERIFIED:** `grep -ci "four-column" PROCESS.md` = 0. This is also contradiction #3 in D-1.
**FIX — INSERT into `PROCESS.md` §5, directly under the heading:**
```
### The Improvement Changelog table — the shape the brief mandates

`CHANGELOG.md` is table-first. These four columns, verbatim from the brief, one row per stage:

| STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING |
|---|---|---|---|
| Baseline | | | |
| Iteration 1 — tool (`cfr_resolve`) | | | |
| Iteration 2 — skill (`SKILL.md`) | | | |
| Iteration 3 — memory (ordered-state ledger) | | | |
| Control — B0′ (compute-matched) | | | |
| Removed 1 — current-CFR-text leakage probe | | | |
| Removed 2 — intra-rule collision detector | | | |
| Final | | | |

Every EVIDENCE cell is a relative path into `docs/evidence/`. The iteration cards below are backing
detail and sit underneath the table, not instead of it. The README embeds the table; it does not
link to it. **The card mechanism applies to controls and removals too, not only to CH-05…CH-07.**
```
*(This also closes L1-17 — the changelog's missing rows for B0′ and the two removed experiments.)*

**M-5 · The `.gitignore` deletes the research agents' instructions while shipping their outputs** · *added by this pass; sharpens L2-11* · **0.15 h**
**VERIFIED:** `DIVERGENT-RESEARCH-PROMPT.md` (194 lines) is the agent instruction that produced `context/06-DIVERGENT-RESEARCH.md`; `KILL-TEST-PROMPT.md` (161 lines) produced `context/07-KILL-TEST.md`. Both outputs ship; both instructions are in the ignore list. **VERIFIED the stated reason is false:** the ignore comment claims *"their content lives in PROVENANCE.md and prompts/"* — `PROVENANCE.md` is 5,591 B and contains none of their text, and `prompts/` held only `CH-00.md` and `REMEDIATION.md`.
> **"Make each trajectory easy to follow from the agent instructions to the final result."** — §8 deliverable 04
**FIX — INSERT into `prompts/CH-00.md` §1 after step 4:**
```
4b. **Move, do not delete, the design-phase agent instructions.**
    mkdir -p prompts/design docs/process/superseded
    git mv DIVERGENT-RESEARCH-PROMPT.md prompts/design/
    git mv KILL-TEST-PROMPT.md          prompts/design/
    git mv BUILD-PHASE-1-PROMPT.md      docs/process/superseded/
    The first two ARE the agent instructions that produced context/06 and context/07, both of which
    ship. Shipping the outputs while deleting the instructions is the one half of deliverable 4 we
    would be failing on purpose. The third is a superseded plan that contradicts plan.md, so it moves
    out of the root where a build session would read it, but stays in the repo because PROVENANCE.md's
    timeline refers to that phase.
```

**M-6 · CH-13 commits a raw MP4 and nothing ignores video** · *added by this pass, independently surfaced by the L1-04 verifier* · **0.1 h**
**VERIFIED:** `plan.md:93` "Raw MP4 also committed as fallback." The `.gitignore` has no video rule. `plan.md:100` asserts the archive is < 50 MB. A five-minute screen recording routinely exceeds 50 MB on its own, and the failure would surface at CH-14 — second to last.
**FIX:** covered by D-5's `.gitignore` (`*.mp4`/`*.mov`/`*.mkv`). **AND REPLACE** `plan.md:93`'s fallback clause with: `A second hosted copy (unlisted, different provider) is the fallback. **The MP4 is not committed** — it would enter `git archive` and can break the 50 MB assertion, which is the one cap that must not move.`

**M-7 · AMBER has no action, RED has no spec, and CH-02/CH-03 have no numeric fallback — all three already exist in the source document and were lost in transcription** · L5-03, L5-04, L5-05 · **0.75 h**
**VERIFIED:** `plan.md:45` GREEN = "B0-agent − B0 ≥ 15 pp, McNemar p < 0.05, **n ≥ 84**". `context/08-FINAL-CALL.md:202` GATE-3 = "B0-agent − B0 ≥ +15 pp with McNemar p < 0.05 at **n ≥ 200**." The n was halved. **VERIFIED** `08-FINAL-CALL.md:196` carries a pool fallback that exists nowhere now: *"Decides on: ≥ 60 … if the full scan returns < 60, fall back to n = 84 as originally specified, demote localisation and class recall to a case study, and proceed."* **VERIFIED** `:206` specifies the RED path in full: *"abandon at H6 and ship the negative result … It costs ~7 hours and leaves 16 to write it up properly."* `plan.md:48` reduces this to "project dead, shipped as dead". **VERIFIED** `PROCESS.md` §7 still says Phase 2 runs "only if GREEN", so AMBER has no branch at all.
**The fix is restoration, not invention.** **REPLACE `plan.md`'s CHECKPOINT decision rule with:**
```
- **GREEN** — B0-agent − B0 ≥ 15 pp, McNemar p < 0.05, at the largest n the eval set supports →
  Phase 2 proceeds.
- **AMBER** — gap present, p ≥ 0.05 → **Phase 2 PROCEEDS.** The checkpoint result enters
  `CHANGELOG.md` as the Baseline row with exact n, gap and p. `GOOD.md` is unchanged. The agent is
  built to move the gap, not to rescue the p-value. If A1 is still p ≥ 0.05, the README leads with
  effect size, its confidence interval, and the n this design would need for power.
- **RED** — gap < 8 pp, or B0 ≥ 0.70 → if B0 ≥ 0.70, strip the *quoted anchor text* (keep operation
  and designation), re-run the gate **once**. Still red = **the accuracy claim is withdrawn and the
  null is published**: CH-08 becomes "why the gap did not open, measured"; the corpus, attributor,
  scorer and permutation null become the contribution; deliverable 4 is satisfied by baseline-arm
  trajectories. This is what 08-FINAL-CALL.md §5 pre-committed to and it leaves ~16 hours to write
  it up properly.
  **But an advanced solution STILL SHIPS — see the validity constraint below. Do not cut CH-05/06/07
  to nothing on RED.** Ship the tool and the skill, and claim the improvement on one of the four
  other axes the rules accept, measured with the same discipline: instruction-level resolution-claim
  correctness (already specified in `CONTEXT.md` §7 as the high-power diagnostic), the checkpoint
  queue's catch rate, per-arm token cost, or coverage of the pool. Report the accuracy null as the
  headline honestly, and the axis that did move beside it.

**VALIDITY CONSTRAINT — this is why the RED path may not cut the agent entirely.**
> *"**Every valid entry must present both a baseline solution and an advanced solution.** The advanced
> solution should show a meaningful improvement in capability, reliability, efficiency, coverage or
> engineering quality, not a cosmetic variation."* — `00-MASTER-CONTEXT.md` §4, verbatim; restated as
> §0 fact 6, *"Every entry must ship BOTH a baseline solution AND an advanced solution."*

The word is **valid**, which ties it to the qualification gate rather than to the rubric. `plan.md:54`
and `PROCESS.md` §7 both gate Phase 2 on GREEN — so a RED checkpoint under the current wording
produces an entry with **no advanced solution at all**. **Note the ambiguity honestly:** this sentence
is in the master context (the HackerEarth page) and **not** in the brief — `grep -c "advanced
solution" context/01-PROBLEM-PDF.md` = **0** — and the master context's own header limits its
authority to "dates, prizes, eligibility, registration and FAQs". Whether Theme binds is genuinely
unclear, which under hard rule 1 is a STOP-and-record, not an assumption. **Record it as a ruling and
take the safe reading, because the safe reading is nearly free:** the five acceptable improvement
axes mean a RED accuracy result does not have to mean "no advanced solution" — it means the
improvement is claimed on a different axis and the accuracy null is published beside it.

**Pre-registered numeric fallbacks — written now, before any number exists, which is what makes
this pre-registration rather than rationalisation:**
- **CH-02.** If global attributor completeness lands in [0.80, 0.90), restrict the eval set to FR
  documents with per-document completeness ≥ 0.90, publish the restriction as a named rung of the
  exclusion ladder with its count, and report both figures. Below 0.80 the attributor is a documented
  failure and the headline is withdrawn.
- **CH-03.** Pool gate: decides on ≥ 60 section-level defect notes with a resolvable FR citation. If
  the full scan returns < 60, fall back to n = 84, demote localisation and class recall to a case
  study, and proceed. If pairs land in [30, 42), report the real n and state in `GOOD.md` and the
  README the effect size the sample can and cannot detect. **Do not relax the exact
  instruction-count match to inflate n** — that is precisely how a predecessor died.
```

**M-8 · Phase 1's budget excludes its own review mechanics; there is no strike rule in `PROCESS.md`, no time box, no sleep plan, no MVS list** · L5-01, L5-02 (partial), L5-07, L5-16, L5-11 · **1.5 h**
**VERIFIED:** `PROCESS.md:156` "Phase 1 — foundation and the go/no-go · ~5 h" while `PROCESS.md` §6 mandates, for each of CH-02/03/04, "reimplement the load-bearing logic from `CONTEXT.md` alone, importing nothing from the project, and diff" plus mutation testing. `grep -ci "strike" PROCESS.md` = **0** (the rule lives only in `plan.md`'s header, and `PROCESS.md` §2's fix loop is still unbounded). `grep -ci "sleep"` = 0, `"alarm"` = 0, `"MVS"` = 0 across all four architect files.
**FIX — INSERT into `PROCESS.md` §6 after the gate table:**
```
**Tiered review.** MANDATORY CORE (45–70 min): rerun the suite from clean and reproduce the count ·
reimplement the load-bearing logic from `CONTEXT.md` alone and diff · rebuild each probe on the
pre-change commit and confirm it fails there. IF-TIME: mutation testing, secret sweep (CH-14
duplicates the latter). The architect picks the tier per chunk and records it as a ruling.

**NUMBERS-ONLY review** — a third, cheap tier (30–40 min, no reimplementation). A fresh session
receives only the committed per-item verdict CSVs and `CONTEXT.md` §7, independently recomputes
accuracy, the McNemar statistic, the bootstrap CI and the effect size, confirms the bootstrap
resamples **documents not items** (with a probe that fails under item-level resampling), confirms
each ablation arm differs from A1 in exactly one capability by diffing arm configs, then diffs
against the reported figures. **Applies to the CHECKPOINT before its call is acted on, and to CH-08
before any number reaches the README.**

**Two-strike rule.** A gated chunk gets at most two fix→re-review rounds. On a second FAIL the
architect either accepts the chunk with its open findings copied verbatim into the README's
LIMITATIONS section and the review report shipped as-is, or invokes the chunk's pre-registered
fallback. The decision and its UTC timestamp go in `QUESTIONS.md`. There is no third round.
```
**AND INSERT into `PROCESS.md` §7, after the wall-clock triggers:**
```
**Minimum viable submission — the drop list, in drop order, last dropped last.** At the T−6h ritual,
read this aloud and mark each item done/not-done before touching more code.
1. Public repo + < 50 MB zip + a submitted form
2. README with user / bottleneck / value / changelog / main failure mode / hot take
3. Tier-1 offline reproduction reaching ONE headline number
4. Video ≤ 5:00
5. Trajectories + `AI-USE.md`
6. Everything else
Anything below the line ships with a stated LIMITATION, never silently absent.

**One protected sleep block of 4.5 h**, placed against the govinfo bulk downloads, with the next two
chunk prompts pre-written so the operator wakes to a queue rather than to a decision.
```

**M-9 · `CONTEXT.md` states the same measurement twice with two different numbers** · *added by this pass* · **0.2 h**
**VERIFIED:** `CONTEXT.md:47` (§3) *"The **+32 pp** from giving the model the CFR text belongs to `B0-agent`"*; `CONTEXT.md:209` (§11) *"giving the agent the CFR text moved accuracy **+27.3 pp**"*. Same intervention, same corpus, 162 lines apart, both shipping, neither carrying an evidence path.
**FIX:** pick one, delete the other, and attach its evidence path. If neither can be re-derived, replace both with the CH-08 figure and label the pilot number `PILOT (pre-competition, n=NN)`.

**M-10 · "order-sensitive" carries two meanings 32× apart against the same denominator** · *added by this pass* · **0.2 h**
**VERIFIED:** `CONTEXT.md:106` (§6, justifying **keeping** memory) *"order-sensitivity fires on **38–42%** of items (31/82 and **833/1,984**…)"*; `CONTEXT.md:198` (§10, justifying **removing** the collision detector) *"**26/1,984** corpus items (**1.31%**) are order-sensitive"*. Same phrase, same denominator, numerators 833 and 26. Inherited from `08-FINAL-CALL.md:10` and `:160`, where context at least separated the two senses; `CONTEXT.md` strips that context. A build session at CH-07 reading both must STOP under hard rule 1.
**FIX — REPLACE the phrase in both places** with the two named senses: §6 → `state-carry sensitivity (instruction k+1 reads the state instructions 1..k left): 833/1,984 = 42.0%`; §10 → `redesignation-collision sensitivity: 26/1,984 = 1.31%`.

**M-11 · The pre-registered success criterion is unreachable at the top of the spec's own predicted range** · *added by this pass* · **0.2 h**
**VERIFIED:** `CONTEXT.md:60` predicts B0-agent at `~0.75–0.82`; `:62` predicts A1 at `~0.85`; `:132` requires `A1 ≥ B0-agent + 8 pp`; `:133` gives point predictions `B0-agent ≈ 0.75 · A1 ≈ 0.85`. At the point prediction the criterion clears by 10 pp. At the top of §4's own range (0.82) it demands A1 ≥ 0.90 — above the predicted 0.85 and inside the zone §7 itself warns against (*"Do not chase 1.00. A saturating metric reads as a rigged baseline"*).
**The defect is not the hard target — that is correct practice.** It is that §4 and §7 predict the same arm differently, and `GOOD.md` is committed before any arm runs while hard rule 5 forbids moving it afterwards. **FIX:** reconcile §4's range to §7's point prediction (or vice versa) **before** `GOOD.md` is written at CH-04.

### CH-00

**M-12 · The instructions that shape each agent are not shipped as files** · L1-05 · **1.0 h**
**VERIFIED:** `grep -ci "agents/"` = 0 across all four architect files. `CONTEXT.md` §4 defines five arms and no chunk commits any arm's prompt text.
> **"Include the code as well as the instructions that shape each agent."** — §8 deliverable 01
**FIX — ADD to `prompts/CH-00.md` §2's skeleton table:**
```
| `agents/` | one file per arm — `B0.md`, `B0-agent.md`, `B0-prime.md`, `A1.md`, `A1-SKILL.md`, and the `cfr_resolve` tool schema — plus `agents/load.py`, a loader that returns (text, sha256). Arm scripts READ these files; they never embed prompt strings. `run_start.agent_instructions` records the file path AND its SHA-256 beside the resolved text, so a judge can confirm the trajectory used the shipped instructions. Create the directory and the loader now; the CHECKPOINT fills B0/B0-agent; CH-05…CH-07 fill A1. |
```

**M-13 · The secret scan names no tool and no pass criterion, and does not cover the risk the logger creates** · L3-10 · **0.5 h**
**VERIFIED:** `grep -ci "gitleaks"` = 0 everywhere. The logger writes `agent_instructions` and raw `tool_response.output` into committed files, so it *creates* the exposure the scan must cover.
**FIX — ADD to `prompts/CH-00.md` §3:** `The logger WHITELISTS the fields it writes rather than dumping raw tool output.` **AND REPLACE `plan.md` CH-14 step 2 with:**
```
2. **Secret scan, with a named tool and a pass criterion.** `gitleaks detect --source . --log-opts="--all"`
   over the full history, plus an explicit regex sweep of `docs/trajectories/**/*.jsonl` for
   `sk-ant`, `AIza`, `Bearer `, `<OPERATOR-PHONE>`, and the funded key's own first eight characters.
   PASS = zero findings. Commit the tool version and the clean output to
   `docs/evidence/secret-scan/`. A scan with no recorded criterion is not a scan.
```

**M-14 · The API budget is short by roughly an order of magnitude** · L5-06 · **0.4 h**
**VERIFIED:** `prompts/CH-00.md` Q1 estimates *"~750 programmatic model calls (3 arms × 3 reps × ~84 items)"* and *"Budget USD 20-30"*. That covers the CHECKPOINT only. CH-08 adds three ablation arms plus B0′ plus final arms × 3 reps. **Note:** L5-06 was filed as "Q1 is OPEN" and is FALSE on that point — Q1 is ANSWERED, and it is the one finding whose requirement quote did not check out. What survives is only the arithmetic.
**FIX — REPLACE Q1's budget line:** `RULING: paid Anthropic API. Budget USD 150-250, loaded by the operator. The earlier USD 20-30 figure covered the CHECKPOINT only (3 arms x 3 reps x ~84 items); the full matrix is 7-8 arms x reps x ~84 multi-turn runs each carrying point-in-time CFR section text.` **AND ADD to `GOOD.md`'s pre-registration:** `Pre-registered cost reduction: if the USD ceiling is reached, ablation arms drop from 3 reps to 1; final arms keep 3. This cut is declared here, before any result exists, so that taking it later is a recorded decision rather than a panic.` **AND** verify the model id in the logger's `PRICES` dict is one the funded account can actually call — a price basis naming an uncallable model silently corrupts every cost row.

**M-15 · The architect is a single point of failure whose state lives in chat** · L5-08 · **0.4 h**
**VERIFIED:** `PROCESS.md` §3 declares *"Chat history is not a record"* while §1 explains the architect must be this session because *"re-bootstrapping costs hours we don't have."* Both cannot be true. `grep -ci "ARCHITECT.md"` = 0.
**FIX — ADD `ARCHITECT.md` to `prompts/CH-00.md` §2's skeleton table** with: `after every chunk, a dated 12-line state block — current chunk and verdict, next chunk, every number verified so far with its evidence path, open rulings, and the read-order a replacement architect needs. Keep the next two chunk prompts pre-written in prompts/ at all times.`

### CH-01 / CH-01b (new)

**M-16 · Every number that justifies the design was computed outside the repo, and the headline three cannot be traced at all** · L1-08, L2-10, L4-11 · **2.0 h** — *this pass sharpens it considerably*
**VERIFIED:** the generating scripts are `killtest/{errata_arms,errata_score,errata_build,score_arms,structural,pairs,attacks}.py`, `probe/*.py`, `replay/*.py` — 40+ files, all inside git-ignored directories. No chunk migrates any of them.
**VERIFIED — the good news:** the **hot take is reproducible**. `killtest/errata/arms.json` (181 B) gives arm1 70/100, arm2 74/100, `fisher_p = 0.6368269514776336` — `CONTEXT.md` §11's "p = 0.64" and "net +4.0" both check out. `arm4.json` gives 27/40 = 0.675, consistent with §11's "made the arm worse overall". So migrating the hot take costs minutes, not hours, and the 11.6 MB IETF corpus need not ship.
**VERIFIED — the bad news:** `CONTEXT.md` §3's headline numbers **0.545 / 0.5855 / 0.52** trace only to `context/08-FINAL-CALL.md:111` and `:143` — *documents, not artifacts*. Grepping the workspace for `0.545` and `0.818` lands in `killtest/redesign_r1/res2_2022.json`, which is the **dead CROSSCheck/HTS project's** data (rows: "A4b BM25 top-1 score magnitude" 0.8185, "A7g frac of similar pre-T rulings with a DIFFERENT heading" 0.5459). I am **not** claiming the numbers were confused between projects. I am reporting that the headline claim's evidence is untraceable and that same-magnitude numbers from a killed project sit in the same workspace.
**VERIFIED — also untraceable:** §6's *"26/33 and 35/42 labelled items have no extractable quoted anchor … ~80% of the pool"*, the entire argument for the tool's ordering. The nearest artifact, `probe/anchor_rows.json` (n = 30), shows **16/30 = 53%** — directionally right, ~27 points off the gloss, and a third pool.
**FIX — NEW CHUNK `CH-01b` in `plan.md`, ungated, runs in parallel with CH-01:**
```
### CH-01b · Evidence migration + the human-time baseline — GATE: none
**Scope:** make every number in `CONTEXT.md` either re-derived in-repo or migrated with its generator.
1. `docs/evidence/spec-claims/` — re-derive, FROM THE FROZEN CORPUS IN-REPO, the four counts
   `CONTEXT.md` §6 depends on. Commit the script. Update `CONTEXT.md` to the re-derived values with
   their paths beside them.
2. `docs/evidence/pilot/<claim-id>/` — for numbers that cannot be re-derived, copy the specific
   generating script + input hash + stdout, with a README stating the date it ran, that it ran
   pre-repo, and which claim it supports. Label every retained figure `PILOT (pre-competition, n=NN)`.
3. `docs/evidence/hot-take/` — Path B: ship `killtest/errata/{arms,arm3,arm4,lookup_loo}.json` plus
   `errata_arms.py` / `errata_score.py`. Do NOT vendor the 11.6 MB corpus; it is fetched by URL at
   replay time. (`07-KILL-TEST.md` §6.1 already resolved IETF redistribution as CONDITIONAL on four
   conditions; Path B avoids all four.)
4. `docs/evidence/pilot/ednote-pool/` — copy `probe/ednote_hits.json` with a README recording that it
   came from the eCFR search API before that host began returning 403, retained as the
   pre-registration record of the pool projection, NOT as a reproducible artifact.
5. **Anything neither re-derivable nor migratable is DELETED from `CONTEXT.md`, not shipped bare.**
   That decision is the architect's, recorded in QUESTIONS.md — not a build session's.
6. **The human-time baseline, while it can still be blind.** Reserve 8 `(rule, section)` ids from
   CH-01's defect pool, exclude them from the golden-fixture set, work them by hand with a stopwatch,
   and commit the per-item log with UTC timestamps to `docs/evidence/human-time/` so the ordering is
   provable from git. The second (worksheet) pass runs in Phase 3 after CH-10.
7. **Compute the count-matched-sibling yield on the pool** and publish it. See M-17.
**Done when:** every numeral in `CONTEXT.md` resolves to a `docs/evidence/` path or has been deleted;
the 8 reserved ids are logged with timestamps preceding CH-02's first commit.
```
*(L5-10 — "the blind study cannot be blind at CH-09" — is closed by item 6. L3-16, the originality re-check, is closed by §7's O-8 below.)*

**M-17 · The eval-set yield after exact count-matching is unquantified by the plan and by all 94 findings** · *added by this pass* · **0.4 h**
`CONTEXT.md` §8 calls exact instruction-count matching "Non-negotiable"; `plan.md` CH-03 requires ≥ 42 pairs. **Nothing anywhere estimates what fraction of candidate positives will find a count-matched sibling.** That yield is the assumption the headline n rests on. **I attempted to measure it and could not** — see §9. **FIX:** item 7 of CH-01b above — compute and publish the yield the moment the pool exists, before the eval set is built, while there is still time to act on a bad number.

### CHECKPOINT / CH-08 / CH-09

**M-18 · The two chunks producing every quotable number are ungated** · L5-09 (+ L4-06 dup) — **2 auditors** · **0.5 h** — closed by M-8's NUMBERS-ONLY tier.
**M-19 · The video has no script and both branches need one** · L1-15 · **0.5 h** — **FIX:** write **both** beat sheets at the CHECKPOINT, timed: GREEN (problem 45 s / baseline 30 s / execution 90 s / comparison 45 s / changelog 40 s / biggest contributor 20 s / removed experiment 20 s) and AMBER-RED (same seven beats, where "the change that contributed most" becomes "the change that did not move the number, and what that tells you"). Pick one at the cutoff. Record to script; never narrate live.
**M-20 · `B0′`, the compute-matched control, appears in no chunk** · L4-08 · **0.5 h** — **VERIFIED:** `grep -c "B0′\|B0'"` → `CONTEXT.md` **1**, `plan.md` **0**, `PROCESS.md` **0**. **FIX — ADD to CH-08's scope:** `Name B0′ explicitly in the arm list and publish the per-arm token table (input tokens, output tokens, tool calls, imputed USD, per item) from the cost ledger. Dropping B0′ silently invites "your agent got 5× the compute"; if the clock forces it out, drop it by recorded ruling, not by omission.`
**M-21 · "Close with the main failure mode" has a README slot and no producer** · L1-07 · **0.75 h** — **FIX — ADD to CH-08's done-when:** `emit docs/evidence/error-taxonomy.csv — every A1 error with (item_id, gold, predicted, failure_class, which resolution_trace step went wrong). CH-09 names the largest class with its count and a worked example. That becomes the README's "main failure mode" section.`
**M-22 · The human checkpoint is claimed everywhere and fires nowhere** · L2-06 (+ L1-09 dup) — **2 auditors** · **1.0 h** — **VERIFIED:** `grep -ci "needs_human_review"` = 0. "Unresolved" is never defined, so a build session reaching CH-06 must STOP under hard rule 1. **FIX — ADD two fields to `CONTEXT.md` §5's output contract:** `"needs_human_review": true|false, "review_reason": "..."`. **AND REPLACE `CONTEXT.md` §9's last paragraph with:**
```
Unresolved cases route to a named human checkpoint with both readings and the paragraph trace.
**"Unresolved" is a trigger rule, not a word.** It fires when any of:
 (a) an instruction in the trace has `level: "none"` AND `designation_exists: true`;
 (b) the designation path and the anchor path disagree on the verdict;
 (c) the ordered-state ledger reports a designation touched twice.
CH-06's done-when: at least one eval item routes to the queue and its trajectory contains a
`human_checkpoint` record. CH-08 runs two hard-case items interactively — the agent emits the
checkpoint with both readings, the human calls it, the run resumes, the resolution is recorded.
**Measure the queue while you are there:** its catch rate (fraction of A1's wrong verdicts routed
rather than shipped confident) and its interruption cost (correct verdicts also stopped). If it does
not pay, it becomes removed experiment #3 with its number.
```
**M-23 · The hot take's evidence and its "what I'd build next"** · L2-09, L4-10 · **0.5 h** *(revised down from 1.65 h — see M-16: the artifacts are 181 B, not a corpus)* — Path B into CH-01b; two authored first-person sentences answering *"how would it change what you build next?"* into CH-09's done-when.
**M-24 · Human time and cost per task are measured for one arm of a two-arm row** · L4-09 (+ L1-18 dup) — **2 auditors** · **0.6 h** — **VERIFIED:** `grep -ci "cost per task"` = 0 across `plan.md`, `PROCESS.md`, `CONTEXT.md`. **FIX:** CH-01b item 6 for the baseline pass; a second worksheet pass in Phase 3 after CH-10 on the **same 8 items**; publish both with the caveat verbatim beside the number, not in a footnote — *the timer is the author, n = 8, the second pass benefits from familiarity, treat the delta as an upper bound.*

### CH-06 / CH-10 / CH-11 / CH-12 / CH-14

**M-25 · The solution has no entry point and is never run on an input the user would bring** · L1-12 (+ L4-04 dup) — **2 auditors** · **1.5 h** — **VERIFIED:** zero hits for `cli|entry point|command|python -m` across `plan.md` and `CONTEXT.md`. This also breaks deliverable 2, which requires *"the exact commands for the solution, the baseline and the evaluation"*. **FIX — ADD to `CONTEXT.md` as a new §5b:**
```
### 5b. The input contract and the entry point
`python -m src.check --rule <FR-citation> --title <N> --part <N> [--as-of YYYY-MM-DD]`
Emits the §5 JSON to stdout and writes the CH-10 worksheet beside it. `--offline` replays a frozen
item and needs no network and no key; that is the Tier-1 path a judge runs.
```
**AND ADD to CH-10's done-when:** `run the pipeline once on a rule that is NOT in the eval set, commit the resulting worksheet as docs/demo/, and make it the artifact the video walks through.`
**M-26 · The clean-clone rehearsal is same-machine, same-OS** · L3-13 (+ L4-17, L5-15 dup) — **3 auditors** · **0.6 h** — **FIX — REPLACE CH-14 step 1 with:** `Fresh venv from a pinned requirements.txt (Python 3.12.2 is the build interpreter — state it), network off, manifest verify, Tier-1 replay, following REPRODUCE.md line by line. Run it once more under WSL or python:3.12-slim, because "a clean environment" is not "a second directory on the same machine".`
**M-27 · Raw JSONL is not "easy to follow"** · L1-10 · **1.5 h** — **FIX:** `tools/render_trajectory.py` → one markdown page per trajectory, agent instructions at the top, then a step table (action → tool response → the feedback that shaped the next step), retries and human checkpoints called out, final result at the bottom. Built at CH-00, run at CH-12.
**M-28 · Rule 05's strongest answer is sitting unused** · L2-07 · **0.5 h** — **FIX — NEW FILE `SAFETY.md`**, ~250 words, linked from the README's first screen, making four points the design already supports and never states: (1) the system performs no action — hard rule 8 makes scorer and resolver pure, the output is a worksheet, never a filing; (2) **every gold label in the eval set was authored by Office of the Federal Register editors — the ground truth *is* a qualified human reviewer's judgement**, which is the sharpest rule-05 answer available; (3) the checkpoint queue routes ambiguous items to a named drafter before use, per M-22's trigger rule; (4) plainly: *"I am not a regulations drafter. This tool is validated against OFR-authored ground truth, not against my own legal judgement, and a qualified drafter reviews every output before it informs a filing."*
**M-29 · Ground rule 03 is cleared for the corpus and nothing else, and the repo ships a self-reported service-terms breach** · L2-17 (+ L4-05, L5-20 dup) — **3 auditors, the highest convergence in the audit** · **1.5 h** — see §3's anti-slop item below; the licence half is: add `THIRD-PARTY.md` (every dependency and data source with licence and link, including the model provider and the basis on which its outputs may be assigned) and a `LICENSE` file — there is none. **And rewrite `CONTEXT.md` §8's constraint note factually, without the admission of fault**, adding the compliance half, which this pass has now evidenced (§7, O-6).
**M-30 · The anti-slop clause has no fix and `PROCESS.md` §0 forbids one** · L2-17 / L4-05 / L5-20 cluster — **3 auditors** · **1.5 h** — **VERIFIED:** `PROCESS.md:22` *"no artifact is written twice… If something has to be reconstructed at the end, the process was wrong."* `grep -ci` for `voice`, `hand-writ`, `read aloud`, `slop`, `AI generated` = **0** across all four architect files. One fifth of the total score is partly a "does this read as AI-generated?" check.
**FIX (a) — AMEND `PROCESS.md` §0:** `**No EVIDENCE artifact is written twice.** Four prose artifacts are explicit exceptions and are rewritten by hand before shipping: the README's first screen, the CHANGELOG's Decision/Learning column, the video script, and the HackerEarth Description.`
**FIX (b) — NEW CHUNK `CH-11b · VOICE PASS`**, operator only, no session, 45–60 min, scheduled **after CH-11 and before CH-13B** so the script inherits the voice: *read aloud; delete every sentence that could appear in any other submission; no em-dash-per-sentence cadence; none of delve / leverage / robust / seamless / comprehensive; no "It's not X, it's Y"; no three-item lists where two or four is truer. Add two or three sentences only the person who did this work could write — the 0.46-completeness bug that poisoned the pilot, the hour ecfr.gov started 403ing, the experiment that got killed. Sign it.*
**FIX (c) — separate the machine records rather than rewriting them:** move `PROCESS.md`, `plan.md`, `CLAUDE.md`, `STATUS.md`, `PROGRESS.md`, `QUESTIONS.md` into `docs/process/`; leave `README.md`, `REPRODUCE.md`, `CHANGELOG.md`, `AI-USE.md`, `GOOD.md`, `PROVENANCE.md`, `SAFETY.md`, `SUBMISSION.md`, `LICENSE` at root. **VERIFIED the need:** 5 machine-authored `.md` files sit at root today and CH-00…CH-14 add 9–12 more, so a judge opening the repo meets 14–17 root markdown files. One authored README line converts the liability into an asset: *"`docs/process/` holds the working records — the spec, the chunk plan, the session journal, the rulings. They are agent-authored and unedited on purpose; they are the audit trail, not the pitch."*

### Found by the adversarial stage — items neither the auditor nor the first verifier raised

**M-31 · This document, and every `context/1*` file after it, falls outside the tracked-set spec** · **0.1 h**
**VERIFIED:** `prompts/CH-00.md:73`'s "What SHOULD be tracked" enumerates `context/00-MASTER-CONTEXT.md`, `context/0[3-9]*.md` and the `*-raw.json` outputs. `ls context/0[3-9]*.md` matches seven files and **does not match `context/10-REMEDIATION.md`** — the glob requires a leading `0`. So the entire verification-and-remediation record, including this file, is outside the spec and would silently never ship. Every future `context/1N-*.md` inherits the bug.
**FIX — REPLACE that clause with:** `context/00-MASTER-CONTEXT.md`, `context/[0-9][0-9]-*.md` **except** `context/01-PROBLEM-PDF.md` and `context/02-ABOUT-ME.md`, and the `context/*-raw.json` agent outputs.

**M-32 · The archive is built before the index it is supposed to contain** · **0.2 h**
**VERIFIED:** `plan.md` CH-14 step **3** builds `submission-<sha>.zip` with `git archive HEAD`; step **5** writes `SUBMISSION.md`. `git archive HEAD` exports committed content, so **the completeness index the whole fix exists for cannot be inside the archive it indexes** — and a commit-then-rebuild changes the SHA the zip is named after.
**FIX — REORDER CH-14 to: (1) rehearsal · (2) secret scan · (3) write `SUBMISSION.md` and commit it · (4) build the zip from that commit · (5) extract and replay from the extraction · (6) record the zip's SHA-256 in `SUBMISSION.md`'s footer *and* in the README, noting that the footer hash necessarily post-dates the archive.** Same for the video URL: CH-13's done-when requires the URL in `README.md` and `SUBMISSION.md`, both of which must therefore be written after upload — state the dependency rather than leaving it circular (m-20).

**M-33 · `CONTEXT.md` declares three normalisation levels and emits two different names for them — in the precision-critical field** · **0.15 h**
**VERIFIED:** `CONTEXT.md:25` (§1, the precision-critical-domain clause) declares the three levels as `exact` / `whitespace-collapsed` / `alphanumeric-only`. `CONTEXT.md:79` (§5, the output contract the scorer and the worksheet both read) emits `"level": "exact|whitespace|alphanumeric|none"`. **Two of the three names differ**, in the one field §1 says must never be silently altered, in the file declared LAW. CH-05 builds the resolver against §5; a reviewer reimplementing from §1 produces different strings and the diff fails for the wrong reason.
**FIX:** pick the §5 enum (`exact|whitespace|alphanumeric|none` — it also carries the `none` case §1 omits) and make §1 quote it verbatim, or vice versa. Either is fine; shipping both is not.

**M-34 · `PROVENANCE.md`'s own stated proof method falsifies one of its claims** · **0.1 h — but it is the sharpest form of D-4**
**VERIFIED**, three lines of the same shipping file:
- `PROVENANCE.md:5` — *"Every claim below is checkable against file modification times, git history, and the public URLs given."* An explicit invitation to check.
- `PROVENANCE.md:85`, under "What is deliberately excluded from this repository" — *"**The operator's personal data** — résumé, contact details, portfolio dumps. Ground rule 08."*
- `PROVENANCE.md:90` — *"`.gitignore` is the enforcement, and `git ls-files` is the proof."*

**`git ls-files` will list `context/09-COMPLIANCE-AUDIT.md` and `context/09b-audit-raw.json`, and both carry the operator's phone number** — a contact detail, by name, in the category the file says is excluded. So the file's own nominated proof disproves its own claim, in the one artifact whose entire purpose is checkable honesty, on a submission whose pitch is integrity. A validator who takes the invitation at line 5 finds this in one command.
**FIX:** D-4 closes it at source — once the sweep runs, the claim becomes true and the invitation becomes an asset. **Order matters: run D-4's redaction before the first commit, or PROVENANCE.md ships a falsehood into git history.** No wording change is needed; the sentence is correct as an intention and wrong only as a statement of present fact.

**M-35 · The harvest scripts impersonate a browser, which is the likely proximate cause of the 403 and a live ground-rule-03 item** · **0.3 h**
**VERIFIED:** nine `killtest/*.py` scripts send `User-Agent: Mozilla/5.0` — `harvest.py:9`, `probe.py:6`, `fetch_priors.py:13`, `fetch_texts.py:31`, `instr_arm.py:44`, `errata_arms.py:49`, `errata_build.py:15`, `tri_arm3.py:16`, `verify_bp.py:8`. That is a browser-impersonating UA, not a descriptive research UA with a contact address. `CONTEXT.md` §8 reports the 403 as *"Sustained automated traffic got us blocked"* and offers no mechanism; the mechanism is probably this, and it is the half a reader would want.
**FIX:** fold into M-29's §8 rewrite. State the mechanism factually and state the correction: `refetch.py` and every harvest script send a descriptive User-Agent naming the project and a contact address, sleep between requests, back off, and honour 429/503. Then the govinfo evidence in O-6 lands as discipline rather than as assertion. **Do not ship the `Mozilla/5.0` pattern in any committed script.**

---

## 4. MINOR and POLISH

One line each, with its fix. All confirmed unless marked.

| # | Finding | Fix | h |
|---|---|---|---|
| m-1 | L1-13 · "Versions pinned" will be read as `requirements.txt` only | REPRODUCE.md states the interpreter (**Python 3.12.2**, verified as the build interpreter), the OS it was built on, the model id `claude-sonnet-5`, and approximate runtime and cost per tier | 0.25 |
| m-2 | L1-14 · the brief says "the baseline" singular; there are four non-solution arms | REPRODUCE.md names one **headline baseline** (B0-agent) for the three-row table and lists the other three beneath as supporting arms | 0.5 |
| m-3 | L1-16 (+L2-14 dup, 2 auditors) · CH-11's README order omits four things `CONTEXT.md` mandates | add to the card: §1 non-goals ("state these in the README"), §2 the generalisation ("lead the README with this"), §12 prior art ("cite on the first screen"), and a `PROVENANCE.md` link | 0.4 |
| m-4 | L1-17 · changelog has no rows for B0′ or the two removals | closed by M-4's table | — |
| m-5 | L2-15 · the worksheet carries no disclaimer on its own face | header band: *"Draft review aid — predicted OFR execution outcomes, not a determination. Not legal advice and not a filing. Every row is a prediction to be checked against the section text beside it; rows flagged for review are the ones the system could not resolve, not the only ones worth reading."* Footer: run id, model, corpus manifest hash, as-of date, queue count. **Note the correction:** an earlier draft of this band said rows "require sign-off by a qualified regulations drafter" — but `CONTEXT.md:24` names the intended user as *"a regulations drafter or Office of the Federal Register liaison"*, so that wording tells the reader to get sign-off from herself. The disclaimer must disclaim the *tool's* authority, not delegate to the person already holding it | 0.25 |
| m-6 | L2-16 · FR XML carries `FOR FURTHER INFORMATION CONTACT` blocks naming agency staff | two sentences in `data/README.md` (**create it — it does not exist**): published under 17 U.S.C. §105; contains agency contact details as published; no data inferred, enriched, joined or republished outside its original document context; no individual is a subject of analysis | 0.25 |
| m-7 | L2-18 · registration is not recorded in the repo | record `Q0 CLOSED` in QUESTIONS.md with the timestamp and citation from §7 O-1 | 0.1 |
| m-8 | L3-18 · the revision rule is ambiguous once a draft exists | one line in CH-15: *every submission event ships a complete four-field package; never replace a complete submission with a partial revision — "only the latest **complete** submission is evaluated" admits a reading where a partial revision destroys a complete one* | 0.1 |
| m-9 | L4-07 · "verification" is named in the 30-point row and is not a capability here | **do not add a fourth capability** — `CONTEXT.md` §6's cap is itself a scoring asset. Name the checkpoint queue as a *verification surface* in the README and measure its catch rate and interruption cost (M-22). If it does not pay it becomes removed experiment #3 with its number | 0.5 |
| m-10 | L4-13 · the two artifacts a judge meets first are ungated with no usability read | one session, not the author, opens the worksheet cold and reports what it could not understand in five minutes | 0.5 |
| m-11 | L4-14 · 14–17 machine-authored markdown files at repo root | closed by M-30(c) | — |
| m-12 | L4-15 · nobody produces the brief's own three-row results table | put it in the README immediately after the headline claim (Primary outcome / Human time per task / Cost per task × Simple baseline / Agent solution / Change), full arm matrix beneath, and on a single video frame | 0.25 |
| m-13 | L4-16 · the hard case is named and nobody writes what it revealed | `docs/evidence/hard-case/` for 12 CFR 702.504→702.304: each arm's full `resolution_trace` side by side, which arms got it right, and what the failure taught — that partial-read agents rule correctly for the wrong reason. Make it the case the video walks through | 0.5 |
| m-14 | L4-19 · no statement of which capabilities were deliberately not used | README table, four rows: orchestration (rejected — single-document read, no sub-goals), RAG over current CFR text (rejected **and measured** — removed experiment #1, leaks the label), verification (m-9), plus anything an ablation removed. Restraint only scores when it is visible | 0.5 |
| m-15 | L5-08 · architect state lives in chat | closed by M-15 | — |
| m-16 | L5-16 · no minimum-viable-submission definition | closed by M-8 | — |
| m-17 | *added* · `CONTEXT.md`'s "13 and 15 independent agents" does not reconcile with the shipped evidence, and the **largest swarm ships no trace at all** | **VERIFIED:** `03b-review-raw.json` = 5 critiques + 2 alternatives + 6 scores = **13**; `08b-audit-raw.json` = 5 audits + 2 rivals + 5 kills = **12**; `PROVENANCE.md:43` separately attributes "15 agents" to `context/03`, whose own dump counts 13. Two shipping files, one countable dump, three numbers. **And:** `context/06-DIVERGENT-RESEARCH.md:10` records **"57 agents, ~1,845 tool calls, ~4.9M subagent tokens"** — larger than every other swarm combined — while **no `06b-*.json` and no `07b-*.json` exist**, so the two biggest bodies of design-agent work ship their prose conclusions and no trace. **FIX:** recount from the dumps and state each count with its file path. The brief asks for *representative* trajectories, so shipping four swarms of six is defensible — **but only if the scoping statement says which four and why**, rather than implying full coverage. Anything not recountable gets deleted, not shipped bare | 0.3 |
| m-18 | *added* · `CONTEXT.md` §8's "the eCFR search API reported 92 — it undercounts by ~2.3×" | **VERIFIED:** `probe/ednote_hits.json` **is** an eCFR search-API dump and yields **474 defect-note hits across 145 distinct (title, section) pairs in 30 titles** — inside §8's own 130–210 projection, not 2.3× below it. The query behind "92" is recorded nowhere. **FIX:** at CH-01 publish the govinfo structural count beside 145 and record the query behind 92, or delete the sentence. Do not ship a comparison whose baseline nobody can reproduce | 0.2 |
| p-1 | L4-18 · the user is asserted, never evidenced | quote NARA's Document Drafting Handbook verbatim on the first screen (*"An amendment that was stated erroneously or that is clearly inconsistent with the codification structure … is cited in an editorial note"*), quote one real NARA note, and give the **rate** — see §7 O-7, which computes it: **~44 defect notes per year** | 0.4 |
| p-2 | *added* · `cfpb/regulations-parser` is archived and deprecated, unmentioned | **VERIFIED:** the repo is titled "(DEPRECATED) Parser for U.S. federal regulations…" and was archived 2018-09-17. Say so in the citation | 0.1 |
| m-19 | *added by the adversarial stage* · the 25 MB guard is calibrated above the largest piece of host copyright it nominally guards | **VERIFIED:** `context/media/challenge-video.mp4` is **19,612,824 B** — micro1's brand film, comfortably under the `no tracked file over 25 MB` assertion at `prompts/CH-00.md:69`. It is excluded by `context/media/` so this is moot today, but the assertion would not have caught it. Lower the threshold to **5 MB** and list the deliberate exceptions; nothing this project legitimately tracks is larger | 0.1 |
| m-20 | *added by the adversarial stage* · CH-13's done-when is circular | **VERIFIED:** `plan.md:94` requires the URL be recorded in `README.md`, `SUBMISSION.md` and the form; `plan.md:95` requires upload by T−8h, before either file exists. State the dependency: upload at T−8h, record the URL into all three surfaces at CH-11/CH-14, and make *that* the done-when — see M-32 | 0.1 |
| m-21 | *added by the adversarial stage* · the repository URL is never recorded or checked for correctness anywhere | **VERIFIED:** `plan.md:94` routes the *video* URL into three surfaces; there is no equivalent clause for the repo URL, which is the one link in the Description and the only route a judge has to the code. Add it to `SUBMISSION.md`, the README and CH-15's done-when, and open it from the anonymous clone in D-3 | 0.1 |

---

## 5. FALSE ALARMS — with the evidence that killed each

**Only two of the 94 survive as outright false.** The list is short and I am not going to pad it: 87 of 88 findings quoted their requirement accurately, and where the auditors erred they erred about the *state of the artifact*, not about the rules. Several findings that looked false at the verification stage were **overturned back to real** by the adversarial pass, and I record those below too, including one where my own reasoning was the thing that got overturned.

**L2-16 · "The frozen corpus vendors whole FR XML documents carrying `FOR FURTHER INFORMATION CONTACT` blocks."**
**KILLED on its factual predicate.** The requirement quote is verbatim (`01-PROBLEM-PDF.md:195`), but the premise is not true of the plan as it stands: nothing vendors whole FR documents. The freeze is extract-then-freeze once D-5 lands, and even before it, the corpus is section blocks and AMDPAR blocks. The privacy paragraph it asks for is still worth two sentences (m-6) — but as courtesy, not as remediation of a defect.

**L4-20 · "The hot take never answers 'how would it change what you build next?'"**
**KILLED, and it survived four separate attacks.** `CONTEXT.md:213` reads *"**The transferable rule:** before building retrieval into an adjudication pipeline, measure the baseline's per-class recall…"* — that is the answer, already in the file. What is missing is only that it reaches the README in the first person, which is p-1's half-sentence, not a finding.

### Findings that looked false and were overturned back to real

**L2-08** — the verifier killed it because `grep -ci "gemini"` = 0 and Q1 is answered. **Both true, and the finding still stands** on a narrower ground: rule 03 clearance covers the corpus and nothing else. Now folded into M-29 / M-35 with the govinfo evidence in O-6.

**L5-13 — and here the correction is to my own earlier reasoning.** The verifier dismissed it, and I repeated that dismissal in an earlier draft of this section: I wrote that nothing says the support window *closes* at 2026-08-30 23:59 UTC, so the audit's urgency framing was unsupported. **The challenger showed that dismissal rests on an inference too** — that the timeline table has uniform event-time semantics, so row 4's timestamp marks when the checkpoint *happens*. Neither reading is stated. **The honest position is that `00-MASTER-CONTEXT.md:215` — `| 4 | Final-day checkpoint | Sun, Aug 30 · 23:59 | Submission reminder, known issues and support escalation window |` — is ambiguous, and both the audit and I over-read it in opposite directions.** The action is unchanged and cheap either way: read the challenge page and any organiser mail before deadline day, and email `yeison@micro1.ai` then rather than Monday if anything is anomalous. Do not build a schedule around either reading.

**L3-01 and L3-17** — both reclassified as duplicates rather than false. The evidence that killed L3-01 as *stated* is still the most valuable single correction in this pass, and it stands: **VERIFIED**, session transcript `9acf056f-….jsonl` lines 436–437, timestamps `2026-08-29T03:51:27.013Z` and `2026-08-29T03:53:39.043Z` — the operator was asked *"Have you registered on HackerEarth yet? Registration closes in 20 hours"* and answered **"Yes, already registered"**, roughly 20 hours before the close. Corroborating: `plan.md:109` records the form's exact four fields *"(verified from inside it, 2026-08-30)"*, unreadable from outside a registered session. Three auditors rated registration a disqualifying unknown; **it is not unknown, it is unrecorded** — which is m-7, ten minutes of work.

**And two the challengers moved the other way:** `L3-16` (the originality re-check) and `L3-18` (the revision-rule ambiguity) both went CONFIRMED → ALREADY-FIXED. For L3-16 the reason is this document: §7 O-8 ran the check, so what remains is recording it.

**Also confirmed strong and not to be touched** (raised by no one, and correctly): the two-tier reproduction design; `.gitattributes = * -text` as the first file in the first commit; `GOOD.md` pre-registered and timestamped before any model arm with hard rule 5 forbidding movement; exact instruction-count-matched negatives asserted by a test under a FULL gate; the B-script arm reported with its permutation null; the T−12h cutoff and its stated rationale; the iteration card committing a numeric prediction before each build; the corpus licence analysis including the incorporation-by-reference check; hard rule 14; and the honesty regime in `PROCESS.md` §9. **Roughly sixty points of method are already well defended.** Everything above is about not losing them at the gate.

---

## 6. Adequacy of the eight already-fixed items

| # | Fix | Verdict |
|---|---|---|
| 1 | `.gitignore` before `git init`, with `<60` tracked files and nothing over 25 MB | **PARTIAL** |
| 2 | Build-session trajectory export | **PARTIAL — and currently inert** |
| 3 | `PROVENANCE.md` | **PARTIAL** |
| 4 | CH-15 Submit, hard start T−3h, draft-early | **PARTIAL** |
| 5 | CH-13 video: unlisted YouTube, signed-out test, sub-5:00 | **SUFFICIENT on content, PARTIAL on schedule** |
| 6 | CH-14: `git archive` zip < 50 MB, Tier-1 replay from the extraction, `SUBMISSION.md` | **SUFFICIENT** |
| 7 | Submission form constraints as Q2 | **PARTIAL — 3 of 5 consequences landed** |
| 8 | Gate structure: three full reviews + two-strike escalation | **PARTIAL** |

**1 — `.gitignore`. PARTIAL.** The size and licence halves are **fully sufficient and verified**: applying the ignore list exactly as written yields **20 tracked files / 1.56 MB**, largest file 406,206 B, so both assertions pass with enormous margin, and every item the auditors named — `d.pdf`, `context/media|images|slices|screenshots|raw/`, `context/02-ABOUT-ME.md`, `context/me/` (which holds the "all rights reserved" third-party README), `aec/ bip/ killtest/ probe/ replay/ scraper/` — is excluded. Three things remain: the **PII residue** (D-4), the **name-specific patterns** that will not survive CH-01's download or CH-13's MP4 (D-5, M-6), and the **research prompts deleted while their outputs ship** (M-5).

**2 — Trajectory export. PARTIAL, and as things stand it will not run.** `prompts/CH-00.md` §1b is a good specification and `tools/export_session.py` is the right tool. But **VERIFIED:** `tools/` does not exist yet (expected — CH-00 builds it), **and `CLAUDE.md`'s end-of-session duties contain five items, none of which is the export.** The duty exists only as an instruction telling the CH-00 session to add it to a file that CH-00's own safety rider declares read-only, and the export tool is outside CH-00's scope fence. So the fix is specified, blocked, and silently inert from CH-01 onward. D-1 repairs all of it.

Three further residuals. **(a)** The exporter copies *the current* session, so the four transcripts already on disk (~23 MB, including the one carrying the registration evidence in §5) are not covered — CH-00 should copy them explicitly. **(b)** The redaction spec is three items (`.env` values, API keys, the phone number) and is far too narrow: exporting raw would re-import 13 MB of git-ignored micro1 page assets and the operator's email at scale — **O-21 measures it and gives the corrected spec.** **(c)** The instructions that shaped the research agents are git-ignored on a stated reason that is false (M-5).

**3 — `PROVENANCE.md`. PARTIAL.** The file is good, and I took its line-5 invitation seriously and checked its falsifiable claims. **They hold, with one exception.** **VERIFIED** `scraper/` is excluded by `.gitignore`. **VERIFIED** the "143 candidates from 18 angles" claim matches `context/06-DIVERGENT-RESEARCH.md:15-16` exactly. **VERIFIED via the GitHub API:** `acumen` is public and was created **2026-07-25**, so *"public since July 2026"* is true; `nistula-assistance-` is public and was last pushed **2026-08-18T15:01:26Z**, so *"last pushed 2026-08-18, ten days before kickoff"* is true to the day. **The one exception is M-34**, and it is not a wording problem — it is D-4's leak making a true-in-intent sentence false-in-fact. What is missing is that **nothing points at it**: `grep -ci "provenance"` = **0** in `plan.md`, `PROCESS.md` and `CLAUDE.md`; it has no Files-table row, no chunk owner, and no slot in CH-11's README order. Also missing: the commit-splitting instruction the audit's D2 asked for (A `.gitattributes` → B `PROVENANCE.md` → C pre-existing import → D+ build), and the `ls -la --time-style=full-iso` mtime capture into `docs/evidence/provenance/` that would let the claim be checked rather than believed. And its agent counts do not reconcile (m-17). **Fixes: M-3's Files row, m-3's README slot, and the commit split.**

**4 — CH-15. PARTIAL.** The card is genuinely good: the four fields are right, the Description is correctly identified as the first thing a judge reads, T−3h/T−1h are stated. Three gaps. (a) **The draft is aspirational, not scheduled** — *"Save a draft as soon as anything complete-but-imperfect exists"* sits inside a chunk whose hard start is T−3h, so the insurance the whole audit recommended is not on the clock; M-1's wall-clock trigger at 12:00 UTC fixes it. (b) **The repo-public flip is absent** — D-3. (c) **`PROCESS.md` does not know CH-15 exists** — `grep -c "CH-15" PROCESS.md` = 0; M-1 fixes it.

**5 — CH-13 video. SUFFICIENT on content, PARTIAL on schedule.** The card names the host, the visibility, signed-out playback with audio, sub-5:00 (not 5:0x), and the three places the URL is recorded — that is item-for-item what was asked, and CH-15 independently re-checks playback, so it is double-anchored. But **the schedule is arithmetically impossible as ordered:** Phase 3 opens at T−12h (06:00 UTC) and `plan.md:95` requires upload by T−8h (10:00 UTC), while CH-13 sits fourth of six behind CH-10 + CH-11 + CH-12, estimated at 2.0 + 2.5 + 1.5 = **6.0 h** for a 4-hour window. And there is still no script (M-19) and no committed-MP4 size rule (M-6). **Fix: the Phase 3 reordering in §8.**

**6 — CH-14. SUFFICIENT.** All five steps are present and correct, and step 4 — replaying from the *extraction* rather than the clone — is the right instinct and better than most entrants will manage. Two upgrades, neither a defect in the fix: the secret scan needs a tool and a pass criterion (M-13), and "clean clone" is not "clean environment" (M-26). One precision note: the card says `git archive` *"respects `.gitignore`"*. It does not, strictly — it exports the tracked tree, and ignored files are absent because they are untracked, not because the ignore file is consulted. Harmless today; worth stating exactly in a project whose stated value is exactness.

**7 — Q2 submission-form constraints. PARTIAL: three of five consequences landed.** C3 (unlisted YouTube, uploaded early) reached CH-13 ✓. C4 (the Description) reached CH-15's field table ✓. C5 (draft early) reached CH-15 as prose but not as a scheduled event ⚠. **C1 (extract-then-freeze, never download-then-freeze) did not reach CH-01 or CH-03** — `grep -ci "extract-then-freeze" plan.md` = **0** — and it is the difference between a 1.4 MB corpus and a 231 MB one (D-5). **C2 (curated trajectory set with a written selection rule) did not reach CH-12** — `grep -ci "selection rule" plan.md` = **0** (D-6). The observation the consolidated audit opened with — *"the knowledge exists; the execution is unowned"* — is still true for exactly these two.

**8 — Gate structure. PARTIAL.** Three separate full reviews for CH-02/03/04 is the right call and the serial-chain rationale in `plan.md`'s header is correct. But the strike limit lives **only** in `plan.md` — `grep -ci "strike" PROCESS.md` = **0**, and `PROCESS.md` §2's fix loop is still unbounded — so the two authority files disagree about whether the loop terminates. And "escalated to the architect" names no outcome: escalation is not a decision. M-8 supplies both the location and the two outcomes (accept with findings in LIMITATIONS, or invoke the pre-registered fallback).

---

## 7. What nobody audited

Requirements and facts in the brief, the master context, or the corpus itself that appear in neither the plan nor the 94 findings. Ordered by what they change.

**O-1 · Registration is evidenced on disk, and the evidence is volatile.**
Covered in §5. The point for *this* section: the proof lives in a Claude Code session transcript that nothing copies and that Claude Code prunes. Capturing it is item 2 of §6 and D-1. **VERIFIED**, timestamps and line numbers given above.

**O-2 · The label element is nested inside the input element.** — D-2. The single most consequential thing nobody looked at, because looking required parsing the corpus rather than reading the plan.

**O-3 · `prompts/CH-00.md` cannot execute as written.** — D-1. Five contradictions; the auditors found the *symptoms* (L3-07, L4-03 on the trajectory duty) and none found that the prompt forbids its own instructions.

**O-4 · The go/no-go n was halved and three pre-registered fallbacks were dropped in transcription.** — M-7. `08-FINAL-CALL.md` §5 specifies GATE-3 at **n ≥ 200**; `plan.md` says **n ≥ 84**. GATE-1's pool fallback and the RED path's full specification exist verbatim in the source document and appear nowhere now. The auditors correctly found that fallbacks were *missing*; nobody found that they had been *written and lost*, which changes the fix from invention to restoration.

**O-5 · "Tests" is a named submission-validity item and appears in no ledger.** — M-3. *"…must include the required repository, archive, **tests**, README, agent-use evidence, and demo video."* `grep -c "tests/" plan.md` = **0**.

**O-6 · The ground-rule-03 clearance the plan needs is available, positive, and I fetched it.**
The audit asks for a compliance half beside the 403 disclosure and assumes it must be asserted. It can be cited. **VERIFIED:** `https://www.govinfo.gov/robots.txt` (4,695 B, 106 lines) contains **no `Disallow` for `/bulkdata/`**, **no `Crawl-delay` directive at all**, and **publishes sitemaps for exactly the three paths this project harvests**: `sitemap/bulkdata/CFR/sitemapindex.xml`, `.../ECFR/...`, `.../FR/...`. **VERIFIED** every endpoint `CONTEXT.md` §8 depends on returns 200: `/bulkdata/ECFR`, `/bulkdata/CFR`, `/bulkdata/FR`, `/bulkdata/ECFR/title-12`, `/bulkdata/CFR/2024`, `/bulkdata/FR/2024`; `www.ecfr.gov` and `www.federalregister.gov` both **403**. The host actively advertises the three bulk paths for crawling and sets no rate directive, which makes the polite-rate policy a self-imposed courtesy worth *saying* rather than implying. **FIX:** commit the fetched file as `docs/evidence/corpus-access/govinfo-robots.txt` with its timestamp, and rewrite `CONTEXT.md` §8's constraint note factually — both hosts return 403 to this environment, neither is used, govinfo bulk data is the sole channel, the two blocked hosts were **abandoned rather than circumvented**, `refetch.py` sends a descriptive User-Agent with a contact address and honours 429/503, and **Tier 1 needs no network at all, so a judge is never exposed to it.** Handled this way the incident is evidence of discipline.

**O-7 · The defect rate the plan needs for its 15-point row — computed.**
**VERIFIED** from `probe/ednote_hits.json`: 474 codification-defect notes, all carrying the mechanism phrase *"inaccurate amendatory instruction"*, distributed by year as `2016:31 · 2017:93 · 2018:35 · 2019:37 · 2020:44 · 2021:34 · 2022:54 · 2023:57 · 2024:46 · 2025:19 · 2026:24` → **~44 per year across the harvested titles**, over 30 titles and 145 distinct `(title, section)` pairs. Each one is an instruction that did not codify, and therefore a correcting document in a later Federal Register cycle. That is the sentence the README's first screen is missing. **Caveats to ship beside it, not smoothed away:** `starts_on` is the note's validity date, not the defective rule's publication date; 2026 is incomplete; 2025's 19 is unexplained against the 2022–24 run of 54/57/46 and may be indexing lag, so **do not draw a trend line**; 2017's 93 is roughly double every neighbour and should be examined before it is quoted; the denominator is harvested titles, not all 50; and the source is the now-403 eCFR search API, so CH-01 must re-derive from govinfo and publish both.

**O-8 · The originality re-check nobody ran — I ran it, and it is clean.**
L3-16 correctly notes the check was run against the dead idea and never re-run. Queries run this pass: *"predict whether Federal Register amendatory instruction will fail to codify CFR agent"* → no prior system, dataset or paper; results were NARA/OFR primary sources only. *"NARA editorial note 'could not be incorporated' CFR codification defect dataset benchmark"* → no dataset, no benchmark. The full NLLP@ACL 2025 volume (all 32 papers read) → **nothing on the CFR or the Federal Register.** Operator name + the concepts → nothing. **CONCLUSION: clean.** The remaining work is one dated paragraph in `PROVENANCE.md` recording these four queries and their outcomes, so the claim ships with its method.

**O-9 · The prior-art citation on the README's first screen mis-describes the paper it cites.**
`CONTEXT.md:221` says *"**Prior et al., NLLP@ACL 2025** — amendatory instruction execution as a task."* **VERIFIED** by reading the full ACL Anthology index for volume `2025.nllp-1`: the only paper with an author surnamed Prior is **Max Prior, Adrian Hof, Niklas Wais, Matthias Grabmair, "Risks and Limits of Automatic Consolidation of Statutes"** — statute *consolidation* in **German** law. No paper in that volume concerns the CFR, the Federal Register, or US regulatory codification. The citation is real; its description is wrong. **The differentiation gets stronger once corrected** — consolidation genuinely is a different axis from predicting non-execution and localising it. `CONTEXT.md` §12's own words are *"Not citing known prior art on a submission staked on integrity is an unforced error and is one search away for a judge."* The citation was one search away. **FIX:** correct title, authors, venue and subject, and restate the differentiation against what the paper actually does. *(ATLAS, arXiv 2509.18400, **checks out**: "ATLAS: Benchmarking and Adapting LLMs for Global Trade via Harmonized Tariff Code Classification", Pritish Yuvraj and Siva Devarakonda, HTS classification from CROSS — `CONTEXT.md` describes it accurately.)*

**O-10 · CH-02's `≥ 0.90` threshold is sound, and the 0.46 that justifies its gate is now explained.**
Nobody checked whether the project's own highest-risk threshold is achievable. **VERIFIED** on `fr20240103.xml`: 42 `<REGTEXT>` blocks, 64 `<AMDPAR>` blocks, and **only 27 of 64 (42%) name a section explicitly**. The other 58% are lettered sub-instructions inheriting their section — verbatim: `"2. The FAA amends § 39.13 by:"` / `"a. Removing Airworthiness Directive (AD) 2020-24-12…"` / `"b. Adding the following new AD:"`. An extractor requiring an explicit section reference attributes **42%**, within noise of the **0.46** `plan.md:30` reports from the poisoned pilot. **So the historical bug is explained, carry-forward is exactly the right fix, and ≥ 0.90 is realistic rather than aspirational.** **Free golden fixture, hand-computable before any code, satisfying hard rule 4 at zero cost:** FR 2024-01-03, part 39, § 39.13 — instruction 2 names the section, sub-instructions a and b inherit it; expected attribution **3/3 to § 39.13**, naive extractor scores **1/3**. That fixture discriminates the exact bug.

**O-11 · Nothing records which model ran the ~90 design-phase agents whose outputs ship.**
**VERIFIED:** `PROVENANCE.md` names only `claude-sonnet-5` (eval arms) and Claude Code (the build). Scanning `context/{03b,04b,05b,08b,09b}-raw.json` finds model names only as *subject matter*; `08b` and `09b` carry no model token at all. `prompts/CH-00.md:108` seeds `AI-USE.md` "with this session" only, and the design swarms pre-date CH-00. `CLAUDE.md` rule 13 requires *"Every model, tool and agent"*. **FIX:** the architect records, from memory of the sessions that ran them, the model and orchestration for each of the four design swarms into `AI-USE.md`'s pre-build section — **before that memory is gone.**

**O-13 · A RED checkpoint produces an entry with no advanced solution — and "valid" is the word the rules use.** — the validity constraint written into M-7. This is the highest-consequence thing nobody looked at, because finding it required reading the *master context's Theme section* rather than the brief, and every auditor treated the brief as the only authority. `grep -c "advanced solution" context/01-PROBLEM-PDF.md` = **0**; `00-MASTER-CONTEXT.md:130` carries it verbatim. **The ambiguity is real and is recorded rather than resolved:** the master context's own header limits its authority to "dates, prizes, eligibility, registration and FAQs", and Theme is not in that list — but the sentence speaks to *validity*, and eligibility is. Under hard rule 1 that is a STOP-and-record. The safe reading is nearly free, because the same sentence names **five** acceptable improvement axes and the plan stakes everything on one.

**O-14 · The judging sentence is a conjunction and the plan executes half of it.**
> *"Judges focus on whether each design choice **improves the solution and helps the agent reach the goal reliably**."* — `01-PROBLEM-PDF.md` §2

CH-08 measures the first conjunct exhaustively. **VERIFIED:** `grep -ihc` over all six plan files for `reliab` = 0, `reach the goal` = 0, `error rate` = 0, `retry` = 0 (except three hits in `prompts/CH-00.md` §3 *defining* the logger record type and never aggregating it), `abstain` = 0. **The data is already being written from the first run and no chunk consumes it.** Worse, there is no declared policy for a run that emits no parseable verdict — so whether an unparseable A1 output counts as wrong or gets dropped is left to whichever session writes CH-08, and **if the two arms resolve it differently the headline comparison is silently rigged.**
**FIX — INSERT as a second done-when on CH-08, using data the logger already captures:**
```
**Reliability — the second conjunct.** A per-arm table beside the accuracy matrix, assembled from the
trajectory records and the cost ledger. No new instrumentation.

| arm | items_attempted | schema_valid_verdicts | no_verdict | tool_error_rate | retry_rate | mean_tool_calls | accuracy min/median/max across 3 reps |

**The no-verdict policy is declared in `GOOD.md` before any arm runs and applied identically to every
arm: a run that emits no schema-valid verdict scores as WRONG, never as excluded.**
`schema_valid_verdicts + no_verdict == items_attempted` is asserted by a test, per arm. Report the
3-rep spread as min/median/max, never as the mean alone.
```

**O-15 · The type-4 baseline is performed and its verdicts are thrown away.**
> *"| 4 | The manual process people use today. |"* — `01-PROBLEM-PDF.md` §3, the four sanctioned baselines
> *"…show through clear evidence that your solution improves **the way the task is handled today**."* — §1

**VERIFIED:** `CONTEXT.md` §4 maps its arms onto PDF baseline types 1, 2 and 3 and stops. `grep -ihc "handled today|manual process|status quo|human accuracy"` across all six plan files = **0**. Yet the manual process *is* performed: `plan.md:75`, CH-09's *"blind human-time study (8 items by hand, stopwatched, before seeing gold)"*. The operator will adjudicate 8 items by hand against the real CFR text before gold is opened — **which is exactly a type-4 baseline producing 8 verdicts — and no card tells him to write them down.** So the whole answer to "improves the way the task is handled today" is a minutes-per-item figure with no correctness number for today's process anywhere. **And the sequencing makes it unrecoverable:** once gold is opened those verdicts can never honestly be collected again.
**FIX — one clause, and it must land before the study runs (it folds into CH-01b item 6):** `the by-hand study records the operator's VERDICT for each of the 8 items alongside the stopwatch time, in docs/evidence/human-time/by-hand-log.md, committed BEFORE gold for those items is opened — the commit timestamp is the proof. Those 8 verdicts are scored by the same scorer as every arm and reported as the type-4 baseline row, with n=8 and "the timer is the author" stated beside the number.`

**O-16 · "Same evaluation method at every row" — the changelog rows will carry four different kinds of thing.**
> *"Then show the result using **the same evaluation method whenever possible**."* — `01-PROBLEM-PDF.md` §4

**VERIFIED:** CH-05's done-when is *"golden fixtures pass"*; CH-06's is *"agent emits the full `resolution_trace`"*; CH-07's is *"card completed"*. None produces a primary-metric number, so the changelog's EVIDENCE column holds a fixture pass, a trace, a card, and only then an accuracy figure. `CONTEXT.md` §4's fairness rule constrains the **arms**; nothing constrains the **estimator** across changelog rows.
**FIX — ADD one line to each of CH-05/06/07's done-when:** `report the primary metric on the frozen eval set at this point in the build, with the same scorer, so the changelog's EVIDENCE column is comparable row to row. If the number cannot be produced for this iteration, say so in the row rather than substituting a different measure.`

**O-17 · The video is a submitted deliverable that no privacy control in the plan can see.**
> *"Keep credentials and private information outside the submission."* — §7 ground rule 08

**VERIFIED:** every rule-08 mechanism in the plan and in all 94 findings reads text that git tooling can read — `CLAUDE.md` rule 12 covers `.env`, CH-14's scan covers history, D-4 covers a string in a markdown file. **A screen recording is none of those.** A five-minute capture of this workstation can show a terminal title, a file tree, an editor tab, a browser tab, a notification, or an `.env` in a sidebar, and nothing in the plan looks.
**FIX — ADD to CH-13's done-when:** `Before upload: watch the recording end to end at full size with the specific intent of finding credentials, absolute home paths, the operator's contact details, other browser tabs, notifications, and any file tree showing git-ignored directories. Record that you did it. Shoot in a clean profile with notifications off and a fresh terminal. This is the one deliverable no secret scanner can read.`

**O-18 · The brief's biggest lever is untouched: nothing tells the judge how to score this.**
> *"**You run this evaluation yourself. If the format above fits your task poorly, design your own clear scoring rubric and propose it, so the judges can use it to assess your workflow.**"* — `01-PROBLEM-PDF.md` §5, in a highlighted box

**VERIFIED:** nothing in any of the six plan files produces an artifact addressed to a judge saying how this submission should be assessed. `01-PROBLEM-PDF.md` §5's own decoded note calls this *"the biggest single lever in the document"*. The project should **not** replace the primary metric — that prohibition is correct and stays. But the escape hatch is not only about replacing a metric: it invites a short, explicit statement of what to look at and in what order. **Cheap, and it is the one place where a hard-on-yourself framing is rewarded.**
**FIX — a ~200-word `HOW-TO-JUDGE.md`, linked from the README's first screen and from the Description:** name the primary metric and why it is the one the intended user cares about; name the trivial attack that was measured against it and its number (`n_instructions` pinned at 0.5000; best of 26 features 0.5934 inside its own null at p = 0.185); point at `GOOD.md`'s pre-registration timestamp and invite the judge to check it precedes every result commit; point at the exclusion ladder and the leakage-strip counts; and state the limits — what the benchmark does not measure, what n can and cannot support, and what was not run. A rubric that tells a judge where the project is weakest reads as confidence, not as risk.

**O-19 · `GOOD.md` defines "good" for the evaluator, not "for the intended user".**
> *"Before running the evaluation, define what a good final result looks like **for the intended user**."* — §5

**VERIFIED:** all three places `GOOD.md` is specified define good as a statistical threshold — `A1 ≥ B0-agent + 8 pp, McNemar p < 0.05, n ≥ 84, A1 ≥ 0.80`. That is what is good *for the experiment*. Nothing states what is good *for the drafter*: how many false alarms per rule she will tolerate before she stops reading the worksheet, or what catch rate makes it worth opening at all.
**FIX — ADD to `GOOD.md`'s pre-registration, above the statistical block:** `**Good, for the drafter clearing a rule for publication:** the worksheet catches the defect before the rule ships, and it does not cry wolf so often that she stops opening it. Operationally, at the pre-registered guards: a missed-defect rate at or under 0.25 means three defects in four are caught before publication, against a status quo where the instruction carries no evidence of its own executability at all; a false-defect rate at or under 0.25 means she re-reads one clean section in four. She would accept that trade; she would not accept it reversed. These two numbers, not the accuracy figure, are what makes the tool usable, which is why they are guards and not headline metrics.`

**O-20 · Judging runs for four days after the deadline, against a live repository nobody is told to freeze.**
> `| 6 | Validation screen | Aug 31 – Sep 1 | … |` and `| 7 | Judge review | Sep 2 – Sep 4 | … |` — `00-MASTER-CONTEXT.md` §7

**VERIFIED:** the plan treats 2026-08-31 18:00 UTC as the finish line. Every judging act happens **after** it, against a GitHub repository that stays live and that the operator can still push to. Nothing says not to. A commit landing on `main` on Sep 2 changes the artifact a judge is mid-way through reading, and it changes the thing the plagiarism and trace-integrity checks were run against.
**FIX — ADD as CH-15's final step:** `After the last permitted touch at 17:00 UTC, tag the submitted state: git tag -a submitted-<sha> -m "the submitted artifact" && git push --tags. Record the tag and the zip's SHA-256 in SUBMISSION.md. Do not push to main again until winners are announced on 2026-09-07. If a defect is found after the deadline, it goes in a branch and in an issue, never on main — the repository under judgement must be the repository that was submitted.`

**O-21 · Exporting the session transcripts raw re-imports everything the `.gitignore` exists to exclude.**
The trajectory export (already-fixed item 2) is the right fix, and executing it naively would undo D-4 and D-5 at once. **VERIFIED, by scanning the four transcripts on disk:**

| Transcript | Size | base64 runs ≥ 10k | Payload | Phone hits | Email hits |
|---|---|---|---|---|---|
| `9acf056f-…` (architect) | 15,902,478 B | **41** | **13.05 MB = 82.1% of the file** | 5 | 20 |
| `6ab8522b-…` | 2,166,960 B | 0 | 0.00 MB | 2 | 2 |
| `3b661cd3-…` | 2,697,409 B | 1 | 0.01 MB | 0 | 0 |
| `e3814df5-…` (this session) | 2,515,991 B | 2 | 0.03 MB | 27 | 2 |

Those 41 base64 runs are the HackerEarth page screenshots — the very assets `context/images/`, `context/screenshots/` and `context/slices/` are git-ignored to keep out. A raw export commits **13 MB of incompressible micro1 page assets** into a 50 MB-capped archive, plus the operator's phone and email at scale, plus verbatim brief text. *(The 27 phone hits in this session's own transcript are an artifact of this audit grepping for the number — which is itself the point: the export must redact, not trust.)*
**FIX — REPLACE `tools/export_session.py`'s redaction spec in `prompts/CH-00.md` §1b with:**
```
The exporter is a REDACTING exporter, and its test asserts each rule fires:
  - replace every base64 run of 1,000+ chars with `[image elided: <N> bytes, <sha256[:12]>]`;
  - replace the user directory with `~`;
  - replace the operator's phone number and email with `[redacted - ground rule 08]`;
  - replace any `sk-ant…`, `AIza…`, `Bearer …` or the funded key's first eight characters;
  - drop any tool_result whose source path is inside a git-ignored directory, replacing it with
    `[elided: read from <path>, excluded from the repository - see PROVENANCE.md §6]`.
Print, per export: input bytes, output bytes, and a count per redaction rule. A rule that fired zero
times prints as zero (hard rule 14). Assert output bytes < 2 MB per transcript.
```

**O-22 · Two eligibility criteria are checked first at the validation screen and appear nowhere.** *(minor)*
**VERIFIED:** `grep` for `payout`, `identity`, `location` across all six plan files = **0**, and across all 94 findings = **0**. Criterion 7 (*"must be able to receive payment through the approved payout rail in their country"*) and criterion 8 (*"Accurate identity, location, contact and eligibility information is required. **Duplicate or false registrations may be disqualified.**"*) are the only criteria whose stated consequence is disqualification, and eligibility heads the six qualification-gate checks. **FIX:** the operator confirms, in ten minutes, that the registration profile carries accurate identity/location/contact and that only one registration exists; record it as `Q0` alongside the registration timestamp (m-7). Nothing to build.

**O-23 · Three separately-awarded prizes with published criteria appear nowhere in the plan or in 180 KB of findings.** *(polish)*
**VERIFIED:** `grep -c "Best Engineering Workflow\|Most Useful Real-World\|Best Demonstrated Improvement"` across all six plan files = **0**. The plan optimises exclusively for the /100 rubric. Two of the three award criteria describe what this project already is — *"Strong architecture, thoughtful technical decisions, clean implementation and a workflow that feels robust"* and *"the clearest improvement from the original baseline… what changed, why it changed, and what got measurably better."* **FIX:** no new work. When writing the README's opening and the HackerEarth Description, use the award language deliberately — it costs nothing and it is the organiser's own vocabulary.

**O-24 · Official clarifications are binding and have no home in the precedence chain.** *(minor)*
**VERIFIED:** `00-MASTER-CONTEXT.md` §12 — *"Official clarifications will be shared with all participants."* `grep -ihc "clarification\|announce"` across all six plan files = **0**. An organiser clarification issued on Aug 30 or 31 would outrank `CONTEXT.md` and there is nowhere to record it and no rule ranking it. **FIX — ADD to `CLAUDE.md`'s Precedence line, at the very top:** `an official organiser clarification (recorded in QUESTIONS.md with its source and UTC timestamp) → context/01-PROBLEM-PDF.md (local, not redistributed — see Q3) → CONTEXT.md → …`

**O-12 · Verbatim reproduction of the brief inside files that ship — checked, and the ruling holds.**
Worth stating because it looks like an inconsistency and is not. `context/01-PROBLEM-PDF.md` is excluded as a full reproduction, yet `09b-audit-raw.json` carries **76 unique `requirement_verbatim` quotes totalling 11,638 characters, 43 of which trace to the brief**. That is quotation-for-analysis, addressed back to the copyright holder, inside a submission they will own — categorically different from republishing the document. **The exclusion ruling is coherent.** One line in `PROVENANCE.md` §6 stating the distinction stops a validator reading it as inconsistent.

**O-25 · `d.pdf` is not micro1's brief. It is a Descartes marketing brochure from the dead project — and the audit's mislabel propagated into the `.gitignore`.**
Nobody opened it. Every auditor, and the consolidated audit, treated it as micro1's problem PDF. **I decoded it** — the file uses subset fonts with a custom CMap, so it needed the ToUnicode tables applied rather than a plain string extraction.

**VERIFIED, from the decoded text of `d.pdf` (134,968 B):** occurrences of `Descartes` = **18**, `Customs Info` = **13**, `CROSS` = 1 — against `micro1` = **0**, `Agentic` = **0**, `Hackathon` = **0**, `rubric` = **0**, `Ground rules` = **0**, `trajector` = **0**, `baseline` = **0**. It opens *"Product Information — Descartes Customs Info Reference — Helping Businesses Work Smarter by Navigating Global Trade Content"* and closes with a 14-day free-trial pitch. It is a trade-compliance product brochure about HTS classification and CBP CROSS rulings — **an artifact of the killed CROSSCheck project**, dated 2026-08-29 20:57, the evening that project died.

**The mislabel is in a file that ships.** `context/09-COMPLIANCE-AUDIT.md:21` states `| d.pdf | 132 K | micro1's own problem PDF, republished |`. That is false, and it propagated: `prompts/CH-00.md:37` now lists `d.pdf` under the comment `# third-party material we must not redistribute (micro1's own assets)`. **The exclusion is right for the wrong reason** — it *is* third-party material that must not be redistributed, but it is *Descartes'*, not micro1's.

**And the consequence that matters more:** `context/01-PROBLEM-PDF.md`'s own header names its source as `micro1 - First Hackathon97ce7c5.pdf`. **VERIFIED: `d.pdf` is the only PDF in the tree outside `context/me/`, and no file by that name exists on this machine.** So the document at the top of the precedence chain — the one carrying the rubric weights, the anti-slop clause, the ten ground rules and the four deliverables, and the one this entire audit and this entire remediation validated against — **is an agent-produced extraction that cannot be checked against its source here.** See §9 item 11.
**FIX (a):** correct `prompts/CH-00.md`'s `.gitignore` comment — move `d.pdf` under a line reading `# third-party marketing material from the abandoned CROSSCheck research (Descartes Customs Info Reference brochure) - not ours to redistribute`. **FIX (b):** leave D-1's Q3 ruling as drafted — it speaks only to `context/01-PROBLEM-PDF.md`, which *is* micro1's material, and it does not repeat the mislabel. Do not let the correction spread further than the two places that carry it. **FIX (c):** the 15-minute read-back in §9 item 11 — which is the fix that actually matters.

---

## 8. The reconciled plan

### 8.1 The arithmetic, stated plainly

**It does not fit. Not by a little.**

| | Hours |
|---|---|
| Now: **2026-08-30 05:15 UTC**. Deadline 2026-08-31 18:00 UTC | **36.8 h wall-clock** |
| Less one protected sleep block | −4.5 |
| **Effective working time** | **≈ 32.3 h** |
| of which Phase 3 is protected from 06:00 UTC Aug 31 | 12.0 h |
| **Available before Phase 3 opens** | **≈ 20.3 h** |

**The remediation bill, two ways, because one of them is misleading.**

Summing the per-finding estimates gives **34.6 h** for the 64 confirmed findings plus **≈ 11 h** for what this pass added — **≈ 46 h**. **That number double-counts heavily** and I will not present it as the answer: thirty-one of the confirmed findings are edits to the same six spec files, and applying them as *grouped* edits — one pass per file — costs a fraction of applying them one at a time. My own estimate for Stage 0 done properly, as eleven grouped edits, is **6–7 h**. The rest is scope added to chunks that were going to run anyway.

| Work | Hours |
|---|---|
| Architect pre-flight, as **grouped** edits (§8.2 Stage 0, P1–P11) | **6.5** |
| Remediation that genuinely adds scope inside chunks | **≈ 11.5** |
| Phase 1 as re-estimated, including three reviews | **15.5** |
| Phase 2 as specified | **11.5** |
| Phase 3 as specified | **12.0** |
| **Total** | **≈ 57 h against ≈ 31.5 h available** |

**The shortfall is roughly 25 hours — the plan is about 1.8× oversubscribed.** This is not a problem remediation created: the audit's own re-estimate already had Phase 1 alone at 15.5 h against a stated "~5 h". Verification *reduced* the raw bill from 74.9 h to 34.6 h on the original findings; this pass then added ~11 h of its own, most of it in Stage 0 where it is cheapest. The gap that remains is structural and predates all of it.

**The operator decides what gives. Here is the honest menu, in the order I would cut, with what each costs.**

| # | Cut | Saves | What it costs |
|---|---|---|---|
| 1 | **CH-07, the ordered-state ledger** — pre-declare it now as the first capability cut | 2.0 | Ship **two** capabilities and **three** counted removals (leakage probe, collision detector, ledger-not-built-with-its-measured-class-size). The brief demands removed experiments and most entrants will have none. Two kept capabilities each traced to a numbered failure, plus three counted removals, is a *better* changelog than three kept capabilities and a rushed CH-08. **Record it as a dated architect ruling with its reason, never as an omission.** |
| 2 | **Ablation reps 3 → 1**; final arms keep 3 | 1.0 | Wider CIs on the ablations only. Pre-register the reduction in `GOOD.md` (M-14) so it is a declared decision. Also saves most of the API budget. |
| 3 | **Merge CH-01 and CH-01b into one session** | 0.5 | Round-trip only. |
| 4 | **Drop the user-facing CLI to a committed demo** (M-25's second half) | 1.5 | Keep `--offline` replay and the `docs/demo/` worksheet on a non-eval rule; drop the polished CLI surface. The video beat survives. |
| 5 | **CH-02's gate FULL → CODE-ONLY + a three-fixture domain spot-check** | 1.25 | **Do this last.** CH-02 is the component that already produced 0.46. O-10's free fixture partially offsets the risk. |

**Cuts 1–4 recover 5.0 h, leaving a ~20 h shortfall.** That is still not enough, and I will not pretend otherwise by trimming the estimates. The remaining lever is the one the process already names: **the T−12h cutoff and the minimum-viable-submission list (M-8).** Phase 2 gets whatever is left when Phase 3 opens, and the MVS drop list decides what ships from wherever the work has reached. That is the design working as intended, not a failure — but it only works if the drop list exists *before* the hour it is needed.

**What must not be cut, at any price:** any Phase-3 item · the NUMBERS-ONLY gates · the voice pass · the early video upload · the 12:00 UTC draft · and every item in §2. Those are the difference between a scored submission and an unscored one.

### 8.2 The corrected chunk list

**Stage 0 · ARCHITECT PRE-FLIGHT — 6.0 h — no session, before CH-00 runs**

| # | Action | Files | h |
|---|---|---|---|
| P1 | **D-1** — repair all five `prompts/CH-00.md` contradictions; add the Q3 block; widen the scope fence; add the `CLAUDE.md` duty | `prompts/CH-00.md`, `CLAUDE.md` | 0.5 |
| P2 | **D-2** — the leakage strips into `CONTEXT.md` §8; CH-03/CH-04 done-when; the review instruction | `CONTEXT.md`, `plan.md` | 1.5 |
| P3 | **D-3** — the repo-public flip into CH-15, with anonymous-clone verification | `plan.md` | 0.2 |
| P4 | **D-4 + D-5 + M-5 + M-6** — the rewritten `.gitignore`, the PII redaction step, the pre-commit hook, the prompt-file moves, extract-then-freeze into CH-01/CH-03 | `prompts/CH-00.md`, `plan.md` | 0.75 |
| P5 | **D-6** — CH-12's selection rule | `plan.md` | 0.4 |
| P6 | **M-7** — AMBER branch, RED path, CH-02/CH-03 numeric fallbacks (restore from `08-FINAL-CALL.md`) | `plan.md` | 0.5 |
| P7 | **M-8** — tiered review, NUMBERS-ONLY tier, two-strike rule, MVS drop list, wall-clock triggers, sleep block | `PROCESS.md` §6–§7 | 1.0 |
| P8 | **M-1 + M-2 + M-3 + M-4** — resync `PROCESS.md` §7 to `plan.md`; read-order and precedence; the Files table; the changelog table | `PROCESS.md`, `CLAUDE.md` | 0.75 |
| P9 | **M-9 + M-10 + M-11 + m-17 + m-18 + O-9** — `CONTEXT.md`'s internal number conflicts, the two senses of "order-sensitive", the §4/§7 prediction mismatch, the agent counts, the "92" claim, the Prior et al. citation | `CONTEXT.md` | 0.75 |
| P10 | **M-22 + M-25** — `needs_human_review` fields, the §9 trigger rule, the §5b entry point | `CONTEXT.md` | 0.4 |
| P11 | **M-14 + m-7 + O-11** — Q1 budget correction with pre-registered reduction; Q0 registration record; design-swarm models into `AI-USE.md`'s seed | `prompts/CH-00.md`, `QUESTIONS.md` seed | 0.25 |

**Phase 1 — 17.0 h**

| Chunk | Change | Gate | h |
|---|---|---|---|
| **CH-00** | + `docs/trajectories/build/`, `agents/` + loader (M-12), `ARCHITECT.md` (M-15), `tools/render_trajectory.py` (M-27), logger field-whitelisting + `gitleaks` pre-commit hook (M-13), the corrected `.gitignore` and the PII redaction step, the prompt-file moves; copy the four existing session transcripts; start the govinfo fetch in background | — | 2.0 |
| **CH-01** | + defect pool converted to a **rate** (O-7); + downloads land in `data/raw/`, extract-then-freeze; + republish O-7's number from govinfo beside the eCFR figure | — | 2.0 |
| **CH-01b** *(new)* | evidence migration (M-16), the blind human-time baseline, the count-matched-sibling yield (M-17) | — | 1.5 |
| **CH-02** | unchanged scope; **fallback pre-registered**; O-10's § 39.13 golden fixture | FULL-core | 2.0 + 1.25 |
| **CH-03** | + **the leakage-strip test** (D-2); + extract-then-freeze (D-5); + `data/README.md` (m-6); fallback pre-registered | FULL-core | 2.5 + 1.25 |
| **CH-04** | + USD ceiling and rep-reduction into `GOOD.md`; + the would-have-leaked count | FULL-core | 1.5 + 1.25 |
| **★ CHECKPOINT** | + **NUMBERS-ONLY review before the call is acted on**; + write **both** video scripts | NUMBERS | 1.5 + 0.5 |

*Parallel, operator, during long jobs:* hand-draft README §§ user / bottleneck / value and video beats 1–2 on a `docs` branch (this is also M-30's fix); build the worksheet HTML shell against a synthetic fixture; append to `AI-USE.md` every session. **CH-13A is recordable and uploadable the moment CH-04 lands.**

**Phase 2 — GREEN *or* AMBER — whatever remains until 06:00 UTC**

| Chunk | Change | Gate | h |
|---|---|---|---|
| CH-05 | + resolve the `me`/`mw`/`ma` inversion flagged in §9 before building | code-only | 2.0 |
| CH-06 | + one eval item routes to the queue and its trajectory contains a `human_checkpoint` record (M-22) | CODE-ONLY | 2.5 |
| CH-07 | unchanged — **pre-declared as the first capability cut** | code-only | 2.0 |
| CH-08 | + B0′ named (M-20); + per-arm token table; + `error-taxonomy.csv` (M-21); + `hard-case/` (m-13); + two interactive checkpoint runs; + catch rate / interruption cost | **NUMBERS** | 3.0 + 0.5 |
| CH-09 | + hot-take Path B; + the second human-time pass deferred to Phase 3; + the two "what I'd build next" sentences | — | 1.5 |

**Phase 3 — protected — opens 06:00 UTC Aug 31 — REORDERED so the video clears T−8h**

| Order | Chunk | h | Why here |
|---|---|---|---|
| 1 | **CH-14a · early rehearsal** — fresh venv from pinned `requirements.txt` (Python 3.12.2), network off, manifest verify, Tier-1 replay, once under WSL or `python:3.12-slim` | 1.25 | a fatal defect must surface with time to fix it, not at T−2h |
| 2 | **CH-13B · video** — record to the chosen script, splice with 13A, upload, verify signed-out, under 5:00 | 1.5 | **must complete by 10:00 UTC (T−8h).** This is the reorder that makes the card's own deadline reachable |
| 3 | **CH-12 · trajectories** — the selection rule, the rendered pages, `AI-USE.md` | 1.5 | |
| 4 | **CH-11 · README + `REPRODUCE.md`** — full section list, per-arm commands with EXPECTED blocks, `THIRD-PARTY.md`, `LICENSE`, `SAFETY.md`, the claims-audit script | 2.5 | |
| 5 | **CH-11b · VOICE PASS** *(new)* — operator only, no session | 1.0 | must precede nothing now, but must follow CH-11; if the video slips, it precedes CH-13B |
| 6 | **CH-10 · worksheet** — + disclaimer band and provenance footer; + second human-time pass; + cold usability read | 2.0 | |
| 7 | **DRAFT-1 · 12:00 UTC** — all four fields saved as a draft | 0.5 | **wall-clock, not dependency.** From here the project is insured |
| 8 | **CH-14b · final rehearsal** — repeat from the finished repo; `gitleaks` over full history; `docs/evidence/access/` | 0.75 | |
| 9 | **CH-15 · SUBMIT · 15:00 UTC** — zip, assert < 50 MB, extract-and-replay, **flip public and verify anonymously**, submit, screenshot. **17:00 last touch. Nothing after 17:30.** | 1.0 | |

**Note on the reorder:** CH-13B moves from fourth to second. Under the current order the video's own T−8h deadline is unreachable by 2 hours (§6, item 5). Under this order it clears with margin, and CH-14a still runs first so a broken manifest surfaces early.

---

## 9. What I could not verify

Honest list, with how much each matters.

1. **Whether registration is currently in a submittable state.** **UNKNOWN.** The public challenge page returns 200 unauthenticated, but registration status requires a logged-in session I cannot open. What I *can* evidence is the operator's own "Yes, already registered" ~20 h before the close, plus a form field list that can only be read from inside. **Matters: low now, catastrophic if wrong.** Cost to close: one screenshot.

2. **The count-matched-sibling yield — the assumption `≥ 42 pairs` rests on.** **UNKNOWN, and I tried.** On `fr20240103.xml` I parsed 42 `<REGTEXT>` blocks and found 0 amending ≥ 2 distinct sections — a result I am **discarding, not reporting**, for two reasons I verified rather than assumed: the issue is dominated by FAA airworthiness directives that all amend § 39.13, and my own `<SECTNO>` extraction failed on 33 of 42 blocks. A number produced that way would be worse than none. **Matters: high** — it is the largest unquantified risk in the project (M-17).

3. **The per-item rate at which the leakage strips actually fire.** **UNKNOWN.** I measured structural containment (26/28 `<EDNOTE>` inside `<SECTION>`) and observed the `<EFFDNOTP>` leak verbatim, but `"could not be incorporated"` appears 0 times in the one volume I parsed, so **I have not observed a positive label leaking.** That is exactly why the fix is a test and a count rather than an argument. **Matters: high.**

4. **`CONTEXT.md` §3's headline numbers 0.545 / 0.5855 / 0.52.** **UNKNOWN — not traced to any artifact.** They resolve only to `08-FINAL-CALL.md:111` and `:143`, which are documents. Grepping for them lands in the dead CROSSCheck project's data. **Matters: high** — it is the claim the README, the Description and the video all lead with (M-16).

5. **`CONTEXT.md` §6's "26/33 and 35/42 … ~80% of the pool".** **UNKNOWN.** Nearest artifact is `probe/anchor_rows.json`, n = 30, showing **16/30 = 53%** — a third pool, ~27 points off the gloss. It is the entire argument for the tool's ordering *and* for capping capabilities at three. **Matters: high** (M-16).

6. **An oddity I flagged and did not interpret.** In that same file the aggregate match counts are `me=36, mw=36, ma=26` — alphanumeric-only matching finding **fewer** anchors than exact matching, the opposite of what a widening normalisation ladder should do. Either the field names mislead or something is inverted. `CONTEXT.md` §1 makes normalisation levels precision-critical. **Matters: medium** — CH-05 should resolve it before building `cfr_resolve`.

7. **The hot take's per-class figures (+12.0 pp Rejected, −4.0 pp Verified, −16.7 pp policy class).** **UNVERIFIED.** The *headline* statistic checks out exactly (`fisher_p = 0.6368`, net +4.0). The per-class split appears only as prose at `killtest/draft_67.md:220`. **Matters: medium** — CH-09 should recompute rather than re-quote.

8. **Whether the funded Anthropic account can call `claude-sonnet-5`.** **UNKNOWN.** No `.env` exists at the repo root and no `ANTHROPIC_API_KEY` is set in the environment (checked by name only, never read). **Matters: high, and it gates the CHECKPOINT** — M-14.

9. **Adversarial coverage is 89 of 94, not 94.** Five verification agents died to connection errors (`L1-01`, `L1-06`, `L2-01`, `L2-07`, `L2-10`) and were re-run in a separate pass that returned verdicts but reached this document too late to be challenged. **Those five carry a single opinion each.** Three of them are load-bearing — L1-01 (build-agent trajectories), L2-01 (the `.gitignore`) and L2-10 (evidence for pre-repo numbers) — but all three are also covered independently: I verified each myself with the commands shown in D-1, D-4, D-5 and M-16, and the re-run agent for L1-01 reached the same conclusion about the `prompts/CH-00.md` self-cancellation that I did. **Matters: low.** Nothing in §2 rests on an unchallenged verdict.

Related, and worth stating plainly: **183 agents ran, 178 returned, 5 died** — a 2.7% failure rate on a read-only workload. A build session doing the same work under a deadline should expect the same, which is an argument for the two-strike rule and the pre-written prompt queue in M-8/M-15 rather than for retrying indefinitely.

10. **HackerEarth form field character limits.** **UNKNOWN.** `grep` for "character" across `plan.md` returns 0. The Description is identified as the first thing a judge reads and its length ceiling is unrecorded. **Matters: low, trivially checkable** — look at the form during DRAFT-1.

11. **Whether `context/01-PROBLEM-PDF.md` faithfully reproduces the actual brief.** **UNKNOWN, and this is the assumption everything else stands on.** Five auditors, eight requirement-sweep agents, ninety-four verification and challenge agents, and this document all validated the plan against that file. **VERIFIED: its stated source, `micro1 - First Hackathon97ce7c5.pdf`, is not on this machine** — `d.pdf` is the only PDF in the tree and it is a Descartes brochure (O-25). So no one has checked the extraction against the original, and the file itself flags the hazard: it marks some passages *(decoded)*, meaning the extracting agent's analysis rather than micro1's words, and **no auditor checked which side of that line their quoted requirement fell on.** The rubric weights, the anti-slop clause, the ten ground rules and the four deliverables all come from it. **Matters: high, and it is fifteen minutes of work.** The operator has the original. Read §6 (rubric), §7 (ground rules) and §8 (deliverables) of `01-PROBLEM-PDF.md` against the actual PDF, confirm the verbatim blocks are verbatim, and record the check in `PROVENANCE.md` with its date. If a single rubric weight or deliverable clause is wrong, everything downstream of it is wrong too — and nothing else in this document would have caught it.

12. **The mutual applicability of the ~35 edits proposed here.** **PARTIALLY UNKNOWN.** They were verified individually. I checked the pairs that touch the same lines — the `.gitignore` (D-4, D-5, M-5, M-6, O-25) is presented as one replacement block precisely because five findings edit it, and CH-15's procedure (D-3, O-20, m-8) likewise. I did **not** systematically diff every proposal against every other. **Matters: medium.** Apply §8.2's Stage 0 in the order given (P1…P11), which groups edits by file, and re-read each file once after its group rather than after each edit.

---

*End of remediation plan. Nothing in this document has been applied. The architect applies it; that separation is the point.*
