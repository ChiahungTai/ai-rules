---
meta:
  title: Permissions and safety
  description: Control what Muse Code can do with approval modes, stage-by-stage shell-command review, scoped trust, and an OS-enforced sandbox.
  keywords: permissions, approvals, sandbox, safety, trust, staged approvals
cms:
  alias: /model-api/docs/muse-code/permissions
  target: aidmc
---

# Permissions and safety

Grant Muse Code only the access you intend. Approval and sandboxing are on by default. The agent asks before any risky action, and every shell command runs inside an OS-enforced sandbox.

> [!NOTE] Guardrails are on by default
> Both guardrails are on unless you opt out. `muse --yolo` turns off approval and the sandbox, and instructs the harness to trust the workspace for the run. Use it only in an already-isolated environment such as a disposable CI container.

## Two layers of control {#how-it-works}

Muse Code controls side effects at two independent layers:

- **Approval**: before a tool call with side effects runs, the agent checks it against the approval policy. Safe actions pass automatically. Risky actions cause the harness to stop for your decision.
- **Sandbox**: shell commands run inside an OS-level sandbox. The sandbox limits filesystem writes and network access, and refuses to run if it cannot enforce that boundary.

Each layer works on its own. If you disable one layer, the other stays in place.

[Workflow](/docs/muse-code/workflows) child agents inherit the lead session's effective tools and permission boundary. A child can narrow that toolset through its agent definition, but it cannot expand it.

## Choose an approval mode {#approval-modes}

Set the mode at launch with `--approval-mode`:

- **`on-request`** (default): recognized, non-dangerous parsed shell stages normally pass without a prompt, and the [sandbox](#sandbox) contains them. Dangerous or external-execution patterns stop for review. These include destructive removal forms and ripgrep options that can launch helper processes, such as `-z`, `--search-zip`, `--pre`, and `--hostname-bin`. Muse Code also checks wrappers around the command they launch.
- **`untrusted`**: this mode is stricter. A shell stage with no matching allow rule stops for review, not only the dangerous ones. It escalates shell execution only. File reads and in-workspace `write_file` and `edit_file` writes still pass in any mode.
- **`never`**: nothing stops for approval. The sandbox alone contains what runs.

```bash
muse --approval-mode untrusted
```

A built-in judge reviews prompt-bound calls automatically. Turn it off to send every review decision to you:

```bash
muse --approval-judge off
```

## Review shell commands stage by stage {#staged-approvals}

Muse Code reviews a compound shell command one stage at a time, not as a single line. It parses the command into ordered stages, checks each one against policy, and blocks on the first stage it cannot approve.

Take this command:

```bash
wc -l report.log && echo cleaning && rm -rf report.log
```

`wc -l report.log` and `echo cleaning` are read-only, so they pass automatically. Muse Code classifies `rm -rf report.log` as dangerous, so it holds for review at stage 3 of 3. The command runs as one unit only after every stage passes. If you reject the held stage, nothing runs, not even the safe stages before it.

The mode decides how Muse Code treats commands and stages that have no matching rule. In `untrusted` mode, every unmatched shell stage stops for review. In `on-request` mode, recognized non-dangerous stages normally pass, while dangerous or external-execution patterns stop. A command that the parser cannot safely decompose, such as shell grouping or control flow that produces no reviewable stages, can also stop for review. To make every unmatched parsed stage stop, run in `untrusted` mode.

## Grant trust at the right scope {#trust-scopes}

When a stage holds, you choose how much trust to grant:

- **Allow once**: run this stage one time only. Muse Code saves nothing.
- **Always allow in this workspace**: save a rule for this command's prefix, scoped to this workspace root. The rule does not apply to other projects, and it does not cover a different command.
- **Reject**: deny the whole command.

Prefix rules apply by specificity. A deny rule always overrides an allow rule, whatever the specificity. You cannot save an interpreter prefix such as `python`, `bash`, or `node` as a broad allow, because everything after the interpreter is arbitrary code.

The first time you open a workspace, Muse Code asks whether to trust it. When you trust a workspace, Muse Code loads its project-local skills, rules, and hooks. Muse Code remembers this trust for each workspace root.

[Session messaging](/docs/muse-code/session-messaging) has a separate peer-admission boundary. Exact-profile peers can be admitted automatically; unverified or non-matching senders may trigger a prompt. A message from another session cannot approve tools, grant consent, or change this session's permissions.

## Run inside the sandbox {#sandbox}

Shell commands run inside a filesystem and network policy that the operating system enforces. On macOS the policy uses Seatbelt. On Linux it uses a bundled bubblewrap helper. The policy grants write access to the workspace and a temp directory, and keeps the rest of the filesystem read-only. Inside the writable workspace, the `.git`, `.muse`, and `.agents` directories stay read-only, so the agent can't rewrite its own history, configuration, or memory.

Muse Code refuses to run a shell command when it can't confirm that the sandbox is active. On Linux, Muse Code checks the sandbox helper first. A host without a working bubblewrap fails every shell command as an environment error, as does a musl build that ships without the helper. On macOS, Muse Code verifies Seatbelt once, at session startup.

A write outside the allowed roots fails at the OS level:

```
$ echo data > $HOME/notes.txt
/bin/bash: line 1: /home/you/notes.txt: Read-only file system
```

Control network access with `--sandbox-network`:

- **`proxy-only`** (default): Muse Code approves outbound connections per destination. The first connection to a new host, port, or protocol stops for review, like a shell command.
- **`restricted`**: no network access.
- **`enabled`**: full network access.

## How the layers combine {#defense-in-depth}

The two layers are independent. Approval decides *whether* a command may run. The sandbox limits *what* it can access when it runs. In the default modes, a shell command passes both layers. The optional [approval judge](#approval-modes) is part of the approval layer, not a separate layer. When the judge is on, it reviews prompt-bound calls automatically instead of stopping for you.

## Run without guardrails {#run-without-guardrails}

For a run inside an already-isolated environment, you can lower or remove the guardrails:

- **`--yolo`**: disable approval and the sandbox, and trust the workspace, for this run.
- **`--disable-approval`**: keep the sandbox, but skip approval prompts.
- **`--disable-sandbox`**: keep approval, but skip the sandbox. This flag also removes workspace confinement from the file tools, so `write_file` and `edit_file` can write anywhere on the filesystem. It also forces the network to full egress and overrides `--sandbox-network`.

> [!WARNING] Use --yolo only when isolated
> Use `--yolo` only where you already trust both the environment and the code, such as a disposable CI container. Never use it on a workstation with access to real credentials or infrastructure. `--yolo` removes both layers and trusts the workspace, so it loads the checkout's `AGENTS.md`, rules, and skills. On a pull-request or fork checkout, those files are attacker-controlled instructions.

## Next steps

- Distribute work across a team of agents under the same guardrails with [multi-agent orchestration](/docs/muse-code/extending#multi-agent).
- Run structured agent groups within this boundary with [workflows](/docs/muse-code/workflows).
- Review how incoming peers are authorized in [session messaging](/docs/muse-code/session-messaging#approval).
- Connect external agent tooling to the model from the [coding agents](/docs/coding-agents) guide.
