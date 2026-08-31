"""CH-06 — `src/a1.py` against `docs/evidence/ch06-a1/goldens.md`.

Every expected value in this file is transcribed from that goldens document, which was
hand-computed from `CONTEXT.md` §5 and committed at `aed8b17` BEFORE this file existed
(hard rule 4). Where a test and the code disagree, the GOLDEN wins.

Naming: `test_D1_*` is golden D1, and so on, so a failure names the fixture it broke.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import a1  # noqa: E402
import arms  # noqa: E402


# ============================================================ fixtures

UMBRELLA = {"operation": "amend", "anchor": None, "designation": None,
            "text": "1. Section 1.1 is amended as follows:"}
TARGETED = {"operation": "revise", "anchor": None, "designation": "(b)(4)",
            "text": "a. Revise paragraph (b)(4);"}


def item(instructions, **kw):
    base = {
        "item_id": "TEST-0001|1.1", "cfr_title": "40", "cfr_part": "1",
        "section": "1.1", "as_of_revision_date": "2004-07-01",
        "as_of_edition": 2004, "frdoc": "TEST-0001", "publication_date": "2005-01-01",
        "instruction_count": len(instructions), "instructions": instructions,
        "section_text": "§ 1.1\nA section.\n(a) alpha.\n(b) beta.\n",
        "label": "WILL_EXECUTE",
    }
    base.update(kw)
    return base


def facts_for(it):
    """The real resolver, unmodified — golden P6."""
    return a1.resolver_facts(it)


def rec(idx, executes, failure_class=None, **kw):
    d = {"instruction_index": idx, "executes": executes,
         "failure_class": failure_class, "why": "fixture"}
    d.update(kw)
    return d


# ============================================================ D — verdict is DERIVED

def test_D1_all_execute_gives_WILL_EXECUTE():
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(it, {1: rec(1, True), 2: rec(2, True)}, facts_for(it), 2)
    assert out["verdict"] == "WILL_EXECUTE"
    assert out["failing_designation"] is None
    assert out["failure_class"] is None
    assert out["instructions_unruled"] == []
    assert len(out["resolution_trace"]) == 2


def test_D2_one_failure_gives_WILL_FAIL_localised():
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(
        it, {1: rec(1, True), 2: rec(2, False, "target-does-not-exist")},
        facts_for(it), 2)
    assert out["verdict"] == "WILL_FAIL"
    assert out["failing_designation"] == "(b)(4)"
    assert out["failure_class"] == "target-does-not-exist"


def test_D2b_first_failing_instruction_wins_not_severity_not_model_order():
    """Three targeted instructions; 2 and 3 both fail. Document order decides."""
    ins = [dict(TARGETED, designation="(a)"), dict(TARGETED, designation="(b)"),
           dict(TARGETED, designation="(c)")]
    it = item(ins)
    out = a1.derive_output(
        it,
        # deliberately supplied in a scrambled dict order
        {3: rec(3, False, "quoted-text-not-present"),
         1: rec(1, True),
         2: rec(2, False, "target-does-not-exist")},
        facts_for(it), 3)
    assert out["verdict"] == "WILL_FAIL"
    assert out["failing_designation"] == "(b)"
    assert out["failure_class"] == "target-does-not-exist"


def test_D3_targeted_instruction_with_no_record_is_NOT_an_execute():
    """THE ANTI-GAMING GOLDEN. Omitting a record must never buy WILL_EXECUTE."""
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(it, {1: rec(1, True)}, facts_for(it), 1)
    assert out["verdict"] is None, "a missing targeted ruling must not derive a verdict"
    assert out["failing_designation"] is None
    assert out["failure_class"] is None
    assert out["instructions_unruled"] == [2]
    assert out["needs_human_review"] is True
    assert out["review_reason"].startswith("EMISSION INCOMPLETE")


def test_D3b_omitting_the_failing_record_cannot_escape_a_defect():
    """The other half of the attack: emit only the records that pass."""
    ins = [dict(TARGETED, designation="(a)"), dict(TARGETED, designation="(b)")]
    it = item(ins)
    out = a1.derive_output(it, {1: rec(1, True)}, facts_for(it), 1)
    assert out["verdict"] is None
    assert out["instructions_unruled"] == [2]


def test_D4_umbrella_with_no_record_is_auto_filled_and_says_so():
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(it, {2: rec(2, True)}, facts_for(it), 1)
    assert out["verdict"] == "WILL_EXECUTE"
    assert out["instructions_unruled"] == []
    assert out["resolution_trace"][0]["model_ruling"]["auto_filled"] is True, \
        "a harness fill that is not visible in the artifact is manufactured evidence"


def test_D5_failure_class_outside_the_five_is_dropped_not_adopted():
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(
        it, {1: rec(1, True), 2: rec(2, False, "paragraph-mismatch")},
        facts_for(it), 2)
    assert out["verdict"] == "WILL_FAIL", "the finding survives"
    assert out["failure_class"] is None, "the invented vocabulary does not"
    assert out["needs_human_review"] is True
    assert "NOT one of" in out["review_reason"]


def test_D5b_the_five_classes_are_exactly_CONTEXT_md_section_5():
    assert a1.FAILURE_CLASSES == (
        "target-does-not-exist", "target-already-exists", "quoted-text-not-present",
        "incomplete-set-out-text", "incorrect-citation-or-designation")


def test_D6_no_records_at_all_gives_a_null_verdict():
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(it, {}, facts_for(it), 0)
    assert out["verdict"] is None
    assert out["needs_human_review"] is True


def test_D7_trace_carries_resolver_facts_even_with_zero_tool_calls():
    """A1-minus-tool still emits the note. These are facts about the ITEM."""
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(it, {1: rec(1, True), 2: rec(2, True)}, facts_for(it), 0)
    assert out["tool_calls_made"] == 0
    for t in out["resolution_trace"]:
        for key in ("found", "level", "designation_exists", "siblings", "char_offset"):
            assert key in t, f"{key} missing from the trace"


def test_D8_the_model_has_no_channel_for_a_section_verdict():
    """`verdict` is DERIVED. A model record claiming one must not be honoured."""
    it = item([UMBRELLA, TARGETED])
    out = a1.derive_output(
        it,
        {1: rec(1, True, verdict="WILL_FAIL"),
         2: rec(2, True, verdict="WILL_FAIL")},
        facts_for(it), 2)
    assert out["verdict"] == "WILL_EXECUTE", \
        "the section verdict must come from the rulings, not from a field the model set"


# ============================================================ C — human checkpoint

def test_C0_the_clean_case_routes_NOTHING():
    """A checkpoint that fires on everything is an opt-out dressed as caution."""
    it = item([UMBRELLA, dict(TARGETED, designation="(a)")])
    assert a1.human_checkpoint_reasons(it, facts_for(it)) == []
    out = a1.derive_output(it, {1: rec(1, True), 2: rec(2, True)}, facts_for(it), 1)
    assert out["needs_human_review"] is False
    assert out["review_reason"] is None


def test_C1_anchor_absent_while_target_present():
    it = item([{"operation": "remove", "anchor": "text that is not in the section",
                "designation": "(a)", "text": "Remove ..."}])
    reasons = a1.human_checkpoint_reasons(it, facts_for(it))
    assert any(r.startswith("C1 instruction 1:") for r in reasons), reasons


def test_C2_both_paths_asked_and_disagreeing():
    it = item([{"operation": "remove", "anchor": "text that is not in the section",
                "designation": "(a)", "text": "Remove ..."}])
    reasons = a1.human_checkpoint_reasons(it, facts_for(it))
    assert any(r.startswith("C2 instruction 1:") for r in reasons), reasons


def test_C2_needs_BOTH_paths_asked():
    """A designation with no anchor fires C1 only — C2 requires both."""
    it = item([{"operation": "revise", "anchor": None, "designation": "(a)",
                "text": "Revise (a)."}])
    reasons = a1.human_checkpoint_reasons(it, facts_for(it))
    assert not any(r.startswith("C2") for r in reasons), reasons


def test_C3_a_designation_touched_twice():
    ins = [{"operation": "redesignate", "anchor": None, "designation": "(a)(38)",
            "text": "Redesignate (a)(38) ..."},
           {"operation": "add", "anchor": None, "designation": "(a)(38)",
            "text": "Add new paragraph (a)(38) ..."}]
    it = item([UMBRELLA, UMBRELLA] + ins)
    reasons = a1.human_checkpoint_reasons(it, facts_for(it))
    c3 = [r for r in reasons if r.startswith("C3")]
    assert c3, reasons
    assert "C3 designation (a)(38) is touched by instructions [3, 4]" in c3[0]
    assert "R-01" in c3[0], "the removal ruling must be named in the escalation"


def test_C3_fires_on_the_REAL_item_05_8447_75_6():
    """CONTEXT.md §9's hard case, on the real corpus rather than a fixture.

    §2c requires at least one eval item to route to the queue. This asserts that at
    least one does, on data, so the requirement cannot be satisfied by a fixture."""
    path = REPO / "data/evalset/items.jsonl"
    items = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    target = [i for i in items if i["item_id"] == "05-8447|75.6"]
    assert target, "the exemplar item is missing from the frozen eval set"
    reasons = a1.human_checkpoint_reasons(target[0], a1.resolver_facts(target[0]))
    assert any(r.startswith("C3 designation (a)(38)") for r in reasons), reasons


def test_C_at_least_one_real_eval_item_routes():
    path = REPO / "data/evalset/items.jsonl"
    items = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    routed = [i["item_id"] for i in items
              if a1.human_checkpoint_reasons(i, a1.resolver_facts(i))]
    assert routed, "no eval item routes to the human queue; §2c requires at least one"
    # and NOT all of them - a checkpoint that fires everywhere measures nothing
    assert len(routed) < len(items), \
        f"every one of {len(items)} items routed; that is not a checkpoint"


# ============================================================ E — emission parsing

GOOD_JSON = ('{"instructions": [{"instruction_index": 1, "executes": true, '
             '"failure_class": null}, {"instruction_index": 2, "executes": false, '
             '"failure_class": "target-does-not-exist"}]}')


def test_E1_bare_json():
    out = a1.extract_records(GOOD_JSON)
    assert sorted(out) == [1, 2]
    assert out[2]["failure_class"] == "target-does-not-exist"


def test_E2_fenced_json():
    assert sorted(a1.extract_records("```json\n" + GOOD_JSON + "\n```")) == [1, 2]


def test_E3_prose_wrapped_json():
    assert sorted(a1.extract_records("Here you go:\n" + GOOD_JSON + "\nHope that helps.")) == [1, 2]


def test_E4_a_refusal_parses_to_nothing():
    assert a1.extract_records("I cannot determine this.") == {}


def test_E5_an_empty_completion_parses_to_nothing():
    """13 of 20 sonnet completions at the checkpoint were empty and nobody noticed
    until afterwards. The behaviour was right; the missing thing was this test."""
    assert a1.extract_records("") == {}
    assert a1.extract_records(None) == {}


def test_E6_records_without_an_index_are_positional():
    out = a1.extract_records('{"instructions": [{"executes": true}, {"executes": false}]}')
    assert sorted(out) == [1, 2]


def test_E_unparseable_emission_scores_as_a_FAILURE_end_to_end():
    """E4 + D6 joined up, through the real scorer: a non-answer is charged, not skipped."""
    from score import score
    it = item([UMBRELLA, TARGETED], label="WILL_FAIL")
    out = a1.derive_output(it, a1.extract_records("I cannot determine this."),
                           facts_for(it), 0)
    res = score([{"item_id": it["item_id"], "label": "WILL_FAIL"}],
                {it["item_id"]: out["verdict"]})
    assert res["success"] == 0 and res["failure"] == 1
    assert res["success"] + res["failure"] == res["n"]


# ============================================================ P — parity and purity

def test_P1_P2_prompt_document_parity():
    parity = a1.assert_skill_matches_agents_md()
    assert parity["skill_chars"] > 4000


def test_P3_the_duplicate_arm_is_refused():
    assert "A1-minus-skill" not in a1.ARMS
    assert "A1-minus-skill" in a1.REFUSED_ARMS
    assert a1.main(["run", "--arm", "A1-minus-skill"]) == 2


def test_P4_A1_and_B0_agent_get_the_SAME_head_and_body():
    """CONTEXT.md §4: the arms differ in capabilities, not in briefing."""
    path = REPO / "data/evalset/items.jsonl"
    it = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    a1_prompt = a1.user_prompt(it)
    b0a_prompt = arms.user_prompt(it, gets_text=True)
    marker = "--- END SECTION TEXT ---"
    assert a1_prompt.split(marker)[0] == b0a_prompt.split(marker)[0], \
        "A1 and B0-agent are briefed differently before the tail; that is not a "\
        "capability difference, it is a confound"


def test_P5_determinism():
    it = item([UMBRELLA, TARGETED])
    recs = {1: rec(1, True), 2: rec(2, False, "target-does-not-exist")}
    a = json.dumps(a1.derive_output(it, recs, facts_for(it), 2), sort_keys=True)
    b = json.dumps(a1.derive_output(it, recs, facts_for(it), 2), sort_keys=True)
    assert a == b


def test_P6_cfr_resolve_is_the_CH05_module_unmodified():
    import cfr_resolve
    assert a1.cfr_resolve is cfr_resolve.cfr_resolve


def test_P_system_prompts_differ_only_where_the_arms_do():
    s_iter1 = a1.system_prompt("A1-iter1")
    s_a1 = a1.system_prompt("A1")
    s_notool = a1.system_prompt("A1-minus-tool")
    skill = a1.load_skill()
    assert skill not in s_iter1, "A1-iter1 must not receive the procedure"
    assert skill in s_a1
    assert skill in s_notool
    assert "You have a deterministic tool" in s_iter1
    assert "You have a deterministic tool" in s_a1
    assert "You have NO tool" in s_notool
    for s in (s_iter1, s_a1, s_notool):
        assert "You do NOT emit a verdict for the section." in s
        assert "Do NOT emit a section-level verdict." in s


def test_P_the_tool_cannot_be_redirected_at_other_text():
    """The model may set only designation / quoted_text / instruction_index."""
    props = set(a1.TOOL_SCHEMA["input_schema"]["properties"])
    assert props == {"designation", "quoted_text", "instruction_index"}
    for forbidden in ("title", "part", "section", "as_of_date", "text"):
        assert forbidden not in props, \
            f"the model can set {forbidden}, so it can choose its own evidence"


@pytest.mark.parametrize("arm", sorted(a1.ARMS))
def test_P_every_arm_names_the_output_contract(arm):
    assert "instruction_index" in a1.system_prompt(arm)
