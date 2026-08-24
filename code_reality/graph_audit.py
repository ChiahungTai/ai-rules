"""CRG graph.db Rust 完整度稽核——D1 風險掃描＋D2 rust-analyzer 對帳。

收編自 NT N1 repo-local 腳本（2026-08-24 驗證輪實測：239 風險檔／187
對帳／219 確定缺差——kernel.rs 九項全中）。偵測 CRG ``nodes.qualified_name
UNIQUE``＋``ON CONFLICT DO UPDATE`` 後寫蓋前寫的靜默丟失：Rust 型別的
inherent impl 與 trait impl 同名方法同鍵 ``X.method``，前者消失
（``head_matches_build`` 新鮮度指標不反映此項——檔案未變不重 parse；
根因記錄見 NT memory crg-graph-build-node-loss）。

兩層偵測：
  D1 風險掃描（純文字，秒級）：同型別多 impl 塊＋方法名 per-block 計數
    ≥2 → 高風險檔。**per-block 計數非全體交集**——交集會被 Drop 等單方法
    impl 清空（kernel.rs 三 impl〔inherent＋Drop＋trait〕漏報實證）。
    僅認 col-0 impl 形態（rustfmt 慣例）——縮排 impl（``mod tests`` 內等）
    對 D1 不可見，誤差方向＝風險檔漏報→預設 D2 scope 外，``--all`` 為兜底
  D2 對帳（每檔百毫秒級）：rust-analyzer ``symbols`` stdin 模式（獨立源）
    vs graph.db nodes 每名計數——DB 少於 rust-analyzer＝被去重吃掉。
    **DB 側 kind 須含 'Test'**——CRG 把 #[test] 函數建為 Test 節點、
    rust-analyzer 側是 Function/Method，漏計＝全部測試函數誤報缺差
    （NT N1 首跑 1,670 假警報實證）

用法::

    uv run --project ~/Github/ai-rules python -m code_reality.graph_audit \
        --repo <repo> [--all] [--json] [--graph PATH]

掃描集＝profile ``[[scan_root]]`` 的 path glob（Rust 形態 repo）；無
scan_root → repo 全 ``*.rs`` 經 exclusions 過濾（generic fallback）。
graph 預設 ``<repo>/.code-review-graph/graph.db``。退出碼：0=乾淨｜
1=發現缺差｜2=環境錯誤（rust-analyzer 未裝／graph.db 不在）。``--json``
輸出鍵（risk_files/audited_files/missing）為 NT 治理鉤子消費契約，勿改。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

from code_reality.common import connect_ro, graph_db_path
from code_reality.exclusions import is_excluded
from code_reality.profile import load_profile, scan_roots

IMPL_RE = re.compile(r"^impl(?:<[^>]*>)?\s+(?:(\w+)\s+for\s+)?([A-Z]\w*)")
FN_RE = re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+(\w+)")
RA_LABEL_RE = re.compile(r'label: "([^"]*)"')
RA_KIND_RE = re.compile(r"kind: SymbolKind\((\w+)\)")
RA_FN_KINDS = {"Function", "Method"}


def scan_files(repo: Path) -> list[Path]:
    """掃描集：profile [[scan_root]] path glob；無 → repo 全 *.rs 經
    exclusions 過濾（generic fallback——與 PathResolver/pkg_roots 同型）。"""
    profile = load_profile(repo)
    roots = scan_roots(profile)
    if roots:
        return sorted({p for sr in roots for p in repo.glob(sr.path)})
    return sorted(
        p
        for p in repo.rglob("*.rs")
        if not is_excluded(p.relative_to(repo).as_posix(), profile)
    )


def risk_scan(files: list[Path]) -> list[tuple[Path, str, list[str]]]:
    """D1：同型別多 impl 塊＋方法名 per-block 計數 ≥2 的檔案（不碰 graph）。

    準則＝「同名方法出現於 ≥2 個 impl 塊」（任兩塊碰撞）——全體交集
    準則會被 Drop 等單方法 impl 清空漏報（kernel.rs 三 impl 實證，
    NT N1 教訓）。
    """
    at_risk: list[tuple[Path, str, list[str]]] = []
    for f in files:
        impls: list[tuple[str, list[str]]] = []
        cur: tuple[str, list[str]] | None = None
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = IMPL_RE.match(line)
            if m:
                cur = (m.group(2), [])
                impls.append(cur)
                continue
            if cur is not None:
                fm = FN_RE.match(line)
                if fm:
                    cur[1].append(fm.group(1))
                elif line.startswith(("}", "impl ")):
                    cur = None
        block_counts: dict[str, Counter] = {}
        for t, fns in impls:
            counts = block_counts.setdefault(t, Counter())
            for name in set(fns):
                counts[name] += 1
        for t, counts in block_counts.items():
            overlap = sorted(n for n, c in counts.items() if c >= 2)
            if overlap:
                at_risk.append((f, t, overlap))
    return at_risk


def parse_ra_symbols(stdout_text: str) -> Counter:
    """rust-analyzer ``symbols`` 輸出 → (label → fn 計數)；非 fn kind 略過。"""
    counts: Counter = Counter()
    for line in stdout_text.splitlines():
        kind = RA_KIND_RE.search(line)
        if not kind or kind.group(1) not in RA_FN_KINDS:
            continue
        label = RA_LABEL_RE.search(line)
        if label:
            counts[label.group(1)] += 1
    return counts


def ra_symbols(path: Path) -> Counter:
    """rust-analyzer stdin 模式（獨立於 CRG parser 的對帳源）。"""
    proc = subprocess.run(
        ["rust-analyzer", "symbols"],
        input=path.read_bytes(),
        capture_output=True,
        timeout=60,
        check=False,  # 非零退出＝輸出空清單——vacuous pass（零比較）非全缺差；
        # audit 迴圈對非空檔零輸出印 [WARN]（防靜默假陰性全綠）
    )
    return parse_ra_symbols(proc.stdout.decode("utf-8", errors="replace"))


def db_functions(conn, path: Path) -> Counter:
    """graph.db nodes 每名計數——kind 含 'Test'（漏計＝測試函數全誤報）。"""
    rows = conn.execute(
        "SELECT name, COUNT(*) FROM nodes WHERE file_path = ? "
        "AND kind IN ('Function', 'Test') GROUP BY name",
        (str(path.resolve()),),
    )
    return Counter({name: count for name, count in rows})


def audit(
    repo: Path,
    graph: Path,
    *,
    all_files: bool = False,
    ra_lookup=None,
) -> tuple[list[tuple[Path, str, list[str]]], int, list[dict[str, object]]]:
    """D1＋D2 主流程——回 (risk, audited_count, missing)。

    ``ra_lookup`` 注入點供測試替身（預設 rust-analyzer subprocess）。
    """
    files = scan_files(repo)
    risk = risk_scan(files)
    scope = files if all_files else sorted({f for f, _, _ in risk})
    lookup = ra_lookup or ra_symbols
    conn = connect_ro(graph)
    try:
        missing: list[dict[str, object]] = []
        for f in scope:
            ra = lookup(f)
            db = db_functions(conn, f)
            if not ra and f.stat().st_size > 0:
                print(
                    f"[WARN] rust-analyzer 對 {f.name} 零輸出（格式 drift 或"
                    "單檔 parse fail）——該檔對帳 vacuous，勿當乾淨讀",
                    file=sys.stderr,
                )
            for name, ra_count in ra.items():
                if db.get(name, 0) < ra_count:
                    missing.append(
                        {
                            "file": str(f),
                            "symbol": name,
                            "ra_count": ra_count,
                            "db_count": db.get(name, 0),
                        }
                    )
    finally:
        conn.close()
    return risk, len(scope), missing


def main() -> int:
    parser = argparse.ArgumentParser(description="CRG graph.db Rust 完整度稽核")
    parser.add_argument("--repo", type=Path, required=True, help="掃描目標 repo 根")
    parser.add_argument(
        "--all", action="store_true", help="對帳全部 .rs（預設僅風險檔）"
    )
    parser.add_argument(
        "--json", action="store_true", help="機器可讀輸出（治理鉤子契約）"
    )
    parser.add_argument(
        "--graph",
        type=Path,
        default=None,
        help="覆寫 graph.db 路徑（預設 <repo>/.code-review-graph/graph.db）",
    )
    args = parser.parse_args()

    if shutil.which("rust-analyzer") is None:
        print(
            "[FAIL] rust-analyzer 不在 PATH——rustup component add rust-analyzer",
            file=sys.stderr,
        )
        return 2
    graph = args.graph if args.graph is not None else graph_db_path(args.repo)
    if not graph.exists():
        print(
            f"[FAIL] graph.db 不存在：{graph}（完整度稽核需要它；新鮮度指標不保證存在）",
            file=sys.stderr,
        )
        return 2

    risk, audited, missing = audit(args.repo, graph, all_files=args.all)

    if args.json:
        print(
            json.dumps(
                {
                    "risk_files": [
                        {"file": str(f), "type": t, "overlap": o} for f, t, o in risk
                    ],
                    "audited_files": audited,
                    "missing": missing,
                },
                ensure_ascii=False,
                indent=1,
            )
        )
    else:
        print(f"[OK] D1 風險掃描：{len(risk)} 檔（同型別多 impl＋方法名 per-block ≥2）")
        print(f"[OK] D2 對帳：{audited} 檔（rust-analyzer vs graph.db）")
        if missing:
            print(
                f"[WARN] DB 缺差 {len(missing)} 項（同鍵去重吃掉——"
                "head_matches_build 不反映此項）："
            )
            by_file: dict[str, list[dict[str, object]]] = {}
            for m in missing:
                by_file.setdefault(str(m["file"]), []).append(m)
            for f, items in sorted(by_file.items()):
                syms = ", ".join(
                    f"{m['symbol']}({m['db_count']}/{m['ra_count']})" for m in items
                )
                print(f"  {f}: {syms}")
        else:
            print("[OK] 無缺差")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
