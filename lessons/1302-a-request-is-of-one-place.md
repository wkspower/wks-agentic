# L1302 — A request is of one active place, an apartment or a common area, and says its category, priority, description, reporter and whether staff may enter; a second request for the place is taken, and the place's page shows its open ones above the form

## Reason
A request with no place cannot be walked to, and one with a free-text place
cannot be listed with its neighbours. So a request belongs to exactly one
row of the register of places: an apartment (number and floor) or a common
area (a name such as Lobby, Lift, Roof).

Every request says: a category from a fixed list (plumbing, electrical,
heating, appliance, doors and windows, pests, other); a priority (urgent,
normal, low); a description; the name and phone of who reported it, typed
on the request; and "may enter when nobody is home", yes or no. None of the
choices is made in advance for the person, and one left out is refused, not
assumed: "may enter" assumed yes is a worker in someone's home uninvited.

The same tap is reported twice, by two people in the household. Refusing
the second would lose a real second fault, so it is taken; what protects
against the duplicate is that the form for a new request is on the place's
page, under that place's open requests.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answers 4, 5, 6 and 12).
The builder's: the form is only on the place's page. The person had not
seen that when it was built.

## What would be a regression
A request stored with no place, with a place that does not exist or is
inactive, with a category or priority outside its list, or without an
answer to "may enter"; a second request for a place refused; a place's page
whose form comes before its open requests, or that does not show them.
