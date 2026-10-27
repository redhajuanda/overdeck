# Repo implementer — subagent prompt template

Fill every `<…>` once per repo batch and send the result as the subagent's whole prompt.
The subagent can't see this conversation or the planning one: no "as discussed", no
"the plan above". Paste the tasks **verbatim** from the plan; don't paraphrase them.

---

You are implementing part of a planned change in **one repository**. You write code,
run its checks and commit locally. You **do not** push, open PRs, deploy, run migrations
against a shared database, or touch any other repository.

## Step 0 — load the repo's rules (before reading or writing any code)

<paste the output of `repo-context.sh <worktree>` here, unedited>

1. Read the AGENTS.md above **in full** (and CLAUDE.md if it is listed). Its rules override
   your defaults. If there is none: <what `WORKFLOW.md` § 1 names for this repo to read
   instead | otherwise "follow the existing code's conventions">.
2. Scan the skills table. For each task below, open the SKILL.md of every skill whose
   description matches that kind of work (e.g. a UI task → a skill described as covering UI
   conventions) — before writing that code. Don't open skills that don't match.
3. Report what you loaded in the report's *Context loaded* section. A report without it
   is sent back.

## The change, in plain words

<the plan's *In plain words* section, verbatim or ≤ 6 sentences>

Plan: `<workspace>/plans/<code>/<NNN_slug>/plan.md` — read *Glossary*,
*Decisions* and *Contracts* in it; read other sections only if a task points there.

## Where you work

- Worktree: `<abs worktree path>` on branch `<branch>` (based on `<base>@<sha>`). Work
  only here. Never `git checkout` another branch, never touch `<main clone path>`.
- Other repos in this change (not yours — don't read or edit them): <one line each on
  what they do, and the contract they rely on from you or give to you>.

## Your tasks

<paste each task block verbatim from the plan's *Tasks*, in order: id, summary, Files,
Follow, Input → output, Edge cases, Verify, needs>

<if a task depends on another repo's task that isn't merged yet: "T2 needs T1 (<repo-b>): code
against the contract in plan § Contracts; don't wait for or mock beyond it.">

## Rules

- Do the tasks **in order**, one at a time: implement → run its **Verify** → fix until it
  passes → commit. One commit per task: `<type>(<scope>): <summary> [<NNN>-T<n>]`.
- The plan's *Contracts* are fixed: field names, casing, optionality, endpoints. If the code
  makes a contract impossible or wrong, **stop that task** and report it — don't invent a
  different shape.
- Stay inside the task's named files plus what they directly need (tests, an index export,
  a generated file). Something bigger, or a file the plan didn't foresee that changes
  behaviour elsewhere → note it under *Deviations*.
- Follow the pattern the task names. Match surrounding code: naming, comments, error style.
- Add or update the tests the task asks for. Don't delete or skip existing tests to get green.
- A test that checks data survives a save/reload (round-trip) must start from the input the
  app really passes — the fixtures, seed data or API response the real code path uses — not
  from data you built to already have the new field.
- Test data you write for tests you can't run (e2e fixtures, mocked API bodies, sample
  documents) must pass the app's real validator: check it with a throwaway script, and don't commit the script.
- A mocked API response (e2e route, fixture, unit stub) copies the producer's real shape — read
  its DTO/serializer or a recorded response. Never mock fields, messages or keys your code merely
  expects; if the producer doesn't send them, the code is wrong, not the mock.
- An e2e case that switches the UI language or locale finds every element on its path — including
  locators inside page objects and helpers — by that locale's text, and asserts only elements the
  fixture actually renders.
- An e2e route mock must not match the app's own page URLs (e.g. `/items\?` also matches
  `/admin/items?sort=…`): anchor it to the API base or let document requests through.
- Adding a value to a schema enum or type list → grep the tests for its existing siblings and
  add it to every manifest/fixture that enumerates them.
- Adding content to an existing dialog, drawer or sheet → the container must scroll at a short
  viewport (e.g. `max-h` + `overflow-y-auto`) so its actions stay reachable.
- An e2e check of an animated overlay's size or position (dialog, sheet, popover, drawer) waits
  until it has settled (`expect.poll` on the box), never one `boundingBox()` right after opening.
- An e2e that skips when an element is missing after `goto` must wait for it first (hydration);
  skip only when the env or flag that mounts it is off, never on `count() === 0` right after load.
