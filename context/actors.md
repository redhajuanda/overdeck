# Actors — __PROJECT__

Checked against: <repo>@<sha>, <repo>@<sha>

Everyone and everything that acts on the system. Who they *are* and what they *want* is in
[`PRODUCT.md`](../PRODUCT.md) § Users; this file is what they **can do** and where that is
enforced.

## Human roles

| Role | Surface | How they sign in | Can | Cannot | Enforced in |
|---|---|---|---|---|---|
| **<role>** | <app / page> | <auth method> | <actions> | <notable denials> | `<repo>/<path>` `<guard>` |

## Systems

External services, schedulers, scripts and other non-human callers.

| Actor | Kind | Calls / is called by | With what credential | Note |
|---|---|---|---|---|
| **<service>** | <third party · cron · worker · admin script> | <direction, endpoint or queue> | <env var name, never the value> | [`integrations/<service>.md`](integrations/) |

## Permission matrix

Only when roles × actions is too dense for the table above.

| Action | <role> | <role> |
|---|---|---|
| <action> | ✓ | — |
