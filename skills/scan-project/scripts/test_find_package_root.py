#!/usr/bin/env python3
"""Regression tests for _find_package_root (deterministic selection).

Guards the iterdir()-order regression: adding a new __init__.py (e.g.
tools/lsp_mcp/) must not flip which directory is resolved as the package
root. The old unsorted-iterdir() implementation returned whichever
 qualifying child the filesystem happened to yield first, which silently
 produced hundreds of false-positive findings when fs order changed.

Run: uv run python test_find_package_root.py
Exit 0 = all pass; nonzero = failure.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scan_project import _find_package_root  # noqa: E402


def _make_pkg(path: Path, py_count: int = 1) -> None:
    """Create a directory that looks like a package (has __init__.py)."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "__init__.py").touch()
    for i in range(py_count):
        (path / f"mod_{i}.py").touch()


def _check(label: str, condition: bool, detail: str = "") -> bool:
    tag = "[OK] " if condition else "[FAIL] "
    print(f"{tag}{label}{(' — ' + detail) if detail else ''}")
    return condition


def test_pyproject_declaration_wins() -> bool:
    """Priority 2: [tool.setuptools.packages.find] include is authoritative.

    Adversarial layout: tests/ is the biggest dir, but the declared package
    must still be selected. This is the direct regression repro.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_pkg(root / "lab", py_count=4)
        _make_pkg(root / "mosaic_alpha", py_count=10)
        _make_pkg(root / "tests", py_count=999)  # biggest, must NOT win
        _make_pkg(root / "tools", py_count=3)
        # The trigger: a nested package under tools/ (mirrors tools/lsp_mcp)
        _make_pkg(root / "tools" / "lsp_mcp")
        (root / "pyproject.toml").write_text(
            '[project]\nname = "mosaic-alpha"\n\n'
            "[tool.setuptools.packages.find]\n"
            'include = ["mosaic_alpha*"]\n'
        )
        result = _find_package_root(root)
        ok = result is not None and result.name == "mosaic_alpha"
        return _check("pyproject declaration wins over bigger tests/", ok, str(result))


def test_glob_and_dotted_declared_names() -> bool:
    """Declared names may be globs or dotted; first segment resolves."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_pkg(root / "my_pkg")
        _make_pkg(root / "tests", py_count=999)
        (root / "pyproject.toml").write_text(
            "[tool.setuptools]\npackages = ['my_pkg.sub']\n"
        )
        result = _find_package_root(root)
        ok = result is not None and result.name == "my_pkg"
        return _check("dotted declared name resolves to first segment", ok, str(result))


def test_name_match_when_no_package_declaration() -> bool:
    """Priority 3: pyproject with only [project] name -> normalized dir match."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_pkg(root / "lab")
        _make_pkg(root / "my_pkg")  # matches "my-pkg" normalized
        _make_pkg(root / "tests", py_count=999)
        (root / "pyproject.toml").write_text('[project]\nname = "my-pkg"\n')
        result = _find_package_root(root)
        ok = result is not None and result.name == "my_pkg"
        return _check("[project] name normalized match wins", ok, str(result))


def test_size_fallback_excludes_non_package_dirs() -> bool:
    """Priority 4: no signals -> largest code candidate, tests/ excluded."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_pkg(root / "alpha", py_count=5)
        _make_pkg(root / "beta", py_count=10)
        _make_pkg(root / "tests", py_count=999)  # excluded by NON_PACKAGE_DIRS
        result = _find_package_root(root)
        ok = result is not None and result.name == "beta"
        return _check("fallback picks largest code dir, not tests/", ok, str(result))


def test_size_tiebreak_is_deterministic() -> bool:
    """Priority 4 tie-break: equal .py count -> sorted (alphabetical) name.

    Pins the docstring claim "ties resolve deterministically" — the original
    bug was non-determinism, so the tie-break path must be mechanically
    guarded, not left as an implicit invariant of the sorted pool.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_pkg(root / "zebra", py_count=3)
        _make_pkg(root / "alpha", py_count=3)
        _make_pkg(root / "mid", py_count=3)  # all equal -> tie-break by name
        result = _find_package_root(root)
        ok = result is not None and result.name == "alpha"
        return _check("equal-size tie-break picks alphabetical first", ok, str(result))


def test_poetry_declaration_wins() -> bool:
    """Priority 2 poetry branch: [[tool.poetry.packages]] include is honoured."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_pkg(root / "lab")
        _make_pkg(root / "my_pkg")
        _make_pkg(root / "tests", py_count=999)
        (root / "pyproject.toml").write_text(
            "[tool.poetry]\nname = " + '"my-project"\n\n'
            "[[tool.poetry.packages]]\n"
            'include = "my_pkg"\n'
        )
        result = _find_package_root(root)
        ok = result is not None and result.name == "my_pkg"
        return _check("poetry [[tool.poetry.packages]] include wins", ok, str(result))


def test_project_root_itself_is_package() -> bool:
    """Priority 1: project_root has __init__.py -> returns project_root."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "__init__.py").touch()
        result = _find_package_root(root)
        return _check("project_root with __init__.py returns itself", result == root)


def test_no_candidates_returns_none() -> bool:
    """No qualifying dir -> None (scanner skips package-root-relative checks)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "README.md").touch()
        result = _find_package_root(root)
        return _check("no candidates -> None", result is None)


def test_deterministic_across_runs() -> bool:
    """Same adversarial layout in N fresh tmpdirs -> always same selection."""
    selection = None
    for _ in range(20):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_pkg(root / "lab")
            _make_pkg(root / "mosaic_alpha", py_count=10)
            _make_pkg(root / "tests", py_count=999)
            _make_pkg(root / "tools")
            (root / "pyproject.toml").write_text(
                '[tool.setuptools.packages.find]\ninclude = ["mosaic_alpha*"]\n'
            )
            result = _find_package_root(root)
            name = result.name if result else None
            if selection is None:
                selection = name
            elif name != selection:
                return _check(
                    "deterministic across 20 fresh tmpdirs",
                    False,
                    f"got {name}, expected {selection}",
                )
    return _check(
        "deterministic across 20 fresh tmpdirs",
        selection == "mosaic_alpha",
        f"selection={selection}",
    )


def main() -> int:
    print("[ACTION] _find_package_root regression tests: start")
    tests = [
        test_pyproject_declaration_wins,
        test_glob_and_dotted_declared_names,
        test_name_match_when_no_package_declaration,
        test_size_fallback_excludes_non_package_dirs,
        test_size_tiebreak_is_deterministic,
        test_poetry_declaration_wins,
        test_project_root_itself_is_package,
        test_no_candidates_returns_none,
        test_deterministic_across_runs,
    ]
    results = [t() for t in tests]
    passed = sum(results)
    total = len(results)
    tag = "[OK] " if passed == total else "[FAIL] "
    print(f"{tag}{passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
