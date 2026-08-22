"""S2 chain_tour 整合測試——真 callchain 文檔 × 真 graph.db（SM-4/5 數字錨）。

對照組＝POC chain_viewer.py（5 場景/187 幀；重錨分佈 same 65/moved 12/
moved-file 1/noref 66——完全命中）。步數與 EP 原文差 1：EP 的 121＝187−66
（g-noref 直減），實際 skipped=65（一幀有 file:line 錨僅 ident 空）。
缺 graph.db 的環境 skip。
"""

import json
import re
from pathlib import Path

import pytest

from code_reality.chain_tour import build_tours, write_tours
from code_reality.common import graph_db_path

REPO_ROOT = (
    Path.home() / "Github" / "mosaic_alpha_offline_backtesting"
)  # 搬遷後錨定 mosaic checkout（整合資料：graph.db/.tours/EP）
CHAIN_MD = REPO_ROOT / "ai-analysis/blueprint/callstack-v1/paper-trading-chain.md"

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not graph_db_path(REPO_ROOT).exists(), reason="缺 .code-review-graph/graph.db"
)
@pytest.mark.skipif(not CHAIN_MD.exists(), reason="缺 callchain 文檔")
def test_real_chain_tours(tmp_path: Path) -> None:
    st = build_tours(CHAIN_MD, REPO_ROOT, graph_db_path(REPO_ROOT))

    # SM-4：5 條 tour（每場景一條）；187 幀。步數 122＝187−65：skipped 是
    # 「無 abs 錨」的真實不可成步數——EP 原文 121 來自 g-noref(66) 直減，
    # 但其中有 1 幀帶 file:line 錨僅 ident 空（無 graph badge）仍可成步。
    assert len(st.tours) == 5
    assert st.frames == 187
    assert st.skipped == 65
    total_steps = sum(len(t["steps"]) for t in st.tours)
    assert total_steps == 122
    assert total_steps == st.frames - st.skipped  # 不變量：步數＝幀−跳過

    flat = [s for t in st.tours for s in t["steps"]]
    # 每步的錨檔真的在磁碟上（moved-file 步指向新檔；其餘指向解析後原檔）
    missing = [s["file"] for s in flat if not (REPO_ROOT / s["file"]).exists()]
    assert missing == [], f"步錨到不存在的檔：{missing[:5]}"

    # tour-contract S1 pattern 抽查：發射出的 pattern 對最終錨檔命中
    # （pattern 由重錨後行內容生成——moved/moved-file 步取新行）
    sampled = [s for s in flat if "pattern" in s]
    assert sampled, "無任何步發射 pattern"
    for s in sampled:
        content = (REPO_ROOT / s["file"]).read_text(encoding="utf-8")
        assert re.search(s["pattern"], content, re.MULTILINE), (
            f"pattern 未命中：{s['file']}"
        )

    # tour-contract S2（SM-4）：寫檔 title 帶 NN - 前綴、上游連鎖 regex 可解析
    paths = write_tours(st, tmp_path)
    assert len(paths) == 5
    for i, p in enumerate(paths, 1):
        written = json.loads(p.read_text())
        m = re.match(r"^#?(\d+)\s+-", written["title"])
        assert m and m.group(1) == f"{i:02d}"

    # SM-5：跨檔重錨——ShioajiLiveExecClientFactory 幀指向新檔 factories.py
    sm5 = [s for s in flat if "ShioajiLiveExecClientFactory" in s["title"]]
    assert sm5, "找不到 ShioajiLiveExecClientFactory 幀"
    assert sm5[0]["file"].endswith("adapters/sj/factories.py")
    assert "搬家" in sm5[0]["description"]

    # 重錨分佈與 POC 同量級（same 65/moved 12/moved-file 1）
    assert st.g_counts.get("same", 0) >= 50
    assert st.g_counts.get("moved", 0) >= 5
    assert st.g_counts.get("moved-file", 0) >= 1
