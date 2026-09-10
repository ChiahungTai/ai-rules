# 兩份 WT 研究對照與融合（2026-09-10，GLM 5.3 judge）

> A＝ai-rules 側 WT 裁決（`reports/2026-09-10-wt-workflow-decision.md`＋`blueprint/workflow.md`——三方：GLM 5.3×muse×codex）。B＝mosaic 側研究（user 轉貼 handoff——muse `job-mtus9qz3`＋codex `job-mtus9r17`＋ZCode judge；工單 `mosaic_alpha_trading_lab/.agent-tmp/wt-usage-advisory-prompt.md`）。本文是融合討論（第三輪）前的 judge 對照分析。

## 一、切入角：互補的拼圖

- **A 管①③⑥站**（開工/收斂的 WT 生命週期）：control/execution plane、board single-writer、wt-open/close、池 symlink、fresh-machine。
- **B 管④⑤站**（任務內陣仗）：scratch WT 三條件、凍結點、reviewer leaf、subagent fallback 守則、runtime 隔離。
- 重疊帶＝「免卡小修的 WT 形態」與「writer 落點」——見衝突點。

## 二、B 的精華（A 缺、值得吸收）

1. **凍結點機制**：impl 停手→pin revision identity→reviewers 綁同版平行進場——A 的 wt-open 有 baseline 驗證但無「impl→review 凍結」概念。吸收落點：`blueprint/workflow.md` ⑤驗證站或 agent-workflow skill。
2. **revision tuple**：base_sha＋head_sha＋tracked diff digest＋**untracked manifest**（B 的 codex 點破：只 pin HEAD 漏 uncommitted/untracked）——比 A 的 baseline 驗證完整。
3. **reviewer＝唯讀 leaf**：不碰 ref lifecycle／不可再派／讀料順序（fresh-eyes 最後讀 impl 自述）——agent 級 single-writer 同構，A 只有 board 級。
4. **subagent 跨 WT fallback 守則**：全絕對路徑／禁相對／寫入探針／寫不進 fail loud 禁退回 caller WT——A 的 workflow.md 無此細節。
5. **runtime 隔離**：WT 隔離不了 PG/Redis/固定 port——整合測試錯峰聲明。A 完全未提（量化 repo 特有但通用性存在）。
6. **線判定 identity contract**（scratch 命名＝前綴繼承＋建立時顯式落盤 owning_line/base/task/branch）——與 A 的「WT path 可機械推導」同向但更具體。

## 三、衝突點（需第三輪裁決）

### C1：免卡小修的落點——B「線 WT 開 branch 直接修（三條件不中）」 vs A「primary 永不寫 code，一律 ephemeral WT」

語境參數不同：B 的線 WT 是**單 session 自有**（無互踩風險，branch-in-place 乾淨）；A 的 primary 是**多 session 共享**（checkout 互踩實證 → 全上 execution plane）。兩個可能：①參數化（線 WT 單 writer→允許 branch-in-place；共享→ephemeral WT）——但與 A 的「ownership 模糊即復活」論證張力；②統一從嚴（都 ephemeral）——B 語境下成本高收益低。judge 傾向：**參數化的判準用「該 WT 是否有 control-plane 職責」**——有（A 的 primary）→禁寫；無（B 的線 WT＝純 trunk 工作 WT）→branch-in-place 可。待顧問裁。

### C2：單 writer gate——B 的 `AGENTS.md:143`「一線同時一卡」 vs A 的多卡並行波次

B 更嚴且 codex（mosaic 側）抓到 scratch＋第二卡現行不合法的矛盾。A 的六線波次事實是序列（O1-O8 衝突矩陣證明「平行」多數假象）。judge 傾向：**吸收為預設 gate**（solo 一線一卡是實態），例外=跨 repo（L6）與唯讀。待顧問裁。

### C3：凍結的機械形態——B 決策點③（commit 到卡 branch vs revision tuple）與 A 的 commit consent 條款互動

A 的 outward 規則：commit 需確認（建卡/特赦例外）。B 的「impl 完工即 commit」若吸收，牽動 commit gate 政策。judge 傾向：revision tuple 為主（不動 consent）、凍結點 commit 列為選配。

## 四、A 有 B 無（回饋價值）

board single-writer＋lock／記憶池 symlink 拓撲（B 未觸 memory）／fresh-machine runbook／過渡條款模式／relay freshness invariant。

## 五、融合後的目標形態（草案，待第三輪驗證）

八站全譜：A 的①③⑥⑦⑧＋B 的④⑤填充＋C1/C2 裁決參數化。載體：`blueprint/workflow.md` 擴充（⑤站新節＋fallback 守則）＋agent-workflow skill（凍結/reviewer leaf）＋B 側落 mosaic 專案段（其 handoff 已界定分工：全域歸 ai-rules、專案段歸 mosaic main WT）。
