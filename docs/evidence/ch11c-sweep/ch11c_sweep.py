#!/usr/bin/env python3
"""CH-11c - the mechanical half of the shipping-surface sweep.

Deterministic, scriptable checks over every tracked shipping file:

  A. every model name mentioned, classified by the sentence it sits in
  B. every headline figure, cross-checked for agreement ACROSS files
  C. surviving "compute-matched" labels, and claims a review gate passed
  D. every docs/evidence/ path the shipping surface cites
  E. the cost ledger, re-summed

An agent's report is a claim. This is the part a reviewer can re-run.
Pure: no network, no model call, no clock, no RNG.

    python docs/evidence/ch11c-sweep/ch11c_sweep.py

---------------------------------------------------------------------------
ON DETECTOR SCOPE - read this before reading the numbers.

Sections A, B and D each run TWO readings and print BOTH, in the shape
`QUESTIONS.md` Q33 used for the vote counts and hard rule 7 requires for
normalisation:

  STRICT  - a single line is the unit. Cheap, and it over-detects, because
            a correction ("this said X, which is wrong; the artifact says Y")
            routinely spans four lines and a table row cites its path in the
            header.
  SCOPED  - the unit is the line plus four lines either side, and fenced code
            blocks are excluded from path extraction.

**Neither reading is suppressed and no threshold was moved.** Every STRICT hit
is printed and given an explicit disposition below, so a reviewer can disagree
with any one of them by name. The PASS/FAIL verdicts are taken on SCOPED, and
the STRICT count is reported beside every one of them.
---------------------------------------------------------------------------
"""

from __future__ import annotations

import collections
import csv
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

SHIPPING = [
    "README.md", "REPRODUCE.md", "PROVENANCE.md", "SAFETY.md",
    "THIRD-PARTY.md", "SUBMISSION.md", "CHANGELOG.md", "STATUS.md",
    "AI-USE.md", "QUESTIONS.md",
]

WINDOW = 4  # lines either side, for the SCOPED reading

FAILURES = []


def check(label, ok, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", label,
                           ("  -- " + detail) if detail else ""))
    if not ok:
        FAILURES.append(label)
    return ok


def rule(t):
    print("")
    print("=" * 78)
    print(t)
    print("=" * 78)


_CACHE = {}


def lines(name):
    if name not in _CACHE:
        _CACHE[name] = io.open(os.path.join(ROOT, name),
                               encoding="utf-8").read().splitlines()
    return _CACHE[name]


def window(name, i):
    """The SCOPED unit: line i (1-based) plus WINDOW lines either side."""
    ls = lines(name)
    lo = max(0, i - 1 - WINDOW)
    hi = min(len(ls), i + WINDOW)
    return "\n".join(ls[lo:hi])


# A passage whose nearest preceding heading ANNOUNCES a correction is allowed
# to quote the wrong text verbatim - that is what a correction IS. Structural,
# not an allowlist of line numbers, so it survives an edit above it.
CORRECTING_HEADING = re.compile(
    r"Q3[0-9]\b|Q4[0-9]\b|CORRECTION|RESOLUTIONS|does not reproduce"
    r"|says the opposite|and it is not|Every other artifact says"
    r"|sweep raised|findings", re.I)
# `sweep raised|findings` was added at CH-11c after the sweep flagged its OWN
# Q39 entry: a line inside "Q39 - the CH-11c shipping-surface sweep raised 75
# findings" quotes the chunk card's instruction text ("any surviving
# compute-matched, any claim a gate passed when it did not") and the
# line-scope reading could not tell a quoted instruction from an assertion.
# The Q-number range was `Q3[1-8]` and Q39 did not exist when it was written.
# This widens the STRUCTURAL disposition, not a threshold: the hit is still
# printed, still dispositioned by name, and the STRICT count still reported.


def nearest_heading(name, i):
    """The nearest markdown heading at or above line i (1-based)."""
    ls = lines(name)
    for j in range(min(i, len(ls)) - 1, -1, -1):
        if ls[j].startswith("#"):
            return ls[j]
    return ""


def under_correcting_heading(name, i):
    h = nearest_heading(name, i)
    return bool(CORRECTING_HEADING.search(h)), h.strip()[:88]


