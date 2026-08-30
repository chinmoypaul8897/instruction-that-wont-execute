# REMEDIATION PASS — verify and resolve all 94 compliance findings

A compliance audit of this project's build plan produced **94 findings: 33 disqualifying, 44 major, 15 minor, 2 polish**, proposing ~75 hours of fixes. Only about six have been addressed. Your job is to turn that pile into a **verified, deduplicated, ordered remediation plan with exact text for every fix.**

**You do not edit the spec.** See §5. You produce one document.

---

## 0. The two ways this goes wrong

**Applying findings blindly.** A previous adversarial round on this project found that *"roughly one kill reason in three was not sound"* — verdicts were right, stated reasons often weren't. Five auditors also overlapped heavily. **74.9 proposed hours across 94 findings is inflated; a large fraction are duplicates, already-fixed, or simply wrong.** Accepting them uncritically produces a bloated plan that cannot be executed.

**Dismissing findings to make the list shorter.** The disqualifying ones are gate items — a single one unfixed loses everything before scoring begins.

**So: verify every finding against the actual files and the actual rules. Kill what is false. Keep what is real. Show your working for both.**

There is no time pressure on this pass. Correctness over speed. Read everything.

---

## 1. Read

| File | What it is |
|---|---|
| `context/09-COMPLIANCE-AUDIT.md` | the consolidated audit — **read all of it**, not the first section |
| `context/09b-audit-raw.json` | **all 94 findings** from five auditors, unmerged, with severity, requirement text, proposed fix and hours |
| `context/01-PROBLEM-PDF.md` | the official rules. **AUTHORITATIVE** — every finding is checked against this |
| `context/00-MASTER-CONTEXT.md` | logistics, timeline, eligibility, FAQs, the qualification gate |
| `PROCESS.md` · `plan.md` · `CONTEXT.md` · `CLAUDE.md` · `PROVENANCE.md` | the artifacts being audited, **as they stand now** |
| `prompts/CH-00.md` | the first build prompt, **already revised twice** |

---

## 2. Already fixed — verify adequacy, do not re-report as new

The architect has already acted on these. **Check each fix is actually sufficient**; if it is half a fix, say so and say what is missing.

1. **`.gitignore` before `git init`** — `prompts/CH-00.md` §1, with an assertion of `<60` tracked files and nothing over 25 MB. *(Working tree is 446 MB and contains micro1's own PDF and brand video, the operator's phone number and résumé, and third-party code marked "all rights reserved".)*
2. **Build-session trajectory export** — `prompts/CH-00.md` §1b, `tools/export_session.py`, plus a CLAUDE.md end-of-session duty.
3. **`PROVENANCE.md`** — written, ground rule 02.
4. **CH-15 Submit** — added, hard start T−3h, draft-early.
5. **CH-13 video** — unlisted YouTube, signed-out playback test, sub-5:00 duration check.
6. **CH-14** — `git archive` zip under 50 MB, Tier-1 replay **from the extraction**, `SUBMISSION.md`.
7. **Submission form constraints** — recorded as Q2 in `prompts/CH-00.md`: four fields, Video is a URL, Source Code is a ≤50 MB zip upload, "Save as Draft" exists.
8. **Gate structure** — a consolidation to one review was **reverted**; CH-02/03/04 now have three separate full reviews again, plus a two-strike escalation rule.

---

## 3. Standing constraints — a fix that violates one of these is not a fix

- **The clock is not a design input.** Do not propose cuts justified by time. The operator has explicitly deprioritised schedule in favour of correctness. If a fix is right, propose it and state its hours honestly.
- **No self-grading.** Build sessions never certify themselves.
- **The primary metric does not change.** It is pre-registered and its trivial-attack surface is measured. Every rival that changed its primary died to the first script someone wrote.
- **Deterministic scoring.** No LLM in the primary scoring path.
- **govinfo only.** `ecfr.gov` and `federalregister.gov` return HTTP 403 from this machine.
- **Total disclosure.** Every agent, model and tool named; commits carry `Co-Authored-By: Claude`.
- **50 MB zip cap** on the submitted archive; the repo itself stays complete.

