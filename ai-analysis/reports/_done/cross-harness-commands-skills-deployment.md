# 跨 harness Commands + Skills 部署設計

> **產出**：`/arch-thinking` 機械查證（3 agents 平行讀 OpenCode/ZCode/Codex/Claude 鏡像 + Gemini web）+ 設計視角綜合。
> **範圍**：Claude Code / OpenCode / ZCode / Codex / Gemini 五家的 commands + skills + context(AGENTS.md) + rules 部署。
> **狀態**：設計提案（grounded 於鏡像 file:line / web URL），待決策。非實作。

---

## TL;DR

1. **Skills 是跨 harness 可攜基質**。`.agents/skills/` 是 **Codex（native）+ OpenCode（compat）共讀**的 open standard 路徑 → 單一 source 最多 harness 的最大槓桿。
2. **commands → skills 是兩家官方收斂方向**：Claude「commands merged into skills，同名 skill 勝」（skills.md:16,110）；Codex custom-prompts 官方棄用 → skills，`/import` 把 `.claude/commands/*.md` map 成 **skills**（非 prompts）。長期靠 skills。
3. **commands 路徑家家分歧、無共用路徑**：Claude `.claude/commands/`、OpenCode `.opencode/commands/`（**不**掃 `.claude/commands/`）、ZCode `~/.zcode/commands/`、Codex 棄用、Gemini `.toml` only。需 per-harness 橋接。
4. **ai-rules 是單一 harness-neutral source，每 harness 用自家相容機制橋接**（依賴向內：adapter → core，core 不認識 harness）。
5. 🔴 **立即**：(a) rename 已弄斷 ZCode `~/.zcode/commands/claude/` ~21 個 symlinks；(b) Codex skills 一個 `~/.agents/skills/` symlink 即解鎖。

---

## 1. 查證事實：五家 carrier 支援矩陣

> 引用：OpenCode/ZCode/Codex/Claude = 本地鏡像 `ref-docs/harness/<src>/`（file:line）；Gemini = web（URL，2026-07）。

### 1.1 Commands（slash commands / custom prompts）

