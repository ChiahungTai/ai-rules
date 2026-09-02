---
meta:
  title: Configuration and context
  description: Configure Muse Code with the settings file, project instruction files, model and reasoning-effort selection, launch flags, and durable project memory.
  keywords: configuration, settings, schema_version, AGENTS.md, muse init, model, reasoning effort, flags, memory, context
cms:
  alias: /model-api/docs/muse-code/configuration
  target: aidmc
---

# Configuration and context

Set Muse Code up once for your machine and once per project, and give the agent the durable project knowledge it needs. This way, you don't repeat yourself every session. User settings live in a JSON file. Project instructions and memory travel with the repository.

## The settings file {#settings-file}

User settings live at `~/.config/muse/settings.json`. The file holds:

- model defaults
- terminal-UI preferences, including [voice](/docs/muse-code/interactive#voice) and [reasoning display](/docs/muse-code/interactive#reasoning)
- tool configuration, including [workflow selection](/docs/muse-code/workflows#configure) and [session messaging](/docs/muse-code/session-messaging#configure)
- [MCP servers](/docs/muse-code/extending#mcp)
- a first-class `hooks` block, plus a `managed_hooks_path` pointer (see [hooks](/docs/muse-code/extending#hooks))
- a `runtime_capabilities` map that toggles capabilities such as the [observer agents](/docs/muse-code/extending#observer-agents)
- telemetry options

> [!IMPORTANT] schema_version must be 1
> `settings.json` must set `"schema_version": 1`. A file that omits that key fails every command at startup with `malformed settings file`. An unrecognized value fails with `unsupported settings schema version`. A **missing** file is fine, because Muse Code applies defaults. Create the file only when you have something to set, and always include `"schema_version": 1`.

## Project instructions with AGENTS.md {#agents-md}

`muse init` seeds your project's agent rules. It writes a single `AGENTS.md` into the current directory. It creates no other files, and does **not** change `settings.json`:

```bash
muse init            # write AGENTS.md in the current directory
muse init --dry-run  # show what it would write, change nothing
```

Without `--force`, it stops if `AGENTS.md` already exists. With `--force`, it overwrites the file completely, so save any existing content first.

**How Muse Code loads instruction files.** From your workspace root, Muse Code walks up to the nearest `.git` boundary. At each directory level, it checks `AGENTS.md`, `CLAUDE.md`, `.agents/AGENTS.md`, then `.claude/CLAUDE.md`; the first existing file in that order wins for that level. Precedence when guidance conflicts:

- **Project rules win over user rules.**
- Among project files, the **deeper file wins** over a shallower one.

Your machine-wide user rules always load. **Project rules load only after you [trust the workspace](/docs/muse-code/permissions#trust-scopes).** On an untrusted checkout, Muse Code ignores project `AGENTS.md` and `CLAUDE.md` until you trust it.

> [!NOTE] Conservative by default
> Muse Code is designed to follow these files, but it stays conservative about your repository by default: it won't commit, amend, or push your work unless you ask it to in the session, it keeps scratch files outside your checkout, and it reverts incidental edits it didn't need. The end of a task is not a request to commit.

## Select a model {#model}

The default model is `muse-spark-1.2`. Override it per run with `--model`, or switch mid-session with the `/models` slash command:

```bash
muse --model muse-spark-1.2
```

## Set reasoning effort {#reasoning-effort}

`--reasoning-effort` trades latency for depth: `none`, `minimal`, `low`, `medium`, `high` (default), `xhigh`, `ultra`. Change it mid-session with `/effort`.

```bash
muse --reasoning-effort medium
```

> [!NOTE] Premium reasoning tiers
> `xhigh` is an optional premium-precision tier. `ultra` is a client-side setting that maps to each provider's highest supported reasoning tier and can make Muse Code delegate more aggressively. The Meta provider does not accept `none`; other providers can support it.

## Launch flags {#flags}

Muse Code has two launch surfaces with **separate** flag sets: the interactive TUI (`muse …`) and headless (`muse exec …`). Some flags exist on only one.

Common to both:

- **`--model <id>`**, **`--reasoning-effort <level>`**: model and reasoning depth.
- **`--sandbox-network <mode>`**, **`--disable-sandbox`**, **`--disable-approval`**, **`--yolo`**, **`--trust-workspace`**: [permissions and sandbox](/docs/muse-code/permissions).
- **`--approval-mode <mode>`**, **`--approval-judge <on|off>`**: tune [approvals](/docs/muse-code/permissions#approval-modes).
- **`--subagent-worktree-isolation`**: compatibility flag. Isolation is requested per [subagent](/docs/muse-code/extending#multi-agent); the flag does not isolate every child.
- **`--workspace <path>`**: root policy-gated workspace tools at a path.
- **`--no-session-log`**: don't retain the [session](/docs/muse-code/interactive#session-model) event log.

Headless only (`muse exec …`):

- **`--json`** (emit JSONL events), **`--prompt-file <path>`** (read the prompt from a file), **`--max-model-steps <n>`** (cap the run).

`muse exec` accepts both approval flags. They configure the policy before the run starts. A headless run has no interactive UI for answering a human approval prompt, so choose a policy that can complete unattended or expect the held action to remain unresolved.

Both `muse --no-session-log` and `muse exec --no-session-log` run without retained session state. This disables resume, trajectory export and reattach, automatic retained-session naming and peer messaging, and retained workflow recovery. Generated inline workflow scripts use process-lifetime temporary storage when no retained workflow session directory is available.

## Local memory {#local-memory}

Memory is Markdown you keep for the agent, so it recalls durable facts on its own. There are three scopes:

- **Personal project memory** (the default): stored on your machine outside the repo, private to you, scoped to this project.
- **Project memory**: committed to the repo under `<repo>/.agents/memory/`, shared with everyone who clones it.
- **Personal memory**: your machine-wide notes, across all projects.

Keep an index in `MEMORY.md` and one Markdown file per topic:

```
.agents/memory/
├── MEMORY.md        # index: one line per topic file
└── deploy.md        # a durable note the agent should know
```

Put durable, project-specific facts here: deployment procedures, the reason a workaround exists, a service's unusual behavior. Facts the agent could get wrong from general knowledge alone are the ones worth recording.

> [!NOTE] Memory loads in untrusted workspaces
> Muse Code reads committed project memory into the model's context even in an **untrusted** workspace. Skills, rules, and hooks differ: they load only after you trust it. Treat a repo's `MEMORY.md` as a prompt-injection surface, and review it on checkouts you don't control.

## How the agent recalls memory {#recall}

At the start of a session, Muse Code injects an *index* of your memory: `MEMORY.md` plus a list of the other Markdown files (their paths, not their contents), up to 48 files. The agent reads individual files on demand, and a [background observer](/docs/muse-code/extending#observer-agents) can insert a relevant note into a turn before the agent answers.

## Next steps

- Save repeatable multi-agent orchestration as [workflows](/docs/muse-code/workflows#save).
- Package reusable instructions and tools as [skills](/docs/muse-code/extending#skills) the agent can load on demand.
- Lock down what the agent can do in [permissions and safety](/docs/muse-code/permissions).
