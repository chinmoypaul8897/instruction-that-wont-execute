#!/usr/bin/env python3
"""SPEC-FIX-1 - count, from the frozen data, the classes of AMDPAR element that
CONTEXT.md section 8's completeness definition scores as incomplete.

The architect's claim under judgement is that three classes of *legitimate* amendatory
instruction cannot parse into an `(operation, anchor OR designation)` triple:
authority citations, lead-ins, and whole-section operations. This script does not take
that on trust (CLAUDE.md hard rule 15). It partitions the whole unparsed population into
mutually exclusive buckets, prints every bucket including the ones the architect did not
name, and asserts the partition is exhaustive.

Reads only. `data/` is sealed (hard rule 11). Deterministic: no clock, no network, no
randomness (hard rules 8, 9). Zero-occurrence branches print as zeros and
`sum(buckets) == n` is asserted (hard rule 14).

Usage:  python docs/evidence/spec-fix-1/spec_fix_1_classes.py
"""
import io
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")

ROOT = Path(__file__).resolve().parents[3]
AMDPARS = ROOT / "data" / "amdpars" / "amdpars.jsonl"
COMPLETENESS = ROOT / "data" / "amdpars" / "completeness.json"

# --- detectors -------------------------------------------------------------------
# P2's section citation, extended per P3 to the word form. Reproduced here rather than
# imported, so this evidence stands on its own text (PROCESS.md section 6).
BASE = r"\d+[A-Za-z]?\.\d+[A-Za-z0-9]*(?:(?:\([A-Za-z0-9]+\))*-\d+[A-Za-z0-9]*)?"
RE_SIGN = re.compile("§§?\\s*" + BASE)
RE_WORD = re.compile(r"\bSections?\s+" + BASE)
RE_AUTHORITY = re.compile(r"authority citation", re.I)
RE_DOC_OPENER = re.compile(
    r"(For the reasons|Accordingly|Under the authority).{0,400}?"
    r"(Code of Federal Regulations|CFR|chapter|title)\b.{0,200}?"
    r"(is|are) amended",
    re.I | re.S,
)
RE_PART_LEVEL = re.compile(
    r"\b(part|subpart|appendi(x|ces)|chapter|title|table|figure)\b", re.I
)
# a paragraph path P5 would have taken if it were there at all
RE_ANY_DESIG = re.compile(r"\([A-Za-z0-9]{1,4}\)")


def names_section(text):
    return bool(RE_SIGN.search(text) or RE_WORD.search(text))


def classify(r):
    """First match wins. Buckets are mutually exclusive by construction."""
    t = r["text"]
    op = r["operation"]
    has_desig = bool(r["designation"])
    has_anchor = bool(r["anchor"])
    ends_colon = t.rstrip().endswith(":")

    # 1. authority citations - the architect's class A
    if RE_AUTHORITY.search(t):
        return "A_authority_citation"

    # 2. the document-level opener: "For the reasons ... parts 60, 72 and 75 ... are
    #    amended as follows:". Not one of the architect's three; counted separately.
    if RE_DOC_OPENER.search(t) and not has_desig and not has_anchor:
        return "D_document_opener"

    if op is None:
        # 5. operation lives in a parent element; this is a continuation fragment.
        #    Not one of the architect's three classes.
        return "E_continuation_fragment_no_operation"

    if has_desig or has_anchor:
        # parsed==False with an operation AND a designation/anchor should be impossible;
        # if it fires, the parse rule and the record disagree and that is a real finding.
        return "Z_UNEXPECTED_operation_and_target"

    if names_section(t):
        if op == "amend" and ends_colon:
            return "B_lead_in_section_named"          # architect's class B
        return "C_whole_section_operation"            # architect's class C

    # names no CFR section at all
    if RE_PART_LEVEL.search(t):
        if ends_colon:
            return "B2_lead_in_part_or_appendix_level"
        return "F_part_or_appendix_level_operation"
    if ends_colon:
        return "B3_lead_in_no_target_named"
    return "G_other_no_target_named"


