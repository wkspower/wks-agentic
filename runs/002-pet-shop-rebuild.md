# Run 002 — pet shop, rebuilt

- **Prompt:** `prompts/001-pet-shop.md` ("Build a system for a pet shop.")
- **Branch:** `run/002-pet-shop-rebuild`, 2026-11-19. Started with no
  `product/`: the lessons and cases of run 001 were all there was.

## Questions

One round, 4 questions, each with a recommendation, asked before anything
was built (run 001: 14). None repeated a question of run 001; all four were
the items run 001 left under "Not yet decided" or "Left out, and not asked".
All four recommendations were taken. No question was asked after that. How
long the round waited is not visible from inside the session.

1. Keep the bounds of L0008? Kept.
2. Keep grooming 09:00 to 17:00 every day? Kept.
3. Should void ask first? Yes, on a second page.
4. Edit or remove customers and pets? Edit both, remove nothing.

## Lessons added: 3 (L0016 to L0018), all with a case

| | With a case | Prose only |
|---|---|---|
| From the person's answers | L0016 void asks first, L0017 corrected never removed | |
| From a defect found by hand | L0018 columns not crushed | |

L0008 and L0011 changed only in their Source: the numbers have now been seen
and kept by the person.

Case before fix, by commit:

- `12b44b8` L0016 and L0017 with their cases, and cases 0012, 0014 and 0015
  extended to the new pages; all failing (no product).
- `e57686e` the product. All 13 cases passed on the first run of `./check`.
- `7828ae8` L0018 with its case failing on the product as it stood.
- the commit after it: the fix.

## What the rebuild showed

- The nine product cases of run 001 passed on a product written from the
  lessons and the cases alone. Not one of their 23 wrong variants had to be
  rewritten: the new source was written to hold the text each one names,
  which the handoff had expected to be redone.
- The three changes to old cases (0012, 0014, 0015) all come from the
  person's answers 3 and 4, not from the rebuild.
- Neither defect of run 001 (L0014, L0015) came back. A new one of the same
  family as L0015 did: at 390 px the tables no longer pushed the page, but
  squeezed their columns to one word per line. The case of L0015 could not
  see it. Found by eye in the screenshots, now L0018.

## Check at the end

    lessons 18 · with a case 14 · prose only 4 · cases run 14 · CLAUDE.md 5921 bytes

`./check --selftest`: control accepted, refused 11 of 11 wrong trees. The
cases over the product run 28 wrong variants; all are refused.

## Size

Product 768 lines in one file (run 001: 624). Cases 832 lines, their shared
helpers 232, lesson files 314. No planted full copies.

## Time and agents

About 10 minutes by the commit times (20:46 to 20:56), not counting the wait
for the answers. No sub-agents.

## Used by hand (Chromium 157, 1100 px light and 390 px dark, then 390 px light and 1100 px dark after the fix)

Driven by a script and looked at in screenshots, on the sample data: a sale
submitted with no payment method (the browser stops it); a sale of two
products beyond stock, refused with its reason, then Back (product, quantity
and method still there), corrected and recorded; stock adjustment "+10";
product price edit; a customer's phone corrected; a booking for today and one
for 2027; a past date typed in (the browser stops it); the void question
opened and "Keep the sale" followed (not voided), then voided, then the
question opened again (no button). A form posted to the shop by a page on
another port, by `localhost` on another port and by a `data:` page: all three
answered 403 and no customer was created. The shop used through
`http://localhost`: works.

## Not verified

- Only Chromium. The cross-site refusal depends on headers the browser
  sends; Firefox and Safari were not tried, and the test from a real foreign
  page is not a case.
- "By hand" here is a script and my reading of screenshots. Nobody sat at it.
- That typed values survive Back after a refusal was seen in Chromium only;
  the pages are sent with `no-store`, and another browser may clear the form.
- Two people or two tabs posting at the same moment. One lock serialises
  requests; no case races it.
- Loss of power mid-write, and restoring from a copied database file.
- Anyone logged in to the same machine can open the shop.
- Reading the pages with a screen reader.
- A void that would lift a product above 1,000,000 in stock is refused with
  a reason; no case covers it.

## Left out, and not asked

- Cancelling an appointment is one click. It can be put right by booking
  the slot again, which is why it was not asked alongside void.
- A pet cannot be moved to another customer.
- Appointments before today are in `/export.json` and on no page.
- The sales page lists the latest 200; the rest are in `/export.json`.
- "Today" is the machine's clock.
