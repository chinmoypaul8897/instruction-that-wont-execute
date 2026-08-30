"""CH-01 - proof for src/harvest_ednotes.py.

Every expected value in this file was hand-computed in
`docs/evidence/ch01-pool/goldens.md` and committed in `dd1504d`, BEFORE
`src/harvest_ednotes.py` existed (hard rule 4). If you change a number here you are
changing a golden, and hard rule 5 says you may not do that to turn a red test green.

The XML fixtures below are **verbatim byte-for-byte excerpts** of the govinfo files
the goldens were read from, re-wrapped in their real `DIV` ancestry. They are embedded
rather than read from `data/raw/`, because `data/raw/` is git-ignored and never
tracked - a suite that needs a 41 MB download to run is a suite that does not run in
the clean-clone rehearsal at CH-14a.

`test_live_*` re-derives the same goldens from the actual downloaded title XML and
SKIPS when it is absent. That is the test that would catch a fixture transcribed
wrongly, so it is reported separately in the pass/fail/skip count rather than folded in.
"""
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from harvest_ednotes import (  # noqa: E402
    DEFECT_LITERAL,
    NORMALISATION,
    SECTION_TYPE,
    collapse_ws,
    find_fr_citations,
    is_defect,
    iter_ednotes,
    normalise_section,
    note_texts,
    tally,
    write_jsonl,
)

S = "§"          # SECTION SIGN, spelled as an escape so this file's own encoding
                      # cannot quietly become the thing under test
LDQ, RDQ = "“", "”"   # the curly quotes inside golden G2

# ------------------------------------------------------------------ raw excerpts
# Copied from data/raw/ecfr/ECFR-title7.xml and ECFR-title11.xml with `sed -n`.

G1_EDNOTE = (
    "<EDNOTE>\n<HED>Editorial Note:</HED><PSPACE>At 83 FR 61311, Nov. 29, 2018, "
    f"{S} 2.22 was amended by adding (a)(1)(xvi), however paragraph (a)(xvi) was not "
    "provided in the text, this amendment could not be incorporated due to inaccurate "
    "amendatory instruction.</PSPACE></EDNOTE>\n"
)
G2_EDNOTE = (
    "<EDNOTE>\n<HED>Editorial Note:</HED><PSPACE>At 58 FR 52646, Oct. 12, 1993, the "
    "Farmers Home Administration attempted to amend exhibit C of subpart B of part 1900 "
    f"by removing in the second paragraph the words {LDQ}(month) ________,{RDQ}; however, "
    f"because {LDQ}(month) ________{RDQ} does not exist in the second paragraph, this "
    "amendment could not be incorporated.</PSPACE></EDNOTE>\n"
)
G3_EDNOTE = (
    "<EDNOTE>\n<HED>Editorial Note:</HED><PSPACE>For <E T=\"04\">Federal Register</E> "
    f"citations affecting {S} 104.3, see the List of CFR Sections Affected, which "
    "appears in the Finding Aids section of the printed volume and at "
    "<I>www.govinfo.gov.</I></PSPACE></EDNOTE>\n"
)
G4_EDNOTE = (
    "<EDNOTE>\n<HED>Editorial Note:</HED><PSPACE>At 88 FR 82235, Nov. 24, 2023, "
    f"{S} 981.467 was amended; however, the amendments could not be incorporated because "
    "the section was stayed indefinitely at 88 FR 67627, Oct. 2, 2023.</PSPACE></EDNOTE>\n"
    # The sibling <EFFDNOT> is kept in the fixture on purpose: it is an adjacent note
    # element carrying the same FR numbers, and the extractor must not absorb it.
    "<EFFDNOT>\n<HED>Effective Date Note:</HED><PSPACE>At 88 FR 67627, Oct. 2, 2023, "
    f"{S} 981.467 was stayed indefinitely.</PSPACE></EFFDNOT>\n"
)


