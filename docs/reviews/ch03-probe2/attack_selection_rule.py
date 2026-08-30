"""CH-03 RE-REVIEW round 2 - the sharpest structural attack available.

The replacement rule does not only balance sort order: within the chosen side it takes
the candidate NEAREST the positive. That is an asymmetry an attacker can aim at,
because the positive is GIVEN and the negative is CHOSEN. If B is "the nearest free
count-matched sibling of A" but A is not the nearest of B, then A is the positive.

The attacker uses only:
    data/evalset/items.jsonl            (never `label`, `role`, `note_*`, `section_text`)
    data/attribution-v11/amdpars_v11.jsonl   (shipped in the repo; no labels in it)

It does NOT know which sections carry a defect note - that is the label - so the
candidate pool is built WITHOUT the defect exclusion the builder applies. Two
variants are tried: excluding nothing, and excluding the pair's own two members.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
_INT = re.compile(r"\d+")


def sortkey(section):
    part, _, rest = section.partition(".")
    m = _INT.match(part)
    pk = int(m.group(0)) if m else 0
    toks = []
    for t in re.findall(r"\d+|\D+", rest):
        toks.append((0, int(t), "") if t.isdigit() else (1, 0, t))
    return (pk, tuple(toks))


def dist(a, b):
    ka, kb = sortkey(a), sortkey(b)
    for x, y in zip(ka[1], kb[1]):
        if x != y:
            return (abs(ka[0] - kb[0]), abs(x[1] - y[1]) if x[0] == y[0] == 0 else 1)
    return (abs(ka[0] - kb[0]), abs(len(ka[1]) - len(kb[1])))


def binom(k, n, p=0.5):
    f = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    return sum(x for x in f if x <= f[k] * (1 + 1e-12))


def main():
    items = [json.loads(l) for l in
             (REPO / "data/evalset/items.jsonl").read_text("utf-8").splitlines() if l.strip()]
    counts = defaultdict(lambda: defaultdict(int))
    with (REPO / "data/attribution-v11/amdpars_v11.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                s = r.get("section_v11")
                if s:
                    counts[r["frdoc"]][s] += 1

    # blocks recoverable with no labels
    blocks = defaultdict(list)
    for it in items:
        blocks[(it["frdoc"], it["instruction_count"])].append(it)
    cand_pairs = []
    for k in sorted(blocks):
        grp = sorted(blocks[k], key=lambda i: sortkey(i["section"]))
        for j in range(0, len(grp), 2):
            if j + 1 < len(grp):
                cand_pairs.append((grp[j], grp[j + 1]))
    print("attacker-recovered pairs: %d over %d items" % (len(cand_pairs), len(items)))

    for exclude_pair in (False, True):
        for tie_direction in ("A-is-positive-when-B-is-nearer", "reverse"):
            right = 0
            decided = 0
            for A, B in cand_pairs:
                frdoc = A["frdoc"]
                doc = counts.get(frdoc, {})
                own = A["instruction_count"]

                def rank_of(target, anchor):
                    """rank of `target` among anchor's count-matched siblings on
                    target's own side, by distance. 0 = nearest."""
                    key = sortkey(anchor)
                    tk = sortkey(target)
                    side = [s for s, c in doc.items()
                            if c == own and s != anchor
                            and ((sortkey(s) < key) == (tk < key))]
                    if exclude_pair:
                        side = [s for s in side if s not in (A["section"], B["section"])
                                or s == target]
                    if target not in side:
                        return None
                    ordered = sorted(side, key=lambda s: (dist(s, anchor), s))
                    return ordered.index(target)

                rb = rank_of(B["section"], A["section"])     # B as A's negative
                ra = rank_of(A["section"], B["section"])     # A as B's negative
                if rb is None and ra is None:
                    guess_pos = A
                elif rb is None:
                    guess_pos = B
                elif ra is None:
                    guess_pos = A
                elif rb == ra:
                    guess_pos = A
                else:
                    decided += 1
                    guess_pos = A if rb < ra else B
                if tie_direction == "reverse":
                    guess_pos = B if guess_pos is A else A
                guess_neg = B if guess_pos is A else A
                right += (guess_pos["label"] == "WILL_FAIL")
                right += (guess_neg["label"] == "WILL_EXECUTE")
            print("  exclude_pair=%-5s %-32s accuracy %d/%d = %.4f   "
                  "(pairs where the ranks differed: %d)"
                  % (exclude_pair, tie_direction, right, len(items),
                     right / len(items), decided))

    # ---- a second angle: is the negative the section with FEWER siblings? --------
    print("\nsecondary structural probes (block halving on a doc-structure feature):")
    feats = {}
    for it in items:
        doc = counts.get(it["frdoc"], {})
        own = it["instruction_count"]
        key = sortkey(it["section"])
        sib = [s for s, c in doc.items() if c == own and s != it["section"]]
        feats[it["item_id"]] = {
            "n_count_matched_siblings": float(len(sib)),
            "n_siblings_lower": float(sum(1 for s in sib if sortkey(s) < key)),
            "n_siblings_higher": float(sum(1 for s in sib if sortkey(s) > key)),
            "sections_in_doc": float(len(doc)),
            "rank_in_doc": float(sorted(doc, key=sortkey).index(it["section"])),
            "rank_frac_in_doc": (sorted(doc, key=sortkey).index(it["section"])
                                 / max(1, len(doc) - 1)),
            "min_dist_to_any_sibling": float(min([dist(s, it["section"])[0] * 1000
                                                  + dist(s, it["section"])[1]
                                                  for s in sib] or [1e9])),
        }
    for name in sorted(next(iter(feats.values()))):
        best = 0.0
        for direction in (1, -1):
            r = 0
            for _, grp in blocks.items():
                k = len(grp) // 2
                o = sorted(grp, key=lambda it: (direction * feats[it["item_id"]][name],
                                                it["item_id"]))
                for j, it in enumerate(o):
                    r += (("WILL_EXECUTE" if j < k else "WILL_FAIL") == it["label"])
            best = max(best, r / len(items))
        print("   %-28s %.4f" % (name, best))
    return 0


if __name__ == "__main__":
    sys.exit(main())
