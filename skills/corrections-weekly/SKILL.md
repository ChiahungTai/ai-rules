---
name: corrections-weekly
description: "糾正模式週報——挖掘本週用戶對 AI 的糾正訊息、分類計數、累積月檔。腳本撈候選（ZCode db.sqlite 面）、LLM 只做判讀分類（scan-project pattern）。每週六 23:10 排程自動跑（ai-rules workspace，排在 22:10 mosaic 週期大活與 23:20 每日 report 之間）；也可手動觸發（『跑糾正週報』『corrections report』）。產出供治理決策：某類糾正暴增＝有規則在衰減的訊號。"
when_to_use: "週期排程到點；或用戶要求糾正模式分析/月報/趨勢對比時手動載入。不適用：單一 session 的即時糾正處理（那是當下對話的事）。"
allowed-tools: ["Read", "Bash", "Write", "Edit"]
---

# corrections-weekly — 糾正模式週報

> 背景：兩週遙測實證（2026-08-29 brainstorm §2.4）——~30 糾正/2週（方向錯＞重複勞動＞遺漏），散在 1/4 sessions，隨 session 消失。本 skill 把它變成可累積的治理訊號。方法經 Agent A 驗證；機械面沉腳本（冷 context 安全），判讀面留 LLM。

## 步驟

1. **跑腳本撈候選**（機械面——勿手打 SQL）：

   ```bash
   uv run python /Users/ctai/Github/ai-rules/skills/corrections-weekly/scripts/mine_corrections.py --days 7
   ```

   輸出：候選清單（時間／session 短 id／摘錄）＋計數。腳本已排除 subagent sessions、task-notification 注入、compact 摘要。

2. **逐則判讀分類**（LLM 面）：對每個候選判斷是否真糾正（關鍵詞有假陽性——技術討論中的「不需要」可能不是糾正），分類：**方向錯／重複勞動（whole-picture blind spot）／遺漏／修了仍壞／過度工程／驗證責任推給用戶／其他**。邊界案例標「疑似」不硬歸。

3. **append 月檔**：`ai-analysis/reports/corrections-<YYYY-MM>.md`（每月一檔累積）。每週一節：

   ```markdown
   ## <起訖日> 週報
   - 計數：方向錯 N／重複 N／遺漏 N／修了仍壞 N／過度工程 N／驗推用戶 N（候選 X、真糾正 Y）
   - Top 引述（≤3，session id＋200 字內摘錄）
   - vs 前週：一句趨勢（哪類升降）
   - 訊號：有無新湧現模式（如新規則繞道形態）——有則明列，無則寫「無新形態」
   ```

4. **判讀產出**（報告尾一行）：本月累積趨勢是否支持「某規則在衰減、該修」的具體建議——沒有就寫「無需動作」（不硬擠結論）。

## 紀律

- DB 唯讀（腳本 mode=ro）；報告一頁內；腳本失敗 2 次即止（印 `[FAIL]` 收工，勿重試迴圈燒 usage——冷 context 教訓）
- 不動 repo 其他檔案；corrections 月檔未 commit 由用戶決定去留
- 排程語境（冷 context）：本 skill 自足——腳本路徑絕對、分類定義內嵌、不依賴其他 skill

## 邊界

- 只挖掘 ZCode 面（CC 側糾正不在 db.sqlite——如需雙面再擴，YAGNI 現不建）
- 常態化裁決已過（用戶 08-30 定案週六排程）；月檔累積 4 週後可做月度趨勢總結（屆時手動）
