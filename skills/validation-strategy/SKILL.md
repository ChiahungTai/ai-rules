---
name: validation-strategy
description: 驗證策略紀律 — e2e 優先於單元隔離、交易相關 replay >>> live、驗證放 scripts/、不重驗 package 已驗證的部分。用於 build/commit 驗證段決定測試類型與方式。觸發詞：e2e、replay、驗證策略、測試類型、live、不重驗 package、驗證放哪、交易驗證、回放。
---

# Validation Strategy — 驗證策略紀律

實戰驗證紀律：測**什麼類型**（e2e vs 單元）、**怎麼測**（replay vs live）、**放哪**（scripts/）、**不測什麼**（package 已驗證的）。與 [acceptance-evidence](../../rules/acceptance-evidence.md) L3-L5（證據階層）互補 — 本 skill 是「選擇紀律」，證據階層是「強度分級」。

## 四紀律

### ① e2e 優先 > 單元隔離

功能是給消費端用的，單元測試通過 ≠ 功能可用。**優先 e2e 驅動真實消費端流程**，單元補邊界邏輯。

判準：
- 涉及消費端完整流程（pipeline、API、CLI）→ e2e
- 純函數邏輯（計算、轉換）→ 單元
- 不確定 → e2e（寧可多整合）

### ② 交易相關 replay >>> live

交易驗證用 **replay（回放）** 優先，遠優於 live（連線）。

- replay：可重現、可控、不消耗資源、不影響真實帳戶
- live：不可控、消耗資源、風險（真實下單）

判準：
- 訊號 / 策略 / 回測邏輯 → replay
- 連線 / 下單基建 → live（但最小化，僅驗連通）

### ③ 驗證放 scripts/

驗證方法（demo、replay 腳本、對照工具）放 `scripts/`，不放 `tests/`（測試是 CI 自動化，scripts 是人為 / 半自動驗證）。

### ④ 不重驗 package 已驗證的部分

主要 package（NT、bokeh、panel）自己有測試，**別重測其內部**。只驗**你的整合**（public API 行為、你的呼叫方式），非 package 內部實作。

判準：
- 驗「NT 的 submit_order 在你的 context 怎麼行為」（你的整合）→ 驗
- 驗「NT submit_order 內部是否正確」（package 內部）→ 不驗（package 自己驗）

## RC-4 邊界：與 test-driven-development

- [test-driven-development](../test-driven-development/SKILL.md)：RED/GREEN **流程** + Test Classification（單元 / 整合 / 外部 API 分類）。
- 本 skill：測試類型**選擇紀律**（e2e vs 單元、replay vs live）。

**分工**：TDD 是「怎麼寫測試」（流程）；本 skill 是「測什麼類型 / 方式」（選擇）。層次不同，非重造 Test Classification。

## 與既有邊界

- [acceptance-evidence](../../rules/acceptance-evidence.md) L3-L5：證據**強度**階層（整合 / 可執行 / 對抗）。本 skill 是**選擇**紀律（引用階層，非重述）。
- [quality-constraints](../../rules/quality-constraints.md) 消費端驗證：在消費端上下文驗。本 skill 提供「怎麼驗」的類型選擇。

## 不適用

- TDD 流程（RED/GREEN）→ `test-driven-development`
- 測試反模式稽核 → `/audit-test`
- 證據強度分級 → `acceptance-evidence`
