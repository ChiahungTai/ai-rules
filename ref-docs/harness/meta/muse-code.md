---
meta:
  title: Muse Code
  description: Muse Code is Meta's coding agent for the terminal and CI, built on Muse Spark, with approvals, sandboxing, sessions, and multi-agent orchestration.
  keywords: Muse Code, coding agent, CLI, terminal, Muse Spark, agent harness
cms:
  alias: /model-api/docs/muse-code
  target: aidmc
---

# Muse Code

Muse Code is Meta's coding agent for the terminal and CI, built on [Muse Spark](/docs/models). Run it in a project and it plans, edits, and runs commands to do a task, with approvals and an OS sandbox on from the first run.

Muse Code and the [Model API](/docs/overview) are two ways to use the same model. Call the API directly when you build your own agent or app. Run Muse Code when you want a ready-made coding agent at the command line or in a pipeline.

[Workflows](/docs/muse-code/workflows) coordinate parallel and staged agent work when the installed build includes the workflow engine and the rollout is enabled. They are not available on every build or platform. [Session messaging](/docs/muse-code/session-messaging) lets independent live sessions exchange handoffs, review requests, and status updates.

## Install {#install}

Install Muse Code with the one-line shell installer. It installs a native binary on your path for macOS and Linux:

```bash
curl -fsSL https://dev.meta.ai/install.sh | sh
```

Confirm it's on your path:

```bash
muse --version
```

## First run {#first-run}

Run `muse` in any project directory to start an interactive session. On first entry Muse Code asks whether to [trust the workspace](/docs/muse-code/permissions#trust-scopes) and prompts you to authenticate with a browser sign-in or an API key. When you trust the workspace, Muse Code loads the project's skills, rules, and hooks. The default model is `muse-spark-1.2`.

```bash
cd /path/to/your/project
muse
```

Reopen the sign-in options any time from an interactive session with `/login`. For a non-interactive environment such as [CI](/docs/muse-code/extending#headless), set `META_API_KEY` instead. See [authentication and billing](/docs/muse-code/auth) for the full sign-in and billing setup flows.

## Interactive or headless {#modes}

The same binary runs two ways:

- **Interactive**: `muse` opens a terminal UI for a back-and-forth session with slash commands, approvals, and live status. See [working with the agent](/docs/muse-code/interactive).
- **Headless**: `muse exec "<prompt>"` runs one prompt to completion for scripts and CI. See [headless and CI](/docs/muse-code/extending#headless).

## What to read next {#whats-here}

- **[Authentication and billing](/docs/muse-code/auth)**: sign in, API keys, and plans.
- **[Permissions and safety](/docs/muse-code/permissions)**: approval modes, staged shell review, and the sandbox.
- **[Working with the agent](/docs/muse-code/interactive)**: slash commands to steer a session, manage context, set goals, and more.
- **[Rewind a conversation](/docs/muse-code/rewind)**: branch from an earlier message while preserving the original session and workspace files.
- **[Workflows](/docs/muse-code/workflows)**: check availability, coordinate parallel and staged agent work, monitor runs, and save repeatable workflows.
- **[Session messaging](/docs/muse-code/session-messaging)**: send handoffs, review requests, and status updates between live local sessions.
- **[Configuration and context](/docs/muse-code/configuration)**: settings, project instructions, model selection, and memory.
- **[Extending and automating](/docs/muse-code/extending)**: subagents, skills, hooks, MCP, and headless runs.

## Next steps

- Sign in and set up billing in [authentication and billing](/docs/muse-code/auth).
- Understand the guardrails before your first real task in [permissions and safety](/docs/muse-code/permissions).
