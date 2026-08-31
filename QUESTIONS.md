# QUESTIONS.md — every ambiguity and every ruling, verbatim

Hard rule 1: spec ambiguous, incomplete or contradictory → stop that item, write it
here with the options seen, continue unblocked work. **Never assume.** Stopping on a
real ambiguity is success, not failure.

Newest questions are appended at the bottom. Nothing here is ever deleted; a
withdrawn ruling is marked WITHDRAWN and kept.

---

## Q1 - Model access for the evaluation arms
Raised: CH-00, 2026-08-30. Status: ANSWERED by OPERATOR, 2026-08-30.

Question: the eval needs ~750 programmatic model calls (3 arms x 3 reps x ~84
items). Claude Code's subscription cannot be called from a script.

RULING (revised 2026-08-30 after real pricing was checked): paid Anthropic API,
operator ceiling USD 20 HARD.
Model: claude-haiku-4-5, THE SAME MODEL FOR EVERY ARM (fairness - CONTEXT.md
section 4). Delivery: MESSAGE BATCHES API (50% discount; the whole eval is
non-latency-sensitive, which is what batch is for). Key lives in .env,
git-ignored, never printed or committed.

Measured budget, at published list prices (Haiku 4.5 = $1.00/M in, $5.00/M out):
  full matrix ~2,520 calls = 11.8M in / 1.26M out
  standard  $18.14   batched  $9.07
  plan: ~$9 matrix + ~$5 rerun reserve + ~$3 model-sensitivity + ~$3 slack

MODEL-SENSITIVITY CHECK (~$2, run AT THE CHECKPOINT, not at the end): re-run B0 and
B0-agent on claude-sonnet-5 over a 20-item subset. Purpose is twofold - it reports
whether the gap holds across model tiers, which almost no entrant will have; and it
guards against a FALSE RED, where a weak model fails to use the CFR text and we kill
a sound project on cheap inference. If Haiku shows no gap and Sonnet does, that is a
finding, not a failure.

HARD SPEND CEILING IN CODE: the run logger already computes imputed USD per run. It
maintains a cumulative total and REFUSES to start a run that would cross USD 18,
printing the ledger. A budget discovered after it is spent is not a budget.

Earlier figures in this project's history were wrong in both directions and are
withdrawn: USD 20-30 (too low - counted only 3 arms x 3 reps, not B0-prime, A1's
multi-turn calls, or ablations) and USD 150-250 (relayed from an audit without
verification; ~3x the measured figure).

Rationale, recorded because it is a judged decision:
 (a) "cost per task" is required by the PDF's results table. A paid API makes it a
     measured figure rather than an imputation. Only two repositories on GitHub
     currently report it.
 (b) Free-tier rate limits risk stretching a 20-minute eval into hours on a
     38-hour clock.
 (c) Haiku rather than Sonnet, forced by the USD 20 ceiling - and the honest risk
     is stated rather than hidden. A WEAKER model produces a WEAKER baseline and
     therefore a LARGER measured gap, which is the "baseline set up to fail"
     pattern judges are explicitly told to look for. Two things answer it, and
     both are cheaper than silence:
       - FAIRNESS IS UNAFFECTED. Every arm gets the same model. What the model
         choice limits is generalisability, not the internal comparison, and the
         README says so in those words.
       - THE SENSITIVITY CHECK MEASURES IT. Re-running B0 and B0-agent on
         claude-sonnet-5 over 20 items turns the objection into a number: the gap
         either holds across tiers or it does not, and either result ships.

Blocks: the CHECKPOINT only. CH-01..CH-04 need no model; the B-script arm needs
none at all.

**CH-03 CORRECTION, 2026-08-31 - measured, and the pre-registered fact was WRONG.**
`prompts/NIGHT-RUN.md` states as a pre-registered fact not to be rediscovered that
*"the alias `claude-haiku-4-5` is **not** on this account and will 404."* Hard rule 15
required checking it before relaying it. **It was checked and it is false.** All three
ids were called through `RunLogger`; evidence
`docs/evidence/ch03-model-id/model-id-probe.txt`, script beside it:

| id called | temperature | result |
|---|---|---|
| `claude-haiku-4-5` (the alias Q1 names) | 0.0 | **HTTP 200**, `in=14 out=4`, USD 0.000034 |
| `claude-haiku-4-5-20251001` (the dated form) | 0.0 | **HTTP 200**, `in=14 out=4`, USD 0.000034 |
| `claude-sonnet-5` | 0.0 | **HTTP 400** - "`temperature` is deprecated for this model" |
| `claude-sonnet-5` | omitted | **HTTP 200**, `in=18 out=4`, USD 0.000076 |

Two consequences, both acted on rather than filed:

1. **The dated id is used anyway, and the reason is now the right one.** Q1's alias
   works, so nothing is broken - but a reproducibility claim that pins "haiku 4.5"
   by a floating alias is not pinned at all. Every arm calls
   `claude-haiku-4-5-20251001`. `src/runlog.py` gains that exact string in `PRICES`
   at the same published list price as the alias (Class B; a second spelling of one
   price, not a new price). Had the night run's claim been taken on trust the outcome
   would have been identical - which is precisely why it needed checking, since a
   claim that happens not to bite is indistinguishable from a true one until it does.

2. **`claude-sonnet-5` rejects `temperature` outright, and that one WOULD have bitten**
   - the model-sensitivity subset is a CHECKPOINT deliverable and it would have failed
   HTTP 400 on its first call. `src/apiclient.py` now treats `temperature=None` as
   "omit the field". **The asymmetry this creates is a reported limitation, not a
   hidden one:** the haiku arms sample at `temperature=0`, the 20-item sonnet subset
   at the model's default. Fairness inside the primary comparison is untouched (every
   primary arm is the same model at the same temperature); what it limits is the
   cross-tier sensitivity reading, and the README says so in those words.

**Delivery, corrected from Q1's own ruling.** Q1 mandates the Message Batches API for
its 50% discount. `prompts/NIGHT-RUN.md` overrides it for the CHECKPOINT: batch is
asynchronous with up to 24h latency and the checkpoint answer is needed tonight. The
CHECKPOINT therefore runs **standard** delivery and the ledger records
`delivery=standard` on every row, so the doubled unit price is visible in the evidence
rather than assumed away. Q1's batch ruling stands for CH-08's full matrix.

**CH-00 verification note (hard rule 15).** Q1's arithmetic was independently
recomputed before being encoded in `src/runlog.py`: 11.8M x $1.00 + 1.26M x $5.00 =
$18.10 standard, $9.05 batched, against Q1's $18.14 / $9.07 — agreement to 0.2%,
the residue being exact token counts versus rounded millions. **Confirmed, not
merely repeated.** The prices themselves were re-read from the published table
rather than recalled. Working: `docs/evidence/ch00-goldens.md`.

---

## Q2 - Submission form mechanics
Raised: CH-00, 2026-08-30. Status: ANSWERED by OPERATOR, 2026-08-30.

The HackerEarth submission form has exactly four required fields:
  1. Title            - short, descriptive
  2. Description      - rich text, supports formatting and links
  3. Video URL        - a LINK, not an upload
  4. Source Code      - an UPLOADED FILE (zip). MAX 50 MB.
Plus "Save as Draft" alongside "Submit".

BINDING CONSEQUENCES - these are spec, not advice:

C1. 50 MB ZIP CAP. The uploaded zip is the primary artifact a judge opens. The
    frozen corpus MUST fit inside it. Therefore data/ freezes ONLY the CFR
    sections and FR amendatory blocks actually used by the eval set - never whole
    title XMLs (a single ECFR title XML is tens of MB; nine titles measured
    407 MB). Extract-then-freeze, never download-then-freeze.

C2. TRAJECTORY BUDGET. ~750 runs x full prompts would alone exceed 50 MB. The PDF
    requires "REPRESENTATIVE trajectories for every agent you used", not all of
    them. Ship a curated representative set in the zip; ship the complete set in
    the git repo and link it from the Description. Record the selection rule so
    the curation is auditable.

C3. VIDEO IS A URL. Upload to YouTube (unlisted) early - processing can take
    hours. A finished video that is still processing at 17:55 UTC is a failure.

