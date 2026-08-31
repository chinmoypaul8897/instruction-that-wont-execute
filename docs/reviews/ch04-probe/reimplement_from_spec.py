"""REVIEW CH-04 - independent reimplementation of CONTEXT.md section 7.

Written by the adversarial reviewer from the SPEC PROSE ONLY. It imports nothing from
`src/`, copies no line from `src/score.py`, and uses no helper from the project. Even
the binomial coefficients are built here by a Pascal recurrence rather than taken from
`math.comb`, and the tail is summed in exact `Fraction` arithmetic, so a floating-point
agreement with the scorer is not an artefact of sharing a library call.

CONTEXT.md section 7, the only text this file implements:

  Primary - execution-prediction accuracy
    "Fraction of exact-instruction-count-matched (rule, section) items where the
     emitted `verdict` equals whether NARA published a live editorial note for that
     section."

  Guards - pre-registered numbers
    | False-defect rate (called WILL_FAIL on an executable section) | <= 0.25 |
    | Missed-defect rate                                            | <= 0.25 |
    | Attributor completeness                                       | >= 0.90 |

  Success  "A1 >= B0-agent + 8 pp, McNemar p < 0.05, at n >= 84, and A1 >= 0.80."

Section 7 names McNemar but does not name a variant; `src/score.py` uses the EXACT
two-sided binomial on the discordant pairs and `plan.md`'s branch table turns on that
p-value, so that is the test reimplemented here.

Usage:  python docs/reviews/ch04-probe/reimplement_from_spec.py
Output: docs/reviews/ch04-probe/reimplement-from-spec.txt
"""
from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVALSET = REPO / "data/evalset/items.jsonl"
CKPT = REPO / "docs/evidence/checkpoint"

FAIL, EXEC = "WILL_FAIL", "WILL_EXECUTE"


# ---------------------------------------------------------------- verdict extraction
def verdict_of(raw):
    """CONTEXT.md section 5's contract admits exactly two values. Anything else is not
    a verdict. Written independently of `score.normalise_verdict`."""
    if raw is None:
        return None
    s = str(raw).strip()
    for _ in range(4):
        stripped = s.strip('"').strip("'").strip()
        if stripped == s:
            break
        s = stripped
    s = s.upper()
    return s if s in (FAIL, EXEC) else None


# ---------------------------------------------------------------- (a) primary accuracy
def primary_accuracy(gold_by_id, preds):
    """Every item in the eval set is in the denominator. A non-answer is wrong."""
    n = len(gold_by_id)
    hits = 0
    for iid, gold in gold_by_id.items():
        if verdict_of(preds.get(iid)) == gold:
            hits += 1
    return {"n": n, "hits": hits, "misses": n - hits, "accuracy": hits / n}


# ---------------------------------------------------------------- (c) the guard rates
def guard_rates(gold_by_id, preds):
    """TWO readings of section 7, reported side by side because they differ.

    STRICT   - the parenthetical, verbatim: "called WILL_FAIL on an executable
               section". A non-answer is not a call of WILL_FAIL, so it is not in the
               numerator (it still counts against accuracy).
    CHARGED  - a non-answer is charged to the class it failed to get right. Stricter;
               this is what `src/score.py` does. Section 7 does not say it.
    """
    n_exec = sum(1 for g in gold_by_id.values() if g == EXEC)
    n_fail = sum(1 for g in gold_by_id.values() if g == FAIL)
    strict_fd = strict_md = charged_fd = charged_md = 0
    na_exec = na_fail = 0
    for iid, gold in gold_by_id.items():
        v = verdict_of(preds.get(iid))
        if gold == EXEC:
            if v == FAIL:
                strict_fd += 1
            if v is None:
                na_exec += 1
            if v != EXEC:
                charged_fd += 1
        else:
            if v == EXEC:
                strict_md += 1
            if v is None:
                na_fail += 1
            if v != FAIL:
                charged_md += 1
    return {
        "n_executable": n_exec, "n_defective": n_fail,
        "strict_false_defect_count": strict_fd,
        "strict_false_defect_rate": strict_fd / n_exec if n_exec else 0.0,
        "strict_missed_defect_count": strict_md,
        "strict_missed_defect_rate": strict_md / n_fail if n_fail else 0.0,
        "charged_false_defect_count": charged_fd,
        "charged_false_defect_rate": charged_fd / n_exec if n_exec else 0.0,
        "charged_missed_defect_count": charged_md,
        "charged_missed_defect_rate": charged_md / n_fail if n_fail else 0.0,
        "nonanswers_on_executable": na_exec,
        "nonanswers_on_defective": na_fail,
    }


# ---------------------------------------------------------------- (b) exact McNemar
def _pascal_row(n):
    """C(n, 0..n) by recurrence. Not math.comb - independence is the point."""
    row = [1]
    for _ in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row


