"""CH-03 · 1d/1e — build the eval set, strip it, prove it, freeze it.

    positives  (rule, section) pairs carrying a live codification-defect note
    negatives  a sibling section amended by the SAME FR document, with EXACTLY the
               same instruction count, carrying NO defect note

**Exact count matching is the whole point.** `CONTEXT.md` §8: *"Non-negotiable —
unmatched, a hardcoded threshold on instruction count beats the agent, and that is
precisely how an earlier candidate died."* Tolerance is 0 here and it is never
relaxed; a ±1 figure is computed as a **diagnostic** and is never the eval set.

THE EXCLUSION LADDER is published with a count at every rung, and every rung records
its **positive/negative split** — because an exclusion that removes mostly positives
biases the eval set even when its total looks small, and a ladder that prints only
totals hides exactly that.

Every arm sees text that has been through `cfr_pit.strip_leakage`, and the freeze
refuses to write if `assert_stripper_on_known_positive()` does not pass first.
A strip counter that prints zero because it is looking for the wrong element name is
`QUESTIONS.md` Q8's trap, and the assertion is what stops the zero being believed.

DETERMINISM - hard rule 9: sorted iteration everywhere, sorted-key JSON, LF endings,
no clock, no randomness.

THE NEGATIVE-SELECTION RULE, and why it is NOT the one the pre-registration declared.
The pre-registration said *"sorted order, first element - deterministic, declared, and
independent of any label."* **The adversarial review falsified that** (finding F1,
`docs/reviews/REVIEW_CH-03.md`): the positive is a GIVEN section and the negative is
CHOSEN, so taking the sorted-first candidate put negatives systematically earlier in
section order, and a label-blind script reading only `frdoc` and `section` scored
**0.8158** on the primary metric. The rule was independent of the label and
**correlated with it through the selection asymmetry**.

`build_pairs` now BALANCES sort order. Recorded as ERRATA E-1 in the pre-registration;
its original text is untouched. Round 2 measured the residual: every structural attack
is dead (numeric sort 0.5244, lexicographic 0.5366, part number 0.5610,
position-in-document <= 0.5976, and an attack on the selection rule itself 0.5122).

    python -m eval_set build --out data/evalset
    python -m eval_set verify --out data/evalset
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from attribute_amdpars import sha256_file, write_json, write_jsonl  # noqa: E402
import cfr_pit  # noqa: E402
from cfr_pit import (  # noqa: E402
    PitError,
    section_sort_key,
    assert_stripper_on_known_positive,
    candidate_volumes,
    edition_year,
    fetch_volume,
    find_section,
    leakage_violations,
    section_text,
    strip_leakage,
    volume_index,
)

DEFAULT_V11 = Path("data/attribution-v11")
DEFAULT_AMDPARS = Path("data/amdpars")
DEFAULT_EDNOTES = Path("data/ednotes")
DEFAULT_RAW_CFR = Path("data/raw/cfr")
DEFAULT_OUT = Path("data/evalset")

# Ruling Q11 / plan.md CH-02's fallback. `QUESTIONS.md` Q16 records why the two
# disagree about whether this floor applies at all in the `< 0.80` branch, what each
# reading costs, and which was taken. BOTH sets are built and committed, so the choice
# is one flag rather than a rebuild:
#     --floor 0.0   -> data/evalset/            the frozen PRIMARY  (Q16 reading (ii))
#     --floor 0.90  -> data/evalset-restricted/ the floor applied   (Q16 reading (i))
# The 0.90 figure is reported as a diagnostic on EVERY build regardless of the floor
# actually applied, so the ladder always shows what it would have cost.
PER_DOCUMENT_COMPLETENESS_FLOOR = 0.90
DEFAULT_FLOOR = 0.0

NORMALISATION = "whitespace-collapsed"          # hard rule 7: declared, never silent


class EvalSetError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips."""