C4. THE DESCRIPTION IS THE FIRST THING A JUDGE READS. It is the 20-second
    impression that decides whether the rest gets read carefully. It carries the
    GitHub link (there is no dedicated repo field).

C5. DRAFT EARLY. "Save as Draft" exists. A complete-but-imperfect draft is saved
    as soon as one exists, then updated. This removes the single-point failure of
    a submission attempt at the deadline.

---

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

---

## Q4 - CH-00 prompt contradicts itself about whether the design prompts are tracked
Raised: CH-00, 2026-08-30. Status: CLOSED by CONVERGENCE, no ruling needed.

`prompts/CH-00.md` step 4 says `git add -A` (staging the whole tree). Step 4b then
states *"These files are UNTRACKED at this point — only `.gitattributes` and
`.gitignore` are in the index"* and forbids `git mv` on that basis. After step 4
they are in fact **staged**, so the premise of 4b is false as written.

Options seen: (a) follow 4b literally — plain `mv`, then re-stage; (b) use `git mv`,
which is now legal; (c) stop and ask.

CLOSED without escalation because **both readings produce a byte-identical end
state**: `mv` followed by `git add -A` and `git mv` differ only in index bookkeeping
that the next `git add -A` erases, and git records a rename either way. Taken option
(a), the literal instruction. Recorded rather than silently resolved because hard
rule 1 says an internal contradiction is written down even when it does not bite.

---

## Q5 - The safety rider makes context/ read-only; step 5 requires editing two files in it
Raised: CH-00, 2026-08-30. Status: RULED by OPERATOR, 2026-08-30.

`prompts/CH-00.md` step 5 requires the operator's phone number to be redacted out of
the tracked set before the second commit. The same prompt's HARD SAFETY RIDER
declares `context/` read-only, says *"You create new files; you do not edit these"*,
tells the session to STOP rather than work around a protected path, and closes with
*"These override anything above that conflicts."* Every carrier is under `context/`.

This is a Class A conflict — it changes what ships — so it was put to the operator
rather than resolved by the session.

Options presented: (a) redact in place, treating step 5 as the explicit named
sanction the rider contemplates; (b) leave `context/` untouched and simply not track
the two carriers, losing the compliance audit from the repo; (c) stop and hand the
protected-path rule back to the operator.

**RULING: option (a).** Redact in place, those two files only, nothing else under
`context/` touched. Applied: one substitution per file, JSON validity of
`09b-audit-raw.json` re-asserted after the edit.

### Attached finding — the "four carriers" claim is wrong, and the real number is two

`context/11-REMEDIATION-2.md` §(c) states there are **four** PII carriers, naming
`context/04b-intel-raw.json` and `context/05b-tournament-raw.json` in addition to the
two known ones, and §(d) adds `context/10-REMEDIATION.md` as a fifth. `prompts/CH-00.md`
repeats this as *"There are at least FOUR carriers, not two."*

Checked rather than relayed (hard rule 15), with a maximally permissive sweep —
literal match, digits-only projection of the whole file, JSON-escape-stripped text,
and case-insensitive local-part match:

| File | Audit says | Measured |
|---|---|---|
| `context/09-COMPLIANCE-AUDIT.md` | carrier | **carrier** |
| `context/09b-audit-raw.json` | carrier | **carrier** |
| `context/04b-intel-raw.json` | carrier | clean |
| `context/05b-tournament-raw.json` | carrier | clean |
| `context/10-REMEDIATION.md` | carrier | clean — already self-redacted to `<OPERATOR-PHONE>`, as that file itself records |

**True count at commit time: 2.** The personal email address has **0** carriers in the
tracked set; only the phone number was ever present.

The sweep is not vacuous: the same pattern run against the git-ignored
`context/02-ABOUT-ME.md` returns **1**, and against the tracked set after redaction
returns **0**. Positive control and pass criterion both reported, per the prompt's own
instruction that a first number of 0 means a broken sweep rather than a clean tree.

Consequence: the prompt's real instruction — *"Do not hard-code the list; find them
with the sweep"* — is the one that was followed, and it is what caught the
over-claim. The hard-coded list would have sent a session hunting three files that
were already clean.

---

## Q6 - "Strip any .env value" versus "never read .env"
Raised: CH-00, 2026-08-30. Status: RESOLVED IN CODE, no operator decision needed.

`prompts/CH-00.md` §1b requires `tools/export_session.py` to strip *"any `.env`
value, API key, or the operator's phone number if present"*. The HARD SAFETY RIDER
says *"Never read, print, echo or commit `.env` or any credential value."* Read
together, the session is told to remove values it is forbidden to read.

RESOLVED without an operator call because the two are only in conflict under one
implementation. `tools/export_session.py` **never opens `.env`.** It strips:
  * credential *shapes* — `sk-ant-…`, `AIza…`, `gh[pousr]_…`, `AKIA…`, `xox[abprs]-…`,
    `Bearer …`, PEM private-key headers;
  * `KEY=value` and `"KEY": "value"` where the key name matches
    `*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)*` — which is the only shape in which a
    `.env` value can actually reach a transcript.

That covers the requirement without a read. CLAUDE.md rule 12's allowance —
*"To confirm a key exists, read only its name"* — is respected: not even the name is
read, because no `.env` exists yet on this machine.

Both mechanisms are proved to fire, on synthetic values, in
`docs/evidence/ch00-guard-probe.txt` cases I–M. If a later chunk finds a real leak
shape these patterns miss, add the pattern — do not add a `.env` read.

---

## Q7 - Commit author identity becomes public with the repository
Raised: CH-00, 2026-08-30. Status: ANSWERED by OPERATOR, 2026-08-30.

Every commit carries the global git identity `chinmoy-paul
<chinmoypaul8897@gmail.com>`. At CH-15 the repository is flipped public, and author
metadata cannot be changed afterwards without rewriting history. Raised at CH-00
because it is cheap now and expensive later.

Noted: this address is **not** the personal email in `context/02-ABOUT-ME.md`; it is
the address behind the public GitHub account `chinmoypaul8897` that will own the
public repository, so it discloses nothing the repository itself does not.

Options presented: (a) keep it; (b) set a repo-local `user.email` to the GitHub
`users.noreply.github.com` address so no real address appears in commit metadata.

**RULING: option (a), keep it.** No action taken; recorded so that the choice is
visible rather than defaulted into.

---

## Q8 - The spec names a `<SECTION>` element that does not exist in the format CH-01 reads
Raised: CH-01, 2026-08-30. Status: RESOLVED IN CODE, no operator decision needed.
Consequence flagged forward to CH-03.

`CONTEXT.md` section 8 and `prompts/CH-01.md` step 2 both ask whether an `<EDNOTE>`
sits "inside a `<SECTION>` block". **The ECFR bulk XML contains no `<SECTION>`
element.** It is a `DLPSTEXTCLASS` document whose structural containers are numbered
`DIV` elements carrying a `TYPE` attribute; the section container is
`<DIV8 TYPE="SECTION">`. Measured on title 7: 17,205 `DIV8 TYPE="SECTION"`, 548
`DIV5 TYPE="PART"`, 144 `DIV9 TYPE="APPENDIX"`, and zero `<SECTION>`.

