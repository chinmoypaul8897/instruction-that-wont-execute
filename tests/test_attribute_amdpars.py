"""CH-02 tests.

Every expected value in the golden section below is quoted from
`docs/evidence/ch02-attributor/goldens.md`, which was committed at 98f1cff - BEFORE
`src/attribute_amdpars.py` existed. None of these numbers came from the code they test
(hard rule 4). Where the parser and the golden disagreed, the golden was NOT edited:
the divergence is recorded as an ERRATUM in the goldens file and the test asserts the
measured value while naming the erratum, exactly as CH-01 did for its G2.

Tests that need the 264 MB of raw FR issues are marked `skipif`, so a clean clone runs
the pure half of the suite with no network and no corpus.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import attribute_amdpars as A  # noqa: E402

RAW = REPO / "data/raw/fr"
OUT = REPO / "data/amdpars"
needs_raw = pytest.mark.skipif(not RAW.exists(), reason="data/raw/fr absent (git-ignored)")
needs_freeze = pytest.mark.skipif(not (OUT / "manifest.json").exists(),
                                  reason="data/amdpars not built")

G1 = ("FR-2020-07-16.xml", 43139, "90.213", "2020-11897", 28)
G2 = ("FR-2021-02-04.xml", 8130, "1468.3", "2021-02268", 29)
G3 = ("FR-2016-10-04.xml", 68317, "236.2", "2016-23968", 40)


# ===================================================== pure: quotes (goldens P1)

def test_split_quotes_lifts_curly_spans_and_leaves_a_separator():
    text = "In paragraph (1), remove the words “farm or ranch or” and add “farm, ranch, or”."
    dequoted, anchors, unclosed = A.split_quotes(text)
    assert anchors == ["farm or ranch or", "farm, ranch, or"]
    assert unclosed is False
    assert "farm or ranch or" not in dequoted
    assert "remove the words   and add" in " ".join(dequoted.split(" "))


def test_split_quotes_reports_an_unclosed_quote_rather_than_guessing():
    dequoted, anchors, unclosed = A.split_quotes("remove “never closed")
    assert unclosed is True
    assert anchors == ["never closed"]
    assert "never closed" not in dequoted


def test_a_quoted_cross_reference_cannot_become_the_designation():
    """Goldens P1/P5, golden G2 element 10. The paragraph being amended is (a)(3)(iii);
    (a)(4) and (a)(5) are cross-references being inserted, inside quotes."""
    text = ("3. Amend § 1468.6 in paragraph (a)(3)(iii) by removing the cross reference "
            "“paragraph (a)(4)” and add in its place add the cross reference "
            "“paragraph (a)(5)”.")
    rec = A.parse_amdpar(text)
    assert rec["designation"] == "(a)(3)(iii)"
    assert rec["designations"] == ["(a)(3)(iii)"]
    assert rec["anchor"] == "paragraph (a)(4)"


# ===================================================== pure: the section (goldens P2)

@pytest.mark.parametrize("cite,expected", [
    ("Amend § 1468.3 as follows:", "1468.3"),
    ("revise § 90.213(a) to read", "90.213"),          # (a) is a paragraph, not the section
    ("Amend § 1.367(a)-8 by", "1.367(a)-8"),
    ("§ 1.1400Z2(b)-1 is amended", "1.1400Z2(b)-1"),
    ("In § 1.401(a)(31)-1 revise", "1.401(a)(31)-1"),
    ("§ 1.199A-0 is revised", "1.199A-0"),
    ("Amend § 1.1502-47 by", "1.1502-47"),
    ("§ 210.8-01 is amended", "210.8-01"),
    ("Amend § 6.302-1 by", "6.302-1"),
    ("§§ 90.209 and 90.213 are amended", "90.209"),
])
def test_section_pattern_does_not_truncate_title_26_numbers(cite, expected):
    """CONTEXT.md section 8's own regex stops at `1.367` and drops `(a)-8`. Truncation
    in exactly this position is what section 8 records as having produced 0.46
    completeness once. Goldens P2 fixes the pattern; this is its table."""
    sections, _ = A.find_sections(cite, "extended")
    assert sections[0] == expected


def test_paragraph_parens_are_absorbed_into_a_section_only_with_a_hyphen_tail():
    assert A.find_sections("§ 90.213(a)", "extended")[0] == ["90.213"]
    assert A.find_sections("§ 1.367(a)-8", "extended")[0] == ["1.367(a)-8"]


def test_the_two_detectors_differ_exactly_on_the_word_form():
    word = "2. Section 1.907 is amended by revising the definition"
    sign = "3. In § 1.9005 add paragraph (nn)"
    assert A.find_sections(word, "spec_literal")[0] == []
    assert A.find_sections(word, "extended")[0] == ["1.907"]
    assert A.find_sections(sign, "spec_literal")[0] == ["1.9005"]
    assert A.find_sections(sign, "extended")[0] == ["1.9005"]


def test_an_unknown_detector_raises_rather_than_defaulting():
    with pytest.raises(A.AttributorError):
        A.find_sections("§ 1.1", "whatever")


# ===================================================== pure: operation (goldens P4)

@pytest.mark.parametrize("text,op", [
    ("2. Amend § 236.1 by revising the last two sentences", "revise"),
    ("3. Amend § 236.2 by:", "amend"),
    ("a. Revise paragraph (b)(11); and", "revise"),
    ("e. Redesignating paragraphs (n) through (p) as paragraphs (o) through (q).", "redesignate"),
    ("c. Add a new paragraph (e)(4)(iii).", "add"),
    ("In paragraph (1), remove the words X and add Y", "remove"),
    ("1. The authority citation for part 90 continues to read as follows:", None),
    ("2.106 Table of Frequency Allocations.", None),
    ("b. In paragraph (a):", None),
])
def test_amend_is_a_fallback_not_a_first_match(text, op):
    assert A.find_operation(text) == op


def test_operation_word_stems_do_not_fire_inside_longer_words():
    """`address` is not `add`; `in addition` is not `add`. Both appear in FR prose."""
    assert A.find_operation("Correct the address of the office.") is None
    assert A.find_operation("In addition, the agency notes the following.") is None


# ===================================================== pure: completeness (goldens P6)

def test_completeness_requires_an_operation_and_one_of_anchor_or_designation():
    whole_section = A.parse_amdpar("21. Section 90.601 is revised to read as follows:")
    assert whole_section["operation"] == "revise"
    assert whole_section["anchor"] is None and whole_section["designation"] is None
    assert whole_section["parsed"] is False          # operation alone is not the bar

    designation_only = A.parse_amdpar("b. In paragraph (a):")
    assert designation_only["designation"] == "(a)"
    assert designation_only["operation"] is None
    assert designation_only["parsed"] is False       # nor is a designation alone


def test_attribution_and_unattributable_always_sum_to_the_total():
    texts = ["1. The authority citation continues to read as follows:",
             "2. Amend § 100.1 as follows:",
             "a. Revise paragraph (b)."]
    c = A.completeness(A.attribute(texts, "spec_literal"))
    assert c["attributed"] + c["unattributable"] == c["total"] == 3
    assert c["unattributable"] == 1                  # nothing named before element 1


def test_completeness_raises_rather_than_asserts_on_an_impossible_tally():
    """`python -O` strips `assert`. A load-bearing count that stops checking itself
    under an optimisation flag is the silent green this project exists to expose."""
    bad = [{"attributed": True, "unattributable": True, "parsed": True, "complete": True,
            "part_mismatch": False, "unclosed_quote": False, "operation": "add"}]
    with pytest.raises(A.AttributorError):
        A.completeness(bad)


# ===================================================== pure: carry-forward

def test_carry_forward_attributes_lettered_children_to_the_last_named_section():
    """CONTEXT.md section 8's worked example, verbatim."""
    texts = ["6. Amend § 1468.23 as follows:",
             "a. Revise paragraph (b)(2);",
             "b. Remove paragraph (c).",
             "7. Amend § 1468.25 by revising paragraph (a)."]
    recs = A.attribute(texts, "spec_literal")
    assert [r["section"] for r in recs] == ["1468.23", "1468.23", "1468.23", "1468.25"]
    assert [r["names_section"] for r in recs] == [True, False, False, True]


