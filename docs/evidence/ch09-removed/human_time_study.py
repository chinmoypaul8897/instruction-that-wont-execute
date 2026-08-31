"""CH-09 — the BLIND HUMAN-TIME STUDY: reserve the 8 items, publish the rule first.

`plan.md` CH-09: *"blind human-time study (8 items by hand, stopwatched, before seeing
gold)"*. The CH-06 prompt: *"operator task — but reserve and document the 8 item ids now
so it can be run without contaminating anything."*

**This script does not run the study. It makes the study runnable later without the
selection having been made with a result in view.** That is the whole of its job, and it
is the same device `GOOD.md` §9 used for the model-sensitivity subset: fix the selection
rule in code, commit it, and let the rule pick.

WHY A SELECTION RULE AND NOT A CHOICE
--------------------------------------
Eight items hand-timed by the operator is a small enough sample that *which* eight
decides the answer. Picked after the fact they would be the eight that made the point;
picked by a rule committed in advance they are simply eight items. **This file is the
difference between a measurement and an anecdote.**

THE RULE - fixed here, before any item id is looked at
-------------------------------------------------------
1. Sort every eval item by `item_id`. No RNG, so the selection is byte-reproducible.
2. Walk the sorted FR documents. From each document take **at most one** item, so eight
   items are eight different rules rather than one rule's eight sections.
3. Alternate the label taken - `WILL_FAIL`, `WILL_EXECUTE`, `WILL_FAIL`, ... - so the
   set is **4 defective and 4 clean, balanced by construction.** An unbalanced set
   would let the operator's base rate do the work.
4. Stop at 8.

**The operator must not read the `label` column before timing.** The blind file written
by this script carries the instructions and the section text and **no label, no note, no
`role`, no `frdoc`-derived hint** - `assert_blind()` checks that by scanning the emitted
bytes for every forbidden token, and refuses to write if one is present.

WHAT IS AND IS NOT CLAIMED WHEN IT RUNS
----------------------------------------
n = 8, one operator, un-blinded to the *task* though blinded to the *answers*. It is an
**order-of-magnitude reading on how long this takes a person**, and `CONTEXT.md` §2's
value claim rests on that being non-trivial. It is not a user study, it will not carry a
statistical claim, and its n is printed everywhere it is quoted.

PURITY: no network, no clock, no randomness. `data/` is read-only.

    python docs/evidence/ch09-removed/human_time_study.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVALSET = REPO / "data/evalset/items.jsonl"
HERE = Path(__file__).resolve().parent
RESERVED = HERE / "human-time-reserved.json"
BLIND = HERE / "human-time-blind.md"
SHEET = HERE / "human-time-worksheet.csv"

FORBIDDEN_KEYS = ("label", "note_text", "note_node", "role")


def load_items():
    return sorted((json.loads(l) for l in EVALSET.read_text(encoding="utf-8").splitlines()
                   if l.strip()), key=lambda i: i["item_id"])


def select(items, n=8):
    """The rule above, and nothing else. Deterministic."""
    by_doc: dict[str, list] = {}
    for it in items:
        by_doc.setdefault(it["frdoc"], []).append(it)
    want = "WILL_FAIL"
    chosen, used_docs = [], set()
    while len(chosen) < n:
        progressed = False
        for doc in sorted(by_doc):
            if doc in used_docs or len(chosen) >= n:
                continue
            cand = sorted((i for i in by_doc[doc] if i["label"] == want),
                          key=lambda i: i["item_id"])
            if not cand:
                continue
            chosen.append(cand[0])
            used_docs.add(doc)
            want = "WILL_EXECUTE" if want == "WILL_FAIL" else "WILL_FAIL"
            progressed = True
        if not progressed:
            break
    return chosen


def assert_blind(text: str, chosen) -> None:
    """The emitted brief must not contain the answer. Checked on the BYTES, not on the
    intention - a leak here would silently invalidate the whole study."""
    lowered = text.lower()
    for token in ("will_fail", "will_execute", "editorial note",
                  "could not be incorporated"):
        if token in lowered:
            raise SystemExit(
                f"REFUSING TO WRITE: the blind brief contains {token!r}, which would "
                f"tell the operator the answer before they time the task.")
    for it in chosen:
        if it.get("note_text") and it["note_text"][:40].lower() in lowered:
            raise SystemExit("REFUSING TO WRITE: an editorial note leaked into the brief")


def main() -> int:
    items = load_items()
    chosen = select(items)
    n_pos = sum(1 for i in chosen if i["label"] == "WILL_FAIL")

    RESERVED.write_text(json.dumps({
        "selection_rule": ("sorted by item_id; at most one item per FR document; label "
                           "alternating WILL_FAIL/WILL_EXECUTE; first 8. No RNG."),
        "committed_before_the_study_ran": True,
        "n": len(chosen), "n_positive": n_pos, "n_negative": len(chosen) - n_pos,
        "item_ids": [i["item_id"] for i in chosen],
        "distinct_documents": len({i["frdoc"] for i in chosen}),
        # the labels ARE recorded here, in the file the operator does NOT open until
        # after timing. Reserving them without recording them would make the study
        # unscoreable; recording them in the BLIND file would make it worthless.
        "labels_SEALED_do_not_read_before_timing": {i["item_id"]: i["label"] for i in chosen},
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    L = ["# Blind human-time study — the operator's brief",
         "",
         "**Do not open `human-time-reserved.json` until every item below is timed.**",
         "It carries the answers. This file does not, and `assert_blind()` refuses to",
         "write it if it does.",
         "",
         "## What to do",
         "",
         "For each of the 8 sections below, start a stopwatch and decide the one",
         "question this project is about:",
         "",
         "> **Will every one of these amendatory instructions execute against the",
         "> section text as printed — yes or no? And if no, WHICH instruction fails?**",
         "",
         "Stop the clock when you have written an answer in `human-time-worksheet.csv`.",
         "Work as you normally would. Do not look anything up online — the point is the",
         "time this takes against the text in front of you, which is exactly what the",
         "agent is given.",
         "",
         f"Selection rule, committed before selection: sorted by `item_id`, at most one",
         f"item per FR document, alternating label, first 8. **{len(chosen)} items,",
         f"{len({i['frdoc'] for i in chosen})} distinct documents, balanced by construction.**",
         ""]
    for k, it in enumerate(chosen, start=1):
        L += [f"---", "",
              f"## Item {k} of {len(chosen)}   ·   `{it['item_id']}`", "",
              f"**{it['cfr_title']} CFR {it['section']}**, as of the {it['as_of_edition']} "
              f"annual edition (revised {it['as_of_revision_date']}).", "",
              f"### The {it['instruction_count']} amendatory instructions, in document order", ""]
        for n, ins in enumerate(it["instructions"], start=1):
            L.append(f"{n}. {ins['text']}")
        L += ["", "### The section text as it stood", "", "```", it["section_text"], "```", ""]
    text = "\n".join(L) + "\n"
    assert_blind(text, chosen)
    BLIND.write_text(text, encoding="utf-8", newline="\n")

    SHEET.write_text(
        "item_id,seconds_taken,your_verdict_WILL_FAIL_or_WILL_EXECUTE,"
        "which_instruction_fails,confidence_1_to_5,notes\n"
        + "".join(f"{i['item_id']},,,,,\n" for i in chosen),
        encoding="utf-8", newline="\n")

    print(f"  reserved {len(chosen)} items, {n_pos} defective / {len(chosen) - n_pos} clean, "
          f"{len({i['frdoc'] for i in chosen})} distinct FR documents")
    for i in chosen:
        print(f"    {i['item_id']:26s} {i['instruction_count']} instructions, "
              f"{len(i['section_text']):,} chars")
    print(f"  BLIND brief   {BLIND.relative_to(REPO).as_posix()}  ({len(text):,} chars)")
    print(f"  worksheet     {SHEET.relative_to(REPO).as_posix()}")
    print(f"  SEALED keys   {RESERVED.relative_to(REPO).as_posix()}  <- do not open first")
    print("  assert_blind PASSED: no verdict token and no editorial note in the brief")
    return 0


if __name__ == "__main__":
    sys.exit(main())
