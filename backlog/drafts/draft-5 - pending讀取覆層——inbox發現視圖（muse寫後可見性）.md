---
id: DRAFT-5
title: pending 讀取覆層——inbox 發現視圖（muse 寫後可見性）
status: Draft
assignee: []
created_date: '2026-09-09 16:30'
labels:
  - memory
  - governance
  - cross-harness
dependencies: []
---

# pending 讀取覆層設計定案（只做設計、不寫程式——user 09-09 拍板）

動機：inbox 模式最大 UX 缺口——已寫入、consolidation 前，其他 session 完全不知道它存在（write→invisible→23:40）。本設計把 consolidation 從 visibility boundary 降為 trust boundary。

## 三層語義（固定優先序 canonical > pending）

| 層 | 位置 | 職責 | 讀取語義 |
|---|---|---|---|
| canonical | `.agents/memory/*.md` | 已治理、可信、可長期引用 | 可以依賴 |
| pending overlay | `.agents/memory/_pending.md`（單檔） | 可發現、明確 provisional | 可找線索，用前驗證；**不得據此覆蓋 canonical contradiction**（表述為「有候選聲稱 X，canonical 仍為 Y」） |
| WAL | `.agents/memory-inbox/`（new/processing/done/rejected） | provenance／recovery／consolidation | agent 平時不必讀 |

一句話：Inbox is the WAL, Pending is the read overlay, Canonical is the trusted memory.

## 形態要點（Codex 提案＋本地驗證）

- **單一 `_pending.md`**，不一條一檔（muse 48-file 開場壓力；`_` 前綴本就在 reserved governance namespace）。
- **generated discovery index，不 dump raw**：每候選＝operation／proposed path／timestamp／content 前 N 字／inbox 檔名／CAS state；edit 類標 `⚠ Pending correction to canonical`（informational weight 高於 add 類的 `Pending candidate`）。
- **MEMORY.md 只帶固定 pointer 行**（例：`Pending candidate memory: _pending.md`），不把候選混進正式 ranked index——否則 pending 會被誤認 canonical。
- **硬規則免費成立（已驗實作）**：generator 遍歷跳過 `_` 前綴（`generate_index.py`  entry 迴圈）→ pending 永不進正式索引；`is_pool_entry` 同樣排除 → pending refresh 不觸發 CC hook 事件（無回授 loop）。
- **MEMORY.md pointer 行需改 generator 樣板**（`render_b_form`＋routing 段）——實作時動。
- **異常偵測必須豁免 `_pending.md`**：否則 refresh 會被 T3-4 的 porcelain-vs-receipt 檢查當 fail-open 直寫誤報（Codex 原提案未提，本地驗證補）。
- **池 git 處置待定**：`_pending.md` 住池內會進池 git 歷史（含 speculative 內容；local-only 但仍是 provisional 入歷史）——選項 (a) 池級 gitignore (b) 接受。實作前拍板。
- **hook 保持極簡**：hook 只寫 inbox JSON；pending index 由外部 refresh（手動／夜波；SessionStart 接線另議——新 hook 面，AIR-56 區）。

## 未決（實作前拍板）

1. 觸發點（手動＋夜波 vs SessionStart 接線）。2. 池 git 處置 (a)/(b)。3. excerpt 長度 N 與單檔尺寸上限（context tax）。

## 正式 code review 檢查清單（reviewer 09-09 預列，實作後逐項）

1. Authority leakage：routing／prompt／generator 是否可能讓 agent 誤認 pending 為 canonical。2. Lifecycle convergence：inbox `done/rejected` 後 pending 必消失或更新（禁 ghost pending）。3. Crash semantics：refresh／consolidation crash 或交錯時 view 可 stale、禁 falsely canonical。4. CAS visibility：base 已失效的 pending edit 顯示 correction 還是直接標 conflict/stale。5. Canonical contradiction：同一 target 多 pending edits 的順序與展示語義。6. Git/anomaly 互作：`_pending.md` refresh 必須列為 T4-1 合法自產物（reviewer-confirmed requirement；現行三 allow 訊號未含，實作時補）。7. Context tax：pointer 外，`_pending.md` 被自然 recall 打開時的 excerpt 數量與尺寸 hard bound。

## Scope 邊界（reviewer 確認 09-09）

AIR-54（migration/inbox/consolidation/guardrail）與 pending（read-model/projection contract，設計稿）分開審；pending 不得拿來補 AIR-54 現有缺口（如 P5）。`_pending.md`／pointer 現只存在於本 draft，無實作。
