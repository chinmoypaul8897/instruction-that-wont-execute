# AI-USE.md — every model, tool and agent used on this project

**This is part of deliverable 4.** Hard rule 13: *"Nothing about how this was built is
concealed — the hackathon requires agent use and scores how well it was directed."*

This project is machine-written throughout, under a written constitution
(`CLAUDE.md`), a spec that outranks the code (`CONTEXT.md`), and adversarial review
gates by sessions with zero shared context. That is the claim; the trajectories below
are what makes it checkable rather than asserted.

---

## Agent classes — five, all evidenced, and one of them cannot be replayed

**Navigate them with [`docs/trajectories/INDEX.md`](docs/trajectories/INDEX.md)**, which
names, per trajectory, where the instructions are, what the agent did, where the result
landed, and what is worth opening the file for. The curation rule is
[`docs/trajectories/SELECTION-RULE.md`](docs/trajectories/SELECTION-RULE.md), committed
**before** it was applied.

| Class | What it is | Count | Trajectories live at | Replayable? |
|---|---|---|---|---|
| **Research / ideation** | ~90 agents across four design workflows that proposed, attacked and killed candidate projects — **two whole projects died before a line of this one was written** | ~90 | `context/*-raw.json` (committed), beside the synthesised verdicts in `context/03`–`09` | synthesised output only; they predate the git history |
| **Coding** | fresh Claude Code BUILD sessions that write this repository | **11 sessions / 12 files** — CH-00, CH-01, CH-02, SPEC-FIX-1, SPEC-FIX-2, NIGHT-RUN (exported twice), CH-06/CH-08/CH-09, CH-14a, CH-11, CH-11c, CH-12 | `docs/trajectories/build/<CHUNK-ID>.jsonl` | **yes** — full transcript, every tool call and response |
| **Adversarial audit** | subagents spawned *by* a coding session to attack its own conclusion before it ships — see the table below | **103** | `docs/reviews/`, `docs/evidence/ch11c-sweep/`, `docs/evidence/spec-fix-1/` | **NO — `QUESTIONS.md` Q40** |
| **Solution** | the evaluation arms — the thing being measured | **2,097** logged runs across every evaluation arm (2,107 ledger rows less the 10 model-id probe calls) | `docs/trajectories/arms/<arm>-rep<N>.jsonl` (bundled, every record kept) + `docs/evidence/runs/cost_ledger.csv` | **yes** — bundled; `per-item/` is git-ignored and its every record is in the bundle |
| **Probe** | the model-id probe that checked a claim the chunk card pre-registered as fact | **10** runs | `docs/trajectories/probe/probe-model-id__*.jsonl` | **yes** |

**38 trajectory files at `7223552`**, measured by `docs/evidence/ch12/trajectory_facts.py`; the byte total is in `docs/evidence/ch12/trajectory-facts.txt` rather than quoted here, because it grows on every re-export. *The figure names a commit because it rises every time a session exports its transcript — it was 36 when CH-12 began and 37 when CH-12 exported its own.*

### The adversarial-audit class, in full — 103 subagents, and its cost stated separately

This is the class the project leans on hardest and the one a reader is most entitled to
be sceptical about, so it is broken out rather than summarised.

| fleet | agents | model | tokens | wall-clock | launched from | what survives in the repository |
|---|---:|---|---:|---:|---|---|
| SPEC-FIX-1 verdict panel | **10** | `claude-opus-5` | see per-agent file | — | `build/SPEC-FIX-1.jsonl` | `docs/evidence/spec-fix-1/` + `spec-fix-1-panel-cost.txt`. **The panel went 4–1 against the verdict the session then reached, and the session refused anyway.** |
| CH-03 gate reviewers | **2** | `claude-opus-5` | — | — | `build/NIGHT-RUN-FINAL.jsonl` | `docs/reviews/REVIEW_CH-03.md`, `REVIEW_CH-03-round2.md` + 15 runnable probe scripts. **FAIL, then FAIL again — strike 2, escalated.** |
| CH-04 gate reviewer | **1** | `claude-opus-5` | — | — | `build/CH-06.jsonl` | `docs/reviews/REVIEW_CH-04.md` + `ch04-probe/`. **FAIL, 16 findings.** |
| CH-11 shipping audit `wf_44b0dd6c-5e5` | **52** | `claude-opus-5` | **2,625,778** | 916 s | `build/CH-11.jsonl` | 8 dimensions → 44 refuters, one per finding; 13 refuted, 31 survived. Its sharpest finding was against the session that ran it |
| CH-11c shipping sweep `wf_74534735-795` | **21** | `claude-opus-5[1m]` | **2,094,887** | 2,170 s | `build/CH-11c.jsonl` | `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md` — **all 75 findings verbatim from the workflow journal.** 18 refuted, 57 standing |
| CH-12 re-verification `wf_3949a5b7-c7b` | **17** | `claude-opus-5[1m]` | **1,679,590** | 1,623 s | `build/CH-12.jsonl` | 10 auditors re-checking all 75 standing findings against the current files, 7 measuring the facts this chunk needed. 666 tool calls, 0 errors |
| **total** | **103** | | **6,400,255** measured on three fleets | | | |

**These tokens are NOT in `docs/evidence/runs/cost_ledger.csv` and are not part of the
USD 11.6323.** The ledger records the *evaluation arms* — the thing being measured.
Audit subagents are Claude Code sessions' own usage, billed on the coding-agent side, and
they are reported here in tokens rather than folded into a spend figure that means
something else. Conflating the two would understate the arms' cost discipline and
overstate the project's API spend at the same time.

**This class has no trajectory file, and that is a gap in deliverable 4 rather than an
omission from this index.** `tools/export_session.py` captures a *session*; a subagent is
not a session, and the `Agent` tool writes each transcript to a temp path outside the
repository. What ships for every fleet is **the launch prompt verbatim inside the parent
build transcript, the final result verbatim in its task-notification, and the runnable
evidence under `docs/reviews/` or `docs/evidence/`** — and for the 21-agent sweep, a
finding-by-finding transcription generated from the journal rather than written by hand.
It is raised as `QUESTIONS.md` **Q40** with the fix costed.

The coding row is the one that is easy to lose and easy to fake. Those transcripts
live outside the repository in `~/.claude/projects/`, where Claude Code rotates and
prunes them, and they contain deliverable 4's own checklist verbatim — agent
instructions, every tool call, every tool response, retries, and human
interruptions. `tools/export_session.py` captures them; `CLAUDE.md`'s end-of-session
duty 6 makes a chunk **not done** until its transcript is exported.

---

## Models

| Model | Exact id | Where used | Price basis |
|---|---|---|---|
| Claude Opus 5 (1M context) | `claude-opus-5` | every Claude Code build/review session, incl. this one | $5.00 / $25.00 per MTok |
| Claude Haiku 4.5 | **`claude-haiku-4-5-20251001`** | **USED** — every evaluation arm. 2,020 logged calls | $1.00 / $5.00 per MTok |
| Claude Haiku 4.5 (alias) | `claude-haiku-4-5` | probe only, 3 calls. See Q1's correction — the night run pre-registered that this alias 404s; **it does not**, and the dated id is used anyway because an alias does not pin a reproducibility claim | same |
| Claude Sonnet 5 | `claude-sonnet-5` | **USED** — model-sensitivity check only, 20-item subset. 84 calls. **Rejects `temperature` (HTTP 400, measured)**, so it ran at the model default while every haiku arm ran at 0 — a reported asymmetry | $2.00 / $10.00 per MTok |

