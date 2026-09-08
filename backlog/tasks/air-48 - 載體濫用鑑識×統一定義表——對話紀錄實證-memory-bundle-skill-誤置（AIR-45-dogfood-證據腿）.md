---
id: AIR-48
title: 載體濫用鑑識×統一定義表——對話紀錄實證 memory/bundle/skill 誤置（AIR-45 dogfood 證據腿）
status: To Do
assignee: []
created_date: '2026-09-08 12:22'
updated_date: '2026-09-08 12:46'
labels:
  - memory
  - governance
  - context
dependencies: []
references:
  - >-
    http://127.0.0.1:6421/viewer/_md-viewer.html?p=/ai-rules/_tasks/09-08-carrier-misuse-definition/ep.md
  - ai-analysis/_tasks/09-08-carrier-misuse-definition/ep.md
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules d00bfe2〕〔已決策勿重辯：①北極星＝稀缺性分層（L2/HBM/DRAM/HDD 類比＋四判準——AIR-45 EP「User 核心定調」段）②任務狀態/暫存→scratch（.agent-tmp）/卡/EP，不進 memory（六問 Q1；user 09-08 再證 sessions「繼續濫用」——紀律灌輸已證弱，修法走預設路徑改道）③specimen 鑑識定案：sess_5220505c 對兩池條目≈30 Write 草稿式迭代（24+32 呼叫）；正確載體＝卡 notes/scratch＋結案一次性蒸餾④歸因破口：originSessionId 只記創建者（後續 writer 不可見）＋rollout session 結束即清（證據發現當下抽取）⑤分析腿派 flash agent；運作方式先定案（user 指示）⑥濫用面＝memory＋bundle(AGENTS.md)＋skills 三面⑦**AIR-45 殘餘移交**：B 上線切換＝本卡 Phase 3；catalog live 單探針補驗隨手做；mosaic 層級軸歸 mosaic 側 session（判準表在 s3-report）⑧階段序：P1 鑑識（證據是過去式，早跑）→P2 統一定義表 v1（三處判準合一：六問載體判定×writing 決策樹×收斂落點慣例）→**P3 B 上線切換＝定義表首次執法**（live MEMORY.md→12 常駐＋inventory＋工作節點；常駐集合依 P1 證據修正）→P4 dogfood 迴圈〕〔驗收：①近 3-7 天對話紀錄橫掃→誤置 taxonomy＋頻率＋session 歸因表 ②統一定義表 v1（載體職責×常駐-按需×寫入預設交叉表；每類誤置→處置設計，預設路徑改道優先）③**B 上線切換完成＋切換後 dogfood 首輪行為對照**（找得到/用得出）④後續 writer 歸因可見性修法建議 ⑤catalog live 探針補驗 ⑥產出＝任務家報告＋定義表；specimen 編入〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 誤置 taxonomy＋統一定義表初稿交付（specimen 編入）
<!-- AC:END -->
