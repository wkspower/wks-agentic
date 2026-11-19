# Run 001 — pet shop

- **Prompt:** `prompts/001-pet-shop.md` ("Build a system for a pet shop.")
- **Branch:** `run/001-pet-shop`, 2026-11-19.

## Questions

One round, 14 questions, each with a recommendation, asked before anything
was built. Answered with a single "ok". No question was asked after that.
How long the round waited is not visible from inside the session.

## Lessons added: 11 (L0005 to L0015)

| | With a case | Prose only |
|---|---|---|
| From the person's answers | L0006 to L0012 (7) | L0005 scope, L0013 done means |
| From defects found by hand | L0014, L0015 (2) | |

Case before fix, by commit:

- `aa4f428` lessons L0005 to L0013 and seven cases, all failing (no product).
- `acd9f13` the product; the seven pass. One of them (L0008) failed on the
  first build for a real reason: 21 lines of one product counted as one.
- `40081d6` L0014 and L0015 with cases failing on the product as it stood.
- `c5acf21` the fixes.
- `bf48fbf` L0015 widened, failing: its first fix passed the case and was
  wrong to the eye (every word could break, so prices read "129.9 / 0").
- the commit after it: the second fix.

Every case over the product also runs wrong variants, 23 in all, each one
piece of text replaced in a scratch copy (L0002). One variant I wrote was
refused by this for not being wrong: a `nowrap` rule that changed nothing.
It was replaced by the real wrong build, the first fix of L0015.

## Check at the end

    lessons 15 · with a case 11 · prose only 4 · cases run 11 · CLAUDE.md 5285 bytes

`./check --selftest`: control accepted, refused 11 of 11 wrong trees.

## Size

Product 624 lines in one file. Cases 555 lines, their shared helpers 232,
lesson files 190. No planted full copies.

## Time and agents

About 13 minutes of work by the commit times (19:59 to 20:12), not counting
the wait for the answer. No sub-agents.

## Used by hand (Chromium 157, 1100 px and 390 px, light and dark)

Sale of two products, a sale submitted with no payment method (the browser
stops it), a sale beyond stock and Back to the form (what was typed is kept),
stock adjustment, product edit, booking for today and the first page after
it, void. A form posted to the shop from a page on another port, from
`localhost` on another port and from a `data:` page: all three refused, and
no customer created.

## Not verified

- The bounds in L0008 and the opening hours in L0011 are my numbers. The
  person accepted "sensible limits" and has not seen them.
- Only Chromium. The cross-site refusal depends on headers the browser
  sends; Firefox and Safari were not tried. The test from a real foreign
  page was done by hand and is not a case.
- Two people or two tabs posting at the same moment. There is a lock; no
  case races it.
- Loss of power mid-write, and restoring from a copied database file.
- Anyone logged in to the same machine can open the shop. That follows from
  "localhost, no login" and was not tested as a risk.
- Reading the pages with a screen reader.

## Left out, and not asked

- Void has no "are you sure". It cannot be undone, only seen.
- Customers, pets and products cannot be removed or (except products)
  edited. Appointments before today are in `/export.json` and on no page.
- "Today" is the machine's clock.
