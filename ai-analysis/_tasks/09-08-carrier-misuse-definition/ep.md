# AIR-48 EP：載體濫用鑑識 × 統一定義表 × B 上線切換 × dogfood

> **ep_type**: implementation（P1-P5；P4 為協議段——首輪跑完轉常態觀測，非一次性 build）
> 卡：AIR-48（desc＝合約，已含 baseline d00bfe2／已決策勿重辯 8 條／驗收 6 項）
> baseline: 8296b79
> 北極星：稀缺性分層（L2/HBM/DRAM/HDD 類比＋四判準——AIR-45 EP「User 核心定調」節，勿重辯）

## 實作總覽

用對話紀錄實證三載體（memory／bundle-AGENTS.md／skills）的誤置模式 → 合一出「rules/skills/memory 各寫啥」統一定義表 v1 → B 上線切換＝定義表首次執法（live MEMORY.md→常駐定額＋inventory）→ dogfood 首輪行為對照。寫入路徑（濫用防制）與讀取路徑（載入面）一體處理。

## UC 盤點

### Backlog 關聯
- 本弧追蹤卡＝AIR-48（To Do）；AIR-45 已 Done（殘餘移交本卡：B 切換＋catalog 探針）

### 受影響命令/rules/skills 清單（docs 面主體）
- `skills/memory-audit/SKILL.md`（寫入端紀律＋引擎——定義表落點候選）
- `skills/instruction-writing/SKILL.md`（載體決策樹——與定義表合一）
- `skills/memory-audit/scripts/generate_index.py`（B 切換改造標的——資產源；池內 `_generate_index.py` 為部署副本，cp+mv 原子刷新）
- `hooks/block-memory-index-write.py`（**兩個面分流**：寫入摩擦設計＝P2 僅設計不實裝；`_inventory.md` 手寫防護＝P3 實作項）
- `rules/context-management.md`（pointer 同步——定義表落點變更時）
- deploy 三端（`scripts/deploy_agents.py`）——本弧原則上不動 bundle 內容

### 同主題 memory 條目（結案蒸餾範圍）
- `memory-redesign-read-path-0908`（AIR-45 終態，rank cold——本弧結案時補 AIR-48 終態行）
- `memory-cc-alignment-diagnosis-0905`（治理線 keeper——定義表吸收其「載體切分評估」段後壓指針）
- `feedback_inflow-needs-outflow`（寫入摩擦設計的互文）
- `project_session-id-continuation-absorption-0908`（in-flight、歸屬他弧——不動）

### 既有 UC 狀態
| 能力 | 狀態 | 來源 | 影響 |
|------|------|------|------|
| memory 索引投影＋gate | ✅ | generate_index.py | 更新（B 形態輸出） |
| 寫入端紀律（六問/文法五條） | ✅ | memory-audit skill | 更新（定義表合一） |
| 兩級稽核＋生命週期引擎 | ✅ | memory-audit skill | 無影響 |

### 新增 UC
| 能力 | 狀態 | 實作路徑 |
|------|------|---------|
| 載體誤置鑑識（session 紀錄→taxonomy） | 📋 | 任務家 P1 產物＋流程入 memory-audit 引擎段 |
| 統一定義表（載體×常駐×寫入預設） | 📋 | memory-audit skill 新節（單一源） |
| B 形態 live 投影（常駐定額＋inventory） | 📋 | generate_index.py 改造 |

## Scenario Matrix

| # | 場景 | 觸發 | 預期行為 | Checkpoint | 對應能力 |
|---|------|------|---------|------------|---------|
| SM-1 | 冷條目任務到來 | 任務涉及非常駐池知識 | 經 routing 行/inventory rg 找到並讀 body | 找不到→升常駐候選（dogfood 記錄） | B 形態投影 |
| SM-2 | 濫用寫入企圖 | session 欲 dump 進度/草稿/任務狀態進池 | 預設路徑改道後：scratch/卡 比 memory 更近；寫入留歸因痕跡 | 改道前：P1 記錄現況誤置 | 統一定義表 |
| SM-3 | 常駐集合失準 | 任務高頻需要非常駐條目 | dogfood 偵測→rank/常駐集合調整（證據驅動） | 誤降必要條目→凍結集合重判 | dogfood 迴圈 |
| SM-4 | pool 增長 | 新條目入池 | 開場載入面不變（常駐定額）；inventory 增長不進開場 | inventory 尺寸無上界→rg 可達即成立 | B 形態投影 |
| SM-5 | 歸因查賴 | 事後追查條目由誰寫 | writer 可見性（修法建議產出；實作另裁） | 現況破口：originSessionId 只記創建者 | 誤置鑑識 |
| SM-6 | 無關任務零誤觸 | 常駐面縮小後 cross-task 噪音 | 誤觸發不升反降（載入面更小） | — | B 形態投影 |
| SM-7 | codex catalog 真縮短行為 | codex skills-budget 載入縮短 desc | 縮短後檢索仍可達 | 模擬 37% 已 12/12；真通道單探針補 | （AIR-45 移交項） |

