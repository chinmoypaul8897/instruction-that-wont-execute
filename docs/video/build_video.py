"""CH-13B - build the submission video from the deck, the script and the screencast.

    python docs/video/build_video.py

Re-runnable and deterministic in everything it controls: the same ``script.md``, the
same deck and the same recording produce the same frame list, the same durations and
the same concat plan. (The *recording* itself is a browser capture and is not
byte-reproducible; that is why ``record_worksheet.js`` writes a sidecar of measured
offsets, and everything downstream of it reads those numbers instead of assuming any.)

The pipeline
------------

1. ``docs/slides/script.md`` is parsed - one ``### Slide N`` heading per slide, each
   ``>`` block a caption block. **Nothing is timed by hand.** A block over 22 words is
   split at a sentence boundary, and inside a sentence only when one sentence is itself
   over 22 words.
2. ``duration = max(3.0, words / 2.8)``, rounded to 0.1s. The 3.0s floor is absolute.
3. ``render_frames.js`` screenshots one 1920x1080 PNG per segment with the caption
   rendered into the page, and reports the measured pixel height of every caption. A
   caption that would run past the band's 124px of text space is a hard failure here,
   not a clipped word discovered in the finished file.
4. The screencast is trimmed by its own measured lead-in and captioned with ffmpeg
   ``drawtext`` in the same band, at the same size, at the same x.
5. Three parts are encoded with identical settings, concatenated, given a silent AAC
   track, and written to ``dist/instruction-that-wont-execute.mp4``.

Every number in the summary is measured from the artifact it describes. ``ffprobe``
reads the finished file back; nothing is asserted from the plan.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "docs" / "slides" / "script.md"
DECK = REPO / "docs" / "slides" / "index.html"
ENDCARD = REPO / "docs" / "video" / "endcard.html"
DIST = REPO / "dist"
FRAMES = DIST / "frames"
CAST_DIR = DIST / "screencast"
CAST = CAST_DIR / "worksheet.webm"
CAST_META = CAST_DIR / "worksheet.json"
CAPS = DIST / "captions"
OUT = DIST / "instruction-that-wont-execute.mp4"
EVIDENCE = REPO / "docs" / "evidence" / "ch13b"

MAX_WORDS = 22
WPS = 2.8               # ~168 wpm
FLOOR = 3.0
TITLE_S = 4.0
ENDCARD_S = 4.0
CAP = 300.0             # 5:00, hard

# The band, in one place. render_frames.js gets these from the deck's own CSS; the
# ffmpeg overlay has to be told, so they are stated once and used by both.
BAND_TOP = 930
BAND_H = 150
BAND_X = 120
TEXT_Y = 959            # matches the browser's first-line box: 930 + 26 padding + half-leading
INK = "0x1A1A18"
PAPER = "0xFBFAF7"
FONT_SIZE = 30

# Where the screencast slots in: straight after the pipeline diagram.
CAST_AFTER_SLIDE = 5
NO_CAPTION_SLIDES = {1, 15}
BAR_CHART_SLIDE = 12
LAST_SLIDE = 15


# ---------------------------------------------------------------------------
# 1. the script
# ---------------------------------------------------------------------------

def parse_script() -> tuple[dict[int, list[str]], list[str]]:
    """``### Slide N`` / ``### Screencast`` headings -> their ``>`` blocks."""
    text = SCRIPT.read_text(encoding="utf-8")
    # anchored to the heading, not the words: the prose above mentions "## The lines"
    # by name, and splitting on the bare phrase silently took the sentence instead.
    parts = text.split("\n## The lines\n", 1)
    assert len(parts) == 2, "script.md has no '## The lines' heading"
    body = parts[1].split("\n---\n", 1)[0]
    slides: dict[int, list[str]] = {}
    cast: list[str] = []
    current: list[str] | None = None
    for chunk in re.split(r"^### ", body, flags=re.M)[1:]:
        head, _, rest = chunk.partition("\n")
        blocks = [re.sub(r"\s+", " ", b).strip()
                  for b in re.findall(r"^> (.+(?:\n> .+)*)", rest, flags=re.M)]
        blocks = [b.replace("> ", " ").strip() for b in blocks]
        m = re.match(r"Slide (\d+)", head.strip())
        if m:
            slides[int(m.group(1))] = blocks
        elif head.strip().startswith("Screencast"):
            cast = blocks
        else:
            raise AssertionError(f"unrecognised heading in script.md: {head!r}")
    assert set(slides) == set(range(1, LAST_SLIDE + 1)), f"script covers slides {sorted(slides)}"
    for n in NO_CAPTION_SLIDES:
        assert slides[n] == [], f"slide {n} is meant to carry no caption"
    return slides, cast


