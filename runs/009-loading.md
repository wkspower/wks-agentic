# Run 009 — loading: the lessons in force are in front of a session with no step to take

- **Prompt:** none under `prompts/`. This run changes the scaffold and tests
  no product prompt.
- **Branch:** `run/009-loading`, 2026-11-20, started from `01f6843` with the
  school library in `product/`. The product was not changed.

## How the instruction arrived

As an automated notice written by the coordinating session, which says so
itself. The person's own words, as that notice reports them: on reading that
"nobody knows whether [a session] will run that command before working",
"sounds like we are relying on non determinism for something we want
determinism?", and then "yes" to the offer of a run that fixes the loading
first. The rule ("what must happen is done by the tooling, and the entry
file holds only what needs judgement"), the two ways, their order and the
constraints are the coordinating session's. No lesson of this run says the
person decided, read or accepted more than those words (L0037).

## Questions

None. The instruction said what to do and gave the order of the two ways.

## What changed

Before, the first instruction in `CLAUDE.md` was "run `./check --lessons`
and read what it prints". Now `.claude/settings.json` has a SessionStart
hook with no matcher that runs `"${CLAUDE_PROJECT_DIR}"/check --start`, and
Claude Code adds what a SessionStart hook prints to the context. It prints:

- with a product, the lesson lines in force besides the `always` ones, and
  each label that is off with its count;
- with no product, every label that exists and under it the lines it
  brings, since choosing labels is the first thing a new product does.

It is worked out from `LESSONS.md` and `product/LABELS` each time, in 0.05 s.
`CLAUDE.md` still holds only the `always` lessons (what run 008 gained), and
now tells no session to run anything for its lessons.

## The include, and why it was not taken

The way proposed first was a file of the lines in force, written by the
check, that `CLAUDE.md` includes with `@path`, refused when stale. It was
rejected before any code, on three of the constraints taken together:

1. The base is this tree with `product/` removed and no step after. So
   every file outside `product/` is the same in both trees, byte for byte.
2. A file that holds the library's lines is stale on the base, and a stale
   file must fail the check, and the base must pass.
3. A file inside `product/` goes with the folder, but then `CLAUDE.md` on
   the base includes a file that is not there, which the documentation does
   not describe and the instruction said not to rely on.

A folder's own `CLAUDE.md` was looked at as a way round and is none: the
documentation says it loads when a file in that folder is first read, not
at the start. The hook has no file, so nothing can be stale and no "stale
file is refused" case exists; the constraint that asked for one has nothing
left to refuse. This is in L0041's Reason so that the next session does not
propose the include again.

## Where the hook does not run

- Anything that reads `CLAUDE.md` and is not Claude Code.
- Claude Code with hooks switched off: `disableAllHooks` in a settings
  file, or an organisation that allows only its own hooks
  (`allowManagedHooksOnly`).
- Where the command fails (no `python3`, a broken `check`): the session
  goes on and the model sees nothing. `./check --start` itself always ends
  with 0 and prints what is wrong in the record instead.
- Sub-agents: the documentation read does not say SessionStart fires for
  one. Not tried.
- Past 10,000 characters the session gets a preview of 2,000 and a file's
  path. `./check` fails before that, on either tree.

For these, `CLAUDE.md` says what the text begins with and tells a session
that does not have it to say so first and take it from `./check --start`.
That is a fallback which depends on the model, and it is named as one.

## The bytes a session has at its start

| | Before (run 008, `01f6843`) | After |
|---|---|---|
| with the library, with no step taken | 5,605: `CLAUDE.md`, and none of the library's 14 lessons | 8,889: `CLAUDE.md` 6,025 and 2,864 from the hook |
| with the library, if the session ran the command | 8,368: 5,605 and 2,763 | the same 8,889 |
| on the base, with no step taken | 5,605, and no label named | 10,270: `CLAUDE.md` 6,025 and 4,245 from the hook |
| on the base, if the session ran the command | 5,981: 5,605 and 376, the labels with counts only | the same 10,270 |
| on the base, to see what each label brings | 6 more commands, 4,215 bytes | nothing more |

`CLAUDE.md` grew by 420 bytes: the line of L0041 (218) and a first
instruction that is longer than the one it replaced. The hook's text is 101
bytes more than `./check --lessons` printed, for its first line. The base
costs more than before because it now carries what a session there had to
fetch with seven commands. The check counts the hook's text in characters
(2,863 and 4,243), because that is what Claude Code limits.

## Lessons: 1 added, with a case, case first; 2 amended

| | Lesson | Case |
|---|---|---|
| Added | L0041: what must happen at the start of a session is done by tooling | `cases/0041-lessons-load-at-start` |
| Amended | L0039: the sentence lost "and a session reads those in force from `./check --lessons`" | not changed; it still proves what the command prints |
| Amended | L0023: one sentence in its Source on where the lines are shown | not changed |

Case first: commit `7d62771` has L0041 and its case failing on the entry
file as it stood ("CLAUDE.md tells the session to run `./check --lessons`:
whether the lessons are read then depends on the model"). The next commit
is the change.

The case reads the settings file in the documented form and runs the hook's
command as a start would: through `sh`, from another directory, with
`CLAUDE_PROJECT_DIR` naming the tree. It works out what must be printed
without the check's code. It accepts four trees (the base; a product of one
label; the same after a second label is declared, with no step between; a
label no lesson carries, which is named and does not fail) and refuses
eight wrong variants, each a small change to a copy: no settings file; a
matcher of `startup` only; a command that works only from the root; a
command that ends with an error; one label's lessons whatever the product;
the lessons that are off printed as well; nothing printed; more than 10,000
characters.

The selftest refuses the 26 wrong trees it refused and 6 more (no hook;
settings that are not JSON; a hook that runs something else; a matcher;
too long with the product; too long without it), and accepts the same 7.

## Seen of a real start

The instruction said one thing could not be proved from inside. Part of it
could be looked at: the Claude Code that runs here (2.1.329) starts a
headless session with `claude -p`, and prints its start-up events.

| Tree | The hook, in the events | What the model said, with no tool and one turn |
|---|---|---|
| a copy with the library, in a git folder under the home folder | ran, ended 0, 2,863 characters | `CLAUDE.md` is there with 14 `always` lessons; the text lists L0006 to L0036, the 14 right numbers |
| the same without `product/` | ran, ended 0, 4,243 characters | 14 `always` lessons; six labels with 1, 1, 9, 1, 8 and 4 lessons, which is right |
| a copy in the scratch folder under `/tmp`, with the library | ran, ended 0, 2,863 characters | the 14 right numbers; and, asked separately, that it had no `CLAUDE.md` at all |
| the same without `product/` | ran, ended 0, 4,243 characters | the six labels, each with its right numbers |
| the same with `.claude/` removed (the control) | no hook event | no such text, and no `CLAUDE.md` |

The third and last rows show something not looked for: in a folder under
`/tmp` that is not a git repository, the headless session did not have
`CLAUDE.md`, and the hook's text arrived all the same. Why was not found
out. It says nothing about a session on the repository, where this
session's own `CLAUDE.md` was loaded.

What this does not show: a session the person starts, in the app, on a
fresh clone. The hook's events are a program's output; that the text is in
front of the model is the model's own answer, once per tree (L0003 applies
to it). `HANDOFF.md` says what the next run should look for.

