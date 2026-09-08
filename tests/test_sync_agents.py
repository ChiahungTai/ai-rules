"""sync_agents.py 純投影器測試（AIR-29 S2）。

覆蓋：schema/render/check purity/map/add-edit-delete/fork-collision/
adopt-legacy/missing pin/idempotence/target 欄位洩漏負向/parity。
fixture policy 採注入形態（module 常數＝真實 10-role 拓撲，見 test_parity）。
"""

from pathlib import Path

import pytest
from conftest import REPO_ROOT, load_module

sync = load_module("scripts/sync_agents.py")

FIXTURE_REQ = {"t-lite": "lite", "t-vision": "vision", "t-full": "full"}
FIXTURE_LEGACY = {"agents/zcode/t-lite.md", "agents/zcode/t-full.md"}

ROLE_LITE = """---
name: t-lite
description: "lite 測試角色"
tools: Read, Bash, mcp__plugin_code-reality_code-reality__refs
background: true
---

## 目標

測試 lite 投影。

## 做法

- 機械執行
"""

ROLE_VISION = """---
name: t-vision
description: "vision 測試角色"
tools: Read, Bash
---

## 目標

測試 vision 投影。
"""

ROLE_FULL = """---
name: t-full
description: "full 測試角色"
tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, mcp__context7__query-docs, mcp__plugin_code-reality_code-reality__refs
background: true
---

## 目標

測試 full 投影。
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    roles = tmp_path / "agents" / "roles"
    roles.mkdir(parents=True)
    (roles / "t-lite.md").write_text(ROLE_LITE, encoding="utf-8")
    (roles / "t-vision.md").write_text(ROLE_VISION, encoding="utf-8")
    (roles / "t-full.md").write_text(ROLE_FULL, encoding="utf-8")
    (tmp_path / "agents" / "zcode").mkdir()
    (tmp_path / "agents" / "claude").mkdir()
    return tmp_path


def run(repo: Path, mode: str) -> int:
    return sync.main(
        repo, mode=mode, requirements=FIXTURE_REQ, legacy_paths=FIXTURE_LEGACY
    )


def expected(repo: Path) -> dict[Path, str]:
    return sync.expected_projections(repo, requirements=FIXTURE_REQ)


# --- schema / render / exact bytes ---


def test_render_zcode_lite_adds_pins():
    rendered = sync.render_registry("t-lite", ROLE_LITE, "zcode", "lite")
    assert rendered.startswith("---\n")
    assert "model: glm-5.3-flash" in rendered
    assert "thoughtLevel: high" in rendered
    # marker 僅在 closing fence 後（YAML 可解析性不因 marker 破壞）
    head = rendered.split("\n---\n", 1)[0]
    assert head.startswith("---\n")
    assert sync.OWNERSHIP_MARKER not in head
    assert sync.OWNERSHIP_MARKER in rendered.split("\n---\n", 1)[1][:80]
    # zcode 保留 CR MCP 全名
    assert "mcp__plugin_code-reality_code-reality__refs" in rendered


def test_render_zcode_full_pins_flagship():
    rendered = sync.render_registry("t-full", ROLE_FULL, "zcode", "full")
    head = rendered.split("\n---\n")[0]
    # 精確斷言含結尾換行——防 "glm-5.3" ⊂ "glm-5.3-flash" 前綴假綠（EP R4）
    assert "model: glm-5.3\n" in head
    assert "thoughtLevel: high" in head


def test_render_claude_no_target_fields_and_strips_cr_mcp():
    """SM-13 負向：claude 生成物零 model:/thoughtLevel；CR MCP 剝除。"""
    rendered = sync.render_registry("t-full", ROLE_FULL, "claude", "full")
    frontmatter = rendered.split("\n---\n")[0]
    assert "model:" not in frontmatter
    assert "thoughtLevel" not in frontmatter
    assert "mcp__plugin_code-reality_code-reality__" not in rendered
    # 非 CR 的 MCP 全名保留（context7）
    assert "mcp__context7__query-docs" in rendered


def test_render_claude_lite_also_no_pins():
    rendered = sync.render_registry("t-lite", ROLE_LITE, "claude", "lite")
    assert "model:" not in rendered.split("\n---\n")[0]


# --- missing policy key fail loud ---


def test_missing_requirement_fails_loud(repo: Path):
    (repo / "agents" / "roles" / "t-extra.md").write_text(
        ROLE_LITE.replace("t-lite", "t-extra"), encoding="utf-8"
    )
    with pytest.raises(AssertionError):
        expected(repo)


# --- check purity（零寫入 tripwire）---


def _snapshot_tree(root: Path) -> dict[Path, tuple[int, bytes]]:
    snap: dict[Path, tuple[int, bytes]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            snap[path] = (path.stat().st_mtime_ns, path.read_bytes())
    return snap


def test_check_mode_never_writes(repo: Path):
    assert run(repo, "sync") == 0
    before = _snapshot_tree(repo)
    exit_code = run(repo, "check")
    assert exit_code == 0
    assert _snapshot_tree(repo) == before  # mtime+content tripwire


def test_check_reports_drift_nonzero_without_write(repo: Path):
    (repo / "agents" / "zcode" / "t-lite.md").write_text(
        "hand-edited", encoding="utf-8"
    )
    before = _snapshot_tree(repo)
    exit_code = run(repo, "check")
    assert exit_code == 1
    assert _snapshot_tree(repo) == before


# --- map ---


def test_map_fixed_columns_and_sorted_roles(repo: Path):
    table = sync.render_map(expected(repo), requirements=FIXTURE_REQ)
    lines = table.splitlines()
    assert lines[0] == "role\trequirement\tzcode\tclaude"
    roles = [line.split("\t")[0] for line in lines[1:]]
    assert roles == sorted(roles)
    reqs = {line.split("\t")[0]: line.split("\t")[1] for line in lines[1:]}
    assert reqs == FIXTURE_REQ


# --- sync / idempotence / add-edit-delete ---


def test_sync_then_check_green_and_idempotent(repo: Path):
    assert run(repo, "sync") == 0
    zcode = repo / "agents" / "zcode"
    claude = repo / "agents" / "claude"
    assert len(list(zcode.glob("*.md"))) == 3
    assert len(list(claude.glob("*.md"))) == 3
    assert run(repo, "check") == 0
    before = _snapshot_tree(repo)
    assert run(repo, "sync") == 0  # second run no diff
    assert _snapshot_tree(repo) == before


def test_edit_role_body_produces_drift_then_resync(repo: Path):
    assert run(repo, "sync") == 0
    body = (repo / "agents" / "roles" / "t-lite.md").read_text(encoding="utf-8")
    (repo / "agents" / "roles" / "t-lite.md").write_text(
        body + "\n新增一行\n", encoding="utf-8"
    )
    assert run(repo, "check") == 1
    assert run(repo, "sync") == 0
    assert run(repo, "check") == 0


def test_delete_role_cleans_marker_owned_only(repo: Path):
    assert run(repo, "sync") == 0
    # unmarked fork（人工檔）必須保留
    fork = repo / "agents" / "zcode" / "manual-fork.md"
    fork.write_text("---\nname: manual-fork\n---\nbody\n", encoding="utf-8")
    # 刪 role＝刪檔＋刪 policy（單側刪除被 mismatch fail loud 擋——exit 2）
    (repo / "agents" / "roles" / "t-vision.md").unlink()
    assert run(repo, "sync") == 2  # policy 仍含 t-vision → fatal
    reduced = {k: v for k, v in FIXTURE_REQ.items() if k != "t-vision"}
    assert (
        sync.main(repo, mode="sync", requirements=reduced, legacy_paths=FIXTURE_LEGACY)
        == 0
    )
    assert not (repo / "agents" / "zcode" / "t-vision.md").exists()
    assert not (repo / "agents" / "claude" / "t-vision.md").exists()
    assert fork.exists()  # stale cleanup 只刪 marker-owned


# --- fork / collision ---


def test_unmarked_same_name_file_blocks_sync(repo: Path):
    (repo / "agents" / "zcode" / "t-lite.md").write_text(
        "---\nname: t-lite\n---\n任何內容\n", encoding="utf-8"
    )
    with pytest.raises(AssertionError):
        run(repo, "sync")


def test_exact_equal_unmarked_fork_still_blocks_default_sync(repo: Path):
    """F3-05：exact-byte 相等不能讓 default sync 靜默收編人工 fork。"""
    exp = expected(repo)
    target = repo / "agents" / "zcode" / "t-lite.md"
    target.write_text(
        exp[target].replace(sync.OWNERSHIP_MARKER + "\n", "", 1),
        encoding="utf-8",
    )
    with pytest.raises(AssertionError):
        run(repo, "sync")


# --- adopt-legacy ---


def test_adopt_legacy_exact_paths_only(repo: Path):
    exp = expected(repo)
    for rel in sorted(FIXTURE_LEGACY):
        target = repo / rel
        target.write_text(
            exp[target].replace(sync.OWNERSHIP_MARKER + "\n", "", 1),
            encoding="utf-8",
        )
    assert run(repo, "adopt-legacy") == 0
    assert run(repo, "check") == 0


def test_adopt_legacy_rejects_divergent_bytes(repo: Path):
    (repo / "agents" / "zcode" / "t-lite.md").write_text(
        "---\nname: t-lite\n---\ndivergent\n", encoding="utf-8"
    )
    with pytest.raises(AssertionError):
        run(repo, "adopt-legacy")


# --- parity（真 repo）：sync_agents dict ↔ model-routing skill 表 ---


def test_parity_with_model_routing_skill_tables():
    drift = sync.check_parity(REPO_ROOT)
    assert drift == [], f"parity drift: {drift}"


def test_parity_pin_value_layer_fails_on_model_change(tmp_path: Path):
    """值層 parity（F1/U-1）：skill zai 欄改 model 而 dict 未跟 → fail。"""
    skill = tmp_path / "skills" / "model-routing" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    real = (REPO_ROOT / sync.PARITY_SOURCE).read_text(encoding="utf-8")
    skill.write_text(
        real.replace(
            "| **lite**（一般） | glm-5.3-flash", "| **lite**（一般） | glm-6.0-flash"
        ),
        encoding="utf-8",
    )
    drift = sync.check_parity(tmp_path)
    assert any("ZCODE_PINS[lite]" in d for d in drift), drift


def test_parity_pin_value_layer_fails_on_full_model_change(tmp_path: Path):
    """值層 parity full 變體（SM-3）：skill 權威表 full 行改 model 而 dict 未跟 → fail。"""
    skill = tmp_path / "skills" / "model-routing" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    real = (REPO_ROOT / sync.PARITY_SOURCE).read_text(encoding="utf-8")
    skill.write_text(
        real.replace(
            "| **full**（旗艦） | `glm-5.3`（旗艦釘選，AIR-43——inherit 洞修補）",
            "| **full**（旗艦） | `glm-6.0`（旗艦釘選，AIR-43——inherit 洞修補）",
        ),
        encoding="utf-8",
    )
    drift = sync.check_parity(tmp_path)
    assert any("ZCODE_PINS[full]" in d for d in drift), drift


def test_parity_unparseable_zai_cell_fails_loud(tmp_path: Path):
    """SM-4 分支釘住（F1）：full 行 zai 欄非反引號 id 開頭（舊 inherit 敘述形態）
    → 「有值但未解析到」分支 fail loud（此分支先前零測試覆蓋）。"""
    skill = tmp_path / "skills" / "model-routing" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    real = (REPO_ROOT / sync.PARITY_SOURCE).read_text(encoding="utf-8")
    skill.write_text(
        real.replace(
            "`glm-5.3`（旗艦釘選，AIR-43——inherit 洞修補）",
            "GLM 5.3＝主 session inherit（不釘 id）",
        ),
        encoding="utf-8",
    )
    drift = sync.check_parity(tmp_path)
    assert any(
        "ZCODE_PINS[full] 有值但 skill 權威表 zai 欄未解析到" in d for d in drift
    ), drift


def test_parity_effort_layer_fails_on_thought_level_change(tmp_path: Path):
    """muse F2：部署填法表 effort 改而 dict 未跟 → fail。"""
    skill = tmp_path / "skills" / "model-routing" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    real = (REPO_ROOT / sync.PARITY_SOURCE).read_text(encoding="utf-8")
    skill.write_text(
        real.replace("thoughtLevel: high", "thoughtLevel: max"), encoding="utf-8"
    )
    drift = sync.check_parity(tmp_path)
    assert any("thoughtLevel" in d for d in drift), drift


def test_zai_pin_parser_ignores_lines_outside_tier_section(tmp_path: Path):
    """muse F3：權威表段落外的同形行不得覆蓋 pins。"""
    text = (
        "## 前言\n| **lite**（誘餌） | fake-model |\n\n"
        "## tier → (model, effort) 解析表（requirement × provider 權威表——model 值單一源）\n"
        "| tier（requirement） | zai | Anthropic |\n"
        "|---|---|---|\n"
        # full 行貼真實表格行全文（M5——非簡化縮影）；cell 以 backtick id 開頭（D2 規約）
        "| **full**（旗艦） | `glm-5.3`（旗艦釘選，AIR-43——inherit 洞修補）〔repo-observed；registry pin wire 首例 first-real-usage-pending→S3 後改 repo-observed〕 | opus〔**未訂閱禁派**〕 | sol high／max〔**預設不派**——額度最少〕 | fabel〔**未訂閱禁派**〕 | muse-spark-1.3（effort xhigh 起） |\n"
        "| **vision**（影像） | glm-5.3-flash（多模✓） | x |\n"
        "| **lite**（一般） | glm-5.3-flash〔repo-observed〕 | x |\n"
        "\n## 後記\n| **vision**（誘餌） | phantom-model |\n"
    )
    pins = sync.parse_skill_zai_pins(text)
    assert pins == {
        "full": "glm-5.3",
        "lite": "glm-5.3-flash",
        "vision": "glm-5.3-flash",
    }


def test_main_fatal_exits_2_not_1(repo: Path):
    """muse F1：parity/mismatch fatal 的 exit 語義與 drift（1）分離——checker 據此分級。"""
    (repo / "agents" / "roles" / "t-ghost.md").write_text(ROLE_LITE, encoding="utf-8")
    rc = run(repo, "check")  # fixture policy 缺 t-ghost → mismatch
    assert rc == 2


def test_main_check_parity_source_missing_exits_3(repo: Path, monkeypatch):
    """codex 09-06 審查 S-4：parity source 缺席＋投影一致 → exit 3（未驗證），非假綠 0。"""
    assert (
        run(repo, "sync") == 0
    )  # 先投影（fixture requirements 注入，不走 parity 路徑）
    monkeypatch.setattr(sync, "ROLE_REQUIREMENTS", FIXTURE_REQ)
    rc = sync.main(repo, mode="check")  # requirements=None 且 tmp repo 無 PARITY_SOURCE
    assert rc == 3


def test_parse_role_requirements_ignores_lines_outside_section():
    """C-3/F7：分配表段落外的同形行不得注入幻影 role。"""
    text = (
        "## 前言\n| lite | see also foo, bar |\n\n"
        "## role → requirement（tier）分配表\n| full | code-reviewer |\n\n"
        "## 後記\n| lite | another, phantom |\n"
    )
    table = sync.parse_skill_role_requirements(text)
    assert table == {"code-reviewer": "full"}


def test_split_frontmatter_reports_distinct_errors():
    """C-4：BOM／缺 frontmatter／未閉合／空 frontmatter／非法鍵分別報。"""
    with pytest.raises(AssertionError, match="BOM"):
        sync.split_frontmatter("t", "\ufeff---\nname: t\n---\nbody")
    with pytest.raises(AssertionError, match="缺 frontmatter"):
        sync.split_frontmatter("t", "name: t\n")
    with pytest.raises(AssertionError, match="未閉合"):
        sync.split_frontmatter("t", "---\nname: t\n")
    with pytest.raises(AssertionError, match="為空"):
        sync.split_frontmatter("t", "---\n---\nbody")
    with pytest.raises(AssertionError, match="白名單"):
        sync.split_frontmatter("t", "---\nname: t\nmodel: x\n---\nbody")


def test_claude_projection_all_cr_tools_fails_loud():
    """C-5：源 tools 只剩 CR MCP 全名時，claude 投影 fail 而非輸出空清單。"""
    role = ROLE_LITE.replace(
        "tools: Read, Bash, mcp__plugin_code-reality_code-reality__refs",
        "tools: mcp__plugin_code-reality_code-reality__refs",
    )
    with pytest.raises(AssertionError, match="tools 全空"):
        sync.render_registry("t-lite", role, "claude", "lite")


def test_map_reflects_disk_state_not_policy(repo: Path):
    """F2：map 的 registry 欄反映磁碟（owned）——手刪生成檔後該欄 no。"""
    exp = expected(repo)
    assert run(repo, "sync") == 0
    owned = sync.inventory_owned_outputs(repo)
    full_map = sync.render_map(exp, requirements=FIXTURE_REQ, owned=owned)
    assert "t-lite\tlite\tyes\tyes" in full_map
    (repo / "agents" / "zcode" / "t-lite.md").unlink()
    owned = sync.inventory_owned_outputs(repo)
    after = sync.render_map(exp, requirements=FIXTURE_REQ, owned=owned)
    assert "t-lite\tlite\tno\tyes" in after


def test_atomic_write_leaves_no_partial_file_on_error(repo: Path, monkeypatch):
    """C-1：寫入中途失敗不留半損檔（tmp 清除、原檔不動）。"""
    target = repo / "agents" / "zcode" / "t-lite.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("original", encoding="utf-8")

    def boom(*args, **kwargs):
        raise RuntimeError("disk full")

    monkeypatch.setattr(sync.tempfile, "mkstemp", boom)
    with pytest.raises(RuntimeError):
        sync.atomic_write(target, "new content")
    assert target.read_text(encoding="utf-8") == "original"
    assert list(target.parent.glob(".*.tmp")) == []


# --- 真樹 snapshot（U-8）：10-role 集合與每名唯一 requirement 入庫釘住 ---


def test_real_tree_map_snapshot():
    exp = sync.expected_projections(REPO_ROOT)
    owned = sync.inventory_owned_outputs(REPO_ROOT)
    table = sync.render_map(exp, owned=owned)
    lines = table.splitlines()
    roles = {line.split("\t")[0]: line.split("\t")[1] for line in lines[1:]}
    assert roles == sync.ROLE_REQUIREMENTS
    assert len(roles) == 10
    assert all(
        line.split("\t")[2] == "yes" and line.split("\t")[3] == "yes"
        for line in lines[1:]
    )


# --- golden bytes（C-6）：全文手寫錨——獨立於被測 render ---


def test_render_golden_bytes_full_role():
    role = (
        "---\n"
        "name: golden\n"
        'description: "golden anchor"\n'
        "tools: Read, Bash\n"
        "background: true\n"
        "---\n"
        "\n## 目標\n\nanchor body。\n"
    )
    zcode = sync.render_registry("golden", role, "zcode", "lite")
    assert zcode == (
        "---\n"
        "name: golden\n"
        'description: "golden anchor"\n'
        "tools: Read, Bash\n"
        "background: true\n"
        "model: glm-5.3-flash\n"
        "thoughtLevel: high\n"
        "---\n"
        f"{sync.OWNERSHIP_MARKER}\n"
        "\n## 目標\n\nanchor body。\n"
    )
    claude = sync.render_registry("golden", role, "claude", "full")
    assert claude == (
        "---\n"
        "name: golden\n"
        'description: "golden anchor"\n'
        "tools: Read, Bash\n"
        "background: true\n"
        "---\n"
        f"{sync.OWNERSHIP_MARKER}\n"
        "\n## 目標\n\nanchor body。\n"
    )


def test_render_golden_bytes_full_role_pins():
    """golden bytes：zcode full 生成形態（AIR-43 釘選——model: glm-5.3＋thoughtLevel: high）；
    claude 對照不變（D4——CC 端零 model/thoughtLevel）。"""
    role = (
        "---\n"
        "name: golden-full\n"
        'description: "golden full anchor"\n'
        "tools: Read, Bash\n"
        "background: true\n"
        "---\n"
        "\n## 目標\n\nanchor body。\n"
    )
    zcode = sync.render_registry("golden-full", role, "zcode", "full")
    assert zcode == (
        "---\n"
        "name: golden-full\n"
        'description: "golden full anchor"\n'
        "tools: Read, Bash\n"
        "background: true\n"
        "model: glm-5.3\n"
        "thoughtLevel: high\n"
        "---\n"
        f"{sync.OWNERSHIP_MARKER}\n"
        "\n## 目標\n\nanchor body。\n"
    )
    claude = sync.render_registry("golden-full", role, "claude", "full")
    assert claude == (
        "---\n"
        "name: golden-full\n"
        'description: "golden full anchor"\n'
        "tools: Read, Bash\n"
        "background: true\n"
        "---\n"
        f"{sync.OWNERSHIP_MARKER}\n"
        "\n## 目標\n\nanchor body。\n"
    )
