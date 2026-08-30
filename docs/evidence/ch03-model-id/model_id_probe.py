"""Q1's model id is an ASSERTION until something calls it. This calls it.

`prompts/NIGHT-RUN.md` pre-registers, as a fact not to be rediscovered, that the alias
`claude-haiku-4-5` "is not on this account and will 404". Hard rule 15 says a claim
from another document is a claim and not a fact, so this probe calls the alias FIRST
and prints whatever comes back.

**IT DOES NOT 404.** The alias answers 200. The pre-registered fact is wrong, and the
correction is recorded in `QUESTIONS.md` Q1 with this output as its evidence path. The
dated id is used anyway - see Q1 - because pinning a dated model is the right call for
a reproducibility claim, not because the alias is broken.

The probe also found the thing that would have broken the sensitivity arm at 3am:
**`claude-sonnet-5` returns HTTP 400 for `temperature`** ("deprecated for this model"),
while `claude-haiku-4-5*` accepts it. Both temperature variants are therefore probed
per model, and the resulting asymmetry - haiku arms at temperature 0, the sonnet subset
at the model default - is reported rather than hidden.

Every call goes through `RunLogger` (hard rule 10 - EVERY agent run is logged, from
the first one). A refused call still gets a ledger row, with an EMPTY cost cell,
because unknown is not the same claim as free.

    python docs/evidence/ch03-model-id/model_id_probe.py
    # committed output: docs/evidence/ch03-model-id/model-id-probe.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from apiclient import ApiError, call_messages, key_fingerprint, load_api_key  # noqa: E402
from runlog import RunLogger, UnknownModel  # noqa: E402

PROMPT = "Reply with exactly one word: ok"

# (model id, why it is here, temperature or None to omit the field)
CANDIDATES = [
    ("claude-haiku-4-5", "the ALIAS QUESTIONS.md Q1 names", 0.0),
    ("claude-haiku-4-5-20251001", "the DATED form prompts/NIGHT-RUN.md pre-registers", 0.0),
    ("claude-sonnet-5", "the model-sensitivity arm, temperature=0", 0.0),
    ("claude-sonnet-5", "the model-sensitivity arm, temperature OMITTED", None),
]


def main() -> int:
    key = load_api_key()
    print("ANTHROPIC_API_KEY :", key_fingerprint(key))
    print("(the key itself is never printed, logged or committed - hard rule 12)")
    print()

    results = []
    for model, why, temp in CANDIDATES:
        label = f"{model} @ temperature={temp!r}"
        print(f"--- {label}   ({why})")
        try:
            with RunLogger(arm="probe-model-id", item_id=f"{model}-t{temp}", model=model,
                           agent_instructions=PROMPT, delivery="standard",
                           est_usd="0.001",
                           traj_dir=REPO / "docs/trajectories/probe",
                           ledger_path=REPO / "docs/evidence/runs/cost_ledger.csv") as log:
                log.action("message", "messages.create", input={"prompt": PROMPT})
                try:
                    text, usage, attempts = call_messages(
                        key, model=model, user=PROMPT, max_tokens=16,
                        temperature=temp, max_attempts=2)
                except ApiError as exc:
                    # finish() is deliberately NOT called: RunLogger.__exit__ then
                    # writes a run_end with verdict ERROR and an EMPTY cost cell.
                    # A refused call is a logged run of unknown cost, never a free one.
                    log.tool_response("messages.create", error=str(exc))
                    log.feedback("the API refused this model id; recorded, not retried")
                    print(f"    REFUSED: {exc}")
                    results.append((label, "REFUSED", str(exc)[:120]))
                else:
                    log.tool_response("messages.create", output={"text": text})
                    for a in attempts:
                        if a["attempt"] > 1:
                            log.retry(reason=str(a["error"])[:200], attempt=a["attempt"])
                    usd = log.finish(verdict=text.strip()[:32],
                                     input_tokens=usage["input_tokens"],
                                     output_tokens=usage["output_tokens"])
                    print(f"    OK  reply={text.strip()!r}  "
                          f"in={usage['input_tokens']} out={usage['output_tokens']} "
                          f"usd={usd}")
                    results.append((label, "OK", text.strip()[:40]))
        except UnknownModel as exc:
            print(f"    NOT PRICED: {exc}")
            results.append((label, "NOT-PRICED", str(exc)[:120]))
        print()

    print("=" * 72)
    print("VERDICT")
    print("=" * 72)
    for model, status, detail in results:
        print(f"  {status:<11} {model:<44} {detail}")
    ok = {m for m, s, _ in results if s == "OK"}
    print()
    print(f"  working ids: {sorted(ok) or 'NONE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
