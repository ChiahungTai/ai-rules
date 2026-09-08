---
id: DRAFT-3
title: muse AGENTS 64KiB 截斷——bundle 瘦身兩案裁決（專用變體 vs 全域）
status: Draft
assignee: []
created_date: '2026-09-08 10:15'
labels:
  - muse
  - deploy
  - governance
dependencies: []
---

# muse AGENTS.md 64KiB 截斷——bundle 瘦身裁決

user 已定向「要修——muse/ai-rules 側瘦身」（09-08）；本 draft 攤裁決材料：**A 專用變體 vs B 全域瘦身**（C 退出已被 user 方向排除，僅記完整性）。

## 事實（09-08 實測，機械證據）

- **muse user-rules context block 上限 = 65,536 bytes（64KiB），靜默截斷**：
  - 檔案 ≤ 上限 → 全載（09-07 邊界探測：65,534B 檔案 block=65,534）
  - 檔案 > 上限 → block 恰 65,536（09-08 三個 post-deploy task sessions 皆 `text_bytes: 65536`，檔案 79,271B）
  - 證據源：`~/.local/share/muse/sessions/<date>/<id>/session.jsonl` 的 `context_block_diagnostic`（`block_id=rules_file`）；diagnostics 不警示、官方文檔（ref-docs/harness/meta/muse-code/configuration.md）未載此上限
- **現值 bundle = 79,271B**（ai-development-guide 10,588 + 16 條 rules 68,447 + wrappers 941；與 repo HEAD 逐檔加總一致），超上限 13,735B。~~memory 記 92KB、user 轉述 123KB~~ 皆過時/無對應實物（歷史高點 141KB＝6fa0184 分層前）
- **被切掉的尾巴**：quality-constraints.md 中段起（marker @63,912，只活前 ~1.6KB——漸進式驗證／消費端驗證／fail loud 全滅）＋ **tool-discipline.md 全部**——即 muse 每個 task session（含 bridge 審查 task）都在缺這兩段的 context 下工作
- **deploy gate 失防**：`BUNDLE_MAX_BYTES=90KiB` 只對齊 ZCode 100KiB 截斷；muse 64KiB 未入 gate（script 註解僅記 ZCode；OpenCode/Codex 上限仍未驗）
- **memory 修正**：「主 session 載入完整、只有 subagent 截」為 09-07 檔案（53,701B）< 上限時的探測結論——09-08 實測 task session 主體同截（rules_file block 本身 65,536）

## 兩案

### A. muse 專用變體（scope 過濾）——建議

以既有 `harness-scope` frontmatter 機制（script 已有 `read_scope`/`discover_rules`）擴充 scope 值，排除 muse 用不到的 harness-mechanics rules：

| 排除候選 | bytes | muse 為何用不到 |
|--|--|--|
| tool-discipline | 7,663 | 背景spawn/TaskOutput/batch——ZCode 機械 |
| symbol-query-routing | 4,529 | cr-first 路由紀律——muse 經 bash 可用 CR CLI（PATH 有 binary，非無法用）；排除理由＝always-on 路由對工單型任務溢價，符號查證由工單按需指名。若裁定 muse 審查高頻需要 callers 查證→放回（代價 4.5KB，bundle 61.2KB 貼 60KiB 線） |
| model-routing | 4,432 | agent tier 派發——本 session 職責 |
| context-management | 3,401 | /compact/STATE.md——headless 無此面 |
| instruction-writing | 2,575 | muse 不寫我們的 instruction 檔 |

→ muse bundle ≈ 56.7KB（headroom ~8.8KB）。rules/ 單一源不變（變體＝scope 標註，非內容分岔）。

### B. 全域瘦身 ≤60KiB

共享 bundle 再砍 ~19KB（141→91.8→79 之後第四輪）——reference 分層第二輪（rule body 下沉 skills；muse 經 `~/.agents/skills` symlink 可 on-demand 讀，skills_catalog block 實測 31.6KB 未截）。四家 all-in 變薄；ZCode/CC 的預算空間（100KiB／無上限）陪葬。

### C. 退出 TARGETS（已排除）

省每 task ~17K tokens（訂閱加總計費面），但 muse 全域行為紀律歸零、全靠工單自足。user 已說「要修＝瘦身」，非退出。

## 建議與配套（A/B 皆做）

- **建議 A**：muse 的委派角色（有界 task＋自足工單）本來就不吃那些 harness mechanics；A 內容零損失，B 要四家一起付內容成本
- per-target budget gate（muse 60KiB、其餘維持 90KiB）＋ script 註解修正（「只有 ZCode 截斷」已過時）
- **lane 合流語義（09-08 bridge review 副產品，強證據）**：bridge stderr warning 明載 `rules file at ~/.config/muse/AGENTS.md produced 92940 bytes, over the 65536 byte subagent delegation startup context limit`——檔案實為 79,287B，produced 92,940B（**+13,653 ≈ ai-rules 專案層 AGENTS.md 12,550B＋~1.1KB 包裝**）→ user/project 兩層**串接**進單一 rules_file lane、共享 64KiB。意涵：**muse 變體的 user bundle 上限 ≈ 65,536 − 專案層 − ~1.1KB（ai-rules 工作區 ≈ 51.9KB）**——A 案 5 條排除後 56.7KB 在 ai-rules 工作區仍超線，需更深篩選（≤50KB）或改 B 案。殘餘待驗：wrapper 1.1KB 構成（交互 probe 收尾）。另：截斷有 loud stderr warning，非全靜默（消費端不重導 stderr 即漏）
- drift 掃描：`rg "90KiB|BUNDLE_MAX"` 全 repo 引用面（rules/AGENTS.md 部署紀律段等）
- 部署後驗收：實測新 task session 的 `rules_file text_bytes` == 檔案大小（全載）
- （B 路線加做：bundle-watch advisory 每週組成分析的 baseline 更新）

## 驗收

- muse bundle ≤60KiB 且部署後實測全載（text_bytes == 檔案大小）
- 其餘三家 bundle 內容不變（A）或如規劃變薄（B）、各自 gate 綠
- 引用面同步：memory（muse-code-cli-facts 已於本弧修正）、rules/AGENTS.md 部署紀律段
