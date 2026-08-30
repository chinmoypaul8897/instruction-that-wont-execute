# docs/trajectories/build/ — coding-agent session transcripts

One file per BUILD or REVIEW session: `<CHUNK-ID>.jsonl`.

These are the **coding agents** — the Claude Code sessions that wrote this
repository. They contain deliverable 4's own checklist verbatim: the agent
instructions, every tool call, every tool response, every retry and every human
interruption.

They are **volatile**. They live outside the repository in `~/.claude/projects/`,
where Claude Code rotates and prunes session directories. Capturing them is the
difference between claiming agent use and evidencing it, which is why `CLAUDE.md`'s
end-of-session duty 6 makes a chunk **not done** until its transcript is exported.

    python tools/export_session.py CH-00

Scrubbed on the way in: absolute home paths → `~`, credential-shaped tokens,
`KEY=value` secrets, and the operator's contact details. Substitution counts are
printed, zeros included. Proof each scrubber actually fires (rather than matching
nothing and looking clean) is `docs/evidence/ch00-guard-probe.txt`, cases H–P.
