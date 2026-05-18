---
description: "基於 Execution Plan 逐段實作（準備、TDD、驗證、提交）。/build <EP路徑> [段落編號]"
when_to_use: "Implement an Execution Plan segment-by-segment using TDD. Use after /ep-review and /verify-review. Supports parallel agents with --max-agents."
usage: "/build <Execution Plan 路徑> [段落編號]"
argument-hint: "<Execution Plan 檔案路徑> [段落編號] [--max-agents N]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]
---

# /build — 基於 Execution Plan 逐段實作

你是實作工程師，負責基於 Execution Plan 進行逐段實作。

## 🎯 核心目標

**「準備 → 逐段實作 → 驗證 → 提交」**

每個段落都是一個 Self-Contained Segment，獨立實作、獨立測試、獨立提交。

## 🧠 自主實作模式

> **EP 已經過 `/ep-review` 和 `/verify-review` 充分審查，實作階段自主執行。** 自主決策、錯誤自癒、完成報告等方法論遵循 [autonomous-execution](../skills/autonomous-execution/SKILL.md) skill。

## 📚 委託 Skills

實作時自動載入以下 skills，提供 HOW 的方法論：

- [rules-reminder](../skills/rules-reminder/SKILL.md) — `rg`/`fd` 取代 `grep`/`find`、禁止 `sed`、管道拆兩步等 Bash 規則
- [test-driven-development](../skills/test-driven-development/SKILL.md) — TDD 循環（RED → GREEN → REFACTOR）、測試寫作規範
- [incremental-implementation](../skills/incremental-implementation/SKILL.md) — 範圍紀律、簡潔優先、漸進式交付、反合理化
- [debugging-and-error-recovery](../skills/debugging-and-error-recovery/SKILL.md) — demo 執行失敗時的系統化除錯
- [autonomous-execution](../skills/autonomous-execution/SKILL.md) — 自主決策框架、錯誤自癒、權限最小化、完成報告
- [python-type-gap](../skills/python-type-gap/SKILL.md) — 第三方套件 type gap 四層處理策略（mypy 失敗時參考）

---

## 📋 執行流程

### 階段 0：EP 快檢（實作前必做）

快速確認 EP 品質，**僅嚴重矛盾才停下，其餘自行判斷並記錄**。

#### 前置流程確認

快速確認以下流程（僅記錄，不因此停下）：

```
/spec → /execution-plan → /ep-review → /verify-review → /build
```

- [ ] `/ep-review` 是否已執行？
- [ ] `/verify-review` 是否已執行？
- [ ] EP 是否已根據審查結果修正？

> 未完成的前置流程記錄於完成報告，不阻擋實作。

#### EP 品質快掃

逐項檢查 EP 是否具備實作條件：

| 檢查項目 | 通過標準 | 發現問題時 |
|----------|----------|------------|
| **段落結構** | 每段有 Context、Pseudo Code、驗證策略、核心要點 | 標記缺漏，自行補上合理內容 |
| **Pseudo Code 可執行性** | 具體到可直接翻譯為程式碼，非模糊描述 | 標記模糊處，自行推斷最合理意圖 |
| **驗證策略具體性** | 有明確的測試案例、輸入輸出、斷言條件 | 標記不具體處，自行補充合理測試 |
| **段落依賴合理性** | 依賴順序可執行，無循環依賴 | 標記衝突，自行調整順序 |
| **技術選型明確** | 套件、API、架構決策已確定，無待選項 | 標記未決項，選擇最簡單方案 |
| **依賴錨點有效性** | 每段「依賴錨點」的 file:line 與實際程式碼一致，或標記為「無」 | 讀取錨點標記的 file:line，比對實際內容；drift 時先更新 EP 再實作 |

#### 依賴圖與平行可行性分析

1. **建構段落依賴圖**：掃描每個段落的「依賴關係」和「語義約束」
2. **識別可平行段落**：無依賴鏈 + 無語義約束關聯的段落可平行
3. **套用 max-agents 限制**：
   - 從系統提示詞偵測自身 GLM 模型，查下表決定 Agent 模型和並發上限：
     | 主 session GLM 模型 | Agent 模型 | 並發上限 |
     |--------------------|-----------|---------|
     | `glm-4.7` (haiku) | haiku | 1 |
     | `glm-5.1` (sonnet) | sonnet | 4 |
     | `glm-5-turbo` (opus) | sonnet（降級） | 1 |
   - 用戶傳入 `--max-agents N` 時，實際上限 = `min(N, 查表上限)`
   - 未傳入時，預設上限 = 查表的並發上限
   - spawn Agent 前印出 `[Agent] model=X, max=N, current=M` 確認
