# -*- coding: utf-8 -*-
"""Generate docs/submission-description.md and assert its own constraints."""
import io

FULL = """The Instruction That Won't Execute

This reads a Federal Register amendatory instruction, resolves it against the Code of Federal Regulations text as it stood on the publication date, and writes the editorial note the National Archives would have to publish if the rule shipped as drafted. It is for a regulations drafter clearing a final rule against a statutory deadline. If an instruction quotes text that is not in the codified section, the Office of the Federal Register cannot execute it, the rule never codifies, and NARA publishes a permanent note saying so. An amendatory instruction carries no evidence of its own executability.

The headline is a null, so it goes first. The agent beats the strongest baseline by 6.1 points, at p = 0.4244, on n = 82. That is not significant. The criterion, committed before any model ran, asked for +8 points, p < 0.05, n of 84, and 0.80 absolute. It is met on none of its four clauses and was not moved.

One result is significant, and it belongs to the corpus, not the agent. Giving the model the point-in-time CFR text moves accuracy from 0.4756 to 0.6585: +18.3 points, exact McNemar p = 0.0059. A reviewer with no shared context reimplemented the scoring from the spec, importing none of my code, and reproduced every checkpoint figure to a delta of 0.000e+00.

The finding worth reading is the composition. Alone, the deterministic resolver scores -9.8 points and the written procedure -1.2. Together they score +6.1, which is 17.1 points above what those two deltas predict. Neither capability helps by itself. The procedure works by repairing a one-way blind spot in the tool, in text the agent reads. That is my answer to which design choices helped.

Checking it takes under a minute, offline, with no API key. Four commands from REPRODUCE.md replay the committed run artifacts and regenerate every headline number byte-identically, measured at 14.42 s and 25.84 s. Rehearsed from the extracted zip, not just a clone.

https://github.com/chinmoypaul8897/instruction-that-wont-execute

On method: built in chunks against a written spec, each gated chunk reviewed by a separate session with zero shared context. Six gated chunks did not pass, and the README's LIMITATIONS section says so. One review found a six-line script, with no model and no CFR text, beating the baseline agent by 17 points on my own eval set. A rigged benchmark, caught before it shipped."""

SHORT = """The Instruction That Won't Execute

US agencies amend the Code of Federal Regulations by publishing instructions that quote the text they edit. If the quoted text is not there, the Office of the Federal Register cannot execute the instruction, the rule never codifies, and the National Archives publishes a permanent note saying so. This agent resolves each instruction against the CFR text as it stood on the publication date and writes that note.

The headline is a null: +6.1 points over the strongest baseline, p = 0.4244, n = 82. The criterion, fixed before any model ran, is met on none of its four clauses and was not moved.

What is significant is the corpus. Point-in-time CFR text is worth +18.3 points, p = 0.0059, reproduced from scratch to zero error by an independent reviewer.

The finding: tool alone -9.8, procedure alone -1.2, the two together +6.1. That is 17.1 points above additive. Neither helps alone; the procedure repairs a blind spot in the tool.

Four offline commands, no API key, replay every number byte-identically.

https://github.com/chinmoypaul8897/instruction-that-wont-execute"""

BANNED = ["delve", "leverage", "robust", "comprehensive", "seamless", "cutting-edge",
          "it's worth noting", "furthermore", "in today's landscape", "we are excited"]

# Title candidates. Lengths are computed, never typed: the first version of this file
# asserted a 90-character string "fits inside 80 characters" because the number was
# written by hand. Hard rule 14 applies to a character count as much as to a p-value.
T1 = "The Instruction That Won't Execute"
T2 = "Will This Amendment Codify?"
T3 = "The Editorial Note NARA Would Publish"
T_BAD = "The Instruction That Won't Execute - a Federal Register agent"
for t in (T1, T2, T3, T_BAD):
    assert len(t) < 80, "title candidate is %d chars: %r" % (len(t), t)

fw, fc = len(FULL.split()), len(FULL)
sw, sc = len(SHORT.split()), len(SHORT)

assert fw < 400, "full version is %d words, must be under 400" % fw
assert sc <= 1200, "cut-down is %d chars, must be <= 1200" % sc
bad = [c for c in FULL + SHORT if ord(c) > 127]
assert not bad, "non-ASCII in a paste block: %r" % sorted(set(bad))
hits = [b for b in BANNED if b in (FULL + SHORT).lower()]
assert not hits, "banned words: %r" % hits
assert "—" not in FULL + SHORT, "em dash in a paste block"
assert not [l for l in (FULL + SHORT).split("\n") if l.startswith("#")], "markdown heading"

