"""CH-14a step 1e - the guard probe, both states printed verbatim.

Hard rule 6: every fix ships a probe that FAILS ON THE OLD CODE AND PASSES ON THE NEW,
and BOTH ARE SHOWN. `tests/test_size_guard.py` asserts the flip; this script is the
same flip printed for a reader who is not going to run pytest.

It builds one synthetic repository whose per-file guards are all green - no blob near
25 MB, far under 300 files - and whose ARCHIVE is over limit, then runs two hooks
against it: the committed bytes of `.githooks/pre-commit` from the commit Q25 was
raised at, and the current one.

No network, no clock. The payload is seeded (20260831) so the sizes below reproduce.

    python docs/evidence/ch14-size/guard_probe.py > docs/evidence/ch14-size/guard-probe.txt
"""
from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OLD_HOOK_REV = "bc99ef4"
SMALL_LIMIT = 300_000
PAYLOAD_FILES = 6
PAYLOAD_BYTES = 120_000


def git(*args: str, cwd: Path, check: bool = True):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, check=check)


def main() -> int:
    repo_root = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()).stdout.strip())
    hook_new = (repo_root / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    old = subprocess.run(["git", "show", f"{OLD_HOOK_REV}:.githooks/pre-commit"],
                         cwd=str(repo_root), capture_output=True, text=True)
    if old.returncode != 0:
        print(f"cannot read {OLD_HOOK_REV}:.githooks/pre-commit", file=sys.stderr)
        return 2
    hook_old = old.stdout

    sh = shutil.which("sh") or shutil.which("bash")
    if not sh:
        print("no POSIX shell", file=sys.stderr)
        return 2

    print("=" * 78)
    print("CH-14a GUARD PROBE - QUESTIONS.md Q25, executed")
    print("=" * 78)
    print()
    print("THE DEFECT, in Q25's words:")
    print('  "It enforces three things: a 25 MB per-blob limit, a 300-file count,')
    print('   and PII / credential sweeps. IT NEVER SUMS THE TRACKED BYTES."')
    print()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "probe-repo"
        root.mkdir()
        git("init", "-q", cwd=root)
        git("config", "user.email", "probe@example.invalid", cwd=root)
        git("config", "user.name", "CH-14a probe", cwd=root)

        rnd = random.Random(20260831)
        for i in range(PAYLOAD_FILES):
            (root / f"payload{i}.bin").write_bytes(
                bytes(rnd.randrange(256) for _ in range(PAYLOAD_BYTES)))
        (root / "README.txt").write_text(
            "CH-14a size-guard probe fixture. Nothing here is a secret.\n",
            encoding="utf-8")
        patterns = Path(td) / "probe_pii_patterns.txt"
        patterns.write_text("nobody@example.invalid\n", encoding="utf-8")
        git("add", "-A", cwd=root)

        tree = git("write-tree", cwd=root).stdout.strip()
        zp = Path(td) / "probe.zip"
        git("archive", "--format=zip", "-o", str(zp), tree, cwd=root)
        arc = zp.stat().st_size
        files = [p for p in git("ls-files", cwd=root).stdout.split("\n") if p]
        biggest = max((root / f).stat().st_size for f in files)

        print("THE SYNTHETIC TREE - every per-file guard green, only the total over:")
        print(f"  tracked files        {len(files):>12,}   (limit 300)")
        print(f"  largest blob         {biggest:>12,} B (limit 26,214,400)")
        print(f"  ARCHIVE              {arc:>12,} B")
        print(f"  archive limit        {SMALL_LIMIT:>12,} B  "
              f"<- the probe's stand-in for 45,000,000")
        print(f"  OVER BY              {arc - SMALL_LIMIT:>12,} B")
        print()
        print("  (The limit is driven down through MICRO1_MAX_ARCHIVE_BYTES so the")
        print("   probe runs in seconds instead of generating 45 MB of payload. The")
        print("   hook announces the override on stderr; that announcement is itself")
        print("   asserted by tests/test_size_guard.py::test_override_is_announced.)")
        print()

        hooks = Path(td) / "hooks"
        hooks.mkdir()

        def run(text: str) -> subprocess.CompletedProcess:
            h = hooks / "pre-commit"
            h.write_text(text, encoding="utf-8", newline="\n")
            h.chmod(0o755)
            env = dict(os.environ)
            env["MICRO1_PII_PATTERNS"] = str(patterns)
            env["MICRO1_MAX_ARCHIVE_BYTES"] = str(SMALL_LIMIT)
            return subprocess.run([sh, str(h)], cwd=str(root), env=env,
                                  capture_output=True, text=True)

        for label, text, expect in (
            (f"OLD hook, as committed at {OLD_HOOK_REV} - THE DEFECT", hook_old, 0),
            ("NEW hook, .githooks/pre-commit as it now stands - THE FIX", hook_new, 1),
        ):
            res = run(text)
            print("-" * 78)
            print(label)
            print("-" * 78)
            print(f"  exit code : {res.returncode}   "
                  f"(expected {expect}: "
                  f"{'PASS - it never measured the total' if expect == 0 else 'REFUSE'})")
            for stream, name in ((res.stdout, "stdout"), (res.stderr, "stderr")):
                for line in stream.rstrip("\n").split("\n"):
                    if line:
                        print(f"  {name} | {line}")
            print()
            if res.returncode != expect:
                print("  *** PROBE DID NOT FLIP AS EXPECTED ***")
                return 1

    print("=" * 78)
    print("THE FLIP: old hook exit 0 on an over-cap tree; new hook exit 1 on the")
    print("same tree, naming the measured archive size. Hard rule 6 satisfied.")
    print()
    print("Note what the OLD hook printed: 'pre-commit ok ... largest blob under")
    print("25 MB'. A green report about a proxy, on a tree that breaches the real")
    print("constraint. That is this project's thesis, found in its own tooling.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