def words(s: str) -> int:
    return len(s.split())


def split_sentence(sentence: str) -> list[str]:
    """A single sentence over 22 words, broken at the latest comma that fits."""
    out, rest = [], sentence.split()
    while len(rest) > MAX_WORDS:
        window = rest[:MAX_WORDS]
        breaks = [i for i, w in enumerate(window) if w.endswith(",")]
        cut = (breaks[-1] + 1) if breaks else MAX_WORDS
        out.append(" ".join(rest[:cut]))
        rest = rest[cut:]
    if rest:
        out.append(" ".join(rest))
    return out


def segment(block: str) -> list[str]:
    """Pack whole sentences up to 22 words; split inside one only if forced."""
    sentences = [s.strip() for s in re.findall(r".+?(?:[.!?]|$)(?:\s|$)", block) if s.strip()]
    out: list[str] = []
    buf: list[str] = []
    for sentence in sentences:
        if words(sentence) > MAX_WORDS:
            if buf:
                out.append(" ".join(buf))
                buf = []
            out.extend(split_sentence(sentence))
            continue
        if buf and words(" ".join(buf)) + words(sentence) > MAX_WORDS:
            out.append(" ".join(buf))
            buf = []
        buf.append(sentence)
    if buf:
        out.append(" ".join(buf))
    assert all(words(s) <= MAX_WORDS for s in out), out
    return out


def duration(text: str) -> float:
    return round(max(FLOOR, words(text) / WPS), 1)


def slide_15_words() -> int:
    """Slide 15 carries no caption, so it holds for its own text at the same rate."""
    parts = re.findall(r'<section class="slide">(.*?)</section>', DECK.read_text(encoding="utf-8"),
                       flags=re.S)
    assert len(parts) == LAST_SLIDE, f"deck has {len(parts)} slides"
    stripped = re.sub(r"<[^>]+>", " ", parts[LAST_SLIDE - 1])
    stripped = stripped.replace("&mdash;", "-").replace("&nbsp;", " ")
    return words(re.sub(r"\s+", " ", stripped).strip())


# ---------------------------------------------------------------------------
# 1b. where the screencast actually holds still
# ---------------------------------------------------------------------------

MARK = {"x": 0, "y": 1000, "w": 120, "h": 80}      # must match record_worksheet.js
MARK_LEVELS = [20, 70, 120, 170, 220]              # one grey per beat, 50 apart
MARK_IDLE = 255                                    # before the storyboard starts


