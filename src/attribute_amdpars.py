"""CH-02 - AMDPAR carry-forward attributor over govinfo Federal Register bulk XML.

Implements `CONTEXT.md` section 8's algorithm, not a reading of it:

  1. iterate <AMDPAR> elements in DOCUMENT ORDER - order is the whole mechanism
  2. maintain `current_section`, initially null
  3. an element that names a section sets `current_section` and attributes there
  4. otherwise it attributes to `current_section`; if that is null the element is
     UNATTRIBUTABLE - counted, never guessed
  5. each attributed element parses into (operation, anchor, designation)

and section 8's completeness definition, verbatim:

    completeness = (AMDPAR elements attributed to a section AND parsed into at least
    one complete (operation, anchor OR designation) triple)
                 / (total AMDPAR elements in the document)

The tokenisation section 8 leaves open - what counts as a section citation, which verb
wins when several appear, where a designation may be read from - was fixed by hand in
`docs/evidence/ch02-attributor/goldens.md` (rules P1-P7) and committed BEFORE this file
existed. Commit 98f1cff adds the goldens; this file arrives later. Hard rule 4.

TWO SECTION DETECTORS, BOTH REPORTED (goldens P3, QUESTIONS.md Q9). Section 8 spells
the detector `\\S\\s*[\\d.]+[a-z]?`, which requires the section sign. A large minority
of the corpus - FCC and SEC style - writes `Section 90.209 is amended by ...` with no
sign at all, and on such a document the sign-only detector does not merely under-detect,
it CARRIES THE PREVIOUS SECTION FORWARD ONTO EVERY ONE OF THEM. Both detectors are
computed, both ship, and the gate branch is taken on the spec-literal figure. Nothing is
substituted silently (hard rule 3).

PURITY - hard rule 8. Everything from `collapse_ws` to `completeness` is pure: data in,
results out, no network, no clock, no randomness. The network lives in `fetch_issues`
and the CLI, and nothing in the pure path imports it.

DETERMINISM - hard rule 9. JSON is written with sorted keys and LF endings, so the same
raw bytes give byte-identical artefacts on any platform.

    python -m attribute_amdpars fetch    --raw data/raw/fr
    python -m attribute_amdpars extract  --raw data/raw/fr --out data/amdpars
    python -m attribute_amdpars verify   --out data/amdpars
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ============================================================ constants

BULKDATA_FR = "https://www.govinfo.gov/bulkdata/FR/{y}/{m}/FR-{date}.xml"
USER_AGENT = "micro1-frontier-challenge CH-02 AMDPAR harvest"

DEFAULT_RAW_DIR = Path("data/raw/fr")
DEFAULT_OUT_DIR = Path("data/amdpars")
DEFAULT_POOL = Path("data/ednotes/defect_notes.jsonl")

NORMALISATION = "whitespace-collapsed"          # hard rule 7: declared, never silent

OPERATIONS = ("revise", "add", "remove", "redesignate", "amend")

MONTHS = {}
for _i, _m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"]
):
    MONTHS[_m] = _i + 1
    MONTHS[_m[:3]] = _i + 1
MONTHS["Sept"] = 9                               # FR style abbreviates September so


class AttributorError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips. A load-bearing count that
    stops checking itself under an optimisation flag is exactly the silent green this
    project exists to expose (CH-01 recorded the same reasoning for `tally`)."""


# ============================================================ pure: text

_WS = re.compile(r"\s+")

LQUOTE, RQUOTE = "“", "”"


def collapse_ws(s: str) -> str:
    return _WS.sub(" ", s).strip()


def element_text(el: ET.Element) -> str:
    """Every descendant text node in document order, whitespace-collapsed.

    NOT `el.text`. Many AMDPARs open with an <E T="03"> italic run, so their direct
    text is empty and a reader of `el.text` silently loses the instruction. Goldens
    section 1 pins the case; `QUESTIONS.md` Q8 is the general form of the hazard.
    """
    return collapse_ws("".join(el.itertext()))


def split_quotes(text: str) -> tuple[str, list[str], bool]:
    """Lift quoted spans out (goldens P1).

    Returns (de-quoted text, anchors in document order, unclosed_quote).

    Section, operation and designation are all read from the DE-QUOTED text, so that a
    cross-reference being inserted - `add the cross reference "paragraph (a)(5)"` -
    can never be mistaken for the paragraph being amended. The de-quoted text keeps a
    space where each span was, so word boundaries either side survive.
    """
    out, anchors, i, unclosed = [], [], 0, False
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == LQUOTE:
            j = text.find(RQUOTE, i + 1)
            if j == -1:
                anchors.append(text[i + 1:])
                unclosed = True
                out.append(" ")
                break
            anchors.append(text[i + 1:j])
            out.append(" ")
            i = j + 1
        elif ch == '"':
            j = text.find('"', i + 1)
            if j == -1:
                anchors.append(text[i + 1:])
                unclosed = True
                out.append(" ")
                break
            anchors.append(text[i + 1:j])
            out.append(" ")
            i = j + 1
        else:
            out.append(ch)
            i += 1
    return "".join(out), anchors, unclosed


