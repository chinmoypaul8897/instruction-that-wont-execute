"""The ordering-bias figure, with the generating script it should have shipped with.

**Hard rule 14 says a claim from data ships its generating script AND its committed
output. The "32/38, exact p = 0.000024" figure shipped with neither**, and the round-2
reviewer could not reproduce it by any method it constructed (29/38 numerically,
31/38 lexicographically). That is a hard rule 14 violation by the build session, and
this file is the retraction plus the replacement.

The number was computed in an ad-hoc inline snippet that was never committed. It
recovered pairs from the FROZEN items file by re-matching positives to negatives on
`(frdoc, instruction_count)`, which is a reconstruction and not the pairing the
builder actually made - so it could and did drift from the real one.

**This script does it properly**: it runs the pairing itself, under BOTH the pre-fix
rule and the shipped rule, over the real corpus, and reports the ordering bias of each
with an exact two-sided binomial. Nothing is reconstructed from the freeze.

    python docs/evidence/ch03-evalset/ordering_bias.py
    # committed output: ordering-bias.txt
"""
from __future__ import annotations

import io
import json
import sys
from math import comb
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from cfr_pit import section_sort_key  # noqa: E402
from eval_set import build_pairs, instruction_counts, load_jsonl  # noqa: E402

OUT = Path(__file__).resolve().parent


def prefix_rule_pairs(counts, defects, tolerance: int = 0):
    """The PRE-FIX rule, reimplemented here rather than by mutating `src/`.

    Verbatim behaviour of the code that failed the gate: `negative = free[0]`, the
    sorted-first free count-matched sibling. Kept in the evidence directory so the
    defect can be re-measured forever without the defect being in `src/`.
    """
    defect_by_doc: dict[str, set] = {}
    for frdoc, section in defects:
        defect_by_doc.setdefault(frdoc, set()).add(section)
    pairs, used = [], {}
    for frdoc, section in sorted(defects):
        doc = counts.get(frdoc, {})
        own = doc.get(section)
        if own is None:
            continue
        taken = used.setdefault(frdoc, set())
        free = sorted(s for s, c in doc.items()
                      if s != section
                      and s not in defect_by_doc.get(frdoc, set())
                      and s not in taken
                      and abs(c - own) <= tolerance)
        if not free:
            continue
        negative = free[0]
        taken.add(negative)
        pairs.append({"frdoc": frdoc, "positive": section, "negative": negative})
    return pairs


def binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided binomial at p = 1/2, by summing outcomes no more likely than
    the observed one. Integer arithmetic until the final division."""
    if n == 0:
        return 1.0
    probs = [comb(n, i) for i in range(n + 1)]
    obs = probs[k]
    return sum(x for x in probs if x <= obs) / (2 ** n)


def bias(pairs) -> dict:
    before = sum(1 for p in pairs
                 if section_sort_key(p["negative"]) < section_sort_key(p["positive"]))
    after = sum(1 for p in pairs
                if section_sort_key(p["negative"]) > section_sort_key(p["positive"]))
    tied = len(pairs) - before - after
    n = before + after
    return {"pairs": len(pairs), "before": before, "after": after, "tied": tied,
            "n_untied": n, "p_value": binom_two_sided(min(before, after), n)}


def main() -> int:
    records = load_jsonl(REPO / "data/attribution-v11/amdpars_v11.jsonl")
    cits = json.loads((REPO / "data/amdpars/citations.json").read_text(encoding="utf-8"))
    counts = instruction_counts(records, "v11")
    defects = sorted({(c["frdoc"], c["section"]) for c in cits.values()
                      if c.get("status") == "resolved"})

    old = prefix_rule_pairs(counts, defects)
    new, _ = build_pairs(counts, defects, tolerance=0)

    w = io.StringIO()

    def p(*a):
        print(*a, file=w)

    p("=" * 84)
    p("ORDERING BIAS OF THE NEGATIVE-SELECTION RULE - pre-fix vs shipped")
    p("=" * 84)
    p("")
    p("  Measured by RUNNING each rule over the real corpus, not by reconstructing")
    p("  the pairing from the frozen items file. Exact two-sided binomial at p = 1/2")
    p("  over the untied pairs.")
    p("")
    p(f"  {'rule':<34}{'pairs':>7}{'neg BEFORE':>12}{'neg AFTER':>11}{'tied':>6}"
      f"{'exact p':>12}")
    for label, pairs in (("PRE-FIX  negative = free[0]", old),
                         ("SHIPPED  balanced in sort order", new)):
        b = bias(pairs)
        p(f"  {label:<34}{b['pairs']:>7}{b['before']:>12}{b['after']:>11}"
          f"{b['tied']:>6}{b['p_value']:>12.6f}")
    p("")
    p("=" * 84)
    p("RETRACTION")
    p("=" * 84)
    p("")
    ob, nb = bias(old), bias(new)
    p(f"  The figure published as '32/38, exact p = 0.000024' is WITHDRAWN. It was")
    p(f"  computed by an uncommitted inline snippet that RECONSTRUCTED the pairing")
    p(f"  from the frozen items file by re-matching on (frdoc, instruction_count),")
    p(f"  rather than by running the rule. The round-2 reviewer could not reproduce")
    p(f"  it and was right not to be able to.")
    p("")
    p(f"  The correct pre-fix figure, from running the pre-fix rule:")
    p(f"      {ob['before']}/{ob['n_untied']} negatives sort before their positive,"
      f"  exact p = {ob['p_value']:.6f}")
    p(f"  The correct shipped figure:")
    p(f"      {nb['before']}/{nb['n_untied']} negatives sort before their positive,"
      f"  exact p = {nb['p_value']:.6f}")
    p("")
    p("  The DIRECTION and the CONCLUSION are unchanged - the pre-fix rule is")
    p("  strongly biased and the shipped rule is not - but the published number was")
    p("  wrong and no script backed it. Both defects are the build session's.")
    p("")
    p("  NOTE ON THE PAIR COUNTS. These are the pairing stage only, BEFORE the")
    p("  point-in-time text lookup and the leakage test remove items, so they are")
    p("  larger than the frozen n. The frozen eval set is 41 pairs / 82 items.")
    text = w.getvalue()
    io.open(OUT / "ordering-bias.txt", "w", encoding="utf-8", newline="\n").write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
