# L0009 — A sale beyond stock is refused whole, stock never goes below zero, and low stock is listed

## Reason
Stock that can go negative stops meaning what is on the shelf. A sale is
refused whole, not trimmed, so the person at the counter decides what to do.
A product is low when its stock is at or below its own threshold.

## Source
The person, run 001, 2026-11-19 (answer 10).

## What would be a regression
A sale recorded in part, two lines of one product passing because each alone
fits, an adjustment that leaves stock below zero, or a product at its
threshold missing from the low-stock list.
