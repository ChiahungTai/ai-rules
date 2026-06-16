---
description: "人類 viewport（結構軸）— whole-picture 渲染（City Map/Flows/Boundaries）+ 重用候選枚舉，讓人判「結構撐得起 use case 嗎」「在重造既有的嗎」。/arch-review [scope]"
when_to_use: "Human-facing structure viewport (layer 3, B-axis). Leverages human whole-picture intuition (detail-forgetful but senses reuse/relationships) by fueling it with machine detail-completeness. Renders architecture as mental models (city map, key flows, boundaries) + enumerates reuse candidates. Human judges 'does this structure support the use cases' and 'am I reinventing existing'. Mechanical division: scan-project/Pattern Radar enumerate (primary), lsp-architect verify (secondary). Timing: post-EP / early build when structure is cheap to change."
usage: "/arch-review [module-path | --ep <EP>] [--focus <symbol>]"
argument-hint: "無參數審變更涉及的結構 / module path 審該模組 / --ep 審 EP 架構段落 / --focus 審某 symbol 生態"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Workflow"]
---

# /arch-review — 結構 viewport（whole-picture）

> **核心理念**：人類 viewport 的**結構軸**（layer 3, B 軸）。
> **人的 edge：whole-picture 直覺** —— 細節會忘（記不全每個 enum / class），但能隱約覺得「那邊好像有可重用的東西」「這感覺在重造」。本命令用**機器的 detail 完整度**給人的 whole-picture 直覺**加燃料**，讓人判「結構撐得起 use case 嗎」「在重造既有的嗎」。

不是 LSP 機械驗證 call chain（`lsp-architect` agent）；不是 diff 結構符合度（`/code-review` axis 3）。
是：渲染**整體結構心智模型** + **枚舉重用候選**，讓人用 whole-picture 判讀。

**LLM blind spot 本命令補的**：LLM detail 強、whole picture 弱 → 傾向重造既有東西（人常需提醒「用那個 enum」）。本命令把所有既有 symbol 撈全，讓人的整體感操作在完整資訊上，而非「我記得」。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [mermaid](../skills/mermaid/SKILL.md) — City Map / Flows 渲染（`--md` 時）
- [agent-workflow](../skills/agent-workflow/SKILL.md) — 並發控制

按需讀取：
- [code-review-and-quality](../skills/code-review-and-quality/SKILL.md) — LSP 輔助查證 + 審查者自證方法論（Phase 2）
- [lsp-navigation](../rules/lsp-navigation.md) — 機械查證工具決策樹

受眾模型見 [CLAUDE.md](../CLAUDE.md)「命令的受眾視角」；理論見 [acceptance-evidence](../rules/acceptance-evidence.md)。

---

## product-type 偵測（code / docs 都通，不硬套）

arch-review 的 topology rendering **天生 product-agnostic** ——「結構拓樸 + 重複/重用」這個 invariant，code 與 docs 用同一套渲染邏輯（節點 + 邊 + 重複偵測），只是節點意義不同：

| 產品形態 | City Map 節點 | 重用枚舉 | 機械查證 |
|----------|--------------|---------|---------|
| **code** | code module（依賴方向） | symbol（enum/func/dataclass）via Pattern Radar + LSP | lsp-architect |
| **docs/rules/command** | command/rule 系統拓樸（受眾軸、carrier、命令依賴） | rule/command 重複重疊 via rg 跨檔 | rg（取代 lsp-architect） |

> docs 變更不空轉：City Map 自然變成「命令系統受眾拓樸」、Pattern Radar 變成「跨檔 rule 一致性/重複檢查」。這不是硬詮釋，是 topology invariant 的自然形態。

**`--ep` 渲染路徑**：從 EP 的 design / pseudo-code 渲染**提案結構拓樸**（還沒 code）；重用枚舉改為「提案 symbol vs 既有 code」的比對。

---

## 審查範圍

| 用法 | scope | 人判什麼 |
|------|-------|---------|
| `/arch-review` | 變更涉及的模組 + 鄰近 | 變更融入既有結構嗎、有無重造 |
| `/arch-review <module>` | 該模組整體 | 模組結構健全嗎、邊界清楚嗎 |
| `/arch-review --ep <EP>` | EP 的架構段落 | 提案結構撐得起 use case 嗎 |
| `/arch-review --focus <symbol>` | 圍繞某 symbol 的 sub-system | 這個 symbol 的生態（誰用、重複嗎） |

**Output 模式**：預設 console（ASCII city map）/ `--md`（Mermaid，寫檔 `ai-analysis/reports/arch-review-{scope}.md`）。渲染引擎：`/illustrate`。

**位置標示（可點擊）**：標定 symbol / 檔案位置一律用 **repo-root 相對路徑 + 行號**（如 `data/fetcher.py:15`），讓 VSCode terminal Cmd+Click 可直接跳轉 —— 人類 viewport 的判讀需要能鑽進 code 看嫌疑。純檔名（`fetcher.py`）terminal 解析不到、點不動。

---

## 執行模式選擇

