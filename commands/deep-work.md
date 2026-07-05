---
description: "深度工作模式 - 用戶離開時的自主實作引擎，AI 全力發揮、慢慢思考、完整交付"
when_to_use: "Autonomous implementation mode for when the user is away. Full-power, self-directed execution with deep thinking, error self-healing, and complete delivery."
usage: "/deep-work <任務描述 或 Execution Plan 路徑>"
argument-hint: "任務描述 | Execution Plan 檔案路徑"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]
---

# /deep-work — 深度工作模式

自主實作引擎。用戶已離開，**全力發揮，完整交付。**

## 核心原則

**「深度思考 → 自主決策 → 完整交付 → 驗證通過」**

- **不問問題**：歧義時選最合理方案並記錄理由
- **不趕時間**：充分思考架構、權衡、邊界後再動手
- **不交半成品**：每個功能完整實作、測試通過、Demo 可跑

委託 Skills：
- [autonomous-execution](../skills/autonomous-execution/SKILL.md) — 自主決策、錯誤自癒、完成報告、**紅線/黃線分級**（半夜自主跑時的危險操作安全網）
- [agent-workflow](../skills/agent-workflow/SKILL.md) — 並發控制、模型偵測、Agent spawn 覄範

---

## 前置：進入無人值守模式

deep-work 前提是用戶已離開 —— 權限提示會卡死無人 flow。**必須在 auto-mode 下執行**（流程 dispatch 前先確認）。auto-mode（詳見 [agent-workflow](../skills/agent-workflow/SKILL.md)「Auto Mode」）：classifier model 在命令執行前把關（阻擋 scope 升級 / 未知基礎設施 / 惡意操作），取代人工權限提示。

### substrate 入口（三選一）

