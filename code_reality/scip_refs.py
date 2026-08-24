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
stdout）＋生成後 stamp 版本 sidecar（⑤標註資料面）::

    mkdir -p ~/.mosaic/code-reality/scip/<repo-basename> \\
        && cd ~/.mosaic/code-reality/scip/<repo-basename> \\
        && rust-analyzer scip <repo-root>
    uv run --project ~/Github/ai-rules python -m code_reality.scip_refs \\
        --stamp-meta --repo <repo-root>

索引慣例（repo-keyed slot）：有 ``--repo`` 時 ``--index`` 可省略——解析
``~/.mosaic/code-reality/scip/<repo-basename>/index.scip``（多 repo 共用
全局單一檔會互蓋）；顯式 ``--index`` 永遠優先；query 模式無 ``--repo``
仍需顯式 ``--index``。**既有全局 slot 索引搬遷**（免 8 分鐘重生成）：
``mkdir -p ~/.mosaic/code-reality/scip/<repo-basename> && mv
~/.mosaic/code-reality/scip/index.scip <dir>/``。

scip_pb2.py 重生（schema 變更時；grpcio-tools 內含 protoc；scip.proto
已 vendored 同目錄）::

    cd code_reality && uv run --with grpcio-tools python -m grpc_tools.protoc \\
        --proto_path=. --python_out=. scip.proto

用法::

    uv run --project ~/Github/ai-rules python -m code_reality.scip_refs \\
        EventStoreLifecycle.open --index <anywhere>/index.scip  # 顯式覆蓋
    uv run --project ~/Github/ai-rules python -m code_reality.scip_refs \\
        EventStoreLifecycle.open --repo <repo-root>     # 預設 slot
    uv run --project ~/Github/ai-rules python -m code_reality.scip_refs \\
        --audit --repo <repo-root>                       # 預設 slot

source 標註（facade 契約「每回應附 source 與 commit 版本」）：stamp 過
sidecar 或給 ``--repo`` 的回應，輸出首行帶 ``[SRC] scip index @ <sha>``
（· ``repo HEAD @ <sha>``）；sidecar 與 HEAD 不一致 → WARN（漂移守衛——
A3 graph.db 過時事件同型防線）。顯式 ``--index`` 無 sidecar 無 ``--repo``
→ 無 [SRC] 行，legacy 輸出位元組不變（NT 查詢契約）。

退出碼：0=有結果｜1=查無｜2=環境錯誤（索引不在/損壞/protobuf 未裝/
graph_audit 子進程失敗/stamp 取不到 HEAD）。原型取舍：每次查詢重新解析
索引（~40s）——常駐/衍生 sqlite 快取為後續優化點。
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

try:
    from code_reality import scip_pb2  # vendored gencode（需 protobuf runtime）
except ImportError:
    scip_pb2 = None  # type: ignore[assignment]

FN_TAIL_RE = re.compile(r"(?<!\w)(\w+)\(\)\.$")

# repo-keyed slot 慣例（boundary sidecar 同族）：多 repo 共用全局單一
# index.scip 會互蓋——basename 為鍵（同名異路徑 repo 需顯式 --index）。
DEFAULT_INDEX_ROOT = Path.home() / ".mosaic" / "code-reality" / "scip"
META_SUFFIX = ".meta.json"


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


def report(index, query: str, src_line: str | None = None) -> int:
    if src_line:
        print(src_line)
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


def audit_mode(index_path: Path, repo: Path, src_line: str | None = None) -> int:
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

    if src_line:
        print(src_line)
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


def default_index_path(repo: Path) -> Path:
    """repo-keyed slot：``DEFAULT_INDEX_ROOT/<repo-basename>/index.scip``。

    ``resolve()`` 先行——相對 ``--repo .`` 取 cwd basename（不 resolve 的
    ``Path('.').name`` 是空字串，``/`` 空段會靜默塌縮回全局單檔＝①要防
    的互蓋）。
    """
    name = repo.resolve().name
    if not name:
        print(
            f"[FAIL] --repo {repo} 解析不出 repo 名——請給絕對路徑",
            file=sys.stderr,
        )
        sys.exit(2)
    return DEFAULT_INDEX_ROOT / name / "index.scip"