def read_beat_windows(path: Path, fps: int = 25) -> list[tuple[float, float]]:
    """Read the beat boundaries out of the recording, in the recording's own timebase.

    The first cut of this script timed the screencast captions off the recorder's wall
    clock, and the extracted frame proved that wrong: a caption reading "the trace row
    where the resolver returned found equals false" sat over 47 CFR 80.905 instead of
    the 49 CFR 1150.35 it names. Chromium's capture drops frames under load, so 41.9
    seconds at the keyboard came out 40.6 seconds on the tape - 3% short, and the error
    grew with every scroll.

    The second attempt looked for still stretches by frame differencing, and that failed
    differently and more quietly: at 64x36 greyscale a blank white page and a light
    document are nearly the same picture, so the lead-in merged into the first hold and
    the trim point was wrong by 1.8 seconds without anything looking broken.

    So the recorder now stamps its own clock into the picture. A 120x80 patch in the
    bottom-left carries one grey level per beat; this reads that patch back per frame
    and returns each beat's window. It is a measurement of the artifact in the
    artifact's timebase, and it cannot drift from what a viewer sees. The patch is
    never visible: it sits inside the strip the caption band paints over, which
    ``assert_mark_is_covered`` checks rather than assumes.
    """
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", fpath(path),
         "-vf", f"fps={fps},crop={MARK['w']}:{MARK['h']}:{MARK['x']}:{MARK['y']},"
                f"scale=1:1,format=gray", "-f", "rawvideo", "-"],
        capture_output=True, cwd=REPO).stdout
    assert raw, "the recording decoded to no frames"

    def classify(v: int) -> int | None:
        best = min(range(len(MARK_LEVELS)), key=lambda i: abs(MARK_LEVELS[i] - v))
        if abs(MARK_LEVELS[best] - v) <= 20:
            return best
        assert abs(MARK_IDLE - v) <= 24, f"unrecognised beat marker: grey {v}"
        return None

    seq = [classify(v) for v in raw]
    windows: list[tuple[float, float]] = []
    for k in range(len(MARK_LEVELS)):
        hits = [i for i, b in enumerate(seq) if b == k]
        assert hits, f"beat {k}'s marker never appears in the recording"
        # contiguous by construction; guard against a stray decode anyway
        assert hits[-1] - hits[0] + 1 == len(hits), f"beat {k}'s marker is not contiguous"
        windows.append((hits[0] / fps, (hits[-1] + 1) / fps))
    for a, b in zip(windows, windows[1:]):
        assert abs(a[1] - b[0]) < 1e-9, f"beats are not back to back: {a} then {b}"
    return windows


def assert_mark_is_covered() -> None:
    """The timing patch must be inside the strip the caption band paints over."""
    assert MARK["y"] >= BAND_TOP and MARK["y"] + MARK["h"] <= BAND_TOP + BAND_H, MARK
    assert MARK["x"] >= 0 and MARK["x"] + MARK["w"] <= 1920, MARK


# ---------------------------------------------------------------------------
# 2. the plan
# ---------------------------------------------------------------------------

def build_plan() -> dict:
    slides, cast_blocks = parse_script()
    meta = json.loads(CAST_META.read_text(encoding="utf-8"))
    beats = meta["beats"]
    assert len(cast_blocks) == len(beats), \
        f"script.md has {len(cast_blocks)} screencast captions for {len(beats)} beats"

    frames: list[dict] = []

    def add(source, slide, step, caption, dur, note):
        frames.append({"index": len(frames), "source": source, "slide": slide, "step": step,
                       "caption": caption, "words": words(caption) if caption else 0,
                       "duration": round(dur, 1), "note": note})

    add("deck", 1, 0, None, TITLE_S, "title card")

    for n in range(2, LAST_SLIDE + 1):
        if n == LAST_SLIDE:
            w = slide_15_words()
            add("deck", n, 0, None, round(max(FLOOR, w / WPS), 1),
                f"the hot take, uncaptioned - {w} words on the slide")
            continue
        blocks = slides[n]
        assert blocks, f"slide {n} has no caption blocks"
        if n == BAR_CHART_SLIDE:
            assert len(blocks) == 4, \
                f"slide {n} is the four-step reveal and needs exactly 4 blocks, got {len(blocks)}"
            for k, block in enumerate(blocks, start=1):
                segs = segment(block)
                assert len(segs) == 1, \
                    f"slide {n} block {k} split into {len(segs)}; one reveal is one frame"
                add("deck", n, k, segs[0], duration(segs[0]), f"reveal {k} of 4")
        else:
            for block in blocks:
                for seg in segment(block):
                    add("deck", n, 0, seg, duration(seg), "")
        if n == CAST_AFTER_SLIDE:
            frames.append({"index": len(frames), "source": "screencast", "slide": None,
                           "step": None, "caption": None, "words": sum(words(b) for b in cast_blocks),
                           "duration": None, "note": "the recording of docs/worksheet/index.html"})

    add(str(ENDCARD.relative_to(REPO)).replace("\\", "/"), None, 0, None, ENDCARD_S, "end card")

    # Timings come off the tape, not off the recorder's clock. See read_beat_windows.
    assert_mark_is_covered()
    windows = read_beat_windows(CAST)
    assert len(windows) == len(beats), f"{len(windows)} beats on the tape, {len(beats)} planned"
    lead_in = round(windows[0][0], 3)
    cast_dur = round(windows[-1][1] - lead_in, 3)

    cast_caps = []
    for k, block in enumerate(cast_blocks):
        start = round(windows[k][0] - lead_in, 3)
        stop = round(windows[k][1] - lead_in, 3)
        assert words(block) <= MAX_WORDS, f"screencast caption {k} is {words(block)} words"
        assert stop - start >= FLOOR - 1e-9, (
            f"screencast caption {k} would hold {stop - start:.2f}s, under the {FLOOR}s floor - "
            f"lengthen beat {k}'s hold in record_worksheet.js and re-record")
        cast_caps.append({"text": block, "words": words(block),
                          "from": start, "to": stop, "duration": round(stop - start, 3),
                          "beat": beats[k]["name"], "scroll_y": beats[k]["scroll_y"],
                          "wall_clock_hold_s": round(float(beats[k]["hold_to_s"])
                                                     - float(beats[k]["hold_from_s"]), 3)})

    return {"frames_dir": str(FRAMES.relative_to(REPO)).replace("\\", "/"),
            "frames": [f for f in frames if f["source"] != "screencast"],
            "timeline": frames,
            "screencast": {"lead_in_s": lead_in, "duration_s": cast_dur, "captions": cast_caps,
                           "measured_windows": [[round(a, 3), round(b, 3)] for a, b in windows],
                           "wall_clock_lead_in_s": float(meta["lead_in_s"]),
                           "wall_clock_duration_s": round(float(beats[-1]["hold_to_s"])
                                                          - float(meta["lead_in_s"]), 3),
                           "page_height_px": meta["page_height_px"],
                           "scrolled_px": meta["scrolled_px"]}}