def doc(*, title_n, part_open, container_open, container_close, ednote):
    """Wrap a verbatim <EDNOTE> in its verbatim DIV ancestry."""
    return (
        '<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>\n<TEXT>\n<BODY>\n'
        '<ECFRBRWS>\n'
        f'<DIV1 N="{title_n}" NODE="{title_n}:1" TYPE="TITLE">\n'
        f"{part_open}{container_open}{ednote}{container_close}"
        "</DIV5>\n</DIV1>\n</ECFRBRWS>\n</BODY>\n</TEXT>\n</DLPSTEXTCLASS>\n"
    ).encode("utf-8")


G1_DOC = doc(
    title_n="7",
    part_open='<DIV5 N="2" NODE="7:1.1.1.1.5" TYPE="PART">\n',
    container_open=f'<DIV8 N="{S} 2.22" NODE="7:1.1.1.1.5.3.29.9" TYPE="SECTION">\n',
    container_close="</DIV8>\n",
    ednote=G1_EDNOTE,
)
G2_DOC = doc(
    title_n="7",
    part_open='<DIV5 N="1900" NODE="7:12.1.2.7.10" TYPE="PART">\n',
    container_open='<DIV9 N="" NODE="7:12.1.2.7.10.2.1.8.15" TYPE="APPENDIX">\n',
    container_close="</DIV9>\n",
    ednote=G2_EDNOTE,
)
G3_DOC = doc(
    title_n="11",
    part_open='<DIV5 N="104" NODE="11:1.0.1.1.12" TYPE="PART">\n',
    container_open=f'<DIV8 N="{S} 104.3" NODE="11:1.0.1.1.12.0.1.3" TYPE="SECTION">\n',
    container_close="</DIV8>\n",
    ednote=G3_EDNOTE,
)
G4_DOC = doc(
    title_n="7",
    part_open='<DIV5 N="981" NODE="7:8.1.1.1.23.3.334" TYPE="PART">\n',
    container_open=f'<DIV8 N="{S} 981.467" NODE="7:8.1.1.1.23.3.334.9" TYPE="SECTION">\n',
    container_close="</DIV8>\n",
    ednote=G4_EDNOTE,
)


def one(raw, name="fixture.xml", hint=None):
    recs = list(iter_ednotes(io.BytesIO(raw), source_name=name, title_hint=hint))
    assert len(recs) == 1, f"expected exactly one EDNOTE, got {len(recs)}"
    return recs[0]


# ---------------------------------------------------------------------- goldens

G1_TEXT = (
    f"At 83 FR 61311, Nov. 29, 2018, {S} 2.22 was amended by adding (a)(1)(xvi), "
    "however paragraph (a)(xvi) was not provided in the text, this amendment could not "
    "be incorporated due to inaccurate amendatory instruction."
)
G2_TEXT = (
    "At 58 FR 52646, Oct. 12, 1993, the Farmers Home Administration attempted to amend "
    "exhibit C of subpart B of part 1900 by removing in the second paragraph the words "
    f"{LDQ}(month) ________,{RDQ}; however, because {LDQ}(month) ________{RDQ} does not "
    "exist in the second paragraph, this amendment could not be incorporated."
)
G3_TEXT = (
    f"For Federal Register citations affecting {S} 104.3, see the List of CFR Sections "
    "Affected, which appears in the Finding Aids section of the printed volume and at "
    "www.govinfo.gov."
)
G4_TEXT = (
    f"At 88 FR 82235, Nov. 24, 2023, {S} 981.467 was amended; however, the amendments "
    "could not be incorporated because the section was stayed indefinitely at "
    "88 FR 67627, Oct. 2, 2023."
)


def test_golden_g1_defect_note_section_level():
    """goldens.md G1 - the usable case, field by field."""
    r = one(G1_DOC, "ECFR-title7.xml", "7")
    assert r["title"] == "7"
    assert r["part"] == "2"
    assert r["section"] == "2.22"
    assert r["section_raw"] == f"{S} 2.22"
    assert r["node"] == "7:1.1.1.1.5.3.29.9"
    assert r["container_type"] == "SECTION"
    assert r["section_level"] is True
    assert r["hed"] == "Editorial Note:"
    assert r["text"] == G1_TEXT
    assert r["is_defect"] is True
    assert r["fr_citation"] == "83 FR 61311"
    assert r["fr_citations"] == ["83 FR 61311"]
    assert r["normalisation"] == NORMALISATION == "whitespace-collapsed"
    assert r["source_file"] == "ECFR-title7.xml"
    assert r["ordinal"] == 1


