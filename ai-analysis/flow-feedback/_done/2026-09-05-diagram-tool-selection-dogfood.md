# Flow Feedback — 2026-09-05 — 畫圖工具選型 dogfood（AIR-29 report shell 六圖）

## 來源（發現脈絡）

AIR-29 兩軸重構收尾補 report shell 圖。user 四輪指示把「光說不練的選型建議」逼成「六圖全 dogfood」（verbatim，09-05 20:01–20:13）：

1. 「是不是有些用 mermaid 比較好畫，不用強用 archify」「有些圖之前用mermaid不好用，有些是 archify 不好用，你嘗試看看」——**不強用任何單一工具**
2. 「沒法直接內刊mermaid嗎？且這種點進去沒用 md preview, 這之前不是說不能這樣用？」——退件 `implementation-diagrams.md`（mermaid code block 經 file:// 開＝純文字死鏈）
3. 「flowchart 我覺得很難用 mermaid」「class 圖也難用，簡單說 如果圖的 物件線條要交錯太複雜，不好用」「其他很像還好 循序圖等比較有規律的mermaid好用，你整理一下 sa 圖有哪些跟適合的畫法」——**核心判準**
4. 「你先dogfood 你的畫圖，先將 report shell 儘量嘗試畫圖，不要光說不練」——**選型結論不算數，畫出來才算**

## 核心判準（user 裁定）

**「如果圖的物件線條要交錯太複雜，不好用」**——判準不是圖的類別名，是**結構剛性**：

- **剛性結構**（時間軸、狀態機——線的路徑被結構釘死，無自由度）→ mermaid 自動布局（dagre）一次成功，零調校
- **自由 node-link**（流程圖、class 繼承網——線要自己找路，交錯不可避免）→ dagre 亂跳亂穿 = mermaid 死穴（user 點名 flowchart 與 class 兩類）
- **層次／對照**（內容本質沒有 edge routing 需求——不是圖論問題）→ HTML div/flex/grid 最乾淨，用 flowchart 畫分層是錯用
- **空間探索型全景**（需要 pan/zoom/search/focus）→ archify 本質優勢

## 選型表（六圖實證）

| 圖型 | 工具 | 實證案例（AIR-29 殼） |
|------|------|---------------------|
| 調用序／互動序 | ✅ mermaid `sequenceDiagram`（最強項） | 圖 A 投影機制（par/alt/loop 全用上）、圖 D muse post-build 逐階段模型分佈 |
| 狀態機（≤6 態） | ✅ mermaid `stateDiagram-v2` | 圖 E registry 檔案生命週期（owned/unmarked/drift/collision/stale） |
| ER／gantt | ✅ mermaid | （規律型同類，本次未用） |
| 多分支決策／分層架構 | ❌ mermaid → **HTML 塊圖**（div/flex 一層一塊＋▼ 衔接） | 圖 B dispatch 兩跳（第一跳→第二跳→權威表三層） |
| 前後／左右對照 | ❌ mermaid → **HTML grid 左右欄**＋色彩語義（rose=痛點/green=改善） | 圖 C 重構前後對照 |
| 架構全景（互動） | ❌ 手畫 → **archify**（JSON IR＋validate showcase 迴圈） | 圖 F 實作終態全景（11 節點×4 boundaries×11 connections） |
| 自由 flowchart／class 繼承網 | ❌ mermaid → HTML 塊（小）或 archify（大） | （user 點名難用，本次成功繞開零使用） |

## 渲染與嵌圖工程教訓

1. **md 檔 mermaid code block 不是「內刊」**：file:// 開 .md＝純文字（無 md preview 就不渲染）——未渲染 .md 圖集連結放殼＝死鏈，這是既有禁例仍被踩（累積失敗：本輪 `implementation-diagrams.md` 退件）。**圖要真的出現在頁面上**（渲染產物嵌殼），不是「原始碼在另一檔」。
2. **mmdc 渲染管線**：`npx -y @mermaid-js/mermaid-cli -i x.mmd -o x.svg -b transparent`（透明底可入任何殼配色；主題穩健性仍守 mermaid skill 既有規範——顯式 fill+color、無 init 配置）。
3. **mmdc SVG id 碰撞**：每張 mmdc 輸出都帶 `id="my-svg"` 且 style 全用 `#my-svg ...` 選擇器——**同頁多張 inline 互污染**（style 穿透＋arrowhead marker id 撞名）。解法：**每頁至多一張 inline**，其餘存檔＋`<iframe src="x.svg">`（iframe 隔離 id 空間）；或 id 全重寫（昂貴——實測一張 112 處）。
4. **（type-2 finding）mermaid 源未進 git——重現性缺口**：慣例是「投影源頭進 git、渲染產物不進」（archify 線有 JSON IR 進 git；.gitignore 已擋 `diagram-*.svg`）——但本次 mermaid 圖**只留了 gitignored 的 .svg，.mmd 源沒落檔**，clone 後 D/E 圖死鏈且不可重渲染。**修法**：mermaid 圖的 `.mmd` 源隨任務家進 git（與 archify JSON IR 對位），或至少在殼註解/附錄保留 mermaid 源碼——「源進 git、產物不進」原則需明文擴及 mermaid 線。
5. **殼嵌圖形態四種**（同殼可混用，按圖選載體）：inline SVG（≤1/頁，剛需快速可視）／iframe+svg 檔（其餘 mermaid）／iframe+`?embed=1`（archify，嵌 入模式）／HTML 塊直接寫殼內（層次/對照）；外框統一 frame-wrap（標題列＋↗ 全屏連結）。

