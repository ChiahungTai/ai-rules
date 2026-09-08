# Codex AGENTS.md 建議用法整理＋架構洞見

> Part A＝文檔忠實整理（來源：`ref-docs/harness/codex/` 內 `guides/agents-md.md`、`concepts/customization.md`、`learn/best-practices.md`、`skills.md`、`memories.md`；句句有檔可查，不摻推論）。
> Part B＝arch-thinking 視角洞見（三主線：依賴規則／bounded context／use case 驅動；其中可機械驗證者已驗，推論標 `open`）。
> 姊妹篇：`2026-09-08-codex-philosophy-instruction-layering.md`（截斷調查＋處方；本篇是用法＋洞見，不重疊）。

---

## Part A：Codex 建議用法整理

### A1．五層互補，不互斥（`concepts/customization.md`）

> "These are complementary, not competing."

| 層 | 職責 | 我方對應物 |
|---|---|---|
| AGENTS.md | shapes behavior（每次必守） | rules/ bundle |
| memories | carry local context forward | 三家 memory（機制各異，見 A6） |
| skills | package repeatable processes | skills/（8 組 rule+skill 分層） |
| MCP | connects outside systems | code-reality 等 |
| subagents | delegate noisy/specialized tasks | Writer/Reviewer、Task 派發 |

官方 build 順序：AGENTS.md（＋pre-commit hooks/linters 強制）→ plugin（有現成先裝）→ skill（無才自建，建完可打包成 plugin 發布）→ MCP（工作流需外部系統才接）→ subagents（最後）。

### A2．Keep it small＋feedback loop（`customization.md`「AGENTS Guidance」）

- 只放「每次在 repo 都要守」的：build/test 命令、review 期待、repo 慣例、目錄指示。原文："Keep it small."
- **犯兩次才 codify**：mistake repeated→加 rule；讀太多文件→加 routing guidance；同樣 PR feedback 出現兩次→寫死。不是預先寫全。
- 放**最近的目錄**（guidance in the closest directory where it applies），叫 agent 自己更新 AGENTS.md（fix persists，future sessions inherit）。
- 配**強制基礎設施**：pre-commit hooks、linters、type checkers 在 agent 之前攔——"so the system gets smarter about preventing recurring mistakes"。

### A3．Global vs repo 分工

- Global（`~/.codex/AGENTS.md`）：**你這個人**的預設——溝通風格、verbosity、跨 repo 偏好。
- Repo（root＋nested）：團隊＋codebase 規則。越深越贏（deeper wins by position，串接時後出現）。
- 我方現況對照：bundle 把「跨 harness 通用紀律」全塞進相當於 global 的位置（79KB），repo 層（ai-rules 12.5KB）在 muse 上 0 bytes——**層級倒置**：global 臃腫、repo 餓死。

### A4．太大時的官方處方（三選一，都不是硬壓）

1. **Raise the limit**（`project_doc_max_bytes`，預設 32KiB combined；我方已調 102400，TOML 過，未驗 runtime 認）。
2. **Split across nested directories**（拆到子目錄，chain 機制天然支援）。
3. **Reference task-specific markdown files**（`best-practices.md` 原話；agent 循引用讀，非機械展開）。

另有管理機制：`AGENTS.override.md`（臨時覆蓋不刪底檔——probe/實驗借用）、`project_doc_fallback_filenames`（認養異名檔）、`CODEX_HOME` 分身（automation 專用 profile）。

### A5．Skills 是 authoring format，plugin 是發布單位

- Skill＝`SKILL.md`（`name`＋`description` 必填）＋scripts／references／assets；repo skills 放 `.agents/skills`，個人放 `$HOME/.agents/skills`。
- **Progressive disclosure**：初始只進 metadata（全表 ≤2% context 或 8K chars，人多時先縮 description、再多則省略＋warning）；選中才讀全文；references/scripts 用時才動。
- "Clear skill descriptions improve triggering reliability."——description 是觸發器，寫爛等於沒有。
- Skill＋MCP 組合：skill 定義流程並點名 MCP 工具；依賴宣告在 `agents/openai.yaml`。

### A6．Memory 自動生成（與兩家對照）

