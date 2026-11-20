# L1201 — The canteen till is for canteen staff at one till: a menu, counter sales in cash or from a prepaid balance, accounts of pupils and staff with top-ups and pay-outs, and the day's totals

## Reason
"A point-of-sale system for a school canteen" can mean a till, a parents'
portal or a stock system. Naming what is in and what is out keeps a rebuild
the same size. In: what the line above says. Out: any login; anything a
pupil or a parent touches; card terminals and online payment; credit;
counting stock; printed receipts; daily spending limits, allergy warnings,
free-meal entitlement, parental restrictions; an opening float and counting
the drawer; import of the school roll. English pages, amounts with two
decimals and no currency symbol, dates as YYYY-MM-DD.

`--sample` loads a small menu and a few accounts into an empty file.
`--today YYYY-MM-DD` starts the till on another day, so that a case or a
person can see a second day; every page says so while it is set.

## Source
The person, run 012, 2026-11-20: one typed word, "Accepted", to fifteen
questions asked in one round before building, each with a recommendation
(answers 1, 3, 6, 7, 11, 12 and 15). They saw the recommendations as one or a
few lines each; they have not read this file.

## What would be a regression
A rebuild that adds one of the things named as out, or drops one named as
in, without the person saying so.
