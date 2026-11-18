# Record of customers

**State.** Built and standing. Verdict passes; number 753.

**How it stood.** Two builds were made by two agents, neither seeing the
other, each given only this unit's document, the pet shop's rule 3 and
`measure/check`. The judge compared them by the measure and let the
alternative (753) over the candidate (855) stand (change `295a2a1`; `judge/stands/petshop/customers.tsv`).
Attempts used: 1 of 2.

**Audit** (`petshop/audit/customers/check`, 97 cases from the document alone):
both builds pass every case. Of the 22 planted wrong builds, 21 also fail the audit; the one the audit passes imports a network module.

**Round before first effect.** Nothing asked of the pet shop. The builders
decided what the document left open, and both decided alike: `get` with an id that is not a string raises `KeyError`; `find` with a text that is not a string returns nothing; case is ignored with `casefold`; a `str` subclass is accepted as a name.

**Tried and rejected.** The candidate (855): a list of names scanned on every `get`; same behaviour, larger.

**Limit.** This stand was made before the judge kept one file per unit; it
cannot be undone by reverting its change alone.

**Due next.** The open points above belong in the document, as rules given
by the pet shop, with cases in the measure (principle 6).
