"""Memory 生命周期工具鏈測試（generator 投影 / MEMORY.md 手寫 gate / Stop 重生成推導）。

三件套行為錨點：索引生成 gate 分級（22,500 字元/190 行 fail-loud——09-05 S1（AIR-25）
CC 式：超限**索引照寫出**＋exit 1＋行動訊息（官方 memory.md:401-403「write still
succeeds + error telling Claude to rewrite」——拒寫會停滯索引＝新條目不可見＝召回斷裂；
`--check` 仍不寫）與 frontmatter 解析、手寫攔截
＋條目寫入治理（desc>100/body 膨脹>12,000 硬擋、收斂放行）的 self-gating 條件、
跨 harness memory 目錄推導——Claude 端底線也轉 dash 的專案名
編碼陷阱與 ZCode 端 basename-sha256 命名皆以本機真實目錄名為錨（hash 是路徑字串的
純函數，跨機器成立）。
"""

import json
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
    """SM-1：超限（n=200 > 190 行 gate）→ 索引**照寫出**＋exit 1＋行動訊息。

    09-05 S1（AIR-25）gate 失敗模式改 CC 式：拒寫會讓索引停滯、新條目對未來
    session 不可見（召回斷裂，flash-forensic 條目實證）——寫出（投影新鮮）＋
    fail-loud 行動訊息（命令當下 session 縮池）才是正確失敗模式。
    """
    pool = make_pool(tmp_path, n=200)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "[FAIL]" in r.stdout
    assert "merge or drop" in r.stdout  # 行動訊息（官方 error telling to rewrite）
    idx_path = pool / "MEMORY.md"
    assert idx_path.exists()  # 照寫出——不停滯
    assert "proj-199" in idx_path.read_text(encoding="utf-8")  # 完整索引（尾條目在場）


def test_generator_e2e_over_limit_check_does_not_write(tmp_path):
    """SM-2：超限時 --check 仍不寫入——寫出動作須 `if not check_only` guard。

    超限 gate 分支在 check_only 分支之前（共用 return 1 路徑），無 guard 照字面
    實作會讓 --check 也寫入＝違反其零副作用語義（既有 check_does_not_write
    是未超限 case，此處釘超限邊界）。
    """
    pool = make_pool(tmp_path, n=200)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "[FAIL]" in r.stdout
    assert not (pool / "MEMORY.md").exists()


def test_generator_e2e_byte_gate(tmp_path):
    """SM-3：CJK 重池——chars/lines gate 內、bytes 破 24,000 → info 縱深預警不擋寫入。

    80 條 × 130 CJK 字 description：chars ≈ 10,418（<22,500）、bytes ≈ 26,464（>24,000）
    ——bytes 非任何端實際截斷線（兩端皆 25,000 chars、量 UTF-16 length）；info 為
    縱深預警（CJK 一字 3B 提前折射），ZCode 主力場景照常寫入（2026-09-03 裁決「zcode 優先」）。
    """
    pool = make_pool(tmp_path, n=80, desc="深" * 130)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "[INFO]" in r.stdout
    assert "25,000 chars" in r.stdout
    assert (pool / "MEMORY.md").exists()


def test_generator_e2e_chars_gate(tmp_path):
    """SM-9：chars gate 邊界——chars 破 22,500 而 lines 未超 → fail-loud（chars 路徑錨）。

    178 條 × desc 130 CJK（截 100）：chars ≈ 23,060（>22,500）、lines = 184（<190）
    ——gate_fail_loud（n=200）兩 gate 皆破，chars-only 邊界由本測試釘住：gate 值 typo 或
    再調整（09-03 18,500→22,500）時有紅燈保護。
    """
    pool = make_pool(tmp_path, n=178, desc="深" * 130)
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1
    assert "[FAIL]" in r.stdout
    assert "chars" in r.stdout
    assert (pool / "MEMORY.md").exists()  # S1：chars-only 超限同樣照寫出（不停滯）


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
    assert block_memory.is_index_violation("/x/memory/MEMORY.md", True)


def test_block_memory_ok_no_generator():
    """self-gating：同目錄沒裝 generator 的專案不攔（opt-in）。"""
    assert not block_memory.is_index_violation("/x/memory/MEMORY.md", False)


def test_block_memory_ok_other_file():
    assert not block_memory.is_index_violation("/x/memory/some-entry.md", True)


def test_block_memory_violation_relative_path():
    assert block_memory.is_index_violation("MEMORY.md", True)


