"""What the pet shop's measures share: calling a unit, cases, a fake peer."""
import json, os, socket, subprocess, sys, tempfile, time, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.getcwd()
WORK = os.path.abspath(os.environ["WORK"])
RUN = os.path.join(WORK, "run")
CONTRACT = json.load(open(os.path.join(HERE, "contract.json")))
OPERATIONS = CONTRACT["operations"]


def tmp():
    base = os.path.join(TOP, ".rehearsal", "tmp")
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(dir=base)


class Cases:
    def __init__(self):
        self.passed = self.total = 0
        self.before = self.listing()

    def listing(self):
        return sorted(os.path.join(b, f) for b, _, fs in os.walk(WORK) for f in fs
                      if "__pycache__" not in b)

    def case(self, name, cond):
        self.total += 1
        try:
            good = bool(cond())
        except Exception as e:
            good, name = False, f"{name} ({type(e).__name__}: {e})"
        self.passed += good
        print("ok  " if good else "FAIL", name)

    def end(self):
        self.case("nothing was written in the work, only in PETSHOP_DATA",
                  lambda: self.listing() == self.before)
        print(f"measured: {self.passed} of {self.total} cases against {WORK}")
        print("number:", self.passed)
        sys.exit(0 if self.passed == self.total else 1)


def caller(data, peer=None):
    """do(operation, **fields) -> the unit's answer, with its exit status."""
    def do(operation, **fields):
        env = dict(os.environ, PETSHOP_DATA=data)
        env.pop("PETSHOP_PEER", None)
        if peer:
            env["PETSHOP_PEER"] = peer
        try:
            p = subprocess.run([RUN, "do", operation], input=json.dumps(fields),
                               capture_output=True, text=True, env=env, timeout=30)
            answer = json.loads(p.stdout)
            assert isinstance(answer, dict)
        except Exception as e:
            return {"ok": None, "error": f"broken: {e}", "_exit": -1}
        answer["_exit"] = p.returncode
        return answer
    return do


def ok(answer):
    return answer.get("ok") is True and answer.get("_exit") == 0


def err(answer, code):
    return answer.get("ok") is False and answer.get("error") == code and answer.get("_exit") != 0


class Fake:
    """A peer that stands in for the other units; see fake_peer.py."""
    def __init__(self):
        self.dir = tmp()
        self.path = os.path.join(self.dir, "peer")
        with open(self.path, "w") as f:
            f.write(f'#!/bin/sh\nexec python3 "{HERE}/fake_peer.py" "{self.dir}" "$@"\n')
        os.chmod(self.path, 0o755)
        self.do = caller(self.dir)

    def stock(self, product_id):
        return json.load(open(os.path.join(self.dir, "state.json")))["products"][str(product_id)]["stock"]

    def calls(self):
        path = os.path.join(self.dir, "calls.jsonl")
        return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


class Desk:
    """`run serve` on a free local port, killed at close()."""
    def __init__(self, data, peer):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        self.port = s.getsockname()[1]
        s.close()
        env = dict(os.environ, PETSHOP_DATA=data, PETSHOP_PORT=str(self.port))
        env.pop("PETSHOP_PEER", None)
        if peer:
            env["PETSHOP_PEER"] = peer
        try:
            self.proc = subprocess.Popen([RUN, "serve"], env=env, stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
        except Exception:
            self.proc = None
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)

    def request(self, path, form=None):
        """(status, page). `form` is a list of (name, value) pairs for a POST."""
        data = urllib.parse.urlencode(form).encode() if form is not None else None
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", data, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception as e:
            return 0, f"broken: {e}"

    def close(self):
        if self.proc:
            self.proc.kill()
            self.proc.wait()
