"""★ CHECKPOINT — run the B0 and B0-agent arms through the run logger.

The prompts are the ones published in `agents/B0.md` and `agents/B0-agent.md`, and
this module is the single place they are constructed, so the shipped instruction files
and the executed prompts cannot drift apart. `assert_prompts_match_agents_md()` checks
that the system prompts in this file appear verbatim in those documents, and the CLI
runs it before the first call.

Everything is fixed in `GOOD.md`, committed at `5172092` BEFORE any arm ran: model,
temperature, max_tokens, reps, delivery, item order, retry policy, no truncation, and
the sensitivity-subset selection rule.

HARD RULE 10 - every call goes through `RunLogger`: trajectory, input tokens, output
tokens, wall-clock, imputed USD. A call that dies before `finish()` gets a ledger row
with an EMPTY cost cell, because unknown is not the same claim as free.

HARD RULE 12 - the API key is read by name and never printed, logged or committed.
`agent_instructions` in the trajectory carries the SYSTEM PROMPT, not the headers.

    python -m arms run --arm B0 --arm B0-agent --reps 3
    python -m arms sensitivity
    python -m arms report
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apiclient import ApiError, call_messages, load_api_key  # noqa: E402
from runlog import RunLogger, SpendCeilingExceeded  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DEFAULT_EVALSET = REPO / "data/evalset/items.jsonl"
# RunLogger writes one file per run. That is its contract and it is not changed -
# but 76 items x 3 reps x 2 arms is 496 files, and the pre-commit guard caps the
# tracked tree at 300 because the 50 MB submission cap is the one limit that must not
# move. So the per-item files land in a git-ignored subdirectory and `bundle()`
# concatenates them into one JSONL per arm-rep, which is the convention
# docs/trajectories/build/ already uses. EVERY RECORD SURVIVES - nothing is sampled,
# summarised or dropped.
DEFAULT_TRAJ = REPO / "docs/trajectories/arms/per-item"
BUNDLE_DIR = REPO / "docs/trajectories/arms"
DEFAULT_LEDGER = REPO / "docs/evidence/runs/cost_ledger.csv"
DEFAULT_OUT = REPO / "docs/evidence/checkpoint"

HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5"
MAX_TOKENS = 16

SYSTEM_COMMON = """You are an editor at the Office of the Federal Register (OFR).

Your job is to decide whether an amendatory instruction in a final rule can be
EXECUTED against the Code of Federal Regulations - that is, whether OFR will be able
to incorporate it into the CFR text.

An instruction fails to execute when, for example, the paragraph it targets does not
exist, the paragraph it adds already exists, quoted text it says to find is not
present in the section, set-out text is incomplete, or a citation or designation is
incorrect. When an instruction cannot be executed, OFR does not change the CFR and
NARA publishes a permanent editorial note recording that the amendment could not be
incorporated.
"""

SYSTEM_B0 = SYSTEM_COMMON + """
You will be shown the amendatory instructions for ONE CFR section from ONE final
rule. You will NOT be shown the CFR text.

Answer with exactly one word, and nothing else:

WILL_FAIL      - at least one instruction cannot be executed as written
WILL_EXECUTE   - every instruction can be executed as written
"""

SYSTEM_B0_AGENT = SYSTEM_COMMON + """
You will be shown the amendatory instructions for ONE CFR section from ONE final
rule, AND the text of that section as it stood immediately before the rule was
published. Check each instruction against the section text.

Answer with exactly one word, and nothing else:

WILL_FAIL      - at least one instruction cannot be executed as written
WILL_EXECUTE   - every instruction can be executed as written
"""

ARMS = {
    "B0": {"system": SYSTEM_B0, "gets_text": False, "doc": "agents/B0.md"},
    "B0-agent": {"system": SYSTEM_B0_AGENT, "gets_text": True,
                 "doc": "agents/B0-agent.md"},
}


class ArmError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips."""


# ============================================================ pure: the prompts

