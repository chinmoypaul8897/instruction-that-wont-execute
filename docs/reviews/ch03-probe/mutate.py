"""ADVERSARIAL REVIEW of CH-03 - mutation testing of the eval-set constructor.

Each mutation is applied to a COPY of src/eval_set.py written back in place, the full
suite is run, and the file is restored from git. Every patch asserts that the old text
is gone and the new text is present (CLAUDE.md hard rule 16) before the suite runs -
a mutation that silently failed to apply would look like a caught mutation.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TARGET = REPO / "src/eval_set.py"
ORIGINAL = TARGET.read_text(encoding="utf-8")
ORIG_SHA = hashlib.sha256(ORIGINAL.encode()).hexdigest()

MUTATIONS = [
    ("M1 tolerance 0 -> effectively 1 (exact matching relaxed)",
     "and abs(c - own) <= tolerance)",
     "and abs(c - own) <= tolerance + 1)"),

    ("M2 a defect section is permitted as a NEGATIVE",
     "                      and s not in defect_by_doc.get(frdoc, set())\n"
     "                      and s not in taken\n",
     "                      and s not in taken\n"),

    ("M3 a negative may be REUSED across positives",
     "        negative = free[0]\n        taken.add(negative)\n",
     "        negative = free[0]\n"),

    ("M4 the exclusion-ladder closure assertion is dropped",
     "    if dropped + kept_pos != len(all_defects):\n"
     "        raise EvalSetError(\n"
     "            f\"exclusion ladder does not close: dropped {dropped} + kept {kept_pos} \"\n"
     "            f\"!= {len(all_defects)} resolved pool citations\")\n",
     "    if False:\n        pass\n"),

    ("M5 build_pairs' own pairs+unmatched==defects guard is dropped",
     "    if len(pairs) + len(unmatched) != len(list(defects)):\n"
     "        raise EvalSetError(\"pairs + unmatched != defects; the ladder does not close\")\n",
     ""),

    ("M6 the leakage gate no longer drops a leaking pair from the freeze",
     "        if bad:\n            leak_failures.append",
     "        if False:\n            leak_failures.append"),

    ("M7 the declared negative-selection rule flips to the LAST sorted candidate",
     "        negative = free[0]",
     "        negative = free[-1]"),

    ("M8 the n_items == 2 * n_pairs assertion is dropped",
     "    if n_items != 2 * n_pairs:\n"
     "        raise EvalSetError(f\"n items {n_items} != 2 x pairs {n_pairs}\")\n",
     ""),

    ("M9 instruction_counts silently counts UNATTRIBUTED elements too",
     "        sec = r.get(key)\n        if sec:\n",
     "        sec = r.get(key) or \"__unattributed__\"\n        if sec:\n"),
]

results = []
for name, old, new in MUTATIONS:
    if old not in ORIGINAL:
        results.append((name, "PATCH-DID-NOT-MATCH", ""))
        print(f"!! {name}: the target text is not in the file - patch skipped")
        continue
    mutated = ORIGINAL.replace(old, new, 1)
    assert new in mutated or new == "", name
    assert mutated != ORIGINAL, name
    TARGET.write_text(mutated, encoding="utf-8", newline="")
    # rule 16: the new text is present AND the old is gone (for this occurrence)
    back = TARGET.read_text(encoding="utf-8")
    assert back.count(old) == ORIGINAL.count(old) - 1, f"{name}: patch did not land"
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-x",
                           "tests/"], cwd=str(REPO), capture_output=True, text=True)
    tail = [l for l in proc.stdout.splitlines() if l.strip()][-1:]
    caught = proc.returncode != 0
    results.append((name, "CAUGHT" if caught else "NOT CAUGHT", tail[0] if tail else ""))
    print(f"  {'CAUGHT    ' if caught else 'NOT CAUGHT'}  {name}")
    print(f"              {tail[0] if tail else ''}")
    TARGET.write_text(ORIGINAL, encoding="utf-8", newline="")

TARGET.write_text(ORIGINAL, encoding="utf-8", newline="")
assert hashlib.sha256(TARGET.read_text(encoding='utf-8').encode()).hexdigest() == ORIG_SHA

print()
print("=" * 100)
for name, verdict, tail in results:
    print(f"  {verdict:<18} {name}")
print("=" * 100)
