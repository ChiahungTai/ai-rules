# 工單：scope 分界原則共析（memory / rules-bundle / skills）——advisory 形態

## 1. 紅線（違反＝失敗）

- read-only 任務：禁任何寫入（檔案、git、backlog 狀態全禁）；交付＝最終回覆文字
- 禁 `git add`/`commit`/`push`；禁把任何產物寫到 /tmp 或 repo 外；中間筆記不留檔
- 驗證命令用**單一 pattern**（`rg "pattern"` 一次一詞）——多 pattern alternation 在你家 shell 曾全數失真（09-12 實證），alternation 查無的結論一律不採信自己，改逐詞分跑

## 2. 目標（一句話）

基於四腿研究材料與主 session 草案 v0，共析「哪些知識放 memory、哪些放 rules（user-level AGENTS.md bundle）、哪些放 skills」的分界原則——對草案提出挑戰/修正/補充，並回答六個開放問題。

（非 role 派發，ad-hoc advisory。）

## 3. Baseline identity

- repo root：`/Users/ctai/Github/ai-rules`（主 working tree）
- base commit：`1158dc9`（2026-09-13；working tree clean——`git status --short` 空輸出；`.agent-tmp/` gitignored 不計）
- 並行改動聲明：無 tracked 改動；`.agents/memory/` 池自帶 git 與本任務無關

## 4. 必讀（按序，絕對路徑）

1. `/Users/ctai/Github/ai-rules/.agent-tmp/scope-research/draft-v0-principles.md`——主 session 草案（共析對象；六開放問題在 §六）
2. `/Users/ctai/Github/ai-rules/.agent-tmp/scope-research/leg1-cc-mechanisms.md`——CC 2.1.263 binary 逆向＋官方文檔（rules-dir 官方性、Cowork 例外、paths: 活機制）
3. `/Users/ctai/Github/ai-rules/.agent-tmp/scope-research/leg2-four-family-comparison.md`——四家 bundle/skills/memory 消費對照
4. `/Users/ctai/Github/ai-rules/.agent-tmp/scope-research/leg3-rules-tagging.md`——rules 19 檔 A/B/C/D 形態標註（A 共識/B 特殊/C 校準/D 機械）
5. `/Users/ctai/Github/ai-rules/.agent-tmp/scope-research/leg4-memory-pool-inventory.md`——memory 池 239 條盤點＋rules 重疊面
6. `/Users/ctai/Github/ai-rules/ai-analysis/reports/2026-09-10-carrier-placement-v2-conference.md`——09-10 載體放置 v2 裁決書（層級閘等已決策源頭）
7. `/Users/ctai/Github/ai-rules/skills/memory-audit/SKILL.md`——「載體統一定義表」節（約 L136-175；現行單一源）
8. `/Users/ctai/Github/ai-rules/rules/`——19 檔本體（抽驗腿 3 標註用，抽 3-5 檔即可）

## 5. 已決策（勿重辯）＋矛盾例外

- user 北極星原話（09-13）：「rules 不應該放太多 common 工程共識，應該是放一些特殊規範」；「skills 我的直接是用觸發的」——這是研究目標非待辯項
- 09-10 裁決已定：層級硬閘最前、memory 只留三物（事故證據/偏好例外/pointer）、混合內容拆層、regex 只產 candidate——勿重辯
- reference 分層（rule 核心＋pointer→skill 深層）是既定模式
- 事實數字（勿質疑來源，可抽驗）：rules/ 19 檔非 20；池 239 條；bundle 現值 32,835B
- **矛盾例外**：材料與 repo 實況衝突時停下舉證（file:line＋逐字引用），勿靜默服從材料

## 6. 範圍限定

- 動：零（read-only）
- 不動：全部（交付附 `git diff --name-only` 空輸出舉證）

## 7. 工具接線

- 讀查：`cat`/`rg`（單 pattern）/`ls`；不引入其他工具
- CR/code-reality 不需要（純文檔分析）

## 8. 驗收（查證命令＋預期證據形態，逐條實跑）

1. `test -f /Users/ctai/Github/ai-rules/.agent-tmp/scope-research/draft-v0-principles.md` → 存在
2. `rg -c "Cowork" /Users/ctai/Github/ai-rules/.agent-tmp/scope-research/leg1-cc-mechanisms.md` → ≥1（Cowork 例外主張在材料）
3. `ls /Users/ctai/Github/ai-rules/rules/*.md | wc -l` → 19（抽驗腿 3 勘誤）
4. `rg -c "層級" /Users/ctai/Github/ai-rules/ai-analysis/reports/2026-09-10-carrier-placement-v2-conference.md` → ≥1
5. 抽驗腿 3 任 3 檔標註：`cat` 該檔全文對照其形態判定（如 design-thinking.md 是否真 ~60% 共識、model-routing.md 是否真近 100% 專案特定）→ 每檔給 同意/修正＋證據

## 9. 證據紀律

- 分析主張附錨點（材料檔名＋節／repo file:line）；查不到標 unverified 禁腦補
- 對草案的每個挑戰附：具體條文位置＋反例或論證＋修正建議
- 失敗/不確定如實記錄

## 10. 交付報告格式（最終回覆承載，不寫檔）

1. **對草案 v0 的總判斷**：成立/有條件成立/不成立＋一句理由
2. **六開放問題逐題立場**（§六 Q1-Q6：A 類刪除安全閥／C 類代際衰減／B 拓撲檔 always-on 正當性／ZCode skills 稅／guide 是否同標準／回填歸屬）——每題：你的答案＋論證＋與草案分歧處
3. **挑戰點清單**：草案哪裡錯/漏/過度設計（附條文位置；沒有就說沒有）
4. **腿 3 抽驗結果**（§8.5 的三檔對照）
5. **你認為草案沒問但該問的問題**（最多三個）
6. 環境前提自曝：HEAD、git diff 舉證、材料讀畢聲明
7. 建議主 session 聚焦點
