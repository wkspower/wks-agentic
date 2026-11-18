"""Shared by the measures of `petshop` and its parts.

Speaks the protocol stated in units/petshop/unit.md: one JSON request on the
standard input of `run <data-dir>`, one JSON answer on its standard output.
"""
import json, os, shutil, subprocess, sys


class Shop:
    def __init__(self, exe, data, **env):
        self.exe, self.data, self.env = exe, data, dict(os.environ, **env)

    def __call__(self, op, **args):
        if not os.path.exists(self.exe):
            return {"ok": None, "_error": "not built"}
        try:
            r = subprocess.run([self.exe, self.data], input=json.dumps(dict(args, op=op)), env=self.env,
                               capture_output=True, text=True, timeout=30)
            out = json.loads(r.stdout)
            return out if isinstance(out, dict) else {"ok": None, "_error": "answer is not an object"}
        except Exception as e:                      # crash, timeout, not JSON: all are wrong answers
            return {"ok": None, "_error": repr(e)[:200]}


def ok(r):
    return r.get("ok") is True


def err(r, code):
    return r.get("ok") is False and r.get("error") == code


def listing(d):
    return sorted(os.path.join(p, f) for p, _, fs in os.walk(d) for f in fs if "__pycache__" not in p)


def fresh(work):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    return lambda name: os.path.join(work, name)


class Cases:
    def __init__(self):
        self.rows = []

    def add(self, name, right, seen=""):
        self.rows.append((name, bool(right), str(seen)[:300]))

    def finish(self, extra=None):
        right = sum(r for _, r, _ in self.rows)
        for name, r, seen in self.rows:
            print(("ok   " if r else "FAIL ") + name + ("" if r else f"  [{seen}]"))
        out = {"pass": bool(self.rows) and right == len(self.rows), "number": right, "cases": len(self.rows),
               "failed": [n for n, r, _ in self.rows if not r]}
        out.update(extra or {})
        print(json.dumps(out))
        sys.exit(0 if out["pass"] else 1)
