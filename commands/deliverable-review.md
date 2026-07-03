---
description: "天才工程師向老闆 demo 完成的交付——product-type-aware（code: demo-checklist / docs: behavior delta），--ep 審 planned deliverable。/deliverable-review [--ep <EP>] [scope]"
when_to_use: "Genius-engineer-shows-boss framing: render completed work for acceptance, force the AI to point at concrete demos (not just claim 'done'). Product-type-aware — code-mode renders a demo checklist (feature → runnable demo → run → confirm); docs/rules-mode renders behavior delta (what AI does differently) + affected UCs. --ep renders PLANNED deliverables (UC/scenario + planned demo targets) for pre-build direction confirmation. Surfaces cognitive-gap points. Priority: direction >> quality; does NOT audit structure (/illustrate 結構 viewport) or correctness (/code-review)."
usage: "/deliverable-review [--ep <EP路徑>] [target] [base]"
argument-hint: "--ep <EP> 審 planned deliverable / 無參數審 uncommitted / commit hash / branch"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent", "Workflow"]
---

# /deliverable-review — 天才工程師向老闆 demo 交付

> **核心理念**：**天才工程師向老闆呈現完成的功能** —— 不只說「做好了」，指**可跑的 demo / 可見的行為改變**給老闆確認。逼 LLM 拿出證據，打中「LLM 說做好但跟預期不符」的痛點。
>
> **優先級：方向 >> 品質**。老闆不逐行審 code（那是 `/code-review`）；老闆看「我要的功能，你 demo 給我看，覆蓋了嗎」。

**不做的事**：逐行正確性 → `/code-review`；結構 / 重用 → `/illustrate`（結構 viewport）；跑測試 / 覆蓋率 → `/build` + `/audit-test`。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則
- [mermaid](../skills/mermaid/SKILL.md) — MD 模式（`--md` 時）

按需讀取：
- [review-engine](../skills/review-engine/SKILL.md) — LSP 查證方法（Phase 2）+ 通用審查邏輯（嚴重度/自證/多層驗證）

受眾模型見 root [AGENTS.md](../AGENTS.md)（legacy `../CLAUDE.md`）「命令的受眾視角」；理論見 [acceptance-evidence](../rules/acceptance-evidence.md)。

---

## product-type 偵測（不硬套）

本命令渲染的「交付」依**產品形態**切換：

| 產品形態 | 觸發 | 渲染 |
|----------|------|------|
| **code** | `.py`/`.pyx`/`.ts` 等程式碼變更為主 | demo-checklist（feature → 可跑 demo → 你跑 → 確認） |
| **docs/rules/command** | `.md` 規則 / 命令 / instruction 檔（AGENTS.md / CLAUDE.md）變更為主 | behavior delta（AI 行為改變）+ 影響 UC |
| **混合** | code + docs 同改 | 兩 mode 都列 |

> 不硬套：docs 變更不硬詮釋成「可跑方法」，而是渲染「AI 讀了改的 rule 後會做什麼不同」。

---

## 審查範圍（source mode）

| 用法 | source | checkpoint | 渲染 |
|------|--------|-----------|------|
| `/deliverable-review --ep <EP>` | EP | post-EP | **planned deliverable**（打算做的 UC/scenario + 打算 demo 什麼）→ 方向確認 |
| `/deliverable-review` | code（uncommitted） | post-build | **demo-checklist**（code）/ **behavior delta**（docs）→ 完成確認 |
| `/deliverable-review abc1234` | code（commit） | post-build | 同上 |
| `/deliverable-review feat/xxx` | code（branch） | post-build | 同上 |

**Source 偵測**：`--ep` → EP mode；否則 commit hash / branch / 預設 uncommitted。`--ep` 與 target/base 互斥。

**Output 模式**：預設 console（ASCII）；`--md` 寫檔 `ai-analysis/reports/deliverable-review-{scope}.md`。

---

## 執行模式選擇

判定規則（effort/max-agents → 模式）見 [review-engine](../skills/review-engine/SKILL.md)；max-agents 上限查 [agent-workflow 並發表](../skills/agent-workflow/SKILL.md)。下表為交付渲染的平行化判定（借用相同條件）：

