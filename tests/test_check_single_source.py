"""check_single_source 的 invariant 檢查單元測試（T1-2/T1-3）。"""

import json
from pathlib import Path

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


# ---------------------------------------------------------------------------
# zcode_live_parity：template 接線必須已部署 live（F8 形狀：註冊≠fire）
# ---------------------------------------------------------------------------


def _parity_inv():
    return next(i for i in css.INVARIANTS if i["id"] == "zcode_live_parity")


TPL_JSON = {
    "hooks": {
        "events": {
            "PreToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "process",
                            "command": "python3",
                            "args": ["/x/hooks/ok.py"],
                        }
                    ],
                }
            ]
        }
    }
}


def _write_tpl(tmp_path):
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "zcode-registration.json").write_text(
        json.dumps(TPL_JSON), encoding="utf-8"
    )


def _ok_group(matcher="Edit|Write", path="/x/hooks/ok.py"):
    return [
        {
            "matcher": matcher,
            "hooks": [{"type": "process", "command": "python3", "args": [path]}],
        }
    ]


def _live(tmp_path, events, enabled=True):
    live = tmp_path / "live.json"
    live.write_text(
        json.dumps({"hooks": {"enabled": enabled, "events": events}}), encoding="utf-8"
    )
    return live


def test_parity_missing_in_live_critical(tmp_path, monkeypatch):
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    findings = css.check_zcode_live_parity(
        _parity_inv(), live_path=_live(tmp_path, events={})
    )
    assert len(findings) == 1
    assert findings[0][1] == "critical"
    assert "ok.py" in findings[0][2]


def test_parity_all_registered_ok(tmp_path, monkeypatch):
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = _live(tmp_path, events={"PreToolUse": _ok_group()})
    assert css.check_zcode_live_parity(_parity_inv(), live_path=live) == []


def test_parity_live_absent_skip(tmp_path, monkeypatch):
    """SM-5：非 ZCode 機器（live config 缺場）skip 不 false positive。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    assert (
        css.check_zcode_live_parity(_parity_inv(), live_path=tmp_path / "nope.json")
        == []
    )


def test_parity_disabled_critical(tmp_path, monkeypatch):
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = _live(tmp_path, events={"PreToolUse": _ok_group()}, enabled=False)
    findings = css.check_zcode_live_parity(_parity_inv(), live_path=live)
    assert len(findings) == 1
    assert "enabled" in findings[0][2]


def test_parity_template_missing_important(tmp_path, monkeypatch):
    """Y4：template 缺席→important（INVARIANTS 路徑 typo 不炸整個 checker）。"""
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    findings = css.check_zcode_live_parity(
        _parity_inv(), live_path=tmp_path / "live.json"
    )
    assert len(findings) == 1
    assert findings[0][1] == "important"


def test_parity_live_bad_json_important(tmp_path, monkeypatch):
    """A4：live config 手改壞→important（非 crash）。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = tmp_path / "live.json"
    live.write_text("not-json", encoding="utf-8")
    findings = css.check_zcode_live_parity(_parity_inv(), live_path=live)
    assert len(findings) == 1
    assert findings[0][1] == "important"


def test_parity_wrong_matcher_critical(tmp_path, monkeypatch):
    """C6③：檔名在 live 但掛錯 matcher（Edit|Write 掛成 Bash）＝未部署。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = _live(tmp_path, events={"PreToolUse": _ok_group(matcher="Bash")})
    findings = css.check_zcode_live_parity(_parity_inv(), live_path=live)
    assert len(findings) == 1
    assert findings[0][1] == "critical"


def test_parity_suffix_lookalike_critical(tmp_path, monkeypatch):
    """C6③：`ok.py.bak` 殘字樣不算 ok.py 已部署（negative lookahead）。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = _live(tmp_path, events={"PreToolUse": _ok_group(path="/x/hooks/ok.py.bak")})
    findings = css.check_zcode_live_parity(_parity_inv(), live_path=live)
    assert len(findings) == 1
    assert findings[0][1] == "critical"


