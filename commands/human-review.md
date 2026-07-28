---
description: "以人類 viewport 審 AI 產出的放大鏡(source + test 批判性查證)。/human-review <dir|files>"
when_to_use: "When the user has read some code and suspects AI added unnecessary code or wrote pointless tests, and wants a human-viewport critique (problem + recommendation + diagram). User points at a dir/files with suspicion. NOT for: change-diff review (use /code-review), full-module baseline (use /codebase-sweep), test anti-pattern scan (use /audit-test)."
usage: "/human-review <dir|files>"
argument-hint: "/human-review common/rate_limiter — dir | /human-review foo.py bar.py — files"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "LSP"]
---

# /human-review — 以人類 viewport 審 AI 產出的放大鏡

> **genesis**：前次設計死因是「分類軸思維 + token 牆 + 重造機械」（過度投資 AI 機械、欠投資人類產出）。本次定位翻轉：**source 側的 audit-test** — 借 audit-test 成熟範式（偵測器 stance + 問題/建議格式）+ 機械全委外既有 skill + 用戶判準封裝成 viewport。

## 定位（三向 + 分工）

| 命令 | 定位 | 觸發 |
|------|------|------|
| `/codebase-sweep` | 盤點既有模組穩固度（baseline，假設 code 該存在） | onboarding / 週期 |
| `/code-review` | 審 diff 正確性（change-driven） | 改完 code |
| `/audit-test` | 測試反模式機械稽核（表格，廣而深） | build / commit gate |
| **`/human-review`** | **放大鏡**：用戶懷疑 → 判準查證 → 問題+建議+圖 | 讀過 code、懷疑 AI 亂加 |

**與 sweep 的關鍵區隔**：sweep 問「這模組穩不穩固」（守護既有）；human-review 問「**這些 code/test 是不是 AI 不必要地加的**」（質疑存在）。兩者正交。

## 委託 Skills

- [review-engine](../skills/review-engine/SKILL.md) — 嚴重度 / 信心 / 審查者自證 / LSP 查證（共用真相源）
- [human-review](../skills/human-review/SKILL.md) — **本命令判準 4/5 + 編排 audit-test + 誠信 stance**（domain 層，本命令獨有價值沉此）
- [arch-thinking](../skills/arch-thinking/SKILL.md) — core/leaf tiering + LSP 查證（按需）
- [crg-query](../skills/crg-query/SKILL.md) — CRG 結構事實（若裝了）
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

## 核心目標

**用戶讀過 code、懷疑某 dir/files 有 AI 亂加的 code 或亂寫的測試 → 用 6 條判準 + 機械查證深挖 → 產「問題 + 建議 + 圖 + 查證誠信」報告供人判讀。**

不是機械列 finding（那是 audit-test），是**批判性追查** — 查證、深化、撤銷 false positive，展示判斷過程。

## 審查範圍

| 用法 | source | 場景 |
|------|--------|------|
| `/human-review <dir>` | 目錄 source + 對應 test | 懷疑整個模組 |
| `/human-review <file...>` | 指定檔 + 對應 test | 懷疑特定檔 |

**預設 source + test 同審**（AI 亂加 code 與亂寫測試是同一類問題，同命令處理）；**user 可明確排除**（prompt 註明只審 source / 只審 test，或 dir 無對應 test 時自動只審 source）。test 側聚焦判準 2（production wrapper 重複），反模式深度（mock / 覆蓋對稱）編排 [audit-test](audit-test.md)。

## 執行模式

**直接執行為主**（單 session，read-only 偵測器，仿 [audit-test](audit-test.md) stance）：scope 是 dir/files（通常 ≤ 10 檔），fit 一個 session。讀 source + test → 6 判準查證 → 產報告。

scope 極大（50+ 檔）才用 Agent（free-text 產出，主 session 組報告；**禁 complex nested schema**，教訓見 [codebase-sweep](codebase-sweep.md) indicators/ rollout）。

## 6 條判準 × 機械查證

> 判準 = 用戶 viewport（人類判讀），機械查證 = 手段。完整定義沉 [human-review skill](../skills/human-review/SKILL.md)；此表為 command 摘要。

| # | 判準（用戶 viewport） | 機械查證 | 既有引用（不重寫） |
|---|---|---|---|
| 1 | **YAGNI 嚴格**（沒用就刪） | LSP `findReferences` + rg 確認零消費者；filter trap 區分（YAGNI 往刪 / 驗證不能刪） | [collaboration-constraints](../rules/collaboration-constraints.md) YAGNI check + [acceptance-evidence](../rules/acceptance-evidence.md) filter trap |
| 2 | **測試要有實際價值** | 隱含覆蓋查證（行為別處已測 = 冗餘）；不為覆蓋率寫 | 委外 [audit-test](audit-test.md) 角度 6 + **補靜態隱含覆蓋**（audit-test 補充段） |
| 3 | **嚴格不放水** | 機械查證不靠善意；對抗性自查（挑戰自己判斷） | [collaboration-constraints](../rules/collaboration-constraints.md) 反 Sycophancy + [review-engine](../skills/review-engine/SKILL.md) 審查者自證 |
| 4 | **質疑命名/設計** | 命名碰撞（LSP）/ domain 一致 / phantom API（rg + LSP 確認符號存在） | **本 skill 自帶**（分散承載 → 封裝即價值） |
| 5 | **scope 釐清** | mixed-tree 分組（`git status`）+ 結論 framing 對應 scope | **本 skill 自帶**（完全無既有承載） |
| 6 | **大改動管控** | 風險分級 → EP / 直接改 分流 | [ai-development-guide](../ai-development-guide.md) 風險 + 規模分級 |

