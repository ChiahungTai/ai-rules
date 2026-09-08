#!/usr/bin/env python3
"""
Deploy bundled AGENTS.md to non-Claude harnesses.

Bundles ai-development-guide.md (guide) + rules with matching harness-scope
frontmatter -> writes to ~/.zcode/AGENTS.md, ~/.codex/AGENTS.md,
~/.config/muse/AGENTS.md (muse machine-wide user rules
path — probe-verified 2026-09-07; loads unconditionally, project AGENTS.md
wins on conflict).

Claude (~/.claude/CLAUDE.md) is NOT touched -- it stays symlink to the
slim guide; Claude gets rules via ~/.claude/rules/ auto-load.

Rule classification is auto-discovered from per-rule frontmatter:
    ---
    harness-scope: neutral
    ---
Scopes: neutral | claude-specific | meta

Default bundles 'neutral'. New rules without an explicit harness-scope
default to 'neutral' (generic knowledge defaults to cross-harness). Rules
that are Claude-specific must declare `harness-scope: claude-specific`
explicitly to be excluded from the bundle.

Broken-ref guard: scans every neutral rule's markdown links; if a neutral
rule links to a claude-specific rule, the deploy aborts with an error
listing each broken ref. This forces fixing the ref (or re-scoping the
target) before the bundle ships -- non-Claude readers would otherwise hit
a dead link. Parenthetical Claude notes `(Claude: ...)` are exempt, since
those are Claude-side pointers that non-Claude readers can ignore.

Bundle slimming: rule bodies may mark sections to drop from the bundle with
    <!-- bundle: skip-start --> ... <!-- bundle: skip-end -->
Claude reads the full file via ~/.claude/rules/ symlink; non-Claude bundles
get the slimmed version. No-op for rules without markers.

Size gate: non-Claude harnesses truncate the single AGENTS.md silently.
ZCode truncates at 102,400 bytes (100KiB, hardcoded in zcode.cjs -- no
config). The bundle carries a hard-fail limit of 90KiB (92,160 bytes),
leaving headroom below the truncation line. Over the limit -> abort with
guidance: slim rules/ (encoder-philosophy) or demote on-demand-grade
content to a reference skill (rule keeps an always-on core + pointer).
Precedents: acceptance-evidence / symbol-query-routing / instruction-writing
rule+skill pairs.

Run after editing rules/ (deploy discipline in rules/AGENTS.md). Idempotent.
"""

import argparse
import dataclasses
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GUIDE = REPO / "ai-development-guide.md"
RULES_DIR = REPO / "rules"

# draft-3 A案（S3）：muse 用不到的 harness-mechanics rules，從 muse 變體
# 排除。rules/ 單一源不變（排除≠改 scope：codex/zcode bundle 不受影響；
# 改名/刪除任一檔 tests/test_deploy_agents.py 即大聲失敗）。
MUSE_MECHANICS_EXCLUDE = frozenset(
    {
        "tool-discipline.md",  # 背景 spawn/TaskOutput/batch——ZCode 機械
        "symbol-query-routing.md",  # cr-first 路由——工單按需指名（高頻需 callers 查證時放回，代價 4.5KB）
        "model-routing.md",  # agent tier 派發——主 session 職責
        "context-management.md",  # /compact/STATE.md——headless 無此面
        "instruction-writing.md",  # muse 不寫我們的 instruction 檔
    }
)


@dataclasses.dataclass(frozen=True)
class DeployTarget:
    """單端部署配置：路徑＋scope＋排除＋獨立 size gate。"""

    path: pathlib.Path
    scopes: frozenset
    exclude: frozenset
    max_bytes: int
    label: str


VARIANT_LABEL_SUFFIX = ",muse-variant(no-mechanics)"


def scopes_label_for(scopes: frozenset, exclude: frozenset) -> str:
    """scopes → bundle label；exclude 非空＝變體後綴。bundle_for 與 main() 的單一組裝點。"""
    label = ",".join(sorted(scopes))
    if exclude:
        label += VARIANT_LABEL_SUFFIX
    return label


def bundle_for(target: DeployTarget) -> str:
    """該 target 的預期 bundle（label 語義與 main() 一致；freshness check 消費）。"""
    return build_bundle(
        discover_rules(RULES_DIR, target.scopes),
        scopes_label_for(target.scopes, target.exclude),
        target.exclude,
    )


