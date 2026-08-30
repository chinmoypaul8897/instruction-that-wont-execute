"""CH-03 · 1a — re-measure the AMDPAR attributor under `CONTEXT.md` **v1.1**.

`QUESTIONS.md` Q14: *"Every `extended` figure in this repository was computed
case-INsensitively"*, but v1.1 specifies the word form **case-sensitively** and adds a
`<REGTEXT>` part-boundary reset. Q14 also records that the case-sensitive figures
**are not reconstructible by arithmetic** from the case-insensitive ones. **So this
module re-measures. It does not adjust.**

It also does not rewrite anything. `data/amdpars/` is CH-02's freeze and is read-only;
this module re-derives from the same raw FR issues and writes to a **new** directory.

THE FOUR CONFIGURATIONS, and why four rather than one
-----------------------------------------------------
Publishing only the v1.1 number would leave a reader unable to tell which of v1.1's
two changes moved what. Pre-registered in `docs/evidence/ch03-evalset/pre-registration.md`
§1 before any of them ran:

    spec_literal  sign only, no reset          CONTEXT.md v1.0's own regex
    extended_ci   + word form, case-INsensitive, no reset      what CH-02 shipped
    extended_cs   + word form, case-SENSITIVE,  no reset       isolates case alone
    v11           + word form, case-SENSITIVE,  + part reset   CONTEXT.md v1.1

`spec_literal` and `extended_ci` are the **control**: they must reproduce CH-02's
committed 0.5080 / 0.6643 exactly. If they do not, this re-measurement is wrong and
nothing downstream of it may be trusted. The control is asserted, not eyeballed.

THE TWO v1.1 RULES, spelled out because a reviewer reimplements from `CONTEXT.md`
----------------------------------------------------------------------------------
1. **Case-sensitive word form.** `Section`/`Sections`, never `section`. §8: *"The word
   form is matched CASE-SENSITIVELY: `Section`, never `section`."* Q12(c) measured why:
   *"Appendix A to part 75 is amended by revising the title of section 1.1"* pins
   `current_section` to `1.1` inside a part-75 `<REGTEXT>`.
2. **Part-boundary reset.** §8 step 2: *"Reset `current_section` to null at every
   `<REGTEXT>` part boundary — an instruction cannot inherit a section from a different
   CFR part."* Operationalised as: reset whenever this element's `<REGTEXT>` `PART`
   differs from the previous element's. Two adjacent `<REGTEXT>` elements carrying the
   same `PART` are not a boundary; a `PART` that goes to or from `None` is.

PURITY - hard rule 8. Everything here is pure. The raw XML reading is delegated to
`attribute_amdpars`, whose network lives only in its own `fetch_issues`.
DETERMINISM - hard rule 9. Sorted keys, LF endings, no clock, no randomness.

    python -m attribute_v11 remeasure --raw data/raw/fr --out data/attribution-v11
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from attribute_amdpars import (  # noqa: E402
    _SECTION,
    AttributorError,
    SIGN_RE,
    completeness,
    load_issue,
    parse_amdpar,
    sha256_file,
    split_quotes,
    write_json,
    write_jsonl,
)

DEFAULT_RAW_DIR = Path("data/raw/fr")
DEFAULT_OUT_DIR = Path("data/attribution-v11")
DEFAULT_AMDPARS = Path("data/amdpars")

# The two word-form spellings, side by side. `WORD_CI_RE` is CH-02's shipped detector,
# kept verbatim so `extended_ci` really is what CH-02 measured rather than a
# reconstruction of it. `WORD_CS_RE` is `CONTEXT.md` v1.1's.
WORD_CI_RE = re.compile(r"\b[Ss]ections?\s+(" + _SECTION + r")")
WORD_CS_RE = re.compile(r"\bSections?\s+(" + _SECTION + r")")

# (word form on?, case-sensitive?, part reset?)
CONFIGS: dict[str, tuple[bool, bool, bool]] = {
    "spec_literal": (False, False, False),
    "extended_ci":  (True,  False, False),
    "extended_cs":  (True,  True,  False),
    "v11":          (True,  True,  True),
}

# CH-02's committed figures, transcribed from `data/amdpars/completeness.json`'s own
# `global` block via STATUS.md and CONTEXT.md section 8. The control asserts against
# the file, not against these; they are here so a reader sees what is being checked.
CH02_CONTROL = {
    "spec_literal": 0.5080,
    "extended_ci": 0.6643,
}


def find_sections_cfg(dequoted: str, word_form: bool, case_sensitive: bool):
    """Section citations in document order, plus the spans they consumed.

    Mirrors `attribute_amdpars.find_sections` but takes the word form and its case
    sensitivity as explicit parameters instead of a detector name, because v1.1 makes
    case a *specified* property rather than an implementation detail.
    """
    hits = [(m.start(), m.end(), m.group(1)) for m in SIGN_RE.finditer(dequoted)]
    if word_form:
        rx = WORD_CS_RE if case_sensitive else WORD_CI_RE
        hits += [(m.start(), m.end(), m.group(1)) for m in rx.finditer(dequoted)]
    hits.sort()
    return [h[2] for h in hits], [(h[0], h[1]) for h in hits]


def attribute_cfg(texts, parts, config: str) -> list[dict]:
    """`CONTEXT.md` v1.1 §8's algorithm under one of the four configurations.

    `texts` is one document's AMDPAR texts in DOCUMENT ORDER — the order of the list
    is the contract, because carry-forward *is* the order.
    """
    if config not in CONFIGS:
        raise AttributorError(f"unknown config {config!r}")
    word_form, case_sensitive, part_reset = CONFIGS[config]
    parts = list(parts or [None] * len(texts))
    if len(parts) != len(texts):
        raise AttributorError("parts must be the same length as texts")

    out: list[dict] = []
    current = None
    prev_part = None
    for ordinal, (text, part) in enumerate(zip(texts, parts), start=1):
        # v1.1 step 2. The reset happens BEFORE this element is read, so an element
        # that both crosses a boundary and names its own section still names it.
        reset_here = False
        if part_reset and ordinal > 1 and part != prev_part:
            current = None
            reset_here = True
        prev_part = part

        rec = parse_amdpar(text)
        # Section, operation and designation are all read from the DE-QUOTED text
        # (goldens P1), so a cross-reference being inserted inside quotation marks
        # can never be mistaken for the section being amended.
        dequoted, _, _ = split_quotes(text)
        named, _ = find_sections_cfg(dequoted, word_form, case_sensitive)
        if named:
            current = named[0]
        section = current
        sec_part = section.split(".")[0] if section else None
        rec.update({
            "ordinal": ordinal,
            "config": config,
            "names_section": bool(named),
            "sections_named": named,
            "section": section,
            "attributed": section is not None,
            "unattributable": section is None,
            "regtext_part": part,
            "part_reset_fired": reset_here,
            "part_mismatch": bool(section and part and sec_part != str(part)),
            "complete": section is not None and rec["parsed"],
        })
        out.append(rec)
    return out


def remeasure(documents: dict) -> dict:
    """All four configurations over every document. Pure.

    `documents` maps frdoc -> {"amdpars": [...], "parts": [...], ...}.
    Returns {"global": {...}, "per_document": {...}, "records": [...]}.
    """
    per_doc: dict[str, dict] = {}
    flat: dict[str, list[dict]] = {c: [] for c in CONFIGS}
    records: list[dict] = []

    for frdoc in sorted(documents):
        d = documents[frdoc]
        rows = {c: attribute_cfg(d["amdpars"], d["parts"], c) for c in CONFIGS}
        per_doc[frdoc] = {c: completeness(rows[c]) for c in CONFIGS}
        for c in CONFIGS:
            flat[c].extend(rows[c])
        for i in range(len(d["amdpars"])):
            merged = {
                "frdoc": frdoc,
                "ordinal": i + 1,
                "issue_date": d.get("issue_date"),
                "regtext_part": d["parts"][i],
                "regtext_title": d["titles"][i] if d.get("titles") else None,
                "text": rows["v11"][i]["text"],
                "operation": rows["v11"][i]["operation"],
                "anchor": rows["v11"][i]["anchor"],
                "anchors": rows["v11"][i]["anchors"],
                "designation": rows["v11"][i]["designation"],
                "designations": rows["v11"][i]["designations"],
                "parsed": rows["v11"][i]["parsed"],
                "part_reset_fired": rows["v11"][i]["part_reset_fired"],
            }
            for c in CONFIGS:
                merged[f"section_{c}"] = rows[c][i]["section"]
                merged[f"names_section_{c}"] = rows[c][i]["names_section"]
                merged[f"complete_{c}"] = rows[c][i]["complete"]
            merged["cs_changes_attribution"] = (
                rows["extended_ci"][i]["section"] != rows["extended_cs"][i]["section"])
            merged["v11_changes_attribution"] = (
                rows["extended_ci"][i]["section"] != rows["v11"][i]["section"])
            records.append(merged)

    glob = {c: completeness(flat[c]) for c in CONFIGS}

    # Q14(b): section 8's "~42% of AMDPARs name a section", measured under each.
    names = {c: sum(1 for r in flat[c] if r["names_section"]) for c in CONFIGS}
    total = len(flat["v11"])
    glob_names = {c: {"names_section": names[c],
                      "total": total,
                      "rate": (names[c] / total) if total else 0.0} for c in CONFIGS}

    return {"global": glob, "per_document": per_doc, "records": records,
            "names_section_rate": glob_names}


def control_check(glob: dict, ch02_completeness_path: Path) -> dict:
    """The pre-registered control: `spec_literal` and `extended_ci` must reproduce
    CH-02's committed figures **exactly**, to every decimal place the file carries.

    Asserted rather than eyeballed. A re-measurement that cannot reproduce the thing
    it is re-measuring is not evidence about the new detector; it is evidence about
    itself, and everything built on it would inherit the error.
    """
    committed = json.loads(ch02_completeness_path.read_text(encoding="utf-8"))["global"]
    # CH-02 spelled its two detectors `spec_literal` and `extended`. This module
    # splits the second into `extended_ci` / `extended_cs` because v1.1 makes case a
    # specified property, so the control maps CH-02's `extended` onto `extended_ci` -
    # the case-INsensitive one, which is what CH-02 actually ran (Q14(a)).
    CH02_KEY = {"spec_literal": "spec_literal", "extended_ci": "extended"}
    out = {}
    for cfg in ("spec_literal", "extended_ci"):
        want, got = committed[CH02_KEY[cfg]], glob[cfg]
        same = {k: (want.get(k), got.get(k)) for k in
                ("total", "attributed", "unattributable", "parsed", "complete")}
        ok = all(a == b for a, b in same.values())
        out[cfg] = {
            "reproduces": ok,
            "ch02_completeness": want["completeness"],
            "remeasured_completeness": got["completeness"],
            "fields": {k: {"ch02": a, "remeasured": b} for k, (a, b) in same.items()},
        }
    return out


# ============================================================ CLI

def load_documents(raw: Path, amdpars_dir: Path) -> dict:
    """Rebuild the 70 FR documents' AMDPAR texts from the raw issues CH-02 used.

    `data/amdpars/documents.json` names the issue file and the FR doc number for each;
    the AMDPAR text itself is re-read from the raw XML, so this is a genuine
    re-measurement from source and not a re-reading of CH-02's derived records.
    """
    meta = json.loads((amdpars_dir / "documents.json").read_text(encoding="utf-8"))
    by_file: dict[str, list[str]] = {}
    for frdoc, d in meta.items():
        by_file.setdefault(d["issue_file"], []).append(frdoc)

    documents: dict[str, dict] = {}
    for issue_file in sorted(by_file):
        path = raw / issue_file
        if not path.exists():
            raise AttributorError(f"raw issue missing: {path}. Run refetch.py first.")
        issue = load_issue(path)
        rules = {r["frdoc"]: r for r in issue["rules"] if r["frdoc"]}
        for frdoc in sorted(by_file[issue_file]):
            r = rules.get(frdoc)
            if r is None:
                raise AttributorError(f"{frdoc} not found in {issue_file}")
            documents[frdoc] = {
                "frdoc": frdoc,
                "issue_date": meta[frdoc]["issue_date"],
                "issue_file": issue_file,
                "amdpars": r["amdpars"],
                "parts": r["parts"],
                "titles": r["titles"],
            }
    return documents


def cmd_remeasure(args) -> int:
    raw, out = Path(args.raw), Path(args.out)
    amdpars_dir = Path(args.amdpars)
    documents = load_documents(raw, amdpars_dir)
    result = remeasure(documents)
    glob = result["global"]

    ctrl = control_check(glob, amdpars_dir / "completeness.json")

    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "amdpars_v11.jsonl", result["records"])
    write_json(out / "completeness_v11.json", {
        "configs": {k: {"word_form": v[0], "case_sensitive": v[1], "part_reset": v[2]}
                    for k, v in CONFIGS.items()},
        "global": glob,
        "per_document": result["per_document"],
        "names_section_rate": result["names_section_rate"],
        "control_vs_ch02": ctrl,
    })
    manifest = {"chunk": "CH-03/1a", "what": "AMDPAR attribution re-measured under "
                                             "CONTEXT.md v1.1", "files": {}}
    for name in sorted(p.name for p in out.iterdir() if p.name != "manifest.json"):
        p = out / name
        manifest["files"][name] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    write_json(out / "manifest.json", manifest)

    # ---- report -----------------------------------------------------------------
    print("=" * 78)
    print("CH-03 1a - ATTRIBUTOR RE-MEASURED UNDER CONTEXT.md v1.1")
    print("=" * 78)
    print(f"  documents={len(documents)}  AMDPAR elements={glob['v11']['total']}")
    print()
    print(f"  {'config':<14}{'complete':>10}{'completeness':>14}{'attributed':>12}"
          f"{'attribution':>13}{'unattrib':>10}{'part_mism':>11}")
    for c in ("spec_literal", "extended_ci", "extended_cs", "v11"):
        g = glob[c]
        print(f"  {c:<14}{g['complete']:>10}{g['completeness']:>14.4f}"
              f"{g['attributed']:>12}{g['attribution_rate']:>13.4f}"
              f"{g['unattributable']:>10}{g['part_mismatch']:>11}")
    print()
    print("  CONTROL - spec_literal and extended_ci must reproduce CH-02 exactly")
    allok = True
    for cfg, c in ctrl.items():
        mark = "OK  " if c["reproduces"] else "FAIL"
        allok &= c["reproduces"]
        print(f"    {mark} {cfg:<14} CH-02 {c['ch02_completeness']:.4f}  "
              f"re-measured {c['remeasured_completeness']:.4f}")
        if not c["reproduces"]:
            for k, v in c["fields"].items():
                if v["ch02"] != v["remeasured"]:
                    print(f"         {k}: CH-02 {v['ch02']} != re-measured {v['remeasured']}")
    print()
    print("  Q14(b) - CONTEXT.md section 8's \"only ~42% of AMDPARs name a section\"")
    for c in ("spec_literal", "extended_ci", "extended_cs", "v11"):
        n = result["names_section_rate"][c]
        print(f"    {c:<14} {n['names_section']:>5} / {n['total']}  = {n['rate']:.4f}")
    print()
    changed_cs = sum(1 for r in result["records"] if r["cs_changes_attribution"])
    changed_v11 = sum(1 for r in result["records"] if r["v11_changes_attribution"])
    resets = sum(1 for r in result["records"] if r["part_reset_fired"])
    print(f"  elements whose attribution CASE-SENSITIVITY alone changes : {changed_cs}")
    print(f"  elements whose attribution v1.1 as a whole changes         : {changed_v11}")
    print(f"  part-boundary resets fired                                 : {resets}")
    print()
    print("  NOTE: a stricter detector cannot RAISE a failing figure. CH-02's gate")
    print("  outcome is not revisited by this re-measurement - it stays FAILED and")
    print("  in its pre-registered '< 0.80 documented failure' branch.")
    return 0 if allok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("remeasure", help="re-measure all four detector configurations")
    r.add_argument("--raw", default=str(DEFAULT_RAW_DIR))
    r.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    r.add_argument("--amdpars", default=str(DEFAULT_AMDPARS))
    r.set_defaults(func=cmd_remeasure)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
