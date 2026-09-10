# Review: skills/instruction-testing/SKILL.md（GLM 5.3 fresh-eyes，2026-09-10）

**Verdict：整體忠實落地工單，可收斂。** 驗收六條全數通過（①③⑤⑥ 機械驗證、②④ 對照源文核對）；無 🔴。4 個 🟡（其中 F1/F4 是 sp 源頭就有、詳盡版與精煉版皆缺的操作缺口；F2/F5 是詳盡版有而精煉版漏掉的實質內容）＋7 個 🟢。A 軸語彙零違規（全檔唯一「已驗收/已證實」出現在禁令句內）。

## Findings

| ID | 嚴重度 | 檔案:行 | 問題 | 建議 | 信心 |
|----|--------|---------|------|------|------|
| F1 | 🟡 | skills/instruction-testing/SKILL.md:44、:75 | fresh-context 取樣機制未定義：RED step 4「每個樣本彼此隔離」與 micro-test「每 arm 5 reps」都沒說「一個樣本怎麼取得」（獨立 subagent？單發 call？guidance 放 system context、壓力任務放 user message 的拆分）。sp 源的操作句（writing-skills/SKILL.md:579 "raw API call, or a single-shot subagent… System prompt = the realistic context…"）兩版皆漏。照做的 AI 可能在同 session 連跑 5 reps——靜默違反隔離保證，GREEN 假綠 | 兩處各加一句：「fresh context＝每樣本獨立 subagent／單發呼叫；guidance 進 system/project context、壓力任務進 user message；禁同 session 連跑多樣本」 | confirmed |
| F2 | 🟡 | skills/instruction-testing/SKILL.md:59-68 vs :30 | REFACTOR 對策與風險分級不對稱：中 tier（technique/pattern/reference）明確存在且跑 retrieval/application scenario，但 REFACTOR 只列 discipline/shaping/omission/conditional 四種 failure 的修法；「找不到、誤解、套錯」在 form 表也無對應列。詳盡版第 5 條「technique/reference gap：補判斷步驟、適用條件、retrieval anchor」精煉時漏掉 | REFACTOR 清單補回該條（或 form 表加 retrieval-failure 列） | confirmed |
| F3 | 🟡 | skills/instruction-testing/SKILL.md:120 | pilot baseline 污染陷阱：must-execute-before-complete 被 deploy_agents 全文打包進 always-on bundle（證據：~/.zcode/AGENTS.md:368-378 內嵌 `<!-- rules/must-execute-before-complete.md -->` 全文）。pilot「baseline arm 不載入該 rule」可被理解成「不引用 rule 檔」——但真實消費端 context 中該 rule 經 bundle 抵達；執行者若按 RED step 3「其餘 context 保持真實消費場景一致」保留 bundle，baseline 已含 guidance → RED 假陰性 | pilot 段加一句：「本 rule 為 always-on bundle 成員，baseline arm 須移除其 bundle 部署投影，非僅不引用 rule 檔」 | confirmed |
| F4 | 🟡 | skills/instruction-testing/SKILL.md:57 | GREEN-fail 分支缺診斷協議：現文只說「先讀新 rationalization，再修改 guidance」。sp 的 meta-testing 三分（testing-skills-with-subagents.md:240-265：skill 清楚但故意無視→加 foundational principle；漏內容→照建議加；組織上沒看到→調結構）兩版皆未吸收。對「清楚但無視」類 failure，預設動作「改 guidance（加字）」正是錯誤修法，會堆成 prohibition 牆（:84 自禁） | 補一行三分 triage 或標注 meta-testing 技術名稱供按需深挖 | evidence-based |
| F5 | 🟢 | skills/instruction-testing/SKILL.md:74 | 詳盡版「Control 的判讀」四條僅存一條：漏「control 沒 failure、既有 wording 卻造成 failure → 優先懷疑既有 instruction 引入 regression，考慮刪除或重寫」——「guidance 本身造成退化」的偵測路徑全文缺失（完成判準也無此項）；「差異不穩→不宣稱有效」由 variance 條部分承接 | 併回 micro-test 點 1 或點 5 一句 | confirmed |
| F6 | 🟢 | skills/instruction-testing/SKILL.md:124-144 | 三個 scenario 的 pass＝「選 B 且真的執行」在裸 prompt 不可觀察——情境未附真實可執行 artifact（sp Key Elements 要求 "Real file paths"）；pilot 弧照文直跑只能收到選擇自述，與本 skill 自己的「複述不算通過」判分規則矛盾 | pilot 段註明：正式執行時 harness 須實例化真實 artifact＋sandbox，以執行紀錄（exit/log）判分，非選擇陳述 | evidence-based |
| F7 | 🟢 | skills/instruction-testing/SKILL.md:52 | 詳盡版「Rationalization counter 的來源限制」段（禁腦補假想藉口；無據條款創造新協商空間）只半承接——GREEN step 1 僅覆 GREEN 端，counter 端（REFACTOR）的來源限制漏 | REFACTOR 段補「counter 只封已觀察到的 loophole」 | confirmed |
| F8 | 🟢 | skills/instruction-testing/SKILL.md:63、88、41/48/57 | 「Red Flag」/「Red Flags」混用；「score」/「判分條件」混用 | 統一（五維第一維：術語一致） | confirmed |
| F9 | 🟢 | skills/instruction-testing/SKILL.md:97 | 「它能證明…有影響」措辭略強；詳盡版「產生了所測到的影響」更精確（限定為量測到的作用，非因果證明宣稱） | 改為「能支持『…條件下產生所測到的影響』的 claim」 | evidence-based |
| F10 | 🟢 | skills/instruction-testing/SKILL.md:45 | 逐字 rationalization capture 無落點（journal？EP notes？專用測試紀錄檔？）；跨 session REFACTOR 弧要回收原句時無處可尋 | RED step 5 註明落點（如 .agent-tmp/ 測試紀錄或 EP 段落） | evidence-based |
| F11 | 🟢 | skills/instruction-testing/SKILL.md:86-93 | sp「No nuance clauses」實證（writing-skills/SKILL.md:473：winning recipe 加一條 nuance clause 即從 consistent 退化成 noisy）未吸收；現文僅經 conditional-drift 列承接 exemption 半邊 | form 表下補一句：「真例外寫成獨立 conditional；禁對已驗證有效的 recipe 附加 nuance/例外條款」 | evidence-based |

