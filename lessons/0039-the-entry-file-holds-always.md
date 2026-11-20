# L0039 — A lesson line holds only what its number does not give; `CLAUDE.md` lists the `always` lessons and `LESSONS.md` the others

## Reason
`CLAUDE.md` is read whole at the start of every session, so every byte in it
is paid for by every session of every product. Two things in it grew with
each run and told the reader nothing.

The links. Each line ended with the path of its lesson file and of its
cases, and both follow from the number: the file of L0026 is
`lessons/0026-*.md`, and a case says in its first lines which lesson it is a
case of. So a line holds the number, the labels, the sentence, and
`· prose: why` when no machine can check it. `./check` finds the rest, and
refuses a lesson with no file or two, a lesson with neither a case nor a
word on why not, and a case that names no listed lesson.

The lessons that are off. A session on the school library read the pet
shop's nine rules, and the next product would read both. So `CLAUDE.md`
keeps only the lessons labelled `always`, which every session needs, and
every other line lives in `LESSONS.md`, which no session reads whole.
`./check --lessons` prints the lines in force for the product in `product/`
and names every label that is off, with its count. `./check --lessons LABEL`
prints the lines a label would bring: that is how a session on the base,
with no product, finds which labels exist and chooses among them.

Since run 009 no session is told to run that command. A hook runs
`./check --start` at the start of every session and its output is put in
front of the session: the lines in force, or on the base every label with
the lines it brings (L0041). `./check --lessons` stays, for a person or a
session that wants to look.

Nothing is lost by a lesson being off: its line, its file and its case are
kept and checked as before (L0023).

## Source
The coordinating session's instruction for run 008, 2026-11-20, and its
measurement: `CLAUDE.md` 11.9 KB, 4.4 KB of it links, 10 of 34 lesson lines
not in force for the product in the tree. The person's own word was
"growth", choosing which open problem to work on. The two constraints (a
session on the base can still find the labels and what each brings; the
check still refuses what its selftest refused) are the coordinating
session's. Where the lines went, that a command prints them, and that a case
names its lesson are this run's choices. The person has not seen this lesson.

Run 009, 2026-11-20: the sentence lost its last part, "and a session reads
those in force from `./check --lessons`". The person, on reading that nobody
knew whether a session would run that command: "sounds like we are relying
on non determinism for something we want determinism?", as the coordinating
session reports it. What replaced it is L0041.

## What would be a regression
A lesson line with a link or a path on it; a lesson in `CLAUDE.md` that is
not `always`, or an `always` lesson in `LESSONS.md`; `./check --lessons`
leaving out a lesson in force or printing one that is off; a label that is
off and not named; the base unable to print what a label brings.

Run 008 left one thing no case caught: a session that did not run
`./check --lessons` read only the `always` lessons. Run 009 took that
dependence away (L0041).
