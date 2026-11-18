# Record of stock

**State.** Built and standing. Verdict passes; number 862.

**How it stood.** Two builds were made by two agents, neither seeing the
other, each given only this unit's document, the pet shop's rule 3 and
`measure/check`. The judge compared them by the measure and let the
alternative (862) over the candidate (878) stand (change `52c251d`; `judge/stands/petshop/stock.tsv`).
Attempts used: 1 of 2.

**Audit** (`petshop/audit/stock/check`, 60 cases from the document alone):
both builds pass every case. Of the 17 planted wrong builds, 16 also fail the audit; the one the audit passes imports a network module, which rule 3 forbids and the audit does not look for.

**Round before first effect.** Nothing asked of the pet shop. The builders
decided what the document left open, and both decided alike: `on_hand` returns 0 for any id that is not a non-empty string; an `int` subclass other than `bool` is accepted as a quantity.

**Tried and rejected.** The candidate (878): same behaviour, larger.

**Limit.** This stand was made before the judge kept one file per unit; it
cannot be undone by reverting its change alone.

**Due next.** The open points above belong in the document, as rules given
by the pet shop, with cases in the measure (principle 6).