Prices are Anthropic published list, re-read from the published table on 2026-08-30
rather than recalled, and recorded in every run as `price_basis` +
`price_basis_url`. Source: <https://docs.claude.com/en/docs/about-claude/pricing>.

**Delivery is STANDARD, not batch, and that is a correction to `QUESTIONS.md` Q1.**
Q1 mandated the Message Batches API for its 50% discount; batch is asynchronous with
up to 24h latency and the CHECKPOINT answer was needed inside one overnight run. Every
ledger row records `delivery=standard`, so the doubled unit price is visible in the
evidence rather than assumed away. Q1's batch ruling stands for CH-08's full matrix.

**Measured spend: USD 11.632274 over 2,107 logged runs** (9,509,276 input / 398,764
output tokens), against the USD 18.00 ceiling enforced in `src/runlog.py`.
*Corrected at CH-11c. This read **"spend to date: USD 1.935538 over 1038 logged
runs"**, which was a true measurement of a ledger that has since grown, not a wrong
one: `git log -- docs/evidence/runs/cost_ledger.csv` shows the file held exactly
**1038 rows** at `9786f6c`, the CHECKPOINT re-run, and 2,107 from `bc99ef4` onward.
Those 1038 rows are the `B0` / `B0-agent` / sonnet-subset / probe arms and they sum
to 1.935538 to the last digit. The figure was a snapshot that stopped being the
total; it is corrected rather than deleted. `QUESTIONS.md` **Q39**.*
3 runs carry an EMPTY cost cell rather than a zero — they died before
reporting token counts, and unknown is not the same claim as free.

**Fairness constraint:** every evaluation arm gets the *same* model. What the model
choice limits is generalisability, not the internal comparison — and the
model-sensitivity check turns that limit into a number instead of a caveat.

---

## Tools available to the coding sessions

Claude Code's own harness, and nothing else:

| tool | used for | seen in |
|---|---|---|
| `Bash` / `PowerShell` | every measurement, every git operation, every script run | all 12 transcripts; 226 Bash calls in NIGHT-RUN-FINAL alone |
| `Read` / `Write` / `Edit` / `Glob` / `Grep` | the code and the documents | all 12 |
| `Agent` | the three gate reviewers, as background subagents with zero shared context | `NIGHT-RUN-FINAL.jsonl` (2), `CH-06.jsonl` (1) |
| `Workflow` | the four subagent fleets — SPEC-FIX-1's panel, CH-11's 52, CH-11c's 21, CH-12's 17 | `SPEC-FIX-1`, `CH-11`, `CH-11c`, `CH-12` |
| `TaskOutput` / `TaskStop` | collecting and cancelling background agents | `SPEC-FIX-1` (2), `CH-11c` (4), `CH-06` (1 stop) |
| `AskUserQuestion` | putting a decision to the operator mid-session | `CH-00.jsonl`, `CH-14a.jsonl` — **two occasions in the whole project** |
| `ToolSearch` | loading deferred tool schemas | `CH-06`, `SPEC-FIX-1`, `CH-11c`, `CH-12` |
| `WebFetch` / `WebSearch` | **not used for the corpus.** `www.govinfo.gov` is fetched by `refetch.py` and `src/apiclient.py`, in code, so the fetch is reproducible | — |

**No custom MCP server. No autonomous scheduling. No agent that could commit.** The
session runs under `CLAUDE.md`, a per-chunk prompt committed verbatim in `prompts/`
(three cards are currently untracked — `QUESTIONS.md` **Q41**), and a hard safety rider
that makes `context/` and the root specs read-only to build sessions.

Tools the *solution* agents get are a different and much smaller set, defined per arm in
`agents/`: `B0` gets the instruction text alone, `B0-agent` also gets the section text,
and only the `A1` family gets `cfr_resolve` and the OFR execution procedure. **That
separation is the point of the experiment and it is not blurred here.**


---

## Human direction

The operator (Chinmoy Paul) is the architect: writes the spec and the chunk prompts,
rules on every question raised to `QUESTIONS.md`, and merges `STATUS.md` /
`PROGRESS.md`. Sessions do not certify their own work (hard rule 2). Human decision
points are recorded as they happen — `QUESTIONS.md` Q5 and Q7 in CH-00 were both
put to the operator mid-session and answered before work continued.

Human time per chunk is tracked for the rubric's *human time per task* row; the
blind human-time study (8 items by hand, stopwatched, before seeing gold) is CH-09.

---

## Session log

Newest first. Every build session appends one row here **and** exports its transcript.

### CH-12 · 2026-08-31 · Claude Code · `claude-opus-5` (1M context) · BUILD · **trajectories, the worksheet, and a disclosure claim one grep falsified**

Transcript: `docs/trajectories/build/CH-12.jsonl`.

**No arm was re-run and no model call was made from this session's code.** API spend is
unchanged at **USD 11.6323**, re-derived from `docs/evidence/runs/cost_ledger.csv`.

**What it produced.** Deliverable 4's navigation —
[`docs/trajectories/SELECTION-RULE.md`](docs/trajectories/SELECTION-RULE.md) committed at
`1afc295` **before** anything was selected, and
[`docs/trajectories/INDEX.md`](docs/trajectories/INDEX.md) pointing a judge at the three
files worth opening first. And CH-10's codification worksheet,
[`docs/worksheet/index.html`](docs/worksheet/index.html), generated from **real committed
A1 output** by `docs/evidence/ch12/build_worksheet.py` — self-contained, offline, with a
disclaimer band, a provenance footer, and the 16-of-82 human-checkpoint queue as its own
section.

**The claim that started the chunk.** `PROVENANCE.md` §4 asserted that the
`nistula-assistance-` result *"is cited in this project's README"*. `README.md` contained
**zero** occurrences of `nistula`, `17 blocker` and `github.com`. The sentence was written
**17 h 33 min before the README existed** and was never re-checked. It is a ground-rule-02
disclosure claim, and **one `grep -c` falsifies it.** The README now carries the citation;
the correction is disclosed in `PROVENANCE.md` rather than quietly amended, and
`docs/evidence/ch12/provenance_claim_check.py` prints the claim FALSE at the old commit
and TRUE now, so nobody has to take the correction's word for it.

**Agents used — 17 subagents in workflow `wf_3949a5b7-c7b`, `claude-opus-5[1m]`, plus a second fleet of 36 in `wf_7b927948-32f` that adversarially audited this chunk's own output: 5 auditors and 31 refuters, 3 of which errored. 53 in total.** *The 17 figure was written mid-session and was already incomplete when written — the same structural caveat the token table below carries, and it was the audit fleet itself that pointed it out.*
Ten read-only auditors, one per shipping file, each re-running the CH-11c sweep's own
checks **against the current files rather than against the sweep report** — hard rule 15
applied to the project's own evidence. Seven more measured the facts this chunk needed:
the trajectory inventory, the agent census, the build-session index, the checkpoint
records, the corpus size, the worksheet's source data, and the README claim above.
**666 tool calls, 1,679,590 subagent tokens, 1,623 s, 0 agent errors, 0 empty results.**
No agent could edit a file.

**Re-verifying 75 findings changed the number.** 7 had already been fixed, **14 did not
reproduce**, 54 still stood. So the sweep's headline **57 is 54**, and the three that fell
are recorded rather than dropped. 26 of the 54 were one-line factual corrections inside
this chunk's fence and were applied by a script that asserts, for every one, that the old
text is gone and the new text is present — 26 of 26 verified on disk, line endings
preserved byte-for-byte. `AI-USE.md`'s own agent-class counts were four of them.

