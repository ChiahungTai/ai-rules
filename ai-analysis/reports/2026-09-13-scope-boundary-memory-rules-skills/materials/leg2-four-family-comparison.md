# 腿 2：四家 harness 對照——user-level AGENTS.md 消費 / skills 觸發 / memory

> 產出者：spec-miner（glm-5.3-flash），2026-09-13。來源＝`ai-analysis/reports/2026-09-12-cross-harness-md-writing-research/` 十檔＋`ref-docs/harness/` 鏡像補查。

**來源縮寫**：CCX=`claude-code-extraction.md`、CDX=`codex-extraction.md`、MUX=`muse-extraction.md`、ZCX=`zcode-extraction.md`（均在 reports/2026-09-12-cross-harness-md-writing-research/）。錨點內 path:line 為 extraction 已實測的鏡像相對路徑。〔鏡像補查〕＝本次直接查 `ref-docs/harness/`；〔實測〕＝ai-rules 反組譯事實（synthesis-draft §2.2/§3d 引 `rules/AGENTS.md`），非官方文檔。

## 表 1　軸 1：user-level AGENTS.md（instruction）消費

| 家 | 全域路徑 | 載入時點 | 掃子目錄 | 尺寸/截斷 | 與專案層合併 |
|---|---|---|---|---|---|
| **Claude Code** | `~/.claude/CLAUDE.md`；原生只讀 CLAUDE.md 不讀 AGENTS.md，橋接靠 `@import`/symlink（CCX；`docs/en/memory.md:59,129`） | cwd 以上層級 launch 時載入；project-root 檔 `/compact` 後從磁碟重讀重注入（`memory.md:63,462`） | 是，但分向：上層 launch 載、**子目錄 lazy**（首次讀該目錄檔案時）（`memory.md:63`） | 每檔 200 行軟目標；>4 MiB 整檔跳過不載（`memory.md:81,405`） | **concatenate 不覆蓋**：全部串接、root 往下排序；user rules 先載、project 優先權較高（`memory.md:157,269`） |
| **Codex** | `~/.codex/AGENTS.override.md` 否則 `AGENTS.md`，首個非空檔（`CODEX_HOME` 可改 home）（CDX；`agent-configuration/agents-md.md:11`） | run 啟動建 instruction chain（TUI 每 session 一次）；session 首回合注入限量 project guidance（`agents-md.md:9,206`＋`config-file/config-advanced.md:744`） | project 層 walk-down：root→cwd **路徑上**每目錄收一檔，非全樹掃描（`agents-md.md:12`） | `project_doc_max_bytes` 預設 **32 KiB 停加**；config-reference.md:1170 另有 per-file 描述，兩處並存鏡像未調和（`agents-md.md:15`） | **concatenate**：root 向下空行串接，靠近 cwd 者排 prompt 較後＝實質覆蓋（`agents-md.md:13`） |
| **Muse** | user rules「machine-wide always load」，**路徑官方未文檔化**〔鏡像補查：`muse-code/configuration.md:46` 僅此一句，全檔無路徑〕 | 官方未載明確時點；定位僅「always load」（MUX；`muse-code/configuration.md:46`） | 是，但 **walk-up 制**：workspace root 向上至最近 `.git` 邊界，每層四檔（AGENTS.md→CLAUDE.md→.agents/→.claude/）首命中勝出（`configuration.md:41`） | 鏡像未載；〔實測〕delegation startup 共享 65,536 bytes 截斷＋警告（synthesis-draft §2.2） | **wins 替換非合併**：project 勝 user、深層勝淺層；project 檔須先 trust workspace（`configuration.md:43-44,46`） |
| **ZCode** | `~/.zcode/AGENTS.md`（qa 定位「全局规则」）（ZCX；`cn/docs/agents.md:69`＋`qa.md:112`） | 啟動任務時讀取（`agents.md:66`） | **明文不掃**：不合併多層、不掃子目錄、不展開 @import/@include、不依任務選規則檔（`agents.md:78`） | 官方未載；〔實測〕100 KiB/檔 硬編碼讀前截斷（synthesis-draft §2.2/§3d） | 兩檔串接：全域前、workspace 後（workspace＝主要專案來源）；僅此兩檔無其他合併語義（`agents.md:71,78`） |

