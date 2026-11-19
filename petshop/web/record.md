# Record of web

**State.** Built and standing. Verdict passes (73 cases over HTTP, 150 in a
browser at 390, 768 and 1280 px); number 0.028550: no graded defect, 28,550
bytes, 604 lines.

**How it stood.** Two agents each wrote `web.py` on unchanged copies of the
four standing modules, neither seeing the other, each given the documents
and `measure/check`. Both passed every check with no graded defect; the
judge let the alternative (0.028550) stand over the candidate (0.037013)
(change `99522a8`; `judge/stands/petshop/web.tsv`; undo proven). Attempts
used: 1 of 2.

**Audit** (`petshop/audit/web/check`, 197 cases from the documents alone,
over HTTP): both builds pass every case. Of the 35 planted wrong builds, 29
also fail the audit; the 6 it passes have defects only a browser shows
(label, focus, sideways scroll, clipped table, foreign font, scripts
needed), which this audit does not open.

**Round before first effect.** Kind, scope and budget were asked of the
person by the root (Q19 to Q22). The builders decided what `pages.md` left
open, and both decided alike: the confirmation after a redirect is carried
as a code in the address and rebuilt from the state; a refused value that
is not on offer in a select is shown back as an extra option; `HEAD` and
every other method on a known path is 405; a `qty-` field for an unknown
item is refused only when it asks for 1 or more; a state file that cannot
be read gives a 500 page and nothing is written; top-level keys the
program does not know are kept on save.

**Tried and rejected.** The candidate (0.037013): the same behaviour and no
graded defect, with per-row shortcuts and extra columns, 8,463 bytes more.

**Limits.**
- The measure cannot tell the two designs apart except by size: the judge
  chose the smaller file, not the better-looking interface. Taste is not
  measured (declaration 5).
- One user at a time; requests are served one after another.

**Due next.** The open points above become sentences of `pages.md` with
cases (principle 6). A browser audit, since the HTTP audit cannot see 6 of
the 35 planted defects.
