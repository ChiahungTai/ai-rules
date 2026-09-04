# Work Order — Foreign-runtime 委派工單模板（_common）

> 共享子範本——foreign runtime（muse bridge task／codex）共用；skill 間引用＋主 session 直接填寫。prompt 為任務本文，禁含委派語言（muse-in-muse EPERM 教訓）。本檔定義十節硬欄位，缺一不可；消費端填寫時逐節落實，空缺＝未就緒。

## 1. 紅線（首段，違反＝失敗）

- 禁 `git add`／`git commit`／`git push`／改任何 backlog 卡狀態——止步於 working tree 編輯（「止步 commit 前」不夠，AIR-18 自行 staged 多檔教訓）
- read-only 任務禁任何寫入（advisory profile 尤甚）
- 禁把產物寫到 `/tmp` 或 repo 外；中間筆記不留檔
- 紅線違反＝失敗，非風格問題；審查未過不得結卡
- 外部 runtime flag 未暴露時，以本紅線承載 read-only 約束（bridge 暴露 `--disable-write` 後改 flag；roadmap 記 muse-plugin-cc 側）

## 2. 目標（一句話）

> 一句話說明本次委派要達成的背景與目標（讓 reviewer 一句看懂為何派）。

- 例句型：「把 X 制度化為 Y，達成 Z」（填寫時替換為本次任務的具體目標）

## 3. Baseline identity

- repo root：絕對路徑（如 `/Users/ctai/Github/ai-rules`）＋是主 working tree 還是 worktree
- 工作目錄：本次任務的 cwd（若與 repo root 不同需明示）
- base commit：凍結基線 commit hash
- 並行改動聲明：working tree 已有但不屬清理範圍的改動（如 backlog 卡、任務家產物），列出路徑與性質，避免誤判為本次改動

## 4. 必讀（按序，絕對路徑）

> 按序列出，確保可執行讀取（`cat`／`Read` 可達）；路徑一律絕對路徑。

1. `.../ep.md`——指定段落（核心原則、S1/S2/S3 等）
2. `.../rules/<rule>.md`——對應段落
3. `.../skills/<skill>/SKILL.md`——解析表結構
4. `.../agents/AGENTS.md`——治理段現況
5. `.../skills/_common/<template>.md`——層慣例（僅檔頭，無需全文）

> review 工單（external second-opinion）必讀含審查方法論 bundle：`review-engine` + 消費命令 profile（如 code-review 場景的 `code-review-and-quality`、結構軸 `arch-thinking`）——findings 沿用 bundle 既有詞彙（不定義新詞，詞彙單一源在對應 skill），供 in-harness judge 對譯裁決。

## 5. 已決策（勿重辯）＋矛盾例外

- 逐條列出已定案事項（落點、thin forwarder 維持、兩層契約、模板節名、family 角色拆名等），標「勿重辯」
- **矛盾例外**：若發現現有檔案內容、程式碼、官方文檔或驗收輸出與已決策具體衝突（同段已有矛盾的既定義），**停下來在報告中舉證**，不要自行改設計或為服從工單靜默做錯
- 舉證需附 file:line 與逐字引用

## 6. 範圍限定

- 動：檔案級列舉（如 `rules/model-routing.md`、`skills/model-routing/SKILL.md`、`agents/AGENTS.md`、`skills/_common/work-order.md`）
- 不動：其他一切（尤其 `agents/zcode/*.md` 定義檔、`rules/tool-discipline.md`、`skills/CLAUDE.md` 以外的索引檔等）
- 違反範圍＝失敗；不動檔需在交付報告中舉證 `git diff --name-only` 未改

## 7. 工具接線

- 讀查：`bash`（`cat`／`rg`／`ls`）、`Read`；字串搜尋一律 `rg`
- external runtime 接線（foreign runtime 無 LSP／MCP 面）：結構查證＝`rg`＋code-reality CLI 查詢面（在場時）；CLI 缺場＝`rg` degraded＋報告標 `[WARN]`
- 最小可用：不引入非必要工具
- 三禁令：
  - 禁 code-reality 寫入面（`build`／`snapshot`／`delta_tour`／`project`）；查詢面可用可不用
  - 禁把任何工具輸出寫到 repo 外（含 `/tmp`）
  - 禁自行妥協路徑（遇缺口停下舉證，不繞路）

## 8. 驗收（命令＋預期結果，逐條實跑）（例——填單時替換為本工單實際命令）

> 每條＝可貼上執行的命令＋預期結果，機械可判；逐條實跑並採集原始輸出。

1. `rg -n "external-runtime" rules/model-routing.md` → ≥1 命中
2. `rg -n "eligibility" rules/model-routing.md` → 命中
3. `rg -n "needs-fix" skills/model-routing/SKILL.md` → 命中
4. `rg -n "flag profile|thin forwarder" agents/AGENTS.md` → 兩詞皆命中
5. `test -f skills/_common/work-order.md && rg -n "紅線|Baseline|矛盾例外|PII|交付報告格式" skills/_common/work-order.md` → 檔在且五關鍵詞皆命中
6. `head -3 skills/_common/work-order.md | rg -c "^---"` → 0
7. `rg -n "<model-id-前綴>" rules/model-routing.md agents/AGENTS.md skills/_common/work-order.md` → 零命中（skill 檔除外；實際掃三家族模型前綴小寫，此處為避模板自身命中而改寫示意）
8. `rg -n "external-runtime" skills/model-routing/SKILL.md` → ≥2 命中
9. `rg -n "model-routing" rules/AGENTS.md` → 讀現況並報告（本次不改）

- 每條附完整命令與原始輸出（截斷標明）；不可只貼結論

## 9. 證據紀律＋PII 禁令

- 每條驗收附完整命令與原始輸出（截斷標明）；宣稱「沒改 X」須附 `git diff --name-only` 佐證
- 報告中禁出現任何 email／人名等 PII（`user_email`／`user_full_name` 禁入輸出）
- 宣稱需有獨立證據（非重跑自身假設）；失敗需如實記錄，不掩蓋

## 10. 交付報告格式（最終回覆承載，不寫檔）

1. 改檔清單（對應 `git diff`）
2. 逐段落落實說明：EP S1 三塊／S2 兩點／S3 十節各落在哪（file:line 級對照）
3. 驗收 1-9 命令與輸出（原始）
4. 偏差記錄：與 EP 規格有任何出入處＋原因
5. 未驗證項／被阻擋項
6. 建議 reviewer 聚焦點（最有信心不足之處）

> 附加：jobId／thread id、改檔清單、實跑命令與輸出、未驗證項、建議 reviewer 聚焦點（completion-check 話術承載節）；無對應項標「無」勿留空。

---

> 消費形態：skill 間以 `../_common/work-order.md` link 引用，或主 session 直接依本模板填寫新工單本文後經 bridge `task`／codex 派發。`rules/model-routing.md` tier 詞彙句與 `skills/model-routing/SKILL.md` 解析表為 family／profile 詞彙與映射單一源，本模板不自帶定義。
