---
id: AIR-41
title: memory 死亡條目盤點——transcript 零讀取條目候選（只列不刪、走核可）
status: To Do
assignee: []
created_date: '2026-09-07 07:56'
labels:
  - memory
  - governance
dependencies: []
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
目標：挖 transcript 找從沒被讀過的 memory 條目，列合併/刪除候選——補現行體系唯一沒量的維度（有流入量測 300/day、無命中量測）。只列候選不自動刪，處置走 advisory→用戶核可→執行。〔baseline：ai-rules 339e2c9〕〔已決策勿重辯：①候選≠刪除——輸出是 advisory 清單，用戶逐條核可才執行（治理三分離）；②讀取定義＝明確 Read 條目檔本體（開場索引載入不算命中；rg 掃描不算）；③雙源——ZCode db.sqlite part 表（Read file_path）＋CC session jsonl 兩邊都挖，只掃一邊會漏判；④誤殺防護——rank hot／近 30 天 mtime／活躍弧條目豁免列入（即使零讀）；⑤與 rank 排序協同不打架（死亡候選預設 cold 沉底，刪除仍要核可）；⑥規模初判 standard（方法＋腳本＋memory-audit 文檔段），開工階段 1 確認是否升 EP〕〔驗收：①腳本對 ai-rules 池跑出零讀取（90 天窗）清單；②人工抽 3 條驗真未讀（含雙源交叉）；③一輪 advisory→核可→≥1 條處置落地；④memory-audit skill 補 lite/full 觸發段；⑤豁免三類零列入〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 跑出 90 天零讀取清單，抽 3 條雙源驗真
- [ ] #2 一輪 advisory→核可→≥1 條處置落地
- [ ] #3 memory-audit 補觸發段文檔
- [ ] #4 豁免三類零列入
<!-- AC:END -->
