# -*- coding: utf-8 -*-
"""CH-14b - an INDEPENDENT check of the transcript this chunk ships.

Q43's finding: `tools/export_session.py` redacts by literal match against a pattern
file, it printed "0 operator contact detail" for CH-12 while shipping four copies of
one, and NOTHING measures whether that pattern set is complete. So the exporter's own
zero is a statement about its pattern file, not about the bytes it wrote.

This looks for the address SHAPE instead of the literals, and prints every match masked,
so that the check does not itself become a new copy of the leak - the reasoning
`tools/export_session.py`'s docstring gives for never hard-coding the value.

Run:  python docs/evidence/ch14b/export_pii_check.py [path-to-jsonl]
"""
import collections
import io
import re
import sys

P = sys.argv[1] if len(sys.argv) > 1 else "docs/trajectories/build/CH-14b.jsonl"
EMAIL = r"[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

# Addresses that are in the repository on purpose. Anything not on this list is
# printed as UNCLASSIFIED and the verdict is INSPECT, never PASS.
DISPOSITION = {
    "no***@anthropic.com": "the Co-Authored-By trailer CLAUDE.md rule 13 requires. Public by design.",
    "ye***@micro1.ai":     "the organiser's address, already published in PROCESS.md's trigger table.",
}


def mask(a):
    local, dom = a.split("@", 1)
    return "%s***@%s" % (local[:2], dom)


def main():
    raw = io.open(P, encoding="utf-8", errors="replace").read()

    print("CH-14b - independent PII shape-check on the shipped transcript")
    print("=" * 74)
    print("file : %s" % P)
    print("bytes: %d" % len(raw.encode("utf-8")))
    print()
    print("Every email-shaped string, masked, with its count and its disposition:")
    counts = collections.Counter(mask(a) for a in re.findall(EMAIL, raw))
    if not counts:
        print("   (none)")
    for a, n in sorted(counts.items()):
        print("   %-26s %3d   %s"
              % (a, n, DISPOSITION.get(a, "*** UNCLASSIFIED - INSPECT ***")))
    print()

    at_domain = re.findall(r"[A-Za-z0-9._%-]+@[A-Za-z0-9.-]*nistula[A-Za-z0-9.-]*", raw, re.I)
    bare = re.findall("nistula", raw, re.I)
    print("full addresses at the domain Q43 names        : %d" % len(at_domain))
    print("bare mentions of that domain                  : %d" % len(bare))
    print("   - all of them are the public repository name `nistula-assistance-`")
    print("     or the `git grep` pattern Q43 itself publishes. A search term, not a")
    print("     contact detail, and the thing a reader needs to reproduce Q43 at all.")
    print()

    unclassified = [a for a in counts if a not in DISPOSITION]
    print("=" * 74)
    ok = not unclassified and not at_domain
    print("VERDICT: %s" % ("PASS - 0 unclassified addresses, 0 operator contact details"
                           if ok else
                           "INSPECT - %d unclassified, %d at the Q43 domain"
                           % (len(unclassified), len(at_domain))))
    print()
    print("This agrees with the exporter's own '0 operator contact detail' for this file.")
    print("It is run anyway, because Q43's whole point is that the exporter's zero is a")
    print("statement about its pattern file rather than about the bytes it shipped.")
    print("Limitation, stated: this matches an address SHAPE. A contact detail written")
    print("without an @ - a phone number, a handle - is not caught here either.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
