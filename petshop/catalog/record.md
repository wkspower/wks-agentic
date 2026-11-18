# Record of catalog

**State.** Built and standing. Verdict passes (18 cases, each run plain and
after a JSON round trip; rules kept); number 1190.

**How it stood.** Two builds were made by two agents, neither seeing the
other, each given only this unit's document, the pet shop's rule 3 and
`measure/check` (never the planted builds, never the audit). The judge
compared them by the measure: candidate 1190, alternative 1264, nothing
existing. The candidate stands (`judge/stands.tsv`, change `e2d0575`).
Attempts used: 1 of 2. Undo was proven by `enforcer/undo e2d0575` when it stood; since the judge's next line it no longer applies (see the judge's record).

**Round before first effect.** Nothing asked of the pet shop. The builders
decided what the document left open, and both decided alike: an id that is
not a string is unknown to `get` and `set_price` (`KeyError`); a price must
be exactly an `int`; an unknown id is refused before an invalid price.

**Tried and rejected.** The alternative (1264): same behaviour, larger.

**Due next.** Change is due even though the verdict passes (principle 6):
the open points above belong in the document, as rules given by the pet
shop, so that no later builder decides them again.
