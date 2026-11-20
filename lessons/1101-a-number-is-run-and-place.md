# L1101 — A lesson's number is its run and its place in it, L1203 for the third lesson of run 12; the plain sequence ended at L0042

## Reason
Until run 010 every run happened after the one before it, and a lesson took
the next number in one sequence. Two runs made from the same base at the
same time, each knowing nothing of the other, both take L0043: two
sentences, two files and two cases under one number, and one of them must be
renumbered after other lessons, cases and run records already cite it.

A number that cannot collide needs something the two runs already do not
share. They share nothing but the base, and the one thing that tells them
apart from their first minute is the name of the branch each was started
on, `run/NNN-slug`, which whoever starts them has to make different anyway.
So the run's number is the first two digits of the lesson's number and the
lesson's place in the run the last two. L1203 is said "twelve oh three": the
third lesson of run 12. The form stays four digits, so every place that
reads `L` and four digits still reads it, and the number now also says which
run record holds the event that taught the lesson.

What follows:

- **L0001 to L0042 keep their numbers** and the sequence is closed. No
  lesson is numbered L0043 to L0099, ever. The check refuses one.
- **A run takes its number from its branch.** `./check --next` reads the
  branch name and the lessons in the tree and prints the next number; the
  text the hook puts in front of a session says the same (L0041), so a
  session does not have to work it out or remember to ask.
- **A lesson of run 12 needs `runs/012-*.md` in the tree.** The run's record
  is begun with its first lesson, not at the end. That is what lets a tree
  with no history be checked: the block of every lesson past L0042 is a run
  the tree has a record of.
- **Uniqueness now rests on one thing: two runs never have the same run
  number.** `./bring --begin SLUG ...` gives the next free numbers, reading
  `runs/` and the names of every branch it can see. When that fails all the
  same, both runs make L1201, and `./bring` refuses the second (L1102); the
  second is then renumbered on its own branch, before anything outside that
  branch cites it. That is the only renumbering there is.

A run has room for 99 lessons; the most so far is 11. Run 100 needs a fifth
digit, and the pattern `L\d{4}` is written in the check, in `bring` and in
five cases. That is 88 runs away and is not solved here.

### Ways not taken
- **A block handed out by the coordinator** (L0100 to L0199 for one branch,
  L0200 for the next): the same single point, the coordinator, but nothing
  in the tree says which block is whose, so no check can refuse a lesson in
  the wrong one.
- **The date, a hash or a random word in the number**: cannot collide, and
  cannot be said aloud or put in order by a reader.
- **Renumbering at the merge**: every citation of the number, in lessons,
  cases, run records and the person's memory, is then wrong on the branch
  that keeps the product.

## Source
The coordinating session's instruction for run 011, 2026-11-20, which names
the collision and sets the constraints: L0001 to L0042 keep their numbers,
L0039 stays true, and "if a lesson's identity stops being a plain sequence
number, say what it becomes and why, and keep it short enough to say
aloud". The person's own words, as that instruction reports them, were about
what the process must be: "It doesn't need to be perfect, it will never be.
It needs to be adaptable and scalable. Different product experiences
contribute with the process improvement. And the process enforces common
practices", and then "Yes" to the offer of two products built at the same
time, "fixing the lesson numbering first". The scheme, the closed sequence,
the record begun with the first lesson and `--next` are this run's (011).
The person has not seen this lesson.

## What would be a regression
A lesson numbered L0043 to L0099; a lesson past L0042 whose first two
digits name no run the tree has a record of; a lesson given a new number
after it left its branch; `./check --next` giving a number already taken, or
any number on a branch that is no run's; a session told to work the number
out for itself.

What no case catches: two runs started with the same run number and never
brought to the same base; a session that ignores the number it was given
and takes another free one in its own block.