| 入口 | 何時用 | 與 auto-mode 關係 |
|------|--------|----------------|
| **agent-view `claude agents` / `claude --bg "<task>"`**（長程 loop 推薦） | EP→build→review 多命令 loop、user 要可監控/介入、要關 terminal 離開 | 用 dir `defaultMode: auto`（repo 已設），**免旗標**；須先互動接受 auto 一次。supervisor 接管、session survive terminal 關閉（「我去洗澡了」不再綁 terminal；[研究預覽 v2.1.139+](https://code.claude.com/docs/zh-TW/agent-view)） |
| **headless `claude -p`**（一次性） | 要 stdout 報告、單一短任務 | `claude --permission-mode auto -p`（現況保留） |
| **`/at` 組合**（跨 session） | 任務超過一個 usage 窗 | `--bg` 派發 → usage 用盡 → `/at <time>` reset 後 resume |

### 與其他自主入口分工（正交可組合）

- **agent-view** = 本機背景長程（同 session，`claude agents` peek/attach 監控）
- **`/at`** = 跨 session 接續（provider usage reset 後 resume；inline 出現在任務描述內，如「`/at 02:20 繼續修`」）
- **`/handoff`** = 跨 session / repo / provider 交接（換手給另一個 session）

組合例：`--bg` 派發長程 loop → usage 用盡 → `/at` reset 接續 → 必要時 `/handoff` 換 provider。

### 誠實處理

permission mode 是 CLI 啟動旗標 / dir 設定，**命令本身無法中途切換**。若當前非 auto-mode → 印出警告「非 auto-mode，無人值守會卡在權限提示；請以 `claude agents`（dir defaultMode=auto）或 `--permission-mode auto` 重啟」並停下，**不靜默降級成互動模式硬跑**。

---

## 流程 dispatch（自主 overlay，依 ARGUMENTS 決定程序）

**deep-work 是「行為模式」（mode）+ 自主 overlay**，可疊加在任意 LLM-chain 程序上。組合時 procedure 委派，deep-work 疊加自主行為（自主決策、歧義選最合理並記錄、完整交付、錯誤自癒、語音通知）。

```
/deep-work <ARG>  ──ARG 決定程序 + 疊加自主行為──

  ├─ ARG 命名 LLM-chain 命令 → 委派該命令 + 自主疊加
  │   • observed：/build、/execution-plan、/code-review、/ep-review、/ep-validate
  │   • reasonable：/fix-test、/lint-fix（自癒 loop）、/audit-test（測試）、/consistency（文檔自洽）、
  │                /followup-review（驗收）、/metadata-sync（commit 前更新 + 補漏）、
  │                /handoff（跨 provider）、/sequential-batch（rate-limit 批次）
  │
  ├─ ARG = 任務描述 → deep-work 自選程序：
  │   • 複雜（需規劃）→ /execution-plan 產 EP →（可選 /ep-validate、/ep-review）→ /build
  │   • fix/debug/研究 → 自身階段 1-5（complex；可自癒接 /fix-test、/lint-fix）
  │   • 完成後自主品質閘門 → /audit-test、/code-review
  │
  └─ ARG 內含接續/substrate 指令：
      • /at <time> → 跨 session 接續修飾詞（reset 後 resume；inline，非獨立分支）
      • substrate 見「前置」（agent-view / -p / /handoff / /sequential-batch）
```

- **ARGUMENTS = `/build <EP>`**（observed 主路徑）：流程骨架**委派 [build.md](./build.md)**（階段 0-6 全跑），deep-work 自身階段 1-5 **不執行**。**不得省略的 build 步驟**（無人在場時唯一機械防線）：階段 0「EP 快檢」強制輸出、階段 1「POC + demo 盤點」映射表、**階段 2「整合路徑覆蓋硬閘門」**（`rg "<新參數>=" tests/`）、階段 5d `/audit-test` —— 絕不靜默跳過（`/deep-work /build` 時硬閘門在最需要它的無人路徑必須生效）。
- **ARGUMENTS = 任務描述**（無 EP）：用 deep-work 自己的階段結構（下方）；複雜者自主升級到 /execution-plan 產 EP 再 build。

## 執行流程

### 階段 1：深度理解

1. **解析輸入**：檔案路徑 → 讀取 EP / Design Plan；任務描述 → 自行分析
2. **探索現有程式碼**：閱讀相關檔案、依賴、import 路徑、模組邊界
3. **架構思考**：列出 ≥ 2 個方案 → 評估權衡 → 選擇最佳並記錄理由
4. **POC + demo 盤點**：掃描 `poc/**/*.py`、`demo_*.py`、`scripts/demo_*.py`、`notebooks/*.ipynb`，建立 `{module} → [poc/demo paths]` 映射表

輸出思考筆記（簡短）：
```markdown
## 深度思考筆記
**任務理解**: [一句話]
**方案選擇**: [選了什麼，為什麼]
**實作範圍**: [新增/修改哪些檔案]
**風險評估**: 🟢/🟡/🔴 + 說明
```

### 階段 2：實作計畫

拆解為 Self-Contained Segments，用 TaskCreate 建立任務清單，按順序逐一執行。

### 階段 3：自主實作

- **Edit 優先**：修改現有檔案用 Edit，新檔案用 Write
- **Read before Edit**：每次編輯前先讀取最新內容
- **Write 降級**：Edit 失敗兩次後改用 Write 整檔覆寫
- **遵循 rules**：遵守所有 `~/Github/ai-rules/rules/`

### 階段 4：驗證

每段完成後：
1. 語法檢查
2. Import 檢查
3. `uv run pytest <test_file> -v`（背景跑）
4. **POC/demo 驗證**（強制）：查映射表，若模組被 POC/demo 引用 → `uv run python <path>`

### 階段 5：收尾

1. `uv run ruff check --fix . && uv run ruff format .`
2. `uv run pytest`（背景跑）
3. POC/demo 全量驗證
4. **Agent Review Cycle**（見下方）
5. instruction 檔同步檢查（AGENTS.md 為主，legacy CLAUDE.md）
6. 移除除錯用程式碼
7. **/audit-test checkpoint**（見 [audit-test](./audit-test.md)）：跑 `/audit-test`（Diff Audit）。重點看角度 4（消費端驗證覆蓋：新 public 參數路徑、整合器型真實邊界）與角度 2（registry 接線）。缺口不得帶進 /commit。用戶不在場時，這是「單元全綠但接線/邊界沒測」隱性 regression 的唯一機械化閘門。
8. **任務級整合路徑檢查**（非 `/build` 任務；若變更含新 callable 參數/注入點 → `rg "<新參數>=" tests/` → 0 hits 必須補消費端整合測試，見 [build.md](./build.md) 階段 2）
9. **紅線跳過覆盤**：盤點任務過程中跳過的紅線操作（見 [autonomous-execution](../skills/autonomous-execution/SKILL.md) Don't-Self-Decide Boundaries 🔴 紅線段），寫入 completion report「🔴 紅線跳過清單」段。半夜自主跑時不阻塞、不語音通知——早上靠此覆盤段判讀任務是否因紅線而半完成。
10. 生成摘要報告

#### Agent Review Cycle

**Writer/Reviewer 分離**：用戶不在場，Agent Review 是唯一的品質閘門。review 執行預設（force 獨立 / max-agents / model inherit / 3-perspective）見 [review-engine](../skills/review-engine/SKILL.md)「review 執行預設」；3-perspective（① clean + ② UC-anchored + ③ Correctness）完整流程見 [agent-review-cycle.md](./instruction/_common/agent-review-cycle.md)。

#### 主 LLM — /judge-review

用 Skill tool invoke `judge-review`，傳入**所有 agent 的 review findings**（合併）。評估每項：✅ 採納 / ❌ 不採納 / ⚠️ 需確認。

#### 主 LLM — Apply Changes

根據 judge-review 的 ✅ 採納清單修改 code。修改完跑 `ruff check --fix && ruff format`。

---

## Agent Spawn 規則

Agent prompt 開頭加上 /rules-reminder 六條規則摘要：
`#` 是毒藥、`$` 是禁區、`rg/fd` 取代 `grep/find`、`uv run` 是王道、`sed` 是地雷、繁體中文

---

## 語音通知

遵循 [voice-notification skill](../skills/voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始深度工作"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「深度工作完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```

---

## 使用範例

```bash
/deep-work 實作用戶認證模組，包含 JWT token 生成、驗證、刷新機制
/deep-work docs/execution-plan.md
/deep-work 重構 data_loader.py，將 CSV 和 Parquet 載入邏輯分離
```

---

## 執行約束

### 強制
1. 動手前先充分思考
2. 核心邏輯必須有單元測試
3. 實作後執行 `uv run pytest` 和 `uv run python demo`
4. 自主決策必須記錄理由

### 禁止
- ❌ 交出半成品就停
- ❌ 遇到錯誤就放棄
- ❌ 使用 `sed` 修改程式碼
- ❌ 多行 `python -c` 中使用 `#` 註解
- ❌ 使用 `timeout`/`gtimeout`/`PYTHONPATH`

### 遵循的 Rules
- `python-standards.md` — Python 規範
- `code-edit-constraints.md` — 編輯約束
- `quality-constraints.md` — 品質約束

---

## 與其他命令的協作

**自主可調度**：`/execution-plan`（無 EP 時 deep-work 任務中自主產，非 user 前置）、`/build`、`/code-review`、`/ep-review`、`/ep-validate`、`/audit-test`
**後續**：`/commit` → `/instruction:sync`
**接續/換手**：`/at`（跨 session reset 接續）、`/handoff`（跨 provider 交接）

> **Agent Review Cycle 已完成。** 可直接 `/commit`；如需額外審查可跑獨立 `/code-review`。

**搭配 `/goal`**：`/goal all TaskCreate tasks completed, uv run pytest exits 0, ruff clean, mypy clean, all demos run`
