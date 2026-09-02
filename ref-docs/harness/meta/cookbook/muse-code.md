---
meta:
  title: Building with Muse Code — Meta Model API cookbook
  description: Cookbook recipes for building durable agents with Muse Code — audit and resume, deterministic replay, staged approvals, sandboxing, immutable guardrails, subagent fanout, goals, bundled skills, scheduling, and side chats.
  keywords: cookbook, Muse Code, agents, audit log, approvals, sandbox, subagents, guardrails, scheduling, Muse Spark
cms:
  layout: large
  in_page_nav: false
  alias: /model-api/docs/cookbook/muse-code
  target: aidmc
---

# Building with Muse Code

Build durable, auditable agents with Muse Code — the harness building blocks for safety, recovery, and orchestration. Part of the [Cookbook](/docs/cookbook).

<tile-group col="3">
<tile color="purple" icon="robot-head" href="/docs/cookbook/audit-agent-sessions" title="Audit and resume agent sessions"> Replay any session exactly as it ran from an append-only event log, show who authorized each action, then kill the run mid-task and resume with no duplicate side effects.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/deterministic-replay" title="Deterministic replay in CI"> Turn recorded events into a golden fixture and replay its model-context projection as a merge-blocking CI check.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/staged-approvals" title="Staged approvals"> Split a compound shell command into stages so safe ones auto-resolve while risky ones hold for review.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/contained-execution" title="Contained execution"> Run every command in an OS sandbox that refuses to proceed unless containment is proven live.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/immutable-guardrails" title="Immutable guardrails"> The agent can't rewrite its own rules: guardrail edits stop for review and a shell write to the same path fails read-only at the sandbox.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/subagent-fanout" title="Subagent fanout"> Fan one job out to parallel subagents, each in its own isolated git worktree.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/goal-tracking" title="Goal tracking"> Pin an objective once and the harness audits the work against acceptance checks before the goal can close.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/bundled-skills" title="Bundled skills"> Drive the built-in /plan, /grilling, /grill-with-docs, and /taste skills to plan, pressure-test, and build.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/loop-and-cron" title="Loop and cron"> Schedule recurring or one-time agent work in natural language, then view, change, or cancel it from the same chat.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/side-chats" title="Side chats"> Branch off the main thread for a side conversation that never enters the main history.</tile>
</tile-group>
