# BOOTSTRAP.md — turn this template into a project workspace

You are an agent setting up a new **overdeck** workspace. Do these steps once, in order,
then delete this file. Ask the user only what you can't find out yourself; ask it all at once.

## 1. Ask

1. **Project name** (short slug, e.g. `acme`) — replaces `__PROJECT__`.
2. **GitHub owner** of the app repos — replaces `__OWNER__`.
3. **Repos**: for each one its SSH URL, default branch, role, and `code` or `knowledge`
   (read-only reference). Repos that don't exist yet: offer to create them with `gh repo create`.
4. **One paragraph** on what the product is and who uses it (for `PRODUCT.md`).

## 2. Fill in

- `workspace.yaml` — one block per repo; remove the sample blocks.
- `AGENTS.md` — the repo table, the "Working rules" lines per repo, the design routing.
- Then `./scripts/ws sync` and read each repo's `AGENTS.md`, `README`, package manifest and
  CI config to fill `WORKFLOW.md` §§ 1–7 from the real code (install, typecheck, lint, test
  commands, dev server port, local config files, deploy trigger). Leave § 9 empty.
  Mark anything you couldn't verify with `<!-- TODO: confirm -->` and list it in your report.
- `PRODUCT.md` from the user's paragraph; `DESIGN.md` stays a stub until the first UI work.
- `context/architecture/README.md` — replace `__PROJECT__`.
- `agents.yaml` — set `max_parallel` to the number of code repos; keep the models unless asked.

## 3. Check

- `grep -rn '__PROJECT__\|__OWNER__' --exclude=BOOTSTRAP.md .` returns nothing.
- `./scripts/ws doctor` exits 0.

## 4. Finish

Delete `BOOTSTRAP.md`, remove the "New workspace?" note at the top of `AGENTS.md`, and commit
(`chore: bootstrap <project> workspace from overdeck`). Report what you filled in and every TODO.
