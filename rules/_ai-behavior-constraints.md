---
harness-scope: neutral
---

# AI 行為約束

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## 🔴 強烈警告：AI 禁止行為

> **這些行為會破壞 instruction 檔（AGENTS.md source；Claude 端另有 CLAUDE.md wrapper）的實用價值，絕對禁止。論證（為什麼統計/版號對 AI 無價值）見 instruction-writing skill「元資訊禁止的第一性原理分析」**

### ❌ 絕對禁止的行為

| 行為 | 原因 | 後果 |
|------|------|------|
| **加入統計資訊** | 行數/字數是快照，每次修改都過時 | AI 被誤導，以為程式碼很小 |
| **加入版本號** | AI 不關心 v1.0 → v2.0 | 浪費 token，無實質資訊 |
| **模組描述標版號** | 如 `ClassName（v3: ...）`必然過時 | 功能性描述始終準確 |
| **加入更新日期** | AI 只需要「當前」規則 | 干擾核心內容 |
| **加入 Changelog** | 歷史變更應放 CHANGELOG.md | 文檔膨脹 |
| **作者資訊** | 除非有特殊意義 | 無聊且干擾 |
| **寫入可推導內容** | API 簽名、參數表、欄位列表可從程式碼直接推導 | 浪費 token，降低 signal/noise ratio |
| **完整程式碼範例 (>5 行)** | 應精簡為一句話描述 + 源碼引用 | 文檔膨脹，維護成本高 |

### ✅ 正確的 AI 行為

專注核心原則（why）、暴露結構關係（檔案依賴）、說明當前狀態（現有規則與約束）。

## 🔴 Bash 強烈警告：`python -c` 禁止寫註解

> **`python -c` 是 AI 自用驗證，不需人類可讀註解。** 多行 `python -c` 中換行後接 `#` 註解會觸發部分 harness 的權限確認（Claude: Claude CLI 無法判斷跨行 `#` 是否被注入惡意內容，故每次需人工確認）。要驗證想法就寫乾淨單行，或落成 `.py` 檔。通用工具紀律（uv run / pipe-exit / 禁 sed / agent prompt 指定工具）見 [tool-discipline.md](tool-discipline.md)；Claude 端 `python -c` / `$` 展開限制（Claude: `bash-hard-rules.md`）。

---

## 執行約束

- **撰寫** instruction 檔（AGENTS.md source；Claude 端另有 CLAUDE.md wrapper）：不加入任何元資訊區塊、不統計行數字數、不標版本日期、專注「當前有效」的規則
- **修改** instruction 檔：移除發現的元資訊（不保留）、不添加新元資訊（即使其他檔案有）、用 instruction-clean 驗證（Claude: `/instruction-clean`；跨 harness 用各家清理工具或人工檢查）

---

## 自檢清單

在輸出或修改 instruction 檔前確認：沒加 `版本`/`更新日期`/`行數`/`字數` 區塊、沒在模組描述標版號、沒加 `變更歷史` 區塊或統計表格、沒寫可推導內容（API 簽名、參數表、欄位列表）、程式碼範例 <= 5 行、內容專注「當前有效」規則。

---

> 💡 **核心原則**: instruction 檔是給 AI 的實用指南，不是專案履歷表。任何對 AI 無意義的資訊都是噪音。
