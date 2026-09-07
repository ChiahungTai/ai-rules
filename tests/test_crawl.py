"""crawl.py manifest 語義測試（codex 09-06 審查 I-4/I-5/S-2）。

manifest 是鏡像的 provenance ledger：抽樣不得縮小 coverage、新鮮度必須
per-source（單源刷新不得刷新他源的表面時間）、磁碟孤兒要可見。
"""

import json

from conftest import load_module

crawl = load_module("ref-docs/harness/crawl.py")


def _install_fake_source(monkeypatch, tmp_path, n_pages: int = 5):
    pages = [crawl.Page(f"https://x.test/{i}.md", f"{i}.md") for i in range(n_pages)]

    def discover():
        return pages

    def fetch(page):
        return "ok", f"# page {page.relpath}\n".encode()

    monkeypatch.setattr(crawl, "BASE_DIR", tmp_path)
    monkeypatch.setattr(crawl, "SOURCES", {"fake": ("https://x.test", discover, fetch)})
    return tmp_path / "manifest.json"


def _write_manifest(path, sources: dict) -> None:
    path.write_text(
        json.dumps({"generated_at": "2020-01-01T00:00:00+00:00", "sources": sources}),
        encoding="utf-8",
    )


def test_limit_smoke_does_not_clobber_manifest_or_disk(monkeypatch, tmp_path):
    """--limit 抽樣零寫入：manifest 與磁碟鏡像都不變（I-5＋followup B1——
    只擋 manifest 不夠：寫了磁碟留舊 hash＝integrity split）。"""
    manifest = _install_fake_source(monkeypatch, tmp_path)
    assert crawl.main(["--source", "fake"]) == 0  # 全量跑，建立 5 頁 ledger
    before_manifest = manifest.read_bytes()
    before_disk = {
        p.name: p.read_bytes() for p in sorted((tmp_path / "fake").iterdir())
    }
    assert crawl.main(["--source", "fake", "--limit", "2"]) == 0  # smoke
    assert manifest.read_bytes() == before_manifest  # manifest 零寫入
    after_disk = {p.name: p.read_bytes() for p in sorted((tmp_path / "fake").iterdir())}
    assert after_disk == before_disk  # 磁碟零寫入（integrity_split=False）


def test_limit_smoke_on_fresh_dir_writes_nothing(monkeypatch, tmp_path):
    """smoke 在全新目錄上也不落任何檔（磁碟＋manifest 皆無）。"""
    manifest = _install_fake_source(monkeypatch, tmp_path)
    assert crawl.main(["--source", "fake", "--limit", "2"]) == 0
    assert not manifest.exists()
    assert not (tmp_path / "fake").exists()


def test_full_run_records_per_source_generated_at(monkeypatch, tmp_path):
    """全量刷新在 source 條目自帶 generated_at（I-4：新鮮度 per-source）。"""
    manifest = _install_fake_source(monkeypatch, tmp_path)
    assert crawl.main(["--source", "fake"]) == 0
    entry = json.loads(manifest.read_text(encoding="utf-8"))["sources"]["fake"]
    assert entry["page_count"] == 5
    assert entry["generated_at"]


def test_single_source_refresh_preserves_other_source_timestamp(monkeypatch, tmp_path):
    """單源刷新不得刷新他源的表面新鮮度（I-4）。"""
    manifest = _install_fake_source(monkeypatch, tmp_path)
    _write_manifest(
        manifest,
        {
            "other": {
                "base": "https://other",
                "generated_at": "2020-01-01T00:00:00+00:00",
                "page_count": 1,
                "pages": [
                    {
                        "url": "u",
                        "path": "p.md",
                        "status": "ok",
                        "sha256": "",
                        "bytes": 1,
                    }
                ],
            }
        },
    )
    assert crawl.main(["--source", "fake"]) == 0
    sources = json.loads(manifest.read_text(encoding="utf-8"))["sources"]
    assert sources["other"]["generated_at"] == "2020-01-01T00:00:00+00:00"
    assert sources["fake"]["generated_at"] > "2020"  # 只有被刷新的本源更新


def test_full_run_reports_disk_orphans(monkeypatch, tmp_path, capsys):
    """磁碟上有、本次 discovery 沒有的鏡像檔要列帳（S-2——不刪，人工裁定）。"""
    _install_fake_source(monkeypatch, tmp_path)
    orphan = tmp_path / "fake" / "zz-orphan.md"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("# orphan\n", encoding="utf-8")
    assert crawl.main(["--source", "fake"]) == 0
    out = capsys.readouterr().out
    assert "[WARN]" in out and "zz-orphan.md" in out
