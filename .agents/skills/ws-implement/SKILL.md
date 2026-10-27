---
name: ws-implement
description: Implement a plan from plans/<member>/NNN_slug/plan.md in this multi-repo workspace (repos declared in `workspace.yaml`) — dispatches one implementer subagent per repository in git worktrees, each briefed with its repo's AGENTS.md and skill descriptions, checks the cross-repo contracts, runs one final code review of the whole change, ticks tasks off, then commits, pushes and opens a PR per repo into the plan's source branch. Use when the user asks to implement, build, execute, ship or "kerjakan" a plan, a plan number ("implement 042"), or the next tasks of a plan. Also use to resume a half-implemented plan.
---

# ws-implement

> **Project overlay.** If `.agents/overlays/ws-implement.md` exists, read it before anything else: its
> rules are this project's additions to this skill and win where they conflict. Pass the ones
> that concern a subagent into its brief. Never edit this skill in a project — lessons go
> through [`ws-learn`](../ws-learn/SKILL.md).

The plan already did the thinking: it names the files, the contracts and a Verify per task.
So implementing is mostly **routing and review**, and the fast, cheap, correct way is:

- **One subagent per repo, not per task.** A repo's tasks share files and conventions; one
  agent that loaded AGENTS.md once does them all in order. Per-task agents re-pay the warm-up.
- **Everything parallel by default.** All repos start at once and build against the plan's
  *Contracts*. Something waits only when it imports another repo's real code.
- **The main session never writes repo code and never reads file dumps.** It briefs, checks
  contracts, runs one final review, and owns every tick in the plan.
- **One review, at the end, one fix round.** Between waves only the contracts are checked.

Critical path: briefs → one parallel implement pass (+ a later wave only when code must be
imported) → one parallel review → one parallel fix round → finish.

## 0. Preconditions

1. Find the plan: `./scripts/ws find plan <id, number or slug>` → `plans/<code>/NNN_slug/plan.md`
   (ask only if several active plans match). Read it fully —
   header, *Glossary*, *Decisions*, *Contracts*, *Tasks*, *Rollout*, *Acceptance*. Also
   `context/architecture/contracts.md` (if filled in) and any note on the plan's `Context:` line.
2. `./scripts/ws doctor`; `./scripts/ws sync` if anything is missing or stale.
3. **Drift check.** For each repo in the header, compare `Based on:` SHA with the branch tip:
   `git -C repositories/<repo> log --oneline <sha>..origin/<branch> -- <files the tasks name>`.
   Commits on those files → re-verify the affected tasks first (ws-plan § *Revising*). Don't
   implement against a plan whose files moved under it.
4. Unanswered *Open questions* that block a task → ask the user before dispatching that
   task, following **Asking the user** below. Non-blocking questions don't stop the work.
5. Start the run record — the retro's metrics read it. Add a line under the plan header:
   `Run: <date -u +%FT%TZ> → ` (resuming: leave the existing start).
6. Which tasks: the user's selection, else every unticked task. Tasks typed `release` or
   anything on the release-only list (`WORKFLOW.md` § 7: deploys, shared-DB migrations, publishing, pushes) → **never by a
   subagent**; they become next steps for the user.

### Asking the user

Every question to the user — open questions here, or anything that comes up mid-run — is asked
**one at a time**: one `AskUserQuestion` call with one question, wait for the answer, then the
next. Never bundle several questions in one call.

- **Plain words.** Write for someone who hasn't read the plan or the code: no task ids,
  file paths, type names or jargon without a short explanation.
- **Clear context first.** In the question say what the feature is, what situation the choice
  is about, and what changes for the user depending on the answer. If it helps, a
  `preview` with a tiny example or mockup.
- **Images and layouts are linked, not pathed.** When the user must look at images or a layout to
  answer, publish them as a viewable page and link it. A local file path can't be opened from the
  terminal (139: the art-pick question was lost).
- **Concrete options.** 2–4 options, each describing its effect in one line; recommended
  option first, marked `(Recommended)`, with the reason.
- Write each answer into the plan's *Decisions* as `- <date> · user: <answer>` and strike the
  question, before asking the next one.

## 1. Worktrees — never the user's checkout

Per repo touched, branch `feat/NNN-slug` off the plan's **source branch** — the branch in its
`Based on:` header (fallback: `workspace.yaml`); `<branch>` below means that branch:

```bash
W=<workspace>/.worktrees/NNN_slug   # ABSOLUTE path (git -C resolves a relative one inside the repo clone); the plan's full folder name, gitignored
git -C repositories/<repo> fetch origin <branch>
git -C repositories/<repo> worktree add -b feat/NNN-slug "$W/<repo>" origin/<branch>
```

