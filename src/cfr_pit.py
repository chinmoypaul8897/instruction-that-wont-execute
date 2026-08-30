"""CH-03 · 1b/1c — point-in-time CFR section text from govinfo annual editions,
with the leakage strips that stop this being a rigged benchmark.

    https://www.govinfo.gov/bulkdata/CFR/{year}/title-{n}/CFR-{year}-title{n}-vol{v}.xml

`www.ecfr.gov` and `www.federalregister.gov` are HTTP 403 from this machine
(`CLAUDE.md`, binding). govinfo is the sole harvest channel.

THE EDITION
-----------
*"For each defect section, the edition preceding its rule's publication date"* —
operationalised as **the latest annual edition whose statutory revision date is
STRICTLY BEFORE the publication date**. Strictly-before is the whole point: an edition
revised *on* the publication date could already contain the amendment under test.
CFR revision dates: titles 1–16 Jan 1 · 17–27 Apr 1 · 28–41 Jul 1 · 42–50 Oct 1.
Goldens G-A.

THE LEAKAGE STRIPS - and why a zero here is not believed
---------------------------------------------------------
`CONTEXT.md` §8 requires `<EDNOTE>`, `<EFFDNOTP>`, `<CITA>` and `<EAR>` stripped and
counted before any text is frozen, because **the label and the input come from the
same XML tree**:

    <EDNOTE>   carries the editorial note that IS the label
    <EFFDNOTP> prints the pending amendment - the rule under test - VERBATIM, and
               says so: "For the convenience of the user, the revised and added
               text is set forth as follows."
    <CITA>     source credit naming the amending rule
    <EAR>      editorial amendment record

**Q8's trap, and it is a trap.** Element names are format-dependent: ECFR bulk XML has
no `<SECTION>` element at all. These four names are correct for CFR annual editions,
which is what this module reads — but *a counter that prints zero because it is
looking for the wrong name is indistinguishable from a corpus that is genuinely
clean*. So `assert_stripper_on_known_positive()` exists, is run before any freeze, and
its expected counts were hand-computed in `goldens.md` G-B from raw bytes.

**THE NESTED-SECTION TRAP** (goldens G-E), found by reading the bytes rather than the
spec. `CFR-2024-title40-vol5.xml` holds 313 `<SECTION>` elements, **2 of which are
nested inside an `<EFFDNOTP>/<REVTXT>`** — a verbatim copy of the pending amendment,
24,455 characters of it for § 52.2320. A lookup that takes any `<SECTION>` with a
matching `<SECTNO>` can therefore return **the leak itself**. Only a `<SECTION>` with
no `EDNOTE`/`EFFDNOTP`/`REVTXT` ancestor is eligible.

PURITY - hard rule 8: every function from `revision_date` to `leakage_violations` is
pure. Network lives in `fetch_volume` / `volume_index` and nowhere else.
DETERMINISM - hard rule 9: no clock, no randomness; JSON sorted, LF endings.
"""
from __future__ import annotations

import copy
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

USER_AGENT = "micro1-frontier-challenge CH-03 CFR annual-edition harvest"
BULK_JSON = "https://www.govinfo.gov/bulkdata/json/CFR/{year}/title-{title}"
DEFAULT_RAW_DIR = Path("data/raw/cfr")

# The four elements CONTEXT.md section 8 names. Order is fixed so the counts dict is
# byte-identical run to run (hard rule 9).
LEAKAGE_ELEMENTS = ("EDNOTE", "EFFDNOTP", "CITA", "EAR")

# A <SECTION> inside any of these is a REPRINT of an amendment, not the codified text.
REPRINT_ANCESTORS = ("EDNOTE", "EFFDNOTP", "REVTXT")

# plan.md's leakage test, literal (c).
LEAKAGE_LITERALS = (
    "could not be incorporated",
    "Editorial Note",
    "Effective Date Note",
    "set forth as follows",
)

# govinfo CFR annual editions start at 1996.
EARLIEST_EDITION = 1996


class PitError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips."""


# ============================================================ pure: the edition

def revision_month_day(title: int) -> tuple[int, int]:
    """The CFR's statutory revision date for a title. Goldens G-A."""
    t = int(title)
    if not 1 <= t <= 50:
        raise PitError(f"CFR title out of range: {title!r}")
    if t <= 16:
        return 1, 1
    if t <= 27:
        return 4, 1
    if t <= 41:
        return 7, 1
    return 10, 1


