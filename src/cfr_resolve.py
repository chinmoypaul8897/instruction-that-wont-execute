"""CH-05 — `cfr_resolve`, the deterministic resolver. Capability 1 of `CONTEXT.md` §6.

    cfr_resolve(title, part, section, as_of_date, quoted_text, designation, text)
    -> {found, level, designation_exists, siblings, char_offset, ...}

**Designation-hierarchy resolution FIRST, quoted-anchor matching second.** The order is
not a preference; §6 forces it by measurement: *"26/33 and 35/42 labelled items have no
extractable quoted anchor, and NARA's dominant note mechanisms (`did-not-exist`,
`already-exists`) are designation-**state** facts. A pure quoted-string matcher no-ops
on ~80% of the pool."*

THE THREE DECLARED LEVELS — hard rule 7, and §1
------------------------------------------------
Matching is attempted at `exact`, then `whitespace-collapsed`, then
`alphanumeric-only`, **the first that matches is reported**, and the level achieved is
**returned in the output, never applied invisibly**.

`alphanumeric-only` strips punctuation and whitespace. **It does NOT fold case.**
Folding case would silently make `(A)` and `(a)` the same designation, and paragraph
designations are the objects this whole project rests on. Golden R-C4 is the test that
stops the levels becoming a licence.

`char_offset` IS ALWAYS AN INDEX INTO THE CALLER'S OWN STRING
--------------------------------------------------------------
Even when the match needed normalisation. A tool that reported an offset into its own
normalised buffer would be reporting a position in a document that does not exist, and
the CH-10 worksheet highlights the anchor in the real text using this number. Golden
R-D asserts `text[char_offset : char_offset + len(matched_span)] == matched_span` at
every level.

PURITY - hard rule 8: no network, no clock, no randomness, and the input text is never
mutated. `as_of_date` selects which frozen text the CALLER passes in; this module
fetches nothing.
DETERMINISM - hard rule 9: same inputs, byte-identical output.

Goldens: `docs/evidence/ch05-resolve/goldens.md`, committed before this file.
"""
from __future__ import annotations

import re

LEVELS = ("exact", "whitespace-collapsed", "alphanumeric-only")
LEVEL_NONE = "none"

# A designation is a run of short parenthesised groups, optionally spaced: FR drafting
# writes both `(b)(4)(i)(A)` and `(b) (4) (i) (A)` and they mean the same target.
_DESIG_GROUP = re.compile(r"\(([A-Za-z0-9]{1,4})\)")
_DESIG_WHOLE = re.compile(r"^\s*(?:\([A-Za-z0-9]{1,4}\)\s*)+$")

# Where a designation is DECLARED in section text: at the start of the text, after a
# newline, or after sentence-ending punctuation - because the CFR runs paragraphs on
# within a single block as often as it breaks them onto their own line. `(a)` inside
# prose - "as described in (a)" - is a cross-reference, not a declaration, and counting
# it would invent paragraphs the instruction never named.
_DECLARED = re.compile(
    r"(?:\A|(?<=\n)|(?<=[.;:])\s)\s*((?:\([A-Za-z0-9]{1,4}\)\s*)+)")


class ResolveError(RuntimeError):
    """Raised instead of `assert`, which `python -O` strips."""


# ============================================================ designations

def parse_designation(designation: str | None) -> list[str]:
    """`(b)(4)(i)(A)` -> `["b", "4", "i", "A"]`. Golden R-A.

    Refuses anything that is not a parenthesised path. A bare `b4iA` is not a
    designation, and guessing at one would invent a target the instruction never
    named — which is the failure mode this tool exists to catch, not to commit.
    """
    if designation is None or not str(designation).strip():
        return []
    text = str(designation)
    if not _DESIG_WHOLE.match(text):
        raise ResolveError(
            f"{designation!r} is not a parenthesised designation path. This is refused "
            "rather than guessed: inventing a target is the defect being looked for.")
    return [m.group(1) for m in _DESIG_GROUP.finditer(text)]


