"""攔截型 hooks 的偵測邏輯單元測試（T1-2）。

這些 is_violation() 是行為閘門的核心——regression 直接改變攔截面
（漏抓 = 規則繞道重現；誤傷 = 正常命令被擋）。
"""

from conftest import load_module

block_comment = load_module("hooks/block-python-c-comment.py")
block_write = load_module("hooks/block-python-file-write.py")


# ---------------------------------------------------------------------------
# block-python-c-comment：python -c 跨行 # 註解
# ---------------------------------------------------------------------------


def test_c_comment_violation_multiline_hash():
    cmd = "python3 -c 'import json\n# 註解\nprint(1)'"
    assert block_comment.is_violation(cmd)


def test_c_comment_ok_single_line():
    assert not block_comment.is_violation("python3 -c 'print(1)'")


def test_c_comment_ok_multiline_no_hash():
    assert not block_comment.is_violation("python -c 'x = 1\nprint(x)'")


def test_c_comment_ok_not_python():
    assert not block_comment.is_violation("echo 'a\n# b'")


# ---------------------------------------------------------------------------
# block-python-file-write：python heredoc 寫檔繞道（遙測實測 319 次的形態）
# ---------------------------------------------------------------------------


def test_write_violation_pathlib(tmp_path):
    cmd = f"python3 - <<'EOF'\nfrom pathlib import Path\nPath('{tmp_path}/x').write_text('hi')\nEOF"
    assert block_write.is_violation(cmd)


def test_write_violation_open_w():
    cmd = (
        "uv run python - <<EOF\nwith open('out.txt', 'w') as f:\n    f.write('x')\nEOF"
    )
    assert block_write.is_violation(cmd)


def test_write_ok_readonly_heredoc():
    cmd = "python3 - <<'EOF'\nimport json\nprint(json.dumps({'a': 1}))\nEOF"
    assert not block_write.is_violation(cmd)


def test_write_ok_open_read_mode():
    cmd = "python3 - <<EOF\nwith open('in.txt', 'r') as f:\n    print(f.read())\nEOF"
    assert not block_write.is_violation(cmd)


def test_write_ok_no_heredoc():
    # 非 heredoc 的單行 write（少見但非本 hook 標的——write 繞道以 heredoc 為大宗）
    assert not block_write.is_violation("python3 -c \"open('x','w')\"")


def test_write_ok_write_before_heredoc_marker():
    # 寫入 pattern 在 heredoc 標記之前（如把 heredoc 輸出導向檔案的字串巧合）
    cmd = "echo \"w_text(\" && python3 - <<'EOF'\nprint(1)\nEOF"
    assert not block_write.is_violation(cmd)
