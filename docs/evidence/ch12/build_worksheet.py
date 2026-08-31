#!/usr/bin/env python3
"""CH-12 - build the codification worksheet from COMMITTED artifacts.

Reads only two files, both already in the repository and both frozen:

    data/evalset/items.jsonl                       the frozen eval set (n = 82)
    docs/evidence/ch06-a1/A1-rep1-artifacts.jsonl  arm A1, rep 1, per-item output

and writes ONE self-contained static HTML file:

    docs/worksheet/index.html

PURITY (hard rule 8) and DETERMINISM (hard rule 9). No network, no clock, no
randomness, no model call, no `git` invocation. The provenance footer is stamped
with the SHA-256 of each input and with commit hashes passed in as constants below,
never with `HEAD` -- embedding HEAD would make the output change on every commit and
break the byte-identical guarantee. Re-running this script on an unchanged tree
reproduces the file byte for byte; `tests/test_worksheet.py` asserts exactly that.

The page is offline by construction: no <script>, no <link>, no <img>, no @import,
no url(), no external font. Everything is inline. See `tests/test_worksheet.py`.
"""

from __future__ import annotations

import hashlib
import html
import json
import pathlib
import sys

# --------------------------------------------------------------------------- paths
ROOT = pathlib.Path(__file__).resolve().parents[3]
ITEMS = ROOT / "data" / "evalset" / "items.jsonl"
ARTIFACTS = ROOT / "docs" / "evidence" / "ch06-a1" / "A1-rep1-artifacts.jsonl"
SUMMARY = ROOT / "docs" / "evidence" / "ch06-a1" / "A1-rep1.json"
OUT = ROOT / "docs" / "worksheet" / "index.html"

# The commit that introduced the A1 rep-1 artifacts. Constant, not read from git,
# so the output is deterministic. Re-derive with:
#   git log --format=%h -- docs/evidence/ch06-a1/A1-rep1-artifacts.jsonl
ARTIFACT_COMMIT = "89d58c5"
# The commit that froze the eval set read here:
#   git log --format=%h -1 -- data/evalset/items.jsonl
EVALSET_COMMIT = "76e2e4b"

# --------------------------------------------------------------- the selection rule
# Published here, in the page, and in docs/evidence/ch12/worksheet-selection.md
# BEFORE it is applied. Every clause is deterministic and ties break on sorted
# item_id, so no item is chosen because of how it looks.
SELECTION_RULE = [
    ("W1", "the composition exemplar named in <code>docs/evidence/ch06-a1/EXEMPLAR-composition.md</code> "
           "- the item where the model overrode <code>cfr_resolve</code> and published the tool's limitation"),
    ("W2", "for every distinct <b>failure class</b> A1 emitted, the first item carrying it by sorted <code>item_id</code>"),
    ("W3", "for every distinct <b>human-checkpoint reason class</b> (C1 / C2 / C3), the first item carrying it by sorted <code>item_id</code>"),
    ("W4", "every item where an anchor resolved at a normalisation level <b>other than <code>exact</code></b> "
           "- hard rule 7 says the level achieved is reported, never applied silently"),
    ("W5", "the first item by sorted <code>item_id</code> whose emitted verdict <b>disagreed with gold</b> "
           "- failures are never filtered out"),
]
EXEMPLAR_ITEM = "05-8447|75.31"
EXEMPLAR_INSTRUCTION = 4


# ---------------------------------------------------------------------- selection
def select(items: dict, arts: dict) -> list[tuple[str, list[str]]]:
    """Apply SELECTION_RULE. Returns [(item_id, [clause ids])] sorted by item_id."""
    picked: dict[str, list[str]] = {}

    def take(item_id: str, clause: str) -> None:
        picked.setdefault(item_id, [])
        if clause not in picked[item_id]:
            picked[item_id].append(clause)

    ordered = sorted(arts.values(), key=lambda a: a["item_id"])

    # W1
    take(EXEMPLAR_ITEM, "W1")

    # W2 - one per distinct failure class
    seen_fc: set[str] = set()
    for a in ordered:
        fc = a["failure_class"]
        if fc and fc not in seen_fc:
            seen_fc.add(fc)
            take(a["item_id"], "W2")

    # W3 - one per distinct checkpoint reason class
    seen_rc: set[str] = set()
    for a in ordered:
        for cls in reason_classes(a):
            if cls not in seen_rc:
                seen_rc.add(cls)
                take(a["item_id"], "W3")

    # W4 - every non-exact resolution
    for a in ordered:
        for t in a["resolution_trace"]:
            if t["found"] and t["level"] not in (None, "none", "exact"):
                take(a["item_id"], "W4")

    # W5 - first disagreement with gold
    for a in ordered:
        if a["verdict"] != items[a["item_id"]]["label"]:
            take(a["item_id"], "W5")
            break

    return sorted(picked.items())


