"""ADVERSARIAL REVIEW of CH-03 - attack the eval set with the cheapest thing that works.

Fits a single threshold on every cheap feature computable from items.jsonl WITHOUT a
model, in-sample (the most generous possible attack), and reports the best accuracy.
Also fits the paired/within-document version, which is the attack that matters for a
matched design, and a permutation null for the best feature.

Fields that ARE the label are excluded by name: label, role, note_text, note_node.
"""
import json
import random
import re
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
items = [json.loads(l) for l in
         (REPO / "data/evalset/items.jsonl").read_text(encoding="utf-8").splitlines()
         if l.strip()]
y = [1 if i["label"] == "WILL_FAIL" else 0 for i in items]
N = len(items)
print(f"n = {N}   positives = {sum(y)}   negatives = {N - sum(y)}")

OPS = ("revise", "add", "remove", "redesignate", "amend")


def feats(i):
    txt = i["section_text"]
    ins = i["instructions"]
    f = {
        "instruction_count": i["instruction_count"],
        "chars_stripped": i["chars_stripped"],
        "chars_unstripped": i["chars_unstripped"],
        "chars_removed_by_strip": i["chars_unstripped"] - i["chars_stripped"],
        "strip_total": i["strip_counts"]["total"],
        "strip_EDNOTE": i["strip_counts"]["EDNOTE"],
        "strip_CITA": i["strip_counts"]["CITA"],
        "strip_EFFDNOTP": i["strip_counts"]["EFFDNOTP"],
        "strip_EAR": i["strip_counts"]["EAR"],
        "text_len": len(txt),
        "text_lines": txt.count("\n") + 1,
        "text_words": len(txt.split()),
        "n_paragraph_designators_in_text": len(re.findall(r"\([a-z0-9]{1,3}\)", txt)),
        "n_digits_in_text": sum(c.isdigit() for c in txt),
        "section_part": int(re.match(r"\d+", i["section"]).group(0)),
        "cfr_title": int(i["cfr_title"]),
        "as_of_edition": i["as_of_edition"],
        "section_numeric_tail": int(re.sub(r"\D", "", i["section"].split(".", 1)[-1]) or 0),
        "section_str_len": len(i["section"]),
        "section_has_letter": int(bool(re.search(r"[A-Za-z]", i["section"].split(".", 1)[-1]))),
        "doc_completeness": i["document_completeness_v11"],
        "doc_attribution": i["document_attribution_rate_v11"],
        "doc_parse": i["document_parse_rate_v11"],
        "doc_amdpar_count": i["document_amdpar_count"],
        "volume_route_is_fallback": int(i["volume_route"] != "range-match"),
        "n_instructions_with_anchor": sum(1 for r in ins if r["anchor"]),
        "n_instructions_with_designation": sum(1 for r in ins if r["designation"]),
        "instr_text_total_len": sum(len(r["text"]) for r in ins),
        "instr_text_mean_len": (statistics.mean(len(r["text"]) for r in ins) if ins else 0),
        "first_ordinal": min((r["ordinal"] for r in ins), default=0),
        "last_ordinal": max((r["ordinal"] for r in ins), default=0),
        "ordinal_span": (max(r["ordinal"] for r in ins) - min(r["ordinal"] for r in ins)
                         if ins else 0),
        "pubdate_year": int(i["publication_date"][:4]),
    }
    for op in OPS:
        f[f"n_op_{op}"] = sum(1 for r in ins if r["operation"] == op)
    f["n_op_none"] = sum(1 for r in ins if r["operation"] is None)
    return f


F = [feats(i) for i in items]
names = sorted(F[0])


def best_threshold_acc(vals, labels):
    """Best in-sample accuracy of  (v > t) or (v <= t)  over all thresholds."""
    best = 0.0
    cands = sorted(set(vals))
    for t in cands:
        a = sum(1 for v, l in zip(vals, labels) if (v > t) == (l == 1)) / len(labels)
        best = max(best, a, 1 - a)
    # also the degenerate constant
    p = sum(labels) / len(labels)
    return max(best, p, 1 - p)


