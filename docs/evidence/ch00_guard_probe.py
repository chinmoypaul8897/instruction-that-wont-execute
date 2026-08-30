"""Positive control for the CH-00 guards. Run: python docs/evidence/ch00_guard_probe.py

A guard that passes on clean input proves nothing -- a guard that scans zero
files also passes. This project exists to make that argument, so its own guards
have to answer it.

Each case below feeds the guard something it MUST refuse, and asserts the
refusal. The .githooks/pre-commit checks run inside a throwaway git repo in the
OS temp directory, driven through a real `git commit`, so the hook is exercised
the way git actually invokes it -- never against this repository's index.

Every value here is synthetic. The operator's real contact details are not in
this file, and cannot be: a document that quotes the value in order to test its
removal is a new copy of the leak.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

FAKE_PHONE = "+91 90000 00001"
FAKE_PHONE_PLAIN = "919000000001"
FAKE_EMAIL = "not-a-real-person@example.invalid"
FAKE_ANTHROPIC_KEY = "sk-ant-api03-" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
# Split so the literal never appears in this file: the pre-commit hook
# refuses AKIA-shaped tokens in staged files and it was right to refuse this
# one. Weakening the guard with an allowlist to let its own test through is
# exactly the move hard rule 5 forbids. The assembled value is identical.
FAKE_AWS = "AKIA" + "IOSFODNN7EXAMPLE"

results: list[tuple[str, str, bool, str]] = []


def record(case, expectation, passed, detail=""):
    results.append((case, expectation, passed, detail))


def run(cwd, *args, env=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


# ===========================================================================
# Part 1 - .githooks/pre-commit
# ===========================================================================
def probe_hook():
    hook_src = (REPO / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="ch00-guard-") as td:
        outer = Path(td)
        # The pattern file must live OUTSIDE the work tree. Keeping it inside
        # made `git add -A` stage the synthetic PII, and the hook duly refused
        # the "clean" case -- the guard was right and the probe was wrong.
        tmp = outer / "repo"
        tmp.mkdir()
        run(tmp, "git", "init", "-q", "-b", "main")
        run(tmp, "git", "config", "user.name", "probe")
        run(tmp, "git", "config", "user.email", "probe@example.invalid")
        (tmp / ".githooks").mkdir()
        hookfile = tmp / ".githooks" / "pre-commit"
        hookfile.write_text(hook_src, encoding="utf-8", newline="\n")
        os.chmod(hookfile, 0o755)
        run(tmp, "git", "config", "core.hooksPath", ".githooks")

        patterns = outer / "patterns.txt"
        patterns.write_text(f"{FAKE_EMAIL}\ncontact {FAKE_PHONE}\n", encoding="utf-8")
        env = dict(os.environ, MICRO1_PII_PATTERNS=str(patterns))

        def commit(msg, env=env):
            run(tmp, "git", "add", "-A")
            return run(tmp, "git", "commit", "-m", msg, env=env)

        # -- A: clean file must be ACCEPTED (guards against a guard that always fails)
        (tmp / "clean.txt").write_text("nothing interesting here\n", encoding="utf-8")
        r = commit("clean")
        record("A. clean file", "ACCEPT", r.returncode == 0,
               (r.stdout + r.stderr).strip().splitlines()[-1][:90] if (r.stdout or r.stderr) else "")

        # -- B: operator phone must be REFUSED
        (tmp / "leak1.md").write_text(f"call me on {FAKE_PHONE} any time\n", encoding="utf-8")
        r = commit("phone")
        ok = r.returncode != 0 and "operator contact detail" in (r.stderr + r.stdout)
        record("B. operator phone staged", "REFUSE", ok, _first_bullet(r))
        run(tmp, "git", "reset", "-q"); (tmp / "leak1.md").unlink()

        # -- C: operator email must be REFUSED
        (tmp / "leak2.md").write_text(f"reach {FAKE_EMAIL} for details\n", encoding="utf-8")
        r = commit("email")
        ok = r.returncode != 0 and "operator contact detail" in (r.stderr + r.stdout)
        record("C. operator email staged", "REFUSE", ok, _first_bullet(r))
        run(tmp, "git", "reset", "-q"); (tmp / "leak2.md").unlink()

        # -- D: credential-shaped token must be REFUSED
        (tmp / "cfg.py").write_text(f'KEY = "{FAKE_ANTHROPIC_KEY}"\n', encoding="utf-8")
        r = commit("key")
        ok = r.returncode != 0 and "anthropic key" in (r.stderr + r.stdout)
        record("D. anthropic key staged", "REFUSE", ok, _first_bullet(r))
        run(tmp, "git", "reset", "-q"); (tmp / "cfg.py").unlink()

        # -- E: AWS key id must be REFUSED
        (tmp / "aws.txt").write_text(f"id={FAKE_AWS}\n", encoding="utf-8")
        r = commit("aws")
        ok = r.returncode != 0 and "aws key id" in (r.stderr + r.stdout)
        record("E. aws key id staged", "REFUSE", ok, _first_bullet(r))
        run(tmp, "git", "reset", "-q"); (tmp / "aws.txt").unlink()

        # -- F: blob over 25 MB must be REFUSED
        big = tmp / "corpus.bin"
        with open(big, "wb") as fh:
            fh.write(b"x" * (26 * 1024 * 1024))
        r = commit("big")
        ok = r.returncode != 0 and "over 25 MB" in (r.stderr + r.stdout)
        record("F. 26 MB blob staged", "REFUSE", ok, _first_bullet(r))
        run(tmp, "git", "reset", "-q"); big.unlink()

        # -- G: NO pattern source at all must FAIL CLOSED, not pass vacuously
        blind = dict(os.environ, MICRO1_PII_PATTERNS=str(outer / "does-not-exist.txt"),
                     HOME=str(outer / "no-home"), USERPROFILE=str(outer / "no-home"))
        (tmp / "ordinary.txt").write_text("harmless\n", encoding="utf-8")
        r = commit("blind", env=blind)
        ok = r.returncode != 0 and "could not run" in (r.stderr + r.stdout)
        record("G. no PII pattern source", "REFUSE (fail closed)", ok, _first_bullet(r))
        run(tmp, "git", "reset", "-q")


def _first_bullet(r):
    for line in (r.stderr + r.stdout).splitlines():
        if line.strip().startswith("*"):
            return line.strip()[:110]
    return ((r.stderr + r.stdout).strip().splitlines() or [""])[-1][:110]


# ===========================================================================
# Part 2 - tools/export_session.py scrubber
# ===========================================================================
def probe_scrubber():
    from export_session import scrub, REDACT_CRED, REDACT_PII

    pii = [
        re.compile(re.escape(FAKE_EMAIL), re.IGNORECASE),
        re.compile(r"\+?\s*" + r"[\s\-()]*".join(FAKE_PHONE_PLAIN)),
    ]
    home = str(Path.home())
    sample = "\n".join([
        f'{{"cwd": "{home}\\\\micro1 engineering challenge"}}',
        f'{{"text": "key is {FAKE_ANTHROPIC_KEY}"}}',
        f'{{"text": "aws {FAKE_AWS}"}}',
        f'{{"text": "ANTHROPIC_API_KEY=abcdefghijklmnopqrstuvwx"}}',
        f'{{"ANTHROPIC_API_KEY": "zyxwvutsrqponmlkjihgfedcba"}}',
        f'{{"text": "ping {FAKE_PHONE} or {FAKE_EMAIL}"}}',
        '{"text": "Bearer abcdefghijklmnopqrstuvwxyz012345"}',
    ])
    cleaned, counts = scrub(sample, pii)

    checks = [
        ("H. home path -> ~", counts["home path -> ~"] > 0 and home not in cleaned),
        ("I. anthropic key", counts["credential: anthropic key"] > 0
         and FAKE_ANTHROPIC_KEY not in cleaned),
        ("J. aws key id", counts["credential: aws key id"] > 0 and FAKE_AWS not in cleaned),
        ("K. bearer token", counts["credential: bearer token"] > 0),
        ("L. KEY=value", counts["env value: KEY=value"] > 0
         and "abcdefghijklmnopqrstuvwx" not in cleaned),
        ("M. json KEY", counts["env value: json KEY"] > 0
         and "zyxwvutsrqponmlkjihgfedcba" not in cleaned),
        ("N. operator contact", counts["operator contact detail"] >= 2
         and FAKE_EMAIL not in cleaned and FAKE_PHONE not in cleaned),
    ]
    for name, ok in checks:
        record(name, "REDACT", ok, "")

    record("O. scrubbed output still JSONL", "VALID",
           all(_json_ok(l) for l in cleaned.splitlines() if l.strip()), "")

    # negative control: ordinary prose must survive untouched
    plain = "The AMDPAR names section 433.2 and the anchor is (b)(4)(i)(A)."
    out, c = scrub(plain, pii)
    record("P. ordinary text left alone", "NO CHANGE",
           out == plain and sum(c.values()) == 0, "")


def _json_ok(line):
    import json
    try:
        json.loads(line)
        return True
    except Exception:
        return False


def main():
    probe_hook()
    probe_scrubber()

    print("CH-00 GUARD PROBE - every case feeds the guard something it must refuse")
    print("=" * 78)
    print(f"{'case':<34}{'expected':<22}{'result'}")
    print("-" * 78)
    for case, exp, ok, detail in results:
        print(f"{case:<34}{exp:<22}{'PASS' if ok else '*** FAIL ***'}")
        if detail:
            print(f"{'':<34}{detail}")
    print("-" * 78)
    n_pass = sum(1 for *_, ok, _ in ((c, e, o, d) for c, e, o, d in results) if ok)
    print(f"{n_pass}/{len(results)} guard probes behaved as required")
    print("success + failure == n :",
          n_pass + (len(results) - n_pass) == len(results))
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
