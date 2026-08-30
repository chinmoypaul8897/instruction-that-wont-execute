# CH-00 golden fixtures — hand-computed BEFORE `src/runlog.py` existed

Hard rule 4: *"Hand-compute expected outputs before writing the code. A test whose
expected value came from the code it tests proves nothing."*

This file was committed in its own commit, **before** the commit that adds
`src/runlog.py`. `git log --follow docs/evidence/ch00-goldens.md src/runlog.py`
shows the order; that ordering is the evidence, not this sentence.

Every number below was computed by hand from the published price table and is
asserted verbatim in `tests/test_runlog.py`. Nothing here was read off a program.

---

## Price basis

Anthropic published list prices, per **1,000,000** tokens.
Source: <https://docs.claude.com/en/docs/about-claude/pricing> (HTTP 200, checked
2026-08-30). Recorded in every `run_end` record as `price_basis` +
`price_basis_url`, per the CH-00 spec.

| Model id | Input $/MTok | Output $/MTok |
|---|---|---|
| `claude-haiku-4-5` | 1.00 | 5.00 |
| `claude-sonnet-5` | 2.00 | 10.00 |
| `claude-opus-5` | 5.00 | 25.00 |

**Message Batches API = 50 % of list**, both directions. `QUESTIONS.md` Q1 mandates
batch delivery for the eval matrix.

**Independent check of Q1's own arithmetic** (hard rule 15 — a number in a ruling is
a claim until checked): Q1 states the full matrix is 11.8 M input / 1.26 M output on
`claude-haiku-4-5` and costs **$18.14** standard, **$9.07** batched.

    11.8  x 1.00 = 11.80
     1.26 x 5.00 =  6.30
                   -----
                   18.10  standard      ->  9.05 batched

$18.10 against Q1's $18.14 — agreement to 0.2 %, the residue being Q1's exact token
counts versus these rounded millions. **Q1's figure is confirmed, not merely
repeated.** The USD 18.00 ceiling therefore sits just below the full standard-price
matrix and roughly 2x the batched matrix, which is the intended headroom.

---

## The arithmetic

    imputed_usd = (input_tokens  / 1e6) * price_in
                + (output_tokens / 1e6) * price_out
                * (0.5 if delivery == "batch" else 1.0)   <- applied to the whole sum

Computed in `decimal.Decimal`, never binary float, then quantised to **6 decimal
places, ROUND_HALF_UP**. Money in float is a defect, not a style preference.

### G1 — primary dummy run · `claude-haiku-4-5` · standard

    input_tokens  = 1_234_567
    output_tokens =    89_012

    input   1_234_567 / 1e6            = 1.234567
            1.234567 x 1.00            = 1.234567
    output     89_012 x 5              =   445_060
              445_060 / 1e6            = 0.445060
    total   1.234567 + 0.445060        = 1.679627

**G1 imputed_usd = 1.679627**

Chosen so that plausible bugs are *not* fixed points:
swapped prices -> 6.261847 · per-1K instead of per-1M -> 1679.627 · output ignored ->
1.234567. None of these equals 1.679627.

### G2 — second run, appended · `claude-haiku-4-5` · standard

    input_tokens  = 250_000  ->  0.250000 x 1.00 = 0.250000
    output_tokens =  40_000  ->  40_000 x 5 = 200_000 / 1e6 = 0.200000
    total                                             = 0.450000

**G2 imputed_usd = 0.450000**
**Cumulative after G1 + G2 = 1.679627 + 0.450000 = 2.129627**

### G3 — batch delivery halves the bill · `claude-haiku-4-5` · batch

    input_tokens  = 1_000_000 -> 1.000000
    output_tokens =   200_000 -> 1.000000
    full                                  = 2.000000
    batch   2.000000 x 0.5                = 1.000000

**G3 imputed_usd = 1.000000**

### G4 — the model id must actually select the price row · `claude-sonnet-5` · standard

Same token counts as G1, different model. If `PRICES` were ignored, G4 would equal G1.

    input   1.234567 x  2.00 = 2.469134
    output  0.089012 x 10.00 = 0.890120
    total                    = 3.359254

**G4 imputed_usd = 3.359254**

### G5 — the hard spend ceiling

`SPEND_CEILING_USD = 18.00`. The operator's hard limit is USD 20 (Q1); the code stops
at 18 so a surprise cannot reach it.

Ledger seeded with one prior run at **17.990000**.

    est 0.050000 -> projected 18.040000 > 18.00  -> REFUSE, headroom 0.010000
    est 0.005000 -> projected 17.995000 <= 18.00 -> ALLOW

**Refusal is raised at `__enter__`, before the run starts.** A budget discovered
after it is spent is not a budget.

---

## Non-numeric goldens

- `docs/trajectories/<run_id>.jsonl` — one JSON object per line, no blank lines,
  `run_start` first, `run_end` last, `step` strictly increasing over the records
  that carry one.
- `run_start` carries: `run_id · arm · item_id · model · timestamp_utc ·
  agent_instructions`.
- `run_end` carries: `verdict · input_tokens · output_tokens · wall_clock_s ·
  imputed_usd · model · price_basis`.
- `docs/evidence/runs/cost_ledger.csv` — header once, then exactly the 8 columns the
  CH-00 spec names, append-only, one row per run, in run order.
- A finished run reporting `0` input **and** `0` output tokens is a defect, not a
  free run: the logger raises. *"Never emit $0."* A run that dies before `finish()`
  records `imputed_usd = null` with a stated reason — **null, not zero**, because
  "unknown" and "free" are different claims.
