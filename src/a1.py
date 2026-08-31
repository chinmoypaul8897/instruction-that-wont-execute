"""CH-06 — **A1, the advanced solution.** `CONTEXT.md` §5's output contract, §6's two
capabilities, and the note-emission contract, run as real Anthropic tool use.

    python -m a1 run --arm A1-iter1 --reps 1
    python -m a1 run --arm A1 --reps 3
    python -m a1 run --arm A1-minus-tool --reps 1
    python -m a1 check

THE FOUR ARMS, AND WHAT EACH ONE GETS
-------------------------------------
    A1-iter1        B0-agent + `cfr_resolve`.  NO procedure.
    A1              + `agents/A1-SKILL.md`.    Both capabilities. THE SOLUTION.
    A1-minus-tool   the procedure, NO resolver.            ablation
    A1-minus-skill  == A1-iter1 BY CONSTRUCTION            ablation

`A1-minus-skill` is the same configuration as `A1-iter1` under a second name, so it is
run ONCE and reported in both rows with the identity stated. This was declared in
`CHANGELOG.md` at `e12466c` **before the runs**, not discovered afterwards. Passing
`--arm A1-minus-skill` is refused with that explanation rather than silently billed
twice.

`verdict` IS A DERIVED FIELD - `CONTEXT.md` §5, and it is enforced HERE, IN CODE
-------------------------------------------------------------------------------
The model is never asked for a section verdict and cannot emit one. It emits one ruling
per amendatory instruction; `derive_output()` computes the section verdict from those
rulings by the rule *a section fails if ANY instruction fails*. So the agent cannot be
right for the wrong reason: to score `WILL_FAIL` correctly it has to name WHICH
instruction fails and WHY.

    "verdict is a DERIVED field of resolution_trace, not the primary output. This is
     the change that earns the 30-point row: every capability becomes directly readable
     in the artifact rather than inferable from an average."   - CONTEXT.md section 5

WHAT AN INCOMPLETE EMISSION SCORES - fixed here, before the runs, and non-gameable
---------------------------------------------------------------------------------
`GOOD.md` §1: *"An unparseable or absent verdict is a FAILURE, never a skip."* Applied
to a per-instruction contract that means:

  * a **targeted** instruction (one carrying an anchor or a designation) with NO model
    record is **NOT RULED**. Any item with a not-ruled instruction derives
    `verdict = None`, which `score.py` charges as a failure, and routes to the human
    queue. An agent cannot buy `WILL_EXECUTE` by omitting the record that would have
    failed.
  * an **umbrella** instruction - no anchor and no designation, e.g. *"Section 75.6 is
    amended as follows:"* - is auto-filled `executes = true` when its record is absent.
    It asserts nothing that can be false, `A1-SKILL.md` says so in Step 3, and this
    leniency cannot be exploited: an umbrella has no target to be wrong about.

THE TOOL-AVAILABILITY-VS-TOOL-USE GAP - `plan.md` CH-06 requires it measured
---------------------------------------------------------------------------
Every arm's artifact carries the DETERMINISTIC resolver facts for every instruction,
computed by this harness whether or not the model asked for them, **beside** the model's
own ruling and a count of the tool calls it actually made. So three different questions
are answerable from one file: what is true, what the model said, and whether it looked.

PURITY - hard rule 8 binds the SCORER and the RESOLVER, and both stay pure: `cfr_resolve`
is imported unmodified and is handed only frozen text. This module is an arm runner and
makes network calls, exactly as `src/arms.py` does.
HARD RULE 10 - every call goes through `RunLogger`. Tool calls, tool responses, retries
and human checkpoints are all trajectory records.
HARD RULE 11 - `data/` is read-only here. Items are read and never written.
HARD RULE 12 - the key is read by name, never printed, never written to a trajectory.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apiclient import API_URL, API_VERSION, ApiError, load_api_key  # noqa: E402
from arms import SYSTEM_COMMON, instruction_block, load_items       # noqa: E402
from cfr_resolve import ResolveError, cfr_resolve                   # noqa: E402
from runlog import RunLogger, SpendCeilingExceeded                  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DEFAULT_EVALSET = REPO / "data/evalset/items.jsonl"
DEFAULT_TRAJ = REPO / "docs/trajectories/arms/per-item"
BUNDLE_DIR = REPO / "docs/trajectories/arms"
DEFAULT_LEDGER = REPO / "docs/evidence/runs/cost_ledger.csv"
DEFAULT_OUT = REPO / "docs/evidence/ch06-a1"
SKILL_PATH = REPO / "agents/A1-SKILL.md"
DOC_PATH = REPO / "agents/A1.md"

HAIKU = "claude-haiku-4-5-20251001"
MAX_TOKENS = 2048
MAX_ROUNDS = 8            # tool-use rounds per item, then the model must answer

# CONTEXT.md section 5, read off NARA's own note vocabulary. Not invented, not extended.
FAILURE_CLASSES = (
    "target-does-not-exist",
    "target-already-exists",
    "quoted-text-not-present",
    "incomplete-set-out-text",
    "incorrect-citation-or-designation",
)

WILL_FAIL = "WILL_FAIL"
WILL_EXECUTE = "WILL_EXECUTE"


class A1Error(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips."""


