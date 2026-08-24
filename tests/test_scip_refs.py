"""scip_refs 單元測試——duck-typed fake index（不依賴 protobuf/scip_pb2）。

釘住查詢匹配邏輯（impl 變體＋trait 宣告位址兩符號形態＋``(?<!\\w)``
邊界）、DEF/refs 收集、audit **雙鍵歸屬**（(定義檔, 方法名)——只按檔
會把同檔鄰居 refs 聯集，原型審查 216→138 實證）、main() 退出碼契約
（0/1/2）與 load_index 截斷 sanity。真索引 L4 基準：NT 實測 --audit
138/861（.agent-tmp/research/scip/ 原型輪）。
"""

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
