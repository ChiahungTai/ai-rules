---
description: "每日自動化 CLAUDE.md 維護 — compare-first：先比對再決定是否重建"
when_to_use: "Automated daily CLAUDE.md maintenance: compare source-docs against .py first, only rebuild when precision drops. Runs autonomously."
usage: "/claude:daily-maintain [--full] [--max-agents N] [--dry-run] [--modules a,b,c]"
argument-hint: "/claude:daily-maintain — compare-first 自動維護，--full 全模組審計（含 Layer D 基礎設施覆蓋）"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
---

# /claude:daily-maintain — 每日自動化 CLAUDE.md 維護（Compare-First）

CLAUDE.md 知識管理自動化引擎。**讓 CLAUDE.md 保持準確且完整。**

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)
遞迴發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)
遞迴處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)
Autonomous execution: [autonomous-execution SKILL.md](../../skills/autonomous-execution/SKILL.md)

---

## 核心架構 — Compare-First

**為什麼 Compare-First**：decode-compare（便宜，幾分鐘）先跑，只有精度不足時才觸發 doc-decode（昂貴，十幾分鐘）。避免對新鮮的 source-docs 做無意義的重建。

**三層資料流**：

```
CLAUDE.md（理解框架）+ .py（程式碼真相）
  ↓ doc-decode（雙輸入）
source-docs/（驗證中間層，非消費層）
  ↓ decode-compare 找缺口
CLAUDE.md（壓縮知識 — 最終目標）
```

**關鍵認知**：LLM 不會直接讀 source-docs。source-docs 是驗證中間層，CLAUDE.md Gap Report 才是目標。doc-decode 必須從 CLAUDE.md 出發（定優先級），再用 .py 驗證（確認準確）。

---

## 操作模式

| 模式 | Scope | Depth | 說明 |
|------|-------|-------|------|
| **Default** | 自上次執行後有變更的模組 | A/B/C | 快速日常維護 |
| **--full** | 全部模組 | A/B/C/D（含基礎設施覆蓋） | CLAUDE.md 完整性審計 |

**Use Case 對照表**：

| # | 場景 | 判斷方式 | 該做什麼 |
|---|------|---------|---------|
| UC1 | 全新專案，無 source-docs | source-docs/ 不存在 | doc-decode → compare → CLAUDE.md |
| UC2 | 每日跑，有 .py 變更 | git log 偵測 | compare → 精度不足才 decode |
| UC3 | source-docs 剛建好 | compare 全部 ✅ | 跳過 decode，只更新 .last-run |
| UC4 | 沒有任何變更 | git log 無新 commit | 全部跳過，只更新 .last-run |
| UC5 | 大重構後 / 需審計 | `--full` | 全模組 compare（含 Layer D）→ 條件 decode |
| UC6 | .py 被刪除 | git diff 偵測 | 清理 source-docs 引用 → compare |
| UC7 | 手動改了 CLAUDE.md | git log 偵測 | compare → 決定是否需要 decode |

---

## 執行流程

```
Phase 0: SCAN — 範圍偵測（哪些模組需要處理）
Phase 1: COMPARE — decode-compare（便宜，永遠先跑）
Phase 2: DECODE — doc-decode（昂貴，精度不足時才觸發）
Phase 3: UPDATE — CLAUDE.md 更新 + Morning Report
```

### Phase 0: SCAN — 範圍偵測

1. **模組發現**：`fd -e py .` 識別含 CLAUDE.md 或 .py 的模組目錄
2. **讀取 .last-run**：從 source-docs/.last-run 讀取上次 HEAD commit hash（不是 wall clock timestamp。**為什麼用 commit hash**：wall clock 會偵測到自己的文檔 commit；commit hash 精確標記「處理到哪裡」）
3. **變更偵測**：`git log {last_hash}..HEAD --name-only` 過濾 .py 和 CLAUDE.md，映射到模組
4. **.py 刪除處理**：`rg "source:.*{deleted_file}" source-docs/` 移除殘留引用
5. **CLAUDE.md 變更語義映射**：`git diff` 識別語義類別 → 映射到 source-docs 子系統
6. **source-docs dirty 偵測**：有 uncommitted changes → 跳過處理
7. **範圍判定**：Default = 變更模組；--full = 全部模組；無變更 → 跳到 Phase 3 minimal report
8. **Agent 分配**：in-scope 模組平分給 --max-agents 個 agent

### Phase 1: COMPARE — decode-compare（永遠先跑）

