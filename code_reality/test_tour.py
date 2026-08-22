"""test case → tour 骨架——tests 作為 tour source（腐化最慢源）。

AST 直讀（不 spawn pytest）：每 test 檔一條 tour、每 test 函數一步。
pattern 錨 def test_*（天然抗漂）；description 首行 >> pytest（SHELL_SCRIPT_PATTERN
可執行步）。骨架免 LLM——敘事填充是後續人/LLM 策展層。
已知限制：parametrize 展開不可見（一個 test 一步，不做 case 展開）。
"""

import argparse
import ast
import json
import re
from pathlib import Path

from . import tour_manifest


def collect_tests(py: Path) -> list[dict]:
    tree = ast.parse(py.read_text(encoding="utf-8"))
    out: list[dict] = []

    def visit(node: ast.AST, prefix: str = "") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            elif isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef)
            ) and child.name.startswith("test"):
                doc = ast.get_docstring(child)
                out.append(
                    {
                        "name": prefix + child.name,
                        "bare": child.name,
                        "line": child.lineno,
                        "doc": ((doc or "").strip().splitlines() or [""])[0],
                    }
                )
            else:
                visit(child, prefix)

    visit(tree)
    out.sort(key=lambda s: s["line"])
    return out


def run(repo: Path, tests_dir: Path, out_dir: Path | None, primary: set[int]) -> list[Path]:
    tdir = repo / tests_dir
    files = [p for p in sorted(tdir.rglob("test_*.py"))]
    assert files, f"{tdir} 無 test_*.py"
    if out_dir is None:
        out_dir = Path(".tours") / "tests" / tests_dir.name
    out_abs = repo / out_dir
    out_abs.mkdir(parents=True, exist_ok=True)
    commit = tour_manifest.git_head(repo)
    mpath = tour_manifest.tours_root_of(out_abs) / "manifest.toml"
    data = tour_manifest.load(mpath)
    data.setdefault("version", 1)
    written: list[Path] = []
    for i, py in enumerate(files, start=1):
        tests = collect_tests(py)
        if not tests:
            continue
        rel = py.relative_to(repo).as_posix()
        steps = [
            {
                "file": rel,
                "line": t["line"],
                "title": t["name"],
                "description": (
                    f">> pytest {rel}::{t['name']}\n\n"
                    + (t["doc"] or "骨架步（test_tour 產）——敘事待策展")
                ),
                "pattern": f"^[ \\t]*def {re.escape(t['bare'])}\\(",
            }
            for t in tests
        ]
        title = f"{i:02d} - tests/{py.relative_to(tdir).as_posix()}"
        tour: dict = {"title": title, "steps": steps}
        if i in primary:
            tour["isPrimary"] = True
        dest = out_abs / f"tests-{i:02d}-{py.stem}.tour"
        dest.write_text(
            json.dumps(tour, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        written.append(dest)
        tour_manifest.upsert(
            data,
            dest.relative_to(tour_manifest.tours_root_of(out_abs)).as_posix(),
            generator="test_tour",
            sources=[rel],
            commit=commit,
        )
        print(f"[OK] test tour -> {dest}（{len(steps)} tests）")
    tour_manifest.dump(mpath, data)
    print(f"[OK] manifest upsert: {mpath}")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="tests → tour 骨架（AST 枚舉）")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--tests-dir", type=Path, required=True, help="如 tests/unit_tests/features")
    parser.add_argument("--out-dir", type=Path, default=None, help="預設 .tours/tests/<stem>/")
    parser.add_argument("--primary", default="", help="標 isPrimary 的檔編號（1-based 逗號分隔）")
    args = parser.parse_args()
    primary = {int(x) for x in args.primary.split(",") if x.strip()}
    run(args.repo, args.tests_dir, args.out_dir, primary)


if __name__ == "__main__":
    main()
