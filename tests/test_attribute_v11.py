"""CH-03 1a - the v1.1 attributor against goldens hand-computed before the code.

Every expected value here is transcribed from `docs/evidence/ch03-evalset/goldens.md`
section G-C, which was committed at c685e80, BEFORE `src/attribute_v11.py` existed.
Hard rule 4: a test whose expected value came from the code it tests proves nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from attribute_amdpars import AttributorError, completeness  # noqa: E402
from attribute_v11 import CONFIGS, attribute_cfg, find_sections_cfg  # noqa: E402

# --------------------------------------------------------------- golden G-C
# Six AMDPAR texts in document order, with the <REGTEXT> PART each sits in.
GC_TEXTS = [
    "1. The authority citation for part 52 continues to read as follows:",
    "2. Section 52.2320 is amended by revising paragraph (c).",
    "a. Revise paragraph (c)(1);",
    "3. Appendix A to part 75 is amended by revising the title of section 1.1.",
    "4. Amend § 75.6 by removing paragraph (b).",
    "b. Remove paragraph (c).",
]
GC_PARTS = ["52", "52", "52", "75", "75", "75"]

# G-C's attribution table, hand-traced. None == unattributable.
GC_SECTIONS = {
    "spec_literal": [None, None, None, None, "75.6", "75.6"],
    "extended_ci":  [None, "52.2320", "52.2320", "1.1", "75.6", "75.6"],
    "extended_cs":  [None, "52.2320", "52.2320", "52.2320", "75.6", "75.6"],
    "v11":          [None, "52.2320", "52.2320", None, "75.6", "75.6"],
}

# G-C's parse table - detector-independent.
GC_PARSED = [False, True, True, False, True, True]
GC_OPERATION = [None, "revise", "revise", "revise", "remove", "remove"]
GC_DESIGNATION = [None, "(c)", "(c)(1)", None, "(b)", "(c)"]

# G-C's expected totals.
GC_TOTALS = {
    "spec_literal": {"attributed": 2, "attribution_rate": 2 / 6,
                     "complete": 2, "completeness": 2 / 6, "unattributable": 4},
    "extended_ci":  {"attributed": 5, "attribution_rate": 5 / 6,
                     "complete": 4, "completeness": 4 / 6, "unattributable": 1},
    "extended_cs":  {"attributed": 5, "attribution_rate": 5 / 6,
                     "complete": 4, "completeness": 4 / 6, "unattributable": 1},
    "v11":          {"attributed": 4, "attribution_rate": 4 / 6,
                     "complete": 4, "completeness": 4 / 6, "unattributable": 2},
}


@pytest.mark.parametrize("config", sorted(CONFIGS))
def test_gc_attribution_matches_the_hand_trace(config):
    rows = attribute_cfg(GC_TEXTS, GC_PARTS, config)
    assert [r["section"] for r in rows] == GC_SECTIONS[config], (
        f"{config}: attribution diverges from goldens.md G-C")


def test_gc_parse_is_detector_independent():
    for config in CONFIGS:
        rows = attribute_cfg(GC_TEXTS, GC_PARTS, config)
        assert [r["parsed"] for r in rows] == GC_PARSED
        assert [r["operation"] for r in rows] == GC_OPERATION
        assert [r["designation"] for r in rows] == GC_DESIGNATION


@pytest.mark.parametrize("config", sorted(CONFIGS))
def test_gc_totals_match_the_hand_computed_table(config):
    got = completeness(attribute_cfg(GC_TEXTS, GC_PARTS, config))
    want = GC_TOTALS[config]
    assert got["total"] == 6
    assert got["attributed"] == want["attributed"]
    assert got["complete"] == want["complete"]
    assert got["unattributable"] == want["unattributable"]
    assert got["attribution_rate"] == pytest.approx(want["attribution_rate"])
    assert got["completeness"] == pytest.approx(want["completeness"])


def test_gc_case_sensitivity_moves_element_4_without_changing_the_count():
    """goldens.md G-C claim 1, and it is SPEC-FIX-1's sabotage finding in miniature.

    extended_ci and extended_cs BOTH attribute 5 of 6. They disagree about where
    element 4 goes - `1.1` versus a carried-forward `52.2320`. Attribution rate is
    blind to the difference; only looking at WHICH section shows it.
    """
    ci = attribute_cfg(GC_TEXTS, GC_PARTS, "extended_ci")
    cs = attribute_cfg(GC_TEXTS, GC_PARTS, "extended_cs")
    assert completeness(ci)["attributed"] == completeness(cs)["attributed"] == 5
    assert ci[3]["section"] == "1.1"
    assert cs[3]["section"] == "52.2320"
    assert ci[3]["section"] != cs[3]["section"]


def test_gc_v11_scores_lower_on_attribution_than_what_ch02_shipped():
    """goldens.md G-C claim 3, pre-registered so it is not a later surprise."""
    ci = completeness(attribute_cfg(GC_TEXTS, GC_PARTS, "extended_ci"))
    v11 = completeness(attribute_cfg(GC_TEXTS, GC_PARTS, "v11"))
    assert v11["attribution_rate"] < ci["attribution_rate"]
    assert v11["completeness"] == pytest.approx(ci["completeness"])


def test_part_reset_fires_exactly_at_the_boundary():
    rows = attribute_cfg(GC_TEXTS, GC_PARTS, "v11")
    assert [r["part_reset_fired"] for r in rows] == [False, False, False,
                                                     True, False, False]
    # and it does NOT fire under the three configs that do not specify it
    for config in ("spec_literal", "extended_ci", "extended_cs"):
        assert not any(r["part_reset_fired"]
                       for r in attribute_cfg(GC_TEXTS, GC_PARTS, config))


def test_reset_does_not_swallow_a_section_named_on_the_boundary_element():
    """The reset happens BEFORE the element is read, so an element that both crosses
    a boundary AND names its own section still names it. Without this ordering the
    reset would delete a correct attribution."""
    rows = attribute_cfg(
        ["1. Amend § 52.10 by revising paragraph (a).",
         "2. Amend § 75.6 by revising paragraph (b)."],
        ["52", "75"], "v11")
    assert [r["section"] for r in rows] == ["52.10", "75.6"]
    assert rows[1]["part_reset_fired"] is True


def test_word_form_case_sensitivity_at_the_regex_level():
    assert find_sections_cfg("Section 90.209 is amended", True, True)[0] == ["90.209"]
    assert find_sections_cfg("section 90.209 is amended", True, True)[0] == []
    assert find_sections_cfg("section 90.209 is amended", True, False)[0] == ["90.209"]
    assert find_sections_cfg("Sections 90.209 and 90.210", True, True)[0] == ["90.209"]
    # the sign form is unaffected by the case rule
    assert find_sections_cfg("§ 90.209 is amended", False, True)[0] == ["90.209"]


def test_unknown_config_is_refused_not_guessed():
    with pytest.raises(AttributorError):
        attribute_cfg(["x"], ["1"], "extended")


def test_parts_length_mismatch_is_refused():
    with pytest.raises(AttributorError):
        attribute_cfg(["a", "b"], ["1"], "v11")


def test_document_order_is_the_contract():
    """Reversing the input reverses the carry-forward. Stated as a test because
    CONTEXT.md section 8 step 1 makes document order load-bearing, and a future
    refactor that sorts the list would silently destroy the mechanism."""
    forward = attribute_cfg(GC_TEXTS, GC_PARTS, "v11")
    backward = attribute_cfg(GC_TEXTS[::-1], GC_PARTS[::-1], "v11")
    assert [r["section"] for r in forward] != [r["section"] for r in backward][::-1]
