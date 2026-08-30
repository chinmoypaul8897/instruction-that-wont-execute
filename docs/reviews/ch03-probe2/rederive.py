"""CH-03 RE-REVIEW round 2 - re-derive every load-bearing number from the raw bytes.

Imports NOTHING from src/. Everything below is reimplemented from CONTEXT.md section 8
and plan.md's CH-03 card:

  * the four leakage elements EDNOTE / EFFDNOTP / CITA / EAR, stripped and counted;
  * the three-rule leakage test (element / own FR citation / four literals);
  * eligibility - a <SECTION> under an EDNOTE, EFFDNOTP or REVTXT ancestor is a
    reprint of the pending amendment and must never be selected;
  * per-item strip counts, corpus totals, and the count of items whose UNSTRIPPED
    text would have leaked.

Run:  python docs/reviews/ch03-probe2/rederive.py
"""
from __future__ import annotations

import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ITEMS = REPO / "data/evalset/items.jsonl"
RAW = REPO / "data/raw/cfr"

LEAK = ("EDNOTE", "EFFDNOTP", "CITA", "EAR")
REPRINT_ANCESTORS = {"EDNOTE", "EFFDNOTP", "REVTXT"}
LITERALS = ("could not be incorporated", "Editorial Note", "Effective Date Note",
            "set forth as follows")


def parents_of(root):
    return {c: p for p in root.iter() for c in p}


def sectno(sec):
    el = sec.find("SECTNO")
    if el is None:
        return None
    t = "".join(el.itertext())
    m = re.search(r"§+\s*([0-9][^\s,;]*)", t)
    if not m:
        m = re.search(r"([0-9]+\.[^\s,;]+)", t)
    return m.group(1).rstrip(".") if m else None


def eligible(root):
    par = parents_of(root)
    out = []
    for sec in root.iter("SECTION"):
        node, bad = sec, False
        while node in par:
            node = par[node]
            if node.tag in REPRINT_ANCESTORS:
                bad = True
                break
        if not bad:
            out.append(sec)
    return out


def strip(sec):
    clone = copy.deepcopy(sec)
    counts = Counter()
    while True:
        par = parents_of(clone)
        target = None
        for el in clone.iter():
            if el.tag in LEAK and el in par:
                target = el
                break
        if target is None:
            break
        for inner in target.iter():
            if inner.tag in LEAK:
                counts[inner.tag] += 1
        par[target].remove(target)
    return clone, counts


def text_of(el):
    return " ".join("".join(el.itertext()).split())


def violations(text, own_citation):
    v = []
    for tag in LEAK:
        if "<" + tag in text:
            v.append(("a", tag))
    if own_citation and own_citation in text:
        v.append(("b", own_citation))
    norm = " ".join(text.split())
    for lit in LITERALS:
        if lit in norm:
            v.append(("c", lit))
    return v


def main():
    items = [json.loads(l) for l in ITEMS.read_text("utf-8").splitlines() if l.strip()]
    print("frozen items: %d   pairs: %d" % (len(items), len(items) // 2))

    roots = {}
    totals = Counter()
    leaked_unstripped = 0
    mismatch = []
    ambiguous = []
    text_mismatch = 0
    for it in items:
        path = RAW / it["volume"]
        if not path.exists():
            print("  MISSING RAW VOLUME %s - cannot re-derive %s" % (it["volume"], it["item_id"]))
            continue
        if path not in roots:
            roots[path] = ET.parse(str(path)).getroot()
        root = roots[path]
        hits = [s for s in eligible(root) if sectno(s) == it["section"]]
        if len(hits) != 1:
            ambiguous.append((it["item_id"], len(hits)))
        if not hits:
            mismatch.append((it["item_id"], "NOT FOUND in the stated volume"))
            continue
        sec = hits[0]
        raw_text = text_of(sec)
        stripped_el, counts = strip(sec)
        st_text = text_of(stripped_el)
        for t in LEAK:
            totals[t] += counts[t]
        got = {t: counts[t] for t in LEAK}
        want = {t: it["strip_counts"].get(t, 0) for t in LEAK}
        if got != want:
            mismatch.append((it["item_id"], "strip counts %s != committed %s" % (got, want)))
        if violations(raw_text, it["fr_citation"]):
            leaked_unstripped += 1
        v = violations(st_text, it["fr_citation"])
        if v:
            mismatch.append((it["item_id"], "LEAKS AFTER STRIP: %s" % v))
        # the frozen text is whitespace-normalised differently; compare token streams
        if "".join(st_text.split()) != "".join(it["section_text"].split()):
            text_mismatch += 1

    print("\nRE-DERIVED strip counts over the frozen corpus:")
    for t in LEAK:
        print("   %-9s %d   (committed %s)" % (t, totals[t], "see leakage.json"))
    print("   total     %d" % sum(totals.values()))
    print("\nitems whose UNSTRIPPED text would have leaked: %d / %d"
          % (leaked_unstripped, len(items)))
    print("sections resolving to != 1 eligible <SECTION>: %d %s"
          % (len(ambiguous), ambiguous[:10]))
    print("frozen section_text differing from my own strip (token stream): %d"
          % text_mismatch)
    print("\nMISMATCHES: %d" % len(mismatch))
    for m in mismatch:
        print("   ", m)

    committed = json.loads((REPO / "data/evalset/leakage.json").read_text("utf-8"))
    print("\ncommitted strip_counts_over_the_frozen_corpus:",
          committed["strip_counts_over_the_frozen_corpus"])
    print("committed items_whose_UNSTRIPPED_text_would_have_leaked:",
          committed["items_whose_UNSTRIPPED_text_would_have_leaked"])
    print("committed items_total:", committed["items_total"])

    # ---- exact instruction-count matching, re-derived from the frozen file -------
    from collections import defaultdict
    bad = []
    byd = defaultdict(list)
    for it in items:
        byd[it["frdoc"]].append(it)
    for f, grp in byd.items():
        pos = sorted(i["instruction_count"] for i in grp if i["label"] == "WILL_FAIL")
        neg = sorted(i["instruction_count"] for i in grp if i["label"] == "WILL_EXECUTE")
        if pos != neg:
            bad.append((f, pos, neg))
        for i in grp:
            if len(i["instructions"]) != i["instruction_count"]:
                bad.append((i["item_id"], "instructions %d != count %d"
                            % (len(i["instructions"]), i["instruction_count"])))
    print("\nEXACT INSTRUCTION-COUNT MATCH violations: %d %s" % (len(bad), bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
