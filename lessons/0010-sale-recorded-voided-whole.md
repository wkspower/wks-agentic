# L0010 — A sale records its method and the amount the server computed; it is never edited, only voided whole, once

## Reason
The record of a sale is what the shop reconciles the till against. The
amount comes from the shop's prices at that moment, not from the form, and
stays as it was when prices change later. A mistake is corrected by voiding
the whole sale, which returns its stock once; the voided sale stays on record.

## Source
The person, run 001, 2026-11-19 (answers 8 and 9).
Read as written and accepted by the person, 2026-11-19 (run 005).

## What would be a regression
A total taken from the form, a method outside cash, card and other, a
finished sale whose lines or amount change, a second void that returns the
stock again, or a voided sale that disappears.