**Two agent claims did not survive my own check**, which is the reason the check exists:
a report said `CH-00.jsonl` is the only transcript containing an `AskUserQuestion`
(`CH-14a.jsonl` has one too), and that the CH-03 reviewers left 23 runnable probe scripts
(there are 15 scripts among 23 files). Both were corrected before publishing.

**What this chunk found in its own safety machinery — Q43.** One operator contact address
survives redaction in a shipped trajectory. The scrubber did not fail: it matches
**literals from a pattern file**, and that address is not in the file. `ch00-guard-probe.txt`
proves every scrubber **fires**; **nothing proves the pattern set is complete.** That is
the same defect class as a green test suite, found in the machinery this project uses to
answer ground rule 08. Not fixed here — removing it means rewriting shipped evidence.

Questions raised: **Q40** (the selection rule names an agent class with no trajectories),
**Q41** (three prompt cards untracked and unfixable from inside any fence), **Q42**
(`NIGHT-RUN-FINAL.jsonl` shipped and disclosed nowhere), **Q43**. **Q39** takes a dated
UPDATE with the re-verification table.

- **Measured usage** (from the session transcript's own `usage` records — measured, not
  estimated from character counts). **Snapshot taken before the closing commits**, so the
  true totals are marginally higher. Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id b9978fdb-e017-4911-ab7a-331394e4cff6`:

  | | tokens |
  |---|---|
  | output | 552,139 |
  | input, uncached | 916 |
  | input, cache write | 1,373,511 |
  | input, cache read | 153,863,804 |
  | **total input** | **155,238,231** |
  | assistant turns | 458 |
  | wall-clock | **7,035 s (1.95 h)**, 08:21:12Z → 10:18:27Z |

  Imputed at `claude-opus-5` list price: **USD 789.994630** upper bound with no cache
  discount, **USD 99.324401** cache-adjusted at the assumed 1.25× / 0.10× multipliers. Both
  are printed because the upper bound rests on no assumption. **This is the coding
  agent's cost and it is NOT charged against the USD 18.00 ceiling in `src/runlog.py`**,
  which governs the evaluation arms. Subagent tokens are counted separately in the
  adversarial-audit table above and are **not** in this table.

### CH-11c · 2026-08-31 · Claude Code · `claude-opus-5` (1M context) · BUILD · **five factual corrections, and the sweep that caught a sixth in my own work**

Transcript: `docs/trajectories/build/CH-11c.jsonl` (746 lines, 1,799,806 B — *this read 669 / 1,669,875 until CH-12; the session was re-exported at `57829c1` after its last fix and the line was not refreshed, the same defect as CH-02's below*; the exporter's
redaction sweep found **zero** credentials and rewrote 789 home paths to `~`).

**No arm was re-run and no model call was made from this session's code.** API spend is
unchanged at **USD 11.6323**, re-derived from `docs/evidence/runs/cost_ledger.csv` by this
chunk's own script. The chunk corrected **statements about the work**, never the work.

**The five, all raised by CH-11 and all outside its fence:** `PROVENANCE.md` naming
`claude-sonnet-5` as the model of every arm (**Q35**); the Q19 ruling misattributing its own
pre-registration to `GOOD.md` §11 (**Q32**); `B0′` called compute-matched at a third of A1's
tokens (**Q34**); `CHANGELOG.md`'s non-reproducing **26** (**Q33**); and the secret sweep's
**450 / 81** against the artifact's **462 / 84** (**Q31**).

**Agents used — one workflow, 21 subagents, `claude-opus-5[1m]`, run `wf_74534735-795`.**
Ten read-only auditors, one per shipping file; ten adversarial refuters, one per file, each
told to kill that file's findings and to default to *refuted* when uncertain; one
completeness critic asked what the sweep missed. **971 tool calls, 2,094,887 subagent
tokens, 2,170 s, 0 agent errors, 0 empty results.** No agent could edit a file. Verbatim
output at `docs/evidence/ch11c-sweep/ch11c-agent-sweep.md`, generated from the workflow
journal rather than summarised by hand. **75 findings, 18 refuted, 57 standing** — and a
finding that survives one refuter is not a confirmed defect, which is how it is reported.

**Four things this session checked instead of trusting:**

1. **The chunk card's own supporting counts do not reproduce.** It stated *"19 artifact
   files name haiku; 4 name sonnet, the withdrawn subset only"*. Measured over tracked
   files: **27 and 13**, and the 13 are not the withdrawn subset only — they include the
   model-id probe, `ch00-goldens.md`, `ch14-size/selection-applied.md`,
   `night-run/summary.md` and the ledger. The card's *conclusion* was right and its
   numbers were not, so the correction shipped resting on the ledger instead (**Q37**).
2. **The claim that 450 / 81 was "written before the last three commits" was checked, not
   assumed.** `git log -- docs/evidence/secret-scan/scan.txt` has two revisions: `0f3f4fe`
   printing 450 / 81 and `263ed29` printing 462 / 84. The stale pair was real output, and
   both files now say so rather than being silently aligned.
3. **`GOOD.md` §11 was read and quoted rather than paraphrased**, because the whole of Q32
   turns on what it says. It is frozen; `git diff -- GOOD.md` is clean and the verification
   script asserts it.
4. **A programmatic edit silently converted four files from CRLF to LF**, turning a
   268-line diff into a 5,000-line one under `.gitattributes`' `* -text`. Caught by reading
   `git diff --stat` before committing and reverted byte-exactly. Hard rule 16 is why the
   check happened at all.

**And the finding this session is least comfortable with, recorded because it is the
point.** The corrected `PROVENANCE.md` row this chunk wrote said *"every evaluation arm,
temperature 0"*. **That was false too:** `B0prime` ran at **temperature 1.0**
(`docs/evidence/ch06-a1/B0prime-rep1.json`; best-of-3 self-consistency at 0 is a no-op,
**Q22**), and the withdrawn sonnet arms ran at the model default because sonnet rejects the
parameter. **A session correcting a false claim about the model introduced a new false
claim about the temperature in the same sentence**, and only its own adversarial sweep
caught it. It is disclosed in `PROVENANCE.md` as a second correction to the first.

Four further findings were fixed because the card's §6 names them: a **false gate-pass
claim** (`AI-USE.md`'s NIGHT-RUN heading read *"CH-03 FAILED then FIXED"* where CH-03 is
`reviewed-FAIL ×2 → ESCALATED`), a stale ledger snapshot presented as project spend, a
stale `QUESTIONS.md` entry count in two files, and a temperature-scope claim in the README.
**The remaining 57 are reported and not fixed** — several are Class A, and two of the
affected files are in no chunk's fence (**Q39**).

Questions raised: **Q36** (three protected files still say *compute-matched*), **Q37**,
**Q38** (the fence excludes `PROGRESS.md` that `CLAUDE.md` requires), **Q39**.

- **Measured usage** (from the session transcript's own `usage` records, **248 assistant
  turns** — measured, not estimated from character counts). **Snapshot taken at export
  time**; the session continues for the final commit and push, so the true totals are
  marginally higher. Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id c5f29e31-d471-4f9c-82c2-3d3a7f7de4d5`:

  | | tokens |
  |---|---|
  | output | 294,756 |
  | input, uncached | 496 |
  | input, cache write | 531,752 |
  | input, cache read | 41,927,070 |

  Wall-clock **3,353 s (0.93 h)**, 07:12:45.883Z to 08:08:39.283Z. Subagent tokens are
  counted separately above and are **not** included in this table.

