# Cross-repo contracts — __PROJECT__

Checked against: <repo>@<sha>, <repo>@<sha>

Rules every boundary between the repos follows, so plans don't restate them and
implementers don't guess. A plan's own *Contracts* section covers only what is **new** in that
change and must not contradict this file; `ws-implement` checks both.

| Topic | Rule | Defined in |
|---|---|---|
| Auth | <how the FE authenticates calls; token location, refresh> | `<repo>/<path>` |
| Errors | <error response shape; how the FE shows it> | |
| IDs | <format: UUID, int, prefixed string> | |
| Time | <UTC ISO 8601 on the wire; who converts to local time> | |
| Money | <integer minor units + currency, or decimal string> | |
| Pagination | <cursor or page/size; response envelope> | |
| Naming | <JSON field casing; enum casing> | |
| Versioning | <how breaking API changes ship> | |