def test_golden_g2_defect_note_in_appendix_is_not_section_level():
    """goldens.md G2 - the rung the section-level filter removes.

    Also the empty `N=""` attribute: an appendix's identity is in its <HEAD>, and a
    parser that assumes N is populated returns the empty string as a section number.
    """
    r = one(G2_DOC, "ECFR-title7.xml", "7")
    assert r["title"] == "7"
    assert r["part"] == "1900"
    assert r["section"] is None
    assert r["section_raw"] is None          # no enclosing SECTION container at all
    assert r["node"] == "7:12.1.2.7.10.2.1.8.15"
    assert r["container_type"] == "APPENDIX"
    assert r["section_level"] is False
    assert r["is_defect"] is True
    assert r["text"] == G2_TEXT
    assert r["fr_citation"] == "58 FR 52646"


def test_golden_g3_negative_control_is_not_a_defect_note():
    """goldens.md G3 - a filter that keeps this one, or invents a citation, is broken."""
    r = one(G3_DOC, "ECFR-title11.xml", "11")
    assert r["title"] == "11"
    assert r["part"] == "104"
    assert r["section"] == "104.3"
    assert r["container_type"] == "SECTION"
    assert r["section_level"] is True
    assert r["is_defect"] is False
    assert r["fr_citation"] is None
    assert r["fr_citations"] == []
    assert r["text"] == G3_TEXT


def test_golden_g3_inline_elements_keep_their_spacing():
    """`For <E>Federal Register</E> citations`, not `ForFederal Registercitations`.

    The tail-text rule is the whole bug class here: an extractor that reads element
    `.text` but forgets `.tail` silently deletes every word that follows an italic.
    """
    r = one(G3_DOC, "ECFR-title11.xml", "11")
    assert "For Federal Register citations" in r["text"]
    assert "ForFederal" not in r["text"]
    assert "Registercitations" not in r["text"]
    assert r["text"].endswith("at www.govinfo.gov.")


def test_golden_g4_first_fr_citation_is_the_rule_under_test():
    """goldens.md G4 - two citations; the first is the amending rule, the second a stay.

    Reading the last match would attribute this defect to the wrong FR document at
    CH-02, and nothing downstream would notice.
    """
    r = one(G4_DOC, "ECFR-title7.xml", "7")
    assert r["text"] == G4_TEXT
    assert r["fr_citations"] == ["88 FR 82235", "88 FR 67627"]
    assert r["fr_citation"] == "88 FR 82235"
    assert r["section"] == "981.467"
    assert r["is_defect"] is True


def test_adjacent_effdnot_is_not_absorbed_into_the_ednote():
    """G4's fixture carries a sibling <EFFDNOT> with the same FR numbers in it."""
    recs = list(iter_ednotes(io.BytesIO(G4_DOC)))
    assert len(recs) == 1
    # The EDNOTE ends at its own closing tag and not one character later.
    assert recs[0]["text"] == G4_TEXT
    assert recs[0]["text"].endswith("Oct. 2, 2023.")
    assert "Effective Date Note" not in recs[0]["text"]
    assert "Effective Date Note" not in recs[0]["hed"]
    assert "was stayed indefinitely." not in recs[0]["text"]   # that is EFFDNOT's wording


def test_hed_is_split_out_and_never_glued_to_the_body():
    """The reason `hed` and `text` are separate fields (goldens.md, normalisation)."""
    for raw in (G1_DOC, G2_DOC, G3_DOC, G4_DOC):
        r = one(raw)
        assert r["hed"] == "Editorial Note:"
        assert not r["text"].startswith("Editorial Note")
        assert "Note:At" not in r["text"]


# ------------------------------------------------------------------ pure helpers