### CH-11 · 2026-08-31 · Claude Code · `claude-opus-5` (1M context) · BUILD · **README, REPRODUCE, and the four files under them**

**Models called against the paid ceiling: NONE.** Zero API calls, zero arms re-run.
Committed spend is **unchanged at USD 11.6323** of 18.00, and
`docs/evidence/runs/cost_ledger.csv` is byte-identical to how this session found it —
hashed before the first commit and again after the last. `prompts/CH-11.md` forbade model
calls; the ledger is the evidence that none were made.

**Arms run: none.** Every figure in the six new files is copied from a committed artefact
and cites its path, or is replayed from those artefacts by `analyse_checkpoint.py`,
`analyse_a1.py` and `run_bscript.py` — all three pure, all three offline.

**Subagents: 52 in one workflow, `claude-opus-5`, effort high, 2,625,778 tokens.**
This is the largest disclosure in this entry and it is made in full.

| | |
|---|---|
| orchestration | one `Workflow` run, id **`wf_44b0dd6c-5e5`**, script `ch11-doc-audit`, 916 s wall-clock, 729 tool uses, 0 errors |
| stage 1 — Audit | **8 agents**, one per dimension, each with zero shared context and read-only: numbers in the results section · numbers everywhere else · mandated structure against `prompts/CH-11.md` §1 · voice against §4 · contradictions against every shipping document · whether `REPRODUCE.md` actually executes · dependencies and licences · scope-fence compliance and omissions |
| stage 2 — Verify | **44 agents, one per finding**, each prompted to **refute** it and defaulting to *refuted* unless it could confirm the defect by opening the files itself. **13 findings were refuted and dropped; 31 survived.** |
| what they could do | read, grep, glob, and run read-only shell commands. **No edits, no network, no model arms.** |
| what was done with the output | every surviving finding was checked by the build session against the artefact a third time before any text changed |

**Their transcripts are not in the repository, and that is a gap.** Hard rule 10 wants
every agent run logged into `docs/trajectories/`; `prompts/CH-11.md`'s fence makes `docs/`
read-only for this chunk. The fence was obeyed. The runs are on disk outside the repo at
`~/.claude/projects/<slug>/subagents/workflows/wf_44b0dd6c-5e5/`, one JSONL per agent plus
`journal.jsonl`, and **`QUESTIONS.md` Q30 asks the architect whether a documentation chunk
should be allowed a directory to put them in.** They are named here rather than left
unmentioned.

**The audit paid for itself, and the sharpest finding was against this session.** The
worked example in the README quoted `2016-09949|1436.3`'s editorial note. My terminal
renders UTF-8 through a cp1252 code page, so `§` and the corpus's curly quotes came back
as `?`. I read that as a decoding artefact **in the corpus**, wrote nine literal U+FFFD
characters into the README, and added a paragraph explaining that the freeze carries
U+FFFD and that reproducing it faithfully was what hard rule 7 demanded. The corpus
contains **zero** U+FFFD: 973 `§` and 755 curly quotes, checked at the byte level. **I
invented a data defect out of my own console encoding and then wrote a principled-sounding
paragraph defending it.** The audit caught it, the bytes settled it, and the paragraph is
gone. Rule 15, on the session that was writing the file about rule 15.

**Tools used, and what each was for:**

| tool | used for |
|---|---|
| `git clone`, `show`, `log`, `ls-files`, `status` | the clean-room clone; dating the Iteration 1 card against the arm it predicted |
| `python -m venv` + `pip install -r requirements.txt` | the fresh environment for the Tier-1 verification — the one step that touched the network |
| `python`, `pytest` | the offline replay, the suite, the import census, the licence-metadata read, the byte-level encoding checks |
| `Workflow` (Claude Code) | the 8 + 44 adversarial audit above |
| `grep`, `sed`, `find` | reading the evidence tree |

**Human direction.** The whole chunk is `prompts/CH-11.md`, issued verbatim and followed.
No question was put to the operator mid-session; six were raised to `QUESTIONS.md` instead
— **Q30** through **Q35** — and each takes the conservative option and continues rather
than blocking.

**Four things this session checked before trusting them:**

1. **The chunk prompt's `764 seconds` was checked, not relayed.** `AI-USE.md` already
   carries a `764` that is `A1-iter1`'s wall-clock, which made the prompt's figure look
   like a transcription slip. It is not: `e12466c` is `02:11:37Z` and the first record of
   `A1-iter1-rep1.jsonl` is `02:24:21.091Z`, so the gap is **764.091 s**. Two unrelated
   quantities agreeing to a tenth of a second, and only one of them is the claim.
2. **Every dependency licence was read out of the installed `dist-info` metadata** in the
   verification venv rather than recalled, and `colorama`'s clause count was checked in
   its own `LICENSE.txt`.
3. **`CONTEXT.md` §3's ⚠️ ban was honoured.** The pilot figures `0.545 / 0.5855 / 0.52`
   and the **+27.3 pp** retrieval gain are marked *provenance-unverified* and forbidden in
   the README until re-derived. They appear nowhere in any file this session wrote, and
   the hot take is carried by in-repo per-class recall instead.
4. **Two numbers this session was about to copy do not reproduce**, and both are now
   `QUESTIONS.md` entries rather than repeated: `CHANGELOG.md`'s *"26 items had samples
   that disagreed"* (the votes file gives **22** — Q33), and two shipping documents
   attributing the restricted-set pre-registration to `GOOD.md` §11, which says the
   opposite (Q32).

