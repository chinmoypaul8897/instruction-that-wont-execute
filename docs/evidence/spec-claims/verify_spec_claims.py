"""Hard rule 14, applied to `CONTEXT.md` itself: every numeral gets an evidence path.

    "Any claim from data ships its generating script AND its committed output under
     docs/evidence/. Zero-occurrence branches print as zeros."

`CONTEXT.md` is LAW and it is dense with measurements. Most were taken by earlier
chunks and frozen; some come from a pre-competition pilot that **is not in this
repository at all**. This script sorts them into three honest piles:

    REPRODUCES     re-derived here from committed artefacts, and it matches
    DIFFERS        re-derived here, and it does NOT match  <- a finding
    NOT-IN-REPO    cannot be re-derived from anything committed; recorded as such

**NOT-IN-REPO is not a failure to be hidden.** `CONTEXT.md` §3 already flags its own
pilot figures as *provenance-unverified*. This turns that warning into a per-number
inventory a judge can check, instead of a sentence a reader has to trust.

Every re-derivation reads only committed artefacts under `data/`. No network.

    python docs/evidence/spec-claims/verify_spec_claims.py
    # committed output: spec-claims.txt / spec-claims.json
"""
from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

OUT = Path(__file__).resolve().parent

REPRODUCES, DIFFERS, NOT_IN_REPO = "REPRODUCES", "DIFFERS", "NOT-IN-REPO"

REFERENCE_TITLES = {"12", "20", "21", "24", "26", "40", "42", "45", "49"}


def load():
    d = {}
    d["ednotes"] = [json.loads(l) for l in
                    (REPO / "data/ednotes/ednotes.jsonl").read_text(encoding="utf-8")
                    .splitlines() if l.strip()]
    d["defects"] = [json.loads(l) for l in
                    (REPO / "data/ednotes/defect_notes.jsonl").read_text(encoding="utf-8")
                    .splitlines() if l.strip()]
    d["counts"] = json.loads((REPO / "data/ednotes/counts.json").read_text(encoding="utf-8"))
    d["documents"] = json.loads((REPO / "data/amdpars/documents.json")
                                .read_text(encoding="utf-8"))
    d["citations"] = json.loads((REPO / "data/amdpars/citations.json")
                                .read_text(encoding="utf-8"))
    d["completeness"] = json.loads((REPO / "data/amdpars/completeness.json")
                                   .read_text(encoding="utf-8"))
    d["v11"] = json.loads((REPO / "data/attribution-v11/completeness_v11.json")
                          .read_text(encoding="utf-8"))
    return d


