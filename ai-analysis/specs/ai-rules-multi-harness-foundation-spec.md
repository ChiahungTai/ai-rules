# ai-rules 多 harness foundation（dogfood）— 需求摘要

> **來源**：`/spec` 討論 + `multi-harness-architecture-direction` memory（MEMORY.md 索引） + [`ref-docs/harness/contracts.md`](../../ref-docs/harness/contracts.md)（grounded 各 harness 契約）
> **下一步**：`/execution-plan`（大型、單向門、跨 ai-rules 核心）
> **定位**：本 spec 是 ai-rules 自身 dogfood（成為 AGENTS.md-first + 多 harness 可讀）的需求層；**mosaic 的 thin EP 在本 EP dogfood 驗過後才做**（mosaic LLM 消費本 EP 內化的能力 + ai-rules 活範例）。

---

## 目標 / User Story

```
作為 ai-rules 維護者 + 多 harness 使用者，我想要 ai-rules 自身以 AGENTS.md 為
source of truth、CLAUDE.md 退化為 thin @wrapper，且 CLAUDE.md 相關 skills/commands
harness-neutral 化，因為 要讓 ai-rules 跨 harness（Claude/ZCode/OpenCode）可被讀取，
並把「成為多 harness」的能力內化成 ai-rules 自己的 skills/commands（自身 dogfood）。

痛點：ai-rules 目前是 CLAUDE.md 單 harness 體系；ZCode 不讀 CLAUDE.md（只讀 AGENTS.md，
contracts.md 引 zcode agents.md:49）→ ai-rules 全域規則在 ZCode 根本不會被載入；
skills/commands 假設 CLAUDE.md 是唯一入口。
workaround：無（目前只能在 Claude Code 跑）。
```

**規模**：🔴 大型（跨 ai-rules 核心 + 多 skills/commands + 影響全域載入鏈 + 單向門）→ 完整 `/execution-plan`。

---

## 假設（已對齊）

| # | 假設 | 結論 |
|---|------|------|
| A1 | AGENTS.md 為 source of truth；CLAUDE.md → `@AGENTS.md` thin wrapper | ✅ |
| A2 | 兩層都做：① 專案層（root CLAUDE.md → AGENTS.md + thin wrapper）② 全域層（`ai-development-guide.md` 內容 neutral 化 + 部署到 `~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`） | ✅ 都做 |
| A3 | `commands/`（slash command）、`hooks/`、`agents/` **排除**（本質 Claude-specific，不強求跨 harness） | ✅ |
| A4 | harness-neutral 化兩階段都做：① 詞彙層（入口/`@` 假設 → AGENTS.md-aware）② 內容層（逐檔審 Claude-only 語意） | ✅ 都做 |
| A5 | **不另建 migration skill/command**——能力內嵌進既有 skills/commands（A4）+ ai-rules 自身遷移的活範例。dogfood 後若步驟值得獨立 capture，下個 EP 再提煉（emergent） | ✅ 溶進 A4 |

---

## UC 定位（需求層能力）

- **UC-1（全域層）**：ai-rules 全域規則可被多 harness 讀取——`ai-development-guide.md`（→ 改名 `AGENTS.md`）內容 harness-neutral 化 + 三 harness 全域位置 symlink（Claude 已存、ZCode/OpenCode 新增）。📋 新增
- **UC-2（專案層 dogfood）**：ai-rules 自身專案指令 harness-neutral——root `CLAUDE.md` → `AGENTS.md`（source）+ thin `CLAUDE.md`（`@AGENTS.md`）。📋 新增
- **UC-3（工具層）**：CLAUDE.md 相關 skills/commands（`rules/claude-writing.md`、`commands/claude/`（`init`/`sync`/`clean`/`distill`）、`skills/CLAUDE.md`）AGENTS.md-aware / 多 harness 中立（詞彙 + 內容）。🔧 更新既有
- **UC-4（驗證）**：跨 harness 可讀性可驗證——dogfood 在 ZCode/OpenCode 確認 ai-rules 被讀到 + 代表性規則生效。📋 新增

---

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 |
|---|------|------|---------|
| SM-1 | Happy: ZCode 讀到全域 | ZCode 啟動讀 `~/.zcode/AGENTS.md` | 讀到 neutral 化的全域規則內容 |
| SM-2 | Happy: OpenCode 讀到 | OpenCode 啟動 | 讀到（AGENTS.md 或 CC fallback） |
| SM-3 | **Happy: Claude 不退化** | Claude Code 讀 `~/.claude/CLAUDE.md` / root `CLAUDE.md` | `@AGENTS.md` 展開 → 全部內容讀到，既有工作流行為不變 |
| SM-4 | 邊界: 既有 Claude 工作流不破 | `/build` `/commit` 等在 Claude 跑 | 行為不變（neutral 化是擴充非移除 Claude 支援） |
| SM-5 | wrapper↔source 不漂移 | 改 AGENTS.md 內容 | CLAUDE.md 經 `@` 自動反映；**無需 sync 命令**（紀律：CLAUDE.md 只放 `@` + Claude 專用段） |
| SM-6 | 全域三位置一致 | 改全域 source | 三 symlink（`~/.claude/CLAUDE.md` 已存 + 新增 `~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`）即時一致；**無 copy/sync** |
| SM-7 | 效能/驗證: dogfood 實跑 | 在 ZCode 開 ai-rules repo | 確認「讀得到」+ 代表性規則（如 fd 不用 find）**在 agent 行為生效**（非只 exit 0） |
| SM-8 | neutral 純度 | 寫入 Claude 專用 body 散文（hooks/paths 等） | 審查/sync 擋下（移到 CLAUDE.md/.claude）；frontmatter 欄位可容忍 |

