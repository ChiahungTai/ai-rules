# Codex 提取覆核報告（codex mentor，job job-mtyhp0nr-rxtzrf；首派 job-mtyhnde1-ecfuuo 撞 at capacity，重試成功）

## 1. 總判：提取可信度**高**（抽驗 10+ 條 claim 與鏡像一致；未發現偽造引文或斷章取義；少數「提取者推論的強化描述」需保留語氣限制）

## 2. confirmed（抽驗通過，12 條）

- `agent-configuration/agents-md.md:9,13` — OK（instruction chain 每次 run 建構；root-down concatenate）
- `config-file/config-reference.md:1170` — OK（`project_doc_max_bytes` per-file 描述存在）
- `agent-configuration/rules.md:5,135` — OK（rules＝sandbox 外 exec policy；Starlark）
- `customization/memories.md:5`、`build-skills.md:33`、`agent-configuration/subagents.md:399`、`hooks.md:82`、`prompting.md:28,311`、`custom-prompts.md:5` — OK

## 3. corrected（無引文錯誤；兩處措辭收斂）

- negative claim 措辭：「rules.md 全檔零次 instruction」這類是**掃描結果**非文件事實——應標「截至目前鏡像搜尋未命中」，勿理解成官方明文宣告
- 「instruction 只在 session 首回合注入」保留原文限定：鏡像確認的是「includes a limited amount of project guidance in the first turn」，不代表任何時刻永遠只注入一次

## 4. missing（歸位建議）

- `config-file/config-basic.md:37`——untrusted project 跳過整個 project-scoped `.codex/` layer（config+hooks+rules）——安全邊界值得獨立列為設定模型機制（提取埋在 config precedence）
- `customization/overview.md:42`——「Pair AGENTS.md with infrastructure that enforces those rules」也是寫作落地指導：AGENTS.md 管 guidance、工具鏈管 enforcement（提取歸在建置順序）
- `prompting.md:17-23`——Goal/Context/Output/Boundaries 是官方推薦**分解模型非 schema**（「Use only the parts that help. You don't need to fill in every item or follow a required format.」）——防使用者把四欄當模板

## 5. 偽陰性（抽查 3 條，全部未推翻）

- 「AGENTS.md 無 frontmatter/schema 規格」——未推翻（agents-md.md 搜 frontmatter 未命中）
- 「rules 與 instruction 生態無橋接」——未推翻（rules.md 搜 instruction 未命中）
- 「subagent 無 markdown manifest 格式」——未推翻（custom agent＝standalone TOML 確認）

## 整體判定

可作為 Codex harness 機制摘要使用；後續只修 negative claim 措辭——把「未命中鏡像」與「官方沒有此機制」分開。
