---
harness-scope: neutral
---

# 搜尋工具分工

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

---

## 核心原則

**文字搜尋用 rg、檔案搜尋用 fd（預設遵守 `.gitignore`，減少噪音）；符號/圖譜與型別面路由見 [symbol-query-routing.md](symbol-query-routing.md)。**

(Claude: `find -exec`、`grep -r` 是 Claude Code 系統層級硬限制；`fd`/`rg` 預設可 auto-allow。其他 harness 無此限制，fd/rg 語法優勢通用)

fd/rg 旗標陷阱（alternation `\|`、隱藏檔旗標跨工具不同義、grep 旗標遷移、glob 錨定）、git pathspec 三陷阱、統計用途禁 head 截斷、盤點執行點雙掃——細則見 modern-cli-preference skill（on-demand；觸發詞：rg 陷阱、fd、pathspec、截斷、計數、旗標遷移、盤點雙掃）。
