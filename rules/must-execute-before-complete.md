# 修改後必須執行驗證

> **載入機制**: source `~/Github/ai-rules/rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide on-demand 讀

---

## 核心原則

**語法正確 ≠ 邏輯正確。修改程式碼後必須實際執行，不能只靠靜態檢查就宣稱完成。**

---

## 強制規則

### 可執行程式碼（.py 腳本、demo、poc/、example）

- 建立/修改後，必須 `uv run python <file>` 實際執行
- 修改多個相關檔案時，每個可執行檔案都必須跑
- AI 不得在未執行的情況下宣稱「完成」或「正確」
- **POC 暫時性**：`poc/` 為暫時性驗證產物，僅存活到所屬 EP 段落 build+commit；build 時驗證行為改寫成正式測試，`/commit` 階段 2.7 確認承接後清除

### 測試程式

- 修改測試後，必須 `uv run pytest <test>` 實際跑
- 新增測試必須先確認 FAIL（RED 階段）再實作對應程式碼
- 測試通過不代表驗證完成 — 還需確認測試確實在測它聲稱測的行為

### 修改後的強制流程

1. **修改程式碼**（.py、配置等）
2. **立即執行** — `uv run python <file>` 或 `uv run pytest <test>`
3. **觀察結果** — 成功？失敗？錯誤訊息是什麼？
4. **根據結果調整** — 不是改完就結束

### 例外（可跳過執行）

- 純文檔/CLAUDE.md 修改（非程式碼）— 純文檔指 `rules/`、`skills/`、`commands/` 下的 `.md` 檔案；含程式碼範例但本身不被執行的 `.md` 仍算純文檔
- 純註解修改（不改變執行邏輯）
- import 排序（由 `ruff check --fix` 處理）

---

## 禁止行為

- ❌ 用 `ast.parse` 語法檢查取代執行 — 語法正確不代表邏輯正確
- ❌ 讀了程式碼就說「看起來正確」— 沒跑過就是沒驗證
- ❌ 一次改多個 POC/demo 但全部沒跑
- ❌ 宣稱「完成」但實際上沒有 `uv run` 過任何一個修改的檔案
- ❌ 說「理論上應該可以」取代實際執行驗證

---

## 為什麼

從 1200+ 個對話 session 的反饋歸納：

- psycopg3 COPY API 中斷、浮點數到整數轉換陷阱、FK 約束問題 — 這些只在實際執行時才被發現
- 循環依賴（structure → datasets → config → features → structure）— 只有執行驗證能發現
- `.item()` 在多標的數據集上出錯 — `ast.parse` 完全無法偵測這類 runtime 錯誤

**結論：實際執行是唯一能發現這類問題的方式。**
