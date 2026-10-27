---
name: ws-explore
description: Open a sticky worktree session for small, iterative changes in this multi-repo workspace (repos in workspace.yaml) — UI, wording, copy, style, layout, polish — without a plan. Creates .worktrees/explore_<slug>/, asks which source branch to cut from (recommends the active worktree/clone branch if one exists, else the workspace default), then applies each "change this" in that worktree, committing locally and not pushing until the user says so. Keeps the worktree until the PR/MR is merged. Use when the user says /ws-explore, "ws-explore", "explore session", "don't push yet", "keep the worktree", "we'll push later", or starts a session of small UI/wording/style tweaks they will keep adding to. Also use to resume an explore worktree, to push/open the PR when they are done, or to remove it after the MR merges. Not a one-shot ship-now fix (ws-direct), not non-trivial work (ws-plan), not product discussion (ws-intent; /ws-explore is this skill).
---

# ws-explore

A session of small tweaks the user will keep adding to — "change this, change this,
change this" — then push once, when they say they are done. Same isolation as
ws-direct (a worktree, never the clone in `repositories/`), **no** `plans/` file, **no**
push until asked, and the worktree **stays until the PR is merged**.

ws-direct is the one-shot: do it, open a PR, remove the worktree. This skill is the
sticky session. Its purpose is **pairing, fast**: small steps, the user checks each one
on a preview. So it **writes** e2e for changes but **does not run** it (§ 5).

## 0. Decide the path — before any worktree or edit

`/ws-explore` (or "ws-explore") is **always this skill**, even if the first ask looks
like a one-line ws-direct fix.

Otherwise pick one:

| Path | When |
|---|---|
| **This skill** | A session of small UI / wording / style / layout / polish they will keep adding to; or they said "don't push yet" / "keep the worktree" / "we'll push later" / "explore session" |
| **ws-direct** | One small, already-clear fix they want shipped now (PR this turn, worktree gone) |
| **ws-plan** | Non-trivial: unknown files, a new or changed cross-repo contract, a bug whose cause isn't obvious |
| **ws-intent** | Big, or they want to discuss *what* to build. The word "explore" in "explore a feature" is that skill |

If mid-session the change grows (new contract, many files, a product fork) → **stop**,
say so, offer ws-plan. Don't keep going and don't write a `plan.md` on the side.