- **Measured usage** (from the session transcript's own `usage` records, 320
  assistant turns — measured, not estimated from character counts). **Snapshot taken
  at export time**; the session continues for the final commit and push, so the true
  totals are marginally higher. Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id <uuid>`:

  | | tokens |
  |---|---|
  | output | 361,822 |
  | input, uncached | 640 |
  | input, cache write | 838,411 |
  | input, cache read | 84,111,529 |
  | **total input** | **84,950,580** |

- **Imputed cost — the build subscription is flat-cost to the operator, so this is an
  imputation and is labelled one (never `$0`):**

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **433.798450** |
  | Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **56.344583** |

  Both are printed because the second rests on cache multipliers that were **not**
  re-verified against the published table this session, and an unverified multiplier is
  a claim rather than a measurement (hard rule 15). The upper bound rests on no
  assumption at all.

- **The 2,625,778 subagent tokens of the audit are NOT in the figures above.**
  `ch00_session_cost.py` reads one transcript; the 52 audit agents have their own, under
  `subagents/workflows/wf_44b0dd6c-5e5/`. Counted together the session is roughly
  87.9 M tokens. Stated rather than left for a reader to discover a gap between two
  numbers this file publishes.

- **This session's spend is not charged against the USD 18 ceiling in `src/runlog.py`.**
  That ceiling governs the paid API used by the evaluation arms (`QUESTIONS.md` Q1);
  build-session cost is a flat subscription and is reported here for disclosure, not
  budgeting. **The ceiling's own counter did not move: USD 11.6323, ledger
  byte-identical.**

**Trajectory:** `docs/trajectories/build/CH-11.jsonl`, exported by
`tools/export_session.py` (hard rule 10, end-of-session duty 6). 987 lines,
2,456,849 bytes. Scrubber counts printed with every zero explicit: **0 credential
substitutions of any class, 0 operator-contact substitutions, 3 `KEY=value` env values
redacted, 1,091 home paths rewritten to `~`, 0 lines that stopped being valid JSON.**

### CH-14a · 2026-08-31 · Claude Code · `claude-opus-5` (1M context) · BUILD · **PACKAGING — and the blocker was never a blocker**

**Models called by THIS session: NONE.** Zero API calls, zero tokens against the paid
ceiling. Committed spend is **unchanged at USD 11.6323** of 18.00 and
`docs/evidence/runs/cost_ledger.csv` is byte-identical to how the session found it.
CH-14a forbade model calls; the ledger is the evidence that none were made, and the
clean-clone replay reproduces the same `TOTAL 11.6323` from the extracted zip.

**Subagents: none.** Every step ran in the main session.

**Arms run: none.** Every number in this session's evidence is either measured from
`git` plumbing and the filesystem, or replayed from committed artefacts by
`analyse_checkpoint.py` and `analyse_a1.py` — both pure, both offline.

**Tools used, and what each was for:**

| tool | used for |
|---|---|
| `git archive`, `ls-tree`, `rev-list`, `cat-file`, `write-tree` | measuring the real submission artifact and sweeping all **462** text blobs of history across **84** commits (`docs/evidence/secret-scan/scan.txt`) |
| `python -m venv` + `pip install pytest` | the clean-room interpreter — the one step that touched the network, before the offline phase began |
| `pytest` | 10 new probe tests; the full suite in three environments |
| filesystem + `zipfile` | building and extracting the submission archive |

**Correction, 2026-08-31 (CH-11c).** This row read *"all 450 blobs of history"* until
CH-11c. The generating artifact `docs/evidence/secret-scan/scan.txt` says **462 text blobs
across 84 commits**, and under hard rule 14 the artifact wins. **The two figures are not a
contradiction and neither was invented**: the sweep was committed twice, and this summary
was written against the earlier run. `git log -- docs/evidence/secret-scan/scan.txt` shows
`0f3f4fe` (repository `f0a246b1`, **450 blobs / 81 commits**) and then `263ed29`
(repository `2453998f`, **462 / 84**) — three commits and twelve blobs later. **The verdict
is PASS with 0 findings on either scope.** `QUESTIONS.md` **Q31**; re-derivation at
`docs/evidence/ch11c-sweep/`.

**Human direction.** The queue was fixed in `prompts/CH-14a.md`, committed verbatim.
One question was put to the architect mid-session — whether to raise the 300-file guard
that was refusing every commit — **and was declined without a ruling**. The session then
took the conservative-and-continue path the prompt specifies for unruled ambiguity and
recorded the deviation as **Class A in `QUESTIONS.md` Q28**, awaiting ratification,
rather than either shipping nothing or changing a guard quietly.

**Three findings this session made against its own side of the project:**

1. **`QUESTIONS.md` Q25's submission blocker does not exist.** The 50 MB cap is on the
   uploaded zip; the zip is 10.18 MB at `bc99ef4` (`docs/evidence/ch14-size/inventory.md`; re-measured **12.51 MB at CH-12's last commit `b39cd0c`**, `docs/evidence/ch12/archive-size.txt`). Q25 measured the uncompressed tree and its four
   proposed remedies — compress, relocate, sample, or unseal `data/` — were all
   unnecessary. `src/arms.py::bundle()`'s promise that *"EVERY RECORD SURVIVES"* is kept.
2. **A test written by this session was broken inside the submission.**
   `test_the_real_repository_is_under_the_real_limit` calls `git write-tree`; an
   extracted zip is not a git repository. A test written to prove the archive is under
   cap failed in the archive. Found by running the suite from the extraction — the one
   environment nobody had tried — alongside a pre-existing CH-02 test with the same
   shape of defect.
3. **This session's own secret scanner reported 74 false findings before it worked.**
   It was matching the credential detectors' own regex source. Rebuilt to classify by
   the match rather than the path, with declared exceptions and staleness reporting.
   The first version's output is preserved in git history.

**Trajectory:** `docs/trajectories/build/CH-14a.jsonl`, exported by
`tools/export_session.py` (hard rule 10, end-of-session duty 6).

### CH-06 → CH-08 → CH-09 · 2026-08-31 · Claude Code · `claude-opus-5` · BUILD, UNATTENDED · **THE ADVANCED SOLUTION**

One unattended session working a pre-registered queue. It produced the project's
first advanced solution, without which the entry is invalid under the hackathon's
own rule that *"every valid entry must present both a baseline solution and an
advanced solution."*

**Models called by THIS session, all logged through `src/runlog.py`:**

| id | calls | USD | why |
|---|---:|---:|---|
| `claude-haiku-4-5-20251001` | 1,069 | 9.6967 | every A1 arm and both ablations, temperature 0 — the same model as every baseline (`CONTEXT.md` §4) |

**Arms run by this session, per-arm, from the ledger:**

| arm | calls | input tok | output tok | USD | wall s | unknown-cost rows |
|---|---:|---:|---:|---:|---:|---:|
| `A1` | 249 | 4,006,662 | 265,354 | 5.3334 | 2516 | 0 |
| `A1-iter1` | 82 | 944,767 | 67,840 | 1.2840 | 764 | 0 |
| `A1-minus-tool` | 164 | 1,158,758 | 51,746 | 1.4175 | 665 | 0 |
| `B0prime` | 492 | 1,377,402 | 4,288 | 1.3988 | 505 | 0 |
| `B0-agent-currenttext` | 82 | 259,727 | 656 | 0.2630 | 81 | 0 |
| **this session** | | | | **9.6967** | | |

**Subagents: one.** An independent adversarial **CH-04 gate reviewer**, `claude-opus-5`, spawned with zero shared context and given only `CLAUDE.md`, `CONTEXT.md` §7, `plan.md`'s CH-04 card and the diff — explicitly *not* this
project's own account of its work. It returned **FAIL with 16 findings**, reimplemented the scorer from the specification prose alone, and mutation-tested `src/score.py` sixteen times, restoring it byte-for-byte after each. Its verdict is `docs/reviews/REVIEW_CH-04.md`; its probes are kept at `docs/reviews/ch04-probe/`. **Nothing it found was taken on trust** — finding F3 was independently checked against the repository before this session acted on it.

**Tools the agent was given, and whether it used them.** `cfr_resolve` was exposed as a real Anthropic tool-use schema rather than pre-computed into the prompt, specifically so that *use* could be counted rather than assumed. It was called and the calls are in the trajectories. The measured availability-vs-use-vs-agreement gap is in `docs/evidence/ch06-a1/a1-result.txt`.

**Human direction: none during the run.** The queue was fixed in `prompts/CH-06.md`, which is committed. Every ambiguity that arose was written to `QUESTIONS.md` (Q20–Q24) and the conservative option taken, rather than self-authorised — including **Q21**, a material defect in a shipped capability that this session declined to fix because the defect was discovered *through the fact that it cost the headline number a point*.

**One published number was retracted by this session, seven minutes after it was published.** `QUESTIONS.md` **Q24** asserted a run duration that had been estimated from a sense of how much work had happened rather than read from the ledger's own `wall_clock_s` column. It was wrong by a factor of eight and the scheduling contingency built on it was unnecessary. The entry is kept unedited with the retraction beside it.

**Cost: USD 9.6967 for this session; USD 11.6323 committed in total against the 18.00 ceiling**, 2,107 logged runs, 3 of unknown cost carrying an empty cell rather than a zero.

### NIGHT-RUN · 2026-08-31 · Claude Code · `claude-opus-5` · BUILD, UNATTENDED · **CH-03 reviewed-FAIL ×2 → ESCALATED · CHECKPOINT GREEN**

One unattended session, roughly six hours, working a pre-registered queue with the
operator asleep. Transcript: `docs/trajectories/build/NIGHT-RUN-CHECKPOINT.jsonl`
(1,348 lines, 3.1 MB; the exporter's redaction sweep found **zero** credentials).

**Models called, all logged through `src/runlog.py`:**

| id | calls | why |
|---|---:|---|
| `claude-haiku-4-5-20251001` | 951 | every evaluation arm, 3 reps, temperature 0 |
| `claude-sonnet-5` | 84 | the 20-item model-sensitivity subset, 1 rep |
| `claude-haiku-4-5` | 3 | the alias probe that disproved a pre-registered "fact" |

**Subagents: two, both adversarial CH-03 gate reviewers with zero shared context.**
The first was stopped by a crash before writing its verdict file; its seven runnable
probes and two RED kept tests survived on disk, the build session re-derived every
finding independently before acting, and the provenance weakness is stated at the top
of `docs/reviews/REVIEW_CH-03.md` rather than glossed. The second re-reviews the fix.

**What the first reviewer found, and why it is the most valuable output of the run.**
The eval set this project built specifically to be unbeatable by a trivial script was
**beatable by a trivial script**: negatives were chosen as the sorted-first
count-matched sibling, so a six-line label-blind program reading only `frdoc` and
`section` — no model, no CFR text, no instruction text — scored **0.8158**, beating
the `B0-agent` baseline by 17 points. `CONTEXT.md` §8 had guarded the *count*; nobody
had guarded the *selection*. Fixed, and the probe flips: **0.8158 → 0.5610**, ordering
bias 36/50 (p = 0.0026) → 25/50 (p = 1.0000). The first CHECKPOINT's numbers were
computed on the defective set and are **withdrawn, not deleted** —
`docs/evidence/checkpoint/withdrawn/`.

**Human direction: none during the run.** Every decision that could have blocked was
pre-registered in `prompts/NIGHT-RUN.md`, and the four questions that arose anyway
(Q15–Q18) were recorded as Class A for the architect rather than self-authorised —
including three defects in `CONTEXT.md` itself, which is LAW and which a build session
does not edit.

**Cost: USD 1.94 of the 18.00 ceiling**, 1,038 logged runs, 3 of unknown cost carrying
an empty cell rather than a zero.

### SPEC-FIX-2 · 2026-08-31 · Claude Code · `claude-opus-5` · BUILD (spec-edit scope) · **APPLIED**

- **Scope:** apply the architect's `QUESTIONS.md` Q11 ruling — which accepted SPEC-FIX-1's
  refusal in full — to `CONTEXT.md`, and clear Q13's housekeeping. `CONTEXT.md` went to
  **v1.1**; **no number moved and the attributor was not re-run**. Written:
  `docs/evidence/spec-fix-2/` (`applied.md`, a re-runnable verifier and its committed
  output), `QUESTIONS.md` Q11 ruling / Q13 closed / **Q14 raised**, `STATUS.md`,
  `PROGRESS.md`.
- **Trajectory:** `docs/trajectories/build/SPEC-FIX-2.jsonl`.

- **NO SUBAGENTS WERE RUN IN THIS CHUNK — and that is a finding, not an omission.**
  `prompts/SPEC-FIX-2.md` forbade a panel in terms, citing SPEC-FIX-1's own disclosure
  immediately above: that its ten-agent panel consumed **55%** of that chunk's spend, voted
  **4–1 for the answer the session correctly rejected**, and that *"a cheaper panel would
  have bought it too."* The instruction was followed. **This session's total is 11.05 M
  input tokens against SPEC-FIX-1's 42.41 M combined — a 3.8× reduction on a chunk of
  comparable stakes.** Recorded here because hard rule 13 requires disclosing what was
  used, and the honest disclosure this time is *nothing beyond the coding agent itself*.

- **Measured usage** (from the session transcript's own `usage` records — measured, not
  estimated from character counts). **Snapshot taken before the closing commits**, so the
  true totals are marginally higher; the same structural caveat every prior chunk recorded.
  Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id a9ecc0ec-dabc-403e-8ae1-3dd27de278fc`;
  committed output: `docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt`.

  | | tokens |
  |---|---|
  | output | 132,805 |
  | input, uncached | 204 |
  | input, cache write | 252,525 |
  | input, cache read | 10,797,901 |
  | **total input** | **11,050,630** |
  | assistant turns | 102 |

  *Corrected at CH-14b, and the old row is named rather than deleted.* Every row above
  and both cost bases below previously read a **pre-close snapshot** — output 126,862 ·
  uncached 198 · cache write 250,800 · cache read 10,327,144 · total 10,578,142 · 99
  turns · USD 56.062260 / 9.903612 — which the committed artifact this entry cites has
  never carried. `git log -- docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt`
  returns exactly one commit, `28a59e3`, holding the figures now shown. The gap is
  3 turns and 472,488 input tokens: the closing commits the caveat above warns about.
  **The defect was not the snapshot; it was quoting pre-close figures beside a
  post-close artifact and calling that artifact the source.** No result moves — this is
  the coding agent's own usage and is not charged against the USD 18 arms ceiling.
  Re-verification: `docs/evidence/ch14b/reverify-before.txt`.

