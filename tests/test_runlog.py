"""CH-00 - proof for src/runlog.py.

Every expected number in this file was hand-computed in
docs/evidence/ch00-goldens.md and committed BEFORE src/runlog.py existed
(hard rule 4). If you change a number here you are changing a golden --
hard rule 5 says you may not do that to make a red test green.
"""
import csv
import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from runlog import (  # noqa: E402
    PRICES,
    PRICE_BASIS,
    SPEND_CEILING_USD,
    RunLogger,
    SpendCeilingExceeded,
    UnknownModel,
    ZeroCostRun,
)

# ---------------------------------------------------------------- goldens
G1_USD = "1.679627"   # claude-haiku-4-5, 1_234_567 in / 89_012 out, standard
G2_USD = "0.450000"   # claude-haiku-4-5,   250_000 in /  40_000 out, standard
G3_USD = "1.000000"   # claude-haiku-4-5, 1_000_000 in / 200_000 out, BATCH
G4_USD = "3.359254"   # claude-sonnet-5,  1_234_567 in /  89_012 out, standard
G1_G2_CUMULATIVE = "2.129627"

LEDGER_COLUMNS = [
    "run_id", "arm", "item_id", "model",
    "input_tokens", "output_tokens", "wall_clock_s", "imputed_usd",
]


class FakeClock:
    """Deterministic monotonic clock so wall_clock_s is an exact golden."""

    def __init__(self, *ticks):
        self._ticks = list(ticks)
        self._last = self._ticks[-1] if self._ticks else 0.0

    def __call__(self):
        if self._ticks:
            self._last = self._ticks.pop(0)
        return self._last


@pytest.fixture
def sandbox(tmp_path):
    """A throwaway repo root -- the real ledger is never touched by the suite."""
    return {
        "traj_dir": tmp_path / "docs" / "trajectories",
        "ledger_path": tmp_path / "docs" / "evidence" / "runs" / "cost_ledger.csv",
    }


def make(sandbox, **kw):
    kw.setdefault("arm", "B0")
    kw.setdefault("item_id", "42-433.2")
    kw.setdefault("model", "claude-haiku-4-5")
    kw.setdefault("agent_instructions",
                  "Predict whether the OFR can execute each instruction.")
    return RunLogger(traj_dir=sandbox["traj_dir"],
                     ledger_path=sandbox["ledger_path"], **kw)


def full_dummy_run(sandbox, **kw):
    """Exercises EVERY record type the CH-00 spec names."""
    kw.setdefault("run_id", "G1")
    kw.setdefault("_clock", FakeClock(100.0, 112.5))
    with make(sandbox, **kw) as log:
        log.action("tool_call", name="cfr_resolve",
                   input={"designation": "(b)(4)(i)(A)"})
        log.tool_response(name="cfr_resolve", output={"level": "exact", "found": False})
        log.feedback("anchor not found at exact level; retrying whitespace-collapsed")
        log.retry(reason="exact match failed", attempt=2)
        log.action("message", name="assistant", input={"text": "no anchor at any level"})
        log.tool_response(name="cfr_resolve", output=None, error="anchor absent")
        log.human_checkpoint(reason="two candidate sections",
                             resolution="operator chose 433.2")
        log.finish(verdict="WILL_FAIL", input_tokens=1_234_567, output_tokens=89_012)
    return log


def records(log):
    lines = Path(log.trajectory_path).read_text(encoding="utf-8").splitlines()
    assert all(line.strip() for line in lines), "blank line in JSONL"
    return [json.loads(line) for line in lines]