偵測 effort level 和 max-agents（查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md)）。

**Phase 1（whole-picture 渲染）**：

| 條件 | 模式 | Agent 數量 |
|------|------|-----------|
| effort = ultracode/xhigh 且 max-agents > 1 | Workflow（枚舉 + 渲染平行 agents） | ≤ max-agents |
| effort < ultracode 或 max-agents = 1 | Main LLM（序列） | 0 |

**Phase 2（互動式調查）**：永遠 Main LLM。

印出確認：`[Arch Review] scope=X, Phase 1: effort=Y, workflow=Z, max=N`

---

## Phase 1: whole-picture viewport 概覽

> **目標**：讓人用 whole-picture 5 秒掌握「結構長怎樣、東西放哪、誰靠誰」，並看見「正在重造什麼既有東西」。四個元件。

### 元件 A：City Map（模組 + 依賴方向）

**人判**：分層清楚嗎、依賴方向對嗎（下層不 import 上層）、有無循環。

**渲染**（ASCII，console；Mermaid flowchart，`--md`）：模組節點 + 依賴箭頭（A ──uses──▶ B）。標變更涉及的節點。

```
🗺️  City Map — 6 modules                變更: data/, pipeline/

  cli/ ──uses──▶ pipeline/ ──uses──▶ data/ ──uses──▶ gateway/
                    │                   │
                    └──uses──▶ features/ ──uses──▶ indicators/

  ⚠️ data/ ──uses──▶ cli/  （依賴方向反向：下層 import 上層）
```

### 元件 B：Key Flows（use case 穿越系統）

**人判**：use case 的路徑合理嗎、跨太多層嗎、有無職責錯置。

**渲染**：挑 2-3 個高頻 use case，畫「request 怎麼穿越模組」（行為疊在結構上）。

```
🎬 Key Flow — UC「每日收盤備份」
  cli.run_daily_close() → pipeline.DailyClosePipeline.run()
    → data.bulk_upsert() → gateway.commit()
    → data.BackupPipeline → GitHub Releases
```

### 元件 C：Boundaries（模組裡 / 外）

**人判**：邊界清楚嗎、有無跨域直接存取內部（`_private`）、職責單一嗎。

**渲染**：每個變更模組的「做什麼 / 不做什麼」+ 公開 vs 內部分界。

```
🚧 Boundaries
  data/    做: 持久化、調整、備份 | 不做: 策略邏輯、UI
           公開: NautilusCatalog, bulk_upsert | 內部: _tsv_encode, _copy
```

### 元件 D：重用候選枚舉（whole-picture 燃料）

> **本命令的核心價值**：機器把所有既有 symbol 撈全 + 算相似度，餵人的 whole-picture 直覺。人說「那邊好像有可重用的」—— 機器給完整清單 + 嫌疑標記，讓直覺落地。

**枚舉策略**（Pattern Radar，按 ROI）：

| 類型 | 觸發 | 搜尋 | ROI |
|------|------|------|-----|
| Enum 重複 | 變更 / EP 含新 enum | LSP `workspaceSymbol` + rg member values | 最高 |
| Function 重複 | 變更 / EP 含新 func | LSP `workspaceSymbol` + `outgoingCalls` 比對 | 高 |
| Data Structure 重複 | 變更 / EP 含新 dataclass | rg field overlap（Jaccard） | 中 |

**信心度評分**（加權加總；只計對應類別標數值的因子，`—` 不適用）：

| 因子 | Enum | Function | Data Struct | Import |
|------|------|----------|-------------|--------|
| 名稱相似 | +3 | +5 | +3 | — |
| 值/簽名重疊 | +4 | +4 | +6 | — |
| Import 路徑已通 | +3 | — | +3 | +4 |
| 呼叫圖重疊 | — | +4 | — | — |
| 欄位重疊 >60%（Jaccard） | — | — | +5 | — |
| diff 重實作已有功能 | — | — | — | +6 |

**Jaccard 欄位重疊** = |欄位 A ∩ 欄位 B| / |欄位 A ∪ 欄位 B|（dataclass / TypedDict 欄位集合）；> 0.6 才計 +5。

**門檻**：HIGH ≥ 7 / MEDIUM 4-6 / LOW 1-3。只展示 HIGH + MEDIUM；LOW 收在 drill-down。

**人判**：嫌疑是不是真重用 —— 機器給候選，人的 whole-picture 裁決「該統一 / 那是巧合相似」。

```
📡 重用候選（whole-picture 燃料）
🔴 HIGH
  RC-001  Enum Dup   TradeAction (data/fetcher.py:15, NEW)
          ↔ TradeSide (core/types.py:23, 12 refs)
          Evidence: same members BUY/SELL, both StrEnum
          → 你判：該重用 TradeSide，還是 TradeAction 真的不同？
🟡 MEDIUM
  RC-002  Fn Dup     _parse_response (data/fetcher.py:88, NEW)
          ↔ _parse_raw (io/parser.py:45, 5 refs)
          Evidence: same (str)→dict, 70% logic overlap
```

