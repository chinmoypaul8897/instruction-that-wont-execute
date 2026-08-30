# STATUS.md — where every chunk stands

One line per chunk. States: `todo` · `built` · `reviewed-PASS` · `reviewed-FAIL`.
Seeded from `plan.md`. **Architect-merged** when sessions run in parallel — a build
session in Phase 3 writes `docs/progress/<CHUNK-ID>.md` instead of editing this file.

`built` is not `done`. A gated chunk is done only at `reviewed-PASS`, awarded by a
fresh session with zero shared context (hard rule 2).

---

## Phase 1 — foundation and the go/no-go

| Chunk | Gate | State | One line |
|---|---|---|---|
| CH-00 · repo, canonical files, run logger | none | **built** | repo initialised private; 53 tracked of a 430 MB / 7,460-file tree; `src/runlog.py` + ledger + USD 18 ceiling; suite 22 green; guard probe 16/16 |
| CH-01 · govinfo EDNOTE harvest | none | **built** | 49 titles / 824 MB → 2,428 EDNOTEs → 107 defect → 86 section-level → **85 with an FR citation**; pool gate ≥ 60 **CLEARS** at 1.42×; the 9-title reference 903 / 44 / 44-of-44 reproduces **exactly**; suite 61 green |
| CH-02 · AMDPAR carry-forward attributor | **FULL** | **built** | 85/85 citations → 70 FR documents / 8,752 AMDPARs; completeness **0.5080** spec-literal · **0.6643** extended — **below 0.80: the pre-registered documented-failure branch, reported not tuned**; attribution 0.9865; **pair yield 0.6000 → 51 pairs against the 42 target, CLEARS at 1.21×**; suite 121 green; goldens committed before the parser (`98f1cff`) |
| CH-03 · point-in-time text + eval set | **FULL** + mutation | todo | ≥ 42 pairs, exact instruction-count match, leakage-strip test |
| CH-04 · scorer + `GOOD.md` | **FULL** + mutation | todo | `GOOD.md` committed before any model arm runs |
| ★ CHECKPOINT · B-script / B0 / B0-agent × 3 | numbers-only | todo | GREEN / AMBER / RED per `plan.md`; first chunk needing model access |

## Phase 2 — the agent · on GREEN or AMBER

| Chunk | Gate | State | One line |
|---|---|---|---|
| CH-05 · `cfr_resolve` tool | code-only | todo | three declared normalisation levels, level reported never applied silently |
| CH-06 · `SKILL.md` + note-emission contract | **CODE-ONLY** | todo | measures the tool-availability-vs-tool-use gap |
| CH-07 · ordered-state ledger | — | **not built** | pre-declared counted removal #3 (ruling R-01); its card ships, its code does not |
| CH-08 · ablations and final arms | none | todo | McNemar; bootstrap clustered by FR document |
| CH-09 · removed experiments + hot take | none | todo | leakage probe, collision detector, blind human-time study |

## Phase 3 — packaging · opens 2026-08-31 06:00 UTC · run in THIS order

| # | Chunk | State | One line |
|---|---|---|---|
| 1 | CH-14a · early rehearsal | todo | fresh venv, network off, manifest verify, Tier-1 replay |
| 2 | CH-13 · video | todo | **must complete by 10:00 UTC (T−8h)** — YouTube processing |
| 3 | CH-12 · trajectories + `AI-USE.md` | todo | publish the selection rule before selecting |
| 4 | CH-11 · README + `REPRODUCE.md` + `THIRD-PARTY.md` + `LICENSE` | todo | |
| 5 | CH-11b · **VOICE PASS** | todo | operator only, no session |
| 6 | CH-10 · worksheet + disclaimer band | todo | opens from a clean clone, network off |
| 7 | DRAFT-1 · **12:00 UTC wall-clock** | todo | all four fields saved as a draft; from here the project is insured |
| 8 | CH-14b · final rehearsal + full-history secret scan | todo | |
| 9 | CH-15 · **SUBMIT · 15:00 UTC** | todo | repo public and 200 to an unauthenticated request |

---

**Repository:** `chinmoypaul8897/instruction-that-wont-execute` — **private** until
CH-15. Anonymous `curl` returns 404, verified at CH-00.
