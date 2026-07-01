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
| [`02-改造方案.md`](02-改造方案.md) | fork-local（立即）vs upstream（高門檻）雙軌 + 第二層後果 | 改 superpowers 側 | 要動 superpowers 時 |
| [`03-雙向借鑒.md`](03-雙向借鑒.md) | superpowers ⟷ ai-rules 移植清單 + 黃金連接點 | 改 ai-rules 側 / 看互補性 | 要借鑒到 ai-rules 時 |

---

## 執行摘要

| 維度 | 結論 |
|------|------|
| **架構體質** | 🟢 **非常乾淨**。三層（Skills ← Tool mapping ← Bootstrap）依賴嚴格向內，skill 內部依賴也向內、無循環、無反向耦合。教科書級 Clean Architecture / DIP 實作。 |
| **方法論核心** | 🟢 **skill-as-TDD** + **carefully-tuned behavior-shaping**（Red Flags tables、rationalization lists、「your human partner」措辭）。這是 superpowers 真正的護城河。 |
| **結構債** | 🟡 **6 個 upstream 問題**（Gemini 移除不完整、4 個幽靈引用、Pi dual-maintenance、bootstrap 全靜默失敗、evals/ 外部依賴、文件回憶≠行為塑造）。**全部是 upstream 的，非 fork 造成**。 |
| **與 ai-rules 的 scope 差異** | superpowers 從未追求 B 軸人類 viewport（受眾是 agent）。所有 review/eval 都是 LLM 鏈 —— 這是 **scope 邊界不是缺陷**，卻是「借鑒到 ai-rules」的關鍵差異點（`ai-rules/rules/acceptance-evidence.md` 證據獨立性視角可補強）。 |
| **fork 現況** | 你已加 7 個 fork-local 導航 CLAUDE.md（借鏡 mosaic_alpha 多層導航）+ 改 root CLAUDE.md，**全部 uncommitted**。方向正確但未完成。 |
| **黃金連接點** | superpowers 的「skill-as-TDD + behavior-shaping」⟷ ai-rules 的「A/B 雙軸 + L1-L6 證據階層 + 人類 viewport」**互補性極強**。兩者結合 > 任一單獨。 |

---

## 優先序建議

依「價值 / 門檻比」排序：

| 優先 | 行動 | 路徑 | 理由 |
|------|------|------|------|
| **P0** | commit 你既有的 7 個 fork-local CLAUDE.md + root 改動 | fork | 工作區有未 commit 改造，先固化（`git status` 確認 `M CLAUDE.md` + 7 個 `??`） |
| **P1** | A2：修 Gemini 殘留（fork-local） | fork | 立即、低風險、清掉 #1 結構債 |
| **P1** | A1：補 `.agents/` CLAUDE.md + 承認導航層 | fork | 完成你已啟動的多層導航策略 |
| **P2** | 借鑑 #2：把 skill-as-TDD 寫成 ai-rules 的 `writing-skills` 對等 skill | ai-rules 側 | **最高價值借鑒**，低衝突，補 ai-rules skill 品質方法論缺口 |
| **P2** | 借鑒 #4：progress ledger 機制引進 ai-rules `/build` / deep-work | ai-rules 側 | 高價值，補 compaction 防失憶 |
| **P3** | B1：提 upstream PR 清 Gemini 殘留 | upstream | 門檻最低的 upstream 貢獻，建立貢獻紀錄 |
| **P3** | A3 + B2：single-source lint（先 fork 再 upstream） | fork → upstream | 機械防護，踏腳石 |
| **P4** | 借鑒 #1：評估 session-start bootstrap 是否引進 ai-rules | ai-rules 側 | ⚠️ 與 ai-rules 省 context 哲學衝突，需深思（可能結論是不引進） |
| **P5** | 借鑒 #5（證據獨立性 → writing-skills 補強） | upstream | 門檻高但理論互補性最強 |

---

## Open Questions（需你決策）

1. **改造重心是 fork 還是 upstream？** —— 本報告假設「fork-local 為主、upstream 貢獻為輔」。若你想把 superpowers 當 ai-rules 的「上游方法論來源」長期追蹤，重心會不同。
2. **借鑒 #1（session-start bootstrap）要不要引進 ai-rules？** —— 這是唯一與 ai-rules 哲學衝突的借鑒。`ai-rules` 刻意 on-demand 省 context（`CLAUDE.md`「載體選擇」）；強制載入用 context 換確定性，值不值得需你判斷。詳 [`03-雙向借鑒.md`](03-雙向借鑒.md)。
3. **你的 7 個 fork-local CLAUDE.md 要不要 commit？** —— 目前全 uncommitted。若 commit，建議先 A2（修 Gemini）再一起 commit，避免固化已知結構債。

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
