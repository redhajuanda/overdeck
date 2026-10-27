---
name: ws-direct
description: Implement a small, already-clear change in this multi-repo workspace (repos declared in workspace.yaml) without writing a plan — creates a git worktree under .worktrees/ for only the repos the task needs, asks which source branch to cut from (with a recommendation), then edits, checks, commits (as many logical commits as the change needs — not limited to one), opens a PR, and asks whether to merge it now or leave it open. Use when the user reports or asks for something that does not need a plan: a small and already very clear fix, copy change, rename, or one-line config they want shipped now; or when they say "edit directly", "direct implement", "just fix", "no plan", "skip the plan", "langsung edit", "edit langsung", "langsung aja", "ga usah plan". An explicit "edit directly" is this skill even if the work takes several commits. Also use to decide the path: one-shot small+clear → this skill; `/ws-explore` session of UI/wording/style tweaks → ws-explore; non-trivial → ws-plan; big or unclear → ws-intent. Not for new cross-repo contracts, multi-task features, product discussion, or `/ws-explore`.
---

# ws-direct

> **Project overlay.** If `.agents/overlays/ws-direct.md` exists, read it before anything else: its
> rules are this project's additions to this skill and win where they conflict. Pass the ones
> that concern a subagent into its brief. Never edit this skill in a project — lessons go
> through [`ws-learn`](../ws-learn/SKILL.md).

A plan exists so an implementer who has not seen the code can still be exact. When the
change is **small and already clear**, that document is overhead: the session that heard
the request can just do it. This skill is that path — same isolation as ws-implement
(worktrees, never the clone in `repositories/`), no `plans/` file.

## 0. Decide the path — before any worktree or edit

The request itself does not choose the path. **Think**, then pick one:

| Path | When |
|---|---|
| **This skill** | Small **and** already clear (below), **or** the user said "edit directly" / "no plan" / "langsung edit". An explicit ask is this skill even when the work needs several commits; only push back if it is actually a plan-sized change (new contract, unknown files, product fork) — never because it isn't one commit |
| **ws-explore** | `/ws-explore`, or a session of small UI / wording / style tweaks they will keep adding to and push later. That skill keeps the worktree until the PR merges |
| **ws-plan** | Non-trivial: several files of unknown shape, a new or changed cross-repo contract, a bug whose cause isn't obvious, a refactor, anything that would need tasks and Verify lines for someone else. Commit count alone is not a reason to plan |
| **ws-intent** | Big (likely several plans), the user is not sure what they want, or several reasonable directions. Optional — suggest it, don't start it unasked |

**Small and already clear** means all of these:

- One user-visible outcome, unambiguous (a typo, a known-wrong label, a one-line config, a
  pinpointed bug with a known fix, a rename the user spelled out).
- Roughly **≤ ~5 files**, about an hour or less. How many commits it takes is not
  the test — split the work into as many logical commits as it needs.
- **No new API / schema / DTO** between repos. A copy-only FE change does not get a BE
  worktree "just in case".
- You can name the files after a short look (`rg`, a couple of reads). If after ~2 minutes
  you still don't know what to change, it isn't clear → ws-plan.
- Not a product fork, not OpenSpec-sized (`WORKFLOW.md` § 8), not a release-only action
  (`WORKFLOW.md` § 7).

Tell the user the path in **one line** ("Direct: one copy fix in app-web, no plan.")
and continue. Don't ask "plan or implement?" when it is clearly small — that is this
skill's job. Borderline, or they said "edit directly" for something that is not small →
ask once, recommended option first.

If mid-edit the change grows (new contract, many files, a product choice) → **stop**, say
so, offer ws-plan. Don't keep going and don't create a plan.md on the side.

Do **not** write a `plans/` folder or an intent. Direct work is recorded by the PR.

## 1. Which repos — only what the task needs

From the request plus a quick `rg` along the data path in `WORKFLOW.md` § 2, list the
repos you will touch. Create a worktree for **those only**. A FE copy change is FE only;
a handler message is BE only; a contract change is not direct work.

Unsure whether a second repo is involved → that uncertainty is a reason to use ws-plan,
not a reason to create a spare worktree.

`./scripts/ws doctor`; `./scripts/ws sync` if a **needed** repo is missing or stale.

## 2. Confirm the source branch — always, before the worktree

Same idea as ws-plan § 0a: the branch you cut from is the PR's base. **Ask every time**,
unless the user already named it.

For each needed repo:

1. Default from `workspace.yaml` (`branch:`).
2. Likely better alternatives: an unmerged `feat/NNN-slug` whose plan touches the same
   files (stack on that, don't fork `development` and conflict), or a recent
   `origin/feat/…` / `origin/fix/…`
   (`git -C repositories/<repo> fetch origin` then
   `git -C repositories/<repo> branch -r --sort=-committerdate | head -5`).
3. **Recommend one, with a reason** — usually the workspace default at
   `origin/<branch>@<short sha>`; recommend a plan/PR branch instead when this edit
   belongs on top of it.

Ask with the structured-question tool (`AskUserQuestion` in Claude Code, `AskQuestion`
in Cursor): **one question**, plain words, recommended option first marked
`(Recommended)`. If every needed repo has the same recommendation, one question covering
all of them; if they differ, one question per repo, one at a time. Skip only when the
user already named the branch — then state it back in one line.

Never `git checkout` the clone in `repositories/`. A non-default source: fetch it, then
cut the worktree from `origin/<that branch>` (or the local `feat/…` if stacking on
unpushed work).

## 3. Worktrees — never the user's checkout

Slug: 2–4 snake_case words from the task (`rsvp_button_label`). Folder
`.worktrees/direct_<slug>/` must not already be in use; if it is, append `-2`.

New branch name (don't ask — tell them): `fix/<kebab-slug>` for a bug/typo,
`feat/<kebab-slug>` for a small addition, `chore/<kebab-slug>` otherwise. Not
`feat/NNN-slug` — there is no plan number.

Per **needed** repo only (`<branch>` = the source they picked):

```bash
W=<workspace>/.worktrees/direct_<slug>   # ABSOLUTE path (git -C resolves a relative one inside the repo clone)
git -C repositories/<repo> fetch origin <branch>
git -C repositories/<repo> worktree add -b <new-branch> "$W/<repo>" origin/<branch>
```

If stacking on a local unmerged branch, cut from that branch instead of `origin/<branch>`.
Worktrees live only under the workspace's `.worktrees/` — never inside a clone, never as
siblings of the workspace. `./scripts/ws doctor` lists them.

Resuming the same slug: reuse the existing worktree (`git -C repositories/<repo> worktree list`).
Dirty + another session writing there in the last ~10 min → ask who owns it first.

Copy gitignored local config from `repositories/<repo>/` (`cp`, never symlink, never
`git add`) as `WORKFLOW.md` § 4. Start that repo's install in the background the same
way. Skip repos you are not touching — no install, no copy, no worktree.

## 4. Implement

Read the needed repo's `AGENTS.md` **before writing** (workspace rule). Load its skill
list without dumping bodies:

```bash
.agents/skills/ws-implement/repo-context.sh "$W/<repo>"
```

Open only the skills whose description matches this edit.

- **One repo:** the main session implements in `$W/<repo>`. Don't spawn a subagent for a
  20-line fix — the warm-up costs more than the change.
- **Two or more repos:** one subagent per repo, in parallel, same as ws-implement § 4.
  Model from `agents.yaml` `roles.repo-implement` (plus `agents.local.yaml` overrides, ws-implement § 3). Fill [`subagent-prompt.md`](subagent-prompt.md)
  (every placeholder; there is no plan.md to point at — paste the restated task). Cap
  `roles.repo-implement.max_parallel`.

Stay inside the files the task needs. Match surrounding code. Don't drive-by refactor.
UI / product-facing copy: read the docs `WORKFLOW.md` § 3 names first.

Commit locally as you go: **one logical change per commit**, as many as the work needs
— a fix plus its test, or two independent edits, are two commits, not one. Don't fold
unrelated changes together and don't squash everything into a single commit to look
"direct". Format: `<type>(<scope>): <summary>` — no `[NNN-Tn]` (no plan). Don't commit
copied local config. Attribution lines from the system reminder, as in ws-implement.

## 5. Checks and finish

Fast checks for the files you touched: `WORKFLOW.md` § 5. UI behaviour: verify the
changed flow (`WORKFLOW.md` § 6 / the session's browser tools), not only a screenshot.
A new e2e spec, if the change is a UI interaction, is run by the main session once,
Chromium, against one dev server — implementers don't run Playwright.

Then **push and open a PR per touched repo**, main session only — this is part of
finishing, not optional:

```bash
git -C "$W/<repo>" push -u origin <new-branch>
gh pr create --repo <owner/name from `git remote get-url origin`> \
  --base <source branch> --head <new-branch> \
  --title "<type>(<scope>): <summary>" --body-file <scratch>/pr-<repo>.md
```

Body: what changed (2–4 bullets), checks → result, sibling PRs if any. Draft if checks
failed. `WORKFLOW.md` § 7 for `gh pr edit` in these repos. A PR already exists for the
head branch (`gh pr view <new-branch> --json url`) → push and update it, don't open a
second one.

Then **remove every worktree this run created** — the commits are on the PR, so the
worktree is leftover either way (merge or leave). Do this before asking. Working tree
must be clean and fully pushed (`status --porcelain` empty, nothing in
`@{u}..HEAD`); commit leftovers first. Then
`git -C repositories/<repo> worktree remove "$W/<repo>"` and `rmdir "$W"` if empty.
Keep the branch — the PR still needs it. Dirty and you can't commit it → keep that
worktree and say so; never `--force` away uncommitted work.

Tell the user, briefly: the **PR link** first, then per repo the source branch, the new
branch, checks → result, and that the worktree is gone.

Then **ask** — structured-question tool, one question, after the PRs exist, never
before and never skipped:

- Prompt: merge this PR now, or leave it open? (several PRs: "merge them now, or leave
  them open?")
- Options: **Leave it open** `(Recommended)` — they can review first; **Merge now** —
  merge into the source branch (see `WORKFLOW.md` § 7 for what a merge triggers).
- Draft or failing checks → say so in the question and still default to leaving it open.
  Don't offer merge as recommended in that case.

**Leave it open** → stop. Don't merge.

**Merge now** → merge each PR (`gh pr merge <n> --repo <owner/name> --squash`), in
the deploy order of `WORKFLOW.md` § 7 (e.g. BE before FE). Failures or a still-draft
PR → don't force-merge; tell the user. Don't merge unasked, and don't deploy anything
beyond what merging into the source branch already does.

**Learn.** Last, run [`ws-learn`](../ws-learn/SKILL.md) § *Record*: a correction, a wrong command or doc, or a detour from this change gets one line in the right project file. Nothing → skip silently.