**Phase 1（交付渲染）**：

| 條件 | 模式 | Agent 數量 |
|------|------|-----------|
| effort = ultracode/xhigh 且 max-agents > 1 | Workflow（跨 feature demo-target 抽取平行） | ≤ max-agents |
| effort < ultracode 或 max-agents = 1 | Main LLM（序列） | 0 |

**Phase 2（互動式調查）**：永遠 Main LLM（互動需 conversation state）。

印出確認：`[Deliverable Review] source=EP|code, product=code|docs, Phase 1: effort=X, workflow=Y, max=N`

---

## Phase 1 渲染

### A. Orientation preamble（兩 mode 共用）

先給「這次改了什麼」全貌：code → Diff Map（per-file +N/-M + 依賴邊）；docs → 章節/檔案改動地圖。老闆 5 秒掌握 scope 再看 demo。

### B. 主渲染（依 mode + checkpoint）

#### code-mode · post-build：demo-checklist（核心）

每個 feature / UC 對到一個**可跑的 demo target**，你跑、看結果、勾確認。feature 沒 demo 到 = 沒證明完成。

**demo target 用 repo-root 相對路徑**（如 `scripts/demo_daily_close.py`），讓 VSCode terminal Cmd+Click 可直接點開看 / 跑 —— 老闆要能鑽進 demo 看程式碼。純檔名 terminal 解析不到、點不動。

```
🎯 Deliverable Demo Checklist — code-mode

Feature / UC         demo target（可跑）                       覆蓋    你跑 → 確認
──────────────────────────────────────────────────────────────────────────────────
每日收盤備份          scripts/demo_daily_close.py                full    [ ] 跑 → 4 release 保留？
FinMind gap 回填      scripts/demo_backfill.py                   full    [ ] 跑 → gap 補齊？
除權息調整            tests/test_apply_adjustment.py + scripts/demo_adj.py  partial [ ] 跑 → adj 欄位？（僅 happy）
成交量單位遷移        （無 demo）                               NONE    ⚠️ 沒 demo = 沒證明完成
```

**demo target 挑選規則**（優先序）：
1. `demo_*.py` / `scripts/demo_*.py` / `notebooks/*.ipynb`（既有 demo）
2. 既有 test（`test_<feature>.py`）—— 可跑驗證
3. 新功能入口 method（`ClassName.method()`）—— 標「需手動跑 / 無現成 demo」
4. 都沒有 → **NONE**（⚠️ 沒 demo = 沒證明完成，老闆該問「這功能怎麼沒 demo？」）

**覆蓋欄**：`full`（完整 path）/ `partial`（僅 happy path）/ `NONE`（無 demo）。

#### docs/rules-mode · post-build：behavior delta

「產品」是 AI 行為規則時，交付 = **AI 讀了改的 rule 後會做什麼不同**。

```
🎯 Behavior Delta — docs/rules-mode

Rule/Command 變更             AI 行為改變（讀了之後做什麼不同）           影響 UC/workflow
──────────────────────────────────────────────────────────────────────────────────────────
human-review → deliverable    審查渲染 demo-checklist 而非 4 lens         post-build 驗收流程
illustrate 結構 viewport       審查渲染結構拓樸 + 重用枚舉                 post-EP/build 結構審查
instruction-writing 種子深度       種子指向 method 不停在 class                instruction 檔導航品質
```

覆蓋確認：rule 宣稱的行為，**涵蓋它聲稱的所有 UC 嗎**？（例：新命令宣告 4 種 source mode，每種都有渲染路徑嗎？）

#### --ep mode（post-EP）：planned deliverable

還沒 code 可 demo。渲染**打算**做的 UC/scenario + **打算 demo 什麼**，讓你 build 前確認方向（cheap to change）。

```
🎯 Planned Deliverable — --ep（pre-build 方向確認）

UC / Feature           我打算做              打算 demo 什麼                  你確認
──────────────────────────────────────────────────────────────────────────────────
UC-1 每日備份           BackupPipeline        scripts/demo_daily_close.py    [ ] 方向對？
UC-2 FinMind 回填       run_backfill()        scripts/demo_backfill.py       [ ]
UC-3 除權息調整         apply_adjustment()    scripts/demo_adj.py            [ ]
```