def abs_rank(a, b) -> tuple:
    """A total, order-only distance between two section sort keys.

    Section keys are nested tuples, so they cannot be subtracted. This compares them
    componentwise and returns a key that increases with distance, which is all the
    "nearest candidate within a side" tie-break needs. Pure and deterministic.
    """
    for x, y in zip(a[1], b[1]):
        if x != y:
            return (abs(a[0] - b[0]), abs(x[1] - y[1]) if x[0] == y[0] == 0 else 1)
    return (abs(a[0] - b[0]), abs(len(a[1]) - len(b[1])))


# ============================================================ pure: the pairing

def instruction_counts(records, config: str = "v11") -> dict[str, dict[str, int]]:
    """{frdoc -> {section -> number of AMDPAR elements attributed to it}}. Pure."""
    key = f"section_{config}"
    out: dict[str, dict[str, int]] = {}
    for r in records:
        sec = r.get(key)
        if sec:
            out.setdefault(r["frdoc"], {})[sec] = \
                out.setdefault(r["frdoc"], {}).get(sec, 0) + 1
    return out


def build_pairs(counts, defects, tolerance: int = 0):
    """Match each positive to one free count-matched sibling. Pure. Goldens G-D.

    `counts`   {frdoc -> {section -> instruction count}}
    `defects`  iterable of (frdoc, section) — every defect section in the corpus,
               including ones excluded upstream, because a defect sibling must never
               be offered as a NEGATIVE even when it is not itself a positive.

    Positives are processed in sorted `(frdoc, section)` order and **each negative is
    consumed on first use** (G-D): reusing one would put the same section in the eval
    set twice and inflate n with a duplicate. Returns (pairs, unmatched).
    """
    if tolerance < 0:
        raise EvalSetError("tolerance must be >= 0")
    defect_by_doc: dict[str, set] = {}
    for frdoc, section in defects:
        defect_by_doc.setdefault(frdoc, set()).add(section)

    pairs, unmatched = [], []
    used: dict[str, set] = {}
    # REVIEW FINDING F1 - the defect that failed CH-03's gate, and the fix.
    #
    # The rule WAS `negative = free[0]`, the sorted-first count-matched sibling, while
    # the positive is a GIVEN section. Negatives therefore sat systematically earlier
    # in section order, and a six-line label-blind script reading only `frdoc` and
    # `section` scored 0.8158 on the primary metric - beating B0-agent by 17 pp and
    # clearing GOOD.md's A1 bar, with no model, no CFR text and no instruction text.
    # Negatives sorted before their positives 36 of 50 times, exact p = 0.0026
    # (docs/evidence/ch03-evalset/ordering_bias.py; an earlier '32/38, p=0.000024'
    # was published without a generating script and is RETRACTED).
    #
    # `balance` is the running (#negatives that sorted BEFORE) - (#that sorted AFTER).
    # When candidates exist on both sides of the positive, the side that reduces the
    # imbalance is taken; within a side the candidate NEAREST the positive is taken,
    # which is deterministic and needs no RNG. When only one side has candidates the
    # choice is structural and is taken as-is, and the counter still records it, so
    # the next free choice compensates.
    #
    # It is label-blind: `balance` is updated from section ORDER only and never sees a
    # verdict. It is deterministic and byte-reproducible (hard rule 9). The residual
    # is MEASURED rather than asserted - see docs/evidence/ch03-evalset/.
    balance = 0
    for frdoc, section in sorted(defects):
        doc = counts.get(frdoc, {})
        own = doc.get(section)
        if own is None:
            unmatched.append({"frdoc": frdoc, "section": section,
                              "instruction_count": None,
                              "reason": "positive-has-no-attributed-instructions"})
            continue
        taken = used.setdefault(frdoc, set())
        free = sorted(s for s, c in doc.items()
                      if s != section
                      and s not in defect_by_doc.get(frdoc, set())
                      and s not in taken
                      and abs(c - own) <= tolerance)
        any_match = sorted(s for s, c in doc.items()
                           if s != section
                           and s not in defect_by_doc.get(frdoc, set())
                           and abs(c - own) <= tolerance)
        if not free:
            unmatched.append({
                "frdoc": frdoc, "section": section, "instruction_count": own,
                "reason": ("no-free-count-matched-sibling" if any_match
                           else "no-count-matched-sibling"),
                "count_matched_but_taken": len(any_match)})
            continue
        key = section_sort_key(section)
        lower = [s for s in free if section_sort_key(s) < key]
        higher = [s for s in free if section_sort_key(s) > key]
        if lower and higher:
            # both sides available - take the side that pulls `balance` toward 0
            side = higher if balance >= 0 else lower
            forced = False
        else:
            # Only one side has candidates: the choice is structural, not selectional,
            # and is taken as-is. `free` is the final fallback for candidates whose
            # sort key TIES with the positive's - degenerate section forms, and the
            # synthetic sections in golden G-D. It must never be empty here: `free`
            # was already checked non-empty above.
            side = lower or higher or free
            forced = True
        # nearest to the positive within the chosen side; deterministic, no RNG
        negative = min(side, key=lambda s: (abs_rank(section_sort_key(s), key), s))
        balance += 1 if section_sort_key(negative) < key else -1
        taken.add(negative)
        pairs.append({"frdoc": frdoc, "positive": section, "negative": negative,
                      "instruction_count": own,
                      "count_matched_candidates": len(any_match),
                      "free_candidates": len(free),
                      "candidates_lower": len(lower),
                      "candidates_higher": len(higher),
                      "side_forced": forced,
                      "negative_sorts_before_positive":
                          section_sort_key(negative) < key})
    if len(pairs) + len(unmatched) != len(list(defects)):
        raise EvalSetError("pairs + unmatched != defects; the ladder does not close")
    return pairs, unmatched