def test_document_order_is_the_mechanism_reordering_changes_the_answer():
    """Section 8: 'Order is the whole mechanism; any reordering breaks it.' A test that
    did not demonstrate this would leave the project's central claim unpinned."""
    texts = ["1. Amend § 100.1 as follows:", "a. Revise paragraph (b).",
             "2. Amend § 100.2 as follows:", "a. Revise paragraph (c)."]
    forward = [r["section"] for r in A.attribute(texts, "spec_literal")]
    shuffled = [r["section"] for r in A.attribute(
        [texts[0], texts[2], texts[1], texts[3]], "spec_literal")]
    assert forward == ["100.1", "100.1", "100.2", "100.2"]
    assert shuffled == ["100.1", "100.2", "100.2", "100.2"]
    assert forward != shuffled


def test_an_element_before_any_named_section_is_unattributable_never_guessed():
    recs = A.attribute(["a. Revise paragraph (b).", "1. Amend § 100.1 as follows:"],
                       "spec_literal")
    assert recs[0]["unattributable"] is True and recs[0]["section"] is None
    assert recs[0]["complete"] is False               # unattributable can never complete


def test_current_section_does_not_reset_at_a_part_boundary_but_the_mismatch_is_recorded():
    """Goldens P7. Section 8 specifies no reset, so none is added - but carrying 27.13
    into part 90 is wrong, and the record says so instead of hiding it."""
    texts = ["12. Section 27.13 is amended by adding paragraph (n).",
             "13. The authority citation for part 90 continues to read as follows:"]
    recs = A.attribute(texts, "extended", ["27", "90"])
    assert recs[1]["section"] == "27.13"
    assert recs[1]["part_mismatch"] is True
    assert recs[0]["part_mismatch"] is False