## 段落劃分原則

P1→P2→P3 強依賴（P2 吃 P1 證據；P3 常駐集合依 P1 修訂）；P4 依 P3；P5（catalog 探針＋歸因修法建議）可與 P2/P3 平行。P1 證據是過去式＋會揮發——最優先。

**產物路徑釘死**：P1→`p1-taxonomy.md`（任務家）；P2→定義表＝memory-audit skill 新節（本體）＋任務家 `p2-definition-table.md`（審計副本）；P4→`p4-dogfood-round1.md`；中間產物 `.agent-tmp/`。

## EP Review Findings（已全採納回寫）

| ID | 嚴重度 | 摘要 | 處置 |
|----|--------|------|------|
| F1 | 🔴 | RESIDENT_SET 主選項 rank==hot 實測空集合＋違北極星（rank 不決定常駐資格） | ✅ 顯式清單檔唯一機制＋釘死 necessity-set.md 路徑 |
| F2 | 🟡 | 他池刷新語義未裁定（mosaic 誤切空常駐 vs stale 停滯） | ✅ 形式選擇＝清單檔在場與否（per-pool opt-in）；mosaic 切 B 列 P4 前置；commit 與刷新同波 |
| F3 | 🟡 | B 後治理信號真空（流入率/夜收斂觸發掛 gate FAIL 會死） | ✅ 信號改掛 inventory 指標＋層 1 pattern/gate prose 同步清單 |
| F4 | 🟢 | hook 兩種待遇混淆（摩擦=設計 vs inventory 防護=實作） | ✅ UC 行拆分＋stale 窗口註記 |
| F5 | 🟢 | gate 新閾值無具體值＋三處單一源未列 | ✅ 6,000 chars 級＋GATE_CHARS/SKILL prose/test 錨清單 |
| F6 | 🟢 | 產物路徑未釘死 | ✅ 段落劃分原則節補產物路徑表 |

### codex 終審輪（NEEDS-REVISE R1-R5 → 全採納回寫）

| ID | 嚴重度 | 摘要 | 處置 |
|----|--------|------|------|
| R1 | 🟡 | 回滾會被 regen 蓋回 B（清單檔未移除） | ✅ 回滾兩層順序敏感：先移 _resident-set.md 再 regen；驗收＝Stop 後仍 A |
| R2 | 🟡 | 常駐清單失效（缺檔/壞 frontmatter/rename）無防護 | ✅ 唯一解析＋fail-loud＋保留上份常駐面；三測試案例 |
| R3 | 🟡 | 首切 B 雙檔發布無順序（inventory 失敗＝入口全滅） | ✅ 先 inventory 後常駐面；失敗不切換＋非零 exit＋marker |
| R4 | 🟡 | 治理信號無消費閉環（夜收斂可能仍不動） | ✅ A 取 index/B 取 inventory 口徑＋基線重建＋cron 鏈釘死＋觸發實測驗收 |
| R5 | 🟡 | dogfood「無 fail→轉常態」把未觀測當通過 | ✅ 分母（確有需求）＋軌跡核對＋未驗證標記＋A 期案例對照；停止條件事先定 |
| C1 | 澄清 | P1 應複用 memory_telemetry.py 既有解析 | ✅ 入 P1 要點②（禁另造解析器） |
| C2 | 澄清 | mosaic 切 B 是 mosaic 自身前置，不綁本弧 P4 | ✅ P3④ 已寫「列 P4 前置/mosaic 側 session」——語義＝mosaic 自己的 dogfood 前置，非 ai-rules P4 依賴 |

---

## P1：鑑識腿（flash agent 執行）

