---
harness-scope: neutral
paths:
  - "**/*.md"
---

# Instruction File 撰寫規範

> **🔴 強烈警告**: AI 寫作 instruction file 時**絕對禁止**加入統計資訊、版本號、更新日期等元資訊（❌ 行為表與自檢清單見下方 skill「元資訊禁止行為」章）

> **完整規範**（frontmatter 欄位、章節組織、引用語法選擇、導航細則與段落標題標準、映射表 drift 查證、Decoder Test、元資訊禁止行為表與第一性原理論證、文檔自洽五維檢查）見 **instruction-writing skill**（on-demand）——撰寫或修改任何 instruction 檔時載入

## 基本原則

instruction file 是給 AI 的協作指南，應專注於**核心原則**和**執行約束**，避免冗餘細節。品質標準是 Signal/Noise ratio——instruction file 是模組知識的 Encoder（壓縮表示）。

## 檔案命名（雙檔模式）

每層都是 `AGENTS.md`（source, harness-neutral——四家 harness 都讀；body 禁 Claude 專屬散文）+ `CLAUDE.md`（`@AGENTS.md` thin wrapper, Claude 專屬）。**每層雙檔確保四家 harness 都讀得到該層 instruction**。全域指南（如 `ai-development-guide.md`）是獨立檔部署到各 harness 全域位置，**不是專案 root AGENTS.md**。

> **`@` transclusion 是 Claude Code 專用**：CLAUDE.md 啟動時自動展開 `@path`；AGENTS.md（與 ZCode/Codex/Muse）**不展開 `@`**——AGENTS.md 內不可用 `@` 拉內容。

## 內容分類（精簡版）

- **High Signal**（該包含）：導航指引（概念→symbol name 種子，位置由 LSP 接手）、設計理由（預設一句 why；易被 rationalize 動搖的規則才展開反駁論證，段落標 `補充論證`/`第一性原理`）、架構約束、模組邊界、失敗教訓、執行約束、型別關係、Pipeline 編排、慣例映射、可複用基礎設施、負空間指導（不做什麼）、行為校準
- **Low Noise**（該避免）：可推導內容（API 簽名、參數表、欄位列表）、完整範例（>5 行）、元資訊（版本號/日期/統計/Changelog）、專案特定事實（泛用 rules 用 `<placeholder>`；失敗教訓真實案例例外——須含「真實案例」marker）、Class→檔案映射表（LSP 可推導、必然 drift）、重複描述（集中清單與 per-concept 種子重複）

## 導航優先

instruction file 的導航職責是「概念→符號」種子；「符號→位置」由 LSP 接手。文檔寫作精力放在語義知識（設計理由、約束、失敗教訓），而非檔案路徑表。
