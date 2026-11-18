# Judge — record

Record of [`units/judge`](../units/judge/unit.md). Newest last.

## 2026-11-18

- Declarations given by the root. Its measure is commissioned from one agent,
  its build from another; neither is the maker of the pet shop.
- Limit found: the agents act on GitHub as the person's own account, so a
  review required from the person cannot be told apart from one by an agent.
  Put to the person in [`queue.md`](../queue.md).

## 2026-11-18 — first build

Built by an agent that wrote neither the judge's measure nor the pet shop.

- `units/judge/__init__.py`, `units/judge/verdict.py` (stdlib only): `build`,
  `verdict`, `proof`, `rules`, `judge --base <ref>` as declared; one JSON object
  on stdout for every call (exit-2 calls print `{"error", "usage", "pass": false}`);
  diagnostics on stderr.
- `.github/workflows/judge.yml`: job `judge` on pull requests to `develop`
  (base `origin/develop`) and pushes to `develop` (base `HEAD~1`); also runs the
  judge's measure, its proof and the root check's tests. Timeout 15 min.

Choices where the declarations leave room:

- **Base numbers.** `judge --base` extracts `src/` and `measures/` of `<ref>` with
  `git archive` into a temporary directory (the repository and its worktrees are
  not touched) and runs the measure *as present at the base* on the base's `src/`.
  A unit whose measure is absent at the base counts 0. An unresolvable ref is a
  malformed call (exit 2).
- **Measure runs.** Each run is a fresh `python3 -I -B` process (no `PYTHONPATH`,
  no bytecode written into `src/`), with cwd the judged tree, killed with its process
  group after 120 s (a fail). The runner imports what it needs before `src/` is on
  the path and writes its counts to a temporary file, not stdout. Cases are test
  methods; a method with failing sub-tests, an error, a skip or an import error
  counts as not passed; zero cases is number 0 and fails. Runs are parallel (≤4).
- **Proof.** Each planted file is loaded with `importlib` as `petshop.<module>` into
  `sys.modules` (and onto the package) before the measure is discovered; a planted
  case is `"failed"` when the number is below 1 (a timeout or crash counts as
  failed). Proof does not itself require the unplanted measure to pass; `verdict` does.
- **`build`** byte-compiles every `.py` under `src/` with `py_compile` into a
  temporary directory, whatever the unit; no source under `src/` fails.
- **R1** (strictest reading): the listed modules, by name and as prefixes
  (`urllib.parse` counts as `urllib`), also via `__import__`/`importlib.import_module`
  with a literal; any top-level import not in `sys.stdlib_module_names` except
  `petshop`; `open(` (builtin, `io.`, `codecs.`, or a `.open(` method) with a mode
  containing `w`, `a`, `x` or `+`, or a non-literal mode; `os.` process/file calls
  (`system`, `exec*`, `spawn*`, `remove`, `open`, …), any `shutil.` call,
  `.write_text`/`.write_bytes`/`.touch`; binary modules or `.pth` under `src/`;
  a file that cannot be parsed (rules cannot be checked).
- **R2**: a name whose tokens include email, mail, phone, address, card, iban, ssn,
  birth, dob, surname, passport, postcode, street, cvv …, or `name` qualified by
  first/last/full/customer/client/user/owner…; checked as dict keys, string
  subscripts, attribute names, function parameters, keyword arguments, class fields
  and `__slots__`. A plain `name` is not flagged.
- **R3**: any `.py` under `src/` outside `src/petshop/`, reported at line 1.

Measure: `python3 measures/judge/prove.py --number` → 54/54, **number 1** (slow
timeout case included); `prove.py` → measure proven.

On the real repository, `judge --base HEAD` fails: numbers all 1 (base 1), build and
proof pass for the four units, but `rules` reports R1 at `src/petshop/app.py:3`
(`from urllib.parse import parse_qs`), since R1 names `urllib`. Work for the pet
shop's maker, or a proposal to the root to narrow R1 to `urllib.request`; the judge
keeps the strict reading until then.
