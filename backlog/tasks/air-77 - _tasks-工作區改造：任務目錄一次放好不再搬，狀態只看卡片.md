---
id: AIR-77
title: _tasks 工作區改造：任務目錄一次放好不再搬，狀態只看卡片
status: To Do
assignee: []
created_date: '2026-09-11 22:51'
updated_date: '2026-09-11 22:52'
labels:
  - structure
  - migration
dependencies: []
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔human-summary〕把弧工作區改成「一次放好、永不搬家」：新任務目錄按月份歸檔，舊的一次遷進 _archived，之後卡片狀態是唯一的生命週期訊號、連結永不因搬移而斷。

〔baseline：ai-rules 882c9b5〕
〔已決策勿重辯：①append-only——task path 只表達 identity＋建立時間，不表達 lifecycle；lifecycle 唯一源＝卡 status ②新弧落 _tasks/YYYY-MM/<弧名>/，永不搬移 ③done/ 26 已閉弧＋AIR-45 兩已閉弧一次遷入 _tasks/_archived/，遷後凍結（可讀可引用、不再新增不再搬）④path→status 消費者翻轉為 card-status 判讀——metadata-sync（:41,45）、memory-audit（:91）、kanban 結案 refs 重寫、check_report_shells.py（:5-10），外加 memory_telemetry.py／scan_project.py 的 depth 假設 ⑤finalization 定義剔除 filesystem relocation ⑥supersession-move（report/blueprint 退役制防雙真相）不變 ⑦月份目錄優於平面——平面 MM-DD 跨年失年份＋碰撞空間（codex 顧問意見）⑧finalization 原子性改寫：badge／卡 status／summary 照舊收斂，filesystem relocation 退出 ⑨三方諮詢（GLM-5.3 主 session 分析＋codex chatgpt-web 段落級複核 09-12；glm 載具回信未及併入，開工時補查）。風險面：寫入契約首改（收尾慣例全 consumer 翻轉）＋跨文件交叉推導〕
〔驗收：rg 全掃 _tasks/done/ 舊路徑引用零殘留；四處 path→status 消費者改讀卡 status 附 rg 機械證據；3 支 script 月份層 depth 假設掃描通過；活弧 09-11-test-contract-v31 遷 2026-09/ 且 AIR-76 refs 更新；workflow.md 放置規則＋illustrate-html-mode＋execution-plan/implement/commit 等 13+16 檔慣例文本同步；一次性遷移在單 commit 內可 revert〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 done/ 26 弧＋AIR-45 兩已閉弧遷入 _tasks/_archived/；rg 全掃無殘留舊路徑引用
- [ ] #2 path→status 四處消費者改讀卡 status，附 rg 機械證據
- [ ] #3 3 支 script（check_report_shells／memory_telemetry／scan_project）月份層 depth 假設通過
- [ ] #4 新弧出生落 _tasks/YYYY-MM/；活弧 test-contract-v31 遷移＋AIR-76 refs 更新
- [ ] #5 workflow.md／illustrate-html-mode 等 13+16 檔慣例文本同步；單 commit 可 revert
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
mosaic 腿（跨 repo）：handoff 已產出交 mosaic 側自行派工——評估 _projects/<線>/tasks/ 同型慣例跟進或分岔；ai-rules 側不 wait mosaic，兩腿獨立結算。
<!-- SECTION:NOTES:END -->