Worktrees live only under the workspace's `.worktrees/` — never inside a repo clone (its
typecheck / lint / test globs would pick them up) and never as siblings of the workspace.
`./scripts/ws doctor` lists them all and flags stale ones.

The worktree folder is the plan's **full** directory name (`.worktrees/NNN_slug/`),
never the bare number. Resuming? Reuse the existing worktree/branch
(`git -C repositories/<repo> worktree list`) — older runs may sit under `.worktrees/NNN/`.
Before reusing one with uncommitted files, check that no other session is running the plan:
look for files changed there in the last ~10 min (`find "$W" -newermt '<now − 10 min, ISO>'`)
and for busy peer sessions (`ListAgents`). If either shows up, ask the user which session owns
the run before dispatching anything.

A fresh worktree has only tracked files. Copy any gitignored local config it needs to build,
run or test from the default clone `repositories/<repo>/` (the list per repo is in `WORKFLOW.md` § 4) with `cp`, never `git add`. Copy, don't
symlink, so a worktree edit can't change the user's checkout. Skip build output and caches
(`WORKFLOW.md` § 4 lists them).

Start dependency installs **in the background** right away (`run_in_background`), with the install command per repo from `WORKFLOW.md` § 4 (background shells may lack tools on PATH; § 4 gives any prefix) — whatever the
repo's AGENTS.md uses. Write the briefs (§ 4) while they run; dispatch when they're done, so
parallel agents never race an install.

## 2. Waves — one by default

Group the selected tasks by repo. Default: **a single wave**, every repo at once.

- `needs:` a task in the **same repo** → same batch, later in order. Never a separate agent.
- `needs:` a task in **another repo** whose shape is in plan § *Contracts* → same wave;
  the brief says "code against plan § Contracts".
- A later wave **only** when a task imports the other repo's real output: generated
  types/client, a migration it must run against, content it must render.
- Later waves don't wait for the whole previous wave: a batch starts the moment the batches
  it depends on pass their contract check (§ 5).

Tell the user the plan in 1–3 lines before dispatching (`<repo-b> T1–T2 ∥ <repo-a> T3–T5 ∥ <repo-c> T7`,
plus anything that waits and why). At most `roles.repo-implement.max_parallel` agents at once.

## 3. Pick the model — from `agents.yaml`

Read `agents.yaml` at the workspace root, then `agents.local.yaml` if it exists (personal overrides, key by key — see the header of `agents.yaml`). Take `subagents.claude`
(Claude Code), `subagents.codex` (Codex) or `subagents.cursor` (Cursor), then apply overrides under the role: `roles.repo-implement` for
implementers, `roles.change-review` for reviewers (§ 7). Never hard-code a model here or in a
prompt. Missing file → use the session default and say so.

## 4. Brief each repo agent

For every repo batch:

1. **Load the repo's context — mandatory.** Run, against the worktree:
   ```bash
   .agents/skills/ws-implement/repo-context.sh "$W/<repo>"
   ```
   It prints the AGENTS.md path (or "none") and each repo skill's **name + description +
   SKILL.md path** — descriptions only, never the skill bodies. Paste its output unedited into
   *Step 0* of the brief. Don't read AGENTS.md or the skills into the main session yourself;
   the brief makes the subagent read AGENTS.md in full and open only the skills whose
   description matches its tasks.
   *Why explicit:* a subagent's working directory is the workspace root, so the repo's
   AGENTS.md/CLAUDE.md and `.claude/skills` aren't reliably loaded for it. Listing them in the
   prompt is the only guarantee — in Claude Code and in Codex alike.
2. Fill [`subagent-prompt.md`](subagent-prompt.md): every placeholder (including *Checks for this
   repo*, pasted from `WORKFLOW.md` § 5 for that repo), task blocks pasted
   verbatim, worktree path, branch, the other repos' contract in one line each.