# ============================================================ the system prompts

SYSTEM_A1_TASK = SYSTEM_COMMON + """
You will be shown the amendatory instructions for ONE CFR section from ONE final
rule, AND the text of that section as it stood immediately before the rule was
published.

You do NOT emit a verdict for the section. You emit ONE RULING PER AMENDATORY
INSTRUCTION, and the section verdict is derived from your rulings by the rule that a
section fails if ANY of its instructions fails. Naming which instruction fails, and
why, IS the task.
"""

SYSTEM_TOOL_NOTE = """
You have a deterministic tool, `cfr_resolve`. It reads the frozen point-in-time section
text and answers two independent questions about one instruction: is this paragraph
designation declared in the section, and is this quoted anchor present in it. It cannot
be wrong about the text; it can only be asked the wrong question.

You may call it several times in a single turn - one call per instruction you are
checking - and doing so is preferred.
"""

OUTPUT_CONTRACT = """
Return ONE JSON object and nothing else. No prose before or after it, no markdown fence:

{"instructions": [
  {"instruction_index": 1, "operation": "amend", "anchor": null, "designation": null,
   "executes": true, "failure_class": null, "why": "umbrella; asserts no target"},
  {"instruction_index": 2, "operation": "remove", "anchor": "1916 Race Street",
   "designation": null, "executes": false, "failure_class": "quoted-text-not-present",
   "why": "cfr_resolve: found=false, level=none at all three declared levels"}
]}

One record per instruction, in document order, NONE OMITTED - umbrellas included.
`executes: false` REQUIRES a `failure_class`, which must be exactly one of:
  target-does-not-exist · target-already-exists · quoted-text-not-present ·
  incomplete-set-out-text · incorrect-citation-or-designation
`executes: true` takes `failure_class: null`.
Do NOT emit a section-level verdict. It is derived from these records.
"""

TOOL_SCHEMA = {
    "name": "cfr_resolve",
    "description": (
        "Resolve one amendatory instruction against the frozen point-in-time text of "
        "the section under review. Designation-hierarchy state is resolved FIRST and "
        "unconditionally, quoted-anchor matching second, and the two results are "
        "INDEPENDENT - neither implies the other. Anchor matching is attempted at "
        "three declared normalisation levels in order - exact, whitespace-collapsed, "
        "alphanumeric-only - and the level actually achieved is reported, never "
        "applied invisibly. The title, part, section and as-of date are fixed for this "
        "item and supplied automatically; you cannot change which text is searched."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "designation": {
                "type": "string",
                "description": (
                    "The paragraph designation path the instruction targets, written "
                    "exactly as the instruction writes it, e.g. '(b)(4)(i)(A)'. Omit "
                    "if the instruction names no paragraph. Do NOT invent one."),
            },
            "quoted_text": {
                "type": "string",
                "description": (
                    "The text the instruction puts in quotation marks and says to "
                    "find, copied character for character. Omit if the instruction "
                    "quotes nothing. Do NOT invent one."),
            },
            "instruction_index": {
                "type": "integer",
                "description": "Which instruction, 1-based, this call is checking.",
            },
        },
        "required": [],
    },
}


def load_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


ARMS = {
    #                              tool   skill
    "A1-iter1":      {"tool": True,  "skill": False},
    "A1":            {"tool": True,  "skill": True},
    "A1-minus-tool": {"tool": False, "skill": True},
}

