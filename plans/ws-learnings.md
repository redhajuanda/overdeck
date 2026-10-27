# ws learnings

One line per lesson, written by the `ws-learn` skill (`.agents/skills/ws-learn/`) and by
ws-implement retros (`retro.md`). A proposed lesson seen from 2+ sources is a pattern → `recommended`;
an applied one seen again is `recurred`.
Applied/rejected lines stay, so nothing is proposed twice.

`- YYYY-MM-DD · <source> · <lesson> · → <target file> · status: <status> [· axis: <axis>] [· upstream]`

- **source** — where it was seen, comma-separated when seen again: a plan ID (`rj-042`),
  `multi rj-042+rj-043`, `direct`, `explore`, `plan`, `intent`, `archive`, `user`.
- **status** — `proposed` · `recommended` (proposed, 2+ sources) · `applied <date>` ·
  `recurred <date>` (applied, then the same mistake happened again: the rule failed — fix
  where it lives, don't just count) · `rejected` (+ reason) · `upstream PR <url>` · `upstreamed`.
- **axis** — retros only: `effective`, `solutive`, `fast`, `cheap`, `multi`.
- `· upstream` = every project would want it: it goes to the overdeck template as a PR
  (`ws-learn` § *Upstream*), never into the local copy of a skill.

Open lines (`proposed`, `recommended`, `recurred`) are counted by `./scripts/ws doctor`.