def reason_classes(a: dict) -> list[str]:
    """C1 / C2 / C3 classes present in an artifact's review_reason, sorted."""
    if not a.get("review_reason"):
        return []
    out = set()
    for part in a["review_reason"].split(";"):
        part = part.strip()
        if len(part) >= 2 and part[0] == "C" and part[1].isdigit():
            out.add(part[:2])
    return sorted(out)


# ------------------------------------------------------------------------- render
def esc(s) -> str:
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def code(s) -> str:
    return f'<code>{esc(s)}</code>'


def highlight(text: str, anchor: str | None, offset: int | None) -> str:
    """Escape the section text, marking the anchor at char_offset if given.

    char_offset indexes the CALLER's string (src/cfr_resolve.py asserts this before
    returning), so the slice is taken on the raw text and each part escaped
    separately. When the offset is absent the text is escaped whole.
    """
    if anchor is None or offset is None or offset < 0 or offset + len(anchor) > len(text):
        return esc(text)
    if text[offset:offset + len(anchor)] != anchor:
        # The offset does not point at the anchor. Report that rather than guessing.
        return esc(text)
    return (esc(text[:offset]) + "<mark>" + esc(anchor) + "</mark>"
            + esc(text[offset + len(anchor):]))


def window(text: str, offset: int | None, radius: int = 700) -> tuple[str, int]:
    """A readable window of the section text around offset. Returns (text, start)."""
    if offset is None:
        return text[: radius * 2], 0
    start = max(0, offset - radius)
    end = min(len(text), offset + radius)
    return text[start:end], start


LEVEL_NOTE = {
    "exact": "byte-for-byte",
    "whitespace-collapsed": "runs of whitespace folded to one space",
    "alphanumeric-only": "everything but letters and digits dropped; case NOT folded",
    "none": "not found at any declared level",
}


def render_trace_row(t: dict, ins: dict) -> str:
    lvl = t["level"] or "none"
    lvl_cls = {"exact": "lvl exact", "none": "lvl none"}.get(lvl, "lvl loose")
    resolved = "yes" if t["found"] else "no"
    resolved_cls = "yes" if t["found"] else "no"

    if t["designation"] is None:
        desig = '<span class="k">none asked</span>'
    elif t["designation_exists"] is True:
        desig = f'{code(t["designation"])} <span class="ok">exists</span>'
    elif t["designation_exists"] is False:
        desig = f'{code(t["designation"])} <span class="absent">DOES NOT EXIST</span>'
    else:
        desig = f'{code(t["designation"])} <span class="k">not asked</span>'

    # Siblings are the point when the target did not resolve.
    sibs = t.get("siblings") or []
    if t["designation_exists"] is False or not t["found"]:
        sib_html = (" ".join(code(s) for s in sibs)
                    if sibs else '<span class="k">none reported</span>')
    else:
        sib_html = '<span class="k">n/a - resolved</span>'

    anchor = t["anchor"]
    anchor_html = (f'<span class="q">{esc(anchor)}</span>' if anchor
                   else '<span class="k">no quoted anchor in the instruction</span>')

    ruling = t.get("model_ruling") or {}
    why = ruling.get("why")
    executes = ruling.get("executes")
    verdict_bit = ("" if executes is None else
                   f'<span class="mini {"WILL_EXECUTE" if executes else "WILL_FAIL"}">'
                   f'{"executes" if executes else "fails"}</span>')

    override = ""
    if why and "cannot see" in why:
        override = ' <span class="flag">MODEL OVERRODE THE TOOL</span>'

    return f"""
    <tr>
      <td class="num">{t["instruction_index"]}</td>
      <td>{code(t["operation"] or "-")}<div class="k instr">{esc(ins.get("text") or "")}</div></td>
      <td>{anchor_html}</td>
      <td><span class="res {resolved_cls}">{resolved}</span></td>
      <td><span class="{lvl_cls}">{esc(lvl)}</span>
          <div class="k">{esc(LEVEL_NOTE.get(lvl, ""))}</div>
          {'<div class="k">char_offset ' + str(t["char_offset"]) + "</div>" if t["char_offset"] is not None else ""}</td>
      <td>{desig}</td>
      <td class="sibs">{sib_html}</td>
      <td>{verdict_bit}{override}<div class="k why">{esc(why or "")}</div></td>
    </tr>"""


