# Workflow Review Pattern — 多 Agent 審查協調範本

> **載入時機**: 僅在 effort = ultracode/xhigh 且審查命令偵測到 max-agents > 1 時讀取。

---

## 何時使用 Workflow

| 條件 | 路徑 | 說明 |
|------|------|------|
| effort = ultracode/xhigh 且 max-agents > 1 | ✅ Workflow tool | 確定性協調、schema 輸出、內建進度追蹤 |
| effort < ultracode 或 max-agents = 1 | ❌ Agent tool | 現有邏輯不變（Fallback） |

Workflow tool 的優勢：
- **確定性協調**：腳本控制流程，非 LLM 逐輪決定
- **Context 保護**：中間結果存在腳本變數，不佔用主 context
- **結構化輸出**：schema 強制 agent 回傳可解析的 JSON
- **可恢復**：同 session 可暫停/恢復
- **進度追蹤**：`/workflows` 內建 view

---

## 兩階段模式

全程自動執行，Workflow 不支援 mid-run 用戶輸入。

### Phase 1: Review — 平行維度審查

- `parallel()` spawn 所有啟用維度的 agents
- 每個 agent 用 `schema` 參數強制結構化輸出
- agent 類型一律 `Explore`（read-only by design）
- agent 看不到主對話歷史、其他 agent 結果 — prompt 是唯一 context 來源

### Phase 2: Verify — Adversarial 驗證

- 對 Critical / must-fix severity 的 findings spawn 驗證 agent
- 驗證 agent 嘗試**推翻（refute）** finding
- **預設強度**：1 verifier/finding
- **Critical 升級**：3 verifier + ≥2/3 確認 → finding 保留
- 非 Critical findings 直接保留（交由 Main LLM judge-review 最終判斷）

---

## Schema 定義

### DimensionVerdict（Review agent 回傳）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "description": "唯一 ID，如 F1, F2" },
          "title": { "type": "string" },
          "severity": { "type": "string", "enum": ["critical", "important", "suggestion"] },
          "file": { "type": "string", "description": "專案相對路徑" },
          "line": { "type": "number" },
          "description": { "type": "string" },
          "suggestion": { "type": "string" }
        },
        "required": ["id", "title", "severity", "description", "suggestion"]
      }
    },
    "summary": { "type": "string", "description": "該維度的整體評估" }
  },
  "required": ["findings", "summary"]
}
```

### VerifyVerdict（Verify agent 回傳）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "isReal": { "type": "boolean", "description": "finding 是否成立" },
    "reason": { "type": "string", "description": "判斷理由" },
    "confidence": { "type": "string", "enum": ["high", "medium", "low"] }
  },
  "required": ["isReal", "reason", "confidence"]
}
```

---

## Finding Record（跨命令持久化標準）

> **核心原則**：審查發現(finding)的對話對象主要是另一個 LLM(`/build` 內串接、`/copy` 給外部 LLM)。finding 必須持久化、結構化,跨 session、跨命令可追蹤。

### Finding Record = DimensionVerdict + 追蹤欄

Review agent 回傳的 `DimensionVerdict.findings[]` 是**發現時**狀態。持久化時擴充為 Finding Record,加入生命週期追蹤欄:

| 欄位 | 來源 | 用途 |
|------|------|------|
| `id` / `title` / `severity` / `file` / `line` / `description` / `suggestion` | DimensionVerdict 沿用 | 發現本體 |
| `status` | 追蹤 | 生命週期見下(跨命令 join key) |
| `source` | 追蹤 | 產生命令(由表格標題 `## <命令> Findings` 編碼,不單獨成欄) |
| `decision` | 追蹤 | judge-review 的 ✅ / ❌ / ⚠️ |

**status 生命週期**:

- **Code review flow**(經 judge-review):`open` →(`adopted` / `rejected` / `needs-confirmation`)→ `implemented` → `verified` → `closed`。**rejected 不經 implemented**,直接 `closed`(不實作)
- **EP flow**(ep-review/ep-validate,無 judge-review):`open` → `implemented`(修正入 EP)/ `verified`(POC 通過)
- **decision → status 映射**(judge-review):✅ → `adopted`、❌ → `rejected`、⚠️ → `needs-confirmation`
- commit 階段 2.6 檢查殘留 `open` Critical

### 持久化位置

| 情境 | 位置 |
|------|------|
| 有 EP 上下文(EP 審查、EP 驅動 build) | 回寫 EP 的 review 區段(沿用 ep-review) |
| 無 EP(獨立 code-review / judge-review / followup-review) | `.review/<branch>.md`(綁定分支,代表一次變更的 finding 清單) |

