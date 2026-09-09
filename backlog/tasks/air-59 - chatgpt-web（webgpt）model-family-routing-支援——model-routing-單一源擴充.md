---
id: AIR-59
title: chatgpt-web（webgpt）model family routing 支援——model-routing 單一源擴充
status: To Do
assignee: []
created_date: '2026-09-09 11:40'
labels:
  - model-routing
  - governance
dependencies: []
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
將 codex-chatgpt-web（user 口語 webgpt，v5.0.6）的 chatgpt-web model family 納入 model-routing 治理單一源。〔baseline：ai-rules 63a8a19〕〔已決策勿重辯：①chatgpt-web/high＝旗艦（full tier），底層 gpt-5.6-sol（web）；每 slug 固定 effort——effort 旗標不會換 browser model ②web 額度＝獨立 pool（ChatGPT web 訊息額度、零 API 費），與訂閱 Codex 額度分帳；原生 slug（gpt-5.6-sol 等）經 bridge passthrough 額度照舊 ③不帶旗標落點＝config 預設 chatgpt-web/medium（09-09 查驗——舊註記 gpt-5.5/low 已過時，本卡修正）④codex 顯式指定才派政策不變、dispatch 預設不派維持 ⑤launcher/bridge（127.0.0.1:17841）是 codex 全 model 單點依賴——進程死＝全 model fail-closed〕〔驗收：family 表 codex row 擴充 chatgpt-web/high（旗艦）＋chatgpt-web/medium 條目含 web pool/passthrough/單點語義；config 預設現值註記修正；單一源引用面 rg 掃描同步（rules 骨架核對＋memory「待同步」註記回收）；部署副本機械驗證；instruction-writing 五維＋consistency gate 過〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 chatgpt-web/{high,medium} 進 family 表且 high 標旗艦 full；額度現值段含 web pool 註記；gpt-5.5/low 過時落點註記修正；部署面 rg 命中驗證；五維自洽＋consistency 過
<!-- AC:END -->