# ============================================================ pure: the three fields

# Goldens P2. The base handles 1468.3 / 90.213 / 1.1400Z2 / 1.199A. The suffix absorbs
# the parenthesised title-26 forms - 1.367(a)-8, 1.401(a)(31)-1 - but ONLY when a
# trailing -N is present, which is what keeps `90.213(a)` reading as section 90.213
# paragraph (a) rather than as a section literally named "90.213(a)".
_SEC_BASE = r"\d+[A-Za-z]?\.\d+[A-Za-z0-9]*"
_SEC_LONG = _SEC_BASE + r"(?:\([A-Za-z0-9]+\))*-\d+[A-Za-z0-9]*"
_SECTION = rf"(?:{_SEC_LONG}|{_SEC_BASE})"

SIGN_RE = re.compile(r"§+\s*(" + _SECTION + r")")
WORD_RE = re.compile(r"\b[Ss]ections?\s+(" + _SECTION + r")")

_OP_RES = (
    ("revise", re.compile(r"\brevis(?:e|es|ed|ing|ion)\b", re.I)),
    ("add", re.compile(r"\badd(?:s|ed|ing)?\b", re.I)),
    ("remove", re.compile(r"\bremov(?:e|es|ed|ing|al)\b", re.I)),
    ("redesignate", re.compile(r"\bredesignat(?:e|es|ed|ing|ion)\b", re.I)),
)
_AMEND_RE = re.compile(r"\bamend(?:s|ed|ing|ment|ments|atory)?\b", re.I)

DESIG_RE = re.compile(r"(?:\([A-Za-z0-9]{1,4}\))+")


def find_sections(dequoted: str, detector: str = "extended"):
    """Return (sections in document order, spans consumed). Goldens P2/P3.

    `detector` is "spec_literal" (the section sign only, CONTEXT.md section 8's own
    rule) or "extended" (the sign OR the word form `Section 90.209`).
    """
    if detector not in ("spec_literal", "extended"):
        raise AttributorError(f"unknown detector {detector!r}")
    hits = [(m.start(), m.end(), m.group(1)) for m in SIGN_RE.finditer(dequoted)]
    if detector == "extended":
        hits += [(m.start(), m.end(), m.group(1)) for m in WORD_RE.finditer(dequoted)]
    hits.sort()
    return [h[2] for h in hits], [(h[0], h[1]) for h in hits]


def find_operation(dequoted: str) -> str | None:
    """Goldens P4. First of the four specific verbs left-to-right; `amend` only as a
    fallback, because FR drafting subordinates the real verb to it - "Amend section
    236.1 by revising the last two sentences" is a revision, not an amendment."""
    best_pos, best_op = None, None
    for name, rx in _OP_RES:
        m = rx.search(dequoted)
        if m and (best_pos is None or m.start() < best_pos):
            best_pos, best_op = m.start(), name
    if best_op is not None:
        return best_op
    return "amend" if _AMEND_RE.search(dequoted) else None


def find_designations(dequoted: str, section_spans) -> list[str]:
    """Goldens P5. Runs of short parenthesised groups, with any span already consumed
    as a section citation blanked out first so that `1.367(a)-8` cannot donate an `(a)`.
    The four-character limit is what excludes prose parentheses such as
    `( e.g., contracts, grants, ...)`."""
    if section_spans:
        chars = list(dequoted)
        for a, b in section_spans:
            for k in range(a, min(b, len(chars))):
                chars[k] = " "
        dequoted = "".join(chars)
    return [m.group(0) for m in DESIG_RE.finditer(dequoted)]


def parse_amdpar(text: str) -> dict:
    """One AMDPAR's text -> the parse half of the record. Pure.

    The parse is detector-INDEPENDENT: it blanks the `extended` section spans, which
    are a superset of the spec-literal ones, so both attributions read the same
    (operation, anchor, designation). Only attribution differs between detectors.
    """
    dequoted, anchors, unclosed = split_quotes(text)
    sec_ext, spans_ext = find_sections(dequoted, "extended")
    sec_lit, _ = find_sections(dequoted, "spec_literal")
    operation = find_operation(dequoted)
    designations = find_designations(dequoted, spans_ext)
    return {
        "text": text,
        "normalisation": NORMALISATION,
        "sections_named_extended": sec_ext,
        "sections_named_spec_literal": sec_lit,
        "operation": operation,
        "anchor": anchors[0] if anchors else None,
        "anchors": anchors,
        "designation": designations[0] if designations else None,
        "designations": designations,
        "unclosed_quote": unclosed,
        # section 8: an element is parsed only if it has an operation AND at least one
        # of anchor / designation. Attribution alone is not the bar.
        "parsed": bool(operation) and bool(anchors or designations),
    }


