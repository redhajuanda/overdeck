---
name: ws-plan
description: Plan a feature, change request, non-trivial bug fix, refactor or any non-trivial work in this multi-repo workspace (repos declared in `workspace.yaml`) before implementing it — reads the affected code in every repo it touches first, then writes plans/<member>/NNN_slug/plan.md with file-level changes, ordered tasks and acceptance checks. Always confirms the source branch to read first. Use when the user asks to plan, scope, design, spec, estimate or "think through" a feature/CR, asks "how would we build X", or says "buat plan" / "rencanakan". Also use to revise or re-verify an existing plan in plans/, or to plan from an agreed intent in intents/ ("plan intent 007"). Not for small, already-clear edits (known files, no new cross-repo contract) — those use ws-direct, including when the user says "edit directly" / "langsung edit" (several commits is still ws-direct). Not for `/ws-explore` (a sticky session of small UI/wording/style tweaks).
---

# ws-plan

> **Project overlay.** If `.agents/overlays/ws-plan.md` exists, read it before anything else: its
> rules are this project's additions to this skill and win where they conflict. Pass the ones
> that concern a subagent into its brief. Never edit this skill in a project — lessons go
> through [`ws-learn`](../ws-learn/SKILL.md).

A plan has two readers, and must work for both:

- **A human** (owner, reviewer, teammate) who wants to understand *what* we're building and
  *how it works* in a few minutes, without reading code.
- **An implementer who has not read the code yet** — often a subagent with an empty context —
  who must start on task 1 without re-exploring and without guessing.

So the plan is layered: **plain words and diagrams first, exact detail after.** A human can stop
reading after *How it works*; an agent reads to the end. Read code before writing, cite what you
read, and write only what changes a decision or an edit. Nothing in it may turn out to be false.

## 0a. Confirm the source branch — always the first thing

Before reading any code (and before §0 / §1), confirm **which branch of each repo the plan is
read from**. That branch is the plan's *source branch*: recon reads it, the header's `Based on:`
records it, and ws-implement later cuts `feat/NNN-slug` from it and opens the PR into it.

- Show the default per repo from `workspace.yaml` (its `branch:` field) plus any likely alternative (`git -C repositories/<repo> branch -r --sort=-committerdate | head -5`,
  or a `feat/…` branch of a plan this one builds on).
- Ask with `AskUserQuestion` — one question, plain words, the default as the first option
  `(Recommended)`. Only the repos this plan may touch; if unsure which, ask for all of them.
- Skip the question only when the user already named the branch in their request — then
  state it back in one line ("Planning against <repo-a> `<branch>`, <repo-b> `<branch>`.").
- Revising an existing plan: confirm its `Based on:` branches the same way before re-reading.
- Knowledge repos (`knowledge:` in `workspace.yaml`) are not asked about: they are read at
  their tracked branch, as synced.

A non-default source branch: `git -C repositories/<repo> fetch origin <branch>` and read it in
a detached read-only worktree, `git -C repositories/<repo> worktree add --detach
.worktrees/NNN_slug-recon/<repo> origin/<branch>` (absolute path), pointing the recon subagent
there. Never switch the branch of the clone in `repositories/`. Remove the recon worktree when
the plan is written.

## 0. Where the plan goes

| Scope | Location |
|---|---|
| Small, already-clear, no new contract (or the user said "edit directly") | Hand off to **ws-direct** — no `plan.md` |
| `/ws-explore`, or a session of small UI/wording/style tweaks they will push later | Hand off to **ws-explore** — no `plan.md` |
| Touches 2+ repos, or product/schema decisions | `plans/<code>/NNN_slug/plan.md` here (your next ID, see below; snake_case slug) |
| One repo, and `WORKFLOW.md` § 8 names a spec flow for it that the change fits | Hand off: tell the user, use that flow instead |
| One repo, no spec flow | `plans/<code>/NNN_slug/plan.md` here is fine |

`<code>` and the ID come from the member running this session (`AGENTS.md` § Members):
`./scripts/ws whoami` for the folder, `./scripts/ws next plan` for the ID (`rj-043`). The ID
carries the member's prefix, so other members can't collide with it; run `ws next` **right
before** creating the folder anyway, since a peer session of the same member may have taken
one meanwhile. Split into several plans → take the IDs one by one as you create them.

