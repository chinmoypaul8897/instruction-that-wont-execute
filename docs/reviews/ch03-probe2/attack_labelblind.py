"""CH-03 RE-REVIEW (round 2) - an independent label-blind attack on the frozen set.

Imports NOTHING from src/. Reads data/evalset/items.jsonl only.
Never reads `label`, `role`, `note_text`, `note_node` or `section_text` when
building a feature - those are used ONLY to score the attack afterwards.

Attack format
-------------
The eval set is a matched design: within one FR document, a positive and its
negative carry EXACTLY the same instruction count. An attacker can therefore
recover the blocks with no labels at all - group by (frdoc, instruction_count).
Each block of size 2k holds k positives and k negatives (verified below, and that
verification IS the attack's licence).

For a feature f: inside every block sort by f, call the top half one class and the
bottom half the other, take whichever direction scores better. Ties break by
`item_id`, so the result is deterministic. Accuracy is over all 82 items.

A permutation null is computed by shuffling labels WITHIN each block, which is the
correct null for a blocked design.
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ITEMS = REPO / "data/evalset/items.jsonl"

FORBIDDEN = ("label", "role", "note_text", "note_node", "section_text")

_INT = re.compile(r"\d+")


def load():
    return [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def sortkey(section):
    part, _, rest = section.partition(".")
    m = _INT.match(part)
    pk = int(m.group(0)) if m else 0
    toks = []
    for t in re.findall(r"\d+|\D+", rest):
        toks.append((0, int(t), "") if t.isdigit() else (1, 0, t))
    return (pk, tuple(toks))


def flat_num(section):
    """A single monotone number for a section, good enough for ordering."""
    k = sortkey(section)
    v = float(k[0]) * 1e9
    scale = 1e6
    for kind, num, txt in k[1]:
        v += (num if kind == 0 else (ord(txt[0]) if txt else 0)) * scale
        scale /= 1e3
    return v


def features(it):
    ins = it["instructions"]
    texts = [(i.get("text") or "") for i in ins]
    ords_ = [i["ordinal"] for i in ins]
    sec = it["section"]
    part, _, rest = sec.partition(".")
    sc = it["strip_counts"]
    vm = re.findall(r"vol(\d+)", it["volume"])
    return {
        # ---- pure position / identity of the section ------------------------
        "section_lex": float(sum(ord(c) for c in sec)),
        "section_num": flat_num(sec),
        "part_num": float(_INT.match(part).group(0)) if _INT.match(part) else 0.0,
        "suffix_num": flat_num("0." + rest),
        "sec_len_chars": float(len(sec)),
        "sec_has_letter": 1.0 if re.search(r"[A-Za-z]", sec) else 0.0,
        "sec_has_dash": 1.0 if "-" in sec else 0.0,
        "title_num": float(it["cfr_title"]),
        "as_of_edition": float(it["as_of_edition"]),
        # ---- position within the document's instruction stream --------------
        "ord_min": float(min(ords_)) if ords_ else 0.0,
        "ord_max": float(max(ords_)) if ords_ else 0.0,
        "ord_mean": (sum(ords_) / len(ords_)) if ords_ else 0.0,
        "ord_span": float(max(ords_) - min(ords_)) if ords_ else 0.0,
        # ---- size of the frozen text (a count, never its content) -----------
        "chars_stripped": float(it["chars_stripped"]),
        "chars_unstripped": float(it["chars_unstripped"]),
        "chars_delta": float(it["chars_unstripped"] - it["chars_stripped"]),
        "chars_ratio": it["chars_stripped"] / max(1.0, float(it["chars_unstripped"])),
        # ---- the leakage strip counters -------------------------------------
        "strip_EDNOTE": float(sc.get("EDNOTE", 0)),
        "strip_EFFDNOTP": float(sc.get("EFFDNOTP", 0)),
        "strip_CITA": float(sc.get("CITA", 0)),
        "strip_EAR": float(sc.get("EAR", 0)),
        "strip_total": float(sc.get("total", 0)),
        # ---- the volume the text came from ----------------------------------
        "vol_num": float(vm[0]) if vm else 0.0,
        "vol_route_fallback": 0.0 if it["volume_route"] == "range-match" else 1.0,
        "vol_header_len": float(len(it["volume_parts_header"] or "")),
        # ---- the instruction text (what B0 itself is given) ------------------
        "instr_n": float(len(ins)),
        "instr_chars_total": float(sum(len(t) for t in texts)),
        "instr_chars_mean": (sum(len(t) for t in texts) / len(texts)) if texts else 0.0,
        "instr_chars_max": float(max([len(t) for t in texts] or [0])),
        "instr_n_anchor": float(sum(1 for i in ins if i.get("anchor"))),
        "instr_n_desig": float(sum(1 for i in ins if i.get("designation"))),
        "instr_n_revise": float(sum(1 for i in ins if i.get("operation") == "revise")),
        "instr_n_add": float(sum(1 for i in ins if i.get("operation") == "add")),
        "instr_n_remove": float(sum(1 for i in ins if i.get("operation") == "remove")),
        "instr_n_redesig": float(sum(1 for i in ins
                                     if i.get("operation") == "redesignate")),
        "instr_desig_depth": float(max([len(re.findall(r"\(", i.get("designation") or ""))
                                        for i in ins] or [0])),
        # ---- document level (constant inside a block; kept for completeness) -
        "doc_completeness": float(it["document_completeness_v11"]),
        "doc_amdpar_count": float(it["document_amdpar_count"]),
    }


def blocks(items, mode="count"):
    b = defaultdict(list)
    for it in items:
        b[(it["frdoc"], it["instruction_count"]) if mode == "count"
          else it["frdoc"]].append(it)
    return b


def block_attack(items, feats, name, mode, lab):
    best = 0.0
    for direction in (1, -1):
        right = 0
        for _, grp in blocks(items, mode).items():
            k = len(grp) // 2
            ordered = sorted(grp, key=lambda it: (direction * feats[it["item_id"]][name],
                                                  it["item_id"]))
            for j, it in enumerate(ordered):
                guess = "WILL_EXECUTE" if j < k else "WILL_FAIL"
                right += (guess == lab[it["item_id"]])
        best = max(best, right / len(items))
    return best


def threshold_attack(items, feats, name, lab):
    vals = sorted({feats[it["item_id"]][name] for it in items})
    cuts = [vals[0] - 1.0] + [(a + b) / 2 for a, b in zip(vals, vals[1:])] + [vals[-1] + 1.0]
    best = 0.0
    for c in cuts:
        for direction in (1, -1):
            right = 0
            for it in items:
                v = direction * feats[it["item_id"]][name]
                guess = "WILL_FAIL" if v > direction * c else "WILL_EXECUTE"
                right += (guess == lab[it["item_id"]])
            best = max(best, right / len(items))
    return best


def best_of_bank(items, feats, names, lab):
    m = 0.0
    for n in names:
        m = max(m, block_attack(items, feats, n, "count", lab),
                block_attack(items, feats, n, "frdoc", lab),
                threshold_attack(items, feats, n, lab))
    return m


def main():
    items = load()
    for it in items:
        for f in FORBIDDEN:
            if f not in it:
                raise SystemExit("schema changed: " + f)
    feats = {it["item_id"]: features(it) for it in items}
    names = sorted(next(iter(feats.values())).keys())
    truth = {it["item_id"]: it["label"] for it in items}

    ok = True
    for k, grp in sorted(blocks(items, "count").items()):
        p = sum(1 for it in grp if it["label"] == "WILL_FAIL")
        if p * 2 != len(grp):
            ok = False
            print("  block %s NOT balanced: %d positives of %d" % (k, p, len(grp)))
    print("blocks recoverable label-free and balanced : %s" % ok)
    print("items %d  count-blocks %d  frdoc-blocks %d"
          % (len(items), len(blocks(items, "count")), len(blocks(items, "frdoc"))))
    print()

    rows = []
    for n in names:
        ab = block_attack(items, feats, n, "count", truth)
        af = block_attack(items, feats, n, "frdoc", truth)
        at = threshold_attack(items, feats, n, truth)
        rows.append((max(ab, af, at), ab, af, at, n))
    rows.sort(reverse=True)
    print("%-26s %11s %11s %10s %8s" % ("feature", "block(cnt)", "block(doc)",
                                        "threshold", "BEST"))
    for best, ab, af, at, n in rows:
        print("%-26s %11.4f %11.4f %10.4f %8.4f" % (n, ab, af, at, best))
    print()

    right = 0
    for grp in blocks(items, "frdoc").values():
        ordered = sorted(grp, key=lambda i: i["section"])
        half = len(ordered) // 2
        for j, it in enumerate(ordered):
            right += (("WILL_EXECUTE" if j < half else "WILL_FAIL") == it["label"])
    print("REVIEWER ROUND-1 ATTACK (frdoc block, lexicographic section sort): "
          "%d/%d = %.4f" % (right, len(items), right / len(items)))

    observed = max(r[0] for r in rows)
    rng = random.Random(20260831)
    nulls = []
    for _ in range(500):
        lab = {}
        for _, grp in blocks(items, "count").items():
            ls = [it["label"] for it in grp]
            rng.shuffle(ls)
            for it, l in zip(grp, ls):
                lab[it["item_id"]] = l
        nulls.append(best_of_bank(items, feats, names, lab))
    ge = sum(1 for x in nulls if x >= observed)
    nulls.sort()
    print()
    print("BEST-OF-%d OBSERVED = %.4f" % (len(names), observed))
    print("within-block permutation null over the SAME bank: mean %.4f  p95 %.4f  "
          "max %.4f" % (sum(nulls) / len(nulls), nulls[int(.95 * len(nulls))], nulls[-1]))
    print("p(best-of-bank >= observed) = %.4f   [%d/%d]"
          % ((ge + 1) / (len(nulls) + 1), ge, len(nulls)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
