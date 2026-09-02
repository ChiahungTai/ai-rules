# EP2：implement 全鏈善用 CR——分層換軌＋考古消化＋stale 清理

> 來源 handoff：`~/Github/code-reality/ai-analysis/handoff-ep2-ai-rules-implement-switchover.md`（凍結決策 §5 勿重辯）。baseline ai-rules `683215d`（開工 git log 對帳零後續 commit，無重疊）。供給端 v0.6.0 已發行（`code-reality --version` = 0.6.0+2b607c0；MCP 資料面四工具本 session tools/list 在場實證）。

## 段落 0：research spawn 三選一裁決

**裁決：② 維持 Explore＋CLI 查詢清單**（`8327ae4` 現狀），升級留待對照數據。

**理由（考古證據引用）**：
- 14% 滲透已翻案不可重現（一般 EP 消費 0/29；真實滲透 4-5%）；機制＝「接線在場但不在生產路徑」——graceful-degrade sidecar 無閉環（handoff §5.4、§7；候選源＝brainstorm §2.1 L41 歸因＋cutover-plan §3 決策表，標明非逐字「三分類」出處）。
- ② 自帶天然對照組：`8327ae4` 的 CLI-in-prompt 是 sidecar 形態，觀察窗從下一個 EP 起（brainstorm T2-1 設計）——先收一個 EP 的對照數據再決定是否升級 ①。**升級觸發條件**：觀察窗內 EP 段落 0 的 CR 查詢被實際執行（EP「依賴關係」小節出現 `[SRC]`／命令列引用）比例仍近零 → 證明 sidecar 形態閉環失效，才升級 ①（掛白名單 research agent，技術障礙已被 `8201987` 解除）。
- ③（複用 spec-miner 形狀）零考古證據支持；spec-miner 職責是逐字挖掘非全域掃描，形狀不匹配。
- 呼應凍結決策 #1（generic Explore→CLI 寫進 spawn prompt 是既定分層）；EP2 的換軌設計回應 sidecar-無閉環機制的方式＝**in-path 必填條文**（下游段落），不是多鋪一層接線。

## 段落 1：implement 分層換軌

`skills/implement/SKILL.md:166` 區：spawned review agent（code-reviewer 族 registry agents——白名單 `8201987` 已掛 CR MCP）查詢改 **MCP-first**（MCP `callers`／`impact_radius`）；CLI fallback 一行留給 generic Explore（spawn prompt 內帶 CLI 形態）。同段資料面指示翻轉 MCP 優先（`build`／`snapshot`／`delta_tour`／`project` MCP face v0.6.0 在場）。

## 段落 2：code-review／execution-plan／cr-query 同步

- `skills/code-review/SKILL.md:127`：「一律 CLI」改分層事實（registry agents MCP-first；generic 無白名單 spawn 才 CLI-in-prompt）。
- `skills/execution-plan/SKILL.md:161`：spawn 對象確為 Explore（裁決②），表述**精確化**非錯誤宣稱——「未掛 MCP／一律以 CLI」改「不在 CR MCP 白名單→CLI 寫進 spawn prompt；掛白名單 registry agents 走 MCP 優先」。Step 3 平行 Spawn 段（~:315-335）核對：spawn 對象 Explore read-only、無 CR 宣稱，無需改。
- `skills/cr-query/SKILL.md:29`：括號內「spawned agent 未掛 code-reality MCP」同步分層事實；:74 project 行補 MCP 雙面。

## 段落 3：MCP 面清單翻轉（凍結決策 #2）

`skills/code-reality/SKILL.md:21`：MCP 面從「四符號工具」翻轉為全面目錄（21 工具）——graph_query 家族＋資料面四工具 `build`／`snapshot`／`delta_tour`／`project` MCP face 在場；CLI 形態保留場景＝spawn prompt（無白名單 agent）與腳本。誠實界線條文（凍結 #3）已在場不動。

## 段落 4：考古換軌消化（§7 死掉模式表逐項判定）

| 死掉模式 | 判定 | 說明 |
|---|---|---|
| CRG MCP 工具條文（ep-codebase-sweep-command:109-119，08-26 retired） | **死得對** | CRG 退役；「EP 條文引用圖工具」形態由段落 0 CLI 清單承接（in-path 必填） |
| skills CRG 查詢面（cutover-plan §3.2「B 保留」） | **復活完成** | cr-query skill 承接查詢紀律面（本 EP 僅更新其分層括號） |
| CRG graph.db 作 CR 原料（tour-bootstrap:20） | **死得對** | 08-27 起 self-owned `.code-reality/graph.db`；原料鏈已斷且不回頭 |
| dependency 三件套＋scan_imports（mosaic 6a7129cd 08-30 退役） | **死得對** | 結構事實面改 CR graph——同向換軌，無需復活 |
| MCP callers 寫進 EP 條文（`8327ae4^`→`8327ae4` 改 CLI） | **歷史形態，部分復活** | 當時全 spawn 無 MCP 故改 CLI；本 EP 以分層翻回——限掛白名單 registry agents MCP-first，generic Explore 維持 CLI（裁決②） |

## 段落 5：mosaic 殘留回報

`/Users/ctai/Github/mosaic_alpha/.code-review-graph/graph.db`（151,552 bytes，mtime 08-28 19:51）在場——與「全刪」宣稱矛盾屬實。**本 session 不動 mosaic 檔案**（單一寫入者紀律）；回報 mosaic 端處置（read-only 驗證已做）。

## 驗收

- `rg -n "未掛 code-reality MCP|一律 CLI|一律以 CLI" skills/` 0 hits
- implement／code-review／execution-plan 三檔分層條文與白名單事實一致；裁決②寫進 EP（本檔段落 0）
- 考古逐項標「復活／死得對」（段落 4）
- docs mode 收尾：rg 殘留＋consistency gate；commit 待 user 確認
