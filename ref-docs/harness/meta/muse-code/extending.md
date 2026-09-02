---
meta:
  title: Extending and automating
  description: Scale Muse Code beyond a single interactive session — parallel subagents, reusable skills, lifecycle hooks, MCP servers, and headless runs for CI.
  keywords: multi-agent, subagents, worktree isolation, skills, hooks, MCP, headless, CI, muse exec
cms:
  alias: /model-api/docs/muse-code/extending
  target: aidmc
---

# Extending and automating

Take Muse Code past a single interactive session: distribute work across parallel agents, package reusable workflows as skills, wire your own commands into the lifecycle with hooks, connect external tools through MCP, and run the agent non-interactively in CI.

For structured orchestration with parallel groups, dependent stages, monitoring, and reusable JavaScript definitions, see [workflows](/docs/muse-code/workflows). To coordinate independent live sessions, use [session messaging](/docs/muse-code/session-messaging).

## Subagents and multi-agent {#multi-agent}

Distribute a large job across a team of agents that work in parallel, and steer them from one place. A lead session spawns child agents, hands each a bounded task, and keeps managing the group while they run.

A **subagent** is a child agent that the lead spawns for one bounded task. Children share the lead's checkout unless the lead requests worktree isolation for that child. Ask for isolated worktrees when parallel children may write, and keep read-only children in the shared checkout.

An isolated child gets a Muse Code-managed Git worktree. The request can be rejected when the current profile, workspace, provider, or Git state cannot support isolation. It never silently falls back to the shared checkout.

The `--subagent-worktree-isolation` launch flag remains accepted for compatibility. It does not force every child into a worktree; isolation is still selected per child.

Use subagents when a job splits into tasks that are each bounded, independently verifiable, and would otherwise contend for the same files. Keep the work on one agent when the steps are strictly sequential.

**Steer the agents.** Run `/subagents` to view running and past subagents. Run `/tasks` to manage direct subagent tasks and use the actions available for the selected row. The lead also manages children through its native subagent tools.

A few properties worth knowing:

- One agent tree can execute eight agents at once by default, including the root agent. Set `agents.execution_capacity` from 1 through 64 in `settings.json` to change the limit. An unconfigured `ultra` root uses 64.
- A spawn attempted when the tree is full is rejected. An accepted child can still wait for a host scheduler slot before it starts.
- Children can spawn grandchildren. Every descendant shares the same root-tree capacity.
- Cancellation is cooperative: a cancelled child that never reaches a checkpoint keeps running, and one mid-write finishes that write.
- The runtime journals every spawn, status change, and control action, so you can answer "which child did what, and when" after the run. A child commits changes only when its task explicitly asks it to.

### Background observer agents {#observer-agents}

Alongside the main session, Muse Code runs a team of background observer agents. Each one watches a single axis of quality, and can insert a short advisory into the main agent's next turn without an interruption. An observer never answers for you: it proposes, a reconciler decides, and only an accepted proposal reaches the main agent.

