"""Memory 生命周期工具鏈測試（generator 投影 / MEMORY.md 手寫 gate / Stop 重生成推導）。

三件套行為錨點：索引生成 gate（17,000 字元/24,000 bytes/190 行 fail-loud——雙單位：
harness 上限 24.4KiB 的 chars 與 bytes 兩種讀法都安全）與 frontmatter 解析、手寫攔截
的 self-gating 條件、跨 harness memory 目錄推導——Claude 端底線也轉 dash 的專案名
編碼陷阱與 ZCode 端 basename-sha256 命名皆以本機真實目錄名為錨（hash 是路徑字串的
純函數，跨機器成立）。
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from conftest import REPO_ROOT, load_module

ASSET_REL = "skills/memory-audit/scripts/generate_index.py"
generator = load_module(ASSET_REL)
block_memory = load_module("hooks/block-memory-index-write.py")
regen = load_module("hooks/memory-index-regen.py")

ASSET = REPO_ROOT / ASSET_REL


def make_pool(tmp_path: Path, n: int = 1, desc: str | None = None) -> Path:
    """建 fixture memory 池：裝 generator + n 個合規條目檔（desc 覆寫供 CJK gate 測試）。"""
    gen = tmp_path / "_generate_index.py"
    shutil.copy(ASSET, gen)
    for i in range(n):
        description = desc if desc is not None else f"條目 {i:03d} 描述"
        (tmp_path / f"proj-{i:03d}.md").write_text(
            "---\n"
            f"name: proj-{i:03d}\n"
            f"description: {description}\n"
            "metadata:\n"
            "  type: project\n"
            "---\n"
            "body\n",
            encoding="utf-8",
        )
    return tmp_path


# ---------------------------------------------------------------------------
# generate_index：frontmatter 解析（頂層 type / metadata.type / 引號剝除）
# ---------------------------------------------------------------------------


def test_parse_frontmatter_top_level_type():
    fm = generator.parse_frontmatter(
        "---\ntype: user\nname: a\ndescription: d\n---\nbody"
    )
    assert fm["type"] == "user" and fm["name"] == "a" and fm["description"] == "d"


def test_parse_frontmatter_metadata_type():
    fm = generator.parse_frontmatter(
        "---\nname: a\ndescription: d\nmetadata:\n  type: project\n---\n"
    )
    assert fm["metadata.type"] == "project"


def test_parse_frontmatter_quotes_stripped():
    fm = generator.parse_frontmatter('---\ndescription: "quoted desc"\n---\n')
    assert fm["description"] == "quoted desc"


def test_parse_frontmatter_absent():
    assert generator.parse_frontmatter("no frontmatter here") == {}


# ---------------------------------------------------------------------------
# generate_index：E2E（subprocess 跑部署形態的 script 檔）
# ---------------------------------------------------------------------------


def test_generator_e2e_writes_index(tmp_path):
    pool = make_pool(tmp_path, n=2)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    idx = (pool / "MEMORY.md").read_text(encoding="utf-8")
    assert "proj-000" in idx and "proj-001" in idx
    assert "禁手寫" in idx  # 投影聲明 header
    assert "## Project" in idx


def test_generator_e2e_check_does_not_write(tmp_path):
    pool = make_pool(tmp_path, n=1)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert not (pool / "MEMORY.md").exists()


def test_generator_e2e_gate_fail_loud(tmp_path):
    # 200 條目 → 產物 >190 行 → gate fail-loud：不寫入、exit 1
    pool = make_pool(tmp_path, n=200)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "[FAIL]" in r.stdout
    assert not (pool / "MEMORY.md").exists()


def test_generator_e2e_byte_gate(tmp_path):
    """SM-3：CJK 重池——chars gate 內、bytes 破 24,000 → fail-loud 不寫入。

    70 條 × 130 CJK 字 description：chars ≈ 10,700（<17,000）、bytes ≈ 29,000（>24,000）
    ——bytes 維度是對「harness 以 bytes 計」未證假設的縱深防禦。
    """
    pool = make_pool(tmp_path, n=70, desc="深" * 130)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "bytes" in r.stdout
    assert not (pool / "MEMORY.md").exists()


def test_generator_stale_tmp_aged_removed(tmp_path):
    """SM-8：aged 殘檔（mtime>60s）在寫入模式被清除。"""
    pool = make_pool(tmp_path, n=1)
    stale = pool / "MEMORY.md.999.tmp"
    stale.write_text("debris", encoding="utf-8")
    old = time.time() - 120
    os.utime(stale, (old, old))
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert not stale.exists()


def test_generator_fresh_tmp_not_deleted(tmp_path):
    """R1 回歸鎖：新鮮 tmp（in-flight 模擬）不被 cleanup 誤殺——並行安全。"""
    pool = make_pool(tmp_path, n=1)
    fresh = pool / "MEMORY.md.12345.tmp"
    fresh.write_text("in-flight", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert fresh.exists()


def test_generator_check_mode_no_fs_side_effects(tmp_path):
    """I1：--check 只驗證——連 aged 殘檔都不清、不寫索引。"""
    pool = make_pool(tmp_path, n=1)
    stale = pool / "MEMORY.md.999.tmp"
    stale.write_text("debris", encoding="utf-8")
    old = time.time() - 120
    os.utime(stale, (old, old))
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert stale.exists()
    assert not (pool / "MEMORY.md").exists()


def test_generator_concurrent_smoke(tmp_path):
    """SM-2：兩 process 並行同池——unique tmp 使交錯無害，兩者皆 exit 0。

    行為鎖（修復後確定性通過；修復前固定檔名下為機率性交錯失敗——本測試
    與 fresh-tmp 鎖共同釘住併發語義）。
    """
    pool = make_pool(tmp_path, n=5)
    procs = [
        subprocess.Popen(
            [sys.executable, str(pool / "_generate_index.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(2)
    ]
    outs = [p.communicate() for p in procs]
    assert all(p.returncode == 0 for p in procs), outs
    idx = (pool / "MEMORY.md").read_text(encoding="utf-8")
    assert "proj-004" in idx
    assert not list(pool.glob("MEMORY.md.*.tmp"))


# ---------------------------------------------------------------------------
# block-memory-index-write：手寫攔截 self-gating
# ---------------------------------------------------------------------------


def test_block_memory_violation_with_generator():
    assert block_memory.is_violation("/x/memory/MEMORY.md", True)


def test_block_memory_ok_no_generator():
    """self-gating：同目錄沒裝 generator 的專案不攔（opt-in）。"""
    assert not block_memory.is_violation("/x/memory/MEMORY.md", False)


def test_block_memory_ok_other_file():
    assert not block_memory.is_violation("/x/memory/some-entry.md", True)


def test_block_memory_violation_relative_path():
    assert block_memory.is_violation("MEMORY.md", True)


# ---------------------------------------------------------------------------
# memory-index-regen：跨 harness 目錄推導（本機真實目錄名為錨）
# ---------------------------------------------------------------------------


def test_sha16_anchor_ai_rules():
    # 錨：本機真實目錄 ~/.zcode/cli/memories/projects/ai-rules-01610fbb20315a8b
    assert regen.sha16("/Users/ctai/Github/ai-rules") == "01610fbb20315a8b"


def test_claude_dir_underscore_trap():
    # 錨：Claude 專案名編碼把底線也轉 dash（mosaic_alpha → mosaic-alpha）
    d = regen.claude_memory_dir("/Users/ctai/Github/mosaic_alpha", Path("/H"))
    assert str(d) == "/H/.claude/projects/-Users-ctai-Github-mosaic-alpha/memory"


def test_zcode_dir_underscore_preserved():
    # 錨：ZCode basename 原樣保留底線＋dash＋sha16（對照真實目錄命名）
    d = regen.zcode_memory_dir("/Users/ctai/Github/mosaic_alpha", Path("/H"))
    assert (
        str(d) == "/H/.zcode/cli/memories/projects/mosaic_alpha-91db1aef2f9baec8/memory"
    )


def test_regen_runs_generator_once_with_symlink_dedupe(tmp_path):
    """ZCode 目錄 symlink → Claude 同一實體 pool：resolve() 去重只跑一次。"""
    zdir = regen.zcode_memory_dir("/Users/ctai/Github/ai-rules", tmp_path)
    zdir.mkdir(parents=True)
    make_pool(zdir, n=1)
    cdir = regen.claude_memory_dir("/Users/ctai/Github/ai-rules", tmp_path)
    cdir.parent.mkdir(parents=True)
    cdir.symlink_to(zdir)
    notes = regen.run_for_cwd("/Users/ctai/Github/ai-rules", tmp_path)
    assert len(notes) == 1
    assert (zdir / "MEMORY.md").exists()


def test_regen_skips_pool_without_generator(tmp_path):
    regen.zcode_memory_dir("/x/p", tmp_path).parent.mkdir(parents=True)
    assert regen.run_for_cwd("/x/p", tmp_path) == []


def test_generator_frontmatter_violation_fail_loud(tmp_path):
    """F-1②：frontmatter 違規（缺 type）→ exit 1＋[FAIL] 含檔名＋不寫入。

    fail-loud 三路徑（frontmatter 違規/chars gate/bytes gate）的最後一塊行為錨。
    """
    pool = make_pool(tmp_path, n=1)
    (tmp_path / "bad-entry.md").write_text(
        "---\nname: bad-entry\ndescription: 缺 type\n---\nbody\n", encoding="utf-8"
    )
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "bad-entry.md" in r.stdout
    assert not (pool / "MEMORY.md").exists()


def test_regen_skips_tampered_generator(tmp_path):
    """F2①：池內 generator 與資產源不符 → 跳過執行（防植入持久化執行鏈）。"""
    zdir = regen.zcode_memory_dir("/Users/ctai/Github/ai-rules", tmp_path)
    zdir.mkdir(parents=True)
    make_pool(zdir, n=1)
    (zdir / "_generate_index.py").write_text("# tampered\n", encoding="utf-8")
    notes = regen.run_for_cwd("/Users/ctai/Github/ai-rules", tmp_path)
    assert any("不符" in n for n in notes)
    assert not (zdir / "MEMORY.md").exists()


def test_regen_failure_marker_written_and_cleared(tmp_path):
    """F4①：generator 失敗→`_regen-failed` 標記；下次成功→清除。

    失敗場景用真實形態：generator 與資產 identical，但池內含 frontmatter
    違規條目 → generator 自身 fail-loud exit 1（偽造 failing generator 會被
    F2 的資產比對防護跳過、走不到 marker 路徑）。
    """
    zdir = regen.zcode_memory_dir("/x/proj", tmp_path)
    zdir.mkdir(parents=True)
    make_pool(zdir, n=1)
    bad = zdir / "bad-entry.md"
    bad.write_text("---\nname: bad\ndescription: 缺 type\n---\n", encoding="utf-8")
    regen.run_for_cwd("/x/proj", tmp_path)
    assert (zdir / "_regen-failed").exists()
    bad.unlink()
    regen.run_for_cwd("/x/proj", tmp_path)
    assert not (zdir / "_regen-failed").exists()
    assert (zdir / "MEMORY.md").exists()