def test_attribute_rejects_a_parts_list_of_the_wrong_length():
    with pytest.raises(A.AttributorError):
        A.attribute(["a", "b"], "extended", ["1"])


# ===================================================== pure: the pair yield

def test_pair_yield_matches_exactly_and_a_near_miss_does_not_count():
    """`CONTEXT.md` section 8: negatives are matched EXACTLY on instruction count,
    'non-negotiable - unmatched, a hardcoded threshold on instruction count beats the
    agent'. This is the test `plan.md`'s CH-03 card requires to exist."""
    docs = {"D1": {"1.1": 3, "1.2": 3, "1.3": 4}}
    exact = A.pair_yield(docs, [("D1", "1.1")], tolerance=0)
    assert exact["with_match"] == 1
    assert exact["rows"][0]["matched_examples"] == ["1.2"]      # 1.3 has 4, not 3

    docs2 = {"D2": {"2.1": 3, "2.2": 4}}
    still_exact = A.pair_yield(docs2, [("D2", "2.1")], tolerance=0)
    assert still_exact["with_match"] == 0 and still_exact["yield"] == 0.0
    loose = A.pair_yield(docs2, [("D2", "2.1")], tolerance=1)
    assert loose["with_match"] == 1
    # The looser rule inflates n. It is computed as a diagnostic and NOT adopted.
    assert still_exact["yield"] < loose["yield"]


def test_a_sibling_carrying_its_own_defect_note_is_not_a_negative():
    docs = {"D": {"1.1": 2, "1.2": 2}}
    y = A.pair_yield(docs, [("D", "1.1"), ("D", "1.2")], tolerance=0)
    assert y["with_match"] == 0            # each is the other's only count match
    assert y["rows"][0]["sibling_sections"] == 0


def test_pair_yield_rejects_a_negative_tolerance():
    with pytest.raises(A.AttributorError):
        A.pair_yield({}, [], tolerance=-1)


def test_pair_yield_counts_close_matched_plus_unmatched_equals_n():
    docs = {"D": {"1.1": 1, "1.2": 1, "1.3": 9}}
    y = A.pair_yield(docs, [("D", "1.1"), ("D", "1.3")], tolerance=0)
    assert y["with_match"] + y["without_match"] == y["n_defect_sections"] == 2


# ===================================================== pure: citations

def test_the_date_is_anchored_to_its_own_citation_not_to_the_first_date_in_the_note():
    text = ("At 87 FR 31688, May 25, 2022, § 1653.2 was amended; the amendment at "
            "80 FR 9879, Feb. 25, 2015, is unrelated.")
    assert A.citation_date(text, "87 FR 31688") == "2022-05-25"
    assert A.citation_date(text, "80 FR 9879") == "2015-02-25"