print()
print("=" * 100)
print("A. SINGLE-THRESHOLD ATTACK, IN-SAMPLE (the most generous attack there is)")
print("=" * 100)
rows = []
for nme in names:
    vals = [f[nme] for f in F]
    rows.append((best_threshold_acc(vals, y), nme,
                 len(set(vals))))
rows.sort(reverse=True)
for acc, nme, k in rows:
    print(f"  {acc:.4f}   {nme:<36} ({k} distinct values)")

best_acc, best_name, _ = rows[0]
print()
print(f"  BEST single feature: {best_name} at {best_acc:.4f} in-sample accuracy")

# permutation null for the best feature
random.seed(20260831)
vals = [f[best_name] for f in F]
null = []
for _ in range(2000):
    perm = y[:]
    random.shuffle(perm)
    null.append(best_threshold_acc(vals, perm))
p = sum(1 for x in null if x >= best_acc) / len(null)
print(f"  permutation null (2000 shuffles): mean {statistics.mean(null):.4f}  "
      f"95th pct {sorted(null)[int(0.95 * len(null))]:.4f}   p = {p:.4f}")

print()
print("=" * 100)
print("B. THE PAIRED ATTACK - within each (positive, negative) pair, does the feature")
print("   order the two correctly?  Chance = 0.50.  This is the attack that matters")
print("   for a matched design.")
print("=" * 100)
pairs = {}
for i, f in zip(items, F):
    pairs.setdefault(i["frdoc"] + "|" + str(i["instruction_count"]), []).append((i, f))
# rebuild real pairs by frdoc + instruction_count + role
by = {}
for i, f in zip(items, F):
    by.setdefault((i["frdoc"], i["instruction_count"]), {}).setdefault(i["role"], []).append((i, f))
real_pairs = []
for k, roles in by.items():
    ps, ns = roles.get("positive", []), roles.get("negative", [])
    for a, b in zip(sorted(ps, key=lambda x: x[0]["section"]),
                    sorted(ns, key=lambda x: x[0]["section"])):
        real_pairs.append((a, b))
print(f"  reconstructed pairs: {len(real_pairs)}")
prows = []
for nme in names:
    wins = ties = 0
    for (pi, pf), (ni, nf) in real_pairs:
        if pf[nme] > nf[nme]:
            wins += 1
        elif pf[nme] == nf[nme]:
            ties += 1
    n = len(real_pairs)
    acc = (wins + 0.5 * ties) / n
    prows.append((max(acc, 1 - acc), acc, ties, nme))
prows.sort(reverse=True)
for best, acc, ties, nme in prows:
    print(f"  {best:.4f}  (raw {acc:.4f}, {ties} ties)  {nme}")

print()
print("=" * 100)
print("C. ORDERING / IDENTITY ARTEFACTS")
print("=" * 100)
alpha = sum(1 for (pi, _), (ni, _) in real_pairs if pi["section"] < ni["section"])
print(f"  positive's section sorts BEFORE its negative's: {alpha}/{len(real_pairs)}"
      f" = {alpha / len(real_pairs):.4f}")
first = sum(1 for i in items[::2])
print(f"  items.jsonl is sorted by (item_id, role); label of the FIRST item of each "
      f"frdoc block:")
blocks = {}
for i in items:
    blocks.setdefault(i["frdoc"], []).append(i["label"])
firstpos = sum(1 for v in blocks.values() if v[0] == "WILL_FAIL")
print(f"    frdoc blocks whose first item is a positive: {firstpos}/{len(blocks)}")

print()
print("=" * 100)
print("D. THE FEATURE THE SPEC SINGLES OUT")
print("=" * 100)
pc = sorted(i["instruction_count"] for i in items if i["label"] == "WILL_FAIL")
nc = sorted(i["instruction_count"] for i in items if i["label"] == "WILL_EXECUTE")
print(f"  positive instruction-count multiset == negative multiset : {pc == nc}")
print(f"  distribution: {sorted(set(pc))}")
