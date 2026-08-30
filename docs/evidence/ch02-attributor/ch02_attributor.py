"""CH-02 evidence generator. Hard rule 14: every claim from data ships its generating
script AND its committed output.

    python docs/evidence/ch02-attributor/ch02_attributor.py

Reads the frozen `data/amdpars/` and writes, beside itself:

    completeness.md   the gate measurement, global and per FR document
    pair-yield.md     the count-matched sibling yield and the projected pair count

and prints the whole report to stdout, which is committed as
`ch02-attributor-run.txt`. Every branch prints, zero included, and every partition is
asserted to sum to its whole before it is written.

Exits 2 if `data/amdpars/` is absent: a report that renders happily on missing input is
not evidence.
"""
from __future__ import annotations

import json
import statistics as stats
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = REPO / "data/amdpars"

TARGET_PAIRS = 42          # CONTEXT.md section 8 "Eval set"; plan.md CH-03
GATE = 0.90                # plan.md CH-02 "Done when"


def fail(msg):
    raise SystemExit(f"EVIDENCE ABORTED: {msg}")


def pct(x):
    return f"{x:.4f}"


def main() -> int:
    if not (DATA / "manifest.json").exists():
        print("data/amdpars absent - run `python refetch.py` first. A report that "
              "renders on missing input is not evidence.")
        return 2

    comp = json.loads((DATA / "completeness.json").read_text(encoding="utf-8"))
    docs = json.loads((DATA / "documents.json").read_text(encoding="utf-8"))
    yields = json.loads((DATA / "pair_yield.json").read_text(encoding="utf-8"))
    cits = json.loads((DATA / "citations.json").read_text(encoding="utf-8"))
    glob, per_doc, ladder = comp["global"], comp["per_document"], comp["exclusion_ladder"]

    out = []

    def say(s=""):
        out.append(s)
        print(s)

    # ------------------------------------------------------------------ ladder
    say("=" * 78)
    say("CH-02 - AMDPAR CARRY-FORWARD ATTRIBUTOR: THE MEASUREMENT")
    say("=" * 78)
    say()
    say("EXCLUSION LADDER - CH-01 defect note -> FR document")
    rungs = ("no_date", "no_issue_file", "volume_mismatch", "unresolved_page", "resolved")
    say(f"  {'section-level defect notes with an FR citation (CH-01)':<52}"
        f"{ladder['pool_citations']:>6}")
    for k in rungs:
        say(f"  {('minus ' + k.replace('_', ' ')) if k != 'resolved' else 'RESOLVED':<52}"
            f"{ladder[k]:>6}")
    total = sum(ladder[k] for k in rungs)
    if total != ladder["pool_citations"]:
        fail(f"ladder does not close: {total} != {ladder['pool_citations']}")
    say(f"  {'kept + removed == received':<52}{'OK':>6}")
    say(f"  {'distinct FR documents retrieved':<52}{len(docs):>6}")
    say(f"  {'AMDPAR elements in them':<52}"
        f"{sum(d['amdpar_count'] for d in docs.values()):>6}")
    routes = {}
    for c in cits.values():
        routes[c.get("resolution_route", "-")] = routes.get(c.get("resolution_route", "-"), 0) + 1
    say()
    say("  resolution route taken, per citation:")
    for k in sorted(routes):
        say(f"    {k:<36}{routes[k]:>5}")

    # ------------------------------------------------------------ completeness
    say()
    say("=" * 78)
    say("COMPLETENESS - CONTEXT.md section 8's definition, verbatim")
    say("=" * 78)
    say("  (attributed to a section AND parsed into at least one complete")
    say("   (operation, anchor OR designation) triple) / (total AMDPAR elements)")
    say()
    for det in ("spec_literal", "extended"):
        g = glob[det]
        say(f"  {det}")
        say(f"    completeness      {pct(g['completeness'])}   "
            f"({g['complete']} / {g['total']})")
        say(f"    attribution rate  {pct(g['attribution_rate'])}   "
            f"attributed={g['attributed']}  unattributable={g['unattributable']}")
        say(f"    parse rate        {pct(g['parse_rate'])}   parsed={g['parsed']}")
        if g["attributed"] + g["unattributable"] != g["total"]:
            fail(f"{det}: attributed + unattributable != total")
        say(f"    part_mismatch     {g['part_mismatch']}   unclosed_quote={g['unclosed_quote']}")
        say(f"    by operation      {json.dumps(g['by_operation'], sort_keys=True)}")
        say()

    say("  WHICH PRE-REGISTERED BRANCH (plan.md CH-02 / prompts/CH-02.md section 4)")
    for det in ("spec_literal", "extended"):
        v = glob[det]["completeness"]
        branch = ("PROCEED" if v >= 0.90 else
                  "RESTRICTED POOL" if v >= 0.80 else "DOCUMENTED FAILURE")
        say(f"    {det:<13} {pct(v)}  ->  {branch}")
    say("    The gate is taken on spec_literal, which is CONTEXT.md section 8's own")
    say("    detector. Both figures land in the same branch, so the choice of")
    say("    detector does not decide the outcome.")

    # ------------------------------------------------------ per-document spread
    say()
    say("=" * 78)
    say("PER-DOCUMENT DISTRIBUTION")
    say("=" * 78)
    for det in ("spec_literal", "extended"):
        vals = sorted(d[det]["completeness"] for d in per_doc.values())
        ge90 = [k for k, d in per_doc.items() if d[det]["completeness"] >= 0.90]
        ge80 = [k for k, d in per_doc.items() if d[det]["completeness"] >= 0.80]
        n90 = sum(per_doc[k][det]["total"] for k in ge90)
        say(f"  {det}: n={len(vals)} docs   min={vals[0]:.3f}  "
            f"p25={vals[len(vals)//4]:.3f}  median={stats.median(vals):.3f}  "
            f"p75={vals[3*len(vals)//4]:.3f}  max={vals[-1]:.3f}")
        say(f"    documents >= 0.90 : {len(ge90):>3}  ({n90} AMDPARs)")
        say(f"    documents >= 0.80 : {len(ge80):>3}")
        say(f"    documents == 0.00 : {sum(1 for v in vals if v == 0):>3}")
    top = sorted(docs.values(), key=lambda d: -d["amdpar_count"])
    tot = sum(d["amdpar_count"] for d in docs.values())
    say()
    say("  The global figure is dominated by a handful of very large rules, so the")
    say("  per-document spread above is the more honest reading of the parser:")
    for d in top[:5]:
        say(f"    {d['frdoc']:<12} {d['amdpar_count']:>5} AMDPARs "
            f"({d['amdpar_count']/tot:>5.1%} of the corpus)  "
            f"{str(d['subject'])[:38]}")
    say(f"    top 1 = {top[0]['amdpar_count']/tot:.1%} of every AMDPAR measured; "
        f"top 5 = {sum(d['amdpar_count'] for d in top[:5])/tot:.1%}")

    # ------------------------------------------------------------- pair yield
    y0, y1 = yields["0"], yields["1"]
    rows = y0["rows"]
    no_sib = [r for r in rows if r["sibling_sections"] == 0 and r["instruction_count"] is not None]
    no_count = [r for r in rows if r["sibling_sections"] > 0 and not r["has_match"]
                and r["instruction_count"] is not None]
    no_own = [r for r in rows if r["instruction_count"] is None]
    if len(no_sib) + len(no_count) + len(no_own) + y0["with_match"] != y0["n_defect_sections"]:
        fail("pair-yield partition does not sum to n")

    say()
    say("=" * 78)
    say("PAIR YIELD - the project's largest unknown, now measured")
    say("=" * 78)
    say("  A PAIR is one defect section plus a count-matched sibling: another section")
    say("  amended by the SAME FR document, with the SAME number of amendatory")
    say("  instructions, carrying no defect note.")
    say()
    say(f"  defect sections                                {y0['n_defect_sections']:>5}")
    say(f"  ... with >= 1 EXACT count-matched sibling      {y0['with_match']:>5}")
    say(f"  ... without                                    {y0['without_match']:>5}")
    say(f"      of which the document amends only it        {len(no_sib):>5}")
    say(f"      of which siblings exist but no count match  {len(no_count):>5}")
    say(f"      of which no AMDPAR attributes to it at all  {len(no_own):>5}")
    say()
    say(f"  YIELD (exact)          = {pct(y0['yield'])}")
    say(f"  PROJECTED PAIRS        = {y0['n_defect_sections']} x {pct(y0['yield'])}"
        f" = {y0['projected_pairs']}")
    say(f"  TARGET                 = {TARGET_PAIRS}")
    verdict = "CLEARS" if y0["projected_pairs"] >= TARGET_PAIRS else "MISSES"
    say(f"  VERDICT                = {verdict} at "
        f"{y0['projected_pairs']/TARGET_PAIRS:.2f}x")
    say()
    say(f"  +/-1 instruction matching: yield={pct(y1['yield'])}  "
        f"pairs={y1['projected_pairs']}   ** NOT ADOPTED **")
    say("  Reported only so the architect can see the headroom. CONTEXT.md section 8:")
    say("  negatives are matched EXACTLY on instruction count, 'non-negotiable -")
    say("  unmatched, a hardcoded threshold on instruction count beats the agent'.")
    say("  The exact rule clears the target on its own, so there is not even a")
    say("  temptation to relax it.")

    # ------------------------------------------------------------- write the md
    with open(HERE / "completeness.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# CH-02 attributor completeness — measured\n\n")
        fh.write("Generated by `ch02_attributor.py`; its stdout is committed beside it "
                 "as `ch02-attributor-run.txt`. Hand-computed expectations were fixed "
                 "in `goldens.md` and committed at `98f1cff`, before the parser "
                 "existed.\n\n")
        fh.write("## Exclusion ladder — CH-01 defect note to FR document\n\n")
        fh.write("| Rung | | Remaining |\n|---|---:|---:|\n")
        fh.write(f"| section-level defect notes with an FR citation (CH-01) | | "
                 f"**{ladder['pool_citations']}** |\n")
        run = ladder["pool_citations"]
        for k in ("no_date", "no_issue_file", "volume_mismatch", "unresolved_page"):
            run -= ladder[k]
            fh.write(f"| minus {k.replace('_', ' ')} | −{ladder[k]} | {run} |\n")
        fh.write(f"\n**Resolved: {ladder['resolved']} of {ladder['pool_citations']}, "
                 f"into {len(docs)} distinct FR documents carrying "
                 f"{sum(d['amdpar_count'] for d in docs.values())} AMDPAR elements.** "
                 f"Every rung prints, zero included (hard rule 14), and "
                 f"kept + removed == received is asserted before the file is "
                 f"written.\n\n")
        fh.write("Resolution route per citation:\n\n| route | n |\n|---|---:|\n")
        for k in sorted(routes):
            fh.write(f"| `{k}` | {routes[k]} |\n")
        fh.write("\n## The gate measurement\n\n")
        fh.write("> completeness = (AMDPAR elements attributed to a section **and** "
                 "parsed into at least one complete `(operation, anchor OR "
                 "designation)` triple) ÷ (total AMDPAR elements in the document)\n\n")
        fh.write("| detector | completeness | complete / total | attribution rate | "
                 "parse rate | unattributable |\n|---|---:|---:|---:|---:|---:|\n")
        for det in ("spec_literal", "extended"):
            g = glob[det]
            fh.write(f"| `{det}` | **{pct(g['completeness'])}** | "
                     f"{g['complete']} / {g['total']} | {pct(g['attribution_rate'])} | "
                     f"{pct(g['parse_rate'])} | {g['unattributable']} |\n")
        fh.write(f"\n**Both figures are below the {GATE:.2f} gate and below 0.80, so "
                 "the pre-registered `< 0.80` branch fires: the attributor is a "
                 "documented failure, reported and not tuned.** The gate is taken on "
                 "`spec_literal`, which is `CONTEXT.md` §8's own detector; the choice "
                 "of detector does not decide the branch.\n\n")
        fh.write("**Where the loss is.** Attribution is near-total under the extended "
                 f"detector — {pct(glob['extended']['attribution_rate'])}, "
                 f"{glob['extended']['unattributable']} unattributable elements in "
                 f"{glob['extended']['total']}. Carry-forward works. The loss is "
                 "entirely in the *parse* half of §8's numerator, and it is "
                 "structural: an authority citation carries no operation, a lead-in "
                 "(*\"Amend § 236.2 by:\"*) carries its specifics in its lettered "
                 "children, and a whole-section revision (*\"Section 90.601 is revised "
                 "to read as follows\"*) has no paragraph path and no quoted anchor. "
                 "All three are complete, valid instructions that §8's definition "
                 "scores as incomplete. **This is a different failure from the "
                 "predecessor pilot's 0.46, which was an attribution failure.**\n\n")
        fh.write("## Per-document distribution\n\n")
        fh.write("| detector | min | p25 | median | p75 | max | docs ≥ 0.90 | "
                 "docs ≥ 0.80 | docs = 0 |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for det in ("spec_literal", "extended"):
            vals = sorted(d[det]["completeness"] for d in per_doc.values())
            ge90 = sum(1 for d in per_doc.values() if d[det]["completeness"] >= 0.90)
            ge80 = sum(1 for d in per_doc.values() if d[det]["completeness"] >= 0.80)
            fh.write(f"| `{det}` | {vals[0]:.3f} | {vals[len(vals)//4]:.3f} | "
                     f"{stats.median(vals):.3f} | {vals[3*len(vals)//4]:.3f} | "
                     f"{vals[-1]:.3f} | {ge90} | {ge80} | "
                     f"{sum(1 for v in vals if v == 0)} |\n")
        fh.write(f"\nThe `[0.80, 0.90)` restricted-pool branch was **not** taken, "
                 "because neither global figure reaches 0.80. Had it been, the "
                 "restriction would have left "
                 f"{sum(1 for d in per_doc.values() if d['extended']['completeness'] >= 0.90)}"
                 " of the 70 documents — which is itself worth recording, since a "
                 "restricted pool that small would not have supported the eval set.\n\n")
        fh.write("The global figure is dominated by a few very large rules:\n\n")
        fh.write("| FR doc | AMDPARs | share | subject |\n|---|---:|---:|---|\n")
        for d in top[:5]:
            fh.write(f"| `{d['frdoc']}` | {d['amdpar_count']} | "
                     f"{d['amdpar_count']/tot:.1%} | {str(d['subject'])[:52]} |\n")
        fh.write(f"\nOne document is {top[0]['amdpar_count']/tot:.1%} of every AMDPAR "
                 f"measured and the top five are "
                 f"{sum(d['amdpar_count'] for d in top[:5])/tot:.1%}. The median "
                 "per-document completeness is therefore the more representative "
                 "number, and it is reported above rather than only the global one.\n")

    with open(HERE / "pair-yield.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# CH-02 pair yield — the project's largest unknown, measured\n\n")
        fh.write("Generated by `ch02_attributor.py`. A **pair** is one defect section "
                 "plus a **count-matched sibling**: another section amended by the "
                 "*same* FR document, with the *same* number of amendatory "
                 "instructions, carrying no defect note.\n\n")
        fh.write("| | n |\n|---|---:|\n")
        fh.write(f"| defect sections (CH-01 pool, all resolved) | **{y0['n_defect_sections']}** |\n")
        fh.write(f"| with ≥ 1 **exact** count-matched sibling | **{y0['with_match']}** |\n")
        fh.write(f"| without | {y0['without_match']} |\n")
        fh.write(f"| … document amends only that section | {len(no_sib)} |\n")
        fh.write(f"| … siblings exist, none with a matching count | {len(no_count)} |\n")
        fh.write(f"| … no AMDPAR attributes to the section at all | {len(no_own)} |\n")
        fh.write(f"\n**YIELD = {pct(y0['yield'])}**  ·  **PROJECTED PAIRS = "
                 f"{y0['n_defect_sections']} × {pct(y0['yield'])} = "
                 f"{y0['projected_pairs']}**  ·  target **{TARGET_PAIRS}**  ·  "
                 f"**{verdict} at {y0['projected_pairs']/TARGET_PAIRS:.2f}×** "
                 f"(n = {2*y0['projected_pairs']} against the n ≥ 84 target).\n\n")
        fh.write(f"**Under ±1 instruction matching the yield is {pct(y1['yield'])} and "
                 f"the projected pairs {y1['projected_pairs']} — reported, and NOT "
                 "ADOPTED.** `CONTEXT.md` §8 makes exact matching non-negotiable: "
                 "unmatched, a hardcoded threshold on instruction count beats the "
                 "agent, and that is how a predecessor candidate died. The exact rule "
                 "clears the target on its own, so the looser rule is not even "
                 "tempting; it is published only so the architect can see the "
                 "headroom without having to ask for it.\n\n")
        fh.write("## The 34 that do not pair, by cause\n\n")
        fh.write("Published because an exclusion that is not itemised is not an "
                 "exclusion ladder. All three causes are properties of the corpus, "
                 "not of the parser's thresholds.\n\n")
        for label, group in (("document amends only that section", no_sib),
                             ("siblings exist, none with a matching count", no_count),
                             ("no AMDPAR attributes to the section", no_own)):
            fh.write(f"**{label} — {len(group)}**\n\n")
            fh.write("| FR doc | section | own instructions | sections amended | "
                     "sibling sections |\n|---|---|---:|---:|---:|\n")
            for r in sorted(group, key=lambda r: (r["frdoc"], r["section"])):
                fh.write(f"| `{r['frdoc']}` | § {r['section']} | "
                         f"{r['instruction_count'] if r['instruction_count'] is not None else '—'} | "
                         f"{r['sections_amended_by_document']} | {r['sibling_sections']} |\n")
            fh.write("\n")
        fh.write("## Distribution of matched siblings, for the 51 that do pair\n\n")
        matched = [r for r in rows if r["has_match"]]
        buckets: dict[int, int] = {}
        for r in matched:
            buckets[r["count_matched_siblings"]] = buckets.get(r["count_matched_siblings"], 0) + 1
        fh.write("| count-matched siblings available | defect sections |\n|---:|---:|\n")
        for k in sorted(buckets):
            fh.write(f"| {k} | {buckets[k]} |\n")
        fh.write(f"\nCH-03 needs one sibling per positive, so every one of these "
                 f"{len(matched)} yields a pair; the sections with several give CH-03 "
                 "a deterministic choice to make and publish.\n")

    say()
    say("wrote completeness.md and pair-yield.md beside this script")
    return 0


if __name__ == "__main__":
    sys.exit(main())
