# Prompts under test

A prompt here states a goal and nothing about method. The method is supposed
to come from `CLAUDE.md` and the lessons; that is what is being tested.

## Running one

1. Start a fresh session on a new branch made from `lessons-and-cases`.
   Name the branch `run/NNN-slug`, matching the prompt file.
   For a product other than the pet shop, make the branch from the base
   (`lessons-and-cases` without `product/`); `HANDOFF.md` says how a new
   product starts and declares its labels.
2. Give it the text of the prompt file and nothing else.
3. Answer its questions as yourself. Do not coach it about lessons or cases.
4. When it stops, record the run.

## Recording a run

Add `runs/NNN-slug.md` on the run's branch with:

- the prompt file and the branch;
- the questions asked, in how many rounds, and how long each waited;
- lessons added: how many with a case, how many prose only, and whether each
  case was committed before the fix it guards;
- the summary line of `./check` at the end, and the labels the product declared;
- time taken and sub-agents used;
- what was not verified.

Lessons a run produces are merged back into `lessons-and-cases` only by the
person, after reading them. That merge is what lets the next run start from
them. Since run 011 it is made with `./bring` and by no other means (L1102);
`HANDOFF.md` has the steps, also for two runs at the same time.

## Comparing

The same goal has been run three other ways on this repository: under the
principles (`run-1` to `run-3`, `claude/wizardly-cerf-94l00l`) and under the
cases-only prompt (`claude/casos-run-1`). Those are the baselines.
