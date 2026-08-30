"""CH-03 RE-REVIEW (round 2) - the findings that survived the fix, as KEPT TESTS.

Written by the round-2 reviewer. `docs/reviews/REVIEW_CH-03-round2.md` carries the
verdict; the runnable probes are in `docs/reviews/ch03-probe2/`.

Two of these are RED on purpose. `CLAUDE.md` hard rule 5: *"A red result ships as
red."* Do not weaken an assertion to get green.

  R1  the negative-selection rule must be unbiased WHEN RUN, not merely in the file
      it once produced. GREEN on the code as shipped at 76e2e4b - it exists because
      five separate mutations of that rule (including a literal revert to the defect
      that failed the gate) left the whole suite 275-green. See
      `docs/reviews/ch03-probe2/mutate2.txt`.

  R2  RED. `items_whose_UNSTRIPPED_text_would_have_leaked` is counted over every item
      that reached the leakage stage (86) and published against `items_total` (82).
      Over the 82 frozen items the number is 3, not 5.

  R3  RED. `src/eval_set.py`'s module docstring still declares the OLD, falsified
      rule ("the FIRST in sorted order ... independent of any label") that the body
      of the same file replaced.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

ITEMS = REPO / "data/evalset/items.jsonl"
LEAKAGE = REPO / "data/evalset/leakage.json"
V11 = REPO / "data/attribution-v11/amdpars_v11.jsonl"
CITATIONS = REPO / "data/amdpars/citations.json"
needs_freeze = pytest.mark.skipif(not ITEMS.exists(), reason="freeze not built")
needs_inputs = pytest.mark.skipif(not (V11.exists() and CITATIONS.exists()),
                                  reason="CH-02/CH-03 inputs not present")


def _binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    probs = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = probs[k]
    return sum(x for x in probs if x <= obs * (1 + 1e-12))


@needs_inputs
def test_R1_the_negative_selection_rule_is_unbiased_WHEN_RUN_not_only_in_the_freeze():
    """The kept round-1 test asserts on `data/evalset/items.jsonl`. A source mutation
    does not touch that file, so the rule that produced it is unguarded: reverting
    `src/eval_set.py` to `negative = free[0]` leaves the suite green while the rebuilt
    pairing goes to 36/50 negatives-sort-before at p = 0.0026.

    This test runs `build_pairs` against the real corpus and asserts the property the
    fix claims, so a change to the RULE is caught by the RULE's own test.
    """
    from eval_set import build_pairs, instruction_counts, load_jsonl
    from cfr_pit import section_sort_key

    records = load_jsonl(V11)
    citations = json.loads(CITATIONS.read_text(encoding="utf-8"))
    counts = instruction_counts(records, "v11")
    defects = sorted({(c["frdoc"], c["section"]) for c in citations.values()
                      if c.get("status") == "resolved"})
    pairs, _ = build_pairs(counts, defects, tolerance=0)
    before = sum(1 for p in pairs
                 if section_sort_key(p["negative"]) < section_sort_key(p["positive"]))
    p = _binom_two_sided(before, len(pairs))
    assert p >= 0.05, (
        f"the negative-selection rule is biased in section-sort order: "
        f"{before}/{len(pairs)} negatives sort before their positive, exact two-sided "
        f"binomial p = {p:.6f}. This is the CH-03 gate defect (review finding F1)."
    )


@needs_freeze
def test_R2_the_unstripped_leak_count_is_measured_over_the_ITEMS_IT_IS_PUBLISHED_AGAINST():
    """`data/evalset/leakage.json` reports
    `items_whose_UNSTRIPPED_text_would_have_leaked` beside `items_total`, and
    `docs/evidence/ch03-evalset/README.md` prints the pair as "5 of 82 items".

    `src/eval_set.py:450` increments the counter for every member of every pair that
    reached the leakage stage - including the two pairs then dropped on the
    `leakage-test-failed-after-strip` rung. The numerator therefore covers 86 items
    and the denominator 82. Re-derived on the real govinfo bytes, the count over the
    82 FROZEN items is 3. `docs/reviews/ch03-probe2/rederive.txt`.

    plan.md CH-04 calls this number "a publishable result about the corpus", so it
    has to be a rate over a stated population.
    """
    from cfr_pit import (eligible_sections, leakage_violations, section_text,
                         sectno_number, strip_leakage)
    import xml.etree.ElementTree as ET

    raw = REPO / "data/raw/cfr"
    items = [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    if not all((raw / i["volume"]).exists() for i in items):
        pytest.skip("data/raw/cfr is git-ignored; run refetch.py to re-derive")

    roots: dict = {}
    leaked = 0
    for it in items:
        path = raw / it["volume"]
        if path not in roots:
            roots[path] = ET.parse(str(path)).getroot()
        sec = next(s for s in eligible_sections(roots[path])
                   if sectno_number(s) == it["section"])
        if leakage_violations(section_text(sec), it["fr_citation"]):
            leaked += 1

    d = json.loads(LEAKAGE.read_text(encoding="utf-8"))
    assert d["items_total"] == len(items)
    assert d["items_whose_UNSTRIPPED_text_would_have_leaked"] == leaked, (
        f"leakage.json publishes "
        f"{d['items_whose_UNSTRIPPED_text_would_have_leaked']} of {d['items_total']}, "
        f"but only {leaked} of the {len(items)} FROZEN items leak unstripped; the "
        f"extra counts come from pairs that were dropped before the freeze"
    )


def test_R3_the_module_docstring_does_not_declare_the_rule_the_code_replaced():
    """`src/eval_set.py:23` still says the negative is "the FIRST in sorted order
    among free count-matched siblings - declared in the pre-registration, so it is
    independent of any label". The body at :177-189 implements the balanced rule, and
    the pre-registration's ERRATA E-1 records that "independent of any label" was
    tested and found FALSE. Two shipping statements of the same rule disagree -
    `CLAUDE.md` hard rule 16's failure mode, in one file.
    """
    head = (REPO / "src/eval_set.py").read_text(encoding="utf-8")[:2000]
    assert "the FIRST in sorted" not in head, (
        "the module docstring still declares the pre-fix negative-selection rule and "
        "repeats its falsified justification"
    )
