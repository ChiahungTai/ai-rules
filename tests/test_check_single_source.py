"""check_single_source 的 invariant 檢查單元測試（T1-2/T1-3）。"""

from conftest import load_module

css = load_module("skills/scan-project/scripts/check_single_source.py")


def test_extract_schema_block_found():
    text = '### DimensionVerdict schema\n\n```json\n{"a": 1}\n```\n'
    assert css.extract_schema_block(text, "DimensionVerdict") == '{"a": 1}'


def test_extract_schema_block_missing():
    assert css.extract_schema_block("no schema here", "X") is None


def _hook_inv():
    return next(i for i in css.INVARIANTS if i["id"] == "hook_registration")


def test_hook_registration_orphan_detected(tmp_path, monkeypatch):
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "ok.py").write_text("pass")
    (tmp_path / "hooks" / "orphan.py").write_text("pass")
    (tmp_path / "settings.json").write_text(
        '"command": "python3 /x/hooks/ok.py"', encoding="utf-8"
    )
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    findings = css.check_hook_registration(_hook_inv())
    assert len(findings) == 1
    assert findings[0][1] == "critical"
    assert "orphan.py" in findings[0][2]


def test_hook_registration_all_registered(tmp_path, monkeypatch):
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "a.py").write_text("pass")
    (tmp_path / "hooks" / "b.py").write_text("pass")
    (tmp_path / "settings.json").write_text("a.py b.py", encoding="utf-8")
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    assert css.check_hook_registration(_hook_inv()) == []


def test_hook_registration_missing_reg_file_skipped(tmp_path, monkeypatch):
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "a.py").write_text("pass")
    # settings.json 不存在（local/gitignored 機器）→ skip 不 false positive，
    # 但 zcode-registration.json 也不存在時仍應全部抓孤兒
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    findings = css.check_hook_registration(_hook_inv())
    assert len(findings) == 1
