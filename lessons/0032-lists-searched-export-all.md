# L0032 — The catalogue and the borrowers are searched and show the first 200 matches, saying how many there are; loans out and overdue are shown in full, returned loans the latest 200; `/export.json` holds everything

## Reason
A school library has thousands of titles and hundreds of borrowers; nobody
reads such a list, they search it. The search box looks in title, author,
ISBN and shelf mark, or in name and class, without regard to capitals. A
page shows at most 200 rows and always says how many matched, so that a cut
list is never taken for the whole (the reasoning of L0021). Loans out and
overdue loans are the work still to do and are never cut; the loans page is
searched by copy number, title or borrower. The whole record is in
`/export.json`.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answer 12).

## What would be a regression
More than 200 titles, borrowers or returned loans on one page, a page silent
about rows it does not show, a search that returns rows that do not match,
an open loan missing from the loans page, or a row missing from
`/export.json`.