class Ladder:
    """The exclusion ladder. Every rung carries a count AND a positive/negative split.

    Hard rule 14: zero-occurrence branches print as zeros; nothing is omitted because
    it did not fire.
    """

    def __init__(self, rungs: list[str]):
        self.order = list(rungs)
        self.rows = {r: {"items": 0, "positives": 0, "negatives": 0, "detail": []}
                     for r in rungs}

    def drop(self, rung: str, positives: int = 0, negatives: int = 0, detail=None):
        if rung not in self.rows:
            raise EvalSetError(f"undeclared ladder rung {rung!r}")
        row = self.rows[rung]
        row["items"] += positives + negatives
        row["positives"] += positives
        row["negatives"] += negatives
        if detail is not None:
            row["detail"].append(detail)

    def as_dict(self):
        return {"order": self.order,
                "rungs": {r: {k: v for k, v in self.rows[r].items()} for r in self.order}}


# ============================================================ I/O

def load_jsonl(path: Path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def _volume_root_cache(cache: dict, path: Path):
    if path not in cache:
        cache[path] = ET.parse(str(path)).getroot()
    return cache[path]


def resolve_text(title, part, section, year, raw_dir, index_cache, root_cache,
                 offline=False):
    """Find one section in its annual edition. Returns a dict, never raises for a
    plain miss — a miss is a ladder rung, not a crash.

    The declared G-G2 fallback is here: tier-1 volumes (part AND section range match)
    are searched first, then every other volume covering the part. `route` records
    which tier found it, so a range-parsing error shows up as a tier-2 hit rather
    than as a silent exclusion.
    """
    key = (int(title), int(year))
    if key not in index_cache:
        if offline:
            cached = raw_dir / f"index-title{title}-{year}.json"
            if not cached.exists():
                return {"found": False, "reason": "no-cached-volume-index"}
        try:
            index_cache[key] = volume_index(int(title), int(year), raw_dir)
        except Exception as exc:
            return {"found": False, "reason": f"volume-index-failed: {exc!r}"[:200]}
    index = index_cache[key]
    cands = candidate_volumes(index, str(part), section)
    if not cands:
        return {"found": False, "reason": "no-volume-covers-this-part",
                "volumes_in_edition": len(index)}

    for tier, vol in enumerate(cands):
        try:
            path = fetch_volume(vol, raw_dir)
        except Exception as exc:
            return {"found": False, "reason": f"volume-fetch-failed: {exc!r}"[:200]}
        root = _volume_root_cache(root_cache, path)
        sec, n = find_section(root, section)
        if sec is None:
            continue
        raw_text = section_text(sec)
        stripped_el, counts = strip_leakage(sec)
        text = section_text(stripped_el)
        return {
            "found": True,
            "volume": vol["name"],
            "volume_url": vol["url"],
            "volume_revised": vol["revised"],
            "volume_parts_header": vol["range"]["raw"],
            "route": "range-match" if tier == 0 else "same-part-fallback",
            "eligible_candidates": n,
            "strip_counts": counts,
            "chars_unstripped": len(raw_text),
            "chars_stripped": len(text),
            "text": text,
            "text_unstripped": raw_text,
        }
    return {"found": False, "reason": "section-not-in-as-of-edition",
            "volumes_searched": len(cands)}


# ============================================================ build

RUNGS = [
    "pool-citations-resolved",
    "document-completeness-below-floor",
    "positive-has-no-attributed-instructions",
    "no-count-matched-sibling",
    "no-free-count-matched-sibling",
    "no-title-for-section",
    "as-of-edition-unavailable",
    "section-not-in-as-of-edition",
    "leakage-test-failed-after-strip",
    "kept",
]


def cmd_build(args) -> int:
    v11_dir, out = Path(args.v11), Path(args.out)
    amdpars_dir, raw_dir = Path(args.amdpars), Path(args.raw)

    # ---- 0. the stripper must prove itself BEFORE anything is frozen -------------
    print("=" * 78)
    print("STRIPPER KNOWN-POSITIVE ASSERTION (QUESTIONS.md Q8 - a zero is not believed)")
    print("=" * 78)
    proof = assert_stripper_on_known_positive()
    print(f"  counts on the known positive : {proof['counts']}")
    print(f"  leakage test BEFORE stripping: {len(proof['violations_before'])} violation(s)"
          f"  <- must be non-zero, and is")
    for v in proof["violations_before"]:
        print(f"      rule {v['rule']}  {v['kind']:<16} {v['detail']}")
    print(f"  leakage test AFTER stripping : {len(proof['violations_after'])} violation(s)")
    print(f"  chars {proof['chars_before']} -> {proof['chars_after']}")
    print()

    # ---- 1. inputs ---------------------------------------------------------------
    records = load_jsonl(v11_dir / "amdpars_v11.jsonl")
    comp = json.loads((v11_dir / "completeness_v11.json").read_text(encoding="utf-8"))
    citations = json.loads((amdpars_dir / "citations.json").read_text(encoding="utf-8"))
    notes = {(r["title"], r["section"], r["node"]): r
             for r in load_jsonl(Path(args.ednotes) / "defect_notes.jsonl")}

    counts = instruction_counts(records, "v11")
    per_doc = comp["per_document"]

    # every defect (frdoc, section) in the corpus - used to keep defect siblings out
    # of the NEGATIVE pool even when they are themselves excluded upstream
    all_defects = sorted({(c["frdoc"], c["section"]) for c in citations.values()
                          if c.get("status") == "resolved"})

    ladder = Ladder(RUNGS)
    ladder.drop("pool-citations-resolved", positives=len(all_defects))
    # `pool-citations-resolved` is the ladder's TOP, not a drop; it is recorded as the
    # starting count and subtracted from below.
    ladder.rows["pool-citations-resolved"]["items"] = len(all_defects)

    # ---- 2. the per-document completeness floor (Q11 ruling) ---------------------
    floor = float(args.floor)
    doc_ok, doc_bad = {}, {}
    for frdoc, cfgs in per_doc.items():
        c = cfgs["v11"]["completeness"]
        (doc_ok if c >= floor else doc_bad)[frdoc] = c

    # The 0.90 diagnostic is computed on EVERY build, whatever floor is applied, so
    # the ladder never hides what the other reading would have cost (Q16).
    ref_ok = {f for f, cfgs in per_doc.items()
              if cfgs["v11"]["completeness"] >= PER_DOCUMENT_COMPLETENESS_FLOOR}

    defects_restricted = [(f, s) for f, s in all_defects if f in doc_ok]
    dropped_floor = [(f, s) for f, s in all_defects if f not in doc_ok]
    ladder.drop("document-completeness-below-floor", positives=len(dropped_floor),
                detail={"floor_applied": floor,
                        "documents_excluded": len(doc_bad),
                        "documents_kept": len(doc_ok),
                        "reference_floor_0_90_would_keep_documents": len(ref_ok),
                        "reference_floor_0_90_would_keep_positives":
                            sum(1 for f, _ in all_defects if f in ref_ok)})

    # ---- 3. pairing, exact and diagnostic ---------------------------------------
    pairs, unmatched = build_pairs(counts, defects_restricted, tolerance=0)
    pairs_t1, _ = build_pairs(counts, defects_restricted, tolerance=1)
    pairs_unrestricted, _ = build_pairs(counts, all_defects, tolerance=0)
    pairs_ref_floor, _ = build_pairs(
        counts, [(f, s) for f, s in all_defects if f in ref_ok], tolerance=0)

    for u in unmatched:
        ladder.drop(u["reason"], positives=1, detail=u)

    # ---- 4. resolve the point-in-time text --------------------------------------
    index_cache, root_cache = {}, {}
    items, strip_totals = [], {t: 0 for t in cfr_pit.LEAKAGE_ELEMENTS}
    strip_totals["total"] = 0
    leak_failures = []
    would_have_leaked = 0

    # title/part per (frdoc, section), read from the AMDPARs attributed to it
    where: dict[tuple, dict] = {}
    for r in records:
        sec = r.get("section_v11")
        if not sec:
            continue
        k = (r["frdoc"], sec)
        if k not in where:
            where[k] = {"title": r.get("regtext_title"), "part": r.get("regtext_part")}

    note_by_doc_section = {}
    for c in citations.values():
        if c.get("status") == "resolved":
            note_by_doc_section[(c["frdoc"], c["section"])] = c

    for pair in pairs:
        frdoc = pair["frdoc"]
        cit = note_by_doc_section[(frdoc, pair["positive"])]
        pub_date = cit["date"]
        note = notes.get((cit["title"], cit["section"], cit["node"]))
        members = []
        fatal = None
        for role, section in (("positive", pair["positive"]),
                              ("negative", pair["negative"])):
            w = where.get((frdoc, section), {})
            title = w.get("title") or (cit["title"] if role == "positive" else None)
            part = w.get("part") or (section.split(".")[0])
            if not title:
                fatal = ("no-title-for-section", role)
                break
            try:
                year = edition_year(int(title), pub_date)
            except (PitError, ValueError) as exc:
                fatal = ("as-of-edition-unavailable", f"{role}: {exc}")
                break
            res = resolve_text(title, part, section, year, raw_dir,
                               index_cache, root_cache)
            if not res["found"]:
                fatal = ("section-not-in-as-of-edition", f"{role}: {res['reason']}")
                break
            members.append((role, section, title, part, year, res))
        if fatal:
            ladder.drop(fatal[0], positives=1, negatives=1,
                        detail={"frdoc": frdoc, "positive": pair["positive"],
                                "negative": pair["negative"], "why": fatal[1]})
            continue

        # ---- the leakage test, on the STRIPPED text, per member ------------------
        own_citation = cit["citation"]
        bad = []
        for role, section, title, part, year, res in members:
            v = leakage_violations(res["text"], own_citation)
            if v:
                bad.append({"role": role, "section": section, "violations": v})
        if bad:
            leak_failures.append({"frdoc": frdoc, "detail": bad})
            ladder.drop("leakage-test-failed-after-strip", positives=1, negatives=1,
                        detail={"frdoc": frdoc, "bad": bad})
            continue

        for role, section, title, part, year, res in members:
            for t in cfr_pit.LEAKAGE_ELEMENTS:
                strip_totals[t] += res["strip_counts"][t]
            strip_totals["total"] += res["strip_counts"]["total"]
            # ROUND-2 REVIEW FINDING R2. This counter used to sit in the loop ABOVE,
            # which runs before the leaking pairs are dropped - so the numerator
            # covered 86 items while it was published against a denominator of 82,
            # and printed 5 where the frozen corpus has 3. It is now incremented only
            # for items that are actually KEPT, so numerator and denominator describe
            # the same set. A ratio whose halves count different things is not a rate.
            if leakage_violations(res["text_unstripped"], own_citation):
                would_have_leaked += 1
            items.append({
                "item_id": f"{frdoc}|{section}",
                "frdoc": frdoc,
                "section": section,
                "role": role,
                "label": "WILL_FAIL" if role == "positive" else "WILL_EXECUTE",
                "cfr_title": str(title),
                "cfr_part": str(part),
                "fr_citation": own_citation,
                "publication_date": pub_date,
                "as_of_edition": year,
                "as_of_revision_date": cfr_pit.revision_date(int(title), year).isoformat(),
                "instruction_count": pair["instruction_count"],
                # Q16's mitigation: a MEASUREMENT, not a metric change. The scorer can
                # stratify accuracy by these without any threshold being introduced.
                "document_completeness_v11": per_doc[frdoc]["v11"]["completeness"],
                "document_attribution_rate_v11": per_doc[frdoc]["v11"]["attribution_rate"],
                "document_parse_rate_v11": per_doc[frdoc]["v11"]["parse_rate"],
                "document_amdpar_count": per_doc[frdoc]["v11"]["total"],
                "instructions": [
                    {"ordinal": r["ordinal"], "operation": r["operation"],
                     "anchor": r["anchor"], "designation": r["designation"],
                     "text": r["text"]}
                    for r in records
                    if r["frdoc"] == frdoc and r.get("section_v11") == section],
                "note_text": (note or {}).get("text") if role == "positive" else None,
                "note_node": (note or {}).get("node") if role == "positive" else None,
                "volume": res["volume"],
                "volume_url": res["volume_url"],
                "volume_revised": res["volume_revised"],
                "volume_parts_header": res["volume_parts_header"],
                "volume_route": res["route"],
                "strip_counts": res["strip_counts"],
                "chars_unstripped": res["chars_unstripped"],
                "chars_stripped": res["chars_stripped"],
                "normalisation": NORMALISATION,
                "section_text": res["text"],
            })
        ladder.drop("kept", positives=1, negatives=1)

    # ---- 5. close the ladder -----------------------------------------------------
    dropped = sum(ladder.rows[r]["positives"] for r in RUNGS
                  if r not in ("pool-citations-resolved", "kept"))
    kept_pos = ladder.rows["kept"]["positives"]
    if dropped + kept_pos != len(all_defects):
        raise EvalSetError(
            f"exclusion ladder does not close: dropped {dropped} + kept {kept_pos} "
            f"!= {len(all_defects)} resolved pool citations")

    n_pairs = kept_pos
    n_items = len(items)
    if n_items != 2 * n_pairs:
        raise EvalSetError(f"n items {n_items} != 2 x pairs {n_pairs}")
    successes = sum(1 for i in items if i["label"] in ("WILL_FAIL", "WILL_EXECUTE"))
    if successes + (n_items - successes) != n_items:
        raise EvalSetError("success + failure != n")

    # ---- 6. freeze ---------------------------------------------------------------
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "items.jsonl", sorted(items, key=lambda i: (i["item_id"], i["role"])))
    write_json(out / "exclusion_ladder.json", {
        "ladder": ladder.as_dict(),
        "n_pairs": n_pairs,
        "n_items": n_items,
        "target_pairs": 42,
        "per_document_completeness_floor": PER_DOCUMENT_COMPLETENESS_FLOOR,
        "documents_kept": len(doc_ok),
        "documents_excluded_by_floor": len(doc_bad),
        "floor_applied": floor,
        "diagnostics_never_used_as_the_eval_set": {
            "pairs_at_tolerance_1": len(pairs_t1),
            "pairs_without_any_completeness_floor": len(pairs_unrestricted),
            "pairs_under_the_0_90_reference_floor": len(pairs_ref_floor),
        },
    })
    write_json(out / "leakage.json", {
        "known_positive_assertion": {
            "counts": proof["counts"],
            "violations_before_stripping": proof["violations_before"],
            "violations_after_stripping": proof["violations_after"],
        },
        "strip_counts_over_the_frozen_corpus": strip_totals,
        "items_whose_UNSTRIPPED_text_would_have_leaked": would_have_leaked,
        "items_total": n_items,
        "leakage_test_failures_after_strip": leak_failures,
    })

    manifest = {"chunk": "CH-03", "what": "point-in-time CFR text and the eval set",
                "normalisation": NORMALISATION, "files": {}, "raw_inputs": {}}
    for name in sorted(p.name for p in out.iterdir() if p.name != "manifest.json"):
        p = out / name
        manifest["files"][name] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    for vol in sorted({i["volume"] for i in items}):
        p = raw_dir / vol
        if p.exists():
            manifest["raw_inputs"][vol] = {"sha256": sha256_file(p),
                                           "bytes": p.stat().st_size}
    write_json(out / "manifest.json", manifest)

    # ---- 7. report ---------------------------------------------------------------
    print("=" * 78)
    print("EXCLUSION LADDER - every rung, with its positive/negative split")
    print("=" * 78)
    for r in RUNGS:
        row = ladder.rows[r]
        print(f"  {r:<42}{row['items']:>6}   (+{row['positives']} / -{row['negatives']})")
    print()
    print(f"  PAIRS = {n_pairs}   n = {n_items}   target >= 42 pairs (n >= 84)")
    print(f"  per-document completeness floor APPLIED: {floor}")
    print(f"  documents kept {len(doc_ok)} / excluded by that floor {len(doc_bad)}")
    print()
    print("  DIAGNOSTICS - computed, published, and NEVER used as the eval set:")
    print(f"    pairs at tolerance +/-1                    {len(pairs_t1)}")
    print(f"    pairs with NO completeness floor           {len(pairs_unrestricted)}")
    print(f"    pairs under the 0.90 reference floor       {len(pairs_ref_floor)}"
          f"   <- QUESTIONS.md Q16")
    print()
    print("=" * 78)
    print("LEAKAGE STRIPS over the frozen corpus")
    print("=" * 78)
    for t in cfr_pit.LEAKAGE_ELEMENTS:
        print(f"  {t:<10} {strip_totals[t]:>6}")
    print(f"  {'TOTAL':<10} {strip_totals['total']:>6}")
    print(f"  items whose UNSTRIPPED text would have contained the answer: "
          f"{would_have_leaked} / {n_items}")
    print(f"  leakage-test failures after stripping: {len(leak_failures)}")
    print()
    print(f"  frozen: {out}   items.jsonl bytes="
          f"{(out / 'items.jsonl').stat().st_size:,}")
    return 0