REFUSED_ARMS = {
    "A1-minus-skill": (
        "`A1-minus-skill` IS `A1-iter1` by construction - both are B0-agent plus "
        "cfr_resolve with no procedure. This identity was declared in CHANGELOG.md at "
        "e12466c BEFORE the runs. Run `--arm A1-iter1` once and report it in both "
        "rows. Billing the same configuration twice would produce two numbers that "
        "differ only by sampling and invite a reader to treat them as independent "
        "evidence."),
}


def system_prompt(arm: str) -> str:
    spec = ARMS[arm]
    out = SYSTEM_A1_TASK
    if spec["tool"]:
        out += SYSTEM_TOOL_NOTE
    else:
        out += ("\nYou have NO tool. Check each instruction against the section text "
                "yourself, by reading it.\n")
    if spec["skill"]:
        out += "\n" + "=" * 70 + "\nTHE PROCEDURE YOU FOLLOW\n" + "=" * 70 + "\n"
        out += load_skill()
    out += "\n" + OUTPUT_CONTRACT
    return out


def user_prompt(item) -> str:
    """The B0-agent user prompt, verbatim in its head and body, with the tail replaced
    by the per-instruction contract. Head and body are IDENTICAL to `arms.user_prompt`
    so that A1 and B0-agent differ in their capabilities and not in their briefing -
    `CONTEXT.md` §4's fairness rule."""
    head = (f"CFR title {item['cfr_title']}, section {item['section']}.\n"
            f"Federal Register document {item['frdoc']}, "
            f"published {item['publication_date']}.\n")
    body = (f"\nThe text of {item['cfr_title']} CFR {item['section']} as of the "
            f"{item['as_of_edition']} annual edition (revised "
            f"{item['as_of_revision_date']}), which is the last edition published "
            f"before this rule:\n\n"
            f"--- BEGIN SECTION TEXT ---\n{item['section_text']}\n"
            f"--- END SECTION TEXT ---\n")
    tail = (f"\nAmendatory instructions ({item['instruction_count']}), in document "
            f"order:\n\n{instruction_block(item)}\n\n"
            f"Rule on each of these {item['instruction_count']} instructions.")
    return head + body + tail


def assert_skill_matches_agents_md() -> dict:
    """The executed prompt and the published instruction files must not drift apart.

    Deliverable 1 is *"the instructions that shape each agent"*. A document that no
    longer matches the code is a claim, not an omission, and is worse than shipping
    nothing. Checked before the first call of every run.
    """
    skill = load_skill()
    for probe in ("THE PROCEDURE — one instruction at a time, in order, no exceptions",
                  "THE NOTE-EMISSION CONTRACT",
                  "WHEN TO STOP AND ASK A HUMAN",
                  "target-does-not-exist"):
        if probe not in skill:
            raise A1Error(f"agents/A1-SKILL.md is missing {probe!r}")
    doc = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else ""
    for arm in ARMS:
        if arm not in doc:
            raise A1Error(f"agents/A1.md does not document the arm {arm!r}")
    for line in SYSTEM_A1_TASK.strip().splitlines():
        line = line.strip()
        if len(line) < 20:
            continue
        if line not in doc:
            raise A1Error(
                "agents/A1.md does not contain this line of A1's system prompt, so "
                f"the published instructions have drifted from the executed ones:\n"
                f"    {line!r}")
    return {"skill": str(SKILL_PATH.relative_to(REPO).as_posix()),
            "doc": str(DOC_PATH.relative_to(REPO).as_posix()),
            "skill_chars": len(skill)}


# ============================================================ the deterministic half

