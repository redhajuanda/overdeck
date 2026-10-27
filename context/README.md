# Context — how __PROJECT__ works, across the repos

What you can't learn by reading one repo: the shared words, who acts on the system, the rules
of the domain, how the parts connect, and why we chose what we chose. Notes **point into the
code** (paths, symbols) and never copy it. What we *want* lives in [`PRODUCT.md`](../PRODUCT.md);
material we were *given* lives in [`sources/`](../sources/README.md).

| Path | Holds | Stamped |
|---|---|---|
| [`glossary.md`](glossary.md) | Domain terms, their names in each repo, what they are *not* | no |
| [`actors.md`](actors.md) | Human roles and external systems, and what each one can do | yes |
| `domain/<concept>.md` | One core concept: states, rules, invariants, who changes it | yes |
| [`architecture/overview.md`](architecture/overview.md) | System map: apps, services, data stores, environments | yes |
| [`architecture/contracts.md`](architecture/contracts.md) | Rules every repo's boundary follows: auth, errors, IDs, time, pagination | yes |
| `architecture/<feature>.md` | One feature end to end: trigger → FE → API → BE → side effects | yes |
| `integrations/<service>.md` | One third party: what for, webhooks, env var names, failure modes | yes |
| `decisions/<prefix>-dNNN_<slug>.md` | One lasting decision (ADR); never rewritten, only superseded | no |

**Stamped** notes describe code, so they go stale. Each one carries
`Checked against: <repo>@<short sha>, …` for the commits it was verified on; `ws-archive`
moves the stamp when a shipped plan changes that area. Re-check the code before relying on
details.

**Templates** for new notes: `.agents/skills/ws-learn/templates/context/` (template-owned, so
format improvements arrive with `./scripts/ws upgrade`). **Create a note when work first needs
it** — a plan or intent that touches the concept, a lesson that has nowhere else to go — not
ahead of time. An empty note is worse than none.

**Decisions** are numbered per member like plans: `./scripts/ws next decision` → `rj-d003`,
`./scripts/ws find decision <id or slug>`. They live flat in `decisions/` (not per member), so
the whole team reads one list.

## Index

One row per note. Keep it sorted by path.

| Note | Covers | Checked against |
|---|---|---|
| [`glossary.md`](glossary.md) | Domain vocabulary | — |
| [`actors.md`](actors.md) | Roles, permissions, external systems | <!-- stamp --> |
| [`architecture/overview.md`](architecture/overview.md) | System map | <!-- stamp --> |
| [`architecture/contracts.md`](architecture/contracts.md) | Cross-repo boundary rules | <!-- stamp --> |

## Decisions

| ID | Decision | Status |
|---|---|---|