def test_collapse_ws_is_the_declared_level():
    assert collapse_ws("  a\n\n b \t c  ") == "a b c"
    assert collapse_ws("") == ""
    assert collapse_ws("\n") == ""


@pytest.mark.parametrize("raw,expected", [
    (f"{S} 2.22", "2.22"),
    (f"{S}2.22", "2.22"),
    (f"{S}{S} 1.1-1.5", "1.1-1.5"),
    ("", None),          # golden G2's appendix
    ("   ", None),
    (None, None),
    ("1416.302", "1416.302"),
])
def test_normalise_section(raw, expected):
    assert normalise_section(raw) == expected


@pytest.mark.parametrize("text,expected", [
    ("At 83 FR 61311, Nov. 29, 2018", ["83 FR 61311"]),
    ("at 88 FR 82235 ... at 88 FR 67627, Oct. 2", ["88 FR 82235", "88 FR 67627"]),
    ("no citation here", []),
    ("89  FR  54360", ["89 FR 54360"]),      # collapses internal spacing
    ("see 12 CFR 1026.1", []),               # CFR is not FR
])
def test_find_fr_citations(text, expected):
    assert find_fr_citations(text) == expected


def test_is_defect_matches_the_spec_literal_exactly():
    assert DEFECT_LITERAL == "could not be incorporated"
    assert is_defect("this amendment could not be incorporated due to ...") is True
    assert is_defect("the amendments could not be incorporated because ...") is True
    assert is_defect("was incorporated without change") is False
    # Case matters, and the harvest reports the case-insensitive delta rather than
    # silently widening the filter (hard rule 5: never loosen to get a bigger number).
    assert is_defect("Could Not Be Incorporated") is False


def test_note_texts_handles_an_ednote_with_no_hed():
    import xml.etree.ElementTree as ET
    el = ET.fromstring("<EDNOTE><PSPACE>bare  body</PSPACE></EDNOTE>")
    assert note_texts(el) == ("", "bare body")


# --------------------------------------------------------------------- ancestry

def test_ednote_with_no_structural_ancestor_is_not_section_level():
    raw = ('<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
           "<EDNOTE><PSPACE>orphan, could not be incorporated</PSPACE></EDNOTE>"
           "</DLPSTEXTCLASS>").encode("utf-8")
    r = one(raw)
    assert r["container_type"] is None
    assert r["section_level"] is False
    assert r["section"] is None
    assert r["part"] is None
    assert r["is_defect"] is True          # still counted - never dropped


def test_nearest_container_wins_and_part_is_found_above_it():
    """A note inside a SECTION inside a SUBPART inside a PART resolves to all three."""
    raw = ('<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
           '<DIV1 N="40" NODE="40:1" TYPE="TITLE">'
           '<DIV5 N="63" NODE="40:1.2.3" TYPE="PART">'
           '<DIV6 N="A" NODE="40:1.2.3.1" TYPE="SUBPART">'
           f'<DIV8 N="{S} 63.14" NODE="40:1.2.3.1.9" TYPE="SECTION">'
           "<EDNOTE><PSPACE>x could not be incorporated at 90 FR 1</PSPACE></EDNOTE>"
           "</DIV8></DIV6></DIV5></DIV1></DLPSTEXTCLASS>").encode("utf-8")
    r = one(raw)
    assert r["title"] == "40"
    assert r["part"] == "63"
    assert r["section"] == "63.14"
    assert r["container_type"] == "SECTION"
    assert r["section_level"] is True


def test_a_note_after_a_closed_section_belongs_to_the_part_not_the_section():
    """The stack must pop. If it does not, a part-level note is miscounted as usable -
    which inflates the pool gate in the flattering direction."""
    raw = ('<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
           '<DIV1 N="7" NODE="7:1" TYPE="TITLE">'
           '<DIV5 N="2" NODE="7:1.1" TYPE="PART">'
           f'<DIV8 N="{S} 2.1" NODE="7:1.1.1" TYPE="SECTION">'
           "<P>body</P></DIV8>"
           "<EDNOTE><PSPACE>could not be incorporated, 90 FR 2</PSPACE></EDNOTE>"
           "</DIV5></DIV1></DLPSTEXTCLASS>").encode("utf-8")
    r = one(raw)
    assert r["container_type"] == "PART"
    assert r["section_level"] is False
    assert r["section"] is None
    assert r["part"] == "2"


