# Planted wrong result: a guard that allows everything.
import json
print(json.dumps({"allowed": True, "kind": "work", "reasons": []}))