# ---------------------------------------------------------------------------
# 3. ffmpeg
# ---------------------------------------------------------------------------

def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-4000:] + "\n" + proc.stderr[-4000:] + "\n")
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])} ...")


def fpath(p: Path) -> str:
    return str(p).replace("\\", "/")


def nb_frames(path: Path) -> int:
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                          "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", fpath(path)],
                         capture_output=True, text=True, cwd=REPO).stdout.strip()
    return int(out)


def encode_stills(frames: list[dict], out: Path, tag: str) -> int:
    """One segment per still, each an EXACT frame count, then concatenated.

    The obvious route - a single concat list with a ``duration`` per image - was tried
    first and measured 4.2% long: 69.0s of plan came out 74.7s, because the image
    demuxer carries a frame duration of its own that the directive does not replace.
    Every caption would then have sat on screen longer than the number this script
    printed for it. ``-frames:v round(d*30)`` cannot drift, and the assertion below
    proves it did not.
    """
    seg_dir = DIST / f"segments-{tag}"
    seg_dir.mkdir(parents=True, exist_ok=True)
    lines, expected = ["ffconcat version 1.0"], 0
    for f in frames:
        n = int(round(f["duration"] * 30))
        expected += n
        seg = seg_dir / f"{f['index']:03d}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1",
             "-i", fpath(FRAMES / f"{f['index']:03d}.png"), "-frames:v", str(n),
             "-vf", "format=yuv420p,setsar=1", "-r", "30",
             "-c:v", "libx264", "-crf", "10", "-preset", "veryfast", fpath(seg)])
        lines.append(f"file '{fpath(seg)}'")
    lst = DIST / f"concat-{tag}.txt"
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", fpath(lst),
         "-c", "copy", fpath(out)])
    got = nb_frames(out)
    assert got == expected, f"part {tag}: {got} frames encoded, {expected} planned"
    return expected