## 表 2　軸 2：skills 觸發機制

| 家 | 觸發方式 | 載入深度（progressive disclosure） | 觸發時載入什麼 |
|---|---|---|---|
| **Claude Code** | slash 叫用＋Claude 判定相關（CCX；`docs/en/memory.md:182`）；`paths` frontmatter 限定匹配檔案時才自動載、nested `.claude/skills/` 延遲載（`docs/en/skills.md:351,167`） | 兩層：listing（name＋desc/when_to_use 合併截 1,536 字元；預算＝context window 1%，溢出從最少用 skill 開始丟 desc、name 永遠全列）→ 選中全 body（`skills.md:337,1052`） | 全 SKILL.md body，**跨 turn 常駐 context**；<500 行軟目標、詳細參考移支援檔（`skills.md:311,472`） |
| **Codex** | explicit（`$skill`／`/skills`）＋implicit（任務匹配 description；`allow_implicit_invocation` 預設 true 可關）（CDX；`build-skills.md:215`） | 明文三層 progressive disclosure：metadata（name/description/路徑）→ 選中讀 SKILL.md → 按需 references/scripts（`build-skills.md:33`＋`customization/overview.md:130-132`）；初始清單預算 2% ctx 或 8,000 字元、超量先縮 desc 再省略（`build-skills.md:38`） | 選中才讀全 SKILL.md；預算只限初始清單（`build-skills.md:43`） |
| **Muse** | slash 快捷鍵明確調用＋背景 skill-recall observer 提案〔鏡像補查〕：「The agent can also load a relevant skill when a background observer surfaces one」（MUX；`muse-code/extending.md:75`） | 「load on demand」確認（`extending.md:55`）；disclosure 層級**材料未涵蓋** | 觸發時載入內容**材料未涵蓋**（frontmatter 欄位契約未文檔化——MUX 未提及清單軸 4） |
| **ZCode** | **元數據每輪注入**所有已啟用技能（名稱＋描述摘要 ≤250 字元/條，全部共享一固定預算；超載降級只留名、自動觸發率明顯下降）（ZCX；`cn/docs/skill.md:62`）；觸發靠 description 寫清「什麼時候用」、越具體越可靠（`skill.md:66`） | 元數據每輪常駐＋body 按需（`skill.md:62`）；無中間 disclosure 層記載 | 觸發時載 SKILL.md 正文（>100 KB 截斷載入，`skill.md:60`）；frontmatter 必填 name+description，缺＝整技忽略＋診斷；description>1,024 字元**整技丟棄非截斷**（`skill.md:58-60`） |

## 表 3　軸 3：memory 機制

| 家 | 原生 auto-memory | 開場注入 | 寫入路徑 |
|---|---|---|---|
| **Claude Code** | 有，預設開；與 CLAUDE.md 並列兩互補系統、每次對話開頭載入（CCX；`docs/en/memory.md:23`） | MEMORY.md 索引前 200 行或 25KB（先到者）；topic 檔不在啟動載、按需讀（`memory.md:401,407`） | 對話說「remember…」Claude 存入 auto memory（plain md 人可編刪）；要進 CLAUDE.md 須明說（`memory.md:417,425`）；位置 `~/.claude/projects/<project>/memory/`，machine-local、同 repo worktree 共享（`memory.md:369,395`）；subagent 不繼承（fork 例外，`memory.md:409`） |
| **Codex** | 有但**預設關**（`[features] memories=true`）（CDX；`customization/memories.md:118,124-125`） | `memories.use_memories` 開啟時注入未來 session；注入格式/數量**材料未涵蓋**（`memories.md:136`〔鏡像補查確認無細節〕） | generated state 禁手編當控制面：`~/.codex/memories/`（summaries/durable entries/recent inputs/evidence）；背景 idle 才寫、跳活躍短 session、redact secrets、rate-limit 低於門檻跳過（`memories.md:89,92,71-79`） |
| **Muse** | 有，三 scope：personal-project（預設機器上 repo 外）／project（`.agents/memory/` 進 repo）／personal（機器級）（MUX；`muse-code/configuration.md:93-97`） | 開場只注入**索引**：MEMORY.md＋其餘檔路徑清單（非內容），上限 48 檔（`configuration.md:114`）；memory-recall observer 可於回合前插入相關筆記（MUX 軸 5） | 寫入 API/閘官方未文檔化（MUX 未提及清單軸 3）；沙箱內 `.agents` 唯讀＝agent 不能改自己 memory（`permissions.md:77`）；committed project memory **未信任 workspace 也載**＝官方明標 prompt-injection 面（`configuration.md:110`） |
| **ZCode** | 有但**預設關**（v3.6.4+，設置開啟）（ZCX；`cn/docs/memory.md:38`） | 後續 session 索引自動載入 context〔鏡像補查：`memory.md:54`「在同一项目的后续会话里，索引会自动加载进 Agent 的上下文」〕；索引有大小上限、過多截斷（`memory.md:65`） | 每輪成功結束後台自動提煉（一條事實一檔＋更新 MEMORY.md，`memory.md:53`）＋對話自然語言增刪（`memory.md:37`）；位置 `~/.zcode/cli/memories/projects/<project>/memory/`（`memory.md:57-60`）；主對話專用、subagent 不讀不寫（`agents.md:91`） |

