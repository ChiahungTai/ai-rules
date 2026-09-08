---
harness-scope: neutral
---

# 設計思考紀律（深層思考＋架構三視角）

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## 核心原則：兩層思考（強制）

**所有決策必須經過兩層思考：第一性原理（向下分解，找到本質）＋第二層思考（向前追蹤，預見後果）。**

只做第一性原理分析，會產生「本質正確但後果災難」的決策<!-- bundle: skip-start -->（例：過度自動化在真實環境的連鎖後果）<!-- bundle: skip-end -->。

- 框架：①本質需求 → ②拆解元素 → ③原理重構 → ④驗證假設 → ⑤追蹤連鎖後果（**至少兩層，強制**）→ ⑥評估影響；不可接受 → 回①
<!-- bundle: skip-start -->
- 深入分析信號：影響多模組、修改公開 API／跨專案方法論、第一層後果不確定（「可能」「或許」）、同類決策曾出錯
<!-- bundle: skip-end -->
- 程式碼查證：直接讀源碼（套件源碼從 `.venv/lib/python*/site-packages/`），用具體路徑不憑記憶
- 輸出格式模板、思維框架圖、關鍵問題清單（0-7 共 8 問，含第 0 問「讀者是誰」強制前置）、查證細則與執行自檢清單見 deep-thinking skill（on-demand）

## 決策分級

| 決策類型 | 思考深度 | 判斷標準 |
|---------|---------|---------|
| **單向門**（不可逆） | 第一性原理＋多層後果追蹤 | 錯了無法逆轉：DB migration、公開 API 合約、跨專案方法論、生產架構 |
| **雙向門**（可逆） | 第一性原理＋第二層後果追蹤 | 錯了可以回退：內部重構、開發工具、配置調整 |

<!-- bundle: skip-start -->
**載體選擇由任務性質決定**：需判斷→LLM；確定性/機械→純程式（bash/plist/script）——LLM 只花在需要判斷的位子，不當萬用鐵錘。
<!-- bundle: skip-end -->

## 架構三視角（設計決策的結構檢視）

所有設計決策（spec/EP/implement/review）用 Clean Architecture＋DDD 視角檢視——**視角非模板**（注入思考，不強制分層、不過度工程）：

- **依賴規則（Clean Architecture 分層）**：domain ← use case ← adapter ← infra，依賴**向內**（內層不依賴外層）。設計時自問「新東西落哪層？依賴方向對嗎？有無循環？」
- **bounded context（DDD 邊界）**：每個 context 邊界清楚，**不跨域直接存取內部**（`_private`）。設計時自問「這該在哪個 context？有無跨域存取？」
- **use case 驅動**：先問**消費者要什麼行為**（use case），再設計結構（與 UC-Driven 呼應）。設計時自問「消費者是誰？結構撐得起 use case 嗎？」

<!-- bundle: skip-start -->
範例領域特定（mosaic：domain=策略訊號 / use case=回測下單 / adapter=NT·SJ·catalog / infra）。
<!-- bundle: skip-end -->
深入視角（三主線在 spec/illustrate/EP/implement 各自怎麼用）與結構機械見 arch-thinking skill（on-demand）。

## 觸發情境

架構變更、技術選型、設計決策、性能優化、重構建議、股票分析（→ 載入 `trading-analysis` skill）、AI 建議評估、文檔架構決策（instruction 檔結構重組、章節劃分）、資訊架構決策。
