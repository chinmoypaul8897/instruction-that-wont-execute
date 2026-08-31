#!/usr/bin/env python3
"""CH-11c — re-derive every figure the five factual corrections rest on.

Hard rule 14: any claim from data ships its generating script AND its committed
output. Hard rule 8/9: this script is pure — it reads the repository and the
frozen artifacts, makes no network call, no model call, and no clock or RNG
enters any published number.

Run from the repository root:

    python docs/evidence/ch11c-sweep/ch11c_verify.py

Every section prints its numbers whether or not they are zero, and each
assertion that decides a correction is printed as PASS/FAIL rather than left
implicit. A FAIL is a real result and is not suppressed.
"""

from __future__ import annotations

import collections
import csv
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
LEDGER = os.path.join(ROOT, "docs", "evidence", "runs", "cost_ledger.csv")
VOTES = os.path.join(ROOT, "docs", "evidence", "ch06-a1",
                     "B0prime-rep1-votes.json")
SCAN = os.path.join(ROOT, "docs", "evidence", "secret-scan", "scan.txt")
GOOD = os.path.join(ROOT, "GOOD.md")

FAILURES = []


def check(label, condition, detail=""):
    """Print a decision as PASS/FAIL. A FAIL is recorded, never swallowed."""
    tag = "PASS" if condition else "FAIL"
    print("  [%s] %s%s" % (tag, label, ("  -- " + detail) if detail else ""))
    if not condition:
        FAILURES.append(label)
    return condition


def rule(title):
    print("")
    print("=" * 78)
    print(title)
    print("=" * 78)


def git(*args):
    out = subprocess.run(["git"] + list(args), cwd=ROOT,
                         capture_output=True, text=True)
    return out.stdout


def read(path):
    return io.open(path, encoding="utf-8").read()


# ---------------------------------------------------------------------------
# 1. Q35 - which model ran which arm, and the total spend
# ---------------------------------------------------------------------------
def section_model():
    rule("1. Q35 - the model of every evaluation arm, from the ledger")

    rows = list(csv.DictReader(io.open(LEDGER, encoding="utf-8")))
    print("  ledger            : docs/evidence/runs/cost_ledger.csv")
    print("  rows              : %d" % len(rows))

    by = collections.Counter((r["model"], r["arm"]) for r in rows)
    print("")
    print("  rows by (model, arm) -- every group printed, none collapsed:")
    for (model, arm), n in sorted(by.items()):
        print("    %6d  %-28s %s" % (n, model, arm))

    # Which arms are evaluation arms? Everything that is not the model-id probe.
    eval_rows = [r for r in rows if r["arm"] != "probe-model-id"]
    eval_models = collections.Counter(r["model"] for r in eval_rows)
    sonnet_arms = sorted({r["arm"] for r in rows
                          if r["model"] == "claude-sonnet-5"})
    haiku_arms = sorted({r["arm"] for r in eval_rows
                         if r["model"] == "claude-haiku-4-5-20251001"})

    print("")
    print("  evaluation-arm rows by model:")
    for m, n in sorted(eval_models.items()):
        print("    %6d  %s" % (n, m))
    print("  arms on claude-haiku-4-5-20251001 : %s" % ", ".join(haiku_arms))
    print("  arms on claude-sonnet-5           : %s" % ", ".join(sonnet_arms))

    print("")
    withdrawn = {"B0-sonnet", "B0-agent-sonnet"}
    check("every non-sonnet evaluation arm runs claude-haiku-4-5-20251001",
          all(r["model"] == "claude-haiku-4-5-20251001"
              for r in eval_rows if r["arm"] not in withdrawn))
    check("claude-sonnet-5 appears ONLY on the withdrawn subset and the "
          "model-id probe",
          set(sonnet_arms) <= withdrawn | {"probe-model-id"},
          "arms = %s" % sonnet_arms)
    check("PROVENANCE.md no longer names sonnet as the model of every arm",
          "| Anthropic API (`claude-sonnet-5`) | commercial, per terms | "
          "every evaluation arm |" not in read(os.path.join(ROOT,
                                                            "PROVENANCE.md")))

    prov = read(os.path.join(ROOT, "PROVENANCE.md"))
    n_sonnet = sum(1 for ln in prov.splitlines() if "sonnet" in ln.lower())
    print("")
    print("  PROVENANCE.md lines mentioning 'sonnet' : %d" % n_sonnet)
    for ln in prov.splitlines():
        if "sonnet" in ln.lower():
            print("    | %s" % ln[:110])

    # -- the chunk card's own counts, checked rather than repeated (rule 15) --
    print("")
    print("  The chunk card claimed 19 haiku-naming / 4 sonnet-naming files")
    print("  under docs/evidence/. Measured over TRACKED files:")
    tracked = [p for p in git("ls-files", "docs/evidence").splitlines()
               if p.strip()]
    n_h = n_s = 0
    sonnet_files = []
    for rel in tracked:
        path = os.path.join(ROOT, rel)
        try:
            blob = io.open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "claude-haiku-4-5-20251001" in blob:
            n_h += 1
        if "claude-sonnet-5" in blob:
            n_s += 1
            sonnet_files.append(rel)
    print("    tracked files naming claude-haiku-4-5-20251001 : %d "
          "(card said 19)" % n_h)
    print("    tracked files naming claude-sonnet-5           : %d "
          "(card said 4)" % n_s)
    print("    the sonnet-naming files:")
    for rel in sonnet_files:
        print("      %s" % rel)
    check("the card's file counts do NOT reproduce, so they are not repeated "
          "(QUESTIONS.md Q37)", (n_h, n_s) != (19, 4),
          "measured %d / %d" % (n_h, n_s))


