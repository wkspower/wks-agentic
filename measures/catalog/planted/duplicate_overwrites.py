# Planted defect: adding an existing sku overwrites it instead of raising KeyError.
KINDS = ("pet", "supply")


def _nonempty_str(v):
    return isinstance(v, str) and v != ""


class Catalog:
    def __init__(self):
        self._items = {}

    def add(self, sku, name, kind, price_cents):
        if not _nonempty_str(sku):
            raise ValueError("sku must be a non-empty string")
        if not _nonempty_str(name):
            raise ValueError("name must be a non-empty string")
        if kind not in KINDS:
            raise ValueError("kind must be 'pet' or 'supply'")
        if isinstance(price_cents, bool) or not isinstance(price_cents, int) or price_cents <= 0:
            raise ValueError("price_cents must be a positive int")
                item = {"sku": sku, "name": name, "kind": kind, "price_cents": price_cents}
        self._items[sku] = item
        return dict(item)

    def get(self, sku):
        return dict(self._items[sku])

    def items(self, kind=None):
        if kind is not None and kind not in KINDS:
            raise ValueError("kind must be 'pet' or 'supply'")
        return [dict(self._items[s]) for s in sorted(self._items)
                if kind is None or self._items[s]["kind"] == kind]