def instruction_block(item) -> str:
    return "\n".join(f"{n}. {ins['text']}"
                     for n, ins in enumerate(item["instructions"], start=1))


def user_prompt(item, gets_text: bool) -> str:
    """Exactly the templates published in `agents/*.md`. Pure.

    STEP 0 of `plan.md`'s decision rule may require re-running with the quoted anchor
    text stripped; that is `strip_anchors=` on `run_arm`, and it is applied to the
    INSTRUCTION text, never to the section text.
    """
    head = (f"CFR title {item['cfr_title']}, section {item['section']}.\n"
            f"Federal Register document {item['frdoc']}, "
            f"published {item['publication_date']}.\n")
    body = ""
    if gets_text:
        body = (f"\nThe text of {item['cfr_title']} CFR {item['section']} as of the "
                f"{item['as_of_edition']} annual edition (revised "
                f"{item['as_of_revision_date']}), which is the last edition published "
                f"before this rule:\n\n"
                f"--- BEGIN SECTION TEXT ---\n{item['section_text']}\n"
                f"--- END SECTION TEXT ---\n")
    tail = (f"\nAmendatory instructions ({item['instruction_count']}), in document "
            f"order:\n\n{instruction_block(item)}\n\n"
            + ("Will these instructions execute against the section text above? "
               if gets_text else "Will these instructions execute? ")
            + "Answer with exactly one word: WILL_FAIL or WILL_EXECUTE.")
    return head + body + tail


def strip_quoted_anchors(item) -> dict:
    """`plan.md` STEP 0: strip the QUOTED ANCHOR TEXT, keep operation and designation.

    Fires only if B0 >= 0.70, i.e. only if the instruction text is leaking
    executability. Pure, and it returns a copy - the frozen item is never mutated.
    """
    out = dict(item)
    out["instructions"] = []
    for ins in item["instructions"]:
        text = ins["text"]
        for anchor in (ins.get("anchors") or ([ins["anchor"]] if ins.get("anchor") else [])):
            if anchor:
                text = text.replace(anchor, "[QUOTED TEXT REMOVED]")
        for q in ("“", "”"):
            text = text.replace(q, '"')
        out["instructions"].append({**ins, "text": text})
    return out


def assert_prompts_match_agents_md() -> dict:
    """The shipped instruction files and the executed prompts must not drift.

    Deliverable 1 requires *"the instructions that shape each agent"*. Publishing a
    document that no longer matches the code is worse than publishing nothing, because
    it is a claim rather than an omission. Checked before the first call.
    """
    out = {}
    for arm, spec in ARMS.items():
        doc = (REPO / spec["doc"]).read_text(encoding="utf-8")
        for line in spec["system"].strip().splitlines():
            line = line.strip()
            if len(line) < 20:
                continue
            if line not in doc:
                raise ArmError(
                    f"{spec['doc']} does not contain this line of {arm}'s system "
                    f"prompt, so the published instructions have drifted from the "
                    f"executed ones:\n    {line!r}")
        out[arm] = spec["doc"]
    return out


# ============================================================ the run

def load_items(path: Path):
    items = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    return sorted(items, key=lambda i: i["item_id"])       # GOOD.md: sorted item order


def sensitivity_subset(items, n_pairs: int = 10):
    """`GOOD.md` §9: the first `n_pairs` pairs by sorted `(frdoc, positive section)`,
    label-balanced by construction. Fixed before the subset ran."""
    by_key: dict[tuple, dict] = {}
    for it in items:
        by_key.setdefault((it["frdoc"], it["instruction_count"]), {}) \
            .setdefault(it["label"], []).append(it)
    chosen = []
    for key in sorted(by_key):
        group = by_key[key]
        pos = sorted(group.get("WILL_FAIL", []), key=lambda i: i["section"])
        neg = sorted(group.get("WILL_EXECUTE", []), key=lambda i: i["section"])
        for p, n in zip(pos, neg):
            if len(chosen) // 2 >= n_pairs:
                break
            chosen.extend([p, n])
    if len(chosen) != 2 * n_pairs:
        raise ArmError(f"subset is {len(chosen)} items, expected {2 * n_pairs}")
    if sum(1 for i in chosen if i["label"] == "WILL_FAIL") != n_pairs:
        raise ArmError("the subset is not label-balanced")
    return sorted(chosen, key=lambda i: i["item_id"])


