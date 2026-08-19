---
name: mosaic-idle-tasks
description: "產出 mosaic_alpha 閒時任務（ZCode idle-time task）指令範本——四張選單（週摘要 / test 失敗歸因 / 文檔同步 / research 掃描），選一張拿到完整 Title + Instructions 內容，copy-paste 到 ZCode UI 建立。解決「idle 要手動設定、會忘記」＋「指令要自足」兩個摩擦。觸發詞：idle task、閒時任務、閒時、idle 排程、免費任務、排一個閒時"
when_to_use: "想把一次性大活（稽核 / 掃描 / 歸因分析）排進 ZCode 免費閒時通道時；或想到『該排個 idle 任務』但忘記怎麼配"
argument-hint: "[list|weekly-standup|test-findings|doc-sync|research-scan]"
allowed-tools: ["Read", "Bash"]
---

# /mosaic-idle-tasks — 閒時任務範本產生器

ZCode 閒時任務 = **免費**（不耗訂閱額度）、**一次性**（FIFO 全局隊列、不承諾開始時間）、只能 UI 手動建立。本 skill 把「想排一個閒時大活」縮成：`/mosaic-idle-tasks` → 選範本 → 拿完整填寫內容 → copy-paste 到 UI。

> **定位紀律**：閒時任務只裝「忘記也無妨」的隨想大活。例行工作（每天/每週必須發生的事）走定時任務（CronCreate，程式建立、可靠）——忘了排閒時只是少一次深掃，忘了例行是運維缺口。

## 執行流程

1. **解析參數**：無參數或 `list` → 印出範本選單（下方四張的一行摘要表）請用戶選；指定範本名 → 直接步驟 3。
2. （選單模式）等待用戶選擇。
3. **產出完整填寫內容**：照該範本「UI 填寫」段逐欄產出——Title、Instructions（原文完整，勿省略）、執行模式建議。日期類佔位符（`<YYYYMMDD>`）先以 `date` 查當天填實。
4. **引導 UI 建立**（見下方「UI 建立步驟」）＋提醒：官方建議排任務前先 git commit（對結果不滿意可乾淨回退；純唯讀稽核類可免）。

## 共通鐵律（已內嵌於每張範本的 Instructions——UI 貼的是範本原文，範本必須自足，故鐵律逐張內嵌精簡版）

- **唯讀優先**：只寫指定輸出檔（`ai-analysis/idle-findings/` 下），不改任何其他檔案
- **禁背景子智能體**（閒時通道不支援 `background: true`，會報錯）
- **遇不確定標 `open` 不猜**：無人值守，猜錯沒人攔
- **可分段續跑**：閒時長任務到時長上限會回隊列續跑——先寫階段性產出再繼續，別把全部產出押在最後一步

## 範本庫

### 1. weekly-standup — 本週 git 摘要（官方 Standup Git Summary 的 mosaic 版）

每週五排。回顧一週 commit + daily-report + kanban 進展，產出週摘要。

**UI 填寫**：

- Title：`Weekly Standup <YYYYMMDD>`
- 執行模式：Ask before changes（唯讀設計，幾乎不會卡；卡了回來點批准仍走免費通道）
- Instructions：

  > 產出本週（`git log --since="7 days ago"` 起）的週摘要報告，寫到 `ai-analysis/idle-findings/weekly-standup-<YYYYMMDD>.md`（只寫這個檔案，本任務其餘操作唯讀）。
  >
  > 素材：① `git log --oneline --since="7 days ago"` 依主題分群（feature/fix/docs/ops）② `ai-analysis/daily-report/` 近 7 天各檔的標題節掃重點 ③ `.kanban/` 各 lane 的卡片移動（新增/完成）。輸出結構：本週主題（≤3 條）／各主題下的 commit 群摘要／kanban 進展／遺留事項。
  >
  > 約束：遇不確定就標 `open` 不猜；不使用背景子智能體；不改任何檔案（輸出檔除外）；先寫大綱到輸出檔再逐段補滿（分段續跑安全）。

### 2. test-findings — test 失敗 / flaky / 耗時回歸歸因（官方 CI Failures & Flaky 的 mosaic 版）

mosaic 無 CI，但有更強的 nightly test-regression 基礎設施。本任務 LLM 深挖近 7 天 findings，產出歸因報告——token 重、免費通道價值最大的一張。

**UI 填寫**：

