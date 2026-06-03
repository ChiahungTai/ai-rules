---
name: skill-cleaner
description: "Audit Claude Code skills: duplicate skills, unused skills, prompt-budget usage, compact descriptions. Use when trimming skill listing budget, finding duplicates, or deciding which skills to remove."
---

# Skill Cleaner (Claude Code)

## Instructions

When invoked, run the analyzer script and present actionable cleanup recommendations to the user.

### Step 1: Run the analyzer

```bash
node --experimental-strip-types ${CLAUDE_SKILL_DIR}/scripts/skill-cleaner.ts --months 3
```

For a quick scan without session log analysis (faster):

```bash
node --experimental-strip-types ${CLAUDE_SKILL_DIR}/scripts/skill-cleaner.ts --no-logs
```

To also scan agent-skills or other extra roots:

```bash
node --experimental-strip-types ${CLAUDE_SKILL_DIR}/scripts/skill-cleaner.ts --months 3 --root ~/Github/agent-skills/skills
```

### Step 2: Summarize the report

Present the findings to the user in this priority order:

1. **Budget Status** — Is the skill listing within budget or overflowing? If overflowing, which skills could be set to `"name-only"` in `skillOverrides` to free space?
2. **Duplicates** — Which skills exist in multiple roots? Recommend which copies to delete (prefer keeping personal scope over extra roots).
3. **Unused Skills** — Which skills have zero invocations in recent months? Are any safe to remove or set to `"name-only"`?
4. **Long Descriptions** — Which skills have descriptions over 120 chars? Suggest shorter alternatives.

### Step 3: Wait for user confirmation

**Do not modify anything without user approval.** For each recommendation category, ask the user which actions to take. Possible actions:

- **Delete duplicate** — remove a skill directory that has an identical copy elsewhere
- **Shorten description** — edit SKILL.md frontmatter to use a shorter `description`
- **Set name-only** — add entry to `skillOverrides` in `~/.claude/settings.json` as `"name-only"` to hide description from listing while keeping the skill available
- **Set off** — add entry to `skillOverrides` as `"off"` to fully hide the skill

When applying changes, group them into small logical commits: description edits separate from deletes separate from settings changes.

## What the analyzer does

- **Skill discovery**: scans `~/.claude/skills/` (personal), `~/.claude/plugins/` (plugin), optional `--root` and `--project` paths. Realpath-deduplicates roots so symlinks do not create false duplicates.
- **Budget**: reads `skillListingBudgetFraction` from `~/.claude/settings.json`. Estimates listing size against context window (200K tokens). Each skill description is capped at 1,536 chars.
- **Usage tracking**: scans Claude Code session transcripts at `~/.claude/projects/*/*.jsonl` for `"name":"Skill"` tool_use entries. Counts invocations per skill name over the configured month window.
- **Duplicate detection**: groups skills by base name and body hash, uses Jaccard similarity to identify near-copies.
- **Settings analysis**: reports `skillOverrides`, `Skill()` permission count, and `skillListingBudgetFraction` value.
