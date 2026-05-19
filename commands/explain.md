---
description: "解釋技術概念、架構設計或流程。可指定 @目錄或 @檔案讓 AI 先讀再解釋，支援 console（即時）和 md（寫檔）兩種輸出模式。"
when_to_use: "Explain technical concepts, architecture, or processes. Supports console (ASCII) and md (Mermaid) output. Use with @dir or @file for code-based explanations."
usage: "/explain [console|md] <主題|@目錄|@檔案1 @檔案2 ...>"
---

# /explain — 智能解釋系統

## 輸出模式

| 模式 | 圖表 | 風格 | 適用 |
|------|------|------|------|
| **Console**（預設） | ASCII | 精簡（3-5 章，每章 3-5 點） | 即時討論、快速查詢 |
| **MD** | Mermaid（`skill: "mermaid"`） | 詳盡（多級標題、完整展開） | 深度分析、知識沉澱 |

**執行鐵律**：Console 禁止 Mermaid 語法。MD 禁止 ASCII 圖表。違反 = 指令執行失敗。

## 核心能力

- **單一主題解釋**：概念解析 + 視覺化圖表
- **批次檔案分析**：`@dir` 自動分析目錄結構，檔案 ≥ 5 時自動 Agent 並行
- **深度分析**：根據內容類型套用對應框架（論文/文章/程式碼）。詳見 [explain-deep-analysis.md](./claude/_common/explain-deep-analysis.md)

## 使用方式

```bash
/explain 微服務架構                         # Console 模式
/explain md Kubernetes 叢集管理              # MD 模式 → ai-analysis/reports/
/explain @src/components/                   # 目錄分析
/explain md @src/ @tests/ --output "分析.md" # 自定義輸出
```

更多範例：[explain-examples.md](./claude/_common/explain-examples.md)

---

## MD 檔案自動儲存

- **預設位置**：`ai-analysis/reports/`
- **自定義**：`--output <路徑>`
- **檔名規則**：單檔案 → `{name}-檔案分析.md`；目錄 → `{dir}-架構分析.md`；主題 → `{topic}-解釋說明.md`
- **備份**：目標檔案存在時加時間戳

---

## 智能並行處理

檔案 ≥ 5 時，Agent tool 並行處理：按關聯性分組 → 每組 spawn Agent → 整合結果。

平行處理架構：[explain-parallel-architecture.md](./claude/_common/explain-parallel-architecture.md)

---

## 決策流程

```
用戶輸入 → 指定 md?
  是 → MD 模式（Mermaid）→ 檔案數 ≥ 5? → 並行處理
  否 → Console 模式（ASCII）→ 檔案數 ≥ 5? → 並行處理
```

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## Supporting Files

| 檔案 | 何時讀取 |
|------|---------|
| [explain-parallel-architecture.md](./claude/_common/explain-parallel-architecture.md) | 檔案 ≥ 5 需並行處理時 |
| [explain-deep-analysis.md](./claude/_common/explain-deep-analysis.md) | 分析特定類型內容時 |
| [explain-examples.md](./claude/_common/explain-examples.md) | 需理解各模式實際輸出時 |
