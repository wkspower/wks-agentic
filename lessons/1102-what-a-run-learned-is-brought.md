# L1102 — What a run learned comes back through `./bring`, never by copying a tree: what one side changed is taken, and what both changed is refused where no product can prove the result, and named

## Reason
After runs 005, 007 and 010 the coordinating session brought a run's lessons
to the base by hand: it copied the branch's tree, without `product/`, over
the base. That works while one branch exists at a time. With two, the
second copy removes what the first brought. A plain `git merge` does not
lose anything, and stops instead: both branches add lines at the end of
`LESSONS.md` and of `CLAUDE.md`, both write at the top of `HANDOFF.md` and
at the end of its list of runs, and git calls each of those a conflict for
a person to settle, every time, although nothing in them disagrees.

`./bring OTHER` is the operation. It is run in a clean checkout, compares
three trees (this one, `OTHER`, and the commit where they parted) and works
by what each file is, not by its text alone:

Where they parted is the common commit git knows. A rebuild is started from
a first commit with no history, so that no earlier build can be read, and
then git knows none: the pet shop's and the library's branches share no
commit with the base. For such a branch the fork is its first commit, when
that holds a tree the other side once had; when it does not, the operation
refuses until `--from COMMIT` says where they parted.

| What | How it is brought |
|---|---|
| `product/` | Never. A product stays on its branch. |
| The lesson lines of `CLAUDE.md` and `LESSONS.md` | By number. A line only one side added, changed or removed is taken. They are written in order of number, each in the file its labels say. |
| `HANDOFF.md` | Every line either side added is kept. |
| Every other file: lesson files, cases, surfaces, run records, `caselib.*`, `check`, `bring` | Whole. A file only one side changed is taken as that side has it. |

What it refuses, changing nothing:

- **One number taken by two lessons**, or one path added by both sides with
  different contents. Nothing can be merged: one of them is renumbered on
  its own branch (L1101).
- **A lesson added in a block that is not its run's**: past L0042 and with
  no `runs/0NN-*.md` brought with it.
- **Where there is no product: anything both sides changed since they
  parted.** A lesson's line, its file, a case, `caselib.py`, the check. The
  base has no product, so no case that needs one runs there, and a merge of
  two changes to shared code would be accepted on no evidence at all.

That last refusal has one way out, and it is the point of the design: **the
merge of two changes is made where a product can prove it.** On the branch
that has the product, `./bring BASE` takes the base in. There the same
operation merges by text a file both sides changed, names it, and runs
`./check` with the product's cases in force; text git cannot merge is left
marked for the session to settle. A lesson line both sides changed is
written twice, which the check refuses until a reader has chosen. When that
is committed the branch holds everything the base has, so bringing it to
the base finds nothing changed on both sides.

What a reader must judge and the operation only names: lessons that came
from the two sides and share a label, which may say the same thing or
contradict each other; a file merged by text. They are printed and put in
the message of the merge commit.

`./bring` ends by running `./check` on the result and leaves the commit to
whoever ran it. `./bring --verify OURS THEIRS` says whether the tree is
what the rules give for those two, however it was made: that is what
refuses a merge done by copying.

### Products that are not in the tree
A change to what products share reaches a product only when its branch
takes the base in. Nobody is made to do that: run 006 made eight cases
general and the pet shop's branch was left as it was. `./bring` says, after
bringing, which of the things it brought reach other products.
`./bring --try BRANCH` runs this tree's check with that branch's product in
a scratch copy, prints what it says and keeps nothing. It was first written
as a merge into the product's branch, and the pet shop's branch (run 005)
showed why not: it is five runs behind, its lesson lines are in an older
form, and the merge refused 35 things before any case ran. Whether a product
meets the base does not depend on how old its branch's scaffold is. On
2026-11-20 both real products met this base: the pet shop's build of run 005
with 29 cases in 59 s, the library's of run 010 with 28 in 84 s. Who
runs it and when is in `HANDOFF.md`; that a product then gets changed to
meet a new general lesson is a decision, not part of the operation.

### Ways not taken
- **`merge=union` in `.gitattributes`**: keeps both sides' lines with no
  program, but only where the merge is made by a git that reads the
  attribute, cannot tell a collision of numbers from two lines that belong
  side by side, and does nothing for a file two products changed.
- **One file per lesson line, and no shared list**: no line to conflict on,
  but `CLAUDE.md` must hold the `always` lines whole, because that file is
  how they reach a session (L0039).
- **Merging shared code by text on the base when git finds no conflict**:
  the result would have been run by no case of either product.

## Source
The coordinating session's instruction for run 011, 2026-11-20: the three
ways the scaffold breaks, the result to prove ("no lesson renumbered, no
line of either lost, and `./check` passing on the result with no product"),
and the constraints, among them "Two products may each change what is
shared […] Do not pretend this away" and "make the check name the
candidates instead of deciding". The person's own words, as that
instruction reports them: "It doesn't need to be perfect, it will never be.
It needs to be adaptable and scalable. Different product experiences
contribute with the process improvement. And the process enforces common
practices", and "Yes" to two products built at the same time and merged
back. The operation, its rules, the two directions and what it refuses are
this run's (011). That branches begun with no history exist is from the
repository itself: `./bring --try run/010-library-rebuild` stopped at
"merge-base" on its first real use. The case plants the situation in
scratch repositories; no two real runs have been brought with it yet. The person has not seen this
lesson.

## What would be a regression
A run's lessons brought to the base by copying its tree; a line or a file
of either side missing after a bring; a lesson's number changed by the
operation; `product/` arriving on the base; a file both sides changed
accepted where there is no product; a bring that changes the tree and then
refuses; candidates decided by the operation instead of named.

What no case catches: a merge by text that every case passes and is still
wrong; two lessons that contradict each other under different labels; a
merge made by hand and never put to `./bring --verify`; a product branch
that never takes the base in.
