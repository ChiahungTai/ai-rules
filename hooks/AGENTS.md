# hooks/ — 跨 harness Hook 實作腳本

> 本目錄腳本跨 Claude/ZCode 單一來源。hooks 無目錄載入點，**不能 symlink**——兩家 config 以絕對路徑引用：Claude `~/.claude/settings.json`；ZCode 3.7.7+ user-level hooks 註冊範本見 [zcode-registration.json](zcode-registration.json)（範本內容是 `~/.zcode/cli/config.json` `hooks:` 鍵下的子樹值，merge 進去而非整檔覆蓋）。`notification.sh` 不移植。

## zcode-registration.json 維護語義

- **merge 方式**：取 `events` 子樹 merge 進 config 的 `hooks:` 鍵下，`_comment` 鍵不隨行
- **SessionEnd 條目＝範本預載、現版不可 merge**：ZCode 3.7.7+ user-level hooks＝7 事件子集、**無 SessionEnd**（`ref-docs/harness/contracts.md` 定案）——待 ZCode 官方支援 SessionEnd（屆時對 zcode hooks 文檔事件表複核一次）才 merge 進 config
- **plugin 升級＝路徑維護點**：plugin cache 版號路徑漂移會使範本內 muse/codex 條目的絕對路徑過時——plugin 升級時同步更新路徑
- **grok-build 未安裝**：安裝後照 muse/codex 條目形態補第三條 SessionEnd（其 cache 的 `scripts/session-lifecycle-hook.mjs` 同款）

## 孤兒清理落差（SessionEnd hook 在 ZCode 缺席）

- 三家 external-runtime plugin 都有 SessionEnd 孤兒清理 hook（muse「reconcile stale jobs on start, cancel+kill on end」、codex `terminateProcessTree`、grok 同款）——CC 原生載入；**ZCode 無 SessionEnd 事件（contracts.md 定案）→ plugin 孤兒清理 hook 在 ZCode 缺席**
- muse 側由 bridge `reconcileStaleRunning` ledger 兜底＋post-build 開工背景寫入者盤點涵蓋
- **remediation＝ZCode app 重開（收同生命週期進程；detached 背景進程跑完自然結束、結果照落 ledger）＋`git status` 檢 working tree 半套編輯——實務成本極低（user 2026-09-05 確認），非防護缺口**