def test_parity_live_hooks_not_dict_important(tmp_path, monkeypatch):
    """C5③：live hooks 區塊結構異常（合法 JSON 非 object）→important 非 crash。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = tmp_path / "live.json"
    live.write_text('{"hooks": [1]}', encoding="utf-8")
    findings = css.check_zcode_live_parity(_parity_inv(), live_path=live)
    assert len(findings) == 1
    assert findings[0][1] == "important"


def test_parity_command_string_wiring_ok(tmp_path, monkeypatch):
    """接線形態 robustness：Claude 式 command 字串（無 args）也算已部署。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = tmp_path / "live.json"
    live.write_text(
        json.dumps(
            {
                "hooks": {
                    "enabled": True,
                    "events": {
                        "PreToolUse": [
                            {
                                "matcher": "Edit|Write",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python3 /x/hooks/ok.py",
                                    }
                                ],
                            }
                        ]
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    assert css.check_zcode_live_parity(_parity_inv(), live_path=live) == []


def test_parity_hook_disabled_in_live_critical(tmp_path, monkeypatch):
    """F1①：live 單條 hook enabled:false＝看得到接線、看不到 fire（第三形態）。"""
    _write_tpl(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    live = tmp_path / "live.json"
    live.write_text(
        json.dumps(
            {
                "hooks": {
                    "enabled": True,
                    "events": {
                        "PreToolUse": [
                            {
                                "matcher": "Edit|Write",
                                "hooks": [
                                    {
                                        "type": "process",
                                        "command": "python3",
                                        "args": ["/x/hooks/ok.py"],
                                        "enabled": False,
                                    }
                                ],
                            }
                        ]
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    findings = css.check_zcode_live_parity(_parity_inv(), live_path=live)
    assert len(findings) == 1
    assert findings[0][1] == "critical"


# --- agents_projection_sync（AIR-29）：subprocess 委派四路 ---


class _Proc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _projection_inv():
    css = load_module("skills/scan-project/scripts/check_single_source.py")
    return next(i for i in css.INVARIANTS if i["id"] == "agents_projection_sync")


def _stub_generator(css, tmp_path, inv):
    gen = tmp_path / inv["generator"]
    gen.parent.mkdir(parents=True, exist_ok=True)
    gen.write_text("#!/usr/bin/env python3\n", encoding="utf-8")


def test_projection_sync_green(tmp_path, monkeypatch):
    css = load_module("skills/scan-project/scripts/check_single_source.py")
    inv = _projection_inv()
    _stub_generator(css, tmp_path, inv)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css.subprocess, "run", lambda *a, **k: _Proc())
    assert css.check_agents_projection_sync(inv) == []


def test_projection_sync_drift_critical(tmp_path, monkeypatch):
    css = load_module("skills/scan-project/scripts/check_single_source.py")
    inv = _projection_inv()
    _stub_generator(css, tmp_path, inv)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        css.subprocess,
        "run",
        lambda *a, **k: _Proc(returncode=1, stdout="agents/zcode/foo.md\n"),
    )
    findings = css.check_agents_projection_sync(inv)
    assert len(findings) == 1
    assert findings[0][1] == "critical"
    assert "foo.md" in findings[0][2]


def test_projection_sync_uv_missing_important(tmp_path, monkeypatch):
    css = load_module("skills/scan-project/scripts/check_single_source.py")
    inv = _projection_inv()
    _stub_generator(css, tmp_path, inv)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)

    def boom(*a, **k):
        raise FileNotFoundError("uv not in PATH")

    monkeypatch.setattr(css.subprocess, "run", boom)
    findings = css.check_agents_projection_sync(inv)
    assert len(findings) == 1
    assert findings[0][1] == "important"


def test_projection_sync_generator_missing_important(tmp_path, monkeypatch):
    css = load_module("skills/scan-project/scripts/check_single_source.py")
    inv = _projection_inv()
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)  # generator 不存在
    findings = css.check_agents_projection_sync(inv)
    assert len(findings) == 1
    assert findings[0][1] == "important"


# ---------------------------------------------------------------------------
# deploy_freshness：worktree authority——非 main worktree 的差異不誤報 stale
# （codex 09-06 審查 I-1：舊 worktree 跑 checker 曾把健康部署誤報 critical
# 並開出無條件 deploy 處方——會用非權威版本覆寫三個 harness）
# ---------------------------------------------------------------------------

_MARKER = "Generated by scripts/deploy_agents.py -- do not edit directly."


def _freshness_inv():
    return next(i for i in css.INVARIANTS if i["id"] == "deploy_bundle_freshness")


def _fake_deploy_repo(tmp_path: Path) -> Path:
    """tmp repo：假 deploy_agents.py（自帶 HEADER/TARGETS/build_bundle）＋已部署 target。"""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    target = tmp_path / "deployed.md"
    target.write_text(_MARKER + "\nSTALE", encoding="utf-8")
    (scripts / "deploy_agents.py").write_text(
        "from pathlib import Path\n"
        "RULES_DIR = Path(__file__).parent\n"
        f"HEADER = {_MARKER!r}\n"
        f"TARGETS = [Path({str(target)!r})]\n"
        "def discover_rules(d, scopes):\n    return []\n"
        "def build_bundle(paths, label):\n    return 'NEW-BUNDLE'\n",
        encoding="utf-8",
    )
    return tmp_path


def test_deploy_freshness_mismatch_in_main_worktree_is_critical(tmp_path, monkeypatch):
    _fake_deploy_repo(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css, "_main_worktree", lambda: tmp_path)
    monkeypatch.setattr(css, "_is_detached_head", lambda: False)
    findings = css.check_deploy_freshness(_freshness_inv())
    assert len(findings) == 1
    assert findings[0][1] == "critical"
    assert "deploy_agents.py" in findings[0][2]  # main worktree 才給 deploy 處方


def test_deploy_freshness_mismatch_in_linked_worktree_downgrades(tmp_path, monkeypatch):
    _fake_deploy_repo(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css, "_main_worktree", lambda: Path("/elsewhere/canonical"))
    findings = css.check_deploy_freshness(_freshness_inv())
    assert len(findings) == 1
    assert findings[0][1] == "important"
    assert "非 main worktree" in findings[0][2]
    assert "勿在非 main worktree" in findings[0][2]  # 不得開無條件 deploy 處方


def test_deploy_freshness_worktree_undeterminable_downgrades(tmp_path, monkeypatch):
    _fake_deploy_repo(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css, "_main_worktree", lambda: None)
    findings = css.check_deploy_freshness(_freshness_inv())
    assert len(findings) == 1
    assert findings[0][1] == "important"


def test_deploy_freshness_detached_head_downgrades(tmp_path, monkeypatch):
    _fake_deploy_repo(tmp_path)
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css, "_main_worktree", lambda: tmp_path)
    monkeypatch.setattr(css, "_is_detached_head", lambda: True)
    findings = css.check_deploy_freshness(_freshness_inv())
    assert len(findings) == 1
    assert findings[0][1] == "important"
    assert "detached" in findings[0][2]


# ---------------------------------------------------------------------------
# shell_provenance：殼 provenance gate 委派（followup B2c——lint 必須接進
# 機械閘門，不能只靠自身 unit test）
# ---------------------------------------------------------------------------


def _shell_inv():
    return next(i for i in css.INVARIANTS if i["id"] == "report_shell_provenance")


def test_shell_provenance_violations_parsed_to_important(tmp_path, monkeypatch):
    import types

    css = load_module("skills/scan-project/scripts/check_single_source.py")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_report_shells.py").write_text("pass\n")
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css.shutil, "which", lambda _: "/usr/local/bin/uv")

    def fake_run(cmd, **kw):
        return types.SimpleNamespace(
            returncode=1,
            stdout="[FAIL] a/index.html: 同殼宣告多個互斥 projection SHA\n",
            stderr="",
        )

    monkeypatch.setattr(css.subprocess, "run", fake_run)
    findings = css.check_shell_provenance(_shell_inv())
    assert len(findings) == 1
    assert findings[0][1] == "important"
    assert "互斥" in findings[0][2]


def test_shell_provenance_clean_returns_empty(tmp_path, monkeypatch):
    import types

    css = load_module("skills/scan-project/scripts/check_single_source.py")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_report_shells.py").write_text("pass\n")
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(css.shutil, "which", lambda _: "/usr/local/bin/uv")
    monkeypatch.setattr(
        css.subprocess,
        "run",
        lambda cmd, **kw: types.SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    assert css.check_shell_provenance(_shell_inv()) == []


def test_shell_provenance_script_missing_important(tmp_path, monkeypatch):
    css = load_module("skills/scan-project/scripts/check_single_source.py")
    monkeypatch.setattr(css, "REPO_ROOT", tmp_path)
    findings = css.check_shell_provenance(_shell_inv())
    assert len(findings) == 1
    assert findings[0][1] == "important"
