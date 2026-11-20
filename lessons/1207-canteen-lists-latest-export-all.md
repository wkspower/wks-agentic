# L1207 — The canteen's sales page lists the latest 200 sales and an account's page its latest 200 sales and its latest 200 top-ups and pay-outs, each saying how many there are; accounts are searched by name, class or card and show the first 200 matches; the menu is shown whole; `/export.json` holds everything

## Reason
A canteen makes hundreds of sales a day; a page that lists them all is
slow by the second week. Each long list shows a bounded part and says how
many there are in all, so nobody takes the part for the whole. Accounts
are found by typing part of a name, a class or a card number, without
regard to capitals. The menu is a few dozen items and is shown whole, as
is the till. Everything ever recorded stays in `/export.json`, which is
also what the cases read.

## Source
The person, run 012, 2026-11-20: one typed word, "Accepted", to fifteen
questions asked in one round before building, each with a recommendation
(answer 13). They saw the recommendations as one or a few lines each; they
have not read this file. The account's page and the menu shown whole are the
builder's.

## What would be a regression
A list that grows without bound; a list cut short that does not say how
many there are; something recorded that is missing from `/export.json`.