def test_abbreviated_months_resolve_and_an_unreadable_date_returns_none():
    assert A.citation_date("At 83 FR 61311, Nov. 29, 2018,", "83 FR 61311") == "2018-11-29"
    assert A.citation_date("At 89 FR 104393, Dec. 23, 2024,", "89 FR 104393") == "2024-12-23"
    assert A.citation_date("At 83 FR , May 1, 2018,", "83 FR 999") is None


def test_neighbour_dates_are_both_sides_because_the_drift_runs_both_ways():
    assert A.neighbour_dates("2020-07-15") == ["2020-07-16", "2020-07-14"]
    assert A.neighbour_dates("2022-05-25") == ["2022-05-26", "2022-05-24"]


# ===================================================== live: the three goldens

@needs_raw
@pytest.mark.parametrize("fname,page,section,frdoc,n", [G1, G2, G3])
def test_live_golden_document_resolves_and_has_the_hand_counted_amdpars(
        fname, page, section, frdoc, n):
    issue = A.load_issue(RAW / fname)
    rule, route = A.resolve_citation(issue, page, section)
    assert rule["frdoc"] == frdoc, route
    assert len(rule["amdpars"]) == n          # counted by hand with grep -c '<AMDPAR>'


@needs_raw
def test_live_golden_G2_reproduces_the_hand_computed_table_element_for_element():
    """goldens.md section 4. 22 of 29 complete, and every field of every element."""
    issue = A.load_issue(RAW / G2[0])
    rule, _ = A.resolve_citation(issue, G2[1], G2[2])
    recs = A.attribute(rule["amdpars"], "extended", rule["parts"])
    c = A.completeness(recs)
    assert (c["complete"], c["total"]) == (22, 29)
    assert c["attributed"] == 28 and c["unattributable"] == 1
    assert round(c["completeness"], 4) == 0.7586

    hand = {                       # (section, operation, designation, complete)
        1: (None, None, None, False),
        2: ("1468.3", "amend", None, False),
        3: ("1468.3", None, None, False),
        4: ("1468.3", "remove", "(1)", True),
        10: ("1468.6", "remove", "(a)(3)(iii)", True),
        13: ("1468.22", "revise", "(b)(11)", True),
        18: ("1468.24", "revise", "(b)(2)(i)", True),
        24: ("1468.27", "redesignate", "(e)(4)(iii)", True),
        25: ("1468.27", "add", "(e)(4)(iii)", True),
        29: ("1468.32", "add", "(c)(2)", True),
    }
    for ordinal, want in hand.items():
        r = recs[ordinal - 1]
        assert (r["section"], r["operation"], r["designation"], r["complete"]) == want, ordinal
    assert recs[3]["anchor"] == "farm or ranch or"
    assert recs[5]["anchor"] == "Eligible land"


@needs_raw
def test_live_golden_G1_reproduces_and_pins_the_detector_divergence():
    """goldens.md section 3, plus its ERRATUM. `extended` 15/28 was predicted by hand
    and reproduces. `spec_literal` was hand-predicted as 13/28; the measured figure is
    14/28, because the hand enumeration omitted element 3 - the one element that names
    its section with the sign and is therefore CORRECTLY attributed. The golden was not
    edited; see goldens.md ERRATUM E1."""
    issue = A.load_issue(RAW / G1[0])
    rule, _ = A.resolve_citation(issue, G1[1], G1[2])
    ext = A.completeness(A.attribute(rule["amdpars"], "extended", rule["parts"]))
    lit = A.completeness(A.attribute(rule["amdpars"], "spec_literal", rule["parts"]))
    assert (ext["complete"], ext["total"]) == (15, 28)
    assert ext["attributed"] == 27 and ext["unattributable"] == 1
    assert (lit["complete"], lit["total"]) == (14, 28)          # ERRATUM E1
    assert lit["unattributable"] == 2
    assert lit["completeness"] < ext["completeness"]

    recs = A.attribute(rule["amdpars"], "spec_literal", rule["parts"])
    # The failure is not under-detection, it is MIS-attribution: element 5 names
    # section 2.106 in the word form, and the sign-only detector pins it to 1.9005.
    assert recs[4]["section"] == "1.9005"
    ext_recs = A.attribute(rule["amdpars"], "extended", rule["parts"])
    assert ext_recs[4]["section"] == "2.106"


