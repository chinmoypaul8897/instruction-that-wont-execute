"""CH-13A - the slide deck opens offline, and every number on it exists in an artifact.

The deck at ``docs/slides/index.html`` is recorded for deliverable 03. Two things can
silently ruin it and neither shows up by looking at the file:

1. **A network reference.** One CDN font, one remote image, one ``src="//"`` and the
   deck degrades on the recording machine - or renders differently in the room where it
   is played than in the room where it was built. The brief for this chunk requires a
   test that fails on ``http://``, ``https://`` and ``src="//"``; that is
   ``test_no_network_references``, and the sibling tests close the same hole from the
   other side - no external stylesheet, script, ``@import``, ``url()`` or media element.

2. **A number that drifted away from its artifact.** ``CLAUDE.md`` hard rule 14 -
   evidence or it did not happen. Every figure the deck displays is recomputed here from
   the committed JSON and asserted to be present in the rendered text, and every verbatim
   quotation - the amendatory instruction, the NARA editorial note, the two ``why``
   strings the model emitted - is read out of the artifact it was copied from and
   asserted character-for-character. A slide that says ``0.7195`` when
   ``a1-result.json`` says something else is a red test, not a surprise discovered
   halfway through recording.

NORMALISATION. The deck is compared at **whitespace-collapsed**, and that is declared
rather than applied silently (hard rule 7): the rendered text has tags stripped, HTML
entities decoded, and runs of whitespace collapsed to one space, because CSS soft-wraps
the artifact strings and the source line breaks are not part of the quotation. The
quoted strings themselves are compared with no other change.

The goldens were hand-computed from the artifacts before this file was written -
39/82 = 0.4756, 54/82 = 0.6585, 59/82 = 0.7195, the gaps +18.3 / +6.1 / +0.0 / -9.8 /
-1.2 pp, and p = 0.0059 / 0.4244 / 1.0000 / 0.4421 - and the test recomputes them from
the JSON, so a change on either side goes red.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DECK = REPO / "docs" / "slides" / "index.html"

A1_RESULT = REPO / "docs" / "evidence" / "ch06-a1" / "a1-result.json"
CHECKPOINT = REPO / "docs" / "evidence" / "checkpoint" / "checkpoint-result.json"
LEAKAGE = REPO / "docs" / "evidence" / "ch09-removed" / "leakage-result.json"
ARTIFACTS = REPO / "docs" / "evidence" / "ch06-a1" / "A1-rep1-artifacts.jsonl"
EVALSET = REPO / "data" / "evalset" / "items.jsonl"
AMDPARS = REPO / "data" / "amdpars" / "amdpars.jsonl"
DEFECT_NOTES = REPO / "data" / "ednotes" / "defect_notes.jsonl"

EXEMPLAR = "05-8447|75.6"
DEFECT_ITEM = "2016-03298|1150.35"

PALETTE = {"#FBFAF7", "#1A1A18", "#6B6862", "#D8D4CC", "#9B2226"}

_ENTITIES = [
    ("&middot;", "·"), ("&sect;", "§"), ("&ldquo;", "“"),
    ("&rdquo;", "”"), ("&minus;", "−"), ("&mdash;", "—"),
    ("&ndash;", "–"), ("&rarr;", "→"), ("&prime;", "′"),
    ("&nbsp;", " "), ("&ge;", "≥"), ("&le;", "≤"),
    ("&times;", "×"), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&"),
]

SRC_SLASHSLASH = 'src="' + "//"


@pytest.fixture(scope="module")
def raw() -> str:
    return DECK.read_text(encoding="utf-8")


def _render(fragment: str) -> str:
    """Tags stripped, entities decoded, whitespace collapsed - the reader's view."""
    s = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.S | re.I)
    s = re.sub(r"<style\b.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", "", s)
    for entity, char in _ENTITIES:
        s = s.replace(entity, char)
    return re.sub(r"\s+", " ", s).strip()


@pytest.fixture(scope="module")
def rendered(raw: str) -> str:
    """The whole deck as one string."""
    return _render(raw)


@pytest.fixture(scope="module")
def slide(raw: str):
    """slide(n) -> the rendered text of slide n, 1-based.

    Numbers are asserted against the slide they are printed on, not against the deck as
    a whole. Without this a wrong figure on one slide hides behind the right figure on
    another - which is exactly what the first negative-control mutation demonstrated
    before this fixture existed.
    """
    parts = re.findall(r'<section class="slide">(.*?)</section>', raw, flags=re.S)
    assert len(parts) == 13, f"expected 13 slides, found {len(parts)}"
    texts = [_render(p) for p in parts]
    return lambda n: texts[n - 1]


def _jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _alnum(s: str) -> str:
    return re.sub(r"[^0-9a-z]", "", s.lower())


# ---------------------------------------------------------------------------
# 1. it opens offline, from the file alone
# ---------------------------------------------------------------------------

def test_deck_exists():
    assert DECK.is_file(), f"{DECK} is missing"


