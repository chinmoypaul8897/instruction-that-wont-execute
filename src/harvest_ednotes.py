"""CH-01 - govinfo ECFR <EDNOTE> harvest.

This chunk answers one question: **how many usable codification-defect cases actually
exist?** Everything downstream - the eval set, the pool gate, the headline - is
downstream of that integer.

WHAT AN EDNOTE IS. The Office of the Federal Register annotates the eCFR wherever an
amendatory instruction in a final rule could not be carried out against the codified
text: the paragraph named does not exist, the quoted words are not there, the section
is stayed. The OFR records the failure in an editorial note and leaves the CFR text
unchanged. Those notes are the gold labels of this project - a published,
human-adjudicated record of an instruction that would not execute.

    <EDNOTE>
    <HED>Editorial Note:</HED><PSPACE>At 83 FR 61311, Nov. 29, 2018, s 2.22 was
    amended by adding (a)(1)(xvi), however paragraph (a)(xvi) was not provided in the
    text, this amendment could not be incorporated due to inaccurate amendatory
    instruction.</PSPACE></EDNOTE>

SOURCE. `https://www.govinfo.gov/bulkdata/ECFR/title-N/ECFR-titleN.xml`, one XML per
title, 49 titles (title 35 is reserved and has no folder). www.ecfr.gov and
www.federalregister.gov return HTTP 403 from this machine and are not used - see
CLAUDE.md's operational constraint. govinfo needs no key.

FORMAT NOTE, and it matters. The spec asks whether a note sits "inside a <SECTION>
block". **ECFR bulk XML has no <SECTION> element** - that is the CFR annual-edition
spelling. Here the containers are numbered DIVs carrying a TYPE attribute, and the
section container is <DIV8 TYPE="SECTION">. See QUESTIONS.md Q8; pinned by golden G2.

PURITY (hard rule 8) and DETERMINISM (hard rule 9). Everything above the NETWORK
banner is pure: bytes in, records out. No clock, no randomness, no network. Records
come out in document order, JSON is written with sorted keys and LF endings, so the
same input yields byte-identical output and the manifest verifies from a clean clone.
The only impure code is under the banner, and it is the only code refetch.py needs a
network for.

    python src/harvest_ednotes.py fetch                  # -> data/raw/ecfr/ (ignored)
    python src/harvest_ednotes.py extract                # -> data/ednotes/
    python src/harvest_ednotes.py verify                 # manifest check, no network
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# --------------------------------------------------------------------------- spec

#: The literal that marks a codification-defect note. `prompts/CH-01.md` step 3 and
#: `CONTEXT.md` section 8 both name this exact string. It is matched case-sensitively
#: on the note body at the declared normalisation level; the case-insensitive count is
#: reported alongside so a hidden variant cannot pass as a zero (hard rule 14).
DEFECT_LITERAL = "could not be incorporated"

#: Structural containers of the ECFR bulk DTD, nearest-enclosing wins. Anything not in
#: this set (e.g. TYPE="CENTER", a layout div) is transparent for ancestry purposes and
#: is counted separately so an unknown container is a visible finding, not a silent drop.
STRUCTURAL_TYPES = (
    "TITLE", "SUBTITLE", "CHAPTER", "SUBCHAP", "PART",
    "SUBPART", "SUBJGRP", "SECTION", "APPENDIX",
)

#: The one that decides the pool gate. `section_level` is exactly `container_type ==
#: SECTION`; an APPENDIX or PART note is real but not section-level.
SECTION_TYPE = "SECTION"

#: `\b(\d+)\s+FR\s+(\d+)\b`. All matches kept in document order; the FIRST is the rule
#: the note is about. Golden G4 is the two-citation case that makes the rule load-bearing.
FR_CITE_RE = re.compile(r"\b(\d+)\s+FR\s+(\d+)\b")

#: A section citation inside the note's own prose, e.g. `s 383.212`. NOT used by the
#: pool gate - the gate uses the container reading the prompt asks for, "section-level
#: (not appendix/part)". This is the SECOND reading, reported as a diagnostic because
#: it is what reconciles our 36 against `CONTEXT.md` section 8's 38 on the nine
#: reference titles. Reporting both is the point; picking the larger one would be
#: exactly the tuning hard rule 5 forbids.
SECTION_NAME_RE = re.compile(r"§+\s*\d+[\w.]*\.\d")

_DIV_TAG_RE = re.compile(r"^DIV\d*$")
_WS_RE = re.compile(r"\s+")
_SECTION_PREFIX_RE = re.compile(r"^[§\s]+")   # leading section sign(s) and space

#: Declared normalisation level, hard rule 7. Reported in every record, never applied
#: silently. `exact` would preserve govinfo's intra-element newlines, which are an
#: artefact of its line wrapping and carry no meaning; `alphanumeric-only` would destroy
#: the paragraph designations this project is precision-critical about.
NORMALISATION = "whitespace-collapsed"

BULKDATA_JSON = "https://www.govinfo.gov/bulkdata/json/ECFR"
BULKDATA_XML = "https://www.govinfo.gov/bulkdata/ECFR/title-{t}/ECFR-title{t}.xml"
USER_AGENT = "micro1-frontier-challenge CH-01 EDNOTE harvest"

DEFAULT_RAW_DIR = Path("data/raw/ecfr")
DEFAULT_OUT_DIR = Path("data/ednotes")

#: Every key a record carries. Asserted on construction rather than left as prose: a
#: field added in one branch and forgotten in another is how a downstream KeyError
#: becomes a silent `.get()` default three chunks later.
RECORD_FIELDS = (
    "container_n", "container_type", "fr_citation", "fr_citations", "hed", "is_defect",
    "names_section", "node", "normalisation", "ordinal", "part", "section",
    "section_level", "section_raw", "source_file", "text", "title", "title_sources",
)


class HarvestError(Exception):
    """Anything that should stop the harvest rather than be silently absorbed."""


# ====================================================================== PURE CORE
# Bytes in, records out. No network, no clock, no randomness below this line and
# above the NETWORK banner.

def collapse_ws(s: str) -> str:
    """Normalisation level `whitespace-collapsed`: runs of whitespace -> one space."""
    return _WS_RE.sub(" ", s).strip()


def note_texts(ednote: ET.Element) -> tuple[str, str]:
    """Split an <EDNOTE> into its (hed, body) at the declared normalisation level.

    Two fields rather than one because `</HED>` abuts `<PSPACE>` with no separating
    character, so concatenating the whole element yields `Editorial Note:At 83 FR ...`
    - a missing space no reader would predict, and one that would then have to be
    hand-waved away in every downstream string comparison.

    `hed` is the <HED> child's own text. `body` is every other descendant text node in
    document order, which is what the defect filter reads. Inline elements such as
    `<E T="04">Federal Register</E>` are traversed, so `For <E>Federal Register</E>
    citations` yields `For Federal Register citations` and not `ForFederal Register`.
    """
    hed_parts: list[str] = []
    body_parts: list[str] = []

    def walk(el: ET.Element, in_hed: bool) -> None:
        sink = hed_parts if in_hed else body_parts
        if el.text:
            sink.append(el.text)
        for child in el:
            child_in_hed = in_hed or child.tag == "HED"
            walk(child, child_in_hed)
            if child.tail:
                # A tail belongs to the child's PARENT context, never to the child.
                # Getting this wrong pulls `<HED>`'s trailing whitespace into `hed`
                # and drops it from the body.
                (hed_parts if in_hed else body_parts).append(child.tail)

    walk(ednote, in_hed=(ednote.tag == "HED"))
    return collapse_ws("".join(hed_parts)), collapse_ws("".join(body_parts))


def find_fr_citations(text: str) -> list[str]:
    """Every `NN FR NNNNN` in document order, normalised to a single space."""
    return [f"{vol} FR {page}" for vol, page in FR_CITE_RE.findall(text)]


def is_defect(text: str) -> bool:
    """True iff the note body carries the codification-defect literal."""
    return DEFECT_LITERAL in text


def normalise_section(section_raw: str | None) -> str | None:
    """`'§ 2.22'` -> `'2.22'`. Empty or absent -> None (golden G2's appendix)."""
    if section_raw is None:
        return None
    stripped = collapse_ws(_SECTION_PREFIX_RE.sub("", section_raw))
    return stripped or None


def _title_from_node(node: str | None) -> str | None:
    """`'7:1.1.1.1.5.3.29.9'` -> `'7'`. The most local statement of the title."""
    if not node or ":" not in node:
        return None
    head = node.split(":", 1)[0].strip()
    return head or None


def iter_ednotes(source, source_name: str = "", title_hint: str | None = None):
    """Yield one dict per <EDNOTE> in document order.

    `source` is a path or a binary file object. Streamed with iterparse and pruned as
    it goes: title 40 is 161 MB and building its whole tree is not necessary to read
    2,000 notes out of it.

    Ancestry is the nearest enclosing structural DIV, tracked on an explicit stack.
    `title` is taken from that container's NODE prefix (the most local statement),
    falling back to the enclosing TYPE="TITLE" DIV's N, then to `title_hint` from the
    filename. Disagreements are surfaced in the record's `title_sources` rather than
    resolved silently.
    """
    stack: list[dict] = []          # structural DIV ancestry
    elems: list[ET.Element] = []    # element ancestry, for pruning
    ednote_depth = 0
    ordinal = 0
    doc_title: str | None = None

    for event, el in ET.iterparse(source, events=("start", "end")):
        if event == "start":
            if el.tag == "EDNOTE":
                ednote_depth += 1
            elif _DIV_TAG_RE.match(el.tag):
                div_type = (el.get("TYPE") or "").strip().upper()
                if div_type in STRUCTURAL_TYPES:
                    frame = {
                        "tag": el.tag,
                        "type": div_type,
                        "n": el.get("N"),
                        "node": el.get("NODE"),
                        "depth": len(elems),
                    }
                    stack.append(frame)
                    if div_type == "TITLE" and doc_title is None:
                        # NOT el.get("N"). On a TYPE="TITLE" div, N is the printed
                        # VOLUME index - `<DIV1 N="1" NODE="11:1" TYPE="TITLE">` is
                        # volume 1 of title 11 - so reading N here labels every title
                        # in the corpus "1". The title number is the NODE prefix.
                        doc_title = _title_from_node(el.get("NODE"))
            elems.append(el)
            continue

        # ---- end event
        elems.pop()
        if el.tag == "EDNOTE":
            ordinal += 1
            yield _build_record(el, stack, ordinal, source_name, doc_title, title_hint)
            ednote_depth -= 1
        elif _DIV_TAG_RE.match(el.tag):
            if stack and stack[-1]["depth"] == len(elems) and stack[-1]["tag"] == el.tag:
                stack.pop()

        if ednote_depth == 0:
            # Prune: drop the finished subtree from its parent so memory stays flat.
            el.clear()
            if elems:
                parent = elems[-1]
                try:
                    parent.remove(el)
                except ValueError:      # pragma: no cover - defensive
                    pass


def _build_record(ednote, stack, ordinal, source_name, doc_title, title_hint) -> dict:
    container = stack[-1] if stack else None
    container_type = container["type"] if container else None

    section_frame = next((f for f in reversed(stack) if f["type"] == SECTION_TYPE), None)
    part_frame = next((f for f in reversed(stack) if f["type"] == "PART"), None)

    node = container["node"] if container else None
    from_node = _title_from_node(node)
    title_sources = {"node": from_node, "div1_node": doc_title, "filename": title_hint}
    title = from_node or doc_title or title_hint

    section_raw = section_frame["n"] if section_frame else None
    hed, text = note_texts(ednote)
    cites = find_fr_citations(text)

    record = {
        "title": title,
        "part": (part_frame["n"] if part_frame else None),
        "section": normalise_section(section_raw),
        # `section_raw` is the enclosing SECTION container's N, and is None when there
        # is no SECTION ancestor at all. `container_n` is the NEAREST structural
        # container's N whatever its type - the empty string for golden G2's appendix,
        # whose identity lives in its <HEAD>. Both are carried because collapsing them
        # loses the distinction between "no section" and "a section with no number".
        "section_raw": section_raw,
        "container_n": (container["n"] if container else None),
        "node": node,
        "container_type": container_type,
        # Exactly the spec's question - "does it sit inside a section block" - asked
        # of this format's spelling of that block. QUESTIONS.md Q8.
        "section_level": container_type == SECTION_TYPE,
        # The second reading, carried but never substituted for the first.
        "names_section": bool(SECTION_NAME_RE.search(text)),
        "hed": hed,
        "text": text,
        "is_defect": is_defect(text),
        "fr_citation": (cites[0] if cites else None),
        "fr_citations": cites,
        "source_file": source_name,
        "ordinal": ordinal,
        "normalisation": NORMALISATION,
        "title_sources": title_sources,
    }
    if tuple(sorted(record)) != RECORD_FIELDS:
        raise HarvestError(
            f"record field set drifted: {sorted(set(record) ^ set(RECORD_FIELDS))}")
    return record


def tally(records: list[dict]) -> dict:
    """The exclusion ladder for one title, as counts. Every rung sums to its parent.

    Hard rule 14: zero-occurrence branches are emitted as explicit zeros, and each
    complementary pair is asserted to sum to n. A ladder whose rungs do not add up is
    a broken ladder, and that must fail here rather than read as a clean result.
    """
    n = len(records)
    defect = [r for r in records if r["is_defect"]]
    non_defect = [r for r in records if not r["is_defect"]]
    sect = [r for r in defect if r["section_level"]]
    non_sect = [r for r in defect if not r["section_level"]]
    with_fr = [r for r in defect if r["fr_citation"]]
    without_fr = [r for r in defect if not r["fr_citation"]]
    usable = [r for r in defect if r["section_level"] and r["fr_citation"]]

    # Hard rule 14's `success + failure == n`, raised rather than asserted: `python -O`
    # strips assert statements, and a load-bearing count that stops checking itself
    # under an optimisation flag is precisely the silent-green failure this project
    # exists to expose. tests/ and docs/evidence/ch01-pool/ch01_pool.py check it again
    # by independent routes.
    for label, lhs, rhs in (
        ("defect + non-defect", len(defect) + len(non_defect), n),
        ("section + non-section", len(sect) + len(non_sect), len(defect)),
        ("with-FR + without-FR", len(with_fr) + len(without_fr), len(defect)),
    ):
        if lhs != rhs:
            raise HarvestError(f"ladder does not sum: {label} = {lhs}, expected {rhs}")

    ci_only = sum(
        1 for r in non_defect if DEFECT_LITERAL.lower() in r["text"].lower()
    )
    hed_only = sum(
        1 for r in non_defect
        if DEFECT_LITERAL in r["hed"] and DEFECT_LITERAL not in r["text"]
    )
    return {
        "ednotes": n,
        "defect": len(defect),
        "non_defect": len(non_defect),
        "defect_pct_of_ednotes": (round(100.0 * len(defect) / n, 2) if n else 0.0),
        "defect_section_level": len(sect),
        "defect_not_section_level": len(non_sect),
        "defect_with_fr": len(with_fr),
        "defect_without_fr": len(without_fr),
        "defect_multi_fr": sum(1 for r in defect if len(r["fr_citations"]) > 1),
        "usable_section_and_fr": len(usable),
        # Reading B, reported not used: a note may name its section in prose while
        # sitting in an appendix or at part level. `CONTEXT.md` section 8's nine-title
        # figure of 38 is this reading; the container reading gives 36. Both ship.
        "defect_section_or_named": sum(
            1 for r in defect if r["section_level"] or r["names_section"]),
        "defect_named_not_contained": sum(
            1 for r in defect if not r["section_level"] and r["names_section"]),
        # Both are expected to be 0. They are printed anyway: a filter that would have
        # matched more under a looser reading is a finding, and an unprinted 0 is
        # indistinguishable from an unasked question.
        "case_insensitive_only_extra": ci_only,
        "literal_in_hed_only": hed_only,
        "container_types": _count_by(records, "container_type"),
        "defect_container_types": _count_by(defect, "container_type"),
    }


def _count_by(records: list[dict], key: str) -> dict:
    out: dict[str, int] = {}
    for r in records:
        out[str(r[key])] = out.get(str(r[key]), 0) + 1
    return dict(sorted(out.items()))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_jsonl(path: Path, records: list[dict]) -> None:
    """LF endings and sorted keys, explicitly - byte-identical output is hard rule 9."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, obj) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, sort_keys=True, indent=1)
        fh.write("\n")


# ======================================================================== NETWORK
# Everything below this banner touches the network. Nothing above it does.

def _get_json(url: str, timeout: int = 60):
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def list_titles() -> list[dict]:
    """Ask govinfo which ECFR titles exist and how big each XML is.

    Not hard-coded to `range(1, 51)`: title 35 is reserved and has no folder, and a
    hard-coded range would silently 404 on it. Measured 2026-08-30: 49 titles,
    824,289,052 B total - not the ~2.3 GB `CONTEXT.md` section 8 extrapolates, because
    that extrapolation was taken from the nine LARGEST titles.
    """
    top = _get_json(BULKDATA_JSON)
    titles = sorted({
        f["cfrTitle"] for f in top["files"]
        if f.get("folder") and str(f.get("name", "")).startswith("title-")
    })
    out = []
    for t in titles:
        d = _get_json(f"{BULKDATA_JSON}/title-{t}")
        for f in d["files"]:
            if f["name"].endswith(".xml"):
                out.append({
                    "title": str(t),
                    "name": f["name"],
                    "size": f["size"],
                    "link": f["link"],
                    "lastmod": f.get("formattedLastModifiedTime"),
                })
    return out


def fetch_titles(dest: Path, only: list[str] | None = None, workers: int = 3) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor

    dest.mkdir(parents=True, exist_ok=True)
    index = [r for r in list_titles() if not only or r["title"] in only]

    def one(r):
        path = dest / r["name"]
        if path.exists() and path.stat().st_size == r["size"]:
            return {**r, "status": "cached"}
        for attempt in range(4):
            try:
                req = urllib.request.Request(r["link"], headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=300) as resp, open(path, "wb") as fh:
                    while True:
                        block = resp.read(1 << 20)
                        if not block:
                            break
                        fh.write(block)
                got = path.stat().st_size
                if got != r["size"]:
                    raise HarvestError(f"{r['name']}: got {got} B, govinfo announced {r['size']} B")
                return {**r, "status": "ok"}
            except Exception as exc:                      # pragma: no cover - network
                if attempt == 3:
                    return {**r, "status": f"FAILED: {exc}"}
                import time
                time.sleep(3 * (attempt + 1))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(one, sorted(index, key=lambda r: -r["size"])))
    results = sorted(results, key=lambda r: int(r["title"]))

    # Record what govinfo announced, so the extract step can carry it into the freeze
    # without itself touching the network.
    write_json(dest / "_govinfo_index.json", {
        "source": BULKDATA_JSON,
        "titles": {r["title"]: {"name": r["name"], "bytes": r["size"],
                                "govinfo_last_modified": r["lastmod"], "url": r["link"]}
                   for r in results},
    })
    return results


# =========================================================================== CLI

def _title_of(path: Path) -> str:
    m = re.search(r"ECFR-title(\w+)\.xml$", path.name)
    return m.group(1) if m else path.stem


def cmd_extract(args) -> int:
    raw_dir, out_dir = Path(args.raw), Path(args.out)
    files = sorted(raw_dir.glob("ECFR-title*.xml"), key=lambda p: int(_title_of(p)))
    if not files:
        raise HarvestError(f"no ECFR title XML under {raw_dir} - run `fetch` first")
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    per_title: dict[str, dict] = {}
    for path in files:
        t = _title_of(path)
        recs = list(iter_ednotes(str(path), source_name=path.name, title_hint=t))
        per_title[t] = tally(recs)
        per_title[t]["raw_bytes"] = path.stat().st_size
        all_records.extend(recs)
        print(f"title-{t:<3} {path.stat().st_size:>12,} B  "
              f"EDNOTE {per_title[t]['ednotes']:>4}  "
              f"defect {per_title[t]['defect']:>3}  "
              f"sect {per_title[t]['defect_section_level']:>3}  "
              f"+FR {per_title[t]['defect_with_fr']:>3}")

    total = tally(all_records)
    total["titles"] = len(files)
    total["defect_notes_per_title"] = round(total["defect"] / len(files), 3)
    mismatches = [
        r for r in all_records
        if len({v for v in r["title_sources"].values() if v}) > 1
    ]
    total["title_source_disagreements"] = len(mismatches)

    defects = [r for r in all_records if r["is_defect"]]
    write_jsonl(out_dir / "ednotes.jsonl", all_records)
    write_jsonl(out_dir / "defect_notes.jsonl", defects)
    write_json(out_dir / "counts.json", {"total": total, "by_title": per_title})

    with open(out_dir / "counts_by_title.csv", "w", encoding="utf-8", newline="") as fh:
        cols = ["title", "raw_bytes", "ednotes", "defect", "non_defect",
                "defect_pct_of_ednotes", "defect_section_level",
                "defect_not_section_level", "defect_with_fr", "defect_without_fr",
                "usable_section_and_fr"]
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        for t in sorted(per_title, key=int):
            w.writerow([t] + [per_title[t][c] for c in cols[1:]])

    # Provenance of the raw inputs. Kept OUT of the hashed set on purpose: govinfo's
    # last-modified stamp moves whenever a title is re-published, even when the bytes
    # that matter are unchanged, and a manifest that fails for that reason would train
    # a reader to ignore it. Committed, dated, and read separately.
    index_path = raw_dir / "_govinfo_index.json"
    if index_path.exists():
        write_json(out_dir / "source_index.json",
                   json.loads(index_path.read_text(encoding="utf-8")))
    else:
        write_json(out_dir / "source_index.json", {
            "note": "no govinfo index present at extract time; run `fetch` to record "
                    "the announced sizes and last-modified stamps",
            "titles": {},
        })

    manifest = {
        "chunk": "CH-01",
        "source": "https://www.govinfo.gov/bulkdata/ECFR",
        "normalisation": NORMALISATION,
        "defect_literal": DEFECT_LITERAL,
        "titles": len(files),
        # sha256 of the raw XML each number came from. This is what turns "we measured
        # 44 defect notes" into "we measured 44 defect notes on THESE bytes".
        "raw_inputs": {
            p.name: {"bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in files
        },
        "unhashed_provenance": ["source_index.json"],
        "files": {},
    }
    for name in ("ednotes.jsonl", "defect_notes.jsonl", "counts.json", "counts_by_title.csv"):
        p = out_dir / name
        manifest["files"][name] = {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
    write_json(out_dir / "manifest.json", manifest)

    print()
    print(f"TOTAL  titles {total['titles']}  EDNOTE {total['ednotes']}  "
          f"defect {total['defect']} ({total['defect_pct_of_ednotes']}%)  "
          f"section-level {total['defect_section_level']}  "
          f"with FR {total['defect_with_fr']}  "
          f"usable {total['usable_section_and_fr']}")
    print(f"       defect notes per title: {total['defect_notes_per_title']}")
    print(f"       POOL GATE (>= 60 section-level with FR citation): "
          f"{total['usable_section_and_fr']} -> "
          f"{'CLEARS' if total['usable_section_and_fr'] >= 60 else 'BELOW - fallback triggers'}")
    return 0


def cmd_fetch(args) -> int:
    results = fetch_titles(Path(args.dest), only=(args.title or None))
    failed = [r for r in results if str(r["status"]).startswith("FAILED")]
    for r in results:
        print(f"title-{r['title']:<3} {r['name']:<24} {r['size']:>12,} B  {r['status']}")
    print(f"\nfiles={len(results)} ok={len(results) - len(failed)} failed={len(failed)} "
          f"bytes={sum(r['size'] for r in results):,}")
    return 1 if failed else 0


def cmd_verify(args) -> int:
    out_dir = Path(args.out)
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    bad = 0
    for name, want in sorted(manifest["files"].items()):
        got = sha256_file(out_dir / name)
        ok = got == want["sha256"]
        bad += (not ok)
        print(f"{'OK  ' if ok else 'FAIL'} {name:<24} {got}")
    print(f"\n{len(manifest['files']) - bad}/{len(manifest['files'])} files verify")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="download ECFR title XML from govinfo")
    f.add_argument("--dest", default=str(DEFAULT_RAW_DIR))
    f.add_argument("--title", action="append", help="restrict to these titles")
    f.set_defaults(func=cmd_fetch)

    e = sub.add_parser("extract", help="extract EDNOTEs, no network")
    e.add_argument("--raw", default=str(DEFAULT_RAW_DIR))
    e.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    e.set_defaults(func=cmd_extract)

    v = sub.add_parser("verify", help="check the frozen artefacts against the manifest")
    v.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    v.set_defaults(func=cmd_verify)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
