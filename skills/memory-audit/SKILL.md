---
name: memory-audit
description: "memory 清理/稽核/過時/記憶健康檢查（memory audit / audit MEMORY.md / auto memory）。兩級稽核：full 四層（索引機械量測→內容核實 vs repo→清理執行→EP/任務盤點）/ lite 增量核實（git log 驅動）。內容核實預設必做——索引整潔 ≠ 記憶健康。狀態戳 _audit-state.md；advisory→用戶核可→執行三分離。"
argument-hint: "full | lite | 無參數（讀狀態戳後建議）"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Edit", "Write"]
---

# /memory-audit — auto memory 兩級稽核 + 增量核實 + 專案狀態戳

> **適用載體**：Claude Code / ZCode auto memory——per-project memory 目錄（`MEMORY.md` 索引 + 各條目 .md；session 啟動只載索引前「200 行或 25KB 先到為準」，**超限的尾端條目靜默不載入**）。ZCode memory 目錄是 symlink → Claude `projects/<project>/memory`，兩端單一真相。memory 跟專案/repo 走：稽核與狀態戳 per-project，跨 worktree 同一份不重複稽核。

## 🔴 反模式警示（最前，必讀）

**索引整潔 ≠ 記憶健康。**

真實案例（2026-08-16，mosaic_alpha）：首輪稽核只做索引層量測（重複/orphan/missing/預算全綠），用戶鞭策後才補內容核實，仍抓到 **3 條 ❌（核心主張被 repo 演進推翻）+ 24 條 🟡（部分過時）**。

根因：「過時」的判準證據**只在 memory claims vs repo 現況對照**——不在索引層。

**自檢句**（advisory 報告產出前必問）：這份報告若只有索引層發現——「過時」的判準證據在哪一層？答案不在「內容 vs repo 對照」就是層次錯了，回去做層 2。內容核實是預設必做，不是升級選項。

## 兩級稽核（開場決策）

開場先讀狀態戳 `memory/_audit-state.md`（規格見下方）：

- 無戳 / `base_commit` 之後 repo 大幅演進 / 距上次 full 已久 → 建議 **full**
- 間隔短或用戶明示 → **lite**

## Full audit — 四層

### 層 1：索引機械量測

> **generator 池**（memory dir 有 `_generate_index.py`）：索引是 frontmatter 投影，重複/orphan/missing 由生成保證不存在——層 1 縮為 `python3 memory/_generate_index.py --check`（gate 17,000 字元/24,000 bytes/190 行 fail-loud——雙單位防 harness chars/bytes 兩種上限讀法）＋確認 MEMORY.md 非手寫。資產源：ai-rules repo `skills/memory-audit/scripts/generate_index.py`（部署 = 複製進各專案 memory dir；Stop hook 自動重生成、PreToolUse hook 擋手寫）；副本新鮮度＝層 1 先 `cmp` 部署副本與資產源（stale 先 cp＋mv 原子刷新再 `--check`——Stop hook 對不符副本跳過執行）；`memory/_regen-failed` 標記存在＝regen 失敗待修（Stop stdout 不進模型 context 的可見錨點）。下表全量手檢僅適用未裝 generator 的池。數值調和：下表「<25,000 bytes」＝未裝池軟目標；24,000 bytes＝generator 池硬 gate——單一硬數值源在 generator 註解。

| 檢查 | 命令 | 判準 |
|------|------|------|
| 索引預算 | `wc -l MEMORY.md` / `wc -c MEMORY.md` | 載入上限「前 200 行或 25KB 先到為準」；超限=尾端條目靜默不載。**目標 <25,000 bytes**（兩種 KB 解讀都安全）＋ **行數軟上限 150**（逼近=合併建議觸發；預設值可在 `_audit-state.md` per-project 覆寫） |
| 索引重複 | `rg -o '\]\(([^)]+)\)' -r '$1' MEMORY.md \| sort \| uniq -d` | 0 輸出 |
| orphan（有檔無索引行） | `comm -23 <(ls *.md \| grep -v -e MEMORY.md -e '^_' \| sort) <(rg -o '\]\(([^)]+)\)' -r '$1' MEMORY.md \| sort)` | 0 輸出（`_` 前綴檔不進索引，排除） |
| missing（索引行無檔） | 同上，`comm -13` 反向 | 0 輸出 |
| 非 one-line-per-entry | `rg -v '^(#\| ?- \[\|$)' MEMORY.md` | 0 hits（索引只允許標題與一行條目；` ?` 容許頂格或縮排條目） |

