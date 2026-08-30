"""ADVERSARIAL REVIEW of CH-03 - independent re-derivation of every load-bearing number.

Imports NOTHING from src/. Reads only:
    data/amdpars/citations.json           (CH-01/02 pool, read-only)
    data/attribution-v11/amdpars_v11.jsonl (the attribution the eval set was built on)
    data/attribution-v11/completeness_v11.json
    data/evalset/items.jsonl
    data/raw/cfr/*.xml                    (the annual editions)

Recomputes:
    pool size, instruction counts, the pairing, every rung of the exclusion ladder,
    per-element leakage strip counts, would-have-leaked count,
and diffs them against the committed artefacts.
"""
import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
D = REPO / "data"

FAIL = []
def check(name, mine, theirs):
    ok = mine == theirs
    print(f"  {'OK  ' if ok else 'DIFF'}  {name:<52} mine={mine!r:<28} committed={theirs!r}")
    if not ok:
        FAIL.append(name)


def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def jlload(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


# ---------------------------------------------------------------- 1. the pool
cits = jload(D / "amdpars/citations.json")
resolved = [c for c in cits.values() if c.get("status") == "resolved"]
pool_pairs = sorted({(c["frdoc"], c["section"]) for c in resolved})
print("=" * 100)
print("1. THE POOL")
print("=" * 100)
print(f"  citations.json entries                  : {len(cits)}")
print(f"  status == resolved                      : {len(resolved)}")
print(f"  distinct (frdoc, section)               : {len(pool_pairs)}")
ladder_c = jload(D / "evalset/exclusion_ladder.json")
rungs_c = ladder_c["ladder"]["rungs"]
check("ladder top = pool-citations-resolved", len(pool_pairs), rungs_c["pool-citations-resolved"]["items"])

# ---------------------------------------------------------------- 2. instruction counts
recs = jlload(D / "attribution-v11/amdpars_v11.jsonl")
counts = {}
for r in recs:
    s = r.get("section_v11")
    if s:
        counts.setdefault(r["frdoc"], {})
        counts[r["frdoc"]][s] = counts[r["frdoc"]].get(s, 0) + 1
print(f"  amdpars_v11.jsonl records               : {len(recs)}")
print(f"  documents with >=1 attributed element   : {len(counts)}")

# ---------------------------------------------------------------- 3. the pairing
# Declared rule (pre-registration section 3): negative = sibling in the SAME FR doc,
# EXACT same instruction count, not a defect section, not already used; where several
# match take the first in sorted order; positives processed in sorted order.
defect_by_doc = {}
for f, s in pool_pairs:
    defect_by_doc.setdefault(f, set()).add(s)

pairs, unmatched = [], []
used = {}
for frdoc, section in pool_pairs:
    doc = counts.get(frdoc, {})
    own = doc.get(section)
    if own is None:
        unmatched.append((frdoc, section, "positive-has-no-attributed-instructions"))
        continue
    taken = used.setdefault(frdoc, set())
    cands = sorted(s for s, c in doc.items()
                   if s != section and s not in defect_by_doc[frdoc] and c == own)
    free = [s for s in cands if s not in taken]
    if not free:
        unmatched.append((frdoc, section,
                          "no-free-count-matched-sibling" if cands else "no-count-matched-sibling"))
        continue
    taken.add(free[0])
    pairs.append((frdoc, section, free[0], own))

print()
print("=" * 100)
print("2. THE PAIRING (my own implementation of the declared rule)")
print("=" * 100)
print(f"  pairs after count-matching              : {len(pairs)}")
print(f"  unmatched                               : {len(unmatched)}")
from collections import Counter
uc = Counter(u[2] for u in unmatched)
for k in ("positive-has-no-attributed-instructions", "no-count-matched-sibling",
          "no-free-count-matched-sibling"):
    check(f"rung {k}", uc.get(k, 0), rungs_c[k]["positives"])
check("pairs before PIT resolution (= diagnostic 'pairs_without_any_completeness_floor')",
      len(pairs), ladder_c["diagnostics_never_used_as_the_eval_set"]["pairs_without_any_completeness_floor"])

# tolerance-1 diagnostic
pairs_t1 = []
used1 = {}
for frdoc, section in pool_pairs:
    doc = counts.get(frdoc, {})
    own = doc.get(section)
    if own is None:
        continue
    taken = used1.setdefault(frdoc, set())
    free = sorted(s for s, c in doc.items()
                  if s != section and s not in defect_by_doc[frdoc]
                  and s not in taken and abs(c - own) <= 1)
    if free:
        taken.add(free[0])
        pairs_t1.append((frdoc, section, free[0]))
check("diagnostic pairs_at_tolerance_1", len(pairs_t1),
      ladder_c["diagnostics_never_used_as_the_eval_set"]["pairs_at_tolerance_1"])

# 0.90 reference floor diagnostic
comp = jload(D / "attribution-v11/completeness_v11.json")
per_doc = comp["per_document"]
ref_ok = {f for f, c in per_doc.items() if c["v11"]["completeness"] >= 0.90}
pairs_ref = []
usedr = {}
for frdoc, section in pool_pairs:
    if frdoc not in ref_ok:
        continue
    doc = counts.get(frdoc, {})
    own = doc.get(section)
    if own is None:
        continue
    taken = usedr.setdefault(frdoc, set())
    free = sorted(s for s, c in doc.items()
                  if s != section and s not in defect_by_doc[frdoc]
                  and s not in taken and c == own)
    if free:
        taken.add(free[0])
        pairs_ref.append((frdoc, section, free[0]))
check("documents at completeness >= 0.90", len(ref_ok),
      rungs_c["document-completeness-below-floor"]["detail"][0]["reference_floor_0_90_would_keep_documents"])
check("positives in those documents", sum(1 for f, _ in pool_pairs if f in ref_ok),
      rungs_c["document-completeness-below-floor"]["detail"][0]["reference_floor_0_90_would_keep_positives"])
check("diagnostic pairs_under_the_0_90_reference_floor", len(pairs_ref),
      ladder_c["diagnostics_never_used_as_the_eval_set"]["pairs_under_the_0_90_reference_floor"])

# ---------------------------------------------------------------- 4. the strips, my own
LEAK = ("EDNOTE", "EFFDNOTP", "CITA", "EAR")
REPRINT = ("EDNOTE", "EFFDNOTP", "REVTXT")
LITERALS = ("could not be incorporated", "Editorial Note", "Effective Date Note",
            "set forth as follows")
SECTOK = re.compile(r"\d+[A-Za-z]?\.[0-9A-Za-z][0-9A-Za-z.\-]*")


def parents_of(root):
    return {c: p for p in root.iter() for c in p}


def my_eligible(root):
    par = parents_of(root)
    out = []
    for sec in root.iter("SECTION"):
        n, bad = sec, False
        while n in par:
            n = par[n]
            if n.tag in REPRINT:
                bad = True
                break
        if not bad:
            out.append(sec)
    return out


def my_sectno(sec):
    el = sec.find("SECTNO")
    if el is None:
        return None
    raw = " ".join("".join(el.itertext()).split())
    m = SECTOK.search(raw)
    return m.group(0).rstrip(".") if m else None


def my_strip(sec):
    clone = copy.deepcopy(sec)
    counts = {t: 0 for t in LEAK}
    while True:
        par = parents_of(clone)
        tgt = None
        for el in clone.iter():
            if el.tag in LEAK and el in par:
                tgt = el
                break
        if tgt is None:
            break
        for inner in tgt.iter():
            if inner.tag in LEAK:
                counts[inner.tag] += 1
        par[tgt].remove(tgt)
    counts["total"] = sum(counts[t] for t in LEAK)
    return clone, counts


BLOCK = ("SECTNO", "SUBJECT", "P", "FP", "HD", "EXTRACT", "ENT", "CHED")


def my_text(sec):
    blocks = []

    def walk(el):
        if el.tag in BLOCK:
            t = " ".join("".join(el.itertext()).split())
            if t:
                blocks.append(t)
            return
        if el.text and el.text.strip():
            blocks.append(" ".join(el.text.split()))
        for c in el:
            walk(c)
            if c.tail and c.tail.strip():
                blocks.append(" ".join(c.tail.split()))
    walk(sec)
    return "\n".join(blocks)


def my_violations(text, cit):
    out = []
    for t in LEAK:
        if f"<{t}" in text or f"</{t}>" in text:
            out.append(("a", t))
    flat = " ".join(text.split())
    if cit and " ".join(cit.split()) in flat:
        out.append(("b", cit))
    for lit in LITERALS:
        if lit in flat:
            out.append(("c", lit))
    return out


items = jlload(D / "evalset/items.jsonl")
print()
print("=" * 100)
print("3. THE LEAKAGE STRIPS - recomputed from data/raw/cfr/ by my own reader")
print("=" * 100)
tot = {t: 0 for t in LEAK}
tot["total"] = 0
would = 0
mismatched_text = []
mismatched_counts = []
rootcache = {}
for it in items:
    vp = D / "raw/cfr" / it["volume"]
    if vp not in rootcache:
        rootcache[vp] = ET.parse(str(vp)).getroot()
    root = rootcache[vp]
    hits = [s for s in my_eligible(root) if my_sectno(s) == it["section"]]
    if len(hits) != 1:
        print(f"  !! {it['item_id']}: {len(hits)} eligible candidates in {it['volume']}")
        continue
    sec = hits[0]
    raw = my_text(sec)
    stripped_el, c = my_strip(sec)
    txt = my_text(stripped_el)
    for t in LEAK:
        tot[t] += c[t]
    tot["total"] += c["total"]
    if c != it["strip_counts"]:
        mismatched_counts.append((it["item_id"], c, it["strip_counts"]))
    if txt != it["section_text"]:
        mismatched_text.append(it["item_id"])
    if my_violations(raw, it["fr_citation"]):
        would += 1

leak_c = jload(D / "evalset/leakage.json")
for t in LEAK + ("total",):
    check(f"strip total {t}", tot[t], leak_c["strip_counts_over_the_frozen_corpus"][t])
check("items whose UNSTRIPPED text would have leaked", would,
      leak_c["items_whose_UNSTRIPPED_text_would_have_leaked"])
check("per-item strip_counts mismatches", len(mismatched_counts), 0)
check("frozen section_text reproduced byte-for-byte from raw XML (mismatches)",
      len(mismatched_text), 0)
for m in mismatched_counts[:10]:
    print("    ", m)
for m in mismatched_text[:10]:
    print("     text differs:", m)

# ---------------------------------------------------------------- 5. n and the closure
print()
print("=" * 100)
print("4. n, THE CLOSURE, AND EXACT COUNT MATCHING")
print("=" * 100)
pos = [i for i in items if i["label"] == "WILL_FAIL"]
neg = [i for i in items if i["label"] == "WILL_EXECUTE"]
check("n_items", len(items), ladder_c["n_items"])
check("positives", len(pos), ladder_c["n_pairs"])
check("negatives", len(neg), ladder_c["n_pairs"])
dropped = sum(rungs_c[r]["positives"] for r in ladder_c["ladder"]["order"]
              if r not in ("pool-citations-resolved", "kept"))
check("ladder closes: dropped + kept", dropped + rungs_c["kept"]["positives"], len(pool_pairs))
print(f"  rung-by-rung positives: " +
      ", ".join(f"{r}={rungs_c[r]['positives']}" for r in ladder_c["ladder"]["order"]))

# exact count matching, independently
bad = []
bydoc = {}
for i in items:
    bydoc.setdefault(i["frdoc"], {}).setdefault(i["label"], []).append(i)
for f, roles in bydoc.items():
    p = sorted(x["instruction_count"] for x in roles.get("WILL_FAIL", []))
    n = sorted(x["instruction_count"] for x in roles.get("WILL_EXECUTE", []))
    if p != n:
        bad.append((f, p, n))
check("documents whose positive/negative instruction counts differ", len(bad), 0)

# and cross-check instruction_count against the attribution file
bad2 = []
for i in items:
    real = counts.get(i["frdoc"], {}).get(i["section"])
    if real != i["instruction_count"]:
        bad2.append((i["item_id"], real, i["instruction_count"]))
    if len(i["instructions"]) != i["instruction_count"]:
        bad2.append((i["item_id"], "len(instructions)", len(i["instructions"]),
                     i["instruction_count"]))
check("items whose instruction_count disagrees with data/attribution-v11", len(bad2), 0)
for b in bad2[:10]:
    print("    ", b)

print()
print("=" * 100)
print("DIFFS:", FAIL if FAIL else "none - every committed number reproduced")
print("=" * 100)
sys.exit(1 if FAIL else 0)