1. **Quick Scan**（秒級）：rg/fd 驗證引用完整性 + CLAUDE.md 語義驗證
2. **Full Compare**（分鐘級）：A/B/C 三層比對 source-docs vs .py
   - A 架構：模組結構、職責劃分、依賴關係
   - B 演算法：核心邏輯、計算流程、邊界處理
   - C 資料結構：型別定義、資料模型
   - D 基礎設施（--full 專用）：跨模組 import 分析
3. **計算精度**：`(✅ + ⚠️×0.5) / (✅ + ⚠️ + ❌ + 🔍) × 100%`
4. **精度門檻**：≥ 90% ✅ 優良 | 70-89% 🟡 可接受 | < 70% 🔴 觸發 Phase 2
5. **產出 ACTION items**（Signal/Noise 過濾）：High Signal 自動套用，Medium 標記建議，Low Noise 跳過

### Phase 2: DECODE — doc-decode（條件觸發）

**只有精度 < 70% 或無 source-docs 時才執行。**

Agent 啟動時強制依序：
1. **S1: READ CLAUDE.md** — 提取理解框架（模組定位、設計決策、約束、導航目標、可複用基礎設施清單）
2. **S2: SCAN .py** — 讀取全部 .py（--full 含跨模組 import 分析）
3. **S3: RECONSTRUCT source-docs** — 以 CLAUDE.md 為優先級指引更新
4. **decode 後驗證**：compare 確認重建品質，仍 < 70% → 標記 ⚠️

### Phase 3: UPDATE + REPORT

1. **CLAUDE.md 更新**：逐項 Edit（不是整檔重寫），git diff 精確到行
   - ✅ 可自動修改：修正過時描述、補充型別關係、更新導航、移除可推導內容
   - ⚠️ 只建議不修改：新增設計理由、新增失敗教訓、刪除原則段落、修改架構約束
2. **一致性檢查**：格式問題直接修正，邏輯問題標記 ⚠️
3. **Morning Report**：寫入 ai-analysis/daily-report/{YYYY-MM-DD}.md
4. **寫入 .last-run**：`git rev-parse HEAD > source-docs/.last-run`（在所有處理完成後寫入）

Morning report 格式：[morning-report-template.md](./_common/morning-report-template.md)

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | Compare-first：掃描變更模組 → compare → 條件 decode → morning report |
| **--full** | 全模組 compare（A/B/C/D）→ 條件 decode → Gap Report → morning report |
| **--max-agents N** | 平行 agent 上限（預設 4） |
| **--dry-run** | 只產出 Phase 0 計劃，不實際執行 |
| **--modules a,b,c** | 只處理指定模組（除錯用） |

---

## 執行約束

### autonomous-execution 模式

本命令預設夜間排程執行：
- **不問問題**：所有決策記錄在 morning report
- **Don't-Self-Decide Boundaries**：不刪除原則/約束段落、不新增設計理由段落、不修改架構約束描述
- **Error Self-Healing**：compare < 50% 重試一次；decode 後仍 < 70% 標記 ⚠️；連續 3 次失敗跳過

### 比例化深度標準

```
最低行數 = max(200, 核心演算法函數數量 × 30 + 子系統數量 × 50)
最低程式碼段落 = max(6, round(核心演算法函數數量 × 0.8))
```

未達標 → 回到 Phase 2 補讀，禁止以「已足夠」為由跳過。

### 強制子系統拆分

觸發條件：模組 .py > 8。按 import 叢集分組（不是按檔案數均分）。

---

## 與其他 Command 的關係

| Command | 角色 |
|---------|------|
| `/claude:decode-compare` | Phase 1：compare source-docs vs .py（便宜，永遠先跑） |
| `/claude:doc-decode` | Phase 2：重建 source-docs（昂貴，精度不足時才觸發） |
| `/claude:clean` | **不屬於 daily workflow** — 特殊處理工具 |
| `/claude:distill` | **不屬於 daily workflow** — 特殊處理工具 |

---

## 使用範例

```bash
/claude:daily-maintain                     # 每日 compare-first
/claude:daily-maintain --full              # 全模組審計
/claude:daily-maintain --full --modules rule_forge  # 只審計特定模組
/claude:daily-maintain --dry-run           # 只看計劃不執行
```

---

> **維護哲學**: Compare-First。先跑便宜的 decode-compare 確認現狀，只有精度不足才觸發昂貴的 doc-decode 重建。`.last-run` 記錄 commit hash 不是 wall clock，精確標記處理進度。
