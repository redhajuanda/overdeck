# WORKFLOW.md — project profile for the `ws-*` skills

The workflow skills (`.agents/skills/ws-intent`, `ws-plan`, `ws-direct`, `ws-explore`,
`ws-implement`, `ws-multi-implement`, `ws-archive`) are general: they work for any
workspace of N repositories and hold no project facts. Everything specific to **this**
workspace (__PROJECT__) lives here. Skills cite sections of this file as `WORKFLOW.md § N`.
`<workspace>` is the directory holding `workspace.yaml`.

Keep the section numbers: the skills refer to them. Write `none` rather than deleting a section.

## 1. Repos & source branches

Declared in [`workspace.yaml`](workspace.yaml); roles and stacks in the table in
[`AGENTS.md`](AGENTS.md). Do not repeat them here. Default source branches come from the
`branch:` field there.

- <repo>: read the repo's own `AGENTS.md` first.
- Repo skills that usually match: <e.g. UI work in __PROJECT__-fe → `frontend-conventions`>.

## 2. Typical data path

```
BE: route → handler → service → repository → migration/table   (__PROJECT__-be)
FE: API client → feature module → page/UI                          (__PROJECT__-fe)
```

Trace a feature along this path, not file by file.

## 3. Product vocabulary & docs

- Terms: **<term>** (<meaning>). The same words are used in plans.
- Read before UI or product-facing copy work: [`PRODUCT.md`](PRODUCT.md), [`DESIGN.md`](DESIGN.md).
- Plan self-check extras: <e.g. compatibility with data saved before the change>.

## 4. Worktree setup

A fresh worktree has only tracked files. Copy (`cp`, never symlink, never `git add`) from the
default clone `repositories/<repo>/`:

| Repo | Local config to copy |
|---|---|
| `__PROJECT__-fe` | `.env.local` |
| `__PROJECT__-be` | <local config files> |

Skip build output and caches: `node_modules`, `.next`, `__pycache__`, `build/`.

Install in the background right away:

| Repo | Install |
|---|---|
| `__PROJECT__-fe` | `pnpm install` |
| `__PROJECT__-be` | <e.g. `go mod download`> |

Use whatever the repo's `AGENTS.md` says if it differs.

## 5. Fast checks per repo

Scope every check to what the change touched; full suites are CI's job.

| Repo | Run | Never (unless asked) |
|---|---|---|
| `__PROJECT__-fe` | <typecheck>; <lint changed files>; <unit tests touched> | whole e2e suite |
| `__PROJECT__-be` | <vet/lint + tests on touched packages> | the full suite |

**Which e2e specs to run:** new or changed UI behaviour → the specs of the screens it changes;
backend only, copy, styling or a pure refactor → no e2e. A spec that fails is first run once on
the source branch: failing there too = pre-existing, note it and move on.

**Implementer's changed-files check** (once, after the last task): <commands>.
Implementers never run e2e; the main session runs new specs once against one dev server.

**Review diff excludes** (pathspecs appended to `git diff … -- .`):
`':!pnpm-lock.yaml' ':!go.sum' ':!**/*.gen.*' ':!**/__snapshots__/**'`

## 6. Dev server & visual QA

- Dev server: `__PROJECT__-fe`, port **<port>**, started in the background once installs finish.
- One dev server per machine. Check `free -g` before starting one; stop it by its port's PID
  (`ss -ltnp | grep ':<port> '`) when the QA step is done, never `pkill -f <pattern>`.
- Cap its memory so only it gets OOM-killed, not the terminal:
  `systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0 <dev command>`.
- Browser engine: <e.g. Playwright Chromium only>.

## 7. Release-only actions (never by a subagent)

Deploying, running a migration on a shared database, and pushing. They become next steps for
the user. Deploy order: <e.g. BE before FE>, as each plan's *Rollout* says.
What a merge triggers: <e.g. merging into `main` auto-deploys to dev>.

## 8. OpenSpec hand-off

<none, or: a change confined to one repo that fits its OpenSpec flow belongs in that repo's
`openspec/` instead of a plan here.>

## 9. Lessons from past runs

<ws-implement retros add one line per lesson here. Start empty.>