def expected_bundle_for(target_path) -> bytes:
    """部署路徑 → 預期 bytes；未知路徑 KeyError。供 check_single_source 消費。"""
    for target in resolve_targets(pathlib.Path.home()):
        if target.path == pathlib.Path(target_path):
            return bundle_for(target).encode("utf-8")
    raise KeyError(f"unknown deploy target: {target_path}")


def resolve_targets(home: pathlib.Path) -> list[DeployTarget]:
    """三端配置。muse 端變體＋獨立 gate；其餘兩端語義不動。"""
    return [
        DeployTarget(
            home / ".zcode" / "AGENTS.md",
            frozenset({"neutral"}),
            frozenset(),
            BUNDLE_MAX_BYTES,
            "zcode",
        ),
        DeployTarget(
            home / ".codex" / "AGENTS.md",
            frozenset({"neutral"}),
            frozenset(),
            BUNDLE_MAX_BYTES,
            "codex",
        ),
        DeployTarget(
            home / ".config" / "muse" / "AGENTS.md",
            frozenset({"neutral"}),
            MUSE_MECHANICS_EXCLUDE,
            50
            * 1024,  # ai-rules 工作區 lane 約 51.9KB（64KiB − 專案層 − 包裝）；對齊 S3 gate
            "muse",
        ),
    ]


# ZCode truncates a single instruction file at 100KiB (102,400 bytes,
# hardcoded; Codex limit covered by project_doc_max_bytes knob, set to
# 102400 on 2026-09-08). Keep the bundle under 90KiB
# so tail rules never land in the silent-truncation zone.
BUNDLE_MAX_BYTES = 90 * 1024

# Early-warning threshold (fraction of BUNDLE_MAX_BYTES). Deploy-time visibility
# only -- the weekly bundle-watch advisory owns per-rule composition analysis
# and slimming candidates; this WARN just prevents "gate abort" being the
# first signal.
BUNDLE_WARN_RATIO = 0.85

# Appended as the bundle's last line; a deployed file whose tail lacks it was
# cut short (or hand-edited) -- load-time truncation is proven by size gate.
BUNDLE_END_SENTINEL = "<!-- bundle-end -->"

TARGETS = [t.path for t in resolve_targets(pathlib.Path.home())]

# Matches <!-- bundle: skip-start --> ... <!-- bundle: skip-end --> (incl. the
# trailing newline) so adjacent sections join cleanly. Non-greedy + DOTALL.
SKIP_PATTERN = re.compile(
    r"<!-- bundle: skip-start -->.*?<!-- bundle: skip-end -->\n?",
    flags=re.DOTALL,
)

HEADER = (
    "<!-- Generated by scripts/deploy_agents.py -- do not edit directly.\n"
    "     Source: ai-rules/ai-development-guide.md + rules/<scope: {scopes}>\n"
    "     Regenerate: uv run python scripts/deploy_agents.py -->\n\n"
)


