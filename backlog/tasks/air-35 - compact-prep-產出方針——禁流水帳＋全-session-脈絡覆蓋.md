---
id: AIR-35
title: compact-prep 產出方針——禁流水帳＋全 session 脈絡覆蓋
status: Done
assignee: []
created_date: '2026-09-06 22:30'
updated_date: '2026-09-06 22:37'
labels:
  - skills
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/viewer/_md-viewer.html?p=/ai-rules/backlog/tasks/air-35
    - compact-prep-產出方針——禁流水帳＋全-session-脈絡覆蓋.md
  - backlog/tasks/air-35 - compact-prep-產出方針——禁流水帳＋全-session-脈絡覆蓋.md
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
user 09-07 回饋：compact-prep 產出不要記流水帳、不要傻傻單純只使用最後幾筆討論跟內容。任務＝盤點 skills/compact-prep/SKILL.md 現行產出方針 → 調整為：①任務脈絡優先（目標/決策/待辦/state）非時序流水；②素材涵蓋整個 session（掃全對話的任務結構）非尾端對話窗口。〔baseline：ai-rules d26dd6f〕〔已決策勿重辯：① 產出方針＝脈絡壓縮非時序摘要（user 09-07 原話「不要記流水帳」）；② 素材範圍＝全 session 非最後幾筆（user 09-07 原話「不要傻傻單純的只使用最後幾筆討論」）〕〔驗收：compact-prep skill 含產出方針兩條約束；與 Summary Instructions（guide 壓縮策略段）語義一致無矛盾〕
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
compact-prep 產出方針落地——落檔從『最後 6 則 raw tail』改為脈絡外部化檔（preserve-list 結構、素材掃全 session、verbatim 按相關性選取）；CC hook 重定位為機械 verbatim 復原層；無 db fallback 同步去尾端窗口語義
<!-- SECTION:FINAL_SUMMARY:END -->