def meta_path(index_path: Path) -> Path:
    return index_path.parent / (index_path.name + META_SUFFIX)


def load_meta(index_path: Path) -> dict | None:
    p = meta_path(index_path)
    if not p.exists():
        return None
    try:
        meta = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] index meta 損壞（[SRC] 缺 index 版本）：{e}", file=sys.stderr)
        return None
    if not isinstance(meta, dict) or not isinstance(meta.get("head"), str):
        print("[WARN] index meta 形狀非預期（[SRC] 缺 index 版本）", file=sys.stderr)
        return None
    return meta


def _git_head(repo: Path) -> str | None:
    """repo live HEAD——取不到回 None＋WARN（標註輔助，不致命）。"""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("[WARN] git rev-parse 逾時——[SRC] 略過 repo HEAD", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("[WARN] git 不在 PATH——[SRC] 略過 repo HEAD", file=sys.stderr)
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        print(
            f"[WARN] git rev-parse 失敗——[SRC] 略過 repo HEAD：{proc.stderr.strip()}",
            file=sys.stderr,
        )
        return None
    return proc.stdout.strip()


def _short(sha: str) -> str:
    return sha[:7]


def source_line(index_path: Path, repo: Path | None) -> str | None:
    """facade 契約「每回應附 source 與 commit 版本」的輸出面。

    證據優先序：stamp sidecar 的 head（index 生成點真相）→ ``--repo``
    live HEAD（audit 端真相）。皆無 → None 不輸出（顯式 --index legacy
    呼叫輸出維持位元組不變——NT 查詢契約）。三道守衛（皆 WARN 不擋服務）：
    sidecar 比 index 檔舊（重生後未重 stamp）；stamp 的 repo 與 ``--repo``
    不符（同名 basename——sha 歸屬可能錯）；兩 sha 皆有但不一致（漂移——
    A3 graph.db 過時事件同型防線）。
    """
    stale_stamp = False
    try:
        stale_stamp = meta_path(index_path).stat().st_mtime < index_path.stat().st_mtime
    except OSError:
        stale_stamp = False
    meta = load_meta(index_path)
    idx_sha = meta.get("head") if meta else None
    repo_sha = _git_head(repo) if repo else None
    if idx_sha is None and repo_sha is None:
        return None
    if stale_stamp and meta is not None:
        print(
            "[WARN] stamp 比索引檔舊——索引重生成後未重 stamp（跑 --stamp-meta）",
            file=sys.stderr,
        )
    parts: list[str] = []
    if idx_sha:
        stamped = str(meta.get("stamped_at", ""))[:10]
        parts.append(
            f"scip index @ {_short(idx_sha)}" + (f"（{stamped}）" if stamped else "")
        )
    else:
        print(
            "[WARN] index meta 未 stamp（生成後跑 --stamp-meta）——[SRC] 缺 index 版本",
            file=sys.stderr,
        )
    if repo_sha:
        parts.append(f"repo HEAD @ {_short(repo_sha)}")
    if idx_sha and repo_sha:
        stamped_repo = meta.get("repo")
        if stamped_repo and stamped_repo != str(repo.resolve()):
            print(
                f"[WARN] stamp 的 repo（{stamped_repo}）與 --repo 不符——"
                "index sha 歸屬可能錯（同名 basename？改用顯式 --index）",
                file=sys.stderr,
            )
        if idx_sha != repo_sha:
            print(
                f"[WARN] repo HEAD 已離開 index 生成點（index @ {_short(idx_sha)}"
                f" vs HEAD @ {_short(repo_sha)}）——重生索引並重跑 --stamp-meta"
                "後再查",
                file=sys.stderr,
            )
    return "[SRC] " + " · ".join(parts)


def stamp_meta(index_path: Path, repo: Path) -> int:
    """資料面：索引生成後落版本 sidecar（重跑覆寫，冪等）。

    查詢端被動讀——未 stamp 的舊索引 [SRC] 缺 index 版本（WARN 提示），
    不拒絕服務。欄位刻意不共用 ``common.make_meta``：``head``/
    ``stamped_at`` 語義是「index 生成點」非產物創建時刻、``repo`` 存
    resolved 全路徑（同名異路徑 repo 排查用），且 make_meta 的
    ``check=True`` 裸 traceback 不合本工具 exit-2 契約。
    """
    head = _git_head(repo)
    if head is None:  # WARN 已印
        print("[FAIL] 取不到 repo HEAD——meta 未 stamp", file=sys.stderr)
        return 2
    sidecar = meta_path(index_path)
    payload = {
        "repo": str(repo.resolve()),
        "head": head,
        "stamped_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "tool": "code_reality.scip_refs",
    }
    try:
        sidecar.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        print(f"[FAIL] sidecar 寫入失敗：{sidecar}：{e}", file=sys.stderr)
        return 2
    print(f"[OK] meta stamped：{sidecar}（{repo.name} @ {_short(head)}）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", nargs="?", help="Type.method 或裸函數名")
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help=(
            "SCIP index 路徑（生成命令見 docstring；rebase 後需重生）；"
            "省略時以 --repo 解析 repo-keyed 預設 slot"
        ),
    )
    parser.add_argument(
        "--audit", action="store_true", help="graph_audit 缺差 → SCIP refs 對照"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help=(
            "目標 repo——audit 餵 graph_audit；--index 省略時解析預設 slot；"
            "補 [SRC] live HEAD 標註"
        ),
    )
    parser.add_argument(
        "--stamp-meta",
        action="store_true",
        help="索引生成後落版本 sidecar（配 --repo；[SRC] 標註的資料面）",
    )
    args = parser.parse_args()

    if args.stamp_meta and (args.audit or args.query):
        print("[FAIL] --stamp-meta 與 --audit/查詢互斥", file=sys.stderr)
        return 2
    if args.stamp_meta:
        if args.repo is None:
            print("[FAIL] --stamp-meta 需 --repo", file=sys.stderr)
            return 2
    elif scip_pb2 is None:  # stamp 不解析 index——protobuf 非其依賴
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

    default_resolved = False
    if args.index is None:
        if args.repo is None:
            print(
                "[FAIL] 需 --index（或 --repo 解析 repo-keyed 預設 slot）",
                file=sys.stderr,
            )
            return 2
        args.index = default_index_path(args.repo)
        default_resolved = True
    if not args.index.exists():
        if default_resolved:
            print(
                f"[FAIL] 預設索引不在：{args.index}"
                f"（--repo {args.repo} → repo-keyed slot；生成命令或搬遷見 docstring）",
                file=sys.stderr,
            )
            legacy = DEFAULT_INDEX_ROOT / "index.scip"
            if legacy.exists():
                print(
                    f"  既有全局 slot 索引可搬遷（免重生成；僅當該索引生成自"
                    f" --repo 指定的 repo——搬錯 repo 的索引會全域查無）："
                    f"mkdir -p {args.index.parent} && mv {legacy} {args.index.parent}/",
                    file=sys.stderr,
                )
        else:
            print(f"[FAIL] 索引不在：{args.index}", file=sys.stderr)
        return 2

    if args.stamp_meta:
        return stamp_meta(args.index, args.repo)
    if not args.audit and not args.query:
        print("[FAIL] 需提供查詢或 --audit", file=sys.stderr)
        return 2
    src_line = source_line(args.index, args.repo)
    if args.audit:
        return audit_mode(args.index, args.repo, src_line)
    return report(load_index(args.index), args.query, src_line)


if __name__ == "__main__":
    sys.exit(main())
