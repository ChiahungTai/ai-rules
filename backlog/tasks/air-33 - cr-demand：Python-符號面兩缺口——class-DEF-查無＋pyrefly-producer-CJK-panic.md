---
id: AIR-33
title: cr-demand：Python 符號面兩缺口——class DEF 查無＋pyrefly-producer CJK panic
status: To Do
assignee: []
created_date: '2026-09-06 05:54'
labels:
  - cr-demand
dependencies: []
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔觸發場景〕AIR-32 dry run（reviewer spawn prompt CR 接線查證段命令實跑，mosaic_alpha）。〔實證缺口〕① class DEF 查無：class ConditionBase(ABC)（mosaic_alpha/conditions/base.py:60）於新鮮 index（@HEAD b206080、16488 nodes、自癒後）下 scip_refs --callers 三種名形態（bare／module.qualified／file::name）皆查無 DEF；同檔函數面正常（separate_up_down_peaks 3 callers＋sites＋item-level OK）——class 符號 lookup 面 gap。② pyrefly-producer regen 對 CJK 原始碼 panic：emit.rs:171 char-boundary（'共' bytes 4255..4258／'會' bytes 3168..3171 兩次實錄）；首次重生成 panic、二次成功（102s heal）——panic 期間查詢以舊 index 作答（degraded contract 有生效、fail loud）。〔期望能力〕Python class DEF 查詢可用；producer 對多位元組內容不 panic。〔驗收：code-reality repo 修復後 scip_refs ConditionBase --callers 回真實 callers；CJK 檔案 regen 不再 panic〕
<!-- SECTION:DESCRIPTION:END -->