def claims(d):
    """(section, claim, spec_value, rederived_value_or_None, note)."""
    ed, defects = d["ednotes"], d["defects"]
    cits, docs = d["citations"], d["documents"]
    g = d["completeness"]["global"]
    v11 = d["v11"]["global"]

    resolved = [c for c in cits.values() if c.get("status") == "resolved"]
    ref_ed = [e for e in ed if str(e.get("title")) in REFERENCE_TITLES]
    ref_def = [e for e in defects if str(e.get("title")) in REFERENCE_TITLES]

    out = []
    A = out.append

    # ---- §8 MEASURED AT CH-01 -------------------------------------------------
    A(("§8 CH-01", "`<EDNOTE>` extracted", 2428, len(ed), ""))
    A(("§8 CH-01", "codification-defect notes", 107, len(defects), ""))
    A(("§8 CH-01", "... section-level", 86,
       sum(1 for r in defects if r.get("section_level")), ""))
    A(("§8 CH-01", "... with a resolvable FR citation (the pool gate)", 85,
       sum(1 for r in defects if r.get("section_level") and r.get("fr_citation")), ""))
    pool = [r for r in defects if r.get("section_level") and r.get("fr_citation")]
    A(("§8 CH-01", "spread over titles (of the 85-item pool)", 25,
       len({str(r.get("title")) for r in pool}),
       "the first version of this script counted titles over all 107 defect notes "
       "and got 28, and reported CONTEXT.md as wrong. The SCRIPT was wrong: the row "
       "sits in the pool block and 25 is right for the pool"))
    A(("§8 CH-01", "distinct FR CITATION STRINGS in the pool", 78,
       len({r["fr_citation"] for r in pool}), ""))
    A(("§8 CH-01", "**distinct FR DOCUMENTS** - section 8 labels this 78", 78, len(docs),
       "MISLABELLED IN THE SPEC. 78 is the number of distinct CITATION STRINGS; the "
       "85 citations resolve to 70 distinct FR documents. Section 8 says the figure "
       "'bounds the count-matched pair yield', and the real bound is 70. QUESTIONS.md Q18"))

    # ---- §8 the 9-title reference ---------------------------------------------
    A(("§8 reference", "total EDNOTEs over 9 reference titles", 903, len(ref_ed), ""))
    A(("§8 reference", "codification-defect notes", 44, len(ref_def), ""))
    A(("§8 reference", "carry their own FR citation", 44,
       sum(1 for r in ref_def if r.get("fr_citation")), ""))
    A(("§8 reference", "section-level (notes that NAME a section)", 38,
       sum(1 for r in ref_def if r.get("names_section")), ""))
    A(("§8 reference", "section-level (notes that SIT INSIDE one)", 36,
       sum(1 for r in ref_def if r.get("section_level")), ""))

    # ---- §8 the attributor -----------------------------------------------------
    A(("§8 gate", "completeness, spec-literal", 0.5080,
       round(g["spec_literal"]["completeness"], 4), ""))
    A(("§8 gate", "completeness, extended", 0.6643,
       round(g["extended"]["completeness"], 4), ""))
    A(("§8 gate", "attribution, spec-literal", 0.7613,
       round(g["spec_literal"]["attribution_rate"], 4), ""))
    A(("§8 gate", "attribution, extended", 0.9865,
       round(g["extended"]["attribution_rate"], 4), ""))
    A(("§8 gate", "total AMDPAR elements", 8752, g["extended"]["total"], ""))
    A(("§8 gate", "attributed elements, extended (the 6,663 control base)", 6663,
       g["spec_literal"]["attributed"], ""))
    A(("§8 v1.1", "part-consistent attribution 0.9066", 0.9066, None,
       "computed at SPEC-FIX-1 under the case-INsensitive detector; that script's "
       "output is committed but the figure is not recomputed here"))
    A(("§8 v1.1", "`part_mismatch` elements, case-insensitive", 699,
       g["extended"]["part_mismatch"], ""))
    A(("§8 v1.1", "`part_mismatch` under v1.1 (CH-03 re-measurement)", 115,
       v11["v11"]["part_mismatch"], "not in CONTEXT.md; published by CH-03"))
    A(("§8 v1.1", "\"only ~42% of AMDPARs name a section\"", 0.42,
       round(d["v11"]["names_section_rate"]["v11"]["rate"], 4),
       "Q14(b): stale in three ways. v11 measures 0.2964"))

    # ---- §8 leakage containment ------------------------------------------------
    vol = REPO / "cfr2024t40v5.xml"
    if vol.exists():
        import xml.etree.ElementTree as ET
        root = ET.parse(str(vol)).getroot()
        parent = {c: p for p in root.iter() for c in p}

        def inside_section(el):
            while el in parent:
                el = parent[el]
                if el.tag == "SECTION":
                    return True
            return False
        c = Counter(e.tag for e in root.iter())
        A(("§8 leakage", "`<EDNOTE>` in CFR-2024-title40-vol5", 28, c.get("EDNOTE", 0), ""))
        A(("§8 leakage", "... of which inside a `<SECTION>`", 26,
           sum(1 for e in root.iter("EDNOTE") if inside_section(e)), ""))
        A(("§8 leakage", "`<EFFDNOTP>` inside a `<SECTION>`", 2,
           sum(1 for e in root.iter("EFFDNOTP") if inside_section(e)), ""))
        A(("§8 leakage", "`<CITA>` total", 255, c.get("CITA", 0), ""))
        A(("§8 leakage", "... of which inside a `<SECTION>`", 252,
           sum(1 for e in root.iter("CITA") if inside_section(e)), ""))
        A(("§8 leakage", "volume size in bytes", 5524321, vol.stat().st_size, ""))
    else:
        A(("§8 leakage", "the whole containment block", None, None,
           "CFR-2024-title40-vol5.xml is a git-ignored raw input; run refetch.py"))

    # ---- figures that are NOT in this repository --------------------------------
    for sec, name, val, why in [
        ("§3", "pilot accuracy 0.545", 0.545, "pre-competition pilot, n=11"),
        ("§3", "pilot accuracy 0.5855", 0.5855, "pre-competition pilot, n=11"),
        ("§3", "pilot accuracy 0.52", 0.52, "pre-competition pilot, n=11"),
        ("§3", "retrieval gain +27.3 pp", 27.3, "pilot figure; CH-08 re-derives it"),
        ("§6", "state-carry sensitivity 833/1,984 = 42.0%", 0.42,
         "pilot pool; the 1,984-item corpus is not committed"),
        ("§6", "state-carry on the pilot pool 31/82", 31, "pilot pool, not committed"),
        ("§6", "26/33 and 35/42 items with no extractable anchor", 26,
         "pilot pool, not committed"),
        ("§7", "n_instructions pinned at 0.5000", 0.5,
         "pilot trivial-attack measurement; CH-04 re-derives on the real pool"),
        ("§7", "best of 26 features 0.5934 at p = 0.185", 0.5934,
         "pilot; CH-04 measured 0.6098 at within-pair p = 0.2355 on the real pool"),
        ("§9", "16 defective items in the 82-item pilot pool", 16, "pilot pool"),
        ("§10", "redesignation collision 26/1,984 = 1.31%", 0.0131,
         "pilot; CONTEXT.md already flags it as PROVISIONAL and non-reproducing"),
        ("§10", "independent naive recount 61/1,984 = 3.07%", 0.0307, "ditto"),
        ("§10", "0/68 labelled items contain a redesignation instruction", 0,
         "pilot pool"),
        ("§11", "IETF errata Rejected recall +12.0 pp", 12.0,
         "second corpus, not in this repository"),
        ("§11", "IETF errata Verified recall -4.0 pp", -4.0, "ditto"),
        ("§11", "IETF three-class policy -16.7 pp", -16.7, "ditto"),
        ("§11", "IETF net +4.0 pp at p = 0.64", 0.64, "ditto"),
    ]:
        A((sec, name, val, None, why))
    return out


