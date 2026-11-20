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
| `CLAUDE.md` | This file. Read at the start of every session. One line for each lesson that is `always` in force. |
| `LESSONS.md` | One line for every other lesson, with its labels. Not read whole: `./check --lessons` prints the ones in force. |
| `lessons/` | One file per lesson, `lessons/NNNN-*.md` for LNNNN: the reason, the source, what would be a regression. |
| `cases/` | The cases. Each says in its first lines which lesson it is a case of; most are `cases/NNNN-*`. |
| `caselib.py`, `caselib.js` | What the cases share: start the product, put a fault in front of it. |
| `surface/` | One file per product: what a case under a general label may know about it. |
| `check` | Proves the lessons, their files and their cases stay linked, and runs the cases in force. |
| `HANDOFF.md` | State of the work and how to resume. Read it second. |
| `product/` | Whatever a run builds. May be deleted and rebuilt at any time. |
| `product/LABELS` | What the product is: the labels it chose, one per line. No product, no labels. |
| `prompts/`, `runs/` | The prompts under test and what each run showed. |

## What a session does

- **First, run `./check --lessons` and read what it prints.** The lessons
  below are in force for every product. That command prints the others in
  force for the product in `product/`, and names each label that is off.
  With no product, `./check --lessons LABEL` prints what a label would bring.
- **When something is learned, it becomes a lesson before the work goes on.**
  Learned means: the person decides or corrects something, a defect is found,
  or an approach is tried and rejected. Write `lessons/NNNN-slug.md` and add
  its line: below if it is `always`, in `LESSONS.md` if not.
- **A lesson line is its number, its labels and its sentence**, and nothing
  its number gives: no link to its file or its cases (L0039). The labels are
  in square brackets after the number: `always`, or one or more plain labels
  separated by commas. There is no list to choose from; reuse a label when
  it fits and write a new one when none does. A lesson is in force when it
  is `always` or the product declared one of its labels in `product/LABELS`.
  Follow the lessons in force; the others are kept for the product that
  switches them on (L0023).
- **If a machine can check it, write the case first.** Its first lines say
  `Case of lesson LNNNN`. See it fail, then fix. If no machine can check it,
  end the line with `· prose:` and say why not.
- **A lesson or a case changes only on evidence from outside**: the person,
  real data, or a case that fails. Say which in the lesson's Source.
- **Run `./check` before saying the work is done**, and report its summary
  line. It runs each case once, in a copy of the tree without the product's
  source (L0038); a case run by hand is run from the repository root.
- **Keep this file short.** One line per lesson. Reasons live in `lessons/`.

## Lessons

- **L0001** [always] A check that measured nothing has failed; every check prints what it measured.
- **L0002** [always] A wrong variant is kept as a small change applied when the check runs, never as a full copy.
- **L0003** [always] Agreement between agents of the same model is not evidence that something is right. · prose: no program can tell where a claim's evidence came from
- **L0004** [always] Before building, ask the person everything foreseeable in one round, each question with a recommendation. · prose: whether a later question could have been foreseen is a judgement
- **L0013** [always] Done means every case in force passes, the agent drove the product by script as a person would and read what came out, and what was not verified is said; none of that is the person using it. · prose: what the agent saw in its own screenshots is not a program's result
- **L0019** [always] A wrong variant is a fault put at the product's interface when the case runs; no case names, reads or edits the product's source.
- **L0023** [always] A lesson says when it applies in plain labels, a product declares the labels it chose, and only `always` and those are in force.
- **L0024** [always] A case is born in the product that needed it, and is made general only when a second product needs it. · prose: whether a second product needs a case is a judgement
- **L0034** [always] What the cases know about a product is in its file under `surface/`, found through `product/LABELS`; nothing the cases share remembers a product of its own.
- **L0037** [always] A record of the person's approval says what they saw and how they said it. · prose: no program can tell what a person read
- **L0038** [always] The check runs every case once, on a copy of the tree with the product's source taken away, and prints the seconds each took.
- **L0039** [always] A lesson line holds only what its number does not give; this file lists the `always` lessons, `LESSONS.md` the others, and a session reads those in force from `./check --lessons`.
- **L0040** [always] The summary line of the check says the lines of the product and of the cases in force; no limit is set.
- **L0041** [always] What must happen at the start of a session is done by tooling: a hook puts the lessons in force for the product in front of the session, and nothing depends on the session running a command.