## 軸 A：工單驗收六條逐項

| 條 | 判定 | 證據 |
|----|------|------|
| ① 自洽＋引用存在 | PASS | 8 個 link 目標全部存在（instruction-writing×3、acceptance-evidence×3、02-sp借鑒報告、test-driven-development、consistency、doc-health）；`rules/must-execute-before-complete.md` 純文字引用存在。僅 F8 術語小雜音 |
| ② A 軸天花板 | PASS | :95-105 專節；A 軸機器自驗證/B 軸人類 viewport/L1–L6 按實際來源分類/禁自稱 L5——與 rules/acceptance-evidence.md:40-45 語彙一致；「獨立 context ≠ 獨立智能」「共用錯誤前提」皆承接 |
| ③ 風險分級 | PASS | :27-31 三級表＋:25「不以檔名或 rule/skill 類型直接判定」＋:152 完成判準反過度工程項 |
| ④ blueprint 合更新紀律 | PASS | workflow.md ⑤ 驗證列單格＋link 最小織入；⚠️ 標記語義與 blueprint/AGENTS.md「已有部分 substrate、target contract 尚未完整落地」吻合；「pilot 尚未實跑」與 skill :120 免責句、skills/CLAUDE.md「⚠️ draft…pilot 尚未執行」三處一致 |
| ⑤ sp 出處標注 | PASS | :10 兩個 sp 檔名＋報告 link＋明列不引入 bootstrap/drill harness/plugin 分發（＝工單決策 1） |
| ⑥ 交叉引用存在 | PASS | 同①；wiring 三處（instruction-writing:10 pointer、skills/CLAUDE.md 條目、blueprint workflow.md）皆在，格式與兄弟條目一致 |
| pilot 設計 | PASS 帶 F3/F6 | 3 scenarios × 3+ 組合壓力 × pass/RED-capture 判準 × baseline-first 護欄（baseline 沒紅不得宣稱有效）齊備 |

## 軸 D：詳盡版（20,305 bytes）→ 精煉版（13,746 bytes）實質差異清單

判定為「精煉」的：A 軸不能證明清單 5→3 項（provider transferability 由 micro-test「獨立實驗軸」承接、共用錯誤前提由 :105 承接）；完成判準 9→8 條（omission/conditional 刪 checklist、正文 REFACTOR 仍在）；micro-test「修改前 wording 作 baseline arm」（微小）；X/Y 引用塊改行內。

判定為「漏」的：F2（technique/reference gap 條）、F5（Control 判讀三條，其中 regression 偵測最實質）、F7（counter 來源限制）。另 F1/F4 是 sp 源頭就有、兩版皆無（非本次精煉造成，屬起草缺口）。

## 審查者自證

已執行：
- 8 個 link 目標存在性逐一 `[ -f ]` 檢查（全 OK）
- `git status`：skills/instruction-testing/ 為 untracked 新檔；workflow.md/skills/CLAUDE.md/instruction-writing/SKILL.md 為已修改（wiring 在場）
- `git diff` 檢視 workflow.md 與 skills/CLAUDE.md 實際改動內容
- blueprint/AGENTS.md「更新紀律」全文核對（⚠️ 語義、最小織入）
- `rg "must-execute-before-complete|語法正確不代表邏輯正確" ~/.zcode/AGENTS.md` → :368-378 全文內嵌（F3 證據）
- `rg "L[1-6]|L4–L6|L5|B 軸|A 軸"` 全檔掃 → 無升格宣稱；`rg "已驗證|已證實|已驗收|proven|已通過"` → 唯一命中是 :103 禁令句
- `wc -c`：skill 13,746 bytes / 詳盡版 20,305 bytes
- sp 兩源全文讀畢（writing-skills/SKILL.md、testing-skills-with-subagents.md）逐概念對照
- 02-sp借鑒報告 P0 段核對（skill-as-TDD 為唯一未落地 P0，本 skill 落地）

無法驗證／未驗證：
- 五維檢查的「程式碼範例可執行」維：skill 內 code block 皆為情境文字（text），無可執行碼，不適用
- pilot scenario 實際紅不紅：本skill明文「本段不構成已執行證據」，pilot 未跑，F3/F6 為設計面推演（F3 有 bundle 內嵌實證，F6 標 evidence-based）
- skills/CLAUDE.md 對 ZCode 端 bundle 的投影是否同步：屬部署流程，非本審查範圍