def cmd_verify(args) -> int:
    out = Path(args.out)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    ok, bad = 0, []
    for name, want in sorted(manifest["files"].items()):
        p = out / name
        if not p.exists():
            bad.append(f"MISSING  {name}")
            continue
        got = sha256_file(p)
        if got == want["sha256"]:
            ok += 1
            print(f"  OK    {name:<24} {got}")
        else:
            bad.append(f"MISMATCH {name}\n    manifest {want['sha256']}\n"
                       f"    on disk  {got}")
            print(f"  FAIL  {name:<24} {got}")
    print(f"  {ok}/{len(manifest['files'])} verify")
    for b in bad:
        print(f"  - {b}")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build, strip, prove and freeze the eval set")
    b.add_argument("--v11", default=str(DEFAULT_V11))
    b.add_argument("--amdpars", default=str(DEFAULT_AMDPARS))
    b.add_argument("--ednotes", default=str(DEFAULT_EDNOTES))
    b.add_argument("--raw", default=str(DEFAULT_RAW_CFR))
    b.add_argument("--out", default=str(DEFAULT_OUT))
    b.add_argument("--floor", default=DEFAULT_FLOOR, type=float,
                   help="per-document v11 completeness floor; see QUESTIONS.md Q16")
    b.set_defaults(func=cmd_build)
    v = sub.add_parser("verify", help="check the freeze against its manifest; no network")
    v.add_argument("--out", default=str(DEFAULT_OUT))
    v.set_defaults(func=cmd_verify)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