# ---------------------------------------------------------------------------
# 2. Q34 - B0-prime is not token-matched
# ---------------------------------------------------------------------------
def section_tokens():
    rule("2. Q34 - B0-prime against A1, in tokens and dollars")

    rows = list(csv.DictReader(io.open(LEDGER, encoding="utf-8")))
    per = collections.defaultdict(lambda: [0, 0, 0.0, 0])
    total = 0.0
    empty_cost_cells = 0
    for r in rows:
        usd = r["imputed_usd"].strip()
        if usd == "":
            empty_cost_cells += 1
        else:
            total += float(usd)
        a = per[r["arm"]]
        a[0] += int(r["input_tokens"] or 0)
        a[1] += int(r["output_tokens"] or 0)
        a[2] += float(usd or 0)
        a[3] += 1

    print("  %-24s %13s %11s %10s %7s" % ("arm", "input_tok", "output_tok",
                                          "usd", "rows"))
    for arm in sorted(per):
        v = per[arm]
        print("  %-24s %13d %11d %10.4f %7d" % (arm, v[0], v[1], v[2], v[3]))

    a1, bp, ba = per["A1"], per["B0prime"], per["B0-agent"]
    print("")
    print("  B0prime input / A1 input : %d / %d = %.4f"
          % (bp[0], a1[0], bp[0] / a1[0]))
    print("  B0prime usd   / A1 usd   : %.4f / %.4f = %.4f"
          % (bp[2], a1[2], bp[2] / a1[2]))
    print("  B0prime input / B0-agent input : %d / %d = %.4f"
          % (bp[0], ba[0], bp[0] / ba[0]))

    print("")
    check("A1 input tokens == 4,006,662", a1[0] == 4006662, str(a1[0]))
    check("B0prime input tokens == 1,377,402", bp[0] == 1377402, str(bp[0]))
    check("B0prime is NOT token-matched to A1 (ratio < 0.5)",
          bp[0] / a1[0] < 0.5, "%.4f" % (bp[0] / a1[0]))
    check("B0prime IS close to B0-agent's own three-rep input (0.8 - 1.2x)",
          0.8 <= bp[0] / ba[0] <= 1.2, "%.4f" % (bp[0] / ba[0]))

    print("")
    print("  rows with an EMPTY cost cell (unknown != free) : %d"
          % empty_cost_cells)
    print("  TOTAL imputed USD                              : %.4f" % total)
    check("API spend unchanged at USD 11.6323", abs(total - 11.6323) < 5e-5,
          "%.4f" % total)
    check("spend is under the USD 18.00 ceiling", total < 18.0)

    # every editable shipping file must be free of the mislabel
    print("")
    for name in ("README.md", "CHANGELOG.md"):
        text = read(os.path.join(ROOT, name))
        bad = [ln for ln in text.splitlines()
               if "compute-match" in ln.lower()
               and "was not run" not in ln
               and "was never run" not in ln
               and "->" not in ln
               and "→" not in ln]
        check("%s carries no surviving 'compute-matched' label" % name,
              not bad, "%d line(s)" % len(bad))
        for ln in bad:
            print("      | %s" % ln[:110])


