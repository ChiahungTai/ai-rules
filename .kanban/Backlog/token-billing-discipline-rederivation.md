# deferred：token 計費紀律重推導（F1-F10 審查 findings）

**2026-08-18 計費定案（用戶裁決 + 證據三角）**：現行 Legacy V1 的計量本質 ≈ **token-value**（dashboard 顯示 Token usage；Claude Max 同構先例——長對話每則訊息全 context 重處理；「prompts」是 UI 話術，1 prompt ≈ 15-20 invocations 估算）+ **premium model 倍率**，細節**不可精算**。策略 = 雙軸省 token：**省 requests**（批次化/組合命令/git 錨定——已落地）+ **省 context**（Read 紀律——已落地）。本卡剩餘項目釘在**計費明朗化或 token-billed model 成為主力時**重推導；F4 已拆出獨立卡（bundle-layered-diet）。

**審查來源**：2026-08-18 跨 session 審查報告（成本模型假設 c=0.1 cache-read / k=4 output，c∈[0.05,0.2] 結論穩健）；五天基線 + db.sqlite 查詢方法見 memory `reference_zcode-telemetry-db`。

**雙計費不變量（落地時保留不動）**：批次化（F1）、Read 紀律（F2）、metadata-sync git 錨定（F8）、批次 Edit、組合驗證命令——兩種計費下皆正節省。

**落地時重推導清單（token-only 槓桿）**：
- **F3 🔴 compact 與 context 水位——已重框（2026-08-18 用戶裁決）**：compact 時機是**使用者判斷**，不做自動水位觸發紀律；重點在**接續品質**——善用 memory 載體（STATE.md、memory 檔、EP 段落自足、handoff context、kanban 卡）讓 session 隨時可結束可接續。token 落地時的推導方向：context 成本的因應是「可接續 → 隨時可關 session 換新」，而非「撐長 session + 自動壓縮」。（原始審查數據保留：150K 水位超額 ≈ 622M input-equiv ≈ 18% 上限估；/compact 節奏死信 224/7 印證 prose 無效）
- **F4 🟡 135KB bundle 減肥**：~38.2M equiv/視窗（11%）；方向是「分層非刪除」（理論重 always-on 內容移 on-demand）
- **F5 🟡 委派經濟學**：委派淨益判據 = 探索 debris×0.1×主 session 剩餘 requests vs subagent 成本（29.6K 全價地板）；consistency per-doc agent 池（969 calls 歸因）是池化候選
- **F7 🟡 無條件 Read limit 收回論證**：token 計費下「碎片化反增 call」論證弱化一個量級——落地時重推論證文字（規則本體現不動，per-call 下現行論證有效）
- **F9 🔴 cache 保溫**：5min TTL 逾期重灌 25.7M 全價（非快取輸入的 42%）；槓桿——長等待前發完獨立 request / 逾期後大 context 先 compact——全新且無規則覆蓋的領域
- **F10 🟢 output/reasoning 軸**：新 model 有 thinking tokens 且 ×3-5 定價則放大至 ~12% 佔比

**參數依賴（落地時先實測再定參）**：實際 cache-read 定價 c、output 定價 k、thinking token 計費——F3 水位值與 F5 委派判據係數依賴這些。

**設計原則（報告結論，已採納）**：一次翻轉、不留條件式文案（ai-rules 不做向後相容既有裁決）；指標從「call 數」改為「request×context 乘積」；沒有觸發機制的規則也是噪音（寫作治理第 3 條的成本維度鏡像）。

**來源**：2026-08-18 用戶指示（數週後導入新 LLM model，token 計量）+ 跨 session 審查報告 findings F1-F10（judge-review 裁決：不變量 4 項維持、token-only 6 項延後釘卡、F7 論證重推導延後）
