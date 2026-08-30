"""ADVERSARIAL REVIEW of CH-03 - hunt for ANY residual label-bearing material in the
frozen items, beyond the four literals and the four element names the spec lists.

(1) census every element tag that survives into the frozen text's source <SECTION>,
(2) grep the frozen text for note-shaped and rule-shaped material, case-insensitively,
(3) check dates near the publication date of the rule under test.
"""
import copy
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
D = REPO / "data"
LEAK = ("EDNOTE", "EFFDNOTP", "CITA", "EAR")
REPRINT = ("EDNOTE", "EFFDNOTP", "REVTXT")
SECTOK = re.compile(r"\d+[A-Za-z]?\.[0-9A-Za-z][0-9A-Za-z.\-]*")


def parents_of(root):
    return {c: p for p in root.iter() for c in p}


def elig(root):
    P = parents_of(root)
    out = []
    for s in root.iter("SECTION"):
        n, bad = s, False
        while n in P:
            n = P[n]
            if n.tag in REPRINT:
                bad = True
                break
        if not bad:
            out.append(s)
    return out


def sn(s):
    e = s.find("SECTNO")
    if e is None:
        return None
    m = SECTOK.search(" ".join("".join(e.itertext()).split()))
    return m.group(0).rstrip(".") if m else None


def strip(sec):
    clone = copy.deepcopy(sec)
    while True:
        P = parents_of(clone)
        t = None
        for el in clone.iter():
            if el.tag in LEAK and el in P:
                t = el
                break
        if t is None:
            break
        P[t].remove(t)
    return clone


items = [json.loads(l) for l in
         (D / "evalset/items.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

cache = {}
surviving_tags = Counter()
tag_examples = defaultdict(list)
for it in items:
    p = D / "raw/cfr" / it["volume"]
    if p not in cache:
        cache[p] = ET.parse(str(p)).getroot()
    hits = [s for s in elig(cache[p]) if sn(s) == it["section"]]
    if len(hits) != 1:
        print("!!", it["item_id"], len(hits))
        continue
    st = strip(hits[0])
    for el in st.iter():
        surviving_tags[el.tag] += 1
        if len(tag_examples[el.tag]) < 2:
            tag_examples[el.tag].append(
                (it["item_id"], " ".join("".join(el.itertext()).split())[:150]))

print("=" * 100)
print("1. ELEMENT TAGS SURVIVING INTO THE FROZEN SECTIONS (after the four strips)")
print("=" * 100)
for t, c in surviving_tags.most_common():
    flag = "  <-- inspect" if t not in (
        "SECTION", "SECTNO", "SUBJECT", "P", "FP", "HD", "E", "EXTRACT", "ENT",
        "CHED", "GPOTABLE", "ROW", "TTITLE", "BOXHD", "SU", "PRTPAGE", "TDESC",
        "STARS", "IMG", "TNOTE", "GID", "CHED", "T", "GPH") else ""
    print(f"  {t:<16}{c:>8}{flag}")

print()
print("  examples for the flagged tags:")
for t in surviving_tags:
    if t in ("NOTE", "SECAUTH", "AUTH", "SOURCE", "EFFDNOT", "EDNOTE", "CITA",
             "EAR", "EFFDNOTP", "APPRO", "CROSSREF", "NOTECOL", "FTNT"):
        for ex in tag_examples[t]:
            print(f"    <{t}> {ex[0]}: {ex[1]}")

print()
print("=" * 100)
print("2. NOTE-SHAPED / RULE-SHAPED SUBSTRINGS IN THE FROZEN TEXT")
print("=" * 100)
PATTERNS = [
    ("could not be incorporated", re.compile(r"could not be incorporated", re.I)),
    ("editorial note (any case)", re.compile(r"editorial\s+note", re.I)),
    ("effective date note (any case)", re.compile(r"effective\s+date\s+note", re.I)),
    ("set forth as follows (any case)", re.compile(r"set\s+forth\s+as\s+follows", re.I)),
    ("FR citation NN FR NNNN", re.compile(r"\b\d{1,3}\s+FR\s+\d{1,6}\b")),
    ("'Nt.' editorial amendment record", re.compile(r"\bNt\.")),
    ("bare 'Note:' heading", re.compile(r"(?m)(^|\n)\s*Notes?:")),
    ("'Source:' credit", re.compile(r"(?m)(^|\n)\s*Source:", re.I)),
    ("'Cross Reference'", re.compile(r"cross\s+reference", re.I)),
    ("'was amended' / 'is amended'", re.compile(r"\b(?:was|is|were|are)\s+amended\b", re.I)),
    ("'for the convenience of the user'", re.compile(r"convenience of the user", re.I)),
    ("'incorporat' anywhere", re.compile(r"incorporat", re.I)),
    ("'delayed' / 'stayed' / 'suspended'", re.compile(r"\b(delayed|stayed|suspended)\b", re.I)),
    ("'the following amendment'", re.compile(r"following amendment", re.I)),
    ("'[Reserved]'", re.compile(r"\[Reserved\]", re.I)),
    ("'Redesignated at'", re.compile(r"[Rr]edesignated at")),
    ("'Editorially' ", re.compile(r"editorial", re.I)),
    ("'amendment could not'", re.compile(r"amendment could not", re.I)),
    ("'text is set forth'", re.compile(r"text is set forth", re.I)),
    ("'At NN FR' pattern", re.compile(r"\bAt\s+\d{1,3}\s+FR\b")),
]
for name, rx in PATTERNS:
    hits = [(i["item_id"], i["label"]) for i in items
            if rx.search(" ".join(i["section_text"].split()))]
    pos = sum(1 for _, l in hits if l == "WILL_FAIL")
    neg = len(hits) - pos
    mark = "" if not hits else ("   <-- PRESENT" if not hits else "")
    print(f"  {name:<42} {len(hits):>3} items  (+{pos} / -{neg}){mark}")
    for h in hits[:6]:
        print(f"        {h[0]}  {h[1]}")

print()
print("=" * 100)
print("3. DOES ANY FROZEN TEXT MENTION A DATE AT OR AFTER ITS RULE'S PUBLICATION DATE?")
print("=" * 100)
MON = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"])}
DATE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|June|July|Aug|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2}),\s*(\d{4})\b")
late = []
for i in items:
    pub = i["publication_date"]
    for m in DATE.finditer(" ".join(i["section_text"].split())):
        y, mo, d = int(m.group(3)), MON[m.group(1)], int(m.group(2))
        iso = f"{y:04d}-{mo:02d}-{d:02d}"
        if iso >= pub:
            late.append((i["item_id"], i["label"], iso, pub, m.group(0)))
            break
print(f"  items quoting a date on or after their own rule's publication date: {len(late)}")
for l in late[:20]:
    print(f"    {l[0]:<28} {l[1]:<12} date={l[2]} pub={l[3]}  ({l[4]})")
