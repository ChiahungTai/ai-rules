# Flow Feedback — 2026-07-31 — illustrate drift detection 不消費語意 context

## 摩擦（發現來源）
> dogfood 剛強化的 /illustrate drift detection 時發現：drift overlay surface 死碼 false-positive 訊號，但 spec 沒要求讀 AGENTS.md 設計意圖標註。user 確認原話：「3」（選擇「小改 spec + 寫 flow-feedback」兩者都做）。

（非典型 session 摩擦——是 dogfood 揭露的設計缺口，非「不順」；user 用 /human-review 推出 dogfood「是不是也應該要好好利用 /illustrate 跟相關的 skill」，dogfood 才挖出此缺口。）

## session 摘要
強化 /illustrate 的 SA/SD artifact menu + drift detection（ep-illustrate-sasd-drift，4 段 docs mode build 完成 + Agent Review）。build 完成後在 mosaic_alpha dogfood（`717f4e0a` facade 激活 refactor），drift overlay 正確 surface「`MarketIntelService` 零外層消費者」訊號，但揭露 drift 不消費 AGENTS.md 設計意圖的缺口。

## type-1 建議（時機）
- **build 完成後該自動 dogfood 被改動的命令/skill** → `build` 階段 6 / `autonomous-execution`
  - 例子：本 session build 完成報告我只「建議」dogfood（layer 旗標軟提示）卻沒做，直到 user 用 `/human-review` 推（「是不是也該好好利用 /illustrate」）才做，dogfood 才挖出 drift 的 AGENTS.md 缺口
  - counter-factual：若 build 階段 6 對「改到 illustrate / code-review / arch-thinking 等會被自己或 review 鏈消費的命令/skill」有「dogfood 自己改動」的觸發步驟，就會在 build 收尾自動驗收（而非等 user human-review 推），早一步挖出缺口

## type-2 建議（設計）—— 強制
- **drift detection（與其他 SA/SD artifact）只比對結構 diff，不消費 AGENTS.md 語意設計意圖** → `illustrate-artifact-menu.md` drift overlay spec（已小改）/ 供 `/flow-review` 討論是否通用化到 `arch-thinking` skill
  - 例子：mosaic_alpha `ranking.py` 改走 `IntelService` 後，drift surface「`MarketIntelService` 14 方法零消費者 → 死碼 candidate」；但 `services/AGENTS.md` 明文「禁誤判、YAGNI facade 起點、14 方法非死碼」（前人曾誤撤 `DataPortal`/`LabelService` 零消費者 facade）。drift 不讀此標註 → 死碼 false-positive（no-severity 硬規避免了自動誤刪，但 false-positive 訊號浪費人類注意力）
  - counter-factual：若 drift overlay spec 的死碼 candidate 查證 step 要求讀目標 symbol 所在 AGENTS.md 設計意圖，drift 就會在 surface 訊號時一併帶出「AGENTS.md 標註 by-design」，false-positive 不再浪費注意力
  - **已修正**：`illustrate-artifact-menu.md` drift overlay spec 加「死碼 false-positive 防護」查證 step + `MarketIntelService` dogfood 範例
  - **待 flow-review 討論**：這個「結構工具 × 語意 context」邊界是 illustrate drift 特例，還是該下沉成 `arch-thinking` skill 通用能力（讓 `/code-review` 死碼 finding 也消費 AGENTS.md）？同類潛在缺口：drift 的 boundary-crossing 訊號是否也該讀 AGENTS.md 的「by-design 跨層」標註？call graph / class slice 有無類似「只看結構漏語意」風險？

## tags
`illustrate` `arch-thinking` `drift-detection` `flow-review` `dogfood` `結構工具-語意context`