def read_scope(path: pathlib.Path) -> str:
    """Extract harness-scope from YAML frontmatter. Default: neutral."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return "neutral"
    for line in content.split("\n")[1:]:
        if line.strip() == "---":
            break
        if line.strip().startswith("harness-scope:"):
            scope = line.split(":", 1)[1].strip()
            return scope or "neutral"
    return "neutral"


def discover_rules(
    rules_dir: pathlib.Path, target_scopes: set[str]
) -> list[pathlib.Path]:
    """Scan rules/*.md, return those whose harness-scope is in target_scopes."""
    rules = []
    for path in sorted(rules_dir.glob("*.md")):
        if read_scope(path) in target_scopes:
            rules.append(path)
    return rules


# Match `(Claude: ...)` parenthetical notes, supporting both ASCII `()`
# and full-width `（）` parens (CJK convention). Refs inside these are
# Claude-side pointers non-Claude readers can ignore, so they're stripped
# before scanning. Allows a single level of nested ASCII parens.
_OPEN = r"[\(（]"
_CLOSE = r"[\)）]"
_NOT_PAREN = r"[^()（）]"
CLAUDE_NOTE_PATTERN = re.compile(
    _OPEN
    + r"Claude[:：]"
    + _NOT_PAREN
    + r"*"
    + r"(?:\([^()]*\)"
    + _NOT_PAREN
    + r"*)*"
    + _CLOSE
)

# Markdown link `[text](target.md)` — capture target path.
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")

# Backtick-quoted bare rule ref like `` `rule-name.md` ``.
BACKTICK_REF_PATTERN = re.compile(r"`([a-z][a-z0-9_-]*\.md)`")


def scan_sources(rules_dir: pathlib.Path, include_guide: bool) -> list[tuple[str, str]]:
    """Bundle sources as (name, content) pairs, Claude notes stripped.

    Neutral rules always (purity scope per rules/AGENTS.md 機械檢查清單:
    rules/*.md only -- the guide legitimately mentions cross-harness bare
    slash commands like `/handoff`, so it must NOT enter the purity scan).
    Guide included only for broken-ref scanning (it ships in the bundle too).
    rules/AGENTS.md itself is meta-scoped and never enters the neutral set,
    so its self-referential examples cannot false-positive either scan.
    """
    sources = [
        (p.name, p.read_text(encoding="utf-8"))
        for p in discover_rules(rules_dir, {"neutral"})
    ]
    if include_guide and GUIDE.exists():
        sources.append((GUIDE.name, GUIDE.read_text(encoding="utf-8")))
    return [(name, CLAUDE_NOTE_PATTERN.sub("", content)) for name, content in sources]


def check_broken_refs(
    rules_dir: pathlib.Path,
) -> list[tuple[str, str, str]]:
    """Find bundle sources (neutral rules + guide) linking to claude-specific rules.

    Returns a list of (source_name, link_target, target_rule_name) tuples.
    Parenthetical Claude notes `(Claude: ...)` are exempt: their contents are
    stripped before scanning, so refs inside them don't count as broken.

    The scan scope is a global invariant -- it always checks neutral sources
    against claude-specific targets, regardless of what deploy is bundling.
    The guide is scanned since build_bundle ships it verbatim (a guide-side
    ref to a claude-specific file is just as dead for non-Claude readers).
    """
    claude_stems = {p.stem for p in discover_rules(rules_dir, {"claude-specific"})}

    broken: list[tuple[str, str, str]] = []
    for src_name, cleaned in scan_sources(rules_dir, include_guide=True):
        # Markdown links `[text](target.md)`.
        for _, link_target in LINK_PATTERN.findall(cleaned):
            stem = pathlib.Path(link_target).stem
            if stem in claude_stems:
                broken.append((src_name, link_target, stem))
        # Bare backtick refs `` `rule-name.md` ``.
        for match in BACKTICK_REF_PATTERN.finditer(cleaned):
            ref = match.group(1)
            stem = ref[:-3]  # strip ".md"
            if stem in claude_stems:
                broken.append((src_name, ref, stem))
    return broken


# Neutral-purity patterns -- the programmatic form of rules/AGENTS.md's
# 機械檢查清單 (which until 2026-08-30 existed only as prose commands nobody
# ran; two live violations had shipped to all three deployed bundles).
# 已知限制：(1) 掃描面 = 全文，build_bundle 的 slim skip 段不 ship 但仍被掃
# （repo 現無 marker；首個 skip marker 出現時重訪此差異）。(2) bare-slash
# pattern 與 checklist 的 rg 原文逐字等價（僅攔 backtick 形態）。(3)
# claude-wrapper 的豁免詞「Claude 端」為列舉制——寫「Claude Code」等其他
# 措辭會誤抓，屬可接受的 heuristic。
PURITY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bare-slash-command", re.compile(r"`/[a-z][a-z-]+[ `]")),
    ("at-transclusion", re.compile(r"@~/|@\.\./|@/[a-z]")),
    ("cross-domain-path", re.compile(r"\.\./(commands|skills)/")),
    ("abs-user-path", re.compile(r"~/Github/ai-rules/")),
]
CLAUDE_WRAPPER_PATTERN = re.compile(r"CLAUDE\.md wrapper")


def check_neutral_purity(rules_dir: pathlib.Path) -> list[tuple[str, str, str]]:
    """Find neutral-rule purity violations (rules/AGENTS.md 機械檢查清單).

    Returns a list of (rule_name, check_label, matched_text) tuples. Input is
    Claude-note-stripped, matching the checklist's 括號注 exemption.
    """
    violations: list[tuple[str, str, str]] = []
    for rule_name, cleaned in scan_sources(rules_dir, include_guide=False):
        for label, pattern in PURITY_PATTERNS:
            for match in pattern.finditer(cleaned):
                violations.append((rule_name, label, match.group(0)))
        for line in cleaned.splitlines():
            if CLAUDE_WRAPPER_PATTERN.search(line) and "Claude 端" not in line:
                violations.append(
                    (rule_name, "claude-wrapper-unannotated", line.strip()[:80])
                )
    return violations


def slim_for_bundle(content: str, rule_name: str = "") -> str:
    """Drop bundle-skip marker sections. No-op when no markers present.

    Warns on unbalanced markers (start without end or vice versa) so future
    edits that drop a marker don't silently skip the slimming.
    """
    starts = content.count("<!-- bundle: skip-start -->")
    ends = content.count("<!-- bundle: skip-end -->")
    if starts != ends:
        loc = f" in {rule_name}" if rule_name else ""
        print(
            f"[WARN] unbalanced bundle markers{loc}: {starts} start vs {ends} end",
            file=sys.stderr,
        )
    return SKIP_PATTERN.sub("", content)


def build_bundle(
    rule_paths: list[pathlib.Path],
    scopes_label: str,
    exclude: frozenset = frozenset(),
) -> str:
    parts = [HEADER.format(scopes=scopes_label)]
    parts.append(GUIDE.read_text(encoding="utf-8").strip())
    parts.append("")
    for rule_path in rule_paths:
        if rule_path.name in exclude:
            continue
        parts.append(f"\n---\n<!-- rules/{rule_path.name} -->\n")
        parts.append(
            slim_for_bundle(
                rule_path.read_text(encoding="utf-8"), rule_path.name
            ).strip()
        )
        parts.append("")
    parts.append(BUNDLE_END_SENTINEL)
    return "\n".join(parts)


def check_size_gate(bundle_bytes: int, target: DeployTarget) -> str | None:
    """該端超 gate 即回報訊息；通過回 None。"""
    if bundle_bytes <= target.max_bytes:
        return None
    return (
        f"[{target.label}] bundle {bundle_bytes:,} bytes exceeds "
        f"{target.max_bytes:,} bytes ({target.max_bytes // 1024}KiB)"
    )


def deploy_all(targets: list[pathlib.Path], bundle: str) -> list[pathlib.Path]:
    """Stage-then-commit 部署，回傳成功替換的 targets。

    被寫入的是 always-on agent policy：單檔用同目錄 temp＋fsync＋os.replace
    保證原子（target 永不出現截斷/partial）；全部 temp 寫完才開始 replace，
    把跨 harness split 窗口壓到 replace 循環內。staging 任一失敗＝全部回滾
    temp、不動任何 target；replace 失敗＝回報該 target、其餘照常（殘餘 split
    由 check_single_source 的 freshness gate 兜底偵測）。
    """
    staged: list[tuple[pathlib.Path, pathlib.Path]] = []
    try:
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and not target.is_symlink():
                existing = target.read_text(encoding="utf-8")
                if "Generated by scripts/deploy_agents.py" not in existing:
                    backup = target.with_suffix(".md.bak")
                    backup.write_text(existing, encoding="utf-8")
                    print(f"  [WARN] backed up {target} -> {backup}")
            tmp = target.with_name(target.name + ".tmp")
            staged.append(
                (tmp, target)
            )  # 先登記再寫——寫入/fsync 失敗時 cleanup 涵蓋本 temp
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(bundle)
                fh.flush()
                os.fsync(fh.fileno())
    except Exception as exc:
        for tmp, _target in staged:
            tmp.unlink(missing_ok=True)
        print(f"  [FAIL] staging: {exc}", file=sys.stderr)
        return []
    deployed: list[pathlib.Path] = []
    for tmp, target in staged:
        try:
            os.replace(tmp, target)
            deployed.append(target)
            print(f"  -> {target}")
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            print(f"  [FAIL] replace {target}: {exc}", file=sys.stderr)
    return deployed


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Deploy bundled AGENTS.md to non-Claude harnesses."
    )
    ap.add_argument(
        "--scope",
        default="neutral",
        help="comma-separated harness-scopes to bundle (default: neutral)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="preview bundle stats without writing (stats only; use `cat` on a deployed target or import build_bundle to inspect content)",
    )
    args = ap.parse_args()

    scope_override = (
        {s.strip() for s in args.scope.split(",")} if args.scope != "neutral" else None
    )

    if not GUIDE.exists():
        print(f"[FAIL] Guide not found: {GUIDE}", file=sys.stderr)
        return 1

    broken = check_broken_refs(RULES_DIR)
    if broken:
        print(
            f"[FAIL] {len(broken)} broken ref(s): bundle sources linking to claude-specific rules:",
            file=sys.stderr,
        )
        for src, target, name in broken:
            print(f"  {src} -> {target} ({name} is claude-specific)", file=sys.stderr)
        print("Fix the ref, or re-scope the target to neutral.", file=sys.stderr)
        return 1

    impure = check_neutral_purity(RULES_DIR)
    if impure:
        print(
            f"[FAIL] {len(impure)} neutral-purity violation(s) "
            "(rules/AGENTS.md 機械檢查清單):",
            file=sys.stderr,
        )
        for rule_name, label, hit in impure:
            print(f"  {rule_name}: [{label}] {hit}", file=sys.stderr)
        print(
            "Neutralize it: move into a (Claude: ...) note, describe the skill "
            "by name, or generalize the path away.",
            file=sys.stderr,
        )
        return 1

    targets = resolve_targets(pathlib.Path.home())
    # partial-deploy 語義（有意）：各端獨立 build＋gate，一端失敗只跳過該端，
    # 其餘端照樣部署；exit code 仍為 1 告警（F4 聲明）。
    ready: list[tuple[DeployTarget, str]] = []
    failed = False
    for target in targets:
        # 自訂 --scope 時 exclude 語義不變（綁 target 非 scope）：muse 端恆為
        # no-mechanics 變體——變體是端點性質，與選了哪些 scope 無關。
        scopes = scope_override or target.scopes
        scopes_label = scopes_label_for(scopes, target.exclude)
        rule_paths = discover_rules(RULES_DIR, scopes)
        if not rule_paths:
            print(f"[FAIL] No rules with scope in {scopes}", file=sys.stderr)
            failed = True
            continue
        bundle = build_bundle(rule_paths, scopes_label, target.exclude)
        # Sentinel integrity is the load-time truncation proof; guard it every run.
        assert bundle.count(BUNDLE_END_SENTINEL) == 1
        assert bundle.rstrip().endswith(BUNDLE_END_SENTINEL)
        bundle_lines = bundle.count("\n") + 1
        bundle_bytes = len(bundle.encode("utf-8"))
        tok_est = bundle_bytes // 3200

        rule_names = [p.name for p in rule_paths if p.name not in target.exclude]
        print(
            f"[OK] [{target.label}] bundle: {len(rule_names)} rules "
            f"(scope={scopes_label}) + guide"
        )
        print(f"     rules: {', '.join(rule_names)}")
        print(
            f"     size: {bundle_lines} lines, {bundle_bytes:,} bytes "
            f"(~{tok_est}K tokens est, "
            f"{bundle_bytes * 100 // target.max_bytes}% of "
            f"{target.max_bytes // 1024}KiB gate)"
        )

        if bundle_bytes >= target.max_bytes * BUNDLE_WARN_RATIO:
            print(
                f"[WARN] [{target.label}] bundle at "
                f"{bundle_bytes * 100 // target.max_bytes}% of "
                f"size gate ({target.max_bytes // 1024}KiB) -- deploy still OK, "
                "but slimming should happen before the gate, not at it "
                "(see rules/AGENTS.md size-gate note)",
                file=sys.stderr,
            )

        gate_msg = check_size_gate(bundle_bytes, target)
        if gate_msg is not None:
            print(f"[FAIL] {gate_msg}", file=sys.stderr)
            print(
                "     Harness lanes truncate (ZCode: 102,400B hard line; "
                "muse: 64KiB shared with project layer). Slim rules/ per "
                "encoder-philosophy, or demote on-demand content to a "
                "reference skill (rule keeps always-on core + pointer; "
                "see rules/AGENTS.md size-gate note).",
                file=sys.stderr,
            )
            failed = True
            continue
        ready.append((target, bundle))

    if args.dry_run:
        print("[DRY-RUN] skipping deploy")
        return 1 if failed else 0

    deployed = 0
    for target, bundle in ready:
        if deploy_all([target.path], bundle) == [target.path]:
            deployed += 1
    if deployed == len(ready) and not failed:
        print(f"[OK] deployed to {deployed}/{len(targets)} non-Claude harnesses")
    else:
        print(
            f"[FAIL] deployed to {deployed}/{len(targets)} non-Claude harnesses",
            file=sys.stderr,
        )
    print(
        "     Claude (~/.claude/CLAUDE.md) untouched -- rules via ~/.claude/rules/ auto-load"
    )
    return 0 if deployed == len(targets) and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
