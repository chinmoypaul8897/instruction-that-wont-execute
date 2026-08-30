"""Prove hard rule 9 for CH-01: same inputs -> byte-identical outputs. Evidence.

Hard rule 9 says determinism must be *provable by hash*, not asserted. So this
re-runs the extractor into a throwaway directory and compares every artefact's
SHA-256 against the committed freeze, then verifies the freeze against its own
manifest with the network untouched.

It is a real re-parse of all 824 MB of raw XML, not a re-read of the committed
output, so a hidden clock, a dict-ordering dependency or a locale-sensitive format
would show up here as a mismatch. Takes a few minutes.

    python docs/evidence/ch01-pool/ch01_determinism.py

Output committed as `ch01-determinism.txt`. Requires `data/raw/ecfr/` to be
populated (`python refetch.py`); prints a SKIP banner and exits 2 if it is not,
because a determinism proof that silently passes on missing input proves nothing.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from harvest_ednotes import main as harvest_main, sha256_file  # noqa: E402

RAW = REPO / "data" / "raw" / "ecfr"
FROZEN = REPO / "data" / "ednotes"
ARTEFACTS = ("ednotes.jsonl", "defect_notes.jsonl", "counts.json",
             "counts_by_title.csv", "manifest.json", "source_index.json")


def main() -> int:
    if not list(RAW.glob("ECFR-title*.xml")):
        print("SKIP - data/raw/ecfr/ is empty. data/raw/ is git-ignored by design;")
        print("       run `python refetch.py` to repopulate it, then re-run this.")
        print("       Exiting 2 rather than 0: a determinism proof that passes on")
        print("       missing input is the exact silent green this project exposes.")
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="ch01-determinism-"))
    try:
        print("RE-EXTRACT  824 MB of raw govinfo XML -> a throwaway directory")
        print("=" * 72)
        rc = harvest_main(["extract", "--raw", str(RAW), "--out", str(tmp)])
        if rc != 0:
            print(f"extract returned {rc}")
            return 1

        print()
        print("COMPARE  fresh run against the committed freeze, artefact by artefact")
        print("=" * 72)
        bad = 0
        for name in ARTEFACTS:
            committed, fresh = FROZEN / name, tmp / name
            if not committed.exists() or not fresh.exists():
                print(f"  MISSING  {name}")
                bad += 1
                continue
            a, b = sha256_file(committed), sha256_file(fresh)
            same = a == b
            bad += (not same)
            print(f"  {'IDENTICAL' if same else 'DIFFERS  '}  {name:<24} {a}")
            if not same:
                print(f"  {'':<11}  {'fresh run':<24} {b}")

        print()
        print(f"{len(ARTEFACTS) - bad}/{len(ARTEFACTS)} artefacts byte-identical across runs")
        print()
        print("VERIFY  the committed freeze against its own manifest (no network)")
        print("=" * 72)
        rc = harvest_main(["verify", "--out", str(FROZEN)])
        return 1 if (bad or rc) else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
