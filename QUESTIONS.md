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