def render_item(item_id: str, clauses: list[str], it: dict, a: dict) -> str:
    gold = it["label"]
    verdict = a["verdict"]
    agrees = gold == verdict

    rows = "".join(render_trace_row(t, it["instructions"][t["instruction_index"] - 1])
                   for t in a["resolution_trace"])

    # The section text, windowed on the first resolved anchor if there is one.
    hit = next((t for t in a["resolution_trace"]
                if t["found"] and t["char_offset"] is not None), None)
    text = it["section_text"]
    if hit:
        win, start = window(text, hit["char_offset"])
        body = highlight(win, hit["anchor"], hit["char_offset"] - start)
        cap = (f'anchor of instruction {hit["instruction_index"]} highlighted at '
               f'char_offset {hit["char_offset"]}, level <code>{esc(hit["level"])}</code>'
               + (f' - window starts at char {start}' if start else ""))
    else:
        win, start = window(text, None)
        body = esc(win)
        missing = [t for t in a["resolution_trace"] if t["designation_exists"] is False]
        cap = ("no anchor resolved anywhere in this section at any declared level"
               + (f' - and {", ".join(esc(t["designation"]) for t in missing)} '
                  f'{"is" if len(missing) == 1 else "are"} not codified in it'
                  if missing else ""))
    truncated = len(win) < len(text)

    checkpoint = ""
    if a["needs_human_review"]:
        checkpoint = (f'<p class="routed"><b>ROUTED TO THE HUMAN CHECKPOINT.</b> '
                      f'{esc(a["review_reason"])}</p>')

    return f"""
  <section class="item" id="{esc(item_id.replace("|", "--"))}">
    <h3>{esc(it["cfr_title"])} CFR {esc(it["section"])}
        <span class="pill">{esc(item_id)}</span>
        {"".join(f'<span class="clause">{c}</span>' for c in clauses)}</h3>
    <table class="meta"><tbody>
      <tr><th>rule</th><td>FR Doc {esc(it["frdoc"])}, {esc(it["fr_citation"])},
          published {esc(it["publication_date"])}</td></tr>
      <tr><th>section text as of</th><td>{esc(it["as_of_edition"])} annual edition,
          revised {esc(it["as_of_revision_date"])}
          <span class="k">- strictly before publication</span></td></tr>
      <tr><th>gold label</th><td><span class="verdict {esc(gold)}">{esc(gold)}</span>
          <span class="k">- {"NARA published a live codification-defect note"
                            if gold == "WILL_FAIL" else "no defect note; the instruction codified"}</span></td></tr>
      <tr><th>emitted verdict</th><td><span class="verdict {esc(verdict)}">{esc(verdict)}</span>
          <span class="k">- derived in code from the per-instruction rulings below,
          never asserted directly</span>
          {'<span class="agree">agrees with gold</span>' if agrees
           else '<span class="disagree">DISAGREES WITH GOLD</span>'}</td></tr>
      <tr><th>failing designation</th><td>{code(a["failing_designation"]) if a["failing_designation"]
          else '<span class="k">none - no instruction failed</span>'}</td></tr>
      <tr><th>failure class</th><td>{code(a["failure_class"]) if a["failure_class"]
          else '<span class="k">none</span>'}</td></tr>
      <tr><th>instructions</th><td>{it["instruction_count"]} ·
          {a["tool_calls_made"]} <code>cfr_resolve</code> call(s) made</td></tr>
    </tbody></table>
    {checkpoint}

    <h4>Resolution trace</h4>
    <div class="scroll"><table class="trace">
      <thead><tr>
        <th>#</th><th>operation</th><th>anchor</th><th>resolved</th>
        <th>normalisation level</th><th>designation</th><th>siblings</th>
        <th>per-instruction ruling</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table></div>

    <h4>Section text <span class="k">- {cap}</span></h4>
    <div class="txt">{body}{'<span class="k">[...] window truncated for the page; '
                             'the full section text is in data/evalset/items.jsonl</span>'
                             if truncated else ''}</div>
  </section>"""


