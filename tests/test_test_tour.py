"""test_tour 單元測試——AST 枚舉／步生成／manifest row。"""

import json
from pathlib import Path

from code_reality import test_tour

SAMPLE = '''\
def test_module_level():
    """模組級案例。"""
    assert True


class TestGroup:
    def test_in_class(self):
        assert True

    def helper(self):
        return 1


def not_a_test():
    return 2
'''


def test_collect_module_and_class_level(tmp_path):
    f = tmp_path / "test_sample.py"
    f.write_text(SAMPLE, encoding="utf-8")
    tests = test_tour.collect_tests(f)
    names = [t["name"] for t in tests]
    assert names == ["test_module_level", "TestGroup.test_in_class"]
    assert tests[0]["doc"] == "模組級案例。"
    assert tests[0]["line"] == 1


def test_run_writes_tour_and_manifest(tmp_path, monkeypatch):
    repo = tmp_path
    tdir = repo / "tests" / "unit"
    tdir.mkdir(parents=True)
    (tdir / "test_alpha.py").write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(test_tour.tour_manifest, "git_head", lambda r: "c0ffee")
    written = test_tour.run(repo, Path("tests/unit"), None, set())
    assert len(written) == 1
    tour = json.loads(written[0].read_text(encoding="utf-8"))
    assert tour["title"].startswith("01 - tests/")
    assert len(tour["steps"]) == 2
    s0 = tour["steps"][0]
    assert s0["line"] == 1
    assert s0["description"].startswith(">> pytest tests/unit/test_alpha.py::test_module_level")
    src = (repo / s0["file"]).read_text(encoding="utf-8").splitlines()
    import re

    assert re.search(s0["pattern"], src[s0["line"] - 1])
    data = test_tour.tour_manifest.load(repo / ".tours" / "manifest.toml")
    rows = data["tour"]
    assert len(rows) == 1
    row = next(iter(rows.values()))
    assert row["generator"] == "test_tour" and row["sources"] == ["tests/unit/test_alpha.py"]