@needs_raw
def test_live_golden_G3_reproduces_and_both_detectors_agree_on_it():
    issue = A.load_issue(RAW / G3[0])
    rule, _ = A.resolve_citation(issue, G3[1], G3[2])
    ext = A.completeness(A.attribute(rule["amdpars"], "extended", rule["parts"]))
    lit = A.completeness(A.attribute(rule["amdpars"], "spec_literal", rule["parts"]))
    assert (ext["complete"], ext["total"]) == (28, 40)
    assert ext["completeness"] == lit["completeness"] == 0.7
    recs = A.attribute(rule["amdpars"], "extended", rule["parts"])
    assert recs[17]["operation"] == "redesignate" and recs[17]["designation"] == "(n)"
    assert recs[18]["operation"] == "redesignate" and recs[18]["designation"] == "(m)(6)"
    assert recs[27]["operation"] is None and recs[27]["designation"] == "(a)"


# ===================================================== live: Q8 known-positive

@needs_raw
@pytest.mark.parametrize("fname", ["FR-2014-04-29.xml", "FR-2019-04-17.xml",
                                   "FR-2021-02-04.xml", "FR-2020-07-16.xml"])
def test_live_parser_amdpar_count_equals_a_plain_text_sweep(fname):
    """`QUESTIONS.md` Q8, applied to this chunk's counter: a zero that means 'wrong tag
    name' looks exactly like a zero that means 'nothing there', so the count is checked
    against a dumb byte-level count of the open tag before any zero is believed.

    The parser walks <RULE> only; <PRORULE> AMDPARs are proposed amendments that never
    executed. So the identity asserted is parser + prorule == raw grep, and the two can
    only disagree if elements are dropped or duplicated.
    """
    path = RAW / fname
    raw_count = len(re.findall(rb"<AMDPAR>", path.read_bytes()))
    assert raw_count > 0, "known-positive input must actually contain AMDPARs"

    root = ET.parse(str(path)).getroot()
    prorule = sum(1 for p in root.iter("PRORULES") for _ in p.iter("AMDPAR"))
    parsed = sum(len(r["amdpars"]) for r in A.iter_rule_documents(path))
    assert parsed + prorule == raw_count


@needs_raw
def test_live_a_zero_amdpar_rule_is_a_real_zero_not_a_wrong_element_name():
    """FR Doc 2014-08743 is the Federal Acquisition Circular 2005-73 cover document. It
    genuinely amends nothing - and the issue it sits in contains 892 AMDPARs, so the
    zero cannot be the extractor looking for the wrong tag."""
    path = RAW / "FR-2014-04-29.xml"
    rules = {r["frdoc"]: r for r in A.iter_rule_documents(path)}
    assert len(rules["2014-08743"]["amdpars"]) == 0
    assert sum(len(r["amdpars"]) for r in rules.values()) == 889


@needs_raw
def test_live_descendant_text_is_read_not_direct_text():
    """An AMDPAR whose first child is an <E> element has an empty `.text`. Reading it
    would silently drop the instruction (goldens section 1)."""
    el = ET.fromstring('<AMDPAR>e. Amend <E T="03">Section II.A.1</E> by removing '
                       'the bullet after “Employees”.</AMDPAR>')
    assert (el.text or "").strip() == "e. Amend"
    assert A.element_text(el) == ("e. Amend Section II.A.1 by removing the bullet "
                                  "after “Employees”.")


# ===================================================== live: the resolution probe

