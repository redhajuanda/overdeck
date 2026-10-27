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
├── members.yaml         who works here: code, ID prefix, git emails, language, tone
├── PRODUCT.md, DESIGN.md
├── scripts/ws           sync | doctor | status | foreach | upgrade
├── .overdeck/           upstream.yaml: which files the template owns + the template commit
├── repositories/        app repos, cloned by `ws sync` (gitignored, never submodules)
├── intents/<member>/  plans/<member>/  context/architecture/
├── .agents/skills/      ws-intent → ws-plan → ws-implement → ws-archive,
│                        ws-direct, ws-explore, ws-multi-implement, ws-learn
└── .agents/overlays/    this project's additions to the ws-* skills
```

## Start a new project

Tell your agent:

> Create a new workspace for project **X** from the `redhajuanda/overdeck` template and follow its BOOTSTRAP.md.

Or by hand:

```bash
gh repo create <owner>/x-workspace --private --template redhajuanda/overdeck --clone
cd x-workspace   # then open an agent here: it sees BOOTSTRAP.md and sets things up
```

## Members

Everyone who works here is in [`members.yaml`](members.yaml): a folder `code` (`redha.juanda`),
an ID `prefix` (`rj`), the git emails that identify them, and the `language` and `tone` the
agent talks to them in. Files are written in one shared `docs_language`. Each member's intents
and plans live in their own folder and carry their prefix (`rj-042`), so two members, or two
branches, never take the same number, with no server to coordinate. `./scripts/ws whoami`,
`ws next plan`, `ws find plan 042`.

## The flow

| Size of the work | Skill |
|---|---|
| Big or unclear — what do we even want? | `ws-intent` → `intents/<member>/rj-007_slug.md` |
| Non-trivial, clear | `ws-plan` → `plans/<member>/rj-042_slug/plan.md`, then `ws-implement` (one subagent per repo, in worktrees, PR per repo) |
| Several plans | `ws-multi-implement` |
| Small and clear | `ws-direct` — worktree, commit, PR |
| A session of UI/copy tweaks, push later | `ws-explore` |
| Done | `ws-archive` — archive the plan, update architecture notes + PRODUCT.md |

## Learning and upgrading

A project workspace learns as it is used, and still takes template upgrades cleanly, because
every file has one owner:

| Owned by the template — `ws upgrade` overwrites | Owned by the project — learning writes here |
|---|---|
| `.agents/skills/`, `scripts/ws` | `WORKFLOW.md`, `PRODUCT.md`, `DESIGN.md`, `workspace.yaml`, `agents.yaml`, `members.yaml` |
| the `<!-- overdeck:begin/end -->` blocks in `AGENTS.md` | the rest of `AGENTS.md` |
| | `.agents/overlays/<skill>.md`, `plans/`, `intents/`, `context/` |

The list lives in [`.overdeck/upstream.yaml`](.overdeck/upstream.yaml).

- **Learning** — the `ws-learn` skill. Every `ws-*` skill ends by recording what went wrong
  or what the user corrected; "remember this" calls it directly. It writes project facts to
  `WORKFLOW.md` and project-specific skill rules to an overlay that the skill reads first.
  It never edits a skill in a project.
- **Upstream** — a lesson every project would want is tagged `upstream` in
  `plans/ws-learnings.md`; `ws-learn upstream` opens a PR here with it.
- **Upgrading** — in a project, `./scripts/ws upgrade --check`, then `./scripts/ws upgrade`.
  It applies only what the template changed since the project's `base:` commit, and only
  where the local copy is untouched. A template file edited in the project is a conflict:
  nothing is written until the edit moves to an overlay. `./scripts/ws doctor` warns early.

```
project lesson ──► WORKFLOW.md / overlay / AGENTS.md outside the blocks     stays local
general lesson ──► ws-learnings.md [upstream] ──► PR here ──► ws upgrade ──► every project
```