def resolver_facts(item) -> dict[int, dict]:
    """`cfr_resolve` over EVERY instruction of the item, computed by the harness.

    Pure, and computed for every arm - including `A1-minus-tool`, which the model runs
    without the tool. These are facts about the ITEM, not about the arm, and they are
    what makes the emitted note a note: `CONTEXT.md` §5's trace fields (`found`,
    `level`, `designation_exists`, `siblings`, `char_offset`) are resolver fields.

    Carrying them for the no-tool arm too is what makes the tool-availability-vs-tool-use
    gap measurable at all: the artifact then says what was true, beside what the model
    said, beside whether it looked.
    """
    out = {}
    text = item["section_text"]
    for idx, ins in enumerate(item["instructions"], start=1):
        desig = ins.get("designation")
        anchor = ins.get("anchor")
        try:
            r = cfr_resolve(item["cfr_title"], item["cfr_part"], item["section"],
                            item["as_of_revision_date"], text,
                            quoted_text=anchor, designation=desig)
        except ResolveError as exc:
            # A designation the parser produced that the resolver refuses to parse is
            # itself a finding - it is recorded, never smoothed into a False.
            r = {"found": False, "level": "none", "char_offset": None,
                 "designation": desig, "designation_exists": None, "siblings": [],
                 "resolver_error": str(exc)}
        out[idx] = r
    return out


def human_checkpoint_reasons(item, facts) -> list[str]:
    """`CONTEXT.md` §9 / the CH-06 card: the three deterministic routing conditions.

    Computed from the trace, by code, not by the model - an agent that decided for
    itself when to escalate would escalate whenever it was unsure, which is a
    confidence report and not a checkpoint.
    """
    reasons = []
    for idx, ins in enumerate(item["instructions"], start=1):
        f = facts[idx]
        # C1 - the anchor is absent and the target paragraph is present. The two halves
        #      of the instruction disagree about whether it can execute.
        #      `level == "none"` is ALSO what `find_anchor` returns when no anchor was
        #      asked for at all, so the anchor must have been ASKED before its absence
        #      means anything. Golden C0 caught this: without the `ins.get("anchor")`
        #      clause, C1 fired on every instruction naming a paragraph that exists,
        #      and a checkpoint that fires on everything is not a checkpoint.
        if (ins.get("anchor")
                and f.get("level") == "none" and f.get("designation_exists") is True):
            reasons.append(
                f"C1 instruction {idx}: level='none' (quoted anchor not present at any "
                f"declared level) while designation_exists=true for "
                f"{f.get('designation')!r} - the designation path and the anchor path "
                f"do not agree about this instruction")
        # C2 - both halves were asked and they returned opposite answers.
        if (ins.get("anchor") and ins.get("designation")
                and f.get("designation_exists") is not None
                and bool(f.get("found")) != bool(f.get("designation_exists"))):
            reasons.append(
                f"C2 instruction {idx}: both paths were asked and disagree - "
                f"found={f.get('found')} designation_exists={f.get('designation_exists')}")
    # C3 - a designation is touched twice, so instruction k changes what k+1 will find.
    #      The ordered-state ledger that would resolve this is CONTEXT.md section 6's
    #      capability 3, NOT BUILT by ruling R-01. This agent does not model execution
    #      order and must not pretend to.
    seen: dict[str, list[int]] = {}
    for idx, ins in enumerate(item["instructions"], start=1):
        d = ins.get("designation")
        if d:
            seen.setdefault(str(d), []).append(idx)
    for d, idxs in sorted(seen.items()):
        if len(idxs) > 1:
            reasons.append(
                f"C3 designation {d} is touched by instructions {idxs} - instruction "
                f"{idxs[0]} changes what instruction {idxs[1]} will find, and the "
                f"ordered-state ledger is NOT BUILT (ruling R-01, counted removal #3)")
    return reasons


def is_umbrella(ins) -> bool:
    """No anchor and no designation: it asserts nothing that can be false."""
    return not ins.get("anchor") and not ins.get("designation")


