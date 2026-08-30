# illustrate HTML 模式 — archify 展示級渲染（opt-in）

> /illustrate 的第三輸出模式。Console（即時）與 MD（Mermaid 沉澱，**source of record**）角色不變——HTML 是**按需渲染的展示層**，服務「一次性人類 viewport」：分享 / demo / re-onboard / drift 審查。三模式是受眾分流非取代。

## 觸發條件

- **明示**：`/illustrate html <主題或 @dir/@file>`（mode D 主題 → archify；mode B @dir → artifact 類型映射；mode A/C 明示 html → city map 走 architecture 映射）
- **增益建議**（不自動切換）：mode D 分享情境——互動搜尋 / focus / reach 追蹤 / Present 導覽對位人類 viewport 消費方式時，建議 html 並由 user 決定
- **drift compare**（opt-in）：post-build drift 審查明示要比對圖時（見下「drift compare」段）
- **永不**：Console 語境不 inline 渲染（明示 html = 切換輸出模式，檔案交付＋路徑回報）

## archify 存在性偵測與降級

偵測順序（skills 根 `~/.zcode/skills`、`~/.agents/skills`、`~/.claude/skills` 三者 symlink 同源，任一根命中即可）：

1. `<skills 根>/archify/bin/archify.mjs`（已安裝）
2. `~/Github/archify/archify/bin/archify.mjs`（repo clone）
3. 全 miss → **缺場降級**：輸出 MD Mermaid 版＋告知安裝方式，不靜默失敗

- **在場但壞**：首次偵測到後跑 `node <archify>/bin/archify.mjs doctor` 一次——doctor 失敗（node 缺 / 版本 <18 / 上游 breaking）→ 同缺場降級＋回報 doctor 診斷
- **安裝建議 clone 優先**（`git clone https://github.com/tt-a1i/archify ~/Github/archify`）；`npx skills add -g` 在本部署架構（skills 根 symlink 到 ai-rules repo）會穿 symlink 寫進 ai-rules 版本控管目錄——除非使用者明知，不建議

## 類型映射（illustrate 概念 → archify 圖型）

mode B artifact 與 mode A/C city map 共用此映射（單一源）：

| illustrate 概念 | archify 圖型 | 備註 |
|----------------|-------------|------|
| boundary / city map | `architecture` | 自由排版型，authoring 成本高 |
| data-flow | `dataflow` | stage/row 語意排版 |
| sequence | `sequence` | y 排序，authoring 成本最低 |
| call graph | `workflow` 或 `sequence` | **優先語意排版型** |
| class slice | **無對應** | 維持 md，不硬映射 |

## Authoring 紀律（委派，不重述）

渲染端全紀律以 archify 自帶 SKILL.md 為準——**檔案位置隨偵測結果**（skills 安裝：`<skills 根>/archify/SKILL.md`；clone：`~/Github/archify/archify/SKILL.md`，schemas/ 與 examples/ 同目錄）。bounded path 摘要：type router → 讀 schema+example → author JSON → `validate --quality showcase` → repair → `deliver` → `visual-check`；label 保留、repair 順序。illustrate 側補充：

- **grounding 事實先產**：讀 code（arch-thinking §二機械）→ 結構事實 → JSON IR 從事實作者化（非直接跳 archify）
- **證據附著**：節點帶 `sources`（repo 相對路徑 + line）；私有 repo 帶 `meta.repository`（GitHub origin + 當下 revision SHA），render 時以 `--repo-root` 本地 git 驗證
- **與 archify standalone 的分工**（觸發詞重疊的裁決）：illustrate 是「讀 code → grounding 結構事實 → 受眾/生命週期管理」的入口，archify skill 在場時 illustrate 仍走自己的委派流程；archify standalone 適合 raw 渲染請求（既有 JSON 渲染、Mermaid beautify、無 grounding 需求的 plain-language 圖）——不競爭，分流

## 輪數 guard

口徑＝**validate 呼叫輪數**（每次 candidate 修改後的 validate 記 1 輪，含 containment 修復）：

