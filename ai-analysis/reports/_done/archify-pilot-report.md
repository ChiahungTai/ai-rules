# Archify Pilot 結算報告 — annotate 標註工作台四圖型驗證

> Pilot 目的：量測 `/illustrate` 候選 HTML 輸出模式（archify 渲染引擎）在真實標的上的 authoring 成本與品質閘門行為。標的：`mosaic_alpha/apps/annotate/`（AGENTS.md 2026-08-30 更新版為 grounding 源 + 程式碼 spot-check）。
>
> **產物處置（2026-08-31 user 裁定）**：本報告為 EP（`_done/ep-illustrate-html-mode.md`）證據鏈唯一保留物；4 組 JSON IR/HTML/receipt/PNG 已清理（副產物可由 JSON 再生，價值已蒸餾進下方成本表與 skill「Authoring 教訓」段）。

## 產出清單（4/4 showcase validate PASS + visual-check PASS）

| 圖 | 檔案 | 內容 | JSON | HTML |
|----|------|------|------|------|
| architecture | annotate-workbench | 11 元件 + 3 邊界（apps/annotate / research 契約層 / truth 邊界）＋ evidence sources（--repo-root 驗證通過） | 6.0KB | 722KB |
| dataflow | golden-pipeline | golden 寫入契約 5-stage 管線（決策輸入→寫入 gate→truth 儲存→讀取合併→下游消費） | 3.5KB | 717KB |
| workflow | annotate-session | 標註 session 生產線（3 lanes × 6 cols，schema v2 compiler） | 3.0KB | 721KB |
| sequence | llm-collab | LLM 協同提案 loop（6 participants × 10 messages，三段 segments） | 2.5KB | 714KB |

## 成本結算（validate→repair 迴圈輪數）

| 圖型 | schema 迭代 | containment 迴圈 | 總輪數 | 主因 |
|------|------------|----------------|--------|------|
| architecture | 7 | 0 | 7 | 邊穿點、label overlap、viewBox 過寬壓縮字級 |
| dataflow | 8 | 4 | 12 | 對角箭頭違規、CJK sublabel 字級 6px 門檻、label 貼線 |
| workflow | 4 | 8 | 12 | viewBox-capacity（compiler 最小值探測）、lane 重疊、卡片行高 |
| sequence | 2 | 4 | 6 | y 軸 160-487 邊界、legend clearance、字級門檻 |

**平均 ~9 輪/圖**。每輪 = 1 validate 命令 + 讀診斷 + 1-3 處 Edit。沒有一輪是「神秘失敗」——每個錯誤都帶 subject/evidence/supportedFixes，修復是機械式的。

## Authoring 教訓（EP 素材）

1. **語意排版 ≠ 自由排版成本**：sequence（y 排序）2 輪、workflow（lane/col）4 輪就過 schema；architecture（自由 pos）與 dataflow（stage/row 但箭頭正交規範）最貴。call graph 類需求應導向 workflow/sequence 而非 architecture。
2. **desktop-readability 是縮放物理**：1440px viewport 下 viewer 給圖 ~930px；`scale = 930/viewBox寬`，最小字級投影需 ≥6px ⇒ viewBox 寬上限 ~1085px（7px 字級 floor）；高則受 900px 頁高預算（svg 顯示高 ≤ ~515px + chrome）。**viewBox 寧窄勿寬**（scale 大 → 字大 → 全部文字過門檻）。
3. **CJK sublabel 是字級殺手**：中文每字 2× 寬，sublabel 帶 CJK 常被縮到 6.3-7px floor 而觸發門檻。解法優先序：縮文字（去 CJK/去裝飾詞）> 縮 viewBox 寬 > 犧牲內容。
4. **卡片（cards）行高參與頁高預算**：卡片 item 過長會 wrap 推高頁面；item 應單行（~40 chars 內）。
5. **低價值邊先砍再繞**：兩次 backward 邊（queue 前進、app-stats）引發交叉/穿點，依 archify 紀律移除並沉到卡片——比硬繞 via 便宜且語意更清楚。schema 驗證也擋 explicit pin（channelY）衝突——v2 compiler 自己排。
6. **repository evidence 可用且嚴格**：component `sources` 需 `meta.repository`（GitHub URL + 40-hex SHA），render 時以本地 git 驗證（origin 比對 + revision）。mosaic_alpha 私有 repo 有 GitHub origin 即可用——**這是 illustrate grounding 紀律（file:line 錨點）的原生支援**。
7. **視覺驗收閘門誠實**：visual-check 抓到 4/4 初版全部 overflow（我第一次交付 3 張失敗）——閘門不是裝飾，走完它的迴圈產物真的收斂。

## 與現況（Console/MD Mermaid）的分工定位

- Console（ASCII）：即時討論——不變
- MD（Mermaid）：知識沉澱（git-diffable、repo 內可 grep）——不變
- **HTML（archify）：展示級 artifact**——給人看/分享/post-build drift 審查時刻；JSON IR 是再生源頭應與 HTML 並存

## 價值驗收（vision agent 判讀，2026-08-30）

**Verdict：有條件價值——值得整合進 /illustrate，限定特定情境觸發。**

- **零渲染缺陷**：4 dark + 1 light 對比截圖全部無重疊/截斷/錯位；主題切換同構（確定性編譯驗證）
- **超越 Mermaid 的點**：truth 邊界與 guard 鏈的「許可權幾何」（邊界框顏色＋線型＋位置一併編碼）；資訊價值排序 **dataflow > architecture > workflow > sequence**（後兩者重疊度高、邊際低）
- **情境分化**：HTML 服務一次性人類 viewport（re-onboard、講解 Present、跨 repo 分享——互動搜尋/focus/reach/GUIDED VIEWS 對位軌道 ②）；Mermaid 服務 repo 文檔生態（git diff、AI 消費、常駐）——**受眾分流非取代**
- **代價可接受**的前提：不侵蝕常規流程——opt-in 觸發＋輪數 guard

整合條件（缺口→設計約束）：
1. **Repair 輪數上限 guard**：>N 輪（建議 6）自動降級回 Mermaid＋回報，防單次渲染吃掉 context 預算
2. **Mermaid 仍是 source of record**；HTML 是按需渲染的展示 artifact（防雙輸出漂移）
3. **AI 判斷增益**：mode D（溝通傳達）/post-build drift 審查等情境才觸發，非四型全上
4. **生命週期約定**：HTML 快照標註生成時間＋commit hash（drift 比過時 .md 更隱形）；JSON IR 與 HTML 並存為再生源頭

## 決策

**進 EP**：/illustrate 新增 html 輸出模式（opt-in），整合設計吸納上述四條件。EP：`ai-analysis/execution-plans/ep-illustrate-html-mode.md`
