---
meta:
  title: Changelog
  description: What's new, improved, and fixed in each Muse Code release.
  keywords: changelog, release notes, muse code, updates, versions
cms:
  alias: /model-api/docs/muse-code/changelog
  target: aidmc
---

# Changelog

What's new, improved, and fixed in each Muse Code release. For install and upgrade steps, see the [Muse Code overview](/docs/muse-code).

## 0.2.1 {#v0-2-1}

### New

- Rewind the conversation with a double Esc: pick an earlier point, confirm before anything is undone, and only safe rewind points are offered
- Automatic approval pre-screening: a model-based reviewer clears tool requests it judges safe, so you see fewer prompts. Anything it doesn't clear still comes to you, and it can be disabled
- When the sandbox blocks a command, the agent can ask for a one-time approval to run that exact command outside it
- Added a "Review plan" action to step through long plans that overflow the panel
- Added `muse config` to validate enterprise-managed configuration documents
- Added a built-in skill for setting up isolated Python environments
- Added a built-in skill for handing off and verifying browser apps the agent builds
- Hook commands now receive a selected set of environment variables
- The input box can show a short contextual hint after a turn finishes

### Improvements

- Approval dialogs wait for a pause in your typing before appearing, so they stop stealing keystrokes mid-sentence
- Permission decisions are retained in the session log and restored on resume
- The resume picker surfaces sessions that were previously hidden
- `--model` accepts any model id; unknown ids use sensible assumed metadata instead of being rejected
- Settings accept the standard `mcpServers` key, matching the common ecosystem format
- MCP configuration across multiple files and scopes merges consistently
- Clearer diagnostics when an MCP server fails to start, reported once instead of pinned in the interface
- Optional MCP servers that fail at startup no longer spam the transcript
- You can see which of your hooks are running in the live activity area
- Messages sent as a turn finishes are delivered together in one follow-up turn
- Text typed as part of a rewind is kept and restored
- The agent can ask longer questions, up to 500 characters
- The Write tool flags when a new file nearly duplicates an existing one
- Sessions at Ultra reasoning effort default to maximum parallel-agent capacity unless you set a limit
- Session export stitches in subagent transcripts that finish independently
- Redesigned `/status` as a cleaner summary card
- `/usage` and `/models` label costs explicitly as USD
- Skill slash commands are highlighted while you type
- Tables stay narrow enough to read in a terminal
- The bundled plan skill researches sources first and presents the plan for review before starting work
- Rewrote the built-in plan, doctor, and source-control skills with clearer guidance
- The design skill reliably engages before the assistant writes visual web frontend code
- Within a session, the agent remembers which skills it already read and avoids redundant re-reads
- Skills with aliases appear once under their canonical name
- `skills import --from` errors now list the accepted values

### Fixes

