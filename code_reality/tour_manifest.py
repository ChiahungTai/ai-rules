"""corpus provenance manifest——.tours/manifest.toml 讀寫。

derived/curated 二分的機械載體：source×generator×anchored_commit。
curated＝generator "manual"；重產 diff 非空的 derived 由 audit 建議升 manual（不覆蓋）。
"""

import argparse
import subprocess
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


def git_head(repo: Path) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        print(f"[WARN] git HEAD 取不到（{repo} 非 git repo？）——anchored_commit 記 unknown")
        return "unknown"
    return out.stdout.strip()


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    if tomllib is None:  # pragma: no cover
        raise RuntimeError("需要 Python 3.11+（tomllib）")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def upsert(
    data: dict,
    rel: str,
    *,
    generator: str,
    sources: list[str],
    commit: str,
) -> dict:
    rows = data.setdefault("tour", {})
    rows[rel] = {
        "generator": generator,
        "sources": sources,
        "anchored_commit": commit,
    }
    return data


def _kv(key: str, val: str) -> str:
        return f'{key} = "{val}"'


def dump(path: Path, data: dict) -> None:
    lines = [f"version = {data.get('version', 1)}"]
    for rel in sorted(data.get("tour", {})):
        row = data["tour"][rel]
        lines.append(f'\n[tour."{rel}"]')
        lines.append(_kv("generator", row["generator"]))
        srcs = ", ".join(f'"{s}"' for s in row.get("sources", []))
        lines.append(f"sources = [{srcs}]")
        lines.append(_kv("anchored_commit", row["anchored_commit"]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def tours_root_of(out_dir: Path) -> Path:
    """out_dir（如 .tours/arch/<stem>）往上找名為 .tours 的根；找不到一路上至 filesystem root——呼叫端以 ``name != ".tours"`` 判定非 corpus 樹。"""
    p = out_dir.resolve()
    while p.name and p.name != ".tours" and p.parent != p:
        p = p.parent
    return p


def init_scan(
    repo: Path,
    tours_dir: Path,
    *,
    generator_rule: str = "chain",
) -> dict:
    """掃 corpus 補 manifest——只補缺行（既有行不覆蓋：generator 原生寫入的 sources 保留）；generator 以檔名慣例猜（`chain-*` 或純序號 `NN.tour`→chain_tour、其餘 manual）、sources 留空。"""
    path = repo / tours_dir / "manifest.toml"
    data = load(path) if path.exists() else {}
    data.setdefault("version", 1)
    data.setdefault("tour", {})
    commit = git_head(repo)
    for f in sorted((repo / tours_dir).rglob("*.tour")):
        rel_path = f.relative_to(repo / tours_dir)
        if any(d in rel_path.parts[:-1] for d in ("delta", "dev-fixture")):
            continue  # 時間層可再生／開發假資料——非 manifest 範圍
        rel = rel_path.as_posix()
        if rel in data["tour"]:
            continue
        gen = (
            "chain_tour"
            if generator_rule == "chain"
            and (f.name.startswith("chain-") or (f.stem.isascii() and f.stem.isdigit()))
            else "manual"
        )
        upsert(data, rel, generator=gen, sources=[], commit=commit)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="manifest 讀寫／--init-scan 骨架生成")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--tours-dir", type=Path, default=Path(".tours"))
    parser.add_argument("--init-scan", action="store_true", help="掃 corpus 生成 manifest 骨架")
    args = parser.parse_args()
    path = args.repo / args.tours_dir / "manifest.toml"
    if not args.init_scan:
        print(f"[OK] manifest path: {path}（exists={path.exists()}）")
        return
    data = init_scan(args.repo, args.tours_dir)
    dump(path, data)
    print(f"[OK] manifest init: {len(data['tour'])} rows -> {path}")


if __name__ == "__main__":
    main()
