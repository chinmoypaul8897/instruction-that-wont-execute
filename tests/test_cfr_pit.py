"""CH-03 1b/1c - point-in-time text and the leakage strips, against hand goldens.

Every expected value is transcribed from `docs/evidence/ch03-evalset/goldens.md`
sections G-A, G-B, G-E, G-F and G-G, all committed BEFORE `src/cfr_pit.py` existed
(c685e80 and f2e8a37). Hard rule 4.

The load-bearing test in this file is
`test_GF_the_leakage_test_FAILS_on_unstripped_real_bytes`. `plan.md` requires the
reviewer to confirm the leakage test fails on unstripped input **before** accepting
that it passes on stripped input, and a test suite that only ever demonstrates the
passing half is the rigged benchmark returning by a different door.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cfr_pit import (  # noqa: E402
    KNOWN_POSITIVE_EXPECTED,
    KNOWN_POSITIVE_XML,
    LEAKAGE_ELEMENTS,
    PitError,
    assert_stripper_on_known_positive,
    candidate_volumes,
    edition_year,
    eligible_sections,
    find_section,
    leakage_violations,
    parse_parts_header,
    revision_month_day,
    section_sort_key,
    section_text,
    sectno_number,
    strip_leakage,
    volume_covers,
)

VOL5 = REPO / "cfr2024t40v5.xml"
needs_vol5 = pytest.mark.skipif(
    not VOL5.exists(),
    reason="CFR-2024-title40-vol5.xml is a git-ignored raw input; run refetch.py")


# ------------------------------------------------------------------ golden G-A
GA = [
    (40, "2005-05-18", 2004),
    (5,  "2022-05-25", 2022),
    (47, "2026-06-10", 2025),
    (26, "2020-01-05", 2019),
    (12, "2019-12-31", 2019),
    (5,  "2022-01-01", 2021),
    (49, "2016-09-30", 2015),
]


@pytest.mark.parametrize("title,pub,expected", GA)
def test_GA_edition_year(title, pub, expected):
    assert edition_year(title, pub) == expected


def test_GA_revision_dates_by_title_band():
    assert revision_month_day(1) == (1, 1)
    assert revision_month_day(16) == (1, 1)
    assert revision_month_day(17) == (4, 1)
    assert revision_month_day(27) == (4, 1)
    assert revision_month_day(28) == (7, 1)
    assert revision_month_day(41) == (7, 1)
    assert revision_month_day(42) == (10, 1)
    assert revision_month_day(50) == (10, 1)
    with pytest.raises(PitError):
        revision_month_day(51)


def test_GA6_strictly_before_is_strict():
    """The boundary case the word 'strictly' exists for. An edition revised ON the
    publication date could already carry the amendment under test."""
    assert edition_year(5, "2022-01-01") == 2021
    assert edition_year(5, "2022-01-02") == 2022


# ------------------------------------------------------------------ golden G-B3
def test_GB3_stripper_known_positive_counts():
    sec = ET.fromstring(KNOWN_POSITIVE_XML)
    _, counts = strip_leakage(sec)
    assert counts == KNOWN_POSITIVE_EXPECTED == {
        "EDNOTE": 2, "EFFDNOTP": 1, "CITA": 3, "EAR": 1, "total": 7}


def test_GB3_the_known_positive_assertion_runs_and_passes():
    out = assert_stripper_on_known_positive()
    assert out["counts"] == KNOWN_POSITIVE_EXPECTED
    assert out["violations_before"], "the test must FIRE on unstripped input"
    assert out["violations_after"] == []
    assert out["chars_after"] < out["chars_before"]


def test_GB3_the_assertion_would_FAIL_if_the_stripper_looked_for_the_wrong_name():
    """Q8's trap, made falsifiable. Point the stripper at element names that do not
    occur - the ECFR spelling - and the known-positive assertion must RAISE. If it
    passed, every zero this module prints anywhere would be worthless."""
    import cfr_pit
    original = cfr_pit.LEAKAGE_ELEMENTS
    try:
        cfr_pit.LEAKAGE_ELEMENTS = ("DIV8", "NOTESET", "SOURCECREDIT", "AMDREC")
        with pytest.raises(PitError) as exc:
            cfr_pit.assert_stripper_on_known_positive()
        assert "known-positive FAILED" in str(exc.value)
    finally:
        cfr_pit.LEAKAGE_ELEMENTS = original
    # and it passes again once the names are right - so the failure was the names,
    # not a broken fixture
    assert assert_stripper_on_known_positive()["counts"] == KNOWN_POSITIVE_EXPECTED


def test_stripper_does_not_mutate_its_input():
    sec = ET.fromstring(KNOWN_POSITIVE_XML)
    before = len(list(sec.iter()))
    strip_leakage(sec)
    assert len(list(sec.iter())) == before, "strip_leakage must be pure"


def test_nested_pending_text_does_not_survive_stripping():
    sec = ET.fromstring(KNOWN_POSITIVE_XML)
    assert "THE PENDING TEXT" in section_text(sec)
    stripped, _ = strip_leakage(sec)
    assert "THE PENDING TEXT" not in section_text(stripped)


# ------------------------------------------------------------------ golden G-B / G-E
@needs_vol5
def test_GB1_whole_volume_totals_reproduce_CONTEXT_section_8():
    root = ET.parse(str(VOL5)).getroot()
    counts = {t: sum(1 for _ in root.iter(t)) for t in LEAKAGE_ELEMENTS}
    assert counts == {"EDNOTE": 28, "EFFDNOTP": 2, "CITA": 255, "EAR": 5}
    assert sum(1 for _ in root.iter("SECTION")) == 313


@needs_vol5
def test_GE_nested_section_trap_real_bytes():
    root = ET.parse(str(VOL5)).getroot()
    all_sections = [s for s in root.iter("SECTION")]
    eligible = eligible_sections(root)
    assert len(all_sections) == 313
    assert len(eligible) == 311, "exactly 2 SECTIONs are reprints inside EFFDNOTP"

    for section in ("52.2320", "52.2520"):
        raw_hits = [s for s in all_sections if sectno_number(s) == section]
        assert len(raw_hits) == 2, "the naive lookup finds the leak as a candidate"
        hit, n = find_section(root, section)
        assert n == 1, "exactly one ELIGIBLE candidate"
        assert hit is not None
        # the eligible one is the big codified section, not the small reprint
        assert len(section_text(hit)) > 10000


@needs_vol5
@pytest.mark.parametrize("section,expected", [
    ("52.2320", {"EDNOTE": 0, "EFFDNOTP": 1, "CITA": 1, "EAR": 1, "total": 3}),
    ("52.2520", {"EDNOTE": 1, "EFFDNOTP": 1, "CITA": 1, "EAR": 0, "total": 3}),
])
def test_GB2_per_section_strip_counts_real_bytes(section, expected):
    root = ET.parse(str(VOL5)).getroot()
    sec, n = find_section(root, section)
    assert n == 1
    _, counts = strip_leakage(sec)
    assert counts == expected


# ------------------------------------------------------------------ golden G-F
@needs_vol5
@pytest.mark.parametrize("section,own_citation", [
    ("52.2320", "89 FR 54360"),
    ("52.2520", "89 FR 50233"),
])
def test_GF_the_leakage_test_FAILS_on_unstripped_real_bytes(section, own_citation):
    """THE test. plan.md: the reviewer must confirm the leakage test FAILS on
    unstripped input BEFORE accepting that it passes on stripped input."""
    root = ET.parse(str(VOL5)).getroot()
    sec, _ = find_section(root, section)

    unstripped = section_text(sec)
    before = leakage_violations(unstripped, own_citation)
    assert before, f"{section}: the leakage test did not fire on UNSTRIPPED input"
    rules = {v["rule"] for v in before}
    assert "c" in rules, "the literals must fire before stripping"
    assert "b" in rules, "the section's own FR citation is present before stripping"

    stripped_el, counts = strip_leakage(sec)
    stripped = section_text(stripped_el)
    after = leakage_violations(stripped, own_citation)
    assert after == [], f"{section}: still leaking after the strip: {after}"
    assert counts["total"] == 3
    assert len(stripped) < len(unstripped)


# ------------------------------------------------------------------ golden G-G
GG = [
    ("Parts 53 to 59", 53, 59, None, None),
    ("Parts 1 to 49", 1, 49, None, None),
    ("Part 52", 52, 52, None, None),
    ("Part 80 to End", 80, None, None, None),
    ("Parts 500 to 599", 500, 599, None, None),
    ("Part 1 (§§ 1.908 to 1.1000)", 1, 1, "1.908", "1.1000"),
    ("Part 63 (§§ 63.600—63.1199)", 63, 63, "63.600", "63.1199"),
    ("Part 1 (§§ 1.1401 to 1.1550)", 1, 1, "1.1401", "1.1550"),
]


@pytest.mark.parametrize("header,plo,phi,slo,shi", GG)
def test_GG_parse_parts_header(header, plo, phi, slo, shi):
    r = parse_parts_header(header)
    assert (r["part_lo"], r["part_hi"]) == (plo, phi)
    assert (r["section_lo"], r["section_hi"]) == (slo, shi)


def test_GG2_section_ordering_is_numeric_not_lexicographic():
    assert section_sort_key("1.908") < section_sort_key("1.1000")
    assert "1.908" > "1.1000", "the lexicographic answer is the WRONG one"
    assert section_sort_key("1.61") < section_sort_key("1.169")
    assert "1.61" > "1.169"
    assert section_sort_key("60.41a") < section_sort_key("60.41b")
    assert section_sort_key("1.199A-0") < section_sort_key("1.199B-1")


def test_GG2_within_part_volume_selection():
    """The title-26 case. Lexicographic ordering sends 1.909 to the wrong volume."""
    index = [
        {"name": "vol11", "range": parse_parts_header(
            "Part 1 (§§ 1.851 to 1.907)")},
        {"name": "vol12", "range": parse_parts_header(
            "Part 1 (§§ 1.908 to 1.1000)")},
        {"name": "vol21", "range": parse_parts_header("Parts 500 to 599")},
    ]
    assert [v["name"] for v in candidate_volumes(index, "1", "1.909")] == \
        ["vol12", "vol11"], "tier 1 first, then the same-part fallback"
    assert [v["name"] for v in candidate_volumes(index, "1", "1.900")] == \
        ["vol11", "vol12"]
    assert [v["name"] for v in candidate_volumes(index, "550", "550.1")] == ["vol21"]
    assert candidate_volumes(index, "700", "700.1") == []


def test_GG_volume_covers_end_is_unbounded():
    rng = parse_parts_header("Part 80 to End")
    assert volume_covers(rng, "80", "80.1") == (True, True)
    assert volume_covers(rng, "9999", "9999.1") == (True, True)
    assert volume_covers(rng, "79", "79.1") == (False, False)


# ------------------------------------------------------------------ leakage test rules
def test_leakage_rules_fire_independently():
    assert [v["rule"] for v in leakage_violations("nothing here", None)] == []
    assert leakage_violations("see <EDNOTE> here", None)[0]["rule"] == "a"
    assert leakage_violations("at 89 FR 54360 the rule", "89 FR 54360")[0]["rule"] == "b"
    assert leakage_violations("this could not be incorporated", None)[0]["rule"] == "c"
    # whitespace between the citation's tokens must not defeat rule (b) on EITHER
    # side - the text is normalised and so is the citation. Measured both ways.
    assert leakage_violations("at 89   FR\n54360 the rule",
                              "89 FR 54360")[0]["rule"] == "b"
    assert leakage_violations("at 89 FR 54360", "89  FR  54360")[0]["rule"] == "b"


def test_leakage_test_reports_every_rule_that_fired_not_just_the_first():
    v = leakage_violations(
        "<EDNOTE> Editorial Note: at 89 FR 1 set forth as follows", "89 FR 1")
    assert {x["rule"] for x in v} == {"a", "b", "c"}
    assert len([x for x in v if x["rule"] == "c"]) == 2

# ------------------------------------------------- Q8's trap, caught for real (Q17)
EFFDNOT_VOLUME = REPO / "data/raw/cfr/CFR-2015-title7-vol13.xml"
needs_effdnot = pytest.mark.skipif(
    not EFFDNOT_VOLUME.exists(),
    reason="git-ignored raw input; run refetch.py")


@needs_effdnot
def test_Q17_the_spec_names_EFFDNOTP_and_the_corpus_also_uses_EFFDNOT():
    """QUESTIONS.md Q17. CONTEXT.md section 8 names <EFFDNOTP>. In this volume
    <EFFDNOTP> occurs ZERO times and <EFFDNOT> occurs four, carrying the identical
    content. The strip counter's zero was true for the tag and false for the corpus -
    exactly the failure Q8 predicted at CH-01.

    The stripper is NOT extended (Class A). This test pins the finding so that a
    later session cannot rediscover it as a surprise, and so that the day the
    architect DOES extend section 8's list, this test is the thing that changes.
    """
    root = ET.parse(str(EFFDNOT_VOLUME)).getroot()
    assert sum(1 for _ in root.iter("EFFDNOTP")) == 0
    assert sum(1 for _ in root.iter("EFFDNOT")) == 4
    assert "EFFDNOT" not in LEAKAGE_ELEMENTS
    assert "EFFDNOTP" in LEAKAGE_ELEMENTS


@needs_effdnot
def test_Q17_rule_c_is_the_backstop_that_actually_caught_it():
    """The element-name rule (a) CANNOT see <EFFDNOT>; the literal rule (c) can.
    A single-rule leakage test keyed on element names would have passed silently."""
    root = ET.parse(str(EFFDNOT_VOLUME)).getroot()
    sec, n = find_section(root, "1942.5")
    assert n == 1 and sec is not None

    stripped, counts = strip_leakage(sec)
    assert counts["EFFDNOTP"] == 0, "the named tag genuinely is absent"
    assert counts["EDNOTE"] == 0 and counts["EAR"] == 0

    text = section_text(stripped)
    violations = leakage_violations(text, "79 FR 55967")
    assert violations, "the leakage test must still fire after a correct strip"
    rules = {v["rule"] for v in violations}
    assert "c" in rules, "the LITERAL rule is what catches the unnamed element"
    assert "a" not in rules, "the element-name rule cannot see <EFFDNOT> and does not"
    # and the pending amendment text really is still sitting there
    assert "set forth as follows" in " ".join(text.split())
