# 人類 viewport 供給架構——裁決記錄（preview server 淘汰／三層分工／放置規則）

> 形態：正式裁決記錄（architecture decision record）。參與：主 session（GLM-5.3）＋muse（xhigh，source 級查證）＋codex（chatgpt-web/high，官方文檔查證）三方諮詢；user 逐段裁定。bridge jobIds：muse `job-mtv3xc96-8apoz6`、codex `job-mtv3xcdr-gighkf`（諮詢全文 `.agent-tmp/vscode-preview-consult.md` 為 prompt）。

## 1. 起因：8765 撞埠連環事故（真實事件）

1. 舊 session 遺留 `http.server` 殭屍（PID 54235，serve mosaic 根目錄殼頁）佔住 8765。
2. mosaic 進行中 session（MOS-22.3 / 09-09-tree-registry-compiler 卡）需要 preview，埠被殭屍擋住。
3. 第三個 session（ai-rules 審查弧）依 handoff 慣例也想開 8765 → 撞牆改開 8766 → user 裁定「砍臨時、只留常駐」→ 誤砍 54235 後活 session 隨即搶到 8765（它其實是活著的）→ 停手，留待該 session 自行收掉（後已乾淨收除）。

根因：**臨時 preview server 無埠治理、無生命週期**——誰開哪個埠、session 結束誰關，全無慣例；`http.server` 活過 VSCode、活過 session，跨 session 佔埠。

## 2. 既有常駐層盤點（全部實測）

| 埠 | launchd | 角色 |
| --- | --- | --- |
| :6420 | `com.mosaic.backlog-browser` | mosaic Backlog.md board |
| :6422 | `com.ai-rules.backlog-browser` | ai-rules Backlog.md board |
| :6421 | `com.mosaic.report-server` | 共享靜態路由（panel serve）——`main`/`v2`/`warrant`（mosaic WT）＋`ai-rules`＋`viewer`；**讀活磁碟，未 commit 的 WT 內容直接可達**（當日 blueprint 未 commit 頁即經此 serve，實測 200） |

事實源：mosaic `deploy/scripts/run-report-server.sh`（:6421 腳本，跨 repo）＋各 repo `run-backlog-browser.sh` 註解＋`schedule-registry.md` 條 A5。board=per-repo plist 先例×2；report shell=共享單體多 route——「新專案接 report shell＝加一條 static route」的擴充機制既已存在。

## 3. 需求演化（三段收縮）

1. **初始 spec（中弧）**：preview 慣例（先查 6421）＋6421 擴 route 到 repo 根＋route 註冊 carrier 中立化（現寫死在 mosaic 腳本）＋新專案 onboarding runbook。
2. **user 實用法揭示**：「我其實只要有路徑就可以看了」——VSCode 點開即看（user 已在用），server 議題在日常預覽面消失 → route 擴充失去主要消費者。
3. **codex 翻案補強**：VS Code 1.121 起內建 Integrated Browser（右鍵 `.html` → Open in Integrated Browser），`file:` 直載、零 server 零埠零擴充——真·零 server 的原生路徑，三層方案的第一層由 Live Preview 改判為內建瀏覽器。

user 最終問題收斂：「要放在哪——我好找、夠簡單的目錄規則」。放置規則既有定案（illustrate-html-mode「產物位置分流」，user 當時拍板「開心目錄、一弧一殼」）直接沿用；`file:` 直開使放置不再受 6421 route 覆蓋範圍約束，規則純為「好找」服務。

## 4. 三方諮詢要點

**muse**（讀 `ms-vscode.live-server-0.4.20` 原始碼）：Live Preview 是 managed server 非「零 server」，但生命週期綁 VSCode window（不存在跨 session 殭屍）；多 window 埠自動遞增自癒；與 :6421 零實務衝突風險（處方＝永不釘 `portNumber`）；`autoRefreshPreview` 預設 "On All Changes in Editor" 對看 report 有害（別檔打字→report 整頁 reload、scroll 丟失）→ 釘 Never；**命名空間規則**：ephemeral 埠 URL 永不進持久引用。

