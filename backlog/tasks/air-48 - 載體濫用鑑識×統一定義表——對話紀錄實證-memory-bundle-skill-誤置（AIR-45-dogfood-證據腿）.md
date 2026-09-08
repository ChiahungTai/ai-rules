---
id: AIR-48
title: 載體濫用鑑識×統一定義表——對話紀錄實證 memory/bundle/skill 誤置（AIR-45 dogfood 證據腿）
status: To Do
assignee: []
created_date: '2026-09-08 12:22'
updated_date: '2026-09-08 12:23'
labels:
  - memory
  - governance
  - context
dependencies: []
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules d00bfe2〕〔已決策勿重辯：①北極星＝稀缺性分層（L2/HBM/DRAM/HDD 類比＋四判準——AIR-45 EP「User 核心定調」段：先辨識最稀缺資源→重要性切分；載體職責×常駐-按需正交；LLM 不知道自己 cache miss→取用入口是另一半）②任務狀態/暫存→scratch（.agent-tmp）/卡/EP，不進 memory（六問 Q1 既有；user 09-08 再證 sessions「繼續濫用」——紀律灌輸已證弱）③specimen 鑑識定案：sess_5220505c「Bridge --session-id L4 probe 驗證與 ai-rules 落地」（09-08 20:05 開工）對 project_session-id-continuation-absorption-0908（24 呼叫）＋reference_cross-harness-session-continuation（32 呼叫、新條目）草稿式迭代≈30 Write——單 session 把池條目當 working scratch 用；正確載體＝卡 notes/scratch＋結案一次性蒸餾④歸因破口：originSessionId 只記創建者（6af3f89d 創建、5220505c 反覆寫——後續 writer 不可見）＋rollout 檔 session 結束即清（證據須發現當下抽取，5220505c rollout 已揮發）⑤分析腿可派 flash agent 執行，但運作方式先定案（user 指示：好好思考→確定怎樣運作→晚點派）⑥濫用面＝memory＋bundle(AGENTS.md)＋skills 三面全查，不只 memory〕〔驗收：①近 3-7 天對話紀錄橫掃（rollout 存檔即時抽取＋db.sqlite part 表＋池 mtime/歸因）→ memory/bundle/skill 誤置 taxonomy＋頻率＋session 歸因表 ②每類誤置→處置設計（紀律/機械閘/載體改道/預設落地點改道——預設路徑改道優先：scratch 比 memory 更近才算修好）餵入 rules/skills/memory 統一定義表初稿（三處分散判準合一：六問載體判定×instruction-writing 決策樹×收斂落點慣例）③後續 writer 歸因可見性修法建議 ④產出＝任務家報告＋定義表初稿；specimen 案例編入〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 誤置 taxonomy＋統一定義表初稿交付（specimen 編入）
<!-- AC:END -->
