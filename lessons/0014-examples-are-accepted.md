# L0014 — Every example a form shows is a value that form accepts

## Reason
The example in a field is the first thing a person types. A form that
refuses its own example teaches the person that the program is wrong about
itself. A placeholder is an example or it is not there; several are
separated by " or ".

## Source
A defect found using the app by hand, run 001, 2026-11-19: the stock
adjustment field showed "+10 or -2" and answered "+10" with "Adjustment must
be a whole number". All seven cases had passed. The case over HTTP for
bounds had only ever sent "5" and "-2".
Accepted by the person on 2026-11-19 (run 005), from a one-line summary of this lesson given in another session; the person has not read this file.

The case was made general in run 006, 2026-11-20, when the school library
chose this label; what it needs to know of a product is in `surface/` (L0024).

## What would be a regression
A placeholder whose text, typed as it stands, is refused; or a placeholder
used as a label instead of an example.
