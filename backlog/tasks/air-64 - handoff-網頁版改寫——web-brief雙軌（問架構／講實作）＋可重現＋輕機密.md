---
id: AIR-64
title: handoff 網頁版改寫——web-brief雙軌（問架構／講實作）＋可重現＋輕機密
status: To Do
assignee: []
created_date: '2026-09-09 10:18'
labels: []
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
把 /handoff 跨provider 軌改寫為 web-brief：網頁 AI 無本地端，本地欄全 drop，改問架構／講實作雙 schema＋可重現片段，機密降級只擋 key。〔baseline：ai-rules 5a6ce2e〕〔已決策勿重辯：①web 兩用法＝問架構（實作前）／講實作求審（實作後）；②嵌入＝可重現片段，廢最小抽象化；③機密只擋 key/token/帳號，策略不擋；④本地軌（同repo/跨repo）schema 不動；⑤只改 self-contained-prompt＋handoff 兩檔，agent-review-cycle 不動〕〔驗收：web-ask/web-tell 範例各一可貼即用，本地軌零變更〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 web-ask/web-tell 範例各一；本地軌零變更；兩檔自洽無 drift
<!-- AC:END -->
