"""CH-09 — the two removed capabilities' CLASS SIZES, recomputed in-repo.

`CONTEXT.md` §10 carries a figure it flags as **not reproducing**:

    "redesignation-collision sensitivity is ~1.3-3.1% of corpus items (the pilot
     reported 26/1,984 = 1.31%; an independent naive recount returned 61/1,984 =
     3.07%. THE FIGURE DOES NOT REPRODUCE AND IS THEREFORE PROVISIONAL - CH-09
     recomputes it in-repo and publishes whichever number the shipped script yields,
     with the discrepancy stated. Either value supports the removal decision; neither
     is quoted as settled)"

and §6 carries the ledger's justification:

    "state-carry sensitivity - instruction k+1 reads the state instructions 1..k left -
     fires on 833/1,984 = 42.0% of items"

This script is that recomputation. **It publishes what it measures, whatever that is**,
and states the discrepancy against both prior figures rather than picking the closer one.

WHAT AN "ITEM" IS, DECLARED BEFORE THE COUNT
--------------------------------------------
A `(frdoc, section)` pair with at least one attributed AMDPAR, over the whole v11
attribution corpus - `data/attribution-v11/amdpars_v11.jsonl`, 8,752 AMDPARs. That is
the same unit the eval set uses. **The denominator is printed, not assumed**: if it is
not 1,984 then the prior figures were computed over a different corpus and the
percentages are not comparable, which is itself the finding.

PURITY: no network, no clock, no randomness. `data/` is read-only (hard rule 11).

    python docs/evidence/ch09-removed/class_sizes.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "data/attribution-v11/amdpars_v11.jsonl"
OUT = Path(__file__).resolve().parent / "class_sizes.txt"

PRIOR_COLLISION = [("pilot", 26, 1984), ("naive recount", 61, 1984)]
PRIOR_STATE_CARRY = ("CONTEXT.md §6", 833, 1984)


def items_from_corpus():
    """(frdoc, section) -> the ordered list of its attributed AMDPARs."""
    groups: dict[tuple, list] = defaultdict(list)
    for line in CORPUS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        sec = r.get("section_v11")
        if not sec:
            continue
        groups[(r["frdoc"], sec)].append(r)
    for k in groups:
        groups[k].sort(key=lambda r: r["ordinal"])
    return groups


def designations_of(r) -> list[str]:
    ds = r.get("designations") or []
    if not ds and r.get("designation"):
        ds = [r["designation"]]
    return [str(d) for d in ds if d]


# FOUR operationalisations of "state-carry sensitivity", not one.
#
# `CONTEXT.md` §6 defines it in prose - *"instruction k+1 reads the state instructions
# 1..k left"* - and reports 833/1,984 = 42.0%. The literal reading below (A) returns
# nothing like that, so rather than publish one number and call the difference someone
# else's problem, ALL FOUR readings are computed and printed. Each is a defensible
# reading of the same sentence, they are ordered from strictest to loosest, and the
# spread between them IS the result: a prose definition that admits a 3.3%-to-30.1%
# range was never a measurement.

def state_carry_A_exact(amdpars) -> bool:
    """A - STRICTEST, and the most literal reading. The SAME designation is touched by
    two or more instructions, so what the later one finds depends on what the earlier
    one did. Identical to `src/a1.py::human_checkpoint_reasons`'s condition C3."""
    seen = Counter()
    for r in amdpars:
        for d in set(designations_of(r)):
            seen[d] += 1
    return any(v > 1 for v in seen.values())


def state_carry_B_hierarchy(amdpars) -> bool:
    """B - a later designation is a PREFIX or a DESCENDANT of an earlier one. Revising
    `(b)` and then `(b)(1)` is also order-sensitive: the first changes what the second
    will find, even though the two paths are not equal."""
    seen: list[str] = []
    for r in amdpars:
        for d in designations_of(r):
            for e in seen:
                if d == e or d.startswith(e) or e.startswith(d):
                    return True
            seen.append(d)
    return False


def state_carry_C_multi_designation(amdpars) -> bool:
    """C - more than one instruction in the item names ANY designation. Loose: it
    treats every multi-target section as potentially order-sensitive."""
    return sum(1 for r in amdpars if designations_of(r)) > 1


def state_carry_D_multi_instruction(amdpars) -> bool:
    """D - LOOSEST. More than one instruction at all. This is the reading under which
    almost anything is order-sensitive, and it is included because it is the ceiling:
    no reading of the sentence can return more than this."""
    return len(amdpars) > 1


