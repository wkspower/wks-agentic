# Judge

Parent: [`root.md`](../../root.md). Governed by [`principles.md`](../../principles.md).
Record: [`record/judge.log.md`](../../record/judge.log.md).

## The six declarations

1. **Purpose** — Decide whether a change to any unit below the root stands, independently of the unit and of the maker of the change, so that no person checks a delivery.
2. **Interface** — Python 3, standard library only, run from the repository root as `python3 -m units.judge.verdict <command>`. Every command prints one JSON object on stdout and exits 0 for pass, 1 for fail, 2 for a malformed call.
   - `build <unit>` — builds the unit from nothing: byte-compiles `src/` into a fresh temporary directory. `{"unit", "pass"}`.
   - `verdict <unit>` — runs the unit's measure against `src/`. `{"unit", "number", "pass"}`; `number` is passed cases / all cases; pass when `number == 1` and there is at least one case.
   - `proof <unit>` — proves the measure: runs it once per planted case and passes only when every planted case fails it and there is at least one. A planted case that cannot be loaded (syntax error, or an error raised by its own import) tests nothing: it is reported `"error"` and makes `proof` fail. `{"unit", "planted": {case: "failed"|"passed"|"error"}, "pass"}`.
   - `rules` — checks the pet shop's rules R1–R3 ([`units/pet-shop`](../pet-shop/unit.md)) on `src/`. `{"violations": [{"rule", "file", "line", "detail"}], "pass"}`.
   - `judge --base <git-ref>` — the decision on a change: passes only when `rules` passes, and for every unit `build`, `verdict` and `proof` pass, and no unit's `number` is lower than at `<git-ref>` (a unit absent at `<git-ref>` counts 0 there). `{"units": {unit: {"build", "number", "base_number", "proof"}}, "rules", "pass"}`.
   - Units known: `catalog`, `stock`, `orders`, `pet-shop`. Unknown unit → exit 2.

   Conventions it reads, which measure writers follow:
   - The measure of unit `u` is `measures/u/test_*.py` (unittest), importing the code as `petshop.<module>` with `src/` on the path. Modules: `catalog`→`petshop.catalog`, `stock`→`petshop.stock`, `orders`→`petshop.orders`, `pet-shop`→`petshop.app`.
   - A planted case is `measures/u/planted/<case>.py`: a whole wrong replacement of that module, starting with a comment that names its defect. `proof` loads it in place of the module before running the measure.
   - Measures run in a fresh process each, with a timeout of 120 s; a timeout is a fail.

   The GitHub workflow [`.github/workflows/judge.yml`](../../.github/workflows/judge.yml) runs `judge --base origin/develop` on every pull request and every push to `develop`, and reports the status check `judge`.
3. **Rules** — The root's, plus: J1 it never imports from `src/` except through the measures it runs; J2 it reads no file the change under judgement can add to change its decision, other than `src/` and `measures/` as the conventions say.
4. **Budget** — From the root's: cost within the root's USD 100/month (GitHub Actions minutes only); a run of `judge` at most 10 minutes; attempts 3 per change; cap on effects without undo zero (it only reads and reports).
5. **Measure** — [`measures/judge/`](../../measures/judge/), written by an agent that does not build the judge. Number: fraction of its cases passing; each case is a planted tree the judge must pass or fail.
6. **Judge** — The root's judge, the person: a change to this unit, to `measures/` or to `.github/` stands only by the person's review (`CODEOWNERS`). Limit: the person also reviews; that is attention, counted by the root's measure.

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | It sees only `src/`, `measures/` and the base ref; it reports pass/fail and numbers, never edits. |
| 2 Single source | The conventions above live only here; measures and workflow cite them. |
| 3 External enforcement | The required status check `judge` on `develop` is what enforces it. Limit: until the person protects `develop`, nothing blocks a change that fails it (see [`queue.md`](../../queue.md)). Its own measure proves it with planted trees. |
| 4 Rehearsal before effect | It has no effect; it runs in the pull request before anything reaches `develop`. |
| 5 Return | It has no effect to undo; a change to it is a commit, undone by `git revert`. |
| 6 Selection | A change to it stands only when its own measure passes and the person accepts it. Limit: no alternatives without sight are paid for. |
| 7 Escalation | It asks nothing; a judgement it cannot make (malformed tree) fails and is reported to the maker. |