def ledger_rows(sandbox):
    with open(sandbox["ledger_path"], newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------- shape of the JSONL
def test_jsonl_parses_one_object_per_line_in_order(sandbox):
    recs = records(full_dummy_run(sandbox))
    assert recs[0]["record"] == "run_start"
    assert recs[-1]["record"] == "run_end"
    assert [r["record"] for r in recs] == [
        "run_start", "action", "tool_response", "feedback", "retry",
        "action", "tool_response", "human_checkpoint", "run_end",
    ]


def test_every_record_type_in_the_spec_is_exercised(sandbox):
    seen = {r["record"] for r in records(full_dummy_run(sandbox))}
    assert seen == {
        "run_start", "action", "tool_response", "feedback",
        "retry", "human_checkpoint", "run_end",
    }


def test_step_numbers_strictly_increase(sandbox):
    steps = [r["step"] for r in records(full_dummy_run(sandbox)) if "step" in r]
    assert steps == sorted(steps) and len(set(steps)) == len(steps)


def test_run_start_carries_every_required_field(sandbox):
    start = records(full_dummy_run(sandbox))[0]
    for field in ("run_id", "arm", "item_id", "model",
                  "timestamp_utc", "agent_instructions"):
        assert field in start, field
        assert start[field] not in (None, ""), field
    assert start["timestamp_utc"].endswith("Z")


def test_run_end_carries_every_required_field(sandbox):
    end = records(full_dummy_run(sandbox))[-1]
    for field in ("verdict", "input_tokens", "output_tokens", "wall_clock_s",
                  "imputed_usd", "model", "price_basis"):
        assert field in end, field
    assert end["verdict"] == "WILL_FAIL"
    assert end["price_basis"] == PRICE_BASIS
    assert end["price_basis_url"].startswith("https://")


def test_feedback_record_names_what_changed_the_next_step(sandbox):
    fb = [r for r in records(full_dummy_run(sandbox)) if r["record"] == "feedback"][0]
    assert fb["what_changed_the_next_step"].startswith("anchor not found")


def test_tool_response_error_is_null_when_clean(sandbox):
    tr = [r for r in records(full_dummy_run(sandbox)) if r["record"] == "tool_response"]
    assert tr[0]["error"] is None
    assert tr[1]["error"] == "anchor absent"


# ------------------------------------------------------------------- money
def test_imputed_usd_matches_the_hand_computed_golden(sandbox):
    end = records(full_dummy_run(sandbox))[-1]
    assert end["imputed_usd"] == float(G1_USD)
    assert end["imputed_usd"] > 0


def test_wall_clock_is_measured_not_guessed(sandbox):
    end = records(full_dummy_run(sandbox))[-1]
    assert end["wall_clock_s"] == 12.5          # FakeClock 112.5 - 100.0


def test_model_id_selects_the_price_row(sandbox):
    log = full_dummy_run(sandbox, run_id="G4", model="claude-sonnet-5")
    assert records(log)[-1]["imputed_usd"] == float(G4_USD)


def test_batch_delivery_halves_the_bill(sandbox):
    with make(sandbox, run_id="G3", delivery="batch") as log:
        log.finish(verdict="WILL_EXECUTE", input_tokens=1_000_000, output_tokens=200_000)
    end = records(log)[-1]
    assert end["imputed_usd"] == float(G3_USD)
    assert end["delivery"] == "batch"


def test_price_table_matches_published_list_prices():
    assert PRICES["claude-haiku-4-5"] == (Decimal("1.00"), Decimal("5.00"))
    assert PRICES["claude-sonnet-5"] == (Decimal("2.00"), Decimal("10.00"))
    assert PRICES["claude-opus-5"] == (Decimal("5.00"), Decimal("25.00"))


def test_unknown_model_raises_rather_than_costing_nothing(sandbox):
    with pytest.raises(UnknownModel):
        with make(sandbox, run_id="unknown", model="gpt-does-not-exist") as log:
            log.finish(verdict="X", input_tokens=10, output_tokens=10)


def test_zero_token_finished_run_is_a_defect_not_a_free_run(sandbox):
    with pytest.raises(ZeroCostRun):
        with make(sandbox, run_id="zero") as log:
            log.finish(verdict="WILL_EXECUTE", input_tokens=0, output_tokens=0)


def test_aborted_run_records_null_cost_not_zero(sandbox):
    with pytest.raises(RuntimeError):
        with make(sandbox, run_id="boom") as log:
            log.action("tool_call", name="x", input={})
            raise RuntimeError("model call blew up")
    end = records(log)[-1]
    assert end["record"] == "run_end"
    assert end["verdict"] == "ERROR"
    assert end["imputed_usd"] is None, "unknown must not be encoded as free"
    assert end["cost_unknown_reason"]
    row = ledger_rows(sandbox)[-1]
    assert row["imputed_usd"] == ""      # empty cell, never 0


# ------------------------------------------------------------------ ledger
def test_ledger_row_matches_the_trajectory(sandbox):
    log = full_dummy_run(sandbox)
    end = records(log)[-1]
    rows = ledger_rows(sandbox)
    assert len(rows) == 1
    row = rows[0]
    assert list(row.keys()) == LEDGER_COLUMNS
    assert row["run_id"] == end["run_id"] == "G1"
    assert row["arm"] == "B0"
    assert row["item_id"] == "42-433.2"
    assert row["model"] == "claude-haiku-4-5"
    assert int(row["input_tokens"]) == end["input_tokens"] == 1_234_567
    assert int(row["output_tokens"]) == end["output_tokens"] == 89_012
    assert float(row["wall_clock_s"]) == end["wall_clock_s"]
    assert row["imputed_usd"] == G1_USD          # exact string, 6 dp


def test_second_run_appends_rather_than_overwrites(sandbox):
    full_dummy_run(sandbox)
    with make(sandbox, run_id="G2", _clock=FakeClock(0.0, 1.0)) as log2:
        log2.finish(verdict="WILL_EXECUTE", input_tokens=250_000, output_tokens=40_000)

    rows = ledger_rows(sandbox)
    assert [r["run_id"] for r in rows] == ["G1", "G2"], "second run must append"
    assert rows[1]["imputed_usd"] == G2_USD

    total = sum(Decimal(r["imputed_usd"]) for r in rows)
    assert str(total) == G1_G2_CUMULATIVE

    # two distinct trajectory files, the first untouched
    assert (sandbox["traj_dir"] / "G1.jsonl").exists()
    assert (sandbox["traj_dir"] / "G2.jsonl").exists()
    assert records(log2)[-1]["run_id"] == "G2"


def test_ledger_header_is_written_exactly_once(sandbox):
    full_dummy_run(sandbox)
    with make(sandbox, run_id="G2b") as log2:
        log2.finish(verdict="X", input_tokens=1, output_tokens=1)
    text = sandbox["ledger_path"].read_text(encoding="utf-8")
    assert text.count("run_id,arm,item_id") == 1


# ---------------------------------------------------------- spend ceiling
def test_ceiling_constant_is_below_the_operators_hard_limit():
    assert SPEND_CEILING_USD == Decimal("18.00") < Decimal("20.00")


def _seed_ledger_at(sandbox, usd):
    sandbox["ledger_path"].parent.mkdir(parents=True, exist_ok=True)
    with open(sandbox["ledger_path"], "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(LEDGER_COLUMNS)
        w.writerow(["prior", "B0", "seed", "claude-haiku-4-5", 1, 1, 1.0, usd])


def test_ceiling_refuses_before_the_run_starts(sandbox):
    _seed_ledger_at(sandbox, "17.990000")
    with pytest.raises(SpendCeilingExceeded) as exc:
        make(sandbox, run_id="over", est_usd="0.05").__enter__()
    msg = str(exc.value)
    assert "18.00" in msg and "17.99" in msg
    assert "0.010000" in msg, "must print the remaining headroom"
    # refused BEFORE the run started: no trajectory, no new ledger row
    assert not (sandbox["traj_dir"] / "over.jsonl").exists()
    assert len(ledger_rows(sandbox)) == 1


def test_ceiling_allows_a_run_inside_the_headroom(sandbox):
    _seed_ledger_at(sandbox, "17.990000")
    with make(sandbox, run_id="under", est_usd="0.005") as log:
        log.finish(verdict="WILL_EXECUTE", input_tokens=1000, output_tokens=100)
    assert Path(log.trajectory_path).exists()
    assert len(ledger_rows(sandbox)) == 2


def test_ceiling_reads_cumulative_from_the_committed_ledger(sandbox):
    _seed_ledger_at(sandbox, "5.000000")
    lg = make(sandbox, run_id="probe", est_usd="0.01")
    assert lg.cumulative_usd() == Decimal("5.000000")