4. **有語義約束的段落強制序列**：即使無依賴鏈，共享語義約束的段落必須序列執行

輸出格式：
```markdown
### 平行可行性分析
**執行模式**: 序列 / 平行（max-agents=N）
**Wave 分組**:
- Wave 1: [段落列表]（可平行）
- Wave 2: [段落列表]（語義約束 → 序列）
- ...
```

#### 關鍵問題釐清

掃描 EP 後，**僅嚴重矛盾才停下問**，其餘自行判斷並記錄。

僅以下情況停下問用戶：
- EP 與現有程式碼存在不可調和的矛盾（且無法合理推斷）
- 缺少關鍵實作細節且有多種差異很大的可能解讀

其餘情況自行決策，記錄於完成報告的「架構決策記錄」。

#### 快檢輸出

```markdown
## EP 快檢結果

**前置流程**: ✅ 已完成 / ⚠️ 未完成（缺 [命令]，但繼續實作）
**EP 品質**: ✅ 可實作 / ⚠️ 有 N 項自行補充

### 自行處理項目（如有）
1. [具體問題] → 決策：[選擇的方案]
2. ...

### 結論
✅ 進入自主實作 / 🛑 嚴重矛盾需用戶確認
```

### 階段 1：準備

1. **讀取計畫書**：完整讀取 Execution Plan，識別段落結構、依賴關係、執行順序
2. **查證現有程式碼**：讀取計畫書提到的檔案，確認現有實作狀態
3. **驗證依賴錨點**：逐一讀取每段「依賴錨點」標記的 file:line，比對實際程式碼與 EP 描述是否一致。drift 時先更新 EP 再繼續
4. **檢查清單**：
   - [ ] Demo 檔案是否需要新增/修改？（`demo_` 前綴）
   - [ ] 測試檔案是否需要新增/修改？（`test_` 前綴）
   - [ ] CLAUDE.md 是否需要同步更新？
   - [ ] 依賴關係是否完整？有循環依賴風險嗎？
   - [ ] 向後相容：預設不考慮，影響外部系統時需確認

### 階段 2：逐段實作

對每個段落執行實作循環。**EP 段落的四個元素直接對應 TDD 步驟**：

| EP 段落元素 | TDD 步驟 | 說明 |
|---|---|---|
| **Context** | 開始前讀取 | 理解背景、依賴、成功標準 |
| **驗證策略** | RED | 照著設計測試，不用自己想 |
| **Pseudo Code** | GREEN | 照著設計實作，不要自己發明 |
| **核心實作要點** | REFACTOR | 檢查是否都涵蓋到了 |

```
讀取 Context → 依驗證策略寫測試（RED）→ 依 Pseudo Code 實作（GREEN）→ 核心要點檢查（REFACTOR）→ 驗證 → 下一段
```

#### 執行模式選擇

**未傳入 --max-agents 或 MAX_CONCURRENT_AGENTS=0 或所有段落有依賴/語義約束**：序列執行（現有流程）

**max-agents > 1 且有可平行段落**（max-agents 由 `--max-agents` 參數與 `MAX_CONCURRENT_AGENTS` 環境變數取較小值決定）：

1. **依賴圖分層**：按依賴順序分為多個 wave
2. **同 wave 平行**：無語義約束關聯的段落 → 啟動平行 Agent（上限 max-agents）
3. **Agent 職責**：每個 Agent 執行完整 TDD 循環（RED → GREEN → REFACTOR → 驗證）
4. **Wave 間序列**：同一 wave 所有 Agent 完成後 → 整合驗證 → 下一 wave

##### Agent Context 邊界

Agent 擁有獨立的 context window，與主對話和其他 Agent 完全隔離：

