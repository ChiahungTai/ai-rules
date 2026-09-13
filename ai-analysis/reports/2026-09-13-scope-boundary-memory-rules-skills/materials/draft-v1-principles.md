# Scope 分界原則草案 v1（memory / rules-bundle / skills）——整合 codex r1 六挑戰＋user steering

> 2026-09-13 deep-work 弧。v0→v1 變更驅動：codex 共析 r1（job `job-mtz1vwwb-o6pzpw`，有條件成立＋六挑戰三測試）＋ user mid-flight steering（「CC 的 rules 機制可能是解掉 bundle 一直很難減少的關鍵」）。待 probe 腿驗證 user-level `paths:` 後定稿。

## 一、北極星（不變）

user 09-13 原話：「rules 不應該放太多 common 工程共識，應該是放一些特殊規範」＋「skills 我的直接是用觸發的」。正式化為兩面：
- **內容方向**（什麼離開 rules）：「模型已知」共識＝**刪除候選訊號**（codex C1 修正：不升格為硬資格反條件——模型能力隨 family/代際變動，硬反條件會誤殺）
- **資格方向**（什麼能進/留 rules）：見 §二公式

## 二、rule 資格公式（codex r1 定版候選，主 session 採納）

> **rule 資格 ＝ 層級相容 ∩「首個有後果的決策前必須在場」∩（經驗證的模型校準需求 ∪ user 特殊裁定 ∪ trigger-bootstrap 必要資訊）**

「模型本來就知道」＝強刪除候選訊號，非數學式硬反條件。

### 三測試（residency 判準核心——codex r1 貢獻）

1. **Bootstrap test**：一段知識移進 skill 後，模型在不知道該段內容的情況下，仍能可靠知道「現在該觸發這個 skill」嗎？——不能→bootstrap 核心留 rule（例：「改 instruction 檔前必載 instruction-writing skill」這行本身）；能→下沉 skill
2. **First consequential action test**：規範最晚可在哪時點出現？等 skill 觸發時若已可能 commit／選錯 model／rg 誤判零消費者→核心必須提前常駐
3. **Portfolio duplication test**：同一校準是否已被 harness system prompt／hook／repo AGENTS／skill trigger 承載？已被更高優先級或機械層可靠承載→user-level rule 是重複 token 稅

### 決策流（定稿形態）

**Scope gate（層級硬閘，09-10）→ 三測試（residency）→ 載體**。形態訊號：common/known＝delete candidate；observed calibration failure＝C 證據；project/user 特殊事實依三物進 memory；可靠 task trigger 的深層方法進 skill；trigger 前必須生效的最小核心留 rule。

## 三、形態→處置映射 v1（修 C2/C3/C6 軸混淆）

| 內容形態 | 處置 | v0→v1 變更 |
|---|---|---|
| A 共識 | **delete candidate**（非自動刪）——兩層安全閥：逐條文判不逐檔判（A 殼 C 核拆開）；刪除者與初判者分離（writer 標 candidate，獨立 reviewer 查現役 model families 反覆失敗證據）；有 observed violation／user override／pre-trigger necessity 者重分類 C/B | v0「A→刪」太直白 |
| 純教學 A（textbook 知識） | **直接刪**，不降 skill——搬 skill 仍付 catalog metadata 稅＋trigger 競爭（ZCode 每輪元數據） | codex C6 新增 |
| C 校準（有觀測失敗證據） | 三路：**留 rule**（跨任務且先於 routing 生效——影響 skill 觸發/授權邊界/驗收宣稱）／**降 skill**（有清楚 task trigger 且 skill 能在首個有害行為前載入）／**移 hook**（純機械＋單入口＋無語義例外） | v0「C→rule」太絕對（codex C3） |
| C 衰減治理 | **事件觸發 re-audit**（非日曆 sunset）：主力 model family 換代／harness 改版／bundle 逼近 gate／相關事故長期消失＋無 rule probe 穩定／該 rule 被修改時順手重判 | codex Q2 |
| B 拓撲 | **bootstrap core vs lookup body 拆分**：核心問「模型若不知道這一行，還知道何時為什麼載對應 skill 嗎」——不知道→留 rule；知道→下沉 skill。例：model-routing 兩跳規則留、委派/resume/rate-limit 細節收 skill；symbol-query 的啟動 gate＋「禁 0-hit 斷言零消費者」留、SCIP/pyrefly 操作細節收 skill | codex Q3 |
| D 機械 | 機械性≠residency（軸混淆修正）——D 只說明**容易成 hook/config/recipe**；是否常駐另判 | codex C2 |
| 治理文件（受眾≠模型） | **第五類**：rules/AGENTS.md 型治理檔不以行為規範身分進 bundle（harness-scope 排除部署面已有） | 主 session 補（腿 1 發現 CC 不限檔名載它） |

