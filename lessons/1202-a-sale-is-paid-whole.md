# L1202 — A canteen sale is of menu items at the menu's prices, paid whole in cash or whole from one account's balance: the server computes the total and the change, and a sold-out item, cash short of the total, or a balance short of it refuses the whole sale

## Reason
The queue is long and the break is short, so a sale is one form: the
quantities, and then either the cash given or a card scanned. Which of the
two was filled says how it is paid; there is nothing to choose and nothing
chosen in advance. Both filled, or neither, is refused.

The total comes from the menu's prices at that moment, never from the
form. For cash the till needs the amount given, at least the total, and
records and shows the change. From a balance the whole total is taken, and
a balance that does not cover it refuses the sale and says the balance:
there is no credit and no part payment. A sale with a sold-out item, an
item that does not exist, or an account that has left or does not exist is
refused whole; nothing of it is recorded.

An account is named by its card number, scanned or typed, or by the till
being opened from the account's page.

## Source
The person, run 012, 2026-11-20: one typed word, "Accepted", to fifteen
questions asked in one round before building, each with a recommendation
(answers 3, 4, 6 and 7). They saw the recommendations as one or a few lines
each; they have not read this file. That the way of paying follows from which
field was filled, and that cash always needs the amount given, are the
builder's; the person has not seen them.

## What would be a regression
A total, a price or a change taken from the form; a sale recorded in part;
a balance below zero; a sale that took both cash and a balance; a sold-out
item sold; a way of paying chosen in advance on the form.
