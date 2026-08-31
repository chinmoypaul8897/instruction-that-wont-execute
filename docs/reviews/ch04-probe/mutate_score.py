"""REVIEW CH-04 - check 3, mutation testing of `src/score.py`.

A green suite is not evidence of correctness. This introduces semantic mutations ONE
AT A TIME, runs the WHOLE suite against each, and records whether the suite noticed.
A mutation the suite does not catch is a finding.

Safety, because `src/` must not be modified permanently:
  * the original bytes and their SHA-256 are captured before anything happens;
  * every mutation is applied, VERIFIED to have landed (new text present AND old text
    gone - hard rule 16), tested, and then restored from the captured bytes;
  * the restore is verified by SHA-256 after every single mutation, in a `finally`;
  * the run ends with `git diff --exit-code src/score.py`.

Run: python docs/reviews/ch04-probe/mutate_score.py
Out: docs/reviews/ch04-probe/mutation-report.txt
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TARGET = REPO / "src" / "score.py"
REPORT = Path(__file__).resolve().parent / "mutation-report.txt"

# (id, description, old_snippet, new_snippet)
MUTATIONS = [
    ("M01", "mcnemar: swap b and c",
     '    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)\n'
     '    c = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)',
     '    c = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)\n'
     '    b = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)'),

    ("M02", "mcnemar: flip the tail comparison, min(b,c) -> max(b,c)",
     '        p = min(1.0, 2.0 * binom_tail_le(min(b, c), nd))',
     '        p = min(1.0, 2.0 * binom_tail_le(max(b, c), nd))'),

    ("M03", "mcnemar: make it ONE-SIDED (drop the factor of two)",
     '        p = min(1.0, 2.0 * binom_tail_le(min(b, c), nd))',
     '        p = min(1.0, 1.0 * binom_tail_le(min(b, c), nd))'),

    ("M04", "mcnemar: count CONCORDANT pairs into b as well",
     '    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)',
     '    b = sum(1 for x, y in zip(a_correct, b_correct) if x)'),

    ("M05", "binom_tail_le: off-by-one, P(X < k) instead of P(X <= k)",
     '    return sum(comb(n, i) for i in range(k + 1)) / (2 ** n)',
     '    return sum(comb(n, i) for i in range(k)) / (2 ** n)'),

    ("M06", "normalise_verdict: LENIENT - prose containing the word counts",
     '    text = str(raw).strip().strip(\'"\').strip("\'").upper()\n'
     '    if text in (WILL_FAIL, WILL_EXECUTE):\n'
     '        return text\n'
     '    return None',
     '    text = str(raw).strip().strip(\'"\').strip("\'").upper()\n'
     '    if WILL_FAIL in text:\n'
     '        return WILL_FAIL\n'
     '    if WILL_EXECUTE in text:\n'
     '        return WILL_EXECUTE\n'
     '    return None'),

    ("M07", "score: DROP the `success + failure == n` check",
     '    if correct + wrong != n:\n'
     '        raise ScoreError(f"success {correct} + failure {wrong} != n {n}")',
     '    if False:\n'
     '        raise ScoreError(f"success {correct} + failure {wrong} != n {n}")'),

    ("M08", "score: charge a wrong answer to the OPPOSITE class",
     '            if gold == WILL_EXECUTE:\n'
     '                false_defect += 1\n'
     '            else:\n'
     '                missed_defect += 1',
     '            if gold == WILL_EXECUTE:\n'
     '                missed_defect += 1\n'
     '            else:\n'
     '                false_defect += 1'),

    ("M09", "score: a NON-ANSWER is charged to NEITHER guard (a silent skip)",
     '            if gold == WILL_EXECUTE:\n'
     '                false_defect += 1\n'
     '            else:\n'
     '                missed_defect += 1',
     '            if pred is None:\n'
     '                pass\n'
     '            elif gold == WILL_EXECUTE:\n'
     '                false_defect += 1\n'
     '            else:\n'
     '                missed_defect += 1'),

    ("M10", "score: a NON-ANSWER is dropped from the denominator entirely",
     '        pred = normalise_verdict(predictions.get(iid))\n'
     '        if pred is None:\n'
     '            unparseable += 1',
     '        pred = normalise_verdict(predictions.get(iid))\n'
     '        if pred is None:\n'
     '            unparseable += 1\n'
     '            n -= 1\n'
     '            continue'),

    ("M11", "guards: WEAKEN both pre-registered thresholds 0.25 -> 0.50",
     'GUARD_FALSE_DEFECT_MAX = 0.25\nGUARD_MISSED_DEFECT_MAX = 0.25',
     'GUARD_FALSE_DEFECT_MAX = 0.50\nGUARD_MISSED_DEFECT_MAX = 0.50'),

    ("M12", "bootstrap: resample ITEMS instead of CLUSTERS",
     '        drawn = [by_cluster[keys[rng.randrange(len(keys))]] for _ in keys]\n'
     '        flat = [it for group in drawn for it in group]',
     '        flat = [items[rng.randrange(len(items))] for _ in items]'),

    ("M13", "paired_accuracy_vectors: drop the sort, so two arms can mis-pair",
     '    for it in sorted(items, key=lambda i: i["item_id"]):',
     '    for it in items:'),

    ("M14", "detectable_effect: require a 1-sided split, not all-one-way",
     '        if min(1.0, 2.0 * binom_tail_le(0, nd)) < alpha:',
     '        if min(1.0, 2.0 * binom_tail_le(1, nd)) < alpha:'),

    ("M15", "n_needed_for_power: flip the significance comparison",
     '        if min(1.0, 2.0 * binom_tail_le(min(c_try, d_try - c_try), d_try)) < alpha:',
     '        if min(1.0, 2.0 * binom_tail_le(min(c_try, d_try - c_try), d_try)) > alpha:'),

    ("M16", "score: DROP the duplicate-item_id check",
     '        if iid in seen:\n'
     '            raise ScoreError(f"duplicate item_id {iid!r} in the eval set")',
     '        if False:\n'
     '            raise ScoreError(f"duplicate item_id {iid!r} in the eval set")'),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run_suite():
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q",
                        "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()]
    return r.returncode, (tail[-1] if tail else "<no output>")


def main():
    original = TARGET.read_bytes()
    orig_sha = sha(original)
    text = original.decode("utf-8")
    out = []

    def p(*a):
        line = " ".join(str(x) for x in a)
        out.append(line)
        print(line, flush=True)

    p("REVIEW CH-04 - check 3: mutation testing of src/score.py")
    p("=" * 78)
    p("target        src/score.py")
    p("git HEAD      %s" % subprocess.run(["git","rev-parse","HEAD"],cwd=REPO,capture_output=True,text=True).stdout.strip())
    p("sha256 before %s" % orig_sha)
    p("")
    p("BASELINE (unmutated tree) - established FIRST, before any mutation")
    rc, summary = run_suite()
    p("    exit %d   %s" % (rc, summary))
    baseline_green = rc == 0
    p("    baseline is %s" % ("GREEN" if baseline_green else "NOT GREEN"))
    if not baseline_green:
        p("    ABORT - cannot mutation-test against a red baseline")
        REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
        return 1
    p("")
    p("%-5s %-62s %-6s %s" % ("id", "mutation", "suite", "result"))
    p("-" * 78)

    caught, survived, skipped = [], [], []
    try:
        for mid, desc, old, new in MUTATIONS:
            if text.count(old) != 1:
                p("%-5s %-62s %-6s SKIPPED (target appears %d times)"
                  % (mid, desc[:62], "-", text.count(old)))
                skipped.append((mid, desc))
                continue
            mutated = text.replace(old, new, 1)
            TARGET.write_text(mutated, encoding="utf-8")
            # hard rule 16 - assert the edit landed AND the old text is gone
            back = TARGET.read_text(encoding="utf-8")
            assert new in back, f"{mid}: new text not present"
            if old not in new:          # a pure replacement must erase the old text
                assert old not in back, f"{mid}: old text still present"
            else:                       # an insertion keeps it; assert the file grew
                assert back != text, f"{mid}: file unchanged"
            assert sha(TARGET.read_bytes()) != orig_sha, f"{mid}: file unchanged"
            rc, summary = run_suite()
            TARGET.write_bytes(original)
            assert sha(TARGET.read_bytes()) == orig_sha, f"{mid}: RESTORE FAILED"
            if rc != 0:
                caught.append((mid, desc, summary))
                p("%-5s %-62s %-6s CAUGHT   %s" % (mid, desc[:62], "RED", summary))
            else:
                survived.append((mid, desc, summary))
                p("%-5s %-62s %-6s *** SURVIVED ***   %s"
                  % (mid, desc[:62], "GREEN", summary))
    finally:
        TARGET.write_bytes(original)
        final_sha = sha(TARGET.read_bytes())
        p("")
        p("sha256 after  %s" % final_sha)
        p("restored byte-for-byte: %s" % (final_sha == orig_sha))

    g = subprocess.run(["git", "diff", "--exit-code", "--", "src/score.py"],
                       cwd=REPO, capture_output=True, text=True)
    p("git diff --exit-code -- src/score.py  ->  exit %d %s"
      % (g.returncode, "(clean)" if g.returncode == 0 else "(DIRTY)"))
    p("")
    p("=" * 78)
    p("applied %d - CAUGHT %d - SURVIVED %d - skipped %d"
      % (len(caught) + len(survived), len(caught), len(survived), len(skipped)))
    if survived:
        p("")
        p("MUTATIONS THE SUITE DID NOT CATCH:")
        for mid, desc, _ in survived:
            p("   %s  %s" % (mid, desc))
    p("=" * 78)

    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
