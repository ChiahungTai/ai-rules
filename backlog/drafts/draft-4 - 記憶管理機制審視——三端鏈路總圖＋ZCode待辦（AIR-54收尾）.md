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

## 三端鏈路總圖（AIR-54 S1-S5 落地後，2026-09-09）

主體＝repo 內 `.agents/memory/`（gitignored＋池自帶 git；bundle 夜波外送 `~/.agents/memory-bundles/`）。

| 端 | 讀鏈 | 寫鏈 | 證據 |
|---|---|---|---|
| muse | project scope 原生讀（開場注入 MEMORY.md＋清單；`read_memory` 按需） | 經 `.muse/hooks.json` PreToolUse 閘代存 `.agents/memory-inbox/`（deny），consolidation 入池 | VP1/VP2 全綠＋recall sentinel 兩腿過（一等公民成立） |
| CC | 舊徑 `~/.claude/projects/<encoded>/memory` 今為目錄 symlink→主體，透明穿透 | 直寫主體（write-sensor 觀測；MEMORY/_index 寫由閘擋） | headless probe 開場載入全綠；write-through 綠 |
| ZCode | 既有 symlink→CC 舊徑→主體（雙跳，同 inode） | 直寫主體 | 三路徑同 inode 實測；真開場＝下 session 自然確認 |
| codex（第四端） | 檔案級 Read 穿透；目錄級 rg/glob 走主體路徑（CC 舊徑需 `-L`） | 回報制，不直寫 | SM-13；AGENTS.md 觀察池路由已註明 |

寫入收斂站＝consolidation（memory-audit「Inbox 消費」節）：夜波 23:40 或手動；WAL light（new→processing→done/rejected＋receipt）；path contract＋CAS＋六問；逾期 >48h 由 daily-maintain watchdog 異故障域報警。

## ZCode 待辦清點（本弧不做，僅盤點）

1. **spine registry routing 待辦腿**（AIR-45 S6 遺留）：`~/.agents/memory-spine/index.md` ZCode 腿仍待認養路由——muse 腿已註記主體直連，本項維持後議。
2. **ZCode memory config 面**：per-project 隔離 v3.6.4+ 預設關，本弧零改；若日後開啟，雙跳鏈需重驗（載入時機＝session 啟動一次性，建/改 symlink 的 session 讀不到）。
3. **per-session 行為**：CC/ZCode 載入器皆啟動一次性—— symlink 變更需新 session 才生效（既有平台事實，非本弧引入）。

## 後續提案（未承諾，按序）

- P1（今晚自然發生）：首個完整 23:40 夜波驗證（inbox 掃描段＋bundle 尾巴在 AGENT_MEM 上運作）→ 綠後刪 `memory.bak`（EP 時點微調：刪除 gate＝矩陣＋首波）。
- P2（待 user 拍板）：inbox→索引 pending 區折衷（只進 `_inventory.md` rg 可達層、不進開場注入）——09-09 討論結論：常態連 MEMORY.md 否決（繞品質閘＋搶 6K context 預算）；同 session 重讀走 deny reason 路徑已夠。
- P3（結案第三動）：divergence 條目終態重寫（收斂宣告尾段；現 desc 有「終態見本條尾段」懸空指針，結案蒸餾時補）。
- P4（另 handoff）：S6 mosaic 移植（owning 線實體＋inbox 比照＋memory-policy 改寫）歸 mosaic session。
- P5（T3-4 殘餘，待 user 拍板）：watchdog 執行者——daily-maintain Phase 0 已有雙檢查（inbox age＋porcelain-vs-receipt），但執行者歸屬未驗證（skill 記每日 23:20 vs registry 無此條，AIR-52 解綁處理中）；選項 (a) 確認／排程執行者 (b) 併入週日 23:00 治理看照（advisory 只讀，體質相合；需 ZCode 側改 prompt，不在本 session 越權範圍）。結案口徑（終審裁定）：git anomaly detector exists; automatic independent execution pending P5——不得宣稱自動雙故障偵測；P5 不必塞回 AIR-54 即可結案。

## 終審第三輪（T3，跨 provider，Conditional Pass → 修畢待關）

7 findings 裁決：T3-1 ✅（hook 未驗證 path 先 dereference→lexical gate＋4 測試）；T3-2 ✅（contract 文字硬化：per-component lstat）；T3-3 ✅（delimiter-aware＋`../memory-inbox/x.md` 回歸）；T3-4 ✅確認且深一層（dirty-sensor live 未驗＋watchdog 無執行者→Phase 0 第二檢查＋P5）；T3-5 ✅（sentinel 方法論收緊重做，見下）；T3-6 ✅（meta 條件釘測試＋文字澄清）；T3-7 ⚠️部分（大小寫無關化；池全 ASCII basename，Unicode 暫 N/A）。**複審**：T3-2/3/5/6/7 關；T3-1 仍開放（`alias/secret.md` 中間段穿透反例成立）→已補 intermediate 逐段 lstat＋2 測試（9 綠；舊邏輯覆現確認）；T3-4 維持開放＝已知殘餘 P5（文檔不得宣稱自動雙故障偵測，寫「detector exists; execution pending P5」）。

sentinel 重做（硬化 oracle）：新 target `reference_zcode-session-store`（開場快照 4720B 機械證實缺席＋全程未預讀）；body-only canary（2.3GB／483 sessions／tool_usage 無 input——快照＋inventory 雙缺席）答對；session.jsonl `assistant_tool_calls_committed` 有該 path 讀事件（oracle 非自述）。殘餘：fresh-session 行為對照未做（快照鑑識已做等價資訊論證，價值低）。

## 方法論附記

- recall sentinel 本弧首次以「同 runtime 在 session 內自測」執行（sentinel 缺席開場注入已用 session.jsonl 機械證實＋全程未預讀）：自然腿（_inventory 定位→讀 body）＋顯式腿（`read_memory(path)` 原生讀逐字一致）兩過。限制：參數級無工具召回按設計失敗（B 形態＝檢索非背誦）；外部 runtime 的結案時點 gate 需工單明示（AIR-50 教訓）。
