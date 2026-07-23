---
description: "Folder baseline audit — 系統性 per-folder 審查既有 code（非 change-driven），產持久化狀態（verdict/guards/gaps/drift）到 ai-analysis/human-review/。折入 coverage + CRG/snapshot ripple + 跨 folder invariant。目的：核心審一次（well-tested + guarded）使後續 AI coding 碰非核心；--stale 抓 drift。與 /code-review（change-driven pre-merge）正交。"
usage: "/human-review <folder> [--status] [--stale]"
argument-hint: "<folder> | --status | --stale"
---

# /human-review — Folder baseline audit

> **Purpose**：系統性 per-folder 審查**既有 code**（非 change-driven），產持久化狀態。目標：foundations 審一次（核心 well-tested + guarded）→ 後續 AI coding 改動是非核心（leaf）；`--stale` 抓審完後又被改的 folder。
>
> **vs `/code-review`**：code-review 是 change-driven（diff、合併前）；human-review 是 baseline-sweep（folder、週期）。兩者共用 facts（CRG/snapshot/coverage）+ [crg-query](../skills/crg-query/SKILL.md) 紀律。

## When to use
- 首次審某 folder 的骨幹（核心不變式、coverage、結構債）
- 週期 re-review（`--stale` 標自 last-reviewed 後被改的 folder）
- **不用於** change review（用 `/code-review`）

## Flow（5 步，per folder）

### 1. Profile
- 職責（folder AGENTS.md）
- deps（`.dependency-snapshot.json` 的 imported_by/internal_deps，或 [scan-project](../skills/scan-project/SKILL.md) dep_graph；CRG `get_architecture_overview` 若裝了）
- N 檔 + 平均 coverage（`pytest --cov`）

### 2. 2D Tier（ripple × test）— smart effort 分配
- **ripple**（core/leaf）：snapshot module fan-out + CRG `get_hub_nodes`（node 級；**snapshot 顆粒度 folder-dependent**——snapshot 粗時用 CRG node 級，見 [crg-query](../skills/crg-query/SKILL.md)）
- **test 軸 = invariant guard 狀態**（guarded / partial / unguarded）——**非 raw coverage %**。coverage % 只是 hint（低→可能 gap，但 coverage 綠 ≠ invariant 守，L2 trap）；verdict 看 invariant 有沒有被測 + assertion 強度。標 guarded 須指認**測該 invariant 的具體 test + 斷言**（見 step 5 🔴 guarded 自審），見 [acceptance-evidence](../rules/acceptance-evidence.md) L2
- matrix → 投入：core×none/weak 深讀 + 補/強化測試；core×strong 驗 assertion；leaf skim

### 3. 跨 folder 不變式勾稽
- 本 folder 是否碰跨 folder 不變式？（查 `ai-analysis/human-review/_invariants/`）
- 是 → 驗 golden set 覆蓋 + assertion 強度；用 **CRG `query_graph callers_of`** 找 invariant-bearing function 的**所有消費者**（消費者可能在 folder 外——CRG 浮現、snapshot/literal-grep 漏）
- 發現新不變式 → 加進 `_invariants/` + 提 guard 測試

### 4. Smart scan（依 2D matrix）
- core×weak/none：深讀 + 補/強化測試
- core×strong：讀 assertion 強度，驗
- leaf：skim docstring + has-test（**每檔至少掃過一次**——抓 stale core/leaf label）

### 5. Verdict → 寫 `<folder>/report.md`
- risk：🟢/🟡/🟥
- guarded：機械保護項——每項**必附 test 名 + 該 test 的具體斷言原文**（如「`test_all_features_override_column_keys`：每個已註冊 Feature 的 `column_keys.__func__` ≠ `FeatureBase` 的」）。只寫「guarded by test X」而無斷言 = guard 冒充風險（halo effect，見 🔴 guarded 自審）
- gaps：需測試/guard 處
- 新 guard 提案：不變式無 guard → 寫 guard 測試（如 shift anti-leakage guard 模式：literal + default + explicit-disable 三層）
- 🔴 **guarded 自審（防 guard 冒充）**：宣稱「X invariant guarded by 測試 Y」時，逐項問——**Y 測的 invariant == X 嗎？**（真實案例：column_keys audit 測「已註冊 Feature 有 column_keys」≠「每個 Feature 都被註冊」= 兩個不同 invariant；conflation 會把 real cov gap 掩飾成「已守」→ 虛假信心）。不確定 → 標 gap + peek，**不宣稱 guarded**。
- 更新 STATUS.md（狀態 + last-reviewed-sha）

## CRG 整合（conditional — 見 crg-query）
- ripple 軸：CRG `get_hub_nodes`（node 級）—— snapshot（folder/module）足夠時用它，粗時用 CRG
- invariant 消費者：CRG `query_graph callers_of` —— 浮現 folder 外消費者（shift `forward_fill` caller 模式）
- impact/drift：CRG `get_impact_radius` 供 `--stale`
- **assume CRG 裝了**；缺席 → `[WARN]` + fallback snapshot/LSP（crg-query 的 assume+warn-if-absent，不靜默降級）

## Flags
- `<folder>`（預設）：跑 5 步，寫 report
- `--status`：印 STATUS.md 全覽（各 folder 狀態/risk/last-reviewed + invariant 清單）
- `--stale`：每個 reviewed folder，`git diff <last-reviewed-sha>..HEAD -- <folder>/`（或 CRG `detect-changes`）→ 標 stale（審完後被改 → re-review）

## Output structure（project-side，非 ai-rules）
```
ai-analysis/human-review/
├── STATUS.md              # 索引：folder 狀態/risk/last-reviewed-sha + invariant 清單
├── _invariants/           # 跨 folder 不變式（golden set + guard 狀態）
└── <folder>/report.md     # per-folder mini-report
```
> Command 是 generic（ai-rules）；state + invariants 是 **project content**（不准 hardcode 進 command）。

## Reference
- [crg-query](../skills/crg-query/SKILL.md) — graph facts 紀律（LSP-vs-CRG、warn-if-absent、anti-over-reliance）
- [scan-project](../skills/scan-project/SKILL.md) — dep_graph（snapshot 源）
- [arch-thinking](../skills/arch-thinking/SKILL.md) — 結構 viewport（core/leaf、ripple、補償邏輯）
- [acceptance-evidence](../rules/acceptance-evidence.md) — coverage ≠ assertion 強度（L2）；Claim→Evidence→Trust
