---
harness-scope: neutral
paths:
  - "**/*.py"
---

# AI Agent 雙通道輸出慣例

## 核心原則

**print 當索引，Logger 當資料庫；print = state transition, not computation trace**。不遵循視為 bug。AI 要據以決定下一步的最終結果/關鍵決策→print 摘要＋rg 指引；中間運算、狀態、debug 細節→Logger file，供後查。

預設單 log，以 level/namespace/prefix 分離；同進程交叉 timing 必單檔，只有不同消費者且不用對時才分檔。

## Namespace 原則（Logger name 強制 module-path）

Logger name 用 module-path（如 Logger(__name__)），禁 flat name，否則無法反查 source；動態識別可附在 module-path 後。框架 Strategy/Actor 已有 self.log namespace 就不自建；框架無檔名/行號時 namespace 是唯一反查鍵。

## 慣例摘要

print 用 status tag，禁 [INFO]（混淆 Logger level）；Logger message 以 action_name: 開頭，print 的 rg tag 在 file 必有對應。tag 全表、stdlib/框架並存、addHandler/lastResort、遷移/自檢見 llm-output-convention skill；framework init/suppress/quirk 由各專案定義。
