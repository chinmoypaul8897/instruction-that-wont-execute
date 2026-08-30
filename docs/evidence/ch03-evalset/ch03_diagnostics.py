"""The two measurements QUESTIONS.md Q15 and Q16 rest on, re-runnable.

Hard rule 14: any claim from data ships its generating script AND its committed
output. Zero-occurrence branches print as zeros.

    python docs/evidence/ch03-evalset/ch03_diagnostics.py
    # committed outputs: case-sensitivity-cost.txt, floor-decomposition.txt

Pure with respect to the network and the clock. Reads only committed artefacts under
`data/attribution-v11/` and `data/amdpars/`.
"""
from __future__ import annotations

import io
import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from attribute_amdpars import _SECTION, split_quotes  # noqa: E402
from attribute_v11 import SIGN_RE, WORD_CS_RE  # noqa: E402

LOWER_RE = re.compile(r"\bsections?\s+(" + _SECTION + r")")
OUT = Path(__file__).resolve().parent

FAR_DOCS = ("2014-08744", "2021-22144")


def load():
    recs = [json.loads(l) for l in
            (REPO / "data/attribution-v11/amdpars_v11.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
    comp = json.loads((REPO / "data/attribution-v11/completeness_v11.json")
                      .read_text(encoding="utf-8"))
    cits = json.loads((REPO / "data/amdpars/citations.json")
                      .read_text(encoding="utf-8"))
    return recs, comp, cits


def case_sensitivity_cost(recs, cits, w):
    p = lambda *a: print(*a, file=w)                              # noqa: E731
    p("=" * 78)
    p("Q15 - WHAT CONTEXT.md v1.1's CASE-SENSITIVE WORD FORM COSTS")
    p("=" * 78)
    p("")
    p("CONTEXT.md section 8 adopts the word form because, under the sign-only reading,")
    p('"ten documents attribute NOTHING - 1,910 elements", naming 2014-08744 (838) and')
    p("2021-22144 (649). Measured below: v1.1 as SPECIFIED puts most of that back.")
    p("")

    docs: dict[str, list] = {}
    for r in recs:
        docs.setdefault(r["frdoc"], []).append(r)
    p(f"  {'detector':<16}{'docs attributing NOTHING':>26}{'elements':>12}")
    zero_by_cfg = {}
    for cfg in ("spec_literal", "extended_ci", "extended_cs", "v11"):
        zero = sorted(d for d, rs in docs.items()
                      if not any(r[f"section_{cfg}"] for r in rs))
        zero_by_cfg[cfg] = zero
        p(f"  {cfg:<16}{len(zero):>26}{sum(len(docs[d]) for d in zero):>12}")
    p("")
    p("  documents attributing NOTHING under v11:")
    for d in zero_by_cfg["v11"]:
        p(f"    {d:<14} {len(docs[d]):>5} elements")
    p("")

    p("  CONTEXT.md section 8 quotes the FAR style as \"Section 52.204-8 is amended\".")
    cap = sum(1 for r in recs if re.search(r"\bSection 52\.204-8", r["text"]))
    low = [r for r in recs if re.search(r"\bsection 52\.204-8", r["text"])]
    p(f"    occurrences with a CAPITAL S in the corpus : {cap}")
    p(f"    occurrences with a lowercase s             : {len(low)}")
    if low:
        p(f"    the actual bytes                           : {low[0]['text'][:80]!r}")
    p("")

    p("  Q12(c)'s 683 lowercase-only namers, DECOMPOSED BY DOCUMENT:")
    by_doc: dict[str, int] = {}
    lower_only = 0
    for r in recs:
        d, _, _ = split_quotes(r["text"])
        if LOWER_RE.search(d) and not SIGN_RE.search(d) and not WORD_CS_RE.search(d):
            lower_only += 1
            by_doc[r["frdoc"]] = by_doc.get(r["frdoc"], 0) + 1
    far = sum(by_doc.get(d, 0) for d in FAR_DOCS)
    p(f"    lowercase-only namers, total          : {lower_only}")
    p(f"    ... in the two FAR rules (CORRECT)    : {far}"
      f"   ({far / lower_only:.1%})" if lower_only else "")
    p(f"    ... elsewhere                         : {lower_only - far}")
    p(f"    ... carrying part_mismatch (Q12(c)'s own harm figure): 44   (6.4%)")
    p("    by document:")
    for d, n in sorted(by_doc.items(), key=lambda x: -x[1]):
        p(f"      {d:<14} {n:>4}")
    p("")

    resolved = [(c["frdoc"], c["section"]) for c in cits.values()
                if c.get("status") == "resolved"]
    zero_v11 = set(zero_by_cfg["v11"])
    hit = sorted(x for x in resolved if x[0] in zero_v11)
    p(f"  pool positives in v11-zero-attribution documents: {len(hit)} of {len(resolved)}")
    for f, s in hit:
        p(f"    {f:<14} {s}")
    p("")


def floor_decomposition(comp, w):
    p = lambda *a: print(*a, file=w)                              # noqa: E731
    p("=" * 78)
    p("Q16 - WHAT THE >= 0.90 PER-DOCUMENT COMPLETENESS FLOOR ACTUALLY SELECTS ON")
    p("=" * 78)
    p("")
    per = comp["per_document"]
    rows = [(f, c["v11"]["completeness"], c["v11"]["attribution_rate"],
             c["v11"]["parse_rate"], c["v11"]["total"]) for f, c in per.items()]
    keep = [r for r in rows if r[1] >= 0.90]
    drop = [r for r in rows if r[1] < 0.90]
    p(f"  documents total                     : {len(rows)}")
    p(f"  pass the >= 0.90 completeness floor : {len(keep)}")
    p(f"  excluded by it                      : {len(drop)}")
    p("")
    for name, rs in (("PASSING", keep), ("EXCLUDED", drop)):
        if not rs:
            p(f"  {name}: none")
            continue
        p(f"  {name:<9} median completeness {statistics.median(r[1] for r in rs):.4f}"
          f"   attribution {statistics.median(r[2] for r in rs):.4f}"
          f"   parse {statistics.median(r[3] for r in rs):.4f}")
    p("")
    p("  Of the EXCLUDED documents:")
    p(f"    bound by the PARSE half (parse_rate < attribution_rate) : "
      f"{sum(1 for r in drop if r[3] < r[2])} / {len(drop)}")
    p(f"    attribution >= 0.90 and yet excluded                    : "
      f"{sum(1 for r in drop if r[2] >= 0.90)}")
    p(f"    attribution >= 0.80 and yet excluded                    : "
      f"{sum(1 for r in drop if r[2] >= 0.80)}")
    p(f"    parse_rate < 0.90                                       : "
      f"{sum(1 for r in drop if r[3] < 0.90)} / {len(drop)}")
    p(f"    attribution == 1.0000 and yet excluded                  : "
      f"{sum(1 for r in drop if r[2] == 1.0)}")
    p("")
    p("  Excluded documents with PERFECT attribution:")
    for r in sorted((r for r in drop if r[2] == 1.0), key=lambda r: r[1]):
        p(f"    {r[0]:<14} completeness {r[1]:.4f}  attribution {r[2]:.4f}"
          f"  parse {r[3]:.4f}  elements {r[4]}")
    p("")
    p("  Q11's ruling, verbatim: \"only 46 of 2,913 unparsed elements (1.6%) are our")
    p("  defect. Parse shape is a property of Federal Register drafting, not of our")
    p("  attributor, and does not belong in an attributor's gate.\"")
    p("")
    p("  A floor on COMPLETENESS therefore selects mostly on FR drafting style.")
    p("  This is a measurement, not a proposal: no metric was changed, no threshold")
    p("  moved, and the >= 0.90 set is BUILT AND COMMITTED at data/evalset-restricted/.")
    p("")


def main() -> int:
    recs, comp, cits = load()
    for name, fn, arg in (("case-sensitivity-cost.txt", case_sensitivity_cost,
                           (recs, cits)),
                          ("floor-decomposition.txt", floor_decomposition, (comp,))):
        buf = io.StringIO()
        fn(*arg, buf)
        text = buf.getvalue()
        io.open(OUT / name, "w", encoding="utf-8", newline="\n").write(text)
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
