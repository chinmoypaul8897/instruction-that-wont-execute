"""CH-02 PROBE - the citation-resolution defect, both states shown. Hard rule 6.

    python docs/evidence/ch02-attributor/ch02_probe_resolution.py

Exits 0 only if BOTH states reproduce: the old rule fails and the new rule passes. It
exits 2 when `data/raw/fr` is absent, because a probe that passes on missing input
proves nothing.

THE DEFECT. `docs/evidence/ch02-attributor/goldens.md` section 0 pre-registered two
independent routes from a citation to an FR document - the front-matter <CNTNTS> page
range, and the <PRTPAGE> carry-forward - and said they must agree. Measured on the real
corpus they disagree twice in 85, and BOTH times the contents route is the wrong one:
govinfo lists a *circular* in the contents as a single entry spanning the page range of
every rule inside it, so the summary document, which amends nothing at all, is indexed
over the top of the rule that does the amending.

Separately, two citations resolved to NOTHING, because an editorial note's date is the
date the rule was filed, not the date it was published, and the two differ by a day in
either direction.

THE FIX. A citation carries three exact keys - volume, page and SECTION - and page
alone cannot separate two documents that share a page. `resolve_citation` gathers every
candidate either route admits and prefers the one whose AMDPARs actually attribute to
the cited section; where that does not separate them, the per-<RULE> PRTPAGE route wins
over the editorial index. When nothing in the noted issue matches, both neighbouring
days are tried and a neighbour is accepted only on a section match.

This is a resolution fix, not a threshold change. It moves no completeness number into
a kinder pre-registered branch: global completeness is 0.5080 / 0.6643 before and after,
and both sit in the same `< 0.80` branch.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
RAW = REPO / "data/raw/fr"

import attribute_amdpars as A  # noqa: E402


def rule_line(rule, route):
    if rule is None:
        return f"NOTHING RESOLVED           route={route}"
    return (f"{rule['frdoc']:<12} amdpars={len(rule['amdpars']):>4}  "
            f"pages={rule['pages'][0] if rule['pages'] else None}-"
            f"{rule['pages'][-1] if rule['pages'] else None}  route={route}\n"
            f"                 subject: {str(rule['subject'])[:64]}")


def main() -> int:
    if not RAW.exists():
        print("data/raw/fr absent - a probe that passes on missing input proves "
              "nothing. Run `python refetch.py` first.")
        return 2

    failures = []
    print("=" * 78)
    print("PROBE 1 - the contents route indexes a circular over the rule that amends")
    print("=" * 78)
    for fname, page, section, want_old, want_new in [
        ("FR-2014-04-29.xml", 24198, "6.302-1", "2014-08743", "2014-08744"),
        ("FR-2025-11-24.xml", 52865, "887.11", "2025-20827", None),
    ]:
        issue = A.load_issue(RAW / fname)
        old, old_route = A.resolve_page(issue, page)
        new, new_route = A.resolve_citation(issue, page, section)
        print(f"\n{fname}  citation page {page}  cited section {section}")
        print(f"  OLD  resolve_page      {rule_line(old, old_route)}")
        print(f"  NEW  resolve_citation  {rule_line(new, new_route)}")
        old_has = section in A.sections_amended(old) if old else False
        new_has = section in A.sections_amended(new) if new else False
        print(f"  does the OLD document amend the cited section? {old_has}")
        print(f"  does the NEW document amend the cited section? {new_has}")
        if old_route != "both-disagree":
            failures.append(f"{fname}: expected the old routes to disagree, got {old_route}")
        if old_has:
            failures.append(f"{fname}: the old document already amended {section}; "
                            "there is no defect to probe")
        if not new_has:
            failures.append(f"{fname}: the new document does not amend {section}")
        if want_old and old and old["frdoc"] != want_old:
            failures.append(f"{fname}: old picked {old['frdoc']}, expected {want_old}")
        if want_new and new and new["frdoc"] != want_new:
            failures.append(f"{fname}: new picked {new['frdoc']}, expected {want_new}")

    print()
    print("=" * 78)
    print("PROBE 2 - the note's date is the FILING date, and drifts a day either way")
    print("=" * 78)
    for noted, published, page, section, want in [
        ("FR-2020-07-15.xml", "FR-2020-07-16.xml", 43138, "90.209", "2020-11897"),
        ("FR-2022-05-25.xml", "FR-2022-05-24.xml", 31688, "1653.2", "2022-10875"),
    ]:
        n_issue = A.load_issue(RAW / noted)
        old, old_route = A.resolve_page(n_issue, page)
        p_issue = A.load_issue(RAW / published)
        new, new_route = A.resolve_citation(p_issue, page, section)
        print(f"\ncited as {noted[3:13]}, published {published[3:13]}  "
              f"page {page}  section {section}")
        print(f"  OLD  in the noted issue      {rule_line(old, old_route)}")
        print(f"  NEW  in the neighbour issue  {rule_line(new, new_route)}")
        if old is not None:
            failures.append(f"{noted}: expected nothing to resolve, got {old['frdoc']}")
        if new is None or new["frdoc"] != want:
            failures.append(f"{published}: expected {want}")
        elif section not in A.sections_amended(new):
            failures.append(f"{published}: {want} does not amend {section}")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"\nPROBE DID NOT FLIP - {len(failures)} problem(s). A probe that does not "
              "fail on the old code is not evidence.")
        return 1
    print("  Both states reproduce: the old rule fails on all four citations, the new")
    print("  rule resolves all four to a document that actually amends the cited")
    print("  section. Kept forever (hard rule 6).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
