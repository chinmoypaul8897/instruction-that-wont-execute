# docs/progress/ — per-chunk session entries

Used only when sessions run **in parallel** (Phase 3, by architect instruction).
`STATUS.md` and `PROGRESS.md` are architect-merged, so a parallel build session
writes `docs/progress/<CHUNK-ID>.md` here instead of editing them directly and the
architect folds it in. Serial sessions write straight to `PROGRESS.md`.

Same template either way: scope · files · tests · decisions · questions · gate ·
status-ledger · state-for-next-session.
