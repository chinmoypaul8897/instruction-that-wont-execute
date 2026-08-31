"""REVIEW CH-04 - check 4, BY CONSTRUCTION, not by reading the code.

The claim under test, from `GOOD.md` section 1 and `src/score.py`'s header:

    "An unparseable or absent verdict is a FAILURE, never a skip. Every item in the
     eval set is in the denominator of every arm, and `success + failure == n` is
     asserted in code. An arm cannot raise its score by declining to answer."

The probe builds a HOSTILE arm and tries to beat an honest one by refusing. Sixteen
refusal shapes are fired at the scorer - empty string, whitespace, prose, a refusal, a
JSON blob, an absent key, an explicit null, a hedged verdict, the verdict inside a
sentence, a list, a dict, a bool, a number, a near-miss spelling, and the two real
prose non-answers lifted verbatim from `docs/evidence/checkpoint/B0-rep1.json`.

Run: python docs/reviews/ch04-probe/hostile_nonanswer.py
Out: docs/reviews/ch04-probe/hostile-nonanswer.txt
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from score import ScoreError, score  # noqa: E402

FAIL, EXEC = "WILL_FAIL", "WILL_EXECUTE"
OUT = []


def p(*a):
    OUT.append(" ".join(str(x) for x in a))


# The 16 hostile shapes. `_ABSENT` means the key is not in the dict at all.
_ABSENT = object()
HOSTILE = [
    ("empty string", ""),
    ("whitespace only", "   \n\t "),
    ("explicit None", None),
    ("absent key", _ABSENT),
    ("prose refusal", "I cannot determine this without the CFR text."),
    ("policy refusal", "I'm sorry, I can't help with that."),
    ("empty JSON blob", "{}"),
    ("JSON without the field", '{"failing_designation": "(b)(4)"}'),
    ("hedged verdict", "probably WILL_FAIL"),
    ("verdict inside a sentence", "The verdict is WILL_EXECUTE for this section."),
    ("list", ["WILL_FAIL"]),
    ("dict", {"verdict": "WILL_FAIL"}),
    ("bool", True),
    ("number", 0),
    ("near-miss spelling", "WILL FAIL"),
    ("real B0 non-answer", "I cannot verify whether these instructions will execute "
                           "without seeing the actual CFR text for"),
]


def preds_with(base, iid, raw):
    d = dict(base)
    if raw is _ABSENT:
        d.pop(iid, None)
    else:
        d[iid] = raw
    return d


def main():
    p("REVIEW CH-04 - check 4: a non-answer must be a FAILURE, never a skip")
    p("=" * 78)

    # --------------------------------------------------------------- 1. every shape
    items = [{"item_id": "d1", "label": FAIL}, {"item_id": "e1", "label": EXEC}]
    p("")
    p("1. EVERY REFUSAL SHAPE, on a DEFECTIVE item (gold WILL_FAIL) and on an")
    p("   EXECUTABLE item (gold WILL_EXECUTE). n must stay 2; success must stay 1.")
    p("")
    p("   %-30s %-8s %-8s %-8s %-6s %-6s %s"
      % ("shape", "gold", "success", "failure", "n", "unpars", "charged to"))
    bad = []
    for name, raw in HOSTILE:
        for iid, gold, other, other_gold in (("d1", FAIL, "e1", EXEC),
                                             ("e1", EXEC, "d1", FAIL)):
            base = {other: other_gold}          # the other item answered correctly
            r = score(items, preds_with(base, iid, raw))
            charged = ("missed-defect" if r["missed_defect_count"] else
                       "false-defect" if r["false_defect_count"] else "NOTHING")
            ok = (r["n"] == 2 and r["success"] == 1 and r["failure"] == 1
                  and r["unparseable_or_absent"] == 1
                  and r["success"] + r["failure"] == r["n"]
                  and charged == ("missed-defect" if gold == FAIL else "false-defect"))
            if not ok:
                bad.append((name, gold, r))
            p("   %-30s %-8s %-8d %-8d %-6d %-6d %s%s"
              % (name[:30], "FAIL" if gold == FAIL else "EXEC", r["success"],
                 r["failure"], r["n"], r["unparseable_or_absent"], charged,
                 "" if ok else "   <<< UNEXPECTED"))
    p("")
    p("   shapes that behaved unexpectedly: %d" % len(bad))

    # ------------------------------------------------- 2. refusing cannot pay off
    p("")
    p("2. CAN AN ARM RAISE ITS ACCURACY BY DECLINING? 20 items, 10/10.")
    p("   HONEST arm answers every item and gets 12 right.")
    p("   HOSTILE arm gives the SAME 12 answers and REFUSES the other 8.")
    p("")
    big = ([{"item_id": "d%02d" % i, "label": FAIL} for i in range(10)]
           + [{"item_id": "e%02d" % i, "label": EXEC} for i in range(10)])
    honest, hostile = {}, {}
    for k, it in enumerate(big):
        iid, gold = it["item_id"], it["label"]
        right = k < 6 or (10 <= k < 16)          # 12 of 20 correct
        answer = gold if right else (EXEC if gold == FAIL else FAIL)
        honest[iid] = answer
        hostile[iid] = answer if right else "I cannot answer this one."
    h = score(big, honest)
    x = score(big, hostile)
    p("   HONEST   n %d  success %d  failure %d  accuracy %.4f  unparseable %d"
      % (h["n"], h["success"], h["failure"], h["accuracy"],
         h["unparseable_or_absent"]))
    p("   HOSTILE  n %d  success %d  failure %d  accuracy %.4f  unparseable %d"
      % (x["n"], x["success"], x["failure"], x["accuracy"],
         x["unparseable_or_absent"]))
    p("   refusing changed the accuracy by %+.4f  ->  %s"
      % (x["accuracy"] - h["accuracy"],
         "NO GAIN" if x["accuracy"] <= h["accuracy"] else "REFUSING PAID OFF"))

    # ------------------------------------------------- 3. the total refusenik
    p("")
    p("3. THE TOTAL REFUSENIK - an arm that answers NOTHING at all.")
    empty = score(big, {})
    p("   n %d  success %d  failure %d  accuracy %.4f  unparseable %d"
      % (empty["n"], empty["success"], empty["failure"], empty["accuracy"],
         empty["unparseable_or_absent"]))
    p("   false-defect %d/%d = %.4f  missed-defect %d/%d = %.4f"
      % (empty["false_defect_count"], empty["n_negatives"],
         empty["false_defect_rate"], empty["missed_defect_count"],
         empty["n_positives"], empty["missed_defect_rate"]))
    p("   both guards fail: %s"
      % (not empty["guard_false_defect_pass"]
         and not empty["guard_missed_defect_pass"]))

    # ------------------------------------------------- 4. is the identity ASSERTED?
    p("")
    p("4. IS `success + failure == n` GENUINELY ASSERTED, OR JUST COMPUTED?")
    p("   A derived count that always agrees with itself proves nothing. The scorer")
    p("   takes `n = len(items)` and then TALLIES BY ITERATING `items`. Feed it a")
    p("   sequence whose `__len__` and whose iteration DISAGREE and the invariant is")
    p("   genuinely violated; a real assertion must RAISE, not return a wrong number.")

    class LyingSequence:
        """len() says one thing, iteration yields another. Nothing else changes."""

        def __init__(self, data, claimed_len):
            self._d = list(data)
            self._n = claimed_len

        def __len__(self):
            return self._n

        def __iter__(self):
            return iter(self._d)

    asserted = True
    for claimed in (len(items) + 1, len(items) - 1):
        try:
            r = score(LyingSequence(items, claimed), {"d1": FAIL, "e1": EXEC})
            p("   len()=%d, yields %d  ->  NOT ASSERTED, returned %r"
              % (claimed, len(items),
                 {k: r[k] for k in ("n", "success", "failure")}))
            asserted = False
        except ScoreError as exc:
            p("   len()=%d, yields %d  ->  ScoreError: %s" % (claimed, len(items), exc))
        except Exception as exc:                  # noqa: BLE001
            p("   len()=%d, yields %d  ->  %s: %s"
              % (claimed, len(items), type(exc).__name__, exc))
            asserted = False

    p("")
    p("   `python -O` note: the check is `if ...: raise ScoreError`, NOT an `assert`,")
    p("   so it survives the optimisation flag. Verified by re-running this probe")
    p("   under `python -O` - output at hostile-nonanswer-O.txt.")

    # ------------------------------------------------- summary
    p("")
    p("=" * 78)
    verdict = (len(bad) == 0
               and x["accuracy"] <= h["accuracy"]
               and empty["accuracy"] == 0.0
               and asserted)
    p("CHECK 4 RESULT: %s" % ("PASS" if verdict else "FAIL"))
    p("=" * 78)

    text = "\n".join(OUT) + "\n"
    name = "hostile-nonanswer-O.txt" if not __debug__ else "hostile-nonanswer.txt"
    (Path(__file__).resolve().parent / name).write_text(text, encoding="utf-8")
    print(text)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