### 層 2：內容核實 vs repo（預設必做）

條目多時 spawn agents 按段平行（每 agent 一段條目清單），少則主 session 直接做；**spawn 失敗（usage limit / 429）→ 降級主 session 分批直接核實，勿中止 audit**：

1. 每檔抽 **3-6 個 load-bearing claims**（路徑、符號、狀態宣稱）
2. 逐項對 repo 驗證：
   - 狀態宣稱（「已修」「已遷移」「已完成」）→ `git log --grep=<關鍵詞>` 找對應 commit
   - 符號/路徑 → rg + fd；**0 hits 先換 2-3 種 pattern 再判不存在**（單一 pattern 會 false negative）
3. verdict：✅ 準確 / 🟡 部分過時 / ❌ 核心被推翻 / ➖ 非程式碼可驗證（用戶偏好、決策脈絡——不標過時）
4. 聚合型條目（一條摘要多檔/多主題）每段抽驗
5. **self-report discount**：memory 記錄的 bug 要**實跑 repro**，不信自述

> 真實案例（self-report discount，mosaic_alpha）：memory 記「sync-stubs loop 有 bug」，實跑無法重現——歷史 commit 已修、memory 沒跟上；實跑反而挖出 memory 沒記的兩個真陷阱（NT source stub 舊於 venv、`set -e` 下 `diff | head` 截斷）。雙向教訓：memory 記的 bug 可能已修（過時），沒記的陷阱仍在（欠收）——兩者都只有實跑能揭露。

### 層 3：清理執行（用戶核可後）

- 刪檔前 `rg "\[\[<name>\]\]"` 查反向引用——不留新 dangling（引用者同步改）
- **多池殘留掃描**：雙 harness 共用腳本跨多池部署後，清理/驗證掃描以「檔名 × 池」為維度——每個 pool 都要 rg（2026-08-30 實例：清理清單漏了 mosaic 池的同名測試條目）
- 合併檔帶 `merged_from` 標記（保留追溯）
- **cluster merge 機械觸發**：同主題散檔 ≥3（rg 主題詞/同前綴判定）→ merge candidate；併入目標優先既有最大 cluster（閾值可在 `_audit-state.md` per-project 覆寫）
- 索引精簡：generator 池＝修條目檔 description（索引行是投影、禁手寫）；未裝池＝一行 = 主題 + 一個鉤子，細節留在條目檔內
- 每輪結束**重跑層 1**——驗證清理本身沒引入新問題

### 層 4：EP/任務狀態盤點

- 完成態信號：EP 已歸檔 `_done/`、工具被取代、等待條件已解除 → 清理候選
- **project-\* 計畫完結收斂**：計畫完成（commit 落地）後，對應 `project-*` 條目收斂——刪現況細節（未 commit 狀態、session 進度），留決策與教訓；主題重疊時併入相關 cluster
- 未完成 → **列表交用戶逐項判斷**；禁自行判斷「應該做完了」——宣稱完成 ≠ 實作落地，查實際檔案與 git 狀態

### 結束：寫狀態戳（見下方規格）

## Lite audit — 增量核實

層 1 機械量測 + 層 2' 增量核實：

```
git log --oneline <base_commit>..HEAD → 抽主題詞（模組名/命令名/遷移動詞）
→ rg <主題詞> memory/ 找命中條目
→ 只核實命中條目
```

drift 原因絕大多數是 repo 演進——git log 就是 drift 索引，沒碰過的主題不過時。

## 狀態戳：`memory/_audit-state.md`

獨立檔（底線前綴**不進索引**；**不放 MEMORY.md frontmatter**——harness 管理索引檔有重寫風險）。欄位：

```
last_full_audit: <date>
last_lite_audit: <date>
base_commit: <sha>    # 用 sha 不用時間——精確對齊 git log 增量範圍
coverage: <n>         # 上次核實覆蓋條目數
```

## 治理三分離

**advisory 報告 → 用戶核可 → 執行**。稽核不得自行刪改用戶想留的條目；報告每項附機械證據（file:line / 命令輸出）。驗證紀律（Claim→Evidence、self-report discount 理論基礎）見 [acceptance-evidence](../../rules/acceptance-evidence.md)，不重抄。