Codex：extraction／consolidation 雙模型背景生成，住 `~/.codex/memories/`，`/memories` 管，secrets 自動 redact（仍警告勿存）。對照：muse 手寫 index（MEMORY.md＋路徑≤48，untrusted 照載）／ZCode 治理（一句話測試＋rank＋蒸餾）。**三家 memory 都是獨立 lane，不進 rules_file 預算**——瘦 bundle 時 memory 規範的「寫入端」是第一個可疑對象（muse 在 ai-rules 唯讀政策下整段死重）。

### A7．Verify your setup（官方驗收手段）

- `codex --ask-for-approval never "Summarize the current instructions."`（覆述探針官方版）。
- `codex -c log_dir=./.codex-log` 看 TUI log；`session-*.jsonl` 稽核載入。
- Chain 每 run／每 TUI session 重建，**無 cache 可清**（stale 先懷疑目錄／override 殘留）。
- Troubleshoot 條目承認截斷是常見態："Instructions truncated: Raise `project_doc_max_bytes` or split large files"。

---

## Part B：arch-thinking 洞見

### B1．依賴規則：我方 bundle 是「分層塌縮」

Codex 五層依賴向內：AGENTS（行為契約）→ skills（流程）→ MCP/scripts（執行），metadata discovery 保證外層內容不預載。**我方 bundle 把 skills 層的 reference 內容 inline 回 AGENTS 層**——等於 adapter 住進 domain，依賴方向反了。截斷不是容量事故，是結構事故：分層塌縮後，單一 64KiB lane 被迫承載三層內容。處方不是「壓字數」，是「恢復分層」（A5 的下沉即此）。

### B2．bounded context：scope 標註 × 目錄層級正交

Codex 用**目錄位置**做 context 邊界（global／repo／nested，deeper wins）；我方用 **`harness-scope` frontmatter** 做邊界（neutral／claude-specific／…）。兩種邊界正交、可並存成矩陣。muse 變體＝只在 scope 軸切（per-target scope set，`read_scope`／`discover_rules` 現成機制延伸），不動層級軸（不拆目錄、不動 chain）。**切 scope 不切層級**——這是 A 案「變體＝標註非分岔」主張的結構表述。

### B3．use case 驅動：cut set 的原則性判準

B2 回答「在哪切」，use case 回答「憑什麼留」。消費者＝muse sessions：有界 task＋自足工單。判準：**一條 rule 是否跨工單**——跨工單的留 bundle（uv run、sed 禁令、Read-before-Edit、no-pipe-gate、fail-loud），工單可自帶的走（單次任務的流程、harness 機械、寫入端規範）。這比 draft-3 的「muse 用不用得到」精準：tool-discipline 通用節跨工單（留），背景執行節是 harness 機械（走）；context-management 糾正／落盤原則跨工單（留），`/clear`／STATE.md／memory 寫入端（走）。**判準本身只有 5 行，可寫進部署紀律**，後續 rule 增刪不再憑感覺。

### B4．共用層外溢：B 案的架構級否決

arch-thinking §一③：多 context 共用層改語意＝強迫所有消費者妥協。B 案（全域瘦身）正是此反模式實例：ZCode（100K 預算充足）被迫為 muse／codex 的 cap 陪瘦，四家妥協於同一語意。**改消費端各取所需（per-target variant），不改共用層**——A 案的架構級論證，與 token 數學無關，即使 B 案字數上可行仍否決。

### B5．先查既有：現成機制優先於新發明

既有：per-target `--scope`（已在 `deploy_agents.py`）、rule+skill 分層（8 先例）、bundle-skip markers、Codex knob、`AGENTS.override.md` probe 法。**新發明只有一個**：per-target slimming（單條 rule 對 muse 更瘦、對別家照舊）——目前無機制承載，排序最後。執行序：scope 切（現成）→ knob（現成，codex 已做）→ 下沉（先例）→ per-target slimming（新發明，不到萬不得已不做）。

### B6．方法論限制（本報告誠實段）

- 文檔引用：以 `ref-docs/harness/codex/` 鏡像為準，未對線上原文（crawl 時點漂移可能；manifest 可查）。
- Loader 實測：muse 側（diagnostics＋cli log，09-07/08 sessions）；Codex 側**零實測**（knob 調整僅 TOML 解析通過，chain／cap 行為全引文檔）。
- 推論（`open`）：framing 殘差約 1KB（未釘死，已吸收進 margin）；mosaic 級 project 鏈 out of scope 判定基於靜態尺寸，未實測。