- **Imputed cost** — the same two bases as every prior chunk, and for the same reason: the
  cache multipliers are assumed and were not re-verified this session, so the
  assumption-free upper bound is printed beside them, never instead.

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **58.573275** |
  | Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **10.298377** |

- **Against the economy instruction — the cheapest chunk in the project, and still a miss.**
  `prompts/SPEC-FIX-2.md` set a target of **under 5 M input tokens**. This session used
  **11.05 M — 2.21× over**. It is nonetheless the lowest figure any chunk has recorded
  (CH-00 21.72 M · CH-01 41.09 M · CH-02 42.21 M · SPEC-FIX-1 19.15 M coding + 23.25 M
  panel), and
  the saving came entirely from not convening a panel. **10.80 M of the 11.05 M is cache
  read** — the `CLAUDE.md` read-order duty (constitution, a 20 KB verdict, five long
  `QUESTIONS.md` entries, `CONTEXT.md`, `STATUS.md`, `PROGRESS.md`) re-presented as cached
  context across 102 turns. That is structural for any session under this constitution, and
  a sub-5 M target may not be reachable while the read order stands; three self-inflicted
  retries (two here-documents that mangled shell escaping, and a verifier check that was
  itself wrong on its first run) account for the rest, and they were mine.

- **Two measurement caveats, both pre-existing, both still unfixed and both stated rather
  than smoothed:**
  1. `docs/evidence/ch00_session_cost.py` hardcodes the header `CH-00 BUILD SESSION COST`,
     so the committed output carries that header even though it was run against this
     session. **The `transcript` line is the discriminator.** The script is outside this
     chunk's scope fence and was **not** edited; the committed file states this at the top.
  2. That script writes **CRLF** into a repository whose `.gitattributes` is `* -text`. The
     output was normalised to LF before staging, as CH-02 and SPEC-FIX-1 also had to do.
     **This chunk's own verifier fixes the defect for itself** in one line
     (`sys.stdout.reconfigure(newline="\n")`), which is the fix the earlier chunks
     described but could not apply inside their fences.

