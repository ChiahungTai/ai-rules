---
description: "為任意專案自動產生 instruction file 體系（root + 模組都雙檔：AGENTS.md source + CLAUDE.md @AGENTS.md wrapper，bottom-up）"
when_to_use: "Generate instruction files for a new or unfamiliar codebase. Bottom-up: analyze structure, generate module AGENTS.md (source) + CLAUDE.md (@AGENTS.md wrapper), synthesize Root AGENTS.md (source) + CLAUDE.md (wrapper). 雙檔模式見 instruction-writing.md。"
usage: "/instruction:init [目錄路徑]"
argument-hint: "/instruction:init — 預設為當前目錄，可指定專案根目錄"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
---

# /instruction:init — instruction file 體系自動生成

為專案從零產生 instruction file 導航體系（**root + 每個模組都雙檔**：`AGENTS.md` source + `CLAUDE.md` `@AGENTS.md` wrapper，雙檔模式見 [instruction-writing.md](../../rules/instruction-writing.md)）。Bottom-up 策略：先理解子模組，再合成 Root，確保上層導航表準確。

## 輸入

- 預設：當前工作目錄
- 可指定：`/instruction:init /path/to/project`

## 執行步驟

### Phase 1：結構探索

先用 subagent 掃描整個目錄結構，產出結構報告：

- 目錄樹（排除 `.git`、`node_modules`、`__pycache__`、`.venv`、`build` 等噪音）
- 識別核心模組、入口點、配置、測試目錄
- 識別語言組成（單語言 / 多語言 / FFI binding）
- 模組間依賴方向（哪些模組被最多地方 import）

### Phase 1.5：Dependency Snapshot（如果 scan-project 可用）

執行 [/scan-project](../../skills/scan-project/SKILL.md) skill 產出統一知識快照：

```bash
uv run python ${CLAUDE_SKILL_DIR}/scripts/scan_project.py --project-root . --output .project-snapshot.json --init
```

從 snapshot 取得：

- `dep_graph.modules` / `dep_graph.edges` — 精確的模組依賴結構（取代 Phase 1 的粗略分析）
- `findings` — 預計算的機械性問題（X6 模組缺 instruction 檔、X-cap-path 路徑失效等）
- `fingerprint` — 變化偵測用 counts + hashes

其餘資訊（現有 Capabilities、Kanban 卡片、instruction 檔（AGENTS.md/CLAUDE.md）分佈）由 LLM 直接讀取檔案系統，不經 snapshot。

**Capabilities 覆蓋缺口報告**：列出缺少 Capabilities 表格的 library 模組（instruction 檔 AGENTS.md/CLAUDE.md），但不自動生成（需要人類意圖）。

**無 scan-project 時**：跳過此 phase，Phase 2 使用 Phase 1 的粗略分析。

### Phase 2：Bottom-up 產生 instruction files（每層 AGENTS.md source + CLAUDE.md wrapper）

從最深層的子模組開始，一路往上寫到 Root：**每層**（root + 模組）都產生 AGENTS.md（source，neutral）+ CLAUDE.md（`@AGENTS.md` wrapper，讓 Claude 讀到 AGENTS.md）——雙檔模式見 [instruction-writing.md](../../rules/instruction-writing.md)。

**既有 instruction 檔處理**：
- Phase 1.5 有 snapshot → LLM 直接掃描目錄結構確認哪些目錄已有 AGENTS.md，跳過
- 無 Phase 1.5 → 目錄已有 AGENTS.md 時預設跳過。使用者可明確確認覆蓋
- legacy 單檔模組（只有 CLAUDE.md，無 AGENTS.md）：從 CLAUDE.md 抽中立內容寫進 AGENTS.md source，CLAUDE.md 改為 `@AGENTS.md` thin wrapper

**每個模組 AGENTS.md 包含**（source，四家 harness 都讀）：

