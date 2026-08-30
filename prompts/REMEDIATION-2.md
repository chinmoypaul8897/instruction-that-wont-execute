# REMEDIATION PASS 2 — finish the outstanding findings, then read the whole spec cold

Two jobs, in order. The second matters more than the first.

**You do not edit the spec.** See §6. You write one file.

---

## 0. How this goes wrong

**Accepting findings without checking them.** The first remediation pass verified 94 findings and killed 22 of them as false or duplicate. The architect then applied fixes and **twice relayed an agent's claim without verifying it** — once calling a file "micro1's brief" when it is a Descartes brochure, once quoting an API budget 3× too high. **Check every claim against the files as they stand now.**

**Reporting stale findings.** The audit and the first remediation were written against an *earlier* version of these files. Roughly two dozen fixes have since been applied (§2). A finding that describes a problem already fixed is noise — say `ALREADY-FIXED` and move on.

**Padding.** A shorter honest list beats a long padded one. `FALSE-ALARM` and `NOT-WORTH-FIXING` are good outcomes.

There is no time pressure on this pass. Read everything.

---

## 1. Read

| File | What it is |
|---|---|
| `context/10-REMEDIATION.md` | the verified remediation plan. **§3 MAJOR (from M-12 onward) and §4 MINOR/POLISH are your input.** §7 "What nobody audited" and §9 "What I could not verify" are also unresolved. |
| `context/09b-audit-raw.json` | all 94 original findings, unmerged |
| `context/01-PROBLEM-PDF.md` | the official rules. **AUTHORITATIVE.** |
| `context/00-MASTER-CONTEXT.md` | logistics, timeline, eligibility, FAQs, the qualification gate |
| `CONTEXT.md` · `plan.md` · `PROCESS.md` · `CLAUDE.md` · `PROVENANCE.md` · `prompts/CH-00.md` | **the current state — this is what you audit, not what the earlier documents describe** |

---

## 2. Already applied — verify adequacy, do not re-report as new

D-1 through D-6 and M-1 through M-11, plus:

- **Leakage strips** into `CONTEXT.md` §8 (`<EDNOTE>`/`<EFFDNOTP>`/`<CITA>`/`<EAR>` stripped and counted), the leakage-strip test in CH-03's done-when, and the reviewer instruction to confirm it fails on unstripped input
- **`.gitignore` rewritten** — `*.xml`, `data/raw/`, `dist/`, `*.zip`, `*.mp4`, `*.stackdump`; design prompts moved to `prompts/design/` rather than ignored
- **PII redaction sweep** as CH-00 step 5; pre-commit hook for size and PII
- **AMBER now proceeds**; RED path specified; **VALIDITY CONSTRAINT** recorded (an entry with no advanced solution is invalid); CH-02/CH-03 numeric fallbacks pre-registered
- **Ruling R-01** — CH-07 NOT BUILT, pre-declared as counted removal #3; ablations 1 rep; CH-01/CH-01b merged; polished CLI dropped
- **Wall-clock triggers, MVS drop list, two-strike rule, NUMBERS-ONLY review tier, protected sleep block** in `PROCESS.md`
- **Phase 3 reordered** — video runs 2nd and must clear 10:00 UTC; **CH-11b voice pass** added; **CH-15 Submit** added with an unauthenticated repo-visibility check
- **`PROVENANCE.md`** written, including a recorded verification that the brief transcription matches the original PDF
- **Parallel-session file-ownership rules** in `CLAUDE.md`
- **Budget ruling revised** — `claude-haiku-4-5` for every arm via the **Message Batches API**, operator ceiling **USD 20**, hard stop at **USD 18 enforced in the logger**, plus a **model-sensitivity check** re-running B0/B0-agent on `claude-sonnet-5` over 20 items at the checkpoint

If any of these is a half-fix, say so and say what is missing.

---

## 3. JOB A — the outstanding findings

**Unapplied MAJORS: M-12 onward.** These are not cosmetic. They include, and this list is not exhaustive — read §3 yourself:

- **M-12** `agents/` — one instruction file per arm, plus a loader returning `(text, sha256)`. Deliverable 1 requires *"the instructions that shape each agent"* as shipped files.
- **M-13** named secret-scan tool and pass criterion; logger field-whitelisting
- **M-15** `ARCHITECT.md` — the architect's state currently lives in chat, which `PROCESS.md` §3 itself forbids
- **M-16 / M-17** evidence migration and the count-matched-sibling yield — **the numbers justifying the design were computed outside the repo and several cannot be traced**
- **M-19** both video scripts written at the checkpoint (GREEN and AMBER-RED branches)
- **M-20** `B0′` named in a chunk — it currently appears in no chunk at all
- **M-21** error taxonomy producing the README's "main failure mode"
- **M-22** `needs_human_review` fields and a **trigger rule** — "unresolved" is undefined, so CH-06 would STOP under hard rule 1
- **M-24** human-time and cost-per-task for **both** arms
- **M-25** the solution has **no entry point** and is never run on an input a user would bring — this also breaks deliverable 2

