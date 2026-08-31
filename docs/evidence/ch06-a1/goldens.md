# CH-06 goldens — hand-computed from `CONTEXT.md` §5, before `tests/test_a1.py` exists

**Hard rule 4.** Every expected value below was derived by reading `CONTEXT.md` §5's
output contract and `src/a1.py`'s pre-declared incomplete-emission rule, and writing down
what the answer *must* be. **None of it came from running the code.** A test whose
expected value came from the code it tests proves nothing.

## Disclosed process deviation — Class B, recorded rather than absorbed

**`src/a1.py` was written before this file.** Hard rule 4 asks for goldens first and that
ordering was not followed, because the module's shape (which functions exist, what they
are called) had to settle before fixtures could name them.

What was preserved is the property the rule exists to protect: **every expected value
here was computed by hand from the specification, not by executing `src/a1.py` and
recording what it did.** The commit order is `goldens.md` → `tests/test_a1.py` → first
run, and it is checkable with `git log`. If a golden below disagrees with the code, **the
golden wins and the code is the defect** — `CLAUDE.md`'s precedence chain, where
`CONTEXT.md` outranks the code.

The scope of what these goldens cover is `src/a1.py` **only**. `cfr_resolve` is CH-05,
unmodified here, and carries its own 41 goldens committed before it at
`docs/evidence/ch05-resolve/goldens.md`.

---

## Group D — `derive_output()`: **`verdict` is a DERIVED field**

The rule, from `CONTEXT.md` §5 and `agents/A1-SKILL.md` Step 4: *a section fails if
**any** instruction fails, and executes only if **every** instruction executes.* The
model never emits a section verdict.

Shared fixture shape. Two instructions unless stated:

```
ins[1] = {"operation": "amend",  "anchor": null,        "designation": null}      <- umbrella
ins[2] = {"operation": "revise", "anchor": null,        "designation": "(b)(4)"}  <- targeted
```

### D1 — every instruction executes → `WILL_EXECUTE`

Model records: `1 → executes true`, `2 → executes true`.

| Field | Hand-computed expectation | Reasoning |
|---|---|---|
| `verdict` | **`"WILL_EXECUTE"`** | no record has `executes: false` |
| `failing_designation` | **`null`** | nothing failed, so nothing to name |
| `failure_class` | **`null`** | §5: null when the verdict is `WILL_EXECUTE` |
| `instructions_unruled` | **`[]`** | both instructions have records |
| `len(resolution_trace)` | **2** | one record per instruction, none omitted |

### D2 — one instruction fails → `WILL_FAIL`, localised to the FIRST failure

Model records: `1 → executes true`; `2 → executes false, failure_class
"target-does-not-exist"`.

| Field | Hand-computed expectation |
|---|---|
| `verdict` | **`"WILL_FAIL"`** |
| `failing_designation` | **`"(b)(4)"`** — the designation of the first failing instruction, taken from the *item*, not from the model's echo of it |
| `failure_class` | **`"target-does-not-exist"`** |

**D2b — first-failure ordering.** Three targeted instructions, designations `(a)`, `(b)`,
`(c)`; records 2 and 3 both `executes: false`, with classes `target-does-not-exist` and
`quoted-text-not-present`. Expected `failing_designation` = **`"(b)"`** and
`failure_class` = **`"target-does-not-exist"`** — instruction order decides, not severity
and not the model's ordering of its own array.

### D3 — a TARGETED instruction has no record → `verdict` is `null`, and it routes

Model records: `1 → executes true` only. Instruction 2 is targeted (it has a designation)
and unruled.

| Field | Hand-computed expectation | Reasoning |
|---|---|---|
| `verdict` | **`null`** | `GOOD.md` §1 — a non-answer is a FAILURE, never a skip. `score.py` charges `None` as wrong. |
| `failing_designation` | **`null`** | |
| `failure_class` | **`null`** | |
| `instructions_unruled` | **`[2]`** | |
| `needs_human_review` | **`true`** | |
| `review_reason` | **starts `"EMISSION INCOMPLETE"`** | and it is the FIRST reason listed |

**This is the anti-gaming golden.** If `verdict` came back `"WILL_EXECUTE"` here, an
agent could buy a correct answer on every clean item by emitting nothing, and buy escape
from every defective one by omitting exactly the record that would have failed.

### D4 — an UMBRELLA instruction has no record → auto-filled `executes: true`

Model records: `2 → executes true` only. Instruction 1 is an umbrella (no anchor, no
designation) and unruled.

| Field | Hand-computed expectation | Reasoning |
|---|---|---|
| `verdict` | **`"WILL_EXECUTE"`** | an umbrella asserts nothing that can be false |
| `instructions_unruled` | **`[]`** | the umbrella was filled, so nothing is unruled |
| `resolution_trace[0].model_ruling.auto_filled` | **`true`** | the fill is **visible in the artifact**, never silent |

The leniency is unexploitable: an umbrella has no target to be wrong about. The
`auto_filled` flag is required — a harness that filled a record without saying so would
be manufacturing evidence.

### D5 — a `failure_class` outside the five NARA classes is DROPPED, not adopted