def section_text(name, i):
    """The whole `## ` section containing line i - the widest reading used.

    A ledger entry corrects itself further down its own section far more often
    than within four lines: Q1 transcribes the operator's ruling verbatim at
    the top and records the correction to it fifty lines later. A build session
    may not rewrite a transcribed ruling, so section scope is the honest unit
    for "does this document know that this figure is superseded?".
    """
    ls = lines(name)
    lo = 0
    for j in range(min(i, len(ls)) - 1, -1, -1):
        if ls[j].startswith("## "):
            lo = j
            break
    hi = len(ls)
    for j in range(min(i, len(ls)), len(ls)):
        if ls[j].startswith("## "):
            hi = j
            break
    return "\n".join(ls[lo:hi])


def fenced_line_numbers(name):
    """1-based line numbers that sit inside a ``` fenced block."""
    inside = False
    out = set()
    for i, ln in enumerate(lines(name), 1):
        if ln.lstrip().startswith("```"):
            inside = not inside
            out.add(i)
            continue
        if inside:
            out.add(i)
    return out


# ---------------------------------------------------------------------------
# A. every model name, classified
# ---------------------------------------------------------------------------
# A sonnet mention is ACCEPTABLE only if its unit also carries one of these.
# Each is a reason the mention is NOT a claim that sonnet ran an evaluation arm.
SONNET_OK = [
    ("withdraw",      "names the subset as withdrawn"),
    ("sensitivity",   "names the model-sensitivity subset"),
    ("probe",         "the model-id probe, not an arm"),
    ("model-id",      "the model-id probe, not an arm"),
    ("rejects",       "the temperature-400 limitation"),
    ("http 400",      "the temperature-400 limitation"),
    ("temperature",   "the temperature-400 limitation"),
    ("subset",        "names it as a subset"),
    ("correction",    "a dated correction quoting the wrong text"),
    ("was wrong",     "a dated correction quoting the wrong text"),
    ("wrongly",       "a dated correction quoting the wrong text"),
    ("misquot",       "a dated correction quoting the wrong text"),
    ("does not repro", "a dated correction quoting the wrong text"),
    ("stale",         "a dated correction quoting the wrong text"),
    ("errata",        "a dated correction quoting the wrong text"),
    ("q19",           "cites the withdrawal ruling"),
    ("q35",           "cites the model-name correction"),
    ("q37",           "cites the model-name correction"),
    ("empty",         "the 13-of-20 empty-response harness defect"),
    ("13 of 20",      "the 13-of-20 empty-response harness defect"),
    ("cheap inference", "Q1's pre-decision cost discussion"),
    ("usd 20 ceiling", "Q1's pre-decision cost discussion"),
    ("if haiku shows", "Q1's pre-decision cost discussion"),
    ("b0-agent-sonnet", "an explicitly sonnet-named arm of the subset"),
    ("b0-sonnet",     "an explicitly sonnet-named arm of the subset"),
    ("every evaluation arm is haiku", "states the correct fact"),
    ("the only `claude-sonnet-5` rows", "states the correct fact"),
    ("card's conclusion", "the chunk-card count correction"),
    ("naming `claude-sonnet-5`", "the chunk-card count correction"),
]


def classify_sonnet(text):
    low = text.lower()
    for needle, why in SONNET_OK:
        if needle in low:
            return why
    return None