@needs_raw
def test_live_probe_page_only_resolution_picks_a_document_that_amends_nothing():
    """PROBE, hard rule 6 - fails on the old rule, passes on the new, both kept.

    `resolve_page` is the rule the goldens pre-registered: contents route first. On
    79 FR 24198 it returns the Federal Acquisition Circular cover document, which has
    ZERO AMDPARs, because the front-matter contents lists the circular over the top of
    the rule that does the amending. `resolve_citation` uses the cited section as a
    third exact key and returns the rule with 838 AMDPARs.
    """
    issue = A.load_issue(RAW / "FR-2014-04-29.xml")

    old, old_route = A.resolve_page(issue, 24198)
    assert old["frdoc"] == "2014-08743"
    assert old_route == "both-disagree"
    assert len(old["amdpars"]) == 0                       # the defect: nothing to attribute

    new, new_route = A.resolve_citation(issue, 24198, "6.302-1")
    assert new["frdoc"] == "2014-08744"
    assert new_route == "section-match-disambiguated"
    assert len(new["amdpars"]) == 838
    assert "6.302-1" in A.sections_amended(new)


@needs_raw
def test_live_probe_an_off_by_one_note_date_resolves_via_the_neighbouring_issue():
    """85 FR 43138 is noted 'July 15, 2020'; the rule was FILED 7-15-20 and PUBLISHED
    7-16-20. Page-only resolution inside the noted issue finds nothing at all."""
    noted = A.load_issue(RAW / "FR-2020-07-15.xml")
    assert A.resolve_page(noted, 43138) == (None, "unresolved")

    published = A.load_issue(RAW / "FR-2020-07-16.xml")
    rule, route = A.resolve_citation(published, 43138, "90.209")
    assert rule["frdoc"] == "2020-11897"
    assert route.startswith("section-match")
    assert "90.209" in A.sections_amended(rule)


# ===================================================== live: the freeze

@needs_freeze
def test_freeze_verifies_against_its_committed_manifest():
    assert A.main(["verify", "--out", str(OUT)]) == 0


@needs_freeze
def test_freeze_exclusion_ladder_closes_and_every_rung_prints_even_at_zero():
    """Hard rule 14: zero-occurrence branches print as zeros; kept + removed == n."""
    ladder = json.loads((OUT / "completeness.json").read_text(encoding="utf-8"))["exclusion_ladder"]
    for rung in ("no_date", "no_issue_file", "volume_mismatch", "unresolved_page", "resolved"):
        assert rung in ladder
    rungs = sum(ladder[k] for k in ("no_date", "no_issue_file", "volume_mismatch",
                                    "unresolved_page", "resolved"))
    assert rungs == ladder["pool_citations"] == 85


@needs_freeze
def test_freeze_global_completeness_is_below_the_090_gate_and_is_reported_not_tuned():
    """The measured result. `plan.md` pre-registers the branches; this test pins which
    one the numbers land in so that a later edit cannot move the chunk into a kinder
    branch without turning the suite red."""
    g = json.loads((OUT / "completeness.json").read_text(encoding="utf-8"))["global"]
    assert round(g["spec_literal"]["completeness"], 4) == 0.5080
    assert round(g["extended"]["completeness"], 4) == 0.6643
    assert g["spec_literal"]["completeness"] < 0.80
    assert g["extended"]["completeness"] < 0.80
    # attribution is near-total; the loss is in the parse half, not the attribution half
    assert g["extended"]["attribution_rate"] > 0.98


@needs_freeze
def test_freeze_pair_yield_clears_the_42_target_on_EXACT_matching_alone():
    y = json.loads((OUT / "pair_yield.json").read_text(encoding="utf-8"))
    assert y["0"]["tolerance"] == 0
    assert y["0"]["n_defect_sections"] == 85
    assert y["0"]["with_match"] == 51
    assert round(y["0"]["yield"], 4) == 0.6000
    assert y["0"]["projected_pairs"] == 51 >= 42
    # the looser rule is reported and NOT adopted; it must never be the one that clears
    assert y["1"]["with_match"] == 58 > y["0"]["with_match"]


@needs_freeze
def test_freeze_is_deterministic_byte_for_byte(tmp_path):
    """Hard rule 9, proved by hash rather than asserted."""
    rc = subprocess.run(
        [sys.executable, str(REPO / "src/attribute_amdpars.py"), "extract",
         "--raw", str(RAW), "--out", str(tmp_path)],
        capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr[-2000:]
    a = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["files"]
    b = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))["files"]
    assert set(a) == set(b)
    for name in sorted(a):
        assert a[name]["sha256"] == b[name]["sha256"], name