Run `./scripts/ws doctor` first; `./scripts/ws sync` if a repo is missing or stale — a plan
written against a stale checkout is wrong on arrival. Note each repo's branch + short SHA in the
plan header as `<source branch>@<sha>` (`git -C repositories/<repo> rev-parse --short origin/<source branch>`).

## 0b. Start from an intent, when there is one

An intent (`intents/<code>/NNN_slug.md`, written with the ws-intent skill; find it with `./scripts/ws find intent <id or slug>`) is the agreed *what and
why*. If the user names one, or the request matches an active intent's slug, read it first.

- `Status: draft` → it isn't agreed yet. Ask whether to finish it with ws-intent first or plan
  anyway (then treat it as input, not as fixed).
- `agreed` / `planned` → its Outcome, Scope and Non-goals are **fixed**. Each plan's *Goal*
  links to it (`Intent: intents/<code>/NNN_slug.md`) instead of rewriting it; *In plain words* stays.
  Its *Likely plans* seeds the split in §1b and its *Evidence* is where recon starts.
- **Code contradicts the intent** (a non-goal turns out to be required, the chosen direction is
  blocked, the cost is far beyond what the intent assumed) → stop and ask the user. Never
  silently widen or narrow scope. If they change it, revise the intent (ws-intent *Revising*).
- After writing the plans: add them to the intent's `Plans:` line and set its status to
  `planned · YYYY-MM-DD`.

No intent and the request is **big** (likely 3+ plans) or **unclear about what the user wants**
(several reasonable directions, no clear outcome)? Suggest ws-intent in one line and let the user
choose; it is optional. Bug fixes and small, clear changes never need an intent; if they also
don't need a plan (known files, no new contract), hand off to **ws-direct** (ship now)
or **ws-explore** (`/ws-explore`, a sticky session).

## 1. Frame the ask (≤ 5 minutes, no code yet)

Write down, for yourself: the user-visible outcome, who it's for (the user roles in `WORKFLOW.md` § 3), and
what "done" looks like. If the request is ambiguous in a way that **changes which code you'd
read**, ask now (AskUserQuestion, ≤ 3 questions, recommended option first). Everything else,
pick a sensible default and record it under *Decisions*.

Load context that applies — and only that:
- Each repo you'll touch: skim its `AGENTS.md` for rules that constrain the design (the
  subagent for that repo reads it in full).
- Product, design and schema docs that apply to this kind of work (`WORKFLOW.md` § 3).
- `context/`: the glossary always; from the `context/README.md` index, the domain,
  feature, integration and decision notes on this topic; `architecture/contracts.md` when the
  change crosses a repo boundary. Treat stamped notes as leads, not truth — the recon in § 2
  confirms them. An accepted decision is a constraint: going against it needs the user's yes
  and a new decision that supersedes it (ws-archive writes it).
- Which repos the change reaches: `./scripts/ws relations <repo>` for each repo you expect to
  touch. A `calls` / `consumes` / `depends-on` edge into a touched repo is a reader of what
  you change — check it in recon even if no task lands there.
- Knowledge repos (`knowledge:` in `workspace.yaml`, cloned in `repositories/knowledges/`)
  whose `read-when:` matches the topic, or that a touched repo `follows` / `depends-on`: give
  each one a recon subagent like any repo (§ 2), read-only by nature. List them on the plan's
  `Knowledge:` header line as `<name>@<sha>`. **Never put a task in one.** A change it would
  need goes under *Upstream asks* (for its `owner:`); a task blocked on it says so.
- Outside material: the `sources/README.md` index — open only the rows on this topic (and
  `project/` when timing or scope matters); list the ones the plan relies on in its
  `Sources:` header line.

## 1b. Split into small plans — one per feature or CR

One plan = **one outcome a user can notice, shipped and reviewed on its own**. A request that
bundles several features, a CR with several independent changes, or a feature that needs a
shared building block becomes **several plans**, not one long one. Small plans are easier to
read, to review, to hand to an implementer, and to cancel one without the others.

Split along these lines (first match wins):

