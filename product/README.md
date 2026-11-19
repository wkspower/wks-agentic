# Pet shop

Disposable. The lessons L0005 to L0015 in `../CLAUDE.md` and their cases are
what a rebuild has to meet; this is one build that meets them.

    python3 product/petshop.py                 # then open http://127.0.0.1:8000/
    python3 product/petshop.py --sample        # a few sample rows, only into an empty database
    python3 product/petshop.py --db shop.db --port 8080

Needs Python 3.10 or later and nothing else. Everything is in the one SQLite
file (`petshop.db` by default): copy it to back up, delete it to start over.
`/export.json` gives the whole state to read; nothing but the pages changes it.