- **模組職責**：這個模組做什麼、不做什麼
- **架構定位**：在整體系統中的角色
- **Module Boundaries**：Depends on / Consumed by / Does NOT depend on
- **關鍵設計決策**：從程式碼推導不出來的「為什麼」
- **導航索引**：如果模組很大，用 `### 類別小標題` 分組導航種子（非集中符號對照表，見 [instruction-writing.md](../../rules/instruction-writing.md)「大模組 selectivity」段；檔案路徑選用，LSP 可從符號解析）

**Module Boundaries 精確度**（有 Phase 1.5 時加成）：
- `Depends on` 從 `edges[]` 精確推導（而非猜測）
- `Does NOT depend on` 從 `modules[]` 的 `imported_by` 反向推導
- Use LSP findReferences on module-level symbols to verify module boundaries when dep_graph is unavailable
- 無 snapshot 時，Module Boundaries 基於 Phase 1 的粗略 import 分析

**Root AGENTS.md 包含**（source，neutral 專案資訊——四家 harness 開本專案都讀）：

- 架構總覽（語言組成、分層、核心設計理念）
- Module Navigation Map（每個重要目錄一行，含模組 AGENTS.md 連結）
- Key Patterns（反覆出現的設計模式）
- Build and Development（如何建置、測試、lint）
- "Finding Things" quick reference（常見問題 → 去哪裡找）

**Root CLAUDE.md** = `@AGENTS.md`（把 neutral 專案資訊拉進 Claude session）+ Claude 專屬段（hooks、slash command workflow——若有）。**thin wrapper，不重複 AGENTS.md 內容**。

**模組 CLAUDE.md** = `@AGENTS.md` thin wrapper（通常只一行——模組層少有 Claude 專屬機制；純粹讓 Claude 讀到模組 AGENTS.md source）。其他 harness（ZCode/OpenCode/Codex）直接讀模組 AGENTS.md，不需此 wrapper。

### Phase 3：驗證

- 確認所有 instruction files（每層 AGENTS.md + CLAUDE.md）的交叉引用路徑存在
- 確認 Root AGENTS.md 的 Module Navigation Map 涵蓋所有重要模組，且連結指向模組 AGENTS.md source
- 確認每個模組 CLAUDE.md = `@AGENTS.md` thin wrapper（不重複 AGENTS.md neutral 內容）；Root CLAUDE.md 同
- **dep-graph 驗證**（有 Phase 1.5 時）：確認 Module Boundaries 的 "Depends on" 與 `edges[]` 一致

## 判斷哪些模組需要 instruction 檔

**需要**：
- 包含 ≥3 個原始碼檔案的目錄
- 架構關鍵層（core、model、engine、config 等）
- 外部參考頻繁的區域（docs、examples）

**不需要**：
- 單檔案目錄（demo 給老闆入口，基於 library）
- 純配置目錄（只有 `__init__.py`）
- 第三方依賴目錄

**Phase 1.5 加成**：`findings` 中的 X6 問題直接指出哪些模組缺少 instruction 檔。

## instruction 檔寫作品質

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

產出時遵守 encoder-philosophy 的 High Signal / Low Noise 分類。額外約束：
- **功能性描述**：用「做什麼」描述模組，不用版號標記

## 產出

1. 每個重要模組目錄新增 `AGENTS.md`（source，四家 harness 讀）+ `CLAUDE.md`（`@AGENTS.md` thin wrapper，Claude 讀）
2. 專案根目錄新增 `AGENTS.md`（source，harness-neutral）+ `CLAUDE.md`（`@AGENTS.md` wrapper + Claude 專屬段）——見 [instruction-writing.md](../../rules/instruction-writing.md) 雙檔模式
3. `.project-snapshot.json`（如果 Phase 1.5 有執行）
4. 最後列出所有新增的 instruction file 路徑

> **下一步**：產出後建議執行 `/instruction:sync` 驗證同步性與品質。

---

## 語音通知

遵循 [voice-notification skill](../../skills/voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始產生 instruction 檔"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「instruction 檔產生完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```
