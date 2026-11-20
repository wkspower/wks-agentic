# L1303 — A request is open, in progress, done or cancelled; done and cancelled can be reopened; every change is kept with its day and its note, and none is removed

## Reason
The states a request moves through: open when reported; in progress when
work starts; done or cancelled from either; and from done or cancelled back
to open when the fault returns or the cancelling was a mistake. Nothing
else: starting what is started, closing what is closed and reopening what
is open are refused and change nothing.

"When was this reported, who was told, when was it closed, why was it
reopened" is what the building is asked months later. So every change is
one row of the request's history with the day the server gave it and a note
if one was typed: reported, started, done, cancelled, reopened, assigned,
corrected, and a note on its own. A reopened request loses its closing day
and keeps its history.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answer 7).

## What would be a regression
A change of state the list above does not have accepted; a change with no
row in the history, or with its note lost; a history row changed or gone;
a closed request that cannot be reopened, or a reopened one that still has
a closing day.
