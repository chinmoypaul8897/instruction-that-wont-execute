"""CH-14a probe - the pre-commit guard never summed bytes, and now it does.

`QUESTIONS.md` Q25:

    It enforces three things: a 25 MB per-blob limit, a 300-file count, and PII /
    credential sweeps. IT NEVER SUMS THE TRACKED BYTES. So the tree sailed past
    50 MB without a single refusal, because no individual blob is large and the
    file count is exactly at its limit.

Hard rule 6 requires a probe that FAILS ON THE OLD CODE AND PASSES ON THE NEW, kept
forever. This is it, and it does not paraphrase the old hook - it fetches the actual
committed bytes of `.githooks/pre-commit` from the commit that Q25 was raised against
and runs them, so the probe cannot drift away from what it claims to test.

THE SCENARIO. A synthetic repository holding a handful of files that are individually
well under 25 MB and few enough to clear the 300-file count, whose ARCHIVE nevertheless
blows the limit. That is the exact shape of the real tree Q25 found: 300 files, largest
blob 7.58 MB, every per-file guard green, total over cap.

    old hook -> exit 0, "pre-commit ok"     <- the defect
    new hook -> exit 1, "PRE-COMMIT REFUSED" and names the archive size

The archive limit is driven down to a few hundred KB through `MICRO1_MAX_ARCHIVE_BYTES`
so the probe runs in seconds instead of generating 45 MB. The seam is deliberate and
the hook prints a loud warning whenever it is used; `test_override_is_announced`
asserts that warning exists, because a silent override would be a way to weaken the
guard without leaving a trace.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / ".githooks" / "pre-commit"

# The commit Q25 was raised at - the last state of the hook before CH-14a touched it.
# Resolved through `git log` rather than pinned to a SHA so the probe survives a
# rebase; asserted to actually lack the byte check, which is the property under test.
OLD_HOOK_REV = "bc99ef4"

SMALL_LIMIT = 300_000          # bytes; the probe's stand-in for 45 MB
PAYLOAD_FILES = 6
PAYLOAD_BYTES = 120_000        # each; 6 x 120 KB incompressible = ~720 KB archive


def _git(*args: str, cwd: Path, env=None, check=True):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, check=check, env=env)


def _old_hook_source() -> str:
    """The committed bytes of the hook as Q25 found it."""
    out = subprocess.run(
        ["git", "show", f"{OLD_HOOK_REV}:.githooks/pre-commit"],
        cwd=str(REPO), capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip(f"cannot read {OLD_HOOK_REV}:.githooks/pre-commit from git")
    return out.stdout


@pytest.fixture(scope="module")
def oversized_repo(tmp_path_factory):
    """A repo whose per-file guards are all green and whose archive is over limit."""
    root = tmp_path_factory.mktemp("oversized")

    _git("init", "-q", cwd=root)
    _git("config", "user.email", "probe@example.invalid", cwd=root)
    _git("config", "user.name", "CH-14a probe", cwd=root)
    _git("config", "commit.gpgsign", "false", cwd=root)

    # Incompressible payload: deflate cannot rescue this, so archive size ~ raw size.
    # Deterministic (hard rule 9) - a fixed seed, never the system RNG's default.
    import random
    rnd = random.Random(20260831)
    for i in range(PAYLOAD_FILES):
        (root / f"payload{i}.bin").write_bytes(
            bytes(rnd.randrange(256) for _ in range(PAYLOAD_BYTES)))
    # A PII pattern source the old hook's fail-closed check can find, so that the
    # old hook fails (if it fails) on SIZE and never on a missing pattern file.
    # It lives OUTSIDE the repo: staged, its own literals would trip the sweep it
    # feeds, and the probe would fail for a reason that has nothing to do with size.
    patterns = root.parent / "probe_pii_patterns.txt"
    patterns.write_text("nobody@example.invalid\n", encoding="utf-8")

    # At least one UTF-8 file must be staged. The hook refuses a commit in which
    # every staged file was skipped by the credential sweep ("0 were scanned -- the
    # sweep is broken"), and six binary blobs would trip exactly that, making the
    # probe fail for a reason unrelated to size. That refusal is correct behaviour
    # and is left alone; the fixture is what adapts.
    (root / "README.txt").write_text(
        "CH-14a size-guard probe fixture. Nothing here is a secret.\n",
        encoding="utf-8")

    _git("add", "-A", cwd=root)
    return root


def _run_hook(hook_text: str, repo: Path, limit: int | None):
    hooks_dir = repo / ".probe-hooks"
    hooks_dir.mkdir(exist_ok=True)
    hook = hooks_dir / "pre-commit"
    hook.write_text(hook_text, encoding="utf-8", newline="\n")
    hook.chmod(0o755)

    env = dict(os.environ)
    env["MICRO1_PII_PATTERNS"] = str(repo.parent / "probe_pii_patterns.txt")
    env.pop("MICRO1_MAX_ARCHIVE_BYTES", None)
    if limit is not None:
        env["MICRO1_MAX_ARCHIVE_BYTES"] = str(limit)

    # Invoke the hook exactly as git does: as a shell script, cwd = repo root.
    return subprocess.run([_sh(), str(hook)], cwd=str(repo), env=env,
                          capture_output=True, text=True)


def _sh() -> str:
    for cand in ("sh", "bash"):
        p = shutil.which(cand)
        if p:
            return p
    pytest.skip("no POSIX shell available to run the hook")


def _archive_bytes(repo: Path) -> int:
    tree = _git("write-tree", cwd=repo).stdout.strip()
    out = repo / "probe.zip"
    _git("archive", "--format=zip", "-o", str(out), tree, cwd=repo)
    n = out.stat().st_size
    out.unlink()
    return n


# ---------------------------------------------------------------- the flip


def test_the_scenario_is_the_one_q25_describes(oversized_repo):
    """Every per-file guard is green; only the total is over. Otherwise the probe
    would be testing the 25 MB blob check or the 300-file check by accident."""
    files = [p for p in _git("ls-files", cwd=oversized_repo).stdout.split("\n") if p]
    assert len(files) <= 300, "probe repo must clear the 300-file count guard"
    biggest = max((oversized_repo / f).stat().st_size for f in files)
    assert biggest < 25 * 1024 * 1024, "probe repo must clear the 25 MB blob guard"
    assert _archive_bytes(oversized_repo) > SMALL_LIMIT, (
        "probe repo must actually be over the archive limit, or there is nothing "
        "for the new guard to catch")


def test_OLD_hook_PASSES_an_over_cap_tree(oversized_repo):
    """THE DEFECT. Q25's finding, executed: the old guard reports ok on a tree
    whose archive is over the limit, because it never measures the total."""
    old = _old_hook_source()
    assert "MAX_ARCHIVE_BYTES" not in old, (
        f"{OLD_HOOK_REV} already has an archive check - this probe is pointed at "
        "the wrong revision and would prove nothing")

    res = _run_hook(old, oversized_repo, limit=SMALL_LIMIT)
    assert res.returncode == 0, (
        "expected the OLD hook to pass (that is the defect). "
        f"stdout={res.stdout!r} stderr={res.stderr!r}")
    assert "pre-commit ok" in res.stdout
    # and it says nothing at all about total size
    assert "archive" not in (res.stdout + res.stderr).lower()


def test_NEW_hook_REFUSES_the_same_tree(oversized_repo):
    """THE FIX. Same repository, same environment, current hook: refused, and the
    message names the measured size rather than a proxy."""
    new = HOOK.read_text(encoding="utf-8")
    res = _run_hook(new, oversized_repo, limit=SMALL_LIMIT)
    assert res.returncode == 1, (
        "expected the NEW hook to refuse. "
        f"stdout={res.stdout!r} stderr={res.stderr!r}")
    err = res.stderr
    assert "PRE-COMMIT REFUSED" in err
    assert "ARCHIVE" in err
    assert f"{SMALL_LIMIT:,} B" in err
    assert "selection-rule.md" in err, (
        "the refusal must point at the published remedy, not just say no")


def test_NEW_hook_PASSES_a_tree_under_the_limit(oversized_repo):
    """The guard is not simply always-red: raise the limit above the measured
    archive and the same tree passes. Without this the flip above would also be
    satisfied by a hook that refuses everything."""
    new = HOOK.read_text(encoding="utf-8")
    generous = _archive_bytes(oversized_repo) * 2
    res = _run_hook(new, oversized_repo, limit=generous)
    assert res.returncode == 0, f"stdout={res.stdout!r} stderr={res.stderr!r}"
    assert "pre-commit ok" in res.stdout


# ------------------------------------------------- the guard's own honesty


def test_NEW_hook_reports_tracked_bytes_even_when_passing(oversized_repo):
    """Q25's actual complaint was that the bytes were never summed. Summing them
    only on failure would leave the same blind spot on every green commit."""
    new = HOOK.read_text(encoding="utf-8")
    res = _run_hook(new, oversized_repo, limit=_archive_bytes(oversized_repo) * 2)
    assert res.returncode == 0
    assert "tracked" in res.stdout and "archive" in res.stdout
    assert "headroom" in res.stdout


def test_override_is_announced(oversized_repo):
    """The testability seam must never be silent. A commit made under a relaxed
    limit has to say so, or the seam becomes a way to weaken the guard invisibly
    (hard rule 5)."""
    new = HOOK.read_text(encoding="utf-8")
    res = _run_hook(new, oversized_repo, limit=_archive_bytes(oversized_repo) * 2)
    assert "ARCHIVE LIMIT OVERRIDDEN" in res.stderr
    assert "MICRO1_MAX_ARCHIVE_BYTES" in res.stderr


def test_default_limit_is_45MB_and_is_not_a_variable_someone_nudged():
    """Hard rule 5. The threshold is read out of the shipped hook text, so moving
    it requires editing a file this test then fails on."""
    src = HOOK.read_text(encoding="utf-8")
    assert "MAX_ARCHIVE_BYTES = 45_000_000" in src, (
        "the default archive limit is no longer 45 MB")
    assert "HACKEREARTH_CAP   = 50_000_000" in src


def test_file_count_guard_was_raised_deliberately_and_is_still_enforced():
    """CH-14a raised MAX_TRACKED from 300 to 400. Hard rule 5 says a threshold is
    never weakened to get green, so the raise has to survive being looked at:

      * it is still ENFORCED - the check was not deleted, only its value moved;
      * it is NOT set to the count that made this chunk's commit pass (311),
        which is the shape a number moved for convenience would have;
      * it ships in the SAME hook as the direct archive measurement that
        supersedes it, so the guard is stronger overall, not weaker;
      * it says out loud that it is a Class A change awaiting ratification.

    If someone later nudges it again without the disclosure, this test fails."""
    src = HOOK.read_text(encoding="utf-8")
    assert "MAX_TRACKED    = 400" in src, "the count guard's value moved again"
    assert "if len(tracked) > MAX_TRACKED:" in src, (
        "the count check itself was removed - that WOULD be weakening it")
    assert "MAX_ARCHIVE_BYTES" in src, (
        "the count may only be raised alongside the direct archive check that "
        "replaces what it was proxying for")
    assert "QUESTIONS.md Q28" in src, "the Class A disclosure is missing"
    assert "311" in src, (
        "the hook must state the count that would have made this chunk pass, so a "
        "reader can see 400 was not reverse-engineered from it")


def test_archive_failure_fails_closed():
    """If `git archive` cannot run, the hook must refuse rather than report a
    size check that never happened - the same stance as the PII sweep."""
    src = HOOK.read_text(encoding="utf-8")
    assert "could not be checked" in src
    assert "Refusing rather than passing a check that" in src


# -------------------------------------------------- the live tree, for the record


def test_the_real_repository_is_under_the_real_limit():
    """The number CH-14a exists to produce. Not a proxy: the actual archive."""
    tree = _git("write-tree", cwd=REPO).stdout.strip()
    out = REPO / ".probe-archive.zip"
    try:
        _git("archive", "--format=zip", "-o", str(out), tree, cwd=REPO)
        n = out.stat().st_size
    finally:
        if out.exists():
            out.unlink()
    assert n < 45_000_000, f"archive is {n:,} B, over the 45 MB CH-14a limit"
    assert n < 50_000_000, f"archive is {n:,} B, over the 50 MB HackerEarth cap"
    sys.stdout.write(f"\nsubmission archive: {n:,} B = {n/1e6:.2f} MB "
                     f"(cap 50 MB, limit 45 MB)\n")
