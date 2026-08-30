"""Capture this Claude Code BUILD/REVIEW session's transcript into the repo.

Deliverable 4 asks for "representative trajectories for EVERY agent you used."
Three classes of agent run on this project:

  research/ideation agents  ~90 agents across four design workflows   context/*-raw.json
  CODING agents             the Claude Code sessions that write this  <- THIS SCRIPT
  solution agents           the evaluation arms                       src/runlog.py

The middle row is the one that is easy to lose. Those transcripts already
contain, verbatim, deliverable 4's own checklist -- the agent instructions,
every tool call, every tool response, every retry and every human interruption
-- and they live OUTSIDE the repo in ~/.claude/projects/, where Claude Code
rotates and prunes them. Capturing them is the difference between claiming
agent use and evidencing it.

    python tools/export_session.py CH-00
    python tools/export_session.py CH-02 --session-id <uuid>
    python tools/export_session.py CH-00 --dry-run

Writes docs/trajectories/build/<CHUNK-ID>.jsonl and prints byte and line counts.

SCRUBBING. The transcript is a verbatim recording, so it is scrubbed before it
enters the repo:
  * absolute home paths      -> ~
  * credential-shaped tokens -> [redacted - credential]
  * KEY=value / "KEY": "..." for secret-looking key names -> value redacted
  * the operator's phone and personal email -> [redacted - operator contact
    detail, ground rule 08], sourced the same way the pre-commit hook sources
    them (see pii_sources()); never hard-coded here, because a file that lists
    the value in order to remove it is a new copy of the leak.

Counts of every substitution are printed. Zero-occurrence categories print as
an explicit 0 (hard rule 14) -- a scrubber that silently matched nothing looks
exactly like a scrubber that worked.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "trajectories" / "build"
PROJECT_SLUG = "c--Users-chinm-micro1-engineering-challenge"
SESSION_ROOT = Path.home() / ".claude" / "projects" / PROJECT_SLUG

REDACT_CRED = "[redacted - credential]"
REDACT_PII = "[redacted - operator contact detail, ground rule 08]"

# Credential shapes. Deliberately broad: a false positive costs one unreadable
# token in a transcript, a false negative publishes a live key.
CREDENTIAL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{16,}")),
    ("openai key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("google key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack token", re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

# KEY=value and "KEY": "value" for key names that look like secrets. This is
# how a .env value actually reaches a transcript, and it needs no read of .env.
SECRET_KEY_NAME = r"[A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*"
ENVISH_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("KEY=value", re.compile(rf"(?m)\b({SECRET_KEY_NAME})=([^\s\"'\\]{{8,}})")),
    ("json KEY", re.compile(rf"\"({SECRET_KEY_NAME})\"\s*:\s*\"([^\"]{{8,}})\"")),
]

HOME_PATTERNS = [
    re.compile(re.escape(str(Path.home())), re.IGNORECASE),
    re.compile(re.escape(str(Path.home()).replace("\\", "\\\\")), re.IGNORECASE),
    re.compile(re.escape(str(Path.home()).replace("\\", "/")), re.IGNORECASE),
    re.compile(r"/c/Users/[A-Za-z0-9._-]+", re.IGNORECASE),
    re.compile(r"/home/[A-Za-z0-9._-]+"),
]


def pii_sources() -> list[Path]:
    """Where the operator's literal contact details may be read from.

    Never a tracked file. First hit wins. Identical order to .githooks/pre-commit
    so the exporter and the hook can never disagree about what counts as PII.
    """
    out = []
    env = os.environ.get("MICRO1_PII_PATTERNS")
    if env:
        out.append(Path(env))
    out.append(Path.home() / ".config" / "micro1" / "pii_patterns.txt")
    out.append(REPO / "context" / "02-ABOUT-ME.md")   # git-ignored dossier
    return out


def load_pii_literals() -> tuple[list[re.Pattern], str]:
    """(compiled patterns, source description). Empty list if no source exists."""
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone_re = re.compile(r"(?:\+\d{1,3}[\s\-]?)?(?:\d[\s\-()]?){9,13}\d")
    for src in pii_sources():
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        pats: list[re.Pattern] = []
        for e in sorted(set(email_re.findall(text))):
            pats.append(re.compile(re.escape(e), re.IGNORECASE))
        for raw in sorted({re.sub(r"\D", "", m) for m in phone_re.findall(text)}):
            if 10 <= len(raw) <= 13:
                pats.append(re.compile(r"\+?\s*" + r"[\s\-()]*".join(raw)))
        if pats:
            return pats, str(src)
    return [], "NONE FOUND"


def find_session(session_id: str | None) -> Path:
    if not SESSION_ROOT.exists():
        sys.exit(f"FATAL: no session directory at {SESSION_ROOT}")
    if session_id:
        p = SESSION_ROOT / f"{session_id}.jsonl"
        if not p.exists():
            sys.exit(f"FATAL: no transcript {p}")
        return p
    files = sorted(SESSION_ROOT.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit(f"FATAL: no *.jsonl transcripts under {SESSION_ROOT}")
    print("  candidates (newest last):")
    for f in files[-4:]:
        print(f"    {f.name}  {f.stat().st_size:>12,} B")
    print("  -> picked the newest by mtime. Pass --session-id to override.")
    return files[-1]


def scrub(text: str, pii: list[re.Pattern]) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    n = 0
    for pat in HOME_PATTERNS:
        text, k = pat.subn("~", text)
        n += k
    counts["home path -> ~"] = n

    for label, pat in CREDENTIAL_PATTERNS:
        text, k = pat.subn(REDACT_CRED, text)
        counts[f"credential: {label}"] = k

    for label, pat in ENVISH_PATTERNS:
        text, k = pat.subn(lambda m: m.group(0).replace(m.group(2), REDACT_CRED), text)
        counts[f"env value: {label}"] = k

    n = 0
    for pat in pii:
        text, k = pat.subn(REDACT_PII, text)
        n += k
    counts["operator contact detail"] = n
    return text, counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("chunk_id", help="e.g. CH-00")
    ap.add_argument("--session-id", default=os.environ.get("CLAUDE_SESSION_ID"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = find_session(args.session_id)
    print(f"source : {src}")

    raw = src.read_text(encoding="utf-8", errors="replace")
    lines_in = raw.count("\n")

    pii, pii_src = load_pii_literals()
    if not pii:
        print("WARNING: no operator PII source found -- contact details were NOT "
              "scrubbed by literal match. Credential and home-path scrubbing still "
              "ran. Checked: " + ", ".join(str(p) for p in pii_sources()),
              file=sys.stderr)
    else:
        print(f"pii src: {pii_src}  ({len(pii)} literal patterns, values never printed)")

    cleaned, counts = scrub(raw, pii)

    print("substitutions (0 is printed explicitly - hard rule 14):")
    for k in sorted(counts):
        print(f"    {counts[k]:>5}  {k}")

    bad = 0
    for i, line in enumerate(cleaned.splitlines(), 1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            if bad <= 3:
                print(f"    WARNING: line {i} is not valid JSON after scrubbing",
                      file=sys.stderr)
    print(f"    {bad:>5}  lines that stopped being valid JSON")

    out = OUT_DIR / f"{args.chunk_id}.jsonl"
    if args.dry_run:
        print(f"DRY RUN: would write {out} "
              f"({len(cleaned.encode('utf-8')):,} B, {cleaned.count(chr(10)):,} lines)")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(cleaned)

    size = out.stat().st_size
    lines_out = cleaned.count("\n")
    print(f"wrote  : {out}")
    print(f"bytes  : {size:,}")
    print(f"lines  : {lines_out:,}  (source had {lines_in:,})")
    if size > 25 * 1024 * 1024:
        print("WARNING: over the 25 MB pre-commit limit; the hook will reject it.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
