"""Run logger - every agent invocation in this project goes through here.

Hard rule 10: EVERY AGENT RUN IS LOGGED. No exceptions, from the first run.
Trajectory + input tokens + output tokens + wall-clock + imputed USD.
Retrofitting is impossible and it is a submission gate item.

Two artifacts per run:

  docs/trajectories/<run_id>.jsonl     one JSON object per line, the full trace
  docs/evidence/runs/cost_ledger.csv   one appended row, the money and the clock

Usage::

    with RunLogger(arm="B0", item_id="42-433.2", model="claude-haiku-4-5",
                   agent_instructions=SYSTEM_PROMPT) as log:
        log.action("tool_call", name="cfr_resolve", input={...})
        log.tool_response(name="cfr_resolve", output={...})
        log.feedback("anchor not found at exact level; retrying whitespace-collapsed")
        log.retry(reason="exact match failed", attempt=2)
        log.human_checkpoint(reason="...", resolution="...")
        log.finish(verdict="WILL_FAIL", input_tokens=..., output_tokens=...)

Wall-clock and imputed_usd are computed here, never passed in.

On purity (hard rule 8): the *scorer* and *resolver* must be clock-free and
network-free. This module is neither -- measuring wall-clock is its job. It
still makes no network call and no random choice, and both the clock and the
UTC stamp are injectable so the suite asserts exact values rather than ranges.

Money is Decimal end to end. Binary float for currency is a defect, not a
style preference.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# --------------------------------------------------------------------------
# Prices
# --------------------------------------------------------------------------
# Anthropic published list prices, USD per 1,000,000 tokens: (input, output).
# Checked against the published table on 2026-08-30. The basis and its source
# URL are recorded in every run_end record, because a cost figure without its
# price basis is not a measurement.
PRICE_BASIS = "anthropic-published-list-2026-08-30"
PRICE_BASIS_URL = "https://docs.claude.com/en/docs/about-claude/pricing"

PRICES: dict[str, tuple[Decimal, Decimal]] = {
    "claude-fable-5":    (Decimal("10.00"), Decimal("50.00")),
    "claude-opus-5":     (Decimal("5.00"),  Decimal("25.00")),
    "claude-opus-4-8":   (Decimal("5.00"),  Decimal("25.00")),
    "claude-opus-4-7":   (Decimal("5.00"),  Decimal("25.00")),
    "claude-opus-4-6":   (Decimal("5.00"),  Decimal("25.00")),
    "claude-sonnet-5":   (Decimal("2.00"),  Decimal("10.00")),
    "claude-sonnet-4-6": (Decimal("3.00"),  Decimal("15.00")),
    "claude-haiku-4-5":  (Decimal("1.00"),  Decimal("5.00")),
}

# Message Batches API bills at 50% of list, both directions (QUESTIONS.md Q1
# mandates batch delivery for the eval matrix). "subscription" is the coding
# agent: flat-cost to us, so we IMPUTE at full list price and say so in the
# record rather than emitting a dishonest $0.
DELIVERY_MULTIPLIER: dict[str, Decimal] = {
    "standard":     Decimal("1"),
    "batch":        Decimal("0.5"),
    "subscription": Decimal("1"),
}

USD = Decimal("0.000001")          # ledger and records carry 6 decimal places

# --------------------------------------------------------------------------
# Spend ceiling
# --------------------------------------------------------------------------
# The operator's hard limit is USD 20 (QUESTIONS.md Q1). The code stops at 18
# so a surprise cannot reach it. A budget discovered after it is spent is not
# a budget.
SPEND_CEILING_USD = Decimal("18.00")

# Projected cost of a run, used at __enter__ before any token count exists.
# Basis: Q1's measured matrix is ~2,520 calls for ~$18.10 at standard price,
# i.e. ~$0.0072 per call. 0.05 is ~7x that -- deliberately conservative, and
# overridable per run via est_usd=.
DEFAULT_RUN_ESTIMATE_USD = Decimal("0.05")

DEFAULT_TRAJ_DIR = Path("docs/trajectories")
DEFAULT_LEDGER_PATH = Path("docs/evidence/runs/cost_ledger.csv")

LEDGER_COLUMNS = [
    "run_id", "arm", "item_id", "model",
    "input_tokens", "output_tokens", "wall_clock_s", "imputed_usd",
]

SCHEMA_VERSION = 1

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


class RunLogError(Exception):
    """Base for every logger refusal."""


class UnknownModel(RunLogError):
    """Model id is not in PRICES. We refuse rather than cost it at zero."""


class ZeroCostRun(RunLogError):
    """A finished run reported no tokens at all. That is a defect, not a free run."""


class SpendCeilingExceeded(RunLogError):
    """Starting this run would push cumulative imputed spend past the ceiling."""


def compute_usd(model: str, input_tokens: int, output_tokens: int,
                delivery: str = "standard") -> Decimal:
    """Imputed USD at published list prices, quantised to 6 dp, ROUND_HALF_UP.

    Pure: no clock, no network, no state. Hand-computed goldens for this
    function live in docs/evidence/ch00-goldens.md.
    """
    if model not in PRICES:
        raise UnknownModel(
            f"no published price for model {model!r}; refusing to impute it at $0. "
            f"Known models: {', '.join(sorted(PRICES))}"
        )
    if delivery not in DELIVERY_MULTIPLIER:
        raise RunLogError(
            f"unknown delivery {delivery!r}; expected one of "
            f"{', '.join(sorted(DELIVERY_MULTIPLIER))}"
        )
    price_in, price_out = PRICES[model]
    per_million = Decimal(1_000_000)
    total = (Decimal(int(input_tokens)) / per_million) * price_in
    total += (Decimal(int(output_tokens)) / per_million) * price_out
    total *= DELIVERY_MULTIPLIER[delivery]
    return total.quantize(USD, rounding=ROUND_HALF_UP)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class RunLogger:
    """One instance per agent run. Use as a context manager."""

    def __init__(
        self,
        arm: str,
        item_id: str,
        model: str,
        agent_instructions: str = "",
        delivery: str = "standard",
        run_id: str | None = None,
        est_usd: Decimal | str | float | None = None,
        traj_dir: Path | str | None = None,
        ledger_path: Path | str | None = None,
        _clock=time.monotonic,
        _utc=_utcnow,
    ) -> None:
        if model not in PRICES:
            # Fail at construction: a run we cannot cost must never start.
            raise UnknownModel(
                f"no published price for model {model!r}; refusing to impute it at $0. "
                f"Known models: {', '.join(sorted(PRICES))}"
            )
        if delivery not in DELIVERY_MULTIPLIER:
            raise RunLogError(f"unknown delivery {delivery!r}")

        self.arm = arm
        self.item_id = item_id
        self.model = model
        self.agent_instructions = agent_instructions
        self.delivery = delivery
        self.est_usd = (DEFAULT_RUN_ESTIMATE_USD if est_usd is None
                        else Decimal(str(est_usd)))

        self.traj_dir = Path(traj_dir) if traj_dir else DEFAULT_TRAJ_DIR
        self.ledger_path = Path(ledger_path) if ledger_path else DEFAULT_LEDGER_PATH

        self._clock = _clock
        self._utc = _utc
        self.run_id = run_id or self._mint_run_id()
        self.trajectory_path = self.traj_dir / f"{self.run_id}.jsonl"

        self._fh = None
        self._step = 0
        self._started = None
        self._finished = False
        self._closed = False

    # ---------------------------------------------------------------- setup
    def _mint_run_id(self) -> str:
        stamp = self._utc().strftime("%Y%m%dT%H%M%S")
        base = f"{_UNSAFE.sub('_', self.arm)}__{_UNSAFE.sub('_', self.item_id)}__{stamp}"
        candidate, n = base, 1
        while (self.traj_dir / f"{candidate}.jsonl").exists():
            n += 1
            candidate = f"{base}__{n:03d}"
        return candidate

    # --------------------------------------------------------------- ledger
    def read_ledger(self) -> list[dict]:
        if not self.ledger_path.exists():
            return []
        with open(self.ledger_path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def cumulative_usd(self) -> Decimal:
        """Total imputed spend already committed to the ledger.

        Rows whose cost is unknown (an aborted run) carry an EMPTY cell, never
        a zero. They contribute nothing to the total and are counted separately
        by unknown_cost_runs() so "unknown" can never masquerade as "free".
        """
        total = Decimal("0.000000")
        for row in self.read_ledger():
            cell = (row.get("imputed_usd") or "").strip()
            if cell:
                total += Decimal(cell)
        return total

    def unknown_cost_runs(self) -> int:
        return sum(1 for r in self.read_ledger()
                   if not (r.get("imputed_usd") or "").strip())

    def _ledger_dump(self) -> str:
        rows = self.read_ledger()
        if not rows:
            return "    (ledger is empty)"
        out = []
        for r in rows:
            out.append("    {:<28} {:<10} {:>12} {:>10}".format(
                r.get("run_id", "?")[:28], r.get("arm", "?"),
                r.get("model", "?")[:12], r.get("imputed_usd", "") or "UNKNOWN"))
        return "\n".join(out)

    def _check_ceiling(self) -> None:
        spent = self.cumulative_usd()
        projected = spent + self.est_usd
        if projected > SPEND_CEILING_USD:
            headroom = SPEND_CEILING_USD - spent
            unknown = self.unknown_cost_runs()
            msg = (
                "SPEND CEILING REACHED - run refused before it started.\n"
                f"  ceiling            USD {SPEND_CEILING_USD}\n"
                f"  already committed  USD {spent}\n"
                f"  this run estimated USD {self.est_usd}\n"
                f"  projected total    USD {projected}\n"
                f"  remaining headroom USD {headroom}\n"
                + (f"  runs of UNKNOWN cost in the ledger: {unknown}\n" if unknown else "")
                + "  ledger:\n" + self._ledger_dump() + "\n"
                "A budget discovered after it is spent is not a budget."
            )
            print(msg, file=sys.stderr)
            raise SpendCeilingExceeded(msg)

    # -------------------------------------------------------------- context
    def __enter__(self) -> "RunLogger":
        self._check_ceiling()           # before anything is created or spent
        self.traj_dir.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.trajectory_path, "w", encoding="utf-8", newline="\n")
        self._started = self._clock()
        self._emit({
            "record": "run_start",
            "schema_version": SCHEMA_VERSION,
            "run_id": self.run_id,
            "arm": self.arm,
            "item_id": self.item_id,
            "model": self.model,
            "timestamp_utc": _stamp(self._utc()),
            "agent_instructions": self.agent_instructions,
            "delivery": self.delivery,
            "price_basis": PRICE_BASIS,
            "price_basis_url": PRICE_BASIS_URL,
        })
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if not self._finished and not self._closed:
            # Hard rule 10 has no exception for a run that blew up. Record it,
            # with cost NULL -- unknown is not the same claim as free.
            reason = (f"run aborted before finish(): "
                      f"{exc_type.__name__ if exc_type else 'no finish() call'}")
            self._write_end(verdict="ERROR", input_tokens=None, output_tokens=None,
                            imputed=None, cost_unknown_reason=reason)
        if self._fh:
            self._fh.close()
            self._fh = None
        return False                    # never swallow the exception

    # --------------------------------------------------------------- emit
    def _emit(self, obj: dict) -> None:
        if self._fh is None:
            raise RunLogError("RunLogger used outside its `with` block")
        self._fh.write(json.dumps(obj, ensure_ascii=False, sort_keys=False) + "\n")
        self._fh.flush()                # a crash must still leave a readable trace

    def _next_step(self) -> int:
        self._step += 1
        return self._step

    # -------------------------------------------------------- record types
    def action(self, type: str, name: str, input=None) -> None:
        """type is 'tool_call' or 'message'."""
        if type not in ("tool_call", "message"):
            raise RunLogError(f"action type must be 'tool_call' or 'message', got {type!r}")
        self._emit({"record": "action", "step": self._next_step(),
                    "type": type, "name": name, "input": input})

    def tool_response(self, name: str, output=None, error=None) -> None:
        self._emit({"record": "tool_response", "step": self._next_step(),
                    "name": name, "output": output, "error": error})

    def feedback(self, what_changed_the_next_step: str) -> None:
        """The observation that shaped what came next."""
        self._emit({"record": "feedback", "step": self._next_step(),
                    "what_changed_the_next_step": what_changed_the_next_step})

    def retry(self, reason: str, attempt: int) -> None:
        self._emit({"record": "retry", "step": self._next_step(),
                    "reason": reason, "attempt": int(attempt)})

    def human_checkpoint(self, reason: str, resolution: str) -> None:
        self._emit({"record": "human_checkpoint", "step": self._next_step(),
                    "reason": reason, "resolution": resolution})

    # --------------------------------------------------------------- finish
    def finish(self, verdict: str, input_tokens: int, output_tokens: int) -> Decimal:
        if self._finished:
            raise RunLogError(f"finish() already called for run {self.run_id}")
        if int(input_tokens) < 0 or int(output_tokens) < 0:
            raise RunLogError("token counts cannot be negative")
        if int(input_tokens) == 0 and int(output_tokens) == 0:
            # "Never emit $0." A completed model call always consumes input
            # tokens; zero here means the caller never wired the usage figures
            # through, and a silent $0 would corrupt every cost-per-task number
            # downstream.
            raise ZeroCostRun(
                f"run {self.run_id} finished reporting 0 input and 0 output tokens. "
                "That is a wiring defect, not a free run -- pass the real usage "
                "counts from the API response."
            )
        usd = compute_usd(self.model, input_tokens, output_tokens, self.delivery)
        self._write_end(verdict=verdict, input_tokens=int(input_tokens),
                        output_tokens=int(output_tokens), imputed=usd,
                        cost_unknown_reason=None)
        return usd

    def _write_end(self, verdict, input_tokens, output_tokens, imputed,
                   cost_unknown_reason) -> None:
        wall = round(self._clock() - (self._started if self._started is not None
                                      else self._clock()), 3)
        self._emit({
            "record": "run_end",
            "run_id": self.run_id,
            "arm": self.arm,
            "item_id": self.item_id,
            "verdict": verdict,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "wall_clock_s": wall,
            "imputed_usd": (float(imputed) if imputed is not None else None),
            "imputed_usd_exact": (str(imputed) if imputed is not None else None),
            "model": self.model,
            "delivery": self.delivery,
            "price_basis": PRICE_BASIS,
            "price_basis_url": PRICE_BASIS_URL,
            "cost_is_imputed": True,
            "cost_unknown_reason": cost_unknown_reason,
            "timestamp_utc": _stamp(self._utc()),
        })
        self._append_ledger(input_tokens, output_tokens, wall, imputed)
        self._finished = True
        self._closed = True
        if imputed is not None:
            after = self.cumulative_usd()
            if after > SPEND_CEILING_USD:
                print(f"WARNING: cumulative imputed spend USD {after} has crossed the "
                      f"ceiling USD {SPEND_CEILING_USD}. The next run will be refused.",
                      file=sys.stderr)

    def _append_ledger(self, input_tokens, output_tokens, wall, imputed) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        fresh = not self.ledger_path.exists() or self.ledger_path.stat().st_size == 0
        with open(self.ledger_path, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")   # LF on every platform
            if fresh:
                w.writerow(LEDGER_COLUMNS)
            w.writerow([
                self.run_id, self.arm, self.item_id, self.model,
                "" if input_tokens is None else input_tokens,
                "" if output_tokens is None else output_tokens,
                wall,
                "" if imputed is None else str(imputed),   # EMPTY, never 0
            ])


def ledger_total(ledger_path: Path | str = DEFAULT_LEDGER_PATH) -> tuple[Decimal, int, int]:
    """(total_usd, n_rows, n_unknown_cost) for the committed ledger."""
    path = Path(ledger_path)
    if not path.exists():
        return Decimal("0.000000"), 0, 0
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    total = Decimal("0.000000")
    unknown = 0
    for r in rows:
        cell = (r.get("imputed_usd") or "").strip()
        if cell:
            total += Decimal(cell)
        else:
            unknown += 1
    return total, len(rows), unknown


if __name__ == "__main__":
    total, n, unknown = ledger_total(
        os.environ.get("RUNLOG_LEDGER", DEFAULT_LEDGER_PATH))
    print(f"runs        : {n}")
    print(f"unknown cost: {unknown}")
    print(f"imputed USD : {total}")
    print(f"ceiling     : {SPEND_CEILING_USD}   headroom: {SPEND_CEILING_USD - total}")