LEGITIMACY = OrderedDict([
    ("A_authority_citation",              ("architect class A", "legitimate-instruction")),
    ("B_lead_in_section_named",           ("architect class B", "legitimate-instruction")),
    ("B2_lead_in_part_or_appendix_level", ("lead-in variant",   "legitimate-instruction")),
    ("B3_lead_in_no_target_named",        ("lead-in variant",   "legitimate-instruction")),
    ("C_whole_section_operation",         ("architect class C", "legitimate-instruction")),
    ("D_document_opener",                 ("NOT NAMED",         "legitimate-instruction")),
    ("E_continuation_fragment_no_operation", ("NOT NAMED",      "legitimate-instruction")),
    ("F_part_or_appendix_level_operation", ("NOT NAMED",        "legitimate-instruction")),
    ("G_other_no_target_named",           ("NOT NAMED",         "ambiguous")),
    ("Z_UNEXPECTED_operation_and_target", ("NOT NAMED",         "parser-defect")),
])


def main():
    recs = [json.loads(l) for l in AMDPARS.open(encoding="utf-8")]
    agg = json.loads(COMPLETENESS.read_text(encoding="utf-8"))
    n = len(recs)

    print("=" * 78)
    print("SPEC-FIX-1 - class counts over the frozen CH-02 corpus")
    print("=" * 78)
    print("records read           : %d" % n)
    print("amdpars.jsonl          : %s" % AMDPARS.relative_to(ROOT).as_posix())
    print("completeness.json      : %s" % COMPLETENESS.relative_to(ROOT).as_posix())
    print()

    # --- the numbers the architect asserts, verified against the frozen aggregate ----
    ext = agg["global"]["extended"]
    lit = agg["global"]["spec_literal"]
    print("-- 1. THE ARCHITECT'S ASSERTED FACTS, RE-DERIVED FROM THE RECORDS ---------")
    checks = [
        ("total elements",       ext["total"],           n),
        ("attributed (extended)", ext["attributed"],
         sum(1 for r in recs if r["attributed_extended"])),
        ("unattributable (ext)", ext["unattributable"],
         sum(1 for r in recs if not r["attributed_extended"])),
        ("parsed",               ext["parsed"],
         sum(1 for r in recs if r["parsed"])),
        ("complete (extended)",  ext["complete"],
         sum(1 for r in recs if r["complete_extended"])),
        ("operation is none",    ext["by_operation"]["none"],
         sum(1 for r in recs if r["operation"] is None)),
    ]
    for name, stated, recomputed in checks:
        ok = "OK " if stated == recomputed else "MISMATCH"
        print("  %s %-22s aggregate=%-6s from records=%s" % (ok, name, stated, recomputed))
        assert stated == recomputed, "%s: %s != %s" % (name, stated, recomputed)
    print()
    print("  attribution_rate  extended     = %d/%d = %.4f   (architect said 0.9865)"
          % (ext["attributed"], n, ext["attributed"] / n))
    print("  attribution_rate  spec_literal = %d/%d = %.4f   (NOT quoted by the architect)"
          % (lit["attributed"], n, lit["attributed"] / n))
    print("  parse_rate                     = %d/%d = %.4f   (architect said 0.6672)"
          % (ext["parsed"], n, ext["parsed"] / n))
    print("  completeness      extended     = %d/%d = %.4f   (architect said 0.6643)"
          % (ext["complete"], n, ext["complete"] / n))
    print("  completeness      spec_literal = %d/%d = %.4f   (the gate CH-02 actually took)"
          % (lit["complete"], n, lit["complete"] / n))
    print()

    # --- the partition ---------------------------------------------------------------
    unparsed = [r for r in recs if not r["parsed"]]
    buckets = OrderedDict((k, []) for k in LEGITIMACY)
    for r in unparsed:
        buckets[classify(r)].append(r)

    print("-- 2. EVERY UNPARSED ELEMENT, PARTITIONED. FIRST MATCH WINS --------------")
    print("   unparsed = %d of %d  (%.4f of the corpus)"
          % (len(unparsed), n, len(unparsed) / n))
    print()
    print("   %-38s %6s %8s  provenance / legitimacy" % ("bucket", "n", "share"))
    total_bucketed = 0
    for key, rows in buckets.items():
        prov, legit = LEGITIMACY[key]
        total_bucketed += len(rows)
        print("   %-38s %6d %8.4f  %s / %s"
              % (key, len(rows), len(rows) / len(unparsed), prov, legit))
    print("   %-38s %6d" % ("TOTAL", total_bucketed))
    assert total_bucketed == len(unparsed), \
        "partition leaks: %d != %d" % (total_bucketed, len(unparsed))
    print("   ASSERTED: sum(buckets) == unparsed  (%d == %d)"
          % (total_bucketed, len(unparsed)))
    print()

    named = ("A_authority_citation", "B_lead_in_section_named",
             "C_whole_section_operation")
    named_n = sum(len(buckets[k]) for k in named)
    lead_family = ("B_lead_in_section_named", "B2_lead_in_part_or_appendix_level",
                   "B3_lead_in_no_target_named")
    lead_n = sum(len(buckets[k]) for k in lead_family)
    print("-- 3. THE ARCHITECT'S THREE CLASSES, STRICTLY READ -----------------------")
    print("   A  authority citations                : %5d" % len(buckets["A_authority_citation"]))
    print("   B  lead-ins (CFR section named)       : %5d" % len(buckets["B_lead_in_section_named"]))
    print("   C  whole-section operations           : %5d" % len(buckets["C_whole_section_operation"]))
    print("   ---------------------------------------------")
    print("   the three as named                    : %5d  = %.4f of unparsed  = %.4f of the corpus"
          % (named_n, named_n / len(unparsed), named_n / n))
    print("   residue the architect did NOT name    : %5d  = %.4f of unparsed"
          % (len(unparsed) - named_n, (len(unparsed) - named_n) / len(unparsed)))
    print()
    print("   reading the lead-in class as the whole family (part/appendix-level and")
    print("   untargeted lead-ins are the same drafting device one level out):")
    broad = (named_n - len(buckets["B_lead_in_section_named"]) + lead_n
             + len(buckets["D_document_opener"])
             + len(buckets["E_continuation_fragment_no_operation"])
             + len(buckets["F_part_or_appendix_level_operation"]))
    print("   A + lead-in family + C + opener + continuation + part-level: %5d  = %.4f of unparsed"
          % (broad, broad / len(unparsed)))
    print()

    # --- is any of it OUR bug rather than FR drafting? --------------------------------
    print("-- 4. IS THE RESIDUE OUR DEFECT OR THE CORPUS'S SHAPE? -------------------")
    print("   The split-metric is legitimate only if what it stops gating is NOT our")
    print("   own parser bug. Three probes:")
    print()
    z = buckets["Z_UNEXPECTED_operation_and_target"]
    print("   4a. elements with an operation AND a target yet parsed==False : %d" % len(z))
    print("       (a non-zero here would mean the record contradicts P6)")
    for r in z[:5]:
        print("       | %s" % r["text"][:100])
    print()
    missed = [r for r in unparsed
              if r["operation"] and not r["designation"] and not r["anchor"]
              and RE_ANY_DESIG.search(r["text"])]
    print("   4b. unparsed, has an operation, no designation recorded, yet the raw")
    print("       text contains a `(x)`-shaped group P5 could have taken : %d" % len(missed))
    for r in missed[:6]:
        print("       | %s" % r["text"][:110])
    print("       -> inspect: P5 excludes the span matched as a section by P2, so a")
    print("          citation like 90.213(a) contributes no designation of its own.")
    print()
    uq = [r for r in recs if r["unclosed_quote"]]
    print("   4c. unclosed_quote (P1's own honest failure counter)          : %d" % len(uq))
    print("       parse_rate ceiling lost to it at most                     : %.6f"
          % (len(uq) / n))
    print()

    # --- what the split metric would gate on -----------------------------------------
    print("-- 5. THE TWO PROPOSED METRICS, COMPUTED -------------------------------")
    for det in ("spec_literal", "extended"):
        g = agg["global"][det]
        print("   %-13s attribution_completeness = %d/%d = %.4f   gate 0.90 -> %s"
              % (det, g["attributed"], n, g["attributed"] / n,
                 "PASS" if g["attributed"] / n >= 0.90 else "FAIL"))
        print("   %-13s parse_completeness       = %d/%d = %.4f   (reported, not gated)"
              % ("", g["parsed"], n, g["parsed"] / n))
        print("   %-13s ORIGINAL completeness    = %d/%d = %.4f   gate 0.90 -> %s"
              % ("", g["complete"], n, g["complete"] / n,
                 "PASS" if g["complete"] / n >= 0.90 else "FAIL"))
    print()
    print("   NOTE: the gate CH-02 actually took was spec_literal. Its")
    print("   attribution_completeness is %.4f, which FAILS the 0.90 gate. The"
          % (lit["attributed"] / n))
    print("   architect quoted only the extended figure.")
    print()

    # --- per-document, both metrics --------------------------------------------------
    print("-- 6. PER-DOCUMENT attribution_completeness ----------------------------")
    per = agg["per_document"]
    vals = sorted((d["extended"]["attributed"] / d["extended"]["total"])
                  for d in per.values())
    lvals = sorted((d["spec_literal"]["attributed"] / d["spec_literal"]["total"])
                   for d in per.values())

    def pct(xs, q):
        return xs[min(len(xs) - 1, int(q * (len(xs) - 1) + 0.5))]

    for name, xs in (("extended", vals), ("spec_literal", lvals)):
        print("   %-13s docs=%d  min=%.4f  p25=%.4f  median=%.4f  p75=%.4f  max=%.4f"
              % (name, len(xs), xs[0], pct(xs, .25), pct(xs, .5), pct(xs, .75), xs[-1]))
        ge90 = sum(1 for v in xs if v >= 0.90)
        ge80 = sum(1 for v in xs if v >= 0.80)
        zero = sum(1 for v in xs if v == 0.0)
        print("   %-13s docs >= 0.90 : %d   docs >= 0.80 : %d   docs == 0 : %d"
              % ("", ge90, ge80, zero))
    print()

    # --- the harder candidates -------------------------------------------------------
    print("-- 7. STRICTLY-HARDER CANDIDATE GATES, COMPUTED ------------------------")
    pm = sum(1 for r in recs if r["part_mismatch_extended"])
    dis = sum(1 for r in recs if r["detector_disagrees"])
    correct = sum(1 for r in recs
                  if r["attributed_extended"] and not r["part_mismatch_extended"])
    agree = sum(1 for r in recs
                if r["attributed_extended"] and not r["part_mismatch_extended"]
                and not r["detector_disagrees"])
    print("   part_mismatch (extended)                       : %d" % pm)
    print("   detector_disagrees                             : %d" % dis)
    print("   H1 attributed AND part-consistent              : %d/%d = %.4f  gate 0.90 -> %s"
          % (correct, n, correct / n, "PASS" if correct / n >= 0.90 else "FAIL"))
    print("   H2 attributed AND part-consistent AND detectors agree : %d/%d = %.4f  gate 0.90 -> %s"
          % (agree, n, agree / n, "PASS" if agree / n >= 0.90 else "FAIL"))
    print()

    # --- operation mix ---------------------------------------------------------------
    print("-- 8. OPERATION MIX, WHOLE CORPUS --------------------------------------")
    c = Counter(r["operation"] or "none" for r in recs)
    for k in ("revise", "add", "remove", "redesignate", "amend", "none"):
        print("   %-14s %6d" % (k, c[k]))
    assert sum(c.values()) == n
    print("   %-14s %6d   ASSERTED == %d" % ("TOTAL", sum(c.values()), n))
    print()

    # --- worked examples, one per bucket ---------------------------------------------
    print("-- 9. ONE VERBATIM EXAMPLE PER BUCKET ----------------------------------")
    for key, rows in buckets.items():
        if not rows:
            print("   %s: (zero occurrences)" % key)
            continue
        print("   %s  n=%d" % (key, len(rows)))
        print("     | %s" % rows[0]["text"][:150])
    print()
    print("=" * 78)
    print("END. Every count above is derived from the frozen records at read time;")
    print("nothing in data/ was written (hard rule 11).")
    print("=" * 78)


if __name__ == "__main__":
    main()
