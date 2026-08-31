# CR 導入效益評估：/execution-plan 與 /implement 的 prompts/tokens 前後對比

> 排程執行（2026-09-01 00:20，usage reset 窗口；origin：user 2026-08-31 19:27 `/at 00:20`）。
> 資料源：ZCode 遙測 DB `~/.zcode/cli/db/db.sqlite`（model_usage / tool_usage / part / session）＋ ai-rules git log。
> 量測腳本與中間產物：`ai-rules/.agent-tmp/`（q_*.sql、episodes.csv、bashmix.csv 等，可重用重跑）。

## 判定（TL;DR）

**不如預期——減量機制根本沒啟動。** 換軌後觀察窗（08-30 11:16 ~ 08-31 10:00）消費端 EP/implement 流程的 CR 結構查詢執行數為**零**；implement 用量不降反升（median requests 166→200、fresh input ×2.0）；EP 用量 median 大降（42→12 requests）但**不可歸因 CR**（CR 零執行、n=8 小樣本、任務組成不同）。EP2 自己定義的**升級觸發條件成立**：應執行升級①（research agent 掛 CR MCP 白名單）。

## 1. 上線時間線（git 證據）

| 時間 | commit | 內容 |
|---|---|---|
| 08-22 00:42 | `ad66919` | CR 工具鏈三接線（implement baseline snapshot——首次，順手用形態） |
| 08-26 | `da2f19d`/`b137940` | cutover：skills 切到 Rust carrier |
| 08-29 22:42 | `8327ae4` | **EP 段落 0 CR 接線**：spawn prompt 帶 CLI 查詢清單＋EP 工具證據 |
| **08-30 11:16** | **`618a9f8`** | **EP2 主換軌：CR 消費分層——MCP-first（白名單 registry agents＋主 session）、CLI 留給無白名單 spawn** |
| 08-31 14:27 | `d024d7e` | rules 層 cr-first 路由（lsp-navigation）——**晚於全部 after 樣本**（見 §5 時間窗邊界） |

測量分相：before = < 08-29 22:42（12 天）；transition = 08-29 22:42~08-30 11:16；**after = ≥ 08-30 11:16（1.5 天，EP2 換軌生效窗口）**。

## 2. 量測方法

- **Episode 歸因**：part 表 Skill invocation（`execution-plan`/`implement`）建立 per-session 時間軸，request 歸給「最近一次 Skill invocation 起至下一次」（與 08-25 implement-request-amplification-analysis 同口徑；暈染兩邊對稱，前後對比公平，但絕對值含後續 coding 暈染）。
- **主 session＋子 session**：subagent 成本在 child sessions（session.parent_id），主口徑外另計（children.csv）。
- 消費端定義：排除 `~/Github/code-reality`（dogfooding）。

## 3. 核心數據

### 3.1 用量對比（per-episode median；all repos）

| skill | phase | n | requests med | fresh input med | input_tokens med |
|---|---|---|---|---|---|
| execution-plan | before | 35 | 42 | 342K | 13.0M |
| execution-plan | after | 8 | **12** | **141K** | **3.2M** |
| implement | before | 37 | 166 | 896K | 63.1M |
| implement | after | 6 | **200** | **1.79M** | **83.8M** |

- EP 降幅大（requests −71%、in_tok −75%）**但不可歸因 CR**：after 樣本 n=8、含多個 trivial 調用（0-15 requests 的 "task brief"/"side chat" 級）、任務組成不同（before 有 nautilus/codetour 重規劃）；且窗口內 CR 零執行——沒有作用機制。
- implement **不降反升**（+21% requests、fresh ×2.0、in_tok +33%）：n=6 且任務重（memory 治理弧、ui-test-parity S1-S3），在任務混雜噪聲內；誠實結論＝**無減少證據**。

### 3.2 CR 實際執行（換軌後觀察窗，主＋子 session）

| 消費形態 | EP | implement |
|---|---|---|
| Bash 結構查詢（scip_refs/graph_query/hub_refs/delta_tour） | **0 / 670** | 9 / 1813 |
| 主 session MCP CR 呼叫 | 0 | 0 |
| 子 session（registry agents）MCP CR 呼叫 | 0 | 1（refs，380B） |
| cr-query Skill 調用（全 DB 史上） | — | **0 次** |
| EP 產出 `[SRC]` 引用（mosaic 消費端） | **0 檔** | — |

implement 那 9 次匹配逐條核實為 `tour_validate`／`--version`／路徑誤配（memory 檔名含 code-reality），**無一是結構查詢**。

### 3.3 Before 窗口「使用」的真相（度量汙染）

