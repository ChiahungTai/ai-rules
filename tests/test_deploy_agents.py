"""deploy_agents 治理閘門單元測試（T1-2）。

這些閘門管四家 harness 的部署行為——靜默 regression = 全體系失效無人知
（F9：2026-08-30 前本 repo 9 個 .py、0 個測試）。
"""

import os

from conftest import load_module

da = load_module("scripts/deploy_agents.py")


def _rule(tmp_path, name: str, scope: str | None, body: str = ""):
    front = f"---\nharness-scope: {scope}\n---\n" if scope else ""
    p = tmp_path / name
    p.write_text(front + body, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# read_scope：frontmatter 解析
# ---------------------------------------------------------------------------


def test_read_scope_default_neutral(tmp_path):
    p = _rule(tmp_path, "bare.md", None, "# no frontmatter\n")
    assert da.read_scope(p) == "neutral"


def test_read_scope_explicit(tmp_path):
    assert da.read_scope(_rule(tmp_path, "a.md", "claude-specific")) == (
        "claude-specific"
    )
    assert da.read_scope(_rule(tmp_path, "b.md", "meta")) == "meta"


def test_read_scope_stops_at_closing_fence(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("---\nother: 1\n---\nharness-scope: meta\n", encoding="utf-8")
    assert da.read_scope(p) == "neutral"  # fence 後的不算 frontmatter


# ---------------------------------------------------------------------------
# CLAUDE_NOTE_PATTERN：括號注剝除（ASCII/全形/單層巢狀）
# ---------------------------------------------------------------------------


def test_claude_note_ascii():
    cleaned = da.CLAUDE_NOTE_PATTERN.sub("", "see (Claude: `../skills/x.md`) end")
    assert "../skills/x.md" not in cleaned
    assert "see" in cleaned and "end" in cleaned


def test_claude_note_fullwidth():
    cleaned = da.CLAUDE_NOTE_PATTERN.sub("", "見（Claude：路徑）完")
    assert "路徑" not in cleaned
    assert "見" in cleaned and "完" in cleaned


def test_claude_note_nested_parens():
    cleaned = da.CLAUDE_NOTE_PATTERN.sub("", "a (Claude: [x](../skills/y.md)) b")
    assert "../skills/y.md" not in cleaned
    assert "a" in cleaned and "b" in cleaned


def test_claude_note_requires_colon():
    # 「（Claude 端 ...）」無冒號 → 不是豁免注，不剝
    cleaned = da.CLAUDE_NOTE_PATTERN.sub("", "（Claude 端 rule）")
    assert "Claude 端 rule" in cleaned


# ---------------------------------------------------------------------------
# slim_for_bundle：skip marker
# ---------------------------------------------------------------------------


def test_slim_strips_marked_section():
    content = "a\n<!-- bundle: skip-start -->\nsecret\n<!-- bundle: skip-end -->\nb"
    out = da.slim_for_bundle(content, "r.md")
    assert "secret" not in out
    assert "a" in out and "b" in out


def test_slim_noop_without_markers():
    content = "plain\n"
    assert da.slim_for_bundle(content, "r.md") == content


# ---------------------------------------------------------------------------
# check_broken_refs：neutral→claude-specific 死連結（rules + guide）
# ---------------------------------------------------------------------------


def test_broken_ref_rule_to_claude_specific(tmp_path):
    _rule(tmp_path, "target.md", "claude-specific")
    _rule(tmp_path, "src.md", "neutral", "see [t](target.md)\n")
    broken = da.check_broken_refs(tmp_path)
    assert broken == [("src.md", "target.md", "target")]


def test_broken_ref_exempt_in_claude_note(tmp_path):
    _rule(tmp_path, "target.md", "claude-specific")
    _rule(tmp_path, "src.md", "neutral", "see (Claude: [t](target.md))\n")
    assert da.check_broken_refs(tmp_path) == []


def test_broken_ref_scans_guide(tmp_path, monkeypatch):
    rules = tmp_path / "rules"
    rules.mkdir()
    _rule(rules, "target.md", "claude-specific")
    guide = tmp_path / "guide.md"
    guide.write_text("詳見 `target.md`（範例）\n", encoding="utf-8")
    monkeypatch.setattr(da, "GUIDE", guide)
    broken = da.check_broken_refs(rules)
    assert ("guide.md", "target.md", "target") in broken


# ---------------------------------------------------------------------------
# check_neutral_purity：rules/AGENTS.md 機械檢查清單的程式化（F4）
# ---------------------------------------------------------------------------


def test_purity_cross_domain_path(tmp_path):
    _rule(tmp_path, "r.md", "neutral", "見 [s](../skills/x/SKILL.md)\n")
    hits = da.check_neutral_purity(tmp_path)
    assert any(label == "cross-domain-path" for _, label, _ in hits)


def test_purity_cross_domain_exempt_in_claude_note(tmp_path):
    _rule(
        tmp_path,
        "r.md",
        "neutral",
        "見 state-md-write（Claude: `../skills/_common/x.md`）\n",
    )
    assert da.check_neutral_purity(tmp_path) == []


def test_purity_bare_slash_command(tmp_path):
    _rule(tmp_path, "r.md", "neutral", "用 `/sync-sources` 檢查\n")
    assert any(
        label == "bare-slash-command"
        for _, label, _ in da.check_neutral_purity(tmp_path)
    )


def test_purity_at_transclusion(tmp_path):
    _rule(tmp_path, "r.md", "neutral", "載入 @~/x.md 或 @../y.md\n")
    hits = da.check_neutral_purity(tmp_path)
    assert any(label == "at-transclusion" for _, label, _ in hits)


def test_purity_abs_user_path(tmp_path):
    _rule(tmp_path, "r.md", "neutral", "在 ~/Github/ai-rules/ 底下\n")
    assert any(
        label == "abs-user-path" for _, label, _ in da.check_neutral_purity(tmp_path)
    )


def test_purity_claude_wrapper_annotation(tmp_path):
    _rule(tmp_path, "ok.md", "neutral", "CLAUDE.md wrapper（Claude 端才有）\n")
    _rule(tmp_path, "bad.md", "neutral", "記得 CLAUDE.md wrapper 同步\n")
    hits = da.check_neutral_purity(tmp_path)
    assert any(
        label == "claude-wrapper-unannotated" and name == "bad.md"
        for name, label, _ in hits
    )


def test_purity_guide_not_scanned(tmp_path, monkeypatch):
    # guide 合法提及跨 harness 裸 slash（/handoff）——purity 掃描範圍限 rules
    rules = tmp_path / "rules"
    rules.mkdir()
    guide = tmp_path / "guide.md"
    guide.write_text("跨 session：`/handoff`\n", encoding="utf-8")
    monkeypatch.setattr(da, "GUIDE", guide)
    assert da.check_neutral_purity(rules) == []


# ---------------------------------------------------------------------------
# deploy_all：staged atomic 部署（codex 09-06 審查 I-2——unlink+write_text 非
# 原子，中斷可留截斷檔；逐 target catch 續行可讓三 harness policy split）
# ---------------------------------------------------------------------------


def test_deploy_all_stage_failure_leaves_targets_untouched(tmp_path, monkeypatch):
    t1, t2 = tmp_path / "a.md", tmp_path / "b.md"
    t1.write_text("OLD1", encoding="utf-8")
    t2.write_text("OLD2", encoding="utf-8")
    calls = {"n": 0}
    real_fsync = os.fsync

    def flaky_fsync(fd):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("disk full (injected)")
        real_fsync(fd)

    monkeypatch.setattr(da.os, "fsync", flaky_fsync)
    deployed = da.deploy_all([t1, t2], "NEW")
    assert deployed == []
    assert t1.read_text(encoding="utf-8") == "OLD1"  # staging 失敗＝沒有 target 被動
    assert t2.read_text(encoding="utf-8") == "OLD2"
    assert not list(tmp_path.glob("*.tmp"))  # temp 全清


def test_deploy_all_replace_failure_never_truncates(tmp_path, monkeypatch):
    t1, t2 = tmp_path / "a.md", tmp_path / "b.md"
    t1.write_text("OLD1", encoding="utf-8")
    t2.write_text("OLD2", encoding="utf-8")
    real_replace = os.replace

    def flaky_replace(src, dst):
        if dst == t2:
            raise OSError("replace injected failure")
        real_replace(src, dst)

    monkeypatch.setattr(da.os, "replace", flaky_replace)
    deployed = da.deploy_all([t1, t2], "NEW")
    assert deployed == [t1]
    assert t1.read_text(encoding="utf-8") == "NEW"
    assert t2.read_text(encoding="utf-8") == "OLD2"  # 舊完整版，絕非截斷/partial
    assert not list(tmp_path.glob("*.tmp"))


def test_deploy_all_success_and_backup_of_foreign_file(tmp_path):
    t1 = tmp_path / "a.md"
    t1.write_text("user managed, no marker", encoding="utf-8")
    deployed = da.deploy_all([t1], "Generated by scripts/deploy_agents.py\nNEW")
    assert deployed == [t1]
    assert t1.read_text(encoding="utf-8").endswith("NEW")
    assert (tmp_path / "a.md.bak").read_text(encoding="utf-8") == (
        "user managed, no marker"
    )


# ---------------------------------------------------------------------------
# per-target 配置：muse 變體（draft-3 A案，S3）＋各端獨立 size gate
# ---------------------------------------------------------------------------


def test_muse_variant_excludes_mechanics_only(tmp_path):
    targets = {t.label: t for t in da.resolve_targets(tmp_path)}
    assert set(targets) == {"zcode", "codex", "muse"}
    assert targets["zcode"].exclude == frozenset()
    assert targets["codex"].exclude == frozenset()
    assert targets["muse"].exclude == da.MUSE_MECHANICS_EXCLUDE
    # 非 muse 端 gate 不動（既有 90KiB 語義）
    assert targets["zcode"].max_bytes == da.BUNDLE_MAX_BYTES
    assert targets["codex"].max_bytes == da.BUNDLE_MAX_BYTES
    # muse 端獨立 gate（ai-rules 工作區 lane 約 51.9KB，取 50KiB 對齊 S3）
    assert targets["muse"].max_bytes == 50 * 1024


def test_muse_exclude_pinned_to_existing_rules():
    # 改名/刪除被排除檔時大聲失敗，不靜默改變變體語義
    for name in da.MUSE_MECHANICS_EXCLUDE:
        assert (da.RULES_DIR / name).exists(), f"excluded rule gone: {name}"
        assert da.read_scope(da.RULES_DIR / name) == "neutral"


def test_build_bundle_respects_exclude(tmp_path):
    a = _rule(tmp_path, "keep.md", "neutral", "# keep\n")
    b = _rule(tmp_path, "drop.md", "neutral", "# drop\n")
    bundle = da.build_bundle([a, b], "neutral", exclude=frozenset({"drop.md"}))
    assert "# keep" in bundle
    assert "# drop" not in bundle
    assert bundle.rstrip().endswith(da.BUNDLE_END_SENTINEL)


def test_check_size_gate_per_target(tmp_path):
    targets = {t.label: t for t in da.resolve_targets(tmp_path)}
    assert da.check_size_gate(10, targets["muse"]) is None
    over = da.check_size_gate(targets["muse"].max_bytes + 1, targets["muse"])
    assert over is not None and "muse" in over
    # 同一尺寸在 90KiB 端通過
    assert da.check_size_gate(targets["muse"].max_bytes + 1, targets["zcode"]) is None