# ============================================================ pure: carry-forward

def attribute(texts, detector: str = "spec_literal", regtext_parts=None) -> list[dict]:
    """CONTEXT.md section 8's algorithm. `texts` is one document's AMDPAR texts in
    DOCUMENT ORDER. Reordering breaks the mechanism, so the order of the input list is
    the contract.

    `current_section` starts null at every document and is never reset inside one
    (goldens P7) - not at a <REGTEXT> boundary, because section 8 specifies no such
    reset. Where that carries a section across a part change the record says so in
    `part_mismatch`, rather than the parser quietly repairing it.
    """
    key = f"sections_named_{detector}"
    parts = list(regtext_parts or [None] * len(texts))
    if len(parts) != len(texts):
        raise AttributorError("regtext_parts must be the same length as texts")

    out, current = [], None
    for ordinal, (text, part) in enumerate(zip(texts, parts), start=1):
        rec = parse_amdpar(text)
        named = rec[key]
        if named:
            current = named[0]
        section = current
        sec_part = section.split(".")[0] if section else None
        rec.update({
            "ordinal": ordinal,
            "detector": detector,
            "names_section": bool(named),
            "section": section,
            "attributed": section is not None,
            "unattributable": section is None,
            "regtext_part": part,
            "part_mismatch": bool(section and part and sec_part != str(part)),
            # section 8's numerator: attributed AND parsed.
            "complete": section is not None and rec["parsed"],
        })
        out.append(rec)
    return out


def completeness(records) -> dict:
    """CONTEXT.md section 8's definition, and the two halves of it reported apart so a
    reader can see WHERE the loss is. Every branch prints, zero included (hard rule 14),
    and the parts are asserted to sum to the whole."""
    total = len(records)
    attributed = sum(1 for r in records if r["attributed"])
    unattributable = sum(1 for r in records if r["unattributable"])
    parsed = sum(1 for r in records if r["parsed"])
    complete = sum(1 for r in records if r["complete"])
    if attributed + unattributable != total:
        raise AttributorError(
            f"attributed {attributed} + unattributable {unattributable} != {total}")
    if complete > attributed or complete > parsed:
        raise AttributorError("complete exceeds attributed or parsed")
    return {
        "total": total,
        "attributed": attributed,
        "unattributable": unattributable,
        "parsed": parsed,
        "complete": complete,
        "incomplete": total - complete,
        "completeness": (complete / total) if total else 0.0,
        "attribution_rate": (attributed / total) if total else 0.0,
        "parse_rate": (parsed / total) if total else 0.0,
        "part_mismatch": sum(1 for r in records if r["part_mismatch"]),
        "unclosed_quote": sum(1 for r in records if r["unclosed_quote"]),
        "by_operation": {
            op: sum(1 for r in records if r["operation"] == op) for op in OPERATIONS
        } | {"none": sum(1 for r in records if r["operation"] is None)},
    }


# ============================================================ pure: citations

CIT_RE = re.compile(r"(\d{1,3})\s*FR\s*(\d{1,6})")


