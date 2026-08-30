"""Does the CONTEXT.md-literal tokenisation change the EVAL SET, not just the number?

Builds the pairing on MY spec-literal attribution and diffs the pair set against the
frozen one. Also prints the 65 'genuinely different' attributions.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reimplement_context8 import (attribute, docs, by_doc)          # noqa: E402

REPO = Path(__file__).resolve().parents[3]
D = REPO / "data"

# my counts
mine_counts = {}
for frdoc in sorted(docs):
    rows = attribute(docs[frdoc], True, True)
    for r in rows:
        if r["section"]:
            mine_counts.setdefault(frdoc, {})
            mine_counts[frdoc][r["section"]] = mine_counts[frdoc].get(r["section"], 0) + 1

cits = json.loads((D / "amdpars/citations.json").read_text(encoding="utf-8"))
pool = sorted({(c["frdoc"], c["section"]) for c in cits.values()
               if c.get("status") == "resolved"})
dbd = {}
for f, s in pool:
    dbd.setdefault(f, set()).add(s)


def pair_up(counts):
    used, pairs, unm = {}, [], []
    for f, s in pool:
        doc = counts.get(f, {})
        own = doc.get(s)
        if own is None:
            unm.append((f, s, "no-attributed-instructions"))
            continue
        t = used.setdefault(f, set())
        cands = sorted(x for x, c in doc.items()
                       if x != s and x not in dbd[f] and c == own)
        free = [x for x in cands if x not in t]
        if not free:
            unm.append((f, s, "no-free" if cands else "no-match"))
            continue
        t.add(free[0])
        pairs.append((f, s, free[0], own))
    return pairs, unm


mine_pairs, mine_unm = pair_up(mine_counts)
frozen = [json.loads(l) for l in
          (D / "evalset/items.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
frozen_pairs = {}
for i in frozen:
    frozen_pairs.setdefault(i["frdoc"], {}).setdefault(i["role"], []).append(i["section"])

print("=" * 100)
print("PAIRING BUILT ON THE CONTEXT.md-LITERAL ATTRIBUTION")
print("=" * 100)
print(f"  pairs before PIT resolution, mine  : {len(mine_pairs)}")
print(f"  pairs before PIT resolution, theirs: 50   (committed diagnostic)")
mp = {(f, p): (n, c) for f, p, n, c in mine_pairs}

# compare against the 50 the shipped code produced (recomputed in recompute_ladder.py)
recs = [json.loads(l) for l in
        (D / "attribution-v11/amdpars_v11.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()]
their_counts = {}
for r in recs:
    s = r.get("section_v11")
    if s:
        their_counts.setdefault(r["frdoc"], {})
        their_counts[r["frdoc"]][s] = their_counts[r["frdoc"]].get(s, 0) + 1
their_pairs, _ = pair_up(their_counts)
tp = {(f, p): (n, c) for f, p, n, c in their_pairs}

only_mine = sorted(set(mp) - set(tp))
only_theirs = sorted(set(tp) - set(mp))
both_diff_neg = sorted(k for k in set(mp) & set(tp) if mp[k] != tp[k])
print(f"  positives paired under MINE only   : {len(only_mine)}")
print(f"  positives paired under THEIRS only : {len(only_theirs)}")
print(f"  same positive, different negative or count: {len(both_diff_neg)}")
for k in only_theirs[:20]:
    print(f"     theirs-only  {k}  neg={tp[k]}")
for k in only_mine[:20]:
    print(f"     mine-only    {k}  neg={mp[k]}")
for k in both_diff_neg[:20]:
    print(f"     differs      {k}  mine={mp[k]}  theirs={tp[k]}")

print()
print("=" * 100)
print("THE 65 'GENUINELY DIFFERENT' ATTRIBUTIONS")
print("=" * 100)
n = 0
for frdoc in sorted(docs):
    rows = attribute(docs[frdoc], True, True)
    th = by_doc.get(frdoc, [])
    if len(rows) != len(th):
        continue
    for m, t in zip(rows, th):
        a, b = m["section"], t["section_v11"]
        if a == b:
            continue
        if (a and b and b.startswith(a)) or a is None:
            continue
        n += 1
        if n <= 30:
            print(f"  {frdoc:<14} mine={str(a):<16} theirs={str(b):<16} | {t['text'][:100]}")
print(f"  total: {n}")