def test_no_network_references(raw: str):
    """The requirement in prompts/CH-13A.md: no http, no https, no src slash-slash."""
    for needle in ("http://", "https://", SRC_SLASHSLASH):
        assert needle not in raw, f"deck contains a network reference: {needle}"


def test_no_external_stylesheet_or_script(raw: str):
    assert not re.search(r"<script[^>]+\bsrc\s*=", raw, re.I), "deck loads an external script"
    assert not re.search(r"<link\b", raw, re.I), "deck loads an external stylesheet"
    assert "@import" not in raw, "deck imports an external stylesheet"
    assert not re.search(r"url\(", raw, re.I), "deck references an external url()"
    assert not re.search(r"<(img|iframe|video|audio|object|embed)\b", raw, re.I), \
        "deck embeds an external media element"


def test_declares_utf8_and_decodes_cleanly(raw: str):
    assert '<meta charset="utf-8">' in raw
    assert "�" not in raw, \
        "deck holds a replacement character - it was written in the wrong encoding"


def test_thirteen_slides(raw: str):
    assert raw.count('<section class="slide">') == 13


def test_palette_is_exactly_five_colours(raw: str):
    found = {m.upper() for m in re.findall(r"#[0-9A-Fa-f]{3,8}\b", raw)}
    assert found == PALETTE, f"palette drifted: {sorted(found)}"


def test_no_banned_decoration(raw: str):
    lowered = raw.lower()
    for banned in ("gradient", "box-shadow", "text-shadow", "border-radius",
                   "transition", "animation"):
        assert banned not in lowered, f"deck uses a banned property: {banned}"


# ---------------------------------------------------------------------------
# 2. every number on a slide is the number in the artifact
# ---------------------------------------------------------------------------

def test_slide_9_arm_accuracies_and_counts(slide):
    page = slide(9)
    results = json.loads(A1_RESULT.read_text(encoding="utf-8"))["results"]
    for arm in ("B0", "B0-agent", "A1", "B0prime"):
        row = results[arm]
        assert f"{row['accuracy']:.4f}" in page, f"{arm} accuracy missing from slide 9"
        assert f"{row['success']} / {row['n']}" in page, f"{arm} success/n missing from slide 9"


def test_slide_9_gaps(slide):
    page = slide(9)
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    assert f"+{comparisons['A1']['gap_pp']:.1f} pp" in page                 # +6.1 pp
    assert f"+{comparisons['B0prime']['gap_pp']:.1f} pp" in page            # +0.0 pp
    assert f"+{-comparisons['B0']['gap_pp']:.1f} pp" in page                # +18.3 pp, B0 -> B0-agent


def test_slide_9_mcnemar_p_values(slide):
    page = slide(9)
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    assert f"{checkpoint['as_run']['mcnemar']['p_value']:.4f}" in page      # 0.0059
    assert f"{comparisons['A1']['mcnemar']['p_value']:.4f}" in page         # 0.4244
    assert f"{comparisons['B0prime']['mcnemar']['p_value']:.4f}" in page    # 1.0000
    assert "not significant" in page


def test_slide_10_predictions_against_measurements(slide):
    page = slide(10)
    data = json.loads(A1_RESULT.read_text(encoding="utf-8"))
    assert f"{data['results']['A1-iter1']['accuracy']:.4f}" in page          # 0.5610
    assert f"−{abs(data['comparisons']['A1-iter1']['gap_pp']):.1f} pp" in page   # -9.8 pp
    assert f"{data['results']['A1']['accuracy']:.4f}" in page                # 0.7195
    assert "764 seconds" in page


def test_slide_11_composition(slide):
    page = slide(11)
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    # U+2212 MINUS SIGN for the two negatives, plain ink for the one that worked
    assert f"−{abs(comparisons['A1-iter1']['gap_pp']):.1f}" in page          # -9.8
    assert f"−{abs(comparisons['A1-minus-tool']['gap_pp']):.1f}" in page     # -1.2
    assert f"+{comparisons['A1']['gap_pp']:.1f}" in page                     # +6.1


def test_slide_12_leakage_probe_numbers(slide):
    page = slide(12)
    probe = json.loads(LEAKAGE.read_text(encoding="utf-8"))
    assert f"{probe['accuracy_point_in_time']:.4f}" in page
    assert f"{probe['accuracy_current_text']:.4f}" in page
    assert f"−{abs(probe['gap_pp']):.1f} pp" in page
    assert f"p = {probe['mcnemar']['p_value']:.4f}" in page
    assert f"b = {probe['mcnemar']['b_only_a_correct']}" in page
    assert f"c = {probe['mcnemar']['c_only_b_correct']}" in page


def test_slide_4_baseline_hero_number(slide):
    page = slide(4)
    b0 = json.loads(CHECKPOINT.read_text(encoding="utf-8"))["b0"]
    assert f"{b0['accuracy'] * 100:.1f}%" in page, \
        "the hero number on slide 4 is not B0's measured accuracy"
    assert f"n = {b0['n']}" in page
    assert f"{b0['success']} / {b0['n']} correct" in page


