# muse-memory-governance

user-scope muse plugin：把 muse 的 `add_memory` / `edit_memory` 寫入導流到 repo 內
`.agents/memory-inbox/`（atomic 代存＋deny），由 consolidation 站（memory-audit skill
「Inbox 消費」節）統一入池。機制出處 AIR-54（per-repo `.muse/hooks.json` 閘），
AIR-79 升級為 user-scope plugin——裝一次，所有帶 marker 的 repo 生效。

## Gate 語義（marker 三態）

per-repo marker 檔＝`.agents/memory-governance.json`：

| marker 狀態 | 行為 |
|---|---|
| absent | 不攔（native write，零攔截零落地） |
| `{"protocol": 1}`（integer 1，唯一合法值） | 導流 inbox＋deny |
| 其餘一切（parse 失敗／缺欄／`0`／`-1`／`"1"`／`null`／`true`／`false`／`>1`） | deny＋報錯，**不落地** |

- governed repo 內閘的任何內部故障（jq 故障、寫入失敗）→ deny（fail-closed）。
- jq 缺失且偵測到 memory tool 特徵 → 保守 deny，reason 帶修復指引。
- inbox 路徑任一已存在段是 symlink → deny 不落地（containment 防護）；尚未存在的段由閘自建。
- 非 memory 工具一律 self-filter 早退（plugin hooks 無 matcher，腳本自濾 `tool_name`）。
- legacy 共存：repo 的 `.muse/hooks.json` 若有「可工作的 legacy owner」（PreToolUse
  entry matcher 涵蓋兩工具、command 存在可執行、realpath 非本腳本），plugin 讓位 no-op；
  malformed / stale / partial matcher 不讓位。repo 本地 launcher（`hooks/muse_memory_inbox.sh`）
  以 registered origin 呼叫，無條件導流——遷移窗行為與改造前 legacy 閘一致。

## Install（user-scope）

```
muse plugins install <path-to>/muse-plugins/memory-governance --scope user
muse plugins approve
muse plugins list
```

- `approve` 是 per-capability 動作；install 後 `trust:"user-local"` **不等於** approved，
  未 approve 的 capability 不會 fire（muse 對 hook 缺席 fail-open——activation 層缺口
  由 consolidation 異常篩＋daily-maintain 直寫偵測把守）。
- manifest 為 nested `.muse-plugin/plugin.json`（exactly-one，雙 manifest 會被拒）。

## Per-repo opt-in marker

```
mkdir -p .agents
printf '{"protocol": 1}\n' > .agents/memory-governance.json
```

marker 進版控（repo 治理宣告）。worktree 只見所屬 branch checkout 的 marker——未 commit
marker 的 worktree 視為 ungoverned。

## 固定安裝點維護（共享 artifact 形態）

repo 本地 launcher 的核心解析序：

1. `MUSE_MEMORY_GOVERNANCE_HOME`（預設 `~/.local/share/muse-memory-governance`）下
   `current` symlink → `hooks/muse_memory_governance.sh`
2. repo 本地副本 `<repo>/muse-plugins/memory-governance/hooks/muse_memory_governance.sh`
3. 雙失敗 → launcher 自行 static deny（fail-closed，不留裸 exec 失敗）

換版＝新版目錄寫入後原子換指（tmp symlink + rename，避免換指瞬間斷鏈）：

```
ln -s <new-version-dir> ~/.local/share/muse-memory-governance/current.tmp
mv -f ~/.local/share/muse-memory-governance/current.tmp \
      ~/.local/share/muse-memory-governance/current
```

## Health check

- `muse plugins list`：plugin 在冊且 capability 已 approve。
- marker：`.agents/memory-governance.json` 存在且 `protocol` 為 integer 1。
- 固定安裝點（若使用）：`current` symlink 可解析且目標 `hooks/muse_memory_governance.sh` 可執行。
- 行為 smoke：governed repo 呼叫 `add_memory` 應得 deny＋inbox receipt 檔；
  ungoverned repo 應零攔截；marker 改壞後同呼叫應 deny 且無新檔。

## Uninstall

```
muse plugins remove muse-memory-governance
```

per-repo marker 移除即回到全 native；固定安裝點不再使用時整目錄移除。