def encode_screencast(plan: dict, out: Path) -> None:
    CAPS.mkdir(parents=True, exist_ok=True)
    font = DIST / "caption-font.ttf"
    if not font.exists():
        shutil.copyfile(Path("C:/Windows/Fonts/georgia.ttf"), font)

    # Paths inside a filter description are RELATIVE, deliberately: ffmpeg reads a
    # colon as an option separator, so "C:/..." is a parse error and escaping it is one
    # more thing to get wrong. ffmpeg runs with cwd=REPO.
    rel_font = str(font.relative_to(REPO)).replace("\\", "/")
    chain = ["setpts=PTS-STARTPTS", "fps=30", "scale=1920:1080", "setsar=1",
             f"drawbox=x=0:y={BAND_TOP}:w=1920:h={BAND_H}:color={INK}@1:t=fill"]
    for k, cap in enumerate(plan["screencast"]["captions"]):
        f = CAPS / f"cast{k}.txt"
        f.write_text(cap["text"], encoding="utf-8")
        rel_txt = str(f.relative_to(REPO)).replace("\\", "/")
        chain.append(
            f"drawtext=fontfile={rel_font}:textfile={rel_txt}:"
            f"fontcolor={PAPER}:fontsize={FONT_SIZE}:x={BAND_X}:y={TEXT_Y}:"
            f"enable='between(t\\,{cap['from']}\\,{cap['to']})'")
    run(["ffmpeg", "-y", "-v", "error",
         "-ss", str(plan["screencast"]["lead_in_s"]), "-i", fpath(CAST),
         "-t", str(plan["screencast"]["duration_s"]),
         "-vf", ",".join(chain), "-an",
         "-c:v", "libx264", "-crf", "12", "-preset", "medium", fpath(out)])


def assemble(parts: list[Path], out: Path) -> None:
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for p in parts:
        cmd += ["-i", fpath(p)]
    cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    streams = "".join(f"[{i}:v]" for i in range(len(parts)))
    cmd += ["-filter_complex", f"{streams}concat=n={len(parts)}:v=1:a=0[v]",
            "-map", "[v]", "-map", f"{len(parts)}:a",
            "-c:v", "libx264", "-crf", "18", "-preset", "slow",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "96k", "-shortest",
            "-movflags", "+faststart", fpath(out)]
    run(cmd)


def probe(path: Path) -> dict:
    def q(args):
        return subprocess.run(["ffprobe", "-v", "error", *args, fpath(path)],
                              capture_output=True, text=True, cwd=REPO).stdout.strip()
    v = q(["-select_streams", "v:0", "-show_entries",
           "stream=width,height,avg_frame_rate,nb_frames,codec_name,pix_fmt",
           "-of", "default=noprint_wrappers=1:nokey=0"])
    a = q(["-select_streams", "a:0", "-show_entries",
           "stream=codec_name,sample_rate,channels", "-of", "default=noprint_wrappers=1:nokey=0"])
    d = q(["-show_entries", "format=duration,size", "-of", "default=noprint_wrappers=1:nokey=0"])
    out = {}
    for line in (v + "\n" + a + "\n" + d).splitlines():
        if "=" in line:
            k, _, val = line.partition("=")
            out.setdefault(k, val)
    return out


# ---------------------------------------------------------------------------

