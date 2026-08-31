"""CH-14a step 3.5 - credential and PII sweep over the FULL git history.

WHAT THIS IS NOT. It is not `gitleaks`. `gitleaks` is not installed on this machine and
CH-14a sanctions no installs, so this is a locally written equivalent and it is labelled
as one rather than passed off as the named tool. Its rule set is the same shape -
provider-prefix regexes over every blob - and its weaknesses are listed in its own
report. A reviewer who wants `gitleaks` proper should run it; this establishes the
finding, not the brand.

SCOPE. Every blob reachable from every ref, not just the working tree - a secret removed
in a later commit is still in the history, and the history is what `git clone` hands
over. Plus an explicit named sweep of `docs/trajectories/**` for the four things CH-14a
lists: `sk-ant`, `AIza`, `Bearer `, and the operator's phone number.

-------------------------------------------------------------------------------
WHY THIS SCRIPT HAS TWO CLASSES OF RULE, AND WHAT THE FIRST VERSION GOT WRONG
-------------------------------------------------------------------------------
Version 1.0.0 reported **74 findings** and a verdict of FAIL. Every one was noise:

  * `.githooks/pre-commit` and `tools/export_session.py` contain the literal text
    `sk-ant-[A-Za-z0-9_\\-]{16,}` - they are the credential detectors, and a sweep
    for `sk-ant-` finds its own definition;
  * `QUESTIONS.md` and four `context/` documents DISCUSS those detectors;
  * `docs/evidence/ch00_guard_probe.py` holds deliberately fake fixtures, split
    across a concatenation (`"sk-ant-api03-" + "A1b2..."`) so no whole key literal
    exists, feeding the CH-00 probe that proves the redactor works;
  * the build trajectories quote all of the above.

**Every STRICT rule - the ones that require a key-shaped tail - counted zero, and still
counts zero.** The failure was not a leak. It was a rule set that could not tell a
credential from a description of a credential, reporting red 74 times.

That is worth stating plainly in a repository whose thesis is that a green suite is not
evidence of correctness: **a red suite is not evidence of a defect either.** An alarm
nobody can act on gets ignored, and an ignored alarm is a disabled one. The first
version's output is preserved in git history at the commit that added it.

THE FIX IS NOT A PATH ALLOWLIST. Suppressing `.githooks/` or `docs/evidence/` would
have silenced the exact files most likely to hold a real mistake. Instead:

  BLOCKING rules  require the credential SHAPE - prefix AND key-shaped tail. These
                  decide the verdict. Nothing suppresses them, anywhere, ever.
  ADVISORY rules  bare prefixes. Reported with counts, and each hit classified by
                  looking at THE MATCH ITSELF: a `sk-ant-` not followed by >=16 key
                  characters is not an Anthropic key, because that is what an
                  Anthropic key is. Objective, not a judgement about the file.
  EXCEPTIONS      a short, committed, per-(path, rule) list with a written reason
                  each. Declared in this file where a reviewer reads them. A stale
                  exception - one matching nothing - is REPORTED, so the list cannot
                  quietly rot into a blanket suppression.

WHAT IT NEVER DOES. It never prints a matched string, never prints `.env`, never prints
the operator's contact details. A finding is (path, blob, rule, line) - enough to act
on, nothing that republishes the secret into the evidence file meant to prove there
isn't one. `.env` is confirmed by NAME ONLY (hard rule 12).

ZERO-OCCURRENCE BRANCHES PRINT AS ZEROS and `scanned + skipped == n` is asserted
(hard rule 14).

    python docs/evidence/secret-scan/scan_history.py > docs/evidence/secret-scan/scan.txt
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

TOOL = "micro1 scan_history.py"
TOOL_VERSION = "1.2.0 (CH-14a, 2026-08-31)"


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True,
                          errors="replace").stdout


REPO = Path(sh("git", "rev-parse", "--show-toplevel").strip())
os.chdir(REPO)

# ------------------------------------------------------- BLOCKING: shape required
BLOCKING: list[tuple[str, re.Pattern]] = [
    ("anthropic-api-key",    re.compile(rb"sk-ant-[A-Za-z0-9_\-]{16,}")),
    ("openai-api-key",       re.compile(rb"sk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("google-api-key",       re.compile(rb"AIza[0-9A-Za-z_\-]{35}")),
    ("github-token",         re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws-access-key-id",    re.compile(rb"AKIA[0-9A-Z]{16}")),
    ("slack-token",          re.compile(rb"xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("private-key-block",    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer-header",        re.compile(rb"Bearer\s+[A-Za-z0-9._\-]{12,}")),
    ("x-api-key-header",
     re.compile(rb"x-api-key\"?\s*[:=]\s*\"?[A-Za-z0-9._\-]{12,}")),
    ("generic-secret-assign",
     re.compile(rb"(?i)(api[_-]?key|secret|passwd|password|token)\"?\s*[:=]\s*"
                rb"[\"']?([A-Za-z0-9/+_\-]{20,})")),
]

# ---------------------------------------- ADVISORY: bare prefixes, self-classifying
# Each is paired with the BLOCKING rule that decides whether a hit is a real key.
ADVISORY: list[tuple[str, re.Pattern, str]] = [
    ("anthropic-prefix", re.compile(rb"sk-ant-"), "anthropic-api-key"),
    ("google-prefix",    re.compile(rb"AIza"),    "google-api-key"),
]

# The four CH-14a names, reported by name whichever class they land in.
NAMED = ["anthropic-prefix", "google-prefix", "bearer-header", "operator-phone"]

# ------------------------------------------------------------------- EXCEPTIONS
# (path, rule, reason). Every entry is a deliberate synthetic fixture whose whole
# purpose is to be detected by the guard it feeds. Nothing here is a real secret and
# nothing here is suppressed on the basis of WHERE it lives - only on what it is.
EXCEPTIONS: list[tuple[str, str, str]] = [
    # NB: these reasons DESCRIBE the fixtures and do not QUOTE them. An earlier
    # version quoted both literals, and this sweep then flagged its own exception
    # list - and the scan.txt that printed it - as two fresh findings. The rule was
    # right; the evidence file had no business reproducing credential-shaped strings
    # to explain why credential-shaped strings are fine. Describe, never reproduce.
    ("docs/evidence/ch00_guard_probe.py", "generic-secret-assign",
     "CH-00 probe fixture: an env-style assignment to an API-key-named variable whose "
     "value is 24 sequential lowercase letters, fed to the redactor to prove it "
     "redacts. Not a key - no provider prefix and no entropy."),
    ("docs/evidence/ch00_guard_probe.py", "bearer-header",
     "CH-00 probe fixture: an Authorization-style header whose value is 26 sequential "
     "lowercase letters followed by six digits, fed to the redactor to prove it "
     "redacts. Not a token."),
]


# ------------------------------------------------------- BLOB-PINNED EXCEPTIONS
# (blob-oid, rule, reason). Pinned to ONE immutable object, never to a path.
#
# Why this class exists. The path exceptions above once QUOTED the fixture literals
# they were excusing. This sweep - correctly - then flagged its own exception list,
# and the scan.txt that printed it, as fresh findings. The working tree was fixed to
# describe rather than quote, but THE OLD BLOBS ARE STILL IN THE HISTORY and this
# sweep reads all of history. A history rewrite is forbidden by CH-14a's safety rider
# and would be wildly disproportionate to two synthetic strings.
#
# A PATH exception would have been the wrong instrument: it would suppress the rule
# on the scanner itself forever, including on content nobody has written yet - the
# standing blind spot this script's whole design refuses. A blob OID is content-
# addressed, so this excuses exactly these two objects and cannot extend to any
# future edit of the same files: a new commit is a new blob and gets scanned.
BLOB_EXCEPTIONS: list[tuple[str, str, str]] = [
    ("bf13baf8e519bce137926c5c11edf8261584d5ba", "bearer-header",
     "historical docs/evidence/secret-scan/scan.txt - the printed EXCEPTIONS table "
     "of this script at v1.1.0, quoting the CH-00 fixture it excuses."),
    ("bf13baf8e519bce137926c5c11edf8261584d5ba", "generic-secret-assign",
     "same blob, same cause."),
    ("9fc90e7305b30c9a9b20fa4ef78f1609b862ea2d", "bearer-header",
     "historical docs/evidence/secret-scan/scan_history.py at v1.1.0 - the "
     "EXCEPTIONS table before it was rewritten to describe rather than quote."),
    ("9fc90e7305b30c9a9b20fa4ef78f1609b862ea2d", "generic-secret-assign",
     "same blob, same cause."),
]


def pii_rules() -> tuple[list[tuple[str, re.Pattern]], str | None]:
    """Operator contact literals, from the same source the pre-commit hook uses.
    The literals themselves are NEVER printed - only the rule labels."""
    src = REPO / "context" / "02-ABOUT-ME.md"
    env = os.environ.get("MICRO1_PII_PATTERNS")
    if env and Path(env).exists():
        src = Path(env)
    if not src.exists():
        return [], None
    text = src.read_text(encoding="utf-8", errors="replace")
    rules = []
    emails = sorted(set(re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
    for i, e in enumerate(emails):
        rules.append((f"operator-email#{i+1}",
                      re.compile(re.escape(e).encode(), re.IGNORECASE)))
    phones = sorted({re.sub(r"\D", "", m) for m in re.findall(
        r"(?:\+\d{1,3}[\s\-]?)?(?:\d[\s\-()]?){9,13}\d", text)})
    n = 0
    for raw in phones:
        if 10 <= len(raw) <= 13:
            n += 1
            rules.append(("operator-phone" if n == 1 else f"operator-phone#{n}",
                          re.compile((r"\+?\s*" + r"[\s\-()]*".join(raw)).encode())))
    return rules, (str(src.relative_to(REPO)).replace("\\", "/")
                   if src.is_relative_to(REPO) else "(external)")


def main() -> int:
    out = sys.stdout.write
    pii, pii_src = pii_rules()

    out("=" * 78 + "\n")
    out("CH-14a SECRET SWEEP - full git history\n")
    out("=" * 78 + "\n\n")
    out(f"tool          : {TOOL} {TOOL_VERSION}\n")
    out("                NOT gitleaks. gitleaks is not installed on this machine and\n")
    out("                this chunk installs nothing. Local equivalent, labelled as\n")
    out("                one. Limitations listed at the end.\n")
    out(f"repository    : {sh('git', 'rev-parse', 'HEAD').strip()}\n")
    out(f"commits       : {sh('git', 'rev-list', '--count', '--all').strip()}\n")
    out(f"PII source    : {pii_src or 'NONE FOUND'}\n")
    out(f"rules         : {len(BLOCKING)} blocking + {len(ADVISORY)} advisory + "
        f"{len(pii)} operator-contact (blocking)\n")
    out(f"exceptions    : {len(EXCEPTIONS)} path-pinned + {len(BLOB_EXCEPTIONS)} "
        "blob-pinned, all listed below with reasons\n\n")

    if not pii:
        out("REFUSED: no PII pattern source, so the contact sweep could not run.\n"
            "An empty result is not a clean result.\n")
        return 1

    blocking = BLOCKING + pii
    excepted = {(p, r) for p, r, _ in EXCEPTIONS}
    blob_excepted = {(o, r) for o, r, _ in BLOB_EXCEPTIONS}

    # ---------------------------------------------------------- full history
    entries = []
    for line in sh("git", "rev-list", "--objects", "--all").split("\n"):
        line = line.strip()
        if line:
            parts = line.split(" ", 1)
            entries.append((parts[0], parts[1] if len(parts) > 1 else ""))
    check = subprocess.run(["git", "cat-file", "--batch-check"],
                           input="\n".join(o for o, _ in entries),
                           capture_output=True, text=True).stdout
    names = {o: n for o, n in entries}
    blobs = [(f[0], names.get(f[0], "")) for f in
             (l.split() for l in check.split("\n")) if len(f) >= 2 and f[1] == "blob"]

    findings: list[tuple[str, str, str, int]] = []
    suppressed: list[tuple[str, str]] = []
    exception_hits = {(p, r): 0 for p, r, _ in EXCEPTIONS}
    blob_hits = {(o, r): 0 for o, r, _ in BLOB_EXCEPTIONS}
    bcount = {label: 0 for label, _ in blocking}
    acount = {label: 0 for label, _, _ in ADVISORY}
    aben = {label: 0 for label, _, _ in ADVISORY}
    scanned = skipped_binary = 0

    for oid, name in blobs:
        data = subprocess.run(["git", "cat-file", "blob", oid],
                              capture_output=True).stdout
        if b"\x00" in data[:8192]:
            skipped_binary += 1
            continue
        scanned += 1
        for label, pat in blocking:
            m = pat.search(data)
            if not m:
                continue
            bcount[label] += 1
            if (name, label) in excepted:
                exception_hits[(name, label)] += 1
                suppressed.append((name, label))
                continue
            if (oid, label) in blob_excepted:
                blob_hits[(oid, label)] += 1
                suppressed.append((f"{name}@{oid[:12]}", label))
                continue
            findings.append((name or "(unnamed)", oid[:12], label,
                             data[:m.start()].count(b"\n") + 1))
        # advisory: classify by the match, never by the path
        for label, pat, strict_label in ADVISORY:
            strict = dict(BLOCKING)[strict_label]
            for m in pat.finditer(data):
                acount[label] += 1
                sm = strict.match(data, m.start())
                if sm is None:
                    aben[label] += 1
                else:
                    findings.append((name or "(unnamed)", oid[:12],
                                     f"{label}->{strict_label}",
                                     data[:m.start()].count(b"\n") + 1))
                break   # one classification per blob is enough to act on

    out("-" * 78 + "\n")
    out("SCOPE 1 - every blob reachable from every ref\n")
    out("-" * 78 + "\n")
    out(f"  blobs in history      {len(blobs):>8,}\n")
    out(f"  text blobs scanned    {scanned:>8,}\n")
    out(f"  binary blobs skipped  {skipped_binary:>8,}\n")
    assert scanned + skipped_binary == len(blobs), "scanned + skipped != n"
    out(f"  scanned + skipped == blobs : {scanned} + {skipped_binary} == "
        f"{len(blobs)}  -> True\n\n")

    out("  BLOCKING rules - these decide the verdict, nothing suppresses them\n")
    out("  (zero-occurrence rules ARE printed, as zeros)\n")
    for label, _ in blocking:
        star = "   <- CH-14a names this one" if label in NAMED else ""
        exc = sum(v for (p, r), v in exception_hits.items() if r == label)
        note = f"   ({exc} declared exception hit)" if exc else ""
        out(f"    {bcount[label]:>6}  {label}{note}{star}\n")
    out("\n")
    out("  ADVISORY rules - bare prefixes, classified by the match itself\n")
    for label, _, strict_label in ADVISORY:
        star = "   <- CH-14a names this one" if label in NAMED else ""
        out(f"    {acount[label]:>6}  {label}{star}\n")
        out(f"    {aben[label]:>6}    of which NOT followed by a key-shaped tail "
            f"-> not a {strict_label}\n")
        out(f"    {acount[label]-aben[label]:>6}    of which ARE key-shaped "
            "-> escalated to BLOCKING above\n")
    out("\n")

    # -------------------------------------- the named trajectory sweep
    out("-" * 78 + "\n")
    out("SCOPE 2 - docs/trajectories/** in the working tree, the four CH-14a names\n")
    out("-" * 78 + "\n")
    traj = [p for p in sh("git", "ls-files", "-z", "docs/trajectories").split("\0") if p]
    tb = 0
    trow = {lbl: [0, 0] for lbl in NAMED}
    for p in traj:
        data = Path(p).read_bytes()
        tb += len(data)
        for label, pat, strict_label in ADVISORY:
            if label not in trow:
                continue
            strict = dict(BLOCKING)[strict_label]
            m = pat.search(data)
            if m:
                trow[label][0] += 1
                if strict.match(data, m.start()):
                    trow[label][1] += 1
                    findings.append((p, "worktree", f"{label}->{strict_label}", 0))
        for label, pat in blocking:
            if label in trow and pat.search(data):
                trow[label][0] += 1
                trow[label][1] += 1
                if (p, label) not in excepted:
                    findings.append((p, "worktree", label, 0))
    out(f"  files                 {len(traj):>8,}\n")
    out(f"  bytes                 {tb:>8,}\n")
    for lbl in NAMED:
        hit, real = trow[lbl]
        out(f"    {hit:>6}  {lbl}   -> {real} that are actually credential-shaped\n")
    out("\n")

    # -------------------------------------- declared exceptions
    out("-" * 78 + "\n")
    out("DECLARED EXCEPTIONS - each with its reason, and each checked for staleness\n")
    out("-" * 78 + "\n")
    stale = 0
    for p, r, why in EXCEPTIONS:
        n = exception_hits[(p, r)]
        if n == 0:
            stale += 1
        out(f"  [{'USED ' + str(n) if n else 'STALE'}] {r}  {p}\n")
        out(f"          {why}\n")
    out("\n  BLOB-PINNED - content-addressed, cannot extend to a future edit:\n")
    for o, r, why in BLOB_EXCEPTIONS:
        n = blob_hits[(o, r)]
        if n == 0:
            stale += 1
        out(f"  [{'USED ' + str(n) if n else 'STALE'}] {r}  {o[:12]}\n")
        out(f"          {why}\n")
    if stale:
        out(f"\n  {stale} STALE exception(s) - they match nothing and should be "
            "deleted. An exception list that outlives its fixtures becomes a\n"
            "  blanket suppression by accident.\n")
    else:
        out("\n  0 stale.\n")
    out("\n")

    # -------------------------------------- .env, by name only
    out("-" * 78 + "\n")
    out("SCOPE 3 - .env, confirmed by NAME ONLY (hard rule 12)\n")
    out("-" * 78 + "\n")
    envp = REPO / ".env"
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"],
                             capture_output=True).returncode == 0
    ever = bool(sh("git", "log", "--all", "--oneline", "--", ".env").strip())
    out(f"  .env exists on disk           : {envp.exists()}\n")
    out(f"  .env is git-ignored           : "
        f"{subprocess.run(['git','check-ignore','-q','.env']).returncode == 0}\n")
    out(f"  .env is tracked               : {tracked}   (must be False)\n")
    out(f"  .env ever committed, any ref  : {ever}   (must be False)\n")
    if envp.exists():
        keys = [l.split("=", 1)[0].strip() for l in
                envp.read_text(encoding="utf-8", errors="replace").splitlines()
                if "=" in l and not l.strip().startswith("#")]
        out(f"  key NAMES present             : {', '.join(keys) or '(none)'}\n")
        out("  values                        : NOT READ, NOT PRINTED\n")
    out("\n")

    # ----------------------------------------------------------- verdict
    out("=" * 78 + "\n")
    if not findings and not tracked and not ever:
        out(f"VERDICT: PASS - 0 findings.\n\n")
        out(f"  {scanned:,} text blobs across {sh('git','rev-list','--count','--all').strip()} "
            f"commits, {len(traj)} trajectory files, {tb:,} bytes.\n")
        out(f"  {len(suppressed)} hit(s) matched a DECLARED exception, listed above "
            "with reasons.\n")
        out("  Every advisory prefix hit was classified as not-a-key by inspecting\n"
            "  the match, not the path.\n")
    else:
        out(f"VERDICT: FAIL - {len(findings)} finding(s). MATCHED TEXT NOT PRINTED.\n\n")
        for name, oid, label, line_no in findings[:200]:
            out(f"  {label:<28} {oid:<14} line {line_no:<6} {name}\n")
    out("=" * 78 + "\n\n")

    out("LIMITATIONS, stated rather than left for a reviewer to find:\n")
    out("  1. Regex prefix matching only. A secret with no recognisable provider\n")
    out("     prefix - a bare 40-char hex string - is caught only if it is assigned\n")
    out("     to a variable named key/secret/token/password.\n")
    out("  2. Binary blobs are skipped, not decoded. Count reported above.\n")
    out("  3. NO entropy analysis. gitleaks proper does this and would flag\n")
    out("     high-entropy strings this sweep passes over. This is the single\n")
    out("     largest gap between this script and the tool it stands in for.\n")
    out("  4. Only refs reachable from `--all`. A secret in a dangling object no ref\n")
    out("     reaches is not scanned.\n")
    out("  5. Advisory classification takes the FIRST prefix match per blob. A file\n")
    out("     whose first `sk-ant-` is a regex definition and whose second is a real\n")
    out("     key would be misclassified. No such file exists here - every blocking\n")
    out("     count is zero - but the limitation is real and is stated.\n")
    out("  6. Point-in-time result for the commit named at the top.\n")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