| Harness | 原生路徑 | 格式 | 讀 `.claude/commands/`? | 狀態 |
|---|---|---|---|---|
| **Claude Code** | `.claude/commands/*.md`（+ `~/.claude/commands/`）| md + frontmatter | native | merged into skills（legacy 仍可用）；**同名 skill 勝**（skills.md:16,110）|
| **OpenCode** | `~/.config/opencode/commands/` + `.opencode/commands/`（commands.md:77-78）| md + frontmatter（`description`/`agent`/`model`/`subtask`）| **否**（rg `compatible\|fallback` 0 hits）| stable；`$ARGUMENTS`/`$1`/`!cmd`/`@file` |
| **ZCode** | `~/.zcode/commands/*.md`（commands.md:48）| md（無 frontmatter 要求）| 否（僅手動 import）| stable；內建 `/goal` `/compact` |
| **Codex** | `~/.codex/prompts/*.md`（**僅 global**，custom-prompts.md:6,10）| md + frontmatter | 否（`/import` 一次性 → map 成 **skills**）| **🔴 棄用 → skills**（custom-prompts.md:3-4）|
| **Gemini** | `~/.gemini/commands/*.toml` + `.gemini/commands/` | **TOML only** | 否 | stable；`.md` 是 open FR（[#15535](https://github.com/google-gemini/gemini-cli/issues/15535)）|

**關鍵不對稱**：OpenCode 的 Claude 相容只及於 rules（AGENTS/CLAUDE fallback）+ skills（並列掃 `.claude/skills/`），**commands + agents 不相容**（OpenCode commands.md 無 `.claude/commands/` 路徑）。

### 1.2 Skills

| Harness | 原生路徑 | 格式 | 讀 `.claude/skills/`? | 讀 `.agents/skills/`? |
|---|---|---|---|---|
| **Claude Code** | `~/.claude/skills/<n>/SKILL.md` + `.claude/skills/` | SKILL.md（frontmatter 最豐）| native | （鏡像未提及）|
| **OpenCode** | `.opencode/skills/` + `~/.config/opencode/skills/`（skills.md:11-16）| SKILL.md（`name`+`description` 必填）| **是**（compat）| **是**（compat）|
| **ZCode** | `~/.zcode/skills/<n>/SKILL.md`（skill.md:41）| SKILL.md（範例 `name`+`description`）| 否（手動 import；**import 支援 symlink 或 copy 雙選**，skill.md:51-60）| （未提及）|
| **Codex** | **`.agents/skills/`** + `~/.agents/skills/`（skills.md:96-102，**非 `~/.codex/skills/`**）| SKILL.md（[agentskills.io](https://agentskills.io) 標準）| 否（`/import` 一次性 `.claude/skills/` → `.agents/skills/`）| **native** |
| **Gemini** | `.gemini/skills/<n>/SKILL.md` | SKILL.md（對稱）| 否 | （未提及）— **experimental**，需 `experimental.skills: true`（[docs](https://geminicli.com/docs/cli/skills/)）|

**★ 最大槓桿**：`.agents/skills/` 同時被 **Codex（native）+ OpenCode（compat）** 讀 → 一個落點覆蓋兩家。

### 1.3 Context 檔（AGENTS.md / CLAUDE.md / GEMINI.md）

| Harness | AGENTS.md | CLAUDE.md | 其他 |
|---|---|---|---|
| Claude Code | 否（可 `@AGENTS.md` import）| **native** | — |
| OpenCode | **primary**（global + project）| fallback（AGENTS.md 不存在時）；first-match AGENTS>CLAUDE | — |
| ZCode | **primary**（`~/.zcode/AGENTS.md` + workspace，agents.md:46-47）| 否（僅 onboarding 一次性遷移，agents.md:49）| `@` 不展開（agents.md:55）|
| Codex | **primary**（`~/.codex/AGENTS.md` + repo）| 否（需手動加 `project_doc_fallback_filenames`）| 32 KiB 限（agents-md.md:13）|
| Gemini | opt-in（`contextFileName: "AGENTS.md"`）| opt-in | **預設 `GEMINI.md`**（[docs](https://geminicli.com/docs/cli/gemini-md/)）|

### 1.4 Rules / Agents / Hooks（分歧大）

| Carrier | Claude | OpenCode | ZCode | Codex | Gemini |
|---|---|---|---|---|---|
| **Rules** | `.claude/rules/*.md`（LLM 行為，auto-load）| AGENTS.md + `opencode.json.instructions` | **無 auto-load**（需注入 AGENTS.md/skill）| `~/.codex/rules/*.rules`（**Starlark**，命令控管 ≠ LLM 行為）| GEMINI.md |
| **Agents** | `.claude/agents/`（md）| `.opencode/agents/`（md + `mode`/`model`/`temperature`）| `~/.zcode/agents/`（md，user-level Beta）| `.codex/agents/*.toml`（**TOML**）| （未確認）|
| **Hooks** | settings.json（豐富事件）| （鏡像未提及）| （鏡像未提及）| `hooks.json` / config.toml（需 `features.hooks=true`）| （未確認）|

**不可攜警告**：(a) Codex rules 是 **Starlark 命令控管**，語意 ≠ Claude `.md` LLM 行為規則 — rules 體系**跨不過 Codex**。(b) Codex agents 是 **TOML** ≠ Claude md。(c) `@` transclusion 僅 Claude 展開。

---

## 2. 設計視角（arch-thinking）

### ① 依賴規則（Clean Architecture 分層）

```
domain(core)  =  ai-rules/（harness-neutral：commands/ skills/ rules/ + ai-development-guide.md）
                          ↑ 依賴向內（adapter → core，core 不認識 harness）
adapter       =  各 harness ~/.xxx/ 部署（讀 ai-rules，非反向）
infra         =  各 harness runtime（Claude/ZCode/OpenCode/Codex/Gemini）
```

- **ai-rules core 必須 harness-agnostic**：不可含 Codex Starlark rules / Gemini `.toml` / OpenCode `opencode.json` 專屬語法 → 那是 adapter concerns，滲入 core 違反依賴向內。
- **橋接是 adapter 層 plumbing**（symlink / import / 格式轉換），core 不感知。
- **反向耦合 flag**：若 core 為某 harness 客製（如指令檔塞 `.claude/` 路徑），等於 core 依賴 adapter — 違規。

### ② bounded context（DDD 邊界）

- **ai-rules core context**：harness-neutral 指令（AGENTS.md 內容、SKILL.md skills、.md commands）。
- **per-harness adapter context**：各家原生格式/設定（Codex `.toml` agents、Gemini `.toml` commands、Codex Starlark rules、OpenCode `opencode.json`）— **獨立 context，不污染 core**。
- **邊界 = 橋接點**：三種橋接類型，語意各異 —
  - **symlink**（零 copy、live-sync、單一 source）← 最佳
  - **import/copy**（snapshot、後續不同步；Codex `/import`、ZCode command import 屬此）
  - **格式轉換**（`.md`→`.toml` 等；有損、需維護轉換器）

### ③ use case 驅動

**消費者**：跨多 harness 開發者，要在每家用到 ai-rules 工作流。

| Use Case | 需求 | 對應 carrier |
|---|---|---|
| UC-A：任 harness 跑 ai-rules 工作流（/build 等）| 顯式觸發 | commands（或 skills-as-command）|
| UC-B：任 harness 用 ai-rules 領域知識（arch-thinking 等）| model-invoked | skills |
| UC-C：任 harness 讀 ai-rules 全域開發規範 | 每次載入 | AGENTS.md（**已部署完成**）|

**共用 domain service 外溢陷阱**（本 skill §一③）：ai-rules 工作流想「跨所有 harness 同語意」= 強迫所有消費者妥協。但各 harness 機制差異大（Codex 無 rules auto-load、Gemini .toml、commands 路徑分歧）→ **改消費端各取所需，不改 core 去湊齊**：core 保持 neutral，各 harness adapter 自選能消化的 carrier，不追求「五家全等」。

---

## 3. 解法設計：雙層模型

### Layer 1 — Skills：跨 harness 主載體（primary，長期收斂點）

**理由**：SKILL.md 是 [agentskills.io](https://agentskills.io) 開放標準，五家都識別；`.agents/skills/` 是 Codex+OpenCode 共讀路徑；commands→skills 是兩家官方方向。

**部署策略**：
- ai-rules skills 留 `ai-rules/skills/`（單一 source）。
- **Claude**：`~/.claude/skills` dir-symlink（**現有**）→ Claude native 讀。
- **OpenCode**：自動經 `.claude/skills/` compat 讀（**現有**）；強化可加 `~/.agents/skills/`。
- **Codex**：`~/.agents/skills/` symlink → ai-rules/skills（**新部署，一個 symlink 解鎖 Codex**；Codex native 讀 `.agents/skills/`）。
- **ZCode**：import（symlink 選項，skill.md:51-60）或 `~/.zcode/skills/` per-skill symlinks。
- **Gemini**：experimental，opt-in 後 `.gemini/skills/` symlink。

**長期**：把 ai-rules「顯式工作流」commands 逐步提煉進 skills（Claude/Codex 都收斂於此；skills 也支援顯式觸發 — Codex `/skills:name`、OpenCode `skill()` tool）。不必一次全轉，按價值逐步。

### Layer 2 — Commands：per-harness 顯式觸發（secondary，保留人類 `/invoke`）

**理由**：commands 路徑家家分歧、無共用路徑；但 Claude/ZCode/OpenCode 都支援顯式命令，部分工作流維持 command 形態有價值（人類明確觸發、不同於 model-invoked skills）。

**per-harness 橋接**（不複製內容，用 symlink 橋到單一 source）：

| Harness | 橋接 | 現況 |
|---|---|---|
| Claude | `~/.claude/commands` dir-symlink → ai-rules/commands | ✅ 已部署 |
| ZCode | `~/.zcode/commands/*.md` per-file symlinks → `~/.claude/commands/*.md` | ✅ top-level 已部署 / 🔴 `instruction/` 子樹 rename 斷掉 |
| OpenCode | `~/.config/opencode/commands/` → ai-rules/commands（**OpenCode 不讀 `.claude/commands/`，需獨立 symlink**）| ❌ 未部署 |
| Codex | **不部署** commands（棄用）→ 走 skills | — |
| Gemini | `.md`→`.toml` 轉換（選擇性），或跳過靠 skills | ❌ 格式 gap |

### Bridge decision matrix（核心摘要）

| Carrier | 最佳單一落點 | 覆蓋 | 不可攜 |
|---|---|---|---|
| **Skills** | `ai-rules/skills/` → `~/.agents/skills/` + `~/.claude/skills/` | Claude + OpenCode + Codex（+ ZCode import / Gemini exp）| Gemini experimental |
| **Commands** | 無共用路徑 → per-harness symlink | Claude + ZCode + OpenCode（各別）| Codex 棄用、Gemini .toml |
| **Context** | `ai-development-guide.md` → 各家 `~/.xxx/AGENTS.md` | OpenCode + ZCode + Codex（+ Claude @import / Gemini opt-in）| Claude 需 @import、Gemini 需 opt-in |
| **Rules** | 不可攜（語意分歧）| Claude + OpenCode + ZCode（.md 注入）| Codex Starlark ≠ LLM 規則 |
| **Agents** | 不可攜（格式分歧 md/toml）| 各自維護 | Codex .toml ≠ Claude .md |
| **Hooks** | Claude 專屬（OpenCode/ZCode 鏡像未提）| Claude（+ Codex 有）| 跨 harness 無對等 |

---

## 4. 部署拓樸

```mermaid
graph LR
  subgraph CORE["ai-rules — single harness-neutral source"]
    AR["ai-rules/<br/>commands/ · skills/ · rules/"]
    G["ai-development-guide.md<br/>(global dev guide)"]
  end

  subgraph ADAPT["per-harness adapter bridges (~/.xxx/)"]
    CC["Claude<br/>~/.claude/{commands,skills,agents,rules}"]
    ZC["ZCode<br/>~/.zcode/{commands,skills} + import"]
    OC["OpenCode<br/>~/.config/opencode/commands +<br/>~/.agents/skills + ~/.claude/skills"]
    CX["Codex<br/>~/.agents/skills +<br/>~/.codex/AGENTS.md"]
    GM["Gemini<br/>~/.gemini/commands/*.toml (convert)<br/>~/.gemini/skills (experimental)"]
  end

  AR == "dir/per-file symlink" ==> CC
  AR == "per-file symlink + import" ==> ZC
  AR == "symlink (.agents/skills shared)" ==> OC
  AR == "symlink (.agents/skills)" ==> CX
  AR -. "format convert / exp" .-> GM

  G == "symlink → AGENTS.md" ==> CC
  G == "symlink → AGENTS.md" ==> ZC
  G == "symlink → AGENTS.md" ==> OC
  G == "symlink → AGENTS.md" ==> CX
  G -. "opt-in contextFileName" .-> GM

  OC -. ".agents/skills 共讀" ..> CX
```

**讀圖**：粗實線 = symlink（live-sync，最佳）；虛線 = 格式轉換/opt-in（有損或需手動）；`OC ..> CX` 標示 `.agents/skills/` 是 OpenCode+Codex 共用開放路徑。

---

## 5. 立即行動（依優先序）

### 🔴 P0：修 ZCode 斷 symlinks（rename collateral damage）

`commands/claude/` → `commands/instruction/` rename 弄斷 `~/.zcode/commands/claude/` 全樹（`clean/distill/init/sync.md` + `_common/` 共 ~21 個 dangling symlinks，指向已不存在的 `~/.claude/commands/claude/`）。

**修法**（二選一）：
```bash
# 方案 A：重建為 instruction/（對齊 rename 後）
mkdir -p ~/.zcode/commands/instruction
ln -s ~/.claude/commands/instruction/clean.md  ~/.zcode/commands/instruction/clean.md
# ...（distill/init/sync + _common/* 各一）
rm -rf ~/.zcode/commands/claude   # 清斷 symlink

# 方案 B：一個 dir-symlink 取代 per-file
mv ~/.zcode/commands/claude ~/.zcode/commands/claude.broken
ln -s ~/.claude/commands/instruction ~/.zcode/commands/instruction
```
方案 B 較簡（單一 dir-symlink，未來 rename 不會再斷一堆 per-file）。需確認 ZCode 是否接受 `~/.zcode/commands/<subdir>/` 的 dir-symlink（runtime POC）。

### 🟡 P1：Codex skills 解鎖（一個 symlink）

```bash
mkdir -p ~/.agents
ln -s /Users/ctai/Github/ai-rules/skills ~/.agents/skills
# Codex native 讀 ~/.agents/skills/（skills.md:101）；OpenCode 也 compat 讀
```
**效果**：Codex + OpenCode 同時吃到 ai-rules 全部 skills（單一 source，零 copy）。

### 🟡 P2：Codex AGENTS.md（補全 context 鏈）

```bash
ln -s /Users/ctai/Github/ai-rules/ai-development-guide.md ~/.codex/AGENTS.md
```
（Codex 讀 `~/.codex/AGENTS.md`，agents-md.md:9-13。）

### 🟢 P3：OpenCode commands（若需顯式命令）

```bash
ln -s /Users/ctai/Github/ai-rules/commands ~/.config/opencode/commands
```
（OpenCode 不讀 `.claude/commands/`，需獨立 symlink 到 `.opencode/commands/` 或 `~/.config/opencode/commands/`。）

### ⚪ P4：Gemini（成本/效益待評）

`.md`→`.toml` 轉換 + skills experimental opt-in。**建議先跳過**，靠 skills（experimental）承擔，等 Gemini skills 轉 stable 再投資。

---

## 6. 決策點 / 開放問題

1. **commands 長期存廢**：是否逐步把 ai-rules commands 提煉進 skills（跟隨 Claude/Codex 收斂）？或保留 commands 作「人類顯式觸發」與 skills「model-invoked」分工（[commands/CLAUDE.md 三層分工]）？→ 兩者不互斥：高頻工作流可雙形態（skill 為主、command 為顯式入口）。
2. **`.agents/` 是否升格為 ai-rules 主要部署面**：`~/.agents/skills/` 一個落點覆蓋 Codex+OpenCode，是否比 `~/.claude/skills/` 更適合作 cross-harness 主麵？代價：Claude 不 native 讀 `.agents/`（需驗證），需維持 `.claude/skills/` + `.agents/skills/` 兩個 symlink。
3. **OpenCode commands 是否值得部署**：OpenCode 已自動吃 skills（`.claude/skills/` compat）；commands 額外 symlink 的邊際效益 vs 維護成本。
4. **runtime POC 需求**（鏡像 caveat）：
   - OpenCode commands 100% 確認不掃 `.claude/commands/`（鏡像未提及 ≠ runtime 不做）。
   - ZCode dir-symlink 於 `~/.zcode/commands/<subdir>/` 是否接受。
   - Codex `~/.agents/skills/` 是否真 native 載入（鏡像說是，runtime 未驗）。
5. **rules 跨 harness 策略**：Codex 無對等（Starlark 是命令控管），ZCode 無 auto-load → ai-rules rules 只能注入 AGENTS.md（context 層）或各 skill，無法複製 Claude `.claude/rules/*.md` auto-load 體驗。

---

## 7. 限制聲明

- OpenCode/ZCode/Codex/Claude 事實 grounding 於本地鏡像（`ref-docs/harness/<src>/`，manifest.json `generated_at: 2026-07-03`）；**鏡像會 stale**，原站為準。
- Gemini 事實 grounding 於 web（2026-07，[geminicli.com/docs](https://geminicli.com/docs/cli/) + [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)）。
- 「（鏡像未提及）」≠ runtime 不做；關鍵部署前建議 runtime POC（§6.4）。
- 本報告是**設計提案**，非實作；P0–P4 均待確認後執行。

## Sources

- 鏡像：`ref-docs/harness/{opencode,zcode,codex,claude-code}/`（file:line 見各矩陣）
- [OpenCode commands.md](https://opencode.ai/docs/commands) · [skills.md](https://opencode.ai/docs/skills) · [rules.md](https://opencode.ai/docs/rules)
- [Codex custom-prompts.md](https://developers.openai.com/codex/custom-prompts) · [skills](https://developers.openai.com/codex/skills) · [agents-md](https://developers.openai.com/codex/guides/agents-md) · [import](https://developers.openai.com/codex/import)
- [Claude Code skills.md](https://code.claude.com/docs/en/skills) · [commands.md](https://code.claude.com/docs/en/commands)
- [Gemini custom-commands](https://geminicli.com/docs/cli/custom-commands/) · [skills](https://geminicli.com/docs/cli/skills/) · [gemini-md](https://geminicli.com/docs/cli/gemini-md/) · [.md FR #15535](https://github.com/google-gemini/gemini-cli/issues/15535)
- [ai-harness-engineering-compatibility-matrix](https://codylindley.github.io/ai-harness-engineering-compatibility-matrix/)（2026-06 第三方對照）
