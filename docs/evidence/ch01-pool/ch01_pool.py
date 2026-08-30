"""Generate the CH-01 exclusion ladder from the frozen extraction. Evidence, hard rule 14.

Reads `data/ednotes/counts.json` - nothing else, no network, no re-parsing - and writes
`docs/evidence/ch01-pool/exclusion-ladder.md`. Its stdout is committed beside it as
`ch01-pool-run.txt` so the ladder in the repository and the run that produced it can be
diffed by anyone.

Every rung asserts that what it removed plus what it kept equals what it received. A
ladder whose rungs do not add up is a broken ladder, and that has to fail loudly here
rather than read as a clean descent from 2,000 to 200.

    python docs/evidence/ch01-pool/ch01_pool.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
COUNTS = REPO / "data" / "ednotes" / "counts.json"
LADDER = REPO / "docs" / "evidence" / "ch01-pool" / "exclusion-ladder.md"

#: `CONTEXT.md` section 8, measured before this project began, on these nine titles.
REFERENCE_TITLES = ["12", "20", "21", "24", "26", "40", "42", "45", "49"]
REFERENCE = {"ednotes": 903, "defect": 44, "with_fr": 44, "section_level": 38}

#: `plan.md` CH-03 pre-registers the gate. It is read here, never adjusted here.
POOL_GATE = 60

#: `CONTEXT.md` section 8's projection for the full corpus, and the eCFR search-API
#: figure it says undercounts by ~2.3x. Both are republished beside our number rather
#: than replaced by it (prompts/CH-01.md step 5).
EXPECTED_RANGE = (150, 250)
EXPECTED_SECTION_RANGE = (130, 210)
ECFR_SEARCH_API_FIGURE = 92


def pct(a: int, b: int) -> str:
    return f"{100.0 * a / b:.1f}%" if b else "n/a (denominator 0)"


def main() -> int:
    if not COUNTS.exists():
        print(f"missing {COUNTS} - run `python src/harvest_ednotes.py extract` first")
        return 1
    data = json.loads(COUNTS.read_text(encoding="utf-8"))
    tot, by_title = data["total"], data["by_title"]

    titles = sorted(by_title, key=int)
    n_titles = len(titles)

    # ------------------------------------------------------------------ the ladder
    r0 = n_titles
    r1 = tot["ednotes"]
    dropped_not_defect = tot["non_defect"]
    r2 = tot["defect"]
    dropped_not_section = tot["defect_not_section_level"]
    r3 = tot["defect_section_level"]
    r3_no_fr = r3 - tot["usable_section_and_fr"]
    r4 = tot["usable_section_and_fr"]

    assert r2 + dropped_not_defect == r1, "rung 2 does not sum"
    assert r3 + dropped_not_section == r2, "rung 3 does not sum"
    assert r4 + r3_no_fr == r3, "rung 4 does not sum"
    assert sum(by_title[t]["ednotes"] for t in titles) == r1, "per-title EDNOTEs != total"
    assert sum(by_title[t]["defect"] for t in titles) == r2, "per-title defect != total"
    assert sum(by_title[t]["usable_section_and_fr"] for t in titles) == r4, "per-title usable != total"

    # --------------------------------------------- the nine-title reference subset
    missing_ref = [t for t in REFERENCE_TITLES if t not in by_title]
    ref = {
        "ednotes": sum(by_title[t]["ednotes"] for t in REFERENCE_TITLES if t in by_title),
        "defect": sum(by_title[t]["defect"] for t in REFERENCE_TITLES if t in by_title),
        "with_fr": sum(by_title[t]["defect_with_fr"] for t in REFERENCE_TITLES if t in by_title),
        "section_level": sum(by_title[t]["defect_section_level"] for t in REFERENCE_TITLES if t in by_title),
        "section_or_named": sum(by_title[t]["defect_section_or_named"]
                                for t in REFERENCE_TITLES if t in by_title),
    }

    # The individual notes behind the 36-vs-38 gap, read from the frozen records rather
    # than described. CONTEXT.md s8 counts a note as section-level when it NAMES a
    # section; the prompt counts it when it SITS in one. Both ship; the gate uses the
    # prompt's, which is the smaller.
    defect_records = [
        json.loads(line) for line in
        (COUNTS.parent / "defect_notes.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    named_gap = sorted(
        (r for r in defect_records
         if r["title"] in REFERENCE_TITLES and not r["section_level"] and r["names_section"]),
        key=lambda x: (int(x["title"]), str(x["part"])))
    usable_reading_b = sum(1 for r in defect_records
                           if (r["section_level"] or r["names_section"]) and r["fr_citation"])
    no_fr = [r for r in defect_records if not r["fr_citation"]]

    # Why the projected range overshot: the nine reference titles are the LARGEST in
    # the corpus, so a per-title extrapolation from them cannot hold. Computed here
    # rather than asserted, because the conclusion contradicts the spec.
    ref_bytes = sum(by_title[t]["raw_bytes"] for t in REFERENCE_TITLES if t in by_title)
    all_bytes = sum(by_title[t]["raw_bytes"] for t in titles)
    ref_proj = ref["defect"] / len(REFERENCE_TITLES) * 50

    rate = tot["defect_notes_per_title"]
    gate_clears = r4 >= POOL_GATE

    lines: list[str] = []
    w = lines.append

    w("# CH-01 exclusion ladder — govinfo `<EDNOTE>` → the usable pool")
    w("")
    w("Generated by `docs/evidence/ch01-pool/ch01_pool.py` from `data/ednotes/counts.json`.")
    w("Its stdout is committed beside it as `ch01-pool-run.txt`. Every rung asserts that")
    w("**kept + removed == received**; the script exits non-zero if any rung fails to sum,")
    w("so a ladder that reaches the bottom is a ladder that adds up (hard rule 14).")
    w("")
    w("Source: `https://www.govinfo.gov/bulkdata/ECFR`. `www.ecfr.gov` and")
    w("`www.federalregister.gov` return HTTP 403 from this machine and were not used.")
    w("")
    w("## The ladder")
    w("")
    w("| # | Rung | Removed here | Remaining |")
    w("|---|---|---:|---:|")
    w(f"| 0 | CFR titles published as ECFR bulk XML on govinfo | — | **{r0}** |")
    w(f"| 1 | `<EDNOTE>` elements extracted structurally (not by regex) | — | **{r1:,}** |")
    w(f"| 2 | minus notes without the literal `\"could not be incorporated\"` | {dropped_not_defect:,} | **{r2}** |")
    w(f"| 3 | minus notes not inside a `<DIV8 TYPE=\"SECTION\">` (appendix / part / subpart) | {dropped_not_section} | **{r3}** |")
    w(f"| 4 | minus notes carrying no resolvable `NN FR NNNNN` citation | {r3_no_fr} | **{r4}** |")
    w("")
    w(f"**Rung 4 is the pool-gate number: {r4}.**")
    w("")
    w("Read as rates rather than counts:")
    w("")
    w(f"- codification-defect notes are **{pct(r2, r1)}** of all `<EDNOTE>` elements ({r2} of {r1:,})")
    w(f"- of those, **{pct(r3, r2)}** are section-level ({r3} of {r2})")
    w(f"- of the section-level ones, **{pct(r4, r3)}** carry an FR citation ({r4} of {r3})")
    w(f"- **defect notes per title: {rate}** — this is the figure that projects to any corpus")
    w("")
    w("## The pool gate")
    w("")
    w("`plan.md` CH-03 pre-registers: *the pool gate decides on ≥ 60 section-level defect")
    w("notes with a resolvable FR citation.* That threshold was written before this")
    w("measurement and is read here, never adjusted here (hard rule 5).")
    w("")
    w(f"| | |")
    w(f"|---|---|")
    w(f"| Pre-registered threshold | ≥ {POOL_GATE} |")
    w(f"| Measured | **{r4}** |")
    w(f"| Verdict | **{'CLEARS' if gate_clears else 'BELOW — the documented fallback triggers'}** |")
    if gate_clears:
        w(f"| Margin | {r4 - POOL_GATE} above the threshold ({r4 / POOL_GATE:.2f}×) |")
    else:
        w(f"| Shortfall | {POOL_GATE - r4} below the threshold |")
    w("")
    w("## Against the reference measurements")
    w("")
    w("`CONTEXT.md` §8 records a nine-title measurement taken before this project began.")
    w("Re-derived here from the same nine titles (12, 20, 21, 24, 26, 40, 42, 45, 49),")
    w("with today's govinfo bytes. **A deviation is a finding, not an error** — nothing was")
    w("tuned toward these numbers.")
    if missing_ref:
        w("")
        w(f"> **Incomplete:** {', '.join('title ' + t for t in missing_ref)} absent from the extraction.")
    w("")
    w("| Measure | `CONTEXT.md` §8 | Re-derived here | Δ |")
    w("|---|---:|---:|---:|")
    for key, label in (("ednotes", "Total `<EDNOTE>`"),
                       ("defect", "Codification-defect notes"),
                       ("with_fr", "Carrying an FR citation"),
                       ("section_level", "Section-level *(container reading)*")):
        d = ref[key] - REFERENCE[key]
        w(f"| {label} | {REFERENCE[key]} | **{ref[key]}** | {d:+d} |")
    w(f"| Section-level *(names-a-section reading)* | {REFERENCE['section_level']} | "
      f"**{ref['section_or_named']}** | "
      f"{ref['section_or_named'] - REFERENCE['section_level']:+d} |")
    w("")
    w("**Three of the four reproduce exactly.** 903 `<EDNOTE>` elements, 44 defect")
    w("notes, 44 of 44 carrying an FR citation — the same integers, on today's govinfo")
    w("bytes, from an independently written parser that had never seen them. That is the")
    w("strongest evidence in this chunk that the extraction is right.")
    w("")
    w("### The fourth: 36 against 38, and why it is a definition rather than a defect")
    w("")
    w("`prompts/CH-01.md` step 5 defines section-level as **\"not appendix/part\"** — a")
    w("question about the note's *container*. `CONTEXT.md` §8's own table answers a")
    w("different question: its rows *Section-level 38/44* and *Localise below section")
    w("level 6/44* sum to 44, so its 38 counts notes that **localise to a named section**,")
    w("wherever the note itself physically sits.")
    w("")
    w("Both readings are computed. On the nine reference titles:")
    w("")
    w("| Reading | Nine titles | Full corpus |")
    w("|---|---:|---:|")
    w("| **A** — sits inside `<DIV8 TYPE=\"SECTION\">` *(the prompt's, and the gate's)* | "
      f"{ref['section_level']} | {r3} |")
    w("| **B** — A, or else names a section in its own prose *(the reference's)* | "
      f"{ref['section_or_named']} | {tot['defect_section_or_named']} |")
    w("")
    w(f"Reading B returns **{ref['section_or_named']}** on the nine titles — the reference")
    w("figure, exactly. The gap is two notes, both real, both identified:")
    w("")
    for g in named_gap:
        w(f"- **title {g['title']}, part {g['part']}**, container `{g['container_type']}`, "
          f"cites `{g['fr_citation']}` — names its section in prose but does not sit in one.")
    w("")
    w("**The pool gate is computed on reading A, the smaller of the two.** Reading B")
    w(f"would give {tot['defect_section_or_named']} section-level rather than {r3}, and "
      f"{usable_reading_b} usable rather than {r4}. Both clear the threshold, so nothing")
    w("turns on the choice — which is exactly why it is recorded now, before anything")
    w("depends on it, rather than settled later in whichever direction helps.")
    w("")
    w("## Against the projection — the largest deviation in this chunk")
    w("")
    w("| | Expected | Measured |")
    w("|---|---:|---:|")
    w(f"| Defect notes, full corpus | {EXPECTED_RANGE[0]}–{EXPECTED_RANGE[1]} | **{r2}** |")
    w(f"| Section-level | {EXPECTED_SECTION_RANGE[0]}–{EXPECTED_SECTION_RANGE[1]} | **{r3}** |")
    w("")
    w(f"**Both land below the projected range** — {r2} against "
      f"{EXPECTED_RANGE[0]}–{EXPECTED_RANGE[1]}, and {r3} against "
      f"{EXPECTED_SECTION_RANGE[0]}–{EXPECTED_SECTION_RANGE[1]}. Reported as measured.")
    w("Nothing was widened to reach the range, and the pool gate clears without it.")
    w("")
    w("### Why the projection overshot, with the arithmetic")
    w("")
    w("`CONTEXT.md` §8's range is a per-title extrapolation from the nine reference")
    w(f"titles: {ref['defect']} notes ÷ 9 titles × 50 titles = **{ref_proj:.0f}**. That step")
    w("assumes the nine are typical. They are the **largest**:")
    w("")
    w("| | Nine reference titles | Full corpus |")
    w("|---|---:|---:|")
    w(f"| Titles | 9 ({100 * 9 / n_titles:.0f}%) | {n_titles} |")
    w(f"| Raw XML bytes | {ref_bytes:,} (**{100 * ref_bytes / all_bytes:.0f}%**) | {all_bytes:,} |")
    w(f"| Defect notes | {ref['defect']} (**{100 * ref['defect'] / r2:.0f}%**) | {r2} |")
    w("")
    w("They include title 40, the largest at 161 MB, and title 26, the second largest.")
    w(f"Nine titles that are {100 * 9 / n_titles:.0f}% of the corpus by count but "
      f"**{100 * ref_bytes / all_bytes:.0f}% by bytes** cannot")
    w(f"carry a per-title extrapolation, and this one missed by **{ref_proj / r2:.2f}×**.")
    w("")
    w("### And that same factor was attributed to the wrong cause")
    w("")
    w(f"`CONTEXT.md` §8 states the eCFR search API's figure of {ECFR_SEARCH_API_FIGURE}")
    w("*\"undercounts by ~2.3×\"*. Measured on govinfo and republished beside it rather")
    w("than in place of it, as `prompts/CH-01.md` step 5 requires:")
    w("")
    w("| | |")
    w("|---|---:|")
    w(f"| eCFR search API | {ECFR_SEARCH_API_FIGURE} |")
    w(f"| govinfo, this chunk | **{r2}** |")
    w(f"| Actual ratio | **{r2 / ECFR_SEARCH_API_FIGURE:.2f}×** |")
    w(f"| Over-projection factor of the nine-title extrapolation | **{ref_proj / r2:.2f}×** |")
    w("")
    w(f"The eCFR API undercounts by **{r2 / ECFR_SEARCH_API_FIGURE:.2f}×**, not 2.3×. The")
    w(f"**{ref_proj / r2:.2f}×** belongs to the extrapolation, not to the API. The two figures")
    w("were reconciled by assuming the API was wrong, when what was wrong was the")
    w(f"arithmetic that produced the expectation — {ECFR_SEARCH_API_FIGURE} was far closer to")
    w("the truth than the range built to discredit it.")
    w("")
    w("This is hard rule 15 — *verify before you relay* — firing on this project's own")
    w("spec. Neither figure was tuned and both are printed. `CONTEXT.md` is protected")
    w("read-only for a build session, so the correction is recorded here and in")
    w("`PROGRESS.md` for the architect rather than applied.")
    w("")
    w("## The one defect note with no FR citation — an upstream typo, not a parser miss")
    w("")
    w(f"Rung 4 removes **{len(no_fr)}** note of {r2}. `CONTEXT.md` §8 records 44/44 on the")
    w("nine reference titles and that reproduces exactly; across all 49 titles the rate")
    w(f"is {r2 - len(no_fr)}/{r2}. The single exception was read back from the source:")
    w("")
    for r in no_fr:
        w(f"> **Title {r['title']}, part {r['part']}, § {r['section']}** — *“{r['text']}”*")
    w("")
    w("The volume number is present and **the page number is simply missing from the")
    w("published note** (`At 83 FR , May 1,2018`). No extractor can resolve that to a")
    w("document. It is excluded, counted, and shown rather than quietly dropped; FR")
    w(f"resolution is deterministic for the other {r2 - len(no_fr)}.")
    w("")
    w("## Two looser readings this ladder declined to take")
    w("")
    w("Both are computed and printed. An unprinted zero is indistinguishable from an")
    w("unasked question, and widening a filter after seeing the result is exactly the")
    w("move hard rule 5 forbids.")
    w("")
    w("| Reading not taken | Extra notes it would have admitted |")
    w("|---|---:|")
    w(f"| case-insensitive `\"could not be incorporated\"` | {tot['case_insensitive_only_extra']} |")
    w(f"| the literal appearing in `<HED>` but not the note body | {tot['literal_in_hed_only']} |")
    w("")
    w("## Where the non-section-level defect notes actually sit")
    w("")
    w("Rung 3 removes them. They are real defects; they are simply not localisable to a")
    w("section, so an eval item built on one has no anchor.")
    w("")
    w("| Container | Defect notes |")
    w("|---|---:|")
    for k, v in sorted(tot["defect_container_types"].items(), key=lambda kv: -kv[1]):
        w(f"| `{k}` | {v} |")
    w("")
    w("## Notes carrying more than one FR citation")
    w("")
    w(f"**{tot['defect_multi_fr']}** of {r2} defect notes cite more than one FR document.")
    w("`fr_citation` is the **first** match — the amending rule the note is about. The")
    w("later citations are context (a stay, a superseding correction). Golden G4 pins")
    w("this; reading the last match would attribute the defect to the wrong rule at CH-02.")
    w("")
    w("## Per title")
    w("")
    w("| Title | raw XML bytes | `<EDNOTE>` | defect | % of EDNOTEs | section-level | with FR | usable |")
    w("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for t in titles:
        b = by_title[t]
        w(f"| {t} | {b['raw_bytes']:,} | {b['ednotes']:,} | {b['defect']} | "
          f"{b['defect_pct_of_ednotes']}% | {b['defect_section_level']} | "
          f"{b['defect_with_fr']} | {b['usable_section_and_fr']} |")
    w(f"| **total** | **{sum(by_title[t]['raw_bytes'] for t in titles):,}** | **{r1:,}** | "
      f"**{r2}** | **{pct(r2, r1)}** | **{r3}** | **{tot['defect_with_fr']}** | **{r4}** |")
    w("")
    w("## Provenance")
    w("")
    w("`data/ednotes/manifest.json` carries the SHA-256 of every frozen artefact **and of")
    w("every raw title XML the numbers came from**, so this ladder is pinned to specific")
    w("upstream bytes rather than to \"govinfo, at some point\". `data/ednotes/")
    w("source_index.json` carries govinfo's announced size and last-modified stamp per")
    w("title; it is deliberately outside the hashed set, because that stamp moves when a")
    w("title is re-published even if nothing that matters changed.")
    w("")
    w("Reproduce: `python refetch.py` (network) or `python refetch.py --verify-only` (none).")

    LADDER.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    # ------------------------------------------------------------------- stdout
    print("CH-01 EXCLUSION LADDER")
    print("=" * 72)
    print(f"rung 0  CFR titles on govinfo ECFR bulk              {r0:>8}")
    print(f"rung 1  <EDNOTE> elements extracted                  {r1:>8,}")
    print(f"rung 2  minus not-a-defect-note      (-{dropped_not_defect:>6,})   {r2:>8}   {pct(r2, r1)} of EDNOTEs")
    print(f"rung 3  minus not section-level      (-{dropped_not_section:>6})   {r3:>8}   {pct(r3, r2)} of defect notes")
    print(f"rung 4  minus no FR citation         (-{r3_no_fr:>6})   {r4:>8}   {pct(r4, r3)} of section-level")
    print("=" * 72)
    print(f"defect notes per title              {rate}")
    print(f"POOL GATE  pre-registered >= {POOL_GATE}       measured {r4}   "
          f"{'CLEARS' if gate_clears else 'BELOW - fallback triggers'}")
    print()
    print("NINE-TITLE REFERENCE (CONTEXT.md s8, re-derived on today's govinfo bytes)")
    for key, label in (("ednotes", "total EDNOTEs"), ("defect", "defect notes"),
                       ("with_fr", "carrying an FR citation"),
                       ("section_level", "section-level (A: container)")):
        print(f"  {label:<30} reference {REFERENCE[key]:>5}   measured {ref[key]:>5}   "
              f"delta {ref[key] - REFERENCE[key]:+d}")
    print(f"  {'section-level (B: names one)':<30} reference {REFERENCE['section_level']:>5}"
          f"   measured {ref['section_or_named']:>5}   "
          f"delta {ref['section_or_named'] - REFERENCE['section_level']:+d}"
          f"   <- B reconciles exactly")
    print("  the gap: " + "; ".join(
        f"title {g['title']} part {g['part']} in a {g['container_type']}" for g in named_gap))
    print(f"  gate uses reading A, the smaller: {r4} usable, not {usable_reading_b}")
    if missing_ref:
        print(f"  INCOMPLETE - missing titles: {', '.join(missing_ref)}")
    print()
    print("PROJECTION  <- the largest deviation in this chunk")
    print(f"  CONTEXT.md s8 expected  {EXPECTED_RANGE[0]}-{EXPECTED_RANGE[1]} defect notes, "
          f"{EXPECTED_SECTION_RANGE[0]}-{EXPECTED_SECTION_RANGE[1]} section-level")
    print(f"  measured                {r2} defect notes, {r3} section-level   <- BELOW BOTH")
    print(f"  cause: the 9 reference titles are the LARGEST - {ref_bytes:,} of "
          f"{all_bytes:,} B,")
    print(f"         {100 * ref_bytes / all_bytes:.0f}% of the corpus by bytes but only "
          f"{100 * 9 / n_titles:.0f}% by title count. Extrapolating")
    print(f"         per title gave {ref_proj:.0f}, over by {ref_proj / r2:.2f}x.")
    print(f"  eCFR search API         {ECFR_SEARCH_API_FIGURE}   "
          f"govinfo/eCFR ratio {r2 / ECFR_SEARCH_API_FIGURE:.2f}x")
    print(f"  CONTEXT.md s8 blames a ~2.3x eCFR undercount. It is not the API: the "
          f"{ref_proj / r2:.2f}x is")
    print(f"  the extrapolation's own error, and {ECFR_SEARCH_API_FIGURE} was closer to the "
          f"truth than {EXPECTED_RANGE[0]}-{EXPECTED_RANGE[1]}.")
    print()
    print("LOOSER READINGS DECLINED (both expected 0; printed either way)")
    print(f"  case-insensitive match would add   {tot['case_insensitive_only_extra']}")
    print(f"  literal in <HED> only would add    {tot['literal_in_hed_only']}")
    print()
    print(f"defect notes citing >1 FR document   {tot['defect_multi_fr']}")
    print(f"defect notes with NO FR citation     {len(no_fr)}" + (
        f"   (title {no_fr[0]['title']} s{no_fr[0]['section']}: the published note omits"
        f" the page number)" if no_fr else ""))
    print(f"non-section-level defect containers  {tot['defect_container_types']}")
    print(f"title-source disagreements           {tot['title_source_disagreements']}")
    print()
    print(f"wrote {LADDER.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