### Phase 1 → Phase 2 過渡

```
──────────────────────────────────────────────────
💬 Phase 1 完成。你現在可以：

  city <module>      — 放大某模組的依賴細節
  flow <use-case>    — 畫另一個 use case 的 flow
  reuse <RC-XXX>     — 深入某重用嫌疑（含 LOW confidence）
  verify <symbol>    — 我鎖定嫌疑，用 lsp-architect 驗 refs / call chain
  boundary <module>  — 細看某模組邊界

  或用自然語言描述「這感覺在重造什麼」。
  完成後說 done 或 summary。
──────────────────────────────────────────────────
```

---

## Phase 2: 互動式調查

> **核心理念**：人提 whole-picture 線索（「那邊好像有可重用的」「這感覺重複」），LLM 做精確查證。

| Type | 人類說什麼 | LLM 調查 |
|------|------------|----------|
| 🔗 重用嫌疑 | 「這感覺跟那個重複」 | Pattern Radar 枚舉 + 信心度 + lsp-architect 驗 refs |
| 🗺️ 結構可疑 | 「這依賴怪怪的」 | LSP `incomingCalls`/`outgoingCalls` 追蹤 + import graph |
| 📐 邊界 | 「這不該在這模組」 | LSP `findReferences` 看跨域存取 + Read 邊界 |
| 💬 Free-form | 任意 | 自動分類或直接回答 |

### 機械分工（何時用哪個工具）

> **核心**：枚舉（撈全 + 相似）用 scan-project / Pattern Radar；驗證（特定 claim）用 lsp-architect。**人鎖定嫌疑後才上驗證**。

| 子任務 | 工具 | 角色 |
|--------|------|------|
| 撈全既有 symbol、找重用候選 | scan-project / Pattern Radar（枚舉） | **primary** —— 餵人的 whole-picture |
| 人鎖定「這 enum 跟那 enum 可能重疊」後驗證 | lsp-architect（`findReferences` / call chain） | **secondary** —— 確認嫌疑 |
| City Map / Flows 渲染 | /illustrate | 渲染引擎 |

> `lsp-architect` 是**反應式驗證**（驗證特定 claim → ✅/❌），不是 holistic 架構判讀 —— 判讀是人的 whole-picture 工作。名字易誤導，定位要清楚：它是本命令的查證 helper，不是 arch-review 本身。

### Final Review Summary

```
## Arch Review Summary（結構 viewport）

### Review Context
- Scope: <module> / EP / 變更
- 結構軸覆蓋: City Map | Flows | Boundaries | 重用枚舉

### 結構判定
| 項目 | 判定 | 說明 |
|------|------|------|
| 分層 / 依賴方向 | ✅/⚠️/❌ | ... |
| 邊界 | ... | ... |
| 重用（whole-picture） | N 嫌疑 | ... |

### Confirmed Reuse / Structure Issues
| ID | 類型 | 位置 | 判定 | Action |
|----|------|------|------|--------|

### Items for Discussion
| # | 嫌疑 | 確認問題 |

### Recommended Next Steps
1. 處理確認的重用 / 結構問題
2. 結構確認後 → /deliverable-review（交付）/ /code-review（正確性）→ /commit
```

---

## 邊界案例處理

| 案例 | 處理 |
|------|------|
| 單檔小變更（無結構影響） | 標「無結構影響，arch-review 不適用」→ 建議 `/code-review` |
| 純新增（無既有結構可比） | 元件 D 聚焦「與鄰近既有 symbol 的相似」 |
| LSP 不可用（subagent worktree） | 枚舉降級 rg-only；驗證標「未驗證」 |
| 大模組（50+ symbol） | City Map 聚焦變更 sub-system；重用枚舉分組（見 claude-writing 分組原則） |

---

## 與其他命令的關係

| 命令 | 軸 | 人 / 機 | 判什麼 |
|------|-----|---------|--------|
| **`/arch-review`** | 結構 | 人（layer 3） | 結構健全、重用（whole-picture） |
| **`/deliverable-review`** | 交付/意圖 | 人（layer 3） | demo 覆蓋、方向對嗎 |
| `/code-review` axis 3 | 結構 | 機（layer 1/2） | diff 結構**符合度**（變更融入既有？） |
| `lsp-architect` agent | 結構 | 機（tool） | call chain / type **驗證**（✅/❌） |

**分工邊界**：arch-review = 人 whole-picture **判讀**；code-review axis 3 = 機器 diff **符合度**；lsp-architect = 機器 **驗證**。三者不同層級，不重疊。

---

## 流程位置

```
post-EP：/deliverable-review --ep（方向）→ /arch-review --ep（結構：提案撐得起嗎）
post-build（看狀況呼叫，不硬定先後）：
  /arch-review（結構）        懷疑「build 期間結構漂移 / 在重造既有」時
  /deliverable-review（demo） 要確認「做成的是我要的嗎 / demo 覆蓋嗎」時
  → /code-review（正確性）→ /commit
```

> 結構問題越早越省 —— post-EP / build 早期跑，結構還能便宜改。
