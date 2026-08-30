# KILL TEST — CROSSCheck

Your job is to **destroy a hackathon project candidate**, not to improve it or defend it. If it survives you, it earns the build. If it dies, we find out at hour 0 instead of hour 20.

**Deadline context: ~50 hours remain. This session decides what gets built. Be fast, be brutal, be honest.**

---

## 0. The rule that governs this session

> **"Every ball we throw is not supposed to be hit. Some are to test."**

You are not here to validate. Assume the candidate is fatally flawed and find out how. **Praise nothing you would not defend under cross-examination.** If your honest conclusion is that it survives, say so — but only after genuinely trying to kill it with running code.

**Reason nothing you can measure.** Every attack below must be *executed*, with real numbers, not argued. An attack you did not run did not happen.

---

## 1. Read these first

| File | What it is |
|---|---|
| `context/05-FINAL-DECISION.md` | **The candidate under attack. Read this in full first.** The project is called CROSSCheck. |
| `context/06-DIVERGENT-RESEARCH.md` | A 143-candidate search where **all 143 died**. Read §6 "Honest assessment" and §3's kill list. It contains the general law that killed most of them, and it killed a *different* CROSS-based idea — understand why. |
| `context/01-PROBLEM-PDF.md` | The official rubric and rules. |
| `context/04-STRATEGY-BRIEF.md` | What the judges value; the crowded and empty lanes. |

---

## 2. The candidate, in one paragraph

US Customs (CBP) publishes classification rulings: "this product gets this tariff code." It later **revokes** some of them and issues replacements — but the revoked ruling stays online and searchable forever, and is usually the *better* keyword match. CROSSCheck is an agent that, given a product description and an entry date, outputs the tariff code **that was controlling law on that date** — i.e. it must notice the ruling was superseded and apply the effective-date rule. Ground truth is CBP's own published codes on both sides. Data: `https://rulings.cbp.gov/api/search`.

---

## 3. MANDATORY ATTACKS — run every one, report real numbers