def _canonical(path: list[str]) -> str:
    return "".join(f"({p})" for p in path)


def declared_designations(text: str) -> list[tuple[str, int]]:
    """Every designation DECLARED in the text, with its offset, in document order.

    Returns canonical strings, e.g. `("(b)(1)", 42)`. A designation appearing inside
    prose is not a declaration and is not returned.
    """
    out = []
    for m in _DECLARED.finditer(text):
        path = [g.group(1) for g in _DESIG_GROUP.finditer(m.group(1))]
        if path:
            out.append((_canonical(path), m.start(1)))
    return out


def designation_state(text: str, designation: str | None) -> dict:
    """Does this designation exist, and what are its siblings? Pure. Golden R-B.

    `siblings` is returned **even when the designation does not exist**, and that is
    the point of the field: §9's hard cases are "revising a definition that did not
    exist" and "adding an entry that already exists", and both are answered by what
    surrounds the target rather than by the target alone.
    """
    declared = declared_designations(text)
    path = parse_designation(designation)
    if not path:
        # Nothing was asked. NULL, not False - False would assert absence.
        depth = 1
        siblings = sorted({d for d, _ in declared
                           if len(_DESIG_GROUP.findall(d)) == depth})
        return {"designation": None, "designation_exists": None,
                "designation_path": [], "siblings": siblings,
                "designation_offset": None, "declared_count": len(declared)}

    canonical = _canonical(path)
    depth = len(path)
    offset = next((o for d, o in declared if d == canonical), None)

    # SIBLINGS = the deepest level ON THE PATH TO THE TARGET that actually exists.
    # Golden R-B asks for ["(a)", "(b)"] when `(b)(1)` is queried and no depth-2
    # designations are declared, and that is the useful answer rather than an empty
    # list: it says "(b) exists, it has no numbered children, and here is what does
    # exist at that level". An empty list would say only "no" - which is exactly the
    # answer a pure quoted-string matcher already gives, and section 6 adopted this
    # tool because that answer is not enough on ~80% of the pool.
    siblings: list[str] = []
    for d in range(depth, 0, -1):
        prefix = _canonical(path[:d - 1]) if d > 1 else None
        at_level = sorted({
            x for x, _ in declared
            if len(_DESIG_GROUP.findall(x)) == d
            and (prefix is None or x.startswith(prefix))
        })
        if at_level:
            siblings = at_level
            break
    return {"designation": canonical,
            "designation_exists": offset is not None,
            "designation_path": path,
            "siblings": siblings,
            "designation_offset": offset,
            "declared_count": len(declared)}


# ============================================================ anchor matching

def _map_normalised(text: str, keep) -> tuple[str, list[int]]:
    """Build a normalised string and the index of each of its characters in the
    ORIGINAL. The map is what makes `char_offset` honest at every level."""
    buf, idx = [], []
    for i, ch in enumerate(text):
        if keep(ch):
            buf.append(ch)
            idx.append(i)
    return "".join(buf), idx


def _collapse_ws(text: str) -> tuple[str, list[int]]:
    """Runs of whitespace become a single space. Each output character records the
    index of the original character it came from."""
    buf, idx = [], []
    prev_ws = False
    for i, ch in enumerate(text):
        if ch.isspace():
            if not prev_ws:
                buf.append(" ")
                idx.append(i)
            prev_ws = True
        else:
            buf.append(ch)
            idx.append(i)
            prev_ws = False
    return "".join(buf), idx


def _alnum_only(text: str) -> tuple[str, list[int]]:
    """Letters and digits only. **Case is preserved** — see R-C4."""
    return _map_normalised(text, lambda c: c.isalnum())


