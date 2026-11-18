"""Fake peer for the measures: fixed customers and pets, products with stock.

Follows contract.json for the operations a unit receives; any other operation
answers {"ok": true, "id": 7}. Every call is appended to calls.jsonl.
"""
import json, os, sys

d, op = sys.argv[1], sys.argv[3]
state_path = os.path.join(d, "state.json")
state = json.load(open(state_path)) if os.path.exists(state_path) else {
    "customers": {"1": {"id": 1, "name": "Ana Souza", "phone": "5550101", "pets": [
        {"id": 1, "name": "Rex", "species": "dog"}]}},
    "pets": {"1": {"id": 1, "name": "Rex", "species": "dog", "customer_id": 1, "customer_name": "Ana Souza"},
             "2": {"id": 2, "name": "Mia", "species": "cat", "customer_id": 2, "customer_name": "Bruno Lima"}},
    "products": {"1": {"id": 1, "name": "Shampoo", "price_cents": 2500, "stock": 10},
                 "2": {"id": 2, "name": "Collar", "price_cents": 1990, "stock": 3}},
}
f = json.load(sys.stdin)
with open(os.path.join(d, "calls.jsonl"), "a") as log:
    log.write(json.dumps({"operation": op, "fields": f}) + "\n")


def out(answer):
    json.dump(state, open(state_path, "w"))
    print(json.dumps(answer))
    sys.exit(0 if answer["ok"] else 1)


def find(table, key):
    row = state[table].get(str(f.get(key)))
    if row is None:
        out({"ok": False, "error": "not_found"})
    return row


if op == "customer.get":
    out({"ok": True, "customer": find("customers", "id")})
if op == "pet.get":
    out({"ok": True, "pet": find("pets", "id")})
if op == "product.get":
    out({"ok": True, "product": find("products", "id")})
if op in ("stock.take", "stock.receive"):
    p, q = find("products", "product_id"), f.get("quantity")
    if not isinstance(q, int) or isinstance(q, bool) or q < 1:
        out({"ok": False, "error": "invalid"})
    if op == "stock.take" and q > p["stock"]:
        out({"ok": False, "error": "insufficient_stock"})
    p["stock"] += q if op == "stock.receive" else -q
    out({"ok": True, "stock": p["stock"]})
out({"ok": True, "id": 7})
