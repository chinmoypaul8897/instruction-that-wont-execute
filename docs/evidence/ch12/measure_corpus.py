#!/usr/bin/env python3
"""CH-12 - measure `data/raw/` and every shipped claim about its size.

`REPRODUCE.md` and `SUBMISSION.md` both said `data/raw/` holds **824 MB**.
`REPRODUCE.md` also contains, 186 lines further down, a table that measures it at
**1,443,366,993 B = 1.44 GB** and explains that 824 MB is the eCFR titles alone. So
one file disagreed with itself and the other simply repeated the wrong half.

This script is the measurement both statements are now corrected against. It reads
`data/` and nothing else. `data/` is SEALED (hard rule 11) - this script only stats
it, it never writes, moves or deletes.

MB and GB below are decimal (10^6 and 10^9), stated rather than assumed: the 824 MB
figure is decimal too (824,298,523 B / 10^6 = 824.3), so switching units mid-argument
would have manufactured a second, fake discrepancy. The binary readings are printed
beside them so nobody has to take the convention on trust.

Run:  python docs/evidence/ch12/measure_corpus.py
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"


def walk(root: pathlib.Path) -> tuple[int, int]:
    """(file count, total bytes) beneath root. Symlinks are not followed."""
    files = 0
    total = 0
    for p in root.rglob("*"):
        if p.is_file() and not p.is_symlink():
            files += 1
            total += p.stat().st_size
    return files, total


def fmt(n: int) -> str:
    return (f"{n:,} B  =  {n / 10**6:,.2f} MB (10^6)  =  {n / 10**9:,.3f} GB (10^9)"
            f"   [{n / 2**20:,.2f} MiB, {n / 2**30:,.3f} GiB]")


def main() -> int:
    print("CH-12 - CORPUS SIZE, MEASURED")
    print("=" * 78)

    if not RAW.exists():
        print(f"data/raw/ does not exist at {RAW}")
        print("It is git-ignored and rebuilt by `python refetch.py`. Nothing to measure.")
        return 1

    print(f"root: {RAW.relative_to(ROOT).as_posix()}")
    print()

    subtotal = 0
    subfiles = 0
    print(f"{'subdirectory':<12} {'files':>6}  bytes")
    print("-" * 78)
    for sub in sorted(p for p in RAW.iterdir() if p.is_dir()):
        files, total = walk(sub)
        subtotal += total
        subfiles += files
        print(f"{sub.name + '/':<12} {files:>6}  {fmt(total)}")

    loose_files = [p for p in RAW.iterdir() if p.is_file()]
    loose_bytes = sum(p.stat().st_size for p in loose_files)
    if loose_files or True:  # print the zero branch too (hard rule 14)
        print(f"{'(loose)':<12} {len(loose_files):>6}  {fmt(loose_bytes)}")

    files, total = walk(RAW)
    print("-" * 78)
    print(f"{'TOTAL':<12} {files:>6}  {fmt(total)}")
    assert total == subtotal + loose_bytes, "subdirectory sizes do not sum to the total"
    assert files == subfiles + len(loose_files), "file counts do not sum"
    print(f"sums check: {subtotal:,} + {loose_bytes:,} == {total:,}  OK")
    print()

    # --- the two numbers the shipped documents disagreed about -------------------
    ecfr = RAW / "ecfr"
    ecfr_files, ecfr_bytes = walk(ecfr) if ecfr.exists() else (0, 0)
    print("THE DISCREPANCY, RESOLVED")
    print("-" * 78)
    print(f"  claimed in REPRODUCE.md and SUBMISSION.md : 824 MB")
    print(f"  data/raw/ecfr/ alone                      : {fmt(ecfr_bytes)}")
    print(f"  data/raw/ (the whole tree)                : {fmt(total)}")
    print(f"  understatement                            : "
          f"{total - ecfr_bytes:,} B  ({total / ecfr_bytes:.2f}x)"
          if ecfr_bytes else "  data/raw/ecfr/ is absent")
    print(f"  REPRODUCE.md's own later table            : 1,443,366,993 B = 1.44 GB")
    print(f"  matches this measurement                  : "
          f"{'YES' if total == 1_443_366_993 else f'NO - measured {total:,} B'}")
    print()

    # --- and the third number, which looks like a fourth discrepancy and is not ---
    # CONTEXT.md section 8 says "49 titles, 824,289,052 B". That is 9,471 B less than
    # data/raw/ecfr/ measures. Traced rather than waved through:
    CONTEXT_ECFR_TITLES = 824_289_052
    titles = sorted(p for p in ecfr.glob("*.xml")) if ecfr.exists() else []
    title_bytes = sum(p.stat().st_size for p in titles)
    others = sorted(p for p in ecfr.iterdir() if p.is_file() and p.suffix != ".xml") \
        if ecfr.exists() else []
    print("AND THE THIRD NUMBER - CONTEXT.md section 8's 824,289,052 B")
    print("-" * 78)
    print(f"  data/raw/ecfr/*.xml            : {len(titles):>3} files  {title_bytes:>15,} B")
    for p in others:
        print(f"  {('data/raw/ecfr/' + p.name):<30} {'':>10}  {p.stat().st_size:>15,} B")
    print(f"  data/raw/ecfr/ total           : {ecfr_files:>3} files  {ecfr_bytes:>15,} B")
    print(f"  CONTEXT.md section 8 claims    :             {CONTEXT_ECFR_TITLES:>15,} B")
    print(f"  gap                            :             "
          f"{ecfr_bytes - CONTEXT_ECFR_TITLES:>15,} B")
    reconciled = title_bytes == CONTEXT_ECFR_TITLES
    print(f"  gap explained by the non-XML file(s) above : "
          f"{'YES - the XML titles alone match CONTEXT.md to the byte' if reconciled else 'NO'}")
    print()

    files, total_data = walk(DATA)
    print(f"data/ as a whole: {files:,} files, {fmt(total_data)}")
    frozen = total_data - walk(RAW)[1]
    print(f"data/ minus data/raw/ (the FROZEN, tracked corpus): {fmt(frozen)}")
    print()
    print("data/ was not modified by this script. It is opened read-only (hard rule 11).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