| 內容 | Agent 可見 | 說明 |
|------|-----------|------|
| CLAUDE.md / rules/ | ✅ | 專案指令自動載入 |
| 工作目錄 | ✅ | 繼承主對話 CWD |
| 主對話歷史 | ❌ | EP 準備階段的分析結論、架構決策完全看不到 |
| 其他 Agent 結果 | ❌ | 各 Agent 獨立 context |
| EP 準備結論 | ❌ | 除非主 LLM 在 prompt 中明確傳遞 |

**因此：主 LLM 傳給 Agent 的 prompt 是 Agent 理解任務的唯一來源。** CLAUDE.md 提供規範，但不提供任務上下文。

##### 主 LLM 的 Prompt 結構

主 LLM 啟動 Agent 時，prompt 必須包含以下欄位，確保 Agent 能獨立完成任務：

```markdown
## 任務：段落 {N} — {段落名稱}

### EP 段落內容
{完整貼上該段落的 Context、Pseudo Code、驗證策略、核心要點}

### 準備階段結論
- 現有程式碼狀態：{相關檔案的當前實作摘要}
- 架構決策：{準備階段做出的關鍵決策及理由}
- 技術選型確認：{使用的套件、API、模式}

### 語義約束
- {與其他段落的共享假設，或「無」}

### 相關檔案路徑
- 必讀：{Agent 應先讀取的檔案清單}
- 可修改：{Agent 有權修改的檔案範圍}
- 禁止修改：{共用檔案，由主 Agent 統一處理}
```

##### Agent 啟動後的 Context 收集流程

Agent 收到 prompt 後，按以下順序建立 context：

1. **讀取 EP 段落** — prompt 中已包含，確認理解
2. **讀取相關檔案** — 按 prompt 中的「必讀」清單逐一讀取
3. **讀取相關 CLAUDE.md** — 修改目錄及上層目錄的 CLAUDE.md（如存在）
4. **確認現有程式碼狀態** — 與 prompt 中的「準備階段結論」交叉驗證
5. **發現不一致時** — 以實際程式碼為準，記錄偏差

##### Skills 處理策略

Agent 不會自動載入主對話的 skills。採用以下策略：

- [rules-reminder](../skills/rules-reminder/SKILL.md)：在 prompt 中明確指示 Agent invoke，確保 Agent 遵守 rg/fd、禁止 sed 等規則
- [test-driven-development](../skills/test-driven-development/SKILL.md)、[incremental-implementation](../skills/incremental-implementation/SKILL.md)：在 prompt 中明確指示 Agent invoke 這些 skills
- [debugging-and-error-recovery](../skills/debugging-and-error-recovery/SKILL.md)：Agent 遇到錯誤時自行 invoke
- [autonomous-execution](../skills/autonomous-execution/SKILL.md)：在 prompt 中明確指示 Agent invoke

Prompt 中的指示範例：
```
執行前先 invoke 以下 skills 載入方法論：
- rules-reminder
- test-driven-development
- incremental-implementation
- autonomous-execution
```

##### Agent 執行約束

- 每個 Agent 只負責一個段落，遵循完整的 TDD 流程
- Agent 之間不共享狀態，所有必要資訊透過 prompt 傳遞
- 共用檔案（如 `__init__.py`）的修改統一由主 Agent 在 wave 間處理，Agent 僅負責段落專屬檔案
- 主 Agent 監控 Agent 結果，失敗時記錄 ⚠️ 並繼續下一 wave
- Agent 發現語義約束衝突時，立即回報主 Agent，不自行決定

TDD 的執行細節（怎麼寫測、怎麼寫最少程式碼、怎麼重構）遵循 [test-driven-development](../skills/test-driven-development/SKILL.md) skill。
範圍紀律和簡潔優先遵循 [incremental-implementation](../skills/incremental-implementation/SKILL.md) skill。

#### EP 專屬約束

- **照著 EP 寫，不要自己發明**：測試依驗證策略，實作依 Pseudo Code
- **記錄偏差**：與 Pseudo Code 有出入時，記錄差異原因
- **自行判斷並記錄**：計畫書不明確時，選擇最合理方案並記錄於完成報告
- **記錄疑慮不中斷**：有疑慮時先選最合理方案繼續，將疑慮、選擇、其他方案記錄到待確認清單，最後統一讓用戶確認
- **錯誤自癒**：連續 3 次失敗 → 記錄問題標記 ⚠️，繼續下一段
- **依賴錨點 drift check**：實作每段前驗證該段的「依賴錨點」。錨點 drift 時先更新 EP（修正過時的 file:line、型別、常數引用），再基於更新後的 EP 實作。避免基於過時假設寫碼

