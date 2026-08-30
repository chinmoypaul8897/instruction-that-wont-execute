"""CH-05 - `cfr_resolve` against goldens hand-computed before the code.

Every expected value is transcribed from `docs/evidence/ch05-resolve/goldens.md`,
committed at 715eeec BEFORE `src/cfr_resolve.py` existed. Hard rule 4.

The fixture is 27 characters long on purpose: every offset below was counted by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cfr_resolve import (  # noqa: E402
    LEVELS,
    ResolveError,
    cfr_resolve,
    declared_designations,
    designation_state,
    find_anchor,
    parse_designation,
)

#          0         1         2
#          0123456789012345678901234567
TEXT = "(a) alpha. (b) beta  gamma."


def resolve(**kw):
    return cfr_resolve("40", "52", "52.10", "2020-01-01", TEXT, **kw)


# ------------------------------------------------------------------ golden R-A
@pytest.mark.parametrize("raw,expected", [
    ("(b)(4)(i)(A)", ["b", "4", "i", "A"]),
    ("(a)", ["a"]),
    ("(b)(1)", ["b", "1"]),
    ("", []),
    (None, []),
    ("(b) (4)", ["b", "4"]),
])
def test_RA_parse_designation(raw, expected):
    assert parse_designation(raw) == expected


@pytest.mark.parametrize("bad", ["b4iA", "(b", "paragraph (b)", "(toolonggroup)"])
def test_RG_a_non_designation_is_REFUSED_not_guessed(bad):
    """Guessing at a target the instruction never named is the defect this tool is
    built to catch, not to commit."""
    with pytest.raises(ResolveError):
        parse_designation(bad)


# ------------------------------------------------------------------ golden R-B
def test_RB_declared_designations_and_offsets():
    assert declared_designations(TEXT) == [("(a)", 0), ("(b)", 11)]


@pytest.mark.parametrize("query,exists,siblings", [
    ("(a)", True, ["(a)", "(b)"]),
    ("(b)", True, ["(a)", "(b)"]),
    ("(c)", False, ["(a)", "(b)"]),
    # goldens.md R-B says ["(a)", "(b)"] here, not []. The first version of this test
    # transcribed [] and FAILED. The TRANSCRIPTION was wrong, not the golden and not
    # the code; recorded as ERRATA E-1 in docs/evidence/ch05-resolve/goldens.md.
    ("(b)(1)", False, ["(a)", "(b)"]),
])
def test_RB_designation_state(query, exists, siblings):
    s = designation_state(TEXT, query)
    assert s["designation_exists"] is exists
    assert s["siblings"] == siblings


def test_RB_siblings_are_returned_even_on_a_MISS():
    """The point of the field. Section 9's hard cases - 'revising a definition that did
    not exist', 'adding an entry that already exists' - are answered by what surrounds
    the target, not by the target."""
    s = designation_state(TEXT, "(c)")
    assert s["designation_exists"] is False
    assert s["siblings"] == ["(a)", "(b)"], "a miss must still report the neighbours"


def test_RB_a_cross_reference_in_prose_is_not_a_declaration():
    """`as described in (z)` must not invent a paragraph (z)."""
    text = "(a) alpha as described in (z) above."
    assert declared_designations(text) == [("(a)", 0)]
    assert designation_state(text, "(z)")["designation_exists"] is False


# ------------------------------------------------------------------ golden R-C
@pytest.mark.parametrize("quoted,level,offset,span", [
    ("beta  gamma", "exact", 15, "beta  gamma"),
    ("beta gamma", "whitespace-collapsed", 15, "beta  gamma"),
    ("betagamma", "alphanumeric-only", 15, "beta  gamma"),
    ("Beta Gamma", "none", None, None),
    ("alpha", "exact", 4, "alpha"),
    ("", "none", None, None),
    (None, "none", None, None),
])
def test_RC_the_three_declared_levels(quoted, level, offset, span):
    r = find_anchor(TEXT, quoted)
    assert r["level"] == level
    assert r["char_offset"] == offset
    assert r["matched_span"] == span
    assert r["found"] is (level != "none")


def test_RC4_alphanumeric_only_does_NOT_fold_case():
    """The test that stops the levels becoming a licence. CONTEXT.md section 1: no
    unicode folding anywhere. Folding case would make (A) and (a) the same
    designation, and those are the objects the whole project rests on."""
    assert find_anchor(TEXT, "Beta Gamma")["level"] == "none"
    assert find_anchor(TEXT, "BETAGAMMA")["level"] == "none"
    assert find_anchor(TEXT, "betagamma")["level"] == "alphanumeric-only"


def test_RC_the_first_matching_level_wins():
    """A string that matches exactly must never be reported as a weaker level."""
    r = find_anchor(TEXT, "beta  gamma")
    assert r["level"] == "exact"
    assert r["levels_tried"] == ["exact"], "no weaker level is even attempted"


def test_RC_levels_are_tried_in_the_declared_order():
    assert find_anchor(TEXT, "zzz")["levels_tried"] == list(LEVELS)


# ------------------------------------------------------------------ golden R-D
@pytest.mark.parametrize("quoted", ["beta  gamma", "beta gamma", "betagamma", "alpha"])
def test_RD_char_offset_indexes_the_CALLERS_string_at_every_level(quoted):
    r = find_anchor(TEXT, quoted)
    s, span = r["char_offset"], r["matched_span"]
    assert TEXT[s:s + len(span)] == span


def test_RD_offset_survives_a_realistic_multiline_text():
    text = ("(a) This section applies.\n"
            "(b) The Administrator shall   review\n"
            "    the plan annually.\n")
    r = find_anchor(text, "The Administrator shall review the plan annually.")
    assert r["level"] == "whitespace-collapsed"
    s, span = r["char_offset"], r["matched_span"]
    assert text[s:s + len(span)] == span
    assert span.startswith("The Administrator")
    assert span.endswith("annually.")


# ------------------------------------------------------------------ golden R-E
def test_RE_found_and_designation_exists_are_INDEPENDENT():
    r = resolve(designation="(c)", quoted_text="alpha")
    assert r["designation_exists"] is False
    assert r["found"] is True and r["level"] == "exact" and r["char_offset"] == 4

    r = resolve(designation="(a)", quoted_text="delta")
    assert r["designation_exists"] is True
    assert r["found"] is False and r["level"] == "none"

    r = resolve(designation="(c)", quoted_text=None)
    assert r["designation_exists"] is False and r["found"] is False


def test_RE_designation_exists_is_NULL_when_nothing_was_asked():
    """False would assert that a designation is absent when none was queried."""
    r = resolve(designation=None, quoted_text="alpha")
    assert r["designation_exists"] is None
    assert r["found"] is True


def test_RE_designation_state_is_computed_even_when_the_anchor_is_absent():
    """Section 6: a pure quoted-string matcher no-ops on ~80% of the pool. The
    designation half must not be skipped when there is no anchor to find."""
    r = resolve(designation="(b)", quoted_text=None)
    assert r["designation_exists"] is True
    assert r["siblings"] == ["(a)", "(b)"]


# ------------------------------------------------------------------ golden R-F/R-G
def test_RF_the_resolver_never_mutates_its_input():
    before = TEXT
    resolve(designation="(a)", quoted_text="alpha")
    assert TEXT == before


def test_RF_deterministic():
    a = resolve(designation="(b)(1)", quoted_text="beta gamma")
    b = resolve(designation="(b)(1)", quoted_text="beta gamma")
    assert a == b


def test_RF_the_resolver_fetches_nothing():
    """Hard rule 8. It is handed the text or it refuses; a resolver that reached for
    the network could not be replayed offline (plan.md CH-11 Tier 1)."""
    import cfr_resolve as mod
    src = Path(mod.__file__).read_text(encoding="utf-8")
    for forbidden in ("urllib", "requests", "socket", "http.client",
                      "datetime.now", "time.time", "random."):
        assert forbidden not in src, f"{forbidden} must not appear in the resolver"
    with pytest.raises(ResolveError):
        cfr_resolve("40", "52", "52.10", "2020-01-01", None, quoted_text="x")


def test_RG_the_identifiers_are_echoed_so_a_trace_can_be_checked():
    r = resolve(designation="(a)", quoted_text="alpha")
    assert (r["title"], r["part"], r["section"], r["as_of_date"]) == \
        ("40", "52", "52.10", "2020-01-01")
    assert r["normalisation_levels_declared"] == list(LEVELS)


def test_the_declared_levels_are_exactly_the_three_the_spec_names():
    assert LEVELS == ("exact", "whitespace-collapsed", "alphanumeric-only")


def test_the_level_is_REPORTED_on_every_call_including_a_miss():
    """Hard rule 7: the level achieved is reported, never applied silently. A call
    that found nothing must still say which levels it tried."""
    r = resolve(quoted_text="nothing here")
    assert r["level"] == "none"
    assert r["levels_tried"] == list(LEVELS)
