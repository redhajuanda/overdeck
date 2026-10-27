# overdeck

A template for an **agent workspace** that sits *above* several independent app repos
(frontend, backend, …) and coordinates them: product docs, cross-repo plans, and a set of
agent skills that take work from idea to merged PRs. Works with Claude Code, Codex and Cursor
(`AGENTS.md` + `.agents/skills/`).

```
overdeck/
├── AGENTS.md            rules every agent reads first
├── WORKFLOW.md          project facts the skills read (commands, dev server, release)
├── workspace.yaml       the repos — the only place they're declared
├── agents.yaml          subagent models per role
├── PRODUCT.md, DESIGN.md
├── scripts/ws           sync | doctor | status | foreach
├── repositories/        app repos, cloned by `ws sync` (gitignored, never submodules)
├── intents/  plans/  context/architecture/
└── .agents/skills/      ws-intent → ws-plan → ws-implement → ws-archive,
                         ws-direct, ws-explore, ws-multi-implement
```

## Start a new project

Tell your agent:

> Create a new workspace for project **X** from the `redhajuanda/overdeck` template and follow its BOOTSTRAP.md.

Or by hand:

```bash
gh repo create <owner>/x-workspace --private --template redhajuanda/overdeck --clone
cd x-workspace   # then open an agent here: it sees BOOTSTRAP.md and sets things up
```

## The flow

| Size of the work | Skill |
|---|---|
| Big or unclear — what do we even want? | `ws-intent` → `intents/NNN_slug.md` |
| Non-trivial, clear | `ws-plan` → `plans/NNN_slug/plan.md`, then `ws-implement` (one subagent per repo, in worktrees, PR per repo) |
| Several plans | `ws-multi-implement` |
| Small and clear | `ws-direct` — worktree, commit, PR |
| A session of UI/copy tweaks, push later | `ws-explore` |
| Done | `ws-archive` — archive the plan, update architecture notes + PRODUCT.md |

## Updating the template

A repo made from a template is a copy, not a fork. Improve a `ws-*` skill in a project, then
copy it back here so the next project starts with it.