`.review/` 為 ephemeral 工作產物,**各專案須將 `.review/` 加入 `.gitignore`**(避免審查筆記污染 repo 歷史)。

### Markdown 表格呈現格式(持久化與 /copy 載體)

人類可讀 + 機器可解析。所有命令的持久化 finding 統一用此格式:

```
## <命令> Findings — <branch 或 EP 段落>

| ID | 嚴重度 | 檔案:行 | 問題 | 建議 | 狀態 | 決策 |
|----|--------|---------|------|------|------|------|
| F1 | 🔴 critical | src/foo.py:42 | ... | ... | open | — |
| F2 | 🟡 important | src/bar.py:10 | ... | ... | adopted | ✅ |
```

`/copy` 場景:用戶貼此表格給外部 LLM,回饋以同格式 append 回寫。

---

## 腳本骨架

各命令提供具體的 `dimensions` 陣列（維度名稱、prompt、啟用條件）。骨架定義通用協調邏輯：

```javascript
export const meta = {
  name: '[command]-review',
  description: '[command] multi-agent review with adversarial verification',
  phases: [
    { title: 'Review', detail: '平行維度審查' },
    { title: 'Verify', detail: 'Adversarial 驗證' }
  ]
}

const REVIEW_SCHEMA = { /* DimensionVerdict schema */ }
const VERIFY_SCHEMA = { /* VerifyVerdict schema */ }

// --- 各命令定義自己的 dimensions ---
// const dimensions = [
//   { key: 'completeness', prompt: '...', enabled: true },
//   ...
// ]
// const enabledDimensions = dimensions.filter(d => d.enabled)

// Phase 1: Review
phase('Review')
const reviews = await parallel(
  enabledDimensions.map(d => () =>
    agent(d.prompt, {
      label: `review:${d.key}`,
      phase: 'Review',
      schema: REVIEW_SCHEMA,
      agentType: 'Explore'
    })
  )
)

// Phase 2: Verify (only Critical findings)
// ⚠️ 可自訂：各命令可調整 verifier 數量和 quorum 門檻
//   預設：Critical → 3 verifier + 2/3 quorum
//   輕量（如 /ep-review）：must-fix → 1 verifier/finding
//   在此修改 verifier 數量：Array.from({length: N}, ...)
phase('Verify')
const allFindings = reviews.filter(Boolean).flatMap(r => r.findings)
const criticalFindings = allFindings.filter(f => f.severity === 'critical')

// 非 Critical 直接保留
const normalFindings = allFindings.filter(f => f.severity !== 'critical')

// Critical → 3 verifier + 2/3 quorum
const verified = await parallel(
  criticalFindings.map(f => () =>
    parallel(Array.from({length: 3}, () =>
      agent(
        `Adversarially verify this finding. Try to REFUTE it. Check against actual code.
         Finding: ${f.title} — ${f.description}
         File: ${f.file}:${f.line}
         Default to isReal=false if uncertain.`,
        { label: `verify:${f.id}`, phase: 'Verify', schema: VERIFY_SCHEMA, agentType: 'Explore' }
      )
    ))
  )
)

// 2/3 quorum
const confirmedCritical = criticalFindings.filter((f, i) => {
  const votes = verified[i].filter(Boolean)
  return votes.filter(v => v.isReal).length >= 2
})

return {
  confirmed: [...normalFindings, ...confirmedCritical],
  stats: { total: allFindings.length, confirmed: normalFindings.length + confirmedCritical.length }
}
```

### Agent Prompt 必須包含

每個 Review agent prompt 必須包含：
1. 審查範圍（git diff 範圍、EP 路徑、檔案清單）
2. 該維度的檢查項目清單
3. 相關檔案路徑（必讀）
4. 方法論引用（code-review-and-quality / 對應 skill）
5. rules-reminder 六條規則摘要（agent 看不到 auto-loaded rules）

---

## 結果交接

Workflow 完成後回傳 `{confirmed, stats}`，由 Main LLM 接手後續處理：

| 命令 | 後續處理 |
|------|---------|
| `/build` Phase 4 | invoke judge-review skill → evaluate ✅/❌/⚠️ → apply ✅ findings |
| `/ep-review` | 合成 4 個 DimensionVerdict → EP write-back（回寫修正） |
| `/code-review` | 合成 results → 分三級（Critical/Important/Suggestion）→ commit message |

---

## 與 Agent Tool Fallback 的關係

Workflow 路徑和 Agent tool 路徑**共存不互斥**：

- 命令文件中現有的 Agent tool 指令標記為「Agent Tool 模式（Fallback）」
- Workflow 指令標記為「Workflow 模式（Ultracode）」
- 分支點在 effort level 偵測，不影響任何現有邏輯
- Fallback 路徑的文字**完全保留**，不做任何修改