# ---------------------------------------------------------------------------
# 3. Q33 - the B0-prime sample-disagreement count
# ---------------------------------------------------------------------------
def section_votes():
    rule("3. Q33 - how many B0-prime items had samples that disagreed")

    votes = json.load(io.open(VOTES, encoding="utf-8"))
    sys.path.insert(0, ROOT)
    from src.score import normalise_verdict  # noqa: E402

    raw = sum(1 for v in votes.values() if len(set(v)) > 1)
    norm = sum(1 for v in votes.values()
               if len({normalise_verdict(x) for x in v}) > 1)
    parseable = 0
    for v in votes.values():
        got = [normalise_verdict(x) for x in v]
        got = [g for g in got if g in ("WILL_EXECUTE", "WILL_FAIL")]
        if len(set(got)) > 1:
            parseable += 1

    print("  artifact : docs/evidence/ch06-a1/B0prime-rep1-votes.json")
    print("  items    : %d" % len(votes))
    print("")
    print("  reading                                                  count")
    print("  raw sample strings not all equal                         %5d"
          % raw)
    print("  same after src/score.py::normalise_verdict               %5d"
          % norm)
    print("  parseable votes disagree, non-answers dropped            %5d"
          % parseable)

    print("")
    check("items == 82", len(votes) == 82, str(len(votes)))
    check("raw reading == 22", raw == 22, str(raw))
    check("normalised reading == 22", norm == 22, str(norm))
    check("parseable-only reading == 8", parseable == 8, str(parseable))
    check("no reading gives 26 -- the changelog's old figure",
          26 not in (raw, norm, parseable))

    chlog = read(os.path.join(ROOT, "CHANGELOG.md"))
    check("CHANGELOG.md's Final row no longer asserts 26",
          "while 26 items had samples that disagreed with each other."
          not in chlog)
    check("CHANGELOG.md's Final row cites the votes artifact",
          "B0prime-rep1-votes.json" in chlog)


# ---------------------------------------------------------------------------
# 4. Q31 - the secret sweep's scope, and why two figures exist
# ---------------------------------------------------------------------------
def section_scan():
    rule("4. Q31 - the secret sweep's scope, both committed versions")

    print("  Every committed revision of docs/evidence/secret-scan/scan.txt,")
    print("  newest first, with the scope each one printed:")
    print("")
    shas = [s for s in git("log", "--format=%H", "--",
                           "docs/evidence/secret-scan/scan.txt").split()
            if s]
    seen = []
    for sha in shas:
        blob = git("show", "%s:docs/evidence/secret-scan/scan.txt" % sha)
        repo = commits = blobs = "?"
        for ln in blob.splitlines():
            if ln.startswith("repository"):
                repo = ln.split(":", 1)[1].strip()
            elif ln.startswith("commits"):
                commits = ln.split(":", 1)[1].strip()
            elif "blobs in history" in ln:
                blobs = ln.split()[-1]
        print("    commit %s  repository %s  commits %s  blobs %s"
              % (sha[:7], repo[:12], commits, blobs))
        seen.append((sha[:7], commits, blobs))

    print("")
    live = read(SCAN)
    print("  The LIVE artifact says:")
    for ln in live.splitlines():
        if (ln.startswith("repository") or ln.startswith("commits")
                or "blobs in history" in ln or ln.startswith("VERDICT")):
            print("    %s" % ln.strip())

    print("")
    check("the live artifact says 84 commits", "commits       : 84" in live)
    check("the live artifact says 462 blobs",
          "blobs in history           462" in live)
    check("the verdict is PASS with 0 findings",
          "VERDICT: PASS - 0 findings." in live)
    check("an EARLIER committed revision really printed 450 / 81 -- so the "
          "stale summaries were not invented",
          any(c == "81" and b == "450" for _, c, b in seen),
          "revisions seen: %s" % seen)

    for name in ("STATUS.md", "AI-USE.md", "SUBMISSION.md", "SAFETY.md"):
        text = read(os.path.join(ROOT, name))
        stale = [ln for ln in text.splitlines()
                 if ("450 blob" in ln or "450 text" in ln)
                 and "read" not in ln and "0f3f4fe" not in ln]
        check("%s states no un-annotated 450-blob scope" % name, not stale,
              "%d line(s)" % len(stale))
        for ln in stale:
            print("      | %s" % ln[:110])


