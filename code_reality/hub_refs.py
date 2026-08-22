"""hub-refs 聚合器——CRG callers_of/callees_of 按檔聚合＋test/prod 切分。

解 hub symbol 洪流（R4 實證：Interval 的 LSP findReferences 195KB 被
resultBudget 截斷；CRG JSON 含 is_test＋file_path——聚合後即為可消費答案）。
精度分工（報告 §4 定版）：LSP 管「邊真相」、本工具管「hub 廣度概覽」。

用法::

    uv run python -m code_reality.hub_refs <symbol> \
        [--repo PATH] [--direction callers|callees] [--top N]

symbol 形態：完整 qualified name（``<abs-path>::Class.method``）直接查；
裸名經 **nodes 表 sqlite 精確匹配**解析（2026-08-21 實測：CRG CLI 的
ambiguous 候選是 fuzzy substring 前 N、不含精確 class node，FTS search 亦
找不到 enum Type——nodes 表是唯一可靠解析源；query 步走 CLI）。

已知限制（R2）：CRG（Tree-sitter 家族）漏跨檔 instance-attr 邊——
本工具輸出末行固定附註提醒消費者。
"""

import argparse
import json
import sqlite3
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from code_reality.common import (
    assert_db_unchanged,
    connect_ro,
    db_mtime_ns,
    graph_db_path,
    repo_relative,
)
from code_reality.exclusions import is_excluded
from code_reality.profile import load_profile

CRG_TIMEOUT_S = 120


@dataclass
class AggResult:
    prod: list[tuple[str, int]]
    test: list[tuple[str, int]]
    total_prod: int
    total_test: int
    excluded: int
    outside: int = 0


def crg_query(pattern: str, target: str, repo_root: Path) -> dict[str, Any]:
    """subprocess 呼叫 CRG CLI——crash-only（SM-13）。

    CRG 對 not_found/ambiguous 回 **exit 0**＋JSON status 欄——exit code
    不可作為成敗判準，status 由呼叫端檢查（resolve_symbol）。
    """
    cmd = ["uvx", "code-review-graph", "query", pattern, target]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=CRG_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise AssertionError(f"CRG CLI 逾時（>{CRG_TIMEOUT_S}s）: {cmd}") from e
    except FileNotFoundError as e:
        raise AssertionError(f"uvx 不在 PATH——先安裝 uv: {cmd[0]}") from e
    assert proc.returncode == 0, (
        f"CRG CLI 失敗（exit {proc.returncode}）: {' '.join(cmd[2:])}\n{proc.stderr[-500:]}"
    )
    try:
        out: dict[str, Any] = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"CRG CLI stdout 非 JSON（可能混入 warnings）: {proc.stdout[:200]} | stderr: {proc.stderr[-200:]}"
        ) from e
    return out


def _require_ok(resp: dict[str, Any]) -> dict[str, Any]:
    """CRG 回應必須 status=ok——not_found/ambiguous 原樣轉發成明確輸出（SM-10）。

    打錯的 qualified name（含 ``::`` 直通）若放行會得到 ``[OK] 0 refs``
    假陰性——對 LLM 消費者（post-build 接線後）是「無引用、可刪」的誤導。
    """
    status = resp.get("status")
    if status == "ok":
        return resp
    print(f"[FAIL] CRG {status}: {resp.get('summary', '(無 summary)')}")
    for c in (resp.get("candidates") or [])[:10]:
        print(f"  候選: {c.get('qualified_name')}  (is_test={c.get('is_test')})")
    raise SystemExit(f"CRG query {status}: {resp.get('summary', '')}")