**codex**（官方文檔）：VS Code 1.121+ 內建 Integrated Browser 為真·零 server 主路徑（本機 1.136.2 已具備）；Live Preview 0.4.20 預設走 Integrated Browser 時，關分頁**不**觸發 keepAlive dispose timer——「關 preview 數分鐘自動收 server」在該路徑不是 invariant（推翻 muse 同項推論）；6421 重定義為 **addressability layer**（stable URL namespace），非「為了預覽存在的 server」；`file:` 與 http URL 是不同 origin，localStorage 不共享；建議全域 `workbench.browser.autoReloadOnFileChange: true`（disk change reload，覆蓋 AI 落盤情境）。

**主 session**：原判 Live Preview 為主層＋YAGNI 真零 server——經 codex 糾正為「內建瀏覽器為主層；真零 server 原生存在」；YAGNI 判詞從「同等 UX」修正為「架構上無免費路徑→如今連自建都不必」。

## 5. 終態架構（裁決）

| 用途 | 載體 | 性質 |
| --- | --- | --- |
| 日常點開 artifact | VS Code 內建 Integrated Browser（`file:` 直載） | 零 server、零埠、零擴充 |
| board 卡 refs／跨 repo 穩定引用／md viewer | `:6421` report-server 常駐 | addressability 層；stable URL 契約 |
| 手改 HTML 未存檔即時刷新 | Live Preview 擴充 | 選配；埠隨 window 漂 |

規則四條：

1. **臨時 server 淘汰**——session 不再自建 `http.server`；交付路徑（user 點開）或 :6421 URL（deep link）。
2. **命名空間**——Live Preview／任何臨時埠 URL 永不寫進 board 卡或持久引用；持久引用只用 :6421。
3. **artifact 慣例**——人類 viewport 產物維持自包含單檔 HTML（資產內嵌、無外部 fetch），`file:` 直開成立的前提。
4. **origin 分離**——`file:` 與 `:6421` 不同 origin，localStorage 各自保存，不作跨入口契約。

放置（規範源不變＝illustrate-html-mode「產物位置分流」）：弧產物→任務家（入口 `index.html`）；常設 domain 導覽→`ai-analysis/<域>/`；按需結構視覺→repo 根 `arch-report/<主題>/`；md→`ai-analysis/reports/`。心法一句：「會動的都在 `ai-analysis/`、弧的家照日期命名、入口一律 `index.html`」。

新 repo onboarding：viewport 面**零步驟**；需 deep link 才加 :6421 route（opt-in）。

## 6. 取消項（曾評估、user 實用法成立後取消）

- :6421 擴 route 到 repo 根（`file:` 直開後無主要消費者）
- route 註冊 carrier 中立化（route 清單不再擴張，異味維持現狀不動）
- 新專案 viewport onboarding runbook（零步驟後無 runbook 可寫）

## 7. 待落檔（併 handoff「四小項已定案未落檔」批）

1. session 交付慣例句（handoff／illustrate-html-mode 端）：給路徑或 :6421 URL，禁開臨時 server。
2. 全域設定 `workbench.browser.autoReloadOnFileChange: true`（user settings，一次）。
3. 命名空間句（kanban refs 慣例）：卡上只放 :6421 URL。
4. 目錄心法句（blueprint workflow viewport 節已承載，本 report 為源）。

## 8. 驗證證據

- `curl 6421/ai-rules/blueprint/index.html` → 200/59KB（未 commit WT 內容可達）
- `launchctl list` 三 plist 在位；`lsof` 8765 釋放後零 listener
- `code --open-url "vscode://simpleBrowser.show?url=…"` 送達成功（session 程式化開頁路徑）
- 諮詢 bridge ledger：`.delegate-bridge/jobs.json`（兩 job completed, exit 0）