Model records: `2 → executes false, failure_class "paragraph-mismatch"`.

| Field | Hand-computed expectation | Reasoning |
|---|---|---|
| `verdict` | **`"WILL_FAIL"`** | the instruction *was* ruled failing; the finding survives |
| `failure_class` | **`null`** | `"paragraph-mismatch"` is not in §5's **closed** five-value vocabulary |
| `needs_human_review` | **`true`** | |
| `review_reason` | contains **`"NOT one of"`** | |

The failure is kept and the invented vocabulary is refused. §5: *"`failure_class` values
are read off NARA's own note vocabulary, not invented."* The five, exactly:
`target-does-not-exist` · `target-already-exists` · `quoted-text-not-present` ·
`incomplete-set-out-text` · `incorrect-citation-or-designation`.

### D6 — no records at all → `verdict` is `null`

Model returned prose, or nothing, or unparseable JSON. Expected `verdict` **`null`**,
`needs_human_review` **`true`**. Same rule as D3.

### D7 — the trace always carries the resolver's facts, for EVERY arm

Even for `A1-minus-tool`, which runs with no tool and makes zero tool calls: every
`resolution_trace` record carries `found`, `level`, `designation_exists`, `siblings`,
`char_offset`. These are facts about the **item**, not about the arm. Expected: with
`tool_calls = 0`, `resolution_trace[i]` still has all five keys present and
`tool_calls_made == 0`.

---

## Group C — `human_checkpoint_reasons()`: the three deterministic conditions

Computed **in code from the trace**, never asked of the model.

### C1 — anchor absent while the target paragraph is present

Instruction with `designation "(b)"` and an anchor; resolver returns `level: "none"`,
`designation_exists: true`.
Expected: **exactly one reason beginning `"C1 instruction 1:"`** — plus C2, see below.

### C2 — both paths asked, and they disagree

Instruction carries **both** an anchor and a designation; resolver returns
`found: false`, `designation_exists: true`.
Expected: a reason beginning **`"C2 instruction 1:"`**.

**C1 and C2 overlap by construction** on an instruction that has both an anchor and a
designation where the anchor is missing and the paragraph is present. That is intended:
they are two separately-named readings of one situation and **both are recorded**.
A fixture with a designation but **no** anchor fires **C1 only** — C2 requires both paths
to have been asked.

### C3 — a designation is touched twice

Two instructions both naming `(a)(38)` — e.g. `redesignate (a)(38)` then `add (a)(38)`,
which is real item `05-8447|75.6`.
Expected: a reason beginning **`"C3 designation (a)(38) is touched by instructions [3, 4]"`**
(1-based indices, in ascending order), naming ruling **R-01** and the ordered-state ledger
as **not built**.

### C0 — the clean case

An item whose instructions each resolve consistently and whose designations are all
distinct: expected **`[]`**, and therefore `needs_human_review: false`,
`review_reason: null`.

**A checkpoint that fires on everything is not a checkpoint.** C0 is the golden that
stops the routing rule degenerating into "escalate always", which would look like caution
and function as an opt-out from the metric.

---

## Group E — `extract_records()`: tolerant of packaging, strict about content

| | Input | Hand-computed expectation |
|---|---|---|
| **E1** | a bare JSON object `{"instructions": [...]}` | parsed; keys are the `instruction_index` values |
| **E2** | the same wrapped in a ```` ```json ```` fence | parsed identically — the fence is packaging, not content |
| **E3** | prose, then the JSON object, then more prose | parsed — the object is found between the first `{` and the last `}` |
| **E4** | `"I cannot determine this."` | **`{}`** — which derives `verdict: null`, which scores as a FAILURE |
| **E5** | `""` (empty, as 13 of 20 sonnet calls returned at the checkpoint) | **`{}`** |
| **E6** | records missing `instruction_index` | positionally indexed 1, 2, 3… — a model that omits the index has still answered in order |

E5 is in this list on purpose. The withdrawn model-sensitivity check was a harness defect
in which empty completions were scored as failures with no one noticing until afterwards
(`QUESTIONS.md`, the 2026-08-31 rulings: **13 of 20**). The behaviour is correct and is
kept; what was missing was a test that made it *visible*. This is that test.

---

## Group P — parity and purity

| | Check | Expectation |
|---|---|---|
| **P1** | every line ≥ 20 chars of the executed system prompt appears in `agents/A1.md` | passes, or the run refuses to start |
| **P2** | `agents/A1-SKILL.md` contains the procedure, the note-emission contract, the human-checkpoint section and all five class names | passes |
| **P3** | `--arm A1-minus-skill` | **refused**, naming `A1-iter1` as the same configuration |
| **P4** | A1's user-prompt **head and body** vs `arms.user_prompt(item, gets_text=True)` | **byte-identical** — `CONTEXT.md` §4: the arms differ in capabilities, not in briefing |
| **P5** | `derive_output` and `human_checkpoint_reasons` called twice on the same input | byte-identical output (hard rule 9) |
| **P6** | `cfr_resolve` is imported unmodified from CH-05 | no monkey-patching, no wrapper that changes its answers |