Build the smallest honest version of the evaluation set first (≥12 superseded pairs, each producing two dated queue lines — one before the revocation's effective date, one after — plus stable controls). Then attack it. **Report a score for every attack, or state explicitly that you could not run it and why.**

**A1 — The graph-lookup script. This is the primary kill attempt.**
Write ≤30 lines, no LLM: retrieve the ruling from the product description (BM25 or plain keyword), follow the revocation edge, compare the entry date to the effective date, emit the corresponding code. **If this scores near 100%, the candidate is dead.** This is the exact attack that killed the previous CROSS candidate.

**A2 — Constants and degenerate policies.** Always-newest-code. Always-oldest-code. Majority class. Most-frequent-code-in-chapter. Report each.

**A3 — Retrieval-only.** BM25 top-1 ruling, emit its code, ignore dates entirely.

**A4 — Regex on the revoking ruling.** Whatever the cheapest text extraction of the new code is (e.g. `TARIFF NO:`).

**A5 — One off-the-shelf model, one prompt, no tools**, over the frozen corpus. This is the honest baseline the project must beat.

**A6 — Leakage probe.** Does the product description uniquely identify its source ruling? Measure it. If descriptions are verbatim from the rulings, retrieval is trivial — quantify how trivial, because the design deliberately makes retrieval easy and that may be the fatal opening.

---

## 4. THE STRUCTURAL QUESTION — answer this explicitly

This is the crux, and the divergent research says it is where every candidate of this family dies:

> **Can the corpus be frozen offline such that the AGENT can determine the controlling authority, but a DETERMINISTIC SCRIPT cannot?**

- The revocation information must be in the shipped corpus, or nobody can answer.
- If it is present in structured form, a script wins.
- If it is present only in prose, measure how well a regex extracts it.
- **If there is no freeze boundary that admits the agent and excludes the script, the candidate is dead.** Say so plainly.

Also check: is the residual difficulty *real judgement* or just lookup? Cases where a revocation **splits** merchandise across two codes are claimed as the hard case — count how many exist in the actual pool. If it is 1 or 2 out of 12, that is not a benchmark, it is an anecdote.

---

## 5. Prior art — verify, do not assume

- **ATLAS**, arXiv 2509.18400 (2025-09-22), *"Benchmarking and Adapting LLMs for Global Trade via Harmonized Tariff Code Classification"* — already exists and is built on CROSS. Read the abstract. Decide honestly: does CROSSCheck measure a genuinely different axis (authority currency, not classification accuracy), or is it a variant of published work?
- Search for anything else on supersession, ruling currency, citators for administrative rulings, or legal-authority-validity benchmarks.
- Re-run a GitHub census for competitors created since 2026-08-27 in this space.

---

## 6. If it dies — bounded redesign

If CROSSCheck fails, attempt **at most 3** structural redesigns. A redesign must change the *shape* (what is frozen, what is predicted, what the unit is) — not add a patch. Attack each redesign with §3 again. **Do not fall in love with a rescue.** Most rescues should also die.

---

## 7. Head-to-head — required regardless of outcome

Two candidates survived the 143-idea search, both wounded. Read their full entries in `context/06-DIVERGENT-RESEARCH.md` §2:

1. **Erratum Gate (redesigned)** — IETF RFC errata adjudication. Best shortcut table in the search, but the improvement is not yet statistically real (p = 0.29 at n=42) and the licence is UNKNOWN.
2. **The Instruction That Won't Execute (redesigned)** — Federal Register amendatory instructions. Clean licence, but a hardcoded constant (0.5876) currently beats the best script (0.5855).

**Do the cheap decisive check on each:**
- Erratum Gate: **resolve the licence** — read IETF Trust Legal Provisions / TLP 5.0 / RFC 5378 and state whether `errata.json` can be redistributed inside a submission that micro1 will own. This is a qualification-gate item.
- Instruction: confirm whether **exact instruction-count matching** neutralises the constant. If it does not, it dies.

Then rank all surviving options — CROSSCheck (or its redesign), Erratum Gate, Instruction — against these six properties:

1. Zero authored ground truth (labels written and published by an external authority)
2. Scorer is a dependency-free script with no model in it
3. Cheating foreclosed **by construction**, not patched
4. Public data, licence unambiguous, freezes offline cleanly
5. No visible competitors
6. A simple baseline fails for a reason statable in advance

Add three practical dimensions: **buildable in ~24 hours solo**, **demonstrable in 60 seconds of video**, **produces a rich agent trajectory** (a required deliverable).

---

## 8. Output → `context/07-KILL-TEST.md`

```
# Kill Test — Results

## 1. VERDICT ON CROSSCHECK
Dead or alive, in one sentence. Then the evidence.

## 2. The attack table
Every attack from §3 with its measured score. Mark anything you could not run.

## 3. The structural question
Direct answer to §4, with the freeze boundary analysis.

## 4. Prior art
ATLAS and anything else, with URLs and an honest collision assessment.

## 5. Redesigns attempted
What was tried, what it scored, what survived. (Omit if CROSSCheck lived.)

## 6. Head-to-head
The three-way comparison table against the six properties plus the three
practical dimensions. Licence question for Erratum Gate RESOLVED.

## 7. RECOMMENDATION
ONE project to build, fully specified enough to start immediately:
user, bottleneck, baseline, control arm, advanced solution with at most
3 capabilities, primary metric, guard metric with a number, corpus with
URLs and licence, hard case, removed experiment, hot take, and an
hour-by-hour plan for ~24 build hours.
Be decisive. Do not present options.

## 8. What I could not settle
Honest gaps and how much they matter.
```

**Rules of evidence:** label every claim **VERIFIED** (you ran it or fetched it — give the number or URL), **INFERRED**, or **UNKNOWN**. Never present a guess as a fact.

**No token or time limits. Use many agents and workflows. Depth over speed — but this is the last gate before building, so do not spiral.**

---

## 9. Final step — the handoff

When finished, print a text block, **under 400 words**, that the user will paste into the other session. It must contain:

1. **VERDICT:** CROSSCheck alive or dead, and the single number that decided it
2. **The attack table** — one line per attack with its score
3. **The answer to the structural question** in one sentence
4. **THE RECOMMENDATION** — which project to build, and the one-line reason it beat the others
5. **The top risk** that remains
6. Confirmation that the full report is at `context/07-KILL-TEST.md`

Then stop. **Do not build anything.**