# ---------------------------------------------------------------------------
# 5. Q32 - what GOOD.md section 11 actually says
# ---------------------------------------------------------------------------
def section_good():
    rule("5. Q32 - GOOD.md section 11, quoted from the frozen file")

    text = read(GOOD)
    start = text.index("## 11. Which eval set")
    end = text.index("## 12. Standing constraints")
    body = text[start:end].rstrip()
    for ln in body.splitlines():
        print("  | %s" % ln)

    print("")
    check("GOOD.md section 11 names data/evalset/ as Primary",
          "**Primary: `data/evalset/`" in body)
    check("GOOD.md section 11 does NOT name the restricted set as primary",
          "Primary: `data/evalset-restricted/" not in body)
    check("GOOD.md section 11 mentions the restricted set only as committed "
          "and flippable",
          "`data/evalset-restricted/` (1 pair, n = 2) is committed" in body)

    prereg = read(os.path.join(ROOT, "docs", "evidence", "ch03-evalset",
                               "pre-registration.md"))
    check("the restricted-primary pre-registration is in "
          "docs/evidence/ch03-evalset/pre-registration.md section 2",
          "the **restricted** set is the primary\neval set" in prereg)

    # GOOD.md must not have been edited by this chunk
    diff = git("diff", "--stat", "--", "GOOD.md").strip()
    check("GOOD.md is unmodified in the working tree (it is frozen)",
          diff == "", diff or "clean")

    q = read(os.path.join(ROOT, "QUESTIONS.md"))
    check("the Q19 ruling's original text survives verbatim and untouched",
          q.count("GOOD.md\npre-registered the RESTRICTED set as primary; "
                  "the restricted set yields ONE pair\nand measures "
                  "nothing.") == 1)
    check("a dated correction is appended beneath it",
          "### CORRECTION TO THE Q19 RULING" in q)

    # the pair counts the decision actually rests on
    print("")
    for label, rel in (("restricted", "data/evalset-restricted/items.jsonl"),
                       ("unrestricted", "data/evalset/items.jsonl")):
        n = sum(1 for ln in io.open(os.path.join(ROOT, rel),
                                    encoding="utf-8") if ln.strip())
        print("  %-13s %-42s items = %3d  pairs = %3d"
              % (label, rel, n, n // 2))
    n_r = sum(1 for ln in io.open(
        os.path.join(ROOT, "data/evalset-restricted/items.jsonl"),
        encoding="utf-8") if ln.strip())
    n_u = sum(1 for ln in io.open(
        os.path.join(ROOT, "data/evalset/items.jsonl"),
        encoding="utf-8") if ln.strip())
    check("the restricted set yields ONE pair -- the fact the ruling's "
          "substance rests on", n_r // 2 == 1, "%d pairs" % (n_r // 2))
    check("the unrestricted set yields 41 pairs / n = 82",
          (n_u // 2, n_u) == (41, 82), "%d pairs / n = %d" % (n_u // 2, n_u))


def main():
    print("CH-11c VERIFICATION -- every figure the five corrections rest on")
    print("repository HEAD : %s" % git("rev-parse", "HEAD").strip())
    print("no network, no model call, no clock, no RNG in any number below")

    section_model()
    section_tokens()
    section_votes()
    section_scan()
    section_good()

    rule("RESULT")
    if FAILURES:
        print("  %d CHECK(S) FAILED -- shipped as failures, not suppressed:"
              % len(FAILURES))
        for f in FAILURES:
            print("    - %s" % f)
        return 1
    print("  ALL CHECKS PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
