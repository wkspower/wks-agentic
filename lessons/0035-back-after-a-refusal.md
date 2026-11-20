# L0035 — After a refusal, going back shows the form with what was typed still in it, except a field that is scanned into, which comes back empty; the refusal page promises only what holds

## Reason
A refusal sends the person back to the form. If the form comes back empty,
a title with five fields is typed again because of one wrong digit. So the
pages are served in a way that lets the browser keep what was typed.

A field that takes a scan is the exception. A scanner types into whatever
has the focus and adds to what is there: a field that came back holding "1"
would read the next book, 17, as 117. That field comes back empty, with the
focus in it.

What the refusal page says about this has to be true for the form it
answers. A sentence shared by every refusal is true for some of them only.

## Source
A defect found in run 006, 2026-11-20, by the agent driving the library by
script and reading what came back (L0013). Every refusal ended "Use your
browser's Back button to return to the form; what you typed is still
there." After a refused loan the copy field was empty. The same sentence
stood on the page for an address that does not exist, which has no form.
All 19 cases had passed. That the scan field comes back empty is the
builder's choice between the two ways of making the sentence true; the
person has not seen it.

## What would be a regression
A form that comes back empty after a refusal; a scanned field that comes
back with the last scan in it; a refusal page that says the typed values
are kept where they are not.

The case measures Chromium only. How another browser restores a form is its
own affair, and none was tried.

No real scanner has been tried (noted in run 007). The reason above is how a
scanner is said to behave: it types the digits and Enter into the field that
has the focus. The case and the agent typed digits and Enter in its place.