- Title：`Test Findings Digest <YYYYMMDD>`
- 執行模式：Ask before changes
- Instructions：

  > 分析近 7 天 nightly test-regression 的失敗 / flaky / 耗時回歸並歸因，報告寫到 `ai-analysis/idle-findings/test-findings-<YYYYMMDD>.md`（只寫這個檔案，其餘唯讀）。
  >
  > 素材：① `ls ~/.mosaic/logs/ops/test-regression-*-findings.json` 取近 7 天，逐檔讀 flaky/regression 判定 ② `sqlite3 ~/.mosaic/logs/ops/test-regression.db`（先 `.schema` 探測 schema，再聚合 per-directory 耗時趨勢，抓週比暴漲 top 5）③ 對每個 finding 用 Read 看對應測試源碼，歸因分類：真回歸／flake（時序/外部依賴）／耗時漂移。
  >
  > 輸出結構：🔥 真回歸（需處理，附測試路徑與嫌疑 commit）／🎲 flaky 清單（附模式猜測）／📈 耗時 top 5（附趨勢）／建議處置。約束：遇不確定標 `open`；禁背景子智能體；每完成一節就先寫入輸出檔（分段續跑安全）；不修改任何測試或程式碼。

### 3. doc-sync — 文檔同步檢查（官方 Documentation sync check 的 mosaic 版）

**UI 填寫**：

- Title：`Doc Sync Check <YYYYMMDD>`
- 執行模式：Ask before changes
- Instructions：

  > 檢查 instruction 文檔與 code 的同步，報告寫到 `ai-analysis/idle-findings/doc-sync-<YYYYMMDD>.md`（只寫這個檔案，其餘唯讀）。
  >
  > 若 `/doc-health` skill 可觸發則依其規範執行；無法觸發就 Read `~/.zcode/skills/doc-health/SKILL.md` 後依其語義執行。檢查範圍：各模組 `AGENTS.md` 的 Capabilities 入口路徑是否存在（fd 驗證）、`SYSTEM-MAP.md` 狀態標記、`deploy/README.md` 排程表與 `deploy/launchd/` plist 實際時間一致、`scripts/AGENTS.md` 的 CLI 對照。
  >
  > 輸出結構：不同步清單（文檔說法 vs code 事實，附 file:line 證據）／建議修正（只建議不動手）。約束：遇不確定標 `open`；禁背景子智能體；不修改任何被檢查的文檔。

### 4. research-scan — research box 分批掃描（mosaic 專屬；天生匹配分段續跑）

掃描引擎有 `--resume` checkpoint（jsonl 斷點續傳），與閒時任務「時長上限回隊列續跑」完美匹配——每排一次推進一批。

**UI 填寫**：

- Title：`Research Scan Batch <YYYYMMDD>`
- 執行模式：Ask before changes（uv run 可能觸發確認，回來批准仍免費）
- Instructions：

  > 在 `/Users/ctai/Github/mosaic_alpha` 執行 research box 掃描一批：`uv run python scripts/research/scan_research_trend_runs.py --limit 50 --resume`（輸出在 `ai-analysis/research-boxes/lib/`，gitignored 可重生研究資料——此輸出為任務目的，允許寫入）。
  >
  > 跑完後 digest 本批結果：讀 `research_boxes.jsonl` 本批新增行數、direction × magnitude 分佈、與前批相比的異常值。摘要寫到 `ai-analysis/idle-findings/research-scan-<YYYYMMDD>.md`。
  >
  > 約束：遇不確定標 `open`；禁背景子智能體；若掃描中途被時長上限切斷，回隊列續跑時先檢查 jsonl checkpoint 再續（`--resume` 冪等）；除掃描輸出目錄與摘要檔外不修改任何檔案。

## UI 建立步驟（引導用）

1. ZCode 左側邊欄 → **自動化** → **閒時任務**標籤 → **建立閒時任務**
2. 專案選 `mosaic_alpha`（當前視窗已開的本地項目；建立後不可改）
3. 貼 Title / Instructions（上面產出的原文）／ 執行模式照建議
4. 提交 → 進全局隊列（卡片顯示排隊位次；不承諾開始時間）
5. 若希望夜間跑完：打開自動化頁面的「保持喚醒」（Keep your computer running）開關

## 維護

- 新增範本：直接在本檔「範本庫」加一節（Title / Instructions / 執行模式建議三件套）——本檔是範本唯一真相源。
- 本 skill source 在 ai-rules repo（`skills/mosaic-idle-tasks/SKILL.md`）；部署副本 `~/.zcode/skills/mosaic-idle-tasks/`——改 source 後同步部署，新 session 生效。
