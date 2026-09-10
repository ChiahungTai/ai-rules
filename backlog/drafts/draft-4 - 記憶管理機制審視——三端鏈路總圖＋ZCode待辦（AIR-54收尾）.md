---
id: DRAFT-4
title: 記憶管理機制審視——三端鏈路總圖＋ZCode 待辦（AIR-54 收尾 6）
status: Draft
assignee: []
created_date: '2026-09-09 15:30'
labels:
  - memory
  - governance
  - cross-harness
dependencies: []
---

# 記憶管理機制審視（AIR-54 收尾步驟 6——審視與提案，不擴實作 scope）

## 三端鏈路總圖（S6 後修訂 2026-09-10——AIR-54 全弧含 mosaic 移植落地後）

主體＝repo 內 `.agents/memory/`（gitignored＋池自帶 git；bundle 夜波外送 `~/.agents/memory-bundles/`）。**同構複製（S6，09-10）**：mosaic_alpha 同形主體（owning＝main WT 實體、`.git/info/exclude` 排除版控；既有池經 MOS-88 遷 B 形態治理池）＋CC 三 project dir symlink＋ZCode 雙跳＋inbox hooks——細節單一源＝mosaic AGENTS.md「Muse memory」節。

| 端 | 讀鏈 | 寫鏈 | 證據 |
|---|---|---|---|
| muse | 讀取分級（S6 F2 實測）：main WT＝project scope 原生（開場注入＝索引 120 行上限＋單條 8KB inline 上限〔超限修剪僅列名〕；`read_memory` 按需）；次 WT 經目錄 symlink 的注入/read_memory 皆拒→降級 read_file 絕對路徑 | 經 `.muse/hooks.json` PreToolUse 閘代存 `.agents/memory-inbox/`（deny——1.1.1 相容），consolidation 入池 | VP1/VP2 全綠＋recall sentinel 兩腿過（一等公民成立）；mosaic main/次 WT 雙探針 |
| CC | 舊徑 `~/.claude/projects/<encoded>/memory` 今為目錄 symlink→主體，透明穿透 | 直寫主體（write-sensor 觀測；MEMORY/_index 寫由閘擋） | headless probe 開場載入全綠；write-through 綠 |
| ZCode | 既有 symlink→CC 舊徑→主體（雙跳，同 inode） | 直寫主體 | 三路徑同 inode 實測；真開場＝下 session 自然確認 |
| codex（第四端） | 檔案級 Read 穿透；目錄級 rg/glob 走主體路徑（CC 舊徑需 `-L`） | 回報制，不直寫 | SM-13；AGENTS.md 觀察池路由已註明 |

寫入收斂站＝consolidation（memory-audit「Inbox 消費」節）：夜波 23:40 或手動；WAL light（new→processing→done/rejected＋receipt）；path contract＋CAS＋六問；逾期 >48h 的 watchdog 檢查已寫入 daily-maintain Phase 0（異故障域設計）——排程承載已定（ai-rules 週日看照段 4，P5 定案 09-10）；runtime 未驗項＝09-13 首跑觀測，不宣稱每日/即時偵測。

## ZCode 待辦清點（本弧不做，僅盤點）

1. **spine registry routing 待辦腿**（AIR-45 S6 遺留）：`~/.agents/memory-spine/index.md` ZCode 腿仍待認養路由——muse 腿已註記主體直連，本項維持後議。
2. **ZCode memory config 面**：per-project 隔離 v3.6.4+ 預設關，本弧零改；若日後開啟，雙跳鏈需重驗（載入時機＝session 啟動一次性，建/改 symlink 的 session 讀不到）。
3. **per-session 行為**：CC/ZCode 載入器皆啟動一次性—— symlink 變更需新 session 才生效（既有平台事實，非本弧引入）。
4. **條目 8KB 消費面張力（S6 後觀察，未承諾）**：池膨脹預算 12K chars vs muse 直達注入單條 8KB 上限（**單位語義 bytes vs chars 未實測釘住**——若為 bytes，CJK 條目受影響區間更寬，判讀前先以修剪樣本實測）——8K-12K 區間條目在 muse 開場直達面僅剩列名（`_inventory` 工具鏈兩跳讀不受限）；是否收緊寫入端預算或接受分級，留 memory 治理線（AIR-69 雙池 full audit）判讀。muse user bundle 36KiB 自限已由 AIR-66 落地（`MUSE_USER_BUDGET` 部署硬 gate——部署面不再掛待辦）。

