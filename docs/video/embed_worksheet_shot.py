"""CH-13B - inline the worksheet screenshot into the deck as a data: URI.

The deck has to open from the file alone, offline, on a machine that has never
seen this repository - ``tests/test_slides.py`` asserts that and the video is
rendered from the same file. So the worksheet picture cannot be an ``src`` that
points at ``dist/``; it is base64 and it lives in the HTML.

Run order::

    node docs/video/shoot_worksheet.js
    python docs/video/embed_worksheet_shot.py

The payload is written between ``WORKSHEET-SHOT-BEGIN`` and
``WORKSHEET-SHOT-END``, so re-running replaces it rather than accumulating.
The script asserts the PNG is exactly 1920x1080 before it writes anything - a
screenshot taken at the wrong viewport would otherwise ship silently.
"""
from __future__ import annotations

import base64
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PNG = REPO / "dist" / "worksheet-1920x1080.png"
DECK = REPO / "docs" / "slides" / "index.html"
BEGIN = "<!-- WORKSHEET-SHOT-BEGIN -->"
END = "<!-- WORKSHEET-SHOT-END -->"


def png_size(blob: bytes) -> tuple[int, int]:
    """Width and height out of the IHDR chunk. No image library needed."""
    assert blob[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    assert blob[12:16] == b"IHDR", "first chunk is not IHDR"
    return struct.unpack(">II", blob[16:24])


def main() -> int:
    if not PNG.is_file():
        print(f"missing {PNG} - run: node docs/video/shoot_worksheet.js", file=sys.stderr)
        return 1
    blob = PNG.read_bytes()
    width, height = png_size(blob)
    assert (width, height) == (1920, 1080), f"screenshot is {width}x{height}, expected 1920x1080"

    payload = base64.b64encode(blob).decode("ascii")
    img = ('          <img class="shot" alt="the codification worksheet, arm A1 rep 1" '
           'src="data:image/png;base64,' + payload + '">')

    html = DECK.read_text(encoding="utf-8")
    start = html.index(BEGIN) + len(BEGIN)
    stop = html.index(END)
    before, after = html[:start], html[stop:]
    new = before + "\n" + img + "\n" + after

    # hard rule 16 - assert the new text is present AND the old text is gone.
    assert 'src="data:image/png;base64,' in new
    assert '<div class="shot" style="width:1030px;height:579px;"></div>' not in new
    assert new.count(BEGIN) == 1 and new.count(END) == 1
    DECK.write_text(new, encoding="utf-8")

    print(f"png            {len(blob):,} bytes  {width}x{height}")
    print(f"base64         {len(payload):,} chars")
    print(f"deck           {len(new):,} bytes  (was {len(html):,})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