## 輸出格式（問題 + 建議 + 圖 + 查證誠信）

> 倒金字塔（結論先行）+ 每個 finding「問題 + 建議 + 圖」一組 + 查證誠信段。標竿實作見 project 端 `ai-analysis/human-review/<scope>.md`。

```
# Human-Review — <scope>

> ✅ 結論：<一句話，行動導向 — 健康或有 N 個債，建議改 X>

## Source 問題 + 建議
### <F1> 🟡 <問題標題>
**問題**：<描述，含 file:line>
**建議：<明確推薦>** — <理由>
<ASCII 圖：現況 vs 建議>

## Test 問題 + 建議
### <T1> <❌撤銷|✅保留|💡可改> <標題>
... （同上格式）

## 查證誠信（過程記錄）
| Finding | 原判斷 | 查證 | 最終（翻案/深化/確認） |

## 附錄（折疊，僅參考）
<details>方法論限制 + 歷史回顧（若有）</details>
```

**關鍵（避開前次失敗陷阱）**：
- **推薦先行**（非選項清單）：每個 finding 給「建議 X，因為 Y」，不給「A or B 你選」— 這是「省 prompt」初衷（前次設計為過程導向，把判斷推回人類）
- **查證誠信段必含**：記錄翻案（撤銷）/ 深化 / 確認，展示「批判性追查」— human-review 對 audit-test 的差異化（audit-test 機械列，不追查過程）
- **撤銷的 finding 保留**（標 ❌）：查證推翻不刪除，示範自我否證建立信任
- **ASCII 圖**（problem → fix 對照）：每個 finding 一張；md 模式可升 Mermaid
- **LSP stale 警告**：判死碼前 LSP `findReferences` 回可疑少（只 intra-file）必須 rg 補（[lsp-navigation](../rules/lsp-navigation.md) 條件式 fallback）— dogfood 實證：throttle() LSP 只回定義點，rg 才發現 production 在用

## 執行流程

| 步驟 | 動作 |
|------|------|
| 1 | 解析 scope（dir/files）+ `git status`（mixed-tree 分組，判準 5） |
| 2 | 讀 source + 對應 test（完整，非截取） |
| 3 | 6 判準查證（LSP `findReferences` + rg；判準 4/5 詳見 skill） |
| 4 | test 側：判準 2（隱含覆蓋查證）+ 編排 audit-test 深度（反模式 / mock） |
| 5 | 查證誠信：每個 finding 標信心；inferred 必查證（防 false positive）；翻案 / 深化記錄 |
| 6 | 產報告（問題 + 建議 + 圖 + 查證誠信），倒金字塔 |

## 與其他命令協作

| 場景 | 導到 |
|------|------|
| 測試反模式深掃（mock / 覆蓋對稱 / 幽靈斷言） | `/audit-test` |
| 變更 diff 正確性 | `/code-review` |
| 模組 baseline 盤點 | `/codebase-sweep` |
| 評估 AI review 建議 | `/judge-review` |

## 流程位置

**user-driven 主動偵查入口**（非 canonical chain）。用戶讀 code → 懷疑 → `/human-review` 放大鏡。非 build / commit 流程節點（那是 code-review / audit-test）。

## 語音通知

遵循 [voice-notification](../skills/voice-notification/SKILL.md)：
- 開始（第一個動作前）：`touch /tmp/.claude-voice-pending` + `say -v Meijia -r 180 "開始 human-review"`
- 完成（輸出後）：`rm -f /tmp/.claude-voice-pending` + say 完成樣板（隨機稱謂，填「human-review 完成」）

## 執行約束 + 誠信約束

- **read-only**（偵測器，非判官）：只產 finding + 建議，不自動改 code（[audit-test](audit-test.md) stance）
- **推薦先行**：不給選項清單，給明確推薦 + 理由（省 prompt 初衷）
- **查證必須**：inferred finding 必查證（LSP / rg）才報；未查標 `inferred ⚠️`（防 false positive — dogfood T1 教訓：未查就報「符號不存在」，rg 推翻）
- **撤銷透明**：查證推翻的 finding 標 ❌ 保留，不刪（示範誠信）
- **LSP stale 警告**：判死碼 LSP 回可疑少 → rg 補（[lsp-navigation](../rules/lsp-navigation.md)）
- **不重造機械**：死碼 → arch-thinking / LSP；測試反模式 → audit-test；severity / confidence → review-engine
- **預設 source + test 同審**（AI 亂寫測試是同等痛點）；user 可明確排除（只審 source / 只審 test）— 不強制，避免稀釋放大鏡焦點