# --------------------------------------------------------------------------- main
def main() -> int:
    items = {json.loads(l)["item_id"]: json.loads(l)
             for l in ITEMS.read_text(encoding="utf-8").splitlines() if l.strip()}
    arts = {json.loads(l)["item_id"]: json.loads(l)
            for l in ARTIFACTS.read_text(encoding="utf-8").splitlines() if l.strip()}
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert set(items) == set(arts), "item_id sets differ between eval set and artifacts"
    n = len(items)
    agree = sum(1 for k in items if arts[k]["verdict"] == items[k]["label"])
    routed = [k for k in sorted(items) if arts[k]["needs_human_review"]]
    assert len(routed) == summary["items_routed_to_human"], "routed count disagrees with the run summary"

    # Level census across all 82 items - reported, never applied silently (hard rule 7).
    levels: dict[str, int] = {}
    for a in arts.values():
        for t in a["resolution_trace"]:
            levels[t["level"] or "none"] = levels.get(t["level"] or "none", 0) + 1
    n_instructions = sum(len(a["resolution_trace"]) for a in arts.values())

    picked = select(items, arts)

    # -------------------------------------------------------------- checkpoint queue
    queue_rows = []
    for k in routed:
        a, it = arts[k], items[k]
        reasons = [p.strip() for p in a["review_reason"].split(";") if p.strip()]
        queue_rows.append(f"""
      <tr>
        <td>{code(k)}<div class="k">{esc(it["cfr_title"])} CFR {esc(it["section"])}</div></td>
        <td><span class="verdict {esc(a["verdict"])}">{esc(a["verdict"])}</span></td>
        <td>{" ".join(f'<span class="clause">{c}</span>' for c in reason_classes(a))}</td>
        <td class="why">{"<br>".join(esc(r) for r in reasons)}</td>
      </tr>""")

    rule_rows = "".join(
        f'<tr><td class="clause-cell"><span class="clause">{cid}</span></td><td>{text}</td></tr>'
        for cid, text in SELECTION_RULE)

    level_rows = "".join(
        f'<tr><td><code>{esc(lv)}</code></td><td class="num">{levels.get(lv, 0)}</td>'
        f'<td class="k">{esc(LEVEL_NOTE.get(lv, ""))}</td></tr>'
        for lv in ("exact", "whitespace-collapsed", "alphanumeric-only", "none"))

    digests = {p.relative_to(ROOT).as_posix():
               hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (ITEMS, ARTIFACTS, SUMMARY)}
    digest_rows = "".join(
        f'<tr><td><code>{esc(k)}</code></td><td class="mono hash">{esc(v)}</td></tr>'
        for k, v in digests.items())

    body_items = "".join(render_item(k, cl, items[k], arts[k]) for k, cl in picked)

    doc = PAGE.format(
        n=n,
        agree=agree,
        accuracy=f"{agree / n:.4f}",
        routed=len(routed),
        n_instructions=n_instructions,
        n_selected=len(picked),
        model=esc(summary["model"]),
        arm=esc(summary["arm"]),
        rep=summary["rep"],
        tool_calls=summary["tool_calls"],
        tokens_in=f'{summary["usage"]["in"]:,}',
        tokens_out=f'{summary["usage"]["out"]:,}',
        rule_rows=rule_rows,
        level_rows=level_rows,
        items=body_items,
        queue_rows="".join(queue_rows),
        digest_rows=digest_rows,
        artifact_commit=ARTIFACT_COMMIT,
        evalset_commit=EVALSET_COMMIT,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT).as_posix()}  {len(doc.encode('utf-8')):,} B")
    print(f"  items in eval set        : {n}")
    print(f"  A1 rep 1 agrees with gold: {agree}/{n} = {agree / n:.4f}")
    print(f"  routed to the checkpoint : {len(routed)}/{n}")
    print(f"  instructions traced      : {n_instructions}")
    print(f"  normalisation levels     : {levels}")
    print(f"  items selected           : {len(picked)} -> {[k for k, _ in picked]}")
    return 0