def run_arm(key, items, model, rep, temperature, traj_dir, ledger_path,
            strip_anchors=False, tag="") -> dict:
    """One arm, one rep, over every item. Returns {item_id -> raw verdict}.

    An item whose call fails after retries gets **no prediction**, which the scorer
    counts as a FAILURE rather than dropping it. That is deliberate: an arm must not
    be able to raise its accuracy by erroring.
    """
    spec = ARMS[key]
    api_key = load_api_key()
    preds, errors, usage_total = {}, [], {"in": 0, "out": 0}
    arm_label = f"{key}{tag}"
    for item in items:
        prompt_item = strip_quoted_anchors(item) if strip_anchors else item
        prompt = user_prompt(prompt_item, spec["gets_text"])
        run_id = f"{arm_label}__{item['item_id'].replace('|', '_')}__rep{rep}"
        run_id = run_id.replace("/", "_")
        try:
            with RunLogger(arm=arm_label, item_id=item["item_id"], model=model,
                           agent_instructions=spec["system"], delivery="standard",
                           est_usd="0.02", run_id=run_id,
                           traj_dir=traj_dir, ledger_path=ledger_path) as log:
                log.action("message", "messages.create",
                           input={"model": model, "temperature": temperature,
                                  "max_tokens": MAX_TOKENS,
                                  "user_prompt_chars": len(prompt),
                                  "gets_cfr_text": spec["gets_text"],
                                  "quoted_anchors_stripped": strip_anchors,
                                  "user_prompt": prompt})
                try:
                    text, usage, attempts = call_messages(
                        api_key, model=model, user=prompt, system=spec["system"],
                        max_tokens=MAX_TOKENS, temperature=temperature)
                except ApiError as exc:
                    log.tool_response("messages.create", error=str(exc))
                    log.feedback("the call failed after retries; this item gets NO "
                                 "prediction and the scorer counts it as a failure")
                    errors.append({"item_id": item["item_id"], "error": str(exc)[:200]})
                    continue
                log.tool_response("messages.create", output={"text": text})
                for a in attempts:
                    if a["attempt"] > 1:
                        log.retry(reason=str(a["error"])[:200], attempt=a["attempt"])
                preds[item["item_id"]] = text.strip()
                usage_total["in"] += usage["input_tokens"]
                usage_total["out"] += usage["output_tokens"]
                log.finish(verdict=text.strip()[:32],
                           input_tokens=usage["input_tokens"],
                           output_tokens=usage["output_tokens"])
        except SpendCeilingExceeded:
            errors.append({"item_id": item["item_id"], "error": "SPEND CEILING"})
            raise
    return {"arm": arm_label, "model": model, "rep": rep, "predictions": preds,
            "errors": errors, "usage": usage_total,
            "n_items": len(items), "n_predicted": len(preds)}


