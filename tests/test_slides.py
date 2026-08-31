"""CH-13A/CH-13B - the deck opens offline, and every number on it exists in an artifact.

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

CH-13B added three slides - the pipeline diagram, the composition as bars, and a real
screenshot of ``docs/worksheet/index.html`` - and with them the deck's first ``<img>``.
The old rule was a blanket ban on ``<img>``; the property it was protecting is *offline
self-containment*, not the absence of a tag. So the ban is replaced by a **stronger**
pair: no ``<iframe|video|audio|object|embed>`` at all, and **every** ``src`` and ``href``
in the file must begin with ``data:`` or ``#`` - which the old rule never checked, and
which would have caught a relative ``src="shot.png"`` that the old rule let through.
``test_worksheet_screenshot_is_a_real_1920x1080_png`` then decodes the payload and reads
its IHDR, so a slide claiming a 1920x1080 capture cannot ship a placeholder.

The bar geometry on slide 12 is asserted against ``a1-result.json`` as well: each bar's
pixel width must equal ``round(|gap_pp| * 52)``. A bar that stops agreeing with the
number printed at its end is a red test, not a drawing anyone has to eyeball.

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

import base64
import json
import re
import struct
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
    assert len(parts) == 15, f"expected 15 slides, found {len(parts)}"
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
    assert not re.search(r"<(iframe|video|audio|object|embed)\b", raw, re.I), \
        "deck embeds an external media element"


def test_every_src_and_href_is_inline(raw: str):
    """Stronger than the old blanket <img> ban: nothing may point off the file.

    The old rule forbade the tag. This one forbids the *reference*, so a relative
    ``src="shot.png"`` - which the old rule permitted, and which breaks the deck the
    moment it is opened anywhere but this directory - now fails.
    """
    refs = re.findall(r'\b(?:src|href)\s*=\s*"([^"]*)"', raw, re.I)
    assert refs, "no src/href found at all - the regex has stopped matching"
    for ref in refs:
        assert ref.startswith("data:") or ref.startswith("#"), \
            f"deck points outside itself: {ref[:60]}"


def test_worksheet_screenshot_is_a_real_1920x1080_png(raw: str):
    """Slide 14 claims a 1920x1080 Playwright capture. Decode it and check."""
    payloads = re.findall(r'src="data:image/png;base64,([A-Za-z0-9+/=]+)"', raw)
    assert len(payloads) == 1, f"expected exactly one inlined PNG, found {len(payloads)}"
    blob = base64.b64decode(payloads[0])
    assert blob[:8] == b"\x89PNG\r\n\x1a\n", "the payload is not a PNG"
    assert blob[12:16] == b"IHDR"
    width, height = struct.unpack(">II", blob[16:24])
    assert (width, height) == (1920, 1080), f"screenshot is {width}x{height}"


def test_declares_utf8_and_decodes_cleanly(raw: str):
    assert '<meta charset="utf-8">' in raw
    assert "�" not in raw, \
        "deck holds a replacement character - it was written in the wrong encoding"


def test_fifteen_slides(raw: str):
    """13 at CH-13A, plus the pipeline diagram and the worksheet screenshot."""
    assert raw.count('<section class="slide">') == 15
    folios = re.findall(r'<div class="folio">(\d\d) / 15</div>', raw)
    assert folios == [f"{n:02d}" for n in range(2, 15)], f"folios drifted: {folios}"


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

def test_slide_10_arm_accuracies_and_counts(slide):
    page = slide(10)
    results = json.loads(A1_RESULT.read_text(encoding="utf-8"))["results"]
    for arm in ("B0", "B0-agent", "A1", "B0prime"):
        row = results[arm]
        assert f"{row['accuracy']:.4f}" in page, f"{arm} accuracy missing from slide 10"
        assert f"{row['success']} / {row['n']}" in page, f"{arm} success/n missing from slide 10"


def test_slide_10_gaps(slide):
    page = slide(10)
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    assert f"+{comparisons['A1']['gap_pp']:.1f} pp" in page                 # +6.1 pp
    assert f"+{comparisons['B0prime']['gap_pp']:.1f} pp" in page            # +0.0 pp
    assert f"+{-comparisons['B0']['gap_pp']:.1f} pp" in page                # +18.3 pp, B0 -> B0-agent


def test_slide_10_mcnemar_p_values(slide):
    page = slide(10)
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    assert f"{checkpoint['as_run']['mcnemar']['p_value']:.4f}" in page      # 0.0059
    assert f"{comparisons['A1']['mcnemar']['p_value']:.4f}" in page         # 0.4244
    assert f"{comparisons['B0prime']['mcnemar']['p_value']:.4f}" in page    # 1.0000
    assert "not significant" in page


def test_slide_11_predictions_against_measurements(slide):
    page = slide(11)
    data = json.loads(A1_RESULT.read_text(encoding="utf-8"))
    assert f"{data['results']['A1-iter1']['accuracy']:.4f}" in page          # 0.5610
    assert f"−{abs(data['comparisons']['A1-iter1']['gap_pp']):.1f} pp" in page   # -9.8 pp
    assert f"{data['results']['A1']['accuracy']:.4f}" in page                # 0.7195
    assert "764 seconds" in page


def test_slide_12_composition(slide):
    page = slide(12)
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    # U+2212 MINUS SIGN for the two negatives, plain ink for the one that worked
    assert f"−{abs(comparisons['A1-iter1']['gap_pp']):.1f}" in page          # -9.8
    assert f"−{abs(comparisons['A1-minus-tool']['gap_pp']):.1f}" in page     # -1.2
    assert f"+{comparisons['A1']['gap_pp']:.1f}" in page                     # +6.1


def test_slide_13_leakage_probe_numbers(slide):
    page = slide(13)
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


def test_slide_8_human_checkpoint_count(slide):
    routed = sum(1 for row in _jsonl(ARTIFACTS) if row["needs_human_review"])
    assert f"{routed} of 82 items routed" in slide(8)


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


def test_slide_6_exemplar_instructions_are_verbatim(slide):
    item = next(r for r in _jsonl(EVALSET) if r["item_id"] == EXEMPLAR)
    assert item["instruction_count"] == 4
    page = slide(6)
    for instruction in item["instructions"]:
        assert _collapse(instruction["text"]) in page
    # the section-text excerpt is the real point-in-time text, not a paraphrase
    for excerpt in ("(38) ASTM D4891-89, Standard Test Method for Heating Value of Gases "
                    "in Natural Gas Range by Stoichiometric Combustion, for appendices D "
                    "and F to this part.",
                    "American Society for Testing and Material (ASTM), 1916 Race Street, "
                    "Philadelphia, Pennsylvania 19103;"):
        assert excerpt in _collapse(item["section_text"]), "excerpt is not in the artifact"
        assert excerpt in page, "excerpt is not on slide 6"


def test_slide_7_tool_response_is_verbatim(slide):
    row = next(r for r in _jsonl(ARTIFACTS) if r["item_id"] == EXEMPLAR)
    trace = {t["instruction_index"]: t for t in row["resolution_trace"]}[4]
    page = slide(7)
    assert '"designation": "(a)(38)"' in page
    assert f'"designation_exists": {str(trace["designation_exists"]).lower()}' in page
    assert '"as_of_date": "2004-07-01"' in page
    assert '"declared_designations": 60' in page


def test_slide_8_and_9_emitted_note_is_verbatim(slide):
    row = next(r for r in _jsonl(ARTIFACTS) if r["item_id"] == EXEMPLAR)
    seven = slide(8)
    assert row["verdict"] in seven
    assert row["failing_designation"] in seven
    assert row["failure_class"] in seven
    by_index = {t["instruction_index"]: t for t in row["resolution_trace"]}
    eight = slide(9)
    for index in (3, 4):
        assert _collapse(by_index[index]["model_ruling"]["why"]) in eight, \
            f"instruction {index}'s why string is not quoted verbatim on slide 9"


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


def test_slide_nine_override_is_true_of_the_data():
    """Slide 9 says the resolver denied (a)(38) while (38) sits in the section and in siblings."""
    item = next(r for r in _jsonl(EVALSET) if r["item_id"] == EXEMPLAR)
    row = next(r for r in _jsonl(ARTIFACTS) if r["item_id"] == EXEMPLAR)
    trace = {t["instruction_index"]: t for t in row["resolution_trace"]}
    for index in (3, 4):
        assert trace[index]["designation"] == "(a)(38)"
        assert trace[index]["designation_exists"] is False, "the resolver did deny it"
        assert "(38)" in trace[index]["siblings"], "siblings did carry it"
    assert "(38) ASTM D4891-89" in item["section_text"], "the paragraph is in the section text"
    assert row["verdict"] == "WILL_FAIL" == item["label"], "the derived verdict matches gold"


# ---------------------------------------------------------------------------
# 5. CH-13B - the three slides added for the video
# ---------------------------------------------------------------------------

def test_slide_5_pipeline_diagram_is_rules_not_pictures(raw: str, slide):
    """The diagram is boxes made of 1px rules and connectors made of thin divs."""
    body = re.search(r'<section class="slide">((?:(?!</section>).)*?class="diagram".*?)</section>',
                     raw, flags=re.S)
    assert body, "no slide carries class=diagram"
    frag = body.group(1)
    assert "<svg" not in frag.lower(), "the diagram was drawn as an SVG"
    assert "<pre" not in frag.lower(), "the diagram is pre-formatted ASCII"
    assert frag.count('class="dbox"') == 6, "expected six boxes on the pipeline diagram"
    assert frag.count('class="hline"') + frag.count('class="vline"') >= 8, \
        "the connectors are not thin divs"
    page = slide(5)
    for noun in ("amendatory instruction", "point-in-time CFR text", "cfr_resolve",
                 "resolution trace", "editorial note", "human review queue"):
        assert noun in page, f"the diagram is missing {noun!r}"


def test_slide_5_queue_count_matches_the_artifact(slide):
    routed = sum(1 for row in _jsonl(ARTIFACTS) if row["needs_human_review"])
    assert f"{routed} of 82 items" in slide(5)
    assert f"{routed} of 82 items" in slide(14), "slide 14 disagrees with the artifact"


def test_slide_12_bar_widths_are_derived_from_the_result_file(raw: str):
    """1 pp = 52 px. A bar that drifts from its own number goes red."""
    comparisons = json.loads(A1_RESULT.read_text(encoding="utf-8"))["comparisons"]
    frag = re.search(r'<div class="chart">(.*?)</div>\s*<div class="gap40">', raw, flags=re.S)
    assert frag, "slide 12's chart block is missing"
    chart = frag.group(1)
    widths = [int(m) for m in re.findall(r'class="bar[^"]*" style="left:\d+px;width:(\d+)px;"', chart)]
    expected = [round(abs(comparisons[arm]["gap_pp"]) * 52)
                for arm in ("A1-iter1", "A1-minus-tool", "A1")]
    assert widths == expected, f"bar widths {widths} != derived {expected}"
    # the two negatives extend LEFT of the zero rule at 690, the positive extends RIGHT
    lefts = [int(m) for m in re.findall(r'class="bar[^"]*" style="left:(\d+)px;', chart)]
    assert [left + width for left, width in zip(lefts[:2], widths[:2])] == [690, 690], \
        "a negative bar does not end on the zero rule"
    assert lefts[2] == 690, "the positive bar does not start on the zero rule"
    assert chart.count("bar neg") == 2 and chart.count('class="bar" ') == 1
    for mark in ("&minus;10", ">0<", "+10"):
        assert mark in chart, f"axis mark {mark} is missing"


def test_slide_12_keeps_the_four_step_reveal(raw: str):
    frag = re.search(r'<div class="chart">.*?class="baxis".*?</section>', raw, flags=re.S)
    assert frag
    assert frag.group(0).count('class="brow step"') == 3
    assert frag.group(0).count('<div class="step">') == 1


def test_caption_band_exists_and_is_off_by_default(raw: str):
    assert '<div id="caption"><span></span></div>' in raw
    assert "#caption{" in raw and "display:none" in raw
    assert "body.cap #caption{display:block;}" in raw
    assert "body.cap .page{bottom:178px;}" in raw, "the band would overlap the slide"
    assert "font-size:30px" in raw and "line-height:1.45" in raw and "max-width:90ch" in raw


# ---------------------------------------------------------------------------
# 6. CH-13B - the end card, which is video-only and not part of the deck
# ---------------------------------------------------------------------------

ENDCARD = REPO / "docs" / "video" / "endcard.html"


@pytest.fixture(scope="module")
def endcard() -> str:
    return ENDCARD.read_text(encoding="utf-8")


def test_endcard_opens_offline(endcard: str):
    """Same rule as the deck: it must render from the file alone."""
    for needle in ("http://", "https://", SRC_SLASHSLASH):
        assert needle not in endcard, f"end card contains a network reference: {needle}"
    assert not re.search(r"<link\b", endcard, re.I)
    assert not re.search(r"<script[^>]+\bsrc\s*=", endcard, re.I)
    assert "@import" not in endcard
    assert not re.search(r"url\(", endcard, re.I)


def test_endcard_uses_the_decks_palette(endcard: str):
    found = {m.upper() for m in re.findall(r"#[0-9A-Fa-f]{3,8}\b", endcard)}
    assert found <= PALETTE, f"the end card invented a colour: {sorted(found - PALETTE)}"


def test_endcard_carries_the_repo_and_the_name_and_nothing_else(endcard: str):
    text = _render(endcard)
    assert "github.com/chinmoypaul8897/instruction-that-wont-execute" in text
    assert "Chinmoy Paul · IIT Guwahati" in text
    # "nothing else" per the card: the title, the repo, the name. No figures, no claims.
    assert not re.search(r"\d+\.\d{2,}", text), f"the end card carries a number: {text}"


def test_endcard_has_no_banned_decoration(endcard: str):
    lowered = endcard.lower()
    for banned in ("gradient", "box-shadow", "text-shadow", "border-radius",
                   "transition", "animation"):
        assert banned not in lowered, f"end card uses a banned property: {banned}"


# ---------------------------------------------------------------------------
# 7. CH-13B - the caption script is the video's source, so it has to parse
# ---------------------------------------------------------------------------

SCRIPT_MD = REPO / "docs" / "slides" / "script.md"


def test_script_covers_every_slide_and_the_screencast():
    """build_video.py fails loudly on a malformed script; so does the suite."""
    body = SCRIPT_MD.read_text(encoding="utf-8").split("\n## The lines\n", 1)[1]
    body = body.split("\n---\n", 1)[0]
    heads = re.findall(r"^### (.+)$", body, flags=re.M)
    slides = [int(m.group(1)) for h in heads if (m := re.match(r"Slide (\d+)", h))]
    assert slides == list(range(1, 16)), f"script covers slides {slides}"
    assert sum(1 for h in heads if h.startswith("Screencast")) == 1


def test_every_caption_segment_is_at_most_22_words():
    """The cap the card sets, checked on the committed source rather than on a build."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_video", REPO / "docs" / "video" / "build_video.py")
    bv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bv)
    slides, cast = bv.parse_script()
    for n, blocks in slides.items():
        for block in blocks:
            for seg in bv.segment(block):
                assert len(seg.split()) <= 22, f"slide {n}: {len(seg.split())} words - {seg}"
                assert bv.duration(seg) >= 3.0
    for block in cast:
        assert len(block.split()) <= 22, f"screencast caption: {len(block.split())} words"
    assert len(slides[12]) == 4, "slide 12's four-step reveal needs exactly four blocks"
    assert slides[1] == [] and slides[15] == [], "slides 1 and 15 carry no caption"
