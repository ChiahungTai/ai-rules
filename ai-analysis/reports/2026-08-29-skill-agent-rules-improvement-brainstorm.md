# ai-rules 治理體系改善 Brainstorm——Uncle Bob 視角 × mosaic 兩週實證 × CR 接線翻轉

> 產出：2026-08-29 deep-work 自主 session（用戶睡覺中）。**v2 終稿**——v1 草稿經魔鬼代言人對抗攻擊後修訂（攻擊抓到 v1 一個致命事實錯誤與多個計數錯，全部修正，見 §5.2）。證據鏈：Uncle Bob 訪談蒸餾＋三平行調查 agents（mosaic 遙測全量／ai-rules 結構審查／mosaic EP 語料）＋flash lite-verify 獨立覆核＋魔鬼代言人攻擊＋翻案宣稱本 session 親驗。**未 commit**——等用戶醒後判讀裁決。

## 0. TL;DR

**核心診斷：「工具在場、紀律在檔、接線不在生產路徑上」**——ai-rules 已把 Uncle Bob 說的「價值」文件化得相當完整（證據階層、UC-driven、writer/reviewer 分離、軌跡管理甚至領先其建議），但「價值要用確定性工具守住」這一半：
1. **對自己豁免**——治理工具鏈零測試、檢查是散文、hook 孤兒、allowlist 與規則對著幹（§2.3，7/7 獨立覆核成立）；
2. **CR 接線是 sidecar 不是 in-path**——三閘接線 08-22 起全程在場（ad66919＋四次強化），但全是「未裝跳過，不阻擋」的 graceful-degrade 消費，EP 作者的生產路徑（段落 0 依賴分析）從不被迫經過 CR → 兩週 0/29 一般 EP 消費 CR 結構查詢、`cr-query` skill 0 次真正調用（§2.1）；
3. **always-on 預算 95.3% 滿載**——同時行為遙測證明規則在檔、行為照樣衰減（§2.2），「更多規則」不是解方。

**提案**：T1 結構修復五項（低阻力）／T2 系統演進四項（旗艦＝CR projected graph overlay：把 EP 證據從「LLM 讀碼」翻轉為「in-path 必填的機械查詢產物」）／T3 spike-first 與決策項四項。

---

## 1. 輸入與方法

