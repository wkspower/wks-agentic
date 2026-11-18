# Measure of the Judge unit

Measure 5 of [`units/judge/unit.md`](../../units/judge/unit.md), written by an
agent that does not build the judge and without sight of it. Interface,
conventions and rules are cited from that document and from
[`units/pet-shop/unit.md`](../../units/pet-shop/unit.md) (R1–R3); they are not
repeated here.

## What is measured

Whether the judge decides correctly. Each case builds a planted repository in
a temporary directory — a tiny `src/petshop/` (`catalog`, `stock`, `orders`,
`app`), a passing `measures/<unit>/test_*.py` and one failing
`measures/<unit>/planted/<case>.py` for each of the four known units, in a git
repository — plants one thing in it, and runs the judge only through its
interface, `python3 -m units.judge.verdict <command>`, with the planted tree as
working directory. It asserts on the exit code (0 pass, 1 fail, 2 malformed),
on stdout being one JSON object, and on the fields the case is about.

| File | Command | Cases |
|---|---|---|
| `test_build.py` | `build` | valid src passes; a syntax error in the unit's module, or anywhere in `src/`, fails; nothing is written into `src/` |
| `test_verdict.py` | `verdict` | each unit with a passing measure passes with number 1; one failing case gives number 0.5 and fails; cases across files and errors count (0.75); another unit's failure does not count; zero cases fails; no measure fails; a measure that hangs past the 120 s timeout fails |
| `test_proof.py` | `proof` | each unit passes; all planted cases failing passes (each reported `"failed"`); one planted case passing the measure fails (reported `"passed"`); no planted directory, or no planted case in it, fails |
| `test_rules.py` | `rules` | clean tree passes with no violations; reading a file and forbidden modules in `measures/` are not violations; R1 once per forbidden module (`socket`, `urllib`, `http.client`, `smtplib`, `subprocess`, `ftplib`, `ssl`), a non-standard-library import and `open(` for writing; R2 for `email` (key and parameter), `card_number`, `address`, `customer_name`; R3 for code in `src/` outside `src/petshop/` — each planted alone and reported with rule, file and line |
| `test_judge.py` | `judge --base` | passes when numbers are equal, rise, or the unit is absent at the base (0); fails when a number drops, when a verdict fails without a drop, when rules, build or proof fail, or when a unit has no measure |
| `test_interface.py` | — | unknown unit (also one with a measure directory) exits 2 for `build`, `verdict`, `proof`; no command, unknown command, missing unit, `judge` without `--base` or its ref exit 2; a malformed call still prints one JSON object |

## The number

Fraction of cases passing: passed / all, one case per test method (a test
with sub-tests counts once and passes only when all its sub-tests do; a
skipped case counts as not passed). The judge's measure passes at 1.

    python3 measures/judge/prove.py --number

prints `{"cases", "passed", "number"}`.

## How to run

From the repository root:

    python3 -m unittest discover -s measures/judge -t .

The case `test_fails_a_measure_that_hangs_beyond_the_timeout` is slow: it
waits out the judge's 120 s timeout. `JUDGE_MEASURE_SKIP_SLOW=1` skips it for
a quick run; such a run gives no valid number.

**Which judge is measured.** The judge under test is the directory placed on
`PYTHONPATH` of the subprocess (and nothing else on it): `JUDGE_ROOT` if set,
else the first `PYTHONPATH` entry holding `units/judge/verdict`, else the real
repository root (two levels above this directory). The planted tree has no
`units/` directory, so `units.judge.verdict` always resolves to that judge,
while the tree's `src/` and `measures/` are reached only through the working
directory, as the interface says. See [`plant.py`](plant.py).

## How the measure is proven

A judge that always passes and one that always fails must each fail this
measure. Both are planted in [`planted/`](planted/):
`always_pass/units/judge/verdict.py` and `always_fail/units/judge/verdict.py`.

    python3 measures/judge/prove.py

(exit 0 = proven) checks, without any judge, that the planted tree's measures
pass on its `src/` and that every planted case and the buggy catalog fail
them, so the cases expect the right decisions; then runs this measure against
each stub, pointed at by `PYTHONPATH`, and requires a number below 1. The same
by hand:

    PYTHONPATH=measures/judge/planted/always_pass python3 -m unittest discover -s measures/judge -t .
    PYTHONPATH=measures/judge/planted/always_fail python3 -m unittest discover -s measures/judge -t .

Both must report failures. Run the proof at every change to this measure.