3. Dispatch all ready batches **in one message**:
   - **Claude Code** — `Agent`, one call per repo: `subagent_type: "general-purpose"`,
     `model` = the family word of the `agents.yaml` ID (`claude-sonnet-5-5` → `sonnet`; the Agent tool only takes family words; it resolves to that family's current model, so an older ID in `agents.yaml` shows up as a mismatch below). After launch, check the result's `resolvedModel` equals the `agents.yaml` ID; if not, stop and tell the user, `effort` from `agents.yaml`, `description: "Implement <repo> NNN"`.
     Results arrive as notifications; don't do their work or poll meanwhile. **Keep each
     agent's id** — fixes go back to the same agent (§ 8).
   - **Codex** — native spawn tool with the `agents.yaml` model if present; otherwise:
     ```bash
     codex exec -m <model> -c model_reasoning_effort=<effort> -s <sandbox> \
       -C "$W/<repo>" --skip-git-repo-check --ephemeral \
       -o <scratch>/impl-<repo>.md - < <scratch>/brief-<repo>.md
     ```
     Tests that need the network or caches outside the worktree (module / package stores) also
     need `-c sandbox_workspace_write.network_access=true` and those dirs as writable roots
     (`WORKFLOW.md` § 5).
   - **Cursor** — its subagent tool with `model` from the `cursor` block (`inherit` = this
     chat's model). Cursor can ignore a pinned model, so report which model you asked for.

## 5. Contract check — as each report arrives (minutes, not a review)

Don't wait for all agents; check each report when it lands:

1. **Context loaded** present: AGENTS.md read, skills chosen sensibly (a task whose kind of work
   matches a listed skill's description, where the report opened none of the matching skills,
   is noted for the final review).
2. **Commits exist and are scoped:** `git -C "$W/<repo>" log --oneline origin/<branch>..HEAD` and
   `git -C "$W/<repo>" diff --stat origin/<branch>...HEAD` (three dots: a moved base must not show
   as reverse changes). Files outside the task lists need a
   matching *Deviation*.
3. **Contract as built = plan § Contracts**, field by field (names, casing, optional vs
   required, enums), and = the other repos' *Contract as built* once they arrive. What the
   plan leaves unsaid (error shape, ID format, time, casing) follows
   `context/architecture/contracts.md`. Open the
   diff only at those boundary lines.
4. Any task `blocked`/`partial`, any `NOT RUN` → note it for § 8 / § 9.

A contract mismatch is the one thing fixed **now** (`SendMessage` to that agent) instead of at
the end, because dependent batches would build on it. Everything else waits for § 7.
Passed → tick tasks provisionally (§ 6) and start any batch that was waiting on this one.

## 6. Record progress

In `plan.md`, as batches pass § 5:
- tick `- [x]` for each task and append `· <repo>@<short sha>`;
- add *Deviations* worth keeping to *Decisions* (one line each);
- `Status:` → `in progress`; after § 9 → `implemented` (only release tasks left).

## 7. Final review — once, after all batches pass § 5

**Start the e2e now, not in § 9.** As soon as a plan's batches pass § 5, start its dev server and
run the new or named specs (§ *Fast checks*, selection rules in `WORKFLOW.md` § 5) in the
background, in parallel with the review. Treat failures as findings for the § 8 fix round;
after the fix, re-run only the failed specs. A change with no e2e-relevant change (see
`WORKFLOW.md` § 5) skips this. In a multi-plan run, ws-multi-implement runs e2e once for the
whole run instead.

Size it first. Per worktree, excluding lockfiles, generated code and snapshots:

```bash
git -C "$W/<repo>" diff --shortstat origin/<branch>...HEAD -- . <excludes: `WORKFLOW.md` § 5>
```

| Changed lines, all repos together | Review |
|---|---|
| ≤ ~300 | **No agent.** The main session reads the diff itself with the § 7 checklist from [`review-prompt.md`](review-prompt.md). |
| > ~300 | **One** reviewer for the whole change, however large: every repo + the cross-repo trace in one agent. It loads **every touched repo's** AGENTS.md and skill list (one `repo-context.sh` block per repo), so it reviews each repo against that repo's own rules. Never split a review per repo: separate reviewers find the same boundary bug twice and cost a pool slot and a warm-up each. |

Fill [`review-prompt.md`](review-prompt.md): worktree paths and
base refs (the reviewer runs `git diff` itself — never paste diffs into a brief), the
*Contract as built* boundary list collected in § 5, the plan's *Edge cases* / *Acceptance* /
*Rollout*, the `repo-context.sh` output for **each** touched repo, and anything § 5 noted. Model from
`roles.change-review`, passed the same way as in § 4. Reviewers are **read-only**.

## 8. One fix round

1. **Verify only blocker and major findings** yourself — open the cited lines; drop what
   doesn't hold. Minor findings aren't fixed; they go to the user's summary.
2. Send all confirmed findings for a repo in **one** `SendMessage` to that repo's implementer
   (Codex: re-run with its last report plus the findings), all repos **in parallel**: file,
   what's wrong, what the plan says, the reviewer's failure scenario.
3. Check only the fix diff (`git -C "$W/<repo>" diff <sha-before-fix>..HEAD`) and the
   implementer's re-run Verify. No second reviewer run.
4. Still wrong → fix a one-liner yourself; otherwise stop and list it for the user. No second
   round.

A real plan defect (contract impossible, missing task) → fix the plan first (ws-plan
§ *Revising*), then continue.

## 9. Finish

Run once, in the main session, the **fast checks** below — in parallel, in the background:
- per repo, the changed-files typecheck/lint and the touched unit tests (table);
- every e2e spec the implementers wrote or the plan names, in the one browser engine the
  profile names, against **one** dev server you start once and reuse;
- browser/visual checks the plan's *Testing* or *Acceptance* asks for (`agent-browser` skill,
  at the viewport the plan names; default in `WORKFLOW.md` § 6) on that same server, and any
  `NOT RUN` item left from the implementers. If `WORKFLOW.md` § 6 names a screenshot script for
  rendering changes, use it with the dev server pointed at the dev API — run it as soon as a
  plan passes § 5, not at the end.
- Stop a dev server by its port's PID (`ss -ltnp | grep ':<port> '`, port per `WORKFLOW.md` § 6),
  never `pkill -f <pattern>` — the pattern matches your own shell and kills it. Check free
  space where the profile says (`WORKFLOW.md` § 6) before starting the server and the browser;
  a full temp dir ends the session.

### Fast checks

Scope every check to what the change touched; the full suites are CI's job. Run a full suite
only when the user asks for it. The concrete commands per repo — what to run, and what never to
run unless asked — are the table in `WORKFLOW.md` § 5 (the changed-files typecheck/lint, the
touched unit tests, the new or named e2e specs against one already-running dev server).

Why: whole e2e folders × a dev server compiling every page cost an implementer most of ~18 min;
the touched files take ~2–4 min. Start the dev server in the background as soon as installs
finish, so it has compiled by the time the specs run. A dev server compiles each route lazily, so once it is up, request every route the specs
open one time (`curl -s -o /dev/null <origin>/<route>`) before the first spec run; a cold route
otherwise times out the first test that opens it.

Then **commit, push and open a PR per repo** — main session only, never a subagent:

1. **Atomic commits.** `git -C "$W/<repo>" status --porcelain` must end empty. Anything
   left (your one-line fixes, formatter output, regenerated files) → commit it, one logical
   change per commit, same format as the implementers:
   `<type>(<scope>): <summary> [<NNN>-T<n>]` (fix-round commits: `fix(<scope>): … [<NNN>-review]`).
   Never fold unrelated changes into one commit, never `git add -A` blindly — stage by file,
   and never commit copied local config (the files copied per `WORKFLOW.md` § 4).
   End each message with the attribution lines from the system reminder.
2. **Push** the branch: `git -C "$W/<repo>" push -u origin feat/NNN-slug`.
3. **Open the PR into the plan's source branch** — the branch the worktree was cut from
   (the `Based on:` branch; in a stacked multi-run, the predecessor's `feat/PPP-slug`):
   ```bash
   gh pr create --repo <owner/name from `git remote get-url origin`> \
     --base <source branch> --head feat/NNN-slug \
     --title "<type>(<scope>): <plan title> [NNN]" --body-file <scratchpad>/pr-<repo>.md
   ```
   Body: what the plan changes in this repo (2–4 bullets), tasks done, checks run → result,
   release steps from *Rollout*, links to the sibling PRs in the other repos (edit the earlier
   PRs once all exist: `gh api -X PATCH repos/<owner>/<name>/pulls/<n> -F body=@<file>` — `gh pr edit`
   can fail on a Projects-classic GraphQL error and leave the body unchanged), then the PR attribution line from the
   system reminder. Checks failing or tasks left → open it as `--draft` and say why in the body.
   Resuming and a PR already exists (`gh pr view feat/NNN-slug --json url`) → push and
   update it instead of opening a new one.
4. Record each PR URL in `plan.md` next to the repo in the header (`<repo> PR: <url>`).

Then tell the user, briefly:
- **the PR link per repo** (first, so it can't be missed) and its base branch;
- per repo: branch, worktree path, commits, checks → result;
- tasks done / left, and the release tasks they must do (deploy order from *Rollout*);
- review: what was found and fixed, minor findings not fixed, anything you couldn't verify.

Then close the run record: finish the plan's `Run:` line with `date -u +%FT%TZ`.
**Then run the retrospective, now, before you stop** — follow [`retro.md`](retro.md). It is
the last step of this skill, not an optional extra. A run stopped early (user cancels,
blocked) gets its end time and a retro too, so its waste is reviewed.

Push and open PRs only in § 9, after the review and fix round. Never merge, deploy or remove
worktrees unless asked. Cleanup after merge:
`git -C repositories/<repo> worktree remove "$W/<repo>"`, then `rmdir "$W"` — or let `ws-archive` do it.
