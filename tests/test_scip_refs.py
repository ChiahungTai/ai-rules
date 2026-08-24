"""scip_refs 單元測試——duck-typed fake index（不依賴 protobuf/scip_pb2）。

釘住查詢匹配邏輯（impl 變體＋trait 宣告位址兩符號形態＋``(?<!\\w)``
邊界）、DEF/refs 收集、audit **雙鍵歸屬**（(定義檔, 方法名)——只按檔
會把同檔鄰居 refs 聯集，原型審查 216→138 實證）、main() 退出碼契約
（0/1/2）與 load_index 截斷 sanity；repo-keyed 預設 slot（--repo 時
--index 可省略）與 [SRC] source 標註（stamp sidecar＋live HEAD＋漂移
守衛；顯式 --index 無證據時輸出位元組不變——NT 契約）。真索引 L4 基準：
NT 實測 --audit 138/861（.agent-tmp/research/scip/ 原型輪）。
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_reality import scip_refs
from code_reality.scip_refs import (
    _matcher,
    audit_targets,
    find_defs,
    find_refs,
    ln,
    load_index,
    loc,
    main,
    missing_refs,
    tail,
)


class FakeOcc:
    def __init__(self, symbol: str, roles: int, rng: list[int]):
        self.symbol = symbol
        self.symbol_roles = roles
        self.range = rng


class FakeDoc:
    def __init__(self, rel: str, occurrences: list[FakeOcc]):
        self.relative_path = rel
        self.occurrences = occurrences


class FakeIndex:
    def __init__(self, docs: list[FakeDoc]):
        self.documents = docs


IMPL = (
    "rust-analyzer cargo nautilus 1.0.0 crates/common/src/events.rs "
    "impl#[EventStoreLifecycle]open()."
)
TRAIT_IMPL = (
    "rust-analyzer cargo nautilus 1.0.0 crates/common/src/events.rs "
    "impl#[EventStoreLifecycle][EventStore]open()."
)
TRAIT_DECL = (
    "rust-analyzer cargo nautilus 1.0.0 crates/common/src/events.rs "
    "EventStoreLifecycle#open()."
)
OTHER_TYPE = (
    "rust-analyzer cargo nautilus 1.0.0 crates/common/src/other.rs "
    "impl#[OtherType]open()."
)


class TestMatcher:
    def test_type_method_matches_all_three_forms(self) -> None:
        match = _matcher("EventStoreLifecycle.open")
        assert match(IMPL)
        assert match(TRAIT_IMPL)
        assert match(TRAIT_DECL)  # trait 宣告位址——漏它＝低報 refs

    def test_type_method_rejects_other_type(self) -> None:
        match = _matcher("EventStoreLifecycle.open")
        assert not match(OTHER_TYPE)

    def test_word_boundary_rejects_prefixed_names(self) -> None:
        match = _matcher("EventStoreLifecycle.open")
        assert not match(IMPL.replace("]open().", "]my_open()."))
        assert not match(IMPL.replace("]open().", "]reopen()."))

    def test_bare_name_matches_any_type(self) -> None:
        match = _matcher("open_run")
        assert match(
            IMPL.replace("open().", "open_run().").replace(
                "[EventStoreLifecycle]", "[Config]"
            )
        )
        assert not match(IMPL.replace("open().", "my_open_run()."))

    def test_bare_name_ignores_type_marker(self) -> None:
        """裸查詢不含型別——任何 marker 上的同名方法都命中。"""
        match = _matcher("open")
        assert match(IMPL)
        assert match(OTHER_TYPE)


class TestFindDefsRefs:
    def test_defs_collect_def_role_only(self) -> None:
        idx = FakeIndex(
            [
                FakeDoc(
                    "crates/x.rs",
                    [
                        FakeOcc(IMPL, 1, [10, 0, 10, 5]),
                        FakeOcc(IMPL, 0, [30, 0, 30, 5]),  # ref——非 DEF
                        FakeOcc(OTHER_TYPE, 1, [50, 0, 50, 5]),
                    ],
                )
            ]
        )
        defs = find_defs(idx, "EventStoreLifecycle.open")
        assert list(defs) == [IMPL]
        assert defs[IMPL] == ["crates/x.rs:11"]

    def test_refs_collect_non_def_of_known_symbols(self) -> None:
        idx = FakeIndex(
            [
                FakeDoc(
                    "crates/y.rs",
                    [
                        FakeOcc(IMPL, 0, [7, 0, 7, 9]),
                        FakeOcc(TRAIT_DECL, 0, [9, 0, 9, 9]),
                        FakeOcc(OTHER_TYPE, 0, [11, 0, 11, 9]),  # 不在查詢集
                    ],
                )
            ]
        )
        refs = find_refs(idx, {IMPL, TRAIT_DECL})
        assert refs[IMPL] == ["crates/y.rs:8"]
        assert refs[TRAIT_DECL] == ["crates/y.rs:10"]
        assert OTHER_TYPE not in refs


class TestLocHelpers:
    def test_ln_one_based(self) -> None:
        assert ln(FakeOcc("s", 0, [4, 0, 4, 9])) == 5

    def test_ln_empty_range(self) -> None:
        assert ln(FakeOcc("s", 0, [])) == -1

    def test_loc_unknown_line(self) -> None:
        assert loc("f.rs", FakeOcc("s", 0, [])) == "f.rs:?"
        assert loc("f.rs", FakeOcc("s", 0, [2, 0, 2, 1])) == "f.rs:3"

    def test_tail_extracts_descriptor(self) -> None:
        assert tail(IMPL) == "impl#[EventStoreLifecycle]open()."
        assert tail("short.rs x#y().") == "short.rs x#y()."


class TestAuditDualKey:
    """(定義檔, 方法名) 雙鍵歸屬——同檔鄰居（不同方法名）refs 不得聯集。"""

    DOC = FakeDoc(
        "crates/x.rs",
        [
            FakeOcc("… impl#[A]push().", 1, [10, 0, 10, 5]),
            FakeOcc("… impl#[B]push().", 1, [20, 0, 20, 5]),
            FakeOcc("… impl#[A]pull().", 1, [30, 0, 30, 5]),  # 同檔鄰居方法
            FakeOcc("… impl#[A]push().", 0, [40, 0, 40, 5]),  # ref——非 DEF
        ],
    )

    def test_targets_match_missing_name_in_file(self) -> None:
        targets = audit_targets([self.DOC], {"push": {"crates/x.rs"}})
        # pull 不在缺差清單 → 不入 targets；push 的兩 impl 變體都入
        assert set(targets) == {"… impl#[A]push().", "… impl#[B]push()."}
        assert targets["… impl#[A]push()."] == ("crates/x.rs", "push")

    def test_targets_skip_files_not_in_missing(self) -> None:
        targets = audit_targets([self.DOC], {"push": {"crates/other.rs"}})
        assert targets == {}

    def test_missing_refs_unions_same_name_only(self) -> None:
        targets = audit_targets([self.DOC], {"push": {"crates/x.rs"}})
        refs_count = {
            "… impl#[A]push().": ["crates/y.rs:1"],
            "… impl#[B]push().": ["crates/z.rs:2"],
            "… impl#[A]pull().": ["crates/w.rs:3"],
        }
        m = {"symbol": "push", "_rel": "crates/x.rs"}
        # push 兩 impl 變體 refs 聯集（同 (檔, 名) 歸屬）；pull 不混入
        assert missing_refs(m, targets, refs_count) == [
            "crates/y.rs:1",
            "crates/z.rs:2",
        ]


class FakePb2Index:
    """load_index 測試替身——duck-typed scip_pb2.Index。"""

    def __init__(self, n_docs: int = 0, corrupt: bool = False):
        self._n = n_docs
        self._corrupt = corrupt
        self.documents = []

    def ParseFromString(self, data: bytes) -> None:
        if self._corrupt:
            raise ValueError("DecodeError: truncated")
        self.documents = [FakeDoc("f.rs", []) for _ in range(self._n)]


class TestLoadIndex:
    """截斷 sanity（教訓③第三項）——protobuf 無完整性校驗，截斷靜默假
    「查無」是這條 sanity 存在的全部理由。"""

    def _patch(self, monkeypatch, **kw) -> FakePb2Index:
        fake = FakePb2Index(**kw)
        monkeypatch.setattr(scip_refs, "scip_pb2", SimpleNamespace(Index=lambda: fake))
        return fake

    def test_corrupt_index_exits_2(self, tmp_path, monkeypatch, capsys) -> None:
        self._patch(monkeypatch, corrupt=True)
        p = tmp_path / "index.scip"
        p.write_bytes(b"junk")
        with pytest.raises(SystemExit) as ei:
            load_index(p)
        assert ei.value.code == 2
        assert "[FAIL]" in capsys.readouterr().err

    def test_zero_documents_exits_2(self, tmp_path, monkeypatch) -> None:
        self._patch(monkeypatch, n_docs=0)
        p = tmp_path / "index.scip"
        p.write_bytes(b"junk")
        with pytest.raises(SystemExit) as ei:
            load_index(p)
        assert ei.value.code == 2

    def test_small_index_warns_but_returns(self, tmp_path, monkeypatch, capsys) -> None:
        fake = self._patch(monkeypatch, n_docs=50)
        p = tmp_path / "index.scip"
        p.write_bytes(b"junk")
        idx = load_index(p)
        assert idx is fake
        assert len(idx.documents) == 50
        assert "[WARN]" in capsys.readouterr().err

    def test_healthy_index_no_warn(self, tmp_path, monkeypatch, capsys) -> None:
        self._patch(monkeypatch, n_docs=200)
        p = tmp_path / "index.scip"
        p.write_bytes(b"junk")
        load_index(p)
        assert "[WARN]" not in capsys.readouterr().err


class TestMainExitCodes:
    """退出碼契約 0/1/2（教訓③——NT 治理鉤子未來接線時漂移即靜默）。"""

    def _run(self, monkeypatch, argv: list[str]) -> int:
        monkeypatch.setattr(sys, "argv", ["scip_refs", *argv])
        return main()

    def _idx(self, tmp_path) -> Path:
        p = tmp_path / "index.scip"
        p.write_bytes(b"junk")
        return p

    def test_protobuf_missing_returns_2(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", None)
        assert self._run(monkeypatch, ["q", "--index", str(self._idx(tmp_path))]) == 2

    def test_audit_query_mutually_exclusive_returns_2(
        self, tmp_path, monkeypatch
    ) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        assert (
            self._run(
                monkeypatch,
                [
                    "q",
                    "--audit",
                    "--repo",
                    str(tmp_path),
                    "--index",
                    str(self._idx(tmp_path)),
                ],
            )
            == 2
        )

    def test_audit_without_repo_returns_2(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        assert (
            self._run(monkeypatch, ["--audit", "--index", str(self._idx(tmp_path))])
            == 2
        )

    def test_missing_index_returns_2(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        missing = tmp_path / "nope.scip"
        assert self._run(monkeypatch, ["q", "--index", str(missing)]) == 2

    def test_no_query_returns_2(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        assert self._run(monkeypatch, ["--index", str(self._idx(tmp_path))]) == 2

    def test_no_query_skips_source_line(self, tmp_path, monkeypatch, capsys) -> None:
        """審查 F6：無 query/audit 的錯誤路徑不跑 source_line——不多印
        meta WARN、不觸 git。"""
        monkeypatch.setattr(scip_refs, "scip_pb2", object())

        def boom(repo):
            raise AssertionError("source_line 不應觸 git")

        monkeypatch.setattr(scip_refs, "_git_head", boom)
        assert self._run(monkeypatch, ["--index", str(self._idx(tmp_path))]) == 2
        err = capsys.readouterr().err
        assert "需提供查詢" in err
        assert "未 stamp" not in err

    def test_query_no_def_returns_1(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        monkeypatch.setattr(scip_refs, "load_index", lambda p: FakeIndex([]))
        assert (
            self._run(monkeypatch, ["whatever", "--index", str(self._idx(tmp_path))])
            == 1
        )

    def test_query_with_def_returns_0(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        idx = FakeIndex([FakeDoc("crates/x.rs", [FakeOcc(IMPL, 1, [1, 0, 1, 5])])])
        monkeypatch.setattr(scip_refs, "load_index", lambda p: idx)
        assert (
            self._run(
                monkeypatch,
                ["EventStoreLifecycle.open", "--index", str(self._idx(tmp_path))],
            )
            == 0
        )


class TestRepoKeyedIndex:
    """①repo-keyed slot——多 repo 互蓋防護；顯式 --index 永遠優先。"""

    def test_default_slot_resolves_repo_basename(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        got = scip_refs.default_index_path(Path("/Users/x/Github/nt_v1"))
        assert got == tmp_path / "scip" / "nt_v1" / "index.scip"

    def test_relative_repo_resolves_cwd_basename(self, tmp_path, monkeypatch) -> None:
        """F1 釘住——不 resolve 的 ``Path('.').name`` 是空字串，會塌縮回
        全局單檔（①要防的互蓋）。"""
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        repo_dir = tmp_path / "nt_v1"
        repo_dir.mkdir()
        monkeypatch.chdir(repo_dir)
        assert scip_refs.default_index_path(Path(".")) == (
            tmp_path / "scip" / "nt_v1" / "index.scip"
        )


class TestMainIndexResolution:
    """①main 接線——--index 省略時走 --repo 預設 slot。"""

    def _run(self, monkeypatch, argv: list[str]) -> int:
        monkeypatch.setattr(sys, "argv", ["scip_refs", *argv])
        return main()

    def test_no_index_no_repo_returns_2(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        assert self._run(monkeypatch, ["q"]) == 2

    def test_default_slot_missing_returns_2(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        assert self._run(monkeypatch, ["q", "--repo", str(tmp_path / "myrepo")]) == 2
        err = capsys.readouterr().err
        assert "預設索引不在" in err
        assert "myrepo/index.scip" in err

    def test_default_slot_missing_with_legacy_shows_migration_hint(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        """審查 F1：legacy 全局 slot 有索引時——錯誤訊息附搬遷命令（免 8
        分鐘重生成誘導）。"""
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        (tmp_path / "scip").mkdir()
        (tmp_path / "scip" / "index.scip").write_bytes(b"junk")
        rc = self._run(monkeypatch, ["q", "--repo", str(tmp_path / "myrepo")])
        assert rc == 2
        err = capsys.readouterr().err
        assert "搬遷" in err and "mv" in err

    def test_audit_via_default_slot_resolves(self, tmp_path, monkeypatch) -> None:
        """審查 F4d：--audit --repo 經 main() 的 slot 解析接線。"""
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: None)
        idx_file = tmp_path / "scip" / "myrepo" / "index.scip"
        idx_file.parent.mkdir(parents=True)
        idx_file.write_bytes(b"junk")
        seen: list[Path] = []

        def fake_audit(index_path, repo, src_line=None):
            seen.append(index_path)
            return 0

        monkeypatch.setattr(scip_refs, "audit_mode", fake_audit)
        rc = self._run(monkeypatch, ["--audit", "--repo", str(tmp_path / "myrepo")])
        assert rc == 0
        assert seen == [idx_file]

    def test_default_slot_hit_loads_it(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: None)  # F6：不觸真 git
        idx_file = tmp_path / "scip" / "myrepo" / "index.scip"
        idx_file.parent.mkdir(parents=True)
        idx_file.write_bytes(b"junk")
        seen: list[Path] = []
        idx = FakeIndex([FakeDoc("crates/x.rs", [FakeOcc(IMPL, 1, [1, 0, 1, 5])])])
        monkeypatch.setattr(scip_refs, "load_index", lambda p: (seen.append(p), idx)[1])
        rc = self._run(
            monkeypatch,
            ["EventStoreLifecycle.open", "--repo", str(tmp_path / "myrepo")],
        )
        assert rc == 0
        assert seen == [idx_file]


class TestStampMeta:
    """⑤資料面——sidecar 落地（repo/head/stamped_at）；冪等覆寫。"""

    def _run(self, monkeypatch, argv: list[str]) -> int:
        monkeypatch.setattr(sys, "argv", ["scip_refs", *argv])
        return main()

    def test_stamps_sidecar_next_to_index(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", None)  # stamp 不需 protobuf
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "abcdef1234567890")
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        rc = self._run(
            monkeypatch,
            ["--stamp-meta", "--repo", str(tmp_path), "--index", str(idx)],
        )
        assert rc == 0
        meta = json.loads(
            (tmp_path / "index.scip.meta.json").read_text(encoding="utf-8")
        )
        assert meta["head"] == "abcdef1234567890"
        assert meta["repo"] == str(Path(tmp_path).resolve())
        assert meta["stamped_at"]
        assert "[OK] meta stamped" in capsys.readouterr().out

    def test_stamp_via_default_slot(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(scip_refs, "DEFAULT_INDEX_ROOT", tmp_path / "scip")
        monkeypatch.setattr(scip_refs, "scip_pb2", None)
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "abcdef1234")
        idx = tmp_path / "scip" / "myrepo" / "index.scip"
        idx.parent.mkdir(parents=True)
        idx.write_bytes(b"junk")
        rc = self._run(
            monkeypatch, ["--stamp-meta", "--repo", str(tmp_path / "myrepo")]
        )
        assert rc == 0
        assert (idx.parent / "index.scip.meta.json").exists()

    def test_second_stamp_latest_wins(self, tmp_path, monkeypatch) -> None:
        """「重跑覆寫，冪等」docstring 宣稱的釘住（審查 F4b）。"""
        monkeypatch.setattr(scip_refs, "scip_pb2", None)
        heads = iter(["1111111111", "2222222222"])
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: next(heads))
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        argv = ["--stamp-meta", "--repo", str(tmp_path), "--index", str(idx)]
        assert self._run(monkeypatch, argv) == 0
        assert self._run(monkeypatch, argv) == 0
        meta = json.loads(
            (tmp_path / "index.scip.meta.json").read_text(encoding="utf-8")
        )
        assert meta["head"] == "2222222222"

    def test_stamp_without_repo_returns_2(self, tmp_path, monkeypatch) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        assert self._run(monkeypatch, ["--stamp-meta", "--index", str(idx)]) == 2

    def test_stamp_git_fail_returns_2(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: None)
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        rc = self._run(
            monkeypatch,
            ["--stamp-meta", "--repo", str(tmp_path), "--index", str(idx)],
        )
        assert rc == 2
        assert "[FAIL]" in capsys.readouterr().err

    def test_stamp_mutually_exclusive_with_query(self, tmp_path, monkeypatch) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        rc = self._run(
            monkeypatch,
            ["q", "--stamp-meta", "--repo", str(tmp_path), "--index", str(idx)],
        )
        assert rc == 2

    def test_stamp_mutually_exclusive_with_audit(self, tmp_path, monkeypatch) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        rc = self._run(
            monkeypatch,
            ["--stamp-meta", "--audit", "--repo", str(tmp_path), "--index", str(idx)],
        )
        assert rc == 2


class TestSourceLine:
    """⑤輸出面——[SRC] 標註；無證據不捏造（legacy 輸出不變）。"""

    def _sidecar(self, tmp_path, head: str) -> Path:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text(
            json.dumps(
                {"repo": "r", "head": head, "stamped_at": "2026-08-24T10:00:00+00:00"}
            ),
            encoding="utf-8",
        )
        return idx

    def test_sidecar_only(self, tmp_path, monkeypatch, capsys) -> None:
        idx = self._sidecar(tmp_path, "abcdef1234567890")
        got = scip_refs.source_line(idx, None)
        assert got == "[SRC] scip index @ abcdef1（2026-08-24）"
        assert capsys.readouterr().err == ""

    def test_repo_only_warns_unstamped(self, tmp_path, monkeypatch, capsys) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "1122334455")
        assert scip_refs.source_line(idx, tmp_path) == "[SRC] repo HEAD @ 1122334"
        assert "未 stamp" in capsys.readouterr().err

    def test_no_evidence_returns_none(self, tmp_path, monkeypatch, capsys) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        assert scip_refs.source_line(idx, None) is None
        assert capsys.readouterr().err == ""

    def test_head_mismatch_warns_drift(self, tmp_path, monkeypatch, capsys) -> None:
        idx = self._sidecar(tmp_path, "abcdef1234")
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "9998887777")
        line = scip_refs.source_line(idx, tmp_path)
        assert "scip index @ abcdef1" in line
        assert "repo HEAD @ 9998887" in line
        assert "已離開 index 生成點" in capsys.readouterr().err

    def test_corrupt_sidecar_falls_back_to_repo(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text("{broken", encoding="utf-8")
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "1122334455")
        assert scip_refs.source_line(idx, tmp_path) == "[SRC] repo HEAD @ 1122334"
        assert "損壞" in capsys.readouterr().err

    def test_non_dict_meta_warns_and_missing(self, tmp_path, capsys) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text("[]", encoding="utf-8")
        assert scip_refs.source_line(idx, None) is None
        assert "形狀非預期" in capsys.readouterr().err

    def test_non_str_head_treated_missing(self, tmp_path, capsys) -> None:
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text(
            json.dumps({"head": 123}), encoding="utf-8"
        )
        assert scip_refs.source_line(idx, None) is None
        assert "形狀非預期" in capsys.readouterr().err

    def test_git_head_non_repo_returns_none(self, tmp_path, capsys) -> None:
        """F6：真 argv 跑一次（非 repo 目錄）——非 None 路徑的實執行釘住。"""
        assert scip_refs._git_head(tmp_path) is None
        assert "git rev-parse 失敗" in capsys.readouterr().err

    def test_match_case_no_warn(self, tmp_path, monkeypatch, capsys) -> None:
        """（sidecar✓, repo✓）sha 一致＋repo 一致——零 WARN（審查 F4c）。"""
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text(
            json.dumps(
                {
                    "repo": str(tmp_path.resolve()),
                    "head": "abcdef1234",
                    "stamped_at": "2026-08-24T10:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "abcdef1234")
        assert scip_refs.source_line(idx, tmp_path) == (
            "[SRC] scip index @ abcdef1（2026-08-24） · repo HEAD @ abcdef1"
        )
        assert capsys.readouterr().err == ""

    def test_stale_stamp_mtime_warns(self, tmp_path, monkeypatch, capsys) -> None:
        """索引重生成後未重 stamp——sidecar mtime 較舊可機械偵測（審查 F2）。"""
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        sidecar = tmp_path / "index.scip.meta.json"
        sidecar.write_text(
            json.dumps({"repo": "r", "head": "abcdef1234"}), encoding="utf-8"
        )
        older = idx.stat().st_mtime - 100
        os.utime(sidecar, (older, older))
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: None)
        assert scip_refs.source_line(idx, None) is not None
        assert "比索引檔舊" in capsys.readouterr().err

    def test_repo_mismatch_warns(self, tmp_path, monkeypatch, capsys) -> None:
        """stamp 的 repo 與 --repo 不符（同名 basename）——sha 歸屬守衛
        （審查 F3）；sha 刻意相同以隔離 mismatch 軸（不觸漂移 WARN）。"""
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text(
            json.dumps({"repo": "/other/place", "head": "abcdef1234"}),
            encoding="utf-8",
        )
        monkeypatch.setattr(scip_refs, "_git_head", lambda repo: "abcdef1234")
        assert scip_refs.source_line(idx, tmp_path) is not None
        err = capsys.readouterr().err
        assert "與 --repo 不符" in err
        assert "已離開" not in err


class TestGitHeadBranches:
    """_git_head 失敗三分支（審查 F4a）——stamp 與 [SRC] 的 git 邊界。"""

    def test_timeout_returns_none(self, monkeypatch, capsys) -> None:
        def fake_run(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd, timeout=1)

        monkeypatch.setattr(scip_refs.subprocess, "run", fake_run)
        assert scip_refs._git_head(Path("/anywhere")) is None
        assert "逾時" in capsys.readouterr().err

    def test_git_missing_returns_none(self, monkeypatch, capsys) -> None:
        def fake_run(cmd, **kw):
            raise FileNotFoundError("git")

        monkeypatch.setattr(scip_refs.subprocess, "run", fake_run)
        assert scip_refs._git_head(Path("/anywhere")) is None
        assert "不在 PATH" in capsys.readouterr().err

    def test_nonzero_exit_returns_none(self, monkeypatch, capsys) -> None:
        proc = SimpleNamespace(returncode=128, stdout="", stderr="fatal: not a git")
        monkeypatch.setattr(scip_refs.subprocess, "run", lambda *a, **kw: proc)
        assert scip_refs._git_head(Path("/anywhere")) is None
        assert "git rev-parse 失敗" in capsys.readouterr().err


class TestReportSourceLine:
    """⑤接線——report/audit 首行 [SRC]；無證據時首行不變。"""

    def _run(self, monkeypatch, argv: list[str]) -> int:
        monkeypatch.setattr(sys, "argv", ["scip_refs", *argv])
        return main()

    def test_src_printed_first(self, capsys) -> None:
        idx = FakeIndex([FakeDoc("crates/x.rs", [FakeOcc(IMPL, 1, [1, 0, 1, 5])])])
        assert scip_refs.report(idx, "EventStoreLifecycle.open", "[SRC] x @ y") == 0
        out = capsys.readouterr().out.splitlines()
        assert out[0] == "[SRC] x @ y"
        assert out[1].startswith("[OK]")

    def test_no_src_keeps_legacy_first_line(self, capsys) -> None:
        idx = FakeIndex([FakeDoc("crates/x.rs", [FakeOcc(IMPL, 1, [1, 0, 1, 5])])])
        assert scip_refs.report(idx, "EventStoreLifecycle.open") == 0
        out = capsys.readouterr().out.splitlines()
        assert out[0].startswith("[OK]")  # legacy 位元組不變——NT 契約釘住

    def test_main_query_sidecar_emits_src_first(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        (tmp_path / "index.scip.meta.json").write_text(
            json.dumps(
                {"head": "abcdef1234567890", "stamped_at": "2026-08-24T10:00:00+00:00"}
            ),
            encoding="utf-8",
        )
        fake = FakeIndex([FakeDoc("crates/x.rs", [FakeOcc(IMPL, 1, [1, 0, 1, 5])])])
        monkeypatch.setattr(scip_refs, "load_index", lambda p: fake)
        rc = self._run(monkeypatch, ["EventStoreLifecycle.open", "--index", str(idx)])
        assert rc == 0
        out = capsys.readouterr().out.splitlines()
        assert out[0] == "[SRC] scip index @ abcdef1（2026-08-24）"

    def test_main_query_no_evidence_no_src(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.setattr(scip_refs, "scip_pb2", object())
        idx = tmp_path / "index.scip"
        idx.write_bytes(b"junk")
        fake = FakeIndex([FakeDoc("crates/x.rs", [FakeOcc(IMPL, 1, [1, 0, 1, 5])])])
        monkeypatch.setattr(scip_refs, "load_index", lambda p: fake)
        rc = self._run(monkeypatch, ["EventStoreLifecycle.open", "--index", str(idx)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "[SRC]" not in out

    def test_audit_prints_src_before_header(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        idx_file = tmp_path / "index.scip"
        idx_file.write_bytes(b"junk")
        monkeypatch.setattr(scip_refs, "load_index", lambda p: FakeIndex([]))
        proc = SimpleNamespace(returncode=0, stdout='{"missing": []}', stderr="")
        monkeypatch.setattr(scip_refs.subprocess, "run", lambda *a, **kw: proc)
        assert scip_refs.audit_mode(idx_file, tmp_path, "[SRC] audit @ z") == 0
        out = capsys.readouterr().out.splitlines()
        assert out[0] == "[SRC] audit @ z"
        assert out[1].startswith("[OK] graph_audit 缺差")
