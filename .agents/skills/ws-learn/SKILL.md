---
name: ws-learn
description: Record what this multi-repo workspace (repos declared in `workspace.yaml`) learned so the next session does better — routes each lesson to the right project-owned file (WORKFLOW.md, a skill overlay in .agents/overlays/, a context/ note (glossary, actors, domain, architecture, integrations, decisions), PRODUCT.md / DESIGN.md, AGENTS.md outside the template blocks), never into the template-owned `ws-*` skills, so `./scripts/ws upgrade` stays clean. Also consolidates the learnings (merge, promote, prune stale ones) and sends improvements every project would want upstream to the overdeck template as a PR. Use when the user says "remember this", "learn this", "note that", "catat ini", "ingat ini", "jangan ulangi", corrects how you worked, or asks to consolidate / clean up learnings or send them upstream. Every `ws-*` skill also calls § Record as its last step.
---

# ws-learn

The workspace learns by writing lessons into files that the next session reads anyway. The
hard rule that keeps it upgradable: **in a project, lessons never go into template-owned
files** — the paths under `owned:` in [`.overdeck/upstream.yaml`](../../../.overdeck/upstream.yaml)
and the `<!-- overdeck:begin … -->` blocks of the files under `blocks:`. `./scripts/ws upgrade`
overwrites those; anything written there is lost or blocks the upgrade.

**Template or project?** `./scripts/ws template` prints `template` or `project` (it compares
`origin` with `source:` in `.overdeck/upstream.yaml`, ignoring ssh/https and `.git`). In the
template, improving the skills is the point: edit them directly. Everywhere else, follow this file.

## Record — one lesson, ≤ 2 minutes

**Record at the moment it happens**, not at the end: the user corrects you, a command, path
or doc turns out wrong, a detour costs time that a sentence would have saved — record it
right then, then carry on with the task. The end of a session is the step most often lost
(context compacted, run failed, user gone). This holds in plain sessions too, not only
inside a `ws-*` skill. Also called by the user ("remember this", "catat ini").

The **last step of every `ws-*` skill is a sweep**, not the main capture: anything from this
run not yet recorded? No → skip silently, say nothing.

1. **Is it worth keeping?** Only if it rests on something that happened (a correction, a
   failure, a wrong doc), would plausibly change what the next session does, and isn't
   already written down (`rg` the target first — sharpen the existing line instead of
   adding one). A one-off, a guess, or the user's personal taste → not here (taste goes to
   your own memory, not the workspace).
2. **Route it** — the most specific place that a future session already reads:

   | The lesson is about | Write it to |
   |---|---|
   | A project fact: command, path, port, env var, tool quirk, branch, deploy rule | `WORKFLOW.md`, in the matching § (1–8); no § fits → § 9 *Lessons* |
   | How a `ws-*` skill should behave **in this project** | `.agents/overlays/<skill>.md` (create from the README example) |
   | A domain word, or two words used for one thing | `context/glossary.md` |
   | Who can do what; an external system that calls us or that we call | `context/actors.md` |
   | A domain rule, state or invariant ("a paid order is never edited") | `context/domain/<concept>.md` |
   | How a feature works across repos; a boundary rule (errors, IDs, time) | `context/architecture/<feature>.md` / `contracts.md` |
   | A third party's quirk, webhook or failure mode | `context/integrations/<service>.md` |
   | A lasting cross-repo choice the team made | a new `context/decisions/<prefix>-dNNN_<slug>.md` (`./scripts/ws next decision`) — ask first |
   | What we want: users' goals, surfaces, principles, product wording, UI | `PRODUCT.md` / `DESIGN.md` |
   | A document or link to keep ("remember this PRD") — not a lesson | `sources/<topic>/` + a row in `sources/README.md` |
   | A rule every agent in this workspace must follow | `AGENTS.md`, **outside** the `overdeck:begin/end` blocks |
   | Models, effort, parallelism | `agents.yaml` for the team; one member's own preference → their `agents.local.yaml` (gitignored) |
   | A convention inside one app repo | that repo's `AGENTS.md` — **suggest only**: show the diff, the repo owns it |
   | A `ws-*` skill improvement **every** project would want | a `plans/ws-learnings.md` line tagged `upstream` (§ Upstream) |

   Both a project rule and a general one? Write the overlay rule now (it helps today) and
   also tag it `upstream`. A `context/` note that doesn't exist yet → create it from
   [`templates/context/`](templates/context/), fill only what you know, and add its row to the
   `context/README.md` index.
