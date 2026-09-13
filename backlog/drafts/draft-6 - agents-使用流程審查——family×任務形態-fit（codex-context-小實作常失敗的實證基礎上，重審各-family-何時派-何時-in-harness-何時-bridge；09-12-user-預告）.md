---
id: DRAFT-6
title: >-
  agents 使用流程審查——family×任務形態 fit（codex context 小實作常失敗的實證基礎上，重審各 family 何時派/何時
  in-harness/何時 bridge；09-12 user 預告）
status: Draft
assignee: []
created_date: '2026-09-12 00:01'
labels: []
dependencies: []
---


09-12 實證素材（架構討論 session，UC 故事審查工單 job-mtyfmclu-fgeu75）：codex webgpt（chatgpt-web/high）read-only 審查工單中，**單一 pattern 查證（test -f／rg 單詞）8/8 全通、alternation 多 pattern 查證 3/3 全失真**（宣稱 rg 查無，機械複驗全推翻——contract 實存於 5 處）；bridge log 並列 rmcp transport worker fatal 連發（codex runtime 工具層降級佐證）。假說：codex shell 對 `|` 引號處理使 pattern 截斷，殘缺 pattern 查無被當「repo 查無」寫成 findings。含義：webgpt 形態的「機械查證」宣稱不可直接採信，查無型結論須獨立複驗；工單驗證命令宜避 alternation 或要求逐 pattern 分跑。

09-12 深夜續證（同一晚後續工單）：webgpt 另兩個失敗簽名——①`Selected model is at capacity`（turn-0 模型池容量拒絕，非帳號額度；序列化重試成功）②`turn token is invalid, expired, or revoked`（工具呼叫層 token 失效——任務誠實棄審零編造，換 muse 承接）。五類 user 裁定失敗態之外的新簽名累積中；webgpt 當晚整體呈「會話退化」趨勢（單 pattern 可用→capacity→token revoked），長晚連續派工建議中途換 family 或預先分攤。

09-13 續證（scope 分界研究弧 followup 工單 job-mtz2jpv5-2afomh）：webgpt 第四個新簽名——`ChatGPT Web supports at most 5 simultaneous browser turns; close or finish a browser tab before starting another`（bridge 瀏覽器分頁併發上限，turn.failed exit 1；重連 5/5 全敗）。與前晚簽名不同家系：非模型池/非 token，是 **bridge 瀏覽器 session 資源面**——前一段 webgpt turn 的分頁未釋放時續派即撞。處置：等分頁釋放後同 payload 重試（本次 90 秒後重試），連續撞上限考慮收斂 bridge 瀏覽器 session 或換 fresh session（放棄 --session-id 續寫）。含義：`--session-id` 連續 followup 形態對分頁生命週期敏感，排程弧（多段 webgpt 鏈）需在段間留釋放窗。

