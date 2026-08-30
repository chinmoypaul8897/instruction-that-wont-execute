"""CH-03 1d/1e - the eval set, its ladder, and the properties the corpus must hold.

Goldens G-D come from `docs/evidence/ch03-evalset/goldens.md`, committed at c685e80
before `src/eval_set.py` existed.

The tests over the FROZEN corpus are the ones a reviewer should read first: they
assert on `data/evalset/items.jsonl` as shipped, so they fail if the freeze is ever
rebuilt into something weaker.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cfr_pit import LEAKAGE_LITERALS, leakage_violations  # noqa: E402
from eval_set import EvalSetError, build_pairs, instruction_counts  # noqa: E402

ITEMS = REPO / "data/evalset/items.jsonl"
LADDER = REPO / "data/evalset/exclusion_ladder.json"
LEAKAGE = REPO / "data/evalset/leakage.json"
needs_freeze = pytest.mark.skipif(
    not ITEMS.exists(), reason="run `python src/eval_set.py build` first")


def load_items():
    return [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines()
            if l.strip()]


# ------------------------------------------------------------------ golden G-D
GD_COUNTS = {"D1": {"A": 3, "B": 3, "C": 2, "D": 3}, "D2": {"E": 5, "F": 4}}
GD_DEFECTS = [("D1", "A"), ("D1", "D"), ("D2", "E")]


def test_GD_pairing_and_the_negative_reuse_collision():
    pairs, unmatched = build_pairs(GD_COUNTS, GD_DEFECTS, tolerance=0)
    assert len(pairs) == 1
    assert pairs[0]["positive"] == "A" and pairs[0]["negative"] == "B"
    assert {u["reason"] for u in unmatched} == {
        "no-free-count-matched-sibling", "no-count-matched-sibling"}


def test_GD_a_negative_is_consumed_on_first_use():
    """Reusing B would put the same section in the eval set twice and inflate n with
    a duplicate item. G-D fixes the resolution before the count existed."""
    pairs, _ = build_pairs(GD_COUNTS, GD_DEFECTS, tolerance=0)
    negatives = [p["negative"] for p in pairs]
    assert len(negatives) == len(set(negatives))


def test_GD_a_defect_sibling_is_never_offered_as_a_negative():
    """D is a defect section with the same count as A. It must not become A's
    negative even though it matches exactly."""
    pairs, _ = build_pairs(GD_COUNTS, GD_DEFECTS, tolerance=0)
    assert all(p["negative"] not in ("A", "D", "E") for p in pairs)


def test_the_ladder_always_closes():
    pairs, unmatched = build_pairs(GD_COUNTS, GD_DEFECTS, tolerance=0)
    assert len(pairs) + len(unmatched) == len(GD_DEFECTS)


def test_tolerance_zero_is_stricter_than_tolerance_one():
    strict, _ = build_pairs({"D": {"P": 5, "Q": 4}}, [("D", "P")], tolerance=0)
    loose, _ = build_pairs({"D": {"P": 5, "Q": 4}}, [("D", "P")], tolerance=1)
    assert len(strict) == 0 and len(loose) == 1


def test_negative_tolerance_is_refused():
    with pytest.raises(EvalSetError):
        build_pairs(GD_COUNTS, GD_DEFECTS, tolerance=-1)


def test_instruction_counts_ignore_unattributed_elements():
    recs = [{"frdoc": "d", "section_v11": "1.1"},
            {"frdoc": "d", "section_v11": "1.1"},
            {"frdoc": "d", "section_v11": None}]
    assert instruction_counts(recs, "v11") == {"d": {"1.1": 2}}


# ------------------------------------------------------------ the FROZEN corpus
@needs_freeze
def test_frozen_corpus_is_balanced_and_paired():
    items = load_items()
    pos = [i for i in items if i["label"] == "WILL_FAIL"]
    neg = [i for i in items if i["label"] == "WILL_EXECUTE"]
    assert len(items) == len(pos) + len(neg)
    assert len(pos) == len(neg), "the eval set is matched; it must be balanced"
    assert len({i["item_id"] for i in items}) == len(items), "no duplicate item"


@needs_freeze
def test_EXACT_instruction_count_matching_is_asserted():
    """plan.md: 'exact instruction-count matching asserted by a test'. This is it.
    CONTEXT.md section 8 calls it non-negotiable - unmatched, a hardcoded threshold on
    instruction count beats the agent, and that is how a predecessor died."""
    items = load_items()
    by_doc: dict[str, dict[str, list]] = {}
    for i in items:
        by_doc.setdefault(i["frdoc"], {}).setdefault(i["label"], []).append(i)
    checked = 0
    for frdoc, roles in by_doc.items():
        pos = sorted(roles.get("WILL_FAIL", []), key=lambda i: i["section"])
        neg = sorted(roles.get("WILL_EXECUTE", []), key=lambda i: i["section"])
        assert len(pos) == len(neg), f"{frdoc}: unbalanced within a document"
        assert sorted(p["instruction_count"] for p in pos) == \
            sorted(n["instruction_count"] for n in neg), \
            f"{frdoc}: instruction counts are not exactly matched"
        checked += len(pos)
    assert checked == len(items) // 2


@needs_freeze
def test_the_instruction_count_feature_alone_cannot_beat_chance():
    """The consequence of exact matching, stated as a measurement rather than as
    faith: positives and negatives have IDENTICAL instruction-count distributions, so
    a threshold on it is exactly at chance."""
    items = load_items()
    pos = sorted(i["instruction_count"] for i in items if i["label"] == "WILL_FAIL")
    neg = sorted(i["instruction_count"] for i in items if i["label"] == "WILL_EXECUTE")
    assert pos == neg, "the two classes must be indistinguishable on this feature"


@needs_freeze
def test_no_frozen_item_leaks():
    items = load_items()
    for i in items:
        v = leakage_violations(i["section_text"], i["fr_citation"])
        assert v == [], f"{i['item_id']} leaks: {v}"


@needs_freeze
def test_no_frozen_item_contains_ANY_fr_citation():
    """Stronger than plan.md rule (b), which only bans the item's OWN citation.
    Measured at 0 of 76 and asserted here so a rebuild cannot quietly weaken it."""
    import re
    pat = re.compile(r"\b\d{1,3}\s+FR\s+\d{1,6}\b")
    offenders = [i["item_id"] for i in load_items()
                 if pat.search(" ".join(i["section_text"].split()))]
    assert offenders == []


@needs_freeze
def test_no_frozen_item_contains_a_leakage_literal():
    items = load_items()
    for lit in LEAKAGE_LITERALS:
        bad = [i["item_id"] for i in items if lit in i["section_text"]]
        assert bad == [], f"{lit!r} survives in {bad}"


@needs_freeze
def test_the_as_of_edition_precedes_publication_STRICTLY():
    from cfr_pit import revision_date
    for i in load_items():
        rev = revision_date(int(i["cfr_title"]), i["as_of_edition"])
        assert rev.isoformat() < i["publication_date"], (
            f"{i['item_id']}: as-of edition {i['as_of_edition']} is not strictly "
            f"before publication {i['publication_date']}")


@needs_freeze
def test_positives_carry_their_note_and_negatives_carry_none():
    for i in load_items():
        if i["label"] == "WILL_FAIL":
            assert i["note_text"], f"{i['item_id']}: positive without its note"
            assert "could not be incorporated" in i["note_text"]
        else:
            assert i["note_text"] is None, \
                f"{i['item_id']}: a negative must carry no editorial note"


@needs_freeze
def test_every_item_declares_its_normalisation_level():
    """Hard rule 7: the level achieved is REPORTED, never applied silently."""
    assert {i["normalisation"] for i in load_items()} == {"whitespace-collapsed"}


@needs_freeze
def test_the_exclusion_ladder_closes_over_the_pool():
    d = json.loads(LADDER.read_text(encoding="utf-8"))
    rungs = d["ladder"]["rungs"]
    top = rungs["pool-citations-resolved"]["items"]
    dropped = sum(rungs[r]["positives"] for r in d["ladder"]["order"]
                  if r not in ("pool-citations-resolved", "kept"))
    assert dropped + rungs["kept"]["positives"] == top
    assert rungs["kept"]["positives"] == d["n_pairs"]
    assert d["n_items"] == 2 * d["n_pairs"]


@needs_freeze
def test_every_ladder_rung_prints_even_when_it_is_zero():
    """Hard rule 14: zero-occurrence branches print as zeros."""
    d = json.loads(LADDER.read_text(encoding="utf-8"))
    rungs = d["ladder"]["rungs"]
    assert len(rungs) == len(d["ladder"]["order"])
    assert any(r["items"] == 0 for r in rungs.values()), \
        "at least one rung is zero and it must still be present"


@needs_freeze
def test_the_stripper_proved_itself_before_the_freeze():
    """QUESTIONS.md Q8: a strip counter that prints zero may be looking for the wrong
    element name. The known-positive assertion is recorded IN the freeze."""
    d = json.loads(LEAKAGE.read_text(encoding="utf-8"))
    proof = d["known_positive_assertion"]
    assert proof["counts"] == {"EDNOTE": 2, "EFFDNOTP": 1, "CITA": 3, "EAR": 1,
                               "total": 7}
    assert len(proof["violations_before_stripping"]) > 0, \
        "the leakage test must FIRE on unstripped input"
    assert proof["violations_after_stripping"] == []


@needs_freeze
def test_the_EAR_zero_is_warranted_not_merely_printed():
    """EAR strips to 0 over the frozen corpus. Q8 says a zero is believed only after
    the counter has been shown to produce a non-zero - which the known-positive
    assertion does, at EAR=1."""
    d = json.loads(LEAKAGE.read_text(encoding="utf-8"))
    assert d["strip_counts_over_the_frozen_corpus"]["EAR"] == 0
    assert d["known_positive_assertion"]["counts"]["EAR"] == 1


@needs_freeze
def test_the_unstripped_leak_count_is_published():
    """plan.md CH-04: 'the count of items whose UNSTRIPPED text would have contained
    the answer. That number is itself a publishable result about the corpus.'"""
    d = json.loads(LEAKAGE.read_text(encoding="utf-8"))
    n = d["items_whose_UNSTRIPPED_text_would_have_leaked"]
    assert isinstance(n, int) and 0 <= n <= d["items_total"]
    assert n > 0, "if this were 0 the strips would be doing nothing and that is a claim"
