# docs/trajectories/ — one JSONL per agent run

**Deliverable 4.** Written by `src/runlog.py`; nothing else may write here.

- `<run_id>.jsonl` — one *solution*-agent run (an evaluation arm). Empty until the
  CHECKPOINT, which is the first chunk that calls a model.
- `build/<CHUNK-ID>.jsonl` — one *coding*-agent session, captured by
  `tools/export_session.py`. See `build/README.md`.

Research/ideation agent trajectories are not here: they predate this repository and
ship as `context/*-raw.json`. All three classes are indexed in `AI-USE.md`.

The curation rule for the ≤50 MB submission zip is published in `AI-USE.md` **before**
selecting (`plan.md` CH-12) — the complete set ships in git, a representative set in
the zip, and every run whose verdict disagreed with gold is in the representative set.
