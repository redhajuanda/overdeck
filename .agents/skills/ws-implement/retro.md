# ws-implement retrospective

Runs once after a plan is implemented, triggered by the Stop hook
(`.claude/hooks/ws-implement-retro.py`). Goal: make the **next** run more **effective**
(right thing built), **solutive** (problems solved, not bounced), **fast** (wall clock) and
**cheap** (tokens). Done by the main session from what it already knows — no subagents, no
re-reading code. ≤ 10 minutes.

## Inputs

- `plans/NNN_slug/run-metrics.md` — minutes, turns, tool calls and tokens per agent
  (written by the hook from the transcripts; Codex runs are missing — add them by hand).
- What you saw in this session: § 5 contract checks, review findings, fix round, deviations,
  waits, re-dispatches, questions you had to ask.
- `plans/NNN_slug/plan.md` — ticks, *Decisions* added during the run.
- `plans/ws-learnings.md` — what earlier retros found.

## 1. Find the waste — with evidence only

Answer each in one line, citing a number from the metrics or a concrete event. "Nothing" is a
fine answer; don't invent problems.

| Axis | Ask |
|---|---|
| Effective | Did review find bugs the implementer should have caught? A contract mismatch in § 5? Was a plan task unclear or wrong (→ ws-plan problem, not ws-implement)? |
| Solutive | Anything sent back more than once, blocked, or left for the user? Why — brief, plan, or tooling? |
| Fast | Longest agent vs. the rest — was it on the critical path? Any wave that waited without importing real code? Time lost to installs, flaky tests, permission prompts? |
| Cheap | Main session share of fresh-input tokens (target: < ~40 %). Any agent with many turns for few tasks (orienting, re-reading, running full suites)? Was the review tier right for the diff size? |

## 2. Turn waste into changes

For each real finding, propose **one** concrete change, in the most specific place:

| Cause | Change goes to |
|---|---|
| The brief left the agent guessing | `subagent-prompt.md` / `review-prompt.md` |
| The orchestration (waves, review tier, thresholds, fix round) | `SKILL.md` |
| Model / effort / parallelism | `agents.yaml` |
| The plan was unclear or wrong | `ws-plan` skill |
| A repo convention the agent missed | that repo's AGENTS.md (suggest only — it's the repo's file) |
| A project-specific learning (stack command, path, tool, product term) | `WORKFLOW.md` or that repo's AGENTS.md (suggest only) — never a skill |

A change must be small (a sentence, a threshold, a line in a template), and say which number
or event it should move next time. Prefer deleting or tightening a rule to adding one.

**Quality bar — propose a change only if ALL of these hold:**
- (a) It rests on **evidence from this run**: a number from `run-metrics.md` or a concrete
  event. No hunches.
- (b) It is **general**: it fits a workflow skill for any project. A project-specific learning
  goes to `WORKFLOW.md` or the repo's AGENTS.md (suggest only), never into a skill.
- (c) It would plausibly **move a named number or prevent a named event** next time.
- (d) It isn't already covered by an existing rule or a `plans/ws-learnings.md` line. If it
  is, add the plan number to that line instead of proposing it again.

If nothing passes, propose nothing: write "No changes proposed" under *Proposed changes* in
`retro.md`, skip § 4's question to the user entirely, and still write the retro file and
`retro=done`.

## 3. Write it down

1. `plans/NNN_slug/retro.md`, ≤ 40 lines:
   ```
   # Retro — NNN <title>
   Run: <wall-clock> min · <subagents> agents · <fresh-input total> fresh input · main <share>%
   ## What worked        (≤ 3 bullets)
   ## Waste              (axis — evidence — cause)
   ## Proposed changes   (file — change — expected effect; or "No changes proposed")
   ```
2. Append one line per proposed change (only those that passed the § 2 bar) to `plans/ws-learnings.md`:
   `- YYYY-MM-DD · NNN · <axis> · <change> · status: proposed`.
   If the same learning already exists there, add the plan number to it instead of a new line.
   **A learning seen in 2+ runs is a pattern** — mark it `recommended`.

## 4. Ask, then apply

If no change passed the § 2 bar, skip the question; go straight to the last paragraph below.
Otherwise show the user only the changes that passed the bar (AskUserQuestion, multiSelect,
`recommended` ones first, ≤ 4 per question). Apply only the chosen ones, then update their
`plans/ws-learnings.md` line to
`status: applied <date>` (or `rejected`, with the user's reason if given — so it isn't
proposed again). Proposals the user doesn't pick stay `proposed`; one that shows up again in a later run becomes `recommended`.

Finally, append `retro=done <ISO>` to `plans/NNN_slug/.ws-implement.run`.
