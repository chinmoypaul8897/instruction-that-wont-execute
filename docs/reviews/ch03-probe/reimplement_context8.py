"""ADVERSARIAL REVIEW of CH-03 - CONTEXT.md section 8's v1.1 attribution algorithm,
reimplemented FROM THE SPEC TEXT ALONE.

Imports nothing from the project. The only project artefact read is
`data/amdpars/documents.json`, and only for the LIST of (frdoc -> issue file); every
AMDPAR, every <REGTEXT> PART and every regex is re-derived here.

Spec text implemented, verbatim from CONTEXT.md section 8:

  1. Iterate <AMDPAR> elements in document order.
  2. Maintain current_section, initially null. Reset current_section to null at every
     <REGTEXT> part boundary.
  3. If the element names a section in its own text, set current_section to it:
       sign form  `\\S\\s*[\\d.]+[a-z]?`   (the section sign followed by the number)
       word form  `Section`/`Sections` + the number, matched CASE-SENSITIVELY
  4. Otherwise attribute to current_section; if null the element is unattributable.
  5. Parse into (operation, anchor, designation): operation is one of
     revise/add/remove/redesignate/amend; anchor is the quoted text if present;
     designation is the paragraph path such as (b)(4)(i)(A).

  completeness = attributed AND parsed into at least one complete
                 (operation, anchor OR designation) triple / total AMDPAR elements
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
D = REPO / "data"

# ---- the spec's own regexes, transcribed character for character -----------------
SPEC_NUM = r"[\d.]+[a-z]?"
SIGN = re.compile(r"§\s*(" + SPEC_NUM + r")")
WORD_CS = re.compile(r"\bSections?\s+(" + SPEC_NUM + r")")

OPS = [re.compile(r"\brevis(?:e|es|ed|ing|ion)\b", re.I),
       re.compile(r"\badd(?:s|ed|ing)?\b", re.I),
       re.compile(r"\bremov(?:e|es|ed|ing|al)\b", re.I),
       re.compile(r"\bredesignat(?:e|es|ed|ing|ion)\b", re.I),
       re.compile(r"\bamend(?:s|ed|ing|ment|ments|atory)?\b", re.I)]
DESIG = re.compile(r"(?:\([A-Za-z0-9]{1,4}\))+")
WS = re.compile(r"\s+")


def collapse(s):
    return WS.sub(" ", s).strip()


def quoted_spans(text):
    """Anchors = quoted text. Both the curly pair and the straight pair."""
    out = []
    for lq, rq in (("“", "”"), ('"', '"')):
        i = 0
        while True:
            a = text.find(lq, i)
            if a < 0:
                break
            b = text.find(rq, a + 1)
            if b < 0:
                out.append(text[a + 1:])
                break
            out.append(text[a + 1:b])
            i = b + 1
    return out


def dequote(text):
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in ("“", '"'):
            close = "”" if ch == "“" else '"'
            j = text.find(close, i + 1)
            out.append(" ")
            if j < 0:
                break
            i = j + 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def parse(text, read_from_dequoted):
    src = dequote(text) if read_from_dequoted else text
    anchors = quoted_spans(text)
    op = any(rx.search(src) for rx in OPS)
    desig = DESIG.findall(src)
    return {"operation": op, "anchor": bool(anchors), "designation": bool(desig),
            "parsed": bool(op) and (bool(anchors) or bool(desig))}


def named_sections(text, read_from_dequoted):
    src = dequote(text) if read_from_dequoted else text
    hits = [(m.start(), m.group(1)) for m in SIGN.finditer(src)]
    hits += [(m.start(), m.group(1)) for m in WORD_CS.finditer(src)]
    hits.sort()
    return [h[1] for h in hits]


# ---- read the raw FR issues myself ------------------------------------------------
def read_document_amdpars(path, wanted):
    """{frdoc -> [(amdpar text, regtext PART), ...]} in document order."""
    out = {}
    stack, regtext, cur = [], [], None
    FRDOC_NUM = re.compile(r"FR Doc\.?\s*(\S+?)\s+Filed", re.I)
    for ev, el in ET.iterparse(str(path), events=("start", "end")):
        if ev == "start":
            if el.tag == "RULE":
                stack.append({"frdoc": None, "rows": []})
            elif el.tag == "REGTEXT":
                regtext.append(el.get("PART"))
        else:
            if el.tag == "AMDPAR" and stack:
                stack[-1]["rows"].append(
                    (collapse("".join(el.itertext())), regtext[-1] if regtext else None))
                el.clear()
            elif el.tag == "REGTEXT":
                if regtext:
                    regtext.pop()
            elif el.tag == "FRDOC" and stack:
                m = FRDOC_NUM.search("".join(el.itertext()))
                if m:
                    stack[-1]["frdoc"] = m.group(1).rstrip(".,;")
            elif el.tag == "RULE" and stack:
                fr = stack.pop()
                if fr["frdoc"] in wanted:
                    out[fr["frdoc"]] = fr["rows"]
    return out


def attribute(rows, part_reset, read_from_dequoted):
    recs = []
    cur, prev_part = None, None
    for i, (text, part) in enumerate(rows):
        if part_reset and i > 0 and part != prev_part:
            cur = None
        prev_part = part
        named = named_sections(text, read_from_dequoted)
        if named:
            cur = named[0]
        p = parse(text, read_from_dequoted)
        recs.append({"section": cur, "attributed": cur is not None,
                     "parsed": p["parsed"],
                     "complete": cur is not None and p["parsed"]})
    return recs


def totals(recs):
    t = len(recs)
    a = sum(1 for r in recs if r["attributed"])
    c = sum(1 for r in recs if r["complete"])
    p = sum(1 for r in recs if r["parsed"])
    return {"total": t, "attributed": a, "complete": c, "parsed": p,
            "completeness": c / t if t else 0.0,
            "attribution_rate": a / t if t else 0.0,
            "parse_rate": p / t if t else 0.0}


meta = json.loads((D / "amdpars/documents.json").read_text(encoding="utf-8"))
by_file = {}
for frdoc, d in meta.items():
    by_file.setdefault(d["issue_file"], set()).add(frdoc)

docs = {}
for f in sorted(by_file):
    docs.update(read_document_amdpars(D / "raw/fr" / f, by_file[f]))

print(f"documents in data/amdpars/documents.json : {len(meta)}")
print(f"documents I re-read from data/raw/fr/    : {len(docs)}")
missing = sorted(set(meta) - set(docs))
if missing:
    print("  MISSING:", missing)

committed = json.loads((D / "attribution-v11/completeness_v11.json").read_text(encoding="utf-8"))
cg = committed["global"]["v11"]

print()
print("=" * 100)
print("GLOBAL, my reimplementation from CONTEXT.md section 8 alone")
print("=" * 100)
variants = {
    "spec-regex, reset on PART change, fields read from DE-QUOTED text": (True, True),
    "spec-regex, reset on PART change, fields read from RAW text": (True, False),
    "spec-regex, NO part reset, DE-QUOTED": (False, True),
}
mine = {}
for label, (reset, deq) in variants.items():
    flat = []
    for frdoc in sorted(docs):
        flat.extend(attribute(docs[frdoc], reset, deq))
    mine[label] = totals(flat)
    t = mine[label]
    print(f"  {label}")
    print(f"      total={t['total']}  attributed={t['attributed']} ({t['attribution_rate']:.4f})"
          f"  parsed={t['parsed']} ({t['parse_rate']:.4f})"
          f"  complete={t['complete']}  completeness={t['completeness']:.4f}")

print()
print("  COMMITTED data/attribution-v11/completeness_v11.json 'v11':")
print(f"      total={cg['total']}  attributed={cg['attributed']} ({cg['attribution_rate']:.4f})"
      f"  parsed={cg['parsed']} ({cg['parse_rate']:.4f})"
      f"  complete={cg['complete']}  completeness={cg['completeness']:.4f}")

# ---- per-element diff on the closest variant --------------------------------------
print()
print("=" * 100)
print("PER-ELEMENT ATTRIBUTION DIFF  (my spec-literal v11 vs the committed section_v11)")
print("=" * 100)
recs = [json.loads(l) for l in
        (D / "attribution-v11/amdpars_v11.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()]
by_doc = {}
for r in recs:
    by_doc.setdefault(r["frdoc"], []).append(r)
for k in by_doc:
    by_doc[k].sort(key=lambda r: r["ordinal"])

same = diff = 0
examples = []
for frdoc in sorted(docs):
    mine_rows = attribute(docs[frdoc], True, True)
    theirs = by_doc.get(frdoc, [])
    if len(mine_rows) != len(theirs):
        print(f"  !! {frdoc}: element count {len(mine_rows)} vs {len(theirs)}")
        continue
    for i, (m, t) in enumerate(zip(mine_rows, theirs)):
        if m["section"] == t["section_v11"]:
            same += 1
        else:
            diff += 1
            if len(examples) < 25:
                examples.append((frdoc, i + 1, m["section"], t["section_v11"],
                                 t["text"][:110]))
print(f"  elements agreeing on the attributed section : {same}")
print(f"  elements disagreeing                        : {diff}"
      f"  ({diff / (same + diff):.4%})")
print()
for e in examples:
    print(f"    {e[0]} #{e[1]:<4} mine={str(e[2]):<14} theirs={str(e[3]):<14} | {e[4]}")

# where the section-token regex is the cause
print()
print("=" * 100)
print("IS THE DIFFERENCE THE SECTION-NUMBER TOKEN?  CONTEXT.md spells the sign form")
print("`\\S\\s*[\\d.]+[a-z]?`; the code uses a richer token that keeps 1.1400Z2(b)-1 whole.")
print("=" * 100)
from collections import Counter
cause = Counter()
for e_frdoc in sorted(docs):
    mine_rows = attribute(docs[e_frdoc], True, True)
    theirs = by_doc.get(e_frdoc, [])
    if len(mine_rows) != len(theirs):
        continue
    for m, t in zip(mine_rows, theirs):
        if m["section"] == t["section_v11"]:
            continue
        a, b = m["section"], t["section_v11"]
        if a and b and b.startswith(a):
            cause["mine is a PREFIX of theirs (spec regex truncates the token)"] += 1
        elif a is None:
            cause["mine null, theirs attributed"] += 1
        elif b is None:
            cause["mine attributed, theirs null"] += 1
        else:
            cause["genuinely different sections"] += 1
for k, v in cause.most_common():
    print(f"  {v:>6}  {k}")