def derive_output(item, model_records: dict, facts: dict, tool_calls: int) -> dict:
    """`CONTEXT.md` §5's output contract. **`verdict` is DERIVED here, in code.**

    The model never sees this function and cannot emit a section verdict. Returns the
    full note artifact; `verdict` is None when the emission is incomplete, and
    `score.py` charges None as a FAILURE.
    """
    trace, unruled = [], []
    for idx, ins in enumerate(item["instructions"], start=1):
        f = facts[idx]
        rec = model_records.get(idx)
        if rec is None and is_umbrella(ins):
            # declared in this module's docstring, before the runs: an umbrella with no
            # record is auto-filled true. It has no target to be wrong about.
            rec = {"executes": True, "failure_class": None,
                   "why": "no model record; umbrella instruction auto-filled by the "
                          "harness (no anchor, no designation, nothing to be false)",
                   "auto_filled": True}
        if rec is None:
            unruled.append(idx)
        trace.append({
            "instruction_index": idx,
            "operation": ins.get("operation"),
            "anchor": ins.get("anchor"),
            "designation": ins.get("designation"),
            # the deterministic half - CONTEXT.md section 5's trace fields
            "found": f.get("found"),
            "level": f.get("level"),
            "designation_exists": f.get("designation_exists"),
            "siblings": f.get("siblings"),
            "char_offset": f.get("char_offset"),
            # the model half, kept apart so the two can be compared
            "model_ruling": rec,
        })

    reasons = human_checkpoint_reasons(item, facts)
    if unruled:
        reasons.insert(0, (
            f"EMISSION INCOMPLETE: targeted instruction(s) {unruled} carry no model "
            f"ruling. GOOD.md §1 - a non-answer is a FAILURE, never a skip - so the "
            f"verdict is not derived and the item is charged as wrong."))

    if unruled or not model_records:
        verdict, failing, fclass = None, None, None
    else:
        failing_recs = [(t["instruction_index"], t) for t in trace
                        if t["model_ruling"] and t["model_ruling"].get("executes") is False]
        if failing_recs:
            verdict = WILL_FAIL
            idx, t = failing_recs[0]
            failing = t["designation"] or (t["model_ruling"] or {}).get("designation")
            raw_class = (t["model_ruling"] or {}).get("failure_class")
            # the five-way vocabulary is CLOSED. A sixth class is not adopted silently.
            fclass = raw_class if raw_class in FAILURE_CLASSES else None
            if raw_class and fclass is None:
                reasons.append(
                    f"instruction {idx} was ruled failing with failure_class "
                    f"{raw_class!r}, which is NOT one of CONTEXT.md §5's five NARA "
                    f"classes; the class is dropped and the item is routed")
        else:
            verdict, failing, fclass = WILL_EXECUTE, None, None

    return {
        "item_id": item["item_id"],
        "verdict": verdict,
        "failing_designation": failing,
        "failure_class": fclass,
        "resolution_trace": trace,
        "needs_human_review": bool(reasons),
        "review_reason": ("; ".join(reasons) if reasons else None),
        "tool_calls_made": tool_calls,
        "instructions_unruled": unruled,
    }


# ============================================================ the model half

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)


def extract_records(text: str) -> dict:
    """The model's final text -> {instruction_index -> record}. Tolerant of a fence,
    strict about everything else. Returns {} if nothing parses, which derives a None
    verdict, which `score.py` charges as a failure."""
    if not text:
        return {}
    candidates = [text.strip()]
    m = _FENCE.search(text)
    if m:
        candidates.insert(0, m.group(1))
    first, last = text.find("{"), text.rfind("}")
    if first != -1 and last > first:
        candidates.append(text[first:last + 1])
    for cand in candidates:
        try:
            obj = json.loads(cand)
        except Exception:
            continue
        recs = obj.get("instructions") if isinstance(obj, dict) else obj
        if not isinstance(recs, list):
            continue
        out = {}
        for i, r in enumerate(recs, start=1):
            if not isinstance(r, dict):
                continue
            idx = r.get("instruction_index", i)
            try:
                idx = int(idx)
            except Exception:
                idx = i
            out[idx] = r
        if out:
            return out
    return {}


