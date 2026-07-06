---
harness-scope: claude-specific
---

# 程式碼編輯約束（Claude）

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

> Claude Code 專屬的 Edit/Write 工具 API 約束。通用編輯紀律（SRP/DIP/變更紀律/禁混合寫法/向後相容）見 [edit-discipline.md](edit-discipline.md)（neutral）。

## Edit 工具使用約束

> **核心原則**：Edit 前必須先 Read，確保 `old_string` 精確匹配檔案當前內容。

### 強制規則

- **Edit 前必須 Read**：編輯任何檔案前，必須先讀取該檔案確認當前內容
- **重複編輯同一檔案**：每次 Edit 後若需再次編輯同一檔案，必須重新 Read 取得最新狀態
- **`old_string` 必須精確**：直接從 Read 輸出複製目標文字，不可憑記憶或推測拼湊

### ❌ 常見錯誤模式

```markdown
## ❌ 錯誤：未重讀就編輯（old_string 與檔案實際內容不符）
# 第一次 Edit 成功後，檔案內容已改變
# 第二次 Edit 仍用舊的 old_string → Error editing file

## ✅ 正確：每次 Edit 前重新 Read
# 1. Read file → 取得當前內容
# 2. Edit file（用 Read 到的精確內容）
# 3. 若需再次 Edit → 先 Read 取得更新後的內容
```

### 連續 Edit 失敗處理

連續兩次 Edit 同一檔案失敗時：
1. **停止重試**：不要用相同的 old_string 再試
2. **重新 Read**：讀取檔案確認當前狀態
3. **確認 old_string**：確保匹配的文字確實存在於檔案中

### 連續同類錯誤處理

寫出的程式碼反覆出現同類錯誤時，必須停下改變策略：

- **連續 2 次 Edit 失敗** → 停下改用 Write 工具整檔覆寫
- **連續 3 次同類語法/邏輯錯誤** → 停下，用 `uv run python -c "compile(...)"` 或 `uv run ruff check` 驗證，確認修正方向正確後再繼續
- **禁止盲目重試**：不改變策略的反覆嘗試是浪費時間

### Edit 失敗時的降級策略

Edit 工具在跨行匹配含多位元組字元（中文等）時可能失敗，即使 `old_string` 精確。

**降級順序**：
1. **縮小 old_string** — 只匹配目標周圍的 ASCII 部分，避開多位元組字元
2. **Write 工具覆寫** — Read 取得完整內容，修改後 Write 整檔覆寫
3. **不使用 sed/Python 替換** — sed 不理解程式碼或 Markdown 語法，批次替換常破壞縮排、誤改字串/註解、毀損多行結構。禁止用 sed 修改 `.py`、`.md`、YAML/JSON/TOML。唯一允許：過濾日誌輸出、處理純文字資料流（不修改原始檔）

```markdown
## ✅ Write 降級流程
# 1. Read file → 取得完整內容
# 2. 在 context 中修改目標段落
# 3. Write file → 寫回完整檔案
```

---

## 編輯前自檢清單

在進行程式碼編輯前確認：
- [ ] 已讀取目標檔案（Edit 前必須 Read）
- [ ] `old_string` 從 Read 輸出精確複製
- [ ] 連續編輯同一檔案時，每次 Edit 前重新 Read
- [ ] Edit 連續失敗時，改用 Write 整檔覆寫
- [ ] 已嘗試編輯現有檔案而非創建新檔案
- [ ] 如果需要破壞性變更，確認不影響外部整合
- [ ] 架構改進有測試保護
