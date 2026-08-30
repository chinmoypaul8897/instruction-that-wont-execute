"""CH-03 RE-REVIEW round 2 - re-derive the exclusion ladder from the inputs.

Reimplements the pairing from CONTEXT.md section 8 + the pre-registration, importing
NOTHING from src/. Reads only:
    data/amdpars/citations.json          the resolved pool
    data/attribution-v11/amdpars_v11.jsonl   the attributed instructions
    data/evalset/*.json / items.jsonl    the committed result, for comparison
"""
from __future__ import annotations

import json
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


def main():
    cit = json.loads((REPO / "data/amdpars/citations.json").read_text("utf-8"))
    resolved = [c for c in cit.values() if c.get("status") == "resolved"]
    pool = sorted({(c["frdoc"], c["section"]) for c in resolved})
    print("resolved citations           : %d" % len(resolved))
    print("distinct (frdoc, section)    : %d   <- the ladder TOP" % len(pool))

    counts = defaultdict(lambda: defaultdict(int))
    with (REPO / "data/attribution-v11/amdpars_v11.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            s = r.get("section_v11")
            if s:
                counts[r["frdoc"]][s] += 1

    defect_by_doc = defaultdict(set)
    for f, s in pool:
        defect_by_doc[f].add(s)

    no_instr, no_count_match, no_free, matched = [], [], [], []
    used = defaultdict(set)
    for frdoc, section in pool:
        doc = counts.get(frdoc, {})
        own = doc.get(section)
        if own is None:
            no_instr.append((frdoc, section))
            continue
        any_match = sorted(s for s, c in doc.items()
                           if s != section and s not in defect_by_doc[frdoc]
                           and c == own)
        free = [s for s in any_match if s not in used[frdoc]]
        if not free:
            (no_free if any_match else no_count_match).append((frdoc, section))
            continue
        # the rule under review, reimplemented from the pre-registration ERRATA
        matched.append((frdoc, section, free))
        used[frdoc].add(None)          # placeholder; the real consumption is below
    print("\nrungs re-derived independently of src/:")
    print("  positive-has-no-attributed-instructions : %d" % len(no_instr))
    print("  no-count-matched-sibling                : %d" % len(no_count_match))
    print("  no-free-count-matched-sibling (approx)  : %d" % len(no_free))
    print("  reach the pairing stage                 : %d" % len(matched))

    # exact re-run of the consumption rule, so `no-free` is exact
    used = defaultdict(set)
    balance = 0
    pairs, unmatched = [], defaultdict(list)
    for frdoc, section in pool:
        doc = counts.get(frdoc, {})
        own = doc.get(section)
        if own is None:
            unmatched["positive-has-no-attributed-instructions"].append((frdoc, section))
            continue
        any_match = sorted(s for s, c in doc.items()
                           if s != section and s not in defect_by_doc[frdoc] and c == own)
        free = sorted(s for s in any_match if s not in used[frdoc])
        if not free:
            unmatched["no-free-count-matched-sibling" if any_match
                      else "no-count-matched-sibling"].append((frdoc, section))
            continue
        key = sortkey(section)
        lower = [s for s in free if sortkey(s) < key]
        higher = [s for s in free if sortkey(s) > key]
        side = (higher if balance >= 0 else lower) if (lower and higher) else (lower or higher or free)

        def dist(s):
            a, b = sortkey(s), key
            for x, y in zip(a[1], b[1]):
                if x != y:
                    return (abs(a[0] - b[0]), abs(x[1] - y[1]) if x[0] == y[0] == 0 else 1)
            return (abs(a[0] - b[0]), abs(len(a[1]) - len(b[1])))

        neg = min(side, key=lambda s: (dist(s), s))
        balance += 1 if sortkey(neg) < key else -1
        used[frdoc].add(neg)
        pairs.append((frdoc, section, neg))
    print("\nexact re-run:")
    for k in ("positive-has-no-attributed-instructions", "no-count-matched-sibling",
              "no-free-count-matched-sibling"):
        print("  %-42s : %d" % (k, len(unmatched[k])))
    print("  %-42s : %d" % ("pairs reaching text resolution", len(pairs)))
    print("  closure: %d + %d = %d (pool %d)"
          % (len(pairs), sum(len(v) for v in unmatched.values()),
             len(pairs) + sum(len(v) for v in unmatched.values()), len(pool)))

    committed = json.loads((REPO / "data/evalset/exclusion_ladder.json").read_text("utf-8"))
    rungs = committed["ladder"]["rungs"]
    print("\ncommitted vs re-derived:")
    checks = [
        ("pool-citations-resolved", rungs["pool-citations-resolved"]["items"], len(pool)),
        ("positive-has-no-attributed-instructions",
         rungs["positive-has-no-attributed-instructions"]["items"],
         len(unmatched["positive-has-no-attributed-instructions"])),
        ("no-count-matched-sibling", rungs["no-count-matched-sibling"]["items"],
         len(unmatched["no-count-matched-sibling"])),
        ("no-free-count-matched-sibling", rungs["no-free-count-matched-sibling"]["items"],
         len(unmatched["no-free-count-matched-sibling"])),
    ]
    for name, c, r in checks:
        print("  %-42s committed %3s   re-derived %3s   %s"
              % (name, c, r, "OK" if c == r else "*** MISMATCH ***"))
    drop_after = len(pairs) - committed["n_pairs"]
    print("  pairs reaching text resolution %d, kept %d, dropped by the text rungs %d"
          % (len(pairs), committed["n_pairs"], drop_after))
    print("  committed text rungs: section-not-in-as-of-edition %d pairs, "
          "leakage-test-failed-after-strip %d pairs"
          % (rungs["section-not-in-as-of-edition"]["positives"],
             rungs["leakage-test-failed-after-strip"]["positives"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