3. **Write it** as one or two lines in the target's own style, with the reason:
   `- <rule> (why: <date>, <what happened>)`. Prefer deleting or tightening a wrong line to
   adding a new one.
4. **Log it** in `plans/ws-learnings.md`, in the one line format its header gives:
   `- YYYY-MM-DD · <source> · <lesson> · → <target> · status: applied`
   (`status: proposed` for suggest-only targets; add ` · upstream` when tagged). Seen
   before → add the source to that line instead; a `proposed` lesson from 2+ sources is
   `recommended`.
   **Seen again after it was `applied` or `upstreamed` → the rule failed**, it is not a
   pattern. Mark the line `status: recurred <date>` and fix the rule, not the count: move it
   where the agent that made the mistake reads it (an implementer reads only its brief —
   WORKFLOW.md § 9 / overlay rules reach it through the brief's *Lessons* slot), make it
   sharper, or make it mechanical (a check, a script line). Then set it `applied` again with
   the new target. Recurring twice → tell the user; the rule may be wrong.
5. **Ask or just do it?** Project-owned docs (`WORKFLOW.md`, overlays, `context/` notes except
   decisions, `ws-learnings.md`): write it, then tell the user in one line (`Learned: <rule> → <file>`).
   `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, `agents.yaml`, a new decision: show the line and ask first. An
   app repo's `AGENTS.md`: suggest only. Don't commit unless asked.

## Consolidate — when asked, or when `ws doctor` says so (~40 open lines, an overlay over ~20 rules)

1. Run `./scripts/ws doctor` (its *learnings* block counts open lines, oversized overlays
   and paths rules name that no longer exist), then read `plans/ws-learnings.md`, every
   `.agents/overlays/*.md` and `WORKFLOW.md` § 9.
2. `recurred` lines first (§ Record step 4). Then merge duplicates; mark lessons with 2+
   sources `recommended`.
3. **Stale:** a rule naming a file, command or symbol that no longer exists (`rg` it in
   `repositories/`) → propose deleting it. Same for `context/` notes whose cited paths or
   symbols are gone → propose re-checking them and moving their `Checked against:` stamp.
4. **Misplaced:** a § 9 lesson that belongs in a specific `WORKFLOW.md` § → move it; an
   overlay rule that is really general → tag it `upstream`.
5. **Covered upstream:** after a `./scripts/ws upgrade`, an overlay rule the skill now says
   itself → delete it, and mark its learning `status: upstreamed`.
6. `./scripts/ws doctor` lists template-owned files edited in this workspace → move each
   edit into an overlay or an `upstream` line, then restore the file (the doctor says how).
7. Show the user the deletions and moves in one list (AskUserQuestion, multiSelect) and
   apply only the chosen ones.

## Upstream — send general lessons to the template

1. Collect `plans/ws-learnings.md` lines tagged `upstream` with `status: proposed`,
   `recommended` or `applied` (applied = an overlay holds it for now).
2. For each, write the general version: no project names, paths, stacks or product terms.
   Can't be said without them → it isn't general; drop the tag.
3. Show the user the list and the target skill files, and ask before anything leaves this
   machine — it opens a PR on the template repo (`source:` in `.overdeck/upstream.yaml`).
4. On a yes: work in a fresh clone of the template under the scratchpad (never in
   `.overdeck/cache`, which `ws upgrade` owns), one branch, one commit per lesson, one PR
   (`gh pr create`) whose body lists each lesson with its evidence from this project.
5. Mark the lines `status: upstream PR <url>`. Once it merges and `./scripts/ws upgrade`
   brings it in, § Consolidate step 5 removes the overlay rules it replaced.
