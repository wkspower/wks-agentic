# Record of sales

**State.** Built and standing. Verdict passes; number 1890.

**How it stood.** Two builds were made by two agents, neither seeing the
other, each given only this unit's document, the pet shop's rule 3 and
`measure/check`. The judge compared them by the measure and let the
candidate (1890) over the alternative (1909) stand (change `614c67b`; `judge/stands/petshop/sales.tsv`).
Attempts used: 1 of 2.

**Audit** (`petshop/audit/sales/check`, 75 cases from the document alone):
both builds pass every case. Of the 24 planted wrong builds, all 24 also fail the audit.

**Round before first effect.** Nothing asked of the pet shop. The builders
decided what the document left open, and both decided alike: `lines` that is not a sequence of pairs is refused with `ValueError`; item ids are not validated but handed to `price_of`; if `take` itself raises midway, earlier takes are not undone.

**Tried and rejected.** The alternative (1909): same behaviour, larger.

**Limit.** This stand was made before the judge kept one file per unit; it
cannot be undone by reverting its change alone.

**Due next.** The open points above belong in the document, as rules given
by the pet shop, with cases in the measure (principle 6).
