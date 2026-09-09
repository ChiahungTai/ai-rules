"""Tests for hooks/muse_memory_inbox.sh (AIR-54 S3).

PreToolUse gate diverts muse add_memory/edit_memory into
.agents/memory-inbox/ and denies. Never touch the live repo: fixtures
copy the script into a tmp repo skeleton (tmp/hooks/ + tmp/.agents/memory/).
"""

import hashlib
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks"
INBOX_HOOK = HOOKS / "muse_memory_inbox.sh"


def make_repo(tmp_path, with_entry=True):
    repo = tmp_path / "repo"
    (repo / "hooks").mkdir(parents=True)
    shutil.copy(INBOX_HOOK, repo / "hooks" / "muse_memory_inbox.sh")
    pool = repo / ".agents" / "memory"
    pool.mkdir(parents=True)
    if with_entry:
        (pool / "note.md").write_text("---\nname: note\n---\n\nbody\n")
    return repo


def run_hook(repo, payload):
    r = subprocess.run(
        ["bash", str(repo / "hooks" / "muse_memory_inbox.sh")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    return r


def inbox_files(repo):
    inbox = repo / ".agents" / "memory-inbox"
    if not inbox.is_dir():
        return []
    return sorted(p for p in inbox.iterdir() if p.suffix == ".json")


def test_add_diverted_to_inbox_and_denied(tmp_path):
    """AIR-54 S3: add_memory -> deny + inbox payload preserves content."""
    repo = make_repo(tmp_path)
    payload = {
        "tool_name": "add_memory",
        "tool_input": {
            "scope": "project",
            "path": "new-note.md",
            "content": "hello inbox",
        },
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    spec = out["hookSpecificOutput"]
    assert spec["permissionDecision"] == "deny"
    assert spec["permissionDecisionReason"].strip() != ""
    files = inbox_files(repo)
    assert len(files) == 1
    saved = json.loads(files[0].read_text())
    assert saved["tool_input"]["content"] == "hello inbox"
    assert "_inbox_meta" not in saved  # add class: no CAS base
    assert spec["permissionDecisionReason"].find(files[0].name) != -1
    mode = stat.S_IMODE(files[0].stat().st_mode)
    assert mode == 0o600


def test_edit_existing_attaches_cas_base(tmp_path):
    """AIR-54 S3/G2-3: edit_memory on existing entry carries base_sha256."""
    repo = make_repo(tmp_path)
    raw = (repo / ".agents" / "memory" / "note.md").read_bytes()
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {"scope": "project", "path": "note.md", "content": "new body"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    files = inbox_files(repo)
    assert len(files) == 1
    saved = json.loads(files[0].read_text())
    meta = saved["_inbox_meta"]
    assert meta["base_path"] == "note.md"
    assert meta["base_sha256"] == hashlib.sha256(raw).hexdigest()


def test_setup_script_generates_portable_hooks_json(tmp_path):
    """Portability: hooks.json is machine-local; the setup script derives
    the absolute hook path from its own location (clone/move safe)."""
    repo = tmp_path / "repo"
    (repo / "hooks").mkdir(parents=True)
    shutil.copy(HOOKS / "setup-muse-hooks.sh", repo / "hooks" / "setup-muse-hooks.sh")
    r = subprocess.run(
        ["bash", str(repo / "hooks" / "setup-muse-hooks.sh")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    cfg = json.loads((repo / ".muse" / "hooks.json").read_text())
    entry = cfg["hooks"]["PreToolUse"][0]
    assert entry["matcher"] == "add_memory|edit_memory"
    assert entry["hooks"][0]["command"] == str(repo / "hooks" / "muse_memory_inbox.sh")


def test_traversal_path_skips_enrichment_still_denied(tmp_path):
    """T3-1: unverified P is never dereferenced (no read/hash outside pool).

    `../memory-inbox/x.md` is also the sibling-prefix collision case (T3-3):
    it must not gain _inbox_meta, while deny+land still happens (the lexical
    gate itself stays fail-open for the diversion function).
    """
    repo = make_repo(tmp_path)
    (repo / ".agents" / "memory-inbox").mkdir(parents=True)
    sentinel = repo / ".agents" / "memory-inbox" / "x.md"
    sentinel.write_text("inbox content")
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {
            "scope": "project",
            "path": "../memory-inbox/x.md",
            "content": "x",
        },
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    files = inbox_files(repo)
    assert len(files) == 1
    assert "_inbox_meta" not in json.loads(files[0].read_text())


def test_absolute_path_skips_enrichment(tmp_path):
    """T3-1: absolute P never dereferenced."""
    repo = make_repo(tmp_path)
    target = repo / ".agents" / "memory" / "note.md"
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {"scope": "project", "path": str(target), "content": "x"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    files = inbox_files(repo)
    assert len(files) == 1
    assert "_inbox_meta" not in json.loads(files[0].read_text())


def test_symlink_entry_skips_enrichment(tmp_path):
    """T3-1: pool-internal symlink targets are not hashed."""
    repo = make_repo(tmp_path, with_entry=False)
    pool = repo / ".agents" / "memory"
    real = pool / "real.md"
    real.write_text("body\n")
    (pool / "alias.md").symlink_to("real.md")
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {"scope": "project", "path": "alias.md", "content": "x"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    files = inbox_files(repo)
    assert len(files) == 1
    assert "_inbox_meta" not in json.loads(files[0].read_text())


def test_intermediate_dir_symlink_skips_enrichment(tmp_path):
    """T3-1b counterexample (now fenced by the T4-2 subdir rule): alias
    -> outside dir, P=alias/secret.md. Enrichment must be skipped
    (no read/hash outside the pool); deny+land still happens.
    """
    repo = make_repo(tmp_path, with_entry=False)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("outside secret\n")
    os.symlink(outside, repo / ".agents" / "memory" / "alias")
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {"scope": "project", "path": "alias/secret.md", "content": "x"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    files = inbox_files(repo)
    assert len(files) == 1
    assert "_inbox_meta" not in json.loads(files[0].read_text())


def test_nested_path_skips_enrichment_contract_rejects(tmp_path):
    """T4-2: consolidation only takes pool-root basenames (generator and
    watch-seed are top-level only), so the hook skips enrichment for any
    P containing `/`. Deny+land still happens; the contract rejects."""
    repo = make_repo(tmp_path, with_entry=False)
    sub = repo / ".agents" / "memory" / "sub"
    sub.mkdir()
    (sub / "note.md").write_bytes(b"---\nname: n\n---\n\nb\n")
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {"scope": "project", "path": "sub/note.md", "content": "x"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    files = inbox_files(repo)
    assert len(files) == 1
    assert "_inbox_meta" not in json.loads(files[0].read_text())


def test_add_to_existing_path_carries_meta_but_tool_name_rules(tmp_path):
    """T3-6: meta condition is path-exists, not tool==edit.

    An add_memory pointing at an existing path also gains _inbox_meta;
    the consumer must discriminate add/edit by immutable tool_name, never
    by meta presence. This test pins that behavior.
    """
    repo = make_repo(tmp_path)
    payload = {
        "tool_name": "add_memory",
        "tool_input": {"scope": "project", "path": "note.md", "content": "clash"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    files = inbox_files(repo)
    assert len(files) == 1
    saved = json.loads(files[0].read_text())
    assert saved["tool_name"] == "add_memory"
    assert saved["_inbox_meta"]["base_path"] == "note.md"


def test_edit_missing_target_no_cas_still_denied(tmp_path):
    """AIR-54 S3: edit_memory on absent path -> no meta, still deny+land."""
    repo = make_repo(tmp_path)
    payload = {
        "tool_name": "edit_memory",
        "tool_input": {"scope": "project", "path": "ghost.md", "content": "x"},
    }
    r = run_hook(repo, payload)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    files = inbox_files(repo)
    assert len(files) == 1
    assert "_inbox_meta" not in json.loads(files[0].read_text())