# ----------------------------------------------------------------------- the page
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Codification worksheet - arm A1, rep 1</title>
<style>
  :root{{
    --bg:#fbfaf7; --ink:#1b1a17; --muted:#6b675f; --rule:#ddd8cd; --card:#fff;
    --fail:#a3271f; --fail-bg:#fbeceb; --exec:#1f6b3f; --exec-bg:#eaf4ee;
    --warn:#8a6100; --warn-bg:#fdf3dd; --hl:#ffe89a; --accent:#2a4d7a;
    --flag:#6d3a8f; --flag-bg:#f3ecf8;
  }}
  @media (prefers-color-scheme: dark){{
    :root:not([data-theme="light"]){{
      --bg:#151412; --ink:#eceae4; --muted:#a6a099; --rule:#34322d; --card:#1d1c19;
      --fail:#ff8a7d; --fail-bg:#2e1a18; --exec:#77d39b; --exec-bg:#152720;
      --warn:#e8bf6a; --warn-bg:#2b2313; --hl:#6a5410; --accent:#8fb6e8;
      --flag:#cda6e8; --flag-bg:#241a2c;
    }}
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);
    font:15px/1.55 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}}
  code,kbd,.mono{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.88em}}
  .wrap{{max-width:1180px;margin:0 auto;padding:0 22px}}
  header{{padding:26px 0 16px;border-bottom:1px solid var(--rule)}}
  h1{{margin:0 0 6px;font-size:1.55rem;letter-spacing:-.01em}}
  h2{{margin:34px 0 8px;font-size:1.15rem;border-bottom:1px solid var(--rule);padding-bottom:5px}}
  h3{{margin:0 0 4px;font-size:1.05rem}}
  h4{{margin:16px 0 4px;font-size:.85rem;letter-spacing:.05em;text-transform:uppercase;
     color:var(--muted);font-weight:600}}
  .sub{{color:var(--muted);margin:0}}
  .band{{background:var(--fail-bg);border:2px solid var(--fail);color:var(--fail);
    border-radius:8px;padding:14px 16px;margin:18px 0;font-size:.94rem}}
  .band b{{color:var(--fail)}}
  .band .k{{color:var(--fail);opacity:.85}}
  table{{width:100%;border-collapse:collapse;margin:8px 0}}
  th,td{{text-align:left;padding:7px 9px;border-bottom:1px solid var(--rule);
    vertical-align:top;font-size:.9rem}}
  thead th{{font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;
    color:var(--muted);font-weight:600}}
  table.meta th{{width:170px;font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;
    color:var(--muted);font-weight:600}}
  .item{{background:var(--card);border:1px solid var(--rule);border-radius:10px;
    padding:16px 18px;margin:18px 0}}
  .verdict{{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.72rem;
    letter-spacing:.05em;font-weight:700;font-family:ui-monospace,monospace}}
  .WILL_FAIL{{background:var(--fail-bg);color:var(--fail);border:1px solid var(--fail)}}
  .WILL_EXECUTE{{background:var(--exec-bg);color:var(--exec);border:1px solid var(--exec)}}
  .mini{{display:inline-block;padding:1px 6px;border-radius:4px;font-size:.68rem;
    font-family:ui-monospace,monospace;font-weight:700}}
  .mini.WILL_FAIL{{background:var(--fail-bg);color:var(--fail)}}
  .mini.WILL_EXECUTE{{background:var(--exec-bg);color:var(--exec)}}
  .lvl{{font-family:ui-monospace,monospace;font-size:.74rem;padding:1px 6px;
    border-radius:4px;border:1px solid var(--rule);color:var(--muted);white-space:nowrap}}
  .lvl.exact{{color:var(--exec);border-color:var(--exec)}}
  .lvl.none{{color:var(--fail);border-color:var(--fail)}}
  .lvl.loose{{color:var(--warn);border-color:var(--warn);background:var(--warn-bg)}}
  .res{{font-family:ui-monospace,monospace;font-size:.74rem;font-weight:700}}
  .res.yes{{color:var(--exec)}} .res.no{{color:var(--fail)}}
  .txt{{background:var(--bg);border:1px solid var(--rule);border-radius:8px;
    padding:12px 14px;white-space:pre-wrap;font-family:ui-monospace,monospace;
    font-size:.8rem;max-height:300px;overflow:auto;margin:6px 0 0}}
  mark{{background:var(--hl);color:inherit;padding:0 1px;border-radius:2px}}
  .absent{{color:var(--fail);font-weight:700;font-size:.75rem}}
  .ok{{color:var(--exec);font-size:.75rem}}
  .agree{{color:var(--exec);font-size:.72rem;margin-left:8px;font-weight:700}}
  .disagree{{color:var(--fail);font-size:.72rem;margin-left:8px;font-weight:700}}
  .k{{color:var(--muted);font-size:.8rem}}
  .q{{font-family:ui-monospace,monospace;font-size:.8rem}}
  .q:before{{content:'\\201C'}} .q:after{{content:'\\201D'}}
  .why{{font-size:.76rem;line-height:1.4}}
  .instr{{margin-top:3px;font-size:.76rem;line-height:1.4}}
  .sibs{{font-size:.74rem;line-height:1.7}}
  .num{{text-align:right;font-family:ui-monospace,monospace}}
  .pill{{font-size:.7rem;color:var(--muted);border:1px solid var(--rule);
    border-radius:999px;padding:1px 8px;margin-left:6px;font-family:ui-monospace,monospace}}
  .clause{{display:inline-block;font-size:.66rem;font-weight:700;letter-spacing:.05em;
    font-family:ui-monospace,monospace;color:var(--accent);border:1px solid var(--accent);
    border-radius:4px;padding:0 5px;margin-left:5px}}
  .clause-cell{{width:60px}}
  .flag{{display:inline-block;font-size:.66rem;font-weight:700;letter-spacing:.04em;
    font-family:ui-monospace,monospace;color:var(--flag);background:var(--flag-bg);
    border:1px solid var(--flag);border-radius:4px;padding:0 5px}}
  .routed{{background:var(--warn-bg);border-left:3px solid var(--warn);color:var(--ink);
    padding:9px 12px;margin:12px 0 0;font-size:.82rem;border-radius:0 6px 6px 0}}
  .routed b{{color:var(--warn)}}
  .scroll{{overflow-x:auto}}
  .hash{{font-size:.7rem;word-break:break-all;color:var(--muted)}}
  footer{{border-top:1px solid var(--rule);margin-top:38px;padding:18px 0 44px;
    color:var(--muted);font-size:.84rem}}
  footer b{{color:var(--ink)}}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>Codification worksheet</h1>
  <p class="sub">Federal Register amendatory instructions, executed against the
     point-in-time CFR text - one row per instruction, with the anchor, the
     normalisation level it resolved at, the designation state, and the siblings
     when it did not resolve.</p>
