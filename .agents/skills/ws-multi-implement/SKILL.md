---
name: ws-multi-implement
description: Implement several plans from plans/<member>/NNN_slug/plan.md in one run in this multi-repo workspace (repos declared in `workspace.yaml`) — orders them by their dependencies and shared files, asks every blocking open question up front (one by one), then drives one shared pool of per-(plan, repo) implementer subagents through ws-implement's worktree / brief / contract-check / review / fix steps, stacking branches where plans touch the same files. The main session acts as the user: it schedules, unblocks and reviews, and asks the user only for product decisions. Use when the user asks to implement, build, ship or "kerjakan" more than one plan ("implement 042–045", "kerjakan semua plan", "do the remaining plans"), or to resume such a run.
---

# ws-multi-implement

> **Project overlay.** If `.agents/overlays/ws-multi-implement.md` exists, read it before anything else: its
> rules are this project's additions to this skill and win where they conflict. Pass the ones
> that concern a subagent into its brief. Never edit this skill in a project — lessons go
> through [`ws-learn`](../ws-learn/SKILL.md).

This skill runs [`ws-implement`](../ws-implement/SKILL.md) for several plans at once, **from a
single orchestrator**. Read ws-implement first. Every step it defines (worktrees, briefs, model
choice, contract check, review tiers, one fix round, finish) applies unchanged per plan. This
file adds only what changes when there are several plans: **ordering, branch stacking, a
shared agent pool, and acting for the user**.

Why flat: subagents can't start subagents or ask the user anything. So there is **no
per-plan lead agent**. The main session is the lead for every plan, and the implementers are
the only layer under it. A per-plan lead would only add an extra warm-up for work that is
just routing.

## 0. Select and preflight

1. Plans: the ones the user named. If they didn't name any, take every plan whose `Status:` is
   `proposed` or `in progress` and whose tasks aren't all ticked. Show the list and continue,
   without asking.
2. `./scripts/ws doctor`; run `./scripts/ws sync` if anything is missing or stale. Do this
   once for the whole run.
3. Per plan, run ws-implement § 0 (read fully, drift check, task selection, release tasks out).
   A plan that fails the drift check is re-verified (ws-plan § *Revising*) before it enters
   the schedule. Other plans don't wait for it.
4. Ledger: create `plans/.ws-multi-implement.md` from § 7, or read it when resuming. Also
   write the `Run:` start line in each plan's header (ws-implement § 0.5).

## 1. Build the schedule

The unit is a **batch = (plan, repo)**: one implementer doing that plan's tasks in that repo,
exactly like a ws-implement batch. Edges between batches come from three sources:

| Source | Edge |
|---|---|
| Header `depends on: NNN` / `blocks: NNN`, task `needs: NNN Tk` | The dependent batch waits until the batch holding the needed task passes § 5. If the dependency names a task, wait only for that task's batch, not for the whole plan. Example: plan A blocks only the *backfill steps* of plans B and C. |
| Same plan, other repo | ws-implement § 2 rules. Usually no edge, because the batches code against plan § *Contracts*. |
| **Shared files**: two plans' tasks name the same file in the same repo (`Files:` lines, plus *Contracts* touching the same schema/DTO) | **Stack edge — on the shared tasks only.** The later plan's tasks that name the shared files wait until the earlier batch passes § 5. Its earlier independent tasks start now (§ 2). If the shared tasks come first, the whole batch waits. |

For a stack edge with no declared dependency, the order is: the plan that others depend on
goes first, then plans with fewer tasks in that repo, then the lower number.

**Migrations:** before dispatch, give each new migration in the run its own timestamp, set after the
newest one on any branch (`git log --all`, not only the clone). Put the timestamps in the briefs, so that
parallel batches can't pick the same one.

A cycle, or two plans that change the same *Contract* in incompatible ways, is a plan defect.
Ask the user (§ 3) before any dispatch.

Tell the user the schedule in ≤ 6 lines, then proceed without waiting for approval:
```
now:   A·<repo-a> ∥ A·<repo-b> ∥ B·<repo-c>
then:  B·<repo-a> (stacked on A·<repo-a>: shared-file.ext) · B·<repo-b> (stacked on A·<repo-b>: schema copy)
then:  C·*, D·* (needs B T2) …
```