def revision_date(title: int, year: int) -> date:
    m, d = revision_month_day(title)
    return date(int(year), m, d)


def edition_year(title: int, publication_date: str) -> int:
    """The latest annual edition revised STRICTLY BEFORE `publication_date`.

    `publication_date` is `YYYY-MM-DD`. Pure - no clock, so a golden can pin a
    future-dated rule (G-A3 uses 2026-06-10) and get the same answer forever.
    """
    y, m, d = (int(x) for x in publication_date.split("-"))
    pub = date(y, m, d)
    year = pub.year
    while revision_date(title, year) >= pub:
        year -= 1
        if year < EARLIEST_EDITION - 1:
            raise PitError(
                f"no CFR annual edition precedes {publication_date} for title {title}")
    return year


# ============================================================ pure: volume ranges

_SECTION_TOKEN = re.compile(r"\d+[A-Za-z]?\.[0-9A-Za-z][0-9A-Za-z.\-]*")
_INT = re.compile(r"\d+")


def section_sort_key(section: str):
    """A NUMERIC ordering key for a CFR section number. Goldens G-G2.

    Lexicographically `1.908` > `1.1000` and `1.61` > `1.169`, both wrong, and a
    lexicographic comparator would send every title-26 lookup to the wrong volume
    SILENTLY - the section would simply not be found and the item would drop off the
    exclusion ladder as "not in the as-of edition". A wrong answer that presents as a
    smaller n rather than as an error is the exact failure this project exists to
    catch.

    The suffix is tokenised into runs of digits and runs of non-digits; a digit run
    sorts as (0, int) and a non-digit run as (1, str), so an int is never compared
    against a str.
    """
    part, _, rest = section.partition(".")
    pm = _INT.match(part)
    part_key = int(pm.group(0)) if pm else 0
    tokens = []
    for tok in re.findall(r"\d+|\D+", rest):
        tokens.append((0, int(tok), "") if tok.isdigit() else (1, 0, tok))
    return (part_key, tuple(tokens))


def parse_parts_header(header: str) -> dict:
    """`<PARTS>` -> {part_lo, part_hi, section_lo, section_hi}. Goldens G-G.

    Handles `Parts 53 to 59`, `Part 52`, `Part 80 to End` (part_hi None = unbounded)
    and the within-part split `Part 1 (§§ 1.908 to 1.1000)` that title 26 and title 40
    part 63 use. `part_hi is None` means "to End".

    The separator is NOT split on: the parenthesised range can use `to`, an em-dash or
    an en-dash, and a real section number can itself contain a hyphen (`1.199A-0`). So
    every section-shaped token inside the parentheses is collected and the first and
    last are taken.
    """
    text = " ".join((header or "").split())
    paren = ""
    m = re.search(r"\((.*)\)", text)
    if m:
        paren = m.group(1)
        text_before = text[:m.start()]
    else:
        text_before = text

    ints = [int(x) for x in _INT.findall(text_before)]
    part_lo = ints[0] if ints else None
    if re.search(r"\bEnd\b", text_before):
        part_hi = None
    elif len(ints) >= 2:
        part_hi = ints[-1]
    else:
        part_hi = part_lo

    sec_lo = sec_hi = None
    if paren:
        toks = _SECTION_TOKEN.findall(paren)
        if toks:
            sec_lo, sec_hi = toks[0], toks[-1]
            if re.search(r"\bEnd\b", paren):
                sec_hi = None
    return {"part_lo": part_lo, "part_hi": part_hi,
            "section_lo": sec_lo, "section_hi": sec_hi, "raw": header,
            # REVIEW FINDING F2. A SINGLE-VOLUME TITLE CARRIES NO <PARTS> ELEMENT AT
            # ALL - CFR-2016-title13-vol1.xml has none in 4,157,015 bytes. Without
            # this flag `part_lo` is None, `volume_covers` returns (False, False) for
            # every part, `candidate_volumes` returns [], and the declared G-G2
            # fallback cannot fire because it is itself gated on covers_part. The
            # section is then dropped as "not in the as-of edition" - a wrong answer
            # presenting as a smaller n rather than as an error, which is the exact
            # shape goldens.md G-G2 warned about.
            "declares_range": part_lo is not None}


