# BOOTSTRAP.md — turn this template into a project workspace

You are an agent setting up a new **overdeck** workspace. Do these steps once, in order,
then delete this file. Ask the user only what you can't find out yourself; ask it all at once.

## 1. Ask

1. **Project name** (short slug, e.g. `acme`) — replaces `__PROJECT__`.
2. **GitHub owner** of the app repos — replaces `__OWNER__`.
3. **Repos**: for each one its SSH URL, default branch, role, and whether it is ours (`repos:`)
   or someone else's read-only reference (`knowledge:` — then also its `owner:` and
   `read-when:`). Which of ours calls, depends on, publishes to or follows which (`relations:`)
   — recommend these from what the code shows after § 2's sync, don't ask blank.
   Repos that don't exist yet: offer to create them with `gh repo create`.
4. **One paragraph** on what the product is and who uses it (for `PRODUCT.md`).
5. **You, as the first member** (for `members.yaml`): `code`, `prefix`, `name`, git `emails`,
   `language`, `tone`, plus the workspace's `docs_language`. Don't ask blank — **recommend
   every value** from what you already know and let them confirm or correct:
   `git config user.name` / `user.email` (code = `firstname.lastname`, prefix = initials,
   lowercase), the language they are writing to you in, and any preference you remember about
   them (your memory, their user-level instructions). No git email set → ask for it and offer
   `git config user.email <it>`. Other members are added the first time each one works here
   (`AGENTS.md` § Members).

## 2. Fill in

- `workspace.yaml` — one block per repo under `repos:` or `knowledge:`; remove the sample
  blocks. After the sync below, fill each `repos:` entry's `relations:` from what the code
  really calls and imports, and confirm them with the user; `./scripts/ws doctor` checks them.
- `AGENTS.md` — the repo table (and the knowledge table, or delete it), the "Working rules"
  lines per repo, the design routing.
- Then `./scripts/ws sync` and read each repo's `AGENTS.md`, `README`, package manifest and
  CI config to fill `WORKFLOW.md` §§ 1–7 from the real code (install, typecheck, lint, test
  commands, dev server port, local config files, deploy trigger). Leave § 9 empty.
  Mark anything you couldn't verify with `<!-- TODO: confirm -->` and list it in your report.
- `PRODUCT.md` from the user's paragraph; `DESIGN.md` stays a stub until the first UI work.
- `context/` — seed from the repos you just read, stamping each with `Checked against:` the
  commits you read: `glossary.md` (the domain words that recur in models, routes and UI),
  `actors.md` (roles from auth/permission code, external systems from env vars and clients),
  `architecture/overview.md` and `architecture/contracts.md` (auth, errors, IDs, time, paging as
  the code really does them). Fill the index in `context/README.md`. Leave `domain/`,
  `integrations/` and `decisions/` empty: they grow when work first needs them. Unsure →
  `<!-- TODO: confirm -->`, as above.
- `agents.yaml` — set `max_parallel` to the number of code repos; keep the models unless asked.
- `members.yaml` — replace the `__MEMBER*__` entry with the first member; set `docs_language`.

## 3. Check

- `grep -rn '__PROJECT__\|__OWNER__\|__MEMBER' --exclude=BOOTSTRAP.md .` returns nothing.
- `./scripts/ws whoami` prints the first member's code; `./scripts/ws next plan` prints `<prefix>-001`.
- `./scripts/ws doctor` exits 0.

## 4. Finish

Run `./scripts/ws upgrade --init`: it finds the template commit this workspace was created
from (by matching the workspace's first commit) and writes it to `.overdeck/upstream.yaml` as
`base:`, so later `ws upgrade` runs know what changed. Project text in `AGENTS.md` goes **outside** the `overdeck:begin/end` blocks.

Delete `BOOTSTRAP.md`, remove the "New workspace?" note at the top of `AGENTS.md`, and commit
(`chore: bootstrap <project> workspace from overdeck`). Report what you filled in and every TODO, then the few things a member should know: their
ID prefix, `agents.local.yaml` for personal model choices, and "remember this" (`ws-learn`).
From here on, talk to them in their `language` and `tone`.
