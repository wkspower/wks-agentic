# Run 004 — pet shop, rebuilt with no history

- **Prompt:** `prompts/001-pet-shop.md` ("Build a system for a pet shop.")
- **Branch:** `run/004-rebuild-no-history`, 2026-11-19. Started from one
  commit with no `product/` and no history. No other branch was fetched or
  read; the product was written from `CLAUDE.md`, the lessons, the cases and
  the two case libraries.

## Questions

One round, 3 questions, each with a recommendation, asked before anything
was built (run 001: 14, run 002: 4). None repeated a question of an earlier
run; all three were items the handoff or run 002 listed as not decided or
not asked. All three recommendations were taken. No question after that.
How long the round waited is not visible from inside the session; the
worker was restarted once while it waited.

1. Should cancelling an appointment ask first, as void does? No, one click.
2. Can a pet move to another customer? No, it stays (L0017 as written).
3. Past appointments on no page and the latest 200 sales on the page: enough? Enough.

## Lessons added: 3 (L0020 to L0022), all with a case

| | With a case | Prose only |
|---|---|---|
| From the person's answers | L0020 cancel is one click, L0021 pages show recent, export all | |
| From a defect found by hand | L0022 row actions in sight | |

L0017 changed only in its Source: the person kept "a pet keeps its customer".

Case before fix, by commit:

- `6b694e0` L0020 and L0021 with their cases, failing (no product).
- `fe65312` the product. All 17 cases passed on their first run, the 15
  inherited ones without a change to any of them.
- `5de966e` L0022 with its case failing on the product as it stood.
- `bfdaccc` the fix.

## What the rebuild showed

- The 13 product cases of run 003 passed on a product whose author had
  never seen an earlier build. Nothing in the cases had to be read as a hint
  about the inside; what they fixed was the command line, the paths and
  form fields, the keys of `/export.json`, the status answers, and a few
  class names (`form.card`, `td.num`, `td.stock`) and texts ("Low stock",
  "only 1 in stock", "already taken", "voided").
- No recorded defect came back: examples are accepted (L0014), nothing
  scrolls sideways or breaks in two (L0015), no column is crushed (L0018),
  nothing is preselected (L0012).
- A new defect of the same family as L0015 and L0018 did appear, for the
  third run in a row: the narrow layout. Each fix so far has pushed the
  problem one step on: page scrolls, then words break, then columns crush,
  now the last column is out of sight. Found by eye in the screenshots.
- The half of L0021 about past appointments cannot be reached from the
  interface (a past date is refused), so it has no machine check. Its
  lesson says so.

## Check at the end

    lessons 22 · with a case 18 · prose only 4 · cases run 18 · CLAUDE.md 6963 bytes

`./check --selftest`: control accepted, refused 11 of 11 wrong trees. The
cases over the product run 36 wrong variants (run 003: 29); all refused
after their fault acted. L0019: 17 of 17 cases pass in a tree with no
product source. `./check` takes about 40 s.

## Size

Product 781 lines in one file (run 002: 768). Cases 1406 lines (run 003:
1177), shared helpers 330, lesson files 445 (380).

## Time and agents

About 16 minutes by the commit times (21:57 to 22:13), including the wait
for the answers. No sub-agents.

## Used by hand (Chromium 157; 1100 px light and 390 px dark, then 1100 px dark and 390 px light after the fix)

Driven by a script and looked at in screenshots, on the sample data: a sale
submitted with no payment method (the browser stops it); a sale of two
products beyond stock, refused with its reason, then Back (customer,
product, quantity and method still there), corrected and recorded; stock
adjustment "+10"; an adjustment of -1 at stock 0 (refused, with the figures);
a price typed "19,90" (refused, with the rule) and then "19.9"; a customer's
phone corrected; a booking for today and one for 2027; a past date typed in
(the browser stops it); an appointment cancelled in one click; the void
question opened and "Keep the sale" followed (not voided), then voided, then
the question opened again (no button). A form posted to the shop by a page
on another port, by `localhost` on another port and by a `data:` page: all
three answered 403 and no customer was created. The shop used through
`http://localhost`: works.

Changed after looking, without a lesson because it is taste and not a
defect: on the sale form every empty line read "None" with a grey "1"
beside it, which looked like six lines of one. Empty lines now read
"Product…" and only the first quantity shows an example.

## Not verified

- Only Chromium. The cross-site refusal depends on headers the browser
  sends; Firefox and Safari were not tried, and the test from a real foreign
  page is not a case.
- "By hand" is a script and my reading of screenshots. Nobody sat at it.
- That typed values survive Back after a refusal: seen in Chromium only.
  Pages are sent with `no-cache`, not `no-store`, to make that likelier
  elsewhere; not tried elsewhere.
- The column that stays in sight (L0022) uses `position: sticky` in a table
  cell. Seen in Chromium only; on a touch screen it was not tried at all.
- Two people or two tabs posting at the same moment. One lock and one
  transaction per request; no case races it.
- Loss of power mid-write, and restoring from a copied database file.
- Anyone logged in to the same machine can open the shop.
- Reading the pages with a screen reader.
- A void that would lift a product above 1,000,000 in stock is refused with
  a reason; no case covers it.
- Mechanical changes to this product's source, to see which wrong builds
  the cases let through (run 003 did it once on the older product).
- "Appointments before today are on no page" (L0021), as said above.

## Left out, and not asked

- A booking date has no stated upper bound in L0008's table. The product
  takes any real day from today to 9999-12-31.
- `/sales/new` shows 6 lines, and 20 through a link that does not carry
  over what was typed. The bound of 20 lines is the server's.
- "Today" is the machine's clock.
- `--db` defaults to `petshop.db` in the directory the shop is started from.