## 四、條件載入層（user steering——本次新增設計；probe 已實證）

**洞察**：CC 原生三段式（always-on rule／path-scoped rule／skill）中間層正是 bundle slimming 的鑰匙——bundle 難減是因為非 CC 三家只有「always-on 或 nothing」二選一。

**設計（草案）**：`paths:` frontmatter 升格為 **deploy 機械 marker**——
- CC 端：原樣部署（原生條件載入——若 user-level 支援成立〔probe 驗證中〕，匹配檔被讀到才載）
- 非 CC 端（ZCode/Muse/Codex）：deploy_agents.py 消費 `paths:` → **body 排除出 bundle、自動生成 bootstrap 指針行**（例：「**/*.py 工作前載 python-standards 深層 skill」）——bootstrap test 決定指針行內容
- 效果：條件性內容從三個 bundle 的 always-on 面移除，CC 行為不變，非 CC 端靠指針＋skill 維持可達性；`paths:` 成為「此檔非 always-on」的機械可判訊號

**候選標的**（bootstrap test 預評）：instruction-writing（`**/*.md`，已標）、llm-output-convention（`**/*.py`，已標）、python-standards（`**/*.py`，候選——但無配對 skill，需先建或併入最近 skill）、bash-hard-rules/code-edit-constraints（claude-specific 已隔離，非 marker 標的）。

**前提依賴**：user-level `paths:` 支援**已實證成立**（腿 5 probe：實驗組 Read 匹配檔→`load_reason:"path_glob_match"` 注入、對照組零事件——見 `leg5-probe-paths-verdict.md`）。CC 端原生條件載入全額成立；非 CC 端排除 marker 照設計生效。

## 五、實證表述修正（codex C4/C5）

- 「四家 instruction bundle 全 always-on 全量注入」→ 改為「**跨 harness portable baseline 不可依賴 path-scoping（CC 以外無原生中間層）；CC 另有原生 path-scoped 例外**」
- 「Codex 32KiB 鏈」→ 「Codex instruction budget 有界（32KiB 語義兩處官方描述未調和，unverified）」——支撐 slimming 但不作精確前提
- 腿 3 百分比（A~10% 等）定位為**排序 heuristic**，非 corpus 精確量測

## 六、ZCode skills 稅治理（codex Q4 採納）

治理對象＝enabled surface（非 repo skill 總數）：descriptions 總預算與區辨度、trigger vocabulary 競爭、rare/manual-only skills 是否值得 ZCode enable、實際 degradation 觀測。不發明通用數量上限 N——ZCode 端 harness-specific enable policy 另案。

## 七、guide 同標準（codex Q5 採納）

判準本次明確涵蓋 guide（它就是 user-level instruction surface）；19 rules 與 guide 的 corpus 逐條量測分兩個 implementation batch。

## 八、回填與實施歸屬（codex Q6 採納）

1. **判準回填併 AIR-70 段二**（連同 09-10 未落的層級閘首句——單一源 memory-audit 載體統一定義表，不再開第二 authority）
2. **corpus slimming 獨立弧**（19 檔＋guide 依新判準搬遷——blast radius 分離，不與判準修訂混驗收）
3. 條件載入層（§四）＝ deploy_agents.py 機械消費——併 corpus 弧或獨立小卡（probe 結果後定）