**Then the MINOR and POLISH tier** in §4.

**For each: verify against the current files → classify `CONFIRMED` / `ALREADY-FIXED` / `FALSE-ALARM` / `NOT-WORTH-FIXING` → for confirmed ones write the exact fix text**, ready to paste, naming file, section, and insert/replace/new.

Also resolve what §7 and §9 of the remediation left open — in particular **whether `CONTEXT.md` still contains any number that cannot be traced to a `docs/evidence/` path**, since hard rule 14 forbids exactly that.

---

## 4. JOB B — read the whole spec cold. This is the more valuable job.

The spec has been edited heavily by one author who has now read it too many times to see it. **Read `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md` and `prompts/CH-00.md` end to end as a fresh build session would**, and answer:

1. **Could a fresh session execute CH-00 without stopping?** Walk it literally. Every instruction, every referenced file, every cited section — does each exist and say what the citation claims? *(The first pass found five contradictions that would have halted the session at hour zero.)*
2. **Do any two files disagree?** The author has already introduced contradictions while fixing contradictions — six of them, found only by a sweep. Check numbers, chunk lists, gate policy, model choice, budgets, phase boundaries, and which capabilities are built.
3. **Does any number appear twice with different values, or once with no evidence path?**
4. **Is anything cited that does not exist** — a section, a table, a file, a ruling ID?
5. **Is the chunk sequence actually executable?** Does every chunk's input exist by the time it runs?
6. **Read `CONTEXT.md` as a reviewer would.** `PROCESS.md` §6 requires reimplementing the load-bearing logic **from `CONTEXT.md` alone, importing nothing from the project.** Is that possible? If a reviewer could not, the gate is theatre. *(This is exactly how the leakage defect survived: `CONTEXT.md` did not mention it, so no reviewer could have caught it.)*

**Job B findings are reported even if they map to no audit item.** They are the point.

---

## 5. Standing constraints — a fix violating one of these is not a fix

- **The clock is not a design input.** The operator has deprioritised schedule for correctness. State hours honestly; propose no cuts justified by time.
- **No self-grading.** **No LLM in the primary scoring path.** **The primary metric does not change.**
- **govinfo only** — `ecfr.gov` and `federalregister.gov` are HTTP 403 from this machine.
- **USD 20 hard ceiling**, `claude-haiku-4-5` every arm, Batch API.
- **50 MB zip cap** on the archive; the repository itself stays complete.
- **Total disclosure** — every agent, model and tool named; commits carry `Co-Authored-By: Claude`.

---

## 6. Scope fence — hard

**You may create exactly one file: `context/11-REMEDIATION-2.md`.**

**You may NOT edit** `CONTEXT.md`, `plan.md`, `PROCESS.md`, `CLAUDE.md`, `PROVENANCE.md`, or anything in `prompts/`. Architect-owned. Proposing a change and making it are different jobs.

**You may NOT** `git init`, commit, create the GitHub repo, write project source, or start any chunk.

Read anything. Run read-only commands to verify — file sizes, greps, `curl -I`, counting, parsing XML already on disk.

---

## 7. Output → `context/11-REMEDIATION-2.md`

```
# Remediation 2

## 1. Verification summary
Counts: confirmed / already-fixed / false-alarm / not-worth-fixing, split MAJOR vs MINOR.

## 2. JOB B — the cold read
The most important section. Findings from reading the spec fresh, whether or not
they map to an audit item. Lead with anything that would stop a build session or
that makes a review gate unable to do its job.

## 3. CONFIRMED MAJORS — grouped by target file
Per finding: what is wrong · the requirement verbatim + source · THE EXACT FIX TEXT ·
file and section · insert/replace/new · hours.

## 4. CONFIRMED MINORS — terse, one line and one fix each

## 5. Untraceable numbers
Every numeral in CONTEXT.md that resolves to no evidence path, with a
keep-and-label / re-derive / delete recommendation for each.

## 6. FALSE ALARMS and NOT-WORTH-FIXING — with the evidence that killed each

## 7. Adequacy of the ~24 already-applied fixes
Sufficient / partial / wrong. If partial, what is missing.

## 8. Is the spec executable?
Direct answer. If a fresh session ran CH-00 right now, would it finish or stop?
If it would stop, at which line and why.

## 9. What I could not verify
Honest, with how much each matters.
```

**Rules of evidence:** label every claim **VERIFIED** (you read it or ran it — give the number, path or output), **INFERRED**, or **UNKNOWN**. Never present a guess as a fact.

---

## 8. Final step

Print a text block, **under 400 words**, for the operator to paste back:

1. Counts: confirmed / already-fixed / false-alarm, MAJOR vs MINOR
2. **The Job B answer: would a fresh session execute CH-00 without stopping — yes or no, and if no, where**
3. The three most serious things found, cold-read findings first
4. How many numbers in `CONTEXT.md` still have no evidence path
5. Whether the ~24 applied fixes are adequate
6. Total remaining hours, honestly
7. Confirmation the full report is at `context/11-REMEDIATION-2.md`

Then stop. **Build nothing.**
