# Pages of the web interface

Part of declaration 2 of [`unit.md`](unit.md). Everything here is checked.

## Running

`python3 web.py --state FILE [--port N]` listens on `127.0.0.1` only, on port N (default 8000; 0 means any free port). Once ready it prints one line `http://127.0.0.1:PORT/` on stdout and serves until killed. The state file is the shop's: one JSON object holding the four units' states under `catalog`, `stock`, `customers`, `sales`. It is read at every request, so a change made by `shop.py` shows on the next page. It is created on the first successful change when missing, and always replaced whole (written beside itself, then renamed). A GET never changes it.

## Every page

An HTML5 document with `lang`, a `<title>` of the form `PAGE · Pet shop`, exactly one `<h1>`, a `<main>`, and a `<nav>` linking to `/`, `/catalog`, `/customers`, `/sell` and `/sales`, in which the link of the current section carries `aria-current="page"`. Every text taken from the state is HTML-escaped. Nothing is fetched from anywhere but this server, and everything works with scripts disabled.

Money is shown as cents ÷ 100 with exactly two decimals and commas between thousands (`26050` → `260.50`, `123456789` → `1,234,567.89`). Money is entered as digits with an optional point and one or two decimals (`3`, `3.5`, `3.50`); anything else is refused. Quantities are entered as digits only.

## Pages

- **`GET /`** (Overview). Elements with `id` `count-items`, `count-customers`, `count-sales` (the counts) and `takings` (money). A table `id="out-of-stock"` with one `<tr data-id="ITEM_ID">` per item with none on hand, in id order.
- **`GET /catalog`**. A table `id="items"` with one `<tr data-id="ITEM_ID">` per item in id order, holding cells of class `name`, `kind`, `price` (money) and `on-hand`. Forms, each `method="post"`:
  - `action="/catalog/add"`: text inputs `id`, `name`, `price` and a select `kind` (`animal`, `product`).
  - `action="/catalog/price"`: `id`, `price`.
  - `action="/stock/receive"` and `action="/stock/remove"`: `id`, `quantity`.
- **`GET /customers`**. A form `method="get"` with a text input `q`. A table `id="customers"` with one `<tr data-id="CUSTOMER_ID">` per customer whose name contains `q` ignoring case (all when `q` is empty or absent), in order of registration, holding a cell of class `name`. A form `action="/customers/register"` with a text input `name`.
- **`GET /sell`**. One form `action="/sell"`: a select `customer` whose options have the customer ids as values, and for every item in id order a number input named `qty-ITEM_ID`, shown with the item's name, price and quantity on hand.
- **`GET /sales`**. A table `id="sales"` with one `<tr data-id="SALE_ID">` per sale, newest first, holding cells of class `customer` (the customer's name) and `total` (money), each row linking to the sale. An element `id="takings"` (money).
- **`GET /sales/SALE_ID`**. Elements `id="sale-id"`, `id="customer"` (the name) and `id="total"` (money), and a table `id="lines"` with one `<tr data-id="ITEM_ID">` per line, holding cells of class `name`, `quantity`, `unit-price` and `line-total`. An unknown sale: status 404.

## Changes

Each form posts `application/x-www-form-urlencoded` in UTF-8. Field `id` in `/catalog/price`, `/stock/receive` and `/stock/remove` is the item id, however the form offers it.

- **Done**: the state is saved and the response is `303` with `Location` back to the page the form is on (for `/sell`: the new sale's page). The page then shown has exactly one element with `role="status"` saying what was done.
- **`POST /sell`** makes one sale with one line per item whose quantity is 1 or more, in id order; empty and `0` mean none.
- **Refused**: anything a unit refuses, an item unknown to the catalog, an unknown customer, a number not written as above, a missing field, or a sale with no line. The response is `400` and shows the page the form is on, with exactly one element `role="alert"` giving the reason and the submitted values still in the form's fields. The state file is byte-identical.
- An unknown path: `404`, a page with the `<nav>`. A known path with another method: `405`.

## Rules of a professional interface

Hard, on every page above, in a browser 390, 768 and 1280 px wide, with a shop that has items, customers and sales:

- The page never scrolls sideways; a wide table scrolls inside its own container.
- Every form control has a label a screen reader announces.
- Everything can be reached and operated with the keyboard alone, and the focused control is visibly marked.
- No error in the browser console and no request to another host.

Graded: each occurrence is one defect in the number of declaration 5.

- A text whose contrast with its background is below 4.5 to 1.
- A link, button or form control smaller than 44 by 44 CSS px at 390 px wide (links inside running text excepted).
- A text smaller than 14 px.
- A line of running text longer than 90 characters at 1280 px wide.