- **No model was invoked by the code.** SPEC-FIX-2 ran no arm, wrote no `src/runlog.py`
  row, and charged nothing against the USD 18 API ceiling in `QUESTIONS.md` Q1. The only
  model in this chunk is the coding agent itself.

### SPEC-FIX-1 · 2026-08-31 · Claude Code · `claude-opus-5` · BUILD (spec-edit scope) · **REFUSED**

- **Scope:** judge whether `prompts/SPEC-FIX-1.md`'s correction to `CONTEXT.md` §8's
  completeness definition is a legitimate spec fix or goalpost-moving, and apply it **only
  if legitimate**. **Verdict: GOALPOST-MOVING. No spec edit was made.** Written:
  `docs/evidence/spec-fix-1/` (verdict, recompute, four scripts and their committed
  output) and `QUESTIONS.md` Q11–Q13.
- **Trajectory:** `docs/trajectories/build/SPEC-FIX-1.jsonl`.
- **Wall-clock:** first turn 18:18:57 UTC → last 19:01:16 UTC = **42.3 min**.

- **⚠️ THIS SESSION USED SUBAGENTS — the first chunk in the project to do so, and they are
  logged here because hard rule 10 admits no exceptions.** An adversarial panel of **ten**
  `claude-opus-5` subagents was run as a single workflow (run `wf_5260a72c-01a`,
  **24.9 min** wall-clock, 384 assistant turns, 206 tool calls, 0 errors):

  | role | n | what it was asked for |
  |---|---:|---|
  | `recount:{regex,fields,sampling}` | 3 | independently count the three claimed classes by three different methods, and name every class the architect omitted |
  | `judge:{prosecutor,defender,counterfactual,gate-integrity,process}` | 5 | judge the correction through five distinct lenses; the prosecutor was instructed to default to GOALPOST-MOVING under uncertainty |
  | `harder:{per-doc,correctness}` | 2 | design gate metrics that are *strictly harder* than the proposal and compute them |

  **Panel tally: 4 LEGITIMATE / 1 GOALPOST-MOVING. The majority was not adopted.** The
  decisive artefact — the sabotage control — came from the lone dissenter, and **no panel
  number reached the verdict without being rebuilt in-repo first** (hard rule 15):
  `spec_fix_1_sabotage.py` asserts its own replay of `CONTEXT.md` §8 reproduces the frozen
  record with 0 mismatches of 8,752 *before* it draws any comparison. Where the panel's
  class counts differ from this session's, both are published in `verdict.md` §Q1.

- **Measured usage — reported in three rows, because the coding session and the panel are
  measured by different scripts and neither total is quoted alone.** Main session read
  from its own transcript's `usage` records; panel read from the ten subagent transcripts.
  Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id 18eb2b78-55e3-46e0-85af-928de9245d32`
  and
  `python docs/evidence/spec-fix-1/spec_fix_1_agent_cost.py --dir <workflow transcript dir>`;
  committed output: `docs/evidence/spec-fix-1/spec-fix-1-session-cost.txt` and
  `spec-fix-1-panel-cost.txt`.

  | | output | total input | assistant turns |
  |---|---:|---:|---:|
  | coding session | 248,015 | 19,152,452 | 136 |
  | **adversarial panel (10 agents)** | **111,349** | **23,254,519** | **384** |
  | **combined** | **359,364** | **42,406,971** | **520** |

  Snapshot taken before the closing commits, so the true totals are marginally higher —
  the same structural caveat CH-00, CH-01 and CH-02 recorded.

- **Imputed cost** — same two bases as every prior chunk, and for the same reason: the
  cache multipliers are assumed and were not re-verified this session, so the
  assumption-free upper bound is printed beside them, never instead.

  | Basis | coding session | panel | **combined** |
  |---|---:|---:|---:|
  | Upper bound — all input at full list, no cache discount | 101.962635 | 119.056320 | **USD 221.018955** |
  | Cache-adjusted — cache write 1.25×, cache read 0.10× | 18.254045 | 24.444148 | **USD 42.698193** |

- **The panel cost more than the coding session did, and that is the honest headline.**
  23.3 M input tokens against 19.2 M — **55% of this chunk's total spend bought a second
  opinion this session then overruled 4–1.** It is recorded rather than netted away
  because the alternative reading — that ten agents agreeing would have made the verdict
  right — is exactly the failure this project exists to expose. What the panel actually
  bought was **one** idea: the prosecutor's sabotage control. That single control is what
  turned an arguable judgement call into a disproof, and on that basis the spend was worth
  it — but a cheaper panel would have bought it too, and a future chunk should say so
  before spending.

- **Two known measurement caveats, both stated rather than smoothed:**
  1. `docs/evidence/ch00_session_cost.py` hardcodes the header string `CH-00 BUILD SESSION
     COST`; the committed output therefore carries that header even though it was run
     against this session. **The `transcript` line is the discriminator.** The script lives
     outside this chunk's scope fence and was not edited.
  2. That script writes **CRLF** under Windows, in a repository whose `.gitattributes` is
     `* -text`. The committed output was normalised to LF before staging. CH-02 recorded
     the same defect; it is still unfixed, and it is a one-line fix for whichever chunk
     owns `docs/evidence/ch00_session_cost.py`.

- **No model was invoked by the code.** SPEC-FIX-1 ran no arm, wrote no `src/runlog.py`
  row, and charged nothing against the USD 18 API ceiling in `QUESTIONS.md` Q1. The only
  models in this chunk are the coding agent and the ten panel agents, all disclosed above.

### CH-02 · 2026-08-30 · Claude Code · `claude-opus-5` · BUILD

- **Scope:** govinfo FR `<AMDPAR>` carry-forward attributor and the count-matched pair
  yield — `src/attribute_amdpars.py`, `tests/test_attribute_amdpars.py`, `refetch.py`,
  the `data/amdpars/` freeze and `docs/evidence/ch02-attributor/`.
- **Trajectory:** `docs/trajectories/build/CH-02.jsonl` (709 lines, 1,689,144 B;
  660 home-path substitutions, every other scrub category an explicit 0).
- **Wall-clock:** measured on the shipped trajectory, first assistant turn
  `2026-08-30T14:43:21.021Z` → last `2026-08-30T18:16:43.050Z` = **213.4 min**, against
  the ~3 h unattended window `prompts/CH-02.md` allowed. **That is over the window, not
  under it.** *Corrected at CH-14b: this read "14:43:18 → 15:30:55 = 47.6 min", which is
  the span of the **first** export (`215052e`, measured 14:43:21.021Z → 15:30:45.240Z =
  47.4 min, 241 turns). The session was re-exported at `940c0b9` and the sentence was
  not. The claim as it stood said the chunk beat its window roughly fourfold; measured
  against the record it cites, it ran past it. The number was corrected in the direction
  that costs the chunk.*
- **Measured usage** (241 assistant turns, read from the transcript's own `usage`
  records — measured, not estimated). Snapshot taken at the export; the commits that
  land these numbers are necessarily not in them, so the true totals are marginally
  higher — the same structural caveat CH-00 and CH-01 recorded. Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id 50cc446c-9e84-43d2-be94-da74bc7545b7`;
  committed output: `docs/evidence/ch02-attributor/ch02-session-cost.txt`.

  | | tokens |
  |---|---|
  | output | 515,671 |
  | input, uncached | 482 |
  | input, cache write | 627,283 |
  | input, cache read | 41,584,976 |
  | **total input** | **42,212,741** |

  *Corrected at CH-14b.* These rows previously read output 514,051 · uncached 478 ·
  cache write 626,057 · cache read 40,957,406 · total 41,583,941 · 239 turns · USD
  220.770980 / 37.245224 — no row of which appears in the artifact named above, and
  `git log` on that artifact returns one commit, `215052e`. **241 turns is the snapshot
  the artifact holds, and the session did not stop there:** `CH-02.jsonl` was
  deliberately re-exported at `940c0b9` to cover the later commits and now carries
  **268** assistant turns. Both numbers are true of different moments; only one of them
  is what this table's source measured.