DOC = """# `docs/submission-description.md` - the HackerEarth Description field

**Written at CH-14b, 2026-08-31.** The form has four required fields; this file holds
two of them, ready to paste. **CH-11b, the operator's voice pass, still follows** - this
is written to be improved by a person, not preserved.

- **FULL VERSION** below is **{fw} words / {fc} characters**.
- **CUT-DOWN** below is **{sw} words / {sc} characters**, for a field with a small cap.
  The form's character limit has not been reported, which is why both exist.
- Both are **plain text with no markdown** and **pure ASCII** - no headings, no bold, no
  em dashes, no smart quotes. That is deliberate: many form fields render `#` and `**`
  literally, and CH-11's audit found nine U+FFFD written into the README from a cp1252
  terminal. A paste field is exactly where that happens again. The assertions are in
  `docs/evidence/ch14b/gen_description.py` and they fail the build, not a reviewer.

---

## TITLE - three options, under 80 characters each

| | option | chars | |
|---|---|---:|---|
| **1** | `{T1}` | {L1} | **RECOMMENDED.** It is the project's name everywhere else - README, video, repository slug - and a judge scanning a list remembers a name, not a summary. It also states the finding: the whole task is that some instructions do not execute. |
| 2 | `{T2}` | {L2} | The drafter's actual question, in her words. Shorter and more concrete, but it reads as a topic rather than a project, and it matches nothing else in the packet. |
| 3 | `{T3}` | {L3} | Names the output contract, which is the load-bearing design decision. Costs a judge one inference before it means anything. |

**Do not** append an explainer after a dash. `{T_BAD}` is {LBAD}
characters, fits the field, and is worse than option 1 at {L1}: the name is the half
that survives a trim, and the appended half describes a category rather than this.

---

## FULL VERSION - paste this

Paste the contents of the block, not the fence.

```text
{FULL}
```

---

## CUT-DOWN - paste this instead if the field is small

Paste the contents of the block, not the fence.

```text
{SHORT}
```

---

## Every number, and the artifact it was read out of

Hard rule 14. Each was re-read from its artifact while writing this file, not copied
across from the README. Both versions above draw on the same set.

| number as written | value in the artifact | artifact |
|---|---|---|
| beats the strongest baseline by **6.1 points** | `gap_pp = 6.097560975609751` | `docs/evidence/ch06-a1/a1-result.json` -> `comparisons/A1/gap_pp` |
| **p = 0.4244** | `p_value = 0.42435622215270996` | same file -> `comparisons/A1/mcnemar/p_value` |
| **n = 82** | `n = 82` | same file -> top-level `n` |
| criterion **+8 pp, p < 0.05, n of 84, 0.80 absolute**, met on **none of four** | the four-clause table, every row NOT MET | `README.md` section c; `GOOD.md` section 4 |
| **0.4756 to 0.6585** | `b0_accuracy = 0.47560975609756095`, `b0_agent_accuracy = 0.6585365853658537` | `docs/evidence/checkpoint/checkpoint-result.json` -> `as_run` |
| **+18.3 points** | `gap_pp = 18.292682926829272` | same file -> `as_run/gap_pp` |
| **exact McNemar p = 0.0059** | `p_value = 0.005924612283706665`, `test = exact two-sided binomial (McNemar)` | same file -> `as_run/mcnemar` |
| reviewer reproduced **to a delta of 0.000e+00** | *"largest absolute disagreement: 0.000e+00"* over 11 quantities | `docs/reviews/REVIEW_CH-04.md` line 142; script `docs/reviews/ch04-probe/reimplement_from_spec.py` |
| resolver alone **-9.8 points** | `gap_pp = -9.756097560975608` | `docs/evidence/ch06-a1/a1-result.json` -> `comparisons/A1-iter1/gap_pp` |
| procedure alone **-1.2 points** | `gap_pp = -1.2195121951219523` | same file -> `comparisons/A1-minus-tool/gap_pp` |
| **17.1 points above** additive | 0.6585365853658537 - 0.09756097560975608 - 0.012195121951219523 = 0.54878; 0.7195121951219512 - 0.54878 = **0.170732** | the three `gap_pp` values above. The subtraction is done in the open, as `README.md` section c also does it, because no committed script publishes it |
| **14.42 s and 25.84 s** | the per-command table, two runs, fresh venv, network proved unreachable first | `REPRODUCE.md`, section *"Under half a minute for the four commands above"* |
| **six gated chunks** did not pass | the gate table: CH-02, CH-03, CH-04, CH-05, CH-06, CH-08 | `README.md` section g LIMITATIONS -> *"Gate status, plainly"* |
| **six-line script**, no model, no CFR text, beating the baseline agent by **17 points** | F1: *"a six-line script that reads neither the instructions, nor the CFR text, nor a model"*; **0.8158** against **B0-agent 0.6447**, written in the report as *"by 17 pp"* | `docs/reviews/REVIEW_CH-03.md` lines 32-60 |

**Two notes on wording, so that neither line reads as more than it is.**

1. *"beating the baseline agent by 17 points on my own eval set"* describes the
   **withdrawn** n = 76 eval set, before the CH-03 review's fix. That is the point of
   the sentence: the benchmark was rigged and it was caught. On the corrected set the
   same attack scores **0.5610** (`STATUS.md`, CH-03 row). The Description says *"caught
   before it shipped"* and claims nothing about the shipped set.
2. *"Four commands"*, not one. `REPRODUCE.md`'s Tier 1 is four -
   `refetch.py --verify-only`, `analyse_checkpoint.py`, `analyse_a1.py`, `pytest -q`.
   The chunk card asked for *"one command"*; there is no one-command wrapper in the
   tree and none was built, because building one is a source change outside this fence.
   Class B deviation, recorded here and in `PROGRESS.md`.

## The self-check the card asks for

*Does this sound like a person who did the work, or like a summary of it?* The test
applied: **no sentence in either version could be moved to another project.** Every
paragraph names a number, a file or a decision that exists only here. The null is in the
second paragraph rather than the last, which is not where a summary would put it.
Banned-word and em-dash checks are run mechanically over both blocks and they pass.

What a person still has to do to it is read it aloud. That is CH-11b, and it is the
operator's job, not a session's.
""".format(FULL=FULL, SHORT=SHORT, fw=fw, fc=fc, sw=sw, sc=sc,
           T1=T1, T2=T2, T3=T3, T_BAD=T_BAD,
           L1=len(T1), L2=len(T2), L3=len(T3), LBAD=len(T_BAD))

with io.open("docs/submission-description.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(DOC)

print("FULL  : %d words / %d chars" % (fw, fc))
print("SHORT : %d words / %d chars  (cap 1200)" % (sw, sc))
print("banned-word hits: 0   em dashes: 0   markdown headings in paste blocks: 0")
print("non-ASCII in paste blocks: 0")
print("written: docs/submission-description.md")