def resolve_qualified(symbol: str, repo_root: Path) -> str:
    """symbol → qualified name——nodes 表 sqlite 精確匹配（SM-10）。

    實測（2026-08-21）：CRG CLI 的 ambiguous 候選是 fuzzy substring 前 N
    （裸名 Interval 回 20 個 ``*interval*`` 函式、不含精確 class node）；
    ``Class.method`` 裸名直接查回 not_found（name 欄只存 method 名）。
    nodes 表（name 精確 + parent_name）是可靠解析源；query 步才走 CLI。
    """
    if "::" in symbol:
        return symbol
    db_path = graph_db_path(repo_root)
    profile = load_profile(repo_root)
    assert db_path.exists(), (
        f"graph.db 不存在：{db_path}——先跑 `uvx code-review-graph build`"
    )
    m0 = db_mtime_ns(db_path)
    conn = connect_ro(db_path)
    try:
        if "." in symbol:
            cls, _, method = symbol.rpartition(".")
            rows = conn.execute(
                "SELECT qualified_name, file_path FROM nodes WHERE name = ? AND parent_name = ?",
                (method, cls),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT qualified_name, file_path FROM nodes WHERE name = ?", (symbol,)
            ).fetchall()
    except sqlite3.DatabaseError as e:
        raise AssertionError(
            f"非 CRG graph.db（讀 nodes 失敗：{e}）：{db_path}"
            "——先跑 `uvx code-review-graph build`"
        ) from e
    finally:
        conn.close()
    assert_db_unchanged(db_path, m0)
    rows = [
        (q, fp)
        for q, fp in rows
        if (rel := repo_relative(fp, repo_root)) is not None
        and not is_excluded(rel, profile)
    ]
    if len(rows) == 1:
        return str(rows[0][0])
    if len(rows) > 1:
        print(f"[FAIL] '{symbol}' 匹配 {len(rows)} 個 node（用 qualified_name 重跑）：")
        for q, _ in rows[:10]:
            print(f"  {q}")
        raise SystemExit(f"ambiguous symbol: {symbol}")
    raise SystemExit(
        f"symbol not found: {symbol}——試完整 qualified name（<abs>::Class.method）"
    )


def resolve_symbol(
    symbol: str, repo_root: Path, direction: str = "callers"
) -> dict[str, Any]:
    """名稱解析＋查詢——qualified 直接查（status 必檢）；裸名 sqlite 精確解析（SM-10）。

    裸名解析結果經 CRG 回應的 ``target`` 欄回流（main 的 [OK] 行印出），
    不另行 print。
    """
    pattern = "callers_of" if direction == "callers" else "callees_of"
    qname = resolve_qualified(symbol, repo_root)
    return _require_ok(crg_query(pattern, qname, repo_root))


def aggregate(
    results: list[dict[str, Any]], repo_root: Path, top: int = 20
) -> AggResult:
    """caller/callee refs 按目錄（去檔名）計數，is_test 切兩欄，exclusions 過濾。"""
    repo_root = repo_root.resolve()
    profile = load_profile(repo_root)
    prod_counts: Counter[str] = Counter()
    test_counts: Counter[str] = Counter()
    excluded = 0
    outside = 0
    for r in results:
        fp = r.get("file_path")
        if not fp:
            continue
        try:
            rel = str(Path(fp).relative_to(repo_root))
        except ValueError:
            outside += 1  # repo 外（venv/其他 checkout）——計數不靜默
            continue
        if is_excluded(rel, profile):
            excluded += 1
            continue
        d = str(Path(rel).parent)
        # 路徑 heuristic 補 CRG is_test 漏標（實測 tests/unit_tests node 出現在 prod 欄）
        if r.get("is_test") or rel.startswith("tests/"):
            test_counts[d] += 1
        else:
            prod_counts[d] += 1
    return AggResult(
        prod=prod_counts.most_common(top),
        test=test_counts.most_common(top),
        total_prod=sum(prod_counts.values()),
        total_test=sum(test_counts.values()),
        excluded=excluded,
        outside=outside,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("symbol", help="qualified name 或裸名（自動解析）")
    parser.add_argument(
        "--repo", type=Path, default=Path.cwd(), help="repo 根（CRG cwd）"
    )
    parser.add_argument(
        "--direction",
        choices=["callers", "callees"],
        default="callers",
        help="refs 方向",
    )
    parser.add_argument("--top", type=int, default=20, help="每欄最多列 N 目錄")
    args = parser.parse_args()

    resp = resolve_symbol(args.symbol, args.repo, args.direction)
    results = resp.get("results", [])
    agg = aggregate(results, args.repo, top=args.top)

    print(
        f"[OK] {args.direction} of {resp.get('target', args.symbol)}: "
        f"{agg.total_prod} prod / {agg.total_test} test refs"
        f"（omitted {resp.get('results_omitted', 0)}，excluded {agg.excluded}，"
        f"outside {agg.outside}）"
    )
    print("prod:")
    for d, n in agg.prod:
        print(f"  {d} ({n})")
    print("test:")
    for d, n in agg.test:
        print(f"  {d} ({n})")
    print(
        "[WARN] 註腳：CRG（Tree-sitter）缺 instance-attr 邊（R2）——跨檔 self._x.method() "
        "呼叫不在本清單；邊真相用 LSP findReferences"
    )


if __name__ == "__main__":
    main()
