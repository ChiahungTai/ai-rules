---
id: AIR-66
title: >-
  muse user bundle 36KiB 自限——guide/三肥段瘦身＋MUSE_USER_BUDGET 部署 gate（×cr-audit
  R8/R5 合流）
status: In Progress
assignee: []
created_date: '2026-09-09 21:43'
updated_date: '2026-09-09 22:13'
labels:
  - governance
  - bundle
dependencies: []
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User 09-10 拍板方案甲：ai-rules 部署的 muse user 層自限 36,864B（現 40,092B——09-09 AIR-53 精煉 mosaic 專案層到貼線 292B、mos-80 +333B 後串接全額 65,577 超 64KiB 線 41B，尾段規則截斷）。範圍：①瘦身 ≥3.2KB——guide+header 6,386B→~4.5KB＋tool-discipline(3,938B)/quality-constraints(3,613B)/collaboration-constraints(3,323B) 三肥段語義壓縮（深層已有 skill 可承接者下沉）；②scripts/deploy_agents.py 加 MUSE_USER_BUDGET=36,864 硬 gate（獨立於 BUNDLE_MAX_BYTES=90KB 共用 gate——只看 user 層不看專案層是本次炸鍋結構破口；超線拒部署）；③合流 cr-audit R8 承諾網掃除（reports/2026-09-09-cr-role-audit.md R8：19 載體零使用掛名刪或降按需參見——瘦身與掃除同面一次做）＋R5 量測換軌（事件觸發主形態＋KPI 換 negative-claim 覆蓋率，併 corrections-weekly 治理腿）。驗收：部署後 ~/.config/muse/AGENTS.md ≤36,864B＋四部署檔 cmp 一致＋24 tests 綠＋mosaic 串接全額 65,536-framing 復歸線內（user 40K 內＋mosaic 24,660＋825 ≤ 65,536 留 ≥3.2KB 緩衝）。
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
〔開工 handoff 09-10 CC〕①瘦身改**源**（ai-development-guide.md＋rules/*.md）非部署產物——改後跑 scripts/deploy_agents.py 重部署＋rg 掃引用防 drift（sync-sources 紀律）；四家共用源，zcode/opencode/codex 同步瘦。②語義壓縮非截斷——已有 skill 深層的（tool-discipline/quality-constraints/acceptance-evidence）rule 面壓薄留 pointer；「易被合理化動搖」的論證保留。③gate 實作參考 :491 既有註記位（muse: 64KiB shared with project layer）——MUSE_USER_BUDGET 獨立常數超線 exit 1。④R8 清單在報告 :196 行表格（19 載體零使用掛名）；R5 併 corrections-weekly 治理腿。⑤驗收：部署檔 ≤36,864B＋四檔 cmp＋288 tests＋mosaic 串接全額 ≤65,536（40,092→36.8K 後全額 62.3K 留 3.2K 緩衝）。⑥codex advisory 進行中——建議回來 CC 轉入本 notes 續用。⑦開 branch air-66。

〔codex advisory 回收 09-10 CC（job-mtumf2xo，read-only 查證）〕①止血目標上調：≥3.3KB（5% floor=減 3,318B）、佳 5KB（7.5% target=減 4,956B）——user bundle 每 byte 對所有 muse 消費 repo 重複課稅，共享層從嚴；只砍 41B＝放回懸崖邊。②水位定錨：34-35KiB operating target＋36KiB hard ceiling（user 拍板 36KiB=ceiling；5% 以下 fail/5-7.5% warn/≥7.5% healthy 三段判讀——mosaic 側腿用）。③機制分工：ai-rules 側=A' global envelope（本卡 gate 即此形態，不列舉 consumer repo——清單必漂）；mosaic 側 B 腿（commit/治理 gate 量 user+project+framing 全額）＝primary gate，歸 mosaic 治理（與 AIR-54 S6 相鄰可順接）；C 腿=bundle-watch 擴跨 repo 漂移偵測（ai-rules 週日看照擴充）。④CLAUDE.md warning 忽略確認（不為消 warning 改拓撲）。最終組合：瘦身+A' +B+C+D 原則。
〔進度 09-10 ZCode 主 session（air-66 branch）〕**瘦身＋gate＋R8/R5 實作完成；advisory floor/target 缺口 82B/1,720B 待補砍；雙 runtime 審查進行中**。①gate：MUSE_USER_BUDGET=36*1024（BUNDLE_MAX_BYTES 旁）＋muse target 換接，TDD（RED→GREEN，26 passed）——即 advisory A' 形態。②瘦身（全改源）：guide 6,179→5,071B＋tool-discipline 3,883→3,252＋quality-constraints 3,568→3,181＋collaboration-constraints 3,272→2,921＋_ai-behavior-constraints 942→595（刪載入注＋重複 pointer 段——修今日 consistency scan G5）＋modern-cli-preference 刪載入注＋acceptance-evidence 刪「與既有規則的關係」闡述段。**部署面 40,092→36,856B（省 3,236B——低於 advisory floor 3,318B 差 82B、離 target 35,136B 差 1,720B）**；三部署檔 cmp 一致；Claude 端 rules/ 目錄 symlink 即時；mosaic 串接 62,341 ≤65,536（緩衝 3,195B）。③R8 九子項：review-engine :169 trigger-based（public/rename-delete/跨模組/negative claim 觸發面＋negative verdict 永不可 rg）＋agent-review-cycle :67 同步；implement snapshot「有 code diff 就跑」＋階段 6 delta_tour rename gate 觸發源；maintain Phase 1 降按需 prefetch（daily-maintain 同步；blueprint/scan-project/artifact-menu 為條件式 Fuel 非「必」掛名——判定不動）；consistency 無接線✓；cr-query project 行觀察窗；smell-detector YAGNI/dead-code verdict 三步；spec-miner 已有 prompt 明示✓；handoff :51 機械驗證（ls snapshots/）。④R5：corrections-weekly 換軌（penetration 降健康診斷、KPI 換 negative-claim CR 覆蓋率等、事件觸發主形態、cron 降 optional）；desc 同步。⑤drift 掃乾淨＋全 tests 288 passed＋check_single_source 10 invariants 綠＋rules/AGENTS.md :30 補 MUSE_USER_BUDGET 註記。⑥user 指示「改好給 muse codex 看看會不會刪太過頭」——兩 delegate-rescue 背景審查中（diff=.agent-tmp/air66-review/slim-diff.txt；verdict→muse/codex-verdict.md）。**下一步**：審查回收→findings 回補＋依 advisory 往 target 再砍（新刀口：outward-action-consent/python-standards/context-management 等審查範圍外肥段）→重部署驗收→post-build（docs-mode）→結案兩步。

〔CC 補充 09-10〕順手項：rules/model-routing.md external-runtime 段加一行 promotion——「外部 runtime 委派＝caller 背景 Bash 直呼 bridge，禁 subagent wrapper 承載；需接續的 background job 必掛 wait <jobId>」（always-on 層補洞——09-10 二輪顧問定案：禁令原本只住 on-demand skill，散發違規率 15%；~30B 計入本弧瘦身預算）。wrapper 退役（delegate-bridge repo 中型弧：/delegate 命令重寫直呼形態＋delegate-runtime skill 改寫＋s3s4 測試＋文檔×3＋dist）另行開工單，不併本弧。
<!-- SECTION:NOTES:END -->
