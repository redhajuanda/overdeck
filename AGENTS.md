# AGENTS.md

> **New workspace?** If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists, this workspace has not been set
> up yet: follow it before anything else.

This is the **__PROJECT__** project workspace. It is a thin coordination layer over the
independent app repositories. It holds planning and cross-repo decisions; it holds **no**
code and **no** copied knowledge.

## Bootstrap — do this before anything else

If a declared repo is missing, run `./scripts/ws sync` **before answering anything
else**, then continue. `./scripts/ws doctor` says what is missing or stale.

The repos are gitignored clones under `repositories/`, **never submodules**: nothing is
pinned, so `ws sync` always leaves you on the real branch tip. Never commit a sub-repo's
files here.

Repos are declared only in [`workspace.yaml`](workspace.yaml).

## Repositories

| Dir | Role | Stack | Own docs |
|-----|------|-------|----------|
| `repositories/__PROJECT__-fe/` | Frontend — <surfaces> | <stack> (`github.com:__OWNER__/__PROJECT__-fe`) | `repositories/__PROJECT__-fe/AGENTS.md` when present |
| `repositories/__PROJECT__-be/` | Backend — <responsibilities> | <stack> (`github.com:__OWNER__/__PROJECT__-be`) | `repositories/__PROJECT__-be/AGENTS.md` when present |

Each repo's own `AGENTS.md` and skills load **on demand, when a file in that directory is
read** — and only via a real file read. Before working in a repo, read its `AGENTS.md` first.

## Working rules

- Frontend task → work inside `repositories/__PROJECT__-fe/`, follow that repo's `AGENTS.md`.
- Backend task → work inside `repositories/__PROJECT__-be/`, follow that repo's `AGENTS.md`.
- Use the skills scoped to the repo you are in, not the other's.
- **Plan from this root; implement from inside the repo.** A change spanning several repos wants
  one session here. Single-repo work is cheaper started from that repo's directory.
- **Dev servers / browsers:** follow `WORKFLOW.md` § 6 — one dev server per machine, stop it when done.

## Design context

Workspace-level product and design live here, not in the repos. Read them before
UI or product-facing copy work:

- [`PRODUCT.md`](PRODUCT.md) — users, surfaces, principles, anti-references
- [`DESIGN.md`](DESIGN.md) — product UI

## Architecture notes — `context/architecture/`

Cross-repo explanations of how a feature works end to end (FE + BE + infra), each stamped with
the commits it was checked against. Read the matching note before planning or changing that
area, and re-check the code for details. Index: [`context/architecture/README.md`](context/architecture/README.md).

## Intents — `intents/`

Optional step before planning, for big features or when it isn't yet clear what we want.
An intent (`intents/007_rsvp_reminders.md`, own numbering) is a short, human-readable agreement
on the problem, outcome, scope, non-goals and chosen direction — no code, no tasks. Discuss and
write it with the `ws-intent` skill (`.agents/skills/ws-intent/`): it acts as a critical senior
product manager and probes the code read-only when an idea needs checking. One intent can
become several plans; ws-plan treats an agreed intent's scope and non-goals as fixed.
Ideas we plan to do later but whose requirements are not clear yet are parked in `intents/backlog/bNNN_<slug>.md`
(own `b001…` numbering by creation order) with the same skill, then picked up as an intent or cancelled.

## Planning — `plans/`

One numbered directory per change (`plans/001_our_story/plan.md`). Cross-repo plans live here
because they belong to neither repo. Write plans with the `ws-plan` skill (`.agents/skills/ws-plan/`):
it reads the affected code first (one read-only subagent per repo), then fills the plan template.
Implement a plan with the `ws-implement` skill (`.agents/skills/ws-implement/`): one
subagent per repo in a worktree, briefed with that repo's AGENTS.md + skill descriptions.
Finished or abandoned plans move to `plans/archived/` with the `ws-archive` skill (`.agents/skills/ws-archive/`).
Several plans at once → `ws-multi-implement` (`.agents/skills/ws-multi-implement/`): one
orchestrator orders them, stacks branches on shared files and runs one shared agent pool.
A small, already-clear change (known files, no new cross-repo contract) skips
the plan: ship it now with the `ws-direct` skill (`.agents/skills/ws-direct/`) — a worktree
under `.worktrees/direct_<slug>/` for only the repos the task needs, after asking which
source branch to cut from; it opens a PR and removes the worktree. The user saying
"edit directly" also takes this path. A session of small UI / wording / style tweaks they
will keep adding to, then push later, uses `ws-explore` (`.agents/skills/ws-explore/`,
`/ws-explore`) — a worktree under `.worktrees/explore_<slug>/` that stays until the PR
merges. Bigger or unclear work still goes through intent and/or plan.
Subagent models are set in [`agents.yaml`](agents.yaml) — change models there, not in skills.
Project-specific workflow facts the skills read (stack commands, worktree setup, dev server,
release-only actions) live in [`WORKFLOW.md`](WORKFLOW.md).
