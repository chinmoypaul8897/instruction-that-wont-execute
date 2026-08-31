"""CH-14a step 3 - the clean-clone rehearsal, re-runnable.

Answers one question: **does the thing a judge actually receives work?**

Three environments, in increasing distance from the build machine:

    1. the build machine        - has data/raw/ (git-ignored, 824 MB of XML)
    2. a fresh `git clone`      - has no data/raw/, no venv, no caches
    3. an EXTRACTED `git archive --format=zip` - not even a git repository

(3) is the one that matters. A judge downloads a zip and unzips it. If the
published numbers reproduce from (2) but not (3), the submission is broken in the
only environment that counts, and CH-14a says to report that immediately and stop.

WHAT IS CHECKED IN EACH
  * the SHA-256 manifest verifies                      (refetch.py --verify-only)
  * Tier-1 replay reproduces the published headlines   EXACTLY:
        checkpoint  gap +18.3 pp,  McNemar p = 0.0059
        A1          0.7195 vs B0-agent 0.6585,  p = 0.4244
        API spend   USD 11.6323
  * the regenerated result files are BYTE-IDENTICAL to the committed ones
  * the test suite runs

NETWORK. Every command runs with the proxy variables pointed at a closed port, and
the script PROVES the block by attempting `https://www.govinfo.gov/` and requiring
the attempt to fail before it will continue. Nothing here is taken on trust; a
rehearsal that claims "network off" without demonstrating it is the vacuous pass
this project exists to expose.

NO MODEL CALLS. Every arm is replayed from committed artefacts. API spend at the end
of this script is identical to API spend at the start.

    python docs/evidence/ch14-clean-clone/rehearse.py <workdir> [--python <exe>]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HEADLINES = [
    ("checkpoint gap", "gap       +18.3 pp"),
    ("checkpoint McNemar", "McNemar   p = 0.0059"),
    ("checkpoint branch", "BRANCH: GREEN"),
    ("A1 accuracy", "accuracy 0.7195   gap +6.1 pp"),
    ("A1 McNemar", "McNemar exact two-sided p = 0.4244"),
    ("B0-agent baseline", "A1  vs  B0-agent 0.6585"),
    ("API spend", "TOTAL                                                11.6323"),
]

RESULT_FILES = [
    "docs/evidence/checkpoint/checkpoint-result.txt",
    "docs/evidence/checkpoint/checkpoint-result.json",
    "docs/evidence/ch06-a1/a1-result.txt",
    "docs/evidence/ch06-a1/a1-result.json",
]

OFFLINE = {
    "http_proxy": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9",
    "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
    "no_proxy": "", "NO_PROXY": "",
}


def sh(*a: str, cwd=None) -> str:
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True,
                          errors="replace").stdout


def env_offline() -> dict:
    e = dict(os.environ)
    e.update(OFFLINE)
    return e


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(py: str, script: str, cwd: Path, out: Path) -> int:
    r = subprocess.run([py, script], cwd=str(cwd), env=env_offline(),
                       capture_output=True, text=True, errors="replace")
    out.write_text(r.stdout + r.stderr, encoding="utf-8")
    return r.returncode


def check_headlines(text: str, w) -> bool:
    ok = True
    for label, needle in HEADLINES:
        hit = needle in text
        ok = ok and hit
        w(f"    {'MATCH  ' if hit else 'MISSING'}  {label:<22} {needle!r}\n")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir")
    ap.add_argument("--python", default=sys.executable,
                    help="interpreter for the clone/extraction (a fresh venv)")
    args = ap.parse_args()

    repo = Path(sh("git", "rev-parse", "--show-toplevel").strip())
    work = Path(args.workdir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    py = args.python
    w = sys.stdout.write

    w("=" * 78 + "\n")
    w("CH-14a CLEAN-CLONE REHEARSAL\n")
    w("=" * 78 + "\n\n")
    w(f"source repo   : {repo}\n")
    w(f"commit        : {sh('git', 'rev-parse', 'HEAD').strip()}\n")
    w(f"interpreter   : {py}\n")
    ver = sh(py, "-V").strip() or sh(py, "--version").strip()
    w(f"python        : {ver}\n")
    pkgs = sh(py, "-m", "pip", "list", "--format=freeze").strip().replace("\n", ", ")
    w(f"installed     : {pkgs}\n")
    w("                NOTE: there is NO requirements.txt in this repository.\n")
    w("                CH-14a section 3 asks for a venv built from a pinned one.\n")
    w("                QUESTIONS.md Q29 records its absence. The dependency set was\n")
    w("                MEASURED instead: stdlib + pytest, nothing else. src/apiclient\n")
    w("                .py uses urllib, so there is no requests and no vendor SDK.\n\n")

    # ---------------------------------------------------- prove the network is off
    w("-" * 78 + "\n")
    w("NETWORK OFF - demonstrated, not asserted\n")
    w("-" * 78 + "\n")
    probe = subprocess.run(
        [py, "-c", "import urllib.request;urllib.request.urlopen("
                   "'https://www.govinfo.gov/',timeout=5)"],
        env=env_offline(), capture_output=True, text=True)
    if probe.returncode == 0:
        w("  REFUSED: the network is REACHABLE, so an offline claim would be false.\n")
        return 2
    last = [l for l in probe.stderr.strip().split("\n") if l.strip()][-1]
    w(f"  outbound to govinfo.gov blocked: {last[:100]}\n")
    w(f"  proxy vars: {OFFLINE['http_proxy']} (closed port)\n\n")

    results: dict[str, bool] = {}

    # ---------------------------------------------------------------- 2. the clone
    clone = work / "clone"
    if clone.exists():
        shutil.rmtree(clone, ignore_errors=True)
    w("-" * 78 + "\n")
    w("ENVIRONMENT 2 - a fresh `git clone`\n")
    w("-" * 78 + "\n")
    subprocess.run(["git", "clone", "-q", str(repo), str(clone)], check=True)
    w(f"  cloned to           {clone}\n")
    w(f"  tracked files       {len(sh('git','ls-files',cwd=clone).strip().splitlines())}\n")
    w(f"  data/raw present    {(clone/'data'/'raw').exists()}"
      "   (False is correct - it is git-ignored)\n")

    # ------------------------------------------------------------ 3. the extraction
    zpath = work / "submission.zip"
    subprocess.run(["git", "archive", "--format=zip", "-o", str(zpath), "HEAD"],
                   cwd=str(repo), check=True)
    fromzip = work / "fromzip"
    if fromzip.exists():
        shutil.rmtree(fromzip, ignore_errors=True)
    fromzip.mkdir(parents=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(fromzip)
        n_entries = len(z.namelist())
    zsize = zpath.stat().st_size
    w("\n" + "-" * 78 + "\n")
    w("ENVIRONMENT 3 - the EXTRACTED zip. THIS IS WHAT A JUDGE OPENS.\n")
    w("-" * 78 + "\n")
    w(f"  zip                 {zsize:,} B = {zsize/1e6:.2f} MB "
      f"(cap 50 MB, CH-14a limit 45 MB)\n")
    w(f"  entries             {n_entries}\n")
    w(f"  extracted to        {fromzip}\n")
    w(f"  is a git repo       {(fromzip/'.git').exists()}"
      "   (False - a plain directory, as received)\n\n")

    for label, root in (("CLONE", clone), ("EXTRACTION", fromzip)):
        w("=" * 78 + "\n")
        w(f"REPLAY IN THE {label}\n")
        w("=" * 78 + "\n")

        r = subprocess.run([py, "refetch.py", "--verify-only"], cwd=str(root),
                           env=env_offline(), capture_output=True, text=True)
        vlines = [l.strip() for l in r.stdout.split("\n") if "verify" in l]
        okc = sum(int(l.split("/")[0]) for l in vlines if "/" in l)
        tot = sum(int(l.split("/")[1].split()[0]) for l in vlines if "/" in l)
        w(f"  manifest verify     {okc}/{tot} files, exit {r.returncode}\n")
        results[f"{label}:manifest"] = (r.returncode == 0 and okc == tot and tot > 0)

        cp = run(py, "docs/evidence/checkpoint/analyse_checkpoint.py", root,
                 work / f"{label.lower()}-checkpoint.txt")
        a1 = run(py, "docs/evidence/ch06-a1/analyse_a1.py", root,
                 work / f"{label.lower()}-a1.txt")
        combined = ((work / f"{label.lower()}-checkpoint.txt").read_text(encoding="utf-8")
                    + (work / f"{label.lower()}-a1.txt").read_text(encoding="utf-8"))
        w(f"  analyse_checkpoint  exit {cp}\n")
        w(f"  analyse_a1          exit {a1}\n")
        w("  headline numbers, matched as literal strings:\n")
        results[f"{label}:headlines"] = check_headlines(combined, w) and cp == 0 and a1 == 0

        w("  regenerated files vs the COMMITTED ones:\n")
        allsame = True
        for rel in RESULT_FILES:
            a, b = sha256(repo / rel), sha256(root / rel)
            same = a == b
            allsame = allsame and same
            w(f"    {'IDENTICAL' if same else 'DIFFERS  '}  {a[:16]}  {rel}\n")
        results[f"{label}:byte-identical"] = allsame

        t = subprocess.run([py, "-m", "pytest", "-q"], cwd=str(root),
                           env=env_offline(), capture_output=True, text=True)
        tail = [l for l in t.stdout.strip().split("\n") if l.strip()][-1]
        w(f"  pytest              {tail}\n")
        results[f"{label}:tests"] = (t.returncode == 0)
        w("\n")

    w("=" * 78 + "\n")
    w("VERDICT\n")
    w("=" * 78 + "\n")
    for k in sorted(results):
        w(f"  {'PASS' if results[k] else 'FAIL'}  {k}\n")
    ok = all(results.values())
    w("\n")
    if ok:
        w("  ALL PASS. The published headline numbers reproduce EXACTLY from the\n")
        w("  extracted zip, offline, on a fresh interpreter, and the regenerated\n")
        w("  result files are byte-identical to the committed ones (hard rule 9).\n")
    else:
        w("  FAILURES ABOVE. CH-14a: a replay that fails from the EXTRACTION is the\n")
        w("  most important finding of the day - report it immediately and stop.\n")
    w("=" * 78 + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