| Situation | Split into |
|---|---|
| Request names several features / CRs ("add export, search and sharing") | one plan per feature |
| A capability **two or more plans need** (a schema flag, a shared toggle, a new option system) | its own plan, done first; others `depend on` it |
| One feature with a platform part and a content part (a platform capability vs. rolling it out to dozens of content items) | keep together **unless** the rollout is large or has its own sign-off — then a separate rollout plan |
| One feature whose phases ship separately (MVP, then admin tools, then analytics) | one plan per phase that ships on its own |
| Changes that would release and be reverted together | keep in **one** plan |

Never split **by repo** (a "<repo-a> plan" and a "<repo-b> plan" for the same feature) — the contract
between them is the part that must stay in one place. A plan is too big and should be split
when it has **> ~10 tasks**, **> ~300 lines**, or **more than one release step** that could
ship alone.

**Don't split into a stack.** Plans that build on each other's code in the **same files** of the
same repo (plan B edits what plan A adds) are implemented as stacked branches: every fix in A
forces a rebase of B and C, and merge conflicts land there. So:
- Split only where the parts can be built **side by side** (different files, or B uses only A's
  published contract), or where a part must **ship on its own** before the next starts.
- Otherwise keep them in **one plan**, even past ~10 tasks (up to ~15): put the later part in
  a clearly marked final phase of *Tasks* ("Phase 2 — editor card") rather than in its own plan.
- Never more than **two** plans in one dependency chain for one intent. A third link means the
  split is by layer, not by shippable outcome — merge it into its neighbour.
State in *Decisions* why a split that does stack can't be avoided.

Before reading code, write the split as a list for yourself: plan name, outcome, `depends on`.
Re-check it after step 2 — the code often reveals a shared building block (→ its own plan) or
shows two "features" are really one change (→ merge). If the split is a real product choice
(e.g. MVP scope), ask the user; otherwise decide and show it.

Each plan of a split:
- gets its own number and folder, and states `depends on:` / `blocks:` in its header;
- repeats only what its reader needs; refers to the other plan for the rest
  (`see plan NNN § Contracts`), never copies its contract;
- is written and self-checked fully (steps 3–5) — a split is not an excuse for a thin plan.

When a split produces **3+ plans**, end your reply to the user with a Mermaid `flowchart LR` of
the plans and their dependencies, plus the recommended order.

## 2. Read the affected code (the part that makes the plan accurate)

Trace the feature **end to end along its data path**, not file by file. This workspace's typical
path is in `WORKFLOW.md` § 2; in general: schema / source of truth → producer repo → consumer
repo → UI.

For larger changes the reading is done by **one subagent per repository**, in parallel, so
each one keeps a narrow focus and its file dumps stay out of the main session. The main
session briefs them, reviews what comes back, and owns every claim that goes into the plan.

### 2·0. Subagents or read it yourself? — decide per repo

A subagent costs a self-contained brief (~3–4k tokens), its own warm-up (AGENTS.md, orienting)
and your review of its report. It pays off when the reading is big; for small reading, do it
directly — it's cheaper and faster.

| For this repo… | Do |
|---|---|
| you already know the files, and need **≤ ~6 files** read and **≤ 3 open questions** | read it yourself (`rg` + targeted `sed -n`/Read ranges, not whole files) |
| **> ~6 files**, **> 3 questions**, or you don't yet know where the code lives | dispatch a subagent (2a–2d) |
| the repo is untouched except for one yes/no fact ("does <repo-b> validate X?") | one `rg` yourself; no subagent |
| several plans touch the same repo at once | **one** subagent per repo answering all plans' questions, not one per plan |

Mixed is normal: e.g. read `<repo-b>` yourself, dispatch `<repo-a>`. Note the choice
in one line to the user. When you read yourself, the rules in "Rules while reading" still apply.

### 2a. Pick the model — from `agents.yaml`

Only for repos where 2·0 chose a subagent. Read `agents.yaml` at the workspace root, then `agents.local.yaml` if it exists (personal overrides, key by key — see the header of `agents.yaml`). Use the block for the tool you are running in
(`subagents.claude` in Claude Code, `subagents.codex` in Codex, `subagents.cursor` in Cursor), then apply any override under
`roles.repo-recon`. Never hard-code a model in a prompt or in this skill. If the file is
missing, use the session's default model and say so to the user.

