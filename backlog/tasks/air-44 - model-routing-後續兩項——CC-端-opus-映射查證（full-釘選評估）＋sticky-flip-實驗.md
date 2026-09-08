---
id: AIR-44
title: model-routing 後續兩項——CC 端 opus 映射查證（full 釘選評估）＋sticky flip 實驗
status: To Do
assignee: []
created_date: '2026-09-08 01:42'
updated_date: '2026-09-08 02:19'
labels:
  - governance
dependencies: []
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
〔baseline：ai-rules 508f4a9〕〔已決策勿重辯：①來源＝AIR-43 EP 後續項（done/09-08-model-vocab-governance）弧外登記，AIR-43 已全弧閉環②CC 查證方法＝CC session spawn 後 transcript rg '"model"' 實測 opus 別名→GLM 映射（agent-workflow Step 1 表 :57 仍列 glm-5-turbo 舊值＋缺 glm-5.3 列，未查證前 CC 端維持 inherit 不釘）③sticky flip＝SKILL.md:68 既有待跑項——AIR-43 S3 已得數據點（variant=max、定義 high 不達 wire、全 agent 一致 max），flip 實驗分辨 sticky override vs silent no-op（改 user reasoningLevel≠定義值再 spawn 看 variant 跟隨否）〕〔驗收：agent-workflow Step 1 表更新為實測值或標註未查證；flip 結果（override/no-op 判定）回寫 SKILL.md:68 但書段＋platform-facts〕
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CC 映射表實測更新；flip 判定回寫但書段
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
【09-08 進展】①CC opus 映射查證✅：定義源＝~/.claude/settings.json env（ANTHROPIC_BASE_URL=z.ai 相容端點）——opus→glm-5.3[1m]、sonnet/haiku→glm-5.3-flash[1m]，走 GLM 額度非 Anthropic 訂閱；agent-workflow Step 1 表＋model-routing 解析表 Anthropic 欄＋dispatch 段已同步更新（commit 見後）。殘餘＝CC 端釘選設計決策（claude 投影 full-tier 可釘 model: opus 別名——補完 inherit 洞雙 harness 修補；涉 sync_agents CC 投影改動）待 user 拍板。②sticky flip 未動。

【09-08 flip 實驗②完成】直寫 local_setting DB 改 user level=max→low，同 session spawn lite-verify（定義 high）：variant=max（舊快取值，非 low 非 high）——定義值 silent no-op 確認；spawn 不逐次重讀 local_setting（app 快取 session 起始值）；殘餘＝UI 動態改是否傳播（DB 實驗無法回答，需 user UI 級操作）。結果已回寫 SKILL.md:68 但書段＋platform-facts。

【09-08 CC 別名釘選落地（user 拍板＋可攜性確認）】CLAUDE_PINS={'full':'opus'}＋_ANTHROPIC_ALIAS_RE parity guard＋render claude 分支；TDD 3 RED→32 passed；生成物 agents/claude/code-reviewer{,-primed}.md 帶 model: opus（lite/vision 對照無）；設計要點＝釘別名非釘 id——env 映射切 provider（glm-5.3↔真 opus↔fabel）時 alias 直接可用免重釘；文檔四處同步（部署填法表/rules×2/agents AGENTS）＋bundle 重部署四家
<!-- SECTION:NOTES:END -->
