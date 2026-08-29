"""compact-tail-inject 的 transcript 解析測試（judge F1）。

fetch_tail 是本批最大行為面變更（sqlite → CC transcript JSONL）；
截斷語義（保最新砍最舊）是回歸時最易靜默壞掉的點。
欄位語義已對真實 transcript 驗證（isCompactSummary/isSidechain 在場）。
"""

import json

from conftest import load_module

cti = load_module("hooks/compact-tail-inject.py")


def _line(**kw) -> str:
    return json.dumps(kw)


def test_texts_of_str_and_list_blocks():
    assert cti._texts_of({"content": "hi"}) == ["hi"]
    assert cti._texts_of(
        {"content": [{"type": "text", "text": "a"}, {"type": "tool_use", "text": "b"}]}
    ) == ["a"]
    assert cti._texts_of({}) == []


def test_fetch_tail_filters_and_chronological_order(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text(
        "\n".join(
            [
                _line(
                    type="user",
                    message={"content": "舊訊息"},
                    timestamp="2026-08-30T01:00:00Z",
                ),
                _line(type="summary", message={"content": "skip-type"}),
                _line(
                    type="user",
                    isCompactSummary=True,
                    message={"content": "skip-compact"},
                    timestamp="2026-08-30T02:00:00Z",
                ),
                _line(
                    type="assistant",
                    isSidechain=True,
                    message={"content": "skip-sidechain"},
                    timestamp="2026-08-30T03:00:00Z",
                ),
                _line(
                    type="assistant",
                    message={"content": [{"type": "text", "text": "最新回覆"}]},
                    timestamp="2026-08-30T04:05:06Z",
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    out = cti.fetch_tail(str(p))
    assert "舊訊息" in out and "最新回覆" in out
    assert "skip-type" not in out and "skip-compact" not in out
    assert "skip-sidechain" not in out
    assert out.index("舊訊息") < out.index("最新回覆")  # 舊在前、新在後
    assert "04:05:06" in out


def test_fetch_tail_skips_prior_injection_marker(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text(
        _line(
            type="user",
            message={"content": "含 <compact-tail-inject> 上代注入"},
            timestamp="2026-08-30T05:00:00Z",
        )
        + "\n",
        encoding="utf-8",
    )
    assert cti.fetch_tail(str(p)) == ""


def test_fetch_tail_budget_drops_oldest_keeps_newest(tmp_path):
    big = "x" * 15000  # TAIL_BUDGET_BYTES=20000：只容得下最新一則
    p = tmp_path / "t.jsonl"
    p.write_text(
        "\n".join(
            [
                _line(
                    type="user",
                    message={"content": big + " OLDEST"},
                    timestamp="2026-08-30T06:00:00Z",
                ),
                _line(
                    type="user",
                    message={"content": big},
                    timestamp="2026-08-30T07:00:00Z",
                ),
                _line(
                    type="user",
                    message={"content": big + " NEWEST"},
                    timestamp="2026-08-30T08:00:00Z",
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    out = cti.fetch_tail(str(p))
    assert "NEWEST" in out
    assert "OLDEST" not in out


def test_fetch_tail_scan_window_truncates(tmp_path):
    # 65 則小訊息全在預算內：CANDIDATE_ENTRIES=60 → 最舊 5 則被窗口截掉
    p = tmp_path / "t.jsonl"
    p.write_text(
        "\n".join(
            _line(
                type="user",
                message={"content": f"msg-{i:02d}"},
                timestamp=f"2026-08-30T09:{i // 60:02d}:{i % 60:02d}Z",
            )
            for i in range(65)
        )
        + "\n",
        encoding="utf-8",
    )
    out = cti.fetch_tail(str(p))
    assert "msg-64" in out  # 最新保留
    assert "msg-04" not in out  # 窗口外最舊被截
    assert "msg-05" in out  # 窗口邊界內保留