- **Security:** a malicious repository's git configuration can no longer run arbitrary commands
- **Security:** git commands on your repos ignore repo-configured hooks, so a malicious repo can't run code through them
- **Security:** skill text containing hidden terminal-control characters is rejected, preventing display spoofing
- **Security:** Linux sandboxed commands can no longer reach host services through Unix-domain sockets
- **Security:** a folder carrying both Mercurial and Sapling metadata is no longer probed for repository status
- Fixed a crash when resuming a session whose background agent run couldn't be re-read
- Fixed a panic when piping output into commands such as `head`
- Fixed a crash on non-UTF-8 command-line arguments
- Partial model responses cut off mid-stream are kept and marked incomplete instead of lost
- Model calls fail fast with a clear status when the network is down, instead of hanging through silent retries
- The working indicator and retry countdown stay visible when a response drops mid-stream
- Streamed answer text no longer appears in the wrong place before the response type is known
- HTTP and HTTPS proxy environment variables are respected for all network traffic
- Keystrokes are no longer lost while an approval decision is submitting
- Multi-line pasted text stays together, including in terminals without bracketed-paste support
- Fixed shifted keys being misread in older VS Code terminals
- Prompts typed in quick succession while a run starts are accepted instead of dropped
- Prompts appear in the transcript as soon as you submit them, even while the run is still starting
- Ctrl-C withdraws queued messages that hadn't started yet
- A steering message you already sent is no longer lost when you retract the turn
- Retracting a turn just after a steering message went through no longer freezes the interface
- Prompts entered when forking a session run in the forked session, not the original
- Esc interrupts the end-of-turn reminder wait instead of appearing to hang
- Tools no longer time out while waiting for you to answer an approval prompt
- Resume restores permission prompts that were still awaiting an answer
- Resumed sessions keep the approval mode you chose
- Permission prompts stay visible when the side panel refreshes
- Denying a network permission request now tells the agent and shows in the transcript
- The automatic permission reviewer is more predictable, with consistent verdicts, retry caps, and timeouts
- `/compact` compacts the session's real working set, including after forks and side chats
- `/compact` runs in the background instead of blocking the session
- Branching into a side chat after a restart no longer breaks conversation history
- Resume replays subagent activity recorded in the parent session log, with the original identity
- Resumed sessions keep subagent lifecycle events in their original order
- Output from background subagents started before a resume is replayed instead of disappearing
- Subagent results that finished before you pressed Esc are preserved instead of disappearing with the cancelled turn
- Long-running background subagents reliably deliver their final answer
- Input submitted just before the app stops is no longer stranded on resume
- Resume no longer writes checkpoints from a half-replayed log, or breaks on expected gaps in the checkpoint log
- Resume no longer risks adopting the wrong `/compact` result during recovery
- Manual `/compact` runs are recorded durably and survive restarts
- A log truncated mid-write no longer restores a partially written permission record
- Session goals are restored with working controls after a kill and resume, and usage totals stay correct when a goal is replaced
- Resumed session goals restore their usage totals instead of failing to resume
- Session goals pause when successive turns stop making progress, instead of looping indefinitely
- Exported sessions keep the full record of permission prompts and decisions
- Sessions get a proper end record on normal exit, keeping history and resume listings accurate
- Closing or losing your terminal is no longer misreported as a crash
- Starting two sessions at the same moment no longer fails to open the local session store on a first run
- Starting from a missing or unreadable folder fails immediately with a clear error
- A prompt passed at startup is no longer occasionally captured as blank
- Fixed a race at run start that could leave the session in a confused launch state
- Headless runs pass your prompt text through unmodified by default
- A `!` shell command whose process dies unexpectedly settles cleanly instead of leaving the session stuck
- Background processes are cleaned up more reliably when a session exits
- The agent gets correct guidance for backgrounding commands from the shell tool on macOS
- Stopping a background task no longer hangs when two stop requests race
- Background reminder checks are tied to their own run, so no activity lingers after it ends
- Headless runs no longer hang after finishing because an older reminder task is still open
- Background command and task ids are globally unique and time-ordered
- Scheduled tasks with a timezone problem warn once instead of every tick
- A corrupt scheduled-task database now warns at startup and identifies where the quarantined data was retained
- A failed subagent launch no longer permanently consumes a capacity slot
- Subagents that finish without a result show a proper final state
- Notes typed in a subagent's view reach the running subagent
- Subagent worktrees whose ownership can't be proven after a crash are quarantined instead of wrongly cleaned up
- Status lines for cancelled and waiting agents show the agent name instead of a raw UUID
- Messages with pasted images sent while the agent is busy arrive in order
- Pasting an image alongside a pending rewind routes correctly
- Hook output starting with a UTF-8 BOM has its allow or deny decision honored
- Project hooks take effect as soon as you trust a folder, without a restart
- Hooks triggered by `!` shell commands are durably recorded and survive resume and export
- Structured JSON output from file hooks is preserved instead of flattened
- Rejected hook output produces a bounded, readable diagnostic
- Shell approval prompts keep the command's original line breaks
- Invalid todo-list tool arguments produce a proper structured error
- A malformed skill on or off value in settings is ignored gracefully instead of breaking loading
- Prompt hints only suggest commands that exist in your session
- A symlinked user config directory no longer breaks loading of project and built-in agent definitions
- Fixed a settings file lock held longer than needed, which could block later writes
- Ctrl-L clears the screen without redraw artifacts
- `/help` shows the full shortcut list in an 80×24 terminal
- Fixed a wildly wrong elapsed time in the activity row after reattaching to a session
- The task panel no longer glitches while old checkpoints are retired
- The Ultra reasoning-effort display and activation animation no longer pop, flicker, or dim
- On Linux, the command sandbox is selected once at startup so behavior stays consistent for the session
- The built-in doctor skill's session-evidence collection and redaction work correctly again

### Performance

- Faster startup with a large skill catalog, and an accurate count of skills dropped from the catalog
- Git operations for isolated subagent worktrees no longer block the agent runtime

## 0.1.x {#v0-1-x}

Also delivered in 0.1.x patches: attaching the session recording when reporting a bug as well as a bad result; correct truecolor detection for Ghostty over SSH; reliable replay of terminal command output in long sessions; subagent results shown once with the correct outcome; and a rollback of a built-in instruction change that had regressed answer quality.

## 0.1.0 {#v0-1-0}

- Launch version
