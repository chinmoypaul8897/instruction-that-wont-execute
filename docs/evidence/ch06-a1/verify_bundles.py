"""Does every committed trajectory BUNDLE still match its per-item sources?

Nothing checked this, and the gap was not hypothetical. At CH-06 the committed
`A1-minus-tool-rep1.jsonl` did not match its 82 per-item trajectories — found by
regenerating the bundle from source and comparing SHA-256, which is what this script now
does for every arm.

**The first explanation written here was wrong and is corrected rather than deleted.** It
said the missing record was *"a `retry`, written after the bundler had already read that
file"* — a race. It was not. The real cause was that **the arm had been run twice**: the
same configuration was queued in two concurrent jobs, the second overwrote the first's
per-item files, and the committed bundle was simply the earlier run's. Diagnosing it as a
race and moving on would have left a real process defect - `QUESTIONS.md` Q26 - hidden
behind a plausible technical story. Hard rule 15 applies to one's own explanations.

WHY IT MATTERS MORE THAN ONE MISSING LINE
------------------------------------------
`docs/trajectories/arms/per-item/` is **git-ignored** — the pre-commit guard caps the
tracked tree, so the per-item files never enter the repository and the bundle is the
*only* copy that ships. A bundle that silently drops a record drops it permanently, and
the record it dropped here was a **retry**: precisely the kind of event deliverable 4
asks to see, and precisely the kind a summary would have smoothed away.

This is the third instance of one pattern in a single session, all in the bundling step:
  * `B0prime`  — bundled **0 of 246** trajectories, wrong glob, no error raised
  * leakage probe — **never bundled at all**, 82 trajectories left only in the ignored dir
  * `A1-minus-tool` — the shipped bundle was a **different run** from the one on disk (Q26)

Each was silent. `plan.md` CH-12 should run this script as a gate.

PURITY: no network, no clock, no randomness. Read-only — it never rewrites a bundle, it
only reports. Fixing is a decision, and a verifier that repaired what it measured could
not be trusted to report honestly.

    python docs/evidence/ch06-a1/verify_bundles.py
    -> exit 0 if every bundle matches, 1 if any does not
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PER_ITEM = REPO / "docs/trajectories/arms/per-item"
BUNDLES = REPO / "docs/trajectories/arms"
LEDGER = REPO / "docs/evidence/runs/cost_ledger.csv"

# run_id prefix -> the bundle basename it ships as, where the two differ
ALIASES = {"B0agentCURRENT": "B0-agent-currenttext"}
_RUN = re.compile(r"^(?P<prefix>.+?)__.*__rep(?P<rep>\d+)(?:__.*)?$")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def regenerate(prefix: str, rep: int) -> tuple[str, int, int]:
    """Rebuild what the bundle SHOULD be, from the per-item files, in bundler order."""
    files = sorted(set(PER_ITEM.glob(f"{prefix}__*__rep{rep}.jsonl"))
                   | set(PER_ITEM.glob(f"{prefix}__*__rep{rep}__*.jsonl")))
    lines = []
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                lines.append(line)
    return ("\n".join(lines) + "\n" if lines else ""), len(files), len(lines)


def discovered_runs() -> set[tuple[str, int]]:
    """Every (run_id prefix, rep) present on disk. Not a hardcoded list - a hardcoded
    list is how the leakage probe's 82 trajectories went unbundled in the first place."""
    out = set()
    for f in PER_ITEM.glob("*.jsonl"):
        m = _RUN.match(f.stem)
        if m:
            out.add((m.group("prefix"), int(m.group("rep"))))
    return out


def ledger_arms() -> set[str]:
    if not LEDGER.exists():
        return set()
    with open(LEDGER, encoding="utf-8", newline="") as fh:
        return {r["arm"] for r in csv.DictReader(fh)}


def main() -> int:
    runs = sorted(discovered_runs())
    L, bad = [], 0
    w = L.append
    w("=" * 78)
    w("TRAJECTORY BUNDLE VERIFICATION - does the shipped copy match its sources?")
    w("=" * 78)
    w("")
    w(f"  per-item dir  {PER_ITEM.relative_to(REPO).as_posix()}  (GIT-IGNORED - the")
    w("                bundle is the ONLY copy that ships)")
    w(f"  runs on disk  {len(runs)}")
    w("")
    w(f"  {'bundle':38s} {'files':>6s} {'records':>8s}  {'status':<10s}")
    for prefix, rep in runs:
        name = f"{ALIASES.get(prefix, prefix)}-rep{rep}.jsonl"
        path = BUNDLES / name
        regen, nfiles, nrec = regenerate(prefix, rep)
        if not path.exists():
            w(f"  {name:38s} {nfiles:>6d} {nrec:>8d}  MISSING - never bundled")
            bad += 1
            continue
        have = path.read_text(encoding="utf-8")
        if sha(have) == sha(regen):
            w(f"  {name:38s} {nfiles:>6d} {nrec:>8d}  OK")
        else:
            have_n = len([x for x in have.splitlines() if x.strip()])
            w(f"  {name:38s} {nfiles:>6d} {nrec:>8d}  MISMATCH - shipped {have_n} "
              f"records, sources have {nrec}")
            bad += 1
    w("")

    # Every arm the ledger names must have a committed bundle. The ledger is the
    # authority on what ran; the bundles are the authority on what shipped.
    w("-" * 78)
    w("EVERY ARM IN THE LEDGER MUST HAVE A SHIPPED BUNDLE")
    w("-" * 78)
    w("")
    shipped = {p.name for p in BUNDLES.glob("*.jsonl")}
    for arm in sorted(ledger_arms()):
        if arm == "probe-model-id":
            w(f"  {arm:26s} SKIPPED - a pre-arm connectivity probe, not an arm")
            continue
        hit = [s for s in shipped if s.startswith(arm + "-rep")]
        if hit:
            w(f"  {arm:26s} OK   {len(hit)} bundle(s)")
        else:
            w(f"  {arm:26s} NO BUNDLE FOUND")
            bad += 1
    w("")
    w("=" * 78)
    w(f"  RESULT: {'ALL BUNDLES VERIFY' if bad == 0 else f'{bad} PROBLEM(S)'}")
    w("=" * 78)
    text = "\n".join(L) + "\n"
    print(text)
    # The output is deliberately NOT written to a tracked file. This script is a
    # deterministic pass/fail check whose result is reproduced by running it, and the
    # tracked-file count sits at the pre-commit guard's hard limit of 300 while the
    # tree is already 9.4 MB over the 50 MB submission cap (QUESTIONS.md Q25). Shipping
    # the CHECKER is worth more than shipping a snapshot of its output; the result at
    # the time of writing - ALL 15 BUNDLES VERIFY, and every ledger arm has a bundle -
    # is recorded in PROGRESS.md and in this commit's message.
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