## 2. Branches — stacking

- Independent batch: `feat/NNN-slug` off `origin/<branch>` in `<workspace>/.worktrees/NNN_slug/<repo>`,
  as in ws-implement § 1 (incl. copying gitignored config from `repositories/<repo>/`).
- Stacked batch: create its worktree **when the predecessor passes § 5**, off the predecessor's
  branch:
  `git -C repositories/<repo> worktree add -b feat/NNN-slug "$W/<repo>" feat/PPP-slug`.
  Its **base ref** for diffs, review and the brief's `Base:` is `feat/PPP-slug`, not
  `origin/<branch>`. That way each plan's review sees only its own change.
- Stacked batch with independent tasks before the shared ones: create its worktree now off
  `origin/<branch>` and dispatch those tasks only ("stop before Tk; keep your context"). When
  the predecessor passes § 5, `git -C "$W_succ/<repo>" rebase feat/PPP-slug`
  (conflict → abort and send it to the implementer), then `SendMessage` the same agent the
  shared tasks. From then on its base ref is `feat/PPP-slug`, as above.
- If the predecessor later gets fix-round commits (§ 4), rebase the successor once, after
  the predecessor's fix round: `git -C "$W_succ/<repo>" rebase feat/PPP-slug`. If it's clean,
  re-run the successor's Verify. If there's a conflict, `git rebase --abort` and send it to
  the successor's implementer with `SendMessage` ("rebase onto feat/PPP-slug, keep both
  intents").
- Start installs in the background as each worktree is created. Never let two agents share a
  worktree.

## 3. Act as the user — decide vs. ask

The user wants this run to replace them, so the orchestrator answers what the plans already
decide, and **asks the user only for real choices**.

**Up front, before the first dispatch:** gather every *blocking* open question from all the
selected plans, then ask them **one by one** as in ws-implement § 0 *Asking the user* (plain
words, clear context, recommended option first), naming the plan's feature — not just its
number — in each. Write each answer into that plan's *Decisions* as
`- <date> · user: <answer>`, and strike the question. Non-blocking questions don't stop the
run.

**During the run**, when an implementer reports `blocked` or asks something:

| The orchestrator decides itself (records it under the plan's *Decisions* as `· orchestrator:`) | The orchestrator asks the user |
|---|---|
| The plan, its *Contracts*, *Decisions*, the project's product/design docs (`WORKFLOW.md` § 3) or the repo's AGENTS.md already answers it | Product, UX or copy choices the plan leaves open |
| Implementation detail inside a task's stated files and intent | Scope change: a task added or dropped, or a feature cut |
| Test or tooling trouble (flaky test, missing dep, install race) | A change to a *Contract* that another plan also uses |
| Naming, file placement, refactor size within the task | Anything release-only (`WORKFLOW.md` § 7), deleting, or pushing outside § 6's PR step |

While the user hasn't answered, keep every other batch running. Only the asking batch waits.
Questions that arrive close together are queued and still asked one at a time.

## 4. Run the pool

Cap: `roles.multi-implement.max_parallel` from `agents.yaml`. It covers implementers **and**
reviewers of all plans together. Models still come from `roles.repo-implement` /
`roles.change-review` (ws-implement § 3).

Loop, driven by agent notifications. Never poll:

1. **Dispatch** every ready batch, up to the cap, in one message. A batch is ready when its
   edges are satisfied, its worktree exists and its install is done. Prefer batches on the
   **critical path**, meaning the ones that unblock the most other batches. Brief each one
   with ws-implement § 4, plus one line per stack: "Built on feat/PPP-slug, which already
   contains plan PPP's <tasks>. Don't change its work beyond what your tasks need."
2. **On each report:** run the ws-implement § 5 contract check for that batch. Then:
   - `git fetch origin <branch>`; if it moved since the batch's base, rebase the batch onto it now
     (conflict → `git rebase --abort` and send it to its implementer), before review and before
     cutting stacked successors from it. Peer sessions merge mid-run.
   - Tick its tasks provisionally (ws-implement § 6) and update the ledger.
   - Create the worktrees of any stacked successors, and mark newly ready batches.
   - If this was the plan's last batch, the plan enters **review**: ws-implement § 7 sizing,
     i.e. **one** whole-change reviewer per plan, briefed with every touched repo's context
     (it takes one pool slot), then § 8's single fix round. After the fix round, rebase
     stacked successors (§ 2). **No e2e per plan** — see *E2E once per run* below.
3. Plans move through review independently. Don't hold finished plans for the rest of the
   run.

### E2E once per run

A multi-plan run starts **one** dev server and runs e2e **once**, not once per plan:
- When every plan of a stack has passed its fix round, run the union of those plans' new and
  named specs (scoped per `WORKFLOW.md` § 5) on the **top branch of the stack** — it contains
  all of them. Independent plans or stacks share the same server, one after another.
- A failure goes to the implementer of the plan whose spec or screen it is; after the fix,
  re-run **only the failed specs** (`--last-failed`), not the whole selection.
- A failure that also happens on the source branch (check with one baseline run of that spec)
  is pre-existing: note it, don't fix it.
- Runs before the last fix round are wasted: fixes and restacks change the code they tested.

When a slot frees up and nothing is ready, wait for the next notification. Don't start work
early and don't read code to fill the time.

## 5. Context discipline — this session holds many plans

- Keep per-plan state in the ledger, not in memory: batches, agent ids, worktrees, bases,
  ticks, open findings. Update it at every state change. After a context compaction,
  re-read the ledger instead of the plans.
- Read implementer reports and review findings. Never read file dumps or full diffs. Only
  the boundary lines the § 5 contract check needs, plus the cited lines when verifying a
  finding (ws-implement § 8).
- For more than ~5 plans, or more than ~15 batches, run a first group to completion, then
  the next group. Tell the user the split.

## 6. Finish

Per plan, when its fix round is done: ws-implement § 9 checks, minus e2e (run once per run, § 4). Run them in the background,
in parallel, at most one check command per repo worktree at a time. Then ws-implement § 9's
commit → push → PR steps for each of its batches: an independent batch's PR targets
the plan's source branch (`Based on:` header), a stacked batch's PR targets its predecessor's
`feat/PPP-slug` (open the predecessor's PR first). Then set `Status:` →
`implemented` and mark it `done` in the ledger. Close the plans' `Run:` lines **only at
the very end, for all plans at once**, so every plan's metrics cover the whole shared run.

When every plan is done, give the user **one** summary:
- A table: plan · repo · **PR link** · branch → PR base · worktree · checks → result ·
  tasks left.
- **Merge order**: the stack order from § 1. Each stacked PR targets its predecessor's branch,
  or is merged after it.
- **Release steps for all plans merged into one ordered list**: producer before
  consumer as each *Rollout* says, with duplicates such as "deploy <repo>" collapsed.
- Decisions the orchestrator made on the user's behalf (§ 3), so they can overrule any.
- Review findings that were fixed, minor ones left, and anything unverified.

**Retro, once for the whole run — the last step, before you stop.** Do a single
[`retro.md`](../ws-implement/retro.md) in the first plan's folder covering all plans (metrics
with that plan's `--plan`), and add a *Multi* axis: idle pool slots, stack rebases and
conflicts, questions asked vs. decided. Every other plan's folder gets a one-line `retro.md`
pointing to it. Learnings go to `plans/ws-learnings.md`, tagged `multi`.

Push and open PRs only in § 6, after each plan's review and fix round. Never merge, deploy
or remove worktrees unless the user asks.

## 7. Ledger — `plans/.ws-multi-implement.md`

```markdown
# ws-multi-implement run — started <ISO>
Plans: NNN, NNN, NNN · cap 3

| Batch | State | Agent id | Worktree | Branch ← base | Tasks | Notes |
|---|---|---|---|---|---|---|
| NNN·<repo-a> | review | a1b2… | .worktrees/NNN_slug/<repo-a> | feat/NNN-slug ← origin/<branch> | T3–T5 | |
| QQQ·<repo-a> | waiting NNN·<repo-a> (stack) | — | — | feat/QQQ-slug ← feat/NNN-slug | T4–T6 | |

## Asked / decided
- NNN · user: <answer to a product question>
- QQQ · orchestrator: <decision the plan already settles> (plan Decisions D3)
```

States: `waiting <edge>` → `ready` → `running` → `passed §5` → `review` → `fixing` →
`done`, or `blocked <why>`.
