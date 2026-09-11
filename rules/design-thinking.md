---
harness-scope: neutral
---

# 設計思考紀律（深層思考＋架構三視角）

## 核心原則：兩層思考（強制）

所有決策須第一性原理向下分解＋第二層思考向前追蹤；本質對但後果壞仍不可接受。

①本質需求→②拆元素→③原理重構→④查證假設→⑤至少兩層連鎖後果→⑥評估；不可接受回①。依實際源碼/venv 查證並附路徑，禁憑記憶。多模組、公開 API/跨專案方法論、後果不確定或同類曾出錯須深入分析。

輸出模板、第 0 問「讀者是誰」、查證/自檢見 deep-thinking skill。

## 決策分級

單向門（DB migration、公開 API、跨專案方法論、生產架構）不可逆，須多層追蹤；雙向門（內部重構/工具/配置）仍須第二層思考。判斷用 LLM，確定性機械工作用程式，不用 LLM 當萬用工具。

## 架構三視角（設計決策的結構檢視）

spec/EP/implement/review 用 Clean Architecture＋DDD 視角，不強制模板/過度分層：

- 依賴向內：domain ← use case ← adapter ← infra，**內層不依賴外層**；問落層、方向/循環。
- bounded context：邊界清楚，禁跨域直接存取 _private；問責任歸屬。
- use case 驅動：先問消費者行為，再驗結構支撐。

深入視角/機械結構查證見 arch-thinking skill。

## 觸發情境

架構/技術選型/性能/重構/AI 建議/文件結構/資訊架構決策；股票分析另載 trading-analysis skill。