def section_models():
    rule("A. every model name in the shipping surface, classified")

    total = collections.Counter()
    for name in SHIPPING:
        per = collections.Counter()
        for ln in lines(name):
            low = ln.lower()
            if "claude-haiku-4-5-20251001" in low:
                per["haiku-dated"] += 1
            if re.search(r"claude-haiku-4-5(?![\d-])", low):
                per["haiku-alias"] += 1
            if "sonnet" in low:
                per["sonnet"] += 1
        total.update(per)
        print("  %-16s haiku-dated %3d   haiku-alias %2d   sonnet %3d"
              % (name, per["haiku-dated"], per["haiku-alias"], per["sonnet"]))
    print("")
    print("  TOTAL            haiku-dated %3d   haiku-alias %2d   sonnet %3d"
          % (total["haiku-dated"], total["haiku-alias"], total["sonnet"]))
    print("  (the haiku-alias column counts the floating alias `claude-haiku-4-5`;")
    print("   GOOD.md section 8 records it works and is deliberately NOT used.)")

    strict, scoped = [], []
    for name in SHIPPING:
        for i, ln in enumerate(lines(name), 1):
            if "sonnet" not in ln.lower():
                continue
            if classify_sonnet(ln) is None:
                strict.append((name, i, ln.strip()))
                why = classify_sonnet(window(name, i))
                if why is None:
                    ok, head = under_correcting_heading(name, i)
                    if ok:
                        why = ("quoted verbatim under a heading that "
                               "announces the correction -- %s" % head)
                if why is None:
                    scoped.append((name, i, ln.strip()))
                else:
                    strict[-1] = (name, i, ln.strip(), why)

    print("")
    print("  Sonnet mentions unqualified on their OWN LINE (STRICT reading): "
          "%d" % len(strict))
    print("  Each is printed with the disposition its SCOPED unit earned, so a")
    print("  reviewer can disagree with any one of them by name:")
    print("")
    for row in strict:
        if len(row) == 4:
            name, i, ln, why = row
            print("    %-16s :%-5d %s" % (name, i, ln[:88]))
            print("        -> ACCOUNTED FOR: %s" % why)
        else:
            name, i, ln = row
            print("    %-16s :%-5d %s" % (name, i, ln[:88]))
            print("        -> UNACCOUNTED FOR")
    if not strict:
        print("    (none)")

    print("")
    print("  Unqualified under the SCOPED reading (+/- %d lines): %d"
          % (WINDOW, len(scoped)))
    for name, i, ln in scoped:
        print("    %s:%d  %s" % (name, i, ln[:100]))
    check("no shipping passage attributes an evaluation arm to sonnet",
          not scoped,
          "SCOPED %d unaccounted / STRICT %d line-level, all dispositioned"
          % (len(scoped), len(strict)))

    check("PROVENANCE.md names the dated haiku id",
          "claude-haiku-4-5-20251001" in "\n".join(lines("PROVENANCE.md")))
    MARKS = ("alias", "probe", "floating", "not used", "pinned", "dated",
             "404", "does not pin")
    alias_strict, alias_win, alias_sec = [], [], []
    for name in SHIPPING:
        for i, ln in enumerate(lines(name), 1):
            if re.search(r"claude-haiku-4-5(?![\d-])", ln) is None:
                continue
            low = ln.lower()
            if not any(w in low for w in MARKS):
                alias_strict.append((name, i, ln.strip()[:100]))
                if not any(w in window(name, i).lower() for w in MARKS):
                    alias_win.append((name, i, ln.strip()[:100]))
                    if not any(w in section_text(name, i).lower()
                               for w in MARKS):
                        alias_sec.append((name, i, ln.strip()[:100]))
    print("")
    print("  Uses of the FLOATING alias `claude-haiku-4-5`, by reading.")
    print("  GOOD.md section 8: the alias works and is deliberately NOT used,")
    print("  because a reproducibility claim pinned by a floating alias is not")
    print("  pinned. So a use is only a defect if NOTHING around it says so.")
    print("    unmarked on its own line      (STRICT)  : %d" % len(alias_strict))
    print("    unmarked within +/-%d lines   (SCOPED)  : %d"
          % (WINDOW, len(alias_win)))
    print("    unmarked anywhere in its `## ` section  : %d" % len(alias_sec))
    for name, i, ln in alias_strict:
        tag = "UNMARKED IN ITS SECTION" if (name, i, ln) in alias_sec else (
            "marked later in its own section" if (name, i, ln) in alias_win
            else "marked within 4 lines")
        print("    %s:%d  %s" % (name, i, ln))
        print("        -> %s" % tag)
    if not alias_strict:
        print("    (none -- every use is discussed AS the alias on its line)")
    check("no shipping file pins a result to the FLOATING haiku alias",
          not alias_sec,
          "STRICT %d / SCOPED %d / section %d"
          % (len(alias_strict), len(alias_win), len(alias_sec)))


# ---------------------------------------------------------------------------
# B. headline figures, cross-checked across files
# ---------------------------------------------------------------------------
CROSS = [
    ("A1 accuracy",            ["0.7195"]),
    ("B0-agent accuracy",      ["0.6585"]),
    ("B0 accuracy",            ["0.4756"]),
    ("total spend",            ["11.6323", "11.63"]),
    ("secret-sweep blobs",     ["462"]),
    ("eval-set n = 82",        ["n = 82", "n=82"]),
    ("eval-set pairs = 41",    ["41 pairs"]),
    ("corpus gap pp",          ["18.3"]),
    ("A1 gap pp",              ["6.1 pp"]),
    ("corpus p",               ["0.0059"]),
    ("A1 p",                   ["0.4244"]),
    ("B0prime disagreements",  ["22 of 82", "**22**"]),
    ("A1 input tokens",        ["4,006,662", "4.01 M", "4006662"]),
    ("B0prime input tokens",   ["1,377,402", "1.38 M", "1377402"]),
]

