"""Hard rule 9, demonstrated rather than asserted: same inputs -> byte-identical output.

Rebuilds every CH-03 artefact into a THROWAWAY directory and compares SHA-256 against
the committed freeze. Nothing under `data/` is touched.

The network is not needed: every annual-edition volume the eval set uses is already in
the git-ignored `data/raw/cfr/`, and the volume index is cached beside it. If a volume
is missing the script says so and exits non-zero rather than silently rebuilding a
smaller corpus and calling the hashes different.

    python docs/evidence/ch03-evalset/ch03_determinism.py
    # committed output: ch03-determinism.txt
"""
from __future__ import annotations

import io
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import attribute_v11 as v11  # noqa: E402
import eval_set as evalset  # noqa: E402
from attribute_amdpars import sha256_file  # noqa: E402

OUT = Path(__file__).resolve().parent
BUILDS = [
    ("data/attribution-v11", lambda d: v11.main(
        ["remeasure", "--raw", str(REPO / "data/raw/fr"), "--out", d])),
    ("data/evalset", lambda d: evalset.main(
        ["build", "--out", d, "--raw", str(REPO / "data/raw/cfr"), "--floor", "0.0"])),
    ("data/evalset-restricted", lambda d: evalset.main(
        ["build", "--out", d, "--raw", str(REPO / "data/raw/cfr"), "--floor", "0.90"])),
]


def main() -> int:
    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 78)
    p("CH-03 DETERMINISM - rebuild into a temp dir, compare SHA-256 (hard rule 9)")
    p("=" * 78)
    p("")
    failures = 0
    tmp_root = Path(tempfile.mkdtemp(prefix="ch03-determinism-"))
    try:
        for committed, build in BUILDS:
            src = REPO / committed
            if not src.exists():
                p(f"  MISSING committed freeze: {committed}")
                failures += 1
                continue
            dest = tmp_root / Path(committed).name
            # silence the builder's own report; only the hashes matter here
            buf, real = io.StringIO(), sys.stdout
            sys.stdout = buf
            try:
                rc = build(str(dest))
            finally:
                sys.stdout = real
            if rc != 0:
                p(f"  {committed}: builder returned {rc}")
                failures += 1
                continue
            p(f"  {committed}")
            for f in sorted(src.iterdir()):
                if f.name == "manifest.json":
                    # the manifest hashes the others; comparing it compares them all,
                    # but it is listed separately so a reader sees it was checked
                    pass
                g = dest / f.name
                if not g.exists():
                    p(f"    MISSING  {f.name}")
                    failures += 1
                    continue
                a, b = sha256_file(f), sha256_file(g)
                same = a == b
                failures += 0 if same else 1
                p(f"    {'OK  ' if same else 'DIFF'}  {f.name:<26} {a}")
                if not same:
                    p(f"          rebuilt {b}")
            p("")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    p("=" * 78)
    p(f"  {'DETERMINISTIC - every artefact reproduces byte-for-byte' if not failures else f'{failures} MISMATCH(ES)'}")
    p("=" * 78)
    io.open(OUT / "ch03-determinism.txt", "w", encoding="utf-8",
            newline="\n").write(w.getvalue())
    print(w.getvalue(), end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
