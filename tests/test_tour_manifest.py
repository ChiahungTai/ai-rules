"""tour_manifest init_scan 單元測試——generator 檔名慣例猜測。

D-f 後新增純序號 NN.tour→chain_tour 分支；delta/dev-fixture 排除；
manual 判定（含全形數字 isascii 防禦）。
"""

from pathlib import Path

from code_reality import tour_manifest


def _touch(root: Path, rel: str) -> None:
    p = root / ".tours" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}", encoding="utf-8")


def test_init_scan_filename_conventions(tmp_path: Path) -> None:
    _touch(tmp_path, "01-族名/01.tour")
    _touch(tmp_path, "02-舊格式/chain-01-x.tour")
    _touch(tmp_path, "00 - codetour 總覽.tour")
    _touch(tmp_path, "03-全形/１２.tour")
    _touch(tmp_path, "delta/2026-08-23-task.tour")
    data = tour_manifest.init_scan(tmp_path, Path(".tours"))
    assert data["tour"]["01-族名/01.tour"]["generator"] == "chain_tour"
    assert data["tour"]["02-舊格式/chain-01-x.tour"]["generator"] == "chain_tour"
    assert data["tour"]["00 - codetour 總覽.tour"]["generator"] == "manual"
    assert data["tour"]["03-全形/１２.tour"]["generator"] == "manual"
    assert "delta/2026-08-23-task.tour" not in data["tour"]
