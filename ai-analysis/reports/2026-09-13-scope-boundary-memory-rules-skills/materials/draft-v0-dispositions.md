# rules 19 檔逐檔裁定建議草案 v0（主 session 起草，待 codex 挑戰＋judge 定稿）

> 依據＝腿 3 形態標註＋腿 1 CC 機制發現＋草案 v0 判準。裁定選項：**留**（維持）／**slim**（刪 A 殼壓縮）／**pointer 化**（骨架壓縮到數行＋深層下沉 skill）／**下沉**（整檔移 skill，rule 留一行 pointer）／**hook 候選**（條目可機械化）。

## 高 A 檔（slimming 主戰場——user 北極星直接適用）

| 檔 | 判定 | 具體動作 |
|---|---|---|
| design-thinking.md（~60% A） | **slim** | 刪純共識論述（兩層思考的第一性原理論證、單向門通用概念解釋）；留 C「至少兩層連鎖後果」強制＋輸出模板 pointer＋B 觸發情境。注意 instruction-writing「易被合理化動搖的規則保留補充論證」——刪的是論證不是判準 |
| edit-discipline.md（~35% A） | **slim** | SOLID 五原則展開壓成一行列舉（模型已內建）；留 C 核（衝突寫法禁混合、預設不相容、變更範圍紀律）＋B（scripts 層級） |
| python-standards.md（~25% A） | **slim** | 「禁舊 typing」共識句壓一行；留 C（禁 `__future__`/TYPE_CHECKING 反主流裁定＋理由）、B/C（re-export 禁令＋真實案例）、D（命名） |

## C 大宗（rule 的核心收件人——留，個別條目 slim）

| 檔 | 判定 | 備註 |
|---|---|---|
| tool-discipline.md | 留＋局部 slim | C 密度最高的樞紐檔；「輸出慣例（繁中）」屬 B 偏好留 |
| collaboration-constraints.md | 留 | 反 Sycophancy/查證觸發/破壞性選擇全是 C 核心 |
| quality-constraints.md | 留＋局部 slim | 「完整交付標準」段 A 註 B 可壓；Crash-Only B 註 A 留（量化鐵律） |
| acceptance-evidence.md | 留＋局部 slim | 證據獨立性/Claim 校驗 C 核心；L1-L6 表 B 註 A 留（本專案框架） |
| outward-action-consent.md | 留 | commit consent 是 user 硬閘；模板/例外 B 段留 |
| must-execute-before-complete.md | 留 | C 原型檔；POC 生命週期 B 段留 |
| code-edit-constraints.md | 留 | claude-specific（harness-scope 隔離部署）；Edit 前 Read 是 C |
| context-management.md | 留 | 已 thin；STATE.md/memory pointer 是 B |
| modern-cli-preference.md | 留（**C 代際衰減首例候選**） | 「rg/fd 優先」2026 模型多已自覺——open Q2 活例，建議列入首次校準 re-audit 清單 |
| _ai-behavior-constraints.md | 留 | 9 行 C/B 全密 |
| llm-output-convention.md | 留 | B/D；CC 端 paths: on-demand 已成立（腿 1 發現） |

## B 拓撲檔（v1：套 bootstrap test——核心留、lookup body 下沉；codex r1 Q3 採納）

| 檔 | 判定 v1 | 備註 |
|---|---|---|
| model-routing.md | **bootstrap core 留＋lookup body 下沉 skill**（corpus 弧動作項） | 留：兩跳解析規則、native-ID 詞彙、角色→tier 表骨架；沉：委派細節/resume/fork/rate-limit/失敗態（深層本就在 model-routing skill，rule 端再加收）；問句「模型不知道這行，還知道何時載 skill 嗎」 |
| symbol-query-routing.md | **同款拆分** | 留：任務啟動 gate＋「禁 0-hit 斷言零消費者」；沉：SCIP/pyrefly/LSP 操作細節（skill 已有） |
| instruction-writing.md | 留＋候選 paths: 標記深化 | B 治理樞紐；CC 端 paths: on-demand 已成立（腿 1）；非 CC 端可走條件載入層 §四 |
| bash-hard-rules.md | 留 | CC 端工具事實，claude-scope 隔離 |
| rules/AGENTS.md | 留＋**排除出 bundle（受眾錯置修正）** | 腿 1 發現：CC 端 rules 掃描不限檔名——治理檔被當行為規範開場載。處置：harness-scope 標 meta 排除部署（deploy_agents.py 消費面已存在）——**第五類「治理文件」首例** |

## 新判準衍生：第五類「治理文件」不進 bundle

腿 3 四類（A/B/C/D）都是「給模型的行為規範」維度；rules/AGENTS.md 揭示另一維度——**受眾**（模型行為 vs 維護者治理）。治理檔應以 harness-scope 排除出 bundle（部署面已有此機制），repo 內保留。

## 與 guide 的關係（open Q5 預答）

ai-development-guide.md（4.3KB）同進 bundle：量化鐵律 B 純度高留；驗證約束表 C 留；UC-Driven/架構紀律/演化性思維段 A 成分未量測——**建議：本次不同步 slim（時間盒），列為原則定稿後首次套用示範**（guide 是 bundle 主體，動它需單獨弧）。