def citation_date(text: str, citation: str) -> str | None:
    """The publication date anchored to THIS citation, not merely the first date in the
    note. Returns YYYY-MM-DD, or None when the note carries no readable date."""
    m = re.search(
        re.escape(citation) + r"\s*,?\s*([A-Z][a-z]{2,8})\.?\s*(\d{1,2})\s*,\s*(\d{4})",
        text)
    if not m or m.group(1) not in MONTHS:
        return None
    return "%04d-%02d-%02d" % (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def parse_citation(citation: str) -> tuple[int, int] | None:
    m = CIT_RE.fullmatch(citation.strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def pool_citations(pool_path: Path) -> list[dict]:
    """The 85 section-level defect notes with a resolvable FR citation, from CH-01's
    frozen `defect_notes.jsonl`. Read-only: CH-02 extends `data/`, it does not rewrite
    what CH-01 froze."""
    rows = [json.loads(l) for l in pool_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for r in rows:
        if not (r.get("section_level") and r.get("fr_citation")):
            continue
        cit = r["fr_citation"]
        vp = parse_citation(cit)
        out.append({
            "citation": cit,
            "volume": vp[0] if vp else None,
            "page": vp[1] if vp else None,
            "date": citation_date(r["text"], cit),
            "title": r["title"],
            "section": r["section"],
            "node": r["node"],
        })
    return out


# ============================================================ I/O: the FR issue

def _int_or_none(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def contents_index(root: ET.Element) -> dict[str, tuple[int, int]]:
    """{FR doc number -> (first page, last page)} from the front-matter <CNTNTS>.

    This is the PUBLISHED page range and the primary resolution route. A joint rule is
    listed under each issuing agency, so the same doc number appears more than once
    with the same range; the widest range wins, which is a no-op when they agree.
    """
    out: dict[str, tuple[int, int]] = {}
    for cnt in root.iter("CNTNTS"):
        for ent in cnt.iter():
            pgs = ent.find("PGS")
            doc = ent.find("FRDOCBP")
            if pgs is None or doc is None or not (pgs.text and doc.text):
                continue
            nums = [_int_or_none(x) for x in re.split(r"[-–]", pgs.text.strip())]
            nums = [n for n in nums if n is not None]
            if not nums:
                continue
            lo, hi = min(nums), max(nums)
            key = doc.text.strip()
            if key in out:
                lo, hi = min(lo, out[key][0]), max(hi, out[key][1])
            out[key] = (lo, hi)
    return out


FRDOC_NUM = re.compile(r"FR Doc\.?\s*(\S+?)\s+Filed", re.I)


def iter_rule_documents(path: Path):
    """Yield one dict per <RULE> in a daily issue, in document order.

    Page attribution follows the goldens' section 0: <PRTPAGE P="n"/> marks the point
    at which page n BEGINS, so a rule's pages are every numeric PRTPAGE inside it plus
    the page in effect when the <RULE> element opened. The second rule of an issue
    usually carries no PRTPAGE before its subject line - it starts on the page the
    previous rule ended on - and a resolver that ignored the carried-in page would miss
    every citation to a rule's first page.

    <PRORULE> is deliberately not walked: a proposed amendment never executed.
    """
    current_page = None
    stack = []            # open <RULE> frames
    regtext = []          # open <REGTEXT> attrs

    for event, el in ET.iterparse(str(path), events=("start", "end")):
        tag = el.tag
        if event == "start":
            if tag == "PRTPAGE":
                p = _int_or_none(el.get("P"))
                if p is not None:
                    current_page = p
                for fr in stack:
                    if p is not None:
                        fr["pages"].add(p)
            elif tag == "RULE":
                stack.append({
                    "start_page": current_page,
                    "pages": {current_page} if current_page is not None else set(),
                    "amdpars": [],
                    "parts": [],
                    "titles": [],
                    "frdoc": None,
                    "subject": None,
                })
            elif tag == "REGTEXT":
                regtext.append((el.get("TITLE"), el.get("PART")))
        else:
            if tag == "AMDPAR" and stack:
                t, p = regtext[-1] if regtext else (None, None)
                stack[-1]["amdpars"].append(element_text(el))
                stack[-1]["titles"].append(t)
                stack[-1]["parts"].append(p)
                el.clear()
            elif tag == "REGTEXT":
                if regtext:
                    regtext.pop()
            elif tag == "SUBJECT" and stack and stack[-1]["subject"] is None:
                stack[-1]["subject"] = collapse_ws("".join(el.itertext()))
            elif tag == "FRDOC" and stack:
                m = FRDOC_NUM.search("".join(el.itertext()))
                if m:
                    stack[-1]["frdoc"] = m.group(1).rstrip(".,;")
            elif tag == "RULE" and stack:
                fr = stack.pop()
                fr["pages"] = sorted(fr["pages"])
                yield fr


def load_issue(path: Path) -> dict:
    """One daily issue -> its volume, date, contents index and rule documents."""
    root = ET.parse(str(path)).getroot()
    vol = root.find("VOL")
    contents = contents_index(root)
    del root
    rules = list(iter_rule_documents(path))
    return {
        "file": path.name,
        "volume": _int_or_none(vol.text if vol is not None else None),
        "contents": contents,
        "rules": rules,
    }


def resolve_page(issue: dict, page: int) -> tuple[dict | None, str]:
    """PAGE-ONLY resolution, contents route first. Kept because it is the rule the
    goldens' section 0 pre-registered, and because `ch02_probe_resolution.py` needs it
    to show the state this chunk's resolution defect was found in. `resolve_citation`
    is what the extract actually uses; see its docstring for why.

    Two independent routes, and disagreement is reported rather than averaged:
      "contents"  - the published <PGS> range for the rule's FR doc number
      "prtpage"   - the carry-forward page set derived from <PRTPAGE>
    """
    by_contents = None
    for rule in issue["rules"]:
        rng = issue["contents"].get(rule["frdoc"] or "")
        if rng and rng[0] <= page <= rng[1]:
            by_contents = rule
            break
    by_prtpage = None
    for rule in issue["rules"]:
        pgs = rule["pages"]
        if pgs and pgs[0] <= page <= pgs[-1]:
            by_prtpage = rule
            break
    if by_contents is not None and by_prtpage is not None:
        same = by_contents["frdoc"] == by_prtpage["frdoc"]
        return by_contents, "both-agree" if same else "both-disagree"
    if by_contents is not None:
        return by_contents, "contents-only"
    if by_prtpage is not None:
        return by_prtpage, "prtpage-only"
    return None, "unresolved"


def sections_amended(rule: dict, detector: str = "extended") -> set:
    """The set of sections a rule's AMDPARs attribute to. Pure."""
    return {r["section"] for r in attribute(rule["amdpars"], detector, rule["parts"])
            if r["section"]}


def resolve_citation(issue: dict, page: int, section: str | None = None):
    """Resolve one citation inside one issue. Returns (rule, route).

    `resolve_page` above takes the contents route first, and MEASURED ON THIS CORPUS
    that is wrong twice out of 83. Both failures are the same upstream shape: the
    front-matter contents lists a *circular* as one entry spanning the page range of
    every rule inside it, so the summary document - which amends nothing - is listed
    over the top of the rule that does the amending.

      79 FR 24198   contents -> 2014-08743  "Federal Acquisition Circular 2005-73",
                                            pages 24191-24192, **0 AMDPARs**
                    correct  -> 2014-08744  "FAR; Positive Law Codification",
                                            pages 24192-24253, 838 AMDPARs
      90 FR 52865   contents -> 2025-20827  pages 52858-52860, 2 AMDPARs
                    correct  -> the rule whose AMDPARs actually reach 30 CFR 887.11

    A citation carries three keys - volume, page and **section** - and page alone does
    not separate two documents that share a page. So: gather every candidate either
    route admits, and prefer the one whose AMDPARs actually attribute to the cited
    section. That is a third exact key, not a heuristic; where it does not separate the
    candidates the PRTPAGE route wins, because it is derived per <RULE> element rather
    than from an editorial index. Every citation records which route decided it.
    """
    cands = []
    for rule in issue["rules"]:
        pgs = rule["pages"]
        in_prt = bool(pgs) and pgs[0] <= page <= pgs[-1]
        rng = issue["contents"].get(rule["frdoc"] or "")
        in_cnt = bool(rng) and rng[0] <= page <= rng[1]
        if (in_prt or in_cnt) and rule["frdoc"]:
            cands.append((rule, in_prt, in_cnt))
    if not cands:
        return None, "unresolved"
    if section:
        amending = [c for c in cands if section in sections_amended(c[0])]
        if amending:
            amending.sort(key=lambda c: (not c[1], not c[2]))
            return amending[0][0], ("section-match-sole" if len(cands) == 1
                                    else "section-match-disambiguated")
    cands.sort(key=lambda c: (not c[1], not c[2]))
    if len(cands) == 1:
        return cands[0][0], "page-unique"
    return cands[0][0], "prtpage-preferred"


def neighbour_dates(date: str) -> list[str]:
    """The issue dates either side of `date`, nearest first.

    An editorial note's date is not always the publication date. Measured: 85 FR 43138
    is noted "July 15, 2020" and published 2020-07-16 (the rule is stamped *Filed
    7-15-20*); 87 FR 31688 is noted "May 25, 2022" and published 2022-05-24. The drift
    runs in BOTH directions, so both neighbours are tried, and a neighbour is only
    accepted when the cited section also matches - volume, page and section all three.
    """
    from datetime import date as _d, timedelta
    y, m, dd = (int(x) for x in date.split("-"))
    base = _d(y, m, dd)
    return [(base + timedelta(days=1)).isoformat(), (base - timedelta(days=1)).isoformat()]


# ============================================================ I/O: fetch, hash, write

def issue_url(date: str) -> str:
    y, m, _ = date.split("-")
    return BULKDATA_FR.format(y=y, m=m, date=date)


def fetch_issues(dest: Path, dates, workers: int = 3) -> list[dict]:
    """Download the daily issues the pool cites. Network lives here and nowhere in the
    pure path (hard rule 8). Already-present files are not re-fetched."""
    from concurrent.futures import ThreadPoolExecutor
    import time

    dest.mkdir(parents=True, exist_ok=True)

    def one(date):
        url = issue_url(date)
        path = dest / f"FR-{date}.xml"
        if path.exists() and path.stat().st_size > 1024:
            return {"date": date, "url": url, "bytes": path.stat().st_size,
                    "status": "cached"}
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=300) as resp, open(path, "wb") as fh:
                    while True:
                        block = resp.read(1 << 20)
                        if not block:
                            break
                        fh.write(block)
                n = path.stat().st_size
                if n < 1024:
                    raise AttributorError(f"{path.name}: {n} B is too small to be an issue")
                return {"date": date, "url": url, "bytes": n, "status": "ok"}
            except Exception as exc:                      # pragma: no cover - network
                if attempt == 3:
                    if path.exists():
                        path.unlink()
                    return {"date": date, "url": url, "bytes": 0,
                            "status": f"FAILED: {exc}"}
                time.sleep(3 * (attempt + 1))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return sorted(ex.map(one, sorted(dates)), key=lambda r: r["date"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n")


# ============================================================ pure: the pair yield

def pair_yield(documents, defect_sections, tolerance: int = 0) -> dict:
    """The measurement `prompts/CH-02.md` section 5 calls the largest unknown.

    A PAIR is one defect section plus a count-matched sibling: another section amended
    by the SAME FR document, with the SAME number of amendatory instructions, carrying
    no defect note.

    `tolerance` is the permitted difference in instruction count. **0 is the rule this
    project adopts** and the only one the eval set may be built on; a non-zero value is
    a diagnostic reported beside it, never a fallback. `CONTEXT.md` section 8 is
    explicit: unmatched, a hardcoded threshold on instruction count beats the agent, and
    that is how a predecessor candidate died.

    `documents` maps frdoc -> {section -> instruction count}.
    `defect_sections` is a list of (frdoc, section).
    """
    if tolerance < 0:
        raise AttributorError("tolerance must be >= 0")
    defect_by_doc: dict[str, set] = {}
    for frdoc, section in defect_sections:
        defect_by_doc.setdefault(frdoc, set()).add(section)

    rows, matched = [], 0
    for frdoc, section in defect_sections:
        counts = documents.get(frdoc, {})
        own = counts.get(section)
        siblings = {
            s: c for s, c in counts.items()
            if s != section and s not in defect_by_doc.get(frdoc, set())
        }
        if own is None:
            cands = []
        else:
            cands = sorted(s for s, c in siblings.items() if abs(c - own) <= tolerance)
        if cands:
            matched += 1
        rows.append({
            "frdoc": frdoc,
            "section": section,
            "instruction_count": own,
            "sections_amended_by_document": len(counts),
            "sibling_sections": len(siblings),
            "count_matched_siblings": len(cands),
            "matched_examples": cands[:5],
            "has_match": bool(cands),
        })
    n = len(defect_sections)
    if matched + sum(1 for r in rows if not r["has_match"]) != n:
        raise AttributorError("matched + unmatched != n")
    return {
        "tolerance": tolerance,
        "n_defect_sections": n,
        "with_match": matched,
        "without_match": n - matched,
        "yield": (matched / n) if n else 0.0,
        "projected_pairs": round(n * (matched / n)) if n else 0,
        "rows": rows,
    }


# ============================================================ CLI

def cmd_fetch(args) -> int:
    pool = pool_citations(Path(args.pool))
    dates = sorted({c["date"] for c in pool if c["date"]})
    print(f"pool citations={len(pool)}  distinct issue dates={len(dates)}")
    res = fetch_issues(Path(args.raw), dates)
    for r in res:
        print(f"  {r['date']}  {r['bytes']:>12,} B  {r['status']}")
    failed = [r for r in res if str(r["status"]).startswith("FAILED")]
    print(f"  issues ok={len(res) - len(failed)}/{len(res)} "
          f"bytes={sum(r['bytes'] for r in res):,}")
    return 1 if failed else 0


def cmd_extract(args) -> int:
    raw, out = Path(args.raw), Path(args.out)
    pool = pool_citations(Path(args.pool))

    # ---- resolve every citation to an FR document ------------------------------
    by_date: dict[str, list[dict]] = {}
    ladder = {"pool_citations": len(pool), "no_date": 0, "no_issue_file": 0,
              "volume_mismatch": 0, "unresolved_page": 0, "resolved": 0}
    for c in pool:
        if not c["date"]:
            ladder["no_date"] += 1
            c["status"] = "no-date"
            continue
        by_date.setdefault(c["date"], []).append(c)

    documents: dict[str, dict] = {}
    issue_cache: dict[str, dict | None] = {}
    wanted: set[str] = set()

    def issue_for(date: str):
        if date not in issue_cache:
            p = raw / f"FR-{date}.xml"
            issue_cache[date] = load_issue(p) if p.exists() else None
        return issue_cache[date]

    for noted_date in sorted(by_date):
        for c in by_date[noted_date]:
            rule, route, used_date = None, "unresolved", noted_date
            issue = issue_for(noted_date)
            if issue is None:
                ladder["no_issue_file"] += 1
                c["status"] = "no-issue-file"
                c["resolution_route"] = "no-issue-file"
                continue
            if c["volume"] is not None and issue["volume"] != c["volume"]:
                ladder["volume_mismatch"] += 1
                c["status"] = "volume-mismatch"
                c["resolution_route"] = "volume-mismatch"
                continue
            rule, route = resolve_citation(issue, c["page"], c["section"])
            if rule is None:
                # The note's date can be off by one from the publication date; try the
                # neighbours, but ONLY accept one that also matches the cited section.
                # BOTH neighbours are always evaluated, never short-circuited on the
                # first hit: a search that stops early makes the answer depend on which
                # files happen to be on disk, and hard rule 9 requires the same inputs
                # to give the same output. A neighbour that is missing is recorded as
                # missing rather than silently treated as a non-match.
                hits, missing = [], []
                for nd in neighbour_dates(noted_date):
                    nb = issue_for(nd)
                    if nb is None:
                        wanted.add(nd)
                        missing.append(nd)
                        continue
                    if c["volume"] is not None and nb["volume"] != c["volume"]:
                        continue
                    cand, croute = resolve_citation(nb, c["page"], c["section"])
                    if cand is not None and croute.startswith("section-match"):
                        hits.append((nd, cand))
                c["neighbour_issues_missing"] = missing
                if len(hits) == 1:
                    used_date, rule = hits[0][0], hits[0][1]
                    route = f"neighbour-day:{used_date}"
                elif len(hits) > 1:
                    route = "neighbour-ambiguous"      # reported, never guessed at
                    rule = None
            c["resolution_route"] = route
            c["issue_date_used"] = used_date
            if rule is None or not rule["frdoc"]:
                ladder["unresolved_page"] += 1
                c["status"] = "unresolved-page"
                continue
            ladder["resolved"] += 1
            c["status"] = "resolved"
            c["frdoc"] = rule["frdoc"]
            used_issue = issue_for(used_date)
            documents.setdefault(rule["frdoc"], {
                "frdoc": rule["frdoc"],
                "issue_date": used_date,
                "issue_file": f"FR-{used_date}.xml",
                "volume": used_issue["volume"],
                "pages": rule["pages"],
                "contents_pages": list(used_issue["contents"].get(rule["frdoc"], ())),
                "subject": rule["subject"],
                "amdpars": rule["amdpars"],
                "parts": rule["parts"],
                "titles": rule["titles"],
            })

    total_rungs = (ladder["no_date"] + ladder["no_issue_file"]
                   + ladder["volume_mismatch"] + ladder["unresolved_page"]
                   + ladder["resolved"])
    if total_rungs != ladder["pool_citations"]:
        raise AttributorError(
            f"exclusion ladder does not close: {total_rungs} != {ladder['pool_citations']}")

    # ---- attribute, under BOTH detectors ---------------------------------------
    records, per_doc = [], {}
    for frdoc in sorted(documents):
        d = documents[frdoc]
        rows = {}
        for det in ("spec_literal", "extended"):
            rows[det] = attribute(d["amdpars"], det, d["parts"])
            per_doc.setdefault(frdoc, {})[det] = completeness(rows[det])
        for i, (lit, ext) in enumerate(zip(rows["spec_literal"], rows["extended"])):
            merged = {k: v for k, v in ext.items() if k not in (
                "detector", "section", "attributed", "unattributable", "complete",
                "names_section", "part_mismatch")}
            merged.update({
                "frdoc": frdoc,
                "issue_date": d["issue_date"],
                "regtext_title": d["titles"][i],
                "section_spec_literal": lit["section"],
                "section_extended": ext["section"],
                "names_section_spec_literal": lit["names_section"],
                "names_section_extended": ext["names_section"],
                "complete_spec_literal": lit["complete"],
                "complete_extended": ext["complete"],
                "attributed_spec_literal": lit["attributed"],
                "attributed_extended": ext["attributed"],
                "part_mismatch_extended": ext["part_mismatch"],
                "detector_disagrees": lit["section"] != ext["section"],
            })
            records.append(merged)

    glob = {}
    for det in ("spec_literal", "extended"):
        flat = [{**r,
                 "attributed": r[f"attributed_{det}"],
                 "unattributable": not r[f"attributed_{det}"],
                 "complete": r[f"complete_{det}"],
                 "part_mismatch": r["part_mismatch_extended"]} for r in records]
        glob[det] = completeness(flat)

    # ---- the pair yield ---------------------------------------------------------
    doc_counts = {}
    for frdoc in sorted(documents):
        counts: dict[str, int] = {}
        for r in records:
            if r["frdoc"] != frdoc:
                continue
            sec = r["section_extended"]
            if sec:
                counts[sec] = counts.get(sec, 0) + 1
        doc_counts[frdoc] = counts
    defect_sections = sorted({(c["frdoc"], c["section"]) for c in pool
                              if c.get("status") == "resolved"})
    yields = {str(t): pair_yield(doc_counts, defect_sections, t) for t in (0, 1)}

    # ---- freeze -----------------------------------------------------------------
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "amdpars.jsonl", records)
    write_json(out / "documents.json", {
        frdoc: {k: v for k, v in d.items() if k not in ("amdpars", "parts", "titles")}
        | {"amdpar_count": len(d["amdpars"]),
           "sections_amended": sorted(doc_counts.get(frdoc, {})),
           "instruction_counts": doc_counts.get(frdoc, {})}
        for frdoc, d in sorted(documents.items())})
    write_json(out / "completeness.json",
               {"global": glob, "per_document": per_doc, "exclusion_ladder": ladder})
    write_json(out / "pair_yield.json", yields)
    write_json(out / "citations.json", {c["citation"] + "|" + c["node"]: c for c in pool})
    write_json(out / "wanted_issues.json", {
        "why": "neighbour-day issues a citation needed but that were not on disk; "
               "refetch.py fetches these and re-runs extract",
        "dates": sorted(wanted)})

    manifest = {
        "chunk": "CH-02",
        "what": "AMDPAR instructions attributed to sections by carry-forward",
        "normalisation": NORMALISATION,
        "files": {},
        "raw_inputs": {},
    }
    for name in sorted(p.name for p in out.iterdir() if p.name != "manifest.json"):
        p = out / name
        manifest["files"][name] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    for date in sorted(d for d, v in issue_cache.items() if v is not None):
        p = raw / f"FR-{date}.xml"
        if p.exists():
            manifest["raw_inputs"][p.name] = {
                "sha256": sha256_file(p), "bytes": p.stat().st_size,
                "url": issue_url(date)}
    write_json(out / "manifest.json", manifest)

    # ---- report ------------------------------------------------------------------
    print("=" * 72)
    print("EXCLUSION LADDER - citation to FR document")
    print("=" * 72)
    for k, v in ladder.items():
        print(f"  {k:<20} {v:>6}")
    print(f"  distinct FR documents retrieved: {len(documents)}")
    routes: dict[str, int] = {}
    for c in pool:
        routes[c.get("resolution_route", "-")] = routes.get(c.get("resolution_route", "-"), 0) + 1
    print("  resolution route:")
    for k in sorted(routes):
        print(f"    {k:<32} {routes[k]:>4}")
    if wanted:
        print(f"  neighbour-day issues NOT on disk: {sorted(wanted)}")
    print()
    print("=" * 72)
    print("COMPLETENESS - CONTEXT.md section 8's definition")
    print("=" * 72)
    for det in ("spec_literal", "extended"):
        g = glob[det]
        print(f"  {det:<13} completeness={g['completeness']:.4f}  "
              f"({g['complete']}/{g['total']})  attribution={g['attribution_rate']:.4f}  "
              f"parse={g['parse_rate']:.4f}  unattributable={g['unattributable']}")
    print()
    print("=" * 72)
    print("PAIR YIELD")
    print("=" * 72)
    for t in ("0", "1"):
        y = yields[t]
        label = "EXACT (adopted)" if t == "0" else "+/-1 (NOT ADOPTED - diagnostic)"
        print(f"  {label:<32} yield={y['yield']:.4f}  "
              f"{y['with_match']}/{y['n_defect_sections']}  "
              f"projected pairs={y['projected_pairs']}")
    return 0


def cmd_verify(args) -> int:
    out = Path(args.out)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    ok, bad = 0, []
    for name, want in sorted(manifest["files"].items()):
        p = out / name
        if not p.exists():
            bad.append(f"MISSING  {name}")
            continue
        got = sha256_file(p)
        if got == want["sha256"]:
            ok += 1
            print(f"  OK    {name:<22} {got}")
        else:
            bad.append(f"MISMATCH {name}\n    manifest {want['sha256']}\n    on disk  {got}")
            print(f"  FAIL  {name:<22} {got}")
    print(f"  {ok}/{len(manifest['files'])} verify")
    for b in bad:
        print(f"  - {b}")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="download the FR daily issues the pool cites")
    f.add_argument("--raw", default=str(DEFAULT_RAW_DIR))
    f.add_argument("--pool", default=str(DEFAULT_POOL))
    f.set_defaults(func=cmd_fetch)

    e = sub.add_parser("extract", help="attribute AMDPARs and freeze data/amdpars/")
    e.add_argument("--raw", default=str(DEFAULT_RAW_DIR))
    e.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    e.add_argument("--pool", default=str(DEFAULT_POOL))
    e.set_defaults(func=cmd_extract)

    v = sub.add_parser("verify", help="check the freeze against its manifest; no network")
    v.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    v.set_defaults(func=cmd_verify)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