# ---------------------------------------------------------------------------
# block-memory-index-write：條目寫入治理（subprocess 餵 stdin JSON——hook 真實形態）
# ---------------------------------------------------------------------------

HOOK = REPO_ROOT / "hooks" / "block-memory-index-write.py"


def run_hook(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def hook_payload(tool: str, file_path: Path, **kw) -> dict:
    ti = {"file_path": str(file_path)}
    ti.update(kw)
    return {"tool_name": tool, "tool_input": ti}


def test_entry_write_desc_overlong_blocked(tmp_path):
    """desc 130 chars（>100）→ exit 2；語義：索引行原料超額在寫入端擋。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "fat-desc.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: fat-desc\ndescription: "
            + "長" * 130
            + "\nmetadata:\n  type: project\n---\nbody\n",
        )
    )
    assert r.returncode == 2
    assert "description" in r.stderr


def test_entry_write_body_overlimit_blocked(tmp_path):
    """既有條目 Write 覆寫 13,000 chars（>12,000，desc 合規）→ exit 2——膨脹治理管既有檔；
    新建檔的等價場景由新建閘（3,000）先攔，見 test_entry_write_new_entry_overlimit_blocked。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "fat-body.md"
    target.write_text(
        "---\nname: fat-body\ndescription: 合規短述\nmetadata:\n  type: project\n---\n"
        + "x" * 11_000,
        encoding="utf-8",
    )
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: fat-body\ndescription: 合規短述\nmetadata:\n  type: project\n---\n"
            + "x" * 13_000,
        )
    )
    assert r.returncode == 2
    assert "12,000" in r.stderr


def test_entry_write_within_limits_allowed(tmp_path):
    """合規 Write（desc 短、body <12,000）→ exit 0。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "ok-entry.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: ok-entry\ndescription: 合規短述\nmetadata:\n  type: project\n---\nbody\n",
        )
    )
    assert r.returncode == 0


def test_entry_write_new_entry_overlimit_blocked(tmp_path):
    """新建條目（target 不存在）content >3,000 → exit 2——寫入當下即蒸後形。

    09-06 user 拍板「不要寫一堆廢話後來再 audit」：新條目直寫敘事流水
    （timeline/過程/commit 清單）是池膨脹主入口——12K 膨脹治理對 cur=0 的
    新建檔案無約束力，此閘補真空。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "new-fat-entry.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: new-fat-entry\ndescription: 合規短述\nmetadata:\n  type: project\n---\n"
            + "y" * 3_500,
        )
    )
    assert r.returncode == 2
    assert "3,000" in r.stderr


def test_entry_rewrite_existing_not_new_entry_gate(tmp_path):
    """既有條目 Write 覆寫（cluster merge 收斂/維護場景，cur>0）不走新建閘——仍走 12K 膨脹治理。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "existing-entry.md"
    target.write_text(
        "---\nname: existing-entry\ndescription: 合規短述\nmetadata:\n  type: project\n---\n"
        + "z" * 4_500,
        encoding="utf-8",
    )
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: existing-entry\ndescription: 合規短述\nmetadata:\n  type: project\n---\n"
            + "z" * 5_000,
        )
    )
    assert r.returncode == 0


def test_entry_write_desc_commit_hash_blocked(tmp_path):
    """SM-3/SM-4（09-05 S2/AIR-25）：desc 含 commit hash（≤100 chars）→ exit 2
    ——內容契約獨立於長度契約；hash 屬 git log 可推導（官方 skip-derivable）。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "hash-desc.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content=(
                "---\nname: hash-desc\ndescription: 全弧完結含 commit 47aa89d 收案\n"
                "metadata:\n  type: project\n---\nbody\n"
            ),
        )
    )
    assert r.returncode == 2
    assert "hash" in r.stderr


def test_entry_write_body_hash_allowed(tmp_path):
    """反向：desc 合規、body 引 hash（歷史合法引用）→ exit 0——契約只約束 desc。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "body-hash.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content=(
                "---\nname: body-hash\ndescription: 合規短述\nmetadata:\n  type: project\n"
                "---\n落地於 commit 47aa89d，細節見 EP。\n"
            ),
        )
    )
    assert r.returncode == 0


def test_entry_edit_desc_commit_hash_blocked(tmp_path):
    """Edit 分支 desc hash 檢查（review F2）——new_string 含 description: 行帶
    commit hash → exit 2（與 Write 分支同契約；釘住 `desc and` guard 不被誤刪）。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "edit-hash.md"
    target.write_text(
        "---\nname: edit-hash\ndescription: 原始合規\nmetadata:\n  type: project\n---\nbody\n",
        encoding="utf-8",
    )
    r = run_hook(
        hook_payload(
            "Edit",
            target,
            old_string="description: 原始合規",
            new_string="description: 全弧完結含 commit 47aa89d 收案",
        )
    )
    assert r.returncode == 2
    assert "hash" in r.stderr


