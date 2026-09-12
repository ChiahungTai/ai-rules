---
id: AIR-78
title: bridge glm 委派檔位規則入 model-routing——派工必帶 --model，禁裸委派防靜默落 flash
status: To Do
assignee: []
created_date: '2026-09-11 23:38'
updated_date: '2026-09-12 00:00'
labels:
  - model-routing
  - bridge
  - governance
dependencies: []
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔human-summary〕把「bridge 派工給 glm 家族必須明確指定模型檔位（lite 用 sonnet、旗艦用 opus）」寫進 model-routing skill——裸委派會靜默落到 flash 版且帳本查不出實際檔位。設計已與 codex 聯合定案，等 M1 瘦身弧落地後開工。

〔baseline：ai-rules 93b5c5a〕
〔已決策勿重辯：①落點＝skill external-runtime family 表加 glm row＋3 行 glm 專節（倣 webgpt 模式）；rules/ 零改動（M1 下沉後 rule 只剩詞彙＋必載條款，family enum 已含 GLM）②檔位語義：sonnet→flash 別名、opus→GLM-5.3 旗艦；lite 派 --model sonnet、full-tier 派 --model opus；裸委派禁止作為 routing contract（09-12 實測落 flash＋ledger effectiveModel null 無證明力）——delegate-bridge d4 default pin 落地前連 lite 都要顯式 --model（codex 收緊：provenance 論證）③審計語義：以 dispatch/requested model flag 為 authoritative evidence；carrier effectiveModel 現不具證明力④唯讀 carrier v1（寫入走 muse）＋--effort/--steps/--yolo 不適用——放專節不放表（表不塞肥）⑤resume/fork 定向接續表不加 glm row（session identity 連續性未證）——專節明寫 resume/fork semantics unverified; do not infer continuation support from muse/codex⑥in-harness 對照句寫條件式：「若 in-harness full dispatch 會繼承 Flash，則 full-tier GLM 工作改走 bridge --model opus」——AIR-76 落地後條件自然失效不留歷史特例⑦時序：嚴格兩弧兩 commit——M1 下沉弧完整落地並 re-read post-M1 skill 實際形態後才開工（root cause 不同：M1 收斂既有真相、本弧新增 family runtime contract，acceptance boundary 與 review identity 不同）⑧arc home 依當下已部署 task topology（legacy 頂層），AIR-77 遷移時搬——不提前走 YYYY-MM/（script depth 假設未翻轉＝false-green 風險：script 成功退出卻沒掃到新弧）；不在本弧順手修 scanner（第三 root cause 不混弧）。源工單＝delegate-bridge f821ca7 跨 repo 交接〕
〔驗收：①family 表 glm row＋專節在場②三 invariant 機械可驗——full 派單必產 --model opus、lite 必產 --model sonnet、unsupported flags 零送出（instruction 層能控制且能獨立驗證者；ledger effectiveModel != null 不屬本弧驗收——那是 delegate-bridge d4 責任邊界）③enum 反查：掃 muse/codex/--family/family switch/generic bridge command builder 暗含二值（只有兩家）假設處逐檔處置——agents/ 零改動須由反查證明而非 glm 零命中證明④rg -i family glm 每個委派指引點帶檔位語義；instruction sync/deploy 完成〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 family 表 glm row＋3 行專節落地（值域／檔位政策／審計語義／resume-fork unverified 句）
- [ ] #2 三 invariant 機械驗證：full→--model opus、lite→--model sonnet、unsupported flags 零送出
- [ ] #3 enum 反查完成（muse/codex/--family 二值假設全掃）；agents/ 零改由反查證明
- [ ] #4 時序證據：M1 弧 commit 在前＋post-M1 skill 形態 re-read 記錄
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔09-12 v2 工單修訂（源 delegate-bridge f821ca7 同 baseline、事實面翻新，含 file:line）——修訂原決策②③④、新增兩毒型〕
◆撤銷：原②「d4 default pin 落地前連 lite 都要顯式 --model」——前提消失：bridge 已 pin（glm.rs:39 DEFAULT_MODEL=sonnet），裸委派確定性落 flash。修訂後核心規則＝full-tier（judge/EP 規劃/重型裁量）必帶 --model opus；flash 段（機械/研究/findings）可不帶。禁裸 full-tier 委派不變。
◆修訂③審計語義：effectiveModel 於 job finalize 才落帳——running 中 runs 顯示 - 屬正常非未 stage；原「carrier effectiveModel 不具證明力」句撤銷（v1 live 觀察係 mid-run 誤讀）。
◆擴充④flag 表面（glm.rs:1010-1031 validate_flags，exit 2 fail-loud）：拒收 --trust-workspace/--steps/--yolo/--effort/--allow-workspace-switch/--network；收 --model/--background/--caller-session/--json/--resume＋positional prompt。「--trust-workspace --steps 800」形＝muse 專用，glm 照抄即炸——skills 內 bridge 委派範例須標 family 差異。
◆新增毒型A（fail-silent，最危險）：glm 載具恆 --mode plan（唯讀，R4 安全決策）——寫入型工單派 glm＝status=completed 但零檔案落地（live 實證：EP 規劃輪）。「GLM 寫」目前只有 orchestrator 直做；寫入型一律走 muse。專節重點標。
◆新增毒型B（三家族通用）：bridge spawn 面 one-shot、child stdin 恆 null（task.rs:610）——muse MSP turn/steer、codex turn/steer+queue、zcode app-server session/send 的 protocol 級 steer bridge 全不可達。操作語義：委派出去不能改道，只能 stop 殺了重派。muse/codex row 同步帶此句（通用事實非 glm 專屬）。
◆不變：落點（family 表 glm row＋專節）、rules/ 零改動、resume/fork 表不加 row（v2 收單含 --resume 但 session identity 連續性仍未證——維持 unverified 句）、兩弧時序（M1 後 re-read post-M1 形態再開工）、arc home legacy 頂層（AIR-77 遷移時搬）、enum 反查、驗收三 invariant（full→opus／lite→可不帶或 sonnet／unsupported flags 零送出——第二項依 v2 放寬）。