## archify 適位與產線經驗

- 適位＝**架構全景空間探索**（互動 focus/pan/zoom/search），不是萬用圖床；規律型硬用 archify＝浪費 validate 迴圈（user：「有些是 archify 不好用」）。
- 產線可靠：本次 5 輪單調收斂（11→1→1→1→1→0 errors）、9/9 artifact checks、0 crossings。

### 踩坑預防（「很慘」的根因分析＋author 期前移）

**診斷**：R1 一次爆 11 errors 的根因不是工具缺陷——**拓撲寫完、幾何沒規劃**（11 條邊全交給 auto-router）。官方 invariants 其實有寫（side contract／crossing／8px-16px rhythm），但它們是「修復期查的規則」，不是「author 期套的檢查」。心得＝把修復期規則**前移到 author 期**：

1. **每條邊 author 時就分級**（R1 主因）：短相鄰邊→auto 可；**跨圖長邊或中間隔 container→必給 via/channelX/channelY 走邊緣通道**；垂直相鄰→釘 fromSide/toSide（auto 的 S 形會違反 side 契約）。法則：兩端跨 >2 個 node 欄寬就不要 auto。
2. **稠密區 label 先佔位**（R2/R5 兩輪）：邊標籤用 labelAt/labelSegment 指到長段，別讓 renderer 自放。
3. **viewBox 寬度預算與字級連動**（R3）：validator 的 desktop-readability 會驗「字級 ×（桌面寬 ÷ viewBox 寬）≥6px」——viewBox 越寬字投影越小（1480 時 9px 字投影 5.66px 不及格，壓到 1376 才 6.08px）。寬圖 author 時先水平緊湊，或拆兩張/改 HTML 塊。
4. **節點離 container 邊框留距**（R4）：貼邊節點的連線會沿邊框平行跑（border run）；對齊節點中線讓 route 成純垂直最穩。
5. **meta 欄位先查 schema enum 再填**（本次兩個 schema 偏離共同根因——「先寫再查」）：`schema_version` 是 **per-type const**（architecture=1、workflow=2——archify-gen 角色檔只標了 workflow 的 2，呼叫端易誤套到 architecture）；`meta.locale` enum 只有 `[en, zh-CN]`，zh-Hant 內容必須**省略 locale＋揭露 Viewer UI fallback English**（圖內 authored 內容不受影響）。

**流程面**：

- 修復迴圈**每次修一類、同類全修**——本次 R2-R5 每輪恰好 1 error 是「擠牙膏」形態（R1 修復時沒順手預防同類 label 位/貼邊）；只修 diagnosed subject＋每改重驗＋兩輪無改善停手（角色檔紀律已有）。
- **事實清單品質決定輪數**：呼叫端先分類主線/分支/消費（本次 6+2+3），agent 才能守「single main path + side branches from nearest node」；下一步是清單同步帶**幾何分類**（哪些邊跨圖、哪些垂直相鄰）。
- 修復順序固定：routing（crossing/corridor）→ label（clearance/labelAt）→ rhythm/readability。
- **schema 偏離要誠實揭露**（產線好慣例）：schema 事實如實報，不硬掰。

## 對位：ai-rules 吸收落點（delta 盤點）

| 落點 | 已有 | 缺（本次心得 delta） |
|------|------|---------------------|
| `skills/mermaid/SKILL.md` | 主題穩健性（fill+color/禁 init）、安全配色、emoji | **選型判準**（交錯=死穴、結構剛性判準＋何時不選 mermaid）、mmdc 管線、id=my-svg 碰撞與 inline×1 原則 |
| `skills/_common/illustrate-html-mode.md` | iframe 嵌入、`?embed=1`、產物位置分流（源進 git 產物不進）、archify 分工 | **圖型→工具選型表**進殼生成分工（report shell 補圖時選載體）、md 不渲染禁例重申、**.mmd 源進 git** 慣例補 mermaid 線 |
| `agents/roles/archify-gen.md` | 產線迴圈＋兩輪停手紀律 | 做法 2 補 **schema_version per-type**（architecture=1／workflow=2——本次偏離源）＋「meta 欄位值一律先查 schema enum」；可選：author 期五條預防收成 checklist |

## tags

`mermaid` `archify` `illustrate` `report-shell` `dogfood` `工具選型` `渲染管線`