### 2b. Decide which repos and what to ask (main session)

Before dispatching, sketch the data path yourself from the request + the schemas the
profile names (`WORKFLOW.md` § 3) + a quick `rg` for the domain words. Out of that, write for **each repo that the change touches**:
- what that repo's part of the feature is, in one or two sentences;
- 3–8 **specific questions** you need answered to plan it ("Where is the
  field list for form X built, and does it read flag Y?"), not "look around";
- known names to start from (routes, types, schema keys, file paths) and the boundary shapes
  you expect to cross into the other repos.

Skip a repo the change truly doesn't touch — but if unsure (e.g. "does <repo-b> validate payload
X?"), dispatch it with that one question.

### 2c. Dispatch — one subagent per repo, all in one turn

Fill [`subagent-prompt.md`](subagent-prompt.md) once per repo — every placeholder, no
"see above": the subagent has **no** access to this conversation. Then launch them together:

- **Claude Code** — `Agent` tool, one call per repo in the **same message**:
  `subagent_type: "general-purpose"`, `model` = the family word of the `agents.yaml` ID (`claude-sonnet-5-5` → `sonnet`; the Agent tool only takes family words; it resolves to that family's current model, so an older ID in `agents.yaml` shows up as a mismatch below). After launch, check the result's `resolvedModel` equals the `agents.yaml` ID; if not, stop and tell the user, `effort` from `agents.yaml`,
  `description: "Recon <repo> for <feature>"`. Results arrive as task notifications; wait for
  all of them. Don't redo their searches meanwhile.
- **Codex** — use the native subagent/spawn tool with the `agents.yaml` model if this Codex
  build has one; otherwise run each in the background and wait:
  ```bash
  codex exec -m <model> -c model_reasoning_effort=<effort> -s read-only \
    -C <workspace>/<repo> --skip-git-repo-check --ephemeral \
    -o <scratch>/recon-<repo>.md - < <scratch>/prompt-<repo>.md
  ```
- **Cursor** — its subagent tool with `model` from the `cursor` block (`inherit` = this chat's
  model), read-only. Cursor can ignore a pinned model, so note which model you asked for.

Respect `roles.repo-recon.max_parallel`.

Before dispatching, check each clone is at the tip it will be read from:
`git -C repositories/<repo> rev-parse HEAD` must equal `origin/<branch>`. If it doesn't, point
the subagent at a detached recon worktree on `origin/<branch>` (§ 0a), not at the clone. A
clone left behind by another session gives confident answers about code that has since changed.

### 2d. Review each report (main session) — don't trust, verify

A report is a lead, not a fact. For each one:
1. **Format check** — every finding has `path:line` (or symbol) evidence; anything without it
   counts as unverified.
2. **Spot-check the load-bearing claims yourself** — open the cited lines for: every file the
   plan will tell someone to change, every boundary shape (DTO / schema / struct / JSON key),
   and anything surprising. Aim for the 3–6 files the design rests on. If a citation is wrong,
   distrust the rest of that report and re-check more of it.
3. **Cross-check the repos against each other** — put the repos' shapes side by side:
   field names, casing (`camelCase` vs `snake_case`), optional vs required, enums, IDs. A
   mismatch is a finding in its own right; it goes into *Current state* or *Open questions*.
4. **Fill the gaps** — an unanswered question, a vague answer ("it's handled somewhere in the
   service layer"), or a new question the reports raised → send a follow-up to the **same**
   subagent (Claude: `SendMessage` to its id; Codex: re-run with the previous report pasted in
   plus the new questions). Small gaps you can close with one `rg`/read, close yourself.
5. Stop when every question from 2b has a cited answer or is consciously parked as an open
   question.

If a repo ships a code-graph / code-exploration skill (`WORKFLOW.md` § 1), tell a subagent to use
it when the impact radius is unclear.

Rules while reading (for subagents and main session alike):
- **Verify, don't assume.** Every path, symbol, line number and behaviour claim in the plan
  must come from something opened this session — by a subagent with a citation you accepted
  in 2d, or by you. If you couldn't verify it, mark it
  `(unverified)` and add it to *Open questions*.
- Prefer symbol anchors over bare line numbers (`path/to/file.ext` `buildFields()` ~L296) —
  lines drift.
- When the plan relies on a value reaching a component through a prop, check **every render
  site** of that component passes it (one branch often renders it without the prop). Check also
  that the user can reach the element the plan changes (it is selectable, not filtered out
  of a list).
- Note what you found that **constrains** the design (an existing enum, a unique index, a
  renderer that strips `\n`, a cache). Those belong in *Current state*.

## 3. Decide

For each real fork in the road, pick one and say why in 1–3 lines. Use an options table only
when there were genuinely competing designs. Push back on scope that the code shows is
expensive for little gain. Anything that's the user's call (product behaviour, pricing, copy,
rollout timing) and can't be defaulted → *Open questions*, with your recommendation.

A plan whose main output is a **new visual page or section** (a layout the user hasn't seen), or that changes the size, spacing or proportions of existing visual output (geometry, borders), gets a
static mockup with real assets, published as a page the user can open. The user approves it before
implementation is dispatched. The approved values go into the tasks, and its link goes in *Decisions*.
Text-only visual specs get rebuilt after the user sees them (139: T4/T5 rebuilt after 6 mockup rounds).
The mockup has one section per screen the plan changes visually, not only the newest one (231: sheet rows only, the landing and onboarding chips were missing, so it was rebuilt).
Check the mockup at every viewport width the plan's Acceptance or Verify names, not only phone + one
desktop (142: nav wrapped at 1440 px, unchecked in the mockup → review major + fix round).

## 4. Write the plan

Copy [`template.md`](template.md) to `plans/<code>/NNN_slug/plan.md` and fill it. Fill it top-down
in this order of readers: *In plain words* → *How it works* (diagrams) → detail → tasks.

### 4a. Words — write so a non-engineer understands and an agent can't misread

- **Short sentences, common words.** "The editor saves the note" beats "persistence of the note
  entity is triggered by the editor component". Active voice; say who does what.
- **One name per thing, everywhere.** Pick a term once (e.g. "saved draft"), define it in the
  *Glossary*, then never swap in synonyms ("autosave", "backup copy"). An agent treats two words as
  two things. Use the code's real name in backticks the first time: saved draft (`drafts`).
- **Be exact, not vague.** Replace "handle", "support", "improve", "update accordingly", "etc.",
  "should probably" with the concrete action: *which* file, *which* field, *what* value,
  *what* happens on error. Numbers instead of "some"/"a few".
- **Say the rule, then the example.** "Hidden items take no space — e.g. hiding item 2 moves
  item 3 up."
- **Define jargon on first use** or avoid it. Product words defined in the project's product docs
  (`WORKFLOW.md` § 3) are fine; internal acronyms aren't, until defined.
- **Must / should / may** mean required / recommended / optional. Use them that way only.
- Every term that is a domain concept, a code name, or could mean two things → *Glossary*.
  Terms already in `context/glossary.md` are used as written there and not redefined; the plan's
  *Glossary* holds only the new ones, and ws-archive adds those to `context/glossary.md` when
  the plan ships.
- The plan's *Contracts* add only what is new; they follow `context/architecture/contracts.md`
  (error shape, IDs, time, casing) and say so where it matters.

### 4b. Diagrams — show the flow, don't just describe it

Use **Mermaid** in fenced ` ```mermaid ` blocks: GitHub and most editors render it, and agents
read it as plain text. Every plan has **at least one** diagram in *How it works*; pick by what
the change is about:

| The change is mainly about… | Diagram |
|---|---|
| who calls whom across repos / services / storage over time (API calls, saves, uploads) | `sequenceDiagram` |
| user steps, branches, decisions, error paths | `flowchart TD` |
| something with states (draft → published, pending → paid) | `stateDiagram-v2` |
| new/changed tables or JSON structure | `erDiagram` or `classDiagram` |
| which repos/modules change and how they connect | `flowchart LR` with subgraphs per repo |

Diagram rules:
- Label with the **same words as the Glossary**; node/participant names match real things
  (`UI (<repo-a>)`, `API POST /v1/<resource>`, `<resource> table`), with code names in labels when they help.
- Show the **error / empty / edge path**, not only the happy path (`alt` / `else` in sequences,
  a "no" branch in flowcharts).
- Mark what is **new or changed** (e.g. `:::new` class or a `(new)` label) so readers see the delta.
- Keep each diagram ≤ ~15 nodes/steps. Split into two diagrams rather than one wall.
- Add one sentence under each diagram saying what to notice.
- Make sure it parses: balanced quotes, no raw `()`/`[]`/`:` inside labels unless quoted
  (`A["save (draft)"]`). Render-test from a scratch dir (writes SVGs next to the output):
  `npx -y @mermaid-js/mermaid-cli -i <path>/plan.md -o out.md -p <(echo '{"args":["--no-sandbox"]}')`
  — every chart must print ✅. If it can't run, re-read each block carefully.

### 4c. Structure and detail

- **Omit sections that would be empty or obvious** — except *In plain words* and *How it
  works*, which every plan has. A small fix might be those two + Current state + Changes +
  Tasks + Acceptance.
- Tables for anything enumerable (files, fields, endpoints, objects). Prose only for reasoning.
- Show **contracts** exactly (JSON / struct / schema / SQL snippets, endpoint + method + payload), not
  implementations. Code snippets only where the shape is the decision. Every error code that
  carries a payload names its `data` shape.
- A response the UI picks a state from (empty vs. hidden vs. loading, a mode, a status) carries the
  field that decides the state, not only the data.
- When a change alters a response shape, *Contracts* list **every** endpoint whose response the
  consumer parses with the same schema (list, detail, mutation responses), not only the one the
  feature is about. A required field one of them doesn't send breaks that screen.
- A new migration file gets a placeholder name (`<next-after-newest>-<name>.sql`), not a fixed
  timestamp: peer plans merge meanwhile, and the implementer picks the real one from its base.
- Run every example payload in *Contracts* through the real validator, refinements
  included, before finalising. An example the existing rules reject is a contract the
  implementer can't satisfy.
- Numeric expectations for an algorithm's tests (thresholds, expected outputs) are computed
  against the plan's own constants with a throwaway script before finalising. Otherwise state
  only the direction ("brighter", "smaller"): an unreachable target becomes a deviation.
- An engine-specific expression in *Contracts* (a SQL function, a JSON path, a regex) is run once on a
  throwaway instance (e.g. a docker database) with true / false / NULL / malformed inputs before
  finalising. The same function can return a different type than its name suggests.
- A guard on state another process can change at the same time (a worker's claim, a status) says how
  the check and the action stay atomic: one transaction or a conditional write. A read followed by a
  separate write races (140 T6: check-then-delete still orphaned files).
- A task that narrows a read (a LIMIT, a filter, a smaller window) lists every value the old result
  fed (counts, flags, the viewer's own row) and says how each still gets it (144: the viewer's own
  older roll showed 0 photos → review fix).
- A validation rule must hold on **every side of a boundary that parses the data**. Rules that
  don't survive schema generation (custom refinements, cross-field checks) are the usual gap:
  for each one, say in *Contracts* how the other side enforces it. If it can't, drop the rule,
  unless the other side tolerates the data. A strict reader receiving data the writer accepted
  is a broken contract, not a harmless gap.
  Name the exact scopes each such rule walks (sections, shared/general objects, stacks), so both
  sides cover the same set.
- When the plan states how something must look or behave on screen (a cover hides what's under
  it, a photo is the hero), give values that produce it (an opaque fill, a size relative to its
  slot). A decorative number that contradicts the stated behaviour gets implemented literally.
- A task that changes a default or template file names the test fixtures that clone it
  (`rg` the tests for its import) and says how they keep their old behaviour (strip the new
  value, or opt in per spec). Otherwise unrelated specs break on the new default.
- When a plan changes defaults or fallbacks, check whether a save path stores the derived
  values. Stored defaults are no longer defaults: a later change to the default won't reach
  them, so the plan must say how saved data follows.
- When a plan rewrites data whose shape another plan's *Contracts* define, restate that
  contract's precedence and default rules (which field wins, what an absent field means) in
  this plan's *Contracts*. Deriving a field afresh silently overwrites what users chose.
- **Tasks** are the core. Each task:
  - one repo, one coherent commit's worth (≈ ≤ 1–2 h, ≤ ~5 files);
  - names the files and the symbol/pattern to follow;
  - ends with a **Verify** line: the exact command or manual check that proves it done —
    scoped to single test files/packages (e2e: one spec), never a whole
    suite (see `WORKFLOW.md` § 5 and ws-implement § *Fast checks*). A UI interaction
    (click, hide, undo …) is never a "manual" Verify: name the e2e spec to add or extend,
    so the implementer writes it. The named spec must open the surface where the asserted
    element renders (e.g. editor vs end-user page vs admin); if no existing spec does, name a
    new one there. A Verify that repeats a test to prove it stable (`--repeat-each`) targets
    that test (`file:line`); the rest of its file runs once;
  - lists `needs: Tn` when ordered. Order so each task leaves the build green
    (schema / contract → producer implementation → consumer client → consumer UI → content → rollout).
  A task should be executable by a subagent that reads only the plan + the files it names.
- Acceptance = observable behaviour, checkboxes, testable by someone who didn't build it.
- Length: as long as the change needs and no longer — usually 80–200 lines. Reference docs
  (`see repositories/<repo>/AGENTS.md § Errors`) instead of restating them.
- In `docs_language` (`members.yaml`), matching the tone of existing `plans/*/*/plan.md`.

## 5. Self-check before showing it

Run through this; fix, don't just note:
- [ ] Every file path in the plan exists (`ls`/`rg` them — a quick loop over backticked paths) or
      is clearly marked **new**.
- [ ] Every symbol named exists where claimed; line hints are within a few lines.
- [ ] Shapes agree across all repos, field by field (names, casing, optionality), and with
      `context/architecture/contracts.md`.
- [ ] Domain words match `context/glossary.md`; nothing contradicts an accepted
      `context/decisions/` entry without the user's yes recorded in *Decisions*.
- [ ] Each task has files + Verify; dependencies form a valid order; no task needs a later one.
- [ ] Migrations, feature flags, backfills, cache/CDN, republishing of already-published
      artifacts, and backwards compatibility with existing data are addressed or explicitly N/A
      (plus the project's own compatibility items, `WORKFLOW.md` § 3).
- [ ] Every Acceptance line agrees with the Decisions and the decision diagram (fallback order, which source wins); a line the diagram contradicts is rewritten now.
- [ ] Non-goals stop the obvious scope creep.
- [ ] A change that locks something users can edit today (disables an input, makes a field
      read-only) names each locked field in *Decisions* with why locking it is fine.
- [ ] From an intent: the plan stays inside its Scope and Non-goals, and the intent's `Plans:`
      line and status are updated.
- [ ] The plan covers **one** feature / CR / shared building block (§1b); ≤ ~10 tasks and
      ≤ ~300 lines, or the reason it can't be split is stated in *Decisions*.
- [ ] `depends on:` / `blocks:` in the header match the other plans of the split.
- [ ] No `(unverified)` claim is load-bearing without also being an open question.
- [ ] Every subagent claim the plan relies on was spot-checked by you (2d), and the repos'
      reports were cross-checked against each other.
- [ ] *In plain words* makes sense to someone who has never seen the code.
- [ ] At least one diagram; each one parses, uses Glossary terms, shows an error/edge path,
      and marks what's new.
- [ ] Every term is used with one meaning only; no vague verbs ("handle", "support",
      "update accordingly") left in tasks.
- [ ] Each task could be done by an agent reading only that task + the files it names, with
      no question it would have to guess the answer to.

Then give the user: the plan path(s), a 3–5 line summary per plan (approach, repos touched, task count,
biggest risk), and the open questions that need their answer. Don't paste the whole plan.
Don't commit unless asked.

**Learn.** Record lessons when they happen ([`ws-learn`](../ws-learn/SKILL.md) § *Record*). Last, sweep for what slipped through: a correction, a wrong command or doc, or a detour from this plan (e.g. a recon claim that proved false, a question the docs should have answered) gets one line in the right project file. Nothing → skip silently.

## Revising an existing plan

Re-read the plan, then re-verify its *Current state* and task file references against the
current code (`git -C repositories/<repo> log --oneline <sha-in-header>..HEAD -- <paths>` shows what moved).
Edit in place, bump the header date/SHAs, and tick tasks that have already landed.