def _post(key, body, timeout=180):
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode("utf-8"),
        headers={"x-api-key": key, "anthropic-version": API_VERSION,
                 "content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_with_tools(key, model, system, user, tools, log, item, facts,
                    max_rounds=MAX_ROUNDS, _sleep=time.sleep):
    """One item's agentic loop. Returns (final_text, usage, tool_calls).

    Retries on 429/5xx and transport errors only, exactly as `apiclient.call_messages`
    does - `GOOD.md` §8 fixes that policy and it is not re-decided here. A 400 or 404
    is a real answer and is raised. Every tool call and every retry is a trajectory
    record (hard rule 10).
    """
    messages = [{"role": "user", "content": user}]
    usage = {"input_tokens": 0, "output_tokens": 0}
    tool_calls = 0
    for _round in range(max_rounds):
        body = {"model": model, "max_tokens": MAX_TOKENS, "temperature": 0.0,
                "system": system, "messages": messages}
        if tools:
            body["tools"] = tools
        obj = None
        for attempt in range(1, 5):
            try:
                obj = _post(key, body)
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:400]
                if not (exc.code == 429 or 500 <= exc.code < 600) or attempt == 4:
                    raise ApiError(f"HTTP {exc.code}: {detail}") from None
                log.retry(reason=f"HTTP {exc.code}: {detail}"[:200], attempt=attempt)
                _sleep(2 ** attempt)
            except Exception as exc:
                if attempt == 4:
                    raise ApiError(f"transport failure: {exc!r}") from None
                log.retry(reason=repr(exc)[:200], attempt=attempt)
                _sleep(2 ** attempt)
        u = obj.get("usage") or {}
        usage["input_tokens"] += int(u.get("input_tokens", 0))
        usage["output_tokens"] += int(u.get("output_tokens", 0))
        content = obj.get("content", [])

        if obj.get("stop_reason") != "tool_use":
            return ("".join(b.get("text", "") for b in content if b.get("type") == "text"),
                    usage, tool_calls)

        messages.append({"role": "assistant", "content": content})
        results = []
        for blk in content:
            if blk.get("type") != "tool_use":
                continue
            tool_calls += 1
            args = blk.get("input") or {}
            log.action("tool_call", "cfr_resolve", input=args)
            try:
                out = cfr_resolve(
                    item["cfr_title"], item["cfr_part"], item["section"],
                    item["as_of_revision_date"], item["section_text"],
                    quoted_text=args.get("quoted_text") or None,
                    designation=args.get("designation") or None)
                # the trajectory carries the tool's whole answer, not a summary
                log.tool_response("cfr_resolve", output=out)
                payload = json.dumps({k: out[k] for k in (
                    "found", "level", "char_offset", "matched_span", "levels_tried",
                    "designation", "designation_exists", "siblings",
                    "declared_designations")})
            except ResolveError as exc:
                # The tool REFUSES rather than guessing - e.g. a designation that is not
                # a parenthesised path. That refusal is the answer and is returned as
                # such, because inventing a target is the defect being looked for.
                log.tool_response("cfr_resolve", error=str(exc))
                payload = json.dumps({"error": str(exc)})
            results.append({"type": "tool_result", "tool_use_id": blk.get("id"),
                            "content": payload})
        if not results:
            return ("".join(b.get("text", "") for b in content if b.get("type") == "text"),
                    usage, tool_calls)
        messages.append({"role": "user", "content": results})
        log.feedback(f"round {_round + 1}: {len(results)} cfr_resolve result(s) "
                     f"returned to the model")
    # Out of rounds. Ask once more with no tools, so the item gets an answer rather
    # than an error - and the exhaustion is a trajectory record either way.
    log.feedback(f"tool-use rounds exhausted at {max_rounds}; requesting the final "
                 f"JSON with the tool withdrawn")
    body = {"model": model, "max_tokens": MAX_TOKENS, "temperature": 0.0,
            "system": system,
            "messages": messages + [{"role": "user", "content":
                                     "Stop calling tools. Return the JSON object now."}]}
    obj = _post(key, body)
    u = obj.get("usage") or {}
    usage["input_tokens"] += int(u.get("input_tokens", 0))
    usage["output_tokens"] += int(u.get("output_tokens", 0))
    return ("".join(b.get("text", "") for b in obj.get("content", [])
                    if b.get("type") == "text"), usage, tool_calls)


