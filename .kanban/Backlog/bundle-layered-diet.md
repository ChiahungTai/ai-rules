# deferred：135KB 全域 bundle 分層減肥（F4 拆卡）

**問題**：部署 bundle（`~/.zcode/AGENTS.md` 等）已達 135KB ≈ 50K tokens——每個 session 地板 52-79K tokens、每個 subagent spawn ~29K，且**每個 request 以 cache-read 折價重送**（token-value 計量下是持續稅）。Claude Max 同構先例明言「長對話每則訊息全 context 重新處理」——bundle 是最固定、最無差異化的那塊。

**方向（分層非刪除）**：理論重的 always-on 內容移 on-demand——候選：`acceptance-evidence.md` 中段理論（A/B 軸細節）、`deep-thinking.md` 長論證、各 rule 的重複範例。機制已存在：skills on-demand 載入、markdown link 不 transclude。寫作治理的「長度預算」從風格建議變有價預算。

**品質護欄**：刪規則省 token 可能付出行為品質（報告 F4 警告）——每項搬移須驗證「on-demand 連結存在且可被觸發」，不做無痕刪除。

**觸發**：token-billed model 成為主力、或現行方案額度轉趨嚴格時啟動（現行 Legacy V1 寬鬆，不急）。屬大型跨檔編輯工程，啟動時走 EP。

**來源**：跨 session 審查 F4 + 2026-08-18 計費定案（token-value + 用戶指示「token 計費是趨勢、注意不要浪費」）