- **單圖止損 12 輪** / **session 總預算 18 輪**（多圖請求合併計）
- 「兩連續輪無改善即停」引用 archify 自帶止損
- 超限 → **降級輸出 MD Mermaid 版**＋回報殘留診斷（subject/evidence）——不接受半成品 HTML 交付

## 產物生命週期

- **輸出位置**：`arch-report/<主題>/`（**repo root 層級**——結構理解視覺產物是人類瀏覽優先，不是 AI session 中間產物，故不進 `ai-analysis/`）——**每次 html 任務（主題）一個子目錄**，入口 HTML 命名 **`index.html`**（靜態伺服器慣例——`python -m http.server`/GitHub Pages 開目錄即入圖）；JSON IR 用自描述名 `<主題>.<type>.json` 並存（每圖約 8 檔）；`--output <path>` 自訂路徑尊崇（track 與否使用者決定）
- **目錄即索引**：不建 index——kebab 檔名＋JSON `meta.title` 自描述；手維護 index 是 drift-prone 清單（同 skills/CLAUDE.md 索引教訓），量大再考慮機械投影生成（YAGNI）
- **git 分工**：**JSON IR＋visual-check receipt 進 git**（JSON=機器可讀結構快照＋HTML 再生源頭）；**HTML/截圖/contact sheet 不進**（每顆 ~720KB 內嵌 viewer runtime，git 比例 175:1——本地在盤、分享時複製出檔、fresh clone 用 JSON＋archify `deliver` 一命令再生）；排除規則 scope 在 `arch-report/`（`.gitignore`：`arch-report/**/*.html`、`arch-report/**/*.visual-check.*.png`）
- **html→md 雙輸出**：同主題先 html 後要 md 沉澱 → 從同一 grounding 事實再渲染 Mermaid（非 JSON 機械轉譯）；md 是 source of record

## 重生（regeneration）

**觸發**：user 說「**重生 arch-report**」（全量）或「重生 `<主題>`」（單目錄）；fresh clone 後；`git clean -Xf arch-report/` 之後。

**程序**（對每個含 JSON IR 的 `arch-report/<主題>/`）：

1. 圖型 = JSON 檔名後綴（`.architecture` / `.workflow` / `.sequence` / `.dataflow` / `.lifecycle`）
2. `deliver <type> <主題>.<type>.json <目錄>/index.html`——JSON 含 `meta.repository`（證據圖）者加 `--repo-root <repo根>`；archify 路徑依上方存在性偵測
3. 驗收態（可選）：`visual-check <目錄>/index.html`（需要 Chrome；產 receipt＋截圖＋contact sheet）
4. 確定性保證：同 JSON → 逐位元組相同 HTML（sha256 可驗）；重生後指紋對不上 = JSON 或 archify 版本變了，如實回報

缺場/壞場：報告哪些目錄待裝 archify，不靜默跳過。

## drift compare（post-build，opt-in）

- 僅 `architecture` 型：`compare architecture <base.json> <head.json> <output.html> --json`
- base/head JSON 由 drift spine 事實作者化（SEED git diff → GENERATE graph facts → 兩時點各作者化一份）；機械 receipt（added/removed/changed/moved/rerouted）與 drift 5 signal class 的 no-severity 原則同構
- guard：compare 任務（base/head/delta 各自 validate）計入 session 總預算**合併計**
- 產物一次性：base/head/delta 審完即棄，不 track

## Authoring 教訓（踩過的坑）

- **viewBox 縮放物理**：1440px viewport 下 viewer 給圖 ~930px；字級投影 = 930/viewBox寬 × 原字級，最小字級需 ≥6px——**viewBox 寧窄勿寬**（scale 大 → 字大 → 全部文字過門檻）；高度受頁高預算限制
- **CJK sublabel 是字級殺手**：中文每字 2× 寬，sublabel 帶 CJK 易縮到字級下限——優先縮文字（去 CJK/去裝飾詞），再縮 viewBox 寬
- **低價值邊先砍再繞**：backward 邊/交叉邊引發穿點與 label 衝突——依 archify 紀律移除並沉到卡片，比硬繞 via 便宜且語意更清楚
- **卡片行高參與頁高預算**：cards item 過長 wrap 推高頁面——item 單行為原則