</div></header>

<div class="wrap">

  <div class="band">
    <b>NOT A FILING. NOT LEGAL ADVICE. NOT REVIEWED BY A QUALIFIED REVIEWER.</b><br>
    This worksheet is an <b>input to a licensed regulations drafter's judgement</b>.
    It does not file anything, does not amend anything, and takes no consequential
    action. <b>No output on this page has been reviewed by a qualified regulations
    drafter or by any other qualified reviewer</b> - not one row. The verdicts below
    are the measured output of an evaluation arm whose pre-registered success
    criterion was <b>NOT MET on all four clauses</b>, and which agrees with gold on
    <b>{agree} of {n}</b> items. Every unresolved case routes to the human-checkpoint
    queue at the foot of this page rather than being decided here.<br>
    <span class="k">Self-contained: no script, no network, no external font, no build
    step. Opens from a clean clone by double-clicking, with the network off.</span>
  </div>

  <h2>What this page is drawn from</h2>
  <table class="meta"><tbody>
    <tr><th>arm</th><td><code>{arm}</code>, rep {rep} - the advanced solution:
        <code>cfr_resolve</code> plus the v2 <code>SKILL.md</code></td></tr>
    <tr><th>model</th><td><code>{model}</code>, temperature 0.0</td></tr>
    <tr><th>eval set</th><td><code>data/evalset/items.jsonl</code> - n = {n},
        balanced by construction, frozen before any arm ran</td></tr>
    <tr><th>per-item output</th><td><code>docs/evidence/ch06-a1/A1-rep1-artifacts.jsonl</code>
        - committed, not regenerated here</td></tr>
    <tr><th>agreement with gold</th><td><b>{agree} / {n} = {accuracy}</b>
        <span class="k">- this is the published A1 primary accuracy</span></td></tr>
    <tr><th>routed to a human</th><td><b>{routed} of {n}</b> items
        <span class="k">- the queue is a section of this page, below</span></td></tr>
    <tr><th>instructions traced</th><td>{n_instructions} across all {n} items;
        {tool_calls} <code>cfr_resolve</code> calls; {tokens_in} input /
        {tokens_out} output tokens</td></tr>
  </tbody></table>

  <h2>Which items are shown, and why</h2>
  <p class="k">A worksheet showing all {n} items would be unreadable, and one showing a
     hand-picked few would be unfalsifiable. The rule below is deterministic, ties
     break on sorted <code>item_id</code>, and it is applied by
     <code>docs/evidence/ch12/build_worksheet.py</code> - the same script that writes
     this page. It selected <b>{n_selected} items</b>. The complete per-item output for
     all {n} is in the artifacts file named above; nothing is hidden by this page,
     only unrendered.</p>
  <table><tbody>{rule_rows}</tbody></table>

  <h2>Normalisation levels actually achieved, across all {n} items</h2>
  <p class="k">Hard rule 7: three declared levels, tried in order, and the level
     achieved is <b>reported</b>, never applied silently. Across
     {n_instructions} instructions:</p>
  <table>
    <thead><tr><th>level</th><th class="num">instructions</th><th>what it means</th></tr></thead>
    <tbody>{level_rows}</tbody>
  </table>
  <p class="k">The <code>whitespace-collapsed</code> row is <b>zero</b>, and it is
     printed as zero rather than omitted: on this corpus no anchor needed that level
     and none was helped by it. <code>none</code> is the majority because most
     instructions carry no quoted anchor at all - they name a designation, and the
     designation path answers them.</p>

  <h2>The items</h2>
{items}

  <h2>Human-checkpoint queue - {routed} of {n}</h2>
  <p class="k">These items are <b>not decided by the tool</b>. Each carries a verdict
     derived from its trace, and each is flagged for a drafter with the reason it was
     flagged. <b>C1</b>: the anchor path and the designation path disagree about an
     instruction. <b>C2</b>: both paths were asked and returned contradictory facts.
     <b>C3</b>: one designation is touched by two instructions, so the result depends
     on execution order - and the ordered-state ledger that would resolve it is a
     <b>declared, counted removal</b> (<code>CHANGELOG.md</code>, ruling R-01), so the
     system refuses rather than guesses.</p>
  <div class="scroll"><table>
    <thead><tr><th>item</th><th>emitted verdict</th><th>class</th><th>reason, verbatim from the artifact</th></tr></thead>
    <tbody>{queue_rows}</tbody>
  </table></div>

  <footer>
    <p><b>Provenance.</b> Every number on this page is read from committed artifacts
    and none is computed by a model at render time. The page is generated by
    <code>docs/evidence/ch12/build_worksheet.py</code> from exactly two inputs, both
    already in this repository:</p>
    <table><tbody>{digest_rows}</tbody></table>
    <p><b>Commit.</b> The A1 rep-1 artifacts were committed at
    <code>{artifact_commit}</code>; the eval set was frozen at
    <code>{evalset_commit}</code>. <b>Arm</b> <code>{arm}</code>, rep {rep}.
    <b>Model</b> <code>{model}</code> at temperature 0.0. The generator makes no
    network call, reads no clock and calls no model, so re-running it on an unchanged
    tree reproduces this file byte for byte -
    <code>tests/test_worksheet.py</code> asserts that, and asserts that this page
    references no external resource.</p>
    <p><b>What this page is not.</b> It is not a filing, not a legal opinion, and not
    a reviewed document. The arm that produced it missed gold on
    <b>{n} &minus; {agree}</b> items and those disagreements are shown, not filtered.
    Read it beside <code>README.md</code> section g, LIMITATIONS.</p>
  </footer>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(main())