#### 自主決策

決策策略、不自行處理邊界、錯誤自癒流程遵循 [autonomous-execution](../skills/autonomous-execution/SKILL.md) skill。EP 專屬補充：

- EP 描述有歧義時，優先依 EP Context 推斷意圖
- 記錄所有偏差和疑慮於完成報告的待確認清單

#### 驗證

每個段落完成後：
- `uv run ruff check --fix . && uv run ruff format .`
- `uv run mypy .`
- `uv run pytest <test_file> -v`
- 確認通過 → 記錄完成 → 下一段
- mypy 失敗時參考 [python-type-gap](../skills/python-type-gap/SKILL.md) skill 的四層策略修正

### 階段 3：整合驗證

所有段落完成後：
1. **全量 Lint**：`uv run ruff check --fix . && uv run ruff format .`
2. **全量型別檢查**：`uv run mypy .`
3. **全量測試**：`uv run pytest`
4. **Demo 驗證**：
   - 掃描 `demo_*.py` 和 `examples/*.py`
   - 逐一 `uv run python <path>` 執行
   - 失敗時用 [debugging-and-error-recovery](../skills/debugging-and-error-recovery/SKILL.md) skill 分析根因
   - 輸出通過/失敗報告

### 階段 4：完成報告

實作全部完成後，輸出以下報告：

```markdown
## 實作完成報告

### 實作結果

**新增檔案**:
- [路徑] - [用途]

**修改檔案**:
- [路徑] - [修改摘要]

**測試結果**: ✅ N passed / ❌ M failed
**Demo 結果**: ✅ 可運行 / ❌ [問題描述]

### 架構決策記錄
| 決策 | 選擇 | 理由 |
|------|------|------|
| [決策] | [選項] | [為什麼] |

### 待確認清單（實作過程中的疑慮）

> 以下是我覺得有問題、自行做了決策的地方。請檢查是否合理，如需調整請告知。

| # | 疑慮描述 | 我的作法 | 理由 | 其他可行方案 |
|---|---------|---------|------|------------|
| 1 | [遇到的問題] | [選了什麼做法] | [為什麼選這個] | [方案A / 方案B] |

### ⚠️ 未解決問題
- [標記為 ⚠️ 的未解決問題]
- [錯誤自癒失敗的段落]

### Agent 執行統計（平行模式適用）
- **執行模式**: 序列 / 平行（max-agents=N）
- **Wave 數量**: N waves
- **Agent 總數**: N agents
```

---

## 🔧 執行約束

### 強制執行
1. **必須先執行 EP 快檢**（階段 0），驗證 EP 狀態
2. **必須完整讀取計畫書**
3. **必須查證現有程式碼**
4. **每個段落必須 TDD（RED → GREEN → REFACTOR）**
5. **每個段落必須獨立驗證**
6. **每個段落必須通過 ruff + mypy 檢查**

### 禁止行為
- ❌ 跳過測試直接實作
- ❌ 一個段落提交多個不相關的修改
- ❌ 在段落範圍外修改程式碼
- ❌ 使用 `sed` 修改程式碼
- ❌ 使用 `from __future__ import annotations`（掩蓋缺失 import 和 circular import）
- ❌ 中間狀態提交破損的程式碼

---

## 📚 與其他命令的協作

### 流程位置
```
/spec → /execution-plan → /ep-review → /verify-review → /build → /code-review → /commit
```

### 前置命令
- `/execution-plan` — 生成被實作的計畫書
- `/ep-review` — 審查計畫書合理性（三個 LLM）
- `/verify-review` — 評估審查建議，修正計畫書

### 後續命令
- `/code-review` — 實作完成後審查程式碼
- `/commit` — 審查通過後提交變更

---

## ✅ 完成標準

1. ✅ 所有段落已實作並通過測試
2. ✅ ruff check + mypy 全量通過
3. ✅ 全量測試通過
4. ✅ Demo 全部通過
5. ✅ 完成報告已輸出（含架構決策記錄）

> **所有變更尚未 commit。** 請執行 `/code-review` 後再 `/commit`。
