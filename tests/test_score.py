"""CH-04 - the scorer and the B-script null, against goldens hand-computed first.

Every expected value is transcribed from `docs/evidence/ch04-scorer/goldens.md`,
committed at 8dae806 BEFORE `src/score.py` and `src/bscript.py` existed. Hard rule 4.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from bscript import (  # noqa: E402
    BScriptError,
    best_threshold,
    cv_accuracy,
    features,
    fold_assignment,
    permutation_null,
)
from score import (  # noqa: E402
    GUARD_FALSE_DEFECT_MAX,
    GUARD_MISSED_DEFECT_MAX,
    ScoreError,
    binom_tail_le,
    detectable_effect,
    mcnemar,
    normalise_verdict,
    score,
)

F, E = "WILL_FAIL", "WILL_EXECUTE"


# ------------------------------------------------------------------ golden S-A
SA_ITEMS = [{"item_id": f"p{i}", "label": F} for i in (1, 2, 3, 4)] + \
           [{"item_id": f"n{i}", "label": E} for i in (1, 2, 3, 4)]
SA_PRED = {"p1": F, "p2": F, "p3": E, "p4": E,
           "n1": E, "n2": E, "n3": E, "n4": F}


def test_SA_primary_metric_and_rates():
    r = score(SA_ITEMS, SA_PRED)
    assert r["n"] == 8 and r["n_positives"] == 4 and r["n_negatives"] == 4
    assert r["success"] == 5 and r["failure"] == 3
    assert r["accuracy"] == pytest.approx(0.6250)
    assert r["false_defect_count"] == 1
    assert r["false_defect_rate"] == pytest.approx(0.2500)
    assert r["missed_defect_count"] == 2
    assert r["missed_defect_rate"] == pytest.approx(0.5000)


def test_SA_success_plus_failure_equals_n_is_ASSERTED():
    r = score(SA_ITEMS, SA_PRED)
    assert r["success"] + r["failure"] == r["n"] == 8


def test_SA_the_guards_are_actually_wired_up():
    """The fixture is chosen so one guard passes AT its boundary and the other FAILS.
    A fixture where every guard passes cannot show the guards are connected."""
    r = score(SA_ITEMS, SA_PRED)
    assert r["false_defect_rate"] == GUARD_FALSE_DEFECT_MAX
    assert r["guard_false_defect_pass"] is True
    assert r["missed_defect_rate"] > GUARD_MISSED_DEFECT_MAX
    assert r["guard_missed_defect_pass"] is False


def test_a_missing_prediction_is_a_FAILURE_not_a_skip():
    """An arm must not be able to raise its accuracy by declining to answer."""
    pred = dict(SA_PRED)
    del pred["p1"]
    r = score(SA_ITEMS, pred)
    assert r["n"] == 8, "the denominator must not shrink"
    assert r["success"] == 4 and r["failure"] == 4
    assert r["unparseable_or_absent"] == 1
    assert r["missed_defect_count"] == 3, "charged to the class it failed to get right"


@pytest.mark.parametrize("raw", [None, "", "maybe", "{}", "WILL FAIL", "unsure", 42])
def test_unparseable_verdicts_are_none_and_score_as_failures(raw):
    assert normalise_verdict(raw) is None
    r = score([{"item_id": "x", "label": F}], {"x": raw})
    assert r["success"] == 0 and r["failure"] == 1 and r["n"] == 1


@pytest.mark.parametrize("raw,want", [
    ("WILL_FAIL", F), ("will_fail", F), ('  "WILL_EXECUTE" ', E), ("will_execute", E)])
def test_verdict_normalisation_accepts_only_the_contract_values(raw, want):
    assert normalise_verdict(raw) == want


def test_duplicate_item_id_is_refused():
    with pytest.raises(ScoreError):
        score([{"item_id": "x", "label": F}, {"item_id": "x", "label": E}], {})


def test_a_gold_label_outside_the_contract_is_refused():
    with pytest.raises(ScoreError):
        score([{"item_id": "x", "label": "MAYBE"}], {"x": F})


# ------------------------------------------------------------------ golden S-B
@pytest.mark.parametrize("b,c,expected", [
    (8, 2, 0.109375),
    (10, 0, 0.001953125),
    (5, 5, 1.0),
    (0, 0, 1.0),
])
def test_SB_mcnemar_exact(b, c, expected):
    a_correct = [True] * b + [False] * c + [True] * 3 + [False] * 3
    b_correct = [False] * b + [True] * c + [True] * 3 + [False] * 3
    r = mcnemar(a_correct, b_correct)
    assert r["b_only_a_correct"] == b
    assert r["c_only_b_correct"] == c
    assert r["p_value"] == pytest.approx(expected)


def test_SB_concordant_pairs_are_excluded_not_counted():
    """Adding pairs where both arms agree must not move the p-value at all."""
    a = [True] * 8 + [False] * 2
    b = [False] * 8 + [True] * 2
    p1 = mcnemar(a, b)["p_value"]
    p2 = mcnemar(a + [True] * 40, b + [True] * 40)["p_value"]
    assert p1 == pytest.approx(p2) == pytest.approx(0.109375)


def test_binomial_tail_is_exact():
    assert binom_tail_le(2, 10) == pytest.approx(56 / 1024)
    assert binom_tail_le(0, 10) == pytest.approx(1 / 1024)
    assert binom_tail_le(10, 10) == pytest.approx(1.0)
    assert binom_tail_le(0, 0) == 1.0


def test_mcnemar_refuses_mismatched_vectors():
    with pytest.raises(ScoreError):
        mcnemar([True, False], [True])


# ------------------------------------------------------------------ golden S-C
def test_SC_best_threshold():
    values = [3, 4, 5, 1, 2, 3]
    labels = [F, F, F, E, E, E]
    r = best_threshold(values, labels)
    assert r["accuracy"] == pytest.approx(5 / 6)
    assert r["direction"] == ">="
    assert r["threshold"] == 3, "declared tie-break: the LOWEST threshold"


def test_SC_the_mirror_direction_is_tried():
    """A feature that separates in REVERSE is still a trivial attack."""
    values = [1, 2, 3, 8, 9, 10]
    labels = [F, F, F, E, E, E]
    r = best_threshold(values, labels)
    assert r["accuracy"] == pytest.approx(1.0)
    assert r["direction"] == "<="


# ------------------------------------------------------------------ golden S-D
def _SD_rows():
    return [
        {"item_id": "a", "label": F, "group": "d1", "features": {"f": 2.0}},
        {"item_id": "b", "label": F, "group": "d2", "features": {"f": 2.0}},
        {"item_id": "c", "label": E, "group": "d1", "features": {"f": 1.0}},
        {"item_id": "d", "label": E, "group": "d2", "features": {"f": 1.0}},
    ]


def test_SD_free_permutation_exhaustive_is_2_of_6():
    """goldens.md S-D, hand-computed: p = 2/6 = 0.3333 over the SIX free label
    assignments. Enumerated HERE, in the test, rather than by calling the sampling
    implementation - so the golden checks `cv_accuracy` against a hand count and not
    the null against itself."""
    rows = _SD_rows()
    observed = cv_accuracy(rows)["best_accuracy"]
    assert observed == pytest.approx(1.0)
    ids = [r["item_id"] for r in rows]
    at_least = 0
    for positives in itertools.combinations(ids, 2):
        for r in rows:
            r["label"] = F if r["item_id"] in positives else E
        if cv_accuracy(rows)["best_accuracy"] >= observed:
            at_least += 1
    assert at_least == 2, "only {a,b} and its mirror {c,d} separate perfectly"
    assert at_least / 6 == pytest.approx(2 / 6)


def test_SD_within_pair_null_over_two_pairs_is_2_of_4():
    """The WITHIN-PAIR null is a different test from S-D's free null and its p-value
    is not interchangeable with it - goldens.md S-E says so in terms.

    Hand-traced over 2 pairs = 4 draws. Keep-both and swap-both both separate
    perfectly (the mirror rule catches the swapped one); the two mixed draws put a
    2 and a 1 in each class and score 0.5. So p = 2/4 = 0.5, NOT 2/6.

    The first version of this test asserted 1.0 and FAILED. The expectation was
    wrong, not the code; the correction is recorded as ERRATA E-1 in
    docs/evidence/ch04-scorer/goldens.md rather than edited out of it."""
    r = permutation_null(_SD_rows(), [("a", "c"), ("b", "d")], n_permutations=64)
    assert r["mode"] == "exhaustive"
    assert r["n_draws"] == 4
    assert r["observed_best_cv_accuracy"] == pytest.approx(1.0)
    assert r["p_value"] == pytest.approx(0.5)


def test_SD_the_null_restores_the_true_labels():
    """A null that leaves the data permuted poisons whatever runs next, and that is a
    silent corruption rather than an error."""
    rows = [
        {"item_id": "a", "label": F, "group": "d1", "features": {"f": 2.0}},
        {"item_id": "c", "label": E, "group": "d1", "features": {"f": 1.0}},
    ]
    permutation_null(rows, [("a", "c")], n_permutations=8)
    assert [r["label"] for r in rows] == [F, E]


def test_SD_p_value_can_never_be_zero():
    rows = [
        {"item_id": "a", "label": F, "group": "d1", "features": {"f": 9.0}},
        {"item_id": "c", "label": E, "group": "d1", "features": {"f": 1.0}},
        {"item_id": "b", "label": F, "group": "d2", "features": {"f": 8.0}},
        {"item_id": "d", "label": E, "group": "d2", "features": {"f": 2.0}},
    ]
    assert permutation_null(rows, [("a", "c"), ("b", "d")],
                            n_permutations=64)["p_value"] > 0


def test_permutation_null_refuses_a_pair_it_does_not_hold():
    rows = [{"item_id": "a", "label": F, "group": "d1", "features": {"f": 1.0}}]
    with pytest.raises(BScriptError):
        permutation_null(rows, [("a", "missing")], n_permutations=4)


# ------------------------------------------------------------------ golden S-F
def test_SF_fold_assignment_groups_by_document_and_uses_no_rng():
    assign = fold_assignment(["d3", "d1", "d7", "d2", "d5", "d4", "d6"])
    assert assign == {"d1": 0, "d2": 1, "d3": 2, "d4": 3, "d5": 4, "d6": 0, "d7": 1}
    assert fold_assignment(["d1", "d2"]) == fold_assignment(["d2", "d1"])


def test_SF_a_document_never_straddles_a_fold():
    rows = [{"item_id": f"{d}-{r}", "label": F if r == "p" else E, "group": d,
             "features": {"f": 1.0}}
            for d in ("d1", "d2", "d3", "d4", "d5", "d6") for r in ("p", "n")]
    assign = fold_assignment([r["group"] for r in rows])
    for d in {r["group"] for r in rows}:
        folds = {assign[r["group"]] for r in rows if r["group"] == d}
        assert len(folds) == 1


# ------------------------------------------------------------------ determinism
def test_SG_the_null_is_byte_reproducible_at_a_fixed_seed():
    def build():
        return [{"item_id": x, "label": lab, "group": g, "features": {"f": v}}
                for x, lab, g, v in [
                    ("a", F, "d1", 3.0), ("c", E, "d1", 1.0),
                    ("b", F, "d2", 4.0), ("d", E, "d2", 2.0),
                    ("e", F, "d3", 5.0), ("g", E, "d3", 9.0),
                    ("h", F, "d4", 6.0), ("i", E, "d4", 0.0),
                    ("j", F, "d5", 7.0), ("k", E, "d5", 1.5),
                    ("l", F, "d6", 2.5), ("m", E, "d6", 8.0),
                    ("n", F, "d7", 3.5), ("o", E, "d7", 2.2),
                    ("q", F, "d8", 4.5), ("r", E, "d8", 1.1),
                    ("s", F, "d9", 5.5), ("t", E, "d9", 0.4),
                    ("u", F, "d10", 6.5), ("v", E, "d10", 0.9),
                    ("w", F, "d11", 7.5), ("x", E, "d11", 1.9),
                    ("y", F, "d12", 8.5), ("z", E, "d12", 2.9),
                    ("A", F, "d13", 9.5), ("B", E, "d13", 3.9)]]
    pairs = [(a, b) for a, b in [("a", "c"), ("b", "d"), ("e", "g"), ("h", "i"),
                                 ("j", "k"), ("l", "m"), ("n", "o"), ("q", "r"),
                                 ("s", "t"), ("u", "v"), ("w", "x"), ("y", "z"),
                                 ("A", "B")]]
    r1 = permutation_null(build(), pairs, n_permutations=200)
    r2 = permutation_null(build(), pairs, n_permutations=200)
    assert r1["mode"] == "sampled", "13 pairs is 8192 draws - above the exhaustive cap"
    assert r1["p_value"] == r2["p_value"]
    assert r1["null_p95"] == r2["null_p95"]


# ------------------------------------------------------------------ features
def test_features_never_read_the_label_or_the_editorial_note():
    """A feature that read `note_text` would score 1.0 and measure nothing. It is
    present on positives only, and this asserts it is not consumed."""
    item = {"item_id": "x", "label": F, "frdoc": "d1", "section": "52.10",
            "cfr_title": "40", "instruction_count": 2, "as_of_edition": 2020,
            "publication_date": "2021-05-05", "section_text": "(a) text",
            "document_amdpar_count": 10, "document_completeness_v11": 0.5,
            "note_text": "could not be incorporated - THE ANSWER",
            "instructions": [{"operation": "revise", "anchor": "abc",
                              "designation": "(a)", "text": "revise paragraph (a)"},
                             {"operation": "remove", "anchor": None,
                              "designation": "(b)", "text": "remove paragraph (b)"}]}
    f = features(item)
    leaked = {k for k, v in f.items()
              if isinstance(v, float) and v == len(item["note_text"])}
    assert not leaked
    without = features({**item, "note_text": None, "label": E})
    assert f == without, "features must not depend on the label or the note"


def test_features_are_all_numeric_and_there_are_at_least_26():
    item = {"item_id": "x", "label": F, "frdoc": "d", "section": "1.1",
            "cfr_title": "1", "instruction_count": 0, "instructions": [],
            "section_text": "", "as_of_edition": 2000,
            "publication_date": "2001-01-01", "document_amdpar_count": 0,
            "document_completeness_v11": 0.0}
    f = features(item)
    assert len(f) >= 26, f"CONTEXT.md section 4 says ~26 cheap features; got {len(f)}"
    assert all(isinstance(v, float) for v in f.values())


def test_cv_refuses_empty_input():
    with pytest.raises(BScriptError):
        cv_accuracy([])


# ------------------------------------------------------------------ power
def test_detectable_effect_is_reported_not_asserted():
    d = detectable_effect(50)
    assert d["n_pairs"] == 50 and d["n_items"] == 100
    # 2 * P(X<=0 | n) < 0.05  =>  2/2^n < 0.05  =>  2^n > 40  =>  n >= 6
    assert d["min_discordant_all_one_way"] == 6
    assert d["min_detectable_gap_pp"] == pytest.approx(6.0)