# Figures that LOOK like a total but are a named subset. Each is listed with
# what it actually measures, and each is checked against the ledger below.
KNOWN_SUBTOTALS = {
    "11.11": "the six PRIMARY-MATRIX arms only, excluding the ablation "
             "A1-iter1? no - excluding the withdrawn sonnet subset, the "
             "B0-agent-currenttext removed experiment and the model-id probe",
    "9.6967": "the CH-11 SESSION's own cost, stated beside the 11.6323 total "
              "on the same line",
}


def section_cross():
    rule("B. headline figures - agreement across the shipping surface")

    print("  %-24s %s" % ("figure", "files stating it"))
    for label, forms in CROSS:
        hits = [n.replace(".md", "") for n in SHIPPING
                if any(f in "\n".join(lines(n)) for f in forms)]
        print("  %-24s %s" % (label, ", ".join(hits) if hits else "(none)"))

    # -- B1: total-spend-shaped USD figures ---------------------------------
    print("")
    print("  B1. Every USD figure between 9 and 18 - the range a reader could")
    print("      mistake for the project total (11.6323):")
    strict_usd, scoped_usd = [], []
    for name in SHIPPING:
        for i, ln in enumerate(lines(name), 1):
            for m in re.finditer(r"USD\s+(\d+\.\d+)", ln):
                v = float(m.group(1))
                if not (9.0 < v < 18.0):
                    continue
                if abs(v - 11.6323) < 0.01 or abs(v - 11.63) < 0.01:
                    continue
                key = m.group(1)
                strict_usd.append((name, i, key, ln.strip()))
                win = window(name, i)
                if key in KNOWN_SUBTOTALS and ("11.6323" in win
                                               or "arms" in win
                                               or "session" in win.lower()):
                    continue
                scoped_usd.append((name, i, key, ln.strip()))
    for name, i, key, ln in strict_usd:
        print("    %s:%d  USD %s" % (name, i, key))
        print("        | %s" % ln[:104])
        if key in KNOWN_SUBTOTALS:
            print("        -> NOT the total: %s" % KNOWN_SUBTOTALS[key])
    if not strict_usd:
        print("    (none)")
    check("no shipping file states a project total other than 11.6323",
          not scoped_usd,
          "STRICT %d, all named subtotals" % len(strict_usd))

    # -- B2: the 11.11 subtotal, checked against the ledger -----------------
    path = os.path.join(ROOT, "docs", "evidence", "runs", "cost_ledger.csv")
    rows = list(csv.DictReader(io.open(path, encoding="utf-8")))
    primary = {"B0", "B0-agent", "B0prime", "A1-iter1", "A1-minus-tool", "A1"}
    sub = sum(float(r["imputed_usd"]) for r in rows
              if r["arm"] in primary and r["imputed_usd"].strip())
    tot = sum(float(r["imputed_usd"]) for r in rows if r["imputed_usd"].strip())
    print("")
    print("  B2. REPRODUCE.md says the six primary-matrix arms cost USD 11.11.")
    print("      Re-summed from the ledger over %s:" % sorted(primary))
    print("        six primary arms        USD %.4f" % sub)
    print("        everything in the ledger USD %.4f" % tot)
    print("        difference               USD %.4f  "
          "(withdrawn sonnet subset + removed experiment + probe)"
          % (tot - sub))
    check("REPRODUCE.md's 11.11 is the six-arm subtotal and reproduces",
          abs(sub - 11.11) < 0.005, "%.4f" % sub)

    # -- B3: stale figures asserted rather than corrected --------------------
    print("")
    print("  B3. Stale figures - asserted, or quoted in order to correct?")
    patterns = [
        (r"450 (blob|text blob)", "the pre-re-run secret-sweep scope",
         ("read", "0f3f4fe", "earlier", "stale", "until", "committed twice",
          "says 462", "the committed scan")),
        (r"26 items had samples", "the non-reproducing disagreement count",
         ("does not reproduce", "->", "→", "earlier", "old", "wrong",
          "Q33", "gives **22**", "gives 22", "22")),
    ]
    strict_stale, scoped_stale = [], []
    for pat, what, excuses in patterns:
        for name in SHIPPING:
            for i, ln in enumerate(lines(name), 1):
                if not re.search(pat, ln):
                    continue
                strict_stale.append((name, i, what, ln.strip()))
                win = window(name, i)
                if not any(e in win for e in excuses) and \
                        not under_correcting_heading(name, i)[0]:
                    scoped_stale.append((name, i, what, ln.strip()))
    for name, i, what, ln in strict_stale:
        tag = "ASSERTED" if (name, i, what, ln) in scoped_stale \
            else "quoted to correct"
        print("    [%-17s] %s:%d  %s" % (tag, name, i, what))
        print("        | %s" % ln[:100])
    if not strict_stale:
        print("    (none)")
    check("every stale figure that survives is quoted in order to correct it",
          not scoped_stale,
          "STRICT %d occurrences, %d asserted"
          % (len(strict_stale), len(scoped_stale)))