def run_arm(arm, items, model, rep, traj_dir, ledger_path, out_dir) -> dict:
    spec = ARMS[arm]
    system = system_prompt(arm)
    tools = [TOOL_SCHEMA] if spec["tool"] else None
    key = load_api_key()
    preds, artifacts, errors = {}, [], []
    usage_total = {"in": 0, "out": 0}
    tool_calls_total = 0
    routed = 0
    for item in items:
        facts = resolver_facts(item)
        run_id = f"{arm}__{item['item_id'].replace('|', '_').replace('/', '_')}__rep{rep}"
        try:
            with RunLogger(arm=arm, item_id=item["item_id"], model=model,
                           agent_instructions=system, delivery="standard",
                           est_usd="0.05", run_id=run_id, traj_dir=traj_dir,
                           ledger_path=ledger_path) as log:
                prompt = user_prompt(item)
                log.action("message", "messages.create",
                           input={"model": model, "temperature": 0.0,
                                  "max_tokens": MAX_TOKENS,
                                  "tool_available": bool(tools),
                                  "skill_loaded": spec["skill"],
                                  "user_prompt_chars": len(prompt),
                                  "user_prompt": prompt})
                try:
                    text, usage, ncalls = call_with_tools(
                        key, model, system, prompt, tools, log, item, facts)
                except ApiError as exc:
                    log.tool_response("messages.create", error=str(exc))
                    log.feedback("the call failed after retries; this item gets NO "
                                 "prediction and the scorer counts it as a failure")
                    errors.append({"item_id": item["item_id"], "error": str(exc)[:200]})
                    continue
                log.tool_response("messages.create", output={"text": text})
                records = extract_records(text)
                art = derive_output(item, records, facts, ncalls)
                art["arm"], art["rep"] = arm, rep
                art["raw_final_text_chars"] = len(text)
                if art["needs_human_review"]:
                    routed += 1
                    log.human_checkpoint(
                        reason=art["review_reason"],
                        resolution=("ROUTED TO THE HUMAN QUEUE. Both readings and the "
                                    "full paragraph trace are emitted in the artifact "
                                    "at docs/evidence/ch06-a1/; this agent does not "
                                    "decide it. CONTEXT.md §9."))
                artifacts.append(art)
                preds[item["item_id"]] = art["verdict"]
                usage_total["in"] += usage["input_tokens"]
                usage_total["out"] += usage["output_tokens"]
                tool_calls_total += ncalls
                log.finish(verdict=str(art["verdict"])[:32],
                           input_tokens=usage["input_tokens"],
                           output_tokens=usage["output_tokens"])
        except SpendCeilingExceeded:
            errors.append({"item_id": item["item_id"], "error": "SPEND CEILING"})
            raise
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{arm}-rep{rep}-artifacts.jsonl").write_text(
        "".join(json.dumps(a, sort_keys=True) + "\n" for a in artifacts),
        encoding="utf-8", newline="\n")
    return {"arm": arm, "model": model, "rep": rep, "predictions": preds,
            "errors": errors, "usage": usage_total, "tool_calls": tool_calls_total,
            "items_routed_to_human": routed,
            "n_items": len(items), "n_predicted": len(preds)}


def bundle(arm: str, rep: int) -> int:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DEFAULT_TRAJ.glob(f"{arm}__*__rep{rep}.jsonl"))
    out = BUNDLE_DIR / f"{arm}-rep{rep}.jsonl"
    n = 0
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for f in files:
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    fh.write(line + "\n")
                    n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "check"])
    ap.add_argument("--arm", action="append", default=None)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--model", default=HAIKU)
    ap.add_argument("--evalset", default=str(DEFAULT_EVALSET))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--limit", type=int, default=0, help="smoke test on the first N items")
    args = ap.parse_args(argv)

    parity = assert_skill_matches_agents_md()
    print(f"  prompt/document parity OK: {parity}")
    if args.cmd == "check":
        return 0

    items = load_items(Path(args.evalset))
    if args.limit:
        items = items[:args.limit]
    out = Path(args.out)
    for arm in (args.arm or ["A1"]):
        if arm in REFUSED_ARMS:
            print(f"  REFUSED: {arm}\n    {REFUSED_ARMS[arm]}")
            return 2
        if arm not in ARMS:
            raise A1Error(f"unknown arm {arm!r}; known: {sorted(ARMS)}")
        for rep in range(1, args.reps + 1):
            print(f"  running {arm} rep {rep}/{args.reps} over {len(items)} items ...")
            r = run_arm(arm, items, args.model, rep, DEFAULT_TRAJ, DEFAULT_LEDGER, out)
            print(f"    predicted {r['n_predicted']}/{r['n_items']}  "
                  f"tool_calls={r['tool_calls']}  routed={r['items_routed_to_human']}  "
                  f"in={r['usage']['in']:,} out={r['usage']['out']:,}  "
                  f"errors={len(r['errors'])}")
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{arm}-rep{rep}.json").write_text(
                json.dumps(r, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n")
            n = bundle(arm, rep)
            print(f"    bundled {arm}-rep{rep}.jsonl  {n} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