def find_anchor(text: str, quoted_text: str | None) -> dict:
    """Try the three declared levels in order; report the first that matches.

    Returns `{found, level, char_offset, matched_span, normalised_query}`.
    `char_offset` indexes the CALLER's string at every level (golden R-D).
    """
    if quoted_text is None or quoted_text == "":
        return {"found": False, "level": LEVEL_NONE, "char_offset": None,
                "matched_span": None, "levels_tried": []}

    tried = []

    # 1. exact
    tried.append("exact")
    pos = text.find(quoted_text)
    if pos != -1:
        return {"found": True, "level": "exact", "char_offset": pos,
                "matched_span": text[pos:pos + len(quoted_text)],
                "levels_tried": tried}

    # 2. whitespace-collapsed - on BOTH sides, and the query is stripped, because a
    #    quoted anchor lifted out of XML routinely carries leading or trailing space
    #    that the codified text does not have.
    tried.append("whitespace-collapsed")
    norm_text, idx = _collapse_ws(text)
    norm_query, _ = _collapse_ws(quoted_text)
    nq = norm_query.strip()
    if nq:
        pos = norm_text.find(nq)
        if pos != -1:
            start = idx[pos]
            end = idx[pos + len(nq) - 1] + 1
            return {"found": True, "level": "whitespace-collapsed",
                    "char_offset": start, "matched_span": text[start:end],
                    "levels_tried": tried}

    # 3. alphanumeric-only - punctuation and whitespace dropped, CASE PRESERVED
    tried.append("alphanumeric-only")
    an_text, aidx = _alnum_only(text)
    an_query, _ = _alnum_only(quoted_text)
    if an_query:
        pos = an_text.find(an_query)
        if pos != -1:
            start = aidx[pos]
            end = aidx[pos + len(an_query) - 1] + 1
            return {"found": True, "level": "alphanumeric-only",
                    "char_offset": start, "matched_span": text[start:end],
                    "levels_tried": tried}

    return {"found": False, "level": LEVEL_NONE, "char_offset": None,
            "matched_span": None, "levels_tried": tried}


# ============================================================ the tool

def cfr_resolve(title, part, section, as_of_date, text,
                quoted_text=None, designation=None) -> dict:
    """`CONTEXT.md` §6's capability 1. Pure: no network, no clock, no randomness.

    `text` is the frozen point-in-time section text the caller supplies; `as_of_date`
    is echoed so the trace records WHICH text was resolved against. This function
    fetches nothing — the corpus is frozen and a resolver that reached for the network
    could not be replayed offline (`plan.md` CH-11's Tier-1 replay).

    **Designation state is computed FIRST and unconditionally**, then the anchor.
    `found` and `designation_exists` are independent fields; neither is derived from
    the other, because collapsing them is how a partial read becomes a confident wrong
    answer (§6, F2).
    """
    if text is None:
        raise ResolveError("cfr_resolve needs the section text; it fetches nothing")

    state = designation_state(text, designation)       # FIRST - §6 fixes the order
    anchor = find_anchor(text, quoted_text)            # second

    if anchor["found"]:
        s, span = anchor["char_offset"], anchor["matched_span"]
        if text[s:s + len(span)] != span:
            raise ResolveError(
                "char_offset does not index the caller's own string; the level "
                "mapping is wrong and the offset would point into a document that "
                "does not exist")

    return {
        # echoed so a resolution_trace says what it resolved against (golden R-G)
        "title": str(title), "part": str(part), "section": str(section),
        "as_of_date": as_of_date,
        # the anchor half
        "found": anchor["found"],
        "level": anchor["level"],
        "char_offset": anchor["char_offset"],
        "matched_span": anchor["matched_span"],
        "levels_tried": anchor["levels_tried"],
        "quoted_text": quoted_text,
        # the designation half - computed first, reported apart
        "designation": state["designation"],
        "designation_exists": state["designation_exists"],
        "designation_path": state["designation_path"],
        "designation_offset": state["designation_offset"],
        "siblings": state["siblings"],
        "declared_designations": state["declared_count"],
        "normalisation_levels_declared": list(LEVELS),
    }
