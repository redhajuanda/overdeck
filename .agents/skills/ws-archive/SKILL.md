---
name: ws-archive
description: Archive a finished or abandoned plan in this multi-repo workspace (repos declared in `workspace.yaml`) — moves plans/<member>/NNN_slug/ to plans/<member>/archived/NNN_slug/ (creating the folder if needed), marks its status, updates context/architecture notes and PRODUCT.md with what the plan shipped, and removes its .worktrees/NNN_slug worktrees once nothing in them is unmerged. Also archives intents (intents/<member>/NNN_slug.md → intents/<member>/archived/) once all their plans are archived, or when abandoned. Use when the user asks to archive, shelve, close out or "arsipkan" a plan or intent, a plan number ("archive 042", "archive intent 007"), or all done plans.
---

# ws-archive

> **Project overlay.** If `.agents/overlays/ws-archive.md` exists, read it before anything else: its
> rules are this project's additions to this skill and win where they conflict. Pass the ones
> that concern a subagent into its brief. Never edit this skill in a project — lessons go
> through [`ws-learn`](../ws-learn/SKILL.md).

Archiving moves a plan out of the active list. It never edits code. The only thing it deletes
is the plan's own worktrees (step 6), and only once they hold nothing unmerged.

## Steps

1. **Resolve the plan.** `./scripts/ws find plan <id, number or slug>` — it searches every
   member's folder, the session member's first. `P` = the match outside `archived/`, e.g.
   `plans/redha.juanda/rj-042_checkout`; `<code>` = its member folder, `NNN_slug` = its name. No
   match, or several active ones → list the candidates and ask. Only an `archived/` match →
   say it is already archived and stop.
2. **Check it is safe to archive.** Read `plan.md`: note its `Status:` line and any unticked
   tasks. Unticked tasks or a status like `proposed` / `in progress` mean unfinished work — tell
   the user and get a yes before continuing (an abandoned plan is fine to archive; say that in the
   status below). A plan that other active plans list in `depends on:` → mention it.
3. **Move it.** `mkdir -p plans/<code>/archived`, then `git mv "$P" plans/<code>/archived/NNN_slug`
   (plain `mv` if the plan is untracked). It stays in its author's folder, whoever archives it. Keep the directory name unchanged so references and the
   number stay stable.
4. **Mark the status.** In the moved `plan.md`, set the `Status:` line to
   `archived · YYYY-MM-DD` and keep the earlier state after it, e.g.
   `Status: archived · 2026-10-10 (was: implemented)`. Change nothing else in the file.
5. **Fix links.** `grep -rn "$P" --include=*.md . ` outside the repos' own
   directories (each `repositories/<repo>/`) and rewrite paths that now point to
   `plans/<code>/archived/NNN_slug`.
6. **Clean up its worktrees.** `W=.worktrees/NNN_slug` (made by ws-implement; older
   runs used `.worktrees/NNN` — clean that up too if present). For each
   `$W/<repo>`:
   - dirty (`git -C "$W/<repo>" status --porcelain`) → keep it and tell the user;
   - `git -C repositories/<repo> fetch origin <branch>` (branch from `workspace.yaml`), then
     `git -C "$W/<repo>" rev-list --count origin/<branch>..HEAD` > 0 → commits not on the base.
     They may be squash-merged, or they may be lost work: list them (`git log --oneline`) and ask
     before removing;
   - otherwise `git -C repositories/<repo> worktree remove "$PWD/$W/<repo>"`. Keep the `feat/NNN-slug` branch.
   Then `rmdir "$W"` if it's empty. `./scripts/ws doctor` should show none of this plan's
   worktrees afterwards.
7. **Its intent.** If the plan header has an `Intent:` line, open that intent and check its
   `Plans:` line. Every listed plan now under an `archived/` folder → archive the intent too (see
   below); fix the plan's `Intent:` link if the intent moved.
8. **Sync the docs with what shipped.** Skip for an abandoned plan, or one whose PRs did not
   merge into the repo's `development` branch. Otherwise find its merged PRs (`<repo>#<n>` in
   the `Status:` line or the plan, else `gh pr list --repo <owner/name> --state merged
   --head feat/NNN-slug`) and read each diff (`gh pr diff <n> --repo <owner/name>`) — skim for
   behaviour, don't re-review.
   - **Architecture notes:** if a note in `context/architecture/README.md` covers an area the
     diff touches, fix what the diff made wrong or incomplete in that note and move its
     "Checked against" commit for that repo to the merge commit. Don't create new notes here.
   - **`PRODUCT.md`:** if the change alters what it describes (surfaces, users, flows,
     features, principles), update it. Move its "Checked against" stamp for that repo only when
     nothing else landed between the old stamp and the merge
     (`git -C repositories/<repo> log --oneline <stamp>..<merge>`); otherwise leave the stamp.
   - Neither affected → say so in the report and change nothing.
9. **Report** the new path, what you changed (including any doc sync) and which worktrees you
   removed or kept. Do not commit unless asked.
10. **Learn.** Last, run [`ws-learn`](../ws-learn/SKILL.md) § *Record*: a correction, a wrong command or doc, or a detour from this plan's life (what the plan got wrong that shipped differently) gets one line in the right project file. Nothing → skip silently.

## Archiving an intent

Intents (`intents/<code>/NNN_slug.md`, from ws-intent) number separately from plans. Asked for
"intent NNN", resolve it with `./scripts/ws find intent <id, number or slug>` like a plan (§ 1).

1. Read its `Status:` and `Plans:` lines. Plans still active (not under an `archived/` folder) →
   tell the user and get a yes first. A `draft` intent with no plans is fine to archive as
   abandoned; say so in the status.
2. `mkdir -p intents/<code>/archived`, then `git mv intents/<code>/NNN_slug.md intents/<code>/archived/`
   (plain `mv` if untracked).
3. Set `Status: archived · YYYY-MM-DD (was: <previous>)`. Change nothing else.
4. Fix links: `grep -rn "intents/<code>/NNN_slug" --include=*.md .` outside `repositories/` and
   rewrite them to `intents/<code>/archived/NNN_slug.md`.

## Notes

- IDs stay taken: `./scripts/ws next` counts archived folders and git history too.
- To restore, `git mv` it back and set the status to what it was.
- Intent numbers stay taken the same way (ws-intent § 0).
