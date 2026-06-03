#!/usr/bin/env -S node --experimental-strip-types
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

type Skill = {
  name: string;
  baseName: string;
  combinedDescription: string;
  description: string;
  whenToUse: string;
  disableModelInvocation: boolean;
  userInvocable: boolean;
  path: string;
  realPath: string;
  dir: string;
  root: string;
  realRoot: string;
  scope: string;
  descChars: number;
  bodyHash: string;
  bodyKey: string;
  descKey: string;
};

type Usage = {
  invocations: number;
};

type Settings = {
  budgetFraction: number;
  budgetSource: string;
  skillOverrides: Record<string, string>;
  skillPermissionCount: number;
  model: string;
};

type Budget = {
  contextTokens: number;
  budgetFraction: number;
  budgetChars: number;
  totalDescriptionChars: number;
  estimatedListingChars: number;
  modelInvocableSkills: number;
  disabledModelInvocation: number;
  status: string;
};

const MAX_DESCRIPTION_CHARS = 1536;
const DEFAULT_CONTEXT_TOKENS = 200_000;
const DEFAULT_BUDGET_FRACTION = 0.01;
const CHARS_PER_TOKEN = 4;

const home = os.homedir();
const args = new Set(process.argv.slice(2));

function argValue(name: string, fallback: string): string {
  const raw = process.argv.slice(2);
  const index = raw.indexOf(name);
  return index >= 0 && raw[index + 1] ? raw[index + 1] : fallback;
}

const months = Number(argValue("--months", "3"));
const noLogs = args.has("--no-logs");
const jsonOutput = args.has("--json");
const includeProject = args.has("--project");
const maxLogBytes = Number(argValue("--max-log-mb", "300")) * 1024 * 1024;
const cutoffMs = Date.now() - Math.max(0, months) * 31 * 24 * 60 * 60 * 1000;
const extraRoots = process.argv
  .slice(2)
  .flatMap((arg, index, all) => (arg === "--root" && all[index + 1] ? [all[index + 1]] : []));

function expandHome(input: string): string {
  return input.replace(/^~(?=$|\/)/, home);
}

function exists(input: string): boolean {
  try {
    fs.accessSync(input);
    return true;
  } catch {
    return false;
  }
}

function walkFiles(root: string, predicate: (file: string) => boolean, maxDepth = 8): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  function walk(dir: string, depth: number) {
    if (depth > maxDepth) return;
    let real = dir;
    try {
      real = fs.realpathSync(dir);
    } catch {
      return;
    }
    if (seen.has(real)) return;
    seen.add(real);
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name === "node_modules" || entry.name === ".git") continue;
      const file = path.join(dir, entry.name);
      if (entry.isDirectory() || entry.isSymbolicLink()) {
        let stat: fs.Stats;
        try {
          stat = fs.statSync(file);
        } catch {
          continue;
        }
        if (stat.isDirectory()) walk(file, depth + 1);
      } else if (entry.isFile() && predicate(file)) {
        out.push(file);
      }
    }
  }
  if (exists(root)) walk(root, 0);
  return out;
}

function walkRecentFiles(root: string, predicate: (file: string) => boolean, maxDepth = 8): string[] {
  const out: string[] = [];
  function walk(dir: string, depth: number) {
    if (depth > maxDepth) return;
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const file = path.join(dir, entry.name);
      let stat: fs.Stats;
      try {
        stat = fs.statSync(file);
      } catch {
        continue;
      }
      if (entry.isDirectory()) {
        if (depth > 0 && stat.mtimeMs < cutoffMs) continue;
        walk(file, depth + 1);
      } else if (entry.isFile() && stat.mtimeMs >= cutoffMs && predicate(file)) {
        out.push(file);
      }
    }
  }
  if (exists(root)) walk(root, 0);
  return out;
}

function sanitizeSingleLine(value: string): string {
  return value.replace(/[\r\n\t]+/g, " ").replace(/\s+/g, " ").trim();
}