- **Imputed cost** — same two bases as CH-00 and CH-01, and for the same reason: the
  cache multipliers are assumed and were not re-verified this session, so the
  assumption-free upper bound is printed beside them, never instead.

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **223.955480** |
  | Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **37.607192** |

- **Against the economy instruction — a miss, and smaller than CH-01's but still a
  miss.** `prompts/CH-02.md` said *"this chunk downloads far less data than CH-01 did.
  Do not re-parse the whole corpus."* The download was indeed far smaller — 272 MB of
  FR issues against CH-01's 824 MB — but input tokens came out at **42.2 M** against
  CH-01's 41.1 M, i.e. **2.7% higher**, not lower. *(Corrected at CH-14b from 41.6 M and
  1.2%, which were derived from the superseded table above; CH-01's 41,093,185 does
  match its own artifact.)* Attributable causes, in order of
  size and stated plainly rather than rounded away:

  1. **Hand-computing 97 golden AMDPAR elements** (hard rule 4) required dumping three
     whole documents' instruction text into the session and reasoning over every line.
     That is the single largest block of tokens in the run and it is **inherent to the
     chunk** — a golden read by the parser is not a golden.
  2. **Four full corpus extracts** rather than one: the first measurement, then the
     citation-resolution fix, then the determinism fix, then the fixed-point round.
     Each re-parse is cheap in wall-clock (11 s) but each printed a report.
  3. **Two `cat > file <<'EOF'` heredocs failed** on command length with an unhelpful
     `unexpected EOF` and had to be re-issued through the Write tool. Self-inflicted,
     ~2 turns, and the lesson is recorded here rather than in the next session's
     surprise.
  4. **The stdout of both evidence scripts was captured under the Windows console
     codepage** on the first attempt, producing a cp1252 em-dash and CRLF endings in a
     `* -text` repository. Caught before the first commit that touched those files, so
     unlike CH-01 the history carries no CRLF — but it cost a regeneration cycle.

  Causes 3 and 4 are self-inflicted and are recorded as such in `PROGRESS.md` too.
  Cause 1 is the chunk doing what it was asked to do.

- **No model was invoked by the code.** CH-02 is a deterministic parser: no arm ran, no
  `src/runlog.py` row was written, and nothing was charged against the USD 18 API
  ceiling in `QUESTIONS.md` Q1. The only model in this chunk is the coding agent whose
  transcript is exported above.

### CH-01 · 2026-08-30 · Claude Code · `claude-opus-5` · BUILD

- **Scope:** govinfo ECFR `<EDNOTE>` harvest — `src/harvest_ednotes.py`,
  `tests/test_harvest_ednotes.py`, `refetch.py`, the `data/ednotes/` freeze and
  `docs/evidence/ch01-pool/`.
- **Trajectory:** `docs/trajectories/build/CH-01.jsonl` (672 lines, 1,433,689 B;
  772 home-path substitutions, every other scrub category an explicit 0).
- **Wall-clock:** first turn 13:51:08 UTC → last 14:30:36 UTC = **39.5 min**.
- **Measured usage** (237 assistant turns, read from the transcript's own `usage`
  records — measured, not estimated). Snapshot taken at the final export; the commit
  that lands these numbers is necessarily not in them, so the true totals are
  marginally higher — the same structural caveat CH-00 recorded. Regenerate with
  `python docs/evidence/ch00_session_cost.py --session-id 577b7ed1-d9e2-49ed-aaf2-53f1454e71ce`;
  committed output: `docs/evidence/ch01-pool/ch01-session-cost.txt`.

  | | tokens |
  |---|---|
  | output | 348,831 |
  | input, uncached | 474 |
  | input, cache write | 546,507 |
  | input, cache read | 40,546,204 |
  | **total input** | **41,093,185** |

- **Imputed cost** — same two bases as CH-00, and for the same reason: the
  cache multipliers are assumed and were not re-verified this session, so the
  assumption-free upper bound is printed beside them, never instead.

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **214.186700** |
  | Cache-adjusted — cache write at 1.25×, cache read at 0.10× input list | **32.411916** |

- **Against the economy instruction — a miss, stated plainly.** `prompts/CH-01.md`
  asked for *"a fraction of"* CH-00's ~26 M input tokens. This session used
  **41.1 M**, about **1.89×** CH-00's measured 21.72 M rather than a fraction, and 32.41 against 22.51
  cache-adjusted. Attributable causes, in order of size: a 824 MB download and two
  full-corpus re-parses (the extraction plus the determinism proof) that produced
  long tool outputs across many turns; a `sed -i` that converted every `\n` escape
  in the test file to a real newline and cost a restore-and-reapply cycle; and a
  CRLF-on-a-`* -text`-repo mistake that had to be found and normalised. The first
  was inherent to the task; the second and third were self-inflicted and are
  recorded as such in `PROGRESS.md`.

### CH-00 · 2026-08-30 · Claude Code · `claude-opus-5` · BUILD

- **Scope:** repository initialisation, canonical files, `src/runlog.py`,
  `tools/export_session.py`, `.githooks/pre-commit`.
- **Trajectory:** `docs/trajectories/build/CH-00.jsonl`
- **Measured usage** (from the session transcript's own `usage` records,
  144 assistant turns — measured, not estimated from character counts).
  **Snapshot taken at export time**; the session necessarily continues for the
  final commit and push, so the true totals are marginally higher. Regenerate with
  `python docs/evidence/ch00_session_cost.py`:

  | | tokens |
  |---|---|
  | output | 315,403 |
  | input, uncached | 288 |
  | input, cache write | 654,586 |
  | input, cache read | 21,069,904 |
  | **total input** | **21,724,778** |

- **Imputed cost — the build subscription is flat-cost to the operator, so this is
  an imputation and is labelled one (never `$0`):**

  | Basis | USD |
  |---|---|
  | Upper bound — all input at full list, no cache discount | **116.508965** |
  | Cache-adjusted — cache write at 1.25x, cache read at 0.10x input list | **22.512630** |

  Both are reported because the second depends on cache-tier multipliers that were
  **not** re-verified against the published table in this session, and an unverified
  multiplier is a claim, not a measurement (hard rule 15). The upper bound rests on
  no assumption at all. Working: `docs/evidence/ch00-session-cost.txt`.

- **Note:** this session's spend is *not* charged against the USD 18 ceiling in
  `src/runlog.py`. That ceiling governs the **paid API** used by the evaluation arms
  (`QUESTIONS.md` Q1). Build-session cost is a flat subscription and is reported here
  for disclosure, not budgeting. Conflating the two would misstate both.
