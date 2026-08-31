# CH-11c — the adversarial half of the shipping-surface sweep

**Workflow run `wf_74534735-795`, 2026-08-31. 21 agents, 0 errors, 971 tool calls,
2,094,887 subagent tokens, 2,170 s wall-clock. Model `claude-opus-5[1m]` throughout.**

Shape: one **read-only auditor per shipping file** (10), then one **adversarial
refuter per file** told to kill that file's findings and to default to *refuted* when
uncertain (10), then one **completeness critic** asked what the sweep missed (1).
No agent could edit a file; every one was told to run commands rather than recall.

**This is generated verbatim from the workflow journal**
(`journal.jsonl`, one `result` line per agent) — no finding is paraphrased, dropped or
re-scored by hand. A finding marked SURVIVED is one a single refuter failed to kill;
**that is not the same as confirmed**, and it is not reported as such.

## Tally

| file | lines read | findings | refuted | survived | could-not-check |
|---|---:|---:|---:|---:|---:|
| `AI-USE.md` | 642 | 19 | 3 | **16** | 5 |
| `CHANGELOG.md` | 400 | 7 | 1 | **6** | 5 |
| `PROVENANCE.md` | 121 | 8 | 2 | **6** | 7 |
| `QUESTIONS.md` | 2568 | 11 | 2 | **9** | 5 |
| `README.md` | 529 | 5 | 0 | **5** | 5 |
| `REPRODUCE.md` | 311 | 6 | 5 | **1** | 6 |
| `SAFETY.md` | 150 | 3 | 2 | **1** | 3 |
| `STATUS.md` | 53 | 8 | 3 | **5** | 5 |
| `SUBMISSION.md` | 152 | 4 | 0 | **4** | 6 |
| `THIRD-PARTY.md` | 137 | 4 | 0 | **4** | 6 |
| **TOTAL** | | **75** | **18** | **57** | **53** |

Severity as the auditors assigned it, over all 75 raised: **2 blocker · 44 material · 29 cosmetic**.

## What CH-11c acted on, and what it did not

**CH-11c's mandate was five named corrections.** The sweep was commissioned by the
same chunk card, which asks it to *report* what it finds. Four surviving findings were
also fixed, because each fell inside the fence AND inside something the card explicitly
named:

| finding | why it was fixed here |
|---|---|
| `PROVENANCE.md:92` — *"every evaluation arm, temperature 0"* is false; `B0prime` ran at **1.0** | **CH-11c wrote that qualifier itself**, an hour earlier, while correcting the model name. A chunk fixes its own defect. |
| `AI-USE.md:307` — the NIGHT-RUN heading read *"CH-03 FAILED then FIXED"* | The card's §6 names *"any claim that a gate passed when it did not"*. CH-03 is `reviewed-FAIL ×2 → ESCALATED`; Q19 says in terms that it is **not** claimed to pass. |
| `AI-USE.md:50` — *"spend to date: USD 1.935538 over 1038 logged runs"* | The card's §6 names *"every numeric claim — does that path contain that number?"*. The ledger holds 2,107 rows / USD 11.632274. |
| `README.md:509` — *"QUESTIONS.md — 31 entries"* | Same clause. `grep -c '^## Q'` gives **38**, and CH-11c itself added three of them. |
| `README.md:217` — *"the only arm in the packet not at temperature 0"* | Adjacent to the Q34 paragraph CH-11c rewrote; the two withdrawn sonnet arms also ran off 0. |

**Everything else is reported and NOT fixed.** Fixing ~50 further findings is a
different chunk: several are Class A, several need the architect's triage, and two of
the affected files (`REPRODUCE.md`, `SAFETY.md`) are outside this chunk's fence
entirely. They are recorded at `QUESTIONS.md` **Q39** rather than absorbed.

---

## Every finding, verbatim

### `AI-USE.md` — 642 lines read, 19 findings

**SURVIVED · line 50 · blocker · number-path-disagrees**

> **Measured spend to date: USD 1.935538 over 1038 logged runs** (1,761,960 input / 8,880 output tokens), against the USD 18.00 ceiling enforced in `src/runlog.py`.

- **problem:** This is presented as the project's spend TO DATE. It is not: it is exactly the NIGHT-RUN subset (arms B0, B0-agent, B0-sonnet, B0-agent-sonnet, probe-model-id = 1038 rows, USD 1.935538, 1,761,960 in / 8,880 out). The ledger total is USD 11.632274 over 2,107 rows. The same file says 11.6323 at lines 93, 203, 215, 218 and 305, so the file contradicts itself and understates headline spend by 6x (11% of ceiling instead of 65%).
- **auditor checked:** python over docs/evidence/runs/cost_ledger.csv: TOTAL USD 11.632274, rows 2107, empty 3. Filtering to arm in (B0,B0-agent,B0-agent-sonnet,B0-sonnet,probe-model-id): rows 1038, usd 1.935538, in 1761960, out 8880.
- **refuter (could not kill it):** Could not kill it. I re-ran the ledger myself: TOTAL USD 11.632274 over 2107 rows, 3 empty cells; filtering arm in (B0,B0-agent,B0-agent-sonnet,B0-sonnet,probe-model-id) reproduces EXACTLY 1038 rows / USD 1.935538 / 1,761,960 in / 8,880 out. So the figure is the night-run subset wearing a project-level label. I looked for an exculpating qualifier and there is none: lines 44-53 are the project-level Models section, the sentence says 'to date' with no date and no arm scope, and the file's own line 305 says 'USD 11.6323 committed in total against the 18.00 ceiling, 2,107 logged runs'. Not a dated correction, not a differently-formatted match. Blocker stands: 11% of ceiling shown where 65% is true.
- **refuter ran:** `python -c "import csv;rows=list(csv.DictReader(open('docs/evidence/runs/cost_ledger.csv')));print(sum(float(r['imputed_usd']) for r in rows if r['imputed_usd'].strip()),len(rows));sub={'B0','B0-agent','B0-agent-sonnet','B0-sonnet','probe-model-id'};s=[r for r in rows if r['arm'] in sub];print(len(s),sum(float(r['imputed_usd']) for r in s if r['imputed_usd'].strip()),sum(int(r['input_tokens']) for `

**SURVIVED · line 36 · material · number-path-disagrees**

> | Claude Haiku 4.5 | **`claude-haiku-4-5-20251001`** | **USED** — every evaluation arm. 951 logged calls | $1.00 / $5.00 per MTok |

- **problem:** The MODEL NAME is correct (dated haiku on every evaluation arm — verified). The COUNT is stale. The ledger has 2,020 rows for claude-haiku-4-5-20251001. 951 is the NIGHT-RUN session subtotal only (B0 474 + B0-agent 474 + probe 3), correctly reported as such at line 317 but wrongly reused here as the project-level total.
- **auditor checked:** python collections.Counter over cost_ledger.csv grouped by model: {'claude-haiku-4-5-20251001': 2020, 'claude-sonnet-5': 84, 'claude-haiku-4-5': 3}. Per-arm: A1 249, A1-iter1 82, A1-minus-tool 164, B0 474, B0-agent 474, B0-agent-currenttext 82, B0prime 492, probe 3 = 2020.
- **refuter (could not kill it):** Survives. collections.Counter over the ledger's model column gives claude-haiku-4-5-20251001: 2020 (A1 249 + A1-iter1 82 + A1-minus-tool 164 + B0 474 + B0-agent 474 + B0-agent-currenttext 82 + B0prime 492 + probe 3). 951 = 474+474+3, the night-run session subtotal, and it is correctly scoped at line 317 inside the dated NIGHT-RUN entry ('| claude-haiku-4-5-20251001 | 951 |'). Line 36 is the project-level Models table and carries no date or scope, so the same number there is simply stale. I could not find any subset or formatting of 951 that matches the project-level claim. Model NAME is right; count is wrong by 1069 calls.
- **refuter ran:** `python -c "import csv,collections;rows=list(csv.DictReader(open('docs/evidence/runs/cost_ledger.csv')));print(collections.Counter(r['model'] for r in rows));print(collections.Counter((r['model'],r['arm']) for r in rows))"`

**SURVIVED · line 20 · material · number-path-disagrees**

> | **Solution** | the evaluation arms — the thing being measured | **1028** logged runs across B0, B0-agent and the sonnet subset | `docs/trajectories/arms/<arm>-rep<N>.jsonl` ... + `docs/evidence/runs/cost_ledger.csv`

- **problem:** The class is defined as 'the evaluation arms'. The cited ledger has 2,097 evaluation-arm rows (2,107 minus 10 probe rows). 1028 counts only B0 + B0-agent + the two sonnet arms and silently omits A1 (249), A1-iter1 (82), A1-minus-tool (164), B0prime (492) and B0-agent-currenttext (82) — i.e. every arm of the advanced solution this file elsewhere describes.
- **auditor checked:** python over cost_ledger.csv: 474+474+40+40 = 1028; total rows 2107; probe-model-id rows 10; evaluation-arm rows 2097.
- **refuter (could not kill it):** Survives, though weaker than the auditor states. My best refutation was that the cell is self-scoped - it names 'B0, B0-agent and the sonnet subset' and 474+474+40+40 = 1028 exactly, so it is not 'silent'. But the Count column of that table is the agent-class total (the other rows give class totals: ~90 research, 6 coding, 12 audit), and the class is defined as 'the evaluation arms'. The cited ledger holds 2097 evaluation-arm rows (2107 minus 10 probe-model-id), and every A1 arm - the advanced solution this same file describes at length - is outside the 1028. The file's own line 305 says 2,107 logged runs. Stale class count; the enumeration only documents which arms it forgot.
- **refuter ran:** `python -c "import csv,collections;rows=list(csv.DictReader(open('docs/evidence/runs/cost_ledger.csv')));c=collections.Counter(r['arm'] for r in rows);print(c);print('total',len(rows),'probe',c['probe-model-id'],'eval-arm',len(rows)-c['probe-model-id'])"`

**SURVIVED · line 18 · material · internal-contradiction**

> | **Coding** | fresh Claude Code BUILD and REVIEW sessions that write this repository | **6** — CH-00, CH-01, CH-02, SPEC-FIX-1, SPEC-FIX-2, NIGHT-RUN | `docs/trajectories/build/<CHUNK-ID>.jsonl`

- **problem:** The count and the enumeration are stale. The same file's own session log carries 9 entries (CH-11, CH-14a, CH-06->CH-08->CH-09, NIGHT-RUN, SPEC-FIX-2, SPEC-FIX-1, CH-02, CH-01, CH-00), and the cited directory holds 10 trajectory files. CH-06, CH-11, CH-14a and NIGHT-RUN-FINAL are all missing from the list.
- **auditor checked:** grep -n '^### ' AI-USE.md -> 9 headings at lines 90,212,272,307,347,420,500,564,607. ls docs/trajectories/build/ -> CH-00, CH-01, CH-02, CH-06, CH-11, CH-14a, NIGHT-RUN-CHECKPOINT, NIGHT-RUN-FINAL, SPEC-FIX-1, SPEC-FIX-2 (10 .jsonl).
- **refuter (could not kill it):** Survives. `grep -n '^### ' AI-USE.md` returns 9 session headings (lines 90 CH-11, 212 CH-14a, 272 CH-06->CH-08->CH-09, 307 NIGHT-RUN, 347 SPEC-FIX-2, 420 SPEC-FIX-1, 500 CH-02, 564 CH-01, 607 CH-00), and the cited directory holds 10 .jsonl files (CH-00, CH-01, CH-02, CH-06, CH-11, CH-14a, NIGHT-RUN-CHECKPOINT, NIGHT-RUN-FINAL, SPEC-FIX-1, SPEC-FIX-2). The row is not dated or scoped to a moment, and CH-11 - which wrote this very version of the file - is missing from its own enumeration. Undercounts by at least 3 sessions and 4 trajectory files.
- **refuter ran:** `grep -n '^### ' AI-USE.md; ls -la docs/trajectories/build/`

**SURVIVED · line 19 · material · internal-contradiction**

> SPEC-FIX-1: ten agents, 4–1 against the verdict the session then reached. **NIGHT-RUN: two CH-03 gate reviewers with zero shared context ...** | **12** |

