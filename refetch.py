"""Reproduce everything under `data/` from govinfo, then prove it matches.

`data/` ships **extracted** artefacts only. The raw inputs are not in the repository
and never will be: 49 ECFR title XMLs are 824 MB against a 50 MB submission cap
(`QUESTIONS.md` Q2, consequence C1). This script is what makes that honest - it
re-downloads the raw XML into the git-ignored `data/raw/`, re-runs the extractor, and
checks the result against the committed SHA-256 manifest.

    python refetch.py                  # fetch + extract + verify   (needs network)
    python refetch.py --verify-only    # verify the committed freeze (no network)
    python refetch.py --title 7 --title 11   # just the two titles the goldens cite

`--verify-only` is the mode the clean-clone rehearsal at CH-14a runs with the network
off. It touches govinfo not at all.

WHY THE HASHES CAN BE TRUSTED TO MEAN SOMETHING. The extractor is pure and its output
is written with sorted keys and LF endings, so the same raw bytes give byte-identical
artefacts on any platform (hard rule 9). What this script cannot promise is that
govinfo still serves the same bytes: the eCFR is a live document and every title XML
carries a last-modified date that moves. A hash mismatch after a refetch is therefore
**a real event to report, not a bug to paper over** - upstream changed, and the
manifest records what it looked like when this project measured it. The mismatch
report below prints both sides rather than exiting on the first difference.

Chunks add to this file as they freeze more of `data/`. CH-01 freezes
`data/ednotes/`; CH-02 adds `data/amdpars/`; CH-03 adds the point-in-time
section text.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))

from harvest_ednotes import (  # noqa: E402
    DEFAULT_OUT_DIR,
    DEFAULT_RAW_DIR,
    fetch_titles,
    main as harvest_main,
    sha256_file,
)
import attribute_amdpars as amdpar  # noqa: E402

# Every frozen artefact set, in the order a fresh clone should rebuild them.
FREEZES = [
    {
        "chunk": "CH-01",
        "dir": DEFAULT_OUT_DIR,
        "raw": DEFAULT_RAW_DIR,
        "what": "govinfo ECFR <EDNOTE> records and the codification-defect pool",
    },
    {
        "chunk": "CH-02",
        "dir": amdpar.DEFAULT_OUT_DIR,
        "raw": amdpar.DEFAULT_RAW_DIR,
        "what": "govinfo FR <AMDPAR> instructions attributed to sections",
    },
]


def verify(freeze: dict) -> tuple[int, int, list[str]]:
    """Return (ok, total, complaints). Never exits early - a partial report is worse
    than a full one, and the second mismatch is often the informative one."""
    out = REPO / freeze["dir"]
    manifest_path = out / "manifest.json"
    if not manifest_path.exists():
        return 0, 0, [f"{freeze['chunk']}: no manifest at {manifest_path}"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ok, complaints = 0, []
    for name, want in sorted(manifest["files"].items()):
        path = out / name
        if not path.exists():
            complaints.append(f"MISSING  {name}")
            continue
        got = sha256_file(path)
        if got == want["sha256"]:
            ok += 1
            print(f"  OK    {name:<24} {got}")
        else:
            complaints.append(
                f"MISMATCH {name}\n"
                f"           manifest {want['sha256']}\n"
                f"           on disk  {got}")
            print(f"  FAIL  {name:<24} {got}")
    return ok, len(manifest["files"]), complaints


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify-only", action="store_true",
                    help="check the committed freeze against its manifest; no network")
    ap.add_argument("--title", action="append",
                    help="restrict the fetch to these CFR titles (repeatable)")
    args = ap.parse_args(argv)

    failures: list[str] = []

    if not args.verify_only:
        print("=" * 72)
        print("FETCH  govinfo ECFR bulk XML -> data/raw/ecfr/  (git-ignored, never tracked)")
        print("=" * 72)
        results = fetch_titles(REPO / DEFAULT_RAW_DIR, only=(args.title or None))
        failed = [r for r in results if str(r["status"]).startswith("FAILED")]
        for r in results:
            print(f"  title-{r['title']:<3} {r['name']:<24} {r['size']:>12,} B  {r['status']}")
        print(f"  files={len(results)} ok={len(results) - len(failed)} failed={len(failed)}"
              f" bytes={sum(r['size'] for r in results):,}")
        if failed:
            failures.append(f"{len(failed)} title(s) failed to download")

        print()
        print("=" * 72)
        print("EXTRACT  <EDNOTE> -> data/ednotes/   (pure: no network, no clock)")
        print("=" * 72)
        rc = harvest_main(["extract", "--raw", str(REPO / DEFAULT_RAW_DIR),
                           "--out", str(REPO / DEFAULT_OUT_DIR)])
        if rc != 0:
            failures.append("extract returned a non-zero status")

        print()
        print("=" * 72)
        print("FETCH  govinfo FR daily issues -> data/raw/fr/   (git-ignored)")
        print("=" * 72)
        rc = amdpar.main(["fetch", "--raw", str(REPO / amdpar.DEFAULT_RAW_DIR)])
        if rc != 0:
            failures.append("FR issue fetch reported a failure")

        print()
        print("=" * 72)
        print("EXTRACT  <AMDPAR> -> data/amdpars/   (pure: no network, no clock)")
        print("=" * 72)
        # Two rounds, bounded. A citation whose note carries the FILING date rather
        # than the publication date resolves in a neighbouring issue, and the extract
        # cannot know which neighbours it needs until it has tried. Round 1 records
        # them in `wanted_issues.json`; round 2 runs with them present. If round 2
        # still wants an issue the ladder says so and the rung is counted, never
        # papered over.
        for round_no in (1, 2):
            rc = amdpar.main(["extract", "--raw", str(REPO / amdpar.DEFAULT_RAW_DIR),
                              "--out", str(REPO / amdpar.DEFAULT_OUT_DIR)])
            if rc != 0:
                failures.append(f"AMDPAR extract round {round_no} returned non-zero")
                break
            wanted_path = REPO / amdpar.DEFAULT_OUT_DIR / "wanted_issues.json"
            wanted = json.loads(wanted_path.read_text(encoding="utf-8"))["dates"]
            if not wanted:
                print(f"  round {round_no}: no neighbour-day issues outstanding")
                break
            print(f"  round {round_no}: fetching neighbour-day issues {wanted}")
            for r in amdpar.fetch_issues(REPO / amdpar.DEFAULT_RAW_DIR, wanted):
                print(f"    {r['date']}  {r['bytes']:>12,} B  {r['status']}")

    print()
    print("=" * 72)
    print("VERIFY  frozen artefacts against the committed SHA-256 manifest")
    print("=" * 72)
    for freeze in FREEZES:
        print(f"{freeze['chunk']} - {freeze['what']}")
        ok, total, complaints = verify(freeze)
        print(f"  {ok}/{total} verify")
        failures.extend(complaints)

    print()
    if failures:
        print(f"REFETCH FAILED - {len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        print()
        print("A hash mismatch is a REPORTABLE EVENT, not a defect to suppress. The eCFR")
        print("is a live document; govinfo re-publishes each title as it is amended. The")
        print("manifest records what this project measured, with the govinfo")
        print("last-modified stamps in manifest.json['raw_inputs'] to date it.")
        return 1

    print("REFETCH OK - every frozen artefact reproduces from govinfo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
