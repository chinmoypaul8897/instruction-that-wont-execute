#!/usr/bin/env python3
"""CH-12 - the probe for the silent-normalisation defect. It FLIPS.

Hard rule 6: every fix ships a probe that fails on the old code and passes on the new,
and both are shown. This is that probe, and it is kept forever.

THE DEFECT. `build_worksheet.py::highlight()` used to draw the `<mark>` only when the
section text at `char_offset` was **byte-identical** to the quoted anchor:

    if text[offset:offset + len(anchor)] != anchor:
        return esc(text)              # <- draws nothing, says nothing

That condition is false exactly when the match was made at `whitespace-collapsed` or
`alphanumeric-only`, because at those levels the offset points at the text that matched
**after punctuation or spacing was dropped** — not at the quoted string. On this corpus
two of the ten rendered items resolve that way:

    2016-09949|1436.3   quoted 'Collateral;'                    codified 'Collateral '
    2024-21984|1321.9   quoted '...subpart F,'                  codified '...subpart F.'

Both rendered as if **nothing had been found**. The page was silently applying a
normalisation level instead of reporting it — which is what `CLAUDE.md` hard rule 7
exists to forbid, in the one artifact whose whole job is to report it.

**Counting caught this. Reading the page did not**: the missing highlight looks exactly
like an item that legitimately has no anchor.

THE FIX. The matched region is always marked; when it diverges from the quote it is
marked differently and the page says so in words, showing both strings and leaving the
judgement to the drafter.

Run:  python docs/evidence/ch12/highlight_probe.py
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PAGE = ROOT / "docs" / "worksheet" / "index.html"
ITEMS = ROOT / "data" / "evalset" / "items.jsonl"
ARTIFACTS = ROOT / "docs" / "evidence" / "ch06-a1" / "A1-rep1-artifacts.jsonl"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def highlight_OLD(text: str, anchor: str | None, offset: int | None) -> str:
    """The shipped-and-wrong version, reproduced verbatim so the probe is honest."""
    if anchor is None or offset is None or offset < 0 or offset + len(anchor) > len(text):
        return esc(text)
    if text[offset:offset + len(anchor)] != anchor:
        return esc(text)                       # <-- the defect
    return (esc(text[:offset]) + "<mark>" + esc(anchor) + "</mark>"
            + esc(text[offset + len(anchor):]))


def highlight_NEW(text: str, anchor: str | None, offset: int | None) -> str:
    """The fix: mark the region that matched, whatever it turned out to be."""
    if anchor is None or offset is None or offset < 0 or offset + len(anchor) > len(text):
        return esc(text)
    matched = text[offset:offset + len(anchor)]
    css = "mark" if matched == anchor else 'mark class="loose"'
    return (esc(text[:offset]) + f"<{css}>" + esc(matched) + "</mark>"
            + esc(text[offset + len(anchor):]))


def main() -> int:
    items = {json.loads(l)["item_id"]: json.loads(l)
             for l in ITEMS.read_text(encoding="utf-8").splitlines() if l.strip()}
    arts = {json.loads(l)["item_id"]: json.loads(l)
            for l in ARTIFACTS.read_text(encoding="utf-8").splitlines() if l.strip()}

    page = PAGE.read_text(encoding="utf-8")
    rendered = sorted(set(re.findall(r'<span class="pill">([^<]+)</span>', page)))

    print("CH-12 - SILENT-NORMALISATION PROBE")
    print("=" * 92)
    print(f"items rendered on the worksheet: {len(rendered)}\n")

    print(f"{'item':<24}{'level':<20}{'quoted anchor':<34}{'codified at that offset'}")
    print("-" * 118)

    old_marks = new_marks = resolvable = divergent = 0
    for item_id in rendered:
        a, it = arts[item_id], items[item_id]
        hit = next((t for t in a["resolution_trace"]
                    if t["found"] and t["char_offset"] is not None), None)
        if not hit:
            continue
        resolvable += 1
        text, off, anchor = it["section_text"], hit["char_offset"], hit["anchor"]
        matched = text[off:off + len(anchor)]
        if matched != anchor:
            divergent += 1
            print(f"{item_id:<24}{hit['level']:<20}{anchor[:32]!r:<34}{matched[:32]!r}")
        old_marks += highlight_OLD(text, anchor, off).count("<mark")
        new_marks += highlight_NEW(text, anchor, off).count("<mark")

    print("-" * 118)
    print(f"\nrendered items whose anchor RESOLVED at a char_offset : {resolvable}")
    print(f"  of which the codified text DIVERGES from the quote  : {divergent}")
    print(f"  of which it is byte-identical                       : {resolvable - divergent}")
    assert divergent + (resolvable - divergent) == resolvable, "success + failure != n"
    print(f"  success + failure == n : {divergent} + {resolvable - divergent} "
          f"== {resolvable}  OK\n")

    print("THE PROBE")
    print("-" * 92)
    print(f"  marks drawn by the OLD highlighter : {old_marks}   "
          f"(expected {resolvable})")
    print(f"  marks drawn by the NEW highlighter : {new_marks}   "
          f"(expected {resolvable})")
    print(f"  marks on the SHIPPED page          : "
          f"{len(re.findall(r'<mark[ >]', page))}")

    old_fails = old_marks != resolvable
    new_passes = new_marks == resolvable
    shipped_ok = len(re.findall(r"<mark[ >]", page)) == resolvable
    named = page.count("THE CODIFIED TEXT IS NOT THE QUOTED TEXT") == divergent

    print()
    print(f"  FAILS on the old code  : {old_fails}   "
          f"({resolvable - old_marks} resolved anchors drawn as if not found)")
    print(f"  PASSES on the new code : {new_passes}")
    print(f"  shipped page agrees    : {shipped_ok}")
    print(f"  divergence NAMED in words on the page, {divergent} time(s) : {named}")

    verdict = old_fails and new_passes and shipped_ok and named
    print(f"\nVERDICT: {'PASS - the probe flips' if verdict else 'FAIL'}")
    print("\nThe kept guard is `tests/test_worksheet.py::"
          "test_every_resolvable_anchor_is_actually_highlighted`.")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