def volume_covers(rng: dict, part: str, section: str) -> tuple[bool, bool]:
    """(covers_part, covers_section). Pure.

    `covers_section` is True when the volume carries no section range at all — a
    volume covering whole parts covers every section in them.
    """
    try:
        p = int(re.match(r"\d+", str(part)).group(0))
    except (AttributeError, TypeError, ValueError):
        return False, False
    lo, hi = rng["part_lo"], rng["part_hi"]
    if lo is None:
        # F2: no declared range means a single-volume title, which covers the WHOLE
        # title. Searching it and finding nothing is a real answer; refusing to search
        # it and reporting "not in the as-of edition" is a fabricated one.
        return True, True
    covers_part = p >= lo and (hi is None or p <= hi)
    if not covers_part:
        return False, False
    if rng["section_lo"] is None:
        return True, True
    k = section_sort_key(section)
    if k < section_sort_key(rng["section_lo"]):
        return True, False
    if rng["section_hi"] is not None and k > section_sort_key(rng["section_hi"]):
        return True, False
    return True, True


def candidate_volumes(index: list[dict], part: str, section: str) -> list[dict]:
    """Volumes to search, best first. Goldens G-G2's declared fallback.

    Tier 1 - the part AND the section range match.
    Tier 2 - the part matches but the section range does not.  <- the fallback that
             stops a range-parsing error becoming a silent exclusion.
    Volumes that do not cover the part at all are not searched.
    """
    tier1, tier2 = [], []
    for vol in index:
        cp, cs = volume_covers(vol["range"], part, section)
        if cp and cs:
            tier1.append(vol)
        elif cp:
            tier2.append(vol)
    key = lambda v: v["name"]                                    # noqa: E731
    return sorted(tier1, key=key) + sorted(tier2, key=key)


# ============================================================ pure: the XML

def _parent_map(root: ET.Element) -> dict:
    return {child: parent for parent in root.iter() for child in parent}


def eligible_sections(root: ET.Element) -> list[ET.Element]:
    """Every `<SECTION>` that is CODIFIED TEXT, not a reprint of an amendment.

    Goldens G-E. A `<SECTION>` nested inside `<EDNOTE>`, `<EFFDNOTP>` or `<REVTXT>` is
    the pending rule printed for the reader's convenience - i.e. it is the answer -
    and must never be selected, frozen or shown to an arm.
    """
    parents = _parent_map(root)
    out = []
    for sec in root.iter("SECTION"):
        node, reprint = sec, False
        while node in parents:
            node = parents[node]
            if node.tag in REPRINT_ANCESTORS:
                reprint = True
                break
        if not reprint:
            out.append(sec)
    return out


def sectno_text(sec: ET.Element) -> str | None:
    el = sec.find("SECTNO")
    if el is None:
        return None
    return " ".join("".join(el.itertext()).split())


def sectno_number(sec: ET.Element) -> str | None:
    """`<SECTNO>§ 52.2320</SECTNO>` -> `52.2320`. Also takes `§§ 52.10-52.12` forms,
    returning the first number, and the sign-less spelling some volumes use."""
    raw = sectno_text(sec)
    if not raw:
        return None
    m = _SECTION_TOKEN.search(raw)
    return m.group(0).rstrip(".") if m else None


def find_section(root: ET.Element, section: str) -> tuple[ET.Element | None, int]:
    """(the eligible SECTION for `section`, number of eligible candidates).

    Returns the FIRST eligible match and the count, so a caller can report an
    ambiguity rather than silently taking one of several. Goldens G-E expects exactly
    one eligible candidate for `52.2320` even though the volume holds two `<SECTION>`
    elements with that `<SECTNO>`.
    """
    hits = [s for s in eligible_sections(root) if sectno_number(s) == section]
    return (hits[0] if hits else None), len(hits)