Tell the user the path in **one line** ("Explore: sticky FE worktree for copy/style,
no push until you say.") and continue.

## 1. Resume or start

`ls -d .worktrees/explore_*/` and `./scripts/ws doctor`.

| Situation | Do |
|---|---|
| This session already has an explore worktree | Reuse it. Don't re-ask the source branch. |
| One existing `explore_<slug>` and the new ask belongs there | Reuse it. State the path, branch, and any open PR in one line. |
| Several `explore_*` folders | Ask which (structured-question tool), recommended = the one whose files match this ask, else the most recently modified. |
| An existing explore's PR is **merged** | Clean it up first (§ 7), then start a new one if they still have a change. |
| None, or they asked for a new session | § 2–4, then the first change. |

Dirty + another session writing there in the last ~10 min → ask who owns it first.

`/ws-explore` with no change yet: set up the worktree (§ 2–4) and wait for the first
tweak. Don't invent work.

## 2. Which repos — only what this session needs

From the first ask (or "frontend" if they only said `/ws-explore` and the work is
UI/copy/style), list the repos. Create a worktree for **those only**. A wording or
style change is almost always FE only.

Unsure whether a second repo is involved → ask once; don't create a spare worktree.

`./scripts/ws doctor`; `./scripts/ws sync` if a **needed** repo is missing or stale.

## 3. Confirm the source branch — always, before a *new* worktree

Same idea as ws-direct § 2 / ws-plan § 0a: the branch you cut from is the PR's base.
**Ask every time** you create a worktree, unless the user already named it or this is
a resume (§ 1).

For each needed repo, gather:

1. **Default** from `workspace.yaml` (`branch:`), as `origin/<branch>@<short sha>`
   (`git -C repositories/<repo> fetch origin <branch>` then `rev-parse --short`).
2. **Active** — the non-default branch this repo is actually on right now, if any:
   - clone `git -C repositories/<repo> branch --show-current` (if it isn't the default);
   - otherwise the most recently modified live worktree for that repo
     (`git -C repositories/<repo> worktree list`, skip the clone itself, skip merged
     explore folders). Name it (`feat/…` from `.worktrees/<folder>/`).
3. Other recent `origin/feat/…` / `origin/fix/…`
   (`git -C repositories/<repo> branch -r --sort=-committerdate | head -5`).

**Recommend one, with a reason:**

- An **active** branch that this tweak belongs on top of (same screen, unmerged
  feature, the worktree they are already looking at) → recommend **active**.
- Otherwise → recommend **default**.

Ask with the structured-question tool (`AskUserQuestion` in Claude Code, `AskQuestion`
in Cursor): **one question**, plain words, recommended option first marked
`(Recommended)`. Typical options: active (if one exists), default, then at most two
other recent branches. If every needed repo has the same recommendation, one question
covering all of them; if they differ, one question per repo, one at a time. Skip only
when the user already named the branch — then state it back in one line.

Never `git checkout` the clone in `repositories/`. A non-default source: fetch it, then
cut the worktree from `origin/<that branch>` (or the local `feat/…` if stacking on
unpushed work).

## 4. Worktrees — never the user's checkout

Slug: 2–4 snake_case words from the session (`rsvp_button_copy`). Folder
`.worktrees/explore_<slug>/` must not already be in use; if it is, this is a resume
(§ 1), not a second folder. A genuinely new session whose slug collides → append `-2`.

New branch name (don't ask — tell them): `fix/<kebab-slug>` for a bug/typo,
`feat/<kebab-slug>` for a small addition, `chore/<kebab-slug>` otherwise. Not
`feat/NNN-slug` — there is no plan number. Not `explore/` as a prefix (PRs look like
ordinary fix/feat/chore).

Per **needed** repo only (`<branch>` = the source they picked):

```bash
W=<workspace>/.worktrees/explore_<slug>   # ABSOLUTE path (git -C resolves a relative one inside the repo clone)
git -C repositories/<repo> fetch origin <branch>
git -C repositories/<repo> worktree add -b <new-branch> "$W/<repo>" origin/<branch>
```

If stacking on a local unmerged branch, cut from that branch instead of `origin/<branch>`.
Worktrees live only under the workspace's `.worktrees/` — never inside a clone, never as
siblings of the workspace. `./scripts/ws doctor` lists them.

Copy gitignored local config from `repositories/<repo>/` (`cp`, never symlink, never
`git add`) as `WORKFLOW.md` § 4. Start that repo's install in the background the same
way. Skip repos you are not touching.

Write a tiny session marker (gitignored with the worktree) so a later session can resume:

```bash
cat > "$W/.ws-explore" <<EOF
slug=<slug>
started=<YYYY-MM-DD>
source_<repo>=<source-branch>
branch_<repo>=<new-branch>
pr_<repo>=
EOF
```

Update `pr_<repo>=<url>` when a PR exists.

## 5. Each change — the loop. Do not push.

Read the needed repo's `AGENTS.md` **before writing** (workspace rule). Load its skill
list without dumping bodies:

```bash
.agents/skills/ws-implement/repo-context.sh "$W/<repo>"
```

Open only the skills whose description matches this edit. UI / product-facing copy:
read the docs `WORKFLOW.md` § 3 names first.

- **One repo:** the main session implements in `$W/<repo>`. Don't spawn a subagent for a
  20-line tweak.
- **Two or more repos:** unusual for this skill (that's often a plan). If it still fits,
  one subagent per repo, same as ws-direct § 4 / [`ws-direct/subagent-prompt.md`](../ws-direct/subagent-prompt.md).

Stay inside the files the ask needs. Match surrounding code. Don't drive-by refactor.

Commit locally as you go: **one logical change per commit**, typically one commit per
user ask. Format: `<type>(<scope>): <summary>` — no `[NNN-Tn]`. Don't commit copied
local config. Attribution lines from the system reminder, as in ws-direct.

Fast checks for the files you touched: `WORKFLOW.md` § 5 (tsc + eslint). Then rebuild
or reload the preview if the user is looking at one, so they can check it themselves.

**Do not run e2e in this mode.** Explore is pairing: the user looks at the result and
says what is next, so speed beats a green suite. Never run Playwright specs (or
screenshot scripts) after a change unless the user asks for it.

**Still write the e2e.** A changed behaviour, a new interaction or a new scenario gets
its spec written or updated in the same commit as the change (the existing spec for
that screen, or a new file next to it), covering every scenario the change adds —
empty, error, phone/desktop, Indonesian where the screen has it. Check it only with
tsc + eslint, and say in the commit message and your report that it was written, not
run. Copy-only edits that no spec asserts need no spec change; grep `tests/` for the
old text and fix any spec that asserts it.

**Need a run anyway?** Only when something is genuinely unclear without one (a
failure you can't explain by reading, a flow you can't judge from the code). Ask first
— structured question, one line on why — and run only the named spec, main session,
Chromium, one dev server per `WORKFLOW.md` § 6. Never run the whole suite here. The
full run belongs to the user's check or to the CI after push.

Then **stop**. Do **not** push. Do **not** open a PR. Do **not** remove the worktree.

Tell the user, briefly: what changed, the worktree path, the branch, that it is local
only. Wait for the next "change this", or for them to say push / done / open PR.

A later ask in this conversation, or a new `/ws-explore` that belongs here → same
worktree, § 5 again. Don't re-ask the source branch.

## 6. Push and open a PR — only when they ask

Triggers: "push", "open PR", "open MR", "buka PR", "done", "udahan", "ship", "we're
good", "push later" now meaning now. Not implied by "looks good" on a single tweak.

Then **push and open a PR per touched repo**, main session only:

```bash
git -C "$W/<repo>" push -u origin <new-branch>
gh pr create --repo <owner/name from `git remote get-url origin`> \
  --base <source branch> --head <new-branch> \
  --title "<type>(<scope>): <summary>" --body-file <scratch>/pr-<repo>.md
```

Body: what changed (2–4 bullets), checks → result, sibling PRs if any. Draft if checks
failed. `WORKFLOW.md` § 7 for `gh pr edit` in these repos. A PR already exists for the
head branch (`gh pr view <new-branch> --json url`) → push and update it, don't open a
second one. Write the URL into `$W/.ws-explore`.

**Keep the worktree.** Do not `worktree remove`. Further tweaks (review comments, one
more wording change) stay on this branch; push again when they ask.

Then **ask** — structured-question tool, one question, after the PRs exist:

- Prompt: merge this PR now, or leave it open?
- Options: **Leave it open** `(Recommended)` — they can review first; **Merge now** —
  merge into the source branch (see `WORKFLOW.md` § 7 for what a merge triggers).
- Draft or failing checks → say so and still default to leaving it open.

**Leave it open** → stop. Worktree stays.

**Merge now** → merge each PR (`gh pr merge <n> --repo <owner/name> --squash`), in
the deploy order of `WORKFLOW.md` § 7 (e.g. BE before FE), then go to § 7 below. Failures or a still-draft PR → don't force-merge.

Tell the user: the **PR link** first, then per repo the source branch, the new branch,
checks → result, and that the worktree is **kept until the PR merges**.

## 7. After the PR merges — then remove the worktree

When the user says it merged, or `gh pr view <new-branch> --json state` is `MERGED`,
or they ask to clean up a finished explore:

Working tree must be clean and fully pushed (`status --porcelain` empty, nothing in
`@{u}..HEAD`); commit leftovers first. Then
`git -C repositories/<repo> worktree remove "$W/<repo>"` and `rmdir "$W"` if empty
(including `$W/.ws-explore`). Keep the branch — the merged PR still has it. Dirty and
you can't commit it → keep that worktree and say so; never `--force` away uncommitted
work.

Abandoned (they say drop it, no PR or PR closed): same removal once clean; don't
delete the remote branch unasked.

## 8. Report

After setup: worktree path, source branch, new branch, "local only until you say push".
After each tweak: what changed + still local (or pushed, if they asked). Name any e2e
spec you wrote or updated and say it was **not run**.
After push: PR link + worktree kept.
After merge: worktree gone.