消費端 before 窗口 Bash 有 8.8-10.3% 匹配 `code-reality` 字樣——per-session 明細核實為**mosaic 舊 Python CR 套件遷移工程**（`test_hub_refs.py`/`hub_refs.py`/`delta_tour.py` 檔名誤配我的 pattern）＋ legacy `uvx code-review-graph`——非 EP/implement 流程消費。與 EP2 考古一致（真實滲透 4-5%、一般 EP 消費 0/29）。

## 4. 判定與修正方向

**判定：不如預期。** 「CR 導入 → EP/implement 省 token」的因果鏈在第一環就斷了——條文在場、行為不在場（in-path 必填條文上線 1.5 天後滲透仍零）。implement 面另有結構性原因：其 hotspot 是 request 批次化與 Read 紀律（`d4e3820`/`a0b2889` 已修兩波），符號查證只佔小塊——**CR 即使滲透成功也動不了 implement 用量大頭**。

**修正方向**（優先序）：

1. **執行 EP2 升級①（主修正）**：research agent 掛 CR MCP 白名單（技術障礙 `8201987` 已解除）——把「CLI 寫進 generic Explore prompt」（sidecar）換成「spawn 專用 agent 自帶 MCP」。修的機制正是 EP2 診斷的「接線在場但不在生產路徑」：generic agent 的工具可見域裡沒有 CR，prose 清單會被跳過；白名單 agent 的工具清單**就是**生產路徑。
2. **重新定位 CR 價值主張**：從「省 token」轉向「結構證據品質」（ripple 宣稱機械反證、死路假設偵測——`_lazy_populate` 案例）。token 論述只在 EP 面成立且以滲透為前提；implement 面減量槓桿在批次化/Read 紀律，不在 CR。
3. **修度量 pattern（本次實測教訓）**：滲透量測改用帶 subcommand 錨的精準 pattern（`code-reality (scip_refs|graph_query|hub_refs|impact_radius|snapshot|delta_tour) `）且排除 `~/Github/code-reality` 路徑與消費端 repo 自帶同名檔案；或直接數 tool_usage 的 MCP 工具名（零誤配）。「什麼算一次 CR 消費」的契約應定義進 cr-query skill。
4. **再收 2-3 天數據再裁**：rules 層 cr-first（`d024d7e`）＋00-tasks 重構（`1c9ea1e`）都在 08-31 14:27 後落地——「EP2＋cr-first 雙加持」的觀察窗當時才開始、目前零數據。若升級①落地，用 `.agent-tmp/` 既有腳本重跑本測量驗收。

## 5. 時間窗誠實邊界

- after 窗口最後樣本 08-31 09:55，**早於** rules 層 cr-first 路由（14:27）——本報告測的是「EP2 換軌單獨加持」窗口。
- 但 EP 段落 0 in-path 條文自 08-29 22:42 生效 1.5 天滲透仍零——升級觸發條件的判定不受此邊界影響。
- after 樣本小（EP n=8、impl n=6）：方向性結論（滲透零、implement 無減少證據）穩；用量百分點勿過度解讀。

## 6. arch-thinking 三視角收尾

- **依賴規則（分層）**：宣告層依賴方向正確（skills→pointer→工具，無實作複製）。斷裂在**宣告式依賴 ≠ 行為式依賴**：skill 條文聲明依賴 CR，runtime LLM 在生產路徑跳過。對 LLM 消費者的架構，prose 接線沒有機械閉環——cr-query GATE 的 assume+warn 是被動版，升級①的白名單 agent 是結構版（把依賴放進工具可見域，而非文字）。這是本次最重要的架構教訓。
- **bounded context**：ai-rules（用法定義）/ code-reality（實作）/ 消費端（profile＋graph.db）三邊界清楚，無跨界違規。缺口＝**滲透量測無 owner**：本次手動量測才發現 pattern 汙染；量測契約該歸 cr-query skill（修正 3），定期量測可掛治理看照 cron 或 cr-demand 卡。
- **use case 驅動**：「省 token」需求對 implement 結構性不成立（hotspot 在別處）、對 EP 理論成立但未啟動；已被反覆驗證的價值在證據品質面。use case 應改寫為「EP 依賴宣稱的機械反證」為主、token 為副產品。

## 附錄：資料檔

`.agent-tmp/`：`q_episodes.sql`/`q_diag2.sql`/`q_consumer.sql`/`q_detail.sql`（可重跑）、`episodes.csv`（96 episodes 明細）、`toolmix.csv`、`bashmix.csv`、`consumer_bashmix.csv`、`children.csv`、`childcr.csv`、`aftersessions.csv`、`before_cr_sessions.csv`、`after_cr_cmds.csv`、`aggregate.py`。
