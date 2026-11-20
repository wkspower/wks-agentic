# The lessons that are not `always` in force

One line per lesson, in the form `CLAUDE.md` describes. No session reads this
file whole: a hook gives each session, at its start, the lines in force for
the product in `product/`, or with no product every label and its lines
(L0041). `./check --lessons LABEL` prints the lines a label brings.

- **L0005** [pet shop] The pet shop system is for staff: products and stock, customers and their pets, counter sales, grooming appointments. · prose: whether a feature is inside the scope is a reader's judgement
- **L0006** [python stdlib and sqlite on localhost] The web app on localhost is the only way in, on Python's standard library and one SQLite file.
- **L0007** [local web server] A request from another site, or to another host name, is refused.
- **L0008** [money] Money is whole cents, and every input has a stated bound.
- **L0009** [pet shop] A sale beyond stock is refused whole, stock never goes below zero, and low stock is listed.
- **L0010** [pet shop] A sale records its method and the amount the server computed; it is never edited, only voided whole, once.
- **L0011** [pet shop] Grooming has one groomer and one-hour slots: an appointment belongs to a pet, and a taken slot is refused.
- **L0012** [web pages] What a person does in the forms is checked in a real browser, and a missing browser fails.
- **L0014** [web pages] Every example a form shows is a value that form accepts.
- **L0016** [pet shop] Voiding a sale asks first, on a second page that shows the sale; no page voids on one click.
- **L0017** [pet shop] Customers and pets can be corrected, and nothing is removed.
- **L0020** [pet shop] Cancelling an appointment is one click on the list: no question page, and opening an address never cancels.
- **L0021** [pet shop] The sales page lists the latest 200 sales and says how many there are; appointments before today are on no page; `/export.json` holds everything.
- **L0025** [pet shop] The pet shop's prices include tax, and its inputs are refused outside the table of bounds in the lesson.
- **L0026** [web pages] On a narrow screen a list is shown as stacked cards, not as a table: nothing scrolls sideways, is crushed or breaks in two, and each row's actions are in sight, from 320 px up with the longest names allowed.
- **L0027** [school library] The school library system is for library staff at one desk: a catalogue of titles and their numbered copies, borrowers, loans, returns, renewals and the overdue list. · prose: whether a feature is inside the scope is a reader's judgement
- **L0028** [school library] A loan is of one numbered copy to one borrower: a copy that is out, lost or withdrawn is refused, and so is a borrower who has left or holds 3 books as a pupil, 10 as staff.
- **L0029** [school library] The server sets every date: due 14 days after lending, renewed at most twice to 14 days from today, and overdue loans are listed by class.
- **L0030** [school library] Returning a book is one click on the list: no question page, opening an address never returns, and a loan is never edited or removed.
- **L0031** [school library] Titles and borrowers can be corrected and nothing is removed: a copy is marked lost or withdrawn and back, lost while it is out ends its loan that day as lost, a borrower who has left is marked so.
- **L0032** [school library] The catalogue and the borrowers are searched and show the first 200 matches, saying how many; loans out and overdue are shown in full, loans that ended (returned or lost) the latest 200; `/export.json` holds everything.
- **L0033** [school library] The school library's inputs are refused outside the table of bounds in the lesson.
- **L0035** [web pages] After a refusal, going back shows the form with what was typed, except a field that is scanned into, which comes back empty; the refusal page promises only what holds.
- **L0036** [school library] Classes are compared without regard to capitals: "7b" and "7B" are one class on the overdue list and in search, shown under the spelling most of its borrowers have.
- **L0042** [school library] Where the library's lists are tables they fit their box with ordinary names: no text of a row is under the column of buttons held in sight.
- **L1201** [school canteen] The canteen till is for canteen staff at one till: a menu, counter sales in cash or from a prepaid balance, accounts of pupils and staff with top-ups and pay-outs, and the day's totals. · prose: whether a feature is inside the scope is a reader's judgement
- **L1202** [school canteen] A canteen sale is of menu items at the menu's prices, paid whole in cash or whole from one account's balance: the server computes the total and the change, and a sold-out item, cash short of the total, or a balance short of it refuses the whole sale.
- **L1203** [school canteen] A canteen balance is what its records add up to: top-ups in cash, less pay-outs in cash and sales paid from it, never below zero, never topped up above 1,000.00, and no top-up or sale for an account that has left.
- **L1204** [school canteen] A canteen sale or top-up is never edited, only voided whole, once, on a second page that shows it: a sale paid from a balance returns its money, and a top-up is voided only while the balance still covers it.
- **L1205** [school canteen] The canteen's items and accounts are corrected and never removed: a sale keeps the names and prices of its moment, an item is marked sold out and back with one click, an account is marked as having left, and a card number belongs to one account.
- **L1206** [school canteen] The server sets every canteen date, and the page of a day adds up what happened that day: sales by method, items sold, top-ups, pay-outs, voids, and the cash expected in the drawer, which is cash sales plus top-ups less pay-outs less what was voided that day.
- **L1207** [school canteen] The canteen's sales page lists the latest 200 sales and an account's page its latest 200 sales and its latest 200 top-ups and pay-outs, each saying how many there are; accounts are searched by name, class or card and show the first 200 matches; the menu is shown whole; `/export.json` holds everything.
- **L1208** [school canteen] The canteen's prices include tax, and its inputs are refused outside the table of bounds in the lesson.
