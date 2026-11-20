# L0041 — What must happen at the start of a session is done by tooling: a hook puts the lessons in force for the product in front of the session, and nothing depends on the session running a command

## Reason
Two things are easy to take for one. Whether a session follows a lesson
cannot be made certain; only a case can tell, afterwards. Whether the lesson
is in front of the session can be made certain. Run 008 moved the lessons
that are not `always` out of `CLAUDE.md` and told the session to run
`./check --lessons`. From then on a product's lessons reached a session only
if the model chose to run a command, and nobody knew whether it would.

So the rule: what must happen is done by the tooling, and the entry file
holds only what needs judgement. `.claude/settings.json` has a SessionStart
hook with no matcher, so it fires on a new session, a resume, a clear and a
compaction. It runs `./check --start`, and Claude Code adds what a
SessionStart hook prints to the context. That prints the lesson lines in
force for the product in `product/` besides the `always` ones, and each
label that is off with its count. With no product it prints every label
with the lines it brings, because choosing labels is the first thing a new
product does. It is worked out at the start of each session from
`LESSONS.md` and `product/LABELS`, so there is nothing to keep up to date.

`./check --start` always ends with 0, and says what is wrong in the record
instead of failing: when a hook fails, Claude Code shows the session nothing
of what it printed. A hook's output is cut at 10,000 characters, with only a
preview shown, so `./check` fails when the output is longer, for the tree
and for the tree without its product.

### The way that was tried first and rejected: a file made by the check, included by `CLAUDE.md`
`CLAUDE.md` can include a file with `@path`. The file would hold the lines
in force, written by `./check`, and be refused when stale. It cannot meet
three things at once. The base is this tree with `product/` removed and no
other step, so every file outside `product/` is the same, byte for byte, in
both trees. A file that is right for the library is then stale on the base,
where the check must pass. Putting the file inside `product/` makes it go
with the folder, but then `CLAUDE.md` on the base includes a file that is
not there, and the documentation does not say what that does. A folder's own
`CLAUDE.md` is no way round: it is loaded when a file in that folder is
first read, not at the start. A hook has no file to go stale.

### Where the hook does not run
- In anything that reads `CLAUDE.md` and is not Claude Code, or a Claude
  Code that is told to skip hooks (`disableAllHooks`, or an organisation
  that allows only its own hooks).
- Where `python3` is missing, or the hook fails for another reason: the
  session goes on and the model sees nothing.
- For a sub-agent: the documentation does not say that SessionStart fires
  for one. A sub-agent that builds needs the lessons in its instructions.

For these `CLAUDE.md` says what the hook's text begins with, so that a
session which does not have it can tell, print it itself and say so. That is
a way to notice a gap, not the way the lessons arrive.

## Source
The person, 2026-11-20, in the coordinating session, on reading that "nobody
knows whether [a session] will run that command before working": "sounds
like we are relying on non determinism for something we want determinism?",
and then "yes" to that session's offer to launch a run that fixes the
loading first. Those are the person's words as the coordinating session
reports them. The rule as worded, the two ways and their order (the include
first, the hook only if it fails), and the constraints are the coordinating
session's. That the include fails, by the argument above, and what the hook
prints are this run's (009). The person has not seen this lesson.

What a hook does with its output, its matchers, its exit codes and the
10,000 characters are from https://code.claude.com/docs/en/hooks.md, read on
2026-11-20 through a summarising reader that quoted it; includes and when a
folder's `CLAUDE.md` loads are from https://code.claude.com/docs/en/memory.md,
read the same way.

## What would be a regression
`CLAUDE.md` telling a session to run a command to see its lessons; no
SessionStart hook, or one with a matcher that leaves out a resume or a
compaction; a hook command that only works from the root; `./check --start`
ending with an error, leaving out a lesson in force, printing one that is
off for a product, or printing more than 10,000 characters; a file of the
lessons in force kept in the tree, which can go stale.

What no case catches: that Claude Code really runs the hook and puts its
output in front of the model. The case runs the command as the
documentation says a session start does, and reads the settings file in the
documented form. Run 009's record says what was seen of a real start.
