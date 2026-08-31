"""CH-13B - pull frames back out of the finished MP4 and save them as evidence.

    python docs/video/extract_frames.py

The build script can only report what it planned. This reads the *encoded* file, so
what lands in ``docs/evidence/ch13b/`` is what a judge will actually see: a still with
its caption band, a step of the bar chart mid-reveal, and a frame of the screencast
with its ffmpeg-drawn caption in the same band.

Offsets are computed from ``dist/plan.json``, so a frame is grabbed from the middle of
the segment it belongs to rather than at a hand-picked timestamp that drifts the next
time a caption is reworded.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "dist" / "plan.json"
MP4 = REPO / "dist" / "instruction-that-wont-execute.mp4"
OUT = REPO / "docs" / "evidence" / "ch13b"

# (label, how to find the segment). Each returns an index into the timeline.
WANTED = [
    ("slide", lambda t: next(i for i, f in enumerate(t)
                             if f["source"] == "deck" and f["slide"] == 9 and f["caption"])),
    ("barchart", lambda t: next(i for i, f in enumerate(t)
                                if f["slide"] == 12 and f["step"] == 2)),
    ("screencast", lambda t: next(i for i, f in enumerate(t) if f["source"] == "screencast")),
]


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    timeline = plan["timeline"]
    cast_s = plan["screencast"]["duration_s"]

    starts, clock = [], 0.0
    for f in timeline:
        starts.append(clock)
        clock += cast_s if f["source"] == "screencast" else f["duration"]

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, find in WANTED:
        i = find(timeline)
        f = timeline[i]
        length = cast_s if f["source"] == "screencast" else f["duration"]
        # Halfway through a still. On the screencast, one second before the third
        # beat's window ends - which is inside its hold, so the page is stationary and
        # the caption naming it is up. Anchored to the END of the window, because the
        # window's length is measured off the tape and its start is a scroll.
        at = starts[i] + (length / 2 if f["source"] != "screencast"
                          else plan["screencast"]["captions"][2]["to"] - 1.0)
        dest = OUT / f"frame-{label}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{at:.3f}", "-i", str(MP4),
                        "-frames:v", "1", "-y", str(dest)], cwd=REPO, check=True)
        rows.append((label, i, at, length, f.get("caption"), f["note"], dest))

    lines = ["CH-13B - frames extracted from the encoded MP4",
             f"source: {MP4.relative_to(REPO)}", ""]
    for label, i, at, length, caption, note, dest in rows:
        lines.append(f"{label:12s} timeline[{i}]  t = {at:7.2f}s  segment {length:5.2f}s")
        lines.append(f"             {dest.relative_to(REPO)}")
        lines.append(f"             caption: {caption or '(none) ' + note}")
        lines.append("")
    text = "\n".join(lines)
    print(text)
    (OUT / "frames-extracted.txt").write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
