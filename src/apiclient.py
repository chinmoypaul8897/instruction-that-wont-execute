"""Minimal Anthropic Messages API client - stdlib only, and it never prints the key.

Why stdlib rather than the `anthropic` SDK: the SDK is not installed on this machine
and adding a third-party dependency at the CHECKPOINT would put an unpinned package
inside the clean-clone rehearsal (CH-14a) for the sake of one POST. The Messages API
is a single JSON POST; `urllib` does it.

SECRETS - hard rule 12. `load_api_key()` reads `.env` and returns the value to the
caller. It is never printed, never logged, never written to a trajectory, and the
only thing this module will report about it is its NAME and its length class. The
`RunLogger` records `agent_instructions`, not headers.

    from apiclient import load_api_key, call_messages
    key = load_api_key()
    text, usage = call_messages(key, model="claude-haiku-4-5-20251001",
                                system="...", user="...", max_tokens=512)

`usage` is the API's own `{"input_tokens": n, "output_tokens": m}` - the real counts,
not an estimate, which is what hard rule 10 asks the ledger to carry.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ENV = REPO / ".env"

# Dated model ids used by the evaluation arms. `QUESTIONS.md` Q1 named the alias
# `claude-haiku-4-5`; the alias is not on this account and 404s. See Q1's correction.
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5"


class ApiError(RuntimeError):
    """The API refused, and we do not pretend the call succeeded."""


def load_api_key(env_path: Path | str | None = None) -> str:
    """Read ANTHROPIC_API_KEY from the process environment or `.env`.

    Returns the key. Callers must not print it. Raises rather than returning an
    empty string, because an empty key produces a 401 that looks like a model
    problem rather than a configuration one.
    """
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    path = Path(env_path) if env_path else DEFAULT_ENV
    if not path.exists():
        raise ApiError(f"no ANTHROPIC_API_KEY in the environment and no {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "ANTHROPIC_API_KEY":
            key = value.strip().strip('"').strip("'")
            if key:
                return key
    raise ApiError(f"ANTHROPIC_API_KEY not found in {path}")


def key_fingerprint(key: str) -> str:
    """A safe description of a key for a log line: its length and nothing else.

    Deliberately NOT a hash prefix - a hash of a secret is still a secret-derived
    value in a public repository. Length alone distinguishes "absent" from "present"
    and reveals nothing.
    """
    return f"present(len={len(key)})"


def call_messages(
    key: str,
    model: str,
    user: str,
    system: str = "",
    max_tokens: int = 1024,
    temperature: float | None = 0.0,
    timeout: int = 180,
    max_attempts: int = 4,
    _sleep=time.sleep,
) -> tuple[str, dict, list[dict]]:
    """One Messages API call. Returns (text, usage, attempts).

    `attempts` is the retry trace: one dict per attempt with its status and error, so
    a retry is visible in the trajectory rather than being smoothed away. Retries are
    on 429 / 5xx / transport errors only; a 400 or a 404 is a real answer and is
    raised immediately - retrying a wrong model id four times just wastes the clock.
    """
    body = {
        "model": model,
        "max_tokens": int(max_tokens),
        "messages": [{"role": "user", "content": user}],
    }
    # MEASURED 2026-08-31, not assumed: `claude-sonnet-5` returns HTTP 400
    # "`temperature` is deprecated for this model." `claude-haiku-4-5*` accepts it.
    # Passing temperature=None omits the field, and the ASYMMETRY that creates -
    # the haiku arms sample at 0, the sonnet sensitivity subset at the model default
    # - is reported rather than hidden. Evidence: docs/evidence/ch03-model-id/.
    if temperature is not None:
        body["temperature"] = float(temperature)
    if system:
        body["system"] = system
    payload = json.dumps(body).encode("utf-8")

    attempts: list[dict] = []
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(
            API_URL,
            data=payload,
            headers={
                "x-api-key": key,
                "anthropic-version": API_VERSION,
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            obj = json.loads(raw.decode("utf-8"))
            text = "".join(
                blk.get("text", "") for blk in obj.get("content", [])
                if blk.get("type") == "text"
            )
            usage = obj.get("usage", {}) or {}
            attempts.append({"attempt": attempt, "status": 200, "error": None})
            return text, {
                "input_tokens": int(usage.get("input_tokens", 0)),
                "output_tokens": int(usage.get("output_tokens", 0)),
                "stop_reason": obj.get("stop_reason"),
            }, attempts
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            attempts.append({"attempt": attempt, "status": exc.code, "error": detail})
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt == max_attempts:
                raise ApiError(f"HTTP {exc.code} from the Messages API: {detail}") from None
            _sleep(2 ** attempt)
        except Exception as exc:                       # transport, timeout, JSON
            attempts.append({"attempt": attempt, "status": None, "error": repr(exc)[:400]})
            if attempt == max_attempts:
                raise ApiError(f"transport failure after {attempt} attempts: {exc!r}") from None
            _sleep(2 ** attempt)
    raise ApiError("unreachable")                      # pragma: no cover
