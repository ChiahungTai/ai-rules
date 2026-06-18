---
name: external-api-investigation
description: Guides investigation of external API / integrator behavior — actual runtime params, quota usage, object fields, domain rules. Use when debugging "external API sends what / uses how much / has which fields", investigating integrator-type problems (quota overrun, wrong params, serialization), or when read-code reasoning (L1) might mislead. Triggers on external API, quota, 用量, API 參數, monkey-patch, dry-run, 整合器調查, stub 查欄位, SJ/NT API 行為, 跨進程調查.
---

# External API / Integrator Investigation

調查「外部組件（API / SDK / 跨進程服務）**實際**做什麼」的方法論。核心：**實證（runtime）優先於推理（讀 code）** —— 讀 code 的因果鏈易錯（L1），runtime 實證才揭露真相（L4）。

## 與既有 skill 的邊界

- `debugging-and-error-recovery`：除**自己 code** 的 bug（根因診斷）。本 skill 調查**外部組件**的真實行為。
- `source-driven-development`：實作 **grounding 於官方文檔**（API 用法）。本 skill 調查文檔不講的 runtime 行為（實際送什麼參數、用量多少）。
- `acceptance-evidence`：測試/驗收的**證據階層**（L1-L6）。本 skill 是 L4（runtime 實證）在「外部 API 調查」場景的具體化。

---

## Monkey-patch dry-run — 攔截實際參數，不真呼叫

調查「外部 API 實際送什麼參數 / 用量多少」（如 quota 超量），**monkey-patch 攔截層印參數**（不真呼叫），比讀 code 推理強很多。

- 在呼叫外部 API（如 SJ `api.kbars`）**前一層** 攔截（monkey-patch `_get_historical_bars_async/sync`），印 (symbol, start, end, days)，`callback([])` 不寫 catalog、不消耗 quota。
- **零 quota 成本**揭露真相：例如 667 檔 `start=2020`（catalog 從沒寫入）—— 讀 code 完全推不出這分布。
- 讀 code 推理（L1）的因果鏈易錯：讀 `coordinator._process_and_write` 推「日K壞 → 死循環 → 分K沒寫」，但實際日K非致命（失敗只 log）。dry-run（L4）直接看真相。

**這是「L1 冒充 L4」的反向 —— 調查時主動升級到 L4。**

## 外部 API 物件屬性查 stub / source，不憑訓練資料

「X API 的 Y 物件有沒有 Z 欄位」必須查 stub（`.pyi`）/ source / 官方文檔，**不憑訓練資料推測**。

- 例如 Contract 有沒有夜盤欄位 → 查 `_core.pyi` 的 Contract 定義確認無 `trading_hours/session/market_type`。
- `context7` 查 lib docs（API **用法**）；但「物件有哪些欄位/屬性」要查 stub/source（欄位**存在性**）—— 兩者不同查證路徑。
- 憑訓練資料推測 API 屬性 = 過時/不全/概化的 high-risk 區。

## Domain 業務規則問用戶，不假設

業務規則（夜盤時段、哪些商品有夜盤、quota 計量單位 MB vs request）用戶比 LLM 懂。調查時**主動問 domain**，不自行假設。

- **程式碼事實**（這 function 怎麼算）→ LLM 查 source（自理）。
- **業務規則**（哪些期貨有夜盤）→ 問用戶（domain 權威）。
- 分工：別把 domain 假設當 code 事實查，也別把 code 事實拿去問用戶。

## 避免 early hypothesis — dry-run 實證驗證假設

讀 code 形成假設 OK，但根因可能更深。**dry-run 實證驗證假設**，不只讀 code。

- 讀 code 假設「時間範圍 bug」→ dry-run 揭露「venue 硬編碼」（更深一層）。
- 形成 hypothesis 後，問「這能用 dry-run / runtime log 證實或否證嗎？」能 → 跑，別只靠推理。

---

## 何時用本 skill

- 「外部 API 實際送什麼參數 / 用量多少 / 為何超量」
- 整合器型問題（接 ≥2 外部組件，行為無法從單方文檔推導）
- 讀 code 推理得出因果鏈，但覺得「可能不對」→ dry-run 驗證
- 「X API 有沒有 Y 欄位」（查 stub，非訓練資料）
- 調查涉及 domain 業務規則（先確認是 code 事實還是 domain）

## 不適用

- 純自己 code 的 bug → `debugging-and-error-recovery`
- 查 API 怎麼呼叫（用法）→ `source-driven-development` / `context7-mcp`
- 測試/驗收證據分級 → `acceptance-evidence`
