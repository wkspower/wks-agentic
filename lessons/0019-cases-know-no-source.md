# L0019 — A wrong variant is a fault put at the product's interface when the case runs; no case names, reads or edits the product's source

## Reason
A case fixes whatever it mentions. A wrong variant written as one line of
the source replaced by another mentions that line, so the line has to be
there, and a rebuild is free only to write it again. What someone depends on
is what the product does at its surface: its command line, its pages and
forms, `/export.json`, the database file. Only that may be fixed.

So a wrong variant is a wrong shop made without touching the program: the
product, started the usual way, with one fault standing between it and the
case. Over HTTP the fault is a front that changes a request on its way in or
an answer on its way out, or sends requests of its own. In the browser it
changes the page after the product served it. Each fault is written from the
rule it breaks ("a sale beyond stock goes through"), not from the request the
case happens to send, and it must act while the case runs: a wrong variant
that was refused without ever acting has measured nothing (L0001).

## What this no longer proves
A one-line change to the real source gave a real wrong build, and the case
refusing it proved that the case reaches that line of that product. A fault
at the interface proves less: that the case sends something the rule forbids
or requires, and that it notices when the answer or the state is wrong. It
does not prove that a mistake inside the product would show itself the way
the fault shows it. Some faults cannot even be made real from outside: the
product will not hold a negative stock or two bookings in one slot, so those
faults accept what should be refused and leave the nearest state the product
allows.

What covers the gap cheaply is a run by hand, outside the cases: change the
source mechanically, run the cases, and read which changes pass. It names no
text in any case, so it pins nothing. Run 003 did it once with the 28
replacements the cases used to carry; `runs/003-variants-by-behaviour.md`
has the count.

## Source
Run 002, 2026-11-19: the product was rebuilt from nothing and its builder
wrote the new source to hold the 23 pieces of text the old wrong variants
named, so that they would still apply. The run record reported this as "not
one had to be rewritten". The cases were pinning about two dozen lines of
the program. The person's decision, 2026-11-19: no case names, reads or
edits the text of the product's source; every rule a case guards is still
shown something wrong, and refuses it.
Read as written and accepted by the person, 2026-11-19 (run 005).

Run 006, 2026-11-20: the case passed on a second product without taking
its source away, because it looked for the first product's file by name.
It now finds the product through `product/LABELS` and stops if any source
is left in its scratch tree (L0034).

## What would be a regression
A case that opens a file under `product/` as text, copies it, or changes it;
a wrong variant given as text to find and replace; a wrong variant counted
as refused when its fault never acted. The case runs every other case in a
tree whose `product/` holds compiled bytecode and no source. It does not
catch a case that reaches the source some other way than through the tree
it runs in.