def run_b0prime(items, model, rep, traj_dir, ledger_path, out_dir,
                samples: int = 3, temperature: float = 1.0) -> dict:
    """**B0-prime** - the COMPUTE-MATCHED CONTROL. `CONTEXT.md` section 4, `plan.md` CH-08.

    B0-agent at A1's token budget, spent on best-of-`samples` self-consistency rather
    than on a tool and a procedure. It exists to answer one specific objection, which
    would otherwise be the first thing a reader says: *"your agent just got more
    compute."*

    THE TIE-BREAK IS PUBLISHED, NOT CHOSEN LATER
    --------------------------------------------
    Majority over `samples` votes; **a tie resolves to `WILL_FAIL`**. That is the same
    rule the CHECKPOINT already applied to aggregate its three reps, restated here
    rather than re-decided, and it is the conservative direction for a defect detector:
    a tie resolves toward flagging, not toward waving through. An unparseable vote is
    NOT a vote and is dropped from the tally; an item where every vote is unparseable
    gets no prediction and `score.py` charges it as a failure.

    TEMPERATURE - A DECLARED, NECESSARY DEVIATION FROM `GOOD.md` section 8
    ---------------------------------------------------------------------
    `GOOD.md` section 8 fixes temperature 0 for every haiku arm. **Self-consistency at
    temperature 0 is a no-op**: three deterministic samples are the same sample, and
    the control would measure nothing while costing three times as much.

    So the two readings are BOTH reported, and only one of them costs money:

      * **B0-prime at temperature 0 IS B0-agent.** Three identical votes, majority
        trivially that vote. Its number is therefore *already published* - 0.6585 - and
        no call is made to re-measure a degeneracy.
      * **B0-prime at temperature 1.0** is the control that can actually exist, and it
        is what this function runs.

    The deviation is disclosed in `QUESTIONS.md` Q22 and in every table B0-prime appears
    in. It is the only arm in the packet not at temperature 0, and saying so is the
    point: a control quietly run at a different temperature would be worse than none.
    """
    spec = ARMS["B0-agent"]
    api_key = load_api_key()
    preds, errors, votes_all = {}, [], {}
    usage_total = {"in": 0, "out": 0}
    for item in items:
        prompt = user_prompt(item, spec["gets_text"])
        votes = []
        for s_i in range(1, samples + 1):
            run_id = (f"B0prime__{item['item_id'].replace('|', '_').replace('/', '_')}"
                      f"__rep{rep}__s{s_i}")
            try:
                with RunLogger(arm="B0prime", item_id=item["item_id"], model=model,
                               agent_instructions=spec["system"], delivery="standard",
                               est_usd="0.02", run_id=run_id, traj_dir=traj_dir,
                               ledger_path=ledger_path) as log:
                    log.action("message", "messages.create",
                               input={"model": model, "temperature": temperature,
                                      "max_tokens": MAX_TOKENS, "sample": s_i,
                                      "of_samples": samples,
                                      "self_consistency": True,
                                      "user_prompt_chars": len(prompt),
                                      "user_prompt": prompt})
                    try:
                        text, usage, attempts = call_messages(
                            api_key, model=model, user=prompt, system=spec["system"],
                            max_tokens=MAX_TOKENS, temperature=temperature)
                    except ApiError as exc:
                        log.tool_response("messages.create", error=str(exc))
                        log.feedback("this SAMPLE failed; it is dropped from the tally "
                                     "and the remaining samples still vote")
                        errors.append({"item_id": item["item_id"], "sample": s_i,
                                       "error": str(exc)[:200]})
                        continue
                    log.tool_response("messages.create", output={"text": text})
                    votes.append(text.strip())
                    usage_total["in"] += usage["input_tokens"]
                    usage_total["out"] += usage["output_tokens"]
                    log.finish(verdict=text.strip()[:32],
                               input_tokens=usage["input_tokens"],
                               output_tokens=usage["output_tokens"])
            except SpendCeilingExceeded:
                errors.append({"item_id": item["item_id"], "error": "SPEND CEILING"})
                raise
        votes_all[item["item_id"]] = votes
        tally = {}
        for v in votes:
            key = v.strip().strip('"').strip("'").upper()
            if key in ("WILL_FAIL", "WILL_EXECUTE"):   # an unparseable vote is not a vote
                tally[key] = tally.get(key, 0) + 1
        if tally:
            top = max(tally.values())
            winners = sorted(k for k, c in tally.items() if c == top)
            preds[item["item_id"]] = ("WILL_FAIL" if len(winners) > 1 and
                                      "WILL_FAIL" in winners else winners[0])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"B0prime-rep{rep}-votes.json").write_text(
        json.dumps(votes_all, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return {"arm": "B0prime", "model": model, "rep": rep, "predictions": preds,
            "errors": errors, "usage": usage_total, "samples_per_item": samples,
            "temperature": temperature,
            "tie_break": "WILL_FAIL (published before the run; same rule as rep "
                         "aggregation; conservative direction for a defect detector)",
            "n_items": len(items), "n_predicted": len(preds)}


def bundle(arm_label: str, rep: int) -> int:
    """Concatenate one arm-rep's per-item trajectories into a single committed JSONL.

    Sorted by filename so the bundle is byte-reproducible (hard rule 9). Every record
    is copied verbatim - this is a container change, not a summary, and a trajectory
    that had been sampled or trimmed would stop being evidence.
    """
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DEFAULT_TRAJ.glob(f"{arm_label}__*__rep{rep}.jsonl"))
    out = BUNDLE_DIR / f"{arm_label}-rep{rep}.jsonl"
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
    ap.add_argument("cmd", choices=["run", "sensitivity", "check", "b0prime"])
    ap.add_argument("--arm", action="append", default=None)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--model", default=HAIKU)
    ap.add_argument("--evalset", default=str(DEFAULT_EVALSET))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--strip-anchors", action="store_true")
    ap.add_argument("--tag", default="")
    args = ap.parse_args(argv)

    docs = assert_prompts_match_agents_md()
    print(f"  prompt/document parity OK: {docs}")
    if args.cmd == "check":
        return 0

    items = load_items(Path(args.evalset))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.cmd == "b0prime":
        out.mkdir(parents=True, exist_ok=True)
        for rep in range(1, args.reps + 1):
            print(f"  running B0prime rep {rep}/{args.reps} over {len(items)} items, "
                  f"best-of-3 self-consistency at temperature 1.0 ...")
            r = run_b0prime(items, args.model, rep, DEFAULT_TRAJ, DEFAULT_LEDGER, out)
            print(f"    predicted {r['n_predicted']}/{r['n_items']}  "
                  f"in={r['usage']['in']:,} out={r['usage']['out']:,}  "
                  f"errors={len(r['errors'])}")
            (out / f"B0prime-rep{rep}.json").write_text(
                json.dumps(r, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n")
            n = bundle("B0prime", rep)
            print(f"    bundled B0prime-rep{rep}.jsonl  {n} records")
        return 0

    if args.cmd == "sensitivity":
        items = sensitivity_subset(items)
        model, reps, temperature, tag = SONNET, 1, None, "-sonnet"
        print(f"  model-sensitivity subset: {len(items)} items on {model}, "
              f"temperature OMITTED (the model rejects the parameter)")
    else:
        model, reps, temperature, tag = args.model, args.reps, 0.0, args.tag

    arms = args.arm or ["B0", "B0-agent"]
    results = []
    for arm in arms:
        for rep in range(1, reps + 1):
            print(f"  running {arm}{tag} rep {rep}/{reps} over {len(items)} items ...")
            r = run_arm(arm, items, model, rep, temperature, DEFAULT_TRAJ,
                        DEFAULT_LEDGER, strip_anchors=args.strip_anchors, tag=tag)
            print(f"    predicted {r['n_predicted']}/{r['n_items']}  "
                  f"in={r['usage']['in']:,} out={r['usage']['out']:,}  "
                  f"errors={len(r['errors'])}")
            results.append(r)
            name = f"{arm}{tag}{'-stripped' if args.strip_anchors else ''}-rep{rep}.json"
            (out / name).write_text(
                json.dumps(r, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n")
    print(f"  wrote {len(results)} run file(s) to {out}")
    for arm in arms:
        for rep in range(1, reps + 1):
            n = bundle(f"{arm}{tag}", rep)
            print(f"  bundled {arm}{tag}-rep{rep}.jsonl  {n} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