function parseYamlScalar(raw: string): string {
  const value = raw.trim();
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function parseFrontmatter(file: string): {
  name?: string;
  description?: string;
  whenToUse?: string;
  disableModelInvocation?: boolean;
  userInvocable?: boolean;
  body: string;
} | null {
  const text = fs.readFileSync(file, "utf8");
  const lines = text.split(/\r?\n/);
  if (lines[0]?.trim() !== "---") return null;
  const fm: string[] = [];
  let end = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i]?.trim() === "---") {
      end = i;
      break;
    }
    fm.push(lines[i] ?? "");
  }
  if (end < 0) return null;
  let name: string | undefined;
  let description: string | undefined;
  let whenToUse: string | undefined;
  let disableModelInvocation: boolean | undefined;
  let userInvocable: boolean | undefined;
  for (let i = 0; i < fm.length; i++) {
    const line = fm[i] ?? "";
    const match = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (!match) continue;
    const key = match[1];
    const raw = match[2] ?? "";
    if (key === "name") name = sanitizeSingleLine(parseYamlScalar(raw));
    if (key === "description") {
      if (raw.trim() === "|" || raw.trim() === ">") {
        const block: string[] = [];
        for (let j = i + 1; j < fm.length; j++) {
          if (/^[A-Za-z0-9_-]+:\s*/.test(fm[j] ?? "")) break;
          block.push((fm[j] ?? "").replace(/^\s{2}/, ""));
        }
        description = sanitizeSingleLine(block.join(" "));
      } else {
        description = sanitizeSingleLine(parseYamlScalar(raw));
      }
    }
    if (key === "when_to_use") {
      if (raw.trim() === "|" || raw.trim() === ">") {
        const block: string[] = [];
        for (let j = i + 1; j < fm.length; j++) {
          if (/^[A-Za-z0-9_-]+:\s*/.test(fm[j] ?? "")) break;
          block.push((fm[j] ?? "").replace(/^\s{2}/, ""));
        }
        whenToUse = sanitizeSingleLine(block.join(" "));
      } else {
        whenToUse = sanitizeSingleLine(parseYamlScalar(raw));
      }
    }
    if (key === "disable-model-invocation") {
      disableModelInvocation = raw.trim().toLowerCase() === "true";
    }
    if (key === "user-invocable") {
      userInvocable = raw.trim().toLowerCase() === "false" ? false : true;
    }
  }
  return {
    name,
    description,
    whenToUse,
    disableModelInvocation,
    userInvocable,
    body: lines.slice(end + 1).join("\n"),
  };
}

function fnv1a(input: string): string {
  let hash = 0x811c9dc5;
  for (let i = 0; i < input.length; i++) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
}

