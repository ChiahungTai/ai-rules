---
id: AIR-33
title: cr-demand：Python 符號面兩缺口——class DEF 查無＋pyrefly-producer CJK panic
status: Done
assignee: []
created_date: '2026-09-06 05:54'
updated_date: '2026-09-06 11:26'
labels:
  - cr-demand
dependencies: []
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔觸發場景〕AIR-32 dry run（reviewer spawn prompt CR 接線查證段命令實跑，mosaic_alpha）。〔實證缺口〕① class DEF 查無：class ConditionBase(ABC)（mosaic_alpha/conditions/base.py:60）於新鮮 index（@HEAD b206080、16488 nodes、自癒後）下 scip_refs --callers 三種名形態（bare／module.qualified／file::name）皆查無 DEF；同檔函數面正常（separate_up_down_peaks 3 callers＋sites＋item-level OK）——class 符號 lookup 面 gap。② pyrefly-producer regen 對 CJK 原始碼 panic：emit.rs:171 char-boundary（'共' bytes 4255..4258／'會' bytes 3168..3171 兩次實錄）；首次重生成 panic、二次成功（102s heal）——panic 期間查詢以舊 index 作答（degraded contract 有生效、fail loud）。〔期望能力〕Python class DEF 查詢可用；producer 對多位元組內容不 panic。〔驗收：code-reality repo 修復後 scip_refs ConditionBase --callers 回真實 callers；CJK 檔案 regen 不再 panic〕
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
09-06 補精確（user『太早查詢？』 challenge 後複測）：①時機假說已否證——stamp 相符（index@HEAD b206080、16488 nodes）下 class 仍全面查無（ConditionBase／ConditionDependency／MovingAverageCondition 三 class 跨兩檔全 miss；同域函數 separate_up_down_peaks 正常）＝系統性 class 符號面 gap，非 stale 造成。②panic 歸因修正：前兩次重生成是真 panic（exit 101、兩個不同 offset），非『查詢太早／部分癒合中間態』；之後多次 heal 乾淨成功（102s＋159.5s 實錄）＝間歇性（疑並行分片切片多位元組邊界，重跑不同 partitioning 即避開）——穩定重現條件待 code-reality 端歸因。③副作用發現：查無 DEF 會觸發反复 heal（159.5s 那次 [SRC] stamp 已相符仍重建）——reviewer 對 class 符號跑 callers 會踩 100~160s/次重建 loop 且仍拿不到結果；class 面修復前，AIR-32 範本的 callers 指令對 class 符號是熱點，消費端 know-this。

09-06 handoff prompt 已交付 user（目標＝code-reality repo session；baseline 1b53f6b＝安裝面 0.6.3+1b53f6b、無部署落差；b30af73 class DEF 修復已在 binary 內但未涵蓋本 repro——接手勿重做；panic 點 emit.rs:171 byte slicing 已定位）

09-06 驗收（owning 側）：step 0 即擋——main 無新 commit、任何 branch 皆無、tree clean、binary 仍 0.6.3+1b53f6b（09-04 build）；sess_6619cd63 尾部停在考古發現後，修復未開工（「修好了」為過時 relay 宣稱）。框架糾正：b30af73 是文檔化限制非修復（class 名非可查 key、workaround＝查 method 形態 bare 或 Class.method）——class 查詢路徑從未被修過。考古戰利品續傳：WARN 源碼 engine.rs:249,262,616,624／cli.rs:643；既有斷言測試 s2_engine.rs:194、build.rs:744,768、callers_cli.rs:163、s4_cli.rs:140；CODE_REALITY_AUTOHEAL=off 可關自動 heal。重發修正版 handoff。

驗收證據（09-06 owning 側）：安裝面 0.6.4+8595984（19:18 build＝source HEAD，f75b86a 在 main）；regen 命令＝pyrefly-index --repo（直接生成後須補 scip_refs --stamp-meta，否則 [SRC] 缺 index 版本——操作指引非 bug）。relay 宣稱 53 suites 未自跑（修復方 L2），驗收以 AIR-33 desc 三項為準、全綠。
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
owning 側 L4 驗收全綠（code-reality 0.6.4+8595984＝f75b86a 修復）：①class callers 三樣本回真實 callers（ConditionBase 15/22 sites CLI＋MCP 一致、ConditionDependency 1、MovingAverageCondition 3）＋函數對照組無回歸 ②CJK regen ×2 零 panic（97.22s／84.51s 全量；refresh.log 15 筆 panic 全為修前歷史）③重複查詢 0.08~0.11s 零 heal 行、缺場改快速 fail-loud。修復確認落地
<!-- SECTION:FINAL_SUMMARY:END -->
