"""CH-03 RE-REVIEW round 2 - hunt for ANY residual label channel in the frozen text.

Goes beyond plan.md's three rules. Imports nothing from src/.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "data/raw/cfr"
LEAK = ("EDNOTE", "EFFDNOTP", "CITA", "EAR")
REPRINT = {"EDNOTE", "EFFDNOTP", "REVTXT"}


def parents_of(root):
    return {c: p for p in root.iter() for c in p}


def sectno(sec):
    el = sec.find("SECTNO")
    if el is None:
        return None
    t = "".join(el.itertext())
    m = re.search(r"§+\s*([0-9][^\s,;]*)", t) or re.search(r"([0-9]+\.[^\s,;]+)", t)
    return m.group(1).rstrip(".") if m else None


def eligible(root):
    par = parents_of(root)
    out = []
    for sec in root.iter("SECTION"):
        node, bad = sec, False
        while node in par:
            node = par[node]
            if node.tag in REPRINT:
                bad = True
                break
        if not bad:
            out.append(sec)
    return out


def main():
    items = [json.loads(l) for l in
             (REPO / "data/evalset/items.jsonl").read_text("utf-8").splitlines() if l.strip()]

    # ---- 1. case-insensitive and near-miss literals ----------------------------
    probes = ["could not be incorporated", "editorial note", "effective date note",
              "set forth as follows", "incorporat", "cannot be", "was not amended",
              "no amendment", "the amendment", "correcting amendment", "reserved",
              "note:", "nomenclature change", "redesignat", "amendment could"]
    print("case-INSENSITIVE literal probes over section_text, split by label:")
    for p in probes:
        c = Counter()
        for it in items:
            if p in it["section_text"].lower():
                c[it["label"]] += 1
        if c:
            print("   %-24s WILL_FAIL %2d   WILL_EXECUTE %2d" % (p, c["WILL_FAIL"],
                                                                 c["WILL_EXECUTE"]))

    # ---- 2. ANY FR citation, any format ----------------------------------------
    pats = {"NN FR NNNN": r"\b\d{1,3}\s+FR\s+\d{1,6}\b",
            "NN F.R. NNNN": r"\b\d{1,3}\s+F\.?\s?R\.?\s+\d{1,6}\b",
            "Fed. Reg.": r"Fed\.?\s*Reg\.?",
            "bracketed date credit": r"\[\d{1,3}\s+FR"}
    print("\nFR-citation shaped strings in section_text:")
    for name, pat in pats.items():
        hits = [i["item_id"] for i in items if re.search(pat, i["section_text"])]
        print("   %-22s %d %s" % (name, len(hits), hits[:5]))

    # ---- 3. does the note's own wording survive in the positive's text? ---------
    print("\nlongest shared word-run between note_text and section_text (positives):")
    worst = []
    for it in items:
        if it["label"] != "WILL_FAIL" or not it["note_text"]:
            continue
        nw = it["note_text"].split()
        sw = set()
        st = " " + " ".join(it["section_text"].split()) + " "
        best, bestrun = 0, ""
        for n in range(len(nw)):
            run = []
            for m in range(n, min(n + 25, len(nw))):
                run.append(nw[m])
                if " " + " ".join(run) + " " in st:
                    if len(run) > best:
                        best, bestrun = len(run), " ".join(run)
                else:
                    break
        worst.append((best, it["item_id"], bestrun))
    worst.sort(reverse=True)
    for b, iid, run in worst[:6]:
        print("   %2d words  %-26s %r" % (b, iid, run[:90]))

    # ---- 4. residual element names inside the frozen SECTION trees --------------
    print("\nresidual element-name census in the frozen sections, BY LABEL:")
    roots, census = {}, defaultdict(Counter)
    for it in items:
        p = RAW / it["volume"]
        if p not in roots:
            roots[p] = ET.parse(str(p)).getroot()
        sec = [s for s in eligible(roots[p]) if sectno(s) == it["section"]][0]
        import copy
        clone = copy.deepcopy(sec)
        while True:
            par = parents_of(clone)
            tgt = next((e for e in clone.iter() if e.tag in LEAK and e in par), None)
            if tgt is None:
                break
            par[tgt].remove(tgt)
        for el in clone.iter():
            census[el.tag][it["label"]] += 1
    for tag in sorted(census):
        f, e = census[tag]["WILL_FAIL"], census[tag]["WILL_EXECUTE"]
        flag = "  <-- one-sided" if (f == 0) != (e == 0) else ""
        print("   %-12s WILL_FAIL %4d   WILL_EXECUTE %4d%s" % (tag, f, e, flag))

    # ---- 5. one-sided METADATA fields in the frozen record ----------------------
    print("\none-sided METADATA in items.jsonl (a channel outside section_text):")
    for field in ("strip_counts.EDNOTE", "strip_counts.EFFDNOTP", "strip_counts.CITA",
                  "strip_counts.EAR", "volume_route"):
        c = defaultdict(Counter)
        for it in items:
            if field.startswith("strip_counts."):
                v = it["strip_counts"].get(field.split(".")[1], 0)
                v = "nonzero" if v else "zero"
            else:
                v = it[field]
            c[v][it["label"]] += 1
        for v, cc in sorted(c.items()):
            one = (cc["WILL_FAIL"] == 0) != (cc["WILL_EXECUTE"] == 0)
            print("   %-24s = %-16s WILL_FAIL %2d  WILL_EXECUTE %2d%s"
                  % (field, v, cc["WILL_FAIL"], cc["WILL_EXECUTE"],
                     "   <-- PERFECT ONE-SIDED INDICATOR" if one else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