def test_entry_write_desc_commit_word_false_positive_allowed(tmp_path):
    """digit-lookahead 補強（mosaic 實戰案例）：desc 含「commit feedback」——
    "feedbac" 恰 7 個純字母 hex 字元，但無數字 → 放行（真 hash 7+ 碼全字母
    機率≈0.01%，誤擋合法 desc 的代價更高）。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "commit-word.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content=(
                "---\nname: commit-word\ndescription: git commit feedback 群——staging 陷阱與 mixed-tree 紀律\n"
                "metadata:\n  type: feedback\n---\nbody\n"
            ),
        )
    )
    assert r.returncode == 0


def test_entry_write_folded_desc_hash_passthrough(tmp_path):
    """F7 反例（EP review）：folded（>-）desc 含 hash → 放行——釘住「與長度檢查
    同界」承諾（folded 量到摺疊符號本身、desc 值抽取不到——既有品質洞邊界不擴大）。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "folded.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content=(
                "---\nname: folded\ndescription: >-\n"
                "  commit 47aa89d hidden in folded\nmetadata:\n  type: project\n---\nbody\n"
            ),
        )
    )
    assert r.returncode == 0


def test_entry_edit_grow_overlimit_blocked(tmp_path):
    """既有 11,800 chars 檔 Edit +500（變大且超 12,000）→ exit 2——膨脹方向擋。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "growing.md"
    base = (
        "---\nname: growing\ndescription: 合規\nmetadata:\n  type: project\n---\n"
        + "y" * 11_700
    )
    target.write_text(base, encoding="utf-8")
    r = run_hook(
        hook_payload(
            "Edit",
            target,
            old_string="y" * 10,
            new_string="y" * 10 + "z" * 500,
        )
    )
    assert r.returncode == 2
    assert "膨脹" in r.stderr


def test_entry_edit_shrink_overlimit_file_allowed(tmp_path):
    """既有超大檔（13,000）收斂型 Edit（delta<0）→ exit 0——不卡 audit 收縮。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "shrinking.md"
    base = (
        "---\nname: shrinking\ndescription: 合規\nmetadata:\n  type: project\n---\n"
        + "y" * 12_900
    )
    target.write_text(base, encoding="utf-8")
    r = run_hook(
        hook_payload(
            "Edit",
            target,
            old_string="y" * 5_000,
            new_string="y" * 10,
        )
    )
    assert r.returncode == 0


def test_entry_edit_desc_overlong_blocked(tmp_path):
    """Edit 的 new_string 含 description: 行且值 >100 → exit 2。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "desc-edit.md"
    target.write_text(
        "---\nname: desc-edit\ndescription: 短\n---\nbody\n", encoding="utf-8"
    )
    r = run_hook(
        hook_payload(
            "Edit",
            target,
            old_string="description: 短",
            new_string="description: " + "長" * 130,
        )
    )
    assert r.returncode == 2


def test_entry_governance_self_gated(tmp_path):
    """同目錄無 generator → 條目寫入不攔（裝 script 即 opt-in，沿襲索引 gate 語義）。"""
    target = tmp_path / "plain-entry.md"
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: plain\ndescription: " + "長" * 130 + "\n---\nbody\n",
        )
    )
    assert r.returncode == 0


def test_entry_write_desc_boundary_100_pass_101_blocked(tmp_path):
    """F6：desc 邊界值——恰 100 放行、101 擋（＝寫入紀律值；09-03 P1 對齊）。"""
    pool = make_pool(tmp_path, n=1)
    for n, expect in ((100, 0), (101, 2)):
        r = run_hook(
            hook_payload(
                "Write",
                pool / f"desc-{n}.md",
                content="---\nname: desc-{n}\ndescription: "
                + "長" * n
                + "\nmetadata:\n  type: project\n---\nbody\n".replace("{n}", str(n)),
            )
        )
        assert r.returncode == expect, f"desc={n}"


def test_entry_write_shrink_overlimit_file_allowed(tmp_path):
    """F2 行為錨：既有 13K 檔 Write 收斂到 12.5K（仍 >12,000 但變短）→ 放行。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "shrink.md"
    target.write_text(
        "---\nname: shrink\ndescription: 合規\nmetadata:\n  type: project\n---\n"
        + "y" * 12_900,
        encoding="utf-8",
    )
    r = run_hook(
        hook_payload(
            "Write",
            target,
            content="---\nname: shrink\ndescription: 合規\nmetadata:\n  type: project\n---\n"
            + "y" * 12_500,
        )
    )
    assert r.returncode == 0


