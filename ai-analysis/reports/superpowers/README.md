# Superpowers 全面改造強化（索引）

> **標的**：`~/Github/superpowers`（fork of `obra/superpowers` @ v6.1.0）
> **視角**：`/arch-thinking`（Clean Architecture + DDD + 結構機械）+ `deep-thinking`（第一性原理 + 第二層後果）
> **比較軸**：與 `ai-rules` 方法論體系雙向對照
> **資料來源**：fork checkout 實讀 + 3 個背景 agent 摘要（hooks/plugins、tests/eval、14 skills）+ git 歸因
> **引用慣例**：行號為寫作時證據錨點；superpowers 後續編輯會漂移，引用以檔名+章節+關鍵句為準。

## 檔案導覽

| 檔案 | 主題 | 服務決策 | 何時讀 |
|------|------|---------|--------|
| **本檔（README）** | 執行摘要 + 優先序 + Open Questions | 快速決策 | 先讀 |
| [`01-結構理解與診斷.md`](01-結構理解與診斷.md) | 三層架構 + skill 拓樸 + skill-as-TDD + 結構債 | 理解 superpowers 是什麼 + 健康度 | 想全面理解時 |
| [`02-sp借鑒到ai-rules.md`](02-sp借鑒到ai-rules.md) | 5 個內容類借鑒（skill-as-TDD/ledger/file-handoff/form-to-failure/behavior-shaping）+ 不借的結構類 | 借鑒到 ai-rules | 要吸收 sp 手法時 |
| [`03-OpenCode退路.md`](03-OpenCode退路.md) | CC 堵 BYOK 風險 + OpenCode CC 相容免費保單 + 四大載體對應 + hooks adapter | 業務連續性 | 準備 OpenCode 退路時 |
| [`04-multi-harness機制對照.md`](04-multi-harness機制對照.md) | sp vs ai-rules multi-harness 機制對照；轉型後回頭檢驗 `02`「不借結構類」；下游缺口（skills/commands/載入語意/acceptance test）；**§7 補 ZCode 3.2.5 權限模型實測**（configuration-file hooks 不支援，官方 issue `zai-org/feedback#32` P2 open；ai-rules 場景採 yolo + 人工把關）| multi-harness 機制是否要借、ZCode 權限決策時 | ai-rules 轉型 multi-harness 後、評估機制借鑒時、用 ZCode 遇權限彈窗問題時 |

---

## Session 結論（最新，優先於下方早期分析）

> 本報告始於 session 早期的「全面改造強化」框架，經討論收斂為以下三點。**下方執行摘要/優先序若與此衝突，以此為準。**

1. **不重寫整個 ai-rules 成 sp**。sp 是 fork 參考源，重心是 ai-rules 側。重寫會稀釋 ai-rules 的量化特化 + B 軸人類 viewport + 載體選擇（與 sp 世界觀衝突），且只 Claude Code 不需多 harness。
2. **借鑒只取「內容/手法」**（skill-as-TDD、progress ledger、file-handoff、form-to-failure、behavior-shaping），**不借「結構/機制」**（bootstrap/adapter/eval harness —— 要重寫才有）。詳 [`02-sp借鑒到ai-rules.md`](02-sp借鑒到ai-rules.md)。
3. **CC 堵 BYOK 是真實業務連續性風險，但 OpenCode 退路成本遠低於預期** —— OpenCode 刻意相容 Claude Code（CLAUDE.md/skills fallback），ai-rules 核心載體零成本可跑，只需 hooks adapter。詳 [`03-OpenCode退路.md`](03-OpenCode退路.md)。

---

## 執行摘要