def exact_two_sided_mcnemar(a_hits, b_hits):
    """Discordant pairs only; H0 says each discordant pair is a fair coin.

    Two-sided p by the "sum every outcome at most as likely as the observed one" rule,
    in exact Fractions. Under Binomial(nd, 1/2) the pmf is symmetric, so it also equals
    min(1, 2 * P(X <= min(b, c))); BOTH are computed and compared here, which checks
    the doubling convention `src/score.py` uses rather than copying it.
    """
    if len(a_hits) != len(b_hits):
        raise SystemExit("vectors of different length")
    b = sum(1 for x, y in zip(a_hits, b_hits) if x and not y)
    c = sum(1 for x, y in zip(a_hits, b_hits) if y and not x)
    nd = b + c
    if nd == 0:
        return {"b": b, "c": c, "nd": nd, "p_value": 1.0, "p_doubled": 1.0,
                "conventions_agree": True}
    row = _pascal_row(nd)
    denom = 2 ** nd
    obs = row[min(b, c)]
    p_all = sum(Fraction(row[k], denom) for k in range(nd + 1) if row[k] <= obs)
    p_dbl = min(Fraction(1),
                2 * sum(Fraction(row[k], denom) for k in range(min(b, c) + 1)))
    return {"b": b, "c": c, "nd": nd,
            "p_value": float(p_all), "p_doubled": float(p_dbl),
            "conventions_agree": p_all == p_dbl}


# ---------------------------------------------------------------- rep aggregation
def majority(reps_preds, ids, tie_to="FAILURE"):
    """NOT FIXED BY ANY BINDING DOCUMENT - see the review. Reproduced from
    analyse_checkpoint.py's stated rule so the numbers are comparable; alternatives are
    computed below to price the unwritten choice."""
    out = {}
    for iid in ids:
        votes = [v for v in (verdict_of(p.get(iid)) for p in reps_preds) if v is not None]
        if not votes:
            out[iid] = None
            continue
        c = Counter(votes).most_common()
        if len(c) > 1 and c[0][1] == c[1][1]:
            out[iid] = FAIL if tie_to == "FAILURE" else EXEC
        else:
            out[iid] = c[0][0]
    return out


