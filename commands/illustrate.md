---
description: "圖解技術概念、架構設計或流程 + 結構 viewport（city map/call stack/drill，三時點 pre-EP/post-EP/post-build）。可指定 @目錄或 @檔案讓 AI 先讀再圖解，支援 console（即時）和 md（寫檔）兩種輸出模式。"
when_to_use: "Illustrate technical concepts, architecture, or processes. Also structure viewport (city map, call stack, reuse candidates, drill) at pre-EP / post-EP / post-build. Supports console (ASCII) and md (Mermaid) output. Use with @dir or @file for code-based explanations."
usage: "/illustrate [console|md] <主題|@目錄|@檔案1 @檔案2 ...>"
---

# /illustrate — 智能圖解系統

## 輸出模式

| 模式 | 圖表 | 風格 | 適用 |
|------|------|------|------|
| **Console**（預設） | ASCII | 精簡（3-5 章，每章 3-5 點） | 即時討論、快速查詢 |
| **MD** | Mermaid（`skill: "mermaid"`） | 詳盡（多級標題、完整展開） | 深度分析、知識沉澱 |

**執行鐵律**：Console 禁止 Mermaid 語法。MD 禁止 ASCII 圖表。違反 = 指令執行失敗。

## 核心能力

- **單一主題圖解**：概念解析 + 視覺化圖表
- **批次檔案分析**：`@dir` 自動分析目錄結構，檔案 ≥ 5 時自動 Agent 並行
- **深度分析**：根據內容類型套用對應框架（論文/文章/程式碼/EP）。詳見 [illustrate-deep-analysis.md](./claude/_common/illustrate-deep-analysis.md)
- **結構 viewport**（人類 viewport，B 軸）：渲染整體結構心智模型讓人判讀 —— **city map**（模組 + 依賴方向 + dep weight lean/heavy，調用 [architecture-viewport](../skills/architecture-viewport/SKILL.md) skill 取資料）、**call stack**（重要節點呼叫鏈）、**重用枚舉**（Pattern Radar 嫌疑標記）。能力來源 skill，本命令負責**渲染給人判讀**（不產機器 finding，那是 `/code-review` axis 3）。詳見 [illustrate-structure-viewport.md](./claude/_common/illustrate-structure-viewport.md)

## 現有程式碼優先原則

> **核心原則**：不管哪種情境，先讀現有程式碼再解釋。不理解現有架構，就無法判斷變更的品質。

| 情境 | 現有程式碼的角色 | 關注點 |
|------|----------------|--------|
| EP 審查（`@ep-*.md`） | **Ground Truth** — EP 假設對不對？ | 依賴錨點、API 簽名、行號、架構假設逐一比對 |
| 變更審查（無參數） | **Baseline** — 改動融入得好不好？ | 語義 diff、架構一致性、下游缺口 |
| 一般圖解 | **Context** — 現有結構是什麼？ | 先理解再解釋 |

## 無參數行為

未提供任何參數時，自動圖解**當前 repo 尚未 commit 的變更**：

1. **讀受影響檔案的現有程式碼**（建立 baseline）— 理解架構、風格、慣例
2. 執行 `git diff` + `git diff --cached` 取得變更
3. **無 uncommitted 變更時**，自動 fallback 到 `git diff HEAD~1`（上一個 commit）
4. 以 Console 模式圖解：
   - **語義 diff**：不只看行數，看能力/行為的變更
   - **交疊偵測**：同一檔案被多個改動觸及的風險
   - **缺口偵測**：下游消費者、索引、文件是否同步更新

此行為等同於 `/illustrate @git-diff`，但不需要使用者記憶語法。

## 使用方式

```bash
/illustrate                                    # 無參數 → 圖解未 commit 變更
/illustrate 微服務架構                         # Console 模式
/illustrate md Kubernetes 叢集管理              # MD 模式 → ai-analysis/reports/
/illustrate @src/components/                   # 目錄分析
/illustrate md @src/ @tests/ --output "分析.md" # 自定義輸出
```

