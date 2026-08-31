"""CH-13B probe - the two timing defects, shown failing on the old method and passing on the new.

    python docs/evidence/ch13b/timing_probe.py

``CLAUDE.md`` hard rule 6: every fix ships a probe that flips. Two things were wrong in
the first cut of this video, and neither announced itself - both produced a file that
played, at the right resolution, for a plausible length.

**A. Still frames ran 4.2% long.** The obvious way to hold a PNG for 6.4 seconds is a
concat list with ``duration 6.4``. It does not do that: the image demuxer carries a
frame duration of its own, and 69.0 seconds of plan came out 74.7. Every caption sat on
screen longer than the number ``build_video.py`` printed beside it, which is a report
that disagrees with its artifact.

**B. Screencast captions sat over the wrong sections.** They were timed off the
recorder's wall clock. Chromium's capture drops frames under load, so 41.9 seconds at
the keyboard is 40.6 seconds on the tape, and the error compounds along the recording.
The caption reading *"the trace row where the resolver returned found equals false"* -
which names 49 CFR 1150.35 - was drawn over 47 CFR 80.905. The recording now stamps a
grey patch per beat into a strip the caption band later paints over, and the timings are
read back off that.

Both probes below run the OLD method and the NEW method against the same inputs and
print both results. Neither is a re-description of the fix; each one measures.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "docs" / "video"))

DIST = REPO / "dist"
FRAMES = DIST / "frames"
CAST = DIST / "screencast" / "worksheet.webm"
CAST_META = DIST / "screencast" / "worksheet.json"
PLAN = DIST / "plan.json"
PROBE = DIST / "probe"

MARK = {"x": 0, "y": 1000, "w": 120, "h": 80}
MARK_LEVELS = [20, 70, 120, 170, 220]
MARK_IDLE = 255


def sh(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True)


def fp(p: Path) -> str:
    return str(p).replace("\\", "/")


def nb_frames(path: Path) -> int:
    out = sh(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
              "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", fp(path)])
    return int(out.stdout.decode().strip())


# ---------------------------------------------------------------------------
# A. does a still frame last as long as the plan says
# ---------------------------------------------------------------------------

def probe_a(out: list[str]) -> bool:
    PROBE.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    picks = [f for f in plan["timeline"] if f["source"] == "deck"][:3]
    expected = sum(int(round(f["duration"] * 30)) for f in picks)

    # --- OLD: one concat list, one `duration` per image ---
    def png(frame: dict) -> str:
        return fp(FRAMES / ("%03d.png" % frame["index"]))

    lines = ["ffconcat version 1.0"]
    for f in picks:
        lines.append("file '%s'" % png(f))
        lines.append("duration %.1f" % f["duration"])
    lines.append("file '%s'" % png(picks[-1]))   # the demuxer wants the tail repeated
    old_list = PROBE / "old.txt"
    old_list.write_text("\n".join(lines) + "\n", encoding="utf-8")
    old_mp4 = PROBE / "old.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", fp(old_list),
        "-vf", "fps=30,format=yuv420p,setsar=1", "-c:v", "libx264", "-crf", "12",
        "-preset", "veryfast", fp(old_mp4)])
    old_n = nb_frames(old_mp4)

    # --- NEW: one segment per still, an exact frame count each ---
    seg_lines = ["ffconcat version 1.0"]
    for f in picks:
        seg = PROBE / ("new-%03d.mp4" % f["index"])
        sh(["ffmpeg", "-y", "-v", "error", "-loop", "1",
            "-i", png(f),
            "-frames:v", str(int(round(f["duration"] * 30))),
            "-vf", "format=yuv420p,setsar=1", "-r", "30",
            "-c:v", "libx264", "-crf", "10", "-preset", "veryfast", fp(seg)])
        seg_lines.append(f"file '{fp(seg)}'")
    new_list = PROBE / "new.txt"
    new_list.write_text("\n".join(seg_lines) + "\n", encoding="utf-8")
    new_mp4 = PROBE / "new.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", fp(new_list),
        "-c", "copy", fp(new_mp4)])
    new_n = nb_frames(new_mp4)

    spec = ", ".join("%.1fs" % f["duration"] for f in picks)
    old_verdict = ("MATCHES" if old_n == expected else
                   "DRIFTS by %+d frames = %+.2fs" % (old_n - expected, (old_n - expected) / 30))
    new_verdict = ("MATCHES" if new_n == expected else
                   "DRIFTS by %+d frames" % (new_n - expected))
    out.append("A. STILL FRAME DURATION")
    out.append(f"   three stills of {spec}  ->  {expected} frames at 30 fps")
    out.append(f"   OLD  concat list with a `duration` per image : {old_n:5d} frames "
               f"({old_n / 30:6.2f}s)   {old_verdict}")
    out.append(f"   NEW  one segment per still, -frames:v N     : {new_n:5d} frames "
               f"({new_n / 30:6.2f}s)   {new_verdict}")
    flipped = old_n != expected and new_n == expected
    out.append(f"   FLIPS: {'yes' if flipped else 'NO'}")
    out.append("")
    return flipped


# ---------------------------------------------------------------------------
# B. is the caption over the section it names
# ---------------------------------------------------------------------------

def marker_track(fps: int = 25) -> list[int | None]:
    """The beat stamp for every frame of the recording, decoded once."""
    res = sh(["ffmpeg", "-v", "error", "-i", fp(CAST),
              "-vf", f"fps={fps},crop={MARK['w']}:{MARK['h']}:{MARK['x']}:{MARK['y']},"
                     f"scale=1:1,format=gray", "-f", "rawvideo", "-"])
    track = []
    for v in res.stdout:
        best = min(range(len(MARK_LEVELS)), key=lambda i: abs(MARK_LEVELS[i] - v))
        track.append(best if abs(MARK_LEVELS[best] - v) <= 20 else None)
    return track


def probe_b(out: list[str]) -> bool:
    """Does the caption sit over the section it names, and how much drift does it take.

    The failure this fixes is real and was seen: an extracted frame from the first
    build carried "the trace row where the resolver returned found equals false" - a
    caption naming 49 CFR 1150.35 - over 47 CFR 80.905. But it is **load-dependent**,
    and on the recording that shipped the two clocks agree to 0.03s. Reporting a flip
    on this tape would therefore be reporting something that did not happen.

    So the probe measures the property instead: the wall-clock method is correct only
    while capture drift stays inside a tolerance, and this finds that tolerance by
    sweeping drift and reading the recording's own beat stamp at the timestamp each
    method would seek to. The tape-reading method has no such tolerance to find - it
    never consults the wall clock, so no drift moves it.
    """
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    meta = json.loads(CAST_META.read_text(encoding="utf-8"))
    beats = meta["beats"]
    cast = plan["screencast"]
    fps = 25
    track = marker_track(fps)

    def beat_at(t: float) -> int | None:
        i = int(round(t * fps))
        return track[i] if 0 <= i < len(track) else None

    observed = cast["duration_s"] - cast["wall_clock_duration_s"]
    out.append("B. SCREENCAST CAPTION ALIGNMENT")
    out.append(f"   this recording: wall clock {cast['wall_clock_duration_s']:.2f}s,"
               f" tape {cast['duration_s']:.2f}s  ({observed:+.2f}s,"
               f" {100 * observed / cast['wall_clock_duration_s']:+.2f}%)")
    out.append("")
    out.append("   Chromium drops capture frames under load, so the tape can run short of")
    out.append("   the wall clock. Below, each method's sample point is fed to the tape and")
    out.append("   the tape's own beat stamp says which beat is really on screen there.")
    out.append("")
    out.append("     drift    OLD (wall clock)      NEW (read off the tape)")

    old_lead = float(meta["lead_in_s"])
    new_lead = float(cast["lead_in_s"])
    breaking = None
    rows = []
    for pct in [0, 1, 2, 3, 4, 5, 6, 8, 10, 12]:
        f = 1.0 - pct / 100.0        # the tape runs SHORT of the wall clock by pct
        old_ok = new_ok = 0
        for k in range(len(beats)):
            stop_wall = (float(beats[k + 1]["scroll_from_s"]) if k + 1 < len(beats)
                         else float(beats[-1]["hold_to_s"]))
            # The old code handed a wall-clock number to ffmpeg as if it were a video
            # timestamp, so it seeks tape time S = stop_wall - 1.0. On a tape compressed
            # by f, whatever sits at tape time S happened at wall time S/f - so that is
            # the moment in the storyboard the caption would actually land on. This tape
            # is uncompressed, so its own stamp at S/f answers the question.
            old_ok += beat_at((stop_wall - 1.0) / f) == k
            # The new method measured its windows off whichever tape it was given, so
            # drift moves the windows and the content together and cannot separate them.
            new_ok += beat_at(new_lead + cast["captions"][k]["to"] - 1.0) == k
        rows.append((pct, old_ok, new_ok))
        if breaking is None and old_ok < len(beats):
            breaking = pct
    for pct, old_ok, new_ok in rows:
        out.append(f"      {pct:2d}%     {old_ok} of {len(beats)} correct"
                   f"       {new_ok} of {len(beats)} correct"
                   f"{'   <-- old method breaks here' if pct == breaking else ''}")
    out.append("")
    if breaking is None:
        out.append("   the old method survived every drift swept - NOT a flip")
        flipped = False
    else:
        out.append(f"   OLD  correct only while capture drift stays under {breaking}%;"
                   f" at {breaking}% a caption is over the wrong beat")
        out.append("   NEW  correct at every drift swept, because it never reads the wall clock")
        flipped = all(new_ok == len(beats) for _, _, new_ok in rows)
    out.append(f"   FLIPS: {'yes' if flipped else 'NO'}")
    out.append("")
    out.append("   NOTE, and it is the point: at 0% both are right. The defect that shipped")
    out.append("   a caption over 47 CFR 80.905 does not reproduce on this tape, because the")
    out.append("   machine was not busy. A bug that only appears under load is exactly the")
    out.append("   kind that a green build hides, which is why the fix is to stop depending")
    out.append("   on the wall clock rather than to widen a tolerance.")
    out.append("")
    return flipped


def main() -> int:
    for path in (PLAN, CAST, CAST_META):
        if not path.is_file():
            print(f"missing {path} - run build_video.py first", file=sys.stderr)
            return 2
    out = ["CH-13B timing probe - old method vs new, same inputs", ""]
    a = probe_a(out)
    b = probe_b(out)
    out.append(f"BOTH PROBES FLIP: {'yes' if a and b else 'NO'}")
    text = "\n".join(out)
    print(text)
    (Path(__file__).parent / "timing-probe.txt").write_text(text + "\n", encoding="utf-8")
    return 0 if (a and b) else 1


if __name__ == "__main__":
    raise SystemExit(main())