〔09-12 補裁決——sonnet 語源查證（glm.rs:50-51,442-455 源碼實查）〕sonnet/opus 與 GLM 無本質關聯——係 bridge 自 V1 JS 原型沿用的內部別名慣例（借 Anthropic 檔位詞彙）；解析順序＝裸委派→DEFAULT_MODEL sonnet→alias 表轉原生 id→才 stage 給 carrier；alias 表外值 pass-through 且不分大小寫——原生名 --model GLM-5.3／--model glm-5.3-flash 直接可用（僅擋非 GLM 模型）。zcode provider table（~/.zcode/v2/config.json）全為原生名鍵、零 sonnet/opus 鍵。**instruction 層詞彙裁決：原生名為 canonical**（full＝--model GLM-5.3、lite＝裸或 --model GLM-5.3-Flash，與 in-harness registry pin 詞彙一致）；sonnet/opus 降為「存在的別名」記載（辨識用不推薦）。user 09-12 提問促成此查證。

〔09-12 詞彙邊界裁定（user）〕glm family 詞彙面＝原生名專用：full＝--model GLM-5.3、lite＝裸（bridge 內建預設落 flash）或 --model GLM-5.3-Flash。sonnet/opus 係 CC 詞彙，禁混入 glm family 指引（opus 要用就走 CC）；bridge 內部 alias 映射（glm.rs MODEL_ALIASES）屬 delegate-bridge 實現細節，住該 repo docs、不進 ai-rules doctrine——與 CC 接線抽樣化同一原則（詞彙面進規範、接線 machine-local）。修正先前「sonnet/opus 降為存在的別名記載」條款：連別名記載都不留。驗收不變：full 派單必產 --model GLM-5.3（非 opus）。
<!-- SECTION:NOTES:END -->
