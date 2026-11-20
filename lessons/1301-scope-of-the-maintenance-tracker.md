# L1301 — The maintenance tracker is for the staff of one apartment building at one desk: places, requests and their history, the workers who take them, and the overdue list

## Reason
"A maintenance request tracker for an apartment building" can mean a desk
program or a portal for every tenant. Naming what is in and what is out
keeps a rebuild the same size. In: what the line above says. Tenants report
by phone or in person and staff record it. Out: a login, a page for tenants,
a register of tenants, costs or invoices or any money, photos or other
attachments, email or SMS notices, recurring preventive maintenance.
English interface, dates as YYYY-MM-DD, and "today" is the machine's clock.
`--sample` fills an empty file with a 24-apartment building.

`--today YYYY-MM-DD` starts the tracker on another day, so that a person
and the cases can see a request fall overdue; every page says so while it
is set.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answers 1, 3, 5, 15 and 16).

## What would be a regression
A rebuild that adds one of the things named as out, or drops one named as
in, without the person saying so.