**Context**：近 3-7 天對話紀錄橫掃，產 memory/bundle/skills 三面誤置 taxonomy＋頻率＋session 歸因。specimen 已鑑識（sess_5220505c：兩池條目≈30 Write 草稿式迭代；歸因破口：originSessionId 只記創建者；rollout session 結束即清）。
**要點**：①資料源優先序＝db.sqlite `part` 表（持久）→ 池 mtime＋frontmatter 歸因 → 存活 rollout（發現當下抽取，禁依賴）；②**歸因解析複用 `memory_telemetry.py` 既有管線**（tool event/session 關聯/時間窗解析已在場）——禁另造解析器；③分類判準用六問 Q1（任務終態 vs 活知識）＋desc 三不——違反即誤置；④bundle/skills 面：git log 近 7 天 rules/skills/AGENTS.md 變更 vs 對應卡/EP 宣稱（無宣稱承諾的即疑似 scope creep）；⑤產出含 SM-5 破口登記與「哪些誤置可由預設路徑改道解決」評估。
**驗證**： taxonomy 每項附機械證據（session id＋條目/檔案＋呼叫計數）；flash 產出由主 session 抽驗 ≥3 條 load-bearing 宣稱（lite 執行＝規格陳述非驗收證據——分工律）。
**紅線**：read-only（池/db 皆只讀）；不觸碰 in-flight 條目；中間產物 `.agent-tmp/`。

## P2：統一定義表 v1（docs mode）

**Context**：三處分散判準合一——memory-audit 六問載體判定 × instruction-writing 載體決策樹 × 收斂落點慣例（跨 repo 方法論→skills/rules；模組知識→模組 AGENTS.md；user 綁定→memory）。產出單一交叉表：**載體職責 × 常駐-按需 × 寫入預設**（含「該寫哪」決策一行流）。
**要點**：①落點＝memory-audit skill 新節（寫入端紀律旁）——instruction-writing 決策樹改指針，單一源；②寫入摩擦設計：讀 P1 發現設計「讓正確載體比 memory 更近」的改道方案（hook 擴充/提示層/工具層——僅設計與建議，實作另裁）；③定義表以稀缺性為軸：每行註明佔用哪層資源（開場常駐/任務中載入/按需檢索）。
**驗證**：docs mode（rg 殘留＋跨檔一致性＋consistency）；Decoder test——拿 P1 taxonomy 的每個誤置案例反查定義表，答得出「該寫哪、為什麼」。

## P3：B 上線切換（實作）