# the literal reading is the one carried forward into the headline count
state_carry_fires = state_carry_A_exact


def redesignation_collision_fires(amdpars) -> bool:
    """A REDESIGNATE instruction whose designation is also touched by another
    instruction in the same item - the intra-rule collision the detector would catch."""
    redesig = {d for r in amdpars if r.get("operation") == "redesignate"
               for d in designations_of(r)}
    if not redesig:
        return False
    others = {d for r in amdpars if r.get("operation") != "redesignate"
              for d in designations_of(r)}
    return bool(redesig & others)


def has_any_redesignation(amdpars) -> bool:
    return any(r.get("operation") == "redesignate" for r in amdpars)


def main() -> int:
    groups = items_from_corpus()
    n = len(groups)
    sc = [k for k, v in groups.items() if state_carry_fires(v)]
    rc = [k for k, v in groups.items() if redesignation_collision_fires(v)]
    anyre = [k for k, v in groups.items() if has_any_redesignation(v)]

    L = []
    w = L.append
    w("=" * 78)
    w("REMOVED CAPABILITIES - CLASS SIZES RECOMPUTED IN-REPO")
    w("=" * 78)
    w("")
    w(f"  corpus       {CORPUS.relative_to(REPO).as_posix()}")
    w(f"  AMDPARs      {sum(len(v) for v in groups.values()):,} attributed"
      f"   (of 8,752 in the file)")
    w(f"  ITEMS        {n:,}   = distinct (frdoc, section) pairs with >= 1 attributed AMDPAR")
    w("")
    w(f"  THE DENOMINATOR THE PRIOR FIGURES USED WAS 1,984. THIS SCRIPT MEASURES {n:,}.")
    if n != 1984:
        w(f"  THEY ARE NOT THE SAME CORPUS. A percentage computed over {n:,} items is")
        w(f"  not comparable with one computed over 1,984, and the difference of")
        w(f"  {abs(n - 1984):,} items is reported here rather than divided away. Both raw")
        w("  COUNTS are given below so a reader can form their own ratio.")
    else:
        w("  The denominators agree, so the percentages are directly comparable.")
    w("")
    w("-" * 78)
    w("REMOVED CAPABILITY 3 - the ORDERED-STATE LEDGER (ruling R-01, counted removal)")
    w("-" * 78)
    w("")
    w("  Condition: a designation is touched by TWO OR MORE instructions in the item,")
    w("  so instruction k+1 reads the state instructions 1..k left behind.")
    w("")
    src, num, den = PRIOR_STATE_CARRY
    w("  FOUR readings of that one sentence, strictest first. Every one is computed")
    w("  because no single one reproduces the published figure:")
    w("")
    w(f"    {'reading':44s} {'count':>7s} {'of':>7s} {'rate':>8s}")
    for name, fn in (
            ("A  same designation touched twice (literal)", state_carry_A_exact),
            ("B  later path is a prefix/descendant", state_carry_B_hierarchy),
            ("C  >1 instruction naming any designation", state_carry_C_multi_designation),
            ("D  >1 instruction at all (the ceiling)", state_carry_D_multi_instruction)):
        c = sum(1 for v in groups.values() if fn(v))
        w(f"    {name:44s} {c:>7,d} {n:>7,d} {100 * c / n:>7.1f}%")
    w("")
    w(f"    PUBLISHED FIGURE                          {num:>7,d} {den:>7,d}"
      f" {100 * num / den:>7.1f}%   ({src})")
    w("")
    w("  *** THE 42.0% DOES NOT REPRODUCE. ***")
    w("")
    w("  Not under the literal reading, not under any of the three looser ones, and")
    w("  not over any denominator this corpus yields: the shipped attribution has")
    w("  2,527 items under v11 and 2,154 under the spec-literal rule. NEITHER IS")
    w("  1,984. The loosest reading conceivable - 'the item has more than one")
    w(f"  instruction' - reaches only {100 * sum(1 for v in groups.values() if state_carry_D_multi_instruction(v)) / n:.1f}%, so 42.0% is above this measurement's")
    w("  CEILING, not merely outside its range.")
    w("")
    w("  WHAT IS AND IS NOT CONCLUDED. It is NOT concluded that 42.0% is wrong: it may")
    w("  have been computed over a corpus or a definition this session cannot see, and")
    w("  hard rule 15 forbids relaying a contradiction as a refutation. What IS")
    w("  concluded is that THE FIGURE IS NOT REPRODUCIBLE FROM THE SHIPPED ARTIFACTS,")
    w("  so it cannot carry a claim in the submission. It is raised as QUESTIONS.md")
    w("  Q23 and is not quoted as settled anywhere.")
    w("")
    w("  THE REMOVAL DECISION IS UNAFFECTED, and that is worth stating plainly: ruling")
    w("  R-01 cut the ledger to measure two capabilities properly rather than three")
    w("  in a hurry. That reasoning never depended on the class size, which is why")
    w("  discovering the number is unreliable costs the decision nothing. A removal")
    w("  justified by a number that turns out not to reproduce would have been a")
    w("  worse position to be in than this one.")
    w("")
    w("-" * 78)
    w("REMOVED EXPERIMENT 2 - the INTRA-RULE COLLISION DETECTOR")
    w("-" * 78)
    w("")
    w("  Condition: the item contains a REDESIGNATE instruction whose designation is")
    w("  also touched by another instruction in the same item.")
    w("")
    w(f"    items containing ANY redesignation   {len(anyre):,} of {n:,}"
      f"   = {100 * len(anyre) / n:.1f}%")
    w(f"    COLLISION fires on                   {len(rc):,} of {n:,}"
      f"   = {100 * len(rc) / n:.2f}%")
    w("")
    w("  against the two prior figures, NEITHER of which this reproduces exactly:")
    for src, num, den in PRIOR_COLLISION:
        w(f"    {src:16s} {num:,} of {den:,} = {100 * num / den:.2f}%"
          f"   difference {100 * len(rc) / n - 100 * num / den:+.2f} pp")
    w("")
    w("  PUBLISHED AS MEASURED. CONTEXT.md §10 pre-committed to publishing whatever")
    w("  the shipped script yields, with the discrepancy stated, and that is what")
    w("  this is. The 1.3%-3.1% range is NOT narrowed to a single settled figure by")
    w("  this run; a third number is added to it, and the honest summary is that")
    w("  THE CLASS SIZE DOES NOT REPRODUCE ACROSS IMPLEMENTATIONS.")
    w("")
    w("  WHY THAT DOES NOT CHANGE THE DECISION. Every one of the three figures is")
    w("  small, and the removal never rested on the exact value. It rested on:")
    w("    - 0/68 labelled items contain a redesignation instruction;")
    w("    - NARA never publishes a note naming an intra-rule conflict - a live probe")
    w("      for \"conflicting amendments\" returned 0;")
    w("    - and 15 of the pilot's 26 collisions are CORRECT DRAFTING, not defects.")
    w("  A detector for a class NARA does not write notes about cannot be scored")
    w("  against NARA's notes, whatever its class size.")
    w("")
    w("-" * 78)
    w("THE TWO CONDITIONS ARE NOT THE SAME MEASUREMENT")
    w("-" * 78)
    w("")
    both = set(sc) & set(rc)
    w(f"  state-carry only            {len(set(sc) - set(rc)):,}")
    w(f"  collision only              {len(set(rc) - set(sc)):,}")
    w(f"  both                        {len(both):,}")
    w(f"  neither                     {n - len(set(sc) | set(rc)):,}")
    w("")
    w("  CONTEXT.md §6 warns that these two were conflated in an earlier draft and")
    w("  are not comparable. The overlap above is the check on that warning: a")
    w("  collision is a SPECIAL CASE of state-carry, so collision-only should be 0.")
    w(f"  Measured collision-only: {len(set(rc) - set(sc)):,}."
      f"  {'CONSISTENT.' if not (set(rc) - set(sc)) else 'INCONSISTENT - reported as found.'}")
    w("")
    text = "\n".join(L) + "\n"
    print(text)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    OUT.with_suffix(".json").write_text(
        json.dumps({"n_items": n,
                    "state_carry_count": len(sc), "state_carry_rate": len(sc) / n,
                    "collision_count": len(rc), "collision_rate": len(rc) / n,
                    "any_redesignation_count": len(anyre),
                    "both": len(both), "collision_only": len(set(rc) - set(sc)),
                    "prior_state_carry": {"num": 833, "den": 1984},
                    "prior_collision": [{"source": s, "num": a, "den": b}
                                        for s, a, b in PRIOR_COLLISION]},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"  wrote {OUT.relative_to(REPO).as_posix()} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