def strip_leakage(sec: ET.Element) -> tuple[ET.Element, dict]:
    """Remove and COUNT every leakage element. Returns (a stripped copy, counts).

    Pure: the input element is never mutated, so a caller can measure the unstripped
    text and the stripped text from the same tree - which is exactly what the
    fails-on-unstripped demonstration needs.
    """
    clone = copy.deepcopy(sec)
    counts = {tag: 0 for tag in LEAKAGE_ELEMENTS}
    # Repeat until stable: removing a parent can expose nothing new, but a leakage
    # element nested inside another one must not be double-counted, so a removed
    # subtree is counted whole before it goes.
    while True:
        parents = _parent_map(clone)
        target = None
        for el in clone.iter():
            if el.tag in LEAKAGE_ELEMENTS and el in parents:
                target = el
                break
        if target is None:
            break
        for inner in target.iter():
            if inner.tag in LEAKAGE_ELEMENTS:
                counts[inner.tag] += 1
        parents[target].remove(target)
    # The root itself being a leakage element would mean the caller passed one in.
    if clone.tag in LEAKAGE_ELEMENTS:
        raise PitError(f"strip_leakage was handed a <{clone.tag}> as the root")
    counts["total"] = sum(counts[t] for t in LEAKAGE_ELEMENTS)
    return clone, counts


def section_text(sec: ET.Element) -> str:
    """The section's readable text. Whitespace-collapsed per line, blank-line
    separated between block elements, so an arm sees prose rather than XML.

    Hard rule 7: the normalisation level is DECLARED - `whitespace-collapsed` - and
    reported in every frozen record. Paragraph designations and quoted anchors pass
    through unaltered: no unicode folding, no smart-quote substitution.
    """
    blocks: list[str] = []

    def walk(el: ET.Element) -> None:
        if el.tag in ("SECTNO", "SUBJECT", "P", "FP", "HD", "EXTRACT", "ENT", "CHED"):
            t = " ".join("".join(el.itertext()).split())
            if t:
                blocks.append(t)
            return
        if el.text and el.text.strip():
            blocks.append(" ".join(el.text.split()))
        for child in el:
            walk(child)
            if child.tail and child.tail.strip():
                blocks.append(" ".join(child.tail.split()))

    walk(sec)
    return "\n".join(blocks)


# ============================================================ pure: the leakage test

def leakage_violations(text: str, fr_citation: str | None) -> list[dict]:
    """`plan.md`'s leakage-strip test, over the FROZEN TEXT.

    Fires on (a) a residual leakage element name, (b) the FR citation of the rule
    under test, (c) any of the four literals. Returns one dict per violation, so the
    caller reports WHICH rule fired rather than a bare boolean.

    Rule (a) is checked on the text rather than the tree on purpose: the text is what
    an arm is shown, and a stripper that removed the element but left its rendered
    heading behind would pass a tree check and fail a reader.
    """
    out = []
    for tag in LEAKAGE_ELEMENTS:
        if f"<{tag}" in text or f"</{tag}>" in text:
            out.append({"rule": "a", "kind": "element", "detail": tag})
    if fr_citation:
        norm = " ".join(fr_citation.split())
        if norm and norm in " ".join(text.split()):
            out.append({"rule": "b", "kind": "own-fr-citation", "detail": norm})
    flat = " ".join(text.split())
    for lit in LEAKAGE_LITERALS:
        if lit in flat:
            out.append({"rule": "c", "kind": "literal", "detail": lit})
    return out


# ============================================================ the known-positive assert

KNOWN_POSITIVE_XML = """<SECTION>
  <SECTNO>&#167; 99.9</SECTNO>
  <SUBJECT>A fixture.</SUBJECT>
  <P>(a) Ordinary codified text.</P>
  <EDNOTE><HD SOURCE="HED">Editorial Note:</HD><P>note one.</P></EDNOTE>
  <EDNOTE><HD SOURCE="HED">Editorial Note:</HD><P>note two.</P></EDNOTE>
  <EFFDNOTP><HD SOURCE="HED">Effective Date Note:</HD>
    <P>At 90 FR 1, Jan. 1, 2025, this was amended; the text is set forth as follows:</P>
    <REVTXT><SECTION><SECTNO>&#167; 99.9</SECTNO><P>(a) THE PENDING TEXT.</P></SECTION></REVTXT>
  </EFFDNOTP>
  <CITA>[70 FR 1, Jan. 1, 2005]</CITA>
  <CITA>[71 FR 2, Jan. 2, 2006]</CITA>
  <CITA>[72 FR 3, Jan. 3, 2007]</CITA>
  <EAR>&#167; 99.9, Nt.</EAR>
  <P>(b) More ordinary codified text.</P>
</SECTION>"""