- **problem:** The adversarial-audit count of 12 is stale by a factor of five against the same file. Line 102 discloses 52 audit subagents in CH-11 and line 296 discloses one CH-04 gate reviewer under CH-06, giving 10+2+52+1 = 65 (STATUS.md line 43 adds CH-11c's 31-agent sweep). The summary table understates the project's own largest disclosure.
- **auditor checked:** grep -n 'Subagents' AI-USE.md -> line 102 '52 in one workflow', line 296 'Subagents: one', line 321 'Subagents: two', line 427 panel of ten. Journal on disk for wf_44b0dd6c-5e5: 52 'started' + 52 'result' records.
- **refuter (could not kill it):** Survives. `grep -in subagent AI-USE.md` gives line 102 '**Subagents: 52 in one workflow**' (CH-11, with workflow id wf_44b0dd6c-5e5 and a stage table of 8 + 44), line 296 '**Subagents: one.**' (the CH-04 gate reviewer under the CH-06 entry), line 321 '**Subagents: two**' (NIGHT-RUN), and the SPEC-FIX-1 panel of ten at 430-437. 10 + 2 + 52 + 1 = 65 against a summary count of 12. The 12 predates the CH-11 workflow, but the row is undated and sits above an entry that discloses the 52 as 'the largest disclosure in this entry'. The summary table understates the file's own biggest disclosure by 5x.
- **refuter ran:** `grep -n -i 'subagent' AI-USE.md`

**SURVIVED · line 307 · blocker · false-gate-pass**

> ### NIGHT-RUN · 2026-08-31 · Claude Code · `claude-opus-5` · BUILD, UNATTENDED · **CH-03 FAILED then FIXED · CHECKPOINT GREEN**

- **problem:** 'FAILED then FIXED' asserts the CH-03 gate was satisfied on re-review. It was not: the round-2 reviewer returned FAIL, CH-03 is reviewed-FAIL x2 -> ESCALATED. The entry's body (line 324) says only 'The second re-reviews the fix' and never states the outcome, so the heading is the only verdict a reader gets and it is the wrong one. The commit that landed the escalation (a7ddf90) states in its own message 'CH-03 is reviewed-FAIL x2, ESCALATED, and is NOT claimed to pass' and edited this very section without correcting the heading.
- **auditor checked:** grep -ni 'verdict' docs/reviews/REVIEW_CH-03-round2.md -> line 3 '## VERDICT: **FAIL**'. git log --date=iso -- docs/reviews/REVIEW_CH-03-round2.md -> c3c416e 2026-08-31 04:33:07, i.e. 20 min AFTER the AI-USE NIGHT-RUN entry (47ce128, 04:13:57); AI-USE.md has been rewritten 5 times since (up to 810e2b1, 11:41) without fixing it.
- **refuter (could not kill it):** Could not kill it, and it got worse on inspection. docs/reviews/REVIEW_CH-03-round2.md line 3 is '## VERDICT: **FAIL**' and its body states 'CH-03 nevertheless fails its gate' on four grounds. QUESTIONS.md Q19 (line 983) is titled 'CH-03 FAILED review TWICE. Strike limit reached, ESCALATED'. The heading is the only verdict in the entry - the body at line 344 says merely 'The second re-reviews the fix'. I tested the 'dated record, old text survives' defence and it fails: `git show a7ddf90 -- AI-USE.md` shows the escalation commit editing THIS section (the ordering-bias line, 32/38 -> 36/50) while leaving the heading, and `grep -in 'escalat|strike|reviewed-FAIL'` over AI-USE.md returns nothing about CH-03's second FAIL anywhere in the file. Blocker stands: the file asserts a gate pass that never happened.
- **refuter ran:** `grep -ni 'verdict' docs/reviews/REVIEW_CH-03-round2.md | head; git log --date=iso --format='%h %ad %s' -- docs/reviews/REVIEW_CH-03-round2.md; git show a7ddf90 -- AI-USE.md | grep -n '^[-+@]'; grep -n -i 'escalat\|strike\|reviewed-FAIL' AI-USE.md`

**SURVIVED · line 379 · material · number-path-disagrees**

> | output | 126,862 | ... | input, cache write | 250,800 | | input, cache read | 10,327,144 | | **total input** | **10,578,142** | | assistant turns | 99 |

- **problem:** Line 371 cites 'committed output: docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt'. That file disagrees on EVERY row: turns 102 (not 99), output 132,805 (not 126,862), uncached 204 (not 198), cache write 252,525 (not 250,800), cache read 10,797,901 (not 10,327,144), TOTAL INPUT 11,050,630 (not 10,578,142). The imputed costs at lines 388-389 (56.062260 / 9.903612) likewise disagree with the artifact's 58.573275 / 10.298377.
- **auditor checked:** cat docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt -> 'assistant turns : 102 / output tokens 132,805 / input, uncached 204 / input, cache write 252,525 / input, cache read 10,797,901 / TOTAL INPUT 11,050,630 / upper bound USD 58.573275 / cache-adjusted USD 10.298377'.
- **refuter (could not kill it):** Survives. cat of the cited artifact gives turns 102, output 132,805, uncached 204, cache write 252,525, cache read 10,797,901, TOTAL INPUT 11,050,630, upper bound 58.573275, cache-adjusted 10.298377 - every row different from the table. I checked for an earlier revision that matches: `git rev-list --all -- <path>` returns a single commit (28a59e3) and its content is identical to the working tree, so there is no superseded version carrying 126,862. The nearby caveat 'snapshot taken before the closing commits, so the true totals are marginally higher' does not save it - the artifact carries that same caveat and is the thing the line names as 'committed output'.
- **refuter ran:** `cat docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt; for c in $(git rev-list --all -- docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt); do git show $c:docs/evidence/spec-fix-2/spec-fix-2-session-cost.txt | grep -E 'assistant turns|output tokens|TOTAL INPUT'; done`

**SURVIVED · line 393 · material · number-path-disagrees**

> **10.58 M — 2.1× over**. It is nonetheless the lowest figure any chunk has recorded (CH-00 21.72 M · CH-01 41.09 M · CH-02 41.58 M · SPEC-FIX-1 19.15 M coding + 23.25 M panel)

- **problem:** Three derived figures inherit the stale table above: against the cited artifact's 11,050,630 the miss is 2.21x not 2.1x, the 'a 4.0x reduction' at line 363 is 3.84x (42,406,971 / 11,050,630), and line 396's '10.33 M of the 10.58 M is cache read' is 10.80 M of 11.05 M. The CH-02 entry in the comparison list (41.58 M) is itself stale — see the CH-02 finding.
- **auditor checked:** python: 11050630/5e6 = 2.210; 42406971/11050630 = 3.838; artifact cache read 10,797,901 of 11,050,630. Cross-checked against docs/evidence/spec-fix-1/spec-fix-1-panel-cost.txt (23,254,519) and spec-fix-1-session-cost.txt (19,152,452), both of which DO match the file.
- **refuter (could not kill it):** Survives as a derivative of the SPEC-FIX-2 table. Against the artifact's 11,050,630: 11050630/5e6 = 2.210 (not 2.1x); (19,152,452 + 23,254,519)/11,050,630 = 3.838 (not the '4.0x reduction' at line 362); cache read is 10,797,901 of 11,050,630, not '10.33 M of the 10.58 M' at line 396. The two SPEC-FIX-1 figures in the comparison list DO match their artifacts (19,152,452 and 23,254,519), and CH-00 21.72 M and CH-01 41.09 M match theirs - which is what makes the CH-02 entry (41.58 M against an artifact of 42,212,741) stale too. Only the SPEC-FIX-2-derived numbers are wrong, and they are wrong in the direction that flatters the chunk.
- **refuter ran:** `grep -n 'TOTAL INPUT' docs/evidence/spec-fix-1/*.txt docs/evidence/ch00-session-cost.txt docs/evidence/ch01-pool/*.txt docs/evidence/ch02-attributor/*.txt docs/evidence/spec-fix-2/*.txt; python -c "print(11050630/5e6,(19152452+23254519)/11050630)"`

**SURVIVED · line 522 · material · number-path-disagrees**

> | output | 514,051 | | input, uncached | 478 | | input, cache write | 626,057 | | input, cache read | 40,957,406 | | **total input** | **41,583,941** |

- **problem:** Line 514 cites 'committed output: docs/evidence/ch02-attributor/ch02-session-cost.txt'. That file disagrees on every row: turns 241 (line 509 says 239), output 515,671, uncached 482, cache write 627,283, cache read 41,584,976, TOTAL INPUT 42,212,741. The imputed costs at lines 530-531 (220.770980 / 37.245224) disagree with the artifact's 223.955480 / 37.607192. The file was committed once only, so there is no later revision that matches. Line 537's derived '1.2% higher' than CH-01 becomes 2.7% on the artifact's number.
- **auditor checked:** cat docs/evidence/ch02-attributor/ch02-session-cost.txt -> 'assistant turns : 241 / output tokens 515,671 / input, uncached 482 / input, cache write 627,283 / input, cache read 41,584,976 / TOTAL INPUT 42,212,741 / upper bound USD 223.955480 / cache-adjusted USD 37.607192'. git log -- that path -> single commit 215052e.
- **refuter (could not kill it):** Survives. The cited artifact gives turns 241 (the entry says 239), output 515,671, uncached 482, cache write 627,283, cache read 41,584,976, TOTAL INPUT 42,212,741, upper bound 223.955480, cache-adjusted 37.607192 - no row matches. `git log -- docs/evidence/ch02-attributor/ch02-session-cost.txt` returns exactly one commit (215052e), so there is no earlier revision the table could be quoting. The derived '1.2% higher than CH-01' at line 537 becomes 2.7% on 42,212,741 against CH-01's 41,093,185 (which does match its own artifact).
- **refuter ran:** `cat docs/evidence/ch02-attributor/ch02-session-cost.txt; git log --format='%h %ad %s' --date=iso -- docs/evidence/ch02-attributor/ch02-session-cost.txt`

**SURVIVED · line 505 · material · number-path-disagrees**

> - **Trajectory:** `docs/trajectories/build/CH-02.jsonl` (644 lines, 1,574,519 B; 660 home-path substitutions, every other scrub category an explicit 0).

- **problem:** The file at that path is 709 lines / 1,689,144 bytes. 644 lines / 1,574,519 B is the FIRST export (commit 215052e); the session was deliberately re-exported at 940c0b9 ('re-export CH-02 to cover the commits made after the first export') and this line was never refreshed. Compare line 568, where CH-01's 672 lines / 1,433,689 B does match the current file.
- **auditor checked:** wc -l docs/trajectories/build/CH-02.jsonl -> 709; ls -la -> 1689144 bytes. git show 215052e:docs/trajectories/build/CH-02.jsonl | wc -c -> 1574519, | wc -l -> 644. git log --follow -> two commits, 215052e then 940c0b9.
- **refuter (could not kill it):** Survives. wc -l on the shipped file gives 709 and ls gives 1,689,144 B. `git show 215052e:docs/trajectories/build/CH-02.jsonl | wc -lc` gives exactly 644 / 1,574,519 - so the line describes the superseded first export, and `git log --follow` shows the deliberate re-export at 940c0b9 ('re-export CH-02 to cover the commits made after the first export') which never refreshed this line. CH-01's parallel line (672 lines / 1,433,689 B) does match its file, which rules out any convention of quoting export-time figures.
- **refuter ran:** `wc -l docs/trajectories/build/CH-02.jsonl; ls -la docs/trajectories/build/CH-02.jsonl; git log --follow --format='%h %ad %s' --date=iso -- docs/trajectories/build/CH-02.jsonl; git show 215052e:docs/trajectories/build/CH-02.jsonl | wc -lc`

**SURVIVED · line 507 · material · number-path-disagrees**

> - **Wall-clock:** first turn 14:43:18 UTC → last 15:30:55 UTC = **47.6 min**, against the ~3 h unattended window `prompts/CH-02.md` allowed.

- **problem:** Measured against the trajectory this entry cites, the CH-02 session's assistant turns run 14:43:21.021Z to 18:16:43.050Z = 213.4 minutes, not 47.6. 47.6 min matches only the superseded first export (14:43:21 -> 15:30:45 = 47.4 min). As shipped the entry claims the chunk came in 4x under its window when the re-exported record shows it ran roughly to the window's edge.
- **auditor checked:** python over docs/trajectories/build/CH-02.jsonl assistant timestamps -> first 2026-08-30T14:43:21.021Z, last 2026-08-30T18:16:43.050Z, 213.37 min. Same computation over git show 215052e:... -> 14:43:21.021Z to 15:30:45.240Z, 47.4 min.
- **refuter (could not kill it):** Survives. Parsing assistant timestamps out of the shipped trajectory gives first 2026-08-30T14:43:21.021Z, last 2026-08-30T18:16:43.050Z = 213.4 min across 268 assistant turns (the entry claims 239). The 47.6 min only reconciles with the superseded first export. This is not a harmless staleness: 213 min exceeds the '~3 h window' the sentence claims the chunk beat by 4x, so the shipped record contradicts its own comparison. Same root cause as the 644-line finding, but a separately wrong claim.
- **refuter ran:** `python -c "import json;ts=[json.loads(l).get('timestamp') for l in open('docs/trajectories/build/CH-02.jsonl',encoding='utf-8',errors='replace') if l.strip()];" ; python - <<'EOF' import json ts=[] for ln in open('docs/trajectories/build/CH-02.jsonl',encoding='utf-8',errors='replace'):     try: r=json.loads(ln)     except: continue     if r.get('timestamp') and (r.get('type')=='assistant' or (r.ge`

**SURVIVED · line 255 · material · number-without-path**

> uploaded zip; the zip is 10.24 MB. Q25 measured the uncompressed tree and its four proposed remedies — compress, relocate, sample, or unseal `data/` — were all unnecessary.

- **problem:** No path is cited for 10.24 MB and no committed artifact contains it. The CH-14a size evidence says 10,182,500 B = 10.18 MB (selection-rule.md, inventory.md, derived-reproduction.md) and the clean-clone rehearsal — the measurement of the actual uploaded zip — says 10,613,737 B = 10.61 MB. REPRODUCE.md line 21 carries both real figures; AI-USE and STATUS.md carry a third that reproduces from neither.
- **auditor checked:** grep -rn '10,24|10\.24 MB|10,2[0-9][0-9],[0-9]' docs/evidence/ -> no matches. grep -n 'zip' docs/evidence/ch14-clean-clone/rehearsal.txt -> 'zip 10,613,737 B = 10.61 MB'. docs/evidence/ch14-size/selection-rule.md:77 -> '10,182,500 B = 10.18 MB'.
- **refuter (could not kill it):** Survives. A repo-wide grep for 10.24 / '10,24' across .md and .txt returns exactly two hits - AI-USE.md:255 and STATUS.md:39 - and no artifact anywhere. The two measured figures are docs/evidence/ch14-size/selection-rule.md:77 '10,182,500 B = 10.18 MB' (git archive) and docs/evidence/ch14-clean-clone/rehearsal.txt:32 'zip 10,613,737 B = 10.61 MB' (the actual uploaded artifact). REPRODUCE.md line 21 carries both and reconciles them; AI-USE carries a third number that reproduces from neither and cites no path. I checked whether 10.24 could be a MiB restatement - 10.18 MB is 9.71 MiB and 10.61 MB is 10.12 MiB, so no. Hard rule 14 violation, and it is the number the '4.9x under cap' claim rests on.
- **refuter ran:** `grep -rn '10\.24\|10,24' --include='*.md' --include='*.txt' . | grep -v '^./.git'; grep -n 'zip' docs/evidence/ch14-clean-clone/rehearsal.txt; grep -rn '10,182,500' docs/evidence/ch14-size/`

**REFUTED · line 267 · material · other**

> The first version's output is preserved in git history.

- **problem:** It is not. docs/evidence/secret-scan/scan.txt has exactly two committed revisions (0f3f4fe: 450 blobs/81 commits, VERDICT PASS 0 findings; 263ed29: 462/84, VERDICT PASS 0 findings) — neither is the 74-finding FAIL run. The generating script scan_history.py exists in history only at TOOL_VERSION 1.1.0 and 1.2.0; v1.0.0, the version that produced the 74 findings, was never committed. The 74 figure survives only as prose in PROGRESS.md, which is exactly the evidence-free form hard rule 14 forbids.
- **auditor checked:** git log -- docs/evidence/secret-scan/scan.txt -> 0f3f4fe, 263ed29. git show 0f3f4fe:... | grep VERDICT -> 'VERDICT: PASS - 0 findings.' git grep '74 findings|74 false|cried wolf' $(git rev-list --all) -> hits only in AI-USE.md/PROGRESS.md/STATUS.md prose. TOOL_VERSION at 0f3f4fe = 1.1.0, at 263ed29 = 1.2.0.
- **refuter (refuted):** REFUTED - the auditor grepped the wrong artifact. The v1.0.0 output IS in git history: docs/trajectories/build/CH-14a.jsonl, committed at 2453998 and present at HEAD, contains the full run verbatim - 'VERDICT: FAIL - 74 finding(s). Matched TEXT IS NOT PRINTED.' followed by the finding list ('anthropic-prefix-any 73f333cc0527 line 204 .githooks/pre-commit', etc). `git show HEAD:docs/trajectories/build/CH-14a.jsonl | grep -c 'VERDICT: FAIL - 74 finding'` returns 1. The auditor searched only scan.txt's revisions and grepped the string '74 findings', while the output says '74 finding(s)'; their own git grep used '|' alternation without -E, which cannot match. The scanner's committed docstring (scan_history.py lines 18-31) also narrates it. Sentence is true as written.
- **refuter ran:** `git show HEAD:docs/trajectories/build/CH-14a.jsonl | grep -c 'VERDICT: FAIL - 74 finding'; git show 2453998:docs/trajectories/build/CH-14a.jsonl | grep -c 'VERDICT: FAIL - 74 finding'; grep -o '.\{120\}VERDICT: FAIL - 74 finding(s).\{160\}' docs/trajectories/build/CH-14a.jsonl | head -1`

**SURVIVED · line 57 · material · other**

> **Fairness constraint:** every evaluation arm gets the *same* model. ... and the model-sensitivity check turns that limit into a number instead of a caveat.

- **problem:** The model-sensitivity check was WITHDRAWN by ruling, so it produced no number. QUESTIONS.md Q19: 'The sonnet-5 subset is a HARNESS DEFECT, not a finding: 13 of 20 B0-agent-sonnet predictions came back EMPTY... The check did not run. It is withdrawn entirely... no sensitivity claim is made anywhere in the submission.' AI-USE makes one here, and line 38 also presents the subset as live ('**USED** — model-sensitivity check only, 20-item subset') with no mention of the withdrawal. Every other shipping file (README.md:144, PROVENANCE.md:93, REPRODUCE.md:233-234, CHANGELOG, STATUS) labels these rows withdrawn; AI-USE.md is the only one that does not.
- **auditor checked:** sed -n '1108,1145p' QUESTIONS.md (Q19 withdrawal text quoted above). grep -rn -i 'withdraw' AI-USE.md -> only lines 335-336, about the checkpoint's defective-eval-set figures, nothing about sonnet. docs/evidence/ch11c-sweep/ch11c-verify.txt:32 '[PASS] claude-sonnet-5 appears ONLY on the withdrawn subset and the model-id probe'.
- **refuter (could not kill it):** Survives. The withdrawal ruling is real - QUESTIONS.md line 1110 'MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31 ... 13 of 20 B0-agent-sonnet predictions came back EMPTY ... The check did not run. It is withdrawn entirely ... no sensitivity claim is made anywhere in the submission', with the binding row at line 1124. AI-USE line 57 makes exactly that claim in the present tense, and `grep -in 'withdraw|sonnet' AI-USE.md` returns only lines 20, 38, 318 (all presenting the subset as live) and 335-336 (a different withdrawal, the defective-eval-set checkpoint numbers). The file's own CH-11c-signed corrections elsewhere show it is maintained, so this is not a frozen dated record. AI-USE.md is the only shipping file that does not label these rows withdrawn.
- **refuter ran:** `sed -n '1108,1128p' QUESTIONS.md; grep -n -i 'withdraw\|sonnet' AI-USE.md`

**REFUTED · line 88 · material · internal-contradiction**

> Newest first. Every build session appends one row here **and** exports its transcript.

- **problem:** CH-11c does neither, and the file knows it exists: line 235 is a correction signed '(CH-11c)'. CH-11c has at least four commits, edited AI-USE.md, PROVENANCE.md, QUESTIONS.md and STATUS.md, and ran a 31-agent adversarial sweep (STATUS.md line 43) — but it has no session-log heading and no docs/trajectories/build/CH-11c.jsonl. Under CLAUDE.md end-of-session duty 6 that makes the chunk not done, and under hard rule 13 it is an undisclosed agent run in the file whose entire purpose is disclosure.
- **auditor checked:** grep -n '^### ' AI-USE.md -> 9 headings, none CH-11c. ls docs/trajectories/build/ | grep -i 11c -> empty. git log --all --oneline | grep -i 'CH-11c' -> a0432e7, b5ebcbd, 3a8797c, 4618345.
- **refuter (refuted):** REFUTED - CH-11c is the session running RIGHT NOW, and its end-of-session duties are not yet due. `git status --porcelain` shows STATUS.md modified-but-uncommitted, docs/evidence/ch11c-sweep/ untracked and prompts/CH-11c.md untracked - i.e. the chunk is mid-flight, not closed. Every other chunk's AI-USE row, PROGRESS entry and trajectory export landed at its own session close (CLAUDE.md end-of-session duties 2, 3 and 6), and PROGRESS.md likewise has no CH-11c entry yet for the same reason. The auditor measured an in-flight session against a duty that fires at session end; the four committed CH-11c commits are mid-session correction commits. No defect established at this point in the session.
- **refuter ran:** `git status --porcelain; git log --all --oneline | grep -i 'CH-11c'; for c in a0432e7 b5ebcbd 3a8797c 4618345; do git show --stat --format='%s' $c | head -6; done; grep -n -i 'CH-11c' PROGRESS.md`

**SURVIVED · line 17 · cosmetic · untraceable-number**

> | **Research / ideation** | ~90 agents across four design workflows that proposed, attacked and killed candidate projects | ~90 | `context/*-raw.json` (committed) |

- **problem:** Neither the agent count nor the workflow count derives from the cited path. context/*-raw.json is FIVE files, not four, and they hold 51 result records in total. The narrative headers give different, larger and non-additive figures (context/06-DIVERGENT-RESEARCH.md: '18 isolated angle agents' and '57 agents'; 04-STRATEGY-BRIEF.md: 'nine research reports'; 09-COMPLIANCE-AUDIT.md: 'Five auditors'). ~90 may be roughly right but it cannot be reproduced from the artifact the row points at.
- **auditor checked:** ls context/*raw*.json -> 03b, 04b, 05b, 08b, 09b (5 files). python summing every list/dict member across them -> 13+9+12+12+5 = 51. head -8 of each context design doc for the stated agent counts.
- **refuter (could not kill it):** Survives, cosmetic. `ls context/*raw*.json` gives FIVE files (03b, 04b, 05b, 08b, 09b), and walking their structure gives 51 records total (03b 5+2+6, 04b 5+4, 05b 5+5+2, 08b 5+2+5, 09b 5). Neither 90 nor four is derivable. The narratives give different, non-additive figures: 06-DIVERGENT-RESEARCH.md line 3 '18 isolated angle agents' and line 11 '57 agents ... across four stages'; 04-STRATEGY-BRIEF.md 'nine research reports'. I found the likely origin of 'four' - context/09-COMPLIANCE-AUDIT.md:65 says 'the four context/0Nb-*-raw.json agent outputs', written before 09b existed - which explains the number without making it current. The '~' concedes an estimate, which is why this is cosmetic, but the largest workflow (57 agents) has no raw JSON at the cited path at all.
- **refuter ran:** `ls context/*raw*.json; python - <<'EOF' import json,glob for f in sorted(glob.glob('context/*raw*.json')):     d=json.load(open(f,encoding='utf-8',errors='replace'))     print(f, {k:len(v) for k,v in d.items()} if isinstance(d,dict) else len(d)) EOF grep -n -m4 -iE 'agent|workflow|report' context/06-DIVERGENT-RESEARCH.md context/09-COMPLIANCE-AUDIT.md`

**SURVIVED · line 598 · cosmetic · internal-contradiction**

> **41.1 M**, about **1.6×** CH-00 rather than a fraction, and 32.41 against 22.51 cache-adjusted.

- **problem:** The ratio is stated against CH-00 but computed against prompts/CH-01.md's estimate of 26 M. This file's own measured CH-00 total input is 21,724,778, which makes CH-01 1.89x CH-00, not 1.6x. The preceding clause correctly attributes '~26 M' to the prompt; the ratio then quietly treats the prompt's wrong estimate as the measurement.
- **auditor checked:** grep -n '26M' prompts/CH-01.md -> line 7 'CH-00 consumed 26M input tokens'. AI-USE.md line 587 and docs/evidence/ch00-session-cost.txt both give TOTAL INPUT 21,724,778. python: 41093185/21724778 = 1.892; 41093185/26000000 = 1.581.
- **refuter (could not kill it):** Survives, cosmetic. prompts/CH-01.md line 7 says 'CH-00 consumed 26M input tokens'; the measured CH-00 total in docs/evidence/ch00-session-cost.txt (and in AI-USE's own CH-00 entry) is 21,724,778. 41,093,185/26e6 = 1.581 and 41,093,185/21,724,778 = 1.892. The sentence attributes the request to the prompt but states 26 M as CH-00's own figure and then computes the ratio 'CH-00' off it, so a measured number in the same file is contradicted by an estimate. Direction and conclusion (a miss, stated plainly) are unaffected, hence cosmetic.
- **refuter ran:** `grep -n '26M' prompts/CH-01.md; grep -n 'TOTAL INPUT' docs/evidence/ch00-session-cost.txt docs/evidence/ch01-pool/ch01-session-cost.txt; python -c "print(41093185/21724778, 41093185/26e6)"`

**REFUTED · line 82 · cosmetic · other**

> blind human-time study (8 items by hand, stopwatched, before seeing gold) is CH-09.

- **problem:** Reads as a completed or in-flight deliverable. The study was reserved and never run: STATUS.md line 33 says 'Blind human-time study reserved, not run', and the worksheet ships with all eight timing cells empty. The rubric row this sentence invokes ('human time per task') therefore has no measurement behind it, and AI-USE does not say so.
- **auditor checked:** cat docs/evidence/ch09-removed/human-time-worksheet.csv -> 8 item rows, every seconds_taken/verdict/confidence field blank. grep -n 'CH-09' STATUS.md -> line 33 '**Blind human-time study reserved, not run**'.
- **refuter (refuted):** REFUTED - the sentence states no result and no number, and every proposition in it is true. 'is CH-09' locates the study in a chunk; the study exists as designed and committed (docs/evidence/ch09-removed/human-time-blind.md briefs 8 items, stopwatch, do-not-open-the-answers, with a selection rule committed before selection, and assert_blind() enforcing it). AI-USE reports no human-time measurement anywhere, so no rubric row is falsely claimed as measured, and STATUS.md line 33 carries 'Blind human-time study reserved, not run' where chunk status belongs. The complaint is that the sentence 'reads as' complete - an interpretive preference about emphasis, not a false statement, a wrong number or a broken path.
- **refuter ran:** `sed -n '80,84p' AI-USE.md; cat docs/evidence/ch09-removed/human-time-worksheet.csv; head -25 docs/evidence/ch09-removed/human-time-blind.md; sed -n '33p' STATUS.md | tr '|' '\n' | grep -i human`

**SURVIVED · line 78 · cosmetic · internal-contradiction**

> points are recorded as they happen — `QUESTIONS.md` Q5 and Q7 in this chunk were both put to the operator mid-session and answered before work continued.

- **problem:** 'this chunk' has no referent in a project-level section — it is CH-00-era text left in place. It also contradicts the current chunk's own entry at line 138: 'No question was put to the operator mid-session; six were raised to QUESTIONS.md instead'. A reader taking the sentence at face value would attribute Q5/Q7 to CH-11.
- **auditor checked:** grep -n '^## Q5|^## Q7' QUESTIONS.md -> line 194 (Q5, safety rider / context read-only) and line 275 (Q7, commit author identity) — both CH-00-era. AI-USE.md line 138 quoted above.
- **refuter (could not kill it):** Survives, cosmetic. QUESTIONS.md line 194 (Q5, safety rider vs context/ read-only) and line 275 (Q7, commit author identity) both read 'Raised: CH-00, 2026-08-30'. The sentence sits in the project-level 'Human direction' section (lines 74-82), which has no chunk referent at all, and the file's newest entry says the opposite at line 143: 'No question was put to the operator mid-session; six were raised to QUESTIONS.md instead - Q30 through Q35'. CH-00-era text left in a section that is no longer CH-00's. Harmless to the numbers, so cosmetic, but the deictic is genuinely dangling.
- **refuter ran:** `grep -n '^## Q5\|^## Q7' QUESTIONS.md; sed -n '195,196p;276,277p' QUESTIONS.md; sed -n '74,84p;142,145p' AI-USE.md`

**Could not check — stated rather than dropped:**

- Scrubber counts. Line 210 ('0 credential substitutions of any class, 0 operator-contact substitutions, 3 KEY=value env values redacted, 1,091 home paths rewritten to ~, 0 lines that stopped being valid JSON'), line 506 ('660 home-path substitutions') and line 570 ('772'). tools/export_session.py prints these to stdout (grep -n 'home path' tools/export_session.py -> line 143 counts['home path -> ~']) and no committed artifact records them; the pre-scrub source transcripts live outside the repo, so the counts cannot be recomputed. Rough proxies only: literal '~' occurrences are 1,251 in CH-11.jsonl, 891 in CH-01.jsonl, 805 in CH-02.jsonl.
- CH-11's own usage table (line 167-179: 320 assistant turns, output 361,822, uncached 640, cache write 838,411, cache read 84,111,529, total input 84,950,580). No committed output file exists for it (find docs -name '*session-cost*' returns files for CH-00, CH-01, CH-02, SPEC-FIX-1 and SPEC-FIX-2 only), and line 171 cites the regenerating command with a literal '<uuid>' placeholder rather than the session id, so it is not runnable as written. My own recomputation gives 318 turns / 360,688 out / 84,051,680 in from the committed transcript and 327 / 367,625 / 88,120,204 from the live session file on disk — the published snapshot sits between the two, consistent with the stated 'snapshot at export time' caveat, but it cannot be reproduced exactly from any committed artifact.
- The 'nine literal U+FFFD characters' written into and then removed from README.md (lines 122-127). The surrounding claims ARE verified — data/evalset/items.jsonl contains exactly 973 section signs, 755 curly quotes and 0 U+FFFD — but the offending README draft was never committed, so the count of nine cannot be checked. git grep for U+FFFD across README.md history found nothing.
- SPEC-FIX-1's wall-clock at line 423 ('first turn 18:18:57 UTC → last 19:01:16 UTC = 42.3 min'). Neither endpoint appears in the committed transcript: assistant turns in docs/trajectories/build/SPEC-FIX-1.jsonl run 18:18:59.346Z to 19:04:07.807Z = 45.14 min. The gap is consistent with a snapshot taken before the closing commits (the same caveat the entry records elsewhere), so I did not raise it as a finding, but the stated figures do not reproduce from the artifact.
- The line-20 claim that the arm trajectories are '(bundled, every record kept)'. Counting run_start records across docs/trajectories/arms/*.jsonl gives 1,446 runs against the ledger's 2,107 rows — B0 324 vs 474, A1-minus-tool 82 vs 164, B0prime 246 vs 492. I could not determine from committed material whether the surplus ledger rows are retries, per-call sub-rows, or genuinely unbundled records, so I make no finding; it is flagged here because 'every record kept' is asserted and the two artifacts do not agree on the count.

### `CHANGELOG.md` — 400 lines read, 7 findings

**SURVIVED · line 23 · material · number-path-disagrees**

> **Observed failure it targets:** B0-agent's missed-defect rate is **0.4737** — it reads the text and still misses nearly half the defects

- **problem:** 0.4737 is the WITHDRAWN checkpoint's B0-agent missed-defect rate, computed on the eval set the CH-03 review failed (n=76, 49+27). The live figure on the corrected 82-item set is 0.4878. Line 22 of this same file declares those earlier figures WITHDRAWN, and the EVIDENCE cell of this very row (line 23) then says "Missed-defect 0.4878 -> 0.3902", so the row contradicts itself. The Iteration 1 card at lines 139-42 also says 0.4878.
- **auditor checked:** grep -rn "0\.4737" . --include=*.md --include=*.txt --include=*.json --include=*.py -> only two hits: ./CHANGELOG.md:23 and ./docs/evidence/checkpoint/withdrawn/checkpoint-result.txt:40 ('B0-agent success+failure 49+27=76 ... missed-defect 0.4737 FAIL'). cat docs/evidence/ch06-a1/iter1/b0agent_error_profile.txt -> 'missed-defect rate 0.4878 (20/41)'. cat docs/evidence/ch06-a1/a1-result.txt -> 'B0-agent 3 0.6585 54/82 0.1951 0.4878'.
- **refuter (could not kill it):** I could not kill this one. 0.4737 appears in exactly two places in the tree: CHANGELOG.md:23 and docs/evidence/checkpoint/withdrawn/checkpoint-result.txt:40 ('B0-agent success+failure 49+27=76 ... missed-defect 0.4737 FAIL') — the eval set the CH-03 review failed. The live checkpoint file docs/evidence/checkpoint/checkpoint-result.txt:40 reads 'success+failure 54+28=82 ... missed-defect 0.4878'. 0.4737 = 18/38 on the withdrawn n=76 set; the live figure is 20/41. Two defences fail. (a) 'It is a dated pre-registration quote from cb65539.' cb65539 is 03:19 and the corrected checkpoint 9786f6c is 04:05, so the figure was live when the card was drafted — but the sentence carries NO date, NO withdrawal marker, and the very next cell of the SAME row says 'Missed-defect 0.4878 -> 0.3902', so the row states two different baselines for one quantity. The file's own convention proves the point: line
- **refuter ran:** `grep -rn "0\.4737" . --include=*.md --include=*.txt --include=*.json ; grep -n "missed-defect" docs/evidence/checkpoint/checkpoint-result.txt ; git show e12466c:CHANGELOG.md | grep -n "0.4737\|0.4878" ; git blame -L 20,30 --date=short CHANGELOG.md ; git log -1 --format='%H %ad' cb65539 9786f6c`

**SURVIVED · line 26 · material · internal-contradiction**

> **A1 is the only agent arm that passes the false-defect guard (0.2195 ≤ 0.25)**

- **problem:** False. Per the cited-family artifact, B0 (0.1220 PASS), B0-agent (0.1951 PASS) and B0prime (0.2195 PASS) all clear the same guard. A1 is only the sole passer among the three A1-family arms. This exact sentence is already recorded as a corrected defect in PROGRESS.md, but the correction was applied to README.md and not to CHANGELOG.md, so the wrong claim survives here.
- **auditor checked:** cat docs/evidence/ch06-a1/a1-result.txt -> guard block: 'B0 false-defect 0.1220 <= 0.25 PASS / B0-agent 0.1951 PASS / B0prime 0.2195 PASS / A1-iter1 0.4878 FAIL / A1-minus-tool 0.3415 FAIL / A1 0.2195 PASS'. grep -rn "only agent arm" --include=*.md . -> CHANGELOG.md:26 and PROGRESS.md:188 ('B0, B0-agent and B0-prime pass it too. A1 is the only one of the three A1-family arms that does').
- **refuter (could not kill it):** Survives. The cited artifact's own guard block (docs/evidence/ch06-a1/a1-result.txt) reads: 'B0 false-defect 0.1220 <= 0.25 PASS / B0-agent 0.1951 <= 0.25 PASS / B0prime 0.2195 <= 0.25 PASS / A1-iter1 0.4878 FAIL / A1-minus-tool 0.3415 FAIL / A1 0.2195 PASS'. Four arms pass, two of them ('B0-agent', 'B0prime' = B0-agent at 3x sampling) are agent arms by any reading of the word. I checked for a qualifier in the same cell: the trailing clause is 'though that guard is still failed by every arm', which attaches to the missed-defect guard named immediately before it, not to the false-defect claim. The correct form is already written down twice in this repo — PROGRESS.md:188 logs it as a found defect ('B0, B0-agent and B0-prime pass it too. A1 is the only one of the three A1-family arms that does') and README.md:237 ships the corrected sentence ('A1 is the only one of the three A1-family arms 
- **refuter ran:** `sed -n '30,45p' docs/evidence/ch06-a1/a1-result.txt ; awk 'NR==26' CHANGELOG.md | grep -o "A1 is the only agent arm that passes the false-defect guard ([^)]*)" ; grep -rn "only agent arm\|only one of the three A1-family" --include=*.md . ; sed -n '233,242p' README.md`

**SURVIVED · line 86 · material · internal-contradiction**

> 2. **Intra-rule collision detector** — CH-09; class size measured five ways at ~1.3%.

- **problem:** The single figure ~1.3% is contradicted by this file's own removed-experiment card (lines 325-332) and by the shipped CH-09 script's output, which measures 43/2,527 = 1.70% in-repo and states the class size does NOT reproduce across implementations (1.31% pilot / 3.07% naive recount / 1.70% in-repo). Presenting it as a settled ~1.3% is exactly the narrowing the artifact refuses.
- **auditor checked:** cat docs/evidence/ch09-removed/class_sizes.txt -> 'COLLISION fires on 43 of 2,527 = 1.70% ... pilot 26 of 1,984 = 1.31% ... naive recount 61 of 1,984 = 3.07% ... The 1.3%-3.1% range is NOT narrowed to a single settled figure by this run'. awk NR==86 CHANGELOG.md and awk NR>=325,NR<=332 CHANGELOG.md compared.
- **refuter (could not kill it):** Survives. The line collapses a range its two sources both refuse to collapse. (a) Its own upstream spec, CONTEXT.md:295, says 'Measured five ways: ... redesignation-collision sensitivity is ~1.3-3.1% ... (the pilot reported 26/1,984 = 1.31%; an independent naive recount returned 61/1,984 = 3.07%. The figure does not reproduce and is therefore provisional ... neither is quoted as settled)'. So 'five ways' is faithful, but '~1.3%' is the low end of a range CONTEXT.md explicitly marks provisional and non-reproducing. (b) The shipped CH-09 script's committed output, docs/evidence/ch09-removed/class_sizes.txt, measures 'COLLISION fires on 43 of 2,527 = 1.70%', reproduces neither prior figure, and states 'The 1.3%-3.1% range is NOT narrowed to a single settled figure by this run ... THE CLASS SIZE DOES NOT REPRODUCE ACROSS IMPLEMENTATIONS'. (c) This same file contradicts line 86 at lines 322-3
- **refuter ran:** `awk 'NR>=80 && NR<=90 {printf "%d: %s\n", NR, $0}' CHANGELOG.md ; cat docs/evidence/ch09-removed/class_sizes.txt ; sed -n '293,298p' CONTEXT.md ; git blame -L 76,90 --date=short CHANGELOG.md ; sed -n '320,342p' CHANGELOG.md`

**SURVIVED · line 88 · material · internal-contradiction**

> Its justification (order-sensitivity fires on 38–42% of items, two independent counts, not label-correlated) is published as the reason it was *worth* building

- **problem:** Stated flatly as fact with no correction marker, while lines 25 and 357-368 of the same file (and the shipped script) establish that the 42.0% end DOES NOT REPRODUCE and sits above the measured ceiling of 30.1%, that no denominator yields 1,984, and that the figure 'cannot carry a claim'. The other of the 'two independent counts' (31/82) is marked NOT-IN-REPO in the spec-claims audit. This is the stale published justification restated in the same document that retracts it.
- **auditor checked:** cat docs/evidence/ch09-removed/class_sizes.txt -> readings A/B/C/D = 3.3/11.1/19.6/30.1%, 'PUBLISHED FIGURE 833 1,984 42.0%', '*** THE 42.0% DOES NOT REPRODUCE. ***', '42.0% is above this measurement's CEILING'. sed -n '65,85p' docs/evidence/spec-claims/spec-claims.txt -> 'state-carry sensitivity 833/1,984 = 42.0% ... pilot pool; the 1,984-item corpus is not committed' and 'state-carry on the pilot pool 31/82 ... pilot pool, not committed' (status NOT-IN-REPO in spec-claims.json:268-273).
- **refuter (could not kill it):** Survives. Both counts trace to CONTEXT.md:110 ('state-carry sensitivity ... fires on 833/1,984 = 42.0% of items (also 31/82 on the pilot pool; two independent counts, not label-correlated - 16 defective / 15 executable)'), so 38-42% is a faithful summary of the SPEC — and the spec figure is precisely what the shipped artifact retracts. docs/evidence/ch09-removed/class_sizes.txt prints four readings at 3.3% / 11.1% / 19.6% / 30.1%, then '*** THE 42.0% DOES NOT REPRODUCE. ***', '42.0% is above this measurement's CEILING, not merely outside its range', 'NEITHER IS 1,984', and the binding instruction 'It is raised as QUESTIONS.md Q23 and is not quoted as settled anywhere'. Line 88 quotes it as settled, which falsifies that sentence inside the same repo. The second count is no better: docs/evidence/spec-claims/spec-claims.json marks both 'state-carry sensitivity 833/1,984 = 42.0%' and 'state-
- **refuter ran:** `awk 'NR>=85 && NR<=91 {printf "%d: %s\n", NR, $0}' CHANGELOG.md ; sed -n '108,114p' CONTEXT.md ; cat docs/evidence/ch09-removed/class_sizes.txt ; sed -n '60,90p' docs/evidence/spec-claims/spec-claims.txt ; sed -n '260,280p' docs/evidence/spec-claims/spec-claims.json ; sed -n '344,375p' CHANGELOG.md`

**SURVIVED · line 22 · material · number-without-path**

> B-script **0.6098**, within-pair permutation **p = 0.2355**. `docs/evidence/checkpoint/`

- **problem:** The only path cited in this EVIDENCE cell is docs/evidence/checkpoint/, which contains neither figure. Both numbers are correct but live in CH-04's artifacts at docs/evidence/ch04-scorer/bscript-run.txt. A reviewer following the citation finds nothing. PROGRESS.md already logs this as a citation defect fixed elsewhere; it survives here.
- **auditor checked:** grep -rn "0.6098\|0.2355\|bscript\|B-script\|b_script" docs/evidence/checkpoint/ -> no output (exit 0, zero matches). grep -rn "0.6098\|0.2355" docs/evidence/ -> docs/evidence/ch04-scorer/bscript-run.txt:16 'held-out CV accuracy 0.6098' and :31 'p-value 0.2355'; docs/evidence/ch04-scorer/bscript-result.json:77 '"p_value": 0.2355'. PROGRESS.md:194 'docs/evidence/checkpoint/ cited for the B-script figures | they are CH-04's, at ch04-scorer/bscript-run.txt'.
- **refuter (could not kill it):** Survives. I ran the recursive grep myself over the cited directory and it returns nothing (exit 1, zero matches) for 0.6098, 0.2355, bscript or B-script. Widening to docs/evidence/ shows both figures live in CH-04's artifacts: docs/evidence/ch04-scorer/bscript-run.txt:16 'held-out CV accuracy 0.6098' and :31 'p-value 0.2355', plus bscript-result.json:77 '"p_value": 0.2355'. I checked the 'path is cited one sentence earlier or in the header' escape: the EVIDENCE cell of line 22 contains exactly one path, docs/evidence/checkpoint/, placed after the B-script sentence, and the table header row (line 20) carries no path. So two published numbers have no reachable evidence path, against hard rule 14 and the 'Never report a number without its evidence path' clause. PROGRESS.md:194 already records this as a found defect fixed elsewhere ('docs/evidence/checkpoint/ cited for the B-script figures |
- **refuter ran:** `grep -rn "0.6098\|0.2355\|bscript\|B-script\|b_script" docs/evidence/checkpoint/ ; echo exit=$? ; grep -rn "0.6098\|0.2355" docs/evidence/ ; awk 'NR==22' CHANGELOG.md ; grep -n "bscript-run" PROGRESS.md`

**REFUTED · line 99 · cosmetic · untraceable-number**

> the first timestamp in `docs/evidence/runs/cost_ledger.csv` for arm `A1-*` are the two facts a reviewer should check against each other

- **problem:** The verification the file instructs a reviewer to perform cannot be performed as written: cost_ledger.csv has no timestamp column, and A1-* run_ids carry no timestamp (only probe run_ids embed one). The underlying ordering claim does hold via git, but the named field does not exist.
- **auditor checked:** head -2 docs/evidence/runs/cost_ledger.csv -> header 'run_id,arm,item_id,model,input_tokens,output_tokens,wall_clock_s,imputed_usd'; python printed first A1 run_id = 'A1__05-8447_75.31__rep1' (no timestamp). git log -- CHANGELOG.md -> cards committed e12466c 2026-08-31 07:41:37; git show <c>:docs/evidence/runs/cost_ledger.csv | grep -c ',A1-iter1,' across ledger commits -> 0 at 9786f6c (04:05) and 82 first at 864e28a (08:56), so the ordering itself is sound.
- **refuter (refuted):** REFUTED — the auditor read 'timestamp in the file' as 'timestamp column in the CSV', a reading the same sentence rules out. The sentence ends '...and they are checkable by `git log` alone', which names the mechanism explicitly: the reviewer git-logs the ledger and finds when the first A1-* rows entered it, then compares that to the card's commit SHA. That check is fully performable, and the auditor performed it successfully — their own evidence_checked shows 0 A1-iter1 rows at 9786f6c (04:05) and 82 first appearing at 864e28a (08:56), against cards committed at e12466c (07:41) — and they concede 'the underlying ordering claim does hold via git'. So the instruction works as written under its own stated method and the fact it asserts is true. The absence of a per-row timestamp column is real (header is run_id,arm,item_id,model,input_tokens,output_tokens,wall_clock_s,imputed_usd, and A1__05
- **refuter ran:** `head -2 docs/evidence/runs/cost_ledger.csv ; grep -n ",A1," docs/evidence/runs/cost_ledger.csv | head -3 ; awk 'NR>=96 && NR<=100 {printf "%d: %s\n", NR, $0}' CHANGELOG.md ; git log --oneline -- CHANGELOG.md`

**SURVIVED · line 76 · cosmetic · internal-contradiction**

> *(No cards yet. The first is written at the CHECKPOINT, for the Baseline row.)*

- **problem:** Stale placeholder. Five completed iteration cards appear below it in the same file (Iteration 1 at line 134, Iteration 2 at line 159, and the three removed-experiment cards at lines 293, 322, 344).
- **auditor checked:** grep -n '^## Iteration\|^## Removed experiment' CHANGELOG.md via awk range reads of lines 94-235 and 286-375 -> '## Iteration 1 - Tool (cfr_resolve)' (L134), '## Iteration 2 - Skill (SKILL.md)' (L159), '## Removed experiment 1/2/3' (L293/L322/L344), all with Result/Prediction blocks filled.
- **refuter (could not kill it):** Survives, though it is cosmetic. git blame puts line 76 at 6abf4f2 (2026-08-30), and five completed cards now sit below it in the same file: '## Iteration 1 - Tool (cfr_resolve)' at line 133, '## Iteration 2 - Skill (SKILL.md)' at 158, and '## Removed experiment 1/2/3' at 293/322/344, each with its Result / Decision / Learning or Class size blocks filled. (The auditor's 134/159 are one line off — those are the fenced-block openers — which does not touch the substance.) I looked for a narrow reading that would save it: 'the first is written at the CHECKPOINT, for the Baseline row' could mean no BASELINE card exists, which is true — no Baseline card was ever written. But the leading assertion 'No cards yet' is flatly false as the file now stands, and it is the sentence a reader hits immediately before five cards. Harmless to the numbers, wrong as a statement.
- **refuter ran:** `sed -n '55,78p' CHANGELOG.md ; grep -n "^## Iteration\|^## Removed experiment" CHANGELOG.md ; git blame -L 76,90 --date=short CHANGELOG.md`

**Could not check — stated rather than dropped:**

- Line 89 'not label-correlated' (the 16 defective / 15 executable split behind the 38-42% figure). docs/evidence/spec-claims/spec-claims.json marks both source counts NOT-IN-REPO ('pilot pool, not committed'); no committed artifact carries the split.
- Lines 337-339 'NARA NEVER PUBLISHES a note naming an intra-rule conflict; a live probe for "conflicting amendments" returned 0'. The probe was a network call; docs/evidence/ch09-removed/class_sizes.txt restates it as prose but commits no probe output, and I may not make network calls.
- Lines 96-97 'These two cards are committed before agents/A1-SKILL.md and src/a1.py exist and before a single A1 call is made.' git log makes the commit ordering consistent (cards e12466c 07:41; first A1-iter1 ledger rows land at 864e28a 08:56), but the ledger has no per-call timestamp for A1 arms, so the 'before a single A1 call' half cannot be confirmed from the tree.
- Line 244 'use `siblings`, which frequently hands back the very paragraph the tool just denied' — 'frequently' carries no committed count; docs/evidence/ch06-a1/iter1/nested_designation_probe.txt counts the ceiling (60/128) but not siblings-recovery rate.
- Lines 249-250 'No item id, gold label, or per-item outcome appears anywhere in the skill' — I checked for item-id patterns (grep -nE '[0-9]{2}-[0-9]{4,5}\|' agents/A1-SKILL.md returned nothing), but I could not exhaustively rule out a paraphrased per-item outcome.

### `PROVENANCE.md` — 121 lines read, 8 findings

**SURVIVED · line 92 · material · number-path-disagrees**

> | Anthropic API — `claude-haiku-4-5-20251001` | commercial, per terms | every evaluation arm, temperature 0 |

- **problem:** The model name is CORRECT (verified against the ledger), but "temperature 0" for EVERY evaluation arm is false. B0prime ran at temperature 1.0. This is not an oversight elsewhere — src/arms.py documents it as a declared, necessary deviation from GOOD.md section 8 and says in terms "It is the only arm in the packet not at temperature 0, and saying so is the point: a control quietly run at a different temperature would be worse than none." PROVENANCE.md is the disclosure file and it states the opposite of the declared deviation, with no pointer to QUESTIONS.md Q22 where the deviation lives.
- **auditor checked:** grep -rn 'temperature' docs/evidence/ch06-a1/B0prime-rep1.json -> '93:  "temperature": 1.0'. sed -n '285,340p' src/arms.py -> 'def run_b0prime(items, model, rep, traj_dir, ledger_path, out_dir, samples: int = 3, temperature: float = 1.0)' and lines 308-324 'TEMPERATURE - A DECLARED, NECESSARY DEVIATION FROM `GOOD.md` section 8 ... It is the only arm in the packet not at temperature 0'. grep -n '^## Q22' QUESTIONS.md -> '1385:## Q22 - B0′, the compute-matched control, CANNOT be built at the pre-registered temperature 0'.
- **refuter (could not kill it):** SURVIVES. PROVENANCE.md:92 is verbatim as quoted and the file contains no other mention of temperature (`grep -ni 'temperature' PROVENANCE.md` returns line 92 only). The shipped artifact contradicts it: docs/evidence/ch06-a1/B0prime-rep1.json:93 is `"temperature": 1.0`, and src/arms.py:291 defaults `run_b0prime(..., temperature: float = 1.0)` while arms.py:454 sets 0.0 for every other haiku arm. arms.py:310-324 states the deviation in terms — 'It is the only arm in the packet not at temperature 0, and saying so is the point: a control quietly run at a different temperature would be worse than none' — and QUESTIONS.md:1385 carries it as Q22. B0prime is unambiguously an evaluation arm: this file's own correction block at :103 lists `B0prime` among the evaluation-arm rows. So the disclosure file asserts the opposite of a deviation the code declares, with no Q22 pointer. Not a dated correcti
- **refuter ran:** `grep -n 'temperature' docs/evidence/ch06-a1/B0prime-rep1.json ; grep -n 'temperature' src/arms.py ; grep -ni 'temperature\|B0prime' PROVENANCE.md ; grep -n '^## Q22' QUESTIONS.md`

**SURVIVED · line 64 · material · other**

> The `nistula-assistance-` result is cited in this project's README as the *motivating hypothesis* for why a green test suite is insufficient evidence — never as a result of this project.

- **problem:** README.md does not cite it at all. The string 'nistula' occurs zero times in README.md, as do 'acumen' and '17 blocker'. README's actual hypothesis passage (README.md:369-376) attributes the transfer hypothesis to "an earlier measurement on IETF errata, from work outside this repository" — a different prior result entirely. This is a ground-rule-02 disclosure claim about a shipping deliverable that a judge falsifies with one grep.
- **auditor checked:** grep -ic nistula README.md -> 0 ; grep -ic acumen README.md -> 0 ; grep -ic '17 blocker' README.md -> 0 (README.md is 529 lines, wc -l). sed -n '365,380p' README.md shows the only 'hypothesis' passage, which names IETF errata, not nistula-assistance-.
- **refuter (could not kill it):** SURVIVES. README.md is 529 lines and contains zero occurrences of 'nistula', 'acumen' or '17 blocker' (case-insensitive), and zero occurrences of 'github.com'. I searched for an unnamed paraphrase too: the only hypothesis-attribution passage, README.md:369-376, credits 'an earlier measurement on IETF errata, from work outside this repository' — a different prior result, explicitly not re-derived. README.md:222's 'An earlier project of ours died to exactly this kind of script' is the kill test (context/07), not the nistula defect count. README.md:308 uses the green-test-suite phrase as this project's own argument with no external citation attached. The PROVENANCE sentence is a factual claim about the content of a shipping deliverable, and one grep falsifies it.
- **refuter ran:** `grep -ic nistula README.md ; grep -ic acumen README.md ; grep -ic '17 blocker' README.md ; grep -n -i 'hypothesis\|green test suite\|IETF\|github.com\|blocker' README.md ; sed -n '360,382p' README.md`

**SURVIVED · line 43 · material · number-path-disagrees**

> | `context/03-IDEA-REVIEW-VERDICT.md` | 15 agents attacking the first candidate. It died. |

- **problem:** The cited artifact accounts for 13 agents, not 15. Its own committed dump context/03b-review-raw.json holds critiques=5, alternatives=2, scores=6 = 13, and the prose file's own subtitle says "Synthesis of five hostile critiques, six independent rubric scorings, and one verified fact". The mismatch was already found and written up as m-17 in context/10-REMEDIATION.md:768 ("PROVENANCE.md:43 separately attributes '15 agents' to context/03, whose own dump counts 13") and the fix was never applied.
- **auditor checked:** python -c "import json; d=json.load(open('context/03b-review-raw.json',encoding='utf-8')); [print(k,len(v)) for k,v in d.items()]" -> critiques 5 / alternatives 2 / scores 6 (=13). head -3 context/03-IDEA-REVIEW-VERDICT.md -> '*Synthesis of five hostile critiques, six independent rubric scorings, and one verified fact none of the critiques fully priced.*'. grep -rn '15 agents' --include=*.md . -> context/10-REMEDIATION.md:768 and PROVENANCE.md:43 only.
- **refuter (could not kill it):** SURVIVES. The cited artifact's own committed dump context/03b-review-raw.json holds critiques=5, alternatives=2, scores=6 = 13, and I dumped each entry to confirm they are distinct agent outputs (5 lenses, 2 angles, 6 candidate scorings). The prose file's subtitle is 'Synthesis of five hostile critiques, six independent rubric scorings, and one verified fact none of the critiques fully priced' — nothing in it claims 15, and `grep -n '15\b\|agents' context/03-IDEA-REVIEW-VERDICT.md` returns no agent count. The only other '15 agents' string in the repo is context/10-REMEDIATION.md:768, which is the VERIFIED write-up of this exact defect (m-17), unapplied. Note the adjacent muddle that makes it worse, not better: CONTEXT.md:8 attaches '13 and 15 independent agents' to context/08 and context/07 respectively, so PROVENANCE:43 is also borrowing a number that belongs to a different artifact.
- **refuter ran:** `python -c "import json; d=json.load(open('context/03b-review-raw.json',encoding='utf-8')); [print(k,len(v)) for k,v in d.items()]" ; head -6 context/03-IDEA-REVIEW-VERDICT.md ; grep -rn '15 agents' --include=*.md . ; grep -rn '13 and 15' CONTEXT.md`

**SURVIVED · line 80 · material · number-path-disagrees**

> | Passages marked *(decoded)* — our analysis, not micro1's words | 4, all in analysis sections (capability menu, deliverable→rubric mapping, what the examples share). **None is a requirement, and no downstream document quotes one as authoritative.** |

- **problem:** The count is 6, not 4, and the reassurance "None is a requirement" is contradicted by one of the two the count omits: context/01-PROBLEM-PDF.md:147 is headed "### Evaluation hard requirements *(decoded checklist)*" and lists seven requirement checkboxes. The literal count of 4 is only reachable by counting the extraction-convention note at :5 (which is not a passage) and dropping the three variant markers. This exact defect, with the corrected count of 6 and the note that two of the six are requirement-shaped, is already written out at context/11-REMEDIATION-2.md:459-467 and was never applied.
- **auditor checked:** grep -n -o '(decoded[^)]*)' context/01-PROBLEM-PDF.md -> 5:(decoded) [the convention note], 57:(decoded), 147:(decoded checklist), 229:(decoded), 280:(decoded), 315:(decoded — my analysis, not micro1's words); grep -n -o 'Decoded:' context/01-PROBLEM-PDF.md -> 95. That is six marked passages. sed -n '140,160p' context/01-PROBLEM-PDF.md confirms :147 is a checklist of hard requirements. context/11-REMEDIATION-2.md:467 gives the corrected row: '**6**: :57 ... :95 ... :147 ... :229 ... :280 ... :315. **Two of the six are requirement-shaped**'.
- **refuter (could not kill it):** SURVIVES on both halves. Marked passages in context/01-PROBLEM-PDF.md: :57 '(decoded)' capability menu, :95 '> **Decoded:**' comparison-fairness note, :147 '(decoded checklist)', :229 '(decoded)' deliverable→rubric mapping, :280 '(decoded)' what the examples share, :315 '(decoded — my analysis, not micro1's words)' strategic read = six. The seventh hit, :5, is the extraction-convention line ('All text below is verbatim unless marked *(decoded)*'), not a passage. The row's parenthetical names only three of them, and the count 4 matches neither. The reassurance fails independently: I read :145-160 and :147 is headed '### Evaluation hard requirements *(decoded checklist)*' followed by seven requirement checkboxes ('One primary metric', '≥10 cases', '≥1 deliberately hard case'…) — requirement-shaped by construction. context/11-REMEDIATION-2.md:459-467 already carries the identical verified f
- **refuter ran:** `grep -n -o '(decoded[^)]*)' context/01-PROBLEM-PDF.md ; grep -n -o 'Decoded:' context/01-PROBLEM-PDF.md ; sed -n '3,7p;145,160p' context/01-PROBLEM-PDF.md ; sed -n '455,470p' context/11-REMEDIATION-2.md`

**REFUTED · line 13 · cosmetic · internal-contradiction**

> **Everything in `src/`, `tests/`, `data/`, `docs/`, and every project artifact.** No line of this project's source existed before 2026-08-30 03:00 UTC.

- **problem:** Checked by the method line 5 nominates ("checkable against file modification times"), one tracked file inside the enumerated set pre-dates the stated boundary by nine minutes: docs/process/superseded/BUILD-PHASE-1-PROMPT.md, mtime 2026-08-30 02:50:40 UTC. The substantive claim (nothing pre-kickoff) still holds — the file post-dates kickoff by 36 hours — so this is a self-imposed boundary being 9 minutes too tight, not a provenance problem.
- **auditor checked:** TZ=UTC ls -l --time-style=full-iso docs/process/superseded/BUILD-PHASE-1-PROMPT.md -> '2026-08-30 02:50:40.592360100 +0000'. git ls-files docs/process/superseded/ -> 'docs/process/superseded/BUILD-PHASE-1-PROMPT.md' (tracked). Python walk of src/tests/data/docs confirms it is the single oldest mtime; the next is 2026-08-30T12:37:36Z.
- **refuter (refuted):** REFUTED — the auditor's own measurement does not contradict the sentence it quotes. The mtime is real (docs/process/superseded/BUILD-PHASE-1-PROMPT.md = 2026-08-30T02:50:40Z, tracked, the single oldest under src/tests/data/docs), but the boundary sentence is scoped to 'this project's **source**', and that file is a prose build-session prompt — its first line is '# BUILD PHASE 1 — Logger, Harvest, and the Go/No-Go Checkpoint', instructions to an agent, not a line of source. Measured against source proper, the claim holds with margin: the oldest file anywhere in src/ or tests/ is tests/test_runlog.py at 2026-08-30T12:39:36Z, nine and a half hours after the stated boundary. The preceding sentence — everything in src/, tests/, data/, docs/ was built during the competition — is the one that covers the prompt file, and it is true by 36 hours against the 2026-08-28 15:00 kickoff. The auditor co
- **refuter ran:** `python -c "import os,datetime;[print(datetime.datetime.utcfromtimestamp(os.path.getmtime(os.path.join(dp,f))).isoformat(),os.path.join(dp,f)) for root in ['src','tests'] for dp,dn,fn in os.walk(root) for f in fn]" | sort | head -3 ; head -6 docs/process/superseded/BUILD-PHASE-1-PROMPT.md ; git ls-files docs/process/superseded/`

**SURVIVED · line 26 · cosmetic · number-path-disagrees**

> **2026-08-27, approximately 21:45 UTC — seventeen hours before kickoff.**  - `scraper/` — Playwright recon scripts written to read the **public** HackerEarth challenge page.

- **problem:** Only 5 of the 9 scraper scripts date from 2026-08-27 ~21:42-21:45 UTC. Four (portfolio.cjs, work.cjs, li.cjs, hn.cjs) were written 2026-08-29 03:13-03:16 UTC — after kickoff — and they do not read the HackerEarth challenge page; all four write to context/me, the operator dossier. The error is harmless in direction (post-kickoff work needs no permission) but the sentence as written is inaccurate, and because /scraper/ is gitignored a judge cannot check it either way.
- **auditor checked:** python mtime dump of scraper/*.cjs -> recon.cjs 2026-08-27T21:42:30Z, sections.cjs 21:43:43Z, sections2.cjs 21:44:10Z, mapimg.cjs 21:44:38Z, slice.cjs 21:45:31Z; portfolio.cjs 2026-08-29T03:13:12Z, work.cjs 03:14:47Z, li.cjs 03:15:52Z, hn.cjs 03:16:38Z. head -6 on each of the four -> all set OUT='.../context/me'. grep -n scraper .gitignore -> '33:/scraper/'.
- **refuter (could not kill it):** SURVIVES. I dumped mtimes for all 43 entries of scraper/. Pre-kickoff (2026-08-27 21:42-21:45): recon.cjs, sections.cjs, sections2.cjs, mapimg.cjs, slice.cjs, package.json, package-lock.json, node_modules — 8 entries. Post-kickoff (2026-08-29 03:13-06:21, i.e. 12-15 hours AFTER the 2026-08-28 15:00 kickoff): portfolio.cjs 03:13:12Z, work.cjs 03:14:47Z, li.cjs 03:15:52Z, hn.cjs 03:16:38Z, he.mjs, rd.mjs, rd2.mjs and 31 rd_*.txt dumps — 35 entries. So the dated bullet covers 5 of the 9 .cjs scripts. I also confirmed the second half of the sentence is wrong for those four: `head -8` on each shows all four set OUT='…/context/me' and target chinmoypaul.vercel.app, LinkedIn and hashnode — the operator dossier, not the HackerEarth page. context/11-REMEDIATION-2.md item (d) independently VERIFIED the same split. Harmless in direction, but the sentence as written is false, and /scraper/ being git
- **refuter ran:** `python -c "import os,datetime,glob;[print(datetime.datetime.utcfromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%dT%H:%M:%SZ'),f) for f in sorted(glob.glob('scraper/*'))]" ; head -8 scraper/portfolio.cjs scraper/work.cjs scraper/li.cjs scraper/hn.cjs ; grep -n scraper .gitignore`

**SURVIVED · line 93 · cosmetic · number-path-disagrees**

> the model-sensitivity subset only, which was **WITHDRAWN** as a harness defect — `QUESTIONS.md` Q19. No claim in this submission rests on it. Also the four rows of the model-id probe.

- **problem:** The substance is right (verified: 80 sonnet subset rows, 4 sonnet probe rows) but the Q19 pointer resolves to the wrong section. QUESTIONS.md:983 Q19 is headed "CH-03 FAILED review TWICE. Strike limit reached, ESCALATED to the architect." The withdrawal is an unnumbered block "MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31" at QUESTIONS.md:1110, which sits under the later heading "## ARCHITECT RULINGS — 2026-08-31" at :1086 — not under Q19. The wrong anchor was inherited verbatim from the suggested correction text in Q35.
- **auditor checked:** grep -n '^## Q19' QUESTIONS.md -> '983:## Q19 - CH-03 FAILED review TWICE. Strike limit reached, ESCALATED to the architect.'. grep -n '^#' QUESTIONS.md between 983 and 1130 -> 1086:'## ARCHITECT RULINGS — 2026-08-31'. sed -n '1110,1115p' QUESTIONS.md -> 'MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31. The sonnet-5 subset is a HARNESS DEFECT ... 13 of 20 B0-agent-sonnet predictions came back EMPTY'.
- **refuter (could not kill it):** SURVIVES as a broken citation. QUESTIONS.md:983 is '## Q19 - CH-03 FAILED review TWICE. Strike limit reached, ESCALATED to the architect.', and the Q19 ruling text at :1093 is about eval-set primacy (unrestricted 41 pairs vs restricted) — neither mentions sonnet. The withdrawal is an unnumbered block, 'MODEL-SENSITIVITY CHECK - WITHDRAWN, 2026-08-31', at :1110, seventeen lines below Q19's ruling inside the same verbatim fence but under the later heading '## ARCHITECT RULINGS — 2026-08-31' at :1086. Every other repo reference to Q19 (PROGRESS.md:727, night-run/summary.md:22, prompts/CH-06.md:33, prompts/CH-11.md:75) reads it as the eval-set/CH-03 ruling; prompts/CH-06.md:186 lists 'Q19 / Q16 / sensitivity-withdrawn' as three separate items, confirming the withdrawal is not Q19. QUESTIONS.md:2443 shows the wrong anchor was inherited verbatim from Q35's suggested correction text. A judge fo
- **refuter ran:** `grep -n '^## Q19' QUESTIONS.md ; awk 'NR>=980 && NR<=1130 && /^#/ {print NR": "$0}' QUESTIONS.md ; sed -n '1086,1118p' QUESTIONS.md ; grep -rn 'Q19' --include=*.md .`

**REFUTED · line 106 · cosmetic · other**

> Re-derivable at `docs/evidence/ch11c-sweep/`.

- **problem:** The path exists on disk and does produce every figure in the correction block, but it is untracked, so it is absent from any clone. The whole CH-11c correction (PROVENANCE.md lines 96-106) is likewise uncommitted working-tree text: git log shows PROVENANCE.md has exactly one commit, and the corrected §5 is a pending 14-line insertion. As the tree stands the shipped-in-git PROVENANCE.md still names claude-sonnet-5 as the model of every evaluation arm. An end-of-session commit closes this.
- **auditor checked:** git status --porcelain -> ' M PROVENANCE.md' and '?? docs/evidence/ch11c-sweep/'. git log --all --format='%h %s' -- PROVENANCE.md -> single line '3ac8207 chore: spec, process and provenance (unreviewed)'. git diff HEAD --stat -- PROVENANCE.md -> '1 file changed, 14 insertions(+), 1 deletion(-)'. cat docs/evidence/ch11c-sweep/ch11c-verify.txt confirms the file reproduces the 2107-row (model, arm) table exactly.
- **refuter (refuted):** REFUTED as stated — its load-bearing assertion is false against the current tree. The auditor claims 'git log shows PROVENANCE.md has exactly one commit', 'the corrected §5 is a pending 14-line insertion' and 'as the tree stands the shipped-in-git PROVENANCE.md still names claude-sonnet-5 as the model of every evaluation arm'. All three are now wrong: PROVENANCE.md has two commits (4618345 'CH-11c: PROVENANCE.md named claude-sonnet-5 as the model of every arm; the ledger says haiku (unreviewed)', on top of 3ac8207), HEAD is a0432e7, `git diff HEAD -- PROVENANCE.md` is empty, and `git show HEAD:PROVENANCE.md` line 92 already reads claude-haiku-4-5-20251001 with the full correction block at :96-106. The residue is narrower than the finding: docs/evidence/ch11c-sweep/ (5 files, incl. ch11c_verify.py and ch11c-verify.txt) is still `??` untracked, so the cited path is not yet in a clone. That
- **refuter ran:** `git rev-parse --short HEAD ; git log --format='%h %ad %s' --date=iso -- PROVENANCE.md ; git status --porcelain ; git diff HEAD --stat ; git show HEAD:PROVENANCE.md | grep -ni 'sonnet\|haiku' ; git ls-files docs/evidence/ch11c-sweep/ ; ls docs/evidence/ch11c-sweep/`

**Could not check — stated rather than dropped:**

- Line 59, "28 adversarial review reports" at github.com/chinmoypaul8897/acumen — the cited path is a GitHub URL and no network call is permitted. The only local corroboration is context/02-ABOUT-ME.md:68 ("28 adversarial reviews"), which is gitignored (.gitignore:19) and therefore not shipped, so a judge cannot reach it either.
- Lines 59-60, "public since July 2026" and "last pushed 2026-08-18, ten days before kickoff" — no network. The 08-18 -> 08-28 arithmetic checks out against the verified kickoff date. context/10-REMEDIATION.md:821 records an earlier agent verifying both via the GitHub API (acumen created 2026-07-25; nistula last pushed 2026-08-18T15:01:26Z), but per hard rule 15 that is another agent's claim and I could not confirm it.
- Line 60, "17 blocker-class defects found while the test suite was green" — no network. Local corroboration exists at context/me/readmes/nistula-assistance-.md:112 and context/03-IDEA-REVIEW-VERDICT.md:15, but context/me/ is untracked, so only the 03 quotation ships.
- Line 118, "~300 MB of intermediate data" in the excluded research scratch directories — the directories are excluded from the machine's shipped tree, so there is nothing on disk to size. Unverifiable by construction.
- Section 4b as a whole, "Checked against the original document, 2026-08-30" — the original PDF is excluded (.gitignore:11 excludes context/01-PROBLEM-PDF.md; §6 excludes micro1's materials). I verified every row against the transcription itself (rubric 15/30/20/15/15/5=100 at context/01-PROBLEM-PDF.md:165-172; the anti-slop clause verbatim at :168 and :177; ten ground rules at :190-199; four deliverable headings at :207-223), but I could not reproduce the comparison against the original.
- Line 80, "no downstream document quotes one as authoritative" — I grepped the tracked tree for the distinctive strings of the decoded checklist and the capability menu ("deliberately hard case", "Complete results shared", "Same cases for baseline", "cost per task, reported", "capability menu") and found no hits outside context/ and PROVENANCE.md itself. That is consistent with the claim but cannot prove a negative over paraphrase.
- Line 118 and line 116, the completeness of the exclusion list — I confirmed no real operator contact details survive in tracked files (git grep for the email and +91 phone patterns returns only synthetic FAKE_ constants in docs/evidence/ch00_guard_probe.py:28-33), which closes the M-34 defect recorded at context/10-REMEDIATION.md:731. I could not enumerate what else is on the build machine and therefore cannot confirm the list is exhaustive.

### `QUESTIONS.md` — 2568 lines read, 11 findings

**REFUTED · line 1385 · material · compute-matched-survivor**

> ## Q22 - B0′, the compute-matched control, CANNOT be built at the pre-registered temperature 0

- **problem:** QUESTIONS.md's own Q22 heading still asserts, in the file's voice (not as a quotation), that B0-prime IS the compute-matched control. Q34 (line 2360) and Q36 (line 2469) of this same file establish that it is not: it spent 1,377,402 input tokens against A1's 4,006,662 (34%) and is a repeated-sampling control. Q24 got a dated RETRACTION appended beneath it; Q22 got nothing, even though QUESTIONS.md was explicitly inside CH-11c's editable fence (line 2455 lists it). CHANGELOG.md line 26 cites '(Q22)' actively, so a reader following that citation lands on the uncorrected heading.
- **auditor checked:** grep -n -i 'compute-matched' QUESTIONS.md -> only 1385 (heading, file's own voice), 1389 (quoting CONTEXT.md), 2360/2469/2476-2482 (Q34/Q36 corrections). python over docs/evidence/runs/cost_ledger.csv: per-arm input tokens A1=4,006,662 B0prime=1,377,402 (34.4%), usd 5.3334 vs 1.3988 (26.2%) — confirms not token/compute matched.
- **refuter (refuted):** REFUTED on four independent grounds. (1) QUESTIONS.md's own preamble (lines 1-8) declares it a dated append-only ledger: 'Newest questions are appended at the bottom. Nothing here is ever deleted; a withdrawn ruling is marked WITHDRAWN and kept.' Q22 is stamped 'Raised at CH-06 §3, 2026-08-31, before the arm ran' — the token measurement that refutes the label did not exist when the heading was written, and the heading uses CONTEXT.md §4's own designation, which the entry's second paragraph quotes verbatim on the very next line. (2) The correction IS in this same file, exactly where the file's convention puts it — appended later, not by editing the original: Q34 at line 2360 is titled 'B0-prime is named the "compute-matched control" and it is not token-matched', the CH-11c resolutions table at 2464 closes it, and Q36 at 2469 tracks the residue. The auditor's own grep found all of these. (
- **refuter ran:** `grep -n -i 'compute-match' QUESTIONS.md README.md CHANGELOG.md; sed -n '1,10p;1385,1430p;2360,2400p;2455,2490p' QUESTIONS.md; grep -n -i 'compute-match' docs/evidence/ch11c-sweep/ch11c-sweep.txt`

**REFUTED · line 2476 · material · internal-contradiction**

> **These three still say compute-matched and CH-11c did not touch them:**

- **problem:** Q36 enumerates exactly three surviving 'compute-matched' locations (CONTEXT.md:63, src/arms.py:292, prompts/CH-06.md:139) and calls them all protected/out-of-fence. The enumeration is incomplete: QUESTIONS.md itself carries a fourth at line 1385 (Q22's heading), and QUESTIONS.md WAS inside CH-11c's fence (its own line 2455 lists QUESTIONS.md among the files the chunk could edit). So the claim 'the shipping surface a judge reads is now consistent' (line 2484) is false for the ledger the judge is reading.
- **auditor checked:** grep -n 'compute-matched\|COMPUTE-MATCHED' CONTEXT.md src/arms.py prompts/CH-06.md README.md CHANGELOG.md STATUS.md AI-USE.md SUBMISSION.md PROVENANCE.md -> CONTEXT.md:63, src/arms.py:292, prompts/CH-06.md:139 (all three citations exact); README/CHANGELOG only in the corrective sense. grep -n -i 'compute-matched' QUESTIONS.md -> 1385 is a fourth, in-file, uncorrected.
- **refuter (refuted):** REFUTED — the finding misreads Q36's declared scope. Q36's heading is 'three PROTECTED files still call B0′ the "compute-matched control". Architect-only', and its lead sentence is 'Not acted on — all three are outside the fence.' The enumerated class is files CH-11c could NOT edit. QUESTIONS.md is inside the fence, so by construction it is not a member of the set being enumerated; adding it would contradict the table's own column semantics. On its own terms the enumeration is complete and every citation is exact — I opened all three: CONTEXT.md:63 '| **B0′** | compute-matched control | B0-agent at A1's exact token budget...', src/arms.py:292 '**B0-prime** - the COMPUTE-MATCHED CONTROL. `CONTEXT.md` section 4, `plan.md` CH-08.', prompts/CH-06.md:139 '**Name `B0′` explicitly** — the compute-matched control: B0-agent at A1's token budget...'. Nor was QUESTIONS.md:1385 unaccounted for: docs
- **refuter ran:** `sed -n '2469,2490p' QUESTIONS.md; sed -n '60,66p' CONTEXT.md; sed -n '290,294p' src/arms.py; sed -n '137,141p' prompts/CH-06.md; sed -n '50,54p;434,463p' docs/evidence/ch11c-sweep/ch11c_sweep.py; grep -n -i 'compute-match' docs/evidence/ch11c-sweep/ch11c-sweep.txt`

**SURVIVED · line 871 · material · number-path-disagrees**

> **Census over all 68 annual-edition volumes CH-03 downloaded:** … | `EDNOTE` | 857 | 67 | YES | … | `CITA` | 31,943 | 68 | YES | | `EAR` | 3,303 | 68 | YES |

- **problem:** Q17 cites `docs/evidence/ch03-evalset/alt-element-census.txt` as its evidence, but the committed file reports different figures: volumes scanned 69 (not 68), EDNOTE 868/68 (not 857/67), CITA 32631/69 (not 31,943/68), EAR 3352/69 (not 3,303/68), NOTE 3053/47 (not 3,051/46), SOURCE 3207/67 (not 3,140/66), APPRO 965/33 (not 964/32). Q17's numbers match only the SUPERSEDED revision of that file at git 067a9d9; it was regenerated at 76e2e4b (the F2 fix that added a volume) and Q17 was never updated. Only EFFDNOTP 446/31, EFFDNOT 379/26, SECAUTH 2322/50 and REVTXT 200/27 still reproduce.
- **auditor checked:** cat docs/evidence/ch03-evalset/alt-element-census.txt -> 'volumes scanned: 69', EDNOTE 868 68, CITA 32631 69, EAR 3352 69, NOTE 3053 47, SOURCE 3207 67, APPRO 965 33. git log --oneline -- that path -> 76e2e4b, 067a9d9. git show 067a9d9:<path> -> 'volumes scanned: 68', EDNOTE 857 67, CITA 31943 68, EAR 3303 68 — i.e. Q17 quotes the older revision.
- **refuter (could not kill it):** SURVIVES — I reproduced every element of it. The committed artifact Q17 names as its evidence reads 'volumes scanned: 69' with EDNOTE 868/68, CITA 32631/69, EAR 3352/69, NOTE 3053/47, SOURCE 3207/67, APPRO 965/33. Q17's table says 68 volumes, EDNOTE 857/67, CITA 31,943/68, EAR 3,303/68, NOTE 3,051/46, SOURCE 3,140/66, APPRO 964/32. `git log` on the path shows exactly two revisions; `git show 067a9d9:<path>` prints 'volumes scanned: 68' with EDNOTE 857/67, CITA 31943/68, EAR 3303/68, NOTE 3051/46, SOURCE 3140/66, APPRO 964/32 — a byte-for-byte match to Q17. The artifact was regenerated at 76e2e4b (the CH-03 FIX that recovered a volume whose missing <PARTS> header had silently excluded a whole title) and Q17 was never updated beside it. The auditor's diagnosis is exactly right. I tried the dated-record refutation and it fails here: this file corrects superseded figures by appending beside 
- **refuter ran:** `cat docs/evidence/ch03-evalset/alt-element-census.txt; git log --oneline -- docs/evidence/ch03-evalset/alt-element-census.txt; git show 067a9d9:docs/evidence/ch03-evalset/alt-element-census.txt | sed -n '1,30p'; sed -n '848,905p' QUESTIONS.md`

**SURVIVED · line 897 · material · number-path-disagrees**

> | unnamed element | surviving in the 76 frozen items | items affected | … | `NOTE` | 14 | 6 | | `APPRO` | 1 | 1 | | `SECAUTH` | 1 | 1 |

- **problem:** Same Q17, residual-exposure table. The cited artifact reports 'frozen items inspected: 82' with NOTE 21 surviving across 7 items, APPRO 2/2 and SECAUTH 4/4 — not 76 items with 14/6, 1/1 and 1/1. Line 906's 'the strongest single figure: 0 of 76 frozen items contain any NN FR NNNN citation' is 0 of 82 in the artifact (the zero holds, the denominator does not). Lines 911 and 924 compound it: 'recovers 2 pairs, taking n from 76 to 80' — the shipped set is 41 pairs / n=82 (data/evalset/items.jsonl = 82 lines, leakage.json items_total=82), so adopting <EFFDNOT> would move 82→86.
- **auditor checked:** cat docs/evidence/ch03-evalset/alt-element-census.txt -> 'frozen items inspected: 82'; NOTE 21/7, APPRO 2/2, SECAUTH 4/4; '0 of 82'. wc -l data/evalset/items.jsonl -> 82. python json.load(data/evalset/leakage.json) -> items_total 82, items_whose_UNSTRIPPED_text_would_have_leaked 3.
- **refuter (could not kill it):** SURVIVES — same entry, second table, same cause, independently confirmed. The current committed artifact's RESIDUAL EXPOSURE block reads 'frozen items inspected: 82' with NOTE 21/7, APPRO 2/2, SECAUTH 4/4, and '0 of 82' for the NN FR NNNN sweep. Q17 says 76 frozen items, NOTE 14/6, APPRO 1/1, SECAUTH 1/1, '0 of 76'. `git show 067a9d9:<path>` prints the superseded block verbatim — 'inside the 76 frozen items', 'frozen items inspected: 76', NOTE 14/6, APPRO 1/1, SECAUTH 1/1 — confirming Q17 quotes the pre-fix revision. The shipped set is 82 items: `wc -l data/evalset/items.jsonl` = 82 and leakage.json items_total = 82, and STATUS.md:21 records the fix as '38 pairs → 41, n 76 → 82'. So Q17's live recommendation to the architect — 'recovers 2 pairs, taking n from 76 to 80', repeated at line 924 — is an actionable instruction stated against a denominator the repository abandoned; the correct 
- **refuter ran:** `git show 067a9d9:docs/evidence/ch03-evalset/alt-element-census.txt | sed -n '/RESIDUAL/,/citation/p'; sed -n '/RESIDUAL/,/citation/p' docs/evidence/ch03-evalset/alt-element-census.txt; wc -l data/evalset/items.jsonl; python -c "import json;d=json.load(open('data/evalset/leakage.json'));print(d['items_total'])"; sed -n '893,930p' QUESTIONS.md`

**SURVIVED · line 1677 · material · internal-contradiction**

> Instead exactly one file was **untracked** to make room: … The generating script, the blind operator brief and the sealed answer key all remain tracked.

- **problem:** Both halves are false against the commit that raised Q25. Commit bc99ef4 (the CH-06 commit carrying Q25) deleted TWO files from the index, not one: docs/evidence/ch09-removed/human-time-blind.md (341 lines — the 'blind operator brief' the entry says remains tracked) and human-time-worksheet.csv (9 lines). The blind operator brief is still untracked today. Q27 item 3 (line 1937) then reasons about restoring only the 292-byte worksheet, so the second untracked file has never been accounted for anywhere.
- **auditor checked:** git diff --name-status bc99ef4^ bc99ef4 | grep '^D' -> D docs/evidence/ch09-removed/human-time-blind.md, D docs/evidence/ch09-removed/human-time-worksheet.csv (git diff --stat: 341 and 9 deletions). git ls-tree -r --name-only bc99ef4 -- docs/evidence/ch09-removed/ | grep human -> only human-time-reserved.json and human_time_study.py. git ls-files docs/evidence/ch09-removed/ today -> human-time-blind.md absent. git show bc99ef4^:.../human-time-worksheet.csv | wc -c -> 292 (that part is right).
- **refuter (could not kill it):** SURVIVES, and it is the strongest finding in the set. `git diff --name-status bc99ef4^ bc99ef4 | grep '^D'` returns TWO deletions: docs/evidence/ch09-removed/human-time-blind.md and human-time-worksheet.csv; `git diff --stat` on that directory shows 341 and 9 deletions, 350 total. `git ls-tree -r --name-only bc99ef4 -- docs/evidence/ch09-removed/` lists neither, and `git ls-files docs/evidence/ch09-removed/` today still lists neither — human-time-blind.md sits untracked on disk at 39,082 bytes. I confirmed the deleted file IS the blind operator brief the sentence says remains tracked: its first line is '# Blind human-time study — the operator's brief' and it instructs 'Do not open human-time-reserved.json until every item below is timed.' So both halves of the quoted sentence are false about the very commit that carries Q25. The auditor's follow-through is also correct: `grep -n 'workshe
- **refuter ran:** `git diff --name-status bc99ef4^ bc99ef4 | grep '^D'; git diff --stat bc99ef4^ bc99ef4 -- docs/evidence/ch09-removed/; git ls-tree -r --name-only bc99ef4 -- docs/evidence/ch09-removed/; git ls-files docs/evidence/ch09-removed/; git show bc99ef4^:docs/evidence/ch09-removed/human-time-blind.md | head -12; grep -n 'worksheet\|human-time' QUESTIONS.md`

**SURVIVED · line 807 · cosmetic · number-path-disagrees**

> Three excluded documents have attribution **1.0000** - perfect - and fail purely on parse rate (`2011-12279` 0.4167, `2020-17549` 0.6111, `2024-30575` 0.2500).

- **problem:** The cited artifact says four, not three. docs/evidence/ch03-evalset/floor-decomposition.txt prints 'attribution == 1.0000 and yet excluded : 4' and lists a fourth document, 2024-31513 (completeness 0.0000, attribution 1.0000, parse 0.0000, 3 elements), which Q16 omits. The error understates Q16's own argument rather than inflating it, and the three quoted per-document parse rates are exact.
- **auditor checked:** cat docs/evidence/ch03-evalset/floor-decomposition.txt -> 'attribution == 1.0000 and yet excluded : 4' followed by 2024-31513, 2024-30575 0.2500, 2011-12279 0.4167, 2020-17549 0.6111. The other Q16 figures (2/70 pass, 68 excluded, 59/68 parse-bound, 36 attribution>=0.90 excluded, 68/68 parse<0.90) all reproduce exactly.
- **refuter (could not kill it):** SURVIVES. docs/evidence/ch03-evalset/floor-decomposition.txt line 17 reads 'attribution == 1.0000 and yet excluded : 4', and the block beneath lists four documents: 2024-31513 (completeness 0.0000, attribution 1.0000, parse 0.0000, 3 elements), 2024-30575 0.2500, 2011-12279 0.4167, 2020-17549 0.6111. I looked for an escape and there is none: 2024-31513 also fails purely on parse rate (its completeness equals its parse rate, as it does for the other three), so no narrower reading of the sentence excludes it. I also tested the stale-revision defence that saved nothing here — `git log` shows floor-decomposition.txt has exactly ONE revision, 067a9d9, and that revision already printed 4 with 2024-31513 listed first. So 'Three' was wrong the day it was written, not superseded later. Correctly graded cosmetic: the three quoted parse rates are exact, and the error understates Q16's own argument.
- **refuter ran:** `grep -n 'attribution == 1.0000' -A 12 docs/evidence/ch03-evalset/floor-decomposition.txt; git log --oneline -- docs/evidence/ch03-evalset/floor-decomposition.txt; git show 067a9d9:docs/evidence/ch03-evalset/floor-decomposition.txt | sed -n '10,24p'; sed -n '790,812p' QUESTIONS.md`

**SURVIVED · line 1744 · cosmetic · untraceable-number**

> | **Wasted spend** | **~USD 1.43** of the 18.00 ceiling |

- **problem:** No evidence path is cited for the wasted-spend figure (hard rule 14 requires one), and recomputing it from the ledger gives USD 1.4082, not 1.43. The duplicated-run cost is exactly half of the two arms' total (A1-minus-tool 0.7087 + B0prime 0.6993 = 1.4081; the two arms total 2.8163). The '~' and the conclusion are unaffected, but the figure has propagated verbatim into CHANGELOG.md line 26 and the bc99ef4 commit message.
- **auditor checked:** python over docs/evidence/runs/cost_ledger.csv: cost of the second occurrence of every duplicated run_id, by arm -> A1-minus-tool 0.7087, B0prime 0.6993 (sum 1.4081); first-occurrence sum for the same two arms 1.4082; both-arms total 2.8163, half 1.4082. grep -rn '1\.43' docs/evidence/ -> only an unrelated file-size row in ch14-size/inventory.md.
- **refuter (could not kill it):** SURVIVES. I attacked this hardest, because a '~' figure is the easiest kind to defend, and it did not hold. Recomputing over docs/evidence/runs/cost_ledger.csv: the cost of the SECOND occurrence of every duplicated run_id in the two doubled arms is A1-minus-tool 0.7087 + B0prime 0.6993 = 1.4080; the FIRST-occurrence sum for the same ids is 1.4082; the two arms' full totals are 1.4175 + 1.3988 = 2.8163, half 1.4082. Every direction gives 1.408, never 1.43. I then tested the one refutation that would have worked — that the ledger has changed since Q26 was written — by extracting the ledger from the raising commit itself: `git show bc99ef4:docs/evidence/runs/cost_ledger.csv` is byte-identical in every quantity (2107 rows, same per-arm totals, grand total 11.6323), so 1.43 never reproduced. I also tried adding the leakage probe (B0-agent-currenttext 0.2630) and the three stray A1 duplicate i
- **refuter ran:** `python over docs/evidence/runs/cost_ledger.csv (second/first-occurrence cost of duplicated run_ids, per-arm totals); git show bc99ef4:docs/evidence/runs/cost_ledger.csv > $TEMP/ledger_bc99ef4.csv and the same recompute; grep -rn '1\.43' --include=*.md --include=*.txt --include=*.json .`

**SURVIVED · line 1745 · cosmetic · untraceable-number**

> | **Ledger integrity** | **651 `run_id` values now appear twice.** `run_id` was intended to be unique. |

- **problem:** 651 is exactly right as a repository-wide total, but it sits in a table headed 'What it cost' for the two accidentally-doubled arms, which implies the double run caused all 651. Only 328 are attributable to it (A1-minus-tool 82 + B0prime 246). The other 323 duplicates are B0 150, B0-agent 150, B0-agent-sonnet 10, B0-sonnet 10 and A1 3 — pre-existing checkpoint/retry collisions unrelated to Q26. No path is cited ('enumerated in this session's evidence', no filename).
- **auditor checked:** python over docs/evidence/runs/cost_ledger.csv: 2107 rows, 1456 distinct run_ids, 651 run_ids with multiplicity 2 (max multiplicity 2); duplicated-id counts by arm -> A1 3, A1-minus-tool 82, B0 150, B0-agent 150, B0-agent-sonnet 10, B0-sonnet 10, B0prime 246; sum 651.
- **refuter (could not kill it):** SURVIVES, though it is the weakest of the survivors and is correctly graded cosmetic. Both halves check out. The arithmetic: 2107 rows, 1456 distinct run_ids, 651 with multiplicity 2 (max multiplicity 2), broken down as B0prime 246 + A1-minus-tool 82 = 328 attributable to Q26's double run, against B0 150, B0-agent 150, B0-agent-sonnet 10, B0-sonnet 10 and A1 3 = 323 that are not — pre-existing collisions in arms Q26 never touched. Identical at bc99ef4, so the split is not an artefact of later commits. The misattribution is aggravated by adjacency: the two rows immediately above give '164 ledger rows' and '492 ledger rows', summing to 656, which invites the reader to read 651 as this incident's damage under a table headed 'What it cost'. The citation half is unambiguous — the following paragraph claims the duplicate ids 'are enumerated in this session's evidence', and no such enumeration 
- **refuter ran:** `python over docs/evidence/runs/cost_ledger.csv (Counter over run_id, duplicates by arm) and the same over git show bc99ef4:docs/evidence/runs/cost_ledger.csv; grep -rn '651' --include=*.md --include=*.txt --include=*.json docs/ *.md; grep -rln 'duplicate' docs/evidence/ tools/ src/`

**SURVIVED · line 2073 · cosmetic · other**

> ## Q29 - SUBMISSION COMPLETENESS. Six files that `PROCESS.md` §3 marks "ships" do not exist anywhere in the tree

- **problem:** Q29's table asserts 'tracked? no / on disk? no' for README.md, REPRODUCE.md, LICENSE, THIRD-PARTY.md, SAFETY.md and requirements.txt. All six now exist and are tracked (CH-11 created them). QUESTIONS.md carries no closure for Q29 anywhere — unlike Q31–Q35, which got an explicit CH-11c resolutions table — even though STATUS.md line 42 states 'QUESTIONS.md Q29 is CLOSED'. A judge reading this ledger straight through concludes deliverable 1 has no README.
- **auditor checked:** git ls-files --error-unmatch on each of the six -> all tracked; test -e -> all present. grep -n 'Q29' QUESTIONS.md -> line 2073 only (no closure entry). grep -n 'Q29' STATUS.md -> line 42 '**`QUESTIONS.md` Q29 is CLOSED — all six files … now exist.**'
- **refuter (could not kill it):** SURVIVES on its factual core, but the harm clause is overstated and the finding is correctly graded cosmetic. Verified: all six are tracked and on disk (git ls-files --error-unmatch and test -e pass for README.md, REPRODUCE.md, LICENSE, THIRD-PARTY.md, SAFETY.md, requirements.txt). Verified: `grep -n 'Q29' QUESTIONS.md` returns line 2073 only — no closure anywhere in the ledger, unlike Q24 (dated RETRACTED IN FULL appended beneath), Q19 (dated correction appended beneath) and Q31–Q35 (an explicit CH-11c resolutions table at line 2462). QUESTIONS.md was editable at CH-11, the chunk that closed it, since CH-11 appended Q30–Q35 to it. What I could NOT confirm is the conclusion: a judge does not reach the ledger for a completeness check, and the closure is published in three shipping files, including SUBMISSION.md's own section headed 'Was missing — closed at CH-11' which cites Q29 by number
- **refuter ran:** `for f in README.md REPRODUCE.md LICENSE THIRD-PARTY.md SAFETY.md requirements.txt; do git ls-files --error-unmatch "$f"; test -e "$f"; done; grep -n 'Q29' QUESTIONS.md STATUS.md PROGRESS.md SUBMISSION.md CHANGELOG.md README.md; sed -n '110,130p' SUBMISSION.md; sed -n '2073,2125p' QUESTIONS.md`

**SURVIVED · line 1624 · cosmetic · untraceable-number**

> total bytes        59,386,953  = 56.6 MiB = 59.4 MB

- **problem:** Q25's headline measurement cites no evidence path — it says only 'Committed with this session's evidence', and the number appears in no committed artifact anywhere in the repository. It does reproduce on recomputation (59,385,512 B of blob bytes at bc99ef4^, a 1,441 B delta consistent with working-tree vs blob sizes), and every area figure in the table below it reproduces exactly, so this is a hard-rule-14 citation gap rather than a wrong number.
- **auditor checked:** grep -rn '59,386,953\|59386953' over *.md/*.txt/*.json/*.py excluding .git -> only QUESTIONS.md:1624. git ls-tree -r -l bc99ef4^ | awk sum -> 300 files, 59,385,512 B = 59.39 MB. Per-area recompute at bc99ef4^ -> docs/trajectories 35.43, data/amdpars 7.82, data/attribution-v11 7.73, docs/evidence 2.72, data/ednotes 1.67 MB — all four table rows exact.
- **refuter (could not kill it):** SURVIVES as stated, and the auditor's own framing is the honest one — a citation gap, not a wrong number. `grep -rn '59,386,953\|59386953'` over every .md/.txt/.json/.py/.csv outside .git returns exactly one hit: QUESTIONS.md:1624 itself. The entry says only 'Committed with this session's evidence', naming no path, and I checked the raising commit's evidence tree — `git ls-tree bc99ef4 docs/evidence/` contains no size artifact at all (docs/evidence/ch14-size/ arrives later, at CH-14a, and measures a different tree state, 61.70 MB per Q27). So the generating script and committed output hard rule 14 requires do not exist. The number does reproduce: `git ls-tree -r -l bc99ef4^` sums to 300 files / 59,385,512 bytes, a 1,441-byte delta consistent with working-tree sizes versus blob sizes, and the file count of 300 matches the entry exactly.
- **refuter ran:** `grep -rn '59,386,953\|59386953' --include=*.md --include=*.txt --include=*.json --include=*.py --include=*.csv . ; git ls-tree -r -l bc99ef4^ | awk '{n++; s+=$4} END {print n, s}'; git ls-tree bc99ef4 docs/evidence/; grep -rln 'tracked files\|total bytes' docs/`

**SURVIVED · line 1249 · cosmetic · internal-contradiction**

> Reading (b) is demanding, and is 0.85 higher than the **0.81** the CH-06 Iteration 2 card commits to.

- **problem:** Reading (b)'s threshold is 0.8585 (line 1245), so the difference from 0.81 is 0.0485 (4.85 pp), not 0.85. The sentence as written states a difference of 0.85 between two accuracies both below 0.86, which is impossible. Line 1256 of the same entry gets it right ('mutually unsatisfiable at 0.81 ≤ A1 < 0.8585'), so this is a wording slip rather than a wrong analysis.
- **auditor checked:** sed -n '1245,1256p' QUESTIONS.md -> line 1245 'A1 > 0.6585 + 0.20 = **0.8585**'; line 1256 '0.81 ≤ A1 < 0.8585'. Arithmetic: 0.8585 − 0.81 = 0.0485. B0-agent 0.6585 confirmed at docs/evidence/ch06-a1/a1-result.txt line 27.
- **refuter (could not kill it):** SURVIVES. I read the whole of Q20 (lines 1229–1275) looking for a charitable parse and found none. Line 1245 defines reading (b) as 'A1 > 0.6585 + 0.20 = **0.8585**', so the gap from 0.81 is 0.0485, not 0.85. As written the sentence asserts a difference of 0.85 between two accuracies both below 0.86, which is impossible on a 0–1 scale. 0.85 is not a rounding of 0.8585 either (that rounds to 0.86), so it cannot be read as 'is 0.85, higher than 0.81'. The same entry states it correctly twice, sixteen and twenty-three lines later: 'These two of this project's own predictions are mutually unsatisfiable at 0.81 ≤ A1 < 0.8585' and 'A1 must reach 0.8585 ... while the CH-06 Iteration 2 card predicts 0.81' — which is what makes this a wording slip rather than a wrong analysis, exactly as the auditor graded it. B0-agent 0.6585, the input to the 0.8585 threshold, is confirmed in docs/evidence/ch06-
- **refuter ran:** `sed -n '1229,1275p' QUESTIONS.md; sed -n '20,32p' docs/evidence/ch06-a1/a1-result.txt`

**Could not check — stated rather than dropped:**

- Q26 lines 1765-1774: the RUN-1 side of the double-run comparison (A1-minus-tool run1 0.6463, B0prime run1 0.6585, the two flipped items 2025-17122|10.237 and 2026-11140|149.510, and the run-1 guard rates 0.1951 / 0.4878). Q26 itself states run 1's per-item trajectories were overwritten, so this is not re-derivable from the tree. I verified the run-2 side exactly (a1-result.txt lines 28/36: B0prime 0.6585, false-defect 0.2195 PASS, missed-defect 0.4634 FAIL) and confirmed the run-1 bundle commit it cites exists (git cat-file -t 89d58c5 -> commit; it carries docs/trajectories/arms/A1-minus-tool-rep1.jsonl).
- Q5 lines 189-212: the PII carrier census (2 carriers measured against the audit's claimed 4-5, and the positive control returning 1 in the git-ignored context/02-ABOUT-ME.md). I deliberately did not run a phone-number sweep over the operator's personal data. Partial corroboration only: context/10-REMEDIATION.md does carry 2 <OPERATOR-PHONE> markers as Q5 says (grep -c), and docs/evidence/secret-scan/scan.txt records the operator-contact rules as blocking with VERDICT PASS / 0 findings over all 462 blobs of 84 commits.
- Q28 lines 1984-1990: the verbatim pre-commit refusal transcript ('tracked file count 311 exceeds 300', 'tracked 61,776,371 B', 'archive 10,215,930 B'). Those three numbers appear nowhere but QUESTIONS.md — it is a quoted terminal session, not a committed artifact. The hook facts around it DO check out: .githooks/pre-commit line 73 MAX_TRACKED = 400, line 78 MAX_ARCHIVE_BYTES = 45_000_000, line 72 'It is NOT set to "whatever makes this commit pass" (that would be 311)'.
- Q12(c) line 596: the counts '684 elements whose only word-form citation is lowercase' and '4 of the clearest cases name an Appendix explicitly'. Neither appears in docs/evidence/spec-fix-1/classes.txt or sabotage.txt. The adjacent figures do reproduce: 683 lowercase-only namers and 44 carrying part_mismatch are printed in docs/evidence/ch03-evalset/case-sensitivity-cost.txt, and I independently recomputed '676 of the 1,086 extended-only namers are lowercase' as exactly 676 from data/amdpars/amdpars.jsonl.
- Q23 line 1478: whether CONTEXT.md §6's 833/1,984 = 42.0% has any derivation at all. This is the entry's own open question to the architect, not a claim; the four replacement readings (83/280/495/760 over 2,527 = 3.3/11.1/19.6/30.1%) and the 43/2,527 = 1.70% collision figure all reproduce exactly from docs/evidence/ch09-removed/class_sizes.txt.

### `README.md` — 529 lines read, 5 findings

**SURVIVED · line 505 · material · number-path-disagrees**

> | **Reproduce it** | [REPRODUCE.md](REPRODUCE.md) — Tier 1 offline in 15 s for USD 0, Tier 2 live |

- **problem:** REPRODUCE.md publishes TWO measured Tier-1 totals - 14.42 s (run 1) and 25.84 s (run 2) - and states in the same section: "Both numbers are published because a single one would be a claim about your machine rather than a measurement of ours." README line 505 reports only the faster run, rounded down to '15 s', as a single figure. It also contradicts README's own line 16 ('in under half a minute') and REPRODUCE.md's own heading sentence ('Under half a minute for the four commands above'). The number 15 appears nowhere in REPRODUCE.md.
- **auditor checked:** grep -n -iE '15 s|15s|second|half a minute|USD 0|tier 1' REPRODUCE.md -> line 119 'Under half a minute for the four commands above. Measured twice at CH-11'; sed -n '110,140p' REPRODUCE.md -> timing table 'refetch.py 0.60/1.75 · analyse_checkpoint 0.39/1.61 · analyse_a1 0.89/1.34 · pytest -q 12.54/21.15 · **total** **14.42 s** **25.84 s**'. STATUS.md line 42 also records '14.42 s and 25.84 s on two runs, both published'.
- **refuter (could not kill it):** Could not kill it. `grep -n '14.42\|25.84\|15 s\|half a minute' README.md` returns only line 16 ('under half a minute') and line 505 ('15 s'); the string '15' as a timing figure appears nowhere in REPRODUCE.md, whose §'Runtime and what has been verified' publishes a two-column table (run 1 total 14.42 s, run 2 total 25.84 s) and states in bold 'Both numbers are published because a single one would be a claim about your machine rather than a measurement of ours.' Line 505 publishes exactly the single number the cited artifact refuses to publish, and it is the faster of the two. Two sub-claims by the auditor ARE wrong and should not be relayed: (a) 14.42 -> '15 s' is rounding UP, not 'rounded down'; (b) there is no contradiction with README line 16 — 15 s is under half a minute. The core number-vs-path disagreement survives; severity is closer to minor (an index-row gloss) than material.
- **refuter ran:** `grep -n "14.42\|25.84\|15 s\|half a minute\|USD 0" README.md ; sed -n '110,140p' REPRODUCE.md ; sed -n '495,520p' README.md`

**SURVIVED · line 509 · material · number-path-disagrees**

> | **Every ambiguity and every ruling** | [QUESTIONS.md](QUESTIONS.md) — 31 entries, including our own retractions |

- **problem:** QUESTIONS.md contains 38 entries (Q1 through Q38, contiguous, no gaps), not 31. The count is stale by seven; Q32, Q34 and Q35 are all cited by this same README, so the file it describes demonstrably runs past 31.
- **auditor checked:** grep -c '^## Q' QUESTIONS.md -> 38. grep -n '^## Q' QUESTIONS.md -> Q1 (line 12) through Q38 (line 2548), contiguous. README itself cites Q32 (line 414) and Q34 (lines 217, 257).
- **refuter (could not kill it):** Verified independently: `grep -c '^## Q' QUESTIONS.md` -> 38, and `grep -n '^## Q'` lists Q1 (line 12) through Q38 (line 2548) with no gaps and no sub-entries that could inflate the count. No alternative reading rescues '31': the row says 'entries', and README itself cites Q32 (line 414) and Q34 (line 217, inside the B0-prime paragraph), both past 31. QUESTIONS.md is a live ledger, not a dated record whose old text must survive — the README row is a description of the current file and it is stale by seven.
- **refuter ran:** `grep -c '^## Q' QUESTIONS.md ; grep -n '^## Q' QUESTIONS.md`

**SURVIVED · line 256 · material · untraceable-number**

> 0 of 68 labelled items contain a redesignation instruction; **NARA never publishes a note naming an intra-rule conflict** — a live probe for *"conflicting amendments"* returned 0

- **problem:** The cited path (docs/evidence/ch09-removed/class_sizes.txt) contains these two strings, but does not PRODUCE them: class_sizes.py writes them as hard-coded string literals (w("    - 0/68 labelled items contain a redesignation instruction;")), computing nothing. The project's own inventory files '0/68 labelled items contain a redesignation instruction' in the NOT-IN-REPO pile - 'Cannot be re-derived from anything committed' - annotated 'pilot pool'. So the two load-bearing reasons the README gives for the Removed-#2 decision are pilot figures presented behind an evidence citation that merely echoes them, while the computed number in the same cell (43 of 2,527 = 1.70%) is genuine.
- **auditor checked:** sed -n '215,250p' docs/evidence/ch09-removed/class_sizes.py -> lines 236-238 are literal w("...") strings, no computation. sed -n '55,110p' docs/evidence/spec-claims/spec-claims.txt -> 'NOT-IN-REPO (18) - Cannot be re-derived from anything committed' includes '§10  0/68 labelled items contain a redesignation instru  0  -  ^ pilot pool'. The computed 43/2,527=1.70%, collision-only=0, and the pilot 1.31%/naive 3.07% comparisons ARE produced by the script and check out.
- **refuter (could not kill it):** Confirmed and could not kill. `sed -n '225,250p' docs/evidence/ch09-removed/class_sizes.py` shows lines 236 and 238 are literal `w("    - 0/68 labelled items contain a redesignation instruction;")` and `w("      for \"conflicting amendments\" returned 0;")` inside a hard-coded prose block — no computation, no data read. Provenance grep shows the two claims originate in CONTEXT.md §10 / context/08-FINAL-CALL.md and are filed by the project's own inventory (docs/evidence/spec-claims/spec-claims.txt, NOT-IN-REPO pile, 18 entries) as '§10  0/68 labelled items contain a redesignation instru  0  -  ^ pilot pool' i.e. 'Cannot be re-derived from anything committed'. The auditor's counterbalance is also right: the computed 43 of 2,527 = 1.70% and collision-only = 0 ARE produced by the script. So the row mixes one genuinely re-derived figure with two pilot-pool assertions that carry no path of the
- **refuter ran:** `sed -n '225,250p' docs/evidence/ch09-removed/class_sizes.py ; grep -rn '0/68\|0 of 68\|conflicting amendments' --include=*.md --include=*.txt --include=*.py . ; sed -n '55,110p' docs/evidence/spec-claims/spec-claims.txt`

**SURVIVED · line 67 · material · number-without-path**

> That order is forced by measurement, not taste: most labelled items have no extractable quoted anchor at all

- **problem:** No path is cited for this measurement claim. It traces to CONTEXT.md line 101 (§6): '26/33 and 35/42 labelled items have no extractable quoted anchor' - which docs/evidence/spec-claims/spec-claims.txt files in the NOT-IN-REPO pile as '^ pilot pool, not committed'. On the shipped, committed eval set the corresponding figure is exactly 41 of 82 items (50.0%) with no instruction carrying an anchor - which is not 'most'. So the sentence asserts a measurement that is either uncheckable (pilot pool) or, on the corpus this README ships, false as stated.
- **auditor checked:** python over data/evalset/items.jsonl -> 'items 82 items with NO instruction carrying an anchor: 41' and 'instructions 208 with anchor 90 with designation 128'. grep -n 'no extractable quoted anchor' CONTEXT.md -> line 101 '26/33 and 35/42 labelled items have no extractable quoted anchor'. sed -n '55,110p' docs/evidence/spec-claims/spec-claims.txt -> '§6  26/33 and 35/42 items with no extractable anchor  26  -  ^ pilot pool, not committed'.
- **refuter (could not kill it):** Survives, but weaker than reported — relay it with the caveat. Reading README lines 55-80 whole: the sentence carries no path, and none appears in the paragraph before or after (the surrounding text cites only src/cfr_resolve.py and agents/A1-SKILL.md). The upstream measurement is CONTEXT.md line 101 ('26/33 and 35/42 labelled items have no extractable quoted anchor'), which spec-claims.txt files as NOT-IN-REPO '^ pilot pool, not committed', and which context/11-REMEDIATION-2.md:788 orders 'RE-DERIVE at CH-01b ... Until re-derived, delete the "~80%" gloss'. I re-ran the count on the shipped set myself: 82 items, 41 with no instruction carrying a non-empty anchor (exactly 50.0%, no blank-string anchors), so 'most' is not supported per item. HOWEVER the auditor's 'false as stated' half is contestable: per instruction the figure is 118 of 208 without an anchor = 56.7%, a slim majority, so '
- **refuter ran:** `python -c "import json;items=[json.loads(l) for l in open('data/evalset/items.jsonl',encoding='utf-8')];print(len(items), sum(1 for o in items if not any(i.get('anchor') for i in o['instructions'])))" ; sed -n '55,80p' README.md ; grep -rn 'no extractable' --include=*.md --include=*.txt .`

**SURVIVED · line 217 · material · internal-contradiction**

> B0′ is also **the only arm in the packet not at temperature 0** — self-consistency at 0 is a no-op, and the deviation is ruled in `QUESTIONS.md` Q22.

- **problem:** Two other arms in the packet also did not run at temperature 0: B0-sonnet and B0-agent-sonnet. claude-sonnet-5 rejects the temperature parameter (HTTP 400, measured), so src/arms.py omits the field entirely and those arms ran at the model default. checkpoint-result.txt names this explicitly as 'A CONFOUND, not merely a limitation'. The sonnet artifacts are kept and shipped (README line 147: 'Artifacts kept, labelled withdrawn'), so they are in the packet. The claim is inherited verbatim from Q22 and src/arms.py's docstring, but it is false as written and understates a second, separately-documented temperature deviation.
- **auditor checked:** grep -rn 'temperature' src/*.py -> src/arms.py:450-452 'model, reps, temperature, tag = SONNET, 1, None, "-sonnet"' / print '...temperature OMITTED (the model rejects the parameter)'; src/apiclient.py:109 'if temperature is not None: body["temperature"]=...'. cat docs/evidence/checkpoint/checkpoint-result.txt -> 'sonnet-5 REJECTS `temperature` (HTTP 400, measured), so this subset ran at the model default while every haiku arm ran at 0'. AI-USE.md:38 states the same.
- **refuter (could not kill it):** Could not kill. src/arms.py:450 sets `model, reps, temperature, tag = SONNET, 1, None, "-sonnet"` and prints 'temperature OMITTED (the model rejects the parameter)'; src/apiclient.py only sets the field `if temperature is not None`, so B0-sonnet and B0-agent-sonnet ran at the sonnet default, not 0. docs/evidence/checkpoint/checkpoint-result.txt lines 74-78 call this out as '2. A CONFOUND, not merely a limitation: sonnet-5 REJECTS `temperature` (HTTP 400, measured), so this subset ran at the model default while every haiku arm ran at 0.' Those arms are shipped, not deleted — `ls docs/evidence/checkpoint/` lists B0-sonnet-rep1.json and B0-agent-sonnet-rep1.json at top level as well as under withdrawn/, and README:147 says 'Artifacts kept, labelled withdrawn'. The only defense available is that 'the packet' (a word used exactly once in README, undefined) means the six headline arms in the a
- **refuter ran:** `grep -n 'temperature' src/arms.py ; sed -n '445,455p' src/arms.py ; grep -n 'CONFOUND\|temperature' docs/evidence/checkpoint/checkpoint-result.txt ; ls docs/evidence/checkpoint/ ; grep -n 'packet\|sonnet' README.md`

**Could not check — stated rather than dropped:**

- Line 518-520: 'Prior et al., NLLP@ACL 2025' and 'cfpb/regulations-parser' as prior art - THIRD-PARTY.md §6 lines 107-117 do carry both citations, but I have no network access and cannot confirm the paper or repo exists externally as described.
- Lines 22-39 and 47-57: the domain narrative (OFR cannot incorporate a defective instruction; NARA publishes a permanent citable editorial note; the remedy is a correcting document) - assertions about Federal Register practice, not traceable to any committed artifact. Only the note_text field in data/evalset/items.jsonl was checkable, and it does match the worked example verbatim.
- Line 350's '71.4% of all its errors' is not printed in any artifact; I derived it from a1-result.txt's published rates (B0-agent 54/82 -> 28 errors; missed-defect 0.4878*41 = 20; 20/28 = 71.43%). It is arithmetically correct but the README does not say it is a derivation, unlike the +17.1 pp subtraction at line 178 which it flags as done in the open.
- Line 375: the IETF-errata provenance of the transferable hypothesis - spec-claims.txt lists all four IETF figures as NOT-IN-REPO ('second corpus, not in this repository'). README explicitly says it 'is not re-derived here and it carries no weight here', so I did not treat it as a claim, but I also cannot check it.
- docs/evidence/runs/cost_ledger.csv holds 40 rows each for B0-sonnet and B0-agent-sonnet with 20 duplicated run_ids per arm, against the 20 predictions in checkpoint/B0-agent-sonnet-rep1.json. README's '13 of 20' matches the committed arm JSON (I counted 20 predictions, 13 empty), so this is a ledger-integrity question outside README's claims - I did not resolve why the ledger carries double.

### `REPRODUCE.md` — 311 lines read, 6 findings

**SURVIVED · line 88 · material · internal-contradiction**

> The 26 skips are the tests that need `data/raw/` — 824 MB of source XML that is git-ignored.

- **problem:** `data/raw/` is 1.44 GB, not 824 MB. Line 272 of this same file gives 234 files / 1,443,366,993 B = 1.44 GB, and lines 274-276 explicitly correct this exact error ("The 824 MB figure quoted elsewhere in this project is the eCFR titles alone ... not the whole raw tree"). Line 88 is the error being corrected, reintroduced 186 lines earlier in the same document. It is also the error PROGRESS.md:194 already logged as a corrected finding (`data/raw/` is *"~824 MB"* -> **1.44 GB**). And the 26 skips are not eCFR-only: running the suite from an extracted zip shows they need data/raw/fr (15), data/raw/cfr (9, incl. test_review_ch03_round2_findings) and data/raw/ecfr (2).
- **auditor checked:** python walk of data/raw: `ecfr 50 824298523 / cfr 110 349679334 / fr 74 269389136 / total 234 1443366993`. `grep -n "1.44 GB|data/raw" PROGRESS.md` -> line 194 `| \`data/raw/\` is *"~824 MB"* | **1.44 GB**. 824 MB is the eCFR titles alone |`. `python -m pytest -q -rs` from an extracted `git archive HEAD` zip -> 26 data/raw skips split across tests/test_attribute_amdpars.py (data/raw/fr), tests/test_cfr_pit.py (data/raw/cfr), tests/test_harvest_ednotes.py (data/raw/ecfr), tests/test_review_ch03_round2_findings.py (data/raw/cfr).
- **refuter (could not kill it):** SURVIVES. I could not kill this. Direct os.walk of data/raw gives ecfr 50/824,298,523 + cfr 110/349,679,334 + fr 74/269,389,136 = 234 files / 1,443,366,993 B, byte-identical to this same file's own table at lines 269-272. Line 88 attaches the 824 MB figure to `data/raw/` as a whole, and lines 274-276 of the SAME file explicitly correct exactly that misattribution ('The 824 MB figure quoted elsewhere in this project is the eCFR titles alone ... not the whole raw tree'). Line 88 is an instance of the error its own document corrects 186 lines later. It is also already on the CH-11 corrected-findings table at PROGRESS.md:194 ('| `data/raw/` is *"~824 MB"* | **1.44 GB**. 824 MB is the eCFR titles alone |'), i.e. a defect the project has already logged as fixed and which is still live here. This is not a dated record or a deliberate quotation of an old figure — it is a plain present-tense fact
- **refuter ran:** `python -c "import os; [print(d, sum(1 for r,_,fs in os.walk(os.path.join('data','raw',d)) for f in fs), sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(os.path.join('data','raw',d)) for f in fs)) for d in ['ecfr','cfr','fr']]" ; grep -n "824\|1.44 GB" PROGRESS.md ; grep -rn "data/raw" tests/*.py | grep -i skip ; sed -n '264,277p' REPRODUCE.md`

**REFUTED · line 207 · material · other**

> `A1-iter1`, that identity was declared in `CHANGELOG.md` before the runs, and billing

- **problem:** CHANGELOG.md contains no occurrence of the string `A1-minus-skill`, in HEAD or in any commit in history. The identity was declared before the runs, but in `agents/A1.md` (lines 22-27), `agents/A1-SKILL.md` (line 12) and `src/a1.py` (lines 14-19) — not in CHANGELOG.md. The claim is substantively true and the cited path is wrong.
- **auditor checked:** `grep -n "A1-minus-skill" CHANGELOG.md` -> exit=1, no output. `git log --oneline --all -S"A1-minus-skill" -- CHANGELOG.md` -> empty. `grep -rn "A1-minus-skill" --include=*.md .` -> agents/A1-SKILL.md:12, agents/A1.md:22,24,27, docs/evidence/ch06-a1/goldens.md:199, REPRODUCE.md:206 only.
- **refuter (refuted):** REFUTED — the auditor grepped for the hyphenated token only. CHANGELOG.md:278 carries the declaration under its own heading '### The ablation identity, declared now rather than discovered later': '`A1 minus skill` **is** `A1-iter1`: both are *B0-agent + `cfr_resolve`, no procedure*. They are the same configuration under two names, so the arm is **run once** and reported in both rows with the identity stated.' The project's CHANGELOG uses the spaced form 'A1 minus skill' (it also writes 'A1 minus tool' two lines down); grep for 'A1-minus-skill' misses it. The 'before the runs' half also checks out: `git log --all -S"A1 minus skill" -- CHANGELOG.md` returns exactly one commit, e12466c (2026-08-31 07:41:37, 'CH-06 section 2a: BOTH iteration cards with their PREDICTIONS, committed before the build'), and `git show e12466c:CHANGELOG.md` contains the line at 179. agents/A1.md:24-25 cites that 
- **refuter ran:** `grep -n "minus" CHANGELOG.md ; sed -n '270,282p' CHANGELOG.md ; git log --format="%h %ad %s" --date=iso --all -S"A1 minus skill" -- CHANGELOG.md ; git show e12466c:CHANGELOG.md | grep -n "minus skill"`

**REFUTED · line 265 · cosmetic · number-without-path**

> machine at CH-11, transcribed into `PROGRESS.md`'s CH-11 entry:

- **problem:** The four-row table that follows (50 / 824,298,523; 110 / 349,679,334; 74 / 269,389,136; 234 / 1,443,366,993) is not in PROGRESS.md. PROGRESS.md's CH-11 entry carries only the rollup "1.44 GB" at line 194. The per-directory rows appear only in THIRD-PARTY.md:75-76. The numbers themselves are correct — I re-measured them on disk and they match to the byte — so this is a wrong citation, not a wrong number.
- **auditor checked:** `grep -rn "1,443,366,993|824,298,523|349,679,334|269,389,136" --include=*.md .` -> only ./REPRODUCE.md:269-272 and ./THIRD-PARTY.md:75-76. `grep -n "1.44 GB|data/raw" PROGRESS.md` -> line 194 has "1.44 GB" and nothing else numeric. Direct os.walk of data/raw reproduces all four rows exactly.
- **refuter (refuted):** REFUTED — differently-formatted version in the cited artifact. PROGRESS.md's CH-11 entry runs from line 14 to line 253, and line 194 inside it reads '| `data/raw/` is *"~824 MB"* | **1.44 GB**. 824 MB is the eCFR titles alone |' — that is the table's total row (1,443,366,993 = 1.44 GB) and the eCFR attribution that lines 274-276 spell out, transcribed into the CH-11 entry exactly as the sentence claims. The auditor grepped only for the comma-formatted byte counts (1,443,366,993 etc.) and so could not match the rollup form. The per-directory rows are additionally corroborated in THIRD-PARTY.md:75-76, and the auditor concedes all four rows reproduce to the byte on disk. So the measurement is real, made at CH-11, and recorded in the artifact named; the most that can be said is that PROGRESS.md carries the rollup rather than the four-way split, which is not a wrong citation. Cosmetic at wors
- **refuter ran:** `grep -n "^## " PROGRESS.md | head -4 ; sed -n '185,196p' PROGRESS.md ; grep -rn "1,443,366,993\|824,298,523\|349,679,334\|269,389,136" --include=*.md .`

**REFUTED · line 176 · cosmetic · internal-contradiction**

> It is the only arm in the packet not at temperature 0.

- **problem:** GOOD.md §8 records that `claude-sonnet-5` rejects the temperature parameter (HTTP 400, measured) and that the sensitivity subset therefore "runs at the model default". The two withdrawn sonnet arms are in this file's own cost table at lines 233-234, so B0prime is not the only arm in the packet not at temperature 0. (The sentence is copied verbatim from QUESTIONS.md Q22, which carries the same over-claim.) Nothing downstream turns on it — the sonnet arms are withdrawn and are not in the six-arm primary matrix.
- **auditor checked:** `sed -n '122,175p' GOOD.md` -> "**Temperature 0** on every haiku arm. **`claude-sonnet-5` rejects the parameter** (HTTP 400, measured), so the sensitivity subset runs at the model default." `sed -n '233,234p' REPRODUCE.md` -> B0-agent-sonnet and B0-sonnet rows present in the packet's cost table. `sed -n '1385,1420p' QUESTIONS.md` -> Q22 contains the same phrase.
- **refuter (refuted):** REFUTED — the claim is about a different set than the auditor assumed, and it matches GOOD.md's own vocabulary. GOOD.md:128-131 reads 'Temperature 0 on every haiku arm. claude-sonnet-5 rejects the parameter (HTTP 400, measured), so the sensitivity SUBSET runs at the model default.' GOOD.md itself distinguishes 'arm' (haiku) from 'subset' (sonnet) — so 'the only ARM not at temperature 0' is consistent with the frozen spec, not contradicted by it. The sentence also sits inside the Tier-2 protocol table whose immediately preceding row pins '**Model** | **claude-haiku-4-5-20251001** — dated, never the floating alias', and the six commands the section documents are B0 / B0-agent / B0prime / A1 / A1-iter1 / A1-minus-tool. The two sonnet rows appear in the cost table only, both tagged *(withdrawn)*, with no reproduction command anywhere in the file — REPRODUCE.md never asserts a temperature for
- **refuter ran:** `grep -n -B3 -A6 "rejects the parameter" GOOD.md ; sed -n '170,178p' REPRODUCE.md ; grep -n -i "sonnet\|withdraw" REPRODUCE.md ; sed -n '1405,1412p' QUESTIONS.md`

**REFUTED · line 21 · cosmetic · other**

> the uploaded zip measured **10,613,737 B = 10.61 MB** (`docs/evidence/ch14-clean-clone/rehearsal.txt` — `inventory.md` records 10.18 MB from an earlier commit)

- **problem:** The cited path does contain 10,613,737, but that measurement is from commit 263ed29 and is now stale at HEAD (810e2b1). `git archive --format=zip HEAD` currently produces 11,221,486 B = 11.22 MB over 374 entries, against the rehearsal's 367. The file flags inventory.md's 10.18 MB as "from an earlier commit" but presents 10.61 MB as current. No decision changes (still 4.5x under the 50 MB cap), but the figure a judge sees will not be the figure they measure.
- **auditor checked:** `git archive --format=zip HEAD -o scratchpad/rep.zip` then python zipfile -> `entries 374 / zip bytes 11221486`. `git rev-parse HEAD` -> 810e2b1651630400dd8a892d002a8542ac30bd16; rehearsal.txt line 6 records commit 263ed2997b488432f91b09448ec755b45b6a24da and line 32 `zip 10,613,737 B = 10.61 MB`. `git diff --name-only 263ed29 HEAD --diff-filter=A | wc -l` -> 7, matching the 374-367 entry delta.
- **refuter (refuted):** REFUTED — the number IS in the cited artifact, verbatim. rehearsal.txt line 32 reads 'zip                 10,613,737 B = 10.61 MB (cap 50 MB, CH-14a limit 45 MB)' with 'entries 367' beneath it, under the header 'ENVIRONMENT 3 - the EXTRACTED zip'. The sentence is a past-tense record of a measurement shipped with its generating artifact — exactly what hard rule 14 requires — not a claim about the current HEAD. Its staleness is structural and unfixable: the archive grows with every commit, and it moved again while I was verifying. The auditor measured 11,221,486 B at 810e2b1; HEAD is now a0432e7 and `git archive --format=zip HEAD` gives 374 entries / 11,227,551 B — a third value. Any figure written into the file is stale by the next commit, so 'the figure a judge sees will not be the figure they measure' is true of every committed size measurement in this repo, including the 61.70 MB track
- **refuter ran:** `git rev-parse HEAD ; git archive --format=zip HEAD -o scratchpad/rep.zip ; python -c "import zipfile,os;p='scratchpad/rep.zip';print('entries',len(zipfile.ZipFile(p).namelist()),'zip bytes',os.path.getsize(p))" ; sed -n '1,40p' docs/evidence/ch14-clean-clone/rehearsal.txt`

**REFUTED · line 91 · cosmetic · other**

> `tests/test_size_guard.py`, which inspects the live repository and carries its own reason string: *"not a git work tree (an extracted submission zip is a plain directory)"*

- **problem:** Both extra skips are indeed in tests/test_size_guard.py (verified), but only one of the two carries that reason string. The second skips with "cannot read bc99ef4:.githooks/pre-commit from git" (tests/test_size_guard.py:75, the `_old_hook_source()` guard), which is a different mechanism — `git show` failing in a non-repo, not the `needs_git_repo` marker. The file has exactly one `@needs_git_repo` decorator.
- **auditor checked:** `python -m pytest -q -rs` from the extracted zip -> `SKIPPED [1] tests\test_size_guard.py:75: cannot read bc99ef4:.githooks/pre-commit from git` and `SKIPPED [1] tests\test_size_guard.py:278: not a git work tree (an extracted submission zip is a plain directory)`; `314 passed, 28 skipped`. `grep -c "@needs_git_repo" tests/test_size_guard.py` -> 1.
- **refuter (refuted):** REFUTED — misparsed relative clause. The full sentence is 'two more, both in `tests/test_size_guard.py`, which inspects the live repository and carries its own reason string: ...'. The antecedent of 'which' is the FILE, not each of the two skips. Every clause is true of the file: tests/test_size_guard.py:47-52 computes `_in_git_repo` by running `git rev-parse --is-inside-work-tree` with cwd=REPO (it inspects the live repository) and defines `needs_git_repo = pytest.mark.skipif(not _in_git_repo, reason="not a git work tree (an extracted submission zip is a plain directory)")` — the quoted string is present character-for-character. REPRODUCE.md never says both skips carry that string, never mentions the `@needs_git_repo` marker, and never claims one mechanism; the auditor's own evidence confirms the load-bearing claims (both extra skips are in that file, count is 314/28). Both skips also s
- **refuter ran:** `sed -n '40,58p' tests/test_size_guard.py ; sed -n '68,80p' tests/test_size_guard.py ; grep -n "needs_git_repo\|pytest.skip" tests/test_size_guard.py ; grep -n "passed" docs/evidence/ch14-clean-clone/rehearsal.txt ; sed -n '86,94p' REPRODUCE.md`

**Could not check — stated rather than dropped:**

- Line 25: the clone URL https://github.com/chinmoypaul8897/instruction-that-wont-execute — I am forbidden network calls, so I cannot confirm the repository exists, is public, or matches this tree.
- Lines 22 and 294-296: govinfo.gov returns 200 / www.ecfr.gov and www.federalregister.gov return HTTP 403, "verified 2026-08-30 02:17 UTC". The date and verdicts are corroborated verbatim in CLAUDE.md:45 and CONTEXT.md:145, but I cannot re-measure them (no network permitted).
- Lines 240-241: "Elapsed time was less than the sum, because some arms ran concurrently." The ledger records per-call wall_clock_s (summing to 6026.7, which matches) but carries no session start/end timestamps, so the concurrency claim has no artifact to check against. QUESTIONS.md Q26 independently confirms two jobs were launched concurrently, which makes the claim consistent but not measured.
- Lines 6-9: the ordering claim that "Tier 1 below was run from a clean environment BEFORE it was written down". PROGRESS.md lines 55-97 record the runs and REPRODUCE.md was committed at 76b9f4a, but nothing in the repo timestamps the run relative to the prose.
- Lines 42-45 and 216-217: I ran `refetch.py --verify-only` (read-only, verified: 4/4 6/6 2/2 3/3 3/3, exact closing string matched) and `pytest -q` (342 passed here because data/raw is populated locally — 316+26 in a clean clone, consistent). I did NOT run analyse_checkpoint.py or analyse_a1.py because they regenerate committed result files and I am read-only; their quoted strings were verified against the committed checkpoint-result.txt/.json and a1-result.txt instead, and rehearsal.txt records both as byte-identical on regeneration.
- Line 135: "143.13 s measured" for run_bscript.py is corroborated at PROGRESS.md:90, but I did not re-run the 2,000-draw permutation null (~2.5 min) to confirm the timing on this machine.

### `SAFETY.md` — 150 lines read, 3 findings

**SURVIVED · line 23 · material · internal-contradiction**

> The only components that reach the network at all are `src/apiclient.py`, which posts to the Anthropic Messages API, and `refetch.py`, which downloads public XML from govinfo.

- **problem:** False as written, and it is the load-bearing boundary claim of the section that answers ground rule 04. `src/a1.py` — the runner for the headline A1 arm, with its own `if __name__ == "__main__"` at line 710 — opens its own socket to the Anthropic Messages API at `src/a1.py:486-490` (`def _post` -> `urllib.request.urlopen`). It imports only API_URL/API_VERSION constants from apiclient (line 77); it does NOT route its calls through `apiclient.call_messages`. Separately, `refetch.py` contains ZERO urlopen calls of its own — the govinfo fetches live in `src/harvest_ednotes.py:396,441`, `src/cfr_pit.py:461,469` and `src/attribute_amdpars.py:591`, two of which (harvest_ednotes, attribute_amdpars) are independently runnable via their own `__main__`. The true count of network-reaching modules is five, not two.
- **auditor checked:** grep -rn -E '^\s*(import|from)\s+(urllib|requests|socket|http\.client|httpx|aiohttp)' src/*.py *.py  ->  src/a1.py:71-72, src/apiclient.py:26-27, src/attribute_amdpars.py:49, src/cfr_pit.py:54, src/harvest_ednotes.py:49.  grep -rn 'urlopen' src/a1.py src/apiclient.py src/harvest_ednotes.py src/cfr_pit.py src/attribute_amdpars.py refetch.py  ->  7 call sites across 5 files; refetch.py 0.  grep -c 'urlopen' refetch.py -> 0.  grep -n '__main__' -> src/harvest_ednotes.py:616, src/attribute_amdpars.py:979, src/a1.py:710.  sed -n '485,491p' src/a1.py -> 'def _post(key, body, timeout=180): req = urll
- **refuter (could not kill it):** I tried to kill this and could not. The sentence is absolute ("at all") and carries no scope restriction — the preceding clause already carved out the scorer and resolver separately, so this one is a whole-system enumeration. It is false. `grep -rn 'urlopen' src/*.py *.py` returns SEVEN call sites in FIVE files, and src/a1.py is one of them: src/a1.py:490 `with urllib.request.urlopen(req, timeout=timeout) as resp:` inside `def _post(key, body, timeout=180)` at :485, which builds its own Request against API_URL with the x-api-key header (:487-489). It is called twice, at :514 and :578. a1.py imports only `API_URL, API_VERSION, ApiError, load_api_key` from apiclient (:77); the ONLY occurrence of `call_messages` anywhere in a1.py is a docstring line at :498 saying it retries 'exactly as apiclient.call_messages does' — i.e. it deliberately reimplements rather than delegates. a1.py is a runna
- **refuter ran:** `grep -rn 'urlopen' src/*.py *.py ; grep -n 'call_messages\|__main__\|apiclient\|API_URL' src/a1.py ; sed -n '485,491p' src/a1.py ; grep -c 'urlopen' refetch.py ; grep -n 'fetch' refetch.py`

**REFUTED · line 146 · material · other**

> And CH-03 and CH-04 would have to pass the review gates they currently fail.

- **problem:** Understates the gate position by two thirds, in the section headed "What would have to be true before this ran on live rules". Six chunks carry a review gate and none passed; SAFETY.md names two. Omitted are CH-02 (FULL gate, never reviewed, and its own done-when is the 0.90 completeness this file admits failed), CH-05 (code-only, not reviewed — the `cfr_resolve` whose one-way defect this file documents at line 106), CH-06 (CODE-ONLY, not reviewed — the chunk that produced the 0.7195 headline and the 16/82 checkpoint this file cites), and CH-08 (NUMBERS gate, not reviewed — the gate `PROCESS.md` §6 binds 'before any number reaches the README'). This file's own README pointer at line 149-150 leads to a table that lists all six. No claim that a gate PASSED is made anywhere in SAFETY.md.
- **auditor checked:** grep -n -iE 'pass|gate|review' SAFETY.md -> only line 146 mentions review gates; no PASS claim about any chunk gate.  grep -n -iE 'CH-02|CH-05|CH-06|CH-08' README.md | grep -iE 'gate|review' -> README.md:427 'CH-02 · AMDPAR attributor | FULL | **never reviewed.**', :430 'CH-05 · cfr_resolve | code-only | **not reviewed.**', :431 'CH-06 · SKILL.md + A1 | CODE-ONLY | **not reviewed.**', :432 'CH-08 · ablations and final arms | **NUMBERS** | **not reviewed — and this is the gate written for this document.**'.  STATUS.md:21 CH-03 'reviewed-FAIL x2 -> ESCALATED', :22 CH-04 'reviewed-FAIL x1'.
- **refuter (refuted):** The finding misreads the sentence's predicate. It does not claim to enumerate every gated chunk; it names the chunks that CURRENTLY FAIL a review gate — i.e. chunks that were reviewed and came back FAIL. STATUS.md:21 gives CH-03 'reviewed-FAIL x2 -> ESCALATED' and STATUS.md:22 gives CH-04 'reviewed-FAIL x1'. Those are the only two. CH-02, CH-05, CH-06 and CH-08 are NOT failing a review gate — README.md:427/430/431/432 record them as 'never reviewed' / 'not reviewed', which is a different state; an unreviewed chunk cannot 'currently fail' a review it never had. So the sentence is literally accurate and makes no false PASS claim, which the auditor concedes ('No claim that a gate PASSED is made anywhere in SAFETY.md'). The 'omission' also does not exist substantively: the same paragraph, ONE and TWO sentences earlier, already requires exactly the two omitted chunks' outstanding items — 'The
- **refuter ran:** `sed -n '140,152p' SAFETY.md ; grep -n -iE 'CH-0[2-9]' README.md | grep -iE 'gate|review|never|not reviewed' ; sed -n '15,35p' STATUS.md ; grep -n -iE 'pass|gate|review' SAFETY.md`

**REFUTED · line 61 · cosmetic · other**

> ## 3. The human checkpoint fires on 16 of 82 items, and code decides when

- **problem:** The 16 is quoted faithfully from the cited artifact, but it is a single-rep figure stated as a flat property of a three-rep arm, in a section whose thesis is that the routing is decided deterministically by code. Counting `record: human_checkpoint` entries against the enclosing item_id in the committed trajectories gives 16 distinct items in rep1, 17 in rep2, 16 in rep3 — the reasons are computed from `facts`, which for A1 depend on the model's tool use, so the count moves between reps. Not a fabricated number and not a wrong citation; the artifact does say 16 of 82. Flagged only because the heading generalises a per-rep count.
- **auditor checked:** grep -n -i 'checkpoint' docs/evidence/ch06-a1/a1-result.txt -> line 219 'items routed to the HUMAN CHECKPOINT: 16 of 82' (exact match to the quotation on SAFETY.md:63-64).  python, walking each jsonl and attributing each record:human_checkpoint to the last seen item_id -> A1-rep1 items 82 hc_records 16 distinct_items 16 / A1-rep2 items 82 hc_records 17 distinct_items 17 / A1-rep3 items 82 hc_records 16 distinct_items 16.
- **refuter (refuted):** The auditor refutes this one themselves ('Not a fabricated number and not a wrong citation; the artifact does say 16 of 82', severity cosmetic). I reproduced their per-rep count exactly — walking docs/trajectories/arms/A1-rep{1,2,3}.jsonl and attributing each record:human_checkpoint to its item gives 16 / 17 / 16 distinct items — and it defeats the finding rather than supporting it. 16 is the MODAL value across the three reps (2 of 3), and it is the value for rep1 and rep3, the two reps carrying the 0.7195 headline accuracy (a1-result.txt:139-140 gives per-rep accuracy ['0.7195','0.6707','0.7195']). Nothing is concealed by quoting it: the SAME cited artifact, at lines 130-149, is headed 'REP-TO-REP STABILITY AT TEMPERATURE 0' and publishes A1's rep variance in the open — 'rep1 vs rep2: 12 of 82 items differ', 'rep1 vs rep3: 10', 'rep2 vs rep3: 9' — plus the explicit statement 'A TEMPERAT
- **refuter ran:** `python -c "import json,glob,os;\nfor f in sorted(glob.glob('docs/trajectories/arms/A1-rep*.jsonl')):\n    ..." (walk each A1 rep jsonl, attribute record:human_checkpoint to last item_id) -> A1-rep1 items 82 hc_records 16 distinct 16 / A1-rep2 82 17 17 / A1-rep3 82 16 16 ; grep -n -B4 -A4 'HUMAN CHECKPOINT' docs/evidence/ch06-a1/a1-result.txt ; sed -n '130,150p' docs/evidence/ch06-a1/a1-result.txt `

**Could not check — stated rather than dropped:**

- Line 121-123, "No personal data is processed... Nothing in it is about an identifiable private individual" — no committed artifact enumerates the corpus for identifiable individuals. docs/evidence/secret-scan/scan.txt's PII rules are sourced from context/02-ABOUT-ME.md and target operator contact detail in the repo, not the federal text corpus. The claim is plausible for Federal Register text but has no generating script under docs/evidence/ backing it, so it is unverified rather than wrong.
- Line 20-21, "It does not file anything... or write to any system outside this repository." I verified the network surface (see finding 1) but did not exhaustively audit every file-write target in src/ for paths outside the repo root, so the second half of that sentence is untraced.
- Line 126-127, "src/apiclient.py returns it to its caller and reports nothing about it but its name." Strictly, src/apiclient.py:71-78 also exposes key_fingerprint(), which returns 'present(len=N)' — the key's LENGTH, not its name. The function has zero call sites outside its own definition (grep -rn key_fingerprint src/ tests/ *.py -> only src/apiclient.py:71 and a stale .pyc), so nothing is emitted in practice and I did not raise it as a finding; recording it so the discrepancy is not silently dropped.

### `STATUS.md` — 53 lines read, 8 findings

**SURVIVED · line 30 · material · other**

> this cell read `p = 0.4421` until 2026-08-31 — a digit transposition, and the only occurrence of that value anywhere in the repository

- **problem:** Two claims in this parenthetical are false. (a) 0.4421 is NOT the only occurrence in the repository — it appears in 7 tracked files, including docs/evidence/ch09-removed/leakage-result.txt:27 as a LIVE published McNemar p for the removed-experiment arm, and 6 times in docs/trajectories/build/CH-06.jsonl. (b) It was not 'a digit transposition': CH-06.jsonl records it as A1 rep1's own McNemar (b=16 c=11) — a real single-rep figure superseded by the 3-rep aggregate 0.4244, which is a different and more serious provenance story than a typo. The corrected value 0.4244 itself is right.
- **auditor checked:** grep -rln "0\.4421" . (git-tracked filter applied) -> TRACKED docs/evidence/ch09-removed/leakage-result.txt (1), docs/trajectories/build/CH-06.jsonl (6), CH-11.jsonl (6), CH-14a.jsonl (10), PROGRESS.md (2), README.md (1), STATUS.md (1). CH-06.jsonl record at 2026-08-31T02:58:45Z: 'A1 rep1 0.7195 (59/82) ... gap +6.1 pp McNemar p=0.4421 b=16 c=11'. python json read of docs/evidence/ch06-a1/a1-result.json -> comparisons/A1/mcnemar/p_value = 0.42435622215270996.
- **refuter (could not kill it):** SURVIVES. Both sub-claims fail. (a) 0.4421 is not unique: docs/evidence/ch09-removed/leakage-result.txt:27 prints 'McNemar exact two-sided p = 0.4421 (b=11 c=16 discordant=27)' as the LIVE published statistic for the removed-experiment (current-CFR-text) arm, and README.md:255 republishes it in the changelog row. Both predate CH-14a. (b) It was not a transposition. I recomputed the exact two-sided McNemar myself: b=16,c=11 -> 0.44206833839416504 = 0.4421, and b=15,c=10 -> 0.42435622215270996 = 0.4244 (the value in a1-result.json). docs/trajectories/build/CH-06.jsonl records 'A1 rep1 0.7195 (59/82) ... gap +6.1 pp McNemar p=0.4421 b=16 c=11'. So 0.4421 was A1 rep1's own real single-rep McNemar, superseded by the 3-rep aggregate — a stale-figure provenance story, not a typo. The corrected 0.4244 is right; the explanation attached to it is not. PROGRESS.md:329 repeats the same false uniquen
- **refuter ran:** `git grep -n "0\.4421" -- . | head -40 ; sed -n '1,45p' docs/evidence/ch09-removed/leakage-result.txt ; python -c "from math import comb;\nimport json;\nmc=lambda b,c:(lambda n,k:min(2*sum(comb(n,i) for i in range(k+1))/2**n,1.0))(b+c,min(b,c));\nprint('b16c11',mc(16,11));print('b15c10',mc(15,10));print(json.load(open('docs/evidence/ch06-a1/a1-result.json'))['comparisons']['A1']['mcnemar'])"`

**SURVIVED · line 32 · material · number-path-disagrees**

> overrides it toward EXECUTES nearly twice as often (45 vs 24)

- **problem:** The generating artifact gives 46, not 45. docs/evidence/ch06-a1/a1-result.txt line 117 (LAYER 2 table) reads 'A1  128  75  53  41.4%  46  7' — override_toward_EXECUTES = 46 for A1 and 24 for A1-iter1 (line 115). '45 vs 24' appears nowhere else in the repository; STATUS.md line 32 is its only occurrence, and the cell cites no path for it.
- **auditor checked:** sed -n '117p' docs/evidence/ch06-a1/a1-result.txt -> '  A1                     128      75        53  41.4%          46        7'; sed -n '113,118p' shows A1-iter1 = 24. grep -rn "45 vs 24|46 vs 24" over the repo -> only STATUS.md:32. a1-result.json carries no tool-gap block, so a1-result.txt is the sole artifact.
- **refuter (could not kill it):** SURVIVES. The sole generating artifact gives 46, not 45. docs/evidence/ch06-a1/a1-result.txt LAYER 2 table (line 117) reads 'A1  128  75  53  41.4%  46  7'; A1-iter1 (line 115) reads '124  89  35  28.2%  24  11'. So the pair is 46 vs 24. I confirmed a1-result.json carries no tool-gap / override block at all (its only keys are comparisons, ledger, n, per_class_recall, results, seed; a full walk found no override or ->EXECUTES key), so a1-result.txt is the only source. Repo-wide grep for the phrase finds '45 vs 24' at STATUS.md:32 and nowhere else, and no docs/, README.md or CHANGELOG.md text carries an override count at all. The cell cites no path for the figure. Off by one against its own evidence.
- **refuter ran:** `sed -n '105,125p' docs/evidence/ch06-a1/a1-result.txt ; grep -rn "45 vs 24\|46 vs 24\|3\.09 vs 4\.48" --include=*.md --include=*.txt --include=*.json . ; python -c "import json;d=json.load(open('docs/evidence/ch06-a1/a1-result.json'));print(list(d.keys()))"`

**SURVIVED · line 32 · material · false-gate-pass**

> | CH-08 · ablations and final arms | none | **built** |

- **problem:** The Gate column says 'none' for CH-08, but PROCESS.md §6 assigns CH-08 a NUMBERS gate and binds it 'before any number reaches the README'. Under this file's own rule at line 7 ('A gated chunk is done only at reviewed-PASS'), marking CH-08 ungated makes 'built' read as done and hides one of the six outstanding gates. STATUS.md contradicts itself: line 42 explicitly lists CH-08 among 'six gated chunks, none passed' — 'CH-08 (NUMBERS, the gate PROCESS.md §6 binds "before any number reaches the README")'.
- **auditor checked:** grep -n "CH-08" PROCESS.md -> line 200: '| CH-08 | ablations (**1 rep**, pre-registered) · final arms × 3 · McNemar · bootstrap clustered by FR document | **NUMBERS** |'; line 173: '**Applies to the CHECKPOINT before its call is acted on, and to CH-08 before any number reaches the README.**'. grep -n "reviewed-PASS" STATUS.md -> only lines 3 and 7 (the legend); no chunk is marked PASS.
- **refuter (could not kill it):** SURVIVES. PROCESS.md is the governing document (CLAUDE.md precedence: CONTEXT.md -> PROCESS.md -> plan.md) and it assigns CH-08 a gate twice: §7's chunk table line 200 '| CH-08 | ablations (**1 rep**, pre-registered) · final arms × 3 · McNemar · bootstrap clustered by FR document | **NUMBERS** |', and §6 line 173 'Applies to the CHECKPOINT before its call is acted on, and to CH-08 before any number reaches the README.' plan.md:116 says 'GATE: none' and STATUS.md:4 says it is 'Seeded from plan.md' — but plan.md loses to PROCESS.md on precedence, and STATUS.md's own line 42 already concedes the point, listing 'CH-08 (NUMBERS, the gate PROCESS.md §6 binds "before any number reaches the README")' among six gated chunks with none passed. Combined with line 7 ('A gated chunk is done only at reviewed-PASS'), an ungated 'built' reads as done. grep confirms no chunk anywhere in STATUS.md is marke
- **refuter ran:** `grep -n "CH-08" PROCESS.md plan.md ; sed -n '165,205p' PROCESS.md ; grep -n "reviewed-PASS" STATUS.md`

**SURVIVED · line 39 · material · untraceable-number**

> **THE 50 MB BLOCKER WAS NEVER A BLOCKER: the zip is 10.24 MB, 4.9× under cap** (Q27)

- **problem:** No artifact contains 10.24 MB. The two committed measurements are 10,182,500 B = 10.18 MB (docs/evidence/ch14-size/inventory.md:8, at commit bc99ef4) and 10,613,737 B = 10.61 MB (docs/evidence/ch14-clean-clone/rehearsal.txt:32, at commit 263ed29); the archive at HEAD measures 11,227,551 B = 11.23 MB. 10.24 appears only in STATUS.md:39 and AI-USE.md:255. The '4.9×' derives from the 10.18 figure (50/10.18 = 4.91, as inventory.md:11 states), so the multiplier survives but the byte figure is invented.
- **auditor checked:** grep -rn "10\.24 MB|10\.18 MB" over .md/.txt -> AI-USE.md:255 (10.24), inventory.md:8 (10.18), rehearsal.txt:32 (10.61), QUESTIONS.md Q27 (10.18), REPRODUCE.md:21 (10.61, noting inventory records 10.18). git archive --format=zip HEAD | wc -c -> 11227551. No file in the repo produces 10.24.
- **refuter (could not kill it):** SURVIVES. No artifact produces 10.24 MB. The two committed measurements are docs/evidence/ch14-size/inventory.md:8 '`git archive --format=zip HEAD` : **10,182,500 B = 10.18 MB = 9.71 MiB**' (at commit bc99ef4) and docs/evidence/ch14-clean-clone/rehearsal.txt:32 'zip 10,613,737 B = 10.61 MB'. I re-measured HEAD myself: git archive --format=zip HEAD | wc -c = 11227551 B = 11.23 MB. A repo-wide grep for 10.24 in shipping text hits exactly two places, both narrative: STATUS.md:39 and AI-USE.md:255 ('the zip is 10.24 MB'). Every other file — QUESTIONS.md Q27:1813, selection-rule.md:77, selection-applied.md:78, derived-reproduction.md:48, PROGRESS.md:262, REPRODUCE.md:21, SUBMISSION.md:30-31 — uses 10.18 or 10.61. The auditor is also right that the '4.9×' survives: inventory.md:11 states the factor as 4.91x off the 10.18 figure. The multiplier is sourced; the byte figure is not.
- **refuter ran:** `git archive --format=zip HEAD | wc -c ; grep -rn "10\.24\|10\.18\|10\.61\|10,182,500\|10,613,737" --include=*.md --include=*.txt . | grep -v trajectories ; sed -n '1,20p' docs/evidence/ch14-size/inventory.md ; sed -n '25,40p' docs/evidence/ch14-clean-clone/rehearsal.txt`

**REFUTED · line 42 · cosmetic · internal-contradiction**

> `STATUS.md`/`AI-USE.md` say 450/81 blobs where the artifact says 462/84

- **problem:** Present-tense claim that is now false and is contradicted three lines above in the same file. CH-11c corrected both: STATUS.md:39 now reads '462 text blobs / 84 commits' with a dated note, and AI-USE.md:230 reads 462/84 with its own dated correction at :235-241. The underlying figures (462/84 authoritative, 450/81 stale-but-real) are correct; only the 'say 450/81' status is stale.
- **auditor checked:** grep -n "450|462|84 commits" AI-USE.md -> :230 '**462** text blobs of history across **84** commits (docs/evidence/secret-scan/scan.txt)'; :235 'This row read "all 450 blobs of history" until CH-11c'. diff of git show HEAD:STATUS.md against the working file shows line 39 was rewritten from '450 blobs / 81 commits' to '462 text blobs / 84 commits' during this audit. head -20 docs/evidence/secret-scan/scan.txt -> repository 2453998f, commits 84, blobs 462; git show 0f3f4fe:docs/evidence/secret-scan/scan.txt -> f0a246b1, 81, 450.
- **refuter (refuted):** REFUTED. The auditor has mistaken a per-chunk historical record for a live claim. The sentence sits inside an enumeration introduced by '**Q30–Q35 raised**:' in the CH-11 row — it is a restatement of Q31's own title, which QUESTIONS.md:2217 gives near-verbatim as 'Q31 - `STATUS.md`'s CH-14a row states the secret sweep's scope as 450 blobs / 81 commits; the committed scan says 462 / 84'. A list of what a chunk raised is supposed to preserve the wording as raised. The file already carries the closure in both directions: line 39 was rewritten to '**462 text blobs / 84 commits** (`docs/evidence/secret-scan/scan.txt`, repository `2453998f`)' with the dated note '*this cell read 450 / 81 until CH-11c*', and the row immediately beneath (4b, CH-11c) records '**Q31:** sweep scope **450 / 81 → 462 / 84** in `STATUS.md` and `AI-USE.md`'. QUESTIONS.md:2461 marks Q31 CLOSED with the same narrative. T
- **refuter ran:** `git diff STATUS.md | head -40 ; grep -n "Q31" QUESTIONS.md ; sed -n '2217p;2461p' QUESTIONS.md`

**REFUTED · line 39 · cosmetic · internal-contradiction**

> **Q29: README.md, REPRODUCE.md, LICENSE, THIRD-PARTY.md, SAFETY.md and requirements.txt do not exist**

- **problem:** Stated in the present tense; all six files now exist, and line 42 of the same table says 'QUESTIONS.md Q29 is CLOSED — all six files that PROCESS.md §3 marked "ships" now exist.' Defensible as a dated per-chunk record, but the tense makes the table contradict itself.
- **auditor checked:** ls README.md REPRODUCE.md LICENSE THIRD-PARTY.md SAFETY.md requirements.txt -> all six present. cat requirements.txt -> single non-comment line 'pytest==9.1.1'.
- **refuter (refuted):** REFUTED. This is the CH-14a row of a one-line-per-chunk record, and the clause is the title of the question CH-14a raised at the time it ran — QUESTIONS.md:2073 reads 'Q29 - SUBMISSION COMPLETENESS. Six files that `PROCESS.md` §3 marks "ships" do not exist anywhere in the tree'. A per-chunk ledger that restates a chunk's raised questions is exactly the kind of dated record whose old text is meant to survive; rewriting it would erase the finding that produced CH-11. The resolution is not hidden — it is three rows below in the same table (row 4, CH-11: '**`QUESTIONS.md` Q29 is CLOSED** — all six files that `PROCESS.md` §3 marked "ships" now exist'), so no reader reaching the end of the table is left with the stale reading. I confirmed all six files are present. The auditor concedes the point themselves ('Defensible as a dated per-chunk record') and rates it cosmetic.
- **refuter ran:** `ls -1 README.md REPRODUCE.md LICENSE THIRD-PARTY.md SAFETY.md requirements.txt ; grep -n "Q29" QUESTIONS.md ; awk 'NR==39||NR==42' STATUS.md | cut -c1-200`

**REFUTED · line 23 · cosmetic · number-without-path**

> Spend USD 1.936 of 18.00

- **problem:** No path cited, and the figure does not appear in any docs/evidence/ artifact — docs/evidence/checkpoint/checkpoint-result.txt prints no spend line. Summing the ledger over the checkpoint arms (B0, B0-agent, B0-sonnet, B0-agent-sonnet) gives 1.935258; adding the model-id probe rows gives 1.935538, which reaches 1.936 only under round-half-up at three decimals. The claim is approximately right but is stated to four significant figures with no generating artifact; it appears elsewhere only in PROGRESS.md:664.
- **auditor checked:** python Decimal sum over docs/evidence/runs/cost_ledger.csv -> checkpoint arms 1.935258, probe-model-id 0.000280, arms+probe 1.935538, ledger total 11.632274, 3 empty cost cells. grep -rn "1\.936" over .md/.txt -> only PROGRESS.md:664 and STATUS.md:23.
- **refuter (refuted):** REFUTED — the number is right and it does come from a docs/evidence artifact; the auditor grepped for a literal string where the figure is a derived aggregate. Summing docs/evidence/runs/cost_ledger.csv over the checkpoint arms gives B0 0.204035 + B0-agent 1.472943 + B0-sonnet 0.050872 + B0-agent-sonnet 0.207408 = 1.935258, plus probe-model-id 0.000280 = 1.935538, which rounds to 1.936 under ordinary rounding (1.935538 > 1.9355) — not 'only under round-half-up' as the finding asserts. The generating artifact is the authoritative ledger the ground truth itself names, and it reproduces the figure to the printed precision. I also checked the auditor's premise about the artifact: checkpoint-result.txt indeed prints no spend line, but checkpoint-result.json does carry a `usage` block, so the claim that the checkpoint evidence is silent on cost is overstated. Finally, singling out this cell fo
- **refuter ran:** `python -c "import csv;from decimal import Decimal;from collections import defaultdict;rows=list(csv.DictReader(open('docs/evidence/runs/cost_ledger.csv',newline='',encoding='utf-8')));t=defaultdict(Decimal);c=defaultdict(int)\nfor r in rows:\n c[r['arm']]+=1\n if r['imputed_usd'].strip(): t[r['arm']]+=Decimal(r['imputed_usd'])\nprint([(a,c[a],str(t[a])) for a in sorted(t)]);ck=['B0','B0-agent','B0`

**SURVIVED · line 23 · cosmetic · other**

> Model sensitivity: on the same 20 items haiku +20.0 pp, sonnet-5 **−30.0 pp** — a flag, not a finding: n = 20, one rep, and sonnet rejects `temperature` so it ran at the model default.

- **problem:** Model attribution is CORRECT (sonnet-5 is confined to the 20-item sensitivity subset, never an evaluation arm) and every number reproduces from docs/evidence/checkpoint/checkpoint-result.txt. But this cell never records that the subset was subsequently WITHDRAWN, while line 42 says 'the sensitivity check **withdrawn**' and PROVENANCE.md:93 calls it 'WITHDRAWN as a harness defect — QUESTIONS.md Q19. No claim in this submission rests on it.' A reader of the CHECKPOINT row alone would take the −30.0 pp as live.
- **auditor checked:** cat docs/evidence/checkpoint/checkpoint-result.txt -> 'claude-sonnet-5, n=20  0.5000  0.2000  -30.0 pp' / 'haiku, THE SAME 20 items  0.5000  0.7000  +20.0 pp' / 'sonnet-5 REJECTS `temperature` (HTTP 400, measured)'. grep -n "sonnet" PROVENANCE.md -> :93 marks the subset WITHDRAWN. Ledger group-by confirms claude-sonnet-5 only on B0-sonnet (40), B0-agent-sonnet (40), probe-model-id (4).
- **refuter (could not kill it):** SURVIVES, and on stronger grounds than the auditor gave. The Q19 ruling that withdrew the subset does not merely withdraw it — QUESTIONS.md:1124 states the disposal condition explicitly: 'The `-sonnet` rows are **withdrawn**. No sensitivity claim appears in any CH-06 artifact. The artifacts stay on disk under `docs/evidence/checkpoint/` and are labelled withdrawn where they are cited.' STATUS.md:23 cites the −30.0 pp and the +20.0 pp and does not label them withdrawn, so it is the citation the ruling's own instruction misses. Every other citation complied: PROVENANCE.md:93 'the model-sensitivity subset only, which was **WITHDRAWN** as a harness defect — `QUESTIONS.md` Q19. No claim in this submission rests on it', and STATUS.md's own line 42 says 'the sensitivity check **withdrawn**'. The same cell already uses the word for the other withdrawal ('An earlier AMBER run is WITHDRAWN'), so t
- **refuter ran:** `grep -n -i "sonnet" PROVENANCE.md ; grep -n -i "sensitivity" QUESTIONS.md | head -20 ; sed -n '1110,1145p' QUESTIONS.md ; tail -25 docs/evidence/checkpoint/checkpoint-result.txt`

**Could not check — stated rather than dropped:**

- Lines 51-52: "Repository: chinmoypaul8897/instruction-that-wont-execute — private until CH-15. Anonymous curl returns 404, verified at CH-00." Verifying this needs a network request, which I am forbidden to make. Nothing in the repo re-attests it.
- Line 16/17/18/21 suite counts ("suite 22 green", "suite 61 green", "suite 121 green", "suite 278 green"): each traces only to PROGRESS.md prose (lines 1630, 1489, 1276, 623) and, for 278, to docs/reviews/REVIEW_CH-03.md:136 and docs/reviews/ch04-probe/mutation-report.txt. No committed pytest-output artifact exists under docs/evidence/ for any of them. Current collection is 342 tests, so all four are historical and unre-runnable as stated. (Line 30's "313 tests green" IS traceable, to docs/reviews/ch04-probe/mutation-report.txt.)
- Line 39: "It found 2 tests that fail in the zip a judge opens — one pre-existing since CH-02, one written by this chunk." docs/evidence/ch14-clean-clone/rehearsal.txt corroborates the count indirectly (clone 316 passed/26 skipped vs extraction 314 passed/28 skipped) but never names the two tests; the identification rests on AI-USE.md prose, not on a generating artifact.
- Line 42: "A 52-agent adversarial audit (8 dimensions, one refutation verifier per finding; 13 refuted, 31 survived)". PROGRESS.md:155-161 corroborates 52 agents / 44 findings / 13 refuted / 31 survived and names run wf_44b0dd6c-5e5, but the audit trajectories themselves are not in the repo (STATUS itself says the fence blocked them, Q30). The 8-dimensions figure is arithmetically consistent (8 + 44 = 52) but has no artifact.
- Line 22: "GOOD.md still saying n=76/38 pairs against the shipped 82/41 with no errata." The n=76/38-pairs text is confirmed at GOOD.md:60, :167 and :195-196, but "with no errata" is now stale — commit f0a246b added a 34-line addendum (GOOD.md:188 onward). I could not determine whether the CH-04 review's finding was meant to be frozen at review time; STATUS line 39 records the addendum, so the file is not silently inconsistent.

### `SUBMISSION.md` — 152 lines read, 4 findings

**SURVIVED · line 53 · material · internal-contradiction**

> The skips are raw-input-dependent tests: `data/raw/` holds 824 MB of source XML, is

- **problem:** 824 MB is wrong for `data/raw/` and this repository already corrects it elsewhere. `data/raw/` measures 234 files / 1,443,366,993 B = 1.44 GB. 824 MB is the eCFR titles ALONE. REPRODUCE.md:274-275 says verbatim: "The **824 MB** figure quoted elsewhere in this project is the **eCFR titles alone** ... not the whole raw tree", and PROGRESS.md:194 lists `data/raw/` is "~824 MB" as a known error whose correct value is 1.44 GB. SUBMISSION.md ships the uncorrected figure and cites no path for it. THIRD-PARTY.md:75 independently gives 1,443,366,993 B across 234 files.
- **auditor checked:** python -c walk over data/raw -> 'files 234 bytes 1443366993 = 1443.37 MB = 1.44 GB'. Grep tool for '824' over *.md -> REPRODUCE.md:269 '| `ecfr/` - 49 title XMLs plus the govinfo index | 50 | 824,298,523 |', REPRODUCE.md:274 'The **824 MB** figure quoted elsewhere in this project is the **eCFR titles alone**', PROGRESS.md:194 '| `data/raw/` is *"~824 MB"* | **1.44 GB**. 824 MB is the eCFR titles alone |', THIRD-PARTY.md:75 '**1,443,366,993 B across 234 files**'. sed -n '260,285p' REPRODUCE.md confirms the total row '| **total** | **234** | **1,443,366,993 = 1.44 GB** |'.
- **refuter (could not kill it):** SURVIVES, material. I measured data/raw/ myself: 234 files / 1,443,366,993 B = 1.44 GB, and broke it down by top dir (ecfr 50 files / 824,298,523 B; cfr 110 / 349,679,334 B; fr 74 / 269,389,136 B) and by extension (191 .xml files = 1,443,182,152 B; 43 .json = 184,841 B). I tried three refutations and all three failed. (1) 'source XML only' does not rescue it - every byte in data/raw/ except 0.18 MB of JSON is XML, so the XML total is 1,443 MB, not 824 MB. (2) It is not a dated correction quoting an old figure on purpose: `grep -n 824 SUBMISSION.md` returns exactly one hit, line 53, with no correction, no commit pin and no evidence path anywhere in the paragraph. (3) It is not a differently-formatted match - the repo's own artifacts give the opposite number: REPRODUCE.md's table totals `| **total** | **234** | **1,443,366,993 = 1.44 GB** |` and then says verbatim 'The **824 MB** figure qu
- **refuter ran:** `python -c "import os,collections; d=collections.Counter(); c=collections.Counter(); [ (d.__setitem__(os.path.splitext(f)[1].lower(), d[os.path.splitext(f)[1].lower()]+os.path.getsize(os.path.join(r,f))), c.update([os.path.splitext(f)[1].lower()])) for r,_,fs in os.walk('data/raw') for f in fs ]; print(d,c)"  +  sed -n '255,290p' REPRODUCE.md  +  sed -n '185,200p' PROGRESS.md  +  sed -n '70,80p' TH`

**SURVIVED · line 109 · material · number-path-disagrees**

> `QUESTIONS.md` holds 31 entries including our own retractions, a duplicated-run

- **problem:** The cited file does not contain 31 entries. At `e01fdfd` - the very commit that introduced this sentence, whose own message reads "Q29 closed, Q30 through Q35 raised" - QUESTIONS.md carried 35 top-level `## Q<n>` entries (Q1-Q35). The parent commit had 29 and the line then said 29; six were added and the count was bumped by four instead of six. In the current working tree QUESTIONS.md carries 38 (Q1-Q38). 31 was never true at any commit.
- **auditor checked:** git show e01fdfd^:QUESTIONS.md | grep -c -E '^## Q[0-9]+' -> 29 ; git show e01fdfd:QUESTIONS.md | grep -c -E '^## Q[0-9]+' -> 35 ; git show HEAD:QUESTIONS.md | grep -c -E '^## Q[0-9]+' -> 35 ; grep -c -E '^#+ *Q[0-9]+' QUESTIONS.md (working tree) -> 39 headings, of which 38 are top-level Q1-Q38 plus one 'Q24 RETRACTED' sub-heading. git show e01fdfd -- SUBMISSION.md | grep '^[+-].*entries' -> '-`QUESTIONS.md` holds 29 entries' / '+`QUESTIONS.md` holds 31 entries'.
- **refuter (could not kill it):** SURVIVES, material. I walked the whole history of QUESTIONS.md, not just the two commits the auditor named, to look for a commit where 31 was true. The distinct top-level `## Q<n>` counts across every commit that touched the file are 7, 8, 10, 13, 14, 17, 18, 19, 20, 21, 23, 24, 26, 29, 35 - the count jumps 29 -> 35 in one commit (e01fdfd) and 31 never occurs. That same commit e01fdfd is the one that edited this very line: `git show e01fdfd -- SUBMISSION.md` shows '-`QUESTIONS.md` holds 29 entries' / '+`QUESTIONS.md` holds 31 entries', i.e. six entries were added (Q30-Q35, per its own commit message) and the count was bumped by two. Working tree now holds 38 (Q1-Q38, unique ids confirmed by `grep -oE '^#+ *Q[0-9]+' | sort -u | wc -l` = 38); HEAD holds 35. The sentence pins no commit and offers no alternative unit - it says 'including our own retractions', so it is not a count net of the 
- **refuter ran:** `for c in $(git log --format=%h -- QUESTIONS.md); do echo "$c $(git show $c:QUESTIONS.md | grep -c -E '^## Q[0-9]+')"; done | sort -k2 -n  ;  git show e01fdfd -- SUBMISSION.md | grep -E '^[+-].*QUESTIONS.md. holds'  ;  grep -c -E '^## Q[0-9]+' QUESTIONS.md`

**SURVIVED · line 21 · cosmetic · number-path-disagrees**

> 34 JSONL trajectories

- **problem:** Stale against the current tree. `docs/trajectories/` holds 34 tracked .jsonl files at `e01fdfd` but 35 at HEAD - commit 810e2b1 added `docs/trajectories/build/CH-11.jsonl`, and 810e2b1 is NEWER than SUBMISSION.md's last edit (8d22305). Line 63 repeats the same figure as "34 files, complete, nothing sampled". Unlike rows 17-18, neither line pins a commit, so the count reads as current and is off by one.
- **auditor checked:** git ls-tree -r --name-only e01fdfd -- docs/trajectories | grep -c '\.jsonl$' -> 34 ; git ls-files docs/trajectories | grep -c '\.jsonl$' -> 35 ; diff of the two lists -> only addition is 'docs/trajectories/build/CH-11.jsonl' ; git log --oneline | head -2 -> 810e2b1 (CH-11 session transcript) is above 8d22305 (last SUBMISSION.md commit).
- **refuter (could not kill it):** SURVIVES, cosmetic/staleness only. Counts confirmed: 34 .jsonl tracked at e01fdfd, 35 at HEAD and in `git ls-files`; the only difference is docs/trajectories/build/CH-11.jsonl, added by 810e2b1, which is newer than 8d22305, the last commit to touch SUBMISSION.md. I tried the strongest refutation available - that the new file is a different category (a build-session transcript) and so not 'one JSONL per agent run' - and it fails: docs/trajectories/build/ already holds nine other build transcripts (CH-00, CH-01, CH-02, CH-06, CH-14a, NIGHT-RUN-CHECKPOINT, NIGHT-RUN-FINAL, SPEC-FIX-1, SPEC-FIX-2) that are inside the 34, so CH-11.jsonl belongs to the same class already counted. Neither line 21 nor line 63 pins a commit (unlike rows 1-2, which say 'at e01fdfd'), so both read as current and are off by one. docs/trajectories/README.md states no count, so nothing else in the tree disambiguates. 
- **refuter ran:** `git ls-tree -r --name-only e01fdfd -- docs/trajectories | grep -c '\.jsonl$'  ;  git ls-tree -r --name-only HEAD -- docs/trajectories | grep -c '\.jsonl$'  ;  diff <(git ls-tree -r --name-only e01fdfd -- docs/trajectories | grep '\.jsonl$') <(git ls-tree -r --name-only HEAD -- docs/trajectories | grep '\.jsonl$')  ;  git log --oneline -3 -- SUBMISSION.md  ;  git ls-files docs/trajectories/build`

**SURVIVED · line 33 · cosmetic · number-without-path**

> The repository is 63.62 MB uncompressed. That number is **not** the constraint and was

- **problem:** No evidence path is cited for 63.62 MB, and the label is imprecise. The figure recomputes exactly as the TRACKED-TREE byte total at `e01fdfd` (63,615,283 B = 63.62 MB), not as "the repository" (which includes `.git`, and on disk also `data/raw/`). The nearest published artifact, `docs/evidence/ch14-size/inventory.md:7`, reports 61,696,512 B at an earlier commit and calls it "tracked bytes"; REPRODUCE.md:21 likewise says "the tracked tree measured 61,696,512 B". The derived "deflates 6x" claim on the next line does hold (63,615,283 / 10,662,339 = 5.97x).
- **auditor checked:** git ls-tree -r -l e01fdfd | awk '{s+=$4} END {...}' -> 'e01fdfd tracked bytes: 63615283 = 63.62 MB (dec) = 60.67 MiB'. Grep tool for '63\.62' across the repo -> only SUBMISSION.md:33 and a CH-11 trajectory line; no docs/evidence/ file carries it. sed -n '1,30p' docs/evidence/ch14-size/inventory.md -> 'tracked bytes : **61,696,512 B = 61.70 MB = 58.84 MiB**'.
- **refuter (could not kill it):** SURVIVES, cosmetic. The 'path cited one sentence earlier' exception does not apply. The preceding sentence does cite `docs/evidence/ch14-size/inventory.md`, but it cites it for the ARCHIVE figure (10,182,500 B), and that artifact's tracked-tree line reads '**61,696,512 B = 61.70 MB = 58.84 MiB**' at an earlier commit bc99ef4 - a different number for a different quantity. A repo-wide grep for '63.62|63,615|63615' over *.md returns only SUBMISSION.md:33 itself, so no evidence file carries the figure in any formatting. I did find the value is arithmetically right and slightly better-founded than the auditor said - tracked bytes are 63,615,283 (63.62 MB) at e01fdfd AND 63,616,784 (63.62 MB) at 8d22305, SUBMISSION.md's own last-edit commit - but that only makes it accurate-when-written, not sourced. The label is also loose: 63.62 MB is the tracked tree, whereas 'the repository' on disk additi
- **refuter ran:** `for c in e01fdfd 8d22305 HEAD; do git ls-tree -r -l $c | awk -v C=$c '{s+=$4} END {printf "%s %d = %.2f MB\n", C, s, s/1e6}'; done  ;  grep -rn --include='*.md' -E '63\.62|63,615|63615' .  ;  sed -n '1,20p' docs/evidence/ch14-size/inventory.md  ;  sed -n '28,40p' SUBMISSION.md`

**Could not check — stated rather than dropped:**

- Line 4 / 17 - that https://github.com/chinmoypaul8897/instruction-that-wont-execute is live and public. No network calls permitted. I only confirmed it matches `git remote -v` (origin fetch/push = the same URL + .git).
- Line 19 / 50 / 89 / 138 - the pytest pass/skip counts (316/26 clone, 314/28 extraction) were NOT re-executed; I am read-only and did not run the suite. They match docs/evidence/ch14-clean-clone/rehearsal.txt:56 and :77 and PROGRESS.md:76 / :81 exactly, and `git diff --name-only 263ed29 HEAD -- tests src` is EMPTY, so no test or source file changed since the rehearsal was run. 13 test modules confirmed by `ls tests/test_*.py | wc -l` -> 13 (also 13 at e01fdfd).
- Line 42 / 151 - "`.githooks/pre-commit` now refuses any commit whose archive exceeds 45 MB, and fails closed if it cannot measure". I read the source (MAX_ARCHIVE_BYTES = 45_000_000 at line 78, MAX_TRACKED = 400 at line 73, fail-closed branches at lines 129-152 and 196) but did not execute the hook.
- Line 22 / 143 - the demo video URL is stated as TBD/not yet recorded. There is an untracked docs/video-script.md in the working tree; nothing numeric to verify.
- Line 30 - "CH-14a measured 10,613,737 B". No path is cited on that line, but the figure appears verbatim in docs/evidence/ch14-clean-clone/rehearsal.txt:32 and REPRODUCE.md:21, so it traces; I could not re-derive it because the CH-14a commit's archive was not rebuilt.
- Line 92 - "across all 462 text blobs of all 84 commits". Matches docs/evidence/secret-scan/scan.txt:18/:10/:89 exactly and the path is cited, but HEAD now has 93 commits, so the word "all" is point-in-time. scan.txt:109 itself discloses this ("Point-in-time result for the commit named at the top"), so I did not raise it as a finding.

### `THIRD-PARTY.md` — 137 lines read, 4 findings

**SURVIVED · line 74 · material · number-path-disagrees**

> Measured on the build machine at CH-11 and transcribed into `PROGRESS.md`: **1,443,366,993 B across 234 files** — 824,298,523 B of eCFR titles, 349,679,334 B of CFR annual-edition volumes and 269,389,136 B of Federal Register issues.

- **problem:** The cited path PROGRESS.md does not contain any of these five numbers. PROGRESS.md's only mention of the raw-corpus size is the rounded "1.44 GB" in the CH-11 audit-findings table (line 194); the file counts and exact byte totals appear nowhere in it, including nowhere in the CH-11 entry that the sentence points at. The numbers themselves are correct and self-consistent, but they live in REPRODUCE.md lines 269-272, which is cited only later and loosely ("See `REPRODUCE.md`"). A reader following the stated citation finds nothing.
- **auditor checked:** grep -n "1,443,366,993\|234 files\|1.44 GB" PROGRESS.md -> single hit, line 194: "| `data/raw/` is *\"~824 MB\"* | **1.44 GB**. 824 MB is the eCFR titles alone |". grep -n "234" PROGRESS.md -> no output. grep -n "443,366\|824,29\|349,679\|269,389" PROGRESS.md -> no output. sed -n '14,120p' PROGRESS.md | grep -n "raw|GB|bytes|824|1.44|234" -> no size line in the CH-11 verification block. sed -n '258,280p' REPRODUCE.md -> the table with 50/824,298,523, 110/349,679,334, 74/269,389,136, total 234/1,443,366,993. python -c "print(824298523+349679334+269389136); print(50+110+74)" -> 1443366993 / 234 
- **refuter (could not kill it):** SURVIVES, but severity is overstated. I could not kill the factual core: PROGRESS.md (1,749 lines) contains none of the five figures in ANY format - not '1,443,366,993' and not '1443366993', not '234', not the three component byte totals - and its CH-11 entry runs lines 14-253 with the corpus size appearing only as the rounded '1.44 GB' in the audit-findings table at line 194. So the explicit citation is wrong for the exact digits, and REPRODUCE.md:265 repeats the identical claim ('transcribed into PROGRESS.md's CH-11 entry'), making it a duplicated error rather than a slip. Two mitigations the auditor undersold: (a) the same paragraph's closing sentence is 'See REPRODUCE.md', and the table at REPRODUCE.md:269-272 does hold every figure, so a reader is not stranded; (b) the measurement IS in PROGRESS.md in rounded form plus the 824 MB gloss, and PROGRESS.md Q30 (line 207) explains why it
- **refuter ran:** `grep -n "1,443,366,993\|234 files\|1.44 GB\|824,298,523\|349,679,334\|269,389,136" PROGRESS.md ; grep -n "1443366993\|824298523\|349679334\|269389136\|234" PROGRESS.md ; sed -n '54,120p;180,210p' PROGRESS.md ; sed -n '255,285p' REPRODUCE.md ; python -c "import os;[print(s,sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk('data/raw/'+s) for f in fs)) for s in ['ecfr','cfr','fr']]"`

**SURVIVED · line 100 · material · other**

> committed verbatim as issued — with **one exception, named rather than glossed: `prompts/CH-11.md`, the prompt for the session that wrote this file, is on disk and untracked.**

- **problem:** There are now two untracked prompt files, not one. `prompts/CH-11c.md` is also on disk and untracked, and CH-11c is a real session (it authored the dated corrections at QUESTIONS.md line 1148 and AI-USE.md line 235, and wrote docs/evidence/ch11c-sweep/). The claim was true when THIRD-PARTY.md was committed (single commit 14d243a, CH-11) and has since gone stale, but as it now ships it understates the disclosure gap in the one file whose whole job is completeness of disclosure. AI-USE.md also carries no row naming either exception (grep for "untracked"/"not committed" in AI-USE.md returns nothing).
- **auditor checked:** git status --porcelain prompts/ -> "?? prompts/CH-11.md" AND "?? prompts/CH-11c.md". git ls-files prompts/ | wc -l -> 12 (10 top-level + 2 under design/); ls prompts/*.md | wc -l -> 12 top-level on disk. git ls-files prompts/CH-11.md -> empty. git log --oneline -- THIRD-PARTY.md -> one commit, 14d243a (CH-11). grep -n "CH-11c" AI-USE.md -> only lines 235-236 (the secret-scan correction), no prompt-tracking note.
- **refuter (could not kill it):** SURVIVES. I tried three refutation routes and all failed. (1) 'Dated record whose old text should survive': THIRD-PARTY.md is not a dated log - its header dates only the licence readings ('read out of the installed package's own metadata in the CH-11 verification venv'), and this paragraph carries no as-of stamp; sibling files that WERE stale got dated corrections at CH-11c (AI-USE.md:235, PROVENANCE.md:96, CHANGELOG.md:28) while this one did not. (2) 'Disclosed one sentence away': grep -rn 'CH-11c.md' across all tracked .md files returns only QUESTIONS.md:2501/2553/2561 and docs/evidence/ch11c-sweep/progress-CH-11c.md:112, every one of them quoting the prompt's CONTENT; nothing anywhere states it is untracked, and 'untracked' does not appear in AI-USE.md at all. (3) 'Not a real session': CH-11c authored the dated corrections at QUESTIONS.md:1148 and AI-USE.md:235-236, the whole ch11c-sw
- **refuter ran:** `git status --porcelain prompts/ ; git ls-files prompts/ ; ls prompts/ ; git log --oneline -- THIRD-PARTY.md ; grep -rn "CH-11c.md" --include="*.md" . ; grep -n "untracked\|not committed" AI-USE.md ; sed -n '2452,2460p' QUESTIONS.md`

**SURVIVED · line 89 · cosmetic · other**

> `claude-sonnet-5` calls exist in the ledger. They belong to the **model-sensitivity check, which is WITHDRAWN** as a harness defect

- **problem:** Not all of them do. The ledger holds 84 claude-sonnet-5 rows: 40 B0-agent-sonnet, 40 B0-sonnet, and 4 in arm `probe-model-id`. The four probe rows are not part of the model-sensitivity check. The sentence is an unqualified all-quantifier over the sonnet rows and is wrong for 4 of 84. (The substantive point is right: sonnet ran no evaluation arm, and the sensitivity subset is withdrawn.)
- **auditor checked:** python over docs/evidence/runs/cost_ledger.csv, Counter((model,arm)) -> claude-sonnet-5: B0-agent-sonnet 40, B0-sonnet 40, probe-model-id 4 (84 sonnet rows total; every evaluation arm is claude-haiku-4-5-20251001). Withdrawal figure separately confirmed: python over docs/evidence/checkpoint/withdrawn/B0-agent-sonnet-rep1.json -> n_items 20, Counter({'': 13, 'WILL_EXECUTE': 7}), i.e. exactly "13 of 20 ... came back empty".
- **refuter (could not kill it):** SURVIVES, and it is the best-supported of the four because the project has already ruled on exactly this wording elsewhere. My own Counter over the 2,107-row ledger reproduces the ground truth: claude-sonnet-5 appears on 84 rows - B0-agent-sonnet 40, B0-sonnet 40, probe-model-id 4. The probe is not the sensitivity check: it is the model-id pin verification from Q1 (artifacts at docs/evidence/ch03-model-id/model-id-probe.txt, and the ten probe run files - 6 haiku, 4 sonnet - are itemised at docs/evidence/ch14-size/selection-applied.md:34-43). I tried to refute by reading the probe rows as part of the sensitivity work and by arguing the preceding sentence about alias-pinning covers them; both fail, because QUESTIONS.md:2543 states in this project's own words that the 4 probe rows are 'a third category the card did not name', and PROVENANCE.md:93 was rewritten at CH-11c to read '...plus 4 r
- **refuter ran:** `python -c "import csv,collections;rows=list(csv.DictReader(open('docs/evidence/runs/cost_ledger.csv',encoding='utf-8')));c=collections.Counter((r['model'],r['arm']) for r in rows);print(len(rows));[print(v,k) for k,v in sorted(c.items())]" ; sed -n '90,115p' PROVENANCE.md ; sed -n '2505,2545p' QUESTIONS.md ; grep -rn "probe-model-id" --include="*.md" .`

**SURVIVED · line 75 · cosmetic · number-path-disagrees**

> 824,298,523 B of eCFR titles

- **problem:** The generating artifact attributes 824,298,523 B to "49 title XMLs plus the govinfo index" across 50 files, not to titles alone. This matters here because the very next sentence contrasts this number with CONTEXT.md §8's "49 titles, 824,289,052 B"; glossing 824,298,523 as "eCFR titles" makes the two figures look like the same quantity with different digits, when the 9,471 B delta is the index file the first number includes and the second does not.
- **auditor checked:** sed -n '269p' REPRODUCE.md -> "| `ecfr/` — 49 title XMLs plus the govinfo index | 50 | 824,298,523 |". grep -n "824,289,052\|49 titles" CONTEXT.md -> line 172, inside §8 (grep -n '^## ' CONTEXT.md puts §8 at line 142 and §9 at 277). 824298523-824289052 = 9471.
- **refuter (could not kill it):** SURVIVES, and I upgraded it from inference to measurement. The auditor asserted the 9,471 B delta is the govinfo index; data/raw/ is present on this machine, so I measured it directly instead of trusting the claim: data/raw/ecfr/ holds 50 files totalling 824,298,523 B; the 49 ECFR-title*.xml files sum to 824,289,052 B - bit-identical to CONTEXT.md §8's '49 titles, 824,289,052 B', delta 0 - and the 50th file, _govinfo_index.json, is exactly 9,471 B. So 'eCFR titles' as a label for 824,298,523 is strictly wrong: that number is titles PLUS the index, and REPRODUCE.md:269 gets it right with 'ecfr/ - 49 title XMLs plus the govinfo index | 50 | 824,298,523'. The refutation I attempted - that 'eCFR titles' is a harmless bucket name for the ecfr/ directory, both digits being correct - does not hold up because of what the very next sentence does with it: it presents CONTEXT.md's 824,289,052 as a 
- **refuter ran:** `python -c "import os;d='data/raw/ecfr';fs=sorted(os.listdir(d));t=[f for f in fs if f.lower().startswith('ecfr-title')];print(len(fs),sum(os.path.getsize(os.path.join(d,f)) for f in fs));print(len(t),sum(os.path.getsize(os.path.join(d,f)) for f in t));[print('OTHER:',f,os.path.getsize(os.path.join(d,f))) for f in fs if f not in t]" ; sed -n '269p' REPRODUCE.md ; sed -n '165,180p' CONTEXT.md`

**Could not check — stated rather than dropped:**

- The licence strings are said to have been "read out of the installed package's own metadata in the CH-11 verification venv" — that venv is not in the repository, so I re-read the same metadata from the interpreter on this machine instead. Every licence claim matched exactly (pytest License-Expression: MIT; iniconfig License-Expression: MIT; packaging License-Expression: Apache-2.0 OR BSD-2-Clause; pluggy License: MIT; Pygments License-Expression: BSD-2-Clause; colorama dist-info licenses/LICENSE.txt is BSD with exactly three bullet conditions). But this machine has packaging 26.2 and Pygments 2.20.0, not the 26.3 / 2.21.0 the table states; those two versions are corroborated only by docs/evidence/ch14-clean-clone/rehearsal.txt line 9 and requirements.txt lines 32-33, never by a dist-info I could open. Version claims traced to a committed artifact, not to an installed package.
- "CPython 3.12.2, under the PSF License Agreement" — the version is confirmed (python -c sys.version -> 3.12.2; rehearsal.txt line 8; REPRODUCE.md line 18), but the PSF licence text itself is not an artifact in this repo.
- "17 U.S.C. §105 ... The corpus is in the public domain" — a legal proposition with no repository artifact behind it. Not checkable here.
- "used under Anthropic's commercial terms" (lines 82 and 96) — no artifact in the repo states the contractual terms; nothing to check it against.
- The two external citations — "Prior et al., NLLP@ACL 2025" and "ATLAS, arXiv 2509.18400" — exist and are quoted identically in CONTEXT.md §12 (lines 318-320), but confirming the papers themselves would need a network call, which I did not make. `cfpb/regulations-parser` likewise named only, not fetched.
- Line 41's "three clauses" for colorama is verified from the installed LICENSE.txt on this machine, not from the CH-11 venv copy the header claims as the source — same caveat as the version numbers above.

---

## Completeness critic — what the sweep missed

Asked: which tracked shipping files were skipped, do the swept files contradict each
other on any shared figure, and is any number in them traceable to no path at all.

```

COMPLETENESS CRITIC — WHAT THE SWEEP MISSED
Repo: c:/Users/chinm/micro1 engineering challenge   HEAD: a0432e7
All findings below were re-derived by command in this session. Read-only; nothing edited.


================================================================================
CATEGORY 1 — TRACKED SHIPPING-SURFACE FILES THE SWEEP SKIPPED
================================================================================
Command:
  git ls-files | grep -v '^docs/trajectories/' | grep -v '^context/' | grep '\.md$'
Returns 61 tracked .md files. The sweep covered 10. FIFTY-ONE WERE SKIPPED.

Top-level tracked *.md NOT swept (a judge opens these first):
  CLAUDE.md  CONTEXT.md  GOOD.md  PROCESS.md  PROGRESS.md  plan.md
Also skipped and judge-facing: agents/*.md (5 files — SUBMISSION.md:21 lists agents/
as deliverable-5 evidence), docs/reviews/*.md (3 — README.md:429 cites them by name),
docs/evidence/**.md (22), prompts/*.md (13), docs/trajectories/README.md +
docs/trajectories/build/README.md.

FOUR of the skipped files carry defects that are exactly what the sweep was looking for:

1.1  PROGRESS.md:397 STILL CARRIES THE STALE SECRET-SCAN FIGURE.
     sed -n '396,398p' PROGRESS.md  ->
       "**VERDICT: PASS, 0 findings** over 450 text blobs of 81 commits and 37.7 MB of
        trajectories."
     Ground truth / docs/evidence/secret-scan/scan.txt:89 = "462 text blobs across 84
     commits, 36 trajectory files, 39,363,213 bytes". STATUS.md and AI-USE.md were
     corrected to 462/84; PROGRESS.md was not. QUESTIONS.md:2564 predicted this exact
     outcome ("a reader who greps for 450 will find it after STATUS.md and AI-USE.md
     have been corrected... Flagged, not edited"). It is a tracked, top-level,
     1000+-line file that ships in the zip. The sweep's fence let it through.

1.2  THE "COMPUTE-MATCHED" LABEL SURVIVES IN THREE SHIPPING FILES OUTSIDE THE TEN.
     The sweep checked surviving compute-matched labels only on the ten. Verified live:
       CONTEXT.md:63       "| **B0′** | compute-matched control | B0-agent at A1's exact
                            token budget, spent on best-of-3 self-consistency ... |"
       src/arms.py:292     '"""**B0-prime** - the COMPUTE-MATCHED CONTROL. `CONTEXT.md`
                            section 4, `plan.md` CH-08.'
       prompts/CH-06.md:139 "- **Name `B0′` explicitly** — the compute-matched control:
                            B0-agent at A1's token budget..."
     CONTEXT.md is the spec of record (CLAUDE.md: "THIS FILE IS LAW"), top-level, and
     ships. Ground truth: B0prime = 1,377,402 input tokens vs A1's 4,006,662 (34%) —
     not token-matched. This is logged as QUESTIONS.md Q36 (architect-only) so it is
     disclosed, but the label is still live in three files a judge reads.

1.3  agents/B0-agent.md STATES n = 76 WITH NO STALENESS NOTE.
     sed -n '25,26p;92p' agents/B0-agent.md  ->
       line 25-26: "8 of the 76 items would have contained it in their unstripped text."
       line 92:    "The 76 items total 847,851 characters"
     The shipped eval set is 82 items / 41 pairs (data/evalset/items.jsonl).
     GOOD.md is stale the same way but reconciles it in its own addendum
     (GOOD.md:188-215, with an explicit "| n | 76 | **82** |" table at line 203).
     agents/ has NO equivalent note — grep -n -iE '82|superseded|stale' agents/*.md
     returns no reconciliation. So the one deliverable-1 artifact a judge reads to see
     what the baseline agent actually was publishes a corpus size that is wrong by 6
     items and unflagged.

1.4  plan.md:94 still specifies the claude-sonnet-5 model-sensitivity check as a live
     arm ("Re-run B0 and B0-agent on `claude-sonnet-5` over a 20-item subset (~$2)")
     with no note that it was WITHDRAWN as a harness defect. Lower severity — plan.md
     is a plan — but it is top-level and tracked, and the withdrawal is the single most
     load-bearing model fact in the ground truth.

Does it matter? Yes for 1.1-1.3. A judge grepping "450" or "compute-matched" or "76"
lands on a tracked file that disagrees with the corrected ones. The sweep's file list,
not the sweep's method, is what let these through.


================================================================================
CATEGORY 2 — CONTRADICTIONS BETWEEN THE TEN SWEPT FILES ON A SHARED FIGURE
================================================================================
Commands: git ls-files '*.md' scoped grep of each headline number across the ten
(0.7195 0.6585 11.6323 0.4756 0.5610 0.6463 0.0059 0.4244 0.5340 462 84 82 41 22).

ON THE ARM ACCURACIES, THE p-VALUES, THE SPEND, AND 462/84: NO CONTRADICTION FOUND.
All ten agree — 0.7195 / 0.6585 / 0.6585 / 0.5610 / 0.6463 / 0.4756, +18.3 pp,
p=0.0059, +6.1 pp, p=0.4244, USD 11.6323, 462 blobs / 84 commits, 22 of 82 votes.
The Q33 "26 of 82" correction has landed everywhere (CHANGELOG.md:26 and README.md:202
both read 22 with the votes-file path beside them). Per-arm tokens in
REPRODUCE.md:226-231 match the ground-truth ledger row-for-row and the ten rows sum to
2,107 calls and USD 11.6323.

But TWO shared figures DO contradict:

2.1  THE UNCOMPRESSED REPOSITORY SIZE — SUBMISSION.md vs REPRODUCE.md.
       SUBMISSION.md:33  "The repository is 63.62 MB uncompressed."
       REPRODUCE.md:21   "the tracked tree measured **61,696,512 B = 61.70 MB**
                          (`docs/evidence/ch14-size/inventory.md`)"
     git grep -n -F '63.62' -- . ':!docs/trajectories'  ->  ONE hit, SUBMISSION.md:33.
     git grep -n -E '61\.7[0-9]|61,696,512'             ->  inventory.md:7, QUESTIONS
     1812/1904/1925/1930/1946, PROGRESS 261/268/303, REPRODUCE:21.
     Every artifact says 61.70 MB. 63.62 exists nowhere else in the repository.

2.2  THE UPLOADED ZIP SIZE — STATUS.md/AI-USE.md vs everything else, AND against the
     source they cite.
       STATUS.md:39   "THE 50 MB BLOCKER WAS NEVER A BLOCKER: the zip is 10.24 MB,
                       4.9× under cap **(Q27)**"
       AI-USE.md:255  "The 50 MB cap is on the uploaded zip; the zip is 10.24 MB."
     The cited source, QUESTIONS.md Q27, line 1813, says:
       "git archive --format=zip HEAD   10,182,500 B  =  10.18 MB  =  9.71 MiB"
     and so do docs/evidence/ch14-size/inventory.md:8 and selection-rule.md:77.
     SUBMISSION.md:28-31 reconciles three figures — 10.66 (CH-11, e01fdfd), 10.61
     (CH-14a rehearsal), 10.18 (inventory) — and 10.24 IS NOT AMONG THEM.
     git grep -n -F '10.24' -- . ':!docs/trajectories'  ->  STATUS.md:39, AI-USE.md:255
     and nothing else. Two swept files state a zip size that contradicts the very
     question number they cite for it.


================================================================================
CATEGORY 3 — ASSERTIONS THE GROUND TRUTH CONTRADICTS
================================================================================

3.1  PROVENANCE.md:92 — "every evaluation arm, temperature 0". FALSE.
     sed -n '92p' PROVENANCE.md ->
       "| Anthropic API — `claude-haiku-4-5-20251001` | commercial, per terms |
         every evaluation arm, temperature 0 |"
     B0prime is an evaluation arm and runs at temperature 1.0:
       REPRODUCE.md:176 "**Temperature** | **0** on every arm **except `B0prime`**,
                          which runs at **1.0**."
       README.md:217    "B0′ is also **the only arm in the packet not at temperature 0**"
       QUESTIONS.md Q22 (line 1385) is titled on exactly this point.
     The row is self-contradicting inside its own section: PROVENANCE.md:103-104, ten
     lines below, lists `B0prime` among the evaluation arms it is describing.
     The sweep checked the MODEL NAME on this row (correct) and did not check the
     temperature clause sharing the cell.

3.2  THIRD-PARTY.md:84 — "Temperature 0 on every arm in the primary comparison."
     Softer version of the same defect. B0prime appears in the primary arm matrix
     (README.md:231, CHANGELOG.md:26) at temperature 1.0. Defensible only if "primary
     comparison" is read as A1-vs-B0-agent alone, which the file never says.

3.3  SUBMISSION.md:21 — "34 JSONL trajectories". Stale by one, and unlabelled.
       git ls-tree -r --name-only e01fdfd -- docs/trajectories/ | grep -c '\.jsonl$' -> 34
       git ls-files 'docs/trajectories/*.jsonl' | wc -l                              -> 35
     Row 5 is the only deliverable row in that table with NO commit label, while rows 1
     and 2 carry "at `e01fdfd`". A judge counting at HEAD gets 35.
     (Verified NOT defects: SUBMISSION.md:15 "323 tracked files, 90 commits at e01fdfd"
     reproduces exactly — git ls-tree -r --name-only e01fdfd | wc -l = 323,
     git rev-list --count e01fdfd = 90. "13 test modules" = 13. "39.4 MB of
     trajectories" = scan.txt's 39,363,213 B.)

3.4  CHECKED AND CLEARED — I do not report these, having verified them:
     - PROVENANCE.md:93 cites "QUESTIONS.md Q19" for the withdrawn sonnet subset. Q19's
       heading (line 983) is about the CH-03 escalation, so this LOOKS like a wrong
       cross-reference. It is not: the next heading is Q20 at line 1229, and the
       withdrawal ruling sits inside Q19 at lines 1110-1142. Correct, just non-obvious.
     - AI-USE.md:317 "every evaluation arm, 3 reps, temperature 0" is inside the
       NIGHT-RUN session entry (heading at line 307) whose scope is B0 + B0-agent +
       probe = 474+474+3 = 951, matching its own call count. Session-scoped and correct.
     - PROVENANCE.md:104 "80 rows of the withdrawn sensitivity subset plus 4 rows of
       probe-model-id" = 84, matching the ground-truth ledger exactly.
     - No file in the ten claims any review gate passed. README.md:423 states "Six
       chunks carry a gate. None of them passed it." STATUS.md rows read reviewed-FAIL /
       built / ESCALATED throughout. The only "GREEN" is the CHECKPOINT branch decision,
       which is not a review gate. NONE FOUND in this sub-category.


================================================================================
CATEGORY 4 — NUMBERS WITH NO PATH ANYWHERE IN THE REPO
================================================================================
Two, both already named above because they are also contradictions:
  63.62  SUBMISSION.md:33   — one occurrence in the entire repository, no source.
  10.24  STATUS.md:39, AI-USE.md:255 — no source; cited to Q27, which says 10.18.

AND THE LARGER FINDING THE SWEEP'S METHOD COULD NOT SEE — CITED PATHS THAT DO NOT SHIP.
The sweep checked "whether that path contains the number". It evidently resolved paths
against the WORKING TREE. The submission is built with `git archive --format=zip HEAD`
(SUBMISSION.md:28,47; REPRODUCE.md:142), so untracked paths are absent from what the
judge receives. Command:
  grep -ohE '(docs|src|tests|data|agents|prompts|tools)/[A-Za-z0-9._/-]+' <the ten>
    | sort -u   (148 distinct paths)   then tested each against `git ls-files`
Result — cited but NOT TRACKED:

  docs/evidence/ch11c-sweep/                     UNTRACKED, on disk
  docs/evidence/ch11c-sweep/ch11c-verify.txt     UNTRACKED, on disk
  docs/evidence/ch11c-sweep/progress-CH-11c.md   UNTRACKED, on disk
  prompts/CH-11.md                               UNTRACKED, on disk
  prompts/CH-11c.md                              UNTRACKED, on disk
  docs/evidence/ch09-removed/human-time-worksheet.csv  UNTRACKED, on disk

Confirmation that they do not ship:
  git archive --format=tar HEAD | tar -t | grep -cE 'ch11c-sweep|prompts/CH-11'  ->  0
On-disk contents of the missing directory (5 files, ~75 KB): ch11c-sweep.txt,
ch11c-verify.txt, ch11c_sweep.py, ch11c_verify.py, progress-CH-11c.md.

Who cites it:
  PROVENANCE.md:106  "Re-derivable at `docs/evidence/ch11c-sweep/`."   <- the generating
                     evidence for the Q35 model-ledger correction, the single biggest
                     factual retraction in the packet
  AI-USE.md:243      "re-derivation at `docs/evidence/ch11c-sweep/`."  <- the 462/84 fix
  QUESTIONS.md:2456, 2506, 2561
  QUESTIONS.md:2561  claims it "**ships** at docs/evidence/ch11c-sweep/progress-CH-11c.md"
                     — it does not ship.
This is a hard-rule-14 breach ("ships its generating script AND its committed output
under docs/evidence/"): the two corrections the sweep session made are both defended by
an evidence directory that is invisible to anyone who clones or unzips. One
`git add docs/evidence/ch11c-sweep/` closes it.

Related disclosure defect: THIRD-PARTY.md:101-103 names the untracked prompt as a single
exception — "with **one exception, named rather than glossed**: `prompts/CH-11.md` ...
is on disk and untracked." There are now TWO. prompts/CH-11c.md is equally untracked and
is disclosed NOWHERE:
  git grep -n -i 'CH-11c' -- '*.md' | grep -iE 'untrack|not committed|on disk'  ->  no hit
So THIRD-PARTY.md's "one exception" claim is now false by count.

Minor: QUESTIONS.md:1679 quotes "`docs/evidence/ch09-removed/human-time-worksheet.csv`
— **292 bytes, a blank form**" against a path that is untracked and will not be in the
zip; QUESTIONS.md:1953 records it was "dropped to make room under the 300-file count",
so the absence is disclosed even though the byte count now cites nothing shippable.

BENIGN, checked and cleared (cited-but-absent by design, each declared as such):
  data/raw/ (git-ignored, declared REPRODUCE.md:264, THIRD-PARTY.md:73, SUBMISSION.md:53)
  data/CFR, data/ECFR, data/FR (fragments of govinfo URLs, THIRD-PARTY.md:58)
  docs/about-claude/pricing (fragment of the docs.claude.com URL, AI-USE.md:42)
  docs/evidence/iter-N/ (a template placeholder, CHANGELOG.md:65)
  docs/evidence/ch11-repro/ (a proposal put to the architect, QUESTIONS.md:2206)
  ~/.claude/.../workflows/wf_44b0dd6c-5e5/ (outside the repo, declared QUESTIONS.md:2199)


================================================================================
RANKED
================================================================================
1. docs/evidence/ch11c-sweep/ is untracked and does not ship — PROVENANCE.md:106 and
   AI-USE.md:243 both rest their corrections on it; QUESTIONS.md:2561 claims it ships.
2. PROVENANCE.md:92 "every evaluation arm, temperature 0" — false for B0prime, and
   contradicted by REPRODUCE.md:176 and README.md:217.
3. SUBMISSION.md:33 "63.62 MB" — sourceless and contradicts REPRODUCE.md:21's 61.70 MB.
4. STATUS.md:39 / AI-USE.md:255 "10.24 MB" — sourceless and contradicts the Q27 it cites.
5. PROGRESS.md:397 still reads 450 blobs / 81 commits (skipped file, known, unfixed).
6. CONTEXT.md:63, src/arms.py:292, prompts/CH-06.md:139 still say "compute-matched".
7. agents/B0-agent.md:25,92 publish n = 76 with no staleness note.
8. THIRD-PARTY.md:101 "one exception" is now two — prompts/CH-11c.md is undisclosed.
9. SUBMISSION.md:21 "34 JSONL trajectories" — 35 at HEAD, row carries no commit label.

```

