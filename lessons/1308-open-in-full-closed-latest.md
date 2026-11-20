# L1308 — Open and in-progress requests are listed in full, urgent first and then oldest; done and cancelled show the latest 200 and say how many; a search shows the first 200 matches and says how many; `/export.json` holds everything

## Reason
What is open is the day's work and must never be cut: a request off the
bottom of the page is a request nobody does. It is ordered by what to do
first: urgent, normal, low, and within each the oldest report first. What
is closed only grows; the page shows the latest 200 by closing day and says
how many there are. A search by words, place, category and state looks in
every request and shows the first 200 matches, newest first, saying how
many matched. Everything, with every history row, is in `/export.json`.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answer 13).

## What would be a regression
An open request missing from the list, or the list in another order; a
closed list that shows more than 200 rows or does not say the count; a
search that hides its count; a request or history row missing from the
export.
