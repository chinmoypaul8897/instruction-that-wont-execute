# docs/evidence/runs/ — the cost and time ledger

## `cost_ledger.csv` — the production ledger

**Absent until the first real run, and that is deliberate.** The USD 18.00 spend
ceiling in `src/runlog.py` is computed by summing this file, so seeding it with demo
rows would corrupt the number the ceiling is enforced against. It is created
automatically by the first `RunLogger` that finishes.

Append-only. Exactly the eight columns the CH-00 spec names:

```
run_id, arm, item_id, model, input_tokens, output_tokens, wall_clock_s, imputed_usd
```

This file is the source for the **cost per task** and **human time per task** rows
the rubric's results table asks for — rows that, at the time of writing, only two
repositories on GitHub carry at all.

### Reading it

```
python src/runlog.py                       # totals, unknown-cost count, headroom
RUNLOG_LEDGER=<path> python src/runlog.py  # any other ledger
```

### Two conventions that matter when you aggregate it

1. **An empty `imputed_usd` cell means UNKNOWN, never zero.** A run that died before
   `finish()` never reported token counts, so its cost is genuinely unknown. Encoding
   that as `0` would quietly understate the total. `cumulative_usd()` excludes those
   rows; `unknown_cost_runs()` counts them, and the ceiling message prints the count
   whenever it is non-zero. If you write your own aggregator, do the same.
2. **Every figure is IMPUTED at published list prices**, from the `PRICES` table in
   `src/runlog.py`, with `price_basis` and `price_basis_url` stamped into each run's
   `run_end` record. It is not a billing extract. Batch delivery is billed at 50% and
   the logger applies that; the flat-cost build subscription is imputed at full list
   and flagged `cost_is_imputed` rather than reported as `$0`.

## `ch00-demo/` — the CH-00 done-when artifact

A sandboxed dummy run, no model called, proving the logger emits a readable
trajectory **and** a cost row carrying input tokens, output tokens, wall-clock and
imputed USD.

- `trajectories/CH-00-demo.jsonl` — 10 records exercising every record type
- `cost_ledger.csv` — the single resulting row

Regenerate with `python docs/evidence/ch00_demo_run.py`; committed output is
`docs/evidence/ch00-demo-run.txt`. The clock and UTC stamp are injected, so the run
is **byte-reproducible** — re-running yields identical SHA-256 for both artifacts,
which is hard rule 9 demonstrated on the smallest possible case:

```
trajectory  5bf7089b5f89f2f198c634bde538b3b385f79809802d84be783e8c2cdc2d6997
ledger      35adf3c60ce6d165f7953558f571d61d3520334e0d5a82e592b127195fa0a428
```

This directory is **not** the production ledger and must never be summed into it.
