"""S1 delta_tour 整合測試——真 snapshot sidecar × 真 repo 歷史（SM-1 數字錨）。

對照組＝POC ``.agent-tmp/ui/build_delta_tour.py`` 產出（22 步實證）：
thin-layer 弧 87173a8a → 9f58f78c。sidecar 在 ``~/.mosaic/code-reality/
snapshots/``（本機環境產物，缺測 skip）。
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from code_reality.common import anchor_pattern
from code_reality.delta_tour import local_today

REPO_ROOT = (
    Path.home() / "Github" / "mosaic_alpha_offline_backtesting"
)  # 搬遷後錨定 mosaic checkout（整合資料：graph.db/.tours/EP）
SNAP_DIR = Path.home() / ".mosaic" / "code-reality" / "snapshots"
SNAP_A = SNAP_DIR / "mosaic_alpha_offline_backtesting-87173a8a.json"
SNAP_B = SNAP_DIR / "mosaic_alpha_offline_backtesting-9f58f78c.json"
EP = REPO_ROOT / "ai-analysis/execution-plans/_done/ep-code-reality-thin-layer.md"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not (SNAP_A.exists() and SNAP_B.exists() and EP.is_file()),
        reason="缺歷史 snapshot sidecar／EP（本機環境產物——重造需 checkout 舊 commit；同 repo integration 慣例）",
    ),
]


def _run(*extra: str, out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "code_reality.delta_tour",
            str(SNAP_A),
            str(SNAP_B),
            "--repo",
            str(REPO_ROOT),
            "--out-dir",
            str(out),
            *extra,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(
    not (SNAP_A.exists() and SNAP_B.exists()), reason="缺歷史 snapshot sidecar"
)
class TestDeltaTourIntegration:
    def test_poc_parity_22_steps(self, tmp_path: Path) -> None:
        """SM-1：--ep 跑 thin-layer 弧 → 22 步（range 推導：1 總覽＋19 新＋2 修改）。

        2026-08-25 dogfood 三 bug 修後：本 EP 的 tools/tests 相對路徑在
        mosaic_alpha/ prefix **之外**（不可正規化命中）→ 宣稱對照**未比對**、
        步驟零 ⚠（舊行為全量 ⚠＝「EP 沒提卻變了」錯誤指控，mosaic dogfood
        bug 1）。計數由 range 同源導出（19 新檔＝步驟數，根治 3-vs-5 不一致）。
        """
        r = _run("--ep", str(EP), out=tmp_path)
        assert r.returncode == 0, r.stderr
        tour = json.loads(
            (
                tmp_path / f"{local_today():%Y-%m-%d}-ep-code-reality-thin-layer.tour"
            ).read_text()
        )
        assert len(tour["steps"]) == 22
        # tour-contract S2（SM-6）：title＝task（無 hash）、步 title 保留 hash
        assert tour["title"] == "ep-code-reality-thin-layer 變更導覽"

        s0 = tour["steps"][0]
        assert s0["title"] == "弧總覽：87173a8a → 9f58f78c"
        assert s0["file"] == str(EP)
        # thin-layer EP 無 mosaic_alpha/ mention 且相對路徑在 prefix 外 →
        # 未比對（三態），非全量 ⚠
        assert "未比對" in s0["description"]
        assert not any("⚠" in s["title"] for s in tour["steps"])
        assert not any("✓宣稱命中" in s["title"] for s in tour["steps"])
        assert "19 新檔" in s0["description"] and "2 修改" in s0["description"]

        # hunk 錨級對照（POC 實證值）：modified 檔跳第一個 hunk
        anchors = {s["file"]: s["line"] for s in tour["steps"]}
        assert anchors["tools/AGENTS.md"] == 29
        assert anchors[".gitignore"] == 229

        # tour-contract S1 pattern 抽查：錨行＝after commit 版本內容、
        # literal-ish 命中該檔（AGENTS.md 錨 :29）
        s_ag = next(
            s for s in tour["steps"] if s["title"].startswith("M修改 AGENTS.md")
        )
        content = subprocess.run(
            ["git", "show", "9f58f78c:tools/AGENTS.md"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert s_ag["pattern"] == anchor_pattern(content.splitlines()[29 - 1])
        assert re.search(s_ag["pattern"], content, re.MULTILINE)
        with_pattern = sum(1 for s in tour["steps"] if "pattern" in s)
        assert with_pattern >= 10  # 刪檔步/空錨行步除外，多數可發射

    def test_without_ep_shows_claims_none(self, tmp_path: Path) -> None:
        """SM-2：無 --ep → claims NONE＋實際變動模組清單（不誤導）。"""
        r = _run(out=tmp_path)
        assert r.returncode == 0, r.stderr
        tour = json.loads(
            (tmp_path / f"{local_today():%Y-%m-%d}-review.tour").read_text()
        )
        assert tour["title"] == "review 變更導覽"
        desc = tour["steps"][0]["description"]
        assert "NONE" in desc
        assert "tools" in desc and "tests" in desc