function normalizeWords(input: string): string {
  return input
    .toLowerCase()
    .replace(/[`"''.,;:!?/\\[\]{}_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function wordSet(input: string): Set<string> {
  return new Set(normalizeWords(input).split(" ").filter((word) => word.length >= 2));
}

function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 && b.size === 0) return 1;
  let intersection = 0;
  for (const item of a) {
    if (b.has(item)) intersection++;
  }
  return intersection / (a.size + b.size - intersection);
}

function similarity(a: Skill, b: Skill): { description: number; body: number; overall: number } {
  const description = jaccard(wordSet(a.combinedDescription), wordSet(b.combinedDescription));
  const body = a.bodyHash === b.bodyHash ? 1 : jaccard(wordSet(a.bodyKey), wordSet(b.bodyKey));
  return {
    description,
    body,
    overall: body * 0.8 + description * 0.2,
  };
}

function isLikelyCopy(score: { description: number; body: number }): boolean {
  return score.body >= 0.95 || (score.body >= 0.85 && score.description >= 0.85);
}

function scopeForRoot(root: string): string {
  const normalized = root.split(path.sep).join("/");
  if (normalized.includes("/.claude/plugins")) return "plugin";
  // ~/.claude/skills = personal; <project>/.claude/skills = project
  if (normalized.startsWith(home + "/.claude/skills")) return "personal";
  if (normalized.includes("/.claude/skills")) return "project";
  return "extra";
}

function preferredKeepSkill(list: Skill[]): Skill {
  return [...list].sort((a, b) => {
    const scopeOrder = (s: string) => (s === "personal" ? 0 : s === "project" ? 1 : s === "plugin" ? 2 : 3);
    const byScope = scopeOrder(a.scope) - scopeOrder(b.scope);
    if (byScope !== 0) return byScope;
    return a.realPath.length - b.realPath.length || a.realPath.localeCompare(b.realPath);
  })[0]!;
}

function groupBy<T>(items: T[], key: (item: T) => string): Map<string, T[]> {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const value = key(item);
    map.set(value, [...(map.get(value) ?? []), item]);
  }
  return map;
}

function formatPct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function formatNumber(value: number): string {
  return Math.round(value).toLocaleString("en-US");
}

function suggestDescription(skill: Skill): string {
  const source = normalizeWords(`${skill.baseName} ${skill.combinedDescription}`);
  const cues: string[] = [];
  const add = (label: string, pattern: RegExp) => {
    if (pattern.test(source) && !cues.includes(label)) cues.push(label);
  };
  add("review", /\b(review|audit|inspect|verify)\b/);
  add("debug", /\b(debug|trace|diagnos|fix)\b/);
  add("deploy", /\b(deploy|release|publish|ship)\b/);
  add("docs", /\b(doc|markdown|write|distill)\b/);
  add("test", /\b(test|spec|tdd|bdd)\b/);
  add("search", /\b(search|sync|archive|crawl)\b/);
  add("GitHub", /\b(github|issue|pr|ci)\b|pull request/);
  add("build", /\b(build|implement|scaffold)\b/);
  add("security", /\b(security|harden|vulnerab)\b/);
  add("performance", /\b(perf|optim|speed|latency)\b/);
  const verbs = cues.length ? cues.slice(0, 5).join(", ") : skill.baseName.replace(/-/g, " ");
  return `${verbs}: keep under 120 chars for best budget fit.`;
}

function readSettings(): Settings {
  const settingsPath = path.join(home, ".claude", "settings.json");
  let budgetFraction = DEFAULT_BUDGET_FRACTION;
  let budgetSource = "default (1%)";
  const skillOverrides: Record<string, string> = {};
  let skillPermissionCount = 0;
  let model = "unknown";

  if (!exists(settingsPath)) {
    return { budgetFraction, budgetSource, skillOverrides, skillPermissionCount, model };
  }

  try {
    const raw = fs.readFileSync(settingsPath, "utf8");
    const settings = JSON.parse(raw);

    if (typeof settings.skillListingBudgetFraction === "number") {
      budgetFraction = settings.skillListingBudgetFraction;
      budgetSource = settingsPath;
    }

    if (settings.skillOverrides && typeof settings.skillOverrides === "object") {
      for (const [key, value] of Object.entries(settings.skillOverrides)) {
        if (typeof value === "string") {
          skillOverrides[key] = value;
        }
      }
    }

    if (typeof settings.model === "string") {
      model = settings.model;
    }

    if (Array.isArray(settings.permissions?.allow)) {
      skillPermissionCount = settings.permissions.allow.filter(
        (entry: unknown) => typeof entry === "string" && entry.startsWith("Skill(")
      ).length;
    }
  } catch {}

  return { budgetFraction, budgetSource, skillOverrides, skillPermissionCount, model };
}

function pluginSkills(): { root: string; prefix: string }[] {
  const plugins: { root: string; prefix: string }[] = [];
  const installedPath = path.join(home, ".claude", "plugins", "installed_plugins.json");
  if (!exists(installedPath)) return plugins;

  try {
    const raw = fs.readFileSync(installedPath, "utf8");
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) return plugins;

    for (const plugin of data) {
      if (!plugin.installPath || !plugin.name) continue;
      const pluginSkillsRoot = path.join(plugin.installPath, "skills");
      if (exists(pluginSkillsRoot)) {
        const prefix = plugin.name.split("@")[0] ?? plugin.name;
        plugins.push({ root: pluginSkillsRoot, prefix });
      }
    }
  } catch {}

  return plugins;
}

function discoverRoots(): string[] {
  const rootsByRealPath = new Map<string, string>();

  const personalRoot = path.join(home, ".claude", "skills");
  if (exists(personalRoot)) {
    const real = fs.realpathSync(personalRoot);
    rootsByRealPath.set(real, personalRoot);
  }

  for (const { root } of pluginSkills()) {
    if (!exists(root)) continue;
    const real = fs.realpathSync(root);
    const current = rootsByRealPath.get(real);
    if (!current || root.length < current.length) rootsByRealPath.set(real, root);
  }

  if (includeProject) {
    const projectRoot = path.join(process.cwd(), ".claude", "skills");
    if (exists(projectRoot)) {
      const real = fs.realpathSync(projectRoot);
      const current = rootsByRealPath.get(real);
      if (!current || projectRoot.length < current.length) rootsByRealPath.set(real, projectRoot);
    }
  }

  for (const extraRoot of extraRoots.map(expandHome)) {
    if (!exists(extraRoot)) continue;
    const real = fs.realpathSync(extraRoot);
    const current = rootsByRealPath.get(real);
    if (!current || extraRoot.length < current.length) rootsByRealPath.set(real, extraRoot);
  }

  return [...rootsByRealPath.values()].sort();
}

function discoverSkills(): Skill[] {
  const settings = readSettings();
  const skillsByRealPath = new Map<string, Skill>();
  const plugins = pluginSkills();

  for (const root of discoverRoots()) {
    const scope = scopeForRoot(root);
    const pluginMatch = plugins.find((p) => {
      try {
        return fs.realpathSync(root) === fs.realpathSync(p.root);
      } catch {
        return false;
      }
    });
    const pluginPrefix = pluginMatch?.prefix;

    for (const file of walkFiles(root, (candidate) => path.basename(candidate) === "SKILL.md", 10)) {
      const parsed = parseFrontmatter(file);
      if (!parsed) continue;

      const baseName = parsed.name || path.basename(path.dirname(file));
      const name = pluginPrefix ? `${pluginPrefix}:${baseName}` : baseName;
      const description = parsed.description ?? "";
      const whenToUse = parsed.whenToUse ?? "";
      let combined = description;
      if (whenToUse) combined = combined ? `${combined} ${whenToUse}` : whenToUse;
      if (combined.length > MAX_DESCRIPTION_CHARS) {
        combined = combined.slice(0, MAX_DESCRIPTION_CHARS);
      }

      const bodyKey = normalizeWords(parsed.body);
      const skill: Skill = {
        name,
        baseName,
        combinedDescription: combined,
        description,
        whenToUse,
        disableModelInvocation: parsed.disableModelInvocation ?? false,
        userInvocable: parsed.userInvocable ?? true,
        path: file,
        realPath: fs.realpathSync(file),
        dir: path.dirname(file),
        root,
        realRoot: fs.realpathSync(root),
        scope,
        descChars: [...combined].length,
        bodyHash: fnv1a(bodyKey),
        bodyKey,
        descKey: normalizeWords(combined),
      };

      const existing = skillsByRealPath.get(skill.realPath);
      if (!existing || skill.path.length <= existing.path.length) {
        skillsByRealPath.set(skill.realPath, skill);
      }
    }
  }

  for (const [key, override] of Object.entries(settings.skillOverrides)) {
    for (const skill of skillsByRealPath.values()) {
      if (skill.name === key || skill.baseName === key) {
        if (override === "off" || override === "name-only") {
          skill.disableModelInvocation = true;
        }
      }
    }
  }

  return [...skillsByRealPath.values()];
}

function recentLogFiles(): string[] {
  if (noLogs) return [];
  const files = new Set<string>();
  const projectsDir = path.join(home, ".claude", "projects");
  if (!exists(projectsDir)) return [];

  for (const projectEntry of fs.readdirSync(projectsDir, { withFileTypes: true })) {
    if (!projectEntry.isDirectory()) continue;
    const projectPath = path.join(projectsDir, projectEntry.name);
    for (const file of walkRecentFiles(
      projectPath,
      (candidate) => candidate.endsWith(".jsonl"),
      4
    )) {
      try {
        if (fs.statSync(file).mtimeMs >= cutoffMs) files.add(file);
      } catch {}
    }
  }

  return [...files].sort();
}

function scanUsage(skills: Skill[], logFiles: string[]): Map<string, Usage> {
  const usage = new Map<string, Usage>();
  for (const skill of skills) {
    usage.set(skill.name, { invocations: 0 });
  }

  const nameToCanonical = new Map<string, string>();
  for (const skill of skills) {
    const names = [skill.name, skill.baseName, skill.name.split(":").at(-1) ?? skill.name];
    for (const n of names) {
      nameToCanonical.set(n.toLowerCase(), skill.name);
    }
  }

  let consumedBytes = 0;
  for (const file of logFiles) {
    let text = "";
    try {
      const stat = fs.statSync(file);
      if (stat.size > 150 * 1024 * 1024) continue;
      if (consumedBytes + stat.size > maxLogBytes) break;
      consumedBytes += stat.size;
      text = fs.readFileSync(file, "utf8");
    } catch {
      continue;
    }

    const invocations = [...text.matchAll(/"name"\s*:\s*"Skill"/g)];
    for (const match of invocations) {
      const start = Math.max(0, match.index! - 200);
      const end = Math.min(text.length, match.index! + 200);
      const context = text.slice(start, end);
      const skillMatch = /"skill"\s*:\s*"([^"]+)"/.exec(context);
      if (skillMatch) {
        const skillName = skillMatch[1]!.toLowerCase();
        const canonical = nameToCanonical.get(skillName);
        if (canonical) {
          const item = usage.get(canonical);
          if (item) item.invocations++;
        }
      }
    }
  }

  return usage;
}

function computeBudget(skills: Skill[], settings: Settings): Budget {
  const modelInvocable = skills.filter((s) => !s.disableModelInvocation);
  const totalDescriptionChars = modelInvocable.reduce((sum, s) => sum + s.descChars, 0);
  const overheadPerSkill = 10;
  const estimatedListingChars = modelInvocable.reduce(
    (sum, s) => sum + s.name.length + s.descChars + overheadPerSkill,
    0
  );
  const budgetChars = Math.floor(DEFAULT_CONTEXT_TOKENS * settings.budgetFraction * CHARS_PER_TOKEN);

  return {
    contextTokens: DEFAULT_CONTEXT_TOKENS,
    budgetFraction: settings.budgetFraction,
    budgetChars,
    totalDescriptionChars,
    estimatedListingChars,
    modelInvocableSkills: modelInvocable.length,
    disabledModelInvocation: skills.length - modelInvocable.length,
    status: estimatedListingChars <= budgetChars ? "within budget" : "overflowing",
  };
}

function render(skills: Skill[], usage: Map<string, Usage>, logFiles: string[]): string {
  const settings = readSettings();
  const budget = computeBudget(skills, settings);
  const modelInvocable = skills.filter((s) => !s.disableModelInvocation);

  const byBase = [...groupBy(modelInvocable, (s) => s.baseName.toLowerCase()).entries()].filter(
    ([, list]) => list.length > 1
  );
  const byBody = [...groupBy(modelInvocable, (s) => s.bodyHash).entries()].filter(
    ([hash, list]) => hash !== "811c9dc5" && list.length > 1
  );
  const longDescriptions = modelInvocable
    .filter((s) => s.descChars >= 120)
    .sort((a, b) => b.descChars - a.descChars)
    .slice(0, 30);
  const unused = modelInvocable
    .filter((s) => {
      const item = usage.get(s.name);
      return !item || item.invocations === 0;
    })
    .filter((s) => s.scope !== "plugin")
    .sort((a, b) => a.scope.localeCompare(b.scope) || a.name.localeCompare(b.name))
    .slice(0, 80);

  const roots = groupBy(skills, (s) => s.root);

  const lines: string[] = [];
  lines.push("# Skill Cleaner Report (Claude Code)", "");
  lines.push(`generated: ${new Date().toISOString()}`);
  lines.push(`months: ${months}`);
  lines.push(`skills: ${skills.length} discovered, ${budget.modelInvocableSkills} model-invocable, ${budget.disabledModelInvocation} disabled-model-invocation`);
  lines.push(`settings: budget_fraction=${(settings.budgetFraction * 100).toFixed(1)}%, model=${settings.model}`);
  lines.push(`log_files_scanned: ${logFiles.length}`, "");

  lines.push("## Skill Budget", "");
  lines.push(`context_tokens: ${formatNumber(budget.contextTokens)}`);
  lines.push(`budget_fraction: ${(budget.budgetFraction * 100).toFixed(1)}% (source: ${settings.budgetSource})`);
  lines.push(`budget_chars: ${formatNumber(budget.budgetChars)}`);
  lines.push(`estimated_listing_chars: ${formatNumber(budget.estimatedListingChars)}`);
  lines.push(`total_description_chars: ${formatNumber(budget.totalDescriptionChars)}`);
  lines.push(`model_invocable_skills: ${budget.modelInvocableSkills}`);
  lines.push(`disabled_model_invocation: ${budget.disabledModelInvocation}`);
  lines.push(`status: ${budget.status}`);
  if (budget.status === "overflowing") {
    const overflow = budget.estimatedListingChars - budget.budgetChars;
    lines.push(`overflow_chars: ${formatNumber(overflow)}`);
  }
  lines.push("");

  lines.push("## Description Candidates", "");
  for (const skill of longDescriptions) {
    lines.push(`- ${skill.name}`);
    lines.push(`  path: ${skill.path}`);
    lines.push(`  chars: ${skill.descChars}`);
    lines.push(`  current: ${skill.combinedDescription.slice(0, 100)}${skill.combinedDescription.length > 100 ? "..." : ""}`);
    lines.push(`  suggested: ${suggestDescription(skill)}`);
  }
  if (longDescriptions.length === 0) lines.push("- none");
  lines.push("");

  lines.push("## Duplicates By Name", "");
  for (const [name, list] of byBase.slice(0, 40)) {
    lines.push(`- ${name}`);
    const keep = preferredKeepSkill(list);
    lines.push(`  keep-default: ${keep.scope}: ${keep.path}`);
    for (const skill of list) {
      const score = skill.realPath === keep.realPath ? { body: 1, description: 1 } : similarity(keep, skill);
      lines.push(
        `  - ${skill.scope}: ${skill.path} (body=${formatPct(score.body)}, description=${formatPct(score.description)})`
      );
    }
  }
  if (byBase.length === 0) lines.push("- none");
  lines.push("");

  lines.push("## Duplicates By Body Hash", "");
  for (const [, list] of byBody.slice(0, 30)) {
    lines.push(`- ${list.map((s) => s.name).join(", ")}`);
    for (const skill of list) lines.push(`  - ${skill.scope}: ${skill.path}`);
  }
  if (byBody.length === 0) lines.push("- none");
  lines.push("");

  lines.push("## Unused Candidates", "");
  for (const skill of unused) {
    const item = usage.get(skill.name) ?? { invocations: 0 };
    lines.push(`- ${skill.name}: ${skill.scope}; invocations=${item.invocations}; ${skill.path}`);
  }
  if (unused.length === 0) lines.push("- none");
  lines.push("");

  lines.push("## Settings Summary", "");
  lines.push(`budget_source: ${settings.budgetSource}`);
  lines.push(`skillOverrides: ${Object.keys(settings.skillOverrides).length === 0 ? "(none)" : ""}`);
  for (const [key, value] of Object.entries(settings.skillOverrides)) {
    lines.push(`  ${key}: ${value}`);
  }
  lines.push(`Skill() permissions: ${settings.skillPermissionCount} entries`);
  lines.push("");

  lines.push("## Root Summary", "");
  for (const [root, list] of [...roots.entries()].sort((a, b) => b[1].length - a[1].length)) {
    const disabled = list.filter((s) => s.disableModelInvocation).length;
    lines.push(`- ${root}: ${list.length} skills${disabled ? `, ${disabled} hidden from model` : ""}`);
  }

  return lines.join("\n");
}

const skills = discoverSkills();
const logFiles = recentLogFiles();
const usage = scanUsage(skills, logFiles);

if (jsonOutput) {
  const settings = readSettings();
  const budget = computeBudget(skills, settings);
  console.log(JSON.stringify({ skills, usage: Object.fromEntries(usage), budget, logFiles }, null, 2));
} else {
  console.log(render(skills, usage, logFiles));
}