def test_layout_divs_are_transparent_for_ancestry():
    """`TYPE="CENTER"` is a layout div, not a structural container."""
    raw = ('<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
           '<DIV1 N="7" NODE="7:1" TYPE="TITLE">'
           '<DIV5 N="2" NODE="7:1.1" TYPE="PART">'
           f'<DIV8 N="{S} 2.1" NODE="7:1.1.1" TYPE="SECTION">'
           '<DIV TYPE="CENTER">'
           "<EDNOTE><PSPACE>could not be incorporated, 90 FR 3</PSPACE></EDNOTE>"
           "</DIV></DIV8></DIV5></DIV1></DLPSTEXTCLASS>").encode("utf-8")
    r = one(raw)
    assert r["container_type"] == "SECTION"
    assert r["section"] == "2.1"


def test_document_order_and_ordinals_survive_subtree_pruning():
    """iter_ednotes prunes finished subtrees to keep 161 MB titles flat in memory.
    Pruning the wrong element would silently drop notes, so pin order and count."""
    body = "".join(
        f'<DIV8 N="{S} 1.{i}" NODE="7:1.1.{i}" TYPE="SECTION">'
        f"<P>filler</P><EDNOTE><PSPACE>note {i} could not be incorporated at 90 FR {i}"
        "</PSPACE></EDNOTE></DIV8>"
        for i in range(1, 51)
    )
    raw = ('<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
           '<DIV1 N="7" NODE="7:1" TYPE="TITLE">'
           f'<DIV5 N="1" NODE="7:1.1" TYPE="PART">{body}'
           "</DIV5></DIV1></DLPSTEXTCLASS>").encode("utf-8")
    recs = list(iter_ednotes(io.BytesIO(raw)))
    assert len(recs) == 50
    assert [r["ordinal"] for r in recs] == list(range(1, 51))
    assert [r["section"] for r in recs] == [f"1.{i}" for i in range(1, 51)]
    assert [r["fr_citation"] for r in recs] == [f"90 FR {i}" for i in range(1, 51)]


# ----------------------------------------------------------------------- ladder

def test_tally_sums_are_asserted_not_assumed():
    recs = [one(d) for d in (G1_DOC, G2_DOC, G3_DOC, G4_DOC)]
    t = tally(recs)
    assert t["ednotes"] == 4
    assert t["defect"] == 3                       # G1, G2, G4
    assert t["non_defect"] == 1                   # G3
    assert t["defect"] + t["non_defect"] == t["ednotes"]
    assert t["defect_section_level"] == 2         # G1, G4
    assert t["defect_not_section_level"] == 1     # G2, the appendix
    assert t["defect_section_level"] + t["defect_not_section_level"] == t["defect"]
    assert t["defect_with_fr"] == 3
    assert t["defect_without_fr"] == 0
    assert t["defect_multi_fr"] == 1              # G4
    assert t["usable_section_and_fr"] == 2
    assert t["defect_pct_of_ednotes"] == 75.0
    assert t["container_types"] == {"APPENDIX": 1, "SECTION": 3}
    assert t["defect_container_types"] == {"APPENDIX": 1, "SECTION": 2}


def test_tally_of_nothing_prints_zeros_not_a_crash():
    """Hard rule 14: a zero-occurrence branch prints as an explicit zero."""
    t = tally([])
    assert t["ednotes"] == 0
    assert t["defect"] == 0
    assert t["defect_pct_of_ednotes"] == 0.0
    assert t["usable_section_and_fr"] == 0
    assert t["container_types"] == {}


