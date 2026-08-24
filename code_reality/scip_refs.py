"""scip_refs——rust-analyzer SCIP 索引查詢端（Rust refs/callers 真相源 sidecar）。

定位：CRG graph.db 對「同型別多 impl 同名方法」有同鍵去重漏收（見
graph_audit——NT 實測 861 顆），受影響符號的 callers 查詢回**假空**。
本工具改查 rust-analyzer 生成的 SCIP 索引（type-aware：inherent 與
trait impl 各自獨立 symbol——``impl#[Type]method().`` vs
``impl#[Type][Trait]method().``——正是 CRG 缺的消歧），作為這些符號的
def/refs 真相源。

SCIP 符號形態（查詢匹配涵蓋兩種）：
  impl 方法：``<mod>/impl#[Type]method().``、``<mod>/impl#[Type][Trait]method().``
  trait 宣告位址：``<mod>/<Trait>#method().``（型別以 ``#`` 為後綴——經
  dyn/泛界呼叫的引用解析到這顆，漏它＝低報 refs）

索引生成（~8 分鐘牆鐘／~270MB／rebase 後重生；輸出寫在 **cwd** 非
stdout）::

    mkdir -p <index-dir> && cd <index-dir> && rust-analyzer scip <repo-root>

scip_pb2.py 重生（schema 變更時；grpcio-tools 內含 protoc；scip.proto
已 vendored 同目錄）::

    cd code_reality && uv run --with grpcio-tools python -m grpc_tools.protoc \\
        --proto_path=. --python_out=. scip.proto

用法::

    uv run --project ~/Github/ai-rules python -m code_reality.scip_refs \\
        EventStoreLifecycle.open --index ~/.mosaic/code-reality/scip/index.scip
    uv run --project ~/Github/ai-rules python -m code_reality.scip_refs \\
        --audit --repo <repo> --index <index.scip>

退出碼：0=有結果｜1=查無｜2=環境錯誤（索引不在/損壞/protobuf 未裝/
graph_audit 子進程失敗）。原型取舍：每次查詢重新解析索引（~40s）——
常駐/快取為後續優化點。
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from code_reality import scip_pb2  # vendored gencode（需 protobuf runtime）
except ImportError:
    scip_pb2 = None  # type: ignore[assignment]

FN_TAIL_RE = re.compile(r"(?<!\w)(\w+)\(\)\.$")


def load_index(path: Path):
    """解析索引；損壞/截斷與空索引走環境錯誤（exit 2），不裸 traceback。

    protobuf 無完整性校驗——截斷恰落在 field 邊界時會靜默解析得部分
    結果（假「查無」），故加文件數下限作最小健全性檢查。
    """
    index = scip_pb2.Index()
    try:
        with open(path, "rb") as f:
            index.ParseFromString(f.read())
    except Exception as e:  # DecodeError 等
        print(f"[FAIL] 索引解析失敗（損壞/截斷？）：{e}", file=sys.stderr)
        sys.exit(2)
    if len(index.documents) == 0:
        print("[FAIL] 索引 0 文檔——空或損壞", file=sys.stderr)
        sys.exit(2)
    if len(index.documents) < 100:
        print(
            f"[WARN] 索引僅 {len(index.documents)} 文檔——可能截斷，結果存疑",
            file=sys.stderr,
        )
    return index


def ln(occ) -> int:
    r = occ.range
    return r[0] + 1 if len(r) >= 2 else -1


def loc(doc_path: str, occ) -> str:
    line = ln(occ)
    return f"{doc_path}:?" if line <= 0 else f"{doc_path}:{line}"


def tail(symbol: str) -> str:
    """`rust-analyzer cargo <crate> <ver> <mod>/descriptor` → descriptor 部分。"""
    parts = symbol.split(" ")
    return parts[-1] if len(parts) > 4 else symbol


def _matcher(query: str):
    """查詢 → symbol 匹配閉包。

    ``Type.method``：匹配 impl 變體（marker ``[Type]``）**與** trait 宣告
    位址（``Type#method`` 形態——漏它會低報 refs）；裸 ``name``：任何
    邊界正確的 ``name().`` 結尾（``(?<!\\w)`` 擋掉 my_open/reopen 誤配）。
    """
    if "." in query:
        type_name, method = query.rsplit(".", 1)
        name_pat = re.compile(r"(?<!\w)" + re.escape(method) + r"\(\)\.$")
        marker = f"[{type_name}]"
        trait_decl = re.compile(r"(?<![\w#])" + re.escape(type_name) + r"#")

        def match(s: str) -> bool:
            return bool(name_pat.search(s)) and (
                marker in s or bool(trait_decl.search(s))
            )

    else:
        name_pat = re.compile(r"(?<!\w)" + re.escape(query) + r"\(\)\.$")

        def match(s: str) -> bool:
            return bool(name_pat.search(s))

    return match


def find_defs(index, query: str) -> dict[str, list[str]]:
    """回 {symbol → [file:line...]}——DEF occurrences 中符合查詢者。"""
    match = _matcher(query)
    defs: dict[str, list[str]] = {}
    for d in index.documents:
        for occ in d.occurrences:
            if occ.symbol_roles & 1 and match(occ.symbol):
                defs.setdefault(occ.symbol, []).append(loc(d.relative_path, occ))
    return defs


def find_refs(index, symbols: set[str]) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {s: [] for s in symbols}
    for d in index.documents:
        for occ in d.occurrences:
            if occ.symbol in refs and not (occ.symbol_roles & 1):
                refs[occ.symbol].append(loc(d.relative_path, occ))
    return refs


def report(index, query: str) -> int:
    defs = find_defs(index, query)
    if not defs:
        print(f"[WARN] 查無 DEF：{query}")
        return 1
    refs = find_refs(index, set(defs))
    for symbol in sorted(defs):
        d_list, r_list = defs[symbol], refs[symbol]
        print(f"[OK] {tail(symbol)}")
        for loc_str in d_list:
            print(f"  DEF  {loc_str}")
        print(f"  refs: {len(r_list)} 處（跨檔）")
        for r in r_list[:6]:
            print(f"    {r}")
        if len(r_list) > 6:
            print(f"    ...共 {len(r_list)} 處")
    return 0


def audit_targets(
    documents, files_by_name: dict[str, set[str]]
) -> dict[str, tuple[str, str]]:
    """DEF occurrences → {symbol → (定義檔, 方法名)}。

    歸屬按 **(定義檔, 方法名) 雙鍵**——只按檔過濾會把同檔鄰居的 refs
    聯集進來（獨立審查實證：216→138，78 項假陽性）。
    """
    target_symbols: dict[str, tuple[str, str]] = {}
    for d in documents:
        for occ in d.occurrences:
            if not (occ.symbol_roles & 1):
                continue
            m = FN_TAIL_RE.search(occ.symbol)
            if not m:
                continue
            name = m.group(1)
            if name in files_by_name and d.relative_path in files_by_name[name]:
                target_symbols[occ.symbol] = (d.relative_path, name)
    return target_symbols


def missing_refs(
    missing: dict[str, object],
    target_symbols: dict[str, tuple[str, str]],
    refs_count: dict[str, list[str]],
) -> list[str]:
    """單一 graph_audit 缺差項 → 對應 SCIP refs（雙鍵歸屬過濾）。"""
    rel = missing["_rel"]
    return [
        r
        for sym, (d_file, d_name) in target_symbols.items()
        if d_file == rel and d_name == missing["symbol"]
        for r in refs_count[sym]
    ]


def _repo_rel(file_str: str, repo: Path) -> str:
    p = Path(file_str)
    try:
        return str(p.relative_to(repo))
    except ValueError:
        # repo 外路徑與 SCIP relative_path 恆不匹配（該項 refs 報 0）——
        # loud 標記防「假 0 callers」靜默混入
        print(
            f"[WARN] 缺差項路徑不在 repo 下（歸屬失敗，refs 將報 0）：{p}",
            file=sys.stderr,
        )
        return p.as_posix()


def audit_mode(index_path: Path, repo: Path) -> int:
    """graph_audit 缺差清單 → 逐符號 SCIP refs——「假 0 callers」的直接解法。

    兩遍式（861 項逐項全掃＝小時級）；graph_audit 經 subprocess
    ``sys.executable -m``（env 檢查＋exit code 契約全在其 main() 重用）。
    ``repo.resolve()`` 正規化——graph_audit 的 file 鍵是 resolved 絕對路徑，
    非 canonical ``--repo``（symlink 別名）會讓每項歸屬失敗（refs 恆 0）。
    """
    repo = repo.resolve()
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "code_reality.graph_audit",
                "--repo",
                str(repo),
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,  # 退出碼 0/1/2 本身是契約——returncode 由呼叫端判讀
        )
    except subprocess.TimeoutExpired:
        print("[FAIL] graph_audit 逾時", file=sys.stderr)
        return 2
    if proc.returncode == 2:
        print(f"[FAIL] graph_audit 環境錯誤：{proc.stderr.strip()}", file=sys.stderr)
        return 2
    if proc.returncode not in (0, 1) or not proc.stdout.strip():
        print(f"[FAIL] graph_audit 異常退出 {proc.returncode}", file=sys.stderr)
        return 2
    try:
        missing = json.loads(proc.stdout)["missing"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[FAIL] graph_audit 輸出異常：{e}", file=sys.stderr)
        return 2

    print(f"[OK] graph_audit 缺差 {len(missing)} 項 → 逐項 SCIP refs 對照：")
    index = load_index(index_path)

    files_by_name: dict[str, set[str]] = {}  # name → {rel path}
    for m in missing:
        m["_rel"] = _repo_rel(str(m["file"]), repo)
        files_by_name.setdefault(m["symbol"], set()).add(m["_rel"])

    target_symbols = audit_targets(index.documents, files_by_name)
    refs_count = find_refs(index, set(target_symbols))

    with_refs = 0
    for m in missing:
        r_list = missing_refs(m, target_symbols, refs_count)
        if r_list:
            with_refs += 1
        print(
            f"  {m['_rel']}: {m['symbol']}({m['db_count']}/{m['ra_count']})"
            f" → SCIP refs {len(r_list)}"
        )
    print(f"[OK] {with_refs}/{len(missing)} 項在 SCIP 有 refs（非零 callers）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", nargs="?", help="Type.method 或裸函數名")
    parser.add_argument(
        "--index",
        type=Path,
        required=True,
        help="SCIP index 路徑（生成命令見 docstring；rebase 後需重生）",
    )
    parser.add_argument(
        "--audit", action="store_true", help="graph_audit 缺差 → SCIP refs 對照"
    )
    parser.add_argument(
        "--repo", type=Path, default=None, help="audit 模式目標 repo（graph_audit）"
    )
    args = parser.parse_args()

    if scip_pb2 is None:
        print(
            "[FAIL] protobuf 未安裝——scip_pb2（vendored gencode）需要 "
            "google.protobuf runtime（uv add --group dev protobuf，或單發 "
            "uv run --with protobuf）",
            file=sys.stderr,
        )
        return 2
    if args.audit and args.query:
        print("[FAIL] --audit 與查詢字串互斥", file=sys.stderr)
        return 2
    if args.audit and args.repo is None:
        print("[FAIL] --audit 需 --repo（graph_audit 目標）", file=sys.stderr)
        return 2
    if not args.index.exists():
        print(f"[FAIL] 索引不在：{args.index}", file=sys.stderr)
        return 2
    if args.audit:
        return audit_mode(args.index, args.repo)
    if not args.query:
        print("[FAIL] 需提供查詢或 --audit", file=sys.stderr)
        return 2
    return report(load_index(args.index), args.query)


if __name__ == "__main__":
    sys.exit(main())