## Decided and not asked

1. **The hook, not the include**, on the argument above and without
   building the include to watch it fail.
2. **On the base the hook prints every lesson that is off**, under its
   label: 4,245 bytes. "What each label brings" was read as the lines
   themselves, not the counts. With a product the lessons that are off are
   not printed, only their labels and counts.
3. **A new command, `./check --start`**, for the hook. `./check --lessons`
   is as it was and its case was not touched.
4. `./check --start` always ends with 0, and puts what is wrong in the
   record (a label no lesson carries, a line in the wrong form) in the text.
5. **The hook has no matcher**: it fires on a new session, a resume, a
   clear and a compaction. After a compaction the text is added again.
6. `./check` itself fails with no hook, a hook with a matcher or another
   command, or a text past 10,000 characters on either tree. The settings
   file is compared with one fixed command; the case runs whatever command
   is there.
7. The command is in the shell form with `"${CLAUDE_PROJECT_DIR}"` in
   quotes. The documentation prefers a form with `args`; the shell form is
   what the case can run with `sh` and what the installed version was seen
   to run.
8. **`CLAUDE.md` keeps one sentence for a session that has no such text**:
   say so first and take it from `./check --start`. The case allows that
   wording and refuses "run `./check --lessons`"; that part of the case is
   a search for words and would not catch the same instruction worded
   another way.
9. The summary line of the check ends `at the start of a session CLAUDE.md
   N bytes and N characters from the hook (N with no product)`, in place of
   `CLAUDE.md N bytes, and N of lessons in force besides`.
10. `./check --plant` writes the settings file too, so the planted trees of
    four other cases pass the new rule. No other case changed.
11. Seven headless sessions were started with the installed `claude` to
    look at a real start, each one question and one turn. Not asked.
12. The rejected include is in L0041 and has no lesson of its own.
13. No Stop hook, as told.

## Check at the end

    lessons 38 · in force 28 · not in force 10 · with a case 31 · prose only 7 · cases run 25 · cases not run 9 · product: school library, web pages, local web server, python stdlib and sqlite on localhost · product 800 lines · cases in force 2404 lines (3.0 to 1) · at the start of a session CLAUDE.md 6025 bytes and 2863 characters from the hook (4243 with no product) · 67 s

Without `product/` (the last commit unpacked in a scratch directory, the
folder removed, no other step):

    lessons 38 · in force 14 · not in force 24 · with a case 31 · prose only 7 · cases run 9 · cases not run 25 · product: none · product 0 lines · cases in force 563 lines · at the start of a session CLAUDE.md 6025 bytes and 4243 characters from the hook (4243 with no product) · 6 s

`./check --selftest`: accepted 7 of 7 right trees, refused 32 of 32 wrong.
The cases refuse 75 wrong variants: the 67 over the product, as in run 008,
and the 8 of the new case. The check took 60 s on this machine before any
change and 67 s after; run 008 measured 41 s on its own.

## Size

Product 800 lines, not changed. Cases 3,266 lines (3,079); the new one is
187. `check` 538 lines (456). Lesson files 1,171 lines (1,078). `CLAUDE.md`
6,025 bytes (5,605), `LESSONS.md` 4,083 (4,012).

## Time and agents

About 45 minutes. One sub-agent, which fetched the two documentation pages
and quoted them; it wrote nothing here.

## Not verified

- **No session of the person's has started from this tree.** See "Seen of a
  real start" for what was looked at and what that is worth.
- The documentation was read through a summarising reader that quoted it.
  About a tenth of the hooks page was not read, and whether SessionStart
  fires for a sub-agent was not found in what was.
- Whether the app asks the person to trust the folder before it runs a
  hook from the repository, and what a session has if they decline. The
  headless starts asked nothing.
- A resume, a clear and a compaction were not tried; that the hook fires
  on them is from the documentation and from the hook having no matcher.
- The pet shop's cases were not run: `caselib` did not change.
- The product was not touched and was not driven by script (L0013):
  nothing a person would see changed.
- The person has seen none of this, and has not read L0041.
