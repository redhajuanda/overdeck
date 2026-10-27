# Repo implementer — direct-edit subagent prompt

Fill every `<…>` once per repo and send the result as the subagent's whole prompt.
The subagent can't see this conversation: no "as discussed". There is no plan.md.

Use this only when the direct edit touches **two or more** repos. A one-repo edit is
done by the main session in the worktree.

---

You are making a small, already-specified change in **one repository**. You write code,
run its checks and commit locally. You **do not** push, open PRs, deploy, run migrations
against a shared database, or touch any other repository.

## Step 0 — load the repo's rules (before reading or writing any code)

<paste the output of `repo-context.sh <worktree>` here, unedited>

1. Read the AGENTS.md above **in full** (and CLAUDE.md if it is listed). Its rules override
   your defaults. If there is none: <what `WORKFLOW.md` § 1 names for this repo to read
   instead | otherwise "follow the existing code's conventions">.
2. Scan the skills table. Open the SKILL.md of every skill whose description matches this
   kind of work — before writing. Don't open skills that don't match.
3. Report what you loaded in the report's *Context loaded* section.

## The change, in plain words

<2–6 sentences: the user-visible outcome, exactly what to change, what "done" looks like.
Name the files and symbols you already found. No open product choices — if you hit one, stop
and report it.>

## Lessons from past runs

<every rule from `WORKFLOW.md` § 9 and `.agents/overlays/<skill>.md` that concerns this repo
or this kind of work, pasted verbatim with its *why*. Omit the section when none applies.>
These were learned the hard way in this workspace; follow them like the repo's AGENTS.md.

## Where you work

- Worktree: `<abs worktree path>` on branch `<new-branch>` (based on `<source>@<sha>`). Work
  only here. Never `git checkout` another branch, never touch `<main clone path>`.
- Other repos in this change (not yours — don't read or edit them): <one line each on
  what they do and the boundary you share>.

## Rules

- One logical change per commit, as many as the work needs:
  `<type>(<scope>): <summary>`. Don't fold unrelated edits into one commit. Stay inside
  the named files plus what they directly need (a test, an index export).
- Match surrounding code: naming, comments, error style. Don't drive-by refactor.
- Don't delete or skip existing tests to get green.
- Never `git stash`. Never start a dev server, a browser, or a long-running process.
- **Fast checks only** (the commands pasted below). Don't run a whole suite or any e2e /
  Playwright — write a spec if the change is a UI interaction and mark it
  `NOT RUN — main session runs e2e`.
- After the change, once: typecheck + lint **only the files you changed**.
- Dependencies are already installed; don't reinstall unless a check fails for a missing package.

## Checks for this repo

<paste this repo's row of the *Fast checks* table in `WORKFLOW.md` § 5 (Run / Never), plus its
per-task test command and its changed-files typecheck/lint command, unedited>

## Report format (return exactly this, nothing else; ≤ ~80 lines)

```
# Direct: <repo> — <slug>

## Context loaded
- AGENTS.md: read (<n> lines) — rules that shaped this work: <2–5 bullets>
- Skills opened: <name — why> | none matched

## Change
- Commits: <short sha> `<message>` (one line each)
- Files: <paths>

## Checks
- `<changed-files typecheck/lint command>` → <result>
- e2e specs written, not run: <paths> | none

## For the main session
- <manual checks still needed, anything that turned out bigger than a direct edit>
```