def test_entry_edit_replace_all_bloat_blocked(tmp_path):
    """F3 行為錨：replace_all 膨脹 = delta × occurrences——多處置換越線要擋。"""
    pool = make_pool(tmp_path, n=1)
    target = pool / "rep.md"
    body = ("y" * 10 + "\n") * 1_050
    target.write_text(
        "---\nname: rep\ndescription: 合規\nmetadata:\n  type: project\n---\n" + body,
        encoding="utf-8",
    )
    r = run_hook(
        hook_payload(
            "Edit",
            target,
            old_string="y" * 10,
            new_string="y" * 10 + "z" * 20,
            replace_all=True,
        )
    )
    assert r.returncode == 2


def test_truncate_threshold_cross_layer_alignment():
    """F4：generator 截斷線 == hook DESC_LIMIT（跨層單一源機械錨）。"""
    assert generator.TRUNCATE_DESC == block_memory.DESC_LIMIT


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


def test_regen_stale_copy_writes_skip_marker(tmp_path):
    """副本與資產源不符 → 跳過執行＋寫 _regen-skipped-stale。

    09-06 pending-decisions ③查證產出：byte 比對跳過是 by-design（信任邊界），
    但跳過路徑 stdout 不進 context＝靜默停滯——marker 讓停滯 fail-visible。"""
    zdir = regen.zcode_memory_dir("/Users/ctai/Github/ai-rules", tmp_path)
    zdir.mkdir(parents=True)
    make_pool(zdir, n=1)
    g = zdir / "_generate_index.py"
    g.write_text(g.read_text(encoding="utf-8") + "# stale\n", encoding="utf-8")
    notes = regen.run_for_cwd("/Users/ctai/Github/ai-rules", tmp_path)
    assert any("不符" in n for n in notes)
    assert not (zdir / "MEMORY.md").exists()  # 未執行 generator
    assert (zdir / "_regen-skipped-stale").exists()  # 停滯可見


def test_regen_fresh_run_clears_skip_marker(tmp_path):
    """副本相符成功執行 → 清 _regen-skipped-stale（殘留標記隨修復消失）。"""
    zdir = regen.zcode_memory_dir("/Users/ctai/Github/ai-rules", tmp_path)
    zdir.mkdir(parents=True)
    make_pool(zdir, n=1)
    (zdir / "_regen-skipped-stale").write_text("殘留\n", encoding="utf-8")
    regen.run_for_cwd("/Users/ctai/Github/ai-rules", tmp_path)
    assert (zdir / "MEMORY.md").exists()  # generator 有跑
    assert not (zdir / "_regen-skipped-stale").exists()


def test_generator_frontmatter_violation_fail_loud(tmp_path):
    """F-1②／AIR-27 CC 式：frontmatter 違規（缺 type）→ exit 1＋[FAIL] 含檔名
    ＋**壞條目跳過、合法條目照常寫出**——一個壞檔不再擋全部條目的投影
    （原拒寫＝停滯面比 size gate 更大，與「拒寫＝召回斷裂」原則自相矛盾）。
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
    idx_path = pool / "MEMORY.md"
    assert idx_path.exists()  # CC 式：合法條目照常投影
    idx = idx_path.read_text(encoding="utf-8")
    assert "proj-000" in idx  # 合法條目在場
    assert "bad-entry" not in idx  # 壞條目被跳過


def test_generator_frontmatter_violation_check_does_not_write(tmp_path):
    """AIR-27 對稱邊界：errs＋--check → 不寫入（--check 零副作用對兩種 gate 一致）。"""
    pool = make_pool(tmp_path, n=1)
    (tmp_path / "bad-entry.md").write_text(
        "---\nname: bad-entry\ndescription: 缺 type\n---\nbody\n", encoding="utf-8"
    )
    r = subprocess.run(
        [sys.executable, str(pool / "_generate_index.py"), "--check"],
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
