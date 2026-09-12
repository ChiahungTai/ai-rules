---
id: AIR-81
title: blueprint 導覽網頁刷新——補優先序治理段與載體結構章投影
status: To Do
assignee: []
created_date: '2026-09-12 13:28'
labels: []
dependencies: []
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔human-summary〕
blueprint 的人類導覽網頁（index.html）是治理檔的投影，目前落後兩個內容：09-12 拍板的多卡優先序治理（Priority backbone 段，48f2f88 已改 AGENTS.md 但投影未刷）與同日新增的載體結構章（structure.md，五層載體×四邊型）。這卡把網頁刷新到與檔案同步——投影落後的首次實證案例。

〔baseline：ai-rules a21ced6〕
〔已決策勿重辯：①投影形態＝手寫＋殼 codegen（AIR-74 裁決：報告殼全走手寫＋codegen，index.html 進版控）②載體 graph 常設位＝blueprint/structure.md 第四檔（09-12 user 拍板；dependency-graph.md 慣例語義為功能 repo 不適用 ai-rules）③本卡只刷新投影，不改四檔內容〕
〔驗收：①index.html 含 Priority backbone 段投影 ②含 structure 章投影（至少：五層載體表＋四邊型清單＋斷鏈表）③頁頭生成註釋更新為四檔投影 ④自包含單檔、file: 直開成立（viewport 慣例：資產內嵌、無外部 fetch）〕

開工提示：894 行手寫檔刷新屬 AIR-73 build_shell.py codegen 可承接域——若 AIR-73 已落地優先走 codegen；未落地則手寫刷新。斷鏈表中「投影無 gate」弱點的機械防線不在本卡範圍（另行評估）。
<!-- SECTION:DESCRIPTION:END -->
