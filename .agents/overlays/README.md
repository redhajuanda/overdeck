# Skill overlays — this project's additions to the `ws-*` skills

The `ws-*` skills in `.agents/skills/` belong to the overdeck template and are replaced by
`./scripts/ws upgrade`. Rules that only make sense for **this** project go here instead,
one file per skill: `.agents/overlays/ws-plan.md`, `ws-direct.md`, …

Each skill reads its overlay first. Overlay rules add to the skill and win where they conflict.
The `ws-learn` skill writes them; edit them by hand freely.

```md
# ws-plan — project overlay

- Every plan touching checkout names the payment provider sandbox it was checked against.
  (why: 2026-11-02, plan 014 assumed the live keys)
```

An overlay rule that every project would want → tag it `upstream` in `plans/ws-learnings.md`
(`ws-learn upstream`). Once the template ships it and `ws upgrade` brings it in, delete the rule here.
