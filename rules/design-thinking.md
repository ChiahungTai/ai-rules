---
harness-scope: neutral
---

# 設計思考紀律（深層思考＋架構三視角）

## 兩層思考（強制）

所有決策須第一性原理分解＋**至少兩層連鎖後果**追蹤；本質對但後果壞仍不可接受。依實際源碼/venv 查證附路徑，禁憑記憶；多模組、公開 API/跨專案方法論、後果不確定或同類曾出錯須深入。輸出模板、第 0 問、查證細則見 deep-thinking skill。

## 決策分級

單向門（不可逆）須多層追蹤；雙向門仍須第二層思考。判斷用 LLM，確定性機械工作用程式，不用 LLM 當萬用工具。

## 架構三視角

Clean Architecture＋DDD 三 lens：依賴向內（內層不依賴外層）、bounded context（禁跨域直接存取 _private）、use case 驅動（先問消費者行為）——不強制模板/過度分層。深入視角見 arch-thinking skill。

## 觸發情境

架構/技術選型/性能/重構/AI 建議/資訊架構決策；股票分析另載 trading-analysis skill。
