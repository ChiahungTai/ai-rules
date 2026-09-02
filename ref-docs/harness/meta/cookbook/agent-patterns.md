---
meta:
  title: Agent patterns — Meta Model API cookbook
  description: Cookbook recipes for turning Muse Spark into an agent — the core loop, interleaved reasoning and tool use, context management, and validated edits.
  keywords: cookbook, agent patterns, agent loop, tool use, context management, Muse Spark
cms:
  layout: large
  in_page_nav: false
  alias: /model-api/docs/cookbook/agent-patterns
  target: aidmc
---

# Agent patterns

Turn a model into an agent. These loops handle planning, self-correction, and staying coherent across long runs. Part of the [Cookbook](/docs/cookbook).

<tile-group col="3">
<tile color="purple" icon="robot-head" href="/docs/cookbook/basic-agent-loop" title="Basic agent loop"> Wire up the core perceive-decide-act loop.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/interleaved-reasoning-tool-use" title="Interleaved reasoning and tool use"> Interleave reasoning with tool calls in a single turn.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/multi-turn-context-management" title="Multi-turn context management"> Keep context under control across a long agent run.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/search-and-replace-edits" title="Search-and-replace edits"> Make exact-match file edits that stay reviewable.</tile>
<tile color="purple" icon="robot-head" href="/docs/cookbook/alert-fatigue-copilot" title="Alert fatigue copilot"> Pull grounded patterns from noisy alerts, then probe, chat, and self-assess with strict JSON.</tile>
</tile-group>