def main() -> int:
    d = load()
    rows = []
    for sec, name, spec, got, note in claims(d):
        if got is None:
            status = NOT_IN_REPO
        elif isinstance(spec, float) or isinstance(got, float):
            status = REPRODUCES if abs(float(spec) - float(got)) < 5e-5 else DIFFERS
        else:
            status = REPRODUCES if spec == got else DIFFERS
        rows.append({"section": sec, "claim": name, "spec_value": spec,
                     "rederived": got, "status": status, "note": note})

    tally = Counter(r["status"] for r in rows)
    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 92)
    p("CONTEXT.md - EVERY NUMERAL, WITH AN EVIDENCE PATH OR AN HONEST ABSENCE")
    p("=" * 92)
    p("")
    p("  hard rule 14: a claim from data ships its generating script AND its output.")
    p("  This inventory sorts CONTEXT.md's own measurements into three piles.")
    p("")
    for st in (REPRODUCES, DIFFERS, NOT_IN_REPO):
        p(f"  {st:<14}{tally.get(st, 0):>4}")
    p("")
    for st, blurb in (
        (DIFFERS, "THESE DO NOT MATCH THE COMMITTED DATA. Each is a finding."),
        (REPRODUCES, "Re-derived here from committed artefacts, and they match."),
        (NOT_IN_REPO, "Cannot be re-derived from anything committed. Recorded, not hidden."),
    ):
        sel = [r for r in rows if r["status"] == st]
        p("=" * 92)
        p(f"{st}  ({len(sel)})  -  {blurb}")
        p("=" * 92)
        p("")
        if not sel:
            p("  (none)")            # hard rule 14: zero branches print as zeros
            p("")
            continue
        p(f"  {'sec':<14}{'claim':<52}{'CONTEXT.md':>14}{'re-derived':>14}")
        for r in sel:
            spec = "-" if r["spec_value"] is None else str(r["spec_value"])
            got = "-" if r["rederived"] is None else str(r["rederived"])
            p(f"  {r['section']:<14}{r['claim'][:50]:<52}{spec:>14}{got:>14}")
            if r["note"]:
                p(f"  {'':<14}   ^ {r['note']}")
        p("")

    p("=" * 92)
    p("HOW TO READ THE NOT-IN-REPO PILE")
    p("=" * 92)
    p("")
    p("  It is not a list of things that are wrong. It is a list of things a reader")
    p("  cannot check from this repository, which is a different and more useful")
    p("  statement than silence. CONTEXT.md section 3 already warns that its pilot")
    p("  figures 'trace to no committed artifact on this machine' and must not appear")
    p("  in the README, the Description or the video until CH-08 re-derives them.")
    p("  This turns that warning into a per-number inventory.")
    p("")
    text = w.getvalue()
    io.open(OUT / "spec-claims.txt", "w", encoding="utf-8", newline="\n").write(text)
    io.open(OUT / "spec-claims.json", "w", encoding="utf-8", newline="\n").write(
        json.dumps({"tally": dict(tally), "claims": rows}, indent=2, sort_keys=True) + "\n")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