更多範例：[illustrate-examples.md](./claude/_common/illustrate-examples.md)

---

## MD 檔案自動儲存

- **預設位置**：`ai-analysis/reports/`
- **自定義**：`--output <路徑>`
- **檔名規則**：單檔案 → `{name}-檔案分析.md`；目錄 → `{dir}-架構分析.md`；主題 → `{topic}-圖解說明.md`
- **備份**：目標檔案存在時加時間戳

---

## 智能並行處理

檔案 ≥ 5 時，Agent tool 並行處理（model 依 [model-routing](../rules/model-routing.md)：session 降一級）：按關聯性分組 → 每組 spawn Agent → 整合結果。

平行處理架構：[illustrate-parallel-architecture.md](./claude/_common/illustrate-parallel-architecture.md)

---

## pre-EP checkpoint（彈性、軟 gate）

> **核心理念**：illustrate 是討論到一定程度時的**結構催化劑**，不是固定流程節點。結構確認前移到寫 EP **之前** —— Clean Architecture 核心順序「先定 use case + 邊界，再寫細節」。

**非線性流程**（非剛性 spec→illustrate→ep）：

```
對話討論新功能 →〔提醒〕/illustrate 結構化提案 → 人判讀（撐得起嗎、在重造嗎）→ 直接 EP 或先 spec
```

- **EP 必備、spec 可選**：EP 是實作起點（必備）；spec 只在需求不明時前置（可選）
- **軟 gate（不硬擋）**：pre-EP 是**標註 + 提醒**，不強制擋流程。前移價值靠提醒（「結構還沒確認，建議先 illustrate」）而非硬性 gate —— 避免流程摩擦，保留前移價值
- **視角來源**：調用 [architecture-thinking](../skills/architecture-thinking/SKILL.md)（分層/bounded context/use case 視角）+ [architecture-viewport](../skills/architecture-viewport/SKILL.md)（結構資料）

**結構 viewport 三時點**（同一載體，三觸發點）：pre-EP（本段，軟 gate）/ post-EP（EP 審查模式渲染提案結構撐得起嗎，見決策流程）/ post-build（懷疑結構漂移或重造既有時，重畫 city map 比對）。

---

## 決策流程

```
用戶輸入 → 有參數?
  否 → Console 模式：讀現有程式碼 → 語義 diff + 缺口偵測
  是 → 結構 viewport 觸發（架構 / 模組邊界 / pre-EP 提醒 / 顯式結構請求）?
    是 → 結構 viewport 模式：調用 architecture-viewport skill → city map/call stack/重用 → 人判讀（詳 illustrate-structure-viewport.md）
    否 → 輸入含 EP 檔案（ep-*.md 或 @execution-plans/）?
      是 → EP 審查模式：讀現有程式碼 → 假設驗證矩陣（詳 illustrate-deep-analysis.md）
      否 → 指定 md?
        是 → MD 模式（Mermaid）→ 檔案數 ≥ 5? → 並行處理
        否 → Console 模式（ASCII）→ 檔案數 ≥ 5? → 並行處理
```

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [architecture-viewport](../skills/architecture-viewport/SKILL.md) — 結構 viewport 能力來源（city map 資料/dep weight/Pattern Radar/LSP 查證；本命令渲染給人判讀）

---

## Supporting Files

| 檔案 | 何時讀取 |
|------|---------|
| [illustrate-parallel-architecture.md](./claude/_common/illustrate-parallel-architecture.md) | 檔案 ≥ 5 需並行處理時 |
| [illustrate-deep-analysis.md](./claude/_common/illustrate-deep-analysis.md) | 分析特定類型內容時（含 EP 審查框架） |
| [illustrate-examples.md](./claude/_common/illustrate-examples.md) | 需理解各模式實際輸出時 |
| [illustrate-structure-viewport.md](./claude/_common/illustrate-structure-viewport.md) | 結構 viewport / drill / pre-EP checkpoint 時 |