## 材料未涵蓋清單

1. **Muse user-level instruction 檔路徑**——已鏡像補查確認官方零記載（僅 configuration.md:46 一句）。
2. Muse instruction 載入時點（session 啟動 vs 每 turn）官方未明載。
3. Muse skill disclosure 層級與觸發時載入內容（frontmatter 契約未文檔化）。
4. Muse memory 寫入 API/治理閘官方未文檔化（ai-rules 的 inbox 治理即建立在缺口上）。
5. Codex memory 開場注入格式/數量（只有 `use_memories` 開關）。
6. Codex 32 KiB 是鏈合計還是 per-file：`agents-md.md:15` vs `config-reference.md:1170` 兩描述並存未調和。
7. ZCode memory 索引截斷具體數值（官方僅「有大小上限」；25,000 字元屬 contracts.md 反組譯實測）。
8. Muse AGENTS.md 尺寸限制官方零記載（65,536 bytes 實測屬 delegation startup 場景，是否等同一般 instruction 載入未證實）。

## 對「scope 分界研究」的機制含義

- **always-on 全量注入（rules 放多胖都吃 token）＝四家皆是**：instruction bundle 全部 always-on 全量——CC launch 全 concatenate（僅 4 MiB 整檔跳過）、Codex run-start 建鏈（32 KiB 停加）、Muse user＋trusted project 全檔、ZCode 兩檔全載。差異只在超限後果：CC 漸進退化（adherence 降、無聲）、Codex 鏈尾停加（最 specific 的近端檔最可能被排掉）、ZCode 尾部靜默截斷（實測 100 KiB，141KB 事故實證）、Muse 未載。
- **真 on-demand 觸發（skills 放深不佔開場）＝CC/Codex/Muse 三家成立**：初始只佔 listing（name+desc），body 選中才載。**ZCode 是半例外**：body 雖 on-demand，但元數據**每輪注入**（非一次性 listing）且共享固定預算——技能多了每 turn 都吃 token、超載後自動觸發率明顯下降，「只啟用常用技能」是官方處方。
- **中間層（rules-bundle）只有 CC 有原生機制**：`.claude/rules/` 無 `paths`＝always-on、有 `paths`＝檔案匹配 on-demand，是唯一內建的三段式（always-on rule／path-scoped rule／skill）。Codex 的 rules 是 Starlark exec policy（與 instruction 生態零耦合）、ZCode 明文無、Muse 名存實無——「核心 rule＋pointer＋skill 深層」的分層在 CC 以外三家只能用 skill 模擬或留在 always-on。
- **memory 端四家都有原生機制，但寫入拓撲截然不同**：CC/ZCode＝對話寫入＋人可手編（開放寫入面、索引注入＋條目 on-demand）；Codex＝generated state 禁手編（封閉寫入面）；Muse＝agent 沙箱唯讀＋寫入閘官方缺口（且 committed memory 未信任也載，是唯一帶 prompt-injection 警示的 memory）。把「經驗事實」從 rules-bundle 抽到 memory 的 scope 分界，寫入端約束須分家設計；另注意 CC/ZCode 的 subagent 都讀不到主對話 memory（委派 session 工單必須自含）。