---

## 4. What to do

**Stage 1 — Verify.** For every one of the 94 findings: check it against the current files and the official rules. Classify as `CONFIRMED` · `ALREADY-FIXED` (say where) · `FALSE-ALARM` (say why) · `DUPLICATE-OF <id>`. **Verify by reading and, where a claim is checkable, by running something** — file sizes, tracked-file counts, whether a string exists in a file, whether a URL responds. Do not accept a finding because it sounds right.

**Stage 2 — Deduplicate and merge.** Five lenses overlapped. Merge into single findings with a note of how many auditors raised each — **convergence across independent lenses is a strength signal, so record it.**

**Stage 3 — Order.** Group by: `DISQUALIFYING` → `MAJOR` → `MINOR` → `POLISH`. Within each, order by **which chunk they land in**, so the architect can apply them chunk by chunk rather than jumping around.

**Stage 4 — Write the exact fix.** For every confirmed finding: the precise change, as text that can be pasted into the target file. Not *"the README should mention provenance"* but the actual paragraph. Name the file, the section, and whether it is an insert, a replace or a new file.

**Stage 5 — Check for what the auditors missed.** They audited the plan against the rules. Now audit the *rules* for anything no auditor covered — read the PDF and the master context end to end and list requirements that appear in neither the plan nor the findings.

**Stage 6 — Reconcile the plan.** Produce the corrected chunk list with every fix folded in, hours per chunk, and honest totals. If the total exceeds what is available, **say so plainly and state what the trade-offs are — do not silently trim.** The operator decides what gives.

---

## 5. Scope fence — hard

**You may create exactly one file: `context/10-REMEDIATION.md`.**

**You may NOT edit:** `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, or anything in `prompts/`. Those are architect-owned; the architect applies your remediation. Proposing a change and making it are different jobs, and the separation is the point.

**You may NOT:** `git init`, commit anything, create the GitHub repo, write project source, or start any chunk.

You may freely **read** anything, and **run read-only commands** to verify claims (file sizes, greps, `curl -I`, counting).

---

## 6. Output → `context/10-REMEDIATION.md`

```
# Remediation Plan

## 1. Verification summary
Table: total findings · confirmed · already-fixed · false-alarm · duplicate.
Per-auditor false-alarm rate — which lens was most and least reliable.

## 2. DISQUALIFYING — confirmed, grouped by chunk
Per finding: id · requirement verbatim + source · why the plan misses it ·
how many auditors raised it · THE EXACT FIX TEXT · target file and section ·
insert/replace/new · hours.

## 3. MAJOR — same format

## 4. MINOR and POLISH — terse, one line each with its fix

## 5. FALSE ALARMS — with the evidence that killed each
Be generous here. A shorter honest list is worth more than a long padded one.

## 6. ADEQUACY OF THE EIGHT ALREADY-FIXED ITEMS
For each: sufficient / partial / wrong. If partial, what is missing.

## 7. WHAT NOBODY AUDITED
Requirements in the PDF or master context that appear in neither the plan nor
the 94 findings.

## 8. THE RECONCILED PLAN
The corrected chunk list, fixes folded in, hours per chunk, honest total.
If it does not fit, say so and lay out the trade-offs. Do not trim silently.

## 9. WHAT I COULD NOT VERIFY
Honest list, and how much each matters.
```

**Rules of evidence:** label every claim **VERIFIED** (you read it or ran it — give the number, path or output), **INFERRED**, or **UNKNOWN**. Never present a guess as a fact.

---

## 7. Final step

Print a text block, **under 400 words**, for the operator to paste back:

1. Findings: total / confirmed / already-fixed / false-alarm / duplicate
2. Count of disqualifying items that survived verification, and the three worst
3. Anything found in Stage 5 that nobody had audited
4. Whether the eight already-applied fixes are adequate
5. Total remediation hours, honestly
6. Confirmation the full plan is at `context/10-REMEDIATION.md`

Then stop. **Build nothing.**