| 輸入 | 內容 | 狀態 |
|---|---|---|
| Uncle Bob 訪談（[Cash Wu 節錄](https://blog.cashwu.com/blog/2026/uncle-bob-ai-software-fundamentals)，Matt Pocock 57 分鐘訪談） | 七論點：①prompt 規則衰減→確定性工具 ②初始 prompt 縮最小 ③pipeline 拆分保單純軌跡 ④紀律可鬆、價值用工具守 ⑤舊工具復活（CRAP/變異測試，利用 agent 速度）⑥SDD 懷疑、spec 價值在寫的當下 ⑦架構仍需人類 | 全文讀取 |
| mosaic 遙測全量 | 08-15~08-29：285 sessions（75 main）、11,226 Bash commands、2,360 則 user text 全量掃 | Agent A |
| ai-rules 結構審查 | fresh eyes、Clean Architecture+DDD 視角、F1-F10＋機械化候選 | Agent B |
| mosaic EP 語料 | 兩週 239 commits、36 新建 EP 全讀、CR 滲透獨立覆核 | Agent C |
| 獨立機械覆核 | Agent B 的 7 項結構宣稱重算 | lite-verify **7/7 成立** |
| 魔鬼代言人攻擊 | v1 草稿逐提案攻擊＋事實查核 20 項＋與用戶既有裁決衝突檢查 | 抓到 v1 一個致命錯（§5.2），已修訂 |
| CR projected graph 想法 | sess_2fe1ad7c（EP 撰寫/ep-review 應受 CR 支撐；overlay 機制 POC 全綠） | ReadSessionContext |

**對抗驗證設計**：宣稱→獨立重算（lite-verify 覆核結構面；魔鬼代言人覆核行為面與事實前提）；滲透率→雙源交叉（遙測面 vs EP 語料面）；翻案宣稱→本 session 親驗（git show＋檔案直讀，不信任何單一 relay）。

## 2. 證據基礎（關鍵數字＋各自覆核狀態）

### 2.1 CR 滲透率——雙源交叉定案＋歸因修正

| 口徑 | 數字 | 覆核狀態 |
|---|---|---|
| 原宣稱（sess_2fe1ad7c） | 3/21 (~14%) | **不可重現**（魔鬼代言人＋Agent C 均無法重建分子分母；~14% 恰等於 LSP 滲透率 4/29=13.8%，疑似誤歸） |
| EP 語料面 | **0/29 一般功能 EP 消費 CR 結構查詢**（pattern 命中皆假陽性："closure 捕獲"、"market closure"） | Agent C；魔鬼代言人方向覆核 ✅（分母 29 的切法不可獨立重現，量級成立） |
| 遙測面（session 粒度） | 14/75 sessions 有任何 CR 使用，**~10 個是 CR 自身開發迴路** → 功能 EP 消費 ≈ 2-3/57 (4-5%) | Agent A |
| `cr-query` skill | **Skill 工具真正調用 0 次**（魔鬼代言人全庫重驗 ✅）；散文提及數十次（量級，具體次數不可重現——v1 引 42 次已撤） | 「知道的人多、真用的人少」成立；可證明的是**觸發/可發現性失效**，非「紀律下達後失效」 |

**歸因（v2 修正，本 session 親驗）**：Agent C 曾宣稱「thin-layer EP 明言的 ai-rules 接線至今未做」——**錯**。`git show ad66919`：08-22 00:42 已落地三接線（implement baseline snapshot／code-review primed transition 底稿／debrief 機械底稿），其後 6a5c591、7ba1894、da2f19d、5786151 四次強化；現行 `skills/implement/SKILL.md:79`、`skills/post-build/SKILL.md:37`、`skills/debrief/SKILL.md:44` 三閘全在。**但這些接線全是 graceful-degrade sidecar**——implement:79 原文「未裝跳過，不阻擋」、debrief:44「未裝、缺 snapshot 或時點不符 → LLM 推導（既有行為不變）」。且消費時點全在 build 之後（post-build/debrief 的事後對照），**EP 作者撰寫段落 0 時的生產路徑從不經過 CR**。08-23 CR 落地 mosaic 後新生的 ~8-11 個一般 EP 依然零消費——接線在場但不在生產路徑上，這才是 0 滲透的機制。

（另：段落 0 的 CR CLI 接線〔commit 8327ae4〕是 08-29 22:42 才落地——晚於全部 36 個 EP，它的效果是真正的未來式，尚無對照數據。）

### 2.2 規則衰減的行為證據（Uncle Bob 論點①的實證；全部來自 ZCode 側遙測）

| 規則（rules/ 內） | 兩週實測行為 | 量級 |
|---|---|---|
| 統計用途禁 head 截斷 | `rg \| head` ~3,750 次（約三分之一的 Bash commands）vs `\| wc` 148~308 次（口徑敏感） | head 壓倒性主導，**1~2 個數量級**（精確比值隨 scoping 變動 17:1~26:1，取量級不取精確值） |
| rg-first（禁 grep 搜尋） | grep 搜尋用途 ~464 次＋pipe filter ~268 次 | — |
| 禁 sed 改檔 | `sed -i` **39 次**（魔鬼代言人重算位元級精確 ✅） | — |
| Python 一律 uv run | 裸 python **319 次**——多為 heredoc `pathlib.write_text()` **改檔繞道**（同時繞 Edit 工具＋sed 禁令；現行規則文本未覆蓋此型態） | — |
| 禁外部 timeout | 59 次 | — |
| Read 紀律 | 206 個 (session,file) 對重讀 ≥3 次、66 對 ≥5 次、最高 x18（片段讀為主，部分生效） | 最大宗可量化 token 浪費 |

### 2.3 ai-rules 結構 findings（lite-verify 7/7 獨立覆核全成立）

| # | Finding | 嚴重度 |
|---|---|---|
| F1 | bundle 87,808 bytes = 90KiB gate（92,160B）的 **95.28%**；歷史是鋸齒（135KB 時期 → 08-24 砍到 79.7KB → 五天回升 87.8KB）——逼近是真的、線性外推無意義；model-routing（5.3KB）承載 churn 最快的 provider 事實（rate limit 表自承可能滯後、thoughtLevel bug 遙測數據點）佔 always-on 預算 | 🔴 |
| F4 | `rules/context-management.md:24,36` 的 `../skills/` 跨域 ref **活違規**進三端 bundle（中性化檢查是散文命令、從未被機械執行；無 `bundle: skip` marker） | 🟡 |
| F5 | deploy 斷 ref gate（`deploy_agents.py:244` 只掃 rules/）不掃 guide；guide「詳見 code-edit-constraints.md」在非 Claude 端是死指標 | 🟡 |
| F8 | `hooks/compact-tail-inject.py` **孤兒**——Claude settings.json 與 zcode-registration.json 皆未註冊，從未生效 | 🔴 |
| F9 | 治理工具鏈 **9 .py、0 測試**（load-bearing 者約 5 個：deploy_agents、check_single_source、3 攔截 hooks） | 🔴 |
| F10 | repo 內 settings.json（symlink 到 ~/.claude）:131/271 預批准 `Bash(python3:*)`/`Bash(python:*)`——與 python-standards/tool-discipline 硬禁矛盾（grep:135/find:142 掛在「純讀取」段下，屬刻意分類、非矛盾） | 🟡 |
| F2 | guide↔rule 同句雙源已實際漂移 3 組（向後相容條件 guide 3 條 vs rule 4 條、數據完整性、SOLID 清單） | 🟡 |
| — | **既有 Backlog 卡兩張未被 v1 引用**（grounding 失敗）：`bundle-layered-diet.md`（同主題 deferred 卡，帶品質護欄與觸發條件）、`mechanical-gate-philosophy-hybrid.md`（「機械閘門 > LLM 自覺」哲學本體，2026-06-17 flow-review 已定調——本報告 §3.4 的 Uncle Bob 對映實為該原則的重述） | 整併 |

### 2.4 用戶糾正模式（~30 真糾正 / ~20 sessions；約 1/4 main session 被明顯糾正）

頻率排序：**理解/方向錯 8** ＞ 重複勞動 6（whole-picture blind spot：「為何又要重新發明？做之前沒有查 system map 嗎？」）＞ 遺漏 5（「只掃 make 引用會漏直呼 pytest」——雙掃教的坑）＞ 修了仍壞 4 ＞ 過度工程 3 ＞ **驗證責任推給用戶 1（質重）**：「你這不能用 playwright 自己驗證嗎？我這樣很累誒」——L4-L6 執行驗收缺口的直接怨言（v1 引用後丟下，v2 已升為正式提案 T3-4）。

### 2.5 工作流健康面（好消息）

- EP 工作流採用 76%（57/75）；arch-thinking 23 次調用（非流程類最高）——結構視角已吸收進日常
- B 軸 viewport 有消費：debrief ~10 次、illustrate ~11 次（唯 smell-detector 掛零，見 T3-3）；驗證文化：pytest 847、ruff 558、mypy 288 commands
- Capabilities 無膨脹（+41/−40 淨 +1）；doc-diet 運轉中；宣稱→commit 忠實度抽樣 3/3
- EP Review 回寫紀律真的在抓 overclaim（「量測宣稱靜態不可驗→標註 POC 口徑」）

---

## 3. 核心診斷（arch-thinking 三視角 × Uncle Bob 對映）

### 3.1 use case 驅動缺口——sidecar vs in-path（歸因修正後更清晰）

CR 故事是教科書級案例：消費者 use case 是「EP 作者需要 ripple/下游證據」，CR 的形態卻是「on-demand 查詢 skill＋事後對照 sidecar」。三種接線（snapshot/delta_tour/primed 餵料）都設計成**可靜默降級**（「未裝跳過，不阻擋」）——這在「不確定工具在不在場」的部署現實下是合理的防護，但後果是：**EP 作者的生產路徑上沒有任何一點被迫經過 CR**。42 次提及 0 次調用＋0/29 EP 消費，就是這個結構的必然輸出，不是 LLM 不乖。

**關鍵區分（v2 新增，回答「為什麼 projection block 不會步 snapshot 後塵」）**：sidecar 消費的失敗模式是「靜默跳過沒人知道」；in-path 必填的失敗模式是「缺欄被 ep-review F3 直接 flag」——前者無閉環、後者有閉環。T2-1 的設計核心就是把 CR 從前者搬到後者。

**Uncle Bob 對映**：guideline（可選查詢）永遠輸給 inertia（LLM 讀碼湊答案）；只有 rule＋closed feedback loop（必填產物＋審查兜底）改變行為——xfail strict 已在我們體系內證明過一次。

### 3.2 治理自我例外（bounded context 內聚失效）

ai-rules 的職責是「把品質要求變成 agent 無法忽略的確定性檢查」，但 context 內部：檢查命令以散文存在（F4）、自己零測試（F9）、hook 孤兒（F8）、allowlist 拆自己的台（F10）。四個不是獨立 bug，是一個模式：**治理體系對自己豁免了它賣給別人的紀律**。且該哲學早有正式決策源（mechanical-gate-philosophy-hybrid 卡）——問題不是缺哲學，是哲學沒有涵蓋到自己頭上。

### 3.3 always-on 預算耗盡（lost-in-middle 字面化）

95.28% gate 滿載＋行為衰減實證（§2.2）＝「規則越多→單條注意力越稀釋→越需要機械化→機械化後規則可退場→bundle 變小」的正向循環起點。ZCode bundle 內真正的結尾自檢清單是 **2 條**（deep-thinking、llm-output-convention；code-edit-constraints 是 Claude-only）——acceptance-evidence 的原話是「自審＝**零獨立性驗證**」（抓不到共享盲點），非「零注意力效果」（不可觀察，不下此斷言）——刪除在 token 帳上成立，理由用前者。

### 3.4 Uncle Bob 七論點對映總表

| # | 論點 | ai-rules 現況 | 判定 |
|---|---|---|---|
| 1 | prompt 規則衰減→確定性工具 | hooks 先例已走通（python -c 攔截）但多條硬禁仍純 prompt（§2.2 量化衰減） | **主要缺口**（=mechanical-gate-philosophy-hybrid 卡的既有定調） |
| 2 | 初始 prompt 縮最小 | bundle 95.28% 滿 | **直接衝突** |
| 3 | pipeline 拆分保單純軌跡 | 一 EP 一 session、writer/reviewer 分離、agent 出生-完成-死亡 | ✅ 領先 |
| 4 | 紀律可鬆、價值用工具守 | xfail strict 先例正確；自檢清單屬可鬆紀律 | 部分做到 |
| 5 | 舊工具復活（agent 速度） | flash 並發已用於 verification（本報告即例）；變異測試未試（T3-2 spike） | 機會點 |
| 6 | SDD 懷疑、spec 價值在寫的當下 | 段落式 EP > 大計畫已內建；spec 已退役為需求釐清 | ✅ 領先 |
| 7 | 架構仍需人類 | B 軸 viewport 在消費（debrief/illustrate）；執行驗收 L4-L6 一格仍空（T3-4） | 對齊但有缺口 |

---

## 4. 提案

### T1 結構修復——「把已經寫好的檢查跑起來」（阻力低；機械閘門哲學卡的運營化）

**T1-1 deploy gate 擴充**（F4/F5）
- rules/AGENTS.md:136-150 五條中性化 rg 檢查搬進 `deploy_agents.py` pre-deploy（命令現成）；`check_broken_refs` 納入 guide 掃描；修 context-management 兩處跨域 ref＋guide 死指標
- **實作陷阱**（魔鬼代言人）：naive `rg '\.\./(commands|skills)/' rules/*.md` 命中 4 處——rules/AGENTS.md:87（規範表格）與 :111（❌ 錯誤示範 codeblock）是檢查文檔自身，須排除
- **宿主選擇**：掛 deploy gate（不過就擋部署）而非 /sync-sources invariant——兩者是重疊機制，deploy 是更硬 chokepoint；差異須在實作時說明
- 驗收：gate 內機械執行、現有 2 活違規歸零、guide 死指標消除

**T1-2 治理工具鏈測試化**（F9）
- 為 load-bearing 純函式補 pytest（~5 檔：`CLAUDE_NOTE_PATTERN`、`slim_for_bundle` marker 配對、`is_violation()`、`read_scope`）；**先決定測試落點**（`tests/` 不存在，naive `pytest scripts/ hooks/` 是 trivially green 的假驗收）
- 掛 **git pre-commit hook**（確定性）而非 /commit skill 內提示（prompt 級——v1 方案自反）
- crawl.py（網路爬蟲）測試價值低，不強求

**T1-3 hook 註冊完整性 invariant**（F8）
- check_single_source 新增：`hooks/*.py` 每檔至少出現在一個註冊處（settings.json / zcode-registration.json），否則 critical
- 連鎖清理：裁決 compact-tail-inject.py 去留（兩端皆死路/未接線）——若刪，`skills/compact-prep/SKILL.md:31` 條件句同步清理

**T1-4 allowlist 矛盾清理＋heredoc 堵漏（重組版）**
- **allowlist（Claude 側真矛盾）**：移除 settings.json:131/271 的 `Bash(python3:*)`/`Bash(python:*)` 預批准。誠實邊界：衰減證據（319 次裸 python）來自 **ZCode 側**遙測、settings.json 是 **Claude 專屬**——此修法修的是「Claude 端與規則矛盾」本身，**不是** ZCode 衰減的解藥；副作用（互動初期權限提示變密）需接受。grep/find 在「純讀取」段屬刻意分類，不動
- **heredoc 繞道（319 次）**：v1 提案「增補規則文本」**違反自家不做清單 #1**（同源證據兩種藥方），撤回。改機械化優先：PreToolUse 偵測 heredoc 內 `write_text|open\(.*['"]w` 寫檔 pattern（可行性 spike——誤傷率待測）；規則增補降為次要（僅在 hook 不可行時）
- **ZCode 側權限面盤點**（新增）：量到的衰減在 ZCode——ZCode 端權限配置（permission/defaultMode）有無等效「預批准拆台」項，一小時盤點可清

**T1-5 guide 銜接機制補 post-build**
- guide「銜接機制」三步鏈（execution-plan→Backlog／build→結算／commit）缺 post-build 環節；用戶實證困惑（sess_825078e2「post-build 應該不是 commit 後…是 ai rules 寫錯嗎？」）——文檔沒錯（post-build SKILL:70,79 明載止步 commit 前）但鏈條缺一角。一行修復
- 樣本僅 1 事件，但成本一分鐘——低證據低成本，照做

### T2 系統演進——「翻轉證據生產模式」（需小 EP 規劃）

**T2-1 CR projected graph overlay 落地（旗艦提案，源自 sess_2fe1ad7c）**

*為什麼是對的方向*（三路證據＋修正後歸因）：
1. EP 三大盲區（Pattern Alignment 錯、下游依賴沒看到、跨模組漣漪）**0/29 有機械證據**——依賴錨點全靠 LLM 列舉、推導工具不透明（29 EP 僅 1 處明示 LSP；f4-removal 初版漏列呼叫鏈靠 review 補）
2. **sidecar 接線已被證明無效**（08-22 起三閘在場、0 滲透）——「接線」的正確形態不是更多消費點，是 in-path 必填
3. overlay 機制零 graph_db 改動、POC 全綠（24 callers=23 真實+1 投影、graft site 自動配對、零邊洞檢測可行）

*落地形態*：
- 工具側：`code-reality project --overlay <plan.toml>`（CR repo 小 EP 已寫，baseline ff6dafa）——hub-relay 模式：CR repo 擁工具、ai-rules 擁接線、mosaic 擁 profile
- ai-rules 側：execution-plan 段落格式增 `projection:` 區塊（planned symbols/edges/modified symbols——LLM 填表）；**ep-review F3 增「projection 區塊在場性＋零邊洞報告」機械檢查**（這是閉環的另一半：不填會被抓）；觸發限縮**整合器型/跨模組 EP**
- 防洗衣陷阱：`[projected]` 標籤一級（overlay=producer 假設非證據）；CR 全綠≠無 ripple
- **驗收（v2 修正）**：逐案檢查每個整合器型 EP 的 projection 區塊在場性＋查詢輸出引用——**不用百分比指標**（兩週整合器型 EP 可能僅 2-3 個，n太小統計無意義）；段落 0 接線（8327ae4）作為「sidecar 式 vs in-path 式」的天然對照，觀察窗從下一個 EP 起

*與 Uncle Bob 對映*：projected graph＝「把架構判斷輔助變成確定性檢查」的 CR 版——論點 1+7 交匯（機械產證據、人類判讀結論）。

**T2-2 bundle 減肥第二波**（F1；**supersede 既有 `bundle-layered-diet.md` Backlog 卡**，非平行提案——該卡帶品質護欄「每項搬移須驗證 on-demand 連結存在且可被觸發」，觸發條件從「token-billed 成主力」改為「90KiB gate 95%+ 現實壓力」）
- 下沉候選：model-routing 深層（解析表細節/遙測/已知 bug 家族→skill，rule 留兩跳解析骨架）、deep-thinking 輸出格式、llm-output-convention 細則——機制成熟（same-name 配對先例 **3 個**：acceptance-evidence / instruction-writing / lsp-navigation）
- **自檢清單退場**：ZCode bundle 內 2 條（deep-thinking、llm-output-convention）——理由用「零獨立性驗證」（可辯護），不用「零約束力」（不可觀察）
- guide↔rule 單源化：三組漂移（F2）收斂為「rule 是源、guide 引用不重述」
- 目標：回到 ≤75KB（gate 81%），買回 ~13KB headroom

**T2-3 agents/ 定義層 CR line**
- 現況：subagent 工具紀律靠主 session 每次 spawn 手工注入（遙測實證、重複 token 成本）；agents/ 零 CR 引用
- agents/shared/ 定義攜帶 CR CLI fallback 一行（**CLI 形態——MCP 未連線全名 spawn 拒絕，既有結論**）
- **與既有餵料機制的差異須說明**：code-reviewer-primed 已透過 post-build 模式 B 吃 delta_tour 餵料——T2-3 增量是「agent 自己查」（審查中主動 closure/impact_radius）而非「吃餵好的」；prompt 增重成本須量（shared 是全 subagent 定義層）

**T2-4 Read-dedup 可見性迴路**（v1 遺漏，v2 升格——最大宗可量化 token 浪費、v1 連提案都沒有）
- 206 對重讀 ≥3 次是既有 Read 紀律 rule 的衰減證據；硬 hook 攔 Read 不可行（無 PreToolUse 於 Read 面/誤傷高）
- 可行形態：**可見性迴路**——standup/daily-maintain 的既有週期任務加「重讀熱點指標」（從遙測 DB 聚合 (session,file) 重讀次數 top-N），讓浪費定期可見而非即時阻擋
- 輕量、純 ai-rules 側、一個小卡可做

### T3 spike-first 與決策項（「先跑一次帶數據來，不開卡等需求」——對齊 spike-now 裁決）

**T3-1 糾正模式挖掘迴路（spike-first）**：Agent A 的方法（關鍵詞候選→人工判讀→分類）＋aggregate_sessions.py 已存在——**先手跑一個月度報告帶數據**（每月 ~60 糾正的成本/發現量），有數據再裁決常態化與否
**T3-2 變異測試 lite（spike-first）**：試點已選得出（mosaic domain core critical path）——跑一次的成本/抓到的同義反覆測試數據，直接取代抽象「成本 vs 收益」問句；前提：T1-2 先補好自己的測試（順序已排）
**T3-3 零採用項拆開處置**（v1 歸類錯誤，v2 修正）：
- **smell-detector（B 軸 viewport）個案**：B 軸整體有消費（debrief ~10、illustrate ~11），唯它掛零——個案處置（合併進 debrief？降維護？）而非「B 軸戰略」
- **ep-validate（1 次）/spec（0-1 次）（A 軸 LLM 鏈命令）**：與 B 軸無關——分別是「EP 後深度驗證」「需求釐清」的低頻命令，去留看 EP 工作流是否真的需要該環節，另行裁決
**T3-4 UI/執行驗證自驗閉環（回應最响的用戶怨言）**：「你這不能用 playwright 自己驗證嗎？我這樣很累誒」——B 軸 L4-L6 缺口的直接證據。mosaic 端 ui-collab skill 已存在、ZCode browser-use plugin 在場；**缺的是流程接線**（implement/fix-test 的驗證階段何時該觸發 browser 自驗、驗證證據怎麼進收尾報告）。盤點現有 ui-collab 接線→小卡補EP 驗證策略段的 UI 觸發條件

---

## 5. 對抗驗證結果

### 5.1 宣稱覆核（結構面）
lite-verify 對 Agent B 七項結構宣稱：**7/7 成立**（87,808 bytes、95.28%、F4 活違規、F8 孤兒、F9 9/0、F10 行號、F5 掃描範圍——數字到位元級吻合）。補充事實：rules/AGENTS.md:111 是反面教材非違規（B 未誤報）；settings.json 矛盾源頭是 repo 內檔案。

### 5.2 魔鬼代言人攻擊摘要與裁決（v1→v2 修訂全記錄）

| 攻擊 | 裁決 | v2 動作 |
|---|---|---|
| 🔴 T1-5「接線至今未做」事實錯誤（ad66919 已落地＋四次強化） | **採納**（本 session 親驗 git show＋三檔直讀確認） | T1-5 整項刪除；§2.1/§3.1 歸因改寫為「sidecar 不在生產路徑」；T2-1 增「為何不步 snapshot 後塵」論證（§3.1） |
| 🔴 T1-4 內部矛盾（heredoc 加規則違反不做清單 #1）＋allowlist 證據-載體錯配 | **採納** | T1-4 重組：heredoc 改機械化優先；allowlist 修「Claude 端矛盾本身」並明言與 ZCode 衰減脫鉤 |
| 🟡 T2-2 漏既有卡＋數字錯（清單 5→2 in bundle、先例 4→3、「零約束力」過度引申、「~2.7 天」假精度） | **採納** | 全部修正＋明示 supersede bundle-layered-diet |
| 🟡 T3-1/T3-2 把可 spike 的問題外包給用戶直覺 | **採納**（違反 spike-now 裁決精神） | 改 spike-first 形態 |
| 🟡 T3-3 歸類錯（B 軸/A 軸混包）＋漏 debrief/illustrate 消費數據 | **採納** | 拆開處置 |
| 🟡 T2-1 驗收指標脆弱（80% of n=3 無意義、對照組觀察窗為零） | **採納** | 改逐案檢查＋對照組說明修正 |
| 🟡 「42 次提及」不可重現；head:wc 26:1 對 scoping 敏感 | **採納** | 改量級表述（§2.1/§2.2） |
| 🟢 T1-1 rg 命中 4 處非 2 處；sync-sources 關係未說明 | **採納** | 實作陷阱寫入 T1-1 |
| 🟢 T1-2 驗收 trivially green＋/commit 是 prompt 級 | **採納** | tests/ 落點＋pre-commit hook |
| 🟢 T1-3 漏 compact-prep:31 連鎖清理 | **採納** | 寫入 T1-3 |
| 遺漏：Read-dedup 無提案；用戶最响怨言被點名後丟下；ZCode 權限面未審 | **採納** | 升格為 T2-4、T3-4、T1-4 第三點 |

**元教訓（建議記入 flow-feedback）**：v1 的最大錯誤（T1-5）來自**未經親驗就採信 Agent C 的 relay 宣稱**——而 lite-verify 7/7 的覆核範圍只涵蓋 Agent B 結構面，v1 §2 開頭「全部經獨立覆核」是**覆核範圍宣稱與覆核範圍事實的 drift**（又是 relay-claims 教訓家族的新實例：調查 agent 的宣稱也是 relay）。魔鬼代言人（獨立第三方）＋本 session 對翻案的親驗，才把這條抓出來——對抗驗證鏈真的有用，但也證明「宣稱覆核狀態」本身要精確到claim 級。

## 6. 不做清單（anti-proposals）

1. **不加 always-on 規則來「修」行為**——§2.2 證明規則在檔行為照樣衰減；行為問題的解法是機械化或流程產物化（v1 的 T1-4 曾違反此條，v2 已改）
2. **不建 CI**——solo+AI 是設計前提，「無 CI」不是缺陷
3. **不強迫每個 EP 用 CR**——整合器型/跨模組觸發；小 EP 走 LSP+rg 三件套是**已驗證的健康現況**，不是要修的問題
4. **不做 hook 自動 compact**——已實測死路（SessionStart compact source 不派發）；且 compact 是使用者判斷
5. **不動 mosaic repo**——本報告全 ai-rules 側；CR 工具側交付 handoff（hub-relay 模式：ai-rules 交代任務、CR session 執行）

## 7. 落地順序建議

```
T1-1..T1-5（純 ai-rules 機械化＋小修，1-2 個 session 可清完）
   ↓
T2-2（bundle 減肥，supersede 既有卡）      ← 在 T2-1 前做：給段落格式變更騰預算
   ↓
T2-1（projected graph：CR repo 工具 EP 先落地〔已寫〕→ ai-rules 接線小 EP）  ← 旗艦，走正規 EP
   ↓
T2-3（agents/ CR line）＋ T2-4（Read-dedup 指標）
   ↓
T3-1/T3-2 spike（跑一次帶數據）＋ T3-3/T3-4 裁決項
```

## 8. 方法論限制

- 遙測只見 ZCode 側（Claude Code 側活動未計）；F10 修的是 Claude 側設定、量到的衰減在 ZCode 側——兩側證據-載體錯配已明示
- `rg|head` 統計 vs 展示用途無法機械區分——「壓倒性主導」是量級結論，精確比值口徑敏感
- 糾正判讀為人工（43 候選→~30 真），關鍵詞法假陰性未估；糾正數是「被抓到」的下界
- EP 語料是 working tree 最終態（曾有後刪可能，機率低）；「一般 EP」切法（29）不可獨立重現、量級成立
- 自檢清單對注意力的 framing 效果不可觀察——刪除理由僅建立在 token 帳＋零獨立性驗證上
- 結構審查是 08-29 快照；Agent spawn 遙測缺 model 欄位（model-routing pins 的 wire 情況無法驗證）
- Uncle Bob 對映表是詮釋性框架；「工具在場、紀律在檔、接線不在生產路徑」是本報告的組織性隱喻，非機械結論

## 9. Pending（需用戶授權/互動 gate）

- **本報告 + 任何後續修改的 commit**：互動 gate，等用戶確認
- **zai-org/feedback issue（Agent spawn 遙測缺 model 欄位）**：outward action——草稿可先備，送出需 AUTH
- T2-1 的 ai-rules 接線小 EP、T2-2 的 supersede 卡：等用戶對本報告裁決後開卡

### 用戶裁決（2026-08-30，T1 批次）

- **T1-1 / T1-2 / T1-5：✅ 照做**
- **T1-3：✅ 照做，但 compact-tail-inject.py 改為「CC 端接線」不刪**（用戶 08-30 翻案，文檔驗證成立）：死路結論只適用 ZCode（08-24 L4 實測＝ZCode compact source 不派發 SessionStart，#167 家族）；CC 官方支援 `SessionStart` + `matcher: "compact"`（ref-docs/harness/claude-code/docs/en/hooks-guide.md:311-323 官方食譜即此場景；hooks.md:983 確認輸入帶 `source` 欄位）。腳本本體已照 CC 形狀寫（stdin JSON / session_id guard / `hookSpecificOutput.additionalContext` 輸出 schema 全相容），**唯一死點是 `fetch_tail()` 硬接 `~/.zcode` db.sqlite**（hooks/compact-tail-inject.py:19）——port 為讀 CC `transcript_path` JSONL。落地：settings.json 註冊＋fetch_tail 換資料源＋compact-prep SKILL:31 改「CC=hook 自動補給／ZCode=手動三動作」；T1-3 invariant 屆時自然滿足
- **T1-4：(a) settings.json 兩行刪除＋(b) heredoc hook spike 照做；(c) ZCode 側權限盤點取消**——用戶裁定 ZCode 給完全訪問、config.json 視為無效（衰減不是 ZCode 權限預批准造成）

### Side chat 結算補記（2026-08-30，sess_a919d9cc）

- **T3-3 smell-detector 定案：接線不進鏈**——post-build 階段 5 收尾報告加 `smell=<建議 zoom 的 dir|無>` triage 欄（訊號源＝code-review/judge findings 的 `[junk]` tag——code-review Finding 呈現段已加標記規則）；baseline/onboarding mode 不掛 post-build（週期需求另議）。零成本常態化 caller，受眾分離保住
- **T3-3 ep-validate/spec：留**——ep-validate 的 ad-hoc 路徑（「討論時直接叫 LLM 寫 POC」）繞過遙測，1 次是下界非零採用；雙路徑並存是現狀正解。spec optional by design
- **T3-2 handoff 已備妥**（貼到 mosaic session 執行；hub-relay：mosaic 只回報 findings＋數據）；**T3-1 spike 已排程**（10-01 上午，九月窗口，一次性手跑）

### T3-2 變異測試 spike 結案（2026-08-30，mosaic 執行回報）

**數據**：scoped 跑 mutmut 3.7.0 於兩個 critical path（cash_tracker 118 行＋risk_guard 170 行、68 tests）——**8.2s wall／103 mutants／90 killed : 13 survived（87.4% kill rate）**。POC 零足跡清除、68 tests 重跑綠、mosaic memory `project-mutation-testing-spike-t32` 固化。

**13 個 survived 全數抽讀分類**：真實測試缺口 **10**（全部同型——比較算子邊界沒鎖：`qty > 0`→`>= 0`、`price >= 0`→`>= 1` 等；兩個最高價值：**price<1〔權證/低僞股〕在會計（cash_tracker:85）＋風控（risk_guard:147）雙處無保護**——台股真實情境）、equivalent 1、極端邊界 2。hub 端已交叉驗證 file:line 錨點全命中。

**理論印證（改寫了假說形態）**：AI 同寫 test+impl 的同義反覆**不是** `assert x==x` 廢話型——happy path 數字斷言具體且鎖死核心代數（90 killed 證明）；真實形態是**測試與 impl 共享同一組典型數字**（1000 股/600 元/85 元），邊界值（0、1、恰好一半、price<1）系統性缺席——測試忠實反映 AI 的 happy-path 理解，盲區也完全一致。只有機械突變能把這種盲區變成可數 survived 名單。

**裁決建議（mosaic 端提出，hub 採納待用戶確認）**：mutation testing 值得進 audit-test，但採 **scoped 手跑抽查形態**（如此 spike）而非常態 gate——機械成本趨近零（8 秒），主成本是 survived 的 LLM 抽讀（13 個約 10 分鐘），一次性投入即抓到 10 個真缺口。待辦：audit-test skill 加此角度（ai-rules 側小改）；mosaic 端 10 個測試缺口補強（mosaic 側，handoff 待出）。

### T1 落地記錄（2026-08-30，同 session 完成）

- **T1-1 ✅**：`deploy_agents.py` 新增 `check_neutral_purity()`（五檢查程式化，掃 neutral rules）＋`scan_sources(include_guide)`（broken-refs 擴掃 guide）。gate 上線首跑抓到 **3** 違規（預期 2＋黑天鵝 1：`_ai-behavior-constraints.md` 的 `` `/sync-sources` `` 裸 slash）→ 三處修正（context-management:24/36 括號注化、_ai-behavior-constraints 去斜線）＋guide:131 死指標改寫 → dry-run 歸零 → 三端部署成功。設計要點：purity 不掃 guide（guide 合法提及跨 harness 裸 slash `/handoff`——範圍忠於原清單）；rules/AGENTS.md（meta scope）天然不在 neutral 集合，自引用零誤報
- **T1-2 ✅**：`tests/` 三檔 34 測試（deploy gate／兩個攔截 hook／invariant checker）＋pyproject pytest dep＋`.githooks/pre-commit`＋`git config core.hooksPath .githooks`（確定性 git hook，非 prompt 級）
- **T1-3 ✅**：`check_single_source.py` 新增第 7 個 invariant `hook_registration`（hooks/*.py 每檔至少一註冊處，否則 critical）＋**compact-tail-inject.py 復活**：port `fetch_tail` 為 CC transcript JSONL、settings.json 註冊 `SessionStart matcher=compact`、煙霧測試通過（tail＋STATE 注入正確、summary 行跳過、非 compact no-op）、compact-prep SKILL 更新（CC=hook 承接／ZCode=手動三動作）
- **T1-4 ✅**：settings.json 刪 `Bash(python3:*)`/`Bash(python:*)`（grep/find 純讀取段不動）＋新 hook `block-python-file-write.py`（heredoc 寫檔攔截，窄 pattern：write_text/write_bytes/open-'w'系）雙端註冊＋煙霧測試通過（違規 exit 2＋指引、純讀放行、JSON 有效）
- **T1-5 ✅**：guide 銜接機制四步鏈（插入 post-build 收尾鏈步驟，已進部署 bundle）
- 驗證：39/39 tests（含 judge F1 補的 compact-tail-inject 測試）、7/7 invariants（含新 hook_registration＋claude_only 豁免）、ruff clean、三端 bundle fresh、CJK 抽驗乾淨。**未 commit（互動 gate）**
- post-build 審查鏈（08-30）：dual-context（fresh 8＋primed 4 findings，primed 意圖對齊 12/12）→ judge 裁決（採納 7/不採納 2/已驗 1）→ 修正落地 → followup 全綠。**heredoc hook 監測點（F9）**：首週觀察誤傷率；已知限制=open() 巢狀括號 path 不攔（regex 實測），加寬前先收誤傷數據
