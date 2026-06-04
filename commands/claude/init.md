---
description: "為任意專案自動產生 CLAUDE.md（bottom-up，從子模組到 Root）"
when_to_use: "Generate CLAUDE.md files for a new or unfamiliar codebase. Bottom-up approach: analyze structure, generate module CLAUDE.md files, then synthesize Root CLAUDE.md."
usage: "/claude:init [目錄路徑]"
argument-hint: "/claude:init — 預設為當前目錄，可指定專案根目錄"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
---

# /claude:init — CLAUDE.md 自動生成

為專案從零產生 CLAUDE.md 導航體系。Bottom-up 策略：先理解子模組，再合成 Root，確保上層導航表準確。

## 輸入

- 預設：當前工作目錄
- 可指定：`/claude:init /path/to/project`

## 執行步驟

### Phase 1：結構探索

先用 subagent 掃描整個目錄結構，產出結構報告：

- 目錄樹（排除 `.git`、`node_modules`、`__pycache__`、`.venv`、`build` 等噪音）
- 識別核心模組、入口點、配置、測試目錄
- 識別語言組成（單語言 / 多語言 / FFI binding）
- 模組間依賴方向（哪些模組被最多地方 import）

### Phase 2：Bottom-up 產生 CLAUDE.md

從最深層的子模組開始，一路往上寫到 Root CLAUDE.md。

**既有 CLAUDE.md 處理**：目錄已有 CLAUDE.md 時預設跳過，避免覆蓋手動編輯。使用者可明確確認覆蓋，或先刪除舊檔再執行。

**每個模組 CLAUDE.md 包含**：

- **模組職責**：這個模組做什麼、不做什麼
- **架構定位**：在整體系統中的角色
- **Module Boundaries**：Depends on / Consumed by / Does NOT depend on
- **關鍵設計決策**：從程式碼推導不出來的「為什麼」
- **導航索引**：如果模組很大，加上檔案→功能對照表

**Root CLAUDE.md 額外包含**：

- 架構總覽（語言組成、分層、核心設計理念）
- Module Navigation Map（每個重要目錄一行，含 CLAUDE.md 連結）
- Key Patterns（反覆出現的設計模式）
- Build and Development（如何建置、測試、lint）
- "Finding Things" quick reference（常見問題 → 去哪裡找）

### Phase 3：驗證

- 確認所有 CLAUDE.md 的交叉引用路徑存在
- 確認 Module Navigation Map 涵蓋所有重要模組
- 確認 Root CLAUDE.md 的導航表與子模組 CLAUDE.md 一致

## 判斷哪些模組需要 CLAUDE.md

**需要**：
- 包含 >3 個原始碼檔案的目錄
- 架構關鍵層（core、model、engine、config 等）
- 外部參考頻繁的區域（docs、examples）

**不需要**：
- 單檔案目錄（CLI 入口、thin wrapper）
- 純配置目錄（只有 `__init__.py`）
- 第三方依賴目錄

## CLAUDE.md 寫作品質

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

產出時遵守 encoder-philosophy 的 High Signal / Low Noise 分類。額外約束：
- **功能性描述**：用「做什麼」描述模組，不用版號標記

## 產出

1. 每個重要模組目錄下新增 `CLAUDE.md`
2. 專案根目錄新增 `CLAUDE.md`（導航入口）
3. 最後列出所有新增的 CLAUDE.md 檔案路徑

> **下一步**：產出後建議執行 `/claude:sync` 驗證同步性與品質。