**Context**：live MEMORY.md 從全量索引改為**常駐定額＋inventory**——AIR-45 (a) 裁定的投產。常駐集合＝S2 定稿 12 條（**顯式清單檔為唯一機制**——凍結版 `ai-analysis/_tasks/09-08-context-lifecycle-unification/s1-probes/necessity-set.md`；rank 語義不變＝僅集合內排序，**不決定常駐資格**——北極星既定），依 P1 讀取證據修訂（升級/降級交 user 確認後凍結）。
**要點**：①generate_index.py 最小改造：**池內存在 `_resident-set.md`（清單檔）才產 B 形態**——MEMORY.md＝常駐段（清單條目行）＋routing 行；`_inventory.md`＝全量投影（不進開場，底線前綴不進索引）；**無清單檔的池維持現行 A 形態**（per-pool opt-in——他池刷新安全，不會誤切）；②gate 語義：B 形態下守常駐段尺寸（新閾值 **6,000 chars 級**——B 實測 3,649B 留成長餘裕；A 形態維持 22,500）——**三處單一源同步**：generator `GATE_CHARS` 分形態、memory-audit SKILL 層 1 prose、`tests/test_memory_lifecycle.py` cross-layer 錨；③切換前快照舊 MEMORY.md 進任務家 version/（回滾面）；④部署副本刷新＝全池（含 mosaic）——**形式選擇由清單檔在場與否決定**，mosaic 未定義常駐集合前自動維持 A 形態（mosaic 切 B＝先定其常駐集合，列 P4 前置/mosaic 側 session；資產源 commit 與池刷新同波執行縮 stale 窗口）；⑤`_inventory.md` 手寫防護＝**P3 實作項**（hook `is_index_violation` 擴 `_inventory.md` 檔名比對）——有別於「寫入摩擦設計」（P2，僅設計不實裝）。
**稽核/收斂消費端同步（B 後治理信號不得真空；消費閉環可驗收）**：lite 流入率與夜間收斂波次②觸發（原掛 MEMORY.md gate FAIL）改掛 **inventory 指標**且語義隨形式——**A 形態取 MEMORY.md chars、B 形態取 inventory chars**（首次切換時重建可比較基線，禁不同口徑相減）；夜 cron 觸發入口釘死（generator 輸出行補 inventory stats → lite 對照欄 → 夜 cron 增量閾值三段鏈）＋**驗收＝「B 常駐面不變、inventory 增長時 lite/夜收斂實際產出候選」實測一次**；層 1 one-line-per-entry 檢查 pattern 擴容 routing 行形態。B 形態下 MEMORY.md ≈常數**不得**作為流入訊號。
**常駐清單失效處理（fail-loud）**：清單內每個 resident id 必須**唯一解析到合法條目**——列名不存在／frontmatter 損壞→**明確報錯＋保留上一份常駐面**（不得發布缺必要成員的子集）；夜間 merge/rename 觸及選中條目→同步改清單＋走集合確認流程（user 凍結）。測試案例：缺檔／壞 frontmatter／rename 三形態。
**雙檔發布順序（首次切 B）**：**先原子發布完整 `_inventory.md`，成功後才發布 B 形態 MEMORY.md**——inventory 寫入失敗＝不切換常駐面（保留 A）＋非零 exit＋marker；補寫入失敗與重跑恢復兩驗收。不新增交易框架（沿用現行單檔原子替換機制分兩步）。
**Pseudo Code（generate_index 改造要點）**：`_resident_set(pool_dir)` 存在→`render_b_form(entries, resident_list)`＋`render_inventory(entries)`；缺→現行 `render_a_form`；gate 依形態取閾值。
**驗證**：單元（resident 投影/gate 分形態/inventory 完整性——全條目仍可 rg 到/A 形態回歸不變）；切換後煙霧：新 session 開場面實測＝常駐行＋routing 行在場；SM-4（新增條目→開場面不變、inventory 增長）；**mosaic 池刷新後煙霧＝A 形態不變**。
**回滾（兩層，順序敏感）**：池回滾＝**先移走 `_resident-set.md`**（形式選擇翻回 A）→ 再 regen（否則 regen 立即以 B 蓋掉還原的 A）；資產源回滾＝git revert generator＋**同步刷新部署副本**（Stop hook 對不符副本會跳過 regen 留 stale marker）。回滾驗收＝下一次 Stop hook regen 後仍為 A 形態。

## P4：dogfood 首輪（協議段）

**Context**：切換後真實任務觀察——定義表與常駐集合的第一次實證回餵。
**要點**：①**首輪範圍與停止條件事先定**（小範圍：N=接下來 3-5 個自然 session 或 48h 先到者；不擴成 benchmark）；②逐案四欄記錄：**確有知識需求？（分母——無需求 session 不計入通過）／有可核對軌跡？（telemetry reads 或 rg 痕跡——mtime 不記讀取、自報非獨立證據）／找得到？／用得出？**；③無相關任務或觀測不足→標**未驗證**（非通過）——「無 fail」不等於成功（codex/muse/bash-rg 未 instrument 是已知觀測限制，接入判準）；④前後對照：取 3-5 個既有 A 形態時期的任務案例做基準對照；⑤回餵：rank/常駐集合調整候選＋定義表 v1.1；「找不到」事件＝最高價值信號逐案歸因。
**驗證**：首輪報告（找得到率＝命中/確有需求、歸因、未驗證清單）；通過判定＝**有確有需求案例且全部可核對軌跡下找得到**——非僅無失敗。

## P5：雜項（可平行）

①codex catalog 縮短真通道探針（SM-7——材料安裝進 codex skills 目錄形態後跑 retrieval；模擬 12/12 已有）；②writer 歸因可見性修法**建議**（設計產物：條目 body 加 writer log 行 vs telemetry 擴欄 vs generator 註記——實作另裁）。

## 整合策略

- staging：P1→P2→P3→P4 強依賴；P5 平行。P3 完成前池形態凍結（不再手動收斂——避免兩種改造交錯）。
- baseline: 8296b79；跨 session 接續靠本檔進度結算（每段落完成即 append）。

## 收尾步驟

1. 卡 AIR-48 結案兩步＋弧結案蒸餾（範圍＝UC 盤點登記條目；AIR-45 終態條目補 AIR-48 行）
2. memory-audit/instruction-writing/rules 同步（定義表單一源+指針）＋consistency
3. 殼（index.html）badge 隨段落推進掛鉤
