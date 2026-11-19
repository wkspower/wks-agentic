# Lessons and cases

This branch tests one thesis:

> Lessons with their reasons kept the way torre does it, and every lesson
> that can be checked by a machine also turned into a case.

A *lesson* is one sentence that changes what the next session does, kept with
the reason for it and the event that taught it. A *case* is a program that
passes or fails and prints what it measured. Code built here is disposable;
the lessons and the cases are what lasts.

## Where things are

| Path | Holds |
|---|---|
| `CLAUDE.md` | This file. Read at the start of every session. One line per lesson. |
| `lessons/` | One file per lesson: the reason, the source, what would be a regression. |
| `cases/` | One executable per checkable lesson. Run from the repository root. |
| `check` | Proves the two stay linked. `./check` and `./check --selftest`. |
| `HANDOFF.md` | State of the work and how to resume. Read it second. |
| `product/` | Whatever a run builds. May be deleted and rebuilt at any time. |
| `prompts/`, `runs/` | The prompts under test and what each run showed. |

## What a session does

- **When something is learned, it becomes a lesson before the work goes on.**
  Learned means: the person decides or corrects something, a defect is found,
  or an approach is tried and rejected. Write `lessons/NNNN-slug.md` and add
  its line below.
- **If a machine can check it, write the case first.** See it fail, then fix.
  If no machine can check it, mark the line `prose:` and say why not.
- **A lesson or a case changes only on evidence from outside**: the person,
  real data, or a case that fails. Say which in the lesson's Source.
- **Run `./check` before saying the work is done**, and report its summary line.
- **Keep this file short.** One line per lesson. Reasons live in `lessons/`.

## Lessons

- **L0001** A check that measured nothing has failed; every check prints what it measured. [why](lessons/0001-empty-is-not-a-result.md) · case: [`cases/0001-empty-is-not-a-result`](cases/0001-empty-is-not-a-result)
- **L0002** A wrong variant is kept as a small change applied when the check runs, never as a full copy. [why](lessons/0002-no-full-copies.md) · case: [`cases/0002-no-full-copies`](cases/0002-no-full-copies)
- **L0003** Agreement between agents of the same model is not evidence that something is right. [why](lessons/0003-same-model-agreement.md) · prose: no program can tell where a claim's evidence came from
- **L0004** Before building, ask the person everything foreseeable in one round, each question with a recommendation. [why](lessons/0004-ask-in-one-round.md) · prose: whether a later question could have been foreseen is a judgement
