"""CH-06 — regression tests for two defects found during the CH-06 run itself.

**D1 — the bundler silently produced ZERO records for `B0prime`.**
`RunLogger` writes one trajectory per run, and `B0prime` logs one run PER SAMPLE, so its
files are named `B0prime__<item>__rep1__s1.jsonl`. `bundle()` globbed only
`{arm}__*__rep{rep}.jsonl`, matched nothing, and **wrote an empty bundle without
erroring**. `docs/trajectories/arms/per-item/` is git-ignored, so 246 trajectories would
have been left out of the repository entirely — a hard rule 10 violation produced by a
glob, announced by nothing except a `0` in a progress line nobody was required to read.

**D2 — the tie-break had no test**, because it was written inline inside a function that
makes network calls. It is extracted to `tally_votes()` here so the published rule is
checkable without spending money.

Goldens for `tally_votes` are hand-computed from the rule as it was published in
`src/arms.py::run_b0prime`'s docstring **before the arm ran**:

    "Majority over `samples` votes; A TIE RESOLVES TO WILL_FAIL. ... An unparseable
     vote is NOT a vote and is dropped from the tally; an item where every vote is
     unparseable gets no prediction and `score.py` charges it as a failure."
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import arms  # noqa: E402

FAIL, EXEC = "WILL_FAIL", "WILL_EXECUTE"


# ============================================================ D1 — the bundler

def _touch(d: Path, name: str, lines: int = 2) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text("".join('{"record": "x"}\n' for _ in range(lines)),
                          encoding="utf-8", newline="\n")


def test_D1_bundle_collects_sample_suffixed_trajectories(tmp_path, monkeypatch):
    """The B0prime shape. Before the fix this returned 0 and lost every file."""
    traj, bundle_dir = tmp_path / "per-item", tmp_path / "bundles"
    monkeypatch.setattr(arms, "DEFAULT_TRAJ", traj)
    monkeypatch.setattr(arms, "BUNDLE_DIR", bundle_dir)
    for s in (1, 2, 3):
        _touch(traj, f"B0prime__05-8447_75.6__rep1__s{s}.jsonl", lines=4)
    n = arms.bundle("B0prime", 1)
    assert n == 12, "sample-suffixed trajectories must be bundled, not silently skipped"
    assert (bundle_dir / "B0prime-rep1.jsonl").exists()


def test_D1_bundle_still_collects_the_plain_shape(tmp_path, monkeypatch):
    """The B0 / B0-agent shape must not regress."""
    traj, bundle_dir = tmp_path / "per-item", tmp_path / "bundles"
    monkeypatch.setattr(arms, "DEFAULT_TRAJ", traj)
    monkeypatch.setattr(arms, "BUNDLE_DIR", bundle_dir)
    _touch(traj, "B0-agent__05-8447_75.6__rep1.jsonl", lines=5)
    assert arms.bundle("B0-agent", 1) == 5


def test_D1_bundle_does_not_bleed_between_arms_or_reps(tmp_path, monkeypatch):
    """`B0__*` must not swallow `B0prime__*`, and rep1 must not swallow rep2."""
    traj, bundle_dir = tmp_path / "per-item", tmp_path / "bundles"
    monkeypatch.setattr(arms, "DEFAULT_TRAJ", traj)
    monkeypatch.setattr(arms, "BUNDLE_DIR", bundle_dir)
    _touch(traj, "B0__item__rep1.jsonl", lines=3)
    _touch(traj, "B0prime__item__rep1__s1.jsonl", lines=7)
    _touch(traj, "B0__item__rep2.jsonl", lines=9)
    assert arms.bundle("B0", 1) == 3, "B0 must not absorb B0prime or rep 2"
    assert arms.bundle("B0prime", 1) == 7
    assert arms.bundle("B0", 2) == 9


def test_D1_an_empty_bundle_is_still_possible_but_now_visible(tmp_path, monkeypatch):
    """Zero is a legitimate answer when there is genuinely nothing; the defect was that
    zero was returned when 246 files existed. Asserted so the fix is not read as
    'bundle can never return 0'."""
    traj, bundle_dir = tmp_path / "per-item", tmp_path / "bundles"
    traj.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(arms, "DEFAULT_TRAJ", traj)
    monkeypatch.setattr(arms, "BUNDLE_DIR", bundle_dir)
    assert arms.bundle("NOSUCHARM", 1) == 0


# ============================================================ D2 — the tie-break

@pytest.mark.parametrize("votes,expected,why", [
    ([FAIL, FAIL, FAIL], FAIL, "unanimous"),
    ([EXEC, EXEC, EXEC], EXEC, "unanimous"),
    ([FAIL, FAIL, EXEC], FAIL, "majority"),
    ([EXEC, EXEC, FAIL], EXEC, "majority"),
    ([FAIL, EXEC], FAIL, "TIE -> WILL_FAIL, the published conservative direction"),
    ([EXEC, FAIL], FAIL, "TIE -> WILL_FAIL, order must not matter"),
    ([FAIL, EXEC, ""], FAIL, "an unparseable vote is NOT a vote; the tie breaks to FAIL"),
    ([EXEC, EXEC, ""], EXEC, "the two real votes decide"),
    ([EXEC, "", ""], EXEC, "one real vote is still a majority of the real votes"),
    (["", "", ""], None, "no real votes -> NO PREDICTION -> score.py charges a failure"),
    ([], None, "no votes at all"),
    (["will_fail", " WILL_EXECUTE ", '"WILL_FAIL"'], FAIL,
     "case, whitespace and quotes are normalised; 2-1 to FAIL"),
    (["maybe?", "I cannot say", EXEC], EXEC, "prose is not a vote"),
])
def test_D2_tally_votes(votes, expected, why):
    assert arms.tally_votes(votes) == expected, why


def test_D2_a_total_non_answer_scores_as_a_FAILURE_end_to_end():
    """`GOOD.md` §1 — a non-answer is a FAILURE, never a skip — through the real scorer."""
    from score import score
    assert arms.tally_votes(["", "", ""]) is None
    res = score([{"item_id": "X", "label": FAIL}], {"X": arms.tally_votes(["", "", ""])})
    assert res["success"] == 0 and res["failure"] == 1
    assert res["success"] + res["failure"] == res["n"]


def test_D2_the_published_rule_is_still_what_the_code_does():
    """The docstring is deliverable-1 material. If the rule text and the behaviour ever
    part company, the published rule becomes a claim rather than a description."""
    doc = arms.run_b0prime.__doc__
    assert "tie resolves to `WILL_FAIL`" in doc
    assert "unparseable vote is\n    NOT a vote" in doc or "NOT a vote" in doc
    assert arms.tally_votes([FAIL, EXEC]) == FAIL