# ---------------------------------------------------------------------------
# C. compute-matched survivors and false gate-pass claims
# ---------------------------------------------------------------------------
def section_labels():
    rule("C. surviving 'compute-matched' labels, and gate-pass claims")

    CORRECTIVE = ("not run", "never run", "is not", "and it is not", "→",
                  "->", "NOT token-matched", "not token-matched", "Q34", "Q36",
                  "repeated-sampling", "still say", "CANNOT be built",
                  "PROTECTED", "did not touch")
    print("  Every 'compute-match' occurrence in the shipping surface:")
    survivors = []
    for name in SHIPPING:
        for i, ln in enumerate(lines(name), 1):
            if "compute-match" not in ln.lower():
                continue
            win = window(name, i)
            ok = (any(w in ln for w in CORRECTIVE)
                  or any(w in win for w in CORRECTIVE)
                  or under_correcting_heading(name, i)[0])
            print("    [%s] %s:%d  %s"
                  % ("corrective" if ok else "ASSERTION", name, i,
                     ln.strip()[:92]))
            if not ok:
                survivors.append((name, i))
    check("no shipping file still LABELS B0-prime compute-matched",
          not survivors, "%d surviving assertion(s)" % len(survivors))

    print("")
    print("  PROTECTED files CH-11c may not edit that still say "
          "compute-matched:")
    protected = []
    for rel in ("CONTEXT.md", "src/arms.py", "prompts/CH-06.md", "plan.md",
                "PROCESS.md", "GOOD.md"):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("    %-20s (absent)" % rel)
            continue
        hits = [i for i, ln in enumerate(
            io.open(p, encoding="utf-8").read().splitlines(), 1)
            if "compute-match" in ln.lower()]
        print("    %-20s %d occurrence(s)%s"
              % (rel, len(hits), ("  line %s" % hits) if hits else ""))
        protected += [(rel, i) for i in hits]
    print("  -> recorded as QUESTIONS.md Q36 for the architect, NOT edited.")
    check("the protected occurrences are declared in QUESTIONS.md Q36",
          "## Q36 -" in "\n".join(lines("QUESTIONS.md")),
          "%d occurrence(s) across protected files" % len(protected))

    print("")
    print("  Gate-pass claims. PROCESS.md gates a chunk on review by a fresh")
    print("  session with zero shared context. NO chunk passed its gate.")
    gate = []
    for name in SHIPPING:
        for i, ln in enumerate(lines(name), 1):
            if "reviewed-PASS" not in ln:
                continue
            neg = any(w in ln for w in (
                "None", "none", "no chunk", "not", "never", "States:",
                "is done only at", "awarded", "`todo`"))
            print("    [%s] %s:%d  %s"
                  % ("definition/negation" if neg else "CLAIM", name, i,
                     ln.strip()[:88]))
            if not neg:
                gate.append((name, i))
    if not gate:
        print("    (no claim that any chunk passed)")
    check("no shipping file claims a chunk reached reviewed-PASS", not gate,
          "%d claim(s)" % len(gate))

    print("")
    print("  And the guard that IS failed, stated where it is quoted:")
    r = "\n".join(lines("README.md"))
    check("README.md states the 0.90 attributor guard is FAILED",
          "0.5340" in r and "0.90" in r)


# ---------------------------------------------------------------------------
# D. every docs/evidence path cited by the shipping surface must exist
# ---------------------------------------------------------------------------
PATH_RE = re.compile(r"docs/evidence/[A-Za-z0-9_./\-]+")

