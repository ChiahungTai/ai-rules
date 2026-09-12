# Claude Code 提取覆核報告（codex mentor，job job-mtyhlif2-f6l1mt）

## 1. 總判：提取可信度**高**（抽驗 claim 與鏡像大多一致；少數「未提及清單」判定需修正——skill/agentskills 相關遺漏）

## 2. confirmed（抽驗通過，12 條）

- `docs/en/memory.md:129,157,97,81,199,23,401` — OK（CLAUDE/AGENTS 關係、concatenate 載入、import 四層、200 行是 target、rule 啟動載入、context 非 enforced、MEMORY.md 200 行/25KB）
- `docs/en/skills.md:328,16,472` — OK（frontmatter 全 optional、commands 併入 skills、SKILL.md 500 行）
- `docs/en/sub-agents.md:27` — OK（description 15,000 tokens 警告）
- `docs/en/hooks.md`（經 best-practices 引用）— OK（hooks 與 CLAUDE.md advisory 差異）

## 3. corrected（一處表述收斂）

- 軸 4「官方把 eval 外包…因此未提及」不成立——`docs/en/skills.md:804-827` 有完整「Run evals with skill-creator」章節＋指向 agentskills.io 評估文檔。正確寫法：「核心 runtime 沒有內建 skill quality score；官方提供 skill-creator eval workflow 與 agentskills.io 評估規範」

## 4. missing（鏡像有但提取漏）

- `docs/en/skills.md:19`——Claude Code skills 遵循 Agent Skills open standard（跨工具）；skill 架構定位背景
- `docs/en/skills.md:359-374`——frontmatter 欄位分兩層：Agent Skills standard fields vs Claude Code extension fields（「Outside Claude Code, you can use only the fields in the Agent Skills spec」）——影響跨工具可攜性
- `docs/en/skills.md:680-703`——`context: fork` 使 skill 直接以 subagent context 執行（不帶對話歷史）；`background` 控制等待行為——skills 與 agents 邊界行為
- `docs/en/sub-agents.md:590-619`——subagent `memory` 欄位給子代理獨立持久記憶目錄（scope user/project/local）——提取只述主對話 memory
- `docs/en/sub-agents.md:834`——custom subagent 的 system prompt「replaces the default Claude Code system prompt entirely」——prompt replacement 語義

## 5. 偽陰性（官方未提及清單反查）

- 「skill description 品質評分/自動驗證內建於核心未提及」——**部分推翻**（官方有 eval workflow 文檔：skills.md:804-827；修正為「runtime 無內建評分，官方提供 eval workflow 文檔」）
- 「Agent Skills 標準細節未提及」——**推翻**（skills.md:19、354-374 明確提及標準與欄位分層）
- 「subagent system prompt 行數/長度建議未提及」——仍成立（只有 description token budget＋「move detail into system prompt」）
- 「blog/agent-view 與寫作零相關」——未發現反例

## 整體判定

七軸事實摘要可通過；需修「官方未提及清單」邊界——避免把「runtime 沒有某功能」誤寫成「官方文檔完全沒談」。
