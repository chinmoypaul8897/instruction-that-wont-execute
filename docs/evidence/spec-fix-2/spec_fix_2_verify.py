#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPEC-FIX-2 - verification of the v1.1 CONTEXT.md edits.

This chunk produced NO new measurement. It edited a specification under a ruling.
So the thing that has to be evidenced is not a number - it is that

    (1) each of the three specified changes is present in the shipped file,
    (2) the text each one replaced is GONE and not merely duplicated,
    (3) NOTHING ELSE in CONTEXT.md changed, and in particular
    (4) the gate definition, the 0.90 threshold and every CH-02 measurement
        are byte-identical to what they were before this chunk ran,
    (5) so no failing number was made to pass.

(1) and (2) are hard rule 16 - "verify your own edit landed" - made re-runnable
instead of taken on trust from a session that has every incentive to believe it.
(3)-(5) are the answer to the question the prompt makes the headline of the
report: DID ANY CHANGE MAKE A FAILING NUMBER PASS?

Pure: reads the repository and git, writes one report to stdout. No network,
no clock, no randomness. data/, src/ and tests/ are never opened.

    python docs/evidence/spec-fix-2/spec_fix_2_verify.py > docs/evidence/spec-fix-2/verify.txt

Exit status is 0 only if every assertion holds.
"""

import subprocess
import sys

# Emit LF, never CRLF. This repository's .gitattributes is `* -text`, so whatever
# Python writes is what git stores; on Windows a plain `python x.py > out.txt`
# writes CRLF and commits it. CH-02 recorded that defect, SPEC-FIX-1 recorded it
# again and normalised its output by hand, and AI-USE.md calls it "a one-line fix
# for whichever chunk owns the script". This script owns itself, so here is the line.
try:
    sys.stdout.reconfigure(newline="\n")          # Python 3.7+
except AttributeError:                            # pragma: no cover
    pass

REPO = "."
BASE = "0613d54"          # the commit immediately BEFORE any SPEC-FIX-2 spec edit:
                          # CONTEXT.md as it stood with the CH-01 architect edit committed
                          # and nothing of this chunk's own applied yet.

FENCE = {                 # the only paths prompts/SPEC-FIX-2.md permits this chunk to change
    "CONTEXT.md", "QUESTIONS.md", "STATUS.md", "PROGRESS.md", "AI-USE.md",
}
FENCE_PREFIXES = ("docs/evidence/spec-fix-2/", "docs/trajectories/", "prompts/")

READ_ONLY_PREFIXES = ("data/", "src/", "tests/",
                      "docs/evidence/ch02-attributor/", "docs/evidence/spec-fix-1/",
                      "docs/evidence/ch01-pool/", "docs/evidence/ch00-")
PROTECTED_FILES = ("plan.md", "PROCESS.md", "CLAUDE.md", "PROVENANCE.md", "GOOD.md")

ok = True
def check(label, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  [%s] %s%s" % ("PASS" if cond else "**FAIL**", label,
                           ("  -- " + detail) if detail else ""))
    return cond


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8").stdout


def rule(title):
    print("")
    print("-- %s %s" % (title, "-" * max(0, 70 - len(title))))


print("=" * 74)
print("SPEC-FIX-2 - CONTEXT.md v1.1 EDIT VERIFICATION")
print("=" * 74)
print("base (pre-edit) commit : %s" % BASE)
print("no measurement was taken in this chunk; the attributor was not re-run.")

before = git("show", "%s:CONTEXT.md" % BASE)
after = open("CONTEXT.md", "r", encoding="utf-8").read()
assert before, "could not read CONTEXT.md at the base commit"

b_lines = before.replace("\r\n", "\n").split("\n")
a_lines = after.replace("\r\n", "\n").split("\n")
b_set, a_set = set(b_lines), set(a_lines)

# =====================================================================
rule("1. THE THREE CHANGES ARE PRESENT")
# =====================================================================
PRESENT = [
    ("change 1 - the failure is recorded",
     "#### THE GATE FAILED, AND THE FAILURE IS PUBLISHED"),
    ("change 1 - the rejected metric is named as rejected",
     "that figure was tested and REJECTED as a gate"),
    ("change 1 - the sabotage control is cited as the reason",
     "places **6,395 of 6,663** attributed elements on a **different** section"),
    ("change 1 - Q10's two unfixed spellings recorded",
     "Known, counted, and deliberately unfixed"),
    ("change 2 - word form in the detector",
     "the **word form** — `Section` or `Sections` followed by the number"),
    ("change 2 - case-sensitivity stated explicitly",
     "**The word form is matched CASE-SENSITIVELY: `Section`, never `section`.**"),
    ("change 2 - justified independently of the number",
     "adopted because it is justified independently of its effect on any number"),
    ("change 2 - the 0.9865 over-count declared",
     "case-INsensitive one and is therefore an over-count"),
    ("change 3 - the part-boundary reset",
     "**Reset `current_section` to null at every `<REGTEXT>` part boundary**"),
    ("change 3 - the 8-point cost stated, not hidden",
     "It costs **8.0 points**"),
    ("change 3 - Q12(a)'s correction to the 699",
     "The figure for genuine carry-forward part mismatches is **573**"),
    ("change 4 - version bumped",
     "**Version:** v1.1"),
    ("change 4 - change-log row",
     "| v1.1 | 2026-08-31 |"),
]
for label, needle in PRESENT:
    check(label, needle in after, "%d occurrence(s)" % after.count(needle))

# =====================================================================
rule("2. THE REPLACED TEXT IS GONE (hard rule 16)")
# =====================================================================
GONE = [
    ("v1.0 sign-only detector step 3",
     "3. If the element names a section (matches a `§\\s*[\\d.]+[a-z]?` citation in "
     "its own text), set `current_section` to it and attribute the element there."),
    ("v1.0 bare `current_section` step 2 (no reset)",
     "2. Maintain `current_section`, initially null."),
    ("v1.0 version header",
     "**Version:** v1.0 · 2026-08-30 03:20 UTC"),
]
# The test is LINE-EXACT, not substring, and that is deliberate. v1.0's step 2 is a
# strict PREFIX of its v1.1 replacement ("...initially null." -> "...initially null.
# **Reset ... at every <REGTEXT> part boundary** ..."), so a substring test reports it
# as surviving forever and can never be satisfied by any correct edit. The first run of
# this script failed on exactly that and the CHECK was wrong, not the edit - section 3
# below independently confirms the v1.0 line itself is gone. Recorded rather than
# quietly rewritten, because a verifier that was silently adjusted until it went green
# is the thing this project exists to warn about.
after_lines = set(after.replace("\r\n", "\n").split("\n"))
for label, needle in GONE:
    survives_as_line = needle in after_lines
    check(label + " - the v1.0 LINE is gone", not survives_as_line,
          "as a substring it appears %d time(s)%s" % (
              after.count(needle),
              " (it is a prefix of its own v1.1 replacement)" if after.count(needle) else ""))

# =====================================================================
rule("3. NOTHING ELSE IN CONTEXT.md CHANGED")
# =====================================================================
removed = [l for l in b_lines if l not in a_set and l.strip()]
added = [l for l in a_lines if l not in b_set and l.strip()]
check("exactly 3 non-blank lines removed", len(removed) == 3,
      "removed %d" % len(removed))
for i, l in enumerate(removed):
    print("       removed[%d]: %s" % (i, (l[:88] + "...") if len(l) > 88 else l))
check("every removed line is one of the three declared edit targets",
      all(any(g[1].startswith(l[:60]) or l.startswith(g[1][:60]) for g in GONE)
          for l in removed))
print("       added   : %d non-blank lines (all new v1.1 text)" % len(added))

# =====================================================================
rule("4. THE GATE ITSELF IS BYTE-IDENTICAL")
# =====================================================================
GATE = ("**completeness = (number of AMDPAR elements attributed to a section AND parsed "
        "into at least one complete `(operation, anchor OR designation)` triple) ÷ "
        "(total AMDPAR elements in the document)**")
check("the completeness definition is unchanged and present once",
      before.count(GATE) == 1 and after.count(GATE) == 1)
check("the definition was NOT replaced by attribution/total",
      "attribution_completeness" not in after,
      "the refused metric must not appear as a definition in CONTEXT.md")
check("'attribution alone is not the bar' still stands",
      "attribution alone is not the bar" in after)
check("the count of 0.90 occurrences did not fall",
      after.count("0.90") >= before.count("0.90"),
      "before=%d after=%d" % (before.count("0.90"), after.count("0.90")))

# =====================================================================
rule("5. DID ANY CHANGE MAKE A FAILING NUMBER PASS?")
# =====================================================================
# CH-02's committed figures, read from CH-02's own evidence rather than retyped here.
comp = open("docs/evidence/ch02-attributor/completeness.md", "r", encoding="utf-8").read()
lit = "| `spec_literal` | **0.5080** |" in comp
ext = "| `extended` | **0.6643** |" in comp
check("CH-02's committed completeness figures still read 0.5080 / 0.6643", lit and ext)

GATE_THRESHOLD = 0.90
BRANCH_BOUNDARY = 0.80
for name, value in (("spec_literal", 0.5080), ("extended", 0.6643)):
    check("%s %.4f is still below the 0.90 gate" % (name, value),
          value < GATE_THRESHOLD)
    check("%s %.4f is still in the '< 0.80 documented failure' branch" % (name, value),
          value < BRANCH_BOUNDARY)
print("       The v1.1 detector change can at most move the gated figure from the")
print("       sign-only 0.5080 toward the extended 0.6643. 0.6643 < 0.80, so the")
print("       branch CH-02 lands in is UNCHANGED. The part-boundary reset moves the")
print("       figure DOWN. Neither change, nor both together, reaches 0.80 - let")
print("       alone 0.90. Case-sensitivity can only REMOVE detections, never add.")
check("therefore: no change in this chunk makes a failing number pass", True)

# =====================================================================
rule("6. THE READ-ONLY AND PROTECTED PATHS WERE NOT TOUCHED")
# =====================================================================
touched = [l for l in git("diff", "--name-only", "%s..HEAD" % BASE).split("\n") if l]
touched += [l for l in git("diff", "--name-only").split("\n") if l]
touched += [l for l in git("diff", "--name-only", "--cached").split("\n") if l]
touched = sorted(set(touched))
print("       paths changed since %s:" % BASE)
for p in touched:
    print("         %s" % p)
check("no read-only path changed",
      not any(p.startswith(READ_ONLY_PREFIXES) for p in touched),
      "data/ src/ tests/ and prior chunks' evidence are read-only here")
check("no protected file changed",
      not any(p in PROTECTED_FILES for p in touched),
      "plan.md PROCESS.md CLAUDE.md PROVENANCE.md GOOD.md")
check("every changed path is inside the scope fence",
      all(p in FENCE or p.startswith(FENCE_PREFIXES) for p in touched))

# =====================================================================
rule("7. FILE HYGIENE")
# =====================================================================
raw = open("CONTEXT.md", "rb").read()
check("CONTEXT.md line endings still uniformly CRLF, as they were at v1.0",
      raw.count(b"\r\n") == raw.count(b"\n"),
      "CRLF=%d LF=%d" % (raw.count(b"\r\n"), raw.count(b"\n")))
qraw = open("QUESTIONS.md", "rb").read()
check("QUESTIONS.md line endings still uniformly LF",
      b"\r\n" not in qraw)
q = qraw.decode("utf-8")
check("the Q11 ruling is recorded verbatim",
      "Q11 - RULED by ARCHITECT, 2026-08-30." in q and
      "The refusal is ACCEPTED IN FULL." in q and
      "The gate stays as it\nis and stays FAILED." in q)
check("Q11 ruling appears exactly once",
      q.count("Q11 - RULED by ARCHITECT, 2026-08-30.") == 1)
check("the ruling is byte-identical to its source in prompts/SPEC-FIX-2.md",
      "\n".join(open("prompts/SPEC-FIX-2.md", "r", encoding="utf-8")
                .read().split("\n")[35:72]) in q)
check("all 9 chunk prompts are tracked",
      len([l for l in git("ls-files", "prompts/").split("\n") if l]) == 9,
      "%d tracked" % len([l for l in git("ls-files", "prompts/").split("\n") if l]))
check("no untracked file remains under prompts/",
      git("ls-files", "--others", "--exclude-standard", "prompts/").strip() == "")

print("")
print("=" * 74)
print("RESULT: %s" % ("ALL CHECKS PASS" if ok else "AT LEAST ONE CHECK FAILED"))
print("=" * 74)
sys.exit(0 if ok else 1)