# Hand-computed in goldens.md G-B3, before this module existed.
KNOWN_POSITIVE_EXPECTED = {"EDNOTE": 2, "EFFDNOTP": 1, "CITA": 3, "EAR": 1, "total": 7}


def assert_stripper_on_known_positive() -> dict:
    """A strip counter that prints zero may simply be looking for the wrong element
    name (`QUESTIONS.md` Q8). **This is the assertion that stops a zero being
    believed**, and it runs before any freeze.

    Returns the measured counts. Raises `PitError` if they differ from the
    hand-computed expectation, or if the stripped text still leaks.
    """
    sec = ET.fromstring(KNOWN_POSITIVE_XML)
    raw_text = section_text(sec)
    stripped_el, counts = strip_leakage(sec)
    stripped_text = section_text(stripped_el)

    if counts != KNOWN_POSITIVE_EXPECTED:
        raise PitError(
            f"stripper known-positive FAILED: {counts} != {KNOWN_POSITIVE_EXPECTED}. "
            "The counter is not seeing the elements it claims to count, so no zero "
            "it prints anywhere else may be believed.")
    before = leakage_violations(raw_text, "90 FR 1")
    if not before:
        raise PitError(
            "the leakage TEST does not fire on a known-positive UNSTRIPPED input. "
            "An unfalsifiable test is not evidence of a clean corpus.")
    after = leakage_violations(stripped_text, "90 FR 1")
    if after:
        raise PitError(f"stripped known-positive still leaks: {after}")
    if "THE PENDING TEXT" in stripped_text:
        raise PitError("the nested REVTXT copy of the pending amendment survived")
    return {"counts": counts, "violations_before": before, "violations_after": after,
            "chars_before": len(raw_text), "chars_after": len(stripped_text)}


# ============================================================ I/O: govinfo

def _get(url: str, timeout: int = 300, accept: str | None = None) -> bytes:
    """MEASURED, not assumed: the govinfo bulkdata JSON endpoint serves an HTML error
    page unless `Accept: application/json` is sent. Without the header the listing
    parses as a JSONDecodeError and every lookup fails - which it did on the first
    build, loudly, as 50 items on the `section-not-in-as-of-edition` rung rather than
    as a silent empty corpus. The rung is why it took one run to find."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _get_head(url: str, n: int, timeout: int = 300) -> bytes:
    """Read only the first `n` bytes of a URL. govinfo ignores Range on bulkdata, so
    this streams and stops rather than pretending a 206 will come back."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(n)


_PARTS_RE = re.compile(rb"<PARTS>(.*?)</PARTS>", re.S)
_REVISED_RE = re.compile(rb"<REVISED>(.*?)</REVISED>", re.S)


def volume_index(title: int, year: int, cache_dir: Path) -> list[dict]:
    """Every XML volume for (title, year) with its parsed part range.

    The range comes from each volume's own `<PARTS>` header, read from the first few
    kilobytes rather than by downloading the volume. The index is cached to disk, so
    a re-run is offline and `refetch.py --verify-only` never touches the network.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"index-title{title}-{year}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))

    listing = json.loads(_get(BULK_JSON.format(year=year, title=title),
                              accept="application/json"))
    out = []
    for f in listing.get("files", []):
        name = f.get("justFileName", "")
        if not name.endswith(".xml"):
            continue
        head = _get_head(f["link"], 8000)
        pm = _PARTS_RE.search(head)
        rm = _REVISED_RE.search(head)
        raw = " ".join(pm.group(1).decode("utf-8", "replace").split()) if pm else ""
        out.append({
            "name": name,
            "url": f["link"],
            "bytes": f.get("size"),
            "revised": (" ".join(rm.group(1).decode("utf-8", "replace").split())
                        if rm else None),
            "range": parse_parts_header(raw),
        })
    out.sort(key=lambda v: v["name"])
    cache.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n",
                     encoding="utf-8", newline="\n")
    return out


def fetch_volume(vol: dict, raw_dir: Path) -> Path:
    """Download one annual-edition volume into the git-ignored `data/raw/cfr/`.
    Already-present files are not re-fetched."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / vol["name"]
    if path.exists() and path.stat().st_size > 1024:
        return path
    data = _get(vol["url"])
    if len(data) < 1024:
        raise PitError(f"{vol['name']}: {len(data)} B is too small to be a volume")
    path.write_bytes(data)
    return path