## 後續提案（未承諾，按序）

- P1 ✅（已完成）：首個完整 23:40 夜波六判據全綠（09-09 首跑）→ 09-10 晨 CC 手動執行驗證、`memory.bak` 刪除閉環＋08:30 一次性驗證 cron 收除。
- P2（待 user 拍板）：inbox→索引 pending 區折衷（只進 `_inventory.md` rg 可達層、不進開場注入）——09-09 討論結論：常態連 MEMORY.md 否決（繞品質閘＋搶 6K context 預算）；同 session 重讀走 deny reason 路徑已夠。
- P3 ✅（已完成 09-10，本弧蒸餾）：divergence 條目終態重寫落地，desc「終態見本條尾段」懸空指針清除。
- P4 ✅（已完成 09-10）：S6 mosaic 移植由 mosaic session 落地（mos-88 池 B 形態遷移結案；F2 次 WT 降級 read_file 路線定案並寫入 mosaic AGENTS.md「Muse memory」節）。
- P5 ✅（已關閉 09-10，user 拍板先(a)後(b)）：(a) lite-verify 觀測 ❌——mosaic 23:20 載體六晚 report（含 nightly-watch 前身檔）零 Phase 0 輸出＝**無 Phase 0 執行正證據**（健康靜默相容；A1 僅載 Phase 1-3、23:20 prompt 段規格跨 workspace 未驗——codex 二輪審查降格原「從未接線」宣稱）；退 (b) 已執行——watchdog 雙檢查併入 ai-rules 週日 23:00 治理看照（CronUpdate 段 4：雙池 inbox age＋porcelain-vs-receipt；升級＝age 訊號連續兩排程週期命中→🔴、processing/直寫立即🔴、手動補跑不推進計數）＋daily-maintain Phase 0 口徑同步＋registry 條 2/A1 修訂（含 stale 指針）。runtime 未驗項＝09-13 首跑觀測。

## 終審第三輪（T3，跨 provider，Conditional Pass → 修畢待關）

7 findings 裁決：T3-1 ✅（hook 未驗證 path 先 dereference→lexical gate＋4 測試）；T3-2 ✅（contract 文字硬化：per-component lstat）；T3-3 ✅（delimiter-aware＋`../memory-inbox/x.md` 回歸）；T3-4 ✅確認且深一層（dirty-sensor live 未驗＋watchdog 無執行者→Phase 0 第二檢查＋P5）；T3-5 ✅（sentinel 方法論收緊重做，見下）；T3-6 ✅（meta 條件釘測試＋文字澄清）；T3-7 ⚠️部分（大小寫無關化；池全 ASCII basename，Unicode 暫 N/A）。**複審**：T3-2/3/5/6/7 關；T3-1 仍開放（`alias/secret.md` 中間段穿透反例成立）→已補 intermediate 逐段 lstat＋2 測試（9 綠；舊邏輯覆現確認）；T3-4 已關閉（P5 定案 09-10：watchdog 排程承載＝ai-rules 週日看照段 4；文檔口徑＝detector exists＋承載已接線，runtime 首跑 09-13 待觀測——不宣稱每日/即時偵測）。

sentinel 重做（硬化 oracle）：新 target `reference_zcode-session-store`（開場快照 4720B 機械證實缺席＋全程未預讀）；body-only canary（2.3GB／483 sessions／tool_usage 無 input——快照＋inventory 雙缺席）答對；session.jsonl `assistant_tool_calls_committed` 有該 path 讀事件（oracle 非自述）。殘餘：fresh-session 行為對照未做（快照鑑識已做等價資訊論證，價值低）。

## 方法論附記

- recall sentinel 本弧首次以「同 runtime 在 session 內自測」執行（sentinel 缺席開場注入已用 session.jsonl 機械證實＋全程未預讀）：自然腿（_inventory 定位→讀 body）＋顯式腿（`read_memory(path)` 原生讀逐字一致）兩過。限制：參數級無工具召回按設計失敗（B 形態＝檢索非背誦）；外部 runtime 的結案時點 gate 需工單明示（AIR-50 教訓）。
