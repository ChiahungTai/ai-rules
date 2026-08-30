---
harness-scope: neutral
paths:
  - "**/*.py"
---

# AI Agent 雙通道輸出慣例

> **scope**：跨專案通用日誌原則。Framework-specific 細節（log format、init 入口、suppress policy、framework quirk）在各專案文檔，本檔不重述，避免雙處真理論漂移。

---

## 核心原則

**print 當索引，Logger 當資料庫。** AI Agent 透過 print 理解執行結果，透過 rg 按需查詢 Logger 檔案取得詳細資訊。

**print = state transition, not computation trace。** 如果 output 不遵循此協議，視為 bug。

| 通道 | 消費者 | 職責 | 何時使用 |
|------|--------|------|----------|
| `print()` | AI Agent (stdout) | 精簡摘要 + rg 搜尋指引 | state transition：流程的最終結果或關鍵決策點 |
| Logger → file | AI Agent (rg 按需) | 可搜尋的詳細資訊 | 中間步驟、狀態變化、除錯資訊 |

決策規則：AI 需要此資訊決定下一步 → print；AI 日後可能需要查閱 → logger。

**單檔 vs 分檔**：預設單一 log 檔 + 三維分離（level / namespace / prefix），不分檔。同進程需交叉 timing 對齊 → 單檔；不同消費者且不需交叉 timing → 才分檔。

---

## Namespace 原則（Logger name 強制 module-path）

Logger name 是 log → 源碼的反查鍵，**必須是 module-path**（`Logger(__name__)` 最常見，自動帶；需 runtime-varying 識別用 `Logger(f"{__name__}({adapter})")` 保留 module-path + 動態段），不可 flat name（`Logger("MyService")`——無法反查）。框架 Strategy/Actor 基類自帶 namespace（如 `self.log`）→ 不自建。框架若不輸出檔名/行號，namespace 是**唯一**反查鍵。

---

## 慣例摘要

- **print**：status tag＋精簡摘要；**不使用 `[INFO]`**（與 Logger level 混淆——tag 全表見 skill）
- **Logger**：message 以 `action_name: ` 開頭（rg 可精準搜）；print 的 rg tag 須在 Logger 有對應行（閉環）

> tag 全表、print/Logger 慣例細則、stdlib `logging` 與框架 Logger 並存、遷移注意、自檢清單——見 llm-output-convention skill（on-demand；觸發詞：print tag、`[LOG]`、Logger prefix、namespace、addHandler、lastResort）。