def test_slide_7_human_checkpoint_count(slide):
    routed = sum(1 for row in _jsonl(ARTIFACTS) if row["needs_human_review"])
    assert f"{routed} of 82 items routed" in slide(7)


# ---------------------------------------------------------------------------
# 3. every quotation is character-for-character the artifact
# ---------------------------------------------------------------------------

def test_slide_2_defective_instruction_is_verbatim(slide):
    hits = [r for r in _jsonl(AMDPARS)
            if r["frdoc"] == "2016-03298" and r["ordinal"] == 180]
    assert len(hits) == 1
    assert _collapse(hits[0]["text"]) in slide(2)


def test_slide_3_editorial_note_is_verbatim(slide):
    hits = [r for r in _jsonl(DEFECT_NOTES)
            if r["section"] == "1150.35" and "81 FR 8855" in r["fr_citations"]]
    assert len(hits) == 1
    page = slide(3)
    assert hits[0]["hed"] in page
    assert _collapse(hits[0]["text"]) in page


def test_slide_5_exemplar_instructions_are_verbatim(slide):
    item = next(r for r in _jsonl(EVALSET) if r["item_id"] == EXEMPLAR)
    assert item["instruction_count"] == 4
    page = slide(5)
    for instruction in item["instructions"]:
        assert _collapse(instruction["text"]) in page
    # the section-text excerpt is the real point-in-time text, not a paraphrase
    for excerpt in ("(38) ASTM D4891-89, Standard Test Method for Heating Value of Gases "
                    "in Natural Gas Range by Stoichiometric Combustion, for appendices D "
                    "and F to this part.",
                    "American Society for Testing and Material (ASTM), 1916 Race Street, "
                    "Philadelphia, Pennsylvania 19103;"):
        assert excerpt in _collapse(item["section_text"]), "excerpt is not in the artifact"
        assert excerpt in page, "excerpt is not on slide 5"


def test_slide_6_tool_response_is_verbatim(slide):
    row = next(r for r in _jsonl(ARTIFACTS) if r["item_id"] == EXEMPLAR)
    trace = {t["instruction_index"]: t for t in row["resolution_trace"]}[4]
    page = slide(6)
    assert '"designation": "(a)(38)"' in page
    assert f'"designation_exists": {str(trace["designation_exists"]).lower()}' in page
    assert '"as_of_date": "2004-07-01"' in page
    assert '"declared_designations": 60' in page


def test_slide_7_and_8_emitted_note_is_verbatim(slide):
    row = next(r for r in _jsonl(ARTIFACTS) if r["item_id"] == EXEMPLAR)
    seven = slide(7)
    assert row["verdict"] in seven
    assert row["failing_designation"] in seven
    assert row["failure_class"] in seven
    by_index = {t["instruction_index"]: t for t in row["resolution_trace"]}
    eight = slide(8)
    for index in (3, 4):
        assert _collapse(by_index[index]["model_ruling"]["why"]) in eight, \
            f"instruction {index}'s why string is not quoted verbatim on slide 8"


# ---------------------------------------------------------------------------
# 4. the claims the slides make in prose are true of the data
# ---------------------------------------------------------------------------

def test_slide_two_anchor_is_absent_at_every_declared_level():
    """Slide 2 asserts the quoted sentence is absent at every declared level. Check it."""
    item = next(r for r in _jsonl(EVALSET) if r["item_id"] == DEFECT_ITEM)
    anchor = next(i["anchor"] for i in item["instructions"] if i.get("anchor"))
    text = item["section_text"]
    assert anchor not in text, "exact"
    assert _collapse(anchor) not in _collapse(text), "whitespace-collapsed"
    assert _alnum(anchor) not in _alnum(text), "alphanumeric-only"
    real = "Stay petitions must be filed within 7 days of the filing of the notice of exemption."
    assert real in text, "the sentence the deck prints as the real text is not the real text"


def test_slide_eight_override_is_true_of_the_data():
    """Slide 8 says the resolver denied (a)(38) while (38) sits in the section and in siblings."""
    item = next(r for r in _jsonl(EVALSET) if r["item_id"] == EXEMPLAR)
    row = next(r for r in _jsonl(ARTIFACTS) if r["item_id"] == EXEMPLAR)
    trace = {t["instruction_index"]: t for t in row["resolution_trace"]}
    for index in (3, 4):
        assert trace[index]["designation"] == "(a)(38)"
        assert trace[index]["designation_exists"] is False, "the resolver did deny it"
        assert "(38)" in trace[index]["siblings"], "siblings did carry it"
    assert "(38) ASTM D4891-89" in item["section_text"], "the paragraph is in the section text"
    assert row["verdict"] == "WILL_FAIL" == item["label"], "the derived verdict matches gold"