def test_tally_reports_the_looser_readings_it_did_not_take():
    """Both are expected to be 0 on real data. They are computed anyway, because an
    unprinted 0 is indistinguishable from an unasked question."""
    import xml.etree.ElementTree as ET
    raw = ('<?xml version="1.0" encoding="UTF-8" ?>\n<DLPSTEXTCLASS>'
           "<EDNOTE><PSPACE>this Could Not Be Incorporated</PSPACE></EDNOTE>"
           "</DLPSTEXTCLASS>").encode("utf-8")
    recs = list(iter_ednotes(io.BytesIO(raw)))
    t = tally(recs)
    assert t["defect"] == 0                          # case-sensitive filter held
    assert t["case_insensitive_only_extra"] == 1     # and the delta is reported
    assert t["literal_in_hed_only"] == 0


# ------------------------------------------------------------------ determinism

def test_same_input_yields_identical_records(tmp_path):
    """Hard rule 9, provable by hash."""
    import hashlib
    a = list(iter_ednotes(io.BytesIO(G1_DOC), "f.xml", "7"))
    b = list(iter_ednotes(io.BytesIO(G1_DOC), "f.xml", "7"))
    assert a == b
    digests = []
    for i in range(2):
        p = tmp_path / f"out{i}.jsonl"
        write_jsonl(p, a)
        digests.append(hashlib.sha256(p.read_bytes()).hexdigest())
    assert digests[0] == digests[1]


def test_jsonl_is_lf_terminated_and_key_sorted(tmp_path):
    p = tmp_path / "o.jsonl"
    write_jsonl(p, [one(G1_DOC)])
    blob = p.read_bytes()
    assert b"\r\n" not in blob, "CRLF would make the manifest platform-dependent"
    keys = list(json.loads(blob.decode("utf-8")).keys())
    assert keys == sorted(keys)


def test_parsing_needs_no_filesystem():
    """Hard rule 8 - the extractor takes bytes and returns records."""
    assert len(list(iter_ednotes(io.BytesIO(G1_DOC)))) == 1


# ------------------------------------------------------- live re-derivation

LIVE7 = REPO / "data" / "raw" / "ecfr" / "ECFR-title7.xml"


@pytest.mark.skipif(not LIVE7.exists(),
                    reason="data/raw/ is git-ignored; run `harvest_ednotes.py fetch`")
def test_live_title7_reproduces_goldens_g1_g2_g4():
    """The test that would catch a fixture transcribed wrongly.

    Skips on a clean clone by design - `data/raw/` is never tracked - so it is
    reported as a skip in the count rather than quietly passing.
    """
    recs = list(iter_ednotes(str(LIVE7), source_name="ECFR-title7.xml", title_hint="7"))
    by_section = {r["section"]: r for r in recs if r["section"]}

    g1 = by_section["2.22"]
    assert g1["text"] == G1_TEXT
    assert g1["part"] == "2" and g1["node"] == "7:1.1.1.1.5.3.29.9"
    assert g1["section_level"] is True and g1["fr_citation"] == "83 FR 61311"

    g4 = by_section["981.467"]
    assert g4["text"] == G4_TEXT
    assert g4["fr_citations"] == ["88 FR 82235", "88 FR 67627"]

    g2 = [r for r in recs if r["node"] == "7:12.1.2.7.10.2.1.8.15"]
    assert len(g2) == 1
    assert g2[0]["text"] == G2_TEXT
    assert g2[0]["container_type"] == "APPENDIX" and g2[0]["section_level"] is False
    assert g2[0]["part"] == "1900"


@pytest.mark.skipif(not LIVE7.exists(), reason="data/raw/ is git-ignored")
def test_live_title7_structural_count_matches_a_text_only_sweep():
    """Independent route to the same number: `grep -c` on the raw bytes.

    The parser and a dumb literal count must agree on how many notes carry the defect
    string. They can only disagree if the parser is dropping or duplicating notes, and
    that is the failure this chunk cannot afford.
    """
    blob = LIVE7.read_text(encoding="utf-8")
    recs = list(iter_ednotes(str(LIVE7), source_name="ECFR-title7.xml", title_hint="7"))
    assert sum(r["is_defect"] for r in recs) == blob.count(DEFECT_LITERAL)
    assert len(recs) == blob.count("<EDNOTE>")
    assert SECTION_TYPE == "SECTION"
