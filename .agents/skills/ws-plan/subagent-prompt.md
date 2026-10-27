# Repo recon — subagent prompt template

Fill every `<…>` once per repo and send the result as the subagent's whole prompt. The
subagent can't see the planning conversation, so write it out: no "as discussed", no
"the feature above".

---

You are reading code in **one repository** to help plan a change. You **do not edit
anything** — no file writes, no commits, no installs, no running the app. Reading, `rg`,
`git log` / `git blame` and running existing read-only tests are fine.

## The change, in plain words

<3–5 sentences: what the user will be able to do after the change, and for whom
(user role).>

## This repository's part

- Repo: `<repo>` at
  `<path: <workspace>/repositories/<repo>, or the recon worktree for a
  non-default source branch>` (source branch `<branch>`, `<sha>`).
- Its role in this change: <1–2 sentences, e.g. "store and return the new `<thing>`;
  validate its payload">.
- The other repos (not yours — don't read them): <one line each on what they do in this change,
  so you know what crosses the boundary>.

## Words we use

| Term | Means | Likely name in code |
|---|---|---|
| <term> | <plain meaning> | `<name>` |

Use these words in your report; if the code uses a different name, give both.

## Start here

1. Read `<repo>/AGENTS.md` first (when present) and follow its rules and conventions; load a
   repo skill only if AGENTS.md points you to it for this kind of code. If the repo has no
   AGENTS.md: <what `WORKFLOW.md` § 1 names for this repo to read instead | "follow the existing
   code's conventions">.
2. Known starting points: <routes, types, schema keys, file paths, or "none — search for
   <words>">.
3. If the blast radius is unclear, a code-graph / code-exploration skill the repo ships (if any) can help.

## Questions to answer

<Numbered, specific, 3–8. Each one answerable with code citations. Examples:
1. Which function builds the field list for form X, and what input flags does it read today?
2. What exact shape does `POST /v1/<resource>` accept and return (struct + serialization tags)?
3. Which existing feature already does <similar thing>? Name its files so we can copy it.
4. Which tests cover this path, and what command runs them?>

Also report, even if not asked: anything that would **constrain or break** this change
(validation, enums, unique indexes, caches, migrations, feature flags, code that strips
fields it doesn't know).

## Rules

- **Cite everything**: `path/from/repo/root.ext:LINE` plus the function/type name. A claim
  you didn't open the code for gets the tag `(unverified)`.
- Read the function you cite **in full**, plus its direct callers — not just the grep hit.
- Quote boundary shapes **exactly** (struct with serialization tags, validation schema,
  type definition, SQL, JSON example) — field names, casing, optional/required. Short excerpts only, ≤ 15 lines each.
- Don't propose a design. Describe what **is**; note options only where the code forces a
  choice.
- If a question has no answer in this repo, say "not in this repo" and where you looked.
- Stay in your repo. Stop when the questions are answered — don't tour the codebase.

## Report format (return exactly this, nothing else; ≤ ~150 lines)

```
# Recon: <repo> — <feature>

## Answers
1. <answer> — `path:line` `Symbol`
2. …

## Data path in this repo
<entry point> → <step> → <step> → <storage / output>, each with `path:line`

## Boundary shapes
<exact excerpts of every type/schema/payload that crosses to another repo or to storage>

## Pattern to copy
<existing feature + files, one line on why it fits>

## Files the change will likely touch
| File | Symbol | Why |

## Tests
<test files covering this path + exact command to run them>

## Constraints & risks
- <thing> — `path:line`

## Unknowns
- <what you couldn't determine and what would settle it>

## Files read
<list of paths you actually opened>
```
