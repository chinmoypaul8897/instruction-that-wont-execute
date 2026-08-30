"""CH-03 RE-REVIEW round 2 - mutation testing of the FIXED code.

Each mutation is written back in place, the full suite is run, and the file is
restored from git. Hard rule 16: the patch is asserted to have landed (new text
present, old text gone) BEFORE the suite runs, so a patch that silently failed to
apply cannot masquerade as a caught mutation.

For every mutation that changes `build_pairs`, the mutated PAIRING is also computed
directly against the real corpus and its sort-order bias reported - because the
suite's frozen-corpus tests read `data/evalset/items.jsonl`, which a source mutation
does not touch. That distinction is the point of this probe.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

MUTATIONS = [
    ("MA revert the negative-selection rule to `free[0]` (the F1 defect)",
     "src/eval_set.py",
     "        negative = min(side, key=lambda s: (abs_rank(section_sort_key(s), key), s))",
     "        negative = free[0]"),

    ("MB the balance counter ALWAYS picks the higher side",
     "src/eval_set.py",
     "            side = higher if balance >= 0 else lower",
     "            side = higher"),

    ("MC the balance counter ALWAYS picks the lower side",
     "src/eval_set.py",
     "            side = higher if balance >= 0 else lower",
     "            side = lower"),

    ("MD revert the <PARTS> fix - a volume with no declared range is skipped again",
     "src/cfr_pit.py",
     "        # F2: no declared range means a single-volume title, which covers the WHOLE\n"
     "        # title. Searching it and finding nothing is a real answer; refusing to search\n"
     "        # it and reporting \"not in the as-of edition\" is a fabricated one.\n"
     "        return True, True",
     "        return False, False"),

    ("ME the nearest-candidate tie-break becomes the farthest",
     "src/eval_set.py",
     "        negative = min(side, key=lambda s: (abs_rank(section_sort_key(s), key), s))",
     "        negative = max(side, key=lambda s: (abs_rank(section_sort_key(s), key), s))"),

    ("MF the balance counter is never updated (it stays at 0 forever)",
     "src/eval_set.py",
     "        balance += 1 if section_sort_key(negative) < key else -1",
     "        balance += 0"),
]


def binom_two_sided(k, n, p=0.5):
    probs = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = probs[k]
    return sum(x for x in probs if x <= obs * (1 + 1e-12))


def pairing_under_current_source():
    """Rebuild the pairing in a FRESH interpreter so the mutated source is used."""
    code = r'''
import json, sys, math
sys.path.insert(0, "src")
from eval_set import build_pairs, instruction_counts, load_jsonl
from cfr_pit import section_sort_key
from pathlib import Path
records = load_jsonl(Path("data/attribution-v11/amdpars_v11.jsonl"))
cit = json.loads(Path("data/amdpars/citations.json").read_text(encoding="utf-8"))
counts = instruction_counts(records, "v11")
defects = sorted({(c["frdoc"], c["section"]) for c in cit.values()
                  if c.get("status") == "resolved"})
pairs, un = build_pairs(counts, defects, 0)
before = sum(1 for p in pairs
             if section_sort_key(p["negative"]) < section_sort_key(p["positive"]))
print(json.dumps({"pairs": len(pairs), "before": before}))
'''
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(REPO),
                          capture_output=True, text=True)
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"pairs": None, "before": None, "err": proc.stderr[-300:]}


def run_suite():
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header",
                           "tests/"], cwd=str(REPO), capture_output=True, text=True)
    tail = [l for l in proc.stdout.splitlines() if l.strip()]
    return proc.returncode != 0, (tail[-1] if tail else "")


def main():
    base = pairing_under_current_source()
    print("BASELINE (unmutated source, pairing rebuilt from the real corpus):")
    print("   %d pairs, %d negatives sort before, p = %.6f\n"
          % (base["pairs"], base["before"],
             binom_two_sided(base["before"], base["pairs"])))

    rows = []
    for name, relpath, old, new in MUTATIONS:
        target = REPO / relpath
        original = target.read_text(encoding="utf-8")
        if old not in original:
            print("!! %s : target text NOT FOUND in %s - SKIPPED" % (name, relpath))
            rows.append((name, "PATCH-DID-NOT-MATCH", "", ""))
            continue
        mutated = original.replace(old, new, 1)
        target.write_text(mutated, encoding="utf-8", newline="")
        back = target.read_text(encoding="utf-8")
        assert back.count(old) == original.count(old) - 1, name + ": patch did not land"
        assert new in back, name + ": new text absent"
        try:
            caught, tail = run_suite()
            pr = pairing_under_current_source()
        finally:
            target.write_text(original, encoding="utf-8", newline="")
            assert target.read_text(encoding="utf-8") == original, "restore failed"
        p = (binom_two_sided(pr["before"], pr["pairs"])
             if pr.get("pairs") else float("nan"))
        rows.append((name, "CAUGHT" if caught else "NOT CAUGHT", tail,
                     "pairs %s, before %s, p = %.6f" % (pr["pairs"], pr["before"], p)))
        print("  %-11s %s" % ("CAUGHT" if caught else "NOT CAUGHT", name))
        print("              suite: %s" % tail)
        print("              rebuilt pairing: %s" % rows[-1][3])

    print("\n" + "=" * 78)
    for name, verdict, tail, pr in rows:
        print("%-11s %s" % (verdict, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