`<SECTION>` is the **CFR annual-edition** spelling - a different govinfo product with
a different DTD. That is in fact the source `CONTEXT.md`'s own leakage measurement was
taken on (`CFR-2024-title40-vol5`, 5,524,321 B, "26 of 28 `<EDNOTE>` sit inside a
`<SECTION>` block"). So both descriptions are correct, each for its own format; the
spec simply carries one format's element name into the other's chunk.

RESOLVED without an operator call because the semantic test is unambiguous - *"section
level, not appendix/part"* - and only the element's spelling differs. CH-01 records
`container_type` as the `TYPE` of the nearest enclosing structural `DIV` and sets
`section_level = (container_type == "SECTION")`. Recorded as a **Class B** deviation in
`PROGRESS.md`, and pinned by golden **G2** (`docs/evidence/ch01-pool/goldens.md`), a
defect note inside a `DIV9 TYPE="APPENDIX"` whose expected `section_level` is `false`.

**Consequence for CH-03, which is the reason this is written down rather than fixed
silently.** `plan.md`'s CH-03 card and `CONTEXT.md` section 8 specify the leakage-strip
test against `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>` and `<EAR>`. Those are annual-edition
names, and CH-03 reads annual editions, so **they are the right names there** - no
change is needed. But a CH-03 session that reaches for ECFR bulk XML for any reason
would strip nothing and its per-element counts would print as zeros, which under hard
rule 14 must read as a real zero. **Any strip counter must therefore assert against a
known-positive input before its zeros are believed.** The element names are
format-dependent and neither file says so.

Not escalated as Class A because it changes no result, no threshold and no count. If
the architect prefers the spec text corrected rather than annotated, that is a
`CONTEXT.md` edit and `CONTEXT.md` is protected read-only for build sessions.

## Q9 - CONTEXT.md section 8's section-citation regex misses a whole drafting style, and the miss MIS-ATTRIBUTES rather than under-detects
Raised: CH-02, 2026-08-30. Status: BOTH READINGS COMPUTED AND SHIPPED; the gate is
taken on the spec-literal one. **An architect decision is wanted, but nothing was
blocked and nothing was substituted silently.**

`CONTEXT.md` section 8 specifies the detector as *"matches a `§\s*[\d.]+[a-z]?`
citation in its own text"*. A large minority of the Federal Register writes the same
thing without the sign:

    2. Section 1.907 is amended by revising the definition of "covered geographic
       licenses" to read as follows:

**Why this is not merely an under-detection.** Carry-forward means an element that
fails to be recognised as naming a section inherits the previous one. On FR Doc
2020-11897 (golden G1, an FCC rule) 24 of 28 elements use the word form, so under the
sign-only detector `current_section` stays pinned at `1.9005` - set by the single
element that used a sign - and **20 elements are attributed to a section they do not
amend.** A silent wrong answer, not a silent gap.

Measured over all 70 FR documents / 8,752 AMDPAR elements:

| detector | completeness | attribution rate | unattributable |
|---|---:|---:|---:|
| `spec_literal` - section 8's own regex | 0.5080 | 0.7613 | 2,089 |
| `extended` - adds the word form | 0.6643 | 0.9865 | 118 |

**How widespread, measured over all 70 documents / 8,752 elements** - not inferred
from golden G1, which is one document chosen precisely because it is hard:

| | elements | share | documents |
|---|---:|---:|---:|
| name a section with the **sign** | 2,191 | 25.0% | - |
| name a section under **extended** | 3,277 | 37.4% | - |
| name it **only** in the word form | **1,086** | **12.4%** | **32 of 70** |
| **attributed differently by the two detectors** | **2,459** | **28.1%** | **32 of 70** |

So this is not a quirk of one FCC rule. Nearly half the documents in the pool contain at
least one word-form lead-in, and **over a quarter of every AMDPAR element in the corpus
is attributed to a different section depending on which detector is used.**

**A corroborating check on section 8's own arithmetic.** Section 8 states that *"only
~42% of AMDPARs name a section."* Measured here: **25.0%** under its own sign-only regex,
**37.4%** under the extended reading. Section 8's own figure is 4.6 points from the
extended reading and 17 points from the regex it prints - which is evidence that the
sentence meant the broader reading and the regex beside it is an imprecise
operationalisation of it, rather than the two being in genuine conflict. Offered as a
measurement, not as a preference; the architect may read it the other way.

**What CH-02 did.** Implemented **both**, recorded both in every frozen record
(`section_spec_literal` / `section_extended`, and `detector_disagrees`), reported both
everywhere, and **took the pre-registered gate branch on `spec_literal`**, because
`prompts/CH-02.md` says *"implement that, not your own reading"* and because it is the
lower of the two. Both land in the same `< 0.80` branch, so the choice of detector does
not decide this chunk's outcome - but it will decide which sections CH-03's eval set is
built from, which is why it is written down rather than settled here.

**The decision wanted:** whether `CONTEXT.md` section 8's regex should be corrected to
recognise the word form. That is an edit to a protected file, so it is **Class A** and
belongs to the architect. Also note section 8's regex truncates every title-26 section
number (`§ 1.367(a)-8` -> `1.367`), which CH-02 fixed under goldens rule P2 and which is
the same class of defect section 8 itself blames for a predecessor's 0.46.

Not escalated as blocking, because both readings are computed and the deliverable
numbers are reported under each.

## Q10 - Two more section-citation spellings, found AFTER the measurement and deliberately not fixed
Raised: CH-02, 2026-08-30. Status: RECORDED, COUNTED, NOT ACTED ON. For the architect
to adopt at CH-03 or decline.

`docs/evidence/ch02-attributor/goldens.md` section 6 states, before any number existed,
that *"no rule in section 2 may be changed after section 7 is measured."* Two further
spellings turned up once the corpus ran. **The detectors were not changed**, and the
findings are published with their counts instead (goldens section 9):

| finding | elements | documents | effect |
|---|---:|---:|---|
| a section cited as `46 CFR 356.3` - no sign, and not the word *Section* either | 9 | 1 (`2026-11267`) | all 27 AMDPARs of that document are unattributable; it is the only document in the corpus with zero attributed sections |
| a table-driven amendment - *"For each section and paragraph indicated in the left column of the following table..."* - where the sections live in a `<GPOTABLE>` and never appear in the AMDPAR text | 26 | 1 (`2024-18445`) | 4 defect sections in that document have no AMDPAR attributed to them |

Adding a `NN CFR X.Y` detector would recover at most 27 elements of 8,752 - **under
0.31 percentage points**, and nowhere near the 0.80 branch boundary. It is declined
anyway: the value of a pre-registration is precisely that it is not revised once the
number is in view. Both numbers are on the table for the architect.

**A third diagnostic, in the same family.** `current_section` is not reset at a
`<REGTEXT>` `PART` boundary, because section 8 specifies no such reset (goldens rule
P7). Measured consequence: **699 of 8,752 elements** are attributed to a section whose
part differs from the part of the `<REGTEXT>` they sit in, and every one of those is
wrong. The record carries `part_mismatch` so CH-03 can exclude them; the parser does not
silently repair them. Resetting at a part boundary is a one-line change and would be an
improvement, but it is a change to a pre-registered rule after the measurement, so it is
the architect's call, not a build session's.
## Q11 - SPEC-FIX-1's metric correction is REFUSED; what would make it legitimate
Raised: SPEC-FIX-1, 2026-08-31. Status: **RULED BY THE ARCHITECT, and the refusal is
ACCEPTED IN FULL.** The ruling is recorded verbatim at the end of this entry and the
consequent spec edits were applied by SPEC-FIX-2. Nothing below this line was rewritten
after the ruling: the case as the refusing session put it stands exactly as it stood.
Full reasoning and evidence: `docs/evidence/spec-fix-1/verdict.md`, committed at `72b95e1`
**before** any other work in the chunk, so the order is provable from git.

`prompts/SPEC-FIX-1.md` section 2a proposed replacing `CONTEXT.md` section 8's failing
completeness definition with `attribution_completeness = attributed / total`, gated at
0.90, and asserted of it: *"This is the gate metric. It answers the question the gate
exists to answer"* - namely *"did carry-forward put each instruction on the RIGHT
section?"*

**That assertion is false, and it is disproved rather than argued.**
`docs/evidence/spec-fix-1/spec_fix_1_sabotage.py` builds a control attributor identical to
the shipped one except for one line - it carries the **first**-named section of a document
forward instead of the **last** - and scores it on the proposed metric:

| detector | real | sabotaged | difference | elements placed differently |
|---|---:|---:|---:|---:|
| `extended` | **0.9865** | **0.9865** | **0.000000** | **8,417 / 8,634 = 97.5%** |
| `spec_literal` | 0.7613 | 0.7613 | 0.000000 | 6,395 / 6,663 = 96.0% |

The script asserts its replay of section 8 reproduces the frozen record with **0 mismatches
of 8,752** before drawing the comparison. The result is structural, not accidental: an
element is attributed iff some section was named at or before it, which holds for both
rules, so `attributed / total` measures only *where the first citation appears*.

**Stated fairly:** the metric is not vacuous in general. It does catch the silent-DROP mode
that killed the predecessor pilot at 0.46 - a lead-ins-only extractor scores 0.2503 /
0.3744 and fails hard. It is blind specifically to the silent-WRONG mode that CH-02
discovered in this corpus (Q9), which is the mode the correction was written in response to.

**Three further findings, each measured in-repo:**

1. **The pass needs both post-hoc edits.** Section 2a alone 0.7613 FAIL; section 2c alone
   0.6643 FAIL; both 0.9865 PASS. The prompt's fact table quotes only the `extended` figure
   and does not say CH-02 gated on `spec_literal`.
2. **Strictly harder metrics were free and none was taken** - every one computable from
   booleans already in the frozen record: attributed AND part-consistent = **0.9066**, which
   still PASSES but at a 0.66-point margin instead of 8.65; attributed AND part-consistent
   AND no rival-section conflict = **0.8579**, FAIL; the per-document floor section 8
   *already mandates* = **57/70 = 0.8143**, FAIL.
3. **Golden G1 passes the proposed gate.** FR Doc 2020-11897 is the document CH-02 chose
   *because* it demonstrates mis-attribution, and Q9 records 20 of its 28 elements pinned to
   a section they do not amend. Its proposed-gate score is **26/28 = 0.9286 - PASS**.

**On the counterfactual the prompt itself made decisive.** Would this have been raised at
0.92? The *diagnosis* would - it already had been, in `goldens.md` section 2 rule P6 at
`98f1cff`, twenty-five minutes before the attributor existed. The *metric change* would not:
`prompts/CH-02.md`'s pre-registered `>= 0.90` row reads, in full, *"Proceed. Report the
figure."*, and CH-02 - holding every fact SPEC-FIX-1 holds - wrote *"The definition was not
rewritten to raise the number."* Nothing was learned between the specification and the
correction except the number.

**THE PATH BACK. Four changes; nothing requires re-running the attributor.**

1. **Keep the split.** `parse_completeness` does not belong in an attributor's gate. Only
   **46 of 2,913** unparsed elements (1.6%) are recoverable parser gaps; the rest is
   Federal Register drafting. This half of the correction survives the refusal intact and
   should be re-issued.
2. **Do not gate on `attributed / total`.** Gate on a correctness-constrained metric. The
   minimum honest version is **attributed AND part-consistent = 0.9066**, one already-frozen
   boolean, still passing. Publish the whole ladder beside whichever is chosen, so a reader
   sees which harder metrics were available and declined at the moment the definition changed.
3. **Restore the per-document floor** section 8 already requires and CH-02's branch table
   already restricts on. Publish **57/70 = 0.8143** and say it fails.
4. **Rule on the part-boundary reset in the same edit as the Q9 regex fix.** Q9's fix is
   worth **+22.5 points** and was adopted; the part-boundary reset is worth **-8.0 points**,
   CH-02 called it *"a one-line change and would be an improvement"*, and SPEC-FIX-1 does not
   mention it. A fix that raises the number and a fix that lowers it must be ruled on
   together, or the ruling is made with the scoreboard visible.

**Recommended regardless of the ruling:** publish the sabotage control itself. A metric
returning 0.9865 for an attributor that is 97.5% wrong is the sharpest artefact this project
has produced for its own thesis that a green number is not evidence of correctness.

**What was NOT done, so the state is unambiguous:** `CONTEXT.md` is untouched - no 2a, no
2b, no 2c, no v1.1 bump, no section 13 row. `data/` was read-only. The attributor was not
re-run. `src/` and `tests/` were not opened.

### THE RULING - recorded verbatim by SPEC-FIX-2, 2026-08-31

Transcribed character-for-character from `prompts/SPEC-FIX-2.md` (now tracked, so the
transcription is checkable against its source). The date inside the block is the
architect's own and is reproduced unaltered; the transcription was made on 2026-08-31.

```
Q11 - RULED by ARCHITECT, 2026-08-30.

The refusal is ACCEPTED IN FULL. The proposed metric was not adopted and will
not be re-proposed. SPEC-FIX-1's sabotage control is decisive: an attributor
that places 6,395 of 6,663 attributed elements on a DIFFERENT section scores
the identical 0.7613, so attributed/total cannot distinguish a correct
attributor from a 96%-wrong one. The architect's claim that it "answers the
question the gate exists to answer" was factually false, and was disproved by
running code rather than argued down.

Three further findings are accepted without qualification:
  (a) the proposed pass required BOTH post-hoc edits - 2a alone 0.7613, 2c
      alone 0.6643, together 0.9865. That is the shape of a rescue.
  (b) golden G1, chosen by CH-02 BECAUSE it demonstrates mis-attribution,
      passes the proposed gate at 0.9286.
  (c) the proposal adopted the +22.5pt correction and omitted the -8.0pt one
      that CH-02 had already called an improvement. Selecting the fix that
      helps and omitting the fix that hurts is the defect this project exists
      to detect, and the architect committed it.

On "would this have been raised at 0.92" - no. The diagnosis pre-existed the
number (goldens.md P6, committed 25 minutes before the attributor). The metric
change did not. Nothing was learned between the spec and the correction except
the number.

WHAT SURVIVES: only 46 of 2,913 unparsed elements (1.6%) are our defect. Parse
shape is a property of Federal Register drafting, not of our attributor, and
does not belong in an attributor's gate. That half of the diagnosis stands and
is recorded - but it does NOT license a metric change now, because no metric
that discriminates was available at a passing threshold. The gate stays as it
is and stays FAILED.

CONSEQUENCE: CH-02 remains in the "< 0.80 - documented failure" branch. The
failure is published in the README, not absorbed. CH-03 proceeds on the
per-document restriction that was pre-registered BEFORE any of this - see
plan.md CH-02's fallback - which is a rescue by nobody's definition because it
was written before the number existed.
```

**What SPEC-FIX-2 applied under it, 2026-08-31 - and no number moved.**

1. `CONTEXT.md` section 8 now **records the failure instead of fixing it**: global
   completeness 0.5080 spec-literal and 0.6643 extended against a 0.90 gate, and the
   0.7613 / 0.9865 attribution figure named as **tested and rejected** as a replacement
   gate, with the sabotage control as the reason. The definition, the threshold and the
   metric are untouched.
2. Section 8 step 3's detector now recognises the **word form** (`Section 1.907 is
   amended by`) beside the sign form, matched **case-sensitively** per Q12(c). Adopted
   because it is justified independently of any number: under the sign-only detector ten
   documents - **1,910 elements**, including the two largest FAR rules in the corpus -
   attribute to nothing at all.
3. Section 8 now **resets `current_section` at a `REGTEXT` part boundary**. Adopted
   although it **costs 8 points**, because the fix that raises the number and the fix
   that lowers it are ruled on together or the ruling is made with the scoreboard
   visible.
4. Q13's housekeeping is done; see Q13.

Changes 2 and 3 alter the spec **for CH-03 onward**. The attributor was **not** re-run,
no committed measurement changed, and CH-02 stays in the `< 0.80` documented-failure
branch.

## Q12 - Q9's and Q10's own numbers overstate the attributor's error; and the word-form detector over-detects
Raised: SPEC-FIX-1, 2026-08-31. Status: MEASURED AND RECORDED, NOT CORRECTED IN PLACE.
Following `goldens.md`'s own ERRATA convention - a wrong number is corrected in a new
entry, never edited out of the old one. Evidence: `docs/evidence/spec-fix-1/sabotage.txt`
section 4, and `classes.txt`.

**(a) Q10 states of the 699 part-mismatched elements that "every one of those is wrong."
126 of them are not.** Those 126 **name their own section in their own text** - e.g. an
element citing 1037.605 sitting inside a `<REGTEXT>` tagged part 1036. Their attribution is
right; the `REGTEXT/@PART` tag is the thing that disagrees. The reliable figure for
*carry-forward* mismatches is **573**, and the residual **126** are evidence of a separate
`regtext_part` extraction defect that nobody has logged. Both figures should ship.

**(b) Q9's `detector_disagrees = 2,459` is not 2,459 conflicts.** Decomposed: **488** are
genuine rival-section conflicts, where both detectors named a section and the two differ;
the other **1,971** are elements `spec_literal` failed to attribute at all. Quoting 2,459 as
"attributed differently" overstates disagreement and, worse, charges the `extended` detector
for repairing the very defect Q9 asks to have fixed.

**(c) NEW - the shipped `extended` detector is case-insensitive, and that over-detects.**
`goldens.md` rule P3 specifies the word form as `Section 90.209` / `Sections 90.209 and
90.210`. The shipped detector also fires on **lowercase** `section 1.1`: of 684 elements
whose only word-form citation is lowercase, **683** are treated as naming a section, and
**676 of the 1,086** extended-only namers are lowercase. Most are correct, but some are
**appendix-internal numbering read as CFR sections** - *"Appendix A to part 75 is amended by
revising the title of section 1.1"* pins `current_section` to `1.1` inside a `REGTEXT` for
part 75. 44 of the 683 lowercase-form namers carry `part_mismatch`, and the 4 clearest cases
name an Appendix explicitly.

**Why this matters for Q11's item 4.** If the Q9 correction is re-issued, `CONTEXT.md`
section 8 must say **whether the word form is case-sensitive**, because the two readings are
different detectors and the 0.9865 figure is the case-**in**sensitive one. Specifying it
either way is an architect decision (Class A); this session did not make it, having refused
the edit that would have required it. The over-detection is bounded and the `part_mismatch`
diagnostic CH-02 shipped already flags it - which is that diagnostic doing exactly the job
it was built for.

## Q13 - SPEC-FIX-1's housekeeping is fenced behind a verdict it did not get
Raised: SPEC-FIX-1, 2026-08-31. Status: **AUTHORISED AND DONE at SPEC-FIX-2, 2026-08-31.**
`prompts/SPEC-FIX-2.md` section 4 gave the one line, explicitly *"unblocked and independent
of all the above"*, so none of it waited on the Q11 ruling. All three items are closed:
the CH-01 working-tree edit is committed in a commit of its own that says it is an
architect edit and not a SPEC-FIX-2 change; `prompts/CH-02.md`, `prompts/SPEC-FIX-1.md`
and `prompts/SPEC-FIX-2.md` are tracked, so all 9 chunk prompts are now in the
repository and `git ls-files --others --exclude-standard prompts/` returns nothing; and
`CONTEXT.md` is at v1.1 with a section 13 change-log row that names the refusal.
**The original text below is left exactly as SPEC-FIX-1 wrote it.**

`prompts/SPEC-FIX-1.md` section 2d asks for three items of pure housekeeping - commit the
uncommitted `CONTEXT.md` working-tree edit from CH-01, commit the untracked
`prompts/CH-02.md`, and bump `CONTEXT.md` to v1.1. But section 2 opens *"If and only if the
verdict is LEGITIMATE - apply these four changes"*, and section 2d is the fourth. The
verdict is GOALPOST-MOVING, so **none of it was done**, and the scope fence's *"anything not
specified above -> STOP"* forbids a build session widening its own mandate to do it anyway.

**Consequently the tree is left as it was found:**

| item | state |
|---|---|
| `CONTEXT.md` | still carries the **uncommitted** CH-01 measured-pool edit |
| `prompts/CH-02.md` | still **untracked** |
| `prompts/SPEC-FIX-1.md` | still **untracked** - not named in section 2d at all, and not in the scope fence |

The first two are genuinely independent of the metric dispute, and the third is a
deliverable-1 gap on the same footing as the second: *the prompts are the instructions that
shape each agent*, and every other chunk prompt is tracked. **Requested: a one-line
authorisation to commit all three, independent of how Q11 is ruled.** Recorded rather than
assumed, because the whole point of this chunk was that a session may not decide the parts
it was told it does not decide.

## Q14 - v1.1 specifies a detector whose corpus figures do not exist yet, and leaves one stale number in force
Raised: SPEC-FIX-2, 2026-08-31. Status: RECORDED, NOT FIXED - and not fixable in this
chunk, because `prompts/SPEC-FIX-2.md` forbids re-running the attributor in terms:
*"Do not re-run the attributor. No number changes in this chunk."* For CH-03.

`CONTEXT.md` v1.1 adopted the word-form detector **case-sensitively** (Q12(c)). That is
the right rule and it is not in dispute. But it creates a divergence between the
specification and every measurement in the repository, and the divergence is written
down here rather than papered over, because a reader of section 8 would otherwise take
its numbers as figures for the detector section 8 now describes. They are not.

**(a) Every `extended` figure in this repository was computed case-INsensitively.** That
includes 0.6643 completeness, 0.9865 attribution, 0.9066 part-consistent, the 57/70
per-document count, `detector_disagrees` = 2,459, the 1,086 word-form-only namers and the
699 / 573 / 126 part-mismatch decomposition. Q12(c) measured the exposure: 683 of 684
lowercase-only elements are treated as naming a section, and 676 of the 1,086
extended-only namers are lowercase. **The case-sensitive figures are unknown**, and they
are not reconstructible by arithmetic from the case-insensitive ones - 44 of the 683
carry `part_mismatch` and the rest are mostly correct, so the delta is neither the whole
683 nor zero. **CH-03 must re-measure rather than adjust.** This does not change the
gate outcome: CH-02 failed at 0.5080 / 0.6643 against 0.90, and a stricter detector
cannot raise either figure.

**(b) Section 8 still says "only ~42% of AMDPARs name a section", and that number is now
stale in a third way.** Q9 already recorded that it matches neither the sign-only reading
(25.0%) nor the case-insensitive extended one (37.4%). Under v1.1's case-sensitive
extended detector it matches a third figure that has not been measured. **It was left
untouched deliberately.** `prompts/SPEC-FIX-2.md`'s scope fence says *"anything else ->
STOP"*, and the ruling authorised three specific changes; editing a fourth number would
have been a build session widening its own mandate, which is the exact failure SPEC-FIX-1
was praised for refusing. The sentence is prose framing rather than a gate input, so
leaving it does not affect any threshold - but it is in a file that is LAW and a CH-03
session will read it, so it is flagged rather than left to be discovered.

**What is wanted:** nothing from the architect now. CH-03 re-measures under the v1.1
detector, publishes the case-sensitive figures beside the case-insensitive ones (the
ERRATA convention: a wrong number is corrected in a new entry, never edited out of the
old one), and at that point the architect can retire the "~42%" sentence with a measured
replacement instead of an estimate.

---

## Q15 - CONTEXT.md v1.1's case-sensitive word form RE-CREATES the failure it was adopted to fix, and section 8's own quoted example does not occur in the corpus
Raised: CH-03, 2026-08-31. Status: **CLASS A - recorded, NOT acted on. The spec was
FOLLOWED, not corrected.** `CONTEXT.md` is LAW and protected; a build session does not
edit it. The eval set is built on v1.1 as written. Evidence:
`docs/evidence/ch03-evalset/remeasure-v11.txt` and `case-sensitivity-cost.txt`.

**The justification section 8 gives for the word form.** v1.1, verbatim:

> *"under the sign-only reading **ten documents attribute NOTHING - 1,910 elements**,
> among them two of the five largest rules in the corpus (`2014-08744` at 838 elements,
> `2021-22144` at 649), because FAR-family rules write "Section 52.204-8 is amended"
> without the sign."*

**Measured under v1.1 as specified** (word form, case-SENSITIVE, part reset):

| detector | documents attributing NOTHING | elements |
|---|---:|---:|
| `spec_literal` - sign only | 10 | 1,910 |
| `extended_ci` - what CH-02 shipped | **1** | **27** |
| `extended_cs` - case-sensitive | 5 | **1,655** |
| **`v11` - CONTEXT.md v1.1** | **5** | **1,655** |

**87% of the harm the word form was adopted to remove is back**, and the two documents
section 8 names by number are among the five. `2014-08744`: 838 elements, **0
attributed**. `2021-22144`: 649 elements, **0 attributed**.

**Why: section 8's quoted example is not what the corpus says.**

| string | occurrences in the corpus |
|---|---:|
| `Section 52.204-8` (capital S, as section 8 quotes it) | **0** |
| `section 52.204-8` (lowercase, the actual bytes) | **2** |

The real text is `"336. Amend section 52.204-8 by-"`. FAR-family rules do not write
*"Section X is amended"*; they write *"Amend section X by..."*, with the word
mid-sentence and therefore lowercase. **The illustrative quotation in section 8 was
reconstructed rather than transcribed**, and the case rule was written to fit the
reconstruction.

**Q12(c)'s over-detection evidence, decomposed.** Q12(c) justified case-sensitivity on
*"684 elements whose only word-form citation is lowercase, 683 treated as naming a
section, 44 of those carry `part_mismatch`"*. Measured here, of the **683**
lowercase-only namers:

| | elements | share |
|---|---:|---:|
| in `2014-08744` and `2021-22144`, where lowercase detection is **CORRECT** | **617** | **90.3%** |
| in the other five documents | 66 | 9.7% |
| carrying `part_mismatch` (Q12(c)'s harm case, its own figure) | 44 | 6.4% |

So the rule trades **617 correct detections for at most 44 suspect ones**, and Q12(c)
did not decompose its own 683 by document. Nothing in Q12(c) was wrong; it measured
the over-detection and never measured the under-detection the fix would cause.

**Direct cost to this chunk:** 6 of the 85 pool positives sit in documents that
attribute nothing under v11 - `2014-08744/6.302-1`, `2020-16986/1831.205-70`,
`2021-22144/15.601`, `2024-29226/252.227-7014`, and both of `2026-11267`'s (the last
document is Q10's already-recorded `46 CFR 356.3` case, not a case-rule casualty).
They drop on the `positive-has-no-attributed-instructions` rung.

**What CH-03 did: followed the spec.** The eval set is built on v11, case-sensitive,
and the affected positives are excluded on a named ladder rung with their count. **No
detector was substituted, no rule was relaxed, and no number was adjusted.** Hard rule
3: this is Class A - it changes meaning and results - so it stops here and goes to the
architect rather than being fixed by the session that found it.

**The options, for the architect, with their measured consequences:**

- **(a) Leave v1.1 as written.** 1,655 elements and 5 documents attribute to nothing;
  4 pool positives are lost to the case rule specifically. Defensible: the rule is at
  least *stated*, and Q12(c)'s appendix-numbering harm is real.
- **(b) Case-INsensitive word form** (revert Q12(c)). Recovers 617 correct detections,
  re-admits ~44 `part_mismatch` elements. **The part-boundary reset already catches
  most of that harm**: `part_mismatch` falls 699 -> 115 under v11, and the reset was
  adopted in the same edit. The two fixes overlap, and Q12(c) was ruled before that
  overlap was measured.
- **(c) Case-sensitive EXCEPT after an amendatory verb** - `Amend/amend section X`.
  Fits the corpus, but it is a new rule invented after seeing the number, which is
  precisely the shape SPEC-FIX-1 refused. **Recorded and NOT recommended.**

**This session recommends nothing and adopted nothing.** The measurement is the
deliverable; the ruling is the architect's.

---

## Q16 - the per-document completeness floor the Q11 ruling points at leaves 1 pair, and it selects on Federal Register drafting style rather than on attribution
Raised: CH-03, 2026-08-31. Status: **CONTRADICTION RECORDED; the option taken is named,
with the count it produces AND the count the other option produces.** Evidence:
`docs/evidence/ch03-evalset/floor-decomposition.txt`.

**The contradiction.** Two binding documents point in different directions.

- **`plan.md` CH-02's pre-registered fallback** scopes the restriction to one branch:
  *"If global attributor completeness lands in **[0.80, 0.90)**, restrict the eval set
  to FR documents with per-document completeness >= 0.90 ... **Below 0.80** the
  attributor is a documented failure and the headline is withdrawn."* CH-02 measured
  0.5080 / 0.6643, i.e. the **< 0.80** branch, whose stated consequence is the
  withdrawal - which has already happened and is published in `CONTEXT.md` section 8.
  **The >= 0.90 restriction is the remedy for a branch this project is not in.**
- **`QUESTIONS.md` Q11's ruling** says *"CH-03 proceeds on the per-document restriction
  that was pre-registered BEFORE any of this - see plan.md CH-02's fallback."* It
  points at the fallback, and the fallback scopes the restriction away from us.

**Measured consequence of each reading:**

| reading | documents kept | pairs | n |
|---|---:|---:|---:|
| (i) apply the >= 0.90 floor - Q11's sentence read literally | **2 / 70** | **1** | **2** |
| (ii) plan.md's fallback as scoped - no floor in the < 0.80 branch | 70 / 70 | **50** | **100** |

**A number-INDEPENDENT reason the floor is the wrong instrument here**, and it is the
reason this entry does not rest on n. Per-document *completeness* is
`attributed AND parsed / total`. Decomposed over the 68 documents the floor excludes:

| | documents |
|---|---:|
| bound by the **parse** half, not the attribution half (`parse_rate < attribution_rate`) | **59 / 68** |
| **attribution >= 0.90** and yet excluded by the completeness floor | **36** |
| `parse_rate < 0.90` | 68 / 68 |

Three excluded documents have attribution **1.0000** - perfect - and fail purely on
parse rate (`2011-12279` 0.4167, `2020-17549` 0.6111, `2024-30575` 0.2500).

**And the ruling that created this situation says the parse half does not belong here.**
Q11, verbatim: *"only 46 of 2,913 unparsed elements (1.6%) are our defect. Parse shape
is a property of Federal Register drafting, not of our attributor, and does not belong
in an attributor's gate."* A per-document floor on *completeness* therefore selects
overwhelmingly on FR drafting style. It is not a validity filter for an eval item.

**WHAT WAS DONE, stated plainly including the part that looks bad.**

**Reading (ii) is the frozen primary: 50 pairs, n = 100.** Reading (i) is **also built
and committed**, at `data/evalset-restricted/`, so the architect can flip the choice
with one command and a reviewer can run either without rebuilding anything.

**The uncomfortable fact, stated rather than buried: the option taken is also the one
with the larger n.** That is exactly the shape SPEC-FIX-1 refused and Q11 condemned -
*"Selecting the fix that helps and omitting the fix that hurts is the defect this
project exists to detect."* Three things are offered against it, and the reader is
invited to weigh them rather than take them:

1. The reason is a **scope mismatch in `plan.md` that is checkable without any
   number** - the fallback names the [0.80, 0.90) branch and we are below 0.80.
2. The decomposition above is **also number-independent** - 59 of 68 exclusions are
   parse-bound, and Q11's own ruling says parse shape does not belong in this gate.
3. **Both sets ship.** Nothing is hidden; the floor is a named ladder rung carrying
   its exact cost; and the choice is one flag.

**A mitigation that is a new MEASUREMENT and not a metric change.** Every frozen item
carries its document's `completeness_v11`, `attribution_rate_v11` and `parse_rate_v11`.
The scorer can therefore report accuracy **stratified by document completeness**, and
if the arms behave differently on low-completeness documents that is a measured fact
rather than an assumption. **No threshold was introduced and no definition was
altered.**

**What is wanted from the architect:** a ruling on whether (i) or (ii) is the eval set,
and, if (i), an instruction on what CH-04 and the CHECKPOINT are supposed to measure at
n = 2. Nothing was blocked; the queue continued.

---

## Q17 - CONTEXT.md section 8 names `<EFFDNOTP>`; the corpus also uses `<EFFDNOT>`, and Q8's trap fired for real
Raised: CH-03, 2026-08-31. Status: **CLASS A - recorded, NOT acted on. The stripper was
NOT extended.** The affected items were excluded on a named ladder rung, which makes
the eval set smaller. Evidence: `docs/evidence/ch03-evalset/alt-element-census.txt`,
script beside it.

**Q8 predicted this in the abstract at CH-01 and it happened in the concrete at CH-03.**
Q8's words: *"a strip counter that reports zero may simply be looking for the wrong
element name ... A silent zero here is the leakage defect returning by a different
door."* It did, and the door was one letter wide.

**What happened.** `CONTEXT.md` section 8 requires `<EFFDNOTP>` stripped. In
`CFR-2015-title7-vol13.xml`, section 1942.5, the strip counter reported

    EDNOTE 0   EFFDNOTP 0   CITA 1   EAR 0

and **every one of those zeros was true for its tag.** The section nonetheless carried
a complete effective-date note - the FR citation, the section, the designations, *"For
the convenience of the user, the revised text is set forth as follows"*, and a
`<REVTXT><SECTION>` reprint of the pending amendment - inside an element spelled
**`<EFFDNOT>`**, with no trailing `P`. `<EFFDNOTP>` occurs **zero** times in that
volume; `<EFFDNOT>` occurs four.

**Census over all 68 annual-edition volumes CH-03 downloaded:**

| element | occurrences | volumes | named by section 8 |
|---|---:|---:|---|
| `EDNOTE` | 857 | 67 | YES |
| `EFFDNOTP` | 446 | 31 | YES |
| `CITA` | 31,943 | 68 | YES |
| `EAR` | 3,303 | 68 | YES |
| **`EFFDNOT`** | **379** | **26** | **no** |
| `NOTE` | 3,051 | 46 | no |
| `SOURCE` | 3,140 | 66 | no |
| `SECAUTH` | 2,322 | 50 | no |
| `APPRO` | 964 | 32 | no |
| `REVTXT` | 200 | 27 | no |
| `EFFDNOTE`, `NOTES`, `NOTE1`, `CREDIT`, `AMDNOTE` | 0 | 0 | no |

**The pre-registered defence held, and it held for the reason it was designed.**
`plan.md`'s leakage test has three rules, not one: element names **(a)**, the item's own
FR citation **(b)**, and four literal strings **(c)**. All **379** `<EFFDNOT>` elements
carry one of the literals, so **rule (c) is a complete backstop for this element**. The
test fired, two pairs were excluded on `leakage-test-failed-after-strip`, and nothing
leaked into the frozen corpus. **A single-rule test keyed on element names alone would
have passed silently.**

**Residual exposure, measured on the FROZEN corpus rather than argued about:**

| unnamed element | surviving in the 76 frozen items | items affected |
|---|---:|---:|
| `EFFDNOT` | **0** | 0 |
| `REVTXT` | **0** | 0 |
| `SOURCE` | **0** | 0 |
| `NOTE` | 14 | 6 |
| `APPRO` | 1 | 1 |
| `SECAUTH` | 1 | 1 |

And the strongest single figure: **0 of 76 frozen items contain any `NN FR NNNN`
citation at all** - not merely none of their own, which is all rule (b) requires, but
none whatsoever. The source-credit channel is empty in the frozen corpus.

**Why the stripper was NOT extended, stated so the choice can be judged.** Adding
`<EFFDNOT>` would be a five-character edit that recovers 2 pairs, taking n from 76 to
80. It was not made, for two reasons:

1. **`CONTEXT.md` is LAW and protected.** Its section 8 names four elements. A fifth is
   a Class A change and belongs to the architect, not to the build session that found
   it. This is the same discipline SPEC-FIX-1 was praised for.
2. **The direction matters.** Excluding makes the eval set **smaller** and the result
   **harder**. Extending the stripper after the number was in view would have made it
   **larger**. When a post-hoc change would raise n, the answer is no.

**For the architect.** Adding `<EFFDNOT>` to section 8's list is almost certainly
correct on the merits - it is the same content under a variant spelling, and the census
above is the evidence. It is recorded here rather than done. If it is adopted, CH-03
re-runs and n moves from 76 to 80; **the two excluded pairs are named in
`data/evalset/leakage.json` so the delta is checkable rather than asserted**:
`2015-01571 / 1942.5` and `2020-07837 / 3.111`.

---

## Q18 - CONTEXT.md section 8's "Distinct FR documents | 78" is a count of CITATIONS, not documents, and the row says it bounds the pair yield
Raised: CH-03 backlog (evidence migration), 2026-08-31. Status: **CLASS A - recorded,
NOT acted on.** `CONTEXT.md` is LAW and protected. Evidence:
`docs/evidence/spec-claims/spec-claims.txt`, script beside it.

`CONTEXT.md` section 8's MEASURED table reads:

> | Distinct FR documents | **78 - this bounds the count-matched pair yield** |

**Re-derived from the committed artefacts, both readings:**

| reading | value |
|---|---:|
| distinct **FR citation strings** in the 85-item pool | **78** |
| distinct **FR documents** the 85 citations resolve to (`data/amdpars/documents.json`) | **70** |

**78 is the citation count.** Eight of the 85 citations share an FR document with
another citation - two editorial notes on different sections of the same rule cite the
same document at different page numbers, so they are distinct citation *strings* and
one document.

**Why this is worth a Class A entry rather than a footnote.** The row does not merely
report a number, it makes a claim about what the number *does*: it *"bounds the
count-matched pair yield"*. A negative must come from **the same FR document** as its
positive, so the quantity that bounds the yield is the **document** count, **70**, not
the citation count, 78. The sentence attaches the right claim to the wrong number.

**It changed no outcome.** CH-02's pair-yield measurement and CH-03's eval set were
both built from `documents.json` - i.e. from the correct 70 - so no downstream figure
inherits the error. The defect is in the spec's prose, not in the pipeline.

**What is wanted from the architect:** correct the row to `70` and either drop `78` or
relabel it as *distinct FR citation strings*. Both numbers are worth keeping - the gap
between them is exactly the "two notes, one rule" case, which is a real property of
the corpus.

**Method note, because it is the reason this was found at all.** The
`verify_spec_claims.py` inventory re-derives every numeral in `CONTEXT.md` that can be
re-derived and sorts the rest into an explicit NOT-IN-REPO pile. Its **first run
reported a second discrepancy that turned out to be the script's own fault** - it
counted "spread over titles" across all 107 defect notes and got 28 against the spec's
25, when the row sits in the pool block and 25 is right for the 85-item pool. That is
recorded in the script rather than quietly deleted: **an inventory that flags the spec
as wrong is itself a claim, and it needs checking in both directions.**

**Current tally: 25 REPRODUCES, 2 DIFFERS (this and Q14(b)'s stale "~42%"), 18
NOT-IN-REPO.** The NOT-IN-REPO pile is not a list of errors; it is a list of figures a
reader cannot check from this repository - almost all of them the pre-competition
pilot numbers that section 3 already marks *provenance-unverified*. Publishing the
inventory turns that warning into something a judge can audit line by line.

---

## Q19 - CH-03 FAILED review TWICE. Strike limit reached, ESCALATED to the architect.
Raised: NIGHT-RUN, 2026-08-31. Status: **ESCALATED. No third review round was run.**

`plan.md`: *"a chunk that FAILS review twice is escalated to the architect rather than
fixed a third time."* `prompts/NIGHT-RUN.md` section 2: *"On a second FAIL: record both
reports, write the open findings verbatim into `QUESTIONS.md`, and move on. No third
round."* Both were followed.

**Both reports are committed**: `docs/reviews/REVIEW_CH-03.md` (round 1) and
`docs/reviews/REVIEW_CH-03-round2.md` (round 2), with runnable probes in
`docs/reviews/ch03-probe/` and `ch03-probe2/`, and kept tests in
`tests/test_review_ch03_findings.py` and `tests/test_review_ch03_round2_findings.py`.

### What the two rounds found

| round | verdict | headline |
|---|---|---|
| 1 | **FAIL** | a label-blind script reading only `frdoc` and `section` scored **0.8158** on the primary metric - beating `B0-agent` by 17 pp and clearing `GOOD.md`'s A1 bar with no model, no CFR text and no instructions |
| 2 | **FAIL** | the fix was real in substance, but **no test protected it**, round 1's mutation table was **false**, and two published numbers did not reproduce |

### The build session's own failures, stated plainly

**I broke hard rule 15 on the evidence that was supposed to prove the gate worked.**
Round 1 reported *"9 mutations designed, 9 caught"*. I repeated it in `REVIEW_CH-03.md`,
`goldens.md` G-D2, `STATUS.md` and `PROGRESS.md` **without checking it**. It is false:
the harness read `returncode != 0` as *caught* with no green baseline, and M7 - flipping
the negative-selection rule from *first* to *last* - **cannot** be caught, because golden
G-D's free candidate list is `["B"]` and the two are the same element.

Rule 15 exists in `CLAUDE.md` because *"the architect broke this three times in one
day"*. I broke it once, in four documents, about the mutation coverage of the gate that
had just caught a benchmark-invalidating defect.

**I broke hard rule 14.** *"32/38, exact p = 0.000024"* was published with no generating
script. It came from an uncommitted inline snippet that **reconstructed** the pairing
from the frozen items file instead of running the rule, and it is wrong. Measured
properly by `docs/evidence/ch03-evalset/ordering_bias.py`: pre-fix **36/50, p = 0.0026**;
shipped **25/50, p = 1.0000**. Direction and conclusion unchanged; the number was wrong.

**A third published number was wrong.** *"5 of 82 items would have leaked unstripped"*
counted a numerator over 86 items - it incremented before the two leaking pairs were
dropped - against a denominator of 82. The frozen figure is **3 of 82**.

### What was corrected, and what was NOT

**Corrected** - these are retractions of demonstrably false statements, not a third
round of fixing, and none of them touches a threshold or a definition:

1. the numerator bug (`src/eval_set.py`), so numerator and denominator describe the
   same set. **3 of 82**, matching round 2's independent re-derivation;
2. the module docstring, which still declared the rule the body had replaced;
3. the `9/9 caught` claim, retracted in all four documents, with the original tables
   **kept** and the retraction written beside them;
4. the `32/38` figure, withdrawn and replaced with a scripted `36/50`;
5. ERRATA E-2's attribution of all +3 pairs to F2. **Measured: F2 alone gives 39/78**,
   so F2 recovers one pair and F1's new selection recovers two;
6. the missing rule-level test. Round 2's `test_R1` runs `build_pairs` over the real
   corpus, so the RULE has a test of its own. Against a green baseline of 278 passed,
   the corrected harness `docs/reviews/ch03-probe2/mutate3.py` reports **6 caught, 0
   missed**.

**NOT done: no third review round.** CH-03's state is **`reviewed-FAIL ×2, escalated`**
and it is **not** claimed to pass.

### The three open items the architect must rule on

1. **The pre-registration says the RESTRICTED set is primary; the shipped primary is
   the unrestricted one.** Pre-registration section 2 fixes the >= 0.90 per-document
   floor as primary *"precisely so that it cannot later be chosen for its effect on
   n"*. The shipped primary is unrestricted: **41 pairs against 1**. `Q16` records the
   contradiction, both readings and both counts, and both sets are built and
   committed - but **Q16 asks for a ruling it has already acted on**, and round 2 is
   right to call that an open Class A deviation. **The re-run CHECKPOINT's GREEN rests
   on it.**
2. **Whether the corrections above are legitimate**, or whether the strike rule should
   have frozen CH-03 exactly as it stood at the second FAIL. My reading: retracting a
   false number is not "fixing a chunk", and leaving a knowingly false figure published
   would violate hard rule 14 more seriously than the strike rule protects against.
   **That reading is mine and it is the architect's to overturn.**
3. **Whether CH-03 may be used at all** in its current state. Everything downstream -
   CH-04's scorer, the B-script arm, the ★ CHECKPOINT's GREEN - is computed on this
   eval set.

### What round 2 confirmed is SOUND

Worth stating, because two FAIL verdicts could otherwise read as a broken chunk:

- the reviewer's own best label-blind attack reaches **0.6585** and sits at **p =
  0.4671** inside its own permutation null. **Every structural attack is dead**:
  numeric section sort 0.5244, lexicographic 0.5366, part number 0.5610,
  position-in-document <= 0.5976, and an attack on the selection rule itself 0.5122;
- 41 pairs / 82 items, every ladder rung, the strip counts, and all 82 `section_text`
  values reproduce **exactly** against an independent implementation;
- exact instruction-count matching holds; determinism is byte-for-byte; `refetch
  --verify-only` is green; `data/ednotes/` and `data/amdpars/` are untouched; and the
  goldens genuinely predate the code they test.

**The eval set is sound in substance. The evidence about it was not, and that is the
finding.**


---

## ARCHITECT RULINGS — 2026-08-31, recorded at the head of CH-06 before any other work

These three arrived together at the opening of the CH-06 build session and are
transcribed **verbatim**, before the session touched anything else, so that the record
of the ruling predates every artifact built under it.

```
Q19 - RULED by ARCHITECT, 2026-08-31.
The primary eval set is the UNRESTRICTED one, 41 pairs / n=82. GOOD.md
pre-registered the RESTRICTED set as primary; the restricted set yields ONE pair
and measures nothing. The pre-registration is therefore DEVIATED FROM, and the
deviation is disclosed prominently in the README and in every results table -
never absorbed. Both sets stay built and committed so a judge can run either.
The reason the restriction existed (so the set could not later be chosen for its
effect on n) is honoured differently: the choice is recorded here, before the A1
arm ran, and the restricted result is published beside the unrestricted one.

Q16 - RULED by ARCHITECT, 2026-08-31.
The pre-registered success criterion requires n >= 84. The corpus yields 82.
THE CRITERION IS NOT MOVED. The result is reported as n=82 against a criterion
written for 84, with the two-item shortfall stated plainly wherever the criterion
is quoted. The gap and the p-value carry the claim; the criterion is reported as
unmet-on-n and met-on-effect, both stated.

MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31.
The sonnet-5 subset is a HARNESS DEFECT, not a finding: 13 of 20 B0-agent-sonnet
predictions came back EMPTY and were scored as failures. The check did not run.
It is withdrawn entirely, the artifacts are kept, and no sensitivity claim is
made anywhere in the submission. Do not re-run it - the clock is better spent on
A1.
```

### What each ruling obliges this session to do

| Ruling | Binding consequence for CH-06 and everything downstream |
|---|---|
| **Q19** | `data/evalset/` (41 pairs, n = 82) is primary for every A1 arm. **The deviation from `GOOD.md` §11 is disclosed in every results table**, never absorbed into a footnote. `data/evalset-restricted/` stays committed and runnable. |
| **Q16** | `GOOD.md`'s `n >= 84` is **not moved**. Every quotation of the success criterion in this session's output states the two-item shortfall in the same breath. The criterion is reported split: **unmet on n, evaluated on effect.** |
| **Sensitivity** | The `-sonnet` rows are **withdrawn**. No sensitivity claim appears in any CH-06 artifact. The artifacts stay on disk under `docs/evidence/checkpoint/` and are labelled withdrawn where they are cited. Not re-run. |

**Q19 and Q16 are hereby CLOSED as ruled.** The escalation that opened them
(`STATUS.md`, CH-03 `reviewed-FAIL ×2 → ESCALATED`) is answered on points 1 and 3 of
its three open items: the unrestricted set is sanctioned as primary, and CH-03 may be
used downstream. **Point 2 — whether CH-03's post-strike corrections were legitimate —
is not addressed by these rulings and remains open.**

### The withdrawn sensitivity check — the defect, stated in numbers

The row is withdrawn on a mechanical fact, not on a judgement about the result. Of the
20 `B0-agent-sonnet` calls, **13 returned an empty text block** and `score.py`
correctly charged each as a failure, because `GOOD.md` §1 fixes that a non-answer is a
FAILURE and never a skip. That rule is right and it is not being relaxed here: what is
withdrawn is the *inference*, because an arm that produced no output on 65% of its
items measured the harness, not the model. `MAX_TOKENS = 16` with no `temperature`
field is the live suspect and it is not investigated, by ruling.

**The checkpoint's GREEN branch is untouched by this withdrawal**, because it was
decided on the full-corpus haiku arms alone — `plan.md`'s branch table reads `B0` and
`B0-agent` and never reads the sensitivity subset.
