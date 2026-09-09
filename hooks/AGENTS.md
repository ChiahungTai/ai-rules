# hooks/ — 跨 harness Hook 實作腳本

> 本目錄腳本跨 Claude/ZCode 單一來源。hooks 無目錄載入點，**不能 symlink**——兩家 config 以絕對路徑引用：Claude `~/.claude/settings.json`；ZCode 3.7.7+ user-level hooks 註冊範本見 [zcode-registration.json](zcode-registration.json)（範本內容是 `~/.zcode/cli/config.json` `hooks:` 鍵下的子樹值，merge 進去而非整檔覆蓋）。`notification.sh` 不移植。

## zcode-registration.json 維護語義

- **merge 方式**：取 `events` 子樹 merge 進 config 的 `hooks:` 鍵下，`_comment` 鍵不隨行
- **SessionEnd 條目＝範本預載、現版不可 merge**：ZCode 3.7.7+ user-level hooks＝7 事件子集、**無 SessionEnd**（`ref-docs/harness/contracts.md` 定案）——待 ZCode 官方支援 SessionEnd（屆時對 zcode hooks 文檔事件表複核一次）才 merge 進 config
- **plugin 升級＝路徑維護點**：plugin cache 版號路徑漂移會使範本內 muse/codex 條目的絕對路徑過時——plugin 升級時同步更新路徑
- **grok-build 未安裝**：安裝後照 muse/codex 條目形態補第三條 SessionEnd（其 cache 的 `scripts/session-lifecycle-hook.mjs` 同款）

## memory sensors（AIR-56，CC-only）

- `memory-write-sensor.py`（PostToolUse，matcher `Edit|Write`）：成功後才記 actor 證據→ `$MEMORY_HOOK_LOG`（預設 `~/.local/share/ai-rules/memory-hook-events.jsonl`）。池判定＝父目錄含 MEMORY.md。
- `memory-dirty-sensor.py`（FileChanged）：只記 dirty（watcher≠writer，不指派）。**接線限制（已驗證）**：FileChanged **matcher 種子**是 cwd 域字面檔名，池在 repo cwd 外→種子路徑 watch 不到；但 hooks 可經 SessionStart／CwdChanged 回傳 `watchPaths`（絕對路徑數組，CC 鏡像 hooks.md watchPaths 節）把池動態納入 watch——接線路徑存在、本弧未接。本腳本邏輯已驗、live 接線未驗證——外部寫入後備仍是 hash 腿。
- ZCode 3.7.7 事件子集**含 PostToolUse**（04 報告 §207 實測：SessionStart/UserPromptSubmit/PreToolUse/PermissionRequest/PostToolUse/PostToolUseFailure/Stop——SessionEnd 不在）→ write-sensor 的 CC-only 範圍是本弧取捨非機制限制，ZCode 側可另接（未接：本弧外決策）。
- 註冊（user 側 `~/.claude/settings.json` 的 `hooks` 鍵，merge 非覆蓋；改前 cp .bak）：PostToolUse 條目 command 指本目錄絕對路徑＋matcher `Edit|Write`；FileChanged 條目待池入 cwd 拓撲才接。collector 消費：`attribution --hook-events <log>`（merge 去重＋dirty 旗）。

## 孤兒清理落差（SessionEnd hook 在 ZCode 缺席）

- 三家 external-runtime plugin 都有 SessionEnd 孤兒清理 hook（muse「reconcile stale jobs on start, cancel+kill on end」、codex `terminateProcessTree`、grok 同款）——CC 原生載入；**ZCode 無 SessionEnd 事件（contracts.md 定案）→ plugin 孤兒清理 hook 在 ZCode 缺席**
- muse 側由 bridge `reconcileStaleRunning` ledger 兜底＋post-build 開工背景寫入者盤點涵蓋
- **remediation＝ZCode app 重開（收同生命週期進程；detached 背景進程跑完自然結束、結果照落 ledger）＋`git status` 檢 working tree 半套編輯——實務成本極低（user 2026-09-05 確認），非防護缺口**
