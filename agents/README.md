# agents/ — one file per evaluation arm

**Deliverable 1.** The exact instructions that shape each arm, one file each, so the
difference between arms is a diff rather than a description.

Empty at CH-00 by scope fence: *"Do NOT write ... any agent."* Populated from CH-05
onward. Planned arms (`CONTEXT.md` §4, `plan.md`):

| Arm | What it is |
|---|---|
| `B-script` | deterministic script, no model, with its permutation null |
| `B0` | model, instruction text only |
| `B0-agent` | model with the CFR text available |
| `A1` | full agent: `cfr_resolve` + `SKILL.md` + note-emission contract |
| ablations | A1 minus exactly one capability each, 1 rep, pre-registered in `GOOD.md` |

Every arm runs the **same model** (fairness — `CONTEXT.md` §4). An ablation that
differs from A1 in more than one capability is a defect the NUMBERS-ONLY review
catches by diffing these files.