| 維度 | 結論 |
|------|------|
| **架構體質** | 🟢 **非常乾淨**。三層（Skills ← Tool mapping ← Bootstrap）依賴嚴格向內，skill 內部依賴也向內、無循環、無反向耦合。教科書級 Clean Architecture / DIP 實作。 |
| **方法論核心** | 🟢 **skill-as-TDD** + **carefully-tuned behavior-shaping**（Red Flags tables、rationalization lists、「your human partner」措辭）。這是 superpowers 真正的護城河。 |
| **結構債** | 🟡 **6 個 upstream 問題**（Gemini 移除不完整、4 個幽靈引用、Pi dual-maintenance、bootstrap 全靜默失敗、evals/ 外部依賴、文件回憶≠行為塑造）。**全部是 upstream 的，非 fork 造成**。 |
| **與 ai-rules 的 scope 差異** | superpowers 從未追求 B 軸人類 viewport（受眾是 agent）。所有 review/eval 都是 LLM 鏈 —— 這是 **scope 邊界不是缺陷**，卻是「借鑒到 ai-rules」的關鍵差異點（`ai-rules/rules/acceptance-evidence.md` 證據獨立性視角可補強）。 |
| **fork 現況** | 7 個 fork-local 導航 CLAUDE.md + root 改動**已 commit**（superpowers repo `c7133db`，借鏡 mosaic_alpha 多層導航；非 upstream 認可）。重心不在改 sp，見 Session 結論 #1。 |
| **黃金連接點** | superpowers 的「skill-as-TDD + behavior-shaping」⟷ ai-rules 的「A/B 雙軸 + L1-L6 證據階層 + 人類 viewport」**互補性極強**。兩者結合 > 任一單獨。 |

---

## 優先序建議

依「價值 / 門檻比」排序：

| 優先 | 行動 | 路徑 | 理由 |
|------|------|------|------|
| **P0** | 借鑒 #1：skill-as-TDD 寫成 ai-rules `writing-skills` skill | ai-rules 側 | 最高價值借鑒，補 ai-rules skill 品質方法論缺口（無前置 TDD 迴圈） |
| **P0** | 借鑒 #2：progress ledger 引進 `/build` / deep-work | ai-rules 側 | 補 compaction 防失憶，高價值低衝突 |
| **P0** | OpenCode 驗證：在 OpenCode 跑一次 ai-rules 確認 fallback 相容 | ai-rules 側 | 1-2 小時，解 CC 堵 BYOK 焦慮 80%，知道 hooks adapter 長怎樣 |
| **P1** | 借鑒 #3：SDD file-handoff 強化 `agent-workflow` | ai-rules 側 | 保護 controller context |
| **P1** | 借鑒 #4：Match the Form to the Failure 寫進 `instruction-writing.md` | ai-rules 側 | 寫 rule/skill 手法精度，純理論無衝突 |
| **P2** 🔧執行中 | 借鑒 #5：behavior-shaping 補 3 skill 行為骨頭（TDD Iron Law / debugging 熔斷 / review 反 sycophancy）| ai-rules 側 | handoff from sp session；保留量化特化只補骨頭；實讀驗證 2 處調整（項2 深化既有熔斷 / 項3 落點改 judge-review）|
| **P3** | sp fork 維護：保持 upstream 純粹，不重心改 sp | fork | 重心不在這；upstream 貢獻只挑低門檻（Gemini 清理）|

---

## Open Questions

1. ~~改造重心是 fork 還是 upstream？~~ **已決（Session 結論 #1）：重心是 ai-rules 側借鑒，sp 是 fork 參考源**（不重心改 sp）。
2. ~~借鑒 session-start bootstrap 要不要引進？~~ **已決：不引進**（屬「結構類」，與 on-demand 省 context 衝突）。
3. **OpenCode 驗證何時做？** —— 現在花 1-2 小時驗證 fallback 相容（買保險），或等 CC 真堵 BYOK 才做（成本低可延遲）。建議現在。
4. **借鑒 P0 項（skill-as-TDD + progress ledger）何時開工？** —— 是 ai-rules 真的缺的能力，值得排進 kanban。

---

## 關鍵檔案索引（superpowers repo）

| 主題 | 路徑 |
|------|------|
| 三層架構權威 | `docs/porting-to-a-new-harness.md` |
| skill 設計哲學 | `skills/CLAUDE.md`（fork-local） |
| skill-as-TDD 方法論 | `skills/writing-skills/SKILL.md` |
| testing 方法論 | `skills/writing-skills/testing-skills-with-subagents.md` |
| SDD 核心 | `skills/subagent-driven-development/SKILL.md` |
| bootstrap 機制 | `hooks/CLAUDE.md`（fork-local）、`hooks/session-start` |
| contributor 紅線 | root `CLAUDE.md:42-99` |
| 測試體系 | `tests/CLAUDE.md`（fork-local）、`docs/testing.md` |
| 唯一自動化 RED-GREEN | `tests/claude-code/test-worktree-native-preference.sh` |
| eval 規範（未實作） | `docs/superpowers/specs/2026-05-06-lift-drill-into-evals-design.md` |
