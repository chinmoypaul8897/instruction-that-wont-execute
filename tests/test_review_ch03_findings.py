"""CH-03 ADVERSARIAL REVIEW - the two decisive findings, pinned as KEPT TESTS.

These tests are RED on purpose. They were written by the CH-03 reviewer, they assert
the behaviour the spec requires, and they fail against the code and the freeze as
committed at `067a9d9`. `CLAUDE.md` hard rule 5: *"A red result ships as red."*
`docs/reviews/REVIEW_CH-03.md` carries the full evidence; the runnable probes are in
`docs/reviews/ch03-probe/`.

Do not weaken either assertion. Each flips to green the moment the defect is fixed:

  F1  choose the negative by a rule that is neutral in section-sort order
  F2  treat a volume whose <PARTS> header is absent as covering the whole title
      (single-volume titles carry no <PARTS> element at all)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

ITEMS = REPO / "data/evalset/items.jsonl"
needs_freeze = pytest.mark.skipif(not ITEMS.exists(), reason="freeze not built")


@needs_freeze
def test_FINDING_SEVERE_a_sort_order_script_must_not_beat_the_eval_set():
    """A six-line script reading ONLY `frdoc` and `section` scores 0.8158 on the
    primary metric - above `GOOD.md`'s A1 bar of 0.80 and above B0-agent's predicted
    0.75. `CONTEXT.md` section 8: exact count matching is non-negotiable *"unmatched,
    a hardcoded threshold on instruction count beats the agent, and that is precisely
    how an earlier candidate died."* The count is matched; the SELECTION is not.

    Cause: `src/eval_set.py:138` takes `free[0]` - the sorted-FIRST count-matched
    sibling - as the negative, while the positive is a given section. Negatives
    therefore sort before their positives 31 times in 38 (binomial p = 0.00032).
    """
    items = [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    blocks = defaultdict(list)
    for i in items:
        blocks[i["frdoc"]].append(i)

    right = 0
    for grp in blocks.values():
        ordered = sorted(grp, key=lambda i: i["section"])
        half = len(ordered) // 2
        for j, i in enumerate(ordered):
            guess = "WILL_EXECUTE" if j < half else "WILL_FAIL"
            right += guess == i["label"]
    acc = right / len(items)
    assert acc <= 0.60, (
        f"a label-blind section-sort script scores {acc:.4f} ({right}/{len(items)}) "
        "on the primary metric - the eval set is beatable without a model, without "
        "the CFR text and without the instructions")


def test_FINDING_MAJOR_a_volume_with_no_PARTS_header_must_not_exclude_everything():
    """`CFR-2016-title13-vol1.xml` is a single-volume title and carries NO `<PARTS>`
    element anywhere in its 4,157,015 bytes. `parse_parts_header("")` returns
    `part_lo=None`, `volume_covers` then returns `(False, False)` for every part, and
    `candidate_volumes` returns `[]` - so the DECLARED G-G2 fallback ("every other
    volume covering that part is searched before the item is excluded") cannot fire,
    because it is itself gated on `covers_part`.

    Consequence, verified against the real bytes: FR Doc 2016-16399's pair - positive
    13 CFR 125.6, negative 13 CFR 121.1001 - is present exactly once each in the 2016
    edition, strips to CITA=1 each and passes the leakage test, yet was excluded on
    the `section-not-in-as-of-edition` rung with the reason
    `no-volume-covers-this-part`. The frozen n should be 39 pairs / 78 items.

    goldens.md G-G2, verbatim: *"a wrong answer that presents as a smaller n rather
    than as an error"* - which is the failure this project exists to catch.
    """
    from cfr_pit import parse_parts_header, volume_covers

    rng = parse_parts_header("")
    assert volume_covers(rng, "125", "125.6") == (True, True), (
        "a volume that declares no part range must be searched, not silently "
        f"skipped; volume_covers returned {volume_covers(rng, '125', '125.6')}")
