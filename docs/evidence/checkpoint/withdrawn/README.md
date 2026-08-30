# WITHDRAWN — the first CHECKPOINT run

**These numbers are wrong and they are kept rather than deleted.**

They were produced at `7595562` against an eval set that the CH-03 adversarial review
then failed: `docs/reviews/REVIEW_CH-03.md` finding **F1**. The negative in each pair
was chosen as the sorted-FIRST count-matched sibling, so negatives sat systematically
earlier in section order than their positives, and **a label-blind script reading only
`frdoc` and `section` scored 0.8158 on the primary metric** — beating `B0-agent` by
17 pp with no model, no CFR text and no instruction text.

The withdrawn figures were:

| | |
|---|---|
| B0 | 0.5263 |
| B0-agent | 0.6447 |
| gap | +11.8 pp |
| McNemar exact p | 0.1221 |
| n | 76 (38 pairs) |
| branch | AMBER |

**They are preserved because withdrawing a number quietly is the failure this project
exists to expose.** The live result is one directory up, computed on the corrected
eval set (41 pairs / n = 82) after F1 and F2 were fixed and the probe was shown to
flip: the same label-blind attack falls to 0.5610, and the ordering bias goes from
36/50 (exact p = 0.0026) to 25/50 (exact p = 1.0000).

*(An earlier version of this note quoted "32/38, p = 0.000024". That figure was
itself withdrawn at the round-2 review - it came from an uncommitted snippet that
reconstructed the pairing instead of running the rule. See
`docs/evidence/ch03-evalset/ordering_bias.py`.)*

Nothing here should be quoted as a result. It is an audit trail.
