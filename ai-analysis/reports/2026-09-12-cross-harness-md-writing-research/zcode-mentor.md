# ZCode 提取覆核報告（codex mentor，job job-mtyhlihc-z2t0fx）

## 1. 總判：提取可信度**高**（抽驗 10+ 條 claim 均與鏡像逐字吻合；未發現已列引文斷章取義）

## 2. confirmed（抽驗通過）

- `cn/docs/agents.md:66,71,72,78` — OK（啟動讀取、全域→Workspace 拼接、CLAUDE.md 一次性遷移、不合併多層/不掃子目錄/不展開 import/不依任務選規則檔，逐字吻合）
- `cn/docs/memory.md:53-54` — OK（自動提取時機與專案隔離）
- `cn/docs/skill.md:45,59` — OK（技能定義；description 1024 上限超出整顆丟棄）
- `cn/docs/subagents.md:74,69` — OK（定義檔 frontmatter Markdown 正文即系統提示詞；description 影響選用）
- `cn/docs/hooks.md:36,58` — OK（stdin JSON 協議；專案級 Hook 整體忽略＋`config_project_hooks_ignored`）
- `cn/docs/commands.md:62`、`cn/docs/plugin.md:169` — OK

## 3. corrected：無

（未發現：引用不存在／行號截斷語意反轉／「官方未支援」誤寫「未提及」／把 reverse engineering 偽裝官方內容）

## 4. missing（建議補入，不影響七軸主結論）

- `cn/docs/commands.md:62`——Command 本身的建立定位（簡單 prompt 保存用 Command；帶腳本/模板/範例/完整流程用 Skill）→ 補軸 4/軸 7
- `cn/docs/plugin.md:169-182`——Command frontmatter 有 `allowed-tools`（逗號分隔限制命令可用工具），與 Skill 白名單無此欄位形成對照：兩者不是同一 metadata 模型
- `cn/docs/plugin.md`——Plugin 作為分發邊界可攜帶 skills、commands、hooks 組合能力；團隊共享機制是 plugin package 層（不只是 Skill 分發）

## 5. 偽陰性反查（抽 3 條，全部未推翻）

- 「AGENTS.md 尺寸/截斷未提及」——未推翻（skill.md:60 的 100KB 是 SKILL.md 正文限制）
- 「SKILL.md 無 model/allowed-tools 欄位」——未推翻（plugin.md:169 顯示 allowed-tools 屬 Command）
- 「無獨立 rules 機制」——未推翻（agents.md:78 明文支持）

## 補充觀察

- 「工作區級 subagent 不支援」「專案級 Hook 不執行」非偽陰性，官方明文
- 提取對「官方文檔 vs ai-rules 實測 reverse engineering」界線處理良好（AGENTS 100KiB 那段標示保留）