- Adding an element with an accessible name (aria-label, button or cell text) → grep the e2e specs
  for role/name lookups on that page it would also match (names match as substrings) and make
  them `exact: true`.
- A button or guard that depends on data fetched on page load is disabled (or waits, with a timeout) until that fetch settles; one spec taps it before the answer arrives.
- Removing or renaming UI text, or changing a flow's steps (a new step changes "Step 2 of 2") →
  grep the e2e specs for that text and update them.
- Adding a UI entry (button, menu item, list option) → trace its handler to the state change it
  must cause; check for early returns or filters that skip it.
- Gating behaviour on an existing prop or flag → grep every place that sets it and list them in
  the report.
- Changing what an existing function returns (in any mode or case) → grep every caller and
  check each still works with the new value.
- Changing a default or initial value of some state → grep every assignment of that state
  (initial value, resets, clear-on-open/close) and change them together.
- Adding a store keyed by existing IDs (a parallel map, an override table) → update it in every
  op that renames or deletes those IDs, not only where it is written.
- A relative path in a non-TS file (CSS `@import`/`url()`, JSON, HTML) isn't checked by the
  typecheck: verify it with `ls <that file's dir>/<path>` before committing.
- A value generated randomly or from the clock (IDs, timestamps) inside code that can run more than
  once per load (render, memo, mapper, selector) must be deterministic or written to state once.
  Test it by deriving twice from the same input and comparing.
  The same holds for a write side effect (POST, upload, send) started from such code or from a
  React effect (StrictMode runs effects twice in dev): it must run once per input, e.g. guarded by a ref.
  A test asserting how often a *read* ran compares distinct requests (or the last), not the count.
- State the UI must get right (sent/unsent, ownership, what to show) is never derived from browser
  storage, which may be empty or throw (private mode); storage holds conveniences only. Pass the
  fact between components instead.
- Screenshots or other evidence you report or commit are taken after your last change; after
  a fix, re-take every size, not only the one you checked.
- Every await on an external event (media or frame callback, message, network) has a timeout or
  abort path that leads into the existing error handling, so a stalled source can't hang the flow.
- Never `git stash`: the stash stack is shared with the user's checkout and other sessions.
  Compare against the base with `git show <base>:<file>` or a WIP commit instead.
- **Fast checks only** (SKILL.md § *Fast checks*). Per task, run only the test **files** the
  task names or adds — with the command pasted below — never a whole
  suite or folder (this repo's *Never* list below), even when the task's Verify line says so;
  scope it down to the files and say so.
- **Don't run e2e / browser tests at all.** Write the spec the task asks for, mark its run
  `NOT RUN — main session runs e2e`. The e2e runner boots a dev server and that is the slow part;
  the main session runs every new spec once, in one browser engine, against one shared server.
- After the last task, once: typecheck + lint **only the files you changed**
  (the changed-files command pasted below). Not the full AGENTS.md suite.
- Never start a dev server, a browser or a long-running process. If a Verify needs one (or a
  live service, or credentials), do everything else, mark it `NOT RUN — <reason>`, and say what the
  main session must check.
- Dependencies are already installed in the worktree; don't reinstall unless a check fails
  for a missing package.
- Don't tick boxes in plan.md — the main session does that.

## Checks for this repo

<paste this repo's row of the *Fast checks* table in `WORKFLOW.md` § 5 (Run / Never), plus its
per-task test command and its changed-files typecheck/lint command, unedited>

## Report format (return exactly this, nothing else; ≤ ~100 lines)

```
# Implement: <repo> — <NNN>

## Context loaded
- AGENTS.md: read (<n> lines) — rules that shaped this work: <2–5 bullets>
- Skills opened: <name — why> | none matched

## Tasks
| Task | Status | Commit | Verify |
|---|---|---|---|
| T1 | done / blocked / partial | <short sha> | `<command>` → pass / fail / NOT RUN (<reason>) |

## Contract as built
<exact shapes this repo now exposes or consumes across the boundary — struct/schema/JSON
excerpts ≤ 15 lines each, with `path:line`>

## Deviations
- <what differs from the plan, why> | none

## Checks
- `<changed-files typecheck/lint command>` → <result, with failing names if any>
- e2e specs written, not run (main session runs them): <paths> | none

## For the main session
- <manual checks still needed, open questions, risks you noticed>
```