- **Memory recall**: surface a note from local project [memory](/docs/muse-code/configuration#local-memory) relevant to the next reply.
- **Skill recall**: surface a project [skill](#skills) the task should load first.
- **Goal tracking**: hold the agent to a declared [goal](/docs/muse-code/interactive#goals-loops) and decline to close the turn until the work is done.
- **Verification**: check that the agent ran the work it claims it finished.

All four observers, including verification, are on by default. Rollout gates and your [settings file](/docs/muse-code/configuration#settings-file) can still disable them.

> [!NOTE] Observers add token usage
> Each enabled observer makes its own model calls, so the default set of four adds token usage in addition to the main session.

## Skills {#skills}

A skill packages a repeatable workflow the agent can load on demand: a set of instructions, and optionally tools and files, that turn "explain how we do X" into a single invocation. Muse Code ships built-in skills, and you can add your own or import them from other agents.

Skills load from four sources:

- **Built-in**: skills that ship with Muse Code.
- **User**: your account-wide skills in `$XDG_CONFIG_HOME/muse/skills` and `~/.agents/skills`, available in every project. Muse Code also discovers `~/.claude/skills` and `$CODEX_HOME/skills` by default, falling back to `~/.codex/skills` when `CODEX_HOME` is unset. A user preference and rollout gate can disable these foreign personal skill roots.
- **Project**: skills committed to a repo under `<repo>/.agents/skills/<skill-id>/SKILL.md`, shared with anyone who clones it. Muse Code also scans repo-local `.codex/skills` and `.claude/skills`.
- **Plugin**: skills contributed by enabled plugin bundles.

Manage and invoke skills:

```bash
muse skills list                    # every skill, all sources
muse skills inspect <skill-id>
muse skills enable <skill-id> --scope project
muse skills install ./my-skill --scope user
muse skills validate ./my-skill     # check it before installing
muse skills import --from claude    # or: --from codex
```

In an interactive session, invoke a skill with its slash shortcut. Built-in skills include `/plan` (turn a task into a grounded, decision-complete plan, then stop for approval), `/grill` (stress-test a plan or design before you build), and `/taste` (a design-quality gate for frontend work). The related `/grill-and-record` skill also records the settled decisions in your project docs. The agent can also load a relevant skill when a [background observer](#observer-agents) surfaces one.

## Hooks {#hooks}

Wire your own shell commands into Muse Code's lifecycle. A hook binds a shell command to a lifecycle event. When the event fires, Muse Code runs the command and acts on its result: enforce a check, format code, or block an action before it happens, without a change to the agent itself.

Hooks come from three sources:

- **Project**: committed to the repo at `<project-root>/.muse/hooks.json`.
- **User**: your machine-wide hooks, defined in your [settings](/docs/muse-code/configuration#settings-file).
- **Managed**: a file that the `managed_hooks_path` setting points to, for centrally administered hooks.

Project hooks run only after you trust the project folder. User hooks run from your own settings without a separate hook-level trust step. Managed hooks also run without a project-trust step, so whoever controls the managed hooks file controls what executes.

> [!WARNING] Hooks run outside the sandbox
> Only add hooks whose commands you've read. A hook's command runs directly through your shell, **outside** the [sandbox and approval](/docs/muse-code/permissions) that govern the agent's own tools. The only hardening is a cleared environment with a small allowlist.

### Lifecycle events {#hook-events}

A hook binds to exactly one event. The available events are `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreLLMCall`, `PostLLMCall`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `Stop`, and `SessionEnd`. `SessionEnd` runs during orderly session termination. It is observational: its output cannot block termination, inject context for a later request, or stop the session.

Muse Code discovers and validates hooks at session startup. A malformed project or managed hook file contributes no handlers from that source and produces a startup warning. A malformed user settings file fails settings validation. Unsupported events, matchers, or handlers skip the affected entry and produce a source-specific warning.

There is no active `muse hooks` command family or per-hook trust command. Fix the reported configuration and start a new session to reload it.

## MCP servers {#mcp}

Connect external tools through the Model Context Protocol (MCP). Declare servers in the `mcp_servers` block of your [settings file](/docs/muse-code/configuration#settings-file). Each server takes a `transport`: either `stdio` (with `command`, `args`, and `env`) or `streamable_http` (with `url` and `headers`). Every server also takes `enabled` and `mode`. For `stdio`, the optional `framing` setting controls message framing. A non-default `framing` value on `streamable_http` fails validation.

```json
{ "mcp_servers": {
    "my-tools": { "transport": "stdio", "command": "my-mcp-server", "args": [] }
} }
```

A server's `mode` defaults to `required`. If a required server fails to start, the whole run aborts. Set `mode` to `optional` for a server that Muse Code should skip with a warning when it's unavailable.

> [!WARNING] MCP tools aren't sandboxed
> Only connect servers you trust. **MCP tools are not sandboxed.** Unlike shell commands, an MCP server runs as an ordinary child process (stdio) or a direct network connection, outside the filesystem and network [sandbox](/docs/muse-code/permissions#sandbox). Approval still applies, but containment does not.

## Headless and CI {#headless}

Run Muse Code without a terminal UI. `muse exec` takes one prompt, runs it to completion, and exits, so you can drive the agent from a script, a job, or a CI pipeline:

```bash
muse exec "Update the changelog for the latest release and run the tests."
muse exec --prompt-file ./task.txt
muse exec --json "Refactor the auth module and run the tests."   # JSONL events on stdout
```

`muse exec` prints the agent's output to stdout and returns a process exit code. The code reflects **how the run ended, not whether the work is correct**: `0` when the turn completes, `1` when it fails or is cancelled (including a `--max-model-steps` limit), `2` for a usage error, and `130` or `143` on SIGINT or SIGTERM. An agent can finish its turn and still report that the tests fail, and it exits `0`. So gate on your own test command, not on Muse Code's exit code alone.

**Control approvals for automation.** A non-interactive run has no one to answer an approval prompt, so choose a posture in advance:

- **`--disable-approval`**: skip approval prompts, but keep the [sandbox](/docs/muse-code/permissions#sandbox) on to contain what runs.
- **`--yolo`**: disable approval and the sandbox for a fully unattended run. It **also trusts the workspace**, and loads the checkout's `AGENTS.md`, rules, and skills. On a fork or pull-request checkout, those are attacker-controlled, so use `--yolo` only on trusted code in a disposable, isolated container.

Cap a run's work with `--max-model-steps` so a stuck task can't loop indefinitely.

> [!NOTE] CI sandbox requirements
> The sandbox in CI requires the OS sandbox to work on the runner. On Linux, that means a working bubblewrap and a non-musl build, because musl artifacts ship without the sandbox helper. On a host without it, every sandboxed shell command aborts as an environment failure. See [permissions](/docs/muse-code/permissions#sandbox).

**Resume and audit non-interactively.** Headless runs are [sessions](/docs/muse-code/interactive#session-model) like any other. To continue an interrupted job non-interactively, use `exec` with the session id. `muse resume` opens the interactive UI and is not a headless surface:

```bash
muse exec --session-id <uuid> "Continue the task."
muse export --session <uuid> --out run.json
```

Muse Code refuses a workspace mismatch unless you pass `--allow-workspace-switch`. The export document embeds the CLI version that produced it, so pin the version if you gate on its hash.

## Next steps

- Keep the whole team inside the same [permissions and sandbox boundary](/docs/muse-code/permissions).
- Build repeatable multi-agent runs with [workflows](/docs/muse-code/workflows).
- Give skills and subagents the project facts they rely on in [configuration and context](/docs/muse-code/configuration).
- Connect external agent tooling to the model from the [coding agents](/docs/coding-agents) guide.
