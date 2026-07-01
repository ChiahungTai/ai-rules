# 03 — OpenCode 退路（CC 堵 BYOK 的業務連續性方案）

> 接續 [`01-結構理解與診斷.md`](01-結構理解與診斷.md)。本檔是 **Session 後半的核心產出**：CC 堵 BYOK 是真實風險，OpenCode 是退路，且 ai-rules 支援 OpenCode 成本遠低於預期（因其刻意相容 Claude Code）。
> sp 借鑒見 [`02-sp借鑒到ai-rules.md`](02-sp借鑒到ai-rules.md)；決策摘要見 [`README.md`](README.md)。

---

## 為什麼需要 OpenCode 退路

**CC（Claude Code）堵 BYOK 是業務連續性風險，不是選擇權**：

- **外部不可控**（Anthropic 推訂閱而限制 BYOK，是合理商業推測）
- 一旦發生，量化交易開發工作流**強迫中斷**
- 觸發時點不可預測；屆時才準備 = 壓力下、時間急迫遷移

OpenCode（`sst/opencode`，開源、provider-agnostic、支援 BYOK）是自然 fallback。所以「提前準備 OpenCode」是正當的風險緩解，不是 over-engineering。

---

## 關鍵發現：OpenCode 的 CC 相容是 ai-rules 的「免費保單」

OpenCode 刻意做了 Claude Code 相容（[官方 docs Rules 頁](https://opencode.ai/docs/rules/)「Claude Code Compatibility」段；context7 查證 `/anomalyco/opencode` + GitHub Gist / Agensi 交叉確認）：

> Project rules: `CLAUDE.md`（used if no `AGENTS.md` exists）
> Global rules: `~/.claude/CLAUDE.md`（used if no `~/.config/opencode/AGENTS.md` exists）
> Skills: `~/.claude/skills/`

這意味 ai-rules 的核心載體**零成本就能跑在 OpenCode** —— 不用像 sp 寫 `.opencode/plugins/superpowers.js`（複雜 JS adapter + lifecycle + bootstrap injection）。因為 sp 是 **plugin 要被 install**，ai-rules 是**個人 rules/skills/commands** 走 fallback 相容，且 ai-rules 不需要 session-start 強制載入（它的 rules 本來就 auto-load）。

---

## 四大載體遷移成本對應表

| ai-rules 載體 | OpenCode 對應 | 成本 | 證據 |
|--------------|-------------|------|------|
| **rules**（CLAUDE.md + `rules/` via `@` transclude）| fallback 讀 CLAUDE.md + 全域 `~/.claude/CLAUDE.md` | **零** | `rules.mdx` CC Compatibility |
| **skills**（`~/.claude/skills/`）| 讀 `~/.claude/skills/`（CC 相容）+ `opencode.json` `skills.paths` | **零 ~ 低** | 同上 + `opencode.json` 結構 |
| **commands**（34 個 `.md`）| `.opencode/commands/*.md` frontmatter（`description`/`agent`/`model`）+ body + `$ARGUMENTS` —— **格式幾乎相同** | **低 ~ 中** | 格式相同；caveat：是 server-side template，**不在 TUI command palette 自動出現**（UX 差異，要驗證觸發方式）|
| **hooks**（`settings.json`，少數如 `block-python-c-comment.py`）| OpenCode **plugin lifecycle**（`tool.execute.before` / `chat.message` / `permission.ask`）—— 機制不同 | **中** | 要改寫成 JS/TS plugin，但 ai-rules hooks 數量少、語義對應清楚（CC `PreToolUse` ≈ OpenCode `tool.execute.before`）|

**整體成本：低 ~ 中**。兩大核心載體（rules + skills）零成本相容，commands 格式相近，只有少數 hooks 要改寫成 plugin。

> **與 sp 的差異**：sp 要寫 `.opencode/plugins/superpowers.js`（JS lifecycle + message transform + bootstrap injection）—— 因為 sp 是 plugin 要 install、且要 session-start 強制載入 `using-superpowers`。ai-rules 不需要這層 —— 它不是 plugin，rules/skills 走 OpenCode fallback 相容即可。

---

## 行動方案

| 動作 | 做什麼 | 成本 | 何時 |
|------|--------|------|------|
| **驗證 fallback 相容** | 在 OpenCode 開 ai-rules repo，確認 CLAUDE.md + skills 被讀到、幾個代表性 command 能跑 | 低（1-2 小時）| 可現在，或 CC 真堵 BYOK 時 |
| **寫 hooks adapter** | 把 ai-rules 少數 hooks（`block-python-c-comment` 等）寫成 OpenCode plugin（借鑒 sp `.opencode/plugins/superpowers.js` 的模式）| 中 | 可延遲到切換時 |
| **記遷移筆記** | 記錄 commands 觸發差異（TUI palette caveat）、hooks 對應表 | 低 | 驗證時順手 |

**建議先做「驗證」** —— 花一兩小時在 OpenCode 跑一次 ai-rules，確認 fallback 相容真的有效。若有效，CC 堵 BYOK 焦慮解 80%，且知道剩下的 20%（hooks adapter）長什麼樣。這比「現在重寫整個 sp 化」或「純擔心不做」都務實。

---

## 附錄：黃金連接點（理論價值，保留參考）

> session 早期發現的 sp ↔ ai-rules 互補性，雖不是行動方案，但有理論參考價值（解釋為何借鑒 sp eval 只取精神不取結構）。

sp 的 eval 體系（drill harness：LLM **actor** + LLM **verifier**）有個結構限制：**verifier 與 actor 同家族 LLM → 共享系統性偏誤**（對應 ai-rules `rules/acceptance-evidence.md`「AI 同寫 test+impl = 零獨立性」的核心警告）。

- sp 的「skill-as-TDD」能保證 skill **被遵守**（GREEN）
- 但只有 ai-rules 的 B 軸人類 viewport（`/deliverable-review`、`/illustrate`）能保證 skill **教對了**（方向對）
- 兩者互補：sp 有 A 軸深度（skill-as-TDD + behavior-shaping），ai-rules 有 B 軸理論（證據獨立性 + 人類 viewport）。**結合 > 任一單獨**。

這也是為什麼 [`02` 借鑒清單](02-sp借鑒到ai-rules.md)取 sp eval 的「前置壓力測試」精神（併入 P0 skill-as-TDD），但不引進 drill harness 結構 —— ai-rules 的 eval 該是「人類 viewport + 機械檢查」混合，不是純 LLM verifier。

---

> 回到：[`README.md`](README.md) 決策摘要 ｜ [`01-結構理解與診斷.md`](01-結構理解與診斷.md) ｜ [`02-sp借鑒到ai-rules.md`](02-sp借鑒到ai-rules.md)
