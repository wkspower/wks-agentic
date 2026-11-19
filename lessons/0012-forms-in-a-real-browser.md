# L0012 — What a person does in the forms is checked in a real browser, and a missing browser fails

## Reason
The cases over HTTP send the fields they choose. They cannot see that a form
sends different ones, that a control comes preselected, or that a refusal is
shown without its reason. Only loading the page and using it can. Nothing is
chosen for the person in advance on a form that records money or a booking.

## Source
The wizardly-cerf run, 2026-11-18: a customer was preselected on the sale
form and every check passed. The person, run 001, 2026-11-19 (answer 14).

## What would be a regression
The browser case skipping instead of failing when there is no browser, or a
select or radio on the sale or appointment form arriving with a choice made.
