---
id: AIR-14
title: Backlog.md 治理設計（卡即 handoff）
status: To Do
assignee: []
created_date: '2026-09-03 04:31'
updated_date: '2026-09-03 05:20'
labels:
  - governance
  - backlog
  - handoff
dependencies: []
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
中繼站治理設計（兩族合一，2026-09-03 開卡）。〔baseline：ai-rules 919c108〕〔已決策勿重辯：①兩族合一框架（任務型+檔案型）user 09-03 裁定 ②討論題即時不建卡——對話即載體，session 斷才落 draft ③drafts=未承諾/觸發型進口（rules-audit draft 首例）④AIR-4 退場走 archive 非 delete（可復活）⑤_inbox 傾向不採——drafts 即進口（待本卡定案）⑥卡三層分工 desc=決策層/EP=規劃層/notes=留言層〕設計問題：卡即 handoff 契約（desc 何時夠格當 handoff——本卡自身即測試案例）、drafts 進口慣例、升卡流程、notes 治理（長度/結案蒸 District/與 EP 邊界）、兩層判定（small 卡即 handoff vs standard+ 卡＋EP）、「做 AIR-N」起手式、EP 修訂時 desc 同步義務；檔案型——.agent-tmp 清淤（36 檔殘留實證）、新 dot-area 門檻、夜間 cron 掃殘留腿、.at-contexts 退場、.review 健康形態參照；共同問法：誰進來/停多久/誰清/清去哪（有進有出）；排程清單單一真相源需求（cron 職責散在 prompt 無總覽——本 session 兩次認知過時實證）。〔驗收：設計文件覆蓋上述全部＋以 MOS-14 卡/EP 與本卡群（AIR-13~17 開卡過程）為回歸樣本；文檔化落地清單（kanban-board/handoff/execution-plan/collaboration-constraints 手術）含 sync-sources 檢查〕
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
接手指針（09-03 開卡 session 留）：①活實踐樣本＝今天開 AIR-13~17 全過程——進入判準三條實戰（建卡=scope 定+跨 session+可驗收；draft=觸發型；不進=session 內可消化）、兩次 desc 漂移修正（AIR-16 .gitignore 項被並行 commit 搶走→如實化；AIR-15 標題帶舊 scope→改名）、合併先例（②暫存區併入本卡）。②卡即 handoff 張力實證：desc 摘要層裝不下 handoff 八欄——本卡補法=desc 收不變決策+驗收、notes 收接手交代；設計時把這個模式定案或改進。③mosaic 原稿七問在 09-03 handoff（用戶可提供）；MOS-14 卡+EP 絕對路徑：/Users/ctai/Github/mosaic_alpha/backlog/tasks/ 與 ai-analysis/_tasks/。④夜間 23:40 收斂 cron 已運行（automation-751ecce2）——檔案型中繼站的清淤腿可考慮掛它。⑤dual-family 審查（GLM+muse）模式今天首發，可作設計參考
<!-- SECTION:NOTES:END -->
