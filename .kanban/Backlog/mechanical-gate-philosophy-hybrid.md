# 機械閘門 > LLM 自覺：rule 指路牌 + skill 顯式化

此原則散落 9 檔（dry-run 實證）、兩筆 feedback 共通根因，但無正式定義源（在 `ai-analysis/` feedback 檔）。

**決策**（flow-review 2026-06-17 討論點 2）：hybrid —— `rules/` 加一句指路牌（auto-loaded 確保每 session 見）+ 新建 `skills/mechanical-gate-philosophy/SKILL.md`（on-demand：L1-L6 階層 + 機械/viewport/prompt 決策樹 + 反模式「加條 rule 就好 = L2 不合格」）。用原則自己的精神（機械指路牌 > 自覺觸發）設計載體，最自洽；順帶收斂散落引用、解決定義源。

屬 docs mode（rule + skill 皆 `.md`）。

**來源**：`hermes-agent-synthesis` §7（自我改進安全檢查表）+ 兩筆 feedback

**回收點（EP `ep-review-assurance-uplift` 2026-07-09 落地，待本 skill 建成統一回收）**：mechanical-gate 原則（機械檢查 > AI 自述 / 人審）目前三處引用，建成本 skill 時須回收為 canonical example：
- **A1 錨點**：`rules/acceptance-evidence.md`「Runtime Invariant Assurance」段（silent-corruption invariant → runtime 機械 check，獨立於 AI mental model）—— 原則的具體機制落點
- **A4 引用點**：`rules/acceptance-evidence.md`「Claim→Evidence→Trust」+ `commands/build.md` Agent 產出機械驗證（no-impact claim 須獨立機械證據）
- **A5 引用點**：`commands/build.md`「complex-change constraint tightening」（constraint check 機械、不可被 AI lobby）