def load(name):
    p = CKPT / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main():
    items = sorted((json.loads(l) for l in
                    EVALSET.read_text(encoding="utf-8").splitlines() if l.strip()),
                   key=lambda i: i["item_id"])
    gold = {i["item_id"]: i["label"] for i in items}
    ids = [i["item_id"] for i in items]
    out = []

    def p(*a):
        out.append(" ".join(str(x) for x in a))

    p("REVIEW CH-04 - independent reimplementation of CONTEXT.md section 7")
    p("=" * 78)
    p("eval set        data/evalset/items.jsonl")
    p("n               %d" % len(items))
    p("labels          %s" % dict(Counter(gold.values())))
    p("FR documents    %d" % len({i["frdoc"] for i in items}))
    p("")

    arms = {}
    gap = None
    mc = None
    for arm, files in (("B0", ["B0-rep1.json", "B0-rep2.json", "B0-rep3.json"]),
                       ("B0-agent", ["B0-agent-rep1.json", "B0-agent-rep2.json",
                                     "B0-agent-rep3.json"])):
        reps = [load(f) for f in files]
        if any(r is None for r in reps):
            p("%s: missing reps, skipped" % arm)
            continue
        preds = [r["predictions"] for r in reps]
        maj = majority(preds, ids)
        acc = primary_accuracy(gold, maj)
        rates = guard_rates(gold, maj)
        arms[arm] = {"maj": maj, "acc": acc, "rates": rates, "preds": preds}
        p("--- %s   (%d reps, majority, ties -> FAILURE)" % (arm, len(reps)))
        p("    accuracy          %.10f   hits %d  misses %d  n %d"
          % (acc["accuracy"], acc["hits"], acc["misses"], acc["n"]))
        p("    hits+misses==n    %s" % (acc["hits"] + acc["misses"] == acc["n"]))
        p("    per-rep accuracy  %s"
          % [round(primary_accuracy(gold, q)["accuracy"], 10) for q in preds])
        p("    STRICT  s7 false-defect   %d/%d = %.10f"
          % (rates["strict_false_defect_count"], rates["n_executable"],
             rates["strict_false_defect_rate"]))
        p("    STRICT  s7 missed-defect  %d/%d = %.10f"
          % (rates["strict_missed_defect_count"], rates["n_defective"],
             rates["strict_missed_defect_rate"]))
        p("    CHARGED score.py f-defect %d/%d = %.10f"
          % (rates["charged_false_defect_count"], rates["n_executable"],
             rates["charged_false_defect_rate"]))
        p("    CHARGED score.py m-defect %d/%d = %.10f"
          % (rates["charged_missed_defect_count"], rates["n_defective"],
             rates["charged_missed_defect_rate"]))
        p("    non-answers       on executable %d - on defective %d"
          % (rates["nonanswers_on_executable"], rates["nonanswers_on_defective"]))
        p("")

    if "B0" in arms and "B0-agent" in arms:
        a_hits = [verdict_of(arms["B0-agent"]["maj"].get(i)) == gold[i] for i in ids]
        b_hits = [verdict_of(arms["B0"]["maj"].get(i)) == gold[i] for i in ids]
        mc = exact_two_sided_mcnemar(a_hits, b_hits)
        gap = 100 * (arms["B0-agent"]["acc"]["accuracy"] - arms["B0"]["acc"]["accuracy"])
        p("--- McNemar, B0-agent vs B0 (exact, two-sided, Fractions)")
        p("    b (agent right, B0 wrong)  %d" % mc["b"])
        p("    c (agent wrong, B0 right)  %d" % mc["c"])
        p("    discordant                 %d" % mc["nd"])
        p("    p (sum-of-at-most-likely)  %r" % mc["p_value"])
        p("    p (doubled smaller tail)   %r" % mc["p_doubled"])
        p("    conventions agree exactly  %s" % mc["conventions_agree"])
        p("    gap                        %+.10f pp" % gap)
        p("")

        p("--- HOW MUCH IS THE UNWRITTEN REP-AGGREGATION RULE WORTH?")
        p("    (no binding document fixes it; these are the alternatives)")
        for name, fn in (
                ("majority, ties -> FAILURE", lambda ps: majority(ps, ids, "FAILURE")),
                ("majority, ties -> EXECUTE", lambda ps: majority(ps, ids, "EXECUTE")),
                ("rep 1 alone", lambda ps: ps[0]),
                ("rep 2 alone", lambda ps: ps[1]),
                ("rep 3 alone", lambda ps: ps[2])):
            ap, bp = fn(arms["B0-agent"]["preds"]), fn(arms["B0"]["preds"])
            a = primary_accuracy(gold, ap)["accuracy"]
            b = primary_accuracy(gold, bp)["accuracy"]
            m = exact_two_sided_mcnemar(
                [verdict_of(ap.get(i)) == gold[i] for i in ids],
                [verdict_of(bp.get(i)) == gold[i] for i in ids])
            p("    %-28s B0 %.4f  agent %.4f  gap %+.1f pp  p %.4f"
              % (name, b, a, 100 * (a - b), m["p_value"]))
        p("")

    shipped = json.loads((CKPT / "checkpoint-result.json").read_text(encoding="utf-8"))
    p("=" * 78)
    p("DIFF - my arithmetic vs docs/evidence/checkpoint/checkpoint-result.json")
    p("=" * 78)
    rows = []
    if "B0" in arms:
        rows += [("B0 accuracy", arms["B0"]["acc"]["accuracy"],
                  shipped["b0"]["accuracy"]),
                 ("B0 false-defect (charged)",
                  arms["B0"]["rates"]["charged_false_defect_rate"],
                  shipped["b0"]["false_defect_rate"]),
                 ("B0 missed-defect (charged)",
                  arms["B0"]["rates"]["charged_missed_defect_rate"],
                  shipped["b0"]["missed_defect_rate"]),
                 ("B0 unparseable", arms["B0"]["rates"]["nonanswers_on_executable"]
                  + arms["B0"]["rates"]["nonanswers_on_defective"],
                  shipped["b0"]["unparseable_or_absent"])]
    if "B0-agent" in arms:
        rows += [("B0-agent accuracy", arms["B0-agent"]["acc"]["accuracy"],
                  shipped["b0_agent"]["accuracy"]),
                 ("B0-agent false-defect (charged)",
                  arms["B0-agent"]["rates"]["charged_false_defect_rate"],
                  shipped["b0_agent"]["false_defect_rate"]),
                 ("B0-agent missed-defect (charged)",
                  arms["B0-agent"]["rates"]["charged_missed_defect_rate"],
                  shipped["b0_agent"]["missed_defect_rate"])]
    if gap is not None:
        rows += [("gap pp", gap, shipped["as_run"]["gap_pp"]),
                 ("McNemar b", mc["b"],
                  shipped["as_run"]["mcnemar"]["b_only_a_correct"]),
                 ("McNemar c", mc["c"],
                  shipped["as_run"]["mcnemar"]["c_only_b_correct"]),
                 ("McNemar p", mc["p_value"], shipped["as_run"]["mcnemar"]["p_value"])]
    worst = 0.0
    for name, mine, theirs in rows:
        d = abs(float(mine) - float(theirs))
        worst = max(worst, d)
        p("    %-34s mine %.12f  theirs %.12f  delta %.3e  %s"
          % (name, float(mine), float(theirs), d, "MATCH" if d == 0 else "DIFFER"))
    p("")
    p("    largest absolute disagreement: %.3e" % worst)
    p("    VERDICT: %s"
      % ("ALL NUMBERS REPRODUCE EXACTLY" if worst == 0 else "DISAGREEMENT"))
    p("")

    p("=" * 78)
    p("SPEC-READING DELTA - section 7's parenthetical vs src/score.py")
    p("=" * 78)
    for arm in arms:
        r = arms[arm]["rates"]
        p("    %-10s false-defect strict %.4f vs charged %.4f   "
          "missed-defect strict %.4f vs charged %.4f"
          % (arm, r["strict_false_defect_rate"], r["charged_false_defect_rate"],
             r["strict_missed_defect_rate"], r["charged_missed_defect_rate"]))
    p("")

    dest = Path(__file__).resolve().parent / "reimplement-from-spec.txt"
    text = "\n".join(out) + "\n"
    dest.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
