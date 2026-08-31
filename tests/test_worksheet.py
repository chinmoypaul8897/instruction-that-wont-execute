"""CH-12 - the codification worksheet must open offline from a clean clone.

The load-bearing assertion is `test_no_external_resource_reference`: the page may
not pull a single byte from the network. A judge double-clicks
`docs/worksheet/index.html` on a machine with the wifi off and sees the whole thing.

One subtlety this file takes seriously rather than legislating away. A naive guard
would be `assert "http://" not in html`, and it would FAIL - not because the page
references anything, but because the *Federal Register text this page renders*
contains a URL: 40 CFR 75.6 tells the reader to "go to:
http://www.archives.gov/...". That is corpus content, escaped and printed inside a
text block, with no anchor around it and no request made for it. Deleting the item
to make the grep pass would be tampering with the corpus to make a test green (hard
rule 5). So the guard is written to the real property - *no external RESOURCE
REFERENCE* - and it additionally proves that every scheme-like substring on the page
lies inside a rendered-text block. `test_scheme_strings_are_corpus_text_only` is the
one that would catch a smuggled reference that the tag scan missed.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "worksheet" / "index.html"
GENERATOR = ROOT / "docs" / "evidence" / "ch12" / "build_worksheet.py"
ITEMS = ROOT / "data" / "evalset" / "items.jsonl"
ARTIFACTS = ROOT / "docs" / "evidence" / "ch06-a1" / "A1-rep1-artifacts.jsonl"
SUMMARY = ROOT / "docs" / "evidence" / "ch06-a1" / "A1-rep1.json"


@pytest.fixture(scope="module")
def html_text() -> str:
    assert PAGE.exists(), f"{PAGE} does not exist - run {GENERATOR}"
    return PAGE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def artifacts() -> list[dict]:
    return [json.loads(line) for line in
            ARTIFACTS.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture(scope="module")
def items() -> dict[str, dict]:
    return {json.loads(line)["item_id"]: json.loads(line) for line in
            ITEMS.read_text(encoding="utf-8").splitlines() if line.strip()}


# --------------------------------------------------------------------------------
# 1. SELF-CONTAINMENT - the assertion the chunk card requires
# --------------------------------------------------------------------------------

#: Every HTML construct that can cause a browser to fetch something.
FETCHING_TAGS = (
    "script", "link", "img", "iframe", "object", "embed", "source", "track",
    "video", "audio", "base", "frame", "frameset", "input", "form", "applet",
    "portal",
)

#: Every attribute that can carry a URL a browser will fetch.
FETCHING_ATTRS = (
    "src", "href", "srcset", "data", "action", "formaction", "poster",
    "background", "codebase", "cite", "ping", "manifest", "archive",
    # Added at CH-12 after this chunk's own adversarial audit pointed out that an
    # enumerated allowlist is only as good as the enumeration. These were missing:
    "http-equiv",          # <meta http-equiv="refresh" content="0;url=...">
    "imagesrcset", "usemap", "profile", "longdesc", "dynsrc", "lowsrc",
)

#: Constructs that fetch without any of the tags or attributes above.
FETCHING_MISC = (
    "@import", "url(", "@font-face", "image-set(", "-webkit-image-set(",
    "javascript:", "data:text/html", "srcdoc",
)


def test_no_external_resource_reference(html_text: str) -> None:
    """No tag, attribute or CSS construct that can cause a network fetch."""
    lowered = html_text.lower()

    for tag in FETCHING_TAGS:
        assert f"<{tag}" not in lowered, (
            f"the worksheet contains a <{tag}> element; the page must fetch nothing")

    for attr in FETCHING_ATTRS:
        assert not re.search(rf"\b{attr}\s*=", lowered), (
            f"the worksheet carries a '{attr}=' attribute; the page must fetch nothing")

    for css in FETCHING_MISC:
        assert css not in lowered, (
            f"the worksheet uses '{css}'; every style must be inline, every font a "
            f"system fallback, and nothing may resolve a URL at render time")

    # An inline event handler is script, and script can fetch. There is no `on*=`
    # attribute the page legitimately needs.
    handlers = re.findall(r"\son[a-z]+\s*=", lowered)
    assert not handlers, f"inline event handler(s) on the page: {sorted(set(handlers))}"

    # `<meta http-equiv="refresh">` navigates without any fetching attribute at all.
    assert not re.search(r"http-equiv\s*=\s*[\"']?\s*refresh", lowered), (
        "the worksheet carries a meta refresh; the page must not navigate")


def _corpus_text_spans(html_text: str) -> list[tuple[int, int]]:
    """Byte spans of the rendered corpus-text blocks - `<div class="txt">...</div>`."""
    spans = [(m.start(), m.end()) for m in
             re.finditer(r'<div class="txt">.*?</div>', html_text, re.S)]
    assert spans, "no rendered corpus-text blocks found - the page is not the worksheet"
    return spans


def test_scheme_strings_are_corpus_text_only(html_text: str) -> None:
    """`http://`, `https://` and protocol-relative `//` may appear ONLY inside a
    rendered corpus-text block - never anywhere a browser could act on them.

    This is the guard that catches what a tag scan cannot: a scheme smuggled into
    an inline style, a comment, or text that is later wired up.
    """
    text_blocks = _corpus_text_spans(html_text)

    def inside_corpus_text(index: int) -> bool:
        return any(start <= index < end for start, end in text_blocks)

    offenders = []
    for pattern in (r"https?://", r"(?<![:\w])//"):
        for m in re.finditer(pattern, html_text):
            if not inside_corpus_text(m.start()):
                line = html_text.count("\n", 0, m.start()) + 1
                offenders.append(
                    f"line {line}: {html_text[max(0, m.start() - 60):m.start() + 60]!r}")

    assert not offenders, (
        "scheme-like text outside a rendered corpus-text block:\n" + "\n".join(offenders))


def test_scheme_strings_that_do_occur_are_inert(html_text: str) -> None:
    """The corpus URLs that DO appear are inert: printed, never linked.

    Zero-occurrence branches print as zeros (hard rule 14), so this test reports the
    count it found rather than only asserting a bound.
    """
    occurrences = list(re.finditer(r"https?://", html_text))
    print(f"scheme strings rendered as corpus text: {len(occurrences)}")

    assert "<a " not in html_text.lower(), (
        "the worksheet contains an anchor element; corpus URLs must stay inert text")

    spans = _corpus_text_spans(html_text)
    for m in occurrences:
        assert any(start <= m.start() < end for start, end in spans), (
            "a scheme string is rendered outside a corpus-text block: "
            f"{html_text[max(0, m.start() - 80):m.start() + 80]!r}")


def test_opens_as_a_standalone_document(html_text: str) -> None:
    """A `file://` open with no server needs a complete, self-describing document."""
    assert html_text.startswith("<!DOCTYPE html>")
    assert '<meta charset="utf-8">' in html_text
    assert "<style>" in html_text and "</style>" in html_text
    assert html_text.rstrip().endswith("</html>")

    # A system-font stack only. The previous version of this assertion was
    # `assert "font-family" in html_text`, which tests that the string occurs, not
    # that the property holds — it would pass on `font-family:'SomeRemoteFont'` with
    # no fallback at all. This checks the actual property: every stack ends in a
    # generic family the browser already has.
    GENERIC = ("serif", "sans-serif", "monospace", "system-ui", "ui-monospace",
               "ui-serif", "ui-sans-serif", "cursive", "fantasy")
    stacks = re.findall(r"font(?:-family)?\s*:\s*([^;}]+)", html_text)
    assert stacks, "no font declaration at all"
    for stack in stacks:
        last = stack.strip().rstrip('"\'').split(",")[-1].strip().strip('"\'')
        assert last in GENERIC, (
            f"font stack does not end in a generic family the browser already has: "
            f"{stack.strip()!r} (ends {last!r})")
    print(f"font stacks checked: {len(stacks)}, all ending in a generic family")


# --------------------------------------------------------------------------------
# 2. THE THREE THINGS THE PAGE MUST CARRY
# --------------------------------------------------------------------------------

def _flat(text: str) -> str:
    """Collapse whitespace so a phrase check is not defeated by a line wrap."""
    return re.sub(r"\s+", " ", text)


def test_disclaimer_band_is_present_and_says_what_it_must(html_text: str) -> None:
    band = re.search(r'<div class="band">(.*?)</div>', html_text, re.S)
    assert band, "no disclaimer band"
    body = _flat(band.group(1))
    # It must appear before any item, i.e. at the top of the page.
    assert html_text.index('<div class="band">') < html_text.index('<section class="item"')
    assert "NOT A FILING" in body
    assert "input to a licensed regulations drafter's judgement" in body
    assert "has been reviewed by a qualified regulations drafter" in body
    assert "takes no consequential action" in body
    assert "does not file anything" in body


def test_provenance_footer_names_commit_arm_model_and_artifacts(
        html_text: str, artifacts: list[dict]) -> None:
    footer = re.search(r"<footer>(.*?)</footer>", html_text, re.S)
    assert footer, "no provenance footer"
    body = footer.group(1)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert "89d58c5" in body, "footer does not name the artifact commit"
    assert "76e2e4b" in body, "footer does not name the eval-set commit"
    assert f"<code>{summary['arm']}</code>" in body, "footer does not name the arm"
    assert summary["model"] in body, "footer does not name the model"
    assert "committed artifacts" in body

    # The SHA-256 of every input the generator read is printed, and is correct.
    for path in (ITEMS, ARTIFACTS, SUMMARY):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest in body, f"footer does not carry the sha256 of {path.name}"


def test_human_checkpoint_queue_is_its_own_section(
        html_text: str, artifacts: list[dict]) -> None:
    routed = [a for a in artifacts if a["needs_human_review"]]
    assert len(routed) == 16, f"expected 16 routed items, artifacts hold {len(routed)}"

    heading = re.search(r"<h2>Human-checkpoint queue[^<]*</h2>", html_text)
    assert heading, "no human-checkpoint queue section"
    assert f"{len(routed)} of {len(artifacts)}" in heading.group(0)

    tail = html_text[heading.end():]
    for a in routed:
        assert a["item_id"] in tail, f"{a['item_id']} routed but absent from the queue"
        # the reason ships verbatim, not summarised
        first_clause = a["review_reason"].split(";")[0].strip()
        assert first_clause.replace("'", "&#x27;") in tail or first_clause in tail, (
            f"{a['item_id']}'s reason is not printed verbatim")


# --------------------------------------------------------------------------------
# 3. THE NUMBERS ON THE PAGE ARE THE NUMBERS IN THE ARTIFACTS
# --------------------------------------------------------------------------------

def test_headline_numbers_match_the_committed_artifacts(
        html_text: str, artifacts: list[dict], items: dict[str, dict]) -> None:
    n = len(artifacts)
    agree = sum(1 for a in artifacts if a["verdict"] == items[a["item_id"]]["label"])
    assert (n, agree) == (82, 59), f"artifacts moved: n={n}, agree={agree}"
    assert f"{agree} / {n} = {agree / n:.4f}" in html_text
    assert "0.7195" in html_text, "the page does not carry A1's published accuracy"


def test_normalisation_level_census_matches_and_prints_its_zero(
        html_text: str, artifacts: list[dict]) -> None:
    census: dict[str, int] = {}
    for a in artifacts:
        for t in a["resolution_trace"]:
            key = t["level"] or "none"
            census[key] = census.get(key, 0) + 1
    assert census == {"none": 130, "exact": 74, "alphanumeric-only": 4}, census

    # hard rule 14: the zero-occurrence branch prints as a zero
    row = re.search(r"<code>whitespace-collapsed</code></td><td class=\"num\">(\d+)</td>",
                    html_text)
    assert row, "the whitespace-collapsed row is missing rather than zero"
    assert row.group(1) == "0"

    for level, count in census.items():
        assert re.search(rf"<code>{re.escape(level)}</code></td><td class=\"num\">{count}</td>",
                         html_text), f"level {level} count {count} not on the page"


def test_every_rendered_item_carries_the_five_required_fields(
        html_text: str, artifacts: list[dict]) -> None:
    """section · verdict · failing designation · failure class · resolution trace."""
    sections = re.findall(r'<section class="item".*?</section>', html_text, re.S)
    assert len(sections) >= 6, f"only {len(sections)} items rendered; the card asks for a handful"

    by_id = {a["item_id"]: a for a in artifacts}
    for block in sections:
        item_id = re.search(r'<span class="pill">([^<]+)</span>', block).group(1)
        a = by_id[item_id]
        assert "CFR" in block, f"{item_id}: no section designation"
        assert f'<span class="verdict {a["verdict"]}">' in block
        assert "failing designation" in block
        assert "failure class" in block
        assert "Resolution trace" in block
        if a["failing_designation"]:
            assert f'<code>{a["failing_designation"]}</code>' in block, (
                f"{item_id}: failing designation {a['failing_designation']} not shown")
        if a["failure_class"]:
            assert f'<code>{a["failure_class"]}</code>' in block
        # one trace row per instruction
        rows = block.count('<td class="num">')
        assert rows == len(a["resolution_trace"]), (
            f"{item_id}: {rows} trace rows for {len(a['resolution_trace'])} instructions")


def test_every_resolvable_anchor_is_actually_highlighted(
        html_text: str, artifacts: list[dict], items: dict[str, dict]) -> None:
    """One `<mark>` per rendered item that resolved an anchor at a char_offset.

    This test exists because the page failed it. `highlight()` used to draw nothing
    whenever the text at `char_offset` was not byte-identical to the quoted anchor —
    which is precisely the case at `whitespace-collapsed` and `alphanumeric-only`,
    where the offset points at the text that matched AFTER punctuation was dropped.
    Two of the ten rendered items resolved that way and both rendered as if nothing
    had been found: a normalisation level applied silently, which hard rule 7 forbids.

    Counting caught it. Reading the page did not.
    """
    rendered = set(re.findall(r'<span class="pill">([^<]+)</span>', html_text))
    by_id = {a["item_id"]: a for a in artifacts}

    expected = 0
    loose_expected = 0
    for item_id in rendered:
        hit = next((t for t in by_id[item_id]["resolution_trace"]
                    if t["found"] and t["char_offset"] is not None), None)
        if not hit:
            continue
        expected += 1
        text = items[item_id]["section_text"]
        off, anchor = hit["char_offset"], hit["anchor"]
        if text[off:off + len(anchor)] != anchor:
            loose_expected += 1

    marks = len(re.findall(r"<mark[ >]", html_text))
    loose = len(re.findall(r'<mark class="loose">', html_text))
    print(f"rendered items with a resolvable anchor: {expected}; "
          f"of which the codified text diverges from the quote: {loose_expected}")

    assert marks == expected, (
        f"{marks} <mark> tags for {expected} resolvable anchors — a resolved anchor "
        f"is being rendered as if it had not resolved")
    assert loose == loose_expected, (
        f"{loose} loose marks for {loose_expected} divergent matches")
    assert html_text.count("THE CODIFIED TEXT IS NOT THE QUOTED TEXT") == loose_expected, (
        "a match that needed punctuation dropped is not named as one; hard rule 7 "
        "says the level achieved is reported, never applied silently")


def test_the_resolver_override_exemplar_is_shown(html_text: str) -> None:
    """The run where the model overrode its own tool and named the tool's limit.

    `docs/evidence/ch06-a1/EXEMPLAR-composition.md` is the published note; this is
    the row it is about, and losing it from the page would lose the finding.
    """
    assert "05-8447|75.31" in html_text
    assert "MODEL OVERRODE THE TOOL" in html_text
    assert "cannot see nested designations" in html_text


def test_siblings_are_shown_when_a_designation_does_not_exist(
        html_text: str, artifacts: list[dict]) -> None:
    """The card's requirement: the sibling designations when it did not resolve."""
    rendered = set(re.findall(r'<span class="pill">([^<]+)</span>', html_text))
    by_id = {a["item_id"]: a for a in artifacts}
    checked = 0
    for item_id in rendered:
        for t in by_id[item_id]["resolution_trace"]:
            if t["designation_exists"] is False and t["siblings"]:
                for sibling in t["siblings"]:
                    assert f"<code>{sibling}</code>" in html_text, (
                        f"{item_id}: sibling {sibling} not shown for a missing designation")
                checked += 1
    print(f"missing-designation traces whose siblings were checked: {checked}")
    assert checked > 0, "no missing-designation trace was rendered; the worksheet's core case is absent"


# --------------------------------------------------------------------------------
# 4. DETERMINISM - hard rule 9
# --------------------------------------------------------------------------------

def test_regenerating_the_page_is_byte_identical(html_text: str, tmp_path) -> None:
    """The generator is pure: no clock, no network, no randomness, no `git`."""
    before = PAGE.read_bytes()
    result = subprocess.run([sys.executable, str(GENERATOR)],
                            capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 0, result.stderr
    after = PAGE.read_bytes()
    assert hashlib.sha256(before).hexdigest() == hashlib.sha256(after).hexdigest(), (
        "regenerating the worksheet changed its bytes; the generator is not pure")


def test_generator_touches_neither_the_clock_nor_the_network(  ) -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    body = "\n".join(line for line in source.splitlines()
                     if not line.lstrip().startswith("#"))
    for forbidden in ("import requests", "urllib.request", "socket", "datetime.now",
                      "time.time", "random.", "subprocess"):
        assert forbidden not in body, (
            f"the worksheet generator references {forbidden}; it must be pure")