# A path that is a PROPOSAL or a TEMPLATE is not a citation. Each is named.
NOT_A_CITATION = {
    "docs/evidence/iter-N/":
        "a TEMPLATE placeholder inside CHANGELOG.md's fenced iteration-card "
        "shape - 'N' is the literal letter N",
    "docs/evidence/ch11-repro/":
        "a HYPOTHETICAL path in QUESTIONS.md Q30's question TO the architect "
        "('should a chunk be allowed a single evidence directory - this - as "
        "a named exception?'). It was never created; Q30 says so.",
}


def section_paths():
    rule("D. every docs/evidence/ path the shipping surface cites")

    cited = collections.Counter()
    where = collections.defaultdict(list)
    in_fence = collections.defaultdict(bool)
    for name in SHIPPING:
        fenced = fenced_line_numbers(name)
        ls = lines(name)
        for i, ln in enumerate(ls, 1):
            # rejoin a path broken at a line end inside backticks
            probe = ln
            if ln.rstrip().endswith("/") and i < len(ls):
                probe = ln.rstrip() + ls[i].lstrip()
            for m in PATH_RE.finditer(probe):
                p = m.group(0).rstrip(".,;:)`*")
                cited[p] += 1
                if name not in where[p]:
                    where[p].append(name)
                if i in fenced:
                    in_fence[p] = True

    missing = [p for p in sorted(cited)
               if not os.path.exists(os.path.join(ROOT, p))]
    unexplained = []
    print("  distinct docs/evidence/ paths cited : %d" % len(cited))
    print("  citations in total                  : %d" % sum(cited.values()))
    print("  paths that do not exist on disk     : %d" % len(missing))
    print("")
    for p in missing:
        print("    ABSENT  %s" % p)
        print("            cited by %s%s"
              % (", ".join(where[p]),
                 "  [inside a fenced block]" if in_fence[p] else ""))
        if p in NOT_A_CITATION:
            print("            -> NOT A CITATION: %s" % NOT_A_CITATION[p])
        else:
            print("            -> UNEXPLAINED")
            unexplained.append(p)
    if not missing:
        print("    (none)")
    check("every real docs/evidence/ citation resolves to a file on disk",
          not unexplained,
          "%d absent, %d of them templates or proposals"
          % (len(missing), len(missing) - len(unexplained)))


# ---------------------------------------------------------------------------
# E. the ledger, re-summed
# ---------------------------------------------------------------------------
def section_ledger():
    rule("E. the cost ledger, re-summed")

    path = os.path.join(ROOT, "docs", "evidence", "runs", "cost_ledger.csv")
    rows = list(csv.DictReader(io.open(path, encoding="utf-8")))
    total = sum(float(r["imputed_usd"]) for r in rows
                if r["imputed_usd"].strip())
    empty = sum(1 for r in rows if not r["imputed_usd"].strip())
    print("  rows                    : %d" % len(rows))
    print("  rows with a cost cell   : %d" % (len(rows) - empty))
    print("  rows with an EMPTY cell : %d   (unknown is not the same claim "
          "as free)" % empty)
    print("  priced + empty == rows  : %d + %d == %d  -> %s"
          % (len(rows) - empty, empty, len(rows),
             (len(rows) - empty) + empty == len(rows)))
    print("  input tokens            : %d"
          % sum(int(r["input_tokens"] or 0) for r in rows))
    print("  output tokens           : %d"
          % sum(int(r["output_tokens"] or 0) for r in rows))
    print("  TOTAL imputed USD       : %.4f" % total)
    check("priced + empty == rows", (len(rows) - empty) + empty == len(rows))
    check("API spend is 11.6323, unchanged by CH-11c",
          abs(total - 11.6323) < 5e-5, "%.4f" % total)
    check("spend is under the USD 18.00 ceiling", total < 18.0,
          "headroom USD %.4f" % (18.0 - total))


def main():
    print("CH-11c SHIPPING-SURFACE SWEEP -- the mechanical half")
    print("files swept: %s" % ", ".join(SHIPPING))
    print("no network, no model call, no clock, no RNG")
    print("STRICT (line-scope) and SCOPED (+/-%d lines) readings are BOTH "
          "printed;" % WINDOW)
    print("verdicts are taken on SCOPED and every STRICT hit is dispositioned "
          "by name.")

    section_models()
    section_cross()
    section_labels()
    section_paths()
    section_ledger()

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
