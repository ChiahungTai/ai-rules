---
id: AIR-85
title: 條件載入層 vertical slice——bundle-mode marker＋deploy 投影（instruction-writing pilot）
status: Done
assignee: []
created_date: '2026-09-13 00:37'
updated_date: '2026-09-13 10:29'
labels: []
dependencies: []
references:
  - ai-analysis/_tasks/09-13-conditional-loading-vertical-slice/ep.md
ordinal: 71000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 目標一句話
把 scope 分界研究（reports/2026-09-13-scope-boundary-memory-rules-skills/）§3.4 條件載入層設計落地為 deploy_agents.py 機制，以 instruction-writing 為 pilot 證明端到端：CC 端原生 paths: 行為不變、非 CC 三端 bundle 排除 body 留作者寫的 bootstrap 指針行、fail-closed。

## baseline
ai-rules main @ 209966a（scope 研究報告已落檔）。材料源＝reports/2026-09-13-.../report.md §3.4＋materials/codex-followup-out.txt §A（三軸分離設計全文）＋materials/leg5-probe-paths-verdict.md（paths: probe 實證）。

## 已決策（勿重辯）
- 三軸分離：harness-scope=誰消費／paths:=CC 何時載／新顯式 marker（定名本卡裁，候選 bundle-mode: pointer）=非 CC 怎麼投影——paths: 不單獨作非 CC 排除訊號
- bootstrap pointer＝作者寫語義（source 同檔明寫 trigger 句）＋deploy 只機械投影＋fail-closed（target skill 缺失/不可達即 deploy 失敗，禁靜默抽 body）
- 處理序：harness-scope → target eligibility → projection mode；claude-specific+paths 與 meta 不生成 pointer
- 新增 paths: ＝ CC 行為變更（須重跑 bootstrap/first-consequential-action 測試）——本卡 pilot 對象 instruction-writing 為既有 paths: 檔，CC 行為不變成立
- pilot 選 instruction-writing（三條件齊備：已帶 paths: **/*.md、有配對 skill、guide L5 已有 bootstrap 句）

## 驗收
- deploy 產出之非 CC bundle（ZCode/Muse/Codex 三端）不含 instruction-writing body、含作者指針行；CC 端 ~/.claude/rules/ 原樣（含 paths:）
- fail-closed 實測：暫時改壞 target skill 路徑 → deploy 非 0 exit 且訊息可判讀
- bundle bytes 前後量測（Muse 端 headroom ~4KB 基準）記入卡 notes
- check_single_source 全綠＋/consistency 過
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 非 CC 三端 bundle 不含 IW body 且含指針行（diff 舉證）
- [ ] #2 CC 端 rules 原樣部署
- [ ] #3 fail-closed 實測非 0 exit
- [ ] #4 deploy 全端綠＋bundle 量測記錄
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
09-13 user 確認排序：AIR-86 四批收斂＋結案後接續開工（86 不依賴 85；批三 python-standards「AIR-85 前禁 pointer-only」即兩卡銜接點）。85 落地後回頭投影 instruction-writing/llm-output 兩支，bundle 終態 band 19–23.5KB 才閉合。user 明示定位＝「很重要的東西」——bundle 縮減的第三手段（刪除/下沉之外的結構性投影），機制卡走 execution-plan 建卡流程。

09-13 四段完成＋全 AC 證據（材料＝ai-analysis/_tasks/09-13-conditional-loading-vertical-slice/ep.md「段 3 驗收證據」節）：AC#1 三端 29,161B byte-identical（29,949→29,161，−788B；Muse headroom 對 36KiB gate 79%）；AC#2 CC 靜態＋L4 三臂 probe PASS（unknown keys 相容；settings.json symlink 隔離法）；AC#3 真環境 fail-closed exit1 實測；AC#4 deploy 全端綠。pointer 行為測試 5/5（ZCode headless 直連 GLM-5.3：.agents 單根可達實證、canary/逐字引用雙證、壓力變體全真載入）。oracle 14/14＋全套 404 tests＋冪等真跑雙驗。deployed 終態 29,161B。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
條件載入層 vertical slice 落地：bundle-projection 三鍵 schema＋deploy 投影（凍結模板 annotation＋作者句逐字）＋全域 preflight fail-closed＋冪等零寫入；instruction-writing pilot 上線（三端 bundle −788B、CC unknown-keys L4 三臂 PASS、ZCode headless pointer 行為 5/5、.agents 單根實證）；404 tests＋codex oracle 14/14。AC#1-4 全證據（EP 段 3 驗收證據節）。後續：llm-output 第二支 opt-in（機制已驗證）＋interface debt（purity/broken-ref 掃 full source）。
<!-- SECTION:FINAL_SUMMARY:END -->