def main() -> int:
    assert CAST.is_file() and CAST_META.is_file(), \
        "run: node docs/video/record_worksheet.js  (writes dist/screencast/)"
    DIST.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    plan = build_plan()
    (DIST / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

    node = subprocess.run(["node", "docs/video/render_frames.js", "dist/plan.json"],
                          cwd=REPO, capture_output=True, text=True)
    sys.stdout.write(node.stdout)
    if node.returncode != 0:
        sys.stderr.write(node.stderr)
        return 1

    measured = json.loads((FRAMES / "_measured.json").read_text(encoding="utf-8"))
    by_index = {m["index"]: m for m in measured}
    over = [m for m in measured if m["caption_h"] > 124]
    assert not over, f"captions overflow the band: {[(m['index'], m['caption_h']) for m in over]}"
    clash = [m for m in measured
             if m["band_top"] is not None and m["content_bottom"] is not None
             and m["content_bottom"] > m["band_top"]]
    assert not clash, f"the caption band overlaps slide content on frames {[m['index'] for m in clash]}"
    spill = [m for m in measured if m["overflow_w"] > 1920 or m["overflow_h"] > 1080]
    assert not spill, f"slide content overflows 1920x1080 on frames {[m['index'] for m in spill]}"

    timeline = plan["timeline"]
    cut = next(i for i, f in enumerate(timeline) if f["source"] == "screencast")
    before = [f for f in timeline[:cut] if f["source"] != "screencast"]
    after = [f for f in timeline[cut + 1:] if f["source"] != "screencast"]

    part_a, part_b, part_c = DIST / "part-a.mp4", DIST / "part-b.mp4", DIST / "part-c.mp4"
    encode_stills(before, part_a, "a")
    encode_screencast(plan, part_b)
    encode_stills(after, part_c, "c")
    assemble([part_a, part_b, part_c], OUT)

    info = probe(OUT)
    stills = before + after
    shortest = min(f["duration"] for f in stills)
    longest_caption = max((f["words"] for f in stills if f["caption"]), default=0)
    cast_longest = max(c["words"] for c in plan["screencast"]["captions"])
    cast_shortest = min(c["duration"] for c in plan["screencast"]["captions"])
    planned = sum(f["duration"] for f in stills) + plan["screencast"]["duration_s"]
    dur = float(info["duration"])

    report = []
    w = report.append
    w("CH-13B  build_video.py")
    w("")
    w(f"  output              {OUT.relative_to(REPO)}")
    w(f"  ffprobe duration    {dur:.2f}s = {int(dur // 60)}:{dur % 60:05.2f}   (cap 5:00)"
      f"   {'UNDER' if dur < CAP else 'OVER - CUT SLIDES 10 AND 11'}")
    w(f"  resolution          {info['width']}x{info['height']}")
    w(f"  frame rate          {info['avg_frame_rate']}   pix_fmt {info['pix_fmt']}"
      f"   codec {info['codec_name']}")
    w(f"  audio stream        {info.get('codec_name.1', 'aac')} "
      f"{info.get('sample_rate', '?')}Hz {info.get('channels', '?')}ch")
    w(f"  size                {int(info['size']) / 1e6:.2f} MB")
    w("")
    still_s = sum(f["duration"] for f in stills)
    w(f"  still frames        {len(stills)}, {still_s:.1f}s   + screencast "
      f"{plan['screencast']['duration_s']:.2f}s   = {planned:.2f}s planned, "
      f"{dur:.2f}s encoded ({dur - planned:+.2f}s)")
    w(f"  shortest frame      {shortest:.1f}s   (floor {FLOOR:.1f}s)"
      f"   {'OK' if shortest >= FLOOR else 'UNDER FLOOR'}")
    w(f"  longest caption     {longest_caption} words on a still, {cast_longest} on the "
      f"screencast   (cap {MAX_WORDS})")
    w(f"  shortest screencast caption  {cast_shortest:.1f}s"
      f"   {'OK' if cast_shortest >= FLOOR else 'UNDER FLOOR'}")
    caph = [m["caption_h"] for m in measured if m["caption_h"] > 0]
    w(f"  caption band        {len(caph)} captions rendered, tallest {max(caph):.1f}px "
      f"of 124px available")
    w("")
    w(f"  screencast          {plan['screencast']['duration_s']:.2f}s, trimmed from "
      f"{plan['screencast']['lead_in_s']:.2f}s in")
    w(f"                      page {plan['screencast']['page_height_px']}px tall, "
      f"scrolled {plan['screencast']['scrolled_px']}px")
    for c in plan["screencast"]["captions"]:
        w(f"    {c['from']:6.2f}-{c['to']:6.2f}s  y={c['scroll_y']:<6}  {c['words']:2d}w  {c['beat'][:64]}")
    w("")
    w("  timeline")
    for f in timeline:
        if f["source"] == "screencast":
            w(f"    [--]  {plan['screencast']['duration_s']:5.1f}s  SCREENCAST  {f['note']}")
            continue
        tag = f"s{f['slide']:02d}" if f["slide"] else "end"
        step = f".{f['step']}" if f["step"] else "  "
        cap = f["caption"] or f"({f['note']})"
        w(f"    [{f['index']:02d}]  {f['duration']:5.1f}s  {tag}{step}  {f['words']:2d}w  {cap[:78]}")

    text = "\n".join(report)
    print(text)
    (EVIDENCE / "build-video.txt").write_text(text + "\n", encoding="utf-8")
    (EVIDENCE / "timeline.json").write_text(json.dumps(
        {"duration_s": dur, "probe": info, "plan": plan,
         "caption_heights": {str(m["index"]): m["caption_h"] for m in measured}},
        indent=2), encoding="utf-8")
    return 0 if dur < CAP and shortest >= FLOOR else 1


if __name__ == "__main__":
    raise SystemExit(main())
