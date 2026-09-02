# Build 驗收記錄 — S1+S2（muse 實作）

> 2026-09-02。Writer：muse 1.0.1（`muse exec`，model=muse-spark-1.2、effort=high（CLI 預設）、--disable-approval、--trust-workspace、--max-model-steps 800）。Reviewer：本 session（Writer/Reviewer 分離）。

## 獨立驗證結果（全部實測，非採信自述）

| 項目 | 結果 |
|---|---|
| `node --test tests/` 重跑 | ✅ fail 0 / exit 0（44 tests、8 suites） |
| Bridge 真 E2E（真 muse＋訂閱 credential） | ✅ `REVIEW-OK`、exit 0、status=completed、sessionId 入 ledger（事件流 `poc-build.jsonl` 尾） |
| `setup` 對真 `auth.json` | ✅ credential 判別正確（onboarding/subscription carrier）；[WARN] workflows（預期，aarch64）；[WARN] sandbox 誤判（見 F2） |
| SM-11 行為 | ✅ 未帶 `--trust-workspace` 時 muse 跳過 repo AGENTS.md（警告如實顯示） |
| Code spot-check | ✅ model pin（DEFAULT_MODEL）、env strip（delete META_API_KEY）、`--` 分隔、prompt-file；❌ 原子寫缺失（F1） |
| NOTICE §4(d) | ⚠️→✅ muse 只再製 codex 原文；reviewer 補 grok 原文（GitHub raw），兩者齊＋addendum 變更清單 |
| 偏差清單 | ✅ 誠實（test-only `MUSE_BRIDGE_PROVIDER` override、classifyError 優先序、skippedUnknown 計數）文件化於 BUILD-REPORT.md |

## Review Findings（reviewer 獨立發現）

- **F1 [P1]** ledger 寫入非原子：`writeFileSync` 直寫三處（jobs.json / setup.json / jobs/<id>.jsonl），EP 契約（第三輪複審 #3 回寫）要求 tmp+rename——build 拿的是 handoff 時 EP 副本，時間差缺口
- **F2 [P2]** setup「sandbox」檢查誤判：trial exec 正常 JSONL 輸出被當 sandbox issue hint、detail 印整包原始 JSON——啟發式應以 exit code/錯誤關鍵字判定＋detail 截斷
- **F3 [P3]** ledger 欄位名 `exit` vs EP 契約 `exitCode`

**Fix round 1**：已回派 muse（背景，僅修 F1-F3＋重跑測試＋BUILD-REPORT 附錄）。NOTICE 由 reviewer 直接修（不在 fix round 範圍）。

## R2 帳務錨點追加

- #6：bridge 真 E2E `REVIEW-OK`（standard 模型、bridge spawn、~19:1x）——**這是 plugin 未來實際使用形態的第一個錨點**

## 備註

- muse 在自身沙箱內無法讀 `~/.config/muse`（credential），其「real bridge」自測用 echo provider——真訂閱路徑 E2E 由 reviewer 補測（上表）
- 本次 handoff 材料（docs/ reference/ BUILD.md）在 workspace 內；EP 第三輪回寫未同步進 workspace 副本（F1 根因）——fix round prompt 已內聯契約文字
