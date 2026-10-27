```text
 ██████╗ ██╗   ██╗███████╗██████╗ ██████╗ ███████╗ ██████╗██╗  ██╗
██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║ ██╔╝
██║   ██║██║   ██║█████╗  ██████╔╝██║  ██║█████╗  ██║     █████╔╝
██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██║  ██║██╔══╝  ██║     ██╔═██╗
╚██████╔╝ ╚████╔╝ ███████╗██║  ██║██████╔╝███████╗╚██████╗██║  ██╗
 ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝

═══════════════ plans · skills · context · lessons ═══════════════
       ║               ║               ║               ║
   ┌───╨────┐      ┌───╨────┐      ┌───╨────┐      ┌───╨────┐
   │   fe   │      │   be   │      │ mobile │      │  ...   │
   └────────┘      └────────┘      └────────┘      └────────┘
```

**A self-learning agent workspace for multi-repo projects.**

overdeck is a template for a workspace that sits *above* several independent app repos
(frontend, backend, …) and coordinates them: product docs, cross-repo plans, and a set of
agent skills that take work from idea to merged PRs. Works with Claude Code, Codex and Cursor
(`AGENTS.md` + `.agents/skills/`).

**It gets better every time you use it.** When an agent is corrected, hits a wrong command or
takes a detour, it writes the lesson where the next session will read it: a project fact in
`WORKFLOW.md`, a rule in the skill's overlay, a domain rule in `context/`. Subagents get the
rules that concern them in their brief. After every implementation, a retro measures the run
(time, tokens, rework) and proposes small fixes. A lesson that comes back after it was applied
is treated as a failed rule and rewritten, not just counted. Lessons every project would want
go back to this template as a PR, and `ws upgrade` brings them to every workspace without
touching what the project learned itself. → [Self-learning](#self-learning-and-upgrading)

```
overdeck/
├── AGENTS.md            rules every agent reads first
├── WORKFLOW.md          project facts the skills read (commands, dev server, release)
├── workspace.yaml       the repos — ours (repos:) and read-only references (knowledge:),
│                        and how they relate (calls, depends-on, …)
├── agents.yaml          subagent models per role (agents.local.yaml: your own, gitignored)
├── members.yaml         who works here: code, ID prefix, git emails, language, tone
├── PRODUCT.md, DESIGN.md what we want: users, principles, UI
├── scripts/ws           sync | doctor | status | foreach | upgrade | relations | template
├── .overdeck/           upstream.yaml: which files the template owns + the template commit
├── repositories/        app repos, cloned by `ws sync` (gitignored, never submodules);
│                        knowledges/<name> holds the read-only knowledge repos
├── intents/<member>/  plans/<member>/
├── context/            how it works today: glossary, actors, domain, architecture,
│                        integrations, decisions (ADRs)
├── sources/             material we were given (PRDs, MOMs, specs), kept as received
├── .agents/skills/      ws-intent → ws-plan → ws-implement → ws-archive,
│                        ws-direct, ws-explore, ws-multi-implement, ws-learn
├── .agents/overlays/    what this project taught the ws-* skills
└── plans/ws-learnings.md the learning ledger: every lesson, its source and status
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
| Done | `ws-archive` — archive the plan, sync `context/` with what shipped, offer an ADR |

## Self-learning and upgrading

A project workspace learns as it is used, and still takes template upgrades cleanly, because
every file has one owner:

| Owned by the template — `ws upgrade` overwrites | Owned by the project — learning writes here |
|---|---|
| `.agents/skills/`, `scripts/ws` | `WORKFLOW.md`, `PRODUCT.md`, `DESIGN.md`, `workspace.yaml`, `agents.yaml`, `members.yaml` |
| the `<!-- overdeck:begin/end -->` blocks in `AGENTS.md` | the rest of `AGENTS.md` |
| | `.agents/overlays/<skill>.md`, `plans/`, `intents/`, `context/`, `sources/` |

The list lives in [`.overdeck/upstream.yaml`](.overdeck/upstream.yaml).

- **Learning** — the `ws-learn` skill. A correction or a wrong command/doc is recorded the
  moment it happens, and every `ws-*` skill ends with a sweep for what slipped through;
  "remember this" calls it directly. It writes project facts to `WORKFLOW.md` and
  project-specific skill rules to an overlay that the skill reads first, and subagent briefs
  carry the rules that concern them. It never edits a skill in a project.
- **Closing the loop** — a lesson that recurs after it was applied is marked `recurred`: the
  rule failed and gets moved or sharpened, not counted. `./scripts/ws doctor` flags recurred
  lessons, a ledger or overlay that needs consolidating, and rules naming paths that no
  longer exist. The ledger union-merges (`.gitattributes`), so members never conflict on it.
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