**必須涵蓋**：SM-1/2/3（happy 跨三 harness）、SM-4（不退化）、SM-5/6（一致性，靠 `@`+symlink）、SM-7（實跑觀察行為）、SM-8（neutral 純度）。

---

## 架構模型（EP 設計依據）

**關鍵機制事實**（grounded）：
- `@` transclusion 是 **Claude Code 專用**（`claude-writing.md` 明定；contracts.md 驗：ZCode **不展開** `@import`）
- symlink 對 file read 透明（`~/.claude/CLAUDE.md` → `ai-development-guide.md` 已是此模式）
- frontmatter 欄位：harness 自動忽略不懂的（OpenCode 忽略未知 SKILL.md frontmatter；ZCode 只用 name+description）
- body 散文：harness **不會跳過**，整份當 context 讀 → Claude 專用散文 = 噪音污染

**結構分離（neutral core + per-harness overlay）**：
```
AGENTS.md        = neutral core（原則/慣例/結構——三家都讀，零 Claude body 噪音）
CLAUDE.md (thin) = @AGENTS.md + Claude 專用段（hooks、/build workflow）→ 只 Claude 讀
.claude/         = Claude 專用機制（hooks、commands）→ 只 Claude 讀
```
**「各自取用」靠結構分離，不靠「harness 跳過未知 body 散文」。**

**Plumbing（無 sync 命令）**：
- **專案層**：root `AGENTS.md`（source, neutral）+ thin `CLAUDE.md`（`@AGENTS.md`）→ `@` 保 Claude 端零 drift
- **全域層**：一份 source（改名 `AGENTS.md`）+ 三 symlink（`~/.claude/CLAUDE.md`、`~/.zcode/AGENTS.md`、`~/.config/opencode/AGENTS.md`）→ 改 source 三處即時一致

---

## 邊界

**Always**：
- AGENTS.md body **neutral**（無 Claude 專用散文；frontmatter 欄位可容忍）
- **單一 source**：專案層 `@`、全域層 symlink——不 copy、不新增 sync 命令
- **Claude 不退化**：既有 `/build` `/commit` 等工作流行為不變

**Ask First（EP 結構層決定）**：
- ⚠️ **root `AGENTS.md` 歸屬**：ai-rules「既是專案又是全域 source」雙重身份——root 同時有專案 guide（root `CLAUDE.md`）與全域 guide（`ai-development-guide.md`）兩個角色。誰是 root `AGENTS.md`、另一個放哪？（mosaic 無此問題——只有專案 guide）
- `ai-development-guide.md` 改名 `AGENTS.md` 後，既有 symlink（`~/.claude/CLAUDE.md`）重建 + rg 全 repo 確認無其他引用斷裂

**Never**：
- 不靠「harness 自動跳過 body 散文」（neutral 靠結構分離）
- 不為跨 harness 動 `commands/`/`hooks/`/`agents/`（Claude-specific，範圍外）
- 不 duplicate content（兩處事實源 = drift 溫床）

---

## 成功條件（= dogfood 具體形態）

| 條件 | 怎麼驗 |
|------|--------|
| ZCode 讀到 | `~/.zcode/AGENTS.md` symlink 通 + ZCode 啟動讀到 + 代表性規則（如「fd 不用 find」）**在 agent 行為觀察到**（非只 exit 0） |
| OpenCode 讀到 | 同上（`~/.config/opencode/AGENTS.md`） |
| Claude 不退化 | `/build`、`/commit` 在 Claude 跑、行為不變 |
| neutral 純度 | AGENTS.md 無 Claude body 散文（`/claude:sync` 或審查檢查） |

**核心防線**：要在 ZCode 看到**代表性規則真的生效**，否則「讀到了」可能只是檔案在、agent 卻沒遵循（silent success 假象）。

---

## 流程位置

```
/spec（本檔·需求釐清）→ /execution-plan（大型 EP：dogfood 自身 + 工具 neutral 化）→ [/ep-validate] → /build → [/code-review] → /commit
                                                                                                          ↓ dogfood 驗過
                                                                              mosaic thin EP（mosaic LLM 消費能力 + 活範例）
```

> EP 自足——本 spec 提供需求層 UC/SM/邊界；EP 做全域 codebase 研究、UC 盤點建卡、段落切分、前期 POC。
