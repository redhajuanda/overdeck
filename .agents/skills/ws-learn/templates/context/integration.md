# <Service> — integration

Checked against: <repo>@<sha>
Docs: <vendor docs URL> · Dashboard: <URL, no credentials>

## What we use it for

<1–3 sentences. Which features depend on it.>

## How we call it

| Direction | What | Code |
|---|---|---|
| us → them | <API / SDK call> | `<repo>/<path>` |
| them → us | <webhook, event> → `<our endpoint>` | `<repo>/<path>` |

## Configuration

Env var **names** only, never values: `<VAR_NAME>` (<what it is>, set in <where>).
Sandbox vs. production: <how they differ, test credentials location by name>.

## Failure modes

- <timeout / duplicate webhook / signature failure> — <how we handle it: retry, idempotency key, alert>

## Gotchas

- <non-obvious behaviour that cost us time>