### C. 認知誤差點（天才工程師主動揭露，消除方向偏差）

不只 demo，還**主動標「我可能哪裡會錯意」**：

| 類型 | 是什麼 |
|------|--------|
| **詮釋假設** | 「你說 X，我理解成 Y」 |
| **歧義選擇** | 「Z 兩種解讀，我選 A 因為…」 |
| **推斷行為** | 「spec 沒寫死，我推斷的」 |

每點附確認問題，讓你一句「對/不對」校正。

### D. 意圖情境完整性（該 demo 的 feature 想全了嗎）

不是測試覆蓋（`/audit-test`），是「**該 demo 給老闆看的 feature，有沒有漏**」。人用領域直覺補 AI 盲區：domain 關鍵 feature（除權息、跨日…）有 demo 嗎？只有 happy path 嗎？

### Phase 1 → Phase 2 過渡

展示完後可：`feature <name>`（深入某 feature demo）、`intent <Q>`（釐清認知誤差點）、`run <demo>`（現場跑）、`add-feature`（補該 demo 但沒列的）。或自然語言。`done`/`summary` 收尾。

---

## Phase 2：互動式調查

你提「這跟我要的不一樣」線索，LLM 精確查證（重跑 demo、對照 spec、影響追蹤）。調查類型：方向偏差 / 詮釋釐清 / demo 可疑 / 影響追蹤。

---

## Final Review Summary

```
## Deliverable Review Summary

### Review Context
- Source / checkpoint / product-type（code/docs）

### 交付判定
| Feature | demo target | 覆蓋 | 你確認 |
|---------|------------|------|--------|

### Confirmed Direction Gaps + 認知誤差點

### Recommended Next Steps
1. 校正方向偏差 / 補漏 demo
2. → /illustrate（結構 viewport）/ /code-review（正確性）→ /commit
```

---

## 邊界

| 案例 | 處理 |
|------|------|
| 純重構（無行為變更、無新 feature） | 標「無交付變更，不適用」→ 建議 `/illustrate`（結構 viewport） |
| Feature 無 demo（NONE） | **不掩蓋**——標 NONE + ⚠️，逼問「這功能怎麼驗？」（本命令核心價值） |
| demo target 跑失敗 | 標「跑失敗」+ 錯誤，交 `/code-review` |
| 混合 code+docs | 兩 mode 都列 |

---

## 與其他命令

| 命令 | 軸 | 老闆問 |
|------|-----|--------|
| **`/deliverable-review`** | 交付/意圖 | 「我要的功能，你 demo 給我看，覆蓋了嗎」 |
| **`/illustrate`** | 結構 viewport | 「結構撐得起嗎 / 在重造既有嗎」 |

兩者 product-type-aware（code/docs 都通）；`--ep` 各審 plan 的對應軸。

**呼叫時機**（你看狀況觸發）：

post-EP — 方向先於結構（plan 階段 cheap to change，錯方向白審結構）：
```
/deliverable-review --ep（方向：打算做對嗎）→ /illustrate --ep（結構：提案撐得起嗎）
```

post-build — 兩 viewport 看狀況呼叫，**不硬定先後**：
```
/illustrate         懷疑「build 期間結構漂移 / 在重造既有」時
/deliverable-review 要確認「做成的是我要的嗎 / demo 覆蓋嗎」時
→ /code-review → /commit
```

---

## 流程位置

```
/spec（純輔助·需求釐清，可選）→ /execution-plan（含 EP Review）
          ↓ post-EP
        /deliverable-review --ep（layer 3，planned）→ /illustrate --ep（layer 3，結構 viewport）
          ↓
        /build（含 Agent Review + /audit-test）
          ↓ post-build（看狀況呼叫，不硬定先後）
        /illustrate（layer 3，結構 viewport）/ /deliverable-review（layer 3，demo 交付）→ /code-review → /commit
```
